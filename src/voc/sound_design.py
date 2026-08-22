from __future__ import annotations

import math
import wave
from pathlib import Path

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None


SAMPLE_RATE = 44100


def _require_numpy():
    if np is None:
        raise RuntimeError("numpy is required for procedural audio generation")


def _write_wav(path: Path, audio, sample_rate: int = SAMPLE_RATE) -> None:
    _require_numpy()
    path.parent.mkdir(parents=True, exist_ok=True)
    audio = np.asarray(audio, dtype=np.float64)
    if audio.ndim == 1:
        audio = np.column_stack([audio, audio])
    peak = float(np.max(np.abs(audio))) if audio.size else 1.0
    if peak > 0.98:
        audio = audio * (0.98 / peak)
    pcm = (audio * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())


def generate_cursor_click(path: Path, sample_rate: int = SAMPLE_RATE) -> Path:
    _require_numpy()
    duration = 0.12
    n = int(duration * sample_rate)
    t = np.arange(n) / sample_rate
    envelope = np.exp(-t * 42)
    tone = 0.55 * np.sin(2 * np.pi * 2100 * t) + 0.25 * np.sin(2 * np.pi * 3200 * t)
    impulse = np.zeros(n)
    impulse[: max(1, int(0.002 * sample_rate))] = 0.7
    _write_wav(path, (tone * envelope + impulse * envelope) * 0.38, sample_rate)
    return path


def generate_woosh(path: Path, duration: float = 0.42, seed: int = 17, sample_rate: int = SAMPLE_RATE) -> Path:
    _require_numpy()
    rng = np.random.default_rng(seed)
    n = int(duration * sample_rate)
    t = np.arange(n) / sample_rate
    noise = rng.normal(0, 1, n)
    # simple smoothed noise creates a soft broadband sweep without external assets
    kernel = np.ones(45) / 45
    smooth = np.convolve(noise, kernel, mode="same")
    envelope = np.sin(np.pi * np.clip(t / duration, 0, 1)) ** 1.7
    sweep = np.sin(2 * np.pi * (320 * t + 1500 * (t**2) / max(duration, .001)))
    audio = (0.75 * smooth + 0.25 * sweep) * envelope * 0.36
    _write_wav(path, audio, sample_rate)
    return path


def generate_music_bed(
    path: Path,
    duration: float,
    bpm: int = 104,
    seed: int = 20260822,
    sample_rate: int = SAMPLE_RATE,
) -> Path:
    """Generate an original, deterministic instrumental bed.

    No third-party recording is copied or bundled. The synthesis is deliberately
    simple and low in the mix so narration remains dominant.
    """
    _require_numpy()
    rng = np.random.default_rng(seed)
    n = int(duration * sample_rate)
    t = np.arange(n) / sample_rate
    out = np.zeros(n, dtype=np.float64)

    # Common non-exclusive chord movement in A minor: Am - F - C - G.
    chords = [
        (220.00, 261.63, 329.63),
        (174.61, 220.00, 261.63),
        (261.63, 329.63, 392.00),
        (196.00, 246.94, 293.66),
    ]
    beat = 60.0 / bpm
    bar = beat * 4
    bars = max(1, int(math.ceil(duration / bar)))

    for b in range(bars):
        start = b * bar
        end = min(duration, start + bar)
        mask = (t >= start) & (t < end)
        local = t[mask] - start
        chord = chords[b % len(chords)]
        pad = sum(np.sin(2 * np.pi * f * local) for f in chord) / len(chord)
        pad += 0.18 * sum(np.sin(2 * np.pi * (f / 2) * local) for f in chord) / len(chord)
        attack = np.minimum(local / 0.12, 1.0)
        release = np.minimum((end - (t[mask])) / 0.20, 1.0)
        out[mask] += pad * attack * release * 0.11

    beat_count = int(math.ceil(duration / beat))
    for i in range(beat_count):
        start = i * beat
        idx = int(start * sample_rate)
        length = min(int(0.18 * sample_rate), n - idx)
        if length <= 0:
            continue
        lt = np.arange(length) / sample_rate
        if i % 4 in (0, 2):
            kick = np.sin(2 * np.pi * (74 - 32 * lt) * lt) * np.exp(-lt * 20)
            out[idx:idx+length] += kick * 0.18
        if i % 4 in (1, 3):
            noise = rng.normal(0, 1, length)
            snare = noise * np.exp(-lt * 30)
            out[idx:idx+length] += snare * 0.035

    # Gentle master fade.
    fade_n = min(int(0.35 * sample_rate), n // 3)
    if fade_n:
        out[:fade_n] *= np.linspace(0, 1, fade_n)
        out[-fade_n:] *= np.linspace(1, 0, fade_n)
    _write_wav(path, out, sample_rate)
    return path


def ensure_default_sfx(root: Path) -> dict[str, Path]:
    sfx_dir = root / "assets" / "sfx"
    click = sfx_dir / "cursor_click.wav"
    woosh = sfx_dir / "woosh.wav"
    if not click.exists():
        generate_cursor_click(click)
    if not woosh.exists():
        generate_woosh(woosh)
    return {"cursor_click": click, "woosh": woosh}
