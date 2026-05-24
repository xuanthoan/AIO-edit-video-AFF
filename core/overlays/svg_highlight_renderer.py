from __future__ import annotations

import logging
from pathlib import Path
from xml.etree import ElementTree as ET

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
        logging.getLogger(__name__).info("[SVG] loading template path=%s", source_path.resolve())
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
        text_node = root.find(".//*[@id='dynamic_text']")
        if text_node is None:
            raise ValueError("Template missing id='dynamic_text'.")
        text_value = (text or "").strip() or " "
        resolved_font_size = self._resolve_font_size(text_node, font_size, base_height)
        measured_text_width = self._measure_text_width(text_node, text_value, resolved_font_size)

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
        inner_left = float(navy_panel.get("x", "0"))
        inner_right = float(navy_panel.get("x", "0")) + float(navy_panel.get("width", "0"))
        padding_left = 60.0
        padding_right = 60.0
        desired_inner_width = max(float(navy_panel.get("width", "0")), measured_text_width + padding_left + padding_right)
        width_delta = desired_inner_width - float(navy_panel.get("width", "0"))

        for node in (orange_stroke, orange_frame, navy_stroke, navy_panel):
            node.set("width", f"{max(1.0, float(node.get('width', '0')) + width_delta):.3f}")
        visible_width = (right_bound - left_bound) + width_delta
        visible_height = bottom_bound - top_bound
        # Keep original vertical composition and avoid giant/tall frame.
        new_total_height = visible_height
        root.set("width", f"{visible_width:.3f}")
        root.set("height", f"{new_total_height:.3f}")
        root.set("viewBox", f"{left_bound:.3f} {top_bound:.3f} {visible_width:.3f} {new_total_height:.3f}")

        text_center_x = float(navy_panel.get("x", "0")) + padding_left
        text_center_y = float(navy_panel.get("y", "0")) + float(navy_panel.get("height", "0")) / 2.0
        text_node.text = text_value
        text_node.set("x", f"{text_center_x:.3f}")
        text_node.set("y", f"{text_center_y:.3f}")
        text_node.set("text-anchor", "start")
        text_node.set("dominant-baseline", "middle")
        text_node.set("font-size", f"{resolved_font_size:.3f}")

        target_width = max(int(canvas_width * 0.38), int(visible_width))
        target_height = max(1, int(round(target_width * (new_total_height / max(1.0, visible_width)))))
        return ET.tostring(root, encoding="utf-8", xml_declaration=True), target_width, target_height

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
    def _measure_text_width(text_node: ET.Element, text: str, font_size: float) -> float:
        if QFont is None or QFontMetricsF is None:
            return max(1.0, len(text) * font_size * 0.6)
        families = [part.strip() for part in str(text_node.get("font-family", "Montserrat")).split(",") if part.strip()]
        font = QFont(families[0] if families else "Montserrat")
        font.setPixelSize(max(1, int(round(font_size))))
        font.setBold(True)
        metrics = QFontMetricsF(font)
        return max(1.0, metrics.horizontalAdvance(text))
