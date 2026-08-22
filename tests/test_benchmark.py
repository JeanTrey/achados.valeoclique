import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from voc.benchmark import build_benchmark_profile


def test_seed_benchmark_profile_is_grounded():
    profile = build_benchmark_profile(ROOT)
    assert profile.sample_count == 12
    assert profile.confidence == 0.24
    assert profile.hook_max_words <= 5
    assert "relatable_problem_first" in profile.patterns
    assert profile.native_content_bias >= 0.8
