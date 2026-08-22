from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter


def open_rgb(path: Path) -> Image.Image:
    with Image.open(path) as image:
        return image.convert("RGB")


def _cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    target_w, target_h = size
    scale = max(target_w / image.width, target_h / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - target_w) // 2
    top = (resized.height - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def _contain(image: Image.Image, max_size: tuple[int, int], scale: float = 1.0) -> Image.Image:
    max_w, max_h = max_size
    factor = min(max_w / image.width, max_h / image.height) * scale
    return image.resize((max(1, round(image.width * factor)), max(1, round(image.height * factor))), Image.Resampling.LANCZOS)


def compose_product_frame(source: Image.Image, canvas_size: tuple[int, int], template: dict, motion_scale: float = 1.0, pan_x: float = 0.0, pan_y: float = 0.0) -> Image.Image:
    width, height = canvas_size
    background = template.get("background", {})
    foreground = template.get("foreground", {})
    bg = _cover(source, (width, height)).filter(ImageFilter.GaussianBlur(float(background.get("blur", 28))))
    bg = ImageEnhance.Brightness(bg).enhance(float(background.get("brightness", .72)))
    bg = ImageEnhance.Contrast(bg).enhance(float(background.get("contrast", .9)))
    canvas = bg.convert("RGBA")
    max_w = int(width * float(foreground.get("max_width_ratio", .90)))
    max_h = int(height * float(foreground.get("max_height_ratio", .58)))
    product = _contain(source, (max_w, max_h), motion_scale).convert("RGBA")
    base_y = int(height * float(foreground.get("center_y_ratio", .45)))
    x = (width - product.width) // 2 + int(pan_x * width)
    y = base_y - product.height // 2 + int(pan_y * height)
    canvas.alpha_composite(product, (x, y))
    return canvas
