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
    role: str = "feature"


def _seller_claim(text: str) -> str:
    text = text.strip().rstrip(".")
    return f"Segundo o anúncio, {text[0].lower() + text[1:] if text else text}."


def _short_display(text: str, max_words: int = 6) -> str:
    words = text.strip().rstrip(".").split()
    return " ".join(words[:max_words]).upper()


def generate_creative_scenes(product: ProductData) -> tuple[CreativeScene, ...]:
    """Generate a compact ad-shaped structure without inventing product facts.

    Screen copy is deliberately shorter than narration. SFX are editorial accents,
    not transition markers. Scene duration is a minimum; prepare.py expands it to
    fit measured narration before rendering.
    """
    name = product.name or "este produto"
    scenes: list[CreativeScene] = [
        CreativeScene(2.6, "SEM FIO. SEM BAGUNÇA.", f"Olha esse {name}.", "pop", "woosh.wav", "hook")
    ]

    # Two proof points are enough for a sub-20-second ad. More facts belong in
    # product data, not automatically on screen.
    for claim in product.features[:2]:
        narration = _seller_claim(claim.text) if claim.source_type == "seller_claim" else claim.text.rstrip(".") + "."
        scenes.append(CreativeScene(3.0, _short_display(claim.text), narration, "pan_zoom", None, "proof"))

    if product.price is not None:
        price_text = f"R$ {product.price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        narration = f"O preço registrado no material era {price_text}."
        scenes.append(CreativeScene(3.0, price_text, narration, "slow_zoom", None, "price"))

    scenes.append(CreativeScene(2.4, "VALE O CLIQUE?", "E aí, vale o clique?", "pop", None, "cta"))
    return tuple(scenes)


def total_creative_duration(scenes: Iterable[CreativeScene]) -> float:
    return sum(scene.duration for scene in scenes)
