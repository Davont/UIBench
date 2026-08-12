"""Classify how the frozen Lucide catalogue maps onto HarmonyOS symbols.

Importable core of ``tools/audit-lucide-coverage.py``. Each name is pushed
through the same two-tier resolution the export uses, so the report describes
exactly what a generated page would experience:

- ``reviewed``: hit through the hand-checked ``lucideSymbolMap``.
- ``direct``: hit by same-name lookup against the SDK symbol list.
- ``near``: rendered through the reviewed approximate substitute map; the
  page shows a similar glyph and reports ``ARKUI_SYMBOL_APPROXIMATED``.
- ``miss-suggested``: no resource, but the resolver has close candidates worth
  a human look.
- ``miss-none``: no resource and nothing close; pages degrade to an empty
  placeholder with ``ARKUI_SYMBOL_UNAVAILABLE``.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from uibench.arkui.symbols import (  # noqa: E402
    load_lucide_registry,
    lucide_symbol_table,
    resolve_lucide_icon,
    resolve_lucide_icon_near,
)

CoverageStatus = Literal[
    "reviewed", "direct", "near", "miss-suggested", "miss-none",
]
_STATUS_ORDER: tuple[CoverageStatus, ...] = (
    "reviewed", "direct", "near", "miss-suggested", "miss-none",
)


def classify_lucide_name(name: str) -> dict[str, object]:
    """Classify one ``data-lucide`` value through the real resolution path."""
    resolution = resolve_lucide_icon(name)
    if resolution.supported:
        status: CoverageStatus = (
            "reviewed" if name.strip().lower() in lucide_symbol_table()
            else "direct"
        )
        return {
            "name": name,
            "status": status,
            "symbol": resolution.canonical,
            "suggestions": [],
        }
    near = resolve_lucide_icon_near(name)
    if near.supported:
        return {
            "name": name,
            "status": "near",
            "symbol": near.canonical,
            "suggestions": [],
        }
    status = "miss-suggested" if resolution.suggestions else "miss-none"
    return {
        "name": name,
        "status": status,
        "symbol": None,
        "suggestions": list(resolution.suggestions),
    }


def _classify_group(names: list[str]) -> dict[str, object]:
    entries = [classify_lucide_name(name) for name in names]
    counts = {
        status: sum(entry["status"] == status for entry in entries)
        for status in _STATUS_ORDER
    }
    covered = counts["reviewed"] + counts["direct"]
    return {
        "total": len(entries),
        "covered": covered,
        "coverage": round(covered / len(entries), 4) if entries else 0.0,
        "counts": counts,
        "entries": entries,
    }


def build_coverage_report() -> dict[str, object]:
    """Audit every canonical icon and alias of the pinned Lucide version."""
    registry = load_lucide_registry()
    icons = _classify_group(sorted(registry.icons))
    aliases = _classify_group(sorted(registry.aliases))
    for entry in aliases["entries"]:
        entry["aliasOf"] = registry.aliases[str(entry["name"])]
    return {
        "kind": "uibench-lucide-coverage-report",
        "lucideVersion": registry.version,
        "reviewedMappings": len(lucide_symbol_table()),
        "icons": icons,
        "aliases": aliases,
    }


def format_summary(report: dict[str, object]) -> str:
    """Render the human-readable audit summary printed by the CLI."""
    lines = [
        f"lucide {report['lucideVersion']} vs HarmonyOS symbol registry",
        f"reviewed mappings in lucideSymbolMap: {report['reviewedMappings']}",
    ]
    for group_name in ("icons", "aliases"):
        group = report[group_name]
        assert isinstance(group, dict)
        counts = group["counts"]
        lines.append(
            f"{group_name}: {group['covered']}/{group['total']} covered "
            f"({group['coverage']:.1%}) — "
            + ", ".join(f"{status} {counts[status]}" for status in _STATUS_ORDER)
        )
    return "\n".join(lines)


__all__ = [
    "CoverageStatus",
    "build_coverage_report",
    "classify_lucide_name",
    "format_summary",
]
