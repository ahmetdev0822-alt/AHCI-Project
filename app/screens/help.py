"""
app/screens/help.py
Help & Support / In-App Guidance Screen.
Searchable FAQ, keyboard shortcut cheat sheet, role tutorials, and ticket submission form.
Addresses CS3014 Section 10 (Help/Support screen) and Section 12 (Digital Inclusion).
"""

import customtkinter as ctk
from app.config import (
    Colors, Fonts, Spacing, CARD_CORNER, ROLE_ADMIN, ROLE_TEACHER, ROLE_PARENT,
)
from app.components.cards import SectionHeader, AlertCard
from app.components.state_view import StateView, StateSwitchDemoBar
from app.db.database import db


class HelpScreen(ctk.CTkFrame):
    """In-app guidance, searchable documentation, keyboard cheatsheet, and helpdesk ticketing."""

    FAQS = [
        {
            "q": "How do I mark attendance in bulk for my class?",
            "a": "Navigate to the Attendance screen as a Teacher. Select your class and date, then click '✓ All Present' or '✕ All Absent'. You can then click individual student status buttons to toggle exceptions. If you make a mistake, click the '↶ Undo' button on the notification toast.",
            "category": "Attendance",
        },
        {
            "q": "How does schedule conflict detection work in Timetable?",
            "a": "When an Administrator assigns or swaps periods in the Timetable matrix, the system checks if the assigned subject teacher or room is already booked in another classroom for the same period. If a conflict is detected, a warning modal prevents accidental double-booking.",
            "category": "Timetable",
        },
        {
            "q": "How do parents submit leave requests for their children?",
            "a": "Parents can sign into the Parent Portal and click '📝 Request Leave' on their dashboard. Select the leave type (Medical, Urgent, etc.), date range, and explanation. The application immediately alerts the student's homeroom teacher.",
            "category": "Parent Portal",
        },
        {
            "q": "How can I operate EduTrack when internet or power is unavailable?",
            "a": "EduTrack is engineered with an offline-first architecture using local SQLite storage. All attendance, marks, and student edits work seamlessly offline. Changes are preserved permanently on the machine and will sync automatically when connectivity is restored.",
            "category": "Offline Mode",
        },
        {
            "q": "How do I switch layout density for larger touch targets or low-spec displays?",
            "a": "Click the '🔍 Density' button located on the top bar or visit System Settings. Switching to 'Comfortable' enlarges touch buttons and typography for accessible viewing.",
            "category": "Accessibility",
        },
    ]

    def __init__(self, parent, state, navigate_fn, toast_fn):
        super().__init__(parent, fg_color=Colors.BG_MAIN, corner_radius=0)
        self._state    = state
        self._navigate = navigate_fn
        self._toast    = toast_fn
        self._search_var = ctk.StringVar()
        self._build()

    def _build(self):
        pad = Spacing.XL

        top_row = ctk.CTkFrame(self, fg_color="transparent")
        top_row.pack(fill="x", padx=pad, pady=(pad, Spacing.SM))
        SectionHeader(top_row, "Helpdesk & User Guidance", "Interactive documentation, accessibility cheat sheets, and technical support").pack(side="left", fill="y")
        StateSwitchDemoBar(top_row, on_switch_fn=self._on_state_switch).pack(side="right")

        self._state_view = StateView(
            self,
            on_retry=lambda: self._on_state_switch("content"),
            on_action=lambda: self._navigate("dashboard"),
        )
        self._state_view.pack(fill="both", expand=True)

        scroll = ctk.CTkScrollableFrame(self._state_view.content_area, fg_color=Colors.BG_MAIN, corner_radius=0)
        scroll.pack(fill="both", expand=True)

        self._render_help_content(scroll)

    def _on_state_switch(self, mode: str):
        if mode == "content":
            self._state_view.set_state("content")
        elif mode == "empty":
            self._state_view.set_state("empty", title="No FAQs Found", message="No knowledge base articles matched your search query.", action_text="Clear Search Query")
        elif mode == "loading":
            self._state_view.set_state("loading", title="Searching Knowledge Base...", message="Querying index for guides, shortcut maps, and tutorials.")
        elif mode == "error":
            self._state_view.set_state("error", title="Knowledge Base Unavailable", message="Could not parse local documentation index.", error_details="ERR_DOCS_INDEX_CORRUPT (Code 404)")
        elif mode == "offline":
            self._state_view.set_state("offline", title="Offline Help Cache", message="Browsing built-in local help articles and emergency contact numbers.", action_text="View Contacts")

    def _render_help_content(self, parent):
        pad = Spacing.XL

        # ── 1. Search Bar & Category Filter ───────────────────────────────────
        search_card = ctk.CTkFrame(parent, fg_color=Colors.BG_CARD, corner_radius=10, border_width=1, border_color=Colors.BORDER)
        search_card.pack(fill="x", padx=pad, pady=(0, Spacing.XL))

        sc_inner = ctk.CTkFrame(search_card, fg_color="transparent")
        sc_inner.pack(fill="x", padx=Spacing.LG, pady=Spacing.LG)

        ctk.CTkLabel(sc_inner, text="🔍  Search Knowledge Base & FAQs:", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_PRIMARY).pack(side="left", padx=(0, 10))

        search_entry = ctk.CTkEntry(
            sc_inner,
            textvariable=self._search_var,
            placeholder_text="Type a question (e.g. attendance, timetable, parent, offline)...",
            height=36,
            fg_color=Colors.BG_INPUT,
            border_color=Colors.BORDER,
            text_color=Colors.TEXT_PRIMARY,
        )
        search_entry.pack(side="left", fill="x", expand=True)
        self._search_var.trace_add("write", lambda *_: self._filter_faqs())

        # ── 2. FAQ Accordion Section ──────────────────────────────────────────
        SectionHeader(parent, "Frequently Asked Questions", "Common workflows and answers for all user roles").pack(fill="x", padx=pad, pady=(0, Spacing.SM))

        self._faq_container = ctk.CTkFrame(parent, fg_color="transparent")
        self._faq_container.pack(fill="x", padx=pad, pady=(0, Spacing.XL))
        self._render_faqs(self.FAQS)

        # ── 3. Two Columns: Keyboard Shortcuts & Support Ticket Form ──────────
        cols = ctk.CTkFrame(parent, fg_color="transparent")
        cols.pack(fill="both", expand=True, padx=pad, pady=(0, pad))
        cols.columnconfigure(0, weight=5)
        cols.columnconfigure(1, weight=5)

        # Left: Keyboard Shortcuts
        sc_card = ctk.CTkFrame(cols, fg_color=Colors.BG_CARD, corner_radius=10, border_width=1, border_color=Colors.BORDER)
        sc_card.grid(row=0, column=0, sticky="nsew", padx=(0, Spacing.MD))

        sck_head = ctk.CTkFrame(sc_card, fg_color="transparent")
        sck_head.pack(fill="x", padx=Spacing.LG, pady=(Spacing.LG, Spacing.SM))
        ctk.CTkLabel(sck_head, text="⌨  Accessibility & Keyboard Shortcuts", font=(Fonts.FAMILY, Fonts.SIZE_LG, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_HEADING).pack(anchor="w")

        sck_body = ctk.CTkFrame(sc_card, fg_color="transparent")
        sck_body.pack(fill="both", expand=True, padx=Spacing.LG, pady=(0, Spacing.LG))

        shortcuts = [
            ("<Tab> / <Shift+Tab>", "Move focus to next / previous interactive element"),
            ("<Enter>", "Trigger selected button or submit active dialog"),
            ("<Escape>", "Cancel action, dismiss modal dialog, or close popup"),
            ("Alt + 1 to 8", "Quick jump to corresponding sidebar navigation screen"),
            ("Spacebar", "Toggle checkbox or select option in table rows"),
        ]

        for keys, desc in shortcuts:
            row = ctk.CTkFrame(sck_body, fg_color=Colors.BG_INPUT, corner_radius=6, border_width=1, border_color=Colors.BORDER)
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=f" {keys} ", font=(Fonts.FAMILY_MONO, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD), fg_color=Colors.PRIMARY_LIGHT, text_color=Colors.PRIMARY, corner_radius=4).pack(side="left", padx=8, pady=6)
            ctk.CTkLabel(row, text=desc, font=(Fonts.FAMILY, Fonts.SIZE_XS), text_color=Colors.TEXT_PRIMARY).pack(side="left", padx=8)

        # Emergency Contact info
        ctk.CTkFrame(sck_body, height=1, fg_color=Colors.BORDER).pack(fill="x", pady=12)
        ctk.CTkLabel(sck_body, text="📞 School Helpdesk Contact Info:", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_HEADING).pack(anchor="w")
        ctk.CTkLabel(sck_body, text="Phone: 0300-1122334 (Ext 101)  ·  Email: support@darearqam.edu.pk\nOffice Hours: Mon–Fri (8:00 AM – 2:00 PM)", font=(Fonts.FAMILY, Fonts.SIZE_XS), text_color=Colors.TEXT_MUTED, justify="left").pack(anchor="w", pady=(2, 0))

        # Right: Submit Support Ticket
        tick_card = ctk.CTkFrame(cols, fg_color=Colors.BG_CARD, corner_radius=10, border_width=1, border_color=Colors.BORDER)
        tick_card.grid(row=0, column=1, sticky="nsew")

        tc_head = ctk.CTkFrame(tick_card, fg_color="transparent")
        tc_head.pack(fill="x", padx=Spacing.LG, pady=(Spacing.LG, Spacing.SM))
        ctk.CTkLabel(tc_head, text="✉  Submit Helpdesk Support Ticket", font=(Fonts.FAMILY, Fonts.SIZE_LG, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_HEADING).pack(anchor="w")

        tc_body = ctk.CTkFrame(tick_card, fg_color="transparent")
        tc_body.pack(fill="both", expand=True, padx=Spacing.LG, pady=(0, Spacing.LG))

        ctk.CTkLabel(tc_body, text="Issue Category:", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_SECONDARY).pack(anchor="w", pady=(2, 2))
        self._cat_var = ctk.StringVar(value="Technical Assistance")
        ctk.CTkOptionMenu(tc_body, values=["Technical Assistance", "Attendance / Marks Data Correction", "Parent Portal Access", "Feature Feedback"], variable=self._cat_var, fg_color=Colors.BG_INPUT, button_color=Colors.PRIMARY, text_color=Colors.TEXT_PRIMARY, height=34).pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(tc_body, text="Subject / Brief Summary:", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_SECONDARY).pack(anchor="w", pady=(2, 2))
        self._tick_subj = ctk.CTkEntry(tc_body, height=34, fg_color=Colors.BG_INPUT, border_color=Colors.BORDER, text_color=Colors.TEXT_PRIMARY, placeholder_text="e.g. Cannot edit period 3 on Thursday")
        self._tick_subj.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(tc_body, text="Detailed Description:", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_SECONDARY).pack(anchor="w", pady=(2, 2))
        self._tick_msg = ctk.CTkTextbox(tc_body, height=75, fg_color=Colors.BG_INPUT, border_width=1, border_color=Colors.BORDER, text_color=Colors.TEXT_PRIMARY, font=(Fonts.FAMILY, Fonts.SIZE_SM))
        self._tick_msg.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(
            tc_body, text="✓  Submit Ticket to Helpdesk", height=36, corner_radius=8,
            font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD),
            fg_color=Colors.PRIMARY, text_color=Colors.TEXT_WHITE,
            hover_color=Colors.PRIMARY_DARK,
            command=self._submit_ticket,
        ).pack(anchor="e")

    def _render_faqs(self, faq_list):
        for w in self._faq_container.winfo_children():
            w.destroy()

        if not faq_list:
            ctk.CTkLabel(self._faq_container, text="No FAQ items matched your query.", font=(Fonts.FAMILY, Fonts.SIZE_SM), text_color=Colors.TEXT_MUTED).pack(pady=10)
            return

        for item in faq_list:
            card = ctk.CTkFrame(self._faq_container, fg_color=Colors.BG_CARD, corner_radius=8, border_width=1, border_color=Colors.BORDER)
            card.pack(fill="x", pady=4)

            head = ctk.CTkFrame(card, fg_color="transparent")
            head.pack(fill="x", padx=14, pady=(10, 4))
            ctk.CTkLabel(head, text=f"Q: {item['q']}", font=(Fonts.FAMILY, Fonts.SIZE_SM, Fonts.WEIGHT_BOLD), text_color=Colors.TEXT_HEADING).pack(side="left")
            ctk.CTkLabel(head, text=f"[{item['category']}]", font=(Fonts.FAMILY, Fonts.SIZE_XS, Fonts.WEIGHT_BOLD), text_color=Colors.PRIMARY).pack(side="right")

            ctk.CTkLabel(card, text=item["a"], font=(Fonts.FAMILY, Fonts.SIZE_SM), text_color=Colors.TEXT_SECONDARY, wraplength=760, justify="left").pack(anchor="w", padx=14, pady=(0, 10))

    def _filter_faqs(self):
        query = self._search_var.get().strip().lower()
        if not query:
            self._render_faqs(self.FAQS)
            return
        filtered = [
            f for f in self.FAQS
            if query in f["q"].lower() or query in f["a"].lower() or query in f["category"].lower()
        ]
        self._render_faqs(filtered)

    def _submit_ticket(self):
        cat = self._cat_var.get()
        subj = self._tick_subj.get().strip()
        msg = self._tick_msg.get("1.0", "end").strip()

        if not subj or not msg:
            self._toast("Validation Error: Please provide both subject and message details.", "error")
            return

        user_name = self._state.current_user.get("username", "user") if self._state.current_user else "user"
        tid = db.create_support_ticket(user_name, cat, subj, msg)

        self._tick_subj.delete(0, "end")
        self._tick_msg.delete("1.0", "end")
        self._toast(f"Ticket #{tid} submitted successfully! Support staff has been notified.", "success")
