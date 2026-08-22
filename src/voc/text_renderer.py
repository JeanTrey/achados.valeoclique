from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def _font(font_path: str | None, size: int):
    if font_path and Path(font_path).is_file():
        return ImageFont.truetype(font_path, size)
    for candidate in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"):
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return []
    lines, current = [], words[0]
    for word in words[1:]:
        trial = current + " " + word
        if draw.textbbox((0, 0), trial, font=font)[2] <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def fit_text(text: str, max_width: int, max_height: int, preferred_size: int, min_size: int, font_path: str | None = None):
    scratch = Image.new("RGBA", (max_width, max_height))
    draw = ImageDraw.Draw(scratch)
    for size in range(preferred_size, min_size - 1, -2):
        font = _font(font_path, size)
        lines = _wrap(draw, text, font, max_width)
        spacing = max(4, int(size * .16))
        boxes = [draw.textbbox((0, 0), line, font=font) for line in lines]
        height = sum(b[3] - b[1] for b in boxes) + spacing * max(0, len(lines) - 1)
        if height <= max_height:
            return font, lines, spacing
    font = _font(font_path, min_size)
    return font, _wrap(draw, text, font, max_width), max(4, int(min_size * .16))


def draw_text_block(canvas: Image.Image, text: str | None, box: tuple[int, int, int, int], style: dict, alpha: int = 255, font_root: Path | None = None) -> None:
    if not text:
        return
    x0, y0, x1, y1 = box
    font_name = style.get("font")
    font_path = str(font_root / font_name) if font_name and font_root else None
    font, lines, spacing = fit_text(text, x1 - x0, y1 - y0, int(style.get("size", 56)), int(style.get("min_size", 28)), font_path)
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    fill = tuple(style.get("color", [255, 255, 255])) + (alpha,)
    stroke_fill = tuple(style.get("stroke_color", [0, 0, 0])) + (alpha,)
    stroke = int(style.get("stroke_width", 3))
    heights = [draw.textbbox((0, 0), line, font=font, stroke_width=stroke)[3] for line in lines]
    total_h = sum(heights) + spacing * max(0, len(lines) - 1)
    y = y0 + max(0, ((y1 - y0) - total_h) // 2)
    for line, height in zip(lines, heights):
        box_line = draw.textbbox((0, 0), line, font=font, stroke_width=stroke)
        width = box_line[2] - box_line[0]
        x = x0 + ((x1 - x0) - width) // 2
        draw.text((x, y), line, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
        y += height + spacing
    canvas.alpha_composite(overlay)
