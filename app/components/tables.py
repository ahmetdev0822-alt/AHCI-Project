"""
app/components/tables.py
Professional scrollable table with alternating rows, hover highlights,
column sorting, and inline action buttons.
"""

import customtkinter as ctk
from app.config import Colors, Fonts, Spacing, TABLE_ROW_HEIGHT


class DataTable(ctk.CTkFrame):
    """
    A fully-featured data table.

    Parameters
    ----------
    columns : list[dict]
        Each dict: {"key": str, "label": str, "width": int, "align": str}
    rows    : list[dict]
        Each row is a dict keyed by column keys.
    on_edit : callable(row_dict) | None
    on_delete : callable(row_dict) | None
    row_color_fn : callable(row_dict) -> str | None
        Return a hex color to override the row background.
    """

    def __init__(
        self, parent,
        columns:      list[dict],
        rows:         list[dict],
        on_edit=None,
        on_delete=None,
        on_view=None,
        row_color_fn=None,
        show_actions: bool = True,
        **kwargs
    ):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self._columns     = columns
        self._all_rows    = rows
        self._filtered    = rows
        self._on_edit     = on_edit
        self._on_delete   = on_delete
        self._on_view     = on_view
        self._color_fn    = row_color_fn
        self._show_actions= show_actions
        self._sort_key    = None
        self._sort_asc    = True

        self._build()

    def _build(self):
        # ── Search bar ──────────────────────────────────────────────────────
        search_row = ctk.CTkFrame(self, fg_color="transparent")
        search_row.pack(fill="x", pady=(0, Spacing.SM))

        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", self._on_search)

        search_entry = ctk.CTkEntry(
            search_row,
            placeholder_text="🔍  Search...",
            textvariable=self._search_var,
            height=36,
            corner_radius=8,
            font=(Fonts.FAMILY, Fonts.SIZE_MD),
            fg_color=Colors.BG_INPUT,
            border_color=Colors.BORDER,
            text_color=Colors.TEXT_PRIMARY,
            placeholder_text_color=Colors.TEXT_MUTED,
        )
        search_entry.pack(side="left", fill="x", expand=True)

        self._count_label = ctk.CTkLabel(
            search_row,
            text=f"{len(self._all_rows)} records",
            font=(Fonts.FAMILY, Fonts.SIZE_SM),
            text_color=Colors.TEXT_MUTED,
        )
        self._count_label.pack(side="right", padx=(10, 0))

        # ── Table container with scroll ──────────────────────────────────────
        container = ctk.CTkFrame(self, fg_color=Colors.BG_CARD,
                                  corner_radius=10, border_width=1,
                                  border_color=Colors.BORDER)
        container.pack(fill="both", expand=True)

        # Header
        self._header_frame = ctk.CTkFrame(container, fg_color=Colors.BG_TABLE_HEAD,
                                           corner_radius=0)
        self._header_frame.pack(fill="x")
        self._draw_header()

        # Scrollable body
        self._scroll = ctk.CTkScrollableFrame(container, fg_color="transparent",
                                               corner_radius=0)
        self._scroll.pack(fill="both", expand=True)

        self._draw_rows()

    def _draw_header(self):
        for w in self._header_frame.winfo_children():
            w.destroy()

        for col in self._columns:
            btn = ctk.CTkButton(
                self._header_frame,
                text=col["label"],
                font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                text_color=Colors.TEXT_HEADING,
                fg_color="transparent",
                hover_color=Colors.BG_HOVER,
                anchor=col.get("align", "w"),
                width=col["width"],
                height=TABLE_ROW_HEIGHT,
                corner_radius=0,
                command=lambda k=col["key"]: self._sort_by(k),
            )
            btn.pack(side="left")

        if self._show_actions:
            ctk.CTkLabel(
                self._header_frame, text="Actions",
                font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                text_color=Colors.TEXT_HEADING, width=130,
                anchor="center",
            ).pack(side="left")

    def _draw_rows(self):
        for w in self._scroll.winfo_children():
            w.destroy()

        if not self._filtered:
            ctk.CTkLabel(
                self._scroll, text="No records found.",
                font=(Fonts.FAMILY, Fonts.SIZE_MD),
                text_color=Colors.TEXT_MUTED,
            ).pack(pady=40)
            return

        for i, row in enumerate(self._filtered):
            bg = Colors.BG_TABLE_ROW if i % 2 == 0 else Colors.BG_TABLE_ALT
            if self._color_fn:
                custom_bg = self._color_fn(row)
                if custom_bg:
                    bg = custom_bg

            row_frame = ctk.CTkFrame(self._scroll, fg_color=bg, corner_radius=0,
                                      height=TABLE_ROW_HEIGHT)
            row_frame.pack(fill="x")
            row_frame.pack_propagate(False)

            # Separator line
            sep = ctk.CTkFrame(row_frame, height=1, fg_color=Colors.DIVIDER,
                                corner_radius=0)
            sep.pack(fill="x", side="bottom")

            for col in self._columns:
                val = str(row.get(col["key"], ""))
                lbl = ctk.CTkLabel(
                    row_frame, text=val,
                    font=(Fonts.FAMILY, Fonts.SIZE_SM),
                    text_color=Colors.TEXT_PRIMARY,
                    anchor=col.get("align", "w"),
                    width=col["width"],
                )
                lbl.pack(side="left", padx=(Spacing.SM, 0))

            if self._show_actions:
                act_frame = ctk.CTkFrame(row_frame, fg_color="transparent",
                                          width=130)
                act_frame.pack(side="left")
                act_frame.pack_propagate(False)

                captured = dict(row)
                if self._on_view:
                    ctk.CTkButton(
                        act_frame, text="View", width=36, height=26,
                        corner_radius=6,
                        font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
                        fg_color=Colors.INFO_BG, text_color=Colors.INFO,
                        hover_color=Colors.INFO,
                        command=lambda r=captured: self._safe_call(self._on_view, r),
                    ).pack(side="left", padx=(4, 2))

                if self._on_edit:
                    ctk.CTkButton(
                        act_frame, text="Edit", width=36, height=26,
                        corner_radius=6,
                        font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
                        fg_color=Colors.PRIMARY_LIGHT, text_color=Colors.PRIMARY,
                        hover_color=Colors.PRIMARY,
                        command=lambda r=captured: self._safe_call(self._on_edit, r),
                    ).pack(side="left", padx=2)

                if self._on_delete:
                    ctk.CTkButton(
                        act_frame, text="Del", width=34, height=26,
                        corner_radius=6,
                        font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
                        fg_color=Colors.DANGER_BG, text_color=Colors.DANGER,
                        hover_color=Colors.DANGER,
                        command=lambda r=captured: self._safe_call(self._on_delete, r),
                    ).pack(side="left", padx=(2, 4))

            # Hover highlight
            def _enter(e, f=row_frame, orig=bg):
                f.configure(fg_color=Colors.BG_HOVER)
            def _leave(e, f=row_frame, orig=bg):
                f.configure(fg_color=orig)
            row_frame.bind("<Enter>", _enter)
            row_frame.bind("<Leave>", _leave)

        self._count_label.configure(text=f"{len(self._filtered)} records")

    def _on_search(self, *args):
        q = self._search_var.get().lower().strip()
        if q:
            self._filtered = [
                r for r in self._all_rows
                if any(q in str(v).lower() for v in r.values())
            ]
        else:
            self._filtered = list(self._all_rows)
        self._draw_rows()

    def _sort_by(self, key: str):
        if self._sort_key == key:
            self._sort_asc = not self._sort_asc
        else:
            self._sort_key = key
            self._sort_asc = True
        self._filtered.sort(
            key=lambda r: str(r.get(key, "")),
            reverse=not self._sort_asc,
        )
        self._draw_rows()

    def refresh(self, rows: list[dict]):
        """Replace the data and redraw."""
        self._all_rows = rows
        self._filtered = rows
        self._search_var.set("")
        self._draw_rows()

    @staticmethod
    def _safe_call(fn, arg):
        if fn:
            try:
                fn(arg)
            except Exception as ex:
                print(f"[Table action error] {ex}")
