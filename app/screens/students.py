"""
app/screens/students.py
Student Management – Admin Only. Blue & White theme.
Full CRUD backed by local SQLite persistence layer with multi-state support.
"""

import customtkinter as ctk
from app.config import Colors, Fonts, Spacing, CARD_CORNER
from app.components.cards import SectionHeader, StatusBadge
from app.components.tables import DataTable
from app.components.state_view import StateView, StateSwitchDemoBar


class StudentsScreen(ctk.CTkFrame):
    def __init__(self, parent, state, navigate_fn, toast_fn):
        super().__init__(parent, fg_color=Colors.BG_MAIN, corner_radius=0)
        self._state    = state
        self._navigate = navigate_fn
        self._toast    = toast_fn
        
        if not hasattr(self._state, "filters"):
            self._state.filters = {}
        
        initial_class_filter = self._state.filters.get("class", "All")
        self._class_filter = ctk.StringVar(value=initial_class_filter)
        
        self._build()
        
        if initial_class_filter != "All":
            self._apply_filter()

    def _build(self):
        pad = Spacing.XL

        top_row = ctk.CTkFrame(self, fg_color="transparent")
        top_row.pack(fill="x", padx=pad, pady=(pad, 0))
        SectionHeader(
            top_row, "Student Management",
            f"Total {len(self._state.students)} enrolled students in SQLite registry",
        ).pack(side="left", fill="y")
        StateSwitchDemoBar(top_row, on_switch_fn=self._on_state_switch).pack(side="right")

        # Toolbar
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=pad, pady=(Spacing.SM, Spacing.SM))

        # Filter: Class
        ctk.CTkLabel(toolbar, text="Filter Class:", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_SECONDARY).pack(side="left", padx=(0, 4))
        class_names = ["All"] + sorted({s["class"] for s in self._state.students})
        
        ctk.CTkOptionMenu(
            toolbar,
            values=class_names,
            variable=self._class_filter,
            width=150, height=34,
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            fg_color=Colors.BG_CARD,
            button_color=Colors.PRIMARY,
            button_hover_color=Colors.PRIMARY_DARK,
            text_color=Colors.TEXT_PRIMARY,
            command=self._on_dropdown_filter_changed,
        ).pack(side="left", padx=(0, 14))

        # Search
        self._search_var = ctk.StringVar()
        search = ctk.CTkEntry(
            toolbar,
            textvariable=self._search_var,
            placeholder_text="🔍  Search student name or roll...",
            height=34, width=220, corner_radius=8,
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            fg_color=Colors.BG_INPUT, border_color=Colors.BORDER,
            text_color=Colors.TEXT_PRIMARY,
        )
        search.pack(side="left")
        self._search_var.trace_add("write", lambda *_: self._apply_filter())

        ctk.CTkButton(
            toolbar, text="＋  Add Student",
            height=36, corner_radius=8,
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_DARK,
            text_color=Colors.TEXT_WHITE,
            command=self._open_add_form,
        ).pack(side="right")

        # ── StateView Container ───────────────────────────────────────────────
        self._state_view = StateView(
            self,
            on_retry=lambda: self._on_state_switch("content"),
            on_action=self._open_add_form,
        )
        self._state_view.pack(fill="both", expand=True)

        self._render_table_content(self._state_view.content_area)

    def _on_state_switch(self, mode: str):
        if mode == "content":
            self._state_view.set_state("content")
        elif mode == "empty":
            self._state_view.set_state("empty", title="No Students Found", message="No active student records matched the current class or search filter.", action_text="＋ Add New Student")
        elif mode == "loading":
            self._state_view.set_state("loading", title="Fetching Student Registry...", message="Loading student demographics, guardian records, and attendance links from SQLite.")
        elif mode == "error":
            self._state_view.set_state("error", title="Student Database Lock", message="Failed to acquire read lock on SQLite data tables.", error_details="ERR_SQLITE_BUSY_LOCK (Code 503)")
        elif mode == "offline":
            self._state_view.set_state("offline", title="Offline Student Management", message="Operating on local encrypted database. All student modifications persist permanently.", action_text="Continue Editing")

    def _render_table_content(self, parent):
        pad = Spacing.XL

        # Summary Chips
        chips = ctk.CTkFrame(parent, fg_color="transparent")
        chips.pack(fill="x", padx=pad, pady=(0, Spacing.SM))
        total   = len(self._state.students)
        active  = sum(1 for s in self._state.students if s["status"] == "Active")
        male    = sum(1 for s in self._state.students if s["gender"] == "M")
        female  = sum(1 for s in self._state.students if s["gender"] == "F")
        for label, val, color, bg in [
            ("Total",   str(total),  Colors.PRIMARY, Colors.PRIMARY_LIGHT),
            ("Active",  str(active), Colors.SUCCESS, Colors.SUCCESS_BG),
            ("Male",    str(male),   Colors.INFO,    Colors.INFO_BG),
            ("Female",  str(female), Colors.ACCENT,  "#E0F2F1"),
        ]:
            chip = ctk.CTkFrame(chips, fg_color=bg, corner_radius=8, border_width=1, border_color=color)
            chip.pack(side="left", padx=(0, Spacing.SM))
            ctk.CTkLabel(chip, text=f"  {val}  {label}  ", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=color).pack(padx=4, pady=4)

        columns = [
            {"key": "id",          "label": "ID",           "width": 60,  "align": "w"},
            {"key": "name",        "label": "Student Name",  "width": 190, "align": "w"},
            {"key": "class",       "label": "Class",         "width": 110, "align": "w"},
            {"key": "roll_no",     "label": "Roll #",        "width": 60,  "align": "center"},
            {"key": "gender",      "label": "Gender",        "width": 70,  "align": "center"},
            {"key": "parent_name", "label": "Parent/Guardian","width": 170, "align": "w"},
            {"key": "phone",       "label": "Phone",         "width": 130, "align": "w"},
            {"key": "status",      "label": "Status",        "width": 80,  "align": "center"},
        ]

        self._table = DataTable(
            parent,
            columns=columns,
            rows=self._state.students,
            on_edit=self._open_edit_form,
            on_delete=self._delete_student,
            on_view=self._view_student,
            row_color_fn=lambda r: "#F7FAFC" if r.get("status") == "Inactive" else None,
        )
        self._table.pack(fill="both", expand=True, padx=pad, pady=(0, pad))

    def _on_dropdown_filter_changed(self, choice):
        self._state.filters["class"] = choice
        self._apply_filter()

    def _apply_filter(self, choice=None):
        cls    = self._class_filter.get()
        query  = self._search_var.get().strip().lower()
        rows   = self._state.students
        if cls != "All":
            rows = [s for s in rows if s["class"] == cls]
        if query:
            rows = [s for s in rows if query in s["name"].lower()
                    or query in s.get("roll_no", "").lower()]
        self._table.refresh(rows)

    def _open_add_form(self):
        StudentForm(self, self._state, None, self._on_save)

    def _open_edit_form(self, row):
        StudentForm(self, self._state, row, self._on_save)

    def _view_student(self, row):
        StudentDetailDialog(self, self._state, row)

    def _on_save(self, data: dict, is_new: bool):
        if is_new:
            data["id"] = f"S{len(self._state.students)+1:03d}"
            self._state.save_student(data)
            self._toast(f"Student {data['name']} added to SQLite!", "success")
        else:
            self._state.save_student(data)
            self._toast(f"Student {data['name']} updated in SQLite!", "success")
        self._apply_filter()

    def _delete_student(self, row):
        ConfirmDialog(
            self,
            title="Delete Student",
            message=f"Are you sure you want to remove {row['name']}?\nThis action will persist to the local database.",
            on_confirm=lambda: self._confirm_delete(row),
        )

    def _confirm_delete(self, row):
        self._state.delete_student(row["id"])
        self._apply_filter()
        self._toast(f"Student {row['name']} removed from database.", "warning")


class StudentForm(ctk.CTkToplevel):
    def __init__(self, parent, state, data: dict | None, on_save):
        super().__init__(parent)
        self._state   = state
        self._data    = data
        self._on_save = on_save
        self._is_new  = data is None

        title = "Add New Student" if self._is_new else f"Edit Student – {data.get('name','')}"
        self.title(title)
        self.geometry("560x640")
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color=Colors.BG_MAIN)
        self._build(title)

    def _build(self, title):
        header = ctk.CTkFrame(self, fg_color=Colors.PRIMARY, corner_radius=0, height=56)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(
            header, text=f"  👤  {title}",
            font=(Fonts.FAMILY, Fonts.SIZE_XL, Fonts.WEIGHT_BOLD),
            text_color=Colors.TEXT_WHITE, anchor="w",
        ).pack(side="left", padx=16, pady=10)

        scroll = ctk.CTkScrollableFrame(self, fg_color=Colors.BG_MAIN)
        scroll.pack(fill="both", expand=True)

        card = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=10, border_width=1, border_color=Colors.BORDER)
        card.pack(fill="both", expand=True, padx=20, pady=16)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        d = self._data or {}

        def label(text):
            ctk.CTkLabel(inner, text=text, font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_SECONDARY, anchor="w").pack(anchor="w", pady=(10, 2))

        def entry(placeholder, value=""):
            e = ctk.CTkEntry(inner, placeholder_text=placeholder, height=38, corner_radius=8, font=(Fonts.FAMILY, Fonts.SIZE_MD), fg_color=Colors.BG_INPUT, border_color=Colors.BORDER, text_color=Colors.TEXT_PRIMARY)
            e.insert(0, str(value))
            e.pack(fill="x", pady=(0, 2))
            return e

        label("Full Name *")
        self._name = entry("e.g. Ahmed Hassan Khan", d.get("name", ""))

        label("Class *")
        class_names = sorted({s["name"] for s in self._state.classes}) or ["Class 8-A"]
        self._class_var = ctk.StringVar(value=d.get("class", class_names[0] if class_names else ""))
        ctk.CTkOptionMenu(inner, values=class_names, variable=self._class_var, width=220, height=38, font=(Fonts.FAMILY, Fonts.SIZE_SM), fg_color=Colors.BG_INPUT, button_color=Colors.PRIMARY, text_color=Colors.TEXT_PRIMARY).pack(anchor="w")

        label("Roll Number")
        self._roll_entry = entry("e.g. 12", d.get("roll_no", ""))

        label("Gender")
        self._gender_var = ctk.StringVar(value=d.get("gender", "M"))
        gf = ctk.CTkFrame(inner, fg_color="transparent")
        gf.pack(anchor="w")
        for g, lbl in [("M", "Male"), ("F", "Female")]:
            ctk.CTkRadioButton(gf, text=lbl, variable=self._gender_var, value=g, font=(Fonts.FAMILY, Fonts.SIZE_MD), fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_DARK).pack(side="left", padx=(0, 20))

        label("Parent / Guardian Name *")
        self._parent = entry("e.g. Khan Bahadur Ali", d.get("parent_name", ""))

        label("Phone Number")
        self._phone = entry("e.g. 0321-1234567", d.get("phone", ""))

        label("Email (Optional)")
        self._email = entry("e.g. parent@gmail.com", d.get("email", ""))

        label("Status")
        self._status_var = ctk.StringVar(value=d.get("status", "Active"))
        sf = ctk.CTkFrame(inner, fg_color="transparent")
        sf.pack(anchor="w")
        for s in ["Active", "Inactive"]:
            ctk.CTkRadioButton(sf, text=s, variable=self._status_var, value=s, font=(Fonts.FAMILY, Fonts.SIZE_MD), fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_DARK).pack(side="left", padx=(0, 20))

        btn_row = ctk.CTkFrame(self, fg_color=Colors.BG_CARD, corner_radius=0, height=60, border_width=1, border_color=Colors.BORDER)
        btn_row.pack(fill="x", side="bottom")
        btn_row.pack_propagate(False)

        ctk.CTkButton(btn_row, text="Cancel", width=100, height=36, corner_radius=8, fg_color=Colors.BG_INPUT, text_color=Colors.TEXT_SECONDARY, command=self.destroy).pack(side="right", padx=(8, 16), pady=12)
        ctk.CTkButton(btn_row, text="💾  Save Student", width=150, height=36, corner_radius=8, fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_DARK, text_color=Colors.TEXT_WHITE, command=self._save).pack(side="right", padx=(0, 4), pady=12)

    def _save(self):
        name = self._name.get().strip()
        pname = self._parent.get().strip()
        if not name or not pname:
            return
        data = {
            "id":             self._data["id"] if self._data else "",
            "name":           name,
            "class":          self._class_var.get(),
            "roll_no":        self._roll_entry.get().strip() or "—",
            "gender":         self._gender_var.get(),
            "parent_name":    pname,
            "phone":          self._phone.get().strip(),
            "email":          self._email.get().strip(),
            "admission_date": self._data.get("admission_date", "2025-01-01") if self._data else "2025-01-01",
            "status":         self._status_var.get(),
        }
        self._on_save(data, self._is_new)
        self.destroy()


class StudentDetailDialog(ctk.CTkToplevel):
    def __init__(self, parent, state, data: dict):
        super().__init__(parent)
        self.title(f"Student Profile – {data['name']}")
        self.geometry("500x480")
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color=Colors.BG_MAIN)

        header = ctk.CTkFrame(self, fg_color=Colors.PRIMARY, corner_radius=0, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text=f"  👤  {data['name']}", font=(Fonts.FAMILY, Fonts.SIZE_XL, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_WHITE, anchor="w").pack(side="left", padx=16)

        card = ctk.CTkFrame(self, fg_color=Colors.BG_CARD, corner_radius=10, border_width=1, border_color=Colors.BORDER)
        card.pack(fill="both", expand=True, padx=20, pady=16)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        for label, val in [
            ("Student ID", data["id"]),
            ("Class", data["class"]),
            ("Roll Number", data.get("roll_no", "—")),
            ("Gender", "Male" if data.get("gender") == "M" else "Female"),
            ("Parent / Guardian", data.get("parent_name", "—")),
            ("Contact Phone", data.get("phone", "—")),
            ("Email", data.get("email", "—")),
            ("Admission Date", data.get("admission_date", "—")),
            ("Status", data.get("status", "Active")),
        ]:
            row = ctk.CTkFrame(inner, fg_color="transparent")
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=label, width=140, font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_SECONDARY, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=str(val), font=(Fonts.FAMILY, Fonts.SIZE_SM), text_color=Colors.TEXT_PRIMARY, anchor="w").pack(side="left")

        ctk.CTkButton(self, text="Close", width=100, height=36, corner_radius=8, fg_color=Colors.PRIMARY, text_color=Colors.TEXT_WHITE, command=self.destroy).pack(pady=(0, 16))


class ConfirmDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message, on_confirm):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color=Colors.BG_MAIN)

        card = ctk.CTkFrame(self, fg_color=Colors.BG_CARD, corner_radius=10, border_width=1, border_color=Colors.BORDER)
        card.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(card, text="⚠  " + title, font=(Fonts.FAMILY, Fonts.SIZE_LG, Fonts.WEIGHT_BOLD), text_color=Colors.DANGER).pack(anchor="w", padx=20, pady=(16, 8))
        ctk.CTkLabel(card, text=message, font=(Fonts.FAMILY, Fonts.SIZE_SM), text_color=Colors.TEXT_SECONDARY, wraplength=340, justify="left").pack(anchor="w", padx=20, pady=(0, 16))

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(0, 16))
        ctk.CTkButton(btn_row, text="Cancel", width=90, height=32, corner_radius=6, fg_color=Colors.BG_INPUT, text_color=Colors.TEXT_SECONDARY, command=self.destroy).pack(side="right", padx=(8, 0))
        ctk.CTkButton(btn_row, text="Confirm Delete", width=120, height=32, corner_radius=6, font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), fg_color=Colors.DANGER, hover_color="#B71C1C", text_color=Colors.TEXT_WHITE, command=lambda: (on_confirm(), self.destroy())).pack(side="right")