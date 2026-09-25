"""
app/screens/classes.py
Class & Section Management – Admin only. Blue & White theme.
Backed by SQLite persistence layer with multi-state support.
"""

import customtkinter as ctk
from app.config import Colors, Fonts, Spacing, CARD_CORNER
from app.components.cards import SectionHeader, StatusBadge
from app.components.state_view import StateView, StateSwitchDemoBar
from app.db.database import db


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

        top_row = ctk.CTkFrame(self, fg_color="transparent")
        top_row.pack(fill="x", padx=pad, pady=(pad, 0))
        SectionHeader(
            top_row, "Classes & Sections",
            f"{len(self._state.classes)} academic rooms in SQLite database | Grades 1–10"
        ).pack(side="left", fill="y")
        StateSwitchDemoBar(top_row, on_switch_fn=self._on_state_switch).pack(side="right")

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=pad, pady=(Spacing.SM, Spacing.SM))
        ctk.CTkButton(
            toolbar, text="＋  Add Class Section",
            height=36, corner_radius=8,
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_DARK,
            text_color=Colors.TEXT_WHITE,
            command=self._open_add_form,
        ).pack(side="right")

        # StateView Container
        self._state_view = StateView(
            self,
            on_retry=lambda: self._on_state_switch("content"),
            on_action=self._open_add_form,
        )
        self._state_view.pack(fill="both", expand=True)

        self._render_classes_layout(self._state_view.content_area)

    def _on_state_switch(self, mode: str):
        if mode == "content":
            self._state_view.set_state("content")
        elif mode == "empty":
            self._state_view.set_state("empty", title="No Classes Configured", message="No active classrooms found in the institutional registry.", action_text="＋ Add Class Section")
        elif mode == "loading":
            self._state_view.set_state("loading", title="Retrieving Class Structures...", message="Loading room allocations, class teachers, and student capacities from SQLite.")
        elif mode == "error":
            self._state_view.set_state("error", title="Class Allocation Fault", message="Database schema mismatch in classroom entity relation.", error_details="ERR_SQLITE_CLASSES_REL_FAIL (Code 502)")
        elif mode == "offline":
            self._state_view.set_state("offline", title="Offline Classroom Registry", message="Operating from local SQLite storage. All section updates are persisted.", action_text="Manage Offline Classes")

    def _render_classes_layout(self, parent):
        pad = Spacing.XL

        body = ctk.CTkFrame(parent, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=pad, pady=(0, pad))
        body.columnconfigure(0, weight=0)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        # Left: Class cards list
        left = ctk.CTkFrame(body, fg_color=Colors.BG_CARD, corner_radius=10,
                             border_width=1, border_color=Colors.BORDER, width=280)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, Spacing.MD))
        left.pack_propagate(False)

        list_head = ctk.CTkFrame(left, fg_color=Colors.PRIMARY, corner_radius=0, height=44)
        list_head.pack(fill="x")
        list_head.pack_propagate(False)
        ctk.CTkLabel(list_head, text="  🏫  All Class Sections",
                     font=(Fonts.FAMILY, Fonts.SIZE_MD, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_WHITE, anchor="w").pack(side="left", padx=12)
        ctk.CTkLabel(list_head, text=f"{len(self._state.classes)}",
                     font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                     text_color="#90CAF9").pack(side="right", padx=12)

        self._list_scroll = ctk.CTkScrollableFrame(left, fg_color="transparent", corner_radius=0)
        self._list_scroll.pack(fill="both", expand=True, pady=4)
        self._class_btns = {}

        self._detail_panel = ctk.CTkFrame(body, fg_color="transparent", corner_radius=0)
        self._detail_panel.grid(row=0, column=1, sticky="nsew")

        self._draw_class_list()
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
                text=f"  {cls['name']}\n  Room {cls.get('room', '101')}  ·  {cls.get('students', 0)} Students",
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

        scroll = ctk.CTkScrollableFrame(self._detail_panel, fg_color=Colors.BG_MAIN, corner_radius=0)
        scroll.pack(fill="both", expand=True)

        # Header Card
        hcard = ctk.CTkFrame(scroll, fg_color=Colors.SECONDARY, corner_radius=12, height=110)
        hcard.pack(fill="x", pady=(0, Spacing.MD))
        hcard.pack_propagate(False)

        hi = ctk.CTkFrame(hcard, fg_color="transparent")
        hi.place(relx=0.03, rely=0.5, anchor="w")
        ctk.CTkLabel(hi, text=f"  {cls['name']}", font=(Fonts.FAMILY, Fonts.SIZE_3XL, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_WHITE).pack(anchor="w")
        ctk.CTkLabel(hi, text=f"  Grade {cls.get('grade', 1)}  ·  Section {cls.get('section', 'A')}  ·  Dar-e-Arqam School", font=(Fonts.FAMILY, Fonts.SIZE_SM), text_color="#90CAF9").pack(anchor="w", pady=(2, 0))

        # Class stats grid
        info_grid = ctk.CTkFrame(scroll, fg_color="transparent")
        info_grid.pack(fill="x", pady=(0, Spacing.MD))
        info_grid.columnconfigure(0, weight=1)
        info_grid.columnconfigure(1, weight=1)

        for col, (label, val, color, bg) in enumerate([
            ("Class Homeroom Teacher",  cls.get("class_teacher", "Ustaz Bilal Ahmed"), Colors.PRIMARY, Colors.PRIMARY_LIGHT),
            ("Allocated Classroom",     f"Room {cls.get('room', '101')}", Colors.SECONDARY, Colors.INFO_BG),
        ]):
            card = ctk.CTkFrame(info_grid, fg_color=bg, corner_radius=8, border_width=1, border_color=color)
            card.grid(row=0, column=col, padx=(0, Spacing.SM if col == 0 else 0), sticky="ew")
            ctk.CTkLabel(card, text=label, font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD), text_color=color, anchor="w").pack(anchor="w", padx=14, pady=(10, 0))
            ctk.CTkLabel(card, text=val, font=(Fonts.FAMILY, Fonts.SIZE_MD, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_HEADING, anchor="w").pack(anchor="w", padx=14, pady=(2, 10))

        # Action buttons
        act_row = ctk.CTkFrame(scroll, fg_color="transparent")
        act_row.pack(fill="x", pady=(0, Spacing.MD))

        def cmd_drill_down():
            if not hasattr(self._state, "filters"):
                self._state.filters = {}
            self._state.filters["class"] = cls["name"]
            self._navigate("students")

        ctk.CTkButton(
            act_row, text="View Students Roster →", height=38, corner_radius=8,
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            fg_color=Colors.PRIMARY, text_color=Colors.TEXT_WHITE,
            command=cmd_drill_down,
        ).pack(side="left", padx=(0, Spacing.SM))

        ctk.CTkButton(
            act_row, text="Mark Attendance →", height=38, corner_radius=8,
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            fg_color=Colors.SUCCESS, text_color=Colors.TEXT_WHITE,
            command=lambda: self._navigate("attendance"),
        ).pack(side="left", padx=(0, Spacing.SM))

    def _open_add_form(self):
        win = ctk.CTkToplevel(self)
        win.title("Add New Class Section")
        win.geometry("450x420")
        win.configure(fg_color=Colors.BG_CARD)
        win.grab_set()
        win.transient(self.winfo_toplevel())

        pad = Spacing.XL
        ctk.CTkLabel(win, text="🏫  Add Class Section", font=(Fonts.FAMILY, Fonts.SIZE_XL, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_HEADING).pack(anchor="w", padx=pad, pady=(pad, 4))

        ctk.CTkLabel(win, text="Class Name:", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_SECONDARY).pack(anchor="w", padx=pad, pady=(4, 2))
        name_e = ctk.CTkEntry(win, height=34, fg_color=Colors.BG_INPUT, border_color=Colors.BORDER, text_color=Colors.TEXT_PRIMARY, placeholder_text="e.g. Class 7-B")
        name_e.pack(fill="x", padx=pad, pady=(0, 8))

        ctk.CTkLabel(win, text="Room Number:", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_SECONDARY).pack(anchor="w", padx=pad, pady=(4, 2))
        room_e = ctk.CTkEntry(win, height=34, fg_color=Colors.BG_INPUT, border_color=Colors.BORDER, text_color=Colors.TEXT_PRIMARY, placeholder_text="e.g. 702")
        room_e.pack(fill="x", padx=pad, pady=(0, 8))

        ctk.CTkLabel(win, text="Homeroom Teacher:", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_SECONDARY).pack(anchor="w", padx=pad, pady=(4, 2))
        teach_e = ctk.CTkEntry(win, height=34, fg_color=Colors.BG_INPUT, border_color=Colors.BORDER, text_color=Colors.TEXT_PRIMARY, placeholder_text="e.g. Ustaza Amina Sheikh")
        teach_e.pack(fill="x", padx=pad, pady=(0, 16))

        def save():
            cname = name_e.get().strip()
            if not cname:
                self._toast("Validation Error: Class section name is required.", "error")
                return
            new_c = {
                "id": f"CL{len(self._state.classes)+1:02d}",
                "name": cname,
                "grade": 7,
                "section": "B",
                "class_teacher": teach_e.get().strip() or "Ustaz Bilal Ahmed",
                "room": room_e.get().strip() or "101",
                "students": 30,
            }
            db.save_class(new_c)
            self._state.classes = db.get_all_classes()
            win.destroy()
            self._draw_class_list()
            self._show_class(new_c)
            self._toast(f"Class {cname} saved to SQLite database!", "success")

        btn_row = ctk.CTkFrame(win, fg_color="transparent")
        btn_row.pack(fill="x", padx=pad, pady=(0, pad))
        ctk.CTkButton(btn_row, text="Cancel", fg_color=Colors.BG_INPUT, text_color=Colors.TEXT_SECONDARY, height=36, command=win.destroy).pack(side="left")
        ctk.CTkButton(btn_row, text="✓  Create Section", fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_DARK, font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), height=36, command=save).pack(side="right")