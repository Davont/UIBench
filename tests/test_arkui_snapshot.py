"""Tests for the bounded browser snapshot and CSS-to-Screen-IR mapping."""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

import app as app_mod
from uibench.arkui.exporter import ArkUiExporterError, export_annotated_html
from uibench.arkui.metadata import (
    analyze_component_metadata,
    repair_arkui_export_html,
)
from uibench.arkui.screen_ir import build_screen_ir
from uibench.arkui.snapshot import (
    BrowserComputedStyle,
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
        "directParentNodeId": None,
        "isFlexItem": False,
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
    parent_by_id = {
        "page.content": ("page", False),
        "page.title": ("page.content", True),
        "page.submit": ("page.content", True),
    }
    for node in nodes:
        parent = parent_by_id.get(node["nodeId"])
        if parent is not None:
            node["directParentNodeId"], node["isFlexItem"] = parent
    for node in nodes:
        computed = BrowserComputedStyle().model_dump(by_alias=True)
        computed.update(node["computed"])
        node["computed"] = computed
    return BrowserSnapshot.model_validate({
        "snapshotVersion": 1,
        "viewportWidth": 390,
        "viewportHeight": 844,
        "theme": "light",
        "tokenTheme": "harmonyos",
        "canvasBackgroundColor": "rgb(255, 255, 255)",
        "canvasBackgroundImage": "none",
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

    styles, lossy = screen_ir_styles(
        "Button", node, button_renders_direct_label=True,
    )

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


def test_single_outer_box_shadow_maps_to_arkui_shadow() -> None:
    node = BrowserNodeSnapshot.model_validate(_node(
        "page.knob", "span", [24, 10, 24, 24], {
            "display": "block",
            "boxShadow": "rgba(31, 35, 41, 0.1) 0px 10px 30px 0px",
        },
    ))

    styles, lossy = screen_ir_styles("Column", node)

    assert styles["shadow"] == {
        "radius": 30,
        "color": "#1A1F2329",
        "offsetX": 0,
        "offsetY": 10,
    }
    assert "box-shadow" not in lossy


@pytest.mark.parametrize("box_shadow", [
    "rgba(0, 0, 0, 0.2) 0px 2px 8px 1px",
    "rgba(0, 0, 0, 0.2) 0px 2px 8px inset",
    "rgba(0, 0, 0, 0.2) 0px 2px 8px, rgb(0, 0, 0) 0px 1px 2px",
])
def test_unrepresentable_box_shadow_shapes_stay_lossy(box_shadow: str) -> None:
    node = BrowserNodeSnapshot.model_validate(_node(
        "page.card", "div", [0, 0, 100, 40], {
            "display": "block",
            "boxShadow": box_shadow,
        },
    ))

    styles, lossy = screen_ir_styles("Column", node)

    assert "shadow" not in styles
    assert "box-shadow" in lossy


def test_absolute_pure_translation_is_baked_into_snapshot_position() -> None:
    node = BrowserNodeSnapshot.model_validate(_node(
        "page.thumb", "div", [72, 18, 28, 28], {
            "display": "block",
            "position": "absolute",
            "transform": "matrix(1, 0, 0, 1, 0, -14)",
        },
    ))

    styles, lossy = screen_ir_styles("Column", node)

    assert styles["position"] == "absolute"
    assert styles["left"] == 72
    assert styles["top"] == 18
    assert "transform" not in lossy


def test_non_translation_transform_stays_lossy() -> None:
    node = BrowserNodeSnapshot.model_validate(_node(
        "page.art", "div", [0, 0, 40, 40], {
            "display": "block",
            "position": "absolute",
            "transform": "matrix(1.1, 0, 0, 1.1, 0, 0)",
        },
    ))

    _, lossy = screen_ir_styles("Column", node)

    assert "transform" in lossy


def test_button_of_component_children_has_no_label_typography_to_lose() -> None:
    """CSS line-height/text-align never styled an icon/row button's children.

    On a flex button whose content is element children, both properties are
    inert in the browser too, so the export loses nothing by dropping them.
    """
    node = BrowserNodeSnapshot.model_validate(_node(
        "page.iconbutton", "button", [0, 0, 44, 44], {
            "display": "flex",
            "flexDirection": "row",
            "lineHeight": "20px",
            "textAlign": "left",
        },
    ))

    _, lossy = screen_ir_styles("Button", node)

    assert lossy == ()


def test_flex_align_items_normal_and_stretch_map_to_start() -> None:
    """Computed ``normal``/``stretch`` place frozen-size children at Start."""
    for align_items in ("normal", "stretch"):
        node = BrowserNodeSnapshot.model_validate(_node(
            "page.row", "div", [0, 0, 358, 56], {
                "display": "flex",
                "flexDirection": "row",
                "justifyContent": "normal",
                "alignItems": align_items,
            },
        ))

        styles, lossy = screen_ir_styles("Row", node)

        assert styles["justifyContent"] == "Start", align_items
        assert styles["alignItems"] == "Start", align_items
        assert lossy == (), align_items


def test_baseline_row_uses_measured_child_offsets_without_loss() -> None:
    html = """<div data-node-id="preview" data-component="row">
      <span data-node-id="preview.small" data-component="text">A</span>
      <span data-node-id="preview.medium" data-component="text">A</span>
      <span data-node-id="preview.large" data-component="text">A</span>
    </div>"""
    raw_nodes = [
        _node("preview", "div", [20, 100, 80, 24], {
            "display": "flex",
            "flexDirection": "row",
            "justifyContent": "flex-start",
            "alignItems": "baseline",
            "paddingTop": "0px",
            "borderTopWidth": "0px",
        }),
        _node("preview.small", "span", [20, 111, 8, 12], {
            "display": "block", "fontSize": "12px", "lineHeight": "12px",
        }),
        _node("preview.medium", "span", [32, 106, 10, 16], {
            "display": "block", "fontSize": "14px", "lineHeight": "16px",
        }),
        _node("preview.large", "span", [46, 101, 12, 20], {
            "display": "block", "fontSize": "16px", "lineHeight": "20px",
        }),
    ]
    for raw in raw_nodes:
        computed = BrowserComputedStyle().model_dump(by_alias=True)
        computed.update(raw["computed"])
        raw["computed"] = computed
        if raw["nodeId"] != "preview":
            raw["directParentNodeId"] = "preview"
            raw["isFlexItem"] = True
    snapshot = BrowserSnapshot.model_validate({
        "snapshotVersion": 1,
        "viewportWidth": 390,
        "viewportHeight": 844,
        "theme": "light",
        "tokenTheme": "harmonyos",
        "nodes": raw_nodes,
    })

    built = build_screen_ir(
        analyze_component_metadata(html),
        page_name="BaselinePreview",
        snapshot=snapshot,
    )

    assert built.screen_ir is not None
    assert built.readiness == "ready"
    assert not any(
        item.code == "UIBENCH_BROWSER_STYLE_LOSSY"
        for item in built.diagnostics
    )
    row = built.screen_ir["ui"]
    assert row["styles"]["alignItems"] == "Start"
    assert [child["styles"]["margin"]["top"] for child in row["children"]] == [
        11, 6, 1,
    ]


def test_single_edge_border_maps_to_per_edge_arkui_forms() -> None:
    """A hairline row separator must not vanish from the export."""
    node = BrowserNodeSnapshot.model_validate(_node(
        "page.row", "div", [0, 0, 358, 56], {
            "display": "flex",
            "flexDirection": "row",
            "borderTopWidth": "0px",
            "borderRightWidth": "0px",
            "borderBottomWidth": "0.5px",
            "borderLeftWidth": "0px",
            "borderBottomColor": "rgba(0, 0, 0, 0.12)",
            "borderBottomStyle": "solid",
        },
    ))

    styles, lossy = screen_ir_styles("Row", node)

    assert lossy == ()
    assert styles["border"] == {
        "width": {"bottom": 0.5},
        "color": "#1F000000",
        "style": "Solid",
    }


def test_mixed_edge_borders_keep_their_per_edge_colors_and_styles() -> None:
    node = BrowserNodeSnapshot.model_validate(_node(
        "page.card", "div", [0, 0, 358, 120], {
            "display": "block",
            "borderTopWidth": "1px",
            "borderTopColor": "rgb(255, 0, 0)",
            "borderTopStyle": "solid",
            "borderRightWidth": "0px",
            "borderBottomWidth": "2px",
            "borderBottomColor": "rgb(0, 0, 255)",
            "borderBottomStyle": "dashed",
            "borderLeftWidth": "0px",
        },
    ))

    styles, lossy = screen_ir_styles("Column", node)

    assert lossy == ()
    assert styles["border"] == {
        "width": {"top": 1, "bottom": 2},
        "color": {"top": "#FF0000", "bottom": "#0000FF"},
        "style": {"top": "Solid", "bottom": "Dashed"},
    }


def test_unsupported_border_style_stays_reported_and_unpainted() -> None:
    node = BrowserNodeSnapshot.model_validate(_node(
        "page.card", "div", [0, 0, 358, 120], {
            "display": "block",
            "borderBottomWidth": "2px",
            "borderBottomColor": "rgb(0, 0, 0)",
            "borderBottomStyle": "double",
            "borderTopWidth": "0px",
            "borderRightWidth": "0px",
            "borderLeftWidth": "0px",
        },
    ))

    styles, lossy = screen_ir_styles("Column", node)

    assert "border" not in styles
    assert lossy == ("border-style:double",)


def test_letter_spacing_maps_on_text_and_span_but_not_button_labels() -> None:
    text = BrowserNodeSnapshot.model_validate(_node(
        "page.label", "p", [0, 0, 120, 16], {
            "display": "block",
            "letterSpacing": "0.6px",
        },
    ))
    button = BrowserNodeSnapshot.model_validate(_node(
        "page.edit", "button", [0, 0, 64, 28], {
            "display": "block",
            "letterSpacing": "0.6px",
        },
    ))

    text_styles, text_lossy = screen_ir_styles("Text", text)
    _, labelled_lossy = screen_ir_styles(
        "Button", button, button_renders_direct_label=True,
    )
    _, icon_lossy = screen_ir_styles("Button", button)

    assert text_styles["letterSpacing"] == 0.6
    assert text_lossy == ()
    assert labelled_lossy == ("letter-spacing",)
    assert icon_lossy == ()


def test_single_line_ellipsis_maps_to_max_lines_and_text_overflow() -> None:
    node = BrowserNodeSnapshot.model_validate(_node(
        "page.name", "p", [0, 0, 180, 20], {
            "display": "block",
            "whiteSpace": "nowrap",
            "textOverflow": "ellipsis",
            "overflowX": "hidden",
        },
    ))

    styles, lossy = screen_ir_styles("Text", node)

    assert styles["maxLines"] == 1
    assert styles["textOverflow"] == "Ellipsis"
    assert lossy == ()


def test_nowrap_without_ellipsis_keeps_the_native_clip_default() -> None:
    node = BrowserNodeSnapshot.model_validate(_node(
        "page.name", "p", [0, 0, 180, 20], {
            "display": "block",
            "whiteSpace": "nowrap",
        },
    ))

    styles, lossy = screen_ir_styles("Text", node)

    assert styles["maxLines"] == 1
    assert "textOverflow" not in styles
    assert lossy == ()


def test_line_clamp_maps_to_max_lines_with_the_browser_ellipsis() -> None:
    node = BrowserNodeSnapshot.model_validate(_node(
        "page.summary", "p", [0, 0, 320, 40], {
            "display": "block",
            "webkitLineClamp": "2",
        },
    ))

    styles, lossy = screen_ir_styles("Text", node)

    assert styles["maxLines"] == 2
    assert styles["textOverflow"] == "Ellipsis"
    assert lossy == ()


def test_line_limits_on_non_text_components_stay_lossy() -> None:
    node = BrowserNodeSnapshot.model_validate(_node(
        "page.row", "div", [0, 0, 358, 56], {
            "display": "flex",
            "flexDirection": "row",
            "whiteSpace": "nowrap",
            "textOverflow": "ellipsis",
        },
    ))

    _, lossy = screen_ir_styles("Row", node)

    assert lossy == ("white-space:nowrap", "text-overflow:ellipsis")


def _snapshot_with_title_computed(**computed: str) -> BrowserSnapshot:
    payload = _snapshot().model_dump(by_alias=True)
    title = next(
        node for node in payload["nodes"] if node["nodeId"] == "page.title"
    )
    title["computed"].update(computed)
    return BrowserSnapshot.model_validate(payload)


def test_text_transform_casing_is_baked_into_the_exported_content() -> None:
    """The browser displayed HELLO; the DOM's ``Hello`` must not resurface."""
    result = export_annotated_html(
        HTML,
        page_name="CasedPage",
        snapshot=_snapshot_with_title_computed(textTransform="uppercase"),
        require_snapshot=True,
    )

    assert result["quality"]["readiness"] == "ready"
    assert 'Text("HELLO")' in result["arkTs"]
    assert not any(
        item["code"] == "UIBENCH_BROWSER_STYLE_LOSSY"
        for item in result["diagnostics"]
    )


def test_text_transform_capitalize_stays_lossy_with_source_content() -> None:
    """CSS titlecasing follows UAX#29 words, which plain casing cannot claim."""
    result = export_annotated_html(
        HTML,
        page_name="CasedPage",
        snapshot=_snapshot_with_title_computed(textTransform="capitalize"),
        require_snapshot=True,
    )

    assert result["quality"]["readiness"] == "lossy"
    assert 'Text("Hello")' in result["arkTs"]
    assert any(
        item["code"] == "UIBENCH_BROWSER_STYLE_LOSSY"
        and "text-transform" in item["message"]
        and item["nodeId"] == "page.title"
        for item in result["diagnostics"]
    )


def test_transparent_button_says_so_instead_of_inheriting_the_theme_fill() -> None:
    """ArkUI Buttons default to a filled theme capsule; HTML buttons do not."""
    node = BrowserNodeSnapshot.model_validate(_node(
        "page.row", "button", [0, 0, 358, 56], {
            "display": "flex",
            "flexDirection": "row",
            "backgroundColor": "rgba(0, 0, 0, 0)",
            "paddingTop": "0px", "paddingRight": "0px",
            "paddingBottom": "0px", "paddingLeft": "0px",
            "borderTopLeftRadius": "0px", "borderTopRightRadius": "0px",
            "borderBottomRightRadius": "0px", "borderBottomLeftRadius": "0px",
        },
    ))

    button, _ = screen_ir_styles("Button", node)
    row, _ = screen_ir_styles("Row", node)

    assert button["backgroundColor"] == "#00000000"
    # ArkUI also supplies Button its own padding and corner radius.
    assert button["padding"] == 0
    assert button["borderRadius"] == 0
    # Every other component starts from the same defaults as the browser.
    assert "backgroundColor" not in row
    assert "padding" not in row
    assert "borderRadius" not in row


def test_modern_css_colors_are_reported_lossy_instead_of_dropped_as_ready() -> None:
    node = BrowserNodeSnapshot.model_validate(_node(
        "page.text", "p", [0, 0, 120, 24], {
            "display": "block",
            "backgroundColor": "oklch(95% 0.02 250)",
            "color": "color(display-p3 1 0 0)",
            "fontSize": "16px",
        },
    ))

    styles, lossy = screen_ir_styles("Text", node)

    assert "backgroundColor" not in styles
    assert "fontColor" not in styles
    assert lossy == (
        "background-color:oklch(95% 0.02 250)",
        "color:color(display-p3 1 0 0)",
    )


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


def test_required_full_snapshot_produces_ready_screen_ir_and_arkts() -> None:
    assert HTML_TO_ARKUI_DIST.is_file()
    result = export_annotated_html(
        HTML,
        page_name="SnapshotPage",
        snapshot=_snapshot(),
        require_snapshot=True,
    )

    assert result["quality"] == {
        "readiness": "ready",
        "errors": 0,
        "warnings": 0,
        "notices": 0,
        "componentCounts": {
            "Row": 0, "Column": 1, "Stack": 0, "Scroll": 1,
            "Text": 1, "Span": 0, "Image": 0, "SymbolGlyph": 0,
            "Divider": 0, "Button": 1, "List": 0, "ListItem": 0,
            "Grid": 0, "GridItem": 0,
            "Toggle": 0, "Slider": 0, "TextInput": 0, "Search": 0,
            "Checkbox": 0, "Radio": 0, "Tabs": 0, "TabContent": 0,
        },
    }
    assert result["viewport"]["source"] == "browser-snapshot"
    assert result["snapshot"] == {
        "snapshotVersion": 1,
        "theme": "light",
        "tokenTheme": "harmonyos",
        "canvasBackgroundColor": "rgb(255, 255, 255)",
        "canvasBackgroundImage": "none",
        "nodes": 4,
    }
    root = result["screenIr"]["ui"]
    assert root["meta"]["bbox"] == [0, 0, 390, 844]
    assert root["styles"]["width"] == "100%"
    assert root["styles"]["height"] == "100%"
    assert '.width("100%")' in result["arkTs"]
    assert '.height("100%")' in result["arkTs"]
    assert ".backgroundColor(\"#0A59F7\")" in result["arkTs"]


def test_native_form_control_snapshot_exports_native_arkts() -> None:
    html = """<!doctype html><html><body>
    <main data-node-id="page" data-component="column" class="flex flex-col">
      <input data-node-id="page.toggle" data-component="toggle"
             type="checkbox" checked disabled>
      <input data-node-id="page.slider" data-component="slider"
             type="range" value="42.5" min="0" max="100" step="0.5">
      <input data-node-id="page.name" data-component="text-input"
             type="text" value="Ada" placeholder="姓名" readonly>
      <input data-node-id="page.search" data-component="search"
             type="search" value="ArkUI" placeholder="搜索" disabled>
    </main></body></html>"""
    raw_nodes = [
        _node("page", "main", [0, 0, 390, 844], {
            "display": "flex", "flexDirection": "column",
            "width": "390px", "height": "844px",
            "justifyContent": "flex-start", "alignItems": "stretch",
            "backgroundColor": "rgb(255, 255, 255)",
        }),
        _node("page.toggle", "input", [326, 20, 48, 28], {
            "display": "block", "width": "48px", "height": "28px",
        }),
        _node("page.slider", "input", [16, 68, 358, 28], {
            "display": "block", "width": "358px", "height": "28px",
        }),
        _node("page.name", "input", [16, 116, 358, 44], {
            "display": "block", "width": "358px", "height": "44px",
            "paddingTop": "10px", "paddingRight": "12px",
            "paddingBottom": "10px", "paddingLeft": "12px",
            "backgroundColor": "rgb(245, 247, 250)",
            "color": "rgb(24, 36, 49)", "fontSize": "16px",
            "fontWeight": "400", "fontFamily": "HarmonyOS Sans",
            "borderTopWidth": "0px", "borderRightWidth": "0px",
            "borderBottomWidth": "0px", "borderLeftWidth": "0px",
            "borderTopLeftRadius": "8px", "borderTopRightRadius": "8px",
            "borderBottomRightRadius": "8px", "borderBottomLeftRadius": "8px",
        }),
        _node("page.search", "input", [16, 180, 358, 44], {
            "display": "block", "width": "358px", "height": "44px",
            "paddingTop": "10px", "paddingRight": "12px",
            "paddingBottom": "10px", "paddingLeft": "12px",
            "backgroundColor": "rgb(245, 247, 250)",
            "color": "rgb(24, 36, 49)", "fontSize": "16px",
            "fontWeight": "500", "fontFamily": "HarmonyOS Sans",
            "borderTopWidth": "0px", "borderRightWidth": "0px",
            "borderBottomWidth": "0px", "borderLeftWidth": "0px",
            "borderTopLeftRadius": "8px", "borderTopRightRadius": "8px",
            "borderBottomRightRadius": "8px", "borderBottomLeftRadius": "8px",
        }),
    ]
    for raw in raw_nodes:
        computed = BrowserComputedStyle().model_dump(by_alias=True)
        computed.update(raw["computed"])
        raw["computed"] = computed
        if raw["nodeId"] != "page":
            raw["directParentNodeId"] = "page"
            raw["isFlexItem"] = True
    snapshot = BrowserSnapshot.model_validate({
        "snapshotVersion": 1,
        "viewportWidth": 390,
        "viewportHeight": 844,
        "theme": "light",
        "tokenTheme": "harmonyos",
        "canvasBackgroundColor": "rgb(255, 255, 255)",
        "canvasBackgroundImage": "none",
        "nodes": raw_nodes,
    })

    result = export_annotated_html(
        html,
        page_name="NativeControls",
        snapshot=snapshot,
        require_snapshot=True,
    )

    assert result["quality"]["readiness"] == "ready"
    assert result["quality"]["componentCounts"] == {
        "Row": 0, "Column": 1, "Stack": 0, "Scroll": 0,
        "Text": 0, "Span": 0, "Image": 0, "SymbolGlyph": 0,
        "Divider": 0, "Button": 0, "List": 0, "ListItem": 0,
        "Grid": 0, "GridItem": 0, "Toggle": 1, "Slider": 1,
        "TextInput": 1, "Search": 1, "Checkbox": 0, "Radio": 0,
        "Tabs": 0, "TabContent": 0,
    }
    assert 'Toggle({ type: ToggleType.Switch, isOn: true })' in result["arkTs"]
    assert 'Slider({ value: 42.5, min: 0, max: 100, step: 0.5 })' in result["arkTs"]
    assert 'TextInput({ text: "Ada", placeholder: "姓名" })' in result["arkTs"]
    assert 'Search({ value: "ArkUI", placeholder: "搜索" })' in result["arkTs"]
    assert result["arkTs"].count(".enabled(false)") == 2
    assert ".enableKeyboardOnFocus(false)" in result["arkTs"]


MIXED_TEXT_HTML = """<main data-node-id="page" data-component="column">
  <div data-node-id="page.duration" data-component="text">
    <i data-node-id="page.duration.icon" data-component="symbol"
       data-lucide="clock"></i>
    45 分钟
  </div>
</main>"""


def _mixed_text_snapshot(
    *, display: str = "flex", flex_direction: str = "row"
) -> BrowserSnapshot:
    nodes = [
        _node("page", "main", [0, 0, 390, 844], {
            "display": "flex",
            "flexDirection": "column",
            "width": "390px",
            "height": "844px",
            "backgroundColor": "rgb(255, 255, 255)",
        }),
        _node("page.duration", "div", [16, 16, 120, 24], {
            "display": display,
            "flexDirection": flex_direction,
            "width": "120px",
            "height": "24px",
            "columnGap": "4px",
            "alignItems": "center",
            "color": "rgb(17, 24, 39)",
            "fontSize": "14px",
            "fontWeight": "500",
            "lineHeight": "20px",
        }),
        _node("page.duration.icon", "i", [16, 18, 20, 20], {
            "display": "block",
            "width": "20px",
            "height": "20px",
            "color": "rgb(17, 24, 39)",
            "fontSize": "20px",
        }),
    ]
    nodes[1]["directParentNodeId"] = "page"
    nodes[1]["isFlexItem"] = True
    nodes[2]["directParentNodeId"] = "page.duration"
    nodes[2]["isFlexItem"] = True
    return BrowserSnapshot.model_validate({
        "snapshotVersion": 1,
        "viewportWidth": 390,
        "viewportHeight": 844,
        "theme": "light",
        "tokenTheme": "harmonyos",
        "canvasBackgroundColor": "rgb(255, 255, 255)",
        "canvasBackgroundImage": "none",
        "nodes": nodes,
    })


def test_text_with_symbol_uses_verified_flex_row_and_generated_text() -> None:
    built = build_screen_ir(
        analyze_component_metadata(MIXED_TEXT_HTML),
        snapshot=_mixed_text_snapshot(),
    )

    assert built.readiness == "ready"
    assert built.screen_ir is not None
    duration = built.screen_ir["ui"]["children"][0]
    assert duration["componentName"] == "Row"
    assert "content" not in duration
    assert [child["componentName"] for child in duration["children"]] == [
        "SymbolGlyph", "Text",
    ]
    label = duration["children"][1]
    assert label["content"] == "45 分钟"
    assert label["styles"] == {
        "fontSize": 14,
        "fontColor": "#111827",
        "fontWeight": 500,
        "lineHeight": 20,
    }


def test_text_with_symbol_blocks_when_layout_is_not_flex() -> None:
    built = build_screen_ir(
        analyze_component_metadata(MIXED_TEXT_HTML),
        snapshot=_mixed_text_snapshot(display="block", flex_direction=""),
    )

    assert built.readiness == "blocked"
    assert built.screen_ir is None
    assert "UIBENCH_TEXT_SYMBOL_LAYOUT_CONFLICT" in {
        item.code for item in built.diagnostics
    }


def test_text_with_symbol_repair_passes_renderer_contract() -> None:
    result = export_annotated_html(
        MIXED_TEXT_HTML,
        page_name="MixedTextPage",
        snapshot=_mixed_text_snapshot(),
    )

    assert result["quality"]["readiness"] == "ready"
    assert result["quality"]["notices"] == 1
    duration = result["screenIr"]["ui"]["children"][0]
    assert duration["componentName"] == "Row"
    assert [child["componentName"] for child in duration["children"]] == [
        "SymbolGlyph", "Text",
    ]
    assert 'Text("45 分钟")' in result["arkTs"]


LIST_HTML = """<!doctype html><html><body>
<main data-node-id="feed" data-component="list">
  <article data-node-id="feed.first" data-component="list-item">
    <div data-node-id="feed.first.body" data-component="row">
      <p data-node-id="feed.first.title" data-component="text">Task 1</p>
    </div>
  </article>
  <article data-node-id="feed.second" data-component="list-item">
    <div data-node-id="feed.second.body" data-component="row">
      <p data-node-id="feed.second.title" data-component="text">Task 2</p>
    </div>
  </article>
</main>
</body></html>"""


def _list_snapshot(*, flex_direction: str = "column") -> BrowserSnapshot:
    horizontal = flex_direction.startswith("row")
    # Distinct axis gaps so the exported spacing proves which one was read.
    nodes = [
        _node("feed", "main", [0, 0, 390, 844], {
            "display": "flex",
            "flexDirection": flex_direction,
            "width": "390px",
            "height": "844px",
            "rowGap": "12px",
            "columnGap": "16px",
            "backgroundColor": "rgb(255, 255, 255)",
        }),
    ]
    parent_by_id = {
        "feed.first": ("feed", True),
        "feed.second": ("feed", True),
        "feed.first.body": ("feed.first", False),
        "feed.second.body": ("feed.second", False),
        "feed.first.title": ("feed.first.body", True),
        "feed.second.title": ("feed.second.body", True),
    }
    for index, prefix in enumerate(("feed.first", "feed.second")):
        left = index * 146.0 if horizontal else 0.0
        top = 0.0 if horizontal else index * 76.0
        item_width = 130.0 if horizontal else 390.0
        title_width = item_width - 32.0
        nodes.append(_node(prefix, "article", [left, top, item_width, 64], {
            "display": "block",
            "width": f"{item_width:g}px",
            "height": "64px",
        }))
        nodes.append(_node(
            f"{prefix}.body", "div", [left + 16, top, title_width, 64], {
                "display": "flex",
                "flexDirection": "row",
                "width": f"{title_width:g}px",
                "height": "64px",
                "alignItems": "center",
                "backgroundColor": "rgb(245, 247, 250)",
            },
        ))
        nodes.append(_node(
            f"{prefix}.title", "p", [left + 16, top + 20, title_width, 24], {
                "display": "block",
                "width": f"{title_width:g}px",
                "height": "24px",
                "color": "rgb(17, 24, 39)",
                "fontSize": "16px",
                "fontWeight": "500",
                "fontFamily": "Arial",
            },
        ))
    for node in nodes:
        parent = parent_by_id.get(node["nodeId"])
        if parent is not None:
            node["directParentNodeId"], node["isFlexItem"] = parent
        computed = BrowserComputedStyle().model_dump(by_alias=True)
        computed.update(node["computed"])
        node["computed"] = computed
    return BrowserSnapshot.model_validate({
        "snapshotVersion": 1,
        "viewportWidth": 390,
        "viewportHeight": 844,
        "theme": "light",
        "tokenTheme": "harmonyos",
        "canvasBackgroundColor": "rgb(255, 255, 255)",
        "canvasBackgroundImage": "none",
        "nodes": nodes,
    })


def test_annotated_list_exports_ready_arkts_with_item_spacing() -> None:
    assert HTML_TO_ARKUI_DIST.is_file()
    result = export_annotated_html(
        LIST_HTML,
        page_name="FeedPage",
        snapshot=_list_snapshot(),
        require_snapshot=True,
    )

    assert result["quality"]["readiness"] == "ready"
    assert result["quality"]["componentCounts"]["List"] == 1
    assert result["quality"]["componentCounts"]["ListItem"] == 2
    root = result["screenIr"]["ui"]
    assert root["componentName"] == "List"
    assert root["styles"]["space"] == 12
    assert [child["componentName"] for child in root["children"]] == [
        "ListItem", "ListItem",
    ]
    assert root["styles"]["listDirection"] == "Vertical"
    assert "List({ space: 12 }) {" in result["arkTs"]
    assert ".listDirection(Axis.Vertical)" in result["arkTs"]
    assert result["arkTs"].count("ListItem() {") == 2
    assert 'Text("Task 1")' in result["arkTs"]


def test_horizontal_list_exports_its_axis_and_main_axis_spacing() -> None:
    """ArkUI's List defaults to Vertical, so a row list must state its axis."""
    result = export_annotated_html(
        LIST_HTML,
        page_name="ShelfPage",
        snapshot=_list_snapshot(flex_direction="row"),
        require_snapshot=True,
    )

    assert result["quality"]["readiness"] == "ready"
    root = result["screenIr"]["ui"]
    assert root["componentName"] == "List"
    assert root["styles"]["listDirection"] == "Horizontal"
    # ArkUI spaces items along the main axis, which is now column-gap.
    assert root["styles"]["space"] == 16
    assert "List({ space: 16 }) {" in result["arkTs"]
    assert ".listDirection(Axis.Horizontal)" in result["arkTs"]


def test_horizontal_list_wrapper_items_span_the_cross_axis() -> None:
    """A generated entry stretches across the list's cross axis, not its main."""
    html = LIST_HTML.replace(
        '<article data-node-id="feed.first" data-component="list-item">',
        '<article data-node-id="feed.first" data-component="column">',
    )

    result = export_annotated_html(
        html,
        page_name="ShelfPage",
        snapshot=_list_snapshot(flex_direction="row"),
        require_snapshot=True,
    )

    generated = result["screenIr"]["ui"]["children"][0]
    assert generated["meta"]["nodeId"] == "feed.first:item"
    assert generated["styles"] == {"height": "100%"}


def test_list_the_browser_never_laid_out_on_one_axis_is_blocked() -> None:
    """A reversed list has no ArkUI axis, so it cannot be exported silently."""
    result = build_screen_ir(
        analyze_component_metadata(LIST_HTML),
        page_name="ShelfPage",
        snapshot=_list_snapshot(flex_direction="row-reverse"),
    )

    assert result.readiness == "blocked"
    assert [item.code for item in result.diagnostics if item.severity == "error"] == [
        "UIBENCH_ARKUI_LAYOUT_METADATA_CONFLICT",
    ]


def test_list_wraps_unwrapped_children_instead_of_blocking() -> None:
    """A plain entry inside a List is exported inside a generated ListItem."""
    html = LIST_HTML.replace(
        '<article data-node-id="feed.first" data-component="list-item">',
        '<article data-node-id="feed.first" data-component="column">',
    )

    result = export_annotated_html(
        html,
        page_name="FeedPage",
        snapshot=_list_snapshot(),
        require_snapshot=True,
    )

    # Wrapping is structural, not lossy: the rendered result is unchanged.
    assert result["quality"]["readiness"] == "ready"
    assert any(
        item["code"] == "ARKUI_LIST_CHILD_WRAPPED_AS_ITEM"
        for item in result["diagnostics"]
    )
    root = result["screenIr"]["ui"]
    assert [child["componentName"] for child in root["children"]] == [
        "ListItem", "ListItem",
    ]
    generated, authored = root["children"]
    assert generated["meta"]["nodeId"] == "feed.first:item"
    assert generated["children"][0]["componentName"] == "Column"
    assert authored["meta"]["nodeId"] == "feed.second"
    assert result["arkTs"].count("ListItem() {") == 2


@pytest.mark.parametrize(
    (
        "parent_direction",
        "flex_basis",
        "flex_shrink",
        "removed_dimension",
        "kept_dimension",
    ),
    [
        ("row", "0px", "1", "width", "height"),
        ("column", "0%", "0", "height", "width"),
    ],
)
def test_flex_grow_maps_to_layout_weight_without_browser_main_axis_size(
    parent_direction: str,
    flex_basis: str,
    flex_shrink: str,
    removed_dimension: str,
    kept_dimension: str,
) -> None:
    node = BrowserNodeSnapshot.model_validate(_node(
        "page.flex", "section", [0, 0, 120, 48], {
            "display": "block",
            "flexGrow": "1",
            "flexShrink": flex_shrink,
            "flexBasis": flex_basis,
        },
    ))

    styles, lossy = screen_ir_styles(
        "Text",
        node,
        parent_direction=parent_direction,
        flex_item_parent_verified=True,
    )

    assert lossy == ()
    assert styles["layoutWeight"] == 1
    assert removed_dimension not in styles
    assert kept_dimension in styles
    assert node.computed.flex_shrink == flex_shrink
    assert node.computed.flex_basis == flex_basis


@pytest.mark.parametrize("flex_basis", ["auto", "200px", "25%"])
def test_nonzero_or_auto_flex_basis_is_lossy_and_keeps_browser_size(
    flex_basis: str,
) -> None:
    node = BrowserNodeSnapshot.model_validate(_node(
        "page.flex", "section", [0, 0, 120, 48], {
            "display": "block",
            "flexGrow": "1",
            "flexShrink": "1",
            "flexBasis": flex_basis,
        },
    ))

    styles, lossy = screen_ir_styles(
        "Text",
        node,
        parent_direction="row",
        flex_item_parent_verified=True,
    )

    assert styles["width"] == 120
    assert "layoutWeight" not in styles
    assert lossy == (f"flex-basis:{flex_basis}",)


def test_unverified_flex_item_parent_does_not_apply_layout_weight() -> None:
    node = BrowserNodeSnapshot.model_validate(_node(
        "page.flex", "section", [0, 0, 120, 48], {
            "display": "block",
            "flexGrow": "1",
            "flexShrink": "1",
            "flexBasis": "0%",
        },
    ))

    styles, lossy = screen_ir_styles(
        "Text", node, parent_direction="row"
    )

    assert styles["width"] == 120
    assert "layoutWeight" not in styles
    assert lossy == ("flex-grow:unverified-flex-item",)


def test_unrepresentable_flex_shrink_is_lossy_and_keeps_browser_size() -> None:
    node = BrowserNodeSnapshot.model_validate(_node(
        "page.flex", "section", [0, 0, 120, 48], {
            "display": "block",
            "flexGrow": "1",
            "flexShrink": "2",
            "flexBasis": "0px",
        },
    ))

    styles, lossy = screen_ir_styles(
        "Text",
        node,
        parent_direction="row",
        flex_item_parent_verified=True,
    )

    assert styles["width"] == 120
    assert "layoutWeight" not in styles
    assert lossy == ("flex-shrink:2",)


def test_flex_grow_against_scroll_main_axis_maps_to_min_height() -> None:
    """layoutWeight against a Scroll clamps content to one viewport.

    ArkUI distributes weight from the scroll viewport, not the content, so
    the mapping keeps the browser bbox for the scroll range and states the
    grow behaviour as a constraintSize minimum that still fills a shorter
    viewport.
    """
    node = BrowserNodeSnapshot.model_validate(_node(
        "page.body", "section", [0, 72, 390, 1004], {
            "display": "flex",
            "flexDirection": "column",
            "flexGrow": "1",
            "flexShrink": "1",
            "flexBasis": "0%",
        },
    ))

    styles, lossy = screen_ir_styles(
        "Column",
        node,
        parent_direction="column",
        flex_item_parent_verified=True,
        flex_container_scrolls_main_axis=True,
    )

    assert "layoutWeight" not in styles
    assert styles["height"] == 1004
    assert styles["minHeight"] == "100%"
    assert lossy == ()


SCROLL_PAGE_HTML = """<!doctype html><html><body>
<main data-node-id="page" data-component="scroll">
  <header data-node-id="page.appbar" data-component="row">
    <p data-node-id="page.appbar.title" data-component="text">设置</p>
  </header>
  <section data-node-id="page.body" data-component="column">
    <p data-node-id="page.body.text" data-component="text">内容</p>
  </section>
</main>
</body></html>"""


def _scroll_page_snapshot() -> BrowserSnapshot:
    nodes = [
        _node("page", "main", [0, 0, 390, 844], {
            "display": "flex",
            "flexDirection": "column",
            "width": "390px",
            "height": "844px",
            "overflowY": "auto",
            "backgroundColor": "rgb(241, 243, 245)",
        }),
        _node("page.appbar", "header", [0, 0, 390, 72], {
            "display": "flex",
            "flexDirection": "row",
            "width": "390px",
            "height": "72px",
            "alignItems": "center",
        }),
        _node("page.appbar.title", "p", [16, 24, 100, 24], {
            "display": "block",
            "width": "100px",
            "height": "24px",
            "color": "rgb(17, 24, 39)",
            "fontSize": "18px",
            "fontWeight": "600",
            "fontFamily": "Arial",
        }),
        # Taller than the viewport: the page only scrolls if this height
        # survives the export instead of being replaced by layoutWeight.
        _node("page.body", "section", [0, 72, 390, 1004], {
            "display": "flex",
            "flexDirection": "column",
            "flexGrow": "1",
            "flexShrink": "1",
            "flexBasis": "0%",
            "width": "390px",
            "height": "1004px",
        }),
        _node("page.body.text", "p", [16, 88, 200, 24], {
            "display": "block",
            "width": "200px",
            "height": "24px",
            "color": "rgb(17, 24, 39)",
            "fontSize": "16px",
            "fontWeight": "400",
            "fontFamily": "Arial",
        }),
    ]
    parent_by_id = {
        "page.appbar": ("page", True),
        "page.appbar.title": ("page.appbar", True),
        "page.body": ("page", True),
        "page.body.text": ("page.body", True),
    }
    for node in nodes:
        parent = parent_by_id.get(node["nodeId"])
        if parent is not None:
            node["directParentNodeId"], node["isFlexItem"] = parent
        computed = BrowserComputedStyle().model_dump(by_alias=True)
        computed.update(node["computed"])
        node["computed"] = computed
    return BrowserSnapshot.model_validate({
        "snapshotVersion": 1,
        "viewportWidth": 390,
        "viewportHeight": 844,
        "theme": "light",
        "tokenTheme": "harmonyos",
        "canvasBackgroundColor": "rgb(255, 255, 255)",
        "canvasBackgroundImage": "none",
        "nodes": nodes,
    })


def test_flex_grow_inside_scroll_keeps_page_scrollable() -> None:
    """A flex:1 area whose flex container is the scroll must keep its bbox."""
    result = export_annotated_html(
        SCROLL_PAGE_HTML,
        page_name="ScrollPage",
        snapshot=_scroll_page_snapshot(),
        require_snapshot=True,
    )

    assert ".layoutWeight(" not in result["arkTs"]
    scroll = result["screenIr"]["ui"]
    assert scroll["componentName"] == "Scroll"
    wrapper = scroll["children"][0]
    assert wrapper["meta"]["nodeId"] == "page:content"
    assert "height" not in wrapper["styles"]
    body = wrapper["children"][1]
    assert body["meta"]["nodeId"] == "page.body"
    assert body["styles"]["height"] == 1004
    assert body["styles"]["minHeight"] == "100%"
    assert "layoutWeight" not in body["styles"]
    assert '.constraintSize({ minHeight: "100%" })' in result["arkTs"]
    assert result["quality"]["readiness"] == "ready"
    assert not any(
        item["code"] == "UIBENCH_BROWSER_STYLE_LOSSY"
        for item in result["diagnostics"]
    )


SANDWICH_PAGE_HTML = """<!doctype html><html><body>
<div data-node-id="page" data-component="column">
  <header data-node-id="page.appbar" data-component="row">
    <p data-node-id="page.appbar.title" data-component="text">设置</p>
  </header>
  <main data-node-id="page.scroll" data-component="scroll">
    <section data-node-id="page.scroll.content" data-component="column">
      <p data-node-id="page.scroll.text" data-component="text">内容</p>
    </section>
  </main>
</div>
</body></html>"""


def _sandwich_page_snapshot() -> BrowserSnapshot:
    nodes = [
        _node("page", "div", [0, 0, 390, 844], {
            "display": "flex",
            "flexDirection": "column",
            "width": "390px",
            "height": "844px",
            "backgroundColor": "rgb(241, 243, 245)",
        }),
        _node("page.appbar", "header", [0, 0, 390, 72], {
            "display": "flex",
            "flexDirection": "row",
            "width": "390px",
            "height": "72px",
            "alignItems": "center",
        }),
        _node("page.appbar.title", "p", [16, 24, 100, 24], {
            "display": "block",
            "width": "100px",
            "height": "24px",
            "color": "rgb(17, 24, 39)",
            "fontSize": "18px",
            "fontWeight": "600",
            "fontFamily": "Arial",
        }),
        _node("page.scroll", "main", [0, 72, 390, 772], {
            "display": "block",
            "flexGrow": "1",
            "flexShrink": "1",
            "flexBasis": "0%",
            "width": "390px",
            "height": "772px",
            "overflowY": "auto",
        }),
        _node("page.scroll.content", "section", [0, 72, 390, 1004], {
            "display": "flex",
            "flexDirection": "column",
            "width": "390px",
            "height": "1004px",
        }),
        _node("page.scroll.text", "p", [16, 88, 200, 24], {
            "display": "block",
            "width": "200px",
            "height": "24px",
            "color": "rgb(17, 24, 39)",
            "fontSize": "16px",
            "fontWeight": "400",
            "fontFamily": "Arial",
        }),
    ]
    parent_by_id = {
        "page.appbar": ("page", True),
        "page.appbar.title": ("page.appbar", True),
        "page.scroll": ("page", True),
        "page.scroll.content": ("page.scroll", False),
        "page.scroll.text": ("page.scroll.content", True),
    }
    for node in nodes:
        parent = parent_by_id.get(node["nodeId"])
        if parent is not None:
            node["directParentNodeId"], node["isFlexItem"] = parent
        computed = BrowserComputedStyle().model_dump(by_alias=True)
        computed.update(node["computed"])
        node["computed"] = computed
    return BrowserSnapshot.model_validate({
        "snapshotVersion": 1,
        "viewportWidth": 390,
        "viewportHeight": 844,
        "theme": "light",
        "tokenTheme": "harmonyos",
        "canvasBackgroundColor": "rgb(255, 255, 255)",
        "canvasBackgroundImage": "none",
        "nodes": nodes,
    })


@pytest.mark.parametrize(
    ("computed_columns", "expected_template", "expected_lossy"),
    [
        # 175 + 8 + 175 fills the 358px content box, so the equal tracks
        # round-trip as adaptive fractions.
        ("175px 175px", "1fr 1fr", ()),
        ("114px 114px 114px", "1fr 1fr 1fr", ()),
        # Equal tracks that do not fill the content box must stay frozen:
        # 1fr would stretch them across the leftover space on device.
        (
            "119.3438px 119.3438px 119.3438px",
            "119.3438vp 119.3438vp 119.3438vp",
            (),
        ),
        ("100px 100px", "100vp 100vp", ()),
        ("96.5px 240px", "96.5vp 240vp", ()),
        ("none", None, ()),
        ("", None, ()),
        (
            "min-content 96px",
            None,
            ("grid-template-columns:min-content 96px",),
        ),
    ],
)
def test_grid_used_tracks_freeze_into_arkui_templates(
    computed_columns: str,
    expected_template: str | None,
    expected_lossy: tuple[str, ...],
) -> None:
    node = BrowserNodeSnapshot.model_validate(_node(
        "page.grid", "section", [16, 16, 358, 96], {
            "display": "grid",
            "gridTemplateColumns": computed_columns,
            "gridAutoFlow": "row",
            "columnGap": "8px",
            "rowGap": "12px",
            "paddingTop": "0px",
            "paddingRight": "0px",
            "paddingBottom": "0px",
            "paddingLeft": "0px",
            "borderTopWidth": "0px",
            "borderRightWidth": "0px",
            "borderBottomWidth": "0px",
            "borderLeftWidth": "0px",
        },
    ))

    styles, lossy = screen_ir_styles("Grid", node)

    if expected_template is None:
        assert "columnsTemplate" not in styles
    else:
        assert styles["columnsTemplate"] == expected_template
    assert "rowsTemplate" not in styles
    assert styles["columnsGap"] == 8
    assert styles["rowsGap"] == 12
    assert lossy == expected_lossy


def test_list_and_grid_report_unmappable_alignment_as_lossy() -> None:
    """ArkUI List/Grid have no justifyContent/alignItems equivalents.

    Entries pack from the main-axis start on device, so any other captured
    distribution must be reported instead of silently repositioning content.
    """
    list_node = BrowserNodeSnapshot.model_validate(_node(
        "feed", "main", [0, 0, 390, 120], {
            "display": "flex",
            "flexDirection": "row",
            "justifyContent": "center",
            "alignItems": "center",
        },
    ))
    grid_node = BrowserNodeSnapshot.model_validate(_node(
        "page.grid", "section", [16, 16, 358, 96], {
            "display": "grid",
            "gridAutoFlow": "row",
            "justifyContent": "space-between",
        },
    ))

    _, list_lossy = screen_ir_styles("List", list_node)
    _, grid_lossy = screen_ir_styles("Grid", grid_node)

    assert "justify-content:center" in list_lossy
    assert "align-items:center" in list_lossy
    assert "justify-content:space-between" in grid_lossy


def test_list_alignments_equivalent_to_packed_start_stay_silent() -> None:
    node = BrowserNodeSnapshot.model_validate(_node(
        "feed", "main", [0, 0, 390, 120], {
            "display": "flex",
            "flexDirection": "row",
            "justifyContent": "normal",
            "alignItems": "stretch",
        },
    ))

    _, lossy = screen_ir_styles("List", node)

    assert lossy == ()


def test_emoji_fallback_families_never_become_the_arkui_font() -> None:
    """Tailwind's default stack lists only emoji faces after the generics."""
    node = BrowserNodeSnapshot.model_validate(_node(
        "page.title", "p", [16, 16, 200, 24], {
            "display": "block",
            "fontFamily": (
                'ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji", '
                '"Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"'
            ),
        },
    ))

    styles, _ = screen_ir_styles("Text", node)

    assert "fontFamily" not in styles


def test_a_concrete_family_ahead_of_emoji_fallbacks_is_still_selected() -> None:
    node = BrowserNodeSnapshot.model_validate(_node(
        "page.title", "p", [16, 16, 200, 24], {
            "display": "block",
            "fontFamily": 'Inter, "Apple Color Emoji", sans-serif',
        },
    ))

    styles, _ = screen_ir_styles("Text", node)

    assert styles["fontFamily"] == "Inter"


GRID_PAGE_HTML = """<!doctype html><html><body>
<main data-node-id="page" data-component="column">
  <section data-node-id="page.grid" data-component="grid">
    <article data-node-id="page.grid.a" data-component="column"></article>
    <article data-node-id="page.grid.b" data-component="column"></article>
  </section>
</main>
</body></html>"""


def _grid_page_snapshot(
    *,
    grid_computed: dict[str, str] | None = None,
    second_cell_computed: dict[str, str] | None = None,
) -> BrowserSnapshot:
    nodes = [
        _node("page", "main", [0, 0, 390, 844], {
            "display": "flex",
            "flexDirection": "column",
            "width": "390px",
            "height": "844px",
            "backgroundColor": "rgb(255, 255, 255)",
        }),
        _node("page.grid", "section", [16, 16, 358, 96], grid_computed or {
            "display": "grid",
            "gridTemplateColumns": "175px 175px",
            "gridTemplateRows": "96px",
            "gridAutoFlow": "row",
            "columnGap": "8px",
            "width": "358px",
            "height": "96px",
            "paddingTop": "0px",
            "paddingRight": "0px",
            "paddingBottom": "0px",
            "paddingLeft": "0px",
            "borderTopWidth": "0px",
            "borderRightWidth": "0px",
            "borderBottomWidth": "0px",
            "borderLeftWidth": "0px",
        }),
        _node("page.grid.a", "article", [16, 16, 175, 96], {
            "display": "flex",
            "flexDirection": "column",
            "width": "175px",
            "height": "96px",
        }),
        _node("page.grid.b", "article", [199, 16, 175, 96], {
            "display": "flex",
            "flexDirection": "column",
            "width": "175px",
            "height": "96px",
            **(second_cell_computed or {}),
        }),
    ]
    parent_by_id = {
        "page.grid": ("page", True),
        "page.grid.a": ("page.grid", False),
        "page.grid.b": ("page.grid", False),
    }
    for node in nodes:
        parent = parent_by_id.get(node["nodeId"])
        if parent is not None:
            node["directParentNodeId"], node["isFlexItem"] = parent
        computed = BrowserComputedStyle().model_dump(by_alias=True)
        computed.update(node["computed"])
        node["computed"] = computed
    return BrowserSnapshot.model_validate({
        "snapshotVersion": 1,
        "viewportWidth": 390,
        "viewportHeight": 844,
        "theme": "light",
        "tokenTheme": "harmonyos",
        "canvasBackgroundColor": "rgb(255, 255, 255)",
        "canvasBackgroundImage": "none",
        "nodes": nodes,
    })


def test_annotated_grid_exports_grid_items_with_track_template() -> None:
    result = export_annotated_html(
        GRID_PAGE_HTML,
        page_name="GalleryPage",
        snapshot=_grid_page_snapshot(),
        require_snapshot=True,
    )

    assert result["quality"]["readiness"] == "ready"
    assert result["quality"]["componentCounts"]["Grid"] == 1
    assert result["quality"]["componentCounts"]["GridItem"] == 2
    grid = result["screenIr"]["ui"]["children"][0]
    assert grid["componentName"] == "Grid"
    assert grid["styles"]["columnsTemplate"] == "1fr 1fr"
    assert grid["styles"]["rowsTemplate"] == "1fr"
    assert grid["styles"]["columnsGap"] == 8
    assert "rowsGap" not in grid["styles"]
    assert [child["componentName"] for child in grid["children"]] == [
        "GridItem", "GridItem",
    ]
    assert grid["children"][0]["meta"]["nodeId"] == "page.grid.a:item"
    assert any(
        item["code"] == "ARKUI_GRID_CHILD_WRAPPED_AS_ITEM"
        for item in result["diagnostics"]
    )
    assert '.columnsTemplate("1fr 1fr")' in result["arkTs"]
    assert '.columnsGap(8)' in result["arkTs"]
    assert result["arkTs"].count("GridItem() {") == 2


def test_explicit_grid_placement_blocks_export() -> None:
    snapshot = _grid_page_snapshot(
        second_cell_computed={"gridColumnStart": "span 2"},
    )

    with pytest.raises(ArkUiExporterError) as raised:
        export_annotated_html(
            GRID_PAGE_HTML,
            page_name="GalleryPage",
            snapshot=snapshot,
            require_snapshot=True,
        )

    assert raised.value.code == "UIBENCH_SCREEN_IR_BLOCKED"
    assert any(
        item["code"] == "UIBENCH_ARKUI_GRID_PLACEMENT_UNSUPPORTED"
        and item["nodeId"] == "page.grid.b"
        for item in raised.value.details
    )


def test_grid_metadata_without_grid_layout_evidence_blocks_export() -> None:
    snapshot = _grid_page_snapshot(grid_computed={
        "display": "flex",
        "flexDirection": "row",
        "width": "358px",
        "height": "96px",
    })

    with pytest.raises(ArkUiExporterError) as raised:
        export_annotated_html(
            GRID_PAGE_HTML,
            page_name="GalleryPage",
            snapshot=snapshot,
            require_snapshot=True,
        )

    assert raised.value.code == "UIBENCH_SCREEN_IR_BLOCKED"
    assert any(
        item["code"] == "UIBENCH_ARKUI_LAYOUT_METADATA_CONFLICT"
        and item["nodeId"] == "page.grid"
        for item in raised.value.details
    )


def test_flex_grow_on_scroll_itself_still_maps_to_layout_weight() -> None:
    """The sandwich pattern anchors the Scroll to a definite page height."""
    result = export_annotated_html(
        SANDWICH_PAGE_HTML,
        page_name="SandwichPage",
        snapshot=_sandwich_page_snapshot(),
        require_snapshot=True,
    )

    root = result["screenIr"]["ui"]
    assert root["componentName"] == "Column"
    scroll = root["children"][1]
    assert scroll["componentName"] == "Scroll"
    assert scroll["styles"]["layoutWeight"] == 1
    assert "height" not in scroll["styles"]
    assert ".layoutWeight(1)" in result["arkTs"]
    content = scroll["children"][0]
    assert content["meta"]["nodeId"] == "page.scroll.content"
    assert content["styles"]["height"] == 1004


def test_snapshot_rejects_unknown_direct_dom_parent_reference() -> None:
    child = _node("page.child", "div", [0, 0, 120, 48], {
        "display": "block",
    })
    child["directParentNodeId"] = "page.wrapper"

    with pytest.raises(
        ValidationError,
        match="directParentNodeId is absent from snapshot nodes",
    ):
        BrowserSnapshot.model_validate({
            "snapshotVersion": 1,
            "viewportWidth": 390,
            "viewportHeight": 844,
            "theme": "light",
            "tokenTheme": "harmonyos",
            "nodes": [child],
        })


def test_unannotated_dom_wrapper_blocks_screen_ir_with_parent_diagnostic() -> None:
    from uibench.arkui.exporter import ArkUiExporterError

    html = """<main data-node-id="page" data-component="column">
      <div data-node-id="page.wrapper">
        <p data-node-id="page.item" data-component="text">Flexible</p>
      </div>
    </main>"""
    root = _node("page", "main", [0, 0, 390, 844], {
        "display": "flex", "flexDirection": "column",
    })
    wrapper = _node("page.wrapper", "div", [0, 0, 390, 100], {
        "display": "block",
    })
    wrapper["directParentNodeId"] = "page"
    wrapper["isFlexItem"] = True
    item = _node("page.item", "p", [0, 0, 390, 100], {
        "display": "block",
        "flexGrow": "1",
        "flexShrink": "1",
        "flexBasis": "0px",
    })
    item["directParentNodeId"] = "page.wrapper"
    item["isFlexItem"] = False
    snapshot = BrowserSnapshot.model_validate({
        "snapshotVersion": 1,
        "viewportWidth": 390,
        "viewportHeight": 844,
        "theme": "light",
        "tokenTheme": "harmonyos",
        "nodes": [root, wrapper, item],
    })

    with pytest.raises(ArkUiExporterError) as raised:
        export_annotated_html(
            html, page_name="WrappedFlexItem", snapshot=snapshot
        )

    assert raised.value.code == "UIBENCH_SCREEN_IR_BLOCKED"
    assert any(
        item["code"] == "UIBENCH_ARKUI_DOM_PARENT_MISMATCH"
        and item["nodeId"] == "page.item"
        and "'page.wrapper'" in item["message"]
        for item in raised.value.details
    )


def test_export_repair_makes_normal_flow_wrapper_snapshot_exportable() -> None:
    html = """<main data-node-id="page" data-component="column"
      class="flex flex-col">
      <div class="space-y-2">
        <p data-node-id="page.item" data-component="text">Flexible</p>
      </div>
    </main>"""
    repaired = repair_arkui_export_html(html)
    root = _node("page", "main", [0, 0, 390, 844], {
        "display": "flex", "flexDirection": "column",
    })
    wrapper = _node("page.content", "div", [0, 0, 390, 100], {
        "display": "block",
    })
    wrapper["directParentNodeId"] = "page"
    wrapper["isFlexItem"] = True
    item = _node("page.item", "p", [0, 0, 390, 100], {
        "display": "block",
    })
    item["directParentNodeId"] = "page.content"
    item["isFlexItem"] = False
    snapshot = BrowserSnapshot.model_validate({
        "snapshotVersion": 1,
        "viewportWidth": 390,
        "viewportHeight": 844,
        "theme": "light",
        "tokenTheme": "harmonyos",
        "nodes": [root, wrapper, item],
    })

    built = build_screen_ir(
        analyze_component_metadata(repaired.html),
        page_name="RepairedWrapper",
        snapshot=snapshot,
    )

    assert repaired.changed is True
    assert built.screen_ir is not None
    assert not any(
        item.code == "UIBENCH_ARKUI_DOM_PARENT_MISMATCH"
        for item in built.diagnostics
    )
    assert 'class="space-y-2"' in repaired.html


def test_direct_verified_flex_item_maps_to_layout_weight_in_screen_ir() -> None:
    html = """<main data-node-id="page" data-component="column">
      <p data-node-id="page.item" data-component="text">Flexible</p>
    </main>"""
    root = _node("page", "main", [0, 0, 390, 844], {
        "display": "flex", "flexDirection": "column",
    })
    item = _node("page.item", "p", [0, 0, 390, 844], {
        "display": "block",
        "flexGrow": "1",
        "flexShrink": "1",
        "flexBasis": "0%",
    })
    item["directParentNodeId"] = "page"
    item["isFlexItem"] = True
    snapshot = BrowserSnapshot.model_validate({
        "snapshotVersion": 1,
        "viewportWidth": 390,
        "viewportHeight": 844,
        "theme": "light",
        "tokenTheme": "harmonyos",
        "nodes": [root, item],
    })

    result = export_annotated_html(
        html, page_name="DirectFlexItem", snapshot=snapshot
    )

    item_styles = result["screenIr"]["ui"]["children"][0]["styles"]
    assert item_styles["layoutWeight"] == 1
    assert "height" not in item_styles
    assert result["quality"]["readiness"] == "ready"


@pytest.mark.parametrize("position", ["absolute", "fixed"])
def test_out_of_flow_flex_child_never_maps_to_layout_weight(
    position: str,
) -> None:
    node = BrowserNodeSnapshot.model_validate(_node(
        "page.overlay", "section", [0, 0, 120, 48], {
            "display": "block",
            "position": position,
            "flexGrow": "1",
            "flexShrink": "1",
            "flexBasis": "0px",
        },
    ))

    styles, lossy = screen_ir_styles(
        "Text",
        node,
        parent_direction="row",
        flex_item_parent_verified=True,
    )

    assert "layoutWeight" not in styles
    assert styles["width"] == 120
    assert f"flex-grow:out-of-flow-position:{position}" in lossy


@pytest.mark.parametrize(
    ("component", "bbox"),
    [
        ("column", [20, 30, 120, 200]),
        ("button", [0, 0, 390, 844]),
    ],
)
def test_non_page_root_keeps_browser_dimensions(
    component: str,
    bbox: list[int],
) -> None:
    tag = "button" if component == "button" else "main"
    html = (
        f'<{tag} data-node-id="root" data-component="{component}">'
        f'</{tag}>'
    )
    computed = {
        "display": "block",
        "width": f"{bbox[2]}px",
        "height": f"{bbox[3]}px",
    }
    if component == "column":
        computed.update({"display": "flex", "flexDirection": "column"})
    snapshot = BrowserSnapshot.model_validate({
        "snapshotVersion": 1,
        "viewportWidth": 390,
        "viewportHeight": 844,
        "theme": "light",
        "tokenTheme": "harmonyos",
        "nodes": [_node("root", tag, bbox, computed)],
    })

    result = export_annotated_html(
        html, page_name="BoundedRoot", snapshot=snapshot
    )

    assert result["screenIr"]["ui"]["styles"]["width"] == bbox[2]
    assert result["screenIr"]["ui"]["styles"]["height"] == bbox[3]


def test_css_font_stack_selects_first_concrete_family() -> None:
    node = BrowserNodeSnapshot.model_validate(_node(
        "page.title", "h1", [0, 0, 120, 32], {
            "display": "block",
            "fontFamily": (
                '\"HarmonyOS Sans SC\", \"HarmonyOS Sans\", '
                '\"PingFang SC\", sans-serif'
            ),
        },
    ))

    styles, _ = screen_ir_styles("Text", node)

    assert styles["fontFamily"] == "HarmonyOS Sans SC"


def test_generic_only_css_font_stack_uses_arkui_default() -> None:
    node = BrowserNodeSnapshot.model_validate(_node(
        "page.title", "h1", [0, 0, 120, 32], {
            "display": "block",
            "fontFamily": "system-ui, sans-serif",
        },
    ))

    styles, _ = screen_ir_styles("Text", node)

    assert "fontFamily" not in styles


def test_divider_single_solid_border_maps_to_native_divider_styles() -> None:
    node = BrowserNodeSnapshot.model_validate(_node(
        "page.divider", "div", [16, 40, 358, 1], {
            "display": "block",
            "borderTopWidth": "0px",
            "borderRightWidth": "0px",
            "borderBottomWidth": "1px",
            "borderLeftWidth": "0px",
            "borderBottomColor": "rgba(0, 0, 0, 0.05)",
            "borderBottomStyle": "solid",
        },
    ))

    styles, lossy = screen_ir_styles("Divider", node)

    assert lossy == ()
    assert styles["width"] == 358
    assert styles["height"] == 1
    assert styles["dividerColor"] == "#0D000000"
    assert styles["dividerStrokeWidth"] == 1
    assert styles["dividerVertical"] is False
    assert "backgroundColor" not in styles
    assert "border" not in styles


def test_divider_vertical_solid_border_maps_to_native_direction() -> None:
    node = BrowserNodeSnapshot.model_validate(_node(
        "page.divider", "div", [40, 16, 2, 358], {
            "display": "block",
            "borderTopWidth": "0px",
            "borderRightWidth": "2px",
            "borderBottomWidth": "0px",
            "borderLeftWidth": "0px",
            "borderRightColor": "rgb(17, 24, 39)",
            "borderRightStyle": "solid",
        },
    ))

    styles, lossy = screen_ir_styles("Divider", node)

    assert lossy == ()
    assert styles["dividerColor"] == "#111827"
    assert styles["dividerStrokeWidth"] == 2
    assert styles["dividerVertical"] is True


def _snapshot_with_content_display(**computed: str) -> BrowserSnapshot:
    payload = _snapshot().model_dump(by_alias=True)
    content = next(
        node for node in payload["nodes"]
        if node["nodeId"] == "page.content"
    )
    content["computed"].update(computed)
    return BrowserSnapshot.model_validate(payload)


def test_normal_flow_container_is_the_column_it_already_renders_as() -> None:
    """Block children stack top to bottom, which is exactly what Column does."""
    result = export_annotated_html(
        HTML,
        page_name="BlockLayout",
        snapshot=_snapshot_with_content_display(display="block"),
    )
    content = result["screenIr"]["ui"]["children"][0]

    assert content["meta"]["nodeId"] == "page.content"
    assert content["componentName"] == "Column"
    assert not any(
        item["code"] == "UIBENCH_ARKUI_LAYOUT_FOLLOWS_BROWSER"
        for item in result["diagnostics"]
    )


def test_row_column_metadata_follows_the_rendered_flex_direction() -> None:
    """Tailwind's bare `flex` is row; the export has to match what shipped."""
    result = export_annotated_html(
        HTML,
        page_name="RowLayout",
        snapshot=_snapshot_with_content_display(
            display="flex", flexDirection="row"
        ),
    )
    content = result["screenIr"]["ui"]["children"][0]
    followed = [
        item for item in result["diagnostics"]
        if item["code"] == "UIBENCH_ARKUI_LAYOUT_FOLLOWS_BROWSER"
    ]

    assert content["componentName"] == "Row"
    assert [item["nodeId"] for item in followed] == ["page.content"]
    assert followed[0]["severity"] == "notice"


@pytest.mark.parametrize("computed", [
    {"display": "grid"},
    {"display": "flex", "flexDirection": "row-reverse"},
    {"display": "inline"},
])
def test_layouts_arkui_cannot_express_still_block_screen_ir(
    computed: dict[str, str],
) -> None:
    from uibench.arkui.exporter import ArkUiExporterError

    with pytest.raises(ArkUiExporterError) as raised:
        export_annotated_html(
            HTML,
            page_name="ConflictingLayout",
            snapshot=_snapshot_with_content_display(**computed),
        )

    assert raised.value.code == "UIBENCH_SCREEN_IR_BLOCKED"
    assert [
        item["nodeId"] for item in raised.value.details
        if item["code"] == "UIBENCH_ARKUI_LAYOUT_METADATA_CONFLICT"
    ] == ["page.content"]


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
            _node("page.hidden.text", "p", [0, 0, 0, 0], {
                "display": "none", "fontSize": "16px",
            }, visible=False),
            _node("page.visible", "p", [0, 0, 80, 20], {
                "display": "block", "fontSize": "16px",
            }),
        ],
    })
    snapshot.nodes[-1].direct_parent_node_id = "page"
    snapshot.nodes[-1].is_flex_item = True

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


def test_hidden_ancestor_does_not_exempt_descendant_snapshot_entry() -> None:
    from uibench.arkui.exporter import ArkUiExporterError

    html = """<main data-node-id="page" data-component="column">
      <section data-node-id="page.hidden" data-component="column">
        <p data-node-id="page.hidden.text" data-component="text">SECRET</p>
      </section>
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
            }),
            _node("page.hidden", "section", [0, 0, 0, 0], {
                "display": "none", "flexDirection": "column",
            }, visible=False),
        ],
    })

    with pytest.raises(ArkUiExporterError) as raised:
        export_annotated_html(
            html, page_name="MissingHiddenDescendant", snapshot=snapshot
        )

    assert raised.value.code == "UIBENCH_SCREEN_IR_BLOCKED"
    assert any(
        item["code"] == "UIBENCH_BROWSER_SNAPSHOT_NODE_MISSING"
        and item["nodeId"] == "page.hidden.text"
        for item in raised.value.details
    )


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
    assert '.backgroundColor("#0A59F7")' in payload["arkTs"]
    assert ".fontSize(20)" in payload["arkTs"]


def test_index_contains_fixed_viewport_snapshot_bridge() -> None:
    assert "function arkuiSnapshotRuntime" in app_mod.INDEX_HTML
    assert "uibench-arkui-snapshot-request" in app_mod.INDEX_HTML
    assert "querySelectorAll('[data-node-id]')" in app_mod.INDEX_HTML
    assert "widthSizing: capturedWidthSizing(element)" in app_mod.INDEX_HTML
    assert "singleLineTextWidth: singleLineTextWidth(element)" in app_mod.INDEX_HTML
    assert "width:390px;height:844px" in app_mod.INDEX_HTML
    assert "typeof arkuiCaptureSession === 'string'" in app_mod.INDEX_HTML
    assert "snapshot: snapshot" in app_mod.INDEX_HTML
    assert "async function captureAssets()" in app_mod.INDEX_HTML
    assert "contentBase64: bytesToBase64(loaded.bytes)" in app_mod.INDEX_HTML
    assert "credentials: 'omit'" in app_mod.INDEX_HTML
    assert "function downloadBase64" in app_mod.INDEX_HTML
    assert "下载鸿蒙工程" in app_mod.INDEX_HTML
