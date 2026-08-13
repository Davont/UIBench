"""Validated browser snapshot protocol and conservative CSS-to-IR mapping."""
from __future__ import annotations

import base64
import binascii
import math
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

_PX_RE = re.compile(r"^(-?(?:\d+(?:\.\d+)?|\.\d+))px$")
_RGB_RE = re.compile(
    r"^rgba?\(\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\s*,\s*"
    r"(\d+(?:\.\d+)?)(?:\s*,\s*(\d+(?:\.\d+)?))?\s*\)$",
    re.IGNORECASE,
)
MAX_BROWSER_ASSET_BYTES = 2_000_000
MAX_BROWSER_ASSET_TOTAL_BYTES = 8_000_000
_NORMAL_FLOW_DISPLAYS = frozenset({
    "block", "inline-block", "flow-root", "list-item",
})


class BrowserAssetUse(BaseModel):
    """One semantic use of bytes captured from an already-rendered resource."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    kind: Literal["image", "background-image"]
    node_ids: list[str] = Field(
        alias="nodeIds", min_length=1, max_length=100
    )

    @field_validator("node_ids")
    @classmethod
    def node_ids_are_unique(cls, value: list[str]) -> list[str]:
        if any(not node_id or len(node_id) > 200 for node_id in value):
            raise ValueError("browser asset nodeIds must be non-empty and bounded")
        if len(set(value)) != len(value):
            raise ValueError("browser asset nodeIds must be unique")
        return value


class BrowserAssetSnapshot(BaseModel):
    """Bounded browser-fetched bytes; URLs are deliberately not trusted."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    mime_type: str = Field(alias="mimeType", min_length=1, max_length=100)
    content_base64: str = Field(
        alias="contentBase64",
        min_length=4,
        max_length=((MAX_BROWSER_ASSET_BYTES + 2) // 3) * 4,
    )
    uses: list[BrowserAssetUse] = Field(min_length=1, max_length=100)

    @field_validator("content_base64")
    @classmethod
    def content_is_valid_base64(cls, value: str) -> str:
        try:
            decoded = base64.b64decode(value, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError("browser asset contentBase64 is invalid") from exc
        if not decoded or len(decoded) > MAX_BROWSER_ASSET_BYTES:
            raise ValueError("browser asset content is empty or exceeds 2 MB")
        return value

    def decoded_content(self) -> bytes:
        return base64.b64decode(self.content_base64, validate=True)


class BrowserComputedStyle(BaseModel):
    """Whitelisted computed CSS values captured by the sandbox iframe."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    display: str = Field(default="", max_length=100)
    flex_direction: str = Field(default="", alias="flexDirection", max_length=100)
    flex_grow: str = Field(default="", alias="flexGrow", max_length=100)
    flex_shrink: str = Field(default="", alias="flexShrink", max_length=100)
    flex_basis: str = Field(default="", alias="flexBasis", max_length=100)
    position: str = Field(default="", max_length=100)
    top: str = Field(default="", max_length=100)
    left: str = Field(default="", max_length=100)
    width: str = Field(default="", max_length=100)
    height: str = Field(default="", max_length=100)
    padding_top: str = Field(default="", alias="paddingTop", max_length=100)
    padding_right: str = Field(default="", alias="paddingRight", max_length=100)
    padding_bottom: str = Field(default="", alias="paddingBottom", max_length=100)
    padding_left: str = Field(default="", alias="paddingLeft", max_length=100)
    margin_top: str = Field(default="", alias="marginTop", max_length=100)
    margin_right: str = Field(default="", alias="marginRight", max_length=100)
    margin_bottom: str = Field(default="", alias="marginBottom", max_length=100)
    margin_left: str = Field(default="", alias="marginLeft", max_length=100)
    row_gap: str = Field(default="", alias="rowGap", max_length=100)
    column_gap: str = Field(default="", alias="columnGap", max_length=100)
    grid_template_columns: str = Field(
        default="", alias="gridTemplateColumns", max_length=1000
    )
    grid_template_rows: str = Field(
        default="", alias="gridTemplateRows", max_length=1000
    )
    grid_auto_flow: str = Field(default="", alias="gridAutoFlow", max_length=100)
    grid_row_start: str = Field(default="", alias="gridRowStart", max_length=100)
    grid_row_end: str = Field(default="", alias="gridRowEnd", max_length=100)
    grid_column_start: str = Field(
        default="", alias="gridColumnStart", max_length=100
    )
    grid_column_end: str = Field(default="", alias="gridColumnEnd", max_length=100)
    justify_content: str = Field(default="", alias="justifyContent", max_length=100)
    align_items: str = Field(default="", alias="alignItems", max_length=100)
    background_color: str = Field(default="", alias="backgroundColor", max_length=100)
    background_image: str = Field(default="", alias="backgroundImage", max_length=1000)
    border_top_width: str = Field(default="", alias="borderTopWidth", max_length=100)
    border_right_width: str = Field(default="", alias="borderRightWidth", max_length=100)
    border_bottom_width: str = Field(default="", alias="borderBottomWidth", max_length=100)
    border_left_width: str = Field(default="", alias="borderLeftWidth", max_length=100)
    border_top_color: str = Field(default="", alias="borderTopColor", max_length=100)
    border_right_color: str = Field(default="", alias="borderRightColor", max_length=100)
    border_bottom_color: str = Field(default="", alias="borderBottomColor", max_length=100)
    border_left_color: str = Field(default="", alias="borderLeftColor", max_length=100)
    border_top_style: str = Field(default="", alias="borderTopStyle", max_length=100)
    border_right_style: str = Field(default="", alias="borderRightStyle", max_length=100)
    border_bottom_style: str = Field(default="", alias="borderBottomStyle", max_length=100)
    border_left_style: str = Field(default="", alias="borderLeftStyle", max_length=100)
    border_top_left_radius: str = Field(default="", alias="borderTopLeftRadius", max_length=100)
    border_top_right_radius: str = Field(default="", alias="borderTopRightRadius", max_length=100)
    border_bottom_right_radius: str = Field(default="", alias="borderBottomRightRadius", max_length=100)
    border_bottom_left_radius: str = Field(default="", alias="borderBottomLeftRadius", max_length=100)
    opacity: str = Field(default="", max_length=100)
    box_shadow: str = Field(default="", alias="boxShadow", max_length=1000)
    color: str = Field(default="", max_length=100)
    font_size: str = Field(default="", alias="fontSize", max_length=100)
    font_weight: str = Field(default="", alias="fontWeight", max_length=100)
    font_family: str = Field(default="", alias="fontFamily", max_length=500)
    line_height: str = Field(default="", alias="lineHeight", max_length=100)
    text_align: str = Field(default="", alias="textAlign", max_length=100)
    letter_spacing: str = Field(default="", alias="letterSpacing", max_length=100)
    text_decoration_line: str = Field(default="", alias="textDecorationLine", max_length=100)
    text_transform: str = Field(default="", alias="textTransform", max_length=100)
    font_style: str = Field(default="", alias="fontStyle", max_length=100)
    white_space: str = Field(default="", alias="whiteSpace", max_length=100)
    text_overflow: str = Field(default="", alias="textOverflow", max_length=100)
    webkit_line_clamp: str = Field(default="", alias="webkitLineClamp", max_length=100)
    object_fit: str = Field(default="", alias="objectFit", max_length=100)
    overflow_x: str = Field(default="", alias="overflowX", max_length=100)
    overflow_y: str = Field(default="", alias="overflowY", max_length=100)
    transform: str = Field(default="", max_length=1000)
    filter: str = Field(default="", max_length=1000)
    backdrop_filter: str = Field(default="", alias="backdropFilter", max_length=1000)
    clip_path: str = Field(default="", alias="clipPath", max_length=1000)
    pseudo_before_content: str = Field(
        default="", alias="pseudoBeforeContent", max_length=1000
    )
    pseudo_after_content: str = Field(
        default="", alias="pseudoAfterContent", max_length=1000
    )


class BrowserNodeSnapshot(BaseModel):
    """One rendered DOM node addressed by its stable UIBench node ID."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
        allow_inf_nan=False,
    )

    node_id: str = Field(alias="nodeId", min_length=1, max_length=200)
    tag: str = Field(min_length=1, max_length=100)
    bbox: tuple[float, float, float, float]
    visible: bool
    width_sizing: Literal["auto", "explicit", "unknown"] = Field(
        default="unknown", alias="widthSizing"
    )
    single_line_text_width: float | None = Field(
        default=None, alias="singleLineTextWidth", ge=0, le=100_000
    )
    resolved_src: str | None = Field(
        default=None, alias="resolvedSrc", max_length=4000
    )
    direct_parent_node_id: str | None = Field(
        default=None,
        alias="directParentNodeId",
        min_length=1,
        max_length=200,
    )
    is_flex_item: bool | None = Field(default=None, alias="isFlexItem")
    computed: BrowserComputedStyle

    @field_validator("bbox")
    @classmethod
    def bbox_is_bounded(
        cls, value: tuple[float, float, float, float]
    ) -> tuple[float, float, float, float]:
        x, y, width, height = value
        if abs(x) > 100_000 or abs(y) > 100_000:
            raise ValueError("browser snapshot bbox coordinates are out of range")
        if width < 0 or height < 0 or width > 100_000 or height > 100_000:
            raise ValueError("browser snapshot bbox size is out of range")
        return value


class BrowserSnapshot(BaseModel):
    """Versioned deterministic snapshot produced by the browser preview."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
        allow_inf_nan=False,
    )

    snapshot_version: Literal[1] = Field(alias="snapshotVersion")
    viewport_width: int = Field(alias="viewportWidth", ge=240, le=3840)
    viewport_height: int = Field(alias="viewportHeight", ge=240, le=3840)
    theme: Literal["light", "dark"]
    token_theme: Literal["harmonyos", "spotify", "netflix", "notion"] = Field(
        alias="tokenTheme"
    )
    canvas_background_color: str | None = Field(
        default=None,
        alias="canvasBackgroundColor",
        max_length=100,
    )
    canvas_background_image: str | None = Field(
        default=None,
        alias="canvasBackgroundImage",
        max_length=1000,
    )
    nodes: list[BrowserNodeSnapshot] = Field(max_length=10_000)
    assets: list[BrowserAssetSnapshot] = Field(default_factory=list, max_length=32)

    @model_validator(mode="after")
    def references_are_bounded_and_unique(self) -> "BrowserSnapshot":
        node_ids = [node.node_id for node in self.nodes]
        if len(set(node_ids)) != len(node_ids):
            raise ValueError("browser snapshot nodeId values must be unique")
        known_node_ids = set(node_ids)
        for node in self.nodes:
            if node.direct_parent_node_id == node.node_id:
                raise ValueError("browser snapshot node cannot be its own parent")
            if (
                node.direct_parent_node_id is not None
                and node.direct_parent_node_id not in known_node_ids
            ):
                raise ValueError(
                    "browser snapshot directParentNodeId is absent from snapshot nodes"
                )
        asset_references: set[tuple[str, str]] = set()
        total_bytes = 0
        for asset in self.assets:
            total_bytes += len(asset.decoded_content())
            for use in asset.uses:
                for node_id in use.node_ids:
                    if node_id not in known_node_ids:
                        raise ValueError(
                            "browser asset nodeId is absent from snapshot nodes"
                        )
                    reference = (node_id, use.kind)
                    if reference in asset_references:
                        raise ValueError(
                            "browser asset node/kind references must be unique"
                        )
                    asset_references.add(reference)
        if total_bytes > MAX_BROWSER_ASSET_TOTAL_BYTES:
            raise ValueError("browser snapshot assets exceed the 8 MB total limit")
        return self


def _px(value: str) -> float | None:
    match = _PX_RE.fullmatch(value.strip())
    if match is None:
        return None
    parsed = float(match.group(1))
    if not math.isfinite(parsed):
        return None
    if abs(parsed) > 100_000:
        return None
    if abs(parsed) < 0.0001:
        return 0.0
    return round(parsed, 4)


def _color(value: str) -> str | None:
    normalized = value.strip().lower()
    if normalized in {"", "transparent", "rgba(0, 0, 0, 0)"}:
        return None
    if re.fullmatch(r"#[0-9a-f]{6}", normalized):
        return normalized.upper()
    if re.fullmatch(r"#[0-9a-f]{8}", normalized):
        # Browser/CSS uses #RRGGBBAA; ArkUI's canonical integer form is #AARRGGBB.
        return f"#{normalized[7:9]}{normalized[1:7]}".upper()
    match = _RGB_RE.fullmatch(normalized)
    if match is None:
        return None
    red, green, blue = (
        max(0, min(255, round(float(match.group(index)))))
        for index in (1, 2, 3)
    )
    alpha_value = match.group(4)
    alpha = 255 if alpha_value is None else max(
        0, min(255, round(float(alpha_value) * 255))
    )
    if alpha == 0:
        return None
    rgb = f"{red:02X}{green:02X}{blue:02X}"
    return f"#{rgb}" if alpha == 255 else f"#{alpha:02X}{rgb}"


def _split_css_top_level(value: str, delimiter: str) -> tuple[str, ...]:
    """Split a computed CSS value without cutting inside functions.

    Chromium serializes shadow colours as ``rgba(...)`` and separates shadow
    layers with the same comma used inside that colour function.  A small
    balanced-parenthesis splitter is sufficient for computed values and keeps
    the shadow parser independent of authored CSS syntax.
    """
    parts: list[str] = []
    start = 0
    depth = 0
    for index, character in enumerate(value):
        if character == "(":
            depth += 1
        elif character == ")":
            depth = max(0, depth - 1)
        elif character == delimiter and depth == 0:
            parts.append(value[start:index].strip())
            start = index + 1
    parts.append(value[start:].strip())
    return tuple(part for part in parts if part)


def _css_value_tokens(value: str) -> tuple[str, ...]:
    """Tokenize one computed CSS value on top-level whitespace."""
    tokens: list[str] = []
    start: int | None = None
    depth = 0
    for index, character in enumerate(value):
        if character == "(":
            depth += 1
        elif character == ")":
            depth = max(0, depth - 1)
        if character.isspace() and depth == 0:
            if start is not None:
                tokens.append(value[start:index])
                start = None
        elif start is None:
            start = index
    if start is not None:
        tokens.append(value[start:])
    return tuple(tokens)


def _css_shadow_length(value: str) -> float | None:
    """Parse the px lengths emitted by getComputedStyle, including bare zero."""
    if value.strip() in {"0", "+0", "-0"}:
        return 0.0
    return _px(value)


def _screen_ir_shadow(
    value: str,
) -> tuple[dict[str, object] | None, bool]:
    """Map the one CSS shadow shape ArkUI renders with the same parameters.

    Screen IR v2 and ArkUI both carry one outer shadow as blur radius, colour,
    and x/y offsets.  Multiple layers, inset shadows, and non-zero spread have
    no equivalent in the renderer contract and remain explicitly lossy.
    The boolean reports whether the CSS value was completely handled; an
    invisible transparent shadow is handled but produces no modifier.
    """
    normalized = value.strip()
    if normalized.lower() in {"", "none"}:
        return None, True
    layers = _split_css_top_level(normalized, ",")
    if len(layers) != 1:
        return None, False
    tokens = _css_value_tokens(layers[0])
    if any(token.lower() == "inset" for token in tokens):
        return None, False

    color_indexes = [
        index for index, token in enumerate(tokens)
        if classify_css_color(token) != "unsupported"
    ]
    if len(color_indexes) != 1:
        return None, False
    color_index = color_indexes[0]
    color_token = tokens[color_index]
    lengths = tuple(
        _css_shadow_length(token)
        for index, token in enumerate(tokens)
        if index != color_index
    )
    if not 2 <= len(lengths) <= 4 or any(item is None for item in lengths):
        return None, False
    offset_x, offset_y = lengths[:2]
    blur = lengths[2] if len(lengths) >= 3 else 0.0
    spread = lengths[3] if len(lengths) == 4 else 0.0
    assert offset_x is not None and offset_y is not None
    assert blur is not None and spread is not None
    if blur < 0 or spread != 0:
        return None, False
    color = _color(color_token)
    if color is None:
        # The only supported colour with no emitted value is transparent.
        return None, classify_css_color(color_token) == "transparent"
    return {
        "radius": blur,
        "color": color,
        "offsetX": offset_x,
        "offsetY": offset_y,
    }, True


def normalize_css_color(value: str) -> str | None:
    """Return the canonical ArkUI color for currently supported CSS syntax."""
    return _color(value)


TRANSPARENT_COLOR = "#00000000"


def is_opaque_css_color(value: str) -> bool:
    """Whether a captured color fully hides whatever is painted behind it."""
    normalized = _color(value)
    # ``_color`` emits #RRGGBB when the alpha channel is fully opaque and
    # #AARRGGBB otherwise.
    return normalized is not None and len(normalized) == 7


def classify_css_color(
    value: str,
) -> Literal["transparent", "supported", "unsupported"]:
    """Classify a captured CSS color without silently treating new syntax as none.

    ArkUI export currently serializes sRGB hex and legacy ``rgb()/rgba()``
    values. Browsers may preserve modern computed forms such as ``oklch()``;
    callers must surface those as unsupported instead of dropping the color.
    """
    normalized = value.strip().lower()
    if normalized in {"", "transparent", "rgba(0, 0, 0, 0)"}:
        return "transparent"
    match = _RGB_RE.fullmatch(normalized)
    if match is not None and match.group(4) is not None:
        try:
            if float(match.group(4)) == 0:
                return "transparent"
        except ValueError:
            pass
    return "supported" if _color(value) is not None else "unsupported"


def _edges(
    values: tuple[str, str, str, str],
    *,
    keep_zero: bool = False,
) -> float | dict[str, float] | None:
    parsed = tuple(_px(value) for value in values)
    if any(value is None for value in parsed):
        return None
    numbers = tuple(value for value in parsed if value is not None)
    if not any(numbers) and not keep_zero:
        return None
    if len(set(numbers)) == 1:
        return numbers[0]
    return dict(zip(("top", "right", "bottom", "left"), numbers, strict=True))


def _radii(
    style: BrowserComputedStyle,
    *,
    keep_zero: bool = False,
) -> float | dict[str, float] | None:
    values = tuple(_px(value) for value in (
        style.border_top_left_radius,
        style.border_top_right_radius,
        style.border_bottom_right_radius,
        style.border_bottom_left_radius,
    ))
    if any(value is None for value in values):
        return None
    numbers = tuple(value for value in values if value is not None)
    if not any(numbers) and not keep_zero:
        return None
    if len(set(numbers)) == 1:
        return numbers[0]
    return dict(zip(
        ("topLeft", "topRight", "bottomRight", "bottomLeft"),
        numbers,
        strict=True,
    ))


_BORDER_EDGE_NAMES = ("top", "right", "bottom", "left")
_BORDER_STYLE_NAMES = {
    "solid": "Solid",
    "dashed": "Dashed",
    "dotted": "Dotted",
}


def _screen_ir_border(
    style: BrowserComputedStyle,
) -> tuple[dict[str, object] | None, str | None]:
    """Reduce the four computed CSS borders to one Screen IR border value.

    Uniform borders keep the scalar form; borders that only paint some edges
    (hairline row separators, underline accents) use the per-edge objects that
    mirror ArkUI's EdgeWidths/EdgeColors/EdgeStyles. Only a painted edge whose
    color or line style ArkUI cannot express is reported as lossy.
    """
    widths = tuple(_px(value) for value in (
        style.border_top_width,
        style.border_right_width,
        style.border_bottom_width,
        style.border_left_width,
    ))
    colors = tuple(_color(value) for value in (
        style.border_top_color,
        style.border_right_color,
        style.border_bottom_color,
        style.border_left_color,
    ))
    css_styles = tuple(value.strip().lower() for value in (
        style.border_top_style,
        style.border_right_style,
        style.border_bottom_style,
        style.border_left_style,
    ))
    if any(value is None for value in widths):
        return None, None
    active = tuple(
        index for index, width in enumerate(widths)
        if width is not None and width > 0
    )
    if not active:
        return None, None
    for index in active:
        if css_styles[index] not in _BORDER_STYLE_NAMES:
            return None, f"border-style:{css_styles[index] or 'unknown'}"
        if colors[index] is None:
            return None, "border-color"
    edge_widths = {
        _BORDER_EDGE_NAMES[index]: widths[index] for index in active
    }
    edge_colors = {
        _BORDER_EDGE_NAMES[index]: colors[index] for index in active
    }
    edge_styles = {
        _BORDER_EDGE_NAMES[index]: _BORDER_STYLE_NAMES[css_styles[index]]
        for index in active
    }
    if len(active) == 4 and all(
        len(set(values.values())) == 1
        for values in (edge_widths, edge_colors, edge_styles)
    ):
        return {
            "width": widths[active[0]],
            "color": colors[active[0]],
            "style": edge_styles[_BORDER_EDGE_NAMES[active[0]]],
        }, None
    # Edges the browser painted identically still collapse to one scalar so
    # the generated ArkTS stays close to what a developer would write.
    color_values = set(edge_colors.values())
    style_values = set(edge_styles.values())
    return {
        "width": edge_widths,
        "color": (
            color_values.pop() if len(color_values) == 1 else edge_colors
        ),
        "style": (
            style_values.pop() if len(style_values) == 1 else edge_styles
        ),
    }, None


def _single_solid_border(
    style: BrowserComputedStyle,
) -> tuple[float, str, Literal["horizontal", "vertical"]] | None:
    """Return one active solid CSS border suitable for native Divider styles."""
    raw_widths = (
        style.border_top_width,
        style.border_right_width,
        style.border_bottom_width,
        style.border_left_width,
    )
    widths = tuple(_px(value) for value in raw_widths)
    if any(value is None for value in widths):
        return None
    active = [
        index for index, width in enumerate(widths)
        if width is not None and width > 0
    ]
    if len(active) != 1:
        return None
    index = active[0]
    colors = (
        style.border_top_color,
        style.border_right_color,
        style.border_bottom_color,
        style.border_left_color,
    )
    css_styles = (
        style.border_top_style,
        style.border_right_style,
        style.border_bottom_style,
        style.border_left_style,
    )
    color = _color(colors[index])
    if color is None or css_styles[index].strip().lower() != "solid":
        return None
    width = widths[index]
    if width is None:
        return None
    axis: Literal["horizontal", "vertical"] = (
        "horizontal" if index in {0, 2} else "vertical"
    )
    return width, color, axis


def _font_weight(value: str) -> int | str | None:
    normalized = value.strip().lower()
    if normalized.isdigit():
        parsed = int(normalized)
        return parsed if 1 <= parsed <= 1000 else None
    return {
        "lighter": "Lighter",
        "normal": "Normal",
        "medium": "Medium",
        "bold": "Bold",
        "bolder": "Bolder",
    }.get(normalized)


_GENERIC_FONT_FAMILIES = frozenset({
    "serif",
    "sans-serif",
    "monospace",
    "cursive",
    "fantasy",
    "system-ui",
    "ui-serif",
    "ui-sans-serif",
    "ui-monospace",
    "ui-rounded",
    "math",
    "emoji",
    "fangsong",
})

# Concrete emoji/symbol faces that stacks such as Tailwind's default append
# after their generic families. They only exist to rasterize emoji code
# points; picking one as the ArkUI ``fontFamily`` would typeset body text in
# an emoji font that HarmonyOS devices do not even ship.
_EMOJI_FALLBACK_FONT_FAMILIES = frozenset({
    "apple color emoji",
    "segoe ui emoji",
    "segoe ui symbol",
    "noto color emoji",
    "noto emoji",
    "android emoji",
    "emojione",
    "emojione color",
    "twemoji mozilla",
})


def _css_font_families(value: str) -> tuple[str, ...]:
    """Parse the useful subset of a computed CSS font-family list.

    ArkUI's ``fontFamily`` modifier accepts one family, not a serialized CSS
    fallback list. Computed values can retain quotes around names containing
    spaces, so split on unquoted commas and remove the CSS quoting before
    selecting a concrete family.
    """
    families: list[str] = []
    token: list[str] = []
    quote: str | None = None
    escaped = False
    for character in value.strip():
        if escaped:
            token.append(character)
            escaped = False
            continue
        if character == "\\":
            escaped = True
            continue
        if quote is not None:
            if character == quote:
                quote = None
            else:
                token.append(character)
            continue
        if character in {"'", '"'}:
            quote = character
        elif character == ",":
            family = "".join(token).strip()
            if family:
                families.append(family)
            token = []
        else:
            token.append(character)
    if escaped:
        token.append("\\")
    # An unterminated quote is malformed and must not become an ArkUI family.
    if quote is not None:
        return ()
    family = "".join(token).strip()
    if family:
        families.append(family)
    return tuple(families)


def _font_family(value: str) -> str | None:
    for family in _css_font_families(value):
        normalized = family.casefold()
        if normalized in _GENERIC_FONT_FAMILIES:
            continue
        if normalized in _EMOJI_FALLBACK_FONT_FAMILIES:
            continue
        if normalized in {"inherit", "initial", "revert", "revert-layer", "unset"}:
            continue
        if len(family) <= 200 and not any(ord(character) < 32 for character in family):
            return family
    # Let ArkUI use its native default when CSS only supplies generic or
    # emoji-fallback families.
    return None


def _finite_css_number(value: str) -> float | None:
    try:
        parsed = float(value.strip())
    except ValueError:
        return None
    if not math.isfinite(parsed) or abs(parsed) > 100_000:
        return None
    if abs(parsed) < 0.0001:
        return 0.0
    return round(parsed, 4)


def _is_zero_flex_basis(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized.endswith("px"):
        parsed = _px(normalized)
        return parsed == 0
    if normalized.endswith("%"):
        parsed = _finite_css_number(normalized[:-1])
        return parsed == 0
    return False


def _has_compatible_flex_shrink(value: str) -> bool:
    parsed = _finite_css_number(value)
    # CSS flex: 1 uses shrink=1. A zero basis also makes shrink=0 safe because
    # there is no positive flex base to remove before distributing free space.
    return parsed in {0, 1}


def _alignment(value: str) -> str | None:
    return {
        "flex-start": "Start",
        "start": "Start",
        "center": "Center",
        "flex-end": "End",
        "end": "End",
    }.get(value.strip().lower())


_MATRIX_TRANSFORM_RE = re.compile(r"^matrix\(([^()]*)\)$", re.IGNORECASE)
_MATRIX_3D_TRANSFORM_RE = re.compile(
    r"^matrix3d\(([^()]*)\)$", re.IGNORECASE,
)
_TRANSLATE_ONLY_RE = re.compile(
    r"^(?:translate(?:x|y|3d)?\([^()]*\)\s*)+$", re.IGNORECASE,
)


def _finite_transform_numbers(value: str, expected: int) -> tuple[float, ...] | None:
    parts = tuple(part.strip() for part in value.split(","))
    if len(parts) != expected:
        return None
    try:
        numbers = tuple(float(part) for part in parts)
    except ValueError:
        return None
    if not all(math.isfinite(number) for number in numbers):
        return None
    return numbers


def _is_translation_only_transform(value: str) -> bool:
    """Whether a computed transform changes position but not box geometry."""
    normalized = value.strip()
    matrix = _MATRIX_TRANSFORM_RE.fullmatch(normalized)
    if matrix is not None:
        numbers = _finite_transform_numbers(matrix.group(1), 6)
        return numbers is not None and all(math.isclose(left, right) for left, right in zip(
            numbers[:4], (1.0, 0.0, 0.0, 1.0), strict=True,
        ))
    matrix_3d = _MATRIX_3D_TRANSFORM_RE.fullmatch(normalized)
    if matrix_3d is not None:
        numbers = _finite_transform_numbers(matrix_3d.group(1), 16)
        if numbers is None:
            return False
        expected = (
            1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            numbers[12], numbers[13], numbers[14], 1.0,
        )
        return all(
            math.isclose(left, right)
            for left, right in zip(numbers, expected, strict=True)
        )
    # Tests and non-Chromium bridges may preserve the authored spelling.
    return _TRANSLATE_ONLY_RE.fullmatch(normalized) is not None


# Alignments equivalent to ArkUI List/Grid's only behaviour: entries pack
# from the main-axis start and the generated ListItem/GridItem stretches
# across the cross axis. Anything else moves content on device.
_PACKED_START_ALIGNMENTS = frozenset({
    "", "normal", "start", "flex-start", "stretch",
})


def _text_alignment(value: str) -> str | None:
    return {
        "left": "Start",
        "start": "Start",
        "center": "Center",
        "right": "End",
        "end": "End",
    }.get(value.strip().lower())


def _has_intrinsic_single_line_width(snapshot: BrowserNodeSnapshot) -> bool:
    """Whether the browser width is text measurement, not a layout constraint.

    A browser can lay out an auto-sized text leaf to the exact glyph advance.
    Reusing that platform-specific measurement as a hard ArkUI width is unsafe:
    another font rasterizer may need a few more pixels and wrap the last glyph.
    The snapshot bridge records both the authored/computed sizing mode and the
    single-line DOM Range width so we only discard widths proven intrinsic.
    """
    if (
        snapshot.width_sizing != "auto"
        or snapshot.single_line_text_width is None
        or snapshot.computed.transform not in {"", "none"}
    ):
        return False
    horizontal_insets = tuple(_px(value) for value in (
        snapshot.computed.padding_left,
        snapshot.computed.padding_right,
        snapshot.computed.border_left_width,
        snapshot.computed.border_right_width,
    ))
    if any(value is None for value in horizontal_insets):
        return False
    expected_outer_width = snapshot.single_line_text_width + sum(
        value for value in horizontal_insets if value is not None
    )
    return math.isclose(
        snapshot.bbox[2], expected_outer_width, rel_tol=0, abs_tol=0.5
    )


def _track_size(value: float) -> str:
    rounded = round(value, 4)
    if rounded == int(rounded):
        return str(int(rounded))
    return f"{rounded:.4f}".rstrip("0").rstrip(".")


def _grid_track_template(
    value: str,
    *,
    available: float | None,
    gap: float,
) -> str | None:
    """Freeze used grid tracks (``"96px 240px"``) into an ArkUI template.

    ``getComputedStyle`` reports used track sizes, so authored ``fr``
    fractions are already resolved to pixels. Equal tracks round-trip
    losslessly through one ``1fr`` per track — but only while they fill the
    container's content box: ArkUI distributes fractions across the whole
    axis, so tracks the browser left short (``100px 100px`` in a wider grid)
    would silently stretch. Those, and unequal tracks, are frozen as the
    exact vp sizes the browser rendered.
    """
    tokens = value.strip().split()
    if not tokens:
        return None
    tracks = []
    for token in tokens:
        parsed = _px(token)
        if parsed is None or parsed < 0:
            return None
        tracks.append(parsed)
    if (
        available is not None
        and tracks[0] > 0
        and all(
            math.isclose(track, tracks[0], rel_tol=0, abs_tol=0.05)
            for track in tracks
        )
        and math.isclose(
            sum(tracks) + gap * (len(tracks) - 1),
            available,
            rel_tol=0,
            abs_tol=1,
        )
    ):
        return " ".join(["1fr"] * len(tracks))
    return " ".join(f"{_track_size(track)}vp" for track in tracks)


def _content_box_size(
    snapshot: BrowserNodeSnapshot,
) -> tuple[float | None, float | None]:
    """Return the CSS content-box size behind a captured border-box bbox."""
    style = snapshot.computed
    horizontal = tuple(_px(value) for value in (
        style.padding_left, style.padding_right,
        style.border_left_width, style.border_right_width,
    ))
    vertical = tuple(_px(value) for value in (
        style.padding_top, style.padding_bottom,
        style.border_top_width, style.border_bottom_width,
    ))
    width = (
        max(0.0, snapshot.bbox[2] - sum(
            inset for inset in horizontal if inset is not None
        ))
        if all(inset is not None for inset in horizontal) else None
    )
    height = (
        max(0.0, snapshot.bbox[3] - sum(
            inset for inset in vertical if inset is not None
        ))
        if all(inset is not None for inset in vertical) else None
    )
    return width, height


def browser_main_axis(
    snapshot: BrowserNodeSnapshot,
) -> Literal["row", "column"] | None:
    """Return the axis the browser laid this container's children along.

    Row/Column metadata is the model's claim about a node; the computed layout
    is the evidence. ``None`` marks a display mode ArkUI's single-axis
    containers cannot express at all, such as ``row-reverse`` or ``grid``.
    """
    display = snapshot.computed.display.strip().lower()
    if display in {"flex", "inline-flex"}:
        direction = snapshot.computed.flex_direction.strip().lower()
        # Reversed and unknown directions are not a plain Row/Column.
        if direction == "row":
            return "row"
        if direction == "column":
            return "column"
        return None
    if display in _NORMAL_FLOW_DISPLAYS:
        # Normal flow stacks block-level children top to bottom, which is
        # exactly what a Column or a vertical List does.
        return "column"
    return None


def screen_ir_styles(
    component_name: str,
    snapshot: BrowserNodeSnapshot,
    *,
    background_image_source: str | None = None,
    parent_direction: Literal["row", "column"] | None = None,
    flex_item_parent_verified: bool = False,
    flex_container_scrolls_main_axis: bool = False,
    button_renders_direct_label: bool = False,
    baseline_alignment_is_baked: bool = False,
) -> tuple[dict[str, object], tuple[str, ...]]:
    """Map only CSS values with a direct Screen IR v2 representation."""
    style = snapshot.computed
    result: dict[str, object] = {}
    lossy: list[str] = []

    if component_name != "Span":
        if (
            snapshot.bbox[2] > 0
            and not (
                component_name == "Text"
                and _has_intrinsic_single_line_width(snapshot)
            )
        ):
            result["width"] = round(snapshot.bbox[2], 4)
        if snapshot.bbox[3] > 0:
            result["height"] = round(snapshot.bbox[3], 4)
        flex_grow = _finite_css_number(style.flex_grow)
        if style.flex_grow.strip() and (flex_grow is None or flex_grow < 0):
            lossy.append(f"flex-grow:{style.flex_grow}")
        elif flex_grow is not None and flex_grow > 0:
            if not _is_zero_flex_basis(style.flex_basis):
                lossy.append(f"flex-basis:{style.flex_basis or 'unknown'}")
            elif not _has_compatible_flex_shrink(style.flex_shrink):
                lossy.append(f"flex-shrink:{style.flex_shrink or 'unknown'}")
            elif style.position.strip().lower() in {"absolute", "fixed"}:
                lossy.append(
                    "flex-grow:out-of-flow-position:"
                    f"{style.position.strip().lower()}"
                )
            elif parent_direction is None or not flex_item_parent_verified:
                lossy.append("flex-grow:unverified-flex-item")
            elif flex_container_scrolls_main_axis:
                # CSS floors a flexed item at its min-content size, so inside
                # a scroll area tall content still grows the scroll range.
                # ArkUI layoutWeight has no such floor: against a scroll
                # container it anchors the child to the viewport, collapsing
                # the page to exactly one screen and killing the scroll.
                # constraintSize carries both claims instead: the minimum
                # still fills a short viewport while taller content keeps
                # the frozen height and scrolls past it.
                result["minHeight"] = "100%"
            else:
                result["layoutWeight"] = flex_grow
                # The browser's flexed main-axis bbox is an outcome, not an
                # authored constraint. Keeping it together with layoutWeight
                # would make ArkUI add that size before distributing free room.
                result.pop(
                    "width" if parent_direction == "row" else "height", None
                )
        # ArkUI gives Button its own padding, corner radius and fill, so for
        # that component alone "zero" and "unspecified" are different claims
        # and every one of them has to be stated.
        states_platform_defaults = component_name in {
            "Button", "TextInput", "Search", "Checkbox", "Radio",
        }
        padding = _edges((
            style.padding_top, style.padding_right,
            style.padding_bottom, style.padding_left,
        ), keep_zero=states_platform_defaults)
        margin = _edges((
            style.margin_top, style.margin_right,
            style.margin_bottom, style.margin_left,
        ))
        if padding is not None:
            result["padding"] = padding
        if margin is not None:
            result["margin"] = margin
        background_color = _color(style.background_color)
        if background_color is not None:
            result["backgroundColor"] = background_color
        elif classify_css_color(style.background_color) == "unsupported":
            lossy.append(f"background-color:{style.background_color}")
        elif states_platform_defaults:
            result["backgroundColor"] = TRANSPARENT_COLOR
        divider_border = (
            _single_solid_border(style) if component_name == "Divider" else None
        )
        if divider_border is not None:
            border_width, border_color, border_axis = divider_border
            result["dividerColor"] = border_color
            result["dividerStrokeWidth"] = border_width
            result["dividerVertical"] = border_axis == "vertical"
        else:
            border, border_lossy = _screen_ir_border(style)
            if border is not None:
                result["border"] = border
            if border_lossy is not None:
                lossy.append(border_lossy)
        radii = _radii(style, keep_zero=states_platform_defaults)
        if radii is not None:
            result["borderRadius"] = radii
        try:
            opacity = float(style.opacity)
        except ValueError:
            opacity = 1.0
        if math.isfinite(opacity) and 0 <= opacity < 1:
            result["opacity"] = round(opacity, 4)
        if style.overflow_x in {"hidden", "clip"} or style.overflow_y in {
            "hidden", "clip",
        }:
            result["overflow"] = "hidden"
        if style.position == "absolute":
            result.update({
                "position": "absolute",
                "left": round(snapshot.bbox[0], 4),
                "top": round(snapshot.bbox[1], 4),
            })
        elif style.position in {"fixed", "sticky"}:
            lossy.append(f"position:{style.position}")

    if component_name == "List":
        # A Row or Column names its axis; a List carries it in listDirection
        # and ArkUI defaults that to Vertical. The frozen bbox cannot recover
        # the axis once the items have been stacked the other way, so the
        # browser's own main axis has to be exported.
        # A layout with no ArkUI axis is reported with node context by the
        # Screen IR adapter, exactly like a Row/Column metadata conflict.
        main_axis = browser_main_axis(snapshot)
        if main_axis is not None:
            result["listDirection"] = (
                "Horizontal" if main_axis == "row" else "Vertical"
            )

    if component_name in {"Row", "Column", "List"}:
        # ArkUI distributes `space` along the container's main axis, which for
        # a List is whichever axis listDirection selected.
        main_axis_is_row = (
            component_name == "Row"
            or result.get("listDirection") == "Horizontal"
        )
        gap = _px(style.column_gap if main_axis_is_row else style.row_gap)
        if gap is not None and gap > 0:
            result["space"] = gap

    if component_name == "Grid":
        columns_gap = _px(style.column_gap)
        rows_gap = _px(style.row_gap)
        content_width, content_height = _content_box_size(snapshot)
        for css_name, css_value, style_key, available, gap in (
            (
                "grid-template-columns", style.grid_template_columns,
                "columnsTemplate", content_width, columns_gap,
            ),
            (
                "grid-template-rows", style.grid_template_rows,
                "rowsTemplate", content_height, rows_gap,
            ),
        ):
            if css_value.strip().lower() in {"", "none"}:
                # No explicit axis template: ArkUI auto-sizes the implicit
                # tracks the same way the browser did, so nothing to state.
                continue
            template = _grid_track_template(
                css_value, available=available, gap=gap or 0.0,
            )
            if template is not None:
                result[style_key] = template
            else:
                lossy.append(f"{css_name}:{css_value}")
        if columns_gap is not None and columns_gap > 0:
            result["columnsGap"] = columns_gap
        if rows_gap is not None and rows_gap > 0:
            result["rowsGap"] = rows_gap

    if component_name in {"Row", "Column"}:
        justify = {
            "normal": "Start",
            "space-between": "SpaceBetween",
            "space-around": "SpaceAround",
        }.get(style.justify_content, _alignment(style.justify_content))
        # Computed ``normal`` behaves as ``stretch`` on a flex container:
        # auto-sized items fill the cross axis and definite-sized items sit at
        # its start. Every exported box carries its frozen browser size, so
        # stretched items already span the container and Start reproduces the
        # rendered placement exactly (omitting alignItems would not: ArkUI
        # centers the cross axis by default).
        align = {
            "normal": "Start",
            "stretch": "Start",
            **({"baseline": "Start"} if baseline_alignment_is_baked else {}),
        }.get(style.align_items, _alignment(style.align_items))
        if justify is not None:
            result["justifyContent"] = justify
        if align is not None:
            result["alignItems"] = align
        elif style.align_items:
            lossy.append(f"align-items:{style.align_items}")
        if justify is None and style.justify_content:
            lossy.append(f"justify-content:{style.justify_content}")
        # Row/Column metadata conflicts are blocking structural errors. The
        # Screen IR adapter validates them with node context before rendering;
        # they are deliberately not downgraded to lossy style warnings here.

    if component_name in {"List", "Grid"}:
        # ArkUI's List and Grid expose no justifyContent/alignItems modifiers,
        # so a browser distribution such as ``justify-content: center`` cannot
        # be reproduced: on device the entries pack from the start. Report the
        # difference instead of silently repositioning content. This stays
        # deliberately conservative: a distribution that happens to have no
        # visible effect (tracks or items already filling the axis) is still
        # reported, because the frozen geometry cannot prove that.
        for css_name, css_value in (
            ("justify-content", style.justify_content),
            ("align-items", style.align_items),
        ):
            if css_value.strip().lower() not in _PACKED_START_ALIGNMENTS:
                lossy.append(f"{css_name}:{css_value}")

    if component_name in {
        "Text", "Span", "Button", "SymbolGlyph", "TextInput", "Search",
    }:
        font_size = _px(style.font_size)
        font_color = _color(style.color)
        font_weight = _font_weight(style.font_weight)
        if font_size is not None:
            result["fontSize"] = font_size
        if font_color is not None:
            result["fontColor"] = font_color
        elif classify_css_color(style.color) == "unsupported":
            lossy.append(f"color:{style.color}")
        if font_weight is not None:
            result["fontWeight"] = font_weight
        if component_name != "SymbolGlyph" and style.font_family:
            font_family = _font_family(style.font_family)
            if font_family is not None:
                result["fontFamily"] = font_family

    if component_name == "Text":
        line_height = _px(style.line_height)
        text_align = _text_alignment(style.text_align)
        if line_height is not None:
            result["lineHeight"] = line_height
        if text_align is not None:
            result["textAlign"] = text_align
    elif component_name == "Button" and button_renders_direct_label:
        # API 22 ButtonAttribute exposes font properties, but not Text's
        # lineHeight/textAlign modifiers. Center is the native Button default;
        # other alignments and explicit CSS line boxes cannot be preserved.
        # Both properties only affect a label the Button itself renders: on a
        # button whose content is component children, CSS line-height and
        # text-align never reached the layout in the browser either.
        if style.line_height not in {"", "normal"}:
            lossy.append("button-line-height")
        if style.text_align not in {"", "center"}:
            lossy.append(f"button-text-align:{style.text_align}")

    if component_name == "Image":
        object_fit = {
            "cover": "Cover",
            "contain": "Contain",
            "fill": "Fill",
        }.get(style.object_fit)
        if object_fit is not None:
            result["objectFit"] = object_fit
        elif style.object_fit:
            lossy.append(f"object-fit:{style.object_fit}")

    if background_image_source is not None:
        result["backgroundImage"] = background_image_source
    elif style.background_image and style.background_image != "none":
        lossy.append("background-image")
    shadow, shadow_is_supported = _screen_ir_shadow(style.box_shadow)
    if shadow is not None:
        result["shadow"] = shadow
    elif not shadow_is_supported:
        lossy.append("box-shadow")
    if style.transform and style.transform != "none":
        # getBoundingClientRect already includes transforms.  For an absolute
        # node the adapter emits that rectangle as left/top, so a pure
        # translation is fully baked into the ArkUI position modifier.
        translation_is_baked = (
            style.position.strip().lower() == "absolute"
            and _is_translation_only_transform(style.transform)
        )
        if not translation_is_baked:
            lossy.append("transform")
    if style.filter and style.filter != "none":
        lossy.append("filter")
    if style.backdrop_filter and style.backdrop_filter != "none":
        lossy.append("backdrop-filter")
    if style.clip_path and style.clip_path != "none":
        lossy.append("clip-path")
    letter_spacing = _px(style.letter_spacing)
    if component_name in {"Text", "Span"}:
        if letter_spacing is not None and letter_spacing != 0:
            result["letterSpacing"] = letter_spacing
        elif letter_spacing is None and style.letter_spacing not in {"", "normal"}:
            lossy.append("letter-spacing")
    elif (
        component_name == "Button"
        and button_renders_direct_label
        and style.letter_spacing not in {"", "normal"}
        and letter_spacing != 0
    ):
        # ButtonAttribute has no letterSpacing modifier, so a tracked-out
        # direct label cannot be reproduced. On every other component the
        # computed value styles no text of its own: annotated Text/Span
        # descendants inherit and export it themselves.
        lossy.append("letter-spacing")
    if style.text_decoration_line not in {"", "none"}:
        lossy.append("text-decoration")
    if style.text_transform.strip().lower() not in {
        "", "none", "uppercase", "lowercase",
    }:
        # uppercase/lowercase are baked into the exported text content by the
        # Screen IR adapter; only transforms plain casing cannot reproduce
        # (capitalize, full-width, ...) remain lossy.
        lossy.append("text-transform")
    if style.font_style not in {"", "normal"}:
        lossy.append("font-style")
    line_clamp = style.webkit_line_clamp.strip().lower()
    clamp_lines: int | None = None
    if line_clamp not in {"", "none", "auto"}:
        clamp_value = _finite_css_number(line_clamp)
        if (
            clamp_value is not None
            and clamp_value >= 1
            and clamp_value == int(clamp_value)
        ):
            clamp_lines = int(clamp_value)
    is_nowrap = style.white_space.strip().lower() == "nowrap"
    is_ellipsis = style.text_overflow.strip().lower() == "ellipsis"
    if component_name == "Text":
        max_lines = 1 if is_nowrap else clamp_lines
        if max_lines is not None:
            result["maxLines"] = max_lines
            # -webkit-line-clamp always truncates with an ellipsis in the
            # browser; bare nowrap clips, which is also ArkUI's default.
            if clamp_lines is not None or is_ellipsis:
                result["textOverflow"] = "Ellipsis"
        # ellipsis without a line limit paints nothing in the browser either,
        # so it is not a loss.
    text_maps_line_limits = component_name == "Text"
    if style.white_space not in {"", "normal"} and not (
        text_maps_line_limits and is_nowrap
    ):
        lossy.append(f"white-space:{style.white_space}")
    if style.text_overflow not in {"", "clip"} and not (
        text_maps_line_limits and is_ellipsis
    ):
        lossy.append(f"text-overflow:{style.text_overflow}")
    if line_clamp not in {"", "none", "auto"} and not (
        text_maps_line_limits and clamp_lines is not None
    ):
        lossy.append("line-clamp")
    if style.pseudo_before_content not in {"", "none", "normal", '""'}:
        lossy.append("pseudo-element:before")
    if style.pseudo_after_content not in {"", "none", "normal", '""'}:
        lossy.append("pseudo-element:after")
    return result, tuple(dict.fromkeys(lossy))


__all__ = [
    "BrowserAssetSnapshot",
    "BrowserAssetUse",
    "BrowserComputedStyle",
    "BrowserNodeSnapshot",
    "BrowserSnapshot",
    "MAX_BROWSER_ASSET_BYTES",
    "MAX_BROWSER_ASSET_TOTAL_BYTES",
    "classify_css_color",
    "is_opaque_css_color",
    "normalize_css_color",
    "screen_ir_styles",
]
