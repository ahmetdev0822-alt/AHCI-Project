"""
app/screens/dashboard.py
Role-aware dashboard: Admin, Teacher, Student views.
"""
import customtkinter as ctk
from datetime import date
from app.config import Colors, Fonts, Spacing, CARD_CORNER, ROLE_ADMIN, ROLE_TEACHER, ROLE_STUDENT
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
        if   role == ROLE_ADMIN:   self._build_admin(scroll)
        elif role == ROLE_TEACHER: self._build_teacher(scroll)
        else:                      self._build_student(scroll)

    # ------------------------------------------------------------------ ADMIN
    def _build_admin(self, parent):
        pad, stats = Spacing.XL, self._stats

        # Banner
        banner = ctk.CTkFrame(parent, fg_color=Colors.SECONDARY, corner_radius=12, height=96)
        banner.pack(fill="x", padx=pad, pady=(pad, 0))
        banner.pack_propagate(False)
        bi = ctk.CTkFrame(banner, fg_color="transparent")
        bi.place(relx=0.02, rely=0.5, anchor="w")
        name = self._state.current_user.get("full_name", "Administrator")
        ctk.CTkLabel(bi, text="Good morning, " + name + "!",
                     font=(Fonts.FAMILY, Fonts.SIZE_2XL, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_WHITE).pack(anchor="w")
        today_str = date.today().strftime("%A, %d %B %Y")
        ctk.CTkLabel(bi, text=today_str + "  -  Dar-e-Arqam School",
                     font=(Fonts.FAMILY, Fonts.SIZE_SM), text_color=Colors.SIDEBAR_TEXT
                     ).pack(anchor="w", pady=(2, 0))
        # Attendance pct in banner
        qs = ctk.CTkFrame(banner, fg_color="transparent")
        qs.place(relx=0.98, rely=0.5, anchor="e")
        ac = Colors.SUCCESS if stats["attendance_pct"] >= 85 else Colors.WARNING
        ctk.CTkLabel(qs, text=str(stats["attendance_pct"]) + "%",
                     font=(Fonts.FAMILY, Fonts.SIZE_4XL, Fonts.WEIGHT_BOLD),
                     text_color=ac).pack()
        ctk.CTkLabel(qs, text="Today Attendance",
                     font=(Fonts.FAMILY, Fonts.SIZE_XS), text_color=Colors.SIDEBAR_TEXT).pack()

        # KPI row
        ctk.CTkLabel(parent, text="Key Performance Indicators",
                     font=(Fonts.FAMILY, Fonts.SIZE_LG, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_HEADING, anchor="w"
                     ).pack(anchor="w", padx=pad, pady=(Spacing.XL, Spacing.SM))
        cf = ctk.CTkFrame(parent, fg_color="transparent")
        cf.pack(fill="x", padx=pad)
        kpis = [
            ("Total Students",  str(stats["total_students"]),
             Colors.PRIMARY,   str(stats["active_students"]) + " active",     "+4 this month",   Colors.SUCCESS),
            ("Total Teachers",  str(stats["total_teachers"]),
             Colors.SECONDARY, str(stats["on_leave_teachers"]) + " on leave", "1 on leave",      Colors.WARNING),
            ("Total Classes",   str(stats["total_classes"]),
             Colors.INFO,      "Grades 1 to 10",                              "All running",     Colors.SUCCESS),
            ("Low Attendance",  str(stats["low_att_students"]),
             Colors.DANGER,    "Students below 75%",                          "Needs attention", Colors.DANGER),
        ]
        for col, (title, value, accent, sub, trend, tc) in enumerate(kpis):
            cf.columnconfigure(col, weight=1)
            MetricCard(cf, title=title, value=value, icon="~", accent=accent,
                       sub_label=sub, trend=trend, trend_color=tc,
                       ).grid(row=0, column=col, padx=(0, Spacing.MD if col < 3 else 0),
                              sticky="nsew", ipady=8)

        # Quick Actions
        SectionHeader(parent, "Quick Actions", "Frequently used operations"
                      ).pack(fill="x", padx=pad, pady=(Spacing.XL, Spacing.SM))
        qa = ctk.CTkFrame(parent, fg_color="transparent")
        qa.pack(fill="x", padx=pad)
        actions = [
            ("Add Student",     "students",   Colors.PRIMARY),
            ("Mark Attendance", "attendance", Colors.SUCCESS),
            ("Enter Marks",     "marks",      Colors.INFO),
            ("View Reports",    "reports",    Colors.WARNING),
            ("Manage Classes",  "classes",    Colors.SECONDARY),
            ("Manage Teachers", "teachers",   Colors.ACCENT),
        ]
        for col, (label, nav, color) in enumerate(actions):
            qa.columnconfigure(col, weight=1)
            QuickActionCard(qa, label=label, icon="+",
                            command=lambda n=nav: self._navigate(n), accent=color,
                            ).grid(row=0, column=col,
                                   padx=(0, Spacing.MD if col < len(actions)-1 else 0),
                                   sticky="nsew", ipady=6)

        # Bottom 2-col
        bottom = ctk.CTkFrame(parent, fg_color="transparent")
        bottom.pack(fill="x", padx=pad, pady=(Spacing.XL, Spacing.XL))
        bottom.columnconfigure(0, weight=2)
        bottom.columnconfigure(1, weight=1)

        # Activity
        ap = ctk.CTkFrame(bottom, fg_color=Colors.BG_CARD, corner_radius=CARD_CORNER,
                           border_width=1, border_color=Colors.BORDER)
        ap.grid(row=0, column=0, sticky="nsew", padx=(0, Spacing.MD))
        aph = ctk.CTkFrame(ap, fg_color=Colors.BG_TABLE_HEAD, corner_radius=0)
        aph.pack(fill="x")
        ctk.CTkLabel(aph, text="  Recent Activity",
                     font=(Fonts.FAMILY, Fonts.SIZE_MD, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_HEADING, anchor="w"
                     ).pack(anchor="w", padx=Spacing.MD, pady=Spacing.SM)
        ab = ctk.CTkFrame(ap, fg_color="transparent")
        ab.pack(fill="both", expand=True, padx=Spacing.MD, pady=Spacing.SM)
        for color, text, ts in [
            (Colors.SUCCESS,   "Attendance marked for Class 8-A",      "2 min ago"),
            (Colors.INFO,      "Marks entered - Math Quiz, Class 9-A",  "15 min ago"),
            (Colors.PRIMARY,   "New student admitted: Hamza Sheikh",    "1 hr ago"),
            (Colors.WARNING,   "3 students attendance below 75%",       "Today"),
            (Colors.ACCENT,    "Ustaza Samina Khatoon on leave",        "Today"),
            (Colors.SECONDARY, "Monthly report - Class 10-A",           "Yesterday"),
        ]:
            r = ctk.CTkFrame(ab, fg_color="transparent", height=44)
            r.pack(fill="x", pady=2)
            r.pack_propagate(False)
            dot = ctk.CTkFrame(r, width=28, height=28,
                                fg_color=MetricCard._alpha_color(color), corner_radius=14)
            dot.pack(side="left", pady=8)
            dot.pack_propagate(False)
            ctk.CTkLabel(dot, text="*", font=(Fonts.FAMILY, Fonts.SIZE_XS),
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
        ctk.CTkLabel(alh, text="  Alerts",
                     font=(Fonts.FAMILY, Fonts.SIZE_MD, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_HEADING, anchor="w"
                     ).pack(anchor="w", padx=Spacing.MD, pady=Spacing.SM)
        alb = ctk.CTkFrame(alp, fg_color="transparent")
        alb.pack(fill="both", expand=True, padx=Spacing.SM, pady=Spacing.SM)
        AlertCard(alb, "Low Attendance",
                  str(stats["low_att_students"]) + " students have attendance below 75%.",
                  kind="danger").pack(fill="x", pady=(0, Spacing.SM))
        AlertCard(alb, "Teacher On Leave",
                  "Ustaza Samina Khatoon is on medical leave. Class 1-B needs a substitute.",
                  kind="warning").pack(fill="x", pady=(0, Spacing.SM))
        AlertCard(alb, "Exams Next Week",
                  "Mid-Term exams starting Monday. Ensure all timetables are updated.",
                  kind="info").pack(fill="x")

    # --------------------------------------------------------------- TEACHER
    def _build_teacher(self, parent):
        pad  = Spacing.XL
        name = self._state.current_user.get("full_name", "Teacher")
        banner = ctk.CTkFrame(parent, fg_color=Colors.PRIMARY, corner_radius=12, height=88)
        banner.pack(fill="x", padx=pad, pady=(pad, 0))
        banner.pack_propagate(False)
        bi = ctk.CTkFrame(banner, fg_color="transparent")
        bi.place(relx=0.03, rely=0.5, anchor="w")
        ctk.CTkLabel(bi, text="Assalam-o-Alaikum, " + name,
                     font=(Fonts.FAMILY, Fonts.SIZE_2XL, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_WHITE).pack(anchor="w")
        ctk.CTkLabel(bi, text=date.today().strftime("%A, %d %B %Y") + "  -  Your schedule for today",
                     font=(Fonts.FAMILY, Fonts.SIZE_SM), text_color="#A8D5BC").pack(anchor="w", pady=(2, 0))

        ctk.CTkLabel(parent, text="Your Today Summary",
                     font=(Fonts.FAMILY, Fonts.SIZE_LG, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_HEADING, anchor="w"
                     ).pack(anchor="w", padx=pad, pady=(Spacing.XL, Spacing.SM))
        cf = ctk.CTkFrame(parent, fg_color="transparent")
        cf.pack(fill="x", padx=pad)
        for col, (title, value, accent, sub) in enumerate([
            ("My Classes",        "1",   Colors.PRIMARY,  "Class 6-A"),
            ("Attendance Marked", "Yes", Colors.SUCCESS,  "Class 6-A - Today"),
            ("Periods Today",     "6",   Colors.INFO,     "Scheduled"),
            ("Pending Marks",     "3",   Colors.WARNING,  "Subjects pending"),
        ]):
            cf.columnconfigure(col, weight=1)
            MetricCard(cf, title=title, value=value, icon="-", accent=accent, sub_label=sub,
                       ).grid(row=0, column=col, padx=(0, Spacing.MD if col < 3 else 0),
                              sticky="nsew", ipady=8)

        SectionHeader(parent, "Quick Actions", "Mark attendance or enter marks quickly"
                      ).pack(fill="x", padx=pad, pady=(Spacing.XL, Spacing.SM))
        qa = ctk.CTkFrame(parent, fg_color="transparent")
        qa.pack(fill="x", padx=pad)
        for col, (label, nav, color) in enumerate([
            ("Mark Attendance", "attendance", Colors.SUCCESS),
            ("Enter Marks",     "marks",      Colors.INFO),
            ("View Timetable",  "timetable",  Colors.PRIMARY),
            ("Generate Report", "reports",    Colors.WARNING),
        ]):
            qa.columnconfigure(col, weight=1)
            QuickActionCard(qa, label=label, icon="+",
                            command=lambda n=nav: self._navigate(n), accent=color,
                            ).grid(row=0, column=col, padx=(0, Spacing.MD if col < 3 else 0),
                                   sticky="nsew", ipady=6)

        ctk.CTkLabel(parent, text="Class 6-A - Today Attendance Preview",
                     font=(Fonts.FAMILY, Fonts.SIZE_LG, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_HEADING, anchor="w"
                     ).pack(anchor="w", padx=pad, pady=(Spacing.XL, Spacing.SM))
        ap = ctk.CTkFrame(parent, fg_color=Colors.BG_CARD, corner_radius=CARD_CORNER,
                           border_width=1, border_color=Colors.BORDER)
        ap.pack(fill="x", padx=pad, pady=(0, pad))
        students_6a = self._state.get_students_by_class("Class 6-A")
        from app.data.sample_data import ATTENDANCE_RECORDS
        today = date.today().isoformat()
        for s in students_6a[:6]:
            recs   = [r for r in ATTENDANCE_RECORDS
                      if r["student_id"] == s["id"] and r["date"] == today]
            status = recs[0]["status"] if recs else "Absent"
            row = ctk.CTkFrame(ap, fg_color="transparent", height=36)
            row.pack(fill="x", padx=Spacing.LG)
            row.pack_propagate(False)
            ctk.CTkLabel(row, text=s["roll_no"] + ".  " + s["name"],
                         font=(Fonts.FAMILY, Fonts.SIZE_SM),
                         text_color=Colors.TEXT_PRIMARY, anchor="w").pack(side="left")
            v = status if status in ("Present", "Absent", "Late") else "Absent"
            StatusBadge(row, v).pack(side="right", pady=4)
            ctk.CTkFrame(ap, height=1, fg_color=Colors.DIVIDER).pack(fill="x", padx=Spacing.LG)

    # --------------------------------------------------------------- STUDENT
    def _build_student(self, parent):
        pad  = Spacing.XL
        name = self._state.current_user.get("full_name", "Student")
        banner = ctk.CTkFrame(parent, fg_color=Colors.SECONDARY, corner_radius=12, height=88)
        banner.pack(fill="x", padx=pad, pady=(pad, 0))
        banner.pack_propagate(False)
        bi = ctk.CTkFrame(banner, fg_color="transparent")
        bi.place(relx=0.03, rely=0.5, anchor="w")
        ctk.CTkLabel(bi, text="Welcome, " + name,
                     font=(Fonts.FAMILY, Fonts.SIZE_2XL, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_WHITE).pack(anchor="w")
        ctk.CTkLabel(bi, text=date.today().strftime("%A, %d %B %Y") + "  -  Class 8-A  |  Roll 12",
                     font=(Fonts.FAMILY, Fonts.SIZE_SM), text_color=Colors.SIDEBAR_TEXT
                     ).pack(anchor="w", pady=(2, 0))

        cf = ctk.CTkFrame(parent, fg_color="transparent")
        cf.pack(fill="x", padx=pad, pady=(Spacing.XL, 0))
        att_pct   = self._state.compute_attendance_pct("S001")
        att_color = Colors.SUCCESS if att_pct >= 75 else Colors.DANGER
        for col, (title, value, accent, sub) in enumerate([
            ("My Attendance", str(att_pct) + "%", att_color,    "This session"),
            ("Best Subject",  "Islamic St.",      Colors.ACCENT,  "92 / 100"),
            ("Class Rank",    "#4",               Colors.WARNING, "Out of 35 students"),
            ("Upcoming Test", "2 Days",           Colors.DANGER,  "Final Exam - Math"),
        ]):
            cf.columnconfigure(col, weight=1)
            MetricCard(cf, title=title, value=value, icon="-", accent=accent, sub_label=sub,
                       ).grid(row=0, column=col, padx=(0, Spacing.MD if col < 3 else 0),
                              sticky="nsew", ipady=8)

        SectionHeader(parent, "Recent Results", "Your latest exam scores"
                      ).pack(fill="x", padx=pad, pady=(Spacing.XL, Spacing.SM))
        mp = ctk.CTkFrame(parent, fg_color=Colors.BG_CARD, corner_radius=CARD_CORNER,
                           border_width=1, border_color=Colors.BORDER)
        mp.pack(fill="x", padx=pad, pady=(0, pad))
        from app.data.sample_data import MARKS_RECORDS
        my_marks = [m for m in MARKS_RECORDS if m["student_id"] == "S001"][:6]
        for i, m in enumerate(my_marks):
            bg  = Colors.BG_TABLE_ROW if i % 2 == 0 else Colors.BG_TABLE_ALT
            row = ctk.CTkFrame(mp, fg_color=bg, height=38)
            row.pack(fill="x")
            row.pack_propagate(False)
            ctk.CTkLabel(row, text="  " + m["subject"],
                         font=(Fonts.FAMILY, Fonts.SIZE_SM),
                         text_color=Colors.TEXT_PRIMARY, anchor="w", width=180).pack(side="left")
            ctk.CTkLabel(row, text=m["assessment"],
                         font=(Fonts.FAMILY, Fonts.SIZE_SM),
                         text_color=Colors.TEXT_SECONDARY, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=str(m["obtained"]) + "/" + str(m["total_marks"]),
                         font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                         text_color=Colors.TEXT_PRIMARY, anchor="e",
                         ).pack(side="right", padx=(0, Spacing.MD))
            StatusBadge(row, m["grade"]).pack(side="right", pady=5, padx=(0, 8))
            ctk.CTkFrame(mp, height=1, fg_color=Colors.DIVIDER).pack(fill="x")
