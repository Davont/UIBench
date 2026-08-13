"""Design Token contract tests; no model credentials or inference required."""
from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import app as app_mod
from uibench.design_tokens import (
    DesignTokenError,
    find_unknown_design_token_classes,
    inject_design_tokens,
    load_tokens,
    normalize_design_token_classes,
    render_token_css,
    validate_tokens,
)
from uibench.prompts import SYSTEM_MOBILE


def test_checked_in_tokens_have_matching_light_dark_contract() -> None:
    tokens = load_tokens()
    validate_tokens(tokens)
    assert tokens["schemaVersion"] == 6
    assert tokens["defaultTheme"] == "harmonyos"
    assert tokens["defaultMode"] == "light"
    assert set(tokens["themes"]) == {
        "harmonyos", "spotify", "netflix", "notion"
    }
    for theme in tokens["themes"].values():
        assert set(theme["modes"]) == {"light", "dark"}
        assert theme["shared"]["radius"]["card"]


def test_harmonyos_uses_official_semantic_color_mapping() -> None:
    harmonyos = load_tokens()["themes"]["harmonyos"]["modes"]
    light = harmonyos["light"]["color"]
    dark = harmonyos["dark"]["color"]

    assert light["primary"] == "#0A59F7"
    assert dark["primary"] == "#317AF7"
    assert light["accent"] == light["primary"]
    assert dark["accent"] == dark["primary"]
    assert light["layer-secondary"] == "#F1F3F5"
    assert light["layer-tertiary"] == "#E5E5EA"
    assert light["surface-subtle"] == "rgba(0, 0, 0, 0.047)"
    assert light["component-subtle"] == "rgba(0, 0, 0, 0.047)"
    assert light["component-secondary"] == "rgba(0, 0, 0, 0.098)"
    assert dark["surface"] == "#202224"
    assert dark["layer-secondary"] == "#191A1C"
    assert dark["layer-tertiary"] == "#202224"
    assert dark["surface-subtle"] == "rgba(255, 255, 255, 0.047)"
    assert dark["surface-raised"] == "#2E3033"
    assert light["text-tertiary"] == "rgba(0, 0, 0, 0.40)"
    assert dark["text-fourth"] == "rgba(255, 255, 255, 0.20)"
    assert light["divider"] == "rgba(0, 0, 0, 0.05)"
    assert dark["divider"] == "rgba(255, 255, 255, 0.05)"
    assert light["success"] == "#64BB5C"
    assert dark["success"] == "#5BA854"
    assert light["warning"] == "#ED6F21"
    assert dark["warning"] == "#DB6B42"
    assert light["danger"] == "#E84026"
    assert dark["danger"] == "#D94838"
    assert light["interaction-hover"] == "rgba(0, 0, 0, 0.047)"
    assert dark["interaction-pressed"] == "rgba(255, 255, 255, 0.098)"


def test_spotify_does_not_introduce_an_unverified_second_brand_color() -> None:
    spotify = load_tokens()["themes"]["spotify"]["modes"]

    for mode in ("light", "dark"):
        color = spotify[mode]["color"]
        assert color["primary"] == "#1ED760"
        assert color["primary-hover"] == "#3BE477"
        assert color["accent"] == color["primary"]
        assert color["accent-hover"] == color["primary-hover"]
        assert color["accent-container"] == color["primary-container"]
        assert (
            color["accent-container-subtle"]
            == color["primary-container-subtle"]
        )
        assert color["on-accent"] == color["on-primary"] == "#000000"

    css = render_token_css()
    assert "#AF2896" not in css
    assert "#E133C5" not in css


def test_validator_rejects_mode_key_drift() -> None:
    tokens = deepcopy(load_tokens())
    del tokens["themes"]["notion"]["modes"]["dark"]["color"]["accent"]
    with pytest.raises(DesignTokenError, match="token keys differ"):
        validate_tokens(tokens)


def test_css_contains_modes_variables_and_semantic_classes() -> None:
    css = render_token_css()
    assert ':root[data-theme="light"]' in css
    assert ':root[data-theme="dark"]' in css
    assert ':root[data-token-theme="harmonyos"][data-theme="light"]' in css
    assert ':root[data-token-theme="spotify"][data-theme="dark"]' in css
    assert ':root[data-token-theme="netflix"]' in css
    assert ':root[data-token-theme="notion"]' in css
    assert "--dt-color-primary: #1ED760" in css
    assert "--dt-color-primary: #E50914" in css
    assert "--dt-color-primary: #37352F" in css
    assert "--dt-color-primary: #E6E6E6" in css
    assert "--dt-color-accent: #9B9A97" in css
    assert "--dt-color-primary-container:" in css
    assert "--dt-color-primary-container-subtle:" in css
    assert "--dt-color-canvas-translucent:" in css
    assert "--dt-color-layer-secondary:" in css
    assert "--dt-color-layer-tertiary:" in css
    assert "--dt-color-component-subtle:" in css
    assert "--dt-color-component-secondary:" in css
    assert "--dt-color-text-tertiary:" in css
    assert "--dt-color-text-fourth:" in css
    assert "--dt-color-divider:" in css
    assert "--dt-color-accent-container:" in css
    assert "--dt-color-accent-container-subtle:" in css
    assert "--dt-color-interaction-hover:" in css
    assert "--dt-color-interaction-pressed:" in css
    assert "--dt-color-interaction-selected:" in css
    assert "--dt-color-canvas:" in css
    assert ".dt-bg-canvas" in css
    assert ".dt-bg-accent" in css
    assert ".dt-text-on-accent" in css
    assert ".dt-bg-primary-container" in css
    assert ".dt-bg-primary-container-subtle" in css
    assert ".dt-bg-canvas-translucent" in css
    assert ".dt-bg-layer-secondary" in css
    assert ".dt-bg-layer-tertiary" in css
    assert ".dt-bg-component-subtle" in css
    assert ".dt-bg-component-secondary" in css
    assert ".dt-bg-accent-container" in css
    assert ".dt-bg-accent-container-subtle" in css
    assert ".dt-interaction-hover:hover" in css
    assert ".dt-interaction-pressed:active" in css
    assert ".dt-interaction-selected" in css
    assert ".dt-text-primary" in css
    assert ".dt-text-tertiary" in css
    assert ".dt-text-fourth" in css
    assert ".dt-border-outline" in css
    assert ".dt-border-divider" in css
    assert ".dt-divide > :not([hidden]) ~ :not([hidden])" in css
    assert ".dt-rounded-card" in css
    assert ".dt-rounded-pill, .dt-rounded-full" in css
    assert ".dt-bg-canvas\\/90" in css
    assert ".hover\\:dt-bg-surface-subtle:hover" in css
    assert "Best-effort theme compatibility" in css
    assert '.bg-white' in css
    assert '.text-gray-900' in css
    assert "background-color: var(--dt-color-surface) !important" in css


def test_model_invented_token_classes_are_normalized() -> None:
    source = """<div class="dt-rounded-full dt-bg-canvas/90
        dt-bg-primary/10 dt-bg-accent/15 hover:dt-bg-surface-subtle
        active:dt-bg-surface-raised focus:dt-focus
        placeholder:dt-placeholder-secondary"></div>"""
    normalized = normalize_design_token_classes(source)

    assert "dt-rounded-pill" in normalized
    assert "dt-bg-canvas-translucent" in normalized
    assert "dt-bg-primary-container-subtle" in normalized
    assert "dt-bg-accent-container-subtle" in normalized
    assert "dt-interaction-hover" in normalized
    assert "dt-interaction-pressed" in normalized
    assert "dt-focus" in normalized
    assert "dt-placeholder-secondary" in normalized
    assert "/90" not in normalized
    assert "hover:dt-" not in normalized
    assert "dt-rounded-full" not in normalized
    assert find_unknown_design_token_classes(normalized) == ()


def test_axis_page_padding_classes_are_part_of_the_contract() -> None:
    """A model asking only for horizontal page insets must get real CSS.

    ``dt-px-page`` used to match no rule at all, so whole sections silently
    rendered flush against the screen edge.
    """
    css = render_token_css()

    assert (
        ".dt-px-page {\n"
        "  padding-left: var(--dt-space-page) !important;\n"
        "  padding-right: var(--dt-space-page) !important;\n"
        "}"
    ) in css
    assert (
        ".dt-py-page {\n"
        "  padding-top: var(--dt-space-page) !important;\n"
        "  padding-bottom: var(--dt-space-page) !important;\n"
        "}"
    ) in css
    assert find_unknown_design_token_classes(
        '<div class="dt-px-page dt-py-page"></div>'
    ) == ()
    assert "dt-px-page" in SYSTEM_MOBILE


def test_unknown_token_classes_are_reported_without_dropping_html(
    caplog: pytest.LogCaptureFixture,
) -> None:
    source = (
        '<html><head></head><body class="dt-bg-canvas dt-made-up '
        'divide-[var(--dt-border)]"></body></html>'
    )
    with caplog.at_level("WARNING", logger="uibench.design_tokens"):
        rendered = inject_design_tokens(source)

    assert "dt-made-up" in rendered
    assert find_unknown_design_token_classes(rendered) == ("dt-made-up",)
    assert "unknown Design Token classes: dt-made-up" in caplog.text


def test_inject_design_tokens_sets_theme_and_deduplicates_link() -> None:
    source = '<!DOCTYPE html><html lang="zh-CN"><head></head><body></body></html>'
    dark = inject_design_tokens(source, "dark", "harmonyos")
    assert (
        '<html lang="zh-CN" data-theme="dark" data-token-theme="harmonyos">'
        in dark
    )
    assert dark.count("design-tokens.css") == 1

    light = inject_design_tokens(dark, "light", "netflix")
    assert 'data-theme="light"' in light
    assert 'data-theme="dark"' not in light
    assert 'data-token-theme="netflix"' in light
    assert 'data-token-theme="harmonyos"' not in light
    assert light.count("design-tokens.css") == 1


@pytest.mark.parametrize(
    "existing_link",
    [
        '<link rel="stylesheet" href="/design-tokens.css">',
        "<LINK HREF='/design-tokens.css' REL='StyleSheet'>",
        '<link rel="preload stylesheet" href="/design-tokens.css">',
    ],
)
def test_inject_design_tokens_only_deduplicates_a_real_exact_stylesheet_link(
    existing_link: str,
) -> None:
    source = f"<html><head>{existing_link}</head><body></body></html>"

    rendered = inject_design_tokens(source)

    assert rendered.count("/design-tokens.css") == 1
    assert existing_link in rendered


@pytest.mark.parametrize(
    "decoy",
    [
        '<!-- <link href="/design-tokens.css" rel="stylesheet"> -->',
        "<script>const link = '<link href=\"/design-tokens.css\" rel=\"stylesheet\">';</script>",
        '<link rel="stylesheet" href="https://example.com/design-tokens.css">',
        '<link rel="stylesheet" href="//example.com/design-tokens.css">',
        '<link rel="stylesheet" href="/assets/design-tokens.css">',
        '<link rel="stylesheet" href="/design-tokens.css?v=1">',
        '<link rel="preload" href="/design-tokens.css">',
        '<template><link rel="stylesheet" href="/design-tokens.css"></template>',
        '<template/><link rel="stylesheet" href="/design-tokens.css">',
        '<noscript><link rel="stylesheet" href="/design-tokens.css"></noscript>',
        '<noscript/><link rel="stylesheet" href="/design-tokens.css">',
        '<svg><link rel="stylesheet" href="/design-tokens.css"></svg>',
    ],
)
def test_inject_design_tokens_does_not_accept_decoy_mentions(decoy: str) -> None:
    source = f"<html><head>{decoy}</head><body></body></html>"

    rendered = inject_design_tokens(source)

    assert '<head><link rel="stylesheet" href="/design-tokens.css">' in rendered
    assert decoy in rendered


def test_inject_design_tokens_rejects_unknown_mode() -> None:
    with pytest.raises(DesignTokenError, match="unknown theme"):
        inject_design_tokens("<html><head></head><body></body></html>", "system")
    with pytest.raises(DesignTokenError, match="unknown token theme"):
        inject_design_tokens(
            "<html><head></head><body></body></html>", "light", "material"
        )


def test_mobile_prompt_requires_semantic_token_contract() -> None:
    assert "Design Token 合约" in SYSTEM_MOBILE
    assert "HarmonyOS" in SYSTEM_MOBILE
    assert "Spotify" in SYSTEM_MOBILE
    assert "Netflix" in SYSTEM_MOBILE
    assert "Notion" in SYSTEM_MOBILE
    assert "dt-bg-accent" in SYSTEM_MOBILE
    assert "dt-bg-primary-container" in SYSTEM_MOBILE
    assert "dt-bg-canvas-translucent" in SYSTEM_MOBILE
    assert "dt-bg-layer-secondary" in SYSTEM_MOBILE
    assert "dt-bg-layer-tertiary" in SYSTEM_MOBILE
    assert "dt-bg-component-subtle" in SYSTEM_MOBILE
    assert "dt-bg-component-secondary" in SYSTEM_MOBILE
    assert "dt-text-tertiary" in SYSTEM_MOBILE
    assert "dt-text-fourth" in SYSTEM_MOBILE
    assert "dt-border-divider" in SYSTEM_MOBILE
    assert "dt-border-outline" in SYSTEM_MOBILE
    assert "dt-divide" in SYSTEM_MOBILE
    assert "新生成内容不要使用" in SYSTEM_MOBILE
    assert "dt-bg-accent-container" in SYSTEM_MOBILE
    assert "不得将它作为随机装饰色" in SYSTEM_MOBILE
    assert "或另一套主色" in SYSTEM_MOBILE
    assert "Spotify 主题中 accent 是 primary 的" in SYSTEM_MOBILE
    assert "第二强调色" not in SYSTEM_MOBILE
    assert "dt-interaction-hover" in SYSTEM_MOBILE
    assert "dt-interaction-pressed" in SYSTEM_MOBILE
    assert "dt-interaction-selected" in SYSTEM_MOBILE
    assert "禁止添加 `hover:`" in SYSTEM_MOBILE
    assert "不要创造\n  `dt-rounded-full`" in SYSTEM_MOBILE
    assert "dt-bg-canvas" in SYSTEM_MOBILE
    assert "禁止使用 Tailwind 调色板颜色类" in SYSTEM_MOBILE
    assert "不要加入主题切换 JS" in SYSTEM_MOBILE


def test_token_routes_and_theme_controls_are_available() -> None:
    with TestClient(app_mod.app) as client:
        css = client.get("/design-tokens.css")
        assert css.status_code == 200
        assert "text/css" in css.headers["content-type"]
        assert css.headers["cache-control"] == "no-store"
        assert "--dt-color-primary" in css.text

        token_json = client.get("/api/design-tokens")
        assert token_json.status_code == 200
        assert token_json.json()["defaultMode"] == "light"
        assert token_json.json()["defaultTheme"] == "harmonyos"
        assert set(token_json.json()["themes"]) == {
            "harmonyos", "spotify", "netflix", "notion"
        }

        index = client.get("/")
        assert 'data-theme="light"' in index.text
        assert 'data-theme="dark"' in index.text
        assert 'data-token-theme="harmonyos"' in index.text
        assert 'data-token-theme="spotify"' in index.text
        assert 'data-token-theme="netflix"' in index.text
        assert 'data-token-theme="notion"' in index.text
        assert 'data-token-theme="tiktok"' not in index.text
        assert 'data-token-theme="material-3"' not in index.text
        assert 'data-token-theme="ibm-carbon"' not in index.text
        assert "uibench-preview-theme" in index.text
        assert "uibench-preview-token-theme" in index.text
        assert "function normalizeDesignTokenClasses" in index.text
        assert "'dt-rounded-full': 'dt-rounded-pill'" in index.text
        assert "dt-bg-canvas-translucent" in index.text
        assert "dt-interaction-hover" in index.text
        # Adding data-theme changes string offsets, so the head lookup must use
        # a refreshed lowercase copy (a browser regression found this ordering).
        theme_replace = index.text.index("html = html.replace(/<html")
        refreshed_index = index.text.index("low = html.toLowerCase();", theme_replace)
        head_lookup = index.text.index("var idx = low.indexOf('<head>');", refreshed_index)
        assert theme_replace < refreshed_index < head_lookup


def test_render_injection_only_applies_tokens_to_mobile() -> None:
    source = "<!DOCTYPE html><html><head></head><body></body></html>"
    mobile = app_mod.inject_for_render(source, "mobile", "dark", "notion")
    assert "/shared.css" in mobile
    assert "/design-tokens.css" in mobile
    assert 'data-theme="dark"' in mobile
    assert 'data-token-theme="notion"' in mobile

    pc = app_mod.inject_for_render(source, "pc", "dark")
    assert "/shared.css" in pc
    assert "/design-tokens.css" not in pc
    assert "react-classic" in pc
