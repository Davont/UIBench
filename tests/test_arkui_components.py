"""Offline tests for the ArkUI component registry and HTML metadata contract."""
import json
from pathlib import Path

import pytest

from uibench.arkui import (
    MOBILE_ARKUI_METADATA_INSTRUCTIONS,
    ComponentRegistryError,
    analyze_component_metadata,
    build_screen_ir,
    load_component_registry,
    load_renderer_contract,
    validate_component_registry,
)
from uibench.prompts import SYSTEM_MOBILE, prompt_for


def _codes(report) -> set[str]:
    return {item.code for item in report.diagnostics}


def test_checked_in_registry_has_phased_component_families() -> None:
    registry = load_component_registry()

    assert registry.schema_version == 1
    assert registry.annotation_version == 1
    assert registry.renderer_contract_version == 2
    assert registry.screen_ir_schema_version == 2
    assert registry.framework == "ArkUI"
    assert registry.components["column"].arkui_component == "Column"
    assert registry.components["symbol"].arkui_component == "SymbolGlyph"
    assert registry.components["scroll"].max_component_children == 1
    assert registry.components["list"].allowed_children == frozenset({"list-item"})
    assert registry.components["grid-item"].allowed_parents == frozenset({"grid"})
    assert registry.components["checkbox"].category == "selection"
    assert "button" in registry.keys_for_phases("P0")
    assert "grid" in registry.keys_for_phases("P1")
    assert "water-flow" in registry.keys_for_phases("P2")
    assert registry.renderer_keys() == (
        "column", "row", "stack", "scroll", "text", "span", "image",
        "symbol", "divider", "button",
    )
    assert registry.components["column"].min_api_version == 7
    assert registry.components["symbol"].min_api_version == 11
    assert registry.components["image"].max_component_children == 0
    assert registry.components["grid"].renderer_supported is False


def test_pinned_renderer_contract_matches_vendored_html_to_arkui() -> None:
    vendored_contract = (
        Path(__file__).resolve().parents[1]
        / "node_modules/@local/html-to-arkui/contracts/arkui-component-registry.json"
    )
    assert vendored_contract.is_file(), (
        "vendored html-to-arkui runtime is missing; run "
        "npm ci --ignore-scripts --offline"
    )
    expected = json.loads(vendored_contract.read_text(encoding="utf-8"))
    pinned_document = json.loads(
        (
            Path(__file__).resolve().parents[1]
            / "uibench/arkui/renderer_contract.json"
        ).read_text(encoding="utf-8")
    )
    pinned = load_renderer_contract()

    assert pinned_document == expected
    assert pinned.contract_version == expected["contractVersion"]
    assert pinned.screen_ir_schema_version == expected["screenIrSchemaVersion"]
    assert set(pinned.components) == {
        component["name"] for component in expected["components"]
    }
    for component in expected["components"]:
        actual = pinned.components[component["name"]]
        assert actual.min_api_version == component["minApiVersion"]
        assert actual.max_children == component["maxChildren"]
        assert actual.required_fields == tuple(component["requiredFields"])


def test_registry_rejects_unknown_component_references() -> None:
    document = {
        "schemaVersion": 1,
        "annotationVersion": 1,
        "target": {
            "framework": "ArkUI",
            "language": "ArkTS",
            "profile": "test",
        },
        "components": {
            "column": {
                "arkuiComponent": "Column",
                "category": "layout",
                "phase": "P0",
                "fallback": "missing",
                "minApiVersion": None,
            }
        },
    }

    with pytest.raises(ComponentRegistryError, match="unknown keys: missing"):
        validate_component_registry(document)


def test_valid_metadata_builds_addressable_manifest() -> None:
    html = """
    <main data-node-id="shop.home" data-component="scroll">
      <section data-node-id="shop.content" data-component="column">
        <section data-node-id="shop.products" data-component="column"
                 data-ui-role="product-list" data-repeat="products">
          <article data-node-id="shop.product-headphones"
                   data-component="row" data-ui-role="product-card"
                   data-item-key="headphones">
            <img data-node-id="shop.product-headphones.image"
                 data-component="image" src="headphones.png" alt="headphones">
            <button data-node-id="shop.product-headphones.add"
                    data-component="button" data-action="cart.add">Add</button>
          </article>
        </section>
      </section>
    </main>
    """

    report = analyze_component_metadata(html)
    manifest = report.to_manifest()

    assert report.errors == ()
    assert report.warnings == ()
    assert report.addressable_coverage == 1.0
    assert report.component_counts == {
        "button": 1,
        "column": 2,
        "image": 1,
        "row": 1,
        "scroll": 1,
    }
    collection = next(
        item for item in manifest["components"]
        if item["nodeId"] == "shop.products"
    )
    assert collection["arkuiComponent"] == "Column"
    assert collection["uiRole"] == "product-list"
    assert collection["metadata"]["data-repeat"] == "products"
    assert manifest["kind"] == "uibench-component-manifest"
    assert manifest["manifestVersion"] == 1
    assert manifest["screenIrSchemaVersion"] == 2
    assert manifest["summary"]["errors"] == 0
    assert manifest["summary"]["explicitComponents"] == 6
    assert manifest["summary"]["inferredComponents"] == 0
    assert manifest["summary"]["metadataPresent"] is True
    assert manifest["summary"]["exportReadiness"] == "ready"
    assert manifest["summary"]["unsupportedComponents"] == {}


def test_planned_component_blocks_renderer_export() -> None:
    report = analyze_component_metadata("""
      <main data-node-id="page" data-component="grid"></main>
    """)
    manifest = report.to_manifest()

    assert "ARKUI_COMPONENT_NOT_RENDERER_SUPPORTED" in _codes(report)
    assert manifest["summary"]["unsupportedComponents"] == {"grid": 1}
    assert manifest["summary"]["exportReadiness"] == "blocked"
    assert build_screen_ir(report).screen_ir is None


def test_native_html_controls_are_inferred_without_rewriting_html() -> None:
    report = analyze_component_metadata("""
      <button>Save</button>
      <img src="cover.png" alt="cover">
      <input type="checkbox" checked>
      <input type="radio" name="theme">
      <input type="search">
      <input type="text">
      <textarea></textarea>
      <i data-lucide="search"></i>
    """)

    assert [node.component for node in report.nodes] == [
        "button", "image", "checkbox", "radio", "search", "text-input",
        "text-area", "symbol",
    ]
    assert all(node.source == "html" for node in report.nodes)
    assert len(report.warnings) == 14
    assert report.errors == ()
    assert _codes(report) == {
        "ARKUI_COMPONENT_NOT_RENDERER_SUPPORTED",
        "ARKUI_COMPONENT_METADATA_MISSING",
        "ARKUI_NODE_ID_MISSING",
    }


def test_metadata_reports_unknown_duplicate_conflicting_and_missing_values() -> None:
    report = analyze_component_metadata("""
      <main data-node-id="Home" data-component="unknown"></main>
      <section data-node-id="shop.same" data-component="column"></section>
      <section data-node-id="shop.same" data-component="row"></section>
      <button data-node-id="shop.action" data-component="grid">Bad</button>
      <i data-node-id="shop.icon" data-component="symbol"></i>
      <section data-node-id="shop.role" data-component="column"
               data-ui-role="ProductCard"></section>
    """)

    assert {
        "ARKUI_COMPONENT_UNKNOWN",
        "ARKUI_NODE_ID_DUPLICATE",
        "ARKUI_COMPONENT_TAG_CONFLICT",
        "ARKUI_COMPONENT_METADATA_MISSING",
        "ARKUI_UI_ROLE_INVALID",
    } <= _codes(report)
    assert "ARKUI_COMPONENT_NOT_RENDERER_SUPPORTED" in _codes(report)
    assert len(report.errors) == 6


def test_collection_parent_child_constraints_are_enforced() -> None:
    report = analyze_component_metadata("""
      <section data-node-id="shop.list" data-component="list">
        <article data-node-id="shop.bad-grid-item" data-component="grid-item">
        </article>
      </section>
      <article data-node-id="shop.orphan" data-component="list-item"></article>
    """)

    assert "ARKUI_COMPONENT_CHILD_INVALID" in _codes(report)
    assert "ARKUI_COMPONENT_PARENT_INVALID" in _codes(report)
    assert "ARKUI_COMPONENT_NOT_RENDERER_SUPPORTED" in _codes(report)
    assert len(report.errors) == 6


def test_scroll_accepts_one_component_child() -> None:
    valid = analyze_component_metadata("""
      <main data-node-id="page" data-component="scroll">
        <section data-node-id="page.content" data-component="column"></section>
      </main>
    """)
    invalid = analyze_component_metadata("""
      <main data-node-id="page" data-component="scroll">
        <header data-node-id="page.header" data-component="row"></header>
        <section data-node-id="page.content" data-component="column"></section>
      </main>
    """)

    assert "ARKUI_COMPONENT_CHILD_COUNT_EXCEEDED" not in _codes(valid)
    assert "ARKUI_COMPONENT_CHILD_COUNT_EXCEEDED" in _codes(invalid)


def test_plain_legacy_html_remains_valid_and_empty_of_component_metadata() -> None:
    report = analyze_component_metadata("<main><section><p>Hello</p></section></main>")
    assert report.nodes == ()
    assert report.diagnostics == ()
    assert report.addressable_coverage == 0.0
    assert report.export_readiness == "unavailable"


def test_supported_annotations_build_canonical_screen_ir_v2() -> None:
    report = analyze_component_metadata("""
      <main data-node-id="page" data-component="scroll">
        <section data-node-id="page.content" data-component="column">
          <p data-node-id="page.title" data-component="text">
            Hello <span data-node-id="page.title.accent"
                        data-component="span">ArkUI</span>
          </p>
          <img data-node-id="page.cover" data-component="image"
               src="cover.png" alt="Cover">
        </section>
      </main>
    """)
    built = build_screen_ir(report, page_name="Demo Page")

    assert built.readiness == "lossy"
    assert built.screen_ir is not None
    assert built.screen_ir["schemaVersion"] == 2
    assert built.screen_ir["page"] == {"name": "Demo_Page"}
    root = built.screen_ir["ui"]
    assert root["componentName"] == "Scroll"
    content = root["children"][0]
    text = content["children"][0]
    assert text["content"] == "Hello"
    assert text["children"][0]["content"] == "ArkUI"
    assert content["children"][1]["src"] == "cover.png"
    assert {
        item.code for item in built.diagnostics
    } == {
        "UIBENCH_COMPUTED_STYLE_SNAPSHOT_PENDING",
        "UIBENCH_IMAGE_ASSET_NOT_MATERIALIZED",
    }


def test_inferred_symbol_without_canonical_resource_blocks_screen_ir() -> None:
    report = analyze_component_metadata("""
      <main data-node-id="page" data-component="column">
        <i data-node-id="page.icon" data-lucide="search"></i>
      </main>
    """)
    built = build_screen_ir(report)

    assert report.export_readiness == "blocked"
    assert built.screen_ir is None
    assert any(
        item.code == "UIBENCH_ARKUI_SYMBOL_REQUIRED"
        for item in built.diagnostics
    )


def test_component_analyzer_rejects_non_string_input() -> None:
    with pytest.raises(TypeError, match="html must be a string"):
        analyze_component_metadata(None)  # type: ignore[arg-type]


def test_component_tree_depth_is_bounded_before_screen_ir_recursion() -> None:
    from uibench.arkui.metadata import MAX_COMPONENT_TREE_DEPTH

    depth = MAX_COMPONENT_TREE_DEPTH + 1
    html = "".join(
        f'<div data-node-id="page.n{i}" data-component="column">'
        for i in range(depth)
    ) + "content" + "</div>" * depth

    report = analyze_component_metadata(html)
    built = build_screen_ir(report)

    assert "ARKUI_COMPONENT_TREE_DEPTH_EXCEEDED" in _codes(report)
    assert built.readiness == "blocked"
    assert built.screen_ir is None


def test_mobile_prompt_includes_arkui_metadata_contract() -> None:
    assert "ArkUI 可导出组件元数据合约" in SYSTEM_MOBILE
    assert "data-node-id" in SYSTEM_MOBILE
    assert "data-component" in SYSTEM_MOBILE
    assert "data-ui-role" in SYSTEM_MOBILE
    assert "list、list-item、grid、grid-item" in SYSTEM_MOBILE
    assert "还不支持" in SYSTEM_MOBILE
    assert "data-component=\"symbol\"" in SYSTEM_MOBILE
    assert "不能直接复制 Lucide 名称" in SYSTEM_MOBILE
    assert "list, list-item" not in SYSTEM_MOBILE.split("第一版允许值为：", 1)[1].split("。", 1)[0]
    assert MOBILE_ARKUI_METADATA_INSTRUCTIONS in SYSTEM_MOBILE


def test_arkui_metadata_prompt_is_opt_in() -> None:
    plain = prompt_for("mobile").invoke({"prompt": "登录页"}).to_messages()[0].content
    export = prompt_for(
        "mobile", arkui_export_enabled=True
    ).invoke({"prompt": "登录页"}).to_messages()[0].content

    assert "ArkUI 可导出组件元数据合约" not in plain
    assert "ArkUI 可导出组件元数据合约" in export
