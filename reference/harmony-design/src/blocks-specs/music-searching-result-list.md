# Music Searching Result List

## 基本信息

| 字段 | 内容 |
|---|---|
| Block ID | `music-searching-result-list` |
| Block 名称 | Music Searching Result List |
| Pixso 来源 | https://pixso.cn/app/design/KXylddm-EMqGBCzGr6ZZgQ?item-id=122:59244 |
| item-id | `122:59244` |
| 源码 | `src/blocks/music-searching-result-list/music-searching-result-list.tsx` |
| 样式 | `src/blocks/music-searching-result-list/music-searching-result-list.css` |
| 变体树 JSON | `src/blocks/music-searching-result-list/music-searching-result-list.json` |
| Storybook | `src/blocks/music-searching-result-list/music-searching-result-list.stories.tsx` |

## Pixso MCP 取数记录

| MCP 调用 | 结果 |
|---|---|
| `design_to_code(clientFrameworks=react, guids=[122:59244])` | 超时，300s 未返回 |
| `take_screenshot(nodeId=122:59244)` | 成功，`image/png`；按用户对比原图采用有效可视裁切 `360×640`，Block 自身无背板色 |
| `get_node_dsl(clientFrameworks=react, guid=122:59244)` | 超时，300s 未返回 |
| `get_screenshot(clientFrameworks=react, guid=138:35)` | 超时，300s 未返回 |
| `get_node_dsl(clientFrameworks=react, guid=138:35)` | 超时，300s 未返回 |
| `get_screenshot(clientFrameworks=react, guid=138:131)` | 超时，300s 未返回 |
| `get_node_dsl(clientFrameworks=react, guid=138:131)` | 超时，300s 未返回 |
| `get_screenshot(clientFrameworks=react, guid=122:59411)` | 超时，300s 未返回 |
| `get_node_dsl(clientFrameworks=react, guid=122:59411)` | 超时，300s 未返回 |

> 降级说明：本次结构化 DSL 未取回；整组结构以 `122:59244` 为来源，单行字体大小、粗细、颜色按用户提供的子单元 `138:35` 截图降级量化还原，两个徽标按用户提供的标签节点 `138:131` 截图降级量化还原。

## 用途与边界

`Music Searching Result List` 是音乐搜索页结果区域的无背板裁切态 Block。节点 `122:59244` 的可见内容是 10 条歌曲结果：歌曲名、金色 `VIP` 标签、金色 `空间音频` 标签、`#FF1949` 的 `周杰伦`、灰色副标题、右侧 Huawei HarmonyOS Symbol `heart` / `dot_grid_1x2`，以及每行底部分割线。

Block 不包含搜索栏、底部播放器、页面容器或额外导航区域。

## Pixso 可见结构

| 节点/元素 | 量化 | 实现映射 |
|---|---|---|
| 根蒙版 | `360×678`，透明背景，clip hidden，完整露出 10 行 | `.music-searching-result-list` |
| 行组 | left `16px`，top `18px`，宽 `328px` | `.music-searching-result-list__rows` |
| 行 ×10 | 每行 `328×66`，垂直步进 `66px` | `.music-searching-result-list__row:nth-child(n)` |
| 歌名 | `16px/22px`，bold，黑色主文字 | `.music-searching-result-list__song-name` |
| VIP 标签 | `24×16`，圆角 `4px`，背景 `20% #C79E63`，文字 `#806540`，`10px/16px` bold | `.music-searching-result-list__vip` |
| 空间音频标签 | `48×16`，圆角 `4px`，背景 `20% #C79E63`，文字 `#806540`，`10px/16px` bold | `.music-searching-result-list__spatial` |
| 歌手 | `周杰伦`，`12px/16px`，regular，`#FF1949` | `.music-searching-result-list__artist` |
| 副标题 | `12px/16px`，灰色，跟随 `-` 连接 | `.music-searching-result-list__subtitle` |
| 右侧 symbol | Huawei HarmonyOS Symbol `heart` + `dot_grid_1x2`，均为 `20×20`，灰色，右对齐 | `.music-searching-result-list__actions` |
| 行分割线 | `1px` 高，`rgba(0, 0, 0, 0.16)` | `.music-searching-result-list__divider` |

## Props

| Prop | 类型 | 默认值 | DSL/截图对齐 |
|---|---|---|---|
| `结果列表` | `MusicSearchingResultListItem[]` | 10 条歌曲结果示例 | 对齐截图中 10 条搜索结果 |
| `on结果点击` | `(item) => void` | `undefined` | 业务扩展，不影响默认视觉 |

### `MusicSearchingResultListItem`

| 字段 | 类型 | 默认/截图值 |
|---|---|---|
| `id` | `string` | `row-1` 至 `row-10` |
| `歌名` | `string` | `不能说的秘密`、`Mojito（莫吉托）`、`错过的烟火`、`说好不哭`、`等你下课` |
| `VIP标签` | `string` | `VIP` |
| `音效标签` | `string` | `空间音频` |
| `歌手` | `string` | `周杰伦` |
| `副标题` | `string` | `不能说的秘密`、`Mojito`、`最伟大的作品` 等 |

## 样式引用

- 复用 `Badge` 组件作为徽标承载。
- 右侧图标复用 `HMSymbolIcon`，名称经 `node skills/01-resource-injection/shadcn/scripts/search-hmsymbol.mjs heart` 与 `node skills/01-resource-injection/shadcn/scripts/search-hmsymbol.mjs dot_grid_1x2` 确认存在。
- 本次未新增 `src/styles/global.css` token。
- Pixso 特定色值在 block CSS 局部落地：`rgba(199, 158, 99, 0.2)`、`#806540`、`#FF1949`、`#8e8e93`；Block 根节点和裁切层均不设置背板色。

## 取舍说明

- `122:59244`、子单元 `138:35`、标签节点 `138:131` 与未截断列表节点 `122:59411` 的 DSL/截图工具存在超时，因此无法记录完整 DSL 字段路径；已在 `music-searching-result-list.json` 中标注 fallback。
- 歌曲名、右侧心形/更多 symbol 与分割线依据用户标注截图补齐。
- 单行字体大小、字重和颜色以用户提供的 `138:35` 子单元截图为准。
- VIP / 空间音频两个徽标以用户提供的 `138:131` 标签截图为准。
- 行宽 `328px` 覆盖左侧文本区和右侧操作区；根节点按 `122:59411` 未截断状态扩展为 `360×678` 透明裁切，使第 10 行 `top=594px`、`height=66px` 在行组 `top=18px` 后完整露出。
