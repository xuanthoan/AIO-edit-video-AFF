from __future__ import annotations

import logging
import re
from xml.etree import ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)

from core.overlays.font_units import log_font_unit, normalize_overlay_font_size
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
    REFERENCE_VIDEO_HEIGHT = 1920.0
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
        layer: str = "highlight_panel",
        preview_scale: float = 1.0,
    ):
        if QImage is None:
            raise RuntimeError("PySide6 is required to render SVG highlight assets.")
        try:
            svg_bytes, output_width, output_height, text_layout = self._build_svg_bytes(
                template_path, text, font_size, canvas_width, canvas_height, layer=layer, preview_scale=preview_scale
            )
        except Exception as exc:
            self._log_svg_error_debug(template_path, exc)
            raise
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
        self._logger.info("[SVG_SIZE] layer=%s", layer)
        self._logger.info("[SVG_SIZE] preview_scale=%s", preview_scale)
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

    @staticmethod
    def _resolve_template_source_path(template_path: str):
        source_path = app_root() / template_path
        if source_path.exists():
            return source_path
        aliases = {
            "sticker_beauty_svg_2.svg": "sticker_beauty_02.svg",
            "sticker_beauty_svg_3.svg": "sticker_beauty_03.svg",
        }
        alias_name = aliases.get(source_path.name)
        if alias_name:
            alias_path = source_path.with_name(alias_name)
            if alias_path.exists():
                return alias_path
        return source_path

    def _build_svg_bytes(
        self,
        template_path: str,
        text: str,
        font_size: float,
        canvas_width: int,
        canvas_height: int | None = None,
        *,
        layer: str = "highlight_panel",
        preview_scale: float = 1.0,
    ):
        source_path = self._resolve_template_source_path(template_path)
        self._logger.info("[SVG] loading template path=%s", source_path.resolve())
        self._logger.info("[SVG] exists=%s", source_path.exists())
        if not source_path.exists():
            raise FileNotFoundError(f"SVG template not found: {source_path}")
        raw = source_path.read_text(encoding="utf-8")
        root = ET.fromstring(raw)
        parent_map = self._parent_map(root)
        root_id = root.attrib.get("id", "")
        normalized_root_id = self._normalize_svg_id(root_id)
        is_sticker_beauty_svg_3 = (
            "sticker_beauty_svg_3" in template_path
            or source_path.name in {"sticker_beauty_svg_3.svg", "sticker_beauty_03.svg"}
            or normalized_root_id in {"sticker_beauty_svg_3", "sticker_beauty_03"}
        )

        view_box = root.attrib.get("viewBox", "").strip().replace(",", " ").split()
        if len(view_box) != 4:
            raise ValueError("Template missing valid viewBox.")
        vb_x = float(view_box[0])
        vb_y = float(view_box[1])
        vb_width = float(view_box[2])
        vb_height = float(view_box[3])

        dynamic_text_nodes = self._find_all(root, "dynamic_text")
        text_layer_nodes = self._find_all(root, "text_layer")
        text_node = (dynamic_text_nodes[0] if dynamic_text_nodes else None) or (text_layer_nodes[0] if text_layer_nodes else None)
        raw_text = (text or "").replace("\r\n", "\n").replace("\r", "\n")
        lines = raw_text.split("\n")
        if not lines or all(not line.strip() for line in lines):
            lines = [" "]

        video_height = int(canvas_height or self.REFERENCE_VIDEO_HEIGHT)
        resolved_font_size = self._resolve_font_size(text_node, font_size, vb_height)
        effective_font_size = normalize_overlay_font_size(resolved_font_size, video_height, preview_scale)
        max_line_width, line_height = self._measure_text_block(lines, effective_font_size)

        orange_stroke = self._find_optional(root, "orange_stroke")
        orange_frame = self._find_optional(root, "orange_frame")
        navy_stroke = self._find_optional(root, "navy_stroke")
        navy_panel = self._find_optional(root, "navy_panel")
        sticker_group = self._find_optional(root, "sticker_group")
        text_safe_area = self._find_optional(root, "text_safe_area")

        padding_left = 60.0
        padding_right = 60.0
        padding_top = 40.0
        padding_bottom = 40.0

        svg_bbox = (vb_x, vb_y, vb_x + vb_width, vb_y + vb_height)
        sticker_bbox = self._collect_bounds(sticker_group, svg_bbox, parent_map) if sticker_group is not None else None
        raw_text_safe_bbox = self._element_bbox(text_safe_area) if text_safe_area is not None else None
        text_safe_bbox = self._element_bbox(text_safe_area, parent_map) if text_safe_area is not None else None
        text_layer_bbox = self._element_bbox(text_node, parent_map) if text_node is not None else None

        layout_source = "viewBox"
        if text_safe_bbox is not None:
            layout_source = "text_safe_area"
            panel_x, panel_y, panel_right, panel_bottom = text_safe_bbox
        elif navy_panel is not None:
            layout_source = "navy_panel"
            panel_x, panel_y, panel_right, panel_bottom = self._element_bbox(navy_panel, parent_map) or svg_bbox
        elif text_layer_bbox is not None:
            layout_source = "text_layer"
            panel_x, panel_y, panel_right, panel_bottom = text_layer_bbox
        else:
            panel_x, panel_y, panel_right, panel_bottom = svg_bbox
        panel_w = max(1.0, panel_right - panel_x)
        panel_h = max(1.0, panel_bottom - panel_y)
        if layout_source == "text_layer" and sticker_bbox is not None and panel_h < vb_height * 0.18:
            sticker_left, sticker_top, sticker_right, sticker_bottom = sticker_bbox
            sticker_w = max(1.0, sticker_right - sticker_left)
            sticker_h = max(1.0, sticker_bottom - sticker_top)
            panel_x = sticker_left + sticker_w * 0.08
            panel_y = sticker_top + sticker_h * 0.20
            panel_right = sticker_right - sticker_w * 0.08
            panel_bottom = sticker_bottom - sticker_h * 0.20
            panel_w = max(1.0, panel_right - panel_x)
            panel_h = max(1.0, panel_bottom - panel_y)
            layout_source = "sticker_group_safe_padding"

        self._logger.info("[SVG_BBOX] svg=%s", self._format_bbox(svg_bbox))
        self._logger.info("[SVG_BBOX] sticker_group=%s", self._format_bbox(sticker_bbox))
        self._logger.info("[SVG_BBOX] text_safe_area=%s", self._format_bbox(text_safe_bbox))
        self._logger.info("[SVG_BBOX] text_layer=%s", self._format_bbox(text_layer_bbox))
        self._logger.info("[SVG_BBOX] dynamic_text_layout_source=%s bbox=%s", layout_source, self._format_bbox((panel_x, panel_y, panel_right, panel_bottom)))
        self._logger.info("[SVG_SAFE_AREA] style=%s", root.attrib.get("id", ""))
        self._logger.info("[SVG_SAFE_AREA] template_path=%s", template_path)
        self._logger.info("[SVG_SAFE_AREA] raw_text_safe_area=%s", self._format_bbox(raw_text_safe_bbox))
        self._logger.info("[SVG_SAFE_AREA] transformed_text_safe_area=%s", self._format_bbox(text_safe_bbox))
        self._logger.info("[SVG_SAFE_AREA] text_layer_bounds=%s", self._format_bbox(text_layer_bbox))
        self._logger.info("[SVG_SAFE_AREA] used_text_rect=%s source=%s", self._format_bbox((panel_x, panel_y, panel_right, panel_bottom)), layout_source)
        self._logger.info("[SVG_SAFE_AREA] cache_invalidated=%s", True)

        auto_shrink_applied = False
        if layout_source in {"text_safe_area", "text_layer", "sticker_group_safe_padding"}:
            if layout_source == "sticker_group_safe_padding":
                available_text_width = max(1.0, panel_w)
                available_text_height = max(1.0, panel_h)
            else:
                available_text_width = max(1.0, panel_w - padding_left - padding_right)
                available_text_height = max(1.0, panel_h - padding_top - padding_bottom)
            # The Highlight Font Size control is the source of truth. Template
            # safe areas guide placement and maximum width, but must not make
            # short text tiny just because SVG viewBox units differ per design.
            should_shrink = max_line_width > max(panel_w, available_text_width) * 1.75
            if should_shrink:
                fit_scale = min(available_text_width / max(1.0, max_line_width), available_text_height / max(1.0, line_height * len(lines)))
                fit_scale = max(0.75, fit_scale)
                effective_font_size = max(1.0, effective_font_size * min(1.0, fit_scale))
                auto_shrink_applied = True
                max_line_width, line_height = self._measure_text_block(lines, effective_font_size)
                self._logger.info("[SVG_TEXT] fit_to_%s scale=%s effective_font_size=%s", layout_source, round(fit_scale, 4), effective_font_size)

        original_panel_width = panel_w
        original_panel_height = panel_h
        desired_inner_width = max(original_panel_width, max_line_width + padding_left + padding_right)
        desired_inner_height = max(original_panel_height, (line_height * len(lines)) + padding_top + padding_bottom)
        width_delta = desired_inner_width - original_panel_width
        height_delta = desired_inner_height - original_panel_height

        resizable_nodes = [node for node in (orange_stroke, orange_frame, navy_stroke, navy_panel) if node is not None]
        for node in resizable_nodes:
            node.set("width", f"{max(1.0, float(node.get('width', '0')) + width_delta):.3f}")
            node.set("height", f"{max(1.0, float(node.get('height', '0')) + height_delta):.3f}")

        if orange_stroke is not None and orange_frame is not None and navy_stroke is not None:
            left_bound = min(float(orange_stroke.get("x", "0")), float(orange_frame.get("x", "0")), float(navy_stroke.get("x", "0")), panel_x)
            right_bound = max(
                float(orange_stroke.get("x", "0")) + float(orange_stroke.get("width", "0")),
                float(orange_frame.get("x", "0")) + float(orange_frame.get("width", "0")),
                float(navy_stroke.get("x", "0")) + float(navy_stroke.get("width", "0")),
                panel_x + max(panel_w, desired_inner_width),
            )
            top_bound = min(float(orange_stroke.get("y", "0")), float(orange_frame.get("y", "0")), float(navy_stroke.get("y", "0")), panel_y)
            bottom_bound = max(
                float(orange_stroke.get("y", "0")) + float(orange_stroke.get("height", "0")),
                float(orange_frame.get("y", "0")) + float(orange_frame.get("height", "0")),
                float(navy_stroke.get("y", "0")) + float(navy_stroke.get("height", "0")),
                panel_y + max(panel_h, desired_inner_height),
            )
        elif sticker_bbox is not None:
            left_bound, top_bound, right_bound, bottom_bound = sticker_bbox
        else:
            left_bound, top_bound, right_bound, bottom_bound = svg_bbox

        if is_sticker_beauty_svg_3 and sticker_bbox is not None and not (orange_stroke is not None and orange_frame is not None and navy_stroke is not None):
            left_bound, top_bound, right_bound, bottom_bound = sticker_bbox

        visible_width = right_bound - left_bound
        visible_height = bottom_bound - top_bound
        root.set("width", f"{visible_width:.3f}")
        root.set("height", f"{visible_height:.3f}")
        root.set("viewBox", f"{left_bound:.3f} {top_bound:.3f} {visible_width:.3f} {visible_height:.3f}")

        # Remove reference-only text/layout nodes from the SVG render path; dynamic text is painted manually.
        removed_dynamic_text_count = self._remove_elements(root, dynamic_text_nodes)
        removed_text_layer_count = self._remove_elements(root, text_layer_nodes)
        if text_safe_area is not None:
            self._remove_element(root, text_safe_area)

        self._logger.info("[SVG_TEXT_CLEAN] style = %s", root.attrib.get("id", ""))
        self._logger.info("[SVG_TEXT_CLEAN] template_path = %s", template_path)
        self._logger.info("[SVG_TEXT_CLEAN] removed_dynamic_text_count = %s", removed_dynamic_text_count)
        self._logger.info("[SVG_TEXT_CLEAN] removed_text_layer_count = %s", removed_text_layer_count)
        self._logger.info("[SVG_TEXT_CLEAN] painter_text = %r", raw_text)
        self._logger.info("[SVG_TEXT_CLEAN] cache_invalidated = %s", True)

        text_align = "center" if layout_source in {"text_safe_area", "text_layer", "sticker_group_safe_padding"} else "left"
        text_x = panel_x + (panel_w / 2.0 if text_align == "center" else padding_left)
        text_block_h = line_height * len(lines)
        first_line_y = panel_y + (panel_h - text_block_h) / 2.0 + line_height * 0.8
        line_y_values = [first_line_y + i * line_height for i in range(len(lines))]

        min_target_width = canvas_width * 1.00
        preferred_target_width = canvas_width * 1.25
        max_target_width = canvas_width * 1.375
        target_width = max(1, int(round(max(min_target_width, min(preferred_target_width, max_target_width)))))
        target_height = max(1, int(round(target_width * (visible_height / max(1.0, visible_width)))))

        if is_sticker_beauty_svg_3:
            self._logger.info("[SVG3_RENDER_BOUNDS] svg_viewBox = %s", self._format_bbox(svg_bbox))
            self._logger.info("[SVG3_RENDER_BOUNDS] sticker_group_bounds = %s", self._format_bbox(sticker_bbox))
            self._logger.info("[SVG3_RENDER_BOUNDS] final_crop_bounds = %s", self._format_bbox((left_bound, top_bound, right_bound, bottom_bound)))
            self._logger.info("[SVG3_RENDER_BOUNDS] output_image_size = %sx%s", target_width, target_height)
            self._logger.info("[SVG3_TEXT] requested_font_size = %s", resolved_font_size)
            self._logger.info("[SVG3_TEXT] effective_font_size = %s", effective_font_size)
            self._logger.info("[SVG3_TEXT] auto_shrink_applied = %s", auto_shrink_applied)
            self._logger.info("[SVG3_TEXT] text_safe_area_raw = %s", self._format_bbox(raw_text_safe_bbox))
            self._logger.info("[SVG3_TEXT] text_safe_area_transformed = %s", self._format_bbox(text_safe_bbox))
            self._logger.info("[SVG3_TEXT] used_text_rect = %s", self._format_bbox((panel_x, panel_y, panel_right, panel_bottom)))
            self._logger.info("[SVG3_TEXT] text_draw_pos = x=%s, y_values=%s", round(text_x, 3), [round(v, 3) for v in line_y_values])

        self._logger.info("[FONT_NORMALIZE] style = %s", root_id)
        self._logger.info("[FONT_NORMALIZE] ui_font_size = %s", resolved_font_size)
        self._logger.info("[FONT_NORMALIZE] video_height = %s", video_height)
        self._logger.info("[FONT_NORMALIZE] effective_font_size = %s", effective_font_size)
        self._logger.info("[FONT_NORMALIZE] text_safe_area = %s", self._format_bbox((panel_x, panel_y, panel_right, panel_bottom)))
        self._logger.info("[FONT_NORMALIZE] auto_shrink_applied = %s", auto_shrink_applied)
        self._logger.info("[FONT_NORMALIZE] final_text_pixel_height = %s", effective_font_size)
        log_font_unit(
            self._logger,
            layer=layer,
            ui_font_size=resolved_font_size,
            video_height=video_height,
            preview_scale=preview_scale,
            effective_font_size=effective_font_size,
            style=root_id,
        )

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
            "font_pixel_size": effective_font_size,
            "text_x": text_x,
            "line_y_values": line_y_values,
            "panel_rect": (panel_x, panel_y, panel_w, panel_h),
            "padding_left": padding_left,
            "text_align": text_align,
            "layout_source": layout_source,
            "view_box": (left_bound, top_bound, visible_width, visible_height),
        }
        return svg_bytes, target_width, target_height, text_layout

    def _paint_text(self, painter: QPainter, layout: dict, image_w: int, image_h: int) -> None:
        lines = layout.get("lines") or [" "]
        raw_text = str(layout.get("raw_text", ""))
        font_size = float(layout.get("font_size", 24.0))
        font_pixel_size = float(layout.get("font_pixel_size", font_size))
        left, top, vb_w, vb_h = layout.get("view_box", (0.0, 0.0, 1.0, 1.0))
        panel_x, panel_y, panel_w, panel_h = layout.get("panel_rect", (0.0, 0.0, vb_w, vb_h))
        sx = image_w / max(1.0, vb_w)
        sy = image_h / max(1.0, vb_h)

        font_px = max(1, int(round(font_pixel_size)))
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
        text_align = str(layout.get("text_align", "left"))
        if text_align == "center":
            text_anchor_px = (panel_x + panel_w / 2.0 - left) * sx
        else:
            text_anchor_px = ((panel_x + float(layout.get("padding_left", 60.0))) - left) * sx

        try:
            for i, line in enumerate(lines):
                draw_text = line if line else " "
                text_x_px = text_anchor_px - metrics.horizontalAdvance(draw_text) / 2.0 if text_align == "center" else text_anchor_px
                painter.drawText(text_x_px, baseline_y + i * line_spacing, draw_text)
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

    def _log_svg_error_debug(self, template_path: str, exc: Exception) -> None:
        import traceback

        source_path = self._resolve_template_source_path(template_path)
        root = None
        raw = ""
        if source_path.exists():
            try:
                raw = source_path.read_text(encoding="utf-8")
                root = ET.fromstring(raw)
            except Exception:
                root = None
        sticker_group = self._find_optional(root, "sticker_group") if root is not None else None
        text_safe_area = self._find_optional(root, "text_safe_area") if root is not None else None
        text_layer = self._find_optional(root, "text_layer") if root is not None else None
        self._logger.exception("[SVG_ERROR_DEBUG] exception while rendering SVG highlight")
        self._logger.error("[SVG_ERROR_DEBUG] style = %s", root.attrib.get("id", "") if root is not None else "")
        self._logger.error("[SVG_ERROR_DEBUG] template_path = %s", template_path)
        self._logger.error("[SVG_ERROR_DEBUG] resolved_path = %s", source_path)
        self._logger.error("[SVG_ERROR_DEBUG] file_exists = %s", source_path.exists())
        self._logger.error("[SVG_ERROR_DEBUG] root_id = %s", root.attrib.get("id", "") if root is not None else "")
        self._logger.error("[SVG_ERROR_DEBUG] viewBox = %s", root.attrib.get("viewBox", "") if root is not None else "")
        self._logger.error("[SVG_ERROR_DEBUG] width = %s", root.attrib.get("width", "") if root is not None else "")
        self._logger.error("[SVG_ERROR_DEBUG] height = %s", root.attrib.get("height", "") if root is not None else "")
        self._logger.error("[SVG_ERROR_DEBUG] sticker_group_found = %s", sticker_group is not None)
        self._logger.error("[SVG_ERROR_DEBUG] text_safe_area_found = %s", text_safe_area is not None)
        self._logger.error("[SVG_ERROR_DEBUG] text_safe_area_tag = %s", self._local_tag(text_safe_area) if text_safe_area is not None else "")
        self._logger.error("[SVG_ERROR_DEBUG] text_layer_found = %s", text_layer is not None)
        self._logger.error("[SVG_ERROR_DEBUG] text_layer_tag = %s", self._local_tag(text_layer) if text_layer is not None else "")
        self._logger.error("[SVG_ERROR_DEBUG] exception_type = %s", type(exc).__name__)
        self._logger.error("[SVG_ERROR_DEBUG] exception_message = %s", exc)
        self._logger.error("[SVG_ERROR_DEBUG] traceback = %s", traceback.format_exc())

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
    def _local_tag(node: ET.Element) -> str:
        return node.tag.rsplit("}", 1)[-1] if "}" in node.tag else node.tag

    @staticmethod
    def _parent_map(root: ET.Element) -> dict[ET.Element, ET.Element]:
        return {child: parent for parent in root.iter() for child in list(parent)}

    @classmethod
    def _element_bbox(
        cls,
        node: ET.Element | None,
        parent_map: dict[ET.Element, ET.Element] | None = None,
    ) -> tuple[float, float, float, float] | None:
        if node is None:
            return None
        tag = cls._local_tag(node)
        if tag == "g":
            group_bbox = cls._collect_bounds(node, (0.0, 0.0, 0.0, 0.0), parent_map)
            if group_bbox != (0.0, 0.0, 0.0, 0.0):
                return group_bbox
            return None
        rect = cls._rect_tuple_from_element(node)
        if rect is not None:
            return cls._apply_transform_to_bbox(rect, cls._node_transform_matrix(node, parent_map, include_self=True))
        circle = cls._circle_bbox(node)
        if circle is not None:
            return cls._apply_transform_to_bbox(circle, cls._node_transform_matrix(node, parent_map, include_self=True))
        path = cls._path_bbox(node)
        if path is not None:
            return cls._apply_transform_to_bbox(path, cls._node_transform_matrix(node, parent_map, include_self=True))
        points = cls._points_bbox(node)
        if points is not None:
            return cls._apply_transform_to_bbox(points, cls._node_transform_matrix(node, parent_map, include_self=True))
        text = cls._text_bbox(node)
        if text is not None:
            return cls._apply_transform_to_bbox(text, cls._node_transform_matrix(node, parent_map, include_self=False))
        return None

    @classmethod
    def _node_transform_matrix(
        cls,
        node: ET.Element,
        parent_map: dict[ET.Element, ET.Element] | None,
        *,
        include_self: bool,
    ) -> tuple[float, float, float, float, float, float]:
        matrix = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
        if parent_map is None:
            return cls._multiply_matrices(matrix, cls._parse_transform(node.get("transform", ""))) if include_self else matrix
        chain = []
        current: ET.Element | None = node if include_self else parent_map.get(node)
        while current is not None:
            chain.append(current)
            current = parent_map.get(current)
        for item in reversed(chain):
            matrix = cls._multiply_matrices(matrix, cls._parse_transform(item.get("transform", "")))
        return matrix

    @staticmethod
    def _multiply_matrices(
        left: tuple[float, float, float, float, float, float],
        right: tuple[float, float, float, float, float, float],
    ) -> tuple[float, float, float, float, float, float]:
        a1, b1, c1, d1, e1, f1 = left
        a2, b2, c2, d2, e2, f2 = right
        return (
            a1 * a2 + c1 * b2,
            b1 * a2 + d1 * b2,
            a1 * c2 + c1 * d2,
            b1 * c2 + d1 * d2,
            a1 * e2 + c1 * f2 + e1,
            b1 * e2 + d1 * f2 + f1,
        )

    @classmethod
    def _parse_transform(cls, transform: str) -> tuple[float, float, float, float, float, float]:
        matrix = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
        for name, raw_args in re.findall(r"(matrix|translate|scale)\(([^)]*)\)", transform or ""):
            values = [float(value) for value in re.findall(r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?", raw_args)]
            if name == "matrix" and len(values) >= 6:
                next_matrix = tuple(values[:6])  # type: ignore[assignment]
            elif name == "translate" and values:
                next_matrix = (1.0, 0.0, 0.0, 1.0, values[0], values[1] if len(values) > 1 else 0.0)
            elif name == "scale" and values:
                next_matrix = (values[0], 0.0, 0.0, values[1] if len(values) > 1 else values[0], 0.0, 0.0)
            else:
                continue
            matrix = cls._multiply_matrices(matrix, next_matrix)
        return matrix

    @staticmethod
    def _apply_transform_to_bbox(
        bbox: tuple[float, float, float, float],
        matrix: tuple[float, float, float, float, float, float],
    ) -> tuple[float, float, float, float]:
        a, b, c, d, e, f = matrix
        left, top, right, bottom = bbox
        points = (
            (left, top),
            (right, top),
            (right, bottom),
            (left, bottom),
        )
        transformed = [(a * x + c * y + e, b * x + d * y + f) for x, y in points]
        xs = [point[0] for point in transformed]
        ys = [point[1] for point in transformed]
        return min(xs), min(ys), max(xs), max(ys)

    @staticmethod
    def _format_bbox(bbox: tuple[float, float, float, float] | None) -> str:
        if bbox is None:
            return "missing"
        left, top, right, bottom = bbox
        return f"x={left:.3f}, y={top:.3f}, w={right - left:.3f}, h={bottom - top:.3f}, right={right:.3f}, bottom={bottom:.3f}"

    @staticmethod
    def _rect_tuple_from_element(node: ET.Element | None) -> tuple[float, float, float, float] | None:
        if node is None:
            return None
        x = node.get("x")
        y = node.get("y")
        width = node.get("width")
        height = node.get("height")
        if x is None or y is None or width is None or height is None:
            return None
        try:
            left = float(str(x).split()[0])
            top = float(str(y).split()[0])
            right = left + float(str(width).split()[0])
            bottom = top + float(str(height).split()[0])
        except ValueError:
            return None
        return left, top, right, bottom

    @staticmethod
    def _circle_bbox(node: ET.Element | None) -> tuple[float, float, float, float] | None:
        if node is None:
            return None
        try:
            cx = float(node.get("cx", ""))
            cy = float(node.get("cy", ""))
            rx = float(node.get("rx", node.get("r", "")))
            ry = float(node.get("ry", node.get("r", "")))
        except ValueError:
            return None
        return cx - rx, cy - ry, cx + rx, cy + ry

    @staticmethod
    def _points_bbox(node: ET.Element | None) -> tuple[float, float, float, float] | None:
        if node is None:
            return None
        points_attr = node.get("points")
        if not points_attr:
            return None
        try:
            values = [float(value) for value in re.findall(r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?", points_attr)]
        except ValueError:
            return None
        if len(values) < 2:
            return None
        points = list(zip(values[0::2], values[1::2]))
        if not points:
            return None
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        return min(xs), min(ys), max(xs), max(ys)

    @classmethod
    def _path_bbox(cls, node: ET.Element | None) -> tuple[float, float, float, float] | None:
        if node is None:
            return None
        d = node.get("d")
        if not d:
            return None
        tokens = re.findall(r"[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?", d)
        if not tokens:
            return None
        points: list[tuple[float, float]] = []
        x = y = start_x = start_y = 0.0
        command = ""
        i = 0

        def is_command(value: str) -> bool:
            return bool(re.fullmatch(r"[A-Za-z]", value))

        def read_number() -> float | None:
            nonlocal i
            if i >= len(tokens) or is_command(tokens[i]):
                return None
            value = float(tokens[i])
            i += 1
            return value

        try:
            while i < len(tokens):
                if is_command(tokens[i]):
                    command = tokens[i]
                    i += 1
                    if command in "Zz":
                        x, y = start_x, start_y
                        points.append((x, y))
                        continue
                if not command:
                    break
                relative = command.islower()
                upper = command.upper()
                if upper == "M":
                    nx = read_number()
                    ny = read_number()
                    if nx is None or ny is None:
                        break
                    x = x + nx if relative else nx
                    y = y + ny if relative else ny
                    start_x, start_y = x, y
                    points.append((x, y))
                    command = "l" if relative else "L"
                elif upper == "L":
                    nx = read_number()
                    ny = read_number()
                    if nx is None or ny is None:
                        break
                    x = x + nx if relative else nx
                    y = y + ny if relative else ny
                    points.append((x, y))
                elif upper == "H":
                    nx = read_number()
                    if nx is None:
                        break
                    x = x + nx if relative else nx
                    points.append((x, y))
                elif upper == "V":
                    ny = read_number()
                    if ny is None:
                        break
                    y = y + ny if relative else ny
                    points.append((x, y))
                elif upper == "C":
                    values = [read_number() for _ in range(6)]
                    if any(value is None for value in values):
                        break
                    for px, py in ((values[0], values[1]), (values[2], values[3]), (values[4], values[5])):
                        assert px is not None and py is not None
                        points.append((x + px if relative else px, y + py if relative else py))
                    assert values[4] is not None and values[5] is not None
                    x = x + values[4] if relative else values[4]
                    y = y + values[5] if relative else values[5]
                else:
                    # Unsupported path command; consume numeric pairs as conservative absolute/relative points.
                    nx = read_number()
                    ny = read_number()
                    if nx is None or ny is None:
                        break
                    x = x + nx if relative else nx
                    y = y + ny if relative else ny
                    points.append((x, y))
        except (ValueError, TypeError):
            return None
        if not points:
            return None
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        return min(xs), min(ys), max(xs), max(ys)

    @staticmethod
    def _text_bbox(node: ET.Element | None) -> tuple[float, float, float, float] | None:
        if node is None:
            return None
        font_size = node.get("font-size")
        classes = node.get("class", "")
        if font_size is None and "st7" in classes:
            font_size = "44.9617"
        try:
            size = float(font_size) if font_size else 44.0
        except ValueError:
            size = 44.0
        x = node.get("x")
        y = node.get("y")
        transform = node.get("transform", "")
        tx = ty = None
        if x and y:
            try:
                tx = float(x.split()[0])
                ty = float(y.split()[0])
            except ValueError:
                tx = ty = None
        if tx is None or ty is None:
            numbers = [float(value) for value in re.findall(r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?", transform)]
            if transform.startswith("matrix") and len(numbers) >= 6:
                tx, ty = numbers[4], numbers[5]
            elif len(numbers) >= 2:
                tx, ty = numbers[-2], numbers[-1]
        if tx is None or ty is None:
            return None
        text = "".join(node.itertext()) or " "
        width = max(1.0, len(text) * size * 0.6)
        height = max(1.0, size * 1.2)
        return tx, ty - height, tx + width, ty

    @staticmethod
    def _remove_element(root: ET.Element, target: ET.Element) -> bool:
        for parent in root.iter():
            for child in list(parent):
                if child is target:
                    parent.remove(child)
                    return True
        return False

    @classmethod
    def _remove_elements(cls, root: ET.Element, targets: list[ET.Element]) -> int:
        removed = 0
        for target in list(targets):
            if cls._remove_element(root, target):
                removed += 1
        return removed

    @staticmethod
    def _find_required(root: ET.Element, element_id: str) -> ET.Element:
        node = root.find(f".//*[@id='{element_id}']")
        if node is None:
            raise ValueError(f"Template missing id='{element_id}'.")
        return node

    @staticmethod
    def _resolve_font_size(text_node: ET.Element | None, font_size: float, base_height: float) -> float:
        if font_size > 1.0:
            return max(10.0, float(font_size))
        if font_size > 0.0:
            return float(font_size)
        current = text_node.get("font-size") if text_node is not None else None
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


    @classmethod
    def _find_optional(cls, root: ET.Element, element_id: str) -> ET.Element | None:
        nodes = cls._find_all(root, element_id)
        return nodes[0] if nodes else None

    @classmethod
    def _find_all(cls, root: ET.Element, element_id: str) -> list[ET.Element]:
        matches = []
        for node in root.iter():
            node_id = node.get("id")
            if not node_id:
                continue
            normalized = cls._normalize_svg_id(node_id)
            if node_id == element_id or normalized == element_id or normalized.startswith(f"{element_id}_"):
                matches.append(node)
        return matches

    @staticmethod
    def _normalize_svg_id(raw_id: str) -> str:
        return raw_id.replace("_x5F_", "_").replace("x5F_", "_")

    @classmethod
    def _collect_bounds(
        cls,
        group: ET.Element,
        fallback: tuple[float, float, float, float],
        parent_map: dict[ET.Element, ET.Element] | None = None,
    ) -> tuple[float, float, float, float]:
        min_x = float("inf")
        min_y = float("inf")
        max_x = float("-inf")
        max_y = float("-inf")
        for node in group.iter():
            if node is group:
                continue
            bbox = cls._element_bbox(node, parent_map)
            if bbox is None:
                continue
            left, top, right, bottom = bbox
            min_x = min(min_x, left)
            min_y = min(min_y, top)
            max_x = max(max_x, right)
            max_y = max(max_y, bottom)
        if min_x == float("inf"):
            return fallback
        return min_x, min_y, max_x, max_y

    @staticmethod
    def _rect_from_text_node(text_node: ET.Element, vb_width: float, vb_height: float) -> ET.Element:
        x = text_node.get("x")
        y = text_node.get("y")
        tx = float(x.split()[0]) if x else vb_width * 0.10
        ty = float(y.split()[0]) if y else vb_height * 0.55
        width = vb_width * 0.70
        height = vb_height * 0.35
        return ET.Element("rect", {"x": f"{tx:.3f}", "y": f"{max(0.0, ty - height * 0.7):.3f}", "width": f"{width:.3f}", "height": f"{height:.3f}"})

    @staticmethod
    def _rect_from_viewbox(vb_x: float, vb_y: float, vb_width: float, vb_height: float) -> ET.Element:
        return ET.Element("rect", {"x": f"{vb_x:.3f}", "y": f"{vb_y:.3f}", "width": f"{vb_width:.3f}", "height": f"{vb_height:.3f}"})
