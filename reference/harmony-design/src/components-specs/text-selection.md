# TextSelection — 文本选择浮动菜单栏

## Metadata

| 字段 | 值 |
|------|-----|
| 实现目录 | `src/components/TextSelection/` |
| Stories 路径 | `src/components/TextSelection/TextSelection.stories.tsx` |
| Pixso 链接 | `https://pixso.cn/app/design/HA_e8I2mE7Oa0b5ZoeokSA?item-id=5311:19644` |
| item-id | `5311:19644` |
| MCP 工具来源 | `get_node_dsl` (5311:19644), `get_all_components`, `get_screenshot` |
| 组件集 | Textselection-Menu-Phone |
| Pixso 页面 | 2. Controls 操作类 → 4.Textselection - 文本选择 |

## 组件变体树 JSON

- 路径：`src/components/TextSelection/TextSelection.json`
- 生成方式：`get_variants` 返回空 `{}`，从 `get_node_dsl` + `get_all_components` 降级重建
- 变体维度：`语言` (中文/英文), `尺寸` (40/32/28)

## 组成与用途

| 导出项 | 说明 |
|--------|------|
| `TextSelection` | 文本选择浮动菜单栏组件 |
| `TextSelectionProps` | Props 类型定义 |
| `textSelection语言Options` | `["中文", "英文"]` |
| `textSelection尺寸Options` | `[40, 32, 28]` |

使用场景：移动端文本选中后出现的浮动操作栏，提供复制、剪切、粘贴、全选等操作入口。

## 量化规格

### 容器（语言=中文）

| 参数 | Pixso DSL 值 | 实现值 | 来源 |
|------|-------------|--------|------|
| 宽度 | 362px | `inline-flex`（自适应） | DSL `1:9608.width` |
| 高度 | 40px | `h-[40px]` | DSL `1:9608.min_node_height` |
| 圆角 | 20px | `rounded-[20px]` | DSL `1:9608.cornerRadius` |
| 背景 | rgba(255,255,255,0.9) | `var(--COMPONENT_ULTRA_THICK_fill)` | DSL fillPaints / style `Light/Blur/COMPONENT_ULTRA_THICK` |
| 背景模糊 | radius 54.37, saturation 0 | `backdrop-blur-[27px]` | DSL effects BACKGROUND_BLUR |
| 外阴影 | rgba(0,0,0,0.13), offset(0,2), radius 30 | `shadow-[0px_2px_30px_rgba(0,0,0,0.13)]` | DSL effects DROP_SHADOW |
| 布局方向 | HORIZONTAL | `flex row` | DSL autoLayout.stackMode |
| 子项间距 | 10px | `gap-[10px]` | DSL autoLayout.autoLayoutItemSpacing |
| 左内边距 | 18px | `pl-[18px]` | DSL autoLayout |
| 右内边距 | 6px | `pr-[6px]` | DSL autoLayout |

### 容器（语言=英文）

| 参数 | Pixso DSL 值 | 说明 |
|------|-------------|------|
| 宽度 | 320px | 比中文窄 42px（少 1 个按钮） |
| 其他 | 同中文 | 高度、圆角、间距等一致 |

### 图标按钮（尺寸=40，默认尺寸）

| 参数 | Pixso DSL 值 | 实现值 | 来源 |
|------|-------------|--------|------|
| 宽高 | 40×40px | `size-[40px]` | DSL `1:8089` |
| 圆角 | 1000（正圆） | `rounded-[999px]` | DSL `1:8089.cornerRadius` |
| 背景 | rgba(0,0,0,0.047) | `var(--harmony-comp-background-tertiary)` | DSL fillPaints / style `Light/comp_background_tertiary` |
| 图标尺寸 | 24×24px | `size={24}` | DSL childNode `.Default` |
| 图标颜色 | rgba(0,0,0,0.898) | `var(--harmony-icon-primary)` | DSL / style `Light/icon_primary` |
| 图标字体 | HM Symbol | `HMSymbolIcon` | DSL `fontFamily: "HM Symbol"` |

### 图标按钮尺寸变体

| 尺寸 | Pixso GUID | 内图标尺寸 | 图标内边距 |
|------|-----------|-----------|-----------|
| 40 | `1:8089` | 24×24 | 8px |
| 32 | `43:34167` | 24×24 | 4px |
| 28 | `43:34217` | 24×24 | 2px |

## 状态与交互

| 状态 | 实现 | 说明 |
|------|------|------|
| default | `--harmony-comp-background-tertiary` | 默认背景 |
| hover | `--harmony-interactive-hover` | 悬停加深 |
| active/pressed | `--harmony-interactive-pressed` | 按下加深 |
| focus | 浏览器默认 focus-visible | 键盘导航 |

## Props

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `语言` | `"中文" \| "英文"` | `"中文"` | 菜单语言变体，决定按钮数量与标签 |

### DSL ↔ Prop 对照

| DSL 属性路径 | Prop 名 | 可取值 | 是否一致 |
|-------------|---------|--------|---------|
| `语言=中文` / `语言=英文` | `语言` | `"中文"`, `"英文"` | ✅ 直接使用 |

Props 命名与取值与 `get_node_dsl` / `get_all_components` 中一致的 Pixso 原始属性名。无需命名映射例外。

## 样式引用

### 使用的 global.css 变量

| 变量 | 用途 | 匹配 DSL |
|------|------|---------|
| `--COMPONENT_ULTRA_THICK_fill` | 容器背景 | `Light/Blur/COMPONENT_ULTRA_THICK` rgba(255,255,255,0.9) ✅ |
| `--harmony-comp-background-tertiary` | 图标按钮背景 | `Light/comp_background_tertiary` rgba(0,0,0,0.047) ✅ |
| `--harmony-icon-primary` | 图标颜色 | `Light/icon_primary` rgba(0,0,0,0.898) ✅ |
| `--harmony-interactive-hover` | 按钮 hover 背景 | rgba(0,0,0,0.047) ✅ |
| `--harmony-interactive-pressed` | 按钮 active 背景 | rgba(0,0,0,0.098) ✅ |

### 新增写入 global.css 的全局 Token

无。本组件全部使用已存在的全局 Token。容器 blur 值 27px（DSL radius 54.37 / 2）直接作为组件内 CSS 值，不设全局变量。

## 取舍说明

1. **宽度自适应**：DSL 中 中文=362px / 英文=320px 固定宽度；实现采用 `inline-flex` 自适应宽度以容纳可变按钮数量，保持精确间距与内边距。
2. **图标按钮尺寸**：DSL 有 40/32/28 三种尺寸变体；当前默认实现使用 40px 尺寸，32 和 28 作为未来扩展通过 `尺寸` prop 支持。
3. **背景模糊值**：DSL BACKGROUND_BLUR radius 54.37，按项目经验（CLAUDE.md 记录）CSS `backdrop-filter: blur()` 取值约为 DSL radius / 2 ≈ 27px。
4. **饱和度**：DSL saturation=0 表示无饱和度调整，CSS 省略 `saturate()`。
5. **`get_variants` 空返回**：降级使用 `get_node_dsl` + `get_all_components` 重建变体树，变体维度覆盖完整。
