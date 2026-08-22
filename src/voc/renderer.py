from __future__ import annotations
import shutil, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageDraw
from .animation import motion, text_alpha
from .image_renderer import compose_product_frame, open_rgb
from .models import LoadedProject, TimelineScene
from .text_renderer import draw_text_block
from .timeline import build_timeline
from .visual_director import direction_for


def _resolve_image(project, scene) -> Path:
    if not scene.image:
        raise FileNotFoundError("Scene has no image")
    path = project.product_dir / "images" / scene.image
    if not path.is_file():
        raise FileNotFoundError(f"Scene image not found: {path}")
    return path


def _role(scene) -> str:
    notes = scene.notes or ""
    return notes.split("role=",1)[1].split(";",1)[0].strip() if "role=" in notes else "proof"


def _logo(canvas, project):
    cfg = project.template.get("logo", {})
    fn = cfg.get("file")
    if not fn:
        return
    path = project.root / "assets" / "branding" / fn
    if not path.is_file():
        return
    with Image.open(path) as src:
        logo = src.convert("RGBA")
    w,h = canvas.size
    logo.thumbnail((int(w*.14), int(h*.065)), Image.Resampling.LANCZOS)
    canvas.alpha_composite(logo, ((w-logo.width)//2, int(h*.025)))


def _panel(canvas, box, color, alpha, radius=26):
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(box, radius=radius, fill=tuple(color)+(alpha,))


def _style(direction, *, dark_text=False, size=None):
    return {
        "size": int(size or direction.preferred_size),
        "min_size": 28,
        "color": list((18,18,20) if dark_text else direction.text),
        "stroke_color": [0,0,0],
        "stroke_width": 0,
    }


def render_frame(project: LoadedProject, ts: TimelineScene, frame_no: int) -> Image.Image:
    scene = ts.scene
    local = (frame_no-ts.start_frame) / max(1, ts.end_frame-ts.start_frame-1)
    scale,px,py = motion(scene.animation, local)
    role = _role(scene)
    image_path = _resolve_image(project, scene)
    canvas = compose_product_frame(open_rgb(image_path), (project.config.width, project.config.height), project.template, scale, px, py)
    _logo(canvas, project)
    w,h = canvas.size
    alpha = text_alpha(local, scene.animation)
    fonts = project.root / "assets" / "fonts"
    direction = direction_for(role, image_path)
    left,right = int(w*.08), int(w*.92)

    if role == "cold_open":
        # Strong interruption without the old giant black rectangle.
        veil = Image.new("RGBA", canvas.size, (0,0,0,125))
        canvas.alpha_composite(veil)
        draw_text_block(canvas, scene.text_primary, (left, int(h*.34), right, int(h*.64)), _style(direction, size=70), alpha, fonts)
        _panel(canvas, (int(w*.30), int(h*.67), int(w*.70), int(h*.71)), direction.accent, min(alpha,220), 12)
    elif role == "tension":
        box = (int(w*.10), int(h*.70), int(w*.90), int(h*.80))
        _panel(canvas, box, direction.panel, min(alpha, direction.panel_alpha))
        draw_text_block(canvas, scene.text_primary, (box[0]+18, box[1]+4, box[2]-18, box[3]-4), _style(direction, size=48), alpha, fonts)
    elif role == "reveal":
        box = (int(w*.26), int(h*.12), int(w*.74), int(h*.19))
        _panel(canvas, box, direction.accent, min(alpha,235), 22)
        draw_text_block(canvas, scene.text_primary, (box[0]+12, box[1]+2, box[2]-12, box[3]-2), _style(direction, dark_text=True, size=38), alpha, fonts)
    elif role == "price":
        _panel(canvas, (int(w*.12), int(h*.64), int(w*.88), int(h*.84)), direction.panel, min(alpha,205), 30)
        draw_text_block(canvas, "OFERTA", (left, int(h*.655), right, int(h*.70)), {"size":30,"min_size":24,"color":list(direction.accent),"stroke_width":0}, alpha, fonts)
        draw_text_block(canvas, scene.text_primary, (left, int(h*.70), right, int(h*.82)), _style(direction, size=82), alpha, fonts)
    elif role == "cta":
        box = (int(w*.12), int(h*.69), int(w*.88), int(h*.80))
        _panel(canvas, box, direction.accent, min(alpha,245), 30)
        draw_text_block(canvas, scene.text_primary, (box[0]+15, box[1]+5, box[2]-15, box[3]-5), _style(direction, dark_text=True, size=50), alpha, fonts)
    else:
        # Proof copy is intentionally compact; the product remains the visual hero.
        box = (int(w*.10), int(h*.70), int(w*.90), int(h*.80))
        _panel(canvas, box, direction.panel, min(alpha, direction.panel_alpha), 26)
        draw_text_block(canvas, scene.text_primary, (box[0]+18, box[1]+4, box[2]-18, box[3]-4), _style(direction, size=44), alpha, fonts)
    return canvas.convert("RGB")


def render_silent_video(project: LoadedProject, out_path: Path, ffmpeg_bin="ffmpeg"):
    if shutil.which(ffmpeg_bin) is None:
        raise RuntimeError("ffmpeg not found in PATH")
    timeline = build_timeline(project.script, project.config.fps)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="voc_frames_") as tmp:
        d = Path(tmp)
        for ts in timeline:
            for frame in range(ts.start_frame, ts.end_frame):
                render_frame(project, ts, frame).save(d/f"frame_{frame:07d}.jpg", quality=92, subsampling=0)
        subprocess.run([ffmpeg_bin,"-y","-hide_banner","-loglevel","error","-framerate",str(project.config.fps),"-i",str(d/"frame_%07d.jpg"),"-vf","scale=in_range=pc:out_range=tv,format=yuv420p","-c:v",project.config.video_codec,"-preset",project.config.preset,"-crf",str(project.config.crf),"-pix_fmt",project.config.pixel_format,"-movflags","+faststart",str(out_path)], check=True)
    return timeline
