#!/usr/bin/env python3
"""Prepare, build, capture, and compare HTML-to-ArkUI visual cases."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pydantic import ValidationError  # noqa: E402

from uibench.arkui.exporter import ArkUiExporterError  # noqa: E402
from uibench.arkui.regression import (  # noqa: E402
    DEFAULT_DEVECO_STUDIO,
    DEFAULT_HDC,
    build_regression_run,
    capture_regression_run_hdc,
    compare_regression_run,
    normalize_hdc_capture,
    prepare_regression_case,
)
from uibench.arkui.hdc import probe_hdc  # noqa: E402
from uibench.arkui.visual_regression import VisualRegressionError  # noqa: E402


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare HTML-to-ArkUI projects and manage visual regression."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare = subparsers.add_parser(
        "prepare",
        help="Validate one browser capture and export its HarmonyOS project.",
    )
    prepare.add_argument("--case", required=True, type=Path)
    prepare.add_argument("--out", required=True, type=Path)

    build = subparsers.add_parser(
        "build",
        help="Compile a prepared project with DevEco's bundled Hvigor.",
    )
    build.add_argument("--run", required=True, type=Path)
    build.add_argument(
        "--deveco-studio",
        type=Path,
        default=DEFAULT_DEVECO_STUDIO,
    )
    build.add_argument("--timeout", type=float, default=180)

    compare = subparsers.add_parser(
        "compare",
        help="Compare a normalized ArkUI screenshot and generate diff metrics.",
    )
    compare.add_argument("--run", required=True, type=Path)
    compare.add_argument("--arkui-screenshot", required=True, type=Path)
    compare.add_argument("--pixel-threshold", type=int)

    probe = subparsers.add_parser(
        "probe-hdc",
        help="List local HDC targets without installing or launching an app.",
    )
    probe.add_argument("--hdc", type=Path, default=DEFAULT_HDC)
    probe.add_argument("--timeout", type=float, default=20)

    capture = subparsers.add_parser(
        "capture-hdc",
        help="Install a current-run HAP and preserve a raw HDC screenshot.",
    )
    capture.add_argument("--run", required=True, type=Path)
    capture.add_argument("--hdc", type=Path, default=DEFAULT_HDC)
    capture.add_argument("--target")
    capture.add_argument("--hap", type=Path)
    capture.add_argument("--timeout", type=float, default=210)
    capture.add_argument("--settle", type=float, default=2)

    normalize = subparsers.add_parser(
        "normalize-hdc",
        help="Explicitly crop and resample the current raw HDC PNG.",
    )
    normalize.add_argument("--run", required=True, type=Path)
    normalize.add_argument(
        "--crop",
        required=True,
        help="Raw physical-pixel crop as x,y,width,height.",
    )
    normalize.add_argument(
        "--scale",
        type=int,
        help="Required by identity/box-v1 and forbidden by area-v1.",
    )
    normalize.add_argument(
        "--content-viewport",
        required=True,
        help="Canonical case viewport as WIDTHxHEIGHT.",
    )
    normalize.add_argument(
        "--resample",
        required=True,
        choices=("identity", "box-v1", "area-v1"),
    )
    return parser


def _comma_integers(value: str, count: int, label: str) -> tuple[int, ...]:
    parts = value.split(",")
    if len(parts) != count:
        raise VisualRegressionError(
            "UIBENCH_HDC_NORMALIZATION_ARGUMENT_INVALID",
            f"{label} must contain {count} comma-separated integers",
        )
    try:
        return tuple(int(part) for part in parts)
    except ValueError as exc:
        raise VisualRegressionError(
            "UIBENCH_HDC_NORMALIZATION_ARGUMENT_INVALID",
            f"{label} must contain integers",
        ) from exc


def _viewport(value: str) -> tuple[int, int]:
    parts = value.lower().split("x")
    if len(parts) != 2:
        raise VisualRegressionError(
            "UIBENCH_HDC_NORMALIZATION_ARGUMENT_INVALID",
            "content viewport must use WIDTHxHEIGHT",
        )
    try:
        return int(parts[0]), int(parts[1])
    except ValueError as exc:
        raise VisualRegressionError(
            "UIBENCH_HDC_NORMALIZATION_ARGUMENT_INVALID",
            "content viewport must use integer dimensions",
        ) from exc


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "probe-hdc":
            probe = probe_hdc(args.hdc, timeout_seconds=args.timeout)
            print(json.dumps({
                "ok": True,
                "version": probe.version,
                "targetCount": len(probe.targets),
                "targets": [
                    {
                        "connectKey": target.connect_key,
                        "status": target.status,
                    }
                    for target in probe.targets
                ],
            }, ensure_ascii=False))
            return 0
        if args.command == "prepare":
            report = prepare_regression_case(args.case, args.out)
        elif args.command == "build":
            report = build_regression_run(
                args.run,
                deveco_studio=args.deveco_studio,
                timeout_seconds=args.timeout,
            )
        elif args.command == "compare":
            report = compare_regression_run(
                args.run,
                args.arkui_screenshot,
                pixel_threshold=args.pixel_threshold,
            )
        elif args.command == "capture-hdc":
            report = capture_regression_run_hdc(
                args.run,
                hdc_path=args.hdc,
                target=args.target,
                hap_path=args.hap,
                timeout_seconds=args.timeout,
                settle_seconds=args.settle,
            )
        else:
            crop_x, crop_y, crop_width, crop_height = _comma_integers(
                args.crop, 4, "crop"
            )
            content_width, content_height = _viewport(args.content_viewport)
            if args.resample == "area-v1" and args.scale is not None:
                raise VisualRegressionError(
                    "UIBENCH_HDC_NORMALIZATION_ARGUMENT_INVALID",
                    "area-v1 is defined by --crop and --content-viewport; "
                    "do not pass --scale",
                )
            if args.resample != "area-v1" and args.scale is None:
                raise VisualRegressionError(
                    "UIBENCH_HDC_NORMALIZATION_ARGUMENT_INVALID",
                    "identity and box-v1 require --scale",
                )
            report = normalize_hdc_capture(
                args.run,
                crop_x=crop_x,
                crop_y=crop_y,
                crop_width=crop_width,
                crop_height=crop_height,
                scale=args.scale,
                content_width=content_width,
                content_height=content_height,
                resample=args.resample,
            )
    except (
        ArkUiExporterError,
        VisualRegressionError,
        ValidationError,
        OSError,
        json.JSONDecodeError,
    ) as exc:
        error = (
            exc.to_dict()
            if isinstance(exc, ArkUiExporterError)
            else {
                "code": getattr(exc, "code", "UIBENCH_REGRESSION_INPUT_INVALID"),
                "message": str(exc),
            }
        )
        print(json.dumps({"ok": False, "error": error}, ensure_ascii=False))
        return 2

    print(json.dumps({
        "ok": True,
        "caseId": report["caseId"],
        "status": report["status"],
        "report": str(args.out / "report.json")
        if args.command == "prepare" else str(args.run / "report.json"),
    }, ensure_ascii=False))
    if args.command == "build":
        return 0 if report["capture"]["buildVerification"] == "passed" else 1
    return 1 if report["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
