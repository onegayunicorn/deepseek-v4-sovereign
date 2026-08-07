# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller onefile spec for the Sovereign CLI/orchestrator.

Build with (from builds/exe/):

    pyinstaller --clean --noconfirm sovereign.spec

The Analysis entry script is ``src/sovereign/main.py`` (resolved relative to
this spec file). ``pathex`` points at ``src/`` so the ``sovereign`` package
imports resolve to the monorepo source tree.
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect every submodule of the `sovereign` package so hidden imports
# (plugins, optional deps) are bundled even when not statically imported.
hiddenimports = collect_submodules("sovereign")

# Additional hidden imports for uvicorn's dynamic protocol/loop loading.
hiddenimports += [
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
]

# Package data (non-.py assets) shipped inside the bundle.
datas = collect_data_files("sovereign")

a = Analysis(
    ["../../../src/sovereign/main.py"],
    pathex=["../../../src"],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "PyQt5",
        "PyQt6",
        "PySide2",
        "PySide6",
        "pytest",
        "IPython",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="sovereign",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # CLI entry point — keep the console.
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # No custom icon; a .ico can be added here later.
)
