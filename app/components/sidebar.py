"""
app/components/sidebar.py
Role-aware sidebar navigation with active state, hover effects.
"""

import customtkinter as ctk
from app.config import (
    Colors, Fonts, Spacing, SIDEBAR_WIDTH, NAV_ITEMS,
    ROLE_ADMIN, ROLE_TEACHER, ROLE_STUDENT, APP_NAME, SCHOOL_NAME,
)


class Sidebar(ctk.CTkFrame):
    """
    Left sidebar.  Calls `navigate_fn(screen_key)` when a nav item is clicked.
    """

    def __init__(self, parent, state, navigate_fn, logout_fn, **kwargs):
        super().__init__(
            parent,
            fg_color=Colors.BG_SIDEBAR,
            corner_radius=0,
            width=SIDEBAR_WIDTH,
            **kwargs,
        )
        self.pack_propagate(False)
        self._state       = state
        self._navigate_fn = navigate_fn
        self._logout_fn   = logout_fn
        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        self._build()

    def _build(self):
        # ── Logo / Brand ────────────────────────────────────────────────────
        brand = ctk.CTkFrame(self, fg_color=Colors.SECONDARY_DARK,
                              corner_radius=0, height=80)
        brand.pack(fill="x")
        brand.pack_propagate(False)

        ctk.CTkLabel(
            brand, text="🏫",
            font=(Fonts.FAMILY, 28),
            text_color=Colors.TEXT_WHITE,
        ).pack(side="left", padx=(16, 8), pady=10)

        brand_text = ctk.CTkFrame(brand, fg_color="transparent")
        brand_text.pack(side="left", pady=10)
        ctk.CTkLabel(
            brand_text, text=APP_NAME,
            font=(Fonts.FAMILY, Fonts.SIZE_XL, Fonts.WEIGHT_BOLD),
            text_color=Colors.TEXT_WHITE,
            anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            brand_text, text=SCHOOL_NAME,
            font=(Fonts.FAMILY, Fonts.SIZE_XS),
            text_color=Colors.SIDEBAR_TEXT,
            anchor="w",
            wraplength=160,
        ).pack(anchor="w")

        # ── Role Indicator ───────────────────────────────────────────────────
        role_bar = ctk.CTkFrame(self, fg_color="#0F1C33", corner_radius=0, height=36)
        role_bar.pack(fill="x")
        role_bar.pack_propagate(False)

        role_colors = {
            ROLE_ADMIN:   Colors.ACCENT,
            ROLE_TEACHER: Colors.SUCCESS,
            ROLE_STUDENT: Colors.INFO,
        }
        rc = role_colors.get(self._state.current_role, Colors.ACCENT)
        ctk.CTkLabel(
            role_bar,
            text=f"● {self._state.current_role}",
            font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
            text_color=rc,
        ).pack(side="left", padx=16)

        # ── Navigation ───────────────────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text="NAVIGATION",
            font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
            text_color=Colors.SIDEBAR_ICON,
        ).pack(anchor="w", padx=16, pady=(20, 6))

        nav_items = NAV_ITEMS.get(self._state.current_role, [])
        for item in nav_items:
            self._add_nav_button(item["key"], item["label"], item["icon"])

        # ── Spacer + Divider ──────────────────────────────────────────────────
        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        ctk.CTkFrame(self, height=1, fg_color=Colors.SIDEBAR_HOVER_BG,
                      corner_radius=0).pack(fill="x", padx=16)

        # ── User Info + Logout ────────────────────────────────────────────────
        user_area = ctk.CTkFrame(self, fg_color="transparent")
        user_area.pack(fill="x", padx=12, pady=12)

        # Avatar circle
        avatar = ctk.CTkFrame(user_area, width=38, height=38,
                               fg_color=Colors.PRIMARY, corner_radius=19)
        avatar.pack(side="left")
        avatar.pack_propagate(False)
        initials = "".join(
            w[0].upper()
            for w in (self._state.current_user or {}).get("full_name", "U").split()[:2]
        )
        ctk.CTkLabel(
            avatar, text=initials,
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            text_color=Colors.TEXT_WHITE,
        ).pack(expand=True)

        user_info = ctk.CTkFrame(user_area, fg_color="transparent")
        user_info.pack(side="left", padx=(8, 0), fill="y")
        name = (self._state.current_user or {}).get("full_name", "User")
        short_name = name if len(name) <= 18 else name[:16] + "…"
        ctk.CTkLabel(
            user_info, text=short_name,
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            text_color=Colors.TEXT_WHITE, anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            user_info,
            text=(self._state.current_user or {}).get("designation", "")[:22],
            font=(Fonts.FAMILY, Fonts.SIZE_XS),
            text_color=Colors.SIDEBAR_TEXT, anchor="w",
        ).pack(anchor="w")

        ctk.CTkButton(
            user_area,
            text="⏻",
            width=32, height=32,
            corner_radius=8,
            font=(Fonts.FAMILY, 16),
            fg_color=Colors.SIDEBAR_HOVER_BG,
            text_color=Colors.DANGER,
            hover_color=Colors.DANGER,
            command=self._logout_fn,
        ).pack(side="right")

        # ── Demo role switcher (subtle) ───────────────────────────────────────
        demo_frame = ctk.CTkFrame(self, fg_color=Colors.SECONDARY_DARK, corner_radius=0)
        demo_frame.pack(fill="x")
        ctk.CTkLabel(
            demo_frame, text="DEMO — Switch Role:",
            font=(Fonts.FAMILY, Fonts.SIZE_XS),
            text_color=Colors.SIDEBAR_ICON,
        ).pack(pady=(6, 2))

        btn_row = ctk.CTkFrame(demo_frame, fg_color="transparent")
        btn_row.pack(pady=(0, 8))
        for role, short in [(ROLE_ADMIN, "Admin"),
                             (ROLE_TEACHER, "Teacher"),
                             (ROLE_STUDENT, "Student")]:
            is_active = role == self._state.current_role
            ctk.CTkButton(
                btn_row,
                text=short,
                width=60, height=22,
                corner_radius=4,
                font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
                fg_color=Colors.PRIMARY if is_active else Colors.SIDEBAR_HOVER_BG,
                text_color=Colors.TEXT_WHITE,
                hover_color=Colors.PRIMARY_DARK,
                command=lambda r=role: self._switch_role(r),
            ).pack(side="left", padx=2)

    def _add_nav_button(self, key: str, label: str, icon: str):
        is_active = self._state.active_screen == key

        btn = ctk.CTkButton(
            self,
            text=f"  {icon}   {label}",
            anchor="w",
            height=42,
            corner_radius=8,
            font=(Fonts.FAMILY, Fonts.SIZE_MD,
                  Fonts.WEIGHT_BOLD if is_active else Fonts.WEIGHT_NORMAL),
            fg_color=Colors.SIDEBAR_ACTIVE_BG if is_active else "transparent",
            text_color=Colors.SIDEBAR_ACTIVE_TEXT if is_active else Colors.SIDEBAR_TEXT,
            hover_color=Colors.SIDEBAR_HOVER_BG,
            command=lambda k=key: self._navigate_fn(k),
        )
        btn.pack(fill="x", padx=10, pady=2)
        self._nav_buttons[key] = btn

    def set_active(self, key: str):
        for k, btn in self._nav_buttons.items():
            if k == key:
                btn.configure(
                    fg_color=Colors.SIDEBAR_ACTIVE_BG,
                    text_color=Colors.SIDEBAR_ACTIVE_TEXT,
                    font=(Fonts.FAMILY, Fonts.SIZE_MD, Fonts.WEIGHT_BOLD),
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=Colors.SIDEBAR_TEXT,
                    font=(Fonts.FAMILY, Fonts.SIZE_MD, Fonts.WEIGHT_NORMAL),
                )

    def _switch_role(self, role: str):
        """Switch demo role and trigger full re-login."""
        from app.config import DEMO_USERS
        user = DEMO_USERS[role]
        self._state.login(role, user)
        # Notify main app
        self.event_generate("<<RoleSwitch>>", when="tail")
