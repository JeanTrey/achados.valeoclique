from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class RetentionReport:
    score: int
    issues: tuple[str, ...]
    passed: bool


def audit_script(script: dict) -> RetentionReport:
    """Static creative gate. It cannot predict humans, but blocks known bad patterns."""
    scenes = script.get("scenes", [])
    issues: list[str] = []
    if not scenes:
        return RetentionReport(0, ("no scenes",), False)

    total = sum(float(s.get("duration", 0)) for s in scenes)
    first_three = sum(float(s.get("duration", 0)) for s in scenes[:2])
    first_text = str(scenes[0].get("text_primary") or "")
    if float(scenes[0].get("duration", 99)) > 1.8:
        issues.append("cold open is too slow")
    if len(first_text.split()) > 6:
        issues.append("hook has too many words")
    if first_three > 3.6:
        issues.append("opening progression is too slow")
    if total > 24:
        issues.append("video is too long for current VOC short-form target")
    if any(len(str(s.get("text_primary") or "").split()) > 8 for s in scenes):
        issues.append("screen copy is too dense")
    sfx_count = sum(bool(s.get("sfx")) for s in scenes)
    if sfx_count > max(2, len(scenes)//3):
        issues.append("too many transition sound effects")
    images = [s.get("image") for s in scenes if s.get("image")]
    if len(set(images)) == 1 and len(images) >= 4:
        issues.append("single source image repeated across the whole ad")
    if str(scenes[-1].get("text_primary") or "").upper() != "VALE O CLIQUE?":
        issues.append("final CTA is missing")

    score = max(0, 100 - len(issues) * 12)
    # Image repetition is currently a warning because source scarcity is real.
    blocking = [x for x in issues if x != "single source image repeated across the whole ad"]
    return RetentionReport(score, tuple(issues), not blocking and score >= 76)
