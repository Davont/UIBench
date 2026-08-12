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
    ComponentDiagnostic,
    ComponentMetadataReport,
    ComponentNode,
    analyze_component_metadata,
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
- 每一个写了 `data-component` 的元素都必须同时写全局唯一的 `data-node-id`，一个都不能
  漏，图标和分隔线也不例外；使用稳定的小写路径，例如 `shop.products.item-headphones`。
- 这些节点必须使用注册表中的 `data-component`，第一版允许值为：
  {_PROMPT_COMPONENTS}。
- 带 `data-node-id` 的根节点必须铺满整个视口，写上 `min-h-screen`。ArkUI 的页面根背后
  没有 body 画布，根节点没有铺满时画布颜色会在边缘露出来，这种页面无法导出。页面背景
  色写在 `<body>` 上还是写在根节点上都可以。
- `data-component` 表达结构和控件类型；可选 `data-ui-role` 表达业务复合语义，例如
  `product-card`、`app-bar`、`hero-banner`，不要把业务名称写进 `data-component`。
- 普通纵向布局标为 column，且该节点必须实际使用 `flex flex-col`；普通横向布局标为 row，
  且该节点必须实际使用 `flex flex-row`。标注必须与浏览器最终 computed layout 一致：
  column 必须得到 `display: flex`、`flex-direction: column`，row 必须得到 `display: flex`、
  `flex-direction: row`；不能只写 `data-component` 而缺少对应的布局 class。注意 Tailwind
  裸写 `flex` 等同于 `flex-row`：图标底座这类只把一个元素居中的方块容器如果写的是
  `flex items-center justify-center`，实际方向就是 row，要标 row 而不是 column。
- 存在覆盖或绝对定位的容器标为 stack；普通长内容用 scroll 包裹一个实际布局容器，scroll
  最多只能有一个已标注组件子节点。
- 同类条目重复出现的列表标为 list，纵向列表和横滑列表都适用：导出按浏览器实际方向
  生成，不需要标注方向，但 list 元素本身要写出真实布局 class（横滑写 `flex flex-row`），
  不要用 `flex-row-reverse` 这类无法表达的方向。每一条用一个 list-item 包起来。
  list 只能包 list-item，list-item 只能出现在 list 内且最多有一个已标注组件子节点，
  条目内部结构要再包一层 row 或 column。条目之间的间距写在 list 上，不要给每个
  list-item 加 margin。
  只出现一次的普通区块仍然用 column/row，不要为了用 list 而把不相关的内容硬凑成列表。
- 多列等宽的宫格（快捷入口、相册、商品网格）标为 grid，且该元素必须实际使用
  `grid grid-cols-N gap-*` 得到 `display: grid`。每个格子用一个 grid-item 包起来：
  grid 只能包 grid-item，grid-item 只能出现在 grid 内且最多有一个已标注组件子节点，
  格子内部结构再包一层 column/row。格子间距写 `gap-*` 在 grid 上，不要给格子加
  margin。不要使用 `col-span-*`、`row-span-*` 或 `grid-flow-col`：ArkUI 的 GridItem
  按行序自动放置，带显式跨行列的网格无法导出。真正的单列长列表仍然用 list。
- 当前渲染器还不支持这些组件：{_PLANNED_COMPONENTS}。这类内容暂时使用 column/row
  表达，并用 `data-ui-role`、`data-repeat`、`data-item-key` 保留业务语义，绝对不能
  输出未列入上面允许值的 `data-component`。
- 所有独立成块的文字都标为 text，包括标题、正文，也包括用 `<span>` 标签写的次要小字、
  数值和状态说明。不要因为 HTML 标签恰好叫 `<span>` 就标成 `data-component="span"`，
  这两者没有关系。
- `data-component="span"` 只用于一种情况：它的直接父节点也是 `data-component="text"`，
  用来给同一段文字里的局部片段单独设置颜色或字重，且必须有非空文本。对照：
  错误 <div data-component="row"><span data-component="span">已开启</span></div>
  正确 <div data-component="row"><span data-component="text">已开启</span></div>
  正确 <p data-component="text">共 <span data-component="span">3</span> 台设备</p>
- 状态圆点、色块、装饰条这类没有文字的元素一律不要标成 span，改标 column 或 stack。
- image 只能用在带非空 `src` 的真实 `<img>` 上，并保留 alt。没有真实图片的头像位、占位块
  不要标成 image，改用 column/stack 加背景色表达。
- button 保留原生 `<button>` 标签，且 Button 最多只能有一个已标注组件子节点。按钮内部
  同时有图标和文字时，必须在 `<button>` 里再包一层已标注的 row，把图标和文字都放进去：

  <button data-node-id="settings.account" data-component="button" class="w-full px-4 py-3">
    <div data-node-id="settings.account.line" data-component="row"
         class="flex flex-row items-center gap-3">
      <i data-node-id="settings.account.icon" data-component="symbol"
         data-lucide="user" data-symbol="sys.symbol.person" class="w-5 h-5"></i>
      <span data-node-id="settings.account.label" data-component="text"
            class="flex-1 text-left">个人资料</span>
      <i data-node-id="settings.account.more" data-component="symbol"
         data-lucide="chevron-right" data-symbol="sys.symbol.chevron_right" class="w-4 h-4"></i>
    </div>
  </button>

- Lucide `<i>` 标为 `data-component="symbol"` 并保留 `data-lucide`，正常按语义挑图标即可。
  不需要写 `data-symbol`：导出时会自动把 Lucide 图标名映射到鸿蒙系统图标资源，少数鸿蒙
  没有对应资源的图标会退化成等大的空占位，不影响其余内容导出。
  摄影图、商品图和品牌 Logo 走 image 方案。
- 行为只写稳定引用，例如 `data-action="cart.add"`，不要因此添加业务 JavaScript。
- 已标注组件的 DOM 直接父节点必须就是组件元数据中的父节点；不要在两个已标注组件之间
  插入未标注 wrapper。布局或分组 wrapper 应删除，或使用允许的 column/row/stack 等组件
  完整标注；纯装饰 wrapper 只能放在不再包含已标注后代的叶子组件内部。HTML 在没有
  ArkUI 转换器时仍必须正常渲染。
"""

__all__ = [
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
    "resolve_symbol",
    "validate_component_registry",
    "validate_renderer_contract",
]
