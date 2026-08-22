from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from voc.assets_import import download_product_images
from voc.benchmark import write_profile
from voc.creative import generate_creative_scenes
from voc.creative_memory import load_creative_memory, summarize_feedback
from voc.loader import load_project
from voc.narration import synthesize_edge_tts, write_narration_manifest
from voc.retention import audit_script
from voc.sound_design import ensure_default_sfx, generate_music_bed


def _pick_images(product_dir: Path, count: int) -> list[str | None]:
    images_dir = product_dir / "images"
    files = sorted(p.name for p in images_dir.iterdir() if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}) if images_dir.exists() else []
    if not files:
        return [None] * count
    return [files[i % len(files)] for i in range(count)]


def _audio_duration(path: Path) -> float:
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)], check=True, capture_output=True, text=True)
    return float(result.stdout.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare editorial/audio assets for a VOC product")
    parser.add_argument("product_id")
    parser.add_argument("--voice", default="pt-BR-AntonioNeural")
    parser.add_argument("--no-tts", action="store_true")
    parser.add_argument("--no-download", action="store_true")
    args = parser.parse_args()
    project = load_project(ROOT, args.product_id, "preview")
    memory = load_creative_memory(ROOT)
    feedback_summary = summarize_feedback(ROOT)
    benchmark = write_profile(ROOT)

    source_images = project.product.extra.get("source_images", [])
    if source_images and not args.no_download:
        recovered = download_product_images(project.product_dir, [str(url) for url in source_images])
        print(f"Recovered {len(recovered)} product image(s)")

    scenes = generate_creative_scenes(project.product, memory, benchmark)
    images = _pick_images(project.product_dir, len(scenes))
    audio_dir = project.product_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    ensure_default_sfx(ROOT)
    script_scenes = []
    for i, (scene, image) in enumerate(zip(scenes, images), start=1):
        narration_file = f"scene_{i:02d}.mp3"
        narration_path = audio_dir / narration_file
        write_narration_manifest(scene.narration_text, narration_path)
        duration = scene.duration
        if not args.no_tts:
            synthesize_edge_tts(scene.narration_text, narration_path, voice=args.voice, rate="+12%")
            duration = max(duration, _audio_duration(narration_path) + memory.narration_breathing_room_s)
        script_scenes.append({"duration": round(duration, 3), "image": image, "text_primary": scene.text_primary, "text_secondary": None, "narration": narration_file if not args.no_tts else None, "animation": scene.animation, "sfx": scene.sfx, "notes": f"auto-generated ad scene; role={scene.role}; review before publishing", "transition": "cut"})

    duration = sum(float(scene["duration"]) for scene in script_scenes)
    music_name = "voc_original_bed.wav"
    generate_music_bed(ROOT / "assets" / "music" / music_name, duration=duration)
    script = {
        "product_id": project.product.id,
        "template": project.script.template,
        "music": music_name,
        "creative_memory": {
            "preferred_hook_style": memory.preferred_hook_style,
            "hook_max_words": memory.hook_max_words,
            "max_proof_scenes": memory.max_proof_scenes,
            "feedback_reviews": feedback_summary["reviews"],
            "feedback_avg_overall": feedback_summary["avg_overall"],
            "known_rejected_patterns": feedback_summary["rejected_patterns"],
        },
        "benchmark_learning": {
            "sample_count": benchmark.sample_count,
            "confidence": benchmark.confidence,
            "preferred_hook_style": benchmark.preferred_hook_style,
            "product_reveal_target_s": benchmark.product_reveal_target_s,
            "target_duration_s": benchmark.target_duration_s,
            "patterns": list(benchmark.patterns),
        },
        "scenes": script_scenes,
    }
    report = audit_script(script)
    script["creative_audit"] = {"score": report.score, "passed": report.passed, "issues": list(report.issues)}
    (project.product_dir / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {project.product.id}: {len(scenes)} scenes, {duration:.2f}s | retention score={report.score} | feedback reviews={feedback_summary['reviews']} | benchmark samples={benchmark.sample_count}")
    for issue in report.issues:
        print(f"CREATIVE WARNING: {issue}")
    if not report.passed:
        raise SystemExit("Creative retention gate failed; fix script before render")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
