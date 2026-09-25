"""
app/db/__init__.py
Database and persistence package for EduTrack.
"""
from app.db.paths import (
    APP_DATA_DIR, LOG_DIR, BACKUP_DIR, DB_PATH, LOG_PATH, logger,
    get_app_data_dir, get_app_log_dir, get_app_backup_dir, get_db_path, get_log_path
)
from app.db.database import DatabaseManager, db

__all__ = [
    "DatabaseManager",
    "db",
    "APP_DATA_DIR",
    "LOG_DIR",
    "BACKUP_DIR",
    "DB_PATH",
    "LOG_PATH",
    "logger",
    "get_app_data_dir",
    "get_app_log_dir",
    "get_app_backup_dir",
    "get_db_path",
    "get_log_path",
]
