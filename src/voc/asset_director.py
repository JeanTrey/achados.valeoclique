from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageStat


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


@dataclass(frozen=True)
class AssetVariant:
    file: str
    kind: str
    score: float


def _score_crop(image: Image.Image) -> float:
    """Prefer object/detail regions over flat saturated catalogue banners.

    This is intentionally generic: edge/detail + tonal variety are rewarded,
    while large highly-saturated flat regions (common in listing text bands)
    are penalized. It is not semantic object detection, but it is a much safer
    fallback than pure contrast scoring.
    """
    rgb = image.convert("RGB").resize((128, 128))
    gray = np.asarray(rgb.convert("L"), dtype=np.float32)
    arr = np.asarray(rgb, dtype=np.float32)
    dx = float(np.abs(np.diff(gray, axis=1)).mean())
    dy = float(np.abs(np.diff(gray, axis=0)).mean())
    contrast = float(gray.std())
    dark_fraction = float((gray < 105).mean())
    chroma = arr.max(axis=2) - arr.min(axis=2)
    saturation = float(chroma.mean())
    very_flat = float(((np.abs(np.diff(gray, axis=1)).mean(axis=1) < 7)).mean())
    return dx + dy + contrast * .45 + dark_fraction * 35.0 - saturation * .12 - very_flat * 8.0


def _crop_candidates(image: Image.Image) -> list[tuple[str, tuple[int, int, int, int]]]:
    w, h = image.size
    out: list[tuple[str, tuple[int, int, int, int]]] = []

    # Product listings often contain a wide product hero surrounded by text.
    # Generate wide and square windows so the director is not forced into a
    # destructive square crop for long objects such as keyboards or shoes.
    specs = [
        (0.96, 0.42), (0.88, 0.48), (0.78, 0.50),
        (0.72, 0.72), (0.58, 0.58),
    ]
    anchors = [(.5, .25), (.5, .38), (.5, .52), (.32, .38), (.68, .38), (.32, .58), (.68, .58)]
    for rw, rh in specs:
        cw = max(1, min(w, int(w * rw)))
        ch = max(1, min(h, int(h * rh)))
        for ax, ay in anchors:
            cx, cy = int(w * ax), int(h * ay)
            left = min(max(0, cx - cw // 2), max(0, w - cw))
            top = min(max(0, cy - ch // 2), max(0, h - ch))
            out.append((f"crop_{int(rw*100)}x{int(rh*100)}_{int(ax*100)}_{int(ay*100)}", (left, top, left + cw, top + ch)))
    return out


def _save_variant(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(path, quality=94, subsampling=0)


def build_asset_pack(product_dir: Path, max_variants_per_source: int = 6) -> list[AssetVariant]:
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

        full_name = f"s{source_index:02d}_full.jpg"
        _save_variant(image, derived_dir / full_name)
        variants.append(AssetVariant(f"derived/{full_name}", "full", 999.0))

        for rank, (score, kind, crop) in enumerate(candidates[:max_variants_per_source], start=1):
            crop = ImageEnhance.Contrast(crop).enhance(1.03)
            name = f"s{source_index:02d}_{rank:02d}_{kind}.jpg"
            _save_variant(crop, derived_dir / name)
            variants.append(AssetVariant(f"derived/{name}", kind, round(score, 3)))
    return variants


def assign_assets_to_roles(variants: list[AssetVariant], roles: list[str]) -> list[str | None]:
    if not variants:
        return [None] * len(roles)
    full = [v for v in variants if v.kind == "full"] or variants
    detail = sorted([v for v in variants if v.kind != "full"] or variants, key=lambda v: v.score, reverse=True)
    result: list[str | None] = []
    di = 0
    for role in roles:
        # Full listing art is now limited to reveal/offer anchors. Hooks/proofs
        # must use a detail region so the same catalogue poster cannot dominate
        # the entire ad again.
        if role in {"reveal", "price", "cta"}:
            result.append(full[0].file)
        else:
            result.append(detail[di % len(detail)].file)
            di += 1
    return result
