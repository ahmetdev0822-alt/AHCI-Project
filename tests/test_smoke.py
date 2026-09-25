"""
tests/test_smoke.py
Headless automated smoke test suite for EduTrack.
Validates module imports, cross-platform path resolution, SQLite database initialization,
automated pre-launch backups, authentication, and core CRUD persistence without requiring a display.
"""

import os
import sys
import pytest


def test_core_imports():
    """Verify all system modules and screen classes resolve without syntax or import errors."""
    import app.config as config
    assert config.APP_NAME == "EduTrack"
    assert config.WINDOW_MIN_SIZE[0] <= 1024
    assert config.WINDOW_MIN_SIZE[1] <= 768

    import app.data.demo_fixtures as demo_fixtures
    assert "Administrator" in demo_fixtures.DEMO_USERS
    assert "Teacher" in demo_fixtures.DEMO_USERS
    assert "Parent" in demo_fixtures.DEMO_USERS

    import app.data.sample_data as sample_data
    assert len(sample_data.CLASSES) > 0
    assert len(sample_data.STUDENTS) > 0
    assert len(sample_data.TEACHERS) > 0

    import app.db.paths as paths
    assert os.path.isabs(paths.APP_DATA_DIR)
    assert os.path.isabs(paths.DB_PATH)
    assert os.path.isabs(paths.LOG_PATH)
    assert os.path.isabs(paths.BACKUP_DIR)

    from app.db.database import DatabaseManager, db
    assert db is not None

    import app.state as state
    assert hasattr(state, "AppState")

    # Import components
    from app.components.cards import MetricCard, StatusBadge, SectionHeader, AlertCard
    from app.components.toast import ToastManager
    from app.components.state_view import StateView

    # Import all 14 screens
    from app.screens.login import LoginScreen
    from app.screens.dashboard import DashboardScreen
    from app.screens.parent_dashboard import ParentDashboardScreen
    from app.screens.students import StudentsScreen
    from app.screens.teachers import TeachersScreen
    from app.screens.classes import ClassesScreen
    from app.screens.attendance import AttendanceScreen
    from app.screens.marks import MarksScreen
    from app.screens.timetable import TimetableScreen
    from app.screens.reports import ReportsScreen
    from app.screens.onboarding import OnboardingScreen
    from app.screens.settings import SettingsScreen
    from app.screens.profile import ProfileScreen
    from app.screens.help import HelpScreen


def test_paths_and_logging(tmp_path):
    """Verify path helpers and logger initialization."""
    from app.db.paths import (
        get_app_data_dir, get_app_log_dir, get_app_backup_dir, get_db_path, get_log_path, logger
    )
    data_dir = get_app_data_dir()
    log_dir = get_app_log_dir()
    backup_dir = get_app_backup_dir()

    assert os.path.exists(data_dir)
    assert os.path.exists(log_dir)
    assert os.path.exists(backup_dir)

    logger.info("Headless smoke test logging verification.")
    log_path = get_log_path()
    assert os.path.exists(os.path.dirname(log_path))


def test_sqlite_database_lifecycle(tmp_path):
    """Verify headless SQLite schema auto-initialization, seeding, backups, and CRUD."""
    from app.db.database import DatabaseManager

    test_db_file = str(tmp_path / "test_edutrack.db")
    db = DatabaseManager(db_path=test_db_file)

    # 1. Verify schema tables and initial seed data
    students = db.get_all_students()
    assert len(students) > 0, "Students table should be seeded on first run"

    classes = db.get_all_classes()
    assert len(classes) > 0, "Classes table should be seeded on first run"

    teachers = db.get_all_teachers()
    assert len(teachers) > 0, "Teachers table should be seeded on first run"

    attendance = db.get_all_attendance()
    assert len(attendance) > 0, "Attendance table should be seeded on first run"

    marks = db.get_all_marks()
    assert len(marks) > 0, "Marks table should be seeded on first run"

    timetable = db.get_timetable()
    assert len(timetable) > 0, "Timetable table should be seeded on first run"

    settings = db.get_settings()
    assert settings.get("school_name") == "Dar-e-Arqam School"

    # 2. Test Authentication
    auth_admin = db.authenticate_user("admin", "admin123")
    assert auth_admin is not None
    assert auth_admin["role"] == "Administrator"

    invalid_auth = db.authenticate_user("admin", "wrong_password")
    assert invalid_auth is None

    # 3. Test Student CRUD
    new_student = {
        "id": "S999",
        "name": "Test Student Automation",
        "class": "Class 8-A",
        "roll_no": "99",
        "gender": "M",
        "phone": "0300-9999999",
        "email": "test.student@example.com",
        "parent_name": "Test Guardian",
        "admission_date": "2026-09-25",
        "status": "Active"
    }
    assert db.save_student(new_student) is True
    updated_students = db.get_all_students()
    assert any(s["id"] == "S999" for s in updated_students)

    assert db.delete_student("S999") is True
    updated_students_post_delete = db.get_all_students()
    assert not any(s["id"] == "S999" for s in updated_students_post_delete)

    # 4. Test Teacher CRUD
    new_teacher = {
        "id": "T99",
        "name": "Prof. Test Automation",
        "subject": "Robotics",
        "qualification": "Ph.D. Computer Science",
        "phone": "0300-8888888",
        "email": "robotics@example.com",
        "experience": 10,
        "status": "Active",
        "class_teacher_of": "Class 8-A"
    }
    assert db.save_teacher(new_teacher) is True
    assert db.delete_teacher("T99") is True

    # 5. Test Password Update
    assert db.update_user_password("admin", "new_admin_pass_456") is True
    assert db.authenticate_user("admin", "new_admin_pass_456") is not None

    # 6. Test Support Ticket & Activity Log
    ticket_id = db.create_support_ticket("test_user", "Bug", "Test Subject", "Test Message")
    assert ticket_id > 0

    db.log_activity("test_user", "Smoke Test", "Validation successful")
    activity = db.get_activity_log(limit=10)
    assert len(activity) > 0
    assert activity[0]["action"] == "Smoke Test"

    # 7. Test Backup Creation on re-initialization
    db._create_backup_if_exists()
