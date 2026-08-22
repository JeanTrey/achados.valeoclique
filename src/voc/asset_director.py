from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


@dataclass(frozen=True)
class AssetVariant:
    file: str
    kind: str
    score: float


def _score_crop(image: Image.Image) -> float:
    arr = np.asarray(image.convert("L").resize((96, 96)), dtype=np.float32)
    dx = np.abs(np.diff(arr, axis=1)).mean()
    dy = np.abs(np.diff(arr, axis=0)).mean()
    contrast = float(arr.std())
    return float(dx + dy + contrast * .35)


def _crop_candidates(image: Image.Image) -> list[tuple[str, tuple[int, int, int, int]]]:
    w, h = image.size
    side = min(w, h)
    if side <= 1:
        return [("hero", (0, 0, w, h))]
    ratios = [1.0, .82, .66]
    anchors = [(.5, .5), (.3, .5), (.7, .5), (.5, .32), (.5, .68)]
    out: list[tuple[str, tuple[int, int, int, int]]] = []
    for r in ratios:
        cw = max(1, int(side * r))
        ch = cw
        for ax, ay in anchors:
            cx, cy = int(w * ax), int(h * ay)
            left = min(max(0, cx - cw // 2), max(0, w - cw))
            top = min(max(0, cy - ch // 2), max(0, h - ch))
            out.append((f"crop_{int(r*100)}_{int(ax*100)}_{int(ay*100)}", (left, top, left + cw, top + ch)))
    return out


def _save_variant(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(path, quality=94, subsampling=0)


def build_asset_pack(product_dir: Path, max_variants_per_source: int = 5) -> list[AssetVariant]:
    """Turn scarce catalogue photos into varied, truthful visual assets.

    Only crops/grades the real source image; it never invents product geometry.
    Generated context imagery belongs to a separate future provider.
    """
    images_dir = product_dir / "images"
    derived_dir = images_dir / "derived"
    sources = sorted(p for p in images_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS) if images_dir.exists() else []
    variants: list[AssetVariant] = []
    for source_index, source in enumerate(sources, start=1):
        with Image.open(source) as raw:
            image = raw.convert("RGB")
        candidates = []
        for kind, box in _crop_candidates(image):
            crop = image.crop(box)
            candidates.append((_score_crop(crop), kind, crop))
        candidates.sort(reverse=True, key=lambda x: x[0])
        selected = candidates[:max_variants_per_source]
        # Always keep a full truthful product view as an anchor asset.
        full_name = f"s{source_index:02d}_full.jpg"
        _save_variant(image, derived_dir / full_name)
        variants.append(AssetVariant(f"derived/{full_name}", "full", 999.0))
        for rank, (score, kind, crop) in enumerate(selected, start=1):
            # Mild contrast only; no hallucinated content or aggressive recoloring.
            crop = ImageEnhance.Contrast(crop).enhance(1.04)
            name = f"s{source_index:02d}_{rank:02d}_{kind}.jpg"
            _save_variant(crop, derived_dir / name)
            variants.append(AssetVariant(f"derived/{name}", kind, round(score, 3)))
    return variants


def assign_assets_to_roles(variants: list[AssetVariant], roles: list[str]) -> list[str | None]:
    if not variants:
        return [None] * len(roles)
    full = [v for v in variants if v.kind == "full"] or variants
    close = [v for v in variants if v.kind != "full"] or variants
    close = sorted(close, key=lambda v: v.score, reverse=True)
    result: list[str | None] = []
    ci = 0
    for role in roles:
        if role in {"reveal", "price", "cta"}:
            result.append(full[len(result) % len(full)].file)
        else:
            result.append(close[ci % len(close)].file)
            ci += 1
    return result
