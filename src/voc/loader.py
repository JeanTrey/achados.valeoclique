from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from .models import LoadedProject, ProductClaim, ProductData, RenderConfig, Scene, Script
from .validators import validate_config, validate_product, validate_script, validate_template


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_project(project_root: str | Path, product_id: str, config_name: str = "preview") -> LoadedProject:
    root = Path(project_root).resolve()
    product_dir = root / "products" / product_id
    product_raw = validate_product(_read_json(product_dir / "product.json"))
    script_raw = validate_script(_read_json(product_dir / "script.json"))
    if script_raw["product_id"] != product_raw["id"]:
        raise ValueError("script.product_id must match product.id")
    template_raw = validate_template(_read_json(root / "templates" / f"{script_raw['template']}.json"))
    config_raw = validate_config(_read_json(root / "config" / f"{config_name}.json"))

    known = {"id", "nome", "preco", "preco_consultado_em", "avaliacao", "quantidade_avaliacoes", "vendidos", "caracteristicas", "observacoes"}
    claims: list[ProductClaim] = []
    for item in product_raw.get("caracteristicas", []):
        if isinstance(item, str):
            claims.append(ProductClaim(item))
        elif isinstance(item, dict) and isinstance(item.get("texto"), str):
            claims.append(ProductClaim(item["texto"], item.get("source_type") or item.get("fonte")))

    product = ProductData(
        id=product_raw["id"], name=product_raw.get("nome"), price=product_raw.get("preco"),
        price_checked_at=product_raw.get("preco_consultado_em"), rating=product_raw.get("avaliacao"),
        review_count=product_raw.get("quantidade_avaliacoes"), sold_count=product_raw.get("vendidos"),
        features=tuple(claims), notes=tuple(str(x) for x in product_raw.get("observacoes", [])),
        extra={k: v for k, v in product_raw.items() if k not in known},
    )
    scenes = tuple(Scene(**scene) for scene in script_raw["scenes"])
    script = Script(product_id=script_raw["product_id"], template=script_raw["template"], scenes=scenes, music=script_raw.get("music"))
    config = RenderConfig(
        width=config_raw["width"], height=config_raw["height"], fps=config_raw["fps"],
        video_codec=config_raw.get("video_codec", "libx264"), pixel_format=config_raw.get("pixel_format", "yuv420p"),
        audio_codec=config_raw.get("audio_codec", "aac"), crf=int(config_raw.get("crf", 20)),
        preset=str(config_raw.get("preset", "medium")), audio_bitrate=str(config_raw.get("audio_bitrate", "192k")),
    )
    return LoadedProject(root=root, product_dir=product_dir, product=product, script=script, template=template_raw, config=config)
