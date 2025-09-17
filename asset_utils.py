"""Utilities for loading image assets in multiple formats."""

from __future__ import annotations

import io
import os
import pygame
import cairosvg


def load_image(path: str) -> pygame.Surface:
    """Load an image file, supporting SVG conversion to a pygame Surface."""

    if not os.path.exists(path):
        raise FileNotFoundError(path)

    ext = os.path.splitext(path)[1].lower()
    if ext == ".svg":
        with open(path, "rb") as svg_file:
            svg_bytes = svg_file.read()
        png_bytes = cairosvg.svg2png(bytestring=svg_bytes)
        surface = pygame.image.load(io.BytesIO(png_bytes))
    else:
        surface = pygame.image.load(path)

    if pygame.display.get_init() and pygame.display.get_surface():
        if surface.get_alpha() is not None:
            return surface.convert_alpha()
        return surface.convert()

    return surface.copy()
