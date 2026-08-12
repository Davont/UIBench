"""Tests for the model registry: defaults merging + credential resolution."""
import pytest

from uibench.models import _resolve_credentials, load_model_registry
from uibench.schemas import ModelConfig


def test_defaults_merged_into_models(tmp_path):
    registry = tmp_path / "models.yaml"
    registry.write_text(
        """
defaults:
  provider: openai
  base_url: https://example.test/v1
  api_key_env: TEST_PROVIDER_API_KEY
models:
  - id: model-a
    name: Model A
  - id: model-b
    name: Model B disabled
    enabled: false
  - id: model-c
    name: Model C
    reasoning_effort: low
""".strip(),
        encoding="utf-8",
    )
    models = load_model_registry(registry)
    assert len(models) == 2
    by_name = {m.name: m for m in models}

    model_a = by_name["Model A"]
    assert model_a.provider == "openai"
    assert model_a.base_url == "https://example.test/v1"
    assert model_a.api_key_env == "TEST_PROVIDER_API_KEY"
    assert model_a.api_key is None
    assert model_a.reasoning_effort is None
    assert by_name["Model C"].reasoning_effort == "low"


def test_run_options_loaded_from_yaml(monkeypatch, tmp_path):
    import importlib

    settings_mod = importlib.import_module("config.settings")

    registry = tmp_path / "models.yaml"
    registry.write_text(
        """
options:
  temperature: 0.25
  max_tokens: 8192
  request_timeout: 180
  recover_incomplete_html: false
  recovery_context_chars: 1234
  image_tools_enabled: false
  image_tool_timeout: 12
  image_tool_max_assets: 7
""".strip(),
        encoding="utf-8",
    )
    monkeypatch.setattr(settings_mod, "MODELS_FILE", registry)
    configured = settings_mod.Settings()
    assert configured.temperature == 0.25
    assert configured.max_tokens == 8192
    assert configured.request_timeout == 180
    assert configured.recover_incomplete_html is False
    assert configured.recovery_context_chars == 1234
    assert configured.image_tools_enabled is False
    assert configured.image_tool_timeout == 12
    assert configured.image_tool_max_assets == 7


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
