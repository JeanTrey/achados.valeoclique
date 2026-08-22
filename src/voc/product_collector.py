from __future__ import annotations

import html
import re
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from .assets_import import ALLOWED_HOSTS, download_product_images

IMAGE_ID_RE = re.compile(r"(?:image|image_id|imageId)[\"']?\s*[:=]\s*[\"']([A-Za-z0-9_-]{20,})[\"']", re.I)


def _fetch(url: str) -> tuple[str, str]:
    request = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/124 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.7",
    })
    with urllib.request.urlopen(request, timeout=25) as response:
        final_url = response.geturl()
        body = response.read(4 * 1024 * 1024).decode("utf-8", errors="ignore")
    return final_url, body


def discover_shopee_image_urls(source_url: str, max_images: int = 12) -> tuple[str, list[str]]:
    final_url, body = _fetch(source_url)
    body = html.unescape(body).replace("\\/", "/")
    found: list[str] = []
    for match in re.findall(r"https://[^\"'<> ]+", body):
        parsed = urlparse(match)
        if parsed.hostname in ALLOWED_HOSTS and "/file/" in parsed.path:
            found.append(match.split("?")[0])
    for image_id in IMAGE_ID_RE.findall(body):
        found.append(f"https://down-br.img.susercontent.com/file/{image_id}")
    deduped: list[str] = []
    for url in found:
        if url not in deduped:
            deduped.append(url)
        if len(deduped) >= max_images:
            break
    return final_url, deduped


def recover_product_assets(product_dir: Path, source_urls: list[str], recorded_urls: list[str] | None = None) -> list[str]:
    candidates: list[str] = list(recorded_urls or [])
    for source_url in source_urls:
        try:
            _, discovered = discover_shopee_image_urls(source_url)
            candidates.extend(discovered)
        except Exception:
            continue
    deduped: list[str] = []
    for url in candidates:
        if url not in deduped:
            deduped.append(url)
    downloaded: list[str] = []
    # Gallery HTML can contain stale/preload IDs. One failed image must not kill
    # the entire product import.
    for url in deduped[:16]:
        try:
            names = download_product_images(product_dir, [url])
        except Exception:
            continue
        for name in names:
            if name not in downloaded:
                downloaded.append(name)
        if len(downloaded) >= 12:
            break
    return downloaded
