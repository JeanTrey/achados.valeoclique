from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from voc.benchmark_video import analyze_video, analyze_directory


def _download_and_analyse(index: int, item: dict, tmp_root: Path) -> dict | None:
    url = str(item.get("url") or "")
    if not url:
        return None
    work = tmp_root / f"w{index:03d}"
    work.mkdir(parents=True, exist_ok=True)
    template = str(work / "media.%(ext)s")
    cmd = [
        "yt-dlp", "--no-playlist", "--quiet", "--no-warnings",
        "--socket-timeout", "20", "--retries", "1",
        "-f", "bv*[height<=360]+ba/b[height<=360]/worst",
        "--merge-output-format", "mp4", "-o", template, url,
    ]
    try:
        subprocess.run(cmd, check=True, timeout=65, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        media = next((p for p in work.iterdir() if p.suffix.lower() in {".mp4", ".webm", ".mkv", ".mov"}), None)
        if media is None:
            return None
        record = analyze_video(media)
    except Exception:
        return None
    record.update({
        "id": str(item.get("id") or record["id"]),
        "source_type": "public_video_analysis",
        "source_url": url,
        "title": item.get("title"),
        "discovery_query": item.get("query"),
        "media_retained": False,
    })
    return record


def _analyse_candidates(max_success: int, workers: int) -> list[dict]:
    path = ROOT / "benchmarks" / "candidate_urls.json"
    if not path.is_file():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    items = [x for x in raw.get("items", []) if isinstance(x, dict)]
    records: list[dict] = []
    with tempfile.TemporaryDirectory(prefix="voc_bench_") as tmp:
        tmp_root = Path(tmp)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(_download_and_analyse, i, item, tmp_root): item for i, item in enumerate(items, start=1)}
            for future in as_completed(futures):
                record = future.result()
                if record:
                    records.append(record)
                    print(f"Benchmark analysed {len(records)}/{max_success}: {record.get('title') or record['id']}")
                if len(records) >= max_success:
                    for pending in futures:
                        pending.cancel()
                    break
    return records[:max_success]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max", type=int, default=50)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    inbox = ROOT / "benchmarks" / "inbox"
    records = analyze_directory(inbox)
    remaining = max(0, args.max - len(records))
    if remaining:
        records.extend(_analyse_candidates(remaining, max(1, args.workers)))
    out = ROOT / "benchmarks" / "generated_records.json"
    out.write_text(json.dumps({
        "analysed_count": len(records),
        "target_count": args.max,
        "records": records,
        "note": "Only actually downloaded-and-processed media counts. Third-party media is temporary and is not committed.",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"ACTUAL benchmark media analysed: {len(records)}/{args.max}")
    return 0 if records else 2


if __name__ == "__main__":
    raise SystemExit(main())
