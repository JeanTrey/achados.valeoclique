import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from voc.loader import load_project
from voc.validators import ValidationError, validate_product, validate_script


def test_voc001_loads_preview_config():
    project = load_project(ROOT, "VOC-001", "preview")
    assert project.product.id == "VOC-001"
    assert project.script.product_id == "VOC-001"
    assert project.script.template == "voc_v1"
    assert project.config.width == 720
    assert project.config.height == 1280
    assert project.config.fps == 30


def test_missing_product_id_is_rejected():
    try:
        validate_product({})
    except ValidationError:
        return
    raise AssertionError("missing product.id must fail")


def test_non_positive_scene_duration_is_rejected():
    bad = {"product_id": "VOC-X", "template": "voc_v1", "scenes": [{"duration": 0}]}
    try:
        validate_script(bad)
    except ValidationError:
        return
    raise AssertionError("duration <= 0 must fail")


def test_cli_validate_only():
    result = subprocess.run(
        [sys.executable, str(ROOT / "render.py"), "VOC-001", "--validate-only"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "720x1280@30fps" in result.stdout
