from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from PIL import Image


@dataclass(frozen=True)
class ArtDirection:
    accent: tuple[int, int, int]
    text: tuple[int, int, int]
    panel: tuple[int, int, int]
    panel_alpha: int
    layout: str
    preferred_size: int
    max_words: int


def _luma(c: tuple[int, int, int]) -> float:
    r, g, b = c
    return 0.2126*r + 0.7152*g + 0.0722*b


def _distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    return sum((x-y)**2 for x, y in zip(a, b)) ** .5


@lru_cache(maxsize=128)
def palette_for_image(path_str: str) -> tuple[tuple[int, int, int], ...]:
    path = Path(path_str)
    with Image.open(path) as raw:
        image = raw.convert("RGB")
    thumb = image.copy()
    thumb.thumbnail((160, 160))
    q = thumb.quantize(colors=8, method=Image.Quantize.MEDIANCUT).convert("RGB")
    colors = q.getcolors(maxcolors=256) or []
    ranked = sorted(colors, reverse=True, key=lambda x: x[0])
    return tuple(color for _, color in ranked[:8])


def choose_accent(path: Path) -> tuple[int, int, int]:
    palette = palette_for_image(str(path))
    candidates = [c for c in palette if 55 < _luma(c) < 220]
    if not candidates:
        return (245, 203, 35)
    # Prefer a saturated-ish color separated from white/black.
    return max(candidates, key=lambda c: max(c)-min(c))


def direction_for(role: str, image_path: Path) -> ArtDirection:
    accent = choose_accent(image_path)
    # Keep brand-level accessibility: if source accent is too dark, brighten it.
    if _luma(accent) < 90:
        accent = tuple(min(255, int(v*1.65 + 22)) for v in accent)
    if role == "cold_open":
        return ArtDirection(accent, (255,255,255), (8,8,10), 210, "center_statement", 76, 5)
    if role == "tension":
        return ArtDirection(accent, (255,255,255), (15,15,18), 175, "lower_card", 58, 6)
    if role == "reveal":
        return ArtDirection(accent, (255,255,255), (10,10,12), 125, "top_badge", 54, 5)
    if role == "proof":
        return ArtDirection(accent, (255,255,255), (12,12,15), 165, "lower_card", 50, 6)
    if role == "price":
        return ArtDirection(accent, accent, (7,7,9), 205, "price_stage", 94, 4)
    if role == "cta":
        return ArtDirection(accent, (18,18,20), accent, 245, "cta", 58, 4)
    return ArtDirection(accent, (255,255,255), (12,12,15), 160, "lower_card", 52, 6)
