from __future__ import annotations


def ease_out_cubic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def motion(animation: str | None, progress: float) -> tuple[float, float, float]:
    p = max(0.0, min(1.0, progress))
    scale = 1.0 + (0.035 * p if animation in {"zoom", "slow_zoom", "pan_zoom"} else 0.0)
    x = (p - 0.5) * 0.025 if animation in {"pan", "slow_pan", "pan_zoom"} else 0.0
    return scale, x, 0.0


def text_alpha(progress: float, animation: str | None) -> int:
    if animation in {"none", None}:
        return 255
    return int(255 * ease_out_cubic(min(1.0, progress / 0.18)))
