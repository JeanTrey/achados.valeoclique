from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CreativeMemory:
    hook_max_words: int = 5
    max_proof_scenes: int = 2
    max_sfx_before_cta: int = 1
    narration_breathing_room_s: float = 0.42
    preferred_hook_style: str = "problem_question"
    avoid_patterns: tuple[str, ...] = ()
    approved_patterns: tuple[str, ...] = ()


def load_creative_memory(root: Path) -> CreativeMemory:
    path = root / "memory" / "creative_profile.json"
    if not path.is_file():
        return CreativeMemory()
    raw = json.loads(path.read_text(encoding="utf-8"))
    return CreativeMemory(
        hook_max_words=int(raw.get("hook_max_words", 5)),
        max_proof_scenes=int(raw.get("max_proof_scenes", 2)),
        max_sfx_before_cta=int(raw.get("max_sfx_before_cta", 1)),
        narration_breathing_room_s=float(raw.get("narration_breathing_room_s", 0.42)),
        preferred_hook_style=str(raw.get("preferred_hook_style", "problem_question")),
        avoid_patterns=tuple(str(x) for x in raw.get("avoid_patterns", [])),
        approved_patterns=tuple(str(x) for x in raw.get("approved_patterns", [])),
    )


def summarize_feedback(root: Path) -> dict:
    """Aggregate explicit human reviews without pretending this is model training."""
    feedback_dir = root / "feedback"
    files = sorted(feedback_dir.glob("*.json")) if feedback_dir.exists() else []
    records = []
    for path in files:
        try:
            records.append(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            continue
    if not records:
        return {"reviews": 0, "avg_overall": None, "rejected_patterns": []}
    scores = [float(r["scores"]["overall"]) for r in records if isinstance(r.get("scores"), dict) and r["scores"].get("overall") is not None]
    rejected: list[str] = []
    for r in records:
        rejected.extend(str(x) for x in r.get("reject", []))
    return {
        "reviews": len(records),
        "avg_overall": round(sum(scores) / len(scores), 2) if scores else None,
        "rejected_patterns": sorted(set(rejected)),
    }
