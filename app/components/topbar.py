"""
app/components/topbar.py
Blue & White themed top navigation bar.
"""

import customtkinter as ctk
from datetime import date
from app.config import Colors, Fonts, Spacing, TOPBAR_HEIGHT, APP_NAME


class TopBar(ctk.CTkFrame):
    """Horizontal top bar – shows page title, user info, current date."""

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
        self._title_lbl    = None
        self._subtitle_lbl = None
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

        # Right side – date + user badge
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.pack(side="right", fill="y", padx=Spacing.XL)

        # Date chip
        today_str = date.today().strftime("%a, %d %b %Y")
        date_chip = ctk.CTkFrame(right, fg_color=Colors.PRIMARY_LIGHT,
                                  corner_radius=8, border_width=1,
                                  border_color=Colors.BORDER)
        date_chip.pack(side="right", padx=(Spacing.MD, 0), pady=12)
        ctk.CTkLabel(
            date_chip, text=f"  📅  {today_str}  ",
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            text_color=Colors.PRIMARY,
        ).pack(pady=2)

        # User role badge
        role_colors = {
            "Administrator": (Colors.PRIMARY,      Colors.PRIMARY_LIGHT),
            "Teacher":       (Colors.ACCENT,       "#E0F2F1"),
            "Student":       ("#E65100",           "#FFF3E0"),
        }
        rc, rbg = role_colors.get(self._state.current_role, (Colors.PRIMARY, Colors.PRIMARY_LIGHT))
        role_badge = ctk.CTkFrame(right, fg_color=rbg, corner_radius=8,
                                   border_width=1, border_color=rc)
        role_badge.pack(side="right", pady=12)
        ctk.CTkLabel(
            role_badge, text=f"  {self._state.current_role}  ",
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            text_color=rc,
        ).pack(pady=2)

    def set_page(self, title: str, subtitle: str = ""):
        if self._title_lbl and self._title_lbl.winfo_exists():
            self._title_lbl.configure(text=title)
        if self._subtitle_lbl and self._subtitle_lbl.winfo_exists():
            self._subtitle_lbl.configure(text=subtitle)
