# Changelog

All notable changes to the **EduTrack** School Management System are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.2.0] - 2026-09-25

### Standalone Desktop Deployment & Infrastructure Pass

#### Added
- **Standalone Packaging Engine**:
  - Configured `PyInstaller` specification (`EduTrack.spec`) bundling CustomTkinter assets, application icons, and dynamic dependencies in windowed mode (no console window).
  - Created automated build scripts: `build.sh` (Linux / macOS) and `build.bat` (Windows).
  - Generated native multi-resolution application icons (`assets/icon.ico` and `assets/icon.png`) and bound them to the main window and OS taskbar.
- **Cross-Platform App-Data Persistence**:
  - Implemented `app/db/paths.py` leveraging `platformdirs` to resolve user-writable application directories for SQLite database, logs, and backups across Linux (`~/.local/share/EduTrack`), macOS (`~/Library/Application Support/EduTrack`), and Windows (`%LOCALAPPDATA%\Dar-e-Arqam\EduTrack`).
- **Data Safety & Automated Pre-Launch Backups**:
  - Added automatic schema creation on first launch with seed data population.
  - Implemented timestamped pre-launch database backups (`edutrack_backup_YYYYMMDD_HHMMSS.db`) in `<app-data>/backups/` with automated retention pruning (retaining the 10 most recent backups).
  - Configured rotating file logger (`<app-data>/logs/edutrack.log`) with 5 MB chunk size and 3 backup rotations.
- **Security & Demo Isolation**:
  - Isolated demo seed fixtures into `app/data/demo_fixtures.py`.
  - Added `DEMO_MODE` configuration toggle in `app/config.py` to seamlessly enable/disable quick 1-click login buttons and prefilled credentials for production environments.
  - Implemented database-backed user authentication (`db.authenticate_user()`) and password update persistence in SQLite.
- **Automated Smoke Test Suite**:
  - Added headless automated pytest suite (`tests/test_smoke.py`, `conftest.py`, `pytest.ini`) testing core imports, path resolution, schema auto-initialization, pre-launch backups, and CRUD operations.
- **Documentation & Open Source Licensing**:
  - Comprehensive `README.md` including feature descriptions, architecture map, data storage paths, build instructions, and developer guides.
  - Added `LICENSE` (MIT License) and `requirements-dev.txt` for development dependencies.

#### Changed
- **Dependency Hygiene**:
  - Pinned exact dependency versions in `requirements.txt` (`customtkinter==6.0.0`, `Pillow==12.3.0`, `platformdirs==4.11.13`, `darkdetect==0.8.0`).
  - Separated build-only tools into `requirements-dev.txt` (`pyinstaller==6.22.3`, `pytest==9.1.1`).
  - Cleaned all compiled `.pyc` and `__pycache__` artifacts from Git tracking and updated `.gitignore`.
- **UI Scaling & Window Resizability**:
  - Updated minimum window size constraints to `1024x680` ensuring flawless readability on standard laptop displays (1366x768) without overlapping or clipped controls.
- **Input Validation & Stability Pass**:
  - Hardened input handling across all form dialogs (`Students`, `Teachers`, `Classes`, `Marks`, `Profile`, `Settings`), preventing crashes on malformed or empty inputs and surfacing informative user-facing toast notifications.

---

## [2.1.0] - 2026-09-24

### AHCI Phase 1 Curriculum Alignment Edition

#### Added
- Implemented 14 distinct system screens supporting 3 institutional roles (Administrator, Teacher, Parent).
- Added multi-state view architecture (`StateView`) supporting `Content`, `Empty`, `Loading`, `Error`, and `Offline` states.
- Implemented WCAG 2.1 AA compliant Blue & White design theme with minimum 4.5:1 text contrast.
- Built interactive onboarding guide (`OnboardingScreen`), system preferences (`SettingsScreen`), user profile (`ProfileScreen`), and helpdesk (`HelpScreen`).
- Added bidirectional interactive timetable grid with conflict detection.
