# Toggle (状态按钮-2in1)

## Metadata

- **实现目录**: `src/components/Toggle/`
- **Stories 路径**: `src/components/Toggle/Toggle.stories.tsx`
- **Pixso 链接**: `https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5319:20089`
- **MCP 工具来源**: `get_node_dsl` (Success), `get_screenshot` (Success), `get_variants` (Failed — 返回 `{}`)

## 组件变体树 JSON

- **路径**: `src/components/Toggle/toggle.json`
- **生成方式**: `get_variants` 返回空对象 `{}`，变体树从 `get_node_dsl` 的 `pixComponentTreeDslNodes` 重建
- **MCP 调用**: `get_node_dsl` (itemId=5319:20089)

## 组成与用途

- **导出项**: `Toggle`（默认导出组件）、`toggleStates`、`toggleTypes`（枚举常量）
- **使用场景**: 移动端二元状态切换按钮（如选中/未选中、开/关），支持完整的交互状态反馈

## 量化规格

| 参数 | 值 | 来源 |
|------|-----|------|
| 宽度 | 72px (FIXED, RESIZE_TO_FIT) | DSL `autoLayout.stackPrimarySizing=FIXED` |
| 高度 | 28px | DSL `height` |
| 内边距 | 4px (上下), 8px (左右) | DSL `autoLayoutPaddingTop/Bottom/Left/Right` |
| 圆角 | 8px | DSL `cornerRadius` |
| 字号 | 14px | DSL `fontSize` |
| 字重 | 400 (Regular) | DSL `fontStyle=Regular` |
| 行高 | 20px | DSL text height=20px |
| 字间距 | 0 | DSL `letterSpacingNumber=0` |
| 字体 | HarmonyHeiTi | DSL `fontFamily` |
| 文字颜色 | `--harmony-font-primary` (rgba(0,0,0,0.898)) | DSL `inheritFillStyleID=602:9446` (Light/font_primary) |

## 状态与交互

### 类型=Unselected

| 状态 | 背景 | 叠加层 | 透明度 |
|------|------|--------|--------|
| Enabled | `--harmony-comp-background-tertiary` (rgba(0,0,0,0.047)) | 无 | 1.0 |
| Hover | `--harmony-comp-background-tertiary` | `--harmony-interactive-hover` (rgba(0,0,0,0.047)) | 1.0 |
| Pressed | `--harmony-comp-background-tertiary` | `--harmony-interactive-click` (rgba(0,0,0,0.098)) | 1.0 |
| Focus | `--harmony-comp-background-tertiary` | 边框 `--harmony-interactive-focus` (rgba(10,89,247,1)) 1px | 1.0 |
| Disabled | `--harmony-comp-background-tertiary` | 无 | 0.4 |

### 类型=Selected

| 状态 | 背景 | 叠加层 | 透明度 |
|------|------|--------|--------|
| Enabled | `--harmony-comp-background-emphasize` (rgba(10,89,247,1)) at 20% opacity | 无 | 1.0 |
| Hover | `--harmony-comp-background-emphasize` at 20% | `--harmony-interactive-hover` | 1.0 |
| Pressed | `--harmony-comp-background-emphasize` at 20% | `--harmony-interactive-click` | 1.0 |
| Focus | `--harmony-comp-background-emphasize` at 20% | 边框 `--harmony-interactive-focus` 1px | 1.0 |
| Disabled | `--harmony-comp-background-emphasize` at 20% | 无 | 0.4 |

## Props

| DSL 字段 | Prop 名 | 类型 | 默认值 | 可取值的集合 |
|----------|---------|------|--------|-------------|
| `状态` | `状态` | `"Enabled" \| "Hover" \| "Pressed" \| "Focus" \| "Disabled"` | `"Enabled"` | Enabled, Hover, Pressed, Focus, Disabled |
| `类型` | `类型` | `"Selected" \| "Unselected"` | `"Unselected"` | Selected, Unselected |

### DSL ↔ Prop 对照

- **属性名策略**: 直接使用 Pixso 原始属性名（中文），无需命名映射
- **取值集合**: 与 `pixComponentTreeDslNodes` 中各变体的 `componentNormName` 解析一致（`状态=X,类型=Y` 格式），共 5×2=10 个变体
- **交互状态说明**: `Hover`/`Pressed`/`Focus` 状态通过 `状态` Prop 显式控制（供 Storybook 展示），实际使用时置 `状态="Enabled"` 并依赖 CSS 伪类 (`:hover`/`:active`/`:focus-visible`) 自动处理

## 样式引用

- `--harmony-comp-background-tertiary` (global.css) — Unselected 类型背景
- `--harmony-interactive-hover` (global.css) — Hover 叠加层
- `--harmony-interactive-click` (global.css) — Pressed 叠加层
- `--harmony-interactive-focus` (global.css) — Focus 边框色
- `--harmony-font-primary` (global.css) — 文字颜色
- `--harmony-comp-background-emphasize` (global.css) — Selected 类型背景（CSS 中用 `rgba(10, 89, 247, 0.2)` 直接表达 20% 透明度）

**无新增全局 Token** — 所有色值均映射到 `global.css` 中已有的 `--harmony-*` 变量。

## 取舍说明

- **`get_variants` 失败**: 返回空对象 `{}`，变体树从 `get_node_dsl` 的 `pixComponentTreeDslNodes` 完整重建，包含全部 10 个变体节点
- **Selected 背景透明度**: DSL 中 `矩形 7` 节点使用 `opacity: 0.2` 叠加 `--harmony-comp-background-emphasize` 纯色，CSS 中直接使用 `rgba(10, 89, 247, 0.2)` 等效表达，避免引入伪元素增加复杂度
- **叠加层实现**: Hover/Pressed 的叠加效果使用 `box-shadow: inset 0 0 0 999px` 技术，相比额外 DOM 节点更轻量，且与 DSL 中绝对定位 Rectangle 叠加层的视觉效果等效
- **交互状态映射**: `Hover`/`Pressed`/`Focus` 保留为显式 Prop 值以满足 Storybook 矩阵展示需求；实际交互时 CSS 伪类提供等效效果
