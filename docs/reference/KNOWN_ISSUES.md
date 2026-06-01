# Known Issues

_Last updated: 2026-06-01_

## Version 1.0 Release Candidate

### Implemented features that close prior risk areas

- Original audio is extracted before shuffle and reattached after video-only segment concat.
- Queue processing skips failed videos instead of aborting the entire batch.
- `.rendering` output staging prevents partial final MP4 files from appearing as completed outputs.
- Developer debug artifacts are controlled by developer mode.
- Text templates use locked built-in color pairs.
- SVG Highlight and Sticker Beauty templates are part of the highlight style system.

### Supported workflows

Known-issue validation applies to all RC workflows:

- Pipeline 1 — Shuffle + Image.
- Pipeline 2 — Shuffle + Image + Overlay.
- Pipeline 3 — Shuffle + Overlay.
- Pipeline 4 — Overlay Only.

### Known limitations

- Automated test coverage is incomplete.
- Preview/export parity must be checked manually for timing, motion, safe-area position, and SVG sizing.
- PySceneDetect is optional; without it, scene shuffle falls back to random time segments.
- Very unusual source media can expose FFmpeg probing, timestamp, or codec edge cases.
- Packaging on a clean target machine remains unvalidated in this documentation refresh.
- Full project/session persistence is not complete RC functionality.

### Recommended future improvements

- Add CI checks for syntax/imports and command-generation tests.
- Add real-media smoke tests with generated no-audio and with-audio clips.
- Add explicit dependency status panel in the GUI.
- Add SVG template schema checks for required layout nodes.
- Add visual comparison tools for preview/export overlay parity.

## Release Summary

No new code bugs were introduced by this documentation refresh. Remaining known issues are validation, packaging, automation, and dependency-hardening items.
