"""Integrity and offline-runtime tests for the vendored html-to-arkui package."""
from __future__ import annotations

import base64
import hashlib
import importlib.util
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import tarfile

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VENDOR_ROOT = PROJECT_ROOT / "vendor/html-to-arkui"
MANIFEST_PATH = VENDOR_ROOT / "manifest.json"
SOURCE_REPOSITORY = PROJECT_ROOT.parent / "html-to-arkui"


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def test_vendored_archive_matches_manifest_and_contains_safe_runtime() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    archive = VENDOR_ROOT / manifest["archive"]
    payload = archive.read_bytes()

    assert manifest["manifestVersion"] == 1
    assert manifest["packageName"] == "@local/html-to-arkui"
    assert manifest["archive"] == (
        f"local-html-to-arkui-{manifest['packageVersion']}.tgz"
    )
    assert len(payload) == manifest["byteLength"]
    assert _sha256(payload) == manifest["sha256"]
    integrity = "sha512-" + base64.b64encode(
        hashlib.sha512(payload).digest()
    ).decode("ascii")
    assert integrity == manifest["npmIntegrity"]

    with tarfile.open(archive, mode="r:gz") as package:
        members = package.getmembers()
        assert 1 <= len(members) <= 600
        assert sum(member.size for member in members) <= 5_000_000

        names: set[str] = set()
        folded_names: set[str] = set()
        for member in members:
            path = PurePosixPath(member.name)
            assert not path.is_absolute()
            assert "\\" not in member.name
            assert path.parts[0] == "package"
            assert not any(part in {"", ".", ".."} for part in path.parts)
            assert member.isfile() or member.isdir()
            assert member.name not in names
            assert member.name.casefold() not in folded_names
            names.add(member.name)
            folded_names.add(member.name.casefold())

        required = {
            "package/package.json",
            "package/dist/index.js",
            "package/contracts/arkui-component-registry.json",
            "package/contracts/screen-ir.schema.json",
        }
        assert required <= names

        package_json_file = package.extractfile("package/package.json")
        assert package_json_file is not None
        package_json = json.load(package_json_file)
        assert package_json["name"] == manifest["packageName"]
        assert package_json["version"] == manifest["packageVersion"]
        assert set(package_json["bundledDependencies"]) == {"css-tree", "parse5"}
        assert not ({"preinstall", "install", "postinstall"} & package_json["scripts"].keys())

        bundled = set(manifest["bundledRuntimeDependencies"])
        assert bundled == {
            "css-tree", "entities", "mdn-data", "parse5", "source-map-js",
        }
        for dependency in bundled:
            prefix = f"package/node_modules/{dependency}/"
            assert any(name.startswith(prefix) for name in names)

        renderer_file = package.extractfile("package/dist/arkts/render.js")
        assert renderer_file is not None
        renderer = renderer_file.read()
        assert b"align(Alignment.TopStart)" in renderer
        assert b"dividerColor" in renderer
        assert b"dividerStrokeWidth" in renderer
        assert b"dividerVertical" in renderer

        screen_ir_file = package.extractfile(
            "package/contracts/screen-ir.schema.json"
        )
        assert screen_ir_file is not None
        screen_ir_schema = json.load(screen_ir_file)
        style_properties = screen_ir_schema["$defs"]["styles"]["properties"]
        assert {
            "dividerColor", "dividerStrokeWidth", "dividerVertical",
        } <= set(style_properties)


def test_source_commit_is_clean_and_reconstructs_package_metadata() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    commit = manifest["sourceCommit"]
    assert manifest["sourceTreeState"] == "clean"
    assert len(commit) == 40
    assert all(character in "0123456789abcdef" for character in commit)
    assert not any(key.startswith("sourcePatch") for key in manifest)
    assert "sourceDiffSha256" not in manifest

    if not (SOURCE_REPOSITORY / ".git").is_dir():
        return

    subprocess.run(
        ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
        cwd=SOURCE_REPOSITORY,
        check=True,
        capture_output=True,
    )
    source_package = subprocess.run(
        ["git", "show", f"{commit}:package.json"],
        cwd=SOURCE_REPOSITORY,
        check=True,
        capture_output=True,
    ).stdout
    source_renderer = subprocess.run(
        ["git", "show", f"{commit}:src/arkts/render.ts"],
        cwd=SOURCE_REPOSITORY,
        check=True,
        capture_output=True,
    ).stdout

    with tarfile.open(VENDOR_ROOT / manifest["archive"], mode="r:gz") as package:
        packaged_json = package.extractfile("package/package.json")
        assert packaged_json is not None
        assert packaged_json.read() == source_package
    assert b"align(Alignment.TopStart)" in source_renderer
    assert b"dividerColor" in source_renderer
    assert b"dividerStrokeWidth" in source_renderer
    assert b"dividerVertical" in source_renderer


def test_package_lock_pins_the_exact_vendored_archive() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    lock = json.loads((PROJECT_ROOT / "package-lock.json").read_text(encoding="utf-8"))
    dependency = lock["packages"]["node_modules/@local/html-to-arkui"]

    assert lock["packages"][""]["dependencies"][manifest["packageName"]] == (
        f"file:vendor/html-to-arkui/{manifest['archive']}"
    )
    assert dependency["version"] == manifest["packageVersion"]
    assert dependency["resolved"] == f"file:vendor/html-to-arkui/{manifest['archive']}"
    assert dependency["integrity"] == manifest["npmIntegrity"]
    assert set(dependency["bundleDependencies"]) == {"css-tree", "parse5"}


def test_installed_contract_is_identical_to_archive_and_pinned_copy() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    archive = VENDOR_ROOT / manifest["archive"]
    installed = (
        PROJECT_ROOT
        / "node_modules/@local/html-to-arkui/contracts/arkui-component-registry.json"
    )
    pinned = PROJECT_ROOT / "uibench/arkui/renderer_contract.json"

    assert installed.is_file(), (
        "vendored html-to-arkui runtime is missing; run "
        "npm ci --ignore-scripts --offline"
    )
    with tarfile.open(archive, mode="r:gz") as package:
        contract_file = package.extractfile(
            "package/contracts/arkui-component-registry.json"
        )
        assert contract_file is not None
        archive_contract = contract_file.read()

    assert installed.read_bytes() == archive_contract
    assert json.loads(pinned.read_text(encoding="utf-8")) == json.loads(archive_contract)

    installed_schema = (
        PROJECT_ROOT
        / "node_modules/@local/html-to-arkui/contracts/screen-ir.schema.json"
    )
    with tarfile.open(archive, mode="r:gz") as package:
        schema_file = package.extractfile(
            "package/contracts/screen-ir.schema.json"
        )
        assert schema_file is not None
        archive_schema = schema_file.read()
    assert installed_schema.read_bytes() == archive_schema


def _load_vendor_tool():
    spec = importlib.util.spec_from_file_location(
        "vendor_html_to_arkui",
        PROJECT_ROOT / "tools/vendor-html-to-arkui.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _minimal_archive(tmp_path: Path, *, with_runtime: bool) -> Path:
    archive = tmp_path / "local-html-to-arkui-9.9.9.tgz"
    members: dict[str, bytes] = {
        "package/package.json": json.dumps({
            "name": "@local/html-to-arkui",
            "version": "9.9.9",
        }).encode("utf-8"),
        "package/contracts/arkui-component-registry.json": b"{}",
    }
    if with_runtime:
        members["package/dist/index.js"] = b"export {};\n"
    with tarfile.open(archive, mode="w:gz") as package:
        for name, content in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(content)
            package.addfile(info, io.BytesIO(content))
    return archive


def test_vendor_tool_refuses_archives_without_the_compiled_runtime(
    tmp_path: Path,
) -> None:
    """The pre-flight guard rejects a runtime-less pack before it pins anything.

    A pack that raced its own prepack build installs cleanly and only fails
    once the bridge tries to load dist/index.js; the vendoring tool must
    refuse such an archive up front instead of updating all four artifacts.
    """
    tool = _load_vendor_tool()

    with pytest.raises(SystemExit, match="dist/index.js"):
        tool._archive_facts(_minimal_archive(tmp_path, with_runtime=False))

    facts = tool._archive_facts(_minimal_archive(tmp_path, with_runtime=True))
    assert facts["version"] == "9.9.9"
    assert facts["bundled"] == []
