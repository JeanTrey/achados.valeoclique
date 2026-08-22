from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

DEFAULT_QUERIES = [
    "shopee achadinhos shorts",
    "shopee afiliado produto viral shorts",
    "tiktok shop viral products ad",
    "amazon finds product ad shorts",
    "gadgets viral product shorts",
]


def _run_json(command: list[str]) -> dict:
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def search_entries(query: str, limit: int) -> list[dict]:
    data = _run_json(["yt-dlp", "--flat-playlist", "--dump-single-json", f"ytsearch{limit}:{query}"])
    return [x for x in data.get("entries", []) if isinstance(x, dict)]


def collect_candidates(target: int = 50) -> list[dict]:
    per_query = max(12, target // max(1, len(DEFAULT_QUERIES)) + 4)
    seen: set[str] = set()
    out: list[dict] = []
    for query in DEFAULT_QUERIES:
        for item in search_entries(query, per_query):
            video_id = str(item.get("id") or "")
            url = str(item.get("url") or "")
            if not video_id or video_id in seen:
                continue
            seen.add(video_id)
            out.append({
                "id": video_id,
                "url": url if url.startswith("http") else f"https://www.youtube.com/watch?v={video_id}",
                "title": item.get("title"),
                "query": query,
            })
    return out[:target]


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect public short-form product-ad benchmarks")
    parser.add_argument("--target", type=int, default=50)
    args = parser.parse_args()
    candidates = collect_candidates(args.target)
    out = ROOT / "benchmarks" / "candidate_urls.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "target": args.target,
        "actual": len(candidates),
        "note": "Candidates are not counted as analysed until media is downloaded temporarily and processed by analyze_benchmarks.py.",
        "items": candidates,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Collected {len(candidates)} candidate public videos -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
