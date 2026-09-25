"""
app/screens/login.py
Premium Blue & White Login Screen – EduTrack / Dar-e-Arqam School.
Supports Administrator, Teacher, and Parent roles with optional 1-click quick-login demo mode.
"""

import customtkinter as ctk
from app.config import (
    Colors, Fonts, Spacing, ROLES, DEMO_USERS, DEMO_MODE,
    APP_NAME, SCHOOL_NAME, ROLE_ADMIN, ROLE_TEACHER, ROLE_PARENT,
)
from app.db.database import db


class LoginScreen(ctk.CTkFrame):
    """Full-screen login page shown before authentication."""

    def __init__(self, parent, on_login_success):
        super().__init__(parent, fg_color=Colors.SECONDARY, corner_radius=0)
        self._on_success = on_login_success
        self._error_var  = ctk.StringVar()
        self._role_var   = ctk.StringVar(value=ROLE_ADMIN)
        self._show_pass_var = ctk.BooleanVar(value=False)
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # ── Left panel – branding ─────────────────────────────────────────────
        left = ctk.CTkFrame(self, fg_color=Colors.PRIMARY, corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew")

        # Decorative gradient overlay bar at top
        top_bar = ctk.CTkFrame(left, fg_color=Colors.PRIMARY_DARK, corner_radius=0, height=6)
        top_bar.pack(fill="x")

        brand_inner = ctk.CTkFrame(left, fg_color="transparent")
        brand_inner.place(relx=0.5, rely=0.44, anchor="center")

        # Icon
        icon_bg = ctk.CTkFrame(brand_inner, width=90, height=90,
                                fg_color="#0D47A1", corner_radius=45)
        icon_bg.pack(pady=(0, 16))
        icon_bg.pack_propagate(False)
        ctk.CTkLabel(icon_bg, text="🎓",
                     font=(Fonts.FAMILY, 44),
                     text_color=Colors.TEXT_WHITE).pack(expand=True)

        ctk.CTkLabel(
            brand_inner, text=APP_NAME,
            font=(Fonts.FAMILY, Fonts.SIZE_5XL, Fonts.WEIGHT_BOLD),
            text_color=Colors.TEXT_WHITE,
        ).pack()

        ctk.CTkLabel(
            brand_inner, text="School Management System",
            font=(Fonts.FAMILY, Fonts.SIZE_XL),
            text_color="#90CAF9",
        ).pack(pady=(2, 0))

        # Divider
        ctk.CTkFrame(
            brand_inner, height=2, width=220,
            fg_color="#42A5F5", corner_radius=1,
        ).pack(pady=18)

        ctk.CTkLabel(
            brand_inner, text=SCHOOL_NAME,
            font=(Fonts.FAMILY, Fonts.SIZE_LG, Fonts.WEIGHT_BOLD),
            text_color="#BBDEFB",
        ).pack()

        ctk.CTkLabel(
            brand_inner, text="Excellence  ·  Discipline  ·  Character",
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            text_color="#90CAF9",
        ).pack(pady=(4, 0))

        # Feature bullets
        bullets_frame = ctk.CTkFrame(brand_inner, fg_color="transparent")
        bullets_frame.pack(pady=(20, 0))
        for bullet in [
            "Role-Based Portals (Admin, Teacher, Parent)",
            "Bulk Attendance with Instant Undo Action",
            "Interactive Weekly Timetable & Conflicts",
            "Local SQLite Persistence & Offline-First Mode",
        ]:
            row = ctk.CTkFrame(bullets_frame, fg_color="transparent")
            row.pack(anchor="w", pady=2)
            ctk.CTkLabel(row, text="✓",
                         font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                         text_color="#42A5F5").pack(side="left", padx=(0, 8))
            ctk.CTkLabel(row, text=bullet,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM),
                         text_color="#BBDEFB").pack(side="left")

        # Bottom tagline
        ctk.CTkLabel(
            left,
            text="Powered by EduTrack v2.2 (Standalone Edition)  ·  © 2026 Dar-e-Arqam School",
            font=(Fonts.FAMILY, Fonts.SIZE_XS),
            text_color="#64B5F6",
        ).place(relx=0.5, rely=0.96, anchor="center")

        # ── Right panel – form ────────────────────────────────────────────────
        right = ctk.CTkFrame(self, fg_color="#F4F7FA", corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew")

        card = ctk.CTkFrame(
            right,
            fg_color=Colors.BG_CARD,
            corner_radius=16,
            border_width=1,
            border_color=Colors.BORDER,
        )
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.76)

        # Card inner
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=36, pady=28)

        # Blue top accent
        ctk.CTkFrame(card, height=4, fg_color=Colors.PRIMARY,
                     corner_radius=0).place(relx=0, rely=0, anchor="nw", relwidth=1.0)

        # Welcome text
        ctk.CTkLabel(
            inner, text="Welcome Back 👋",
            font=(Fonts.FAMILY, Fonts.SIZE_3XL, Fonts.WEIGHT_BOLD),
            text_color=Colors.TEXT_HEADING,
            anchor="w",
        ).pack(anchor="w")

        subtitle_text = "Sign in or use 1-click demo access below" if DEMO_MODE else "Sign in with your institutional credentials"
        ctk.CTkLabel(
            inner, text=subtitle_text,
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            text_color=Colors.TEXT_MUTED,
            anchor="w",
        ).pack(anchor="w", pady=(2, 14))

        # Role selector
        self._make_label(inner, "Select Role")
        role_frame = ctk.CTkFrame(inner, fg_color=Colors.BG_INPUT,
                                   corner_radius=8, border_width=1,
                                   border_color=Colors.BORDER)
        role_frame.pack(fill="x", pady=(2, 12))
        role_inner = ctk.CTkFrame(role_frame, fg_color="transparent")
        role_inner.pack(padx=10, pady=6)
        for role in ROLES:
            rb = ctk.CTkRadioButton(
                role_inner, text=role,
                variable=self._role_var, value=role,
                font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                text_color=Colors.TEXT_PRIMARY,
                fg_color=Colors.PRIMARY,
                hover_color=Colors.PRIMARY_DARK,
                command=self._prefill,
            )
            rb.pack(side="left", padx=(0, 14))

        # Username
        self._make_label(inner, "Username")
        self._username_entry = self._make_entry(inner, "Enter your username", False)

        # Password
        self._make_label(inner, "Password")
        self._password_entry = self._make_entry(inner, "Enter your password", True)
        self._password_entry.bind("<Return>", lambda e: self._attempt_login())

        # Show Password Toggle
        self._show_pass_btn = ctk.CTkCheckBox(
            inner, text="Show Password",
            variable=self._show_pass_var,
            onvalue=True, offvalue=False,
            font=(Fonts.FAMILY, Fonts.SIZE_XS),
            text_color=Colors.TEXT_SECONDARY,
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_DARK,
            command=self._toggle_password_visibility,
        )
        self._show_pass_btn.pack(anchor="w", pady=(0, 6))

        # Error message
        self._error_lbl = ctk.CTkLabel(
            inner, textvariable=self._error_var,
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            text_color=Colors.DANGER,
            anchor="w",
        )
        self._error_lbl.pack(anchor="w", pady=(0, 4))

        # Login button
        ctk.CTkButton(
            inner, text="Sign In  →",
            height=42, corner_radius=8,
            font=(Fonts.FAMILY, Fonts.SIZE_MD, Fonts.WEIGHT_BOLD),
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_DARK,
            text_color=Colors.TEXT_WHITE,
            command=self._attempt_login,
        ).pack(fill="x", pady=(8, 12))

        # ── Quick 1-Click Demo Buttons (Only if DEMO_MODE enabled) ────────────
        if DEMO_MODE:
            demo_title = ctk.CTkLabel(
                inner, text="⚡  1-Click Instant Demo Portals:",
                font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
                text_color=Colors.TEXT_SECONDARY,
                anchor="w",
            )
            demo_title.pack(anchor="w", pady=(4, 6))

            btn_row = ctk.CTkFrame(inner, fg_color="transparent")
            btn_row.pack(fill="x")

            # Admin Demo
            ctk.CTkButton(
                btn_row, text="🛡 Admin Portal",
                height=32, corner_radius=6,
                font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
                fg_color=Colors.PRIMARY_LIGHT, text_color=Colors.PRIMARY,
                hover_color=Colors.PRIMARY,
                command=lambda: self._quick_login(ROLE_ADMIN),
            ).pack(side="left", fill="x", expand=True, padx=(0, 4))

            # Teacher Demo
            ctk.CTkButton(
                btn_row, text="📚 Teacher Portal",
                height=32, corner_radius=6,
                font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
                fg_color="#E0F2F1", text_color=Colors.ACCENT,
                hover_color=Colors.ACCENT,
                command=lambda: self._quick_login(ROLE_TEACHER),
            ).pack(side="left", fill="x", expand=True, padx=4)

            # Parent Demo
            ctk.CTkButton(
                btn_row, text="👨‍👩‍👧 Parent Portal",
                height=32, corner_radius=6,
                font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
                fg_color=Colors.PARENT_BG, text_color=Colors.PARENT_ACCENT,
                hover_color=Colors.PARENT_ACCENT,
                command=lambda: self._quick_login(ROLE_PARENT),
            ).pack(side="left", fill="x", expand=True, padx=(4, 0))

        # Pre-fill initial state
        self._prefill()

    def _make_label(self, parent, text: str):
        ctk.CTkLabel(
            parent, text=text,
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            text_color=Colors.TEXT_SECONDARY,
            anchor="w",
        ).pack(anchor="w", pady=(0, 2))

    def _make_entry(self, parent, placeholder: str, is_password: bool) -> ctk.CTkEntry:
        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            height=38,
            corner_radius=8,
            font=(Fonts.FAMILY, Fonts.SIZE_MD),
            fg_color=Colors.BG_INPUT,
            border_color=Colors.BORDER,
            text_color=Colors.TEXT_PRIMARY,
            placeholder_text_color=Colors.TEXT_MUTED,
            show="●" if is_password else "",
        )
        entry.pack(fill="x", pady=(0, 8))
        entry.bind("<FocusIn>",  lambda e: entry.configure(border_color=Colors.BORDER_FOCUS))
        entry.bind("<FocusOut>", lambda e: entry.configure(border_color=Colors.BORDER))
        return entry

    def _toggle_password_visibility(self):
        if self._show_pass_var.get():
            self._password_entry.configure(show="")
        else:
            self._password_entry.configure(show="●")

    def _prefill(self):
        role = self._role_var.get()
        self._username_entry.delete(0, "end")
        self._password_entry.delete(0, "end")
        if DEMO_MODE:
            user = DEMO_USERS.get(role, {})
            self._username_entry.insert(0, user.get("username", ""))
            self._password_entry.insert(0, user.get("password", ""))
        self._show_pass_var.set(False)
        self._password_entry.configure(show="●")
        self._error_var.set("")

    def _quick_login(self, role: str):
        if not DEMO_MODE:
            return
        self._role_var.set(role)
        self._prefill()
        self._attempt_login()

    def _attempt_login(self):
        role     = self._role_var.get()
        username = self._username_entry.get().strip()
        password = self._password_entry.get().strip()

        if not username or not password:
            self._error_var.set("⚠  Please enter both username and password.")
            return

        # 1. Try authenticating via SQLite database
        db_user = db.authenticate_user(username, password)
        if db_user:
            # If authenticated user has matching role or allows role override in demo
            user_role = db_user.get("role", role)
            self._error_var.set("")
            self._on_success(user_role, db_user)
            return

        # 2. Fallback to DEMO_USERS if DEMO_MODE is active
        if DEMO_MODE:
            expected = DEMO_USERS.get(role, {})
            if username == expected.get("username") and password == expected.get("password"):
                self._error_var.set("")
                self._on_success(role, expected)
                return

        self._error_var.set("✕  Invalid credentials for selected role.")