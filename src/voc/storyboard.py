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


def _render_panel(frame: Image.Image, scene: PlannedScene, font_root: Path) -> Image.Image:
    w, h = frame.size
    canvas = frame.convert("RGBA")
    overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    accent = tuple(scene.accent)
    white = (250, 250, 250)

    # Layouts intentionally keep copy within a small percentage of the screen.
    if scene.role == "cold_open":
        box = (int(w*.08), int(h*.10), int(w*.78), int(h*.27))
        draw.rounded_rectangle(box, radius=22, fill=(10, 10, 12, 145))
        style = {"size": scene.preferred_text_size, "min_size": 30, "color": white, "stroke_width": 0}
    elif scene.role == "reveal":
        box = (int(w*.08), int(h*.08), int(w*.55), int(h*.17))
        draw.rounded_rectangle(box, radius=18, fill=(10, 10, 12, 130))
        style = {"size": scene.preferred_text_size, "min_size": 28, "color": white, "stroke_width": 0}
    elif scene.role == "price":
        box = (int(w*.08), int(h*.70), int(w*.60), int(h*.84))
        draw.rounded_rectangle(box, radius=24, fill=(8, 8, 10, 150))
        style = {"size": scene.preferred_text_size, "min_size": 38, "color": accent, "stroke_width": 0}
    elif scene.role == "cta":
        box = (int(w*.20), int(h*.76), int(w*.80), int(h*.86))
        draw.rounded_rectangle(box, radius=28, fill=accent + (175,))
        style = {"size": scene.preferred_text_size, "min_size": 30, "color": (18, 18, 20), "stroke_width": 0}
    else:
        box = (int(w*.08), int(h*.72), int(w*.72), int(h*.82))
        draw.rounded_rectangle(box, radius=20, fill=(10, 10, 12, 135))
        style = {"size": scene.preferred_text_size, "min_size": 28, "color": white, "stroke_width": 0}

    canvas.alpha_composite(overlay)
    pad_x, pad_y = 18, 8
    draw_text_block(canvas, scene.text, (box[0]+pad_x, box[1]+pad_y, box[2]-pad_x, box[3]-pad_y), style, 255, font_root)
    return canvas.convert("RGB")


def render_storyboard(plan: CreativePlan, product_dir: Path, output_dir: Path, size: tuple[int, int] = (720, 1280)) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    frames: list[Path] = []
    for scene in plan.scenes:
        source = product_dir / "images" / scene.asset
        if not source.is_file():
            raise FileNotFoundError(f"storyboard asset missing: {source}")
        with Image.open(source) as raw:
            base = _cover(raw, size)
        # Subtle depth only; the real asset remains readable.
        if scene.role in {"cold_open", "tension"}:
            softened = base.filter(ImageFilter.GaussianBlur(radius=1.2))
            base = Image.blend(base, softened, 0.20)
        frame = _render_panel(base, scene, product_dir.parent.parent / "assets" / "fonts")
        path = output_dir / f"scene_{scene.index:02d}_{scene.role}.jpg"
        frame.save(path, quality=94, subsampling=0)
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
    # Human review is mandatory by design. Machine checks only catch obvious regressions.
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
