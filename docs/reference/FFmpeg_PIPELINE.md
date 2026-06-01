# FFmpeg Pipeline

_Last updated: 2026-06-01_

## Version 1.0 Release Candidate

The RC renderer builds one FFmpeg command per input video. Enabled modules append inputs and filter nodes to a shared `FilterGraph`, then `FFmpegBuilder` maps the final video label and optional audio into the output.

### Implemented features

- Base input is always the source video.
- Additional looped image/static overlay inputs are appended by image and overlay modules.
- Scene shuffle creates trim nodes for enabled segments and concatenates video only with `concat=n=...:v=1:a=0`.
- Shuffle workflows set audio mapping to original extracted audio when extraction succeeds, otherwise optional source audio mapping is used.
- Image composite adds the selected image as a looped input and emits layout/fade filter nodes.
- Overlay pipeline renders watermark/text/highlight static assets, loops them as inputs, and overlays them with timing/motion expressions.
- Sticker pipeline loops the selected sticker asset directly.
- Final export appends H.264/AAC output arguments, yuv420p pixel format, CRF, preset, and `+faststart`.
- Commands map the final filtered video label when a filtergraph exists, or `0:v`/`0:a?` when no filters exist.
- Developer mode can write `debug_filtergraph.txt` and `debug_fade_filter.txt`.

### Supported workflows

| Workflow | FFmpeg graph behavior |
| --- | --- |
| Pipeline 1 — Shuffle + Image | Source video trim/concat, image composite, final encode, original audio reattach if available. |
| Pipeline 2 — Shuffle + Image + Overlay | Shuffle graph, image graph, overlay graph, final encode, original audio reattach if available. |
| Pipeline 3 — Shuffle + Overlay | Shuffle graph, overlay graph, final encode, original audio reattach if available. |
| Pipeline 4 — Overlay Only | Overlay graph over original source timeline, optional source audio map. |

### Known limitations

- The output aspect-ratio filter dictionary exists in code but is not currently appended by `output_args`; current output size follows the filtergraph/source behavior.
- Unusual audio codecs can still require manual validation even though extraction falls back from stream copy to AAC.
- Command construction should be covered by automated tests before final production release.
- Looping static overlay inputs relies on `-shortest` to avoid extending renders.

### Recommended future improvements

- Add tests for audio/no-audio mapping in all four workflows.
- Add tests ensuring no invalid map is emitted when source audio is absent.
- Add tests for developer debug artifact gating.
- Decide whether aspect-ratio normalization should be active in final export or removed from the unused dictionary.

## Release Summary

The RC FFmpeg pipeline meets the single-encode architecture goal and avoids intermediate video-stage MP4s. Remaining work is validation coverage and clarifying final aspect-ratio behavior.
