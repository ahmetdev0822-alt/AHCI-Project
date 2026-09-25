"""
app/screens/attendance.py
Attendance Screen – Blue & White theme + strict RBAC:
  - Admin:   VIEW ONLY  – audit inspection, stats breakdown
  - Teacher: EDIT – mark attendance, bulk actions with instant Undo
  - Parent:  CHILD VIEW – 30-day chronological attendance log & stats
Addresses CS3014 Section 2 (Bulk actions + Undo) and Section 10 (Multi-state views).
"""

import customtkinter as ctk
from datetime import date
from app.config import (
    Colors, Fonts, Spacing, CARD_CORNER,
    ROLE_ADMIN, ROLE_TEACHER, ROLE_PARENT,
)
from app.components.cards import SectionHeader, StatusBadge, MetricCard
from app.components.state_view import StateView, StateSwitchDemoBar


class AttendanceScreen(ctk.CTkFrame):
    """Bulk attendance interface with role-based access control and inline undo."""

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
        self._row_vars:  dict[str, ctk.StringVar] = {}
        self._row_frames: dict[str, ctk.CTkFrame] = {}
        self._last_bulk_state: dict[str, str] = {}
        self._selected_date = date.today().isoformat()
        self._search_var = ctk.StringVar()

        role = self._state.current_role

        # Determine allowed classes
        if role == ROLE_TEACHER:
            my_classes = self._state.get_classes_for_role()
            self._selected_class = my_classes[0] if my_classes else "Class 8-A"
        elif role == ROLE_PARENT:
            child = self._state.get_linked_child()
            self._selected_class = child.get("class", "Class 8-A") if child else "Class 8-A"
        else:  # Admin
            all_classes = sorted({s["class"] for s in self._state.students})
            self._selected_class = all_classes[0] if all_classes else "Class 8-A"

        self._editable = (role == ROLE_TEACHER)
        self._build()

    def _build(self):
        pad  = Spacing.XL
        role = self._state.current_role

        # Top Bar
        top_row = ctk.CTkFrame(self, fg_color="transparent")
        top_row.pack(fill="x", padx=pad, pady=(pad, 0))
        SectionHeader(top_row, "Attendance Registry", "Real-time presence tracking and bulk class operations").pack(side="left", fill="y")
        StateSwitchDemoBar(top_row, on_switch_fn=self._on_state_switch).pack(side="right")

        # Read-Only Banner for Admin
        if not self._editable and role == ROLE_ADMIN:
            banner = ctk.CTkFrame(self, fg_color=Colors.INFO_BG, corner_radius=8, border_width=1, border_color=Colors.INFO)
            banner.pack(fill="x", padx=pad, pady=(Spacing.SM, 0))
            ctk.CTkLabel(banner, text="🔒  Administrator View  –  Audit and print attendance records across all school sections.", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.INFO).pack(padx=16, pady=6)

        # Toolbar
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=pad, pady=(Spacing.SM, Spacing.SM))

        if self._editable:
            ctk.CTkButton(
                toolbar, text="✓  All Present",
                height=34, corner_radius=8, width=120,
                font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                fg_color=Colors.SUCCESS_BG, text_color=Colors.SUCCESS,
                hover_color=Colors.SUCCESS,
                command=lambda: self._bulk_set("Present"),
            ).pack(side="right", padx=(6, 0))

            ctk.CTkButton(
                toolbar, text="✕  All Absent",
                height=34, corner_radius=8, width=120,
                font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                fg_color=Colors.DANGER_BG, text_color=Colors.DANGER,
                hover_color=Colors.DANGER,
                command=lambda: self._bulk_set("Absent"),
            ).pack(side="right", padx=(6, 0))

        # Search box
        search_entry = ctk.CTkEntry(
            toolbar,
            textvariable=self._search_var,
            placeholder_text="🔍  Filter student name...",
            height=34, width=220, corner_radius=8,
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            fg_color=Colors.BG_INPUT, border_color=Colors.BORDER, text_color=Colors.TEXT_PRIMARY,
        )
        search_entry.pack(side="left")
        self._search_var.trace_add("write", lambda *_: self._filter_rows())

        # ── Selector Bar ──────────────────────────────────────────────────────
        sel_bar = ctk.CTkFrame(self, fg_color=Colors.BG_CARD, corner_radius=10, border_width=1, border_color=Colors.BORDER)
        sel_bar.pack(fill="x", padx=pad, pady=(0, Spacing.MD))
        sel_inner = ctk.CTkFrame(sel_bar, fg_color="transparent")
        sel_inner.pack(fill="x", padx=Spacing.LG, pady=Spacing.MD)

        if role == ROLE_PARENT:
            child = self._state.get_linked_child()
            cname = child.get("name", "Student") if child else "Fatima Bibi"
            ctk.CTkLabel(sel_inner, text=f"Viewing Attendance For: {cname} ({self._selected_class})", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.PRIMARY).pack(side="left")
        else:
            ctk.CTkLabel(sel_inner, text="Class:", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_SECONDARY).pack(side="left")
            class_list = self._state.get_classes_for_role() if role == ROLE_TEACHER else sorted({s["class"] for s in self._state.students})
            self._class_var = ctk.StringVar(value=self._selected_class)
            ctk.CTkOptionMenu(
                sel_inner, values=class_list, variable=self._class_var,
                width=160, height=34, font=(Fonts.FAMILY, Fonts.SIZE_SM),
                fg_color=Colors.BG_INPUT, button_color=Colors.PRIMARY, text_color=Colors.TEXT_PRIMARY,
                command=self._on_class_change,
            ).pack(side="left", padx=(8, 20))

            ctk.CTkLabel(sel_inner, text="Date:", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_SECONDARY).pack(side="left")
            self._date_var = ctk.StringVar(value=self._selected_date)
            ctk.CTkEntry(
                sel_inner, textvariable=self._date_var, width=130, height=34, corner_radius=8,
                font=(Fonts.FAMILY, Fonts.SIZE_SM), fg_color=Colors.BG_INPUT, border_color=Colors.BORDER, text_color=Colors.TEXT_PRIMARY,
            ).pack(side="left", padx=(8, 0))

            ctk.CTkButton(
                sel_inner, text="Load", height=34, width=70, corner_radius=8,
                font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                fg_color=Colors.SECONDARY, text_color=Colors.TEXT_WHITE,
                command=self._load_attendance,
            ).pack(side="left", padx=(12, 0))

        if self._editable:
            ctk.CTkButton(
                sel_inner, text="💾  Save to Database",
                height=34, width=160, corner_radius=8,
                font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_DARK,
                text_color=Colors.TEXT_WHITE,
                command=self._save_attendance,
            ).pack(side="right")
        elif role == ROLE_ADMIN:
            ctk.CTkButton(
                sel_inner, text="🖨  Print Sheet", height=34, width=120, corner_radius=8,
                font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                fg_color=Colors.INFO_BG, text_color=Colors.INFO,
                command=lambda: self._toast("Attendance sheet generated for printing.", "info"),
            ).pack(side="right")

        # ── StateView Container ───────────────────────────────────────────────
        self._state_view = StateView(
            self,
            on_retry=lambda: self._on_state_switch("content"),
            on_action=lambda: self._navigate("dashboard"),
        )
        self._state_view.pack(fill="both", expand=True)

        if role == ROLE_PARENT:
            self._render_parent_attendance(self._state_view.content_area)
        else:
            self._render_table_scaffold(self._state_view.content_area)

    def _on_state_switch(self, mode: str):
        if mode == "content":
            self._state_view.set_state("content")
        elif mode == "empty":
            self._state_view.set_state("empty", title="No Attendance Logs Found", message="No attendance entries recorded for this section on the selected date.", action_text="Mark Class Roster")
        elif mode == "loading":
            self._state_view.set_state("loading", title="Fetching Attendance Records...", message="Querying student roll call and percentage distributions from SQLite.")
        elif mode == "error":
            self._state_view.set_state("error", title="Attendance Sync Error", message="Failed to commit batch attendance update to the local database.", error_details="ERR_SQLITE_BATCH_TRANSACTION_FAILED (Code 503)")
        elif mode == "offline":
            self._state_view.set_state("offline", title="Offline Attendance Marking", message="Operating in offline mode. Bulk attendance edits are cached locally in SQLite.", action_text="Continue Offline")

    def _render_table_scaffold(self, parent):
        pad = Spacing.XL

        # Stats Chips
        self._stats_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self._stats_frame.pack(fill="x", padx=pad, pady=(0, Spacing.SM))
        self._stat_labels: dict[str, ctk.CTkLabel] = {}
        for key, label, color, bg in [
            ("present", "Present", Colors.SUCCESS, Colors.SUCCESS_BG),
            ("absent",  "Absent",  Colors.DANGER,  Colors.DANGER_BG),
            ("late",    "Late",    Colors.WARNING, Colors.WARNING_BG),
            ("leave",   "Leave",   Colors.INFO,    Colors.INFO_BG),
        ]:
            chip = ctk.CTkFrame(self._stats_frame, fg_color=bg, corner_radius=8, border_width=1, border_color=color)
            chip.pack(side="left", padx=(0, Spacing.SM))
            lbl = ctk.CTkLabel(chip, text=f"  {label}: 0  ", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=color)
            lbl.pack(padx=8, pady=4)
            self._stat_labels[key] = lbl

        # Table Container
        tbl = ctk.CTkFrame(parent, fg_color=Colors.BG_CARD, corner_radius=10, border_width=1, border_color=Colors.BORDER)
        tbl.pack(fill="both", expand=True, padx=pad, pady=(0, pad))

        # Header
        h = ctk.CTkFrame(tbl, fg_color=Colors.BG_TABLE_HEAD, corner_radius=0, height=38)
        h.pack(fill="x")
        h.pack_propagate(False)

        cols = [("#", 45), ("Roll No", 75), ("Student Name", 240), ("Attendance Status", 320), ("30-Day %", 100)]
        for label, w in cols:
            ctk.CTkLabel(h, text=label, width=w, font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_HEADING, anchor="w").pack(side="left", padx=10)

        # Scrollable Rows
        self._table_scroll = ctk.CTkScrollableFrame(tbl, fg_color="transparent", corner_radius=0)
        self._table_scroll.pack(fill="both", expand=True)

        self._populate_rows()

    def _render_parent_attendance(self, parent):
        pad = Spacing.XL
        child = self._state.get_linked_child() or {"id": "S003", "name": "Fatima Bibi Chaudhry", "class": "Class 8-A"}
        pct = self._state.compute_attendance_pct(child["id"])

        # KPI Summary Cards
        kpi_row = ctk.CTkFrame(parent, fg_color="transparent")
        kpi_row.pack(fill="x", padx=pad, pady=(0, Spacing.LG))

        child_records = [r for r in self._state.attendance if r["student_id"] == child["id"]]
        pres = sum(1 for r in child_records if r["status"] == "Present")
        absn = sum(1 for r in child_records if r["status"] == "Absent")
        late = sum(1 for r in child_records if r["status"] == "Late")

        kpis = [
            ("Attendance Rate", f"{pct}%", Colors.SUCCESS if pct >= 85 else Colors.WARNING, "30-Day Overall Track"),
            ("Present Days", f"{pres} Days", Colors.SUCCESS, "Attended lectures"),
            ("Absent Days", f"{absn} Days", Colors.DANGER if absn > 2 else Colors.TEXT_MUTED, "Unexcused absences"),
            ("Late Arrivals", f"{late} Days", Colors.WARNING, "Recorded late check-ins"),
        ]
        for col, (title, val, acc, sub) in enumerate(kpis):
            kpi_row.columnconfigure(col, weight=1)
            MetricCard(kpi_row, title=title, value=val, accent=acc, sub_label=sub).grid(row=0, column=col, padx=(0, Spacing.MD if col < 3 else 0), sticky="nsew")

        # Chronological Log Table
        tbl = ctk.CTkFrame(parent, fg_color=Colors.BG_CARD, corner_radius=10, border_width=1, border_color=Colors.BORDER)
        tbl.pack(fill="both", expand=True, padx=pad, pady=(0, pad))

        h = ctk.CTkFrame(tbl, fg_color=Colors.BG_TABLE_HEAD, corner_radius=0, height=38)
        h.pack(fill="x")
        h.pack_propagate(False)

        ctk.CTkLabel(h, text="Date", width=140, font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_HEADING, anchor="w").pack(side="left", padx=12)
        ctk.CTkLabel(h, text="Day", width=140, font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_HEADING, anchor="w").pack(side="left", padx=12)
        ctk.CTkLabel(h, text="Status", width=140, font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_HEADING, anchor="w").pack(side="left", padx=12)
        ctk.CTkLabel(h, text="Remarks / Verification", width=260, font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_HEADING, anchor="w").pack(side="left", padx=12)

        scroll = ctk.CTkScrollableFrame(tbl, fg_color="transparent", corner_radius=0)
        scroll.pack(fill="both", expand=True)

        for idx, r in enumerate(child_records[:20]):
            rf = ctk.CTkFrame(scroll, fg_color=Colors.BG_TABLE_ROW if idx % 2 == 0 else Colors.BG_TABLE_ALT, height=38)
            rf.pack(fill="x")
            rf.pack_propagate(False)

            ctk.CTkLabel(rf, text=r["date"], width=140, font=(Fonts.FAMILY, Fonts.SIZE_SM), text_color=Colors.TEXT_PRIMARY, anchor="w").pack(side="left", padx=12)
            ctk.CTkLabel(rf, text="Weekday", width=140, font=(Fonts.FAMILY, Fonts.SIZE_SM), text_color=Colors.TEXT_MUTED, anchor="w").pack(side="left", padx=12)
            StatusBadge(rf, r["status"]).pack(side="left", padx=12)
            ctk.CTkLabel(rf, text="Verified by Class Teacher" if r["status"]=="Present" else "Parent notified via SMS", width=260, font=(Fonts.FAMILY, Fonts.SIZE_XS), text_color=Colors.TEXT_MUTED, anchor="w").pack(side="left", padx=12)

    def _populate_rows(self):
        for w in self._table_scroll.winfo_children():
            w.destroy()
        self._row_vars.clear()
        self._row_frames.clear()

        students = [s for s in self._state.students if s["class"] == self._selected_class]
        date_str = self._date_var.get()

        for idx, student in enumerate(students):
            sid = student["id"]
            # Find existing record
            existing = next((r for r in self._state.attendance if r["student_id"] == sid and r["date"] == date_str), None)
            init_status = existing["status"] if existing else "Present"

            var = ctk.StringVar(value=init_status)
            self._row_vars[sid] = var

            rf = ctk.CTkFrame(self._table_scroll, fg_color=Colors.BG_TABLE_ROW if idx % 2 == 0 else Colors.BG_TABLE_ALT, height=44)
            rf.pack(fill="x")
            rf.pack_propagate(False)
            self._row_frames[sid] = rf

            ctk.CTkLabel(rf, text=str(idx + 1), width=45, font=(Fonts.FAMILY, Fonts.SIZE_SM), text_color=Colors.TEXT_MUTED, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(rf, text=student.get("roll_no", "-"), width=75, font=(Fonts.FAMILY_MONO, Fonts.SIZE_SM), text_color=Colors.TEXT_PRIMARY, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(rf, text=student["name"], width=240, font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_PRIMARY, anchor="w").pack(side="left", padx=10)

            # Buttons container
            bc = ctk.CTkFrame(rf, fg_color="transparent", width=320)
            bc.pack(side="left", padx=10)

            if self._editable:
                for status in self.STATUSES:
                    sc = self.STATUS_COLORS[status]
                    btn = ctk.CTkRadioButton(
                        bc, text=status, variable=var, value=status,
                        font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
                        text_color=sc, fg_color=sc, hover_color=sc,
                        command=self._update_stats_display,
                    )
                    btn.pack(side="left", padx=(0, 10))
            else:
                StatusBadge(bc, init_status).pack(side="left")

            pct = self._state.compute_attendance_pct(sid)
            pct_color = Colors.SUCCESS if pct >= 85 else (Colors.WARNING if pct >= 75 else Colors.DANGER)
            ctk.CTkLabel(rf, text=f"{pct}%", width=100, font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=pct_color, anchor="w").pack(side="left", padx=10)

        self._update_stats_display()

    def _filter_rows(self):
        q = self._search_var.get().strip().lower()
        students = [s for s in self._state.students if s["class"] == self._selected_class]
        for s in students:
            sid = s["id"]
            rf = self._row_frames.get(sid)
            if rf:
                if not q or q in s["name"].lower() or q in s.get("roll_no", ""):
                    rf.pack(fill="x")
                else:
                    rf.pack_forget()

    def _bulk_set(self, status: str):
        # Save snapshot for undo
        self._last_bulk_state = {sid: var.get() for sid, var in self._row_vars.items()}
        for var in self._row_vars.values():
            var.set(status)
        self._update_stats_display()
        self._toast(
            f"Marked all students as '{status}'.",
            "info",
            action_label="↶ Undo",
            action_fn=self._undo_bulk_action,
        )

    def _undo_bulk_action(self):
        if self._last_bulk_state:
            for sid, prev_stat in self._last_bulk_state.items():
                if sid in self._row_vars:
                    self._row_vars[sid].set(prev_stat)
            self._update_stats_display()
            self._toast("Bulk action undone. Reverted previous statuses.", "success")
            self._last_bulk_state.clear()

    def _update_stats_display(self):
        if not hasattr(self, "_stat_labels"):
            return
        vals = [var.get() for var in self._row_vars.values()]
        for k in ["present", "absent", "late", "leave"]:
            c = vals.count(k.capitalize())
            if k in self._stat_labels:
                self._stat_labels[k].configure(text=f"  {k.capitalize()}: {c}  ")

    def _save_attendance(self):
        date_str = self._date_var.get()
        students = [s for s in self._state.students if s["class"] == self._selected_class]
        records = []
        for s in students:
            sid = s["id"]
            stat = self._row_vars[sid].get()
            records.append({
                "id": f"ATT{sid}{date_str}",
                "student_id": sid,
                "student_name": s["name"],
                "class": self._selected_class,
                "date": date_str,
                "status": stat,
            })
        self._state.save_attendance_batch(records)
        self._toast(f"Attendance for {self._selected_class} ({date_str}) saved to SQLite database!", "success")

    def _load_attendance(self):
        self._selected_date = self._date_var.get()
        self._populate_rows()
        self._toast(f"Loaded attendance records for {self._selected_date}", "info")

    def _on_class_change(self, val):
        self._selected_class = val
        self._populate_rows()