"""
conftest.py
Pytest configuration and environment setup for EduTrack test runner.
"""
import sys
import os

# ── Ensure native Tkinter/Tcl libraries and antialiased fonts are available on Linux ──
_tk_lib_dir = os.path.expanduser("~/.local/opt/arch_tk/usr/lib")
if os.path.exists(_tk_lib_dir):
    os.environ.setdefault("TCL_LIBRARY", os.path.expanduser("~/.local/opt/arch_tk/usr/lib/tcl8.6"))
    os.environ.setdefault("TK_LIBRARY", os.path.expanduser("~/.local/opt/arch_tk/usr/lib/tk8.6"))
    _current_ld = os.environ.get("LD_LIBRARY_PATH", "")
    if _tk_lib_dir not in _current_ld.split(":"):
        os.environ["LD_LIBRARY_PATH"] = f"{_tk_lib_dir}:{_current_ld}".strip(":")
        os.execv(sys.executable, [sys.executable] + sys.argv)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
