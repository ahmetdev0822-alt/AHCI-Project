"""
app/components/sidebar.py
Blue & White themed sidebar with role-aware navigation,
active state, hover effects, and clear session logout.
"""

import customtkinter as ctk
from app.config import (
    Colors, Fonts, Spacing, SIDEBAR_WIDTH, NAV_ITEMS,
    ROLE_ADMIN, ROLE_TEACHER, APP_NAME, SCHOOL_NAME,
)


class Sidebar(ctk.CTkFrame):
    """
    Left sidebar. Calls `navigate_fn(screen_key)` when a nav item is clicked.
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

        role_icons  = {ROLE_ADMIN: "🛡", ROLE_TEACHER: "📚"}
        role_colors = {ROLE_ADMIN: "#64B5F6", ROLE_TEACHER: "#80CBC4"}
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

        # ── Scrollable Navigation Items Area ─────────────────────────────────
        nav_container = ctk.CTkFrame(self, fg_color="transparent")
        nav_container.pack(fill="both", expand=True)

        nav_items = NAV_ITEMS.get(self._state.current_role, [])
        for item in nav_items:
            self._add_nav_button(nav_container, item["key"], item["label"], item["icon"])

        # ── Fixed Bottom Container ──────────────────
        bottom_anchor = ctk.CTkFrame(self, fg_color="transparent")
        bottom_anchor.pack(side="bottom", fill="x", pady=(0, 15))

        # Divider
        ctk.CTkFrame(bottom_anchor, height=1, fg_color="#243D5E",
                     corner_radius=0).pack(fill="x", padx=14, pady=(0, 12))

        # User Profile Block Row
        user_area = ctk.CTkFrame(bottom_anchor, fg_color="transparent")
        user_area.pack(fill="x", padx=14, pady=(0, 12))
        user_area.columnconfigure(0, weight=0) # Avatar
        user_area.columnconfigure(1, weight=1) # Information Labels

        # Avatar circle
        avatar = ctk.CTkFrame(user_area, width=38, height=38,
                               fg_color=Colors.PRIMARY, corner_radius=19)
        avatar.grid(row=0, column=0, sticky="w")
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

        # Profile Labels
        user_info = ctk.CTkFrame(user_area, fg_color="transparent")
        user_info.grid(row=0, column=1, padx=10, sticky="ew")
        name = (self._state.current_user or {}).get("full_name", "User")
        short_name = name if len(name) <= 16 else name[:14] + "…"
        ctk.CTkLabel(
            user_info, text=short_name,
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            text_color=Colors.TEXT_WHITE, anchor="w",
        ).pack(anchor="w")
        
        desig = (self._state.current_user or {}).get("designation", "")
        short_desig = desig if len(desig) <= 22 else desig[:20] + "…"
        ctk.CTkLabel(
            user_info,
            text=short_desig,
            font=(Fonts.FAMILY, Fonts.SIZE_XS),
            text_color=Colors.SIDEBAR_TEXT, anchor="w",
        ).pack(anchor="w")

        # ── Fully Prominent White Logout Button ──────────────────────────────
        logout_btn = ctk.CTkButton(
            bottom_anchor,
            text="🚪  Logout Session",
            height=36,
            corner_radius=8,
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            fg_color="#D32F2F",
            text_color=Colors.TEXT_WHITE,
            hover_color="#B71C1C",
            command=self._logout_fn,
        )
        logout_btn.pack(fill="x", padx=14)

    def _add_nav_button(self, container, key: str, label: str, icon: str):
        is_active = self._state.active_screen == key

        btn = ctk.CTkButton(
            container,
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