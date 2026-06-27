"""
app/screens/timetable.py
Weekly timetable grid with conflict detection.
Role-Aware for Teachers (Personal Slots vs Homeroom Class View).
"""

import customtkinter as ctk
from app.config import Colors, Fonts, Spacing, CARD_CORNER, ROLE_TEACHER, ROLE_ADMIN
from app.components.cards import SectionHeader
from app.data.sample_data import DAYS, PERIODS, TIMETABLE_DATA


class TimetableScreen(ctk.CTkFrame):
    def __init__(self, parent, state, navigate_fn, toast_fn):
        super().__init__(parent, fg_color=Colors.BG_MAIN, corner_radius=0)
        self._state    = state
        self._navigate = navigate_fn
        self._toast    = toast_fn
        
        role = self._state.current_role
        self._editable = (role == ROLE_ADMIN)

        # ── Resolve Teacher Homeroom & Personal Timetable Scope ───────────────
        classes_with_tt = list(TIMETABLE_DATA.keys())
        self._allowed_options = []
        
        if role == ROLE_TEACHER:
            # Check if this teacher is assigned as a class teacher for any room
            my_classes = self._state.get_classes_for_role() if hasattr(self._state, "get_classes_for_role") else []
            
            # Policy Rule: If they are a class teacher, they get the full class view option first
            if my_classes:
                self._allowed_options = [c for c in classes_with_tt if c in my_classes]
            
            # Every teacher always has access to view their own synchronized personal timeline
            self._allowed_options.append("My Personal Timetable")
            self._sel_class = self._allowed_options[0]
        else:
            # Admin gets global roster layout visibility
            self._allowed_options = classes_with_tt
            self._sel_class = classes_with_tt[0] if classes_with_tt else "Class 8-A"

        self._build()

    def _build(self):
        pad = Spacing.XL
        role = self._state.current_role

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=pad, pady=(pad, Spacing.SM))
        
        SectionHeader(toolbar, "Timetable Matrix", "Weekly educational period schedule").pack(side="left", fill="y")

        # Dynamic Dropdown Menu
        self._class_var = ctk.StringVar(value=self._sel_class)
        ctk.CTkLabel(toolbar, text="Select View:",
                     font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_SECONDARY).pack(side="right", padx=(0, 8))
        ctk.CTkOptionMenu(
            toolbar, values=self._allowed_options, variable=self._class_var,
            width=200, height=34, font=(Fonts.FAMILY, Fonts.SIZE_SM),
            fg_color=Colors.BG_INPUT, button_color=Colors.PRIMARY,
            text_color=Colors.TEXT_PRIMARY,
            command=self._reload,
        ).pack(side="right")

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

        # ── Scrollable Grid Box ───────────────────────────────────────────────
        scroll = ctk.CTkScrollableFrame(self, fg_color=Colors.BG_MAIN, corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=pad, pady=(0, pad))

        self._grid_container = scroll
        self._draw_grid()

    def _get_subject_colors(self):
        palette = [
            (Colors.PRIMARY,   Colors.PRIMARY_LIGHT),
            (Colors.INFO,      Colors.INFO_BG),
            (Colors.WARNING,   Colors.WARNING_BG),
            (Colors.SUCCESS,   Colors.SUCCESS_BG),
            (Colors.DANGER,    Colors.DANGER_BG),
            (Colors.ACCENT,    "#E0F2F1"),
            ("#5C6BC0",        "#E8EAF6"),
            ("#00ACC1",        "#E0F7FA"),
        ]
        subjects = set()
        for day_data in TIMETABLE_DATA.values():
            for periods in day_data.values():
                subjects.update(p for p in periods if p and p != "—")
        return {subj: palette[i % len(palette)] for i, subj in enumerate(sorted(subjects))}

    def _draw_grid(self):
        for w in self._grid_container.winfo_children():
            w.destroy()

        role = self._state.current_role
        view_choice = self._class_var.get()
        subject_colors = self._get_subject_colors()

        # Check if we are rendering personal schedule layout
        is_personal_mode = (view_choice == "My Personal Timetable")

        # Grid frame container setup
        grid = ctk.CTkFrame(self._grid_container, fg_color=Colors.BG_CARD,
                             corner_radius=10, border_width=1, border_color=Colors.BORDER)
        grid.pack(fill="both", expand=True)

        # ── Header row ────────────────────────────────────────────────────────
        hrow = ctk.CTkFrame(grid, fg_color=Colors.PRIMARY, corner_radius=0, height=44)
        hrow.pack(fill="x")
        hrow.pack_propagate(False)

        ctk.CTkLabel(hrow, text="Day / Period", width=100,
                     font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_WHITE, anchor="w").pack(side="left", padx=8)

        for period in PERIODS:
            is_break = "Break" in period or "Zuhr" in period
            ctk.CTkLabel(hrow, text=period,
                         width=130 if not is_break else 100,
                         font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
                         text_color=Colors.ACCENT if is_break else Colors.TEXT_WHITE,
                         anchor="center").pack(side="left", padx=1)

        # ── Day rows mapping calculations loop ───────────────────────────────
        for day_idx, day in enumerate(DAYS):
            row = ctk.CTkFrame(grid, fg_color=Colors.BG_TABLE_ROW if day_idx % 2 == 0 else Colors.BG_TABLE_ALT, height=64, corner_radius=0)
            row.pack(fill="x")
            row.pack_propagate(False)
            ctk.CTkFrame(grid, height=1, fg_color=Colors.DIVIDER, corner_radius=0).pack(fill="x")

            # Day title card
            day_lbl = ctk.CTkFrame(row, width=100, fg_color="transparent")
            day_lbl.pack(side="left", fill="y")
            day_lbl.pack_propagate(False)
            ctk.CTkLabel(day_lbl, text=day,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                         text_color=Colors.TEXT_HEADING, anchor="w").pack(expand=True, padx=8)

            # Period cell block iterations
            for p_idx in range(len(PERIODS)):
                period_time = PERIODS[p_idx]
                is_break = "Break" in period_time or "Zuhr" in period_time
                w = 130 if not is_break else 100

                if is_break:
                    cell = ctk.CTkFrame(row, width=w, fg_color="#F0F4F8", corner_radius=0)
                    cell.pack(side="left", fill="y", padx=1)
                    cell.pack_propagate(False)
                    ctk.CTkLabel(cell, text="BREAK", font=(Fonts.FAMILY, Fonts.SIZE_XS), text_color=Colors.TEXT_MUTED).pack(expand=True)
                    continue

                display_text = "—"
                is_substitute = False
                target_colors = (Colors.PRIMARY, Colors.PRIMARY_LIGHT)

                # Tuesday substitute validation logic check 
                if role == ROLE_TEACHER and day == "Tuesday" and p_idx == 2:
                    display_text = "Mathematics\n(Sub: Class 7-A)"
                    is_substitute = True
                
                elif is_personal_mode:
                    # Scan across the dictionary data matrix to find lectures matching the teacher core subjects profile
                    found_lecture = False
                    for class_name, days_dict in TIMETABLE_DATA.items():
                        day_slots = days_dict.get(day, [])
                        if p_idx < len(day_slots):
                            subj = day_slots[p_idx]
                            # Simulation match constraint filter rules
                            if subj in ["Mathematics", "Science"]:
                                display_text = f"{subj}\n({class_name})"
                                target_colors = subject_colors.get(subj, target_colors)
                                found_lecture = True
                                break
                    if not found_lecture:
                        display_text = "—"
                else:
                    # Standard structural full timeline view mode loop (Admin or Homeroom class tracker mode)
                    class_key = view_choice
                    day_slots = TIMETABLE_DATA.get(class_key, {}).get(day, [])
                    if p_idx < len(day_slots) and day_slots[p_idx] != "—":
                        subj = day_slots[p_idx]
                        display_text = subj
                        target_colors = subject_colors.get(subj, target_colors)

                # Draw the widget cells canvas elements structures
                if display_text == "—":
                    cell = ctk.CTkFrame(row, width=w, fg_color="transparent", corner_radius=0)
                    cell.pack(side="left", fill="y", padx=1)
                    cell.pack_propagate(False)
                    ctk.CTkLabel(cell, text="—", font=(Fonts.FAMILY, Fonts.SIZE_XS), text_color=Colors.TEXT_MUTED).pack(expand=True)
                elif is_substitute:
                    cell = ctk.CTkFrame(row, width=w, fg_color=Colors.WARNING_BG, corner_radius=4, border_width=1, border_color=Colors.WARNING)
                    cell.pack(side="left", fill="y", padx=2, pady=4)
                    cell.pack_propagate(False)
                    ctk.CTkLabel(cell, text=display_text, font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD), text_color=Colors.WARNING, justify="center").pack(expand=True)
                else:
                    cell = ctk.CTkFrame(row, width=w, fg_color=target_colors[1], corner_radius=4)
                    cell.pack(side="left", fill="y", padx=2, pady=4)
                    cell.pack_propagate(False)
                    ctk.CTkLabel(cell, text=display_text, font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD), text_color=target_colors[0], justify="center", wraplength=120).pack(expand=True)

        # Bottom actions block
        hint = ctk.CTkFrame(self._grid_container, fg_color="transparent")
        hint.pack(fill="x", pady=(Spacing.SM, 0))
        ctk.CTkButton(hint, text="🖨  Print Timetable", height=34, width=150,
                      corner_radius=8, font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                      fg_color=Colors.SECONDARY, text_color=Colors.TEXT_WHITE,
                      command=lambda: self._toast("Timetable report sent to print buffer!", "success")
                      ).pack(side="left")
        
        if self._editable:
            ctk.CTkButton(hint, text="✏  Edit Period Slots", height=34, width=150,
                          corner_radius=8, font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                          fg_color=Colors.PRIMARY, text_color=Colors.TEXT_WHITE,
                          command=lambda: self._toast("Opening master configurations schedule block manager!", "info")
                          ).pack(side="left", padx=(8, 0))

    def _reload(self, choice=None):
        self._draw_grid()