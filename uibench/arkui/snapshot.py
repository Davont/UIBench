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
    nodes: list[BrowserNodeSnapshot] = Field(max_length=10_000)
    assets: list[BrowserAssetSnapshot] = Field(default_factory=list, max_length=32)

    @model_validator(mode="after")
    def references_are_bounded_and_unique(self) -> "BrowserSnapshot":
        node_ids = [node.node_id for node in self.nodes]
        if len(set(node_ids)) != len(node_ids):
            raise ValueError("browser snapshot nodeId values must be unique")
        known_node_ids = set(node_ids)
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


def _edges(values: tuple[str, str, str, str]) -> float | dict[str, float] | None:
    parsed = tuple(_px(value) for value in values)
    if any(value is None for value in parsed):
        return None
    numbers = tuple(value for value in parsed if value is not None)
    if not any(numbers):
        return None
    if len(set(numbers)) == 1:
        return numbers[0]
    return dict(zip(("top", "right", "bottom", "left"), numbers, strict=True))


def _radii(style: BrowserComputedStyle) -> float | dict[str, float] | None:
    values = tuple(_px(value) for value in (
        style.border_top_left_radius,
        style.border_top_right_radius,
        style.border_bottom_right_radius,
        style.border_bottom_left_radius,
    ))
    if any(value is None for value in values):
        return None
    numbers = tuple(value for value in values if value is not None)
    if not any(numbers):
        return None
    if len(set(numbers)) == 1:
        return numbers[0]
    return dict(zip(
        ("topLeft", "topRight", "bottomRight", "bottomLeft"),
        numbers,
        strict=True,
    ))


def _uniform_border(
    style: BrowserComputedStyle,
) -> tuple[dict[str, object] | None, bool]:
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
    css_styles = tuple(value.lower() for value in (
        style.border_top_style,
        style.border_right_style,
        style.border_bottom_style,
        style.border_left_style,
    ))
    if any(value is None for value in widths):
        return None, False
    if not any(value for value in widths if value is not None):
        return None, False
    if len(set(widths)) != 1 or len(set(colors)) != 1 or len(set(css_styles)) != 1:
        return None, True
    width = widths[0]
    color = colors[0]
    border_style = {
        "solid": "Solid",
        "dashed": "Dashed",
        "dotted": "Dotted",
    }.get(css_styles[0])
    if width is None or color is None or border_style is None:
        return None, True
    return {"width": width, "color": color, "style": border_style}, False


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


def _alignment(value: str) -> str | None:
    return {
        "flex-start": "Start",
        "start": "Start",
        "center": "Center",
        "flex-end": "End",
        "end": "End",
    }.get(value.strip().lower())


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


def screen_ir_styles(
    component_name: str,
    snapshot: BrowserNodeSnapshot,
    *,
    background_image_source: str | None = None,
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
        padding = _edges((
            style.padding_top, style.padding_right,
            style.padding_bottom, style.padding_left,
        ))
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
        border, border_lossy = _uniform_border(style)
        if border is not None:
            result["border"] = border
        if border_lossy:
            lossy.append("non-uniform-border")
        radii = _radii(style)
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

    if component_name in {"Row", "Column"}:
        gap_value = style.column_gap if component_name == "Row" else style.row_gap
        gap = _px(gap_value)
        if gap is not None and gap > 0:
            result["space"] = gap
        justify = {
            "normal": "Start",
            "space-between": "SpaceBetween",
            "space-around": "SpaceAround",
        }.get(style.justify_content, _alignment(style.justify_content))
        align = _alignment(style.align_items)
        if justify is not None:
            result["justifyContent"] = justify
        if align is not None:
            result["alignItems"] = align
        elif style.align_items:
            lossy.append(f"align-items:{style.align_items}")
        if justify is None and style.justify_content:
            lossy.append(f"justify-content:{style.justify_content}")
        expected_direction = "row" if component_name == "Row" else "column"
        if style.display not in {"flex", "inline-flex"}:
            lossy.append(f"display:{style.display or 'unknown'}")
        elif style.flex_direction != expected_direction:
            lossy.append(f"flex-direction:{style.flex_direction or 'unknown'}")

    if component_name in {"Text", "Span", "Button", "SymbolGlyph"}:
        font_size = _px(style.font_size)
        font_color = _color(style.color)
        font_weight = _font_weight(style.font_weight)
        if font_size is not None:
            result["fontSize"] = font_size
        if font_color is not None:
            result["fontColor"] = font_color
        if font_weight is not None:
            result["fontWeight"] = font_weight
        if component_name != "SymbolGlyph" and style.font_family:
            result["fontFamily"] = style.font_family

    if component_name == "Text":
        line_height = _px(style.line_height)
        text_align = _text_alignment(style.text_align)
        if line_height is not None:
            result["lineHeight"] = line_height
        if text_align is not None:
            result["textAlign"] = text_align
    elif component_name == "Button":
        # API 22 ButtonAttribute exposes font properties, but not Text's
        # lineHeight/textAlign modifiers. Center is the native Button default;
        # other alignments and explicit CSS line boxes cannot be preserved.
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
    if style.box_shadow and style.box_shadow != "none":
        lossy.append("box-shadow")
    if style.transform and style.transform != "none":
        lossy.append("transform")
    if style.filter and style.filter != "none":
        lossy.append("filter")
    if style.backdrop_filter and style.backdrop_filter != "none":
        lossy.append("backdrop-filter")
    if style.clip_path and style.clip_path != "none":
        lossy.append("clip-path")
    if style.letter_spacing not in {"", "normal", "0px"}:
        lossy.append("letter-spacing")
    if style.text_decoration_line not in {"", "none"}:
        lossy.append("text-decoration")
    if style.text_transform not in {"", "none"}:
        lossy.append("text-transform")
    if style.font_style not in {"", "normal"}:
        lossy.append("font-style")
    if style.white_space not in {"", "normal"}:
        lossy.append(f"white-space:{style.white_space}")
    if style.text_overflow not in {"", "clip"}:
        lossy.append(f"text-overflow:{style.text_overflow}")
    if style.webkit_line_clamp not in {"", "none", "auto"}:
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
    "screen_ir_styles",
]
