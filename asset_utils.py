"""Utilities for loading image assets in multiple formats."""

from __future__ import annotations

import io
import os
import pygame
try:
    import cairosvg  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    cairosvg = None


def _fallback_svg_surface(path: str) -> pygame.Surface:
    """Return a simple placeholder surface when ``cairosvg`` is unavailable."""

    with open(path, "rb") as svg_file:
        svg_bytes = svg_file.read()

    width = height = 64
    try:
        import xml.etree.ElementTree as ET

        root = ET.fromstring(svg_bytes)
        width_attr = root.get("width")
        height_attr = root.get("height")
        view_box = root.get("viewBox")

        def _parse_length(value: str | None) -> float | None:
            if not value:
                return None
            value = value.strip()
            for suffix in ("px", "pt", "cm", "mm", "in"):
                if value.endswith(suffix):
                    value = value[: -len(suffix)]
                    break
            try:
                return float(value)
            except ValueError:
                return None

        width_val = _parse_length(width_attr)
        height_val = _parse_length(height_attr)

        if width_val and height_val:
            width, height = int(max(1, round(width_val))), int(max(1, round(height_val)))
        elif view_box:
            parts = [p for p in view_box.replace(",", " ").split(" ") if p]
            if len(parts) == 4:
                try:
                    width = int(max(1, round(float(parts[2]))))
                    height = int(max(1, round(float(parts[3]))))
                except ValueError:
                    pass
    except Exception:
        # If any parsing fails we keep the default placeholder size.
        width = max(1, int(width))
        height = max(1, int(height))

    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    surface.fill((120, 120, 120, 255))
    pygame.draw.rect(surface, (200, 200, 200, 255), surface.get_rect(), 2)
    return surface


def load_image(path: str) -> pygame.Surface:
    """Load an image file, supporting SVG conversion to a pygame Surface."""

    if not os.path.exists(path):
        raise FileNotFoundError(path)

    ext = os.path.splitext(path)[1].lower()
    if ext == ".svg":
        if cairosvg is None:
            surface = _fallback_svg_surface(path)
        else:
            try:
                with open(path, "rb") as svg_file:
                    svg_bytes = svg_file.read()
                png_bytes = cairosvg.svg2png(bytestring=svg_bytes)
                surface = pygame.image.load(io.BytesIO(png_bytes))
            except Exception:
                surface = _fallback_svg_surface(path)
    else:
        surface = pygame.image.load(path)

    if pygame.display.get_init() and pygame.display.get_surface():
        if surface.get_alpha() is not None:
            return surface.convert_alpha()
        return surface.convert()

    return surface.copy()
