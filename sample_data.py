"""
Sample degree-audit data for the Lion GPS technical spike.

This is MOCK data modeled on a typical SLU Computer Science (BS) degree audit
and on the Phase 1 personas. It is not an official SLU record. In the real app
these records come from (1) the public SLU catalog for program requirements and
(2) the student's own uploaded Workday academic progress report / transcript.

Every record has a stable ID so the model can cite it and the UI can link to it.
"""

# ---- Program requirements (would come from the public catalog) -------------
REQUIREMENTS = [
    {"id": "REQ-CS-CORE-1", "text": "CS core: CMPS 161 Algorithm Design and Implementation I (3 cr). No prerequisite beyond MATH 161 placement."},
    {"id": "REQ-CS-CORE-2", "text": "CS core: CMPS 280 Algorithm Design and Implementation II (3 cr). Prerequisite: CMPS 161 with a C or better."},
    {"id": "REQ-CS-CORE-3", "text": "CS core: CMPS 290 Computer Organization (3 cr). Prerequisite: CMPS 280."},
    {"id": "REQ-CS-CORE-4", "text": "CS core: CMPS 390 Data Structures (3 cr). Prerequisite: CMPS 280 and MATH 241."},
    {"id": "REQ-CS-CORE-5", "text": "CS core: CMPS 3290 Computer Networks (3 cr). Prerequisite: CMPS 290."},
    {"id": "REQ-CS-CORE-6", "text": "CS core: CMPS 415 Operating Systems (3 cr). Prerequisite: CMPS 390 and CMPS 290."},
    {"id": "REQ-CS-CORE-7", "text": "CS core: CMPS 4150 Enterprise Systems (3 cr). Prerequisite: CMPS 390."},
    {"id": "REQ-CS-CAP",    "text": "CS capstone: CMPS 4910 Senior Project (3 cr). Prerequisite: senior standing (90+ credit hours) and CMPS 4150."},
    {"id": "REQ-CS-ELEC",   "text": "CS upper-level electives: 9 credit hours from CMPS 4000-level courses not otherwise required (e.g., CMPS 4200 HCI, CMPS 4300 Cybersecurity, CMPS 4400 Machine Learning)."},
    {"id": "REQ-MATH-1",    "text": "Mathematics: MATH 200 Calculus I (4 cr) and MATH 201 Calculus II (4 cr)."},
    {"id": "REQ-MATH-2",    "text": "Mathematics: MATH 241 Discrete Mathematics (3 cr). Prerequisite: MATH 200."},
    {"id": "REQ-GENED-HUM", "text": "General education humanities: 6 credit hours from the approved humanities list (e.g., ENGL 230, PHIL 101, HIST 101)."},
    {"id": "REQ-GENED-SCI", "text": "General education natural science: 9 credit hours including one two-course sequence (e.g., BIOL 151/152 or CHEM 121/122)."},
    {"id": "REQ-TOTAL",     "text": "Degree total: 120 credit hours minimum, including 39 upper-level (300/400-level) hours and a 2.0 overall GPA."},
]

# ---- Student record: "Chidi" persona (CS junior, works 20 hrs/week) ---------
TRANSCRIPT_CHIDI = [
    {"id": "TR-001", "text": "Completed: CMPS 161, Fall 2024, grade A."},
    {"id": "TR-002", "text": "Completed: CMPS 280, Spring 2025, grade B."},
    {"id": "TR-003", "text": "Completed: CMPS 290, Fall 2025, grade B."},
    {"id": "TR-004", "text": "Completed: MATH 200, Fall 2024, grade B; MATH 201, Spring 2025, grade C."},
    {"id": "TR-005", "text": "In progress: MATH 241 Discrete Mathematics, Fall 2026."},
    {"id": "TR-006", "text": "In progress: CMPS 3290 Computer Networks, Fall 2026."},
    {"id": "TR-007", "text": "Completed: ENGL 101, ENGL 102, HIST 101 (humanities, 3 cr)."},
    {"id": "TR-008", "text": "Completed: BIOL 151 (4 cr). BIOL 152 not taken."},
    {"id": "TR-009", "text": "Credit hours earned: 62. Overall GPA: 3.1. Classification: Junior."},
    {"id": "TR-010", "text": "Student-provided availability: can only attend classes Tuesday and Thursday before 2:00 PM (works off campus)."},
]

# ---- Spring 2027 offerings (would come from the public class schedule) -------
SCHEDULE = [
    {"id": "SCH-01", "text": "Spring 2027: CMPS 390 Data Structures, section 01, MWF 9:00-9:50 AM."},
    {"id": "SCH-02", "text": "Spring 2027: CMPS 390 Data Structures, section 02, TR 11:00 AM-12:15 PM."},
    {"id": "SCH-03", "text": "Spring 2027: CMPS 4200 HCI, section 01, TR 9:30-10:45 AM."},
    {"id": "SCH-04", "text": "Spring 2027: CMPS 4300 Cybersecurity, section 01, TR 3:30-4:45 PM."},
    {"id": "SCH-05", "text": "Spring 2027: CMPS 4400 Machine Learning, section 01, MW 2:00-3:15 PM."},
    {"id": "SCH-06", "text": "Spring 2027: BIOL 152, section 03, TR 8:00-9:15 AM (lab Thursday 12:30-2:20 PM)."},
    {"id": "SCH-07", "text": "Spring 2027: PHIL 101, online asynchronous."},
]

ALL_RECORDS = REQUIREMENTS + TRANSCRIPT_CHIDI + SCHEDULE

# ---- Realistic questions, one per core feature from the Phase 1 proposal ------
TEST_QUESTIONS = [
    {"id": "Q1", "feature": "Elective recommendation", "persona": "Chidi",
     "text": "What CS electives can I take next spring that fit my Tuesday/Thursday schedule?"},
    {"id": "Q2", "feature": "Prerequisite detection", "persona": "Chidi",
     "text": "Can I register for Operating Systems (CMPS 415) next semester?"},
    {"id": "Q3", "feature": "On-track check", "persona": "Chidi",
     "text": "Am I on track to graduate in two more years? What's still left?"},
    {"id": "Q4", "feature": "Gen-ed gap", "persona": "Chidi",
     "text": "Do I still need any science classes? I only remember taking one bio course."},
    {"id": "Q5", "feature": "What-if scenario", "persona": "Chidi",
     "text": "If I took Data Structures and HCI in the spring, would that keep me on schedule for the senior project?"},
    {"id": "Q6", "feature": "Capstone readiness", "persona": "Chidi",
     "text": "When is the earliest I can start the senior project, CMPS 4910?"},
]
