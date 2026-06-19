"""
app/screens/attendance.py
Fast bulk attendance marking screen – Teacher & Admin.
Most important screen in EduTrack. Designed for speed.
"""

import customtkinter as ctk
from datetime import date
from app.config import (
    Colors, Fonts, Spacing, CARD_CORNER,
    ROLE_ADMIN, ROLE_TEACHER,
)
from app.components.cards import SectionHeader, StatusBadge, MetricCard


class AttendanceScreen(ctk.CTkFrame):
    """
    Bulk attendance marking interface.
    Features:
      - Class + date selector
      - One-click per-student Present/Absent/Late/Leave
      - Real-time attendance percentage counter
      - Low-attendance students highlighted in red
      - Save all in one click
    """

    STATUSES    = ["Present", "Absent", "Late", "Leave"]
    STATUS_COLORS = {
        "Present": Colors.SUCCESS,
        "Absent":  Colors.DANGER,
        "Late":    Colors.WARNING,
        "Leave":   Colors.INFO,
    }
    STATUS_BG = {
        "Present": Colors.SUCCESS_BG,
        "Absent":  Colors.DANGER_BG,
        "Late":    Colors.WARNING_BG,
        "Leave":   Colors.INFO_BG,
    }

    def __init__(self, parent, state, navigate_fn, toast_fn):
        super().__init__(parent, fg_color=Colors.BG_MAIN, corner_radius=0)
        self._state      = state
        self._navigate   = navigate_fn
        self._toast      = toast_fn
        self._row_vars: dict[str, ctk.StringVar] = {}   # student_id -> status var
        self._selected_date = date.today().isoformat()

        # Determine default class
        role = self._state.current_role
        if role == ROLE_TEACHER:
            my_classes = self._state.get_classes_for_role()
            self._selected_class = my_classes[0] if my_classes else "Class 8-A"
        else:
            self._selected_class = "Class 8-A"

        self._build()

    def _build(self):
        pad = Spacing.XL

        # ── Top toolbar ───────────────────────────────────────────────────────
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=pad, pady=(pad, Spacing.SM))
        SectionHeader(toolbar, "Attendance Marking",
                      "Select class and mark attendance quickly"
                      ).pack(side="left", fill="y")

        # Bulk action buttons (right)
        ctk.CTkButton(
            toolbar, text="✓  All Present",
            height=34, corner_radius=8, width=110,
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            fg_color=Colors.SUCCESS_BG, text_color=Colors.SUCCESS,
            hover_color=Colors.SUCCESS,
            command=lambda: self._bulk_set("Present"),
        ).pack(side="right", padx=(4, 0))
        ctk.CTkButton(
            toolbar, text="✕  All Absent",
            height=34, corner_radius=8, width=110,
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            fg_color=Colors.DANGER_BG, text_color=Colors.DANGER,
            hover_color=Colors.DANGER,
            command=lambda: self._bulk_set("Absent"),
        ).pack(side="right", padx=(4, 0))

        # ── Selector bar (class + date) ───────────────────────────────────────
        sel_bar = ctk.CTkFrame(self, fg_color=Colors.BG_CARD, corner_radius=10,
                                border_width=1, border_color=Colors.BORDER)
        sel_bar.pack(fill="x", padx=pad, pady=(0, Spacing.MD))

        sel_inner = ctk.CTkFrame(sel_bar, fg_color="transparent")
        sel_inner.pack(fill="x", padx=Spacing.LG, pady=Spacing.MD)

        # Class dropdown
        ctk.CTkLabel(sel_inner, text="Class:",
                     font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_SECONDARY).pack(side="left")
        role = self._state.current_role
        if role == ROLE_TEACHER:
            class_list = self._state.get_classes_for_role()
        else:
            class_list = sorted({s["class"] for s in self._state.students})

        self._class_var = ctk.StringVar(value=self._selected_class)
        ctk.CTkOptionMenu(
            sel_inner, values=class_list, variable=self._class_var,
            width=160, height=34, font=(Fonts.FAMILY, Fonts.SIZE_SM),
            fg_color=Colors.BG_INPUT, button_color=Colors.PRIMARY,
            text_color=Colors.TEXT_PRIMARY,
            command=self._on_class_change,
        ).pack(side="left", padx=(8, 24))

        # Date picker (simplified)
        ctk.CTkLabel(sel_inner, text="Date:",
                     font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_SECONDARY).pack(side="left")
        self._date_var = ctk.StringVar(value=self._selected_date)
        date_entry = ctk.CTkEntry(
            sel_inner, textvariable=self._date_var,
            width=130, height=34, corner_radius=8,
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            fg_color=Colors.BG_INPUT, border_color=Colors.BORDER,
            text_color=Colors.TEXT_PRIMARY,
        )
        date_entry.pack(side="left", padx=(8, 0))
        ctk.CTkLabel(sel_inner, text="(YYYY-MM-DD)",
                     font=(Fonts.FAMILY, Fonts.SIZE_XS),
                     text_color=Colors.TEXT_MUTED).pack(side="left", padx=(4, 0))

        ctk.CTkButton(
            sel_inner, text="Load",
            height=34, width=70, corner_radius=8,
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            fg_color=Colors.SECONDARY, text_color=Colors.TEXT_WHITE,
            command=self._load_attendance,
        ).pack(side="left", padx=(16, 0))

        # Save button
        ctk.CTkButton(
            sel_inner, text="💾  Save Attendance",
            height=34, width=150, corner_radius=8,
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_DARK,
            text_color=Colors.TEXT_WHITE,
            command=self._save_attendance,
        ).pack(side="right")

        # ── Live stats bar ────────────────────────────────────────────────────
        self._stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._stats_frame.pack(fill="x", padx=pad, pady=(0, Spacing.MD))

        self._stat_labels: dict[str, ctk.CTkLabel] = {}
        for key, label, color, bg in [
            ("present", "Present",  Colors.SUCCESS, Colors.SUCCESS_BG),
            ("absent",  "Absent",   Colors.DANGER,  Colors.DANGER_BG),
            ("late",    "Late",     Colors.WARNING,  Colors.WARNING_BG),
            ("leave",   "Leave",    Colors.INFO,    Colors.INFO_BG),
            ("pct",     "Attendance %", Colors.PRIMARY, Colors.PRIMARY_LIGHT),
        ]:
            chip = ctk.CTkFrame(self._stats_frame, fg_color=bg, corner_radius=8,
                                 border_width=1, border_color=color, height=48)
            chip.pack(side="left", padx=(0, Spacing.SM))
            chip.pack_propagate(False)
            inner = ctk.CTkFrame(chip, fg_color="transparent")
            inner.pack(expand=True, padx=16)
            val_lbl = ctk.CTkLabel(inner, text="—",
                                    font=(Fonts.FAMILY, Fonts.SIZE_XL, Fonts.WEIGHT_BOLD),
                                    text_color=color)
            val_lbl.pack(side="left")
            ctk.CTkLabel(inner, text=f"  {label}",
                         font=(Fonts.FAMILY, Fonts.SIZE_XS),
                         text_color=color).pack(side="left")
            self._stat_labels[key] = val_lbl

        # ── Attendance list ───────────────────────────────────────────────────
        list_panel = ctk.CTkFrame(self, fg_color=Colors.BG_CARD, corner_radius=10,
                                   border_width=1, border_color=Colors.BORDER)
        list_panel.pack(fill="both", expand=True, padx=pad, pady=(0, pad))

        # Table header
        thead = ctk.CTkFrame(list_panel, fg_color=Colors.BG_TABLE_HEAD,
                              corner_radius=0, height=38)
        thead.pack(fill="x")
        thead.pack_propagate(False)
        for w, lbl in [(50, "#"), (60, "Roll"), (200, "Student Name"),
                        (100, "Prev. Att%"), (300, "Status"), (80, "Overall")]:
            ctk.CTkLabel(thead, text=lbl, width=w,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                         text_color=Colors.TEXT_HEADING, anchor="w").pack(side="left", padx=(8,0))

        self._att_scroll = ctk.CTkScrollableFrame(list_panel, fg_color="transparent",
                                                   corner_radius=0)
        self._att_scroll.pack(fill="both", expand=True)

        self._load_attendance()

    def _load_attendance(self):
        """Load students for selected class and prefill existing attendance."""
        self._selected_class = self._class_var.get()
        self._selected_date  = self._date_var.get().strip()
        students = self._state.get_students_by_class(self._selected_class)

        # Clear existing rows
        for w in self._att_scroll.winfo_children():
            w.destroy()
        self._row_vars = {}

        if not students:
            ctk.CTkLabel(self._att_scroll, text="No students in this class.",
                         font=(Fonts.FAMILY, Fonts.SIZE_MD),
                         text_color=Colors.TEXT_MUTED).pack(pady=30)
            return

        # Existing records for selected date
        existing = {
            r["student_id"]: r["status"]
            for r in self._state.attendance
            if r["class"] == self._selected_class and r["date"] == self._selected_date
        }

        for i, student in enumerate(students):
            sid = student["id"]
            # Compute overall attendance %
            all_recs = [r for r in self._state.attendance if r["student_id"] == sid]
            if all_recs:
                pres = sum(1 for r in all_recs if r["status"] == "Present")
                att_pct = round((pres / len(all_recs)) * 100, 1)
            else:
                att_pct = 100.0
            low_att = att_pct < 75

            # Row background – highlight low-attendance students
            bg = Colors.DANGER_BG if low_att else (
                Colors.BG_TABLE_ROW if i % 2 == 0 else Colors.BG_TABLE_ALT
            )

            row = ctk.CTkFrame(self._att_scroll, fg_color=bg, height=46, corner_radius=0)
            row.pack(fill="x")
            row.pack_propagate(False)

            # Row number
            ctk.CTkLabel(row, text=str(i+1), width=50,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM),
                         text_color=Colors.TEXT_MUTED, anchor="w").pack(side="left", padx=(8,0))
            # Roll
            ctk.CTkLabel(row, text=student["roll_no"], width=60,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM),
                         text_color=Colors.TEXT_SECONDARY, anchor="w").pack(side="left")
            # Name + warning
            name_frame = ctk.CTkFrame(row, fg_color="transparent", width=200)
            name_frame.pack(side="left")
            name_frame.pack_propagate(False)
            name_text = student["name"]
            name_color = Colors.DANGER if low_att else Colors.TEXT_PRIMARY
            ctk.CTkLabel(name_frame, text=name_text,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM,
                               Fonts.WEIGHT_BOLD if low_att else Fonts.WEIGHT_NORMAL),
                         text_color=name_color, anchor="w").pack(anchor="w", padx=4, pady=2)
            if low_att:
                ctk.CTkLabel(name_frame, text="⚠ Low Attendance",
                             font=(Fonts.FAMILY, Fonts.SIZE_XS),
                             text_color=Colors.DANGER, anchor="w").pack(anchor="w", padx=4)

            # Previous att%
            pct_color = Colors.SUCCESS if att_pct >= 75 else Colors.DANGER
            ctk.CTkLabel(row, text=f"{att_pct}%", width=100,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                         text_color=pct_color, anchor="w").pack(side="left")

            # Status buttons (Present / Absent / Late / Leave)
            btn_frame = ctk.CTkFrame(row, fg_color="transparent", width=300)
            btn_frame.pack(side="left")

            status_var = ctk.StringVar(value=existing.get(sid, "Present"))
            self._row_vars[sid] = status_var

            for stat in self.STATUSES:
                color  = self.STATUS_COLORS[stat]
                bgcol  = self.STATUS_BG[stat]

                def make_cmd(s=stat, sv=status_var, bf=btn_frame):
                    def cmd():
                        sv.set(s)
                        self._refresh_btn_group(bf, s)
                        self._update_stats()
                    return cmd

                is_sel = (status_var.get() == stat)
                b = ctk.CTkButton(
                    btn_frame,
                    text=stat,
                    width=68, height=28,
                    corner_radius=6,
                    font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
                    fg_color=color if is_sel else bgcol,
                    text_color=Colors.TEXT_WHITE if is_sel else color,
                    hover_color=color,
                    command=make_cmd(),
                )
                b.pack(side="left", padx=2)

            # Overall badge
            pct_badge_color = Colors.SUCCESS if att_pct >= 75 else Colors.DANGER
            ctk.CTkLabel(row, text=f"{att_pct}%", width=80,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                         text_color=pct_badge_color, anchor="center").pack(side="left")

            # Divider
            ctk.CTkFrame(self._att_scroll, height=1, fg_color=Colors.DIVIDER,
                          corner_radius=0).pack(fill="x")

        self._update_stats()

    def _refresh_btn_group(self, frame: ctk.CTkFrame, selected: str):
        """Refresh color of all status buttons in a row's button frame."""
        btns = [w for w in frame.winfo_children() if isinstance(w, ctk.CTkButton)]
        for btn in btns:
            stat = btn.cget("text")
            color = self.STATUS_COLORS.get(stat, Colors.PRIMARY)
            bg    = self.STATUS_BG.get(stat, Colors.PRIMARY_LIGHT)
            if stat == selected:
                btn.configure(fg_color=color, text_color=Colors.TEXT_WHITE)
            else:
                btn.configure(fg_color=bg, text_color=color)

    def _bulk_set(self, status: str):
        for sid, var in self._row_vars.items():
            var.set(status)
        # Refresh all button groups
        for row_frame in self._att_scroll.winfo_children():
            if not isinstance(row_frame, ctk.CTkFrame):
                continue
            for child in row_frame.winfo_children():
                if isinstance(child, ctk.CTkFrame) and child.winfo_width() >= 280:
                    self._refresh_btn_group(child, status)
        self._update_stats()

    def _update_stats(self):
        counts = {"Present": 0, "Absent": 0, "Late": 0, "Leave": 0}
        for var in self._row_vars.values():
            s = var.get()
            if s in counts:
                counts[s] += 1
        total = len(self._row_vars) or 1
        pct = round((counts["Present"] / total) * 100, 1)

        self._stat_labels["present"].configure(text=str(counts["Present"]))
        self._stat_labels["absent"].configure(text=str(counts["Absent"]))
        self._stat_labels["late"].configure(text=str(counts["Late"]))
        self._stat_labels["leave"].configure(text=str(counts["Leave"]))
        pct_color = Colors.SUCCESS if pct >= 85 else (Colors.WARNING if pct >= 75 else Colors.DANGER)
        self._stat_labels["pct"].configure(text=f"{pct}%", text_color=pct_color)

    def _save_attendance(self):
        date_str = self._date_var.get().strip()
        cls      = self._class_var.get()

        # Remove existing records for this class + date
        self._state.attendance = [
            r for r in self._state.attendance
            if not (r["class"] == cls and r["date"] == date_str)
        ]

        # Add new records
        from app.data.sample_data import STUDENTS
        students = self._state.get_students_by_class(cls)
        for student in students:
            sid    = student["id"]
            status = self._row_vars.get(sid, ctk.StringVar(value="Present")).get()
            self._state.attendance.append({
                "id":           f"ATT{sid}{date_str}",
                "student_id":   sid,
                "student_name": student["name"],
                "class":        cls,
                "date":         date_str,
                "status":       status,
            })

        self._toast(f"Attendance saved for {cls} – {date_str}!", "success")

    def _on_class_change(self, choice):
        self._selected_class = choice
        self._load_attendance()
