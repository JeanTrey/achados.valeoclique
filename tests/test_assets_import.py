from pathlib import Path

import pytest

from voc.assets_import import download_product_images


def test_importer_rejects_untrusted_hosts(tmp_path: Path):
    with pytest.raises(ValueError, match="unsupported product image host"):
        download_product_images(tmp_path, ["https://example.com/product.jpg"])


def test_importer_rejects_non_https(tmp_path: Path):
    with pytest.raises(ValueError, match="unsupported product image host"):
        download_product_images(tmp_path, ["http://down-br.img.susercontent.com/file/example"])
