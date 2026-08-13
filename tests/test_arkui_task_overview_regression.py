"""Regression coverage for the task-overview HTML reported by the user."""
from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path

from tools.task_overview_fixture import (
    build_task_overview_snapshot,
    load_task_overview_html,
)
from uibench.arkui.exporter import export_annotated_html
from uibench.arkui.snapshot import BrowserSnapshot


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPORT_TOOL = PROJECT_ROOT / "tools/export-task-overview-fixture.py"


class _ClassCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.body_classes: set[str] = set()
        self.node_classes: dict[str, tuple[str, set[str]]] = {}

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        attributes = dict(attrs)
        classes = set((attributes.get("class") or "").split())
        if tag == "body":
            self.body_classes = classes
        node_id = attributes.get("data-node-id")
        component = attributes.get("data-component")
        if node_id and component:
            self.node_classes[node_id] = (component, classes)


def _screen_ir_by_id(root: dict[str, object]) -> dict[str, dict[str, object]]:
    indexed: dict[str, dict[str, object]] = {}
    pending = [root]
    while pending:
        node = pending.pop()
        meta = node["meta"]
        assert isinstance(meta, dict)
        indexed[str(meta["nodeId"])] = node
        children = node.get("children", [])
        assert isinstance(children, list)
        pending.extend(children)
    return indexed


def test_task_overview_exports_ready_with_truthful_layout_and_styles() -> None:
    html = load_task_overview_html()
    classes = _ClassCollector()
    classes.feed(html)

    assert {"dt-bg-canvas", "dt-text-primary", "dt-font"} <= classes.body_classes
    for node_id, (component, node_classes) in classes.node_classes.items():
        if component == "column":
            assert {"flex", "flex-col"} <= node_classes, node_id
        elif component == "row":
            assert {"flex", "flex-row"} <= node_classes, node_id

    # The browser capture promotes the body canvas onto the one annotated root;
    # the root itself deliberately has no dt-bg-canvas class in the source HTML.
    assert "dt-bg-canvas" not in classes.node_classes["task-overview"][1]
    snapshot = build_task_overview_snapshot(html)
    result = export_annotated_html(
        html,
        page_name="TaskOverview",
        snapshot=snapshot,
        require_snapshot=True,
    )

    assert result["quality"] == {
        "readiness": "ready",
        "errors": 0,
        "warnings": 0,
        "notices": 0,
        "componentCounts": {
            "Row": 5,
            "Column": 10,
            "Stack": 0,
            "Scroll": 0,
            "Text": 16,
            "Span": 0,
            "Image": 0,
            "SymbolGlyph": 0,
            "Divider": 3,
            "Button": 2,
            "List": 0,
            "ListItem": 0,
            "Grid": 0,
            "GridItem": 0,
            "Toggle": 0,
            "Slider": 0,
            "TextInput": 0,
            "Search": 0,
            "Checkbox": 0,
            "Radio": 0,
            "Tabs": 0,
            "TabContent": 0,
        },
    }
    root = result["screenIr"]["ui"]
    nodes = _screen_ir_by_id(root)
    assert root["styles"]["width"] == "100%"
    assert root["styles"]["height"] == "100%"
    assert root["styles"]["backgroundColor"] == "#F1F3F5"
    text_node_ids = {
        node.node_id
        for node in snapshot.nodes
        if node.width_sizing == "auto"
    }
    assert len(text_node_ids) == 16
    assert all(
        "width" not in nodes[node_id]["styles"]
        for node_id in text_node_ids
    )

    weighted_nodes = {
        "task-overview.main",
        "task-overview.stats.completed",
        "task-overview.stats.pending",
        "task-overview.footer.primary-btn",
        "task-overview.footer.secondary-btn",
    }
    assert {
        node_id: nodes[node_id]["styles"]["layoutWeight"]
        for node_id in weighted_nodes
    } == {node_id: 1.0 for node_id in weighted_nodes}

    font_families = {
        node["styles"]["fontFamily"]
        for node in nodes.values()
        if "fontFamily" in node.get("styles", {})
    }
    assert font_families == {"HarmonyOS Sans SC"}
    assert all("," not in family for family in font_families)

    ark_ts = result["arkTs"]
    assert '.backgroundColor("#F1F3F5")' in ark_ts
    assert '.fontFamily("HarmonyOS Sans SC")' in ark_ts
    assert 'Button("新建任务")' in ark_ts
    assert 'Button("查看全部")' in ark_ts
    assert ark_ts.index('Button("新建任务")') < ark_ts.index('Button("查看全部")')
    twelve_block = ark_ts[
        ark_ts.index('Text("12")'):
        ark_ts.index('Text("待处理")')
    ]
    assert ".width(" not in twelve_block


def test_task_overview_export_cli_materializes_canonical_artifacts(
    tmp_path: Path,
) -> None:
    output = tmp_path / "task-overview"
    completed = subprocess.run(
        [sys.executable, str(EXPORT_TOOL), "--out", str(output)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert {path.name for path in output.iterdir()} == {
        "screen.html",
        "browser-snapshot.json",
        "page.ets",
        "project.zip",
        "export-summary.json",
    }
    assert (output / "screen.html").read_text(encoding="utf-8") == (
        load_task_overview_html()
    )
    BrowserSnapshot.model_validate_json(
        (output / "browser-snapshot.json").read_text(encoding="utf-8")
    )
    summary_text = (output / "export-summary.json").read_text(encoding="utf-8")
    summary = json.loads(summary_text)
    assert "contentBase64" not in summary_text
    assert "arkTs" not in summary
    assert summary["quality"]["readiness"] == "ready"
    assert summary["artifacts"] == {
        "arkTs": "page.ets",
        "browserSnapshot": "browser-snapshot.json",
        "html": "screen.html",
        "project": "project.zip",
    }

    with zipfile.ZipFile(output / "project.zip") as archive:
        zipped_page = archive.read(
            "entry/src/main/ets/pages/TaskOverview.ets"
        ).decode("utf-8")
    assert zipped_page == (output / "page.ets").read_text(encoding="utf-8")
