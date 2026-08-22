from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from .benchmark import BenchmarkProfile
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


def _hook(memory: CreativeMemory, benchmark: BenchmarkProfile) -> tuple[str, str]:
    style = memory.preferred_hook_style
    if benchmark.confidence >= 0.15 and benchmark.preferred_hook_style:
        style = benchmark.preferred_hook_style
    if style in {"problem_question", "native_content", "story_first"}:
        return "AINDA PRESO NOS FIOS?", "Seu setup ainda está preso nos fios?"
    if style == "comparison":
        return "COM FIO OU SEM FIO?", "Qual desses setups você escolheria?"
    if style in {"sensory_interruption", "audio_hook"}:
        return "OLHA ESSA MUDANÇA.", "Olha como uma mudança simples já limpa a mesa."
    return "DÁ PRA DEIXAR MAIS LIMPO.", "Dá para deixar a mesa bem mais limpa."


def generate_creative_scenes(
    product: ProductData,
    memory: CreativeMemory | None = None,
    benchmark: BenchmarkProfile | None = None,
) -> tuple[CreativeScene, ...]:
    """Create a short-form ad arc influenced by explicit human feedback and benchmark patterns."""
    memory = memory or CreativeMemory()
    benchmark = benchmark or BenchmarkProfile()
    name = product.name or "este produto"
    hook_text, hook_narration = _hook(memory, benchmark)
    hook_max = min(memory.hook_max_words, benchmark.hook_max_words or memory.hook_max_words)
    hook_text = _short_display(hook_text, hook_max)

    reveal_target = benchmark.product_reveal_target_s if benchmark.confidence >= 0.1 else 2.8
    cold = min(1.35, max(1.0, reveal_target * 0.45))
    tension = max(1.1, reveal_target - cold)

    scenes: list[CreativeScene] = [
        CreativeScene(round(cold, 2), hook_text, hook_narration, "pop", "woosh.wav", "cold_open"),
        CreativeScene(round(tension, 2), "DÁ PRA LIMPAR ISSO.", "Dá para deixar a mesa bem mais limpa.", "quick_zoom", None, "tension"),
        CreativeScene(2.2, "CONHEÇA O KIT", f"Esse é o {name}.", "pop", None, "reveal"),
    ]

    proof_limit = min(memory.max_proof_scenes, benchmark.max_proof_scenes or memory.max_proof_scenes)
    for claim in product.features[:proof_limit]:
        narration = _seller_claim(claim.text) if claim.source_type == "seller_claim" else claim.text.rstrip(".") + "."
        scenes.append(CreativeScene(2.5, _short_display(claim.text, 5), narration, "pan_zoom", None, "proof"))

    if product.price is not None:
        price_text = f"R$ {product.price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        scenes.append(CreativeScene(2.6, price_text, f"O preço registrado no material era {price_text}.", "slow_zoom", None, "price"))

    scenes.append(CreativeScene(2.0, "VALE O CLIQUE?", "E aí, vale o clique?", "pop", None, "cta"))
    return tuple(scenes)


def total_creative_duration(scenes: Iterable[CreativeScene]) -> float:
    return sum(scene.duration for scene in scenes)
