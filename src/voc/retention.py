from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class RetentionReport:
    score: int
    issues: tuple[str, ...]
    passed: bool


def _creative_duration(scene: dict) -> float:
    # TTS may expand the rendered scene to protect intelligibility. Retention
    # should judge the intended edit separately, otherwise a slow TTS provider
    # falsely turns a good 1.3 s hook into a failed 3 s hook.
    return float(scene.get("creative_duration", scene.get("duration", 0)))


def audit_script(script: dict) -> RetentionReport:
    """Static preflight gate for known bad creative patterns."""
    scenes = script.get("scenes", [])
    issues: list[str] = []
    if not scenes:
        return RetentionReport(0, ("no scenes",), False)

    creative_total = sum(_creative_duration(s) for s in scenes)
    rendered_total = sum(float(s.get("duration", 0)) for s in scenes)
    first_two = sum(_creative_duration(s) for s in scenes[:2])
    first_text = str(scenes[0].get("text_primary") or "")

    if _creative_duration(scenes[0]) > 1.8:
        issues.append("cold open is too slow")
    if len(first_text.split()) > 6:
        issues.append("hook has too many words")
    if first_two > 3.6:
        issues.append("opening progression is too slow")
    if creative_total > 24:
        issues.append("creative plan is too long for current VOC short-form target")
    if rendered_total > creative_total + 7:
        issues.append("narration expands the edit too much; shorten spoken copy")
    if any(len(str(s.get("text_primary") or "").split()) > 8 for s in scenes):
        issues.append("screen copy is too dense")
    sfx_count = sum(bool(s.get("sfx")) for s in scenes)
    if sfx_count > max(2, len(scenes) // 3):
        issues.append("too many transition sound effects")
    images = [s.get("image") for s in scenes if s.get("image")]
    if len(set(images)) == 1 and len(images) >= 4:
        issues.append("single source image repeated across the whole ad")
    if str(scenes[-1].get("text_primary") or "").upper() != "VALE O CLIQUE?":
        issues.append("final CTA is missing")

    score = max(0, 100 - len(issues) * 12)
    warning_only = {"single source image repeated across the whole ad"}
    blocking = [x for x in issues if x not in warning_only]
    return RetentionReport(score, tuple(issues), not blocking and score >= 76)
