# EduTrack — Platform Choice & Justification Notes (CS3014 AHCI Section 2 & 7.2)

## 1. Platform Choice: Python Desktop Application (CustomTkinter)

### One-Line Platform Justification (for Section 2)
> *"EduTrack is built as an offline-first native desktop application to guarantee zero-latency data entry and continuous operational uptime for private school administrative offices operating under intermittent internet connectivity and shared hardware constraints."*

---

## 2. Contextual Rationale for Target School Environment

1. **Connectivity Realities in Pakistani Educational Institutions**:
   - Many private and community schools in urban and semi-urban Pakistan experience frequent broadband outages, high mobile data latency, and load-shedding.
   - A traditional cloud-only web app halts administrative workflows (morning attendance roll call, fee verification, exam entry) when internet drops.
   - EduTrack operates entirely on local **SQLite 3** persistence, allowing full offline CRUD operations with zero dependency on cloud availability.

2. **Dedicated Single-Terminal Office Workstation**:
   - In target schools, school records are maintained by administrative staff working at a fixed desktop terminal in the main office.
   - A native desktop application integrates directly with local operating system hardware, enabling direct printing to receipt and report printers without web browser print dialog quirks.

3. **High-Speed Keyboard-First Data Entry**:
   - Staff members enter marks for hundreds of students during examination cycles.
   - Native desktop event loops allow ultra-responsive keyboard tabbing (`<Tab>`, `<Enter>`, numeric keypad entry) with sub-millisecond input latency, preventing input dropouts common in slow web interfaces.

4. **Zero Recurring Infrastructure & Hosting Overhead**:
   - Low-tier and mid-tier private schools operate on tight operational margins and resist monthly cloud software-as-a-service (SaaS) subscription fees.
   - EduTrack is self-contained with zero server infrastructure costs, making adoption economically viable.

5. **Data Privacy & Local Sovereignty**:
   - Student demographic records and family contact details remain stored securely on the school's local encrypted storage rather than third-party cloud servers.

---

## 3. Operational Feasibility Summary (for Section 7.2)

| Dimension | Justification |
|---|---|
| **Hardware Requirements** | Runs smoothly on entry-level Dual-Core x86_64 machines with 2 GB RAM. |
| **Operating System** | Cross-platform compatibility across Linux, Windows 10/11, and macOS. |
| **Installation Footprint** | Standalone lightweight Python bundle with embedded SQLite database (`< 40 MB` total footprint). |
| **Staff Training Time** | Minimized via intuitive visual layouts, 1-click role demo buttons, and interactive Onboarding Tour. |
