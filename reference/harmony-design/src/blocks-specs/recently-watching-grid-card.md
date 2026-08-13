# Recently Watching Grid Card - 宫格式列表 Block 规格

## Metadata

| 项目 | 值 |
| --- | --- |
| Block ID | `recently-watching-grid-card` |
| 实现目录 | `src/blocks/recently-watching-grid-card/` |
| Stories 路径 | `src/blocks/recently-watching-grid-card/RecentlyWatchingGridCard.stories.tsx` |
| Storybook Title | `Pages/我的-卡片blocks/宫格式列表` |
| Pixso 链接 | `https://pixso.cn/app/design/f3YuUJ1DHBrZxJcUHOJeYg?item-id=53:56323` |
| MCP 工具来源 | `get_node_dsl` + `get_screenshot` + `design_to_code` |
| 变体树 JSON | `src/blocks/recently-watching-grid-card/recently-watching-grid-card.json` |

## 组件变体树 JSON

- 文件路径: `src/blocks/recently-watching-grid-card/recently-watching-grid-card.json`
- 生成方式: `get_node_dsl`（`item-id=53:56323`）+ `get_variants`（返回空，使用降级: 从 DSL 树结构推断）
- 该节点无变体属性，为单一状态组件

## 组成与用途

**导出项**: `RecentlyWatchingGridCard`（主组件）、`GridCardItem`（类型）、`RecentlyWatchingGridCardProps`（类型）

**使用场景**: "我的"页面中展示用户最近观看的视频/剧集列表，以 2×3 宫格形式呈现，每项含封面图、徽标（评分/集数）与副标题。

## 量化规格

| 参数 | 值 | 来源 |
| --- | --- | --- |
| 外层容器宽 | 352px | DSL `width: 352` |
| 外层容器高 | 422px | DSL `height: 422` |
| 外层容器背景 | `rgba(24, 24, 26, 1)` | DSL fillPaints |
| 外层容器 padding | 12px | DSL autoLayoutPadding |
| 内层卡片宽 | 328px | DSL `width: 328` |
| 内层卡片高 | 398px | DSL `height: 398` |
| 内层卡片背景 | `rgba(255, 255, 255, 0.098039)` | DSL fillPaints |
| 内层卡片圆角 | 16px | DSL cornerRadius |
| 内层卡片 padding-x | 12px | DSL autoLayoutPaddingLeft/Right |
| 头部高度 | 56px | DSL SubHeaderPhone height |
| 标题字号 | 24px | DSL text-fontsubtitle_lbold |
| 标题字重 | 700 | DSL Subtitle_L Bold |
| 标题颜色 | `--harmony-font-primary` | DSL fill-darkfont_primary |
| 更多文字颜色 | `--harmony-font-secondary` | DSL fill-darkfont_secondary |
| 宫格列数 | 2 | DSL flex-wrap layout |
| 宫格水平间距 | 8px | DSL gap (column) |
| 宫格垂直间距 | 12px | DSL gap (row) |
| 封面图宽 | 96px | DSL `width: 96` |
| 封面图高 | 133px | DSL `height: 133` |
| 封面图圆角 | 8px | DSL borderRadius |
| 封面图阴影 | `drop-shadow(0px 1px 5px rgba(0,0,0,0.051))` | DSL filter |
| 徽标背景 | `rgba(255, 255, 255, 0.30)` | DSL fillPaints |
| 徽标渐变 | `linear-gradient(90deg, rgba(0,0,0,0.30), rgba(0,0,0,0.30))` | DSL background-image |
| 徽标圆角 | 6px 2px 6px 2px | DSL borderRadius |
| 徽标 padding | 1px 4px | DSL autoLayoutPadding |
| 徽标字号 | 10px | DSL text-fontcaption_mregular |
| 徽标字重 | 500 | DSL Caption_M Regular |
| 徽标颜色 | `--harmony-font-on-primary` | DSL fill-darkfont_on_primary |
| 标题下方文字字号 | 14px | DSL text-fontbody_sregular → 实际 12px |
| 标题下方文字颜色 | `--harmony-font-secondary` | DSL fill-darkfont_secondary |
| 分割线颜色（全宽） | `rgba(255, 255, 255, 0.40)` | DSL fillPaints |
| 分割线颜色（已播放） | `rgba(255, 255, 255, 1)` | DSL fillPaints |
| 分割线高度 | 2px | DSL height |

## 状态与交互

| 状态 | 说明 |
| --- | --- |
| Default | 默认展示，宫格项完整渲染 |
| Empty | 无数据时宫格区域为空 |
| FewItems | 少于 6 条时宫格自动排列（2×2、1×2 等） |
| Hover (更多按钮) | 鼠标悬停"更多"按钮，可添加 hover 态（当前未实现） |

## Props

| Prop | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `title` | `string` | `"最近在看"` | 区块标题 |
| `moreText` | `string` | `"更多"` | "更多"链接文字 |
| `items` | `GridCardItem[]` | `[]` | 卡片列表数据（最多 6 条） |
| `onMoreClick` | `() => void` | `undefined` | 点击"更多"回调 |
| `className` | `string` | `undefined` | 自定义类名 |

### GridCardItem 类型

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `image` | `string \| undefined` | 封面图 URL |
| `subtitle` | `string` | 副标题文本 |
| `badgeText` | `string \| undefined` | 徽标文本（评分/集数） |

## DSL ↔ Prop 对照

| DSL 字段路径 | Prop 名 | 可取值 | 说明 |
| --- | --- | --- | --- |
| `2:61534` (paragraph text) | `title` | 任意字符串 | 区块标题，DSL 中为"最近在看" |
| `2:61551` (paragraph text) | `moreText` | 任意字符串 | "更多"文字，DSL 中为"更多" |
| `2:67102, 2:67105, ...` (paragraph text) | `items[].subtitle` | 任意字符串 | 宫格项副标题 |
| `2:67123` (paragraph text) | `items[].badgeText` | 任意字符串 | 徽标文字（如"8.5"、"32集全"） |
| `2:67119` (rectangle backgroundImage) | `items[].image` | URL 字符串 | 封面图 |

**命名映射说明**: DSL 中组件属性为 slot-based（`slot_2_67102` 等），React 组件转换为语义化 Props（`subtitle`、`badgeText`、`image`），语义保持一致，取值集合不受限。

## 样式引用

### 使用的 global.css 变量

| CSS 变量 | 用途 | Pixso 取值 |
| --- | --- | --- |
| `--harmony-font-on-primary` | 区块标题、徽标文字颜色 | `rgba(255, 255, 255, 1)` |
| `--harmony-font-on-secondary` | "更多"文字、宫格项副标题颜色 | `rgba(255, 255, 255, 0.6)` |

### 新增 Token（如需复用）

当前组件使用局部 CSS 变量（`--rwgc-*`），未新增 global.css Token。若后续多页面复用此卡片，可考虑将以下值提升为全局 Token:

| 建议 Token 名 | 取值 | 适用范围 |
| --- | --- | --- |
| `--harmony-comp-background-list-card` | `rgba(255, 255, 255, 0.098039)` | 深色列表卡片背景 |

## 取舍说明

1. **封面图**: DSL 中封面图使用 Pixso 内部资源 URL，组件中使用 `backgroundImage` CSS 属性 + 外部 URL 传入，视觉一致。
2. **进度分割线**: DSL 中分割线宽度因图片而异（55.8px/96px ≈ 58%），组件中统一使用 `57%` 作为默认值，可通过 CSS 变量自定义。
3. **宫格布局**: DSL 使用 `flex-wrap: wrap` + `flex-grow: 1; flex-basis: 0; min-width: 96px`，组件中使用固定宽度 `96px` + `flex-shrink: 0` 以确保 2 列精确对齐。
4. **字体**: DSL 引用 Harmony 字阶（`fontsubtitle_lbold`、`fontbody_sregular`、`fontcaption_mregular`），组件中直接映射为 px 值（24px/700、12px/400、10px/500），与 global.css 字阶一致。
5. **移除宫格项标题**: DSL 中宫格项有标题（`fontbody_sregular`，14px）和副标题两行文字，根据需求移除了标题行，仅保留副标题（`rwgc__subtitle`，12px）。
