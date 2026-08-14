"""Built-in application icons for generated UI previews and exports.

Photo search is intentionally the wrong source for application logos: a
curated photo library can return a phone or a generic icon grid, but it cannot
provide one stable asset for each application label.  This module owns a
small, local catalogue and exposes only the entries relevant to the current
request to keep the model prompt compact.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from html import escape, unescape
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_ICON_DIR = PROJECT_ROOT / "assets" / "app-icons"
APP_ICON_URL_PREFIX = "/assets/app-icons/"


@dataclass(frozen=True)
class AppIcon:
    slug: str
    name: str
    aliases: tuple[str, ...]
    generic_only: bool = False

    @property
    def url(self) -> str:
        return f"{APP_ICON_URL_PREFIX}{self.slug}.png"


APP_ICONS = (
    AppIcon("wechat", "微信", ("微信", "wechat", "weixin")),
    AppIcon("alipay", "支付宝", ("支付宝", "alipay")),
    AppIcon("qq", "QQ", ("腾讯qq", "qq")),
    AppIcon("douyin", "抖音", ("抖音", "douyin", "tiktok")),
    AppIcon("taobao", "淘宝", ("淘宝", "taobao")),
    AppIcon("meituan", "美团", ("美团", "meituan")),
    AppIcon("xiaohongshu", "小红书", ("小红书", "rednote", "xiaohongshu")),
    AppIcon("bilibili", "哔哩哔哩", ("哔哩哔哩", "b站", "bilibili")),
    AppIcon("camera", "相机", ("相机", "camera"), generic_only=True),
    AppIcon("maps", "地图", ("地图", "maps"), generic_only=True),
    AppIcon("photos", "相册", ("相册", "photos", "gallery"), generic_only=True),
    AppIcon("contacts", "通讯录", ("通讯录", "contacts"), generic_only=True),
)
APP_ICON_BY_SLUG = {icon.slug: icon for icon in APP_ICONS}

_GENERIC_APP_ICON_RE = re.compile(
    r"应用(?:程序)?(?:图标|logo)|常用应用|品牌(?:图标|logo)|"
    r"app\s*(?:icon|logo)s?|brand\s*(?:icon|logo)s?",
    re.IGNORECASE,
)
_APP_IMAGE_NODE_RE = re.compile(
    r"(?:^|[._-])(?:apps?|icons?|logos?)(?:[._-]|$)|应用图标",
    re.IGNORECASE,
)
_IMG_TAG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE | re.DOTALL)
_TAG_RE = re.compile(r"<[^>]+>", re.DOTALL)
_START_TAG_RE = re.compile(
    r"<(?P<tag>[a-z][a-z0-9:-]*)\b[^>]*>",
    re.IGNORECASE | re.DOTALL,
)
_HTML_TAG_RE = re.compile(
    r"<(?P<closing>/)?(?P<tag>[a-z][a-z0-9:-]*)\b[^>]*>",
    re.IGNORECASE | re.DOTALL,
)
_VOID_TAGS = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
})


def _mentions(text: str, alias: str) -> bool:
    if not alias.isascii() or not alias.isalnum():
        return alias.casefold() in text.casefold()
    return re.search(
        rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])",
        text,
        re.IGNORECASE,
    ) is not None


def app_icons_for_prompt(prompt_text: str) -> tuple[AppIcon, ...]:
    """Return explicit app matches, or the compact default catalogue."""
    explicit = tuple(
        icon
        for icon in APP_ICONS
        if not icon.generic_only
        and any(_mentions(prompt_text, alias) for alias in icon.aliases)
    )
    if _GENERIC_APP_ICON_RE.search(prompt_text):
        return APP_ICONS
    return explicit


def app_icon_catalog_instruction(prompt_text: str) -> str:
    """Build the request-local asset note appended to model messages."""
    icons = app_icons_for_prompt(prompt_text)
    if not icons:
        return ""
    catalog = "；".join(f"{icon.name}={icon.url}" for icon in icons)
    return (
        "UIBench 内置应用图标（本地资源，可直接用于 <img src>）："
        f"{catalog}。应用名称与资源必须一一对应，不得把同一图片复用给不同应用；"
        "同一区域展示 3 个及以上应用图标时，使用四列 grid：父节点标注 "
        "data-component=\"grid\" 并使用 grid grid-cols-4，子节点标注 "
        "data-component=\"grid-item\"；单个图标内部保持 Logo 在上、名称在下，"
        "不要把图标集合的父节点写成 flex-col。"
        "不要用 search_photos 搜索应用图标。未列出的应用使用 Lucide 或 token 色块占位，"
        "不得编造其他 Logo URL。"
    )


def _attribute(tag: str, name: str) -> str:
    match = re.search(
        rf"\b{re.escape(name)}\s*=\s*([\"'])(.*?)\1",
        tag,
        re.IGNORECASE | re.DOTALL,
    )
    return unescape(match.group(2)).strip() if match else ""


def _set_attribute(tag: str, name: str, value: str) -> str:
    replacement = f'{name}="{escape(value, quote=True)}"'
    pattern = re.compile(
        rf"\b{re.escape(name)}\s*=\s*([\"']).*?\1",
        re.IGNORECASE | re.DOTALL,
    )
    if pattern.search(tag):
        return pattern.sub(replacement, tag, count=1)
    stripped = tag.rstrip()
    closing = "/>" if stripped.endswith("/>") else ">"
    body = stripped[:-len(closing)].rstrip()
    return body + " " + replacement + closing


def _app_from_context(text: str) -> AppIcon | None:
    matches = [
        icon
        for icon in APP_ICONS
        if any(_mentions(text, alias) for alias in icon.aliases)
    ]
    return matches[0] if len(matches) == 1 else None


def _class_tokens(tag: str) -> list[str]:
    return _attribute(tag, "class").split()


def _set_class_tokens(tag: str, tokens: list[str]) -> str:
    unique: list[str] = []
    for token in tokens:
        if token and token not in unique:
            unique.append(token)
    return _set_attribute(tag, "class", " ".join(unique))


def _matching_element_close(
    html: str,
    *,
    tag_name: str,
    start: int,
) -> tuple[int, int] | None:
    """Return the matching close-tag span for one ordinary HTML element."""
    tag_re = re.compile(
        rf"</?{re.escape(tag_name)}\b[^>]*>",
        re.IGNORECASE | re.DOTALL,
    )
    depth = 0
    for match in tag_re.finditer(html, start):
        token = match.group(0)
        if token.startswith("</"):
            depth -= 1
            if depth == 0:
                return match.start(), match.end()
            continue
        if not token.rstrip().endswith("/>"):
            depth += 1
    return None


def _direct_child_ranges(
    html: str,
    *,
    body_start: int,
    body_end: int,
) -> list[tuple[int, int, int]]:
    """Return (start-tag start, start-tag end, element end) for direct children."""
    children: list[tuple[int, int, int]] = []
    stack: list[str] = []
    child_start: int | None = None
    child_start_end: int | None = None
    for match in _HTML_TAG_RE.finditer(html, body_start, body_end):
        tag_name = match.group("tag").casefold()
        if match.group("closing"):
            if not stack:
                continue
            if stack[-1] == tag_name:
                stack.pop()
            else:
                # Complete generated HTML is expected to be balanced. Avoid a
                # speculative layout rewrite when the local subtree is not.
                return []
            if not stack and child_start is not None and child_start_end is not None:
                children.append((child_start, child_start_end, match.end()))
                child_start = None
                child_start_end = None
            continue

        token = match.group(0)
        is_void = tag_name in _VOID_TAGS or token.rstrip().endswith("/>")
        if not stack:
            child_start = match.start()
            child_start_end = match.end()
        if is_void:
            if not stack and child_start is not None and child_start_end is not None:
                children.append((child_start, child_start_end, match.end()))
                child_start = None
                child_start_end = None
            continue
        stack.append(tag_name)
    if stack:
        return []
    return children


def _is_app_icon_tile(html: str, child: tuple[int, int, int]) -> bool:
    start, start_end, end = child
    start_tag = html[start:start_end]
    classes = set(_class_tokens(start_tag))
    if _attribute(start_tag, "data-component").casefold() != "list-item":
        return False
    if not {"flex", "flex-col", "items-center"}.issubset(classes):
        return False
    content = html[start_end:end]
    has_builtin_icon = re.search(
        r'<img\b[^>]*\bsrc\s*=\s*(["\'])/assets/app-icons/'
        r'[a-z0-9-]+\.png\1',
        content,
        re.IGNORECASE | re.DOTALL,
    ) is not None
    has_label = re.search(
        r'<(?:span|p)\b[^>]*\bdata-component\s*=\s*(["\'])text\1',
        content,
        re.IGNORECASE | re.DOTALL,
    ) is not None
    return has_builtin_icon and has_label


def repair_builtin_app_icon_layout(html: str) -> str:
    """Turn an accidental vertical app-icon list into a four-column grid.

    The signature is deliberately narrow: an explicit vertical flex list,
    at least three direct list-items, and every item must be a centered
    built-in app icon tile with a text label. Regular application setting rows
    remain lists because their items use a horizontal layout.
    """
    replacements: list[tuple[int, int, str]] = []
    occupied_until = -1
    for match in _START_TAG_RE.finditer(html):
        if match.start() < occupied_until:
            continue
        parent_tag = match.group(0)
        if _attribute(parent_tag, "data-component").casefold() != "list":
            continue
        parent_classes = _class_tokens(parent_tag)
        if "flex" not in parent_classes or "flex-col" not in parent_classes:
            continue
        close = _matching_element_close(
            html,
            tag_name=match.group("tag"),
            start=match.start(),
        )
        if close is None:
            continue
        close_start, close_end = close
        children = _direct_child_ranges(
            html,
            body_start=match.end(),
            body_end=close_start,
        )
        if len(children) < 3 or not all(
            _is_app_icon_tile(html, child) for child in children
        ):
            continue

        grid_classes = [
            "grid",
            "grid-cols-4",
            *(token for token in parent_classes if token not in {"flex", "flex-col"}),
        ]
        repaired_parent = _set_attribute(parent_tag, "data-component", "grid")
        repaired_parent = _set_class_tokens(repaired_parent, grid_classes)
        replacements.append((match.start(), match.end(), repaired_parent))
        for child_start, child_start_end, _ in children:
            child_tag = html[child_start:child_start_end]
            repaired_child = _set_attribute(
                child_tag,
                "data-component",
                "grid-item",
            )
            replacements.append((child_start, child_start_end, repaired_child))
        occupied_until = close_end

    for start, end, replacement in reversed(replacements):
        html = html[:start] + replacement + html[end:]
    return html


def repair_builtin_app_icon_bindings(html: str) -> str:
    """Bind known app-label images to their matching built-in asset.

    Models sometimes place one broad photo into every item of an application
    icon row.  The repair is deliberately narrow: the image must look like an
    app/icon node (or carry an explicit app name in ``alt``), and exactly one
    known app name must occur in its tag plus the following short label window.
    """
    replacements: list[tuple[int, int, str]] = []
    for match in _IMG_TAG_RE.finditer(html):
        tag = match.group(0)
        node_id = _attribute(tag, "data-node-id")
        alt = _attribute(tag, "alt")
        tail = html[match.end():match.end() + 320]
        item_end = re.search(r"</(?:div|li|button)\s*>", tail, re.IGNORECASE)
        if item_end:
            tail = tail[:item_end.end()]
        context = unescape(_TAG_RE.sub(" ", f"{alt} {tail}"))
        icon = _app_from_context(context)
        if icon is None:
            continue
        named_icon_alt = alt.casefold() in {
            f"{icon.name}图标".casefold(),
            f"{icon.name}logo".casefold(),
        }
        looks_like_app_icon = (
            _APP_IMAGE_NODE_RE.search(node_id) is not None
            or "应用图标" in alt
            or named_icon_alt
            or (
                not icon.generic_only
                and any(_mentions(alt, alias) for alias in icon.aliases)
            )
        )
        if not looks_like_app_icon:
            continue
        repaired = _set_attribute(tag, "src", icon.url)
        if not alt or alt == "应用图标":
            repaired = _set_attribute(repaired, "alt", f"{icon.name}图标")
        if repaired != tag:
            replacements.append((match.start(), match.end(), repaired))

    for start, end, replacement in reversed(replacements):
        html = html[:start] + replacement + html[end:]
    return repair_builtin_app_icon_layout(html)


__all__ = [
    "APP_ICONS",
    "APP_ICON_BY_SLUG",
    "APP_ICON_DIR",
    "APP_ICON_URL_PREFIX",
    "AppIcon",
    "app_icon_catalog_instruction",
    "app_icons_for_prompt",
    "repair_builtin_app_icon_bindings",
    "repair_builtin_app_icon_layout",
]
