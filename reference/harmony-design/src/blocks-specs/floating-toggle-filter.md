# FloatingToggleFilter 规格文档

## Metadata

| 字段 | 值 |
| --- | --- |
| 实现目录 | `src/blocks/floating-toggle-filter/` |
| Stories 路径 | `src/blocks/floating-toggle-filter/floating-toggle-filter.stories.tsx` |
| Storybook Title | `Pages/筛选页面-blocks/FloatingToggle筛选按钮` |
| Pixso 链接 | `https://pixso.cn/app/design/f3YuUJ1DHBrZxJcUHOJeYg?item-id=79:57144` |
| MCP 工具来源 | `get_node_dsl(guid=79:57144)` + `get_screenshot(guid=79:57144)` |
| blocks.json 注册 | `src/blocks-specs/blocks.json` — id: `floating-toggle-filter` |

## 组件变体树 JSON

- 文件路径：`src/blocks/floating-toggle-filter/floating-toggle-filter.json`
- 生成方式：`get_node_dsl` 提取 `pixTreeNodes` + `props` 中的 FRAME/SYMBOL 层级结构
- 变体真值：
  - `状态`：默认 / 选中
  - `通透度`：弱 / 标准 / 强

## 组成与用途

- **导出项**：`FloatingToggleFilter`（默认导出）
- **类型导出**：`FloatingToggleFilterProps`、`FloatingToggleFilterRow`、`FloatingToggleFilter状态`、`FloatingToggleFilter通透度`
- **使用场景**：筛选页面的多行浮动切换按钮组，每行展示一个维度的筛选项，每行仅一个 active 项

## 量化规格

### 容器

| 属性 | 值 | 来源 |
| --- | --- | --- |
| 宽度 | 360px（自适应 100%） | Pixso DSL root node width=360 |
| 背景色 | `#F1F3F5` / `var(--harmony-background-secondary)` | Pixso fill `rgba(241,243,245,1)` |
| 内边距 | 16px 四周 | Pixso instance `left=16` |

### 行布局

| 属性 | 值 | 来源 |
| --- | --- | --- |
| 行数 | 3 行 | Pixso DSL 3× FRAME |
| 行间距 | 8px | Pixso FRAME `stackSpacing=8` |
| 排列方式 | Flex row, wrap | Pixso autoLayout |

### Chip 尺寸与间距

| 属性 | 值 | 来源 |
| --- | --- | --- |
| 宽度 | 72px (min-width) | Pixso DSL `width=72` |
| 高度 | 28px | Pixso DSL `height=28` |
| 圆角 | 20px (全角) | Pixso DSL `cornerRadius=20` |
| 内边距 | 9px 上下 × 16px 左右 | Pixso `stackPaddingTop=9, stackPaddingLeft=16` |
| Chip 间距 | 8px | Pixso FRAME `stackSpacing=8` |

### 材质样式（FLOATING_THIN — inactive chip）

| 层级 | 类型 | 参数 | CSS 映射 |
| --- | --- | --- | --- |
| Fill 1 | SOLID | `rgba(255,255,255,0.1)` normal | `background-color` |
| Fill 2 | SOLID | `rgba(255,255,255,0.1)` plus-lighter | `background-color + mix-blend-mode` |
| Effect 1 | BACKGROUND_BLUR | `blur(15px) saturate(120%)` | `backdrop-filter` |
| Effect 3 | INNER_SHADOW | `inset 0 10px 80px rgba(0,0,0,0.06)` darken | `box-shadow + mix-blend-mode` |
| Effect 4 | INNER_SHADOW | `inset 0 -4px 40px rgba(0,0,0,0.03)` normal | `box-shadow` |
| Effect 5 | INNER_SHADOW | `inset 0.5px 0 0.5px rgba(0,0,0,0.2)` multiply | `box-shadow + mix-blend-mode` |
| Effect 6 | INNER_SHADOW | `inset -0.5px 0 0.75px rgba(40,40,40,0.25)` darken | `box-shadow + mix-blend-mode` |
| Effect 7 | INNER_SHADOW | `inset 0 -0.5px 0.5px rgba(255,255,255,0.4)` plus-lighter | `box-shadow + mix-blend-mode` |
| Effect 8 | INNER_SHADOW | `inset 0 0.5px 0.75px rgba(255,255,255,0.7)` plus-lighter | `box-shadow + mix-blend-mode` |
| Drop Shadow | DROP_SHADOW | `0 8px 48px rgba(0,0,0,0.08)` | `box-shadow` (on container) |

### Active Chip

| 属性 | 值 | 来源 |
| --- | --- | --- |
| 填充色 | `#FF1949` / `rgba(255,25,73,1)` | Pixso style `2:65926` "品牌色" |
| 文字色 | 白色 `rgba(255,255,255,1)` | 对比度需要（active bg 深色） |
| 材质层 | 同 FLOATING_THIN 8 层 | 叠加在品牌色填充之上 |

### Typography

| 属性 | 值 | 来源 |
| --- | --- | --- |
| 字体 | `var(--button-harmony-font-family)` → "HarmonyHeiTi" | Pixso text style `2:60338` "Font/Body_S/Regular" |
| 字号 | `var(--harmony-font-size-body-s)` → 12px | Pixso `fontSize=12` |
| 字重 | `var(--harmony-font-weight-body-s)` → 400 | Pixso `fontStyle=Regular` |
| 行高 | 1 (inline) | 推算（单行文本） |
| 字间距 | 0 | 默认 |
| Inactive 文字色 | `rgba(0,0,0,0.898)` | Pixso style `2:67257` "Light/font_primary" → `--harmony-font-primary` |
| Active 文字色 | `rgba(255,255,255,1)` | Pixso "Light/font_on_primary" → `--harmony-font-on-primary` |

### 状态与交互

| 状态 | 样式 |
| --- | --- |
| 默认 (inactive) | FLOATING_THIN 材质 + dark text |
| 选中 (active) | 品牌红 #FF1949 填充 + white text + FLOATING_THIN 材质叠加 |
| Hover (inactive) | `var(--harmony-interactive-hover)` 背景叠加 |
| Active/Pressed (inactive) | `var(--harmony-interactive-pressed)` 背景叠加 |
| Focus-visible | 2px `var(--harmony-interactive-focus)` outline |

## Props

### DSL ↔ Prop 对照表

| DSL 字段 | Prop 名 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `通透度` (variant) | `通透度` | `"弱" \| "标准" \| "强"` | `"弱"` | 直接使用 DSL 原名 |
| `状态` (variant on chip) | 内部处理 | — | — | 通过 `activeIndices` / `defaultActiveIndices` 控制 |
| Row/child 结构 | `rows` | `FloatingToggleFilterRow[]` | Demo 数据 | 行数据 |
| Active item index | `activeIndices` / `defaultActiveIndices` | `number[]` | `[0, 0, ...]` | 受控/非受控 active 索引 |
| Chip click | `onActiveChange` | `(rowIndex, itemIndex) => void` | — | 点击回调 |

### 完整 Props 签名

```typescript
interface FloatingToggleFilterProps {
  通透度?: "弱" | "标准" | "强"
  rows?: FloatingToggleFilterRow[]
  defaultActiveIndices?: number[]
  activeIndices?: number[]
  onActiveChange?: (rowIndex: number, itemIndex: number) => void
  className?: string
}

interface FloatingToggleFilterRow {
  items: string[]
  activeIndex?: number
}
```

## 样式引用

### 使用的 global.css 变量

| 变量 | 用途 |
| --- | --- |
| `--harmony-background-secondary` | 容器背景色 |
| `--harmony-font-primary` | Inactive chip 文字色 |
| `--harmony-font-on-primary` | Active chip 文字色 |
| `--harmony-interactive-hover` | Hover 状态 |
| `--harmony-interactive-pressed` | Active/Pressed 状态 |
| `--harmony-interactive-focus` | Focus ring 色 |

### 使用的 global.css 材质层类

无（组件内自建 FLOATING_THIN 层，与 `global.css` 中的 `hm-material-style-layer-floating-thin-*` 类等价）。

### 新增全局 Token

无。组件使用已有 `--harmony-background-secondary` 和 Harmony 交互色 Token。

品牌红 `#FF1949` 直接内联（Pixso 品牌色，尚未映射到全局 `--harmony-brand`，因 `--harmony-brand` 为 `#0A59F7`）。

## 取舍说明

1. **材质层实现方式**：`global.css` 中的 `hm-material-style-layer-floating-thin-*` 类使用 `position: absolute` + 全局选择器。本组件在 chip 内部使用相对定位的 `<span>` 元素实现相同效果，避免全局类名冲突。视觉效果与 DSL 截图一致。

2. **Drop Shadow 分离**：DSL 中 `DROP_SHADOW` 是 effect style 的一部分，但在 DOM 中需要独立元素承载（mix-blend-mode 冲突）。本组件将 drop shadow 放在独立的 `__chip-shadow` span 中。

3. **Active 颜色**：Pixso 品牌色 `#FF1949` 与全局 `--harmony-brand` (`#0A59F7`) 不一致，使用内联色值。已在规格中标注。

4. **Typography lineHeight**：DSL 未提供 lineHeight 值，使用 `line-height: 1`（单行 12px 文本在 28px 高度容器中居中）。
