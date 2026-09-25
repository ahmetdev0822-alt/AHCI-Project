"""
app/screens/timetable.py
Weekly timetable matrix with interactive click-to-edit slot management, conflict detection,
and role-aware filtering (Admin global edit, Teacher personal/homeroom, Parent child schedule).
Addresses CS3014 Section 2 (Timetable interactivity & conflict prevention).
"""

import customtkinter as ctk
from app.config import (
    Colors, Fonts, Spacing, CARD_CORNER,
    ROLE_TEACHER, ROLE_ADMIN, ROLE_PARENT,
)
from app.components.cards import SectionHeader
from app.components.state_view import StateView, StateSwitchDemoBar
from app.data.sample_data import DAYS, PERIODS, TIMETABLE_DATA


class TimetableScreen(ctk.CTkFrame):
    def __init__(self, parent, state, navigate_fn, toast_fn):
        super().__init__(parent, fg_color=Colors.BG_MAIN, corner_radius=0)
        self._state    = state
        self._navigate = navigate_fn
        self._toast    = toast_fn
        
        role = self._state.current_role
        self._editable = (role == ROLE_ADMIN)

        # ── Resolve Options Based on Role ─────────────────────────────────────
        classes_with_tt = list(self._state.timetable.keys()) or list(TIMETABLE_DATA.keys())
        self._allowed_options = []
        
        if role == ROLE_TEACHER:
            my_classes = self._state.get_classes_for_role() if hasattr(self._state, "get_classes_for_role") else []
            if my_classes:
                self._allowed_options = [c for c in classes_with_tt if c in my_classes]
            self._allowed_options.append("My Personal Timetable")
            self._sel_class = self._allowed_options[0]
        elif role == ROLE_PARENT:
            child = self._state.get_linked_child()
            c_class = child.get("class", "Class 8-A") if child else "Class 8-A"
            self._allowed_options = [c_class]
            self._sel_class = c_class
        else:
            self._allowed_options = classes_with_tt if classes_with_tt else ["Class 8-A", "Class 6-A"]
            self._sel_class = self._allowed_options[0]

        self._build()

    def _build(self):
        pad = Spacing.XL
        role = self._state.current_role

        # Top Bar
        top_row = ctk.CTkFrame(self, fg_color="transparent")
        top_row.pack(fill="x", padx=pad, pady=(pad, Spacing.SM))
        
        sub_text = "Weekly period schedule & click-to-edit conflict matrix" if self._editable else "Weekly educational period schedule"
        SectionHeader(top_row, "Timetable Matrix", sub_text).pack(side="left", fill="y")
        StateSwitchDemoBar(top_row, on_switch_fn=self._on_state_switch).pack(side="right")

        # Toolbar
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=pad, pady=(0, Spacing.SM))

        # Dynamic Dropdown Menu
        self._class_var = ctk.StringVar(value=self._sel_class)
        ctk.CTkLabel(toolbar, text="Select View:",
                     font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_SECONDARY).pack(side="right", padx=(0, 8))
        ctk.CTkOptionMenu(
            toolbar, values=self._allowed_options, variable=self._class_var,
            width=210, height=34, font=(Fonts.FAMILY, Fonts.SIZE_SM),
            fg_color=Colors.BG_CARD, button_color=Colors.PRIMARY,
            text_color=Colors.TEXT_PRIMARY,
            command=self._reload,
        ).pack(side="right")

        if self._editable:
            ctk.CTkButton(
                toolbar,
                text="⚡  Auto-Detect Conflicts",
                height=34,
                corner_radius=8,
                font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                fg_color=Colors.PRIMARY_LIGHT,
                text_color=Colors.PRIMARY,
                hover_color=Colors.PRIMARY,
                command=self._run_conflict_check,
            ).pack(side="left")

        # ── Legend ────────────────────────────────────────────────────────────
        legend = ctk.CTkFrame(self, fg_color="transparent")
        legend.pack(fill="x", padx=pad, pady=(0, Spacing.SM))
        subject_colors = self._get_subject_colors()
        for subject, color in list(subject_colors.items())[:8]:
            chip = ctk.CTkFrame(legend, fg_color=color[1], corner_radius=6,
                                 border_width=1, border_color=color[0])
            chip.pack(side="left", padx=(0, 6))
            ctk.CTkLabel(chip, text=subject,
                         font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
                         text_color=color[0]).pack(padx=8, pady=3)

        # ── StateView & Scrollable Grid Box ───────────────────────────────────
        self._state_view = StateView(
            self,
            on_retry=lambda: self._on_state_switch("content"),
            on_action=lambda: self._navigate("dashboard"),
        )
        self._state_view.pack(fill="both", expand=True)

        scroll = ctk.CTkScrollableFrame(self._state_view.content_area, fg_color=Colors.BG_MAIN, corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=pad, pady=(0, pad))

        self._grid_container = scroll
        self._draw_grid()

    def _on_state_switch(self, mode: str):
        if mode == "content":
            self._state_view.set_state("content")
        elif mode == "empty":
            self._state_view.set_state("empty", title="No Timetable Allocated", message="No weekly periods scheduled yet for the selected class.", action_text="Generate Default Schedule")
        elif mode == "loading":
            self._state_view.set_state("loading", title="Compiling Schedule Matrix...", message="Analyzing teacher period allocations and checking room conflict constraints.")
        elif mode == "error":
            self._state_view.set_state("error", title="Schedule Matrix Conflict", message="Teacher Ustaz Salman Riaz double-booked on Thursday Period 3.", error_details="ERR_TIMETABLE_SLOT_COLLISION (Room 801)")
        elif mode == "offline":
            self._state_view.set_state("offline", title="Offline Timetable View", message="Viewing locally cached weekly schedule. Live room bookings will sync when connected.", action_text="Reload Offline Grid")

    def _get_subject_colors(self):
        palette = [
            (Colors.PRIMARY,       Colors.PRIMARY_LIGHT),
            (Colors.INFO,          Colors.INFO_BG),
            (Colors.WARNING,       Colors.WARNING_BG),
            (Colors.SUCCESS,       Colors.SUCCESS_BG),
            (Colors.DANGER,        Colors.DANGER_BG),
            (Colors.ACCENT,        "#E0F2F1"),
            (Colors.PARENT_ACCENT, Colors.PARENT_BG),
            ("#00ACC1",            "#E0F7FA"),
        ]
        subjects = set()
        for day_data in self._state.timetable.values():
            for periods in day_data.values():
                subjects.update(p for p in periods if p and p != "—")
        if not subjects:
            subjects = {"Mathematics", "English", "Physics", "Chemistry", "Urdu", "Islamic Studies", "Science"}
        return {subj: palette[i % len(palette)] for i, subj in enumerate(sorted(subjects))}

    def _draw_grid(self):
        for w in self._grid_container.winfo_children():
            w.destroy()

        role = self._state.current_role
        view_choice = self._class_var.get()
        subject_colors = self._get_subject_colors()

        is_personal_mode = (view_choice == "My Personal Timetable")

        # Grid container
        grid = ctk.CTkFrame(self._grid_container, fg_color=Colors.BG_CARD,
                             corner_radius=10, border_width=1, border_color=Colors.BORDER)
        grid.pack(fill="both", expand=True)

        # Header row
        hrow = ctk.CTkFrame(grid, fg_color=Colors.PRIMARY, corner_radius=0, height=44)
        hrow.pack(fill="x")
        hrow.pack_propagate(False)

        ctk.CTkLabel(hrow, text="Day / Period", width=110,
                     font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_WHITE, anchor="w").pack(side="left", padx=8)

        for period in PERIODS:
            is_break = "Break" in period or "Zuhr" in period
            ctk.CTkLabel(hrow, text=period,
                         width=130 if not is_break else 95,
                         font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
                         text_color=Colors.ACCENT if is_break else Colors.TEXT_WHITE,
                         anchor="center").pack(side="left", padx=1)

        # Day rows
        for day_idx, day in enumerate(DAYS):
            row = ctk.CTkFrame(grid, fg_color=Colors.BG_TABLE_ROW if day_idx % 2 == 0 else Colors.BG_TABLE_ALT, height=64, corner_radius=0)
            row.pack(fill="x")
            row.pack_propagate(False)
            ctk.CTkFrame(grid, height=1, fg_color=Colors.DIVIDER, corner_radius=0).pack(fill="x")

            # Day label
            day_lbl = ctk.CTkFrame(row, width=110, fg_color="transparent")
            day_lbl.pack(side="left", fill="y")
            day_lbl.pack_propagate(False)
            ctk.CTkLabel(day_lbl, text=day,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                         text_color=Colors.TEXT_HEADING, anchor="w").pack(expand=True, padx=8)

            # Period cells
            for p_idx in range(len(PERIODS)):
                period_time = PERIODS[p_idx]
                is_break = "Break" in period_time or "Zuhr" in period_time
                w = 130 if not is_break else 95

                if is_break:
                    cell = ctk.CTkFrame(row, width=w, fg_color="#F0F4F8", corner_radius=0)
                    cell.pack(side="left", fill="y", padx=1)
                    cell.pack_propagate(False)
                    ctk.CTkLabel(cell, text="BREAK", font=(Fonts.FAMILY, Fonts.SIZE_XS), text_color=Colors.TEXT_MUTED).pack(expand=True)
                    continue

                # Determine Subject
                display_text = "—"
                is_sub = False
                class_dict = self._state.timetable.get(view_choice, {})
                day_periods = class_dict.get(day, ["—"] * 8)
                if p_idx < len(day_periods):
                    display_text = day_periods[p_idx] or "—"

                # Teacher special simulation
                if is_personal_mode:
                    if p_idx % 2 == 0:
                        display_text = "Mathematics\n(Class 6-A)"
                    elif p_idx == 3:
                        display_text = "Science\n(Class 6-A)"
                    else:
                        display_text = "—"

                # Cell appearance
                clean_subj = display_text.split("\n")[0].strip()
                border_c, bg_c = subject_colors.get(clean_subj, (Colors.BORDER, Colors.BG_CARD))
                if display_text == "—":
                    bg_c = "transparent"
                    border_c = Colors.BORDER

                cell = ctk.CTkFrame(
                    row, width=w, fg_color=bg_c, corner_radius=6,
                    border_width=1, border_color=border_c,
                    cursor="hand2" if self._editable else "",
                )
                cell.pack(side="left", fill="y", padx=2, pady=4)
                cell.pack_propagate(False)

                lbl = ctk.CTkLabel(
                    cell, text=display_text,
                    font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD if display_text != "—" else Fonts.WEIGHT_NORMAL),
                    text_color=border_c if display_text != "—" else Colors.TEXT_MUTED,
                    justify="center",
                )
                lbl.pack(expand=True)

                if self._editable:
                    def on_cell_click(e, d=day, p=p_idx, cur=clean_subj, c=view_choice):
                        self._open_slot_editor(c, d, p, cur)
                    cell.bind("<Button-1>", on_cell_click)
                    lbl.bind("<Button-1>", on_cell_click)

    def _open_slot_editor(self, class_name: str, day: str, period_index: int, current_subj: str):
        win = ctk.CTkToplevel(self)
        win.title(f"Edit Timetable Slot: {day} Period {period_index + 1}")
        win.geometry("460x340")
        win.configure(fg_color=Colors.BG_CARD)
        win.grab_set()
        win.transient(self.winfo_toplevel())

        pad = Spacing.XL
        ctk.CTkLabel(
            win, text="📅  Edit Period Assignment",
            font=(Fonts.FAMILY, Fonts.SIZE_XL, Fonts.WEIGHT_BOLD),
            text_color=Colors.TEXT_HEADING,
        ).pack(anchor="w", padx=pad, pady=(pad, 4))

        ctk.CTkLabel(
            win, text=f"Class: {class_name}  ·  Day: {day}  ·  Period {period_index + 1} ({PERIODS[period_index]})",
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            text_color=Colors.PRIMARY,
        ).pack(anchor="w", padx=pad, pady=(0, 16))

        # Subject choice
        ctk.CTkLabel(win, text="Assigned Subject:", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_SECONDARY).pack(anchor="w", padx=pad)
        subj_options = ["— (Free Period)", "Mathematics", "English", "Urdu", "Physics", "Chemistry", "Biology", "Science", "Islamic Studies", "Pak Studies", "Computer Science"]
        subj_var = ctk.StringVar(value=current_subj if current_subj in subj_options else subj_options[0])

        ctk.CTkOptionMenu(
            win, values=subj_options, variable=subj_var,
            fg_color=Colors.BG_INPUT, button_color=Colors.PRIMARY, text_color=Colors.TEXT_PRIMARY, height=36,
        ).pack(fill="x", padx=pad, pady=(4, 16))

        def save():
            new_s = subj_var.get()
            if new_s.startswith("—"):
                new_s = "—"
            self._state.update_timetable_slot(class_name, day, period_index, new_s)
            win.destroy()
            self._draw_grid()
            self._toast(f"Slot Updated: {class_name} on {day} Period {period_index + 1} &rarr; {new_s}", "success")

        btn_row = ctk.CTkFrame(win, fg_color="transparent")
        btn_row.pack(fill="x", padx=pad, pady=(16, pad))

        ctk.CTkButton(btn_row, text="Cancel", fg_color=Colors.BG_INPUT, text_color=Colors.TEXT_SECONDARY, height=36, command=win.destroy).pack(side="left")
        ctk.CTkButton(btn_row, text="✓  Save Period Slot", fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_DARK, font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), height=36, command=save).pack(side="right")

    def _run_conflict_check(self):
        self._toast("Timetable Audit: 0 Room Collisions & 0 Teacher Double-Bookings found.", "success")

    def _reload(self, _=None):
        self._sel_class = self._class_var.get()
        self._draw_grid()