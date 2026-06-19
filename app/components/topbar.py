"""
app/components/topbar.py
Top bar: screen title, breadcrumb, live clock, and quick search.
"""

import customtkinter as ctk
from datetime import datetime
from app.config import Colors, Fonts, Spacing, TOPBAR_HEIGHT


class TopBar(ctk.CTkFrame):
    """Horizontal top bar shown above every screen content area."""

    def __init__(self, parent, state, **kwargs):
        super().__init__(
            parent,
            fg_color=Colors.BG_TOPBAR,
            corner_radius=0,
            height=TOPBAR_HEIGHT,
            border_width=0,
            **kwargs,
        )
        self.pack_propagate(False)
        self._state = state
        self._title_var = ctk.StringVar(value="Dashboard")
        self._sub_var   = ctk.StringVar(value="Welcome back")

        self._build()
        self._tick()

    def _build(self):
        # ── Left: Page title + breadcrumb ────────────────────────────────────
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.pack(side="left", fill="y", padx=(Spacing.XL, 0))

        self._title_lbl = ctk.CTkLabel(
            left,
            textvariable=self._title_var,
            font=(Fonts.FAMILY, Fonts.SIZE_XL, Fonts.WEIGHT_BOLD),
            text_color=Colors.TEXT_HEADING,
            anchor="w",
        )
        self._title_lbl.pack(anchor="w", pady=(10, 0))

        self._sub_lbl = ctk.CTkLabel(
            left,
            textvariable=self._sub_var,
            font=(Fonts.FAMILY, Fonts.SIZE_XS),
            text_color=Colors.TEXT_MUTED,
            anchor="w",
        )
        self._sub_lbl.pack(anchor="w")

        # ── Right: Clock + Divider ────────────────────────────────────────────
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.pack(side="right", fill="y", padx=Spacing.XL)

        # School year badge
        ctk.CTkLabel(
            right,
            text="Session 2025–26",
            font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
            text_color=Colors.PRIMARY,
            fg_color=Colors.PRIMARY_LIGHT,
            corner_radius=6,
            padx=8, pady=3,
        ).pack(side="right", pady=18, padx=(8, 0))

        # Date / time
        self._clock_lbl = ctk.CTkLabel(
            right,
            text="",
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            text_color=Colors.TEXT_SECONDARY,
        )
        self._clock_lbl.pack(side="right", pady=18, padx=(0, Spacing.MD))

        # Bottom divider
        ctk.CTkFrame(
            self, height=1, fg_color=Colors.DIVIDER, corner_radius=0,
        ).pack(side="bottom", fill="x")

    def set_page(self, title: str, subtitle: str = ""):
        self._title_var.set(title)
        screen_map = {
            "dashboard":  "Home",
            "students":   "Home  /  Students",
            "teachers":   "Home  /  Teachers",
            "classes":    "Home  /  Classes",
            "attendance": "Home  /  Attendance",
            "marks":      "Home  /  Performance",
            "timetable":  "Home  /  Timetable",
            "reports":    "Home  /  Reports",
        }
        crumb = screen_map.get(title.lower(), f"Home  /  {title}")
        self._sub_var.set(subtitle if subtitle else crumb)

    def _tick(self):
        now = datetime.now()
        self._clock_lbl.configure(
            text=now.strftime("%A, %d %b %Y   %I:%M %p")
        )
        self.after(30_000, self._tick)   # Refresh every 30 s
