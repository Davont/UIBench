#!/usr/bin/env python3
"""Build the local photo gallery from Unsplash — one-shot, offline afterwards.

Reads ``tools/gallery_topics.yaml`` (the only place categories, search terms
and match keywords are defined), searches Unsplash per category, downloads two
sizes per photo into ``assets/gallery/<category>/`` and writes
``assets/gallery/manifest.json`` — the only contract the runtime code reads.

Usage:
    python tools/build_gallery.py               # build every category
    python tools/build_gallery.py -c food       # rebuild selected categories
    python tools/build_gallery.py --dry-run     # show the plan, no network

Requires UNSPLASH_ACCESS_KEY in the project .env or the environment.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(PROJECT_ROOT / ".env")

import os  # noqa: E402

TOPICS_FILE = Path(__file__).resolve().parent / "gallery_topics.yaml"
GALLERY_DIR = PROJECT_ROOT / "assets" / "gallery"
MANIFEST_FILE = GALLERY_DIR / "manifest.json"
API_SEARCH = "https://api.unsplash.com/search/photos"

_WORD_RE = re.compile(r"[a-z0-9]+")
# Generic photo-speak that would pollute keyword matching at runtime.
_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "by", "for", "from", "his", "her",
    "in", "into", "is", "it", "its", "of", "on", "or", "over", "the", "to",
    "with", "photo", "photography", "photograph", "image", "picture",
    "stock", "background", "wallpaper", "closeup", "close", "up", "shot",
    "view", "free", "download",
}


def _tokens(text: str | None) -> set[str]:
    return {
        word for word in _WORD_RE.findall((text or "").lower())
        if len(word) >= 3 and word not in _STOPWORDS
    }


def _orientation(width: int, height: int) -> str:
    if not width or not height:
        return "squarish"
    ratio = width / height
    if ratio >= 1.2:
        return "landscape"
    if ratio <= 0.85:
        return "portrait"
    return "squarish"


def _load_topics() -> dict:
    with open(TOPICS_FILE, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data.get("categories"), dict) or not data["categories"]:
        raise SystemExit(f"no categories defined in {TOPICS_FILE}")
    return data


def _load_previous_manifest() -> dict:
    if not MANIFEST_FILE.is_file():
        return {}
    try:
        with open(MANIFEST_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh) or {}
    except (OSError, json.JSONDecodeError):
        return {}


async def _search(
    client: httpx.AsyncClient, key: str, query: str,
    orientation: str, per_page: int,
) -> list[dict]:
    params = {
        "query": query,
        "per_page": max(1, min(30, per_page)),
        "content_filter": "high",
    }
    if orientation in {"landscape", "portrait", "squarish"}:
        params["orientation"] = orientation
    response = await client.get(
        API_SEARCH,
        params=params,
        headers={"Authorization": f"Client-ID {key}", "Accept-Version": "v1"},
    )
    response.raise_for_status()
    payload = response.json()
    return payload.get("results") or []


async def _download(
    client: httpx.AsyncClient, sem: asyncio.Semaphore,
    url: str, target: Path,
) -> bool:
    if target.is_file() and target.stat().st_size > 0:
        return True
    async with sem:
        for attempt in (1, 2, 3):
            try:
                response = await client.get(url)
                response.raise_for_status()
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(response.content)
                return True
            except httpx.HTTPError as exc:
                if attempt == 3:
                    print(f"    ! download failed {target.name}: {exc}")
                    return False
                await asyncio.sleep(1.5 * attempt)
    return False


def _photo_keywords(photo: dict, search_query: str) -> list[str]:
    keywords = _tokens(search_query)
    keywords |= _tokens(photo.get("description"))
    keywords |= _tokens(photo.get("alt_description"))
    for tag in (photo.get("tags") or [])[:6]:
        if isinstance(tag, dict):
            keywords |= _tokens(tag.get("title"))
    return sorted(keywords)[:24]


async def _build_category(
    client: httpx.AsyncClient, sem: asyncio.Semaphore, key: str,
    name: str, spec: dict, candidate_factor: int, used_ids: set[str],
) -> tuple[list[dict], bool]:
    """Build one category; returns (entries, quota_exhausted).

    On an auth/rate-limit rejection the partial entries are still returned so
    the manifest keeps everything downloaded before the cutoff.
    """
    entries: list[dict] = []
    for search in spec.get("searches") or []:
        query = str(search.get("query") or "").strip()
        count = max(1, int(search.get("count", 4)))
        orientation = str(search.get("orientation") or "")
        if not query:
            continue
        try:
            results = await _search(
                client, key, query, orientation,
                per_page=max(count * max(1, candidate_factor) + 2, 24),
            )
            # Relevance alone surfaces many mediocre shots; likes are the
            # strongest free quality signal Unsplash exposes, so prefer the
            # most-liked candidates within each search.
            results = sorted(
                results, key=lambda p: -int(p.get("likes") or 0)
            )
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            print(f"    ! search '{query}' failed: HTTP {status}")
            if status in {401, 403, 429}:
                print(
                    "    ! quota or key rejected; keeping partial results. "
                    "Re-run later with -c for the missing categories."
                )
                return entries, True
            continue
        except httpx.HTTPError as exc:
            print(f"    ! search '{query}' failed: {exc}")
            continue

        picked = 0
        for photo in results:
            if picked >= count:
                break
            photo_id = str(photo.get("id") or "")
            urls = photo.get("urls") or {}
            small_url = urls.get("small")
            regular_url = urls.get("regular")
            if not photo_id or photo_id in used_ids:
                continue
            if not small_url or not regular_url:
                continue
            small_file = GALLERY_DIR / name / f"{photo_id}-small.jpg"
            regular_file = GALLERY_DIR / name / f"{photo_id}-regular.jpg"
            ok_small, ok_regular = await asyncio.gather(
                _download(client, sem, small_url, small_file),
                _download(client, sem, regular_url, regular_file),
            )
            if not (ok_small and ok_regular):
                for leftover in (small_file, regular_file):
                    leftover.unlink(missing_ok=True)
                continue
            width = int(photo.get("width") or 0)
            height = int(photo.get("height") or 0)
            regular_w = min(1080, width) if width else 1080
            regular_h = (
                round(regular_w * height / width) if width and height else 0
            )
            used_ids.add(photo_id)
            picked += 1
            entries.append({
                "id": photo_id,
                "files": {
                    "small": f"{name}/{photo_id}-small.jpg",
                    "regular": f"{name}/{photo_id}-regular.jpg",
                },
                "width": regular_w,
                "height": regular_h,
                "orientation": _orientation(regular_w, regular_h),
                "description": (
                    str(photo.get("description")
                        or photo.get("alt_description") or "")[:200]
                ),
                "keywords": _photo_keywords(photo, query),
                "photographer": str(
                    ((photo.get("user") or {}).get("name")) or ""
                )[:120],
            })
        print(f"    {query!r} -> {picked} photos")
    return entries, False


def _reuse_category(name: str, previous: dict, used_ids: set[str]) -> list[dict]:
    """Keep an already-built category when only some categories are rebuilt."""
    photos = (
        ((previous.get("categories") or {}).get(name) or {}).get("photos") or []
    )
    kept: list[dict] = []
    for photo in photos:
        files = photo.get("files") or {}
        paths = [GALLERY_DIR / str(files.get(size, "")) for size in ("small", "regular")]
        if all(path.is_file() for path in paths):
            kept.append(photo)
            used_ids.add(str(photo.get("id") or ""))
    return kept


def _cleanup_orphans(manifest: dict) -> int:
    referenced = {
        str(files.get(size))
        for category in (manifest.get("categories") or {}).values()
        for photo in category.get("photos") or []
        for size in ("small", "regular")
        if (files := photo.get("files") or {})
    }
    removed = 0
    for path in GALLERY_DIR.rglob("*.jpg"):
        if str(path.relative_to(GALLERY_DIR)).replace("\\", "/") not in referenced:
            path.unlink(missing_ok=True)
            removed += 1
    return removed


async def _main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-c", "--category", action="append", default=None,
        help="rebuild only these categories (repeatable)",
    )
    parser.add_argument(
        "--refresh-manifest", action="store_true",
        help=(
            "rewrite manifest.json from existing photos and the current "
            "gallery_topics.yaml vocabulary, without any network calls"
        ),
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    topics = _load_topics()
    categories: dict = topics["categories"]
    if args.refresh_manifest:
        selected = []
    else:
        selected = list(categories) if not args.category else args.category
    unknown = [name for name in selected if name not in categories]
    if unknown:
        raise SystemExit(f"unknown categories: {', '.join(unknown)}")

    factor = int((topics.get("options") or {}).get("candidate_factor", 2))
    planned_searches = sum(
        len(categories[name].get("searches") or []) for name in selected
    )
    planned_photos = sum(
        int(search.get("count", 4))
        for name in selected
        for search in categories[name].get("searches") or []
    )
    print(
        f"plan: {len(selected)} categories, {planned_searches} search calls, "
        f"~{planned_photos} photos -> {GALLERY_DIR}"
    )
    if args.dry_run:
        return 0

    key = os.environ.get("UNSPLASH_ACCESS_KEY") or ""
    if selected and not key:
        raise SystemExit("UNSPLASH_ACCESS_KEY is missing (.env or environment)")

    previous = _load_previous_manifest()
    used_ids: set[str] = set()
    manifest_categories: dict[str, dict] = {}

    # Keep untouched categories first so their photo ids stay reserved.
    for name, spec in categories.items():
        if name not in selected:
            kept = _reuse_category(name, previous, used_ids)
            if kept:
                manifest_categories[name] = {
                    "label": str(spec.get("label") or name),
                    "match_keywords": [
                        str(word) for word in spec.get("match_keywords") or []
                    ],
                    "photos": kept,
                }

    sem = asyncio.Semaphore(6)
    quota_exhausted = False
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(60.0), follow_redirects=True
    ) as client:
        for name in selected:
            spec = categories[name]
            if quota_exhausted:
                # Out of quota: fall back to whatever an earlier manifest had
                # so previously built photos stay visible at runtime.
                kept = _reuse_category(name, previous, used_ids)
                if kept:
                    manifest_categories[name] = {
                        "label": str(spec.get("label") or name),
                        "match_keywords": [
                            str(word)
                            for word in spec.get("match_keywords") or []
                        ],
                        "photos": kept,
                    }
                print(f"[{name}] skipped (quota exhausted)")
                continue
            print(f"[{name}]")
            photos, quota_exhausted = await _build_category(
                client, sem, key, name, spec, factor, used_ids,
            )
            if not photos:
                photos = _reuse_category(name, previous, used_ids)
            if photos:
                manifest_categories[name] = {
                    "label": str(spec.get("label") or name),
                    "match_keywords": [
                        str(word) for word in spec.get("match_keywords") or []
                    ],
                    "photos": photos,
                }

    manifest = {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "unsplash",
        "fallback_categories": [
            str(name) for name in topics.get("fallback_categories") or []
            if name in manifest_categories
        ],
        "categories": manifest_categories,
    }

    GALLERY_DIR.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_FILE, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

    orphans = _cleanup_orphans(manifest)
    total = sum(
        len(category["photos"]) for category in manifest_categories.values()
    )
    size_mb = sum(
        path.stat().st_size for path in GALLERY_DIR.rglob("*.jpg")
    ) / 1024 / 1024
    print(
        f"done: {total} photos across {len(manifest_categories)} categories, "
        f"{size_mb:.1f} MB on disk, {orphans} orphan files removed"
    )
    print(f"manifest: {MANIFEST_FILE}")
    if quota_exhausted:
        print(
            "NOTE: the Unsplash hourly quota ran out; re-run the skipped "
            "categories with -c once the window resets."
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_main()))
