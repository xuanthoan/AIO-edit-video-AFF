# AutoVideoAFF Release Notes v1.0

Release date: 2026-06-01
Status: Version 1.0 Release Candidate

## Features

- Four production workflows:
  - Pipeline 1 — Shuffle + Image.
  - Pipeline 2 — Shuffle + Image + Overlay.
  - Pipeline 3 — Shuffle + Overlay.
  - Pipeline 4 — Overlay Only.
- Queue-based batch rendering with per-video progress logging and failed-video skip behavior.
- Scene shuffle using PySceneDetect when available, with randomized fallback segmentation and manual timeline segment support.
- Image compositing with selectable image pool, crop focus, image height percentage, overlap percentage, and fade settings.
- Overlay support for watermark text, regular text, sales highlights, SVG highlight templates, Sticker Beauty SVG templates, and external sticker images.
- Preview canvas with playhead-aware overlay visibility, drag/resize/rotation controls, safe-area clamping, and center snap guides.
- Mini timeline for playback, playhead scrubbing, overlay timing, manual cuts, segment enable/lock controls, and shuffle-order review.
- Single final FFmpeg export command per rendered video, with modular filtergraph assembly and no intermediate video-stage MP4 files.
- Original audio preservation for shuffle workflows when audio extraction succeeds.
- Atomic `.rendering` output staging, ffprobe validation, automatic output-folder creation, temporary-file cleanup, and Stop support.
- Portable-build spec that bundles assets and optionally includes local FFmpeg binaries from `bin/`.

## Requirements

- Python 3.11 or newer recommended for source runs.
- Python packages listed in `requirements.txt`:
  - `PySide6>=6.7`
  - `scenedetect[opencv]>=0.6.4`
- PyInstaller 6.0+ for portable/release builds.
- FFmpeg and ffprobe are required for rendering and probing. They may be placed in `bin/` beside the app or installed globally on `PATH`.
- Windows portable builds should include `ffmpeg.exe` and `ffprobe.exe` in `bin/` before running PyInstaller if the target machines should not depend on PATH.

## Installation

### Source installation

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -c "import main; print('AutoVideoAFF import OK')"
python main.py
```

On macOS/Linux, activate the virtual environment with `source .venv/bin/activate` instead of the PowerShell activation command.

### FFmpeg installation

Choose one of these options:

1. Copy FFmpeg binaries into `bin/`:
   - `bin/ffmpeg.exe`
   - `bin/ffprobe.exe`
2. Install FFmpeg globally and ensure both `ffmpeg` and `ffprobe` are available on `PATH`.

The app validates both binaries before rendering starts and reports a user-actionable error if either binary is missing.

### Portable build

```bash
python -m pip install -r requirements.txt
python -m pip install "pyinstaller>=6.0"
pyinstaller --noconfirm AutoVideoAFF.spec
```

The output folder is `dist/AutoVideoAFF/`. The spec bundles `assets/`, includes Qt SVG support for SVG highlight rendering, and includes local `bin/ffmpeg(.exe)` and `bin/ffprobe(.exe)` only when those files exist.

## Known limitations

- Automated release tests are still limited; manual render validation is required before broad distribution.
- Preview/export parity should be checked manually for each motion preset, SVG highlight template, and Sticker Beauty template.
- PySceneDetect is optional for detection but recommended; fallback segmentation is less semantically aware than real scene detection.
- No-audio inputs are supported, but unusual audio codecs and extraction failures still require sample-based QA.
- Full project/session persistence is not treated as a completed v1.0 feature.
- Packaging has been prepared for portability, but clean-machine installation/build verification should still be performed before publishing binaries.

## Changelog

### v1.0 Release Candidate

- Refreshed project documentation for the current implementation and release-readiness workflow.
- Added this v1.0 release notes document.
- Verified and documented source installation, FFmpeg setup, output-folder behavior, application import path, and portable build expectations.
- Verified `requirements.txt` as the source-runtime dependency list and documented PyInstaller as a separate release-build tool.
- Hardened `AutoVideoAFF.spec` so release builds remain portable when local `bin/` FFmpeg binaries are present and do not fail when `bin/` is absent.
- Removed a checked-in SVG debug artifact and ignored common render/debug artifacts.
