"""Tests for the bounded browser snapshot and CSS-to-Screen-IR mapping."""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

import app as app_mod
from uibench.arkui.exporter import export_annotated_html
from uibench.arkui.snapshot import (
    BrowserNodeSnapshot,
    BrowserSnapshot,
    screen_ir_styles,
)

HTML_TO_ARKUI_DIST = (
    Path(__file__).resolve().parents[1]
    / "node_modules/@local/html-to-arkui/dist/index.js"
)

HTML = """<!doctype html><html><body>
<main data-node-id="page" data-component="scroll">
  <section data-node-id="page.content" data-component="column">
    <p data-node-id="page.title" data-component="text">Hello</p>
    <button data-node-id="page.submit" data-component="button">提交</button>
  </section>
</main>
</body></html>"""


def _node(
    node_id: str,
    tag: str,
    bbox: list[float],
    computed: dict[str, str],
    *,
    visible: bool = True,
) -> dict:
    return {
        "nodeId": node_id,
        "tag": tag,
        "bbox": bbox,
        "visible": visible,
        "resolvedSrc": None,
        "computed": computed,
    }


def _snapshot(*, omit: str | None = None) -> BrowserSnapshot:
    nodes = [
        _node("page", "main", [0, 0, 390, 844], {
            "display": "block",
            "width": "390px",
            "height": "844px",
            "overflowY": "auto",
            "backgroundColor": "rgb(255, 255, 255)",
        }),
        _node("page.content", "section", [0, 0, 390, 160], {
            "display": "flex",
            "flexDirection": "column",
            "width": "390px",
            "height": "160px",
            "rowGap": "12px",
            "paddingTop": "16px",
            "paddingRight": "16px",
            "paddingBottom": "16px",
            "paddingLeft": "16px",
            "justifyContent": "flex-start",
            "alignItems": "flex-start",
        }),
        _node("page.title", "p", [16, 16, 358, 24], {
            "display": "block",
            "width": "358px",
            "height": "24px",
            "color": "rgb(17, 24, 39)",
            "fontSize": "20px",
            "fontWeight": "700",
            "fontFamily": "Arial",
            "lineHeight": "24px",
            "textAlign": "left",
        }),
        _node("page.submit", "button", [16, 52, 358, 44], {
            "display": "block",
            "width": "358px",
            "height": "44px",
            "paddingTop": "10px",
            "paddingRight": "16px",
            "paddingBottom": "10px",
            "paddingLeft": "16px",
            "backgroundColor": "rgb(10, 89, 247)",
            "color": "rgb(255, 255, 255)",
            "fontSize": "16px",
            "fontWeight": "600",
            "fontFamily": "Arial",
            "textAlign": "center",
            "borderTopWidth": "0px",
            "borderRightWidth": "0px",
            "borderBottomWidth": "0px",
            "borderLeftWidth": "0px",
            "borderTopLeftRadius": "8px",
            "borderTopRightRadius": "8px",
            "borderBottomRightRadius": "8px",
            "borderBottomLeftRadius": "8px",
        }),
    ]
    return BrowserSnapshot.model_validate({
        "snapshotVersion": 1,
        "viewportWidth": 390,
        "viewportHeight": 844,
        "theme": "light",
        "tokenTheme": "harmonyos",
        "nodes": [node for node in nodes if node["nodeId"] != omit],
    })


def test_snapshot_rejects_duplicate_ids_and_unknown_css_fields() -> None:
    node = _node("page", "main", [0, 0, 390, 844], {"display": "block"})
    with pytest.raises(ValidationError, match="nodeId values must be unique"):
        BrowserSnapshot.model_validate({
            "snapshotVersion": 1,
            "viewportWidth": 390,
            "viewportHeight": 844,
            "theme": "light",
            "tokenTheme": "harmonyos",
            "nodes": [node, node],
        })

    node["computed"]["cursor"] = "pointer"
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        BrowserSnapshot.model_validate({
            "snapshotVersion": 1,
            "viewportWidth": 390,
            "viewportHeight": 844,
            "theme": "light",
            "tokenTheme": "harmonyos",
            "nodes": [node],
        })

    with pytest.raises(ValidationError, match="bbox size is out of range"):
        BrowserNodeSnapshot.model_validate(
            _node("page", "main", [0, 0, -1, 844], {"display": "block"})
        )


def test_css_snapshot_maps_only_supported_screen_ir_styles() -> None:
    node = BrowserNodeSnapshot.model_validate(_node(
        "page.button", "button", [12, 20, 200, 44], {
            "display": "block",
            "paddingTop": "10px",
            "paddingRight": "16px",
            "paddingBottom": "10px",
            "paddingLeft": "16px",
            "backgroundColor": "rgba(10, 89, 247, 0.5)",
            "color": "rgb(255, 255, 255)",
            "fontSize": "16px",
            "fontWeight": "600",
            "fontFamily": "Arial",
            "lineHeight": "24px",
            "textAlign": "center",
            "borderTopWidth": "1px",
            "borderRightWidth": "1px",
            "borderBottomWidth": "1px",
            "borderLeftWidth": "1px",
            "borderTopColor": "rgb(17, 24, 39)",
            "borderRightColor": "rgb(17, 24, 39)",
            "borderBottomColor": "rgb(17, 24, 39)",
            "borderLeftColor": "rgb(17, 24, 39)",
            "borderTopStyle": "solid",
            "borderRightStyle": "solid",
            "borderBottomStyle": "solid",
            "borderLeftStyle": "solid",
            "borderTopLeftRadius": "8px",
            "borderTopRightRadius": "8px",
            "borderBottomRightRadius": "8px",
            "borderBottomLeftRadius": "8px",
        },
    ))

    styles, lossy = screen_ir_styles("Button", node)

    assert lossy == ("button-line-height",)
    assert styles["width"] == 200
    assert styles["height"] == 44
    assert styles["padding"] == {
        "top": 10, "right": 16, "bottom": 10, "left": 16,
    }
    assert styles["backgroundColor"] == "#800A59F7"
    assert styles["fontColor"] == "#FFFFFF"
    assert styles["fontWeight"] == 600
    assert styles["border"] == {
        "width": 1, "color": "#111827", "style": "Solid",
    }
    assert styles["borderRadius"] == 8
    assert "lineHeight" not in styles
    assert "textAlign" not in styles


@pytest.mark.parametrize(
    ("width_sizing", "single_line_width", "expected_width"),
    [
        ("auto", 27.8125, None),
        ("auto", 20.0, 27.8125),
        ("auto", None, 27.8125),
        ("explicit", 27.8125, 27.8125),
        ("unknown", 27.8125, 27.8125),
    ],
)
def test_text_width_is_omitted_only_when_browser_proves_it_is_intrinsic(
    width_sizing: str,
    single_line_width: float | None,
    expected_width: float | None,
) -> None:
    payload = _node("page.value", "div", [12, 20, 27.8125, 32], {
        "display": "block",
        "paddingLeft": "0px",
        "paddingRight": "0px",
        "borderLeftWidth": "0px",
        "borderRightWidth": "0px",
        "fontSize": "25px",
        "fontWeight": "700",
        "lineHeight": "32px",
        "transform": "none",
    })
    payload["widthSizing"] = width_sizing
    payload["singleLineTextWidth"] = single_line_width
    node = BrowserNodeSnapshot.model_validate(payload)

    styles, _ = screen_ir_styles("Text", node)

    if expected_width is None:
        assert "width" not in styles
    else:
        assert styles["width"] == expected_width
    assert styles["height"] == 32


def test_intrinsic_text_width_accounts_for_padding_and_border() -> None:
    payload = _node("page.badge", "div", [12, 20, 37, 24], {
        "display": "block",
        "paddingLeft": "4px",
        "paddingRight": "4px",
        "borderLeftWidth": "1px",
        "borderRightWidth": "1px",
        "fontSize": "14px",
        "lineHeight": "20px",
        "transform": "none",
    })
    payload["widthSizing"] = "auto"
    payload["singleLineTextWidth"] = 27

    styles, _ = screen_ir_styles(
        "Text", BrowserNodeSnapshot.model_validate(payload)
    )

    assert "width" not in styles


def test_full_snapshot_produces_ready_screen_ir_and_arkts() -> None:
    assert HTML_TO_ARKUI_DIST.is_file()
    result = export_annotated_html(
        HTML,
        page_name="SnapshotPage",
        snapshot=_snapshot(),
    )

    assert result["quality"] == {
        "readiness": "ready",
        "errors": 0,
        "warnings": 0,
        "componentCounts": {
            "Row": 0, "Column": 1, "Stack": 0, "Scroll": 1,
            "Text": 1, "Span": 0, "Image": 0, "SymbolGlyph": 0,
            "Divider": 0, "Button": 1,
        },
    }
    assert result["viewport"]["source"] == "browser-snapshot"
    assert result["snapshot"] == {
        "snapshotVersion": 1,
        "theme": "light",
        "tokenTheme": "harmonyos",
        "nodes": 4,
    }
    root = result["screenIr"]["ui"]
    assert root["meta"]["bbox"] == [0, 0, 390, 844]
    assert root["styles"]["width"] == 390
    assert ".backgroundColor(\"#0A59F7\")" in result["arkTs"]


def test_stack_card_intrinsic_numbers_do_not_become_hard_text_widths() -> None:
    assert HTML_TO_ARKUI_DIST.is_file()
    fixture = Path(__file__).parent / "fixtures/arkui_regression/stack-card"
    snapshot = BrowserSnapshot.model_validate_json(
        (fixture / "browser-snapshot.json").read_text(encoding="utf-8")
    )
    result = export_annotated_html(
        (fixture / "screen.html").read_text(encoding="utf-8"),
        page_name="StackCardPage",
        snapshot=snapshot,
    )

    nodes: dict[str, dict] = {}

    def collect(node: dict) -> None:
        nodes[node["meta"]["nodeId"]] = node
        for child in node.get("children", []):
            collect(child)

    collect(result["screenIr"]["ui"])

    assert "width" not in nodes["page.stats.coverage.value"]["styles"]
    assert "width" not in nodes["page.stats.viewport.value"]["styles"]
    assert nodes["page.hero.title"]["styles"]["width"] == 250
    assert nodes["page.hero.body"]["styles"]["width"] == 250

    arkts = result["arkTs"]
    ten_block = arkts[arkts.index('Text("10")'):arkts.index('Text("首批契约")')]
    viewport_block = arkts[
        arkts.index('Text("390")'):arkts.index('Text("CSS pixels")')
    ]
    assert ".width(" not in ten_block
    assert ".width(" not in viewport_block


def test_missing_snapshot_node_blocks_export() -> None:
    assert HTML_TO_ARKUI_DIST.is_file()
    from uibench.arkui.exporter import ArkUiExporterError

    with pytest.raises(ArkUiExporterError) as raised:
        export_annotated_html(
            HTML,
            page_name="BlockedPage",
            snapshot=_snapshot(omit="page.title"),
        )

    assert raised.value.code == "UIBENCH_SCREEN_IR_BLOCKED"
    assert any(
        diagnostic["code"] == "UIBENCH_BROWSER_SNAPSHOT_NODE_MISSING"
        for diagnostic in raised.value.details
    )


def test_hidden_snapshot_node_and_its_subtree_are_pruned() -> None:
    assert HTML_TO_ARKUI_DIST.is_file()
    html = """<main data-node-id="page" data-component="column">
      <section data-node-id="page.hidden" data-component="column">
        <p data-node-id="page.hidden.text" data-component="text">SECRET</p>
      </section>
      <p data-node-id="page.visible" data-component="text">Visible</p>
    </main>"""
    snapshot = BrowserSnapshot.model_validate({
        "snapshotVersion": 1,
        "viewportWidth": 390,
        "viewportHeight": 844,
        "theme": "light",
        "tokenTheme": "harmonyos",
        "nodes": [
            _node("page", "main", [0, 0, 390, 844], {
                "display": "flex", "flexDirection": "column",
                "alignItems": "flex-start", "justifyContent": "flex-start",
            }),
            _node("page.hidden", "section", [0, 0, 0, 0], {
                "display": "none", "flexDirection": "column",
            }, visible=False),
            # The browser may omit descendants of display:none ancestors. The
            # hidden ancestor is sufficient evidence to prune the whole subtree.
            _node("page.visible", "p", [0, 0, 80, 20], {
                "display": "block", "fontSize": "16px",
            }),
        ],
    })

    result = export_annotated_html(
        html, page_name="PrunedPage", snapshot=snapshot
    )

    assert result["quality"]["readiness"] == "lossy"
    assert "SECRET" not in result["arkTs"]
    assert 'Text("Visible")' in result["arkTs"]
    assert result["screenIr"]["ui"]["children"] == [{
        "componentName": "Text",
        "meta": {
            "nodeId": "page.visible",
            "htmlTag": "p",
            "bbox": [0.0, 0.0, 80.0, 20.0],
        },
        "content": "Visible",
        "styles": {"width": 80.0, "height": 20.0, "fontSize": 16.0},
    }]


def test_hidden_snapshot_root_blocks_export() -> None:
    from uibench.arkui.exporter import ArkUiExporterError

    payload = _snapshot().model_dump(by_alias=True)
    payload["nodes"][0]["visible"] = False
    with pytest.raises(ArkUiExporterError) as raised:
        export_annotated_html(
            HTML,
            page_name="HiddenRoot",
            snapshot=BrowserSnapshot.model_validate(payload),
        )

    assert raised.value.code == "UIBENCH_SCREEN_IR_BLOCKED"
    assert any(
        item["code"] == "UIBENCH_BROWSER_SNAPSHOT_ROOT_NOT_VISIBLE"
        for item in raised.value.details
    )


def test_export_api_accepts_validated_browser_snapshot() -> None:
    assert HTML_TO_ARKUI_DIST.is_file()
    with TestClient(app_mod.app) as client:
        response = client.post("/api/arkui/export", json={
            "html": HTML,
            "page_name": "SnapshotApiPage",
            "mode": "annotated",
            "snapshot": _snapshot().model_dump(by_alias=True),
        })

    assert response.status_code == 200
    payload = response.json()
    assert payload["quality"]["readiness"] == "ready"
    assert payload["viewport"] == {
        "width": 390,
        "height": 844,
        "source": "browser-snapshot",
    }


def test_index_contains_fixed_viewport_snapshot_bridge() -> None:
    assert "function arkuiSnapshotRuntime" in app_mod.INDEX_HTML
    assert "uibench-arkui-snapshot-request" in app_mod.INDEX_HTML
    assert "querySelectorAll('[data-node-id]')" in app_mod.INDEX_HTML
    assert "widthSizing: capturedWidthSizing(element)" in app_mod.INDEX_HTML
    assert "singleLineTextWidth: singleLineTextWidth(element)" in app_mod.INDEX_HTML
    assert "width:390px;height:844px" in app_mod.INDEX_HTML
    assert "mode === 'mobile' && arkuiCapture === true" in app_mod.INDEX_HTML
    assert "snapshot: snapshot" in app_mod.INDEX_HTML
    assert "async function captureAssets()" in app_mod.INDEX_HTML
    assert "contentBase64: bytesToBase64(loaded.bytes)" in app_mod.INDEX_HTML
    assert "credentials: 'omit'" in app_mod.INDEX_HTML
    assert "function downloadBase64" in app_mod.INDEX_HTML
    assert "下载鸿蒙工程" in app_mod.INDEX_HTML
