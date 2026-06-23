"""
app/screens/reports.py
Reports generation screen – Admin and Teacher views (filtered by access).
"""

import customtkinter as ctk
from collections import defaultdict
from app.config import Colors, Fonts, Spacing, CARD_CORNER
from app.components.cards import SectionHeader, StatusBadge, MetricCard


class ReportsScreen(ctk.CTkFrame):
    def __init__(self, parent, state, navigate_fn, toast_fn):
        super().__init__(parent, fg_color=Colors.BG_MAIN, corner_radius=0)
        self._state    = state
        self._navigate = navigate_fn
        self._toast    = toast_fn
        self._active_report = None
        self._build()

    def _build(self):
        pad = Spacing.XL

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=pad, pady=(pad, Spacing.SM))
        SectionHeader(toolbar, "Reports & Analytics",
                      "Generate, preview, and export school reports"
                      ).pack(side="left", fill="y")

        # Two-column layout
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=pad, pady=(0, pad))
        body.columnconfigure(0, weight=0)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        # ── Left: Report type list ────────────────────────────────────────────
        left = ctk.CTkFrame(body, fg_color=Colors.BG_CARD, corner_radius=10,
                             border_width=1, border_color=Colors.BORDER, width=260)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, Spacing.MD))
        left.pack_propagate(False)

        lh = ctk.CTkFrame(left, fg_color=Colors.PRIMARY, corner_radius=0, height=44)
        lh.pack(fill="x")
        lh.pack_propagate(False)
        ctk.CTkLabel(lh, text="  📋  Report Types",
                     font=(Fonts.FAMILY, Fonts.SIZE_MD, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_WHITE, anchor="w").pack(side="left", padx=12)

        report_types = [
            ("📋", "Student Report Card",     "student_report",   Colors.PRIMARY),
            ("✓",  "Class Attendance Report", "att_report",       Colors.SUCCESS),
            ("⚠",  "Low Attendance Alerts",   "low_att_report",   Colors.DANGER),
            ("📊", "Performance Summary",     "perf_report",      Colors.INFO),
        ]

        self._report_btns = {}
        list_scroll = ctk.CTkScrollableFrame(left, fg_color="transparent", corner_radius=0)
        list_scroll.pack(fill="both", expand=True)

        for icon, label, key, color in report_types:
            btn = ctk.CTkButton(
                list_scroll,
                text=f"  {icon}  {label}",
                anchor="w", height=48, corner_radius=8,
                font=(Fonts.FAMILY, Fonts.SIZE_SM),
                fg_color="transparent",
                text_color=Colors.TEXT_PRIMARY,
                hover_color=Colors.PRIMARY_LIGHT,
                command=lambda k=key, c=color: self._show_report(k, c),
            )
            btn.pack(fill="x", padx=6, pady=2)
            self._report_btns[key] = (btn, color)

        # Export buttons
        export_frame = ctk.CTkFrame(left, fg_color="transparent")
        export_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(
            export_frame, text="📄  Export PDF", height=34, corner_radius=8,
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            fg_color=Colors.DANGER_BG, text_color=Colors.DANGER,
            hover_color=Colors.DANGER,
            command=lambda: self._toast("PDF export – feature ready for integration!", "info"),
        ).pack(fill="x", pady=(0, 6))
        ctk.CTkButton(
            export_frame, text="📊  Export Excel", height=34, corner_radius=8,
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            fg_color=Colors.SUCCESS_BG, text_color=Colors.SUCCESS,
            hover_color=Colors.SUCCESS,
            command=lambda: self._toast("Excel export – feature ready for integration!", "info"),
        ).pack(fill="x")

        # ── Right: Report preview panel ───────────────────────────────────────
        self._preview = ctk.CTkFrame(body, fg_color=Colors.BG_CARD, corner_radius=10,
                                      border_width=1, border_color=Colors.BORDER)
        self._preview.grid(row=0, column=1, sticky="nsew")

        self._show_placeholder()

    def _show_placeholder(self):
        for w in self._preview.winfo_children():
            w.destroy()
        placeholder = ctk.CTkFrame(self._preview, fg_color="transparent")
        placeholder.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(placeholder, text="📋",
                     font=(Fonts.FAMILY, 52),
                     text_color=Colors.TEXT_MUTED).pack()
        ctk.CTkLabel(placeholder, text="Select a report type to preview",
                     font=(Fonts.FAMILY, Fonts.SIZE_LG),
                     text_color=Colors.TEXT_MUTED).pack(pady=(12, 0))
        ctk.CTkLabel(placeholder, text="Use the panel on the left to choose a report.",
                     font=(Fonts.FAMILY, Fonts.SIZE_SM),
                     text_color=Colors.TEXT_MUTED).pack(pady=(4, 0))

    def _show_report(self, key: str, color: str):
        self._active_report = key

        # Highlight active button
        for k, (btn, c) in self._report_btns.items():
            if k == key:
                btn.configure(fg_color=MetricCard._alpha_color(c), text_color=c)
            else:
                btn.configure(fg_color="transparent", text_color=Colors.TEXT_PRIMARY)

        for w in self._preview.winfo_children():
            w.destroy()

        if key == "student_report":
            self._draw_student_report()
        elif key == "att_report":
            self._draw_attendance_report()
        elif key == "low_att_report":
            self._draw_low_att_report()
        elif key == "perf_report":
            self._draw_performance_report()

    # ── Report Renderers ─────────────────────────────────────────────────────

    def _report_header(self, title: str, subtitle: str, color: str):
        hdr = ctk.CTkFrame(self._preview, fg_color=color, corner_radius=0, height=60)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        inner = ctk.CTkFrame(hdr, fg_color="transparent")
        inner.place(relx=0.02, rely=0.5, anchor="w")
        ctk.CTkLabel(inner, text=title,
                     font=(Fonts.FAMILY, Fonts.SIZE_XL, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_WHITE).pack(anchor="w")
        ctk.CTkLabel(inner, text=subtitle,
                     font=(Fonts.FAMILY, Fonts.SIZE_XS),
                     text_color="#C8DFF0").pack(anchor="w")
        # School watermark
        ctk.CTkLabel(hdr, text="Dar-e-Arqam School  ·  Session 2026–27",
                     font=(Fonts.FAMILY, Fonts.SIZE_XS),
                     text_color="#A0C0D8").place(relx=0.98, rely=0.5, anchor="e")
        return hdr

    def _draw_student_report(self):
        self._report_header("📋  Student Report Card",
                             "Mid-Term Examination Results", Colors.PRIMARY)
        scroll = ctk.CTkScrollableFrame(self._preview, fg_color="transparent", corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=16, pady=12)

        # Selector
        sel_row = ctk.CTkFrame(scroll, fg_color="transparent")
        sel_row.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(sel_row, text="Student:",
                     font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_SECONDARY).pack(side="left", padx=(0, 6))

        student_options = [f"{s['name']} ({s['id']})" for s in self._state.students[:20]]

        self._rep_student_var = ctk.StringVar(value=student_options[0] if student_options else "")
        ctk.CTkOptionMenu(
            sel_row, values=student_options, variable=self._rep_student_var,
            width=260, height=32, font=(Fonts.FAMILY, Fonts.SIZE_SM),
            fg_color=Colors.BG_INPUT, button_color=Colors.PRIMARY,
            text_color=Colors.TEXT_PRIMARY,
            command=lambda _: self._refresh_student_report(scroll),
        ).pack(side="left")
        ctk.CTkButton(sel_row, text="Generate", height=32, width=90, corner_radius=8,
                      font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                      fg_color=Colors.PRIMARY, text_color=Colors.TEXT_WHITE,
                      command=lambda: self._refresh_student_report(scroll)
                      ).pack(side="left", padx=(8, 0))

        self._rc_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self._rc_frame.pack(fill="both", expand=True)
        self._refresh_student_report(scroll)

    def _refresh_student_report(self, scroll):
        for w in self._rc_frame.winfo_children():
            w.destroy()

        sel = self._rep_student_var.get()
        if not sel:
            return
        sid = sel.split("(")[-1].rstrip(")")
        student = next((s for s in self._state.students if s["id"] == sid), None)
        if not student:
            return

        # Info card
        info = ctk.CTkFrame(self._rc_frame, fg_color=Colors.PRIMARY,
                             corner_radius=8, height=60)
        info.pack(fill="x", pady=(0, 12))
        info.pack_propagate(False)
        il = ctk.CTkFrame(info, fg_color="transparent")
        il.place(relx=0.02, rely=0.5, anchor="w")
        ctk.CTkLabel(il, text=student["name"],
                     font=(Fonts.FAMILY, Fonts.SIZE_LG, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_WHITE).pack(anchor="w")
        ctk.CTkLabel(il, text=f"Class: {student['class']}  ·  Roll: {student['roll_no']}  ·  {student['gender']}",
                     font=(Fonts.FAMILY, Fonts.SIZE_XS),
                     text_color="#90CAF9").pack(anchor="w")

        # Marks table
        marks = [m for m in self._state.marks if m["student_id"] == sid]

        thead = ctk.CTkFrame(self._rc_frame, fg_color=Colors.BG_TABLE_HEAD,
                              corner_radius=0, height=34)
        thead.pack(fill="x")
        thead.pack_propagate(False)
        for w, lbl in [(200, "Subject"), (120, "Assessment"), (100, "Marks"), (80, "Grade")]:
            ctk.CTkLabel(thead, text=lbl, width=w,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                         text_color=Colors.TEXT_HEADING, anchor="w").pack(side="left", padx=(8,0))

        total_obt = 0
        total_max = 0
        for i, m in enumerate(marks):
            bg = Colors.BG_TABLE_ROW if i % 2 == 0 else Colors.BG_TABLE_ALT
            row = ctk.CTkFrame(self._rc_frame, fg_color=bg, height=36, corner_radius=0)
            row.pack(fill="x")
            row.pack_propagate(False)
            for w, val in [(200, m["subject"]), (120, m["assessment"]),
                            (100, f"{m['obtained']}/{m['total_marks']}")]:
                ctk.CTkLabel(row, text=val, width=w,
                             font=(Fonts.FAMILY, Fonts.SIZE_SM),
                             text_color=Colors.TEXT_PRIMARY, anchor="w").pack(side="left", padx=(8,0))
            StatusBadge(row, m["grade"]).pack(side="left", padx=(8,0), pady=6)
            total_obt += m.get("obtained", 0)
            total_max += m.get("total_marks", 0)

        # Summary
        if total_max:
            pct  = round((total_obt / total_max) * 100, 1)
            grade = "A+" if pct>=90 else "A" if pct>=80 else "B+" if pct>=70 else "B" if pct>=60 else "C" if pct>=50 else "F"
            sumrow = ctk.CTkFrame(self._rc_frame, fg_color=Colors.PRIMARY,
                                   corner_radius=8, height=44)
            sumrow.pack(fill="x", pady=(8, 0))
            sumrow.pack_propagate(False)
            ctk.CTkLabel(sumrow,
                         text=f"  Total: {total_obt}/{total_max}   ·   Overall: {pct}%   ·   Grade: {grade}",
                         font=(Fonts.FAMILY, Fonts.SIZE_MD, Fonts.WEIGHT_BOLD),
                         text_color=Colors.TEXT_WHITE).pack(side="left", padx=16)

    def _draw_attendance_report(self):
        self._report_header("✓  Class Attendance Report",
                             "Monthly attendance summary by class", Colors.SUCCESS)
        scroll = ctk.CTkScrollableFrame(self._preview, fg_color="transparent", corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=16, pady=12)

        # Class selector
        class_list = sorted({s["class"] for s in self._state.students})
        sel_row = ctk.CTkFrame(scroll, fg_color="transparent")
        sel_row.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(sel_row, text="Class:",
                     font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_SECONDARY).pack(side="left", padx=(0, 6))
        self._att_class_var = ctk.StringVar(value=class_list[0] if class_list else "")
        ctk.CTkOptionMenu(sel_row, values=class_list, variable=self._att_class_var,
                          width=160, height=32, font=(Fonts.FAMILY, Fonts.SIZE_SM),
                          fg_color=Colors.BG_INPUT, button_color=Colors.SUCCESS,
                          text_color=Colors.TEXT_PRIMARY,
                          command=lambda _: self._draw_att_table(scroll)).pack(side="left")

        self._att_table_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self._att_table_frame.pack(fill="both", expand=True)
        self._draw_att_table(scroll)

    def _draw_att_table(self, scroll):
        for w in self._att_table_frame.winfo_children():
            w.destroy()
        cls = self._att_class_var.get()
        if not cls:
            return
        students = self._state.get_students_by_class(cls)

        thead = ctk.CTkFrame(self._att_table_frame, fg_color=Colors.BG_TABLE_HEAD,
                              corner_radius=0, height=34)
        thead.pack(fill="x")
        thead.pack_propagate(False)
        for w, lbl in [(200,"Student"), (80,"Present"), (80,"Absent"), (80,"Late"), (100,"Att %"), (80,"Status")]:
            ctk.CTkLabel(thead, text=lbl, width=w,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                         text_color=Colors.TEXT_HEADING, anchor="w").pack(side="left", padx=(8,0))

        for i, s in enumerate(students):
            recs = [r for r in self._state.attendance if r["student_id"] == s["id"]]
            pres = sum(1 for r in recs if r["status"]=="Present")
            abst = sum(1 for r in recs if r["status"]=="Absent")
            late = sum(1 for r in recs if r["status"]=="Late")
            total = len(recs) or 1
            pct = round((pres/total)*100, 1)
            status = "Good" if pct>=90 else "Warning" if pct>=75 else "Critical"

            bg = Colors.DANGER_BG if pct < 75 else (
                Colors.BG_TABLE_ROW if i%2==0 else Colors.BG_TABLE_ALT)
            row = ctk.CTkFrame(self._att_table_frame, fg_color=bg, height=36, corner_radius=0)
            row.pack(fill="x")
            row.pack_propagate(False)
            for w, val in [(200,s["name"]), (80,str(pres)), (80,str(abst)), (80,str(late)),
                            (100, f"{pct}%")]:
                ctk.CTkLabel(row, text=val, width=w,
                             font=(Fonts.FAMILY, Fonts.SIZE_SM),
                             text_color=Colors.TEXT_PRIMARY, anchor="w").pack(side="left", padx=(8,0))
            s_color = Colors.SUCCESS if status=="Good" else Colors.WARNING if status=="Warning" else Colors.DANGER
            ctk.CTkLabel(row, text=status, width=80,
                         font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
                         text_color=s_color, anchor="w").pack(side="left", padx=(8,0))
            ctk.CTkFrame(self._att_table_frame, height=1, fg_color=Colors.DIVIDER).pack(fill="x")

    def _draw_low_att_report(self):
        self._report_header("⚠  Low Attendance Alert List",
                             "Students with attendance below 75%", Colors.DANGER)
        scroll = ctk.CTkScrollableFrame(self._preview, fg_color="transparent", corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=16, pady=12)

        # Find low-attendance students
        low_students = []
        for s in self._state.students:
            recs = [r for r in self._state.attendance if r["student_id"] == s["id"]]
            if recs:
                pres = sum(1 for r in recs if r["status"]=="Present")
                pct  = round((pres/len(recs))*100, 1)
                if pct < 75:
                    low_students.append((s, pct))
        low_students.sort(key=lambda x: x[1])

        ctk.CTkLabel(scroll, text=f"⚠  {len(low_students)} students require immediate attention",
                     font=(Fonts.FAMILY, Fonts.SIZE_MD, Fonts.WEIGHT_BOLD),
                     text_color=Colors.DANGER).pack(anchor="w", pady=(0, 12))

        if not low_students:
            ctk.CTkLabel(scroll, text="✓  All students have attendance above 75%",
                         font=(Fonts.FAMILY, Fonts.SIZE_MD),
                         text_color=Colors.SUCCESS).pack(pady=30)
            return

        thead = ctk.CTkFrame(scroll, fg_color=Colors.DANGER, corner_radius=0, height=34)
        thead.pack(fill="x")
        thead.pack_propagate(False)
        for w, lbl in [(200,"Student"), (120,"Class"), (100,"Att %"), (100,"Missing"), (80,"Alert")]:
            ctk.CTkLabel(thead, text=lbl, width=w,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                         text_color=Colors.TEXT_WHITE, anchor="w").pack(side="left", padx=(8,0))

        for i, (s, pct) in enumerate(low_students):
            recs  = [r for r in self._state.attendance if r["student_id"]==s["id"]]
            abst  = sum(1 for r in recs if r["status"]=="Absent")
            bg    = "#FFF0F0" if i%2==0 else "#FFE0E0"
            row   = ctk.CTkFrame(scroll, fg_color=bg, height=38, corner_radius=0)
            row.pack(fill="x")
            row.pack_propagate(False)
            for w, val in [(200,s["name"]), (120,s["class"]),
                            (100, f"{pct}%"), (100, f"{abst} days")]:
                ctk.CTkLabel(row, text=val, width=w,
                             font=(Fonts.FAMILY, Fonts.SIZE_SM),
                             text_color=Colors.DANGER if "pct" in str(val) else Colors.TEXT_PRIMARY,
                             anchor="w").pack(side="left", padx=(8,0))
            alert = "Critical" if pct < 60 else "Warning"
            ac = Colors.DANGER if alert=="Critical" else Colors.WARNING
            ctk.CTkLabel(row, text=alert, width=80,
                         font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
                         text_color=ac, anchor="w").pack(side="left", padx=(8,0))
            ctk.CTkFrame(scroll, height=1, fg_color=Colors.DANGER, corner_radius=0).pack(fill="x")

    def _draw_performance_report(self):
        self._report_header("📊  Performance Summary Report",
                             "Class-wise academic performance overview", Colors.INFO)
        scroll = ctk.CTkScrollableFrame(self._preview, fg_color="transparent", corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=16, pady=12)

        class_list = sorted({s["class"] for s in self._state.students})
        for cls in class_list:
            marks = [m for m in self._state.marks if m["class"] == cls]
            if not marks:
                continue
            scores = [(m["obtained"]/m["total_marks"])*100 for m in marks if m["total_marks"]]
            avg = round(sum(scores)/len(scores), 1) if scores else 0
            fail_count = sum(1 for s in scores if s < 50)

            avg_color = Colors.SUCCESS if avg >= 70 else Colors.WARNING if avg >= 50 else Colors.DANGER

            row = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=8,
                                border_width=1, border_color=Colors.BORDER, height=52)
            row.pack(fill="x", pady=(0, 6))
            row.pack_propagate(False)

            ctk.CTkLabel(row, text=f"  🏫 {cls}", width=160,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                         text_color=Colors.TEXT_HEADING, anchor="w").pack(side="left")

            # Progress bar
            bar_bg = ctk.CTkFrame(row, width=200, height=18,
                                   fg_color=Colors.BG_INPUT, corner_radius=9)
            bar_bg.pack(side="left", padx=(12, 0))
            bar_bg.pack_propagate(False)
            fill_w = max(4, int(200 * avg / 100))
            bar_fill = ctk.CTkFrame(bar_bg, width=fill_w, height=18,
                                     fg_color=avg_color, corner_radius=9)
            bar_fill.place(x=0, y=0)

            ctk.CTkLabel(row, text=f"{avg}% avg",
                         font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                         text_color=avg_color).pack(side="left", padx=(12, 0))
            ctk.CTkLabel(row, text=f"{fail_count} failed",
                         font=(Fonts.FAMILY, Fonts.SIZE_SM),
                         text_color=Colors.DANGER if fail_count else Colors.TEXT_MUTED,
                         ).pack(side="right", padx=16)


from app.components.cards import MetricCard