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
        svg_bytes, output_width, output_height, text_layout = self._build_svg_bytes(
            template_path, text, font_size, canvas_width
        )
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
        self._log_color_debug(mode, image)
        return image

    def _build_svg_bytes(self, template_path: str, text: str, font_size: float, canvas_width: int):
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

        text_node = self._find_optional(root, "dynamic_text") or self._find_optional(root, "text_layer")
        if text_node is None:
            raise ValueError("Template missing text reference layer (dynamic_text/text_layer).")
        raw_text = (text or "").replace("\r\n", "\n").replace("\r", "\n")
        lines = raw_text.split("\n")
        if not lines or all(not line.strip() for line in lines):
            lines = [" "]

        resolved_font_size = self._resolve_font_size(text_node, font_size, vb_height)
        effective_font_size = resolved_font_size * self.TEXT_SIZE_MULTIPLIER
        max_line_width, line_height = self._measure_text_block(lines, effective_font_size)

        orange_stroke = self._find_optional(root, "orange_stroke")
        orange_frame = self._find_optional(root, "orange_frame")
        navy_stroke = self._find_optional(root, "navy_stroke")
        navy_panel = self._find_optional(root, "navy_panel")

        padding_left = 60.0
        padding_right = 60.0
        padding_top = 40.0
        padding_bottom = 40.0

        if navy_panel is None:
            navy_panel = self._find_required(root, "text_safe_area")

        original_panel_width = float(navy_panel.get("width", "0"))
        original_panel_height = float(navy_panel.get("height", "0"))
        desired_inner_width = max(original_panel_width, max_line_width + padding_left + padding_right)
        desired_inner_height = max(original_panel_height, (line_height * len(lines)) + padding_top + padding_bottom)
        width_delta = desired_inner_width - original_panel_width
        height_delta = desired_inner_height - original_panel_height

        resizable_nodes = [node for node in (orange_stroke, orange_frame, navy_stroke, navy_panel) if node is not None]
        for node in resizable_nodes:
            node.set("width", f"{max(1.0, float(node.get('width', '0')) + width_delta):.3f}")
            node.set("height", f"{max(1.0, float(node.get('height', '0')) + height_delta):.3f}")

        if orange_stroke is not None and orange_frame is not None and navy_stroke is not None:
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
        else:
            sticker_group = self._find_required(root, "sticker_group")
            left_bound, top_bound, right_bound, bottom_bound = self._collect_bounds(sticker_group)

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

        min_target_width = canvas_width * 1.00
        preferred_target_width = canvas_width * 1.25
        max_target_width = canvas_width * 1.375
        target_width = max(1, int(round(max(min_target_width, min(preferred_target_width, max_target_width)))))
        target_height = max(1, int(round(target_width * (visible_height / max(1.0, visible_width)))))

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
        return svg_bytes, target_width, target_height, text_layout

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



    def _log_color_debug(self, mode: str, image) -> None:
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


    @staticmethod
    def _find_optional(root: ET.Element, element_id: str) -> ET.Element | None:
        return root.find(f".//*[@id='{element_id}']")

    @staticmethod
    def _collect_bounds(group: ET.Element) -> tuple[float, float, float, float]:
        min_x = float("inf")
        min_y = float("inf")
        max_x = float("-inf")
        max_y = float("-inf")
        for node in group.iter():
            if node is group:
                continue
            x = node.get("x")
            y = node.get("y")
            w = node.get("width")
            h = node.get("height")
            if x is None or y is None or w is None or h is None:
                continue
            xf, yf, wf, hf = float(x), float(y), float(w), float(h)
            min_x = min(min_x, xf)
            min_y = min(min_y, yf)
            max_x = max(max_x, xf + wf)
            max_y = max(max_y, yf + hf)
        if min_x == float("inf"):
            raise ValueError("sticker_group has no measurable rectangular elements.")
        return min_x, min_y, max_x, max_y
