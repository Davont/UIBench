# Layout: services-ranking

> Page Type: Services Ranking. 云服务业务榜单模板，适用于阅读、视频、音乐、游戏、应用市场、主题、云空间&查找、浏览器等云服务类业务的排行榜页面。原始 Pixso source 为 `排行榜`，节点 `36:37008`，画布 `360 × 792`。

## hit_rules

命中 `services-ranking` 时，页面应同时满足以下特征：

- 用户明确要求排行榜、榜单页、视频排行、音乐排行、热度榜、电影榜或电视剧榜页面。
- 页面是移动端深色主题排名列表页，顶部为头图背景 + 金色标题插图（麦穗 + 主标题 + 描述文字）。
- 页面包含分类页签（ChipsTab）用于切换榜单类别，常见为综合榜/电视剧榜/电影榜/综艺榜。
- 排名列表为纵向卡片流，每项含排名序号、封面图、标题、演员/副标题、年份类型和追按钮。
- 存在底部 Aibottombar 指示条。
- Prompt 中出现 `MainChart03`、`主榜03`、`排名列表`、`RankingChipsTabPhone`、`麦穗`、`综合排行榜`、`金色标题` 等已登记 Block 或特征词时，应优先命中本 page type。

## exclusion_rules

- 仅为沉浸式 Hero Banner 首页、无排名列表 → 优先评估 `services-home`。
- 以宫格卡片为核心，非纵向排名列表 → 优先评估 `mobile-grid`。
- 以通用卡片流为核心，顶部无可替换头图 → 优先评估 `mobile-card`。
- 以入口列表、资产中心、个人中心列表为核心 → 优先评估 `mobile-list`。
- 设置 / 表单 / 后台管理 / 详情页 / 播放器页不命中本布局。
- 若页面只有单个 Block 展示，不构成完整榜单模板，则先抽取或复用 Block，不生成本 page type。

## implementation_details

- **导出项**：`ServicesRanking`（默认导出）、`ServicesRankingProps`、`DEFAULT_CHIPS_TABS`、`DEFAULT_RANKING_ITEMS`
- **用途**：榜单页面 — 深色主题纵向排名列表页，自上而下包含 StatusBar、TitleBar(排行榜)、**麦穗+金色标题插图** (Pixso 69:225)、ChipsTab 标签栏(4 页签)、排名列表(12 项)和 Aibottombar
- **复用组件**：
  - `StatusBar` (src/components/StatusBar/) — ColorModeDark
  - `TitleBar` (src/components/TitleBar/) — secondary-phone, 仅左右按钮无标题
  - `HMSymbolIcon` (src/components/HMSymbolIcon/) — 返回 chevron_left + 搜索 magnifyingglass
  - 麦穗 SVG 矢量 (src/blocks/ranking-topbanner/svg/) — 24×59px 矢量对
  - `ChartChipsTabPhone` (src/blocks/ranking-chipstab-phone/) — 360×64px, 4 页签
  - `MainChart03` (src/blocks/ranking-list/) — 360×auto 纵向排行榜
  - `Aibottombar` (src/components/Aibottombar/) — ColorModeDark

## reference_blocks

- `ranking-topbanner` — 默认 IllustrationSlot，用于金色标题插图区域（麦穗 SVG 矢量对 + 思源宋体主标题 + 描述文字）；对应 Pixso 节点 `36:37010` / `69:225`。
- `ranking-chipstab-phone` — 默认 ChipsTabSlot，用于榜单分类页签切换（4 页签：综合榜/电视剧榜/电影榜/综艺榜）；对应 Pixso 节点 `36:37061`。
- `ranking-list` — 默认 RankingListSlot，用于纵向排名列表（328×120px 每项，排名 + 封面 + 标题/演员/年份 + 追按钮）；对应 Pixso 节点 `36:37062`。
- `mini-player` — 默认 MiniPlayerSlot，用于迷你播放器（ranking variant），支持 compact/large 双尺寸，位于排名列表与底部导航栏之间。

## layout_skeleton

```html
<main class="layout-services-ranking">
  <!-- 头部区域：背景图 + overlay（StatusBar, TitleBar）+ 插图 -->
  <section class="layout-header">
    <img data-slot="headerBgSlot" />
    <div class="layout-header-overlay">
      <header data-slot="statusBarSlot"></header>
      <header data-slot="titleBarSlot"></header>
    </div>
    <div data-slot="illustrationSlot"></div>
  </section>

  <!-- 内容面板：顶部圆角深色面板，与 header 底部重叠 -->
  <section class="layout-content-panel">
    <nav data-slot="chipsTabSlot"></nav>
    <section data-slot="rankingListSlot"></section>
    <footer data-slot="bottomBarSlot"></footer>
  </section>
</main>
```

## layout_runtime

| 能力 | 源码支撑 | 说明 |
| --- | --- | --- |
| 页面实现 | `src/pages/services-ranking/services-ranking.tsx` | 360×792 固定移动端深色主题页面壳 |
| 头部背景 | `头图?: string` | 默认 `/chart-header-bg.png`，可替换为其他头图 URL |
| 插图区域 | `主标题?: string` + `描述?: string` | 麦穗 SVG 矢量对 + 金色主标题 (30px/900/思源宋体) + 金色描述 (12px/400)；默认 "综合排行榜" / "-根据榜单实时热度得出排名-" |
| 分类页签 | `chipsTabItems` + `chipsTabActiveKey` + `chipsTabDefaultActiveKey` + `on页签切换` | 默认 4 页签：综合榜/电视剧榜/电影榜/综艺榜；支持受控/非受控两种模式 |
| 排名列表 | `rankingItems?: MainChart03Item[]` | 默认 12 条榜单数据，每项含排名/封面图/标题/演员/年份类型；空列表自动显示"暂无数据" |
| 标题栏交互 | `on返回` / `on搜索` | 左侧返回按钮 + 右侧搜索按钮，HMSymbolIcon 图标 |
| 页面标题 | `页面标题?: string` | 默认 "排行榜"，传递给 TitleBar |
| 已废弃 prop | `插图标题?: string` | 降级为 `主标题`，新代码使用 `主标题` + `描述` |

## fixed_blocks

| Block / Component | 位置 | 是否必选 | 说明 |
| --- | --- | --- | --- |
| status-bar | header overlay 顶部 | 是 | ColorModeDark，半透明叠在头图之上 |
| title-bar | header overlay，StatusBar 下方 | 是 | secondary-page-phone，左侧返回按钮 (chevron_left) + 右侧搜索按钮 (magnifyingglass)，标题为 " "（空），不显示大标题文字 |
| aibottombar | content panel 底部 | 是 | ColorModeDark，360×28，白色半透明 pill 指示器居中，透明背景不遮挡列表 |

## slots

| Slot | 默认 Block | 可替换 Block 清单 | 是否必选 | 说明 |
| --- | --- | --- | --- | --- |
| HeaderBgSlot | `/chart-header-bg.png` | 任意头图 URL / none | 否 | 360×237 头部背景图；隐藏时保留深色背景 `#18181A`；与 `services-home` 的 `HeroSlot` 同为顶部视觉锚点，但本 Slot 为静态头图而非交互 Banner |
| IllustrationSlot | `ranking-topbanner` | `ranking-topbanner` / `ranking-hotlist-topbanner` / 自定义 ReactNode / none | 否 | 221×63px 插图区域；默认必须命中 `ranking-topbanner` block：麦穗 SVG 矢量对 (24×59px) + 金色主标题 (30px/900/思源宋体/#E0AF89/LS:1) + 金色描述 (12px/400/#E0AF89×0.6/LH:17/LS:1)；用户明确要求替换插图时才替换此槽 |
| ChipsTabSlot | `ranking-chipstab-phone` | `ranking-chipstab-phone` / `chips-tab` / `category-pills` / none | 否 | 360×64 分类页签，类型=tab，4 页签 (综合榜/电视剧榜/电影榜/综艺榜)；栏通透度=标准；可替换为 `services-home` 的分类胶囊 `category-pills` 或其他 ChipsTab 变体 |
| RankingListSlot | `ranking-list` | `ranking-list` / `ranking-categories` / `recommended-new-books` / `new-book-preview` / none | 否 | `ranking-list`：纵向排名列表，每项 328×120px，含排名序号 (top3 特殊色)、70×96 封面图 (圆角 8px)、标题 (16px Medium)、演员/副标题 (12px Regular)、年份类型 (12px Regular)、分割线 (218×0.5px)、追按钮 (28×28)；`ranking-categories`：分类榜单卡片列表；也可替换为 `services-home` 的推荐内容块 |
| MiniPlayerSlot | `mini-player` | `mini-player` (ranking variant) / `mini-player` (compact) / none | 否 | 迷你播放器 ranking 变体，位于排名列表与底部导航栏之间；compact/large 双尺寸；与 `services-home` 共用 `mini-player` block，通过 variant 区分场景；隐藏时不保留空白容器 |
| BottomBarSlot | `aibottombar` | `aibottombar` / none | 否 | 360×28，ColorModeDark，白色半透明 pill (112×5px/cornerRadius:4) 居中，透明背景 + pointer-events:none；与 `services-home` 的 `BottomNavSlot` 同为底部导航区域，但本 Slot 仅含 Aibottombar 指示条，不含 FloatingTab |

## visibility_rules

| 区域 | 默认 | 显隐 prop | 何时隐藏 |
| --- | --- | --- | --- |
| HeaderBg | 显示 | `showHeaderBg` | 头部无需背景图时隐藏，保留 #18181A 底色 |
| IllustrationSlot | 显示 | `showIllustration` | 页面不需要金色标题插图时隐藏 |
| ChipsTabSlot | 显示 | `showChipsTab` | 业务无分类切换（如单榜展示）时隐藏 |
| RankingListSlot | 显示 | `showRankingList` | 仅展示页面壳层时隐藏 |
| BottomBarSlot | 显示 | `showBottomBar` | 页面嵌入到已有 tab shell 时隐藏 |
| TitleBar 搜索按钮 | 显示 | `showSearchAction` | 页面无搜索入口时隐藏 |

## needed_components

- `status-bar`
- `title-bar`
- `aibottombar`
- `hmsymbol-icon`（chevron_left + magnifyingglass）
- `chips-tab`（被 `ranking-chipstab-phone` 依赖）

## composition_mapping

| 页面区域 | 优先使用 | 可替换为 | 说明 |
| --- | --- | --- | --- |
| StatusBarSlot | `StatusBar Color Mode="Dark"` | none | 固定顶部，深色模式，半透明背景叠在头图之上 |
| TitleBarSlot | `TitleBar category="secondary page-phone"` | none | 328×56px，左右各 16px padding；左侧 `3.Icon Button` (40×40/cornerRadius:1000) chevron_left 返回；右侧 `3.Icon Button` (40×40/cornerRadius:1000) magnifyingglass 搜索；fillPaints #FFFFFF → 使用 dark 模式 CSS 变量覆写；不得手写匿名 header 替代 |
| IllustrationSlot | 页面内联麦穗 SVG 矢量对 + 思源宋体标题描述 | 自定义插图 ReactNode | 麦穗 SVG 来自 `src/blocks/ranking-topbanner/svg/` (vector-left.svg + vector-right.svg)，各 24×59px；容器 221×63px，麦穗 absolute 底层 (z-index:0)，文字 relative 覆盖 (z-index:1)；字体回退顺序: "Source Han Serif CN" (思源宋体), "HarmonyHeiTi", serif |
| ChipsTabSlot | `RankingChipsTabPhone` | 同类 ChipsTab 组合 | 360×64px，4 页签 (综合榜/电视剧榜/电影榜/综艺榜)，类型=tab，栏通透度=标准；页签容器距 content panel 顶部 12px |
| RankingListSlot | `MainChart03` | 同类榜单/推荐 list | 328px 宽，列表项 328×120px；可见区域约 462px 高，内容超出可纵向滚动（隐藏滚动条）；列表底部预留 28px 给 Aibottombar |
| BottomBarSlot | `Aibottombar Color Mode="Dark"` | none | 360×28，absolute 贴 content panel 底部；白色半透明 pill 112×5px/cornerRadius:4/#FFFFFF 50%/blur；透明背景 + pointer-events:none 让点击穿透到列表 |

## spatial_tokens

- 画布：`360 × 792`。
- 头部区域：`360 × 237`，从 `y=0` 开始。头图 absolute 填满。
- 顶部 overlay：StatusBar 高 `36px`，TitleBar 紧接 StatusBar，下边界到上边界间距为 `0px`；TitleBar 页面坐标从 `y=36` 开始，宽 `328px`（左右各 16px padding），高 `56px`。
- 插图区域：容器 `221 × 63px`，absolute 居中于 header。麦穗 SVG 左 `24×59` (left=0)，右 `24×59` (left=197)。主标题 `30px/900`，描述 `12px/400/LH:17`。
- 内容面板：`360 × 578px`，`margin-top: -23px`（与 header 底部重叠 23px，实现 Pixso top=214），`border-radius: 24px 24px 0 0`，背景 `#18181A`，`z-index: 1`。
- ChipsTabSlot：padding-top `12px`（content panel 内，对应 Pixso top=226），容器高 `64px`。
- RankingListSlot：`flex: 1`，overflow-y auto，左右 padding `16px`，底部 padding `28px`；可见高度约 `462px`（578 - 12 - 64 - 28 - 底部余量），内容总高 `1440px`。
- BottomBarSlot：`absolute bottom: 0`，`360 × 28px`，padding-bottom `6px`，pill `112 × 5px`，border-radius `4px`，backdrop-filter `blur(27.18px)`。
- 列表项内部：排名序号 16px Bold；标题 16px Medium 218×22；演员 12px Regular 218×16；年份类型 12px Regular 154×16；封面图 70×96px 圆角 8px；分割线 218×0.5px left=110；追按钮 28×28px 圆角 22px。

## shell_rules

- 页面固定为 360px 宽移动端壳层，居中于预览容器。
- 根背景为深色 `#18181A`，对齐 Pixso Frame fill。
- 头部区域 237px 高，背景图 absolute 填满 + 状态栏/标题栏/插图 overlay 叠于其上。
- 内容面板通过负 margin 与头部底部重叠 23px，顶部圆角衔接头部，形成连续深色面板。
- 排名列表独立纵向滚动，隐藏滚动条保持设计干净。
- 底部导航条 absolute 浮动在列表上方，透明背景 + pointer-events:none 不遮挡列表交互。
- slot 为 `none` 或 `show* = false` 时不保留空白容器。

## stacking_context

| Layer | z-index | Positioning | Notes |
| --- | --- | --- | --- |
| header background | auto (0) | absolute top | 360×237 头图，底层 |
| illustration | 1 | absolute center in header | 麦穗 (z-index:0) + 文字 (z-index:1) |
| header overlay | 2 | absolute top | StatusBar + TitleBar，叠加在头图和插图上 |
| content panel | 1 | relative, margin-top -23px | 顶部圆角深色面板，覆盖 header 底部 23px |
| bottom bar | 2 | absolute bottom in panel | Aibottombar pill，浮动在列表上方 |

## adaptive_behavior

- 当前 page type 只覆盖竖屏手机页面；宽度保持 360px。
- 排名列表允许纵向滚动；头部区域不随内容重排。
- ChipsTab 页签自适应宽度，4 页签均分或内容撑开。
- 替换 RankingListSlot 的 block 必须能在 328px 宽容器内稳定渲染。
- 列表项封面图使用 `object-fit: cover` 保持比例。

## semantic_tokens

| Semantic Part | Token / Value |
| --- | --- |
| Page canvas | `#18181A` / dark background |
| Header background | `/chart-header-bg.png` (可替换) |
| Illustration gold text | `#E0AF89` / `rgba(224, 175, 137, 1)` |
| Illustration gold text (muted) | `rgba(224, 175, 137, 0.6)` |
| Top overlay text | `Dark/font_primary` `rgba(255, 255, 255, 0.898)` |
| Top overlay icon | `Dark/icon_primary` `rgba(255, 255, 255, 0.898)` |
| TitleBar button bg | `Dark/comp_background_tertiary` `rgba(255, 255, 255, 0.1)` |
| Content panel bg | `#18181A` |
| ChipsTab inactive text | `Dark/font_secondary` `rgba(255, 255, 255, 0.6)` |
| ChipsTab inactive bg | `rgba(255, 255, 255, 0.1)` |
| ChipsTab active bg | `#FFFFFF` |
| ChipsTab active text | `rgba(0, 0, 0, 0.9)` |
| Rank text (enable) | `rgba(255, 255, 255, 0.6)` |
| Rank text (top3) | 品牌色（特殊色，如品牌橙等） |
| Bottom bar pill | `rgba(255, 255, 255, 0.5)` |
| Font family (illustration) | `"Source Han Serif CN" (思源宋体), "HarmonyHeiTi", serif` |
| Font family (UI) | `"HarmonyHeiTi", "Geist Variable", sans-serif` |

## generation_constraints

- `services-ranking` 默认组合必须保留 `ranking-chipstab-phone` 和 `ranking-list`；顶部插图默认使用麦穗 SVG + 金色标题，只有用户明确替换插图时才传入其他 `illustrationSlot`。
- 顶部标题栏和返回/搜索按钮必须调用 `TitleBar` 组件，不能手写匿名 header 替代。
- 头部背景图、ChisTab、排名列表都是可替换 slot；生成页面时不得把它们写死成不可替换的内部 DOM。
- 若 prompt 要替换其中任一区块，只替换对应 slot，不重写整个页面模板。
- 可隐藏 slot 隐藏后不保留空白容器。
- 不要把本页面错误命中到 `mobile-grid` 或 `services-home`：本模板的核心是深色主题排名列表 + 金色插图 + ChipsTab 分类切换，不是宫格卡片首页或沉浸 Hero 首页。
- 不要将整个 Pixso 页面作为单张图片；必须保留 slot 装配能力。
- 插图区域 font-family 必须以 `"Source Han Serif CN"` (思源宋体) 为首选，不得省略思源宋体回退链。
- 底部导航必须使用 `Aibottombar` 组件，不得手写 home indicator。

## validation_notes

- `src/pages/services-ranking/services-ranking.tsx` 已提供 `头图`、`主标题`、`描述`、`chipsTabItems`、`chipsTabActiveKey`、`chipsTabDefaultActiveKey`、`rankingItems` 及对应回调；插图区使用麦穗 SVG 矢量对 + 思源宋体金色标题。
- Storybook: `Pages/services-ranking`，覆盖 Default / TVActive / MovieActive / WithEmpty / Status / Matrix 共 7 个 story。
- 插图数据来自 Pixso `query_nodes(36:37010)` + `get_screenshot(69:225)` 双证据；麦穗 `icon_font` "编组 6" → SVG 矢量对 (vector-left.svg + vector-right.svg) 位于 `src/blocks/ranking-topbanner/svg/`。
- TitleBar 按钮数据来自 Pixso `query_nodes(76:88687, 76:88696)`。
- DSL 列表实例文本（"姜子牙"、"夏日友晴天"等）与 MainChart03 默认数据一致，直接复用。

## source

- Pixso: `https://pixso.cn/app/design/KXylddm-EMqGBCzGr6ZZgQ?item-id=36:37008`
- Node: `36:37008`
- Node name: `排行榜`
- Canvas: `360 × 792`
- Secondary nodes:
  - `36:37010` — `#illustration_title` (插圖區域)
  - `36:37060` — `TitleBar-secondary page-Phone` (标题栏)
  - `36:37061` — `ChipsTab` (分类页签)
  - `36:37062` — `列表` (排名列表)
  - `36:37075` — `Aibottombar` (底部导航)
  - `76:88687` — `3.Icon Button` 返回
  - `76:88696` — `3.Icon Button` 搜索
