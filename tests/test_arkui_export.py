"""End-to-end tests for the UIBench-owned ArkUI export adapter."""
from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
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
from uibench.arkui.snapshot import BrowserComputedStyle, BrowserSnapshot

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


def _captured_computed(**overrides: str) -> dict[str, str]:
    computed = BrowserComputedStyle().model_dump(by_alias=True)
    computed.update(overrides)
    return computed


def _browser_snapshot_payload() -> dict[str, object]:
    return {
        "snapshotVersion": 1,
        "viewportWidth": 390,
        "viewportHeight": 844,
        "theme": "light",
        "tokenTheme": "harmonyos",
        "canvasBackgroundColor": "rgb(255, 255, 255)",
        "canvasBackgroundImage": "none",
        "nodes": [
            {
                "nodeId": "page",
                "tag": "main",
                "bbox": [0, 0, 390, 844],
                "visible": True,
                "directParentNodeId": None,
                "isFlexItem": False,
                "computed": _captured_computed(
                    display="block", width="390px", height="844px",
                    backgroundColor="rgb(255, 255, 255)",
                ),
            },
            {
                "nodeId": "page.content",
                "tag": "section",
                "bbox": [0, 0, 390, 160],
                "visible": True,
                "directParentNodeId": "page",
                "isFlexItem": False,
                "computed": _captured_computed(
                    display="flex",
                    flexDirection="column",
                    width="390px",
                    height="160px",
                ),
            },
            {
                "nodeId": "page.title",
                "tag": "p",
                "bbox": [16, 16, 358, 24],
                "visible": True,
                "directParentNodeId": "page.content",
                "isFlexItem": True,
                "computed": _captured_computed(
                    display="block", width="358px", height="24px",
                ),
            },
            {
                "nodeId": "page.submit",
                "tag": "button",
                "bbox": [16, 52, 358, 44],
                "visible": True,
                "directParentNodeId": "page.content",
                "isFlexItem": True,
                "computed": _captured_computed(
                    display="block", width="358px", height="44px",
                ),
            },
        ],
    }


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


def test_exporter_error_can_escape_contextmanager_without_being_replaced() -> None:
    """Exception machinery must be able to assign ``__traceback__``.

    ``contextlib`` restores the traceback when an exception leaves a generator
    context manager.  A frozen dataclass blocks that standard assignment and
    replaces the useful exporter error with ``FrozenInstanceError``.
    """
    @contextmanager
    def passthrough() -> Iterator[None]:
        yield

    with pytest.raises(ArkUiExporterError) as raised:
        with passthrough():
            raise ArkUiExporterError("TEST_ERROR", "expected exporter error")

    assert raised.value.code == "TEST_ERROR"


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


def test_annotated_export_renders_selection_controls_and_tabs() -> None:
    _require_vendored_converter()
    result = export_annotated_html(
        """<!doctype html><html><body>
        <main data-node-id="page" data-component="column">
          <input data-node-id="page.check" data-component="checkbox"
                 type="checkbox" name="consents" value="terms" checked>
          <input data-node-id="page.radio" data-component="radio"
                 type="radio" name="theme" value="dark" checked>
          <button data-node-id="page.button" data-component="button" disabled>保存</button>
          <div data-node-id="page.tabs" data-component="tabs" data-index="1">
            <section data-node-id="page.one" data-component="tab-content"
                     data-tab-bar="概览"></section>
            <section data-node-id="page.two" data-component="tab-content"
                     data-tab-bar="设置"></section>
          </div>
        </main></body></html>""",
        page_name="SelectionPage",
    )

    assert result["quality"]["errors"] == 0
    assert 'Checkbox({ name: "terms", group: "consents" })' in result["arkTs"]
    assert ".select(true)" in result["arkTs"]
    assert 'Radio({ value: "dark", group: "theme" })' in result["arkTs"]
    assert ".checked(true)" in result["arkTs"]
    assert 'Button("保存")' in result["arkTs"]
    assert "Tabs({ index: 1 }) {" in result["arkTs"]
    assert '.tabBar("概览")' in result["arkTs"]
    assert '.tabBar("设置")' in result["arkTs"]
    assert result["arkTs"].count(".enabled(false)") == 1


def test_annotated_export_emits_the_canonical_symbol_resource() -> None:
    """A kebab-case annotation must reach ArkTS in its SDK spelling."""
    _require_vendored_converter()
    result = export_annotated_html(
        """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>Demo</title></head><body>
  <div data-node-id="page" data-component="column">
    <i data-node-id="page.more" data-component="symbol"
       data-lucide="chevron-right" data-symbol="sys.symbol.chevron-right"></i>
  </div>
</body></html>""",
        page_name="SymbolPage",
    )

    assert result["quality"]["errors"] == 0
    assert "sys.symbol.chevron-right" not in result["arkTs"]
    assert "sys.symbol.chevron_right" in result["arkTs"]


def test_annotated_export_wraps_plain_list_entries_in_generated_items() -> None:
    """A settings-style group renders even when entries skip list-item."""
    _require_vendored_converter()
    result = export_annotated_html(
        """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>Demo</title></head><body>
  <section data-node-id="page" data-component="list">
    <div data-node-id="page.header" data-component="row" class="flex flex-row">
      <span data-node-id="page.header.label" data-component="text">支持</span>
    </div>
    <button data-node-id="page.help" data-component="button">帮助中心</button>
  </section>
</body></html>""",
        page_name="ListPage",
    )

    assert result["quality"]["errors"] == 0
    assert any(
        item["code"] == "ARKUI_LIST_CHILD_WRAPPED_AS_ITEM"
        for item in result["diagnostics"]
    )
    ui = result["screenIr"]["ui"]
    assert ui["componentName"] == "List"
    assert [child["componentName"] for child in ui["children"]] == [
        "ListItem", "ListItem",
    ]
    assert "ListItem" in result["arkTs"]
    assert 'Button("帮助中心")' in result["arkTs"]


def _canvas_promotion_snapshot(root_background: str) -> dict[str, object]:
    return {
        "snapshotVersion": 1,
        "viewportWidth": 390,
        "viewportHeight": 844,
        "theme": "light",
        "tokenTheme": "harmonyos",
        "canvasBackgroundColor": "rgb(245, 245, 245)",
        "canvasBackgroundImage": "none",
        "nodes": [
            {
                "nodeId": "page",
                "tag": "div",
                "bbox": [0, 0, 390, 844],
                "visible": True,
                "directParentNodeId": None,
                "isFlexItem": False,
                "computed": _captured_computed(
                    display="flex", flexDirection="column",
                    width="390px", height="844px",
                    backgroundColor=root_background,
                ),
            },
            {
                "nodeId": "page.title",
                "tag": "h1",
                "bbox": [0, 0, 390, 28],
                "visible": True,
                "directParentNodeId": "page",
                "isFlexItem": False,
                "computed": _captured_computed(
                    display="block", width="390px", height="28px",
                ),
            },
        ],
    }


CANVAS_PROMOTION_HTML = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>Demo</title></head>
<body class="dt-bg-canvas">
  <div data-node-id="page" data-component="column" class="flex flex-col min-h-screen">
    <h1 data-node-id="page.title" data-component="text">设置</h1>
  </div>
</body></html>"""


def test_canvas_colour_left_on_body_moves_onto_the_page_root() -> None:
    """ArkUI paints nothing behind the page root, so the canvas moves onto it."""
    _require_vendored_converter()
    result = export_annotated_html(
        CANVAS_PROMOTION_HTML,
        page_name="CanvasPage",
        snapshot=BrowserSnapshot.model_validate(
            _canvas_promotion_snapshot("rgba(0, 0, 0, 0)")
        ),
        require_snapshot=True,
    )

    assert result["quality"]["readiness"] == "ready"
    assert result["screenIr"]["ui"]["styles"]["backgroundColor"] == "#F5F5F5"
    assert '.backgroundColor("#F5F5F5")' in result["arkTs"]


@pytest.mark.parametrize("root_background", [
    "rgba(0, 0, 0, 0)",
    "rgb(245, 245, 245)",
    "rgb(17, 17, 17)",
])
def test_a_page_taller_than_the_viewport_still_exports(root_background: str) -> None:
    """Any scrollable page is taller than the viewport it was captured in."""
    _require_vendored_converter()
    payload = _canvas_promotion_snapshot(root_background)
    payload["nodes"][0]["bbox"] = [0, 0, 390, 1680]  # type: ignore[index]
    payload["nodes"][0]["computed"]["height"] = "1680px"  # type: ignore[index]

    result = export_annotated_html(
        CANVAS_PROMOTION_HTML,
        page_name="TallPage",
        snapshot=BrowserSnapshot.model_validate(payload),
        require_snapshot=True,
    )

    assert result["quality"]["errors"] == 0
    # The page root always follows the ArkUI content area, never capture pixels.
    assert result["screenIr"]["ui"]["styles"]["height"] == "100%"


def test_document_scrolled_page_gains_a_generated_scroll() -> None:
    """A viewport-spanning root taller than the viewport is the browser's
    document scroll; ArkUI clips instead, so the export synthesizes one."""
    _require_vendored_converter()
    payload = _canvas_promotion_snapshot("rgba(0, 0, 0, 0)")
    payload["nodes"][0]["bbox"] = [0, 0, 390, 1680]  # type: ignore[index]
    payload["nodes"][0]["computed"]["height"] = "1680px"  # type: ignore[index]

    result = export_annotated_html(
        CANVAS_PROMOTION_HTML,
        page_name="TallScrollPage",
        snapshot=BrowserSnapshot.model_validate(payload),
        require_snapshot=True,
    )

    assert result["quality"]["readiness"] == "ready"
    assert any(
        item["code"] == "UIBENCH_ARKUI_DOCUMENT_SCROLL_SYNTHESIZED"
        for item in result["diagnostics"]
    )
    ui = result["screenIr"]["ui"]
    assert ui["componentName"] == "Column"
    assert ui["styles"]["height"] == "100%"
    scroll = ui["children"][0]
    assert scroll["componentName"] == "Scroll"
    assert scroll["meta"]["nodeId"] == "page:scroll"
    content = scroll["children"][0]
    assert content["meta"]["nodeId"] == "page:content"
    assert content["children"][0]["componentName"] == "Text"
    assert "Scroll()" in result["arkTs"]


def test_viewport_high_page_keeps_its_root_unwrapped() -> None:
    """A root that exactly spans the viewport does not scroll the document."""
    _require_vendored_converter()
    result = export_annotated_html(
        CANVAS_PROMOTION_HTML,
        page_name="ExactViewportPage",
        snapshot=BrowserSnapshot.model_validate(
            _canvas_promotion_snapshot("rgba(0, 0, 0, 0)")
        ),
        require_snapshot=True,
    )

    ui = result["screenIr"]["ui"]
    assert all(
        child["componentName"] != "Scroll"
        for child in ui.get("children", [])
    )
    assert "UIBENCH_ARKUI_DOCUMENT_SCROLL_SYNTHESIZED" not in {
        item["code"] for item in result["diagnostics"]
    }


def test_canvas_colour_carried_by_the_root_component_exports() -> None:
    _require_vendored_converter()
    result = export_annotated_html(
        CANVAS_PROMOTION_HTML,
        page_name="CanvasPage",
        snapshot=BrowserSnapshot.model_validate(
            _canvas_promotion_snapshot("rgb(245, 245, 245)")
        ),
        require_snapshot=True,
    )

    assert result["quality"]["readiness"] == "ready"
    assert result["screenIr"]["ui"]["styles"]["backgroundColor"] == "#F5F5F5"


def test_opaque_root_colour_of_its_own_is_kept_over_the_canvas() -> None:
    """A root painting its own opaque colour already hides the canvas."""
    _require_vendored_converter()
    result = export_annotated_html(
        CANVAS_PROMOTION_HTML,
        page_name="CanvasPage",
        snapshot=BrowserSnapshot.model_validate(
            _canvas_promotion_snapshot("rgb(17, 17, 17)")
        ),
        require_snapshot=True,
    )

    assert result["screenIr"]["ui"]["styles"]["backgroundColor"] == "#111111"


def test_translucent_root_over_a_canvas_colour_is_refused() -> None:
    with pytest.raises(ArkUiExporterError) as raised:
        export_annotated_html(
            CANVAS_PROMOTION_HTML,
            page_name="CanvasPage",
            snapshot=BrowserSnapshot.model_validate(
                _canvas_promotion_snapshot("rgba(17, 17, 17, 0.4)")
            ),
            require_snapshot=True,
        )

    assert raised.value.code == "UIBENCH_CANVAS_BACKGROUND_ROOT_UNSUPPORTED"
    assert raised.value.details["reason"] == "canvas-root-is-translucent"


def test_annotated_export_can_require_browser_snapshot() -> None:
    with pytest.raises(ArkUiExporterError) as raised:
        export_annotated_html(
            ANNOTATED_HTML,
            page_name="SnapshotRequired",
            require_snapshot=True,
        )

    assert raised.value.code == "UIBENCH_BROWSER_SNAPSHOT_REQUIRED"
    assert raised.value.details == {
        "mode": "annotated",
        "snapshotRequired": True,
    }


def test_required_snapshot_rejects_non_positive_visible_node_bbox() -> None:
    payload = _browser_snapshot_payload()
    payload["nodes"][2]["bbox"] = [16, 16, 0, 24]  # type: ignore[index]

    with pytest.raises(ArkUiExporterError) as raised:
        export_annotated_html(
            ANNOTATED_HTML,
            page_name="InvalidGeometry",
            snapshot=BrowserSnapshot.model_validate(payload),
            require_snapshot=True,
        )

    assert raised.value.to_dict() == {
        "code": "UIBENCH_BROWSER_SNAPSHOT_INCOMPLETE",
        "message": "Browser-computed style snapshot is incomplete",
        "details": {
            "mode": "annotated",
            "snapshotRequired": True,
            "nodeId": "page.title",
            "reason": "visible-node-bbox-not-positive",
            "bbox": [16.0, 16.0, 0.0, 24.0],
        },
    }


def test_required_snapshot_rejects_missing_canvas_background_contract() -> None:
    payload = _browser_snapshot_payload()
    del payload["canvasBackgroundImage"]

    with pytest.raises(ArkUiExporterError) as raised:
        export_annotated_html(
            ANNOTATED_HTML,
            page_name="MissingCanvasContract",
            snapshot=BrowserSnapshot.model_validate(payload),
            require_snapshot=True,
        )

    assert raised.value.to_dict() == {
        "code": "UIBENCH_BROWSER_SNAPSHOT_INCOMPLETE",
        "message": "Browser-computed style snapshot is incomplete",
        "details": {
            "mode": "annotated",
            "snapshotRequired": True,
            "reason": "canvas-background-fields-missing",
            "missingFields": ["canvasBackgroundImage"],
        },
    }


@pytest.mark.parametrize(
    "background_image",
    [
        "linear-gradient(rgb(0, 0, 0), rgb(255, 255, 255))",
        'url("https://images.example.test/canvas.png")',
    ],
)
def test_required_snapshot_blocks_canvas_background_images(
    background_image: str,
) -> None:
    payload = _browser_snapshot_payload()
    payload["canvasBackgroundImage"] = background_image

    with pytest.raises(ArkUiExporterError) as raised:
        export_annotated_html(
            ANNOTATED_HTML,
            page_name="UnsupportedCanvasImage",
            snapshot=BrowserSnapshot.model_validate(payload),
            require_snapshot=True,
        )

    assert raised.value.to_dict() == {
        "code": "UIBENCH_CANVAS_BACKGROUND_IMAGE_UNSUPPORTED",
        "message": (
            "Canvas background images and gradients are not supported by "
            "ArkUI export"
        ),
        "details": {
            "mode": "annotated",
            "snapshotRequired": True,
            "reason": "canvas-background-image-unsupported",
            "backgroundImage": background_image,
        },
    }


def test_required_snapshot_rejects_sparse_computed_style_capture() -> None:
    payload = _browser_snapshot_payload()
    payload["nodes"][2]["computed"] = {  # type: ignore[index]
        "display": "block",
        "width": "358px",
        "height": "24px",
    }

    with pytest.raises(ArkUiExporterError) as raised:
        export_annotated_html(
            ANNOTATED_HTML,
            page_name="SparseComputedCapture",
            snapshot=BrowserSnapshot.model_validate(payload),
            require_snapshot=True,
        )

    expected_missing = [
        str(field.serialization_alias or field.alias or field_name)
        for field_name, field in BrowserComputedStyle.model_fields.items()
        if field_name not in {"display", "width", "height"}
    ]
    assert raised.value.to_dict() == {
        "code": "UIBENCH_BROWSER_SNAPSHOT_INCOMPLETE",
        "message": "Browser-computed style snapshot is incomplete",
        "details": {
            "mode": "annotated",
            "snapshotRequired": True,
            "nodeId": "page.title",
            "reason": "computed-style-capture-fields-missing",
            "missingFields": expected_missing,
        },
    }


def test_supplied_incomplete_snapshot_precedes_screen_ir_metadata_errors() -> None:
    snapshot = BrowserSnapshot.model_validate({
        "snapshotVersion": 1,
        "viewportWidth": 390,
        "viewportHeight": 844,
        "theme": "light",
        "tokenTheme": "harmonyos",
        "nodes": [{
            "nodeId": "page",
            "tag": "main",
            "bbox": [0, 0, 390, 844],
            "visible": True,
            "computed": {},
        }],
    })

    with pytest.raises(ArkUiExporterError) as raised:
        export_annotated_html(
            "<main>missing component metadata</main>",
            page_name="IncompleteBeforeMetadata",
            snapshot=snapshot,
            require_snapshot=True,
        )

    assert raised.value.code == "UIBENCH_BROWSER_SNAPSHOT_INCOMPLETE"


def test_missing_required_snapshot_preserves_metadata_error_precedence() -> None:
    with pytest.raises(ArkUiExporterError) as raised:
        export_annotated_html(
            "<main>missing component metadata</main>",
            page_name="MetadataBeforeMissingSnapshot",
            require_snapshot=True,
        )

    assert raised.value.code == "UIBENCH_SCREEN_IR_BLOCKED"
    assert raised.value.details[0]["code"] == "UIBENCH_ARKUI_METADATA_MISSING"


def test_annotated_export_blocks_planned_components_before_node_bridge() -> None:
    html = """
      <main data-node-id="page" data-component="swiper"></main>
    """
    with pytest.raises(ArkUiExporterError) as raised:
        export_annotated_html(html, page_name="SwiperPage")

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


def test_arkui_export_api_requires_browser_snapshot() -> None:
    with TestClient(app_mod.app) as client:
        response = client.post("/api/arkui/export", json={
            "html": ANNOTATED_HTML,
            "page_name": "ApiPage",
            "mode": "annotated",
        })

    assert response.status_code == 422
    error = response.json()["error"]
    assert error == {
        "code": "UIBENCH_BROWSER_SNAPSHOT_REQUIRED",
        "message": (
            "Annotated HarmonyOS project export requires a browser-computed "
            "style snapshot"
        ),
        "details": {
            "mode": "annotated",
            "snapshotRequired": True,
        },
    }


def test_arkui_export_api_rejects_incomplete_computed_snapshot_as_422() -> None:
    snapshot = _browser_snapshot_payload()
    snapshot["nodes"][3]["computed"] = {}  # type: ignore[index]

    with TestClient(app_mod.app) as client:
        response = client.post("/api/arkui/export", json={
            "html": ANNOTATED_HTML,
            "page_name": "ApiPage",
            "mode": "annotated",
            "snapshot": snapshot,
        })

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "UIBENCH_BROWSER_SNAPSHOT_INCOMPLETE"
    assert error["message"] == "Browser-computed style snapshot is incomplete"
    assert error["details"]["nodeId"] == "page.submit"
    assert error["details"]["reason"] == "computed-style-capture-fields-missing"
    assert error["details"]["missingFields"] == [
        str(field.serialization_alias or field.alias or field_name)
        for field_name, field in BrowserComputedStyle.model_fields.items()
    ]


@pytest.mark.parametrize("field", ["directParentNodeId", "isFlexItem"])
def test_arkui_export_api_requires_node_provenance_fields(field: str) -> None:
    snapshot = _browser_snapshot_payload()
    del snapshot["nodes"][2][field]  # type: ignore[index]

    with TestClient(app_mod.app) as client:
        response = client.post("/api/arkui/export", json={
            "html": ANNOTATED_HTML,
            "page_name": "ApiPage",
            "mode": "annotated",
            "snapshot": snapshot,
        })

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "UIBENCH_BROWSER_SNAPSHOT_INCOMPLETE"
    assert error["details"] == {
        "mode": "annotated",
        "snapshotRequired": True,
        "nodeId": "page.title",
        "reason": "node-capture-fields-missing",
        "missingFields": [field],
    }


def test_arkui_export_api_rejects_modern_canvas_color_until_supported() -> None:
    snapshot = _browser_snapshot_payload()
    snapshot["canvasBackgroundColor"] = "oklch(55% 0.2 30)"

    with TestClient(app_mod.app) as client:
        response = client.post("/api/arkui/export", json={
            "html": ANNOTATED_HTML,
            "page_name": "ApiPage",
            "mode": "annotated",
            "snapshot": snapshot,
        })

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "UIBENCH_CANVAS_BACKGROUND_COLOR_UNSUPPORTED"
    assert error["details"]["backgroundColor"] == "oklch(55% 0.2 30)"


def test_arkui_export_api_rejects_a_short_root_in_its_own_colour() -> None:
    """Two colours are visible at once, which one ArkUI background cannot be."""
    snapshot = _browser_snapshot_payload()
    snapshot["nodes"][0]["bbox"] = [0, 0, 100, 100]  # type: ignore[index]
    snapshot["nodes"][0]["computed"]["width"] = "100px"  # type: ignore[index]
    snapshot["nodes"][0]["computed"]["height"] = "100px"  # type: ignore[index]
    snapshot["nodes"][0]["computed"]["backgroundColor"] = "rgb(17, 17, 17)"  # type: ignore[index]

    with TestClient(app_mod.app) as client:
        response = client.post("/api/arkui/export", json={
            "html": ANNOTATED_HTML,
            "page_name": "ApiPage",
            "mode": "annotated",
            "snapshot": snapshot,
        })

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "UIBENCH_CANVAS_BACKGROUND_ROOT_UNSUPPORTED"
    assert error["details"]["reason"] == "canvas-root-does-not-cover-viewport"
    assert error["details"]["nodeId"] == "page"
    assert error["details"]["bbox"] == [0.0, 0.0, 100.0, 100.0]


def test_arkui_export_api_accepts_a_short_root_painting_the_canvas_colour() -> None:
    """One colour is visible, so the root's extent does not matter."""
    snapshot = _browser_snapshot_payload()
    snapshot["nodes"][0]["bbox"] = [0, 0, 390, 100]  # type: ignore[index]
    snapshot["nodes"][0]["computed"]["height"] = "100px"  # type: ignore[index]

    with TestClient(app_mod.app) as client:
        response = client.post("/api/arkui/export", json={
            "html": ANNOTATED_HTML,
            "page_name": "ApiPage",
            "mode": "annotated",
            "snapshot": snapshot,
        })

    assert response.status_code == 200


def test_arkui_export_api_rejects_addressable_wrapper_above_component_root() -> None:
    snapshot = _browser_snapshot_payload()
    snapshot["nodes"][0]["directParentNodeId"] = "shell"  # type: ignore[index]
    snapshot["nodes"].insert(0, {  # type: ignore[union-attr]
        "nodeId": "shell",
        "tag": "div",
        "bbox": [0, 0, 390, 844],
        "visible": True,
        "directParentNodeId": None,
        "isFlexItem": False,
        "computed": _captured_computed(
            display="block",
            width="390px",
            height="844px",
            backgroundColor="rgb(255, 255, 255)",
        ),
    })

    with TestClient(app_mod.app) as client:
        response = client.post("/api/arkui/export", json={
            "html": ANNOTATED_HTML,
            "page_name": "ApiPage",
            "mode": "annotated",
            "snapshot": snapshot,
        })

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "UIBENCH_CANVAS_BACKGROUND_ROOT_UNSUPPORTED"
    assert error["details"]["reason"] == "canvas-root-has-addressable-wrapper"


def test_arkui_export_api_promotes_canvas_colour_onto_a_transparent_root() -> None:
    """dt-bg-canvas on <body> is the normal way to author a page background."""
    snapshot = _browser_snapshot_payload()
    snapshot["nodes"][0]["computed"]["backgroundColor"] = "rgba(0, 0, 0, 0)"  # type: ignore[index]

    with TestClient(app_mod.app) as client:
        response = client.post("/api/arkui/export", json={
            "html": ANNOTATED_HTML,
            "page_name": "ApiPage",
            "mode": "annotated",
            "snapshot": snapshot,
        })

    assert response.status_code == 200
    assert response.json()["screenIr"]["ui"]["styles"]["backgroundColor"] == "#FFFFFF"


def test_required_snapshot_rejects_a_dark_canvas_behind_a_short_transparent_root() -> None:
    """A transparent root only inherits the canvas colour while spanning it.

    Screen IR promotes the canvas colour onto viewport page roots alone, so a
    100x100 transparent root would export as an unpainted box on the default
    white window: a dark captured page would silently become a white screen.
    """
    payload = _browser_snapshot_payload()
    payload["canvasBackgroundColor"] = "rgb(17, 17, 17)"
    payload["nodes"][0]["bbox"] = [0, 0, 100, 100]  # type: ignore[index]
    payload["nodes"][0]["computed"].update(  # type: ignore[index]
        backgroundColor="rgba(0, 0, 0, 0)", width="100px", height="100px",
    )

    with pytest.raises(ArkUiExporterError) as raised:
        export_annotated_html(
            ANNOTATED_HTML,
            page_name="ShortRootPage",
            snapshot=BrowserSnapshot.model_validate(payload),
            require_snapshot=True,
        )

    assert raised.value.code == "UIBENCH_CANVAS_BACKGROUND_ROOT_UNSUPPORTED"
    assert raised.value.details["reason"] == "canvas-root-does-not-cover-viewport"


def test_required_snapshot_rejects_a_dark_canvas_painted_only_by_a_short_root() -> None:
    """A root painting the canvas colour hides it only where it reaches."""
    payload = _browser_snapshot_payload()
    payload["canvasBackgroundColor"] = "rgb(17, 17, 17)"
    payload["nodes"][0]["bbox"] = [0, 0, 100, 100]  # type: ignore[index]
    payload["nodes"][0]["computed"].update(  # type: ignore[index]
        backgroundColor="rgb(17, 17, 17)", width="100px", height="100px",
    )

    with pytest.raises(ArkUiExporterError) as raised:
        export_annotated_html(
            ANNOTATED_HTML,
            page_name="ShortRootPage",
            snapshot=BrowserSnapshot.model_validate(payload),
            require_snapshot=True,
        )

    assert raised.value.code == "UIBENCH_CANVAS_BACKGROUND_ROOT_UNSUPPORTED"
    assert raised.value.details["reason"] == "canvas-root-does-not-cover-viewport"


def test_required_snapshot_accepts_a_short_transparent_root_on_a_white_canvas() -> None:
    """The generated project's window background reproduces a white canvas."""
    payload = _browser_snapshot_payload()
    payload["nodes"][0]["bbox"] = [0, 0, 390, 100]  # type: ignore[index]
    payload["nodes"][0]["computed"].update(  # type: ignore[index]
        backgroundColor="rgba(0, 0, 0, 0)", width="390px", height="100px",
    )

    result = export_annotated_html(
        ANNOTATED_HTML,
        page_name="ShortRootPage",
        snapshot=BrowserSnapshot.model_validate(payload),
        require_snapshot=True,
    )

    assert result["quality"]["readiness"] == "ready"


def test_dark_canvas_is_promoted_onto_a_spanning_transparent_root() -> None:
    payload = _browser_snapshot_payload()
    payload["canvasBackgroundColor"] = "rgb(17, 17, 17)"
    payload["nodes"][0]["computed"]["backgroundColor"] = "rgba(0, 0, 0, 0)"  # type: ignore[index]

    result = export_annotated_html(
        ANNOTATED_HTML,
        page_name="DarkPage",
        snapshot=BrowserSnapshot.model_validate(payload),
        require_snapshot=True,
    )

    assert result["screenIr"]["ui"]["styles"]["backgroundColor"] == "#111111"


def test_rich_text_keeps_parent_fragments_around_spans_in_order() -> None:
    """``共 <span>3</span> 台`` must not lose the text around the span.

    ArkUI's Text renders either its own content or its Span children, never
    both, so the parent's fragments have to become ordered sibling Spans.
    """
    html = (
        '<main data-node-id="page" data-component="column">'
        '<p data-node-id="page.count" data-component="text">共 <span'
        ' data-node-id="page.count.value" data-component="span">3</span>'
        " 台</p></main>"
    )

    result = export_annotated_html(html, page_name="RichTextPage")

    ark_ts = result["arkTs"]
    assert (
        ark_ts.index('Span("共 ")')
        < ark_ts.index('Span("3")')
        < ark_ts.index('Span(" 台")')
    )
    text_node = result["screenIr"]["ui"]["children"][0]
    assert "content" not in text_node
    assert [child["content"] for child in text_node["children"]] == [
        "共 ", "3", " 台",
    ]


def test_arkui_export_api_rejects_a_translucent_component_root() -> None:
    """A root that lets the canvas show through cannot be flattened."""
    snapshot = _browser_snapshot_payload()
    snapshot["nodes"][0]["computed"]["backgroundColor"] = "rgba(0, 0, 0, 0.5)"  # type: ignore[index]

    with TestClient(app_mod.app) as client:
        response = client.post("/api/arkui/export", json={
            "html": ANNOTATED_HTML,
            "page_name": "ApiPage",
            "mode": "annotated",
            "snapshot": snapshot,
        })

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "UIBENCH_CANVAS_BACKGROUND_ROOT_UNSUPPORTED"
    assert error["details"]["reason"] == "canvas-root-is-translucent"


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


def test_vendored_bridge_renders_native_divider_visual_styles() -> None:
    _require_vendored_converter()
    rendered = run_arkui_bridge({
        "action": "render-screen-ir",
        "screenIr": {
            "schemaVersion": 2,
            "page": {"name": "StyledDivider"},
            "ui": {
                "componentName": "Divider",
                "styles": {
                    "width": "100%",
                    "dividerColor": "#0D000000",
                    "dividerStrokeWidth": 1,
                    "dividerVertical": False,
                },
                "meta": {"nodeId": "divider"},
            },
        },
    })

    assert rendered["validation"]["valid"] is True
    assert '.vertical(false)' in rendered["arkTs"]
    assert '.color("#0D000000")' in rendered["arkTs"]
    assert '.strokeWidth(1)' in rendered["arkTs"]


def test_vendored_bridge_lowers_solid_hr_border_to_native_divider() -> None:
    _require_vendored_converter()
    converted = run_arkui_bridge({
        "action": "convert-html",
        "html": (
            "<style>hr{border:0;border-bottom:1px solid "
            "rgba(0,0,0,.05)}</style><hr>"
        ),
        "options": {"pageName": "StyledDividerHtml"},
    })

    divider = converted["screenIr"]["ui"]["children"][0]
    assert divider["componentName"] == "Divider"
    assert divider["styles"] == {
        "width": "100%",
        "dividerColor": "#0D000000",
        "dividerStrokeWidth": 1,
        "dividerVertical": False,
    }
    assert converted["quality"]["readiness"] == "ready"
    assert converted["diagnostics"] == []
