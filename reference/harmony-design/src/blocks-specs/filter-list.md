# Filter List - 筛选页面列表 Block 规格

## Metadata

| 项目 | 值 |
| --- | --- |
| Block ID | `filter-list` |
| 实现目录 | `src/blocks/filter-list/` |
| Stories 路径 | `src/blocks/filter-list/filter-list.stories.tsx` |
| Storybook Title | `Pages/筛选页面-blocks/筛选列表` |
| Pixso 链接 | `https://pixso.cn/app/design/f3YuUJ1DHBrZxJcUHOJeYg?item-id=79:57058` |
| MCP 工具来源 | `get_node_dsl` + `get_screenshot` |
| 变体树 JSON | `src/blocks/filter-list/filter-list.json` |

## 组件变体树 JSON

- 文件路径: `src/blocks/filter-list/filter-list.json`
- 生成方式: `get_node_dsl`（`item-id=79:57058`）+ `get_variants`（返回空，降级: 从 DSL 树结构推断）
- 该节点包含 9 个 `list_` 组件实例，均为同一主组件（`2:67455`）的实例

## 组成与用途

**导出项**:
- `FilterList` — 列表容器组件，接受 `items` 数组并渲染列表项
- `FilterListItem` — 单个列表项组件，基于 `ListPhone` 承载行高、标题和统一分隔线，左侧通过 `leftSlot` 注入头像
- `FilterListItemData` — 列表项数据类型
- `FilterListProps` / `FilterListItemProps` — Props 类型

**使用场景**: 筛选页面中的艺人/歌曲/专辑列表，每项展示头像 + 名称。

## 量化规格

| 参数 | 值 | 来源 |
| --- | --- | --- |
| 根容器宽 | 360px | DSL `width: 360` |
| 根容器高 | 648px | DSL `height: 648` |
| 根容器背景 | `rgba(241, 243, 245, 1)` = #F1F3F5 | DSL fillPaints |
| 内容区宽 | 344px (left:16px padding) | DSL childNode |
| 列表容器宽 | 328px | DSL childNode |
| 列表容器背景 | `rgba(255, 255, 255, 1)` | 白色背景 |
| Item 宽 | 328px | DSL instance `width: 328` |
| Item 高 | 72px | DSL instance `height: 72` |
| Item padding (上下) | 12px | DSL autoLayoutPaddingTop/Bottom |
| Item padding (左右) | 12px | 与 ListItem 对齐 |
| Item 水平间距 (avatar ↔ title) | 8px | DSL autoLayoutItemSpacing |
| Item 垂直间距 | 8px | DSL autoLayoutItemSpacing |
| 头像尺寸 | 48×48px | DSL 推导: (72 - 12×2) = 48px |
| 头像圆角 | 50% (圆形) | 截图视觉 |
| 标题字号 | 16px | DSL TEXT `height: 21` → 16px |
| 标题字重 | 400 | Harmony Body_M Regular |
| 标题行高 | 22px | Harmony 字阶标准 |
| 标题颜色 | `--harmony-font-primary` | DSL |
| 分隔线高度 | `ListPhone divider` | 由 `ListPhone` 内部统一分隔线提供视觉 0.5px |
| 分隔线颜色 | `--harmony-comp-divider` | Harmony Token |
| 分隔线 inset | 从标题内容列起始位置到右边缘 | `ListPhone dividerMode="custom"`，由 `filter-list.css` 保留既有视觉校准 |

## 状态与交互

| 状态 | 说明 |
| --- | --- |
| Default | 默认展示，列表项完整渲染 |
| Hover | 鼠标悬停时背景变为 `--harmony-interactive-hover` |
| Active/Pressed | 点击时背景变为 `--harmony-interactive-pressed` |
| FewItems | 少于默认数量时自动适应 |
| SingleItem | 单条数据时不显示底部分隔线 |

## Props

### FilterList

| Prop | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `items` | `FilterListItemData[]` | `[]` | 列表项数据 |
| `onItemClick` | `(index, item) => void` | `undefined` | 点击列表项回调 |
| `className` | `string` | `undefined` | 自定义类名 |

### FilterListItem

| Prop | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `avatarSrc` | `string \| undefined` | `undefined` | 头像图 URL |
| `avatarAlt` | `string` | `""` | 头像 alt 文本 |
| `title` | `string` | — | 主标题（必填） |
| `showDivider` | `boolean` | `true` | 是否展示底部分隔线 |
| `onClick` | `() => void` | `undefined` | 点击回调 |
| `className` | `string` | `undefined` | 自定义类名 |

### FilterListItemData

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `avatarSrc` | `string \| undefined` | 头像图 URL |
| `avatarAlt` | `string` | 头像 alt 文本 |
| `title` | `string` | 主标题 |
| `showDivider` | `boolean` | 是否展示分隔线 |

## DSL ↔ Prop 对照

| DSL 字段路径 | Prop 名 | 可取值 | 说明 |
| --- | --- | --- | --- |
| `2:67460` (RECTANGLE image) | `avatarSrc` | URL 字符串 | 头像图片，DSL 中为 Pixso 内部资源 |
| `2:67464` (TEXT 268×21) | `title` | 任意字符串 | 主标题文本（艺人名称） |
| `2:67455` (SYMBOL 328×72) | — | — | 主组件实例，映射为 FilterListItem |
| `autoLayoutItemSpacing: 8` | — | — | Item 间距，组件内部固定 |
| `autoLayoutPaddingTop/Bottom: 12` | — | — | Item 垂直 padding，组件内部固定 |

**命名映射说明**: DSL 中组件为 `list_` 实例，属性为 slot-based（`slot_2_67464` 等），React 组件转换为语义化 Props（`title`、`avatarSrc`），语义保持一致。DSL 中的图像资源（如 "Adele"、"James Arthur"）为 Pixso 内部哈希，组件中通过外部 URL 传入。

## 样式引用

### 使用的 global.css 变量

| CSS 变量 | 用途 | Pixso 取值 |
| --- | --- | --- |
| `--harmony-background-primary` | 列表背景色 | `rgba(255, 255, 255, 1)` |
| `--harmony-font-primary` | 标题文字颜色 | `rgba(0, 0, 0, 0.9)` |
| `--harmony-icon-tertiary` | （预留，当前未使用） | `rgba(0, 0, 0, 0.4)` |
| `--harmony-comp-divider` | 分隔线颜色 | `rgba(0, 0, 0, 0.06)` |
| `--harmony-interactive-hover` | Hover 背景 | `rgba(0, 0, 0, 0.04)` |
| `--harmony-interactive-pressed` | Pressed 背景 | `rgba(0, 0, 0, 0.08)` |
| `--harmony-comp-background-tertiary` | 头像占位背景 | `rgba(0, 0, 0, 0.04)` |

### 新增 Token

本次未新增 global.css Token。

## 取舍说明

1. **头像资源**: DSL 中头像使用 Pixso 内部资源，组件中通过 `avatarSrc` prop 传入 Wikimedia Commons（Wikipedia 信息框）外部 URL。缩略图尺寸固定 `500px`（Wikimedia 仅支持特定尺寸，`400px` 会返回 400 错误）。
2. **列表容器**: DSL 中列表容器有明确的高度（648px），组件中采用 flex 自适应高度，更灵活。
3. **移除右箭头**: DSL 中有箭头元素（`2:67469` TEXT 10×20），按需求移除，列表项仅展示头像+名称。
4. **复用策略**: 本 block 的行项底层复用 `src/components/Container/ListPhone`；头像通过 `leftSlot` 注入，标题通过 `title` 注入，`filter-list.css` 保留既有头像、字号、间距和 divider inset 的视觉校准。
5. **分隔线实现**: 行内分隔线由 `ListPhone` 的 `divider` / `dividerMode="custom"` 承载；`filter-list.css` 只负责兼容既有定位和滚动列表场景的 inset，不再直接引入 `Divider` 原子组件。
