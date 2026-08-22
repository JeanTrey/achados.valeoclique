from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from voc.asset_director import assign_assets_to_roles, build_asset_pack
from voc.benchmark import write_profile
from voc.creative import generate_creative_scenes
from voc.creative_memory import load_creative_memory
from voc.creative_plan import build_creative_plan
from voc.loader import load_project
from voc.product_collector import recover_product_assets
from voc.storyboard import write_storyboard_bundle


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a storyboard before any VOC video render")
    parser.add_argument("product_id")
    parser.add_argument("--no-download", action="store_true")
    args = parser.parse_args()

    project = load_project(ROOT, args.product_id, "preview")
    memory = load_creative_memory(ROOT)
    benchmark = write_profile(ROOT)

    if not args.no_download:
        source_urls = [str(x) for x in (
            project.product.extra.get("source_url_original"),
            project.product.extra.get("source_url_recovered"),
        ) if x]
        recorded = [str(x) for x in project.product.extra.get("source_images", [])]
        recovered = recover_product_assets(project.product_dir, source_urls, recorded)
        print(f"Collector recovered/discovered {len(recovered)} source image(s)")

    scenes = generate_creative_scenes(project.product, memory, benchmark)
    variants = build_asset_pack(project.product_dir)
    assets = assign_assets_to_roles(variants, [scene.role for scene in scenes])
    plan = build_creative_plan(project.product, project.product_dir, scenes, assets)
    report = write_storyboard_bundle(plan, project.product_dir)

    print(f"Storyboard: {len(plan.scenes)} scene(s); machine_checks={report.passed_machine_checks}; status={report.status}")
    for warning in report.warnings:
        print(f"STORYBOARD WARNING: {warning}")
    for issue in report.issues:
        print(f"STORYBOARD BLOCK: {issue}")
    if not report.passed_machine_checks:
        return 2
    print("Human visual review is mandatory before MP4 render.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
