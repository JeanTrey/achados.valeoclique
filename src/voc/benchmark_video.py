from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


def _run(command: list[str]) -> str:
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return result.stdout + result.stderr


def probe_video(path: Path) -> dict:
    raw = _run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration:stream=index,codec_type,width,height,r_frame_rate",
        "-of", "json", str(path)
    ])
    data = json.loads(raw)
    duration = float(data.get("format", {}).get("duration", 0.0) or 0.0)
    video = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
    has_audio = any(s.get("codec_type") == "audio" for s in data.get("streams", []))
    return {
        "duration_s": round(duration, 3),
        "width": video.get("width"),
        "height": video.get("height"),
        "fps": video.get("r_frame_rate"),
        "has_audio": has_audio,
    }


def detect_cuts(path: Path, threshold: float = 0.32) -> list[float]:
    # ffmpeg emits pts_time for frames whose scene score crosses the threshold.
    output = _run([
        "ffmpeg", "-hide_banner", "-i", str(path),
        "-filter:v", f"select='gt(scene,{threshold})',showinfo",
        "-f", "null", "-"
    ])
    times = [float(x) for x in re.findall(r"pts_time:([0-9.]+)", output)]
    deduped: list[float] = []
    for value in times:
        if not deduped or value - deduped[-1] > 0.12:
            deduped.append(value)
    return deduped


def analyze_video(path: Path) -> dict:
    info = probe_video(path)
    cuts = detect_cuts(path)
    duration = float(info["duration_s"] or 0.0)
    intervals: list[float] = []
    points = [0.0, *cuts, duration]
    for a, b in zip(points, points[1:]):
        if b > a:
            intervals.append(b - a)
    avg_cut = sum(intervals) / len(intervals) if intervals else duration
    return {
        "id": path.stem,
        "source_type": "local_video_analysis",
        **info,
        "cut_count": len(cuts),
        "first_cut_s": round(cuts[0], 3) if cuts else None,
        "avg_shot_duration_s": round(avg_cut, 3) if avg_cut else None,
        "semantic_annotation_required": True,
        "patterns": [],
    }


def analyze_directory(inbox: Path) -> list[dict]:
    videos = sorted(p for p in inbox.iterdir() if p.is_file() and p.suffix.lower() in {".mp4", ".mov", ".m4v", ".webm"}) if inbox.exists() else []
    return [analyze_video(path) for path in videos]
