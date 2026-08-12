"""End-to-end API tests using fake chat models (no API keys needed)."""
import asyncio
import json
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from langchain_core.language_models.fake_chat_models import FakeListChatModel

import app as app_mod

CANNED_HTML = (
    "```html\n<!DOCTYPE html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
    "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
    "<title>Demo</title><style>body{margin:0;font-family:sans-serif}"
    ".bar{padding:16px;background:#4f8cff;color:#fff}</style></head>"
    "<body><div class=\"bar\">Hello</div></body></html>\n```"
)

CANNED_REASONING = "我先想一下：需要顶部搜索框和底部 Tab 导航。"
CANNED_HTML_WITH_REASON = (
    "```html\n<!DOCTYPE html><html><head></head><body>hi</body></html>\n```"
)

# records kwargs of every create() call made by the reasoning stub
_REASONING_CALLS: list[dict] = []


def _fake_factory(*args, **kwargs):
    return FakeListChatModel(responses=[CANNED_HTML] * 100)


class _FakeMsg:
    def __init__(self) -> None:
        self.content = CANNED_HTML_WITH_REASON
        self.reasoning_content = CANNED_REASONING
        self.model_extra = {"reasoning_content": CANNED_REASONING}


def _reasoning_factory(*args, **kwargs):
    msg = _FakeMsg()

    def _create(**k):
        _REASONING_CALLS.append(k)
        return SimpleNamespace(choices=[SimpleNamespace(message=msg)])

    completions = SimpleNamespace(create=_create)
    return SimpleNamespace(root_client=SimpleNamespace(
        chat=SimpleNamespace(completions=completions)))


def _openai_response(content: str, reasoning: str, finish_reason: str,
                     *, prompt_tokens: int = 10, completion_tokens: int = 20,
                     reasoning_tokens: int = 5, tool_calls=None):
    msg = SimpleNamespace(
        content=content,
        reasoning_content=reasoning,
        model_extra={"reasoning_content": reasoning},
        tool_calls=tool_calls or [],
    )
    usage = SimpleNamespace(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        completion_tokens_details=SimpleNamespace(reasoning_tokens=reasoning_tokens),
    )
    return SimpleNamespace(
        choices=[SimpleNamespace(message=msg, finish_reason=finish_reason)],
        usage=usage,
    )


@pytest.fixture(autouse=True)
def _disable_image_tools(monkeypatch):
    """Keep the baseline suite offline even when local MCP config exists."""
    monkeypatch.setattr(app_mod, "image_tool_available", lambda: False)


@pytest.fixture()
def client(monkeypatch, tmp_path):
    monkeypatch.setattr(app_mod, "chat_model_for", _fake_factory)
    monkeypatch.setattr(app_mod, "LOGS_DIR", tmp_path / "logs")
    with TestClient(app_mod.app) as c:
        yield c


@pytest.fixture()
def reasoning_client(monkeypatch, tmp_path):
    _REASONING_CALLS.clear()
    monkeypatch.setattr(app_mod, "chat_model_for", _reasoning_factory)
    monkeypatch.setattr(app_mod, "LOGS_DIR", tmp_path / "logs")
    with TestClient(app_mod.app) as c:
        yield c


def _parse_stream(resp):
    return [json.loads(line) for line in resp.text.splitlines() if line.strip()]


def _results(messages):
    return [m["result"] for m in messages if m["type"] == "result"]


def _first_result(messages):
    return _results(messages)[0]


def _progress(messages, key: str | None = None):
    events = [m for m in messages if m["type"] == "progress"]
    if key is not None:
        events = [m for m in events if m["key"] == key]
    return events


def test_index_page(client) -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    assert "UIBench" in resp.text
    assert "function applyProgress" in resp.text
    assert "prefers-reduced-motion: reduce" in resp.text
    assert 'aria-live="polite"' in resp.text
    assert 'aria-busy="false"' in resp.text
    assert "生成流提前结束" in resp.text
    assert "iframe.title" in resp.text
    assert "const head = document.createElement('div')" in resp.text
    assert "head.className = 'card-head'" in resp.text
    assert 'class="head-status"' in resp.text
    assert "function formatSeconds" in resp.text
    assert "progress-content" not in resp.text
    assert "progress-log" not in resp.text
    assert "summary-chevron" not in resp.text
    assert "已加入并行生成队列" not in resp.text
    assert "stage === 'preparing' || stage === 'generating'" in resp.text
    assert '<input id="arkui-export" type="checkbox">' in resp.text
    assert '<input id="arkui-export" type="checkbox" checked>' not in resp.text


def test_generate_stream(client) -> None:
    resp = client.post("/api/generate", json={"prompt": "一个登录页"})
    assert resp.status_code == 200
    messages = _parse_stream(resp)
    types = [m["type"] for m in messages]
    assert types[0] == "start"
    assert types[-1] == "done"
    results = _results(messages)
    progress = _progress(messages)
    assert progress
    assert any(
        event["stage"] == "generating"
        and event["message"] == "正在请求模型，等待生成"
        for event in progress
    )
    assert len(results) >= 1
    first = results[0]
    assert "<!DOCTYPE html>" in first["html"]
    assert first["elapsed_seconds"] >= 0
    assert first["error"] is None
    assert first["arkui_export_enabled"] is False
    assert first["arkui_manifest"] == {}
    assert len(messages[0]["models"]) == len(results)
    assert messages[0]["run_id"]
    assert resp.headers["cache-control"] == "no-cache"
    assert resp.headers["x-accel-buffering"] == "no"

    allowed_stages = {
        "preparing", "generating", "processing", "recovering",
        "searching_images", "finalizing", "failed",
    }
    for event in progress:
        assert set(event) == {
            "type", "key", "stage", "message", "elapsed_seconds"
        }
        assert event["stage"] in allowed_stages
        assert event["elapsed_seconds"] >= 0
        serialized = json.dumps(event, ensure_ascii=False)
        assert CANNED_REASONING not in serialized
        assert "<!DOCTYPE html>" not in serialized

    for result in results:
        key = result["key"]
        model_progress = _progress(messages, key)
        stages = [event["stage"] for event in model_progress]
        assert stages[0] == "preparing"
        assert "generating" in stages
        assert "processing" in stages
        assert stages[-1] == "finalizing"
        elapsed = [event["elapsed_seconds"] for event in model_progress]
        assert elapsed == sorted(elapsed)
        result_index = next(
            i for i, event in enumerate(messages)
            if event["type"] == "result" and event["result"]["key"] == key
        )
        assert all(messages.index(event) < result_index for event in model_progress)


def test_openai_role_mapping(reasoning_client) -> None:
    """langchain 'human' must be sent to the OpenAI API as 'user'."""
    resp = reasoning_client.post("/api/generate", json={"prompt": "电商首页"})
    assert resp.status_code == 200
    assert _REASONING_CALLS
    roles = [m["role"] for m in _REASONING_CALLS[0]["messages"]]
    assert "human" not in roles
    assert "user" in roles
    assert "system" in roles


def test_generate_stream_extracts_annotated_arkui_manifest(
    monkeypatch, tmp_path,
) -> None:
    from uibench.schemas import ModelConfig

    annotated_html = (
        "<!DOCTYPE html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        "<title>ArkUI metadata</title></head><body>"
        "<main data-node-id=\"home\" data-component=\"scroll\">"
        "<section data-node-id=\"home-content\" data-component=\"column\">"
        "<button data-node-id=\"home-submit\" data-component=\"button\" "
        "data-action=\"submit\">提交</button>"
        "</section></main></body></html>"
    )
    logs_dir = tmp_path / "logs"
    monkeypatch.setattr(
        app_mod,
        "chat_model_for",
        lambda *args, **kwargs: FakeListChatModel(
            responses=[annotated_html] * 10
        ),
    )
    monkeypatch.setattr(app_mod, "LOGS_DIR", logs_dir)
    monkeypatch.setattr(app_mod, "load_model_registry", lambda: [
        ModelConfig(
            id="arkui-metadata-test",
            provider="openai",
            name="ArkUI Metadata Test",
        )
    ])

    with TestClient(app_mod.app) as test_client:
        response = test_client.post(
            "/api/generate",
            json={
                "prompt": "生成一个提交页",
                "arkui_export_enabled": True,
            },
        )

    assert response.status_code == 200
    result = _first_result(_parse_stream(response))
    manifest = result["arkui_manifest"]
    assert result["arkui_export_enabled"] is True
    assert manifest["kind"] == "uibench-component-manifest"
    assert manifest["manifestVersion"] == 1
    assert manifest["screenIrSchemaVersion"] == 2
    assert manifest["summary"]["componentCounts"] == {
        "button": 1,
        "column": 1,
        "scroll": 1,
    }
    assert manifest["summary"]["explicitComponents"] == 3
    assert manifest["summary"]["inferredComponents"] == 0
    assert manifest["summary"]["addressableCoverage"] == 1.0
    assert manifest["diagnostics"] == []

    model_logs = list(logs_dir.glob("*/*.md"))
    assert len(model_logs) == 1
    log_text = model_logs[0].read_text(encoding="utf-8")
    assert "## ArkUI 组件 Manifest" in log_text
    assert '"arkuiComponent": "Button"' in log_text


def test_generate_repairs_button_label_id_before_preview_and_manifest(
    monkeypatch, tmp_path,
) -> None:
    from uibench.schemas import ModelConfig

    annotated_html = (
        '<!DOCTYPE html><html lang="zh-CN"><head><title>ArkUI</title></head>'
        '<body><main data-node-id="page" data-component="column">'
        '<button data-node-id="page.more" data-component="button">'
        '<span data-component="text">查看全部</span>'
        '</button></main></body></html>'
    )
    monkeypatch.setattr(
        app_mod,
        "chat_model_for",
        lambda *args, **kwargs: FakeListChatModel(
            responses=[annotated_html] * 10
        ),
    )
    monkeypatch.setattr(app_mod, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(app_mod, "load_model_registry", lambda: [
        ModelConfig(
            id="arkui-id-repair-test",
            provider="openai",
            name="ArkUI ID Repair Test",
        )
    ])

    with TestClient(app_mod.app) as test_client:
        response = test_client.post(
            "/api/generate",
            json={
                "prompt": "生成一个更多按钮",
                "arkui_export_enabled": True,
            },
        )

    result = _first_result(_parse_stream(response))
    manifest = result["arkui_manifest"]
    assert 'data-node-id="page.more.label"' in result["html"]
    assert manifest["summary"]["exportReadiness"] == "ready"
    assert manifest["summary"]["errors"] == 0
    assert manifest["summary"]["notices"] == 1
    assert [item["code"] for item in manifest["diagnostics"]] == [
        "ARKUI_NODE_ID_GENERATED",
    ]


def test_reasoning_effort_passed_when_set(monkeypatch, tmp_path) -> None:
    """A model with reasoning_effort set must forward it to the API."""
    from uibench.schemas import ModelConfig
    captured: list[dict] = []

    def _factory(*a, **k):
        msg = _FakeMsg()

        def _create(**kk):
            captured.append(kk)
            return SimpleNamespace(choices=[SimpleNamespace(message=msg)])
        return SimpleNamespace(root_client=SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=_create))))

    # patch the registry to a single deepseek-style model with effort=high
    monkeypatch.setattr(app_mod, "chat_model_for", _factory)
    monkeypatch.setattr(app_mod, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(app_mod, "load_model_registry", lambda: [
        ModelConfig(id="deepseek-v4-flash", provider="openai",
                    name="DeepSeek v4 Flash (官方)",
                    base_url="https://api.deepseek.com/v1",
                    api_key="sk-x", reasoning_effort="high")
    ])
    with TestClient(app_mod.app) as c:
        resp = c.post("/api/generate", json={"prompt": "x"})
    assert resp.status_code == 200
    assert captured
    call = captured[0]
    assert call["reasoning_effort"] == "high"
    assert call["extra_body"] == {"thinking": {"type": "enabled"}}


def test_no_reasoning_effort_when_unset(client) -> None:
    """DashScope-style models (no reasoning_effort) must not send thinking params."""
    # the default client fixture uses FakeListChatModel (no root_client -> invoke path)
    # so nothing to assert on the wire; this just guards the field defaults to None
    from uibench.schemas import ModelConfig
    m = ModelConfig(id="qwen3.7-plus", provider="openai")
    assert m.reasoning_effort is None


def _system_text(calls) -> str:
    for m in calls[0]["messages"]:
        if m["role"] == "system":
            return m["content"]
    return ""


def test_default_mode_is_mobile(reasoning_client) -> None:
    resp = reasoning_client.post("/api/generate", json={"prompt": "电商首页"})
    assert resp.status_code == 200
    assert _REASONING_CALLS
    assert "Tailwind" in _system_text(_REASONING_CALLS)
    assert "最终 answer/content" in _system_text(_REASONING_CALLS)
    assert "不要使用 Markdown 代码围栏" in _system_text(_REASONING_CALLS)
    first = _first_result(_parse_stream(resp))
    assert first["mode"] == "mobile"


def test_pc_mode_uses_pc_prompt(reasoning_client) -> None:
    resp = reasoning_client.post("/api/generate", json={"prompt": "后台仪表盘", "mode": "pc"})
    assert resp.status_code == 200
    assert _REASONING_CALLS
    sys_text = _system_text(_REASONING_CALLS)
    assert "Ant Design" in sys_text
    assert "ECharts" in sys_text
    assert "React" in sys_text
    assert "Tailwind" in sys_text
    first = _first_result(_parse_stream(resp))
    assert first["mode"] == "pc"
    assert first["arkui_manifest"] == {}


def test_reasoning_captured_and_archived(reasoning_client, tmp_path) -> None:
    resp = reasoning_client.post(
        "/api/generate",
        json={"prompt": "电商首页", "arkui_export_enabled": True},
    )
    assert resp.status_code == 200
    messages = _parse_stream(resp)
    run_id = messages[0]["run_id"]
    first = _first_result(messages)
    assert first["reasoning"] == CANNED_REASONING
    assert first["log_url"] == f"/api/log/{run_id}/{first['key']}"

    files = list((tmp_path / "logs" / run_id).glob("*.md"))
    assert files
    on_disk = files[0].read_text(encoding="utf-8")
    assert CANNED_REASONING in on_disk
    assert "## 思考过程" in on_disk
    assert "## ArkUI 组件 Manifest" in on_disk
    assert '"kind": "uibench-component-manifest"' in on_disk
    assert '"schemaVersion": 1' in on_disk

    log_resp = reasoning_client.get(first["log_url"])
    assert log_resp.status_code == 200
    assert CANNED_REASONING in log_resp.text


def test_log_not_found(reasoning_client) -> None:
    assert reasoning_client.get("/api/log/nope/0").status_code == 404


def test_last_run_404_when_none(client) -> None:
    assert client.get("/api/last").status_code == 404


def test_last_run_restorable(reasoning_client, tmp_path) -> None:
    resp = reasoning_client.post("/api/generate", json={"prompt": "电商首页"})
    assert resp.status_code == 200
    last = reasoning_client.get("/api/last")
    assert last.status_code == 200
    data = last.json()
    assert data["prompt"] == "电商首页"
    assert data["run_id"]
    assert data["mode"] == "mobile"
    assert data["models"]
    assert data["results"]
    assert data["results"][0]["log_url"].startswith("/api/log/")
    assert data["results"][0]["mode"] == "mobile"
    # both last_run.json and per-run run.json are persisted
    assert (tmp_path / "logs" / "last_run.json").exists()
    assert (tmp_path / "logs" / data["run_id"] / "run.json").exists()


def test_last_run_repairs_button_label_id_before_restored_preview(
    monkeypatch, tmp_path,
) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    html = (
        '<!DOCTYPE html><html><body>'
        '<main data-node-id="page" data-component="column">'
        '<button data-node-id="page.more" data-component="button">'
        '<span data-component="text">查看全部</span>'
        '</button></main></body></html>'
    )
    (logs / "last_run.json").write_text(json.dumps({
        "run_id": "arkui-repair",
        "prompt": "更多按钮",
        "mode": "mobile",
        "arkui_export_enabled": True,
        "total_seconds": 1,
        "models": [],
        "results": [{
            "key": "0",
            "model_id": "model",
            "name": "Model",
            "provider": "openai",
            "mode": "mobile",
            "html": html,
            "status": "success",
            "arkui_export_enabled": True,
            "arkui_manifest": {},
            "error": None,
        }],
    }), encoding="utf-8")
    monkeypatch.setattr(app_mod, "LOGS_DIR", logs)

    with TestClient(app_mod.app) as client:
        response = client.get("/api/last")

    result = response.json()["results"][0]
    assert 'data-node-id="page.more.label"' in result["html"]
    assert result["arkui_manifest"]["summary"]["exportReadiness"] == "ready"
    assert [item["code"] for item in result["arkui_manifest"]["diagnostics"]] == [
        "ARKUI_NODE_ID_GENERATED",
    ]


def test_legacy_last_run_warns_without_blocking_unapproved_remote_images(
    monkeypatch, tmp_path,
) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / "last_run.json").write_text(json.dumps({
        "run_id": "legacy",
        "prompt": "画廊",
        "mode": "mobile",
        "total_seconds": 1,
        "models": [],
        "results": [{
            "key": "0",
            "model_id": "legacy-model",
            "name": "Legacy",
            "provider": "openai",
            "html": (
                '<!DOCTYPE html><html><body>'
                '<img src="https://images.unsplash.com/photo-invented">'
                '</body></html>'
            ),
            "image_tool_used": False,
            "image_count": 0,
            "image_error": "",
            "error": None,
        }],
    }), encoding="utf-8")
    monkeypatch.setattr(app_mod, "LOGS_DIR", logs)

    with TestClient(app_mod.app) as client:
        response = client.get("/api/last")

    result = response.json()["results"][0]
    assert result["status"] == "degraded"
    assert "photo-invented" in result["html"]
    assert result["error"] is None
    assert "历史结果包含未经图片工具批准" in result["image_error"]
    assert "已继续预览" in result["image_error"]


def test_shared_css(client) -> None:
    resp = client.get("/shared.css")
    assert resp.status_code == 200
    assert "scrollbar-width" in resp.text
    assert "::-webkit-scrollbar" in resp.text


def test_inject_shared_css_into_head() -> None:
    html = "<html><head><title>x</title></head><body></body></html>"
    out = app_mod.inject_shared_css(html)
    assert "/shared.css" in out
    assert out.index("<link") < out.index("<title>")


def test_inject_shared_css_no_head() -> None:
    html = "<html><body>hi</body></html>"
    out = app_mod.inject_shared_css(html)
    assert '<head><link rel="stylesheet" href="/shared.css"></head>' in out


def test_inject_shared_css_neither() -> None:
    html = "<div>hi</div>"
    out = app_mod.inject_shared_css(html)
    assert out.startswith('<link rel="stylesheet" href="/shared.css">')


def test_inject_pc_bootstrap_after_babel() -> None:
    html = ('<html><head>'
            '<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>'
            '<script type="text/babel" data-presets="react">const A=1;</script>'
            '</head><body></body></html>')
    out = app_mod.inject_pc_bootstrap(html)
    # registers react-classic right after the babel loader
    assert "registerPreset(\"react-classic\"" in out
    assert out.index("react-classic") > out.index("babel.min.js")
    # the text/babel script now points at react-classic
    assert 'data-presets="react-classic"' in out
    assert 'data-presets="react"' not in out


def test_inject_pc_bootstrap_includes_error_handler() -> None:
    html = ('<html><head>'
            '<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>'
            '</head><body></body></html>')
    out = app_mod.inject_pc_bootstrap(html)
    # global error handler surfaces Babel/runtime errors on a blank root
    # instead of leaving the card white-screened
    assert 'addEventListener("error"' in out
    assert '渲染失败' in out
    assert 'getElementById("root")' in out


def test_inject_for_render_pc_combines() -> None:
    html = ('<html><head><script src="https://unpkg.com/@babel/standalone/babel.min.js">'
            '</script></head><body></body></html>')
    out = app_mod.inject_for_render(html, "pc")
    assert "/shared.css" in out
    assert "react-classic" in out
    assert 'runtime:"classic"' in out


def test_inject_for_render_mobile_no_bootstrap() -> None:
    html = "<html><head></head><body></body></html>"
    out = app_mod.inject_for_render(html, "mobile")
    assert "/shared.css" in out
    assert "react-classic" not in out


def test_empty_prompt_rejected(client) -> None:
    resp = client.post("/api/generate", json={"prompt": ""})
    assert resp.status_code == 422


def test_extract_html_picks_code_block():
    raw = "intro\n```html\n<html></html>\n```\ntail"
    assert app_mod.extract_html(raw) == "<html></html>"


def test_extract_html_handles_truncated_no_closing_fence():
    raw = "```html\n<!DOCTYPE html><html><body>hi</body></html>"
    assert app_mod.extract_html(raw) == "<!DOCTYPE html><html><body>hi</body></html>"


def test_extract_complete_html_rejects_truncated_document():
    raw = "```html\n<!DOCTYPE html><html><body><form>"
    assert app_mod.extract_complete_html(raw) == ""


def test_extract_complete_html_accepts_raw_document():
    raw = "说明文字\n<!DOCTYPE html><html><body>hi</body></html>\n尾部文字"
    assert app_mod.extract_complete_html(raw) == (
        "<!DOCTYPE html><html><body>hi</body></html>"
    )


def test_complete_html_can_fall_back_to_reasoning(monkeypatch, tmp_path) -> None:
    from uibench.schemas import ModelConfig

    calls: list[dict] = []

    def _factory(*args, **kwargs):
        def _create(**call_kwargs):
            calls.append(call_kwargs)
            return _openai_response("", CANNED_HTML_WITH_REASON, "stop")
        return SimpleNamespace(root_client=SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=_create))))

    monkeypatch.setattr(app_mod, "chat_model_for", _factory)
    monkeypatch.setattr(app_mod, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(app_mod, "load_model_registry", lambda: [
        ModelConfig(id="thinking-model", provider="openai", api_key="sk-test")
    ])
    with TestClient(app_mod.app) as client:
        messages = _parse_stream(client.post(
            "/api/generate", json={"prompt": "登录页"}
        ))

    result = _first_result(messages)
    assert result["error"] is None
    assert result["html_source"] == "reasoning"
    assert "<html>" in result["html"]
    assert result["recovered"] is False
    assert len(calls) == 1


def test_incomplete_reasoning_triggers_one_code_only_recovery(
    monkeypatch, tmp_path,
) -> None:
    from uibench.schemas import ModelConfig

    calls: list[dict] = []
    responses = [
        _openai_response(
            "", "先确定暖色登录页。```html\n<html><body><form>", "length",
            prompt_tokens=100, completion_tokens=4096, reasoning_tokens=4000,
        ),
        _openai_response(
            CANNED_HTML_WITH_REASON, "", "stop",
            prompt_tokens=200, completion_tokens=300, reasoning_tokens=0,
        ),
    ]

    def _factory(*args, **kwargs):
        def _create(**call_kwargs):
            calls.append(call_kwargs)
            return responses[len(calls) - 1]
        return SimpleNamespace(root_client=SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=_create))))

    monkeypatch.setattr(app_mod, "chat_model_for", _factory)
    monkeypatch.setattr(app_mod, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(app_mod, "load_model_registry", lambda: [
        ModelConfig(id="thinking-model", provider="openai", api_key="sk-test")
    ])
    with TestClient(app_mod.app) as client:
        messages = _parse_stream(client.post(
            "/api/generate", json={"prompt": "登录页"}
        ))

    result = _first_result(messages)
    assert result["error"] is None
    assert result["html_source"] == "recovery-content"
    assert result["recovered"] is True
    assert result["finish_reason"] == "length"
    assert result["recovery_finish_reason"] == "stop"
    assert result["prompt_tokens"] == 300
    assert result["completion_tokens"] == 4396
    assert result["reasoning_tokens"] == 4000
    assert len(calls) == 2
    assert calls[1]["extra_body"] == {"thinking": {"type": "disabled"}}
    assert "<design_context>" in calls[1]["messages"][-1]["content"]
    assert "recovering" in [event["stage"] for event in _progress(messages, "0")]


def test_incomplete_after_recovery_is_reported_as_error(monkeypatch, tmp_path) -> None:
    from uibench.schemas import ModelConfig

    calls: list[dict] = []

    def _factory(*args, **kwargs):
        def _create(**call_kwargs):
            calls.append(call_kwargs)
            return _openai_response("", "```html\n<html><body>", "length")
        return SimpleNamespace(root_client=SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=_create))))

    monkeypatch.setattr(app_mod, "chat_model_for", _factory)
    monkeypatch.setattr(app_mod, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(app_mod, "load_model_registry", lambda: [
        ModelConfig(id="thinking-model", provider="openai", api_key="sk-test")
    ])
    with TestClient(app_mod.app) as client:
        messages = _parse_stream(client.post(
            "/api/generate", json={"prompt": "登录页"}
        ))

    result = _first_result(messages)
    assert result["html"] == ""
    assert result["recovered"] is True
    assert "模型未返回完整 HTML" in result["error"]
    assert "已自动进行一次无思考恢复" in result["error"]
    assert len(calls) == 2
    assert "recovering" in [event["stage"] for event in _progress(messages, "0")]


def test_openai_image_tool_loop(monkeypatch, tmp_path) -> None:
    """A model tool request is fulfilled by MCP before final HTML generation."""
    from uibench.schemas import ModelConfig

    image_url = "https://images.unsplash.com/photo-test"
    tool_call = SimpleNamespace(
        id="call_image_1",
        function=SimpleNamespace(
            name="search_photos",
            arguments=json.dumps({
                "requests": [
                    {
                        "slot": "hero-banner",
                        "query": "tropical beach resort",
                        "orientation": "portrait",
                    },
                    {
                        "slot": "beach-bag",
                        "query": "summer beach bag product",
                        "orientation": "squarish",
                    },
                ],
            }),
        ),
    )
    second_image_url = "https://images.unsplash.com/photo-bag"
    final_html = (
        '<!DOCTYPE html><html><head></head><body>'
        f'<img src="{image_url}" alt="Beach">'
        f'<img src="{second_image_url}" alt="Beach bag">'
        '<a href="https://unsplash.com/@photographer?utm_source=uibench&amp;utm_medium=referral">'
        'Photo by Example on Unsplash</a></body></html>'
    )
    responses = [
        _openai_response("", "", "tool_calls", tool_calls=[tool_call]),
        _openai_response(final_html, "", "stop"),
    ]
    calls: list[dict] = []

    def _factory(*args, **kwargs):
        def _create(**call_kwargs):
            calls.append(call_kwargs)
            return responses[len(calls) - 1]
        return SimpleNamespace(root_client=SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=_create))))

    async def _search(arguments, *, max_requests, progress=None):
        assert max_requests == 6
        assert [item["query"] for item in arguments["requests"]] == [
            "tropical beach resort", "summer beach bag product",
        ]
        photos = [
            {
                "id": "photo-test",
                "slot": "hero-banner",
                "query": "tropical beach resort",
                "description": "A tropical beach",
                "urls": {"small": image_url, "regular": image_url + "?w=1080"},
                "width": 1080,
                "height": 1620,
                "photographer": "Example",
                "photographer_url": "https://unsplash.com/@photographer?utm_source=uibench&utm_medium=referral",
                "unsplash_url": "https://unsplash.com/?utm_source=uibench&utm_medium=referral",
                "download_location": "https://api.unsplash.com/photos/photo-test/download",
            },
            {
                "id": "photo-bag",
                "slot": "beach-bag",
                "query": "summer beach bag product",
                "description": "A beach bag",
                "urls": {"small": second_image_url, "regular": second_image_url + "?w=1080"},
                "width": 1080,
                "height": 1080,
                "photographer": "Example",
                "photographer_url": "https://unsplash.com/@photographer?utm_source=uibench&utm_medium=referral",
                "unsplash_url": "https://unsplash.com/?utm_source=uibench&utm_medium=referral",
                "download_location": "https://api.unsplash.com/photos/photo-bag/download",
            },
        ]
        if progress is not None:
            for index, request in enumerate(arguments["requests"]):
                await progress(index + 1, len(arguments["requests"]), request["slot"])
        return photos

    async def _track(photos, html):
        assert len(photos) == 2
        assert image_url in html and second_image_url in html
        return 2

    monkeypatch.setattr(app_mod, "image_tool_available", lambda: True)
    monkeypatch.setattr(app_mod, "call_unsplash_mcp_batch", _search)
    monkeypatch.setattr(app_mod, "track_used_photos", _track)
    monkeypatch.setattr(app_mod, "chat_model_for", _factory)
    monkeypatch.setattr(app_mod, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(app_mod, "load_model_registry", lambda: [
        ModelConfig(id="tool-model", provider="openai", api_key="sk-test")
    ])

    with TestClient(app_mod.app) as client:
        messages = _parse_stream(client.post(
            "/api/generate", json={"prompt": "海边度假详情页"}
        ))

    result = _first_result(messages)
    assert len(calls) == 2
    assert calls[0]["tools"] == [app_mod.UNSPLASH_TOOL]
    assert calls[0]["tool_choice"] == "required"
    assert calls[1]["tool_choice"] == "none"
    assert calls[1]["messages"][-2]["role"] == "assistant"
    assert calls[1]["messages"][-1]["role"] == "tool"
    assert image_url in calls[1]["messages"][-1]["content"]
    assert second_image_url in calls[1]["messages"][-1]["content"]
    assert '"slot": "hero-banner"' in calls[1]["messages"][-1]["content"]
    assert result["error"] is None
    assert result["image_tool_used"] is True
    assert result["image_count"] == 2
    assert result["image_required"] == 2
    assert result["image_used"] == 2
    assert result["status"] == "success"
    assert result["image_queries"] == [
        "tropical beach resort", "summer beach bag product",
    ]
    assert result["image_tracked"] == 2
    assert "searching_images" in [
        event["stage"] for event in _progress(messages, "0")
    ]


def test_product_prompt_enforces_fallback_slots_and_repairs_image_usage(
    monkeypatch, tmp_path,
) -> None:
    """Legacy broad queries cannot leave a product grid as empty placeholders."""
    from uibench.schemas import ModelConfig

    legacy_tool_call = SimpleNamespace(
        id="call_legacy_image",
        function=SimpleNamespace(
            name="search_photos",
            arguments=json.dumps({
                "query": "shopping mall banner",
                "per_page": 2,
            }),
        ),
    )
    photo_urls = [
        f"https://images.unsplash.com/photo-slot-{index}"
        for index in range(4)
    ]
    partial_html = (
        '<!DOCTYPE html><html><body>'
        f'<img src="{photo_urls[0]}"></body></html>'
    )
    repaired_html = (
        '<!DOCTYPE html><html><body>'
        + "".join(f'<img src="{url}">' for url in photo_urls)
        + '<a href="https://unsplash.com/@example">'
        + 'Photo by Example on Unsplash</a>'
        + '</body></html>'
    )
    responses = [
        _openai_response("", "", "tool_calls", tool_calls=[legacy_tool_call]),
        _openai_response(partial_html, "", "stop"),
        _openai_response(repaired_html, "", "stop"),
    ]
    calls: list[dict] = []

    def _factory(*args, **kwargs):
        def _create(**call_kwargs):
            calls.append(call_kwargs)
            return responses[len(calls) - 1]
        return SimpleNamespace(root_client=SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=_create))))

    async def _search(arguments, *, max_requests, progress=None):
        requests = arguments["requests"]
        assert max_requests == 6
        assert [item["slot"] for item in requests[:4]] == [
            "hero-banner", "product-card-1", "product-card-2",
            "product-card-3",
        ]
        assert all(item["query"] != "shopping mall banner" for item in requests)
        photos = [
            {
                "id": f"slot-{index}",
                "slot": request["slot"],
                "query": request["query"],
                "description": request["slot"],
                "urls": {"small": photo_urls[index]},
                "width": 800,
                "height": 800,
                "photographer": "Example",
                "photographer_url": "https://unsplash.com/@example",
                "unsplash_url": "https://unsplash.com/",
                "download_location": f"https://api.unsplash.com/photos/slot-{index}/download",
            }
            for index, request in enumerate(requests[:4])
        ]
        if progress is not None:
            for index, request in enumerate(requests):
                await progress(index + 1, len(requests), request["slot"])
        return photos

    async def _track(photos, html):
        assert len(photos) == 4
        assert all(url in html for url in photo_urls)
        return 4

    monkeypatch.setattr(app_mod, "image_tool_available", lambda: True)
    monkeypatch.setattr(app_mod, "call_unsplash_mcp_batch", _search)
    monkeypatch.setattr(app_mod, "track_used_photos", _track)
    monkeypatch.setattr(app_mod, "chat_model_for", _factory)
    monkeypatch.setattr(app_mod, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(app_mod, "load_model_registry", lambda: [
        ModelConfig(id="tool-model", provider="openai", api_key="sk-test")
    ])

    with TestClient(app_mod.app) as client:
        messages = _parse_stream(client.post(
            "/api/generate",
            json={"prompt": "移动端商城商品推荐页面，包含 Banner 和商品流"},
        ))

    result = _first_result(messages)
    assert len(calls) == 3
    assert calls[0]["tool_choice"] == "required"
    assert calls[1]["tool_choice"] == "none"
    assert "至少使用 4 张不同" in calls[2]["messages"][-1]["content"]
    assert result["image_count"] == 4
    assert result["image_tracked"] == 4
    assert result["image_repaired"] is True
    assert result["image_error"] == ""
    assert result["html"] == repaired_html
    image_progress = [
        event["message"]
        for event in _progress(messages, "0")
        if event["stage"] == "searching_images"
    ]
    assert "正在搜索图片素材 0/4" in image_progress
    assert "正在搜索图片素材 3/4" in image_progress
    assert "正在搜索图片素材 4/4" in image_progress


def test_run_image_batch_cache_deduplicates_parallel_models(monkeypatch) -> None:
    calls: list[tuple[list[dict], int]] = []
    requests = [{
        "slot": "hero-banner",
        "query": "ecommerce banner",
        "orientation": "landscape",
    }]

    async def _search(arguments, *, max_requests, progress=None):
        calls.append((arguments["requests"], max_requests))
        await asyncio.sleep(0)
        if progress is not None:
            await progress(1, 1, "hero-banner")
        return [{"id": "shared-photo", "slot": "hero-banner", "urls": {}}]

    async def _exercise():
        cache = app_mod.RunImageBatchCache()
        return await asyncio.gather(
            cache.search(requests, max_requests=6),
            cache.search(requests, max_requests=6),
            cache.search(requests, max_requests=6),
        )

    monkeypatch.setattr(app_mod, "call_unsplash_mcp_batch", _search)
    results = asyncio.run(_exercise())
    assert len(calls) == 1
    assert len(results) == 3
    assert all(result[0]["id"] == "shared-photo" for result in results)


def test_run_image_tracking_is_deduplicated_across_models(monkeypatch) -> None:
    calls: list[list[str]] = []
    photo = {
        "id": "shared-photo",
        "urls": {"small": "https://images.unsplash.com/photo-shared"},
        "download_location": "https://api.unsplash.com/photos/shared/download",
    }
    html = '<img src="https://images.unsplash.com/photo-shared">'

    async def _track(photos, _html):
        calls.append([item["id"] for item in photos])
        await asyncio.sleep(0)
        return len(photos)

    async def _exercise():
        cache = app_mod.RunImageBatchCache()
        return await asyncio.gather(
            cache.track([photo], html),
            cache.track([photo], html),
            cache.track([photo], html),
        )

    monkeypatch.setattr(app_mod, "track_used_photos", _track)
    results = asyncio.run(_exercise())
    assert calls == [["shared-photo"]]
    assert results.count(1) == 1
    assert results.count(0) == 2


@pytest.mark.parametrize("prompt", [
    "生成5张肖像图",
    "生成五张人像照片",
    "Create 5 portraits",
])
def test_explicit_portrait_count_becomes_hard_slot_floor(prompt) -> None:
    assert app_mod._explicit_photo_count(prompt) == 5
    assert app_mod._minimum_photo_slots(prompt) == 5


def test_five_portraits_get_five_distinct_fallback_slots() -> None:
    requests = app_mod._fallback_photo_requests(
        "生成5张肖像图", "mobile", limit=6,
    )
    assert len(requests) == 5
    assert [request["slot"] for request in requests] == [
        "portrait-1", "portrait-2", "portrait-3", "portrait-4", "portrait-5",
    ]
    assert len({request["query"] for request in requests}) == 5
    assert all(request["orientation"] == "portrait" for request in requests)

    photos = [
        {"slot": request["slot"], "urls": {"small": f"photo-{index}"}}
        for index, request in enumerate(requests)
    ]
    instruction = app_mod._image_repair_instruction(
        photos, '<img src="photo-0"><img src="photo-1">', required=5,
    )
    assert "至少使用 5 张不同" in instruction


def test_product_fallback_preserves_user_semantics_and_photo_opt_out() -> None:
    prompt = "鲜花商城，展示玫瑰、百合、郁金香和向日葵"
    requests = app_mod._fallback_photo_requests(
        prompt, "mobile", limit=4,
    )
    assert [request["slot"] for request in requests] == [
        "hero-banner", "product-card-1", "product-card-2", "product-card-3",
    ]
    assert all("鲜花商城" in request["query"] for request in requests)
    assert not any(
        product in request["query"]
        for request in requests
        for product in ("headphones", "smartwatch", "speaker", "laptop")
    )
    assert app_mod._minimum_photo_slots(
        "商城后台订单管理页，不要图片，只显示表格"
    ) == 0


@pytest.mark.parametrize("prompt", [
    "商城页不要用图片",
    "商城页别用图片",
    "商城页不放照片",
    "Product page: do not include images",
    "Product page: don't use photos",
])
def test_common_photo_opt_out_phrases_override_visual_heuristics(prompt) -> None:
    assert app_mod._minimum_photo_slots(prompt) == 0


def test_protocol_relative_image_is_never_approved() -> None:
    assert app_mod._unapproved_remote_image_urls(
        [], '<img src="//tracker.example/pixel.png">',
    ) == {"//tracker.example/pixel.png"}


def test_chinese_gallery_uses_six_shared_photo_slots() -> None:
    assert app_mod._minimum_photo_slots("生成一个画廊APP") == 6
    requests = app_mod._fallback_photo_requests(
        "生成一个画廊APP", "mobile", limit=6,
    )
    assert len(requests) == 6
    assert len({request["slot"] for request in requests}) == 6
    assert requests[0]["slot"] == "hero-artwork"


def test_image_search_failure_is_degraded_not_success(monkeypatch, tmp_path) -> None:
    from uibench.image_tools import ImageToolError
    from uibench.schemas import ModelConfig

    placeholder_html = (
        '<!DOCTYPE html><html><head></head><body>'
        '<div class="gallery-placeholder">暂无图片</div></body></html>'
    )
    responses = [
        _openai_response("", "", "tool_calls"),
        _openai_response(placeholder_html, "", "stop"),
    ]
    calls: list[dict] = []

    def _factory(*args, **kwargs):
        def _create(**call_kwargs):
            calls.append(call_kwargs)
            return responses[len(calls) - 1]
        return SimpleNamespace(root_client=SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=_create))))

    async def _search(*args, **kwargs):
        raise ImageToolError("403 Forbidden: Rate Limit Exceeded")

    monkeypatch.setattr(app_mod, "image_tool_available", lambda: True)
    monkeypatch.setattr(app_mod, "call_unsplash_mcp_batch", _search)
    monkeypatch.setattr(app_mod, "chat_model_for", _factory)
    monkeypatch.setattr(app_mod, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(app_mod, "load_model_registry", lambda: [
        ModelConfig(id="tool-model", provider="openai", api_key="sk-test")
    ])

    with TestClient(app_mod.app) as client:
        messages = _parse_stream(client.post(
            "/api/generate", json={"prompt": "生成一个画廊APP"}
        ))

    result = _first_result(messages)
    assert len(calls) == 2
    assert result["error"] is None
    assert result["status"] == "degraded"
    assert result["image_required"] == 6
    assert result["image_count"] == 0
    assert result["image_used"] == 0
    assert "Rate Limit Exceeded" in result["image_error"]
    assert "返回 0/6" in result["image_error"]


def test_non_openai_provider_preplans_required_images(monkeypatch, tmp_path) -> None:
    from uibench.schemas import ModelConfig

    image_url = "https://images.unsplash.com/photo-anthropic"
    final_html = (
        '<!DOCTYPE html><html><body>'
        f'<img src="{image_url}">'
        '<a href="https://unsplash.com/@example">'
        'Photo by Example on Unsplash</a></body></html>'
    )
    invoked_messages: list = []

    class FakeProviderChat:
        def invoke(self, messages):
            invoked_messages.extend(messages)
            return SimpleNamespace(
                content=final_html,
                additional_kwargs={},
                response_metadata={},
            )

    searches: list[list[dict]] = []

    async def _search(arguments, *, max_requests, progress=None):
        searches.append(arguments["requests"])
        if progress is not None:
            for index, request in enumerate(arguments["requests"]):
                await progress(index + 1, len(arguments["requests"]), request["slot"])
        return [{
            "id": "anthropic",
            "slot": arguments["requests"][0]["slot"],
            "query": arguments["requests"][0]["query"],
            "urls": {"small": image_url},
            "photographer": "Example",
            "photographer_url": "https://unsplash.com/@example",
            "download_location": "https://api.unsplash.com/photos/anthropic/download",
        }]

    async def _track(photos, html):
        return 1

    monkeypatch.setattr(app_mod, "image_tool_available", lambda: True)
    monkeypatch.setattr(app_mod, "call_unsplash_mcp_batch", _search)
    monkeypatch.setattr(app_mod, "track_used_photos", _track)
    monkeypatch.setattr(app_mod, "chat_model_for", lambda *_: FakeProviderChat())
    monkeypatch.setattr(app_mod, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(app_mod, "load_model_registry", lambda: [
        ModelConfig(id="claude-test", provider="anthropic", api_key="test")
    ])

    with TestClient(app_mod.app) as client:
        result = _first_result(_parse_stream(client.post(
            "/api/generate", json={"prompt": "餐厅菜单，展示一道招牌菜"}
        )))

    assert len(searches) == 1
    assert any("经过批准的图片素材库" in message.content for message in invoked_messages)
    assert result["status"] == "degraded"
    assert result["image_tool_used"] is True
    assert result["image_count"] == 1
    assert result["image_used"] == 1
    assert result["error"] is None


def test_unapproved_remote_image_warns_without_blocking_preview(
    monkeypatch, tmp_path,
) -> None:
    from uibench.schemas import ModelConfig

    unsafe_html = (
        '<!DOCTYPE html><html><head></head><body>'
        '<img src="https://images.unsplash.com/photo-invented">'
        '</body></html>'
    )

    def _factory(*args, **kwargs):
        def _create(**call_kwargs):
            return _openai_response(unsafe_html, "", "stop")
        return SimpleNamespace(root_client=SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=_create))))

    monkeypatch.setattr(app_mod, "chat_model_for", _factory)
    monkeypatch.setattr(app_mod, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(app_mod, "load_model_registry", lambda: [
        ModelConfig(id="unsafe-model", provider="openai", api_key="sk-test")
    ])

    with TestClient(app_mod.app) as client:
        messages = _parse_stream(client.post(
            "/api/generate", json={"prompt": "简单待办清单"}
        ))

    result = _first_result(messages)
    assert result["status"] == "degraded"
    assert "photo-invented" in result["html"]
    assert result["error"] is None
    assert "未经图片工具批准" in result["image_error"]
    assert "已继续预览" in result["image_error"]
    assert result["image_used"] == 0


@pytest.mark.parametrize("unsafe_body", [
    '<img src=https://tracker.example/unquoted.png>',
    '<object data=https://tracker.example/payload.png></object>',
    (
        '<script type="text/babel">'
        'const rows=[{image:"https://tracker.example/dynamic.png"}];'
        'const App=()=> <img src={rows[0].image}/>;'
        '</script>'
    ),
])
def test_unapproved_image_syntaxes_warn_without_blocking_preview(
    monkeypatch, tmp_path, unsafe_body,
) -> None:
    from uibench.schemas import ModelConfig

    unsafe_html = f"<!DOCTYPE html><html><body>{unsafe_body}</body></html>"

    def _factory(*args, **kwargs):
        def _create(**call_kwargs):
            return _openai_response(unsafe_html, "", "stop")
        return SimpleNamespace(root_client=SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=_create))))

    monkeypatch.setattr(app_mod, "chat_model_for", _factory)
    monkeypatch.setattr(app_mod, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(app_mod, "load_model_registry", lambda: [
        ModelConfig(id="unsafe-model", provider="openai", api_key="sk-test")
    ])

    with TestClient(app_mod.app) as client:
        result = _first_result(_parse_stream(client.post(
            "/api/generate", json={"prompt": "简单待办清单"}
        )))

    assert result["status"] == "degraded"
    assert unsafe_body in result["html"]
    assert result["error"] is None
    assert "未经图片工具批准" in result["image_error"]
    assert "已继续预览" in result["image_error"]


def test_used_unsplash_image_without_attribution_is_allowed(
    monkeypatch, tmp_path,
) -> None:
    from uibench.schemas import ModelConfig

    image_url = "https://images.unsplash.com/photo-no-credit"
    tool_call = SimpleNamespace(
        id="call_image",
        function=SimpleNamespace(
            name="search_photos",
            arguments=json.dumps({
                "requests": [{
                    "slot": "hero",
                    "query": "profile portrait",
                }],
            }),
        ),
    )
    responses = [
        _openai_response("", "", "tool_calls", tool_calls=[tool_call]),
        _openai_response(
            f'<!DOCTYPE html><html><body><img src="{image_url}"></body></html>',
            "",
            "stop",
        ),
    ]
    calls = 0

    def _factory(*args, **kwargs):
        def _create(**call_kwargs):
            nonlocal calls
            response = responses[calls]
            calls += 1
            return response
        return SimpleNamespace(root_client=SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=_create))))

    async def _search(arguments, *, max_requests, progress=None):
        return [{
            "id": "no-credit",
            "slot": "hero",
            "query": "profile portrait",
            "urls": {"small": image_url},
            "photographer": "",
            "photographer_url": "",
            "download_location": "https://api.unsplash.com/photos/no-credit/download",
        }]

    monkeypatch.setattr(app_mod, "image_tool_available", lambda: True)
    monkeypatch.setattr(app_mod, "call_unsplash_mcp_batch", _search)
    monkeypatch.setattr(app_mod, "chat_model_for", _factory)
    monkeypatch.setattr(app_mod, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(app_mod, "load_model_registry", lambda: [
        ModelConfig(id="tool-model", provider="openai", api_key="sk-test")
    ])

    with TestClient(app_mod.app) as client:
        result = _first_result(_parse_stream(client.post(
            "/api/generate", json={"prompt": "用户设置页面"}
        )))

    assert result["status"] == "success"
    assert result["html"] == (
        f'<!DOCTYPE html><html><body><img src="{image_url}"></body></html>'
    )
    assert result["error"] is None


def test_tool_model_invented_image_url_warns_without_blocking_preview(
    monkeypatch, tmp_path,
) -> None:
    """A DeepSeek-style tool call must not make an invented URL fatal."""
    from uibench.schemas import ModelConfig

    approved_url = "https://images.unsplash.com/photo-approved"
    invented_url = "https://images.unsplash.com/photo-invented-by-model"
    tool_call = SimpleNamespace(
        id="call_image",
        function=SimpleNamespace(
            name="search_photos",
            arguments=json.dumps({
                "requests": [{
                    "slot": "profile-avatar",
                    "query": "user profile portrait avatar",
                }],
            }),
        ),
    )
    final_html = (
        '<!DOCTYPE html><html><body>'
        f'<img src="{invented_url}"></body></html>'
    )
    responses = [
        _openai_response("", "", "tool_calls", tool_calls=[tool_call]),
        _openai_response(final_html, "", "stop"),
    ]
    calls = 0

    def _factory(*args, **kwargs):
        def _create(**call_kwargs):
            nonlocal calls
            response = responses[calls]
            calls += 1
            return response
        return SimpleNamespace(root_client=SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=_create))))

    async def _search(arguments, *, max_requests, progress=None):
        return [{
            "id": "approved",
            "slot": "profile-avatar",
            "query": "user profile portrait avatar",
            "urls": {"small": approved_url},
            "photographer": "Example",
            "photographer_url": "https://unsplash.com/@example",
            "download_location": "https://api.unsplash.com/photos/approved/download",
        }]

    monkeypatch.setattr(app_mod, "image_tool_available", lambda: True)
    monkeypatch.setattr(app_mod, "call_unsplash_mcp_batch", _search)
    monkeypatch.setattr(app_mod, "chat_model_for", _factory)
    monkeypatch.setattr(app_mod, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(app_mod, "load_model_registry", lambda: [
        ModelConfig(id="deepseek-test", provider="openai", api_key="sk-test")
    ])

    with TestClient(app_mod.app) as client:
        result = _first_result(_parse_stream(client.post(
            "/api/generate", json={"prompt": "帮我生成一个用户设置页面"}
        )))

    assert result["status"] == "degraded"
    assert result["html"] == final_html
    assert result["error"] is None
    assert result["image_tool_used"] is True
    assert result["image_count"] == 1
    assert result["image_used"] == 0
    assert "未经图片工具批准" in result["image_error"]
    assert "已继续预览" in result["image_error"]
    assert "图片使用不足" in result["image_error"]


def test_image_tool_can_be_declined(monkeypatch, tmp_path) -> None:
    """The model may generate HTML directly when photography is unnecessary."""
    from uibench.schemas import ModelConfig

    calls: list[dict] = []

    def _factory(*args, **kwargs):
        def _create(**call_kwargs):
            calls.append(call_kwargs)
            return _openai_response(CANNED_HTML_WITH_REASON, "", "stop")
        return SimpleNamespace(root_client=SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=_create))))

    monkeypatch.setattr(app_mod, "image_tool_available", lambda: True)
    monkeypatch.setattr(app_mod, "chat_model_for", _factory)
    monkeypatch.setattr(app_mod, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(app_mod, "load_model_registry", lambda: [
        ModelConfig(id="tool-model", provider="openai", api_key="sk-test")
    ])
    with TestClient(app_mod.app) as client:
        messages = _parse_stream(client.post(
            "/api/generate", json={"prompt": "简单待办清单"}
        ))

    result = _first_result(messages)
    assert len(calls) == 1
    assert calls[0]["tool_choice"] == "auto"
    assert result["image_tool_used"] is False
    assert result["image_count"] == 0
