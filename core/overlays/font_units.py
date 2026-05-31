"""Shared overlay font-size unit conversion for text and highlight layers."""
from __future__ import annotations

import logging

from core.normalized_layout import NormalizedLayoutEngine


DEFAULT_PREVIEW_SCALE = 1.0


def normalize_overlay_font_size(ui_font_size: float, video_height: int, preview_scale: float = DEFAULT_PREVIEW_SCALE) -> int:
    """Map a UI font-size value or persisted ratio to video/preview pixels.

    Text Panel and Highlight Panel keep independent values, but both interpret
    those values through this same normalized unit. Values <= 1 are treated as
    persisted ratios; values > 1 are legacy/reference-height UI pixels.
    """
    layout = NormalizedLayoutEngine()
    ratio = layout.normalize_font_size(float(ui_font_size))
    scaled_height = max(1.0, float(video_height) * max(float(preview_scale), 0.001))
    return max(1, round(ratio * scaled_height))


def log_font_unit(
    logger: logging.Logger,
    *,
    layer: str,
    ui_font_size: float,
    video_height: int,
    preview_scale: float,
    effective_font_size: float,
    style: str | None = None,
) -> None:
    logger.info("[FONT_UNIT] layer=%s", layer)
    logger.info("[FONT_UNIT] ui_font_size=%s", ui_font_size)
    logger.info("[FONT_UNIT] video_height=%s", video_height)
    logger.info("[FONT_UNIT] preview_scale=%s", preview_scale)
    logger.info("[FONT_UNIT] effective_font_size=%s", effective_font_size)
    logger.info("[FONT_UNIT_COMPARE] layer=%s", layer)
    if layer == "highlight_panel" and style is not None:
        logger.info("[FONT_UNIT_COMPARE] style=%s", style)
    logger.info("[FONT_UNIT_COMPARE] ui_font_size=%s", ui_font_size)
    logger.info("[FONT_UNIT_COMPARE] video_height=%s", video_height)
    logger.info("[FONT_UNIT_COMPARE] effective_font_px=%s", effective_font_size)
