"""
app/state.py
Global application state – backed by SQLite persistence layer and shared across all screens.
"""

from app.config import ROLE_ADMIN, ROLE_TEACHER, ROLE_PARENT
from app.db.database import db


class AppState:
    """
    Singleton-style state holder.
    The single instance lives on the App object and is passed to every screen.
    Persists mutations to SQLite and maintains in-memory mirrors for high performance.
    """

    def __init__(self):
        # ── Auth ──────────────────────────────────────────────────────────────
        self.current_user: dict | None = None   # Full user dict from DEMO_USERS / DB
        self.current_role: str = ROLE_ADMIN

        # ── Navigation ────────────────────────────────────────────────────────
        self.active_screen: str = "dashboard"
        self.previous_screen: str | None = None

        # ── Filters / Context (shared between screens) ────────────────────────
        self.selected_class:   str = "All"
        self.selected_section: str = "All"
        self.selected_subject: str = "All"
        self.filters: dict = {}

        # ── App-level UI Settings ─────────────────────────────────────────────
        self.ui_density: str = "Comfortable"  # "Comfortable" | "Compact"
        self.high_contrast: bool = False
        self.offline_mode: bool = False

        # ── Mutable Data Mirrors (loaded from SQLite) ─────────────────────────
        self.students:   list[dict] = []
        self.teachers:   list[dict] = []
        self.classes:    list[dict] = []
        self.attendance: list[dict] = []
        self.marks:      list[dict] = []
        self.timetable:  dict       = {}
        self.settings:   dict       = {}

        self.reload_from_db()

    # ── Database Sync ─────────────────────────────────────────────────────────

    def reload_from_db(self):
        """Reload all active data mirrors from the SQLite database."""
        self.students   = db.get_all_students()
        self.teachers   = db.get_all_teachers()
        self.classes    = db.get_all_classes()
        self.attendance = db.get_all_attendance()
        self.marks      = db.get_all_marks()
        self.timetable  = db.get_timetable()
        self.settings   = db.get_settings()
        self.ui_density = self.settings.get("ui_density", "Comfortable")
        self.high_contrast = self.settings.get("high_contrast", "False") == "True"

    # ── Auth Helpers ──────────────────────────────────────────────────────────

    def login(self, role: str, user_dict: dict):
        self.current_role = role
        self.current_user = user_dict
        db.log_activity(user_dict.get("username", "user"), "Login", f"Logged in as {role}")

    def logout(self):
        if self.current_user:
            db.log_activity(self.current_user.get("username", "user"), "Logout", "Logged out of session")
        self.current_user = None
        self.current_role = ROLE_ADMIN
        self.active_screen = "dashboard"

    # ── Role-Specific Data Scoping ────────────────────────────────────────────

    def get_classes_for_role(self) -> list[str]:
        """Return class names visible to the current user."""
        if self.current_role == ROLE_TEACHER and self.current_user:
            teacher_name = self.current_user.get("full_name", "")
            assigned = [
                c["name"] for c in self.classes
                if c.get("class_teacher") == teacher_name
            ]
            return assigned if assigned else [c["name"] for c in self.classes]
        elif self.current_role == ROLE_PARENT and self.current_user:
            child_class = self.current_user.get("class")
            return [child_class] if child_class else [c["name"] for c in self.classes]
        return [c["name"] for c in self.classes]

    def get_linked_child(self) -> dict | None:
        """For Parent role: returns the student record corresponding to parent's linked child."""
        if not self.current_user:
            return None
        student_id = self.current_user.get("student_id")
        if student_id:
            for s in self.students:
                if s["id"] == student_id:
                    return s
        # Fallback to matching child name or parent name
        pname = self.current_user.get("full_name", "")
        for s in self.students:
            if s.get("parent_name") == pname:
                return s
        return self.students[2] if len(self.students) > 2 else (self.students[0] if self.students else None)

    def get_students_by_class(self, class_name: str) -> list[dict]:
        if class_name == "All":
            return self.students
        return [s for s in self.students if s["class"] == class_name]

    def compute_attendance_pct(self, student_id: str) -> float:
        """Compute attendance percentage for a given student."""
        records = [r for r in self.attendance if r["student_id"] == student_id]
        if not records:
            return 100.0
        present = sum(1 for r in records if r["status"] == "Present")
        return round((present / len(records)) * 100, 1)

    # ── Data Mutation Pass-Throughs ───────────────────────────────────────────

    def save_student(self, student_data: dict) -> bool:
        res = db.save_student(student_data)
        if res:
            self.students = db.get_all_students()
            actor = self.current_user.get("username", "system") if self.current_user else "system"
            db.log_activity(actor, "Save Student", f"Saved student {student_data.get('name')} ({student_data.get('id')})")
        return res

    def delete_student(self, student_id: str) -> bool:
        res = db.delete_student(student_id)
        if res:
            self.students = db.get_all_students()
            actor = self.current_user.get("username", "system") if self.current_user else "system"
            db.log_activity(actor, "Delete Student", f"Deleted student ID: {student_id}")
        return res

    def save_teacher(self, teacher_data: dict) -> bool:
        res = db.save_teacher(teacher_data)
        if res:
            self.teachers = db.get_all_teachers()
            actor = self.current_user.get("username", "system") if self.current_user else "system"
            db.log_activity(actor, "Save Teacher", f"Saved teacher {teacher_data.get('name')} ({teacher_data.get('id')})")
        return res

    def delete_teacher(self, teacher_id: str) -> bool:
        res = db.delete_teacher(teacher_id)
        if res:
            self.teachers = db.get_all_teachers()
            actor = self.current_user.get("username", "system") if self.current_user else "system"
            db.log_activity(actor, "Delete Teacher", f"Deleted teacher ID: {teacher_id}")
        return res

    def save_attendance_batch(self, records: list[dict]) -> bool:
        res = db.save_attendance_batch(records)
        if res:
            self.attendance = db.get_all_attendance()
            actor = self.current_user.get("username", "system") if self.current_user else "system"
            db.log_activity(actor, "Mark Attendance", f"Updated {len(records)} attendance records")
        return res

    def save_marks_batch(self, records: list[dict]) -> bool:
        res = db.save_marks_batch(records)
        if res:
            self.marks = db.get_all_marks()
            actor = self.current_user.get("username", "system") if self.current_user else "system"
            db.log_activity(actor, "Save Marks", f"Updated {len(records)} mark entries")
        return res

    def update_timetable_slot(self, class_name: str, day: str, period_index: int, subject: str) -> bool:
        res = db.update_timetable_slot(class_name, day, period_index, subject)
        if res:
            self.timetable = db.get_timetable()
            actor = self.current_user.get("username", "system") if self.current_user else "system"
            db.log_activity(actor, "Update Timetable", f"{class_name} {day} period {period_index+1} -> {subject}")
        return res
