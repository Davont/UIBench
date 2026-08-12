"""Offline tests for the frozen HarmonyOS symbol registry and its resolution."""
import json
import re

import pytest

from uibench.arkui import analyze_component_metadata
from uibench.arkui.symbols import (
    LUCIDE_REGISTRY_FILE,
    LUCIDE_REGISTRY_VERSION,
    LucideRegistryError,
    SYMBOL_REGISTRY_FILE,
    SYMBOL_REGISTRY_VERSION,
    SymbolRegistryError,
    canonical_symbol,
    format_lucide_symbol_table,
    is_known_lucide_icon,
    load_lucide_registry,
    load_symbol_registry,
    lucide_pascal_name,
    lucide_symbol_table,
    normalize_symbol_name,
    pinned_lucide_version,
    resolve_lucide_icon,
    resolve_symbol,
)


def _codes(report) -> set[str]:
    return {item.code for item in report.diagnostics}


def _symbol_metadata(report, node_id: str) -> str:
    node = next(item for item in report.nodes if item.node_id == node_id)
    return dict(node.metadata)["data-symbol"]


def test_frozen_registry_records_its_sdk_provenance() -> None:
    registry = load_symbol_registry()

    assert registry.registry_version == SYMBOL_REGISTRY_VERSION
    assert registry.source["apiVersion"] == 22
    assert registry.source["displayName"] == "HarmonyOS 6.0.2"
    # A syntax pattern cannot tell a real resource from an invented one, so the
    # registry has to be large enough to be the actual SDK catalogue.
    assert len(registry.symbols) > 3000
    assert "chevron_right" in registry.symbols
    assert "ohos_wifi" in registry.symbols


def test_registry_file_is_canonical_and_sorted() -> None:
    payload = json.loads(SYMBOL_REGISTRY_FILE.read_text(encoding="utf-8"))

    assert payload["kind"] == "uibench-harmony-symbol-registry"
    assert payload["symbols"] == sorted(set(payload["symbols"]))
    assert all(
        re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_]*", name)
        for name in payload["symbols"]
    )


def test_every_prompt_mapping_resolves_to_a_real_resource() -> None:
    registry = load_symbol_registry()
    table = lucide_symbol_table()

    assert len(table) > 80
    for lucide_name, symbol_name in table.items():
        assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", lucide_name), lucide_name
        assert symbol_name in registry.symbols, lucide_name
        assert resolve_symbol(f"sys.symbol.{symbol_name}").supported


def test_prompt_table_renders_every_mapping_within_the_line_budget() -> None:
    table = format_lucide_symbol_table(width=78)
    rendered = dict(
        entry.split("=", 1)
        for line in table.splitlines()
        for entry in line.split()
    )

    assert rendered == lucide_symbol_table()
    assert all(len(line) <= 78 for line in table.splitlines())


@pytest.mark.parametrize("spelling", [
    "sys.symbol.chevron_right",
    "sys.symbol.chevron-right",
    "sys.symbol.chevron.right",
    "  sys.symbol.chevron-right  ",
])
def test_separator_spellings_fold_onto_one_canonical_resource(spelling: str) -> None:
    resolution = resolve_symbol(spelling)

    assert resolution.supported
    assert resolution.canonical == "sys.symbol.chevron_right"


def test_case_insensitive_recovery_restores_the_sdk_spelling() -> None:
    assert canonical_symbol("sys.symbol.ai_search") == "sys.symbol.AI_search"


def test_invented_names_are_rejected_with_reviewed_suggestions() -> None:
    resolution = resolve_symbol("sys.symbol.shield")

    assert resolution.status == "unknown"
    assert resolution.canonical is None
    assert "sys.symbol.lock_shield" in resolution.suggestions


def test_lucide_spelling_of_a_mapped_icon_suggests_the_mapped_resource() -> None:
    resolution = resolve_symbol("sys.symbol.help-circle")

    assert resolution.status == "unknown"
    assert resolution.suggestions[0] == "sys.symbol.questionmark_circle"


@pytest.mark.parametrize("spelling", ["more-vertical", "ellipsis-vertical"])
def test_vertical_more_spellings_substitute_the_horizontal_more_glyph(
    spelling: str,
) -> None:
    """HarmonyOS ships no vertical-dots symbol; ``more`` is its affordance.

    The 90° orientation difference is user-visible, so the hit lives in the
    near map and stays flagged approximate instead of claiming fidelity.
    """
    from uibench.arkui.symbols import resolve_lucide_icon_near

    assert not resolve_lucide_icon(spelling).supported
    resolution = resolve_lucide_icon_near(spelling)

    assert resolution.supported
    assert resolution.approximate
    assert resolution.canonical == "sys.symbol.more"


def test_app_scoped_symbols_are_rejected_because_bundles_have_no_icons() -> None:
    resolution = resolve_symbol("app.symbol.chevron-right")

    assert resolution.status == "unsupported-scope"
    assert resolution.suggestions == ("sys.symbol.chevron_right",)


@pytest.mark.parametrize("value", [
    "chevron_right",
    "lucide:bell",
    "sys.symbol.",
    "sys.symbol.9lives!",
    "sys.media.chevron_right",
])
def test_non_system_symbol_spellings_are_malformed(value: str) -> None:
    assert resolve_symbol(value).status == "malformed"


def test_normalization_leaves_canonical_sdk_names_untouched() -> None:
    for name in ("chevron_right", "AI_search", "M_", "ohos_wifi"):
        assert normalize_symbol_name(name) == name


def test_annotated_symbol_is_stored_in_canonical_form() -> None:
    report = analyze_component_metadata("""
    <div data-node-id="page" data-component="column" class="flex flex-col">
      <i data-node-id="page.more" data-component="symbol"
         data-lucide="chevron-right" data-symbol="sys.symbol.chevron-right"></i>
    </div>
    """)

    assert not report.errors
    assert report.export_readiness == "ready"
    assert _symbol_metadata(report, "page.more") == "sys.symbol.chevron_right"


def test_lucide_name_overrides_a_hand_written_symbol_guess() -> None:
    """`sys.symbol.shield` does not exist; the Lucide name maps to one that does."""
    report = analyze_component_metadata("""
    <div data-node-id="page" data-component="column" class="flex flex-col">
      <i data-node-id="page.shield" data-component="symbol"
         data-lucide="shield" data-symbol="sys.symbol.shield"></i>
    </div>
    """)

    assert not report.errors
    assert report.export_readiness == "ready"
    assert _symbol_metadata(report, "page.shield") == "sys.symbol.lock_shield"


def test_app_scoped_guess_is_replaced_by_the_lucide_mapping() -> None:
    """Bundles carry no custom icons, but the Lucide name needs no bundle."""
    report = analyze_component_metadata("""
    <div data-node-id="page" data-component="column" class="flex flex-col">
      <i data-node-id="page.user" data-component="symbol"
         data-lucide="user" data-symbol="app.symbol.person"></i>
    </div>
    """)

    assert not report.errors
    assert _symbol_metadata(report, "page.user") == "sys.symbol.person"


def test_a_symbol_with_no_usable_name_at_all_degrades_to_a_placeholder() -> None:
    report = analyze_component_metadata("""
    <div data-node-id="page" data-component="column" class="flex flex-col">
      <i data-node-id="page.mystery" data-component="symbol"></i>
    </div>
    """)
    diagnostic = next(
        item for item in report.diagnostics
        if item.code == "ARKUI_SYMBOL_UNAVAILABLE"
    )

    assert not report.errors
    assert report.export_readiness == "lossy"
    assert diagnostic.node_id == "page.mystery"
    assert "without data-lucide" in diagnostic.message


def test_registry_rejects_a_mapping_the_sdk_does_not_define(tmp_path) -> None:
    payload = json.loads(SYMBOL_REGISTRY_FILE.read_text(encoding="utf-8"))
    payload["lucideSymbolMap"]["ghost"] = "no_such_symbol"
    broken = tmp_path / "symbol_registry.json"
    broken.write_text(json.dumps(payload), encoding="utf-8")

    load_symbol_registry.cache_clear()
    import uibench.arkui.symbols as symbols

    original = symbols.SYMBOL_REGISTRY_FILE
    symbols.SYMBOL_REGISTRY_FILE = broken
    try:
        with pytest.raises(SymbolRegistryError, match="no_such_symbol"):
            load_symbol_registry()
    finally:
        symbols.SYMBOL_REGISTRY_FILE = original
        load_symbol_registry.cache_clear()


def test_frozen_lucide_registry_records_its_package_provenance() -> None:
    registry = load_lucide_registry()

    assert registry.registry_version == LUCIDE_REGISTRY_VERSION
    assert registry.source["package"] == "lucide"
    assert pinned_lucide_version() == str(registry.source["version"])
    # The catalogue must be the actual package inventory, not a curated subset,
    # otherwise real icons would be reported as unknown.
    assert len(registry.icons) > 1500
    assert "chevron-right" in registry.icons
    assert registry.aliases
    assert set(registry.aliases.values()) <= registry.icons


def test_lucide_registry_file_is_canonical_and_sorted() -> None:
    payload = json.loads(LUCIDE_REGISTRY_FILE.read_text(encoding="utf-8"))

    assert payload["kind"] == "uibench-lucide-icon-registry"
    assert payload["icons"] == sorted(set(payload["icons"]))
    name_re = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
    assert all(name_re.fullmatch(name) for name in payload["icons"])
    assert list(payload["aliases"]) == sorted(payload["aliases"])
    assert all(name_re.fullmatch(name) for name in payload["aliases"])


def test_lucide_lookup_matches_the_cdn_pascal_folding() -> None:
    """The browser folds data-lucide via toPascalCase; validation must too."""
    assert lucide_pascal_name("arrow-down-0-1") == "ArrowDown01"
    assert lucide_pascal_name("axis-3d") == "Axis3d"
    # Both spellings reach the same PascalCase key, so both render.
    assert is_known_lucide_icon("arrow-down-0-1")
    assert is_known_lucide_icon("arrow-down-01")
    # Deprecated aliases stay renderable in the pinned CDN build.
    assert is_known_lucide_icon("help-circle")
    assert not is_known_lucide_icon("no-such-icon")
    assert not is_known_lucide_icon("")


def test_every_map_key_is_a_renderable_lucide_name() -> None:
    """A mapping for a name Lucide cannot render would never be exercised."""
    for lucide_name in lucide_symbol_table():
        assert is_known_lucide_icon(lucide_name), lucide_name


@pytest.mark.parametrize(("lucide_name", "expected"), [
    ("palette", "sys.symbol.paintpalette"),
    ("map-pin", "sys.symbol.local"),
    ("menu", "sys.symbol.line_3_horizontal"),
    ("history", "sys.symbol.arrow_counterclockwise_clock"),
    ("thumbs-down", "sys.symbol.hand_thumbsdown"),
    ("battery-full", "sys.symbol.battery_100percent"),
])
def test_curated_additions_resolve_to_their_reviewed_resources(
    lucide_name: str, expected: str,
) -> None:
    resolution = resolve_lucide_icon(lucide_name)

    assert resolution.supported
    assert resolution.canonical == expected


def test_lucide_registry_rejects_an_alias_to_an_unknown_icon(tmp_path) -> None:
    payload = json.loads(LUCIDE_REGISTRY_FILE.read_text(encoding="utf-8"))
    payload["aliases"]["not-a-real-alias"] = "no-such-icon"
    broken = tmp_path / "lucide_registry.json"
    broken.write_text(json.dumps(payload), encoding="utf-8")

    load_lucide_registry.cache_clear()
    import uibench.arkui.symbols as symbols

    original = symbols.LUCIDE_REGISTRY_FILE
    symbols.LUCIDE_REGISTRY_FILE = broken
    try:
        with pytest.raises(LucideRegistryError, match="no-such-icon"):
            load_lucide_registry()
    finally:
        symbols.LUCIDE_REGISTRY_FILE = original
        load_lucide_registry.cache_clear()


def test_coverage_classification_follows_the_real_resolution_path() -> None:
    from tools.lucide_coverage import classify_lucide_name

    assert classify_lucide_name("search")["status"] == "reviewed"
    assert classify_lucide_name("handshake")["status"] == "direct"
    globe = classify_lucide_name("globe")
    assert globe["status"] == "near"
    assert globe["symbol"] == "sys.symbol.worldclock"
    banknote = classify_lucide_name("banknote")
    assert banknote["status"] == "miss-none"
    assert banknote["symbol"] is None


def test_coverage_summary_reports_both_name_groups() -> None:
    from tools.lucide_coverage import format_summary

    summary = format_summary({
        "lucideVersion": "1.31.0",
        "reviewedMappings": 2,
        "icons": {
            "total": 4, "covered": 2, "coverage": 0.5,
            "counts": {
                "reviewed": 1, "direct": 1, "near": 0,
                "miss-suggested": 1, "miss-none": 1,
            },
            "entries": [],
        },
        "aliases": {
            "total": 1, "covered": 1, "coverage": 1.0,
            "counts": {
                "reviewed": 1, "direct": 0, "near": 0,
                "miss-suggested": 0, "miss-none": 0,
            },
            "entries": [],
        },
    })

    assert "lucide 1.31.0" in summary
    assert "icons: 2/4 covered (50.0%)" in summary
    assert "aliases: 1/1 covered (100.0%)" in summary


def test_near_map_entries_are_renderable_and_not_shadowed() -> None:
    """Every近似 entry must name a real resource for a real unresolved icon."""
    from uibench.arkui.symbols import lucide_symbol_near_table

    registry = load_symbol_registry()
    exact = lucide_symbol_table()
    near = lucide_symbol_near_table()

    assert near
    for lucide_name, symbol_name in near.items():
        assert is_known_lucide_icon(lucide_name), lucide_name
        assert symbol_name in registry.symbols, lucide_name
        assert lucide_name not in exact, lucide_name
        assert not resolve_lucide_icon(lucide_name).supported, lucide_name


def test_near_resolution_is_flagged_approximate() -> None:
    from uibench.arkui.symbols import resolve_lucide_icon_near

    resolution = resolve_lucide_icon_near("globe")
    assert resolution.supported
    assert resolution.approximate
    assert resolution.canonical == "sys.symbol.worldclock"
    # Exact resolution stays exact and never claims an approximation.
    assert not resolve_lucide_icon("globe").supported
    assert not resolve_lucide_icon("bell").approximate
    assert resolve_lucide_icon_near("banknote").status == "unknown"


def test_missing_icon_with_a_near_entry_substitutes_with_a_warning() -> None:
    report = analyze_component_metadata("""
    <div data-node-id="page" data-component="column" class="flex flex-col">
      <i data-node-id="page.globe" data-component="symbol" data-lucide="globe"></i>
    </div>
    """)
    node = next(item for item in report.nodes if item.node_id == "page.globe")
    diagnostic = next(
        item for item in report.diagnostics
        if item.code == "ARKUI_SYMBOL_APPROXIMATED"
    )

    assert not report.errors
    # A similar glyph is not the captured glyph, so the export stays lossy.
    assert report.export_readiness == "lossy"
    assert node.arkui_component == "SymbolGlyph"
    assert _symbol_metadata(report, "page.globe") == "sys.symbol.worldclock"
    assert diagnostic.severity == "warning"
    assert "worldclock" in diagnostic.message


def test_declared_symbol_beats_the_near_substitute() -> None:
    """An explicitly declared valid resource is exact; the near tier is not."""
    report = analyze_component_metadata("""
    <div data-node-id="page" data-component="column" class="flex flex-col">
      <i data-node-id="page.icon" data-component="symbol" data-lucide="globe"
         data-symbol="sys.symbol.translate"></i>
    </div>
    """)

    assert _symbol_metadata(report, "page.icon") == "sys.symbol.translate"
    assert "ARKUI_SYMBOL_APPROXIMATED" not in {
        item.code for item in report.diagnostics
    }


def test_unknown_lucide_name_never_invents_a_matching_harmony_symbol() -> None:
    """``data-lucide="person"`` renders nothing in the pinned Lucide build.

    HarmonyOS happening to define a symbol of the same name (or the model
    declaring one) must not conjure an icon the captured page never showed;
    the node degrades to the same-size placeholder with a warning.
    """
    assert not is_known_lucide_icon("person")
    report = analyze_component_metadata("""
    <div data-node-id="page" data-component="column" class="flex flex-col">
      <i data-node-id="page.icon" data-component="symbol"
         data-lucide="person" data-symbol="sys.symbol.person"></i>
    </div>
    """)
    node = next(item for item in report.nodes if item.node_id == "page.icon")
    diagnostic = next(
        item for item in report.diagnostics
        if item.code == "ARKUI_LUCIDE_ICON_UNKNOWN"
    )

    assert not report.errors
    assert report.export_readiness == "lossy"
    assert node.arkui_component == "Column"
    assert "data-symbol" not in dict(node.metadata)
    assert diagnostic.severity == "warning"
    assert "person" in diagnostic.message


def _load_registry_export_tool():
    import importlib.util
    from pathlib import Path

    spec = importlib.util.spec_from_file_location(
        "export_symbol_registry_tool",
        Path(__file__).resolve().parents[1] / "tools/export-symbol-registry.py",
    )
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    return tool


def _fake_deveco_studio(tmp_path, symbol_names):
    studio = tmp_path / "DevEco-Studio.app"
    toolchains = studio / "Contents/sdk/default/openharmony/toolchains"
    toolchains.mkdir(parents=True)
    (toolchains / "id_defined.json").write_text(json.dumps({
        "record": [
            {"type": "symbol", "name": name} for name in symbol_names
        ],
    }), encoding="utf-8")
    (studio / "Contents/sdk/default/sdk-pkg.json").write_text(json.dumps({
        "data": {
            "displayName": "HarmonyOS 6.0.2", "apiVersion": "22",
            "version": "6.0.2", "releaseType": "Release",
        },
    }), encoding="utf-8")
    return studio


def test_registry_export_tool_preserves_both_curated_maps(tmp_path) -> None:
    """An SDK refresh must not silently drop the hand-reviewed mappings."""
    import shutil

    tool = _load_registry_export_tool()
    current = json.loads(SYMBOL_REGISTRY_FILE.read_text(encoding="utf-8"))
    studio = _fake_deveco_studio(tmp_path, current["symbols"])
    output = tmp_path / "symbol_registry.json"
    shutil.copyfile(SYMBOL_REGISTRY_FILE, output)

    result = tool.export_symbol_registry(studio, output)
    regenerated = json.loads(output.read_text(encoding="utf-8"))

    assert result["ok"] is True
    assert regenerated["lucideSymbolMap"] == current["lucideSymbolMap"]
    assert regenerated["lucideSymbolNearMap"] == current["lucideSymbolNearMap"]


def test_registry_export_tool_refuses_a_near_key_the_new_sdk_resolves_directly(
    tmp_path,
) -> None:
    """A refresh must fail loudly instead of persisting an unloadable file.

    When a new SDK gains a symbol named like a near-map key (e.g. ``globe``),
    that entry now resolves by direct lookup and ``load_symbol_registry``
    refuses the whole registry. The tool runs the same parser before writing,
    so the refusal happens up front and the previous registry stays intact.
    """
    import shutil

    tool = _load_registry_export_tool()
    current = json.loads(SYMBOL_REGISTRY_FILE.read_text(encoding="utf-8"))
    assert "globe" in current["lucideSymbolNearMap"]
    assert "globe" not in current["symbols"]
    studio = _fake_deveco_studio(
        tmp_path, sorted([*current["symbols"], "globe"]),
    )
    output = tmp_path / "symbol_registry.json"
    shutil.copyfile(SYMBOL_REGISTRY_FILE, output)

    with pytest.raises(SymbolRegistryError, match="direct lookup"):
        tool.export_symbol_registry(studio, output)

    assert json.loads(output.read_text(encoding="utf-8")) == current


def test_registry_export_tool_refuses_a_curated_value_the_new_sdk_dropped(
    tmp_path,
) -> None:
    """Curated values must still point at symbols the new SDK defines."""
    import shutil

    tool = _load_registry_export_tool()
    current = json.loads(SYMBOL_REGISTRY_FILE.read_text(encoding="utf-8"))
    survivors = [
        name for name in current["symbols"] if name != "worldclock"
    ]
    assert "worldclock" in current["lucideSymbolNearMap"].values()
    studio = _fake_deveco_studio(tmp_path, survivors)
    output = tmp_path / "symbol_registry.json"
    shutil.copyfile(SYMBOL_REGISTRY_FILE, output)

    with pytest.raises(SymbolRegistryError, match="worldclock"):
        tool.export_symbol_registry(studio, output)

    assert json.loads(output.read_text(encoding="utf-8")) == current


def test_registry_rejects_a_shadowed_near_entry(tmp_path) -> None:
    payload = json.loads(SYMBOL_REGISTRY_FILE.read_text(encoding="utf-8"))
    payload["lucideSymbolNearMap"]["handshake"] = "handshake"
    broken = tmp_path / "symbol_registry.json"
    broken.write_text(json.dumps(payload), encoding="utf-8")

    load_symbol_registry.cache_clear()
    import uibench.arkui.symbols as symbols

    original = symbols.SYMBOL_REGISTRY_FILE
    symbols.SYMBOL_REGISTRY_FILE = broken
    try:
        with pytest.raises(SymbolRegistryError, match="direct lookup"):
            load_symbol_registry()
    finally:
        symbols.SYMBOL_REGISTRY_FILE = original
        load_symbol_registry.cache_clear()
