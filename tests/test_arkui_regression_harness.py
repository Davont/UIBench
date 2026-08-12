"""Tests for the regression-only HarmonyOS project harness."""
from __future__ import annotations

import hashlib
import io
import json
import stat
import warnings
import zipfile

import pytest

from uibench.arkui.regression_harness import (
    ENTRY_ABILITY_PATH,
    EXPORT_MANIFEST_PATH,
    HARNESS_MARKER,
    HARNESS_STRATEGY,
    HARNESS_VERSION,
    inject_regression_harness,
)
from uibench.arkui.resources import MaterializedResources, build_harmony_project
from uibench.arkui.visual_regression import VisualRegressionError


PAGE_PATH = "entry/src/main/ets/pages/HarnessPage.ets"
CANONICAL_PAGE = """@Entry
@Component
struct HarnessPage {
  build() {
    Column() {
      Text("brace } and // text")
    }
      .width(390)
      .height(844)
  }
}
"""


def _project() -> bytes:
    project, _, _ = build_harmony_project(
        "HarnessPage",
        CANONICAL_PAGE,
        MaterializedResources(entries=(), bindings={}, rejected=()),
    )
    return project


def _rewrite_zip(
    project: bytes,
    *,
    replacement: tuple[str, bytes] | None = None,
    extra: tuple[zipfile.ZipInfo | str, bytes] | None = None,
) -> bytes:
    with zipfile.ZipFile(io.BytesIO(project)) as source:
        files = [(item.filename, source.read(item)) for item in source.infolist()]
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        for name, content in files:
            if replacement is not None and name == replacement[0]:
                content = replacement[1]
            archive.writestr(name, content)
        if extra is not None:
            archive.writestr(extra[0], extra[1])
    return output.getvalue()


def test_harness_is_deterministic_and_preserves_canonical_page() -> None:
    source = _project()
    first = inject_regression_harness(
        source,
        canonical_page=CANONICAL_PAGE,
        viewport_width=390,
        viewport_height=844,
    )
    second = inject_regression_harness(
        source,
        canonical_page=CANONICAL_PAGE,
        viewport_width=390,
        viewport_height=844,
    )

    assert first.content == second.content
    assert first.provenance == second.provenance
    assert first.provenance["sourceProjectSha256"] == hashlib.sha256(
        source
    ).hexdigest()
    assert first.provenance["preparedProjectSha256"] == hashlib.sha256(
        first.content
    ).hexdigest()
    assert first.provenance["viewport"] == {"width": 390, "height": 844}
    assert first.provenance["harnessVersion"] == HARNESS_VERSION == 2
    assert first.provenance["strategy"] == HARNESS_STRATEGY
    assert first.provenance["layoutContract"] == {
        "displayMetrics": "display.getDefaultDisplaySync",
        "childMeasure": "fixed-canonical-viewport",
        "scale": "minimum-display-vp-ratio",
        "origin": {"x": 0, "y": 0},
    }
    assert first.provenance["sourcePageSha256"] == hashlib.sha256(
        CANONICAL_PAGE.encode()
    ).hexdigest()

    with zipfile.ZipFile(io.BytesIO(source)) as original, zipfile.ZipFile(
        io.BytesIO(first.content)
    ) as prepared:
        assert prepared.namelist() == sorted(prepared.namelist())
        assert prepared.namelist() == original.namelist()
        changed = {
            name for name in prepared.namelist()
            if prepared.read(name) != original.read(name)
        }
        assert changed == {PAGE_PATH, ENTRY_ABILITY_PATH, EXPORT_MANIFEST_PATH}
        page = prepared.read(PAGE_PATH).decode()
        entry = prepared.read(ENTRY_ABILITY_PATH).decode()
        manifest = json.loads(prepared.read(EXPORT_MANIFEST_PATH))
        assert CANONICAL_PAGE not in page
        assert page.startswith(
            "import { display } from '@kit.ArkUI';\n\n"
            + HARNESS_MARKER
            + "@Entry\n"
        )
        assert "RenderFit" not in page
        assert "Stack({ alignContent: Alignment.TopStart })" in page
        assert page.count("display.getDefaultDisplaySync()") == 1
        assert page.count("this.uibenchDisplay.densityPixels") == 4
        assert (
            "this.uibenchDisplay.width / this.uibenchDisplay.densityPixels / 390"
            in page
        )
        assert (
            "this.uibenchDisplay.height / this.uibenchDisplay.densityPixels / 844"
            in page
        )
        assert page.count("onMeasureSize(") == 1
        assert page.count("onPlaceChildren(") == 1
        assert (
            "child.measure({ minWidth: 390, maxWidth: 390, "
            "minHeight: 844, maxHeight: 844 });"
        ) in page
        assert "child.layout({ x: 0, y: 0 })" in page
        assert page.index("onMeasureSize(") < page.index("  build() {")
        assert page.index("onPlaceChildren(") < page.index("  build() {")
        wrapper = page.rsplit("    }\n      .width(390)\n", 1)[1]
        assert wrapper.startswith(
            "      .height(844)\n"
            "      .scale({\n"
            "        x: this.uibenchViewportScale,\n"
            "        y: this.uibenchViewportScale,\n"
            "        centerX: 0,\n"
            "        centerY: 0\n"
            "      })\n"
        )
        assert entry.index("await mainWindow.setWindowLayoutFullScreen(true)") < (
            entry.index("await mainWindow.setWindowSystemBarEnable([])")
        ) < entry.index("windowStage.loadContent")
        assert manifest["regressionHarness"]["sourceProjectSha256"] == (
            first.provenance["sourceProjectSha256"]
        )
        assert manifest["regressionHarness"]["strategy"] == HARNESS_STRATEGY
        assert manifest["regressionHarness"]["layoutContract"] == (
            first.provenance["layoutContract"]
        )
        assert "preparedProjectSha256" not in manifest["regressionHarness"]
        for info in prepared.infolist():
            assert info.date_time == (1980, 1, 1, 0, 0, 0)
            assert info.create_system == 3
            assert info.external_attr >> 16 == 0o100644
            assert info.extra == b""
            assert info.comment == b""


def test_harness_rejects_source_mismatch_and_reinjection() -> None:
    source = _project()
    with pytest.raises(VisualRegressionError) as mismatch:
        inject_regression_harness(
            source,
            canonical_page=CANONICAL_PAGE.replace("HarnessPage", "OtherPage"),
            viewport_width=390,
            viewport_height=844,
        )
    assert mismatch.value.code == "UIBENCH_REGRESSION_HARNESS_SOURCE_MISMATCH"

    prepared = inject_regression_harness(
        source,
        canonical_page=CANONICAL_PAGE,
        viewport_width=390,
        viewport_height=844,
    )
    with pytest.raises(VisualRegressionError) as reinjected:
        inject_regression_harness(
            prepared.content,
            canonical_page=CANONICAL_PAGE,
            viewport_width=390,
            viewport_height=844,
        )
    assert reinjected.value.code == "UIBENCH_REGRESSION_HARNESS_MANIFEST_INVALID"


@pytest.mark.parametrize(
    "unsafe_name",
    [
        "../outside.txt",
        "/absolute.txt",
        "entry\\windows.txt",
        "Entry/src/main/module.json5",
    ],
)
def test_harness_rejects_unsafe_or_case_colliding_entries(
    unsafe_name: str,
) -> None:
    unsafe = _rewrite_zip(_project(), extra=(unsafe_name, b"unsafe"))

    with pytest.raises(VisualRegressionError) as rejected:
        inject_regression_harness(
            unsafe,
            canonical_page=CANONICAL_PAGE,
            viewport_width=390,
            viewport_height=844,
        )

    assert rejected.value.code == "UIBENCH_REGRESSION_HARNESS_PROJECT_PATH_INVALID"


def test_harness_rejects_symlink_and_duplicate_entries() -> None:
    symlink = zipfile.ZipInfo("symlink")
    symlink.create_system = 3
    symlink.external_attr = (stat.S_IFLNK | 0o777) << 16
    unsafe = _rewrite_zip(_project(), extra=(symlink, b"target"))
    with pytest.raises(VisualRegressionError) as rejected_symlink:
        inject_regression_harness(
            unsafe,
            canonical_page=CANONICAL_PAGE,
            viewport_width=390,
            viewport_height=844,
        )
    assert rejected_symlink.value.code == (
        "UIBENCH_REGRESSION_HARNESS_PROJECT_PATH_INVALID"
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        duplicate = _rewrite_zip(
            _project(),
            extra=("entry/src/main/module.json5", b"duplicate"),
        )
    with pytest.raises(VisualRegressionError) as rejected_duplicate:
        inject_regression_harness(
            duplicate,
            canonical_page=CANONICAL_PAGE,
            viewport_width=390,
            viewport_height=844,
        )
    assert rejected_duplicate.value.code == (
        "UIBENCH_REGRESSION_HARNESS_PROJECT_PATH_INVALID"
    )


def test_harness_rejects_invalid_manifest_and_generated_page_shape() -> None:
    missing_manifest = _rewrite_zip(
        _project(),
        replacement=(EXPORT_MANIFEST_PATH, b"{}"),
    )
    with pytest.raises(VisualRegressionError) as manifest:
        inject_regression_harness(
            missing_manifest,
            canonical_page=CANONICAL_PAGE,
            viewport_width=390,
            viewport_height=844,
        )
    assert manifest.value.code == "UIBENCH_REGRESSION_HARNESS_MANIFEST_INVALID"

    unsupported_page = CANONICAL_PAGE.replace("  build() {", "  build(): void {")
    unsupported_project = _rewrite_zip(
        _project(),
        replacement=(PAGE_PATH, unsupported_page.encode()),
    )
    with pytest.raises(VisualRegressionError) as page:
        inject_regression_harness(
            unsupported_project,
            canonical_page=unsupported_page,
            viewport_width=390,
            viewport_height=844,
        )
    assert page.value.code == "UIBENCH_REGRESSION_HARNESS_PAGE_INVALID"


@pytest.mark.parametrize(
    ("width", "height"),
    [(0, 844), (390, 0), (3841, 844), (390, 3841), (True, 844)],
)
def test_harness_rejects_unbounded_viewport(
    width: object,
    height: object,
) -> None:
    with pytest.raises(VisualRegressionError) as viewport:
        inject_regression_harness(
            _project(),
            canonical_page=CANONICAL_PAGE,
            viewport_width=width,  # type: ignore[arg-type]
            viewport_height=height,  # type: ignore[arg-type]
        )
    assert viewport.value.code == "UIBENCH_REGRESSION_HARNESS_VIEWPORT_INVALID"
