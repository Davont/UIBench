"""System prompts for UI generation.

The mobile prompt lives here; PC-mode generation (system prompt with the
design-system tokens, plus the Babel classic-runtime injector) lives in
``uibench.pc``.
"""
from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

from uibench.arkui import MOBILE_ARKUI_METADATA_INSTRUCTIONS
from uibench.arkui.symbols import pinned_lucide_version
from uibench.design_tokens import MOBILE_TOKEN_INSTRUCTIONS
from uibench.pc import PC_GENERATION_PROMPT

# The icon vocabulary is audited against one frozen Lucide catalogue, so the
# pages must load exactly that version instead of whatever `latest` means on
# the day the page is rendered.
_LUCIDE_CDN_VERSION = pinned_lucide_version()

SYSTEM_MOBILE_BASE = """你是移动端 UI/UX 前端专家。根据需求生成生产级、约 390px 宽的单页 HTML。

【硬性输出】
- 只返回一个完整 HTML 文档；从 <!DOCTYPE html> 开始，到 </html> 结束，不要使用 Markdown 代码围栏或说明。
- 只实现用户明确提出的当前页面；不臆造模块、功能、字段、导航、Tab、路由或子页面。
- 布局、尺寸、定位、响应式、排版和主题外观统一使用 Tailwind。禁止自定义 <style>
  和用于布局的内联 style。
- <head> 引入 <script src="https://cdn.tailwindcss.com"></script>，以及：
  <link rel="stylesheet" href="/hm-fonts.css">
  <script src="https://unpkg.com/lucide@__LUCIDE_VERSION__"></script>
  操作与系统图标只用 `<i data-lucide="名称">`，禁止 emoji/自绘 SVG；应用品牌图标仅使用
  UIBench 随当前需求提供的本地 PNG 目录；</body> 前调用 `<script>lucide.createIcons()</script>`。
- 禁止业务 JavaScript、事件处理和动态 DOM。script 仅允许 Tailwind、Lucide 与
  `lucide.createIcons()`；Tailwind Theme 由 UIBench 注入，不要输出 `tailwind.config`。
- 外部资源仅限上述 CDN、本地 `/design-tokens.css`、`/hm-fonts.css`、UIBench 提供的
  `/assets/app-icons/*.png` 和图片工具返回内容。
- 需要摄影图时，`search_photos` 最多调用一次：一次提交具名英文 slot/query；Banner 用
  portrait，卡片用 squarish。仅使用对应 slot 返回的 `urls.small|regular`，绝不得自行编造
  图片 URL。工具无结果时用 token 色块或非图标内联 SVG，不得引用其他远程图片。
- 使用语义 HTML、必要 ARIA、系统字体和移动端响应式布局。
""".replace("__LUCIDE_VERSION__", _LUCIDE_CDN_VERSION) + MOBILE_TOKEN_INSTRUCTIONS

SYSTEM_MOBILE_DESIGN_REQUIREMENTS = """

【设计与交付】
- 用字号、字重、语义色和统一间距建立清晰层级；文案真实，不用 Lorem ipsum。
- 可点击区域至少 44px；交互只用颜色/透明度过渡。不要用 transform、animate-*、阴影或
  额外 DOM 手绘原生控件。
- 重复结构逐项写完整，禁止“其余同上”等省略。额度不足时先删装饰，保证 HTML 完整闭合。"""

SYSTEM_MOBILE = (
    SYSTEM_MOBILE_BASE
    + MOBILE_ARKUI_METADATA_INSTRUCTIONS
    + SYSTEM_MOBILE_DESIGN_REQUIREMENTS
)
SYSTEM_MOBILE_WITHOUT_ARKUI = (
    SYSTEM_MOBILE_BASE + SYSTEM_MOBILE_DESIGN_REQUIREMENTS
)

MOBILE_GENERATION_PROMPT = ChatPromptTemplate(
    messages=[
        ("system", SYSTEM_MOBILE),
        ("human", "需求：{prompt}"),
    ],
)

MOBILE_GENERATION_PROMPT_WITHOUT_ARKUI = ChatPromptTemplate(
    messages=[
        ("system", SYSTEM_MOBILE_WITHOUT_ARKUI),
        ("human", "需求：{prompt}"),
    ],
)


def prompt_for(
    mode: str,
    *,
    arkui_export_enabled: bool = False,
) -> ChatPromptTemplate:
    """Pick the generation prompt for a given mode."""
    if mode == "pc":
        return PC_GENERATION_PROMPT
    return (
        MOBILE_GENERATION_PROMPT
        if arkui_export_enabled
        else MOBILE_GENERATION_PROMPT_WITHOUT_ARKUI
    )
