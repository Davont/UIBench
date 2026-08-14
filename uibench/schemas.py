"""Pydantic schemas: model registry entry + generation result."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from uibench.arkui.snapshot import BrowserSnapshot

Provider = Literal["openai", "anthropic", "google", "deepseek"]
Mode = Literal["mobile", "pc"]
ResultStatus = Literal["success", "degraded", "failed"]
ArkUiExportMode = Literal["annotated", "generic"]
ColorMode = Literal["light", "dark"]
TokenTheme = Literal["harmonyos", "spotify", "netflix", "notion"]
# "" means "use options.image_source from config/models.yaml".
ImageSource = Literal["", "local", "unsplash"]


class ModelConfig(BaseModel):
    """A registered LLM that participates in the side-by-side run.

    Per-model URL/key overrides (optional):

    - ``base_url``: an explicit endpoint for this model (e.g. an OpenAI-
      compatible proxy). Falls back to the provider-level URL in ``.env``.
    - ``api_key_env``: name of the environment variable that holds this
      model's key (recommended - keeps secrets out of the YAML). If unset
      in the environment the build fails explicitly.
    - ``api_key``: a literal key (NOT recommended - will be committed).
    - ``reasoning_effort``: DeepSeek thinking-mode strength. One of
      ``low`` / ``high`` / ``xhigh`` / ``max`` (enables thinking), or
      ``none`` (disables thinking). When unset, the API default applies
      (DeepSeek: thinking on, effort high). Only used for the openai-
      compatible direct call path.
    """

    id: str
    provider: Provider
    name: str = ""
    enabled: bool = True
    base_url: str | None = None
    api_key_env: str | None = None
    api_key: str | None = None
    reasoning_effort: str | None = None


class GenerationResult(BaseModel):
    """One model's outcome for a single user prompt."""

    key: str = ""
    model_id: str
    name: str
    provider: Provider
    mode: Mode = "mobile"
    html: str = ""
    reasoning: str = ""
    html_source: str = ""
    finish_reason: str = ""
    recovery_finish_reason: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    reasoning_tokens: int = 0
    recovered: bool = False
    status: ResultStatus = "success"
    image_tool_used: bool = False
    image_required: int = 0
    image_count: int = 0
    image_used: int = 0
    image_queries: list[str] = Field(default_factory=list)
    image_tracked: int = 0
    image_repaired: bool = False
    image_error: str = ""
    image_source: str = ""
    # dt-* classes the model invented: they match no CSS rule, so that styling
    # is silently dropped from the rendered page.
    unknown_token_classes: list[str] = Field(default_factory=list)
    arkui_export_enabled: bool = False
    arkui_manifest: dict[str, object] = Field(default_factory=dict)
    log_url: str = ""
    elapsed_seconds: float = 0.0
    error: str | None = None


class GenerateRequest(BaseModel):
    """The user's one-sentence UI requirement."""

    prompt: str = Field(min_length=1)
    mode: Mode = "mobile"
    arkui_export_enabled: bool = False
    # Per-run override of the configured photo source (offline gallery vs
    # live Unsplash search); empty keeps the config default.
    image_source: ImageSource = ""


class ArkUiPrepareRequest(BaseModel):
    """HTML that must be repaired before its browser snapshot is captured."""

    html: str = Field(min_length=1, max_length=2_000_000)


class HtmlPackageRequest(BaseModel):
    """One generated page prepared for a double-clickable HTML ZIP."""

    html: str = Field(min_length=1, max_length=2_000_000)
    mode: Mode = "mobile"
    theme: ColorMode = "light"
    token_theme: TokenTheme = "harmonyos"


class ArkUiExportRequest(BaseModel):
    """One bounded HTML-to-ArkUI export request."""

    html: str = Field(min_length=1, max_length=2_000_000)
    page_name: str = Field(default="GeneratedPage", min_length=1, max_length=100)
    page_description: str | None = Field(default=None, max_length=500)
    mode: ArkUiExportMode = "annotated"
    viewport_width: int = Field(default=390, ge=240, le=3840)
    viewport_height: int = Field(default=844, ge=240, le=3840)
    snapshot: BrowserSnapshot | None = None
