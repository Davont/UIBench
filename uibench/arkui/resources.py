"""Materialize browser-captured image bytes into a deterministic ArkUI bundle."""
from __future__ import annotations

import hashlib
import io
import json
import re
import struct
import zipfile
import zlib
from dataclasses import dataclass

from uibench.arkui.metadata import ComponentMetadataReport
from uibench.arkui.snapshot import BrowserSnapshot

ResourceBindingKey = tuple[str, str]

_RESOURCE_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")
HARMONY_MODEL_VERSION = "6.0.2"
HARMONY_SDK_VERSION = "6.0.2(22)"
# The generated project paints this behind the page root: it seeds
# start_window_background and matches the ArkUI runtime's default window
# colour. Export gates compare the captured document canvas against it to
# decide whether a root that does not span the viewport still reproduces
# the captured page.
HARMONY_WINDOW_BACKGROUND = "#FFFFFF"


@dataclass(frozen=True)
class MaterializedResource:
    resource_name: str
    asset_uri: str
    logical_path: str
    mime_type: str
    byte_length: int
    sha256: str
    content: bytes
    kinds: tuple[str, ...]
    node_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "resourceName": self.resource_name,
            "assetUri": self.asset_uri,
            "logicalPath": self.logical_path,
            "mimeType": self.mime_type,
            "byteLength": self.byte_length,
            "sha256": self.sha256,
            "kinds": list(self.kinds),
            "nodeIds": list(self.node_ids),
        }


@dataclass(frozen=True)
class ResourceRejection:
    code: str
    message: str
    node_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "message": self.message,
            "nodeIds": list(self.node_ids),
        }


@dataclass(frozen=True)
class MaterializedResources:
    entries: tuple[MaterializedResource, ...]
    bindings: dict[ResourceBindingKey, str]
    rejected: tuple[ResourceRejection, ...]

    def resource_for(self, node_id: str, kind: str) -> str | None:
        return self.bindings.get((node_id, kind))

    def to_dict(self) -> dict[str, object]:
        return {
            "entries": [entry.to_dict() for entry in self.entries],
            "rejected": [item.to_dict() for item in self.rejected],
        }


def _sniff_image(content: bytes) -> tuple[str, str] | None:
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png", "png"
    if content.startswith(b"\xff\xd8\xff"):
        return "image/jpeg", "jpg"
    if content.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif", "gif"
    if len(content) >= 12 and content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return "image/webp", "webp"
    return None


def _valid_use(
    component_by_id: dict[str, str],
    snapshot_by_id: dict[str, object],
    node_id: str,
    kind: str,
) -> bool:
    node = snapshot_by_id[node_id]
    component_name = component_by_id.get(node_id)
    if component_name is None:
        return False
    if kind == "image":
        return component_name == "Image" and bool(
            getattr(node, "resolved_src", None)
        )
    return component_name != "Span" and bool(
        getattr(getattr(node, "computed"), "background_image", "")
        not in {"", "none"}
    )


def materialize_browser_assets(
    report: ComponentMetadataReport,
    snapshot: BrowserSnapshot | None,
) -> MaterializedResources:
    """Validate image bytes and bind them to annotated nodes without I/O."""
    if snapshot is None or not snapshot.assets:
        return MaterializedResources(entries=(), bindings={}, rejected=())

    component_by_id = {
        node.node_id: node.arkui_component
        for node in report.nodes
        if node.node_id is not None
    }
    snapshot_by_id = {node.node_id: node for node in snapshot.nodes}
    pending: dict[str, dict[str, object]] = {}
    bindings: dict[ResourceBindingKey, str] = {}
    rejected: list[ResourceRejection] = []

    for captured in snapshot.assets:
        content = captured.decoded_content()
        sniffed = _sniff_image(content)
        all_node_ids = tuple(sorted({
            node_id
            for use in captured.uses
            for node_id in use.node_ids
        }))
        if sniffed is None:
            rejected.append(ResourceRejection(
                code="UIBENCH_ASSET_FORMAT_UNSUPPORTED",
                message="Captured resource is not PNG, JPEG, GIF, or WebP",
                node_ids=all_node_ids,
            ))
            continue

        mime_type, extension = sniffed
        digest = hashlib.sha256(content).hexdigest()
        resource_name = f"uibench_{digest[:16]}"
        if _RESOURCE_NAME_RE.fullmatch(resource_name) is None:  # defensive
            raise ValueError("generated ArkUI resource name is invalid")
        asset_uri = f"asset://media/{resource_name}"
        accepted_uses: list[tuple[str, str]] = []
        for use in captured.uses:
            for node_id in use.node_ids:
                if _valid_use(
                    component_by_id,
                    snapshot_by_id,
                    node_id,
                    use.kind,
                ):
                    accepted_uses.append((node_id, use.kind))
                else:
                    rejected.append(ResourceRejection(
                        code="UIBENCH_ASSET_USE_INVALID",
                        message=(
                            "Captured resource use does not match the annotated "
                            "node or computed background"
                        ),
                        node_ids=(node_id,),
                    ))
        if not accepted_uses:
            continue

        item = pending.setdefault(digest, {
            "resource_name": resource_name,
            "asset_uri": asset_uri,
            "logical_path": (
                "entry/src/main/resources/base/media/"
                f"{resource_name}.{extension}"
            ),
            "mime_type": mime_type,
            "content": content,
            "kinds": set(),
            "node_ids": set(),
        })
        for node_id, kind in accepted_uses:
            bindings[(node_id, kind)] = asset_uri
            item["kinds"].add(kind)  # type: ignore[union-attr]
            item["node_ids"].add(node_id)  # type: ignore[union-attr]

    entries = tuple(
        MaterializedResource(
            resource_name=str(item["resource_name"]),
            asset_uri=str(item["asset_uri"]),
            logical_path=str(item["logical_path"]),
            mime_type=str(item["mime_type"]),
            byte_length=len(item["content"]),  # type: ignore[arg-type]
            sha256=digest,
            content=item["content"],  # type: ignore[arg-type]
            kinds=tuple(sorted(item["kinds"])),  # type: ignore[arg-type]
            node_ids=tuple(sorted(item["node_ids"])),  # type: ignore[arg-type]
        )
        for digest, item in sorted(pending.items())
    )
    return MaterializedResources(
        entries=entries,
        bindings=bindings,
        rejected=tuple(rejected),
    )


def rewrite_arkts_resources(
    ark_ts: str,
    resources: MaterializedResources,
) -> str:
    """Replace only renderer-emitted asset URI arguments with ArkUI resources."""
    rewritten = ark_ts
    for entry in resources.entries:
        quoted_uri = json.dumps(entry.asset_uri, ensure_ascii=False)
        arkui_resource = f"$r('app.media.{entry.resource_name}')"
        rewritten = rewritten.replace(
            f"Image({quoted_uri})",
            f"Image({arkui_resource})",
        )
        rewritten = rewritten.replace(
            f".backgroundImage({quoted_uri})",
            f".backgroundImage({arkui_resource})",
        )
    return rewritten


def _json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    ).encode("utf-8")


def _png_chunk(kind: bytes, content: bytes) -> bytes:
    return (
        struct.pack(">I", len(content))
        + kind
        + content
        + struct.pack(">I", zlib.crc32(kind + content) & 0xFFFFFFFF)
    )


def _default_app_icon() -> bytes:
    """Return a deterministic 128px Harmony-blue PNG without image deps."""
    width = 128
    height = 128
    pixel = bytes((10, 89, 247, 255))
    scanlines = b"".join(
        b"\x00" + pixel * width for _ in range(height)
    )
    return (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(
            b"IHDR",
            struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0),
        )
        + _png_chunk(b"IDAT", zlib.compress(scanlines, level=9))
        + _png_chunk(b"IEND", b"")
    )


def _bundle_name(page_name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "", page_name.lower())[:36]
    if not slug or not slug[0].isalpha():
        slug = f"page{hashlib.sha256(page_name.encode()).hexdigest()[:12]}"
    return f"com.uibench.generated.{slug}"


def _harmony_project_files(
    page_name: str,
    ark_ts: str,
    resources: MaterializedResources,
) -> tuple[dict[str, bytes], str]:
    """Render a complete single-module HarmonyOS Stage project."""
    bundle_name = _bundle_name(page_name)
    page_path = f"entry/src/main/ets/pages/{page_name}.ets"
    icon = _default_app_icon()
    files: dict[str, bytes] = {
        ".gitignore": (
            "/node_modules\n/oh_modules\n/local.properties\n/.idea\n"
            "**/build\n/.hvigor\n**/.preview\n"
        ).encode("utf-8"),
        "AppScope/app.json5": _json_bytes({
            "app": {
                "bundleName": bundle_name,
                "vendor": "UIBench",
                "versionCode": 1000000,
                "versionName": "1.0.0",
                "icon": "$media:app_icon",
                "label": "$string:app_name",
            }
        }),
        "AppScope/resources/base/element/string.json": _json_bytes({
            "string": [{"name": "app_name", "value": page_name}]
        }),
        "AppScope/resources/base/media/app_icon.png": icon,
        "build-profile.json5": _json_bytes({
            "app": {
                "signingConfigs": [],
                "products": [{
                    "name": "default",
                    "targetSdkVersion": HARMONY_SDK_VERSION,
                    "compatibleSdkVersion": HARMONY_SDK_VERSION,
                    "runtimeOS": "HarmonyOS",
                    "buildOption": {
                        "strictMode": {
                            "caseSensitiveCheck": True,
                            "useNormalizedOHMUrl": True,
                        }
                    },
                }],
                "buildModeSet": [
                    {"name": "debug"},
                    {"name": "release"},
                ],
            },
            "modules": [{
                "name": "entry",
                "srcPath": "./entry",
                "targets": [{
                    "name": "default",
                    "applyToProducts": ["default"],
                }],
            }],
        }),
        "hvigor/hvigor-config.json5": _json_bytes({
            "modelVersion": HARMONY_MODEL_VERSION,
            "dependencies": {},
            "execution": {},
            "logging": {},
            "debugging": {},
            "nodeOptions": {},
        }),
        "hvigorfile.ts": (
            "import { appTasks } from '@ohos/hvigor-ohos-plugin';\n\n"
            "export default {\n"
            "  system: appTasks,\n"
            "  plugins: []\n"
            "}\n"
        ).encode("utf-8"),
        "oh-package.json5": _json_bytes({
            "modelVersion": HARMONY_MODEL_VERSION,
            "description": "UIBench generated HarmonyOS project.",
            "dependencies": {},
            "devDependencies": {},
        }),
        "entry/build-profile.json5": _json_bytes({
            "apiType": "stageMode",
            "buildOption": {
                "resOptions": {
                    "copyCodeResource": {"enable": False}
                }
            },
            "targets": [{"name": "default"}],
        }),
        "entry/hvigorfile.ts": (
            "import { hapTasks } from '@ohos/hvigor-ohos-plugin';\n\n"
            "export default {\n"
            "  system: hapTasks,\n"
            "  plugins: []\n"
            "}\n"
        ).encode("utf-8"),
        "entry/oh-package.json5": _json_bytes({
            "name": "entry",
            "version": "1.0.0",
            "description": "UIBench generated entry module.",
            "main": "",
            "author": "UIBench",
            "license": "",
            "dependencies": {},
        }),
        "entry/src/main/ets/entryability/EntryAbility.ets": (
            "import { UIAbility } from '@kit.AbilityKit';\n"
            "import { window } from '@kit.ArkUI';\n\n"
            "export default class EntryAbility extends UIAbility {\n"
            "  onWindowStageCreate(windowStage: window.WindowStage): void {\n"
            f"    windowStage.loadContent('pages/{page_name}', (error) => {{\n"
            "      if (error.code) {\n"
            "        console.error(`Failed to load generated page: ${error.message}`);\n"
            "      }\n"
            "    });\n"
            "  }\n"
            "}\n"
        ).encode("utf-8"),
        page_path: ark_ts.encode("utf-8"),
        "entry/src/main/module.json5": _json_bytes({
            "module": {
                "name": "entry",
                "type": "entry",
                "description": "$string:module_desc",
                "mainElement": "EntryAbility",
                "deviceTypes": ["phone"],
                "deliveryWithInstall": True,
                "installationFree": False,
                "pages": "$profile:main_pages",
                "abilities": [{
                    "name": "EntryAbility",
                    "srcEntry": "./ets/entryability/EntryAbility.ets",
                    "description": "$string:entryability_desc",
                    "icon": "$media:start_icon",
                    "label": "$string:entryability_label",
                    "startWindowIcon": "$media:start_icon",
                    "startWindowBackground": "$color:start_window_background",
                    "exported": True,
                    "skills": [{
                        "entities": ["entity.system.home"],
                        "actions": ["ohos.want.action.home"],
                    }],
                }],
            }
        }),
        "entry/src/main/resources/base/element/color.json": _json_bytes({
            "color": [{
                "name": "start_window_background",
                "value": HARMONY_WINDOW_BACKGROUND,
            }]
        }),
        "entry/src/main/resources/base/element/string.json": _json_bytes({
            "string": [
                {"name": "module_desc", "value": "UIBench generated module"},
                {"name": "entryability_desc", "value": "Generated UI preview"},
                {"name": "entryability_label", "value": page_name},
            ]
        }),
        "entry/src/main/resources/base/media/start_icon.png": icon,
        "entry/src/main/resources/base/profile/main_pages.json": _json_bytes({
            "src": [f"pages/{page_name}"]
        }),
        "README.md": (
            f"# {page_name}\n\n"
            "UIBench generated HarmonyOS Stage project.\n\n"
            f"- DevEco Studio: 6.0.2\n"
            f"- Target/compatible SDK: {HARMONY_SDK_VERSION}\n"
            f"- Entry page: `{page_path}`\n"
            "- Signing and `local.properties` are intentionally not included.\n\n"
            "Open this directory in DevEco Studio, allow project sync, "
            "configure automatic signing if device installation is needed, "
            "and run the `entry` module.\n"
        ).encode("utf-8"),
    }
    for entry in resources.entries:
        files[entry.logical_path] = entry.content
    return files, bundle_name


def build_harmony_project(
    page_name: str,
    ark_ts: str,
    resources: MaterializedResources,
) -> tuple[bytes, tuple[str, ...], str]:
    """Create a deterministic complete HarmonyOS Stage project ZIP."""
    files, bundle_name = _harmony_project_files(page_name, ark_ts, resources)
    page_path = f"entry/src/main/ets/pages/{page_name}.ets"
    manifest = {
        "kind": "uibench-harmonyos-project",
        "projectVersion": 1,
        "page": page_path,
        "bundleName": bundle_name,
        "model": "stageMode",
        "module": "entry",
        "modelVersion": HARMONY_MODEL_VERSION,
        "targetSdkVersion": HARMONY_SDK_VERSION,
        "compatibleSdkVersion": HARMONY_SDK_VERSION,
        "completeProject": True,
        "buildVerification": "not-run",
        "assets": [entry.to_dict() for entry in resources.entries],
        "note": (
            "Open in DevEco Studio and configure signing before installing "
            "on a physical device."
        ),
    }
    files["uibench-export.json"] = (
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")

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
            info.external_attr = 0o100644 << 16
            archive.writestr(info, files[name])
    return output.getvalue(), tuple(sorted(files)), bundle_name


__all__ = [
    "MaterializedResource",
    "MaterializedResources",
    "ResourceRejection",
    "HARMONY_MODEL_VERSION",
    "HARMONY_SDK_VERSION",
    "HARMONY_WINDOW_BACKGROUND",
    "build_harmony_project",
    "materialize_browser_assets",
    "rewrite_arkts_resources",
]
