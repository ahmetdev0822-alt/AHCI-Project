"""
main.py
EduTrack – Dar-e-Arqam School Management System
Entry point. Manages the main window, navigation, and screen lifecycle.
"""

import os
import sys

# ── Ensure native Tkinter/Tcl libraries and antialiased fonts are available on Linux ──
_tk_lib_dir = os.path.expanduser("~/.local/opt/arch_tk/usr/lib")
if os.path.exists(_tk_lib_dir):
    os.environ.setdefault("TCL_LIBRARY", os.path.expanduser("~/.local/opt/arch_tk/usr/lib/tcl8.6"))
    os.environ.setdefault("TK_LIBRARY", os.path.expanduser("~/.local/opt/arch_tk/usr/lib/tk8.6"))
    _current_ld = os.environ.get("LD_LIBRARY_PATH", "")
    if _tk_lib_dir not in _current_ld.split(":"):
        os.environ["LD_LIBRARY_PATH"] = f"{_tk_lib_dir}:{_current_ld}".strip(":")
        os.execv(sys.executable, [sys.executable] + sys.argv)

import customtkinter as ctk
from app.config import (
    APP_NAME, SCHOOL_NAME, WINDOW_SIZE, WINDOW_MIN_SIZE,
    Colors, Fonts, NAV_ITEMS, DEMO_USERS,
    ROLE_ADMIN,
)
from app.state import AppState
from app.components.sidebar import Sidebar
from app.components.topbar  import TopBar
from app.components.toast   import ToastManager

# ── Screen imports ────────────────────────────────────────────────────────────
from app.screens.login      import LoginScreen
from app.screens.dashboard  import DashboardScreen
from app.screens.students   import StudentsScreen
from app.screens.teachers   import TeachersScreen
from app.screens.classes    import ClassesScreen
from app.screens.attendance import AttendanceScreen
from app.screens.marks      import MarksScreen
from app.screens.timetable  import TimetableScreen
from app.screens.reports    import ReportsScreen

SCREEN_MAP = {
    "dashboard":  DashboardScreen,
    "students":   StudentsScreen,
    "teachers":   TeachersScreen,
    "classes":    ClassesScreen,
    "attendance": AttendanceScreen,
    "marks":      MarksScreen,
    "timetable":  TimetableScreen,
    "reports":    ReportsScreen,
}

SCREEN_TITLES = {
    "dashboard":  ("Dashboard",          ""),
    "students":   ("Student Management", "Admin  /  Students"),
    "teachers":   ("Teacher Management", "Admin  /  Teachers"),
    "classes":    ("Classes & Sections", "Admin  /  Classes"),
    "attendance": ("Attendance Marking", "Mark today's attendance"),
    "marks":      ("Performance & Marks","Enter and view exam scores"),
    "timetable":  ("Timetable",          "Weekly class schedule"),
    "reports":    ("Reports",            "Generate and export reports"),
}


class EduTrackApp(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self._state        = AppState()
        self._sidebar      = None
        self._topbar       = None
        self._content      = None
        self._main_layout  = None
        self._current_screen_widget = None

        # ── Window setup ──────────────────────────────────────────────────────
        self.title(f"{APP_NAME} – {SCHOOL_NAME}")
        self.geometry(WINDOW_SIZE)
        self.minsize(*WINDOW_MIN_SIZE)
        self.configure(fg_color=Colors.BG_MAIN)

        # Set appearance
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        # Custom window icon via title (no .ico needed for demo)
        # self.iconbitmap("assets/icon.ico")  # Uncomment if icon available

        # ── Show login ────────────────────────────────────────────────────────
        self._show_login()

        # ── Role switch event (from sidebar demo switcher) ────────────────────
        self.bind("<<RoleSwitch>>", self._on_role_switch)

    # ── Login ─────────────────────────────────────────────────────────────────

    def _show_login(self):
        """Display the login screen (clears everything else)."""
        self._destroy_main_layout()
        self._login_screen = LoginScreen(self, self._on_login_success)
        self._login_screen.pack(fill="both", expand=True)

    def _on_login_success(self, role: str, user_dict: dict):
        """Called by LoginScreen after successful auth."""
        self._state.login(role, user_dict)
        if hasattr(self, "_login_screen") and self._login_screen.winfo_exists():
            self._login_screen.destroy()
        self._build_main_layout()
        self.navigate("dashboard")

    # ── Main Layout ───────────────────────────────────────────────────────────

    def _build_main_layout(self):
        """Build sidebar + topbar + content area."""
        self._main_layout = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self._main_layout.pack(fill="both", expand=True)
        self._main_layout.rowconfigure(0, weight=1)
        self._main_layout.columnconfigure(1, weight=1)

        # Sidebar
        self._sidebar = Sidebar(
            self._main_layout,
            state=self._state,
            navigate_fn=self.navigate,
            logout_fn=self._logout,
        )
        self._sidebar.grid(row=0, column=0, sticky="nsew")

        # Right area (topbar + content)
        right = ctk.CTkFrame(self._main_layout, fg_color=Colors.BG_MAIN, corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        self._topbar = TopBar(right, state=self._state)
        self._topbar.grid(row=0, column=0, sticky="ew")

        self._content = ctk.CTkFrame(right, fg_color=Colors.BG_MAIN, corner_radius=0)
        self._content.grid(row=1, column=0, sticky="nsew")

    def _destroy_main_layout(self):
        if self._main_layout and self._main_layout.winfo_exists():
            self._main_layout.destroy()
            self._main_layout  = None
            self._sidebar      = None
            self._topbar       = None
            self._content      = None
            self._current_screen_widget = None

    # ── Navigation ────────────────────────────────────────────────────────────

    def navigate(self, screen_key: str):
        """Switch the content area to the given screen."""
        # Validate access
        allowed = [item["key"] for item in NAV_ITEMS.get(self._state.current_role, [])]
        if screen_key not in allowed:
            self.toast(f"Access denied: {screen_key} is not available for your role.", "error")
            return

        # Destroy old screen
        if self._current_screen_widget and self._current_screen_widget.winfo_exists():
            self._current_screen_widget.destroy()

        # Update state
        self._state.previous_screen = self._state.active_screen
        self._state.active_screen   = screen_key

        # Update sidebar active state
        if self._sidebar and self._sidebar.winfo_exists():
            self._sidebar.set_active(screen_key)

        # Update topbar title
        if self._topbar and self._topbar.winfo_exists():
            title, subtitle = SCREEN_TITLES.get(screen_key, (screen_key.title(), ""))
            self._topbar.set_page(title, subtitle)

        # Instantiate new screen
        ScreenClass = SCREEN_MAP.get(screen_key)
        if ScreenClass:
            screen = ScreenClass(
                self._content,
                state=self._state,
                navigate_fn=self.navigate,
                toast_fn=self.toast,
            )
            screen.pack(fill="both", expand=True)
            self._current_screen_widget = screen
        else:
            self._show_not_found(screen_key)

    def _show_not_found(self, key: str):
        f = ctk.CTkFrame(self._content, fg_color=Colors.BG_MAIN)
        f.pack(fill="both", expand=True)
        ctk.CTkLabel(f, text=f"Screen '{key}' not found.",
                     font=(Fonts.FAMILY, Fonts.SIZE_2XL),
                     text_color=Colors.TEXT_MUTED).place(relx=0.5, rely=0.5, anchor="center")

    # ── Toast ─────────────────────────────────────────────────────────────────

    def toast(self, message: str, kind: str = "success"):
        ToastManager.show(self, message, kind)

    # ── Logout ────────────────────────────────────────────────────────────────

    def _logout(self):
        self._state.logout()
        self._destroy_main_layout()
        self._show_login()

    # ── Role Switch (demo) ────────────────────────────────────────────────────

    def _on_role_switch(self, event=None):
        """Re-build the entire layout for the new role."""
        self._destroy_main_layout()
        self._build_main_layout()
        self.navigate("dashboard")
        self.toast(
            f"Switched to {self._state.current_role} view.",
            "info"
        )


# ── Entry Point ───────────────────────────────────────────────────────────────

def main():
    app = EduTrackApp()
    app.mainloop()


if __name__ == "__main__":
    main()
