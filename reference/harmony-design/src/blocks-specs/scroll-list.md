# Scroll List - 滚动列表 Block 规格

## Metadata

| 项目 | 值 |
| --- | --- |
| Block ID | `scroll-list` |
| 实现目录 | `src/blocks/scroll-list/` |
| Stories 路径 | `src/blocks/scroll-list/scroll-list.stories.tsx` |
| Storybook Title | `Pages/筛选页面-blocks/滚动列表` |
| Pixso 链接 | `https://pixso.cn/app/design/f3YuUJ1DHBrZxJcUHOJeYg?item-id=79:57567` |
| MCP 工具来源 | `get_node_dsl` + `get_screenshot` |
| 变体树 JSON | `src/blocks/scroll-list/scroll-list.json` |

## 组件变体树 JSON

- 文件路径: `src/blocks/scroll-list/scroll-list.json`
- 生成方式: `get_node_dsl`（`item-id=79:57567`）+ `get_screenshot`
- `get_variants` 返回空（该节点非组件集根），降级: 从 DSL 树结构推断
- 该节点包含：
  - `FloatingAlphabetIndexer-Lable-Phone`（INSTANCE, 56×56）
  - `AlphabetIndexer-Phone`（FRAME, ~24×496, 28 个子项）
  - 9 个 `list/有封面_专辑` 实例（328×72）

## 组成与用途

**导出项**:
- `ScrollList` — 滚动列表容器 block，组合基于 ListPhone 的 FilterListItem + AlphabetIndexer + FloatingAlphabetIndexerLable
- `ScrollListItemData` — 列表项数据类型（扩展 FilterListItemData + indexLetter）
- `ScrollListProps` — Props 类型

**使用场景**: 音乐/联系人筛选页面中的可滚动列表，带字母索引侧边栏和浮动字母指示器。

**复用组件**:
- `FilterListItem`（`src/blocks/filter-list/filter-list-item.tsx`）— 列表项（基于 `ListPhone` 实现头像+标题+分隔线）
- `AlphabetIndexer`（`src/components/Views/AlphabetIndexer/`）— 字母索引侧边栏
- `FloatingAlphabetIndexerLable`（`src/components/Views/FloatingAlphabetIndexerLable/`）— 浮动字母标签指示器

## 量化规格

| 参数 | 值 | 来源 |
| --- | --- | --- |
| 根容器宽 | 360px | DSL `width: 360` |
| 根容器高 | 648px | DSL `height: 648` |
| 根容器背景 | `rgba(241, 243, 245, 1)` = `--harmony-background-secondary` | DSL fillPaints |
| 列表区 padding-left | 16px | DSL 内容区偏移 |
| 列表区 padding-right | 40px | 预留 AlphabetIndexer 空间 |
| Item 宽 | 328px | DSL instance |
| Item 高 | 72px | DSL instance |
| Item 垂直间距 | 0px（相邻无间距，靠 divider 分隔） | DSL |
| 头像尺寸 | 48×48px | DSL 推导 |
| 头像圆角 | 50% | 截图视觉 |
| 标题字号 | 16px | Harmony Body_L |
| 标题字重 | 400 | Harmony Body_L Regular |
| 标题行高 | 22px | Harmony 字阶标准 |
| AlphabetIndexer 容器宽 | 24px | DSL `width: 23.996` |
| AlphabetIndexer 子项宽 | 16px | 组件 item 尺寸，居中包裹在 24px 容器内 |
| AlphabetIndexer 高 | 496px | DSL `height: 496` |
| AlphabetIndexer 位置 | right: 16px, 容器 24px，垂直居中 | DSL `left: 320` |
| Floating Label 尺寸 | 56×56px | DSL INSTANCE |
| Floating Label 圆角 | 28px（50%） | DSL `cornerRadius: 28` |
| Floating Label 位置 | 仅按住并拖动索引条时显示在索引条左侧；与 24px 索引容器横向间隔 48px；首个放大项与当前字母垂直对齐 | 参考交互截图 + DSL label 尺寸 |
| Floating Label 背景 | 毛玻璃效果 | FloatingAlphabetIndexerLable 组件 |
| Floating Label 阴影 | backdrop-blur + inner shadow | FloatingAlphabetIndexerLable 组件 |

## 状态与交互

| 状态 | 说明 |
| --- | --- |
| Default | 默认展示，列表可滚动，索引栏可用 |
| Scroll | 滚动列表时，AlphabetIndexer 激活态跟踪当前可视区域首字母 |
| Indexer Click | 点击 AlphabetIndexer 字母，列表滚动到对应字母分组 |
| Indexer Drag | 按住并拖动 AlphabetIndexer 时才挂载 FloatingAlphabetIndexerLable cn 放大窗，显示当前字母及当前分组候选项；松手或取消后立即卸载 |
| Item Hover | 鼠标悬停列表项时背景变为 `--harmony-interactive-hover` |
| Item Active | 点击列表项时背景变为 `--harmony-interactive-pressed` |

## Props

### ScrollList

| Prop | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `items` | `ScrollListItemData[]` | `[]` | 列表项数据 |
| `类型` | `"port" \| "land"` | `"land"` | AlphabetIndexer 变体 |
| `onItemClick` | `(index, item) => void` | `undefined` | 点击列表项回调 |
| `getIndexPreviewItems` | `(letter, items) => CnIndexItem[]` | `undefined` | 拖动索引条时自定义放大窗内容 |
| `className` | `string` | `undefined` | 自定义类名 |

### ScrollListItemData

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `avatarSrc` | `string \| undefined` | 头像图 URL |
| `avatarAlt` | `string` | 头像 alt 文本 |
| `title` | `string` | 主标题 |
| `indexLetter` | `string \| undefined` | 索引字母（可选，默认从 title 首字母推导） |

## DSL ↔ Prop 对照

| DSL 字段路径 | Prop 名 | 可取值 | 说明 |
| --- | --- | --- | --- |
| `79:58023` (INSTANCE `list/有封面_专辑`) | `items[]` | 数组 | 列表项，映射为 FilterListItem |
| `79:58024` (FRAME `AlphabetIndexer-Phone`) | `类型` | `"port"` / `"land"` | AlphabetIndexer 变体 |
| `79:58238` (INSTANCE `FloatingAlphabetIndexer-Lable-Phone`) | `getIndexPreviewItems` / 运行时状态 | — | FloatingAlphabetIndexerLable，仅在拖动索引条时以 `cn` 放大窗形式展示 |
| `2:67460` (RECTANGLE image) | `items[].avatarSrc` | URL 字符串 | 头像图片 |
| `2:67464` (TEXT) | `items[].title` | 任意字符串 | 标题文本 |

**命名映射说明**: DSL 中 `类型` 属性直接用作 React Prop 名（中文），符合仓库「Props 与 get_node_dsl 硬对齐」规范。

## 样式引用

### 使用的 global.css 变量

| CSS 变量 | 用途 | Pixso 取值 |
| --- | --- | --- |
| `--harmony-background-secondary` | 根容器背景色 | `rgba(241, 243, 245, 1)` |
| `--harmony-font-primary` | 标题文字颜色 | `rgba(0, 0, 0, 0.898)` |
| `--harmony-comp-divider` | 分隔线颜色 | `rgba(0, 0, 0, 0.06)` |
| `--harmony-interactive-hover` | Hover 背景 | `rgba(0, 0, 0, 0.04)` |
| `--harmony-interactive-pressed` | Pressed 背景 | `rgba(0, 0, 0, 0.08)` |
| `--harmony-comp-background-tertiary` | 头像占位背景 | `rgba(0, 0, 0, 0.047)` |
| `--harmony-font-emphasize` | 索引激活态文字色 | `rgba(10, 89, 247, 1)` |

### 新增 Token

本次未新增 global.css Token。

## 取舍说明

1. **复用策略**: 本 block 完全复用现有 `FilterListItem`、`AlphabetIndexer`、`FloatingAlphabetIndexerLable` 三个组件；其中 `FilterListItem` 底层复用 `ListPhone`。
2. **Floating Label 定位**: FloatingAlphabetIndexerLable 默认不挂载；仅按住并拖动索引条时采用 `position: absolute` 固定在索引条左侧，并让 cn 放大窗首个圆形项对齐当前字母。横向位置按 `右侧安全距 16px + 索引容器 24px + 间隔 48px = right: 88px` 计算。
3. **滚动跟踪**: 实现 scroll 事件监听，自动跟踪当前可视区域首字母并更新 `AlphabetIndexer.activeLabel`。
4. **索引交互**: `AlphabetIndexer` 默认独立展示并支持点击跳转；只有按住并拖动时才挂载 `FloatingAlphabetIndexerLable 类型="cn"` 放大窗，松手或取消时立即卸载，默认态不能同时存在两个组件。
5. **索引器模式**: 支持 `port`（全量 A-Z + # + ☆）和 `land`（字母+圆点缩写）两种模式，默认 `land` 与 DSL 截图一致。
6. **列表项复用**: 直接复用基于 `ListPhone` 的 `FilterListItem` 组件（含头像+标题+分隔线），保持与 `filter-list` block 的视觉一致性；滚动列表的右侧 divider inset 继续由 `scroll-list.css` 按 AlphabetIndexer 安全区校准。
