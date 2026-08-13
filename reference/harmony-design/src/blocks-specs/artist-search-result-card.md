# Artist Search Result Card

## Metadata

| 字段 | 内容 |
|---|---|
| Block ID | `artist-search-result-card` |
| Block 名称 | Artist Search Result Card |
| Pixso 来源 | https://pixso.cn/app/design/KXylddm-EMqGBCzGr6ZZgQ?item-id=138:53 |
| item-id | `138:53` |
| 源码 | `src/blocks/artist-search-result-card/artist-search-result-card.tsx` |
| 样式 | `src/blocks/artist-search-result-card/artist-search-result-card.css` |
| 变体树 JSON | `src/blocks/artist-search-result-card/artist-search-result-card.json` |
| Storybook | `src/blocks/artist-search-result-card/artist-search-result-card.stories.tsx` |

## Pixso MCP 取数记录

| MCP 调用 | 结果 |
|---|---|
| `take_screenshot(nodeId=138:53)` | 成功，早期截图仅覆盖封面组；后续按用户提供的完整设计截图补齐文字层 |
| `design_to_code(clientFrameworks=react, guids=[138:53])` | 成功，返回 `Frame_138_53`、`List`、`Viewsdivider` 代码与样式清单 |
| `get_screenshot(clientFrameworks=react, guid=138:53)` | 成功，但 Pixso 返回截图只包含封面/头像层，未包含用户截图中的文字层 |
| `get_node_dsl(clientFrameworks=react, guid=138:53)` | 成功，提取到 `320×72` 歌手卡、`104×104` 封面卡、字体与色值信息 |

> 降级说明：Pixso 截图仍缺失完整文字层。本次以 DSL / design_to_code 的量化结构为主，结合用户提供的完整设计稿截图补齐 `搜索结果歌手卡`、艺人名、统计文案与封面标题层。

## 组成与用途

`Artist Search Result Card` 是音乐搜索中艺人结果的横向作品组：Block 自身无背板颜色，包含艺人头像、艺人名称、歌曲/专辑统计、歌单/专辑封面卡片、播放量与作品标题。

## 复用 Component

| 用途 | 复用资源 |
|---|---|
| 封面右上角“歌单/专辑”标签 | `Badge` |
| 播放量左侧播放图标 | `HMSymbolIcon name="play_fill"` |

## 量化规格

| 元素 | 规格 |
|---|---|
| 根节点 | `656×242`，背景透明 / 无背板，overflow hidden；覆盖两张 `320×72` 歌手卡与 `440×146` 横向作品组 |
| 顶部说明 | `搜索结果歌手卡`，`13px/18px`，颜色 `#b6b6b6` |
| 头像 | `48×48`，圆形；左头像 `x=0 y=36`，右头像 `x=336 y=36`；右头像左边界与第 4 张 album 左边界对齐 |
| 艺人名称 | 左侧 `歌手： ROSÉ`，右侧 `Bruno Mars`，`16px/21px`，Medium，颜色 `rgba(0,0,0,.898)` |
| 艺人统计 | `歌曲: 491 | 专辑: 37`，`12px/16px`，颜色 `rgba(0,0,0,.4)`，分隔符按截图合并为文本 |
| 作品行 | `top=96px`，横向 flex，gap `8px`；与头像底部距离 `12px`，对应 DSL `组合 1 top=72` 与 avatar `top=12 height=48` 的 `72 - (12 + 48) = 12` |
| 封面卡片 | `104×104`，圆角 `8px` |
| 封面蒙层 | 底部 `40px`，线性渐变 `transparent → rgba(0,0,0,.4)` |
| 类型标签 | 复用 `Badge`，`28×16`，右上角 `x=74 y=2`，`10px/14px` Medium，圆角 `2px 6px 2px 6px`，背景 `rgba(255,255,255,.3)` 叠加 `rgba(0,0,0,.3)` |
| 播放量 | 左下角 `x=4 y=80`，图标 `20×20`，文字 `10px/14px`，白色 |
| 作品标题 | 封面下方 `4px`，`14px/19px`，颜色 `rgba(0,0,0,.898)`，最多 2 行 |

## Props

| Prop | 类型 | 默认值 |
|---|---|---|
| `左侧头像` | `string` | `assets/avatar1.png` |
| `右侧头像` | `string` | `assets/avatar2.png` |
| `左侧艺人` | `ArtistSearchResultCardArtist` | `ROSÉ` / `歌曲: 491 | 专辑: 37` |
| `右侧艺人` | `ArtistSearchResultCardArtist` | `Bruno Mars` / `歌曲: 491 | 专辑: 37` |
| `作品列表` | `ArtistSearchResultCardAlbum[]` | `album1-4` |
| `on作品点击` | `(item, index) => void` | `undefined` |

### `ArtistSearchResultCardArtist`

| 字段 | 类型 | 默认值 |
|---|---|---|
| `头像` | `string` | `assets/avatar1.png` / `assets/avatar2.png` |
| `名称` | `string` | `ROSÉ` / `Bruno Mars` |
| `前缀` | `string` | 左侧 `歌手：`，右侧为空 |
| `歌曲数` | `string` | `491` |
| `专辑数` | `string` | `37` |

### `ArtistSearchResultCardAlbum`

| 字段 | 类型 | 默认值 |
|---|---|---|
| `id` | `string` | `apt-left` 等 |
| `图片` | `string` | `assets/album1.png` 等 |
| `类型标签` | `string` | `歌单` / `专辑` |
| `播放量` | `string` | `234万` |
| `标题` | `string` | `不要睡了起来嗨 APT.APT.` / `ROSE《rosie》` / `KPOP嗨起来的洗脑节奏` / `不要睡了起来嗨 APT....` |

## 取舍说明

- 上一版误按 `141:121` 还原为艺人信息行；本版已改回用户指定的 `138:53` 横向作品组。
- 根节点不绘制黑色背板；Pixso 截图中的黑色仅作为画布/预览环境，不作为 Block 背景实现。
- 上一轮实现漏掉设计稿中的文字层，本轮已按用户补充截图恢复：`搜索结果歌手卡`、艺人名、统计文案和封面标题。
- 2026-06-30 复核时，`get_node_dsl` 已成功返回；本轮把上一版过大的艺人文字、统计文字、封面标题、标签与播放量改回 DSL 字阶，并把作品行上移到接近用户设计截图的位置。
- 2026-06-30 二次复核时，根据 DSL 明确修正作品行与头像底部的纵向距离为 `12px`：本地 avatar `top=36 height=48`，作品行 `top=96`。
- 2026-06-30 三次复核时，根据 DSL `右侧歌手卡 left=336` 与第 4 张 album `left=336`，修正右侧 avatar `x=336`、右侧文字 `x=396`，保证两者左边界对齐。
- 2026-06-30 四次复核时，根据 DSL `组合 6` 修正 album 角标：`28×16`、`top=2 left=74`、`padding=1px 4px`、圆角 `2px 6px 2px 6px`、白色 30% 与黑色 30% 叠层背景。
- Pixso `get_screenshot` 本轮仍只返回封面/头像层，缺失完整文字层，因此文字可见性仍以用户提供的完整设计截图作为补充真值。
