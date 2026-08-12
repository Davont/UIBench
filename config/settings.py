"""Runtime settings loaded from the single config file (config/models.yaml).

Everything the user needs to configure lives in one YAML file: run options
(temperature, max_tokens, timeout) plus the model registry (endpoint, key,
models). This module exposes a small object with the run options and the path
to that file.
"""
from __future__ import annotations

from pathlib import Path

import yaml
from dotenv import load_dotenv

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
MODELS_FILE: Path = PROJECT_ROOT / "config" / "models.yaml"
load_dotenv(PROJECT_ROOT / ".env")

_DEFAULTS = {"temperature": 0.0}


class Settings:
    """Thin accessor over the single config file."""

    def __init__(self) -> None:
        self.models_file: Path = MODELS_FILE
        data = self._load()
        options = data.get("options") or {}
        self.temperature: float = float(options.get("temperature", _DEFAULTS["temperature"]))
        # None means "not configured" -> the chat model won't pass it through,
        # i.e. no output-token limit and no request timeout.
        self.max_tokens: int | None = options.get("max_tokens")
        self.request_timeout: int | None = options.get("request_timeout")
        self.recover_incomplete_html: bool = bool(
            options.get("recover_incomplete_html", True)
        )
        self.recovery_context_chars: int = int(
            options.get("recovery_context_chars", 6000)
        )
        self.image_tools_enabled: bool = bool(
            options.get("image_tools_enabled", True)
        )
        self.image_tool_timeout: float = float(
            options.get("image_tool_timeout", 90)
        )
        self.image_tool_max_assets: int = max(
            1, min(8, int(options.get("image_tool_max_assets", 6)))
        )
        if self.max_tokens is not None:
            self.max_tokens = int(self.max_tokens)
        if self.request_timeout is not None:
            self.request_timeout = int(self.request_timeout)

    @staticmethod
    def _load() -> dict:
        if not MODELS_FILE.exists():
            return {}
        with open(MODELS_FILE, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}


settings = Settings()
