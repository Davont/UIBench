# FloatingChips 组件规格

## Metadata

| 项目 | 值 |
|------|-----|
| 实现目录 | `src/components/FloatingChips/` |
| Stories 路径 | `src/components/FloatingChips/FloatingChips.stories.tsx` |
| Pixso 链接 | `https://pixso.cn/app/design/Xs4by4YngOt5unb-_N4vxQ?item-id=5425:435` |
| Item ID | `5425:435` |
| MCP 工具来源 | `get_node_dsl(guid=5425:435)` + `get_screenshot(guid=5425:435)` |
| Fallback | `get_screenshot` 成功，未调用 `get_export_image` |

## 量化规格

| 类型 | 值 |
|------|-----|
| 外层组 | `94×301`，5 个状态纵向排列 |
| 单个 chip | `93×28` |
| 内边距 | `12px` 左右，`4px` 上下 |
| 元素间距 | `4px` |
| 圆角 | `56px` |
| 前置 icon | 本地 `HMSymbolIcon name="star"`（U+F004E），`16×16`，颜色 `rgba(0,0,0,0.6)` |
| Close icon | 本地 `HMSymbolIcon name="xmark"`（U+F0056），`16×16`，颜色继承组件 token |
| 文本 | `HarmonyHeiTi Regular 14px`，行高约 `19px`；Light `rgba(0,0,0,0.898039)`，Dark `rgba(255,255,255,0.9)` |
| Focus ring | `2px #0A59F7`，外扩 `4px`，视觉尺寸约 `101×36` |

## DSL 属性/变体

| DSL 字段 | Prop | 类型 | 默认值 | 取值 |
|---------|------|------|--------|------|
| `visible_66_1` / `Close` | `Close` | `boolean` | `true` | `true` / `false` |
| `visible_2260_1` / `icon` | `icon` | `boolean` | `true` | `true` / `false` |
| 实例名 `状态=*` | `状态` | `FloatingChipsState` | `"Enabled"` | `"Enabled"` / `"Hover"` / `"Pressed"` / `"Focus"` / `"Disabled"` |
| 实例名 `通透度=*` | `通透度` | `FloatingChips通透度` | `"标准"` | `"标准"` |

命名映射：`Close`、`icon`、`状态`、`通透度` 均直接保留 DSL 字段；只补充 React 惯例 props `children`、`iconElement`、`closeLabel`、`onClose`。

## 状态

| 状态 | DSL 节点 | 视觉 |
|------|---------|------|
| Enabled | `5425:195` / 实例 `5425:387` | 根部胶囊背板 `rgba(0,0,0,0.047059)` + `FLOATING_ULTRA_THIN` 浮层材质 |
| Hover | `5425:223` / 实例 `5425:415` | 根部背板 + `矩形 6` 叠加 `interactive_hover rgba(0,0,0,0.047059)` |
| Pressed | `5425:233` / 实例 `5425:425` | 根部背板 + `矩形 6` 叠加 `interactive_click rgba(0,0,0,0.098039)` |
| Focus | `5425:204` / 实例 `5425:396` | 浮层材质 + 外描边 |
| Disabled | `5425:214` / 实例 `5425:406` | 内容 opacity `0.4` |

## global.css 对照

| 设计 token / style | 结论 |
|--------------------|------|
| `Light/font_primary` | 复用 `--harmony-font-primary` |
| `Dark/font_primary` | 组件 dark 下显式使用 `rgba(255,255,255,0.9)` |
| `Light/icon_secondary` | 复用 `--harmony-icon-secondary` |
| `Light/interactive_hover` | 复用 `--harmony-interactive-hover` |
| `Light/interactive_click` | 复用 `--harmony-interactive-pressed` |
| `Light/interactive_focus` | 复用 `--harmony-interactive-focus` |
| `Light/Blur/FLOATING_ULTRA_THIN` | 复用 `--FLOATING_ULTRA_THIN_fill`，阴影/高光/blur 在组件局部补齐 |

新增全局 token：无。浮层材质细节仅在组件 CSS 局部声明，避免污染全局 token。
