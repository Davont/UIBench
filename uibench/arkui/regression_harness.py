"""Regression-only transformation of deterministic HarmonyOS project bundles.

The canonical ArkTS export remains untouched.  This module rewrites only the
copy embedded in a visual-regression project so a device capture gets a stable,
display-independent canonical viewport and a fail-closed immersive EntryAbility.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import stat
import unicodedata
import zipfile
from dataclasses import dataclass
from pathlib import PurePosixPath

from uibench.arkui.visual_regression import VisualRegressionError

HARNESS_VERSION = 2
HARNESS_KIND = "uibench-arkui-regression-harness"
HARNESS_STRATEGY = "custom-layout-display-density-contain-top-left"
HARNESS_MARKER = "// UIBench regression harness v2\n"
ENTRY_ABILITY_PATH = "entry/src/main/ets/entryability/EntryAbility.ets"
EXPORT_MANIFEST_PATH = "uibench-export.json"
MAX_PROJECT_BYTES = 64 * 1024 * 1024
MAX_PROJECT_FILES = 5000
MAX_PROJECT_UNCOMPRESSED_BYTES = 50_000_000
_PAGE_PATH_RE = re.compile(
    r"^entry/src/main/ets/pages/[A-Za-z_][A-Za-z0-9_]*\.ets$"
)


@dataclass(frozen=True)
class HarnessedProject:
    content: bytes
    files: tuple[str, ...]
    provenance: dict[str, object]


def _fail(code: str, message: str) -> VisualRegressionError:
    return VisualRegressionError(code, message)


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _safe_archive_files(project: bytes) -> dict[str, bytes]:
    if len(project) > MAX_PROJECT_BYTES:
        raise _fail(
            "UIBENCH_REGRESSION_HARNESS_PROJECT_TOO_LARGE",
            "HarmonyOS project ZIP exceeds the regression harness byte limit",
        )
    try:
        archive = zipfile.ZipFile(io.BytesIO(project))
    except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
        raise _fail(
            "UIBENCH_REGRESSION_HARNESS_PROJECT_INVALID",
            "HarmonyOS project ZIP is invalid",
        ) from exc
    try:
        with archive:
            entries = archive.infolist()
            if (
                len(entries) > MAX_PROJECT_FILES
                or sum(item.file_size for item in entries)
                > MAX_PROJECT_UNCOMPRESSED_BYTES
            ):
                raise _fail(
                    "UIBENCH_REGRESSION_HARNESS_PROJECT_TOO_LARGE",
                    "HarmonyOS project ZIP exceeds regression harness limits",
                )
            files: dict[str, bytes] = {}
            identities: set[str] = set()
            for item in entries:
                name = item.filename
                segments = name.split("/")
                path = PurePosixPath(name)
                mode = item.external_attr >> 16
                identity = unicodedata.normalize("NFC", name).casefold()
                if (
                    not name
                    or len(name) > 500
                    or "\\" in name
                    or "\x00" in name
                    or any(part in {"", ".", ".."} for part in segments)
                    or any(ord(char) < 32 for char in name)
                    or path.is_absolute()
                    or ".." in path.parts
                    or item.is_dir()
                    or stat.S_ISLNK(mode)
                    or stat.S_IFMT(mode) not in {0, stat.S_IFREG}
                    or bool(item.flag_bits & 0x1)
                    or name in files
                    or identity in identities
                ):
                    raise _fail(
                        "UIBENCH_REGRESSION_HARNESS_PROJECT_PATH_INVALID",
                        "HarmonyOS project ZIP contains an unsafe or duplicate entry",
                    )
                try:
                    content = archive.read(item)
                except (
                    OSError,
                    RuntimeError,
                    NotImplementedError,
                    RecursionError,
                    zipfile.BadZipFile,
                ) as exc:
                    raise _fail(
                        "UIBENCH_REGRESSION_HARNESS_PROJECT_INVALID",
                        "HarmonyOS project ZIP entry could not be read",
                    ) from exc
                if len(content) != item.file_size:
                    raise _fail(
                        "UIBENCH_REGRESSION_HARNESS_PROJECT_INVALID",
                        "HarmonyOS project ZIP entry length is inconsistent",
                    )
                files[name] = content
                identities.add(identity)
            return files
    except VisualRegressionError:
        raise
    except (
        OSError,
        RuntimeError,
        NotImplementedError,
        RecursionError,
        zipfile.BadZipFile,
    ) as exc:
        raise _fail(
            "UIBENCH_REGRESSION_HARNESS_PROJECT_INVALID",
            "HarmonyOS project ZIP could not be inspected",
        ) from exc


def _entry_ability_source(page_route: str) -> bytes:
    return (
        "import { UIAbility } from '@kit.AbilityKit';\n"
        "import { BusinessError } from '@kit.BasicServicesKit';\n"
        "import { window } from '@kit.ArkUI';\n\n"
        f"{HARNESS_MARKER}"
        "export default class EntryAbility extends UIAbility {\n"
        "  onWindowStageCreate(windowStage: window.WindowStage): void {\n"
        "    this.configureRegressionWindow(windowStage).catch((error: BusinessError) => {\n"
        "      console.error(`Failed to configure regression window: ${error.code}: ${error.message}`);\n"
        "    });\n"
        "  }\n\n"
        "  private async configureRegressionWindow(\n"
        "    windowStage: window.WindowStage,\n"
        "  ): Promise<void> {\n"
        "    const mainWindow = windowStage.getMainWindowSync();\n"
        "    await mainWindow.setWindowLayoutFullScreen(true);\n"
        "    await mainWindow.setWindowSystemBarEnable([]);\n"
        f"    windowStage.loadContent('{page_route}', (error) => {{\n"
        "      if (error.code) {\n"
        "        console.error(`Failed to load generated page: ${error.message}`);\n"
        "      }\n"
        "    });\n"
        "  }\n"
        "}\n"
    ).encode("utf-8")


def _canonical_entry_ability_source(page_route: str) -> bytes:
    return (
        "import { UIAbility } from '@kit.AbilityKit';\n"
        "import { window } from '@kit.ArkUI';\n\n"
        "export default class EntryAbility extends UIAbility {\n"
        "  onWindowStageCreate(windowStage: window.WindowStage): void {\n"
        f"    windowStage.loadContent('{page_route}', (error) => {{\n"
        "      if (error.code) {\n"
        "        console.error(`Failed to load generated page: ${error.message}`);\n"
        "      }\n"
        "    });\n"
        "  }\n"
        "}\n"
    ).encode("utf-8")


def _balanced_arkts_braces(source: str) -> bool:
    """Check generated ArkTS braces while ignoring quoted text and comments."""
    depth = 0
    index = 0
    quote: str | None = None
    escaped = False
    line_comment = False
    block_comment = False
    while index < len(source):
        char = source[index]
        following = source[index + 1] if index + 1 < len(source) else ""
        if line_comment:
            line_comment = char != "\n"
        elif block_comment:
            if char == "*" and following == "/":
                block_comment = False
                index += 1
        elif quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
        elif char == "/" and following == "/":
            line_comment = True
            index += 1
        elif char == "/" and following == "*":
            block_comment = True
            index += 1
        elif char in {"'", '"', "`"}:
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth < 0:
                return False
        index += 1
    return depth == 0 and quote is None and not block_comment


def _harness_page(
    canonical_page: bytes,
    *,
    viewport_width: int,
    viewport_height: int,
) -> bytes:
    try:
        source = canonical_page.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise _fail(
            "UIBENCH_REGRESSION_HARNESS_PAGE_INVALID",
            "Canonical ArkTS page is not UTF-8",
        ) from exc
    build_marker = "  build() {\n"
    closing = "  }\n}\n"
    if (
        "// UIBench regression harness v" in source
        or source.count(build_marker) != 1
        or not source.endswith(closing)
        or "@Entry" not in source
        or "@Component" not in source
        or not _balanced_arkts_braces(source)
    ):
        raise _fail(
            "UIBENCH_REGRESSION_HARNESS_PAGE_INVALID",
            "Canonical ArkTS page does not match the supported generated shape",
        )
    prefix, remainder = source.split(build_marker, 1)
    build_body = remainder[:-len(closing)]
    reserved_prefix_fragments = (
        "import { display } from '@kit.ArkUI';",
        "uibenchDisplay",
        "uibenchViewportScale",
        "onMeasureSize(",
        "onPlaceChildren(",
    )
    if (
        any(fragment in prefix for fragment in reserved_prefix_fragments)
        or ".renderFit(RenderFit.RESIZE_CONTAIN_TOP_LEFT)" in build_body
        or not build_body.strip()
        or build_body.rstrip()[-1] not in {")", "}"}
    ):
        raise _fail(
            "UIBENCH_REGRESSION_HARNESS_PAGE_INVALID",
            "Canonical ArkTS page does not end in a root component chain",
        )
    transformed = (
        "import { display } from '@kit.ArkUI';\n\n"
        + HARNESS_MARKER
        + prefix
        + "  private readonly uibenchDisplay: display.Display = "
        + "display.getDefaultDisplaySync();\n"
        + "  private readonly uibenchViewportScale: number = Math.min(\n"
        + "    this.uibenchDisplay.width / this.uibenchDisplay.densityPixels / "
        + f"{viewport_width},\n"
        + "    this.uibenchDisplay.height / this.uibenchDisplay.densityPixels / "
        + f"{viewport_height}\n"
        + "  );\n\n"
        + "  onMeasureSize(\n"
        + "    selfLayoutInfo: GeometryInfo,\n"
        + "    children: Array<Measurable>,\n"
        + "    constraint: ConstraintSizeOptions,\n"
        + "  ): SizeResult {\n"
        + "    children.forEach((child: Measurable) => {\n"
        + "      child.measure({ "
        + f"minWidth: {viewport_width}, maxWidth: {viewport_width}, "
        + f"minHeight: {viewport_height}, maxHeight: {viewport_height}"
        + " });\n"
        + "    });\n"
        + "    return {\n"
        + "      width: this.uibenchDisplay.width / "
        + "this.uibenchDisplay.densityPixels,\n"
        + "      height: this.uibenchDisplay.height / "
        + "this.uibenchDisplay.densityPixels,\n"
        + "    };\n"
        + "  }\n\n"
        + "  onPlaceChildren(\n"
        + "    selfLayoutInfo: GeometryInfo,\n"
        + "    children: Array<Layoutable>,\n"
        + "    constraint: ConstraintSizeOptions,\n"
        + "  ): void {\n"
        + "    children.forEach((child: Layoutable) => "
        + "child.layout({ x: 0, y: 0 }));\n"
        + "  }\n\n"
        + build_marker
        + "    Stack({ alignContent: Alignment.TopStart }) {\n"
        + build_body
        + "    }\n"
        + f"      .width({viewport_width})\n"
        + f"      .height({viewport_height})\n"
        + "      .scale({\n"
        + "        x: this.uibenchViewportScale,\n"
        + "        y: this.uibenchViewportScale,\n"
        + "        centerX: 0,\n"
        + "        centerY: 0\n"
        + "      })\n"
        + closing
    )
    if not _balanced_arkts_braces(transformed):
        raise _fail(
            "UIBENCH_REGRESSION_HARNESS_PAGE_INVALID",
            "Regression harness produced invalid ArkTS brace structure",
        )
    return transformed.encode("utf-8")


def _deterministic_zip(files: dict[str, bytes]) -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(
        output,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.extra = b""
            info.comment = b""
            archive.writestr(info, files[name], compresslevel=9)
    return output.getvalue()


def inject_regression_harness(
    project: bytes,
    *,
    canonical_page: str,
    viewport_width: int,
    viewport_height: int,
) -> HarnessedProject:
    """Return a deterministic regression project derived from one exporter ZIP."""
    if (
        type(viewport_width) is not int
        or type(viewport_height) is not int
        or not 1 <= viewport_width <= 3840
        or not 1 <= viewport_height <= 3840
    ):
        raise _fail(
            "UIBENCH_REGRESSION_HARNESS_VIEWPORT_INVALID",
            "Regression harness viewport must contain bounded positive integers",
        )
    files = _safe_archive_files(project)
    manifest_bytes = files.get(EXPORT_MANIFEST_PATH)
    if manifest_bytes is None:
        raise _fail(
            "UIBENCH_REGRESSION_HARNESS_MANIFEST_INVALID",
            "HarmonyOS project is missing uibench-export.json",
        )
    try:
        manifest = json.loads(manifest_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise _fail(
            "UIBENCH_REGRESSION_HARNESS_MANIFEST_INVALID",
            "HarmonyOS project export manifest is invalid",
        ) from exc
    page_path = manifest.get("page") if isinstance(manifest, dict) else None
    if (
        not isinstance(manifest, dict)
        or manifest.get("kind") != "uibench-harmonyos-project"
        or manifest.get("projectVersion") != 1
        or "regressionHarness" in manifest
        or not isinstance(page_path, str)
        or not _PAGE_PATH_RE.fullmatch(page_path)
    ):
        raise _fail(
            "UIBENCH_REGRESSION_HARNESS_MANIFEST_INVALID",
            "HarmonyOS project export manifest is unsupported",
        )
    canonical_page_bytes = canonical_page.encode("utf-8")
    archived_page = files.get(page_path)
    archived_entry = files.get(ENTRY_ABILITY_PATH)
    page_route = page_path.removeprefix("entry/src/main/ets/").removesuffix(".ets")
    expected_entry = _canonical_entry_ability_source(page_route)
    if archived_page != canonical_page_bytes:
        raise _fail(
            "UIBENCH_REGRESSION_HARNESS_SOURCE_MISMATCH",
            "Project page does not match the canonical ArkTS export",
        )
    if archived_entry != expected_entry:
        raise _fail(
            "UIBENCH_REGRESSION_HARNESS_SOURCE_MISMATCH",
            "Project EntryAbility does not match the canonical exporter shell",
        )

    prepared_page = _harness_page(
        canonical_page_bytes,
        viewport_width=viewport_width,
        viewport_height=viewport_height,
    )
    prepared_entry = _entry_ability_source(page_route)
    embedded_provenance: dict[str, object] = {
        "kind": HARNESS_KIND,
        "harnessVersion": HARNESS_VERSION,
        "strategy": HARNESS_STRATEGY,
        "viewport": {"width": viewport_width, "height": viewport_height},
        "layoutContract": {
            "displayMetrics": "display.getDefaultDisplaySync",
            "childMeasure": "fixed-canonical-viewport",
            "scale": "minimum-display-vp-ratio",
            "origin": {"x": 0, "y": 0},
        },
        "canonicalPageArtifact": "export/page.ets",
        "projectPage": page_path,
        "entryAbility": ENTRY_ABILITY_PATH,
        "sourceProjectSha256": _sha256(project),
        "sourcePageSha256": _sha256(canonical_page_bytes),
        "preparedPageSha256": _sha256(prepared_page),
        "sourceEntryAbilitySha256": _sha256(archived_entry),
        "preparedEntryAbilitySha256": _sha256(prepared_entry),
    }
    manifest["regressionHarness"] = embedded_provenance
    files[page_path] = prepared_page
    files[ENTRY_ABILITY_PATH] = prepared_entry
    files[EXPORT_MANIFEST_PATH] = _json_bytes(manifest)
    prepared_project = _deterministic_zip(files)
    provenance = {
        **embedded_provenance,
        "preparedProjectSha256": _sha256(prepared_project),
        "fileCount": len(files),
    }
    return HarnessedProject(
        content=prepared_project,
        files=tuple(sorted(files)),
        provenance=provenance,
    )


__all__ = [
    "ENTRY_ABILITY_PATH",
    "EXPORT_MANIFEST_PATH",
    "HARNESS_KIND",
    "HARNESS_MARKER",
    "HARNESS_STRATEGY",
    "HARNESS_VERSION",
    "HarnessedProject",
    "inject_regression_harness",
]
