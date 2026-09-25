"""
app/db/database.py
Robust local SQLite persistence layer for EduTrack standalone desktop application.
Features:
- Cross-platform user-writable data directory resolution (platformdirs).
- Automatic timestamped database backups before startup/migrations with retention pruning.
- Automatic schema initialization on first launch with seed data.
- Safe try/except wrapped transactions with structured rotating file logging.
- Authentication and user management helpers.
"""

import os
import sys
import shutil
import sqlite3
import json
from datetime import datetime

from app.db.paths import (
    APP_DATA_DIR, LOG_DIR, BACKUP_DIR, DB_PATH, LOG_PATH, logger
)


class DatabaseManager:
    """Manages SQLite database connections, backups, schema migrations, and CRUD operations."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._create_backup_if_exists()
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Create and return a new SQLite database connection with row factory enabled."""
        conn = sqlite3.connect(self.db_path, timeout=20.0)
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for high concurrency & robustness
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA foreign_keys=ON;")
        except Exception:
            pass
        return conn

    def _create_backup_if_exists(self):
        """Create a timestamped backup before any schema check or migration."""
        try:
            if os.path.exists(self.db_path) and os.path.getsize(self.db_path) > 0:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"edutrack_backup_{ts}.db"
                backup_dest = os.path.join(BACKUP_DIR, backup_filename)
                shutil.copy2(self.db_path, backup_dest)
                logger.info(f"Pre-launch backup created successfully: {backup_dest}")
                self._prune_backups(max_keep=10)
        except Exception as e:
            logger.exception(f"Failed to create pre-launch database backup: {e}")

    def _prune_backups(self, max_keep: int = 10):
        """Retain only the most recent N backup files to prevent disk bloating."""
        try:
            if not os.path.exists(BACKUP_DIR):
                return
            backups = []
            for f in os.listdir(BACKUP_DIR):
                if f.startswith("edutrack_backup_") and f.endswith(".db"):
                    fp = os.path.join(BACKUP_DIR, f)
                    backups.append((os.path.getmtime(fp), fp))
            backups.sort(key=lambda x: x[0], reverse=True)
            for _, old_file in backups[max_keep:]:
                try:
                    os.remove(old_file)
                    logger.debug(f"Pruned old backup: {old_file}")
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"Error during backup pruning: {e}")

    def _init_db(self):
        """Create database tables if they do not exist and seed initial records on first run."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # ── 1. Users Table ────────────────────────────────────────────
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    designation TEXT,
                    student_id TEXT,
                    class_name TEXT,
                    email TEXT,
                    phone TEXT,
                    created_at TEXT
                )
                """)

                # ── 2. Classes Table ──────────────────────────────────────────
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS classes (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    grade INTEGER NOT NULL,
                    section TEXT NOT NULL,
                    class_teacher TEXT,
                    room TEXT,
                    students INTEGER DEFAULT 0
                )
                """)

                # ── 3. Teachers Table ─────────────────────────────────────────
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS teachers (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    subject TEXT,
                    qualification TEXT,
                    phone TEXT,
                    email TEXT,
                    experience INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'Active',
                    class_teacher_of TEXT
                )
                """)

                # ── 4. Students Table ─────────────────────────────────────────
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    class_name TEXT NOT NULL,
                    roll_no TEXT,
                    gender TEXT,
                    phone TEXT,
                    email TEXT,
                    parent_name TEXT,
                    admission_date TEXT,
                    status TEXT DEFAULT 'Active'
                )
                """)

                # ── 5. Attendance Table ───────────────────────────────────────
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS attendance (
                    id TEXT PRIMARY KEY,
                    student_id TEXT NOT NULL,
                    student_name TEXT,
                    class_name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    status TEXT NOT NULL
                )
                """)

                # ── 6. Marks Table ────────────────────────────────────────────
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS marks (
                    id TEXT PRIMARY KEY,
                    student_id TEXT NOT NULL,
                    student_name TEXT,
                    class_name TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    assessment TEXT NOT NULL,
                    total_marks INTEGER NOT NULL,
                    obtained INTEGER NOT NULL,
                    grade TEXT
                )
                """)

                # ── 7. Timetable Table ────────────────────────────────────────
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS timetable (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    class_name TEXT NOT NULL,
                    day TEXT NOT NULL,
                    period_index INTEGER NOT NULL,
                    subject TEXT,
                    teacher TEXT
                )
                """)

                # ── 8. Settings Table ─────────────────────────────────────────
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
                """)

                # ── 9. Activity Log Table ─────────────────────────────────────
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    user TEXT,
                    action TEXT,
                    details TEXT
                )
                """)

                # ── 10. Support Tickets Table ─────────────────────────────────
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS support_tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT,
                    user TEXT,
                    category TEXT,
                    subject TEXT,
                    message TEXT,
                    status TEXT DEFAULT 'Open'
                )
                """)

                conn.commit()

            # Seed data if tables are empty
            self._seed_if_needed()
            logger.info("Database initialized successfully.")
        except Exception as e:
            logger.exception(f"Fatal error initializing database schema: {e}")
            raise

    def _seed_if_needed(self):
        """Seed initial dataset if the database is newly initialized."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) as count FROM classes")
                row = cursor.fetchone()
                if row and row["count"] > 0:
                    return  # Already seeded

                logger.info("Empty database detected. Seeding baseline application data...")
                from app.data.sample_data import (
                    CLASSES, TEACHERS, STUDENTS, ATTENDANCE_RECORDS,
                    MARKS_RECORDS, TIMETABLE_DATA
                )
                from app.config import DEMO_MODE, DEMO_USERS

                # Seed Users from Demo Fixtures if in DEMO_MODE or available
                if DEMO_USERS:
                    for role, user in DEMO_USERS.items():
                        cursor.execute("""
                        INSERT OR REPLACE INTO users (username, password, role, full_name, designation, student_id, class_name, email, phone, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            user.get("username"),
                            user.get("password"),
                            role,
                            user.get("full_name"),
                            user.get("designation"),
                            user.get("student_id"),
                            user.get("class"),
                            user.get("email", ""),
                            user.get("phone", ""),
                            datetime.now().isoformat()
                        ))

                # Seed Classes
                for c in CLASSES:
                    cursor.execute("""
                    INSERT OR REPLACE INTO classes (id, name, grade, section, class_teacher, room, students)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (c["id"], c["name"], c["grade"], c["section"], c["class_teacher"], c["room"], c["students"]))

                # Seed Teachers
                for t in TEACHERS:
                    cursor.execute("""
                    INSERT OR REPLACE INTO teachers (id, name, subject, qualification, phone, email, experience, status, class_teacher_of)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (t["id"], t["name"], t["subject"], t["qualification"], t["phone"], t["email"], t["experience"], t["status"], t["class_teacher_of"]))

                # Seed Students
                for s in STUDENTS:
                    cursor.execute("""
                    INSERT OR REPLACE INTO students (id, name, class_name, roll_no, gender, phone, email, parent_name, admission_date, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (s["id"], s["name"], s["class"], s["roll_no"], s["gender"], s["phone"], s["email"], s["parent_name"], s["admission_date"], s["status"]))

                # Seed Attendance
                for a in ATTENDANCE_RECORDS:
                    cursor.execute("""
                    INSERT OR REPLACE INTO attendance (id, student_id, student_name, class_name, date, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (a["id"], a["student_id"], a["student_name"], a["class"], a["date"], a["status"]))

                # Seed Marks
                for m in MARKS_RECORDS:
                    cursor.execute("""
                    INSERT OR REPLACE INTO marks (id, student_id, student_name, class_name, subject, assessment, total_marks, obtained, grade)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (m["id"], m["student_id"], m["student_name"], m["class"], m["subject"], m["assessment"], m["total_marks"], m["obtained"], m["grade"]))

                # Seed Timetable
                for class_name, days in TIMETABLE_DATA.items():
                    for day, periods in days.items():
                        for idx, subject in enumerate(periods):
                            cursor.execute("""
                            INSERT INTO timetable (class_name, day, period_index, subject, teacher)
                            VALUES (?, ?, ?, ?, ?)
                            """, (class_name, day, idx, subject, ""))

                # Seed Settings
                default_settings = {
                    "school_name": "Dar-e-Arqam School",
                    "academic_session": "2025-2026",
                    "current_term": "First Term (Mid-Term)",
                    "ui_density": "Comfortable",
                    "high_contrast": "False",
                    "notifications_sms": "True",
                    "notifications_email": "True",
                    "offline_sync_interval": "15 mins",
                }
                for k, v in default_settings.items():
                    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, v))

                conn.commit()
                logger.info("Baseline data seeded successfully.")
        except Exception as e:
            logger.exception(f"Error seeding database records: {e}")

    # ── Authentication Operations ──────────────────────────────────────────────

    def authenticate_user(self, username: str, password: str) -> dict | None:
        """Authenticate user against SQLite users table. Returns user dictionary on success, None on failure."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
                row = cursor.fetchone()
                if row:
                    return {
                        "username": row["username"],
                        "password": row["password"],
                        "role": row["role"],
                        "full_name": row["full_name"],
                        "designation": row["designation"],
                        "student_id": row["student_id"],
                        "class": row["class_name"],
                        "email": row["email"],
                        "phone": row["phone"],
                    }
                return None
        except Exception as e:
            logger.exception(f"Authentication database error for username '{username}': {e}")
            return None

    def update_user_password(self, username: str, new_password: str) -> bool:
        """Update password for an existing user."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.exception(f"Failed to update password for user '{username}': {e}")
            return False

    # ── CRUD Operations ────────────────────────────────────────────────────────

    def get_all_students(self) -> list[dict]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM students ORDER BY class_name, CAST(roll_no AS INTEGER)")
                return [
                    {
                        "id": r["id"],
                        "name": r["name"],
                        "class": r["class_name"],
                        "roll_no": r["roll_no"],
                        "gender": r["gender"],
                        "phone": r["phone"],
                        "email": r["email"],
                        "parent_name": r["parent_name"],
                        "admission_date": r["admission_date"],
                        "status": r["status"]
                    }
                    for r in cursor.fetchall()
                ]
        except Exception as e:
            logger.exception(f"Failed to fetch students from database: {e}")
            return []

    def save_student(self, s: dict) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT OR REPLACE INTO students (id, name, class_name, roll_no, gender, phone, email, parent_name, admission_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    s["id"], s["name"], s["class"], s.get("roll_no", "1"),
                    s.get("gender", "M"), s.get("phone", ""), s.get("email", ""),
                    s.get("parent_name", ""), s.get("admission_date", ""), s.get("status", "Active")
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.exception(f"Failed to save student record: {e}")
            return False

    def delete_student(self, student_id: str) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
                conn.commit()
                return True
        except Exception as e:
            logger.exception(f"Failed to delete student ID '{student_id}': {e}")
            return False

    def get_all_teachers(self) -> list[dict]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM teachers ORDER BY name")
                return [dict(r) for r in cursor.fetchall()]
        except Exception as e:
            logger.exception(f"Failed to fetch teachers: {e}")
            return []

    def save_teacher(self, t: dict) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT OR REPLACE INTO teachers (id, name, subject, qualification, phone, email, experience, status, class_teacher_of)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    t["id"], t["name"], t.get("subject", ""), t.get("qualification", ""),
                    t.get("phone", ""), t.get("email", ""), t.get("experience", 0),
                    t.get("status", "Active"), t.get("class_teacher_of", "")
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.exception(f"Failed to save teacher record: {e}")
            return False

    def delete_teacher(self, teacher_id: str) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
                conn.commit()
                return True
        except Exception as e:
            logger.exception(f"Failed to delete teacher ID '{teacher_id}': {e}")
            return False

    def get_all_classes(self) -> list[dict]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM classes ORDER BY grade, section")
                return [dict(r) for r in cursor.fetchall()]
        except Exception as e:
            logger.exception(f"Failed to fetch classes: {e}")
            return []

    def save_class(self, c: dict) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT OR REPLACE INTO classes (id, name, grade, section, class_teacher, room, students)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    c["id"], c["name"], c.get("grade", 1), c.get("section", "A"),
                    c.get("class_teacher", ""), c.get("room", ""), c.get("students", 0)
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.exception(f"Failed to save class record: {e}")
            return False

    def get_all_attendance(self) -> list[dict]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM attendance ORDER BY date DESC")
                return [
                    {
                        "id": r["id"],
                        "student_id": r["student_id"],
                        "student_name": r["student_name"],
                        "class": r["class_name"],
                        "date": r["date"],
                        "status": r["status"]
                    }
                    for r in cursor.fetchall()
                ]
        except Exception as e:
            logger.exception(f"Failed to fetch attendance: {e}")
            return []

    def save_attendance_batch(self, records: list[dict]) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                for r in records:
                    cursor.execute("""
                    INSERT OR REPLACE INTO attendance (id, student_id, student_name, class_name, date, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (r["id"], r["student_id"], r["student_name"], r["class"], r["date"], r["status"]))
                conn.commit()
                return True
        except Exception as e:
            logger.exception(f"Failed to save attendance batch: {e}")
            return False

    def get_all_marks(self) -> list[dict]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM marks")
                return [
                    {
                        "id": r["id"],
                        "student_id": r["student_id"],
                        "student_name": r["student_name"],
                        "class": r["class_name"],
                        "subject": r["subject"],
                        "assessment": r["assessment"],
                        "total_marks": r["total_marks"],
                        "obtained": r["obtained"],
                        "grade": r["grade"]
                    }
                    for r in cursor.fetchall()
                ]
        except Exception as e:
            logger.exception(f"Failed to fetch marks: {e}")
            return []

    def save_marks_batch(self, records: list[dict]) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                for r in records:
                    cursor.execute("""
                    INSERT OR REPLACE INTO marks (id, student_id, student_name, class_name, subject, assessment, total_marks, obtained, grade)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        r["id"], r["student_id"], r["student_name"], r["class"],
                        r["subject"], r["assessment"], r["total_marks"], r["obtained"], r["grade"]
                    ))
                conn.commit()
                return True
        except Exception as e:
            logger.exception(f"Failed to save marks batch: {e}")
            return False

    def get_timetable(self) -> dict:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM timetable ORDER BY class_name, day, period_index")
                rows = cursor.fetchall()
                tt: dict[str, dict[str, list[str]]] = {}
                for r in rows:
                    c = r["class_name"]
                    d = r["day"]
                    if c not in tt:
                        tt[c] = {}
                    if d not in tt[c]:
                        tt[c][d] = ["—"] * 8
                    idx = r["period_index"]
                    if 0 <= idx < 8:
                        tt[c][d][idx] = r["subject"] or "—"
                return tt
        except Exception as e:
            logger.exception(f"Failed to fetch timetable: {e}")
            return {}

    def update_timetable_slot(self, class_name: str, day: str, period_index: int, subject: str) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                DELETE FROM timetable WHERE class_name = ? AND day = ? AND period_index = ?
                """, (class_name, day, period_index))
                cursor.execute("""
                INSERT INTO timetable (class_name, day, period_index, subject, teacher)
                VALUES (?, ?, ?, ?, '')
                """, (class_name, day, period_index, subject))
                conn.commit()
                return True
        except Exception as e:
            logger.exception(f"Failed to update timetable slot: {e}")
            return False

    def get_settings(self) -> dict[str, str]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM settings")
                return {r["key"]: r["value"] for r in cursor.fetchall()}
        except Exception as e:
            logger.exception(f"Failed to fetch settings: {e}")
            return {}

    def set_setting(self, key: str, value: str):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
                conn.commit()
        except Exception as e:
            logger.exception(f"Failed to set setting '{key}': {e}")

    def log_activity(self, user: str, action: str, details: str = ""):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO activity_log (timestamp, user, action, details)
                VALUES (?, ?, ?, ?)
                """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user, action, details))
                conn.commit()
        except Exception as e:
            logger.exception(f"Failed to record activity log: {e}")

    def get_activity_log(self, limit: int = 100) -> list[dict]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM activity_log ORDER BY id DESC LIMIT ?", (limit,))
                return [dict(r) for r in cursor.fetchall()]
        except Exception as e:
            logger.exception(f"Failed to fetch activity log: {e}")
            return []

    def create_support_ticket(self, user: str, category: str, subject: str, message: str) -> int:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO support_tickets (created_at, user, category, subject, message, status)
                VALUES (?, ?, ?, ?, ?, 'Open')
                """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user, category, subject, message))
                conn.commit()
                return cursor.lastrowid or 0
        except Exception as e:
            logger.exception(f"Failed to create support ticket: {e}")
            return 0


# Global singleton database instance
db = DatabaseManager()
