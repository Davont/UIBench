"""Resolve ``data-symbol`` against the frozen HarmonyOS symbol registry.

``SymbolGlyph`` only renders system-preset symbol resources: an invented name
passes any syntax check but renders as a broken glyph on device. Validation
therefore resolves every annotation against the names frozen out of a real SDK
by ``tools/export-symbol-registry.py``.
"""
from __future__ import annotations

import difflib
import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Literal

SYMBOL_REGISTRY_FILE = Path(__file__).with_name("symbol_registry.json")
SYMBOL_REGISTRY_VERSION = 1
LUCIDE_REGISTRY_FILE = Path(__file__).with_name("lucide_registry.json")
LUCIDE_REGISTRY_VERSION = 1
SYSTEM_SYMBOL_PREFIX = "sys.symbol."
APP_SYMBOL_PREFIX = "app.symbol."
MAX_SYMBOL_SUGGESTIONS = 3

SymbolStatus = Literal["supported", "unknown", "unsupported-scope", "malformed"]

# Model output routinely arrives in Lucide's kebab-case or in SF Symbols' dotted
# style. Both are unambiguous spellings of the same underscore resource name.
_SEPARATOR_RE = re.compile(r"[-.]+")
_CANONICAL_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_]*$")
LUCIDE_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class SymbolRegistryError(RuntimeError):
    """Raised when the frozen symbol registry is missing or inconsistent."""


class LucideRegistryError(RuntimeError):
    """Raised when the frozen Lucide icon registry is missing or inconsistent."""


@dataclass(frozen=True)
class SymbolRegistry:
    registry_version: int
    source: dict[str, object]
    symbols: frozenset[str]
    lucide_symbol_map: dict[str, str]
    lucide_symbol_near_map: dict[str, str]
    _by_lowercase: dict[str, str]

    def resolve_name(self, name: str) -> str | None:
        """Return the canonical SDK spelling of a bare symbol name."""
        if name in self.symbols:
            return name
        return self._by_lowercase.get(name.lower())

    def suggest(self, name: str) -> tuple[str, ...]:
        lucide_match = self.lucide_symbol_map.get(name.lower().replace("_", "-"))
        matches = difflib.get_close_matches(
            name.lower(),
            self._by_lowercase,
            n=MAX_SYMBOL_SUGGESTIONS,
            cutoff=0.72,
        )
        ordered = ([lucide_match] if lucide_match else []) + [
            self._by_lowercase[match] for match in matches
        ]
        return tuple(dict.fromkeys(ordered))[:MAX_SYMBOL_SUGGESTIONS]


@dataclass(frozen=True)
class SymbolResolution:
    status: SymbolStatus
    canonical: str | None = None
    suggestions: tuple[str, ...] = ()
    # An approximate resolution renders a real glyph that is only visually
    # similar to the requested icon; exports must report it as lossy.
    approximate: bool = False

    @property
    def supported(self) -> bool:
        return self.status == "supported"


def normalize_symbol_name(name: str) -> str:
    """Fold Lucide and SF Symbols separators into HarmonyOS underscore form."""
    return _SEPARATOR_RE.sub("_", name.strip())


_LUCIDE_PART_RE = re.compile(r"[-_\s]+")


def lucide_pascal_name(name: str) -> str:
    """Fold a ``data-lucide`` value the way the Lucide CDN build looks it up.

    The browser resolves the attribute through ``toPascalCase`` and reads the
    icon off one PascalCase key, so PascalCase is the only space in which two
    spellings provably render the same glyph. ``clock-10`` and ``axis-3d``
    style names make the reverse direction ambiguous.
    """
    return "".join(
        part.capitalize()
        for part in _LUCIDE_PART_RE.split(name.strip())
        if part
    )


def parse_symbol_registry(payload: object) -> SymbolRegistry:
    """Validate one raw registry payload into the frozen registry model.

    This is the single authority on registry validity. The loader runs it on
    the checked-in file, and ``tools/export-symbol-registry.py`` runs it on a
    freshly generated payload before writing, so an SDK refresh can never
    persist a registry this parser would refuse at load time — for example a
    near-map key that a new SDK suddenly resolves by direct lookup.
    """
    if not isinstance(payload, dict):
        raise SymbolRegistryError("symbol registry must contain an object")
    if payload.get("registryVersion") != SYMBOL_REGISTRY_VERSION:
        raise SymbolRegistryError(
            "symbol registry version "
            f"{payload.get('registryVersion')!r} is not supported"
        )
    raw_symbols = payload.get("symbols")
    if not isinstance(raw_symbols, list) or not raw_symbols:
        raise SymbolRegistryError("symbol registry has no symbols array")

    symbols: set[str] = set()
    by_lowercase: dict[str, str] = {}
    for entry in raw_symbols:
        if not isinstance(entry, str) or not _CANONICAL_NAME_RE.fullmatch(entry):
            raise SymbolRegistryError(f"invalid symbol name: {entry!r}")
        symbols.add(entry)
        lowered = entry.lower()
        collision = by_lowercase.get(lowered)
        if collision is not None:
            # Case-insensitive recovery is only safe while it stays unambiguous.
            raise SymbolRegistryError(
                f"symbol names {collision!r} and {entry!r} differ only by case"
            )
        by_lowercase[lowered] = entry

    raw_map = payload.get("lucideSymbolMap")
    if not isinstance(raw_map, dict):
        raise SymbolRegistryError("symbol registry has no lucideSymbolMap object")
    lucide_symbol_map: dict[str, str] = {}
    for lucide_name, symbol_name in sorted(raw_map.items()):
        if not isinstance(lucide_name, str) or not isinstance(symbol_name, str):
            raise SymbolRegistryError("lucideSymbolMap entries must be strings")
        if symbol_name not in symbols:
            raise SymbolRegistryError(
                f"lucideSymbolMap maps {lucide_name!r} to {symbol_name!r}, "
                "which this SDK does not define"
            )
        lucide_symbol_map[lucide_name] = symbol_name

    # The near map holds visually similar substitutes for icons the SDK has
    # no exact counterpart for. An entry that the exact tiers already resolve
    # would never be consulted, so its presence can only be a curation error.
    raw_near = payload.get("lucideSymbolNearMap", {})
    if not isinstance(raw_near, dict):
        raise SymbolRegistryError(
            "symbol registry lucideSymbolNearMap must be an object"
        )
    lucide_symbol_near_map: dict[str, str] = {}
    for lucide_name, symbol_name in sorted(raw_near.items()):
        if not isinstance(lucide_name, str) or not isinstance(symbol_name, str):
            raise SymbolRegistryError("lucideSymbolNearMap entries must be strings")
        if symbol_name not in symbols:
            raise SymbolRegistryError(
                f"lucideSymbolNearMap maps {lucide_name!r} to {symbol_name!r}, "
                "which this SDK does not define"
            )
        if lucide_name in lucide_symbol_map:
            raise SymbolRegistryError(
                f"lucideSymbolNearMap entry {lucide_name!r} is shadowed by "
                "an exact lucideSymbolMap entry"
            )
        normalized = _SEPARATOR_RE.sub("_", lucide_name.strip())
        if normalized in symbols or by_lowercase.get(normalized.lower()):
            raise SymbolRegistryError(
                f"lucideSymbolNearMap entry {lucide_name!r} resolves exactly "
                "by direct lookup and does not belong in the near map"
            )
        lucide_symbol_near_map[lucide_name] = symbol_name

    source = payload.get("source")
    return SymbolRegistry(
        registry_version=SYMBOL_REGISTRY_VERSION,
        source=source if isinstance(source, dict) else {},
        symbols=frozenset(symbols),
        lucide_symbol_map=lucide_symbol_map,
        lucide_symbol_near_map=lucide_symbol_near_map,
        _by_lowercase=by_lowercase,
    )


@lru_cache(maxsize=1)
def load_symbol_registry() -> SymbolRegistry:
    """Load and validate the frozen registry once per process."""
    if not SYMBOL_REGISTRY_FILE.is_file():
        raise SymbolRegistryError(
            f"symbol registry not found at {SYMBOL_REGISTRY_FILE}; run "
            "tools/export-symbol-registry.py against a local DevEco SDK"
        )
    with SYMBOL_REGISTRY_FILE.open("r", encoding="utf-8") as stream:
        payload = json.load(stream)
    return parse_symbol_registry(payload)


@dataclass(frozen=True)
class LucideRegistry:
    """Frozen catalogue of the Lucide icon names one pinned version renders.

    The CDN build resolves ``data-lucide`` through ``toPascalCase``, so both
    canonical icon names and their deprecated aliases are renderable spellings.
    This registry powers validation and coverage audits only; runtime symbol
    resolution keeps consulting the HarmonyOS registry alone.
    """

    registry_version: int
    source: dict[str, object]
    icons: frozenset[str]
    aliases: dict[str, str]
    _pascal_names: frozenset[str]

    @property
    def version(self) -> str:
        return str(self.source.get("version") or "unknown")

    def is_known(self, name: str) -> bool:
        """Whether the pinned CDN build would render this ``data-lucide``."""
        candidate = name.strip()
        if not candidate:
            return False
        return lucide_pascal_name(candidate) in self._pascal_names


@lru_cache(maxsize=1)
def load_lucide_registry() -> LucideRegistry:
    """Load and validate the frozen Lucide icon catalogue once per process."""
    if not LUCIDE_REGISTRY_FILE.is_file():
        raise LucideRegistryError(
            f"lucide registry not found at {LUCIDE_REGISTRY_FILE}; run "
            "tools/export-lucide-registry.py against a downloaded lucide package"
        )
    with LUCIDE_REGISTRY_FILE.open("r", encoding="utf-8") as stream:
        payload = json.load(stream)
    if not isinstance(payload, dict):
        raise LucideRegistryError("lucide registry must contain an object")
    if payload.get("registryVersion") != LUCIDE_REGISTRY_VERSION:
        raise LucideRegistryError(
            "lucide registry version "
            f"{payload.get('registryVersion')!r} is not supported"
        )
    raw_icons = payload.get("icons")
    if not isinstance(raw_icons, list) or not raw_icons:
        raise LucideRegistryError("lucide registry has no icons array")
    icons: set[str] = set()
    for entry in raw_icons:
        if not isinstance(entry, str) or not LUCIDE_NAME_RE.fullmatch(entry):
            raise LucideRegistryError(f"invalid lucide icon name: {entry!r}")
        if entry in icons:
            raise LucideRegistryError(f"duplicate lucide icon name: {entry!r}")
        icons.add(entry)

    raw_aliases = payload.get("aliases")
    if not isinstance(raw_aliases, dict):
        raise LucideRegistryError("lucide registry has no aliases object")
    aliases: dict[str, str] = {}
    for alias, canonical in sorted(raw_aliases.items()):
        if not isinstance(alias, str) or not isinstance(canonical, str):
            raise LucideRegistryError("lucide aliases entries must be strings")
        if not LUCIDE_NAME_RE.fullmatch(alias):
            raise LucideRegistryError(f"invalid lucide alias name: {alias!r}")
        if alias in icons:
            raise LucideRegistryError(
                f"lucide alias {alias!r} collides with a canonical icon name"
            )
        if canonical not in icons:
            raise LucideRegistryError(
                f"lucide alias {alias!r} points to {canonical!r}, "
                "which this catalogue does not define"
            )
        aliases[alias] = canonical

    # The browser reads icons off PascalCase keys, so every registered
    # spelling must occupy its own key there; a collision would make two
    # entries indistinguishable at render time.
    pascal_names = [
        lucide_pascal_name(name) for name in (*icons, *aliases)
    ]
    if len(set(pascal_names)) != len(pascal_names):
        duplicates = sorted({
            name for name in pascal_names if pascal_names.count(name) > 1
        })
        raise LucideRegistryError(
            "lucide names collide in PascalCase lookup space: "
            + ", ".join(duplicates[:5])
        )

    source = payload.get("source")
    return LucideRegistry(
        registry_version=LUCIDE_REGISTRY_VERSION,
        source=source if isinstance(source, dict) else {},
        icons=frozenset(icons),
        aliases=aliases,
        _pascal_names=frozenset(pascal_names),
    )


def is_known_lucide_icon(name: str) -> bool:
    """Whether the pinned Lucide build can render this ``data-lucide`` value."""
    return load_lucide_registry().is_known(name)


def pinned_lucide_version() -> str:
    """Return the Lucide package version the frozen catalogue was built from."""
    return load_lucide_registry().version


def resolve_symbol(value: str) -> SymbolResolution:
    """Resolve one ``data-symbol`` annotation to a renderable resource name."""
    candidate = value.strip()
    if candidate.startswith(APP_SYMBOL_PREFIX):
        # Exported projects only materialize media resources, so an app-scoped
        # symbol always references a file the bundle does not contain.
        registry = load_symbol_registry()
        bare = normalize_symbol_name(candidate[len(APP_SYMBOL_PREFIX):])
        resolved = registry.resolve_name(bare)
        return SymbolResolution(
            status="unsupported-scope",
            suggestions=(
                (f"{SYSTEM_SYMBOL_PREFIX}{resolved}",) if resolved
                else tuple(
                    f"{SYSTEM_SYMBOL_PREFIX}{name}"
                    for name in registry.suggest(bare)
                )
            ),
        )
    if not candidate.startswith(SYSTEM_SYMBOL_PREFIX):
        return SymbolResolution(status="malformed")

    bare = normalize_symbol_name(candidate[len(SYSTEM_SYMBOL_PREFIX):])
    if not _CANONICAL_NAME_RE.fullmatch(bare):
        return SymbolResolution(status="malformed")

    registry = load_symbol_registry()
    resolved = registry.resolve_name(bare)
    if resolved is None:
        return SymbolResolution(
            status="unknown",
            suggestions=tuple(
                f"{SYSTEM_SYMBOL_PREFIX}{name}"
                for name in registry.suggest(bare)
            ),
        )
    return SymbolResolution(
        status="supported",
        canonical=f"{SYSTEM_SYMBOL_PREFIX}{resolved}",
    )


def resolve_lucide_icon_near(lucide_name: str) -> SymbolResolution:
    """Substitute the closest reviewed HarmonyOS symbol for a missing icon.

    Near entries render a real glyph that is only visually similar, so this
    tier is consulted last — after the exact tiers and after an explicitly
    declared ``data-symbol`` — and every hit is flagged ``approximate`` so
    the export stays honest about the visual difference.
    """
    name = lucide_name.strip().lower()
    if not name:
        return SymbolResolution(status="malformed")
    substitute = load_symbol_registry().lucide_symbol_near_map.get(name)
    if substitute is None:
        return SymbolResolution(status="unknown")
    return SymbolResolution(
        status="supported",
        canonical=f"{SYSTEM_SYMBOL_PREFIX}{substitute}",
        approximate=True,
    )


def resolve_lucide_icon(lucide_name: str) -> SymbolResolution:
    """Map a Lucide icon name onto a HarmonyOS system symbol.

    The model already has to write ``data-lucide`` for the page to render, and
    that name is evidence rather than a guess, so it outranks any hand-written
    ``data-symbol``. Resolution is two-tier: a reviewed mapping first, then a
    direct lookup for the many icons both libraries happen to name the same.
    """
    name = lucide_name.strip().lower()
    if not name:
        return SymbolResolution(status="malformed")
    registry = load_symbol_registry()
    reviewed = registry.lucide_symbol_map.get(name)
    if reviewed is not None:
        return SymbolResolution(
            status="supported",
            canonical=f"{SYSTEM_SYMBOL_PREFIX}{reviewed}",
        )
    direct = registry.resolve_name(normalize_symbol_name(name))
    if direct is not None:
        return SymbolResolution(
            status="supported",
            canonical=f"{SYSTEM_SYMBOL_PREFIX}{direct}",
        )
    return SymbolResolution(
        status="unknown",
        suggestions=tuple(
            f"{SYSTEM_SYMBOL_PREFIX}{candidate}"
            for candidate in registry.suggest(normalize_symbol_name(name))
        ),
    )


def canonical_symbol(value: str) -> str:
    """Return the canonical resource name, or the input when unresolvable."""
    resolution = resolve_symbol(value)
    return resolution.canonical or value.strip()


def lucide_symbol_table() -> dict[str, str]:
    """Return the reviewed Lucide icon name to system symbol mapping."""
    return dict(load_symbol_registry().lucide_symbol_map)


def lucide_symbol_near_table() -> dict[str, str]:
    """Return the reviewed approximate Lucide icon substitutions."""
    return dict(load_symbol_registry().lucide_symbol_near_map)


def format_lucide_symbol_table(*, indent: str = "  ", width: int = 78) -> str:
    """Render the mapping as compact prompt lines."""
    entries = [
        f"{lucide}={symbol}"
        for lucide, symbol in sorted(lucide_symbol_table().items())
    ]
    lines: list[str] = []
    current = indent
    for entry in entries:
        candidate = entry if current == indent else f"{current}  {entry}"
        if current != indent and len(candidate) > width:
            lines.append(current)
            current = indent + entry
            continue
        current = candidate if current != indent else indent + entry
    if current != indent:
        lines.append(current)
    return "\n".join(lines)


__all__ = [
    "APP_SYMBOL_PREFIX",
    "LUCIDE_NAME_RE",
    "LUCIDE_REGISTRY_FILE",
    "LUCIDE_REGISTRY_VERSION",
    "LucideRegistry",
    "LucideRegistryError",
    "MAX_SYMBOL_SUGGESTIONS",
    "SYMBOL_REGISTRY_FILE",
    "SYMBOL_REGISTRY_VERSION",
    "SYSTEM_SYMBOL_PREFIX",
    "SymbolRegistry",
    "SymbolRegistryError",
    "SymbolResolution",
    "SymbolStatus",
    "canonical_symbol",
    "format_lucide_symbol_table",
    "is_known_lucide_icon",
    "load_lucide_registry",
    "load_symbol_registry",
    "lucide_pascal_name",
    "lucide_symbol_near_table",
    "lucide_symbol_table",
    "normalize_symbol_name",
    "parse_symbol_registry",
    "pinned_lucide_version",
    "resolve_lucide_icon",
    "resolve_lucide_icon_near",
    "resolve_symbol",
]
