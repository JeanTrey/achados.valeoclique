from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from .creative_memory import CreativeMemory
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


def _short_display(text: str, max_words: int = 5) -> str:
    return " ".join(text.strip().rstrip(".").split()[:max_words]).upper()


def _hook(memory: CreativeMemory) -> tuple[str, str]:
    if memory.preferred_hook_style == "problem_question":
        return "AINDA PRESO NOS FIOS?", "Seu setup ainda está preso nos fios?"
    return "DÁ PRA DEIXAR MAIS LIMPO.", "Dá para deixar a mesa bem mais limpa."


def generate_creative_scenes(product: ProductData, memory: CreativeMemory | None = None) -> tuple[CreativeScene, ...]:
    """Create a short-form ad arc influenced by explicit, versioned human feedback."""
    memory = memory or CreativeMemory()
    name = product.name or "este produto"
    hook_text, hook_narration = _hook(memory)
    hook_text = _short_display(hook_text, memory.hook_max_words)

    scenes: list[CreativeScene] = [
        CreativeScene(1.35, hook_text, hook_narration, "pop", "woosh.wav", "cold_open"),
        CreativeScene(1.65, "DÁ PRA LIMPAR ISSO.", "Dá para deixar a mesa bem mais limpa.", "quick_zoom", None, "tension"),
        CreativeScene(2.4, "CONHEÇA O KIT", f"Esse é o {name}.", "pop", None, "reveal"),
    ]

    for claim in product.features[: memory.max_proof_scenes]:
        narration = _seller_claim(claim.text) if claim.source_type == "seller_claim" else claim.text.rstrip(".") + "."
        scenes.append(CreativeScene(2.7, _short_display(claim.text, 5), narration, "pan_zoom", None, "proof"))

    if product.price is not None:
        price_text = f"R$ {product.price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        scenes.append(CreativeScene(2.8, price_text, f"O preço registrado no material era {price_text}.", "slow_zoom", None, "price"))

    scenes.append(CreativeScene(2.2, "VALE O CLIQUE?", "E aí, vale o clique?", "pop", None, "cta"))
    return tuple(scenes)


def total_creative_duration(scenes: Iterable[CreativeScene]) -> float:
    return sum(scene.duration for scene in scenes)
