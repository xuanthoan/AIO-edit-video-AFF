from __future__ import annotations

import logging
from pathlib import Path
from xml.etree import ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
XML_NS = "http://www.w3.org/XML/1998/namespace"
ET.register_namespace("", SVG_NS)

from utils.ffmpeg_helper import app_root

try:
    from PySide6.QtCore import QByteArray, Qt
    from PySide6.QtGui import QFont, QFontMetricsF, QImage, QPainter
    from PySide6.QtSvg import QSvgRenderer
except ImportError:  # allows non-GUI CI imports when PySide6 is absent
    QByteArray = Qt = QFont = QFontMetricsF = QImage = QPainter = QSvgRenderer = None


class SVGHighlightRenderer:
    BASE_WIDTH = 1073.0
    BASE_HEIGHT = 646.0
    _logger = logging.getLogger(__name__)
    def render_image(
        self,
        template_path: str,
        text: str,
        font_size: float,
        canvas_width: int,
        canvas_height: int,
    ):
        if QImage is None:
            raise RuntimeError("PySide6 is required to render SVG highlight assets.")
        svg_bytes, output_width, output_height = self._build_svg_bytes(template_path, text, font_size, canvas_width)
        renderer = QSvgRenderer(QByteArray(svg_bytes))
        if not renderer.isValid():
            raise ValueError(f"Invalid SVG renderer for template: {template_path}")
        image = QImage(max(1, int(output_width)), max(1, int(output_height)), QImage.Format_ARGB32_Premultiplied)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        renderer.render(painter)
        painter.end()
        return image

    def _build_svg_bytes(self, template_path: str, text: str, font_size: float, canvas_width: int) -> tuple[bytes, int, int]:
        source_path = app_root() / template_path
        self._logger.info("[SVG] loading template path=%s", source_path.resolve())
        if not source_path.exists():
            raise FileNotFoundError(f"SVG template not found: {source_path}")
        raw = source_path.read_text(encoding="utf-8")
        root = ET.fromstring(raw)
        if not root.tag.lower().endswith("svg"):
            raise ValueError("Template root is not <svg>.")
        view_box = root.attrib.get("viewBox", "").strip().replace(",", " ").split()
        if len(view_box) != 4:
            raise ValueError("Template missing valid viewBox.")
        vb_width = float(view_box[2])
        vb_height = float(view_box[3])
        if vb_width <= 0 or vb_height <= 0:
            raise ValueError("Template viewBox dimensions must be > 0.")
        base_width = vb_width
        base_height = vb_height
        text_node = self._find_required(root, "dynamic_text")
        if text_node is None:
            raise ValueError("Template missing id='dynamic_text'.")
        raw_text = (text or "").replace("\r\n", "\n").replace("\r", "\n")
        self._logger.info("[SVG_TEXT] raw input text = %r", raw_text)
        lines = [line for line in raw_text.split("\n")]
        if not lines:
            lines = [" "]
        if all(not line.strip() for line in lines):
            lines = [" "]
        self._logger.info("[SVG_TEXT] lines = %s", lines)
        resolved_font_size = self._resolve_font_size(text_node, font_size, base_height)
        self._logger.info("[SVG_TEXT] font size = %s", resolved_font_size)
        max_line_width, line_height = self._measure_text_block(text_node, lines, resolved_font_size)

        orange_stroke = self._find_required(root, "orange_stroke")
        orange_frame = self._find_required(root, "orange_frame")
        navy_stroke = self._find_required(root, "navy_stroke")
        navy_panel = self._find_required(root, "navy_panel")

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
        padding_left = 60.0
        padding_right = 60.0
        padding_top = 36.0
        padding_bottom = 36.0
        desired_inner_width = max(float(navy_panel.get("width", "0")), max_line_width + padding_left + padding_right)
        desired_inner_height = max(float(navy_panel.get("height", "0")), (line_height * len(lines)) + padding_top + padding_bottom)
        width_delta = desired_inner_width - float(navy_panel.get("width", "0"))
        height_delta = desired_inner_height - float(navy_panel.get("height", "0"))

        for node in (orange_stroke, orange_frame, navy_stroke, navy_panel):
            node.set("width", f"{max(1.0, float(node.get('width', '0')) + width_delta):.3f}")
            node.set("height", f"{max(1.0, float(node.get('height', '0')) + height_delta):.3f}")
        visible_width = (right_bound - left_bound) + width_delta
        visible_height = (bottom_bound - top_bound) + height_delta
        # Keep original vertical composition and avoid giant/tall frame.
        new_total_height = visible_height
        root.set("width", f"{visible_width:.3f}")
        root.set("height", f"{new_total_height:.3f}")
        root.set("viewBox", f"{left_bound:.3f} {top_bound:.3f} {visible_width:.3f} {new_total_height:.3f}")

        text_center_x = float(navy_panel.get("x", "0")) + padding_left
        panel_y = float(navy_panel.get("y", "0"))
        panel_h = float(navy_panel.get("height", "0"))
        text_block_height = line_height * len(lines)
        first_line_y = panel_y + (panel_h - text_block_height) / 2.0 + line_height * 0.8
        line_y_values = [first_line_y + i * line_height for i in range(len(lines))]
        self._logger.info("[SVG_TEXT] text x = %s", text_center_x)
        self._logger.info("[SVG_TEXT] text y values = %s", [round(v, 3) for v in line_y_values])

        text_node.clear()
        text_node.set("x", f"{text_center_x:.3f}")
        text_node.set("y", f"{first_line_y:.3f}")
        text_node.set("text-anchor", "start")
        text_node.set("dominant-baseline", "alphabetic")
        text_node.set("font-size", f"{resolved_font_size:.3f}")
        text_node.set("font-family", "Montserrat, Arial, sans-serif")
        text_node.set("font-weight", "700")
        text_node.set(f"{{{XML_NS}}}space", "preserve")
        try:
            for i, line in enumerate(lines):
                span = ET.SubElement(text_node, f"{{{SVG_NS}}}tspan")
                span.set("x", f"{text_center_x:.3f}")
                span.set("y", f"{line_y_values[i]:.3f}")
                span.text = line if line else " "
        except Exception:
            fallback_text = " ".join(part for part in lines if part) or " "
            text_node.text = fallback_text

        parent = self._find_parent(root, text_node)
        if parent is not None:
            parent.remove(text_node)
            parent.append(text_node)

        target_width = max(220, int(round(min(canvas_width * 0.45, canvas_width * 0.35))))
        target_width = max(target_width, int(round(visible_width)))
        target_height = max(1, int(round(target_width * (new_total_height / max(1.0, visible_width)))))
        svg_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        svg_text = svg_bytes.decode("utf-8", errors="ignore")
        self._logger.info("[SVG_TEXT] generated svg contains dynamic_text = %s", "dynamic_text" in svg_text)
        self._logger.info("[SVG_TEXT] generated svg contains tspan = %s", "tspan" in svg_text)
        self._dump_debug_svg(svg_bytes)
        test_renderer = QSvgRenderer(QByteArray(svg_bytes)) if QSvgRenderer is not None and QByteArray is not None else None
        self._logger.info("[SVG_TEXT] renderer valid = %s", bool(test_renderer and test_renderer.isValid()))
        return svg_bytes, target_width, target_height


    @staticmethod
    def _find_parent(root: ET.Element, target: ET.Element) -> ET.Element | None:
        for parent in root.iter():
            for child in list(parent):
                if child is target:
                    return parent
        return None

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
    def _measure_text_block(text_node: ET.Element, lines: list[str], font_size: float) -> tuple[float, float]:
        if QFont is None or QFontMetricsF is None:
            line_height = max(1.0, font_size * 1.2)
            max_width = max(max(1.0, len(line) * font_size * 0.6) for line in lines)
            return max_width, line_height
        families = [part.strip() for part in str(text_node.get("font-family", "Montserrat")).split(",") if part.strip()]
        font = QFont(families[0] if families else "Montserrat")
        font.setPixelSize(max(1, int(round(font_size))))
        font.setBold(True)
        metrics = QFontMetricsF(font)
        max_width = max(max(1.0, metrics.horizontalAdvance(line if line else " ")) for line in lines)
        return max_width, max(1.0, metrics.lineSpacing())
