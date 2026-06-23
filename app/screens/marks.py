"""
app/screens/marks.py
Marks / Performance Screen – Blue & White theme + strict RBAC:
  - Admin:   VIEW ONLY – read-only labels, no Save button
  - Teacher: EDIT – enter marks for their assigned classes only
  - Student: VIEW ONLY – sees only their own marks
"""

import customtkinter as ctk
from app.config import (
    Colors, Fonts, Spacing, CARD_CORNER,
    ROLE_ADMIN, ROLE_TEACHER, ROLE_STUDENT,
)
from app.components.cards import SectionHeader, StatusBadge
from app.data.sample_data import SUBJECTS, ASSESSMENT_TYPES


class MarksScreen(ctk.CTkFrame):
    def __init__(self, parent, state, navigate_fn, toast_fn):
        super().__init__(parent, fg_color=Colors.BG_MAIN, corner_radius=0)
        self._state    = state
        self._navigate = navigate_fn
        self._toast    = toast_fn
        self._mark_entries: dict[str, ctk.StringVar] = {}

        role = self._state.current_role
        self._editable = (role == ROLE_TEACHER)
        self._is_student = (role == ROLE_STUDENT)

        if role == ROLE_TEACHER:
            my_classes = self._state.get_classes_for_role()
            self._sel_class = my_classes[0] if my_classes else "Class 8-A"
        elif role == ROLE_STUDENT:
            self._sel_class = self._state.current_user.get("class", "Class 8-A")
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

        # ── Read-Only Banner ──────────────────────────────────────────────────
        if not self._editable:
            if role == ROLE_ADMIN:
                banner_text  = "🔒  Administrator View  –  You can view and print marks, but cannot enter or edit them."
                banner_color = Colors.INFO_BG
                border_color = Colors.INFO
                text_color   = Colors.INFO
            else:
                banner_text  = f"👁  Viewing your own marks for {self._sel_class}  –  Read Only."
                banner_color = Colors.PRIMARY_LIGHT
                border_color = Colors.PRIMARY
                text_color   = Colors.PRIMARY

            banner = ctk.CTkFrame(self, fg_color=banner_color, corner_radius=8,
                                   border_width=1, border_color=border_color)
            banner.pack(fill="x", padx=pad, pady=(pad, 0))
            ctk.CTkLabel(banner, text=banner_text,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                         text_color=text_color).pack(padx=16, pady=8)

        # ── Toolbar ───────────────────────────────────────────────────────────
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=pad,
                     pady=(Spacing.MD if not self._editable else pad, Spacing.SM))
        SectionHeader(toolbar, "Marks & Performance",
                      "View or enter exam marks by class, subject, and assessment"
                      ).pack(side="left", fill="y")

        # ── Selector Panel ────────────────────────────────────────────────────
        sel = ctk.CTkFrame(self, fg_color=Colors.BG_CARD, corner_radius=10,
                            border_width=1, border_color=Colors.BORDER)
        sel.pack(fill="x", padx=pad, pady=(0, Spacing.MD))
        sel_inner = ctk.CTkFrame(sel, fg_color="transparent")
        sel_inner.pack(fill="x", padx=Spacing.LG, pady=Spacing.MD)

        if role == ROLE_TEACHER:
            class_list = self._state.get_classes_for_role()
        elif role == ROLE_STUDENT:
            class_list = [self._sel_class]
        else:
            class_list = sorted({s["class"] for s in self._state.students})

        def make_selector(label_text, values, default, disabled=False):
            ctk.CTkLabel(sel_inner, text=label_text,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                         text_color=Colors.TEXT_SECONDARY).pack(side="left", padx=(0, 4))
            var = ctk.StringVar(value=default)
            menu = ctk.CTkOptionMenu(
                sel_inner, values=values, variable=var,
                width=148, height=34, font=(Fonts.FAMILY, Fonts.SIZE_SM),
                fg_color=Colors.BG_INPUT, button_color=Colors.PRIMARY,
                text_color=Colors.TEXT_PRIMARY,
                command=lambda _: self._reload(),
            )
            menu.pack(side="left", padx=(0, 20))
            if disabled:
                menu.configure(state="disabled")
            return var

        self._class_var      = make_selector("Class:",      class_list,     self._sel_class,
                                             disabled=self._is_student)
        subject_list         = SUBJECTS.get(self._sel_class, ["Mathematics"])
        self._subject_var    = make_selector("Subject:",    subject_list,   self._sel_subject)
        self._assessment_var = make_selector("Assessment:", ASSESSMENT_TYPES, self._sel_assessment)

        # Total marks (only for teachers)
        if self._editable:
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
        else:
            ctk.CTkButton(sel_inner, text="🖨  Print Marks",
                          height=34, width=130, corner_radius=8,
                          font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                          fg_color=Colors.INFO_BG, text_color=Colors.INFO,
                          hover_color=Colors.INFO,
                          command=lambda: self._toast("Marks report sent to printer!", "info")
                          ).pack(side="right")

        # ── Summary chips ─────────────────────────────────────────────────────
        self._summary_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._summary_frame.pack(fill="x", padx=pad, pady=(0, Spacing.MD))
        self._avg_lbl  = self._make_chip(self._summary_frame, "Class Average", "—", Colors.PRIMARY)
        self._high_lbl = self._make_chip(self._summary_frame, "Highest",       "—", Colors.SUCCESS)
        self._low_lbl  = self._make_chip(self._summary_frame, "Lowest",        "—", Colors.DANGER)
        self._fail_lbl = self._make_chip(self._summary_frame, "Failed",        "—", Colors.WARNING)

        # ── Marks Table ───────────────────────────────────────────────────────
        marks_panel = ctk.CTkFrame(self, fg_color=Colors.BG_CARD, corner_radius=10,
                                    border_width=1, border_color=Colors.BORDER)
        marks_panel.pack(fill="both", expand=True, padx=pad, pady=(0, pad))

        thead = ctk.CTkFrame(marks_panel, fg_color=Colors.BG_TABLE_HEAD,
                              corner_radius=0, height=36)
        thead.pack(fill="x")
        thead.pack_propagate(False)
        if self._editable:
            cols = [(40, "#"), (60, "Roll"), (220, "Student Name"), (120, "Obtained Marks"), (80, "Grade"), (80, "% Score")]
        else:
            cols = [(40, "#"), (60, "Roll"), (220, "Student Name"), (120, "Marks Obtained"), (80, "Grade"), (80, "% Score")]
        for w, lbl in cols:
            ctk.CTkLabel(thead, text=lbl, width=w,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                         text_color=Colors.TEXT_HEADING, anchor="w").pack(side="left", padx=(8, 0))

        self._marks_scroll = ctk.CTkScrollableFrame(marks_panel, fg_color="transparent",
                                                     corner_radius=0)
        self._marks_scroll.pack(fill="both", expand=True)
        self._reload()

    @staticmethod
    def _make_chip(parent, label, val, color):
        from app.components.cards import MetricCard
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

        # Update subject list
        subjects = SUBJECTS.get(self._sel_class, ["Mathematics"])
        self._subject_var.set(subjects[0] if subjects else "Mathematics")
        self._sel_subject = self._subject_var.get()

        # For students: only their own row
        if self._is_student:
            sid = self._state.current_user.get("student_id", "S001")
            students = [s for s in self._state.students if s["id"] == sid]
        else:
            students = self._state.get_students_by_class(self._sel_class)

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
            ctk.CTkLabel(self._marks_scroll, text="No students found.",
                         font=(Fonts.FAMILY, Fonts.SIZE_MD),
                         text_color=Colors.TEXT_MUTED).pack(pady=30)
            return

        for i, student in enumerate(students):
            sid = student["id"]
            bg  = Colors.BG_TABLE_ROW if i % 2 == 0 else Colors.BG_TABLE_ALT
            row = ctk.CTkFrame(self._marks_scroll, fg_color=bg, height=44, corner_radius=0)
            row.pack(fill="x")
            row.pack_propagate(False)

            ctk.CTkLabel(row, text=str(i + 1), width=40,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM),
                         text_color=Colors.TEXT_MUTED, anchor="w").pack(side="left", padx=(8, 0))
            ctk.CTkLabel(row, text=student["roll_no"], width=60,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM),
                         text_color=Colors.TEXT_SECONDARY, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=student["name"], width=220,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM),
                         text_color=Colors.TEXT_PRIMARY, anchor="w").pack(side="left")

            entry_var = ctk.StringVar(value=str(existing.get(sid, "")))
            self._mark_entries[sid] = entry_var

            if self._editable:
                # Editable entry (Teacher)
                entry = ctk.CTkEntry(
                    row, textvariable=entry_var,
                    width=100, height=28, corner_radius=6,
                    font=(Fonts.FAMILY, Fonts.SIZE_SM),
                    fg_color=Colors.BG_INPUT, border_color=Colors.BORDER,
                    text_color=Colors.TEXT_PRIMARY,
                    placeholder_text="0–100",
                )
                entry.pack(side="left", padx=4)
            else:
                # Read-only label (Admin / Student)
                score_text = str(existing.get(sid, "—"))
                try:
                    total = int(self._total_marks.get())
                    obt   = int(score_text)
                    score_display = f"{obt}/{total}"
                except Exception:
                    score_display = score_text if score_text else "—"
                ctk.CTkLabel(row, text=score_display, width=100,
                             font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                             text_color=Colors.TEXT_PRIMARY, anchor="w").pack(side="left", padx=4)

            # Grade / pct – live or static
            grade_lbl = ctk.CTkLabel(row, text="—", width=80,
                                      font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                                      text_color=Colors.TEXT_MUTED, anchor="w")
            grade_lbl.pack(side="left")
            pct_lbl = ctk.CTkLabel(row, text="—", width=80,
                                    font=(Fonts.FAMILY, Fonts.SIZE_SM),
                                    text_color=Colors.TEXT_MUTED, anchor="w")
            pct_lbl.pack(side="left")

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
        self._avg_lbl.configure(text=str(avg))
        self._high_lbl.configure(text=str(high))
        self._low_lbl.configure(text=str(low))
        self._fail_lbl.configure(text=str(fail))

    def _save_marks(self):
        if not self._editable:
            self._toast("Access denied. Admins cannot edit marks.", "error")
            return
        try:
            total = int(self._total_marks.get())
        except Exception:
            total = 100

        cls  = self._sel_class
        subj = self._sel_subject
        asmn = self._sel_assessment

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

        self._toast(f"✓  Marks saved – {cls}  ·  {subj}  ·  {asmn}", "success")
        self._update_summary()

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
