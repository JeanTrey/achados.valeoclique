from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from voc import ValidationError, load_project


def main() -> int:
    parser = argparse.ArgumentParser(description="Vale o Clique Video Engine")
    parser.add_argument("product_id", help="Product folder id, e.g. VOC-001")
    parser.add_argument("--config", default="preview", help="Render config preset")
    parser.add_argument("--validate-only", action="store_true", help="Validate inputs without rendering")
    args = parser.parse_args()

    try:
        project = load_project(ROOT, args.product_id, args.config)
    except (FileNotFoundError, ValueError, ValidationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    duration = sum(scene.duration for scene in project.script.scenes)
    print(
        f"OK {project.product.id}: {len(project.script.scenes)} scene(s), "
        f"{duration:.3f}s, {project.config.width}x{project.config.height}@{project.config.fps}fps, "
        f"template={project.script.template}"
    )
    if not args.validate_only:
        print("Foundation only: rendering is intentionally not implemented yet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
