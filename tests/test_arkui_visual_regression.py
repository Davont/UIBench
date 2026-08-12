"""Offline tests for ArkUI screenshot metrics and regression artifacts."""
from __future__ import annotations

import base64
import json
import subprocess
import sys
import zipfile
from fractions import Fraction
from pathlib import Path

import pytest
from pydantic import ValidationError

from uibench.arkui import regression, visual_regression
from uibench.arkui.regression import (
    RegressionCase,
    build_regression_run,
    compare_regression_run,
    load_regression_case,
    prepare_regression_case,
)
from uibench.arkui.metadata import analyze_component_metadata
from uibench.arkui.resources import MaterializedResources, build_harmony_project
from uibench.arkui.snapshot import BrowserSnapshot
from uibench.arkui.visual_regression import (
    PixelCrop,
    PngNormalizationSpec,
    VisualRegressionError,
    compare_png_bytes,
    decode_png,
    encode_rgba_png,
    normalize_png_bytes,
)


def _png(width: int, height: int, pixels: list[tuple[int, int, int, int]]) -> bytes:
    return encode_rgba_png(width, height, b"".join(bytes(pixel) for pixel in pixels))


def test_png_round_trip_and_identical_metrics() -> None:
    source = _png(2, 2, [
        (255, 0, 0, 255),
        (0, 255, 0, 255),
        (0, 0, 255, 255),
        (255, 255, 255, 255),
    ])

    decoded = decode_png(source)
    result = compare_png_bytes(source, source)

    assert (decoded.width, decoded.height) == (2, 2)
    assert decoded.rgba == b"".join(bytes(pixel) for pixel in [
        (255, 0, 0, 255),
        (0, 255, 0, 255),
        (0, 0, 255, 255),
        (255, 255, 255, 255),
    ])
    assert result.metrics.different_pixels == 0
    assert result.metrics.different_ratio == 0
    assert result.metrics.mean_absolute_error == 0
    assert result.metrics.root_mean_square_error == 0
    assert result.metrics.max_channel_delta == 0
    assert result.metrics.different_bounding_box is None
    assert decode_png(result.diff_png).width == 2


def test_png_normalization_identity_and_integer_box_average() -> None:
    source = _png(2, 2, [
        (0, 0, 0, 255),
        (2, 4, 6, 255),
        (4, 8, 12, 255),
        (6, 12, 18, 255),
    ])
    identity = normalize_png_bytes(source, PngNormalizationSpec(
        crop=PixelCrop(0, 0, 2, 2),
        pixels_per_content_pixel=1,
        content_width=2,
        content_height=2,
        resample="identity",
    ))
    boxed = normalize_png_bytes(source, PngNormalizationSpec(
        crop=PixelCrop(0, 0, 2, 2),
        pixels_per_content_pixel=2,
        content_width=1,
        content_height=1,
        resample="box-v1",
    ))

    assert decode_png(identity).rgba == decode_png(source).rgba
    assert decode_png(boxed).rgba == bytes((3, 6, 9, 255))


def test_png_area_normalization_has_exact_golden_pixels() -> None:
    horizontal_down = _png(3, 1, [
        (0, 0, 0, 255),
        (90, 90, 90, 255),
        (180, 180, 180, 255),
    ])
    horizontal_up = _png(2, 1, [
        (0, 0, 0, 255),
        (100, 100, 100, 255),
    ])
    matrix = _png(3, 3, [
        (value, value, value, 255)
        for value in (0, 30, 60, 90, 120, 150, 180, 210, 240)
    ])

    down = decode_png(normalize_png_bytes(
        horizontal_down,
        PngNormalizationSpec(PixelCrop(0, 0, 3, 1), None, 2, 1, "area-v1"),
    ))
    up = decode_png(normalize_png_bytes(
        horizontal_up,
        PngNormalizationSpec(PixelCrop(0, 0, 2, 1), None, 3, 1, "area-v1"),
    ))
    two_dimensional = decode_png(normalize_png_bytes(
        matrix,
        PngNormalizationSpec(PixelCrop(0, 0, 3, 3), None, 2, 2, "area-v1"),
    ))

    assert down.rgba[::4] == bytes((30, 150))
    assert up.rgba[::4] == bytes((0, 50, 100))
    assert two_dimensional.rgba[::4] == bytes((40, 80, 160, 200))


def test_png_area_normalization_matches_identity_and_integer_box() -> None:
    source = _png(4, 4, [
        ((index * 17) % 256, (index * 29) % 256, (index * 43) % 256, 255)
        for index in range(16)
    ])
    area_identity = normalize_png_bytes(
        source,
        PngNormalizationSpec(PixelCrop(0, 0, 4, 4), None, 4, 4, "area-v1"),
    )
    area_box = normalize_png_bytes(
        source,
        PngNormalizationSpec(PixelCrop(0, 0, 4, 4), None, 2, 2, "area-v1"),
    )
    legacy_box = normalize_png_bytes(
        source,
        PngNormalizationSpec(PixelCrop(0, 0, 4, 4), 2, 2, 2, "box-v1"),
    )

    assert decode_png(area_identity).rgba == decode_png(source).rgba
    assert area_box == legacy_box
    assert PngNormalizationSpec(
        PixelCrop(0, 0, 4, 4), None, 2, 2, "area-v1"
    ).to_dict() == {
        "normalizationVersion": 2,
        "source": {"cropPx": {"x": 0, "y": 0, "width": 4, "height": 4}},
        "target": {"contentViewport": {"width": 2, "height": 2}},
        "resample": "area-v1",
    }


def test_png_area_normalization_matches_fraction_oracle() -> None:
    def rounded_fraction(value: Fraction) -> int:
        return (
            2 * value.numerator + value.denominator
        ) // (2 * value.denominator)

    for source_width in range(1, 4):
        for source_height in range(1, 4):
            pixels = [
                ((index * 47 + 13) % 256,) * 3 + (255,)
                for index in range(source_width * source_height)
            ]
            source = _png(source_width, source_height, pixels)
            for target_width in range(1, 4):
                for target_height in range(1, 4):
                    normalized = decode_png(normalize_png_bytes(
                        source,
                        PngNormalizationSpec(
                            PixelCrop(0, 0, source_width, source_height),
                            None,
                            target_width,
                            target_height,
                            "area-v1",
                        ),
                    ))
                    expected: list[int] = []
                    for target_y in range(target_height):
                        top = Fraction(target_y * source_height, target_height)
                        bottom = Fraction(
                            (target_y + 1) * source_height, target_height
                        )
                        for target_x in range(target_width):
                            left = Fraction(target_x * source_width, target_width)
                            right = Fraction(
                                (target_x + 1) * source_width, target_width
                            )
                            weighted = Fraction(0)
                            for source_y in range(source_height):
                                overlap_y = max(
                                    Fraction(0),
                                    min(bottom, source_y + 1) - max(top, source_y),
                                )
                                for source_x in range(source_width):
                                    overlap_x = max(
                                        Fraction(0),
                                        min(right, source_x + 1) - max(left, source_x),
                                    )
                                    value = pixels[
                                        source_y * source_width + source_x
                                    ][0]
                                    weighted += value * overlap_x * overlap_y
                            area = (right - left) * (bottom - top)
                            expected.append(rounded_fraction(weighted / area))
                    assert normalized.rgba[::4] == bytes(expected)


def test_png_area_normalization_enforces_bounds_and_work_budget(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class ExplodingInteger(int):
        def __lt__(self, other: object) -> bool:
            raise AssertionError("untrusted integer subclass was evaluated")

    source = _png(2, 2, [(10, 20, 30, 255)] * 4)
    with pytest.raises(VisualRegressionError) as scaled:
        normalize_png_bytes(
            source,
            PngNormalizationSpec(PixelCrop(0, 0, 2, 2), 1, 2, 2, "area-v1"),
        )
    assert scaled.value.code == "UIBENCH_VISUAL_NORMALIZATION_RESAMPLE_INVALID"

    with pytest.raises(VisualRegressionError) as huge_integer:
        normalize_png_bytes(
            source,
            PngNormalizationSpec(
                PixelCrop(0, 0, 10**1000, 1), None, 1, 1, "area-v1"
            ),
        )
    assert huge_integer.value.code == "UIBENCH_VISUAL_NORMALIZATION_CROP_OUT_OF_BOUNDS"

    with pytest.raises(VisualRegressionError) as integer_subclass:
        normalize_png_bytes(
            source,
            PngNormalizationSpec(
                PixelCrop(ExplodingInteger(0), 0, 2, 2), None, 1, 1, "area-v1"
            ),
        )
    assert integer_subclass.value.code == "UIBENCH_VISUAL_NORMALIZATION_INVALID"

    with pytest.raises(VisualRegressionError) as oversized_target:
        normalize_png_bytes(
            source,
            PngNormalizationSpec(PixelCrop(0, 0, 2, 2), None, 3841, 1, "area-v1"),
        )
    assert oversized_target.value.code == "UIBENCH_VISUAL_NORMALIZATION_INVALID"

    transparent = _png(2, 2, [(10, 20, 30, 254)] * 4)
    with pytest.raises(VisualRegressionError) as alpha:
        normalize_png_bytes(
            transparent,
            PngNormalizationSpec(PixelCrop(0, 0, 2, 2), None, 1, 1, "area-v1"),
        )
    assert alpha.value.code == "UIBENCH_VISUAL_SCREENSHOT_TRANSPARENT"

    assert visual_regression._area_resample_contributions(
        1320, 2856, 390, 844
    ) == 6_209_280

    monkeypatch.setattr(visual_regression, "MAX_AREA_RESAMPLE_CONTRIBUTIONS", 3)
    with pytest.raises(VisualRegressionError) as expensive:
        normalize_png_bytes(
            source,
            PngNormalizationSpec(PixelCrop(0, 0, 2, 2), None, 1, 1, "area-v1"),
        )
    assert expensive.value.code == "UIBENCH_VISUAL_NORMALIZATION_TOO_EXPENSIVE"


@pytest.mark.parametrize(
    ("spec", "code"),
    [
        (
            PngNormalizationSpec(PixelCrop(-1, 0, 1, 1), 1, 1, 1, "identity"),
            "UIBENCH_VISUAL_NORMALIZATION_INVALID",
        ),
        (
            PngNormalizationSpec(PixelCrop(1, 1, 2, 2), 1, 2, 2, "identity"),
            "UIBENCH_VISUAL_NORMALIZATION_CROP_OUT_OF_BOUNDS",
        ),
        (
            PngNormalizationSpec(PixelCrop(0, 0, 2, 2), 1, 1, 1, "identity"),
            "UIBENCH_VISUAL_NORMALIZATION_SCALE_MISMATCH",
        ),
        (
            PngNormalizationSpec(PixelCrop(0, 0, 2, 2), 2, 1, 1, "identity"),
            "UIBENCH_VISUAL_NORMALIZATION_RESAMPLE_INVALID",
        ),
    ],
)
def test_png_normalization_rejects_implicit_or_invalid_geometry(
    spec: PngNormalizationSpec,
    code: str,
) -> None:
    source = _png(2, 2, [(255, 255, 255, 255)] * 4)

    with pytest.raises(VisualRegressionError) as invalid:
        normalize_png_bytes(source, spec)

    assert invalid.value.code == code


def test_single_pixel_difference_has_exact_metrics_and_bounding_box() -> None:
    browser = _png(2, 2, [(0, 0, 0, 255)] * 4)
    arkui = _png(2, 2, [
        (0, 0, 0, 255),
        (100, 0, 0, 255),
        (0, 0, 0, 255),
        (0, 0, 0, 255),
    ])

    metrics = compare_png_bytes(browser, arkui).metrics

    assert metrics.different_pixels == 1
    assert metrics.different_ratio == 0.25
    assert metrics.mean_absolute_error == 6.25
    assert metrics.root_mean_square_error == 25
    assert metrics.max_channel_delta == 100
    assert metrics.different_bounding_box == (1, 0, 1, 1)
    assert compare_png_bytes(
        browser, arkui, pixel_threshold=100
    ).metrics.different_pixels == 0


def test_visual_comparison_rejects_invalid_inputs() -> None:
    one_pixel = _png(1, 1, [(0, 0, 0, 255)])
    two_pixels = _png(2, 1, [(0, 0, 0, 255)] * 2)

    with pytest.raises(VisualRegressionError) as dimensions:
        compare_png_bytes(one_pixel, two_pixels)
    assert dimensions.value.code == "UIBENCH_VISUAL_DIMENSIONS_MISMATCH"

    corrupted = bytearray(one_pixel)
    corrupted[-5] ^= 1
    with pytest.raises(VisualRegressionError) as crc:
        decode_png(bytes(corrupted))
    assert crc.value.code == "UIBENCH_VISUAL_PNG_CRC_INVALID"

    with pytest.raises(VisualRegressionError) as threshold:
        compare_png_bytes(one_pixel, one_pixel, pixel_threshold=256)
    assert threshold.value.code == "UIBENCH_VISUAL_THRESHOLD_INVALID"


def test_visual_comparison_rejects_transparent_full_screen_pixels() -> None:
    transparent_black = _png(1, 1, [(0, 0, 0, 0)])
    transparent_red = _png(1, 1, [(255, 0, 0, 0)])

    with pytest.raises(VisualRegressionError) as transparent:
        compare_png_bytes(transparent_black, transparent_red)

    assert transparent.value.code == "UIBENCH_VISUAL_SCREENSHOT_TRANSPARENT"


def test_png_decoder_enforces_byte_chunk_and_idat_limits(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    screenshot = _png(1, 1, [(0, 0, 0, 255)])
    screenshot_path = tmp_path / "screenshot.png"
    screenshot_path.write_bytes(screenshot)

    with monkeypatch.context() as scoped:
        scoped.setattr(
            visual_regression, "MAX_SCREENSHOT_PNG_BYTES", len(screenshot) - 1
        )
        with pytest.raises(VisualRegressionError) as too_large:
            decode_png(screenshot)
        assert too_large.value.code == "UIBENCH_VISUAL_PNG_TOO_LARGE"
        with pytest.raises(VisualRegressionError) as file_too_large:
            visual_regression.read_png_file(screenshot_path)
        assert file_too_large.value.code == "UIBENCH_VISUAL_PNG_TOO_LARGE"

    with monkeypatch.context() as scoped:
        scoped.setattr(visual_regression, "MAX_PNG_CHUNKS", 2)
        with pytest.raises(VisualRegressionError) as too_many_chunks:
            decode_png(screenshot)
        assert (
            too_many_chunks.value.code
            == "UIBENCH_VISUAL_PNG_CHUNKS_EXCEEDED"
        )

    with monkeypatch.context() as scoped:
        scoped.setattr(visual_regression, "MAX_IDAT_BYTES", 0)
        with pytest.raises(VisualRegressionError) as idat_too_large:
            decode_png(screenshot)
        assert idat_too_large.value.code == "UIBENCH_VISUAL_PNG_IDAT_TOO_LARGE"


@pytest.mark.parametrize("case_id", ["typography", "stack-card", "scroll-feed"])
def test_checked_in_regression_cases_are_self_consistent(case_id: str) -> None:
    case_root = Path(__file__).parent / "fixtures/arkui_regression" / case_id
    case = load_regression_case(case_root / "case.json")
    html = (case_root / case.html).read_text(encoding="utf-8")
    metadata = analyze_component_metadata(html)
    snapshot = BrowserSnapshot.model_validate_json(
        (case_root / case.snapshot).read_text(encoding="utf-8")
    )
    screenshot = decode_png((case_root / case.browser_screenshot).read_bytes())

    assert metadata.export_readiness == "ready"
    assert len(metadata.nodes) == len(snapshot.nodes)
    assert {node.node_id for node in metadata.nodes} == {
        node.node_id for node in snapshot.nodes
    }
    assert (snapshot.viewport_width, snapshot.viewport_height) == (
        case.viewport.width, case.viewport.height,
    )
    assert (screenshot.width, screenshot.height) == (
        case.viewport.width, case.viewport.height,
    )
    if case_id == "scroll-feed":
        assert len(snapshot.assets) == 1


def _snapshot() -> dict[str, object]:
    return {
        "snapshotVersion": 1,
        "viewportWidth": 390,
        "viewportHeight": 844,
        "theme": "light",
        "tokenTheme": "harmonyos",
        "nodes": [{
            "nodeId": "page",
            "tag": "main",
            "bbox": [0, 0, 390, 844],
            "visible": True,
            "resolvedSrc": None,
            "computed": {
                "display": "flex",
                "flexDirection": "column",
                "width": "390px",
                "height": "844px",
            },
        }],
        "assets": [],
    }


def _case_directory(tmp_path: Path, *, thresholds: dict | None = None) -> Path:
    case_root = tmp_path / "case"
    case_root.mkdir()
    (case_root / "screen.html").write_text(
        '<main data-node-id="page" data-component="column"></main>',
        encoding="utf-8",
    )
    (case_root / "browser-snapshot.json").write_text(
        json.dumps(_snapshot()), encoding="utf-8",
    )
    browser_png = _png(390, 844, [(255, 255, 255, 255)] * (390 * 844))
    (case_root / "browser.png").write_bytes(browser_png)
    (case_root / "case.json").write_text(json.dumps({
        "caseVersion": 1,
        "id": "minimal-column",
        "title": "Minimal column",
        "pageName": "MinimalColumn",
        "html": "screen.html",
        "snapshot": "browser-snapshot.json",
        "browserScreenshot": "browser.png",
        "viewport": {"width": 390, "height": 844},
        "theme": "light",
        "tokenTheme": "harmonyos",
        "coverage": ["Column"],
        "thresholds": thresholds or {},
    }), encoding="utf-8")
    return case_root


def _fake_export(*args, **kwargs) -> dict[str, object]:
    del args, kwargs
    ark_ts = (
        "@Entry\n"
        "@Component\n"
        "struct MinimalColumn {\n"
        "  build() {\n"
        "    Column() {\n"
        "    }\n"
        "      .width(390)\n"
        "      .height(844)\n"
        "  }\n"
        "}\n"
    )
    project, files, bundle_name = build_harmony_project(
        "MinimalColumn",
        ark_ts,
        MaterializedResources(entries=(), bindings={}, rejected=()),
    )
    return {
        "kind": "uibench-arkui-export",
        "exportVersion": 1,
        "mode": "annotated",
        "screenIr": {"schemaVersion": 2, "page": {"name": "MinimalColumn"}},
        "arkTs": ark_ts,
        "viewport": {"width": 390, "height": 844},
        "snapshot": {"snapshotVersion": 1, "nodes": 1},
        "assets": {"entries": [], "rejected": []},
        "bundle": {
            "kind": "uibench-harmonyos-project",
            "projectVersion": 1,
            "filename": "MinimalColumn_HarmonyOS.zip",
            "byteLength": len(project),
            "contentBase64": base64.b64encode(project).decode("ascii"),
            "files": list(files),
            "bundleName": bundle_name,
            "buildVerification": "not-run",
        },
        "diagnostics": [],
        "quality": {"readiness": "ready", "errors": 0, "warnings": 0},
    }


def _attach_stale_hdc_raw(run_root: Path) -> Path:
    capture_id = "a" * 32
    raw_path = run_root / f"screenshots/hdc/{capture_id}/raw.png"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_bytes((run_root / "screenshots/browser.png").read_bytes())
    report_path = run_root / "report.json"
    report = json.loads(report_path.read_text())
    report["capture"].update({
        "arkui": "captured-raw",
        "arkuiProvider": "hdc",
        "hdc": {
            "captureId": capture_id,
            "rawArtifact": raw_path.relative_to(run_root).as_posix(),
        },
    })
    report["artifacts"].append(regression._artifact(raw_path, run_root))
    report_path.write_text(json.dumps(report), encoding="utf-8")
    return raw_path


def test_prepare_and_compare_regression_case(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    case_root = _case_directory(tmp_path)
    run_root = tmp_path / "run"
    monkeypatch.setattr(regression.exporter, "export_annotated_html", _fake_export)

    prepared = prepare_regression_case(case_root / "case.json", run_root)

    assert prepared["status"] == "incomplete"
    project_bytes = (run_root / "export/project.zip").read_bytes()
    assert project_bytes != base64.b64decode(_fake_export()["bundle"]["contentBase64"])
    with zipfile.ZipFile(run_root / "export/project.zip") as archive:
        page = archive.read(
            "entry/src/main/ets/pages/MinimalColumn.ets"
        ).decode()
        assert "RenderFit" not in page
        assert "display.getDefaultDisplaySync()" in page
        assert "onMeasureSize(" in page
        assert "onPlaceChildren(" in page
        assert "Stack({ alignContent: Alignment.TopStart })" in page
        assert ".scale({" in page
    assert (run_root / "export/page.ets").read_text() == _fake_export()["arkTs"]
    export_summary = json.loads(
        (run_root / "export/export-summary.json").read_text()
    )
    assert "contentBase64" not in export_summary["bundle"]
    assert export_summary["bundle"]["byteLength"] == len(project_bytes)
    assert export_summary["regressionHarness"] == prepared["regressionHarness"]

    report = compare_regression_run(
        run_root, case_root / "browser.png"
    )

    assert report["status"] == "incomplete"
    assert report["visualStatus"] == "observed"
    assert report["metrics"]["differentRatio"] == 0
    artifact_paths = {item["path"] for item in report["artifacts"]}
    diff_path = next(path for path in artifact_paths if path.endswith("/diff.png"))
    markdown_path = next(
        path for path in artifact_paths if path.endswith("/report.md")
    )
    assert (run_root / diff_path).is_file()
    assert (run_root / markdown_path).is_file()
    assert len({item["path"] for item in report["artifacts"]}) == len(
        report["artifacts"]
    )

    previous_comparison = report["comparisonId"]
    repeated = compare_regression_run(run_root, case_root / "browser.png")
    comparison_directories = {
        path.name for path in (run_root / "screenshots/comparisons").iterdir()
    }
    assert comparison_directories == {repeated["comparisonId"]}
    assert repeated["comparisonId"] != previous_comparison


def test_reprepare_removes_stale_hdc_raw_evidence(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    case_root = _case_directory(tmp_path)
    run_root = tmp_path / "run"
    monkeypatch.setattr(regression.exporter, "export_annotated_html", _fake_export)
    prepare_regression_case(case_root / "case.json", run_root)
    raw_path = _attach_stale_hdc_raw(run_root)

    report = prepare_regression_case(case_root / "case.json", run_root)

    assert not raw_path.exists()
    assert not any(
        str(item["path"]).startswith("screenshots/hdc/")
        for item in report["artifacts"]
    )
    with pytest.raises(VisualRegressionError) as blocked:
        compare_regression_run(run_root, raw_path)
    assert blocked.value.code == "UIBENCH_HDC_SCREENSHOT_NORMALIZATION_REQUIRED"


def test_compare_rejects_raw_hdc_path_aliases(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    case_root = _case_directory(tmp_path)
    run_root = tmp_path / "run"
    monkeypatch.setattr(regression.exporter, "export_annotated_html", _fake_export)
    prepare_regression_case(case_root / "case.json", run_root)
    raw_path = _attach_stale_hdc_raw(run_root)
    report_path = run_root / "report.json"
    report = json.loads(report_path.read_text())
    report["capture"] = {
        "browser": "provided",
        "arkui": "pending",
        "buildVerification": "not-run",
    }
    report["artifacts"] = [
        item for item in report["artifacts"]
        if not str(item["path"]).startswith("screenshots/hdc/")
    ]
    report_path.write_text(json.dumps(report), encoding="utf-8")
    lexical_alias_root = run_root / "screenshots/alias"
    lexical_alias_root.mkdir()
    lexical_alias = lexical_alias_root / ".." / "hdc" / raw_path.parent.name / "raw.png"
    symlink_alias = tmp_path / "raw-alias.png"
    symlink_alias.symlink_to(raw_path)

    for alias in (lexical_alias, symlink_alias):
        with pytest.raises(VisualRegressionError) as blocked:
            compare_regression_run(run_root, alias)
        assert blocked.value.code == (
            "UIBENCH_HDC_SCREENSHOT_NORMALIZATION_REQUIRED"
        )


def test_compare_rejects_case_insensitive_raw_hdc_alias(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    case_root = _case_directory(tmp_path)
    run_root = tmp_path / "run"
    monkeypatch.setattr(regression.exporter, "export_annotated_html", _fake_export)
    prepare_regression_case(case_root / "case.json", run_root)
    raw_path = _attach_stale_hdc_raw(run_root)
    report_path = run_root / "report.json"
    report = json.loads(report_path.read_text())
    report["capture"] = {
        "browser": "provided",
        "arkui": "pending",
        "buildVerification": "not-run",
    }
    report["artifacts"] = [
        item for item in report["artifacts"]
        if not str(item["path"]).startswith("screenshots/hdc/")
    ]
    report_path.write_text(json.dumps(report), encoding="utf-8")
    raw_text = str(raw_path)
    alias_text = raw_text.replace("/private/", "/PRIVATE/", 1)
    case_alias = Path(alias_text)
    if alias_text == raw_text or not case_alias.is_file():
        pytest.skip("requires a case-insensitive /private filesystem alias")

    with pytest.raises(VisualRegressionError) as blocked:
        compare_regression_run(run_root, case_alias)

    assert blocked.value.code == "UIBENCH_HDC_SCREENSHOT_NORMALIZATION_REQUIRED"


def test_failed_compare_preserves_previous_report_and_screenshots(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    case_root = _case_directory(tmp_path)
    run_root = tmp_path / "run"
    monkeypatch.setattr(regression.exporter, "export_annotated_html", _fake_export)
    prepare_regression_case(case_root / "case.json", run_root)
    initial_report = compare_regression_run(run_root, case_root / "browser.png")
    comparison_paths = [
        run_root / artifact["path"]
        for artifact in initial_report["artifacts"]
        if str(artifact["path"]).startswith("screenshots/comparisons/")
    ]
    completed = {
        path: path.read_bytes()
        for path in [run_root / "report.json", *comparison_paths]
    }
    corrupted = bytearray((case_root / "browser.png").read_bytes())
    corrupted[-5] ^= 1
    corrupted_path = tmp_path / "corrupted.png"
    corrupted_path.write_bytes(corrupted)

    with pytest.raises(VisualRegressionError):
        compare_regression_run(run_root, corrupted_path)

    assert all(path.read_bytes() == content for path, content in completed.items())
    assert not list(run_root.glob("**/*.tmp"))


def test_failed_reprepare_downgrades_report_before_replacing_artifacts(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    case_root = _case_directory(tmp_path)
    run_root = tmp_path / "run"
    monkeypatch.setattr(regression.exporter, "export_annotated_html", _fake_export)
    prepare_regression_case(case_root / "case.json", run_root)
    original_write_bytes = Path.write_bytes

    def fail_project_write(path: Path, content: bytes) -> int:
        if path == run_root / "export/project.zip":
            raise OSError("simulated project write failure")
        return original_write_bytes(path, content)

    monkeypatch.setattr(Path, "write_bytes", fail_project_write)

    with pytest.raises(OSError, match="simulated project write failure"):
        prepare_regression_case(case_root / "case.json", run_root)

    report = json.loads((run_root / "report.json").read_text())
    assert report["status"] == "incomplete"
    assert report["capture"]["browser"] == "preparing"
    assert report["artifacts"] == []
    with pytest.raises(VisualRegressionError) as compare_blocked:
        compare_regression_run(run_root, case_root / "browser.png")
    with pytest.raises(VisualRegressionError) as build_blocked:
        build_regression_run(run_root)
    assert (
        compare_blocked.value.code
        == "UIBENCH_REGRESSION_PREPARATION_INCOMPLETE"
    )
    assert (
        build_blocked.value.code
        == "UIBENCH_REGRESSION_PREPARATION_INCOMPLETE"
    )


def test_report_switch_failure_keeps_previous_comparison_consistent(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    case_root = _case_directory(tmp_path)
    run_root = tmp_path / "run"
    monkeypatch.setattr(regression.exporter, "export_annotated_html", _fake_export)
    prepare_regression_case(case_root / "case.json", run_root)
    initial_report = compare_regression_run(run_root, case_root / "browser.png")
    initial_json = (run_root / "report.json").read_bytes()
    initial_artifacts = {
        artifact["path"]: (run_root / artifact["path"]).read_bytes()
        for artifact in initial_report["artifacts"]
        if str(artifact["path"]).startswith("screenshots/comparisons/")
    }
    initial_directories = set((run_root / "screenshots/comparisons").iterdir())
    original_replace = Path.replace

    def fail_report_replace(path: Path, target: Path) -> Path:
        if Path(target) == run_root / "report.json":
            raise OSError("simulated report switch failure")
        return original_replace(path, target)

    monkeypatch.setattr(Path, "replace", fail_report_replace)

    with pytest.raises(OSError, match="simulated report switch failure"):
        compare_regression_run(run_root, case_root / "browser.png")

    assert (run_root / "report.json").read_bytes() == initial_json
    assert all(
        (run_root / path).read_bytes() == content
        for path, content in initial_artifacts.items()
    )
    assert set((run_root / "screenshots/comparisons").iterdir()) == (
        initial_directories
    )


def test_comparison_rejects_symlinked_managed_root(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    case_root = _case_directory(tmp_path)
    run_root = tmp_path / "run"
    monkeypatch.setattr(regression.exporter, "export_annotated_html", _fake_export)
    prepare_regression_case(case_root / "case.json", run_root)
    comparisons_root = run_root / "screenshots/comparisons"
    comparisons_root.rmdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    comparisons_root.symlink_to(outside, target_is_directory=True)

    with pytest.raises(VisualRegressionError) as invalid:
        compare_regression_run(run_root, case_root / "browser.png")

    assert invalid.value.code == "UIBENCH_REGRESSION_MANAGED_PATH_INVALID"
    assert list(outside.iterdir()) == []


def test_concurrent_run_mutation_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    case_root = _case_directory(tmp_path)
    run_root = tmp_path / "run"
    monkeypatch.setattr(regression.exporter, "export_annotated_html", _fake_export)
    prepare_regression_case(case_root / "case.json", run_root)
    script = """
from pathlib import Path
import sys
from uibench.arkui.regression import _exclusive_run_lock
with _exclusive_run_lock(Path(sys.argv[1])):
    print("locked", flush=True)
    sys.stdin.readline()
"""
    holder = subprocess.Popen(
        [sys.executable, "-c", script, str(run_root)],
        cwd=Path(__file__).resolve().parents[1],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        assert holder.stdout is not None
        assert holder.stdout.readline().strip() == "locked"
        with pytest.raises(VisualRegressionError) as busy:
            compare_regression_run(run_root, case_root / "browser.png")
        assert busy.value.code == "UIBENCH_REGRESSION_RUN_BUSY"
    finally:
        stdout, stderr = holder.communicate("\n", timeout=10)
    assert holder.returncode == 0, stdout + stderr


def test_regression_threshold_failure_and_path_validation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    case_root = _case_directory(tmp_path, thresholds={
        "maxDifferentRatio": 0,
        "maxMeanAbsoluteError": 0,
    })
    run_root = tmp_path / "run"
    monkeypatch.setattr(regression.exporter, "export_annotated_html", _fake_export)
    prepare_regression_case(case_root / "case.json", run_root)
    arkui = _png(390, 844, [(254, 255, 255, 255)] * (390 * 844))
    arkui_path = tmp_path / "arkui.png"
    arkui_path.write_bytes(arkui)

    report = compare_regression_run(run_root, arkui_path)

    assert report["status"] == "failed"
    assert report["metrics"]["differentRatio"] == 1
    assert len(report["failedChecks"]) == 2

    with pytest.raises(ValidationError, match="inside the case directory"):
        RegressionCase.model_validate({
            "caseVersion": 1,
            "id": "unsafe-case",
            "title": "Unsafe",
            "pageName": "Unsafe",
            "html": "../screen.html",
            "snapshot": "snapshot.json",
            "browserScreenshot": "browser.png",
            "viewport": {"width": 390, "height": 844},
            "theme": "light",
            "tokenTheme": "harmonyos",
        })


def test_build_regression_run_records_log_and_unsigned_hap(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    case_root = _case_directory(tmp_path)
    run_root = tmp_path / "run"
    monkeypatch.setattr(regression.exporter, "export_annotated_html", _fake_export)
    prepare_regression_case(case_root / "case.json", run_root)
    stale_raw = _attach_stale_hdc_raw(run_root)
    studio = tmp_path / "DevEco-Studio.app"
    for path in (
        studio / "Contents/tools/node/bin/node",
        studio / "Contents/tools/hvigor/bin/hvigorw.js",
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    (studio / "Contents/sdk").mkdir(parents=True)
    (studio / "Contents/jbr/Contents/Home").mkdir(parents=True)

    def fake_run(command, *, cwd, **kwargs):
        del command, kwargs
        hap = Path(cwd) / "entry/build/default/outputs/default/entry-default-unsigned.hap"
        hap.parent.mkdir(parents=True)
        hap.write_bytes(b"unsigned-hap")
        return subprocess.CompletedProcess(
            args=[], returncode=0, stdout="\x1b[32mBUILD SUCCESSFUL\x1b[0m\n", stderr=""
        )

    monkeypatch.setattr(regression.subprocess, "run", fake_run)

    report = build_regression_run(run_root, deveco_studio=studio)

    assert report["status"] == "incomplete"
    assert report["statusReason"] == "ArkUI screenshot has not been supplied"
    assert report["capture"]["buildVerification"] == "passed"
    assert report["capture"]["buildExitCode"] == 0
    assert report["capture"]["hapSigning"] == "unsigned"
    assert (run_root / "build/hvigor.log").read_text() == "BUILD SUCCESSFUL\n"
    assert not stale_raw.exists()
    paths = {artifact["path"] for artifact in report["artifacts"]}
    assert "build/hvigor.log" in paths
    assert any(path.endswith("entry-default-unsigned.hap") for path in paths)
    assert not any(path.startswith("screenshots/hdc/") for path in paths)
    with pytest.raises(VisualRegressionError) as stale_raw_blocked:
        compare_regression_run(run_root, stale_raw)
    assert stale_raw_blocked.value.code == (
        "UIBENCH_HDC_SCREENSHOT_NORMALIZATION_REQUIRED"
    )

    def fake_mixed_run(command, *, cwd, **kwargs):
        del command, kwargs
        output = Path(cwd) / "entry/build/default/outputs/default"
        output.mkdir(parents=True)
        (output / "entry-default-unsigned.hap").write_bytes(b"unsigned-hap")
        (output / "entry-default-signed.hap").write_bytes(b"signed-hap")
        return subprocess.CompletedProcess(
            args=[], returncode=0, stdout="BUILD SUCCESSFUL\n", stderr=""
        )

    monkeypatch.setattr(regression.subprocess, "run", fake_mixed_run)
    mixed_report = build_regression_run(run_root, deveco_studio=studio)
    mixed_paths = {artifact["path"] for artifact in mixed_report["artifacts"]}

    assert mixed_report["capture"]["hapSigning"] == "signed"
    assert any(path.endswith("entry-default-signed.hap") for path in mixed_paths)
    assert any(path.endswith("entry-default-unsigned.hap") for path in mixed_paths)

    def fail_to_start(*args, **kwargs):
        del args, kwargs
        raise OSError("simulated launch failure")

    monkeypatch.setattr(regression.subprocess, "run", fail_to_start)
    with pytest.raises(VisualRegressionError) as start_failed:
        build_regression_run(run_root, deveco_studio=studio)
    failed_report = json.loads((run_root / "report.json").read_text())
    assert start_failed.value.code == "UIBENCH_REGRESSION_BUILD_START_FAILED"
    assert failed_report["status"] == "failed"
    assert failed_report["capture"]["buildVerification"] == "failed"
    assert not any(
        artifact["path"].endswith(".hap")
        for artifact in failed_report["artifacts"]
    )

    monkeypatch.setattr(
        regression.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=[], returncode=0, stdout="BUILD SUCCESSFUL\n", stderr=""
        ),
    )
    rebuilt = build_regression_run(run_root, deveco_studio=studio)
    rebuilt_paths = {artifact["path"] for artifact in rebuilt["artifacts"]}

    assert rebuilt["status"] == "failed"
    assert rebuilt["capture"]["buildVerification"] == "failed"
    assert not any(path.endswith(".hap") for path in rebuilt_paths)


@pytest.mark.parametrize("timeout", [float("nan"), float("inf"), 0, -1, 3601])
def test_build_regression_run_rejects_invalid_timeout(
    tmp_path: Path,
    timeout: float,
) -> None:
    with pytest.raises(VisualRegressionError) as invalid:
        build_regression_run(tmp_path, timeout_seconds=timeout)

    assert invalid.value.code == "UIBENCH_REGRESSION_BUILD_TIMEOUT_INVALID"
