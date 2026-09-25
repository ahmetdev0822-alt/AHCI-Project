"""
app/screens/settings.py
System Settings & Accessibility Preferences Screen.
Configures school metadata, UI density, WCAG contrast mode, and offline sync intervals.
Addresses CS3014 Section 6 (Accessibility NFRs) and Section 12 (Digital Inclusion).
"""

import os
import customtkinter as ctk
from app.config import (
    Colors, Fonts, Spacing, CARD_CORNER, ROLE_ADMIN,
)
from app.components.cards import SectionHeader, AlertCard
from app.components.state_view import StateView, StateSwitchDemoBar
from app.db.database import db, DB_PATH


class SettingsScreen(ctk.CTkFrame):
    """System preferences, appearance scaling, and accessibility management."""

    def __init__(self, parent, state, navigate_fn, toast_fn):
        super().__init__(parent, fg_color=Colors.BG_MAIN, corner_radius=0)
        self._state    = state
        self._navigate = navigate_fn
        self._toast    = toast_fn
        self._settings = dict(self._state.settings)
        self._build()

    def _build(self):
        pad = Spacing.XL

        # Top Bar
        top_row = ctk.CTkFrame(self, fg_color="transparent")
        top_row.pack(fill="x", padx=pad, pady=(pad, Spacing.SM))
        SectionHeader(top_row, "System & Accessibility Settings", "Configure institution metadata, visual density, and offline synchronization").pack(side="left", fill="y")
        StateSwitchDemoBar(top_row, on_switch_fn=self._on_state_switch).pack(side="right")

        self._state_view = StateView(
            self,
            on_retry=lambda: self._on_state_switch("content"),
            on_action=lambda: self._navigate("dashboard"),
        )
        self._state_view.pack(fill="both", expand=True)

        scroll = ctk.CTkScrollableFrame(self._state_view.content_area, fg_color=Colors.BG_MAIN, corner_radius=0)
        scroll.pack(fill="both", expand=True)

        self._render_settings_form(scroll)

    def _on_state_switch(self, mode: str):
        if mode == "content":
            self._state_view.set_state("content")
        elif mode == "empty":
            self._state_view.set_state("empty", title="No Configuration Profiles Found", message="No active settings keys were loaded from the database.", action_text="Load Default Configuration")
        elif mode == "loading":
            self._state_view.set_state("loading", title="Writing System Configuration...", message="Updating local SQLite storage and applying global theme variables.")
        elif mode == "error":
            self._state_view.set_state("error", title="Permission Denied", message="Administrative privileges are required to modify institutional settings.", error_details="ERR_SECURITY_POLICY_VIOLATION (Code 403)")
        elif mode == "offline":
            self._state_view.set_state("offline", title="Offline Settings Mode", message="Settings will be stored in your local configuration mirror.", action_text="Sync with Network")

    def _render_settings_form(self, parent):
        pad = Spacing.XL

        # ── 1. Accessibility & Visual Density Section ─────────────────────────
        card1 = ctk.CTkFrame(parent, fg_color=Colors.BG_CARD, corner_radius=10, border_width=1, border_color=Colors.BORDER)
        card1.pack(fill="x", padx=pad, pady=(0, Spacing.XL))

        c1_head = ctk.CTkFrame(card1, fg_color="transparent")
        c1_head.pack(fill="x", padx=Spacing.LG, pady=(Spacing.LG, Spacing.SM))
        ctk.CTkLabel(c1_head, text="♿  Accessibility & Interface Density (WCAG 2.1 AA)", font=(Fonts.FAMILY, Fonts.SIZE_LG, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_HEADING).pack(anchor="w")
        ctk.CTkLabel(c1_head, text="Adapt the UI for low-vision users, elderly guardians, or touch terminals", font=(Fonts.FAMILY, Fonts.SIZE_SM), text_color=Colors.TEXT_MUTED).pack(anchor="w")

        c1_body = ctk.CTkFrame(card1, fg_color="transparent")
        c1_body.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.LG))

        # Density Mode Selector
        d_row = ctk.CTkFrame(c1_body, fg_color="transparent")
        d_row.pack(fill="x", pady=8)
        ctk.CTkLabel(d_row, text="Interface Layout Density:", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_PRIMARY).pack(side="left")
        self._density_var = ctk.StringVar(value=self._state.ui_density)
        ctk.CTkOptionMenu(
            d_row,
            values=["Comfortable (Large Touch Targets)", "Compact (High Data Density)"],
            variable=self._density_var,
            fg_color=Colors.BG_INPUT,
            button_color=Colors.PRIMARY,
            text_color=Colors.TEXT_PRIMARY,
            width=260, height=34,
        ).pack(side="right")

        # High Contrast Toggle
        hc_row = ctk.CTkFrame(c1_body, fg_color="transparent")
        hc_row.pack(fill="x", pady=8)
        ctk.CTkLabel(hc_row, text="High Contrast Mode (Enhanced 7:1 Contrast):", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_PRIMARY).pack(side="left")
        self._hc_var = ctk.BooleanVar(value=self._state.high_contrast)
        ctk.CTkSwitch(
            hc_row,
            text="Enabled" if self._state.high_contrast else "Standard WCAG AA (4.5:1)",
            variable=self._hc_var,
            progress_color=Colors.PRIMARY,
            command=self._on_hc_toggle,
        ).pack(side="right")

        # Font Engine Status
        f_row = ctk.CTkFrame(c1_body, fg_color="transparent")
        f_row.pack(fill="x", pady=8)
        ctk.CTkLabel(f_row, text="Active UI Font Family:", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_PRIMARY).pack(side="left")
        ctk.CTkLabel(f_row, text=f"{Fonts.FAMILY} (Antialiased System Native)", font=(Fonts.FAMILY_MONO, Fonts.SIZE_SM), text_color=Colors.PRIMARY).pack(side="right")

        # ── 2. Institution Metadata Section ───────────────────────────────────
        card2 = ctk.CTkFrame(parent, fg_color=Colors.BG_CARD, corner_radius=10, border_width=1, border_color=Colors.BORDER)
        card2.pack(fill="x", padx=pad, pady=(0, Spacing.XL))

        c2_head = ctk.CTkFrame(card2, fg_color="transparent")
        c2_head.pack(fill="x", padx=Spacing.LG, pady=(Spacing.LG, Spacing.SM))
        ctk.CTkLabel(c2_head, text="🏫  Institutional Profile & Academic Session", font=(Fonts.FAMILY, Fonts.SIZE_LG, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_HEADING).pack(anchor="w")

        c2_body = ctk.CTkFrame(card2, fg_color="transparent")
        c2_body.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.LG))

        # School Name
        s_row = ctk.CTkFrame(c2_body, fg_color="transparent")
        s_row.pack(fill="x", pady=6)
        ctk.CTkLabel(s_row, text="Institution Name:", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_PRIMARY).pack(side="left")
        self._name_entry = ctk.CTkEntry(s_row, width=320, height=34, fg_color=Colors.BG_INPUT, border_color=Colors.BORDER, text_color=Colors.TEXT_PRIMARY)
        self._name_entry.insert(0, self._settings.get("school_name", "Dar-e-Arqam School"))
        self._name_entry.pack(side="right")

        # Academic Session
        sess_row = ctk.CTkFrame(c2_body, fg_color="transparent")
        sess_row.pack(fill="x", pady=6)
        ctk.CTkLabel(sess_row, text="Academic Session:", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_PRIMARY).pack(side="left")
        self._sess_var = ctk.StringVar(value=self._settings.get("academic_session", "2025-2026"))
        ctk.CTkOptionMenu(sess_row, values=["2024-2025", "2025-2026", "2026-2027"], variable=self._sess_var, fg_color=Colors.BG_INPUT, button_color=Colors.PRIMARY, text_color=Colors.TEXT_PRIMARY, width=320, height=34).pack(side="right")

        # Current Term
        term_row = ctk.CTkFrame(c2_body, fg_color="transparent")
        term_row.pack(fill="x", pady=6)
        ctk.CTkLabel(term_row, text="Active Academic Term:", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_PRIMARY).pack(side="left")
        self._term_var = ctk.StringVar(value=self._settings.get("current_term", "First Term (Mid-Term)"))
        ctk.CTkOptionMenu(term_row, values=["First Term (Mid-Term)", "Second Term (Pre-Finals)", "Final Examination Session"], variable=self._term_var, fg_color=Colors.BG_INPUT, button_color=Colors.PRIMARY, text_color=Colors.TEXT_PRIMARY, width=320, height=34).pack(side="right")

        # ── 3. Digital Inclusion & Offline Resilience ─────────────────────────
        card3 = ctk.CTkFrame(parent, fg_color=Colors.BG_CARD, corner_radius=10, border_width=1, border_color=Colors.BORDER)
        card3.pack(fill="x", padx=pad, pady=(0, Spacing.XL))

        c3_head = ctk.CTkFrame(card3, fg_color="transparent")
        c3_head.pack(fill="x", padx=Spacing.LG, pady=(Spacing.LG, Spacing.SM))
        ctk.CTkLabel(c3_head, text="☁⃠  Digital Inclusion & Offline Synchronization", font=(Fonts.FAMILY, Fonts.SIZE_LG, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_HEADING).pack(anchor="w")
        ctk.CTkLabel(c3_head, text="Guarantees operation in environments with erratic power and zero cloud bandwidth", font=(Fonts.FAMILY, Fonts.SIZE_SM), text_color=Colors.TEXT_MUTED).pack(anchor="w")

        c3_body = ctk.CTkFrame(card3, fg_color="transparent")
        c3_body.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.LG))

        # DB File status
        db_size_kb = round(os.path.getsize(DB_PATH) / 1024, 1) if os.path.exists(DB_PATH) else 0.0
        db_row = ctk.CTkFrame(c3_body, fg_color="transparent")
        db_row.pack(fill="x", pady=6)
        ctk.CTkLabel(db_row, text="Local Storage Engine:", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_PRIMARY).pack(side="left")
        ctk.CTkLabel(db_row, text=f"SQLite 3 ({db_size_kb} KB · {len(self._state.students)} Students, {len(self._state.attendance)} Attendance Records)", font=(Fonts.FAMILY_MONO, Fonts.SIZE_SM), text_color=Colors.SUCCESS).pack(side="right")

        # Sync Interval
        sync_row = ctk.CTkFrame(c3_body, fg_color="transparent")
        sync_row.pack(fill="x", pady=6)
        ctk.CTkLabel(sync_row, text="Background Sync Frequency:", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_PRIMARY).pack(side="left")
        self._sync_var = ctk.StringVar(value=self._settings.get("offline_sync_interval", "15 mins"))
        ctk.CTkOptionMenu(sync_row, values=["5 mins", "15 mins", "30 mins", "Manual Trigger Only"], variable=self._sync_var, fg_color=Colors.BG_INPUT, button_color=Colors.PRIMARY, text_color=Colors.TEXT_PRIMARY, width=220, height=34).pack(side="right")

        # ── 4. Save Changes Bar ───────────────────────────────────────────────
        action_bar = ctk.CTkFrame(parent, fg_color="transparent")
        action_bar.pack(fill="x", padx=pad, pady=(0, pad))

        ctk.CTkButton(
            action_bar,
            text="⟳  Reset Sample Data",
            height=40,
            corner_radius=8,
            fg_color=Colors.BG_INPUT,
            text_color=Colors.DANGER,
            border_width=1,
            border_color=Colors.BORDER,
            hover_color=Colors.DANGER_BG,
            command=self._reset_sample_data,
        ).pack(side="left")

        ctk.CTkButton(
            action_bar,
            text="💾  Save Settings & Apply Changes",
            height=40,
            corner_radius=8,
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            fg_color=Colors.PRIMARY,
            text_color=Colors.TEXT_WHITE,
            hover_color=Colors.PRIMARY_DARK,
            command=self._save_settings,
        ).pack(side="right")

    def _on_hc_toggle(self):
        is_on = self._hc_var.get()
        self._state.high_contrast = is_on
        db.set_setting("high_contrast", str(is_on))
        self._toast(f"High Contrast Mode {'Enabled' if is_on else 'Disabled'}.", "info")

    def _save_settings(self):
        name = self._name_entry.get().strip() or "Dar-e-Arqam School"
        sess = self._sess_var.get()
        term = self._term_var.get()
        density = "Comfortable" if "Comfortable" in self._density_var.get() else "Compact"
        sync_int = self._sync_var.get()

        db.set_setting("school_name", name)
        db.set_setting("academic_session", sess)
        db.set_setting("current_term", term)
        db.set_setting("ui_density", density)
        db.set_setting("offline_sync_interval", sync_int)

        self._state.ui_density = density
        self._state.settings["school_name"] = name
        self._state.settings["academic_session"] = sess
        self._state.settings["current_term"] = term
        self._state.settings["ui_density"] = density
        self._state.settings["offline_sync_interval"] = sync_int

        self._toast("Settings successfully saved to local SQLite database!", "success")

    def _reset_sample_data(self):
        self._state.reload_from_db()
        self._toast("Local data mirrors refreshed from SQLite database.", "info")
