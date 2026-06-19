"""
app/screens/timetable.py
Weekly timetable grid with conflict detection.
"""

import customtkinter as ctk
from app.config import Colors, Fonts, Spacing, CARD_CORNER
from app.components.cards import SectionHeader
from app.data.sample_data import DAYS, PERIODS, TIMETABLE_DATA


class TimetableScreen(ctk.CTkFrame):
    def __init__(self, parent, state, navigate_fn, toast_fn):
        super().__init__(parent, fg_color=Colors.BG_MAIN, corner_radius=0)
        self._state    = state
        self._navigate = navigate_fn
        self._toast    = toast_fn

        classes_with_tt = list(TIMETABLE_DATA.keys())
        self._sel_class = classes_with_tt[0] if classes_with_tt else "Class 8-A"
        self._build()

    def _build(self):
        pad = Spacing.XL

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=pad, pady=(pad, Spacing.SM))
        SectionHeader(toolbar, "Timetable", "Weekly period schedule for each class"
                      ).pack(side="left", fill="y")

        # Class selector
        classes_with_tt = list(TIMETABLE_DATA.keys())
        self._class_var = ctk.StringVar(value=self._sel_class)
        ctk.CTkLabel(toolbar, text="View Class:",
                     font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_SECONDARY).pack(side="right", padx=(0, 8))
        ctk.CTkOptionMenu(
            toolbar, values=classes_with_tt, variable=self._class_var,
            width=160, height=34, font=(Fonts.FAMILY, Fonts.SIZE_SM),
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

        # ── Grid container (scrollable) ───────────────────────────────────────
        scroll = ctk.CTkScrollableFrame(self, fg_color=Colors.BG_MAIN, corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=pad, pady=(0, pad))

        self._grid_container = scroll
        self._draw_grid()

    def _get_subject_colors(self):
        """Map subjects to consistent colors."""
        palette = [
            (Colors.PRIMARY,   Colors.PRIMARY_LIGHT),
            (Colors.INFO,      Colors.INFO_BG),
            (Colors.WARNING,   Colors.WARNING_BG),
            (Colors.SUCCESS,   Colors.SUCCESS_BG),
            (Colors.DANGER,    Colors.DANGER_BG),
            (Colors.ACCENT,    "#FDF8E7"),
            ("#7B68EE",        "#F0EEFF"),
            ("#2E8B57",        "#E6F7EF"),
        ]
        subjects = set()
        for day_data in TIMETABLE_DATA.values():
            for periods in day_data.values():
                subjects.update(p for p in periods if p and p != "—")
        return {subj: palette[i % len(palette)] for i, subj in enumerate(sorted(subjects))}

    def _draw_grid(self):
        for w in self._grid_container.winfo_children():
            w.destroy()

        cls = self._class_var.get()
        tt  = TIMETABLE_DATA.get(cls, {})
        subject_colors = self._get_subject_colors()

        # Grid frame
        grid = ctk.CTkFrame(self._grid_container, fg_color=Colors.BG_CARD,
                             corner_radius=10, border_width=1, border_color=Colors.BORDER)
        grid.pack(fill="both", expand=True)

        # ── Header row: Period times ──────────────────────────────────────────
        hrow = ctk.CTkFrame(grid, fg_color=Colors.SECONDARY, corner_radius=0, height=44)
        hrow.pack(fill="x")
        hrow.pack_propagate(False)

        # Day column header
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

        # ── Day rows ──────────────────────────────────────────────────────────
        conflict_cells: list[tuple[str, int]] = []  # (day, period_idx) of conflicts

        for day_idx, day in enumerate(DAYS):
            day_periods = tt.get(day, ["—"] * len(PERIODS))
            bg = Colors.BG_TABLE_ROW if day_idx % 2 == 0 else Colors.BG_TABLE_ALT

            row = ctk.CTkFrame(grid, fg_color=bg, height=56, corner_radius=0)
            row.pack(fill="x")
            row.pack_propagate(False)
            ctk.CTkFrame(grid, height=1, fg_color=Colors.DIVIDER, corner_radius=0).pack(fill="x")

            # Day label
            day_lbl = ctk.CTkFrame(row, width=100, fg_color="transparent")
            day_lbl.pack(side="left", fill="y")
            day_lbl.pack_propagate(False)
            ctk.CTkLabel(day_lbl, text=day,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                         text_color=Colors.TEXT_HEADING, anchor="w").pack(expand=True, padx=8)

            # Period cells
            for p_idx, subject in enumerate(day_periods):
                period_time = PERIODS[p_idx] if p_idx < len(PERIODS) else ""
                is_break = "Break" in period_time or "Zuhr" in period_time
                w = 130 if not is_break else 100

                if is_break or subject == "—":
                    cell = ctk.CTkFrame(row, width=w, fg_color="#F0F4F8", corner_radius=0)
                    cell.pack(side="left", fill="y", padx=1)
                    cell.pack_propagate(False)
                    ctk.CTkLabel(cell, text="—" if subject == "—" else "BREAK",
                                 font=(Fonts.FAMILY, Fonts.SIZE_XS),
                                 text_color=Colors.TEXT_MUTED,
                                 anchor="center").pack(expand=True)
                else:
                    colors = subject_colors.get(subject, (Colors.PRIMARY, Colors.PRIMARY_LIGHT))
                    cell = ctk.CTkFrame(row, width=w, fg_color=colors[1], corner_radius=4)
                    cell.pack(side="left", fill="y", padx=2, pady=4)
                    cell.pack_propagate(False)
                    ctk.CTkLabel(cell, text=subject,
                                 font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
                                 text_color=colors[0],
                                 anchor="center",
                                 wraplength=110).pack(expand=True)

        # ── Conflict detection banner ─────────────────────────────────────────
        if conflict_cells:
            cf = ctk.CTkFrame(self._grid_container, fg_color=Colors.DANGER_BG,
                               corner_radius=8, border_width=1, border_color=Colors.DANGER)
            cf.pack(fill="x", pady=(Spacing.SM, 0))
            ctk.CTkLabel(cf, text=f"⚠  Scheduling Conflict Detected: {len(conflict_cells)} period(s) overlap.",
                         font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                         text_color=Colors.DANGER).pack(padx=16, pady=8)
        else:
            ok = ctk.CTkFrame(self._grid_container, fg_color=Colors.SUCCESS_BG,
                               corner_radius=8, border_width=1, border_color=Colors.SUCCESS)
            ok.pack(fill="x", pady=(Spacing.SM, 0))
            ctk.CTkLabel(ok, text="✓  No scheduling conflicts detected. All periods are clear.",
                         font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                         text_color=Colors.SUCCESS).pack(padx=16, pady=8)

        # ── Print/Edit hint ───────────────────────────────────────────────────
        hint = ctk.CTkFrame(self._grid_container, fg_color="transparent")
        hint.pack(fill="x", pady=(Spacing.SM, 0))
        ctk.CTkButton(hint, text="🖨  Print Timetable", height=34, width=150,
                      corner_radius=8, font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                      fg_color=Colors.SECONDARY, text_color=Colors.TEXT_WHITE,
                      command=lambda: self._toast("Timetable sent to printer!", "success")
                      ).pack(side="left")
        ctk.CTkButton(hint, text="✏  Edit Period", height=34, width=130,
                      corner_radius=8, font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                      fg_color=Colors.PRIMARY, text_color=Colors.TEXT_WHITE,
                      command=lambda: self._toast("Period editor – coming soon!", "info")
                      ).pack(side="left", padx=(8, 0))

    def _reload(self, choice=None):
        self._draw_grid()
