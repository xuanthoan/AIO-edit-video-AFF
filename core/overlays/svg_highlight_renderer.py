from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET

from utils.ffmpeg_helper import app_root

try:
    from PySide6.QtCore import QByteArray, Qt
    from PySide6.QtGui import QImage, QPainter
    from PySide6.QtSvg import QSvgRenderer
except ImportError:  # allows non-GUI CI imports when PySide6 is absent
    QByteArray = Qt = QImage = QPainter = QSvgRenderer = None


class SVGHighlightRenderer:
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
        svg_bytes, aspect_ratio = self._build_svg_bytes(template_path, text, font_size)
        renderer = QSvgRenderer(QByteArray(svg_bytes))
        if not renderer.isValid():
            raise ValueError(f"Invalid SVG renderer for template: {template_path}")
        target_width = max(1, int(canvas_width * 0.35))
        target_height = max(1, int(round(target_width / max(aspect_ratio, 0.01))))
        image = QImage(target_width, target_height, QImage.Format_ARGB32_Premultiplied)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        renderer.render(painter)
        painter.end()
        return image

    def _build_svg_bytes(self, template_path: str, text: str, font_size: float) -> tuple[bytes, float]:
        source_path = app_root() / template_path
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
        aspect_ratio = vb_width / vb_height
        text_node = root.find(".//*[@id='dynamic_text']")
        if text_node is None:
            raise ValueError("Template missing id='dynamic_text'.")
        text_node.text = text
        return ET.tostring(root, encoding="utf-8", xml_declaration=True), aspect_ratio
