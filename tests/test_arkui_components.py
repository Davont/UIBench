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
    repair_arkui_export_html,
    repair_missing_component_node_ids,
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
        "search", "text-input", "checkbox", "radio", "toggle", "tabs",
        "tab-content", "slider",
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
    assert len(report.warnings) == 9
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
    assert "图标和文字并排时，外层必须标为 row" in SYSTEM_MOBILE
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
    allowed = SYSTEM_MOBILE.split("第一版允许值为：", 1)[1].split("。", 1)[0]
    assert all(
        component in allowed
        for component in (
            "toggle", "slider", "text-input", "search", "checkbox", "radio",
            "tabs", "tab-content",
        )
    )
    assert 'type="checkbox" data-component="toggle"' in SYSTEM_MOBILE
    assert "深色模式" in SYSTEM_MOBILE
    assert "设置项的即时开/关不能用 checkbox" in SYSTEM_MOBILE
    assert 'type="range" data-component="slider"' in SYSTEM_MOBILE
    assert 'type="checkbox" data-component="checkbox"' in SYSTEM_MOBILE
    assert 'type="radio" data-component="radio"' in SYSTEM_MOBILE
    assert 'data-component="tabs" data-index="0"' in SYSTEM_MOBILE
    assert 'data-component="tab-content" data-tab-bar="概览"' in SYSTEM_MOBILE


def test_mobile_prompt_stays_compact_and_arkui_safe() -> None:
    assert len(SYSTEM_MOBILE) < 7000
    assert len(MOBILE_ARKUI_METADATA_INSTRUCTIONS) < 4000
    assert "样式全部使用 Tailwind" not in SYSTEM_MOBILE
    assert "用 Tailwind 的 transition / transform / animate-*" not in SYSTEM_MOBILE
    assert all(
        forbidden in MOBILE_ARKUI_METADATA_INSTRUCTIONS
        for forbidden in ("box-shadow", "transform", "align-items:baseline")
    )
    assert "不要再写 `sticky`/`fixed`" in SYSTEM_MOBILE
    assert "开放网络用 `unlock`" in SYSTEM_MOBILE
    assert "语言/翻译用 `languages`" in SYSTEM_MOBILE


def test_native_form_controls_build_screen_ir_props() -> None:
    report = analyze_component_metadata("""
      <main data-node-id="page" data-component="column" class="flex flex-col">
        <input data-node-id="page.toggle" data-component="toggle"
               type="checkbox" checked disabled>
        <input data-node-id="page.slider" data-component="slider"
               type="range" value="42.5" min="0" max="100" step="0.5">
        <input data-node-id="page.name" data-component="text-input"
               type="text" value="Ada" placeholder="姓名" readonly>
        <input data-node-id="page.search" data-component="search"
               type="search" value="ArkUI" placeholder="搜索" disabled>
      </main>
    """)
    built = build_screen_ir(report)

    assert report.errors == ()
    assert report.warnings == ()
    assert built.screen_ir is not None
    children = built.screen_ir["ui"]["children"]
    assert [child["componentName"] for child in children] == [
        "Toggle", "Slider", "TextInput", "Search",
    ]
    assert children[0]["props"] == {"checked": True, "disabled": True}
    assert children[1]["props"] == {
        "value": 42.5, "min": 0, "max": 100, "step": 0.5,
    }
    assert children[2]["props"] == {
        "value": "Ada", "placeholder": "姓名", "readOnly": True,
    }
    assert children[3]["props"] == {
        "value": "ArkUI", "placeholder": "搜索", "disabled": True,
    }


def test_slider_rejects_non_numeric_html_state() -> None:
    report = analyze_component_metadata("""
      <input data-node-id="page.slider" data-component="slider"
             type="range" value="bright">
    """)

    assert "ARKUI_CONTROL_VALUE_INVALID" in _codes(report)
    assert report.export_readiness == "blocked"


def test_selection_controls_and_tabs_build_screen_ir_props() -> None:
    report = analyze_component_metadata("""
      <main data-node-id="page" data-component="column" class="flex flex-col">
        <input data-node-id="page.marketing" data-component="checkbox"
               type="checkbox" name="consents" value="marketing" checked disabled>
        <input data-node-id="page.light" data-component="radio"
               type="radio" name="theme" value="light">
        <input data-node-id="page.dark" data-component="radio"
               type="radio" name="theme" value="dark" checked>
        <button data-node-id="page.save" data-component="button" disabled>保存</button>
        <div data-node-id="page.tabs" data-component="tabs" data-index="1">
          <section data-node-id="page.overview" data-component="tab-content"
                   data-tab-bar="概览">
            <p data-node-id="page.overview.text" data-component="text">第一页</p>
          </section>
          <section data-node-id="page.settings" data-component="tab-content"
                   data-tab-bar="设置"></section>
        </div>
      </main>
    """)
    built = build_screen_ir(report)

    assert report.errors == ()
    assert report.warnings == ()
    assert built.screen_ir is not None
    children = built.screen_ir["ui"]["children"]
    assert children[0]["props"] == {
        "name": "marketing", "group": "consents",
        "checked": True, "disabled": True,
    }
    assert children[1]["props"] == {
        "value": "light", "group": "theme", "checked": False,
    }
    assert children[2]["props"] == {
        "value": "dark", "group": "theme", "checked": True,
    }
    assert children[3]["props"] == {"disabled": True}
    assert children[4]["props"] == {"index": 1}
    assert [item["props"] for item in children[4]["children"]] == [
        {"tabBar": "概览"}, {"tabBar": "设置"},
    ]


def test_tabs_require_valid_index_and_tab_bar() -> None:
    report = analyze_component_metadata("""
      <div data-node-id="page.tabs" data-component="tabs" data-index="1.5">
        <section data-node-id="page.tab" data-component="tab-content"></section>
      </div>
    """)

    assert report.export_readiness == "blocked"
    assert {
        "ARKUI_CONTROL_VALUE_INVALID", "ARKUI_COMPONENT_METADATA_MISSING",
    }.issubset(_codes(report))


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


def test_text_with_symbol_is_deferred_to_the_layout_adapter() -> None:
    report = analyze_component_metadata("""
    <div data-node-id="page" data-component="column" class="flex flex-col">
      <div data-node-id="page.duration" data-component="text"
           class="flex flex-row items-center gap-1">
        <i data-node-id="page.duration.icon" data-component="symbol"
           data-lucide="clock"></i>
        45 分钟
      </div>
    </div>
    """)

    assert not report.errors
    assert not report.warnings
    assert report.export_readiness == "ready"
    assert "ARKUI_COMPONENT_CHILD_INVALID" not in _codes(report)
    assert [item.code for item in report.notices] == [
        "ARKUI_TEXT_SYMBOL_LAYOUT_ADAPTED",
    ]


def test_button_only_text_child_gets_a_stable_generated_node_id() -> None:
    html = """
    <div data-node-id="page" data-component="column">
      <button data-node-id="page.more" data-component="button">
        <span class="label" data-component="text">查看全部</span>
      </button>
    </div>
    """

    repaired = repair_missing_component_node_ids(html)
    report = analyze_component_metadata(repaired)

    assert 'data-node-id="page.more.label"' in repaired
    assert 'data-uibench-generated-node-id="button-label"' in repaired
    assert not report.errors
    assert not report.warnings
    assert report.export_readiness == "ready"
    assert [item.code for item in report.notices] == [
        "ARKUI_NODE_ID_GENERATED",
    ]
    assert repair_missing_component_node_ids(repaired) == repaired


def test_missing_node_id_repair_avoids_collisions() -> None:
    repaired = repair_missing_component_node_ids("""
    <div data-node-id="page" data-component="column">
      <span data-node-id="page.more.label" data-component="text">已占用</span>
      <button data-node-id="page.more" data-component="button">
        <span data-component="text">查看全部</span>
      </button>
    </div>
    """)

    assert 'data-node-id="page.more.label-2"' in repaired


def test_ambiguous_button_children_keep_missing_node_id_error() -> None:
    html = """
    <div data-node-id="page" data-component="column">
      <button data-node-id="page.more" data-component="button">
        <i data-node-id="page.more.icon" data-component="symbol"
           data-lucide="chevron-right"></i>
        <span data-component="text">查看全部</span>
      </button>
    </div>
    """

    repaired = repair_missing_component_node_ids(html)
    report = analyze_component_metadata(repaired)

    assert repaired == html
    assert "ARKUI_NODE_ID_MISSING" in _codes(report)
    assert "ARKUI_NODE_ID_GENERATED" not in _codes(report)
    assert report.export_readiness == "blocked"


def test_unannotated_button_sibling_keeps_missing_node_id_error() -> None:
    html = """
    <div data-node-id="page" data-component="column">
      <button data-node-id="page.more" data-component="button">
        <b>NEW</b>
        <span data-component="text">查看全部</span>
      </button>
    </div>
    """

    repaired = repair_missing_component_node_ids(html)

    assert repaired == html
    assert "ARKUI_NODE_ID_MISSING" in _codes(
        analyze_component_metadata(repaired)
    )


def test_export_repair_annotates_unannotated_layout_wrapper() -> None:
    html = """<div data-component="scroll" data-node-id="display.brightness"
      class="flex flex-col min-h-screen">
      <main class="flex-1 px-4 pt-3 pb-10 space-y-6">
        <section data-component="column" data-node-id="display.brightness.card"
          class="flex flex-col gap-4"></section>
        <footer data-component="column" data-node-id="display.footer"
          class="flex flex-col"></footer>
      </main>
    </div>"""

    repaired = repair_arkui_export_html(html)
    report = analyze_component_metadata(repaired.html)
    by_id = {node.node_id: node for node in report.nodes}
    content = by_id["display.brightness.content"]

    assert repaired.changed is True
    assert [item.code for item in repaired.repairs] == [
        "ARKUI_UNANNOTATED_WRAPPER_REPAIRED",
    ]
    assert 'data-component="column"' in repaired.html
    assert 'data-node-id="display.brightness.content"' in repaired.html
    assert 'data-uibench-generated-node-id="layout-wrapper"' in repaired.html
    assert re.search(
        r'<main[^>]*class="flex-1 px-4 pt-3 pb-10 space-y-6"',
        repaired.html,
    )
    assert report.nodes[content.parent_index].node_id == "display.brightness"
    assert all(
        report.nodes[node.parent_index].node_id == "display.brightness.content"
        for node in report.nodes
        if node.node_id in {"display.brightness.card", "display.footer"}
    )
    assert "ARKUI_CONTENT_WRAPPED_FOR_SINGLE_SLOT" not in _codes(report)

    second = repair_arkui_export_html(repaired.html)
    assert second.changed is False
    assert second.html == repaired.html
    assert second.repairs == ()


def test_export_repair_preserves_existing_flex_wrapper_direction() -> None:
    html = """<div data-component="column" data-node-id="page"
      class="flex flex-col min-h-screen">
      <nav class="flex items-center justify-between">
        <span data-component="text" data-node-id="page.previous">上一页</span>
        <span data-component="text" data-node-id="page.next">下一页</span>
      </nav>
    </div>"""

    repaired = repair_arkui_export_html(html)
    report = analyze_component_metadata(repaired.html)
    wrapper = next(node for node in report.nodes if node.node_id == "page.content")

    assert wrapper.component == "row"
    assert re.search(
        r'<nav[^>]*class="flex items-center justify-between"',
        repaired.html,
    )


def test_export_repair_generates_ids_for_all_component_nodes() -> None:
    html = """<main data-component="column" class="flex flex-col min-h-screen">
      <h1 data-component="text">设置</h1>
      <div data-component="row" class="flex">
        <span data-component="text">显示</span>
      </div>
    </main>"""

    repaired = repair_arkui_export_html(html)
    report = analyze_component_metadata(repaired.html)

    assert [node.node_id for node in report.nodes] == [
        "page",
        "page.text",
        "page.row",
        "page.row.text",
    ]
    assert {item.code for item in repaired.repairs} == {
        "ARKUI_NODE_ID_REPAIRED",
    }
    assert report.export_readiness == "ready"


def test_export_repair_fixes_open_network_icon_and_redundant_sticky_bar() -> None:
    html = """<div data-component="column" class="min-h-screen flex flex-col">
      <header data-component="row"
        class="flex flex-row items-center sticky top-0 z-10">
        <span data-component="text">WLAN</span>
      </header>
      <main data-component="scroll" class="flex-1 overflow-y-auto">
        <div data-component="column" class="flex flex-col">
          <div data-component="row" class="flex flex-row items-center">
            <i data-node-id="wlan.net.cafe.open" data-component="symbol"
               data-lucide="globe"></i>
            <span data-component="text">开放网络 · 2.4 GHz</span>
          </div>
        </div>
      </main>
    </div>"""

    repaired = repair_arkui_export_html(html)
    report = analyze_component_metadata(repaired.html)
    icon = next(
        node for node in report.nodes
        if node.node_id == "wlan.net.cafe.open"
    )

    assert {item.code for item in repaired.repairs}.issuperset({
        "ARKUI_REDUNDANT_STICKY_REMOVED",
        "ARKUI_OPEN_NETWORK_ICON_REPAIRED",
    })
    assert not re.search(r'class="[^"]*\bsticky\b', repaired.html)
    assert 'data-lucide="unlock"' in repaired.html
    assert dict(icon.metadata)["data-symbol"] == "sys.symbol.lock_open"
    assert "ARKUI_SYMBOL_APPROXIMATED" not in _codes(report)

    second = repair_arkui_export_html(repaired.html)
    assert second.changed is False
    assert second.html == repaired.html


def test_export_repair_preserves_meaningful_sticky_and_non_network_globe() -> None:
    html = """<div data-node-id="page" data-component="scroll">
      <div data-node-id="page.content" data-component="column"
           class="flex flex-col">
        <header data-node-id="page.header" data-component="row"
                class="flex flex-row sticky top-0">
          <i data-node-id="page.language" data-component="symbol"
             data-lucide="globe"></i>
          <span data-node-id="page.label" data-component="text">语言</span>
        </header>
      </div>
    </div>"""

    repaired = repair_arkui_export_html(html)

    assert repaired.changed is False
    assert "sticky top-0" in repaired.html
    assert 'data-lucide="globe"' in repaired.html


def test_export_repair_promotes_unique_common_component_root() -> None:
    html = """<!DOCTYPE html><html><body>
      <main class="min-h-screen flex flex-col">
        <header data-node-id="settings.header" data-component="row"
                class="flex flex-row"></header>
        <section data-node-id="settings.content" data-component="column"
                 class="flex flex-col"></section>
      </main>
    </body></html>"""

    repaired = repair_arkui_export_html(html)
    report = analyze_component_metadata(repaired.html)

    assert [item.code for item in repaired.repairs] == [
        "ARKUI_ROOT_WRAPPER_REPAIRED",
    ]
    assert re.search(
        r'<main[^>]*data-node-id="page"[^>]*data-component="column"',
        repaired.html,
    )
    assert report.root_components == 1
    assert report.export_readiness == "ready"

    second = repair_arkui_export_html(repaired.html)
    assert second.changed is False
    assert second.html == repaired.html


def test_export_repair_does_not_opt_legacy_html_into_explicit_mode() -> None:
    html = """<!DOCTYPE html><html><body>
      <main class="min-h-screen flex flex-col">
        <button>保存</button>
        <input type="search" placeholder="搜索">
      </main>
    </body></html>"""

    repaired = repair_arkui_export_html(html)

    assert "ARKUI_ROOT_WRAPPER_REPAIRED" not in {
        item.code for item in repaired.repairs
    }
    assert "data-component" not in repaired.html


def test_export_repair_does_not_create_an_addressable_root_wrapper() -> None:
    html = """<!DOCTYPE html><html><head><title>设置</title></head>
    <body class="dt-bg-canvas">
      <header data-component="column" data-node-id="settings.header"
        class="flex flex-col"></header>
      <main data-component="column" data-node-id="settings.content"
        class="flex flex-col"></main>
    </body></html>"""

    repaired = repair_arkui_export_html(html)
    report = analyze_component_metadata(repaired.html)

    assert repaired.changed is False
    assert repaired.html == html
    assert report.root_components == 2
    assert 'data-component="column"' not in repaired.html.split("<body", 1)[1].split(
        ">", 1,
    )[0]


def test_export_repair_retypes_unambiguous_search_wrapper() -> None:
    html = """<main data-node-id="app" data-component="column"
      class="min-h-screen flex flex-col">
      <div data-node-id="app.search" data-component="search"
           class="flex flex-row">
        <input type="search" data-node-id="app.search.input"
               data-component="search" placeholder="搜索">
      </div>
    </main>"""

    repaired = repair_arkui_export_html(html)
    report = analyze_component_metadata(repaired.html)
    wrapper = next(node for node in report.nodes if node.node_id == "app.search")

    assert [item.code for item in repaired.repairs] == [
        "ARKUI_SEARCH_WRAPPER_REPAIRED",
    ]
    assert wrapper.component == "row"
    assert "ARKUI_COMPONENT_CHILD_COUNT_EXCEEDED" not in _codes(report)
    assert "ARKUI_COMPONENT_CHILD_INVALID" not in _codes(report)
    assert report.export_readiness == "ready"


def test_export_repair_keeps_ambiguous_search_wrapper_blocked() -> None:
    html = """<main data-node-id="app" data-component="column"
      class="min-h-screen flex flex-col">
      <div data-node-id="app.search" data-component="search"
           class="flex flex-row">
        <i data-node-id="app.search.icon" data-component="symbol"
           data-lucide="search"></i>
        <input type="search" data-node-id="app.search.input"
               data-component="search" placeholder="搜索">
      </div>
    </main>"""

    repaired = repair_arkui_export_html(html)
    report = analyze_component_metadata(repaired.html)

    assert "ARKUI_SEARCH_WRAPPER_REPAIRED" not in {
        item.code for item in repaired.repairs
    }
    assert report.export_readiness == "blocked"
    assert "ARKUI_COMPONENT_CHILD_COUNT_EXCEEDED" in _codes(report)


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


def test_native_button_annotated_as_list_item_reads_as_button() -> None:
    """The tag is evidence for what the element is; its entry-ness comes from
    the ListItem that Screen IR generates around plain list children."""
    report = analyze_component_metadata("""
      <section data-node-id="page" data-component="list">
        <button data-node-id="page.entry" data-component="list-item">
          <div data-node-id="page.entry.line" data-component="row"
               class="flex flex-row">
            <span data-node-id="page.entry.label" data-component="text">帮助</span>
          </div>
        </button>
      </section>
    """)
    entry = next(node for node in report.nodes if node.node_id == "page.entry")

    assert not report.errors
    assert not report.warnings
    assert report.export_readiness == "ready"
    assert entry.component == "button"
    assert entry.arkui_component == "Button"
    assert [item.code for item in report.notices] == [
        "ARKUI_LIST_CHILD_WRAPPED_AS_ITEM",
        "ARKUI_LIST_ITEM_READ_AS_NATIVE",
    ]

    built = build_screen_ir(report)
    assert built.screen_ir is not None
    item = built.screen_ir["ui"]["children"][0]
    assert item["componentName"] == "ListItem"
    assert item["meta"]["nodeId"] == "page.entry:item"
    assert item["children"][0]["componentName"] == "Button"


def test_native_button_annotated_as_grid_item_reads_as_button() -> None:
    """A native control directly inside Grid keeps its control semantics;
    Screen IR supplies the GridItem required by ArkUI."""
    report = analyze_component_metadata("""
      <section data-node-id="page" data-component="grid">
        <button data-node-id="page.entry" data-component="grid-item">
          <div data-node-id="page.entry.line" data-component="row"
               class="flex flex-row">
            <span data-node-id="page.entry.label" data-component="text">分类</span>
          </div>
        </button>
      </section>
    """)
    entry = next(node for node in report.nodes if node.node_id == "page.entry")

    assert not report.errors
    assert not report.warnings
    assert report.export_readiness == "ready"
    assert entry.component == "button"
    assert entry.arkui_component == "Button"
    assert [item.code for item in report.notices] == [
        "ARKUI_GRID_CHILD_WRAPPED_AS_ITEM",
        "ARKUI_GRID_ITEM_READ_AS_NATIVE",
    ]

    built = build_screen_ir(report)
    assert built.screen_ir is not None
    item = built.screen_ir["ui"]["children"][0]
    assert item["componentName"] == "GridItem"
    assert item["meta"]["nodeId"] == "page.entry:item"
    assert item["children"][0]["componentName"] == "Button"


def test_grid_item_tag_conflict_outside_grid_still_blocks() -> None:
    report = analyze_component_metadata("""
      <main data-node-id="page" data-component="column" class="flex flex-col">
        <button data-node-id="page.entry" data-component="grid-item">分类</button>
      </main>
    """)

    assert "ARKUI_COMPONENT_TAG_CONFLICT" in _codes(report)
    assert report.export_readiness == "blocked"


def test_other_tag_conflicts_still_block() -> None:
    """Only the list-item reading is uniquely determined; a button annotated
    as an arbitrary container stays contradictory evidence."""
    report = analyze_component_metadata("""
      <main data-node-id="page" data-component="column">
        <button data-node-id="page.box" data-component="row">内容</button>
      </main>
    """)

    assert "ARKUI_COMPONENT_TAG_CONFLICT" in _codes(report)
    assert report.export_readiness == "blocked"


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
