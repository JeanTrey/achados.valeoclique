from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

from .creative_plan import CreativePlan, PlannedScene
from .text_renderer import draw_text_block


@dataclass(frozen=True)
class StoryboardReport:
    passed_machine_checks: bool
    status: str
    issues: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def _cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(image.convert("RGB"), size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))


def _contain(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    copy = image.convert("RGB").copy()
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    return copy


def _rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0]-1, size[1]-1), radius=radius, fill=255)
    return mask


def _make_background(source: Image.Image, size: tuple[int, int], accent: tuple[int, int, int]) -> Image.Image:
    bg = _cover(source, size).filter(ImageFilter.GaussianBlur(radius=34))
    shade = Image.new("RGBA", size, (8, 10, 14, 150))
    bg = bg.convert("RGBA")
    bg.alpha_composite(shade)
    # Very subtle product-derived accent glow, not a neon wash.
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    w, h = size
    gd.ellipse((int(w*.48), int(h*.08), int(w*1.18), int(h*.72)), fill=accent + (42,))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=90))
    bg.alpha_composite(glow)
    return bg


def _paste_product_card(canvas: Image.Image, source: Image.Image, role: str) -> None:
    w, h = canvas.size
    if role in {"cold_open", "tension", "proof"}:
        box = (int(w*.07), int(h*.24), int(w*.93), int(h*.72))
    else:
        box = (int(w*.07), int(h*.22), int(w*.93), int(h*.68))
    bw, bh = box[2]-box[0], box[3]-box[1]
    card = Image.new("RGBA", (bw, bh), (246, 246, 244, 250))
    product = _contain(source, (int(bw*.92), int(bh*.90)))
    px = (bw - product.width)//2
    py = (bh - product.height)//2
    card.paste(product, (px, py))
    shadow = Image.new("RGBA", canvas.size, (0,0,0,0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((box[0]+4, box[1]+14, box[2]+4, box[3]+14), radius=28, fill=(0,0,0,70))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=16))
    canvas.alpha_composite(shadow)
    mask = _rounded_mask((bw, bh), 28)
    canvas.paste(card, (box[0], box[1]), mask)


def _render_copy(canvas: Image.Image, scene: PlannedScene, font_root: Path) -> None:
    w, h = canvas.size
    accent = tuple(scene.accent)
    white = (248, 248, 246)
    dark = (15, 17, 20)
    overlay = Image.new("RGBA", canvas.size, (0,0,0,0))
    draw = ImageDraw.Draw(overlay)

    # Small editorial eyebrow replaces the old giant grey pill language.
    eyebrow_y = int(h*.08)
    draw.rounded_rectangle((int(w*.07), eyebrow_y, int(w*.18), eyebrow_y+8), radius=4, fill=accent + (240,))

    if scene.role == "price":
        box = (int(w*.07), int(h*.72), int(w*.93), int(h*.90))
        style = {"size": min(scene.preferred_text_size, 58), "min_size": 36, "color": white, "stroke_width": 0}
        draw.text((int(w*.07), int(h*.69)), "OFERTA DO VÍDEO", fill=accent+(255,))
    elif scene.role == "cta":
        box = (int(w*.15), int(h*.75), int(w*.85), int(h*.85))
        draw.rounded_rectangle(box, radius=22, fill=accent + (235,))
        style = {"size": min(scene.preferred_text_size, 38), "min_size": 28, "color": dark, "stroke_width": 0}
    elif scene.role == "reveal":
        box = (int(w*.07), int(h*.72), int(w*.90), int(h*.84))
        style = {"size": min(scene.preferred_text_size, 38), "min_size": 28, "color": white, "stroke_width": 0}
    else:
        box = (int(w*.07), int(h*.73), int(w*.90), int(h*.86))
        style = {"size": min(scene.preferred_text_size, 36), "min_size": 26, "color": white, "stroke_width": 0}

    canvas.alpha_composite(overlay)
    draw_text_block(canvas, scene.text, box, style, 255, font_root)


def render_storyboard(plan: CreativePlan, product_dir: Path, output_dir: Path, size: tuple[int, int] = (720, 1280)) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    frames: list[Path] = []
    font_root = product_dir.parent.parent / "assets" / "fonts"
    for scene in plan.scenes:
        source_path = product_dir / "images" / scene.asset
        if not source_path.is_file():
            raise FileNotFoundError(f"storyboard asset missing: {source_path}")
        with Image.open(source_path) as raw:
            source = raw.convert("RGB")
        canvas = _make_background(source, size, tuple(scene.accent))
        _paste_product_card(canvas, source, scene.role)
        _render_copy(canvas, scene, font_root)
        path = output_dir / f"scene_{scene.index:02d}_{scene.role}.jpg"
        canvas.convert("RGB").save(path, quality=94, subsampling=0)
        frames.append(path)

    if frames:
        thumb_w = 270
        thumb_h = int(thumb_w * size[1] / size[0])
        gap = 18
        cols = min(4, len(frames))
        rows = (len(frames) + cols - 1) // cols
        sheet = Image.new("RGB", (gap + cols*(thumb_w+gap), gap + rows*(thumb_h+56+gap)), (22,22,24))
        draw = ImageDraw.Draw(sheet)
        for i, (scene, path) in enumerate(zip(plan.scenes, frames)):
            with Image.open(path) as raw:
                thumb = raw.convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            x = gap + (i % cols)*(thumb_w+gap)
            y = gap + (i // cols)*(thumb_h+56+gap)
            sheet.paste(thumb, (x,y))
            draw.text((x, y+thumb_h+8), f"{scene.index:02d} · {scene.role}", fill=(235,235,235))
            draw.text((x, y+thumb_h+28), scene.purpose[:38], fill=(165,165,170))
        sheet.save(output_dir / "contact_sheet.jpg", quality=94, subsampling=0)
    return frames


def audit_storyboard_plan(plan: CreativePlan) -> StoryboardReport:
    issues: list[str] = []
    warnings: list[str] = []
    scenes = list(plan.scenes)
    if len(scenes) < 5:
        issues.append("storyboard has too few scenes for the current ad arc")
    if any(scene.text_words > 6 for scene in scenes):
        issues.append("copy density exceeds six words in at least one frame")
    for a, b in zip(scenes, scenes[1:]):
        if a.asset == b.asset:
            warnings.append(f"scenes {a.index} and {b.index} reuse the exact same asset")
        if a.layout == b.layout and a.role not in {"proof"}:
            warnings.append(f"scenes {a.index} and {b.index} repeat the same layout")
    distinct = len({scene.asset for scene in scenes})
    if distinct < min(3, len(scenes)):
        warnings.append("visual variety is still limited; collector/asset director needs more source material")
    return StoryboardReport(
        passed_machine_checks=not issues,
        status="REQUIRES_HUMAN_REVIEW" if not issues else "BLOCKED",
        issues=tuple(issues),
        warnings=tuple(dict.fromkeys(warnings)),
    )


def write_storyboard_bundle(plan: CreativePlan, product_dir: Path) -> StoryboardReport:
    out = product_dir / "storyboard"
    render_storyboard(plan, product_dir, out)
    report = audit_storyboard_plan(plan)
    (product_dir / "creative_plan.json").write_text(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "storyboard_report.json").write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report
