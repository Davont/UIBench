"""HDC device probing, HAP inspection, launch, and screenshot capture."""
from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
import time
import uuid
import zipfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from uibench.arkui.visual_regression import (
    VisualRegressionError,
    decode_png,
    read_png_file,
)

DEFAULT_HDC = Path(
    "/Applications/DevEco-Studio.app/Contents/sdk/default/openharmony/"
    "toolchains/hdc"
)
MAX_HAP_BYTES = 256 * 1024 * 1024
MAX_HAP_UNCOMPRESSED_BYTES = 512 * 1024 * 1024
MAX_HDC_OUTPUT_CHARS = 64 * 1024
MAX_LAYOUT_BYTES = 8 * 1024 * 1024
MAX_LAYOUT_NODES = 100_000
_SAFE_HARMONY_IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9_.-]{1,256}$")
_HDC_FATAL_DIAGNOSTIC_RE = re.compile(
    r"(?im)(?:^|\n)\s*(?:\[Fail\]|\[Error\]|\[E[0-9A-F]{6}\])"
    r"|Connect server failed"
)
_HDC_ERROR_RE = re.compile(
    r"(?im)(?:^|\n)\s*(?:\[Fail\]|\[Error\]|\[E[0-9A-F]{6}\])"
    r"|Connect server failed|\bUnauthorized\b|\bOffline\b"
    r"|\bfailed\b|\bfailure\b|\bno such file\b|\bnot found\b"
)


@dataclass(frozen=True)
class HapLaunchTarget:
    bundle_name: str
    module_name: str
    ability_name: str
    debug: bool


@dataclass(frozen=True)
class HdcTarget:
    connect_key: str
    status: str


@dataclass(frozen=True)
class HdcProbeResult:
    version: str
    targets: tuple[HdcTarget, ...]


@dataclass(frozen=True)
class HdcCaptureResult:
    launch: HapLaunchTarget
    target_fingerprint: str
    hdc_version: str
    hap_sha256: str
    png: bytes
    width: int
    height: int
    layout_json: bytes
    log: str


class HdcCaptureError(VisualRegressionError):
    """A device-stage error that also carries a redacted bounded log."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        log: str = "",
        cause_code: str | None = None,
    ) -> None:
        super().__init__(code, message)
        self.log = log
        self.cause_code = cause_code


Runner = Callable[..., subprocess.CompletedProcess[str]]
Sleeper = Callable[[float], None]
Clock = Callable[[], float]


def _bounded_output(result: subprocess.CompletedProcess[str]) -> str:
    output = f"{result.stdout or ''}{result.stderr or ''}".strip()
    if len(output) > MAX_HDC_OUTPUT_CHARS:
        output = output[:MAX_HDC_OUTPUT_CHARS] + "\n...[truncated]"
    return output


def _run_hdc(
    hdc_path: Path,
    arguments: list[str],
    *,
    timeout_seconds: float,
    runner: Runner,
) -> subprocess.CompletedProcess[str]:
    if not hdc_path.is_file():
        raise VisualRegressionError(
            "UIBENCH_HDC_TOOL_MISSING",
            f"HDC executable does not exist: {hdc_path}",
        )
    try:
        return runner(
            [str(hdc_path), *arguments],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise VisualRegressionError(
            "UIBENCH_HDC_COMMAND_TIMEOUT",
            f"HDC command timed out after {timeout_seconds:g} seconds",
        ) from exc
    except OSError as exc:
        raise VisualRegressionError(
            "UIBENCH_HDC_UNAVAILABLE",
            f"Could not start HDC: {exc}",
        ) from exc


def _remaining_timeout(deadline: float, monotonic: Clock) -> float:
    remaining = deadline - monotonic()
    if not math.isfinite(remaining) or remaining <= 0:
        raise VisualRegressionError(
            "UIBENCH_HDC_COMMAND_TIMEOUT",
            "HDC capture deadline was exhausted",
        )
    return remaining


def _has_fatal_diagnostic(output: str) -> bool:
    return bool(_HDC_FATAL_DIAGNOSTIC_RE.search(output))


def _parse_targets(output: str) -> tuple[HdcTarget, ...]:
    targets: list[HdcTarget] = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line or line == "[Empty]" or line.startswith("["):
            continue
        parts = line.split()
        connect_key = parts[0]
        lower = line.lower()
        if "unauthorized" in lower:
            status = "unauthorized"
        elif "offline" in lower or "unknown" in lower:
            status = "offline"
        else:
            status = "ready"
        targets.append(HdcTarget(connect_key=connect_key, status=status))
    return tuple(targets)


def probe_hdc(
    hdc_path: str | Path = DEFAULT_HDC,
    *,
    timeout_seconds: float = 20,
    runner: Runner = subprocess.run,
    monotonic: Clock = time.monotonic,
) -> HdcProbeResult:
    """Return the local HDC version and all reported device targets."""
    if not math.isfinite(timeout_seconds) or not 0 < timeout_seconds <= 120:
        raise VisualRegressionError(
            "UIBENCH_HDC_TIMEOUT_INVALID",
            "HDC timeout must be greater than 0 and no more than 120 seconds",
        )
    deadline = monotonic() + timeout_seconds
    hdc = Path(hdc_path).resolve()
    version_result = _run_hdc(
        hdc,
        ["-v"],
        timeout_seconds=_remaining_timeout(deadline, monotonic),
        runner=runner,
    )
    version_output = _bounded_output(version_result)
    if version_result.returncode != 0 or _has_fatal_diagnostic(version_output):
        raise VisualRegressionError(
            "UIBENCH_HDC_UNAVAILABLE",
            "HDC version probe failed: " + (version_output or "unknown error"),
        )
    version = version_output.splitlines()[0].strip() if version_output else "unknown"
    targets_result = _run_hdc(
        hdc,
        ["list", "targets", "-v"],
        timeout_seconds=_remaining_timeout(deadline, monotonic),
        runner=runner,
    )
    targets_output = _bounded_output(targets_result)
    if targets_result.returncode != 0 or _has_fatal_diagnostic(targets_output):
        raise VisualRegressionError(
            "UIBENCH_HDC_SERVER_UNAVAILABLE",
            "HDC server is unavailable: " + (targets_output or "unknown error"),
        )
    return HdcProbeResult(version=version, targets=_parse_targets(targets_output))


def select_hdc_target(
    targets: tuple[HdcTarget, ...],
    requested: str | None,
) -> HdcTarget:
    """Select one ready target or return a precise environment error."""
    indexed = {target.connect_key: target for target in targets}
    if requested is not None:
        selected = indexed.get(requested)
        if selected is None or selected.status != "ready":
            raise VisualRegressionError(
                "UIBENCH_HDC_TARGET_UNAVAILABLE",
                "Requested HDC target is not connected and ready",
            )
        return selected
    ready = [target for target in targets if target.status == "ready"]
    if not ready:
        raise VisualRegressionError(
            "UIBENCH_HDC_TARGET_MISSING",
            "No connected HarmonyOS target is available",
        )
    if len(ready) > 1:
        raise VisualRegressionError(
            "UIBENCH_HDC_TARGET_AMBIGUOUS",
            "Multiple HarmonyOS targets are ready; select one with --target",
        )
    return ready[0]


def _safe_identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not _SAFE_HARMONY_IDENTIFIER_RE.fullmatch(value):
        raise VisualRegressionError(
            "UIBENCH_HAP_LAUNCH_METADATA_INVALID",
            f"HAP {label} is missing or unsafe",
        )
    return value


def inspect_hap(path: str | Path) -> HapLaunchTarget:
    """Read bounded launch metadata from a compiled HAP without executing it."""
    hap_path = Path(path)
    if not hap_path.is_file():
        raise VisualRegressionError(
            "UIBENCH_HAP_MISSING",
            f"HAP does not exist: {hap_path}",
        )
    try:
        hap_size = hap_path.stat().st_size
    except OSError as exc:
        raise VisualRegressionError(
            "UIBENCH_HAP_INVALID",
            "HAP metadata could not be read",
        ) from exc
    if hap_size > MAX_HAP_BYTES:
        raise VisualRegressionError(
            "UIBENCH_HAP_TOO_LARGE",
            "HAP exceeds the capture size limit",
        )
    try:
        archive = zipfile.ZipFile(hap_path)
    except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
        raise VisualRegressionError(
            "UIBENCH_HAP_INVALID",
            "HAP is not a readable ZIP application package",
        ) from exc
    try:
        with archive:
            entries = archive.infolist()
            if (
                len(entries) > 5000
                or any(entry.file_size < 0 for entry in entries)
                or sum(entry.file_size for entry in entries)
                > MAX_HAP_UNCOMPRESSED_BYTES
            ):
                raise VisualRegressionError(
                    "UIBENCH_HAP_TOO_LARGE",
                    "HAP contents exceed the capture limits",
                )
            module_entries = [
                entry for entry in entries if entry.filename == "module.json"
            ]
            if len(module_entries) != 1 or module_entries[0].file_size > 1024 * 1024:
                raise VisualRegressionError(
                    "UIBENCH_HAP_MODULE_METADATA_INVALID",
                    "HAP must contain one bounded root module.json",
                )
            try:
                document = json.loads(archive.read(module_entries[0]))
            except (
                EOFError,
                KeyError,
                OSError,
                RecursionError,
                RuntimeError,
                NotImplementedError,
                TypeError,
                UnicodeDecodeError,
                ValueError,
                zipfile.BadZipFile,
            ) as exc:
                raise VisualRegressionError(
                    "UIBENCH_HAP_MODULE_METADATA_INVALID",
                    "HAP module.json is not valid JSON",
                ) from exc
            if not isinstance(document, dict):
                raise VisualRegressionError(
                    "UIBENCH_HAP_MODULE_METADATA_INVALID",
                    "HAP module.json must be an object",
                )
            app = document.get("app")
            module = document.get("module")
            if not isinstance(app, dict) or not isinstance(module, dict):
                raise VisualRegressionError(
                    "UIBENCH_HAP_MODULE_METADATA_INVALID",
                    "HAP module.json is missing app or module metadata",
                )
            bundle_name = _safe_identifier(app.get("bundleName"), "bundle name")
            module_name = _safe_identifier(module.get("name"), "module name")
            ability_name = _safe_identifier(module.get("mainElement"), "main ability")
            abilities = module.get("abilities")
            matching = [
                ability
                for ability in abilities if isinstance(ability, dict)
                and ability.get("name") == ability_name
            ] if isinstance(abilities, list) else []
            if len(matching) != 1 or matching[0].get("exported") is not True:
                raise VisualRegressionError(
                    "UIBENCH_HAP_ABILITY_INVALID",
                    "HAP main ability must exist once and be exported",
                )

            pack_entries = [entry for entry in entries if entry.filename == "pack.info"]
            if len(pack_entries) > 1 or (
                pack_entries and pack_entries[0].file_size > 1024 * 1024
            ):
                raise VisualRegressionError(
                    "UIBENCH_HAP_PACK_METADATA_MISMATCH",
                    "HAP must not contain duplicate or oversized pack.info metadata",
                )
            if len(pack_entries) == 1:
                try:
                    pack_info = json.loads(archive.read(pack_entries[0]))
                    summary = pack_info.get("summary", {})
                    pack_app = summary.get("app", {})
                    pack_modules = summary.get("modules", [])
                    if pack_app.get("bundleName") not in {None, bundle_name}:
                        raise ValueError("bundle mismatch")
                    if pack_modules and not any(
                        isinstance(item, dict)
                        and item.get("mainAbility") == ability_name
                        for item in pack_modules
                    ):
                        raise ValueError("ability mismatch")
                except (
                    AttributeError,
                    EOFError,
                    KeyError,
                    OSError,
                    RecursionError,
                    RuntimeError,
                    NotImplementedError,
                    TypeError,
                    UnicodeDecodeError,
                    ValueError,
                    zipfile.BadZipFile,
                ) as exc:
                    raise VisualRegressionError(
                        "UIBENCH_HAP_PACK_METADATA_MISMATCH",
                        "HAP pack.info does not match module.json",
                    ) from exc
            return HapLaunchTarget(
                bundle_name=bundle_name,
                module_name=module_name,
                ability_name=ability_name,
                debug=app.get("debug") is True,
            )
    except VisualRegressionError:
        raise
    except (
        AttributeError,
        EOFError,
        KeyError,
        OSError,
        RecursionError,
        RuntimeError,
        NotImplementedError,
        TypeError,
        UnicodeDecodeError,
        ValueError,
        zipfile.BadZipFile,
        zipfile.LargeZipFile,
    ) as exc:
        raise VisualRegressionError(
            "UIBENCH_HAP_INVALID",
            "HAP ZIP or JSON metadata is invalid",
        ) from exc


def _failed(result: subprocess.CompletedProcess[str]) -> bool:
    output = _bounded_output(result)
    return result.returncode != 0 or bool(_HDC_ERROR_RE.search(output))


def _redact(output: str, replacements: dict[str, str]) -> str:
    redacted = output
    for value, replacement in replacements.items():
        if value:
            redacted = redacted.replace(value, replacement)
    return redacted


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_layout_file(path: Path, expected_bundle_name: str) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise VisualRegressionError(
            "UIBENCH_HDC_LAYOUT_MISSING",
            "HDC did not receive a regular layout JSON file",
        )
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise VisualRegressionError(
            "UIBENCH_HDC_LAYOUT_MISSING",
            "HDC did not receive the layout JSON",
        ) from exc
    if size <= 0:
        raise VisualRegressionError(
            "UIBENCH_HDC_LAYOUT_INVALID",
            "HDC layout JSON is empty",
        )
    if size > MAX_LAYOUT_BYTES:
        raise VisualRegressionError(
            "UIBENCH_HDC_LAYOUT_TOO_LARGE",
            "HDC layout JSON exceeds the bounded size",
        )
    try:
        with path.open("rb") as handle:
            data = handle.read(MAX_LAYOUT_BYTES + 1)
        if len(data) > MAX_LAYOUT_BYTES:
            raise VisualRegressionError(
                "UIBENCH_HDC_LAYOUT_TOO_LARGE",
                "HDC layout JSON exceeds the bounded size",
            )
        document = json.loads(data)
    except VisualRegressionError:
        raise
    except (
        OSError,
        RecursionError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ) as exc:
        raise VisualRegressionError(
            "UIBENCH_HDC_LAYOUT_INVALID",
            "HDC layout is not valid bounded JSON",
        ) from exc
    if not isinstance(document, (dict, list)) or not document:
        raise VisualRegressionError(
            "UIBENCH_HDC_LAYOUT_INVALID",
            "HDC layout JSON must contain a non-empty object or array",
        )

    stack: list[tuple[object, bool]] = [(document, False)]
    visited = 0
    found_bundle = False
    found_ui_node = False
    while stack:
        value, inside_expected_bundle = stack.pop()
        visited += 1
        if visited > MAX_LAYOUT_NODES:
            raise VisualRegressionError(
                "UIBENCH_HDC_LAYOUT_TOO_LARGE",
                "HDC layout JSON contains too many nodes",
            )
        if isinstance(value, dict):
            attributes = value.get("attributes")
            owns_expected_bundle = value.get("bundleName") == expected_bundle_name or (
                isinstance(attributes, dict)
                and attributes.get("bundleName") == expected_bundle_name
            )
            if owns_expected_bundle:
                found_bundle = True
            in_expected_subtree = inside_expected_bundle or owns_expected_bundle
            node_type = value.get("type")
            if not isinstance(node_type, str) and isinstance(attributes, dict):
                node_type = attributes.get("type")
            visible = (
                attributes.get("visible")
                if isinstance(attributes, dict) else value.get("visible")
            )
            if (
                in_expected_subtree
                and isinstance(node_type, str)
                and node_type.lower() != "root"
                and visible is not False
            ):
                found_ui_node = True
            stack.extend(
                (child, in_expected_subtree) for child in value.values()
            )
        elif isinstance(value, list):
            stack.extend((child, inside_expected_bundle) for child in value)
    if not found_bundle:
        raise VisualRegressionError(
            "UIBENCH_HDC_LAYOUT_BUNDLE_MISMATCH",
            "HDC layout does not contain the launched bundle",
        )
    if not found_ui_node:
        raise VisualRegressionError(
            "UIBENCH_HDC_LAYOUT_INVALID",
            "HDC layout does not contain a visible application UI node",
        )
    return data


def capture_hdc_png(
    hap_path: str | Path,
    destination: str | Path,
    *,
    hdc_path: str | Path = DEFAULT_HDC,
    target: str | None = None,
    timeout_seconds: float = 210,
    settle_seconds: float = 2,
    runner: Runner = subprocess.run,
    sleeper: Sleeper = time.sleep,
    monotonic: Clock = time.monotonic,
) -> HdcCaptureResult:
    """Install one HAP, launch its exported ability, and capture a PNG."""
    if not math.isfinite(timeout_seconds) or not 0 < timeout_seconds <= 600:
        raise VisualRegressionError(
            "UIBENCH_HDC_TIMEOUT_INVALID",
            "Capture timeout must be greater than 0 and no more than 600 seconds",
        )
    if not math.isfinite(settle_seconds) or not 0 <= settle_seconds <= 30:
        raise VisualRegressionError(
            "UIBENCH_HDC_SETTLE_INVALID",
            "Settle time must be between 0 and 30 seconds",
        )
    deadline = monotonic() + timeout_seconds
    hap = Path(hap_path).resolve()
    destination_path = Path(destination).resolve()
    launch = inspect_hap(hap)
    try:
        hap_sha256 = _sha256_file(hap)
    except OSError as exc:
        raise VisualRegressionError(
            "UIBENCH_HAP_INVALID",
            "HAP contents could not be read",
        ) from exc
    probe = probe_hdc(
        hdc_path,
        timeout_seconds=min(_remaining_timeout(deadline, monotonic), 30),
        runner=runner,
        monotonic=monotonic,
    )
    selected = select_hdc_target(probe.targets, target)
    target_fingerprint = hashlib.sha256(
        selected.connect_key.encode("utf-8")
    ).hexdigest()[:16]
    hdc = Path(hdc_path).resolve()
    remote_id = uuid.uuid4().hex
    remote_png = f"/data/local/tmp/uibench-regression-{remote_id}.png"
    remote_layout = f"/data/local/tmp/uibench-regression-{remote_id}.json"
    local_layout = destination_path.parent / f".{remote_id}.layout.json"
    replacements = {
        selected.connect_key: f"<target:{target_fingerprint}>",
        str(hdc): "<hdc>",
        str(hap): "<hap>",
        str(destination_path): "<local-png>",
        str(local_layout): "<local-layout>",
    }
    log_lines = [
        f"hdcVersion={probe.version}",
        f"targetFingerprint={target_fingerprint}",
    ]

    def checked(stage: str, arguments: list[str], code: str) -> None:
        try:
            result = _run_hdc(
                hdc,
                ["-t", selected.connect_key, *arguments],
                timeout_seconds=_remaining_timeout(deadline, monotonic),
                runner=runner,
            )
        except VisualRegressionError as exc:
            cause_message = _redact(str(exc), replacements)
            log_lines.append(
                f"[{stage}] causeCode={exc.code}: {cause_message}"
            )
            raise HdcCaptureError(
                code,
                f"HDC {stage} failed: {cause_message}",
                log="\n".join(log_lines) + "\n",
                cause_code=exc.code,
            ) from exc
        output = _redact(_bounded_output(result), replacements)
        log_lines.append(f"[{stage}] returnCode={result.returncode}")
        if output:
            log_lines.append(output)
        if _failed(result):
            cause_code = "UIBENCH_HDC_COMMAND_FAILED"
            log_lines.append(f"[{stage}] causeCode={cause_code}")
            raise HdcCaptureError(
                code,
                f"HDC {stage} failed: {output or 'unknown error'}",
                log="\n".join(log_lines) + "\n",
                cause_code=cause_code,
            )

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    primary_error: BaseException | None = None
    try:
        checked(
            "install",
            ["install", "-r", str(hap)],
            "UIBENCH_HDC_INSTALL_FAILED",
        )
        checked(
            "launch",
            [
                "shell", "aa", "start",
                "-b", launch.bundle_name,
                "-a", launch.ability_name,
            ],
            "UIBENCH_HDC_LAUNCH_FAILED",
        )
        try:
            remaining = _remaining_timeout(deadline, monotonic)
        except VisualRegressionError as exc:
            raise HdcCaptureError(
                "UIBENCH_HDC_APP_NOT_READY",
                f"HDC settle failed: {exc}",
                log="\n".join(log_lines) + "\n",
                cause_code=exc.code,
            ) from exc
        if settle_seconds > remaining:
            raise HdcCaptureError(
                "UIBENCH_HDC_APP_NOT_READY",
                "HDC settle delay exceeds the capture deadline",
                log="\n".join(log_lines) + "\n",
                cause_code="UIBENCH_HDC_COMMAND_TIMEOUT",
            )
        sleeper(settle_seconds)
        checked(
            "layout",
            [
                "shell", "uitest", "dumpLayout",
                "-p", remote_layout,
                "-b", launch.bundle_name,
            ],
            "UIBENCH_HDC_APP_NOT_READY",
        )
        checked(
            "layout-receive",
            ["file", "recv", remote_layout, str(local_layout)],
            "UIBENCH_HDC_APP_NOT_READY",
        )
        try:
            layout_json = _validate_layout_file(local_layout, launch.bundle_name)
        except VisualRegressionError as exc:
            log_lines.append(f"[layout-validate] causeCode={exc.code}: {exc}")
            raise HdcCaptureError(
                "UIBENCH_HDC_APP_NOT_READY",
                f"HDC layout validation failed: {exc}",
                log="\n".join(log_lines) + "\n",
                cause_code=exc.code,
            ) from exc
        checked(
            "screenshot",
            ["shell", "uitest", "screenCap", "-p", remote_png],
            "UIBENCH_HDC_CAPTURE_FAILED",
        )
        checked(
            "receive",
            ["file", "recv", remote_png, str(destination_path)],
            "UIBENCH_HDC_PULL_FAILED",
        )
    except BaseException as exc:
        primary_error = exc
        raise
    finally:
        try:
            local_layout.unlink(missing_ok=True)
        except OSError as exc:
            log_lines.append(f"[local-layout-cleanup] {type(exc).__name__}")
        cleanup_error: HdcCaptureError | None = None
        try:
            cleanup = _run_hdc(
                hdc,
                [
                    "-t", selected.connect_key,
                    "shell", "rm", "-f", remote_png, remote_layout,
                ],
                timeout_seconds=min(_remaining_timeout(deadline, monotonic), 30),
                runner=runner,
            )
            cleanup_output = _redact(_bounded_output(cleanup), replacements)
            log_lines.append(f"[cleanup] returnCode={cleanup.returncode}")
            if cleanup_output:
                log_lines.append(cleanup_output)
            if _failed(cleanup):
                cause_code = "UIBENCH_HDC_COMMAND_FAILED"
                log_lines.append(f"[cleanup] causeCode={cause_code}")
                cleanup_error = HdcCaptureError(
                    "UIBENCH_HDC_CLEANUP_FAILED",
                    f"HDC cleanup failed: {cleanup_output or 'unknown error'}",
                    log="\n".join(log_lines) + "\n",
                    cause_code=cause_code,
                )
        except VisualRegressionError as exc:
            cause_message = _redact(str(exc), replacements)
            log_lines.append(
                f"[cleanup] causeCode={exc.code}: {cause_message}"
            )
            cleanup_error = HdcCaptureError(
                "UIBENCH_HDC_CLEANUP_FAILED",
                f"HDC cleanup failed: {cause_message}",
                log="\n".join(log_lines) + "\n",
                cause_code=exc.code,
            )
        if isinstance(primary_error, HdcCaptureError):
            primary_error.log = "\n".join(log_lines) + "\n"
        if primary_error is None and cleanup_error is not None:
            raise cleanup_error

    if destination_path.is_symlink() or not destination_path.is_file():
        cause_code = "UIBENCH_HDC_SCREENSHOT_MISSING"
        log_lines.append(f"[validation] causeCode={cause_code}")
        raise HdcCaptureError(
            "UIBENCH_HDC_PULL_FAILED",
            "HDC did not create a regular local screenshot file",
            log="\n".join(log_lines) + "\n",
            cause_code=cause_code,
        )
    try:
        png = read_png_file(destination_path)
        decoded = decode_png(png)
    except VisualRegressionError as exc:
        log_lines.append(f"[validation] causeCode={exc.code}: {exc}")
        raise HdcCaptureError(
            "UIBENCH_HDC_SCREENSHOT_INVALID",
            f"Captured screenshot is invalid: {exc}",
            log="\n".join(log_lines) + "\n",
            cause_code=exc.code,
        ) from exc
    return HdcCaptureResult(
        launch=launch,
        target_fingerprint=target_fingerprint,
        hdc_version=probe.version,
        hap_sha256=hap_sha256,
        png=png,
        width=decoded.width,
        height=decoded.height,
        layout_json=layout_json,
        log="\n".join(log_lines) + "\n",
    )


__all__ = [
    "DEFAULT_HDC",
    "HapLaunchTarget",
    "HdcCaptureError",
    "HdcCaptureResult",
    "HdcProbeResult",
    "HdcTarget",
    "capture_hdc_png",
    "inspect_hap",
    "probe_hdc",
    "select_hdc_target",
]
