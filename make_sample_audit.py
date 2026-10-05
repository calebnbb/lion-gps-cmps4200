"""Generates sample_audit.pdf: a MOCK academic progress report (Ngozi persona,
transfer business major) used to test AI audit parsing. Not an official SLU document."""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
c = canvas.Canvas("sample_audit.pdf", pagesize=letter)
y = 750
def line(t, size=10, bold=False, dy=15):
    global y
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size); c.drawString(50, y, t); y -= dy
line("SAMPLE - Academic Progress Report (mock data for testing)", 13, True, 22)
line("Student: N. Sample     Program: Business Administration, BBA     Catalog: 2025-2026")
line("Classification: Sophomore     Institutional GPA: 3.40     Transfer hours accepted: 30", dy=25)
line("TRANSFER CREDIT (Delgado Community College)", 11, True)
for t in ["ENGL 101  English Composition I      3  A   -> ENGL 101",
          "ENGL 102  English Composition II     3  B   -> ENGL 102",
          "MATH 128  Precalculus Algebra        3  B   -> MATH 161",
          "ACCT 201  Principles of Accounting I 3  A   -> ACCT 2000",
          "BUSG 110  Intro to Business          3  B   -> BUSG 1XXX (elective credit only)",
          "ECON 201  Macroeconomics             3  C   -> ECON 201",
          "CMIS 101  Computer Literacy          3  A   -> NOT APPLIED (no equivalent)",
          "BIOL 101  General Biology            3  B   -> BIOL 151",
          "HIST 101  World Civilization         3  B   -> HIST 101",
          "SPCH 130  Public Speaking            3  A   -> COMM 211"]:
    line("   " + t, 9)
y -= 8
line("SLU COURSEWORK", 11, True)
for t in ["Spring 2026  ACCT 2010  Principles of Accounting II  3  B",
          "Spring 2026  ECON 202   Microeconomics               3  B",
          "Spring 2026  MATH 162   Finite Mathematics           3  C",
          "Fall 2026    BUAD 2050  Business Statistics          3  IP",
          "Fall 2026    MGMT 3050  Principles of Management     3  IP"]:
    line("   " + t, 9)
y -= 8
line("REQUIREMENTS STATUS", 11, True)
for t in ["Business core ............... 5 of 13 courses complete",
          "General education ........... 27 of 39 hours complete",
          "Free electives .............. 3 of 9 hours (BUSG 1XXX applied)",
          "Upper-level hours ........... 0 of 39"]:
    line("   " + t, 9)
c.save(); print("wrote sample_audit.pdf")
