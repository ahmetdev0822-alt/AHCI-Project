"""
app/screens/classes.py
Class & Section Management – Admin only. Blue & White theme.
"""

import customtkinter as ctk
from app.config import Colors, Fonts, Spacing, CARD_CORNER
from app.components.cards import SectionHeader, StatusBadge


class ClassesScreen(ctk.CTkFrame):
    def __init__(self, parent, state, navigate_fn, toast_fn):
        super().__init__(parent, fg_color=Colors.BG_MAIN, corner_radius=0)
        self._state    = state
        self._navigate = navigate_fn
        self._toast    = toast_fn
        self._selected_class = None
        self._build()

    def _build(self):
        pad = Spacing.XL

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=pad, pady=(pad, Spacing.SM))
        SectionHeader(
            toolbar, "Classes & Sections",
            f"{len(self._state.classes)} classes registered | Grades 1–10"
        ).pack(side="left", fill="y")
        ctk.CTkButton(
            toolbar, text="＋  Add Class",
            height=36, corner_radius=8,
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_DARK,
            text_color=Colors.TEXT_WHITE,
            command=self._open_add_form,
        ).pack(side="right")

        # Two-column layout: class list | class detail
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=pad, pady=(0, pad))
        body.columnconfigure(0, weight=0)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        # ── Left: Class cards list ───────────────────────────────────────────
        left = ctk.CTkFrame(body, fg_color=Colors.BG_CARD, corner_radius=10,
                             border_width=1, border_color=Colors.BORDER, width=280)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, Spacing.MD))
        left.pack_propagate(False)

        list_head = ctk.CTkFrame(left, fg_color=Colors.PRIMARY, corner_radius=0, height=44)
        list_head.pack(fill="x")
        list_head.pack_propagate(False)
        ctk.CTkLabel(list_head, text="  🏠  All Classes",
                     font=(Fonts.FAMILY, Fonts.SIZE_MD, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_WHITE, anchor="w").pack(side="left", padx=12)
        ctk.CTkLabel(list_head, text=f"{len(self._state.classes)}",
                     font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                     text_color="#90CAF9").pack(side="right", padx=12)

        self._list_scroll = ctk.CTkScrollableFrame(left, fg_color="transparent", corner_radius=0)
        self._list_scroll.pack(fill="both", expand=True)
        self._class_btns = {}
        self._draw_class_list()

        # ── Right: Detail panel ───────────────────────────────────────────────
        self._detail_panel = ctk.CTkFrame(body, fg_color="transparent", corner_radius=0)
        self._detail_panel.grid(row=0, column=1, sticky="nsew")

        # Initial: show first class
        if self._state.classes:
            self._show_class(self._state.classes[0])

    def _draw_class_list(self):
        for w in self._list_scroll.winfo_children():
            w.destroy()
        self._class_btns = {}
        for cls in self._state.classes:
            is_sel = (self._selected_class and
                      self._selected_class.get("id") == cls["id"])
            btn = ctk.CTkButton(
                self._list_scroll,
                text=f"  {cls['name']}\n  Room {cls['room']}",
                anchor="w", height=54, corner_radius=8,
                font=(Fonts.FAMILY, Fonts.SIZE_SM),
                fg_color=Colors.PRIMARY if is_sel else "transparent",
                text_color=Colors.TEXT_WHITE if is_sel else Colors.TEXT_PRIMARY,
                hover_color=Colors.PRIMARY_LIGHT if not is_sel else Colors.PRIMARY_DARK,
                command=lambda c=cls: self._show_class(c),
            )
            btn.pack(fill="x", padx=6, pady=2)
            self._class_btns[cls["id"]] = btn

    def _show_class(self, cls: dict):
        self._selected_class = cls
        for w in self._detail_panel.winfo_children():
            w.destroy()
        self._draw_class_list()

        scroll = ctk.CTkScrollableFrame(self._detail_panel, fg_color=Colors.BG_MAIN,
                                         corner_radius=0)
        scroll.pack(fill="both", expand=True)

        # Class header card
        hdr = ctk.CTkFrame(scroll, fg_color=Colors.SECONDARY, corner_radius=10, height=80)
        hdr.pack(fill="x", pady=(0, Spacing.MD))
        hdr.pack_propagate(False)

        hl = ctk.CTkFrame(hdr, fg_color="transparent")
        hl.place(relx=0.03, rely=0.5, anchor="w")
        ctk.CTkLabel(hl, text=f"🏠  {cls['name']}",
                     font=(Fonts.FAMILY, Fonts.SIZE_2XL, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_WHITE).pack(anchor="w")
        ctk.CTkLabel(hl, text=f"Grade {cls['grade']}  ·  Section {cls['section']}  ·  Room {cls['room']}",
                     font=(Fonts.FAMILY, Fonts.SIZE_SM),
                     text_color="#90CAF9").pack(anchor="w", pady=(2, 0))

        hr = ctk.CTkFrame(hdr, fg_color="transparent")
        hr.place(relx=0.97, rely=0.5, anchor="e")
        ctk.CTkLabel(hr, text=str(cls["students"]),
                     font=(Fonts.FAMILY, Fonts.SIZE_3XL, Fonts.WEIGHT_BOLD),
                     text_color="#90CAF9").pack()
        ctk.CTkLabel(hr, text="Total Strength",
                     font=(Fonts.FAMILY, Fonts.SIZE_XS),
                     text_color="#BBDEFB").pack()

        # Info grid
        info_grid = ctk.CTkFrame(scroll, fg_color="transparent")
        info_grid.pack(fill="x", pady=(0, Spacing.MD))
        info_grid.columnconfigure(0, weight=1)
        info_grid.columnconfigure(1, weight=1)

        for col, (label, val, color, bg) in enumerate([
            ("Class Teacher",  cls["class_teacher"], Colors.PRIMARY, Colors.PRIMARY_LIGHT),
            ("Room Number",    f"Room {cls['room']}", Colors.SECONDARY, Colors.INFO_BG),
        ]):
            card = ctk.CTkFrame(info_grid, fg_color=bg, corner_radius=8,
                                 border_width=1, border_color=color)
            card.grid(row=0, column=col,
                      padx=(0, Spacing.SM if col == 0 else 0), sticky="ew")
            ctk.CTkLabel(card, text=label,
                         font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
                         text_color=color, anchor="w").pack(anchor="w", padx=14, pady=(10, 0))
            ctk.CTkLabel(card, text=val,
                         font=(Fonts.FAMILY, Fonts.SIZE_MD, Fonts.WEIGHT_BOLD),
                         text_color=Colors.TEXT_HEADING, anchor="w").pack(anchor="w", padx=14, pady=(2, 10))

        # Action buttons
        act_row = ctk.CTkFrame(scroll, fg_color="transparent")
        act_row.pack(fill="x", pady=(0, Spacing.MD))
        
        def cmd_drill_down():
            # Explicitly force-inject the active class selection filter straight into the shared runtime global state dict
            if not hasattr(self._state, "filters"):
                self._state.filters = {}
            
            self._state.filters["class"] = cls["name"]
            
            # Now trigger the screen viewport shift over to the students template screen layout
            self._navigate("students")

        ctk.CTkButton(
            act_row, text="View Students →", height=40, corner_radius=8,
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            fg_color=Colors.PRIMARY, text_color=Colors.TEXT_WHITE,
            command=cmd_drill_down,
        ).pack(side="left", padx=(0, Spacing.SM))

        ctk.CTkButton(
            act_row, text="View Attendance →", height=40, corner_radius=8,
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            fg_color=Colors.SUCCESS, text_color=Colors.TEXT_WHITE,
            command=lambda: self._navigate("attendance"),
        ).pack(side="left", padx=(0, Spacing.SM))

        ctk.CTkButton(
            act_row, text="Edit Class Details", height=40, corner_radius=8,
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            fg_color=Colors.SECONDARY, text_color=Colors.TEXT_WHITE,
            command=lambda: self._open_edit_form(cls),
        ).pack(side="left", padx=(0, Spacing.SM))

    def _open_add_form(self):
        self._toast("Class creation form – coming soon!", "info")

    def _open_edit_form(self, cls):
        self._toast(f"Editing {cls['name']} – form ready!", "info")