from __future__ import annotations
import json
import math
import shutil
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from voc.export import probe_video, render_project
from voc.loader import load_project
from voc.timeline import build_timeline


def make_project(tmp_path: Path):
    (tmp_path / "products/TST/images").mkdir(parents=True)
    (tmp_path / "products/TST/audio").mkdir(parents=True)
    (tmp_path / "templates").mkdir()
    (tmp_path / "config").mkdir()
    (tmp_path / "assets/branding").mkdir(parents=True)
    (tmp_path / "assets/fonts").mkdir()
    (tmp_path / "assets/sfx").mkdir()
    (tmp_path / "assets/music").mkdir()
    (tmp_path / "output").mkdir()
    Image.new("RGB", (500, 500), (230, 80, 30)).save(tmp_path / "products/TST/images/01.jpg")
    (tmp_path / "products/TST/product.json").write_text(json.dumps({"id": "TST", "nome": "Produto teste"}), encoding="utf-8")
    (tmp_path / "products/TST/script.json").write_text(json.dumps({"product_id": "TST", "template": "voc_v1", "scenes": [{"duration": 0.4, "image": "01.jpg", "text_primary": "TEXTO GRANDE DE TESTE", "animation": "slow_zoom"}]}), encoding="utf-8")
    (tmp_path / "templates/voc_v1.json").write_text(json.dumps({"name": "voc_v1", "background": {"blur": 8, "brightness": .8}, "foreground": {"max_width_ratio": .9, "max_height_ratio": .58}, "cta": {"text": "VALE O CLIQUE?", "text_style": {"size": 26, "min_size": 16}}, "text_primary": {"size": 28, "min_size": 14}, "audio": {}}), encoding="utf-8")
    (tmp_path / "config/preview.json").write_text(json.dumps({"width": 180, "height": 320, "fps": 10, "video_codec": "libx264", "pixel_format": "yuv420p", "audio_codec": "aac", "crf": 30, "preset": "ultrafast", "audio_bitrate": "96k"}), encoding="utf-8")
    return load_project(tmp_path, "TST")


def test_timeline_rounds_to_frames(tmp_path):
    project = make_project(tmp_path)
    timeline = build_timeline(project.script, project.config.fps)
    assert timeline[0].start_frame == 0
    assert timeline[0].end_frame == 4
    assert math.isclose(timeline[0].end, .4)


def test_square_image_render_end_to_end(tmp_path):
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        return
    project = make_project(tmp_path)
    output = tmp_path / "output/TST.mp4"
    render_project(project, output)
    metadata = probe_video(output)
    video = next(stream for stream in metadata["streams"] if stream["codec_type"] == "video")
    audio = next(stream for stream in metadata["streams"] if stream["codec_type"] == "audio")
    assert (video["width"], video["height"]) == (180, 320)
    assert video["codec_name"] == "h264"
    assert video["pix_fmt"] == "yuv420p"
    assert audio["codec_name"] == "aac"
