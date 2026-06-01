# Animation System

_Last updated: 2026-06-01_

## Version 1.0 Release Candidate

The animation system is shared by preview and export through normalized overlay state and FFmpeg expression generation.

### Implemented features

- `MotionPreset` supports None, Fade In, Fade Out, Bounce, Pop, Scale, Scale Up, Scale Down, Float, Shake, Slide Left, Slide Right, Slide Up, Slide Down, Pulse, Rotate Float, Drift, and backward-compatible aliases.
- Highlight UI exposes sales-oriented animation labels, including aliases such as Wiggle, Zoom In, Zoom Out, and Random Animation.
- Text and sticker controls expose motion speed and motion strength.
- Overlay timing uses `start_time`, `end_time`, and derived `duration` on `OverlayBase`.
- Preview evaluates transforms at the current playhead time and hides overlays outside their timing windows.
- Export uses per-overlay FFmpeg expressions for alpha, scale, position, and rotation where supported.
- Static overlay assets are looped as FFmpeg inputs and composited with timeline enable expressions.

### Supported workflows

- Pipeline 2, Pipeline 3, and Pipeline 4 support overlay motion.
- Pipeline 1 has no overlay motion because overlays are not active in the workflow.
- Highlights, text, and stickers use the same timing model; watermark motion is handled by watermark layout/floating settings rather than mini-timeline blocks.

### Known limitations

- Preview and FFmpeg may not be pixel-perfect for every easing/motion combination.
- Complex motion QA is still manual.
- Some labels are compatibility aliases that map to current `MotionPreset` values.
- Rotation/scale interaction should be checked manually for very large sticker and SVG highlight sizes.

### Recommended future improvements

- Add unit tests for motion preset alias mapping.
- Add numeric tests for preview transform values at key times.
- Add FFmpeg expression tests for alpha, position, scale, and rotation.
- Add visual regression clips for motion presets.

## Release Summary

The RC animation system is implemented for timeline-driven overlay editing and final export, with remaining work focused on automated parity tests and visual regression coverage.
