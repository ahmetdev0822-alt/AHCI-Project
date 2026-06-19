"""
app/components/toast.py
Animated slide-in toast notification system.
Usage:
    ToastManager.show(parent_window, "Saved successfully!", kind="success")
"""

import customtkinter as ctk
from app.config import Colors, Fonts


class _Toast(ctk.CTkFrame):
    """A single toast notification that slides in from the bottom-right."""

    KINDS = {
        "success": (Colors.SUCCESS,     Colors.SUCCESS_BG, "✓  "),
        "error":   (Colors.DANGER,      Colors.DANGER_BG,  "✕  "),
        "warning": (Colors.WARNING,     Colors.WARNING_BG, "⚠  "),
        "info":    (Colors.INFO,        Colors.INFO_BG,    "ℹ  "),
    }

    def __init__(self, parent, message: str, kind: str = "success"):
        accent, bg, icon = self.KINDS.get(kind, self.KINDS["info"])
        super().__init__(
            parent,
            fg_color=bg,
            corner_radius=10,
            border_width=2,
            border_color=accent,
        )
        self._accent = accent

        # Left accent bar
        bar = ctk.CTkFrame(self, width=5, fg_color=accent, corner_radius=0)
        bar.pack(side="left", fill="y", padx=(0, 10))

        # Content
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(side="left", fill="both", expand=True, pady=10, padx=(0, 16))

        ctk.CTkLabel(
            inner,
            text=f"{icon}{message}",
            font=(Fonts.FAMILY, Fonts.SIZE_MD, Fonts.WEIGHT_BOLD),
            text_color=accent,
            anchor="w",
            wraplength=280,
        ).pack(anchor="w")

    def place_toast(self, win_width, win_height, index: int = 0):
        """Place the toast at the bottom-right, stacked above previous ones."""
        w, h = 320, 68
        x = win_width - w - 20
        y = win_height - 80 - index * (h + 10)
        self.place(x=x, y=y, width=w, height=h)
        self.lift()


class ToastManager:
    """Global toast queue manager."""
    _active: list[_Toast] = []

    @classmethod
    def show(cls, parent, message: str, kind: str = "success", duration: int = 3000):
        try:
            toast = _Toast(parent, message, kind)
            cls._active.append(toast)
            cls._restack(parent)
            parent.after(duration, lambda: cls._dismiss(parent, toast))
        except Exception:
            pass   # Silently ignore if parent is destroyed

    @classmethod
    def _restack(cls, parent):
        try:
            w = parent.winfo_width()
            h = parent.winfo_height()
            for i, t in enumerate(cls._active):
                t.place_toast(w, h, i)
        except Exception:
            pass

    @classmethod
    def _dismiss(cls, parent, toast: _Toast):
        try:
            toast.place_forget()
            toast.destroy()
            if toast in cls._active:
                cls._active.remove(toast)
            cls._restack(parent)
        except Exception:
            pass
