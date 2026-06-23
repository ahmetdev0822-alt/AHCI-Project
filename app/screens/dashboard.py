"""
app/screens/dashboard.py
Role-aware dashboard – Blue & White theme.
Admin / Teacher views.
"""

import customtkinter as ctk
from datetime import date
from app.config import (
    Colors, Fonts, Spacing, CARD_CORNER,
    ROLE_ADMIN, ROLE_TEACHER,
)
from app.components.cards import MetricCard, AlertCard, QuickActionCard, SectionHeader, StatusBadge
from app.data.sample_data import get_dashboard_stats


class DashboardScreen(ctk.CTkFrame):
    def __init__(self, parent, state, navigate_fn, toast_fn):
        super().__init__(parent, fg_color=Colors.BG_MAIN, corner_radius=0)
        self._state    = state
        self._navigate = navigate_fn
        self._toast    = toast_fn
        self._stats    = get_dashboard_stats()
        self._build()

    def _build(self):
        role   = self._state.current_role
        scroll = ctk.CTkScrollableFrame(self, fg_color=Colors.BG_MAIN, corner_radius=0)
        scroll.pack(fill="both", expand=True)
        if role == ROLE_ADMIN:
            self._build_admin(scroll)
        elif role == ROLE_TEACHER:
            self._build_teacher(scroll)

    # ─────────────────────────────────────────────── ADMIN ────
    def _build_admin(self, parent):
        pad   = Spacing.XL
        stats = self._stats

        # Banner
        banner = ctk.CTkFrame(parent, fg_color=Colors.SECONDARY, corner_radius=12, height=100)
        banner.pack(fill="x", padx=pad, pady=(pad, 0))
        banner.pack_propagate(False)

        bi = ctk.CTkFrame(banner, fg_color="transparent")
        bi.place(relx=0.02, rely=0.5, anchor="w")
        name = self._state.current_user.get("full_name", "Administrator")

        # Greeting based on time
        hour = date.today().timetuple().tm_mday  # placeholder
        ctk.CTkLabel(bi,
                     text=f"Welcome back, {name}! 🛡",
                     font=(Fonts.FAMILY, Fonts.SIZE_2XL, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_WHITE).pack(anchor="w")
        ctk.CTkLabel(bi,
                     text=date.today().strftime("%A, %d %B %Y") + "  ·  Dar-e-Arqam School",
                     font=(Fonts.FAMILY, Fonts.SIZE_SM),
                     text_color="#90CAF9").pack(anchor="w", pady=(3, 0))
        ctk.CTkLabel(bi,
                     text="Administrator  ·  Full System Access",
                     font=(Fonts.FAMILY, Fonts.SIZE_XS),
                     text_color="#64B5F6").pack(anchor="w", pady=(2, 0))

        # Attendance pct on right
        qs = ctk.CTkFrame(banner, fg_color="transparent")
        qs.place(relx=0.97, rely=0.5, anchor="e")
        ac = Colors.SUCCESS if stats["attendance_pct"] >= 85 else Colors.WARNING
        ctk.CTkLabel(qs, text=f"{stats['attendance_pct']}%",
                     font=(Fonts.FAMILY, Fonts.SIZE_4XL, Fonts.WEIGHT_BOLD),
                     text_color=ac).pack()
        ctk.CTkLabel(qs, text="Today's Attendance",
                     font=(Fonts.FAMILY, Fonts.SIZE_XS),
                     text_color="#90CAF9").pack()

        # ── KPI Row ──────────────────────────────────────────────────────────
        ctk.CTkLabel(parent, text="Key Performance Indicators",
                     font=(Fonts.FAMILY, Fonts.SIZE_LG, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_HEADING, anchor="w",
                     ).pack(anchor="w", padx=pad, pady=(Spacing.XL, Spacing.SM))
        cf = ctk.CTkFrame(parent, fg_color="transparent")
        cf.pack(fill="x", padx=pad)
        kpis = [
            ("Total Students",  str(stats["total_students"]),  Colors.PRIMARY,  str(stats["active_students"]) + " active",     "+4 this month", Colors.SUCCESS),
            ("Total Teachers",  str(stats["total_teachers"]),  Colors.ACCENT,   str(stats["on_leave_teachers"]) + " on leave",  "1 on leave",    Colors.WARNING),
            ("Total Classes",   str(stats["total_classes"]),   Colors.INFO,     "Grades 1 to 10",                               "All running",   Colors.SUCCESS),
            ("Low Attendance",  str(stats["low_att_students"]),Colors.DANGER,   "Students below 75%",                           "⚠ Needs action",Colors.DANGER),
        ]
        for col, (title, value, accent, sub, trend, tc) in enumerate(kpis):
            cf.columnconfigure(col, weight=1)
            MetricCard(cf, title=title, value=value, icon="●", accent=accent,
                       sub_label=sub, trend=trend, trend_color=tc,
                       ).grid(row=0, column=col,
                               padx=(0, Spacing.MD if col < 3 else 0),
                               sticky="nsew", ipady=6)

        # ── Quick Actions ─────────────────────────────────────────────────────
        SectionHeader(parent, "Quick Actions", "Frequently used operations"
                      ).pack(fill="x", padx=pad, pady=(Spacing.XL, Spacing.SM))
        qa = ctk.CTkFrame(parent, fg_color="transparent")
        qa.pack(fill="x", padx=pad)
        actions = [
            ("Add Student",     "students",   Colors.PRIMARY),
            ("Mark Attendance", "attendance", Colors.SUCCESS),
            ("Enter Marks",     "marks",      Colors.ACCENT),
            ("View Reports",    "reports",    Colors.WARNING),
            ("Manage Classes",  "classes",    Colors.INFO),
            ("Manage Teachers", "teachers",   Colors.SECONDARY),
        ]
        for col, (label, nav, color) in enumerate(actions):
            qa.columnconfigure(col, weight=1)
            QuickActionCard(qa, label=label, icon="→",
                            command=lambda n=nav: self._navigate(n), accent=color,
                            ).grid(row=0, column=col,
                                    padx=(0, Spacing.MD if col < len(actions)-1 else 0),
                                    sticky="nsew", ipady=4)

        # ── Bottom 2-column ───────────────────────────────────────────────────
        bottom = ctk.CTkFrame(parent, fg_color="transparent")
        bottom.pack(fill="x", padx=pad, pady=(Spacing.XL, Spacing.XL))
        bottom.columnconfigure(0, weight=3)
        bottom.columnconfigure(1, weight=2)

        # Recent Activity
        ap = ctk.CTkFrame(bottom, fg_color=Colors.BG_CARD, corner_radius=CARD_CORNER,
                           border_width=1, border_color=Colors.BORDER)
        ap.grid(row=0, column=0, sticky="nsew", padx=(0, Spacing.MD))

        aph = ctk.CTkFrame(ap, fg_color=Colors.BG_TABLE_HEAD, corner_radius=0)
        aph.pack(fill="x")
        ctk.CTkLabel(aph, text="  📌  Recent Activity",
                     font=(Fonts.FAMILY, Fonts.SIZE_MD, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_HEADING, anchor="w",
                     ).pack(anchor="w", padx=Spacing.MD, pady=10)

        ab = ctk.CTkFrame(ap, fg_color="transparent")
        ab.pack(fill="both", expand=True, padx=Spacing.MD, pady=Spacing.SM)
        for color, text, ts in [
            (Colors.SUCCESS,  "Attendance marked for Class 8-A",       "2 min ago"),
            (Colors.INFO,     "Marks entered – Math Quiz, Class 9-A",  "15 min ago"),
            (Colors.PRIMARY,  "New student admitted: Hamza Sheikh",     "1 hr ago"),
            (Colors.WARNING,  "3 students attendance below 75%",        "Today"),
            (Colors.ACCENT,   "Ustaza Samina Khatoon on leave",         "Today"),
            (Colors.SECONDARY,"Monthly report – Class 10-A generated",  "Yesterday"),
        ]:
            r = ctk.CTkFrame(ab, fg_color="transparent", height=42)
            r.pack(fill="x", pady=1)
            r.pack_propagate(False)
            dot = ctk.CTkFrame(r, width=26, height=26,
                                fg_color=MetricCard._alpha_color(color), corner_radius=13)
            dot.pack(side="left", pady=8)
            dot.pack_propagate(False)
            ctk.CTkLabel(dot, text="●", font=(Fonts.FAMILY, 8),
                         text_color=color).pack(expand=True)
            ctk.CTkLabel(r, text=text, font=(Fonts.FAMILY, Fonts.SIZE_SM),
                         text_color=Colors.TEXT_PRIMARY, anchor="w").pack(side="left", padx=(10, 0))
            ctk.CTkLabel(r, text=ts, font=(Fonts.FAMILY, Fonts.SIZE_XS),
                         text_color=Colors.TEXT_MUTED, anchor="e").pack(side="right")
            ctk.CTkFrame(ab, height=1, fg_color=Colors.DIVIDER).pack(fill="x")

        # Alerts
        alp = ctk.CTkFrame(bottom, fg_color=Colors.BG_CARD, corner_radius=CARD_CORNER,
                            border_width=1, border_color=Colors.BORDER)
        alp.grid(row=0, column=1, sticky="nsew")
        alh = ctk.CTkFrame(alp, fg_color=Colors.BG_TABLE_HEAD, corner_radius=0)
        alh.pack(fill="x")
        ctk.CTkLabel(alh, text="  🔔  System Alerts",
                     font=(Fonts.FAMILY, Fonts.SIZE_MD, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_HEADING, anchor="w",
                     ).pack(anchor="w", padx=Spacing.MD, pady=10)
        alb = ctk.CTkFrame(alp, fg_color="transparent")
        alb.pack(fill="both", expand=True, padx=Spacing.SM, pady=Spacing.SM)
        AlertCard(alb, "Low Attendance",
                  f"{stats['low_att_students']} students have attendance below 75%. Notify parents.",
                  kind="danger").pack(fill="x", pady=(0, Spacing.SM))
        AlertCard(alb, "Teacher On Leave",
                  "Ustaza Samina Khatoon is on medical leave. Class 1-B needs a substitute.",
                  kind="warning").pack(fill="x", pady=(0, Spacing.SM))
        AlertCard(alb, "Exams Next Week",
                  "Mid-Term exams start Monday. Ensure all timetables are finalized.",
                  kind="info").pack(fill="x")

    # ─────────────────────────────────────────────── TEACHER ──
    def _build_teacher(self, parent):
        pad  = Spacing.XL
        name = self._state.current_user.get("full_name", "Teacher")
        my_class = self._state.current_user.get("class", "—")

        banner = ctk.CTkFrame(parent, fg_color=Colors.ACCENT, corner_radius=12, height=96)
        banner.pack(fill="x", padx=pad, pady=(pad, 0))
        banner.pack_propagate(False)
        bi = ctk.CTkFrame(banner, fg_color="transparent")
        bi.place(relx=0.03, rely=0.5, anchor="w")
        ctk.CTkLabel(bi, text=f"Assalam-o-Alaikum, {name} 📚",
                     font=(Fonts.FAMILY, Fonts.SIZE_2XL, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_WHITE).pack(anchor="w")
        ctk.CTkLabel(bi, text=date.today().strftime("%A, %d %B %Y") + f"  ·  Your class: {my_class}",
                     font=(Fonts.FAMILY, Fonts.SIZE_SM),
                     text_color="#E0F2F1").pack(anchor="w", pady=(3, 0))
        ctk.CTkLabel(bi, text="Teacher  ·  Access limited to your assigned class only",
                     font=(Fonts.FAMILY, Fonts.SIZE_XS),
                     text_color="#B2DFDB").pack(anchor="w", pady=(2, 0))

        # KPIs
        ctk.CTkLabel(parent, text="Your Today Summary",
                     font=(Fonts.FAMILY, Fonts.SIZE_LG, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_HEADING, anchor="w",
                     ).pack(anchor="w", padx=pad, pady=(Spacing.XL, Spacing.SM))
        cf = ctk.CTkFrame(parent, fg_color="transparent")
        cf.pack(fill="x", padx=pad)
        for col, (title, value, accent, sub) in enumerate([
            ("My Class",         my_class,  Colors.PRIMARY,  "Assigned class"),
            ("Attendance Status","Pending",  Colors.WARNING,  "Mark today's attendance"),
            ("Periods Today",    "6",        Colors.ACCENT,   "Scheduled periods"),
            ("Pending Marks",    "3",        Colors.DANGER,   "Subjects pending entry"),
        ]):
            cf.columnconfigure(col, weight=1)
            MetricCard(cf, title=title, value=value, icon="●", accent=accent, sub_label=sub,
                       ).grid(row=0, column=col, padx=(0, Spacing.MD if col < 3 else 0),
                               sticky="nsew", ipady=6)

        # Quick actions
        SectionHeader(parent, "Quick Actions", "Jump to your tasks"
                      ).pack(fill="x", padx=pad, pady=(Spacing.XL, Spacing.SM))
        qa = ctk.CTkFrame(parent, fg_color="transparent")
        qa.pack(fill="x", padx=pad)
        for col, (label, nav, color) in enumerate([
            ("Mark Attendance", "attendance", Colors.SUCCESS),
            ("Enter Marks",     "marks",      Colors.ACCENT),
            ("View Timetable",  "timetable",  Colors.PRIMARY),
            ("Class Reports",   "reports",    Colors.WARNING),
        ]):
            qa.columnconfigure(col, weight=1)
            QuickActionCard(qa, label=label, icon="→",
                            command=lambda n=nav: self._navigate(n), accent=color,
                            ).grid(row=0, column=col, padx=(0, Spacing.MD if col < 3 else 0),
                                    sticky="nsew", ipady=4)

        # Attendance preview
        ctk.CTkLabel(parent, text=f"{my_class}  –  Today's Attendance Preview",
                     font=(Fonts.FAMILY, Fonts.SIZE_LG, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_HEADING, anchor="w",
                     ).pack(anchor="w", padx=pad, pady=(Spacing.XL, Spacing.SM))
        ap = ctk.CTkFrame(parent, fg_color=Colors.BG_CARD, corner_radius=CARD_CORNER,
                           border_width=1, border_color=Colors.BORDER)
        ap.pack(fill="x", padx=pad, pady=(0, pad))

        # Header
        thead = ctk.CTkFrame(ap, fg_color=Colors.BG_TABLE_HEAD, corner_radius=0, height=34)
        thead.pack(fill="x")
        thead.pack_propagate(False)
        for w, lbl in [(60, "Roll"), (220, "Student Name"), (120, "Status")]:
            ctk.CTkLabel(thead, text=lbl, width=w,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                         text_color=Colors.TEXT_HEADING, anchor="w").pack(side="left", padx=(8, 0))

        students_in_class = self._state.get_students_by_class(my_class)
        from app.data.sample_data import ATTENDANCE_RECORDS
        today_str = date.today().isoformat()
        for i, s in enumerate(students_in_class[:8]):
            recs   = [r for r in ATTENDANCE_RECORDS if r["student_id"] == s["id"] and r["date"] == today_str]
            status = recs[0]["status"] if recs else "—"
            bg = Colors.BG_TABLE_ROW if i % 2 == 0 else Colors.BG_TABLE_ALT
            row = ctk.CTkFrame(ap, fg_color=bg, height=36)
            row.pack(fill="x")
            row.pack_propagate(False)
            ctk.CTkLabel(row, text=s["roll_no"], width=60,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM),
                         text_color=Colors.TEXT_SECONDARY, anchor="w").pack(side="left", padx=(8, 0))
            ctk.CTkLabel(row, text=s["name"], width=220,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM),
                         text_color=Colors.TEXT_PRIMARY, anchor="w").pack(side="left")
            if status != "—":
                StatusBadge(row, status).pack(side="left", pady=5)
            else:
                ctk.CTkLabel(row, text="Not marked",
                             font=(Fonts.FAMILY, Fonts.SIZE_XS),
                             text_color=Colors.TEXT_MUTED).pack(side="left", padx=4)
            ctk.CTkFrame(ap, height=1, fg_color=Colors.DIVIDER).pack(fill="x")