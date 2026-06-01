# Current Task

_Last updated: 2026-06-01_

## Version 1.0 Release Candidate

The active task is **Release Candidate validation and documentation stabilization**. No new features, GUI changes, render changes, or business-logic changes are required for the current milestone.

### Implemented features

- Four RC workflow modes are implemented and documented.
- GUI layout is implemented as queue/log, preview/timeline, and workflow-control columns.
- SVG Highlight templates and Sticker Beauty SVG templates are implemented through the highlight style system.
- Preview, mini timeline, overlay timing, manual segment editing, and batch export are implemented for RC validation.
- Export uses a modular single-encode FFmpeg graph with output staging and verification.

### Supported workflows

- Pipeline 1 — Shuffle + Image.
- Pipeline 2 — Shuffle + Image + Overlay.
- Pipeline 3 — Shuffle + Overlay.
- Pipeline 4 — Overlay Only.

### Known limitations

- Automated coverage remains incomplete.
- Manual render QA is still required across workflows, audio/no-audio inputs, SVG templates, and motion presets.
- Packaging/install validation on a clean Windows machine remains future work.

### Recommended future improvements

- Add automated command-generation and filtergraph tests.
- Add visual regression checks for overlays and SVG templates.
- Add a batch summary report.
- Add project-file persistence and user-facing dependency diagnostics.

## Current RC checklist

1. Run static import/syntax checks.
2. Validate FFmpeg command construction for all four workflows.
3. Run short manual media exports for audio and no-audio sources.
4. Verify preview/timeline behavior against final output for representative overlays.
5. Verify SVG Highlight and Sticker Beauty templates render readable text and clean bounds.
6. Verify Stop, failed-video skipping, temporary-file cleanup, and output-folder behavior.

## Release Summary

This task closes the documentation refresh phase. The next session should prioritize validation evidence and test automation, not feature expansion.
