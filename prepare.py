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

from voc.asset_director import assign_assets_to_roles, build_asset_pack
from voc.benchmark import write_profile
from voc.creative import generate_creative_scenes
from voc.creative_memory import load_creative_memory, summarize_feedback
from voc.loader import load_project
from voc.narration import synthesize_edge_tts, write_narration_manifest
from voc.product_collector import recover_product_assets
from voc.retention import audit_script
from voc.sound_design import ensure_default_sfx, generate_music_bed


def _audio_duration(path: Path) -> float:
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)], check=True, capture_output=True, text=True)
    return float(result.stdout.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a product-specific VOC creative")
    parser.add_argument("product_id")
    parser.add_argument("--voice", default="pt-BR-AntonioNeural")
    parser.add_argument("--no-tts", action="store_true")
    parser.add_argument("--no-download", action="store_true")
    args = parser.parse_args()

    project = load_project(ROOT, args.product_id, "preview")
    memory = load_creative_memory(ROOT)
    feedback_summary = summarize_feedback(ROOT)
    benchmark = write_profile(ROOT)

    recovered: list[str] = []
    if not args.no_download:
        source_urls = [str(x) for x in (
            project.product.extra.get("source_url_original"),
            project.product.extra.get("source_url_recovered"),
        ) if x]
        recorded = [str(x) for x in project.product.extra.get("source_images", [])]
        recovered = recover_product_assets(project.product_dir, source_urls, recorded)
        print(f"Recovered/discovered {len(recovered)} product image(s)")

    scenes = generate_creative_scenes(project.product, memory, benchmark)
    variants = build_asset_pack(project.product_dir)
    roles = [scene.role for scene in scenes]
    images = assign_assets_to_roles(variants, roles)
    print(f"Asset Director built {len(variants)} truthful visual variant(s) for {len(scenes)} scene(s)")

    audio_dir = project.product_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    ensure_default_sfx(ROOT)
    script_scenes = []
    for i, (scene, image) in enumerate(zip(scenes, images), start=1):
        narration_file = f"scene_{i:02d}.mp3"
        narration_path = audio_dir / narration_file
        write_narration_manifest(scene.narration_text, narration_path)
        creative_duration = scene.duration
        duration = creative_duration
        if not args.no_tts:
            synthesize_edge_tts(scene.narration_text, narration_path, voice=args.voice, rate="+24%")
            duration = max(creative_duration, _audio_duration(narration_path) + memory.narration_breathing_room_s)
        script_scenes.append({
            "duration": round(duration, 3),
            "creative_duration": round(creative_duration, 3),
            "image": image,
            "text_primary": scene.text_primary,
            "text_secondary": None,
            "narration": narration_file if not args.no_tts else None,
            "animation": scene.animation,
            "sfx": scene.sfx,
            "notes": f"auto-generated ad scene; role={scene.role}; asset_director=v1; review before publishing",
            "transition": "cut"
        })

    duration = sum(float(scene["duration"]) for scene in script_scenes)
    music_name = "voc_original_bed.wav"
    generate_music_bed(ROOT / "assets" / "music" / music_name, duration=duration)
    script = {
        "product_id": project.product.id,
        "template": project.script.template,
        "music": music_name,
        "asset_learning": {"source_images_recovered": len(recovered), "derived_variants": len(variants)},
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
            "reference_count": benchmark.reference_count,
            "confidence": benchmark.confidence,
            "preferred_hook_style": benchmark.preferred_hook_style,
            "product_reveal_target_s": benchmark.product_reveal_target_s,
            "target_duration_s": benchmark.target_duration_s,
            "avg_shot_duration_s": benchmark.avg_shot_duration_s,
            "patterns": list(benchmark.patterns),
        },
        "scenes": script_scenes,
    }
    report = audit_script(script)
    script["creative_audit"] = {"score": report.score, "passed": report.passed, "issues": list(report.issues)}
    (project.product_dir / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {project.product.id}: {len(scenes)} scenes, {duration:.2f}s | retention={report.score} | truly analysed benchmarks={benchmark.sample_count}/50")
    for issue in report.issues:
        print(f"CREATIVE WARNING: {issue}")
    if not report.passed:
        raise SystemExit("Creative retention gate failed; fix script before render")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
