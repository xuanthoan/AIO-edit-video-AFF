# Testing

_Last updated: 2026-06-01_

## Version 1.0 Release Candidate

The RC has limited automated coverage and should be validated with both static checks and manual media renders.

### Implemented features to validate

- GUI importability and application startup.
- Four workflow modes.
- Scene detection/fallback/manual segments.
- Image composite layout and fade overlap.
- Text, watermark, highlight, SVG highlight, Sticker Beauty SVG, and sticker overlays.
- Preview playback, preview cache reset, playhead scrubbing, timeline block edit behavior, and overlay visibility windows.
- FFmpeg command generation, audio mapping, output staging, verification, temporary cleanup, and Stop.

### Required checks

```bash
python -m compileall main.py core gui models
```

Expected result: command exits with status 0.

### Manual render matrix

| Workflow | With audio | No audio | Required result |
| --- | --- | --- | --- |
| Pipeline 1 — Shuffle + Image | Test | Test | Valid MP4; original audio retained when present; no invalid audio map when absent. |
| Pipeline 2 — Shuffle + Image + Overlay | Test | Test | Valid MP4 with image composite and overlays. |
| Pipeline 3 — Shuffle + Overlay | Test | Test | Valid MP4 with shuffled video and overlays. |
| Pipeline 4 — Overlay Only | Test | Test | Valid MP4 on original timeline with overlays. |

### Overlay QA matrix

- Text templates: Orange White, White Black, Pink White, Red White, Yellow White, Pastel Pink, Green White, Random Template.
- Highlight styles: standard built-in styles, Random Style, Blue Tag SVG, Orange Tag SVG, Sticker Beauty SVG 1, Sticker Beauty SVG 2, Sticker Beauty SVG 3.
- Sticker controls: position, scale, rotation, start/end time, motion.
- Motion presets: None, Fade In, Fade Out, Pop, Bounce, Scale, Scale Up, Scale Down, Float, Slide directions, Pulse, Shake, Rotate Float.

### Command-generation tests to add

- No-audio inputs do not produce mandatory audio maps.
- Shuffle workflows map extracted original audio only when extraction succeeds.
- Overlay-only commands do not require shuffle/image labels.
- Static overlay inputs include `-shortest` behavior.
- Developer debug artifacts are written only when developer mode is true.

### Known limitations

- No committed media fixtures are documented for the RC.
- Visual QA remains manual.
- FFmpeg command tests are planned but not implemented in this documentation refresh.

### Recommended future improvements

- Generate synthetic video/audio fixtures in tests to avoid copyrighted samples.
- Add golden SVG output tests.
- Add snapshot tests for filtergraph strings.
- Add GUI smoke tests around signal wiring if a Qt test harness is introduced.

## Release Summary

The RC is ready for validation, but production readiness depends on completing the manual matrix and adding automated command/filtergraph coverage.
