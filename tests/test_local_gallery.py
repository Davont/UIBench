"""Offline tests for the local categorized photo gallery."""
import asyncio
import json

import pytest

import uibench.image_tools as image_tools_mod
import uibench.local_gallery as local_gallery_mod
from uibench.image_tools import (
    approved_image_urls,
    call_image_search_batch,
    distinct_used_photos,
    image_resource_urls,
    image_tool_result_for_model,
)
from uibench.local_gallery import gallery_available, search_gallery_photos


def _manifest() -> dict:
    def photo(pid: str, category: str, orientation: str, keywords: list[str]):
        return {
            "id": pid,
            "files": {
                "small": f"{category}/{pid}-small.jpg",
                "regular": f"{category}/{pid}-regular.jpg",
            },
            "width": 1080,
            "height": 720 if orientation == "landscape" else 1350,
            "orientation": orientation,
            "description": f"{category} photo {pid}",
            "keywords": keywords,
            "photographer": "Test Author",
        }

    return {
        "version": 1,
        "source": "unsplash",
        "fallback_categories": ["life"],
        "categories": {
            "food": {
                "label": "美食",
                "match_keywords": ["food", "dish", "noodles", "美食", "菜品"],
                "photos": [
                    photo("food-1", "food", "landscape", ["noodles", "bowl"]),
                    photo("food-2", "food", "squarish", ["dessert", "cake"]),
                ],
            },
            "product": {
                "label": "商品",
                "match_keywords": ["product", "headphones", "watch"],
                "photos": [
                    photo("prod-1", "product", "squarish", ["headphones"]),
                    photo("prod-2", "product", "squarish", ["smartwatch", "watch"]),
                ],
            },
            "life": {
                "label": "生活",
                "match_keywords": ["lifestyle", "city"],
                "photos": [
                    photo("life-1", "life", "landscape", ["friends", "city"]),
                    photo("life-2", "life", "portrait", ["reading", "cozy"]),
                ],
            },
        },
    }


@pytest.fixture
def gallery(monkeypatch, tmp_path):
    manifest_file = tmp_path / "manifest.json"
    manifest_file.write_text(
        json.dumps(_manifest(), ensure_ascii=False), encoding="utf-8"
    )
    monkeypatch.setattr(local_gallery_mod, "MANIFEST_FILE", manifest_file)
    monkeypatch.setattr(local_gallery_mod, "_cached_manifest", None)
    monkeypatch.setattr(local_gallery_mod, "_cached_mtime", None)
    return manifest_file


def test_gallery_unavailable_without_manifest(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        local_gallery_mod, "MANIFEST_FILE", tmp_path / "missing.json"
    )
    monkeypatch.setattr(local_gallery_mod, "_cached_manifest", None)
    monkeypatch.setattr(local_gallery_mod, "_cached_mtime", None)
    assert gallery_available() is False
    assert search_gallery_photos(
        [{"slot": "hero", "query": "food"}], max_requests=4
    ) == []


def test_queries_resolve_to_matching_categories(gallery) -> None:
    photos = search_gallery_photos(
        [
            {"slot": "hero", "query": "spicy noodles bowl"},
            {"slot": "card-1", "query": "wireless headphones product"},
        ],
        max_requests=4,
    )
    assert [photo["category"] for photo in photos] == ["food", "product"]
    assert photos[0]["id"] == "food-1"
    assert photos[1]["id"] == "prod-1"
    assert photos[0]["urls"]["small"] == "/gallery/food/food-1-small.jpg"
    assert photos[0]["slot"] == "hero"
    assert photos[0]["query"] == "spicy noodles bowl"


def test_chinese_queries_match_by_substring(gallery) -> None:
    photos = search_gallery_photos(
        [{"slot": "hero", "query": "一个美食外卖 App 首页 hero"}],
        max_requests=4,
    )
    assert photos and photos[0]["category"] == "food"


def test_orientation_preference_breaks_ties(gallery) -> None:
    photos = search_gallery_photos(
        [{"slot": "hero", "query": "美食", "orientation": "landscape"}],
        max_requests=4,
    )
    assert photos[0]["id"] == "food-1"
    photos = search_gallery_photos(
        [{"slot": "card", "query": "美食", "orientation": "squarish"}],
        max_requests=4,
    )
    assert photos[0]["id"] == "food-2"


def test_batch_deduplicates_and_falls_back(gallery) -> None:
    photos = search_gallery_photos(
        [
            {"slot": "dish-1", "query": "noodles dish"},
            {"slot": "dish-2", "query": "noodles dish"},
            {"slot": "dish-3", "query": "noodles dish"},
        ],
        max_requests=4,
    )
    ids = [photo["id"] for photo in photos]
    assert len(ids) == len(set(ids)) == 3
    # Two photos exist in food; the third slot falls back to another category.
    assert {ids[0], ids[1]} == {"food-1", "food-2"}


def test_unmatched_query_uses_declared_fallback(gallery) -> None:
    photos = search_gallery_photos(
        [{"slot": "hero", "query": "zzz unmatched keywords"}],
        max_requests=4,
    )
    assert photos and photos[0]["category"] == "life"


def test_results_are_deterministic(gallery) -> None:
    requests = [
        {"slot": "hero", "query": "noodles", "orientation": "landscape"},
        {"slot": "card", "query": "watch product"},
    ]
    first = search_gallery_photos(requests, max_requests=4)
    second = search_gallery_photos(requests, max_requests=4)
    assert [p["id"] for p in first] == [p["id"] for p in second]


def test_gallery_urls_pass_audit_and_model_payload(gallery) -> None:
    photos = search_gallery_photos(
        [{"slot": "hero", "query": "noodles"}], max_requests=4
    )
    approved = approved_image_urls(photos)
    assert "/gallery/food/food-1-small.jpg" in approved

    html = '<img src="/gallery/food/food-1-small.jpg">'
    assert image_resource_urls(html) == {"/gallery/food/food-1-small.jpg"}
    assert len(distinct_used_photos(photos, html)) == 1

    payload = json.loads(image_tool_result_for_model(photos))
    assert payload["photos"][0]["urls"]["small"].startswith("/gallery/")
    assert "download_location" not in payload["photos"][0]


def test_invented_gallery_urls_are_flagged(gallery) -> None:
    photos = search_gallery_photos(
        [{"slot": "hero", "query": "noodles"}], max_requests=4
    )
    html = '<img src="/gallery/food/made-up.jpg">'
    violations = image_resource_urls(html) - approved_image_urls(photos)
    assert violations == {"/gallery/food/made-up.jpg"}


def test_call_image_search_batch_uses_local_source(gallery, monkeypatch) -> None:
    monkeypatch.setattr(image_tools_mod.settings, "image_source", "local")
    progress_calls: list[tuple[int, int, str]] = []

    async def progress(completed: int, total: int, slot: str) -> None:
        progress_calls.append((completed, total, slot))

    photos = asyncio.run(call_image_search_batch(
        {"requests": [{"slot": "hero", "query": "noodles dish"}]},
        max_requests=4,
        progress=progress,
    ))
    assert photos and photos[0]["category"] == "food"
    assert progress_calls == [(1, 1, "hero")]


def test_local_gallery_available_gates_image_tool(gallery, monkeypatch) -> None:
    monkeypatch.setattr(image_tools_mod.settings, "image_tools_enabled", True)
    monkeypatch.setattr(image_tools_mod.settings, "image_source", "local")
    assert image_tools_mod.image_tool_available() is True

    monkeypatch.setattr(
        local_gallery_mod, "MANIFEST_FILE", gallery.parent / "gone.json"
    )
    monkeypatch.setattr(local_gallery_mod, "_cached_manifest", None)
    monkeypatch.setattr(local_gallery_mod, "_cached_mtime", None)
    assert image_tools_mod.image_tool_available() is False
