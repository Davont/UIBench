# Chips 组件规格

## Metadata

| 项目 | 值 |
|------|-----|
| 实现目录 | `src/components/Chips/` |
| Stories 路径 | `src/components/Chips/chips.stories.tsx` |
| Pixso 链接 | `https://pixso.cn/app/design/HA_e8I2mE7Oa0b5ZoeokSA?item-id=5313:49` |
| Item ID | `5313:49` |
| MCP 工具来源 | `get_node_dsl` (itemId=5313:49) + `get_screenshot` (itemId=5313:49) |
| 变体树 JSON | `src/components/Chips/chips.json` |
| 变体树来源 | `get_variants` 返回 `{}`，从 `get_node_dsl` 的 `pixComponentTreeDslNodes` 子节点名称重建 |

## 组成与用途

单个标签/芯片 (Chip) 组件，用于展示可选的分类标签、筛选条件或选中项。支持前置图标、文本内容和关闭按钮。

导出项：
- `Chips` — 默认导出，芯片组件
- `chipsStates` — 状态枚举常量
- `ChipsProps` — Props 类型
- `ChipsState` — 状态类型

## 量化规格

### 尺寸与间距

| 属性 | 值 | DSL 来源 |
|------|-----|---------|
| 高度 | 28px | `autoLayout` height |
| 水平内边距 | 12px | `autoLayoutPaddingLeft` / `autoLayoutPaddingRight` |
| 垂直内边距 | 4px | `autoLayoutPaddingTop` / `autoLayoutPaddingBottom` |
| 元素间距 | 4px | `autoLayoutItemSpacing` |
| 圆角 | 56px | `cornerRadius` (全圆角胶囊形) |

### 字体

| 属性 | 值 | DSL 来源 |
|------|-----|---------|
| 字体家族 | HarmonyHeiTi | `fontFamily` |
| 字号 | 14px | `fontSize` (style: Font/Body_M/Regular, ID: 602:9661) |
| 字重 | 400 (Regular) | `fontStyle` |
| 行高 | 19px | 文字节点高度 19px / fontSize 14px = ~1.357 |
| 字间距 | 0 | 默认值 |

### 色值

| 角色 | 值 | CSS 变量 | DSL 来源 |
|------|-----|---------|---------|
| 背景 (Enabled/Hover) | rgba(0,0,0,0.047) | `--harmony-comp-background-tertiary` | style ID 602:9420 / 602:9466 |
| 背景 (Pressed) | rgba(0,0,0,0.098) | `--harmony-interactive-pressed` | style ID 602:9464 |
| 文字颜色 | rgba(0,0,0,0.898) | `--harmony-font-primary` | style ID 602:9446 |
| 图标颜色 | rgba(0,0,0,0.6) | `--harmony-icon-secondary` | style ID 602:9460 |
| Focus 描边 | rgba(10,89,247,1) | `--harmony-interactive-focus` | style ID 602:9465 |

### 子元素布局

视觉顺序 (左→右)：前置图标 (16×16) → 文本 → 关闭按钮 (16×16)

> Pixso `autoLayoutItemReverseDraw: true` 导致 DSL 子节点顺序为 `.cancel`, `Text`, `icon`，实际视觉顺序已反转。React 实现按视觉顺序渲染。

## 状态与交互

| 状态 | DSL 节点 | 视觉特征 |
|------|---------|---------|
| Enabled | `1:9507` | 基础背景 `--harmony-comp-background-tertiary` |
| Hover | `1:9522` | 背景 `--harmony-interactive-hover` (值与 Enabled 相同，此版设计中视觉一致) |
| Pressed | `25:36009` | 背景 `--harmony-interactive-pressed` (rgba(0,0,0,0.098)) |
| Focus | `1:9513` | 基础背景 + 2px `--harmony-interactive-focus` 外描边 (矩形 5, guid: 25:35989) |
| Disabled | `25:36024` | opacity: 0.4，pointer-events: none |

## Props

### DSL ↔ Prop 对照表

| DSL 字段 | Prop 名 | 类型 | 默认值 | 合法取值 | 说明 |
|---------|---------|------|--------|---------|------|
| `visible_66_1` / `Close` | `Close` | `boolean` | `true` | `true` \| `false` | 显示/隐藏关闭图标 |
| `visible_2260_1` / `icon` | `icon` | `boolean` | `true` | `true` \| `false` | 显示/隐藏前置图标 |
| 实例名 `状态=*` | `状态` | `ChipsState` | `undefined` | `"Enabled"` \| `"Hover"` \| `"Pressed"` \| `"Focus"` \| `"Disabled"` | 组件状态 |

> **命名映射说明**：Prop 名 `Close` 和 `icon` 直接来自 DSL `propDefMap` 中的原始属性名（已是英文 camelCase），无需翻译。`状态` 使用 DSL 实例名中的中文字段名，符合「Props 与 DSL 硬对齐」规则。

### 额外便捷 Props

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `children` | `ReactNode` | `"Tabs"` | 芯片文本内容 |
| `iconElement` | `ReactNode` | `undefined` | 自定义前置图标元素，覆盖默认 HM Symbol 图标 |
| `disabled` | `boolean` | `undefined` | HTML 原生 disabled，效果同 `状态="Disabled"` |
| `closeLabel` | `string` | `"Remove"` | 关闭按钮 aria-label |
| `onClose` | `() => void` | `undefined` | 关闭按钮点击回调 |
| `className` | `string` | `undefined` | 自定义类名 |
| `onClick` | `(e) => void` | `undefined` | 点击回调 (disabled 时不触发) |

## 样式引用

### 使用的全局 CSS 变量

| 变量 | 用途 |
|------|------|
| `--harmony-comp-background-tertiary` | Enabled/Hover 背景 |
| `--harmony-interactive-hover` | Hover 背景 |
| `--harmony-interactive-pressed` | Pressed 背景 |
| `--harmony-interactive-focus` | Focus 描边 |
| `--harmony-font-primary` | 文字颜色 |
| `--harmony-icon-secondary` | 图标 & 关闭按钮颜色 |

### 新增全局 Token

无。所有样式均使用 `global.css` 中已有的 Token。

## 取舍说明

| 项目 | 决策 | 原因 |
|------|------|------|
| `design_to_code` CSS 不可用 | 手工基于 DSL + 截图 + global.css 变量手写样式 | 批次缓存过期 (Invalid batch timestamp) |
| `get_variants` 返回 `{}` | 从 `get_node_dsl` 子节点名称重建变体树 | Pixso 组件变体属性未通过该接口暴露 |
| HM Symbol 默认图标 | 使用本地 `HMSymbolIcon` 的 `star` | DSL 中 icon 使用 `HM Symbol` 字体 `󰁎`（U+F004E）；通过本地 `HMSymbolVF.ttf` 渲染，用户可通过 `iconElement` 自定义 |
| Hover 与 Enabled 背景色值相同 | 保留两个独立状态数据属性 | DSL 中两者使用不同样式 ID，虽色值相同但语义不同；保留以支持未来差异化 |
| Xmark 图标 | 本地 `HMSymbolIcon name="xmark"`（U+F0056） | 与 Pixso `.cancel` 形状差异小，统一使用本地字体资源 |
