#!/usr/bin/env python3
"""Extract the HM Symbol preview font and freeze its name-to-codepoint table.

The DevEco previewer renders ``SymbolGlyph`` with ``HMSymbolVF.ttf``, whose
``post`` table names every glyph with the same canonical resource names the
symbol registry uses. This tool copies that font into a git-ignored local
asset directory (the font itself is never committed or redistributed) and
freezes the name-to-codepoint join into a checked-in JSON so the browser can
render the exact device glyphs.

Run once per SDK install/upgrade::

    python tools/export-hm-symbol-assets.py
"""
from __future__ import annotations

import argparse
import json
import os
import struct
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from uibench.arkui.symbols import (  # noqa: E402
    HM_SYMBOL_CODEPOINTS_FILE,
    HM_SYMBOL_CODEPOINTS_VERSION,
    HM_SYMBOL_FONT_FILE,
    load_symbol_registry,
)

DEFAULT_DEVECO_STUDIO = Path("/Applications/DevEco-Studio.app")
FONTS_DIR = Path("Contents/sdk/default/openharmony/previewer/common/bin/fonts")
FONT_FILE = FONTS_DIR / "HMSymbolVF.ttf"
# The text faces the generated pages declare (`--dt-font-family`); serving
# them locally makes browser text metrics match the device, weights included
# (both are variable fonts with a wght axis).
TEXT_FONT_FILES = ("HarmonyOS_Sans_SC.ttf", "HarmonyOS_Sans.ttf")
SDK_PACKAGE = Path("Contents/sdk/default/sdk-pkg.json")
_NAME_ID_VERSION = 5
# A few registry names coincide with TrueType's standard Macintosh glyph
# names, so the post table stores them as bare indices instead of custom
# strings. Only the indices verified against Apple's normative 258-name list
# are translated; anything else keeps an explicit placeholder.
_STANDARD_INDEX_NAMES: dict[int, str] = {
    3: "space",
    14: "plus",
    35: "at",
    72: "e",
    221: "ring",
    239: "minus",
    240: "multiply",
}


def _to_woff2(font_bytes: bytes) -> bytes:
    """Repackage one font as woff2 without touching glyphs or variation axes."""
    from io import BytesIO

    from fontTools.ttLib import TTFont

    font = TTFont(BytesIO(font_bytes))
    font.flavor = "woff2"
    buffer = BytesIO()
    font.save(buffer)
    return buffer.getvalue()


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
        os.chmod(temporary, 0o644)
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def _sfnt_tables(data: bytes) -> dict[str, tuple[int, int]]:
    if len(data) < 12:
        raise ValueError("font file is too small to contain an sfnt directory")
    num_tables = struct.unpack(">H", data[4:6])[0]
    tables: dict[str, tuple[int, int]] = {}
    for index in range(num_tables):
        offset = 12 + index * 16
        tag = data[offset:offset + 4].decode("ascii", "replace")
        table_offset, length = struct.unpack(">II", data[offset + 8:offset + 16])
        tables[tag] = (table_offset, length)
    return tables


def _glyph_names(data: bytes, tables: dict[str, tuple[int, int]]) -> list[str]:
    """Read glyph names from a version 2.0 ``post`` table."""
    if "post" not in tables:
        raise ValueError("font has no post table")
    offset, length = tables["post"]
    version = struct.unpack(">I", data[offset:offset + 4])[0]
    if version != 0x00020000:
        raise ValueError(
            f"post table version 0x{version:08X} carries no glyph names; "
            "the extraction rule needs to be revisited"
        )
    num_glyphs = struct.unpack(">H", data[offset + 32:offset + 34])[0]
    index_offset = offset + 34
    indices = struct.unpack(
        f">{num_glyphs}H", data[index_offset:index_offset + num_glyphs * 2]
    )
    pool: list[str] = []
    position = index_offset + num_glyphs * 2
    end = offset + length
    while position < end:
        name_length = data[position]
        pool.append(
            data[position + 1:position + 1 + name_length].decode("latin1")
        )
        position += 1 + name_length
    names: list[str] = []
    for index in indices:
        if index >= 258:
            names.append(pool[index - 258])
        else:
            names.append(
                _STANDARD_INDEX_NAMES.get(index, f"<macintosh-{index}>")
            )
    return names


def _cmap_format12(
    data: bytes, tables: dict[str, tuple[int, int]],
) -> tuple[dict[int, int], dict[int, int]]:
    """Read a format 12 ``cmap`` subtable in both directions."""
    if "cmap" not in tables:
        raise ValueError("font has no cmap table")
    cmap_offset, _ = tables["cmap"]
    subtable_count = struct.unpack(">H", data[cmap_offset + 2:cmap_offset + 4])[0]
    format12_offset: int | None = None
    for index in range(subtable_count):
        record = cmap_offset + 4 + index * 8
        _, _, sub_offset = struct.unpack(">HHI", data[record:record + 8])
        table_format = struct.unpack(
            ">H", data[cmap_offset + sub_offset:cmap_offset + sub_offset + 2]
        )[0]
        if table_format == 12:
            format12_offset = cmap_offset + sub_offset
            break
    if format12_offset is None:
        raise ValueError("font has no format 12 cmap subtable")
    group_count = struct.unpack(
        ">I", data[format12_offset + 12:format12_offset + 16]
    )[0]
    by_glyph: dict[int, int] = {}
    by_codepoint: dict[int, int] = {}
    for group in range(group_count):
        record = format12_offset + 16 + group * 12
        start, end, glyph_start = struct.unpack(">III", data[record:record + 12])
        for codepoint in range(start, end + 1):
            glyph = glyph_start + (codepoint - start)
            by_codepoint[codepoint] = glyph
            # Prefer the first (lowest) codepoint when a glyph is multi-mapped.
            by_glyph.setdefault(glyph, codepoint)
    return by_glyph, by_codepoint


def _font_version(data: bytes, tables: dict[str, tuple[int, int]]) -> str:
    if "name" not in tables:
        return "unknown"
    offset, _ = tables["name"]
    count, string_offset = struct.unpack(">HH", data[offset + 2:offset + 6])
    for index in range(count):
        record = offset + 6 + index * 12
        platform, encoding, _, name_id, length, name_offset = struct.unpack(
            ">HHHHHH", data[record:record + 12]
        )
        if name_id != _NAME_ID_VERSION:
            continue
        raw = data[
            offset + string_offset + name_offset:
            offset + string_offset + name_offset + length
        ]
        if platform == 3 or (platform == 0):
            return raw.decode("utf-16-be", "replace")
        return raw.decode("latin1", "replace")
    return "unknown"


def _sdk_provenance(studio: Path) -> dict[str, object]:
    package_file = studio / SDK_PACKAGE
    if not package_file.is_file():
        return {}
    with package_file.open("r", encoding="utf-8") as stream:
        package = json.load(stream)
    data = package.get("data") if isinstance(package, dict) else None
    if not isinstance(data, dict):
        return {}
    return {
        "displayName": str(data.get("displayName") or "unknown"),
        "apiVersion": int(str(data.get("apiVersion") or "0")),
        "sdkVersion": str(data.get("version") or "unknown"),
    }


def export_hm_symbol_assets(
    studio: Path = DEFAULT_DEVECO_STUDIO,
    font_output: Path = HM_SYMBOL_FONT_FILE,
    output: Path = HM_SYMBOL_CODEPOINTS_FILE,
) -> dict[str, object]:
    studio = studio.resolve()
    font_source = studio / FONT_FILE
    if not font_source.is_file():
        raise FileNotFoundError(f"HM Symbol font not found at {font_source}")
    data = font_source.read_bytes()
    tables = _sfnt_tables(data)
    glyph_names = _glyph_names(data, tables)
    codepoint_by_glyph, _ = _cmap_format12(data, tables)
    named_codepoints: dict[str, int] = {}
    for glyph_id, name in enumerate(glyph_names):
        codepoint = codepoint_by_glyph.get(glyph_id)
        if codepoint is None or name.startswith("<"):
            continue
        named_codepoints.setdefault(name, codepoint)

    registry = load_symbol_registry()
    codepoints: dict[str, int] = {}
    missing: list[str] = []
    for name in sorted(registry.symbols):
        codepoint = named_codepoints.get(name)
        if codepoint is None:
            missing.append(name)
        else:
            codepoints[name] = codepoint

    # Legacy aliases and typo entries in id_defined.json have no previewer
    # glyph at all; they are recorded rather than fatal. Names the reviewed
    # mapping tables actually target must be renderable, however, or the
    # browser could not mirror the export.
    targets = set(registry.lucide_symbol_map.values()) | set(
        registry.lucide_symbol_near_map.values()
    )
    unrenderable = sorted(targets - set(codepoints))
    if unrenderable:
        raise ValueError(
            "font cannot render reviewed mapping targets: "
            + ", ".join(unrenderable[:5])
        )

    document = {
        "kind": "uibench-hm-symbol-codepoints",
        "registryVersion": HM_SYMBOL_CODEPOINTS_VERSION,
        "source": {
            **_sdk_provenance(studio),
            "font": FONT_FILE.name,
            "fontVersion": _font_version(data, tables),
            "file": FONT_FILE.as_posix(),
        },
        "missingFromFont": missing,
        "codepoints": codepoints,
    }
    _atomic_write(
        output,
        (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
    )
    # The fonts themselves stay out of git: they are the developer's local
    # SDK assets, repackaged next to the code purely so the web app can serve
    # them. Only variable woff2 is kept (same glyphs and weight axis as the
    # SDK TTF sources at roughly half the bytes); stale TTF copies from
    # earlier extractions are removed.
    _atomic_write(font_output, _to_woff2(data))
    font_output.with_suffix(".ttf").unlink(missing_ok=True)
    text_fonts: list[str] = []
    for filename in TEXT_FONT_FILES:
        source_file = studio / FONTS_DIR / filename
        if not source_file.is_file():
            raise FileNotFoundError(
                f"HarmonyOS text font not found at {source_file}"
            )
        woff2_name = Path(filename).with_suffix(".woff2").name
        _atomic_write(
            font_output.parent / woff2_name, _to_woff2(source_file.read_bytes())
        )
        (font_output.parent / filename).unlink(missing_ok=True)
        text_fonts.append(woff2_name)
    return {
        "ok": True,
        "font": str(font_output),
        "fontBytes": font_output.stat().st_size,
        "textFonts": text_fonts,
        "output": str(output),
        "codepoints": len(codepoints),
        "source": document["source"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Copy the DevEco previewer's HM Symbol font into a git-ignored "
            "local asset and freeze its name-to-codepoint table so browsers "
            "can render device-identical glyphs."
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
        "--font-out",
        default=HM_SYMBOL_FONT_FILE,
        type=Path,
        metavar="FILE",
        help="git-ignored font destination (default: %(default)s)",
    )
    parser.add_argument(
        "--out",
        default=HM_SYMBOL_CODEPOINTS_FILE,
        type=Path,
        metavar="FILE",
        help="codepoint registry to write (default: %(default)s)",
    )
    args = parser.parse_args()
    result = export_hm_symbol_assets(args.deveco_studio, args.font_out, args.out)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
