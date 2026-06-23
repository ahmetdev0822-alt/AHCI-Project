"""
app/config.py
EduTrack Design System – Blue & White Theme (Admin & Teacher Focused)
"""

# ─── Application Meta ────────────────────────────────────────────────────────
APP_NAME        = "EduTrack"
SCHOOL_NAME     = "Dar-e-Arqam School"
APP_VERSION     = "2.0.0"
WINDOW_SIZE     = "1400x820"
WINDOW_MIN_SIZE = (1200, 700)

# ─── Roles ───────────────────────────────────────────────────────────────────
ROLE_ADMIN   = "Administrator"
ROLE_TEACHER = "Teacher"

ROLES = [ROLE_ADMIN, ROLE_TEACHER]

# ─── Color Palette ── Blue & White Theme ─────────────────────────────────────
class Colors:
    # Brand – Deep Blue
    PRIMARY       = "#1565C0"   # Deep Blue
    PRIMARY_DARK  = "#0D47A1"   # Darker blue (hover)
    PRIMARY_LIGHT = "#E3F2FD"   # Light blue tint (backgrounds)
    SECONDARY     = "#1E3A5F"   # Dark Navy Blue (sidebar)
    SECONDARY_DARK= "#152B47"   # Darker navy (active items)
    ACCENT        = "#00897B"   # Teal – positive actions

    # Status / Semantic
    SUCCESS       = "#2E7D32"
    SUCCESS_BG    = "#E8F5E9"
    WARNING       = "#E65100"
    WARNING_BG    = "#FFF3E0"
    DANGER        = "#C62828"
    DANGER_BG     = "#FFEBEE"
    INFO          = "#1565C0"
    INFO_BG       = "#E3F2FD"

    # Neutrals
    BG_MAIN       = "#F4F7FA"   # Page background – very light blue-gray
    BG_CARD       = "#FFFFFF"   # Card / panel
    BG_SIDEBAR    = "#1E3A5F"   # Sidebar background
    BG_TOPBAR     = "#FFFFFF"   # Top bar background
    BG_INPUT      = "#F8FAFC"   # Input field background
    BG_TABLE_ROW  = "#FFFFFF"
    BG_TABLE_ALT  = "#F7F9FC"
    BG_TABLE_HEAD = "#E8EEF7"
    BG_HOVER      = "#E3F2FD"

    # Text
    TEXT_PRIMARY   = "#1A2744"
    TEXT_SECONDARY = "#4A5568"
    TEXT_MUTED     = "#718096"
    TEXT_WHITE     = "#FFFFFF"
    TEXT_HEADING   = "#0F2042"

    # Borders
    BORDER         = "#E2E8F0"
    BORDER_FOCUS   = "#1565C0"
    DIVIDER        = "#EDF2F7"

    # Sidebar
    SIDEBAR_TEXT        = "#A8BDD6"
    SIDEBAR_ICON        = "#6B8CAE"
    SIDEBAR_ACTIVE_BG   = "#1565C0"
    SIDEBAR_ACTIVE_TEXT = "#FFFFFF"
    SIDEBAR_HOVER_BG    = "#243D5E"

    # Attendance Colors
    PRESENT_COLOR = "#2E7D32"
    ABSENT_COLOR  = "#C62828"
    LATE_COLOR    = "#E65100"
    LEAVE_COLOR   = "#1565C0"


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

SIDEBAR_WIDTH     = 235
TOPBAR_HEIGHT     = 64
CARD_CORNER       = 10
BUTTON_CORNER     = 8
INPUT_CORNER      = 8
TABLE_ROW_HEIGHT  = 40

# ─── Navigation Items per Role ───────────────────────────────────────────────
NAV_ITEMS = {
    ROLE_ADMIN: [
        {"key": "dashboard",   "label": "Dashboard",          "icon": "⊞"},
        {"key": "students",    "label": "Students",           "icon": "👤"},
        {"key": "teachers",    "label": "Teachers",           "icon": "🎓"},
        {"key": "classes",     "label": "Classes",            "icon": "🏫"},
        {"key": "attendance",  "label": "Attendance",         "icon": "✓"},
        {"key": "marks",       "label": "Marks & Performance","icon": "📊"},
        {"key": "timetable",   "label": "Timetable",          "icon": "📅"},
        {"key": "reports",     "label": "Reports",            "icon": "📋"},
    ],
    ROLE_TEACHER: [
        {"key": "dashboard",   "label": "Dashboard",          "icon": "⊞"},
        {"key": "attendance",  "label": "Mark Attendance",    "icon": "✓"},
        {"key": "marks",       "label": "Enter Marks",        "icon": "📊"},
        {"key": "timetable",   "label": "Timetable",          "icon": "📅"},
        {"key": "reports",     "label": "Class Reports",      "icon": "📋"},
    ],
}

# ─── Default Demo Credentials ─────────────────────────────────────────────────
DEMO_USERS = {
    ROLE_ADMIN: {
        "username":    "admin",
        "password":    "admin123",
        "full_name":   "Muhammad Arif Khan",
        "designation": "System Administrator",
        "student_id":  None,
        "class":       None,
    },
    ROLE_TEACHER: {
        "username":    "teacher",
        "password":    "teacher123",
        "full_name":   "Ustaz Bilal Ahmed",
        "designation": "Class Teacher – Class 6-A",
        "student_id":  None,
        "class":       "Class 6-A",
    },
}