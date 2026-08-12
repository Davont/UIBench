#!/usr/bin/env python3
"""Pin a freshly packed html-to-arkui tarball as the vendored runtime.

The vendored package is UIBench's only renderer, so every release has to keep
four artifacts consistent: the tarball itself, ``vendor/html-to-arkui/
manifest.json``, the root npm dependency plus lockfile, and the pinned public
contract copy in ``uibench/arkui/renderer_contract.json``. This tool performs
those steps from one ``npm pack`` output so a release can never ship a
partially updated pin; ``tests/test_arkui_vendor.py`` stays the independent
auditor of the result.

The update itself is staged: every check that can fail (archive facts, npm
lockfile resolution, offline install, runtime materialization) runs before
the manifest, the pinned contract or the previous tarball are touched, and a
failure restores package.json, package-lock.json and the staged tarball, so
an aborted run leaves no partially updated working tree behind.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VENDOR_ROOT = PROJECT_ROOT / "vendor/html-to-arkui"
MANIFEST_PATH = VENDOR_ROOT / "manifest.json"
PINNED_CONTRACT_PATH = PROJECT_ROOT / "uibench/arkui/renderer_contract.json"
PACKAGE_NAME = "@local/html-to-arkui"
ARCHIVE_RE = re.compile(r"^local-html-to-arkui-\d+\.\d+\.\d+\.tgz$")


def _fail(message: str) -> "SystemExit":
    return SystemExit(f"error: {message}")


def _run(command: list[str], cwd: Path) -> str:
    result = subprocess.run(
        command, cwd=cwd, check=True, capture_output=True, text=True,
    )
    return result.stdout.strip()


def _source_commit(source_repository: Path) -> str:
    if not (source_repository / ".git").is_dir():
        raise _fail(f"{source_repository} is not a git repository")
    dirty = _run(["git", "status", "--porcelain"], source_repository)
    if dirty:
        raise _fail(
            "the html-to-arkui working tree is dirty; commit it first so the "
            "manifest can promise a reconstructable clean source commit"
        )
    return _run(["git", "rev-parse", "HEAD"], source_repository)


def _archive_facts(archive: Path) -> dict[str, object]:
    payload = archive.read_bytes()
    with tarfile.open(archive, mode="r:gz") as package:
        names = package.getnames()
        # package.json and the contracts are checked in, but dist is generated,
        # so a pack that skipped the build still yields a valid archive that
        # installs cleanly and only fails once an export asks the bridge to
        # load dist/index.js. Refuse it here rather than pin four artifacts to
        # a runtime that is not there.
        if "package/dist/index.js" not in names:
            raise _fail(
                "archive has no package/dist/index.js; run npm pack without "
                "--ignore-scripts, or npm run build before packing"
            )
        package_json_file = package.extractfile("package/package.json")
        if package_json_file is None:
            raise _fail("archive has no package/package.json")
        package_json = json.load(package_json_file)
        contract_file = package.extractfile(
            "package/contracts/arkui-component-registry.json"
        )
        if contract_file is None:
            raise _fail("archive has no contracts/arkui-component-registry.json")
        contract = contract_file.read()
    if package_json.get("name") != PACKAGE_NAME:
        raise _fail(f"archive package name is not {PACKAGE_NAME}")
    version = package_json.get("version")
    if not isinstance(version, str) or archive.name != (
        f"local-html-to-arkui-{version}.tgz"
    ):
        raise _fail("archive filename does not match the packaged version")
    bundled = sorted({
        name.split("/")[2]
        for name in names
        if name.startswith("package/node_modules/") and name.count("/") >= 3
    })
    return {
        "version": version,
        "byteLength": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "npmIntegrity": "sha512-" + base64.b64encode(
            hashlib.sha512(payload).digest()
        ).decode("ascii"),
        "bundled": bundled,
        "contract": contract,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="npm pack output (.tgz)")
    parser.add_argument(
        "--source-repository",
        type=Path,
        default=PROJECT_ROOT.parent / "html-to-arkui",
        help="html-to-arkui checkout the archive was packed from",
    )
    arguments = parser.parse_args()

    archive = arguments.archive.resolve()
    if not archive.is_file() or not ARCHIVE_RE.fullmatch(archive.name):
        raise _fail(f"{archive} is not a local-html-to-arkui-<version>.tgz file")
    facts = _archive_facts(archive)
    commit = _source_commit(arguments.source_repository.resolve())

    vendored = VENDOR_ROOT / archive.name
    if vendored.is_file() and (
        hashlib.sha256(vendored.read_bytes()).hexdigest() != facts["sha256"]
    ):
        # Refuse before touching anything: npm resolves a file: dependency by
        # version + path, so repacked bytes under an already-vendored version
        # would fight the lockfile no matter what this run writes.
        raise _fail(
            f"{vendored.name} is already vendored with different bytes; "
            "never repack an already vendored version — bump the patch "
            "version and vendor that"
        )

    # Stage and verify everything that can fail before any pinned artifact
    # changes. Only the new tarball copy and the npm files are touched here,
    # and a failure rolls those back, so an aborted run cannot leave the
    # manifest, the pinned contract and the lockfile disagreeing.
    package_json_path = PROJECT_ROOT / "package.json"
    package_lock_path = PROJECT_ROOT / "package-lock.json"
    original_package_json = package_json_path.read_text(encoding="utf-8")
    original_package_lock = package_lock_path.read_text(encoding="utf-8")
    tarball_was_vendored = vendored.is_file()
    try:
        shutil.copyfile(archive, vendored)

        package_json = json.loads(original_package_json)
        package_json["dependencies"][PACKAGE_NAME] = (
            f"file:vendor/html-to-arkui/{archive.name}"
        )
        package_json_path.write_text(
            json.dumps(package_json, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        subprocess.run(
            ["npm", "install", "--package-lock-only", "--ignore-scripts"],
            cwd=PROJECT_ROOT, check=True,
        )
        # Defence in depth behind the byte check above: the lock must pin
        # exactly the archive this run vendored before installing from it.
        lock = json.loads(package_lock_path.read_text(encoding="utf-8"))
        locked = lock["packages"][f"node_modules/{PACKAGE_NAME}"]
        if locked.get("integrity") != facts["npmIntegrity"]:
            raise _fail(
                "package-lock.json still pins different tarball bytes for "
                f"{PACKAGE_NAME}@{facts['version']}; never repack an already "
                "vendored version — bump the patch version and vendor that"
            )
        subprocess.run(
            ["npm", "ci", "--ignore-scripts", "--offline"],
            cwd=PROJECT_ROOT, check=True,
        )
        installed_runtime = (
            PROJECT_ROOT / "node_modules" / PACKAGE_NAME / "dist/index.js"
        )
        if not installed_runtime.is_file():
            raise _fail(
                f"npm ci did not materialize the vendored runtime at "
                f"{installed_runtime}"
            )
    except BaseException:
        package_json_path.write_text(original_package_json, encoding="utf-8")
        package_lock_path.write_text(original_package_lock, encoding="utf-8")
        if not tarball_was_vendored:
            vendored.unlink(missing_ok=True)
        print(
            "vendoring failed; package.json, package-lock.json and the "
            "staged tarball were restored (rerun npm ci to restore "
            "node_modules)",
            file=sys.stderr,
        )
        raise

    # Everything installable is verified; only now touch the audited pins.
    manifest = {
        "manifestVersion": 1,
        "packageName": PACKAGE_NAME,
        "packageVersion": facts["version"],
        "archive": archive.name,
        "byteLength": facts["byteLength"],
        "sha256": facts["sha256"],
        "npmIntegrity": facts["npmIntegrity"],
        "bundledRuntimeDependencies": facts["bundled"],
        "sourceCommit": commit,
        "sourceTreeState": "clean",
        "builtWith": {
            "node": _run(["node", "--version"], PROJECT_ROOT),
            "npm": _run(["npm", "--version"], PROJECT_ROOT),
        },
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    PINNED_CONTRACT_PATH.write_bytes(facts["contract"])
    for stale in VENDOR_ROOT.glob("local-html-to-arkui-*.tgz"):
        if stale.name != archive.name and ARCHIVE_RE.fullmatch(stale.name):
            stale.unlink()

    print(
        f"vendored {archive.name} (sha256 {facts['sha256'][:12]}..., "
        f"source {commit[:12]}); manifest, lockfile and pinned contract updated"
    )


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        stderr = (error.stderr or "").strip()
        raise SystemExit(
            f"error: {' '.join(map(str, error.cmd))} failed"
            + (f"\n{stderr}" if stderr else "")
        )
