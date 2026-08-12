"""Offline preparation and comparison for HTML-to-ArkUI visual cases."""
from __future__ import annotations

import base64
import binascii
import errno
import hashlib
import json
import math
import os
import re
import shutil
import stat
import subprocess
import time
import uuid
import zipfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Literal

if os.name == "nt":
    import msvcrt
else:
    import fcntl

from pydantic import BaseModel, ConfigDict, Field, model_validator

from uibench.arkui import exporter
from uibench.arkui.hdc import (
    DEFAULT_HDC,
    HdcCaptureError,
    capture_hdc_png,
    inspect_hap,
)
from uibench.arkui.regression_harness import inject_regression_harness
from uibench.arkui.snapshot import BrowserSnapshot
from uibench.arkui.visual_regression import (
    MAX_NORMALIZED_EDGE,
    MAX_NORMALIZED_PIXELS,
    MAX_SCREENSHOT_PNG_BYTES,
    PixelCrop,
    PngNormalizationSpec,
    VisualRegressionError,
    compare_png_bytes,
    decode_png,
    normalize_png_bytes,
    read_png_file,
)

CASE_VERSION = 1
REPORT_VERSION = 1
_CASE_ID_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
_COMPARISON_ID_RE = re.compile(r"^[0-9a-f]{32}$")
_COMPARISON_TEMP_RE = re.compile(r"^\.[0-9a-f]{32}\.tmp$")
_ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*m")
_NORMALIZATION_V1_SPEC_KEYS = (
    "normalizationVersion",
    "cropPx",
    "scale",
    "contentViewport",
    "resample",
)
_NORMALIZATION_V2_SPEC_KEYS = (
    "normalizationVersion",
    "source",
    "target",
    "resample",
)
DEFAULT_DEVECO_STUDIO = Path("/Applications/DevEco-Studio.app")
_PREPARATION_ARTIFACTS = (
    "screenshots/browser.png",
    "browser-snapshot.json",
    "export/screen-ir.json",
    "export/page.ets",
    "export/project.zip",
    "export/export-summary.json",
)


class RegressionViewport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    width: int = Field(ge=240, le=3840)
    height: int = Field(ge=240, le=3840)


class RegressionThresholds(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    pixel_threshold: int = Field(default=0, alias="pixelThreshold", ge=0, le=255)
    max_different_ratio: float | None = Field(
        default=None, alias="maxDifferentRatio", ge=0, le=1
    )
    max_mean_absolute_error: float | None = Field(
        default=None, alias="maxMeanAbsoluteError", ge=0, le=255
    )


class RegressionCase(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    case_version: Literal[1] = Field(alias="caseVersion")
    case_id: str = Field(alias="id", min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=200)
    page_name: str = Field(alias="pageName", min_length=1, max_length=100)
    html: str = Field(min_length=1, max_length=300)
    snapshot: str = Field(min_length=1, max_length=300)
    browser_screenshot: str = Field(
        alias="browserScreenshot", min_length=1, max_length=300
    )
    viewport: RegressionViewport
    theme: Literal["light", "dark"]
    token_theme: Literal["harmonyos", "spotify", "netflix", "notion"] = Field(
        alias="tokenTheme"
    )
    coverage: list[str] = Field(default_factory=list, max_length=30)
    thresholds: RegressionThresholds = Field(default_factory=RegressionThresholds)

    @model_validator(mode="after")
    def stable_identifiers_and_paths(self) -> "RegressionCase":
        if not _CASE_ID_RE.fullmatch(self.case_id):
            raise ValueError("case id must be a lower-case kebab path segment")
        for value in (self.html, self.snapshot, self.browser_screenshot):
            path = Path(value)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("case artifact paths must stay inside the case directory")
        return self


def load_regression_case(path: str | Path) -> RegressionCase:
    case_path = Path(path)
    return RegressionCase.model_validate_json(case_path.read_text(encoding="utf-8"))


def _case_artifact(case_path: Path, relative_path: str) -> Path:
    case_root = case_path.resolve().parent
    candidate = (case_root / relative_path).resolve()
    if not candidate.is_relative_to(case_root):
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_PATH_INVALID",
            "Case artifact path escapes the case directory",
        )
    if not candidate.is_file():
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_ARTIFACT_MISSING",
            f"Case artifact does not exist: {relative_path}",
        )
    return candidate


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary_path.write_text(
            json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary_path.replace(path)
    finally:
        temporary_path.unlink(missing_ok=True)


def _artifact(
    path: Path,
    run_directory: Path,
    *,
    reported_path: str | None = None,
) -> dict[str, object]:
    content = path.read_bytes()
    return {
        "path": reported_path or path.relative_to(run_directory).as_posix(),
        "byteLength": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
    }


def _artifact_descriptor(
    report: dict[str, object],
    relative_path: str,
) -> dict[str, object]:
    artifacts = report.get("artifacts")
    matches = [
        artifact for artifact in artifacts
        if isinstance(artifact, dict) and artifact.get("path") == relative_path
    ] if isinstance(artifacts, list) else []
    if len(matches) != 1:
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_ARTIFACT_DESCRIPTOR_INVALID",
            f"Report must contain exactly one artifact: {relative_path}",
        )
    return matches[0]


def _verify_artifact_descriptor(
    run_root: Path,
    descriptor: dict[str, object],
) -> tuple[Path, bytes]:
    reported_path = descriptor.get("path")
    relative_path = Path(reported_path) if isinstance(reported_path, str) else Path()
    if (
        not isinstance(reported_path, str)
        or not reported_path
        or relative_path.is_absolute()
        or ".." in relative_path.parts
    ):
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_ARTIFACT_MISSING",
            "Reported artifact is missing or outside the run directory",
        )
    path = (run_root / relative_path).absolute()
    try:
        resolved = path.resolve()
    except (OSError, RuntimeError) as exc:
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_ARTIFACT_MISSING",
            "Reported artifact is missing or outside the run directory",
        ) from exc
    if (
        not path.is_relative_to(run_root)
        or resolved != path
        or path.is_symlink()
        or not path.is_file()
    ):
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_ARTIFACT_MISSING",
            "Reported artifact is missing or outside the run directory",
        )
    expected_length = descriptor.get("byteLength")
    if (
        type(expected_length) is not int
        or expected_length < 0
        or expected_length > MAX_SCREENSHOT_PNG_BYTES
    ):
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_ARTIFACT_MISMATCH",
            "Reported artifact has an invalid byte length",
        )
    try:
        with path.open("rb") as handle:
            content = handle.read(MAX_SCREENSHOT_PNG_BYTES + 1)
    except OSError as exc:
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_ARTIFACT_MISSING",
            "Reported artifact cannot be read",
        ) from exc
    if (
        expected_length != len(content)
        or descriptor.get("sha256") != hashlib.sha256(content).hexdigest()
    ):
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_ARTIFACT_MISMATCH",
            "Reported artifact no longer matches its descriptor",
        )
    return path, content


def _normalization_spec(value: object) -> dict[str, object] | None:
    """Return a strictly validated normalization spec projection."""
    if not isinstance(value, dict):
        return None
    version = value.get("normalizationVersion")
    if type(version) is not int:
        return None
    if version == 1:
        spec = {key: value.get(key) for key in _NORMALIZATION_V1_SPEC_KEYS}
        crop = spec["cropPx"]
        scale = spec["scale"]
        viewport = spec["contentViewport"]
        if (
            not isinstance(crop, dict)
            or set(crop) != {"x", "y", "width", "height"}
            or not isinstance(scale, dict)
            or set(scale) != {"pixelsPerContentPixel"}
            or not isinstance(viewport, dict)
            or set(viewport) != {"width", "height"}
            or any(type(crop[key]) is not int for key in crop)
            or any(type(scale[key]) is not int for key in scale)
            or any(type(viewport[key]) is not int for key in viewport)
        ):
            return None
        pixels_per_content_pixel = scale["pixelsPerContentPixel"]
        if (
            crop["x"] < 0
            or crop["y"] < 0
            or crop["width"] <= 0
            or crop["height"] <= 0
            or not 1 <= pixels_per_content_pixel <= 8
            or viewport["width"] <= 0
            or viewport["height"] <= 0
            or crop["width"] != viewport["width"] * pixels_per_content_pixel
            or crop["height"] != viewport["height"] * pixels_per_content_pixel
            or spec["resample"]
            != ("identity" if pixels_per_content_pixel == 1 else "box-v1")
        ):
            return None
        return spec
    if version != 2:
        return None
    spec = {key: value.get(key) for key in _NORMALIZATION_V2_SPEC_KEYS}
    source = spec["source"]
    target = spec["target"]
    if (
        not isinstance(source, dict)
        or set(source) != {"cropPx"}
        or not isinstance(target, dict)
        or set(target) != {"contentViewport"}
    ):
        return None
    crop = source.get("cropPx")
    viewport = target.get("contentViewport")
    if (
        not isinstance(crop, dict)
        or set(crop) != {"x", "y", "width", "height"}
        or not isinstance(viewport, dict)
        or set(viewport) != {"width", "height"}
        or any(type(crop[key]) is not int for key in crop)
        or any(type(viewport[key]) is not int for key in viewport)
        or crop["x"] < 0
        or crop["y"] < 0
        or crop["width"] <= 0
        or crop["height"] <= 0
        or viewport["width"] <= 0
        or viewport["height"] <= 0
        or viewport["width"] > MAX_NORMALIZED_EDGE
        or viewport["height"] > MAX_NORMALIZED_EDGE
        or viewport["width"] > MAX_NORMALIZED_PIXELS // viewport["height"]
        or spec["resample"] != "area-v1"
    ):
        return None
    return spec


def _normalization_content_viewport(
    spec: dict[str, object] | None,
) -> dict[str, int] | None:
    if not isinstance(spec, dict):
        return None
    if spec.get("normalizationVersion") == 1:
        viewport = spec.get("contentViewport")
    else:
        target = spec.get("target")
        viewport = target.get("contentViewport") if isinstance(target, dict) else None
    return viewport if isinstance(viewport, dict) else None


def _ensure_managed_directory(path: Path, owner_root: Path) -> Path:
    """Create one run-owned directory without following symlink components."""
    owner = owner_root.resolve()
    candidate = path.absolute()
    try:
        relative = candidate.relative_to(owner)
    except ValueError as exc:
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_MANAGED_PATH_INVALID",
            "Regression artifact directory escapes the run directory",
        ) from exc
    current = owner
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise VisualRegressionError(
                "UIBENCH_REGRESSION_MANAGED_PATH_INVALID",
                "Regression artifact directories must not be symbolic links",
            )
        if current.exists():
            if not current.is_dir():
                raise VisualRegressionError(
                    "UIBENCH_REGRESSION_MANAGED_PATH_INVALID",
                    "Regression artifact path is not a directory",
                )
        else:
            current.mkdir()
    resolved = candidate.resolve()
    if resolved != candidate or not resolved.is_relative_to(owner):
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_MANAGED_PATH_INVALID",
            "Regression artifact directory is not a normal run-owned path",
        )
    return candidate


def _is_within_same_filesystem_directory(path: Path, directory: Path) -> bool:
    """Use filesystem identity to catch case and symlink aliases of a root."""
    try:
        if not directory.is_dir():
            return False
    except OSError:
        return False
    for candidate in (path, *path.parents):
        try:
            if candidate.samefile(directory):
                return True
        except (OSError, RuntimeError):
            continue
    return False


def _prune_unreferenced_versions(
    versions_root: Path,
    *,
    keep_id: str,
    owner_root: Path,
) -> None:
    """Best-effort cleanup of version directories owned by this pipeline."""
    try:
        safe_root = _ensure_managed_directory(versions_root, owner_root)
        candidates = list(safe_root.iterdir())
    except (OSError, VisualRegressionError):
        return
    for candidate in candidates:
        if candidate.name == keep_id:
            continue
        if not (
            _COMPARISON_ID_RE.fullmatch(candidate.name)
            or _COMPARISON_TEMP_RE.fullmatch(candidate.name)
        ):
            continue
        if candidate.is_symlink() or not candidate.is_dir():
            continue
        shutil.rmtree(candidate, ignore_errors=True)


def _export_summary(result: dict[str, object]) -> dict[str, object]:
    bundle = result.get("bundle")
    safe_bundle = {
        key: value
        for key, value in bundle.items()
        if key != "contentBase64"
    } if isinstance(bundle, dict) else bundle
    return {
        key: value
        for key, value in result.items()
        if key not in {"arkTs", "screenIr", "bundle"}
    } | {"bundle": safe_bundle}


def _load_report(run_root: Path) -> dict[str, object]:
    report_path = run_root / "report.json"
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_REPORT_MISSING",
            "Run directory does not contain report.json",
        ) from exc
    if (
        not isinstance(report, dict)
        or report.get("kind") != "uibench-arkui-visual-regression"
        or report.get("reportVersion") != REPORT_VERSION
    ):
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_REPORT_INVALID",
            "Run directory does not contain a supported regression report",
        )
    return report


def _require_complete_preparation(
    report: dict[str, object],
    run_root: Path,
) -> None:
    capture = report.get("capture")
    artifacts = report.get("artifacts")
    if not isinstance(capture, dict) or capture.get("browser") != "provided":
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_PREPARATION_INCOMPLETE",
            "Regression preparation has not completed successfully",
        )
    indexed = {
        str(artifact.get("path")): artifact
        for artifact in artifacts if isinstance(artifact, dict)
    } if isinstance(artifacts, list) else {}
    for relative_path in _PREPARATION_ARTIFACTS:
        descriptor = indexed.get(relative_path)
        path = run_root / relative_path
        if not isinstance(descriptor, dict) or not path.is_file():
            raise VisualRegressionError(
                "UIBENCH_REGRESSION_PREPARATION_INCOMPLETE",
                f"Prepared artifact is missing: {relative_path}",
            )
        digest = hashlib.sha256()
        byte_length = 0
        try:
            with path.open("rb") as handle:
                while chunk := handle.read(1024 * 1024):
                    byte_length += len(chunk)
                    digest.update(chunk)
        except OSError as exc:
            raise VisualRegressionError(
                "UIBENCH_REGRESSION_PREPARATION_INCOMPLETE",
                f"Prepared artifact cannot be read: {relative_path}",
            ) from exc
        if (
            descriptor.get("byteLength") != byte_length
            or descriptor.get("sha256") != digest.hexdigest()
        ):
            raise VisualRegressionError(
                "UIBENCH_REGRESSION_PREPARATION_INCOMPLETE",
                f"Prepared artifact no longer matches its report: {relative_path}",
            )


@contextmanager
def _exclusive_run_lock(run_root: Path) -> Iterator[None]:
    """Reject concurrent mutations of one regression run across processes."""
    lock_path = run_root / ".arkui-regression.lock"
    try:
        lock_handle = lock_path.open("a+b")
    except FileNotFoundError as exc:
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_REPORT_MISSING",
            "Run directory does not exist",
        ) from exc
    with lock_handle:
        acquired = False
        try:
            try:
                if os.name == "nt":
                    lock_handle.seek(0, os.SEEK_END)
                    if lock_handle.tell() == 0:
                        lock_handle.write(b"\0")
                        lock_handle.flush()
                    lock_handle.seek(0)
                    msvcrt.locking(lock_handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    fcntl.flock(
                        lock_handle.fileno(),
                        fcntl.LOCK_EX | fcntl.LOCK_NB,
                    )
                acquired = True
            except OSError as exc:
                if exc.errno not in {
                    errno.EACCES,
                    errno.EAGAIN,
                    errno.EDEADLK,
                }:
                    raise
                raise VisualRegressionError(
                    "UIBENCH_REGRESSION_RUN_BUSY",
                    "Another regression command is already mutating this run",
                ) from exc
            yield
        finally:
            if acquired:
                if os.name == "nt":
                    lock_handle.seek(0)
                    msvcrt.locking(lock_handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)


def _extract_project(archive_path: Path, destination: Path) -> None:
    try:
        archive = zipfile.ZipFile(archive_path)
    except (OSError, zipfile.BadZipFile) as exc:
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_PROJECT_INVALID",
            "Prepared HarmonyOS project ZIP is missing or invalid",
        ) from exc
    with archive:
        entries = archive.infolist()
        if len(entries) > 5000 or sum(item.file_size for item in entries) > 50_000_000:
            raise VisualRegressionError(
                "UIBENCH_REGRESSION_PROJECT_TOO_LARGE",
                "Prepared HarmonyOS project exceeds regression build limits",
            )
        for item in entries:
            path = Path(item.filename)
            mode = item.external_attr >> 16
            if (
                path.is_absolute()
                or ".." in path.parts
                or stat.S_ISLNK(mode)
            ):
                raise VisualRegressionError(
                    "UIBENCH_REGRESSION_PROJECT_PATH_INVALID",
                    "Prepared HarmonyOS project contains an unsafe ZIP entry",
                )
        destination.mkdir(parents=True, exist_ok=True)
        archive.extractall(destination)


def _build_regression_run_locked(
    run_directory: str | Path,
    *,
    deveco_studio: str | Path = DEFAULT_DEVECO_STUDIO,
    timeout_seconds: float = 180,
) -> dict[str, object]:
    """Compile a prepared project with DevEco's bundled API 22 toolchain."""
    if (
        not math.isfinite(timeout_seconds)
        or timeout_seconds <= 0
        or timeout_seconds > 3600
    ):
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_BUILD_TIMEOUT_INVALID",
            "Build timeout must be greater than 0 and no more than 3600 seconds",
        )
    run_root = Path(run_directory).resolve()
    report = _load_report(run_root)
    _require_complete_preparation(report, run_root)
    studio = Path(deveco_studio).resolve()
    node = studio / "Contents/tools/node/bin/node"
    hvigor = studio / "Contents/tools/hvigor/bin/hvigorw.js"
    sdk = studio / "Contents/sdk"
    java_home = studio / "Contents/jbr/Contents/Home"
    missing = [
        str(path) for path in (node, hvigor, sdk, java_home)
        if not path.exists()
    ]
    if missing:
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_DEVECO_TOOLCHAIN_MISSING",
            "DevEco toolchain is incomplete: " + ", ".join(missing),
        )
    project_root = run_root / "project"
    if project_root.is_symlink() or (
        project_root.exists() and not project_root.is_dir()
    ):
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_PROJECT_DIRECTORY_INVALID",
            "Regression project path must be a normal directory",
        )
    report_path = run_root / "report.json"
    screenshots_root = _ensure_managed_directory(
        run_root / "screenshots", run_root
    )
    capture = dict(report.get("capture") or {})
    capture.update({
        "buildVerification": "running",
        "buildExitCode": None,
        "buildTimedOut": False,
        "hapSigning": "unknown",
    })
    report["capture"] = capture
    if report.get("visualStatus") == "failed":
        report["status"] = "failed"
        report["statusReason"] = "Visual thresholds exceeded"
    else:
        report["status"] = "incomplete"
        report["statusReason"] = "DevEco build verification is running"
    existing_artifacts = [
        artifact for artifact in report.get("artifacts", [])
        if isinstance(artifact, dict)
        and artifact.get("path") != "build/hvigor.log"
        and not str(artifact.get("path", "")).startswith(
            "project/entry/build/"
        )
        and not str(artifact.get("path", "")).startswith(
            "screenshots/comparisons/"
        )
        and not str(artifact.get("path", "")).startswith(
            "screenshots/normalizations/"
        )
        and not str(artifact.get("path", "")).startswith(
            "screenshots/hdc/"
        )
    ]
    capture["arkui"] = "pending"
    capture.pop("arkuiProvider", None)
    capture.pop("hdc", None)
    report["metrics"] = None
    for key in ("visualStatus", "failedChecks", "comparisonId"):
        report.pop(key, None)
    report["artifacts"] = existing_artifacts
    # Commit the non-passing transition before removing any previous build
    # evidence. A crash from this point can leave an incomplete run, never a
    # stale report that still claims the deleted HAP passed.
    _write_json(report_path, report)
    for version_root in ("comparisons", "normalizations", "hdc"):
        _prune_unreferenced_versions(
            screenshots_root / version_root,
            keep_id="",
            owner_root=run_root,
        )
    try:
        if project_root.exists():
            # This directory is exclusively generated from export/project.zip.
            # Recreate it so a failed rebuild can never reuse a stale HAP.
            shutil.rmtree(project_root)
        _extract_project(run_root / "export/project.zip", project_root)
    except (OSError, VisualRegressionError):
        capture["buildVerification"] = "failed"
        report["status"] = "failed"
        report["statusReason"] = "DevEco project preparation failed"
        _write_json(report_path, report)
        raise
    command = [
        str(node),
        str(hvigor),
        "assembleHap",
        "--mode", "module",
        "-p", "product=default",
        "-p", "module=entry@default",
        "-p", "buildMode=debug",
        "--no-daemon",
    ]
    environment = os.environ.copy()
    environment.update({
        "DEVECO_SDK_HOME": str(sdk),
        "JAVA_HOME": str(java_home),
    })
    timed_out = False
    try:
        completed = subprocess.run(
            command,
            cwd=project_root,
            env=environment,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        exit_code = completed.returncode
        output = completed.stdout + completed.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        exit_code = 124
        output = "".join(
            part.decode(errors="replace") if isinstance(part, bytes) else part or ""
            for part in (exc.stdout, exc.stderr)
        ) + f"\nBuild timed out after {timeout_seconds:g} seconds\n"
    except OSError as exc:
        capture["buildVerification"] = "failed"
        report["status"] = "failed"
        report["statusReason"] = "DevEco build could not be started"
        _write_json(report_path, report)
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_BUILD_START_FAILED",
            f"Could not start DevEco build: {exc}",
        ) from exc
    output = _ANSI_ESCAPE_RE.sub("", output)
    build_root = run_root / "build"
    build_root.mkdir(parents=True, exist_ok=True)
    log_path = build_root / "hvigor.log"
    log_path.write_text(output, encoding="utf-8")
    discovered_haps = sorted(
        project_root.glob("entry/build/default/outputs/default/*.hap")
    )
    passed = exit_code == 0 and bool(discovered_haps)
    hap_files = discovered_haps if passed else []
    signed_haps = [
        item for item in hap_files
        if "signed" in item.name.lower() and "unsigned" not in item.name.lower()
    ]
    unsigned_haps = [
        item for item in hap_files if "unsigned" in item.name.lower()
    ]
    capture.update({
        "buildVerification": "passed" if passed else "failed",
        "buildExitCode": exit_code,
        "buildTimedOut": timed_out,
        "hapSigning": (
            "signed" if signed_haps
            else "unsigned" if unsigned_haps
            else "unknown"
        ),
        "hapSignatureVerification": "not-verified",
    })
    report["capture"] = capture
    visual_status = report.get("visualStatus")
    if not passed:
        report["status"] = "failed"
        report["statusReason"] = "DevEco build verification failed"
    elif visual_status in {"observed", "passed", "failed"}:
        report["status"] = visual_status
        report["statusReason"] = {
            "observed": "Metrics recorded without acceptance thresholds",
            "passed": "Visual thresholds satisfied",
            "failed": "Visual thresholds exceeded",
        }[visual_status]
    else:
        report["status"] = "incomplete"
        report["statusReason"] = "ArkUI screenshot has not been supplied"
    report["artifacts"] = existing_artifacts + [
        _artifact(log_path, run_root),
        *(_artifact(path, run_root) for path in hap_files),
    ]
    _write_json(report_path, report)
    return report


def build_regression_run(
    run_directory: str | Path,
    *,
    deveco_studio: str | Path = DEFAULT_DEVECO_STUDIO,
    timeout_seconds: float = 180,
) -> dict[str, object]:
    """Compile one prepared run while holding its cross-process lock."""
    run_root = Path(run_directory).resolve()
    with _exclusive_run_lock(run_root):
        return _build_regression_run_locked(
            run_root,
            deveco_studio=deveco_studio,
            timeout_seconds=timeout_seconds,
        )


def _prepare_regression_case_locked(
    case_file: str | Path,
    run_directory: str | Path,
) -> dict[str, object]:
    """Validate captured browser inputs and export a reproducible project."""
    case_path = Path(case_file)
    case = load_regression_case(case_path)
    html_path = _case_artifact(case_path, case.html)
    snapshot_path = _case_artifact(case_path, case.snapshot)
    browser_path = _case_artifact(case_path, case.browser_screenshot)

    snapshot = BrowserSnapshot.model_validate_json(
        snapshot_path.read_text(encoding="utf-8")
    )
    expected_viewport = (case.viewport.width, case.viewport.height)
    if (snapshot.viewport_width, snapshot.viewport_height) != expected_viewport:
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_SNAPSHOT_VIEWPORT_MISMATCH",
            "Browser snapshot viewport does not match case.json",
        )
    if snapshot.theme != case.theme or snapshot.token_theme != case.token_theme:
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_SNAPSHOT_THEME_MISMATCH",
            "Browser snapshot theme does not match case.json",
        )
    browser_png = read_png_file(browser_path)
    browser_image = decode_png(browser_png)
    if (browser_image.width, browser_image.height) != expected_viewport:
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_BROWSER_VIEWPORT_MISMATCH",
            "Browser screenshot dimensions do not match case.json",
        )

    result = exporter.export_annotated_html(
        html_path.read_text(encoding="utf-8"),
        page_name=case.page_name,
        viewport_width=case.viewport.width,
        viewport_height=case.viewport.height,
        snapshot=snapshot,
    )
    bundle = result.get("bundle")
    if not isinstance(bundle, dict):
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_BUNDLE_MISSING",
            "ArkUI export did not return a project bundle",
        )
    try:
        project_bytes = base64.b64decode(
            str(bundle.get("contentBase64") or ""), validate=True
        )
    except (binascii.Error, ValueError) as exc:
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_BUNDLE_INVALID",
            "ArkUI project bundle is not valid base64",
        ) from exc
    if len(project_bytes) != bundle.get("byteLength"):
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_BUNDLE_LENGTH_MISMATCH",
            "ArkUI project bundle length does not match its metadata",
        )
    canonical_arkts = result.get("arkTs")
    if not isinstance(canonical_arkts, str):
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_ARKTS_MISSING",
            "ArkUI export did not return canonical ArkTS source",
        )
    harnessed_project = inject_regression_harness(
        project_bytes,
        canonical_page=canonical_arkts,
        viewport_width=case.viewport.width,
        viewport_height=case.viewport.height,
    )
    project_bytes = harnessed_project.content
    harness_provenance = harnessed_project.provenance
    export_summary = _export_summary(result)
    summary_bundle = export_summary.get("bundle")
    if not isinstance(summary_bundle, dict):
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_BUNDLE_MISSING",
            "ArkUI export summary does not contain project metadata",
        )
    summary_bundle.update({
        "byteLength": len(project_bytes),
        "files": list(harnessed_project.files),
        "sha256": harness_provenance["preparedProjectSha256"],
    })
    export_summary["regressionHarness"] = harness_provenance

    run_root = Path(run_directory).resolve()
    export_root = run_root / "export"
    screenshots_root = run_root / "screenshots"
    _ensure_managed_directory(export_root, run_root)
    _ensure_managed_directory(screenshots_root, run_root)
    report_path = run_root / "report.json"
    report: dict[str, object] = {
        "kind": "uibench-arkui-visual-regression",
        "reportVersion": REPORT_VERSION,
        "caseVersion": CASE_VERSION,
        "caseId": case.case_id,
        "title": case.title,
        "status": "incomplete",
        "statusReason": "Preparation outputs are being written",
        "viewport": case.viewport.model_dump(),
        "theme": case.theme,
        "tokenTheme": case.token_theme,
        "coverage": case.coverage,
        "thresholds": case.thresholds.model_dump(by_alias=True),
        "metrics": None,
        "exportQuality": result.get("quality"),
        "diagnostics": result.get("diagnostics", []),
        "regressionHarness": harness_provenance,
        "capture": {
            "browser": "preparing",
            "arkui": "pending",
            "buildVerification": "not-run",
        },
        "artifacts": [],
    }
    # Replace any previous passing report before touching its stable artifact
    # paths. A failed re-prepare is therefore explicitly incomplete.
    _write_json(report_path, report)
    browser_destination = screenshots_root / "browser.png"
    browser_destination.write_bytes(browser_png)
    snapshot_destination = run_root / "browser-snapshot.json"
    _write_json(snapshot_destination, snapshot.model_dump(by_alias=True))
    screen_ir_path = export_root / "screen-ir.json"
    arkts_path = export_root / "page.ets"
    project_path = export_root / "project.zip"
    summary_path = export_root / "export-summary.json"
    _write_json(screen_ir_path, result["screenIr"])
    arkts_path.write_text(canonical_arkts, encoding="utf-8")
    project_path.write_bytes(project_bytes)
    _write_json(summary_path, export_summary)

    artifact_paths = (
        browser_destination,
        snapshot_destination,
        screen_ir_path,
        arkts_path,
        project_path,
        summary_path,
    )
    report.update({
        "statusReason": "ArkUI screenshot has not been supplied",
        "capture": {
            "browser": "provided",
            "arkui": "pending",
            "buildVerification": bundle.get("buildVerification", "not-run"),
        },
        "artifacts": [
            _artifact(path, run_root) for path in artifact_paths
        ],
    })
    _write_json(report_path, report)
    _prune_unreferenced_versions(
        screenshots_root / "comparisons",
        keep_id="",
        owner_root=run_root,
    )
    _prune_unreferenced_versions(
        screenshots_root / "normalizations",
        keep_id="",
        owner_root=run_root,
    )
    _prune_unreferenced_versions(
        screenshots_root / "hdc",
        keep_id="",
        owner_root=run_root,
    )
    return report


def prepare_regression_case(
    case_file: str | Path,
    run_directory: str | Path,
) -> dict[str, object]:
    """Prepare one run while excluding concurrent build/compare commands."""
    run_root = Path(run_directory).resolve()
    run_root.mkdir(parents=True, exist_ok=True)
    with _exclusive_run_lock(run_root):
        return _prepare_regression_case_locked(case_file, run_root)


def _threshold_result(
    metrics: dict[str, object],
    thresholds: dict[str, object],
) -> tuple[str, list[str]]:
    checks: list[tuple[bool, str]] = []
    maximum_ratio = thresholds.get("maxDifferentRatio")
    if maximum_ratio is not None:
        checks.append((
            float(metrics["differentRatio"]) <= float(maximum_ratio),
            f"differentRatio <= {maximum_ratio}",
        ))
    maximum_error = thresholds.get("maxMeanAbsoluteError")
    if maximum_error is not None:
        checks.append((
            float(metrics["meanAbsoluteError"]) <= float(maximum_error),
            f"meanAbsoluteError <= {maximum_error}",
        ))
    if not checks:
        return "observed", []
    failed = [description for passed, description in checks if not passed]
    return ("failed" if failed else "passed"), failed


def _markdown_report(report: dict[str, object]) -> str:
    metrics = report.get("metrics")
    lines = [
        f"# {report['title']}",
        "",
        f"- 状态：`{report['status']}`",
        f"- 样本：`{report['caseId']}`",
        f"- 视口：`{report['viewport']['width']}×{report['viewport']['height']}`",
    ]
    if report.get("visualStatus"):
        lines.append(f"- 视觉状态：`{report['visualStatus']}`")
    if isinstance(metrics, dict):
        lines.extend([
            f"- 差异像素比例：`{metrics['differentRatio']:.8f}`",
            f"- 平均通道绝对误差：`{metrics['meanAbsoluteError']:.6f}`",
            f"- RMSE：`{metrics['rootMeanSquareError']:.6f}`",
            f"- 最大通道差：`{metrics['maxChannelDelta']}`",
            f"- 差异包围盒：`{metrics['differentBoundingBox']}`",
        ])
    reasons = report.get("failedChecks")
    if isinstance(reasons, list) and reasons:
        lines.extend(["", "未通过阈值："] + [f"- {item}" for item in reasons])
    comparison_id = report.get("comparisonId")
    artifact_root = (
        f"screenshots/comparisons/{comparison_id}"
        if isinstance(comparison_id, str)
        else "screenshots"
    )
    lines.extend([
        "",
        "截图产物：",
        "",
        "- `screenshots/browser.png`",
        f"- `{artifact_root}/arkui.png`",
        f"- `{artifact_root}/diff.png`",
        "",
    ])
    return "\n".join(lines)


def _compare_regression_run_locked(
    run_directory: str | Path,
    arkui_screenshot: str | Path,
    *,
    pixel_threshold: int | None = None,
) -> dict[str, object]:
    """Attach an ArkUI screenshot, calculate metrics, and finalize the report."""
    run_root = Path(run_directory).resolve()
    report_path = run_root / "report.json"
    report = _load_report(run_root)
    _require_complete_preparation(report, run_root)
    screenshots_root = run_root / "screenshots"
    _ensure_managed_directory(screenshots_root, run_root)
    source_input = Path(arkui_screenshot).absolute()
    hdc_evidence_root = (screenshots_root / "hdc").absolute()
    if source_input.is_relative_to(hdc_evidence_root):
        raise VisualRegressionError(
            "UIBENCH_HDC_SCREENSHOT_NORMALIZATION_REQUIRED",
            "Raw HDC evidence can never be compared directly",
        )
    try:
        source = source_input.resolve()
        resolved_hdc_evidence_root = hdc_evidence_root.resolve()
    except (OSError, RuntimeError) as exc:
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_ARKUI_SCREENSHOT_MISSING",
            "ArkUI screenshot path cannot be resolved",
        ) from exc
    if source.is_relative_to(resolved_hdc_evidence_root):
        raise VisualRegressionError(
            "UIBENCH_HDC_SCREENSHOT_NORMALIZATION_REQUIRED",
            "Raw HDC evidence can never be compared directly",
        )
    if _is_within_same_filesystem_directory(source, hdc_evidence_root):
        raise VisualRegressionError(
            "UIBENCH_HDC_SCREENSHOT_NORMALIZATION_REQUIRED",
            "Raw HDC evidence can never be compared directly",
        )
    if not source.is_file():
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_ARKUI_SCREENSHOT_MISSING",
            "ArkUI screenshot does not exist",
        )
    verified_hdc_png: bytes | None = None
    capture_metadata = report.get("capture")
    if isinstance(capture_metadata, dict) and capture_metadata.get(
        "arkuiProvider"
    ) == "hdc":
        hdc_metadata = capture_metadata.get("hdc")
        normalization = (
            hdc_metadata.get("normalization")
            if isinstance(hdc_metadata, dict) else None
        )
        if (
            capture_metadata.get("arkui") != "normalized"
            or not isinstance(normalization, dict)
            or normalization.get("status") != "ready"
        ):
            raise VisualRegressionError(
                "UIBENCH_HDC_SCREENSHOT_NORMALIZATION_REQUIRED",
                "Raw HDC screenshots must be normalized into the case coordinate "
                "space before visual comparison",
            )
        hdc_capture_id = hdc_metadata.get("captureId")
        normalization_id = normalization.get("normalizationId")
        if (
            hdc_metadata.get("normalizationRequired") is not False
            or not isinstance(hdc_capture_id, str)
            or not _COMPARISON_ID_RE.fullmatch(hdc_capture_id)
            or not isinstance(normalization_id, str)
            or not _COMPARISON_ID_RE.fullmatch(normalization_id)
            or normalization.get("sourceCaptureId") != hdc_capture_id
        ):
            raise VisualRegressionError(
                "UIBENCH_HDC_NORMALIZATION_PROVENANCE_INVALID",
                "Current normalization does not belong to the current HDC capture",
            )
        output_relative = normalization.get("outputArtifact")
        manifest_relative = normalization.get("manifestArtifact")
        if not isinstance(output_relative, str) or not isinstance(
            manifest_relative, str
        ):
            raise VisualRegressionError(
                "UIBENCH_HDC_NORMALIZATION_PROVENANCE_INVALID",
                "Current HDC normalization is missing artifact provenance",
            )
        normalization_prefix = f"screenshots/normalizations/{normalization_id}"
        raw_relative = hdc_metadata.get("rawArtifact")
        layout_relative = hdc_metadata.get("layoutArtifact")
        hdc_prefix = f"screenshots/hdc/{hdc_capture_id}"
        if (
            output_relative != f"{normalization_prefix}/arkui.png"
            or manifest_relative != f"{normalization_prefix}/normalization.json"
            or raw_relative != f"{hdc_prefix}/raw.png"
            or layout_relative != f"{hdc_prefix}/layout.json"
        ):
            raise VisualRegressionError(
                "UIBENCH_HDC_NORMALIZATION_PROVENANCE_INVALID",
                "Current HDC normalization artifact paths are inconsistent",
            )
        output_descriptor = _artifact_descriptor(report, output_relative)
        manifest_descriptor = _artifact_descriptor(report, manifest_relative)
        raw_descriptor = _artifact_descriptor(report, raw_relative)
        layout_descriptor = _artifact_descriptor(report, layout_relative)
        expected_source, verified_hdc_png = _verify_artifact_descriptor(
            run_root, output_descriptor
        )
        _, manifest_bytes = _verify_artifact_descriptor(
            run_root, manifest_descriptor
        )
        _verify_artifact_descriptor(run_root, raw_descriptor)
        _verify_artifact_descriptor(run_root, layout_descriptor)
        try:
            manifest = json.loads(manifest_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise VisualRegressionError(
                "UIBENCH_HDC_NORMALIZATION_PROVENANCE_INVALID",
                "Current normalization manifest is invalid",
            ) from exc
        manifest_output = manifest.get("output") if isinstance(manifest, dict) else None
        report_spec = _normalization_spec(normalization)
        manifest_spec = _normalization_spec(manifest)
        case_viewport = report.get("viewport")
        expected_viewport = (
            {
                "width": case_viewport.get("width"),
                "height": case_viewport.get("height"),
            }
            if isinstance(case_viewport, dict)
            and type(case_viewport.get("width")) is int
            and type(case_viewport.get("height")) is int
            else None
        )
        if (
            not isinstance(manifest, dict)
            or manifest.get("kind")
            != "uibench-arkui-screenshot-normalization"
            or manifest.get("normalizationId")
            != normalization.get("normalizationId")
            or manifest.get("sourceCaptureId") != hdc_capture_id
            or manifest.get("sourceRawSha256")
            != normalization.get("sourceRawSha256")
            or manifest.get("sourceLayoutSha256")
            != normalization.get("sourceLayoutSha256")
            or normalization.get("sourceRawSha256")
            != raw_descriptor.get("sha256")
            or normalization.get("sourceLayoutSha256")
            != layout_descriptor.get("sha256")
            or report_spec is None
            or manifest_spec is None
            or report_spec != manifest_spec
            or _normalization_content_viewport(report_spec) != expected_viewport
            or not isinstance(manifest_output, dict)
            or type(manifest_output.get("byteLength")) is not int
            or manifest_output.get("byteLength") <= 0
            or manifest_output.get("byteLength")
            != output_descriptor.get("byteLength")
            or manifest_output.get("sha256")
            != output_descriptor.get("sha256")
            or manifest_output.get("path") != output_relative
        ):
            raise VisualRegressionError(
                "UIBENCH_HDC_NORMALIZATION_PROVENANCE_INVALID",
                "Current normalization manifest does not match the report",
            )
        if source != expected_source:
            raise VisualRegressionError(
                "UIBENCH_HDC_NORMALIZATION_SOURCE_REQUIRED",
                "HDC comparison only accepts the current normalized artifact",
            )
    thresholds = report.get("thresholds")
    if not isinstance(thresholds, dict):
        thresholds = {}
    browser_descriptor = _artifact_descriptor(
        report, "screenshots/browser.png"
    )
    _, verified_browser_png = _verify_artifact_descriptor(
        run_root, browser_descriptor
    )
    effective_pixel_threshold = (
        int(thresholds.get("pixelThreshold", 0))
        if pixel_threshold is None else pixel_threshold
    )
    token = uuid.uuid4().hex
    comparisons_root = screenshots_root / "comparisons"
    _ensure_managed_directory(comparisons_root, run_root)
    temporary_comparison = comparisons_root / f".{token}.tmp"
    comparison_root = comparisons_root / token
    temporary_comparison.mkdir(parents=True)
    temporary_arkui = temporary_comparison / "arkui.png"
    temporary_diff = temporary_comparison / "diff.png"
    temporary_markdown = temporary_comparison / "report.md"
    temporary_report = run_root / f".report-{token}.json.tmp"
    comparison_prefix = f"screenshots/comparisons/{token}"
    comparison_committed = False
    report_committed = False
    try:
        # Finish validation and rendering in one private directory. The whole
        # directory is renamed first and report.json is the sole commit marker,
        # so a failed comparison never mixes evidence from two versions.
        arkui_png = (
            verified_hdc_png
            if verified_hdc_png is not None
            else read_png_file(source)
        )
        visual_result = compare_png_bytes(
            verified_browser_png,
            arkui_png,
            pixel_threshold=effective_pixel_threshold,
        )
        metrics = visual_result.metrics.to_dict()
        temporary_diff.write_bytes(visual_result.diff_png)
        temporary_arkui.write_bytes(arkui_png)
        visual_status, failed_checks = _threshold_result(metrics, thresholds)
        capture = dict(report.get("capture") or {})
        capture["arkui"] = (
            "normalized"
            if capture.get("arkuiProvider") == "hdc"
            else "provided"
        )
        build_verification = capture.get("buildVerification", "not-run")
        if visual_status == "failed":
            status = "failed"
            status_reason = "Visual thresholds exceeded"
        elif build_verification == "failed":
            status = "failed"
            status_reason = "DevEco build verification failed"
        elif build_verification != "passed":
            status = "incomplete"
            status_reason = (
                "Visual metrics recorded; build verification has not passed"
            )
        else:
            status = visual_status
            status_reason = (
                "Metrics recorded without acceptance thresholds"
                if visual_status == "observed"
                else "Visual thresholds satisfied"
            )
        report.update({
            "status": status,
            "statusReason": status_reason,
            "comparisonId": token,
            "visualStatus": visual_status,
            "metrics": metrics,
            "failedChecks": failed_checks,
            "capture": capture,
        })
        existing_artifacts = [
            artifact for artifact in report.get("artifacts", [])
            if isinstance(artifact, dict)
            and artifact.get("path") not in {
                "screenshots/arkui.png", "screenshots/diff.png", "report.md"
            }
            and not str(artifact.get("path", "")).startswith(
                "screenshots/comparisons/"
            )
        ]
        report["artifacts"] = existing_artifacts + [
            _artifact(
                temporary_arkui,
                run_root,
                reported_path=f"{comparison_prefix}/arkui.png",
            ),
            _artifact(
                temporary_diff,
                run_root,
                reported_path=f"{comparison_prefix}/diff.png",
            ),
        ]
        temporary_markdown.write_text(
            _markdown_report(report), encoding="utf-8"
        )
        report["artifacts"].append(_artifact(
            temporary_markdown,
            run_root,
            reported_path=f"{comparison_prefix}/report.md",
        ))
        _write_json(temporary_report, report)

        temporary_comparison.replace(comparison_root)
        comparison_committed = True
        temporary_report.replace(report_path)
        report_committed = True
        _prune_unreferenced_versions(
            comparisons_root,
            keep_id=token,
            owner_root=run_root,
        )
        return report
    finally:
        if temporary_comparison.exists():
            shutil.rmtree(temporary_comparison)
        temporary_report.unlink(missing_ok=True)
        if comparison_committed and not report_committed:
            shutil.rmtree(comparison_root, ignore_errors=True)


def compare_regression_run(
    run_directory: str | Path,
    arkui_screenshot: str | Path,
    *,
    pixel_threshold: int | None = None,
) -> dict[str, object]:
    """Compare one screenshot while holding the run's cross-process lock."""
    run_root = Path(run_directory).resolve()
    with _exclusive_run_lock(run_root):
        return _compare_regression_run_locked(
            run_root,
            arkui_screenshot,
            pixel_threshold=pixel_threshold,
        )


def _normalize_hdc_capture_locked(
    run_root: Path,
    *,
    crop_x: int,
    crop_y: int,
    crop_width: int,
    crop_height: int,
    scale: int | None,
    content_width: int,
    content_height: int,
    resample: str,
) -> dict[str, object]:
    report_path = run_root / "report.json"
    report = _load_report(run_root)
    _require_complete_preparation(report, run_root)
    capture = report.get("capture")
    hdc = capture.get("hdc") if isinstance(capture, dict) else None
    if (
        not isinstance(capture, dict)
        or capture.get("arkui") not in {
            "captured-raw", "normalized", "provided",
        }
        or not isinstance(hdc, dict)
        or not isinstance(hdc.get("captureId"), str)
    ):
        raise VisualRegressionError(
            "UIBENCH_HDC_CAPTURE_REQUIRED",
            "Normalization requires the current run's raw HDC capture",
        )
    viewport = report.get("viewport")
    expected_viewport = (
        (viewport["width"], viewport["height"])
        if isinstance(viewport, dict)
        and type(viewport.get("width")) is int
        and type(viewport.get("height")) is int
        else (0, 0)
    )
    if (content_width, content_height) != expected_viewport:
        raise VisualRegressionError(
            "UIBENCH_HDC_NORMALIZATION_VIEWPORT_MISMATCH",
            "Normalization content viewport must equal the case viewport",
        )
    raw_relative = hdc.get("rawArtifact")
    layout_relative = hdc.get("layoutArtifact")
    capture_id = hdc.get("captureId")
    if not all(isinstance(value, str) for value in (
        raw_relative,
        layout_relative,
        capture_id,
    )):
        raise VisualRegressionError(
            "UIBENCH_HDC_CAPTURE_EVIDENCE_INVALID",
            "HDC capture is missing raw or layout provenance",
        )
    raw_descriptor = _artifact_descriptor(report, raw_relative)
    layout_descriptor = _artifact_descriptor(report, layout_relative)
    _, raw_png = _verify_artifact_descriptor(run_root, raw_descriptor)
    _verify_artifact_descriptor(run_root, layout_descriptor)
    spec = PngNormalizationSpec(
        crop=PixelCrop(crop_x, crop_y, crop_width, crop_height),
        pixels_per_content_pixel=scale,
        content_width=content_width,
        content_height=content_height,
        resample=resample,
    )
    normalized_png = normalize_png_bytes(raw_png, spec)
    normalization_spec = spec.to_dict()

    screenshots_root = _ensure_managed_directory(
        run_root / "screenshots", run_root
    )
    normalizations_root = _ensure_managed_directory(
        screenshots_root / "normalizations", run_root
    )
    normalization_id = uuid.uuid4().hex
    temporary_root = normalizations_root / f".{normalization_id}.tmp"
    final_root = normalizations_root / normalization_id
    output_path = temporary_root / "arkui.png"
    manifest_path = temporary_root / "normalization.json"
    output_sha256 = hashlib.sha256(normalized_png).hexdigest()
    prefix = f"screenshots/normalizations/{normalization_id}"
    manifest = {
        **normalization_spec,
        "kind": "uibench-arkui-screenshot-normalization",
        "normalizationId": normalization_id,
        "sourceCaptureId": capture_id,
        "sourceRawSha256": raw_descriptor["sha256"],
        "sourceLayoutSha256": layout_descriptor["sha256"],
        "output": {
            "path": f"{prefix}/arkui.png",
            "byteLength": len(normalized_png),
            "sha256": output_sha256,
        },
    }
    temporary_report = run_root / f".report-normalize-{normalization_id}.json.tmp"
    directory_committed = False
    report_committed = False
    try:
        temporary_root.mkdir()
        output_path.write_bytes(normalized_png)
        _write_json(manifest_path, manifest)
        existing_artifacts = [
            artifact for artifact in report.get("artifacts", [])
            if isinstance(artifact, dict)
            and not str(artifact.get("path", "")).startswith(
                "screenshots/comparisons/"
            )
            and not str(artifact.get("path", "")).startswith(
                "screenshots/normalizations/"
            )
        ]
        normalization = {
            **normalization_spec,
            "status": "ready",
            "normalizationId": normalization_id,
            "sourceCaptureId": capture_id,
            "sourceRawSha256": raw_descriptor["sha256"],
            "sourceLayoutSha256": layout_descriptor["sha256"],
            "outputArtifact": f"{prefix}/arkui.png",
            "manifestArtifact": f"{prefix}/normalization.json",
        }
        hdc = {**hdc, "normalizationRequired": False, "normalization": normalization}
        capture = {**capture, "arkui": "normalized", "hdc": hdc}
        report.update({
            "status": "incomplete",
            "statusReason": "HDC screenshot normalized; visual comparison is pending",
            "metrics": None,
            "capture": capture,
            "artifacts": existing_artifacts + [
                _artifact(
                    output_path,
                    run_root,
                    reported_path=f"{prefix}/arkui.png",
                ),
                _artifact(
                    manifest_path,
                    run_root,
                    reported_path=f"{prefix}/normalization.json",
                ),
            ],
        })
        for key in ("visualStatus", "failedChecks", "comparisonId"):
            report.pop(key, None)
        _write_json(temporary_report, report)
        temporary_root.replace(final_root)
        directory_committed = True
        temporary_report.replace(report_path)
        report_committed = True
        _prune_unreferenced_versions(
            normalizations_root,
            keep_id=normalization_id,
            owner_root=run_root,
        )
        _prune_unreferenced_versions(
            screenshots_root / "comparisons",
            keep_id="",
            owner_root=run_root,
        )
        return report
    finally:
        if temporary_root.exists():
            shutil.rmtree(temporary_root)
        temporary_report.unlink(missing_ok=True)
        if directory_committed and not report_committed:
            shutil.rmtree(final_root, ignore_errors=True)


def normalize_hdc_capture(
    run_directory: str | Path,
    *,
    crop_x: int,
    crop_y: int,
    crop_width: int,
    crop_height: int,
    scale: int | None,
    content_width: int,
    content_height: int,
    resample: str,
) -> dict[str, object]:
    """Normalize the current raw HDC screenshot under the run lock."""
    run_root = Path(run_directory).resolve()
    with _exclusive_run_lock(run_root):
        return _normalize_hdc_capture_locked(
            run_root,
            crop_x=crop_x,
            crop_y=crop_y,
            crop_width=crop_width,
            crop_height=crop_height,
            scale=scale,
            content_width=content_width,
            content_height=content_height,
            resample=resample,
        )


def _resolve_capture_hap(
    report: dict[str, object],
    run_root: Path,
    explicit_hap: str | Path | None,
) -> Path:
    capture = report.get("capture")
    if (
        not isinstance(capture, dict)
        or capture.get("buildVerification") != "passed"
    ):
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_BUILD_REQUIRED",
            "HDC capture requires a successful build for the current run",
        )
    signing = capture.get("hapSigning") if isinstance(capture, dict) else None
    artifacts = report.get("artifacts")
    reported_haps = [
        artifact
        for artifact in artifacts if isinstance(artifact, dict)
        and str(artifact.get("path", "")).endswith(".hap")
    ] if isinstance(artifacts, list) else []
    candidates = [
        artifact for artifact in reported_haps
        if "signed" in Path(str(artifact.get("path", ""))).name.lower()
        and "unsigned" not in str(artifact.get("path", "")).lower()
    ]
    if explicit_hap is not None:
        hap_path = Path(explicit_hap).resolve()
        if not hap_path.is_file():
            raise VisualRegressionError(
                "UIBENCH_REGRESSION_HAP_MISSING",
                f"Explicit HAP does not exist: {hap_path}",
            )
        explicit_digest = _hap_payload_digest(hap_path)
        if not any(
            _hap_payload_digest(
                _verified_report_hap(run_root, descriptor)
            ) == explicit_digest
            for descriptor in reported_haps
        ):
            raise VisualRegressionError(
                "UIBENCH_REGRESSION_HAP_PROVENANCE_MISMATCH",
                "Explicit HAP payload does not match this run's built HAP",
            )
        return hap_path
    if signing != "signed" or not candidates:
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_SIGNED_HAP_REQUIRED",
            "Capture requires a signed HAP; configure local DevEco debug signing "
            "or pass --hap",
        )
    if len(candidates) != 1:
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_HAP_AMBIGUOUS",
            "Report contains multiple signed HAP artifacts; pass --hap explicitly",
        )
    return _verified_report_hap(run_root, candidates[0])


def _verified_report_hap(
    run_root: Path,
    descriptor: dict[str, object],
) -> Path:
    relative_path = Path(str(descriptor["path"]))
    hap_path = (run_root / relative_path).resolve()
    if not hap_path.is_relative_to(run_root) or not hap_path.is_file():
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_HAP_MISSING",
            "Reported HAP is missing or outside the run directory",
        )
    digest = hashlib.sha256()
    byte_length = 0
    with hap_path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            byte_length += len(chunk)
            digest.update(chunk)
    if (
        descriptor.get("byteLength") != byte_length
        or descriptor.get("sha256") != digest.hexdigest()
    ):
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_HAP_ARTIFACT_MISMATCH",
            "Reported HAP no longer matches its artifact descriptor",
        )
    return hap_path


def _hap_payload_digest(path: Path) -> str:
    """Hash HAP payload entries while excluding optional signing metadata."""
    inspect_hap(path)
    digest = hashlib.sha256()
    total = 0
    try:
        with zipfile.ZipFile(path) as archive:
            entries = [entry for entry in archive.infolist() if not entry.is_dir()]
            names = [entry.filename for entry in entries]
            if len(names) != len(set(names)):
                raise ValueError("duplicate HAP entry")
            for entry in sorted(entries, key=lambda item: item.filename):
                name = entry.filename
                parts = Path(name).parts
                if not parts or Path(name).is_absolute() or ".." in parts:
                    raise ValueError("unsafe HAP entry")
                if name.upper().startswith("META-INF/"):
                    continue
                encoded_name = name.encode("utf-8")
                digest.update(len(encoded_name).to_bytes(4, "big"))
                digest.update(encoded_name)
                digest.update(entry.file_size.to_bytes(8, "big"))
                with archive.open(entry) as handle:
                    while chunk := handle.read(1024 * 1024):
                        total += len(chunk)
                        if total > 512 * 1024 * 1024:
                            raise ValueError("HAP payload is too large")
                        digest.update(chunk)
    except (
        OSError,
        RuntimeError,
        NotImplementedError,
        RecursionError,
        ValueError,
        zipfile.BadZipFile,
    ) as exc:
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_HAP_PROVENANCE_INVALID",
            "HAP payload could not be verified for this run",
        ) from exc
    return digest.hexdigest()


def _stage_capture_hap(source: Path, destination: Path) -> None:
    """Copy a bounded immutable HAP and verify its payload did not change."""
    source_digest = _hap_payload_digest(source)
    byte_length = 0
    try:
        with source.open("rb") as input_handle, destination.open("xb") as output_handle:
            while chunk := input_handle.read(1024 * 1024):
                byte_length += len(chunk)
                if byte_length > 256 * 1024 * 1024:
                    raise VisualRegressionError(
                        "UIBENCH_HAP_TOO_LARGE",
                        "HAP exceeds the capture size limit",
                    )
                output_handle.write(chunk)
        if _hap_payload_digest(destination) != source_digest:
            raise VisualRegressionError(
                "UIBENCH_REGRESSION_HAP_CHANGED",
                "HAP changed while it was being staged for capture",
            )
    except Exception:
        destination.unlink(missing_ok=True)
        raise


def _expected_bundle_name(run_root: Path) -> str:
    try:
        summary = json.loads(
            (run_root / "export/export-summary.json").read_text(encoding="utf-8")
        )
        bundle_name = summary["bundle"]["bundleName"]
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_EXPORT_SUMMARY_INVALID",
            "Prepared export summary does not contain a bundle name",
        ) from exc
    if not isinstance(bundle_name, str):
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_EXPORT_SUMMARY_INVALID",
            "Prepared export bundle name must be a string",
        )
    return bundle_name


def _capture_regression_run_hdc_locked(
    run_directory: str | Path,
    *,
    hdc_path: str | Path = DEFAULT_HDC,
    target: str | None = None,
    hap_path: str | Path | None = None,
    timeout_seconds: float = 210,
    settle_seconds: float = 2,
    runner=subprocess.run,
    sleeper=time.sleep,
) -> dict[str, object]:
    """Capture an unnormalized device screenshot as regression evidence."""
    run_root = Path(run_directory).resolve()
    report_path = run_root / "report.json"
    report = _load_report(run_root)
    _require_complete_preparation(report, run_root)
    hap = _resolve_capture_hap(report, run_root, hap_path)
    launch = inspect_hap(hap)
    expected_bundle = _expected_bundle_name(run_root)
    if launch.bundle_name != expected_bundle:
        raise VisualRegressionError(
            "UIBENCH_REGRESSION_HAP_BUNDLE_MISMATCH",
            "HAP bundle name does not match the prepared ArkUI project",
        )

    screenshots_root = _ensure_managed_directory(
        run_root / "screenshots",
        run_root,
    )
    comparisons_root = _ensure_managed_directory(
        screenshots_root / "comparisons",
        run_root,
    )
    hdc_root = _ensure_managed_directory(
        screenshots_root / "hdc",
        run_root,
    )
    capture_id = uuid.uuid4().hex
    temporary_capture = hdc_root / f".{capture_id}.tmp"
    capture_root = hdc_root / capture_id
    temporary_capture.mkdir()
    staged_hap = temporary_capture / "input.hap"
    try:
        _stage_capture_hap(hap, staged_hap)
    except Exception:
        shutil.rmtree(temporary_capture, ignore_errors=True)
        raise
    raw_path = temporary_capture / "raw.png"
    layout_path = temporary_capture / "layout.json"
    log_path = temporary_capture / "hdc.log"
    temporary_report = run_root / f".report-hdc-{capture_id}.json.tmp"
    prefix = f"screenshots/hdc/{capture_id}"
    directory_committed = False
    report_committed = False

    existing_artifacts = [
        artifact for artifact in report.get("artifacts", [])
        if isinstance(artifact, dict)
        and not str(artifact.get("path", "")).startswith(
            "screenshots/comparisons/"
        )
        and not str(artifact.get("path", "")).startswith("screenshots/hdc/")
        and not str(artifact.get("path", "")).startswith(
            "screenshots/normalizations/"
        )
    ]
    capture = dict(report.get("capture") or {})
    capture.update({
        "arkui": "capturing",
        "arkuiProvider": "hdc",
        "hdc": {
            "install": "pending",
            "launch": "pending",
            "appReady": "pending",
            "screenshot": "pending",
            "pull": "pending",
            "validation": "pending",
            "cleanup": "pending",
            "signatureVerification": "device-install-pending",
            "normalization": "none",
            "normalizationRequired": True,
        },
    })
    report.update({
        "status": "incomplete",
        "statusReason": "HDC screenshot capture is running",
        "metrics": None,
        "capture": capture,
        "artifacts": existing_artifacts,
    })
    for key in ("visualStatus", "failedChecks", "comparisonId"):
        report.pop(key, None)

    def commit_capture(artifact_paths: list[tuple[Path, str]]) -> None:
        nonlocal directory_committed, report_committed
        allowed_paths = {path.absolute() for path, _ in artifact_paths}
        for candidate in temporary_capture.iterdir():
            if candidate.is_symlink():
                candidate.unlink()
                continue
            if candidate.absolute() in allowed_paths:
                continue
            if candidate.is_file():
                candidate.unlink()
                continue
            raise VisualRegressionError(
                "UIBENCH_HDC_LOCAL_ARTIFACT_UNEXPECTED",
                "HDC capture produced an unexpected local artifact",
            )
        report["artifacts"] = existing_artifacts + [
            _artifact(path, run_root, reported_path=f"{prefix}/{name}")
            for path, name in artifact_paths
        ]
        _write_json(temporary_report, report)
        temporary_capture.replace(capture_root)
        directory_committed = True
        temporary_report.replace(report_path)
        report_committed = True
        _prune_unreferenced_versions(
            hdc_root,
            keep_id=capture_id,
            owner_root=run_root,
        )

    try:
        _write_json(report_path, report)
        _prune_unreferenced_versions(
            comparisons_root,
            keep_id="",
            owner_root=run_root,
        )
        _prune_unreferenced_versions(
            screenshots_root / "normalizations",
            keep_id="",
            owner_root=run_root,
        )
        try:
            result = capture_hdc_png(
                staged_hap,
                raw_path,
                hdc_path=hdc_path,
                target=target,
                timeout_seconds=timeout_seconds,
                settle_seconds=settle_seconds,
                runner=runner,
                sleeper=sleeper,
            )
        except VisualRegressionError as exc:
            staged_hap.unlink(missing_ok=True)
            raw_path.unlink(missing_ok=True)
            log = exc.log if isinstance(exc, HdcCaptureError) else (
                f"{exc.code}\n"
            )
            log_path.write_text(log, encoding="utf-8")
            stage_status = dict(capture.get("hdc") or {})
            if exc.code == "UIBENCH_HDC_INSTALL_FAILED":
                stage_status["install"] = "failed"
            elif exc.code == "UIBENCH_HDC_LAUNCH_FAILED":
                stage_status.update({"install": "passed", "launch": "failed"})
            elif exc.code == "UIBENCH_HDC_APP_NOT_READY":
                stage_status.update({
                    "install": "passed",
                    "launch": "passed",
                    "appReady": "failed",
                })
            elif exc.code == "UIBENCH_HDC_CAPTURE_FAILED":
                stage_status.update({
                    "install": "passed",
                    "launch": "passed",
                    "appReady": "passed",
                    "screenshot": "failed",
                })
            elif exc.code == "UIBENCH_HDC_PULL_FAILED":
                stage_status.update({
                    "install": "passed",
                    "launch": "passed",
                    "appReady": "passed",
                    "screenshot": "passed",
                    "pull": "failed",
                })
            elif exc.code == "UIBENCH_HDC_SCREENSHOT_INVALID":
                stage_status.update({
                    "install": "passed",
                    "launch": "passed",
                    "appReady": "passed",
                    "screenshot": "passed",
                    "pull": "passed",
                    "validation": "failed",
                    "cleanup": "passed",
                })
            elif exc.code == "UIBENCH_HDC_CLEANUP_FAILED":
                stage_status.update({
                    "install": "passed",
                    "launch": "passed",
                    "appReady": "passed",
                    "screenshot": "passed",
                    "pull": "passed",
                    "validation": "not-run",
                    "cleanup": "failed",
                })
            stage_status["errorCode"] = exc.code
            cause_code = getattr(exc, "cause_code", None)
            if isinstance(cause_code, str):
                stage_status["causeCode"] = cause_code
            stage_status["signatureVerification"] = (
                "device-install-rejected-or-unverified"
                if exc.code == "UIBENCH_HDC_INSTALL_FAILED"
                else stage_status.get(
                    "signatureVerification",
                    "device-install-pending",
                )
            )
            capture.update({
                "arkui": "failed",
                "hdc": stage_status,
            })
            report["status"] = "incomplete"
            report["statusReason"] = f"HDC capture failed: {exc.code}"
            commit_capture([(log_path, "hdc.log")])
            raise

        staged_hap.unlink()
        raw_path.write_bytes(result.png)
        layout_path.write_bytes(result.layout_json)
        log_path.write_text(result.log, encoding="utf-8")
        viewport = report.get("viewport")
        expected_size = (
            (int(viewport["width"]), int(viewport["height"]))
            if isinstance(viewport, dict) else (0, 0)
        )
        captured_size = (result.width, result.height)
        capture.update({
            "arkui": "captured-raw",
            "arkuiProvider": "hdc",
            "hdc": {
                "version": result.hdc_version,
                "targetFingerprint": result.target_fingerprint,
                "bundleName": result.launch.bundle_name,
                "moduleName": result.launch.module_name,
                "abilityName": result.launch.ability_name,
                "hapSha256": result.hap_sha256,
                "install": "passed",
                "launch": "passed",
                "appReady": "passed",
                "screenshot": "passed",
                "pull": "passed",
                "validation": "passed",
                "cleanup": "passed",
                "signatureVerification": "device-install-accepted",
                "normalization": "none",
                "normalizationRequired": True,
                "width": result.width,
                "height": result.height,
                "settleSeconds": settle_seconds,
                "captureId": capture_id,
                "rawArtifact": f"{prefix}/raw.png",
                "layoutArtifact": f"{prefix}/layout.json",
                "layoutValidation": "bundle-visible",
            },
        })
        report["capture"] = capture
        report["status"] = "incomplete"
        report["statusReason"] = (
            "Raw HDC screenshot captured; coordinate normalization and visual "
            "comparison are pending"
        )
        capture["hdc"]["matchesCasePixelDimensions"] = (
            captured_size == expected_size
        )
        commit_capture([
            (raw_path, "raw.png"),
            (layout_path, "layout.json"),
            (log_path, "hdc.log"),
        ])
        return report
    except (OSError, VisualRegressionError) as exc:
        if report_committed:
            raise
        capture["arkui"] = "failed"
        hdc_status = dict(capture.get("hdc") or {})
        hdc_status["errorCode"] = "UIBENCH_HDC_LOCAL_ARTIFACT_FAILED"
        capture["hdc"] = hdc_status
        report["capture"] = capture
        report["status"] = "incomplete"
        report["statusReason"] = "HDC capture artifact commit failed"
        try:
            _write_json(report_path, report)
        except OSError:
            pass
        raise VisualRegressionError(
            "UIBENCH_HDC_LOCAL_ARTIFACT_FAILED",
            "Could not commit HDC capture evidence inside the run directory",
        ) from exc
    finally:
        if temporary_capture.exists():
            shutil.rmtree(temporary_capture)
        temporary_report.unlink(missing_ok=True)
        if directory_committed and not report_committed:
            shutil.rmtree(capture_root, ignore_errors=True)


def capture_regression_run_hdc(
    run_directory: str | Path,
    *,
    hdc_path: str | Path = DEFAULT_HDC,
    target: str | None = None,
    hap_path: str | Path | None = None,
    timeout_seconds: float = 210,
    settle_seconds: float = 2,
    runner=subprocess.run,
    sleeper=time.sleep,
) -> dict[str, object]:
    """Capture one HDC target while holding the run's cross-process lock."""
    run_root = Path(run_directory).resolve()
    with _exclusive_run_lock(run_root):
        return _capture_regression_run_hdc_locked(
            run_root,
            hdc_path=hdc_path,
            target=target,
            hap_path=hap_path,
            timeout_seconds=timeout_seconds,
            settle_seconds=settle_seconds,
            runner=runner,
            sleeper=sleeper,
        )


__all__ = [
    "CASE_VERSION",
    "DEFAULT_DEVECO_STUDIO",
    "DEFAULT_HDC",
    "REPORT_VERSION",
    "RegressionCase",
    "RegressionThresholds",
    "RegressionViewport",
    "build_regression_run",
    "capture_regression_run_hdc",
    "compare_regression_run",
    "load_regression_case",
    "normalize_hdc_capture",
    "prepare_regression_case",
]
