import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from voc.creative import generate_creative_scenes
from voc.models import ProductClaim, ProductData
from voc.sound_design import generate_cursor_click, generate_music_bed, generate_woosh


def test_creative_attributes_seller_claims_and_does_not_invent():
    product = ProductData(
        id="VOC-T",
        name="Produto Teste",
        features=(ProductClaim("alcance de até 10 metros", "seller_claim"),),
    )
    scenes = generate_creative_scenes(product)
    narration = " ".join(s.narration_text for s in scenes)
    assert "Segundo o anúncio" in narration
    assert "R$" not in narration


def test_procedural_audio_assets_are_valid_wav(tmp_path):
    click = generate_cursor_click(tmp_path / "click.wav")
    woosh = generate_woosh(tmp_path / "woosh.wav")
    music = generate_music_bed(tmp_path / "music.wav", duration=1.2)
    for path in (click, woosh, music):
        assert path.stat().st_size > 1000
        with wave.open(str(path), "rb") as wf:
            assert wf.getnchannels() == 2
            assert wf.getframerate() == 44100
            assert wf.getnframes() > 0
