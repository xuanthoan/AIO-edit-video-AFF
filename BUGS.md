# Bugs and Known Limitations

_Last updated: 2026-06-01_

## Version 1.0 Release Candidate

### Implemented features relevant to past bugs

- Shuffle workflows now operate on video-only segments and reattach original audio when extraction succeeds.
- Output files are staged as `.rendering` files and verified before final rename.
- Batch rendering logs failed videos and continues with the remaining queue.
- Stop requests terminate active rendering through the process manager.
- Developer debug files are gated by export developer mode.
- Overlay assets are generated as minimal-region static inputs rather than full-frame video intermediates.

### Supported workflows

Known issues should be tested against all four RC workflows:

1. Pipeline 1 — Shuffle + Image.
2. Pipeline 2 — Shuffle + Image + Overlay.
3. Pipeline 3 — Shuffle + Overlay.
4. Pipeline 4 — Overlay Only.

### Known limitations and remaining issues

| Area | Status | Notes |
| --- | --- | --- |
| Automated testing | Open | Manual QA matrix exists, but command/filtergraph/media tests are not fully automated. |
| Dependency diagnostics | Open | Missing FFmpeg/ffprobe is handled, but broader user-facing dependency checks can improve. |
| Preview/export parity | Watch | Preview is close enough for editing but should be manually checked for each motion preset and SVG template. |
| SVG template assumptions | Watch | SVG highlight rendering depends on expected template IDs/bounds/text-safe-area structure. |
| Audio edge cases | Watch | No-audio videos are supported, but unusual audio codecs or extraction failures need sample-based validation. |
| Project persistence | Open | Timeline save/load hooks exist; full project-session persistence is not treated as complete for RC. |
| Packaging | Open | Clean-machine packaging and bundled binary validation remain future work. |

### Recommended future improvements

- Add regression tests for no-audio, original-audio reattachment, and optional audio mapping.
- Add tests that ensure developer debug artifacts are only written in developer mode.
- Add fixture-based tests for SVG Highlight and Sticker Beauty template rendering.
- Add clearer GUI messages for missing optional dependencies such as PySceneDetect.
- Add reproducible release packaging instructions and smoke tests.

## Release Summary

No blocking code bug is documented as unresolved in the RC documentation baseline, but the release should not be called production-ready until automated and manual validation gates are completed with real media.
