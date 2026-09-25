"""
app/screens/dashboard.py
Role-aware dashboard – Blue & White theme.
Supports Administrator, Teacher, and Parent views with interactive KPI drill-downs.
Addresses CS3014 Section 2 (Deep HCI interactivity via drill-down navigation).
"""

import customtkinter as ctk
from datetime import date
from app.config import (
    Colors, Fonts, Spacing, CARD_CORNER,
    ROLE_ADMIN, ROLE_TEACHER, ROLE_PARENT,
)
from app.components.cards import MetricCard, AlertCard, QuickActionCard, SectionHeader, StatusBadge
from app.components.state_view import StateView, StateSwitchDemoBar
from app.data.sample_data import get_dashboard_stats


class DashboardScreen(ctk.CTkFrame):
    def __init__(self, parent, state, navigate_fn, toast_fn):
        super().__init__(parent, fg_color=Colors.BG_MAIN, corner_radius=0)
        self._state    = state
        self._navigate = navigate_fn
        self._toast    = toast_fn
        self._stats    = get_dashboard_stats(state)
        self._build()

    def _build(self):
        pad = Spacing.XL

        top_row = ctk.CTkFrame(self, fg_color="transparent")
        top_row.pack(fill="x", padx=pad, pady=(pad, 0))
        StateSwitchDemoBar(top_row, on_switch_fn=self._on_state_switch).pack(side="right")

        self._state_view = StateView(
            self,
            on_retry=lambda: self._on_state_switch("content"),
            on_action=lambda: self._navigate("help"),
        )
        self._state_view.pack(fill="both", expand=True)

        role = self._state.current_role
        scroll = ctk.CTkScrollableFrame(self._state_view.content_area, fg_color=Colors.BG_MAIN, corner_radius=0)
        scroll.pack(fill="both", expand=True)

        if role == ROLE_ADMIN:
            self._build_admin(scroll)
        elif role == ROLE_TEACHER:
            self._build_teacher(scroll)
        elif role == ROLE_PARENT:
            from app.screens.parent_dashboard import ParentDashboardScreen
            p_dash = ParentDashboardScreen(self._state_view.content_area, self._state, self._navigate, self._toast)
            p_dash.pack(fill="both", expand=True)

    def _on_state_switch(self, mode: str):
        if mode == "content":
            self._state_view.set_state("content")
        elif mode == "empty":
            self._state_view.set_state("empty", title="No Active Academic Session", message="No active term data found. Please configure session in Settings.", action_text="Open Settings")
        elif mode == "loading":
            self._state_view.set_state("loading", title="Computing Institutional Analytics...", message="Aggregating attendance percentages, grade distributions, and teacher rosters.")
        elif mode == "error":
            self._state_view.set_state("error", title="Failed to Compute Dashboard Metrics", message="A transient error occurred while querying the local SQLite database.", error_details="ERR_SQLITE_QUERY_METRIC_FAIL (Code 500)")
        elif mode == "offline":
            self._state_view.set_state("offline", title="Viewing Offline Snapshot", message="Metrics are compiled from your local SQLite cache. Sync will resume when online.", action_text="Refresh Offline Data")

    # ─────────────────────────────────────────────── ADMIN ────
    def _build_admin(self, parent):
        pad   = Spacing.XL
        stats = self._stats

        # Banner
        banner = ctk.CTkFrame(parent, fg_color=Colors.SECONDARY, corner_radius=12, height=100)
        banner.pack(fill="x", padx=pad, pady=(Spacing.SM, 0))
        banner.pack_propagate(False)

        bi = ctk.CTkFrame(banner, fg_color="transparent")
        bi.place(relx=0.02, rely=0.5, anchor="w")
        name = (self._state.current_user or {}).get("full_name", "Administrator")

        ctk.CTkLabel(bi,
                     text=f"Welcome back, {name}! 🛡",
                     font=(Fonts.FAMILY, Fonts.SIZE_2XL, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_WHITE).pack(anchor="w")
        ctk.CTkLabel(bi,
                     text=date.today().strftime("%A, %d %B %Y") + "  ·  Dar-e-Arqam School",
                     font=(Fonts.FAMILY, Fonts.SIZE_SM),
                     text_color="#90CAF9").pack(anchor="w", pady=(3, 0))
        ctk.CTkLabel(bi,
                     text="Administrator  ·  Full System Access  ·  SQLite Active",
                     font=(Fonts.FAMILY, Fonts.SIZE_XS),
                     text_color="#64B5F6").pack(anchor="w", pady=(2, 0))

        # Attendance pct on right
        qs = ctk.CTkFrame(banner, fg_color="transparent", cursor="hand2")
        qs.place(relx=0.97, rely=0.5, anchor="e")
        ac = Colors.SUCCESS if stats["attendance_pct"] >= 85 else Colors.WARNING
        ctk.CTkLabel(qs, text=f"{stats['attendance_pct']}%",
                     font=(Fonts.FAMILY, Fonts.SIZE_4XL, Fonts.WEIGHT_BOLD),
                     text_color=ac).pack()
        ctk.CTkLabel(qs, text="Today's Attendance ↗",
                     font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
                     text_color="#90CAF9").pack()
        qs.bind("<Button-1>", lambda e: self._navigate("attendance"))

        # ── KPI Row with Interactive Drill-Downs ──────────────────────────────
        SectionHeader(parent, "Key Performance Indicators", "Click any KPI card to open filtered management views"
                      ).pack(fill="x", padx=pad, pady=(Spacing.XL, Spacing.SM))

        cf = ctk.CTkFrame(parent, fg_color="transparent")
        cf.pack(fill="x", padx=pad)

        kpis = [
            ("Total Students",  str(len(self._state.students)),  Colors.PRIMARY,  f"{sum(1 for s in self._state.students if s['status']=='Active')} active",     "+4 this month", Colors.SUCCESS, lambda: self._navigate("students")),
            ("Total Teachers",  str(len(self._state.teachers)),  Colors.ACCENT,   f"{sum(1 for t in self._state.teachers if t['status']=='On Leave')} on leave",  "1 on leave",    Colors.WARNING, lambda: self._navigate("teachers")),
            ("Total Classes",   str(len(self._state.classes)),   Colors.INFO,     "Grades 1 to 10",                               "All running",   Colors.SUCCESS, lambda: self._navigate("classes")),
            ("Low Attendance",  str(stats["low_att_students"]),Colors.DANGER,   "Students below 75%",                           "⚠ Needs action",Colors.DANGER,  lambda: self._navigate("attendance")),
        ]
        for col, (title, value, accent, sub, trend, tc, cmd) in enumerate(kpis):
            cf.columnconfigure(col, weight=1)
            MetricCard(cf, title=title, value=value, icon="●", accent=accent,
                       sub_label=sub, trend=trend, trend_color=tc, command=cmd
                       ).grid(row=0, column=col,
                                padx=(0, Spacing.MD if col < 3 else 0),
                                sticky="nsew", ipady=4)

        # ── Quick Actions ─────────────────────────────────────────────────────
        SectionHeader(parent, "Quick Operations", "Direct shortcuts to frequent administrator tasks"
                      ).pack(fill="x", padx=pad, pady=(Spacing.XL, Spacing.SM))
        qa = ctk.CTkFrame(parent, fg_color="transparent")
        qa.pack(fill="x", padx=pad)
        actions = [
            ("Add Student",     "👤", lambda: self._navigate("students"),   Colors.PRIMARY),
            ("Add Teacher",     "🎓", lambda: self._navigate("teachers"),   Colors.ACCENT),
            ("Class Timetable", "📅", lambda: self._navigate("timetable"),  Colors.INFO),
            ("View Reports",    "📋", lambda: self._navigate("reports"),    Colors.PRIMARY),
            ("Interactive Tour","✨", lambda: self._navigate("onboarding"), Colors.PARENT_ACCENT),
            ("Settings",        "⚙",  lambda: self._navigate("settings"),   Colors.TEXT_SECONDARY),
        ]
        for col, (label, icon, cmd, acc) in enumerate(actions):
            qa.columnconfigure(col, weight=1)
            QuickActionCard(qa, label=label, icon=icon, command=cmd, accent=acc
                            ).grid(row=0, column=col,
                                   padx=(0, Spacing.SM if col < len(actions)-1 else 0),
                                   sticky="nsew", ipady=2)

        # ── Two-Column Lower Section ──────────────────────────────────────────
        cols = ctk.CTkFrame(parent, fg_color="transparent")
        cols.pack(fill="both", expand=True, padx=pad, pady=(Spacing.XL, pad))
        cols.columnconfigure(0, weight=6)
        cols.columnconfigure(1, weight=4)

        # Left: Recent Attendance Overview
        left_card = ctk.CTkFrame(cols, fg_color=Colors.BG_CARD, corner_radius=10, border_width=1, border_color=Colors.BORDER)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, Spacing.MD))

        l_head = ctk.CTkFrame(left_card, fg_color="transparent")
        l_head.pack(fill="x", padx=Spacing.LG, pady=(Spacing.LG, Spacing.SM))
        ctk.CTkLabel(l_head, text="📋  Today's Attendance Status by Class", font=(Fonts.FAMILY, Fonts.SIZE_LG, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_HEADING).pack(side="left")
        ctk.CTkButton(l_head, text="Full Matrix ↗", height=28, width=110, corner_radius=6, font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD), fg_color=Colors.BG_INPUT, text_color=Colors.PRIMARY, command=lambda: self._navigate("attendance")).pack(side="right")

        rows_f = ctk.CTkFrame(left_card, fg_color="transparent")
        rows_f.pack(fill="both", expand=True, padx=Spacing.LG, pady=(0, Spacing.LG))

        sample_classes = [
            ("Class 8-A", 35, 33, 2, "94.3%"),
            ("Class 6-A", 33, 31, 2, "93.9%"),
            ("Class 9-A", 38, 34, 4, "89.5%"),
            ("Class 10-A", 40, 37, 3, "92.5%"),
        ]
        for cname, tot, pres, absn, pct in sample_classes:
            r = ctk.CTkFrame(rows_f, fg_color=Colors.BG_INPUT, corner_radius=6, border_width=1, border_color=Colors.BORDER)
            r.pack(fill="x", pady=4)
            ctk.CTkLabel(r, text=cname, font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_PRIMARY).pack(side="left", padx=12, pady=8)
            ctk.CTkLabel(r, text=f"Present: {pres}/{tot}  ·  Absent: {absn}", font=(Fonts.FAMILY, Fonts.SIZE_XS), text_color=Colors.TEXT_MUTED).pack(side="left", padx=10)
            ctk.CTkLabel(r, text=pct, font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.SUCCESS).pack(side="right", padx=12)

        # Right: System Alerts & Diagnostics
        right_card = ctk.CTkFrame(cols, fg_color=Colors.BG_CARD, corner_radius=10, border_width=1, border_color=Colors.BORDER)
        right_card.grid(row=0, column=1, sticky="nsew")

        r_head = ctk.CTkFrame(right_card, fg_color="transparent")
        r_head.pack(fill="x", padx=Spacing.LG, pady=(Spacing.LG, Spacing.SM))
        ctk.CTkLabel(r_head, text="⚠  Action Required", font=(Fonts.FAMILY, Fonts.SIZE_LG, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_HEADING).pack(anchor="w")

        AlertCard(right_card, title="Low Attendance Trigger", message="4 students in Class 8-A and Class 9-A have attendance below the 75% threshold.", kind="warning").pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.SM))
        AlertCard(right_card, title="Offline Storage Synced", message="All database transactions are persisted to local SQLite engine. Zero data loss guarantee.", kind="success").pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.LG))

    # ─────────────────────────────────────────────── TEACHER ──
    def _build_teacher(self, parent):
        pad   = Spacing.XL
        user  = self._state.current_user or {}
        name  = user.get("full_name", "Ustaz")
        t_class = user.get("class", "Class 6-A")

        banner = ctk.CTkFrame(parent, fg_color=Colors.SECONDARY, corner_radius=12, height=100)
        banner.pack(fill="x", padx=pad, pady=(Spacing.SM, 0))
        banner.pack_propagate(False)

        bi = ctk.CTkFrame(banner, fg_color="transparent")
        bi.place(relx=0.02, rely=0.5, anchor="w")
        ctk.CTkLabel(bi, text=f"Assalam-o-Alaikum, {name}! 📚", font=(Fonts.FAMILY, Fonts.SIZE_2XL, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_WHITE).pack(anchor="w")
        ctk.CTkLabel(bi, text=f"Class Teacher – {t_class}  ·  Dar-e-Arqam School", font=(Fonts.FAMILY, Fonts.SIZE_SM), text_color="#80CBC4").pack(anchor="w", pady=(3, 0))

        # KPI Row
        SectionHeader(parent, "Teacher Overview", "Click cards for direct marking and schedule management").pack(fill="x", padx=pad, pady=(Spacing.XL, Spacing.SM))

        cf = ctk.CTkFrame(parent, fg_color="transparent")
        cf.pack(fill="x", padx=pad)

        teacher_kpis = [
            ("My Homeroom", t_class, Colors.PRIMARY, "33 Enrolled Students", "Homeroom Active", Colors.SUCCESS, lambda: self._navigate("attendance")),
            ("Attendance Marked", "Today: Yes", Colors.SUCCESS, "Roll call completed", "31 Present", Colors.SUCCESS, lambda: self._navigate("attendance")),
            ("Pending Marks", "0 Exams", Colors.INFO, "Mid-Term Submitted", "100% Graded", Colors.SUCCESS, lambda: self._navigate("marks")),
            ("Today's Periods", "4 Lectures", Colors.ACCENT, "Math & Science", "Next: 10:30 AM", Colors.TEXT_MUTED, lambda: self._navigate("timetable")),
        ]

        for col, (title, val, acc, sub, tr, tc, cmd) in enumerate(teacher_kpis):
            cf.columnconfigure(col, weight=1)
            MetricCard(cf, title=title, value=val, icon="●", accent=acc, sub_label=sub, trend=tr, trend_color=tc, command=cmd).grid(row=0, column=col, padx=(0, Spacing.MD if col < 3 else 0), sticky="nsew", ipady=4)

        # Quick Actions
        SectionHeader(parent, "Teacher Shortcuts", "Direct operations").pack(fill="x", padx=pad, pady=(Spacing.XL, Spacing.SM))
        qa = ctk.CTkFrame(parent, fg_color="transparent")
        qa.pack(fill="x", padx=pad)
        t_actions = [
            ("Mark Attendance", "✓", lambda: self._navigate("attendance"), Colors.SUCCESS),
            ("Enter Marks",     "📊", lambda: self._navigate("marks"),      Colors.PRIMARY),
            ("My Timetable",    "📅", lambda: self._navigate("timetable"),  Colors.ACCENT),
            ("Class Reports",   "📋", lambda: self._navigate("reports"),    Colors.INFO),
        ]
        for col, (label, icon, cmd, acc) in enumerate(t_actions):
            qa.columnconfigure(col, weight=1)
            QuickActionCard(qa, label=label, icon=icon, command=cmd, accent=acc).grid(row=0, column=col, padx=(0, Spacing.SM if col < 3 else 0), sticky="nsew")