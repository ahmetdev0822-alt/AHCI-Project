"""
app/data/sample_data.py
Realistic Pakistani school sample data for Dar-e-Arqam School EduTrack demo.
"""

import random
from datetime import date, timedelta

# ─── Classes ─────────────────────────────────────────────────────────────────
CLASSES = [
    {"id": "CL01", "name": "Class 1-A",  "grade": 1,  "section": "A", "class_teacher": "Ustaza Nadia Rashid",  "room": "101", "students": 28},
    {"id": "CL02", "name": "Class 1-B",  "grade": 1,  "section": "B", "class_teacher": "Ustaza Samina Khatoon","room": "102", "students": 26},
    {"id": "CL03", "name": "Class 2-A",  "grade": 2,  "section": "A", "class_teacher": "Ustaz Tariq Mahmood",  "room": "201", "students": 30},
    {"id": "CL04", "name": "Class 3-A",  "grade": 3,  "section": "A", "class_teacher": "Ustaza Rabia Jamil",   "room": "301", "students": 29},
    {"id": "CL05", "name": "Class 4-A",  "grade": 4,  "section": "A", "class_teacher": "Ustaz Imran Siddiqui", "room": "401", "students": 31},
    {"id": "CL06", "name": "Class 5-A",  "grade": 5,  "section": "A", "class_teacher": "Ustaza Huma Nawaz",    "room": "501", "students": 27},
    {"id": "CL07", "name": "Class 6-A",  "grade": 6,  "section": "A", "class_teacher": "Ustaz Bilal Ahmed",    "room": "601", "students": 33},
    {"id": "CL08", "name": "Class 7-A",  "grade": 7,  "section": "A", "class_teacher": "Ustaza Amina Sheikh",  "room": "701", "students": 32},
    {"id": "CL09", "name": "Class 8-A",  "grade": 8,  "section": "A", "class_teacher": "Ustaz Salman Riaz",    "room": "801", "students": 35},
    {"id": "CL10", "name": "Class 9-A",  "grade": 9,  "section": "A", "class_teacher": "Ustaz Farhan Malik",   "room": "901", "students": 38},
    {"id": "CL11", "name": "Class 9-B",  "grade": 9,  "section": "B", "class_teacher": "Ustaza Zara Ahmed",    "room": "902", "students": 36},
    {"id": "CL12", "name": "Class 10-A", "grade": 10, "section": "A", "class_teacher": "Ustaz Kashif Raza",    "room": "1001","students": 40},
]

# ─── Teachers ────────────────────────────────────────────────────────────────
TEACHERS = [
    {"id": "T001", "name": "Ustaz Bilal Ahmed",      "subject": "Mathematics",     "qualification": "M.Sc Mathematics",  "phone": "0321-1234567", "email": "bilal@darearqam.edu.pk",    "experience": 8,  "status": "Active",  "class_teacher_of": "Class 6-A"},
    {"id": "T002", "name": "Ustaza Nadia Rashid",    "subject": "English",         "qualification": "M.A English Lit",   "phone": "0333-2345678", "email": "nadia@darearqam.edu.pk",    "experience": 5,  "status": "Active",  "class_teacher_of": "Class 1-A"},
    {"id": "T003", "name": "Ustaz Tariq Mahmood",    "subject": "Science",         "qualification": "M.Sc Chemistry",    "phone": "0312-3456789", "email": "tariq@darearqam.edu.pk",    "experience": 10, "status": "Active",  "class_teacher_of": "Class 2-A"},
    {"id": "T004", "name": "Ustaza Rabia Jamil",     "subject": "Urdu",            "qualification": "M.A Urdu",          "phone": "0345-4567890", "email": "rabia@darearqam.edu.pk",    "experience": 7,  "status": "Active",  "class_teacher_of": "Class 3-A"},
    {"id": "T005", "name": "Ustaz Imran Siddiqui",   "subject": "Islamic Studies", "qualification": "M.A Islamiat",      "phone": "0301-5678901", "email": "imran@darearqam.edu.pk",    "experience": 12, "status": "Active",  "class_teacher_of": "Class 4-A"},
    {"id": "T006", "name": "Ustaza Huma Nawaz",      "subject": "Social Studies",  "qualification": "M.A History",       "phone": "0311-6789012", "email": "huma@darearqam.edu.pk",     "experience": 6,  "status": "Active",  "class_teacher_of": "Class 5-A"},
    {"id": "T007", "name": "Ustaza Amina Sheikh",    "subject": "Computer Science","qualification": "BS Computer Sci",   "phone": "0322-7890123", "email": "amina@darearqam.edu.pk",    "experience": 4,  "status": "Active",  "class_teacher_of": "Class 7-A"},
    {"id": "T008", "name": "Ustaz Salman Riaz",      "subject": "Physics",         "qualification": "M.Sc Physics",      "phone": "0331-8901234", "email": "salman@darearqam.edu.pk",   "experience": 9,  "status": "Active",  "class_teacher_of": "Class 8-A"},
    {"id": "T009", "name": "Ustaz Farhan Malik",     "subject": "Chemistry",       "qualification": "M.Sc Chemistry",    "phone": "0341-9012345", "email": "farhan@darearqam.edu.pk",   "experience": 11, "status": "Active",  "class_teacher_of": "Class 9-A"},
    {"id": "T010", "name": "Ustaza Zara Ahmed",      "subject": "Biology",         "qualification": "M.Sc Zoology",      "phone": "0352-0123456", "email": "zara@darearqam.edu.pk",     "experience": 5,  "status": "Active",  "class_teacher_of": "Class 9-B"},
    {"id": "T011", "name": "Ustaz Kashif Raza",      "subject": "Pakistan Studies","qualification": "M.A Pak Studies",   "phone": "0362-1234567", "email": "kashif@darearqam.edu.pk",   "experience": 8,  "status": "Active",  "class_teacher_of": "Class 10-A"},
    {"id": "T012", "name": "Ustaza Samina Khatoon",  "subject": "Arts & Drawing",  "qualification": "BFA Fine Arts",     "phone": "0302-2345678", "email": "samina@darearqam.edu.pk",   "experience": 3,  "status": "On Leave","class_teacher_of": "Class 1-B"},
]

# ─── Students ────────────────────────────────────────────────────────────────
_student_data = [
    # Class 8-A (focus class for teacher demo – Ustaz Bilal / admin can see all)
    ("S001","Ahmed Hassan Khan",     "Class 8-A","1","M","0321-1111111","ahmed.khan@gmail.com",    "Khan Bahadur Ali",  "2026-01-15","Active"),
    ("S002","Muhammad Usman Tariq",  "Class 8-A","2","M","0333-2222222","usman.t@gmail.com",       "Tariq Hussain",     "2025-08-20","Active"),
    ("S003","Fatima Bibi Chaudhry",  "Class 8-A","3","F","0312-3333333","fatima.c@gmail.com",      "Rao Chaudhry",      "2026-02-10","Active"),
    ("S004","Ayesha Siddiqui",       "Class 8-A","4","F","0345-4444444","ayesha.s@gmail.com",      "Dr. Wasim Siddiqui","2025-09-05","Active"),
    ("S005","Ali Raza Butt",         "Class 8-A","5","M","0301-5555555","ali.butt@gmail.com",      "Rana Abdul Basit",  "2026-03-18","Active"),
    ("S006","Zainab Noor",           "Class 8-A","6","F","0311-6666666","zainab.n@gmail.com",      "Noor Muhammad",     "2025-10-22","Active"),
    ("S007","Hamza Sheikh",          "Class 8-A","7","M","0322-7777777","hamza.sh@gmail.com",      "Sheikh Amjad Ali",  "2026-01-30","Active"),
    ("S008","Sara Batool",           "Class 8-A","8","F","0331-8888888","sara.b@gmail.com",        "Ghulam Batool",     "2025-11-14","Active"),
    ("S009","Omar Farooq",           "Class 8-A","9","M","0341-9999999","omar.f@gmail.com",        "Farooq Ahmed",      "2026-04-02","Active"),
    ("S010","Madiha Pervaiz",        "Class 8-A","10","F","0352-0101010","madiha.p@gmail.com",     "Pervaiz Alam",      "2025-12-08","Active"),
    ("S011","Talha Rehman",          "Class 8-A","11","M","0362-1111222","talha.r@gmail.com",      "Abdul Rehman Gul",  "2026-05-16","Active"),
    ("S012","Nimra Shahid",          "Class 8-A","12","F","0302-2222333","nimra.sh@gmail.com",     "Shahid Mehmood",    "2025-07-25","Active"),
    # Class 9-A
    ("S013","Bilal Mustafa",         "Class 9-A","1","M","0321-3333444","bilal.m@gmail.com",       "Mustafa Kamal",     "2026-01-10","Active"),
    ("S014","Hira Baig",             "Class 9-A","2","F","0333-4444555","hira.b@gmail.com",        "Baig Sahib",        "2025-08-15","Active"),
    ("S015","Sohail Akhtar",         "Class 9-A","3","M","0312-5555666","sohail.a@gmail.com",      "Akhtar Nawaz",      "2026-02-20","Active"),
    ("S016","Mariam Zahid",          "Class 9-A","4","F","0345-6666777","mariam.z@gmail.com",      "Zahid Hussain",     "2025-09-28","Active"),
    ("S017","Asad Mehmood",          "Class 9-A","5","M","0301-7777888","asad.m@gmail.com",        "Mehmood Sultan",    "2026-03-12","Active"),
    ("S018","Aroha Malik",           "Class 9-A","6","F","0311-8888999","aroha.m@gmail.com",       "Malik Irfan",       "2025-10-30","Active"),
    # Class 10-A
    ("S019","Zubair Ahmed",          "Class 10-A","1","M","0322-9999000","zubair.a@gmail.com",     "Ahmed Nawaz",       "2026-01-05","Active"),
    ("S020","Sana Riaz",             "Class 10-A","2","F","0331-0000111","sana.r@gmail.com",       "Riaz Ahmed",        "2025-08-10","Active"),
    ("S021","Adeel Qureshi",         "Class 10-A","3","M","0341-1111222","adeel.q@gmail.com",      "Qureshi Sahib",     "2026-02-14","Active"),
    ("S022","Kiran Anwar",           "Class 10-A","4","F","0352-2222333","kiran.a@gmail.com",      "Anwar Hussain",     "2025-09-18","Active"),
    # Class 6-A (Ustaz Bilal's class)
    ("S023","Raza Ul Haq",           "Class 6-A","1","M","0362-3333444","raza.h@gmail.com",        "Haq Nawaz",         "2026-01-22","Active"),
    ("S024","Amna Bibi",             "Class 6-A","2","F","0302-4444555","amna.b@gmail.com",        "Bibi Jan",          "2025-08-28","Active"),
    ("S025","Yasir Khan",            "Class 6-A","3","M","0321-5555666","yasir.k@gmail.com",       "Khan Muhammad",     "2026-03-08","Active"),
    ("S026","Nadia Aslam",           "Class 6-A","4","F","0333-6666777","nadia.a@gmail.com",       "Aslam Pervaiz",     "2025-10-16","Active"),
    ("S027","Usama Javed",           "Class 6-A","5","M","0312-7777888","usama.j@gmail.com",       "Javed Iqbal",       "2026-04-24","Active"),
    ("S028","Sobia Rashid",          "Class 6-A","6","F","0345-8888999","sobia.r@gmail.com",       "Rashid Khan",       "2025-11-02","Active"),
    # Class 1-A
    ("S029","Abdullah Mir",          "Class 1-A","1","M","0301-9999000","abdullah.m@gmail.com",    "Mir Sahib",         "2026-01-18","Active"),
    ("S030","Maryam Toor",           "Class 1-A","2","F","0311-0000111","maryam.t@gmail.com",      "Toor Khan",         "2025-08-24","Active"),
]

STUDENTS = [
    {
        "id":            row[0],
        "name":          row[1],
        "class":         row[2],
        "roll_no":       row[3],
        "gender":        row[4],
        "phone":         row[5],
        "email":         row[6],
        "parent_name":   row[7],
        "admission_date":row[8],
        "status":        row[9],
    }
    for row in _student_data
]

# ─── Attendance Records ───────────────────────────────────────────────────────
def _generate_attendance():
    records = []
    today = date.today()
    statuses = ["Present", "Present", "Present", "Present", "Absent", "Late"]
    for student in STUDENTS:
        # Generate 30 days of records
        for i in range(30):
            day = today - timedelta(days=i)
            if day.weekday() >= 5:   # Skip weekends
                continue
            records.append({
                "id":         f"ATT{student['id']}{day.isoformat()}",
                "student_id": student["id"],
                "student_name": student["name"],
                "class":      student["class"],
                "date":       day.isoformat(),
                "status":     random.choice(statuses),
            })
    return records

ATTENDANCE_RECORDS = _generate_attendance()

# ─── Marks Records ────────────────────────────────────────────────────────────
SUBJECTS = {
    "Class 6-A":  ["Mathematics", "English", "Urdu", "Science", "Islamic Studies"],
    "Class 8-A":  ["Mathematics", "English", "Urdu", "Physics", "Chemistry", "Islamic Studies"],
    "Class 9-A":  ["Mathematics", "English", "Urdu", "Physics", "Chemistry", "Biology"],
    "Class 10-A": ["Mathematics", "English", "Urdu", "Physics", "Chemistry", "Biology", "Pak Studies"],
    "Class 1-A":  ["Mathematics", "English", "Urdu", "Drawing"],
    "Class 1-B":  ["Mathematics", "English", "Urdu", "Drawing"],
    "Class 2-A":  ["Mathematics", "English", "Urdu", "Science"],
    "Class 3-A":  ["Mathematics", "English", "Urdu", "Science"],
    "Class 4-A":  ["Mathematics", "English", "Urdu", "Science", "Islamic Studies"],
    "Class 5-A":  ["Mathematics", "English", "Urdu", "Science", "Social Studies"],
    "Class 7-A":  ["Mathematics", "English", "Urdu", "Science", "Computer Science"],
    "Class 9-B":  ["Mathematics", "English", "Urdu", "Physics", "Chemistry", "Biology"],
}

ASSESSMENT_TYPES = ["Monthly Test", "Mid-Term", "Final Exam", "Quiz", "Assignment"]

def _generate_marks():
    records = []
    mid = {
        "Mathematics": (55, 100), "English": (50, 100), "Urdu": (60, 100),
        "Science": (50, 100), "Physics": (45, 100), "Chemistry": (40, 100),
        "Biology": (50, 100), "Islamic Studies": (65, 100), "Pak Studies": (60, 100),
        "Social Studies": (55, 100), "Computer Science": (60, 100), "Drawing": (65, 100),
    }
    assessment = "Mid-Term"
    for student in STUDENTS:
        subjects = SUBJECTS.get(student["class"], ["Mathematics", "English", "Urdu"])
        for subject in subjects:
            mn, mx = mid.get(subject, (40, 100))
            obtained = random.randint(mn, mx)
            records.append({
                "id":           f"MK{student['id']}{subject[:3]}",
                "student_id":   student["id"],
                "student_name": student["name"],
                "class":        student["class"],
                "subject":      subject,
                "assessment":   assessment,
                "total_marks":  mx,
                "obtained":     obtained,
                "grade":        _grade(obtained, mx),
            })
    return records

def _grade(obtained: int, total: int) -> str:
    pct = (obtained / total) * 100
    if pct >= 90: return "A+"
    if pct >= 80: return "A"
    if pct >= 70: return "B+"
    if pct >= 60: return "B"
    if pct >= 50: return "C"
    return "F"

MARKS_RECORDS = _generate_marks()

# ─── Timetable ────────────────────────────────────────────────────────────────
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
PERIODS = ["8:00–8:45", "8:45–9:30", "9:30–10:15", "10:15–10:30 (Break)",
           "10:30–11:15", "11:15–12:00", "12:00–12:45", "12:45–1:00 (Zuhr)"]

TIMETABLE_DATA = {
    "Class 8-A": {
        "Monday":    ["Mathematics","English","Physics","—","Chemistry","Urdu","Islamic Studies","—"],
        "Tuesday":   ["Urdu","Mathematics","English","—","Physics","Chemistry","Urdu","—"],
        "Wednesday": ["English","Physics","Mathematics","—","Urdu","Islamic Studies","Mathematics","—"],
        "Thursday":  ["Chemistry","Urdu","English","—","Mathematics","Physics","English","—"],
        "Friday":    ["Islamic Studies","Mathematics","Urdu","—","English","Physics","—","—"],
    },
    "Class 6-A": {
        "Monday":    ["Mathematics","English","Urdu","—","Science","Islamic Studies","Mathematics","—"],
        "Tuesday":   ["Urdu","Science","Mathematics","—","English","Mathematics","Urdu","—"],
        "Wednesday": ["English","Mathematics","Science","—","Urdu","Islamic Studies","English","—"],
        "Thursday":  ["Science","Urdu","English","—","Mathematics","Science","Urdu","—"],
        "Friday":    ["Islamic Studies","Mathematics","English","—","Urdu","Science","—","—"],
    },
}

# ─── Dashboard Stats ─────────────────────────────────────────────────────────
def get_dashboard_stats(state=None):
    """Compute live dashboard statistics."""
    from datetime import date as dt
    today_str = dt.today().isoformat()
    today_att = [r for r in ATTENDANCE_RECORDS if r["date"] == today_str]
    total_students = len(STUDENTS)
    if today_att:
        present_today = sum(1 for r in today_att if r["status"] == "Present")
        att_pct = round((present_today / len(today_att)) * 100, 1)
    else:
        present_today = 0
        att_pct = 0.0

    # Low attendance (<75%)
    from collections import defaultdict
    student_records: dict[str, list] = defaultdict(list)
    for r in ATTENDANCE_RECORDS:
        student_records[r["student_id"]].append(r)

    low_att = 0
    for sid, recs in student_records.items():
        if recs:
            pres = sum(1 for r in recs if r["status"] == "Present")
            pct = (pres / len(recs)) * 100
            if pct < 75:
                low_att += 1

    return {
        "total_students":    total_students,
        "total_teachers":    len(TEACHERS),
        "total_classes":     len(CLASSES),
        "attendance_pct":    att_pct,
        "present_today":     present_today,
        "low_att_students":  low_att,
        "active_students":   sum(1 for s in STUDENTS if s["status"] == "Active"),
        "on_leave_teachers": sum(1 for t in TEACHERS if t["status"] == "On Leave"),
    }
