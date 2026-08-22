from __future__ import annotations
import shutil, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageDraw
from .animation import motion, text_alpha
from .image_renderer import compose_product_frame, open_rgb
from .models import LoadedProject, TimelineScene
from .text_renderer import draw_text_block
from .timeline import build_timeline


def _resolve_image(project, scene) -> Path:
    if not scene.image: raise FileNotFoundError("Scene has no image")
    path = project.product_dir / "images" / scene.image
    if not path.is_file(): raise FileNotFoundError(f"Scene image not found: {path}")
    return path


def _role(scene) -> str:
    notes = scene.notes or ""
    return notes.split("role=",1)[1].split(";",1)[0].strip() if "role=" in notes else "proof"


def _logo(canvas, project):
    cfg=project.template.get("logo",{}); fn=cfg.get("file")
    if not fn: return
    path=project.root/"assets/branding"/fn
    if not path.is_file(): return
    with Image.open(path) as src: logo=src.convert("RGBA")
    w,h=canvas.size; logo.thumbnail((int(w*float(cfg.get("max_width_ratio",.16))),int(h*.08)),Image.Resampling.LANCZOS)
    canvas.alpha_composite(logo,((w-logo.width)//2,int(h*float(cfg.get("top_ratio",.025)))))


def _pill(canvas, text, box, style, alpha, fonts):
    draw=ImageDraw.Draw(canvas); fill=tuple(style.get("panel_color",[15,15,15]))+(min(alpha,220),)
    draw.rounded_rectangle(box,radius=28,fill=fill)
    draw_text_block(canvas,text,(box[0]+22,box[1]+8,box[2]-22,box[3]-8),style,alpha,fonts)


def render_frame(project: LoadedProject, ts: TimelineScene, frame_no: int) -> Image.Image:
    scene=ts.scene; local=(frame_no-ts.start_frame)/max(1,ts.end_frame-ts.start_frame-1)
    scale,px,py=motion(scene.animation,local); role=_role(scene)
    canvas=compose_product_frame(open_rgb(_resolve_image(project,scene)),(project.config.width,project.config.height),project.template,scale,px,py)
    _logo(canvas,project); w,h=canvas.size; alpha=text_alpha(local,scene.animation); fonts=project.root/"assets/fonts"
    left,right=int(w*.07),int(w*.93)
    if role=="cold_open":
        # Cold open owns the screen: dark veil + oversized question.
        veil=Image.new("RGBA",canvas.size,(0,0,0,105)); canvas.alpha_composite(veil)
        draw_text_block(canvas,scene.text_primary,(left,int(h*.55),right,int(h*.82)),project.template.get("cold_open_text",{}),alpha,fonts)
    elif role=="tension":
        _pill(canvas,scene.text_primary,(int(w*.08),int(h*.68),int(w*.92),int(h*.80)),project.template.get("tension_text",{}),alpha,fonts)
    elif role=="reveal":
        _pill(canvas,scene.text_primary,(int(w*.20),int(h*.69),int(w*.80),int(h*.78)),project.template.get("reveal_text",{}),alpha,fonts)
    elif role=="price":
        draw_text_block(canvas,"OFERTA DO VÍDEO",(left,int(h*.64),right,int(h*.70)),project.template.get("eyebrow_text",{}),alpha,fonts)
        draw_text_block(canvas,scene.text_primary,(left,int(h*.69),right,int(h*.84)),project.template.get("price_text",{}),alpha,fonts)
    elif role=="cta":
        _pill(canvas,scene.text_primary,(int(w*.09),int(h*.67),int(w*.91),int(h*.81)),project.template.get("cta",{}).get("text_style",{}),alpha,fonts)
    else:
        _pill(canvas,scene.text_primary,(int(w*.08),int(h*.68),int(w*.92),int(h*.81)),project.template.get("text_primary",{}),alpha,fonts)
    return canvas.convert("RGB")


def render_silent_video(project: LoadedProject,out_path: Path,ffmpeg_bin="ffmpeg"):
    if shutil.which(ffmpeg_bin) is None: raise RuntimeError("ffmpeg not found in PATH")
    timeline=build_timeline(project.script,project.config.fps); out_path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="voc_frames_") as tmp:
        d=Path(tmp)
        for ts in timeline:
            for frame in range(ts.start_frame,ts.end_frame): render_frame(project,ts,frame).save(d/f"frame_{frame:07d}.jpg",quality=92,subsampling=0)
        subprocess.run([ffmpeg_bin,"-y","-hide_banner","-loglevel","error","-framerate",str(project.config.fps),"-i",str(d/"frame_%07d.jpg"),"-vf","scale=in_range=pc:out_range=tv,format=yuv420p","-c:v",project.config.video_codec,"-preset",project.config.preset,"-crf",str(project.config.crf),"-pix_fmt",project.config.pixel_format,"-movflags","+faststart",str(out_path)],check=True)
    return timeline
