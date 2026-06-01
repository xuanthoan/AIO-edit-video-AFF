# Decisions

_Last updated: 2026-06-01_

## Version 1.0 Release Candidate

This document captures the current decisions reflected by the implementation.

### Implemented decisions

- Use one PySide6 desktop app rather than multiple scripts.
- Use a central `ProjectState` dataclass tree for GUI-to-renderer state transfer.
- Expose exactly four workflow modes for RC production.
- Use modular pipeline classes but merge their work into one final FFmpeg command per rendered video.
- Shuffle video-only segments and restore original audio separately.
- Keep image composite, overlay, and export stages as filtergraph fragments rather than intermediate MP4 stages.
- Store overlay positions and sizes as normalized ratios for cross-resolution behavior.
- Render text/highlight/watermark overlays as minimal static assets and loop them in FFmpeg.
- Treat SVG Highlight and Sticker Beauty SVG templates as highlight styles.
- Keep safe-area and snap behavior internal instead of exposing a separate safe-area settings panel in the current UI.
- Use output staging and ffprobe verification before finalizing each output file.

### Supported workflows

The four RC workflows are fixed as:

1. Pipeline 1 — Shuffle + Image.
2. Pipeline 2 — Shuffle + Image + Overlay.
3. Pipeline 3 — Shuffle + Overlay.
4. Pipeline 4 — Overlay Only.

### Known limitations accepted for RC

- Automated testing is not complete.
- Sequential rendering is acceptable for RC.
- Preview/export parity is validated manually.
- Full project persistence is deferred.
- Packaging and installer polish are deferred.

### Recommended future improvements

- Revisit aspect-ratio normalization in final export and decide whether to enable or remove the unused filter map.
- Add formal schema/versioning to project state if persistence becomes a release feature.
- Add test-driven documentation generation for workflow and file-structure tables.
- Add an explicit deprecation policy for legacy UI/helper modules.

## Release Summary

The RC decisions favor a stable, understandable batch-rendering app: a small set of workflows, normalized overlay state, single-command FFmpeg exports, and minimal intermediate artifacts.
