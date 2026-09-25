# EduTrack — Requirements & Screen Traceability Matrix (CS3014 AHCI Phase 1)

This traceability matrix maps Functional Requirements (FRs), Non-Functional Requirements (NFRs), and Stakeholder Use Cases directly to the **14 concrete screens** and interactive UI states implemented in the `EduTrack` codebase.

---

## 1. Screen Inventory (14 Distinct Screens)

| # | Screen ID | Screen Title | Primary User Roles | Core HCI Interactions & Features | Supported UI States |
|---|---|---|---|---|---|
| 1 | `login` | **Authentication & Role Portal** | Admin, Teacher, Parent | 1-Click Instant Demo Login buttons, show/hide password, explicit error validation | `Content`, `Error`, `Offline` |
| 2 | `dashboard` | **Institutional Dashboard** | Admin, Teacher | Interactive KPI cards with one-click drill-downs into filtered tables, quick action shortcuts, live attendance gauge | `Content`, `Empty`, `Loading`, `Error`, `Offline` |
| 3 | `parent_dashboard` | **Parent & Guardian Portal** | Parent | Real-time child attendance gauge, subject progress bars, teacher remarks note, modal leave request application, teacher messaging dialog | `Content`, `Empty`, `Loading`, `Error`, `Offline` |
| 4 | `students` | **Student Management Registry** | Admin | Dynamic class dropdown filter, instant fuzzy search, add/edit modal form, student detail modal, delete with safety confirmation dialog | `Content`, `Empty`, `Loading`, `Error`, `Offline` |
| 5 | `teachers` | **Teacher Management Directory** | Admin | Searchable faculty roster, homeroom assignment selector, add/edit teacher modal, status badge tags, deletion safeguards | `Content`, `Empty`, `Loading`, `Error`, `Offline` |
| 6 | `classes` | **Classes & Sections Roster** | Admin | Classroom list with capacity indicators, class detail card, drill-down buttons into student roster and class attendance, add section modal | `Content`, `Empty`, `Loading`, `Error`, `Offline` |
| 7 | `attendance` | **Attendance Registry** | Admin, Teacher, Parent | Role-aware bulk actions ("All Present", "All Absent"), interactive undo toast callback, inline student name search, Parent child attendance log | `Content`, `Empty`, `Loading`, `Error`, `Offline` |
| 8 | `marks` | **Performance & Marks Ledger** | Admin, Teacher, Parent | Accessible numerical score validation with out-of-bounds error badges, live class mean/high/low calculation, Parent term gradebook | `Content`, `Empty`, `Loading`, `Error`, `Offline` |
| 9 | `timetable` | **Timetable Matrix** | Admin, Teacher, Parent | Color-coded 8-period weekly schedule grid, click-to-edit period slot modal, room collision & teacher double-booking conflict detection, Teacher personal schedule | `Content`, `Empty`, `Loading`, `Error`, `Offline` |
| 10 | `reports` | **Reports & Analytics Engine** | Admin, Teacher | Dynamic multi-faceted filtering (Class, Assessment, Performance Band: Top/Average/At-Risk), live statistical summaries, CSV & PDF export | `Content`, `Empty`, `Loading`, `Error`, `Offline` |
| 11 | `onboarding` | **Interactive System Tour** | Admin, Teacher, Parent | Step-by-step interactive walkthrough carousel, module highlights, digital inclusion tips, keyboard shortcut reference, direct module launcher | `Content`, `Empty`, `Loading`, `Error`, `Offline` |
| 12 | `settings` | **System & Accessibility Settings** | Admin | Layout Density toggle ("Comfortable" 44px vs "Compact" 34px), WCAG 2.1 AA High Contrast mode toggle, SQLite persistence status & offline sync interval | `Content`, `Empty`, `Loading`, `Error`, `Offline` |
| 13 | `profile` | **My Account & Profile** | Admin, Teacher, Parent | Editable personal contact information, credential security & password change, role badge, session audit trail from SQLite | `Content`, `Empty`, `Loading`, `Error`, `Offline` |
| 14 | `help` | **Helpdesk & User Guidance** | Admin, Teacher, Parent | Searchable FAQ knowledge base, keyboard accessibility cheat sheet, emergency phone directory, support ticket submission form | `Content`, `Empty`, `Loading`, `Error`, `Offline` |

---

## 2. Functional Requirements ↔ Screen Traceability

| FR-ID | Functional Requirement Description | User Role(s) | Primary Screen(s) | Key Code Components |
|---|---|---|---|---|
| **FR-01** | Role-based authentication with distinct permissions | Admin, Teacher, Parent | `login` | `LoginScreen`, `DEMO_USERS`, `AppState.login()` |
| **FR-02** | Executive KPI dashboard with drill-down navigation | Admin, Teacher | `dashboard` | `DashboardScreen`, `MetricCard(command=...)` |
| **FR-03** | Parent real-time visibility into attendance & grades | Parent | `parent_dashboard` | `ParentDashboardScreen`, `AppState.get_linked_child()` |
| **FR-04** | Parent leave request submission & teacher messaging | Parent | `parent_dashboard` | `_open_leave_dialog()`, `_open_contact_dialog()` |
| **FR-05** | Student lifecycle management (Add/Edit/Delete/Search) | Admin | `students`, `classes` | `StudentsScreen`, `StudentForm`, `db.save_student()` |
| **FR-06** | Faculty registry & homeroom class assignment | Admin | `teachers` | `TeachersScreen`, `TeacherForm`, `db.save_teacher()` |
| **FR-07** | Classroom section structure & capacity tracking | Admin | `classes` | `ClassesScreen`, `db.save_class()` |
| **FR-08** | Rapid bulk attendance marking with undo capability | Teacher | `attendance` | `AttendanceScreen._bulk_set()`, `ToastManager` with action callback |
| **FR-09** | Read-only child attendance log for parents | Parent | `attendance`, `parent_dashboard` | `AttendanceScreen._render_parent_attendance()` |
| **FR-10** | Examination score entry with bounded validation | Teacher | `marks` | `MarksScreen._on_mark_changed()`, `db.save_marks_batch()` |
| **FR-11** | Interactive weekly timetable with conflict detection | Admin, Teacher, Parent | `timetable` | `TimetableScreen._open_slot_editor()`, `_run_conflict_check()` |
| **FR-12** | Faceted performance reports & multi-format export | Admin, Teacher | `reports` | `ReportsScreen._render_active_report()`, CSV/PDF dispatch |
| **FR-13** | First-run interactive walkthrough & feature guidance | All Roles | `onboarding` | `OnboardingScreen`, step carousel & direct launchers |
| **FR-14** | Accessibility density toggle & high contrast mode | All Roles | `settings`, `topbar` | `SettingsScreen`, `TopBar._toggle_density()` |
| **FR-15** | User account management & session activity audit | All Roles | `profile` | `ProfileScreen`, `db.log_activity()` |
| **FR-16** | Searchable helpdesk knowledge base & support tickets | All Roles | `help` | `HelpScreen`, `db.create_support_ticket()` |
| **FR-17** | Offline-first local SQLite persistence & caching | All Roles | All Screens | `app/db/database.py`, `AppState.reload_from_db()` |

---

## 3. Measurable Accessibility & Usability (NFR) Compliance

| NFR Category | Target Metric | Code Implementation | Verification Screen |
|---|---|---|---|
| **Color Contrast (WCAG 2.1 AA)** | &ge; 4.5:1 for normal text, &ge; 3.0:1 for large UI | `app/config.py` uses `#0F172A` on `#FFFFFF` (15.8:1), `#C9DCF2` on `#1E3A5F` (6.2:1) | All Screens |
| **Layout Density Modes** | 44px min touch target ("Comfortable") vs 34px ("Compact") | `app/components/topbar.py` + `app/screens/settings.py` | `settings`, `topbar` |
| **Keyboard Navigation** | 100% focusable buttons, `<Tab>`, `<Enter>`, `<Esc>` | CustomTkinter event bindings and tab traverse orders | `help`, `students`, `marks` |
| **Error Feedback** | Dual-channel feedback (Icon + Explanatory Text, non-color-only) | Modal validation banners, `StateView(error)` | `marks`, `profile`, `login` |
| **Data Resilience** | Zero data loss during network or power disruption | SQLite 3 write-through transactions (`data/edutrack.db`) | `app/db/database.py` |
