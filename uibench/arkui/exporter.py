"""Bounded Python adapter for the html-to-arkui Node bridge."""
from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from uibench.arkui.metadata import (
    MAX_HTML_TREE_DEPTH,
    ComponentMetadataReport,
    analyze_component_metadata,
    find_html_tree_depth_violation,
)
from uibench.arkui.resources import (
    HARMONY_MODEL_VERSION,
    HARMONY_SDK_VERSION,
    HARMONY_WINDOW_BACKGROUND,
    build_harmony_project,
    materialize_browser_assets,
    rewrite_arkts_resources,
)
from uibench.arkui.screen_ir import (
    build_screen_ir,
    is_viewport_page_root,
    root_covers_viewport,
)
from uibench.arkui.snapshot import (
    BrowserComputedStyle,
    BrowserSnapshot,
    classify_css_color,
    is_opaque_css_color,
    normalize_css_color,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BRIDGE_FILE = PROJECT_ROOT / "tools" / "arkui-export.mjs"
MAX_BRIDGE_OUTPUT_CHARS = 10_000_000
_NON_EMPTY_SNAPSHOT_COMPUTED_FIELDS = ("display", "width", "height")


def _computed_style_field_alias(field_name: str) -> str:
    field = BrowserComputedStyle.model_fields[field_name]
    return str(field.serialization_alias or field.alias or field_name)


_CAPTURED_COMPUTED_STYLE_FIELDS = tuple(
    (
        field_name,
        _computed_style_field_alias(field_name),
    )
    for field_name in BrowserComputedStyle.model_fields
)


@dataclass
class ArkUiExporterError(RuntimeError):
    """Structured export failure addressed by a stable machine-readable code.

    ``message`` is the human-readable summary surfaced to the caller and UI;
    ``details`` carries optional JSON-serializable evidence such as the
    blocking diagnostics list or protocol field names.

    Deliberately not ``frozen``: when an exception leaves a generator context
    manager, ``contextlib`` restores ``exc.__traceback__`` with a plain Python
    assignment, which a frozen dataclass rejects — the exporter error would be
    replaced mid-flight by ``FrozenInstanceError``. Pinned by
    ``test_exporter_error_can_escape_contextmanager_without_being_replaced``.
    """

    code: str
    message: str
    details: object | None = None

    def __str__(self) -> str:
        return self.message

    def to_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "code": self.code,
            "message": self.message,
        }
        if self.details is not None:
            result["details"] = self.details
        return result


def _require_bounded_html_tree(html: str) -> None:
    violation = find_html_tree_depth_violation(html)
    if violation is None:
        return
    line, column = violation
    raise ArkUiExporterError(
        "UIBENCH_HTML_TREE_DEPTH_EXCEEDED",
        f"HTML nesting exceeds the supported depth of {MAX_HTML_TREE_DEPTH}",
        {
            "line": line,
            "column": column,
            "maxDepth": MAX_HTML_TREE_DEPTH,
        },
    )


def _require_complete_browser_snapshot(
    snapshot: BrowserSnapshot,
    report: ComponentMetadataReport,
) -> None:
    """Reject snapshots that cannot have come from a visible browser layout."""
    canvas_fields = {
        "canvasBackgroundColor": snapshot.canvas_background_color,
        "canvasBackgroundImage": snapshot.canvas_background_image,
    }
    missing_canvas_fields = [
        name
        for name, value in canvas_fields.items()
        if value is None or not value.strip()
    ]
    if missing_canvas_fields:
        raise ArkUiExporterError(
            "UIBENCH_BROWSER_SNAPSHOT_INCOMPLETE",
            "Browser-computed style snapshot is incomplete",
            {
                "mode": "annotated",
                "snapshotRequired": True,
                "reason": "canvas-background-fields-missing",
                "missingFields": missing_canvas_fields,
            },
        )

    assert snapshot.canvas_background_image is not None
    if snapshot.canvas_background_image.strip().lower() != "none":
        raise ArkUiExporterError(
            "UIBENCH_CANVAS_BACKGROUND_IMAGE_UNSUPPORTED",
            "Canvas background images and gradients are not supported by ArkUI export",
            {
                "mode": "annotated",
                "snapshotRequired": True,
                "reason": "canvas-background-image-unsupported",
                "backgroundImage": snapshot.canvas_background_image,
            },
        )

    assert snapshot.canvas_background_color is not None
    canvas_color_status = classify_css_color(snapshot.canvas_background_color)
    if canvas_color_status == "unsupported":
        raise ArkUiExporterError(
            "UIBENCH_CANVAS_BACKGROUND_COLOR_UNSUPPORTED",
            "Canvas background color uses unsupported CSS color syntax",
            {
                "mode": "annotated",
                "snapshotRequired": True,
                "reason": "canvas-background-color-unsupported",
                "backgroundColor": snapshot.canvas_background_color,
            },
        )

    for node in snapshot.nodes:
        # BrowserComputedStyle intentionally has defaults so older/internal
        # structure-only callers remain easy to construct.  For a downloadable
        # project, however, defaults must not masquerade as browser evidence:
        # every field emitted by arkuiSnapshotRuntime must have been present in
        # the original payload.  Empty strings are still valid computed values
        # for properties such as webkitLineClamp.
        missing_capture_fields = [
            alias
            for field_name, alias in _CAPTURED_COMPUTED_STYLE_FIELDS
            if field_name not in node.computed.model_fields_set
        ]
        if missing_capture_fields:
            raise ArkUiExporterError(
                "UIBENCH_BROWSER_SNAPSHOT_INCOMPLETE",
                "Browser-computed style snapshot is incomplete",
                {
                    "mode": "annotated",
                    "snapshotRequired": True,
                    "nodeId": node.node_id,
                    "reason": "computed-style-capture-fields-missing",
                    "missingFields": missing_capture_fields,
                },
            )

        missing_node_fields = [
            alias
            for field_name, alias in (
                ("direct_parent_node_id", "directParentNodeId"),
                ("is_flex_item", "isFlexItem"),
            )
            if field_name not in node.model_fields_set
        ]
        if missing_node_fields:
            raise ArkUiExporterError(
                "UIBENCH_BROWSER_SNAPSHOT_INCOMPLETE",
                "Browser-computed style snapshot is incomplete",
                {
                    "mode": "annotated",
                    "snapshotRequired": True,
                    "nodeId": node.node_id,
                    "reason": "node-capture-fields-missing",
                    "missingFields": missing_node_fields,
                },
            )

        if not node.visible:
            continue

        width, height = node.bbox[2:]
        if width <= 0 or height <= 0:
            raise ArkUiExporterError(
                "UIBENCH_BROWSER_SNAPSHOT_INCOMPLETE",
                "Browser-computed style snapshot is incomplete",
                {
                    "mode": "annotated",
                    "snapshotRequired": True,
                    "nodeId": node.node_id,
                    "reason": "visible-node-bbox-not-positive",
                    "bbox": list(node.bbox),
                },
            )

        missing_fields = [
            field
            for field in _NON_EMPTY_SNAPSHOT_COMPUTED_FIELDS
            if not getattr(node.computed, field).strip()
        ]
        if missing_fields:
            raise ArkUiExporterError(
                "UIBENCH_BROWSER_SNAPSHOT_INCOMPLETE",
                "Browser-computed style snapshot is incomplete",
                {
                    "mode": "annotated",
                    "snapshotRequired": True,
                    "nodeId": node.node_id,
                    "reason": "computed-style-fields-missing",
                    "missingFields": missing_fields,
                },
            )

    # ArkUI has no document canvas behind the page root, so the page root ends
    # up painting the whole background. That reproduces the browser unless two
    # different colors are visible at once: the refusals below are exactly the
    # cases where the canvas stays partly visible next to a different root
    # color, which one ArkUI background cannot express.
    if canvas_color_status == "supported":
        root_indices = [
            index for index, node in enumerate(report.nodes)
            if node.parent_index is None
        ]
        root_node_id = (
            report.nodes[root_indices[0]].node_id
            if len(root_indices) == 1 else None
        )
        browser_root = next(
            (node for node in snapshot.nodes if node.node_id == root_node_id),
            None,
        )
        if browser_root is not None:
            canvas_color = normalize_css_color(snapshot.canvas_background_color)
            root_color = normalize_css_color(
                browser_root.computed.background_color
            )
            reason: str | None = None
            if browser_root.direct_parent_node_id is not None:
                reason = "canvas-root-has-addressable-wrapper"
            elif root_color is None or root_color == canvas_color:
                # The browser shows one colour, but the device only reproduces
                # it where the root reaches: Screen IR promotes the canvas
                # colour onto a transparent root only when it is a viewport
                # page root, and a root painting the colour itself hides the
                # canvas only while covering the viewport. Everywhere else the
                # project window background shows instead, so any other canvas
                # colour still needs the root to span the captured page.
                canvas_reproduced = (
                    is_viewport_page_root(
                        report.nodes[root_indices[0]].arkui_component,
                        browser_root,
                        snapshot,
                    )
                    if root_color is None
                    else root_covers_viewport(browser_root, snapshot)
                )
                if not canvas_reproduced and canvas_color != (
                    normalize_css_color(HARMONY_WINDOW_BACKGROUND)
                ):
                    reason = (
                        "canvas-root-does-not-cover-viewport"
                        if not root_covers_viewport(browser_root, snapshot)
                        else "canvas-root-cannot-inherit-canvas"
                    )
            elif not is_opaque_css_color(browser_root.computed.background_color):
                reason = "canvas-root-is-translucent"
            elif not root_covers_viewport(browser_root, snapshot):
                # An opaque root in its own colour hides the canvas only where
                # it actually reaches; anywhere else the canvas shows through.
                reason = "canvas-root-does-not-cover-viewport"
            if reason is not None:
                raise ArkUiExporterError(
                    "UIBENCH_CANVAS_BACKGROUND_ROOT_UNSUPPORTED",
                    "Canvas background is not bound to the exported component root",
                    {
                        "mode": "annotated",
                        "snapshotRequired": True,
                        "reason": reason,
                        "nodeId": root_node_id,
                        "bbox": list(browser_root.bbox),
                        "viewport": {
                            "width": snapshot.viewport_width,
                            "height": snapshot.viewport_height,
                        },
                    },
                )


def run_arkui_bridge(
    payload: dict[str, object],
    *,
    timeout_seconds: float = 30,
) -> dict[str, object]:
    """Run one JSON request without shell expansion or filesystem writes."""
    node = shutil.which("node")
    if node is None:
        raise ArkUiExporterError(
            "ARKUI_NODE_NOT_FOUND",
            "Node.js 18 or newer is required for ArkUI export",
        )
    if not BRIDGE_FILE.is_file():
        raise ArkUiExporterError(
            "ARKUI_BRIDGE_NOT_FOUND",
            f"ArkUI bridge not found at {BRIDGE_FILE}",
        )
    try:
        completed = subprocess.run(
            [node, str(BRIDGE_FILE)],
            input=json.dumps(payload, ensure_ascii=False),
            text=True,
            capture_output=True,
            cwd=PROJECT_ROOT,
            env=os.environ.copy(),
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ArkUiExporterError(
            "ARKUI_BRIDGE_TIMEOUT",
            f"ArkUI export exceeded {timeout_seconds:g} seconds",
        ) from exc
    except OSError as exc:
        raise ArkUiExporterError(
            "ARKUI_BRIDGE_START_FAILED",
            f"Could not start ArkUI bridge: {exc}",
        ) from exc

    if len(completed.stdout) > MAX_BRIDGE_OUTPUT_CHARS:
        raise ArkUiExporterError(
            "ARKUI_BRIDGE_OUTPUT_TOO_LARGE",
            "ArkUI bridge output exceeded the 10 MB limit",
        )
    try:
        response = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        stderr = completed.stderr.strip()[:2000]
        raise ArkUiExporterError(
            "ARKUI_BRIDGE_INVALID_RESPONSE",
            "ArkUI bridge returned invalid JSON",
            {"stderr": stderr} if stderr else None,
        ) from exc
    if not isinstance(response, dict):
        raise ArkUiExporterError(
            "ARKUI_BRIDGE_INVALID_RESPONSE",
            "ArkUI bridge response must be an object",
        )
    if not response.get("ok"):
        error = response.get("error")
        if not isinstance(error, dict):
            error = {}
        raise ArkUiExporterError(
            str(error.get("code") or "ARKUI_EXPORT_FAILED"),
            str(error.get("message") or "ArkUI export failed"),
            error.get("details"),
        )
    result = response.get("result")
    if not isinstance(result, dict):
        raise ArkUiExporterError(
            "ARKUI_BRIDGE_INVALID_RESPONSE",
            "ArkUI bridge result must be an object",
        )
    return result


def export_annotated_html(
    html: str,
    *,
    page_name: str,
    page_description: str | None = None,
    viewport_width: int = 390,
    viewport_height: int = 844,
    snapshot: BrowserSnapshot | None = None,
    require_snapshot: bool = False,
) -> dict[str, object]:
    """Export semantic annotations through canonical Screen IR v2.

    ``require_snapshot`` is intended for user-facing project delivery.  The
    default preserves the explicit structure-only path used by internal tools
    and compatibility tests.
    """
    _require_bounded_html_tree(html)
    report = analyze_component_metadata(html)
    if require_snapshot and snapshot is not None:
        # A supplied delivery snapshot is its own fail-closed protocol gate.
        # Validate it before resource processing or Screen IR adaptation so an
        # incomplete capture is never obscured by downstream layout diagnostics.
        _require_complete_browser_snapshot(snapshot, report)
    resources = materialize_browser_assets(report, snapshot)
    built = build_screen_ir(
        report,
        page_name=page_name,
        page_description=page_description,
        snapshot=snapshot,
        resource_bindings=resources.bindings,
    )
    if built.screen_ir is None:
        raise ArkUiExporterError(
            "UIBENCH_SCREEN_IR_BLOCKED",
            "UIBench component metadata cannot be exported",
            [item.to_dict() for item in built.diagnostics],
        )
    if require_snapshot:
        if snapshot is None:
            raise ArkUiExporterError(
                "UIBENCH_BROWSER_SNAPSHOT_REQUIRED",
                (
                    "Annotated HarmonyOS project export requires a browser-"
                    "computed style snapshot"
                ),
                {
                    "mode": "annotated",
                    "snapshotRequired": True,
                },
            )
    rendered = run_arkui_bridge({
        "action": "render-screen-ir",
        "screenIr": built.screen_ir,
    })
    validation = rendered.get("validation")
    component_counts = (
        validation.get("componentCounts", {})
        if isinstance(validation, dict) else {}
    )
    diagnostics = [item.to_dict() for item in built.diagnostics]
    diagnostics.extend({
        "code": item.code,
        "severity": "warning",
        "message": item.message,
        "nodeId": item.node_ids[0] if item.node_ids else None,
    } for item in resources.rejected)
    ark_ts = rewrite_arkts_resources(str(rendered["arkTs"]), resources)
    rendered_screen_ir = rendered["screenIr"]
    rendered_page = (
        rendered_screen_ir.get("page", {})
        if isinstance(rendered_screen_ir, dict) else {}
    )
    rendered_page_name = str(
        rendered_page.get("name") or "GeneratedPage"
    ) if isinstance(rendered_page, dict) else "GeneratedPage"
    bundle_bytes, bundle_files, bundle_name = build_harmony_project(
        rendered_page_name,
        ark_ts,
        resources,
    )
    actual_viewport_width = (
        snapshot.viewport_width if snapshot is not None else viewport_width
    )
    actual_viewport_height = (
        snapshot.viewport_height if snapshot is not None else viewport_height
    )
    return {
        "kind": "uibench-arkui-export",
        "exportVersion": 1,
        "mode": "annotated",
        "screenIr": rendered_screen_ir,
        "arkTs": ark_ts,
        "viewport": {
            "width": actual_viewport_width,
            "height": actual_viewport_height,
            "source": (
                "browser-snapshot" if snapshot is not None else "uibench-options"
            ),
        },
        "snapshot": (
            None if snapshot is None else {
                "snapshotVersion": snapshot.snapshot_version,
                "theme": snapshot.theme,
                "tokenTheme": snapshot.token_theme,
                "canvasBackgroundColor": snapshot.canvas_background_color,
                "canvasBackgroundImage": snapshot.canvas_background_image,
                "nodes": len(snapshot.nodes),
            }
        ),
        "assets": resources.to_dict(),
        "bundle": {
            "kind": "uibench-harmonyos-project",
            "projectVersion": 1,
            "filename": f"{rendered_page_name}_HarmonyOS.zip",
            "mimeType": "application/zip",
            "byteLength": len(bundle_bytes),
            "contentBase64": base64.b64encode(bundle_bytes).decode("ascii"),
            "files": list(bundle_files),
            "completeProject": True,
            "bundleName": bundle_name,
            "model": "stageMode",
            "modelVersion": HARMONY_MODEL_VERSION,
            "targetSdkVersion": HARMONY_SDK_VERSION,
            "compatibleSdkVersion": HARMONY_SDK_VERSION,
            "buildVerification": "not-run",
        },
        "diagnostics": diagnostics,
        "quality": {
            # Only a warning means the project can no longer look like the
            # captured page; a notice just records a rewritten annotation.
            "readiness": (
                "lossy" if any(
                    item["severity"] == "warning" for item in diagnostics
                ) else "ready"
            ),
            "errors": 0,
            "warnings": sum(
                item["severity"] == "warning" for item in diagnostics
            ),
            "notices": sum(
                item["severity"] == "notice" for item in diagnostics
            ),
            "componentCounts": component_counts,
        },
    }


def export_generic_html(
    html: str,
    *,
    page_name: str,
    page_description: str | None = None,
    viewport_width: int = 390,
    viewport_height: int = 844,
    snapshot: BrowserSnapshot | None = None,
) -> dict[str, object]:
    """Use html-to-arkui's source-agnostic best-effort HTML converter."""
    _require_bounded_html_tree(html)
    del snapshot  # Generic conversion deliberately does not consume UIBench metadata.
    options: dict[str, object] = {
        "mode": "best-effort",
        "viewport": {"width": viewport_width, "height": viewport_height},
        "pageName": page_name,
        "includeSourceMetadata": True,
    }
    if page_description:
        options["pageDescription"] = page_description
    result = run_arkui_bridge({
        "action": "convert-html",
        "html": html,
        "options": options,
    })
    return {
        "kind": "uibench-arkui-export",
        "exportVersion": 1,
        "mode": "generic",
        **result,
    }


__all__ = [
    "ArkUiExporterError",
    "export_annotated_html",
    "export_generic_html",
    "run_arkui_bridge",
]
