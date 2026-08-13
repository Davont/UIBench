# Music Search History

## 基本信息

| 字段 | 内容 |
|---|---|
| Block ID | `music-search-history` |
| Block 名称 | music search history |
| Pixso 来源 | https://pixso.cn/app/design/KXylddm-EMqGBCzGr6ZZgQ?item-id=100:59860 |
| 源码 | `src/blocks/music-search-history/music-search-history.tsx` |
| Storybook | `src/blocks/music-search-history/music-search-history.stories.tsx` |

## 使用场景

`music search history` 是音乐搜索页中的搜索历史区域。Block 自身不带有色背板，承接所在页面背景；内部展示标题、清空入口、横向历史词条和展开入口。设计稿中的历史词条为纯展示 Chip，不包含关闭图标。

## 结构

| 区域 | 说明 |
|---|---|
| 根容器 | Pixso DSL `#illustration_编组 2`，`328×88`，无 `fillPaints` / 无有色背板 |
| 标题 | SubHeader 实例内文案「搜索历史」，坐标 `left=0 top=24`，`18px Bold` |
| 历史词条 | DSL `搜索历史` 分组，`328×28`，坐标 `left=0 top=60`；复用 `Chips`，`icon=false`、`Close=false` |
| 清空入口 | DSL `Public/ic_public_delete`，`24×24`，坐标 `left=304 top=24`，颜色 `rgba(0,0,0,0.6)` |
| 展开入口 | DSL `Button / Public/ic_public_arrow_down_0`，圆形按钮 `28×28`，坐标 `left=300 top=60`，底色 `rgba(0,0,0,0.05098)`，图标色 `rgba(0,0,0,0.90196)` |

## Component 复用

| 资源 | 用法 |
|---|---|
| `Chips` | 搜索历史词条，纯展示胶囊态，不显示前置图标或关闭图标 |
| `HMSymbolIcon` | 清空图标使用 `trash`，展开图标使用 `chevron_down`，映射 Pixso symbol |

## Props

| Prop | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `标题` | `string` | `"搜索历史"` | 区域标题 |
| `历史记录` | `MusicSearchHistoryItem[]` | `[]` | 搜索历史词条 |
| `显示标题` | `boolean` | `true` | 是否显示标题 |
| `显示展开` | `boolean` | `true` | 是否显示右侧展开按钮 |
| `on历史点击` | `(item) => void` | `undefined` | 点击历史词条回调 |
| `on清空点击` | `() => void` | `undefined` | 点击右上角清空按钮回调 |
| `on展开点击` | `() => void` | `undefined` | 点击右侧展开按钮回调 |

## Storybook 审查点

- `Playground`：标题 + 历史 Chips 的默认可审查状态。
- `EmptyState`：无词条空态。
- `LongHistory`：较多历史词条的横向滚动状态。

## DSL 对齐记录

- MCP: `get_node_dsl(guid=100:59860, clientFrameworks=react)` 与 `get_screenshot(guid=100:59860)`。
- 根节点 `#illustration_编组 2` 没有 `fillPaints`，因此实现为透明背景；`#EFEFEF/#F1F3F5` 等页面底色必须由父页面提供。
- 原手写 SVG 已替换为 `HMSymbolIcon`：`Public/ic_public_delete` -> `trash`，`Public/ic_public_arrow_down_0` -> `chevron_down`。
