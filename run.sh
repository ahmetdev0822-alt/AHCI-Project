#!/usr/bin/env bash
# EduTrack Launcher Script
set -e
cd "$(dirname "$0")"

if [ -d "$HOME/.local/opt/arch_tk/usr/lib" ]; then
    export LD_LIBRARY_PATH="$HOME/.local/opt/arch_tk/usr/lib:${LD_LIBRARY_PATH:-}"
    export TCL_LIBRARY="$HOME/.local/opt/arch_tk/usr/lib/tcl8.6"
    export TK_LIBRARY="$HOME/.local/opt/arch_tk/usr/lib/tk8.6"
fi

# Execute EduTrack using the virtual environment
exec .venv/bin/python main.py "$@"
