"""Reusable deterministic input for the task-overview ArkUI regression."""
from __future__ import annotations

from pathlib import Path

from uibench.arkui.metadata import analyze_component_metadata
from uibench.arkui.snapshot import BrowserComputedStyle, BrowserSnapshot


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = PROJECT_ROOT / "tests/fixtures/arkui_task_overview"
FONT_STACK = (
    '"HarmonyOS Sans SC", "HarmonyOS Sans", "PingFang SC", sans-serif'
)

# Representative 390 x 844 light-theme browser geometry. Keeping every node
# explicit makes accidental annotation/snapshot drift fail at the fixture edge.
BOXES: dict[str, tuple[int, int, int, int]] = {
    "task-overview": (0, 0, 390, 844),
    "task-overview.header": (0, 0, 390, 87),
    "task-overview.header.title": (16, 16, 96, 32),
    "task-overview.header.subtitle": (16, 52, 154, 20),
    "task-overview.main": (0, 87, 390, 681),
    "task-overview.stats": (16, 103, 358, 84),
    "task-overview.stats.completed": (16, 103, 173, 84),
    "task-overview.stats.completed-label": (32, 119, 36, 16),
    "task-overview.stats.completed-value": (32, 139, 27, 32),
    "task-overview.stats.pending": (201, 103, 173, 84),
    "task-overview.stats.pending-label": (217, 119, 36, 16),
    "task-overview.stats.pending-value": (217, 139, 14, 32),
    "task-overview.tasks": (16, 211, 358, 323),
    "task-overview.tasks.title": (32, 227, 64, 24),
    "task-overview.tasks.divider-1": (32, 263, 326, 1),
    "task-overview.tasks.item-1": (32, 276, 326, 64),
    "task-overview.tasks.item-1-row": (32, 284, 326, 24),
    "task-overview.tasks.item-1-title": (32, 284, 144, 24),
    "task-overview.tasks.item-1-status": (322, 288, 36, 16),
    "task-overview.tasks.item-1-desc": (32, 312, 238, 20),
    "task-overview.tasks.divider-2": (32, 352, 326, 1),
    "task-overview.tasks.item-2": (32, 365, 326, 64),
    "task-overview.tasks.item-2-row": (32, 373, 326, 24),
    "task-overview.tasks.item-2-title": (32, 373, 96, 24),
    "task-overview.tasks.item-2-status": (294, 377, 64, 16),
    "task-overview.tasks.item-2-desc": (32, 401, 224, 20),
    "task-overview.tasks.divider-3": (32, 441, 326, 1),
    "task-overview.tasks.item-3": (32, 454, 326, 64),
    "task-overview.tasks.item-3-row": (32, 462, 326, 24),
    "task-overview.tasks.item-3-title": (32, 462, 112, 24),
    "task-overview.tasks.item-3-status": (322, 466, 36, 16),
    "task-overview.tasks.item-3-desc": (32, 490, 210, 20),
    "task-overview.footer": (0, 768, 390, 76),
    "task-overview.footer.buttons": (16, 784, 358, 44),
    "task-overview.footer.primary-btn": (16, 784, 173, 44),
    "task-overview.footer.secondary-btn": (201, 784, 173, 44),
}


def _px(value: int) -> str:
    return f"{value}px"


def _insets(
    name: str,
    top: int,
    right: int,
    bottom: int,
    left: int,
) -> dict[str, str]:
    return {
        f"{name}Top": _px(top),
        f"{name}Right": _px(right),
        f"{name}Bottom": _px(bottom),
        f"{name}Left": _px(left),
    }


def _radius(value: int) -> dict[str, str]:
    radius = _px(value)
    return {
        "borderTopLeftRadius": radius,
        "borderTopRightRadius": radius,
        "borderBottomRightRadius": radius,
        "borderBottomLeftRadius": radius,
    }


CARD_STYLE = {
    "backgroundColor": "rgb(255, 255, 255)",
    **_insets("padding", 16, 16, 16, 16),
    **_radius(24),
}
FLEX_ONE = {
    "flexGrow": "1",
    "flexShrink": "1",
    "flexBasis": "0%",
}
TEXT_PRIMARY = "rgba(0, 0, 0, 0.90)"
TEXT_SECONDARY = "rgba(0, 0, 0, 0.60)"
TEXT_TERTIARY = "rgba(0, 0, 0, 0.40)"

NODE_STYLES: dict[str, dict[str, str]] = {
    "task-overview": {
        "backgroundColor": "rgb(241, 243, 245)",
        "justifyContent": "flex-start",
    },
    "task-overview.header": _insets("padding", 16, 16, 16, 16),
    "task-overview.header.title": {
        "fontSize": "24px",
        "fontWeight": "700",
        "lineHeight": "32px",
    },
    "task-overview.header.subtitle": {
        "fontSize": "14px",
        "lineHeight": "20px",
        "color": TEXT_SECONDARY,
        **_insets("margin", 4, 0, 0, 0),
    },
    "task-overview.main": {
        **FLEX_ONE,
        **_insets("padding", 16, 16, 16, 16),
    },
    "task-overview.stats": {"columnGap": "12px"},
    "task-overview.stats.completed": {**CARD_STYLE, **FLEX_ONE},
    "task-overview.stats.pending": {**CARD_STYLE, **FLEX_ONE},
    "task-overview.stats.completed-label": {
        "fontSize": "12px",
        "lineHeight": "16px",
        "color": TEXT_SECONDARY,
    },
    "task-overview.stats.completed-value": {
        "fontSize": "24px",
        "fontWeight": "700",
        "lineHeight": "32px",
        **_insets("margin", 4, 0, 0, 0),
    },
    "task-overview.stats.pending-label": {
        "fontSize": "12px",
        "lineHeight": "16px",
        "color": TEXT_SECONDARY,
    },
    "task-overview.stats.pending-value": {
        "fontSize": "24px",
        "fontWeight": "700",
        "lineHeight": "32px",
        **_insets("margin", 4, 0, 0, 0),
    },
    "task-overview.tasks": {
        **CARD_STYLE,
        **_insets("margin", 24, 0, 0, 0),
    },
    "task-overview.tasks.title": {
        "fontSize": "16px",
        "fontWeight": "600",
        "lineHeight": "24px",
    },
    "task-overview.tasks.item-1": _insets("padding", 8, 0, 8, 0),
    "task-overview.tasks.item-2": _insets("padding", 8, 0, 8, 0),
    "task-overview.tasks.item-3": _insets("padding", 8, 0, 8, 0),
    "task-overview.tasks.item-1-row": {
        "alignItems": "center",
        "justifyContent": "space-between",
    },
    "task-overview.tasks.item-2-row": {
        "alignItems": "center",
        "justifyContent": "space-between",
    },
    "task-overview.tasks.item-3-row": {
        "alignItems": "center",
        "justifyContent": "space-between",
    },
    "task-overview.tasks.item-1-title": {"fontWeight": "500"},
    "task-overview.tasks.item-2-title": {"fontWeight": "500"},
    "task-overview.tasks.item-3-title": {"fontWeight": "500"},
    "task-overview.tasks.item-1-status": {
        "fontSize": "12px",
        "lineHeight": "16px",
        "color": TEXT_TERTIARY,
    },
    "task-overview.tasks.item-2-status": {
        "fontSize": "12px",
        "lineHeight": "16px",
        "color": TEXT_TERTIARY,
    },
    "task-overview.tasks.item-3-status": {
        "fontSize": "12px",
        "lineHeight": "16px",
        "color": TEXT_TERTIARY,
    },
    "task-overview.tasks.item-1-desc": {
        "fontSize": "14px",
        "lineHeight": "20px",
        "color": TEXT_SECONDARY,
        **_insets("margin", 4, 0, 0, 0),
    },
    "task-overview.tasks.item-2-desc": {
        "fontSize": "14px",
        "lineHeight": "20px",
        "color": TEXT_SECONDARY,
        **_insets("margin", 4, 0, 0, 0),
    },
    "task-overview.tasks.item-3-desc": {
        "fontSize": "14px",
        "lineHeight": "20px",
        "color": TEXT_SECONDARY,
        **_insets("margin", 4, 0, 0, 0),
    },
    "task-overview.footer": _insets("padding", 16, 16, 16, 16),
    "task-overview.footer.buttons": {"columnGap": "12px"},
    "task-overview.footer.primary-btn": {
        **FLEX_ONE,
        "backgroundColor": "rgb(10, 89, 247)",
        "color": "rgb(255, 255, 255)",
        "fontSize": "14px",
        "fontWeight": "500",
        "lineHeight": "normal",
        "textAlign": "center",
        **_radius(16),
    },
    "task-overview.footer.secondary-btn": {
        **FLEX_ONE,
        "backgroundColor": "rgba(0, 0, 0, 0.047)",
        "color": TEXT_PRIMARY,
        "fontSize": "14px",
        "fontWeight": "500",
        "lineHeight": "normal",
        "textAlign": "center",
        **_radius(16),
        "borderTopWidth": "1px",
        "borderRightWidth": "1px",
        "borderBottomWidth": "1px",
        "borderLeftWidth": "1px",
        "borderTopColor": "rgba(0, 0, 0, 0.20)",
        "borderRightColor": "rgba(0, 0, 0, 0.20)",
        "borderBottomColor": "rgba(0, 0, 0, 0.20)",
        "borderLeftColor": "rgba(0, 0, 0, 0.20)",
        "borderTopStyle": "solid",
        "borderRightStyle": "solid",
        "borderBottomStyle": "solid",
        "borderLeftStyle": "solid",
    },
}

for divider in (1, 2, 3):
    NODE_STYLES[f"task-overview.tasks.divider-{divider}"] = {
        **_insets("margin", 12, 0, 12, 0),
        "borderTopWidth": "0px",
        "borderRightWidth": "0px",
        "borderBottomWidth": "1px",
        "borderLeftWidth": "0px",
        "borderBottomColor": "rgba(0, 0, 0, 0.05)",
        "borderBottomStyle": "solid",
    }


def load_task_overview_html() -> str:
    return (FIXTURE_DIR / "screen.html").read_text(encoding="utf-8")


def build_task_overview_snapshot(html: str | None = None) -> BrowserSnapshot:
    html = load_task_overview_html() if html is None else html
    report = analyze_component_metadata(html)
    if report.errors or report.warnings:
        diagnostics = ", ".join(item.code for item in report.diagnostics)
        raise ValueError(f"task-overview fixture metadata is invalid: {diagnostics}")
    report_ids = {node.node_id for node in report.nodes}
    if report_ids != set(BOXES):
        raise ValueError("task-overview fixture and geometry node IDs differ")

    nodes: list[dict[str, object]] = []
    for node in report.nodes:
        if node.node_id is None:
            raise ValueError("task-overview fixture node is missing data-node-id")
        x, y, width, height = BOXES[node.node_id]
        computed = {
            "display": (
                "flex" if node.arkui_component in {"Column", "Row"} else "block"
            ),
            "width": _px(width),
            "height": _px(height),
            "fontFamily": FONT_STACK,
            "fontSize": "16px",
            "fontWeight": "400",
            "lineHeight": "24px" if node.arkui_component == "Text" else "normal",
            "color": TEXT_PRIMARY,
        }
        if node.arkui_component == "Column":
            computed["flexDirection"] = "column"
        elif node.arkui_component == "Row":
            computed["flexDirection"] = "row"
        elif node.arkui_component == "Text":
            # These fixture boxes represent a one-line glyph measurement, not
            # an authored width. Mirror the browser bridge provenance so ArkUI
            # can remeasure the text with its own font rasterizer instead of
            # freezing a CSS-pixel width that may wrap (for example, "12").
            computed.update({
                "paddingLeft": "0px",
                "paddingRight": "0px",
                "borderLeftWidth": "0px",
                "borderRightWidth": "0px",
                "transform": "none",
            })
        computed.update(NODE_STYLES.get(node.node_id, {}))
        captured_computed = BrowserComputedStyle().model_dump(by_alias=True)
        captured_computed.update(computed)
        computed = captured_computed

        parent_id = None
        if node.parent_index is not None:
            parent_id = report.nodes[node.parent_index].node_id
        payload: dict[str, object] = {
            "nodeId": node.node_id,
            "tag": node.tag,
            "bbox": [x, y, width, height],
            "visible": True,
            "directParentNodeId": parent_id,
            "isFlexItem": parent_id is not None,
            "computed": computed,
        }
        if node.arkui_component == "Text":
            payload["widthSizing"] = "auto"
            payload["singleLineTextWidth"] = width
        nodes.append(payload)

    return BrowserSnapshot.model_validate({
        "snapshotVersion": 1,
        "viewportWidth": 390,
        "viewportHeight": 844,
        "theme": "light",
        "tokenTheme": "harmonyos",
        "canvasBackgroundColor": "rgb(241, 243, 245)",
        "canvasBackgroundImage": "none",
        "nodes": nodes,
        "assets": [],
    })


__all__ = [
    "BOXES",
    "FIXTURE_DIR",
    "build_task_overview_snapshot",
    "load_task_overview_html",
]
