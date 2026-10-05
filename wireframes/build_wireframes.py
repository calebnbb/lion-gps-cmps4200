"""Generates the Lion GPS Phase 2 low-fidelity wireframe canvas (.dc.html artboards + canvas.json)."""
import json, os, sys
from datetime import datetime, timezone

OUT = sys.argv[1]
os.makedirs(os.path.join(OUT, "project"), exist_ok=True)

INK = "#1E1E1C"; MID = "#5F5E5A"; LINE = "#BDBBB4"; FILL = "#ECEAE4"; BG = "#FFFFFF"
ANN = "#1F4FD1"; FLAG = "#F3E3AE"
W, H = 390, 844
FONT = "'IBM Plex Sans', system-ui, sans-serif"
MONO = "'IBM Plex Mono', ui-monospace, monospace"

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# ---------------------------------------------------------------- atoms
def ann(t):
    return (f'<div style="align-self: flex-start; font-family: {MONO}; font-size: 11px; font-weight: 600; color: #FFFFFF; '
            f'background: {ANN}; padding: 3px 8px; border-radius: 4px; letter-spacing: 0.02em">{esc(t)}</div>')

def txt(t, size=14, weight=400, color=INK, extra=""):
    return f'<p style="margin: 0; font-size: {size}px; font-weight: {weight}; color: {color}; line-height: 1.4; {extra}">{esc(t)}</p>'

def h2(t): return txt(t, 20, 600)
def small(t, color=MID): return txt(t, 12, 400, color)
def label(t): return txt(t.upper(), 11, 600, MID, "letter-spacing: 0.06em;")

def btn(t, kind="secondary", full=False, disabled=False):
    if kind == "primary":
        s = f"background: {INK}; color: #FFFFFF; border: 1px solid {INK};"
    elif kind == "danger":
        s = f"background: #FFFFFF; color: #A1261B; border: 1.5px solid #A1261B;"
    elif kind == "link":
        s = f"background: transparent; color: {INK}; border: none; text-decoration: underline; padding-left: 0; padding-right: 0;"
    else:
        s = f"background: #FFFFFF; color: {INK}; border: 1.5px solid {INK};"
    if disabled:
        s = f"background: {FILL}; color: {MID}; border: 1px solid {LINE};"
    w = "width: 100%;" if full else ""
    dis = ' disabled="disabled"' if disabled else ""
    return (f'<button type="button"{dis} style="{s} {w} min-height: 44px; padding: 0 16px; border-radius: 8px; '
            f'font-family: {FONT}; font-size: 14px; font-weight: 600">{esc(t)}</button>')

def row(*items, gap=8, wrap=True, align="center", justify="flex-start"):
    return (f'<div style="display: flex; gap: {gap}px; align-items: {align}; justify-content: {justify}; '
            f'flex-wrap: {"wrap" if wrap else "nowrap"}">' + "".join(items) + "</div>")

def col(*items, gap=10, extra=""):
    return f'<div style="display: flex; flex-direction: column; gap: {gap}px; {extra}">' + "".join(items) + "</div>"

def chip(t, filled=False):
    bg = FILL if filled else "#FFFFFF"
    return (f'<span style="display: inline-block; font-size: 12px; color: {INK}; background: {bg}; border: 1px solid {LINE}; '
            f'border-radius: 999px; padding: 6px 12px">{esc(t)}</span>')

def src(t):
    return (f'<span style="display: inline-block; font-size: 11px; color: {INK}; background: #FFFFFF; border: 1px solid {INK}; '
            f'border-radius: 4px; padding: 3px 7px; text-decoration: underline">{esc(t)}</span>')

def card(*items, dashed=False, fill="#FFFFFF", gap=8, pad=14, border=None):
    b = border or (f"1.5px dashed {INK}" if dashed else f"1px solid {LINE}")
    return (f'<div style="display: flex; flex-direction: column; gap: {gap}px; background: {fill}; border: {b}; '
            f'border-radius: 10px; padding: {pad}px">' + "".join(items) + "</div>")

def ai_card(*items, label_text="AI answer"):
    tag = (f'<div style="align-self: flex-start; font-size: 10px; font-weight: 700; letter-spacing: 0.08em; color: {INK}; '
           f'border: 1px solid {INK}; border-radius: 3px; padding: 1px 5px">{esc(label_text.upper())}</div>')
    return card(tag, *items, dashed=True)

def bars(n=3, widths=(100, 92, 70)):
    return col(*[f'<div style="height: 10px; width: {widths[i % len(widths)]}%; background: {FILL}; border-radius: 4px"></div>'
                 for i in range(n)], gap=8)

def inp(ph, h=44, lbl=None):
    field = (f'<div style="min-height: {h}px; box-sizing: border-box; border: 1.5px solid {INK}; border-radius: 8px; padding: 12px; '
             f'font-size: 14px; color: {MID}">{esc(ph)}</div>')
    return col(label(lbl), field, gap=6) if lbl else field

def progress(p):
    return (f'<div style="height: 8px; background: {FILL}; border-radius: 4px; overflow: hidden">'
            f'<div style="height: 8px; width: {p}%; background: {INK}"></div></div>')

def step(t, state):
    mark = {"done": "✓", "now": "●", "todo": "○"}[state]
    color = INK if state != "todo" else MID
    w = 600 if state == "now" else 400
    return (f'<div style="display: flex; gap: 10px; align-items: center; font-size: 14px; color: {color}; font-weight: {w}">'
            f'<span style="width: 18px; font-family: {MONO}">{mark}</span><span>{esc(t)}</span></div>')

def banner(t, sub=None, kind="warn"):
    bg = FLAG if kind == "warn" else FILL
    inner = txt(t, 13, 600) + (small(sub, INK) if sub else "")
    return f'<div style="display: flex; flex-direction: column; gap: 2px; background: {bg}; border: 1px solid {INK}; border-radius: 8px; padding: 10px 12px">{inner}</div>'

def bubble_user(t):
    return (f'<div style="align-self: flex-end; max-width: 78%; background: {FILL}; border-radius: 14px 14px 4px 14px; '
            f'padding: 10px 12px; font-size: 14px; color: {INK}">{esc(t)}</div>')

def hatch(t):
    return (f'<div style="background: repeating-linear-gradient(45deg, {FILL}, {FILL} 6px, #FFFFFF 6px, #FFFFFF 12px); '
            f'border: 1px solid {LINE}; border-radius: 8px; display: flex; align-items: center; justify-content: center; '
            f'min-height: 90px; font-size: 12px; color: {MID}">{esc(t)}</div>')

def course_row(code, title, meta, flag=False, note=None, action="Edit"):
    bg = FLAG if flag else "#FFFFFF"
    extra = small(note, INK) if note else ""
    return (f'<div style="display: flex; gap: 10px; align-items: flex-start; padding: 10px; background: {bg}; '
            f'border-bottom: 1px solid {LINE}">'
            f'<div style="flex-grow: 1; display: flex; flex-direction: column; gap: 2px">{txt(code + " · " + title, 13, 600)}{small(meta)}{extra}</div>'
            f'<span style="font-size: 12px; text-decoration: underline; color: {INK}">{esc(action)}</span></div>')

# ---------------------------------------------------------------- frame
TABS = ["Home", "Ask", "My Path", "Plan", "More"]

def header(title, back=True, right=None):
    left = f'<span style="font-size: 20px; width: 24px">{"‹" if back else ""}</span>'
    r = f'<span style="font-size: 13px; text-decoration: underline; min-width: 24px">{esc(right or "")}</span>'
    return (f'<div style="height: 56px; flex-shrink: 0; box-sizing: border-box; padding: 0 16px; display: flex; align-items: center; '
            f'justify-content: space-between; border-bottom: 1px solid {LINE}">{left}'
            f'<span style="font-size: 16px; font-weight: 600">{esc(title)}</span>{r}</div>')

def tabbar(active):
    items = []
    for t in TABS:
        on = t == active
        items.append(f'<div style="flex-grow: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; '
                     f'font-size: 11px; font-weight: {600 if on else 400}; color: {INK if on else MID}">'
                     f'<div style="width: 22px; height: 22px; border-radius: 6px; border: 1.5px solid {INK if on else LINE}; '
                     f'background: {INK if on else "#FFFFFF"}"></div><span>{esc(t)}</span></div>')
    return (f'<div style="height: 64px; flex-shrink: 0; display: flex; align-items: center; border-top: 1px solid {LINE}; '
            f'padding: 0 8px">' + "".join(items) + "</div>")

def screen(title, body, tab=None, back=True, right=None, footer=None, overlay=None):
    foot = f'<div style="flex-shrink: 0; padding: 12px 16px; border-top: 1px solid {LINE}; display: flex; flex-direction: column; gap: 8px">{footer}</div>' if footer else ""
    over = overlay or ""
    return (f'<div style="position: relative; width: {W}px; height: {H}px; box-sizing: border-box; background: {BG}; color: {INK}; '
            f'font-family: {FONT}; display: flex; flex-direction: column; overflow: hidden">'
            + header(title, back, right)
            + f'<div style="flex-grow: 1; overflow: hidden; padding: 16px; display: flex; flex-direction: column; gap: 14px">{body}</div>'
            + foot + (tabbar(tab) if tab else "") + over + "</div>")

def page(title, root):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{esc(title)}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&amp;family=IBM+Plex+Sans:wght@400;600;700&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0;font-family:{FONT};color:{INK};background:#FFFFFF}}
a{{color:{INK}}}a:hover{{color:{ANN}}}
</style>
</helmet>
{root}
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{W},"height":{H}}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
"""

BOARDS = []  # (row, filename, title, html)
def add(rowi, fname, title, root):
    BOARDS.append((rowi, fname, title, page(title, root)))

# ================================================================ ROW 0: core screens
add(0, "S0-1-Welcome.dc.html", "S0.1 Welcome and sign in", screen("", col(
    f'<div style="height: 120px; border: 1.5px solid {INK}; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: 700; letter-spacing: 0.1em">LION GPS</div>',
    txt("Your degree plan, in plain English.", 22, 600),
    col(txt("• Ask questions about your degree and see the source for every answer"),
        txt("• Plan next semester around your schedule"),
        txt("• Hand anything tricky to a real advisor"), gap=6),
    f'<div style="flex-grow: 1"></div>',
    small("Lion GPS is a study aid, not official advising. Always confirm registration decisions with your advisor."),
    gap=18, extra="flex-grow: 1"), back=False,
    footer=btn("Sign in with your SLU email", "primary", True) + btn("How Lion GPS uses your data", "link")))

add(0, "S0-4-Availability.dc.html", "S0.4 Availability and goals", screen("Your week", col(
    txt("When can you take classes?", 18, 600),
    small("Used to filter course suggestions. You can change this anytime."),
    f'<div style="display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 4px; font-size: 11px; text-align: center">'
    + "".join(f'<div style="color: {MID}">{d}</div>' for d in ["", "Mon", "Tue", "Wed", "Thu", "Fri"])
    + "".join(
        f'<div style="color: {MID}; text-align: left">{slot}</div>' + "".join(
            f'<div style="height: 36px; border: 1px solid {INK}; border-radius: 4px; background: {INK if (d in (1, 3) and slot != "Eve") else "#FFFFFF"}"></div>'
            for d in range(5))
        for slot in ["AM", "PM", "Eve"]) + "</div>",
    small("Filled = available. Example: Tue/Thu mornings and early afternoons (Chidi)."),
    label("Interests (optional)"),
    row(chip("Security", True), chip("AI / ML"), chip("Web"), chip("Networking", True), chip("+ Add")),
    inp("Spring 2028", lbl="Target graduation"),
    gap=12), right="Skip", footer=btn("Continue", "primary", True) + small("Step 3 of 3")))

add(0, "Main.dc.html", "S1 Home dashboard", screen("Home", col(
    row(txt("Hi, Chidi", 22, 600)),
    small("From your audit uploaded Sep 20 · Update"),
    card(row(
        f'<svg width="96" height="96" viewBox="0 0 96 96" aria-hidden="true"><circle cx="48" cy="48" r="40" fill="none" stroke="{FILL}" stroke-width="10"></circle>'
        f'<circle cx="48" cy="48" r="40" fill="none" stroke="{INK}" stroke-width="10" stroke-dasharray="130 251" transform="rotate(-90 48 48)"></circle>'
        f'<text x="48" y="53" text-anchor="middle" font-size="16" font-weight="700" fill="{INK}">62/120</text></svg>',
        col(txt("62 of 120 credits", 15, 600), small("18 of 31 requirements met"), small("Calculated from catalog, not AI"), gap=4),
        gap=16, wrap=False)),
    card(label("Heads up"), txt("Operating Systems (CMPS 415) is blocked: take Data Structures (CMPS 390) first.", 13),
         btn("See why", "link"), fill="#FFFFFF", border=f"1.5px solid {INK}"),
    row(txt("Registration opens Nov 3", 13, 600)),
    ann("AI-2 entry · F2 · Empty"),
    inp("Ask about your degree…"),
    btn("Plan next semester", "secondary", True),
    gap=12), tab="Home", back=False))

add(0, "S3-MyPath.dc.html", "S3 My Path timeline", screen("My Path", col(
    small("Computer Science BS · 2025–26 catalog · audit Sep 20"),
    row(chip("Done", True), chip("In progress"), chip("Remaining")),
    *[card(row(txt(t, 14, 600), small(s), justify="space-between"), small(c))
      for t, s, c in [("Fall 2024", "✓ 15 cr", "CMPS 161 · MATH 200 · ENGL 101 · +2"),
                      ("Spring 2025", "✓ 16 cr", "CMPS 280 · MATH 201 · ENGL 102 · +2"),
                      ("Fall 2025", "✓ 15 cr", "CMPS 290 · BIOL 151 · HIST 101 · +2"),
                      ("Fall 2026", "In progress · 16 cr", "MATH 241 · CMPS 3290 · +3")]],
    card(row(txt("Spring 2027", 14, 600), small("Not planned"), justify="space-between"),
         small("Needed soon: CMPS 390 Data Structures, BIOL 152"), btn("Plan this semester", "link"), dashed=True),
    label("By category"),
    col(*[row(f'<span style="width: 110px; font-size: 12px">{n}</span>', f'<div style="flex-grow: 1">{progress(p)}</div>', small(f"{p}%"), wrap=False)
          for n, p in [("CS core", 45), ("Math", 100), ("Gen-ed", 70), ("Electives", 0)]], gap=6),
    gap=10), tab="My Path", back=False))

add(0, "S3-1-Requirement.dc.html", "S3.1 Requirement detail", screen("Requirement", col(
    txt("Data Structures", 20, 600), small("CMPS 390 · 3 credits · CS core"),
    card(label("Your status"), txt("Not started", 14, 600)),
    card(label("Prerequisites"), txt("✓ CMPS 280 (B, Spring 2025)"), txt("◐ MATH 241 (in progress, Fall 2026)"),
         small("You can register once MATH 241 is in progress or complete.")),
    card(label("Spring 2027 sections"), txt("01 · MWF 9:00–9:50 AM"), txt("02 · TR 11:00 AM–12:15 PM  ✓ fits your week")),
    small("Source: SLU 2025–26 catalog · Open official page"),
    ann("AI-2 entry · F2 · Empty"),
    btn("Ask about this requirement", "secondary", True),
    gap=12), tab="My Path"))

add(0, "S4-1-DraftSchedule.dc.html", "S4.1 Draft schedule", screen("Spring 2027 draft", col(
    row(txt("10 credits", 16, 600), small("3 courses"), justify="space-between"),
    f'<div style="display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 3px; font-size: 10px">'
    + "".join(f'<div style="color: {MID}; text-align: center">{d}</div>' for d in ["", "Mon", "Tue", "Wed", "Thu", "Fri"])
    + "".join(f'<div style="color: {MID}">{h}</div>' + "".join(
        (f'<div style="height: 44px; border-radius: 4px; background: {INK}; color: #FFFFFF; padding: 3px; box-sizing: border-box">{c}</div>'
         if c else f'<div style="height: 44px; border-radius: 4px; background: {FILL if d in (1, 3) else "#FFFFFF"}; border: 1px solid {LINE}"></div>')
        for d, c in enumerate([cell.get((h, i)) for i in range(5)]))
        for h, cell in [(h, {("8", 1): "BIOL 152", ("8", 3): "BIOL 152", ("9:30", 1): "CMPS 4200", ("9:30", 3): "CMPS 4200",
                              ("11", 1): "CMPS 390", ("11", 3): "CMPS 390", ("12:30", 3): "BIOL lab"}) for h in ["8", "9:30", "11", "12:30", "2"]])
    + "</div>",
    small("Shaded = your available hours. No conflicts."),
    card(txt("Undo: removed CMPS 4300", 13), btn("Undo", "link")),
    small("Lion GPS can't register you. Copy the course list into Workday registration."),
    gap=12), tab="Plan", footer=btn("Copy course list", "primary", True) + btn("Ask an advisor to review", "link")))

add(0, "S2-2-History.dc.html", "S2.2 Past conversations", screen("Past conversations", col(
    inp("Search conversations"),
    *[card(txt(t, 14, 600), small(d)) for t, d in [
        ("Can I take Operating Systems next semester?", "Today · 3 answers · 2 sources"),
        ("Electives that fit Tue/Thu", "Sep 18 · sent to advisor"),
        ("Do I still need science?", "Sep 12"),
        ("What counts as upper-level?", "Sep 2")]],
    small("Conversations are deleted after one semester."),
    gap=10), tab="Ask"))

add(0, "S7-Settings.dc.html", "S7 Settings", screen("More", col(
    label("Tools"),
    card(txt("What-if scenarios", 14, 600), small("Try a different major or minor")),
    card(txt("Ask an advisor", 14, 600), small("Send a summary to the advising office")),
    label("Settings"),
    card(txt("Program", 14, 600), small("Computer Science BS · 2025–26 catalog")),
    card(txt("Availability and interests", 14, 600), small("Tue/Thu mornings · Security, Networking")),
    card(txt("My documents and data", 14, 600), small("Audit uploaded Sep 20 · delete anytime")),
    card(txt("Notifications", 14, 600), small("Registration reminders on")),
    gap=10), tab="More", back=False))

add(0, "S7-1-MyData.dc.html", "S7.1 My documents and data", screen("My data", col(
    label("Documents"),
    card(row(txt("Academic progress report", 14, 600), small("Sep 20"), justify="space-between"),
         small("PDF deleted after reading. 31 course rows kept."), row(btn("Re-upload"), btn("View rows", "link"))),
    label("What the AI provider sees"),
    card(txt("Sent to Claude (Anthropic): your question and the 8 most relevant course records, such as “CMPS 290, Fall 2025, B”.", 13),
         txt("Never sent: your name, W-number or email.", 13, 600),
         txt("Your audit PDF is sent once to read it, then deleted.", 13)),
    label("Chats"), small("Kept for one semester, then deleted automatically."),
    f'<div style="flex-grow: 1"></div>',
    btn("Delete all my data", "danger", True),
    gap=10), tab="More"))

# ================================================================ ROW 1: AI-1 audit parsing
def upload_body(*top):
    return col(*top, gap=12)

add(1, "AI1-Empty.dc.html", "AI-1 Audit upload · Empty", screen("Add your record", col(
    txt("Upload your academic progress report", 18, 600),
    small("Lion GPS reads it so answers match your real record. No Workday login needed."),
    card(label("How to get it"), txt("1. Open Workday → Academics → Academic Progress"),
         txt("2. Choose “Download as PDF”"), txt("3. Upload it here"), hatch("[Screenshot of the Workday download button]")),
    ann("AI-1 · F1 · Empty / initial"),
    f'<div style="border: 2px dashed {INK}; border-radius: 12px; padding: 22px; display: flex; flex-direction: column; align-items: center; gap: 8px">'
    + txt("Drop your PDF here", 15, 600) + small("PDF only · up to 10 pages") + btn("Choose file", "primary") + "</div>",
    small("Your PDF is sent to our AI provider once to read it, then deleted."),
    gap=12), footer=btn("Enter courses manually instead", "link") + small("Step 1 of 3")))

add(1, "AI1-Loading.dc.html", "AI-1 Audit upload · Loading", screen("Reading your record", col(
    ann("AI-1 · F1 · Loading (10–25 s est.)"),
    card(txt("progress_report_fall26.pdf", 14, 600), small("2 pages · 184 KB")),
    progress(55),
    col(step("Uploaded", "done"), step("Reading page 2 of 2…", "now"), step("Matching courses to the SLU catalog", "todo"), step("Ready for you to check", "todo"), gap=10),
    small("This usually takes 10–25 seconds. You'll check every row before anything is saved."),
    f'<div style="flex-grow: 1"></div>',
    gap=14, extra="flex-grow: 1"), footer=btn("Cancel", "secondary", True)))

add(1, "AI1-Success.dc.html", "AI-1 Confirm what we read · Success", screen("Check your courses", col(
    ann("AI-1 · F1 · Success"),
    ai_card(txt("We found 15 courses: 10 transfer, 5 at SLU.", 14, 600), small("Compare with your PDF, then confirm."), label_text="AI-read"),
    row(chip("Transfer (10)", True), chip("SLU (5)"), chip("View original PDF")),
    f'<div style="border: 1px solid {LINE}; border-radius: 8px; overflow: hidden">'
    + course_row("ENGL 101", "English Comp I", "Delgado → ENGL 101 · A · 3 cr")
    + course_row("MATH 128", "Precalculus", "Delgado → MATH 161 · B · 3 cr")
    + course_row("ACCT 201", "Accounting I", "Delgado → ACCT 2000 · A · 3 cr")
    + course_row("ECON 201", "Macroeconomics", "Delgado → ECON 201 · C · 3 cr")
    + course_row("BIOL 101", "General Biology", "Delgado → BIOL 151 · B · 3 cr") + "</div>",
    small("+ 5 more · Add a missing course"),
    gap=10), footer=btn("Confirm 15 courses", "primary", True) + btn("Re-read PDF", "link")))

add(1, "AI1-LowConfidence.dc.html", "AI-1 Confirm what we read · Low confidence", screen("Check your courses", col(
    ann("AI-1 · F1 · Low confidence"),
    banner("2 rows need your check", "We weren't sure how these transfer credits apply. Your advisor can confirm."),
    f'<div style="border: 1px solid {LINE}; border-radius: 8px; overflow: hidden">'
    + course_row("BUSG 110", "Intro to Business", "Delgado → BUSG 1XXX · B · 3 cr", True, "Shows as “elective credit only”. It may not count toward the business core.", "Check")
    + course_row("CMIS 101", "Computer Literacy", "Delgado → not applied · A · 3 cr", True, "Marked “no equivalent”. It won't count toward your degree.", "Check")
    + course_row("ENGL 101", "English Comp I", "Delgado → ENGL 101 · A · 3 cr")
    + course_row("ACCT 201", "Accounting I", "Delgado → ACCT 2000 · A · 3 cr") + "</div>",
    row(btn("Looks right"), btn("Edit row"), btn("Ask an advisor", "link")),
    small("Unclear rows stay flagged in My Path until you or an advisor confirm them."),
    gap=10), footer=btn("Confirm (2 still flagged)", "primary", True)))

add(1, "AI1-Error.dc.html", "AI-1 Audit upload · Error", screen("Add your record", col(
    ann("AI-1 · F1 · Error (E3 wrong file / E1 service down)"),
    hatch("[Simple illustration: document with question mark]"),
    txt("This doesn't look like an academic progress report", 18, 600),
    small("We couldn't find any courses in grocery_list.pdf. Make sure you download “Academic Progress” from Workday, not your schedule or a receipt."),
    btn("Try another file", "primary", True),
    btn("See how to download it", "secondary", True),
    card(txt("Reader not working right now?", 13, 600), small("If the AI reader is down, manual entry always works. It takes about 5 minutes."), btn("Enter courses manually", "link")),
    gap=12)))

# ================================================================ ROW 2: AI-2 Ask
EX_Q = "Can I register for Operating Systems next semester?"
add(2, "AI2-Empty.dc.html", "AI-2 Ask · Empty", screen("Ask", col(
    ann("AI-2 · F2 · Empty / initial"),
    ai_card(txt("Ask me anything about your degree plan.", 15, 600),
            small("I answer only from your audit (Sep 20) and the SLU catalog, and I show my sources. For official decisions, check with your advisor.", INK),
            label_text="Lion GPS"),
    label("Try asking"),
    col(chip("Can I take Operating Systems next semester?"), chip("Which electives fit Tue/Thu?"), chip("Am I on track to graduate in 2028?"), chip("Do I still need a science class?"), gap=8),
    f'<div style="flex-grow: 1"></div>',
    gap=12, extra="flex-grow: 1"), tab="Ask", back=False, right="History",
    footer=row(f'<div style="flex-grow: 1">{inp("Type your question…")}</div>', btn("Send", "primary"), wrap=False)))

add(2, "AI2-Loading.dc.html", "AI-2 Ask · Loading (streaming)", screen("Ask", col(
    bubble_user(EX_Q),
    ann("AI-2 · F2 · Loading"),
    ai_card(row(txt("Checking your records", 13, 600), txt("• • •", 13, 700), wrap=False),
            txt("Not yet. Operating Systems (CMPS 415) needs Data Structures…", 14),
            bars(2, (85, 50)), small("Text appears as it's written (about 1–2 s to first words, est.)"), label_text="Lion GPS"),
    f'<div style="flex-grow: 1"></div>',
    gap=12, extra="flex-grow: 1"), tab="Ask", back=False, right="History",
    footer=row(f'<div style="flex-grow: 1">{inp("Wait for the answer or stop…")}</div>', btn("Stop"), wrap=False)))

add(2, "AI2-Success.dc.html", "AI-2 Ask · Success", screen("Ask", col(
    bubble_user(EX_Q),
    ann("AI-2 · F2 · Success"),
    ai_card(txt("Not yet. Operating Systems (CMPS 415) needs Data Structures (CMPS 390) and Computer Organization (CMPS 290). You've finished CMPS 290 but haven't taken CMPS 390.", 14),
            txt("If you take CMPS 390 this spring, you can take CMPS 415 next fall.", 14),
            label("Based on"),
            row(src("CMPS 415 prerequisites · catalog"), src("Your CMPS 290 · Fall 2025 · B"), src("CMPS 390 status · not taken")),
            label_text="Based on your records"),
    ann("User control · F2"),
    row(btn("Helpful"), btn("Not helpful"), btn("Regenerate"), btn("Edit question", "link")),
    row(chip("When is CMPS 390 offered?"), chip("Plan my spring")),
    gap=10), tab="Ask", back=False, right="History",
    footer=row(f'<div style="flex-grow: 1">{inp("Ask a follow-up…")}</div>', btn("Send", "primary"), wrap=False) + btn("Ask an advisor", "link")))

add(2, "AI2-LowConfidence.dc.html", "AI-2 Ask · Low confidence", screen("Ask", col(
    bubble_user("Does ACCT 2020 count toward my CS degree?"),
    ann("AI-2 · F2 · Low confidence (certainty: insufficient)"),
    ai_card(txt("I couldn't confirm this.", 15, 600),
            txt("Your records and the CS requirements don't mention ACCT 2020, so I can't tell whether it counts as an elective.", 14),
            label("What's missing"), small("The free-elective rules for your catalog year.", INK),
            label("I checked"), row(src("CS upper-level electives · catalog"), src("Degree total · catalog")),
            label_text="Not confirmed"),
    btn("Ask an advisor (summary drafted for you)", "primary", True),
    row(btn("Rephrase"), btn("Add detail", "link")),
    gap=10), tab="Ask", back=False, right="History",
    footer=row(f'<div style="flex-grow: 1">{inp("Ask something else…")}</div>', btn("Send", "primary"), wrap=False)))

add(2, "AI2-Error.dc.html", "AI-2 Ask · Error", screen("Ask", col(
    ann("AI-2 · F2 · Error (E1 unavailable / timeout, E2 bad answer)"),
    banner("AI answers are paused right now", "Your path, requirements and advisor handoff still work."),
    bubble_user(EX_Q),
    card(txt("I couldn't answer this time.", 14, 600), small("We tried twice. Your question is saved, so you don't have to retype it."),
         row(btn("Retry", "primary"), btn("Notify me when it's answered", "link"))),
    label("Meanwhile"),
    card(txt("CMPS 415 Operating Systems", 14, 600), small("Open the requirement to see its prerequisites yourself"), btn("Open in My Path", "link")),
    btn("Ask an advisor", "secondary", True),
    gap=10), tab="Ask", back=False, right="History"))

add(2, "S2-1-SourceDrawer.dc.html", "S2.1 Source drawer (AI-2 verification)", screen("Ask", col(
    bubble_user(EX_Q), bars(4)),
    tab="Ask", back=False,
    overlay=(f'<div style="position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; background: rgba(30,30,28,0.45)"></div>'
             f'<div style="position: absolute; left: 0; bottom: 0; width: {W}px; height: 560px; box-sizing: border-box; background: #FFFFFF; '
             f'border-radius: 16px 16px 0 0; padding: 16px; display: flex; flex-direction: column; gap: 12px">'
             f'<div style="align-self: center; width: 40px; height: 4px; border-radius: 2px; background: {LINE}"></div>'
             + ann("AI-2 · F2 · Success → verify source")
             + txt("3 sources for this answer", 16, 600)
             + card(label("SLU catalog 2025–26 · CS core"), txt("CMPS 415 Operating Systems (3 cr). Prerequisite: CMPS 390 and CMPS 290.", 13), row(btn("Open official page", "link"), btn("This is wrong", "link")))
             + card(label("Your audit · Sep 20"), txt("Completed: CMPS 290, Fall 2025, grade B.", 13), btn("This is wrong", "link"))
             + card(label("Your audit · Sep 20"), txt("CMPS 390 Data Structures: not taken.", 13), btn("This is wrong", "link"))
             + btn("Close", "secondary", True) + "</div>")))

# ================================================================ ROW 3: AI-3 Plan
def opt_card(title, courses, cr, why, srcs, extra=None):
    items = [row(txt(title, 15, 600), small(cr), justify="space-between")]
    items += [txt(c, 13) for c in courses]
    items += [label("Why this?"), small(why, INK), row(*[src(s) for s in srcs])]
    if extra: items.append(extra)
    items.append(row(btn("Add to draft", "primary"), btn("Swap a course"), btn("Dismiss", "link")))
    return ai_card(*items, label_text="Suggestion")

add(3, "AI3-Empty.dc.html", "AI-3 Plan · Empty", screen("Plan Spring 2027", col(
    ann("AI-3 · F3 · Empty / initial"),
    card(row(txt("Your week", 14, 600), btn("Edit", "link"), justify="space-between"), small("Tue/Thu, 8 AM–2 PM", INK)),
    label("How many credits?"), row(chip("6"), chip("9", True), chip("12"), chip("15")),
    label("Interests"), row(chip("Security", True), chip("Networking", True), chip("+ Add")),
    small("Suggestions use your remaining requirements, prerequisites and the public Spring 2027 schedule."),
    f'<div style="flex-grow: 1"></div>',
    gap=12, extra="flex-grow: 1"), tab="Plan", back=False,
    footer=btn("Suggest courses", "primary", True) + btn("Or browse all courses myself", "link")))

add(3, "AI3-Loading.dc.html", "AI-3 Plan · Loading", screen("Plan Spring 2027", col(
    ann("AI-3 · F3 · Loading (5–10 s est.)"),
    col(step("Checking what you've completed", "done"), step("Checking prerequisites…", "now"), step("Matching your Tue/Thu times", "todo"), gap=10),
    progress(40),
    card(bars(3)), card(bars(3)),
    small("If this takes more than 10 seconds, you can cancel and browse courses yourself."),
    gap=14), tab="Plan", back=False, footer=btn("Cancel", "secondary", True)))

add(3, "AI3-Success.dc.html", "AI-3 Plan · Success", screen("Plan Spring 2027", col(
    ann("AI-3 · F3 · Success (2 alternatives)"),
    small("2 options that fit Tue/Thu before 2 PM"),
    opt_card("A · Stay on track for capstone", ["CMPS 390 Data Structures · TR 11:00", "CMPS 4200 HCI · TR 9:30", "BIOL 152 · TR 8:00 + Thu lab"], "10 cr",
             "CMPS 390 unlocks OS and Enterprise Systems. BIOL 152 finishes your science sequence.", ["CMPS 390 · catalog", "Your BIOL 151", "Spring schedule"]),
    card(row(txt("B · Lighter semester", 14, 600), small("6 cr"), justify="space-between"), small("CMPS 390 + CMPS 4200 · Tap to expand")),
    gap=10), tab="Plan", back=False, footer=row(btn("Regenerate"), btn("Change constraints", "link"))))

add(3, "AI3-LowConfidence.dc.html", "AI-3 Plan · Low confidence", screen("Plan Spring 2027", col(
    ann("AI-3 · F3 · Low confidence (certainty: partial)"),
    banner("Only 1 option fits your hours", "Cybersecurity (CMPS 4300) meets TR 3:30 PM, outside your hours."),
    opt_card("A · Best available fit", ["CMPS 390 Data Structures · TR 11:00", "CMPS 4200 HCI · TR 9:30"], "6 cr",
             "Partly confirmed: the BIOL 152 lab time isn't in the spring schedule yet, so I left it out.", ["CMPS 390 · catalog", "Spring schedule"]),
    row(btn("Widen my hours"), btn("Ask an advisor", "link")),
    gap=10), tab="Plan", back=False))

add(3, "AI3-Error.dc.html", "AI-3 Plan · Error", screen("Plan Spring 2027", col(
    ann("AI-3 · F3 · Error → fallback (no AI)"),
    banner("Couldn't make suggestions right now", "You can still browse courses by requirement."),
    btn("Retry", "primary", True),
    label("Browse by requirement"),
    *[card(row(txt(t, 14, 600), small(s), justify="space-between"), small(c)) for t, s, c in [
        ("CS core", "3 left", "CMPS 390 · TR 11:00 fits your week"),
        ("CS electives", "9 cr left", "CMPS 4200 · TR 9:30 fits · CMPS 4300 doesn't fit"),
        ("Science sequence", "1 left", "BIOL 152 · TR 8:00 fits")]],
    gap=10), tab="Plan", back=False))

# ================================================================ ROW 4: AI-4 What-if
def compare(now, new):
    rows = [("Semesters left", now[0], new[0]), ("Credits that count", now[1], new[1]), ("Requirements left", now[2], new[2])]
    head = (f'<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 6px; font-size: 12px; font-weight: 600; color: {MID}">'
            f'<span></span><span>Now</span><span>Biology BS</span></div>')
    body = "".join(f'<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 6px; font-size: 13px; padding: 6px 0; border-top: 1px solid {LINE}">'
                   f'<span style="color: {MID}">{esc(a)}</span><span style="font-weight: 600">{esc(b)}</span><span style="font-weight: 600">{esc(c)}</span></div>' for a, b, c in rows)
    return card(label("Calculated from catalog, not AI"), head + body)

add(4, "AI4-Empty.dc.html", "AI-4 What-if · Empty", screen("What if…", col(
    ann("AI-4 · F4 · Empty / initial"),
    txt("See how a change affects your path", 18, 600),
    card(label("Now"), txt("Undeclared (General Studies) · 30 credits", 14, 600)),
    label("I want to"), row(chip("Declare a major", True), chip("Add a minor")),
    inp("Choose a program from the catalog ▾", lbl="Program"),
    small("Programs come from the SLU catalog list, so there's nothing to type or misspell."),
    f'<div style="flex-grow: 1"></div>',
    gap=12, extra="flex-grow: 1"), tab="More", footer=btn("Compare", "primary", True)))

add(4, "AI4-Loading.dc.html", "AI-4 What-if · Loading", screen("Undeclared → Biology BS", col(
    compare(("8", "30", "28"), ("7", "27", "25")),
    ann("AI-4 · F4 · Loading (5–10 s est.)"),
    ai_card(txt("Explaining the difference…", 14, 600), bars(4), label_text="Explanation"),
    small("The numbers above are ready now. The explanation takes a few seconds."),
    gap=12), tab="More", footer=btn("Cancel explanation", "secondary", True)))

add(4, "AI4-Success.dc.html", "AI-4 What-if · Success", screen("Undeclared → Biology BS", col(
    compare(("8", "30", "28"), ("7", "27", "25")),
    ann("AI-4 · F4 · Success"),
    ai_card(txt("Declaring Biology now could save you a semester. 27 of your 30 credits count, including BIOL 151 and CHEM 121.", 14),
            txt("MATH 162 wouldn't count: Biology requires MATH 200 instead.", 14),
            row(src("Biology BS · catalog"), src("Your MATH 162 · Spring 2026")), label_text="Based on the catalog"),
    row(btn("Save scenario", "primary"), btn("Try another"), btn("Ask an advisor", "link")),
    gap=10), tab="More"))

add(4, "AI4-LowConfidence.dc.html", "AI-4 What-if · Low confidence", screen("Undeclared → Pre-med", col(
    ann("AI-4 · F4 · Low confidence (certainty: partial)"),
    banner("Partly confirmed", "Pre-med isn't a separate program in the catalog."),
    ai_card(txt("I can compare you to Biology BS, the most common pre-med path, but medical-school prerequisites come from the Pre-Health advising office, not the catalog.", 14),
            row(src("Biology BS · catalog")), label_text="Not fully confirmed"),
    btn("Compare to Biology BS instead", "primary", True),
    btn("Ask the Pre-Health advisor", "secondary", True),
    gap=12), tab="More"))

add(4, "AI4-Error.dc.html", "AI-4 What-if · Error", screen("Undeclared → Biology BS", col(
    compare(("8", "30", "28"), ("7", "27", "25")),
    ann("AI-4 · F4 · Error (explanation only)"),
    card(txt("Explanation unavailable right now", 14, 600), small("The comparison above is still accurate: it's calculated from the catalog."),
         row(btn("Retry", "primary"), btn("See course-by-course list", "link"))),
    btn("Save scenario", "secondary", True),
    gap=12), tab="More"))

# ================================================================ ROW 5: AI-5 Advisor handoff
DRAFT = ("Ngozi (Business BBA, transferred from Delgado) wants to know whether BUSG 110 Intro to Business can count "
         "toward the business core. Her audit lists it as “elective credit only.” She also asks whether CMIS 101 "
         "can apply anywhere, since it shows as “not applied.” Lion GPS could not confirm either from the catalog.")

def draft_box(text, flag=None):
    extra = f'<span style="background: {FLAG}; padding: 0 2px">{esc(flag)}</span>' if flag else ""
    return (f'<div style="border: 1.5px solid {INK}; border-radius: 8px; padding: 12px; font-size: 13px; line-height: 1.5; min-height: 150px">'
            f'{esc(text)} {extra}</div>')

add(5, "AI5-Empty.dc.html", "AI-5 Advisor handoff · Empty", screen("Ask an advisor", col(
    ann("AI-5 · F5 · Empty / initial"),
    txt("We'll draft a short summary for the advising office.", 15, 600),
    card(label("Included"), txt("✓ This conversation (4 messages)"), txt("✓ Audit date: Sep 20"), txt("✓ Flagged rows: BUSG 110, CMIS 101")),
    inp("What do you most want the advisor to answer? (optional)", 90, "Your note"),
    small("You'll see and edit everything before it's sent."),
    gap=12), footer=btn("Draft summary", "primary", True) + btn("Write it myself", "link")))

add(5, "AI5-Loading.dc.html", "AI-5 Advisor handoff · Loading", screen("Ask an advisor", col(
    ann("AI-5 · F5 · Loading (3–5 s est.)"),
    txt("Drafting a summary of your question…", 15, 600),
    card(bars(6, (100, 96, 88, 100, 72, 40))),
    small("Nothing is sent until you press Send."),
    gap=12), footer=btn("Cancel", "secondary", True)))

add(5, "AI5-Success.dc.html", "AI-5 Advisor handoff · Success", screen("Ask an advisor", col(
    ann("AI-5 · F5 · Success (editable)"),
    inp("Business advising office ▾", lbl="To"),
    label("Summary · edit freely"), draft_box(DRAFT),
    row(chip("Conversation attached"), chip("Audit Sep 20 attached")),
    row(btn("Regenerate"), btn("Undo my edits", "link")),
    gap=10), footer=btn("Send to advisor", "primary", True) + btn("Cancel", "link")))

add(5, "AI5-LowConfidence.dc.html", "AI-5 Advisor handoff · Low confidence", screen("Ask an advisor", col(
    ann("AI-5 · F5 · Low confidence"),
    banner("Please check the highlighted part", "I wasn't sure which office handles transfer credit appeals."),
    inp("Choose an office ▾ (required)", lbl="To"),
    label("Summary · edit freely"), draft_box(DRAFT[:170] + "…", "[Check: should this go to the Registrar's transfer credit office instead?]"),
    gap=10), footer=btn("Send (choose an office first)", "primary", True, disabled=True) + btn("Cancel", "link")))

add(5, "AI5-Error.dc.html", "AI-5 Advisor handoff · Error", screen("Ask an advisor", col(
    ann("AI-5 · F5 · Error → fallback template"),
    banner("Couldn't draft a summary", "Fill in this short template instead. Your conversation is still attached."),
    inp("Business advising office ▾", lbl="To"),
    inp("e.g. Can BUSG 110 count toward the business core?", 64, "My question"),
    inp("e.g. Checked my audit; asked Lion GPS", 64, "What I've already checked"),
    row(chip("Conversation attached"), chip("Audit Sep 20 attached")),
    btn("Retry the draft", "link"),
    gap=10), footer=btn("Send to advisor", "primary", True)))

# ================================================================ canvas.json
ROW_TITLES = [
    "Core screens · non-AI and AI entry points",
    "AI-1 Audit parsing · F1 · Ngozi · Claude Sonnet",
    "AI-2 Ask a question · F2 · Amara · MiniLM + Claude Sonnet",
    "AI-3 Course suggestions · F3 · Chidi · MiniLM + Claude Sonnet",
    "AI-4 What-if · F4 · Amara · MiniLM + Claude Sonnet",
    "AI-5 Advisor handoff · F5 · Ngozi · Claude Sonnet",
]
GAPX, TITLE_H = 80, 300
ROW_PITCH = H + 120 + TITLE_H
boards, order, notes = {}, [], {}
counts = {}
for r, fname, title, html in BOARDS:
    i = counts.get(r, 0); counts[r] = i + 1
    x = i * (W + GAPX); y = r * ROW_PITCH
    boards[fname] = {"x": x, "y": y, "w": W, "h": H, "title": title}
    order.append(fname)
    with open(os.path.join(OUT, "project", fname), "w") as f:
        f.write(html)
for r, t in enumerate(ROW_TITLES):
    n = counts[r]
    notes[f"row{r}"] = {"x": 0, "y": r * ROW_PITCH - 260, "text": t, "kind": "title1", "maxW": n * W + (n - 1) * GAPX}
notes["legend"] = {"x": -560, "y": 0, "w": 440, "maxH": 700, "fill": "blue", "size": "m",
                   "text": ("How to read these wireframes\n\n"
                            "Blue tags = annotations: AI feature · flow · state.\n\n"
                            "Dashed box with a small label = AI-generated content. Solid boxes = facts calculated from the catalog (not AI).\n\n"
                            "Underlined chips = citations; tapping one opens the source drawer (S2.1).\n\n"
                            "Yellow = needs the student's attention (low confidence, unclear rows).\n\n"
                            "Each AI row shows all 5 required states: empty, loading, success, low confidence, error.\n\n"
                            "Response times marked est. will be updated from the technical spike.")}
canvas = {"v": 3, "createdOnFiles": {"v": 1, "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
          "title": "Lion GPS Phase 2 Wireframes", "launch": {"view": "canvas"}, "pages": [],
          "boards": boards, "order": order, "notes": notes, "designSystems": []}
with open(os.path.join(OUT, "project", "canvas.json"), "w") as f:
    json.dump(canvas, f, indent=1)
print(len(BOARDS), "boards;", counts)
