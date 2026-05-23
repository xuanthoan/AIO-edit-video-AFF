"""Scene shuffle pipeline module.

Only video frames are shuffled. Audio is deliberately kept outside the shuffle
concat and reattached from the original timeline by the final FFmpeg command.
"""
from __future__ import annotations

from random import Random

from core.pipeline.base import FilterGraph, RenderJob, ShufflePlan, ShuffleSegment
from core.video.scene_detector import SceneDetector
from models.project_state import TimelineSegment
from core.video.segmenter import Segmenter


class SceneShufflePipeline:
    name = "scene_shuffle"

    def __init__(self, detector: SceneDetector | None = None, random: Random | None = None) -> None:
        self.detector = detector or SceneDetector()
        self.random = random or Random()

    def enabled(self, state) -> bool:
        return state.scene_shuffle.enabled

    def apply(self, job: RenderJob, graph: FilterGraph) -> FilterGraph:
        settings = job.state.scene_shuffle
        path_matches = settings.segment_video_path in {None, str(job.input_path)}
        has_manual = bool(settings.manual_segments) and path_matches
        source = "manual" if has_manual else "none"
        fallback_used = False
        scene_detect_count = 0
        if settings.manual_segments and not path_matches:
            graph.debug_events.append("[SHUFFLE] timeline segments belong to another selected video; using auto scene detect")
        if has_manual:
            timeline_segments = settings.manual_segments
            graph.debug_events.append("[SHUFFLE] manual segment mode active; scene detection skipped")
            scene_detect_count = len(timeline_segments)
        else:
            scenes = self.detector.detect(job.input_path, settings.sensitivity)
            scene_detect_count = len(scenes)
            fallback_used = scene_detect_count <= 1
            detected = Segmenter(settings.fallback_min_seconds, settings.fallback_max_seconds, random=self.random).ensure_segments(scenes, job.input_path)
            source = "auto_fallback" if fallback_used else "auto_scene"
            timeline_segments = [TimelineSegment(segment.start, segment.end, source=source) for segment in detected]

        segments = self._enabled_segments(timeline_segments)
        segments = self._shuffle_segments(segments, settings.random_mode, settings.keep_first_segment)

        graph.shuffle_plan = ShufflePlan([ShuffleSegment(segment.start_time, segment.end_time) for segment in segments])
        graph.debug_events.append(f"[SEGMENT] manual_segments_count={len(settings.manual_segments) if path_matches else 0}")
        graph.debug_events.append(f"[SEGMENT] scene_detect_segments={scene_detect_count}")
        graph.debug_events.append(f"[SEGMENT] fallback_random_split={'true' if fallback_used else 'false'}")
        graph.debug_events.append(f"[SEGMENT] fallback_range={settings.fallback_min_seconds:.1f}-{settings.fallback_max_seconds:.1f}")
        graph.debug_events.append(f"[SEGMENT] final_segment_count={len(segments)}")
        graph.debug_events.append(f"[SEGMENT] segment_source={source}")
        graph.debug_events.append(
            f"[SHUFFLE] source={source} segment_count={len(segments)} order={graph.shuffle_plan.order_summary}"
        )

        v_labels: list[str] = []
        for idx, segment in enumerate(segments):
            v = f"shv{idx}"
            graph.add_node(
                f"shuffle_trim_{idx}",
                f"[{graph.video_label}]trim=start={segment.start_time:.3f}:end={segment.end_time:.3f},setpts=PTS-STARTPTS[{v}]",
                None,
            )
            v_labels.append(f"[{v}]")
        out_v = "shuffled_v"
        graph.add_node("shuffle_concat", "".join(v_labels) + f"concat=n={len(segments)}:v=1:a=0[{out_v}]", out_v)
        graph.audio_label = "original_audio" if job.original_audio_path else "0:a?"
        graph.extra_args.extend(["-fps_mode", "passthrough", "-fflags", "+genpts", "-shortest"])
        return graph

    def _enabled_segments(self, segments: list[TimelineSegment]) -> list[TimelineSegment]:
        enabled = [segment.normalized() for segment in segments if segment.enabled and segment.duration > 0.05]
        return enabled or [TimelineSegment(0.0, 0.1, source="manual")]

    def _shuffle_segments(self, segments: list[TimelineSegment], random_mode: bool, keep_first_segment: bool) -> list[TimelineSegment]:
        if not random_mode or len(segments) <= 1:
            return segments
        indexed = list(enumerate(segments))
        locked = {index: segment for index, segment in indexed if segment.locked or (keep_first_segment and index == 0)}
        movable = [segment for index, segment in indexed if index not in locked]
        self.random.shuffle(movable)
        output: list[TimelineSegment] = []
        movable_index = 0
        for index in range(len(segments)):
            if index in locked:
                output.append(locked[index])
            else:
                output.append(movable[movable_index])
                movable_index += 1
        return output
