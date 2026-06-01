# Render Pipeline

_Last updated: 2026-06-01_

## Version 1.0 Release Candidate

The render workflow is a sequential batch process managed by the GUI render thread and `BatchRenderer`.

### Implemented features

1. User adds one or more videos to the queue.
2. GUI copies current controls into `ProjectState`.
3. Render thread calls `BatchRenderer.render(state, progress, log)`.
4. Renderer validates FFmpeg and ffprobe.
5. Renderer chooses the batch output directory.
6. For each video:
   - create a safe output path;
   - remove stale `.rendering` output/audio files;
   - extract original audio for shuffle workflows;
   - build per-video render state for random templates/styles and seeded watermark layout;
   - build the FFmpeg command through `PipelineManager`;
   - optionally write developer debug files;
   - run FFmpeg with retry;
   - verify staged output with ffprobe;
   - replace the final output path;
   - verify final output quietly;
   - clean temp audio and overlay assets.
7. Failed videos are logged and skipped.
8. Stop requests terminate active processes and end the queue safely.

### Supported workflows

- Pipeline 1 uses shuffle, image composite, and export stages.
- Pipeline 2 uses shuffle, image composite, overlay, and export stages.
- Pipeline 3 uses shuffle, overlay, and export stages.
- Pipeline 4 uses overlay and export stages.

### Known limitations

- Rendering is sequential, not parallel.
- Progress is per-file rather than per-frame.
- FFmpeg stderr is summarized on failure rather than streamed continuously during successful renders.
- Full media validation still requires manual QA assets.

### Recommended future improvements

- Add structured render result metadata for each queue item.
- Add optional JSON/CSV batch report output.
- Add estimated-time/progress parsing from FFmpeg when desired.
- Add automated tests with short generated media fixtures.

## Release Summary

The RC render pipeline is complete for safe sequential batch rendering with atomic staging, verification, cleanup, and Stop handling.
