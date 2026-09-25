"""
app/components/toast.py
Toast notification system with action callback (Undo / View) and high-contrast styling.
"""

import customtkinter as ctk
from app.config import Colors, Fonts


class ToastManager:
    """
    Shows a transient notification in the bottom-right corner.
    Supports optional interactive action callback (e.g. "Undo").
    kind: "success" | "error" | "info" | "warning"
    """

    STYLES = {
        "success": ("#FFFFFF", Colors.SUCCESS,  Colors.SUCCESS_BG,  "✓"),
        "error":   ("#FFFFFF", Colors.DANGER,   Colors.DANGER_BG,   "✕"),
        "info":    ("#FFFFFF", Colors.INFO,     Colors.INFO_BG,     "ℹ"),
        "warning": ("#FFFFFF", Colors.WARNING,  Colors.WARNING_BG,  "⚠"),
    }

    @staticmethod
    def show(root, message: str, kind: str = "success", duration_ms: int = 3500, action_label: str = "", action_fn=None):
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
            wraplength=300,
            justify="left",
            anchor="w",
        ).pack(side="left", fill="x", expand=True)

        dismiss_after_id = None

        def dismiss():
            if toast.winfo_exists():
                toast.place_forget()
                toast.destroy()

        if action_label and action_fn:
            def on_action_click():
                if dismiss_after_id:
                    root.after_cancel(dismiss_after_id)
                dismiss()
                action_fn()

            ctk.CTkButton(
                inner,
                text=action_label,
                height=28,
                width=64,
                corner_radius=6,
                font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
                fg_color=border_color,
                text_color=Colors.TEXT_WHITE,
                hover_color=Colors.PRIMARY_DARK,
                command=on_action_click,
            ).pack(side="right", padx=(10, 0))

        # Position in bottom-right
        toast.place(relx=1.0, rely=1.0, anchor="se", x=-24, y=-24)
        toast.lift()

        dismiss_after_id = root.after(duration_ms, dismiss)
