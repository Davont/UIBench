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
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, StreamingResponse

from config import settings
from uibench.models import chat_model_for, load_model_registry
from uibench.prompts import MOBILE_GENERATION_PROMPT
from uibench.schemas import GenerateRequest, GenerationResult, ModelConfig

app = FastAPI(title="UIBench", version="0.4.0")

PROJECT_ROOT = Path(__file__).resolve().parent
LOGS_DIR = PROJECT_ROOT / "logs"

_FENCE_RE = re.compile(r"```(?:\w+)?\s*\n(.*?)```", re.DOTALL)
_THINK_RE = re.compile(r"<think>(.*?)</think>", re.DOTALL)

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
               error: str | None) -> None:
    """Archive one model's full output to a markdown log file."""
    try:
        run_dir = LOGS_DIR / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        path = run_dir / f"{key}_{_safe_name(model_cfg.name or model_cfg.id)}.md"
        parts = [
            f"# {model_cfg.name or model_cfg.id}",
            f"- 模型: `{model_cfg.id}`  供应商: {model_cfg.provider}  端点: `{model_cfg.base_url or '默认'}`",
            f"- 运行: `{run_id}`  卡片key: `{key}`",
            f"- 时间: {datetime.now().isoformat(timespec='seconds')}",
            f"- 耗时: {elapsed}s",
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
        if error:
            parts += ["> ⚠️ 生成异常:", "", f"```\n{error}\n```", ""]
        path.write_text("\n".join(parts), encoding="utf-8")
    except Exception:
        # logging must never break the response
        pass


def _write_last_run(run_id: str, prompt_text: str, keyed, results, total: float) -> None:
    """Persist the full result set so a page refresh can restore it."""
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        payload = {
            "run_id": run_id,
            "prompt": prompt_text,
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
                        key: str, run_id: str) -> GenerationResult:
    """Call one model (in a worker thread) and return its rendered result."""
    start = time.perf_counter()
    try:
        chat = chat_model_for(model_cfg)
        messages = MOBILE_GENERATION_PROMPT.invoke({"prompt": prompt_text})

        content = ""
        reasoning = ""

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
            raw = await asyncio.to_thread(
                root_client.chat.completions.create, **kwargs
            )
            msg = raw.choices[0].message
            content = msg.content or ""
            reasoning = (getattr(msg, "reasoning_content", None)
                         or (getattr(msg, "model_extra", None) or {}).get("reasoning_content")
                         or "")
            reasoning = reasoning or ""
        else:
            response = await asyncio.to_thread(chat.invoke, messages)
            content = getattr(response, "content", str(response))
            if isinstance(content, list):
                content = "".join(b.get("text", "") for b in content if isinstance(b, dict))
            reasoning = _extract_reasoning(response, content)

        elapsed = time.perf_counter() - start
        html = extract_html(content)
        if not reasoning:
            reasoning = _extract_reasoning(None, content)
        _write_log(run_id, key, model_cfg, prompt_text, content, reasoning,
                   html, round(elapsed, 2), None)
        return GenerationResult(
            key=key,
            model_id=model_cfg.id,
            name=model_cfg.name or model_cfg.id,
            provider=model_cfg.provider,
            html=html,
            reasoning=reasoning,
            log_url=f"/api/log/{run_id}/{key}",
            elapsed_seconds=round(elapsed, 2),
        )
    except Exception as exc:  # noqa: BLE001 - surface the error on the card
        elapsed = round(time.perf_counter() - start, 2)
        _write_log(run_id, key, model_cfg, prompt_text, "", "", "", elapsed, str(exc))
        return GenerationResult(
            key=key,
            model_id=model_cfg.id,
            name=model_cfg.name or model_cfg.id,
            provider=model_cfg.provider,
            html="",
            reasoning="",
            log_url=f"/api/log/{run_id}/{key}",
            elapsed_seconds=elapsed,
            error=str(exc),
        )


@app.post("/api/generate")
async def generate(req: GenerateRequest):
    """Stream every enabled model's result as NDJSON (one JSON object per line).

    Line 1: {"type":"start","run_id":"...","models":[...]}
    Then:   {"type":"result","result":{...}}   (one per model, in completion order)
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

        queue: asyncio.Queue[GenerationResult] = asyncio.Queue()

        async def worker(i: int, m: ModelConfig) -> None:
            await queue.put(await _generate_one(m, req.prompt, str(i), run_id))

        tasks = [asyncio.create_task(worker(i, m)) for i, m in keyed]
        collected: list[GenerationResult] = []
        remaining = len(models)
        while remaining > 0:
            result = await queue.get()
            remaining -= 1
            collected.append(result)
            yield json.dumps(
                {"type": "result", "result": result.model_dump(mode="json")},
                ensure_ascii=False,
                default=str,
            ) + "\n"

        await asyncio.gather(*tasks)
        total = round(time.perf_counter() - start, 2)
        _write_last_run(run_id, req.prompt, keyed, collected, total)
        yield json.dumps(
            {"type": "done", "total_seconds": total},
            ensure_ascii=False,
        ) + "\n"

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")


@app.get("/api/last")
def last_run():
    """Return the most recent run's full result set (for page-refresh restore)."""
    p = LOGS_DIR / "last_run.json"
    if not p.exists():
        return JSONResponse({"error": "尚无运行记录"}, status_code=404)
    return JSONResponse(json.loads(p.read_text(encoding="utf-8")))


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


def inject_shared_css(html: str) -> str:
    """Inject a <link> to /shared.css into a model's HTML so its internal
    scrollbars also use the mobile style. Handles missing <head>."""
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


@app.get("/", response_class=HTMLResponse)
def index():
    return INDEX_HTML


# --------------------------------------------------------------------------- #
# Single-page UI (self-contained, no external assets)
# --------------------------------------------------------------------------- #
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
  .meta { color: var(--muted); font-size: 13px; min-height: 18px; margin-bottom: 18px; }
  .meta b { color: var(--text); }
  .grid { display: grid; gap: 22px;
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); }
  .card { background: var(--panel); border: 1px solid var(--border);
    border-radius: 14px; overflow: hidden; display: flex; flex-direction: column; }
  .card-head { display: flex; align-items: center; justify-content: space-between;
    padding: 12px 16px; border-bottom: 1px solid var(--border); }
  .titles { display: flex; align-items: center; gap: 10px; min-width: 0; }
  .name { font-weight: 600; font-size: 15px; white-space: nowrap;
    overflow: hidden; text-overflow: ellipsis; }
  .provider { font-size: 11px; color: var(--muted); background: #11141a;
    border: 1px solid var(--border); padding: 2px 8px; border-radius: 999px;
    text-transform: uppercase; letter-spacing: .5px; }
  .time { font-size: 13px; color: var(--time); font-variant-numeric: tabular-nums;
    white-space: nowrap; }
  .card-body { display: flex; flex-direction: column; align-items: center;
    padding: 16px; flex: 1; }
  .tools { display: flex; gap: 8px; margin-bottom: 12px; }
  .tools button { background: #11141a; color: var(--muted); border: 1px solid var(--border);
    border-radius: 8px; padding: 5px 12px; font-size: 12px; cursor: pointer; }
  .tools button:hover { color: var(--text); border-color: var(--accent); }
  .phone { width: 360px; max-width: 100%; height: 640px; border: 0;
    border-radius: 18px; background: #fff;
    box-shadow: 0 8px 30px rgba(0,0,0,.45); }
  .error { color: var(--err); padding: 24px 16px; text-align: center;
    font-size: 14px; word-break: break-word; width: 100%; }
  .empty { color: var(--muted); padding: 48px 16px; text-align: center; width: 100%; }
  @keyframes shimmer { 0%{background-position:-400px 0} 100%{background-position:400px 0} }
  .skeleton { width: 360px; max-width: 100%; height: 640px; border-radius: 18px;
    background: linear-gradient(90deg, #11141a 0px, #1c212b 200px, #11141a 400px);
    background-size: 800px 100%; animation: shimmer 1.3s infinite linear; }
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
</style>
</head>
<body>
<header>
  <h1>UI<span>Bench</span></h1>
  <p class="sub">输入一句话的移动端 UI 需求，并行调用多个模型，同屏渲染对比并显示每个模型耗时</p>
</header>
<main>
  <form id="form">
    <textarea id="prompt" placeholder="例如：一个带顶部搜索框、商品轮播图和底部 Tab 导航的电商首页"></textarea>
    <button id="btn" type="submit">生成对比</button>
  </form>
  <div id="meta" class="meta"></div>
  <div id="results" class="grid"></div>
</main>
<div id="modal-root"></div>
<script>
const form = document.getElementById('form');
const btn = document.getElementById('btn');
const promptEl = document.getElementById('prompt');
const resultsEl = document.getElementById('results');
const metaEl = document.getElementById('meta');
const modalRoot = document.getElementById('modal-root');

let count = 0, done = 0;

function applyStart(models) {
  count = models.length; done = 0;
  metaEl.innerHTML = '<span class="spin"></span>共 ' + count + ' 个模型生成中…';
  resultsEl.innerHTML = '';
  models.forEach(m => resultsEl.appendChild(makeCard(m)));
}
function applyResult(r) {
  fillCard(r);
  done++;
  if (done < count) metaEl.innerHTML = '<span class="spin"></span>已完成 ' + done + '/' + count + '…';
}
function applyDone(total) {
  metaEl.innerHTML = '共 <b>' + count + '</b> 个模型 · 并行总耗时 <b>' + total + 's</b>';
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const prompt = promptEl.value.trim();
  if (!prompt) return;
  btn.disabled = true;
  const oldText = btn.textContent;
  btn.textContent = '生成中…';
  try {
    const resp = await fetch('/api/generate', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({prompt})
    });
    if (!resp.ok) {
      const t = await resp.text();
      metaEl.innerHTML = '<span style="color:var(--err)">' + esc(t) + '</span>';
      return;
    }
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
        const msg = JSON.parse(line);
        if (msg.type === 'start') applyStart(msg.models);
        else if (msg.type === 'result') applyResult(msg.result);
        else if (msg.type === 'done') applyDone(msg.total_seconds);
      }
      if (rd) break;
    }
  } catch (err) {
    metaEl.innerHTML = '<span style="color:var(--err)">请求失败：' + esc(String(err)) + '</span>';
  } finally {
    btn.disabled = false;
    btn.textContent = oldText;
  }
});

// restore the last run after a page refresh
async function restoreLast() {
  try {
    const resp = await fetch('/api/last');
    if (!resp.ok) return;
    const data = await resp.json();
    if (data.prompt) promptEl.value = data.prompt;
    applyStart(data.models || []);
    (data.results || []).forEach(r => applyResult(r));
    applyDone(data.total_seconds);
  } catch (e) { /* ignore - no prior run */ }
}
restoreLast();

function makeCard(m) {
  const card = document.createElement('section');
  card.className = 'card';
  card.dataset.key = m.key;
  const head = document.createElement('div');
  head.className = 'card-head';
  head.innerHTML =
    '<div class="titles"><span class="name">' + esc(m.name) + '</span>' +
    '<span class="provider">' + esc(m.provider) + '</span></div>' +
    '<span class="time">生成中…</span>';
  const body = document.createElement('div');
  body.className = 'card-body';
  body.innerHTML = '<div class="skeleton"></div>';
  card.append(head, body);
  return card;
}

function fillCard(r) {
  const cards = resultsEl.querySelectorAll('.card');
  let card = null;
  for (const c of cards) {
    if (c.dataset.key === String(r.key)) { card = c; break; }
  }
  if (!card) return;
  card.querySelector('.time').textContent = '⏱ ' + r.elapsed_seconds + 's';
  const body = card.querySelector('.card-body');
  body.innerHTML = '';

  // tools (always available so the log is reachable even on error/empty)
  const tools = document.createElement('div');
  tools.className = 'tools';
  const logBtn = document.createElement('button');
  logBtn.textContent = '查看日志';
  logBtn.onclick = () => openLog(r.log_url, r.name + ' · ⏱ ' + r.elapsed_seconds + 's');
  tools.appendChild(logBtn);

  if (r.error) {
    tools.style.marginBottom = '0';
    body.appendChild(tools);
    const err = document.createElement('div');
    err.className = 'error';
    err.textContent = '生成失败：' + r.error;
    body.appendChild(err);
    return;
  }
  if (r.html) {
    const copy = document.createElement('button');
    copy.textContent = '复制 HTML';
    copy.onclick = () => {
      navigator.clipboard.writeText(r.html).then(() => {
        copy.textContent = '已复制'; setTimeout(() => copy.textContent = '复制 HTML', 1500);
      });
    };
    const open = document.createElement('button');
    open.textContent = '新标签打开';
    open.onclick = () => {
      const b = new Blob([injectSharedCss(r.html)], {type: 'text/html'});
      window.open(URL.createObjectURL(b), '_blank');
    };
    tools.append(copy, open);
    body.appendChild(tools);
    const iframe = document.createElement('iframe');
    iframe.className = 'phone';
    iframe.setAttribute('sandbox', 'allow-scripts allow-forms allow-modals allow-popups');
    iframe.srcdoc = injectSharedCss(r.html);
    body.appendChild(iframe);
  } else {
    body.appendChild(tools);
    const empty = document.createElement('div');
    empty.className = 'empty';
    empty.textContent = '模型未返回 HTML';
    body.appendChild(empty);
  }
}

function injectSharedCss(html) {
  const link = '<link rel="stylesheet" href="/shared.css">';
  const low = html.toLowerCase();
  let idx = low.indexOf('<head>');
  if (idx !== -1) { const at = idx + 6; return html.slice(0, at) + link + html.slice(at); }
  idx = low.indexOf('<html');
  if (idx !== -1) {
    const at = low.indexOf('>', idx);
    if (at !== -1) return html.slice(0, at + 1) + '<head>' + link + '</head>' + html.slice(at + 1);
  }
  return link + html;
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

function esc(s) {
  return String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
}
</script>
</body>
</html>
"""


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
