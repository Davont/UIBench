from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app as app_mod
from uibench.html_package import (
    GeneratedPackageAsset,
    HtmlPackageError,
    build_html_package,
)


def _write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def test_html_package_rewrites_and_includes_referenced_local_assets(tmp_path) -> None:
    assets = tmp_path / "assets"
    gallery = assets / "gallery"
    font = tmp_path / "font.woff2"
    _write(assets / "logo.svg", b"<svg>logo</svg>")
    _write(assets / "background.png", b"background")
    _write(assets / "unused.png", b"unused")
    _write(gallery / "food" / "small.jpg", b"small")
    _write(gallery / "food" / "large.jpg", b"large")
    _write(font, b"font")
    html = """<!DOCTYPE html><html><head>
      <link rel="stylesheet" href="/shared.css?v=1">
      <style>.hero{background:url('/assets/background.png#hero')}</style>
    </head><body>
      <img src="/gallery/food/small.jpg"
           srcset="/gallery/food/small.jpg 1x, /gallery/food/large.jpg 2x">
      <img src="./assets/logo.svg">
      <script>const remote = 'https://example.com/assets/remote.png';</script>
    </body></html>"""

    result = build_html_package(
        html,
        assets_root=assets,
        gallery_root=gallery,
        generated_assets={
            "/shared.css": GeneratedPackageAsset(
                "assets/uibench/shared.css", b"body{}",
            ),
        },
        extra_files={"assets/uibench/fonts/font.woff2": font},
    )

    with zipfile.ZipFile(io.BytesIO(result.archive)) as archive:
        names = set(archive.namelist())
        packaged_html = archive.read("index.html").decode("utf-8")

    assert names == {
        "index.html",
        "assets/background.png",
        "assets/gallery/food/large.jpg",
        "assets/gallery/food/small.jpg",
        "assets/logo.svg",
        "assets/uibench/fonts/font.woff2",
        "assets/uibench/shared.css",
    }
    assert "assets/uibench/shared.css?v=1" in packaged_html
    assert "assets/background.png#hero" in packaged_html
    assert "assets/gallery/food/small.jpg" in packaged_html
    assert "assets/gallery/food/large.jpg" in packaged_html
    assert "assets/logo.svg" in packaged_html
    assert "https://example.com/assets/remote.png" in packaged_html
    assert "unused.png" not in names
    assert result.asset_count == 6

    repeated = build_html_package(
        html,
        assets_root=assets,
        gallery_root=gallery,
        generated_assets={
            "/shared.css": GeneratedPackageAsset(
                "assets/uibench/shared.css", b"body{}",
            ),
        },
        extra_files={"assets/uibench/fonts/font.woff2": font},
    )
    assert repeated.archive == result.archive


@pytest.mark.parametrize(
    ("reference", "code"),
    [
        (
            "/assets/../secret.txt",
            "UIBENCH_HTML_PACKAGE_ASSET_PATH_INVALID",
        ),
        (
            "/assets/missing.png",
            "UIBENCH_HTML_PACKAGE_ASSET_NOT_FOUND",
        ),
    ],
)
def test_html_package_rejects_unsafe_or_missing_assets(
    tmp_path, reference: str, code: str,
) -> None:
    assets = tmp_path / "assets"
    gallery = assets / "gallery"
    assets.mkdir()
    gallery.mkdir()

    with pytest.raises(HtmlPackageError) as raised:
        build_html_package(
            f'<img src="{reference}">',
            assets_root=assets,
            gallery_root=gallery,
            generated_assets={},
        )

    assert raised.value.code == code


def test_html_package_api_returns_double_clickable_zip(monkeypatch, tmp_path) -> None:
    gallery = tmp_path / "gallery"
    _write(gallery / "food" / "meal.jpg", b"meal")
    monkeypatch.setattr(app_mod, "GALLERY_DIR", gallery)
    monkeypatch.setattr(app_mod, "HM_TEXT_FONTS", ())
    monkeypatch.setattr(app_mod, "hm_fonts_css", lambda: "")
    html = """<!DOCTYPE html><html><head></head><body>
      <img src="/gallery/food/meal.jpg" alt="meal">
    </body></html>"""

    with TestClient(app_mod.app) as client:
        response = client.post("/api/html/package", json={
            "html": html,
            "mode": "mobile",
            "theme": "dark",
            "token_theme": "harmonyos",
        })

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    assert response.headers["x-uibench-asset-count"] == "4"
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        names = set(archive.namelist())
        packaged_html = archive.read("index.html").decode("utf-8")

    assert {
        "index.html",
        "assets/gallery/food/meal.jpg",
        "assets/uibench/shared.css",
        "assets/uibench/design-tokens.css",
        "assets/uibench/hm-fonts.css",
    } == names
    assert 'data-theme="dark"' in packaged_html
    assert 'href="assets/uibench/shared.css"' in packaged_html
    assert 'href="assets/uibench/design-tokens.css"' in packaged_html
    assert 'href="assets/uibench/hm-fonts.css"' in packaged_html
    assert 'src="assets/gallery/food/meal.jpg"' in packaged_html
    assert "data-uibench-tailwind-theme" in packaged_html
    assert "window.tailwind.config=" in packaged_html
    assert '"ui-surface":"var(--dt-color-surface)"' in packaged_html


def test_index_offers_html_package_download() -> None:
    html = app_mod.INDEX_HTML

    assert "下载 HTML 包" in html
    assert "requestHtmlPackage(r)" in html
    assert "fetch('/api/html/package'" in html
    assert "tools.append(copy, packageBtn, open)" in html
    assert "downloadBlob(" in html


def test_html_package_includes_builtin_app_icons(monkeypatch) -> None:
    monkeypatch.setattr(app_mod, "HM_TEXT_FONTS", ())
    monkeypatch.setattr(app_mod, "hm_fonts_css", lambda: "")
    html = """<!DOCTYPE html><html><head></head><body>
      <img data-node-id="apps.wechat.icon" src="/assets/app-icons/wechat.png"
           alt="微信图标">
    </body></html>"""

    with TestClient(app_mod.app) as client:
        response = client.post("/api/html/package", json={
            "html": html,
            "mode": "mobile",
            "theme": "light",
            "token_theme": "harmonyos",
        })

    assert response.status_code == 200
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        names = set(archive.namelist())
        packaged_html = archive.read("index.html").decode("utf-8")

    assert "assets/app-icons/wechat.png" in names
    assert 'src="assets/app-icons/wechat.png"' in packaged_html
