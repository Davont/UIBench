#!/usr/bin/env python3
"""Materialize the task-overview regression as compile-ready artifacts."""
from __future__ import annotations

import argparse
import base64
import copy
import json
import os
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.task_overview_fixture import (  # noqa: E402
    build_task_overview_snapshot,
    load_task_overview_html,
)
from uibench.arkui.exporter import export_annotated_html  # noqa: E402


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def export_fixture(output_dir: Path) -> tuple[Path, ...]:
    html = load_task_overview_html()
    snapshot = build_task_overview_snapshot(html)
    result = export_annotated_html(
        html,
        page_name="TaskOverview",
        snapshot=snapshot,
        require_snapshot=True,
    )
    if result.get("quality", {}).get("readiness") != "ready":
        raise RuntimeError("task-overview fixture did not produce a ready export")

    bundle = result.get("bundle")
    if not isinstance(bundle, dict):
        raise RuntimeError("task-overview export did not include a project bundle")
    encoded_project = bundle.get("contentBase64")
    if not isinstance(encoded_project, str):
        raise RuntimeError("task-overview project bundle has no contentBase64")
    project = base64.b64decode(encoded_project, validate=True)
    if len(project) != bundle.get("byteLength"):
        raise RuntimeError("task-overview project bundle byte length is invalid")

    summary = copy.deepcopy(result)
    summary.pop("arkTs", None)
    summary_bundle = summary.get("bundle")
    if not isinstance(summary_bundle, dict):
        raise RuntimeError("task-overview export summary has no bundle metadata")
    summary_bundle.pop("contentBase64", None)
    summary["artifacts"] = {
        "html": "screen.html",
        "browserSnapshot": "browser-snapshot.json",
        "arkTs": "page.ets",
        "project": "project.zip",
    }

    output_dir = output_dir.resolve()
    if output_dir.exists() and not output_dir.is_dir():
        raise NotADirectoryError(f"artifact output is not a directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = (
        output_dir / "screen.html",
        output_dir / "browser-snapshot.json",
        output_dir / "page.ets",
        output_dir / "project.zip",
        output_dir / "export-summary.json",
    )
    _atomic_write(artifacts[0], html.encode("utf-8"))
    _atomic_write(
        artifacts[1],
        _canonical_json(snapshot.model_dump(
            mode="json",
            by_alias=True,
            exclude_none=True,
        )),
    )
    _atomic_write(artifacts[2], str(result["arkTs"]).encode("utf-8"))
    _atomic_write(artifacts[3], project)
    _atomic_write(artifacts[4], _canonical_json(summary))
    return artifacts


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Export the deterministic task-overview fixture for local "
            "HarmonyOS compile/install verification."
        ),
    )
    parser.add_argument(
        "--out",
        required=True,
        type=Path,
        metavar="DIR",
        help="directory that receives the five canonical artifacts",
    )
    args = parser.parse_args()
    artifacts = export_fixture(args.out)
    print(json.dumps({
        "ok": True,
        "artifacts": [str(path) for path in artifacts],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
