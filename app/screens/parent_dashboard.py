"""
app/screens/parent_dashboard.py
Parent Portal – Child Performance & Guardian Communication Dashboard.
Provides real-time visibility into attendance, grade breakdown, timetable, and teacher notes.
Addresses CS3014 Section 1 (Parent visibility gap) and Section 2 (Deep HCI interaction).
"""

import customtkinter as ctk
from datetime import date
from app.config import (
    Colors, Fonts, Spacing, CARD_CORNER, ROLE_PARENT,
)
from app.components.cards import MetricCard, AlertCard, SectionHeader, StatusBadge
from app.components.state_view import StateView, StateSwitchDemoBar


class ParentDashboardScreen(ctk.CTkFrame):
    """Parent dashboard centered around the linked student's academic journey."""

    def __init__(self, parent, state, navigate_fn, toast_fn):
        super().__init__(parent, fg_color=Colors.BG_MAIN, corner_radius=0)
        self._state    = state
        self._navigate = navigate_fn
        self._toast    = toast_fn
        self._child    = self._state.get_linked_child()
        self._build()

    def _build(self):
        pad = Spacing.XL

        # Top HCI Demo State Switcher
        demo_bar_wrap = ctk.CTkFrame(self, fg_color="transparent")
        demo_bar_wrap.pack(fill="x", padx=pad, pady=(pad, 0))
        StateSwitchDemoBar(demo_bar_wrap, on_switch_fn=self._on_state_switch).pack(side="right")

        self._state_view = StateView(
            self,
            on_retry=lambda: self._on_state_switch("content"),
            on_action=lambda: self._navigate("help"),
        )
        self._state_view.pack(fill="both", expand=True)

        # Build main content inside state view
        scroll = ctk.CTkScrollableFrame(self._state_view.content_area, fg_color=Colors.BG_MAIN, corner_radius=0)
        scroll.pack(fill="both", expand=True)
        self._render_dashboard_content(scroll)

    def _on_state_switch(self, mode: str):
        if mode == "content":
            self._state_view.set_state("content")
        elif mode == "empty":
            self._state_view.set_state(
                "empty",
                title="No Linked Student Record",
                message="Your guardian account is not currently linked with any active student in the school registry.",
                action_text="Contact School Helpdesk",
            )
        elif mode == "loading":
            self._state_view.set_state(
                "loading",
                title="Synchronizing Child Gradebook...",
                message="Retrieving term scores, attendance logs, and teacher remarks from the school database.",
            )
        elif mode == "error":
            self._state_view.set_state(
                "error",
                title="Connection Timed Out",
                message="Unable to reach the school local records server. Please verify your network or retry.",
                error_details="ERR_PARENT_PORTAL_SYNC_TIMEOUT (Code 504)",
            )
        elif mode == "offline":
            self._state_view.set_state(
                "offline",
                title="Viewing Cached Child Report",
                message="You are viewing the offline snapshot of your child's data. Changes will sync when online.",
                action_text="Refresh Cached Data",
            )

    def _render_dashboard_content(self, parent):
        pad = Spacing.XL
        child = self._child or {
            "name": "Fatima Bibi Chaudhry",
            "class": "Class 8-A",
            "roll_no": "3",
            "id": "S003",
            "parent_name": "Rao Chaudhry",
        }

        # Calculate student stats
        att_pct = self._state.compute_attendance_pct(child["id"])
        child_marks = [m for m in self._state.marks if m["student_id"] == child["id"]]
        if child_marks:
            avg_score = round(sum(m["obtained"] for m in child_marks) / sum(m["total_marks"] for m in child_marks) * 100, 1)
        else:
            avg_score = 86.5

        # ── 1. Student Hero Profile Banner ────────────────────────────────────
        banner = ctk.CTkFrame(parent, fg_color=Colors.SECONDARY, corner_radius=12, height=115)
        banner.pack(fill="x", padx=pad, pady=(Spacing.SM, 0))
        banner.pack_propagate(False)

        # Left Info
        bi = ctk.CTkFrame(banner, fg_color="transparent")
        bi.place(relx=0.02, rely=0.5, anchor="w")

        # Avatar circle
        avatar_col = ctk.CTkFrame(bi, fg_color="transparent")
        avatar_col.pack(side="left", padx=(0, 14))
        av = ctk.CTkFrame(avatar_col, width=54, height=54, fg_color=Colors.PARENT_ACCENT, corner_radius=27)
        av.pack()
        av.pack_propagate(False)
        ctk.CTkLabel(av, text="👧", font=(Fonts.FAMILY, 24)).pack(expand=True)

        txt_col = ctk.CTkFrame(bi, fg_color="transparent")
        txt_col.pack(side="left")

        ctk.CTkLabel(
            txt_col,
            text=f"{child['name']}",
            font=(Fonts.FAMILY, Fonts.SIZE_2XL, Fonts.WEIGHT_BOLD),
            text_color=Colors.TEXT_WHITE,
        ).pack(anchor="w")

        ctk.CTkLabel(
            txt_col,
            text=f"{child['class']}  ·  Roll No: {child.get('roll_no', '3')}  ·  Student ID: {child['id']}  ·  Homeroom: Ustaz Bilal Ahmed",
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            text_color="#BBDEFB",
        ).pack(anchor="w", pady=(2, 0))

        badge_row = ctk.CTkFrame(txt_col, fg_color="transparent")
        badge_row.pack(anchor="w", pady=(4, 0))
        StatusBadge(badge_row, "Active").pack(side="left", padx=(0, 6))
        ctk.CTkLabel(
            badge_row,
            text="Fee Status: Paid (April 2026)  ·  Conduct: Excellent",
            font=(Fonts.FAMILY, Fonts.SIZE_XS),
            text_color="#90CAF9",
        ).pack(side="left")

        # Quick Leave & Teacher Action on Right
        btn_area = ctk.CTkFrame(banner, fg_color="transparent")
        btn_area.place(relx=0.98, rely=0.5, anchor="e")

        ctk.CTkButton(
            btn_area,
            text="✉  Message Teacher",
            height=34,
            corner_radius=8,
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            fg_color="#3949AB",
            text_color=Colors.TEXT_WHITE,
            hover_color="#283593",
            command=self._open_contact_dialog,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            btn_area,
            text="📝  Request Leave",
            height=34,
            corner_radius=8,
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            fg_color=Colors.PRIMARY,
            text_color=Colors.TEXT_WHITE,
            hover_color=Colors.PRIMARY_DARK,
            command=self._open_leave_dialog,
        ).pack(side="right")

        # ── 2. KPI Metrics with Drill-Down Clicks ─────────────────────────────
        SectionHeader(parent, "Child Academic Overview", "Click any metric card for full details"
                      ).pack(fill="x", padx=pad, pady=(Spacing.XL, Spacing.SM))

        kpi_frame = ctk.CTkFrame(parent, fg_color="transparent")
        kpi_frame.pack(fill="x", padx=pad)

        kpis = [
            ("Attendance Rate", f"{att_pct}%", Colors.SUCCESS if att_pct >= 85 else Colors.WARNING,
             "30-Day presence tracker", "+2.1% this month", Colors.SUCCESS, lambda: self._navigate("attendance")),
            ("Term Average", f"{avg_score}%", Colors.PRIMARY,
             "Overall exam performance", "Grade A", Colors.SUCCESS, lambda: self._navigate("marks")),
            ("Class Standing", "3rd of 33", Colors.INFO,
             "Rank in Class 8-A", "Top 10% Decile", Colors.SUCCESS, lambda: self._navigate("marks")),
            ("Next Exam", "12 Oct 2026", Colors.PARENT_ACCENT,
             "Mid-Term Mathematics", "In 17 Days", Colors.TEXT_MUTED, lambda: self._navigate("timetable")),
        ]

        for col, (title, val, acc, sub, tr, tc, cmd) in enumerate(kpis):
            kpi_frame.columnconfigure(col, weight=1)
            MetricCard(
                kpi_frame,
                title=title,
                value=val,
                icon="●",
                accent=acc,
                sub_label=sub,
                trend=tr,
                trend_color=tc,
                command=cmd,
            ).grid(row=0, column=col, padx=(0, Spacing.MD if col < 3 else 0), sticky="nsew", ipady=4)

        # ── 3. Two-Column Layout: Subject Scores & Attendance Breakdown ────────
        cols = ctk.CTkFrame(parent, fg_color="transparent")
        cols.pack(fill="both", expand=True, padx=pad, pady=(Spacing.XL, pad))
        cols.columnconfigure(0, weight=6)
        cols.columnconfigure(1, weight=4)

        # Left Column: Recent Subject Performance Breakdown
        left_card = ctk.CTkFrame(cols, fg_color=Colors.BG_CARD, corner_radius=10, border_width=1, border_color=Colors.BORDER)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, Spacing.MD))

        lc_head = ctk.CTkFrame(left_card, fg_color="transparent")
        lc_head.pack(fill="x", padx=Spacing.LG, pady=(Spacing.LG, Spacing.SM))
        ctk.CTkLabel(
            lc_head,
            text="📊  Subject Score Breakdown (Mid-Term)",
            font=(Fonts.FAMILY, Fonts.SIZE_LG, Fonts.WEIGHT_BOLD),
            text_color=Colors.TEXT_HEADING,
        ).pack(side="left")
        ctk.CTkButton(
            lc_head, text="Full Gradebook ↗",
            height=28, width=120, corner_radius=6,
            font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
            fg_color=Colors.BG_INPUT, text_color=Colors.PRIMARY,
            command=lambda: self._navigate("marks"),
        ).pack(side="right")

        # Render Subject Bars
        subj_container = ctk.CTkFrame(left_card, fg_color="transparent")
        subj_container.pack(fill="both", expand=True, padx=Spacing.LG, pady=(0, Spacing.LG))

        sample_subjects = [
            ("Mathematics", 92, 100, "A+"),
            ("Physics", 88, 100, "A"),
            ("Urdu Language", 90, 100, "A+"),
            ("English Lit", 82, 100, "A"),
            ("Chemistry", 79, 100, "B+"),
            ("Islamic Studies", 95, 100, "A+"),
        ]

        for sname, obt, tot, grd in sample_subjects:
            row = ctk.CTkFrame(subj_container, fg_color="transparent")
            row.pack(fill="x", pady=6)

            # Label + Grade
            r_top = ctk.CTkFrame(row, fg_color="transparent")
            r_top.pack(fill="x")
            ctk.CTkLabel(r_top, text=sname, font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_PRIMARY).pack(side="left")
            ctk.CTkLabel(r_top, text=f"{obt}/{tot}  ({grd})", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.PRIMARY).pack(side="right")

            # Progress bar
            bar = ctk.CTkProgressBar(row, height=8, corner_radius=4, progress_color=Colors.PRIMARY)
            bar.pack(fill="x", pady=(3, 0))
            bar.set(obt / tot)

        # Right Column: Teacher Remarks & Announcements
        right_card = ctk.CTkFrame(cols, fg_color=Colors.BG_CARD, corner_radius=10, border_width=1, border_color=Colors.BORDER)
        right_card.grid(row=0, column=1, sticky="nsew")

        rc_head = ctk.CTkFrame(right_card, fg_color="transparent")
        rc_head.pack(fill="x", padx=Spacing.LG, pady=(Spacing.LG, Spacing.SM))
        ctk.CTkLabel(
            rc_head,
            text="💬  Homeroom Teacher's Note",
            font=(Fonts.FAMILY, Fonts.SIZE_LG, Fonts.WEIGHT_BOLD),
            text_color=Colors.TEXT_HEADING,
        ).pack(anchor="w")

        # Note Card
        note_box = ctk.CTkFrame(right_card, fg_color=Colors.PRIMARY_LIGHT, corner_radius=8, border_width=1, border_color=Colors.BORDER)
        note_box.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.MD))
        ctk.CTkLabel(
            note_box,
            text="“Fatima has demonstrated remarkable analytical thinking in Mathematics and science practicals this term. Her attendance is consistent and she actively participates in classroom discussions. Keep up the high standard!”",
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            text_color=Colors.TEXT_PRIMARY,
            wraplength=320,
            justify="left",
        ).pack(padx=14, pady=12)

        ctk.CTkLabel(
            note_box,
            text="— Ustaz Bilal Ahmed (Class Teacher, Class 8-A)  ·  18 Sep 2026",
            font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
            text_color=Colors.PRIMARY,
        ).pack(anchor="e", padx=14, pady=(0, 10))

        # Important Notice Card
        AlertCard(
            right_card,
            title="Parent-Teacher Meeting",
            message="Scheduled for Saturday, 17th October 2026 at 10:00 AM in Hall-B. Please bring the mid-term progress booklet.",
            kind="info",
        ).pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.LG))

    # ── Dialogs ───────────────────────────────────────────────────────────────

    def _open_leave_dialog(self):
        win = ctk.CTkToplevel(self)
        win.title("Submit Leave Application")
        win.geometry("520x440")
        win.configure(fg_color=Colors.BG_CARD)
        win.grab_set()

        # Center top level
        win.transient(self.winfo_toplevel())

        pad = Spacing.XL
        ctk.CTkLabel(
            win, text="📝  Submit Student Leave Request",
            font=(Fonts.FAMILY, Fonts.SIZE_XL, Fonts.WEIGHT_BOLD),
            text_color=Colors.TEXT_HEADING,
        ).pack(anchor="w", padx=pad, pady=(pad, 4))

        ctk.CTkLabel(
            win, text=f"Student: {self._child['name']} ({self._child['class']})",
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            text_color=Colors.TEXT_MUTED,
        ).pack(anchor="w", padx=pad, pady=(0, 16))

        # Leave Type
        ctk.CTkLabel(win, text="Leave Reason Type:", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_SECONDARY).pack(anchor="w", padx=pad)
        ltype_var = ctk.StringVar(value="Medical / Sick Leave")
        ctk.CTkOptionMenu(
            win,
            values=["Medical / Sick Leave", "Family Urgent Work", "Out of Station", "Other"],
            variable=ltype_var,
            fg_color=Colors.BG_INPUT,
            button_color=Colors.PRIMARY,
            text_color=Colors.TEXT_PRIMARY,
            height=34,
        ).pack(fill="x", padx=pad, pady=(4, 12))

        # Date range
        ctk.CTkLabel(win, text="Leave Date(s):", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_SECONDARY).pack(anchor="w", padx=pad)
        date_entry = ctk.CTkEntry(
            win,
            placeholder_text=f"e.g. {date.today().isoformat()}",
            height=34, fg_color=Colors.BG_INPUT, border_color=Colors.BORDER, text_color=Colors.TEXT_PRIMARY,
        )
        date_entry.insert(0, date.today().isoformat())
        date_entry.pack(fill="x", padx=pad, pady=(4, 12))

        # Description
        ctk.CTkLabel(win, text="Reason Explanation:", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_SECONDARY).pack(anchor="w", padx=pad)
        reason_entry = ctk.CTkTextbox(
            win, height=80, fg_color=Colors.BG_INPUT, border_width=1, border_color=Colors.BORDER, text_color=Colors.TEXT_PRIMARY, font=(Fonts.FAMILY, Fonts.SIZE_SM)
        )
        reason_entry.insert("1.0", "Suffering from seasonal fever. Doctor advised 2 days bed rest.")
        reason_entry.pack(fill="x", padx=pad, pady=(4, 18))

        def submit():
            win.destroy()
            self._toast(f"Leave application submitted for {self._child['name']}. Notified homeroom teacher.", "success")

        btn_row = ctk.CTkFrame(win, fg_color="transparent")
        btn_row.pack(fill="x", padx=pad, pady=(0, pad))

        ctk.CTkButton(
            btn_row, text="Cancel", fg_color=Colors.BG_INPUT, text_color=Colors.TEXT_SECONDARY,
            height=36, corner_radius=8, command=win.destroy,
        ).pack(side="left")

        ctk.CTkButton(
            btn_row, text="✓  Submit Application", fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_DARK,
            height=36, corner_radius=8, font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            command=submit,
        ).pack(side="right")

    def _open_contact_dialog(self):
        win = ctk.CTkToplevel(self)
        win.title("Contact Homeroom Teacher")
        win.geometry("500x380")
        win.configure(fg_color=Colors.BG_CARD)
        win.grab_set()
        win.transient(self.winfo_toplevel())

        pad = Spacing.XL
        ctk.CTkLabel(
            win, text="✉  Direct Message to Teacher",
            font=(Fonts.FAMILY, Fonts.SIZE_XL, Fonts.WEIGHT_BOLD),
            text_color=Colors.TEXT_HEADING,
        ).pack(anchor="w", padx=pad, pady=(pad, 4))

        ctk.CTkLabel(
            win, text="Recipient: Ustaz Bilal Ahmed (Class Teacher, 8-A)",
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            text_color=Colors.PRIMARY,
        ).pack(anchor="w", padx=pad, pady=(0, 14))

        ctk.CTkLabel(win, text="Message Content:", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_SECONDARY).pack(anchor="w", padx=pad)
        msg_box = ctk.CTkTextbox(
            win, height=120, fg_color=Colors.BG_INPUT, border_width=1, border_color=Colors.BORDER, text_color=Colors.TEXT_PRIMARY, font=(Fonts.FAMILY, Fonts.SIZE_SM)
        )
        msg_box.insert("1.0", "Respected Ustaz Bilal,\nI wanted to discuss Fatima's preparation for the upcoming Science exam. Is there a convenient time for a brief call?")
        msg_box.pack(fill="x", padx=pad, pady=(4, 20))

        def send():
            win.destroy()
            self._toast("Message dispatched to Ustaz Bilal Ahmed via school communication channel.", "success")

        btn_row = ctk.CTkFrame(win, fg_color="transparent")
        btn_row.pack(fill="x", padx=pad, pady=(0, pad))
        ctk.CTkButton(btn_row, text="Cancel", fg_color=Colors.BG_INPUT, text_color=Colors.TEXT_SECONDARY, height=36, corner_radius=8, command=win.destroy).pack(side="left")
        ctk.CTkButton(btn_row, text="Send Message ✉", fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_DARK, height=36, corner_radius=8, font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), command=send).pack(side="right")
