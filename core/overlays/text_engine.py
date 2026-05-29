"""FFmpeg overlay engine for Qt-rendered social typography assets."""
from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from core.normalized_layout import NormalizedLayoutEngine
from core.overlays.motion_engine import MotionEngine
from core.overlays.svg_highlight_renderer import SVGHighlightRenderer
from core.overlays.template_manager import TemplateManager
from core.overlays.typography_engine import SocialTypographyRenderer
from models.text_overlay import TextOverlay


class TextEngine:
    _logger = logging.getLogger(__name__)

    def __init__(self, templates=None, prefix: str = "text") -> None:
        self.templates = templates or TemplateManager()
        self.prefix = prefix
        self.motion = MotionEngine()
        self.typography = SocialTypographyRenderer()
        self.svg_renderer = SVGHighlightRenderer()
        self.layout = NormalizedLayoutEngine()
        self._asset_cache: dict[tuple[str, str, float, int, int], Path] = {}

    def build_filter(
        self,
        video_label: str,
        text_label: str,
        overlay: TextOverlay,
        suffix: str = "",
    ) -> tuple[str, str]:
        out = f"{self.prefix}_v{suffix}"
        prepared = f"{self.prefix}_src{suffix}"
        x, y, enable = self.motion.position_expr(overlay.x, overlay.y, overlay.motion, overlay.start_time, overlay.end_time, overlay.motion_speed, overlay.motion_strength)
        template_name = getattr(overlay, "template", getattr(overlay, "style", ""))
        svg_template = getattr(self.templates, "svg_template_path", lambda _name: None)(template_name)
        base_scale = min(max(float(getattr(overlay, "scale", 1.0) or 1.0), 0.01), 10.0)
        base_width = "iw" if abs(base_scale - 1.0) < 0.001 else f"iw*{base_scale:.6f}"
        if svg_template:
            width_expr, height_expr = self._svg_highlight_scale_expr(base_width, overlay)
        else:
            width_expr, height_expr = self.motion.region_scale_expr(base_width, overlay.motion, overlay.start_time, overlay.end_time, speed=overlay.motion_speed, strength=overlay.motion_strength)
        alpha_filter = self.motion.alpha_filter(overlay.motion, overlay.start_time, overlay.end_time, speed=overlay.motion_speed, strength=overlay.motion_strength)
        rotation_expr = self.motion.rotation_expr(float(getattr(overlay, "rotation", 0.0) or 0.0), overlay.motion, overlay.start_time, overlay.motion_speed, overlay.motion_strength)
        chain = (
            f"[{text_label}]scale=w='{width_expr}':h='{height_expr}':eval=frame,"
            f"rotate='{rotation_expr}':ow=rotw(iw):oh=roth(ih):c=none"
            f"{alpha_filter}[{prepared}];"
            f"[{video_label}][{prepared}]overlay=x={x}:y={y}:eval=frame:enable='{enable}'[{out}]"
        )
        return chain, out

    def _svg_highlight_scale_expr(self, base_width: str, overlay: TextOverlay) -> tuple[str, str]:
        """Apply user scale once, then clamp SVG highlight animation to a small multiplier."""
        factor = self.motion._scale_factor_expr(overlay.motion, overlay.start_time, overlay.end_time, overlay.motion_speed, overlay.motion_strength)
        if factor == "1.00":
            return base_width, "-1"
        animation_scale = f"min(max({factor}\\,0.92)\\,1.08)"
        return f"({base_width})*({animation_scale})", "-1"

    def _log_svg_frame_scale_debug(
        self,
        overlay: TextOverlay,
        base_width: float,
        base_height: float,
        output_resolution: tuple[int, int],
        render_mode: str,
    ) -> None:
        user_scale = min(max(float(getattr(overlay, "scale", 1.0) or 1.0), 0.01), 10.0)
        for frame_index in range(5):
            local_t = max(0.0, (frame_index / 30.0 - float(overlay.start_time)) * max(float(overlay.motion_speed), 0.05))
            raw_animation_scale = self.motion.preview_scale(overlay.motion, local_t, max(float(overlay.end_time - overlay.start_time), 0.1), float(overlay.motion_strength))
            animation_scale = min(max(raw_animation_scale, 0.92), 1.08)
            final_draw_width = base_width * user_scale * animation_scale if base_width else 0.0
            final_draw_height = base_height * user_scale * animation_scale if base_height else 0.0
            self._logger.info(
                "[SVG_FRAME_SCALE] frame_index=%s base_image_width=%.3f base_image_height=%.3f "
                "user_scale=%.6f animation_scale=%.6f final_draw_width=%.3f final_draw_height=%.3f "
                "output_resolution=%s render_mode=%s",
                frame_index,
                base_width,
                base_height,
                user_scale,
                animation_scale,
                final_draw_width,
                final_draw_height,
                output_resolution,
                render_mode,
            )

    def render_asset(
        self,
        overlay: TextOverlay,
        canvas_width: int,
        canvas_height: int,
        temp_files: list[Path] | None = None,
    ) -> Path:
        template_name = getattr(overlay, "template", getattr(overlay, "style", ""))
        template = self.templates.get(template_name)
        font_ratio = overlay.effective_font_ratio()
        svg_template = getattr(self.templates, "svg_template_path", lambda _name: None)(template_name)
        svg_mtime_ns = 0
        if svg_template:
            svg_path = self._resolve_svg_path(svg_template)
            try:
                svg_mtime_ns = svg_path.stat().st_mtime_ns
            except OSError:
                svg_mtime_ns = 0
        key = (overlay.text, template_name, round(font_ratio, 6), canvas_width, canvas_height, svg_mtime_ns)
        path = self._asset_cache.get(key)
        if path is None or not path.exists():
            path = self._new_asset_path()
            if svg_template:
                image = self.svg_renderer.render_image(
                    svg_template,
                    overlay.text,
                    self.layout.denormalize_font_size(font_ratio, canvas_height),
                    canvas_width,
                    canvas_height,
                    mode="export",
                    logical_width=getattr(overlay, "w", 0.0),
                    logical_height=getattr(overlay, "h", 0.0),
                    item_scale=float(getattr(overlay, "scale", 1.0) or 1.0),
                    output_resolution=(canvas_width, canvas_height),
                )
                self._log_svg_frame_scale_debug(
                    overlay,
                    float(image.width()),
                    float(image.height()),
                    (canvas_width, canvas_height),
                    "export",
                )
                if not image.save(str(path), "PNG"):
                    raise RuntimeError(f"Unable to write SVG highlight PNG: {path}")
            else:
                self.typography.render_png(path, overlay.text, template, font_ratio, canvas_width, canvas_height)
            self._asset_cache[key] = path
        if temp_files is not None and path not in temp_files:
            temp_files.append(path)
        return path

    @staticmethod
    def _new_asset_path() -> Path:
        handle = tempfile.NamedTemporaryFile(prefix="autovideoaff_text_region_", suffix=".png", delete=False)
        path = Path(handle.name)
        handle.close()
        return path

    @staticmethod
    def _resolve_svg_path(template_path: str) -> Path:
        from utils.ffmpeg_helper import app_root

        return app_root() / template_path
