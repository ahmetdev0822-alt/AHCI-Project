"""
app/db/__init__.py
Database package for EduTrack.
"""
from app.db.database import DatabaseManager, db

__all__ = ["DatabaseManager", "db"]
