"""
app/data/demo_fixtures.py
DEMO-ONLY SEED DATA & MOCK FIXTURES – NOT FOR PRODUCTION DEPLOYMENT.

This fixture provides seed accounts and mock credentials for development, demonstrations,
and educational usability evaluations (AHCI Phase 1).
For production deployments, disable DEMO_MODE in app/config.py to enforce real database
authentication and prevent pre-filled credentials.
"""

ROLE_ADMIN   = "Administrator"
ROLE_TEACHER = "Teacher"
ROLE_PARENT  = "Parent"

DEMO_USERS = {
    ROLE_ADMIN: {
        "username":    "admin",
        "password":    "admin123",
        "full_name":   "Muhammad Arif Khan",
        "designation": "System Administrator",
        "student_id":  None,
        "class":       None,
        "email":       "admin@darearqam.edu.pk",
        "phone":       "0300-1122334",
    },
    ROLE_TEACHER: {
        "username":    "teacher",
        "password":    "teacher123",
        "full_name":   "Ustaz Bilal Ahmed",
        "designation": "Class Teacher – Class 6-A",
        "student_id":  None,
        "class":       "Class 6-A",
        "email":       "bilal@darearqam.edu.pk",
        "phone":       "0321-1234567",
    },
    ROLE_PARENT: {
        "username":    "parent",
        "password":    "parent123",
        "full_name":   "Rao Chaudhry",
        "designation": "Parent / Guardian",
        "student_id":  "S003",
        "class":       "Class 8-A",
        "child_name":  "Fatima Bibi Chaudhry",
        "email":       "rao.chaudhry@gmail.com",
        "phone":       "0312-3333333",
    },
}
