"""Adapt UIBench component annotations to canonical Screen IR v2.

This module owns UIBench-specific ``data-*`` semantics. The html-to-arkui
package remains source-agnostic and only validates/renders the resulting IR.
"""
from __future__ import annotations

import math
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
    browser_main_axis,
    normalize_css_color,
    screen_ir_styles,
)

AdapterSeverity = Literal["notice", "warning", "error"]
AdapterReadiness = Literal["ready", "lossy", "blocked"]

_PAGE_NAME_RE = re.compile(r"[^A-Za-z0-9_]+")
_VIEWPORT_ROOT_COMPONENTS = frozenset({
    "Column", "Row", "Stack", "Scroll", "List", "Grid",
})
_GENERATED_TEXT_STYLE_KEYS = frozenset({
    "fontColor",
    "fontFamily",
    "fontSize",
    "fontWeight",
    "letterSpacing",
    "lineHeight",
    "maxLines",
    "textAlign",
    "textOverflow",
})
# Shared with the exporter's canvas gate: both sides must agree on what
# "covers the viewport" means, or a root the gate waves through can still
# fail the promotion below and leave the document canvas unreproduced.
_VIEWPORT_EDGE_TOLERANCE = 1


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


def _bake_text_transform(
    content: str,
    browser_node: BrowserNodeSnapshot | None,
) -> str:
    """Apply the rendered CSS text-transform to the frozen text content.

    Exported text is a static string, so casing can be applied exactly at
    export time: the browser already displayed the transformed glyphs and the
    untransformed DOM source never reaches the device. ``capitalize`` is
    deliberately not baked because CSS titlecases the first letter unit of
    UAX#29 words, which plain string casing cannot reproduce; it stays a
    lossy-style diagnostic in the snapshot mapping.
    """
    if browser_node is None:
        return content
    transform = browser_node.computed.text_transform.strip().lower()
    if transform == "uppercase":
        return content.upper()
    if transform == "lowercase":
        return content.lower()
    return content


def _node_attributes(node: ComponentNode) -> dict[str, str]:
    return dict(node.attributes)


def _node_metadata(node: ComponentNode) -> dict[str, str]:
    return dict(node.metadata)


def _component_direction(component_name: str) -> Literal["row", "column"] | None:
    if component_name == "Row":
        return "row"
    if component_name == "Column":
        return "column"
    return None


def _browser_container_component(browser_node: BrowserNodeSnapshot) -> str | None:
    """Return the ArkUI container the browser actually laid out.

    Where the computed evidence is unambiguous the export follows it, because
    the rendered page is what the ArkUI project has to reproduce. ``None``
    marks a display mode ArkUI cannot express at all.
    """
    axis = browser_main_axis(browser_node)
    if axis is None:
        return None
    return "Row" if axis == "row" else "Column"


def _browser_flex_container_component(
    browser_node: BrowserNodeSnapshot,
) -> str | None:
    """Return a container only when mixed inline content is explicitly flex.

    Normal block flow stacks element children, but text and inline icons still
    share a line. Treating that display mode as a Column would therefore move
    the label below the icon. Flex evidence is required for this repair.
    """
    display = browser_node.computed.display.strip().lower()
    if display not in {"flex", "inline-flex"}:
        return None
    return _browser_container_component(browser_node)


def root_covers_viewport(
    browser_node: BrowserNodeSnapshot,
    snapshot: BrowserSnapshot,
) -> bool:
    """Whether the node's rectangle contains the whole captured viewport.

    A scrollable page is taller than the viewport it was captured in, so this
    asks the node to contain the viewport rather than match it exactly.
    """
    x, y, width, height = browser_node.bbox
    return all((
        x <= _VIEWPORT_EDGE_TOLERANCE,
        y <= _VIEWPORT_EDGE_TOLERANCE,
        x + width >= snapshot.viewport_width - _VIEWPORT_EDGE_TOLERANCE,
        y + height >= snapshot.viewport_height - _VIEWPORT_EDGE_TOLERANCE,
    ))


def is_viewport_page_root(
    component_name: str,
    browser_node: BrowserNodeSnapshot,
    snapshot: BrowserSnapshot,
) -> bool:
    """Whether a layout root is the page surface Screen IR may retarget.

    Only such a root gets browser viewport pixels replaced by 100% sizing and
    inherits the document canvas colour; any other root keeps its captured
    geometry untouched.
    """
    if component_name not in _VIEWPORT_ROOT_COMPONENTS:
        return False
    return root_covers_viewport(browser_node, snapshot)


def _list_entry_children(
    children: list[dict[str, object]],
    *,
    horizontal: bool,
) -> list[dict[str, object]]:
    """Give every plain List entry the ListItem ArkUI requires around it.

    ArkUI's ``List`` accepts only ``ListItem`` children, so a component
    annotated directly inside a list can only mean the content of one entry.
    The generated item invents no geometry: it spans the list's content across
    the cross axis like a stretched flex child does in the browser, while the
    entry keeps its own computed size and decoration.
    """
    wrapped: list[dict[str, object]] = []
    for child in children:
        if child.get("componentName") == "ListItem":
            wrapped.append(child)
            continue
        meta = child.get("meta")
        child_node_id = str(
            meta.get("nodeId") if isinstance(meta, dict) else ""
        )
        wrapped.append({
            "componentName": "ListItem",
            # Screen IR node ids allow ':', UIBench data-node-id does not, so
            # this can never collide with an authored id.
            "meta": {"nodeId": f"{child_node_id}:item"},
            "styles": {"height": "100%"} if horizontal else {"width": "100%"},
            "children": [child],
        })
    return wrapped


def _grid_entry_children(
    children: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Give every plain Grid entry the GridItem ArkUI requires around it.

    ArkUI's ``Grid`` accepts only ``GridItem`` children, so a component
    annotated directly inside a grid can only mean the content of one cell.
    The generated item invents no geometry: the grid's track template sizes
    the cell and the entry keeps its own computed size and decoration.
    """
    wrapped: list[dict[str, object]] = []
    for child in children:
        if child.get("componentName") == "GridItem":
            wrapped.append(child)
            continue
        meta = child.get("meta")
        child_node_id = str(
            meta.get("nodeId") if isinstance(meta, dict) else ""
        )
        wrapped.append({
            "componentName": "GridItem",
            # Screen IR node ids allow ':', UIBench data-node-id does not, so
            # this can never collide with an authored id.
            "meta": {"nodeId": f"{child_node_id}:item"},
            "styles": {"width": "100%"},
            "children": [child],
        })
    return wrapped


def _wrap_document_scroll(
    screen_ir: dict[str, object], root_node_id: str,
) -> None:
    """Give a document-scrolled page the Scroll ArkUI needs to reproduce it.

    A viewport-spanning page root taller than the captured viewport means the
    browser scrolled the document itself. ArkUI has no document scroll: the
    page root is pinned to the window, so the overflow would simply be
    clipped. The root keeps its size and background; its inner layout moves
    onto a generated content node inside a generated Scroll, which is exactly
    how such a page is written by hand.
    """
    ui = screen_ir["ui"]
    assert isinstance(ui, dict)
    root_styles = dict(ui.get("styles") or {})
    content_styles: dict[str, object] = {"width": "100%"}
    for key in ("padding", "space", "justifyContent", "alignItems"):
        if key in root_styles:
            content_styles[key] = root_styles.pop(key)
    content: dict[str, object] = {
        "componentName": ui["componentName"],
        # Screen IR node ids allow ':', UIBench data-node-id does not, so
        # these can never collide with an authored id.
        "meta": {"nodeId": f"{root_node_id}:content"},
        "styles": content_styles,
    }
    if ui.get("children"):
        content["children"] = ui["children"]
    if root_styles:
        ui["styles"] = root_styles
    else:
        ui.pop("styles", None)
    ui["children"] = [{
        "componentName": "Scroll",
        "meta": {"nodeId": f"{root_node_id}:scroll"},
        "styles": {"width": "100%", "height": "100%"},
        "children": [content],
    }]


def _single_slot_children(
    component_name: str,
    node_id: str,
    browser_node: BrowserNodeSnapshot | None,
    children: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Give a single-slot container the one child ArkUI allows it.

    ``Button``, ``Scroll`` and ``ListItem`` take exactly one child, but the HTML
    element they came from is itself the flex container holding several. The
    generated wrapper invents no geometry: it takes over that element's own
    computed direction, alignment and gap, while the element keeps its box
    decoration and padding, which is how the pair is written in ArkTS by hand.
    """
    definition = load_renderer_contract().components.get(component_name)
    if definition is None or definition.max_children != 1 or len(children) <= 1:
        return children
    wrapper = (
        _browser_container_component(browser_node)
        if browser_node is not None else None
    ) or "Column"
    # The element's padding already inset the slot, so the wrapper spans it.
    styles: dict[str, object] = {"width": "100%"}
    if browser_node is not None:
        layout, _ = screen_ir_styles(wrapper, browser_node)
        styles.update({
            key: layout[key]
            for key in ("justifyContent", "alignItems", "space")
            if key in layout
        })
    return [{
        "componentName": wrapper,
        # Screen IR node ids allow ':', UIBench data-node-id does not, so this
        # can never collide with an authored id.
        "meta": {"nodeId": f"{node_id}:content"},
        "styles": styles,
        "children": children,
    }]


def _text_children_with_runs(
    node: ComponentNode,
    browser_node: BrowserNodeSnapshot | None,
    positioned_children: list[tuple[int, dict[str, object]]],
    total_child_count: int,
    *,
    run_component: Literal["Span", "Text"] = "Span",
    run_styles: dict[str, object] | None = None,
    trim_runs: bool = False,
) -> list[dict[str, object]]:
    """Interleave a node's own text fragments with its component children.

    ArkUI's Text renders either its own content or its Span children, never
    both, so rich text such as ``共 <span>3</span> 台`` must become one
    ordered Span per fragment; the parent's fragments keep their document
    position around the styled spans. A model-authored Text that also contains
    a SymbolGlyph is instead adapted to a layout container, whose anonymous
    browser text runs become generated Text children. Positions still count
    children hidden from the export, so pruning one cannot shift the rest.
    """
    assert node.node_id is not None
    runs = list(node.text_runs)
    merged: list[dict[str, object]] = []
    synthetic = 0

    def emit_runs(position: int) -> None:
        nonlocal synthetic
        while runs and runs[0][0] <= position:
            _, text = runs.pop(0)
            content = _bake_text_transform(text, browser_node)
            if trim_runs:
                content = content.strip()
            if not content:
                continue
            generated: dict[str, object] = {
                "componentName": run_component,
                # Screen IR node ids allow ':', UIBench data-node-id does
                # not, so this can never collide with an authored id.
                "meta": {"nodeId": f"{node.node_id}:run{synthetic}"},
                "content": content,
            }
            if run_styles:
                generated["styles"] = run_styles
            merged.append(generated)
            synthetic += 1

    for position, child in positioned_children:
        emit_runs(position)
        merged.append(child)
    emit_runs(total_child_count)
    return merged


def _to_ir_node(
    node_index: int,
    report: ComponentMetadataReport,
    children_by_parent: dict[int, list[int]],
    snapshot_by_id: dict[str, BrowserNodeSnapshot],
    styles_by_id: dict[str, dict[str, object]],
    resource_bindings: dict[tuple[str, str], str],
    included_indices: frozenset[int],
    component_overrides: dict[int, str],
    generated_text_styles_by_id: dict[str, dict[str, object]],
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
        "componentName": component_overrides.get(
            node_index, node.arkui_component
        ),
        "meta": meta,
    }
    attributes = _node_attributes(node)
    metadata = _node_metadata(node)

    if node.arkui_component in {"Text", "Span", "Button"} and node.text_content:
        result["content"] = _bake_text_transform(node.text_content, browser_node)
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

    child_indices = children_by_parent.get(node_index, [])
    positioned_children = [
        (
            position,
            _to_ir_node(
                child_index,
                report,
                children_by_parent,
                snapshot_by_id,
                styles_by_id,
                resource_bindings,
                included_indices,
                component_overrides,
                generated_text_styles_by_id,
            ),
        )
        for position, child_index in enumerate(child_indices)
        if child_index in included_indices
    ]
    children = [child for _, child in positioned_children]
    component_name = str(result["componentName"])
    if (
        node.arkui_component == "Text"
        and node.text_runs
        and (children or node.mixed_symbol_content)
    ):
        result.pop("content", None)
        if node.mixed_symbol_content and component_name in {"Row", "Column"}:
            children = _text_children_with_runs(
                node,
                browser_node,
                positioned_children,
                len(child_indices),
                run_component="Text",
                run_styles=generated_text_styles_by_id.get(node.node_id),
                trim_runs=True,
            )
        else:
            children = _text_children_with_runs(
                node, browser_node, positioned_children, len(child_indices),
            )
    if children:
        if component_name == "List":
            result["children"] = _list_entry_children(
                children,
                horizontal=(styles or {}).get("listDirection") == "Horizontal",
            )
        elif component_name == "Grid":
            result["children"] = _grid_entry_children(children)
        else:
            result["children"] = _single_slot_children(
                component_name, node.node_id, browser_node, children,
            )
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
    for item in (*report.warnings, *report.notices):
        diagnostics.append(ScreenIrAdapterDiagnostic(
            code=item.code,
            severity=item.severity,
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
    generated_text_styles_by_id: dict[str, dict[str, object]] = {}
    component_overrides: dict[int, str] = {}
    document_scroll_root_id: str | None = None
    included_indices = frozenset(range(len(report.nodes)))
    for parent_index, parent in enumerate(report.nodes):
        if not parent.mixed_symbol_content:
            continue
        for child_index in children_by_parent.get(parent_index, []):
            child = report.nodes[child_index]
            if child.arkui_component == "Span":
                component_overrides[child_index] = "Text"
                diagnostics.append(ScreenIrAdapterDiagnostic(
                    code="UIBENCH_MIXED_TEXT_SPAN_PROMOTED",
                    severity="notice",
                    message=(
                        "A Span beside a symbol was exported as Text inside "
                        "the generated layout container"
                    ),
                    node_id=child.node_id,
                ))
    if snapshot is None:
        for index, node in enumerate(report.nodes):
            if node.mixed_symbol_content:
                component_overrides[index] = "Row"
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
            hidden_by_ancestor = (
                node.parent_index is not None
                and node.parent_index in hidden_indices
            )
            if hidden_by_ancestor:
                hidden_indices.add(index)
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
            effective_component = component_overrides.get(
                index, node.arkui_component
            )
            if node.mixed_symbol_content:
                resolved = _browser_flex_container_component(browser_node)
                if resolved is None:
                    diagnostics.append(ScreenIrAdapterDiagnostic(
                        code="UIBENCH_TEXT_SYMBOL_LAYOUT_CONFLICT",
                        severity="error",
                        message=(
                            "Text containing a symbol can only be adapted when "
                            "the browser computed an ordinary flex row or column"
                        ),
                        node_id=node.node_id,
                    ))
                else:
                    effective_component = resolved
                    component_overrides[index] = resolved
            # Row and Column name their axis, a List carries it in
            # listDirection; either way the browser has to have laid the node
            # out along an axis ArkUI can express. Only the name can be wrong
            # about it: a List stays a List and exports the axis it was given.
            annotated_direction = _component_direction(node.arkui_component)
            if annotated_direction is not None or node.arkui_component == "List":
                resolved = _browser_container_component(browser_node)
                if resolved is None:
                    diagnostics.append(ScreenIrAdapterDiagnostic(
                        code="UIBENCH_ARKUI_LAYOUT_METADATA_CONFLICT",
                        severity="error",
                        message=(
                            f"{node.arkui_component} metadata cannot be "
                            "reconciled with the browser layout: computed "
                            f"display {browser_node.computed.display or 'unknown'}"
                            " / flex-direction "
                            f"{browser_node.computed.flex_direction or 'unknown'}"
                        ),
                        node_id=node.node_id,
                    ))
                elif (
                    annotated_direction is not None
                    and resolved != node.arkui_component
                ):
                    effective_component = resolved
                    component_overrides[index] = resolved
                    diagnostics.append(ScreenIrAdapterDiagnostic(
                        code="UIBENCH_ARKUI_LAYOUT_FOLLOWS_BROWSER",
                        severity="notice",
                        message=(
                            f"Annotated as {node.arkui_component} but the "
                            f"browser laid the node out as {resolved}; the "
                            "rendered layout was exported"
                        ),
                        node_id=node.node_id,
                    ))
            if node.arkui_component == "Grid":
                # A Grid claim needs grid evidence: ArkUI Grid auto-places
                # GridItems in row order, so only a browser grid flowing in
                # row order renders the same page.
                display = browser_node.computed.display.strip().lower()
                auto_flow = browser_node.computed.grid_auto_flow.strip().lower()
                if display not in {"grid", "inline-grid"}:
                    diagnostics.append(ScreenIrAdapterDiagnostic(
                        code="UIBENCH_ARKUI_LAYOUT_METADATA_CONFLICT",
                        severity="error",
                        message=(
                            "Grid metadata cannot be reconciled with the "
                            "browser layout: computed display "
                            f"{browser_node.computed.display or 'unknown'}"
                        ),
                        node_id=node.node_id,
                    ))
                elif auto_flow not in {"", "row"}:
                    diagnostics.append(ScreenIrAdapterDiagnostic(
                        code="UIBENCH_ARKUI_LAYOUT_METADATA_CONFLICT",
                        severity="error",
                        message=(
                            "ArkUI Grid auto-places items in row order; "
                            f"computed grid-auto-flow {auto_flow} cannot be "
                            "reproduced"
                        ),
                        node_id=node.node_id,
                    ))
            parent_direction = None
            flex_item_parent_verified = False
            flex_container_scrolls_main_axis = False
            if node.parent_index is not None:
                parent = report.nodes[node.parent_index]
                # Read the parent's direction off the browser rather than its
                # component name: a Button is a flex container in the DOM even
                # though ArkUI reaches its children through a wrapper.
                parent_browser = (
                    snapshot_by_id.get(parent.node_id)
                    if parent.node_id is not None else None
                )
                parent_direction = _component_direction(
                    _browser_container_component(parent_browser) or ""
                ) if parent_browser is not None else None
                if parent.component == "list" and node.component != "list-item":
                    # This entry is exported inside a generated ListItem, and
                    # a ListItem does not distribute main-axis space, so a
                    # browser flex weight against the list cannot transfer.
                    parent_direction = None
                if parent.component == "grid":
                    # ArkUI GridItem is auto-placed into the next free cell;
                    # explicit line numbers or spans have no representation.
                    placement = {
                        "grid-row-start": browser_node.computed.grid_row_start,
                        "grid-row-end": browser_node.computed.grid_row_end,
                        "grid-column-start": (
                            browser_node.computed.grid_column_start
                        ),
                        "grid-column-end": browser_node.computed.grid_column_end,
                    }
                    explicit = {
                        name: value.strip()
                        for name, value in placement.items()
                        if value.strip().lower() not in {"", "auto"}
                    }
                    if explicit:
                        diagnostics.append(ScreenIrAdapterDiagnostic(
                            code="UIBENCH_ARKUI_GRID_PLACEMENT_UNSUPPORTED",
                            severity="error",
                            message=(
                                "ArkUI GridItem auto-placement cannot "
                                "reproduce explicit grid placement: "
                                + ", ".join(
                                    f"{name}:{value}"
                                    for name, value in sorted(explicit.items())
                                )
                            ),
                            node_id=node.node_id,
                        ))
                if (
                    browser_node.direct_parent_node_id is not None
                    and browser_node.is_flex_item is None
                ):
                    diagnostics.append(ScreenIrAdapterDiagnostic(
                        code="UIBENCH_BROWSER_PARENT_PROVENANCE_MISSING",
                        severity="error",
                        message=(
                            "Browser snapshot contains incomplete direct-parent "
                            "provenance; the component tree cannot be verified"
                        ),
                        node_id=node.node_id,
                    ))
                elif (
                    browser_node.is_flex_item is not None
                    and browser_node.direct_parent_node_id != parent.node_id
                ):
                    actual_parent = (
                        repr(browser_node.direct_parent_node_id)
                        if browser_node.direct_parent_node_id is not None
                        else "an unannotated DOM element"
                    )
                    diagnostics.append(ScreenIrAdapterDiagnostic(
                        code="UIBENCH_ARKUI_DOM_PARENT_MISMATCH",
                        severity="error",
                        message=(
                            f"Component metadata parent is {parent.node_id!r}, "
                            f"but the direct DOM parent is {actual_parent}; "
                            "unannotated wrapper elements cannot be projected "
                            "into a different ArkUI layout tree"
                        ),
                        node_id=node.node_id,
                    ))
                flex_item_parent_verified = (
                    parent.node_id is not None
                    and browser_node.direct_parent_node_id == parent.node_id
                    and browser_node.is_flex_item is True
                )
                # The exported Scroll always scrolls vertically and sizes its
                # content chain by content, so a column-axis flex weight
                # against it would be anchored to the scroll viewport instead
                # of the content and the page would stop scrolling.
                flex_container_scrolls_main_axis = (
                    parent.arkui_component == "Scroll"
                    and parent_direction == "column"
                )
            styles, lossy_properties = screen_ir_styles(
                effective_component,
                browser_node,
                background_image_source=resource_bindings.get(
                    (node.node_id, "background-image")
                ),
                parent_direction=parent_direction,
                flex_item_parent_verified=flex_item_parent_verified,
                flex_container_scrolls_main_axis=flex_container_scrolls_main_axis,
                button_renders_direct_label=bool(node.text_content),
            )
            if node.mixed_symbol_content:
                text_styles, text_lossy_properties = screen_ir_styles(
                    "Text",
                    browser_node,
                    background_image_source=resource_bindings.get(
                        (node.node_id, "background-image")
                    ),
                    parent_direction=parent_direction,
                    flex_item_parent_verified=flex_item_parent_verified,
                    flex_container_scrolls_main_axis=(
                        flex_container_scrolls_main_axis
                    ),
                )
                generated_text_styles_by_id[node.node_id] = {
                    key: value
                    for key, value in text_styles.items()
                    if key in _GENERATED_TEXT_STYLE_KEYS
                }
                lossy_properties = tuple(dict.fromkeys((
                    *lossy_properties,
                    *text_lossy_properties,
                )))
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
        root_node_id = report.nodes[roots[0]].node_id
        root_browser_node = (
            snapshot_by_id.get(root_node_id)
            if root_node_id is not None
            else None
        )
        root_component_name = component_overrides.get(
            roots[0], report.nodes[roots[0]].arkui_component
        )
        if (
            root_node_id is not None
            and root_browser_node is not None
            and root_node_id in styles_by_id
            and is_viewport_page_root(
                root_component_name,
                root_browser_node,
                snapshot,
            )
        ):
            # Browser viewport pixels are not a portable application-window
            # constraint. The root must follow the ArkUI content area so safe
            # areas and device sizes do not push fixed-height children offscreen.
            styles_by_id[root_node_id]["width"] = "100%"
            styles_by_id[root_node_id]["height"] = "100%"
            # A transparent root filling the viewport shows the document
            # canvas in the browser. ArkUI paints nothing behind the page
            # root, so that colour has to move onto the root itself.
            if (
                "backgroundColor" not in styles_by_id[root_node_id]
                and snapshot.canvas_background_color is not None
            ):
                canvas_color = normalize_css_color(
                    snapshot.canvas_background_color
                )
                if canvas_color is not None:
                    styles_by_id[root_node_id]["backgroundColor"] = canvas_color
            if (
                root_component_name in {"Column", "Stack"}
                and root_browser_node.bbox[3]
                > snapshot.viewport_height + _VIEWPORT_EDGE_TOLERANCE
            ):
                # A root taller than the viewport is the browser's document
                # scroll; ArkUI clips instead, so the page needs a Scroll.
                # (A List root scrolls by itself and a Scroll root already
                # is one, which is why only plain containers qualify.)
                document_scroll_root_id = root_node_id
                diagnostics.append(ScreenIrAdapterDiagnostic(
                    code="UIBENCH_ARKUI_DOCUMENT_SCROLL_SYNTHESIZED",
                    severity="notice",
                    message=(
                        "The browser scrolls this page as a document; the "
                        "page content was exported inside a generated Scroll"
                    ),
                    node_id=root_node_id,
                ))
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
            definition = renderer.components.get(component_overrides.get(
                index, report.nodes[index].arkui_component
            ))
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
            component_overrides,
            generated_text_styles_by_id,
        ),
    }
    if document_scroll_root_id is not None:
        _wrap_document_scroll(screen_ir, document_scroll_root_id)
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
    "is_viewport_page_root",
    "normalize_page_name",
    "root_covers_viewport",
]
