"""Local categorized photo gallery — an offline photo source for UIBench.

The gallery is pure data produced by ``tools/build_gallery.py``: photos on
disk under ``assets/gallery/<category>/`` plus one ``manifest.json`` holding
categories, per-photo keywords and the category match vocabulary.  This
module only implements a generic matching algorithm over that manifest; no
category name or domain keyword is hard-coded here, so the gallery can be
regrown or re-themed without touching runtime code.
"""
from __future__ import annotations

import hashlib
import json
import re
import threading
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GALLERY_DIR = PROJECT_ROOT / "assets" / "gallery"
MANIFEST_FILE = GALLERY_DIR / "manifest.json"
GALLERY_URL_PREFIX = "/gallery/"

_WORD_RE = re.compile(r"[a-z0-9]+")
_CJK_RE = re.compile(r"[\u3400-\u9fff]")

_cache_lock = threading.Lock()
_cached_manifest: dict[str, Any] | None = None
_cached_mtime: float | None = None


def _load_manifest() -> dict[str, Any] | None:
    """Return the parsed manifest, re-reading only when the file changes."""
    global _cached_manifest, _cached_mtime
    try:
        mtime = MANIFEST_FILE.stat().st_mtime
    except OSError:
        return None
    with _cache_lock:
        if _cached_manifest is not None and _cached_mtime == mtime:
            return _cached_manifest
        try:
            with open(MANIFEST_FILE, "r", encoding="utf-8") as fh:
                manifest = json.load(fh)
        except (OSError, json.JSONDecodeError):
            return None
        if not isinstance(manifest, dict):
            return None
        _cached_manifest = manifest
        _cached_mtime = mtime
        return manifest


def gallery_available() -> bool:
    """Return whether the local gallery holds at least one usable photo."""
    manifest = _load_manifest()
    if manifest is None:
        return False
    return any(
        category.get("photos")
        for category in (manifest.get("categories") or {}).values()
        if isinstance(category, dict)
    )


def _tokens(text: str) -> set[str]:
    return {word for word in _WORD_RE.findall(text.lower()) if len(word) >= 2}


def _keyword_hits(keywords: Any, tokens: set[str], text: str) -> int:
    """Count vocabulary hits; CJK keywords match by substring, latin by token."""
    hits = 0
    for keyword in keywords or []:
        keyword = str(keyword).strip().lower()
        if not keyword:
            continue
        if _CJK_RE.search(keyword):
            if keyword in text:
                hits += 1
        elif keyword in tokens:
            hits += 1
    return hits


def _tiebreak(query: str, photo_id: str) -> str:
    digest = hashlib.sha1(f"{query}|{photo_id}".encode("utf-8")).hexdigest()
    return digest


def _photo_payload(
    photo: dict[str, Any], category: str, slot: str, query: str,
) -> dict[str, Any]:
    files = photo.get("files") or {}
    return {
        "id": str(photo.get("id") or ""),
        "slot": slot,
        "query": query,
        "category": category,
        "description": str(photo.get("description") or "")[:300],
        "urls": {
            "small": f"{GALLERY_URL_PREFIX}{files.get('small', '')}",
            "regular": f"{GALLERY_URL_PREFIX}{files.get('regular', '')}",
        },
        "width": max(0, int(photo.get("width") or 0)),
        "height": max(0, int(photo.get("height") or 0)),
        "photographer": str(photo.get("photographer") or "")[:120],
        "photographer_url": "",
    }


def _valid_photos(category: dict[str, Any]) -> list[dict[str, Any]]:
    photos = []
    for photo in category.get("photos") or []:
        if not isinstance(photo, dict):
            continue
        files = photo.get("files") or {}
        if files.get("small") and files.get("regular") and photo.get("id"):
            photos.append(photo)
    return photos


def _best_photo(
    photos: list[dict[str, Any]], tokens: set[str], text: str,
    orientation: str, query: str, used_ids: set[str],
) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None
    best_rank: tuple[float, str] | None = None
    for photo in photos:
        photo_id = str(photo.get("id") or "")
        if photo_id in used_ids:
            continue
        score = 2.0 * _keyword_hits(photo.get("keywords"), tokens, text)
        if orientation and photo.get("orientation") == orientation:
            score += 3.0
        # Deterministic per-query shuffle: equal scores rotate through the
        # category instead of always electing the same first photo.
        rank = (-score, _tiebreak(query, photo_id))
        if best_rank is None or rank < best_rank:
            best, best_rank = photo, rank
    return best


def search_gallery_photos(
    requests: list[dict[str, Any]], *, max_requests: int,
) -> list[dict[str, Any]]:
    """Resolve named photo slots against the local manifest.

    Returns at most one photo per slot, deduplicated across the batch, in a
    payload shape identical to the Unsplash MCP boundary so the rest of the
    pipeline (model payload, URL audit, repair loop) works unchanged.
    """
    manifest = _load_manifest()
    if manifest is None:
        return []
    categories: dict[str, dict[str, Any]] = {
        str(name): category
        for name, category in (manifest.get("categories") or {}).items()
        if isinstance(category, dict)
    }
    if not categories:
        return []
    fallback_order = [
        str(name) for name in manifest.get("fallback_categories") or []
        if str(name) in categories
    ]

    photos: list[dict[str, Any]] = []
    used_ids: set[str] = set()
    for request in requests[: max(1, min(8, int(max_requests)))]:
        slot = str(request.get("slot") or "photo")
        query = str(request.get("query") or "")
        orientation = str(request.get("orientation") or "")
        text = f"{slot} {query}".lower()
        tokens = _tokens(text)

        scored = sorted(
            (
                (
                    -_keyword_hits(category.get("match_keywords"), tokens, text),
                    index,
                    name,
                )
                for index, (name, category) in enumerate(categories.items())
            ),
        )
        best_score = -scored[0][0] if scored else 0
        ordered_names = [name for score, _, name in scored if -score > 0]
        if not best_score:
            ordered_names = []

        # Preference order: matching categories, then declared fallbacks,
        # then anything with photos left so a slot never goes empty.
        candidates = ordered_names + [
            name for name in fallback_order if name not in ordered_names
        ] + [name for name in categories if name not in ordered_names
             and name not in fallback_order]

        for name in candidates:
            photo = _best_photo(
                _valid_photos(categories[name]), tokens, text,
                orientation, query, used_ids,
            )
            if photo is not None:
                used_ids.add(str(photo.get("id")))
                photos.append(_photo_payload(photo, name, slot, query))
                break
    return photos
