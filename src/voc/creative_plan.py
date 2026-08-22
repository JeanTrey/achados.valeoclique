from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from .asset_director import AssetVariant
from .creative import CreativeScene
from .models import ProductData
from .visual_director import direction_for


@dataclass(frozen=True)
class PlannedScene:
    index: int
    role: str
    purpose: str
    duration_s: float
    asset: str
    layout: str
    text: str
    text_words: int
    preferred_text_size: int
    accent: tuple[int, int, int]
    panel_alpha: int
    motion: str
    why_this_frame: str


@dataclass(frozen=True)
class CreativePlan:
    product_id: str
    strategy: str
    visual_rule: str
    scenes: tuple[PlannedScene, ...]

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "strategy": self.strategy,
            "visual_rule": self.visual_rule,
            "scenes": [asdict(scene) for scene in self.scenes],
        }


_PURPOSES = {
    "cold_open": "stop the scroll with a product-relevant visual problem",
    "tension": "make the problem immediately legible without repeating the hook",
    "reveal": "show the real product clearly for the first time",
    "proof": "support one claim with a real product detail",
    "price": "make the offer easy to read without covering the product",
    "cta": "close with one simple decision prompt",
}


def _why(role: str, asset: str) -> str:
    if role == "cold_open":
        return "Use a detail crop rather than a catalogue poster; the frame must feel like content before it feels like an ad."
    if role == "tension":
        return "Change framing and information; never repeat the previous frame with only new copy."
    if role == "reveal":
        return "Return to a truthful full-product view so the viewer understands what is being sold."
    if role == "proof":
        return "Use a close/detail derived from the real listing image; text is a caption, not the main visual."
    if role == "price":
        return "Keep product visible and isolate the price in negative space."
    if role == "cta":
        return "End cleanly; no new factual claim and no giant banner."
    return f"Use {asset} to introduce genuinely new visual information."


def build_creative_plan(
    product: ProductData,
    product_dir: Path,
    scenes: tuple[CreativeScene, ...],
    assigned_assets: list[str | None],
) -> CreativePlan:
    planned: list[PlannedScene] = []
    for index, (scene, asset) in enumerate(zip(scenes, assigned_assets), start=1):
        if not asset:
            raise ValueError(f"scene {index} has no visual asset; storyboard cannot be directed")
        image_path = product_dir / "images" / asset
        art = direction_for(scene.role, image_path)
        # The plan deliberately caps typography below the older renderer defaults.
        size_cap = 62 if scene.role == "price" else 48 if scene.role == "cold_open" else 42
        preferred = min(art.preferred_size, size_cap)
        planned.append(PlannedScene(
            index=index,
            role=scene.role,
            purpose=_PURPOSES.get(scene.role, "introduce new information"),
            duration_s=float(scene.duration),
            asset=asset,
            layout=art.layout,
            text=scene.text_primary,
            text_words=len(scene.text_primary.split()),
            preferred_text_size=preferred,
            accent=art.accent,
            panel_alpha=min(art.panel_alpha, 175),
            motion=scene.animation,
            why_this_frame=_why(scene.role, asset),
        ))
    return CreativePlan(
        product_id=product.id,
        strategy="problem -> visual change -> truthful reveal -> proof -> offer -> decision",
        visual_rule="Every scene must introduce new visual information. Product imagery leads; copy supports it.",
        scenes=tuple(planned),
    )
