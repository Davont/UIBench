"""End-to-end tests for the UIBench-owned ArkUI export adapter."""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app as app_mod
from uibench.arkui.exporter import (
    ArkUiExporterError,
    export_annotated_html,
    export_generic_html,
    run_arkui_bridge,
)
from uibench.arkui.metadata import (
    MAX_COMPONENT_TREE_DEPTH,
    MAX_HTML_TREE_DEPTH,
    find_html_tree_depth_violation,
)

HTML_TO_ARKUI_DIST = (
    Path(__file__).resolve().parents[1]
    / "node_modules/@local/html-to-arkui/dist/index.js"
)

ANNOTATED_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>Demo</title></head>
<body>
  <main data-node-id="page" data-component="scroll">
    <section data-node-id="page.content" data-component="column">
      <p data-node-id="page.title" data-component="text">Hello ArkUI</p>
      <button data-node-id="page.submit" data-component="button">提交</button>
    </section>
  </main>
</body>
</html>"""


def _require_vendored_converter() -> None:
    assert HTML_TO_ARKUI_DIST.is_file(), (
        "vendored html-to-arkui runtime is missing; run "
        "npm ci --ignore-scripts --offline"
    )


def _nested_html(depth: int, *, annotated: bool) -> str:
    if annotated:
        opening = "".join(
            f'<div data-node-id="page.n{i}" data-component="column">'
            for i in range(depth)
        )
    else:
        opening = "<div>" * depth
    return opening + "content" + "</div>" * depth


def _slash_nested_html(depth: int, *, annotated: bool) -> str:
    if annotated:
        return "".join(
            f'<div data-node-id="page.n{i}" data-component="column"/>'
            for i in range(depth)
        ) + "content"
    return "<div/>" * depth + "content"


def _repeated_document_structure_html(tag: str, count: int) -> str:
    repeated = "".join(
        f'<{tag} data-repeat-{index}="{index}">' for index in range(count)
    )
    if tag == "html":
        return (
            "<!doctype html>" + repeated
            + "<head></head><body><main>content</main></body></html>"
        )
    if tag == "head":
        late_heads = "".join(
            f'<head data-repeat-{index}="{index}">' for index in range(1, count)
        )
        return (
            '<!doctype html><html><head data-repeat-0="0"></head>'
            + late_heads
            + "<body><main>content</main></body></html>"
        )
    return (
        "<!doctype html><html><head></head>" + repeated
        + "<main>content</main></body></html>"
    )


def test_annotated_export_renders_canonical_screen_ir() -> None:
    _require_vendored_converter()
    result = export_annotated_html(ANNOTATED_HTML, page_name="Login Page")

    assert result["kind"] == "uibench-arkui-export"
    assert result["mode"] == "annotated"
    assert result["screenIr"]["schemaVersion"] == 2
    assert result["screenIr"]["page"]["name"] == "Login_Page"
    assert result["quality"]["readiness"] == "lossy"
    assert result["quality"]["errors"] == 0
    assert "struct Login_Page" in result["arkTs"]
    assert 'Text("Hello ArkUI")' in result["arkTs"]
    assert 'Button("提交")' in result["arkTs"]


def test_annotated_export_blocks_planned_components_before_node_bridge() -> None:
    html = """
      <main data-node-id="page" data-component="grid"></main>
    """
    with pytest.raises(ArkUiExporterError) as raised:
        export_annotated_html(html, page_name="GridPage")

    assert raised.value.code == "UIBENCH_SCREEN_IR_BLOCKED"
    assert any(
        item["code"] == "ARKUI_COMPONENT_NOT_RENDERER_SUPPORTED"
        for item in raised.value.details
    )


def test_generic_export_keeps_platform_converter_as_fallback() -> None:
    _require_vendored_converter()
    result = export_generic_html(
        """<!doctype html><html><body>
        <main style="display:flex;flex-direction:column;width:390px">
          <h1>Hello</h1>
        </main></body></html>""",
        page_name="LegacyPage",
    )

    assert result["mode"] == "generic"
    assert result["screenIr"]["schemaVersion"] == 2
    assert "struct LegacyPage" in result["arkTs"]
    assert result["quality"]["readiness"] in {"ready", "lossy"}


@pytest.mark.parametrize("mode", ["annotated", "generic"])
def test_export_api_rejects_excessive_html_nesting_as_422(mode: str) -> None:
    html = _nested_html(
        MAX_HTML_TREE_DEPTH + 1,
        annotated=mode == "annotated",
    )

    with TestClient(app_mod.app, raise_server_exceptions=False) as client:
        response = client.post("/api/arkui/export", json={
            "html": html,
            "page_name": "TooDeep",
            "mode": mode,
        })

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "UIBENCH_HTML_TREE_DEPTH_EXCEEDED"
    assert error["details"]["maxDepth"] == MAX_HTML_TREE_DEPTH


@pytest.mark.parametrize("mode", ["annotated", "generic"])
def test_export_api_treats_non_void_slash_tags_as_nested_html(mode: str) -> None:
    html = _slash_nested_html(
        MAX_HTML_TREE_DEPTH + 1,
        annotated=mode == "annotated",
    )

    with TestClient(app_mod.app, raise_server_exceptions=False) as client:
        response = client.post("/api/arkui/export", json={
            "html": html,
            "page_name": "TooDeepSlashTags",
            "mode": mode,
        })

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "UIBENCH_HTML_TREE_DEPTH_EXCEEDED"
    assert error["details"]["maxDepth"] == MAX_HTML_TREE_DEPTH


def test_export_api_rejects_excessive_component_nesting_as_422() -> None:
    html = _slash_nested_html(MAX_COMPONENT_TREE_DEPTH + 1, annotated=True)

    with TestClient(app_mod.app, raise_server_exceptions=False) as client:
        response = client.post("/api/arkui/export", json={
            "html": html,
            "page_name": "TooDeepComponents",
            "mode": "annotated",
        })

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "UIBENCH_SCREEN_IR_BLOCKED"
    assert {
        item["code"] for item in error["details"]
    } >= {
        "ARKUI_COMPONENT_TREE_DEPTH_EXCEEDED",
        "UIBENCH_ARKUI_TREE_DEPTH_EXCEEDED",
    }


@pytest.mark.parametrize("tag", ["br", "img"])
def test_html_depth_tracker_does_not_stack_void_slash_tags(tag: str) -> None:
    html = f"<{tag}/>" * (MAX_HTML_TREE_DEPTH + 1)

    assert find_html_tree_depth_violation(html) is None


def test_html_depth_tracker_honors_rawtext_and_optional_end_tags() -> None:
    rawtext = "<script/>" + "<div/>" * (MAX_HTML_TREE_DEPTH + 1) + "</script>"
    optional_ends = "<ul>" + "<li>item" * (MAX_HTML_TREE_DEPTH + 1)

    assert find_html_tree_depth_violation(rawtext) is None
    assert find_html_tree_depth_violation(optional_ends) is None


@pytest.mark.parametrize("tag", ["html", "head", "body"])
def test_export_api_ignores_repeated_document_structure_tags(tag: str) -> None:
    html = _repeated_document_structure_html(tag, MAX_HTML_TREE_DEPTH + 1)

    assert find_html_tree_depth_violation(html) is None
    with TestClient(app_mod.app, raise_server_exceptions=False) as client:
        response = client.post("/api/arkui/export", json={
            "html": html,
            "page_name": "RepeatedDocumentStructure",
            "mode": "generic",
        })

    assert response.status_code == 200


def test_arkui_export_api_returns_arkts() -> None:
    _require_vendored_converter()
    with TestClient(app_mod.app) as client:
        response = client.post("/api/arkui/export", json={
            "html": ANNOTATED_HTML,
            "page_name": "ApiPage",
            "mode": "annotated",
        })

    assert response.status_code == 200
    payload = response.json()
    assert payload["screenIr"]["schemaVersion"] == 2
    assert "struct ApiPage" in payload["arkTs"]


def test_arkui_export_api_reports_metadata_errors() -> None:
    with TestClient(app_mod.app) as client:
        response = client.post("/api/arkui/export", json={
            "html": "<html><body><main>plain html</main></body></html>",
            "page_name": "BlockedPage",
            "mode": "annotated",
        })

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "UIBENCH_SCREEN_IR_BLOCKED"
    assert payload["error"]["details"][0]["code"] == "UIBENCH_ARKUI_METADATA_MISSING"


def test_vendored_bridge_supports_all_actions_without_sibling_override(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _require_vendored_converter()
    monkeypatch.delenv("HTML_TO_ARKUI_ROOT", raising=False)
    monkeypatch.chdir(tmp_path)

    contract = run_arkui_bridge({"action": "contract"})
    converted = run_arkui_bridge({
        "action": "convert-html",
        "html": "<main style='display:flex;flex-direction:column'>Offline</main>",
        "options": {"pageName": "VendoredPage"},
    })
    rendered = run_arkui_bridge({
        "action": "render-screen-ir",
        "screenIr": converted["screenIr"],
    })

    assert contract["screenIrSchemaVersion"] == 2
    assert {item["name"] for item in contract["components"]} >= {"Column", "Scroll"}
    assert "struct VendoredPage" in converted["arkTs"]
    assert rendered["validation"]["valid"] is True
    assert converted["arkTs"].endswith(rendered["arkTs"])
