"""UIBench - one prompt, many models, side-by-side mobile UI comparison.

Run with:  python app.py
Then open: http://127.0.0.1:8000

Results are streamed (NDJSON): each model's card appears the moment that
model finishes, instead of the page waiting for every model to complete.
Each model's reasoning (thinking process) + raw output is archived to
logs/<run_id>/<key>_<name>.md and viewable via an in-page modal.
"""
from __future__ import annotations

import asyncio
import json
import re
import time
from collections.abc import Awaitable, Callable
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    Response,
    StreamingResponse,
)
from fastapi.staticfiles import StaticFiles
from langchain_core.messages import HumanMessage

from config import settings
from uibench.arkui import (
    analyze_component_metadata,
    repair_missing_component_node_ids,
)
from uibench.arkui.exporter import (
    ArkUiExporterError,
    export_annotated_html,
    export_generic_html,
)
from uibench.arkui.hm_symbol_web import (
    HM_TEXT_FONTS,
    hm_fonts_css,
    hm_symbol_shim_js,
    inject_hm_fonts_link,
)
from uibench.arkui.symbols import HM_SYMBOL_FONT_FILE, hm_symbol_manifest
from uibench.design_tokens import (
    DEFAULT_TOKEN_THEME,
    inject_design_tokens,
    load_tokens,
    render_token_css,
)
from uibench.models import chat_model_for, load_model_registry
from uibench.image_tools import (
    IMAGE_SEARCH_TOOL,
    approved_image_urls,
    call_image_search_batch,
    distinct_used_photos,
    image_resource_urls,
    image_tool_available,
    image_tool_result_for_model,
    image_tool_unavailable_reason,
    image_search_requests,
    resolve_image_source,
    track_used_photos,
    unresolved_image_bindings,
)
from uibench.local_gallery import GALLERY_DIR
from uibench.pc import inject_pc_bootstrap
from uibench.prompts import prompt_for
from uibench.schemas import (
    ArkUiExportRequest,
    GenerateRequest,
    GenerationResult,
    ModelConfig,
)

app = FastAPI(title="UIBench", version="0.5.0")


class _CorsStaticFiles(StaticFiles):
    """Static files readable from the sandboxed, opaque-origin capture iframe.

    The ArkUI snapshot iframe has no allow-same-origin, so even a /gallery
    path is a cross-origin fetch for it. Without these headers the exporter
    silently drops every photo and ships a project with no media.
    """

    def file_response(self, *args, **kwargs):
        response = super().file_response(*args, **kwargs)
        response.headers.update(_GALLERY_CORS)
        return response


_GALLERY_CORS = {"Access-Control-Allow-Origin": "*"}
# The offline photo gallery (assets/gallery) renders inside srcdoc iframes via
# same-origin /gallery/... URLs. check_dir=False lets the server start before
# tools/build_gallery.py has been run for the first time.
app.mount(
    "/gallery",
    _CorsStaticFiles(directory=GALLERY_DIR, check_dir=False),
    name="gallery",
)

PROJECT_ROOT = Path(__file__).resolve().parent
LOGS_DIR = PROJECT_ROOT / "logs"

_FENCE_RE = re.compile(r"```(?:\w+)?\s*\n(.*?)```", re.DOTALL)
_HTML_FENCE_RE = re.compile(r"```(?:html|htm)?\s*\n(.*?)```", re.IGNORECASE | re.DOTALL)
_HTML_START_RE = re.compile(r"<!doctype\s+html\b|<html\b", re.IGNORECASE)
_THINK_RE = re.compile(r"<think>(.*?)</think>", re.DOTALL)
_PRODUCT_PHOTO_RE = re.compile(
    r"商城|商品|电商|购物|店铺|货架|"
    r"\b(?:product|products|e-?commerce|shopping|storefront|catalog)\b",
    re.IGNORECASE,
)
_VISUAL_PHOTO_RE = re.compile(
    r"餐厅|菜单|菜品|酒店|民宿|旅行|旅游|景点|房产|楼盘|画廊|图库|相册|作品集|摄影集|摄影|"
    r"肖像|人像|"
    r"新闻|社交|电影|短视频|封面|海边|度假|"
    r"\b(?:restaurant|food|hotel|travel|tourism|real estate|portfolio|photo|"
    r"news|social|movie|video|gallery|resort|beach|hero|banner)\b",
    re.IGNORECASE,
)
_GALLERY_PHOTO_RE = re.compile(
    r"画廊|图库|相册|摄影集|\b(?:gallery|photo\s*gallery|portfolio)\b",
    re.IGNORECASE,
)
_PHOTO_COUNT_RE = re.compile(
    r"(?:(\d+)|([一二三四五六七八]))\s*张\s*(?:肖像图|肖像|人像|照片|图片|图)?|"
    r"\b(\d+)\s*(?:images?|photos?|portraits?)\b",
    re.IGNORECASE,
)
_NO_PHOTO_RE = re.compile(
    r"(?:不要(?:使用|用|放|包含)?|别(?:使用|用|放|包含)?|"
    r"不(?:使用|用|放|需要)|无需|禁止使用|去掉|移除)"
    r"(?:任何|真实|摄影|商品|远程|外部|Unsplash|\s)*"
    r"(?:图片|照片|摄影图|商品图)|"
    r"(?:纯文字|无图(?:版|模式|设计)?)|"
    r"\b(?:no|without)\s+(?:any\s+)?"
    r"(?:(?:remote|product|photographic)\s+)?(?:images?|photos?|photography)\b|"
    r"\b(?:do\s+not|don['’]?t)\s+(?:use|include|add|show)\s+"
    r"(?:any\s+)?(?:images?|photos?)\b",
    re.IGNORECASE,
)
_CHINESE_PHOTO_COUNTS = {
    "一": 1, "二": 2, "三": 3, "四": 4,
    "五": 5, "六": 6, "七": 7, "八": 8,
}

ProgressCallback = Callable[[str, str, float], Awaitable[None]]
ImageProgressCallback = Callable[[int, int, str], Awaitable[None]]


class RunImageBatchCache:
    """Deduplicate identical image batches across models in one run."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._tasks: dict[str, asyncio.Task[list[dict]]] = {}
        self._tracked_locations: set[str] = set()
        self._subscribers: dict[str, list[ImageProgressCallback]] = {}
        self._state: dict[str, tuple[int, int, str]] = {}

    async def _broadcast(
        self, key: str, completed: int, total: int, slot: str,
    ) -> None:
        async with self._lock:
            self._state[key] = (completed, total, slot)
            subscribers = list(self._subscribers.get(key, []))
        if subscribers:
            await asyncio.gather(
                *(callback(completed, total, slot) for callback in subscribers),
                return_exceptions=True,
            )

    async def search(
        self, requests: list[dict], *, max_requests: int,
        progress: ImageProgressCallback | None = None,
        source: str | None = None,
    ) -> list[dict]:
        key = json.dumps(
            {
                "requests": requests,
                "max_requests": max_requests,
                "source": resolve_image_source(source),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        state: tuple[int, int, str] | None = None
        async with self._lock:
            if progress is not None:
                self._subscribers.setdefault(key, []).append(progress)
                state = self._state.get(key)
            task = self._tasks.get(key)
            if task is None:
                task = asyncio.create_task(call_image_search_batch(
                    {"requests": requests},
                    max_requests=max_requests,
                    progress=lambda completed, total, slot: self._broadcast(
                        key, completed, total, slot
                    ),
                    source=source,
                ))
                self._tasks[key] = task
        if progress is not None and state is not None:
            await progress(*state)
        photos = await task
        return [dict(photo) for photo in photos]

    async def track(self, photos: list[dict], html: str) -> int:
        """Track each selected photo at most once per comparison run."""
        rendered_urls = image_resource_urls(html)
        pending: list[dict] = []
        async with self._lock:
            for photo in photos:
                urls = (photo.get("urls") or {}).values()
                if not any(url and url in rendered_urls for url in urls):
                    continue
                location = str(photo.get("download_location") or "")
                if not location or location in self._tracked_locations:
                    continue
                self._tracked_locations.add(location)
                pending.append(photo)
        if not pending:
            return 0
        return await track_used_photos(pending, html)

# Public CSS that gives the outer page, the modal, and every iframe a
# mobile-style scrollbar: native bar hidden, scrolling + momentum kept.
SHARED_CSS = """/* mobile-style scrollbars: hide native bar, keep scroll + momentum */
* { scrollbar-width: none; -ms-overflow-style: none; }
*::-webkit-scrollbar { width: 0; height: 0; display: none; }
html, body { -webkit-overflow-scrolling: touch; }
"""


def extract_html(raw: str) -> str:
    """Pull the HTML out of the raw model output.

    Tolerates a missing closing fence: when a model gets truncated
    (e.g. hits max_tokens) it often emits the opening ```html but never
    closes it. In that case we take everything after the opening fence.
    """
    if not raw:
        return ""
    raw = raw.strip()
    match = _FENCE_RE.search(raw)
    if match:
        return match.group(1).strip()
    match = re.search(r"```(?:html|htm|vue|jsx|tsx)?\s*\n(.*)$", raw, re.DOTALL)
    if match:
        return match.group(1).strip()
    return raw


def is_complete_html(html: str) -> bool:
    """Return whether a candidate is a complete renderable HTML document."""
    if not html:
        return False
    low = html.lower()
    return (
        "<html" in low
        and "</html>" in low
        and "<body" in low
        and "</body>" in low
    )


def extract_complete_html(raw: str) -> str:
    """Extract only a complete HTML document from prose or a code fence.

    A browser can auto-close truncated markup, but accepting it hides output
    budget failures and makes model comparisons misleading.  UIBench therefore
    requires explicit body/html closing tags before rendering a result.
    """
    if not raw:
        return ""

    for match in _HTML_FENCE_RE.finditer(raw):
        candidate = match.group(1).strip()
        if is_complete_html(candidate):
            return candidate

    start = _HTML_START_RE.search(raw)
    end = raw.lower().rfind("</html>")
    if start and end >= start.start():
        candidate = raw[start.start():end + len("</html>")].strip()
        if is_complete_html(candidate):
            return candidate
    return ""


def _select_complete_html(content: str, reasoning: str) -> tuple[str, str]:
    """Prefer final content, then accept complete HTML from reasoning."""
    html = extract_complete_html(content)
    if html:
        return html, "content"
    html = extract_complete_html(reasoning)
    if html:
        return html, "reasoning"
    return "", ""


def _as_text(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "".join(
            block.get("text", "")
            for block in value
            if isinstance(block, dict)
        )
    return "" if value is None else str(value)


def _read_field(value, name: str, default=None):
    if value is None:
        return default
    if isinstance(value, dict):
        return value.get(name, default)
    return getattr(value, name, default)


def _openai_response_parts(raw) -> tuple[str, str, str, dict[str, int]]:
    """Normalize content, reasoning, finish reason, and token usage."""
    choice = raw.choices[0]
    msg = choice.message
    content = _as_text(getattr(msg, "content", ""))
    reasoning = (
        getattr(msg, "reasoning_content", None)
        or (getattr(msg, "model_extra", None) or {}).get("reasoning_content")
        or ""
    )
    reasoning = _as_text(reasoning)
    finish_reason = str(getattr(choice, "finish_reason", None) or "")

    usage = getattr(raw, "usage", None)
    details = _read_field(usage, "completion_tokens_details")
    token_usage = {
        "prompt_tokens": int(_read_field(usage, "prompt_tokens", 0) or 0),
        "completion_tokens": int(_read_field(usage, "completion_tokens", 0) or 0),
        "reasoning_tokens": int(_read_field(details, "reasoning_tokens", 0) or 0),
    }
    return content, reasoning, finish_reason, token_usage


def _openai_tool_calls(raw) -> list:
    """Return assistant tool calls from an OpenAI-compatible response."""
    try:
        return list(getattr(raw.choices[0].message, "tool_calls", None) or [])
    except (AttributeError, IndexError, TypeError):
        return []


def _tool_call_payload(tool_call) -> dict:
    """Convert SDK/dict tool-call objects back into request JSON."""
    function = _read_field(tool_call, "function", {}) or {}
    return {
        "id": str(_read_field(tool_call, "id", "") or ""),
        "type": "function",
        "function": {
            "name": str(_read_field(function, "name", "") or ""),
            "arguments": str(_read_field(function, "arguments", "{}") or "{}"),
        },
    }


def _tooling_not_supported(exc: Exception) -> bool:
    """Identify only clear provider rejections so ordinary errors still surface."""
    text = str(exc).lower()
    mentions_tooling = "tool" in text or "function call" in text
    rejected = any(fragment in text for fragment in (
        "unsupported", "does not support", "not support", "unknown parameter",
        "unrecognized", "not allowed",
    ))
    return mentions_tooling and rejected


def _tool_choice_rejected(exc: Exception) -> bool:
    """Detect gateways that reject tool_choice="required" with a vague 400.

    The Ark coding gateway (e.g. Kimi) accepts tools with tool_choice="auto"
    but returns a generic InvalidParameter error for "required". Downgrading
    is safe: the application still enforces photo slots through the
    deterministic fallback plan when a model skips the tool call.
    """
    text = str(exc).lower()
    if "tool_choice" in text:
        return True
    return "invalid" in text and "parameter" in text


def _minimum_photo_slots(prompt_text: str) -> int:
    """Return an enforceable asset floor for prompts that visibly need photos."""
    if _NO_PHOTO_RE.search(prompt_text):
        return 0
    explicit = _explicit_photo_count(prompt_text)
    if explicit:
        return min(explicit, settings.image_tool_max_assets)
    if _PRODUCT_PHOTO_RE.search(prompt_text):
        return min(4, settings.image_tool_max_assets)
    if _GALLERY_PHOTO_RE.search(prompt_text):
        return min(6, settings.image_tool_max_assets)
    if _VISUAL_PHOTO_RE.search(prompt_text):
        return min(2, settings.image_tool_max_assets)
    return 0


def _explicit_photo_count(prompt_text: str) -> int:
    match = _PHOTO_COUNT_RE.search(prompt_text)
    if not match:
        return 0
    arabic = match.group(1) or match.group(3)
    if arabic:
        return max(1, min(8, int(arabic)))
    return _CHINESE_PHOTO_COUNTS.get(match.group(2) or "", 0)


def _has_named_photo_batch(arguments: dict, minimum: int) -> bool:
    requests = arguments.get("requests")
    if not isinstance(requests, list) or len(requests) < minimum:
        return False
    slots: list[str] = []
    for item in requests:
        if not isinstance(item, dict):
            return False
        slot = str(item.get("slot") or "").strip()
        query = str(item.get("query") or "").strip()
        if not slot or not query:
            return False
        slots.append(slot)
    return len(set(slots)) == len(slots)


def _fallback_photo_requests(
    prompt_text: str, mode: str, *, limit: int,
) -> list[dict[str, str]]:
    """Provide deterministic slots when a model ignores the batch contract."""
    explicit_count = _explicit_photo_count(prompt_text)
    query_seed = " ".join(prompt_text.split())[:120]
    if re.search(r"肖像|人像|\bportrait", prompt_text, re.I):
        portrait_queries = [
            "studio portrait person natural light",
            "editorial portrait person side lighting",
            "outdoor portrait person golden hour",
            "professional portrait person neutral background",
            "candid portrait person soft window light",
            "dramatic portrait person rim lighting",
            "environmental portrait person urban setting",
            "close up portrait person soft light",
        ]
        target = explicit_count or min(4, limit)
        requests = [
            {
                "slot": f"portrait-{index + 1}",
                "query": portrait_queries[index],
                "orientation": "portrait",
            }
            for index in range(min(target, len(portrait_queries)))
        ]
    elif _PRODUCT_PHOTO_RE.search(prompt_text):
        # Preserve the user's product semantics in the query.  Generic slot
        # names deliberately do not authorize rewriting card copy to a fixed
        # electronics catalog.
        query_seed = query_seed or "ecommerce products"
        requests = [
            {
                "slot": "hero-banner",
                "query": f"{query_seed} hero banner",
                "orientation": "landscape",
            },
            *[
                {
                    "slot": f"product-card-{index}",
                    "query": f"{query_seed} product photo {index}",
                    "orientation": "squarish",
                }
                for index in range(1, 6)
            ],
        ]
    elif _GALLERY_PHOTO_RE.search(prompt_text):
        query_seed = query_seed or "art gallery"
        requests = [
            {"slot": "hero-artwork", "query": f"{query_seed} hero artwork", "orientation": "landscape"},
            {"slot": "gallery-item-1", "query": f"{query_seed} artwork 1", "orientation": "squarish"},
            {"slot": "gallery-item-2", "query": f"{query_seed} artwork 2", "orientation": "squarish"},
            {"slot": "gallery-item-3", "query": f"{query_seed} artwork 3", "orientation": "portrait"},
            {"slot": "gallery-item-4", "query": f"{query_seed} artwork 4", "orientation": "squarish"},
            {"slot": "gallery-item-5", "query": f"{query_seed} artwork 5", "orientation": "squarish"},
        ]
    elif re.search(r"餐厅|菜单|菜品|\b(?:restaurant|food)\b", prompt_text, re.I):
        query_seed = query_seed or "restaurant food"
        requests = [
            {"slot": "hero", "query": f"{query_seed} hero", "orientation": "landscape"},
            {"slot": "content-card-1", "query": f"{query_seed} dish 1", "orientation": "squarish"},
            {"slot": "content-card-2", "query": f"{query_seed} dish 2", "orientation": "squarish"},
            {"slot": "content-card-3", "query": f"{query_seed} detail", "orientation": "squarish"},
        ]
    elif re.search(r"酒店|民宿|旅行|旅游|海边|度假|\b(?:hotel|travel|resort|beach)\b", prompt_text, re.I):
        query_seed = query_seed or "travel destination"
        requests = [
            {"slot": "hero", "query": f"{query_seed} hero", "orientation": "landscape"},
            {"slot": "content-card-1", "query": f"{query_seed} detail 1", "orientation": "squarish"},
            {"slot": "content-card-2", "query": f"{query_seed} detail 2", "orientation": "squarish"},
            {"slot": "content-card-3", "query": f"{query_seed} detail 3", "orientation": "squarish"},
        ]
    else:
        query_seed = query_seed or "editorial lifestyle"
        requests = [
            {"slot": "hero", "query": f"{query_seed} hero", "orientation": "landscape"},
            {"slot": "featured-card", "query": f"{query_seed} detail", "orientation": "squarish"},
        ]
    target = explicit_count or len(requests)
    max_count = max(1, min(8, limit, target))
    while len(requests) < max_count:
        index = len(requests) + 1
        seed = requests[-1] if requests else {
            "query": "editorial lifestyle photo",
            "orientation": "squarish",
        }
        requests.append({
            "slot": f"photo-{index}",
            "query": f"{seed['query']} alternative composition {index}",
            "orientation": seed.get("orientation", "squarish"),
        })
    bounded = requests[:max_count]
    if mode == "pc" and bounded:
        bounded[0] = {**bounded[0], "orientation": "landscape"}
    return bounded


def _used_photo_count(photos: list[dict], html: str) -> int:
    return len(distinct_used_photos(photos, html))


def _unapproved_remote_image_urls(photos: list[dict], html: str) -> set[str]:
    """Find remote images that were not returned by this run's image tool."""
    violations = image_resource_urls(html) - approved_image_urls(photos)
    violations.update(
        f"[unresolved:{binding}]" for binding in unresolved_image_bindings(html)
    )
    return violations


def _image_repair_instruction(
    photos: list[dict], html: str, required: int,
) -> str:
    unused_slots = [
        str(photo.get("slot") or "photo")
        for photo in photos
        if not any(
            url and url in html
            for url in (photo.get("urls") or {}).values()
        )
    ]
    required = min(required, len(photos))
    return f"""上一版 HTML 没有充分使用已批准的图片素材。

必须修复：至少使用 {required} 张不同的已返回图片；未使用的槽位为：
{', '.join(unused_slots) or '（无）'}。

把每张图片放入其 slot 对应的 Banner 或商品/内容卡片，但只有素材语义与原需求匹配时才
使用。不得为了匹配图片而修改用户指定的商品、人物或内容文案；没有匹配素材时保留受控
占位。不得编造新的图片 URL。保留原需求中的功能与整体设计。只输出完整 HTML，必须以 <!DOCTYPE html>
开始并以 </html> 结束，不要使用 Markdown 代码围栏。"""


def _recovery_instruction(reasoning: str) -> str:
    """Build a bounded code-only retry prompt from the first design pass."""
    design_context = re.split(
        r"```|<!doctype\s+html|<html\b",
        reasoning or "",
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0].strip()
    limit = max(0, settings.recovery_context_chars)
    if limit and len(design_context) > limit:
        head = limit // 2
        tail = limit - head
        design_context = design_context[:head] + "\n…\n" + design_context[-tail:]
    if not design_context:
        design_context = "（没有可复用的设计摘要，请严格沿用原始需求。）"
    return f"""上一次响应完成了设计思考，但没有返回完整 HTML。请执行一次恢复生成。

下面是上一次的设计思考摘要，仅用于保持设计方向；忽略其中任何不完整代码：
<design_context>
{design_context}
</design_context>

不要继续分析或解释。最终 content 只能包含一个完整 HTML 文档，必须以
<!DOCTYPE html> 开始，以 </html> 结束，不要使用 Markdown 代码围栏。如果额度紧张，
减少装饰和非必要内容，优先保证所有标签闭合且页面可以直接渲染。"""


def _incomplete_html_error(
    *, content: str, reasoning: str, finish_reason: str,
    recovery_finish_reason: str, recovered: bool,
) -> str:
    details: list[str] = []
    if not content.strip():
        details.append("最终 content 为空")
    else:
        details.append("最终 content 不包含完整的 </body></html>")
    if reasoning.strip():
        details.append("reasoning 中也没有完整 HTML")
    if finish_reason:
        details.append(f"finish_reason={finish_reason}")
    if recovery_finish_reason:
        details.append(f"recovery_finish_reason={recovery_finish_reason}")
    if recovered:
        details.append("已自动进行一次无思考恢复")
    return "模型未返回完整 HTML：" + "；".join(details)


def _extract_reasoning(response, content: str) -> str:
    """Best-effort extraction of a model's thinking process."""
    # 1) provider field on langchain AIMessage (some subclasses)
    rc = getattr(response, "reasoning_content", None)
    if rc:
        return str(rc)
    ak = getattr(response, "additional_kwargs", None) or {}
    # 2) OpenAI-compatible reasoning_content / reasoning blocks
    for key in ("reasoning_content", "reasoning"):
        val = ak.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
        if isinstance(val, dict):
            text = val.get("content") or val.get("text") or val.get("summary")
            if isinstance(text, str) and text.strip():
                return text.strip()
    rm = getattr(response, "response_metadata", None) or {}
    val = rm.get("reasoning_content") or rm.get("reasoning")
    if isinstance(val, str) and val.strip():
        return val.strip()
    # 3) <think>...</think> embedded in content (open-source compatible models)
    m = _THINK_RE.search(content or "")
    if m:
        return m.group(1).strip()
    return ""


def _safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("_") or "model"


def _write_log(run_id: str, key: str, model_cfg: ModelConfig, prompt_text: str,
               content: str, reasoning: str, html: str, elapsed: float,
               error: str | None, mode: str = "mobile", *,
               html_source: str = "", finish_reason: str = "",
               recovery_finish_reason: str = "", prompt_tokens: int = 0,
               completion_tokens: int = 0, reasoning_tokens: int = 0,
               recovered: bool = False, status: str = "success",
               image_tool_used: bool = False, image_required: int = 0,
               image_count: int = 0, image_used: int = 0,
               image_queries: list[str] | None = None,
               image_tracked: int = 0, image_repaired: bool = False,
               image_error: str = "",
               arkui_manifest: dict[str, object] | None = None) -> None:
    """Archive one model's full output to a markdown log file."""
    try:
        run_dir = LOGS_DIR / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        path = run_dir / f"{key}_{_safe_name(model_cfg.name or model_cfg.id)}.md"
        arkui_summary = (arkui_manifest or {}).get("summary", {})
        if not isinstance(arkui_summary, dict):
            arkui_summary = {}
        parts = [
            f"# {model_cfg.name or model_cfg.id}",
            f"- 模型: `{model_cfg.id}`  供应商: {model_cfg.provider}  端点: `{model_cfg.base_url or '默认'}`",
            f"- 模式: {mode}（{'PC端 antd+echarts' if mode == 'pc' else '移动端 Tailwind'}）",
            f"- 运行: `{run_id}`  卡片key: `{key}`",
            f"- 时间: {datetime.now().isoformat(timespec='seconds')}",
            f"- 耗时: {elapsed}s",
            f"- HTML 来源: `{html_source or '无'}`  自动恢复: `{'是' if recovered else '否'}`",
            f"- 结束原因: `{finish_reason or '未提供'}`"
            + (f"  恢复结束原因: `{recovery_finish_reason}`" if recovery_finish_reason else ""),
            f"- Token: prompt={prompt_tokens}  completion={completion_tokens}  reasoning={reasoning_tokens}",
            f"- 结果状态: `{status}`",
            f"- 图片工具: `{'已调用' if image_tool_used else '未调用'}`"
            f"  需要={image_required}  返回={image_count}  使用={image_used}"
            f"  已完成追踪={image_tracked}",
            f"- 图片搜索: {', '.join(image_queries or []) or '（无）'}",
            f"- 图片修复: `{'是' if image_repaired else '否'}`",
            f"- 图片错误: {image_error or '（无）'}",
            f"- ArkUI 元数据: components={sum((arkui_summary.get('componentCounts') or {}).values())}"
            f"  explicit={arkui_summary.get('explicitComponents', 0)}"
            f"  inferred={arkui_summary.get('inferredComponents', 0)}"
            f"  errors={arkui_summary.get('errors', 0)}"
            f"  warnings={arkui_summary.get('warnings', 0)}"
            f"  notices={arkui_summary.get('notices', 0)}",
            "",
            "## 用户需求",
            "",
            prompt_text,
            "",
            "## 思考过程",
            "",
            reasoning.strip() if reasoning else "（该模型未返回思考过程 / 无 reasoning_content）",
            "",
            "## 原始输出",
            "",
            content if content else "（无输出）",
            "",
            "## 提取的 HTML",
            "",
            "```html" if html else "",
            html if html else "（未能提取 HTML）",
            "```" if html else "",
            "",
        ]
        if arkui_manifest:
            parts += [
                "## ArkUI 组件 Manifest",
                "",
                "```json",
                json.dumps(arkui_manifest, ensure_ascii=False, indent=2),
                "```",
                "",
            ]
        if error:
            parts += ["> ⚠️ 生成异常:", "", f"```\n{error}\n```", ""]
        path.write_text("\n".join(parts), encoding="utf-8")
    except Exception:
        # logging must never break the response
        pass


def _write_last_run(run_id: str, prompt_text: str, keyed, results, total: float,
                    mode: str = "mobile",
                    arkui_export_enabled: bool = False) -> None:
    """Persist the full result set so a page refresh can restore it."""
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        payload = {
            "run_id": run_id,
            "prompt": prompt_text,
            "mode": mode,
            "arkui_export_enabled": arkui_export_enabled,
            "total_seconds": total,
            "models": [
                {"key": str(i), "model_id": m.id, "name": m.name or m.id, "provider": m.provider}
                for i, m in keyed
            ],
            "results": [r.model_dump(mode="json") for r in results],
        }
        text = json.dumps(payload, ensure_ascii=False, default=str)
        (LOGS_DIR / "last_run.json").write_text(text, encoding="utf-8")
        run_dir = LOGS_DIR / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "run.json").write_text(text, encoding="utf-8")
    except Exception:
        pass


async def _generate_one(model_cfg: ModelConfig, prompt_text: str,
                        key: str, run_id: str, mode: str = "mobile",
                        arkui_export_enabled: bool = False,
                        progress: ProgressCallback | None = None,
                        image_cache: RunImageBatchCache | None = None,
                        image_source: str = "",
                        ) -> GenerationResult:
    """Call one model (in a worker thread) and return its rendered result."""
    start = time.perf_counter()
    effective_image_source = resolve_image_source(image_source or None)

    async def report(stage: str, message: str) -> None:
        """Emit a safe lifecycle summary without exposing model reasoning."""
        if progress is None:
            return
        try:
            await progress(
                stage,
                message,
                round(time.perf_counter() - start, 2),
            )
        except Exception:
            # Progress reporting must never break a model comparison run.
            pass

    content = ""
    log_content = ""
    reasoning = ""
    html = ""
    html_source = ""
    finish_reason = ""
    recovery_finish_reason = ""
    prompt_tokens = 0
    completion_tokens = 0
    reasoning_tokens = 0
    recovered = False
    minimum_photo_slots = _minimum_photo_slots(prompt_text)
    image_tool_used = False
    image_photos: list[dict] = []
    image_queries: list[str] = []
    image_tracked = 0
    image_error = ""
    image_repaired = False
    arkui_manifest: dict[str, object] = {}

    async def resolve_image_requests(requests: list[dict]) -> str:
        """Resolve one bounded batch and update this model's image telemetry."""
        nonlocal image_error
        for request in requests:
            query = request["query"]
            if query not in image_queries:
                image_queries.append(query)

        result_text = json.dumps(
            {"photos": [], "error": "Image search was not available."},
            ensure_ascii=False,
        )
        if not requests:
            return result_text

        await report(
            "searching_images",
            f"正在搜索图片素材 0/{len(requests)}",
        )

        async def image_progress(
            completed: int, total: int, _slot: str,
        ) -> None:
            await report(
                "searching_images",
                f"正在搜索图片素材 {completed}/{total}",
            )

        try:
            if image_cache is not None:
                photos = await image_cache.search(
                    requests,
                    max_requests=settings.image_tool_max_assets,
                    progress=image_progress,
                    source=effective_image_source,
                )
            else:
                photos = await call_image_search_batch(
                    {"requests": requests},
                    max_requests=settings.image_tool_max_assets,
                    progress=image_progress,
                    source=effective_image_source,
                )
            image_photos.extend(photos)
            result_text = image_tool_result_for_model(photos)
            required_return = minimum_photo_slots or len(requests)
            if len(photos) < required_return:
                image_error = (
                    f"图片素材仅返回 {len(photos)}/{required_return} 张"
                )
        except Exception as exc:
            image_error = f"{type(exc).__name__}: {exc}"[:500]
            result_text = json.dumps(
                {
                    "photos": [],
                    "error": (
                        "Image search failed; use a token-controlled "
                        "placeholder."
                    ),
                },
                ensure_ascii=False,
            )
        return result_text

    try:
        await report("preparing", "正在准备模型请求")
        chat = chat_model_for(model_cfg)
        messages = prompt_for(
            mode,
            arkui_export_enabled=arkui_export_enabled,
        ).invoke({"prompt": prompt_text})
        images_available = image_tool_available(effective_image_source)
        if minimum_photo_slots and not images_available:
            image_error = image_tool_unavailable_reason(effective_image_source)
        await report("generating", "正在请求模型，等待生成")

        # For OpenAI-compatible models, call the underlying openai client
        # directly so we keep `reasoning_content` (langchain's ChatOpenAI
        # drops it). Still a single call per model.
        root_client = getattr(chat, "root_client", None)
        if model_cfg.provider == "openai" and root_client is not None:
            # langchain message types ("human"/"ai") must map to openai roles
            role_map = {"system": "system", "human": "user", "ai": "assistant",
                        "tool": "tool", "function": "function"}
            oai_messages = [
                {"role": role_map.get(m.type, m.type), "content": m.content}
                for m in messages.to_messages()
            ]
            kwargs: dict = {"model": model_cfg.id, "messages": oai_messages,
                            "temperature": settings.temperature}
            if settings.max_tokens is not None:
                kwargs["max_tokens"] = settings.max_tokens
            # DeepSeek thinking-mode strength (effort). None = API default.
            effort = model_cfg.reasoning_effort
            if effort == "none":
                kwargs["extra_body"] = {"thinking": {"type": "disabled"}}
            elif effort:
                kwargs["reasoning_effort"] = effort
                kwargs["extra_body"] = {"thinking": {"type": "enabled"}}
            if images_available:
                kwargs["tools"] = [IMAGE_SEARCH_TOOL]
                kwargs["tool_choice"] = (
                    "required" if minimum_photo_slots else "auto"
                )
            try:
                raw = await asyncio.to_thread(
                    root_client.chat.completions.create, **kwargs
                )
            except Exception as exc:
                # Some OpenAI-compatible providers implement chat completions
                # but not function calling, and some reject only
                # tool_choice="required". Fall back progressively for explicit
                # tooling rejections; authentication/network/model errors must
                # remain visible to the user.
                if (
                    kwargs.get("tool_choice") == "required"
                    and _tool_choice_rejected(exc)
                ):
                    kwargs["tool_choice"] = "auto"
                    try:
                        raw = await asyncio.to_thread(
                            root_client.chat.completions.create, **kwargs
                        )
                    except Exception as auto_exc:
                        if not _tooling_not_supported(auto_exc):
                            raise
                        kwargs.pop("tools", None)
                        kwargs.pop("tool_choice", None)
                        raw = await asyncio.to_thread(
                            root_client.chat.completions.create, **kwargs
                        )
                elif "tools" in kwargs and _tooling_not_supported(exc):
                    kwargs.pop("tools", None)
                    kwargs.pop("tool_choice", None)
                    raw = await asyncio.to_thread(
                        root_client.chat.completions.create, **kwargs
                    )
                else:
                    raise

            generation_messages = list(oai_messages)
            await report("processing", "已收到模型响应，正在整理 HTML")
            content, reasoning, finish_reason, usage = _openai_response_parts(raw)
            prompt_tokens += usage["prompt_tokens"]
            completion_tokens += usage["completion_tokens"]
            reasoning_tokens += usage["reasoning_tokens"]

            tool_calls = _openai_tool_calls(raw)
            if tool_calls or (minimum_photo_slots and images_available):
                image_tool_used = True
                await report("searching_images", "正在规划图片素材")
                tool_payloads = [_tool_call_payload(call) for call in tool_calls]
                for index, payload in enumerate(tool_payloads):
                    if not payload["id"]:
                        payload["id"] = f"image-call-{index}"
                selected_payload = next(
                    (
                        payload for payload in tool_payloads
                        if payload["function"]["name"] == "search_photos"
                    ),
                    None,
                )
                arguments: dict = {}
                if selected_payload is not None:
                    try:
                        parsed = json.loads(
                            selected_payload["function"]["arguments"] or "{}"
                        )
                        if isinstance(parsed, dict):
                            arguments = parsed
                    except (TypeError, ValueError, json.JSONDecodeError):
                        arguments = {}

                # Tool schemas are advisory on several OpenAI-compatible
                # providers. Enforce a useful batch in the application when a
                # model sends one legacy broad query or too few named slots.
                # Every model in a comparison run uses the same deterministic
                # plan for required photography. This makes the run-level cache
                # effective and avoids multiplying image-source requests by
                # the number of models.
                planned_requests: list[dict] = []
                try:
                    planned_requests = image_search_requests(
                        arguments,
                        max_requests=settings.image_tool_max_assets,
                    )
                except Exception:
                    planned_requests = []
                if (
                    minimum_photo_slots
                    and not _has_named_photo_batch(arguments, minimum_photo_slots)
                ):
                    requests = _fallback_photo_requests(
                        prompt_text,
                        mode,
                        limit=minimum_photo_slots,
                    )
                else:
                    requests = planned_requests

                result_text = await resolve_image_requests(requests)

                if tool_payloads:
                    assistant_message = {
                        "role": "assistant",
                        "content": content or None,
                        "tool_calls": tool_payloads,
                    }
                    tool_messages = [
                        {
                            "role": "tool",
                            "tool_call_id": payload["id"],
                            "content": (
                                result_text
                                if payload is selected_payload
                                else json.dumps(
                                    {
                                        "photos": [],
                                        "error": "This tool call was not executed.",
                                    },
                                    ensure_ascii=False,
                                )
                            ),
                        }
                        for payload in tool_payloads
                    ]
                    generation_messages = [
                        *oai_messages,
                        assistant_message,
                        *tool_messages,
                    ]
                else:
                    generation_messages = [
                        *oai_messages,
                        {"role": "assistant", "content": content or ""},
                        {
                            "role": "user",
                            "content": (
                                "请使用下面这份经过批准的图片素材库重新生成完整 HTML。"
                                "每张图片必须用于其 slot 对应的可见区域；不得使用图标或"
                                "空色块代替已有素材，也不得编造 URL。\n\n"
                                + result_text
                            ),
                        },
                    ]
                final_kwargs = dict(kwargs)
                final_kwargs["messages"] = generation_messages
                if tool_payloads:
                    final_kwargs["tools"] = [IMAGE_SEARCH_TOOL]
                    final_kwargs["tool_choice"] = "none"
                else:
                    final_kwargs.pop("tools", None)
                    final_kwargs.pop("tool_choice", None)
                # The second generation is the longest phase of the run. Without
                # this the card would keep showing the image-search counter for
                # minutes and look frozen, which is worst with the local gallery
                # because its search finishes instantly.
                await report("generating", "图片已就绪，正在生成 HTML")
                try:
                    raw = await asyncio.to_thread(
                        root_client.chat.completions.create, **final_kwargs
                    )
                except Exception as exc:
                    if not _tooling_not_supported(exc):
                        raise
                    final_kwargs.pop("tools", None)
                    final_kwargs.pop("tool_choice", None)
                    raw = await asyncio.to_thread(
                        root_client.chat.completions.create, **final_kwargs
                    )
                await report("processing", "已收到模型响应，正在整理 HTML")
                final_content, final_reasoning, finish_reason, usage = (
                    _openai_response_parts(raw)
                )
                prompt_tokens += usage["prompt_tokens"]
                completion_tokens += usage["completion_tokens"]
                reasoning_tokens += usage["reasoning_tokens"]
                reasoning = "\n\n".join(
                    part for part in (
                        reasoning.strip(),
                        final_reasoning.strip(),
                    ) if part
                )
                content = final_content
                kwargs = final_kwargs

            log_content = content
            html, html_source = _select_complete_html(content, reasoning)

            # Thinking models can consume their entire completion budget before
            # producing final content.  Retry once with thinking disabled, using
            # a bounded excerpt of the first pass as design context.
            if not html and settings.recover_incomplete_html:
                recovered = True
                await report("recovering", "正在生成 HTML 代码")
                primary_content = content
                primary_reasoning = reasoning
                recovery_kwargs = dict(kwargs)
                recovery_kwargs["messages"] = [
                    *generation_messages,
                    {"role": "user", "content": _recovery_instruction(primary_reasoning)},
                ]
                recovery_kwargs.pop("tools", None)
                recovery_kwargs.pop("tool_choice", None)
                recovery_kwargs.pop("reasoning_effort", None)
                extra_body = dict(recovery_kwargs.get("extra_body") or {})
                extra_body["thinking"] = {"type": "disabled"}
                recovery_kwargs["extra_body"] = extra_body

                recovery_raw = await asyncio.to_thread(
                    root_client.chat.completions.create, **recovery_kwargs
                )
                await report("processing", "已收到补全结果，正在校验 HTML")
                recovery_content, recovery_reasoning, recovery_finish_reason, recovery_usage = (
                    _openai_response_parts(recovery_raw)
                )
                prompt_tokens += recovery_usage["prompt_tokens"]
                completion_tokens += recovery_usage["completion_tokens"]
                reasoning_tokens += recovery_usage["reasoning_tokens"]

                content = recovery_content
                reasoning_parts = [primary_reasoning.strip()]
                if recovery_reasoning.strip():
                    reasoning_parts.append(
                        "[自动恢复调用的 reasoning]\n" + recovery_reasoning.strip()
                    )
                reasoning = "\n\n".join(part for part in reasoning_parts if part)
                log_content = (
                    "[首次正文（可能为空或不完整）]\n"
                    + (primary_content or "（无输出）")
                    + "\n\n[自动恢复正文]\n"
                    + (recovery_content or "（无输出）")
                )
                html, recovery_source = _select_complete_html(
                    recovery_content, recovery_reasoning
                )
                if html:
                    html_source = f"recovery-{recovery_source}"

            repair_photo_use = min(
                minimum_photo_slots,
                len(image_photos),
            )
            current_photo_use = _used_photo_count(image_photos, html)
            if (
                html
                and repair_photo_use
                and current_photo_use < repair_photo_use
            ):
                await report("processing", "图片使用不足，正在修复商品卡素材")
                repair_kwargs = dict(kwargs)
                repair_kwargs["messages"] = [
                    *generation_messages,
                    {"role": "assistant", "content": content},
                    {
                        "role": "user",
                        "content": _image_repair_instruction(
                            image_photos, html, repair_photo_use
                        ),
                    },
                ]
                repair_kwargs.pop("tools", None)
                repair_kwargs.pop("tool_choice", None)
                repair_kwargs.pop("reasoning_effort", None)
                repair_extra_body = dict(repair_kwargs.get("extra_body") or {})
                repair_extra_body["thinking"] = {"type": "disabled"}
                repair_kwargs["extra_body"] = repair_extra_body
                repair_raw = await asyncio.to_thread(
                    root_client.chat.completions.create, **repair_kwargs
                )
                (
                    repair_content,
                    repair_reasoning,
                    repair_finish_reason,
                    repair_usage,
                ) = _openai_response_parts(repair_raw)
                prompt_tokens += repair_usage["prompt_tokens"]
                completion_tokens += repair_usage["completion_tokens"]
                reasoning_tokens += repair_usage["reasoning_tokens"]
                repair_html, repair_source = _select_complete_html(
                    repair_content, repair_reasoning
                )
                if (
                    repair_html
                    and _used_photo_count(image_photos, repair_html)
                    > current_photo_use
                ):
                    image_repaired = True
                    previous_content = content
                    content = repair_content
                    html = repair_html
                    html_source = f"image-repair-{repair_source}"
                    finish_reason = repair_finish_reason or finish_reason
                    if repair_reasoning.strip():
                        reasoning = "\n\n".join(
                            part for part in (
                                reasoning.strip(),
                                "[图片修复调用的 reasoning]\n"
                                + repair_reasoning.strip(),
                            ) if part
                        )
                    log_content = (
                        "[图片修复前正文]\n"
                        + (previous_content or "（无输出）")
                        + "\n\n[图片修复后正文]\n"
                        + (repair_content or "（无输出）")
                    )
        else:
            invoke_messages = messages
            if minimum_photo_slots and images_available:
                image_tool_used = True
                await report("searching_images", "正在规划图片素材")
                requests = _fallback_photo_requests(
                    prompt_text,
                    mode,
                    limit=minimum_photo_slots,
                )
                result_text = await resolve_image_requests(requests)
                invoke_messages = [
                    *messages.to_messages(),
                    HumanMessage(content=(
                        "请使用下面这份经过批准的图片素材库生成完整 HTML。"
                        "每张图片只能用于语义匹配的 slot；不得为了匹配素材改写用户"
                        "指定的内容，不得编造 URL；没有匹配素材时使用受控占位。\n\n"
                        + result_text
                    )),
                ]
                await report("generating", "图片已就绪，正在生成 HTML")
            response = await asyncio.to_thread(chat.invoke, invoke_messages)
            await report("processing", "已收到模型响应，正在整理 HTML")
            content = _as_text(getattr(response, "content", str(response)))
            reasoning = _extract_reasoning(response, content)
            log_content = content
            html, html_source = _select_complete_html(content, reasoning)

        elapsed = time.perf_counter() - start
        if not reasoning:
            reasoning = _extract_reasoning(None, content)
        error = None
        if mode == "mobile" and arkui_export_enabled and html:
            # Repair before the HTML reaches either the preview iframe or the
            # manifest. The later browser snapshot and backend export then see
            # the exact same deterministic node IDs.
            html = repair_missing_component_node_ids(html)
        image_used = _used_photo_count(image_photos, html)
        unapproved_images = _unapproved_remote_image_urls(image_photos, html)
        if html and unapproved_images:
            image_error = (
                "模型使用了未经图片工具批准的远程图片，已继续预览"
                f"（{len(unapproved_images)} 个 URL）"
            )
        elif not html:
            error = _incomplete_html_error(
                content=content,
                reasoning=reasoning,
                finish_reason=finish_reason,
                recovery_finish_reason=recovery_finish_reason,
                recovered=recovered,
            )
        if mode == "mobile" and arkui_export_enabled and html:
            arkui_manifest = analyze_component_metadata(html).to_manifest()
        if error is None and minimum_photo_slots:
            if len(image_photos) < minimum_photo_slots:
                shortage = (
                    f"图片素材不足：返回 {len(image_photos)}/"
                    f"{minimum_photo_slots} 张"
                )
                if shortage not in image_error:
                    image_error = "; ".join(
                        part for part in (image_error, shortage) if part
                    )[:500]
            elif image_used < minimum_photo_slots:
                shortage = (
                    f"图片使用不足：使用 {image_used}/"
                    f"{minimum_photo_slots} 张"
                )
                if shortage not in image_error:
                    image_error = "; ".join(
                        part for part in (image_error, shortage) if part
                    )[:500]
        elif error is None and image_photos and image_used < len(image_photos):
            shortage = (
                f"图片使用不足：使用 {image_used}/{len(image_photos)} 张"
            )
            if shortage not in image_error:
                image_error = "; ".join(
                    part for part in (image_error, shortage) if part
                )[:500]

        if error is None and html and image_photos:
            if image_cache is not None:
                image_tracked = await image_cache.track(image_photos, html)
            else:
                image_tracked = await track_used_photos(image_photos, html)

        status = (
            "failed" if error is not None
            else "degraded" if image_error
            else "success"
        )
        await report(
            "finalizing",
            "HTML 已整理，正在生成预览" if html else "正在整理生成结果",
        )
        _write_log(run_id, key, model_cfg, prompt_text, log_content or content, reasoning,
                   html, round(elapsed, 2), error, mode,
                   html_source=html_source, finish_reason=finish_reason,
                   recovery_finish_reason=recovery_finish_reason,
                   prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
                   reasoning_tokens=reasoning_tokens, recovered=recovered,
                   status=status, image_required=minimum_photo_slots,
                   image_tool_used=image_tool_used,
                   image_count=len(image_photos), image_used=image_used,
                   image_queries=image_queries,
                   image_tracked=image_tracked,
                   image_repaired=image_repaired, image_error=image_error,
                   arkui_manifest=arkui_manifest)
        return GenerationResult(
            key=key,
            model_id=model_cfg.id,
            name=model_cfg.name or model_cfg.id,
            provider=model_cfg.provider,
            mode=mode,
            html=html,
            reasoning=reasoning,
            html_source=html_source,
            finish_reason=finish_reason,
            recovery_finish_reason=recovery_finish_reason,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            reasoning_tokens=reasoning_tokens,
            recovered=recovered,
            status=status,
            image_tool_used=image_tool_used,
            image_required=minimum_photo_slots,
            image_count=len(image_photos),
            image_used=image_used,
            image_queries=image_queries,
            image_tracked=image_tracked,
            image_repaired=image_repaired,
            image_error=image_error,
            image_source=effective_image_source,
            arkui_export_enabled=(mode == "mobile" and arkui_export_enabled),
            arkui_manifest=arkui_manifest,
            log_url=f"/api/log/{run_id}/{key}",
            elapsed_seconds=round(elapsed, 2),
            error=error,
        )
    except Exception as exc:  # noqa: BLE001 - surface the error on the card
        await report("failed", "生成失败，正在整理错误信息")
        elapsed = round(time.perf_counter() - start, 2)
        _write_log(run_id, key, model_cfg, prompt_text, log_content or content,
                   reasoning, html, elapsed, str(exc), mode,
                   html_source=html_source, finish_reason=finish_reason,
                   recovery_finish_reason=recovery_finish_reason,
                   prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
                   reasoning_tokens=reasoning_tokens, recovered=recovered,
                   status="failed", image_required=minimum_photo_slots,
                   image_tool_used=image_tool_used,
                   image_count=len(image_photos), image_used=0,
                   image_queries=image_queries,
                   image_tracked=image_tracked,
                   image_repaired=image_repaired, image_error=image_error,
                   arkui_manifest=arkui_manifest)
        return GenerationResult(
            key=key,
            model_id=model_cfg.id,
            name=model_cfg.name or model_cfg.id,
            provider=model_cfg.provider,
            mode=mode,
            html=html,
            reasoning=reasoning,
            html_source=html_source,
            finish_reason=finish_reason,
            recovery_finish_reason=recovery_finish_reason,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            reasoning_tokens=reasoning_tokens,
            recovered=recovered,
            status="failed",
            image_tool_used=image_tool_used,
            image_required=minimum_photo_slots,
            image_count=len(image_photos),
            image_used=0,
            image_queries=image_queries,
            image_tracked=image_tracked,
            image_repaired=image_repaired,
            image_error=image_error,
            image_source=effective_image_source,
            arkui_export_enabled=(mode == "mobile" and arkui_export_enabled),
            arkui_manifest=arkui_manifest,
            log_url=f"/api/log/{run_id}/{key}",
            elapsed_seconds=elapsed,
            error=str(exc),
        )


@app.post("/api/generate")
async def generate(req: GenerateRequest):
    """Stream every enabled model's result as NDJSON (one JSON object per line).

    Line 1: {"type":"start","run_id":"...","models":[...]}
    Then:   {"type":"progress",...}              (safe lifecycle summaries)
            {"type":"result","result":{...}}   (one per model, in completion order)
    Last:   {"type":"done","total_seconds":...}
    """
    models = load_model_registry()
    if not models:
        return JSONResponse(
            {"error": "没有启用的模型，请在 config/models.yaml 中开启至少一个模型"},
            status_code=400,
        )

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    async def event_stream():
        start = time.perf_counter()
        keyed = list(enumerate(models))
        yield json.dumps(
            {
                "type": "start",
                "run_id": run_id,
                "models": [
                    {"key": str(i), "model_id": m.id, "name": m.name or m.id, "provider": m.provider}
                    for i, m in keyed
                ],
            },
            ensure_ascii=False,
        ) + "\n"

        queue: asyncio.Queue[dict] = asyncio.Queue()
        image_cache = RunImageBatchCache()

        async def worker(i: int, m: ModelConfig) -> None:
            key = str(i)

            async def progress(stage: str, message: str, elapsed: float) -> None:
                await queue.put({
                    "type": "progress",
                    "key": key,
                    "stage": stage,
                    "message": message,
                    "elapsed_seconds": elapsed,
                })

            result = await _generate_one(
                m,
                req.prompt,
                key,
                run_id,
                req.mode,
                req.arkui_export_enabled,
                progress=progress,
                image_cache=image_cache,
                image_source=req.image_source,
            )
            await queue.put({"type": "result", "result": result})

        tasks = [asyncio.create_task(worker(i, m)) for i, m in keyed]
        collected: list[GenerationResult] = []
        remaining = len(models)
        while remaining > 0:
            event = await queue.get()
            if event["type"] == "result":
                result = event["result"]
                remaining -= 1
                collected.append(result)
                payload = {
                    "type": "result",
                    "result": result.model_dump(mode="json"),
                }
            else:
                payload = event
            yield json.dumps(payload, ensure_ascii=False, default=str) + "\n"

        await asyncio.gather(*tasks)
        total = round(time.perf_counter() - start, 2)
        _write_last_run(
            run_id,
            req.prompt,
            keyed,
            collected,
            total,
            req.mode,
            req.arkui_export_enabled,
        )
        yield json.dumps(
            {"type": "done", "total_seconds": total},
            ensure_ascii=False,
        ) + "\n"

    return StreamingResponse(
        event_stream(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/last")
def last_run():
    """Return the most recent run's full result set (for page-refresh restore)."""
    p = LOGS_DIR / "last_run.json"
    if not p.exists():
        return JSONResponse({"error": "尚无运行记录"}, status_code=404)
    payload = json.loads(p.read_text(encoding="utf-8"))
    # Results written before image-policy telemetry may contain model-invented
    # remote image URLs. Keep their preview available and surface the condition
    # as a non-blocking image warning on restore.
    for raw_result in payload.get("results", []):
        if not isinstance(raw_result, dict):
            continue
        restored_html = str(raw_result.get("html") or "")
        result_mode = str(
            raw_result.get("mode") or payload.get("mode") or "mobile"
        )
        arkui_enabled = bool(
            raw_result.get("arkui_export_enabled")
            or payload.get("arkui_export_enabled")
            or raw_result.get("arkui_manifest")
        )
        if result_mode == "mobile" and arkui_enabled and restored_html:
            restored_html = repair_missing_component_node_ids(restored_html)
            raw_result["html"] = restored_html
            raw_result["arkui_manifest"] = analyze_component_metadata(
                restored_html
            ).to_manifest()
        if raw_result.get("status"):
            continue
        raw_result.setdefault("image_required", 0)
        raw_result.setdefault("image_used", raw_result.get("image_tracked", 0))
        remote_images = image_resource_urls(restored_html)
        unresolved_images = unresolved_image_bindings(restored_html)
        has_no_approved_batch = (
            not raw_result.get("image_tool_used")
            or int(raw_result.get("image_count") or 0) == 0
        )
        if unresolved_images or (remote_images and has_no_approved_batch):
            message = (
                "历史结果包含未经图片工具批准的远程图片，已继续预览"
            )
            raw_result["image_error"] = message
        if raw_result.get("error"):
            raw_result["status"] = "failed"
        elif raw_result.get("image_error"):
            raw_result["status"] = "degraded"
        else:
            raw_result["status"] = "success"
    return JSONResponse(payload)


@app.get("/api/log/{run_id}/{key}")
def get_log(run_id: str, key: str):
    """Return one model's archived markdown log."""
    run_dir = LOGS_DIR / run_id
    if not run_dir.is_dir():
        return JSONResponse({"error": "运行不存在"}, status_code=404)
    matches = list(run_dir.glob(f"{key}_*.md"))
    if not matches:
        return JSONResponse({"error": "日志不存在"}, status_code=404)
    text = matches[0].read_text(encoding="utf-8")
    return PlainTextResponse(text, media_type="text/plain; charset=utf-8")


@app.get("/shared.css", response_class=PlainTextResponse)
def shared_css():
    return PlainTextResponse(SHARED_CSS, media_type="text/css; charset=utf-8")


@app.get("/design-tokens.css", response_class=PlainTextResponse)
def design_tokens_css():
    """Serve the checked-in multi-system token contract as semantic CSS."""
    return PlainTextResponse(
        render_token_css(),
        media_type="text/css; charset=utf-8",
        headers={"Cache-Control": "no-store"},
    )


@app.get("/api/design-tokens")
def design_tokens():
    """Expose the versioned token document for inspectors and future editors."""
    return JSONResponse(load_tokens())


# The capture iframe is sandboxed without allow-same-origin, so its requests
# arrive from an opaque origin; fonts and fetch() both require CORS headers.
_HM_SYMBOL_CORS = {"Access-Control-Allow-Origin": "*"}


@app.get("/hm-symbol.js", response_class=PlainTextResponse)
def hm_symbol_shim():
    """Serve the createIcons-compatible shim that paints device glyphs."""
    return PlainTextResponse(
        hm_symbol_shim_js(),
        media_type="text/javascript; charset=utf-8",
        headers=_HM_SYMBOL_CORS,
    )


@app.get("/hm-symbol/manifest.json")
def hm_symbol_manifest_json():
    """Classify every renderable data-lucide value with its device glyph."""
    return JSONResponse(
        hm_symbol_manifest(),
        headers={**_HM_SYMBOL_CORS, "Cache-Control": "no-store"},
    )


def _serve_font_file(font_file):
    if not font_file.is_file():
        return JSONResponse(
            {
                "error": (
                    "HM 字体尚未提取；运行 "
                    "python tools/export-hm-symbol-assets.py"
                ),
            },
            status_code=404,
            headers=_HM_SYMBOL_CORS,
        )
    media_type = (
        "font/woff2" if font_file.suffix == ".woff2" else "font/ttf"
    )
    return Response(
        font_file.read_bytes(),
        media_type=media_type,
        headers={**_HM_SYMBOL_CORS, "Cache-Control": "max-age=3600"},
    )


@app.get("/hm-symbol/font.woff2")
def hm_symbol_font():
    """Serve the locally extracted symbol font; 404 keeps Lucide fallback."""
    return _serve_font_file(HM_SYMBOL_FONT_FILE)


@app.get("/hm-fonts.css", response_class=PlainTextResponse)
def hm_fonts_stylesheet():
    """Declare @font-face for extracted HarmonyOS text fonts (may be empty)."""
    return PlainTextResponse(
        hm_fonts_css(),
        media_type="text/css; charset=utf-8",
        headers={**_HM_SYMBOL_CORS, "Cache-Control": "no-store"},
    )


@app.get("/hm-fonts/{filename}")
def hm_text_font(filename: str):
    """Serve one locally extracted HarmonyOS text font by exact name."""
    if filename not in {name for _, name in HM_TEXT_FONTS}:
        return JSONResponse(
            {"error": "字体不存在或尚未提取"},
            status_code=404,
            headers=_HM_SYMBOL_CORS,
        )
    return _serve_font_file(HM_SYMBOL_FONT_FILE.parent / filename)


@app.post("/api/arkui/export")
async def export_arkui(req: ArkUiExportRequest):
    """Export annotated or legacy HTML through the platform converter."""
    exporter = (
        export_annotated_html
        if req.mode == "annotated"
        else export_generic_html
    )
    export_options: dict[str, object] = {
        "page_name": req.page_name,
        "page_description": req.page_description,
        "viewport_width": req.viewport_width,
        "viewport_height": req.viewport_height,
        "snapshot": req.snapshot,
    }
    if req.mode == "annotated":
        # A downloadable annotated project must preserve the rendered visual
        # contract.  Structure-only conversion remains available to internal
        # callers through export_annotated_html(require_snapshot=False), but
        # the public delivery endpoint must never silently emit an unstyled
        # HarmonyOS project.
        export_options["require_snapshot"] = True
    try:
        result = await asyncio.to_thread(
            exporter,
            req.html,
            **export_options,
        )
    except ArkUiExporterError as exc:
        status_code = 422
        if exc.code in {
            "ARKUI_NODE_NOT_FOUND",
            "ARKUI_BRIDGE_NOT_FOUND",
            "ARKUI_BRIDGE_START_FAILED",
            "ARKUI_BRIDGE_FAILED",
        }:
            status_code = 503
        elif exc.code == "ARKUI_BRIDGE_TIMEOUT":
            status_code = 504
        return JSONResponse(
            {"error": exc.to_dict()},
            status_code=status_code,
        )
    return JSONResponse(result)


def inject_shared_css(html: str) -> str:
    """Inject a <link> to /shared.css into a model's HTML.

    Kept for reference/tests; the live injection (shared.css + PC babel
    classic-runtime bootstrap) happens in the frontend JS `injectForRender`.
    """
    link = '<link rel="stylesheet" href="/shared.css">'
    low = html.lower()
    idx = low.find("<head>")
    if idx != -1:
        at = idx + len("<head>")
        return html[:at] + link + html[at:]
    idx = low.find("<html")
    if idx != -1:
        at = low.find(">", idx)
        if at != -1:
            return html[:at + 1] + "<head>" + link + "</head>" + html[at + 1:]
    return link + html


def inject_for_render(
    html: str,
    mode: str = "mobile",
    theme: str = "light",
    token_theme: str = DEFAULT_TOKEN_THEME,
) -> str:
    """Apply shared assets, mobile tokens, and the PC runtime when needed."""
    html = inject_shared_css(html)
    if mode == "mobile":
        html = inject_design_tokens(html, theme, token_theme)
        html = inject_hm_fonts_link(html)
    else:
        html = inject_pc_bootstrap(html)
    return html


@app.get("/", response_class=HTMLResponse)
def index():
    return INDEX_HTML


# --------------------------------------------------------------------------- #
# Single-page UI (self-contained, no external assets)
# --------------------------------------------------------------------------- #
MOBILE_VIEWPORT_WIDTH = 390
MOBILE_VIEWPORT_HEIGHT = 844


INDEX_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>UIBench · 多模型移动端 UI 对比</title>
<style>
  :root {
    --bg: #0f1115; --panel: #1a1d24; --border: #2a2f3a;
    --text: #e6e8eb; --muted: #8b93a1; --accent: #4f8cff;
    --ok: #34d399; --err: #f87171; --time: #fbbf24;
  }
  * { box-sizing: border-box; scrollbar-width: none; -ms-overflow-style: none; }
  *::-webkit-scrollbar { width: 0; height: 0; display: none; }
  html, body { -webkit-overflow-scrolling: touch; }
  body { margin: 0; background: var(--bg); color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
      "Microsoft YaHei", sans-serif; }
  header { padding: 24px 24px 8px; max-width: 1400px; margin: 0 auto; }
  header h1 { margin: 0; font-size: 24px; letter-spacing: .5px; }
  header h1 span { color: var(--accent); }
  header .sub { color: var(--muted); margin: 6px 0 0; font-size: 14px; }
  main { max-width: 1400px; margin: 0 auto; padding: 0 24px 48px; }
  form { display: flex; gap: 12px; margin: 16px 0 8px; flex-wrap: wrap; }
  textarea { flex: 1; min-width: 280px; min-height: 52px; resize: vertical;
    background: var(--panel); border: 1px solid var(--border); color: var(--text);
    border-radius: 10px; padding: 14px 16px; font-size: 15px; outline: none; }
  textarea:focus { border-color: var(--accent); }
  button#btn { background: var(--accent); color: #fff; border: 0; border-radius: 10px;
    padding: 0 28px; font-size: 15px; font-weight: 600; cursor: pointer;
    transition: opacity .15s; }
  button#btn:hover { opacity: .9; }
  button#btn:disabled { opacity: .5; cursor: progress; }
  .meta { color: var(--muted); font-size: 13px; min-height: 18px; margin-bottom: 18px;
    display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
  .meta b { color: var(--text); }
  .meta-note { color: #667085; }
  .meta-pulse { width: 7px; height: 7px; border-radius: 50%; background: var(--accent);
    box-shadow: 0 0 0 0 rgba(79,140,255,.35); animation: softPulse 1.8s ease-out infinite; }
  .grid { display: grid; gap: 22px;
    /* 390px preview + 2x16px card padding + 2px card border. On narrow hosts
       the card may shrink, but the iframe itself keeps the canonical export
       viewport and the preview slot owns any horizontal scrolling. */
    grid-template-columns: repeat(auto-fill,
      minmax(min(calc(__UIBENCH_MOBILE_VIEWPORT_WIDTH__px + 34px), 100%), 1fr)); }
  .card { background: var(--panel); border: 1px solid var(--border);
    border-radius: 14px; overflow: hidden; display: flex; flex-direction: column; }
  .card-head { display: grid; grid-template-columns: minmax(0, 1fr) auto;
    align-items: center; gap: 5px 12px; padding: 10px 16px; }
  .titles { display: flex; align-items: center; gap: 10px; min-width: 0; }
  .name { font-weight: 600; font-size: 15px; white-space: nowrap;
    overflow: hidden; text-overflow: ellipsis; }
  .provider { font-size: 11px; color: var(--muted); background: #11141a;
    border: 1px solid var(--border); padding: 2px 8px; border-radius: 999px;
    text-transform: uppercase; letter-spacing: .5px; }
  .time { font-size: 13px; color: var(--time); font-variant-numeric: tabular-nums;
    white-space: nowrap; }
  .head-status { grid-column: 1 / -1; display: flex; align-items: center;
    gap: 8px; min-width: 0; }
  .head-status .stage-label { max-width: 100%; }
  .card-body { display: flex; flex-direction: column; align-items: center;
    padding: 16px; flex: 1; }
  .progress-panel { width: 100%; color: var(--muted); background: var(--panel);
    border-bottom: 1px solid var(--border); }
  .stage-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--accent);
    flex: 0 0 auto; box-shadow: 0 0 0 0 rgba(79,140,255,.3);
    animation: softPulse 1.8s ease-out infinite; }
  .stage-label { min-width: 0; color: var(--text); font-size: 13px; font-weight: 600;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .preview-slot { width: 100%; display: flex; flex-direction: column; align-items: center;
    overflow-x: auto; overflow-y: hidden; }
  .render-status { width: __UIBENCH_MOBILE_VIEWPORT_WIDTH__px; max-width: 100%; margin-bottom: 12px; padding: 9px 12px;
    border-radius: 9px; background: rgba(79,140,255,.08); color: #aabbd6;
    font-size: 12px; text-align: center; }
  .render-status.wide { width: 100%; }
  .card[data-state="completed"] .stage-dot { background: var(--ok); animation: none;
    box-shadow: none; }
  .card[data-state="degraded"] .stage-dot { background: var(--time); animation: none;
    box-shadow: none; }
  .card[data-state="failed"] .stage-dot,
  .card[data-state="interrupted"] .stage-dot { background: var(--err); animation: none;
    box-shadow: none; }
  .tools { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap;
    justify-content: center; }
  .tools button { background: #11141a; color: var(--muted); border: 1px solid var(--border);
    border-radius: 8px; padding: 5px 12px; font-size: 12px; cursor: pointer; }
  .tools button:hover { color: var(--text); border-color: var(--accent); }
  .tools button:disabled { opacity: .45; cursor: not-allowed; }
  .tools button.export-blocked { color: var(--err); border-color: rgba(255,107,107,.4); }
  .tools button.export-blocked:hover { color: var(--err); border-color: var(--err); }
  .phone { width: __UIBENCH_MOBILE_VIEWPORT_WIDTH__px; min-width: __UIBENCH_MOBILE_VIEWPORT_WIDTH__px; max-width: none;
    height: __UIBENCH_MOBILE_VIEWPORT_HEIGHT__px; border: 0;
    border-radius: 18px; background: #fff;
    box-shadow: 0 8px 30px rgba(0,0,0,.45); }
  @media (max-width: 520px) {
    .preview-slot { align-items: flex-start; }
    .preview-slot > .tools, .preview-slot > .render-status,
    .preview-slot > .skeleton, .preview-slot > .error { width: 100%; }
  }
  /* mode segmented control */
  .seg { display: inline-flex; border: 1px solid var(--border);
    border-radius: 10px; overflow: hidden; align-self: flex-start; }
  .seg button { background: transparent; color: var(--muted); border: 0;
    padding: 8px 16px; font-size: 14px; cursor: pointer; }
  .seg button + button { border-left: 1px solid var(--border); }
  .seg button.active { background: var(--accent); color: #fff; }
  .arkui-option { display: inline-flex; align-items: center; gap: 8px;
    align-self: flex-start; min-height: 36px; padding: 0 12px; border: 1px solid var(--border);
    border-radius: 10px; color: var(--muted); font-size: 13px; cursor: pointer; }
  .arkui-option input { accent-color: var(--accent); }
  .arkui-option.disabled { opacity: .45; cursor: not-allowed; }
  .seg.theme button.active { background: #344054; color: #fff; }
  .seg.token-theme button { padding-inline: 12px; }
  .seg.token-theme button[data-token-theme="harmonyos"].active { background: #0A59F7; color: #fff; }
  .seg.token-theme button[data-token-theme="spotify"].active { background: #1ED760; color: #000; }
  .seg.token-theme button[data-token-theme="netflix"].active { background: #E50914; color: #fff; }
  .seg.token-theme button[data-token-theme="notion"].active {
    background: #F7F6F3; color: #37352F; box-shadow: inset 0 0 0 1px #E3E2E0;
  }
  /* PC desktop preview (scaled to fit) */
  .pc-wrap { width: 100%; overflow: hidden; border-radius: 18px; background: #fff;
    box-shadow: 0 8px 30px rgba(0,0,0,.45); position: relative; }
  .pc-frame { width: 1920px; height: 1080px; border: 0; display: block;
    transform-origin: top left; background: #fff; }
  .error { color: var(--err); padding: 24px 16px; text-align: center;
    font-size: 14px; word-break: break-word; width: 100%; }
  .empty { color: var(--muted); padding: 48px 16px; text-align: center; width: 100%; }
  @keyframes shimmer { 0%{background-position:-400px 0} 100%{background-position:400px 0} }
  @keyframes softPulse { 70%,100% { box-shadow: 0 0 0 7px rgba(79,140,255,0); } }
  .skeleton { width: __UIBENCH_MOBILE_VIEWPORT_WIDTH__px; max-width: 100%; height: __UIBENCH_MOBILE_VIEWPORT_HEIGHT__px; border-radius: 18px;
    background: linear-gradient(90deg, #11141a 0px, #181d26 200px, #11141a 400px);
    background-size: 800px 100%; animation: shimmer 2.2s infinite ease-in-out; }
  .spin { display:inline-block; width:14px; height:14px; border:2px solid var(--muted);
    border-top-color:var(--accent); border-radius:50%; animation:rot .8s linear infinite;
    vertical-align:-2px; margin-right:6px; }
  @keyframes rot { to { transform: rotate(360deg); } }
  /* log modal */
  .overlay { position: fixed; inset: 0; background: rgba(0,0,0,.6);
    display: flex; align-items: center; justify-content: center; z-index: 50; }
  .modal { background: var(--panel); border: 1px solid var(--border);
    border-radius: 14px; width: min(900px, 92vw); height: min(80vh, 720px);
    display: flex; flex-direction: column; overflow: hidden; }
  .modal-head { display: flex; align-items: center; justify-content: space-between;
    padding: 12px 16px; border-bottom: 1px solid var(--border); gap: 10px; }
  .modal-head .m-title { font-weight: 600; font-size: 15px; white-space: nowrap;
    overflow: hidden; text-overflow: ellipsis; }
  .modal-head button { background: #11141a; color: var(--muted);
    border: 1px solid var(--border); border-radius: 8px; padding: 5px 12px;
    font-size: 12px; cursor: pointer; }
  .modal-head button:hover { color: var(--text); border-color: var(--accent); }
  .modal-body { flex: 1; overflow: auto; padding: 16px 20px; }
  .modal-body pre { margin: 0; white-space: pre-wrap; word-break: break-word;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 12.5px; line-height: 1.6; color: var(--text); }
  .modal-load { color: var(--muted); padding: 24px; text-align: center; }
  .modal-err { color: var(--err); padding: 24px; text-align: center; }
  /* lossy export details */
  .tools button.lossy-reasons { color: var(--time); border-color: rgba(251,191,36,.4); }
  .tools button.lossy-reasons:hover { color: var(--time); border-color: var(--time); }
  .diag-summary { margin: 0 0 14px; font-size: 13px; line-height: 1.7; color: var(--text); }
  .diag-note-head { margin: 18px 0 10px; font-size: 12.5px; color: var(--muted); }
  .diag-item { border: 1px solid var(--border); border-radius: 10px;
    padding: 10px 12px; margin-bottom: 10px; }
  .diag-title { display: flex; align-items: baseline; gap: 8px;
    font-size: 13px; line-height: 1.5; color: var(--text); }
  .diag-badge { flex: none; font-size: 11px; border-radius: 6px; padding: 1px 7px;
    border: 1px solid var(--border); color: var(--muted); }
  .diag-item.warning .diag-badge { color: var(--time); border-color: rgba(251,191,36,.5); }
  .diag-meta { margin-top: 5px; font-size: 11.5px; color: var(--muted); word-break: break-word;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
  @media (prefers-reduced-motion: reduce) {
    .spin, .skeleton, .stage-dot, .meta-pulse { animation: none !important; }
  }
</style>
</head>
<body>
<header>
  <h1>UI<span>Bench</span></h1>
  <p class="sub">输入一句话的移动端 UI 需求，并行调用多个模型，同屏渲染对比并显示每个模型耗时</p>
</header>
<main>
  <form id="form">
    <div class="seg" id="mode">
      <button type="button" data-mode="mobile">移动端</button>
      <button type="button" data-mode="pc" class="active">PC 端</button>
    </div>
    <div class="seg theme" id="theme" aria-label="移动端预览主题">
      <button type="button" data-theme="light" class="active">白天</button>
      <button type="button" data-theme="dark">黑夜</button>
    </div>
    <div class="seg token-theme" id="token-theme" aria-label="移动端设计体系">
      <button type="button" data-token-theme="harmonyos" class="active">HarmonyOS</button>
      <button type="button" data-token-theme="spotify">Spotify</button>
      <button type="button" data-token-theme="netflix">Netflix</button>
      <button type="button" data-token-theme="notion">Notion</button>
    </div>
    <div class="seg hm-symbol" id="hm-symbol-mode" aria-label="移动端图标渲染">
      <button type="button" data-hm-symbol="lucide" class="active">Lucide 图标</button>
      <button type="button" data-hm-symbol="harmony">鸿蒙图标</button>
    </div>
    <div class="seg image-source" id="image-source" aria-label="图片来源">
      <button type="button" data-image-source="local" class="active"
        title="从本地图库取图：毫秒级、可复现、无外网依赖">离线图库</button>
      <button type="button" data-image-source="unsplash"
        title="实时搜索 Unsplash：更贴合需求，但依赖网络与 API 配额">在线搜索</button>
    </div>
    <label class="arkui-option" id="arkui-option">
      <input id="arkui-export" type="checkbox">
      生成 ArkUI 可导出元数据
    </label>
    <textarea id="prompt" placeholder="例如：移动端→带顶部搜索框、商品轮播图和底部 Tab 导航的电商首页；PC 端→带侧边菜单、统计卡和销售趋势折线图的后台仪表盘"></textarea>
    <button id="btn" type="submit">生成对比</button>
  </form>
  <div id="meta" class="meta" role="status" aria-live="polite" aria-atomic="true"></div>
  <div id="results" class="grid" aria-busy="false"></div>
</main>
<div id="modal-root"></div>
<script>
const form = document.getElementById('form');
const btn = document.getElementById('btn');
const promptEl = document.getElementById('prompt');
const resultsEl = document.getElementById('results');
const metaEl = document.getElementById('meta');
const modalRoot = document.getElementById('modal-root');
const modeEl = document.getElementById('mode');
const themeEl = document.getElementById('theme');
const tokenThemeEl = document.getElementById('token-theme');
const hmSymbolModeEl = document.getElementById('hm-symbol-mode');
const imageSourceEl = document.getElementById('image-source');
const arkuiOptionEl = document.getElementById('arkui-option');
const arkuiExportEl = document.getElementById('arkui-export');

let count = 0, done = 0, successCount = 0, degradedCount = 0, failureCount = 0;
let sawStreamDone = true;
let requestSerial = 0;
let currentMode = 'mobile';
let currentTheme = localStorage.getItem('uibench-preview-theme') === 'dark' ? 'dark' : 'light';
const tokenThemes = ['harmonyos', 'spotify', 'netflix', 'notion'];
const savedTokenTheme = localStorage.getItem('uibench-preview-token-theme');
let currentTokenTheme = tokenThemes.includes(savedTokenTheme) ? savedTokenTheme : 'harmonyos';
// Preview icon rendering: Lucide keeps the benchmark look; the HarmonyOS
// mode paints the exact device glyphs the export will produce. Snapshot
// capture always forces the HarmonyOS mode regardless of this toggle.
let hmSymbolPreview = localStorage.getItem('uibench-preview-hm-symbol') === 'harmony';
// Photo source toggle: offline gallery (default) vs live Unsplash search.
// Falls back to the server-configured default until the user picks one.
const imageSources = ['local', 'unsplash'];
const savedImageSource = localStorage.getItem('uibench-image-source');
let currentImageSource = imageSources.includes(savedImageSource)
  ? savedImageSource
  : ('__UIBENCH_IMAGE_SOURCE__' === 'unsplash' ? 'unsplash' : 'local');
function setImageSource(source) {
  currentImageSource = source;
  localStorage.setItem('uibench-image-source', source);
  imageSourceEl.querySelectorAll('button').forEach(b => {
    b.classList.toggle('active', b.dataset.imageSource === source);
  });
}
imageSourceEl.querySelectorAll('button').forEach(b => {
  b.addEventListener('click', () => setImageSource(b.dataset.imageSource));
});
setImageSource(currentImageSource);
const pcFrames = [];  // [{wrap, iframe}] to rescale on resize
const previewFrames = [];  // mobile frames rerendered when mode/design system changes
const cardTimers = new Map();
const renderTimers = new Map();
let timerId = null;

const stageLabels = {
  queued: '等待开始',
  preparing: '正在准备请求',
  generating: '正在等待模型响应',
  searching_images: '正在搜索图片素材',
  processing: '正在校验页面完整性',
  recovering: '正在生成 HTML 代码',
  finalizing: '正在整理结果',
  rendering: '正在加载预览',
  completed: '预览已就绪',
  degraded: '预览已显示 · 图片异常',
  failed: '生成失败',
  interrupted: '连接已中断'
};

function formatSeconds(seconds) {
  const value = Math.max(0, Number(seconds) || 0);
  return value.toFixed(1) + 's';
}

function resultTimeSuffix(result) {
  const parts = [];
  const sourceLabel = result.image_source === 'unsplash' ? '在线' : '本地';
  if (Number(result.image_required) > 0) {
    parts.push(sourceLabel + '图片 ' + Number(result.image_used || 0) + '/' + Number(result.image_required));
  } else if (Number(result.image_count) > 0) {
    parts.push(sourceLabel + '图片 ' + result.image_count + ' 张');
  }
  if (result.image_repaired) parts.push('图片已修复');
  if (result.image_error) parts.push('图片检索失败');
  if (result.recovered) parts.push('自动恢复');
  if (result.html_source === 'reasoning') parts.push('reasoning 兜底');
  return parts.length ? ' · ' + parts.join(' · ') : '';
}

function setCardTotal(card, seconds, result = {}) {
  const value = Math.max(0, Number(seconds) || 0);
  card.dataset.totalElapsed = String(value);
  const headTime = card.querySelector('.time');
  if (headTime) headTime.textContent = '⏱ ' + formatSeconds(value) + resultTimeSuffix(result);
}

function cardForKey(key) {
  for (const card of resultsEl.querySelectorAll('.card')) {
    if (card.dataset.key === String(key)) return card;
  }
  return null;
}

function updateResultsBusy() {
  const busy = Array.from(resultsEl.querySelectorAll('.card')).some(
    card => card.getAttribute('aria-busy') === 'true'
  );
  resultsEl.setAttribute('aria-busy', busy ? 'true' : 'false');
}

function updateTimerDisplay(state) {
  const now = performance.now();
  const elapsed = state.baseElapsed + (now - state.receivedAt) / 1000;
  const headTime = state.card.querySelector('.time');
  if (headTime) headTime.textContent = '⏱ ' + formatSeconds(elapsed);
  if (elapsed >= 60 && state.card.dataset.stage === 'generating') {
    const label = state.card.querySelector('.stage-label');
    if (label) label.textContent = '仍在生成，复杂页面可能需要更久';
  }
}

function ensureTimer() {
  if (timerId !== null) return;
  timerId = window.setInterval(() => {
    cardTimers.forEach(updateTimerDisplay);
    if (cardTimers.size === 0) {
      window.clearInterval(timerId);
      timerId = null;
    }
  }, 500);
}

function startCardTimer(card) {
  const now = performance.now();
  cardTimers.set(card.dataset.key, {
    card,
    baseElapsed: 0,
    receivedAt: now
  });
  ensureTimer();
}

function syncCardTimer(key, elapsed) {
  const state = cardTimers.get(String(key));
  if (!state) return;
  const now = performance.now();
  const liveElapsed = state.baseElapsed + (now - state.receivedAt) / 1000;
  const eventElapsed = Math.max(0, Number(elapsed) || 0);
  state.baseElapsed = Math.max(liveElapsed, eventElapsed);
  state.receivedAt = now;
  const headTime = state.card.querySelector('.time');
  if (headTime) headTime.textContent = '⏱ ' + formatSeconds(state.baseElapsed);
}

function stopCardTimer(key, elapsed) {
  const state = cardTimers.get(String(key));
  if (state) {
    const now = performance.now();
    const liveElapsed = state.baseElapsed + (now - state.receivedAt) / 1000;
    const reportedElapsed = Number(elapsed) || 0;
    const finalElapsed = reportedElapsed > 0
      ? reportedElapsed
      : liveElapsed;
    state.baseElapsed = finalElapsed;
    state.receivedAt = now;
    const headTime = state.card.querySelector('.time');
    if (headTime) headTime.textContent = '⏱ ' + formatSeconds(finalElapsed);
    cardTimers.delete(String(key));
    return finalElapsed;
  }
  return null;
}

function clearCardTimers() {
  cardTimers.clear();
  if (timerId !== null) {
    window.clearInterval(timerId);
    timerId = null;
  }
}

function clearRenderTimers() {
  renderTimers.forEach(id => window.clearInterval(id));
  renderTimers.clear();
}

function getMode() {
  const active = modeEl.querySelector('.active');
  return active ? active.dataset.mode : 'mobile';
}
function setMode(mode) {
  currentMode = mode;
  modeEl.querySelectorAll('button').forEach(b => {
    b.classList.toggle('active', b.dataset.mode === mode);
  });
  const mobile = mode === 'mobile';
  arkuiExportEl.disabled = !mobile;
  arkuiOptionEl.classList.toggle('disabled', !mobile);
}
modeEl.querySelectorAll('button').forEach(b => {
  b.addEventListener('click', () => setMode(b.dataset.mode));
});
setMode(getMode());

function setTheme(theme) {
  currentTheme = theme === 'dark' ? 'dark' : 'light';
  localStorage.setItem('uibench-preview-theme', currentTheme);
  themeEl.querySelectorAll('button').forEach(b => {
    b.classList.toggle('active', b.dataset.theme === currentTheme);
  });
  previewFrames.forEach(entry => {
    entry.iframe.srcdoc = injectForRender(
      entry.html, entry.mode, currentTheme, currentTokenTheme
    );
  });
}
themeEl.querySelectorAll('button').forEach(b => {
  b.addEventListener('click', () => setTheme(b.dataset.theme));
});

function setTokenTheme(tokenTheme) {
  currentTokenTheme = tokenThemes.includes(tokenTheme) ? tokenTheme : 'harmonyos';
  localStorage.setItem('uibench-preview-token-theme', currentTokenTheme);
  tokenThemeEl.querySelectorAll('button').forEach(b => {
    b.classList.toggle('active', b.dataset.tokenTheme === currentTokenTheme);
  });
  previewFrames.forEach(entry => {
    entry.iframe.srcdoc = injectForRender(
      entry.html, entry.mode, currentTheme, currentTokenTheme
    );
  });
}
tokenThemeEl.querySelectorAll('button').forEach(b => {
  b.addEventListener('click', () => setTokenTheme(b.dataset.tokenTheme));
});

function setHmSymbolPreview(value) {
  hmSymbolPreview = value === 'harmony';
  localStorage.setItem(
    'uibench-preview-hm-symbol', hmSymbolPreview ? 'harmony' : 'lucide'
  );
  hmSymbolModeEl.querySelectorAll('button').forEach(b => {
    b.classList.toggle(
      'active', (b.dataset.hmSymbol === 'harmony') === hmSymbolPreview
    );
  });
  previewFrames.forEach(entry => {
    entry.iframe.srcdoc = injectForRender(
      entry.html, entry.mode, currentTheme, currentTokenTheme
    );
  });
}
hmSymbolModeEl.querySelectorAll('button').forEach(b => {
  b.addEventListener('click', () => setHmSymbolPreview(b.dataset.hmSymbol));
});
setHmSymbolPreview(hmSymbolPreview ? 'harmony' : 'lucide');
setTokenTheme(currentTokenTheme);
setTheme(currentTheme);

function scalePcFrame(entry) {
  const scale = Math.min(entry.wrap.clientWidth / 1920, 1);
  entry.iframe.style.transform = 'scale(' + scale + ')';
  entry.wrap.style.height = Math.round(1080 * scale) + 'px';
}
window.addEventListener('resize', () => pcFrames.forEach(scalePcFrame));

function updateRunningMeta() {
  const remaining = Math.max(0, count - done);
  metaEl.innerHTML = '<span class="meta-pulse" aria-hidden="true"></span>' +
    '并行生成中 · 已完成 <b>' + done + '/' + count + '</b> · 成功 ' + successCount +
    ' · 图片异常 ' + degradedCount + ' · 失败 ' + failureCount + ' · 剩余 ' + remaining +
    ' <span class="meta-note">结果完成后会立即出现</span>';
}

function applyStart(models, restoring = false) {
  clearCardTimers();
  clearRenderTimers();
  count = models.length; done = 0; successCount = 0; degradedCount = 0; failureCount = 0;
  sawStreamDone = restoring;
  metaEl.setAttribute('role', 'status');
  resultsEl.setAttribute('aria-busy', restoring ? 'false' : 'true');
  if (restoring) metaEl.textContent = '正在恢复上次生成结果…';
  else updateRunningMeta();
  resultsEl.innerHTML = '';
  pcFrames.length = 0;
  previewFrames.length = 0;
  models.forEach(m => resultsEl.appendChild(makeCard(m, restoring)));
}

function applyProgress(progress) {
  const card = cardForKey(progress.key);
  if (!card || card.dataset.finished === 'true') return;
  const stage = progress.stage || 'generating';
  const message = progress.message || stageLabels[stage] || '正在生成';
  const label = card.querySelector('.stage-label');

  // Queueing and request preparation are near-instant implementation details.
  // Keep their real time inside the first meaningful, user-facing stage.
  if (stage === 'preparing' || stage === 'generating') {
    card.dataset.stage = 'generating';
    card.dataset.state = 'running';
    if (label) label.textContent = stageLabels.generating;
    return;
  }

  card.dataset.stage = stage;
  card.dataset.state = stage === 'failed' ? 'failed' : 'running';
  syncCardTimer(progress.key, progress.elapsed_seconds);
  if (label) label.textContent = message;
}
function applyResult(r) {
  fillCard(r);
  done++;
  const status = r.status || (r.error ? 'failed' : (r.image_error ? 'degraded' : 'success'));
  if (status === 'failed') failureCount++;
  else if (status === 'degraded') degradedCount++;
  else successCount++;
  if (done < count) updateRunningMeta();
}
function applyDone(total) {
  sawStreamDone = true;
  clearCardTimers();
  updateResultsBusy();
  const tag = currentMode === 'pc' ? 'PC端 antd' : '移动端';
  const label = failureCount ? '本次生成结束' :
    (degradedCount ? '本次生成完成（有图片异常）' : '本次生成完成');
  metaEl.innerHTML = label + ' · 成功 <b>' + successCount + '/' + count + '</b>' +
    (degradedCount ? ' · 图片异常 <b>' + degradedCount + '</b>' : '') +
    (failureCount ? ' · 失败 <b>' + failureCount + '</b>' : '') +
    ' · ' + tag + ' · 并行总耗时 <b>' + total + 's</b>';
}

function interruptPendingCards(message) {
  let pending = 0;
  resultsEl.querySelectorAll('.card').forEach(card => {
    if (card.dataset.finished === 'true') return;
    pending++;
    card.dataset.finished = 'true';
    card.dataset.state = 'interrupted';
    card.dataset.stage = 'interrupted';
    card.setAttribute('aria-busy', 'false');
    stopCardTimer(card.dataset.key, 0);
    const label = card.querySelector('.stage-label');
    if (label) label.textContent = stageLabels.interrupted;
    const slot = card.querySelector('.preview-slot');
    if (slot) {
      slot.innerHTML = '';
      const error = document.createElement('div');
      error.className = 'error';
      error.textContent = '未收到该模型的完整结果，请重新生成。';
      slot.appendChild(error);
    }
  });
  clearCardTimers();
  resultsEl.setAttribute('aria-busy', 'false');
  metaEl.setAttribute('role', 'alert');
  if (pending) {
    metaEl.innerHTML = '连接中断 · 已保留 <b>' + done + '</b> 个结果，另外 <b>' +
      pending + '</b> 个未完成';
  } else {
    metaEl.innerHTML = '<span style="color:var(--err)">请求失败：' + esc(message) + '</span>';
  }
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const prompt = promptEl.value.trim();
  if (!prompt) return;
  currentMode = getMode();
  const thisRequest = ++requestSerial;
  sawStreamDone = false;
  btn.disabled = true;
  const oldText = btn.textContent;
  btn.textContent = '生成中…';
  try {
    const resp = await fetch('/api/generate', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        prompt,
        mode: currentMode,
        arkui_export_enabled: currentMode === 'mobile' && arkuiExportEl.checked,
        image_source: currentImageSource
      })
    });
    if (!resp.ok) {
      const t = await resp.text();
      throw new Error(t || ('HTTP ' + resp.status));
    }
    if (!resp.body) throw new Error('浏览器不支持流式响应');
    const reader = resp.body.getReader();
    const dec = new TextDecoder();
    let buf = '';
    while (true) {
      const { done: rd, value } = await reader.read();
      if (value) buf += dec.decode(value, {stream: true});
      let i;
      while ((i = buf.indexOf('\\n')) >= 0) {
        const line = buf.slice(0, i); buf = buf.slice(i + 1);
        if (!line.trim()) continue;
        if (thisRequest !== requestSerial) return;
        const msg = JSON.parse(line);
        if (msg.type === 'start') applyStart(msg.models);
        else if (msg.type === 'progress') applyProgress(msg);
        else if (msg.type === 'result') applyResult(msg.result);
        else if (msg.type === 'done') applyDone(msg.total_seconds);
      }
      if (rd) break;
    }
    if (!sawStreamDone) throw new Error('生成流提前结束');
  } catch (err) {
    interruptPendingCards(String(err));
  } finally {
    btn.disabled = false;
    btn.textContent = oldText;
  }
});

// restore the last run after a page refresh
async function restoreLast() {
  const restoreSerial = requestSerial;
  try {
    const resp = await fetch('/api/last');
    if (!resp.ok) return;
    const data = await resp.json();
    if (restoreSerial !== requestSerial) return;
    if (data.prompt) promptEl.value = data.prompt;
    if (data.mode) setMode(data.mode);
    if (typeof data.arkui_export_enabled === 'boolean') {
      arkuiExportEl.checked = data.arkui_export_enabled;
    }
    applyStart(data.models || [], true);
    (data.results || []).forEach(r => applyResult(r));
    applyDone(data.total_seconds);
  } catch (e) { /* ignore - no prior run */ }
}
restoreLast();

function makeCard(m, restoring = false) {
  const card = document.createElement('section');
  card.className = 'card';
  card.dataset.key = m.key;
  card.dataset.state = restoring ? 'restoring' : 'running';
  card.dataset.stage = restoring ? 'queued' : 'generating';
  card.dataset.finished = 'false';
  card.setAttribute('aria-busy', restoring ? 'false' : 'true');
  const titleId = 'model-title-' + m.key;
  card.setAttribute('aria-labelledby', titleId);
  const progress = document.createElement('div');
  progress.className = 'progress-panel';
  const head = document.createElement('div');
  head.className = 'card-head';
  head.innerHTML =
    '<div class="titles"><span class="name" id="' + esc(titleId) + '">' + esc(m.name) + '</span>' +
    '<span class="provider">' + esc(m.provider) + '</span></div>' +
    '<span class="time" aria-hidden="true">⏱ 0.0s</span>' +
    '<div class="head-status"><span class="stage-dot" aria-hidden="true"></span>' +
    '<span class="stage-label">' + (restoring ? '正在恢复结果' : stageLabels.generating) + '</span></div>';
  progress.appendChild(head);
  const body = document.createElement('div');
  body.className = 'card-body';

  const slot = document.createElement('div');
  slot.className = 'preview-slot';
  const sk = document.createElement('div');
  sk.className = 'skeleton';
  sk.setAttribute('aria-hidden', 'true');
  if (currentMode === 'pc') {
    sk.style.width = '100%';
    sk.style.height = '480px';
    sk.style.maxWidth = 'none';
  }
  slot.appendChild(sk);
  body.append(slot);
  card.append(progress, body);
  if (!restoring) startCardTimer(card);
  return card;
}

function fillCard(r) {
  const card = cardForKey(r.key);
  if (!card) return;
  card.dataset.finished = 'true';
  let modelElapsed = stopCardTimer(r.key, r.elapsed_seconds);
  if (modelElapsed === null) modelElapsed = Math.max(0, Number(r.elapsed_seconds) || 0);
  card.dataset.modelElapsed = String(modelElapsed);
  setCardTotal(card, modelElapsed, r);
  const label = card.querySelector('.stage-label');
  const slot = card.querySelector('.preview-slot');
  const resultStatus = r.status || (r.error ? 'failed' : (r.image_error ? 'degraded' : 'success'));
  slot.innerHTML = '';

  // tools (always available so the log is reachable even on error/empty)
  const tools = document.createElement('div');
  tools.className = 'tools';
  const logBtn = document.createElement('button');
  logBtn.textContent = '查看日志';
  logBtn.onclick = () => openLog(r.log_url, r.name + ' · ⏱ ' + r.elapsed_seconds + 's');
  tools.appendChild(logBtn);

  const arkuiSummary = r.arkui_manifest && r.arkui_manifest.summary;
  if (r.mode === 'mobile' && arkuiSummary && arkuiSummary.metadataPresent) {
    const exportBtn = document.createElement('button');
    const readiness = arkuiSummary.exportReadiness || 'blocked';
    exportBtn.textContent = readiness === 'blocked' ? 'ArkUI 不可导出' : '下载鸿蒙工程';
    if (!arkuiSummary.exportable) exportBtn.classList.add('export-blocked');
    exportBtn.title = readiness === 'ready'
      ? '在固定 __UIBENCH_MOBILE_VIEWPORT_WIDTH__×__UIBENCH_MOBILE_VIEWPORT_HEIGHT__ 视口固化当前主题的计算样式后导出'
      : (arkuiSummary.exportable
          ? '查看日志中的 ArkUI Manifest 诊断'
          : '点击查看不可导出的原因');
    const lossyBtn = document.createElement('button');
    lossyBtn.className = 'lossy-reasons';
    lossyBtn.style.display = 'none';
    lossyBtn.textContent = '有损原因';
    lossyBtn.title = '查看这次导出无法还原网页效果的具体差异';
    var exportLabelResetTimer = null;
    exportBtn.onclick = async () => {
      if (!arkuiSummary.exportable) {
        window.alert(formatArkUiBlockReasons(r.arkui_manifest));
        return;
      }
      if (exportLabelResetTimer !== null) {
        window.clearTimeout(exportLabelResetTimer);
        exportLabelResetTimer = null;
      }
      const oldLabel = exportBtn.textContent;
      exportBtn.disabled = true;
      lossyBtn.style.display = 'none';
      exportBtn.textContent = '导出中…';
      try {
        exportBtn.textContent = '固化样式…';
        const snapshot = await captureArkUiSnapshot(r);
        exportBtn.textContent = '生成 ArkTS…';
        const exported = await requestArkUiExport(r, snapshot);
        downloadBase64(
          withDownloadTimestamp(
            exported.bundle.filename || ('Generated_' + r.key + '_HarmonyOS.zip')
          ),
          exported.bundle.contentBase64,
          exported.bundle.mimeType || 'application/zip'
        );
        const exportDiagnostics = Array.isArray(exported.diagnostics)
          ? exported.diagnostics : [];
        const isLossy = exported.quality.readiness !== 'ready';
        if (isLossy) {
          const warningCount = exportDiagnostics.filter(
            item => item && item.severity === 'warning').length;
          lossyBtn.textContent = '有损原因（' + warningCount + '）';
          lossyBtn.style.display = '';
          lossyBtn.onclick = () => openArkUiLossDetails(r.name, exportDiagnostics);
        }
        exportBtn.textContent = isLossy ? '已下载（有损）' : '已下载';
        exportLabelResetTimer = window.setTimeout(() => {
          exportLabelResetTimer = null;
          exportBtn.textContent = oldLabel;
        }, 1500);
      } catch (error) {
        console.error('ArkUI export failed', error);
        window.alert('ArkUI 导出失败：' + String(error));
        exportBtn.textContent = oldLabel;
      } finally {
        exportBtn.disabled = false;
      }
    };
    tools.append(exportBtn, lossyBtn);
  }

  if (r.error) {
    card.dataset.state = 'failed';
    card.dataset.stage = 'failed';
    card.setAttribute('aria-busy', 'false');
    updateResultsBusy();
    if (label) label.textContent = stageLabels.failed;
    tools.style.marginBottom = '0';
    slot.appendChild(tools);
    const err = document.createElement('div');
    err.className = 'error';
    err.textContent = '生成失败：' + r.error;
    slot.appendChild(err);
    return;
  }
  if (r.html) {
    card.dataset.state = 'rendering';
    card.dataset.stage = 'rendering';
    card.setAttribute('aria-busy', 'true');
    if (label) label.textContent = stageLabels.rendering;
    const copy = document.createElement('button');
    copy.textContent = '复制 HTML';
    copy.onclick = () => {
      const copyHtml = r.mode === 'mobile'
        ? normalizeDesignTokenClasses(r.html) : r.html;
      navigator.clipboard.writeText(copyHtml).then(() => {
        copy.textContent = '已复制'; setTimeout(() => copy.textContent = '复制 HTML', 1500);
      });
    };
    const open = document.createElement('button');
    open.textContent = '新标签打开';
    open.onclick = () => {
      const b = new Blob([
        injectForRender(r.html, r.mode, currentTheme, currentTokenTheme)
      ], {type: 'text/html'});
      window.open(URL.createObjectURL(b), '_blank');
    };
    tools.append(copy, open);
    slot.appendChild(tools);

    const isPc = (r.mode === 'pc');
    const renderStatus = document.createElement('div');
    renderStatus.className = 'render-status' + (isPc ? ' wide' : '');
    renderStatus.setAttribute('role', 'status');
    renderStatus.textContent = '页面已生成，正在加载预览…';
    slot.appendChild(renderStatus);
    const iframe = document.createElement('iframe');
    iframe.setAttribute('sandbox', 'allow-scripts allow-forms allow-modals allow-popups');
    iframe.title = r.name + ' 生成的' + (isPc ? 'PC 端' : '移动端') + '预览';
    const renderStartedAt = performance.now();
    const renderKey = String(r.key);
    renderTimers.set(renderKey, window.setInterval(() => {
      const renderElapsed = (performance.now() - renderStartedAt) / 1000;
      setCardTotal(card, modelElapsed + renderElapsed, r);
    }, 100));
    let previewSettled = false;
    const settlePreview = (fullyLoaded) => {
      if (previewSettled) return;
      previewSettled = true;
      const renderTimer = renderTimers.get(renderKey);
      if (renderTimer !== undefined) window.clearInterval(renderTimer);
      renderTimers.delete(renderKey);
      const renderElapsed = Math.max(0, (performance.now() - renderStartedAt) / 1000);
      renderStatus.remove();
      const degraded = resultStatus === 'degraded';
      card.dataset.state = degraded ? 'degraded' : 'completed';
      card.dataset.stage = degraded ? 'degraded' : 'completed';
      card.setAttribute('aria-busy', 'false');
      updateResultsBusy();
      if (label) label.textContent = degraded
        ? stageLabels.degraded
        : (fullyLoaded ? stageLabels.completed : '预览已显示');
      const totalElapsed = modelElapsed + renderElapsed;
      setCardTotal(card, totalElapsed, r);
    };
    iframe.addEventListener('load', () => settlePreview(true), {once: true});
    iframe.srcdoc = injectForRender(
      r.html, r.mode, currentTheme, currentTokenTheme
    );
    if (isPc) {
      const wrap = document.createElement('div');
      wrap.className = 'pc-wrap';
      iframe.className = 'pc-frame';
      wrap.appendChild(iframe);
      slot.appendChild(wrap);
      const entry = {wrap, iframe};
      pcFrames.push(entry);
      // scale after the iframe is in the layout
      requestAnimationFrame(() => scalePcFrame(entry));
    } else {
      iframe.className = 'phone';
      slot.appendChild(iframe);
      previewFrames.push({iframe, html: r.html, mode: r.mode});
    }
    // Some generated pages keep remote fonts/scripts pending for a long time.
    // The iframe is already mounted and visible, so stop the anxious loading
    // state while truthfully noting that external resources may continue.
    window.setTimeout(() => settlePreview(false), 1800);
  } else {
    card.dataset.state = 'failed';
    card.dataset.stage = 'failed';
    card.setAttribute('aria-busy', 'false');
    updateResultsBusy();
    if (label) label.textContent = stageLabels.failed;
    slot.appendChild(tools);
    const empty = document.createElement('div');
    empty.className = 'empty';
    empty.textContent = '模型未返回 HTML';
    slot.appendChild(empty);
  }
}

function normalizeDesignTokenClassName(token) {
  var aliases = {
    'dt-rounded-full': 'dt-rounded-pill',
    'dt-bg-canvas/90': 'dt-bg-canvas-translucent',
    'dt-bg-primary/10': 'dt-bg-primary-container-subtle',
    'dt-bg-accent/15': 'dt-bg-accent-container-subtle',
    'focus:dt-focus': 'dt-focus',
    'placeholder:dt-placeholder-secondary': 'dt-placeholder-secondary'
  };
  if (aliases[token]) return aliases[token];
  var opacity = token.match(/^dt-bg-(canvas|primary|accent)\\/(\\d{1,3})$/);
  if (opacity) {
    if (opacity[1] === 'canvas') return 'dt-bg-canvas-translucent';
    return 'dt-bg-' + opacity[1]
      + (Number(opacity[2]) >= 20 ? '-container' : '-container-subtle');
  }
  if (/^hover:dt-bg-/.test(token)) return 'dt-interaction-hover';
  if (/^active:dt-bg-/.test(token)) return 'dt-interaction-pressed';
  return token;
}

function normalizeDesignTokenClasses(html) {
  return html.replace(/\\bclass\\s*=\\s*(["'])([\\s\\S]*?)\\1/gi,
    function(whole, quote, classNames) {
      var seen = new Set();
      var normalized = classNames.trim().split(/\\s+/).filter(Boolean).map(
        normalizeDesignTokenClassName
      ).filter(function(token) {
        if (seen.has(token)) return false;
        seen.add(token);
        return true;
      });
      return 'class=' + quote + normalized.join(' ') + quote;
    });
}

function arkuiSnapshotRuntime(captureSession) {
  var styleProperties = [
    'display', 'flexDirection', 'flexGrow', 'flexShrink', 'flexBasis',
    'position', 'top', 'left', 'width', 'height',
    'paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft',
    'marginTop', 'marginRight', 'marginBottom', 'marginLeft',
    'rowGap', 'columnGap', 'justifyContent', 'alignItems',
    'gridTemplateColumns', 'gridTemplateRows', 'gridAutoFlow',
    'gridRowStart', 'gridRowEnd', 'gridColumnStart', 'gridColumnEnd',
    'backgroundColor', 'backgroundImage',
    'borderTopWidth', 'borderRightWidth', 'borderBottomWidth', 'borderLeftWidth',
    'borderTopColor', 'borderRightColor', 'borderBottomColor', 'borderLeftColor',
    'borderTopStyle', 'borderRightStyle', 'borderBottomStyle', 'borderLeftStyle',
    'borderTopLeftRadius', 'borderTopRightRadius',
    'borderBottomRightRadius', 'borderBottomLeftRadius',
    'opacity', 'boxShadow', 'color', 'fontSize', 'fontWeight', 'fontFamily',
    'lineHeight', 'textAlign', 'letterSpacing', 'textDecorationLine',
    'textTransform', 'fontStyle', 'whiteSpace', 'textOverflow', 'webkitLineClamp',
    'objectFit', 'overflowX', 'overflowY', 'transform', 'filter',
    'backdropFilter', 'clipPath'
  ];

  function boundedWait(promise, milliseconds) {
    return Promise.race([
      promise.catch(function() {}),
      new Promise(function(resolve) { setTimeout(resolve, milliseconds); })
    ]);
  }

  async function settleResources() {
    if (window.__uibenchHmSymbolReady) {
      // Glyph substitution must finish before styles are frozen, or the
      // captured font evidence would describe the un-substituted page.
      await boundedWait(window.__uibenchHmSymbolReady, 3000);
    }
    if (document.fonts && document.fonts.ready) {
      await boundedWait(document.fonts.ready, 1800);
    }
    var images = Array.from(document.images || []);
    await Promise.all(images.map(function(image) {
      if (image.complete) return Promise.resolve();
      return boundedWait(new Promise(function(resolve) {
        image.addEventListener('load', resolve, {once: true});
        image.addEventListener('error', resolve, {once: true});
      }), 1800);
    }));
    // Browsers may suspend requestAnimationFrame inside an off-screen,
    // transparent iframe.  Keep the double-frame settle when available, but
    // never let it prevent the snapshot response.
    await boundedWait(new Promise(function(resolve) {
      requestAnimationFrame(function() { requestAnimationFrame(resolve); });
    }), 250);
  }

  function rounded(value) {
    return Math.round(Number(value) * 10000) / 10000;
  }

  function capturedWidthSizing(element) {
    try {
      if (typeof element.computedStyleMap !== 'function') return 'unknown';
      var typedWidth = element.computedStyleMap().get('width');
      if (!typedWidth) return 'unknown';
      return String(typedWidth).trim().toLowerCase() === 'auto'
        ? 'auto' : 'explicit';
    } catch (_) {
      return 'unknown';
    }
  }

  function singleLineTextWidth(element) {
    if (String(element.getAttribute('data-component') || '').trim().toLowerCase() !== 'text') {
      return null;
    }
    var range = document.createRange();
    try {
      range.selectNodeContents(element);
      var rects = Array.from(range.getClientRects()).filter(function(rect) {
        return rect.width > 0 && rect.height > 0;
      });
      if (!rects.length) return null;
      var first = rects[0];
      var oneLine = rects.every(function(rect) {
        return Math.abs(rect.top - first.top) <= 0.5
          && Math.abs(rect.bottom - first.bottom) <= 0.5;
      });
      if (!oneLine) return null;
      var left = first.left;
      var right = first.right;
      rects.slice(1).forEach(function(rect) {
        left = Math.min(left, rect.left);
        right = Math.max(right, rect.right);
      });
      return rounded(right - left);
    } catch (_) {
      return null;
    }
  }

  function isTransparentColor(value) {
    var color = String(value || '').trim().toLowerCase();
    if (!color || color === 'transparent') return true;
    var functional = color.match(/^(?:rgba?|hsla?|color)\\(([\\s\\S]*)\\)$/);
    if (!functional) return false;
    var alpha = functional[1].match(
      /(?:,|\\/)\\s*([+-]?(?:\\d+\\.?\\d*|\\.\\d+))(%)?\\s*$/
    );
    return Boolean(alpha) && Number(alpha[1]) === 0;
  }

  function visibleCanvasBackground() {
    var htmlStyle = getComputedStyle(document.documentElement);
    var htmlColor = String(htmlStyle.backgroundColor || '');
    var htmlImage = String(htmlStyle.backgroundImage || 'none');
    var bodyStyle = document.body ? getComputedStyle(document.body) : null;
    var bodyColor = bodyStyle
      ? String(bodyStyle.backgroundColor || '') : '';
    var bodyImage = bodyStyle
      ? String(bodyStyle.backgroundImage || 'none') : 'none';
    if (htmlImage.trim().toLowerCase() !== 'none') {
      return {backgroundColor: htmlColor, backgroundImage: htmlImage};
    }
    // A body image may either propagate to the canvas or paint the body box,
    // depending on the root background. Both affect the rendered page behind
    // the annotated tree, so report either case and fail closed downstream.
    if (bodyImage.trim().toLowerCase() !== 'none') {
      return {
        backgroundColor: isTransparentColor(htmlColor) ? bodyColor : htmlColor,
        backgroundImage: bodyImage
      };
    }
    if (!isTransparentColor(htmlColor)) {
      return {backgroundColor: htmlColor, backgroundImage: htmlImage};
    }
    // When the root canvas is fully transparent and has no image, the body
    // background propagates to the canvas. Preserve both layers so a gradient
    // or image can be rejected explicitly instead of becoming a flat color.
    return {
      backgroundColor: bodyStyle ? bodyColor : htmlColor,
      backgroundImage: bodyStyle ? bodyImage : htmlImage
    };
  }

  function singleAnnotatedRoot(elements) {
    var annotated = new Set(elements);
    var roots = elements.filter(function(element) {
      var ancestor = element.parentElement;
      while (ancestor) {
        if (annotated.has(ancestor)) return false;
        ancestor = ancestor.parentElement;
      }
      return true;
    });
    if (roots.length !== 1) return null;
    var root = roots[0];
    var rect = root.getBoundingClientRect();
    // A scrollable page is taller than the viewport, so ask the root to
    // contain the viewport rather than match it exactly.
    var coversViewport = rect.x <= 1
      && rect.y <= 1
      && rect.x + rect.width >= window.innerWidth - 1
      && rect.y + rect.height >= window.innerHeight - 1;
    return coversViewport ? root : null;
  }

  function isActuallyVisible(element, rect) {
    if (rect.width <= 0 || rect.height <= 0) return false;
    if (typeof element.checkVisibility === 'function') {
      try {
        return element.checkVisibility({
          checkOpacity: true,
          opacityProperty: true,
          checkVisibilityCSS: true,
          visibilityProperty: true
        });
      } catch (_) {
        // Older engines may expose checkVisibility without option support.
      }
    }
    var current = element;
    while (current) {
      var currentStyle = getComputedStyle(current);
      var display = String(currentStyle.display || '').toLowerCase();
      var visibility = String(currentStyle.visibility || '').toLowerCase();
      var contentVisibility = String(
        currentStyle.contentVisibility || ''
      ).toLowerCase();
      var opacity = Number(currentStyle.opacity || 1);
      if (display === 'none'
          || visibility === 'hidden'
          || visibility === 'collapse'
          || contentVisibility === 'hidden'
          || (Number.isFinite(opacity) && opacity <= 0)) {
        return false;
      }
      current = current.parentElement;
    }
    return true;
  }

  function captureNode(element, canvasRoot, canvasBackground) {
    var rect = element.getBoundingClientRect();
    var style = getComputedStyle(element);
    var elementPosition = String(style.position || '').trim().toLowerCase();
    var directParent = element.parentElement;
    var directParentNodeId = directParent
      ? String(directParent.getAttribute('data-node-id') || '').trim() || null
      : null;
    var isFlexItem = false;
    if (directParent && elementPosition !== 'absolute' && elementPosition !== 'fixed') {
      var directParentDisplay = String(
        getComputedStyle(directParent).display || ''
      ).toLowerCase();
      isFlexItem = directParentDisplay === 'flex'
        || directParentDisplay === 'inline-flex';
    }
    var computed = {};
    styleProperties.forEach(function(property) {
      computed[property] = String(style[property] || '');
    });
    if (element === canvasRoot
        && isTransparentColor(computed.backgroundColor)
        && canvasBackground.backgroundImage.trim().toLowerCase() === 'none'
        && !isTransparentColor(canvasBackground.backgroundColor)) {
      computed.backgroundColor = canvasBackground.backgroundColor;
    }
    if (computed.backgroundImage.length > 1000) {
      computed.backgroundImage = 'url("[uibench-captured-resource]")';
    }
    computed.pseudoBeforeContent = String(
      getComputedStyle(element, '::before').content || ''
    );
    computed.pseudoAfterContent = String(
      getComputedStyle(element, '::after').content || ''
    );
    if (!computed.backdropFilter && style.webkitBackdropFilter) {
      computed.backdropFilter = String(style.webkitBackdropFilter);
    }
    var visible = isActuallyVisible(element, rect);
    var resolvedSrc = null;
    if (element.tagName && element.tagName.toLowerCase() === 'img') {
      resolvedSrc = element.currentSrc || element.src || null;
      if (resolvedSrc && resolvedSrc.length > 4000) {
        resolvedSrc = 'data:[uibench-captured-resource]';
      }
    }
    return {
      nodeId: element.getAttribute('data-node-id'),
      tag: String(element.tagName || 'unknown').toLowerCase(),
      bbox: [rounded(rect.x), rounded(rect.y), rounded(rect.width), rounded(rect.height)],
      visible: visible,
      widthSizing: capturedWidthSizing(element),
      singleLineTextWidth: singleLineTextWidth(element),
      resolvedSrc: resolvedSrc,
      directParentNodeId: directParentNodeId,
      isFlexItem: isFlexItem,
      computed: computed
    };
  }

  function simpleBackgroundUrl(value) {
    var match = String(value || '').trim().match(/^url\\((?:"([\\s\\S]*)"|'([\\s\\S]*)'|([^)]*))\\)$/);
    return match ? String(match[1] || match[2] || match[3] || '').trim() : null;
  }

  function bytesToBase64(bytes) {
    var binary = '';
    for (var offset = 0; offset < bytes.length; offset += 32768) {
      binary += String.fromCharCode.apply(null, bytes.subarray(offset, offset + 32768));
    }
    return btoa(binary);
  }

  async function fetchAssetBytes(source) {
    var parsed = new URL(source, document.baseURI);
    // http: covers the local gallery served by UIBench itself over
    // http://127.0.0.1. This frame is sandboxed without allow-same-origin,
    // so every network read is cross-origin and must go through CORS.
    var networkProtocols = ['https:', 'http:'];
    if (!networkProtocols.concat(['data:', 'blob:']).includes(parsed.protocol)) {
      throw new Error('unsupported resource protocol');
    }
    var controller = new AbortController();
    var timer = setTimeout(function() { controller.abort(); }, 3000);
    try {
      var response = await fetch(parsed.href, {
        credentials: 'omit',
        mode: networkProtocols.includes(parsed.protocol) ? 'cors' : 'same-origin',
        referrerPolicy: 'no-referrer',
        signal: controller.signal
      });
      if (!response.ok) throw new Error('resource fetch failed');
      var declaredLength = Number(response.headers.get('content-length') || 0);
      if (declaredLength > 2000000) throw new Error('resource exceeds 2 MB');
      var blob = await response.blob();
      if (!blob.size || blob.size > 2000000) throw new Error('resource exceeds 2 MB');
      return {
        mimeType: String(blob.type || response.headers.get('content-type') || 'application/octet-stream')
          .split(';')[0].slice(0, 100),
        bytes: new Uint8Array(await blob.arrayBuffer())
      };
    } finally {
      clearTimeout(timer);
    }
  }

  async function captureAssets() {
    var grouped = new Map();
    Array.from(document.querySelectorAll('[data-node-id]')).forEach(function(element) {
      var nodeId = element.getAttribute('data-node-id');
      if (!nodeId) return;
      var candidates = [];
      if (element.tagName && element.tagName.toLowerCase() === 'img') {
        var imageSource = element.currentSrc || element.src || '';
        if (imageSource) candidates.push({kind: 'image', source: imageSource});
      }
      var backgroundSource = simpleBackgroundUrl(getComputedStyle(element).backgroundImage);
      if (backgroundSource) candidates.push({kind: 'background-image', source: backgroundSource});
      candidates.forEach(function(candidate) {
        var source;
        try {
          source = new URL(candidate.source, document.baseURI).href;
        } catch (_) {
          return;
        }
        var item = grouped.get(source);
        if (!item) {
          item = {source: source, uses: new Map()};
          grouped.set(source, item);
        }
        var nodeIds = item.uses.get(candidate.kind) || new Set();
        nodeIds.add(nodeId);
        item.uses.set(candidate.kind, nodeIds);
      });
    });

    var groups = Array.from(grouped.values()).sort(function(a, b) {
      return a.source.localeCompare(b.source);
    }).slice(0, 16);
    var captured = await Promise.all(groups.map(async function(group) {
      try {
        var loaded = await fetchAssetBytes(group.source);
        return {
          mimeType: loaded.mimeType,
          contentBase64: bytesToBase64(loaded.bytes),
          byteLength: loaded.bytes.length,
          uses: Array.from(group.uses.entries()).map(function(pair) {
            return {kind: pair[0], nodeIds: Array.from(pair[1]).sort()};
          })
        };
      } catch (_) {
        return null;
      }
    }));
    var totalBytes = 0;
    return captured.filter(function(asset) {
      if (!asset || totalBytes + asset.byteLength > 8000000) return false;
      totalBytes += asset.byteLength;
      delete asset.byteLength;
      return true;
    });
  }

  window.addEventListener('message', async function(event) {
    var request = event.data;
    if (!request || request.type !== 'uibench-arkui-snapshot-request') return;
    if (request.session !== captureSession) return;
    if (typeof request.token !== 'string' || !request.token) return;
    try {
      await settleResources();
      var annotatedElements = Array.from(document.querySelectorAll('[data-node-id]'))
        .filter(function(element) { return element.getAttribute('data-node-id'); });
      var componentElements = annotatedElements.filter(function(element) {
        return String(element.getAttribute('data-component') || '').trim();
      });
      var canvasRoot = singleAnnotatedRoot(componentElements);
      var canvasBackground = visibleCanvasBackground();
      var nodes = annotatedElements.map(function(element) {
        return captureNode(element, canvasRoot, canvasBackground);
      });
      var assets = await captureAssets();
      window.parent.postMessage({
        type: 'uibench-arkui-snapshot-response',
        session: captureSession,
        token: request.token,
        snapshot: {
          snapshotVersion: 1,
          viewportWidth: window.innerWidth,
          viewportHeight: window.innerHeight,
          theme: document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light',
          tokenTheme: document.documentElement.dataset.tokenTheme || 'harmonyos',
          canvasBackgroundColor: canvasBackground.backgroundColor,
          canvasBackgroundImage: canvasBackground.backgroundImage.length > 1000
            ? '[uibench-captured-background-image]'
            : canvasBackground.backgroundImage,
          nodes: nodes,
          assets: assets
        }
      }, '*');
    } catch (error) {
      window.parent.postMessage({
        type: 'uibench-arkui-snapshot-error',
        session: captureSession,
        token: request.token,
        message: error instanceof Error ? error.message : String(error)
      }, '*');
    }
  });
  window.parent.postMessage({
    type: 'uibench-arkui-snapshot-ready',
    session: captureSession
  }, '*');
}

function arkuiSnapshotBootstrap(captureSession) {
  return '<style data-uibench-arkui-snapshot>'
    + '*,*::before,*::after{animation:none!important;transition:none!important;}'
    + '</style><scr' + 'ipt>(' + arkuiSnapshotRuntime.toString() + ')('
    + JSON.stringify(captureSession) + ');<' + '/script>';
}

function injectForRender(html, mode, theme, tokenTheme, arkuiCaptureSession) {
  // 1) shared scrollbar css + mobile Design Token contract
  var link = '<link rel="stylesheet" href="/shared.css">';
  if (mode === 'mobile') {
    html = normalizeDesignTokenClasses(html);
    theme = theme === 'dark' ? 'dark' : 'light';
    tokenTheme = tokenThemes.includes(tokenTheme) ? tokenTheme : 'harmonyos';
    html = html.replace(/<html\\b([^>]*)>/i, function(whole, attrs) {
      if (/\\sdata-theme\\s*=/i.test(attrs)) {
        attrs = attrs.replace(/\\sdata-theme\\s*=\\s*["'][^"']*["']/i,
          ' data-theme="' + theme + '"');
      } else {
        attrs += ' data-theme="' + theme + '"';
      }
      if (/\\sdata-token-theme\\s*=/i.test(attrs)) {
        attrs = attrs.replace(/\\sdata-token-theme\\s*=\\s*["'][^"']*["']/i,
          ' data-token-theme="' + tokenTheme + '"');
      } else {
        attrs += ' data-token-theme="' + tokenTheme + '"';
      }
      return '<html' + attrs + '>';
    });
  }
  if (mode === 'mobile') {
    var hmSymbolActive = hmSymbolPreview
      || (typeof arkuiCaptureSession === 'string' && arkuiCaptureSession);
    if (hmSymbolActive) {
      // The shim takes over lucide.createIcons and paints the exact device
      // glyphs (or export placeholders); the CDN build must not race it.
      html = html.replace(
        /<script[^>]*src=["']https?:\\/\\/unpkg\\.com\\/lucide@[^"']*["'][^>]*>\\s*<\\/script>/gi,
        ''
      );
      link += '<scr' + 'ipt src="/hm-symbol.js"></scr' + 'ipt>';
    }
  }
  var low = html.toLowerCase();
  if (mode === 'mobile') {
    if (low.indexOf('design-tokens.css') === -1) {
      link += '<link rel="stylesheet" href="/design-tokens.css">';
    }
    // Generated pages carry this link themselves; legacy documents get the
    // HarmonyOS text faces injected. The stylesheet is empty when the fonts
    // are not extracted, so pages keep the system-font fallback.
    if (low.indexOf('hm-fonts.css') === -1) {
      link += '<link rel="stylesheet" href="/hm-fonts.css">';
    }
  }
  var idx = low.indexOf('<head>');
  if (idx !== -1) { html = html.slice(0, idx + 6) + link + html.slice(idx + 6); }
  else {
    idx = low.indexOf('<html');
    if (idx !== -1) {
      var at = low.indexOf('>', idx);
      if (at !== -1) html = html.slice(0, at + 1) + '<head>' + link + '</head>' + html.slice(at + 1);
    } else { html = link + html; }
  }
  if (mode === 'mobile' && typeof arkuiCaptureSession === 'string'
      && arkuiCaptureSession) {
    var snapshotScript = arkuiSnapshotBootstrap(arkuiCaptureSession);
    var bodyEnd = html.toLowerCase().lastIndexOf('</body>');
    html = bodyEnd === -1
      ? html + snapshotScript
      : html.slice(0, bodyEnd) + snapshotScript + html.slice(bodyEnd);
  }
  // 2) PC: force classic JSX runtime so Babel emits React.createElement (no ESM import)
  if (mode === 'pc') html = injectPcBootstrap(html);
  return html;
}

function injectPcBootstrap(html) {
  // Force classic JSX runtime: register a wrapped preset pointing at the
  // built-in react preset with {runtime:"classic"} (per @babel/standalone
  // docs), then rewrite data-presets="react" -> "react-classic" so scripts
  // use it. Emits React.createElement, no ESM import, no blank page.
  var reg = '<script>'
    + '(function(){'
    + 'window.addEventListener("error",function(e){'
    + 'var b=document.getElementById("root");'
    + 'if(!b||b.innerHTML.trim())return;'
    + 'var m=(e&&(e.message||(e.error&&(e.error.stack||e.error.message))))||String(e);'
    + 'var s=String(m).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");'
    + 'b.innerHTML=`<div style="font:13px/1.6 -apple-system,system-ui,sans-serif;padding:16px;color:#b91c1c;white-space:pre-wrap;word-break:break-all;background:#fef2f2;border:1px solid #fecaca;border-radius:8px"><b>渲染失败</b>（脚本错误）\\n${s}</div>`;'
    + '});'
    + '})();'
    + 'Babel.registerPreset("react-classic",'
    + '{presets:[[Babel.availablePresets["react"],{runtime:"classic"}]]});'
    + '<' + '/script>';
  var m = html.match(/<script\\s+src="[^"]*babel[^"]*\\.js"[^>]*><\\/script>/i);
  if (m) {
    var end = m.index + m[0].length;
    html = html.slice(0, end) + reg + html.slice(end);
  } else {
    html = reg + html;
  }
  html = html.replace(/(data-presets\\s*=\\s*["'][^"']*)\\breact\\b([^"']*["'])/g,
    '$1react-classic$2');
  return html;
}

function openLog(url, title) {
  modalRoot.innerHTML = '';
  const overlay = document.createElement('div');
  overlay.className = 'overlay';
  overlay.onclick = (e) => { if (e.target === overlay) closeLog(); };
  const modal = document.createElement('div');
  modal.className = 'modal';
  const head = document.createElement('div');
  head.className = 'modal-head';
  head.innerHTML = '<span class="m-title">' + esc(title) + '</span>';
  const closeBtn = document.createElement('button');
  closeBtn.textContent = '关闭';
  closeBtn.onclick = closeLog;
  head.appendChild(closeBtn);
  const bodyEl = document.createElement('div');
  bodyEl.className = 'modal-body';
  bodyEl.innerHTML = '<div class="modal-load">加载日志中…</div>';
  modal.append(head, bodyEl);
  overlay.appendChild(modal);
  modalRoot.appendChild(overlay);
  fetch(url).then(r => r.ok ? r.text() : Promise.reject(r.status + ' ' + r.statusText))
    .then(txt => { bodyEl.innerHTML = '<pre></pre>'; bodyEl.firstChild.textContent = txt; })
    .catch(err => { bodyEl.innerHTML = '<div class="modal-err">加载失败：' + esc(String(err)) + '</div>'; });
  document.addEventListener('keydown', _escClose);
}

function _escClose(e) { if (e.key === 'Escape') closeLog(); }

function closeLog() {
  modalRoot.innerHTML = '';
  document.removeEventListener('keydown', _escClose);
}

// Human-readable explanations for export diagnostics whose message alone
// does not say what the deviation looks like on device.
const ARKUI_DIAG_EXPLANATIONS = {
  ARKUI_SYMBOL_UNAVAILABLE: '鸿蒙没有对应的系统图标，已替换为等大的空占位：布局不变，但缺一个图标',
  UIBENCH_BROWSER_SNAPSHOT_NODE_NOT_VISIBLE: '节点在当前主题/视口下不可见，它和它的子树没有导出',
  ARKUI_IMAGE_SRC_MISSING: 'image 节点缺少图片地址，导出成了空容器',
  UIBENCH_IMAGE_ASSET_NOT_MATERIALIZED: '图片没能打进工程资源包，设备上不会显示',
  UIBENCH_ASSET_FORMAT_UNSUPPORTED: '图片格式不支持（仅 PNG/JPEG/GIF/WebP），没有打进资源包',
  UIBENCH_ASSET_USE_INVALID: '捕获的图片与标注节点对不上，没有打进资源包',
  UIBENCH_COMPUTED_STYLE_SNAPSHOT_PENDING: '缺少浏览器样式快照，样式与几何没有固化',
  ARKUI_CONTENT_WRAPPED_FOR_SINGLE_SLOT: '单槽容器有多个子节点，已包进一层生成的容器',
  ARKUI_LIST_CHILD_WRAPPED_AS_ITEM: 'list 的直接子节点已包进生成的 ListItem，几何不变',
  ARKUI_LIST_ITEM_PROMOTED_TO_COLUMN: 'list 之外的 list-item 已按 column 导出',
  ARKUI_SPAN_PROMOTED_TO_TEXT: 'text 之外的 span 已按 text 导出',
  UIBENCH_ARKUI_LAYOUT_FOLLOWS_BROWSER: '标注方向与浏览器实际布局不同，已按浏览器实际方向导出'
};

function groupArkUiDiagnostics(items) {
  // One entry per (code, message): style-lossy repeats per node, and forty
  // identical box-shadow lines would bury the one icon that went missing.
  const groups = [];
  const byKey = {};
  items.forEach(item => {
    const key = (item.code || 'UNKNOWN') + ' :: ' + (item.message || '');
    if (!byKey[key]) {
      byKey[key] = {
        code: item.code || 'UNKNOWN',
        message: item.message || '',
        nodeIds: []
      };
      groups.push(byKey[key]);
    }
    if (item.nodeId) byKey[key].nodeIds.push(item.nodeId);
  });
  return groups;
}

function arkUiDiagnosticTitle(group) {
  if (group.code === 'UIBENCH_BROWSER_STYLE_LOSSY') {
    const marker = group.message.indexOf(': ');
    const property = marker === -1 ? group.message : group.message.slice(marker + 2);
    return '样式无法在 ArkUI 精确表达：' + property;
  }
  return ARKUI_DIAG_EXPLANATIONS[group.code] || group.message || group.code;
}

function renderArkUiDiagnosticGroup(group, severity) {
  const item = document.createElement('div');
  item.className = 'diag-item ' + severity;
  const title = document.createElement('div');
  title.className = 'diag-title';
  const badge = document.createElement('span');
  badge.className = 'diag-badge';
  badge.textContent = severity === 'warning' ? '有损' : '改写';
  title.appendChild(badge);
  const count = group.nodeIds.length;
  title.appendChild(document.createTextNode(
    arkUiDiagnosticTitle(group) + (count > 1 ? '（' + count + ' 处）' : '')));
  const meta = document.createElement('div');
  meta.className = 'diag-meta';
  const nodes = group.nodeIds.slice(0, 8).join('、');
  meta.textContent = group.code + (nodes
    ? ' · 节点：' + nodes + (count > 8 ? ' 等 ' + count + ' 处' : '')
    : '');
  item.append(title, meta);
  return item;
}

function openArkUiLossDetails(modelName, diagnostics) {
  const warnings = diagnostics.filter(item => item && item.severity === 'warning');
  const notices = diagnostics.filter(item => item && item.severity === 'notice');
  modalRoot.innerHTML = '';
  const overlay = document.createElement('div');
  overlay.className = 'overlay';
  overlay.onclick = (e) => { if (e.target === overlay) closeLog(); };
  const modal = document.createElement('div');
  modal.className = 'modal';
  const head = document.createElement('div');
  head.className = 'modal-head';
  head.innerHTML = '<span class="m-title">' + esc('有损导出明细 · ' + modelName) + '</span>';
  const closeBtn = document.createElement('button');
  closeBtn.textContent = '关闭';
  closeBtn.onclick = closeLog;
  head.appendChild(closeBtn);
  const bodyEl = document.createElement('div');
  bodyEl.className = 'modal-body';
  const summary = document.createElement('p');
  summary.className = 'diag-summary';
  summary.textContent = '工程 zip 已完整下载。「有损」指下面 ' + warnings.length
    + ' 条差异让 ArkUI 工程无法 1:1 还原网页渲染效果：';
  bodyEl.appendChild(summary);
  groupArkUiDiagnostics(warnings).forEach(group => {
    bodyEl.appendChild(renderArkUiDiagnosticGroup(group, 'warning'));
  });
  if (notices.length) {
    const noteHead = document.createElement('p');
    noteHead.className = 'diag-note-head';
    noteHead.textContent = '另有 ' + notices.length
      + ' 条结构性改写（notice），不影响渲染结果：';
    bodyEl.appendChild(noteHead);
    groupArkUiDiagnostics(notices).forEach(group => {
      bodyEl.appendChild(renderArkUiDiagnosticGroup(group, 'notice'));
    });
  }
  modal.append(head, bodyEl);
  overlay.appendChild(modal);
  modalRoot.appendChild(overlay);
  document.addEventListener('keydown', _escClose);
}

function esc(s) {
  return String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
}

function newArkUiCaptureId(prefix) {
  return window.crypto && crypto.randomUUID
    ? prefix + '-' + crypto.randomUUID()
    : prefix + '-' + Date.now() + '-' + Math.random().toString(16).slice(2);
}

function waitForCaptureFrame(frame, captureSession) {
  return new Promise(function(resolve, reject) {
    var settled = false;
    var loaded = false;
    var timer = window.setTimeout(function() {
      var stage = loaded ? '初始化' : '加载或初始化';
      finish(reject, new Error('浏览器样式快照' + stage + '超时'));
    }, 12000);
    function finish(callback, value) {
      if (settled) return;
      settled = true;
      window.clearTimeout(timer);
      window.removeEventListener('message', onMessage);
      frame.removeEventListener('load', onLoad);
      frame.removeEventListener('error', onError);
      callback(value);
    }
    function onLoad() {
      loaded = true;
    }
    function onError() {
      finish(reject, new Error('浏览器样式快照 iframe 加载失败'));
    }
    function onMessage(event) {
      if (event.source !== frame.contentWindow) return;
      var message = event.data;
      if (!message || message.type !== 'uibench-arkui-snapshot-ready') return;
      if (message.session !== captureSession) return;
      // The runtime sends ready only after its request listener is installed.
      // That handshake is authoritative even in browsers which do not emit a
      // reliable iframe load event for detached srcdoc assignment.
      finish(resolve);
    }
    window.addEventListener('message', onMessage);
    frame.addEventListener('load', onLoad);
    frame.addEventListener('error', onError);
  });
}

function requestSnapshotFromFrame(frame, captureSession) {
  return new Promise(function(resolve, reject) {
    var token = newArkUiCaptureId('snapshot-request');
    var timer = window.setTimeout(function() {
      window.removeEventListener('message', onMessage);
      reject(new Error('浏览器样式快照超时'));
    }, 12000);
    function finish(callback, value) {
      window.clearTimeout(timer);
      window.removeEventListener('message', onMessage);
      callback(value);
    }
    function onMessage(event) {
      if (event.source !== frame.contentWindow) return;
      var message = event.data;
      if (!message || message.session !== captureSession || message.token !== token) return;
      if (message.type === 'uibench-arkui-snapshot-response') {
        finish(resolve, message.snapshot);
      } else if (message.type === 'uibench-arkui-snapshot-error') {
        finish(reject, new Error(message.message || '浏览器样式快照失败'));
      }
    }
    window.addEventListener('message', onMessage);
    if (!frame.contentWindow) {
      finish(reject, new Error('浏览器快照 iframe 不可用'));
      return;
    }
    frame.contentWindow.postMessage({
      type: 'uibench-arkui-snapshot-request',
      session: captureSession,
      token: token
    }, '*');
  });
}

async function captureArkUiSnapshot(result) {
  var frame = document.createElement('iframe');
  var captureSession = newArkUiCaptureId('snapshot-capture');
  var captureHtml = injectForRender(
    result.html, 'mobile', currentTheme, currentTokenTheme, captureSession
  );
  frame.setAttribute('sandbox', 'allow-scripts allow-forms allow-modals allow-popups');
  frame.setAttribute('aria-hidden', 'true');
  frame.style.cssText = 'position:fixed;left:-10000px;top:0;width:__UIBENCH_MOBILE_VIEWPORT_WIDTH__px;height:__UIBENCH_MOBILE_VIEWPORT_HEIGHT__px;'
    + 'border:0;opacity:0;pointer-events:none;';
  var readiness = waitForCaptureFrame(frame, captureSession);
  try {
    frame.srcdoc = captureHtml;
    document.body.appendChild(frame);
    await readiness;
    return await requestSnapshotFromFrame(frame, captureSession);
  } finally {
    frame.remove();
  }
}

function formatArkUiBlockReasons(manifest) {
  // Mirrors ComponentMetadataReport.export_readiness (metadata.py): errors
  // always block; missing node ids and renderer-unsupported components block
  // even when they are only warnings (inferred markup); the single-root rule
  // emits no diagnostic of its own, so it is reconstructed from the summary.
  const summary = (manifest && manifest.summary) || {};
  const diagnostics = (manifest && Array.isArray(manifest.diagnostics))
    ? manifest.diagnostics : [];
  const blockingWarningCodes = [
    'ARKUI_NODE_ID_MISSING', 'ARKUI_COMPONENT_NOT_RENDERER_SUPPORTED'
  ];
  const reasons = [];
  if (typeof summary.rootComponents === 'number' && summary.rootComponents !== 1) {
    reasons.push('页面有 ' + summary.rootComponents
      + ' 个根组件，导出要求恰好 1 个根组件');
  }
  diagnostics.forEach(item => {
    if (item.severity !== 'error'
        && blockingWarningCodes.indexOf(item.code) === -1) return;
    let text = item.message || item.code;
    const where = item.nodeId || item.component;
    if (where) text += '（' + where + '）';
    reasons.push(text);
  });
  if (!reasons.length) {
    return 'ArkUI 不可导出：原因未包含在生成结果里，完整诊断见「查看日志」。';
  }
  const shown = reasons.slice(0, 8).map((text, index) => (index + 1) + '. ' + text);
  if (reasons.length > shown.length) {
    shown.push('… 以及另外 ' + (reasons.length - shown.length)
      + ' 条，完整诊断见「查看日志」');
  }
  return 'ArkUI 不可导出，原因：\\n\\n' + shown.join('\\n');
}

function describeExportErrorDetails(details) {
  // Screen IR blocks report a diagnostic list; snapshot and canvas gates report
  // a single object whose reason is the only thing that says what to fix.
  if (Array.isArray(details)) {
    return details.slice(0, 3).map(item => item.message).filter(Boolean).join('；');
  }
  if (!details || typeof details !== 'object') return '';
  const parts = [];
  if (details.reason) parts.push(String(details.reason));
  if (details.nodeId) parts.push('节点 ' + details.nodeId);
  if (Array.isArray(details.missingFields) && details.missingFields.length) {
    parts.push('缺少 ' + details.missingFields.slice(0, 5).join('、'));
  }
  if (details.backgroundColor) parts.push(String(details.backgroundColor));
  if (details.backgroundImage) parts.push(String(details.backgroundImage));
  return parts.join('，');
}

async function requestArkUiExport(result, snapshot) {
  const response = await fetch('/api/arkui/export', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      html: result.html,
      page_name: 'Generated_' + result.key,
      mode: 'annotated',
      viewport_width: __UIBENCH_MOBILE_VIEWPORT_WIDTH__,
      viewport_height: __UIBENCH_MOBILE_VIEWPORT_HEIGHT__,
      snapshot: snapshot
    })
  });
  const payload = await response.json();
  if (!response.ok) {
    const error = payload.error || {};
    const details = describeExportErrorDetails(error.details);
    throw new Error((error.message || ('HTTP ' + response.status)) + (details ? '：' + details : ''));
  }
  if (!payload.bundle
      || typeof payload.bundle.contentBase64 !== 'string'
      || !payload.bundle.contentBase64.trim()) {
    throw new Error('ArkUI 完整工程响应缺少 bundle.contentBase64');
  }
  return payload;
}

function downloadText(filename, content, mimeType) {
  const url = URL.createObjectURL(new Blob([content], {type: mimeType}));
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function withDownloadTimestamp(filename) {
  // The bundle name is deterministic on purpose so regression artifacts stay
  // comparable; the download gets a local timestamp so repeated exports of the
  // same page land side by side instead of as "(1)", "(2)".
  const now = new Date();
  const pad = value => String(value).padStart(2, '0');
  const stamp = String(now.getFullYear()) + pad(now.getMonth() + 1) + pad(now.getDate())
    + '_' + pad(now.getHours()) + pad(now.getMinutes()) + pad(now.getSeconds());
  const dot = filename.lastIndexOf('.');
  return dot > 0
    ? filename.slice(0, dot) + '_' + stamp + filename.slice(dot)
    : filename + '_' + stamp;
}

function downloadBase64(filename, contentBase64, mimeType) {
  const binary = atob(contentBase64);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) {
    bytes[index] = binary.charCodeAt(index);
  }
  const url = URL.createObjectURL(new Blob([bytes], {type: mimeType}));
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}
</script>
</body>
</html>
"""

INDEX_HTML = (
    INDEX_HTML
    .replace(
        "__UIBENCH_MOBILE_VIEWPORT_WIDTH__",
        str(MOBILE_VIEWPORT_WIDTH),
    )
    .replace(
        "__UIBENCH_MOBILE_VIEWPORT_HEIGHT__",
        str(MOBILE_VIEWPORT_HEIGHT),
    )
    .replace("__UIBENCH_IMAGE_SOURCE__", settings.image_source)
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
