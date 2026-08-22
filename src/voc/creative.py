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


def _short_display(text: str, max_words: int = 5) -> str:
    return " ".join(text.strip().rstrip(".").split()[:max_words]).upper()


def _short_spoken_claim(text: str, seller_claim: bool) -> str:
    spoken = " ".join(text.strip().rstrip(".").split()[:7])
    if seller_claim:
        return f"Segundo o anúncio: {spoken}."
    return spoken + "."


def _product_label(product: ProductData) -> str:
    brand = str(product.extra.get("marca") or product.extra.get("brand") or "").strip()
    model = str(product.extra.get("modelo") or product.extra.get("model") or "").strip()
    if brand or model:
        return " ".join(x for x in (brand, model) if x)
    if product.name:
        return " ".join(product.name.split()[:5])
    return "este produto"


def _hook(memory: CreativeMemory, benchmark: BenchmarkProfile) -> tuple[str, str]:
    style = memory.preferred_hook_style
    if benchmark.confidence >= 0.15 and benchmark.preferred_hook_style:
        style = benchmark.preferred_hook_style
    if style in {"problem_question", "native_content", "story_first"}:
        return "AINDA PRESO NOS FIOS?", "Ainda preso nos fios?"
    if style == "comparison":
        return "COM FIO OU SEM FIO?", "Com fio ou sem fio?"
    if style in {"sensory_interruption", "audio_hook"}:
        return "OLHA ESSA MUDANÇA.", "Olha essa mudança."
    return "DÁ PRA DEIXAR MAIS LIMPO.", "Dá para deixar mais limpo."


def generate_creative_scenes(
    product: ProductData,
    memory: CreativeMemory | None = None,
    benchmark: BenchmarkProfile | None = None,
) -> tuple[CreativeScene, ...]:
    """Create a concise short-form ad arc influenced by human feedback and benchmark patterns."""
    memory = memory or CreativeMemory()
    benchmark = benchmark or BenchmarkProfile()
    label = _product_label(product)
    hook_text, hook_narration = _hook(memory, benchmark)
    hook_max = min(memory.hook_max_words, benchmark.hook_max_words or memory.hook_max_words)
    hook_text = _short_display(hook_text, hook_max)

    reveal_target = benchmark.product_reveal_target_s if benchmark.confidence >= 0.1 else 2.8
    cold = min(1.25, max(1.0, reveal_target * 0.42))
    tension = max(1.0, min(1.45, reveal_target - cold))

    scenes: list[CreativeScene] = [
        CreativeScene(round(cold, 2), hook_text, hook_narration, "pop", "woosh.wav", "cold_open"),
        CreativeScene(round(tension, 2), "DÁ PRA LIMPAR ISSO.", "Mesa mais limpa.", "quick_zoom", None, "tension"),
        CreativeScene(2.0, "CONHEÇA O KIT", f"Esse é o {label}.", "pop", None, "reveal"),
    ]

    proof_limit = min(memory.max_proof_scenes, benchmark.max_proof_scenes or memory.max_proof_scenes)
    for claim in product.features[:proof_limit]:
        narration = _short_spoken_claim(claim.text, claim.source_type == "seller_claim")
        scenes.append(CreativeScene(2.35, _short_display(claim.text, 5), narration, "pan_zoom", None, "proof"))

    if product.price is not None:
        price_text = f"R$ {product.price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        scenes.append(CreativeScene(2.4, price_text, f"Registrado por {price_text}.", "slow_zoom", None, "price"))

    scenes.append(CreativeScene(1.8, "VALE O CLIQUE?", "Vale o clique?", "pop", None, "cta"))
    return tuple(scenes)


def total_creative_duration(scenes: Iterable[CreativeScene]) -> float:
    return sum(scene.duration for scene in scenes)
