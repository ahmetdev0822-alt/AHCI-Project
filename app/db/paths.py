"""
app/db/paths.py
System-wide cross-platform path resolution and logging configuration for EduTrack.
Ensures SQLite persistence and logs reside in user-writable application directories
(e.g., via platformdirs or OS standard fallbacks), complying with standalone packaging standards.
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

try:
    import platformdirs
    _HAS_PLATFORMDIRS = True
except ImportError:
    _HAS_PLATFORMDIRS = False


APP_NAME = "EduTrack"
APP_AUTHOR = "Dar-e-Arqam"


def get_app_data_dir() -> str:
    """Return user-writable application data directory."""
    if _HAS_PLATFORMDIRS:
        data_dir = platformdirs.user_data_dir(appname=APP_NAME, appauthor=APP_AUTHOR)
    else:
        # Fallback based on OS
        if sys.platform.startswith("win"):
            base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or os.path.expanduser("~")
            data_dir = os.path.join(base, APP_AUTHOR, APP_NAME)
        elif sys.platform == "darwin":
            data_dir = os.path.join(os.path.expanduser("~/Library/Application Support"), APP_NAME)
        else:
            base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
            data_dir = os.path.join(base, APP_NAME)

    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def get_app_log_dir() -> str:
    """Return user-writable application log directory."""
    if _HAS_PLATFORMDIRS:
        log_dir = platformdirs.user_log_dir(appname=APP_NAME, appauthor=APP_AUTHOR)
    else:
        log_dir = os.path.join(get_app_data_dir(), "logs")

    os.makedirs(log_dir, exist_ok=True)
    return log_dir


def get_app_backup_dir() -> str:
    """Return directory for timestamped SQLite database backups."""
    backup_dir = os.path.join(get_app_data_dir(), "backups")
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir


def get_db_path() -> str:
    """Return absolute path to the main EduTrack SQLite database file."""
    # Allow overriding via environment variable for headless tests / CI
    env_path = os.environ.get("EDUTRACK_DB_PATH")
    if env_path:
        os.makedirs(os.path.dirname(os.path.abspath(env_path)), exist_ok=True)
        return os.path.abspath(env_path)
    return os.path.join(get_app_data_dir(), "edutrack.db")


def get_log_path() -> str:
    """Return absolute path to the rotating application log file."""
    return os.path.join(get_app_log_dir(), "edutrack.log")


# Pre-resolved constants
APP_DATA_DIR = get_app_data_dir()
LOG_DIR      = get_app_log_dir()
BACKUP_DIR   = get_app_backup_dir()
DB_PATH      = get_db_path()
LOG_PATH     = get_log_path()


# ── Configure Logging ───────────────────────────────────────────────────────────
logger = logging.getLogger("edutrack")
logger.setLevel(logging.DEBUG)

# Avoid adding duplicate handlers if reloaded
if not logger.handlers:
    # 1. Rotating File Handler (5 MB per file, 3 backups)
    try:
        file_handler = RotatingFileHandler(
            LOG_PATH,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(name)s:%(filename)s:%(lineno)d] - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        sys.stderr.write(f"Failed to initialize rotating file logger: {e}\n")

    # 2. Console Handler (for dev/debugging when console exists)
    try:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter("[%(levelname)s] %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    except Exception:
        pass
