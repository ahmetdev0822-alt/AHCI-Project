# -*- mode: python ; coding: utf-8 -*-
"""
EduTrack.spec
PyInstaller specification file for building the standalone EduTrack desktop application.
Produces a clean windowed standalone package with bundled CustomTkinter assets and app icons.
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect package data and assets
datas = [
    ('assets', 'assets'),
]
datas += collect_data_files('customtkinter')
datas += collect_data_files('platformdirs')

binaries = []

# If custom Tkinter libraries exist on Linux, bundle them
arch_tk_lib = os.path.expanduser("~/.local/opt/arch_tk/usr/lib")
if os.path.exists(arch_tk_lib):
    for f in os.listdir(arch_tk_lib):
        if (f.startswith("libtcl") or f.startswith("libtk") or f.startswith("libfontconfig") or f.startswith("libfreetype")) and ".so" in f:
            fp = os.path.join(arch_tk_lib, f)
            if os.path.isfile(fp):
                binaries.append((fp, '.'))
    tcl_data = os.path.join(arch_tk_lib, "tcl8.6")
    tk_data = os.path.join(arch_tk_lib, "tk8.6")
    if os.path.exists(tcl_data):
        datas.append((tcl_data, 'tcl8.6'))
        datas.append((tcl_data, '_internal/tcl8.6'))
    if os.path.exists(tk_data):
        datas.append((tk_data, 'tk8.6'))
        datas.append((tk_data, '_internal/tk8.6'))

# Include all submodules and dynamic imports
hiddenimports = [
    'customtkinter',
    'PIL',
    'PIL.ImageTk',
    'PIL.Image',
    'platformdirs',
    'sqlite3',
    'darkdetect',
]
hiddenimports += collect_submodules('app')

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter.test', 'unittest', 'pytest'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='EduTrack',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Windowed mode: no console / terminal window attached
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='EduTrack',
)
