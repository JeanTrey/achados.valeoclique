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
    """Download explicitly recorded product image URLs into products/<id>/images.

    This intentionally does not scrape arbitrary HTML. URLs are provenance-bearing
    inputs and only known Shopee image hosts are accepted for the V0.1 importer.
    """
    images_dir = product_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    downloaded: list[str] = []
    for index, url in enumerate(urls, start=1):
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
            raise ValueError(f"unsupported product image host: {parsed.hostname}")
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 VOC-Video-Engine/0.1"})
        with urllib.request.urlopen(request, timeout=20) as response:
            data = response.read(MAX_IMAGE_BYTES + 1)
            if len(data) > MAX_IMAGE_BYTES:
                raise ValueError("product image exceeds size limit")
            content_type = response.headers.get("Content-Type")
        if not data:
            raise ValueError(f"empty image response: {url}")
        ext = _safe_extension(url, content_type)
        digest = hashlib.sha256(data).hexdigest()[:10]
        name = f"{index:02d}_{digest}{ext}"
        (images_dir / name).write_bytes(data)
        downloaded.append(name)
    return downloaded
