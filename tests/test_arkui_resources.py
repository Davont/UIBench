"""Tests for browser-owned ArkUI image resource materialization."""
from __future__ import annotations

import base64
import io
import json
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

import app as app_mod
from uibench.arkui.exporter import export_annotated_html
from uibench.arkui.snapshot import BrowserComputedStyle, BrowserSnapshot

HTML_TO_ARKUI_DIST = (
    Path(__file__).resolve().parents[1]
    / "node_modules/@local/html-to-arkui/dist/index.js"
)

HTML = """<!doctype html><html><body>
<main data-node-id="page" data-component="column">
  <img data-node-id="page.hero" data-component="image"
       src="https://images.example.test/hero.png" alt="Hero">
</main>
</body></html>"""

PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk"
    "+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


def _snapshot(content_base64: str = PNG_BASE64) -> BrowserSnapshot:
    payload = {
        "snapshotVersion": 1,
        "viewportWidth": 390,
        "viewportHeight": 844,
        "theme": "light",
        "tokenTheme": "harmonyos",
        "canvasBackgroundColor": "rgb(255, 255, 255)",
        "canvasBackgroundImage": "none",
        "nodes": [{
            "nodeId": "page",
            "tag": "main",
            "bbox": [0, 0, 390, 844],
            "visible": True,
            "resolvedSrc": None,
            "computed": {
                "display": "flex",
                "flexDirection": "column",
                "width": "390px",
                "height": "844px",
                "rowGap": "0px",
                "justifyContent": "flex-start",
                "alignItems": "flex-start",
                "backgroundColor": "rgb(255, 255, 255)",
                "backgroundImage": "url(\"https://images.example.test/hero.png\")",
            },
        }, {
            "nodeId": "page.hero",
            "tag": "img",
            "bbox": [0, 0, 390, 240],
            "visible": True,
            "resolvedSrc": "https://images.example.test/hero.png",
            "computed": {
                "display": "block",
                "width": "390px",
                "height": "240px",
                "objectFit": "cover",
            },
        }],
        "assets": [{
            "mimeType": "text/plain",
            "contentBase64": content_base64,
            "uses": [{
                "kind": "image",
                "nodeIds": ["page.hero"],
            }, {
                "kind": "background-image",
                "nodeIds": ["page"],
            }],
        }],
    }
    for node in payload["nodes"]:
        computed = BrowserComputedStyle().model_dump(by_alias=True)
        computed.update(node["computed"])
        node["computed"] = computed
    return BrowserSnapshot.model_validate(payload)


def test_snapshot_rejects_invalid_or_ambiguous_asset_references() -> None:
    payload = _snapshot().model_dump(by_alias=True)
    payload["assets"][0]["contentBase64"] = "not-base64!"
    with pytest.raises(ValidationError, match="contentBase64 is invalid"):
        BrowserSnapshot.model_validate(payload)

    payload = _snapshot().model_dump(by_alias=True)
    payload["assets"].append(payload["assets"][0])
    with pytest.raises(ValidationError, match="node/kind references must be unique"):
        BrowserSnapshot.model_validate(payload)

    payload = _snapshot().model_dump(by_alias=True)
    payload["assets"][0]["uses"][0]["nodeIds"] = ["missing"]
    with pytest.raises(ValidationError, match="absent from snapshot nodes"):
        BrowserSnapshot.model_validate(payload)


def test_export_materializes_media_and_complete_harmony_project() -> None:
    assert HTML_TO_ARKUI_DIST.is_file()

    result = export_annotated_html(
        HTML,
        page_name="ResourcePage",
        snapshot=_snapshot(),
    )

    assert result["quality"]["readiness"] == "ready"
    assert result["quality"]["warnings"] == 0
    assert len(result["assets"]["entries"]) == 1
    entry = result["assets"]["entries"][0]
    assert entry["mimeType"] == "image/png"
    assert entry["kinds"] == ["background-image", "image"]
    assert entry["nodeIds"] == ["page", "page.hero"]
    resource = f"$r('app.media.{entry['resourceName']}')"
    assert f"Image({resource})" in result["arkTs"]
    assert f".backgroundImage({resource})" in result["arkTs"]
    assert result["screenIr"]["ui"]["styles"]["backgroundImage"] == entry["assetUri"]

    bundle = result["bundle"]
    assert bundle["kind"] == "uibench-harmonyos-project"
    assert bundle["completeProject"] is True
    assert bundle["model"] == "stageMode"
    assert bundle["targetSdkVersion"] == "6.0.2(22)"
    assert bundle["buildVerification"] == "not-run"
    archive_bytes = base64.b64decode(bundle["contentBase64"], validate=True)
    assert len(archive_bytes) == bundle["byteLength"]
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        assert archive.namelist() == bundle["files"]
        assert archive.read("entry/src/main/ets/pages/ResourcePage.ets").decode() == result["arkTs"]
        assert archive.read(entry["logicalPath"]) == base64.b64decode(PNG_BASE64)
        assert "windowStage.loadContent('pages/ResourcePage'," in archive.read(
            "entry/src/main/ets/entryability/EntryAbility.ets"
        ).decode()
        assert json.loads(archive.read(
            "entry/src/main/resources/base/profile/main_pages.json"
        )) == {"src": ["pages/ResourcePage"]}
        app_config = json.loads(archive.read("AppScope/app.json5"))
        assert app_config["app"]["bundleName"] == bundle["bundleName"]
        module_config = json.loads(archive.read("entry/src/main/module.json5"))
        assert module_config["module"]["mainElement"] == "EntryAbility"
        build_config = json.loads(archive.read("build-profile.json5"))
        assert build_config["app"]["products"][0]["targetSdkVersion"] == "6.0.2(22)"
        export_manifest = json.loads(archive.read("uibench-export.json"))
        assert export_manifest["completeProject"] is True
        assert export_manifest["buildVerification"] == "not-run"
        assert archive.read("AppScope/resources/base/media/app_icon.png").startswith(
            b"\x89PNG\r\n\x1a\n"
        )


def test_unsupported_captured_format_degrades_without_fake_resource() -> None:
    assert HTML_TO_ARKUI_DIST.is_file()
    svg = base64.b64encode(b"<svg xmlns='http://www.w3.org/2000/svg'/>").decode()

    result = export_annotated_html(
        HTML,
        page_name="RejectedResourcePage",
        snapshot=_snapshot(svg),
    )

    assert result["quality"]["readiness"] == "lossy"
    assert result["assets"]["entries"] == []
    assert result["assets"]["rejected"][0]["code"] == "UIBENCH_ASSET_FORMAT_UNSUPPORTED"
    assert 'Image("https://images.example.test/hero.png")' in result["arkTs"]
    assert "$r('app.media." not in result["arkTs"]


def test_export_api_returns_validated_resource_bundle() -> None:
    assert HTML_TO_ARKUI_DIST.is_file()
    with TestClient(app_mod.app) as client:
        response = client.post("/api/arkui/export", json={
            "html": HTML,
            "page_name": "ResourceApiPage",
            "mode": "annotated",
            "snapshot": _snapshot().model_dump(by_alias=True),
        })

    assert response.status_code == 200
    payload = response.json()
    assert payload["bundle"]["filename"] == "ResourceApiPage_HarmonyOS.zip"
    assert payload["bundle"]["mimeType"] == "application/zip"
    assert payload["bundle"]["completeProject"] is True
    assert len(payload["assets"]["entries"]) == 1
