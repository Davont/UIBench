"""Offline tests for the image tool boundary (local gallery + Unsplash MCP)."""
from types import SimpleNamespace

import pytest

import uibench.image_tools as image_tools_mod
from uibench.image_tools import (
    ImageToolError,
    IMAGE_SEARCH_TOOL,
    _parse_mcp_text,
    _sanitize_photos,
    _should_stop_image_batch,
    approved_image_urls,
    distinct_used_photos,
    image_resource_urls,
    image_search_requests,
    image_tool_result_for_model,
    unresolved_image_bindings,
)
from uibench.pc import SYSTEM_PC
from uibench.prompts import SYSTEM_MOBILE


def _photo(**overrides):
    value = {
        "id": "safe-id",
        "description": "A beach",
        "urls": {
            "small": "https://images.unsplash.com/photo-safe",
            "regular": "https://images.unsplash.com/photo-safe?w=1080",
        },
        "width": 1080,
        "height": 1620,
        "photographer": "Example",
        "photographer_url": "https://unsplash.com/@example",
        "download_location": "https://api.unsplash.com/photos/safe-id/download",
    }
    value.update(overrides)
    return value


def test_sanitize_accepts_only_unsplash_https_urls() -> None:
    safe = _sanitize_photos([_photo()])
    assert len(safe) == 1
    assert safe[0]["urls"]["small"].startswith("https://images.unsplash.com/")
    assert "utm_source=uibench" in safe[0]["photographer_url"]

    malicious = _photo(urls={"small": "https://example.com/tracker.jpg"})
    assert _sanitize_photos([malicious]) == []


def test_sanitize_allows_missing_attribution_but_requires_tracking_metadata() -> None:
    without_attribution = _sanitize_photos([
        _photo(photographer="", photographer_url=""),
    ])
    assert len(without_attribution) == 1
    assert without_attribution[0]["photographer"] == ""
    assert without_attribution[0]["photographer_url"] == ""
    assert _sanitize_photos([_photo(download_location="")]) == []


def test_model_payload_hides_download_tracking_url() -> None:
    photo = _sanitize_photos([_photo()])[0]
    photo.update({"slot": "wireless-headphones", "query": "wireless headphones"})
    payload = image_tool_result_for_model([photo])
    assert "images.unsplash.com" in payload
    assert "download_location" not in payload
    assert "api.unsplash.com" not in payload
    assert "wireless-headphones" in payload
    assert "instead of an icon or empty placeholder" in payload


def test_image_resource_urls_only_counts_rendered_image_contexts() -> None:
    html = """
    <!-- https://images.unsplash.com/photo-comment -->
    <a href="https://images.unsplash.com/photo-link">source</a>
    <img src="https://images.unsplash.com/photo-one?w=600">
    <source srcset="https://images.unsplash.com/photo-two?w=400 1x,
                    https://images.unsplash.com/photo-two?w=800 2x">
    <div style="background-image:url('https://images.unsplash.com/photo-three')"></div>
    """
    assert image_resource_urls(html) == {
        "https://images.unsplash.com/photo-one?w=600",
        "https://images.unsplash.com/photo-two?w=400",
        "https://images.unsplash.com/photo-two?w=800",
        "https://images.unsplash.com/photo-three",
    }


def test_image_resource_audit_handles_unquoted_and_static_jsx_values() -> None:
    html = """
    <img src=https://images.unsplash.com/photo-unquoted>
    <img src={"https://images.unsplash.com/photo-jsx"}>
    <object data=https://images.unsplash.com/photo-object></object>
    <embed src="https://images.unsplash.com/photo-embed">
    <input type="image" src=https://images.unsplash.com/photo-input>
    <input type="text" src=https://example.test/not-an-image>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    """
    assert image_resource_urls(html) == {
        "https://images.unsplash.com/photo-unquoted",
        "https://images.unsplash.com/photo-jsx",
        "https://images.unsplash.com/photo-object",
        "https://images.unsplash.com/photo-embed",
        "https://images.unsplash.com/photo-input",
    }


def test_protocol_relative_urls_are_audited_in_every_image_context() -> None:
    html = """
    <img src=//evil.test/img>
    <source srcset="//evil.test/a 1x, //evil.test/b 2x">
    <object data=//evil.test/object></object>
    <embed src=//evil.test/embed>
    <input type=image src=//evil.test/input>
    <svg><image href=//evil.test/svg></image></svg>
    <div style="background:url(//evil.test/css)"></div>
    """
    assert image_resource_urls(html) == {
        "//evil.test/img", "//evil.test/a", "//evil.test/b",
        "//evil.test/object", "//evil.test/embed", "//evil.test/input",
        "//evil.test/svg", "//evil.test/css",
    }


def test_html_comments_do_not_create_image_evidence() -> None:
    html = """
    <!-- <img src=//evil.test/commented> -->
    <img src="https://images.unsplash.com/photo-safe">
    <!-- <a href="https://unsplash.com/@example?utm_source=uibench&utm_medium=referral">
      Photo by Example on Unsplash</a> -->
    """
    assert image_resource_urls(html) == {
        "https://images.unsplash.com/photo-safe",
    }


def test_dynamic_image_bindings_are_fail_closed_without_blocking_script_cdn() -> None:
    html = """
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script type="text/babel">
      const rows = [{image: "https://tracker.example/a.png"}];
      const App = () => <img src={rows[0].image}/>;
      const Spread = () => <img {...rows[0]}/>;
      const Css = () => <div style={{backgroundImage: 'url(' + rows[0].image + ')'}}/>;
    </script>
    """
    assert image_resource_urls(html) == set()
    assert unresolved_image_bindings(html) == ("css.url", "img.spread", "img.src")


def test_react_image_and_create_element_are_audited_fail_closed() -> None:
    html = """
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script type="text/babel">
      const Static = () => <Image src="//evil.test/component"/>;
      const Dynamic = () => <Image src={photo.url}/>;
      const A = React.createElement('img', {src: '//evil.test/create'});
      const B = React.createElement('img', {src: photo.url});
      const C = React.createElement('img', {...photo});
    </script>
    """
    assert image_resource_urls(html) == {
        "//evil.test/component", "//evil.test/create",
    }
    assert unresolved_image_bindings(html) == (
        "createElement.img.spread",
        "createElement.img.src",
        "image.src",
    )


def test_distinct_used_photos_deduplicates_shared_id_and_url() -> None:
    shared = "https://images.unsplash.com/photo-shared"
    photos = [
        {"id": "same", "slot": "one", "urls": {"small": shared}},
        {"id": "same", "slot": "two", "urls": {"small": shared}},
    ]
    assert len(distinct_used_photos(photos, f'<img src="{shared}">')) == 1


def test_distinct_photos_canonicalize_unsplash_query_variants() -> None:
    base = "https://images.unsplash.com/photo-shared"
    photos = [
        {"id": "first", "urls": {"small": base + "?w=400"}},
        {"id": "second", "urls": {"small": base + "?w=900"}},
    ]
    html = f'<img src="{base}?w=400"><img src="{base}?w=900">'
    assert len(distinct_used_photos(photos, html)) == 1


def test_sanitize_rejects_missing_or_invalid_photo_ids() -> None:
    assert _sanitize_photos([_photo(id="")]) == []
    assert _sanitize_photos([_photo(id="bad/id")]) == []


def test_approved_image_urls_are_exact_tool_results() -> None:
    assert approved_image_urls([_photo()]) == {
        "https://images.unsplash.com/photo-safe",
        "https://images.unsplash.com/photo-safe?w=1080",
    }


def test_tool_schema_requests_named_photo_batch() -> None:
    parameters = IMAGE_SEARCH_TOOL["function"]["parameters"]
    assert parameters["required"] == ["requests"]
    requests = parameters["properties"]["requests"]
    assert requests["maxItems"] == 8
    assert requests["items"]["required"] == ["slot", "query"]


def test_batch_requests_are_bounded_and_keep_slot_metadata() -> None:
    requests = image_search_requests({
        "requests": [
            {
                "slot": f"product-{index}",
                "query": f"product photo {index}",
                "orientation": "squarish",
            }
            for index in range(9)
        ],
    }, max_requests=6)
    assert len(requests) == 6
    assert requests[0] == {
        "slot": "product-0",
        "query": "product photo 0",
        "per_page": 2,
        "orientation": "squarish",
    }


def test_legacy_single_query_is_still_normalized() -> None:
    requests = image_search_requests({
        "query": "tropical beach",
        "per_page": 1,
        "orientation": "portrait",
    }, max_requests=6)
    assert requests == [{
        "slot": "photo",
        "query": "tropical beach",
        "per_page": 1,
        "orientation": "portrait",
    }]


def test_mcp_v2_snake_case_error_is_detected() -> None:
    result = SimpleNamespace(
        is_error=True,
        content=[SimpleNamespace(type="text", text="401 Unauthorized")],
    )
    with pytest.raises(ImageToolError, match="tool error: 401 Unauthorized"):
        _parse_mcp_text(result)


def test_mcp_error_redacts_access_key(monkeypatch) -> None:
    monkeypatch.setenv("UNSPLASH_ACCESS_KEY", "secret-test-key")
    result = SimpleNamespace(
        is_error=True,
        content=[SimpleNamespace(
            type="text",
            text="request failed for secret-test-key",
        )],
    )
    with pytest.raises(ImageToolError) as raised:
        _parse_mcp_text(result)
    assert "secret-test-key" not in str(raised.value)
    assert "[redacted]" in str(raised.value)


def test_auth_and_quota_errors_stop_the_remaining_batch() -> None:
    assert _should_stop_image_batch(ImageToolError("403 Forbidden")) is True
    assert _should_stop_image_batch(ImageToolError("Rate Limit Exceeded")) is True
    assert _should_stop_image_batch(ImageToolError("temporary timeout")) is False


def test_mcp_structured_result_is_unwrapped() -> None:
    result = SimpleNamespace(
        is_error=False,
        structured_content={"result": [_photo()]},
        content=[],
    )
    assert _parse_mcp_text(result)[0]["id"] == "safe-id"


def test_prompts_never_allow_invented_image_urls() -> None:
    for prompt in (SYSTEM_MOBILE, SYSTEM_PC):
        assert "search_photos" in prompt
        assert "绝不得自行编造" in prompt
        assert "Photo by <photographer> on Unsplash" not in prompt


def test_image_tool_accepts_windows_virtualenv_python(monkeypatch, tmp_path) -> None:
    windows_python = tmp_path / ".venv" / "Scripts" / "python.exe"
    windows_python.parent.mkdir(parents=True)
    windows_python.write_bytes(b"python")
    server = tmp_path / "server.py"
    server.write_text("", encoding="utf-8")

    monkeypatch.setattr(
        image_tools_mod,
        "MCP_PYTHON_CANDIDATES",
        (tmp_path / ".venv" / "bin" / "python", windows_python),
    )
    monkeypatch.setattr(image_tools_mod, "MCP_SERVER", server)
    monkeypatch.setattr(image_tools_mod.settings, "image_tools_enabled", True)
    monkeypatch.setattr(image_tools_mod.settings, "image_source", "unsplash")
    monkeypatch.setenv("UNSPLASH_ACCESS_KEY", "test-key")

    assert image_tools_mod.image_tool_available() is True
    assert image_tools_mod._mcp_python() == windows_python
