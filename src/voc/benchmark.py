from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from statistics import median


@dataclass(frozen=True)
class BenchmarkProfile:
    sample_count: int = 0
    reference_count: int = 0
    confidence: float = 0.0
    preferred_hook_style: str = "problem_question"
    hook_max_words: int = 5
    product_reveal_target_s: float = 2.8
    target_duration_s: float = 18.0
    avg_shot_duration_s: float = 1.8
    max_proof_scenes: int = 2
    price_emphasis: str = "strong"
    cta_style: str = "single_final"
    native_content_bias: float = 0.7
    patterns: tuple[str, ...] = ()


def _read_records(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [x for x in raw.get("records", []) if isinstance(x, dict)]


def build_benchmark_profile(root: Path) -> BenchmarkProfile:
    references = _read_records(root / "benchmarks" / "records.json")
    analysed = _read_records(root / "benchmarks" / "generated_records.json")
    # Only records derived from actual media count toward training confidence.
    measured = [r for r in analysed if r.get("source_type") in {"public_video_analysis", "local_video_analysis"}]
    durations = [float(r["duration_s"]) for r in measured if r.get("duration_s")]
    shots = [float(r["avg_shot_duration_s"]) for r in measured if r.get("avg_shot_duration_s")]
    hooks = [str(r.get("hook_style")) for r in measured if r.get("hook_style")]
    reference_hooks = [str(r.get("hook_style")) for r in references if r.get("hook_style")]
    preferred = max(set(hooks), key=hooks.count) if hooks else (max(set(reference_hooks), key=reference_hooks.count) if reference_hooks else "problem_question")
    patterns: list[str] = []
    for record in [*references, *measured]:
        patterns.extend(str(x) for x in record.get("patterns", []))
    return BenchmarkProfile(
        sample_count=len(measured),
        reference_count=len(references),
        confidence=round(min(1.0, len(measured) / 50.0), 3),
        preferred_hook_style=preferred,
        product_reveal_target_s=2.8,
        target_duration_s=round(median(durations), 2) if durations else 18.0,
        avg_shot_duration_s=round(median(shots), 2) if shots else 1.8,
        native_content_bias=0.85 if references else 0.7,
        patterns=tuple(sorted(set(patterns))),
    )


def write_profile(root: Path) -> BenchmarkProfile:
    profile = build_benchmark_profile(root)
    path = root / "memory" / "benchmark_profile.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "sample_count": profile.sample_count,
        "reference_count": profile.reference_count,
        "confidence": profile.confidence,
        "preferred_hook_style": profile.preferred_hook_style,
        "hook_max_words": profile.hook_max_words,
        "product_reveal_target_s": profile.product_reveal_target_s,
        "target_duration_s": profile.target_duration_s,
        "avg_shot_duration_s": profile.avg_shot_duration_s,
        "max_proof_scenes": profile.max_proof_scenes,
        "price_emphasis": profile.price_emphasis,
        "cta_style": profile.cta_style,
        "native_content_bias": profile.native_content_bias,
        "patterns": list(profile.patterns),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return profile
