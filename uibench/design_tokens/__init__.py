"""Multi-system Design Token support for generated mobile previews.

The feature is intentionally isolated in this package so the upstream UIBench
layout, model registry, and logging code can continue to track the fork with
minimal changes.  Tokens are stored as data, validated here, and rendered into
CSS variables plus a small semantic utility-class contract.
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
    "dt-p-card",
    "dt-p-page",
    "dt-placeholder-secondary",
    "dt-px-page",
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
}


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
            ".dt-form-accent, .dt-accent { accent-color: var(--dt-color-primary) !important; }",
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
            ".dt-px-page {",
            "  padding-left: var(--dt-space-page) !important;",
            "  padding-right: var(--dt-space-page) !important;",
            "}",
            ".dt-py-page {",
            "  padding-top: var(--dt-space-page) !important;",
            "  padding-bottom: var(--dt-space-page) !important;",
            "}",
            ".dt-p-card { padding: var(--dt-space-card) !important; }",
            ".dt-gap-section { gap: var(--dt-space-section) !important; }",
            ".dt-gap-item { gap: var(--dt-space-item) !important; }",
            ".dt-gap-compact { gap: var(--dt-space-compact) !important; }",
            ".dt-rounded-card { border-radius: var(--dt-radius-card) !important; }",
            ".dt-rounded-control { border-radius: var(--dt-radius-control) !important; }",
            ".dt-rounded-pill, .dt-rounded-full { border-radius: var(--dt-radius-pill) !important; }",
            "",
            "/* Compatibility aliases for previously generated Tailwind-like dt-* classes. */",
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
            "/* Best-effort theme compatibility for HTML generated before v0.5.",
            "   New generations must use dt-* classes and do not rely on this layer. */",
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
_HTML_TAG_RE = re.compile(r"<html\b([^>]*)>", re.IGNORECASE)
_THEME_ATTR_RE = re.compile(r"\sdata-theme\s*=\s*([\"']).*?\1", re.IGNORECASE)
_TOKEN_THEME_ATTR_RE = re.compile(
    r"\sdata-token-theme\s*=\s*([\"']).*?\1", re.IGNORECASE
)


def _normalize_class_token(token: str) -> str:
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
            if replacement not in normalized:
                normalized.append(replacement)
        return f"{match.group(1)}{match.group(2)}{' '.join(normalized)}{match.group(2)}"

    return _CLASS_ATTR_RE.sub(replace_classes, html)


def find_unknown_design_token_classes(html: str) -> tuple[str, ...]:
    """Return unresolved dt-* classes after known aliases are normalized."""
    normalized = normalize_design_token_classes(html)
    unknown: set[str] = set()
    for match in _CLASS_ATTR_RE.finditer(normalized):
        for token in match.group(3).split():
            is_token_class = token.startswith("dt-") or ":dt-" in token
            if is_token_class and token not in DESIGN_TOKEN_CLASSES:
                unknown.add(token)
    return tuple(sorted(unknown))


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

    if _has_design_token_stylesheet(html):
        return html

    link = '<link rel="stylesheet" href="/design-tokens.css">'
    head = re.search(r"<head\b[^>]*>", html, re.IGNORECASE)
    if head:
        return html[:head.end()] + link + html[head.end():]

    tag = _HTML_TAG_RE.search(html)
    if tag:
        return html[:tag.end()] + f"<head>{link}</head>" + html[tag.end():]
    return link + html


MOBILE_TOKEN_INSTRUCTIONS = """

【Design Token 合约：多品牌风格 × 白天 / 黑夜】
- UIBench 会注入 `/design-tokens.css`，通过 `data-token-theme` 在 HarmonyOS、Spotify、
  Netflix、Notion 风格间迁移，并通过 `data-theme="light|dark"` 切换明暗模式。
- 所有可主题化颜色必须使用以下语义类，禁止使用 Tailwind 调色板颜色类、十六进制、
  rgb/hsl 颜色以及 `dark:*`：
  - 页面和不透明层级：dt-bg-canvas / dt-bg-canvas-translucent /
    dt-bg-layer-secondary / dt-bg-layer-tertiary
  - 内容表面：dt-bg-surface / dt-bg-surface-raised
  - 组件弱填充：搜索框、弱按钮、图标底使用 dt-bg-component-subtle；需要更明显的
    中性填充时使用 dt-bg-component-secondary。dt-bg-surface-subtle 仅为历史 HTML 兼容，
    新生成内容不要使用
  - 文字：dt-text-primary / dt-text-secondary / dt-text-tertiary /
    dt-text-fourth / dt-text-disabled
  - 主操作：dt-bg-primary / dt-text-on-primary / dt-focus；交互态组合
    dt-interaction-hover / dt-interaction-pressed，不要自行换成另一种主色
  - 高亮容器：dt-bg-primary-container / dt-bg-primary-container-subtle；选中态可组合
    dt-interaction-selected
  - 辅助强调：dt-bg-accent / dt-bg-accent-hover / dt-bg-accent-container /
    dt-bg-accent-container-subtle / dt-text-accent / dt-text-on-accent。只有业务确实存在
    独立的次级品牌或信息语义时才能小面积使用，不得将它作为随机装饰色
    或另一套主色；一般 CTA、
    选中态和品牌强调继续使用 primary。Spotify 主题中 accent 是 primary 的
    兼容别名，不会引入第二套品牌色。
  - 边界与表单：组件轮廓使用 border dt-border-outline；单条列表分隔使用
    border-b dt-border-divider；一组相邻列表项可在父容器使用 divide-y dt-divide。
    dt-border 仅为历史兼容；表单还可使用 dt-placeholder-secondary / dt-form-accent
  - 状态：dt-text-success|warning|danger、dt-bg-success|warning|danger，状态色背景中的
    文字使用对应的 dt-text-on-success|warning|danger
- 页面根容器使用 `dt-bg-canvas dt-text-primary dt-font`；卡片优先组合
  `dt-bg-surface dt-rounded-card dt-p-card`，不要为了装饰给每张卡片默认添加边框或阴影；
  只有确实需要层级或边界时才增加 `dt-shadow-surface` 或 `border dt-border-outline`。
- 主要间距与形状使用共享类：dt-p-page / dt-px-page / dt-py-page / dt-p-card /
  dt-gap-section / dt-gap-item / dt-gap-compact / dt-rounded-card /
  dt-rounded-control / dt-rounded-pill。页面左右安全边距用 dt-px-page，纵向节奏
  自行用 Tailwind 的 pt-*/pb-* 控制；只需要横向内边距时不要退回四边的 dt-p-page。
- `dt-*` 是完整的普通 CSS 类名，不是 Tailwind 类：禁止添加 `hover:`、`active:`、
  `focus:`、`placeholder:` 等前缀，也禁止添加 `/10`、`/90` 等透明度后缀。
  例如直接写 `dt-interaction-hover`、`dt-focus`、`dt-placeholder-secondary`、
  `dt-bg-primary-container-subtle`、`dt-bg-canvas-translucent`。
- 头像、圆形图标和进度条圆头必须使用 `dt-rounded-pill`；不要创造
  `dt-rounded-full` 或其他未在本合约列出的 `dt-*` 类。
- 可以继续使用 Tailwind 的布局、尺寸、定位、响应式和字重工具类，但不要再用
  `bg-white`、`text-gray-*`、`bg-slate-*`、`border-zinc-*` 等直接决定主题的类。
- 同一份 HTML 必须同时适配全部设计体系及白天/黑夜；不要复制 DOM，不要加入主题切换 JS。
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
    "render_token_css",
    "validate_tokens",
]
