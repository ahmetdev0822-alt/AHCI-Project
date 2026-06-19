"""
app/screens/teachers.py
Teacher Management screen – Admin only.
"""

import customtkinter as ctk
from app.config import Colors, Fonts, Spacing, CARD_CORNER
from app.components.cards import SectionHeader, StatusBadge
from app.components.tables import DataTable


class TeachersScreen(ctk.CTkFrame):
    def __init__(self, parent, state, navigate_fn, toast_fn):
        super().__init__(parent, fg_color=Colors.BG_MAIN, corner_radius=0)
        self._state    = state
        self._navigate = navigate_fn
        self._toast    = toast_fn
        self._build()

    def _build(self):
        pad = Spacing.XL

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=pad, pady=(pad, Spacing.SM))

        SectionHeader(
            toolbar, "Teacher Management",
            f"Total {len(self._state.teachers)} teachers registered"
        ).pack(side="left", fill="y")

        ctk.CTkButton(
            toolbar, text="+  Add Teacher",
            height=36, corner_radius=8,
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_DARK,
            text_color=Colors.TEXT_WHITE,
            command=self._open_add_form,
        ).pack(side="right")

        # Stat chips
        chips = ctk.CTkFrame(self, fg_color="transparent")
        chips.pack(fill="x", padx=pad, pady=(0, Spacing.SM))
        chip_data = [
            ("Active",   sum(1 for t in self._state.teachers if t["status"]=="Active"),   Colors.SUCCESS, Colors.SUCCESS_BG),
            ("On Leave", sum(1 for t in self._state.teachers if t["status"]=="On Leave"), Colors.WARNING, Colors.WARNING_BG),
        ]
        for label, val, color, bg in chip_data:
            chip = ctk.CTkFrame(chips, fg_color=bg, corner_radius=8,
                                 border_width=1, border_color=color)
            chip.pack(side="left", padx=(0, Spacing.SM))
            ctk.CTkLabel(chip, text=f"{val} {label}",
                         font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                         text_color=color).pack(padx=12, pady=4)

        columns = [
            {"key": "id",              "label": "ID",          "width": 60,  "align": "w"},
            {"key": "name",            "label": "Teacher Name", "width": 200, "align": "w"},
            {"key": "subject",         "label": "Subject",      "width": 150, "align": "w"},
            {"key": "qualification",   "label": "Qualification","width": 160, "align": "w"},
            {"key": "experience",      "label": "Exp (Yrs)",    "width": 80,  "align": "center"},
            {"key": "phone",           "label": "Phone",        "width": 130, "align": "w"},
            {"key": "class_teacher_of","label": "Class Teacher","width": 110, "align": "w"},
            {"key": "status",          "label": "Status",       "width": 90,  "align": "center"},
        ]

        self._table = DataTable(
            self,
            columns=columns,
            rows=self._state.teachers,
            on_edit=self._open_edit_form,
            on_delete=self._delete_teacher,
            row_color_fn=lambda r: "#FFFBF0" if r.get("status") == "On Leave" else None,
        )
        self._table.pack(fill="both", expand=True, padx=pad, pady=(0, pad))

    def _open_add_form(self):
        TeacherForm(self, self._state, None, self._on_save)

    def _open_edit_form(self, row):
        TeacherForm(self, self._state, row, self._on_save)

    def _on_save(self, data: dict, is_new: bool):
        if is_new:
            data["id"] = f"T{len(self._state.teachers)+1:03d}"
            self._state.teachers.append(data)
            self._toast("Teacher added successfully!", "success")
        else:
            for i, t in enumerate(self._state.teachers):
                if t["id"] == data["id"]:
                    self._state.teachers[i] = data
                    break
            self._toast("Teacher record updated!", "success")
        self._table.refresh(self._state.teachers)

    def _delete_teacher(self, row):
        self._state.teachers = [t for t in self._state.teachers if t["id"] != row["id"]]
        self._table.refresh(self._state.teachers)
        self._toast(f"{row['name']} removed.", "warning")


class TeacherForm(ctk.CTkToplevel):
    def __init__(self, parent, state, data: dict | None, on_save):
        super().__init__(parent)
        self._state   = state
        self._data    = data
        self._on_save = on_save
        self._is_new  = data is None

        title = "Add New Teacher" if self._is_new else "Edit Teacher"
        self.title(title)
        self.geometry("520x580")
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color=Colors.BG_MAIN)
        self._build(title)

    def _build(self, title):
        header = ctk.CTkFrame(self, fg_color=Colors.SECONDARY, corner_radius=0, height=56)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text=f"  🎓  {title}",
                     font=(Fonts.FAMILY, Fonts.SIZE_XL, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_WHITE, anchor="w").pack(side="left", padx=16)

        scroll = ctk.CTkScrollableFrame(self, fg_color=Colors.BG_MAIN)
        scroll.pack(fill="both", expand=True)

        card = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=10,
                             border_width=1, border_color=Colors.BORDER)
        card.pack(fill="both", expand=True, padx=20, pady=16)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        d = self._data or {}

        def lbl(text):
            ctk.CTkLabel(inner, text=text,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                         text_color=Colors.TEXT_SECONDARY, anchor="w").pack(anchor="w", pady=(8,2))

        def ent(ph, val=""):
            e = ctk.CTkEntry(inner, placeholder_text=ph, height=38,
                              corner_radius=8, font=(Fonts.FAMILY, Fonts.SIZE_MD),
                              fg_color=Colors.BG_INPUT, border_color=Colors.BORDER,
                              text_color=Colors.TEXT_PRIMARY)
            e.pack(fill="x")
            if val: e.insert(0, val)
            return e

        lbl("Full Name *")
        self._name = ent("e.g. Ustaz Bilal Ahmed", d.get("name", ""))
        lbl("Subject Specialization *")
        self._subject = ent("e.g. Mathematics", d.get("subject", ""))
        lbl("Qualification")
        self._qual = ent("e.g. M.Sc Mathematics", d.get("qualification", ""))
        lbl("Phone")
        self._phone = ent("e.g. 0321-1234567", d.get("phone", ""))
        lbl("Email")
        self._email = ent("e.g. teacher@darearqam.edu.pk", d.get("email", ""))
        lbl("Experience (years)")
        self._exp = ent("e.g. 5", str(d.get("experience", "")))
        lbl("Class Teacher Of (optional)")
        class_names = ["—"] + sorted({c["name"] for c in self._state.classes})
        self._class_var = ctk.StringVar(value=d.get("class_teacher_of", "—"))
        ctk.CTkOptionMenu(
            inner, values=class_names, variable=self._class_var,
            width=200, height=38, font=(Fonts.FAMILY, Fonts.SIZE_SM),
            fg_color=Colors.BG_INPUT, button_color=Colors.PRIMARY,
            text_color=Colors.TEXT_PRIMARY,
        ).pack(anchor="w")
        lbl("Status")
        self._status_var = ctk.StringVar(value=d.get("status", "Active"))
        sf = ctk.CTkFrame(inner, fg_color="transparent")
        sf.pack(anchor="w")
        for s in ["Active", "On Leave"]:
            ctk.CTkRadioButton(sf, text=s, variable=self._status_var, value=s,
                                font=(Fonts.FAMILY, Fonts.SIZE_MD),
                                fg_color=Colors.PRIMARY).pack(side="left", padx=(0, 16))

        btn_row = ctk.CTkFrame(self, fg_color=Colors.BG_CARD, corner_radius=0,
                                height=60, border_width=1, border_color=Colors.BORDER)
        btn_row.pack(fill="x", side="bottom")
        btn_row.pack_propagate(False)
        ctk.CTkButton(btn_row, text="Cancel", width=100, height=36, corner_radius=8,
                      fg_color=Colors.BG_INPUT, text_color=Colors.TEXT_SECONDARY,
                      hover_color=Colors.BG_HOVER, command=self.destroy
                      ).pack(side="right", padx=(8, 16), pady=12)
        ctk.CTkButton(btn_row, text="Save Teacher", width=140, height=36, corner_radius=8,
                      fg_color=Colors.SECONDARY, hover_color=Colors.SECONDARY_DARK,
                      text_color=Colors.TEXT_WHITE, command=self._save
                      ).pack(side="right", padx=(0, 4), pady=12)

    def _save(self):
        name = self._name.get().strip()
        if not name:
            return
        try:
            exp = int(self._exp.get().strip())
        except ValueError:
            exp = 0
        data = {
            "id":               self._data["id"] if self._data else "",
            "name":             name,
            "subject":          self._subject.get().strip(),
            "qualification":    self._qual.get().strip(),
            "phone":            self._phone.get().strip(),
            "email":            self._email.get().strip(),
            "experience":       exp,
            "class_teacher_of": self._class_var.get(),
            "status":           self._status_var.get(),
        }
        self._on_save(data, self._is_new)
        self.destroy()
