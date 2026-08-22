from __future__ import annotations
import shutil, subprocess
from pathlib import Path
from .models import LoadedProject
from .timeline import build_timeline, total_duration


def mix_audio(project: LoadedProject, silent_video: Path, out_path: Path, ffmpeg_bin: str = "ffmpeg") -> None:
    if shutil.which(ffmpeg_bin) is None:
        raise RuntimeError("ffmpeg not found in PATH")
    timeline = build_timeline(project.script, project.config.fps)
    duration = total_duration(timeline, project.config.fps)
    inputs: list[str] = []
    chains: list[str] = []
    labels: list[str] = []
    input_index = 1
    audio_cfg = project.template.get("audio", {})
    narration_gain = float(audio_cfg.get("narration_gain_db", 0.0))
    music_gain = float(audio_cfg.get("music_gain_db", -22.0))
    sfx_gain = float(audio_cfg.get("sfx_gain_db", -8.0))

    for timeline_scene in timeline:
        scene = timeline_scene.scene
        if scene.narration:
            path = project.product_dir / "audio" / scene.narration
            if path.is_file():
                inputs += ["-i", str(path)]
                delay = round(timeline_scene.start * 1000)
                label = f"n{input_index}"
                chains.append(f"[{input_index}:a]volume={narration_gain}dB,adelay={delay}|{delay}[{label}]")
                labels.append(f"[{label}]")
                input_index += 1
        if scene.sfx:
            path = project.root / "assets/sfx" / scene.sfx
            if path.is_file():
                inputs += ["-i", str(path)]
                delay = round(timeline_scene.start * 1000)
                label = f"s{input_index}"
                chains.append(f"[{input_index}:a]volume={sfx_gain}dB,adelay={delay}|{delay}[{label}]")
                labels.append(f"[{label}]")
                input_index += 1

    if project.script.music:
        path = project.root / "assets/music" / project.script.music
        if path.is_file():
            inputs += ["-stream_loop", "-1", "-i", str(path)]
            label = f"m{input_index}"
            chains.append(f"[{input_index}:a]volume={music_gain}dB,atrim=0:{duration}[{label}]")
            labels.insert(0, f"[{label}]")
            input_index += 1

    click = project.root / "assets/sfx" / str(audio_cfg.get("end_click", "cursor_click.wav"))
    if click.is_file():
        inputs += ["-i", str(click)]
        delay = max(0, round((duration - float(audio_cfg.get("end_click_lead", .22))) * 1000))
        label = f"c{input_index}"
        chains.append(f"[{input_index}:a]volume={sfx_gain}dB,adelay={delay}|{delay}[{label}]")
        labels.append(f"[{label}]")

    if not labels:
        subprocess.run([ffmpeg_bin, "-y", "-hide_banner", "-loglevel", "error", "-i", str(silent_video), "-f", "lavfi", "-t", str(duration), "-i", "anullsrc=r=44100:cl=stereo", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", project.config.audio_codec, "-b:a", project.config.audio_bitrate, "-shortest", "-movflags", "+faststart", str(out_path)], check=True)
        return

    chains.append("".join(labels) + f"amix=inputs={len(labels)}:duration=longest:normalize=0,atrim=0:{duration},aresample=48000[aout]")
    command = [ffmpeg_bin, "-y", "-hide_banner", "-loglevel", "error", "-i", str(silent_video), *inputs, "-filter_complex", ";".join(chains), "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", project.config.audio_codec, "-b:a", project.config.audio_bitrate, "-movflags", "+faststart", "-t", str(duration), str(out_path)]
    subprocess.run(command, check=True)
