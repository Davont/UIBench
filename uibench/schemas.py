"""Pydantic schemas: model registry entry + generation result."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Provider = Literal["openai", "anthropic", "google", "deepseek"]
Mode = Literal["mobile", "pc"]


class ModelConfig(BaseModel):
    """A registered LLM that participates in the side-by-side run.

    Per-model URL/key overrides (optional):

    - ``base_url``: an explicit endpoint for this model (e.g. an OpenAI-
      compatible proxy). Falls back to the provider-level URL in ``.env``.
    - ``api_key_env``: name of the environment variable that holds this
      model's key (recommended - keeps secrets out of the YAML). If unset
      in the environment the build fails explicitly.
    - ``api_key``: a literal key (NOT recommended - will be committed).
    """

    id: str
    provider: Provider
    name: str = ""
    enabled: bool = True
    base_url: str | None = None
    api_key_env: str | None = None
    api_key: str | None = None


class GenerationResult(BaseModel):
    """One model's outcome for a single user prompt."""

    key: str = ""
    model_id: str
    name: str
    provider: Provider
    mode: Mode = "mobile"
    html: str = ""
    reasoning: str = ""
    log_url: str = ""
    elapsed_seconds: float = 0.0
    error: str | None = None


class GenerateRequest(BaseModel):
    """The user's one-sentence UI requirement."""

    prompt: str = Field(min_length=1)
    mode: Mode = "mobile"
