"""
app/state.py
Global application state – shared across all screens.
"""

from app.config import ROLE_ADMIN


class AppState:
    """
    Singleton-style state holder.
    The single instance lives on the App object and is passed to every screen.
    """

    def __init__(self):
        # ── Auth ──────────────────────────────────────────────────────────────
        self.current_user: dict | None = None   # Full user dict from DEMO_USERS
        self.current_role: str = ROLE_ADMIN

        # ── Navigation ────────────────────────────────────────────────────────
        self.active_screen: str = "dashboard"
        self.previous_screen: str | None = None

        # ── Filters / Context (shared between screens) ────────────────────────
        self.selected_class:   str = "All"
        self.selected_section: str = "All"
        self.selected_subject: str = "All"

        # ── Mutable Data Mirrors (in-memory "database") ───────────────────────
        # These get populated from sample_data and can be mutated by CRUD ops
        from app.data.sample_data import (
            STUDENTS, TEACHERS, CLASSES, ATTENDANCE_RECORDS,
            MARKS_RECORDS, TIMETABLE_DATA
        )
        self.students:          list[dict] = list(STUDENTS)
        self.teachers:          list[dict] = list(TEACHERS)
        self.classes:           list[dict] = list(CLASSES)
        self.attendance:        list[dict] = list(ATTENDANCE_RECORDS)
        self.marks:             list[dict] = list(MARKS_RECORDS)
        self.timetable:         dict       = dict(TIMETABLE_DATA)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def login(self, role: str, user_dict: dict):
        self.current_role = role
        self.current_user = user_dict

    def logout(self):
        self.current_user = None
        self.current_role = ROLE_ADMIN
        self.active_screen = "dashboard"

    def get_classes_for_role(self) -> list[str]:
        """Return class names visible to the current user."""
        from app.config import ROLE_TEACHER
        if self.current_role == ROLE_TEACHER:
            teacher_name = self.current_user.get("full_name", "")
            return [
                c["name"] for c in self.classes
                if c.get("class_teacher") == teacher_name
            ]
        return [c["name"] for c in self.classes]

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
