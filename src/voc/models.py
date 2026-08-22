from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProductClaim:
    text: str
    source_type: str | None = None


@dataclass(frozen=True)
class ProductData:
    id: str
    name: str | None = None
    price: float | None = None
    price_checked_at: str | None = None
    rating: float | None = None
    review_count: int | None = None
    sold_count: int | None = None
    features: tuple[ProductClaim, ...] = ()
    notes: tuple[str, ...] = ()
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Scene:
    duration: float
    image: str | None = None
    text_primary: str | None = None
    text_secondary: str | None = None
    narration: str | None = None
    animation: str | None = None
    sfx: str | None = None
    notes: str | None = None
    transition: str | None = None


@dataclass(frozen=True)
class Script:
    product_id: str
    template: str
    scenes: tuple[Scene, ...]
    music: str | None = None


@dataclass(frozen=True)
class RenderConfig:
    width: int
    height: int
    fps: int
    video_codec: str = "libx264"
    pixel_format: str = "yuv420p"
    audio_codec: str = "aac"
    crf: int = 20
    preset: str = "medium"
    audio_bitrate: str = "192k"


@dataclass(frozen=True)
class TimelineScene:
    index: int
    start: float
    end: float
    start_frame: int
    end_frame: int
    scene: Scene


@dataclass(frozen=True)
class LoadedProject:
    root: Path
    product_dir: Path
    product: ProductData
    script: Script
    template: dict[str, Any]
    config: RenderConfig
