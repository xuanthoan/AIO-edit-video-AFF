# AutoVideoAFF

AutoVideoAFF is a PySide6 desktop application for queue-based short-form video production for TikTok, Instagram Reels, and YouTube Shorts. The current implementation is a documentation-finalized **Version 1.0 Release Candidate** focused on four production workflows, timeline-driven preview, SVG/text/sticker overlays, scene shuffling, image compositing, and a single FFmpeg export graph per rendered video.

## Version 1.0 Release Candidate

### Implemented features

- Four mutually exclusive workflows:
  - **Pipeline 1 — Shuffle + Image**
  - **Pipeline 2 — Shuffle + Image + Overlay**
  - **Pipeline 3 — Shuffle + Overlay**
  - **Pipeline 4 — Overlay Only**
- Batch video queue with add-file, add-folder, remove, clear, selection-driven preview, and per-item output generation.
- Scene shuffle with PySceneDetect content detection when available, manual timeline cuts, enabled/locked segment flags, keep-first-segment behavior, and randomized fallback splitting.
- Image compositing with selectable image pool, deterministic per-video image choice, image height percentage, overlap percentage, crop focus, and fade curve settings.
- Overlay system for watermark text, regular text, sales highlights, SVG highlight templates, Sticker Beauty SVG templates, and image stickers.
- Motion presets shared across preview/export for text, highlights, and stickers, including fade, pop, bounce, scale, slide, pulse, shake, float, and rotate-float variants.
- Preview canvas with playhead-aware overlay visibility, draggable/resizable/rotatable overlay handles, safe-area clamping, and center snap guides.
- Mini timeline with playback controls, playhead scrubbing, overlay timing blocks, segment list, manual cut controls, timeline save/load hooks, and shuffle-order preview hooks.
- Single final FFmpeg command per output video. Enabled modules append to one `filter_complex`; no intermediate video-stage MP4s are produced.
- Original audio preservation for shuffle workflows by extracting audio before shuffling video-only segments and reattaching it during final export when audio exists.
- Atomic output staging with `.rendering` files, ffprobe verification, safe rename to final MP4, per-video failure isolation, and Stop support through the process manager.

### Supported workflows

| Workflow | Scene shuffle | Image composite | Overlays | Typical use |
| --- | --- | --- | --- | --- |
| Pipeline 1 — Shuffle + Image | Yes | Yes | No | Recut product clips with a top/bottom image layout. |
| Pipeline 2 — Shuffle + Image + Overlay | Yes | Yes | Yes | Full social-commerce edit with image layout and captions/stickers/highlights. |
| Pipeline 3 — Shuffle + Overlay | Yes | No | Yes | Recut clips while keeping full-frame video and adding overlays. |
| Pipeline 4 — Overlay Only | No | No | Yes | Keep original video order and add text/highlights/stickers/watermark. |

### Known limitations

- Automated tests are still limited; release validation is currently a mix of `compileall`, command-generation checks to add, and manual render QA.
- PySide6, FFmpeg/ffprobe, PySceneDetect, and Qt SVG rendering must be available in the runtime environment for full functionality.
- Audio is preserved best-effort: no-audio inputs render as video-only outputs, while audio extraction failures are logged and skipped or escalated depending on FFmpeg output.
- Preview is optimized for lightweight timeline work and does not guarantee pixel-perfect parity with every FFmpeg filter expression.
- SVG highlight rendering depends on template structure conventions such as text-safe-area and sticker-group bounds.

### Recommended future improvements

- Add automated unit tests for FFmpeg command construction, audio mapping, shuffle filtergraphs, overlay timing, and SVG template sizing.
- Add snapshot/golden-image validation for SVG highlights and Sticker Beauty templates.
- Add project save/load UI around the existing state models and timeline serialization hooks.
- Add user-facing dependency diagnostics for missing PySide6, PySceneDetect, FFmpeg, ffprobe, and Qt SVG support.
- Add structured error reporting for failed videos and export a batch summary file.

## Project layout

```text
main.py                                  PySide6 application entry point
core/compositor/                         image composite and fade mask helpers
core/overlays/                           text, watermark, highlight, sticker, SVG template, typography, and motion engines
core/pipeline/                           scene shuffle, image composite, overlay, final export modules, and pipeline manager
core/renderer/                           preview renderer, FFmpeg command builder, and batch renderer
core/video/                              scene detection, fallback segmentation, concat helper, timestamp constants
gui/                                     main window, queue, preview canvas, workflow controls, mini timeline, export panel
models/                                  serializable project, timeline, workflow, and overlay dataclasses
assets/vector_highlight_templates/       SVG highlight and Sticker Beauty template assets
docs/reference/                          architecture, rendering, pipeline, testing, decisions, and handoff notes
```

## Requirements

- Python 3.11+ recommended.
- Python packages from `requirements.txt`:
  - `PySide6` for the GUI and Qt SVG rendering.
  - `scenedetect[opencv]` for automatic scene detection.
- FFmpeg and ffprobe, either:
  - copied into a local `bin/` directory beside the source tree or portable executable as `ffmpeg.exe` and `ffprobe.exe`; or
  - installed globally and available on `PATH`.

PySceneDetect is recommended but the shuffle workflow can fall back to randomized time-based segments when detection returns one or zero scenes.

## Installation from source

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Then verify startup imports:

```bash
python -c "import main; print('AutoVideoAFF import OK')"
```

Run the app:

```bash
python main.py
```

## FFmpeg dependency setup

The renderer validates both `ffmpeg` and `ffprobe` before a batch starts. The lookup order is:

1. `bin/ffmpeg.exe` and `bin/ffprobe.exe` under the application root.
2. Executables directly under the application root.
3. The same locations under the current working directory.
4. System `PATH`.

For portable Windows builds, place `ffmpeg.exe` and `ffprobe.exe` in `bin/` before building, or copy the `bin/` folder beside the generated `AutoVideoAFF.exe` after building. If the binaries are not bundled, the target machine must have FFmpeg installed on `PATH`.

## Building a portable release

Use the checked-in spec so assets are bundled and optional local FFmpeg binaries are included only when present:

```bash
python -m pip install "pyinstaller>=6.0"
pyinstaller --noconfirm AutoVideoAFF.spec
```

The generated app folder is `dist/AutoVideoAFF/`. The spec includes `assets/`, PySide6 Qt SVG support, PySceneDetect/OpenCV hidden imports, and any existing `bin/ffmpeg(.exe)` / `bin/ffprobe(.exe)` files. This keeps source builds working even when `bin/` is absent while still supporting fully portable releases.

## Export behavior

Rendering validates FFmpeg and ffprobe before processing a batch. Each queue item is rendered independently to an `output/` folder beside the first imported source video. If no source-specific output folder is available, relative output paths resolve under the application root. The renderer creates output directories automatically, writes to a hidden `.rendering` output first, verifies the result with ffprobe, and then replaces/renames it to the final MP4 path. Failed videos are logged and skipped so the rest of the queue can continue.

## Release notes

See `RELEASE_NOTES_v1.0.md` for the release feature summary, requirements, installation notes, known limitations, and changelog.
