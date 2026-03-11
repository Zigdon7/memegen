"""Pillow-based meme rendering engine."""

import io
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from ..config import settings
from ..models.template import Template
from ..models.text import TextZone


def _load_font(font_name: str, size: int) -> ImageFont.FreeTypeFont:
    """Load a font by name at the given size."""
    font_map = {
        "impact": settings.fonts_dir / "Impact.ttf",
    }
    font_path = font_map.get(font_name.lower())
    if font_path and font_path.exists():
        return ImageFont.truetype(str(font_path), size)
    # Fallback: try system fonts
    for fallback in [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/TTF/LiberationSans-Bold.ttf",
        "/usr/share/fonts/liberation-sans/LiberationSans-Bold.ttf",
    ]:
        if Path(fallback).exists():
            return ImageFont.truetype(fallback, size)
    return ImageFont.load_default()


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Word-wrap text to fit within max_width pixels."""
    if not text:
        return []
    # Start with a rough character estimate
    avg_char_width = font.getlength("A")
    if avg_char_width <= 0:
        avg_char_width = 10
    chars_per_line = max(1, int(max_width / avg_char_width))

    # Try different wrap widths to find the best fit
    for width in range(chars_per_line, 1, -1):
        lines = textwrap.wrap(text, width=width, break_long_words=True, break_on_hyphens=False)
        if not lines:
            return []
        max_line_width = max(font.getlength(line) for line in lines)
        if max_line_width <= max_width:
            return lines

    # Last resort: one word per line
    return text.split()


def _fit_font_size(
    text: str,
    font_name: str,
    zone_width: int,
    zone_height: int,
    max_size: int,
) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    """Find the largest font size that fits the text in the zone."""
    for size in range(max_size, 8, -2):
        font = _load_font(font_name, size)
        lines = _wrap_text(text, font, zone_width - 10)  # 5px padding each side
        if not lines:
            return font, []
        line_height = size * 1.2
        total_height = line_height * len(lines)
        if total_height <= zone_height:
            return font, lines
    # Minimum size
    font = _load_font(font_name, 10)
    lines = _wrap_text(text, font, zone_width - 10)
    return font, lines


def _draw_text_with_stroke(
    draw: ImageDraw.ImageDraw,
    position: tuple[float, float],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: str,
    stroke_color: str,
    stroke_width: int,
    alignment: str = "center",
):
    """Draw text with a stroke/outline effect."""
    x, y = position
    # Draw stroke
    if stroke_width > 0:
        for dx in range(-stroke_width, stroke_width + 1):
            for dy in range(-stroke_width, stroke_width + 1):
                if dx == 0 and dy == 0:
                    continue
                draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
    # Draw main text
    draw.text((x, y), text, font=font, fill=fill)


def render_meme(
    template: Template,
    texts: list[str],
    *,
    width: int = 0,
    height: int = 0,
    font_override: str = "",
    output_format: str = "jpg",
) -> bytes:
    """Render a meme image and return bytes."""
    image_path = template.get_image_path(settings.templates_dir)
    image = Image.open(image_path).convert("RGBA")
    image = ImageOps.exif_transpose(image)

    # Resize if requested
    if width or height:
        orig_w, orig_h = image.size
        if width and height:
            image = image.resize((min(width, settings.max_width), min(height, settings.max_height)))
        elif width:
            ratio = width / orig_w
            image = image.resize((min(width, settings.max_width), int(orig_h * ratio)))
        elif height:
            ratio = height / orig_h
            image = image.resize((int(orig_w * ratio), min(height, settings.max_height)))

    img_w, img_h = image.size
    draw = ImageDraw.Draw(image)

    zones = template.text
    for i, zone in enumerate(zones):
        if i >= len(texts):
            break
        text = texts[i]
        if not text:
            continue

        # Apply style
        text = zone.apply_style(text)

        # Get zone position and size
        ax, ay = zone.get_anchor(img_w, img_h)
        zw, zh = zone.get_size(img_w, img_h)
        if zw <= 0 or zh <= 0:
            continue

        font_name = font_override or zone.font
        font, lines = _fit_font_size(text, font_name, zw, zh, zone.max_font_size)
        if not lines:
            continue

        line_height = font.size * 1.2
        total_text_height = line_height * len(lines)
        # Center text vertically in zone
        start_y = ay + (zh - total_text_height) / 2

        for j, line in enumerate(lines):
            line_width = font.getlength(line)
            # Horizontal alignment
            if zone.alignment == "center":
                lx = ax + (zw - line_width) / 2
            elif zone.alignment == "right":
                lx = ax + zw - line_width - 5
            else:
                lx = ax + 5
            ly = start_y + j * line_height

            _draw_text_with_stroke(
                draw,
                (lx, ly),
                line,
                font,
                fill=zone.color,
                stroke_color=zone.stroke_color,
                stroke_width=zone.stroke_width,
                alignment=zone.alignment,
            )

    # Convert and save
    stream = io.BytesIO()
    fmt_map = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "webp": "WEBP"}
    pil_format = fmt_map.get(output_format.lower(), "JPEG")
    if pil_format == "JPEG":
        image = image.convert("RGB")
    image.save(stream, format=pil_format, quality=95)
    return stream.getvalue()
