from __future__ import annotations

import logging
from xml.etree import ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)

from utils.ffmpeg_helper import app_root

try:
    from PySide6.QtCore import QByteArray, Qt
    from PySide6.QtGui import QColor, QFont, QFontInfo, QFontMetricsF, QImage, QPainter
    from PySide6.QtSvg import QSvgRenderer
except ImportError:  # allows non-GUI CI imports when PySide6 is absent
    QByteArray = Qt = QRectF = QColor = QFont = QFontInfo = QFontMetricsF = QImage = QPainter = QSvgRenderer = None


class SVGHighlightRenderer:
    BASE_WIDTH = 1073.0
    BASE_HEIGHT = 646.0
    TEXT_SIZE_MULTIPLIER = 4.5
    _logger = logging.getLogger(__name__)

    def render_image(
        self,
        template_path: str,
        text: str,
        font_size: float,
        canvas_width: int,
        canvas_height: int,
        *,
        mode: str = "export",
        logical_width: float | None = None,
        logical_height: float | None = None,
        item_scale: float = 1.0,
        preview_video_rect: tuple[float, float, float, float] | None = None,
        output_resolution: tuple[int, int] | None = None,
    ):
        if QImage is None:
            raise RuntimeError("PySide6 is required to render SVG highlight assets.")
        svg_bytes, output_width, output_height, text_layout, layout_debug = self._build_svg_bytes(
            template_path, text, font_size, canvas_width, logical_width=logical_width, logical_height=logical_height
        )
        is_tag_svg = "blue_tag_template" in template_path or "orange_tag_template" in template_path or "simple_blue_tag_template" in template_path
        if is_tag_svg:
            self._logger.info("[BLUE_TAG_RENDER] mode=%s", mode)
            self._logger.info("[BLUE_TAG_RENDER] text_len = %s", len((text or "")))
            self._logger.info("[BLUE_TAG_RENDER] logical_width = %s", logical_width if logical_width is not None else output_width)
            self._logger.info("[BLUE_TAG_RENDER] logical_height = %s", logical_height if logical_height is not None else output_height)
            self._logger.info("[BLUE_TAG_RENDER] stored_scale = %s", item_scale)
            self._logger.info("[BLUE_TAG_RENDER] final_visual_width = %s", output_width * max(0.0, float(item_scale)))
            self._logger.info("[BLUE_TAG_RENDER] final_visual_height = %s", output_height * max(0.0, float(item_scale)))
        self._logger.info("[SVG_LAYOUT] mode=%s text_len=%s", mode, len((text or "")))
        self._logger.info("[SVG_LAYOUT] final_frame_width=%s", layout_debug["final_frame_width"])
        self._logger.info("[SVG_LAYOUT] final_frame_height=%s", layout_debug["final_frame_height"])
        self._logger.info("[SVG_LAYOUT] rendered_image_width=%s", layout_debug["rendered_image_width"])
        self._logger.info("[SVG_LAYOUT] rendered_image_height=%s", layout_debug["rendered_image_height"])
        self._logger.info("[SVG_LAYOUT] font_size=%s", layout_debug["font_size"])
        self._logger.info("[SVG_LAYOUT] scale=%s", item_scale)
        self._logger.info("[SVG_COMPARE] mode=%s", mode)
        self._logger.info("[SVG_COMPARE] text_len=%s", len((text or "")))
        self._logger.info("[SVG_COMPARE] font_size=%s", layout_debug["font_size"])
        self._logger.info("[SVG_COMPARE] text_width=%s", layout_debug["text_width"])
        self._logger.info("[SVG_COMPARE] frame_width=%s", layout_debug["final_frame_width"])
        self._logger.info("[SVG_COMPARE] frame_height=%s", layout_debug["final_frame_height"])
        self._logger.info("[SVG_COMPARE] render_image_width=%s", layout_debug["rendered_image_width"])
        self._logger.info("[SVG_COMPARE] render_image_height=%s", layout_debug["rendered_image_height"])
        self._logger.info("[SVG_COMPARE] item_scale=%s", item_scale)
        self._logger.info("[SVG_COMPARE] final_visual_width=%s", layout_debug["rendered_image_width"] * max(0.0, float(item_scale)))
        self._logger.info("[SVG_COMPARE] final_visual_height=%s", layout_debug["rendered_image_height"] * max(0.0, float(item_scale)))
        self._logger.info("[SVG_SIZE] mode=%s", mode)
        self._logger.info("[SVG_SIZE] text=%r", text)
        self._logger.info("[SVG_SIZE] font_size=%s", font_size)
        self._logger.info("[SVG_SIZE] logical_width=%s", logical_width if logical_width is not None else output_width)
        self._logger.info("[SVG_SIZE] logical_height=%s", logical_height if logical_height is not None else output_height)
        self._logger.info("[SVG_SIZE] item_scale=%s", item_scale)
        self._logger.info("[SVG_SIZE] preview_video_rect=%s", preview_video_rect)
        self._logger.info("[SVG_SIZE] output_resolution=%s", output_resolution or (canvas_width, canvas_height))
        self._logger.info("[SVG_SIZE] final_render_width=%s", output_width)
        self._logger.info("[SVG_SIZE] final_render_height=%s", output_height)
        renderer = QSvgRenderer(QByteArray(svg_bytes))
        if not renderer.isValid():
            raise ValueError(f"Invalid SVG renderer for template: {template_path}")
        image = QImage(max(1, int(output_width)), max(1, int(output_height)), QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        painter.save()
        renderer.render(painter)
        painter.restore()
        self._paint_text(painter, text_layout, output_width, output_height)
        painter.end()
        self._log_color_debug(mode, image, is_tag_svg=is_tag_svg)
        return image

    def _build_svg_bytes(self, template_path: str, text: str, font_size: float, canvas_width: int, *, logical_width: float | None = None, logical_height: float | None = None):
        source_path = app_root() / template_path
        self._logger.info("[SVG] loading template path=%s", source_path.resolve())
        if not source_path.exists():
            raise FileNotFoundError(f"SVG template not found: {source_path}")
        raw = source_path.read_text(encoding="utf-8")
        root = ET.fromstring(raw)

        view_box = root.attrib.get("viewBox", "").strip().replace(",", " ").split()
        if len(view_box) != 4:
            raise ValueError("Template missing valid viewBox.")
        vb_x = float(view_box[0])
        vb_y = float(view_box[1])
        vb_width = float(view_box[2])
        vb_height = float(view_box[3])

        text_node = self._find_required(root, "dynamic_text")
        raw_text = (text or "").replace("\r\n", "\n").replace("\r", "\n")
        lines = raw_text.split("\n")
        if not lines or all(not line.strip() for line in lines):
            lines = [" "]

        resolved_font_size = self._resolve_font_size(text_node, font_size, vb_height)
        effective_font_size = resolved_font_size * self.TEXT_SIZE_MULTIPLIER
        max_line_width, line_height = self._measure_text_block(lines, effective_font_size)

        orange_stroke = self._find_required(root, "orange_stroke")
        orange_frame = self._find_required(root, "orange_frame")
        navy_stroke = self._find_required(root, "navy_stroke")
        navy_panel = self._find_required(root, "navy_panel")

        padding_left = 60.0
        padding_right = 60.0
        padding_top = 40.0
        padding_bottom = 40.0

        original_panel_width = float(navy_panel.get("width", "0"))
        original_panel_height = float(navy_panel.get("height", "0"))
        layout = self._compute_layout(
            original_panel_width=original_panel_width,
            original_panel_height=original_panel_height,
            max_line_width=max_line_width,
            line_height=line_height,
            line_count=len(lines),
            padding_left=padding_left,
            padding_right=padding_right,
            padding_top=padding_top,
            padding_bottom=padding_bottom,
            resolved_font_size=resolved_font_size,
            canvas_width=canvas_width,
            min_logical_width=max(0.0, float(logical_width or 0.0)),
            min_logical_height=max(0.0, float(logical_height or 0.0)),
        )
        width_delta = layout["width_delta"]
        height_delta = layout["height_delta"]

        for node in (orange_stroke, orange_frame, navy_stroke, navy_panel):
            node.set("width", f"{max(1.0, float(node.get('width', '0')) + width_delta):.3f}")
            node.set("height", f"{max(1.0, float(node.get('height', '0')) + height_delta):.3f}")

        left_bound = min(float(orange_stroke.get("x", "0")), float(orange_frame.get("x", "0")), float(navy_stroke.get("x", "0")), float(navy_panel.get("x", "0")))
        right_bound = max(
            float(orange_stroke.get("x", "0")) + float(orange_stroke.get("width", "0")),
            float(orange_frame.get("x", "0")) + float(orange_frame.get("width", "0")),
            float(navy_stroke.get("x", "0")) + float(navy_stroke.get("width", "0")),
            float(navy_panel.get("x", "0")) + float(navy_panel.get("width", "0")),
        )
        top_bound = min(float(orange_stroke.get("y", "0")), float(orange_frame.get("y", "0")), float(navy_stroke.get("y", "0")), float(navy_panel.get("y", "0")))
        bottom_bound = max(
            float(orange_stroke.get("y", "0")) + float(orange_stroke.get("height", "0")),
            float(orange_frame.get("y", "0")) + float(orange_frame.get("height", "0")),
            float(navy_stroke.get("y", "0")) + float(navy_stroke.get("height", "0")),
            float(navy_panel.get("y", "0")) + float(navy_panel.get("height", "0")),
        )

        visible_width = right_bound - left_bound
        visible_height = bottom_bound - top_bound
        root.set("width", f"{visible_width:.3f}")
        root.set("height", f"{visible_height:.3f}")
        root.set("viewBox", f"{left_bound:.3f} {top_bound:.3f} {visible_width:.3f} {visible_height:.3f}")

        # Remove text from SVG render path; it is painted manually for reliability.
        text_node.text = ""
        for child in list(text_node):
            text_node.remove(child)

        text_x = float(navy_panel.get("x", "0")) + padding_left
        panel_y = float(navy_panel.get("y", "0"))
        panel_h = float(navy_panel.get("height", "0"))
        text_block_h = line_height * len(lines)
        first_line_y = panel_y + (panel_h - text_block_h) / 2.0 + line_height * 0.8
        line_y_values = [first_line_y + i * line_height for i in range(len(lines))]

        target_width = int(layout["rendered_image_width"])
        target_height = int(layout["rendered_image_height"])

        self._logger.info("[SVG_TEXT] raw input text = %r", raw_text)
        self._logger.info("[SVG_TEXT] lines = %s", lines)
        self._logger.info("[SVG_TEXT] font size = %s", resolved_font_size)
        self._logger.info("[SVG_TEXT] effective font size = %s", effective_font_size)
        self._logger.info("[SVG_TEXT] text x = %s", text_x)
        self._logger.info("[SVG_TEXT] text y values = %s", [round(v, 3) for v in line_y_values])

        svg_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        svg_text = svg_bytes.decode("utf-8", errors="ignore")
        self._logger.info("[SVG_TEXT] generated svg contains dynamic_text = %s", "dynamic_text" in svg_text)
        self._logger.info("[SVG_TEXT] generated svg contains tspan = %s", "tspan" in svg_text)
        self._dump_debug_svg(svg_bytes)

        text_layout = {
            "raw_text": raw_text,
            "lines": lines,
            "font_size": effective_font_size,
            "text_x": text_x,
            "line_y_values": line_y_values,
            "panel_rect": (float(navy_panel.get("x", "0")), float(navy_panel.get("y", "0")), float(navy_panel.get("width", "0")), float(navy_panel.get("height", "0"))),
            "padding_left": padding_left,
            "view_box": (left_bound, top_bound, visible_width, visible_height),
        }
        layout_debug = {
            "final_frame_width": visible_width,
            "final_frame_height": visible_height,
            "rendered_image_width": target_width,
            "rendered_image_height": target_height,
            "font_size": resolved_font_size,
            "padding": (padding_left, padding_right, padding_top, padding_bottom),
            "text_width": max_line_width,
            "text_height": line_height * len(lines),
            "scale": 1.0,
        }
        return svg_bytes, target_width, target_height, text_layout, layout_debug

    @staticmethod
    def _compute_layout(
        *,
        original_panel_width: float,
        original_panel_height: float,
        max_line_width: float,
        line_height: float,
        line_count: int,
        padding_left: float,
        padding_right: float,
        padding_top: float,
        padding_bottom: float,
        resolved_font_size: float,
        canvas_width: int,
        min_logical_width: float = 0.0,
        min_logical_height: float = 0.0,
    ) -> dict[str, float]:
        desired_inner_width = max(original_panel_width, max_line_width + padding_left + padding_right, min_logical_width)
        desired_inner_height = max(original_panel_height, (line_height * line_count) + padding_top + padding_bottom, min_logical_height)
        width_delta = desired_inner_width - original_panel_width
        height_delta = desired_inner_height - original_panel_height
        # Render with the computed frame geometry directly so preview/export don't diverge on long text.
        rendered_image_width = max(1.0, round(desired_inner_width))
        rendered_image_height = max(1.0, round(desired_inner_height))
        return {
            "text_width": max_line_width,
            "text_height": line_height * line_count,
            "final_frame_width": desired_inner_width,
            "final_frame_height": desired_inner_height,
            "font_size": resolved_font_size,
            "padding_left": padding_left,
            "padding_right": padding_right,
            "padding_top": padding_top,
            "padding_bottom": padding_bottom,
            "scale": 1.0,
            "width_delta": width_delta,
            "height_delta": height_delta,
            "rendered_image_width": rendered_image_width,
            "rendered_image_height": rendered_image_height,
        }

    def _paint_text(self, painter: QPainter, layout: dict, image_w: int, image_h: int) -> None:
        lines = layout.get("lines") or [" "]
        raw_text = str(layout.get("raw_text", ""))
        font_size = float(layout.get("font_size", 24.0))
        left, top, vb_w, vb_h = layout.get("view_box", (0.0, 0.0, 1.0, 1.0))
        panel_x, panel_y, panel_w, panel_h = layout.get("panel_rect", (0.0, 0.0, vb_w, vb_h))
        sx = image_w / max(1.0, vb_w)
        sy = image_h / max(1.0, vb_h)

        font_px = max(1, int(round(font_size * sy)))
        font = QFont("Montserrat")
        font.setBold(True)
        font.setPixelSize(font_px)
        if not QFontInfo(font).family().lower().startswith("montserrat"):
            font = QFont("Arial")
            font.setBold(True)
            font.setPixelSize(font_px)

        painter.setRenderHint(QPainter.TextAntialiasing, True)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setClipping(False)
        painter.setPen(QColor("#FFFFFF"))
        painter.setFont(font)

        metrics = QFontMetricsF(font)
        line_spacing = metrics.lineSpacing()
        text_block_h = line_spacing * len(lines)
        panel_y_px = (panel_y - left * 0 + 0 - top) * sy
        panel_h_px = panel_h * sy
        baseline_y = panel_y_px + (panel_h_px - text_block_h) / 2.0 + metrics.ascent()
        text_x_px = ((panel_x + float(layout.get("padding_left", 60.0))) - left) * sx

        try:
            for i, line in enumerate(lines):
                painter.drawText(text_x_px, baseline_y + i * line_spacing, line if line else " ")
        except Exception as exc:
            self._logger.exception("[SVG_TEXT] paint primary failed, fallback Arial draw. err=%s", exc)
            fallback = QFont("Arial")
            fallback.setBold(True)
            fallback.setPixelSize(font_px)
            painter.setFont(fallback)
            fallback_text = raw_text if raw_text.strip() else " "
            painter.drawText(text_x_px, baseline_y, fallback_text)



    def _log_color_debug(self, mode: str, image, *, is_tag_svg: bool = False) -> None:
        try:
            fmt = int(image.format())
            premul = "yes" if fmt == int(QImage.Format_ARGB32_Premultiplied) else "no"
            navy = self._sample_color(image, "#123368")
            orange = self._sample_color(image, "#EC4C2C")
            self._logger.info("[SVG_COLOR] mode=%s", mode)
            self._logger.info("[SVG_COLOR] qimage_format=%s", fmt)
            self._logger.info("[SVG_COLOR] premultiplied_alpha=%s", premul)
            self._logger.info("[SVG_COLOR] sample_navy_rgb=%s", navy)
            self._logger.info("[SVG_COLOR] sample_orange_rgb=%s", orange)
            self._logger.info("[SVG_COLOR] output_overlay_format=PNG_RGBA")
            self._logger.info("[SVG_COLOR] ffmpeg_pix_fmt=%s", "overlay-input:rgba")
            self._logger.info("[SVG_COMPARE] image_format=%s", fmt)
            self._logger.info("[SVG_COMPARE] sample_navy_rgb=%s", navy)
            self._logger.info("[SVG_COMPARE] sample_orange_rgb=%s", orange)
            if is_tag_svg:
                self._logger.info("[BLUE_TAG_RENDER] image_format = %s", fmt)
                self._logger.info("[BLUE_TAG_RENDER] sample_navy_rgb = %s", navy)
                self._logger.info("[BLUE_TAG_RENDER] sample_orange_rgb = %s", orange)
        except Exception:
            pass

    @staticmethod
    def _sample_color(image, target_hex: str) -> tuple[int, int, int] | None:
        if QImage is None or QColor is None:
            return None
        target = QColor(target_hex)
        best = None
        best_dist = 10**9
        step_x = max(1, image.width() // 64)
        step_y = max(1, image.height() // 64)
        for y in range(0, image.height(), step_y):
            for x in range(0, image.width(), step_x):
                c = image.pixelColor(x, y)
                if c.alpha() < 16:
                    continue
                d = abs(c.red()-target.red()) + abs(c.green()-target.green()) + abs(c.blue()-target.blue())
                if d < best_dist:
                    best_dist = d
                    best = (c.red(), c.green(), c.blue())
        return best
    @staticmethod
    def _dump_debug_svg(svg_bytes: bytes) -> None:
        try:
            debug_path = app_root() / "devtools/vector_preview/debug_last_svg_highlight.svg"
            debug_path.parent.mkdir(parents=True, exist_ok=True)
            debug_path.write_bytes(svg_bytes)
        except Exception:
            pass

    @staticmethod
    def _find_required(root: ET.Element, element_id: str) -> ET.Element:
        node = root.find(f".//*[@id='{element_id}']")
        if node is None:
            raise ValueError(f"Template missing id='{element_id}'.")
        return node

    @staticmethod
    def _resolve_font_size(text_node: ET.Element, font_size: float, base_height: float) -> float:
        if font_size > 1.0:
            return max(10.0, float(font_size))
        current = text_node.get("font-size")
        if current:
            try:
                return max(10.0, float(current))
            except ValueError:
                pass
        return max(10.0, base_height * 0.30)

    @staticmethod
    def _measure_text_block(lines: list[str], font_size: float) -> tuple[float, float]:
        if QFont is None or QFontMetricsF is None:
            line_height = max(1.0, font_size * 1.2)
            max_width = max(max(1.0, len(line) * font_size * 0.6) for line in lines)
            return max_width, line_height
        font = QFont("Montserrat")
        font.setPixelSize(max(1, int(round(font_size))))
        font.setBold(True)
        metrics = QFontMetricsF(font)
        max_width = max(max(1.0, metrics.horizontalAdvance(line if line else " ")) for line in lines)
        return max_width, max(1.0, metrics.lineSpacing())
