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
    analyze_component_metadata,
    find_html_tree_depth_violation,
)
from uibench.arkui.resources import (
    HARMONY_MODEL_VERSION,
    HARMONY_SDK_VERSION,
    build_harmony_project,
    materialize_browser_assets,
    rewrite_arkts_resources,
)
from uibench.arkui.screen_ir import build_screen_ir
from uibench.arkui.snapshot import BrowserSnapshot

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BRIDGE_FILE = PROJECT_ROOT / "tools" / "arkui-export.mjs"
MAX_BRIDGE_OUTPUT_CHARS = 10_000_000


@dataclass(frozen=True)
class ArkUiExporterError(RuntimeError):
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
) -> dict[str, object]:
    """Export semantic annotations through canonical Screen IR v2."""
    _require_bounded_html_tree(html)
    report = analyze_component_metadata(html)
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
            "readiness": (
                "lossy" if any(
                    item["severity"] == "warning" for item in diagnostics
                ) else "ready"
            ),
            "errors": 0,
            "warnings": sum(
                item["severity"] == "warning" for item in diagnostics
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
