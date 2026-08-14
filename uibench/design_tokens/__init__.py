"""Multi-system Design Token support for generated mobile previews.

The feature is intentionally isolated in this package so the upstream UIBench
layout, model registry, and logging code can continue to track the fork with
minimal changes. Tokens are stored as data and compiled into CSS variables plus
a system-owned Tailwind theme preset. Legacy ``dt-*`` utilities remain as a
compatibility layer, but new model generations only need Tailwind's grammar.
"""
from __future__ import annotations

import json
import logging
import re
from functools import lru_cache
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

TOKEN_FILE = Path(__file__).with_name("tokens.json")
THEME_NAMES = ("light", "dark")
TOKEN_THEME_NAMES = ("harmonyos", "spotify", "netflix", "notion")
DEFAULT_TOKEN_THEME = "harmonyos"
LOGGER = logging.getLogger(__name__)

DESIGN_TOKEN_CLASSES = frozenset({
    "dt-accent",
    "dt-bg-accent",
    "dt-bg-accent-container",
    "dt-bg-accent-container-subtle",
    "dt-bg-accent-hover",
    "dt-bg-canvas",
    "dt-bg-canvas-translucent",
    "dt-bg-component-secondary",
    "dt-bg-component-subtle",
    "dt-bg-danger",
    "dt-bg-disabled",
    "dt-bg-layer-secondary",
    "dt-bg-layer-tertiary",
    "dt-bg-primary",
    "dt-bg-primary-container",
    "dt-bg-primary-container-subtle",
    "dt-bg-primary-hover",
    "dt-bg-scrim",
    "dt-bg-success",
    "dt-bg-surface",
    "dt-bg-surface-raised",
    "dt-bg-surface-subtle",
    "dt-bg-warning",
    "dt-border",
    "dt-border-divider",
    "dt-border-outline",
    "dt-divide",
    "dt-focus",
    "dt-font",
    "dt-form-accent",
    "dt-gap-compact",
    "dt-gap-item",
    "dt-gap-section",
    "dt-interaction-hover",
    "dt-interaction-pressed",
    "dt-interaction-selected",
    "dt-mb-section",
    "dt-mt-compact",
    "dt-mt-section",
    "dt-mx-page",
    "dt-p-card",
    "dt-pb-page",
    "dt-p-page",
    "dt-placeholder-secondary",
    "dt-pt-section",
    "dt-px-page",
    "dt-py-card",
    "dt-py-page",
    "dt-rounded-card",
    "dt-rounded-control",
    "dt-rounded-pill",
    "dt-shadow-surface",
    "dt-text-accent",
    "dt-text-body",
    "dt-text-caption",
    "dt-text-danger",
    "dt-text-disabled",
    "dt-text-fourth",
    "dt-text-on-accent",
    "dt-text-on-danger",
    "dt-text-on-primary",
    "dt-text-on-success",
    "dt-text-on-warning",
    "dt-text-primary",
    "dt-text-secondary",
    "dt-text-tertiary",
    "dt-text-success",
    "dt-text-title",
    "dt-text-warning",
})

TOKEN_CLASS_ALIASES = {
    "dt-rounded-full": "dt-rounded-pill",
    "dt-bg-canvas/90": "dt-bg-canvas-translucent",
    "dt-bg-primary/10": "dt-bg-primary-container-subtle",
    "dt-bg-accent/15": "dt-bg-accent-container-subtle",
    "hover:dt-bg-surface": "dt-interaction-hover",
    "hover:dt-bg-surface-subtle": "dt-interaction-hover",
    "hover:dt-bg-surface-raised": "dt-interaction-hover",
    "hover:dt-bg-primary-hover": "dt-interaction-hover",
    "active:dt-bg-surface": "dt-interaction-pressed",
    "active:dt-bg-surface-subtle": "dt-interaction-pressed",
    "active:dt-bg-surface-raised": "dt-interaction-pressed",
    "active:dt-bg-primary-hover": "dt-interaction-pressed",
    "focus:dt-focus": "dt-focus",
    "placeholder:dt-placeholder-secondary": "dt-placeholder-secondary",
    "dt-mt-gap-section": "dt-mt-section",
    "dt-pt-gap-section": "dt-pt-section",
    "dt-py-3": "dt-py-card",
    # GLM-style cross-namespace inventions from the legacy prompt. These map
    # to real Tailwind preset utilities instead of remaining inert CSS names.
    "dt-gap-card": "gap-ui-card",
    "dt-px-card": "px-ui-card",
    "dt-px-compact": "px-ui-compact",
    "dt-py-compact": "py-ui-compact",
    "dt-ml-9": "ml-9",
}

# State-prefixed Design Token names are not Tailwind utilities. Native ArkUI
# controls already receive their checked visuals from the component stylesheet,
# so retaining these inert spellings only creates a false degradation warning.
_DROPPED_TOKEN_CLASSES = frozenset({
    "checked:dt-bg-primary",
    "peer-checked:dt-bg-primary",
})

TAILWIND_TOKEN_COLOR_ROLES = {
    "ui-canvas": "canvas",
    "ui-canvas-translucent": "canvas-translucent",
    "ui-layer-secondary": "layer-secondary",
    "ui-layer-tertiary": "layer-tertiary",
    "ui-surface": "surface",
    "ui-surface-raised": "surface-raised",
    "ui-component-subtle": "component-subtle",
    "ui-component-secondary": "component-secondary",
    "ui-primary": "primary",
    "ui-primary-hover": "primary-hover",
    "ui-primary-container": "primary-container",
    "ui-primary-container-subtle": "primary-container-subtle",
    "ui-accent": "accent",
    "ui-accent-hover": "accent-hover",
    "ui-accent-container": "accent-container",
    "ui-accent-container-subtle": "accent-container-subtle",
    "ui-fg": "text-primary",
    "ui-fg-secondary": "text-secondary",
    "ui-fg-tertiary": "text-tertiary",
    "ui-fg-fourth": "text-fourth",
    "ui-fg-disabled": "disabled-text",
    "ui-on-primary": "on-primary",
    "ui-on-accent": "on-accent",
    "ui-border": "border",
    "ui-divider": "divider",
    "ui-focus": "focus",
    "ui-success": "success",
    "ui-success-container": "success-container",
    "ui-on-success": "on-success-container",
    "ui-warning": "warning",
    "ui-warning-container": "warning-container",
    "ui-on-warning": "on-warning-container",
    "ui-danger": "danger",
    "ui-danger-container": "danger-container",
    "ui-on-danger": "on-danger-container",
    "ui-disabled-surface": "disabled-surface",
    "ui-scrim": "scrim",
}
TAILWIND_TOKEN_SPACING_ROLES = {
    "ui-page": "page",
    "ui-section": "section",
    "ui-card": "card",
    "ui-item": "item",
    "ui-compact": "compact",
}
TAILWIND_TOKEN_RADIUS_ROLES = {
    "ui-card": "card",
    "ui-control": "control",
    "ui-pill": "pill",
}
TAILWIND_TOKEN_FONT_SIZE_ROLES = {
    "ui-title": "title",
    "ui-body": "body",
    "ui-caption": "caption",
}
TAILWIND_TOKEN_BORDER_WIDTH_ROLES = {
    "ui-hairline": "0.5px",
}
TAILWIND_TOKEN_PRESET_MARKER = "data-uibench-tailwind-theme"


@lru_cache(maxsize=1)
def tailwind_token_preset() -> dict[str, Any]:
    """Return the fixed Tailwind extension backed by token CSS variables."""
    colors = {
        name: f"var(--dt-color-{token})"
        for name, token in TAILWIND_TOKEN_COLOR_ROLES.items()
    }
    spacing = {
        name: f"var(--dt-space-{token})"
        for name, token in TAILWIND_TOKEN_SPACING_ROLES.items()
    }
    radius = {
        name: f"var(--dt-radius-{token})"
        for name, token in TAILWIND_TOKEN_RADIUS_ROLES.items()
    }
    font_size = {
        "ui-title": [
            "var(--dt-font-size-title)",
            {
                "lineHeight": "var(--dt-font-line-title)",
                "fontWeight": "var(--dt-font-weight-title)",
            },
        ],
        "ui-body": [
            "var(--dt-font-size-body)",
            {"lineHeight": "var(--dt-font-line-body)"},
        ],
        "ui-caption": "var(--dt-font-size-caption)",
    }
    return {
        "theme": {
            "extend": {
                "colors": colors,
                "spacing": spacing,
                "borderRadius": radius,
                "fontFamily": {"ui": "var(--dt-font-family)"},
                "fontSize": font_size,
                "borderWidth": TAILWIND_TOKEN_BORDER_WIDTH_ROLES,
                "boxShadow": {"ui-surface": "var(--dt-elevation-surface)"},
            },
        },
    }


def render_tailwind_token_config_script() -> str:
    """Render the system-owned Tailwind config installed after the CDN."""
    config = json.dumps(
        tailwind_token_preset(),
        ensure_ascii=False,
        separators=(",", ":"),
    ).replace("</", "<\\/")
    return (
        f"<script {TAILWIND_TOKEN_PRESET_MARKER}>"
        "window.tailwind=window.tailwind||{};"
        f"window.tailwind.config={config};"
        "</script>"
    )


class DesignTokenError(ValueError):
    """Raised when the checked-in token contract is incomplete or malformed."""


def _leaf_paths(value: dict[str, Any], prefix: tuple[str, ...] = ()) -> set[tuple[str, ...]]:
    paths: set[tuple[str, ...]] = set()
    for key, child in value.items():
        path = (*prefix, key)
        if isinstance(child, dict):
            paths.update(_leaf_paths(child, path))
        else:
            paths.add(path)
    return paths


def _flatten(value: dict[str, Any], prefix: tuple[str, ...] = ()) -> dict[str, str]:
    flattened: dict[str, str] = {}
    for key, child in value.items():
        path = (*prefix, key)
        if isinstance(child, dict):
            flattened.update(_flatten(child, path))
            continue
        if not isinstance(child, (str, int, float)):
            joined = ".".join(path)
            raise DesignTokenError(f"Token {joined!r} must be a CSS scalar value")
        flattened["-".join(path)] = str(child)
    return flattened


def validate_tokens(tokens: dict[str, Any]) -> None:
    """Validate design-system parity and the versioned token envelope."""
    if tokens.get("schemaVersion") != 6:
        raise DesignTokenError("schemaVersion must be 6")
    if tokens.get("defaultMode") not in THEME_NAMES:
        raise DesignTokenError("defaultMode must be light or dark")

    themes = tokens.get("themes")
    if not isinstance(themes, dict) or not themes:
        raise DesignTokenError("themes must be a non-empty object")
    if set(themes) != set(TOKEN_THEME_NAMES):
        raise DesignTokenError(
            f"themes must be exactly {list(TOKEN_THEME_NAMES)!r}"
        )
    if tokens.get("defaultTheme") not in themes:
        raise DesignTokenError("defaultTheme must name a configured theme")

    expected_shared_paths: set[tuple[str, ...]] | None = None
    expected_mode_paths: set[tuple[str, ...]] | None = None
    for theme_name, theme in themes.items():
        if not re.fullmatch(r"[a-z0-9-]+", theme_name):
            raise DesignTokenError(f"invalid CSS-safe theme name {theme_name!r}")
        if not isinstance(theme, dict) or not theme:
            raise DesignTokenError(f"theme {theme_name!r} must be a non-empty object")
        if not isinstance(theme.get("label"), str) or not theme["label"].strip():
            raise DesignTokenError(f"theme {theme_name!r} must have a label")

        shared = theme.get("shared")
        modes = theme.get("modes")
        if not isinstance(shared, dict) or not shared:
            raise DesignTokenError(f"theme {theme_name!r} shared tokens must be non-empty")
        if not isinstance(modes, dict):
            raise DesignTokenError(f"theme {theme_name!r} modes must be an object")
        for mode in THEME_NAMES:
            if not isinstance(modes.get(mode), dict) or not modes[mode]:
                raise DesignTokenError(
                    f"theme {theme_name!r} is missing non-empty {mode!r} mode"
                )

        light_paths = _leaf_paths(modes["light"])
        dark_paths = _leaf_paths(modes["dark"])
        if light_paths != dark_paths:
            missing_dark = sorted(".".join(p) for p in light_paths - dark_paths)
            missing_light = sorted(".".join(p) for p in dark_paths - light_paths)
            raise DesignTokenError(
                f"theme {theme_name!r} light/dark token keys differ; "
                f"missing in dark={missing_dark}, missing in light={missing_light}"
            )

        shared_paths = _leaf_paths(shared)
        if expected_shared_paths is None:
            expected_shared_paths = shared_paths
            expected_mode_paths = light_paths
        elif shared_paths != expected_shared_paths or light_paths != expected_mode_paths:
            raise DesignTokenError(
                f"theme {theme_name!r} does not implement the common token contract"
            )

        # Flattening also validates that all leaves can safely become CSS values.
        _flatten(shared)
        _flatten(modes["light"])
        _flatten(modes["dark"])


@lru_cache(maxsize=1)
def load_tokens() -> dict[str, Any]:
    """Load and validate the checked-in Design Token document."""
    tokens = json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
    validate_tokens(tokens)
    return tokens


def _css_variables(value: dict[str, Any]) -> list[str]:
    return [f"  --dt-{name}: {css_value};" for name, css_value in _flatten(value).items()]


def render_token_css(tokens: dict[str, Any] | None = None) -> str:
    """Compile token JSON into CSS variables and semantic utility classes."""
    tokens = tokens or load_tokens()
    validate_tokens(tokens)
    default_theme = tokens["themes"][tokens["defaultTheme"]]
    shared = _css_variables(default_theme["shared"])
    light = _css_variables(default_theme["modes"]["light"])
    dark = _css_variables(default_theme["modes"]["dark"])
    theme_blocks: list[str] = []
    for theme_name, theme in tokens["themes"].items():
        theme_blocks.extend([
            f':root[data-token-theme="{theme_name}"] {{',
            *_css_variables(theme["shared"]),
            "}",
        ])
        for mode in THEME_NAMES:
            theme_blocks.extend([
                f':root[data-token-theme="{theme_name}"][data-theme="{mode}"] {{',
                f"  color-scheme: {mode};",
                *_css_variables(theme["modes"][mode]),
                "}",
            ])

    return "\n".join(
        [
            "/* UIBench Design Tokens v6: generated from design_tokens/tokens.json */",
            ":root {",
            *shared,
            *light,
            "}",
            ":root[data-theme=\"light\"] {",
            "  color-scheme: light;",
            *light,
            "}",
            ":root[data-theme=\"dark\"] {",
            "  color-scheme: dark;",
            *dark,
            "}",
            *theme_blocks,
            "html[data-theme] { background: var(--dt-color-canvas) !important; }",
            "html[data-theme] body {",
            "  margin: 0 !important;",
            "  min-inline-size: 100%;",
            "  min-block-size: 100vh;",
            "  background-color: var(--dt-color-canvas) !important;",
            "  color: var(--dt-color-text-primary) !important;",
            "  font-family: var(--dt-font-family) !important;",
            "}",
            ".dt-bg-canvas { background-color: var(--dt-color-canvas) !important; }",
            ".dt-bg-canvas-translucent { background-color: var(--dt-color-canvas-translucent) !important; }",
            ".dt-bg-layer-secondary { background-color: var(--dt-color-layer-secondary) !important; }",
            ".dt-bg-layer-tertiary { background-color: var(--dt-color-layer-tertiary) !important; }",
            ".dt-bg-surface { background-color: var(--dt-color-surface) !important; }",
            ".dt-bg-surface-subtle { background-color: var(--dt-color-surface-subtle) !important; }",
            ".dt-bg-surface-raised { background-color: var(--dt-color-surface-raised) !important; }",
            ".dt-bg-component-subtle { background-color: var(--dt-color-component-subtle) !important; }",
            ".dt-bg-component-secondary { background-color: var(--dt-color-component-secondary) !important; }",
            ".dt-bg-primary { background-color: var(--dt-color-primary) !important; }",
            ".dt-bg-primary-hover:hover { background-color: var(--dt-color-primary-hover) !important; }",
            ".dt-bg-primary-container { background-color: var(--dt-color-primary-container) !important; }",
            ".dt-bg-primary-container-subtle { background-color: var(--dt-color-primary-container-subtle) !important; }",
            ".dt-interaction-hover:hover {",
            "  background-image: linear-gradient(var(--dt-color-interaction-hover), var(--dt-color-interaction-hover)) !important;",
            "}",
            ".dt-interaction-pressed:active {",
            "  background-image: linear-gradient(var(--dt-color-interaction-pressed), var(--dt-color-interaction-pressed)) !important;",
            "}",
            ".dt-interaction-selected {",
            "  background-image: linear-gradient(var(--dt-color-interaction-selected), var(--dt-color-interaction-selected)) !important;",
            "}",
            ".dt-bg-disabled { background-color: var(--dt-color-disabled-surface) !important; }",
            ".dt-bg-accent { background-color: var(--dt-color-accent) !important; }",
            ".dt-bg-accent-hover:hover { background-color: var(--dt-color-accent-hover) !important; }",
            ".dt-bg-accent-container { background-color: var(--dt-color-accent-container) !important; }",
            ".dt-bg-accent-container-subtle { background-color: var(--dt-color-accent-container-subtle) !important; }",
            ".dt-text-primary { color: var(--dt-color-text-primary) !important; }",
            ".dt-text-secondary { color: var(--dt-color-text-secondary) !important; }",
            ".dt-text-tertiary { color: var(--dt-color-text-tertiary) !important; }",
            ".dt-text-fourth { color: var(--dt-color-text-fourth) !important; }",
            ".dt-text-on-primary { color: var(--dt-color-on-primary) !important; }",
            ".dt-text-accent { color: var(--dt-color-accent) !important; }",
            ".dt-text-on-accent { color: var(--dt-color-on-accent) !important; }",
            ".dt-text-disabled { color: var(--dt-color-disabled-text) !important; }",
            ".dt-placeholder-secondary::placeholder { color: var(--dt-color-text-secondary) !important; }",
            ".dt-border { border-color: var(--dt-color-border) !important; }",
            ".dt-border-outline { border-color: var(--dt-color-border) !important; }",
            ".dt-border-divider { border-color: var(--dt-color-divider) !important; }",
            ".dt-divide > :not([hidden]) ~ :not([hidden]) {",
            "  border-color: var(--dt-color-divider) !important;",
            "}",
            "/* Harmony content cards are separated by surface contrast, not an outline. */",
            ':root[data-token-theme="harmonyos"] :where(',
            "  .bg-ui-surface.rounded-ui-card.border.border-ui-border,",
            "  .dt-bg-surface.dt-rounded-card.border.dt-border,",
            "  .dt-bg-surface.dt-rounded-card.border.dt-border-outline",
            ") { border-width: 0 !important; }",
            ".dt-form-accent, .dt-accent { accent-color: var(--dt-color-primary) !important; }",
            "input[type=\"checkbox\"][data-component=\"toggle\"] {",
            "  -webkit-appearance: none !important;",
            "  appearance: none !important;",
            "  position: relative !important;",
            "  display: inline-block !important;",
            "  flex: 0 0 auto !important;",
            "  inline-size: 48px !important;",
            "  block-size: 28px !important;",
            "  margin: 0 !important;",
            "  padding: 0 !important;",
            "  border: 0 !important;",
            "  border-radius: 9999px !important;",
            "  background-color: var(--dt-color-component-secondary) !important;",
            "  cursor: pointer;",
            "  vertical-align: middle;",
            "  transition: background-color 120ms ease;",
            "}",
            "input[type=\"checkbox\"][data-component=\"toggle\"]::before {",
            "  content: \"\";",
            "  position: absolute;",
            "  inset-block-start: 2px;",
            "  inset-inline-start: 2px;",
            "  inline-size: 24px;",
            "  block-size: 24px;",
            "  border-radius: 50%;",
            "  background-color: var(--dt-color-surface);",
            "  transition: transform 120ms ease;",
            "}",
            "input[type=\"checkbox\"][data-component=\"toggle\"]:checked {",
            "  background-color: var(--dt-color-primary) !important;",
            "}",
            "input[type=\"checkbox\"][data-component=\"toggle\"]:checked::before {",
            "  transform: translateX(20px);",
            "}",
            "input[type=\"checkbox\"][data-component=\"toggle\"]:disabled {",
            "  cursor: not-allowed;",
            "  opacity: 0.4;",
            "}",
            ".dt-focus:focus-visible {",
            "  outline: 2px solid var(--dt-color-focus) !important;",
            "  outline-offset: 2px !important;",
            "}",
            ".dt-text-success { color: var(--dt-color-success) !important; }",
            ".dt-bg-success { background-color: var(--dt-color-success-container) !important; }",
            ".dt-text-on-success { color: var(--dt-color-on-success-container) !important; }",
            ".dt-text-warning { color: var(--dt-color-warning) !important; }",
            ".dt-bg-warning { background-color: var(--dt-color-warning-container) !important; }",
            ".dt-text-on-warning { color: var(--dt-color-on-warning-container) !important; }",
            ".dt-text-danger { color: var(--dt-color-danger) !important; }",
            ".dt-bg-danger { background-color: var(--dt-color-danger-container) !important; }",
            ".dt-text-on-danger { color: var(--dt-color-on-danger-container) !important; }",
            ".dt-bg-scrim { background-color: var(--dt-color-scrim) !important; }",
            ".dt-shadow-surface { box-shadow: var(--dt-elevation-surface) !important; }",
            ".dt-font { font-family: var(--dt-font-family) !important; }",
            ".dt-text-title {",
            "  font-size: var(--dt-font-size-title) !important;",
            "  font-weight: var(--dt-font-weight-title) !important;",
            "  line-height: var(--dt-font-line-title) !important;",
            "}",
            ".dt-text-body {",
            "  font-size: var(--dt-font-size-body) !important;",
            "  line-height: var(--dt-font-line-body) !important;",
            "}",
            ".dt-text-caption { font-size: var(--dt-font-size-caption) !important; }",
            ".dt-p-page { padding: var(--dt-space-page) !important; }",
            ".dt-mx-page {",
            "  margin-left: var(--dt-space-page) !important;",
            "  margin-right: var(--dt-space-page) !important;",
            "}",
            ".dt-px-page {",
            "  padding-left: var(--dt-space-page) !important;",
            "  padding-right: var(--dt-space-page) !important;",
            "}",
            ".dt-py-page {",
            "  padding-top: var(--dt-space-page) !important;",
            "  padding-bottom: var(--dt-space-page) !important;",
            "}",
            ".dt-pb-page { padding-bottom: var(--dt-space-page) !important; }",
            ".dt-p-card { padding: var(--dt-space-card) !important; }",
            ".dt-py-card {",
            "  padding-top: var(--dt-space-card) !important;",
            "  padding-bottom: var(--dt-space-card) !important;",
            "}",
            ".dt-gap-section { gap: var(--dt-space-section) !important; }",
            ".dt-mt-section { margin-top: var(--dt-space-section) !important; }",
            ".dt-mb-section { margin-bottom: var(--dt-space-section) !important; }",
            ".dt-pt-section { padding-top: var(--dt-space-section) !important; }",
            ".dt-gap-item { gap: var(--dt-space-item) !important; }",
            ".dt-gap-compact { gap: var(--dt-space-compact) !important; }",
            ".dt-mt-compact { margin-top: var(--dt-space-compact) !important; }",
            ".dt-rounded-card { border-radius: var(--dt-radius-card) !important; }",
            ".dt-rounded-control { border-radius: var(--dt-radius-control) !important; }",
            ".dt-rounded-pill, .dt-rounded-full { border-radius: var(--dt-radius-pill) !important; }",
            "",
            "/* Compatibility aliases for previously generated Tailwind-like dt-* classes. */",
            ".dt-py-3 {",
            "  padding-top: var(--dt-space-card) !important;",
            "  padding-bottom: var(--dt-space-card) !important;",
            "}",
            ".dt-bg-canvas\\/90 { background-color: var(--dt-color-canvas-translucent) !important; }",
            ".dt-bg-primary\\/10 { background-color: var(--dt-color-primary-container-subtle) !important; }",
            ".dt-bg-accent\\/15 { background-color: var(--dt-color-accent-container-subtle) !important; }",
            ".hover\\:dt-bg-surface:hover,",
            ".hover\\:dt-bg-surface-subtle:hover,",
            ".hover\\:dt-bg-surface-raised:hover,",
            ".hover\\:dt-bg-primary-hover:hover {",
            "  background-image: linear-gradient(var(--dt-color-interaction-hover), var(--dt-color-interaction-hover)) !important;",
            "}",
            ".active\\:dt-bg-surface:active,",
            ".active\\:dt-bg-surface-subtle:active,",
            ".active\\:dt-bg-surface-raised:active,",
            ".active\\:dt-bg-primary-hover:active {",
            "  background-image: linear-gradient(var(--dt-color-interaction-pressed), var(--dt-color-interaction-pressed)) !important;",
            "}",
            ".focus\\:dt-focus:focus-visible {",
            "  outline: 2px solid var(--dt-color-focus) !important;",
            "  outline-offset: 2px !important;",
            "}",
            ".placeholder\\:dt-placeholder-secondary::placeholder {",
            "  color: var(--dt-color-text-secondary) !important;",
            "}",
            "",
            "/* Best-effort theme compatibility for historical generated HTML.",
            "   New generations receive the system Tailwind token preset. */",
            ':root[data-token-theme] :is(.bg-white) {',
            "  background-color: var(--dt-color-surface) !important;",
            "}",
            ':root[data-token-theme] :is(.bg-gray-50, .bg-slate-50, .bg-zinc-50, .bg-neutral-50) {',
            "  background-color: var(--dt-color-canvas) !important;",
            "}",
            ':root[data-token-theme] :is(.bg-gray-100, .bg-gray-200, .bg-slate-100, .bg-slate-200, .bg-zinc-100, .bg-neutral-100) {',
            "  background-color: var(--dt-color-component-subtle) !important;",
            "}",
            ':root[data-token-theme] :is(.bg-gray-600, .bg-gray-700, .bg-gray-800, .bg-gray-900, .bg-slate-700, .bg-slate-800, .bg-slate-900) {',
            "  background-color: var(--dt-color-surface-raised) !important;",
            "}",
            ':root[data-token-theme] :is(.text-gray-900, .text-gray-800, .text-gray-700, .text-slate-900, .text-slate-800, .text-slate-700, .text-zinc-900, .text-neutral-900) {',
            "  color: var(--dt-color-text-primary) !important;",
            "}",
            ':root[data-token-theme] :is(.text-gray-600, .text-gray-500, .text-gray-400, .text-gray-300, .text-slate-600, .text-slate-500, .text-slate-400, .text-slate-300, .text-zinc-500, .text-neutral-500) {',
            "  color: var(--dt-color-text-secondary) !important;",
            "}",
            ':root[data-token-theme] :is(.border-white, .border-gray-100, .border-gray-200, .border-gray-300, .border-gray-700, .border-slate-100, .border-slate-200, .border-slate-700, .border-zinc-200, .border-neutral-200) {',
            "  border-color: var(--dt-color-border) !important;",
            "}",
            ':root[data-token-theme] :is(.bg-indigo-600, .bg-blue-600, .bg-violet-600) {',
            "  background-color: var(--dt-color-primary) !important;",
            "}",
            ':root[data-token-theme] :is(.bg-indigo-600, .bg-blue-600, .bg-violet-600).text-white {',
            "  color: var(--dt-color-on-primary) !important;",
            "}",
            ':root[data-token-theme] :is(.text-indigo-600, .text-blue-600, .text-violet-600, .text-purple-600, .text-sky-600, .text-cyan-600, .text-teal-600) {',
            "  color: var(--dt-color-primary) !important;",
            "}",
            ':root[data-token-theme] :is(.bg-indigo-50, .bg-indigo-100, .bg-blue-50, .bg-blue-100, .bg-violet-50, .bg-violet-100, .bg-purple-50, .bg-sky-50, .bg-cyan-50, .bg-cyan-100, .bg-teal-50) {',
            "  background-color: var(--dt-color-component-subtle) !important;",
            "}",
            ':root[data-token-theme] :is(.bg-green-50, .bg-green-100, .bg-emerald-50, .bg-emerald-100) {',
            "  background-color: var(--dt-color-success-container) !important;",
            "}",
            ':root[data-token-theme] :is(.text-green-600, .text-emerald-600) {',
            "  color: var(--dt-color-success) !important;",
            "}",
            ':root[data-token-theme] :is(.bg-amber-50, .bg-amber-100, .bg-yellow-50, .bg-orange-50) {',
            "  background-color: var(--dt-color-warning-container) !important;",
            "}",
            ':root[data-token-theme] :is(.text-amber-600, .text-orange-600) {',
            "  color: var(--dt-color-warning) !important;",
            "}",
            ':root[data-token-theme] :is(.bg-red-50, .bg-red-100, .bg-rose-50, .bg-rose-100, .bg-pink-50) {',
            "  background-color: var(--dt-color-danger-container) !important;",
            "}",
            ':root[data-token-theme] :is(.text-red-600, .text-rose-600, .text-pink-600) {',
            "  color: var(--dt-color-danger) !important;",
            "}",
            ':root[data-token-theme] :is(.ring-indigo-200, .ring-blue-200) {',
            "  --tw-ring-color: var(--dt-color-focus) !important;",
            "}",
            "",
        ]
    )


_CLASS_ATTR_RE = re.compile(
    r"(\bclass\s*=\s*)([\"'])(.*?)\2",
    re.IGNORECASE | re.DOTALL,
)
_TOKEN_OPACITY_RE = re.compile(
    r"dt-bg-(canvas|primary|accent)/(\d{1,3})$",
    re.IGNORECASE,
)
_UI_BG_OPACITY_RE = re.compile(
    r"bg-ui-(canvas|primary|accent|surface-raised|success|warning|danger)"
    r"/(\d{1,3})$",
    re.IGNORECASE,
)
_UI_SHADOW_OPACITY_RE = re.compile(
    r"shadow-ui-(primary|accent|surface)/(\d{1,3})$",
    re.IGNORECASE,
)
_HTML_TAG_RE = re.compile(r"<html\b([^>]*)>", re.IGNORECASE)
_THEME_ATTR_RE = re.compile(r"\sdata-theme\s*=\s*([\"']).*?\1", re.IGNORECASE)
_TOKEN_THEME_ATTR_RE = re.compile(
    r"\sdata-token-theme\s*=\s*([\"']).*?\1", re.IGNORECASE
)
_TAILWIND_PRESET_SCRIPT_RE = re.compile(
    rf"<script\b[^>]*\b{TAILWIND_TOKEN_PRESET_MARKER}\b[^>]*>",
    re.IGNORECASE,
)


def _tailwind_token_class_is_known(token: str) -> bool:
    """Return whether a class is generated by the token Tailwind preset."""
    base = token.rsplit(":", 1)[-1]
    color_roles = TAILWIND_TOKEN_COLOR_ROLES
    for prefix in (
        "bg-", "text-", "border-", "divide-", "ring-", "outline-",
        "accent-", "placeholder-", "caret-", "decoration-", "from-",
        "via-", "to-",
    ):
        if base.startswith(prefix) and base[len(prefix):] in color_roles:
            return True

    spacing = "|".join(re.escape(key) for key in TAILWIND_TOKEN_SPACING_ROLES)
    if re.fullmatch(
        rf"(?:p[trblxy]?|m[trblxy]?|gap(?:-[xy])?|space-[xy]|"
        rf"inset(?:-[xy])?|top|right|bottom|left|w|min-w|max-w|h|min-h|max-h|"
        rf"translate-[xy])-({spacing})",
        base,
    ):
        return True

    radius = "|".join(re.escape(key) for key in TAILWIND_TOKEN_RADIUS_ROLES)
    if re.fullmatch(rf"rounded(?:-[trbl]{{1,2}})?-({radius})", base):
        return True
    if base == "font-ui":
        return True
    if base in {f"text-{key}" for key in TAILWIND_TOKEN_FONT_SIZE_ROLES}:
        return True
    if re.fullmatch(r"border(?:-[trblxy])?-ui-hairline", base):
        return True
    return base == "shadow-ui-surface"


def _normalize_class_token(token: str) -> str | None:
    if token in _DROPPED_TOKEN_CLASSES:
        return None
    aliased = TOKEN_CLASS_ALIASES.get(token)
    if aliased:
        return aliased

    opacity = _TOKEN_OPACITY_RE.fullmatch(token)
    if opacity:
        role, raw_opacity = opacity.groups()
        amount = int(raw_opacity)
        if role == "canvas":
            return "dt-bg-canvas-translucent"
        suffix = "container" if amount >= 20 else "container-subtle"
        return f"dt-bg-{role}-{suffix}"

    variant_prefix, separator, base = token.rpartition(":")
    if not separator:
        variant_prefix = ""
        base = token
    ui_opacity = _UI_BG_OPACITY_RE.fullmatch(base)
    if ui_opacity:
        role, raw_opacity = ui_opacity.groups()
        amount = int(raw_opacity)
        if role == "canvas":
            replacement = "bg-ui-canvas-translucent"
        elif role in {"primary", "accent"}:
            suffix = "container" if amount >= 20 else "container-subtle"
            replacement = f"bg-ui-{role}-{suffix}"
        elif role in {"success", "warning", "danger"}:
            replacement = f"bg-ui-{role}-container"
        else:
            # There is intentionally no cross-theme translucent raised-surface
            # token. Preserve the surface role and drop only the invented alpha.
            replacement = "bg-ui-surface-raised"
        return f"{variant_prefix}:{replacement}" if variant_prefix else replacement

    ui_shadow = _UI_SHADOW_OPACITY_RE.fullmatch(base)
    if ui_shadow:
        # Coloured shadow tokens are not part of the multi-theme contract.
        # Preserve elevation intent with the one neutral semantic shadow.
        replacement = "shadow-ui-surface"
        return f"{variant_prefix}:{replacement}" if variant_prefix else replacement

    if token.startswith("hover:dt-bg-"):
        return "dt-interaction-hover"
    if token.startswith("active:dt-bg-"):
        return "dt-interaction-pressed"
    if token == "focus:dt-focus":
        return "dt-focus"
    if token == "placeholder:dt-placeholder-secondary":
        return "dt-placeholder-secondary"
    return token


def normalize_design_token_classes(html: str) -> str:
    """Rewrite common model-invented dt-* spellings to the stable contract."""

    def replace_classes(match: re.Match[str]) -> str:
        normalized: list[str] = []
        for token in match.group(3).split():
            replacement = _normalize_class_token(token)
            if replacement is None:
                continue
            if replacement not in normalized:
                normalized.append(replacement)
        return f"{match.group(1)}{match.group(2)}{' '.join(normalized)}{match.group(2)}"

    return _CLASS_ATTR_RE.sub(replace_classes, html)


def find_unknown_design_token_classes(html: str) -> tuple[str, ...]:
    """Return unresolved legacy or Tailwind-preset token utilities."""
    normalized = normalize_design_token_classes(html)
    unknown: set[str] = set()
    for match in _CLASS_ATTR_RE.finditer(normalized):
        for token in match.group(3).split():
            is_legacy = token.startswith("dt-") or ":dt-" in token
            if is_legacy and token not in DESIGN_TOKEN_CLASSES:
                unknown.add(token)
                continue
            base = token.rsplit(":", 1)[-1]
            if "ui-" in base and not _tailwind_token_class_is_known(token):
                unknown.add(token)
    return tuple(sorted(unknown))


def _inject_tailwind_token_preset(html: str) -> str:
    if _TAILWIND_PRESET_SCRIPT_RE.search(html):
        return html
    script = render_tailwind_token_config_script()
    head_end = re.search(r"</head\s*>", html, re.IGNORECASE)
    if head_end:
        return html[:head_end.start()] + script + html[head_end.start():]
    body = re.search(r"<body\b", html, re.IGNORECASE)
    if body:
        return html[:body.start()] + script + html[body.start():]
    return html + script


class _DesignTokenStylesheetParser(HTMLParser):
    """Detect the document's exact token stylesheet link."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.found = False
        self._inert_roots: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        tag = tag.casefold()
        if tag in {"template", "svg", "math", "noscript"}:
            self._inert_roots.append(tag)
            return
        if self.found or self._inert_roots or tag != "link":
            return

        # HTML ignores duplicate attributes after the first one. Mirror that
        # behavior so a later decoy href cannot suppress the real injection.
        attributes: dict[str, str | None] = {}
        for name, value in attrs:
            attributes.setdefault(name.casefold(), value)

        href = attributes.get("href")
        rel = attributes.get("rel")
        if href != "/design-tokens.css" or rel is None:
            return
        if "stylesheet" in {token.casefold() for token in rel.split()}:
            self.found = True

    def handle_endtag(self, tag: str) -> None:
        tag = tag.casefold()
        if tag in self._inert_roots:
            index = len(self._inert_roots) - 1 - self._inert_roots[::-1].index(tag)
            del self._inert_roots[index:]

    def handle_startendtag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        """Mirror HTML self-closing semantics for inert containers.

        The slash in ``<template/>`` and ``<noscript/>`` is ignored by an HTML
        parser, so a following link is still inert.  SVG and MathML enter
        foreign-content parsing, where the self-closing flag is meaningful.
        """
        folded = tag.casefold()
        self.handle_starttag(tag, attrs)
        if folded not in {"template", "noscript"}:
            self.handle_endtag(tag)


def _has_design_token_stylesheet(html: str) -> bool:
    parser = _DesignTokenStylesheetParser()
    parser.feed(html)
    parser.close()
    return parser.found


def inject_design_tokens(
    html: str,
    theme: str = "light",
    token_theme: str = DEFAULT_TOKEN_THEME,
) -> str:
    """Attach the token stylesheet, design system, and mode to a document."""
    if theme not in THEME_NAMES:
        raise DesignTokenError(f"unknown theme {theme!r}")
    if token_theme not in TOKEN_THEME_NAMES:
        raise DesignTokenError(f"unknown token theme {token_theme!r}")

    html = normalize_design_token_classes(html)
    unknown_classes = find_unknown_design_token_classes(html)
    if unknown_classes:
        LOGGER.warning(
            "Generated HTML contains unknown Design Token classes: %s",
            ", ".join(unknown_classes),
        )

    def set_theme(match: re.Match[str]) -> str:
        attrs = match.group(1)
        if _THEME_ATTR_RE.search(attrs):
            attrs = _THEME_ATTR_RE.sub(f' data-theme="{theme}"', attrs)
        else:
            attrs += f' data-theme="{theme}"'
        if _TOKEN_THEME_ATTR_RE.search(attrs):
            attrs = _TOKEN_THEME_ATTR_RE.sub(
                f' data-token-theme="{token_theme}"', attrs
            )
        else:
            attrs += f' data-token-theme="{token_theme}"'
        return f"<html{attrs}>"

    html, replaced = _HTML_TAG_RE.subn(set_theme, html, count=1)
    if not replaced:
        html = (
            f'<html data-theme="{theme}" data-token-theme="{token_theme}">'
            f"<head></head><body>{html}</body></html>"
        )

    if not _has_design_token_stylesheet(html):
        link = '<link rel="stylesheet" href="/design-tokens.css">'
        head = re.search(r"<head\b[^>]*>", html, re.IGNORECASE)
        if head:
            html = html[:head.end()] + link + html[head.end():]
        else:
            tag = _HTML_TAG_RE.search(html)
            if tag:
                html = html[:tag.end()] + f"<head>{link}</head>" + html[tag.end():]
            else:
                html = link + html
    return _inject_tailwind_token_preset(html)


MOBILE_TOKEN_INSTRUCTIONS = """

【主题 Tailwind Preset】
- 只写 Tailwind class；不要写 CSS 变量、自定义 style 或 `tailwind.config`。
  UIBench 会把 Design Token 作为固定 Tailwind Theme 注入，同一 DOM 自动适配
  HarmonyOS、Spotify、Netflix、Notion 及 light/dark，不要加入主题切换 JS。
- 主题颜色使用 Tailwind 语法：背景优先 bg-ui-canvas / bg-ui-surface /
  bg-ui-surface-raised / bg-ui-component-subtle / bg-ui-component-secondary；正文使用
  text-ui-fg / text-ui-fg-secondary / text-ui-fg-tertiary / text-ui-fg-fourth；品牌操作使用
  bg-ui-primary text-ui-on-primary，hover:bg-ui-primary-hover；次级强调使用 ui-accent 系列。
- 不给 `ui-*` 添加 `/10`、`/20`、`/90` 等透明度后缀：弱品牌背景使用
  bg-ui-primary-container-subtle，半透明画布使用 bg-ui-canvas-translucent；确需浮层阴影时
  只使用 shadow-ui-surface。
- 普通卡片使用 `bg-ui-surface rounded-ui-card p-ui-card`，依靠画布与表面色形成层级，
  默认不要添加整圈 border 或 shadow。列表内部需要分隔时，只在相邻行之间使用
  `border-b-ui-hairline border-ui-divider`，最后一行不画；焦点使用
  focus-visible:ring-2 focus-visible:ring-ui-focus。状态色使用 ui-success / ui-warning / ui-danger 系列。不要使用
  Tailwind 内置调色板色、hex、rgb/hsl 或 `dark:*` 决定主题外观。
- Token 间距是普通 Tailwind spacing key：ui-page / ui-section / ui-card / ui-item /
  ui-compact，可自由组合 px-ui-page、p-ui-card、py-ui-item、gap-ui-item、mt-ui-section 等
  标准方向；圆角使用 rounded-ui-card / rounded-ui-control / rounded-ui-pill，字体使用 font-ui。
- 根容器建议 `bg-ui-canvas text-ui-fg font-ui`；其余 flex/grid、尺寸、定位和响应式继续使用
  标准 Tailwind。
"""


__all__ = [
    "DESIGN_TOKEN_CLASSES",
    "DesignTokenError",
    "DEFAULT_TOKEN_THEME",
    "MOBILE_TOKEN_INSTRUCTIONS",
    "THEME_NAMES",
    "TOKEN_THEME_NAMES",
    "find_unknown_design_token_classes",
    "inject_design_tokens",
    "load_tokens",
    "normalize_design_token_classes",
    "render_tailwind_token_config_script",
    "render_token_css",
    "tailwind_token_preset",
    "validate_tokens",
]
