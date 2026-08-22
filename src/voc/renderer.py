from __future__ import annotations
import shutil, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageDraw
from .animation import motion, text_alpha
from .image_renderer import compose_product_frame, open_rgb
from .models import LoadedProject, TimelineScene
from .text_renderer import draw_text_block
from .timeline import build_timeline


def _resolve_image(project: LoadedProject, scene) -> Path:
    if not scene.image:
        raise FileNotFoundError("Scene has no image")
    path = project.product_dir / "images" / scene.image
    if not path.is_file():
        raise FileNotFoundError(f"Scene image not found: {path}")
    return path


def _branding(canvas: Image.Image, project: LoadedProject) -> None:
    width, height = canvas.size
    template = project.template
    cta = template.get("cta", {})
    cta_h = int(height * float(cta.get("height_ratio", .095)))
    y = height - cta_h
    draw = ImageDraw.Draw(canvas)
    fill = tuple(cta.get("background_color", [255, 210, 0])) + (235,)
    draw.rounded_rectangle((int(width * .05), y - int(height * .035), int(width * .95), height - int(height * .035)), radius=int(width * .035), fill=fill)
    draw_text_block(canvas, cta.get("text", "VALE O CLIQUE?"), (int(width * .09), y - int(height * .03), int(width * .91), height - int(height * .04)), cta.get("text_style", {}), 255, project.root / "assets/fonts")
    logo_cfg = template.get("logo", {})
    logo_file = logo_cfg.get("file")
    if logo_file:
        path = project.root / "assets/branding" / logo_file
        if path.is_file():
            with Image.open(path) as source:
                logo = source.convert("RGBA")
            max_width = int(width * float(logo_cfg.get("max_width_ratio", .22)))
            logo.thumbnail((max_width, int(height * .12)), Image.Resampling.LANCZOS)
            canvas.alpha_composite(logo, ((width - logo.width) // 2, int(height * float(logo_cfg.get("top_ratio", .035)))))


def render_frame(project: LoadedProject, timeline_scene: TimelineScene, frame_no: int) -> Image.Image:
    scene = timeline_scene.scene
    local = (frame_no - timeline_scene.start_frame) / max(1, timeline_scene.end_frame - timeline_scene.start_frame - 1)
    scale, pan_x, pan_y = motion(scene.animation, local)
    canvas = compose_product_frame(open_rgb(_resolve_image(project, scene)), (project.config.width, project.config.height), project.template, scale, pan_x, pan_y)
    _branding(canvas, project)
    safe = project.template.get("safe_area", {})
    width, height = canvas.size
    left = int(width * float(safe.get("left_ratio", .07)))
    right = width - int(width * float(safe.get("right_ratio", .07)))
    alpha = text_alpha(local, scene.animation)
    draw_text_block(canvas, scene.text_primary, (left, int(height * .67), right, int(height * .80)), project.template.get("text_primary", {}), alpha, project.root / "assets/fonts")
    draw_text_block(canvas, scene.text_secondary, (left, int(height * .79), right, int(height * .86)), project.template.get("text_secondary", {}), alpha, project.root / "assets/fonts")
    return canvas.convert("RGB")


def render_silent_video(project: LoadedProject, out_path: Path, ffmpeg_bin: str = "ffmpeg") -> tuple[TimelineScene, ...]:
    if shutil.which(ffmpeg_bin) is None:
        raise RuntimeError("ffmpeg not found in PATH")
    timeline = build_timeline(project.script, project.config.fps)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="voc_frames_") as tmp:
        frame_dir = Path(tmp)
        for timeline_scene in timeline:
            for frame in range(timeline_scene.start_frame, timeline_scene.end_frame):
                render_frame(project, timeline_scene, frame).save(frame_dir / f"frame_{frame:07d}.jpg", quality=92, subsampling=0)
        command = [ffmpeg_bin, "-y", "-hide_banner", "-loglevel", "error", "-framerate", str(project.config.fps), "-i", str(frame_dir / "frame_%07d.jpg"), "-vf", "scale=in_range=pc:out_range=tv,format=yuv420p", "-c:v", project.config.video_codec, "-preset", project.config.preset, "-crf", str(project.config.crf), "-pix_fmt", project.config.pixel_format, "-movflags", "+faststart", str(out_path)]
        subprocess.run(command, check=True)
    return timeline
