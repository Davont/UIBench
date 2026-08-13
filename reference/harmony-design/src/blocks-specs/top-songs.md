# Top Songs

## 基本信息

| 字段 | 内容 |
|---|---|
| Block ID | `top-songs` |
| Block 名称 | Top Songs |
| Pixso 来源 | https://pixso.cn/app/design/KXylddm-EMqGBCzGr6ZZgQ?item-id=100:59786 |
| 源码 | `src/blocks/top-songs/top-songs.tsx` |
| Storybook | `src/blocks/top-songs/top-songs.stories.tsx` |

## 使用场景

`Top Songs` 是音乐首页或榜单页中的窄列歌曲排行榜卡片。它用于展示一个榜单名称、播放入口和 1 到 20 条歌曲排名。页面样例中该 Block 以两列并排出现，分别承载「新歌榜」和「热歌榜」。

## 结构

| 区域 | 说明 |
|---|---|
| 卡片容器 | 白色背景，圆角 16px，固定宽度 244px，高度 852px，超出裁切 |
| 标题区 | 左侧粗体榜单标题，右侧粉色圆形播放按钮 |
| 排名列表 | 纵向歌曲条目；前 3 名排名为品牌粉色，其余为灰色 |
| 状态标签 | 复用 `Badge` 组件，显示 `热` / `升` / `新` |

## Component 复用

| 资源 | 用法 |
|---|---|
| `Badge` | 歌曲标题后的单字状态标签 |

播放按钮没有复用 `IconButton`：现有 `IconButton` 是 Harmony 材质多按钮组，和设计稿中的单个粉色圆形播放入口不一致，因此作为 Block 内部结构实现。

## Props

| Prop | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `标题` | `string` | `"新歌榜"` | 榜单标题，例如「新歌榜」「热歌榜」 |
| `歌曲列表` | `TopSongsItem[]` | `[]` | 歌曲排名数据 |
| `on播放点击` | `() => void` | `undefined` | 播放按钮点击回调 |

### TopSongsItem

| 字段 | 类型 | 说明 |
|---|---|---|
| `排名` | `number` | 榜单排名 |
| `歌名` | `string` | 歌曲名称，长文本单行省略 |
| `标签` | `"hot" \| "up" \| "new"` | 可选状态标签，对应 `热` / `升` / `新` |

## Storybook 审查点

- `Playground`：并排展示「新歌榜」和「热歌榜」，对应页面样例。
- `NewSongs`：单张「新歌榜」卡片。
- `HotSongs`：单张「热歌榜」卡片。

## 实现备注

- 该版本按用户提供的页面样例截图重新抽取，替换上一版深色榜单组合实现。
- 截图按 2x 导出理解，单张卡片采用 244×852 CSS px；Storybook 中两张卡片间距为 8px。
- 列表容器固定高度并裁切，保持第 20 条在底部接近截图中的裁切状态。
