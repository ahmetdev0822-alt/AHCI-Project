"""
app/screens/marks.py
Marks / Performance Screen – Blue & White theme + strict RBAC:
  - Admin:   VIEW ONLY – audit scores, grade analytics
  - Teacher: EDIT – enter marks with accessible validation
  - Parent:  CHILD GRADEBOOK – child report card & subject marks
Addresses CS3014 Section 4 (Accessible validation) and Section 10 (Multi-state views).
"""

import customtkinter as ctk
from app.config import (
    Colors, Fonts, Spacing, CARD_CORNER,
    ROLE_ADMIN, ROLE_TEACHER, ROLE_PARENT,
)
from app.components.cards import SectionHeader, StatusBadge, MetricCard
from app.components.state_view import StateView, StateSwitchDemoBar
from app.data.sample_data import SUBJECTS, ASSESSMENT_TYPES


class MarksScreen(ctk.CTkFrame):
    def __init__(self, parent, state, navigate_fn, toast_fn):
        super().__init__(parent, fg_color=Colors.BG_MAIN, corner_radius=0)
        self._state    = state
        self._navigate = navigate_fn
        self._toast    = toast_fn
        self._mark_entries: dict[str, ctk.StringVar] = {}
        self._grade_lbls:   dict[str, ctk.CTkLabel]  = {}
        self._pct_lbls:     dict[str, ctk.CTkLabel]  = {}

        role = self._state.current_role
        self._editable = (role == ROLE_TEACHER)

        if role == ROLE_TEACHER:
            my_classes = self._state.get_classes_for_role()
            self._sel_class = my_classes[0] if my_classes else "Class 8-A"
        elif role == ROLE_PARENT:
            child = self._state.get_linked_child()
            self._sel_class = child.get("class", "Class 8-A") if child else "Class 8-A"
        else:
            all_classes = sorted({s["class"] for s in self._state.students})
            self._sel_class = all_classes[0] if all_classes else "Class 8-A"

        subjects_for_class  = SUBJECTS.get(self._sel_class, ["Mathematics"])
        self._sel_subject   = subjects_for_class[0]
        self._sel_assessment= ASSESSMENT_TYPES[0]
        self._total_marks   = ctk.StringVar(value="100")

        self._build()

    def _build(self):
        pad  = Spacing.XL
        role = self._state.current_role

        # Top Bar
        top_row = ctk.CTkFrame(self, fg_color="transparent")
        top_row.pack(fill="x", padx=pad, pady=(pad, 0))
        SectionHeader(top_row, "Performance & Marks Registry", "Examination scores, grading curves, and term report cards").pack(side="left", fill="y")
        StateSwitchDemoBar(top_row, on_switch_fn=self._on_state_switch).pack(side="right")

        # Read-Only Banner (Admin)
        if not self._editable and role == ROLE_ADMIN:
            banner = ctk.CTkFrame(self, fg_color=Colors.INFO_BG, corner_radius=8, border_width=1, border_color=Colors.INFO)
            banner.pack(fill="x", padx=pad, pady=(Spacing.SM, 0))
            ctk.CTkLabel(banner, text="🔒  Administrator View  –  Audit and export examination marks. Score entry is reserved for assigned subject teachers.", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.INFO).pack(padx=16, pady=6)

        # ── Selector Panel ────────────────────────────────────────────────────
        sel = ctk.CTkFrame(self, fg_color=Colors.BG_CARD, corner_radius=10, border_width=1, border_color=Colors.BORDER)
        sel.pack(fill="x", padx=pad, pady=(Spacing.SM, Spacing.MD))
        sel_inner = ctk.CTkFrame(sel, fg_color="transparent")
        sel_inner.pack(fill="x", padx=Spacing.LG, pady=Spacing.MD)

        if role == ROLE_PARENT:
            child = self._state.get_linked_child()
            cname = child.get("name", "Student") if child else "Fatima Bibi"
            ctk.CTkLabel(sel_inner, text=f"Gradebook Report Card: {cname} ({self._sel_class})", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.PRIMARY).pack(side="left")
            self._assessment_var = ctk.StringVar(value="Mid-Term")
            ctk.CTkOptionMenu(
                sel_inner, values=["Monthly Test", "Mid-Term", "Final Exam"], variable=self._assessment_var,
                width=160, height=34, font=(Fonts.FAMILY, Fonts.SIZE_SM), fg_color=Colors.BG_INPUT, button_color=Colors.PRIMARY, text_color=Colors.TEXT_PRIMARY,
                command=lambda _: self._reload_parent_view(),
            ).pack(side="right")
        else:
            class_list = self._state.get_classes_for_role() if role == ROLE_TEACHER else sorted({s["class"] for s in self._state.students})

            def make_selector(label_text, values, default):
                ctk.CTkLabel(sel_inner, text=label_text, font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_SECONDARY).pack(side="left", padx=(0, 4))
                var = ctk.StringVar(value=default)
                menu = ctk.CTkOptionMenu(
                    sel_inner, values=values, variable=var,
                    width=140, height=34, font=(Fonts.FAMILY, Fonts.SIZE_SM),
                    fg_color=Colors.BG_INPUT, button_color=Colors.PRIMARY, text_color=Colors.TEXT_PRIMARY,
                    command=lambda _: self._reload(),
                )
                menu.pack(side="left", padx=(0, 16))
                return var

            self._class_var      = make_selector("Class:", class_list, self._sel_class)
            subject_list         = SUBJECTS.get(self._sel_class, ["Mathematics"])
            self._subject_var    = make_selector("Subject:", subject_list, self._sel_subject)
            self._assessment_var = make_selector("Exam:", ASSESSMENT_TYPES, self._sel_assessment)

            if self._editable:
                ctk.CTkLabel(sel_inner, text="Total:", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_SECONDARY).pack(side="left", padx=(0, 4))
                ctk.CTkEntry(sel_inner, textvariable=self._total_marks, width=60, height=34, corner_radius=8, font=(Fonts.FAMILY, Fonts.SIZE_SM), fg_color=Colors.BG_INPUT, border_color=Colors.BORDER, text_color=Colors.TEXT_PRIMARY).pack(side="left", padx=(0, 16))
                ctk.CTkButton(
                    sel_inner, text="💾  Save Marks", height=34, width=130, corner_radius=8,
                    font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                    fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_DARK, text_color=Colors.TEXT_WHITE,
                    command=self._save_marks,
                ).pack(side="right")
            else:
                ctk.CTkButton(
                    sel_inner, text="🖨  Print Sheet", height=34, width=120, corner_radius=8,
                    font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                    fg_color=Colors.INFO_BG, text_color=Colors.INFO,
                    command=lambda: self._toast("Marks ledger sent to printer!", "info"),
                ).pack(side="right")

        # ── StateView Container ───────────────────────────────────────────────
        self._state_view = StateView(
            self,
            on_retry=lambda: self._on_state_switch("content"),
            on_action=lambda: self._navigate("dashboard"),
        )
        self._state_view.pack(fill="both", expand=True)

        if role == ROLE_PARENT:
            self._render_parent_gradebook(self._state_view.content_area)
        else:
            self._render_teacher_table(self._state_view.content_area)

    def _on_state_switch(self, mode: str):
        if mode == "content":
            self._state_view.set_state("content")
        elif mode == "empty":
            self._state_view.set_state("empty", title="No Marks Ledger Created", message="No examination scores recorded yet for this subject and assessment.", action_text="Create Gradebook")
        elif mode == "loading":
            self._state_view.set_state("loading", title="Computing Grade Curves...", message="Calculating class averages, standard deviations, and letter grades from SQLite.")
        elif mode == "error":
            self._state_view.set_state("error", title="Grade Calculation Error", message="Score entry contains out-of-range numerical values (> Total Marks).", error_details="ERR_SCORE_OVERFLOW_VALIDATION (Row 4)")
        elif mode == "offline":
            self._state_view.set_state("offline", title="Offline Grade Entry", message="Marks are saved directly to the local encrypted SQLite database.", action_text="Continue Grading")

    def _render_teacher_table(self, parent):
        pad = Spacing.XL

        # Summary Chips
        self._summary_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self._summary_frame.pack(fill="x", padx=pad, pady=(0, Spacing.MD))
        self._avg_lbl  = self._make_chip(self._summary_frame, "Class Average", "—", Colors.PRIMARY)
        self._high_lbl = self._make_chip(self._summary_frame, "Highest",       "—", Colors.SUCCESS)
        self._low_lbl  = self._make_chip(self._summary_frame, "Lowest",        "—", Colors.DANGER)
        self._fail_lbl = self._make_chip(self._summary_frame, "Failed (<50%)", "—", Colors.WARNING)

        # Marks Table
        marks_panel = ctk.CTkFrame(parent, fg_color=Colors.BG_CARD, corner_radius=10, border_width=1, border_color=Colors.BORDER)
        marks_panel.pack(fill="both", expand=True, padx=pad, pady=(0, pad))

        thead = ctk.CTkFrame(marks_panel, fg_color=Colors.BG_TABLE_HEAD, corner_radius=0, height=36)
        thead.pack(fill="x")
        thead.pack_propagate(False)

        cols = [(50, " #"), (70, "Roll"), (240, "Student Name"), (160, "Marks Obtained"), (100, "Grade"), (100, "% Score")]
        for w, lbl in cols:
            ctk.CTkLabel(thead, text=lbl, width=w, font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_HEADING, anchor="w").pack(side="left", padx=4)

        self._marks_scroll = ctk.CTkScrollableFrame(marks_panel, fg_color="transparent", corner_radius=0)
        self._marks_scroll.pack(fill="both", expand=True)
        self._populate_teacher_rows()

    def _render_parent_gradebook(self, parent):
        pad = Spacing.XL
        child = self._state.get_linked_child() or {"id": "S003", "name": "Fatima Bibi Chaudhry", "class": "Class 8-A"}

        # Marks Table
        panel = ctk.CTkFrame(parent, fg_color=Colors.BG_CARD, corner_radius=10, border_width=1, border_color=Colors.BORDER)
        panel.pack(fill="both", expand=True, padx=pad, pady=(0, pad))

        thead = ctk.CTkFrame(panel, fg_color=Colors.BG_TABLE_HEAD, corner_radius=0, height=36)
        thead.pack(fill="x")
        thead.pack_propagate(False)

        cols = [("Subject", 200), ("Assessment", 140), ("Max Marks", 100), ("Obtained", 100), ("Percentage", 120), ("Grade", 90), ("Remarks", 200)]
        for label, w in cols:
            ctk.CTkLabel(thead, text=label, width=w, font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_HEADING, anchor="w").pack(side="left", padx=10)

        scroll = ctk.CTkScrollableFrame(panel, fg_color="transparent", corner_radius=0)
        scroll.pack(fill="both", expand=True)

        child_marks = [m for m in self._state.marks if m["student_id"] == child["id"]]
        if not child_marks:
            # Fallback sample
            child_marks = [
                {"subject": "Mathematics", "assessment": "Mid-Term", "total_marks": 100, "obtained": 92, "grade": "A+"},
                {"subject": "Physics", "assessment": "Mid-Term", "total_marks": 100, "obtained": 88, "grade": "A"},
                {"subject": "Urdu", "assessment": "Mid-Term", "total_marks": 100, "obtained": 90, "grade": "A+"},
                {"subject": "English", "assessment": "Mid-Term", "total_marks": 100, "obtained": 82, "grade": "A"},
                {"subject": "Chemistry", "assessment": "Mid-Term", "total_marks": 100, "obtained": 79, "grade": "B+"},
                {"subject": "Islamic Studies", "assessment": "Mid-Term", "total_marks": 100, "obtained": 95, "grade": "A+"},
            ]

        for idx, m in enumerate(child_marks):
            rf = ctk.CTkFrame(scroll, fg_color=Colors.BG_TABLE_ROW if idx % 2 == 0 else Colors.BG_TABLE_ALT, height=40)
            rf.pack(fill="x")
            rf.pack_propagate(False)

            pct = round((m["obtained"] / m["total_marks"]) * 100, 1)
            ctk.CTkLabel(rf, text=m["subject"], width=200, font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_PRIMARY, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(rf, text=m["assessment"], width=140, font=(Fonts.FAMILY, Fonts.SIZE_SM), text_color=Colors.TEXT_MUTED, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(rf, text=str(m["total_marks"]), width=100, font=(Fonts.FAMILY_MONO, Fonts.SIZE_SM), text_color=Colors.TEXT_SECONDARY, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(rf, text=str(m["obtained"]), width=100, font=(Fonts.FAMILY_MONO, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.PRIMARY, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(rf, text=f"{pct}%", width=120, font=(Fonts.FAMILY_MONO, Fonts.SIZE_SM), text_color=Colors.SUCCESS if pct >= 80 else Colors.TEXT_PRIMARY, anchor="w").pack(side="left", padx=10)
            StatusBadge(rf, m.get("grade", "A")).pack(side="left", padx=10)
            ctk.CTkLabel(rf, text="Distinction Achieved" if pct>=90 else "Good Standing", width=200, font=(Fonts.FAMILY, Fonts.SIZE_XS), text_color=Colors.TEXT_MUTED, anchor="w").pack(side="left", padx=10)

    def _populate_teacher_rows(self):
        for w in self._marks_scroll.winfo_children():
            w.destroy()
        self._mark_entries.clear()
        self._grade_lbls.clear()
        self._pct_lbls.clear()

        students = [s for s in self._state.students if s["class"] == self._sel_class]
        subj = self._sel_subject
        assess = self._sel_assessment

        for idx, s in enumerate(students):
            sid = s["id"]
            rec = next((m for m in self._state.marks if m["student_id"] == sid and m["subject"] == subj and m["assessment"] == assess), None)
            init_obt = str(rec["obtained"]) if rec else "75"

            rf = ctk.CTkFrame(self._marks_scroll, fg_color=Colors.BG_TABLE_ROW if idx % 2 == 0 else Colors.BG_TABLE_ALT, height=40)
            rf.pack(fill="x")
            rf.pack_propagate(False)

            ctk.CTkLabel(rf, text=str(idx + 1), width=50, font=(Fonts.FAMILY, Fonts.SIZE_SM), text_color=Colors.TEXT_MUTED, anchor="w").pack(side="left", padx=4)
            ctk.CTkLabel(rf, text=s.get("roll_no", "-"), width=70, font=(Fonts.FAMILY_MONO, Fonts.SIZE_SM), text_color=Colors.TEXT_PRIMARY, anchor="w").pack(side="left", padx=4)
            ctk.CTkLabel(rf, text=s["name"], width=240, font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_PRIMARY, anchor="w").pack(side="left", padx=4)

            entry_f = ctk.CTkFrame(rf, width=160, fg_color="transparent")
            entry_f.pack(side="left", padx=4)

            var = ctk.StringVar(value=init_obt)
            self._mark_entries[sid] = var

            if self._editable:
                ent = ctk.CTkEntry(entry_f, textvariable=var, width=80, height=28, corner_radius=6, font=(Fonts.FAMILY_MONO, Fonts.SIZE_SM), fg_color=Colors.BG_INPUT, border_color=Colors.BORDER, text_color=Colors.TEXT_PRIMARY)
                ent.pack(side="left")
                var.trace_add("write", lambda *_, sid=sid: self._on_mark_changed(sid))
            else:
                ctk.CTkLabel(entry_f, text=init_obt, width=80, font=(Fonts.FAMILY_MONO, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.PRIMARY, anchor="w").pack(side="left")

            glbl = StatusBadge(rf, rec["grade"] if rec else "B")
            glbl.pack(side="left", padx=10)
            self._grade_lbls[sid] = glbl

            plbl = ctk.CTkLabel(rf, text="75.0%", width=100, font=(Fonts.FAMILY_MONO, Fonts.SIZE_SM), text_color=Colors.TEXT_SECONDARY, anchor="w")
            plbl.pack(side="left", padx=4)
            self._pct_lbls[sid] = plbl

            self._on_mark_changed(sid)

        self._update_analytics()

    def _on_mark_changed(self, sid: str):
        var = self._mark_entries.get(sid)
        if not var:
            return
        val_str = var.get().strip()
        try:
            tot = float(self._total_marks.get())
            obt = float(val_str)
            if obt < 0 or obt > tot:
                raise ValueError("Out of bounds")
            pct = round((obt / tot) * 100, 1)
            grd = "A+" if pct >= 90 else ("A" if pct >= 80 else ("B+" if pct >= 70 else ("B" if pct >= 60 else ("C" if pct >= 50 else "F"))))
            if sid in self._grade_lbls:
                self._grade_lbls[sid].configure(text=f"  {grd}  ")
            if sid in self._pct_lbls:
                self._pct_lbls[sid].configure(text=f"{pct}%")
        except Exception:
            if sid in self._pct_lbls:
                self._pct_lbls[sid].configure(text="⚠ Invalid")

    def _update_analytics(self):
        vals = []
        for var in self._mark_entries.values():
            try:
                vals.append(float(var.get().strip()))
            except Exception:
                pass
        if vals:
            avg = round(sum(vals) / len(vals), 1)
            high = round(max(vals), 1)
            low = round(min(vals), 1)
            fail = sum(1 for v in vals if v < 50)
            self._avg_lbl.configure(text=str(avg))
            self._high_lbl.configure(text=str(high))
            self._low_lbl.configure(text=str(low))
            self._fail_lbl.configure(text=str(fail))

    def _save_marks(self):
        students = [s for s in self._state.students if s["class"] == self._sel_class]
        if not students:
            self._toast("No students found in selected class.", "warning")
            return

        subj = self._sel_subject
        assess = self._sel_assessment
        try:
            tot = int(float(self._total_marks.get().strip()))
            if tot <= 0:
                raise ValueError("Total marks must be > 0")
        except Exception:
            self._toast("Validation Error: Total marks must be a positive number.", "error")
            return

        records = []
        invalid_entries = []

        for s in students:
            sid = s["id"]
            raw_val = self._mark_entries.get(sid, ctk.StringVar(value="0")).get().strip()
            try:
                obt = int(float(raw_val))
                if obt < 0 or obt > tot:
                    invalid_entries.append(f"{s['name']} ({obt}/{tot})")
            except Exception:
                invalid_entries.append(f"{s['name']} (invalid score)")
                obt = 0

            pct = (obt / tot) * 100 if tot > 0 else 0
            grd = "A+" if pct >= 90 else ("A" if pct >= 80 else ("B+" if pct >= 70 else ("B" if pct >= 60 else ("C" if pct >= 50 else "F"))))
            records.append({
                "id": f"MK{sid}{subj[:3]}",
                "student_id": sid,
                "student_name": s["name"],
                "class": self._sel_class,
                "subject": subj,
                "assessment": assess,
                "total_marks": tot,
                "obtained": obt,
                "grade": grd,
            })

        if invalid_entries:
            self._toast(f"Validation Error: Score out of bounds for {invalid_entries[0]}.", "error")
            return

        ok = self._state.save_marks_batch(records)
        if ok:
            self._toast(f"Marks for {self._sel_class} - {subj} ({assess}) saved to SQLite!", "success")
        else:
            self._toast("Failed to save marks to database.", "error")

    def _reload(self):
        self._sel_class = self._class_var.get()
        self._sel_subject = self._subject_var.get()
        self._sel_assessment = self._assessment_var.get()
        self._populate_teacher_rows()

    def _reload_parent_view(self):
        for w in self._state_view.content_area.winfo_children():
            w.destroy()
        self._render_parent_gradebook(self._state_view.content_area)

    @staticmethod
    def _make_chip(parent, label, val, color):
        from app.components.cards import MetricCard
        chip = ctk.CTkFrame(parent, fg_color=MetricCard._alpha_color(color), corner_radius=8, border_width=1, border_color=color, height=44)
        chip.pack(side="left", padx=(0, Spacing.SM))
        chip.pack_propagate(False)
        inner = ctk.CTkFrame(chip, fg_color="transparent")
        inner.pack(expand=True, padx=12)
        v_lbl = ctk.CTkLabel(inner, text=val, font=(Fonts.FAMILY, Fonts.SIZE_LG, Fonts.WEIGHT_BOLD), text_color=color)
        v_lbl.pack(side="left")
        ctk.CTkLabel(inner, text=f"  {label}", font=(Fonts.FAMILY, Fonts.SIZE_XS), text_color=color).pack(side="left")
        return v_lbl