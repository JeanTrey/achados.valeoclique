from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from statistics import median


@dataclass(frozen=True)
class BenchmarkProfile:
    sample_count: int = 0
    confidence: float = 0.0
    preferred_hook_style: str = "problem_question"
    hook_max_words: int = 5
    product_reveal_target_s: float = 2.8
    target_duration_s: float = 18.0
    max_proof_scenes: int = 2
    price_emphasis: str = "strong"
    cta_style: str = "single_final"
    native_content_bias: float = 0.7
    patterns: tuple[str, ...] = ()


def _mode(values: list[str], default: str) -> str:
    if not values:
        return default
    counts = {v: values.count(v) for v in set(values)}
    return max(counts, key=counts.get)


def load_benchmark_records(root: Path) -> list[dict]:
    path = root / "benchmarks" / "records.json"
    if not path.is_file():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [x for x in raw.get("records", []) if isinstance(x, dict)]


def build_benchmark_profile(root: Path) -> BenchmarkProfile:
    records = load_benchmark_records(root)
    if not records:
        return BenchmarkProfile()
    hooks = [str(r.get("hook_style")) for r in records if r.get("hook_style")]
    reveal = [float(r["product_reveal_s"]) for r in records if r.get("product_reveal_s") is not None]
    durations = [float(r["duration_s"]) for r in records if r.get("duration_s") is not None]
    native = [float(r.get("native_content_score", 0.7)) for r in records]
    patterns: list[str] = []
    for record in records:
        patterns.extend(str(x) for x in record.get("patterns", []))
    confidence = min(1.0, len(records) / 50.0)
    return BenchmarkProfile(
        sample_count=len(records),
        confidence=round(confidence, 3),
        preferred_hook_style=_mode(hooks, "problem_question"),
        hook_max_words=5,
        product_reveal_target_s=round(median(reveal), 2) if reveal else 2.8,
        target_duration_s=round(median(durations), 2) if durations else 18.0,
        max_proof_scenes=2,
        price_emphasis="strong",
        cta_style="single_final",
        native_content_bias=round(sum(native) / len(native), 2) if native else 0.7,
        patterns=tuple(sorted(set(patterns))),
    )


def write_profile(root: Path) -> BenchmarkProfile:
    profile = build_benchmark_profile(root)
    path = root / "memory" / "benchmark_profile.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "sample_count": profile.sample_count,
        "confidence": profile.confidence,
        "preferred_hook_style": profile.preferred_hook_style,
        "hook_max_words": profile.hook_max_words,
        "product_reveal_target_s": profile.product_reveal_target_s,
        "target_duration_s": profile.target_duration_s,
        "max_proof_scenes": profile.max_proof_scenes,
        "price_emphasis": profile.price_emphasis,
        "cta_style": profile.cta_style,
        "native_content_bias": profile.native_content_bias,
        "patterns": list(profile.patterns),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return profile
