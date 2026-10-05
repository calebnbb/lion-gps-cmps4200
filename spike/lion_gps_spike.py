#!/usr/bin/env python3
"""
Lion GPS - Phase 2 AI Technical Spike
CMPS 4200 HCI: AI-Enhanced UI/UX  |  Caleb Nwego & David Soboma

Tests the two models chosen in Phase 1, end to end:
  0. Claude Sonnet reading an uploaded audit PDF -> structured course list
  1. all-MiniLM-L6-v2 (sentence-transformers)  -> retrieve relevant audit records
  2. Claude Sonnet (Anthropic API)              -> grounded, cited answer

What it measures (maps 1:1 to the Phase 2 rubric):
  * Working call   - 6 realistic advising questions, outputs saved
  * Latency        - per call: retrieval ms, time-to-first-token, total time;
                     min / avg / max reported
  * Failure tests  - invalid API key, timeout, invalid model, empty input,
                     out-of-scope question, no supporting records, wrong PDF uploaded
  * Rate limits / cost - read from API response headers + token usage

Outputs (in ./results/):
  spike_results.json   raw data for every call
  spike_log.md         readable log of every input/output/error
  spike_summary.md     one-page summary with the numbers filled in

Setup (macOS):
  python3 -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  export ANTHROPIC_API_KEY="sk-ant-..."
  python lion_gps_spike.py

Options:
  --model NAME     Claude model string (default: claude-sonnet-5)
  --runs N         repeat the question set N times for steadier latency (default 1)
  --mock           offline pipeline test with a fake model (NOT valid spike data)
"""

import argparse
import json
import os
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path

from sample_data import ALL_RECORDS, TEST_QUESTIONS

# Pricing in USD per million tokens. Verify against the current Anthropic
# pricing page before submitting - update these two numbers if they differ.
PRICE_IN_PER_MTOK = 3.00
PRICE_OUT_PER_MTOK = 15.00

TOP_K = 8
MAX_TOKENS = 600
REQUEST_TIMEOUT_S = 30

RESULTS_DIR = Path(__file__).parent / "results"

SYSTEM_PROMPT = """You are Lion GPS, an academic advising assistant for a Southeastern Louisiana University student.

Rules:
1. Answer ONLY from the records provided in <records>. Do not use outside knowledge about courses, prerequisites, or policies.
2. Cite the ID of every record you rely on, e.g. [REQ-CS-CORE-4].
3. If the records do not contain enough information, say so plainly and set "needs_advisor" to true. Never guess.
4. If the question is not about the student's degree plan, politely decline and set "in_scope" to false.
5. Be concise and plain-spoken: the student may be reading on a phone between classes.

Respond with ONLY a JSON object, no prose before or after:
{
  "answer": "plain-language answer, 2-5 sentences",
  "citations": ["RECORD-ID", ...],
  "certainty": "high" | "partial" | "insufficient",
  "missing_info": "what is missing, or empty string",
  "needs_advisor": true | false,
  "in_scope": true | false,
  "suggested_followups": ["short follow-up question", ...]
}
"certainty" is NOT a probability. Use "high" only when every claim is directly supported by a cited record."""


# --------------------------------------------------------------------------- #
# Retrieval (all-MiniLM-L6-v2)
# --------------------------------------------------------------------------- #
class Retriever:
    def __init__(self, records, mock=False):
        self.records = records
        self.backend = None
        t0 = time.perf_counter()
        if mock:
            self._init_tfidf()
        else:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
                self.backend = "all-MiniLM-L6-v2"
            except Exception as e:  # model download blocked, library missing, etc.
                print(f"[warn] could not load all-MiniLM-L6-v2 ({e}); falling back to TF-IDF")
                self._init_tfidf()
        self.load_ms = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        if self.backend == "all-MiniLM-L6-v2":
            self.vectors = self.model.encode([r["text"] for r in records], normalize_embeddings=True)
        else:
            self.vectors = self.tfidf.fit_transform([r["text"] for r in records])
        self.index_ms = (time.perf_counter() - t0) * 1000

    def _init_tfidf(self):
        from sklearn.feature_extraction.text import TfidfVectorizer
        self.tfidf = TfidfVectorizer()
        self.backend = "tfidf-fallback"

    def search(self, query, k=TOP_K):
        import numpy as np
        t0 = time.perf_counter()
        if self.backend == "all-MiniLM-L6-v2":
            q = self.model.encode([query], normalize_embeddings=True)[0]
            scores = self.vectors @ q
        else:
            q = self.tfidf.transform([query])
            scores = (self.vectors @ q.T).toarray().ravel()
        order = np.argsort(-scores)[:k]
        hits = [{"id": self.records[i]["id"], "text": self.records[i]["text"],
                 "score": round(float(scores[i]), 3)} for i in order]
        return hits, (time.perf_counter() - t0) * 1000


def build_user_message(question, hits):
    recs = "\n".join(f'<record id="{h["id"]}">{h["text"]}</record>' for h in hits)
    return f"<records>\n{recs}\n</records>\n\n<question>{question}</question>"


# --------------------------------------------------------------------------- #
# Claude call (streamed, so we can measure time-to-first-token)
# --------------------------------------------------------------------------- #
def call_claude(client, model, question, hits, timeout=REQUEST_TIMEOUT_S):
    """Returns a dict describing success or failure. Never raises.
    max_retries=0 so each failure is recorded exactly as the API returns it
    (the production app would retry once with backoff)."""
    rec = {"model": model, "ok": False}
    t0 = time.perf_counter()
    try:
        with client.with_options(timeout=timeout, max_retries=0).messages.stream(
            model=model,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_user_message(question, hits)}],
        ) as stream:
            ttft = None
            chunks = []
            for text in stream.text_stream:
                if ttft is None:
                    ttft = time.perf_counter() - t0
                chunks.append(text)
            final = stream.get_final_message()
            headers = {}
            try:
                headers = {k: v for k, v in stream.response.headers.items()
                           if k.startswith("anthropic-ratelimit") or k in ("request-id", "retry-after")}
            except Exception:
                pass
        total = time.perf_counter() - t0
        raw = "".join(chunks)
        rec.update({
            "ok": True,
            "ttft_s": round(ttft or total, 3),
            "total_s": round(total, 3),
            "input_tokens": final.usage.input_tokens,
            "output_tokens": final.usage.output_tokens,
            "stop_reason": final.stop_reason,
            "raw_output": raw,
            "parsed": parse_json(raw),
            "rate_limit_headers": headers,
        })
        rec["cost_usd"] = round(rec["input_tokens"] / 1e6 * PRICE_IN_PER_MTOK
                                + rec["output_tokens"] / 1e6 * PRICE_OUT_PER_MTOK, 6)
    except Exception as e:
        rec.update({
            "total_s": round(time.perf_counter() - t0, 3),
            "error_type": type(e).__name__,
            "status_code": getattr(e, "status_code", None),
            "error_message": str(e)[:500],
        })
    return rec


def parse_json(raw):
    s = raw.strip()
    if s.startswith("```"):
        s = s.strip("`")
        s = s[s.find("{"):]
    try:
        return json.loads(s[s.find("{"): s.rfind("}") + 1])
    except Exception:
        return None  # counts as a "malformed output" failure in the UI



# --------------------------------------------------------------------------- #
# Audit parsing test: student-uploaded PDF -> structured course list
# --------------------------------------------------------------------------- #
PARSE_PROMPT = """Extract every course from this academic progress report.
Return ONLY JSON: {"courses": [{"code": "...", "title": "...", "credits": 3, "grade": "A|B|C|D|F|IP|W",
"term": "...", "source": "transfer|institutional", "applied_as": "course code or NOT APPLIED or null",
"unclear": false}], "program": "...", "notes": ["anything ambiguous a human should check"]}
Mark "unclear": true for any row you are not sure you read correctly. Do not invent rows."""

def parse_audit(client, model, pdf_path, timeout=90):
    import base64
    rec = {"model": model, "ok": False, "test": "P1 Audit PDF parsing"}
    t0 = time.perf_counter()
    try:
        data = base64.standard_b64encode(Path(pdf_path).read_bytes()).decode()
        msg = client.with_options(timeout=timeout, max_retries=0).messages.create(
            model=model, max_tokens=2500,
            messages=[{"role": "user", "content": [
                {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": data}},
                {"type": "text", "text": PARSE_PROMPT}]}])
        raw = msg.content[0].text
        parsed = parse_json(raw)
        rec.update({"ok": True, "total_s": round(time.perf_counter() - t0, 3),
                    "input_tokens": msg.usage.input_tokens, "output_tokens": msg.usage.output_tokens,
                    "raw_output": raw, "parsed": parsed,
                    "courses_found": len(parsed["courses"]) if parsed else 0,
                    "flagged_unclear": sum(1 for c in parsed["courses"] if c.get("unclear")) if parsed else 0,
                    "expected_courses": 15})
        rec["cost_usd"] = round(rec["input_tokens"] / 1e6 * PRICE_IN_PER_MTOK
                                + rec["output_tokens"] / 1e6 * PRICE_OUT_PER_MTOK, 6)
    except Exception as e:
        rec.update({"total_s": round(time.perf_counter() - t0, 3), "error_type": type(e).__name__,
                    "status_code": getattr(e, "status_code", None), "error_message": str(e)[:500]})
    return rec

# --------------------------------------------------------------------------- #
# Mock client for --mock (offline pipeline check only)
# --------------------------------------------------------------------------- #
class _MockStream:
    def __init__(self, text): self._t = text; self.response = None
    def __enter__(self): return self
    def __exit__(self, *a): return False
    @property
    def text_stream(self):
        for w in self._t.split(" "):
            time.sleep(0.01); yield w + " "
    def get_final_message(self):
        class U: input_tokens = 900; output_tokens = 120
        class M: usage = U(); stop_reason = "end_turn"
        return M()

class MockClient:
    def __init__(self): self.messages = self
    def with_options(self, **kw): return self
    def stream(self, **kw):
        return _MockStream('{"answer": "MOCK", "citations": [], "certainty": "insufficient", '
                           '"missing_info": "mock", "needs_advisor": true, "in_scope": true, '
                           '"suggested_followups": []}')


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def stats(values):
    return {"min": round(min(values), 3), "avg": round(statistics.mean(values), 3),
            "max": round(max(values), 3), "n": len(values)} if values else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=os.environ.get("LION_GPS_MODEL", "claude-sonnet-5"))
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--mock", action="store_true")
    args = ap.parse_args()

    if args.mock:
        client = MockClient()
    else:
        import anthropic
        if not os.environ.get("ANTHROPIC_API_KEY"):
            sys.exit("Set ANTHROPIC_API_KEY first (or use --mock for an offline pipeline check).")
        client = anthropic.Anthropic(base_url="https://api.anthropic.com")

    RESULTS_DIR.mkdir(exist_ok=True)
    out = {"started": datetime.now().isoformat(timespec="seconds"),
           "model": args.model, "mock": args.mock, "runs": args.runs}

    # ---- 1. Retrieval setup ----------------------------------------------
    print("Loading retriever...")
    retr = Retriever(ALL_RECORDS, mock=args.mock)
    out["retrieval"] = {"backend": retr.backend, "model_load_ms": round(retr.load_ms, 1),
                        "index_ms": round(retr.index_ms, 1), "records_indexed": len(ALL_RECORDS)}
    print(f"  backend={retr.backend} load={retr.load_ms:.0f}ms index={retr.index_ms:.0f}ms")

    # ---- 2. Working calls ------------------------------------------------
    calls = []
    for run in range(args.runs):
        for q in TEST_QUESTIONS:
            hits, r_ms = retr.search(q["text"])
            res = call_claude(client, args.model, q["text"], hits)
            res.update({"run": run + 1, "question_id": q["id"], "feature": q["feature"],
                        "persona": q["persona"], "question": q["text"],
                        "retrieval_ms": round(r_ms, 1), "retrieved_ids": [h["id"] for h in hits]})
            calls.append(res)
            flag = f'{res["total_s"]:.2f}s' if res["ok"] else f'ERROR {res.get("error_type")}'
            print(f"  [{q['id']} run {run+1}] {flag}")
            time.sleep(0.5)  # be gentle with rate limits
    out["calls"] = calls

    good = [c for c in calls if c["ok"]]
    out["latency"] = {
        "retrieval_ms": stats([c["retrieval_ms"] for c in calls]),
        "time_to_first_token_s": stats([c["ttft_s"] for c in good]),
        "total_response_s": stats([c["total_s"] for c in good]),
        "end_to_end_s": stats([c["total_s"] + c["retrieval_ms"] / 1000 for c in good]),
    }
    out["cost"] = {
        "avg_input_tokens": round(statistics.mean([c["input_tokens"] for c in good]), 1) if good else None,
        "avg_output_tokens": round(statistics.mean([c["output_tokens"] for c in good]), 1) if good else None,
        "avg_cost_per_question_usd": round(statistics.mean([c["cost_usd"] for c in good]), 5) if good else None,
        "json_parse_success": f'{sum(1 for c in good if c["parsed"])}/{len(good)}',
    }
    out["rate_limit_headers_sample"] = good[-1]["rate_limit_headers"] if good else {}

    # ---- 3. Failure tests ------------------------------------------------
    print("Running failure tests...")
    failures = []
    hits, _ = retr.search("CMPS 415 prerequisite")

    def run_fail(name, expected_ui, fn):
        r = fn(); r.update({"test": name, "ui_response": expected_ui}); failures.append(r)
        print(f"  {name}: {'ok' if r['ok'] else r.get('error_type')}")

    if not args.mock:
        import anthropic
        bad = anthropic.Anthropic(api_key="sk-ant-INVALID-KEY-FOR-TESTING", base_url="https://api.anthropic.com")
        run_fail("F1 Invalid API key", "Service-unavailable banner; keep audit view usable; log for devs",
                 lambda: call_claude(bad, args.model, "Can I take CMPS 415?", hits))
        run_fail("F2 Timeout (0.5 s limit)", "Cancel-able loading state -> 'Taking longer than usual' -> retry/advisor",
                 lambda: call_claude(client, args.model, TEST_QUESTIONS[2]["text"], hits, timeout=0.5))
        run_fail("F3 Invalid model name", "Same as service unavailable (config error, not user's fault)",
                 lambda: call_claude(client, "claude-does-not-exist", "Can I take CMPS 415?", hits))
    run_fail("F4 Empty question", "Should be blocked client-side; test shows what the model does if it slips through",
             lambda: call_claude(client, args.model, "", hits))
    run_fail("F5 Out-of-scope request", "Model should set in_scope=false; UI shows polite redirect chips",
             lambda: call_claude(client, args.model, "Write my 500-word essay on the French Revolution.",
                                 retr.search("essay French Revolution")[0]))
    run_fail("F6 No supporting records", "Model should return certainty=insufficient + needs_advisor; UI shows low-confidence state",
             lambda: call_claude(client, args.model, "Does ACCT 2020 count toward my CS degree?",
                                 retr.search("ACCT 2020 accounting")[0]))
    # Invalid input for the upload feature: a PDF that is not an audit
    if not args.mock:
        notaudit = Path(__file__).parent / "results" / "not_an_audit.pdf"
        from reportlab.pdfgen import canvas as _c
        cv = _c.Canvas(str(notaudit)); cv.drawString(72, 720, "Grocery list: eggs, rice, plantains, milk."); cv.save()
        r = parse_audit(client, args.model, notaudit)
        r.update({"test": "F7 Wrong document uploaded",
                  "ui_response": "Parse returns 0 courses -> 'This doesn't look like an academic progress report' + how to download the right one"})
        failures.append(r); print(f"  F7 Wrong document: {'ok' if r['ok'] else r.get('error_type')}")
    out["failures"] = failures

    # ---- 3b. Audit parsing (PDF upload feature) ---------------------------
    if not args.mock:
        print("Parsing sample audit PDF...")
        out["audit_parse"] = parse_audit(client, args.model, Path(__file__).parent / "sample_audit.pdf")
        ap_ = out["audit_parse"]
        print(f"  {'ok' if ap_['ok'] else ap_.get('error_type')} in {ap_['total_s']} s, "
              f"{ap_.get('courses_found')} of 15 courses, {ap_.get('flagged_unclear')} flagged unclear")
    out["finished"] = datetime.now().isoformat(timespec="seconds")

    # ---- 4. Save --------------------------------------------------------
    (RESULTS_DIR / "spike_results.json").write_text(json.dumps(out, indent=2))
    write_log(out)
    write_summary(out)
    print(f"\nDone. See {RESULTS_DIR}/spike_summary.md")


# --------------------------------------------------------------------------- #
# Reports
# --------------------------------------------------------------------------- #
def write_log(out):
    L = [f"# Lion GPS spike log - {out['started']}", f"Model: `{out['model']}`  |  Retrieval: `{out['retrieval']['backend']}`"
         + ("  |  **MOCK RUN - not valid spike data**" if out["mock"] else ""), ""]
    for c in out["calls"]:
        L += [f"## {c['question_id']} (run {c['run']}) - {c['feature']} - persona: {c['persona']}",
              f"**Question:** {c['question']}", f"**Retrieved:** {', '.join(c['retrieved_ids'])} ({c['retrieval_ms']} ms)"]
        if c["ok"]:
            L += [f"**Latency:** first token {c['ttft_s']} s, total {c['total_s']} s  |  tokens {c['input_tokens']} in / {c['output_tokens']} out",
                  "```json", c["raw_output"].strip(), "```", ""]
        else:
            L += [f"**ERROR:** {c['error_type']} ({c.get('status_code')}) - {c['error_message']}", ""]
    L += ["# Failure tests", ""]
    for f in out["failures"]:
        L += [f"## {f['test']}", f"**Planned UI response:** {f['ui_response']}"]
        if f["ok"]:
            L += [f"**Model returned (in {f['total_s']} s):**", "```json", f["raw_output"].strip(), "```", ""]
        else:
            L += [f"**Error returned after {f['total_s']} s:** `{f['error_type']}` status={f.get('status_code')}",
                  f"> {f['error_message']}", ""]
    ap_ = out.get("audit_parse")
    if ap_:
        L += ["# Audit PDF parsing (sample_audit.pdf, 15 course rows)"]
        if ap_["ok"]:
            L += [f"{ap_['total_s']} s, {ap_['input_tokens']} in / {ap_['output_tokens']} out tokens, "
                  f"{ap_['courses_found']} courses found, {ap_['flagged_unclear']} flagged unclear", "```json", ap_["raw_output"].strip(), "```"]
        else:
            L += [f"ERROR {ap_['error_type']}: {ap_['error_message']}"]
    (RESULTS_DIR / "spike_log.md").write_text("\n".join(L))


def write_summary(out):
    lat, cost = out["latency"], out["cost"]
    fmt = lambda s, u="s": f"{s['min']} / {s['avg']} / {s['max']} {u}" if s else "n/a"
    good = [c for c in out["calls"] if c["ok"]]
    grounded = sum(1 for c in good if c["parsed"] and c["parsed"].get("citations"))
    fail_rows = "\n".join(
        f"| {f['test']} | " + (f"Model answered: certainty=`{(f.get('parsed') or {}).get('certainty')}`, "
                                f"in_scope=`{(f.get('parsed') or {}).get('in_scope')}`, needs_advisor=`{(f.get('parsed') or {}).get('needs_advisor')}`"
                                if f["ok"] else f"`{f['error_type']}` ({f.get('status_code')}) after {f['total_s']} s")
        + f" | {f['ui_response']} |" for f in out["failures"])
    rl = out.get("rate_limit_headers_sample") or {}
    rl_line = ", ".join(f"{k.replace('anthropic-ratelimit-', '')}={v}" for k, v in rl.items()
                        if k.endswith("-limit")) or "not returned"
    avg_total = lat["end_to_end_s"]["avg"] if lat["end_to_end_s"] else None

    ap_ = out.get("audit_parse")
    if ap_ and ap_["ok"]:
        parse_line = (f"**Audit PDF parsing** (one call per upload): {ap_['total_s']} s, found {ap_['courses_found']} of "
                      f"{ap_['expected_courses']} course rows, {ap_['flagged_unclear']} flagged unclear, cost ${ap_['cost_usd']}.")
    elif ap_:
        parse_line = f"**Audit PDF parsing:** failed with {ap_['error_type']}."
    else:
        parse_line = "**Audit PDF parsing:** not run (mock mode)."
    S = f"""# Lion GPS - AI Technical Spike Summary
**Team:** Caleb Nwego, David Soboma  |  **Run:** {out['started']}  |  **Model:** `{out['model']}` + `{out['retrieval']['backend']}`{'  |  **MOCK RUN**' if out['mock'] else ''}

## Latency ({len(good)} successful calls)
| Stage | Min / Avg / Max |
|---|---|
| Retrieval (embed question + search {out['retrieval']['records_indexed']} records) | {fmt(lat['retrieval_ms'], 'ms')} |
| Claude: time to first token | {fmt(lat['time_to_first_token_s'])} |
| Claude: full answer | {fmt(lat['total_response_s'])} |
| **End to end** | **{fmt(lat['end_to_end_s'])}** |

{parse_line}

One-time setup: embedding model load {out['retrieval']['model_load_ms']} ms, indexing the audit {out['retrieval']['index_ms']} ms (done once per login).

## Output quality
- Valid JSON returned: **{cost['json_parse_success']}**
- Answers that cited at least one record: **{grounded}/{len(good)}**
- Manual review of each answer (fill in from spike_log.md): correct / partially correct / wrong, and whether each citation actually supports the claim.

## Failure behavior
| Test | What came back | Our UI response |
|---|---|---|
{fail_rows}

## Rate limits & cost
- Rate-limit headers on our key: {rl_line}
- Avg tokens per question: {cost['avg_input_tokens']} in / {cost['avg_output_tokens']} out
- Avg cost per question: **${cost['avg_cost_per_question_usd']}** (at ${PRICE_IN_PER_MTOK}/${PRICE_OUT_PER_MTOK} per M tokens)
- At 20 questions per student per week, 1,000 active students = about ${round((cost['avg_cost_per_question_usd'] or 0) * 20 * 1000, 2)} per week.

## How this shaped our design
- **Loading:** end-to-end averages about {avg_total} s, which is in the 1-10 s band, so every AI screen gets a clear, staged progress message ("Reading your audit..." then "Checking requirements..."). We stream the answer as it arrives so the student sees text at about {lat['time_to_first_token_s']['avg'] if lat['time_to_first_token_s'] else 'n/a'} s instead of waiting for the full response. At 10 s we show "Taking longer than usual" with Cancel and Ask an advisor.
- **Errors:** auth/model/network failures fail fast and look the same to the student: a banner that says AI answers are paused, while the audit view, requirement list, and advisor handoff keep working. There is no dead end.
- **Trust:** Claude gives no reliable confidence number, so we show no percentages. We use the model's `certainty` label as a *wording switch* ("Based on your records..." vs "I couldn't confirm this...") plus clickable citations. `insufficient` answers always show the advisor handoff.
- **Scope:** out-of-scope requests are declined by the model, and the UI turns them into suggested advising questions.
- **Model decision:** keep / switch (justify).
"""
    (RESULTS_DIR / "spike_summary.md").write_text(S)


if __name__ == "__main__":
    main()
