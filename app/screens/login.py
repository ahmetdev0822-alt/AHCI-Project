"""
app/screens/login.py
Professional login screen for EduTrack – Dar-e-Arqam School.
"""

import customtkinter as ctk
from app.config import (
    Colors, Fonts, Spacing, ROLES, DEMO_USERS,
    APP_NAME, SCHOOL_NAME, CARD_CORNER, ROLE_ADMIN,
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

        brand_inner = ctk.CTkFrame(left, fg_color="transparent")
        brand_inner.place(relx=0.5, rely=0.45, anchor="center")

        ctk.CTkLabel(
            brand_inner, text="🏫",
            font=(Fonts.FAMILY, 72),
            text_color=Colors.TEXT_WHITE,
        ).pack(pady=(0, 16))

        ctk.CTkLabel(
            brand_inner, text=APP_NAME,
            font=(Fonts.FAMILY, Fonts.SIZE_5XL, Fonts.WEIGHT_BOLD),
            text_color=Colors.TEXT_WHITE,
        ).pack()

        ctk.CTkLabel(
            brand_inner, text="School Management System",
            font=(Fonts.FAMILY, Fonts.SIZE_XL),
            text_color="#A8D5BC",
        ).pack(pady=(4, 0))

        ctk.CTkFrame(
            brand_inner, height=2, width=200,
            fg_color=Colors.ACCENT, corner_radius=1,
        ).pack(pady=24)

        ctk.CTkLabel(
            brand_inner, text=SCHOOL_NAME,
            font=(Fonts.FAMILY, Fonts.SIZE_LG, Fonts.WEIGHT_BOLD),
            text_color=Colors.ACCENT,
        ).pack()

        ctk.CTkLabel(
            brand_inner, text="Excellence · Discipline · Character",
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            text_color="#A8D5BC",
        ).pack(pady=(6, 0))

        # Bottom tagline
        ctk.CTkLabel(
            left,
            text="Powered by EduTrack v1.0  |  © 2025 Dar-e-Arqam",
            font=(Fonts.FAMILY, Fonts.SIZE_XS),
            text_color="#68A882",
        ).place(relx=0.5, rely=0.95, anchor="center")

        # ── Right panel – form ────────────────────────────────────────────────
        right = ctk.CTkFrame(self, fg_color=Colors.BG_MAIN, corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew")

        card = ctk.CTkFrame(
            right,
            fg_color=Colors.BG_CARD,
            corner_radius=16,
            border_width=1,
            border_color=Colors.BORDER,
        )
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.72)

        # Card inner
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=40, pady=40)

        # Welcome text
        ctk.CTkLabel(
            inner, text="Welcome Back",
            font=(Fonts.FAMILY, Fonts.SIZE_4XL, Fonts.WEIGHT_BOLD),
            text_color=Colors.TEXT_HEADING,
            anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            inner, text="Sign in to access your EduTrack dashboard",
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            text_color=Colors.TEXT_MUTED,
            anchor="w",
        ).pack(anchor="w", pady=(4, 28))

        # Role selector
        self._make_label(inner, "Login As")
        role_frame = ctk.CTkFrame(inner, fg_color="transparent")
        role_frame.pack(fill="x", pady=(4, 16))
        for role in ROLES:
            rb = ctk.CTkRadioButton(
                role_frame, text=role,
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
        self._error_lbl.pack(anchor="w", pady=(4, 0))

        # Login button
        ctk.CTkButton(
            inner, text="Sign In  →",
            height=48, corner_radius=10,
            font=(Fonts.FAMILY, Fonts.SIZE_LG, Fonts.WEIGHT_BOLD),
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_DARK,
            text_color=Colors.TEXT_WHITE,
            command=self._attempt_login,
        ).pack(fill="x", pady=(20, 0))

        # Demo credentials hint
        hint_box = ctk.CTkFrame(
            inner, fg_color=Colors.PRIMARY_LIGHT,
            corner_radius=8, border_width=1, border_color=Colors.PRIMARY,
        )
        hint_box.pack(fill="x", pady=(20, 0))
        ctk.CTkLabel(
            hint_box,
            text="💡  Demo Credentials  —  Admin: admin / admin123  |  "
                 "Teacher: teacher / teacher123  |  Student: student / student123",
            font=(Fonts.FAMILY, Fonts.SIZE_XS),
            text_color=Colors.PRIMARY,
            wraplength=340,
            justify="left",
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
        entry.pack(fill="x", pady=(0, 16))
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
