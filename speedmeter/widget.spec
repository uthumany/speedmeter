# -*- mode: python ; coding: utf-8 -*-
#
# SpeedMeter Widget — PyInstaller Specification
#
# Build a standalone executable for the SpeedMeter GUI widget.
# Usage:
#   pyinstaller speedmeter/widget.spec
#
# The resulting binary will be placed in dist/speedmeter-widget/.

import sys
from pathlib import Path

# Project root
project_root = Path(__file__).resolve().parent.parent

block_cipher = None

a = Analysis(
    [str(project_root / "speedmeter" / "__main__.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[],
    hiddenimports=[
        "speedmeter",
        "speedmeter.app",
        "speedmeter.config",
        "speedmeter.history",
        "speedmeter.tester",
        "speedmeter.widgets",
        "speedmeter.__main__",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="speedmeter-widget",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # GUI mode (no terminal window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
