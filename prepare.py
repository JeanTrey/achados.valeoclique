from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from voc.assets_import import download_product_images
from voc.creative import generate_creative_scenes, total_creative_duration
from voc.loader import load_project
from voc.narration import synthesize_edge_tts, write_narration_manifest
from voc.sound_design import ensure_default_sfx, generate_music_bed


def _pick_images(product_dir: Path, count: int) -> list[str | None]:
    images_dir = product_dir / "images"
    files = sorted(p.name for p in images_dir.iterdir() if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}) if images_dir.exists() else []
    if not files:
        return [None] * count
    return [files[i % len(files)] for i in range(count)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare editorial/audio assets for a VOC product")
    parser.add_argument("product_id")
    parser.add_argument("--voice", default="pt-BR-AntonioNeural")
    parser.add_argument("--no-tts", action="store_true", help="Create narration text manifests but skip TTS")
    parser.add_argument("--no-download", action="store_true", help="Do not recover source_images recorded in product.json")
    args = parser.parse_args()

    project = load_project(ROOT, args.product_id, "preview")
    source_images = project.product.extra.get("source_images", [])
    if source_images and not args.no_download:
        recovered = download_product_images(project.product_dir, [str(url) for url in source_images])
        print(f"Recovered {len(recovered)} product image(s)")

    scenes = generate_creative_scenes(project.product)
    images = _pick_images(project.product_dir, len(scenes))
    audio_dir = project.product_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    ensure_default_sfx(ROOT)

    script_scenes = []
    for i, (scene, image) in enumerate(zip(scenes, images), start=1):
        narration_file = f"scene_{i:02d}.mp3"
        narration_path = audio_dir / narration_file
        write_narration_manifest(scene.narration_text, narration_path)
        if not args.no_tts:
            synthesize_edge_tts(scene.narration_text, narration_path, voice=args.voice)
        script_scenes.append({"duration": scene.duration, "image": image, "text_primary": scene.text_primary, "text_secondary": None, "narration": narration_file if not args.no_tts else None, "animation": scene.animation, "sfx": scene.sfx, "notes": "auto-generated editorial scene; review before publishing", "transition": "cut"})

    duration = total_creative_duration(scenes)
    music_name = "voc_original_bed.wav"
    generate_music_bed(ROOT / "assets" / "music" / music_name, duration=duration)
    script = {"product_id": project.product.id, "template": project.script.template, "music": music_name, "scenes": script_scenes}
    (project.product_dir / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {project.product.id}: {len(scenes)} scenes, {duration:.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
