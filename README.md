# EduTrack — Dar-e-Arqam School Management System

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![UI: CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-00897B.svg)](https://customtkinter.tomschimansky.com/)
[![Persistence: SQLite](https://img.shields.io/badge/Persistence-SQLite3-1565C0.svg)](https://www.sqlite.org/)

**EduTrack** is a standalone, offline-first institutional school management desktop application developed for **Dar-e-Arqam School**. Built with **CustomTkinter** and backed by a local **SQLite** persistence engine, EduTrack delivers a cohesive, role-based experience for school administrators, subject teachers, and student guardians.

---

## Key Features

- **Role-Based Portals**:
  - 🛡 **Administrator**: Institutional dashboard, student registry, faculty directory, classroom management, marks audit, analytics reports, and system settings.
  - 📚 **Teacher**: Daily class attendance marking with instant undo, exam mark entry with automatic grading curves, and personal timetable.
  - 👨‍👩‍👧 **Parent / Guardian**: Child attendance overview, term gradebook, class timetable, and direct school helpdesk communications.
- **14 Fully-Functional Screens**:
  - `login`, `dashboard`, `parent_dashboard`, `students`, `teachers`, `classes`, `attendance`, `marks`, `timetable`, `reports`, `onboarding`, `settings`, `profile`, `help`.
- **WCAG 2.1 AA Compliant Design**:
  - High-contrast Blue & White theme (`#1565C0` brand blue, `#1E3A5F` navy sidebar, certified > 4.5:1 text contrast).
  - Density toggle (`Comfortable` vs `Compact`) and high-contrast accessibility support.
- **Robust Multi-State Architecture (`StateView`)**:
  - Built-in multi-state handling (`Content`, `Empty`, `Loading`, `Error`, `Offline`) across all module screens.
- **Data Safety & Pre-Launch Backups**:
  - Automatic SQLite schema creation and baseline seed population on first run.
  - Timestamped pre-launch database backups (`edutrack_backup_YYYYMMDD_HHMMSS.db`) retained in a dedicated backups directory.
  - Rotating structured file logging (`edutrack.log`) with automatic size limits.
- **Standalone Desktop Packaging**:
  - PyInstaller configuration producing standalone, windowed (no console window) executables for Linux, Windows, and macOS.

---

## Architecture & Directory Structure

```text
AHCI-Project/
├── app/
│   ├── components/       # Reusable UI widgets (cards, sidebar, topbar, tables, toast, state_view)
│   ├── data/             # Demo fixtures and sample data
│   │   ├── demo_fixtures.py  # Isolated mock credentials (DEMO_MODE)
│   │   └── sample_data.py    # Baseline institutional entities
│   ├── db/               # SQLite persistence & path engine
│   │   ├── database.py   # DatabaseManager CRUD & schema lifecycle
│   │   └── paths.py      # Cross-platform user app-data path resolver (platformdirs)
│   ├── screens/          # 14 Role-scoped screen implementations
│   ├── config.py         # Global theme constants, colors, fonts, and flags (DEMO_MODE)
│   └── state.py          # Central application state singleton
├── assets/               # Application icons (icon.ico, icon.png)
├── tests/                # Automated headless smoke test suite
│   └── test_smoke.py
├── build.sh              # Linux / macOS standalone build script
├── build.bat             # Windows standalone build script
├── conftest.py           # Pytest root configuration
├── EduTrack.spec         # PyInstaller packaging specification
├── main.py               # Main application entry point & Tkinter window lifecycle
├── requirements.txt      # Exact pinned runtime dependencies
├── requirements-dev.txt  # Exact pinned build and test dependencies
└── run.sh                # Local source execution script
```

---

## Runtime Data Storage Locations

EduTrack adheres to standard OS filesystem conventions using `platformdirs`. The database and runtime logs are stored in user-writable application directories, ensuring that standalone packaged binaries operate without permission issues:

| Platform | Database Path (`edutrack.db`) | Backups Directory | Application Logs |
| :--- | :--- | :--- | :--- |
| **Linux** | `~/.local/share/EduTrack/edutrack.db` | `~/.local/share/EduTrack/backups/` | `~/.local/state/EduTrack/log/edutrack.log` |
| **Windows** | `%LOCALAPPDATA%\Dar-e-Arqam\EduTrack\edutrack.db` | `%LOCALAPPDATA%\Dar-e-Arqam\EduTrack\backups\` | `%LOCALAPPDATA%\Dar-e-Arqam\EduTrack\Logs\edutrack.log` |
| **macOS** | `~/Library/Application Support/EduTrack/edutrack.db` | `~/Library/Application Support/EduTrack/backups/` | `~/Library/Logs/EduTrack/edutrack.log` |

---

## Installation & Running from Source

### Prerequisites
- Python **3.10** or higher
- Tkinter installed on your system (e.g. `sudo apt-get install python3-tk` on Debian/Ubuntu)

### 1. Clone & Set Up Virtual Environment

```bash
# Clone repository
git clone https://github.com/ahmetdev0822-alt/AHCI-Project.git
cd AHCI-Project

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install runtime dependencies
pip install -r requirements.txt
```

### 2. Launch Application

```bash
# Using the launcher script (Linux / macOS)
chmod +x run.sh
./run.sh

# Or directly with Python
python main.py
```

---

## Building Standalone Executables

EduTrack can be packaged into a self-contained desktop application that runs without requiring Python pre-installed on the host machine.

### Linux / macOS

```bash
# Make build script executable and run
chmod +x build.sh
./build.sh
```
The packaged binary lands at:
```text
dist/EduTrack/EduTrack
```

### Windows

Open Command Prompt or PowerShell in the repository directory and run:
```cmd
build.bat
```
The packaged binary lands at:
```text
dist\EduTrack\EduTrack.exe
```

---

## Security & Demo Mode Configuration

In `app/config.py`, the `DEMO_MODE` flag controls demo fixtures:

```python
# app/config.py
DEMO_MODE = True  # Set to False for production deployment
```

- **When `DEMO_MODE = True` (Default)**:
  - 1-Click Instant Demo Portals are displayed on the login screen for quick evaluation.
  - Pre-filled sample accounts are loaded from `app/data/demo_fixtures.py`.
- **When `DEMO_MODE = False` (Production)**:
  - 1-Click demo buttons are removed.
  - Form fields remain blank.
  - User authentication strictly verifies credentials against the local SQLite `users` table.

### Default Demo Credentials (Demo Mode Only)
- **Administrator**: Username: `admin` | Password: `admin123`
- **Teacher**: Username: `teacher` | Password: `teacher123`
- **Parent**: Username: `parent` | Password: `parent123`

---

## Automated Testing

EduTrack includes a headless test suite that validates core imports, path resolution, database schema creation, pre-launch backups, and CRUD operations without opening a GUI window:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run pytest smoke tests
pytest -v
```

---

## License

This project is licensed under the [MIT License](LICENSE) — see the LICENSE file for details.
