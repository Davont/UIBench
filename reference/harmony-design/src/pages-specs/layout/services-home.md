# Layout: services-home

> Page Type: Services Home. 云服务业务首页模板，适用于阅读、视频、音乐厅、游戏、应用市场、主题、云空间&查找、浏览器等云服务类 App 的首页。原始 Pixso source 为 `首页_4C`，节点 `67:56732`，画布 `360 × 792`。

## page_type_scope

`services-home` 覆盖同一类 4C 服务首页骨架：顶部沉浸式 Hero + 中部内容 Block 串联 + 底部主导航。该 page type 的固定区域只有：

- 顶部 Overlay：`StatusBar` + `TitleBar`，包含页面标题「首页」和可选搜索 action。
- 底部主导航：`bottomNavSlot`，默认 `FloatingTab` 主导航，业务可替换 tab 数据或整个 slot。

除上述固定壳层外，Hero、频道胶囊、第二内容段和第三内容段均为可替换 Block slot。默认注入形态偏阅读；游戏首页应使用本 spec 的 `game-home` 拼接形态，音乐厅首页使用 `music-home` 拼接形态，电影/视频首页使用 `movie-home` 拼接形态。

## hit_rules

命中 `services-home` 时，页面应同时满足以下特征：

- 用户明确要求云服务业务首页、服务首页，或阅读首页、书城首页、视频首页、音乐厅首页、游戏首页、游戏库首页、应用市场首页、主题首页、云空间首页、浏览器首页等业务线首页。
- 页面是移动端 4C 首页，首屏顶部为沉浸式大 Hero。
- 首页包含多个业务内容区块垂直串联，常见组合为阅读形态 `TopBanner` Hero slot + 分类胶囊 + `NewBookPreview` + `RecommendedNewBooks`，游戏形态 `top-banner-2(Game)` Hero slot + 游戏频道胶囊 + `my-game-review` + `recommended-new-games`，音乐厅形态 `top-banner-2(Music)` + 音乐厅频道胶囊 + `music-recommended`，或电影形态 `top-banner-2(Movie)` + 影视频道胶囊 + `my-movie-review` + `today-movie-list`。
- 存在底部主导航，通常是书架/书城/精品书/我的，或同等业务 tab。
- Prompt 中出现 `top banner`、`TopBanner`、`南方有嘉木`、`新书速览`、`新书强推`、`推荐新书`、`top-banner-2`、`TopBanner2`、`我的游戏`、`my-game-review`、`MyGameReview`、`新游情报局`、`recommended-new-games`、`RecommendedNewGames`、`Hi Raven，为你推荐`、`music-recommended`、`MusicRecommended`、`欢迎你回来续看`、`my-movie-review`、`MyMovieReview`、`today-movie-list`、`今日热播大片` 等已登记 Block 名称时，应优先命中本 page type，而不是泛化到 `mobile-grid`。

## exclusion_rules

- 仅为通用卡片流、无沉浸式顶部大 Banner → 优先评估 `mobile-card`。
- 以宫格卡片为核心，顶部没有可替换 Hero slot → 优先评估 `mobile-grid`。
- 以入口列表、资产中心、个人中心列表为核心 → 优先评估 `mobile-list`。
- 设置 / 表单 / 后台管理 / 详情页 / 播放器页不命中本布局。
- 若页面只有单个 Block 展示，不构成完整首页模板，则先抽取或复用 Block，不生成本 page type。

## reference_blocks

- `top-banner` — 默认 HeroSlot，用于首屏沉浸式阅读推荐 Banner；对应 Pixso `top banner` 节点 `71:770`。
- `top-banner-2` — 游戏 HeroSlot，用于首屏沉浸式游戏推荐 Banner；与默认 Hero 同为 `360 × 450`，底部渐变延展 `160px`。
- `new-book-preview` — 默认 NewBookPreviewSlot，用于横向新书速览。
- `recommended-new-books` — 默认 RecommendedNewBooksSlot，用于纵向推荐新书列表。
- `my-game-review` — 游戏形态的 NewBookPreviewSlot 替换 Block，用于「我的游戏 / 你最近在玩的游戏」横向滚动卡片。
- `recommended-new-games` — 游戏形态的 RecommendedNewBooksSlot 替换 Block，用于「新游情报局」推荐新游内容区。
- `music-recommended` — 音乐厅形态的 NewBookPreviewSlot 替换 Block，用于「Hi Raven，为你推荐」横向专辑推荐。
- `my-movie-review` — 电影形态的 NewBookPreviewSlot 替换 Block，用于「欢迎你回来续看」横向续看内容。
- `today-movie-list` — 电影形态的 RecommendedNewBooksSlot 替换 Block，用于「今日热播大片」三列影视卡片列表。

## composition_variants

| Variant | 适用场景 | HeroSlot | CategoryTabsSlot | NewBookPreviewSlot | RecommendedNewBooksSlot | BottomNavSlot |
| --- | --- | --- | --- | --- | --- | --- |
| `reading-home` | 阅读、书城、小说、内容阅读服务首页 | `top-banner` | 精选 / 小说 / 商业 / 历史 | `new-book-preview` | `recommended-new-books` | 书架 / 书城 / 精品书 / 我的 |
| `game-home` | 游戏首页、游戏库、游戏服务推荐、云游戏首页 | `top-banner-2` | 在玩 / 精选 / 排行 / 上新 | `my-game-review` | `recommended-new-games` | 首页 / 游戏库 / 圈子 / 我的 |
| `music-home` | 音乐厅首页、音乐厅、音乐厅推荐、音频服务首页 | `top-banner-2` with `场景="music"` | 精选 / 古典音乐 / 空间音频 / 播客 | `music-recommended` | none 或同类音乐厅推荐列表 | 首页 / 音乐厅 / Cafe听 / 我的 |
| `movie-home` | 视频首页、电影首页、影视推荐、剧集续看首页 | `top-banner-2` with `场景="movie"` | 精选 / 电视剧 / 电影 / 少儿 | `my-movie-review` | `today-movie-list` | 首页 / 看点 / 全网影视 / 影院 / 我的 |

### game-home assembly

游戏形态是 `services-home` 的同 page type 拼接形式，不创建新的 page_type：

```tsx
<ServicesHomeTemplatePage
  heroSlot={<TopBanner2 />}
  categories={[
    { id: "playing", label: "在玩" },
    { id: "featured", label: "精选" },
    { id: "ranking", label: "排行" },
    { id: "new", label: "上新" },
  ]}
  activeCategoryId="featured"
  newBookPreviewSlot={<MyGameReview />}
  recommendedNewBooksSlot={<RecommendedNewGames />}
  bottomTabs={gameBottomTabs}
  activeTabKey="home"
/>
```

`gameBottomTabs` 应按业务使用首页 / 游戏库 / 圈子 / 我的，图标优先使用已注册 HMSymbol 或现有导航组件支持的 icon node；不要为了游戏形态新增 page shell。

### music-home assembly

音乐厅形态是 `services-home` 的同 page type 拼接形式，不创建新的 page_type。参考 Pixso `36:24440`：

```tsx
<ServicesHomeTemplatePage
  pageTitle="音乐厅"
  heroSlot={<TopBanner2 场景="music" />}
  categories={[
    { id: "picks", label: "精选" },
    { id: "classical", label: "古典音乐" },
    { id: "spatial-audio", label: "空间音频" },
    { id: "podcast", label: "播客" },
  ]}
  activeCategoryId="picks"
  newBookPreviewSlot={<MusicRecommended />}
  showRecommendedNewBooks={false}
  bottomTabs={musicBottomTabs}
  activeTabKey="music"
/>
```

`musicBottomTabs` 应按业务使用首页 / 音乐厅 / Cafe听 / 我的。若需要底部迷你播放器，可通过 `bottomNavSlot` 注入包含 MiniPlayer + FloatingTab 的组合；若仅验证 page type 拼接，保留默认 `FloatingTab` shell。

### movie-home assembly

电影形态是 `services-home` 的同 page type 拼接形式，不创建新的 page_type。参考 Pixso `36:23079`：

```tsx
<ServicesHomeTemplatePage
  pageTitle="首页"
  heroSlot={<TopBanner2 场景="movie" />}
  categories={[
    { id: "picks", label: "精选" },
    { id: "tv", label: "电视剧" },
    { id: "movie", label: "电影" },
    { id: "kids", label: "少儿" },
  ]}
  activeCategoryId="picks"
  newBookPreviewSlot={<MyMovieReview />}
  recommendedNewBooksSlot={<TodayMovieList />}
  bottomTabs={movieBottomTabs}
  activeTabKey="home"
/>
```

`movieBottomTabs` 应按业务使用首页 / 看点 / 全网影视 / 影院 / 我的。若实现侧 FloatingTab 仅支持 4 tab，优先保留首页 / 看点 / 全网影视 / 我的；5 tab 需使用可支持对应数量的底部导航组件或自定义 `bottomNavSlot`。

## layout_skeleton

```html
<main class="layout-services-home">
  <section data-slot="heroSlot"></section>

  <div class="layout-overlay">
    <header data-slot="statusBarSlot"></header>
    <header data-slot="titleBarSlot"></header>
  </div>

  <section class="layout-content">
    <nav data-slot="categoryTabsSlot"></nav>
    <section data-slot="newBookPreviewSlot"></section>
    <section data-slot="recommendedNewBooksSlot"></section>
  </section>

  <footer data-slot="bottomNavSlot"></footer>
</main>
```

## layout_runtime

| 能力 | 源码支撑 | 说明 |
| --- | --- | --- |
| 页面实现 | `src/pages/services-home-template/services-home-template.tsx` | 360×792 固定移动端页面壳 |
| Hero slot | `heroSlot?: ReactNode` + `showHero` | 默认渲染 `TopBanner`；游戏/音乐厅/电影形态传入 `TopBanner2` 的对应 `场景`；可替换为同类 hero/banner block 或隐藏 |
| NewBookPreview slot | `newBookPreviewSlot?: ReactNode` + `showNewBookPreview` | 默认渲染 `NewBookPreview`；游戏传入 `MyGameReview`，音乐厅传入 `MusicRecommended`，电影传入 `MyMovieReview`；可替换为服务首页中同尺寸的横向内容 |
| RecommendedNewBooks slot | `recommendedNewBooksSlot?: ReactNode` + `showRecommendedNewBooks` | 默认渲染 `RecommendedNewBooks`；游戏传入 `RecommendedNewGames`，电影传入 `TodayMovieList`，音乐厅可隐藏或替换为同类音乐厅推荐列表 |
| 分类胶囊 slot | `categoryTabsSlot?: ReactNode` + `showCategoryTabs` | 默认 4 个胶囊：精选/小说/商业/历史；可通过 `categories` 替换为游戏/音乐厅/影视频道，或整段替换 |
| 顶部状态/标题显隐 | `showStatusBar` / `showPageHeader` / `showSearchAction` | 顶部标题区由 `TitleBar` 组件承载，支持隐藏状态栏、TitleBar 或搜索 action |
| 底部导航 slot | `bottomNavSlot?: ReactNode` + `showBottomNav` | 默认 `FloatingTab` 主导航，可通过 `bottomTabs`/`activeTabKey` 切换业务 tab，也可整段替换或隐藏 |

## fixed_blocks

| Block / Component | 位置 | 是否必选 | 说明 |
| --- | --- | --- | --- |
| status-bar | overlay 顶部 | 否 | 默认显示，深色模式 |
| title-bar | overlay 顶部 | 否 | 页面标题「首页」与搜索 action 必须通过 `TitleBar` 组件渲染；搜索按钮可单独隐藏 |
| bottom floating tab | bottomNavSlot | 否 | 默认主导航；若业务无底部 tab 可隐藏 |

## slots

| Slot | 默认 Block | 可替换 Block 清单 | 是否必选 | 说明 |
| --- | --- | --- | --- | --- |
| HeroSlot | `top-banner` | `top-banner` / `top-banner-2(game)` / `top-banner-2(music)` / `top-banner-2(movie)` / hero-banner / service-promo-banner / none | 否 | 首屏沉浸 Banner；阅读默认用 `top-banner`，游戏/音乐厅/电影形态用 `top-banner-2` 对应场景，用户明确要求替换时只替换此槽 |
| CategoryTabsSlot | category-pills | category-pills / game category pills / music category pills / movie category pills / chips-tab-rail / none | 否 | 业务频道胶囊；可按游戏/阅读/音乐厅/视频切换；音乐厅建议精选/古典音乐/空间音频/播客，电影建议精选/电视剧/电影/少儿 |
| NewBookPreviewSlot | `new-book-preview` | `new-book-preview` / `my-game-review` / `music-recommended` / `my-movie-review` / book-preview-rail / content-preview-rail / none | 否 | 第二段横向内容；阅读默认新书速览，游戏替换为我的游戏，音乐厅替换为音乐厅推荐，电影替换为续看内容 |
| RecommendedNewBooksSlot | `recommended-new-books` | `recommended-new-books` / `recommended-new-games` / `today-movie-list` / ranking-list / recommendation-list / none | 否 | 第三段纵向推荐列表；阅读默认推荐新书，游戏替换为新游情报局，电影替换为今日热播大片，音乐厅可隐藏 |
| BottomNavSlot | floating-tab | floating-tab / bottom-tab / none | 否 | 首页主导航；`FloatingTab` 自带底部手势指示条，不得再叠加独立 `Aibottombar` |

## visibility_rules

| 区域 | 默认 | 显隐 prop | 何时隐藏 |
| --- | --- | --- | --- |
| StatusBar | 显示 | `showStatusBar` | 外部壳层已提供系统状态栏时隐藏 |
| TitleBar | 显示 | `showPageHeader` | 顶部 Banner 自带完整标题区时隐藏 |
| SearchAction | 显示 | `showSearchAction` | 页面无搜索入口时隐藏 |
| HeroSlot | 显示 | `showHero` | 非沉浸首页或只需要内容流时隐藏 |
| CategoryTabsSlot | 显示 | `showCategoryTabs` | 业务无频道切换时隐藏 |
| NewBookPreviewSlot | 显示 | `showNewBookPreview` | 页面不需要横向新书速览时隐藏 |
| RecommendedNewBooksSlot | 显示 | `showRecommendedNewBooks` | 页面不需要纵向推荐列表时隐藏 |
| BottomNavSlot | 显示 | `showBottomNav` | 页面嵌入到已有 tab shell 时隐藏 |

## needed_components

- `status-bar`
- `title-bar`
- `floating-tab`
- `hmsymbol-icon` 或 `lucide-react` 图标

## composition_mapping

| 页面区域 | 优先使用 | 可替换为 | 说明 |
| --- | --- | --- | --- |
| TitleBarSlot | `TitleBar category="normal-phone"` | none | 页面标题「首页」与搜索 action；不得手写匿名 header 替代 |
| HeroSlot | `TopBanner` | `TopBanner2` / 同类 hero/banner block | 默认使用 `top-banner`，游戏/音乐厅/电影使用 `top-banner-2` 对应场景；根布局保持 360×450，底部取色渐变背景继续延展 160px；替换 block 不应改变后续内容起点 |
| CategoryTabsSlot | 页面级 category pills | `chips-tab` 组合 | 胶囊高度 36px，容器高度 56px，横向滚动；游戏/音乐厅/电影形态可直接传 `categories` 数据，无需自写 slot |
| NewBookPreviewSlot | `NewBookPreview` | `MyGameReview` / `MusicRecommended` / `MyMovieReview` / 同类横向内容 rail | 页面内从 `x=16` 开始放置；默认阅读 block 宽 `422px`，右侧超出 360 画布自然裁切；游戏、音乐厅、电影横向内容均通过 slot 注入，block 自身不得增加破坏 Hero 渐变露出的硬底板 |
| RecommendedNewBooksSlot | `RecommendedNewBooks` | `RecommendedNewGames` / `TodayMovieList` / 同类榜单/推荐 list | 阅读默认 360 宽；游戏 `RecommendedNewGames` 根宽 328px；电影 `TodayMovieList` 根宽 360px；音乐厅形态可隐藏此 slot |
| BottomNavSlot | `FloatingTab-Phone` shell (`FloatingTab` only) | `BottomTab` / none | 默认还原 Pixso `实例 47`：整体 `360 × 100` 固定贴底，内部渲染 328×56 FloatingTab；FloatingTab 已内置底部手势指示条区域。禁止在同一 slot 内再叠加独立 `Aibottombar`。若 Pixso 实例节点 `82:58365` 对 `design_to_code` 返回 `Index out of bounds`，使用已验证的 FloatingTab 组件源 DSL `5344:21809` / `5344:21795` 作为组件结构来源，再叠加本 page type 的书城态颜色。 |

## implementation_slot_check

当前模板 `src/pages/services-home-template/services-home-template.tsx` 已具备以下能力，可支撑 `game-home`、`music-home`、`movie-home` 形态：

- `heroSlot?: ReactNode` + `showHero`：可注入 `TopBanner2` 的 game/music/movie 场景，默认仍为 `TopBanner`。
- `categories` / `activeCategoryId` / `onCategoryChange` + `categoryTabsSlot` + `showCategoryTabs`：可直接把默认阅读频道替换为游戏、音乐厅或电影频道，或整段注入自定义频道栏。
- `newBookPreviewSlot?: ReactNode` + `showNewBookPreview`：可注入 `MyGameReview`、`MusicRecommended` 或 `MyMovieReview`。
- `recommendedNewBooksSlot?: ReactNode` + `showRecommendedNewBooks`：可注入 `RecommendedNewGames` 或 `TodayMovieList`；音乐厅形态可通过 `showRecommendedNewBooks={false}` 隐藏。
- `bottomTabs` / `activeTabKey` / `onTabChange` + `bottomNavSlot` + `showBottomNav`：可把默认书城导航替换为游戏、音乐厅或电影导航，或整段注入自定义底部导航。
- `showStatusBar` / `showPageHeader` / `showSearchAction`：固定顶部区可独立显隐；默认显示，符合图中红框固定区。

注意：本仓库约定 `src/pages/` 整体只读，因此 page type 完善优先更新 route/layout 规格；运行时 slot 能力当前已经满足。

## spatial_tokens

- 画布：`360 × 792`。
- 顶部 overlay：StatusBar 高 `36px`，TitleBar 紧接 StatusBar，下边界到上边界间距为 `0px`；TitleBar 页面坐标从 `y=36` 开始，不额外加 `margin-top`。
- HeroSlot：背景可视范围 `360 × 610`，从 `y=0` 开始；默认 `TopBanner` 根布局对齐 Pixso `71:770` 的 `360 × 450`，并允许 `.背景智能取渐变色` 在 `y=450` 后继续显示 `160px`。
- 内容滚动区：`padding-top: 470px`，分类胶囊叠在 TopBanner 下方取色渐变区域上，不得用页面底色或白色背景覆盖该渐变。
- CategoryTabsSlot：高度 `56px`，左边距 `16px`，胶囊 `78 × 36`，gap `8px`。
- NewBookPreviewSlot：左边距 `16px`，紧接胶囊区；默认 `NewBookPreview` block 保持 Pixso 自身宽 `422px`，title、首张封面和首个书名在页面坐标 `x=16` 左对齐，右侧内容允许超出并由 360px 页面画布裁切；根背景必须透明，`y=526~610` 区域应透出 `TopBanner` 的 `.背景智能取渐变色`。
- RecommendedNewBooksSlot：宽 `360px`，距上方 `6px`。
- 游戏形态 HeroSlot：`TopBanner2` 保持 `360 × 450`，下方智能渐变继续覆盖至 `y=610`；频道胶囊仍叠在渐变区上。
- 游戏形态 NewBookPreviewSlot：`MyGameReview` 根宽 `360px`，紧接频道胶囊；卡片横向滚动，底色应与 Hero 下方深色/渐变自然衔接。
- 游戏形态 RecommendedNewBooksSlot：`RecommendedNewGames` 根宽 `328px`，以 16px 内容边距放置，距离 `MyGameReview` 可按 block 自身标题间距自然衔接。
- 音乐厅形态 HeroSlot：`TopBanner2 场景="music"`；频道胶囊叠在 Grammy Hero 渐变区上，NewBookPreviewSlot 注入 `MusicRecommended`，第三段推荐可隐藏。
- 电影形态 HeroSlot：`TopBanner2 场景="movie"`；频道胶囊叠在影视 Hero 渐变区上，NewBookPreviewSlot 注入 `MyMovieReview`，RecommendedNewBooksSlot 注入 `TodayMovieList`。
- BottomNavSlot：固定底部，整体 `360 × 100`，对应 Pixso `FloatingTab-Phone` 实例 `67:57090`；背景过渡使用该实例继承的 `Light/comp_gradient_overlay_background`，即 `rgba(241,243,245,0)` 到 `rgba(241,243,245,0.2)` 的轻量透明渐变，不得使用黑色硬背板；内部 FloatingTab `328 × 56` 位于 `x=16, y=16`。`FloatingTab` 自带底部手势指示条区域，禁止额外渲染 `Aibottombar`。当前书城态 active symbol / label 使用 `#F34D4F`，inactive symbol / label 使用 `rgba(255,255,255,0.9)`。

## shell_rules

- 页面固定为 360px 宽移动端壳层，居中于预览容器。
- 根背景为深色 `#18181A`，对齐 Pixso Frame fill。
- Hero slot 占首屏背景，状态栏、页面标题和搜索按钮作为 overlay 叠在 Hero 之上。
- 主内容区独立纵向滚动，底部预留 `116px` 给 `FloatingTab-Phone` 壳层和内容露出。
- slot 为 `none` 或 `show* = false` 时不保留空白容器。

## stacking_context

| Layer | z-index | Positioning | Notes |
| --- | --- | --- | --- |
| top overlay | 20 | absolute top | StatusBar、页面标题、搜索按钮 |
| content | 10 | relative scroll | Category / NewBookPreview / RecommendedNewBooks |
| heroSlot | auto | absolute top | 首屏沉浸背景；TopBanner 下方取色渐变需露出至 `y=610` |
| bottomNavSlot | 50 | absolute bottom | `360 × 100` FloatingTab-Phone shell，只包含 self-contained FloatingTab |

## adaptive_behavior

- 当前 page type 只覆盖 4C 竖屏手机页面；宽度保持 360px。
- 内容区允许纵向滚动；Hero slot 不随内容重排。
- category pills 可横向滚动，末尾保留右侧 padding。
- Hero/NewBookPreview/RecommendedNewBooks 替换 block 必须能在 360px 宽容器内稳定渲染。

## semantic_tokens

| Semantic Part | Token / Value |
| --- | --- |
| Page canvas | `#18181A` / dark background |
| Top overlay text | `Dark/font_primary` `rgba(255,255,255,0.9)` |
| Category inactive text | `Dark/font_secondary` `rgba(255,255,255,0.6)` |
| Category inactive bg | `rgba(255,255,255,0.1)` |
| Category active bg | `#FFFFFF` |
| Category active text | `rgba(0,0,0,0.9)` |
| Bottom overlay | dark gradient mask |

## generation_constraints

- `services-home` 默认阅读组合必须保留 `top-banner`、`new-book-preview`、`recommended-new-books`；顶部 Hero 默认命中 `TopBanner`，并保留其下方 `360 × 160` 取色渐变背景，只有用户明确替换 Hero 时才传入其他 `heroSlot`。
- 当 prompt 命中游戏首页、游戏库首页、`top-banner-2`、`my-game-review`、`recommended-new-games` 或截图展示游戏推荐首页时，使用 `game-home` composition：`TopBanner2` + 游戏 category pills + `MyGameReview` + `RecommendedNewGames` + 游戏底部 tab。
- 当 prompt 命中音乐厅首页、音乐厅、`top-banner-2` Music、`music-recommended`、`Hi Raven，为你推荐` 或截图展示 Grammy 音乐厅首页时，使用 `music-home` composition：`TopBanner2 场景="music"` + 音乐厅 category pills + `MusicRecommended` + 音乐厅底部 tab；默认隐藏第三内容段，除非用户要求更多音乐厅推荐列表。
- 当 prompt 命中视频首页、电影首页、影视首页、`top-banner-2` Movie、`my-movie-review`、`today-movie-list`、`欢迎你回来续看`、`今日热播大片` 或截图展示影视首页时，使用 `movie-home` composition：`TopBanner2 场景="movie"` + 影视 category pills + `MyMovieReview` + `TodayMovieList` + 影视底部 tab。
- 顶部页面标题和搜索入口必须调用 `TitleBar` 组件，不能手写 `h1 + button` 顶部区域。
- 顶部 Hero、NewBookPreview、RecommendedNewBooks 都是可替换 slot；生成页面时不得把它们写死成不可替换的内部 DOM。
- 若 prompt 要替换其中任一区块，只替换对应 slot，不重写整个页面模板。
- 可隐藏 slot 隐藏后不保留空白容器。
- 不要把本页面错误命中到 `mobile-grid`：本模板的核心是服务首页沉浸 Banner + 内容 Block 串联，不是宫格卡片首页。
- 不要将整个 Pixso 页面作为单张图片；必须保留 slot 装配能力。

## validation_notes

- `src/pages/services-home-template/services-home-template.tsx` 已提供 `heroSlot`、`categoryTabsSlot`、`newBookPreviewSlot`、`recommendedNewBooksSlot`、`bottomNavSlot` 和对应 `show*` 显隐能力；`heroSlot` 默认渲染 `TopBanner`，顶部标题区已切换为 `TitleBar` 组件，可支撑 reading/game/music/movie 四种拼接形态。
- Storybook: `Pages/ServicesHome`。
- Pixso `design_to_code(67:56732)` 返回 500；本 spec 使用 `get_screenshot` + `get_node_dsl` 校准页面骨架、尺寸和默认内容。
- Route 试跑见 `src/render/req-services-home-route-check/index.log.md`。

## source

- Pixso: `https://pixso.cn/app/design/KXylddm-EMqGBCzGr6ZZgQ?item-id=67:56732`
- Node: `67:56732`
- Node name: `首页_4C`
- Canvas: `360 × 792`
