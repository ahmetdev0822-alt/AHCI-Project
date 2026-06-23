"""
app/components/cards.py
Reusable card widgets – Blue & White theme.
MetricCard, AlertCard, QuickActionCard, SectionHeader, StatusBadge
"""

import customtkinter as ctk
from app.config import Colors, Fonts, Spacing, CARD_CORNER


class MetricCard(ctk.CTkFrame):
    """
    A stat/KPI card:
      ┌─────────────────────────────┐
      │  [top accent strip]         │
      │  [icon]   [title]           │
      │  [big value]                │
      │  [sub-label]   [trend]      │
      └─────────────────────────────┘
    """

    def __init__(
        self, parent,
        title:      str,
        value:      str,
        icon:       str  = "📊",
        sub_label:  str  = "",
        accent:     str  = Colors.PRIMARY,
        trend:      str  = "",
        trend_color:str  = Colors.SUCCESS,
        **kwargs
    ):
        super().__init__(
            parent,
            fg_color=Colors.BG_CARD,
            corner_radius=CARD_CORNER,
            border_width=1,
            border_color=Colors.BORDER,
            **kwargs
        )
        self._accent = accent
        self._build(title, value, icon, sub_label, accent, trend, trend_color)
        self._bind_hover()

    def _build(self, title, value, icon, sub_label, accent, trend, trend_color):
        # Top accent strip
        strip = ctk.CTkFrame(self, height=4, fg_color=accent, corner_radius=0)
        strip.pack(fill="x", side="top")

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=Spacing.LG, pady=Spacing.LG)

        # Row 1: icon + title
        row1 = ctk.CTkFrame(body, fg_color="transparent")
        row1.pack(fill="x")

        icon_bg = ctk.CTkFrame(row1, width=38, height=38,
                                fg_color=self._alpha_color(accent),
                                corner_radius=8)
        icon_bg.pack(side="left")
        icon_bg.pack_propagate(False)
        ctk.CTkLabel(icon_bg, text=icon,
                     font=(Fonts.FAMILY, Fonts.SIZE_LG),
                     text_color=accent).pack(expand=True)

        ctk.CTkLabel(row1, text=title,
                     font=(Fonts.FAMILY, Fonts.SIZE_SM),
                     text_color=Colors.TEXT_SECONDARY,
                     anchor="w").pack(side="left", padx=(10, 0))

        # Row 2: big value
        ctk.CTkLabel(body, text=value,
                     font=(Fonts.FAMILY, Fonts.SIZE_4XL, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_HEADING,
                     anchor="w").pack(fill="x", pady=(8, 0))

        # Row 3: sub-label + trend
        row3 = ctk.CTkFrame(body, fg_color="transparent")
        row3.pack(fill="x", pady=(2, 0))
        if sub_label:
            ctk.CTkLabel(row3, text=sub_label,
                         font=(Fonts.FAMILY, Fonts.SIZE_XS),
                         text_color=Colors.TEXT_MUTED,
                         anchor="w").pack(side="left")
        if trend:
            ctk.CTkLabel(row3, text=trend,
                         font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
                         text_color=trend_color,
                         anchor="e").pack(side="right")

    @staticmethod
    def _alpha_color(hex_color: str) -> str:
        """Return a very light tint of the given hex color."""
        mapping = {
            Colors.PRIMARY:  Colors.PRIMARY_LIGHT,
            Colors.SUCCESS:  Colors.SUCCESS_BG,
            Colors.WARNING:  Colors.WARNING_BG,
            Colors.DANGER:   Colors.DANGER_BG,
            Colors.INFO:     Colors.INFO_BG,
            Colors.ACCENT:   "#E0F2F1",
        }
        return mapping.get(hex_color, Colors.BG_INPUT)

    def _bind_hover(self):
        def on_enter(e):
            self.configure(border_color=self._accent)
        def on_leave(e):
            self.configure(border_color=Colors.BORDER)
        self.bind("<Enter>", on_enter)
        self.bind("<Leave>", on_leave)


class AlertCard(ctk.CTkFrame):
    """A warning / alert box with icon and message."""
    STYLES = {
        "warning": (Colors.WARNING, Colors.WARNING_BG, "⚠"),
        "danger":  (Colors.DANGER,  Colors.DANGER_BG,  "✕"),
        "success": (Colors.SUCCESS, Colors.SUCCESS_BG,  "✓"),
        "info":    (Colors.INFO,    Colors.INFO_BG,     "ℹ"),
    }

    def __init__(self, parent, title: str, message: str,
                 kind: str = "warning", **kwargs):
        accent, bg, icon = self.STYLES.get(kind, self.STYLES["info"])
        super().__init__(parent, fg_color=bg, corner_radius=CARD_CORNER,
                         border_width=1, border_color=accent, **kwargs)
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=14, pady=10)

        head = ctk.CTkFrame(body, fg_color="transparent")
        head.pack(fill="x")
        ctk.CTkLabel(head, text=f"{icon}  {title}",
                     font=(Fonts.FAMILY, Fonts.SIZE_MD, Fonts.WEIGHT_BOLD),
                     text_color=accent).pack(side="left")
        ctk.CTkLabel(body, text=message,
                     font=(Fonts.FAMILY, Fonts.SIZE_SM),
                     text_color=Colors.TEXT_SECONDARY,
                     wraplength=280, anchor="w", justify="left").pack(fill="x", pady=(4, 0))


class QuickActionCard(ctk.CTkFrame):
    """A clickable action button styled as a card."""

    def __init__(self, parent, label: str, icon: str, command=None,
                 accent: str = Colors.PRIMARY, **kwargs):
        super().__init__(parent, fg_color=Colors.BG_CARD,
                         corner_radius=CARD_CORNER,
                         border_width=1, border_color=Colors.BORDER,
                         cursor="hand2", **kwargs)
        self._accent = accent
        self._cmd = command

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(expand=True, pady=Spacing.LG, padx=Spacing.MD)

        # Icon circle
        icon_bg = ctk.CTkFrame(inner, width=46, height=46,
                                fg_color=MetricCard._alpha_color(accent),
                                corner_radius=23)
        icon_bg.pack()
        icon_bg.pack_propagate(False)
        ctk.CTkLabel(icon_bg, text=icon,
                     font=(Fonts.FAMILY, 18),
                     text_color=accent).pack(expand=True)

        ctk.CTkLabel(inner, text=label,
                     font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_PRIMARY).pack(pady=(8, 0))

        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        for child in self.winfo_children():
            child.bind("<Button-1>", self._on_click)

    def _on_click(self, e=None):
        if self._cmd:
            self._cmd()

    def _on_enter(self, e=None):
        self.configure(fg_color=Colors.BG_HOVER, border_color=self._accent)

    def _on_leave(self, e=None):
        self.configure(fg_color=Colors.BG_CARD, border_color=Colors.BORDER)


class SectionHeader(ctk.CTkFrame):
    """A clean section title with blue left accent bar."""

    def __init__(self, parent, title: str, subtitle: str = "",
                 right_widget=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.pack(side="left", fill="y")

        # Blue left border accent
        ctk.CTkFrame(left, width=4, height=32,
                     fg_color=Colors.PRIMARY, corner_radius=2).pack(
            side="left", padx=(0, 10))

        text_col = ctk.CTkFrame(left, fg_color="transparent")
        text_col.pack(side="left")
        ctk.CTkLabel(text_col, text=title,
                     font=(Fonts.FAMILY, Fonts.SIZE_XL, Fonts.WEIGHT_BOLD),
                     text_color=Colors.TEXT_HEADING).pack(anchor="w")
        if subtitle:
            ctk.CTkLabel(text_col, text=subtitle,
                         font=(Fonts.FAMILY, Fonts.SIZE_SM),
                         text_color=Colors.TEXT_MUTED).pack(anchor="w")

        if right_widget:
            right_widget.pack(side="right")


class StatusBadge(ctk.CTkLabel):
    """Colored status pill."""
    PRESETS = {
        "Active":   (Colors.SUCCESS_BG, Colors.SUCCESS),
        "Present":  (Colors.SUCCESS_BG, Colors.SUCCESS),
        "Absent":   (Colors.DANGER_BG,  Colors.DANGER),
        "Late":     (Colors.WARNING_BG, Colors.WARNING),
        "Leave":    (Colors.INFO_BG,    Colors.INFO),
        "On Leave": (Colors.WARNING_BG, Colors.WARNING),
        "Inactive": ("#F0F0F0",         Colors.TEXT_MUTED),
        "Good":     (Colors.SUCCESS_BG, Colors.SUCCESS),
        "Warning":  (Colors.WARNING_BG, Colors.WARNING),
        "Critical": (Colors.DANGER_BG,  Colors.DANGER),
        "A+":       (Colors.SUCCESS_BG, Colors.SUCCESS),
        "A":        (Colors.SUCCESS_BG, Colors.SUCCESS),
        "B+":       (Colors.INFO_BG,    Colors.INFO),
        "B":        (Colors.INFO_BG,    Colors.INFO),
        "C":        (Colors.WARNING_BG, Colors.WARNING),
        "F":        (Colors.DANGER_BG,  Colors.DANGER),
    }

    def __init__(self, parent, status: str, **kwargs):
        bg, fg = self.PRESETS.get(status, ("#F0F0F0", Colors.TEXT_MUTED))
        super().__init__(
            parent,
            text=f"  {status}  ",
            font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
            text_color=fg,
            fg_color=bg,
            corner_radius=12,
            **kwargs
        )
