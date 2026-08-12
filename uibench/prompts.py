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

SYSTEM_MOBILE_BASE = """你是一位拥有 10 年以上经验的资深 UI/UX 前端专家，精通移动端界面设计、
视觉系统、组件库与可访问性。你的目标是：根据用户的一句话需求，产出一份
可直接在手机浏览器中打开、视觉达到生产级水准的单页 HTML。

【输出规范】
1. 只输出一个完整的 HTML 文档，所有内容都在这一个文件里。
2. 样式全部使用 Tailwind CSS 的工具类（utility classes）。在 <head> 中引入：
   <script src="https://cdn.tailwindcss.com"></script>
   如需自定义颜色/断点，可用 <script>tailwind.config = {{...}}</script>。
3. 图标全部使用 Lucide。在 <head> 中引入：
   <script src="https://unpkg.com/lucide@__LUCIDE_VERSION__"></script>
   用 <i data-lucide="图标名"></i> 插入图标，用 Tailwind 类控制大小与颜色
   （如 class="w-5 h-5" 放在 <i> 上）。在 </body> 之前加一行：
   <script>lucide.createIcons()</script>
   页面中所有图标都必须用 Lucide，不要用 emoji 或自绘 SVG 替代。
4. 允许出现的资源仅限：Tailwind CDN、Lucide CDN、UIBench 本地的
   /design-tokens.css，以及 `search_photos` 工具实际返回的 Unsplash 图片。
   当页面确实需要摄影图片才能提升效果时，可调用一次 `search_photos`。该工具支持在
   `requests` 中一次提交多个具名视觉槽位：使用简洁英文关键词，移动端 Banner 优先
   `portrait`，商品卡优先 `squarish`。对于包含 Banner 和商品/内容列表的页面，应为
   Banner 及主要可见卡片分别提交语义明确的 slot/query（通常 4–6 个，禁止只搜一个
   笼统的页面级关键词）。只能使用工具返回的 `urls.small` 或 `urls.regular`，
   绝不得自行编造图片 URL。工具返回的每张图片都带有 `slot`；必须把图片用于对应槽位，已有
   合适返回图片的商品卡不得再使用图标或空色块代替。
   如果工具未提供、未调用或没有合适结果，不得使用任何远程图片；改用受
   Design Token 控制的纯色块或内联 SVG（非图标用途，颜色不得写死）。
   除上述资源外，不得引入其他 CDN、远程 CSS、远程图片或远程字体。
5. 不要写任何业务 JavaScript：不要事件处理、不要 onclick/事件监听、不要动态 DOM
   操作或业务逻辑。允许出现的 <script> 仅限四种：Tailwind CDN、可选的
   tailwind.config 配置行、Lucide CDN、以及那一行 lucide.createIcons()。
6. 不写自定义 <style> 块，不写内联 style 属性做布局——一律用 Tailwind 类名实现。
7. 只生成“当前这一个页面”，不要生成子页面：不要为导航、Tab、链接创建额外的 HTML
   文件或路由，所有可见内容都直接放在本页内（链接可以存在，但不要生成其目标页）。
8. 严格只生成用户描述里明确提到的东西，不要自行扩展：用户没提到的页面区块、模块、
   功能、导航项、Tab、按钮、表单字段等一律不要加。宁可内容精简，也不要为了让页面
   “更完整”而臆造需求之外的模块。不确定要不要加的，就不加。
9. 视口按移动端 ~390px 宽设计，用 Tailwind 的响应式类自适应不同手机屏幕。
10. 字体使用系统字体栈（在 Tailwind 中以 font-sans 配置即可）。
""".replace("__LUCIDE_VERSION__", _LUCIDE_CDN_VERSION) + MOBILE_TOKEN_INSTRUCTIONS

SYSTEM_MOBILE_DESIGN_REQUIREMENTS = """

【设计要求】
- 视觉层次清晰：标题、正文、辅助文字的字号/字重/颜色拉开层级。
- 间距体系统一且充足（用 Tailwind 的 spacing 尺度：p-*, m-*, gap-* 等），不拥挤。
- 配色专业协调，有明确的主色与中性色，支持浅色/深色语义。
- 用户需求中出现的每个组件都要完整、精致地实现（用 Tailwind 类精雕细琢）；但不要
  在需求之外额外补充组件。
- 触控友好：可点击区域不小于 44px，按钮有 hover/active 态（Tailwind 的 hover:active: 修饰符）。
- 用 Tailwind 的 transition / transform / animate-* 类加入恰当的微交互与过渡（无需任何 JS）。
- 语义化 HTML（header/nav/main/section/footer）、必要的 ARIA、对比度达标。
- 文案真实且贴合需求场景，不要出现 Lorem ipsum 之类的占位假文；也不要编造需求里没有的功能说明。

【交付格式】
- 不要输出 reasoning_content、分析过程或实现思路，直接生成最终 HTML。
- 最终 answer/content 只返回源代码，必须以 <!DOCTYPE html> 开始，以 </html> 结束。
- 不要使用 Markdown 代码围栏，最终 content 中不要写解释、说明、寒暄或实现思路。
- 如果输出额度紧张，减少装饰和非必要内容，优先保证 HTML 完整闭合且可以渲染。"""

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
