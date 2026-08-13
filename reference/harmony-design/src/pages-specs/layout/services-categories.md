# Layout: services-categories

> Page Type: Services Categories. 云服务业务筛选分类页面模板，适用于阅读、视频、音乐、游戏、应用市场、主题、云空间&查找、浏览器等业务的筛选/分类浏览页。原始 Pixso source 为 `筛选-4c`，节点 `36:41326`，画布 `360 × 792`。

## hit_rules

命中 `services-categories` 时，页面应同时满足以下特征：

- 用户明确要求筛选页、分类页、全部页面、视频分类、电影分类或服务分类浏览页。
- 页面是移动端 4C 深色模式页面，顶部为返回+标题+搜索的平铺标题栏。
- 页面主体为多行筛选 Chip（标签胶囊）+ 内容网格（宫格卡片）的经典筛选布局。
- 存在底部手势横条（Aibottombar），无底部主导航 tab。
- Prompt 中出现 `筛选`、`分类`、`全部`、`FilterChip`、`评分`、`年份`、`地区`、`MovieCard` 等已登记组件或关键词时，应优先命中本 page type，而不是泛化到 `mobile-grid`。

## exclusion_rules

- 以宫格卡片为首页核心，无筛选行 → 优先评估 `mobile-grid`。
- 顶部有沉浸式大 Banner / Hero → 优先评估 `services-home`。
- 以纵向列表、资产中心、个人中心列表为核心 → 优先评估 `mobile-list`。
- 设置 / 表单 / 后台管理 / 详情页 / 播放器页不命中本布局。
- 若页面无筛选 Chip 行，仅为纯内容网格，不构成本 page type。

## reference_blocks

- `filter-chips` — 筛选胶囊组，支持 active/inactive 双态；active 态橙色背景 `rgb(255,117,0)`，inactive 态半透明白底 `rgba(255,255,255,0.1)`。
- `movie-grid-card` — 电影封面宫格卡片，3:4 比例海报 + VIP 标签 + 评分角标 + 标题。

## layout_skeleton

```html
<main class="layout-services-categories">
  <header data-slot="statusBarSlot"></header>

  <header data-slot="titleBarSlot"></header>

  <section class="layout-content">
    <section data-slot="filterSectionSlot"></section>
    <section data-slot="contentGridSlot"></section>
  </section>

  <footer data-slot="bottomBarSlot"></footer>
</main>
```

## layout_runtime

| 能力 | 源码支撑 | 说明 |
| --- | --- | --- |
| 页面实现 | `src/pages/services-categories/ServicesCategoriesPage.tsx` | 360×792 固定移动端页面壳 |
| 状态栏 slot | `statusBarSlot` — 默认 `StatusBar Color Mode="Dark"` | 深色模式透明背景状态栏 |
| 标题栏 slot | `titleBarSlot` — 返回 + 标题 + 搜索 | 自定义标题栏，56px 高；返回/搜索按钮 40×40 圆形，半透明白底 |
| 筛选区 slot | `filterSectionSlot` — 多行 FilterChip | 默认 6 行：评分/年份/地区/会员/类型/平台；行内横向排列，Chip 高 36px |
| 内容网格 slot | `contentGridSlot` — 3 列电影封面网格 | 默认 3×3 网格；每卡 3:4 海报 + VIP 角标 + 评分角标 + 标题 |
| 底部横条 slot | `bottomBarSlot` — 默认 `Aibottombar Color Mode="Dark"` | 28px 深色模式手势横条，固定底部 |

## fixed_blocks

| Block / Component | 位置 | 是否必选 | 说明 |
| --- | --- | --- | --- |
| status-bar | 顶部 | 否 | 默认显示，深色模式，透明背景 |
| title-bar | 顶部 | 是 | 返回按钮 + 标题"全部" + 搜索按钮；标题栏 56px，按钮 40×40 圆形半透明白底 |
| aibottombar | 底部 | 否 | 深色模式手势横条，28px 固定底部 |

## slots

| Slot | 默认内容 | 可替换内容 | 是否必选 | 说明 |
| --- | --- | --- | --- | --- |
| StatusBarSlot | `StatusBar` (Dark) | `StatusBar` / none | 否 | 深色模式状态栏；外部壳层已提供时隐藏 |
| TitleBarSlot | 自定义标题栏 (返回 + "全部" + 搜索) | 同结构标题栏 / none | 是 | 页面标题和导航入口；当页面嵌入已有导航壳时可隐藏 |
| FilterSectionSlot | `FilterChips` 块 — 6 行筛选标签（评分/年份/地区/会员/类型/平台），active 态橙色 Chip，inactive 态半透明白底 | `FloatingToggleFilter` 块 — 毛玻璃通透切换标签（品牌红选中态 + 8 层材质效果） / `FilterComplete` 块 — 筛选摘要条（如"战争 / 2023 / 免费"），点击可重开筛选面板 / none | 否 | 筛选条件区；页面无筛选需求时隐藏；`FilterComplete` 适合作为筛选收折后的紧凑摘要条替代完整 Chip 行 |
| ContentGridSlot | `MovieGridCard` 块 — 3 列宫格影片卡片（3:4 海报 + VIP 金角标 + 评分角标 + 标题），默认 9 张卡 | `ScrollList` 块 — 字母索引导航滚动列表（含 AlphabetIndexer 侧边栏 + FloatingAlphabetIndexerLable 浮动指示器） / `FilterList` 块 — 头像 + 标题列表（48px 圆形头像 + 16px 标题 + 分割线，72px 行高） / none | 是 | 内容展示区；可替换卡片类型、列表样式、列数；`ScrollList` 适合音乐/联系人等字母索引场景，`FilterList` 适合歌手/作者等头像列表场景 |
| BottomBarSlot | `Aibottombar` (Dark) | `Aibottombar` / none | 否 | 底部手势横条；页面嵌入已有底部壳时隐藏 |

## visibility_rules

| 区域 | 默认 | 显隐 prop | 何时隐藏 |
| --- | --- | --- | --- |
| StatusBar | 显示 | `showStatusBar` | 外部壳层已提供系统状态栏时隐藏 |
| TitleBar | 显示 | `showTitleBar` | 页面嵌入已有导航壳时隐藏 |
| FilterSection | 显示 | `showFilters` | 页面无筛选需求时隐藏 |
| ContentGrid | 显示 | `showContent` | 仅作为空态占位时不适用（保持显示） |
| BottomBar | 显示 | `showBottomBar` | 页面嵌入已有底部壳时隐藏 |

## needed_components

- `status-bar`
- `aibottombar`
- 图标使用页面内联 SVG 或现有 HMSymbolIcon，不作为注册表组件引用。

## composition_mapping

| 页面区域 | 优先使用 | 可替换为 | 说明 |
| --- | --- | --- | --- |
| StatusBarSlot | `StatusBar Color Mode="Dark"` | none | 透明背景，36px 高 |
| TitleBarSlot | 自定义 titlebar（返回 + "全部" + 搜索） | 同类标题栏 | 高度 56px，左右 padding 16px；返回/搜索按钮 40×40 圆形，`rgba(255,255,255,0.1)` 背景；标题 18px/600；不使用 `FloatingTitleBar`（本页为 flat dark 风格） |
| FilterSectionSlot | 页面级 FilterChip 行 | 任意 FilterRow[] | Chip 高 36px，圆角 21px，padding 8px 16px；行 gap 12px，Chip 间距 8px；active 态 `rgb(255,117,0)` 橙色背景白色文字，inactive 态 `rgba(255,255,255,0.1)` 背景 |
| ContentGridSlot | 3 列 MovieCard 网格 | 任意 Card 网格 | 列宽 104px，gap 16px(row) × 8px(col)；卡片 3:4 海报 + 右上 VIP 标签 + 右下评分角标 + 标题 13px |
| BottomBarSlot | `Aibottombar Color Mode="Dark"` | none | 28px 固定底部，深色模式白色半透明 home indicator pill |

## spatial_tokens

- 画布：`360 × 792`。
- 根背景：`rgb(24, 24, 26)` 深色背景。
- StatusBar：高 `36px`，透明背景，深色模式。
- TitleBar：高 `56px`，左右 padding `16px`；返回按钮和搜索按钮 `40×40`；标题字号 `18px`，字重 `600`。
- FilterSection：`padding: 12px 0 0 16px`；每行高度自适应（Chip 36px），行间距 `12px`；Chip 默认宽度 `72px`（自适应内容），Chip 间距 `8px`；行宽度 `344px`，行内横向滚动允许。
- ContentGrid：`padding: 12px 16px 16px`；3 列 `repeat(3, 104px)`，行 gap `16px`，列 gap `8px`。
- BottomBar：固定底部 `28px`，`360×28`，深色模式。

## shell_rules

- 页面固定为 360px 宽移动端壳层，居中于预览容器。
- 根背景为深色 `rgb(24, 24, 26)`，对齐 Pixso Frame fill。
- 页面内容区纵向自然排列，无独立滚动区（页面高度 792px 足够容纳默认内容）。
- slot 为 `none` 或 `show* = false` 时不保留空白容器。
- 底部预留 `28px` 给 Aibottombar。

## stacking_context

| Layer | z-index | Positioning | Notes |
| --- | --- | --- | --- |
| bottomBarSlot | 50 | absolute bottom | `360×28` Aibottombar，贴底 |
| content | auto | normal flow | StatusBar → TitleBar → FilterSection → ContentGrid |
| statusBarSlot | auto | normal flow | 首个子元素，透明背景 |

## adaptive_behavior

- 当前 page type 只覆盖 4C 竖屏手机页面；宽度保持 360px。
- FilterSection 行内内容超出 344px 时可横向滚动，末尾保留右侧 padding。
- ContentGrid 支持列数调整（2~4 列），卡片宽度随列数自适应。
- 替换内容必须能在 360px 宽容器内稳定渲染。

## semantic_tokens

| Semantic Part | Token / Value |
| --- | --- |
| Page canvas | `rgb(24, 24, 26)` / dark background |
| Title text | `Dark/font_primary` `rgba(255,255,255,0.9)` |
| TitleBar button bg | `rgba(255,255,255,0.1)` |
| Chip active bg | `rgb(255, 117, 0)` (华为视频品牌橙色) |
| Chip active text | `rgba(255,255,255,1)` |
| Chip inactive bg | `rgba(255,255,255,0.1)` |
| Chip inactive text | `rgba(255,255,255,0.9)` |
| Movie title text | `rgba(255,255,255,0.9)` / 13px |
| Rating bg | `rgba(0,0,0,0.30)` + white gradient overlay |
| VIP badge bg | `#F0C990` / gold |
| VIP badge text | `#764B08` |
| Bottom indicator | white semi-transparent pill |

## generation_constraints

- `services-categories` 默认组合必须保留 StatusBar(Dark)、自定义标题栏、6 行筛选 Chip、3 列电影网格、Aibottombar(Dark)。
- 标题栏不得使用 `FloatingTitleBar` 或手写 `h1 + button` 替代；使用本 page type 定义的自定义 titlebar 结构（返回 + 标题 + 搜索）。
- 筛选行和内容网格都是可替换 slot；生成页面时不得把它们写死成不可替换的内部 DOM。
- 若 prompt 要替换其中任一区域，只替换对应 slot，不重写整个页面模板。
- 可隐藏 slot 隐藏后不保留空白容器。
- 不要把本页面错误命中到 `mobile-grid`：本模板的核心是筛选 Chip + 内容网格，不是纯宫格卡片首页。
- 不要将整个 Pixso 页面作为单张图片；必须保留 slot 装配能力。
- 页面使用深色模式，根背景 `rgb(24,24,26)`，不得使用浅色/白色背景。

## validation_notes

- `src/pages/services-categories/ServicesCategoriesPage.tsx` 已提供完整实现，包含 `StatusBar`(Dark)、自定义标题栏、`FilterChip` 子组件、`MovieCard` 子组件、`Aibottombar`(Dark)。
- Storybook: `Pages/ServicesCategories`，decorator 设置 `data-theme="dark"`。
- Props 接口：`ServicesCategoriesPageProps`、`FilterRow`、`FilterOption`、`MovieItem`。
- Pixso `design_to_code(36:41326)` 用于校准页面骨架、尺寸和默认内容。
- 变体树 JSON：`src/pages/services-categories/services-categories.json`。

## source

- Pixso: `https://pixso.cn/app/design/f3YuUJ1DHBrZxJcUHOJeYg?item-id=36:41326`
- Node: `36:41326`
- Node name: `筛选-4c`
- Canvas: `360 × 792`
