from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import ProductData


@dataclass(frozen=True)
class CreativeScene:
    duration: float
    text_primary: str
    narration_text: str
    animation: str = "pan_zoom"
    sfx: str | None = None


def _seller_claim(text: str) -> str:
    text = text.strip().rstrip(".")
    return f"Segundo o anúncio, {text[0].lower() + text[1:] if text else text}."


def generate_creative_scenes(product: ProductData) -> tuple[CreativeScene, ...]:
    """Generate a short factual-safe editorial structure from ProductData.

    This module never invents missing facts. Seller-provided characteristics are
    explicitly attributed in narration instead of being promoted to verified facts.
    """
    name = product.name or "este produto"
    scenes: list[CreativeScene] = [
        CreativeScene(
            duration=3.0,
            text_primary="VALE O CLIQUE?",
            narration_text=f"Olha esse {name}. Vale o clique?",
            animation="slow_zoom",
            sfx="woosh.wav",
        )
    ]

    for claim in product.features[:3]:
        narration = _seller_claim(claim.text) if claim.source_type == "seller_claim" else claim.text.rstrip(".") + "."
        scenes.append(
            CreativeScene(
                duration=3.2,
                text_primary=claim.text.upper(),
                narration_text=narration,
                animation="pan_zoom",
                sfx="woosh.wav",
            )
        )

    if product.price is not None:
        price_text = f"R$ {product.price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        if product.price_checked_at:
            narration = f"Na consulta de {product.price_checked_at}, o preço registrado era {price_text}."
        else:
            narration = f"O preço informado no material de origem era {price_text}."
        scenes.append(CreativeScene(3.0, price_text, narration, "slow_zoom"))

    scenes.append(
        CreativeScene(
            duration=2.6,
            text_primary="VALE O CLIQUE?",
            narration_text="E aí, vale o clique?",
            animation="slow_zoom",
            sfx=None,
        )
    )
    return tuple(scenes)


def total_creative_duration(scenes: Iterable[CreativeScene]) -> float:
    return sum(scene.duration for scene in scenes)
