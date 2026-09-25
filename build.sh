#!/usr/bin/env bash
# ==============================================================================
# EduTrack Standalone Desktop Build Script (Linux / macOS)
# Produces a standalone, windowed desktop executable with bundled assets.
# ==============================================================================

set -e

# Change to repository root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================================"
echo " Building EduTrack Desktop Application"
echo "========================================================"

# Ensure Linux local Tkinter libraries are discovered during build if present
ARCH_TK_DIR="$HOME/.local/opt/arch_tk/usr/lib"
if [ -d "$ARCH_TK_DIR" ]; then
    export LD_LIBRARY_PATH="$ARCH_TK_DIR:${LD_LIBRARY_PATH:-}"
    export TCL_LIBRARY="$ARCH_TK_DIR/tcl8.6"
    export TK_LIBRARY="$ARCH_TK_DIR/tk8.6"
fi

# Locate Python environment
if [ -d ".venv" ]; then
    PYTHON_EXEC=".venv/bin/python"
    PYINSTALLER_EXEC=".venv/bin/pyinstaller"
elif command -v python3 &> /dev/null; then
    PYTHON_EXEC="python3"
    PYINSTALLER_EXEC="pyinstaller"
else
    echo "[-] Error: Python 3 not found. Please install Python 3 or create a .venv virtual environment."
    exit 1
fi

echo "[+] Using Python: $($PYTHON_EXEC --version)"

# Verify / install development dependencies
echo "[+] Checking build dependencies..."
if ! $PYTHON_EXEC -c "import PyInstaller" 2>/dev/null; then
    echo "[+] Installing build tools from requirements-dev.txt..."
    $PYTHON_EXEC -m pip install -r requirements-dev.txt
fi

# Clean previous build artifacts
echo "[+] Cleaning previous build and dist directories..."
rm -rf build/ dist/

# Run PyInstaller
echo "[+] Running PyInstaller packaging..."
$PYINSTALLER_EXEC EduTrack.spec --noconfirm --clean

# Verify output
if [ -f "dist/EduTrack/EduTrack" ]; then
    chmod +x dist/EduTrack/EduTrack
    echo ""
    echo "========================================================"
    echo " [SUCCESS] Build completed successfully!"
    echo " Output Directory: dist/EduTrack/"
    echo " Executable Path:  dist/EduTrack/EduTrack"
    echo "========================================================"
elif [ -f "dist/EduTrack" ]; then
    chmod +x dist/EduTrack
    echo ""
    echo "========================================================"
    echo " [SUCCESS] Build completed successfully!"
    echo " Output File:      dist/EduTrack"
    echo "========================================================"
else
    echo "[-] Warning: Build finished but executable was not found at expected location."
    exit 1
fi
