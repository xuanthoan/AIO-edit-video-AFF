"""FFmpeg overlay engine for smart sales highlight text regions."""
from __future__ import annotations

from core.overlays.highlight_library import HighlightStyleManager
from core.overlays.text_engine import TextEngine


class HighlightEngine(TextEngine):
    def __init__(self) -> None:
        super().__init__(templates=HighlightStyleManager(), prefix="highlight")

    def build_filter(
        self,
        video_label: str,
        text_label: str,
        overlay,
        suffix: str = "",
    ) -> tuple[str, str]:
        out = f"{self.prefix}_v{suffix}"
        prepared = f"{self.prefix}_src{suffix}"
        x, y, enable = self.motion.position_expr(
            overlay.x,
            overlay.y,
            overlay.motion,
            overlay.start_time,
            overlay.end_time,
            overlay.motion_speed,
            overlay.motion_strength,
        )
        base_scale = max(0.05, float(getattr(overlay, "scale", 1.0) or 1.0))
        width_expr, height_expr = self.motion.region_scale_expr(
            f"iw*{base_scale:.6f}",
            overlay.motion,
            overlay.start_time,
            overlay.end_time,
            speed=overlay.motion_speed,
            strength=overlay.motion_strength,
        )
        alpha_filter = self.motion.alpha_filter(
            overlay.motion,
            overlay.start_time,
            overlay.end_time,
            speed=overlay.motion_speed,
            strength=overlay.motion_strength,
        )
        chain = (
            f"[{text_label}]scale=w='{width_expr}':h='{height_expr}':eval=frame{alpha_filter}[{prepared}];"
            f"[{video_label}][{prepared}]overlay=x={x}:y={y}:eval=frame:enable='{enable}'[{out}]"
        )
        return chain, out
