from __future__ import annotations
from typing import Any


class ValidationError(ValueError):
    """Raised when a VOC input file is structurally invalid."""


def _require_dict(data: Any, label: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValidationError(f"{label} must be a JSON object")
    return data


def _opt_string(obj: dict[str, Any], key: str, label: str) -> None:
    value = obj.get(key)
    if value is not None and not isinstance(value, str):
        raise ValidationError(f"{label}.{key} must be a string or null")


def validate_product(data: Any) -> dict[str, Any]:
    product = _require_dict(data, "product")
    if not isinstance(product.get("id"), str) or not product["id"].strip():
        raise ValidationError("product.id must be a non-empty string")
    price = product.get("preco")
    if price is not None and (not isinstance(price, (int, float)) or isinstance(price, bool) or price < 0):
        raise ValidationError("product.preco must be a non-negative number or null")
    return product


def validate_script(data: Any) -> dict[str, Any]:
    script = _require_dict(data, "script")
    for key in ("product_id", "template"):
        if not isinstance(script.get(key), str) or not script[key].strip():
            raise ValidationError(f"script.{key} must be a non-empty string")
    _opt_string(script, "music", "script")
    scenes = script.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        raise ValidationError("script.scenes must be a non-empty array")
    allowed = {"duration", "image", "text_primary", "text_secondary", "narration", "animation", "sfx", "notes", "transition"}
    for index, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            raise ValidationError(f"script.scenes[{index}] must be an object")
        unknown = set(scene) - allowed
        if unknown:
            raise ValidationError(f"script.scenes[{index}] has unsupported keys: {sorted(unknown)}")
        duration = scene.get("duration")
        if not isinstance(duration, (int, float)) or isinstance(duration, bool) or duration <= 0:
            raise ValidationError(f"script.scenes[{index}].duration must be > 0")
        for key in allowed - {"duration"}:
            _opt_string(scene, key, f"script.scenes[{index}]")
    return script


def validate_template(data: Any) -> dict[str, Any]:
    template = _require_dict(data, "template")
    if not isinstance(template.get("name"), str) or not template["name"].strip():
        raise ValidationError("template.name must be a non-empty string")
    return template


def validate_config(data: Any) -> dict[str, Any]:
    config = _require_dict(data, "config")
    for key in ("width", "height", "fps"):
        value = config.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ValidationError(f"config.{key} must be a positive integer")
    return config
