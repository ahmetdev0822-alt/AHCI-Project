"""
app/components/topbar.py
Blue & White themed top navigation bar.
Includes breadcrumbs, live date, density switcher, offline status badge, and role pill.
"""

import customtkinter as ctk
from datetime import date
from app.config import Colors, Fonts, Spacing, TOPBAR_HEIGHT, ROLE_ADMIN, ROLE_TEACHER, ROLE_PARENT


class TopBar(ctk.CTkFrame):
    """Horizontal top bar – shows page title, HCI controls, offline status, and user info."""

    def __init__(self, parent, state, navigate_fn=None, toast_fn=None, **kwargs):
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
        self._navigate_fn = navigate_fn
        self._toast_fn = toast_fn
        self._title_lbl    = None
        self._subtitle_lbl = None
        self._offline_chip = None
        self._build()

        # Blue accent bottom border
        ctk.CTkFrame(self, height=2, fg_color=Colors.BORDER,
                     corner_radius=0).place(relx=0, rely=1.0, anchor="sw", relwidth=1.0)

    def _build(self):
        # Left side – breadcrumb / title
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.pack(side="left", fill="y", padx=(Spacing.XL, 0))

        # Blue accent left stripe
        ctk.CTkFrame(left, width=3, height=28,
                     fg_color=Colors.PRIMARY,
                     corner_radius=2).pack(side="left", padx=(0, 10))

        title_col = ctk.CTkFrame(left, fg_color="transparent")
        title_col.pack(side="left", fill="y", pady=10)

        self._title_lbl = ctk.CTkLabel(
            title_col,
            text="Dashboard",
            font=(Fonts.FAMILY, Fonts.SIZE_XL, Fonts.WEIGHT_BOLD),
            text_color=Colors.TEXT_HEADING,
            anchor="w",
        )
        self._title_lbl.pack(anchor="w")

        self._subtitle_lbl = ctk.CTkLabel(
            title_col,
            text="",
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            text_color=Colors.TEXT_MUTED,
            anchor="w",
        )
        self._subtitle_lbl.pack(anchor="w")

        # Right side – Controls & user badge
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.pack(side="right", fill="y", padx=Spacing.LG)

        # 1. User role badge
        role_colors = {
            ROLE_ADMIN:   (Colors.PRIMARY,       Colors.PRIMARY_LIGHT),
            ROLE_TEACHER: (Colors.ACCENT,        "#E0F2F1"),
            ROLE_PARENT:  (Colors.PARENT_ACCENT, Colors.PARENT_BG),
        }
        rc, rbg = role_colors.get(self._state.current_role, (Colors.PRIMARY, Colors.PRIMARY_LIGHT))
        role_badge = ctk.CTkFrame(right, fg_color=rbg, corner_radius=8,
                                   border_width=1, border_color=rc)
        role_badge.pack(side="right", padx=(Spacing.SM, 0), pady=14)
        ctk.CTkLabel(
            role_badge, text=f"  {self._state.current_role}  ",
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            text_color=rc,
        ).pack(pady=3)

        # 2. Offline Mode Status Chip (Clickable to toggle demo offline state)
        self._offline_chip = ctk.CTkButton(
            right,
            text="☁  Online (Sync OK)" if not self._state.offline_mode else "☁⃠  Offline (Cached)",
            font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
            height=30,
            corner_radius=6,
            fg_color=Colors.SUCCESS_BG if not self._state.offline_mode else Colors.WARNING_BG,
            text_color=Colors.SUCCESS if not self._state.offline_mode else Colors.WARNING,
            border_width=1,
            border_color=Colors.SUCCESS if not self._state.offline_mode else Colors.WARNING,
            hover_color=Colors.BG_HOVER,
            command=self._toggle_offline_mode,
        )
        self._offline_chip.pack(side="right", padx=Spacing.SM, pady=14)

        # 3. Density Mode quick toggle
        self._density_btn = ctk.CTkButton(
            right,
            text="🔍  " + self._state.ui_density,
            font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
            height=30,
            width=110,
            corner_radius=6,
            fg_color=Colors.BG_INPUT,
            text_color=Colors.TEXT_SECONDARY,
            border_width=1,
            border_color=Colors.BORDER,
            hover_color=Colors.BG_HOVER,
            command=self._toggle_density,
        )
        self._density_btn.pack(side="right", padx=Spacing.SM, pady=14)

        # 4. Tour quick button
        if self._navigate_fn:
            ctk.CTkButton(
                right,
                text="✨  Tour",
                font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
                height=30,
                width=80,
                corner_radius=6,
                fg_color=Colors.PRIMARY_LIGHT,
                text_color=Colors.PRIMARY,
                hover_color=Colors.PRIMARY_DARK,
                command=lambda: self._navigate_fn("onboarding"),
            ).pack(side="right", padx=Spacing.SM, pady=14)

        # 5. Date chip
        today_str = date.today().strftime("%a, %d %b %Y")
        date_chip = ctk.CTkFrame(right, fg_color=Colors.BG_INPUT,
                                  corner_radius=6, border_width=1,
                                  border_color=Colors.BORDER)
        date_chip.pack(side="right", padx=Spacing.SM, pady=14)
        ctk.CTkLabel(
            date_chip, text=f"  📅 {today_str}  ",
            font=(Fonts.FAMILY, Fonts.SIZE_XS),
            text_color=Colors.TEXT_SECONDARY,
        ).pack(pady=4)

    def _toggle_offline_mode(self):
        self._state.offline_mode = not self._state.offline_mode
        is_off = self._state.offline_mode
        self._offline_chip.configure(
            text="☁⃠  Offline (Cached)" if is_off else "☁  Online (Sync OK)",
            fg_color=Colors.WARNING_BG if is_off else Colors.SUCCESS_BG,
            text_color=Colors.WARNING if is_off else Colors.SUCCESS,
            border_color=Colors.WARNING if is_off else Colors.SUCCESS,
        )
        if self._toast_fn:
            msg = "Offline Mode Enabled: Using encrypted local SQLite cache." if is_off else "Online Mode Restored: Synced changes with school network."
            self._toast_fn(msg, "warning" if is_off else "success")

    def _toggle_density(self):
        new_d = "Compact" if self._state.ui_density == "Comfortable" else "Comfortable"
        self._state.ui_density = new_d
        self._density_btn.configure(text="🔍  " + new_d)
        if self._toast_fn:
            self._toast_fn(f"UI Density set to {new_d} mode.", "info")

    def set_page(self, title: str, subtitle: str = ""):
        if self._title_lbl and self._title_lbl.winfo_exists():
            self._title_lbl.configure(text=title)
        if self._subtitle_lbl and self._subtitle_lbl.winfo_exists():
            self._subtitle_lbl.configure(text=subtitle)
