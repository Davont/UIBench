# Music Search Completed Result List

## Metadata

| 字段 | 值 |
| --- | --- |
| Block ID | `music-search-completed-result-list` |
| Block 名称 | Music Search Completed Result List |
| Pixso 来源 | `https://pixso.cn/app/design/KXylddm-EMqGBCzGr6ZZgQ?item-id=143:59576` |
| item-id | `143:59576` |
| 源码 | `src/blocks/music-search-completed-result-list/music-search-completed-result-list.tsx` |
| 样式 | `src/blocks/music-search-completed-result-list/music-search-completed-result-list.css` |
| 变体树 JSON | `src/blocks/music-search-completed-result-list/music-search-completed-result-list.json` |
| Storybook | `src/blocks/music-search-completed-result-list/music-search-completed-result-list.stories.tsx` |

## MCP 调用

| 工具 | 结果 |
| --- | --- |
| `design_to_code(clientFrameworks=react, guids=[143:59576])` | 成功，返回 `Frame_143_59576`、`List`、`Component_2_65668`、标签与 Divider 等结构草案 |
| `get_screenshot(clientFrameworks=react, guid=143:59576)` | 成功，作为视觉真值截图 |
| `get_node_dsl(clientFrameworks=react, guid=143:59576)` | 成功，根节点 `music search completed result list`，尺寸 `328×450` |

## 组成与用途

`MusicSearchCompletedResultList` 是音乐搜索完成态歌曲列表 Block。它包含顶部“歌曲 + 播放”入口，以及 6 条歌曲结果，其中首条为展开态，显示“更多版本 5”。

复用资源：

| 设计元素 | 仓库资源 |
| --- | --- |
| VIP / 原唱标签 | `Badge` (`src/components/Views/Badge`) |
| 播放、列表添加、更多、展开图标 | `HMSymbolIcon` (`src/components/HMSymbolIcon`) |
| 行容器 / 列表结构 | Block 层按 DSL 组合，不创建临时相似组件 |

## 量化规格

| 项 | Pixso / DSL | 实现 |
| --- | --- | --- |
| 根节点 | `328×450`，透明背景，纵向 auto layout | `.music-search-completed-result-list` |
| 顶部播放区 | `328×48`，padding `12 0 4`，标题 `18px`，播放入口外层圆形背板 `32×32`，内部 `play_fill` symbol `18×18` | `__header`, `__title`, `__play-all`, `__play-symbol` |
| 列表区域 | `328×402`，位于顶部后方 | `__rows` |
| 普通行 | `328×64`，padding `12 0`，横向 gap `20` | `__row` |
| 展开行 | `328×83`，标题 + 标签行 + 更多版本行 | `__row--expanded` |
| 行坐标 | `top=0/82/146/210/274/338` | `nth-child` 绝对定位 |
| 主标题 | `16px/21px`，Medium；展开态 `#FF1949` | `__song` |
| 副信息 | `12px/16px`，tertiary | `__artist-album`, `__versions` |
| VIP 标签 | `24×16`，圆角 `4px`，背景 `rgba(199,158,99,.2)`，文字 `#806540`，`10px` Medium | `Badge` + `__vip` |
| 原唱标签 | `28×16`，圆角 `4px`，背景 `rgba(255,25,73,.1)`，文字 `#FF1949`，`10px` Medium | `Badge` + `__source` |
| 已下载图标 | 圆形背板 `16×16`；内部 symbol 对齐盒 `8.34×5.36`，`checkmark` 完整居中显示，颜色 `rgba(0,0,0,.4)` | `HMSymbolIcon checkmark` + `__downloaded` |
| 右侧操作 | `60×20`，两个 `20×20` symbol，gap `20` | `HMSymbolIcon plus_list/dot_grid_1x2` |
| 分割线 | `328×1`，底部，Light comp divider | `__divider` |

## Props

| Prop | 类型 | 默认值 | DSL 对齐 |
| --- | --- | --- | --- |
| `标题` | `string` | `"歌曲"` | `2:65670 nodeText` |
| `显示播放全部` | `boolean` | `true` | 顶部 `播放全部/搜索` 可见性 |
| `结果列表` | `MusicSearchCompletedResultListItem[]` | 6 条 Pixso 示例 | `list` 实例与展开态行实例 |
| `on播放全部` | `() => void` | `undefined` | 播放按钮交互扩展 |
| `on结果点击` | `(item) => void` | `undefined` | 行点击交互扩展 |

### `MusicSearchCompletedResultListItem`

| 字段 | 类型 | 默认示例 | DSL 对齐 |
| --- | --- | --- | --- |
| `歌名` | `string` | `APT` / `DDU-DU DDU-DU` | `2:68346`, `143:59666` |
| `歌手专辑` | `string` | `最伟大的作品 - 周杰伦` | `2:68350`, `143:59688` |
| `VIP标签` | `string` | `VIP` | `2:65698`, `2:65705` |
| `类型标签` | `string` | `原唱` | `2:65700`, `2:65750` |
| `已下载` | `boolean` | `true` | `2:65737` downloaded icon，映射为 `HMSymbolIcon checkmark` + 圆形弱背板 |
| `展开版本文案` | `string` | `更多版本 5` | `143:59690` |
| `展开` | `boolean` | `true` 首行 | `143:59660` 83px 展开态 |

## 样式引用

使用已有全局变量：

- `--harmony-font-primary`
- `--harmony-font-tertiary`
- `--harmony-icon-tertiary`
- `--harmony-comp-divider`
- `--harmony-comp-background-secondary`

新增全局变量：

| Token | Light | Dark | 来源 |
| --- | --- | --- | --- |
| `--harmony-music-search-brand` | `rgba(255,25,73,1)` | `rgba(255,25,73,1)` | Pixso `音乐品牌色` |
| `--harmony-music-search-brand-soft` | `rgba(255,25,73,.1)` | `rgba(255,25,73,.16)` | Pixso `音乐品牌色-标签bg` |
| `--harmony-music-vip-text` | `rgba(128,101,64,1)` | `rgba(228,191,136,1)` | Pixso VIP 文本 |
| `--harmony-music-vip-bg` | `rgba(199,158,99,.2)` | `rgba(199,158,99,.28)` | Pixso `会员色-背景-light` |

## 取舍说明

- Pixso 中 `#illustration_ic_lable_16/已下载` 对应 symbol 库 `checkmark`；实现复用 `HMSymbolIcon name="checkmark"`，外层为 `16×16` 圆形弱背板，内部用 `8.34×5.36` 对齐盒控制落位，但不裁切字体 glyph，避免 HM Symbol 字体边界与 Pixso SVG 路径坐标差异导致截断；颜色 `40% #000000` 并居中，不再用 CSS 绘制勾形。
- Pixso 右侧列表添加图标为 HM Symbol 私有码位 `F0156`，本地 symbol 名表未收录；在 `HMSymbolIcon` legacy alias 中补充 `plus_list` 后复用。
- Pixso 生成的 `List.tsx` 是临时导出组件；本实现未落入仓库组件层，而是在 Block 层组合现有 `Badge` 与 `HMSymbolIcon`，避免污染 `src/components`。
