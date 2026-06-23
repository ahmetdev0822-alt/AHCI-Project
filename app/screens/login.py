"""
app/screens/login.py
Premium Blue & White Login Screen – EduTrack / Dar-e-Arqam School.
"""

import customtkinter as ctk
from app.config import (
    Colors, Fonts, Spacing, ROLES, DEMO_USERS,
    APP_NAME, SCHOOL_NAME, ROLE_ADMIN,
)


class LoginScreen(ctk.CTkFrame):
    """Full-screen login page shown before authentication."""

    def __init__(self, parent, on_login_success):
        super().__init__(parent, fg_color=Colors.SECONDARY, corner_radius=0)
        self._on_success = on_login_success
        self._error_var  = ctk.StringVar()
        self._role_var   = ctk.StringVar(value=ROLE_ADMIN)
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
        icon_bg = ctk.CTkFrame(brand_inner, width=100, height=100,
                                fg_color="#0D47A1", corner_radius=50)
        icon_bg.pack(pady=(0, 20))
        icon_bg.pack_propagate(False)
        ctk.CTkLabel(icon_bg, text="🎓",
                     font=(Fonts.FAMILY, 48),
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
        ).pack(pady=(4, 0))

        # Divider
        ctk.CTkFrame(
            brand_inner, height=2, width=220,
            fg_color="#42A5F5", corner_radius=1,
        ).pack(pady=22)

        ctk.CTkLabel(
            brand_inner, text=SCHOOL_NAME,
            font=(Fonts.FAMILY, Fonts.SIZE_LG, Fonts.WEIGHT_BOLD),
            text_color="#BBDEFB",
        ).pack()

        ctk.CTkLabel(
            brand_inner, text="Excellence  ·  Discipline  ·  Character",
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            text_color="#90CAF9",
        ).pack(pady=(6, 0))

        # Feature bullets
        bullets_frame = ctk.CTkFrame(brand_inner, fg_color="transparent")
        bullets_frame.pack(pady=(28, 0))
        for bullet in ["Role-Based Access Control", "Attendance & Marks Management",
                        "Timetable & Conflict Detection", "PDF & Excel Report Export"]:
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
            text="Powered by EduTrack v2.0  ·  © 2025 Dar-e-Arqam School",
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
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.74)

        # Card inner
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=40, pady=36)

        # Blue top accent
        ctk.CTkFrame(card, height=4, fg_color=Colors.PRIMARY,
                     corner_radius=0).place(relx=0, rely=0, anchor="nw", relwidth=1.0)

        # Welcome text
        ctk.CTkLabel(
            inner, text="Welcome Back 👋",
            font=(Fonts.FAMILY, Fonts.SIZE_4XL, Fonts.WEIGHT_BOLD),
            text_color=Colors.TEXT_HEADING,
            anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            inner, text="Sign in to access your EduTrack dashboard",
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            text_color=Colors.TEXT_MUTED,
            anchor="w",
        ).pack(anchor="w", pady=(4, 24))

        # Role selector
        self._make_label(inner, "Login As")
        role_frame = ctk.CTkFrame(inner, fg_color=Colors.BG_INPUT,
                                   corner_radius=8, border_width=1,
                                   border_color=Colors.BORDER)
        role_frame.pack(fill="x", pady=(4, 18))
        role_inner = ctk.CTkFrame(role_frame, fg_color="transparent")
        role_inner.pack(padx=12, pady=8)
        for role in ROLES:
            rb = ctk.CTkRadioButton(
                role_inner, text=role,
                variable=self._role_var, value=role,
                font=(Fonts.FAMILY, Fonts.SIZE_MD),
                text_color=Colors.TEXT_PRIMARY,
                fg_color=Colors.PRIMARY,
                hover_color=Colors.PRIMARY_DARK,
                command=self._prefill,
            )
            rb.pack(side="left", padx=(0, 20))

        # Username
        self._make_label(inner, "Username")
        self._username_entry = self._make_entry(inner, "Enter your username", False)

        # Password
        self._make_label(inner, "Password")
        self._password_entry = self._make_entry(inner, "Enter your password", True)
        self._password_entry.bind("<Return>", lambda e: self._attempt_login())

        # Error message
        self._error_lbl = ctk.CTkLabel(
            inner, textvariable=self._error_var,
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            text_color=Colors.DANGER,
            anchor="w",
        )
        self._error_lbl.pack(anchor="w", pady=(2, 0))

        # Login button
        ctk.CTkButton(
            inner, text="Sign In  →",
            height=46, corner_radius=10,
            font=(Fonts.FAMILY, Fonts.SIZE_LG, Fonts.WEIGHT_BOLD),
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_DARK,
            text_color=Colors.TEXT_WHITE,
            command=self._attempt_login,
        ).pack(fill="x", pady=(18, 0))

        # Demo credentials hint
        hint_box = ctk.CTkFrame(
            inner, fg_color=Colors.PRIMARY_LIGHT,
            corner_radius=8, border_width=1, border_color="#90CAF9",
        )
        hint_box.pack(fill="x", pady=(16, 0))
        ctk.CTkLabel(
            hint_box,
            text="💡  Demo Credentials\n"
                 "Admin: admin / admin123   ·   Teacher: teacher / teacher123   ·   Student: student / student123",
            font=(Fonts.FAMILY, Fonts.SIZE_XS),
            text_color=Colors.PRIMARY,
            wraplength=340,
            justify="center",
        ).pack(padx=12, pady=8)

        # Pre-fill based on current role selection
        self._prefill()

    def _make_label(self, parent, text: str):
        ctk.CTkLabel(
            parent, text=text,
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            text_color=Colors.TEXT_SECONDARY,
            anchor="w",
        ).pack(anchor="w", pady=(0, 4))

    def _make_entry(self, parent, placeholder: str, is_password: bool) -> ctk.CTkEntry:
        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            height=44,
            corner_radius=8,
            font=(Fonts.FAMILY, Fonts.SIZE_MD),
            fg_color=Colors.BG_INPUT,
            border_color=Colors.BORDER,
            text_color=Colors.TEXT_PRIMARY,
            placeholder_text_color=Colors.TEXT_MUTED,
            show="●" if is_password else "",
        )
        entry.pack(fill="x", pady=(0, 14))
        entry.bind("<FocusIn>",  lambda e: entry.configure(border_color=Colors.BORDER_FOCUS))
        entry.bind("<FocusOut>", lambda e: entry.configure(border_color=Colors.BORDER))
        return entry

    def _prefill(self):
        role = self._role_var.get()
        user = DEMO_USERS.get(role, {})
        self._username_entry.delete(0, "end")
        self._password_entry.delete(0, "end")
        self._username_entry.insert(0, user.get("username", ""))
        self._password_entry.insert(0, user.get("password", ""))
        self._error_var.set("")

    def _attempt_login(self):
        role     = self._role_var.get()
        username = self._username_entry.get().strip()
        password = self._password_entry.get().strip()

        if not username or not password:
            self._error_var.set("⚠  Please enter both username and password.")
            return

        expected = DEMO_USERS.get(role, {})
        if username == expected.get("username") and password == expected.get("password"):
            self._error_var.set("")
            self._on_success(role, expected)
        else:
            self._error_var.set("✕  Invalid username or password. Please try again.")
