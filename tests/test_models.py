"""Tests for the model registry: defaults merging + credential resolution."""
import pytest

from uibench.models import _resolve_credentials, load_model_registry
from uibench.schemas import ModelConfig


def test_defaults_merged_into_models():
    models = load_model_registry()
    assert len(models) == 9
    by_name = {m.name: m for m in models}

    # DashScope models inherit the default endpoint + key
    ds = by_name["GLM 5.2"]
    assert ds.provider == "openai"
    assert ds.base_url == "https://dashscope.aliyuncs.com/compatible-mode/v1"
    assert ds.api_key == "sk-2ab9f98663e7471aaaef953d21f5b1e4"

    # DeepSeek-official: one model expanded into 4 effort cards
    flash_cards = [m for m in models if m.id == "deepseek-v4-flash"]
    assert len(flash_cards) == 4
    assert {m.reasoning_effort for m in flash_cards} == {"none", "low", "high", "max"}
    none_card = by_name["DeepSeek v4 Flash · 无思考"]
    assert none_card.base_url == "https://api.deepseek.com/v1"
    assert none_card.api_key == "sk-a1d2a065cc2e431fbbb6c914f986018b"
    assert none_card.reasoning_effort == "none"


def test_run_options_loaded_from_yaml():
    from config import settings
    assert settings.temperature == 0.0
    # max_tokens / request_timeout are not configured -> no limit applied
    assert settings.max_tokens is None
    assert settings.request_timeout is None


def test_resolve_credentials_from_env(monkeypatch):
    monkeypatch.setenv("DASHSCOPE_API_KEY", "sk-test-123")
    m = ModelConfig(id="qwen3.7-plus", provider="openai", base_url="https://x/v1",
                   api_key_env="DASHSCOPE_API_KEY")
    key, url = _resolve_credentials(m)
    assert key == "sk-test-123"
    assert url == "https://x/v1"


def test_resolve_credentials_missing_env_raises(monkeypatch):
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
    m = ModelConfig(id="x", provider="openai", api_key_env="DASHSCOPE_API_KEY")
    with pytest.raises(Exception):
        _resolve_credentials(m)


def test_resolve_credentials_literal_key_wins():
    m = ModelConfig(id="x", provider="openai", api_key="sk-literal",
                   api_key_env="DASHSCOPE_API_KEY")
    key, _ = _resolve_credentials(m)
    assert key == "sk-literal"


def test_resolve_credentials_no_override_returns_none():
    # no api_key / api_key_env -> override is None (provider-level fallback)
    m = ModelConfig(id="x", provider="openai")
    key, url = _resolve_credentials(m)
    assert key is None
    assert url is None
