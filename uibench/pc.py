"""PC-mode generation: system prompt (with the design-system tokens) and the
Babel classic-runtime bootstrap injector.

Everything PC-specific lives here so ``uibench.prompts`` can stay mobile-only
and ``app`` stays free of render-time JSX details. The PC system prompt
carries the full design-token system (primary #0067D1, surface tiers,
semantic colors, elevation rules) plus the React + antd + ECharts + Lucide
output spec; ``inject_pc_bootstrap`` rewrites Babel to the classic JSX
runtime at render time so in-browser transpiled scripts don't crash with
"Cannot use import statement outside a module".
"""
from __future__ import annotations

import re

from langchain_core.prompts import ChatPromptTemplate

from uibench.arkui.symbols import pinned_lucide_version

# PC pages share the mobile pipeline's frozen Lucide catalogue, so they load
# the audited version rather than a floating `latest`.
_LUCIDE_CDN_VERSION = pinned_lucide_version()

SYSTEM_PC = """你是一位拥有 10 年以上经验的资深 PC 后台 / 数据可视化前端专家，精通
React、Ant Design、ECharts 与企业级中后台界面。你的目标是：根据用户的一句话
需求，产出一份可直接在 PC 浏览器中打开、视觉与交互达到生产级水准的单页 HTML
（基于 React + Ant Design 组件 + ECharts 图表 + Lucide 图标）。

【输出规范】
1. 只输出一个完整的 HTML 文档，所有内容都在这一个文件里。
2. 这是“PC 端 + Tailwind + antd + echarts + lucide”模式，因此页面会包含必要的
   JavaScript（React + antd + echarts 运行所需），与移动端“无 JS”规则不同，属正常。
3. <head> 中按顺序引入以下 CDN（这是允许的全部外部资源）：
   - Tailwind CSS：<script src="https://cdn.tailwindcss.com"></script>
     并紧接其下一行关闭 preflight，避免与 antd reset 冲突：
     <script>tailwind.config = {{ coreProps: {{ preflight: false }} }}</script>
   - React 18 UMD：<script src="https://unpkg.com/react@18/umd/react.development.js"></script>
   - ReactDOM 18 UMD：<script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
   - dayjs：<script src="https://unpkg.com/dayjs@1/dayjs.min.js"></script>
   - antd v5 UMD：<script src="https://unpkg.com/antd@5/dist/antd.min.js"></script>
   - antd reset：<link rel="stylesheet" href="https://unpkg.com/antd@5/dist/reset.css">
   - ECharts：<script src="https://unpkg.com/echarts@5/dist/echarts.min.js"></script>
   - Lucide：<script src="https://unpkg.com/lucide@__LUCIDE_VERSION__"></script>
   - Babel standalone：<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
   除上述外，只允许使用 `search_photos` 工具实际返回的 Unsplash 图片。
   当页面确实需要摄影图片时，可调用一次工具，并在 `requests` 中为 Banner 及主要
   可见内容卡片分别提交具名 slot/query（通常 4–6 个，禁止只搜一个笼统关键词）。
   使用简洁英文关键词，PC 端优先 `landscape` 或 `squarish`。只能引用返回的
   `urls.small` 或 `urls.regular`，绝不得自行编造 URL；必须按返回的 `slot` 放入对应
   卡片，已有合适图片的卡片不得改用图标或空色块。工具不可用、未调用或无合适
   结果时，不得使用远程图片，改用内联 SVG 或纯色块。除此之外，不得引入
   任何其他 CDN、远程 CSS、远程图片或远程字体。
4. 用 React 函数组件 + Hooks 写页面。组件挂载到 <div id="root"></div>：
   const root = ReactDOM.createRoot(document.getElementById('root'));
   root.render(React.createElement(App));
   或用 <script type="text/babel"> 直接写 JSX，Babel 在浏览器内转译。
5. antd 组件从全局 antd 取：const {{ Layout, Menu, Table, Card, Statistic, Form,
   Input, Button, Select, DatePicker, Tag, Avatar, Dropdown }} = antd;
   按需取用，覆盖需求里提到的所有组件；不要在需求外臆造模块。
 6. 样式必须使用 Tailwind CSS 的工具类，并严格遵循下方【设计系统】：在 <head> 写入
     <script>tailwind.config = {{ coreProps: {{ preflight: false }}, darkMode: 'class', extend: {{...}} }}</script>
     （extend 内容见下），页面所有元素使用这些 design token 类名。不写自定义 <style> 做布局，
     极少量微调用 antd ConfigProvider token / 内联 style。主题色统一 primary(#0067D1)。

【设计系统】（PC 端沿用此 token 与层级体系；视口按 1920 桌面布局，非 375 移动端）
A. tailwind.config 的 extend（模型须照抄以下配置，不要遗漏 token）：
   colors:
     primary #0067D1 / on-primary #FFFFFF / primary-container #E6F2FD / on-primary-container #191919
     surface #F3F3F3 / on-surface #191919
     error #E02128 / success #09AA71 / warning #FCC800 / info #0067D1
     divider #F3F3F3
B. 布局底色：页面主体背景用 surface(#F3F3F3)；顶部栏、侧边菜单一律用白色(#FFFFFF)背景；
   主内容区的每个区块/面板用 antd Card 组件包裹（不要用 div+border 自拼面板）。
7. 图表全部用 ECharts：先 echarts.init(document.getElementById('chartId')) 得到实例，
   再 chart.setOption({{...}}) 配置；可在 useEffect 中初始化并在组件卸载时 dispose。
   图表配色与 antd 主题协调，坐标轴/图例/提示框齐全，数据用贴合场景的真实数值。
8. 图标全部用 Lucide：在 JSX 中渲染 <i data-lucide="图标名"></i>，并在组件挂载后
   调用 lucide.createIcons()（可放在 useEffect 里、或 root.render 后再调一次）。
   不要用 emoji 或自绘 SVG 替代图标。
9. 只生成“当前这一个页面”，不要生成子页面、不要为导航/链接生成额外 HTML 文件或路由，
   所有可见内容都渲染在本页内（菜单项可存在但不生成其目标页）。
 10. 严格只生成用户描述里明确提到的东西，不要自行扩展：用户没提到的页面区块、模块、
     功能、菜单项、Tab、表格列、按钮、表单字段等一律不要加。宁可精简，也不臆造需求
     之外的模块。不确定要不要加的，就不加。
 11. 桌面布局按 ~1920px 宽设计（1080p 全屏桌面）。外层主容器用 Tailwind 限制最大宽度
     `max-w-[1920px] mx-auto` 居中，两侧留白，超宽屏不拉伸；用 antd 的 Row/Col 或
     Tailwind 的响应式断点（lg/xl/2xl）自适应；侧边栏折叠、表格横向滚动等中后台常见
     交互按需实现。

【设计要求】
- 信息架构清晰：顶部栏 + 侧边菜单 + 主内容区，符合中后台习惯。
- 视觉层次、间距、配色专业协调，遵循 antd 设计语言。
- 表格、表单、统计卡、图表等组件完整、精致，空状态/加载态可省但数据真实。
- 文案真实贴合需求场景，不要 Lorem ipsum，不要编造需求里没有的功能说明。

【交付格式】
- 不要输出 reasoning_content、分析过程或实现思路，直接生成最终 HTML/JSX。
- 最终 answer/content 只返回源代码，必须以 <!DOCTYPE html> 开始，以 </html> 结束。
- 不要使用 Markdown 代码围栏，最终 content 中不要写解释、说明、寒暄或实现思路。
- 如果输出额度紧张，减少装饰和非必要内容，优先保证 HTML 完整闭合且可以渲染。""".replace(
    "__LUCIDE_VERSION__", _LUCIDE_CDN_VERSION
)

PC_GENERATION_PROMPT = ChatPromptTemplate(
    messages=[
        ("system", SYSTEM_PC),
        ("human", "需求：{prompt}"),
    ],
)


def inject_pc_bootstrap(html: str) -> str:
    """Force Babel to use the CLASSIC JSX runtime (emit React.createElement,
    no ESM `import`) so the transformed script doesn't crash as a classic
    <script> ("Cannot use import statement outside a module").

    Per @babel/standalone docs, options are passed to a built-in preset by
    registering a NEW preset that wraps it, then pointing data-presets at it.
    """
    reg = (
        '<script>'
        '(function(){'
        'window.addEventListener("error",function(e){'
        'var b=document.getElementById("root");'
        'if(!b||b.innerHTML.trim())return;'
        'var m=(e&&(e.message||(e.error&&(e.error.stack||e.error.message))))||String(e);'
        'var s=String(m).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");'
        'b.innerHTML=`<div style="font:13px/1.6 -apple-system,system-ui,sans-serif;padding:16px;color:#b91c1c;white-space:pre-wrap;word-break:break-all;background:#fef2f2;border:1px solid #fecaca;border-radius:8px"><b>渲染失败</b>（脚本错误）\\n${s}</div>`;'
        '});'
        '})();'
        'Babel.registerPreset("react-classic",'
        '{presets:[[Babel.availablePresets["react"],{runtime:"classic"}]]});'
        '</script>'
    )
    m = re.search(r'<script\s+src="[^"]*babel[^"]*\.js"[^>]*></script>', html, re.IGNORECASE)
    if m:
        html = html[:m.end()] + reg + html[m.end():]
    else:
        html = reg + html
    # point every text/babel script's data-presets at react-classic instead of react
    html = re.sub(
        r'(data-presets\s*=\s*["\'][^"\']*)\breact\b([^"\']*["\'])',
        r'\1react-classic\2',
        html,
    )
    return html
