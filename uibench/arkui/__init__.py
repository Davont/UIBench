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

_REGISTRY = load_component_registry()
_PROMPT_COMPONENTS = ", ".join(_REGISTRY.renderer_keys())

MOBILE_ARKUI_METADATA_INSTRUCTIONS = f"""

【ArkUI 可导出组件元数据合约】
- 为页面根节点、关键布局容器、文字、图片、图标和交互控件提供全局唯一的
  `data-node-id`；使用稳定的小写路径，例如 `shop.products.item-headphones`。
- 这些节点必须使用注册表中的 `data-component`，第一版允许值为：
  {_PROMPT_COMPONENTS}。
- `data-component` 表达结构和控件类型；可选 `data-ui-role` 表达业务复合语义，例如
  `product-card`、`app-bar`、`hero-banner`，不要把业务名称写进 `data-component`。
- 普通纵向/横向布局分别标为 column/row；存在覆盖或绝对定位的容器标为 stack；普通长内容
  用 scroll 包裹一个实际布局容器，scroll 最多只能有一个已标注组件子节点。
- 当前渲染器还不支持 list、list-item、grid、grid-item、checkbox、radio、input、textarea、tabs
  等组件。重复内容暂时使用 column/row 表达，并用 `data-ui-role`、`data-repeat`、
  `data-item-key` 保留业务语义，绝对不能输出未列入第一版允许值的 `data-component`。
- 标题、正文等文本节点标为 text；只有 text 内需要独立样式的文字片段才标为 span，span
  必须有非空文本且不能出现在 text 之外。
- button 保留原生 `<button>` 标签；如果内部同时有图标和文字，只标注一个 row 子节点，
  确保 Button 最多只有一个已标注组件子节点。
- Lucide `<i>` 标为 `data-component="symbol"` 并保留 `data-lucide`；`data-symbol` 必须填写
  已确认的 `sys.symbol.*` 或 `app.symbol.*` 规范资源名，不能直接复制 Lucide 名称。无法确认
  Symbol 资源映射时使用 image 方案。摄影图、商品图和品牌 Logo 也使用 image 并保留 src/alt。
- 行为只写稳定引用，例如 `data-action="cart.add"`，不要因此添加业务 JavaScript。
- 不需要给纯装饰 wrapper 强行添加组件元数据；HTML 必须在没有 ArkUI 转换器时仍能正常渲染。
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
    "analyze_component_metadata",
    "build_screen_ir",
    "load_component_registry",
    "load_renderer_contract",
    "normalize_page_name",
    "validate_component_registry",
    "validate_renderer_contract",
]
