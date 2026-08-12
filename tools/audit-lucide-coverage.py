#!/usr/bin/env python3
"""Audit how much of the pinned Lucide catalogue maps onto HarmonyOS symbols.

Read-only: loads the two frozen registries, classifies every icon and alias
through the real resolution path, and prints a summary. ``--out`` writes the
full JSON report (including per-name status and resolver suggestions), which
is the working document for extending ``lucideSymbolMap`` by hand.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.lucide_coverage import (  # noqa: E402
    build_coverage_report,
    format_summary,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Classify every pinned Lucide icon and alias as reviewed, direct, "
            "miss-suggested, or miss-none against the HarmonyOS registry."
        ),
    )
    parser.add_argument(
        "--out",
        type=Path,
        metavar="FILE",
        help="write the full JSON report to this file",
    )
    args = parser.parse_args()
    report = build_coverage_report()
    print(format_summary(report))
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"report written to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
