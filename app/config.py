"""
app/config.py
EduTrack Design System – Colors, Fonts, Constants
"""

# ─── Application Meta ────────────────────────────────────────────────────────
APP_NAME        = "EduTrack"
SCHOOL_NAME     = "Dar-e-Arqam School"
APP_VERSION     = "1.0.0"
WINDOW_SIZE     = "1400x820"
WINDOW_MIN_SIZE = (1200, 700)

# ─── Roles ───────────────────────────────────────────────────────────────────
ROLE_ADMIN   = "Administrator"
ROLE_TEACHER = "Teacher"
ROLE_STUDENT = "Student"

ROLES = [ROLE_ADMIN, ROLE_TEACHER, ROLE_STUDENT]

# ─── Color Palette ───────────────────────────────────────────────────────────
class Colors:
    # Brand
    PRIMARY       = "#1B5E3B"   # Deep Forest Green
    PRIMARY_DARK  = "#144830"   # Darker green (hover)
    PRIMARY_LIGHT = "#E8F5EE"   # Light green tint (backgrounds)
    SECONDARY     = "#1A2744"   # Navy Blue (sidebar)
    SECONDARY_DARK= "#111B33"   # Darker navy (active items)
    ACCENT        = "#D4AF37"   # Gold accent

    # Status / Semantic
    SUCCESS       = "#27AE60"
    SUCCESS_BG    = "#E8F8F0"
    WARNING       = "#F39C12"
    WARNING_BG    = "#FEF9E7"
    DANGER        = "#E74C3C"
    DANGER_BG     = "#FDEDEC"
    INFO          = "#2980B9"
    INFO_BG       = "#EBF5FB"

    # Neutrals
    BG_MAIN       = "#F0F2F5"   # Page background
    BG_CARD       = "#FFFFFF"   # Card / panel
    BG_SIDEBAR    = "#1A2744"   # Sidebar background
    BG_TOPBAR     = "#FFFFFF"   # Top bar background
    BG_INPUT      = "#F8F9FA"   # Input field background
    BG_TABLE_ROW  = "#FFFFFF"
    BG_TABLE_ALT  = "#F7F9FC"
    BG_TABLE_HEAD = "#EEF1F8"
    BG_HOVER      = "#EBF3FF"

    # Text
    TEXT_PRIMARY   = "#1A2744"
    TEXT_SECONDARY = "#5A6A85"
    TEXT_MUTED     = "#8A9BBE"
    TEXT_WHITE     = "#FFFFFF"
    TEXT_HEADING   = "#0F1C35"

    # Borders
    BORDER         = "#E2E8F0"
    BORDER_FOCUS   = "#1B5E3B"
    DIVIDER        = "#ECF0F7"

    # Sidebar
    SIDEBAR_TEXT        = "#B8C5D6"
    SIDEBAR_ICON        = "#7A8FAD"
    SIDEBAR_ACTIVE_BG   = "#1B5E3B"
    SIDEBAR_ACTIVE_TEXT = "#FFFFFF"
    SIDEBAR_HOVER_BG    = "#243559"

    # Attendance Colors
    PRESENT_COLOR = "#27AE60"
    ABSENT_COLOR  = "#E74C3C"
    LATE_COLOR    = "#F39C12"
    LEAVE_COLOR   = "#2980B9"

# ─── Font Sizes ──────────────────────────────────────────────────────────────
class Fonts:
    FAMILY      = "Segoe UI"
    FAMILY_MONO = "Consolas"

    SIZE_XS   = 10
    SIZE_SM   = 11
    SIZE_BASE = 12
    SIZE_MD   = 13
    SIZE_LG   = 14
    SIZE_XL   = 16
    SIZE_2XL  = 18
    SIZE_3XL  = 22
    SIZE_4XL  = 28
    SIZE_5XL  = 36

    WEIGHT_NORMAL = "normal"
    WEIGHT_BOLD   = "bold"

# ─── Spacing & Sizing ────────────────────────────────────────────────────────
class Spacing:
    XS  = 4
    SM  = 8
    MD  = 12
    LG  = 16
    XL  = 20
    XXL = 28
    SECTION = 32

SIDEBAR_WIDTH     = 230
TOPBAR_HEIGHT     = 64
CARD_CORNER       = 10
BUTTON_CORNER     = 8
INPUT_CORNER      = 8
TABLE_ROW_HEIGHT  = 40

# ─── Navigation Items per Role ───────────────────────────────────────────────
NAV_ITEMS = {
    ROLE_ADMIN: [
        {"key": "dashboard",   "label": "Dashboard",   "icon": "⊞"},
        {"key": "students",    "label": "Students",    "icon": "👤"},
        {"key": "teachers",    "label": "Teachers",    "icon": "🎓"},
        {"key": "classes",     "label": "Classes",     "icon": "🏫"},
        {"key": "attendance",  "label": "Attendance",  "icon": "✓"},
        {"key": "marks",       "label": "Performance", "icon": "📊"},
        {"key": "timetable",   "label": "Timetable",   "icon": "📅"},
        {"key": "reports",     "label": "Reports",     "icon": "📋"},
    ],
    ROLE_TEACHER: [
        {"key": "dashboard",   "label": "Dashboard",   "icon": "⊞"},
        {"key": "attendance",  "label": "Attendance",  "icon": "✓"},
        {"key": "marks",       "label": "Performance", "icon": "📊"},
        {"key": "timetable",   "label": "Timetable",   "icon": "📅"},
        {"key": "reports",     "label": "Reports",     "icon": "📋"},
    ],
    ROLE_STUDENT: [
        {"key": "dashboard",   "label": "Dashboard",   "icon": "⊞"},
        {"key": "attendance",  "label": "My Attendance","icon": "✓"},
        {"key": "marks",       "label": "My Results",  "icon": "📊"},
        {"key": "timetable",   "label": "Timetable",   "icon": "📅"},
        {"key": "reports",     "label": "My Report",   "icon": "📋"},
    ],
}

# ─── Default Demo Credentials ─────────────────────────────────────────────────
DEMO_USERS = {
    ROLE_ADMIN: {
        "username": "admin",
        "password": "admin123",
        "full_name": "Muhammad Arif",
        "designation": "System Administrator",
    },
    ROLE_TEACHER: {
        "username": "teacher",
        "password": "teacher123",
        "full_name": "Ustaz Bilal Ahmed",
        "designation": "Senior Teacher – Mathematics",
    },
    ROLE_STUDENT: {
        "username": "student",
        "password": "student123",
        "full_name": "Ahmed Hassan Khan",
        "designation": "Class 8-A | Roll# 12",
    },
}
