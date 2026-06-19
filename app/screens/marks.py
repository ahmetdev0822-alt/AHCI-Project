"""
app/screens/marks.py
Marks / Performance Entry Screen – Teacher & Admin.
"""

import customtkinter as ctk
from app.config import Colors, Fonts, Spacing, CARD_CORNER, ROLE_TEACHER
from app.components.cards import SectionHeader, StatusBadge
from app.data.sample_data import SUBJECTS, ASSESSMENT_TYPES


class MarksScreen(ctk.CTkFrame):
    def __init__(self, parent, state, navigate_fn, toast_fn):
        super().__init__(parent, fg_color=Colors.BG_MAIN, corner_radius=0)
        self._state    = state
        self._navigate = navigate_fn
        self._toast    = toast_fn
        self._mark_entries: dict[str, ctk.CTkEntry] = {}

        # Defaults
        role = self._state.current_role
        if role == ROLE_TEACHER:
            my_classes = self._state.get_classes_for_role()
            self._sel_class = my_classes[0] if my_classes else "Class 8-A"
        else:
            self._sel_class = "Class 8-A"

        subjects_for_class = SUBJECTS.get(self._sel_class, ["Mathematics"])
        self._sel_subject   = subjects_for_class[0]
        self._sel_assessment= ASSESSMENT_TYPES[0]
        self._total_marks   = ctk.StringVar(value="100")

        self._build()

    def _build(self):
        pad = Spacing.XL

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=pad, pady=(pad, Spacing.SM))
        SectionHeader(toolbar, "Performance & Marks",
                      "Enter marks for a class, subject, and assessment"
                      ).pack(side="left", fill="y")

        # ── Selector panel ────────────────────────────────────────────────────
        sel = ctk.CTkFrame(self, fg_color=Colors.BG_CARD, corner_radius=10,
                            border_width=1, border_color=Colors.BORDER)
        sel.pack(fill="x", padx=pad, pady=(0, Spacing.MD))
        sel_inner = ctk.CTkFrame(sel, fg_color="transparent")
        sel_inner.pack(fill="x", padx=Spacing.LG, pady=Spacing.MD)

        role = self._state.current_role
        class_list = (self._state.get_classes_for_role()
                      if role == ROLE_TEACHER
                      else sorted({s["class"] for s in self._state.students}))

        def make_selector(label_text, values, default):
            ctk.CTkLabel(sel_inner, text=label_text,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                         text_color=Colors.TEXT_SECONDARY).pack(side="left", padx=(0, 4))
            var = ctk.StringVar(value=default)
            menu = ctk.CTkOptionMenu(
                sel_inner, values=values, variable=var,
                width=150, height=34, font=(Fonts.FAMILY, Fonts.SIZE_SM),
                fg_color=Colors.BG_INPUT, button_color=Colors.PRIMARY,
                text_color=Colors.TEXT_PRIMARY,
                command=lambda _: self._reload(),
            )
            menu.pack(side="left", padx=(0, 20))
            return var

        self._class_var      = make_selector("Class:", class_list, self._sel_class)
        subject_list         = SUBJECTS.get(self._sel_class, ["Mathematics"])
        self._subject_var    = make_selector("Subject:", subject_list, self._sel_subject)
        self._assessment_var = make_selector("Assessment:", ASSESSMENT_TYPES, self._sel_assessment)

        # Total marks entry
        ctk.CTkLabel(sel_inner, text="Total Marks:",
                     font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_SECONDARY).pack(side="left", padx=(0, 4))
        ctk.CTkEntry(sel_inner, textvariable=self._total_marks,
                     width=70, height=34, corner_radius=8,
                     font=(Fonts.FAMILY, Fonts.SIZE_SM),
                     fg_color=Colors.BG_INPUT, border_color=Colors.BORDER,
                     text_color=Colors.TEXT_PRIMARY).pack(side="left", padx=(0, 20))

        ctk.CTkButton(sel_inner, text="💾  Save Marks",
                      height=34, width=130, corner_radius=8,
                      font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                      fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_DARK,
                      text_color=Colors.TEXT_WHITE,
                      command=self._save_marks).pack(side="right")

        # ── Live summary bar ──────────────────────────────────────────────────
        self._summary_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._summary_frame.pack(fill="x", padx=pad, pady=(0, Spacing.MD))
        self._avg_lbl   = self._make_chip(self._summary_frame, "Class Average", "—", Colors.PRIMARY)
        self._high_lbl  = self._make_chip(self._summary_frame, "Highest",       "—", Colors.SUCCESS)
        self._low_lbl   = self._make_chip(self._summary_frame, "Lowest",        "—", Colors.DANGER)
        self._fail_lbl  = self._make_chip(self._summary_frame, "Failed",        "—", Colors.WARNING)

        # ── Marks table ───────────────────────────────────────────────────────
        marks_panel = ctk.CTkFrame(self, fg_color=Colors.BG_CARD, corner_radius=10,
                                    border_width=1, border_color=Colors.BORDER)
        marks_panel.pack(fill="both", expand=True, padx=pad, pady=(0, pad))

        thead = ctk.CTkFrame(marks_panel, fg_color=Colors.BG_TABLE_HEAD,
                              corner_radius=0, height=38)
        thead.pack(fill="x")
        thead.pack_propagate(False)
        for w, lbl in [(50, "#"), (60, "Roll"), (220, "Student Name"),
                        (120, "Obtained Marks"), (80, "Grade"), (80, "% Score")]:
            ctk.CTkLabel(thead, text=lbl, width=w,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                         text_color=Colors.TEXT_HEADING, anchor="w").pack(side="left", padx=(8,0))

        self._marks_scroll = ctk.CTkScrollableFrame(marks_panel, fg_color="transparent",
                                                     corner_radius=0)
        self._marks_scroll.pack(fill="both", expand=True)
        self._marks_panel = marks_panel

        self._reload()

    @staticmethod
    def _make_chip(parent, label, val, color):
        chip = ctk.CTkFrame(parent, fg_color=MetricCard._alpha_color(color),
                             corner_radius=8, border_width=1, border_color=color, height=44)
        chip.pack(side="left", padx=(0, Spacing.SM))
        chip.pack_propagate(False)
        inner = ctk.CTkFrame(chip, fg_color="transparent")
        inner.pack(expand=True, padx=12)
        v_lbl = ctk.CTkLabel(inner, text=val,
                              font=(Fonts.FAMILY, Fonts.SIZE_LG, Fonts.WEIGHT_BOLD),
                              text_color=color)
        v_lbl.pack(side="left")
        ctk.CTkLabel(inner, text=f"  {label}",
                     font=(Fonts.FAMILY, Fonts.SIZE_XS),
                     text_color=color).pack(side="left")
        return v_lbl

    def _reload(self):
        self._sel_class      = self._class_var.get()
        self._sel_subject    = self._subject_var.get()
        self._sel_assessment = self._assessment_var.get()

        # Update subject list for class
        subjects = SUBJECTS.get(self._sel_class, ["Mathematics"])
        self._subject_var.set(subjects[0] if subjects else "Mathematics")
        self._sel_subject = self._subject_var.get()

        students = self._state.get_students_by_class(self._sel_class)

        # Existing marks
        existing = {
            m["student_id"]: m["obtained"]
            for m in self._state.marks
            if (m["class"] == self._sel_class
                and m["subject"] == self._sel_subject
                and m["assessment"] == self._sel_assessment)
        }

        for w in self._marks_scroll.winfo_children():
            w.destroy()
        self._mark_entries = {}

        if not students:
            ctk.CTkLabel(self._marks_scroll, text="No students in this class.",
                         font=(Fonts.FAMILY, Fonts.SIZE_MD),
                         text_color=Colors.TEXT_MUTED).pack(pady=30)
            return

        for i, student in enumerate(students):
            sid = student["id"]
            bg  = Colors.BG_TABLE_ROW if i % 2 == 0 else Colors.BG_TABLE_ALT
            row = ctk.CTkFrame(self._marks_scroll, fg_color=bg, height=44, corner_radius=0)
            row.pack(fill="x")
            row.pack_propagate(False)

            ctk.CTkLabel(row, text=str(i+1), width=50,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM),
                         text_color=Colors.TEXT_MUTED, anchor="w").pack(side="left", padx=(8,0))
            ctk.CTkLabel(row, text=student["roll_no"], width=60,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM),
                         text_color=Colors.TEXT_SECONDARY, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=student["name"], width=220,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM),
                         text_color=Colors.TEXT_PRIMARY, anchor="w").pack(side="left")

            # Marks entry
            entry_var = ctk.StringVar(value=str(existing.get(sid, "")))
            entry = ctk.CTkEntry(
                row, textvariable=entry_var,
                width=100, height=28, corner_radius=6,
                font=(Fonts.FAMILY, Fonts.SIZE_SM),
                fg_color=Colors.BG_INPUT, border_color=Colors.BORDER,
                text_color=Colors.TEXT_PRIMARY,
                placeholder_text="0–100",
            )
            entry.pack(side="left", padx=4)
            entry_var.trace_add("write", lambda *_, sv=entry_var: self._update_live(sv))
            self._mark_entries[sid] = entry_var

            # Grade / pct placeholders – updated live
            grade_lbl = ctk.CTkLabel(row, text="—", width=80,
                                      font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                                      text_color=Colors.TEXT_MUTED, anchor="w")
            grade_lbl.pack(side="left")
            pct_lbl = ctk.CTkLabel(row, text="—", width=80,
                                    font=(Fonts.FAMILY, Fonts.SIZE_SM),
                                    text_color=Colors.TEXT_MUTED, anchor="w")
            pct_lbl.pack(side="left")

            # Update grade/pct when entry changes
            def update_row_grade(sv=entry_var, gl=grade_lbl, pl=pct_lbl):
                try:
                    total = int(self._total_marks.get())
                    obt   = int(sv.get())
                    pct   = round((obt / total) * 100, 1) if total else 0
                    grade = self._grade(obt, total)
                    gc    = self._grade_color(grade)
                    gl.configure(text=grade, text_color=gc)
                    pl.configure(text=f"{pct}%", text_color=gc)
                except Exception:
                    gl.configure(text="—", text_color=Colors.TEXT_MUTED)
                    pl.configure(text="—", text_color=Colors.TEXT_MUTED)

            entry_var.trace_add("write", lambda *_, fn=update_row_grade: fn())
            update_row_grade()

            ctk.CTkFrame(self._marks_scroll, height=1, fg_color=Colors.DIVIDER).pack(fill="x")

        self._update_summary()

    def _update_live(self, sv):
        self._update_summary()

    def _update_summary(self):
        try:
            total = int(self._total_marks.get())
        except Exception:
            total = 100
        scores = []
        for sv in self._mark_entries.values():
            try:
                scores.append(int(sv.get()))
            except Exception:
                pass
        if not scores:
            for lbl in [self._avg_lbl, self._high_lbl, self._low_lbl, self._fail_lbl]:
                lbl.configure(text="—")
            return
        avg  = round(sum(scores) / len(scores), 1)
        high = max(scores)
        low  = min(scores)
        fail = sum(1 for s in scores if (s / total * 100) < 50 if total)
        self._avg_lbl.configure(text=f"{avg}")
        self._high_lbl.configure(text=str(high))
        self._low_lbl.configure(text=str(low))
        self._fail_lbl.configure(text=str(fail))

    def _save_marks(self):
        try:
            total = int(self._total_marks.get())
        except Exception:
            total = 100

        cls  = self._sel_class
        subj = self._sel_subject
        asmn = self._sel_assessment

        # Remove existing marks for this combination
        self._state.marks = [
            m for m in self._state.marks
            if not (m["class"] == cls and m["subject"] == subj and m["assessment"] == asmn)
        ]

        students = self._state.get_students_by_class(cls)
        for student in students:
            sid = student["id"]
            sv  = self._mark_entries.get(sid)
            if not sv:
                continue
            try:
                obtained = int(sv.get())
            except Exception:
                continue
            grade = self._grade(obtained, total)
            self._state.marks.append({
                "id":           f"MK{sid}{subj[:3]}{asmn[:3]}",
                "student_id":   sid,
                "student_name": student["name"],
                "class":        cls,
                "subject":      subj,
                "assessment":   asmn,
                "total_marks":  total,
                "obtained":     obtained,
                "grade":        grade,
            })

        self._toast(f"Marks saved for {cls} – {subj} – {asmn}!", "success")

    @staticmethod
    def _grade(obtained: int, total: int) -> str:
        pct = (obtained / total) * 100 if total else 0
        if pct >= 90: return "A+"
        if pct >= 80: return "A"
        if pct >= 70: return "B+"
        if pct >= 60: return "B"
        if pct >= 50: return "C"
        return "F"

    @staticmethod
    def _grade_color(grade: str) -> str:
        if grade in ("A+", "A"): return Colors.SUCCESS
        if grade in ("B+", "B"): return Colors.INFO
        if grade == "C":          return Colors.WARNING
        return Colors.DANGER


from app.components.cards import MetricCard
