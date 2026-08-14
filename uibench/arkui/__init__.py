"""ArkUI export contracts shared by prompting, validation, and future rendering."""
from uibench.arkui.components import (
    ComponentDefinition,
    ComponentRegistry,
    ComponentRegistryError,
    RendererComponentDefinition,
    RendererContract,
    load_component_registry,
    load_renderer_contract,
    validate_component_registry,
    validate_renderer_contract,
)
from uibench.arkui.metadata import (
    ArkUiHtmlRepair,
    ArkUiHtmlRepairResult,
    ComponentDiagnostic,
    ComponentMetadataReport,
    ComponentNode,
    analyze_component_metadata,
    repair_arkui_export_html,
    repair_missing_component_node_ids,
)
from uibench.arkui.screen_ir import (
    ScreenIrAdapterDiagnostic,
    ScreenIrBuildResult,
    build_screen_ir,
    normalize_page_name,
)
from uibench.arkui.symbols import (
    SymbolRegistryError,
    SymbolResolution,
    canonical_symbol,
    format_lucide_symbol_table,
    load_symbol_registry,
    lucide_symbol_table,
    resolve_symbol,
)

_REGISTRY = load_component_registry()
_PROMPT_COMPONENTS = ", ".join(_REGISTRY.renderer_keys())
# Derived from the pinned renderer contract so a vendor upgrade cannot leave
# the prompt advertising a component as both allowed and unsupported.
_PLANNED_COMPONENTS = "、".join(_REGISTRY.planned_keys())
_SYMBOL_TABLE = format_lucide_symbol_table()

MOBILE_ARKUI_METADATA_INSTRUCTIONS = f"""

【ArkUI 可导出组件元数据合约】
- 每个 `data-component` 必须同时有全局唯一的稳定小写路径 `data-node-id`，图标/分隔线也不例外。
- `data-component` 第一版允许值为：{_PROMPT_COMPONENTS}。
- 根组件写 `min-h-screen`。`data-component` 只表示结构/控件；业务语义写可选
  `data-ui-role`（如 product-card/app-bar）。
- 已标注组件的 DOM 直接父节点必须就是组件元数据中的父节点；不要在两个已标注组件之间
  插入未标注 wrapper。wrapper 应删除或标为允许的结构组件。
- 当前渲染器还不支持这些组件：{_PLANNED_COMPONENTS}。用 column/row 加 `data-ui-role`、
  `data-repeat`、`data-item-key` 代替，禁止输出其他 `data-component`。
- ArkUI 导出样式避免 `box-shadow`、`transform`、`align-items:baseline`；用边框、间距和
  `items-center` 表达。

【结构】
- column 必须实际使用 `flex flex-col`，row 必须实际使用 `flex flex-row`。标注必须与浏览器最终 computed layout 一致：column 必须得到 `display: flex`、`flex-direction: column`；
  row 必须得到 `display: flex`、`flex-direction: row`。裸 `flex` 是 row。
- 覆盖/绝对定位容器用 stack。长内容用 scroll，且最多一个已标注子组件；固定顶/底栏放在
  scroll 外，中间正文用 `flex-1 overflow-y-auto`；栏移到 scroll 外后不要再写 `sticky`/`fixed`。
- 重复条目用 list，纵向列表和横滑列表都适用；每项用 list-item。list 只能包 list-item，list-item 只能出现在 list 内，且最多一个已标注子组件；内部再包 row/column，间距写在 list。
- 等宽多列用 `grid grid-cols-N gap-*` 并标 grid；grid 只能包 grid-item，grid-item 只能在
  grid 内且最多一个已标注子组件。禁止 `col-span-*`、`row-span-*`、`grid-flow-col`。
- 独立文字都标 text。不要因为 HTML 标签恰好叫 `<span>` 就标成 `data-component="span"`；
  span 仅用于 text 直属的非空局部文字，text 的已标注直属子组件也只能是 span：
  错误 <div data-component="row"><span data-component="span">已开启</span></div>
  正确 <div data-component="row"><span data-component="text">已开启</span></div>
  正确 <p data-component="text">共 <span data-component="span">3</span> 台设备</p>
- 图标和文字并排时，外层必须标为 row，并实际使用 `flex flex-row`；symbol 与 text 同级。
- image 只标在有非空 `src` 和 alt 的真实 `<img>`；占位块/无字装饰用 column/stack。

【原生控件】
- 即时开关（如深色模式/护眼模式）用原生
  `<input type="checkbox" data-component="toggle">`，状态用 `checked|disabled`；禁止手绘。
- 滑块用 `<input type="range" data-component="slider">`，状态用 `value|min|max|step`；
  不要另画轨道/thumb。
- 单行输入用 `<input type="text" data-component="text-input">`，搜索用
  `<input type="search" data-component="search">`；状态用 `value|placeholder|readonly|disabled`，
  Search 不再添加搜索 symbol。
- 多选/协议才用 `<input type="checkbox" data-component="checkbox">`，状态用
  `name|value|checked|disabled`；设置项的即时开/关不能用 checkbox。
- 单选用 `<input type="radio" data-component="radio">`；同组 `name` 相同，`value` 非空且不同，
  初始项写 `checked`。
- Tabs 用 `<div data-component="tabs" data-index="0">`，直属子组件只能是
  `<section data-component="tab-content" data-tab-bar="概览">`；index 从 0 开始，tab-bar 非空。
- button 保留 `<button>` 且最多一个已标注子组件；图标+文字时只包一个已标注 row：

  <button data-node-id="settings.account" data-component="button" class="w-full px-4 py-3">
    <div data-node-id="settings.account.line" data-component="row"
         class="flex flex-row items-center gap-3">
      <i data-node-id="settings.account.icon" data-component="symbol"
         data-lucide="user" class="w-5 h-5"></i>
      <span data-node-id="settings.account.label" data-component="text"
            class="flex-1 text-left">个人资料</span>
      <i data-node-id="settings.account.more" data-component="symbol"
         data-lucide="chevron-right" class="w-4 h-4"></i>
    </div>
  </button>

- Lucide `<i>` 标为 `data-component="symbol"` 并保留 `data-lucide`；不需要写 `data-symbol`。
  开放网络用 `unlock`，语言/翻译用 `languages`，不要用近似的 `globe`。摄影图、商品图、
  品牌 Logo 用 image。行为引用可写 `data-action`，但不要添加业务 JS。
"""

__all__ = [
    "ArkUiHtmlRepair",
    "ArkUiHtmlRepairResult",
    "ComponentDefinition",
    "ComponentDiagnostic",
    "ComponentMetadataReport",
    "ComponentNode",
    "ComponentRegistry",
    "ComponentRegistryError",
    "RendererComponentDefinition",
    "RendererContract",
    "MOBILE_ARKUI_METADATA_INSTRUCTIONS",
    "ScreenIrAdapterDiagnostic",
    "ScreenIrBuildResult",
    "SymbolRegistryError",
    "SymbolResolution",
    "analyze_component_metadata",
    "build_screen_ir",
    "canonical_symbol",
    "format_lucide_symbol_table",
    "load_component_registry",
    "load_renderer_contract",
    "load_symbol_registry",
    "lucide_symbol_table",
    "normalize_page_name",
    "repair_missing_component_node_ids",
    "resolve_symbol",
    "repair_arkui_export_html",
    "validate_component_registry",
    "validate_renderer_contract",
]
