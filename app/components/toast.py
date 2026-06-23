"""
app/components/toast.py
Elegant notification toasts – Blue & White theme.
"""

import customtkinter as ctk
from app.config import Colors, Fonts


class ToastManager:
    """
    Shows a transient notification in the bottom-right corner.
    kind: "success" | "error" | "info" | "warning"
    """

    STYLES = {
        "success": ("#FFFFFF", Colors.SUCCESS,  Colors.SUCCESS_BG,  "✓"),
        "error":   ("#FFFFFF", Colors.DANGER,   Colors.DANGER_BG,   "✕"),
        "info":    ("#FFFFFF", Colors.INFO,     Colors.INFO_BG,     "ℹ"),
        "warning": ("#FFFFFF", Colors.WARNING,  Colors.WARNING_BG,  "⚠"),
    }

    @staticmethod
    def show(root, message: str, kind: str = "success", duration_ms: int = 3000):
        _, border_color, bg, icon = ToastManager.STYLES.get(kind, ToastManager.STYLES["info"])

        toast = ctk.CTkFrame(
            root,
            fg_color=bg,
            corner_radius=10,
            border_width=2,
            border_color=border_color,
        )

        inner = ctk.CTkFrame(toast, fg_color="transparent")
        inner.pack(padx=16, pady=10, fill="x")

        ctk.CTkLabel(
            inner,
            text=icon,
            font=(Fonts.FAMILY, 16, Fonts.WEIGHT_BOLD),
            text_color=border_color,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            inner,
            text=message,
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            text_color=border_color,
            wraplength=320,
            justify="left",
            anchor="w",
        ).pack(side="left", fill="x", expand=True)

        # Position in bottom-right
        toast.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)
        toast.lift()

        def dismiss():
            if toast.winfo_exists():
                toast.place_forget()
                toast.destroy()

        root.after(duration_ms, dismiss)
