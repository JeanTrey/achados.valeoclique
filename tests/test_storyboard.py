from pathlib import Path

from PIL import Image

from voc.creative import CreativeScene
from voc.creative_plan import build_creative_plan
from voc.models import ProductData
from voc.storyboard import audit_storyboard_plan, render_storyboard


def test_storyboard_plan_requires_human_review(tmp_path: Path):
    product_dir = tmp_path / "products" / "VOC-T"
    images = product_dir / "images"
    images.mkdir(parents=True)
    for i in range(1, 7):
        Image.new("RGB", (900, 900), (30*i, 40+i, 80)).save(images / f"a{i}.jpg")

    scenes = tuple(
        CreativeScene(1.4, text, text, role=role)
        for role, text in [
            ("cold_open", "SEM FIO?"),
            ("tension", "MENOS BAGUNÇA"),
            ("reveal", "CONHEÇA O KIT"),
            ("proof", "2.4 GHZ"),
            ("price", "R$ 79,00"),
            ("cta", "VALE O CLIQUE?"),
        ]
    )
    assets = [f"a{i}.jpg" for i in range(1, 7)]
    plan = build_creative_plan(ProductData(id="VOC-T"), product_dir, scenes, assets)
    report = audit_storyboard_plan(plan)
    assert report.passed_machine_checks is True
    assert report.status == "REQUIRES_HUMAN_REVIEW"
    assert max(scene.preferred_text_size for scene in plan.scenes) <= 62

    out = product_dir / "storyboard"
    frames = render_storyboard(plan, product_dir, out, size=(360, 640))
    assert len(frames) == 6
    assert (out / "contact_sheet.jpg").is_file()
