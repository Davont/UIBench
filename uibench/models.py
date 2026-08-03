"""LLM model registry and chat-model factory.

Builds LangChain chat models for the four supported providers. Each provider
is imported lazily, so a user without an Anthropic key can still run OpenAI
comparisons without the anthropic package ever being touched.
"""
from __future__ import annotations

from typing import Any

from config import settings
from uibench.schemas import ModelConfig

_PROVIDER_PACKAGES: dict[str, str] = {
    "openai": "langchain_openai",
    "anthropic": "langchain_anthropic",
    "google": "langchain_google_genai",
    "deepseek": "langchain_deepseek",
}


class ModelError(RuntimeError):
    """Raised when a model cannot be constructed (missing key / package)."""


def load_model_registry(path: Any | None = None) -> list[ModelConfig]:
    """Load enabled models from the YAML registry.

    A top-level ``defaults:`` mapping (optional) is merged into every model
    entry; per-model fields take precedence. This lets a set of models that
    share an endpoint (e.g. an OpenAI-compatible gateway) declare the
    ``provider`` / ``base_url`` / ``api_key_env`` once.
    """
    import yaml

    file_path = str(path or settings.models_file)
    with open(file_path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}

    defaults = data.get("defaults") or {}
    raw_models = data.get("models", [])
    models = [ModelConfig(**{**defaults, **m}) for m in raw_models]
    return [m for m in models if m.enabled]


def _resolve_credentials(
    model_cfg: ModelConfig,
) -> tuple[str | None, str | None]:
    """Resolve per-model (api_key, base_url).

    Key resolution order:
      1. ``model_cfg.api_key`` (literal, not recommended)
      2. ``model_cfg.api_key_env`` -> value of that env var (errors if unset)
      3. ``None`` -> fall back to the provider-level key in ``.env``

    URL resolution:
      1. ``model_cfg.base_url`` (per-model endpoint)
      2. ``None`` -> fall back to the provider-level URL in ``.env``
    """
    import os

    api_key = model_cfg.api_key
    if not api_key and model_cfg.api_key_env:
        api_key = os.environ.get(model_cfg.api_key_env)
        if not api_key:
            raise ModelError(
                f"api_key_env {model_cfg.api_key_env!r} is not set in the environment"
            )
    base_url = model_cfg.base_url
    return api_key, base_url


def chat_model_for(model_cfg: ModelConfig):
    """Build a chat model from a registry entry, honoring per-model URL/key."""
    api_key, base_url = _resolve_credentials(model_cfg)
    return build_chat_model(
        model_cfg.id,
        model_cfg.provider,
        api_key=api_key,
        base_url=base_url,
    )


def build_chat_model(
    model_id: str,
    provider: str,
    *,
    temperature: float | None = None,
    max_tokens: int | None = None,
    timeout: int | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
):
    """Construct a LangChain chat model for the given provider + model id.

    ``api_key`` / ``base_url`` override the provider-level values when given.
    ``max_tokens`` / ``timeout`` are only forwarded to the SDK when configured
    (either via the call or via ``config/models.yaml``); when both are ``None``
    no output-token limit and no request timeout are applied.
    """
    pkg = _PROVIDER_PACKAGES.get(provider)
    if pkg is None:
        raise ModelError(f"Unknown provider: {provider!r}")
    temperature = settings.temperature if temperature is None else temperature
    if max_tokens is None:
        max_tokens = settings.max_tokens
    if timeout is None:
        timeout = settings.request_timeout

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        key = api_key or settings.openai_api_key
        url = base_url or settings.openai_base_url
        if not key:
            raise ModelError("OPENAI_API_KEY is not set")
        kwargs: dict = dict(model=model_id, temperature=temperature,
                             api_key=key, base_url=url)
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        if timeout is not None:
            kwargs["timeout"] = timeout
        return ChatOpenAI(**kwargs)

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        key = api_key or settings.anthropic_api_key
        if not key:
            raise ModelError("ANTHROPIC_API_KEY is not set")
        kwargs = dict(model=model_id, temperature=temperature, api_key=key)
        if base_url:
            kwargs["base_url"] = base_url
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        if timeout is not None:
            kwargs["timeout"] = timeout
        return ChatAnthropic(**kwargs)

    if provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI

        key = api_key or settings.google_api_key
        if not key:
            raise ModelError("GOOGLE_API_KEY is not set")
        kwargs = dict(model=model_id, temperature=temperature, api_key=key)
        if base_url:
            kwargs["base_url"] = base_url
        if max_tokens is not None:
            kwargs["max_output_tokens"] = max_tokens
        if timeout is not None:
            kwargs["timeout"] = timeout
        return ChatGoogleGenerativeAI(**kwargs)

    if provider == "deepseek":
        from langchain_deepseek import ChatDeepSeek

        key = api_key or settings.deepseek_api_key
        url = base_url or settings.deepseek_base_url
        if not key:
            raise ModelError("DEEPSEEK_API_KEY is not set")
        kwargs = dict(model=model_id, temperature=temperature,
                      api_key=key, base_url=url)
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        if timeout is not None:
            kwargs["timeout"] = timeout
        return ChatDeepSeek(**kwargs)

    raise ModelError(f"Provider {provider!r} is not implemented")
