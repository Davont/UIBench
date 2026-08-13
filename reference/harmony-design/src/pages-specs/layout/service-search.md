# Page Spec: service-search

> 别名：`ServiceSearch`、`servicessearch`。云服务应用搜索场景模板，适用于视频、应用市场、音乐、游戏、主题、阅读、云空间、查找、浏览器等云服务 APP 的搜索，以及同类搜索前/搜索中/搜索结果页。

## source

- Pixso search-before: https://pixso.cn/app/design/KXylddm-EMqGBCzGr6ZZgQ?item-id=36:45118
- Pixso search-in/result: https://pixso.cn/app/design/KXylddm-EMqGBCzGr6ZZgQ?item-id=36:45082
- Pixso search-completed/result composition: https://pixso.cn/app/design/KXylddm-EMqGBCzGr6ZZgQ?item-id=36:45193
- Pixso DSL: `get_node_dsl(guid=36:45118, clientFrameworks=react)`
- Pixso completed DSL: `get_node_dsl(guid=36:45193, clientFrameworks=react)`; root `#illustration_搜索结果-多个歌手多卡-可横滑`, `FRAME 360×792`, fixed `StatusBar 360×36 @0,0`, `SearchSecondPagePhone 328×40 @16,36`, bottom minibar group `328×56 @16,708`.
- Pixso screenshot: `get_screenshot(guid=36:45118)`
- Pixso completed screenshot: `get_screenshot(guid=36:45193)` shows category chips, artist result card rail, completed song result list, and bottom MiniPlayer on the same fixed search shell.
- Search-in/result reference: user-provided Pixso screenshot for node `36:45082`; Pixso desktop `get_screenshot(guid=36:45082)` timed out during the 2026-06-29 spec update.
- Pixso design-to-code: `design_to_code(guid=36:45118)` returned 500 in MCP; implementation falls back to DSL geometry + screenshot verification.
- Root node (search-before): `搜索前` / `36:45118` / `FRAME 360×792`
- Root node (search-in/result): `36:45082` / `FRAME 720×1584` rendered as 360 logical px mobile canvas in this repo.
- Root node (search-completed/result): `#illustration_搜索结果-多个歌手多卡-可横滑` / `36:45193` / `FRAME 360×792`
- Root fill: `#F1F3F5` or `#EFEFEF`-family light neutral depending on source node; child Blocks must not add their own page backplate unless the Block spec requires it.
- Template implementation: `src/pages/service-search-template/service-search-template.tsx`
- Storybook: `Pages/service-search-template`

## hit_rules

- 命中关键词：`ServiceSearch`、`servicessearch`、`服务搜索`、`云服务搜索`、`搜索页`、`视频搜索`、`应用市场搜索`、`音乐搜索`、`游戏搜索`、`主题搜索`、`阅读搜索`、`云空间搜索`、`查找搜索`、`浏览器搜索`、`搜索中`、`搜索结果`、`搜索结果页`、`搜索完成`、`搜索完成态`、`completed-results`、`综合`、`分类胶囊`、`歌手卡片`、`多歌手多卡`、`播放全部`、`在线搜索`
- 内容特征：固定顶部搜索壳层；搜索前为搜索历史、搜索建议、热搜榜/新歌榜/榜单 rail、底部导航；搜索中/结果态为播放全部操作行、结果列表、在线搜索 CTA、MiniPlayer；搜索完成态为分类 chips、歌手卡片横滑 rail、歌曲完成结果列表、MiniPlayer。
- Pixso 特征：`SearchSecondPagePhone`、`#illustration_编组 2`、`#illustration_新歌榜`、`minibar56`。

## exclusion_rules

- 明确是首页/服务首页/频道首页时优先 `services-home`。
- 明确是设置页时优先 `mobile-settings` 或 `settings-context-list`。
- 明确是纯列表、详情页、后台管理或表单页时不要命中本 page type。

## reference_blocks

| Resource | Path | Pixso mapping | Usage |
|---|---|---|---|
| `MusicSearchHistory` | `src/blocks/music-search-history` | `#illustration_编组 2` / `36:45121` / `328×88 @16,92` | SearchHistorySlot 默认 Block |
| `TopSongs` | `src/blocks/top-songs` | `#illustration_新歌榜` / `36:45129` 与 `#illustration_新歌榜备份` / `36:45155` | RankingRailSlot 默认双榜单 |
| `IconButton + Search` | `src/components/IconButton`, `src/components/Search` | `SearchSecondPagePhone` / `36:45187` / `328×40 @16,36` | SearchSlot 默认返回按钮 + 搜索框 |
| `StatusBar` | `src/components/StatusBar` | `Color Mode=Light` / `36:45120` / `360×36 @0,0` | StatusBarSlot |
| `FloatingTab` | `src/components/Navigation/FloatingTab` | `tab` / `36:45191`，内部 `minibar56` / `36:45192`，以及 bottom safe area | BottomNavSlot / MiniPlayerSlot，默认使用 `数量="1+bar"` 变体 |
| `MusicSearchingResultList` | `src/blocks/music-searching-result-list` | result list in `36:45082` / related node `122:59411` | ResultListSlot 默认 Block |
| `FloatingSearchSecondPagePhone` | `src/components/Input/FloatingSearchSecondPagePhone` | result search shell in `36:45082` | SearchSlot 默认搜索中壳层 |
| `FloatingChipsTabPhone` | `src/components/Navigation/FloatingChipsTabPhone` | category chips in `36:45193` | CategoryTabsSlot 默认分类 tabs |
| `ArtistSearchResultCard` | `src/blocks/artist-search-result-card` | artist result rail in `36:45193` | ArtistCardSlot 默认歌手卡片横滑 rail |
| `MusicSearchCompletedResultList` | `src/blocks/music-search-completed-result-list` | song result list in `36:45193` | CompletedResultListSlot 默认歌曲结果列表 |

## composition_modes

| Mode | Scenario | Fixed page-type regions | Replaceable content regions | Default visible slots |
|---|---|---|---|---|
| `pre-search` | 搜索前，未输入或尚未提交查询 | status bar、顶部搜索壳层、底部浮动导航锚点 | history、ranking rail、bottom nav content | `statusBarSlot`、`searchSlot`、`historySlot`、`rankingRailSlot`、`bottomNavSlot` |
| `in-search` | 搜索中/搜索结果，已输入关键词（如 `周杰伦`） | status bar、顶部搜索壳层、底部浮层锚点 | play all action、result list、online search CTA、mini player | `statusBarSlot`、`searchSlot`、`resultActionSlot`、`resultListSlot`、`onlineSearchSlot`、`miniPlayerSlot` |
| `completed-results` | 搜索完成后的多 Block 结果页（如 `APT`） | status bar、顶部搜索壳层、底部浮层锚点 | category tabs、artist-card rail、completed song result list、mini player | `statusBarSlot`、`searchSlot`、`categoryTabsSlot`、`artistCardSlot`、`completedResultListSlot`、`miniPlayerSlot` |

`service-search` 的固定部分是页面壳层位置关系：顶部状态栏 + 搜索框区域，以及底部浮层锚点。除这些固定锚点外，正文 Block 均可替换；搜索前、搜索中、搜索完成结果页只是同一个 page type 的不同组合形式。

## layout_skeleton

```html
<main data-page-type="service-search">
  <section data-slot="statusBarSlot"></section>
  <section data-slot="searchSlot"></section>
  <section data-mode="pre-search">
    <section data-slot="historySlot"></section>
    <section data-slot="rankingRailSlot"></section>
    <footer data-slot="bottomNavSlot"></footer>
  </section>
  <section data-mode="in-search">
    <section data-slot="resultActionSlot"></section>
    <section data-slot="resultListSlot"></section>
    <section data-slot="onlineSearchSlot"></section>
    <footer data-slot="miniPlayerSlot"></footer>
  </section>
  <section data-mode="completed-results">
    <section data-slot="categoryTabsSlot"></section>
    <section data-slot="artistCardSlot"></section>
    <section data-slot="completedResultListSlot"></section>
    <footer data-slot="miniPlayerSlot"></footer>
  </section>
</main>
```

## slots

| Slot | Default | Replaceable | Visibility prop | Notes |
|---|---|---|---|---|
| `statusBarSlot` | `StatusBar Color Mode=Light` | status-bar / none | `showStatusBar` | 固定 `360×36 @0,0` |
| `searchSlot` | `IconButton + Search` | `Search` / `FloatingSearchPhone` / custom search / none | `showSearchBar` | 默认 `328×40 @16,36`，返回按钮 `40×40`，搜索框 `280×40` |
| `historySlot` | `MusicSearchHistory` | `music-search-history` / custom chips history / none | `showSearchHistory` | 默认 `328×88 @16,92`，必须使用刚注入的 Block |
| `rankingRailSlot` | two `TopSongs` cards | `top-songs` / ranking-list / recommendation rail / none | `showRankingRail` | 默认左卡 `244×856 @16,196`，右卡 `244×856 @268,196`，允许被 360px 画布裁切 |
| `bottomNavSlot` | `FloatingTab 数量="1+bar"` | floating-tab music variant / custom player bar / none | `showBottomNav` | 搜索前底部浮层；默认底部渐变 `360×96 @0,696`，外层 `tab` 为 `328×56 @16,708`，实际 `minibar56` 为 `280×56 @16,708`；FloatingTab 已包含底部手势指示条，不得额外叠加 Aibottombar |
| `categoryTabsSlot` | `FloatingChipsTabPhone` | category chips / custom filters / none | `showCategoryTabs` | 搜索完成态专用；默认位于 `328×44 @16,92`，可横向滚动，默认 `综合/歌曲/歌单/歌手/专辑`；腰部胶囊组高 `44px`，单个按钮按 Pixso DSL 还原为 `76×28`、间距 `8px`，并在组内垂直居中；搜索框底部到胶囊按钮顶部为 `16px` |
| `artistCardSlot` | `ArtistSearchResultCard` | artist card rail / custom artist result block / none | `showArtistCard` | 搜索完成态专用；复用 `artist-search-result-card` 原尺寸 `656×242`，在 page type 中作为横向 rail 拼接 |
| `completedResultListSlot` | `MusicSearchCompletedResultList` | completed music list / service-specific result block / none | `showCompletedResultList` | 搜索完成态专用；复用 `music-search-completed-result-list`，从歌手卡片下方承接 |
| `resultActionSlot` | play all row (`播放全部`) | action row / toolbar / none | `showResultAction` | 搜索中模式专用；位于搜索壳层下方，包含左侧粉色播放 icon + `播放全部` 文案，右侧列表/排序 symbol |
| `resultListSlot` | `MusicSearchingResultList` | `music-searching-result-list` / service-specific result list / none | `showResultList` | 搜索中模式专用；默认承接 `122:59411` 音乐结果列表，无额外背板，列表可被底部浮层遮罩但行内容不能被硬截断 |
| `onlineSearchSlot` | pill CTA (`试试在线搜索`) | online-search CTA / none | `showOnlineSearch` | 搜索中模式专用；底部浮动胶囊按钮，位于 MiniPlayer 上方，颜色使用品牌粉色文字 |
| `miniPlayerSlot` | `FloatingTab 数量="1+bar"` | floating-tab music variant / custom playback bar / none | `showMiniPlayer` | 搜索中/搜索完成态底部音乐播放条；复用 `FloatingTab` 的 `1+bar` 变体（左侧圆形 tab + 右侧音乐胶囊 + 内置底部手势指示条），和 `bottomNavSlot` 互斥 |

## visibility_model

| Prop | Type | Default | Applies to | Notes |
|---|---|---:|---|---|
| `mode` | `"pre-search" \| "in-search" \| "completed-results"` | `"pre-search"` | page | 控制默认 slot 组合。`pre-search` 显示历史/榜单/底部导航；`in-search` 显示播放全部/结果列表/在线搜索/MiniPlayer；`completed-results` 显示分类 tabs/歌手卡片/完成结果列表/MiniPlayer。 |
| `showStatusBar` | `boolean` | `true` | both modes | 固定顶部系统状态栏。 |
| `showSearchBar` | `boolean` | `true` | both modes | 固定顶部搜索壳层。 |
| `showSearchHistory` | `boolean` | `mode === "pre-search"` | pre-search | 搜索前历史区域。 |
| `showRankingRail` | `boolean` | `mode === "pre-search"` | pre-search | 搜索前榜单 rail。 |
| `showBottomNav` | `boolean` | `mode === "pre-search"` | pre-search | 搜索前底部导航/播放器组合；与 `showMiniPlayer` 必须互斥。 |
| `showCategoryTabs` | `boolean` | `mode === "completed-results"` | completed-results | 搜索完成态分类 tabs。 |
| `showArtistCard` | `boolean` | `mode === "completed-results"` | completed-results | 搜索完成态歌手卡片横滑 rail。 |
| `showCompletedResultList` | `boolean` | `mode === "completed-results"` | completed-results | 搜索完成态歌曲结果列表。 |
| `showResultAction` | `boolean` | `mode === "in-search"` | in-search | 搜索中播放全部工具行。 |
| `showResultList` | `boolean` | `mode === "in-search"` | in-search | 搜索结果列表。 |
| `showOnlineSearch` | `boolean` | `mode === "in-search"` | in-search | 在线搜索 CTA。 |
| `showMiniPlayer` | `boolean` | `mode === "in-search" \|\| mode === "completed-results"` | in-search / completed-results | 底部 FloatingTab music variant；与 `showBottomNav` 必须互斥。 |

## spatial_tokens

| Token | Value | Source |
|---|---:|---|
| screen width | `360px` | DSL root |
| screen height | `792px` | DSL root |
| screen fill | `#F1F3F5` | DSL root fill |
| horizontal inset | `16px` | Search/history/tab x |
| search top | `36px` | `36:45187` |
| history top | `92px` | `36:45121` |
| ranking top | `196px` | `36:45129` / `36:45155` |
| bottom overlay top | `696px` | `36:45188` |
| bottom tab top | `708px` | `36:45191` |
| result action top | `100px` approx | `36:45082` screenshot |
| result list top | `150px` approx | `36:45082` screenshot |
| completed category tabs top | `92px` | `36:45193` screenshot |
| completed category tabs size | `328×44px` | `36:45193` DSL |
| completed category chip size | `76×28px`, gap `8px` | `36:45193` DSL |
| search bottom to category chip top | `16px` | `36:45193` screenshot |
| completed artist card top | `112px` page slot / unscaled rail | `36:45193` screenshot + `ArtistSearchResultCard` block |
| completed result list top | `364px` | `36:45193` screenshot |
| online search CTA bottom | above mini player | `36:45082` screenshot |
| mini player bottom | `84px` slot anchored to bottom `0` | `FloatingTab` `1+bar` variant includes `56px` music row + `28px` internal gesture indicator |

## composition_mapping

- SearchSlot maps Pixso `实例 12` (`SearchSecondPagePhone`) to repository `IconButton + Search`.
- SearchHistorySlot maps Pixso `#illustration_编组 2` to `MusicSearchHistory`; no ad hoc chip DOM should be handwritten.
- RankingRailSlot maps Pixso two `#illustration_新歌榜*` groups to two `TopSongs` blocks. The rail width exceeds the viewport; the page shell clips horizontally.
- BottomNavSlot maps Pixso `tab` / `minibar56` + `组合 30079` to `FloatingTab 数量="1+bar"` with a page-level gradient overlay. The FloatingTab is self-contained and must not be paired with an extra Aibottombar.
- The `miniPlayerSlot` reuses `FloatingTab` with `数量="1+bar"` so the bottom player uses the design-system FloatingTab music variant instead of a page-local handwritten player.
- In `in-search` mode, ResultListSlot maps to `MusicSearchingResultList`; the list Block keeps its own item typography, divider, VIP/spatial tags, `#FF1949` artist color, and HM Symbols.
- In `in-search` mode, OnlineSearchSlot and MiniPlayerSlot are bottom overlays. They must not force the result list to shrink to an artificial viewport height; leave enough bottom padding or overlay clearance so the last visible row is not clipped by Storybook controls or the MiniPlayer.
- In `completed-results` mode, CategoryTabsSlot maps to `FloatingChipsTabPhone`, ArtistCardSlot maps to `ArtistSearchResultCard`, and CompletedResultListSlot maps to `MusicSearchCompletedResultList`. These are replaceable content slots; do not rebuild the card/list rows directly inside the page template.
- The `completed-results` mode represents Pixso node `36:45193`: fixed shell remains status/search/miniplayer anchoring, while the body combines category filters, artist result rail, and completed song list for a search-result scenario.

## adaptive_behavior

- Default target is a fixed mobile canvas `360×792`; Pixso result state `720×1584` is scaled to the same 360 logical px layout.
- Horizontal ranking rail is intentionally wider than the viewport; do not shrink cards to fit.
- Hidden slots do not reserve blank space unless a replacement slot explicitly requests the same coordinates.
- Search/history/top ranking coordinates are absolute to preserve Pixso DSL geometry.
- In `in-search` mode, the result list can scroll under bottom overlays, but list rows, right-side symbols, and separators must remain complete. Do not crop the last row to satisfy a fixed Storybook viewport.
- In `completed-results` mode, artist card content can horizontally exceed the 360px screen and be clipped by the shell; do not squeeze the card rail to fit the viewport.

## generation_constraints

- Do not render the Pixso page as one flat image.
- Do not duplicate `MusicSearchHistory` with temporary chip markup; use the Block resource.
- Do not hand-roll the two ranking cards when `TopSongs` is available.
- Do not hand-roll the music result rows when `MusicSearchingResultList` is available.
- Do not hand-roll the search-completed artist card or completed song rows when `ArtistSearchResultCard` and `MusicSearchCompletedResultList` are available.
- When applying this page type to games or reading, keep the shell and slots but replace content labels/items through props or slot replacement.
- `bottomNavSlot` and `miniPlayerSlot` are mutually exclusive bottom layers. Generation must not pass both `showBottomNav={true}` and `showMiniPlayer={true}`; if a caller supplies both, treat `miniPlayerSlot` as taking precedence in search/result modes and hide `bottomNavSlot`, unless a custom product spec explicitly asks for two bottom layers.
- `src/pages/` templates are treated as stable page type sources. If implementation slots need to be added, add them in the template through the page-generation workflow and keep the same data-slot names defined here.

## validation_notes

- Real prompt smoke test:
  - Prompt: `生成一个音乐 app 的搜索页，包含搜索历史、新歌榜、热歌榜和底部导航。`
  - Expected route: `service-search`
  - Match reason: contains `音乐 app`, `搜索页`, `搜索历史`, `新歌榜`, `热歌榜`.
- Template slot coverage checked in `src/pages/service-search-template/service-search-template.tsx`: `searchSlot`, `historySlot`, `rankingRailSlot`, `bottomNavSlot`, plus `showSearchBar`, `showSearchHistory`, `showRankingRail`, `showBottomNav`, `showStatusBar`.
- Default `searchSlot` now uses `FloatingSearchSecondPagePhone` for Pixso node `36:45118` search-before state. Pixso MCP rerun: `get_screenshot` and `get_node_dsl` succeeded; `design_to_code(react)` returned 500; `get_variants` returned `{}`. DSL node `36:45187` confirms `width=328 height=40`, `Left icon=true`, `Right icon=false`; in the template the slot is placed at `top=44` so its y-axis gap from the `36px` `StatusBar` is `8px`.
- 2026-06-29 implementation audit: `src/pages/service-search-template/service-search-template.tsx` now supports both `pre-search` and `in-search` modes. The in-search mode adds `mode`, `resultActionSlot`, `resultListSlot`, `onlineSearchSlot`, `miniPlayerSlot`, `showResultAction`, `showResultList`, `showOnlineSearch`, and `showMiniPlayer`.
- Storybook coverage: `Pages/service-search-template--default` keeps the search-before composition; `Pages/service-search-template--in-search` renders the Pixso `36:45082` search-in/result composition with `MusicSearchingResultList`.
- 2026-06-30 implementation audit: `src/pages/service-search-template/service-search-template.tsx` adds `completed-results` mode for Pixso `36:45193`, with `categoryTabsSlot`, `artistCardSlot`, `completedResultListSlot`, `showCategoryTabs`, `showArtistCard`, and `showCompletedResultList`.
- Storybook coverage: `Pages/service-search-template--completed-results` renders the Pixso `36:45193` search-completed composition with `FloatingChipsTabPhone`, `ArtistSearchResultCard`, `MusicSearchCompletedResultList`, and MiniPlayer.
- 2026-06-30 category/artist rail correction: waist chip group in `completed-results` is fixed to `328×44px @16,92`; chips are `76×28px` with `8px` rail gap per Pixso DSL, centered inside the group, with `16px` from search bottom to chip top. ArtistCardSlot uses the unscaled `ArtistSearchResultCard` rail at `top=112px`.
- 2026-06-30 bottom player correction: `miniPlayerSlot` default was replaced with `FloatingTab 数量="1+bar"` to match the FloatingTab music variant requested for the bottom tab area.
