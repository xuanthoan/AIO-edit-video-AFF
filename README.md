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

## Runtime requirements

- Python 3.11+ recommended.
- PySide6 for the GUI.
- FFmpeg and ffprobe available either globally on `PATH` or through the app's configured binary lookup.
- PySceneDetect is optional but recommended; when unavailable or when detection returns one or zero scenes, shuffle falls back to randomized time-based segments.

## Running the app

```bash
python main.py
```

## Building

```bash
pyinstaller --noconfirm --onedir --windowed main.py
```

If using a spec file, bundle assets and FFmpeg binaries as appropriate for the target machine.

## Export behavior

Rendering validates FFmpeg and ffprobe before processing a batch. Each queue item is rendered independently to the selected output directory. The renderer writes to a hidden `.rendering` output first, verifies the result with ffprobe, and then replaces/renames it to the final MP4 path. Failed videos are logged and skipped so the rest of the queue can continue.

