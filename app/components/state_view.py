"""
app/components/state_view.py
Reusable HCI state container widget – renders Empty, Loading, Error, Offline, and Success states.
Designed to meet CS3014 Section 10 multi-state UI requirements.
"""

import customtkinter as ctk
from app.config import Colors, Fonts, Spacing, CARD_CORNER


class StateView(ctk.CTkFrame):
    """
    State container widget.
    Can dynamically switch between:
      - 'content': Normal children display
      - 'empty': No data found with call-to-action button
      - 'loading': Styled loading skeleton / progress view
      - 'error': Clear error explanation with retry button
      - 'offline': Offline banner / local cache indicator
    """

    def __init__(self, parent, state_mode: str = "content", on_retry=None, on_action=None, **kwargs):
        super().__init__(parent, fg_color="transparent", corner_radius=0, **kwargs)
        self._current_state = state_mode
        self._on_retry  = on_retry
        self._on_action = on_action
        self._state_container = None
        self._content_container = None
        self._build_scaffolding()

    def _build_scaffolding(self):
        self._content_container = ctk.CTkFrame(self, fg_color="transparent")
        self._content_container.pack(fill="both", expand=True)

    @property
    def content_area(self) -> ctk.CTkFrame:
        """Add child widgets to this container."""
        return self._content_container

    def set_state(
        self,
        state_mode: str,
        title: str = "",
        message: str = "",
        action_text: str = "",
        error_details: str = "",
    ):
        """Switch the visible state of this container."""
        self._current_state = state_mode

        if self._state_container and self._state_container.winfo_exists():
            self._state_container.destroy()
            self._state_container = None

        if state_mode == "content":
            self._content_container.pack(fill="both", expand=True)
            return

        # Hide normal content when displaying an alternative state
        self._content_container.pack_forget()

        self._state_container = ctk.CTkFrame(
            self,
            fg_color=Colors.BG_CARD,
            corner_radius=CARD_CORNER,
            border_width=1,
            border_color=Colors.BORDER,
        )
        self._state_container.pack(fill="both", expand=True, padx=Spacing.XL, pady=Spacing.XL)

        center = ctk.CTkFrame(self._state_container, fg_color="transparent")
        center.place(relx=0.5, rely=0.48, anchor="center")

        if state_mode == "empty":
            self._render_empty(center, title, message, action_text)
        elif state_mode == "loading":
            self._render_loading(center, title, message)
        elif state_mode == "error":
            self._render_error(center, title, message, error_details)
        elif state_mode == "offline":
            self._render_offline(center, title, message, action_text)

    def _render_empty(self, parent, title, message, action_text):
        icon_box = ctk.CTkFrame(parent, width=72, height=72, fg_color=Colors.PRIMARY_LIGHT, corner_radius=36)
        icon_box.pack(pady=(0, 14))
        icon_box.pack_propagate(False)
        ctk.CTkLabel(icon_box, text="📂", font=(Fonts.FAMILY, 32)).pack(expand=True)

        t = title or "No Records Found"
        m = message or "There are currently no entries matching the selected criteria."
        ctk.CTkLabel(parent, text=t, font=(Fonts.FAMILY, Fonts.SIZE_XL, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_HEADING).pack()
        ctk.CTkLabel(parent, text=m, font=(Fonts.FAMILY, Fonts.SIZE_SM), text_color=Colors.TEXT_MUTED, wraplength=420, justify="center").pack(pady=(6, 18))

        if action_text and self._on_action:
            ctk.CTkButton(
                parent, text=action_text,
                height=36, corner_radius=8,
                font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_DARK,
                command=self._on_action,
            ).pack()

    def _render_loading(self, parent, title, message):
        icon_box = ctk.CTkFrame(parent, width=72, height=72, fg_color=Colors.INFO_BG, corner_radius=36)
        icon_box.pack(pady=(0, 14))
        icon_box.pack_propagate(False)
        ctk.CTkLabel(icon_box, text="⏳", font=(Fonts.FAMILY, 32)).pack(expand=True)

        t = title or "Loading Data..."
        m = message or "Fetching and computing latest records from the local SQLite database."
        ctk.CTkLabel(parent, text=t, font=(Fonts.FAMILY, Fonts.SIZE_XL, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_HEADING).pack()
        ctk.CTkLabel(parent, text=m, font=(Fonts.FAMILY, Fonts.SIZE_SM), text_color=Colors.TEXT_MUTED, wraplength=400, justify="center").pack(pady=(6, 12))

        # Simulated progress bar
        bar = ctk.CTkProgressBar(parent, width=280, height=8, corner_radius=4, progress_color=Colors.PRIMARY)
        bar.pack(pady=8)
        bar.set(0.65)

    def _render_error(self, parent, title, message, details):
        icon_box = ctk.CTkFrame(parent, width=72, height=72, fg_color=Colors.DANGER_BG, corner_radius=36)
        icon_box.pack(pady=(0, 14))
        icon_box.pack_propagate(False)
        ctk.CTkLabel(icon_box, text="⚠", font=(Fonts.FAMILY, 34), text_color=Colors.DANGER).pack(expand=True)

        t = title or "Failed to Load Records"
        m = message or "An unexpected issue occurred while parsing records."
        ctk.CTkLabel(parent, text=t, font=(Fonts.FAMILY, Fonts.SIZE_XL, Fonts.WEIGHT_BOLD), text_color=Colors.DANGER).pack()
        ctk.CTkLabel(parent, text=m, font=(Fonts.FAMILY, Fonts.SIZE_SM), text_color=Colors.TEXT_SECONDARY, wraplength=440, justify="center").pack(pady=(6, 10))

        if details:
            df = ctk.CTkFrame(parent, fg_color=Colors.BG_INPUT, corner_radius=6, border_width=1, border_color=Colors.BORDER)
            df.pack(fill="x", padx=16, pady=(0, 16))
            ctk.CTkLabel(df, text=f"Diagnostic Code: {details}", font=(Fonts.FAMILY_MONO, Fonts.SIZE_XS), text_color=Colors.TEXT_MUTED).pack(padx=12, pady=6)

        if self._on_retry:
            ctk.CTkButton(
                parent, text="⟳  Retry Operation",
                height=36, corner_radius=8,
                font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_DARK,
                command=self._on_retry,
            ).pack()

    def _render_offline(self, parent, title, message, action_text):
        icon_box = ctk.CTkFrame(parent, width=72, height=72, fg_color=Colors.WARNING_BG, corner_radius=36)
        icon_box.pack(pady=(0, 14))
        icon_box.pack_propagate(False)
        ctk.CTkLabel(icon_box, text="☁⃠", font=(Fonts.FAMILY, 32), text_color=Colors.WARNING).pack(expand=True)

        t = title or "Offline Mode Active"
        m = message or "Operating on local encrypted cache. All modifications will sync automatically once connection is restored."
        ctk.CTkLabel(parent, text=t, font=(Fonts.FAMILY, Fonts.SIZE_XL, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_HEADING).pack()
        ctk.CTkLabel(parent, text=m, font=(Fonts.FAMILY, Fonts.SIZE_SM), text_color=Colors.TEXT_MUTED, wraplength=440, justify="center").pack(pady=(6, 16))

        if action_text and self._on_action:
            ctk.CTkButton(
                parent, text=action_text,
                height=36, corner_radius=8,
                font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
                fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_DARK,
                command=self._on_action,
            ).pack()


class StateSwitchDemoBar(ctk.CTkFrame):
    """
    A subtle test strip that allows HCI evaluators to switch between Empty, Loading, Error, Offline, and Content states.
    """

    def __init__(self, parent, on_switch_fn, **kwargs):
        super().__init__(
            parent,
            fg_color=Colors.BG_INPUT,
            corner_radius=8,
            border_width=1,
            border_color=Colors.BORDER,
            **kwargs
        )
        self._on_switch = on_switch_fn
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self,
            text="HCI State Test Mode:",
            font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD),
            text_color=Colors.TEXT_MUTED,
        ).pack(side="left", padx=(10, 8), pady=4)

        states = [
            ("Normal", "content"),
            ("Empty", "empty"),
            ("Loading", "loading"),
            ("Error", "error"),
            ("Offline", "offline"),
        ]
        for label, mode in states:
            ctk.CTkButton(
                self,
                text=label,
                width=64,
                height=24,
                corner_radius=4,
                font=(Fonts.FAMILY, Fonts.SIZE_XS),
                fg_color=Colors.BG_CARD,
                text_color=Colors.TEXT_SECONDARY,
                hover_color=Colors.PRIMARY_LIGHT,
                command=lambda m=mode: self._on_switch(m),
            ).pack(side="left", padx=2, pady=4)
