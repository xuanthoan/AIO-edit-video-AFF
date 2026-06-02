# -*- mode: python ; coding: utf-8 -*-
"""Production onefile PyInstaller spec for the Windows AutoVideoAFF release."""
from pathlib import Path

block_cipher = None
ROOT = Path(SPECPATH).resolve()
ICON_PATH = ROOT / "creative.ico"



def add_tree(source: str, target: str | None = None) -> list[tuple[str, str]]:
    """Bundle a resource directory only when it exists in the checkout."""
    path = ROOT / source
    if not path.exists():
        return []
    return [(str(path), target or source)]


def add_file(source: str, target: str = ".") -> list[tuple[str, str]]:
    """Bundle a config/resource file only when it exists in the checkout."""
    path = ROOT / source
    if not path.exists():
        return []
    return [(str(path), target)]


def optional_bin(name: str) -> tuple[str, str] | None:
    """Bundle local FFmpeg binaries when present for portable Windows builds."""
    for filename in (f"{name}.exe", name):
        candidate = ROOT / "bin" / filename
        if candidate.exists():
            return (str(candidate), "bin")
    return None


binaries = [item for item in (optional_bin("ffmpeg"), optional_bin("ffprobe")) if item]

datas = []
datas += add_tree("assets", "assets")
datas += add_tree("fonts", "fonts")
datas += add_tree("templates", "templates")
for config_name in ("config.json", "config.yaml", "config.yml", "config.ini", "settings.json"):
    datas += add_file(config_name, ".")

hiddenimports = [
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "PySide6.QtSvg",
    "scenedetect",
    "cv2",
]


a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name="AutoVideoAFF.exe",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ICON_PATH) if ICON_PATH.exists() else None,
)
