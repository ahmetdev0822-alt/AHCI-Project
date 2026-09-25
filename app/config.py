"""
app/config.py
EduTrack Design System – Blue & White Theme (Admin, Teacher, and Parent Focused)
WCAG 2.1 AA Accessible Colors, Density Modes, and Role-Based Navigation.
"""

import os

# ─── Application Meta ────────────────────────────────────────────────────────
APP_NAME        = "EduTrack"
SCHOOL_NAME     = "Dar-e-Arqam School"
APP_VERSION     = "2.2.0 (Standalone Desktop Edition)"
WINDOW_SIZE     = "1400x840"
WINDOW_MIN_SIZE = (1024, 680)

# ─── Asset Paths ─────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR    = os.path.join(BASE_DIR, "assets")
ICON_ICO_PATH = os.path.join(ASSETS_DIR, "icon.ico")
ICON_PNG_PATH = os.path.join(ASSETS_DIR, "icon.png")

# ─── Demo Mode & Security Flags ───────────────────────────────────────────────
# Toggle DEMO_MODE to False for production deployment without demo fixtures or quick-login
DEMO_MODE = True

if DEMO_MODE:
    from app.data.demo_fixtures import DEMO_USERS
else:
    DEMO_USERS = {}

# ─── Roles ───────────────────────────────────────────────────────────────────
ROLE_ADMIN   = "Administrator"
ROLE_TEACHER = "Teacher"
ROLE_PARENT  = "Parent"

ROLES = [ROLE_ADMIN, ROLE_TEACHER, ROLE_PARENT]

# ─── Color Palette ── Blue & White Theme (WCAG 2.1 AA Compliant) ────────────
class Colors:
    # Brand – Deep Blue
    PRIMARY       = "#1565C0"   # Deep Blue (4.8:1 contrast on white)
    PRIMARY_DARK  = "#0D47A1"   # Darker blue (hover)
    PRIMARY_LIGHT = "#E3F2FD"   # Light blue tint (backgrounds)
    SECONDARY     = "#1E3A5F"   # Dark Navy Blue (sidebar)
    SECONDARY_DARK= "#152B47"   # Darker navy (active items)
    ACCENT        = "#00897B"   # Teal – positive actions

    # Parent Role Brand Accents
    PARENT_ACCENT = "#7B1FA2"   # Purple accent for Parent role
    PARENT_BG     = "#F3E5F5"

    # Status / Semantic (4.5:1+ contrast on light backgrounds)
    SUCCESS       = "#1B5E20"   # Dark Forest Green (WCAG AA)
    SUCCESS_BG    = "#E8F5E9"
    WARNING       = "#BF360C"   # Deep Amber-Orange
    WARNING_BG    = "#FFF3E0"
    DANGER        = "#B71C1C"   # Deep Crimson
    DANGER_BG     = "#FFEBEE"
    INFO          = "#0D47A1"   # Navy Blue
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

    # Text (High contrast certified)
    TEXT_PRIMARY   = "#0F172A"  # 15.8:1 on white (Ultra-legible)
    TEXT_SECONDARY = "#334155"  # 9.5:1 on white
    TEXT_MUTED     = "#475569"  # 5.6:1 on white (passes WCAG AA 4.5:1)
    TEXT_WHITE     = "#FFFFFF"
    TEXT_HEADING   = "#0F2042"

    # Borders
    BORDER         = "#CBD5E1"
    BORDER_FOCUS   = "#1565C0"
    DIVIDER        = "#E2E8F0"

    # Sidebar (Ensured > 5.5:1 contrast on #1E3A5F)
    SIDEBAR_TEXT        = "#C9DCF2"  # 6.2:1 contrast against #1E3A5F
    SIDEBAR_ICON        = "#93B7DC"
    SIDEBAR_ACTIVE_BG   = "#1565C0"
    SIDEBAR_ACTIVE_TEXT = "#FFFFFF"
    SIDEBAR_HOVER_BG    = "#243D5E"

    # Attendance Colors
    PRESENT_COLOR = "#1B5E20"
    ABSENT_COLOR  = "#B71C1C"
    LATE_COLOR    = "#BF360C"
    LEAVE_COLOR   = "#0D47A1"


def _detect_ui_font() -> str:
    candidates = ["Segoe UI", "Inter", "Ubuntu", "Adwaita Sans", "DejaVu Sans", "Liberation Sans", "Cantarell", "Helvetica", "Arial"]
    try:
        import tkinter as _tk
        import tkinter.font as _tkfont
        _r = _tk.Tk()
        _r.withdraw()
        _avail = set(_tkfont.families(_r))
        _r.destroy()
        for c in candidates:
            if c in _avail:
                return c
    except Exception:
        pass
    return "DejaVu Sans"


def _detect_mono_font() -> str:
    candidates = ["Consolas", "Adwaita Mono", "DejaVu Sans Mono", "Liberation Mono", "Hack", "monospace"]
    try:
        import tkinter as _tk
        import tkinter.font as _tkfont
        _r = _tk.Tk()
        _r.withdraw()
        _avail = set(_tkfont.families(_r))
        _r.destroy()
        for c in candidates:
            if c in _avail:
                return c
    except Exception:
        pass
    return "monospace"


# ─── Font Sizes ──────────────────────────────────────────────────────────────
class Fonts:
    FAMILY      = _detect_ui_font()
    FAMILY_MONO = _detect_mono_font()

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

SIDEBAR_WIDTH     = 240
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
        {"key": "reports",     "label": "Reports & Analytics","icon": "📋"},
        {"key": "onboarding",  "label": "Interactive Tour",   "icon": "✨"},
        {"key": "settings",    "label": "System Settings",    "icon": "⚙"},
        {"key": "profile",     "label": "My Profile",         "icon": "👤"},
        {"key": "help",        "label": "Help & Support",     "icon": "❓"},
    ],
    ROLE_TEACHER: [
        {"key": "dashboard",   "label": "Dashboard",          "icon": "⊞"},
        {"key": "attendance",  "label": "Mark Attendance",    "icon": "✓"},
        {"key": "marks",       "label": "Enter Marks",        "icon": "📊"},
        {"key": "timetable",   "label": "My Timetable",       "icon": "📅"},
        {"key": "reports",     "label": "Class Reports",      "icon": "📋"},
        {"key": "onboarding",  "label": "Quick Tour",         "icon": "✨"},
        {"key": "profile",     "label": "My Profile",         "icon": "👤"},
        {"key": "help",        "label": "Help & Support",     "icon": "❓"},
    ],
    ROLE_PARENT: [
        {"key": "parent_dashboard", "label": "Child Overview",     "icon": "⊞"},
        {"key": "attendance",       "label": "Attendance Record",  "icon": "✓"},
        {"key": "marks",            "label": "Marks & Gradebook",  "icon": "📊"},
        {"key": "timetable",        "label": "Class Timetable",    "icon": "📅"},
        {"key": "onboarding",       "label": "Parent Guide",       "icon": "✨"},
        {"key": "profile",          "label": "Guardian Profile",   "icon": "👤"},
        {"key": "help",             "label": "School Helpdesk",    "icon": "❓"},
    ],
}