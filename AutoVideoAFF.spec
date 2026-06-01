# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller release build configuration for AutoVideoAFF.

The spec is portable by default: assets are bundled when present, and optional
FFmpeg binaries are included only when a local bin/ directory exists. Release
builders may either place ffmpeg/ffprobe in bin/ before running PyInstaller or
ship a build that relies on the user's PATH installation.
"""
from pathlib import Path

block_cipher = None
ROOT = Path(SPECPATH)


def optional_bin(name: str) -> tuple[str, str] | None:
    """Return a PyInstaller binary tuple for bin/name when it exists."""
    for filename in (f"{name}.exe", name):
        candidate = ROOT / "bin" / filename
        if candidate.exists():
            return (str(candidate), "bin")
    return None


binaries = [item for item in (optional_bin("ffmpeg"), optional_bin("ffprobe")) if item]
datas = [(str(ROOT / "assets"), "assets")] if (ROOT / "assets").exists() else []


a = Analysis(
    ['main.py'],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=['PySide6.QtSvg', 'scenedetect', 'cv2'],
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
    [],
    exclude_binaries=True,
    name='AutoVideoAFF',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AutoVideoAFF',
)
