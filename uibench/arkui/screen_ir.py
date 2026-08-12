"""Adapt UIBench component annotations to canonical Screen IR v2.

This module owns UIBench-specific ``data-*`` semantics. The html-to-arkui
package remains source-agnostic and only validates/renders the resulting IR.
"""
from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Literal

from uibench.arkui.components import load_renderer_contract
from uibench.arkui.metadata import (
    MAX_COMPONENT_TREE_DEPTH,
    ComponentMetadataReport,
    ComponentNode,
)
from uibench.arkui.snapshot import (
    BrowserNodeSnapshot,
    BrowserSnapshot,
    screen_ir_styles,
)

AdapterSeverity = Literal["warning", "error"]
AdapterReadiness = Literal["ready", "lossy", "blocked"]

_PAGE_NAME_RE = re.compile(r"[^A-Za-z0-9_]+")


@dataclass(frozen=True)
class ScreenIrAdapterDiagnostic:
    code: str
    severity: AdapterSeverity
    message: str
    node_id: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "nodeId": self.node_id,
        }


@dataclass(frozen=True)
class ScreenIrBuildResult:
    screen_ir: dict[str, object] | None
    readiness: AdapterReadiness
    diagnostics: tuple[ScreenIrAdapterDiagnostic, ...]


def normalize_page_name(value: str) -> str:
    """Return a deterministic ArkTS-friendly page name."""
    cleaned = _PAGE_NAME_RE.sub("_", value.strip()).strip("_")
    if not cleaned:
        return "GeneratedPage"
    if cleaned[0].isdigit():
        cleaned = f"Page_{cleaned}"
    return cleaned


def _node_attributes(node: ComponentNode) -> dict[str, str]:
    return dict(node.attributes)


def _node_metadata(node: ComponentNode) -> dict[str, str]:
    return dict(node.metadata)


def _to_ir_node(
    node_index: int,
    report: ComponentMetadataReport,
    children_by_parent: dict[int, list[int]],
    snapshot_by_id: dict[str, BrowserNodeSnapshot],
    styles_by_id: dict[str, dict[str, object]],
    resource_bindings: dict[tuple[str, str], str],
    included_indices: frozenset[int],
) -> dict[str, object]:
    node = report.nodes[node_index]
    if node.node_id is None:  # guarded before tree construction
        raise ValueError("Screen IR nodes require data-node-id")

    meta: dict[str, object] = {
        "nodeId": node.node_id,
        "htmlTag": node.tag,
    }
    browser_node = snapshot_by_id.get(node.node_id)
    if browser_node is not None:
        meta["bbox"] = [round(value, 4) for value in browser_node.bbox]
    result: dict[str, object] = {
        "componentName": node.arkui_component,
        "meta": meta,
    }
    attributes = _node_attributes(node)
    metadata = _node_metadata(node)

    if node.arkui_component in {"Text", "Span", "Button"} and node.text_content:
        result["content"] = node.text_content
    if node.arkui_component == "Image":
        result["src"] = resource_bindings.get(
            (node.node_id, "image"), attributes["src"]
        )
        if attributes.get("alt"):
            result["props"] = {"alt": attributes["alt"]}
    elif node.arkui_component == "SymbolGlyph":
        result["props"] = {"symbol": metadata["data-symbol"]}
    styles = styles_by_id.get(node.node_id)
    if styles:
        result["styles"] = styles

    children = [
        _to_ir_node(
            child_index,
            report,
            children_by_parent,
            snapshot_by_id,
            styles_by_id,
            resource_bindings,
            included_indices,
        )
        for child_index in children_by_parent.get(node_index, [])
        if child_index in included_indices
    ]
    if children:
        result["children"] = children
    return result


def build_screen_ir(
    report: ComponentMetadataReport,
    *,
    page_name: str = "GeneratedPage",
    page_description: str | None = None,
    snapshot: BrowserSnapshot | None = None,
    resource_bindings: dict[tuple[str, str], str] | None = None,
) -> ScreenIrBuildResult:
    """Build Screen IR v2 from one analyzed annotated HTML document.

    The adapter intentionally does not invent styles. Until the browser
    snapshot stage is connected, valid output is reported as ``lossy``.
    """
    diagnostics: list[ScreenIrAdapterDiagnostic] = []
    resource_bindings = resource_bindings or {}

    if report.explicit_components == 0:
        diagnostics.append(ScreenIrAdapterDiagnostic(
            code="UIBENCH_ARKUI_METADATA_MISSING",
            severity="error",
            message="No explicit data-component annotations were found",
        ))
    for item in report.errors:
        diagnostics.append(ScreenIrAdapterDiagnostic(
            code=item.code,
            severity="error",
            message=item.message,
            node_id=item.node_id,
        ))
    for item in report.warnings:
        diagnostics.append(ScreenIrAdapterDiagnostic(
            code=item.code,
            severity="warning",
            message=item.message,
            node_id=item.node_id,
        ))
    for node in report.nodes:
        if not node.renderer_supported:
            diagnostics.append(ScreenIrAdapterDiagnostic(
                code="UIBENCH_ARKUI_COMPONENT_UNSUPPORTED",
                severity="error",
                message=(
                    f"{node.arkui_component} is not supported by the current "
                    "html-to-arkui renderer contract"
                ),
                node_id=node.node_id,
            ))
        if node.node_id is None:
            diagnostics.append(ScreenIrAdapterDiagnostic(
                code="UIBENCH_ARKUI_NODE_ID_REQUIRED",
                severity="error",
                message="Every Screen IR node requires a stable data-node-id",
            ))
        attributes = _node_attributes(node)
        metadata = _node_metadata(node)
        if node.arkui_component == "Image" and not attributes.get("src"):
            diagnostics.append(ScreenIrAdapterDiagnostic(
                code="UIBENCH_ARKUI_IMAGE_SRC_REQUIRED",
                severity="error",
                message="Image requires a non-empty src attribute",
                node_id=node.node_id,
            ))
        if node.arkui_component == "SymbolGlyph" and not metadata.get("data-symbol"):
            diagnostics.append(ScreenIrAdapterDiagnostic(
                code="UIBENCH_ARKUI_SYMBOL_REQUIRED",
                severity="error",
                message="SymbolGlyph requires canonical data-symbol metadata",
                node_id=node.node_id,
            ))
        if node.arkui_component == "Span" and not node.text_content:
            diagnostics.append(ScreenIrAdapterDiagnostic(
                code="UIBENCH_ARKUI_SPAN_CONTENT_REQUIRED",
                severity="error",
                message="Span requires non-empty text content",
                node_id=node.node_id,
            ))
        if node.arkui_component == "Image":
            source = attributes.get("src", "").strip()
            is_materialized = (
                node.node_id is not None
                and (node.node_id, "image") in resource_bindings
            )
            if source and not is_materialized and not source.startswith("$r("):
                diagnostics.append(ScreenIrAdapterDiagnostic(
                    code="UIBENCH_IMAGE_ASSET_NOT_MATERIALIZED",
                    severity="warning",
                    message=(
                        "Image source is referenced but has not been materialized "
                        "into an ArkUI resource bundle"
                    ),
                    node_id=node.node_id,
                ))

    roots = [
        index for index, node in enumerate(report.nodes)
        if node.parent_index is None
    ]
    if report.explicit_components > 0 and len(roots) != 1:
        diagnostics.append(ScreenIrAdapterDiagnostic(
            code="UIBENCH_ARKUI_ROOT_COUNT_INVALID",
            severity="error",
            message=f"Expected exactly one component root; found {len(roots)}",
        ))

    children_by_parent: dict[int, list[int]] = defaultdict(list)
    for index, node in enumerate(report.nodes):
        if node.parent_index is not None:
            children_by_parent[node.parent_index].append(index)

    if len(roots) == 1:
        pending = [(roots[0], 1)]
        while pending:
            node_index, depth = pending.pop()
            if depth > MAX_COMPONENT_TREE_DEPTH:
                diagnostics.append(ScreenIrAdapterDiagnostic(
                    code="UIBENCH_ARKUI_TREE_DEPTH_EXCEEDED",
                    severity="error",
                    message=(
                        "Screen IR component nesting exceeds the supported "
                        f"depth of {MAX_COMPONENT_TREE_DEPTH}"
                    ),
                    node_id=report.nodes[node_index].node_id,
                ))
                break
            pending.extend(
                (child_index, depth + 1)
                for child_index in children_by_parent.get(node_index, [])
            )

    if any(item.severity == "error" for item in diagnostics):
        unique = tuple(dict.fromkeys(diagnostics))
        return ScreenIrBuildResult(
            screen_ir=None,
            readiness="blocked",
            diagnostics=unique,
        )

    snapshot_by_id: dict[str, BrowserNodeSnapshot] = {}
    styles_by_id: dict[str, dict[str, object]] = {}
    included_indices = frozenset(range(len(report.nodes)))
    if snapshot is None:
        diagnostics.append(ScreenIrAdapterDiagnostic(
            code="UIBENCH_COMPUTED_STYLE_SNAPSHOT_PENDING",
            severity="warning",
            message=(
                "Component structure was exported, but browser-computed styles "
                "and geometry have not been frozen yet"
            ),
        ))
    else:
        snapshot_by_id = {node.node_id: node for node in snapshot.nodes}
        hidden_indices: set[int] = set()
        for index, node in enumerate(report.nodes):
            if node.node_id is None:
                continue
            hidden_by_ancestor = (
                node.parent_index is not None
                and node.parent_index in hidden_indices
            )
            if hidden_by_ancestor:
                hidden_indices.add(index)
                continue
            browser_node = snapshot_by_id.get(node.node_id)
            if browser_node is None:
                diagnostics.append(ScreenIrAdapterDiagnostic(
                    code="UIBENCH_BROWSER_SNAPSHOT_NODE_MISSING",
                    severity="error",
                    message=(
                        "Annotated node was not present in the browser snapshot; "
                        "export cannot safely infer whether it is visible"
                    ),
                    node_id=node.node_id,
                ))
                continue
            if not browser_node.visible:
                hidden_indices.add(index)
            if not browser_node.visible:
                diagnostics.append(ScreenIrAdapterDiagnostic(
                    code="UIBENCH_BROWSER_SNAPSHOT_NODE_NOT_VISIBLE",
                    severity="warning",
                    message=(
                        "Annotated node and its component subtree were omitted because "
                        "the node was not visible in the selected viewport/theme"
                    ),
                    node_id=node.node_id,
                ))
            if index in hidden_indices:
                continue
            styles, lossy_properties = screen_ir_styles(
                node.arkui_component,
                browser_node,
                background_image_source=resource_bindings.get(
                    (node.node_id, "background-image")
                ),
            )
            styles_by_id[node.node_id] = styles
            for property_name in lossy_properties:
                diagnostics.append(ScreenIrAdapterDiagnostic(
                    code="UIBENCH_BROWSER_STYLE_LOSSY",
                    severity="warning",
                    message=f"Computed style cannot be represented exactly: {property_name}",
                    node_id=node.node_id,
                ))
        included_indices = frozenset(
            index for index in range(len(report.nodes))
            if index not in hidden_indices
        )
        if roots[0] not in included_indices:
            diagnostics.append(ScreenIrAdapterDiagnostic(
                code="UIBENCH_BROWSER_SNAPSHOT_ROOT_NOT_VISIBLE",
                severity="error",
                message=(
                    "The root component was not visible in the selected "
                    "viewport/theme"
                ),
                node_id=report.nodes[roots[0]].node_id,
            ))

        renderer = load_renderer_contract()
        for index in included_indices:
            definition = renderer.components.get(
                report.nodes[index].arkui_component
            )
            if definition is None:
                continue
            visible_child_count = sum(
                child_index in included_indices
                for child_index in children_by_parent.get(index, [])
            )
            if visible_child_count < definition.min_children:
                diagnostics.append(ScreenIrAdapterDiagnostic(
                    code="UIBENCH_BROWSER_SNAPSHOT_PRUNE_INVALID",
                    severity="error",
                    message=(
                        f"Pruning hidden nodes leaves {definition.name} with "
                        f"{visible_child_count} children; at least "
                        f"{definition.min_children} are required"
                    ),
                    node_id=report.nodes[index].node_id,
                ))

    if any(item.severity == "error" for item in diagnostics):
        unique = tuple(dict.fromkeys(diagnostics))
        return ScreenIrBuildResult(
            screen_ir=None,
            readiness="blocked",
            diagnostics=unique,
        )

    page: dict[str, str] = {"name": normalize_page_name(page_name)}
    if page_description and page_description.strip():
        page["description"] = page_description.strip()
    screen_ir: dict[str, object] = {
        "schemaVersion": 2,
        "page": page,
        "ui": _to_ir_node(
            roots[0],
            report,
            children_by_parent,
            snapshot_by_id,
            styles_by_id,
            resource_bindings,
            included_indices,
        ),
    }
    readiness: AdapterReadiness = (
        "lossy"
        if any(item.severity == "warning" for item in diagnostics)
        else "ready"
    )
    return ScreenIrBuildResult(
        screen_ir=screen_ir,
        readiness=readiness,
        diagnostics=tuple(diagnostics),
    )


__all__ = [
    "ScreenIrAdapterDiagnostic",
    "ScreenIrBuildResult",
    "build_screen_ir",
    "normalize_page_name",
]
