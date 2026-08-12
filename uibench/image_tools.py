"""Optional Unsplash image tool backed by a local stdio MCP server."""
from __future__ import annotations

import asyncio
import json
import os
import re
from collections.abc import Awaitable, Callable
from html import unescape
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import httpx

# Preload the optional MCP SDK (and its httpx2 dependency) while the process is
# still single-threaded.  The openai client probes sys.modules["httpx2"] without
# taking the import lock, so letting the first `import mcp` happen inside a
# concurrent request can expose a partially initialized httpx2 module to the
# model-call worker threads (AttributeError: ... has no attribute 'Response').
try:
    import mcp.client.stdio  # noqa: F401
except ImportError:
    pass

from config import settings

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MCP_ROOT = PROJECT_ROOT / ".mcp" / "unsplash-mcp-server"
MCP_SERVER = MCP_ROOT / "server.py"
MCP_PYTHON_CANDIDATES = (
    MCP_ROOT / ".venv" / "bin" / "python",
    MCP_ROOT / ".venv" / "Scripts" / "python.exe",
)

UNSPLASH_TOOL = {
    "type": "function",
    "function": {
        "name": "search_photos",
        "description": (
            "Search Unsplash for multiple named visual slots in one call. When a UI "
            "contains a hero plus product/content cards, request a separate slot for "
            "each major visible photo (for example hero-banner, wireless-headphones, "
            "smartwatch). Use concise English queries. Do not call for icons, charts, "
            "decorative gradients, or when photography is unnecessary."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "requests": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": 8,
                    "description": (
                        "Named photo slots needed by the page. Use one request per "
                        "major visible photo instead of one broad page-level query."
                    ),
                    "items": {
                        "type": "object",
                        "properties": {
                            "slot": {
                                "type": "string",
                                "description": (
                                    "Stable semantic slot name such as hero-banner, "
                                    "wireless-headphones, or smartwatch."
                                ),
                            },
                            "query": {
                                "type": "string",
                                "description": "Concise English photo search query.",
                            },
                            "orientation": {
                                "type": "string",
                                "enum": ["portrait", "landscape", "squarish"],
                            },
                            "color": {
                                "type": "string",
                                "enum": [
                                    "black_and_white", "black", "white", "yellow",
                                    "orange", "red", "purple", "magenta", "green",
                                    "teal", "blue",
                                ],
                            },
                        },
                        "required": ["slot", "query"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["requests"],
            "additionalProperties": False,
        },
    },
}

_IMAGE_HOSTS = {"images.unsplash.com", "plus.unsplash.com"}
_UNSPLASH_HOSTS = {"unsplash.com", "www.unsplash.com"}
_ORIENTATIONS = {"portrait", "landscape", "squarish"}
_COLORS = {
    "black_and_white", "black", "white", "yellow", "orange", "red",
    "purple", "magenta", "green", "teal", "blue",
}
_PHOTO_ID_RE = re.compile(r"[A-Za-z0-9_-]{1,80}")
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_IMAGE_ELEMENT_RE = re.compile(
    r"<(?P<tag>img|source|video|input|image|object|embed)\b"
    r"(?P<attrs>(?:[^>\"']|\"[^\"]*\"|'[^']*')*)>",
    re.IGNORECASE | re.DOTALL,
)
_ATTRIBUTE_VALUE = (
    r'(?P<value>"[^\"]*"|\'[^\']*\'|'
    r'\{\s*(?:"[^\"]*"|\'[^\']*\'|`[^`]*`)\s*\}|'
    r'\{[^}]*\}|[^\s>]+)'
)
_IMAGE_ATTR_RE = re.compile(
    r"\b(?P<name>src|srcset|poster|xlink:href|href|data)\s*=\s*" + _ATTRIBUTE_VALUE,
    re.IGNORECASE | re.DOTALL,
)
_TYPE_ATTR_RE = re.compile(
    r"\btype\s*=\s*" + _ATTRIBUTE_VALUE,
    re.IGNORECASE | re.DOTALL,
)
_CREATE_ELEMENT_START_RE = re.compile(
    r"(?:React\s*\.\s*)?createElement\s*\(\s*"
    r"(?P<quote>['\"])(?P<tag>img|source|video|input|image|object|embed)"
    r"(?P=quote)\s*,",
    re.IGNORECASE,
)
_JS_IMAGE_PROP_RE = re.compile(
    r"(?P<quote>['\"]?)(?P<name>src|srcset|poster|data|href|xlinkhref|type)"
    r"(?P=quote)\s*:\s*"
    r"(?P<value>\"[^\"]*\"|'[^']*'|`[^`]*`|[^,}]+)",
    re.IGNORECASE | re.DOTALL,
)
_CSS_URL_RE = re.compile(
    r"url\(\s*(?P<value>[^)]*)\)",
    re.IGNORECASE,
)
ImageSearchProgress = Callable[[int, int, str], Awaitable[None]]


class ImageToolError(RuntimeError):
    """Raised when the optional image MCP cannot provide a safe result."""


def _attribute_literal(raw_value: str) -> tuple[str, bool]:
    """Return one static attribute value and whether it is unresolved JSX."""
    value = raw_value.strip()
    if value.startswith("{"):
        if not value.endswith("}"):
            return "", True
        expression = value[1:-1].strip()
        if (
            len(expression) >= 2
            and expression[0] in {'"', "'", "`"}
            and expression[-1] == expression[0]
        ):
            literal = expression[1:-1]
            if expression[0] == "`" and "${" in literal:
                return "", True
            return unescape(literal), False
        return "", True
    if len(value) >= 2 and value[0] in {'"', "'", "`"} and value[-1] == value[0]:
        if value[0] == "`" and "${" in value:
            return "", True
        value = value[1:-1]
    return unescape(value), False


def _js_literal(raw_value: str) -> tuple[str, bool]:
    value = raw_value.strip()
    if (
        len(value) >= 2
        and value[0] in {'"', "'", "`"}
        and value[-1] == value[0]
    ):
        if value[0] == "`" and "${" in value:
            return "", True
        return unescape(value[1:-1]), False
    return "", True


def _without_html_comments(html: str) -> str:
    return _HTML_COMMENT_RE.sub("", html or "")


def _is_remote_url(value: str) -> bool:
    return value.startswith(("https://", "http://", "//"))


def _balanced_js_object(source: str, start: int) -> str | None:
    """Return one JS object literal, or None when it cannot be proven bounded."""
    if start >= len(source) or source[start] != "{":
        return None
    depth = 0
    quote = ""
    escaped = False
    for index in range(start, len(source)):
        char = source[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            continue
        if char in {'"', "'", "`"}:
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[start:index + 1]
    return None


def _create_element_props(html: str):
    for match in _CREATE_ELEMENT_START_RE.finditer(html):
        tag = match.group("tag").lower()
        start = match.end()
        while start < len(html) and html[start].isspace():
            start += 1
        if html.startswith("null", start):
            yield tag, "", ""
            continue
        props = _balanced_js_object(html, start)
        yield tag, props or "", props


def _image_attribute_matches(html: str):
    for element in _IMAGE_ELEMENT_RE.finditer(_without_html_comments(html)):
        raw_tag = element.group("tag")
        tag = element.group("tag").lower()
        attrs = element.group("attrs")
        if tag == "input":
            type_match = _TYPE_ATTR_RE.search(attrs)
            if type_match is None:
                continue
            input_type, dynamic_type = _attribute_literal(type_match.group("value"))
            if dynamic_type or input_type.casefold() != "image":
                continue
        for attribute in _IMAGE_ATTR_RE.finditer(attrs):
            name = attribute.group("name").lower()
            if tag == "image" and raw_tag == "image":
                if name not in {"href", "xlink:href"}:
                    continue
            elif tag == "image":
                if name not in {"src", "srcset", "poster"}:
                    continue
            elif tag == "object":
                if name != "data":
                    continue
            elif name in {"href", "xlink:href"}:
                continue
            elif name == "data":
                continue
            yield tag, name, attribute.group("value")

    source = _without_html_comments(html)
    for tag, raw_props, props in _create_element_props(source):
        if props is None:
            continue
        properties = list(_JS_IMAGE_PROP_RE.finditer(raw_props))
        type_property = next(
            (item for item in properties if item.group("name").lower() == "type"),
            None,
        )
        if tag == "input":
            if type_property is None:
                continue
            input_type, dynamic_type = _js_literal(type_property.group("value"))
            if dynamic_type or input_type.casefold() != "image":
                continue
        for prop in properties:
            name = prop.group("name").lower()
            if name == "type":
                continue
            if tag == "image" and name not in {"href", "xlinkhref"}:
                continue
            if tag == "object" and name != "data":
                continue
            if tag not in {"image", "object"} and name in {"href", "xlinkhref", "data"}:
                continue
            raw_value = prop.group("value")
            _, dynamic = _js_literal(raw_value)
            yield (
                f"createElement.{tag}", name,
                "{" + raw_value + "}" if dynamic else raw_value,
            )


def unresolved_image_bindings(html: str) -> tuple[str, ...]:
    """Return image-bearing JSX/CSS bindings whose target cannot be proven."""
    unresolved: set[str] = set()
    source = _without_html_comments(html)
    for element in _IMAGE_ELEMENT_RE.finditer(source):
        if re.search(r"\{\s*\.\.\.", element.group("attrs")):
            unresolved.add(f"{element.group('tag').lower()}.spread")
    for tag, raw_props, props in _create_element_props(source):
        if props is None:
            unresolved.add(f"createElement.{tag}.props")
        elif re.search(r"(?:^|[,{}])\s*\.\.\.", raw_props):
            unresolved.add(f"createElement.{tag}.spread")
    for tag, name, raw_value in _image_attribute_matches(source):
        _, dynamic = _attribute_literal(raw_value)
        if dynamic:
            unresolved.add(f"{tag}.{name}")
    for match in _CSS_URL_RE.finditer(source):
        value = unescape(match.group("value").strip().strip("'\""))
        concatenated = (
            value.startswith("+")
            or value.endswith("+")
            or re.search(r"['\"`]\s*\+|\+\s*['\"`]", value) is not None
            or re.search(r"\s\+\s", value) is not None
        )
        if any(marker in value for marker in ("${", "var(", "{")) or concatenated:
            unresolved.add("css.url")
    return tuple(sorted(unresolved))


def image_resource_urls(html: str) -> set[str]:
    """Return remote URLs used in image-bearing HTML/CSS contexts.

    This deliberately ignores ordinary links, comments, and script ``src``
    attributes so a URL only counts when the generated page would render it as
    an image. JSX inside a PC-mode script is still matched as source text.
    """
    urls: set[str] = set()
    for _, name, raw_value in _image_attribute_matches(html):
        value, dynamic = _attribute_literal(raw_value)
        if dynamic:
            continue
        values = value.split(",") if name == "srcset" else [value]
        for candidate in values:
            url = candidate.strip().split(maxsplit=1)[0]
            if _is_remote_url(url):
                urls.add(url)
    for match in _CSS_URL_RE.finditer(_without_html_comments(html)):
        value = unescape(match.group("value").strip().strip("'\""))
        if _is_remote_url(value):
            urls.add(value)
    return urls


def approved_image_urls(photos: list[dict[str, Any]]) -> set[str]:
    """Return the exact image URLs supplied by the trusted image tool."""
    return {
        str(url)
        for photo in photos
        for name, url in (photo.get("urls") or {}).items()
        if name in {"small", "regular"}
        if str(url).startswith("https://")
    }


def distinct_used_photos(
    photos: list[dict[str, Any]], html: str,
) -> list[dict[str, Any]]:
    """Return rendered photos, deduplicated by both asset id and URL."""
    rendered_urls = image_resource_urls(html)
    used: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_assets: set[str] = set()
    for photo in photos:
        photo_urls = {
            str(url)
            for name, url in (photo.get("urls") or {}).items()
            if name in {"small", "regular"} and url
        }
        matched_urls = photo_urls & rendered_urls
        if not matched_urls:
            continue
        photo_id = str(photo.get("id") or "")
        valid_id = photo_id if _PHOTO_ID_RE.fullmatch(photo_id) else ""
        assets = {_canonical_image_asset(url) for url in photo_urls}
        assets.discard("")
        if not valid_id and not assets:
            continue
        if (valid_id and valid_id in seen_ids) or assets & seen_assets:
            continue
        used.append(photo)
        if valid_id:
            seen_ids.add(valid_id)
        seen_assets.update(assets)
    return used


def _canonical_image_asset(value: str) -> str:
    parsed = urlparse("https:" + value if value.startswith("//") else value)
    host = (parsed.hostname or "").lower()
    if host not in _IMAGE_HOSTS or not parsed.path:
        return ""
    return f"{host}{parsed.path}"


def image_search_requests(
    arguments: dict[str, Any], *, max_requests: int,
) -> list[dict[str, Any]]:
    """Normalize a batch tool call, with legacy single-query compatibility."""
    limit = max(1, min(8, int(max_requests)))
    raw_requests = arguments.get("requests")
    if isinstance(raw_requests, list):
        candidates = raw_requests[:limit]
    elif arguments.get("query"):
        # Accept archived/older provider calls while the public schema moves to
        # named batches. The next model turn always sees the new schema.
        candidates = [{
            "slot": arguments.get("slot") or "photo",
            "query": arguments.get("query"),
            "orientation": arguments.get("orientation"),
            "color": arguments.get("color"),
            "per_page": arguments.get("per_page", 1),
        }]
    else:
        raise ImageToolError("search_photos requires at least one request")

    requests: list[dict[str, Any]] = []
    for index, raw in enumerate(candidates):
        if not isinstance(raw, dict):
            continue
        query = str(raw.get("query") or "").strip()[:160]
        if not query:
            continue
        slot = str(raw.get("slot") or f"photo-{index + 1}").strip()[:80]
        if not slot:
            slot = f"photo-{index + 1}"
        try:
            per_page = min(2, max(1, int(raw.get("per_page", 2))))
        except (TypeError, ValueError):
            per_page = 2
        request: dict[str, Any] = {
            "slot": slot,
            "query": query,
            # Fetch two candidates so the batch can avoid duplicate top hits,
            # while still returning at most one photo for each named slot.
            "per_page": per_page,
        }
        orientation = str(raw.get("orientation") or "")
        color = str(raw.get("color") or "")
        if orientation in _ORIENTATIONS:
            request["orientation"] = orientation
        if color in _COLORS:
            request["color"] = color
        requests.append(request)
    if not requests:
        raise ImageToolError("search_photos contains no valid requests")
    return requests


def image_tool_available() -> bool:
    """Return whether local configuration is sufficient to offer the tool."""
    return bool(
        settings.image_tools_enabled
        and os.environ.get("UNSPLASH_ACCESS_KEY")
        and any(candidate.is_file() for candidate in MCP_PYTHON_CANDIDATES)
        and MCP_SERVER.is_file()
    )


def _mcp_python() -> Path:
    for candidate in MCP_PYTHON_CANDIDATES:
        if candidate.is_file():
            return candidate
    raise ImageToolError("Unsplash MCP Python environment is not installed")


def _safe_https_url(value: Any, hosts: set[str]) -> str:
    url = str(value or "").strip()
    parsed = urlparse(url)
    if parsed.scheme != "https" or (parsed.hostname or "").lower() not in hosts:
        return ""
    return url


def _with_attribution_query(url: str) -> str:
    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query.update({"utm_source": "uibench", "utm_medium": "referral"})
    return urlunparse(parsed._replace(query=urlencode(query)))


def _sanitize_photos(payload: Any) -> list[dict[str, Any]]:
    """Keep only bounded, HTTPS Unsplash fields before sending data to a model."""
    if not isinstance(payload, list):
        raise ImageToolError("Unsplash MCP returned a non-list payload")
    photos: list[dict[str, Any]] = []
    for raw in payload[:2]:
        if not isinstance(raw, dict):
            continue
        photo_id = str(raw.get("id") or "")[:80]
        if not _PHOTO_ID_RE.fullmatch(photo_id):
            continue
        urls = raw.get("urls") if isinstance(raw.get("urls"), dict) else {}
        safe_urls = {
            name: url
            for name in ("regular", "small")
            if (url := _safe_https_url(urls.get(name), _IMAGE_HOSTS))
        }
        if not safe_urls:
            continue
        photographer_url = _safe_https_url(
            raw.get("photographer_url"), _UNSPLASH_HOSTS
        )
        download_location = _safe_https_url(
            raw.get("download_location"), {"api.unsplash.com"}
        )
        photographer = str(raw.get("photographer") or "").strip()[:120]
        # Keep download tracking mandatory, but do not discard an otherwise
        # usable image when photographer attribution metadata is unavailable.
        if not download_location:
            continue
        photos.append({
            "id": photo_id,
            "description": str(raw.get("description") or "")[:300],
            "urls": safe_urls,
            "width": max(0, int(raw.get("width") or 0)),
            "height": max(0, int(raw.get("height") or 0)),
            "photographer": photographer,
            "photographer_url": (
                _with_attribution_query(photographer_url) if photographer_url else ""
            ),
            "unsplash_url": (
                "https://unsplash.com/?utm_source=uibench&utm_medium=referral"
            ),
            "download_location": download_location,
        })
    return photos


async def _enrich_photo_metadata(payload: Any) -> Any:
    """Add attribution/tracking fields absent from the upstream MCP project."""
    if not isinstance(payload, list):
        return payload
    key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not key:
        return payload
    headers = {"Authorization": f"Client-ID {key}", "Accept-Version": "v1"}
    enriched: list[Any] = []
    async with httpx.AsyncClient(timeout=20.0) as client:
        for item in payload[:2]:
            if not isinstance(item, dict):
                enriched.append(item)
                continue
            photo = dict(item)
            has_metadata = all(photo.get(field) for field in (
                "photographer", "photographer_url", "download_location",
            ))
            photo_id = str(photo.get("id") or "")
            if not has_metadata and _PHOTO_ID_RE.fullmatch(photo_id):
                try:
                    response = await client.get(
                        f"https://api.unsplash.com/photos/{photo_id}",
                        headers=headers,
                    )
                    response.raise_for_status()
                    detail = response.json()
                    user = detail.get("user") or {}
                    links = detail.get("links") or {}
                    photo["photographer"] = user.get("name") or ""
                    photo["photographer_url"] = (user.get("links") or {}).get("html") or ""
                    photo["download_location"] = links.get("download_location") or ""
                except (httpx.HTTPError, ValueError, TypeError):
                    pass
            enriched.append(photo)
    return enriched


def _parse_mcp_text(result: Any) -> Any:
    texts = [
        str(getattr(block, "text", ""))
        for block in (getattr(result, "content", None) or [])
        if getattr(block, "type", None) == "text"
    ]
    if (
        getattr(result, "isError", False)
        or getattr(result, "is_error", False)
    ):
        detail = " ".join(" ".join(text.split()) for text in texts if text.strip())
        key = os.environ.get("UNSPLASH_ACCESS_KEY") or ""
        if key:
            detail = detail.replace(key, "[redacted]")
        detail = detail[:400]
        suffix = f": {detail}" if detail else ""
        raise ImageToolError(f"Unsplash MCP reported a tool error{suffix}")
    structured = (
        getattr(result, "structuredContent", None)
        or getattr(result, "structured_content", None)
    )
    if structured is not None:
        if isinstance(structured, dict) and set(structured) == {"result"}:
            return structured["result"]
        return structured
    if not texts:
        raise ImageToolError("Unsplash MCP returned no text content")
    try:
        return json.loads("\n".join(texts))
    except json.JSONDecodeError as exc:
        raise ImageToolError("Unsplash MCP returned invalid JSON") from exc


def _should_stop_image_batch(exc: Exception) -> bool:
    """Stop spending requests after authentication or quota rejection."""
    text = str(exc).lower()
    return any(fragment in text for fragment in (
        "403 forbidden",
        "401 unauthorized",
        "rate limit",
        "missing unsplash_access_key",
    ))


async def call_unsplash_mcp(arguments: dict[str, Any]) -> list[dict[str, Any]]:
    """Spawn the configured MCP server, call ``search_photos``, and sanitize it."""
    requests = image_search_requests(arguments, max_requests=1)
    return await _call_unsplash_requests(
        requests, one_per_slot=False, progress=None
    )


async def call_unsplash_mcp_batch(
    arguments: dict[str, Any], *, max_requests: int,
    progress: ImageSearchProgress | None = None,
) -> list[dict[str, Any]]:
    """Resolve multiple named photo slots through one MCP server session."""
    requests = image_search_requests(arguments, max_requests=max_requests)
    return await _call_unsplash_requests(
        requests, one_per_slot=True, progress=progress
    )


async def _call_unsplash_requests(
    requests: list[dict[str, Any]], *, one_per_slot: bool,
    progress: ImageSearchProgress | None,
) -> list[dict[str, Any]]:
    if not image_tool_available():
        raise ImageToolError("Unsplash MCP is not installed or configured")

    # Import lazily so UIBench still runs normally when the optional MCP SDK
    # has not been installed yet.
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    child_env = {
        key: os.environ[key]
        for key in (
            "PATH", "HOME", "USERPROFILE", "SystemRoot", "WINDIR",
            "COMSPEC", "PATHEXT", "TEMP", "TMP", "APPDATA", "LOCALAPPDATA",
            "SSL_CERT_FILE", "REQUESTS_CA_BUNDLE",
        )
        if key in os.environ
    }
    child_env["UNSPLASH_ACCESS_KEY"] = os.environ["UNSPLASH_ACCESS_KEY"]
    params = StdioServerParameters(
        command=str(_mcp_python()),
        args=[str(MCP_SERVER)],
        cwd=MCP_ROOT,
        env=child_env,
    )
    photos: list[dict[str, Any]] = []
    used_ids: set[str] = set()
    used_assets: set[str] = set()
    failures: list[str] = []
    with open(os.devnull, "w", encoding="utf-8") as errlog:
        async with asyncio.timeout(settings.image_tool_timeout):
            async with stdio_client(params, errlog=errlog) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    total = len(requests)
                    for index, request in enumerate(requests):
                        tool_args = {
                            key: value
                            for key, value in request.items()
                            if key not in {"slot"}
                        }
                        try:
                            result = await session.call_tool(
                                "search_photos", tool_args
                            )
                            payload = await _enrich_photo_metadata(
                                _parse_mcp_text(result)
                            )
                            candidates = _sanitize_photos(payload)
                        except Exception as exc:
                            # A single missing slot should not discard other
                            # successfully resolved assets in the batch.
                            failures.append(
                                f"{request['slot']}: {type(exc).__name__}: {exc}"
                            )
                            if progress is not None:
                                try:
                                    await progress(index + 1, total, request["slot"])
                                except Exception:
                                    pass
                            if _should_stop_image_batch(exc):
                                break
                            continue
                        if not one_per_slot:
                            photos.extend(candidates)
                        else:
                            selected = next(
                                (
                                    photo for photo in candidates
                                    if (
                                        str(photo.get("id") or "") not in used_ids
                                        and not (
                                            {
                                                _canonical_image_asset(str(url))
                                                for name, url in (
                                                    photo.get("urls") or {}
                                                ).items()
                                                if name in {"small", "regular"}
                                                and url
                                            }
                                            & used_assets
                                        )
                                    )
                                ),
                                None,
                            )
                            if selected is not None:
                                selected = dict(selected)
                                selected["slot"] = request["slot"]
                                selected["query"] = request["query"]
                                selected_id = str(selected.get("id") or "")
                                if selected_id:
                                    used_ids.add(selected_id)
                                used_assets.update(
                                    _canonical_image_asset(str(url))
                                    for name, url in (
                                        selected.get("urls") or {}
                                    ).items()
                                    if name in {"small", "regular"} and url
                                )
                                photos.append(selected)
                        if progress is not None:
                            try:
                                await progress(index + 1, total, request["slot"])
                            except Exception:
                                pass
    if not photos and failures:
        raise ImageToolError(
            f"all {len(requests)} photo slots failed; first error: {failures[0]}"
        )
    if not photos and requests:
        raise ImageToolError(
            f"Unsplash returned no safe photos for {len(requests)} requested slots"
        )
    return photos


def image_tool_result_for_model(photos: list[dict[str, Any]]) -> str:
    """Serialize only fields the model may embed; keep tracking URLs private."""
    public_photos = [
        {key: value for key, value in photo.items() if key != "download_location"}
        for photo in photos
    ]
    return json.dumps(
        {
            "photos": public_photos,
            "usage_rules": [
                "Use only a returned urls.regular or urls.small URL; never invent a URL.",
                "Each photo.slot is the exact page slot it belongs to; do not swap unrelated assets.",
                "If a returned slot represents a visible product/content card, render its photo in that card instead of an icon or empty placeholder.",
                "If no photo fits, use a token-controlled placeholder instead.",
            ],
        },
        ensure_ascii=False,
    )


async def track_used_photos(photos: list[dict[str, Any]], html: str) -> int:
    """Notify Unsplash only for MCP photos actually embedded in final HTML."""
    key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not key or not html:
        return 0
    rendered_urls = image_resource_urls(html)
    locations = []
    for photo in photos:
        urls = photo.get("urls") or {}
        if any(url and url in rendered_urls for url in urls.values()):
            location = str(photo.get("download_location") or "")
            if location and location not in locations:
                locations.append(location)
    if not locations:
        return 0
    headers = {"Authorization": f"Client-ID {key}", "Accept-Version": "v1"}
    tracked = 0
    async with httpx.AsyncClient(timeout=20.0) as client:
        for location in locations:
            try:
                response = await client.get(location, headers=headers)
                response.raise_for_status()
                tracked += 1
            except httpx.HTTPError:
                # Tracking failure should not discard an otherwise valid UI.
                pass
    return tracked
