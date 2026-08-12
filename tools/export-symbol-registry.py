#!/usr/bin/env python3
"""Freeze the HarmonyOS system symbol names from a local DevEco SDK.

``SymbolGlyph`` only renders system-preset symbol resources, so UIBench cannot
validate ``data-symbol`` with a syntax pattern alone. This tool copies the
authoritative names out of the SDK's ``id_defined.json`` so validation, prompts
and tests work on machines without DevEco Studio installed.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from uibench.arkui.symbols import (  # noqa: E402
    SYMBOL_REGISTRY_FILE,
    SYMBOL_REGISTRY_VERSION,
    normalize_symbol_name,
    parse_symbol_registry,
)

DEFAULT_DEVECO_STUDIO = Path("/Applications/DevEco-Studio.app")
SDK_ID_TABLE = Path("Contents/sdk/default/openharmony/toolchains/id_defined.json")
SDK_PACKAGE = Path("Contents/sdk/default/sdk-pkg.json")


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        # mkstemp is 0600; the registry is checked in and read like any source.
        os.chmod(temporary, 0o644)
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def _read_json(path: Path) -> object:
    if not path.is_file():
        raise FileNotFoundError(f"required SDK file is missing: {path}")
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def _sdk_provenance(studio: Path) -> dict[str, object]:
    package = _read_json(studio / SDK_PACKAGE)
    if not isinstance(package, dict):
        raise ValueError("sdk-pkg.json must contain an object")
    data = package.get("data")
    if not isinstance(data, dict):
        raise ValueError("sdk-pkg.json has no data object")
    return {
        "displayName": str(data.get("displayName") or "unknown"),
        "apiVersion": int(str(data.get("apiVersion") or "0")),
        "sdkVersion": str(data.get("version") or "unknown"),
        "releaseType": str(data.get("releaseType") or "unknown"),
        "file": SDK_ID_TABLE.as_posix(),
    }


def _extract_symbols(studio: Path) -> tuple[str, ...]:
    table = _read_json(studio / SDK_ID_TABLE)
    if not isinstance(table, dict):
        raise ValueError("id_defined.json must contain an object")
    records = table.get("record")
    if not isinstance(records, list):
        raise ValueError("id_defined.json has no record array")
    names: set[str] = set()
    for record in records:
        if not isinstance(record, dict) or record.get("type") != "symbol":
            continue
        name = str(record.get("name") or "").strip()
        if not name:
            continue
        if normalize_symbol_name(name) != name:
            raise ValueError(
                f"SDK symbol {name!r} is not in canonical underscore form; "
                "the normalization rule needs to be revisited"
            )
        names.add(name)
    if not names:
        raise ValueError("id_defined.json contained no symbol records")
    return tuple(sorted(names))


def _existing_curated_map(path: Path, map_name: str) -> dict[str, str]:
    """Preserve a hand-maintained mapping across SDK refreshes."""
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8") as stream:
        current = json.load(stream)
    mapping = current.get(map_name) if isinstance(current, dict) else None
    if not isinstance(mapping, dict):
        return {}
    return {str(key): str(value) for key, value in mapping.items()}


def export_symbol_registry(
    studio: Path = DEFAULT_DEVECO_STUDIO,
    output: Path = SYMBOL_REGISTRY_FILE,
) -> dict[str, object]:
    studio = studio.resolve()
    if not studio.is_dir():
        raise NotADirectoryError(f"DevEco Studio not found at {studio}")
    symbols = _extract_symbols(studio)
    # Both curated maps survive an SDK refresh; whether they still fit the
    # freshly extracted symbol table is decided below by the runtime parser.
    lucide_map = _existing_curated_map(output, "lucideSymbolMap")
    near_map = _existing_curated_map(output, "lucideSymbolNearMap")
    registry = {
        "kind": "uibench-harmony-symbol-registry",
        "registryVersion": SYMBOL_REGISTRY_VERSION,
        "source": _sdk_provenance(studio),
        "lucideSymbolMap": dict(sorted(lucide_map.items())),
        "lucideSymbolNearMap": dict(sorted(near_map.items())),
        "symbols": list(symbols),
    }
    # The runtime loader is the single authority on registry validity, so run
    # its parser on the generated payload before persisting anything. This
    # refuses here whatever load_symbol_registry() would refuse at import
    # time — a curated value the new SDK dropped, a near-map key the new SDK
    # now resolves directly (e.g. it gained a "globe" symbol), case-colliding
    # symbol names — instead of writing a registry that can never load.
    parse_symbol_registry(registry)
    _atomic_write(
        output,
        (json.dumps(registry, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
    )
    return {
        "ok": True,
        "output": str(output),
        "symbols": len(symbols),
        "lucideSymbolMap": len(lucide_map),
        "lucideSymbolNearMap": len(near_map),
        "source": registry["source"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Freeze HarmonyOS system symbol names from a local DevEco SDK into "
            "the repository so ArkUI export can validate data-symbol offline."
        ),
    )
    parser.add_argument(
        "--deveco-studio",
        default=DEFAULT_DEVECO_STUDIO,
        type=Path,
        metavar="DIR",
        help="DevEco Studio .app root (default: %(default)s)",
    )
    parser.add_argument(
        "--out",
        default=SYMBOL_REGISTRY_FILE,
        type=Path,
        metavar="FILE",
        help="registry file to write (default: %(default)s)",
    )
    args = parser.parse_args()
    result = export_symbol_registry(args.deveco_studio, args.out)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
