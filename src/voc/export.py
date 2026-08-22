from __future__ import annotations
import json, shutil, subprocess, tempfile
from pathlib import Path
from .audio import mix_audio
from .models import LoadedProject
from .renderer import render_silent_video


def render_project(project: LoadedProject, out_path: Path, ffmpeg_bin: str = "ffmpeg") -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="voc_render_") as tmp:
        silent = Path(tmp) / "silent.mp4"
        render_silent_video(project, silent, ffmpeg_bin)
        mix_audio(project, silent, out_path, ffmpeg_bin)
    return out_path


def probe_video(path: Path, ffprobe_bin: str = "ffprobe") -> dict:
    if shutil.which(ffprobe_bin) is None:
        raise RuntimeError("ffprobe not found in PATH")
    result = subprocess.run([ffprobe_bin, "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt:format=duration", "-of", "json", str(path)], capture_output=True, text=True, check=True)
    return json.loads(result.stdout)
