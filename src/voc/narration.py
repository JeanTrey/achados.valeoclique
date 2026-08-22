from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_VOICE = "pt-BR-AntonioNeural"


def edge_tts_available() -> bool:
    return shutil.which("edge-tts") is not None


def synthesize_edge_tts(
    text: str,
    out_path: Path,
    voice: str = DEFAULT_VOICE,
    rate: str = "+6%",
    volume: str = "+0%",
) -> Path:
    """Synthesize narration with Edge TTS when available.

    The renderer itself does not depend on a cloud TTS provider; this is a
    swappable prototype provider. Generated audio is stored with the product so
    subsequent video renders are reproducible.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "edge-tts",
        "--voice", voice,
        "--rate", rate,
        "--volume", volume,
        "--text", text,
        "--write-media", str(out_path),
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise RuntimeError("edge-tts is not installed; install requirements.txt or provide narration files") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        raise RuntimeError(f"edge-tts failed: {detail}") from exc
    return out_path


def write_narration_manifest(text: str, out_path: Path) -> Path:
    """Always preserve the exact text used for TTS beside the audio asset."""
    txt = out_path.with_suffix(".txt")
    txt.write_text(text.strip() + "\n", encoding="utf-8")
    return txt
