"""Builds the Lion GPS Phase 2 deck files (project/deck.json + project/slides/*.html)."""
import json, os, sys
from datetime import datetime, timezone

OUT = sys.argv[1]
os.makedirs(os.path.join(OUT, "project", "slides"), exist_ok=True)

DARK = "#15301F"; LIGHT = "#F7F5EE"; PAPER = "#EFEBDF"; GOLD = "#E0B43B"; BODY = "#44564B"; LINE = "#CFC9B8"; SOFT = "#C9D8CE"
HEAD = "font-family:'Domine', Georgia, serif"
TXT = "font-family:'Nunito Sans', Arial, sans-serif"

slides = []

def sec(sid, inner, notes, bg=LIGHT, color=DARK, extra="", page=True):
    n = len(slides) + 1
    foot = (f'<p style="position:absolute; left:128px; bottom:64px; width:1664px; font-size:24px; color:{BODY if bg != DARK else SOFT}">'
            f'Lion GPS · Phase 2 · {n}</p>') if page else ""
    html = (f'<section id="{sid}" data-transition="fade" style="background:{bg}; color:{color}; {TXT}; '
            f'padding:128px 128px 160px; display:flex; flex-direction:column; gap:48px; {extra}">'
            f'{inner}{foot}<aside>{notes}</aside></section>')
    slides.append((sid, html))

def eyebrow(t, color=None):
    return f'<p style="font-size:26px; font-weight:700; letter-spacing:3px; text-transform:uppercase; color:{color or "#8A6A12"}">{t}</p>'

def title(t, color=DARK):
    return f'<h2 style="{HEAD}; font-size:64px; font-weight:700; line-height:1.15; color:{color}">{t}</h2>'

def head(eb, t, color=DARK, ebc=None):
    return f'<div style="display:flex; flex-direction:column; gap:16px">{eyebrow(eb, ebc)}{title(t, color)}</div>'

def card(h, body, bg="#FFFFFF", border=LINE, hc=DARK, bc=BODY, extra=""):
    return (f'<div style="flex:1; display:flex; flex-direction:column; gap:12px; background:{bg}; padding:36px; '
            f'border:1px solid {border}; border-radius:16px; {extra}">'
            f'<h3 style="{HEAD}; font-size:36px; font-weight:700; color:{hc}">{h}</h3>'
            f'<p style="font-size:28px; line-height:1.4; color:{bc}">{body}</p></div>')

def table(headers, rows, widths, size=26):
    th = "".join(f'<th style="width:{w}%; text-align:left">{h}</th>' for h, w in zip(headers, widths))
    trs = "".join(f'<tr style="background:{"#FFFFFF" if i % 2 == 0 else LIGHT}">' + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
                  for i, r in enumerate(rows))
    return (f'<table style="{TXT}; font-size:{size}px; color:{DARK}; padding:14px"><tr style="background:{PAPER}">{th}</tr>{trs}</table>')

# 1 Cover ------------------------------------------------------------------
sec("cover",
    f'<div style="flex:1"></div>'
    f'{eyebrow("CMPS 4200 · Phase 2", GOLD)}'
    f'<h1 style="{HEAD}; font-size:120px; font-weight:700; line-height:1.05; color:{LIGHT}">Lion GPS</h1>'
    f'<p style="font-size:44px; line-height:1.3; color:{SOFT}; width:1300px">Information architecture, user flows, wireframes and an AI technical spike for an advising companion that always shows its sources.</p>'
    f'<div style="flex:1"></div>'
    f'<p style="font-size:30px; color:{LIGHT}">Caleb Nwego · David Soboma</p>',
    "DAVID (0:00-0:40). Hi, we're Caleb and David. Lion GPS is an AI advising companion for SLU students. In Phase 1 we defined the problem and personas. In Phase 2 we designed the structure, the flows, the wireframes, and we tested the AI for real so our loading and error designs match how the model actually behaves.",
    bg=DARK, color=LIGHT, extra="padding:128px", page=False)

# 2 Problem + personas -----------------------------------------------------
sec("personas",
    head("Who we designed for", "Three students, one question: am I on track?") +
    '<div style="display:flex; gap:32px">'
    + card("Amara, 18", "Undeclared freshman, first-gen. Checks her phone between classes. Needs to know which classes “count” and to trust the answer.")
    + card("Chidi, 20", "CS junior, works 20 hrs/week. Plans late at night. Needs options that fit Tue/Thu and no prerequisite surprises.")
    + card("Ngozi, 24", "Transfer business major. Got conflicting advice before. Needs to verify transfer credit and reach a human easily.")
    + "</div>"
    + f'<p style="font-size:30px; color:{BODY}">Every screen and flow in this phase is labeled with the persona it serves.</p>',
    "DAVID (0:40-1:30). Quick recap of our Phase 1 personas. Amara needs plain language and reassurance. Chidi needs speed and schedule fit. Ngozi needs transparency and an easy path to a human. The common thread from research: students will use AI only if they can check where the answer came from. That became our design rule for Phase 2.")

# 3 Data approach -----------------------------------------------------------
sec("data",
    head("Where the data comes from", "No Workday or Canvas integration needed") +
    '<div style="display:flex; gap:32px">'
    + card("Public catalog", "Program requirements and prerequisites for every major, imported nightly from SLU's online catalog.")
    + card("Student upload", "The student downloads their academic progress report PDF from Workday and uploads it. AI reads it; the student confirms every row.")
    + card("Manual entry", "Check off completed courses from a list. Always works, even when the AI is down.")
    + "</div>"
    + f'<p style="font-size:30px; color:{BODY}">The class schedule is public too, so “fits my Tue/Thu” needs no system access.</p>',
    "DAVID (1:30-2:20). The obvious question is: how do you get student data without Workday or Canvas access? We don't need it. Requirements are public in the catalog. Students already can download their own progress report as a PDF, and they upload it. That also helps trust, because students see exactly which document the AI is reading. Manual entry is the fallback.")

# 4 Site map ----------------------------------------------------------------
def node(t, sub, bg="#FFFFFF", c=DARK):
    return (f'<div style="flex:1; display:flex; flex-direction:column; gap:6px; background:{bg}; border:2px solid {DARK}; border-radius:14px; padding:24px">'
            f'<p style="font-size:30px; font-weight:700; color:{c}">{t}</p><p style="font-size:24px; color:{BODY if bg == "#FFFFFF" else SOFT}">{sub}</p></div>')
sec("sitemap",
    head("Information architecture", "One-time onboarding, then a five-tab app") +
    f'<div style="display:flex; flex-direction:column; gap:28px">'
    f'<div style="display:flex; gap:24px">{node("S0 Onboarding", "Sign in → upload audit ✦ → confirm rows ✦ → availability", DARK, LIGHT)}</div>'
    f'<div style="display:flex; gap:20px">'
    + node("S1 Home", "Progress, alerts, quick-ask")
    + node("S2 Ask ✦", "Chat, source drawer, history")
    + node("S3 My Path", "Timeline, requirement detail")
    + node("S4 Plan ✦", "Suggestions, draft schedule")
    + node("More", "S5 What-if ✦ · S6 Advisor ✦ · S7 My data")
    + "</div></div>"
    + f'<p style="font-size:30px; color:{BODY}">16 screens · ✦ = AI feature · progress numbers are calculated from the catalog, not AI, so they stay right when the AI is down.</p>',
    "DAVID (2:20-3:10). Here's the site map: 16 screens in 8 areas. The tab bar suits Amara on her phone. The five AI features are marked with a star. One key IA decision: progress numbers on Home and My Path are plain rules, catalog minus completed courses. So the core facts never depend on the AI.")

# 5 Flows -------------------------------------------------------------------
sec("flows",
    head("User flows", "Five key tasks, each designed around one persona") +
    table(["Flow", "Task", "Persona", "AI feature"],
          [["F1", "Import my audit and check transfer credit", "Ngozi", "AI-1 audit parsing"],
           ["F2", "Ask a question and verify the answer", "Amara", "AI-2 grounded Q&amp;A"],
           ["F3", "Plan next semester around work hours", "Chidi", "AI-3 course suggestions"],
           ["F4", "See what happens if I declare Biology", "Amara", "AI-4 what-if"],
           ["F5", "Hand a question to a real advisor", "Ngozi", "AI-5 advisor summary"]],
          [8, 50, 16, 26], 28),
    "DAVID (3:10-4:00). Five flows, each labeled with its persona. For example, F1 is built around Ngozi: the AI reads her PDF, but nothing is saved until she confirms every row, and unclear transfer rows are flagged. F3 is Chidi: suggestions arrive already filtered to his Tuesday/Thursday hours. Full diagrams are in our IA document. Now Caleb will cover the AI side.")

# 6 AI integration points ----------------------------------------------------
sec("aipoints",
    head("AI integration points", "Two models, five features") +
    table(["Feature", "Model", "Input → output", "Time"],
          [["AI-1 Audit parsing", "Claude Sonnet", "PDF → course list with “unclear” flags", "[P1] s"],
           ["AI-2 Ask", "MiniLM + Sonnet", "Question + top-8 records → cited answer", "[avg] s"],
           ["AI-3 Suggestions", "MiniLM + Sonnet", "Requirements + schedule → 2–3 course sets", "est. 5–10 s"],
           ["AI-4 What-if", "MiniLM + Sonnet", "Transcript + 2 programs → comparison", "est. 5–10 s"],
           ["AI-5 Advisor summary", "Claude Sonnet", "Conversation → editable summary", "est. 3–5 s"]],
          [26, 20, 40, 14], 26)
    + f'<p style="font-size:28px; color:{BODY}">all-MiniLM-L6-v2 runs on our server for retrieval; only the retrieved records go to Claude.</p>',
    "CALEB (4:00-4:50). We kept the Phase 1 pair: Claude Sonnet for reasoning and all-MiniLM-L6-v2 for retrieval. Here's where each is used, what goes in, what comes out, and the response time we measured in the spike. [Fill in the bracketed numbers from spike_summary.md.] Retrieval runs locally, so only the handful of relevant records ever leaves our server.")

# 7 Data flow ----------------------------------------------------------------
def box(t, bg="#FFFFFF", c=DARK, w=0):
    ww = f"width:{w}px;" if w else "flex:1;"
    return (f'<div style="{ww} background:{bg}; border:2px solid {DARK}; border-radius:14px; padding:22px">'
            f'<p style="font-size:28px; font-weight:700; color:{c}; text-align:center">{t}</p></div>')
arrow = f'<x-shape kind="arrow-right" style="background:{GOLD}; width:56px; height:32px"></x-shape>'
sec("dataflow",
    head("Data flow", "Names and IDs never leave our server") +
    f'<div style="display:flex; align-items:center; gap:16px">'
    + box("Student") + arrow + box("React front end") + arrow + box("FastAPI: strip name, W-number") + arrow + box("MiniLM retrieval") + arrow + box("Claude Sonnet", DARK, LIGHT)
    + "</div>"
    + '<div style="display:flex; gap:32px">'
    + card("Sent to Anthropic", "The question and the 8 most relevant course records. The audit PDF once, for parsing.")
    + card("Stored by us", "Profile, confirmed courses and chats in Postgres. PDF deleted after reading. Chats kept one semester.")
    + card("Checked on return", "JSON must parse and every citation must be a record we actually sent, or the answer is hidden.")
    + "</div>",
    "CALEB (4:50-5:40). Data flow. The student's input goes through our FastAPI back end, which strips personal identifiers before anything reaches the AI. Retrieval picks the 8 relevant records locally. Claude gets only those. When the answer comes back, we validate it: if it cites a record we never sent, we treat it as a failed answer. Before a real launch we'd need SLU sign-off for FERPA.")

# 8 Spike --------------------------------------------------------------------
def stat(v, l):
    return (f'<div style="flex:1; display:flex; flex-direction:column; gap:8px; background:#FFFFFF; border:1px solid {LINE}; border-radius:16px; padding:32px">'
            f'<p style="{HEAD}; font-size:72px; font-weight:700; color:{DARK}">{v}</p><p style="font-size:26px; color:{BODY}">{l}</p></div>')
sec("spike",
    head("AI technical spike", "What we measured before designing") +
    '<div style="display:flex; gap:24px">'
    + stat("[__] s", "time to first words (avg)")
    + stat("[__] s", "full answer, min / avg / max [__ / __ / __]")
    + stat("[__] s", "reading an audit PDF")
    + stat("$[__]", "per question")
    + "</div>"
    + table(["Failure we triggered", "What came back"],
            [["Invalid API key", "401 authentication_error, “API key is invalid.” (fails in under 0.1 s)"],
             ["0.5 s timeout", "[APITimeoutError after __ s]"],
             ["Off-topic / no supporting records", "[in_scope / certainty values from spike_log.md]"]],
            [36, 64], 26),
    "CALEB (5:40-6:50). The spike: 6 realistic advising questions from our personas, plus an audit PDF, sent to Claude with retrieval in front. [Read the numbers from spike_summary.md.] We triggered 7 failures: invalid key, timeout, wrong model name, empty input, off-topic request, a question with no supporting records, and a wrong PDF. The invalid key fails instantly with a 401, so fast errors need a clear message, not a spinner.")

# 9 Five states --------------------------------------------------------------
def state(n, t, d, bg="#FFFFFF", c=DARK, bc=BODY):
    return (f'<div style="flex:1; display:flex; flex-direction:column; gap:10px; background:{bg}; border:1px solid {LINE}; border-radius:16px; padding:28px">'
            f'<p style="font-size:24px; font-weight:700; color:{c}">{n}</p><h3 style="{HEAD}; font-size:32px; font-weight:700; color:{c}">{t}</h3>'
            f'<p style="font-size:24px; line-height:1.4; color:{bc}">{d}</p></div>')
sec("states",
    head("Designing from the spike", "Every AI feature has five states") +
    '<div style="display:flex; gap:20px">'
    + state("1", "Empty", "Example questions; says it answers only from your records")
    + state("2", "Loading", "Named steps; text streams in; Cancel after 10 s")
    + state("3", "Success", "Plain answer + clickable source chips")
    + state("4", "Low confidence", "“I couldn't confirm this” + advisor handoff", "#FBF1D3")
    + state("5", "Error", "Input kept; Retry; non-AI path still works", DARK, LIGHT, SOFT)
    + "</div>"
    + f'<p style="font-size:30px; color:{BODY}">No confidence percentages: Claude doesn’t produce reliable ones. We show sources, a rationale, and hedged wording instead.</p>',
    "CALEB (6:50-7:50). The spike shaped five states for every AI feature; there are 25 AI wireframes in total. Loading uses named steps and streaming because responses fall in the 1-10 second band. Low confidence is its own state: the model returns a certainty label, and we use it only to switch wording, never as a fake percentage. Citations do the trust work.")

# 10 Edge cases ---------------------------------------------------------------
sec("edges",
    head("Edge cases", "No dead ends") +
    table(["Scenario", "What the student sees", "Way forward"],
          [["AI down, timeout, rate limit", "“AI answers are paused.” Question saved.", "Retry · My Path · advisor"],
           ["Wrong or empty answer", "Answer hidden: “I couldn't give a reliable answer.”", "Rephrase · regenerate · advisor"],
           ["Invalid input (wrong PDF, off-topic)", "What we expected + how to fix it", "Upload guide · example questions"],
           ["Biased output", "Rationale is requirements-only; Report button", "Flagged answers hidden and reviewed"],
           ["Stale or conflicting records", "Audit date on every screen; both records side by side", "Re-upload · advisor prefilled"]],
          [30, 42, 28], 26),
    "CALEB (7:50-8:50). Six edge cases, including the three required ones. The rule: the student never hits a dead end. If the AI is down, the path and requirements still work, and the question is saved. If the answer is wrong or uncited, we hide it and offer a human. And Lion GPS never says you're cleared to register or graduate; advisors stay the authority.")

# 11 Next -------------------------------------------------------------------
sec("next",
    head("What's next", "From wireframes to a testable prototype", color=LIGHT, ebc=GOLD) +
    '<div style="display:flex; gap:32px">'
    + card("From critique", "[Top 2 changes from the Sep 28 team-to-team critique]", bg="#1E3D2A", border="#2F5A3F", hc=LIGHT, bc=SOFT)
    + card("Phase 3", "Mid-fidelity prototype of flows F1–F3, tested with our three personas' task sets.", bg="#1E3D2A", border="#2F5A3F", hc=LIGHT, bc=SOFT)
    + card("Open question", "Would SLU advising accept handoff summaries by email, or need a form?", bg="#1E3D2A", border="#2F5A3F", hc=LIGHT, bc=SOFT)
    + "</div>"
    + f'<p style="{HEAD}; font-size:44px; color:{GOLD}">Questions?</p>',
    "DAVID (8:50-10:00). What's next: we'll fold in feedback from the team critique, then build a mid-fidelity prototype of the first three flows and test it with tasks based on our personas. One open question for the class: how would advisors prefer to receive handoffs? Thanks, we're happy to take questions.",
    bg=DARK, color=LIGHT)

for sid, html in slides:
    with open(os.path.join(OUT, "project", "slides", f"{sid}.html"), "w") as f:
        f.write(html)
deck = {"v": 4, "createdOnFiles": {"v": 1, "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "title": "Lion GPS Phase 2 Presentation", "order": [s for s, _ in slides],
        "sections": {"intro": {"description": "Problem, personas and where the data comes from (David)", "start": "cover"},
                     "ia": {"description": "Site map and user flows (David)", "start": "sitemap"},
                     "ai": {"description": "AI integration, data flow, spike and the states it shaped (Caleb)", "start": "aipoints"},
                     "close": {"description": "Next steps and Q&A (David)", "start": "next"}},
        "faces": {"domine": {"family": "Domine", "href": "https://fonts.googleapis.com/css2?family=Domine:wght@400..700&display=swap"},
                  "nunito-sans": {"family": "Nunito Sans", "href": "https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@400;600;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "project", "deck.json"), "w") as f:
    json.dump(deck, f, indent=1)
print(len(slides), "slides")
