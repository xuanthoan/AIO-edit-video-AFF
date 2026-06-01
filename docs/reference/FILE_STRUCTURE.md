# File Structure

_Last updated: 2026-06-01_

## Version 1.0 Release Candidate

This file documents the current repository areas used by the RC implementation.

### Implemented structure

```text
main.py
  Application entry point. Creates QApplication and MainWindow.

core/
  __init__.py
  motion_engine.py
  normalized_layout.py
  safe_area_engine.py

core/compositor/
  fade_mask.py
  image_compositor.py

core/overlays/
  font_units.py
  highlight_engine.py
  highlight_library.py
  motion_engine.py
  sticker_engine.py
  svg_highlight_renderer.py
  template_manager.py
  text_engine.py
  transform.py
  typography_engine.py
  watermark_engine.py

core/pipeline/
  base.py
  compositor_pipeline.py
  export_pipeline.py
  manager.py
  overlay_pipeline.py
  shuffle_pipeline.py

core/renderer/
  batch_renderer.py
  ffmpeg_builder.py
  preview_renderer.py

core/video/
  concat_engine.py
  scene_detector.py
  segmenter.py
  timestamp_manager.py

gui/
  export_panel.py
  main_window.py
  mini_timeline.py
  preview_canvas.py
  queue_panel.py
  timeline_panel.py
  toolbar.py
  workflow_panel.py

models/
  highlight_overlay.py
  overlay.py
  project_state.py
  sticker_overlay.py
  text_overlay.py
  watermark_overlay.py

assets/vector_highlight_templates/
  orange_tag_template.svg
  simple_blue_tag_template.svg
  sticker_beauty_01-1.svg
  sticker_beauty_02.svg
  sticker_beauty_03.svg
  sticker_beauty_04.svg
  sticker_beauty_svg_1.svg
  sticker_beauty_svg_2.svg
  sticker_beauty_svg_3.svg

docs/reference/
  ANIMATION_SYSTEM.md
  ARCHITECTURE.md
  DECISIONS.md
  FFmpeg_PIPELINE.md
  FILE_STRUCTURE.md
  KNOWN_ISSUES.md
  NEXT_SESSION_HANDOFF.md
  RENDER_PIPELINE.md
  TESTING.md

Root documentation:
  README.md
  PROJECT_STATUS.md
  CURRENT_TASK.md
  BUGS.md
```

### Supported workflows reflected by structure

- GUI files collect user choices and update `ProjectState`.
- Models hold workflow, scene, export, and overlay configuration.
- Core pipeline files map state into scene shuffle, image composite, overlay, and final export modules.
- Renderer files execute preview extraction and final batch export.
- SVG template assets provide the vector bases for highlight and Sticker Beauty styles.

### Known limitations

- Some legacy GUI modules remain as compatibility stubs or lightly used panels.
- The docs focus on the primary RC paths and do not describe every helper imported by renderer utilities.
- SVG template filenames include both active RC templates and older design assets retained for reference.

### Recommended future improvements

- Add a generated file inventory check in CI to keep this document synchronized.
- Mark deprecated/legacy helper modules explicitly if they are removed from active UI flows.
- Add packaging-file documentation once distribution artifacts are finalized.

## Release Summary

The current file structure supports the RC scope without feature gaps: GUI, state, core engines, modular pipeline, renderer, SVG assets, and reference docs are all present.
