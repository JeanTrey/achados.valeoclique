from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from voc.benchmark_video import analyze_directory


def main() -> int:
    inbox = ROOT / "benchmarks" / "inbox"
    records = analyze_directory(inbox)
    out = ROOT / "benchmarks" / "generated_records.json"
    out.write_text(json.dumps({"records": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Analysed {len(records)} benchmark video(s) from {inbox}")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
