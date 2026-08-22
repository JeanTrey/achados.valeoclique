from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

ALLOWED_HOSTS = {"down-br.img.susercontent.com", "cf.shopee.com.br", "down-bs-br.img.susercontent.com"}
MAX_IMAGE_BYTES = 15 * 1024 * 1024


def _safe_extension(url: str, content_type: str | None) -> str:
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp"}:
        return suffix
    mapping = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
    return mapping.get((content_type or "").split(";")[0].lower(), ".jpg")


def download_product_images(product_dir: Path, urls: list[str]) -> list[str]:
    """Best-effort recovery of provenance-bearing Shopee image URLs.

    A single stale/broken candidate must never abort the whole creative. Unsupported
    hosts, empty responses, oversized files and network failures are skipped. The
    caller decides whether the surviving asset count is sufficient for production.
    """
    images_dir = product_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    downloaded: list[str] = []
    seen: set[str] = set()
    for index, url in enumerate(urls, start=1):
        if url in seen:
            continue
        seen.add(url)
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
            continue
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 VOC-Video-Engine/0.3"})
            with urllib.request.urlopen(request, timeout=20) as response:
                data = response.read(MAX_IMAGE_BYTES + 1)
                if len(data) > MAX_IMAGE_BYTES:
                    continue
                content_type = response.headers.get("Content-Type")
            if not data:
                continue
            ext = _safe_extension(url, content_type)
            digest = hashlib.sha256(data).hexdigest()[:10]
            name = f"{index:02d}_{digest}{ext}"
            path = images_dir / name
            if not path.exists():
                path.write_bytes(data)
            downloaded.append(name)
        except Exception:
            continue
    return downloaded
