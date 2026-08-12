"""Offline tests for HAP inspection and the HDC capture provider."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

import uibench.arkui.hdc as hdc_module
import uibench.arkui.regression as regression_module
from uibench.arkui.hdc import (
    HdcCaptureError,
    HdcTarget,
    capture_hdc_png,
    inspect_hap,
    probe_hdc,
    select_hdc_target,
)
from uibench.arkui.regression import (
    capture_regression_run_hdc,
    compare_regression_run,
    normalize_hdc_capture,
)
from uibench.arkui.visual_regression import (
    VisualRegressionError,
    encode_rgba_png,
)


def _png(
    width: int = 2,
    height: int = 2,
    color: tuple[int, int, int, int] = (255, 255, 255, 255),
) -> bytes:
    return encode_rgba_png(
        width,
        height,
        bytes(color) * width * height,
    )


def _hap(
    path: Path,
    *,
    bundle_name: str = "com.uibench.generated.capture",
) -> Path:
    module = {
        "app": {
            "bundleName": bundle_name,
            "debug": True,
        },
        "module": {
            "name": "entry",
            "mainElement": "EntryAbility",
            "abilities": [{
                "name": "EntryAbility",
                "exported": True,
            }],
        },
    }
    pack_info = {
        "summary": {
            "app": {"bundleName": bundle_name},
            "modules": [{"mainAbility": "EntryAbility"}],
        },
    }
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("module.json", json.dumps(module))
        archive.writestr("pack.info", json.dumps(pack_info))
    return path


class FakeHdc:
    def __init__(
        self,
        screenshot: bytes,
        *,
        targets: str = "emulator-5555 Connected\n",
        fail_stage: str | None = None,
        fail_stages: set[str] | None = None,
        layout: bytes | None = None,
        version_output: str = "3.2.0c\n",
        version_returncode: int = 0,
        targets_returncode: int = 0,
        clock: "FakeClock | None" = None,
        elapsed_seconds: float = 0,
        timeout_stage: str | None = None,
    ) -> None:
        self.screenshot = screenshot
        self.targets = targets
        self.fail_stages = set(fail_stages or ())
        if fail_stage is not None:
            self.fail_stages.add(fail_stage)
        self.layout = layout if layout is not None else json.dumps({
            "windows": [{
                "attributes": {
                    "bundleName": "com.uibench.generated.capture",
                },
                "children": [{"type": "Column"}],
            }],
        }).encode()
        self.version_output = version_output
        self.version_returncode = version_returncode
        self.targets_returncode = targets_returncode
        self.clock = clock
        self.elapsed_seconds = elapsed_seconds
        self.timeout_stage = timeout_stage
        self.commands: list[list[str]] = []
        self.timeouts: list[float] = []

    def __call__(self, command, **kwargs):
        arguments = [str(item) for item in command]
        self.commands.append(arguments)
        timeout = float(kwargs["timeout"])
        self.timeouts.append(timeout)

        def complete(result: subprocess.CompletedProcess[str]):
            if self.clock is not None:
                self.clock.advance(self.elapsed_seconds)
            return result

        if arguments[-1] == "-v" and len(arguments) == 2:
            return complete(subprocess.CompletedProcess(
                arguments,
                self.version_returncode,
                self.version_output,
                "",
            ))
        if arguments[-3:] == ["list", "targets", "-v"]:
            return complete(subprocess.CompletedProcess(
                arguments,
                self.targets_returncode,
                self.targets,
                "",
            ))
        stage = None
        if "install" in arguments:
            stage = "install"
        elif "aa" in arguments and "start" in arguments:
            stage = "launch"
        elif "dumpLayout" in arguments:
            stage = "layout"
        elif "screenCap" in arguments:
            stage = "screenshot"
        elif "recv" in arguments:
            stage = (
                "layout-receive"
                if arguments[-2].endswith(".json") else "receive"
            )
        elif "rm" in arguments:
            stage = "cleanup"
        if stage == self.timeout_stage:
            if self.clock is not None:
                self.clock.advance(self.elapsed_seconds)
            raise subprocess.TimeoutExpired(arguments, timeout)
        if stage in self.fail_stages:
            return complete(subprocess.CompletedProcess(
                arguments, 0, f"[Fail] simulated {stage} error\n", ""
            ))
        if stage in {"layout-receive", "receive"}:
            destination = Path(arguments[-1])
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(
                self.layout if stage == "layout-receive" else self.screenshot
            )
        return complete(subprocess.CompletedProcess(
            arguments, 0, "successfully\n", ""
        ))


class FakeClock:
    def __init__(self) -> None:
        self.value = 0.0

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


def _artifact(path: Path, run_root: Path) -> dict[str, object]:
    content = path.read_bytes()
    return {
        "path": path.relative_to(run_root).as_posix(),
        "byteLength": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
    }


def _prepared_run(tmp_path: Path) -> Path:
    run_root = tmp_path / "run"
    paths = {
        "screenshots/browser.png": _png(),
        "browser-snapshot.json": b"{}\n",
        "export/screen-ir.json": b"{}\n",
        "export/page.ets": b"@Entry struct Capture {}\n",
        "export/project.zip": b"project",
        "export/export-summary.json": json.dumps({
            "bundle": {"bundleName": "com.uibench.generated.capture"},
        }).encode(),
    }
    artifact_paths: list[Path] = []
    for relative_path, content in paths.items():
        path = run_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        artifact_paths.append(path)
    (run_root / "build").mkdir()
    built_hap = _hap(run_root / "build/entry-default-unsigned.hap")
    artifact_paths.append(built_hap)
    report = {
        "kind": "uibench-arkui-visual-regression",
        "reportVersion": 1,
        "caseVersion": 1,
        "caseId": "capture-case",
        "title": "Capture case",
        "status": "incomplete",
        "statusReason": "ArkUI screenshot has not been supplied",
        "viewport": {"width": 2, "height": 2},
        "theme": "light",
        "tokenTheme": "harmonyos",
        "coverage": [],
        "thresholds": {"pixelThreshold": 0},
        "metrics": None,
        "capture": {
            "browser": "provided",
            "arkui": "pending",
            "buildVerification": "passed",
            "hapSigning": "unsigned",
        },
        "artifacts": [_artifact(path, run_root) for path in artifact_paths],
    }
    (run_root / "report.json").write_text(json.dumps(report), encoding="utf-8")
    return run_root


def test_hap_inspection_and_hdc_capture_command_sequence(tmp_path: Path) -> None:
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    hap = _hap(tmp_path / "capture-signed.hap")
    destination = tmp_path / "device.png"
    fake = FakeHdc(_png())

    launch = inspect_hap(hap)
    result = capture_hdc_png(
        hap,
        destination,
        hdc_path=hdc,
        runner=fake,
        sleeper=lambda _: None,
    )

    assert launch.bundle_name == "com.uibench.generated.capture"
    assert launch.module_name == "entry"
    assert launch.ability_name == "EntryAbility"
    assert result.width == 2 and result.height == 2
    assert result.target_fingerprint in result.log
    assert "emulator-5555" not in result.log
    device_commands = [
        command for command in fake.commands if "-t" in command
    ]
    assert device_commands
    assert all(
        command[command.index("-t") + 1] == "emulator-5555"
        for command in device_commands
    )
    assert any("install" in command for command in device_commands)
    assert any("dumpLayout" in command for command in device_commands)
    screenshot_command = next(
        command for command in device_commands if "screenCap" in command
    )
    assert "-d" not in screenshot_command
    receive_commands = [
        command for command in device_commands if "recv" in command
    ]
    assert len(receive_commands) == 2
    assert receive_commands[0][-2].endswith(".json")
    assert receive_commands[1][-2].endswith(".png")
    assert any("rm" in command for command in device_commands)


def test_probe_and_target_selection_errors(tmp_path: Path) -> None:
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    empty = probe_hdc(hdc, runner=FakeHdc(_png(), targets="[Empty]\n"))
    assert empty.targets == ()
    with pytest.raises(VisualRegressionError) as missing:
        select_hdc_target(empty.targets, None)
    assert missing.value.code == "UIBENCH_HDC_TARGET_MISSING"

    targets = (
        HdcTarget("one", "ready"),
        HdcTarget("two", "ready"),
    )
    with pytest.raises(VisualRegressionError) as ambiguous:
        select_hdc_target(targets, None)
    assert ambiguous.value.code == "UIBENCH_HDC_TARGET_AMBIGUOUS"
    with pytest.raises(VisualRegressionError) as unavailable:
        select_hdc_target((HdcTarget("one", "offline"),), "one")
    assert unavailable.value.code == "UIBENCH_HDC_TARGET_UNAVAILABLE"


def test_probe_rejects_success_exit_with_hdc_error_marker(tmp_path: Path) -> None:
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")

    with pytest.raises(VisualRegressionError) as version_error:
        probe_hdc(
            hdc,
            runner=FakeHdc(_png(), version_output="[Error] bad client\n"),
        )
    assert version_error.value.code == "UIBENCH_HDC_UNAVAILABLE"

    with pytest.raises(VisualRegressionError) as targets_error:
        probe_hdc(
            hdc,
            runner=FakeHdc(_png(), targets="[E000001] bad server\n"),
        )
    assert targets_error.value.code == "UIBENCH_HDC_SERVER_UNAVAILABLE"


def test_probe_preserves_offline_and_unauthorized_target_statuses(
    tmp_path: Path,
) -> None:
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    result = probe_hdc(
        hdc,
        runner=FakeHdc(
            _png(),
            targets=(
                "ready USB Connected localhost hdc\n"
                "pending USB Unauthorized localhost hdc\n"
                "gone TCP Offline localhost hdc\n"
            ),
        ),
    )

    assert [(item.connect_key, item.status) for item in result.targets] == [
        ("ready", "ready"),
        ("pending", "unauthorized"),
        ("gone", "offline"),
    ]


def test_hdc_failure_is_redacted_and_remote_files_are_cleaned(
    tmp_path: Path,
) -> None:
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    hap = _hap(tmp_path / "capture-signed.hap")
    fake = FakeHdc(_png(), fail_stage="install")

    with pytest.raises(HdcCaptureError) as failure:
        capture_hdc_png(
            hap,
            tmp_path / "device.png",
            hdc_path=hdc,
            runner=fake,
            sleeper=lambda _: None,
        )

    assert failure.value.code == "UIBENCH_HDC_INSTALL_FAILED"
    assert "emulator-5555" not in failure.value.log
    assert str(hap) not in failure.value.log
    assert any("rm" in command for command in fake.commands)


@pytest.mark.parametrize(
    ("layout", "cause_code"),
    [
        (b"", "UIBENCH_HDC_LAYOUT_INVALID"),
        (b"{}", "UIBENCH_HDC_LAYOUT_INVALID"),
        (
            b'{"attributes":{"bundleName":"com.uibench.generated.capture"}}',
            "UIBENCH_HDC_LAYOUT_INVALID",
        ),
        (
            b'{"attributes":{"bundleName":"com.example.wrong"}}',
            "UIBENCH_HDC_LAYOUT_BUNDLE_MISMATCH",
        ),
        (
            b'{"windows":['
            b'{"attributes":{"bundleName":"com.uibench.generated.capture"}},'
            b'{"type":"Column"}]}',
            "UIBENCH_HDC_LAYOUT_INVALID",
        ),
    ],
)
def test_hdc_rejects_empty_or_wrong_bundle_layout(
    tmp_path: Path,
    layout: bytes,
    cause_code: str,
) -> None:
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    hap = _hap(tmp_path / "capture-signed.hap")
    fake = FakeHdc(_png(), layout=layout)

    with pytest.raises(HdcCaptureError) as failure:
        capture_hdc_png(
            hap,
            tmp_path / "device.png",
            hdc_path=hdc,
            runner=fake,
            sleeper=lambda _: None,
        )

    assert failure.value.code == "UIBENCH_HDC_APP_NOT_READY"
    assert failure.value.cause_code == cause_code
    assert cause_code in failure.value.log
    assert not any("screenCap" in command for command in fake.commands)
    assert any("rm" in command for command in fake.commands)


def test_hdc_rejects_oversized_layout_before_json_decode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(hdc_module, "MAX_LAYOUT_BYTES", 8)
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    hap = _hap(tmp_path / "capture-signed.hap")
    fake = FakeHdc(_png(), layout=b'{"bundleName":"too-long"}')

    with pytest.raises(HdcCaptureError) as failure:
        capture_hdc_png(
            hap,
            tmp_path / "device.png",
            hdc_path=hdc,
            runner=fake,
            sleeper=lambda _: None,
        )

    assert failure.value.code == "UIBENCH_HDC_APP_NOT_READY"
    assert failure.value.cause_code == "UIBENCH_HDC_LAYOUT_TOO_LARGE"


def test_cleanup_failure_is_primary_only_when_capture_succeeded(
    tmp_path: Path,
) -> None:
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    hap = _hap(tmp_path / "capture-signed.hap")

    cleanup_only = FakeHdc(_png(), fail_stage="cleanup")
    with pytest.raises(HdcCaptureError) as cleanup_failure:
        capture_hdc_png(
            hap,
            tmp_path / "cleanup.png",
            hdc_path=hdc,
            runner=cleanup_only,
            sleeper=lambda _: None,
        )
    assert cleanup_failure.value.code == "UIBENCH_HDC_CLEANUP_FAILED"
    assert cleanup_failure.value.cause_code == "UIBENCH_HDC_COMMAND_FAILED"

    primary_and_cleanup = FakeHdc(
        _png(),
        fail_stages={"install", "cleanup"},
    )
    with pytest.raises(HdcCaptureError) as install_failure:
        capture_hdc_png(
            hap,
            tmp_path / "install.png",
            hdc_path=hdc,
            runner=primary_and_cleanup,
            sleeper=lambda _: None,
        )
    assert install_failure.value.code == "UIBENCH_HDC_INSTALL_FAILED"
    assert "[cleanup] causeCode=UIBENCH_HDC_COMMAND_FAILED" in (
        install_failure.value.log
    )


def test_invalid_screenshot_preserves_decoder_cause(tmp_path: Path) -> None:
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    hap = _hap(tmp_path / "capture-signed.hap")

    with pytest.raises(HdcCaptureError) as failure:
        capture_hdc_png(
            hap,
            tmp_path / "device.png",
            hdc_path=hdc,
            runner=FakeHdc(b"not-a-png"),
            sleeper=lambda _: None,
        )

    assert failure.value.code == "UIBENCH_HDC_SCREENSHOT_INVALID"
    assert failure.value.cause_code == "UIBENCH_VISUAL_PNG_SIGNATURE_INVALID"
    assert failure.value.cause_code in failure.value.log


def test_capture_uses_one_monotonic_deadline_and_preserves_timeout_cause(
    tmp_path: Path,
) -> None:
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    hap = _hap(tmp_path / "capture-signed.hap")
    clock = FakeClock()
    fake = FakeHdc(
        _png(),
        clock=clock,
        elapsed_seconds=1,
    )

    capture_hdc_png(
        hap,
        tmp_path / "device.png",
        hdc_path=hdc,
        timeout_seconds=20,
        settle_seconds=0,
        runner=fake,
        sleeper=lambda _: None,
        monotonic=clock,
    )

    assert len(fake.timeouts) >= 8
    assert all(
        later < earlier
        for earlier, later in zip(fake.timeouts, fake.timeouts[1:])
    )

    timeout_clock = FakeClock()
    timeout_fake = FakeHdc(
        _png(),
        clock=timeout_clock,
        elapsed_seconds=1,
        timeout_stage="install",
    )
    with pytest.raises(HdcCaptureError) as timeout_failure:
        capture_hdc_png(
            hap,
            tmp_path / "timeout.png",
            hdc_path=hdc,
            timeout_seconds=20,
            settle_seconds=0,
            runner=timeout_fake,
            sleeper=lambda _: None,
            monotonic=timeout_clock,
        )
    assert timeout_failure.value.code == "UIBENCH_HDC_INSTALL_FAILED"
    assert timeout_failure.value.cause_code == "UIBENCH_HDC_COMMAND_TIMEOUT"
    assert "causeCode=UIBENCH_HDC_COMMAND_TIMEOUT" in timeout_failure.value.log


def test_hap_zip_and_json_failures_are_visual_regression_errors(
    tmp_path: Path,
) -> None:
    invalid_zip = tmp_path / "invalid.hap"
    invalid_zip.write_bytes(b"not a zip")
    with pytest.raises(VisualRegressionError) as zip_failure:
        inspect_hap(invalid_zip)
    assert zip_failure.value.code == "UIBENCH_HAP_INVALID"

    invalid_json = tmp_path / "invalid-json.hap"
    with zipfile.ZipFile(invalid_json, "w") as archive:
        archive.writestr("module.json", "{")
    with pytest.raises(VisualRegressionError) as json_failure:
        inspect_hap(invalid_json)
    assert json_failure.value.code == "UIBENCH_HAP_MODULE_METADATA_INVALID"

    invalid_pack = tmp_path / "invalid-pack.hap"
    valid_hap = _hap(tmp_path / "valid.hap")
    with zipfile.ZipFile(valid_hap) as archive:
        module_json = archive.read("module.json")
    with zipfile.ZipFile(invalid_pack, "w") as archive:
        archive.writestr("module.json", module_json)
        archive.writestr("pack.info", "[]")
    with pytest.raises(VisualRegressionError) as pack_failure:
        inspect_hap(invalid_pack)
    assert pack_failure.value.code == "UIBENCH_HAP_PACK_METADATA_MISMATCH"


def test_capture_regression_run_keeps_matching_raw_hdc_png(tmp_path: Path) -> None:
    run_root = _prepared_run(tmp_path)
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    hap = _hap(tmp_path / "capture-signed.hap")
    fake = FakeHdc(_png())

    report = capture_regression_run_hdc(
        run_root,
        hdc_path=hdc,
        hap_path=hap,
        runner=fake,
        sleeper=lambda _: None,
    )

    assert report["status"] == "incomplete"
    assert report["metrics"] is None
    assert report["capture"]["arkui"] == "captured-raw"
    hdc_report = report["capture"]["hdc"]
    assert hdc_report["install"] == "passed"
    assert hdc_report["width"] == 2
    assert hdc_report["matchesCasePixelDimensions"] is True
    assert hdc_report["normalizationRequired"] is True
    serialized = json.dumps(report)
    assert "emulator-5555" not in serialized
    artifact_paths = {artifact["path"] for artifact in report["artifacts"]}
    assert any(path.endswith("/hdc.log") for path in artifact_paths)
    assert any(path.endswith("/raw.png") for path in artifact_paths)
    assert not any(path.endswith("/diff.png") for path in artifact_paths)
    raw_path = next(
        run_root / path for path in artifact_paths if path.endswith("/raw.png")
    )
    with pytest.raises(VisualRegressionError) as normalization_required:
        compare_regression_run(run_root, raw_path)
    assert normalization_required.value.code == (
        "UIBENCH_HDC_SCREENSHOT_NORMALIZATION_REQUIRED"
    )


def test_normalize_current_hdc_capture_then_compare(tmp_path: Path) -> None:
    run_root = _prepared_run(tmp_path)
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    hap = _hap(tmp_path / "capture-signed.hap")
    capture_regression_run_hdc(
        run_root,
        hdc_path=hdc,
        hap_path=hap,
        runner=FakeHdc(_png()),
        sleeper=lambda _: None,
    )

    normalized = normalize_hdc_capture(
        run_root,
        crop_x=0,
        crop_y=0,
        crop_width=2,
        crop_height=2,
        scale=1,
        content_width=2,
        content_height=2,
        resample="identity",
    )

    assert normalized["status"] == "incomplete"
    assert normalized["capture"]["arkui"] == "normalized"
    normalization = normalized["capture"]["hdc"]["normalization"]
    output_path = run_root / normalization["outputArtifact"]
    manifest_path = run_root / normalization["manifestArtifact"]
    assert output_path.is_file() and manifest_path.is_file()
    assert normalized["metrics"] is None

    compared = compare_regression_run(run_root, output_path)
    assert compared["status"] == "observed"
    assert compared["metrics"]["differentRatio"] == 0

    repeated = compare_regression_run(run_root, output_path, pixel_threshold=1)
    assert repeated["status"] == "observed"
    assert repeated["capture"]["arkui"] == "normalized"


def test_area_normalization_v2_manifest_and_compare(tmp_path: Path) -> None:
    run_root = _prepared_run(tmp_path)
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    hap = _hap(tmp_path / "capture-signed.hap")
    capture_regression_run_hdc(
        run_root,
        hdc_path=hdc,
        hap_path=hap,
        runner=FakeHdc(_png(3, 3)),
        sleeper=lambda _: None,
    )

    normalized = normalize_hdc_capture(
        run_root,
        crop_x=0,
        crop_y=0,
        crop_width=3,
        crop_height=3,
        scale=None,
        content_width=2,
        content_height=2,
        resample="area-v1",
    )

    normalization = normalized["capture"]["hdc"]["normalization"]
    manifest = json.loads(
        (run_root / normalization["manifestArtifact"]).read_text()
    )
    expected_spec = {
        "normalizationVersion": 2,
        "source": {"cropPx": {"x": 0, "y": 0, "width": 3, "height": 3}},
        "target": {"contentViewport": {"width": 2, "height": 2}},
        "resample": "area-v1",
    }
    assert {
        key: normalization[key] for key in expected_spec
    } == expected_spec
    assert {key: manifest[key] for key in expected_spec} == expected_spec
    assert "scale" not in normalization and "scale" not in manifest

    output = run_root / normalization["outputArtifact"]
    compared = compare_regression_run(run_root, output)
    assert compared["status"] == "observed"
    assert compared["metrics"]["differentRatio"] == 0


def test_area_normalization_v2_provenance_rejects_spec_drift(
    tmp_path: Path,
) -> None:
    run_root = _prepared_run(tmp_path)
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    hap = _hap(tmp_path / "capture-signed.hap")
    capture_regression_run_hdc(
        run_root,
        hdc_path=hdc,
        hap_path=hap,
        runner=FakeHdc(_png(3, 3)),
        sleeper=lambda _: None,
    )
    normalized = normalize_hdc_capture(
        run_root,
        crop_x=0,
        crop_y=0,
        crop_width=3,
        crop_height=3,
        scale=None,
        content_width=2,
        content_height=2,
        resample="area-v1",
    )
    normalization = normalized["capture"]["hdc"]["normalization"]
    output = run_root / normalization["outputArtifact"]
    report_path = run_root / "report.json"
    report = json.loads(report_path.read_text())
    report["capture"]["hdc"]["normalization"]["source"]["cropPx"]["x"] = 1
    report_path.write_text(json.dumps(report), encoding="utf-8")

    with pytest.raises(VisualRegressionError) as provenance:
        compare_regression_run(run_root, output)

    assert provenance.value.code == "UIBENCH_HDC_NORMALIZATION_PROVENANCE_INVALID"


def test_normalize_cli_enforces_conditional_scale_for_area_v1(
    tmp_path: Path,
) -> None:
    tool = Path(__file__).parents[1] / "tools/arkui-regression.py"
    common = [
        sys.executable,
        str(tool),
        "normalize-hdc",
        "--run",
        str(tmp_path / "missing-run"),
        "--crop",
        "0,0,3,3",
        "--content-viewport",
        "2x2",
    ]
    forbidden = subprocess.run(
        [*common, "--resample", "area-v1", "--scale", "1"],
        text=True,
        capture_output=True,
        check=False,
    )
    accepted = subprocess.run(
        [*common, "--resample", "area-v1"],
        text=True,
        capture_output=True,
        check=False,
    )
    missing_legacy_scale = subprocess.run(
        [*common, "--resample", "box-v1"],
        text=True,
        capture_output=True,
        check=False,
    )

    assert forbidden.returncode == 2
    assert json.loads(forbidden.stdout)["error"]["code"] == (
        "UIBENCH_HDC_NORMALIZATION_ARGUMENT_INVALID"
    )
    assert accepted.returncode == 2
    assert json.loads(accepted.stdout)["error"]["code"] == (
        "UIBENCH_REGRESSION_REPORT_MISSING"
    )
    assert missing_legacy_scale.returncode == 2
    assert json.loads(missing_legacy_scale.stdout)["error"]["code"] == (
        "UIBENCH_HDC_NORMALIZATION_ARGUMENT_INVALID"
    )


def test_normalize_and_compare_reuse_verified_artifact_bytes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    run_root = _prepared_run(tmp_path)
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    hap = _hap(tmp_path / "capture-signed.hap")
    captured = capture_regression_run_hdc(
        run_root,
        hdc_path=hdc,
        hap_path=hap,
        runner=FakeHdc(_png()),
        sleeper=lambda _: None,
    )
    raw_path = (run_root / captured["capture"]["hdc"]["rawArtifact"]).resolve()
    original_read_png_file = regression_module.read_png_file

    def reject_raw_reread(path: str | Path) -> bytes:
        assert Path(path).resolve() != raw_path
        return original_read_png_file(path)

    monkeypatch.setattr(regression_module, "read_png_file", reject_raw_reread)
    normalized = normalize_hdc_capture(
        run_root,
        crop_x=0,
        crop_y=0,
        crop_width=2,
        crop_height=2,
        scale=1,
        content_width=2,
        content_height=2,
        resample="identity",
    )
    output = (
        run_root
        / normalized["capture"]["hdc"]["normalization"]["outputArtifact"]
    ).resolve()

    def reject_comparison_reread(path: str | Path) -> bytes:
        raise AssertionError(f"comparison re-read verified PNG: {path}")

    monkeypatch.setattr(
        regression_module, "read_png_file", reject_comparison_reread
    )
    compared = compare_regression_run(run_root, output)

    assert compared["metrics"]["differentRatio"] == 0


def test_normalization_can_be_recomputed_from_same_raw_capture(tmp_path: Path) -> None:
    run_root = _prepared_run(tmp_path)
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    hap = _hap(tmp_path / "capture-signed.hap")
    capture_regression_run_hdc(
        run_root,
        hdc_path=hdc,
        hap_path=hap,
        runner=FakeHdc(_png()),
        sleeper=lambda _: None,
    )
    first = normalize_hdc_capture(
        run_root,
        crop_x=0,
        crop_y=0,
        crop_width=2,
        crop_height=2,
        scale=1,
        content_width=2,
        content_height=2,
        resample="identity",
    )
    first_id = first["capture"]["hdc"]["normalization"]["normalizationId"]
    second = normalize_hdc_capture(
        run_root,
        crop_x=0,
        crop_y=0,
        crop_width=2,
        crop_height=2,
        scale=1,
        content_width=2,
        content_height=2,
        resample="identity",
    )
    second_id = second["capture"]["hdc"]["normalization"]["normalizationId"]

    assert second_id != first_id
    assert not (run_root / f"screenshots/normalizations/{first_id}").exists()
    assert (run_root / f"screenshots/normalizations/{second_id}").is_dir()


def test_hdc_compare_rejects_external_copy_of_normalized_png(tmp_path: Path) -> None:
    run_root = _prepared_run(tmp_path)
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    hap = _hap(tmp_path / "capture-signed.hap")
    capture_regression_run_hdc(
        run_root,
        hdc_path=hdc,
        hap_path=hap,
        runner=FakeHdc(_png()),
        sleeper=lambda _: None,
    )
    normalized = normalize_hdc_capture(
        run_root,
        crop_x=0,
        crop_y=0,
        crop_width=2,
        crop_height=2,
        scale=1,
        content_width=2,
        content_height=2,
        resample="identity",
    )
    normalization = normalized["capture"]["hdc"]["normalization"]
    external = tmp_path / "copied-normalized.png"
    external.write_bytes((run_root / normalization["outputArtifact"]).read_bytes())

    with pytest.raises(VisualRegressionError) as provenance:
        compare_regression_run(run_root, external)

    assert provenance.value.code == "UIBENCH_HDC_NORMALIZATION_SOURCE_REQUIRED"


def test_hdc_compare_rejects_symlinked_normalized_artifact(tmp_path: Path) -> None:
    run_root = _prepared_run(tmp_path)
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    hap = _hap(tmp_path / "capture-signed.hap")
    capture_regression_run_hdc(
        run_root,
        hdc_path=hdc,
        hap_path=hap,
        runner=FakeHdc(_png()),
        sleeper=lambda _: None,
    )
    normalized = normalize_hdc_capture(
        run_root,
        crop_x=0,
        crop_y=0,
        crop_width=2,
        crop_height=2,
        scale=1,
        content_width=2,
        content_height=2,
        resample="identity",
    )
    normalization = normalized["capture"]["hdc"]["normalization"]
    output = run_root / normalization["outputArtifact"]
    external = tmp_path / "outside-normalized.png"
    output.replace(external)
    output.symlink_to(external)

    with pytest.raises(VisualRegressionError) as provenance:
        compare_regression_run(run_root, output)

    assert provenance.value.code == "UIBENCH_REGRESSION_ARTIFACT_MISSING"


def test_hdc_compare_rejects_manifest_report_provenance_mismatch(
    tmp_path: Path,
) -> None:
    run_root = _prepared_run(tmp_path)
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    hap = _hap(tmp_path / "capture-signed.hap")
    capture_regression_run_hdc(
        run_root,
        hdc_path=hdc,
        hap_path=hap,
        runner=FakeHdc(_png()),
        sleeper=lambda _: None,
    )
    normalized = normalize_hdc_capture(
        run_root,
        crop_x=0,
        crop_y=0,
        crop_width=2,
        crop_height=2,
        scale=1,
        content_width=2,
        content_height=2,
        resample="identity",
    )
    normalization = normalized["capture"]["hdc"]["normalization"]
    output = run_root / normalization["outputArtifact"]
    report_path = run_root / "report.json"
    report = json.loads(report_path.read_text())
    report["capture"]["hdc"]["normalization"]["sourceCaptureId"] = "stale"
    report_path.write_text(json.dumps(report), encoding="utf-8")

    with pytest.raises(VisualRegressionError) as provenance:
        compare_regression_run(run_root, output)

    assert provenance.value.code == "UIBENCH_HDC_NORMALIZATION_PROVENANCE_INVALID"


def test_hdc_compare_rejects_normalization_spec_drift(tmp_path: Path) -> None:
    run_root = _prepared_run(tmp_path)
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    hap = _hap(tmp_path / "capture-signed.hap")
    capture_regression_run_hdc(
        run_root,
        hdc_path=hdc,
        hap_path=hap,
        runner=FakeHdc(_png()),
        sleeper=lambda _: None,
    )
    normalized = normalize_hdc_capture(
        run_root,
        crop_x=0,
        crop_y=0,
        crop_width=2,
        crop_height=2,
        scale=1,
        content_width=2,
        content_height=2,
        resample="identity",
    )
    normalization = normalized["capture"]["hdc"]["normalization"]
    output = run_root / normalization["outputArtifact"]
    report_path = run_root / "report.json"
    report = json.loads(report_path.read_text())
    report["capture"]["hdc"]["normalization"]["cropPx"]["x"] = 1
    report_path.write_text(json.dumps(report), encoding="utf-8")

    with pytest.raises(VisualRegressionError) as provenance:
        compare_regression_run(run_root, output)

    assert provenance.value.code == "UIBENCH_HDC_NORMALIZATION_PROVENANCE_INVALID"


def test_hdc_compare_rejects_manifest_output_length_drift(tmp_path: Path) -> None:
    run_root = _prepared_run(tmp_path)
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    hap = _hap(tmp_path / "capture-signed.hap")
    capture_regression_run_hdc(
        run_root,
        hdc_path=hdc,
        hap_path=hap,
        runner=FakeHdc(_png()),
        sleeper=lambda _: None,
    )
    normalized = normalize_hdc_capture(
        run_root,
        crop_x=0,
        crop_y=0,
        crop_width=2,
        crop_height=2,
        scale=1,
        content_width=2,
        content_height=2,
        resample="identity",
    )
    normalization = normalized["capture"]["hdc"]["normalization"]
    output = run_root / normalization["outputArtifact"]
    manifest_path = run_root / normalization["manifestArtifact"]
    manifest = json.loads(manifest_path.read_text())
    manifest["output"]["byteLength"] += 1
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    report_path = run_root / "report.json"
    report = json.loads(report_path.read_text())
    descriptor = next(
        item for item in report["artifacts"]
        if item["path"] == normalization["manifestArtifact"]
    )
    manifest_bytes = manifest_path.read_bytes()
    descriptor.update({
        "byteLength": len(manifest_bytes),
        "sha256": hashlib.sha256(manifest_bytes).hexdigest(),
    })
    report_path.write_text(json.dumps(report), encoding="utf-8")

    with pytest.raises(VisualRegressionError) as provenance:
        compare_regression_run(run_root, output)

    assert provenance.value.code == "UIBENCH_HDC_NORMALIZATION_PROVENANCE_INVALID"


@pytest.mark.parametrize("failure_point", ["png", "manifest"])
def test_failed_normalization_write_leaves_no_temporary_version(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    failure_point: str,
) -> None:
    run_root = _prepared_run(tmp_path)
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    hap = _hap(tmp_path / "capture-signed.hap")
    capture_regression_run_hdc(
        run_root,
        hdc_path=hdc,
        hap_path=hap,
        runner=FakeHdc(_png()),
        sleeper=lambda _: None,
    )
    report_before = (run_root / "report.json").read_bytes()
    if failure_point == "png":
        original_write_bytes = Path.write_bytes

        def fail_png_write(path: Path, content: bytes) -> int:
            if path.name == "arkui.png" and path.parent.name.endswith(".tmp"):
                raise OSError("simulated normalization PNG write failure")
            return original_write_bytes(path, content)

        monkeypatch.setattr(Path, "write_bytes", fail_png_write)
    else:
        original_write_json = regression_module._write_json

        def fail_manifest_write(path: Path, value: object) -> None:
            if path.name == "normalization.json":
                raise OSError("simulated normalization manifest write failure")
            original_write_json(path, value)

        monkeypatch.setattr(regression_module, "_write_json", fail_manifest_write)

    with pytest.raises(OSError, match="simulated normalization"):
        normalize_hdc_capture(
            run_root,
            crop_x=0,
            crop_y=0,
            crop_width=2,
            crop_height=2,
            scale=1,
            content_width=2,
            content_height=2,
            resample="identity",
        )

    normalization_root = run_root / "screenshots/normalizations"
    assert not normalization_root.exists() or not list(normalization_root.iterdir())
    assert (run_root / "report.json").read_bytes() == report_before


def test_normalize_two_x_box_capture(tmp_path: Path) -> None:
    run_root = _prepared_run(tmp_path)
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    hap = _hap(tmp_path / "capture-signed.hap")
    capture_regression_run_hdc(
        run_root,
        hdc_path=hdc,
        hap_path=hap,
        runner=FakeHdc(_png(4, 4)),
        sleeper=lambda _: None,
    )

    normalized = normalize_hdc_capture(
        run_root,
        crop_x=0,
        crop_y=0,
        crop_width=4,
        crop_height=4,
        scale=2,
        content_width=2,
        content_height=2,
        resample="box-v1",
    )
    output = (
        run_root
        / normalized["capture"]["hdc"]["normalization"]["outputArtifact"]
    )
    compared = compare_regression_run(run_root, output)

    assert compared["metrics"]["differentRatio"] == 0


def test_normalization_rejects_tampered_raw_capture(tmp_path: Path) -> None:
    run_root = _prepared_run(tmp_path)
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    hap = _hap(tmp_path / "capture-signed.hap")
    captured = capture_regression_run_hdc(
        run_root,
        hdc_path=hdc,
        hap_path=hap,
        runner=FakeHdc(_png()),
        sleeper=lambda _: None,
    )
    raw = run_root / captured["capture"]["hdc"]["rawArtifact"]
    raw.write_bytes(_png(3, 3))

    with pytest.raises(VisualRegressionError) as mismatch:
        normalize_hdc_capture(
            run_root,
            crop_x=0,
            crop_y=0,
            crop_width=2,
            crop_height=2,
            scale=1,
            content_width=2,
            content_height=2,
            resample="identity",
        )

    assert mismatch.value.code == "UIBENCH_REGRESSION_ARTIFACT_MISMATCH"


def test_normalization_rejects_viewport_or_scale_guessing(tmp_path: Path) -> None:
    run_root = _prepared_run(tmp_path)
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    hap = _hap(tmp_path / "capture-signed.hap")
    capture_regression_run_hdc(
        run_root,
        hdc_path=hdc,
        hap_path=hap,
        runner=FakeHdc(_png()),
        sleeper=lambda _: None,
    )

    with pytest.raises(VisualRegressionError) as viewport:
        normalize_hdc_capture(
            run_root,
            crop_x=0,
            crop_y=0,
            crop_width=2,
            crop_height=2,
            scale=1,
            content_width=1,
            content_height=1,
            resample="identity",
        )
    assert viewport.value.code == "UIBENCH_HDC_NORMALIZATION_VIEWPORT_MISMATCH"

    with pytest.raises(VisualRegressionError) as scale:
        normalize_hdc_capture(
            run_root,
            crop_x=0,
            crop_y=0,
            crop_width=2,
            crop_height=2,
            scale=2,
            content_width=2,
            content_height=2,
            resample="box-v1",
        )
    assert scale.value.code == "UIBENCH_VISUAL_NORMALIZATION_SCALE_MISMATCH"


def test_capture_regression_run_keeps_raw_mismatched_png(tmp_path: Path) -> None:
    run_root = _prepared_run(tmp_path)
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    hap = _hap(tmp_path / "capture-signed.hap")
    fake = FakeHdc(_png(3, 2))

    report = capture_regression_run_hdc(
        run_root,
        hdc_path=hdc,
        hap_path=hap,
        runner=fake,
        sleeper=lambda _: None,
    )

    assert report["status"] == "incomplete"
    assert report["capture"]["arkui"] == "captured-raw"
    assert report["capture"]["hdc"]["width"] == 3
    assert report["capture"]["hdc"]["matchesCasePixelDimensions"] is False
    raw_artifact = next(
        artifact for artifact in report["artifacts"]
        if artifact["path"].endswith("/raw.png")
    )
    assert (run_root / raw_artifact["path"]).is_file()


def test_recapture_invalidates_previous_normalization(tmp_path: Path) -> None:
    run_root = _prepared_run(tmp_path)
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    hap = _hap(tmp_path / "capture-signed.hap")
    fake = FakeHdc(_png())
    capture_regression_run_hdc(
        run_root,
        hdc_path=hdc,
        hap_path=hap,
        runner=fake,
        sleeper=lambda _: None,
    )
    normalized = normalize_hdc_capture(
        run_root,
        crop_x=0,
        crop_y=0,
        crop_width=2,
        crop_height=2,
        scale=1,
        content_width=2,
        content_height=2,
        resample="identity",
    )
    old_id = normalized["capture"]["hdc"]["normalization"]["normalizationId"]

    recaptured = capture_regression_run_hdc(
        run_root,
        hdc_path=hdc,
        hap_path=hap,
        runner=FakeHdc(_png()),
        sleeper=lambda _: None,
    )

    assert recaptured["capture"]["arkui"] == "captured-raw"
    assert not any(
        str(artifact["path"]).startswith("screenshots/normalizations/")
        for artifact in recaptured["artifacts"]
    )
    assert not (run_root / f"screenshots/normalizations/{old_id}").exists()


def test_capture_regression_report_preserves_hdc_cause_code(
    tmp_path: Path,
) -> None:
    run_root = _prepared_run(tmp_path)
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    hap = _hap(tmp_path / "capture-signed.hap")

    with pytest.raises(HdcCaptureError):
        capture_regression_run_hdc(
            run_root,
            hdc_path=hdc,
            hap_path=hap,
            runner=FakeHdc(_png(), fail_stage="install"),
            sleeper=lambda _: None,
        )

    report = json.loads((run_root / "report.json").read_text())
    hdc_report = report["capture"]["hdc"]
    assert hdc_report["errorCode"] == "UIBENCH_HDC_INSTALL_FAILED"
    assert hdc_report["causeCode"] == "UIBENCH_HDC_COMMAND_FAILED"
    assert report["status"] == "incomplete"


@pytest.mark.parametrize(
    ("screenshot", "fail_stage", "validation", "cleanup"),
    [
        (_png(), "cleanup", "not-run", "failed"),
        (b"not-a-png", None, "failed", "passed"),
    ],
)
def test_capture_regression_reports_validation_and_cleanup_order(
    tmp_path: Path,
    screenshot: bytes,
    fail_stage: str | None,
    validation: str,
    cleanup: str,
) -> None:
    run_root = _prepared_run(tmp_path)
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    hap = _hap(tmp_path / "capture-signed.hap")

    with pytest.raises(HdcCaptureError):
        capture_regression_run_hdc(
            run_root,
            hdc_path=hdc,
            hap_path=hap,
            runner=FakeHdc(screenshot, fail_stage=fail_stage),
            sleeper=lambda _: None,
        )

    report = json.loads((run_root / "report.json").read_text())
    assert report["capture"]["hdc"]["validation"] == validation
    assert report["capture"]["hdc"]["cleanup"] == cleanup


def test_capture_commit_error_does_not_leave_running_report(tmp_path: Path) -> None:
    class UnexpectedDirectoryHdc(FakeHdc):
        def __call__(self, command, **kwargs):
            result = super().__call__(command, **kwargs)
            arguments = [str(item) for item in command]
            if "recv" in arguments and arguments[-2].endswith(".png"):
                (Path(arguments[-1]).parent / "unexpected").mkdir()
            return result

    run_root = _prepared_run(tmp_path)
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    hap = _hap(tmp_path / "capture-signed.hap")

    with pytest.raises(VisualRegressionError) as failed:
        capture_regression_run_hdc(
            run_root,
            hdc_path=hdc,
            hap_path=hap,
            runner=UnexpectedDirectoryHdc(_png()),
            sleeper=lambda _: None,
        )

    report = json.loads((run_root / "report.json").read_text())
    assert failed.value.code == "UIBENCH_HDC_LOCAL_ARTIFACT_FAILED"
    assert report["capture"]["arkui"] == "failed"
    assert report["capture"]["hdc"]["errorCode"] == (
        "UIBENCH_HDC_LOCAL_ARTIFACT_FAILED"
    )
    assert report["statusReason"] != "HDC screenshot capture is running"


def test_capture_regression_rejects_symlinked_hdc_artifact_root(
    tmp_path: Path,
) -> None:
    run_root = _prepared_run(tmp_path)
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")
    hap = _hap(tmp_path / "capture-signed.hap")
    outside = tmp_path / "outside"
    outside.mkdir()
    (run_root / "screenshots/hdc").symlink_to(outside, target_is_directory=True)

    with pytest.raises(VisualRegressionError) as unsafe:
        capture_regression_run_hdc(
            run_root,
            hdc_path=hdc,
            hap_path=hap,
            runner=FakeHdc(_png()),
            sleeper=lambda _: None,
        )

    assert unsafe.value.code == "UIBENCH_REGRESSION_MANAGED_PATH_INVALID"
    assert list(outside.iterdir()) == []


def test_capture_rejects_same_bundle_hap_from_another_build(tmp_path: Path) -> None:
    run_root = _prepared_run(tmp_path)
    stale_hap = _hap(tmp_path / "stale-signed.hap")
    with zipfile.ZipFile(stale_hap, "a") as archive:
        archive.writestr("ets/modules.abc", b"stale-page-bytecode")

    with pytest.raises(VisualRegressionError) as mismatch:
        capture_regression_run_hdc(run_root, hap_path=stale_hap)

    assert mismatch.value.code == "UIBENCH_REGRESSION_HAP_PROVENANCE_MISMATCH"


def test_capture_selects_unique_signed_hap_alongside_unsigned(
    tmp_path: Path,
) -> None:
    run_root = _prepared_run(tmp_path)
    signed = _hap(run_root / "build/entry-default-signed.hap")
    report_path = run_root / "report.json"
    report = json.loads(report_path.read_text())
    report["capture"]["hapSigning"] = "signed"
    report["artifacts"].append(_artifact(signed, run_root))
    report_path.write_text(json.dumps(report), encoding="utf-8")
    hdc = tmp_path / "hdc"
    hdc.write_text("", encoding="utf-8")

    captured = capture_regression_run_hdc(
        run_root,
        hdc_path=hdc,
        runner=FakeHdc(_png()),
        sleeper=lambda _: None,
    )

    assert captured["capture"]["arkui"] == "captured-raw"
    assert captured["capture"]["hdc"]["signatureVerification"] == (
        "device-install-accepted"
    )


def test_capture_without_explicit_hap_rejects_unsigned_build(tmp_path: Path) -> None:
    run_root = _prepared_run(tmp_path)
    unsigned = _hap(run_root / "project-entry-default-unsigned.hap")
    report_path = run_root / "report.json"
    report = json.loads(report_path.read_text())
    report["artifacts"].append(_artifact(unsigned, run_root))
    report_path.write_text(json.dumps(report), encoding="utf-8")

    with pytest.raises(VisualRegressionError) as required:
        capture_regression_run_hdc(run_root)

    assert required.value.code == "UIBENCH_REGRESSION_SIGNED_HAP_REQUIRED"
