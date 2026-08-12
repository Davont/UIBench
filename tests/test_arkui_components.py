"""Offline tests for the ArkUI component registry and HTML metadata contract."""
import itertools
import json
import re
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
    # grid ships alongside list: exportable and offered to the model, so the
    # registry phase matches its real availability.
    assert "grid" in registry.keys_for_phases("P0")
    assert "tabs" in registry.keys_for_phases("P1")
    assert "water-flow" in registry.keys_for_phases("P2")
    assert registry.renderer_keys() == (
        "column", "row", "stack", "scroll", "text", "span", "image",
        "symbol", "divider", "button", "list", "list-item", "grid", "grid-item",
    )
    assert registry.components["list"].allowed_children == frozenset({"list-item"})
    assert registry.components["list-item"].max_component_children == 1
    assert registry.components["column"].min_api_version == 7
    assert registry.components["symbol"].min_api_version == 11
    assert registry.components["image"].max_component_children == 0
    assert registry.components["grid"].renderer_supported is True
    assert registry.components["grid"].allowed_children == frozenset({"grid-item"})
    assert registry.components["grid-item"].max_component_children == 1
    assert registry.components["swiper"].renderer_supported is False


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
      <main data-node-id="page" data-component="swiper"></main>
    """)
    manifest = report.to_manifest()

    assert "ARKUI_COMPONENT_NOT_RENDERER_SUPPORTED" in _codes(report)
    assert manifest["summary"]["unsupportedComponents"] == {"swiper": 1}
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
    assert len(report.warnings) == 13
    assert report.errors == ()
    assert _codes(report) == {
        "ARKUI_COMPONENT_NOT_RENDERER_SUPPORTED",
        "ARKUI_NODE_ID_MISSING",
    }
    # data-lucide alone is enough; the export resolves the resource itself.
    symbol = report.nodes[-1]
    assert dict(symbol.metadata)["data-symbol"] == "sys.symbol.magnifyingglass"


def test_metadata_reports_unknown_duplicate_conflicting_and_missing_values() -> None:
    report = analyze_component_metadata("""
      <main data-node-id="Home" data-component="unknown"></main>
      <section data-node-id="shop.same" data-component="column"></section>
      <section data-node-id="shop.same" data-component="row"></section>
      <button data-node-id="shop.action" data-component="swiper">Bad</button>
      <i data-node-id="shop.icon" data-component="symbol"></i>
      <section data-node-id="shop.role" data-component="column"
               data-ui-role="ProductCard"></section>
    """)

    assert {
        "ARKUI_COMPONENT_UNKNOWN",
        "ARKUI_NODE_ID_DUPLICATE",
        "ARKUI_COMPONENT_TAG_CONFLICT",
        "ARKUI_SYMBOL_UNAVAILABLE",
        "ARKUI_UI_ROLE_INVALID",
    } <= _codes(report)
    assert "ARKUI_COMPONENT_NOT_RENDERER_SUPPORTED" in _codes(report)
    # The unusable symbol is a placeholder warning now, not a sixth error.
    assert len(report.errors) == 5


def test_collection_parent_child_constraints_are_enforced() -> None:
    report = analyze_component_metadata("""
      <section data-node-id="shop.list" data-component="list">
        <article data-node-id="shop.bad-grid-item" data-component="grid-item">
        </article>
      </section>
    """)

    # A grid-item declares its own legal parents, so a list cannot absorb it
    # into a generated ListItem the way it absorbs plain entries.
    assert "ARKUI_COMPONENT_CHILD_INVALID" in _codes(report)
    assert "ARKUI_COMPONENT_PARENT_INVALID" in _codes(report)
    assert "ARKUI_LIST_CHILD_WRAPPED_AS_ITEM" not in _codes(report)
    assert len(report.errors) == 2


def test_single_slot_container_wraps_extra_children_instead_of_failing() -> None:
    valid = analyze_component_metadata("""
      <main data-node-id="page" data-component="scroll">
        <section data-node-id="page.content" data-component="column"></section>
      </main>
    """)
    crowded = analyze_component_metadata("""
      <main data-node-id="page" data-component="scroll">
        <header data-node-id="page.header" data-component="row"></header>
        <section data-node-id="page.content" data-component="column"></section>
      </main>
    """)

    assert _codes(valid) == set()
    assert not crowded.errors
    assert not crowded.warnings
    # Wrapping is structural, not lossy: the rendered result is unchanged.
    assert crowded.export_readiness == "ready"
    assert [item.code for item in crowded.notices] == [
        "ARKUI_CONTENT_WRAPPED_FOR_SINGLE_SLOT",
    ]


def test_leaf_component_holding_children_is_still_an_error() -> None:
    report = analyze_component_metadata("""
      <main data-node-id="page" data-component="column">
        <div data-node-id="page.rule" data-component="divider">
          <span data-node-id="page.rule.label" data-component="text">或</span>
        </div>
      </main>
    """)

    assert "ARKUI_COMPONENT_CHILD_COUNT_EXCEEDED" in _codes(report)
    assert "ARKUI_CONTENT_WRAPPED_FOR_SINGLE_SLOT" not in _codes(report)
    assert report.export_readiness == "blocked"


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
    # ArkUI's Text renders either its own content or its Span children, so
    # mixed rich text becomes ordered Spans: the parent fragment must not be
    # silently dropped in favour of the styled span.
    assert "content" not in text
    assert [child["content"] for child in text["children"]] == [
        "Hello ", "ArkUI",
    ]
    assert text["children"][0]["meta"]["nodeId"] == "page.title:run0"
    assert content["children"][1]["src"] == "cover.png"
    assert {
        item.code for item in built.diagnostics
    } == {
        "UIBENCH_COMPUTED_STYLE_SNAPSHOT_PENDING",
        "UIBENCH_IMAGE_ASSET_NOT_MATERIALIZED",
    }


def test_inferred_symbol_resolves_its_resource_from_the_lucide_name() -> None:
    """A bare Lucide icon carries everything the export needs."""
    report = analyze_component_metadata("""
      <main data-node-id="page" data-component="column">
        <i data-node-id="page.icon" data-lucide="search"></i>
      </main>
    """)
    built = build_screen_ir(report)

    assert report.export_readiness == "ready"
    assert built.screen_ir is not None
    assert built.screen_ir["ui"]["children"][0]["props"] == {
        "symbol": "sys.symbol.magnifyingglass",
    }


def test_icon_harmonyos_has_no_resource_for_degrades_to_a_placeholder() -> None:
    """A missing glyph must not cost the page its whole export."""
    report = analyze_component_metadata("""
      <main data-node-id="page" data-component="column">
        <i data-node-id="page.icon" data-component="symbol"
           data-lucide="air-vent"></i>
      </main>
    """)
    placeholder = next(
        node for node in report.nodes if node.node_id == "page.icon"
    )

    assert not report.errors
    assert report.export_readiness == "lossy"
    assert "ARKUI_SYMBOL_UNAVAILABLE" in _codes(report)
    assert placeholder.arkui_component == "Column"


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
    # The unsupported list is derived from the pinned renderer contract, so a
    # vendor upgrade can never advertise a component as allowed and unsupported.
    registry = load_component_registry()
    unsupported = SYSTEM_MOBILE.split("还不支持这些组件：", 1)[1].split("。", 1)[0]
    assert unsupported == "、".join(registry.planned_keys())
    assert not set(registry.renderer_keys()) & set(unsupported.split("、"))
    assert "list 只能包 list-item，list-item 只能出现在 list 内" in SYSTEM_MOBILE
    # A horizontal list is exportable, so the prompt must not ask for vertical.
    assert "纵向列表和横滑列表都适用" in SYSTEM_MOBILE
    assert "data-component=\"symbol\"" in SYSTEM_MOBILE
    # The icon mapping lives in the engine, not in the contract.
    assert "不需要写 `data-symbol`" in SYSTEM_MOBILE
    assert "sys.symbol." not in SYSTEM_MOBILE.split("Lucide `<i>` 标为", 1)[1]
    assert "不要因为 HTML 标签恰好叫 `<span>` 就标成" in SYSTEM_MOBILE
    assert "必须实际使用 `flex flex-col`" in SYSTEM_MOBILE
    assert "DOM 直接父节点必须就是组件元数据中的父节点" in SYSTEM_MOBILE
    assert "不要在两个已标注组件之间" in SYSTEM_MOBILE
    assert "必须实际使用 `flex flex-row`" in SYSTEM_MOBILE
    assert "标注必须与浏览器最终 computed layout 一致" in SYSTEM_MOBILE
    assert "column 必须得到 `display: flex`、`flex-direction: column`" in SYSTEM_MOBILE
    assert "row 必须得到 `display: flex`、" in SYSTEM_MOBILE
    assert "`flex-direction: row`" in SYSTEM_MOBILE
    assert "list, list-item" in SYSTEM_MOBILE.split("第一版允许值为：", 1)[1].split("。", 1)[0]
    assert MOBILE_ARKUI_METADATA_INSTRUCTIONS in SYSTEM_MOBILE


def test_prompts_pin_the_frozen_lucide_version() -> None:
    """Pages must load the audited Lucide build, not whatever `latest` is."""
    from uibench.arkui.symbols import pinned_lucide_version
    from uibench.pc import SYSTEM_PC

    pinned = f"https://unpkg.com/lucide@{pinned_lucide_version()}"
    for prompt in (SYSTEM_MOBILE, SYSTEM_PC):
        assert pinned in prompt
        assert "lucide@latest" not in prompt
        assert "__LUCIDE_VERSION__" not in prompt


def test_button_example_in_the_prompt_actually_passes_validation() -> None:
    """The worked example must be copyable; a broken one teaches the failure."""
    start = MOBILE_ARKUI_METADATA_INSTRUCTIONS.index("  <button data-node-id=")
    end = MOBILE_ARKUI_METADATA_INSTRUCTIONS.index("  </button>", start)
    example = "\n".join(
        line[2:]
        for line in MOBILE_ARKUI_METADATA_INSTRUCTIONS[start:end].splitlines()
    ) + "</button>"
    report = analyze_component_metadata(
        '<div data-node-id="page" data-component="column" class="flex flex-col">'
        + example
        + "</div>"
    )

    assert not report.errors
    assert report.export_readiness == "ready"
    assert report.component_counts == {
        "button": 1, "column": 1, "row": 1, "symbol": 2, "text": 1,
    }


def test_span_outside_text_is_exported_as_text_with_a_notice() -> None:
    """Span has no legal form outside Text, so the node is kept as Text."""
    report = analyze_component_metadata("""
    <div data-node-id="page" data-component="row" class="flex flex-row">
      <span data-node-id="page.label" data-component="text">消息通知</span>
      <span data-node-id="page.badge" data-component="span">已开启</span>
    </div>
    """)
    promoted = next(item for item in report.nodes if item.node_id == "page.badge")

    assert not report.errors
    assert not report.warnings
    assert report.export_readiness == "ready"
    assert [item.code for item in report.notices] == [
        "ARKUI_SPAN_PROMOTED_TO_TEXT",
    ]
    assert promoted.component == "text"
    assert promoted.arkui_component == "Text"
    assert promoted.text_content == "已开启"


def test_span_inside_text_keeps_its_rich_text_meaning() -> None:
    report = analyze_component_metadata("""
    <div data-node-id="page" data-component="column" class="flex flex-col">
      <p data-node-id="page.line" data-component="text">共 <span
         data-node-id="page.line.count" data-component="span">3</span> 台设备</p>
    </div>
    """)

    assert report.export_readiness == "ready"
    assert "ARKUI_SPAN_PROMOTED_TO_TEXT" not in _codes(report)
    assert report.component_counts == {"column": 1, "span": 1, "text": 1}


def test_empty_span_inside_text_still_blocks_export() -> None:
    report = analyze_component_metadata("""
    <div data-node-id="page" data-component="column" class="flex flex-col">
      <p data-node-id="page.line" data-component="text"><span
         data-node-id="page.line.gap" data-component="span"></span></p>
    </div>
    """)

    assert "ARKUI_SPAN_CONTENT_MISSING" in _codes(report)
    assert report.export_readiness == "blocked"


def test_promoted_span_reaches_screen_ir_as_a_text_component() -> None:
    report = analyze_component_metadata("""
    <div data-node-id="page" data-component="row" class="flex flex-row">
      <span data-node-id="page.value" data-component="span">128.4 MB</span>
    </div>
    """)
    built = build_screen_ir(report)

    assert built.screen_ir is not None
    assert built.screen_ir["ui"]["children"][0]["componentName"] == "Text"
    assert built.screen_ir["ui"]["children"][0]["content"] == "128.4 MB"


_LIST_WITH_PLAIN_ENTRIES = """
  <section data-node-id="page" data-component="list">
    <div data-node-id="page.header" data-component="row"
         class="flex flex-row"></div>
    <button data-node-id="page.help" data-component="button">帮助中心</button>
    <div data-node-id="page.about" data-component="list-item">
      <button data-node-id="page.about.btn" data-component="button">关于</button>
    </div>
  </section>
"""


def test_plain_list_entries_are_wrapped_into_list_items_with_a_notice() -> None:
    """A List only holds ListItems, so a plain entry can only mean one item."""
    report = analyze_component_metadata(_LIST_WITH_PLAIN_ENTRIES)

    assert not report.errors
    assert not report.warnings
    # Wrapping is structural, not lossy: the rendered result is unchanged.
    assert report.export_readiness == "ready"
    assert [item.code for item in report.notices] == [
        "ARKUI_LIST_CHILD_WRAPPED_AS_ITEM",
        "ARKUI_LIST_CHILD_WRAPPED_AS_ITEM",
    ]
    assert [item.node_id for item in report.notices] == [
        "page.header", "page.help",
    ]
    # The annotations themselves are kept: the wrapper is a Screen IR affair.
    assert report.component_counts == {
        "button": 2, "list": 1, "list-item": 1, "row": 1,
    }


def test_wrapped_list_entries_reach_screen_ir_inside_generated_items() -> None:
    report = analyze_component_metadata(_LIST_WITH_PLAIN_ENTRIES)
    built = build_screen_ir(report)

    assert built.screen_ir is not None
    root = built.screen_ir["ui"]
    assert root["componentName"] == "List"
    children = root["children"]
    assert [child["componentName"] for child in children] == ["ListItem"] * 3
    generated = children[0]
    assert generated["meta"]["nodeId"] == "page.header:item"
    assert generated["styles"] == {"width": "100%"}
    assert generated["children"][0]["meta"]["nodeId"] == "page.header"
    assert children[1]["children"][0]["content"] == "帮助中心"
    # The authored list-item flows through untouched.
    assert children[2]["meta"]["nodeId"] == "page.about"


def test_list_item_outside_a_list_is_exported_as_column_with_a_notice() -> None:
    """ListItem has no legal form outside List, so the container reading wins."""
    report = analyze_component_metadata("""
    <div data-node-id="page" data-component="column" class="flex flex-col">
      <div data-node-id="page.card" data-component="list-item">
        <p data-node-id="page.card.text" data-component="text">内容</p>
      </div>
    </div>
    """)
    demoted = next(node for node in report.nodes if node.node_id == "page.card")

    assert not report.errors
    assert not report.warnings
    assert report.export_readiness == "ready"
    assert [item.code for item in report.notices] == [
        "ARKUI_LIST_ITEM_PROMOTED_TO_COLUMN",
    ]
    assert demoted.component == "column"
    assert demoted.arkui_component == "Column"


def _prompt_fragment(marker: str, occurrence: int = 0) -> str:
    """Extract one inline example from the metadata contract."""
    lines = [
        line.strip()[len(marker):].strip()
        for line in MOBILE_ARKUI_METADATA_INSTRUCTIONS.splitlines()
        if line.strip().startswith(marker)
    ]
    counter = itertools.count()
    return re.sub(
        r"(?=data-component=)",
        lambda _: f'data-node-id="n{next(counter)}" ',
        lines[occurrence],
    )


def _analyze_fragment(fragment: str):
    return analyze_component_metadata(
        '<div data-node-id="page" data-component="column" class="flex flex-col">'
        + fragment
        + "</div>"
    )


def test_span_counter_example_in_the_prompt_really_is_flagged() -> None:
    report = _analyze_fragment(_prompt_fragment("错误"))

    assert "ARKUI_SPAN_PROMOTED_TO_TEXT" in _codes(report)
    assert report.export_readiness == "ready"


@pytest.mark.parametrize("occurrence", [0, 1])
def test_span_examples_in_the_prompt_really_are_accepted(occurrence: int) -> None:
    report = _analyze_fragment(_prompt_fragment("正确", occurrence))

    assert not report.errors
    assert report.export_readiness == "ready"


def test_arkui_metadata_prompt_is_opt_in() -> None:
    plain = prompt_for("mobile").invoke({"prompt": "登录页"}).to_messages()[0].content
    export = prompt_for(
        "mobile", arkui_export_enabled=True
    ).invoke({"prompt": "登录页"}).to_messages()[0].content

    assert "ArkUI 可导出组件元数据合约" not in plain
    assert "ArkUI 可导出组件元数据合约" in export
