"""End-to-end API tests using fake chat models (no API keys needed)."""
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


def test_index_page(client) -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    assert "UIBench" in resp.text


def test_generate_stream(client) -> None:
    resp = client.post("/api/generate", json={"prompt": "一个登录页"})
    assert resp.status_code == 200
    messages = _parse_stream(resp)
    types = [m["type"] for m in messages]
    assert types[0] == "start"
    assert types[-1] == "done"
    results = [m for m in messages if m["type"] == "result"]
    assert len(results) >= 1
    first = results[0]["result"]
    assert "<!DOCTYPE html>" in first["html"]
    assert first["elapsed_seconds"] >= 0
    assert first["error"] is None
    assert len(messages[0]["models"]) == len(results)
    assert messages[0]["run_id"]


def test_openai_role_mapping(reasoning_client) -> None:
    """langchain 'human' must be sent to the OpenAI API as 'user'."""
    resp = reasoning_client.post("/api/generate", json={"prompt": "电商首页"})
    assert resp.status_code == 200
    assert _REASONING_CALLS
    roles = [m["role"] for m in _REASONING_CALLS[0]["messages"]]
    assert "human" not in roles
    assert "user" in roles
    assert "system" in roles


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
    first = _parse_stream(resp)[1]["result"]
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
    first = _parse_stream(resp)[1]["result"]
    assert first["mode"] == "pc"


def test_reasoning_captured_and_archived(reasoning_client, tmp_path) -> None:
    resp = reasoning_client.post("/api/generate", json={"prompt": "电商首页"})
    assert resp.status_code == 200
    messages = _parse_stream(resp)
    run_id = messages[0]["run_id"]
    first = messages[1]["result"]
    assert first["reasoning"] == CANNED_REASONING
    assert first["log_url"] == f"/api/log/{run_id}/{first['key']}"

    files = list((tmp_path / "logs" / run_id).glob("*.md"))
    assert files
    on_disk = files[0].read_text(encoding="utf-8")
    assert CANNED_REASONING in on_disk
    assert "## 思考过程" in on_disk

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
