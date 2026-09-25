@echo off
REM ==============================================================================
REM EduTrack Standalone Desktop Build Script (Windows)
REM Produces a standalone, windowed desktop executable (dist\EduTrack\EduTrack.exe)
REM ==============================================================================

echo ========================================================
echo  Building EduTrack Desktop Application for Windows
echo ========================================================

cd /d "%~dp0"

REM Locate Python environment
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXEC=.venv\Scripts\python.exe"
    set "PYINSTALLER_EXEC=.venv\Scripts\pyinstaller.exe"
) else (
    set "PYTHON_EXEC=python"
    set "PYINSTALLER_EXEC=pyinstaller"
)

echo [+] Using Python interpreter: %PYTHON_EXEC%

REM Check if PyInstaller is installed
%PYTHON_EXEC% -c "import PyInstaller" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [+] Installing build dependencies from requirements-dev.txt...
    %PYTHON_EXEC% -m pip install -r requirements-dev.txt
    if %ERRORLEVEL% NEQ 0 (
        echo [-] Error: Failed to install requirements-dev.txt.
        exit /b 1
    )
)

REM Clean previous build artifacts
echo [+] Cleaning old build and dist folders...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Run PyInstaller
echo [+] Executing PyInstaller build...
%PYINSTALLER_EXEC% EduTrack.spec --noconfirm --clean
if %ERRORLEVEL% NEQ 0 (
    echo [-] Error: PyInstaller build failed.
    exit /b 1
)

echo.
echo ========================================================
echo  [SUCCESS] Windows build completed successfully!
echo  Output Directory: dist\EduTrack\
echo  Executable File:  dist\EduTrack\EduTrack.exe
echo ========================================================
