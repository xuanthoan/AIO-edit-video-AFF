# Project Status

_Last updated: 2026-06-01_

## Version 1.0 Release Candidate

AutoVideoAFF is at a **Version 1.0 Release Candidate** documentation baseline. The current codebase implements the core desktop workflow for batch short-form video editing without requiring feature work for the RC scope.

### Implemented features

- PySide6 desktop application entry point and main window.
- Three-column editor layout: left queue/log column, center preview/timeline column, and right workflow controls column.
- Four workflow modes: Shuffle + Image, Shuffle + Image + Overlay, Shuffle + Overlay, and Overlay Only.
- Queue-based batch rendering with per-video progress/log callbacks.
- Scene shuffle with automatic PySceneDetect scenes, manual timeline segments, randomized fallback segments, segment enable/lock flags, and keep-first behavior.
- Image compositing with image pool selection, crop focus, image height, overlap, and fade configuration.
- Watermark, text, highlight, and sticker overlays with normalized positioning and timeline visibility.
- SVG Highlight styles: Blue Tag SVG and Orange Tag SVG.
- Sticker Beauty SVG templates: Sticker Beauty SVG 1, 2, and 3.
- Mini timeline for playback, playhead scrubbing, overlay timing edits, manual cuts, undo/redo cut actions, segment list, and overlay list.
- Preview playback controller and cached preview-frame extraction.
- FFmpeg single-command final export with modular filtergraph composition.
- Shuffle-workflow original audio extraction and reattachment.
- Atomic output staging, ffprobe verification, retry-on-FFmpeg-failure, Stop handling, and temporary-file cleanup.

### Supported workflows

| Pipeline | Status | Notes |
| --- | --- | --- |
| Pipeline 1 — Shuffle + Image | Implemented | Shuffles video-only segments, composites one selected image from the image pool, and exports final MP4. |
| Pipeline 2 — Shuffle + Image + Overlay | Implemented | Full workflow with shuffle, image composite, text/highlight/sticker/watermark overlays, and final export. |
| Pipeline 3 — Shuffle + Overlay | Implemented | Shuffles video-only segments and applies overlays without image compositing. |
| Pipeline 4 — Overlay Only | Implemented | Applies overlays to the original input timeline without scene shuffle. |

### Known limitations

- Automated test coverage is not yet complete.
- Release readiness depends on manual render QA with representative media.
- Preview/export visual parity should be validated for each motion preset and SVG template before production distribution.
- Dependency availability is environment-specific, especially FFmpeg/ffprobe, PySide6, PySceneDetect, and Qt SVG support.
- Timeline save/load UI hooks exist, but full project persistence is not documented as a completed RC feature.

### Recommended future improvements

- Add unit tests for FFmpegBuilder, PipelineManager, scene fallback segmentation, overlay timing, and SVG sizing.
- Add golden-image checks for SVG Highlight and Sticker Beauty output.
- Add a batch summary artifact containing successes, skipped files, and error tails.
- Add project-file persistence UI and validation.
- Add installer/build documentation for Windows distribution.

## Current status by subsystem

| Subsystem | Status | Summary |
| --- | --- | --- |
| GUI shell | Complete for RC | Main window, queue, preview, mini timeline, workflow controls, and logs are wired. |
| Scene shuffle | Complete for RC | Auto/manual/fallback segments feed FFmpeg trim/concat filtergraph. |
| Image composite | Complete for RC | Single deterministic image input per rendered video, with layout/fade plan debug events. |
| Text overlay | Complete for RC | Seven locked built-in templates plus Random Template selection at render time. |
| Highlight overlay | Complete for RC | Built-in styles, random wording/style support, SVG tag templates, and Sticker Beauty SVG templates. |
| Sticker overlay | Complete for RC | External image stickers with normalized scale, rotation, timing, and motion. |
| Watermark overlay | Complete for RC | Text watermark asset generation with density/opacity/font options and seeded layout. |
| Preview/timeline | Complete for RC | Timeline controls overlay and segment timing; preview playback is cached and playhead-aware. |
| Export pipeline | Complete for RC | Single FFmpeg command, output staging, verification, skip-on-failure, and process stop. |
| Testing | Partial | Manual matrix exists; automated checks still need expansion. |

## Release Summary

The RC is suitable for controlled validation of batch social-video workflows. Documentation now reflects the current implementation and removes completed TODO-style notes. Remaining work should focus on testing, packaging, dependency diagnostics, and production hardening rather than core feature additions.
