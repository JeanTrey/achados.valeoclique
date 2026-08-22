from __future__ import annotations
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from voc.export import probe_video, render_project
from voc.loader import load_project
from voc.timeline import build_timeline, total_duration
from voc.validators import ValidationError


def main() -> int:
    parser = argparse.ArgumentParser(description="Vale o Clique Video Engine")
    parser.add_argument("product_id", help="Product folder id, e.g. VOC-001")
    parser.add_argument("--config", default="preview", help="Render config preset")
    parser.add_argument("--validate-only", action="store_true", help="Validate inputs without rendering")
    parser.add_argument("--output", help="Optional output path")
    args = parser.parse_args()

    try:
        project = load_project(ROOT, args.product_id, args.config)
        timeline = build_timeline(project.script, project.config.fps)
        duration = total_duration(timeline, project.config.fps)
        if args.validate_only:
            print(f"OK {project.product.id}: {len(timeline)} scene(s), {duration:.3f}s, {project.config.width}x{project.config.height}@{project.config.fps}fps, template={project.script.template}")
            return 0
        out = Path(args.output) if args.output else ROOT / "output" / f"{project.product.id}.mp4"
        render_project(project, out)
        print(f"Rendered {out}")
        print(probe_video(out))
        return 0
    except (FileNotFoundError, RuntimeError, ValueError, ValidationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
