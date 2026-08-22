from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from voc.benchmark_video import analyze_video, analyze_directory


def _download(url: str, out_dir: Path, stem: str) -> Path | None:
    template = str(out_dir / f"{stem}.%(ext)s")
    cmd = [
        "yt-dlp", "--no-playlist", "--quiet", "--no-warnings",
        "-f", "bv*[height<=480]+ba/b[height<=480]/worst",
        "--merge-output-format", "mp4", "-o", template, url,
    ]
    try:
        subprocess.run(cmd, check=True, timeout=90)
    except Exception:
        return None
    matches = sorted(out_dir.glob(f"{stem}.*"))
    return next((p for p in matches if p.suffix.lower() in {".mp4", ".webm", ".mkv", ".mov"}), None)


def _analyse_candidates() -> list[dict]:
    path = ROOT / "benchmarks" / "candidate_urls.json"
    if not path.is_file():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    items = [x for x in raw.get("items", []) if isinstance(x, dict)]
    records: list[dict] = []
    with tempfile.TemporaryDirectory(prefix="voc_bench_") as tmp:
        tmpdir = Path(tmp)
        for index, item in enumerate(items, start=1):
            url = str(item.get("url") or "")
            if not url:
                continue
            media = _download(url, tmpdir, f"bench_{index:03d}")
            if media is None:
                continue
            try:
                record = analyze_video(media)
            except Exception:
                continue
            record.update({
                "id": str(item.get("id") or record["id"]),
                "source_type": "public_video_analysis",
                "source_url": url,
                "title": item.get("title"),
                "discovery_query": item.get("query"),
                "media_retained": False,
            })
            records.append(record)
    return records


def main() -> int:
    inbox = ROOT / "benchmarks" / "inbox"
    records = analyze_directory(inbox)
    records.extend(_analyse_candidates())
    out = ROOT / "benchmarks" / "generated_records.json"
    out.write_text(json.dumps({
        "analysed_count": len(records),
        "records": records,
        "note": "Third-party media is downloaded only temporarily. Repository stores extracted structural measurements, not the videos.",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Actually analysed {len(records)} benchmark video(s)")
    print(f"Wrote {out}")
    return 0 if records else 2


if __name__ == "__main__":
    raise SystemExit(main())
