# TextSelectionHandle — 文本选择手柄

## Metadata

| 字段 | 值 |
|------|-----|
| 实现目录 | `src/components/TextSelectionHandle/` |
| Stories | `src/components/TextSelectionHandle/TextSelectionHandle.stories.tsx` |
| Pixso 链接 | `https://pixso.cn/app/design/HA_e8I2mE7Oa0b5ZoeokSA?item-id=5314:19590` |
| Pixso 节点 | Textselection-Hander bottom (Frame, 94×73) |
| MCP 工具来源 | `get_node_dsl` + `get_screenshot` (降级 `get_export_image`) + `get_variants` (返回 `{}`) |
| 变体树 JSON | `src/components/TextSelectionHandle/TextSelectionHandle.json` |

## 组件变体树 JSON

- **路径**：`src/components/TextSelectionHandle/TextSelectionHandle.json`
- **生成方式**：`get_variants` 返回 `{}`，降级结合 `get_node_dsl` 的 `pixComponentTreeDslNodes` 重建
- **variantOptions**：`{ "属性 1": ["Hander bottom", "Hander top"] }`
- **pixTreeNodes**：包含主 Frame (5314:19590) 及两个子节点的树结构

## 组成与用途

| 导出项 | 用途 |
|--------|------|
| `TextSelectionHandle` | 文本选择手柄组件，渲染可选择起始端/结束端的手柄图标 |
| `TextSelectionHandleProps` | 组件 Props 类型 |
| `TextSelectionHandle属性` | `"Hander bottom" \| "Hander top"` 联合类型 |
| `textSelectionHandle属性Options` | 属性可选值常量数组 |

## 量化规格

### 主容器 (5314:19590)

| 参数 | 值 | 来源 |
|------|-----|------|
| 宽度 | 94px | DSL `width` |
| 高度 | 73px | DSL `height` |
| 背景 | `#ffffff` (SOLID) | DSL `fillPaints[0]` |

### Hander bottom (5314:19586 / 1:9604)

| 参数 | 值 | 来源 |
|------|-----|------|
| 宽度 | 19px | DSL `width` |
| 高度 | 40px | DSL `height` |
| X 坐标 | 21px | DSL `left` |
| Y 坐标 | 16px | DSL `top` |
| 填充色 | `rgba(10, 89, 247, 1)` | DSL `localStyleMap["602:9401"]` (`Light/brand`) |
| 对应 Token | `var(--harmony-brand)` | `global.css :root` |
| SVG 路径 | `Boolean_operation_67_34909` | Pixso 导出 SVG |

### Hander top (5314:19580 / 1:9600)

| 参数 | 值 | 来源 |
|------|-----|------|
| 宽度 | 19px | DSL `width` |
| 高度 | 40px | DSL `height` |
| X 坐标 | 64px | DSL `left` |
| Y 坐标 | 16px | DSL `top` |
| 填充色 | `rgba(10, 89, 247, 1)` | DSL `localStyleMap["602:9401"]` (`Light/brand`) |
| 对应 Token | `var(--harmony-brand)` | `global.css :root` |
| SVG 路径 | `Boolean_operation_67_34911` | Pixso 导出 SVG |

## 状态与交互

本组件为纯展示型组件（`role="presentation"`），不含交互状态。手柄的拖拽交互由使用方（文本选择系统）实现。

## Props

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `属性` | `"Hander bottom" \| "Hander top" \| undefined` | `undefined` | Pixso `属性 1` 映射。`undefined` 同时渲染两个手柄 |

### DSL ↔ Prop 对照

| DSL 字段 | Prop 名 | 映射说明 |
|----------|---------|----------|
| `属性 1` (实例属性) | `属性` | 去掉了空格和数字后缀（TypeScript 标识符不支持空格）；语义与合法取值集合完全一致 |

| DSL 合法取值 | 实现取值 | 一致性 |
|-------------|---------|--------|
| `"Hander bottom"` | `"Hander bottom"` | ✓ 一致 |
| `"Hander top"` | `"Hander top"` | ✓ 一致 |

## 样式引用

### 使用的全局 Token

| Token | 用途 |
|-------|------|
| `var(--harmony-brand)` | 手柄 SVG 填充色（`currentColor`） |

### 组件级样式类

| 类名 | 用途 |
|------|------|
| `.hm-text-selection-handle` | 双柄容器（94×73, bg white, relative） |
| `.hm-text-selection-handle__icon` | 单个手柄 SVG（absolute, 19×40, top 16px） |
| `.hm-text-selection-handle__icon--bottom` | Hander bottom 定位（left 21px） |
| `.hm-text-selection-handle__icon--top` | Hander top 定位（left 64px） |
| `.hm-text-selection-handle--standalone` | 单柄模式（去除固定容器尺寸和背景） |

## 取舍说明

- `get_variants` 返回 `{}`，变体树基于 `get_node_dsl` 的子节点结构手工重建
- `design_to_code` CSS 批次时间戳过期（`Invalid batch timestamp`），样式基于 DSL + 导出 SVG 手写
- `属性 1` → `属性` 命名映射（去掉空格和数字后缀），因 TypeScript 标识符不支持空格；语义和取值集合未变
- 无视觉回归自动化（Storybook 截图脚本未运行），以人工对照 DSL 坐标 + 导出 SVG 复核
