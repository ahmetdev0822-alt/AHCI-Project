"""
app/components/sidebar.py
Blue & White themed sidebar with role-aware navigation,
active state, hover effects, and demo role switcher.
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
                              corner_radius=0, height=78)
        brand.pack(fill="x")
        brand.pack_propagate(False)

        # Blue accent left bar
        ctk.CTkFrame(brand, width=4, fg_color=Colors.PRIMARY,
                     corner_radius=0).pack(side="left", fill="y")

        ctk.CTkLabel(
            brand, text="🎓",
            font=(Fonts.FAMILY, 26),
            text_color="#90CAF9",
        ).pack(side="left", padx=(12, 8), pady=10)

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
            wraplength=162,
        ).pack(anchor="w")

        # ── Role Indicator ───────────────────────────────────────────────────
        role_bar = ctk.CTkFrame(self, fg_color="#0F2440", corner_radius=0, height=34)
        role_bar.pack(fill="x")
        role_bar.pack_propagate(False)

        role_icons  = {ROLE_ADMIN: "🛡", ROLE_TEACHER: "📚", ROLE_STUDENT: "🎒"}
        role_colors = {ROLE_ADMIN: "#64B5F6", ROLE_TEACHER: "#80CBC4", ROLE_STUDENT: "#FFE082"}
        ri = role_icons.get(self._state.current_role, "●")
        rc = role_colors.get(self._state.current_role, "#64B5F6")
        ctk.CTkLabel(
            role_bar,
            text=f"  {ri}  {self._state.current_role}",
            font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
            text_color=rc,
            anchor="w",
        ).pack(side="left", padx=10)

        # ── Navigation Label ─────────────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text="  NAVIGATION",
            font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
            text_color=Colors.SIDEBAR_ICON,
            anchor="w",
        ).pack(anchor="w", padx=12, pady=(18, 6))

        nav_items = NAV_ITEMS.get(self._state.current_role, [])
        for item in nav_items:
            self._add_nav_button(item["key"], item["label"], item["icon"])

        # ── Spacer ────────────────────────────────────────────────────────────
        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        # ── Thin divider ──────────────────────────────────────────────────────
        ctk.CTkFrame(self, height=1, fg_color="#243D5E",
                     corner_radius=0).pack(fill="x", padx=14)

        # ── User Info + Logout ────────────────────────────────────────────────
        user_area = ctk.CTkFrame(self, fg_color="transparent")
        user_area.pack(fill="x", padx=10, pady=10)

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
            text=(self._state.current_user or {}).get("designation", "")[:24],
            font=(Fonts.FAMILY, Fonts.SIZE_XS),
            text_color=Colors.SIDEBAR_TEXT, anchor="w",
        ).pack(anchor="w")

        ctk.CTkButton(
            user_area,
            text="⏻",
            width=30, height=30,
            corner_radius=8,
            font=(Fonts.FAMILY, 15),
            fg_color=Colors.SIDEBAR_HOVER_BG,
            text_color=Colors.DANGER,
            hover_color="#4A1E1E",
            command=self._logout_fn,
        ).pack(side="right")

        # ── Demo Role Switcher ────────────────────────────────────────────────
        demo_frame = ctk.CTkFrame(self, fg_color=Colors.SECONDARY_DARK,
                                  corner_radius=0, border_width=0)
        demo_frame.pack(fill="x")

        ctk.CTkLabel(
            demo_frame, text="DEMO — Switch Role",
            font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
            text_color=Colors.SIDEBAR_ICON,
        ).pack(pady=(8, 4))

        btn_row = ctk.CTkFrame(demo_frame, fg_color="transparent")
        btn_row.pack(pady=(0, 10))
        for role, short, color in [
            (ROLE_ADMIN,   "Admin",   "#64B5F6"),
            (ROLE_TEACHER, "Teacher", "#80CBC4"),
            (ROLE_STUDENT, "Student", "#FFE082"),
        ]:
            is_active = role == self._state.current_role
            ctk.CTkButton(
                btn_row,
                text=short,
                width=64, height=24,
                corner_radius=12,
                font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
                fg_color=Colors.PRIMARY if is_active else "#243D5E",
                text_color=Colors.TEXT_WHITE if is_active else color,
                hover_color=Colors.PRIMARY_DARK,
                command=lambda r=role: self._switch_role(r),
            ).pack(side="left", padx=3)

    def _add_nav_button(self, key: str, label: str, icon: str):
        is_active = self._state.active_screen == key

        btn = ctk.CTkButton(
            self,
            text=f"  {icon}   {label}",
            anchor="w",
            height=40,
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
        self.event_generate("<<RoleSwitch>>", when="tail")
