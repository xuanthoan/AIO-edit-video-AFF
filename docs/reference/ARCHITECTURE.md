# Architecture

_Last updated: 2026-06-01_

## Version 1.0 Release Candidate

AutoVideoAFF uses a layered desktop architecture:

1. **GUI layer** (`gui/`) owns queue management, workflow controls, preview playback, timeline editing, and render-thread callbacks.
2. **State layer** (`models/`) stores serializable dataclasses for project settings, workflow mode, scene segments, export settings, safe area settings, and overlay definitions.
3. **Core pipeline layer** (`core/pipeline/`) builds enabled render modules into one `FilterGraph`.
4. **Overlay/compositor/video engines** (`core/overlays/`, `core/compositor/`, `core/video/`) generate filtergraph fragments, temporary overlay assets, scene segments, and layout plans.
5. **Renderer layer** (`core/renderer/`) validates runtime dependencies, extracts preview frames, builds FFmpeg commands, runs batch exports, verifies outputs, and handles Stop.

### Implemented features

- PySide6 application entry through `main.py`.
- `ProjectState` as the central data object passed from GUI to renderer.
- `WorkflowMode` enum for four mutually exclusive pipelines.
- `PipelineManager` that selects scene shuffle, image composite, overlay, and final export modules by workflow state.
- `FilterGraph` object containing FFmpeg inputs, filter nodes, video/audio labels, extra args, temporary files, layout plans, shuffle plans, and debug events.
- `BatchRenderer` for sequential per-video rendering with callbacks and failure isolation.
- Overlay engines for text, watermark, highlights, SVG highlights, Sticker Beauty templates, stickers, typography, transform normalization, and motion expressions.

### Supported workflows

| Workflow | Active modules |
| --- | --- |
| Pipeline 1 — Shuffle + Image | Scene shuffle, image composite, final export. |
| Pipeline 2 — Shuffle + Image + Overlay | Scene shuffle, image composite, overlay, final export. |
| Pipeline 3 — Shuffle + Overlay | Scene shuffle, overlay, final export. |
| Pipeline 4 — Overlay Only | Overlay, final export. |

### Known limitations

- The architecture is optimized for a desktop single-user app, not a headless service.
- Most validation is runtime/manual rather than automated unit coverage.
- Overlay rendering can create temporary static assets that must be cleaned after each queue item.
- GUI fallback classes allow imports without PySide6, but full operation requires PySide6.

### Recommended future improvements

- Add a command-generation test harness around `PipelineManager` and `FFmpegBuilder`.
- Add project-file serialization/deserialization as a first-class architecture feature.
- Split GUI signal wiring docs into a dedicated reference if the editor grows.
- Add structured render-result objects instead of string-only output lists/log callbacks.

## Release Summary

The RC architecture is stable enough for controlled production validation: GUI state flows into modular pipeline modules, modules append to one FFmpeg graph, and the renderer handles queue execution, verification, cleanup, and Stop.
