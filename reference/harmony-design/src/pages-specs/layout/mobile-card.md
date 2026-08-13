# Layout: mobile-card

> 移动端内容卡片页（卡片布局）：以多种卡片类型垂直堆叠 + section header 分区管理为核心组织形式。
> 原始 source: `.tmp/layout-card.md` (Pixso node `23:13468`, canvas `360 × 780`)

## hit_rules

命中 `mobile-card` 时，页面应同时满足以下特征：

- 画布为单屏移动端竖向比例 `360 × 780`，页面为长滚动形式。
- 顶部固定壳层为 `titlebar`（已包含 statusbar）；`search bar` 属于内容区首项，初始与 titlebar 视觉重叠但随内容滚动。
- 内容区由 2 个以上 section 垂直堆叠，每个 section 有 section header（标题文本，fs=16 Medium）。
- 内容以多种类型卡片为核心，卡片按 2 列或 3 列网格排列（非水平滚动行）。
- 卡片结构以「封面图 + 标题 + 副标题」为基础，叠加可选信息（评分 badge、播放按钮、元数据）。
- 至少存在一种大尺寸特色卡片（宽度 328px，高度 > 150px），包含海报图 + 文本 + 操作按钮。
- 底部为 tab bar（4~5 tab），活跃态使用品牌橙色（`rgba(237,111,33,1.0)`）。

## exclusion_rules

出现以下任一特征时，不应优先命中该布局：

- 页面以水平滚动宫格卡片为主 → 优先评估 `mobile-grid`。
- 页面为单列垂直 list item 堆叠，无封面图卡片 → 优先评估 `mobile-list`。
- 页面为纯设置/控件操作页 → 优先评估 `mobile-settings`。
- 页面无 section header，内容区域不分区。
- 卡片类型单一（全为同一尺寸/结构），无大尺寸特色卡片。
- 底部无 tab bar（仅 home indicator）且为独立功能页。

## reference_blocks


## layout_skeleton

```html
<main class="layout-mobile-card">
  <header class="layout-titlebar"></header>

  <section class="layout-content">
    <!-- Search 是 .layout-content 的首个内容项（floating glass），
         初始位于 y≈96，并随纵向内容一起滚动。 -->
    <section class="layout-search-bar"></section>

    <!-- Hero banner -->
    <section class="layout-region layout-region-hero">
      <div class="layout-hero-banner"></div>
      <div class="layout-hero-indicator"></div>
    </section>

    <!-- 5 列 icon 入口 -->
    <section class="layout-region layout-region-entrance">
      <div class="layout-entrance-grid"></div>
    </section>

    <!-- 2 列横向卡片 -->
    <section class="layout-region layout-region-h2col">
      <div class="layout-grid-2col"></div>
    </section>

    <!-- section header + 3 列竖向缩略卡片 -->
    <section class="layout-region layout-region-thumb">
      <header class="layout-section-header"></header>
      <div class="layout-grid-3col"></div>
    </section>

    <!-- section header + 大尺寸特色卡片 -->
    <section class="layout-region layout-region-feature">
      <header class="layout-section-header"></header>
      <div class="layout-card-feature-large"></div>
    </section>

    <!-- 横向特色卡片（poster + 文本 + 按钮） -->
    <section class="layout-region layout-region-hfeature">
      <header class="layout-section-header"></header>
      <div class="layout-card-hfeature"></div>
    </section>

    <!-- 竖向特色卡片（image + text plate） -->
    <section class="layout-region layout-region-vfeature">
      <div class="layout-grid-2col"></div>
    </section>
  </section>

  <footer class="layout-bottom-shell">
    <nav class="layout-bottomtab"></nav>
  </footer>
</main>
```

## needed_components

- `status-bar` — 顶部状态栏，作为 titlebar 壳层内的独立系统组件
- `floating-title-bar` — 顶部 titlebar，包装在固定 124px 渐变背板壳层内
- `search` — 浮动搜索条（详见 §local-component-mapping 备注）
- `hmsymbol-icon` — 入口 / 播放 / chevron 类系统图标
- `bottom-tab` — 4-tab 底部导航 pill；仅当明确需要 FloatingTab 风格时才替换为 `floating-tab`
- `aibottombar` — 底部 home indicator pill（替代手写 5px 横条）
- `floating-swiper-dot-phone` — hero banner 指示点

## local_component_mapping

- statusbar: 使用 `@/components/StatusBar` 作为顶部 36px 状态栏；本地壳层只负责固定定位与渐隐背板。
- titlebar: 使用 `@/components/TitleBar` 提供 title + leading icon + actions；本地壳层仅提供 124px 高度与常驻纵向渐隐背板。
- search bar: 使用 `@/components/Search`（Search=OFF variant，placeholder + magnifying glass icon）。**API mismatch**：Search 组件的尺寸是固定的 343×40，而本布局的搜索条规格为 336×40，差 7px；搜索条居中渲染以匹配 360 画板。filter 按钮（speech/clock affordance）由 Search 自身 ON-variant 承载，本模板默认 OFF，不暴露。
- hero indicator: 使用 `@/components/FloatingSwiperDotPhone`（`类型="OFF"`，`组数=5`）替代手写 dot。
- entrance / play / chevron 类图标: 使用 `@/components/HMSymbolIcon`，避免引入外部图标风格。
- bottomtab pill: 使用 `@/components/BottomTab`（`layout="port"`）的玻璃 pill；本地壳层在 pill 下方叠加渐变蒙层与 Aibottombar，组成 97px 底部浮层。若改用 `FloatingTab`，则不得再叠加独立 Aibottombar。
- bottom home indicator: 使用 `@/components/Aibottombar` 取代手写 5px 横条。
- 7 种卡片类型：主体仍为页面级自定义内容块（hero banner、entrance grid、horizontal card、vertical thumbnail、large feature、horizontal feature、vertical feature）；其中通用图标与轮播指示器使用本地组件承载。

## composition_mapping

| Layout Block | Component Reference | Variant / Composition | Layout Responsibility | Component Responsibility |
| --- | --- | --- | --- | --- |
| `titlebar` | `titlebar.md` | `harmony-titlebar` + `normal` + 1 action（grid icon） | 贴顶 124px，完整承载 statusbar + 标题内容 + floating button | 时间文本、状态图标、标题文本、右侧 icon button、渐变模糊背板 |
| `search bar` | `search.md` | `harmony-search` + `off/normal` + filter button | 336×40 glass pill，作为 `.layout-content` 首项，初始位于 y≈96，并随内容滚动 | 搜索 icon、placeholder、filter button（clock icon） |
| `Hero Banner` | `FloatingSwiperDotPhone` + 页面级自定义 | 328×219 图片 + page indicator dots | banner 容器 | 整图渲染 + 5 点指示器（1 个 pill 激活态） |
| `Entrance Icon Grid` | 无 — 页面级自定义 | 5 列 icon 入口（68×76） | 5 列网格容器 | icon 圆形背板、标签文本 |
| `Horizontal Card` | 无 — 页面级自定义 | 156×88 cover + rating badge + title + subtitle，2 列排列 | 2 列网格容器 | cover 图片、评分 badge、标题、副标题 |
| `Section Header` | `subheader.md` | 240×48，fs=16 Medium | section 标题区域 | 标题文本 |
| `Vertical Thumbnail Card` | 无 — 页面级自定义 | 98×140 cover + play button + 可选 rating + title + subtitle，3 列排列 | 3 列网格容器 | cover 图片、播放按钮、评分、标题、副标题 |
| `Large Feature Card` | 无 — 页面级自定义 | 328×212，底板(r≈17) + cover + overlay + 底部信息 + button | 全宽卡片容器 | cover 图片、title overlay、评分、缩略图、标题、副标题、关注 button |
| `Large Horizontal Feature Card` | 无 — 页面级自定义 | 328×172，poster(114×152) + 文本栈 + 播放/缓存 button | 全宽卡片容器 | poster 图片、标题、元数据、统计、播放 button（橙色 pill）、缓存 button（灰色 pill） |
| `Vertical Feature Card` | 无 — 页面级自定义 | 156×163~189 image + 156×61 text plate，2 列排列 | 2 列网格容器 | cover 图片、文本底板（title+subtitle） |
| `bottom shell` | `bottomtab.md` + 可选 `aibottombar.md` | `layout-bottom-shell` 包裹 `harmony-bottomtab(4)` + `activeIndex=0` | 贴底 97px（含渐变蒙层 + pill + indicator） | 4 tab 项（首页/动态/会员购/我的），活跃态橙色；home indicator 渲染 |

## spatial_tokens

### Horizontal
- 页面边距：`16px`（内容区 328px 居中于 360px）。
- 2 列卡片列间距：`16px`（156 + 16 + 156 = 328）。
- 3 列缩略卡片列间距：`17px`（98 + 17 + 98 + 17 + 98 = 328）。
- 5 列 icon 入口间距：约 `19px`。
- 全宽卡片（banner / feature）：`328px`。

### Vertical
- titlebar 内容层底边 → search bar：`8px`（search 初始 y≈96）。
- search bar → hero banner：`16px`。
- hero banner → entrance grid：`24px`。
- entrance grid → 2-col cards：`12px`。
- section header（48px）→ 其下方卡片：`10px`。
- 2-col card 行间距：约 `60px`。
- large feature card → 下方 section：`16px`。
- horizontal feature card 间距：`12px`。
- vertical feature card 行间距：约 `74px`。

## shell_rules

- 画板固定 `360 × 780`；页面背景使用 `background_primary`（白色）。
- 顶部固定保留 titlebar `124px`（含 statusbar 36px + content-area 88px）。
- 底部固定保留 `layout-bottom-shell` `97px`（含 tab pill + home indicator / aibottombar + gradient mask）。
- 主内容区宽度 `328px`，水平居中。
- 浮层使用 `position: absolute` 定位参考 `.screen`；`search bar` 不是固定壳层，必须作为 `.layout-content` 首项使用 `position: relative; z-index: 30`。

## stacking_context

| Layer | z-index | Positioning | Notes |
| --- | --- | --- | --- |
| `layout-bottom-shell` | 100 | `position: absolute; bottom: 0` | 包含 tab pill + home indicator |
| `search bar` (内容流首项) | 30 | `position: relative` | 随内容滚动，初始 y≈96 |
| `titlebar` | 10 | `position: absolute; top: 0` | 常驻纵向渐隐背板 |
| 内容区 | `auto` | `position: relative` | 不得设置 `z-index` / `transform` / `filter` / `opacity<1` / `isolation: isolate` |

## adaptive_behavior

- `.screen` 固定高度 `780px`，`overflow: hidden; display: flex; flex-direction: column`。
- 内容滚动委托给 `.layout-content`（`overflow-y: auto; flex: 1 1 auto; min-height: 0`）。
- 内容区 `padding-top: 96px; padding-bottom: 113px`（含底部 shell 97px + 安全余量）。
- 卡片图片使用 `object-fit: cover`。文字遵循 P0/P1/P2：P0（权限名称、状态、数量、风险提示）完整展示；P1（说明文案）最多两行且卡片高度自适应；仅明确属于 P2（如歌名、用户名、元信息）的 title/subtitle 才可单行截断 `text-overflow: ellipsis`，并须有 Pixso 或布局约束依据。
- Glass morphism 元素（search、filter button、bottomtab pill）使用统一 glass token。

## semantic_tokens

| Semantic Part | Token |
| --- | --- |
| Page canvas | `background_primary`（白色） |
| Card text plate / large feature card plate | `comp_background_primary` |
| Titlebar title / section header / card title | `font_primary` |
| Card subtitle / description | `font_tertiary`（40% opacity） |
| Card metadata / stats | `font_tertiary`（50% opacity） |
| Rating badge background | 半透明黑 `rgba(0,0,0,0.30)` |
| Rating badge text / title overlay on dark | `font_on_primary`（白色） |
| Brand accent（active tab, play button） | 品牌橙色 `rgba(237,111,33,1.0)` |
| Entrance icon background | 品牌橙色 20% `rgba(237,111,33,0.20)` |
| Play button（pill） | 品牌橙色 |
| Cache/follow button（pill） | `comp_background_tertiary` |
| Glass fill（search bar / bottomtab / filter button） | glass token |
| Search placeholder | `font_secondary` |

## generation_constraints

- 禁止把整页实现为连续的匿名 frame 容器。
- 内容区必须以 section（header + 卡片组）为单位组织，不得平铺卡片。
- 2 列/3 列网格使用 CSS Grid 或 Flexbox，不得用绝对定位逐卡摆放。
- 全宽卡片使用 328px 宽度 + 16px 左边距。
- 卡片内 cover image 固定尺寸，使用 `object-fit: cover`，禁止拉伸变形。
- 固定系统壳层使用 `position: absolute`，不得使用 `position: fixed`。
- search bar 不属于固定系统壳层：必须作为 `.layout-content` 首项参与内容流，使用 `position: relative; z-index: 30`。
- 禁止用 `.bottom-glass-probe` 或类似节点在 bottomtab 背后生成可见的整宽灰/白矩形面板。
- titlebar 背板必须为常驻纵向渐隐层，不得按 `scrollTop` 切换硬背板，不得在 `.harmony-titlebar` 根节点添加整块 `backdrop-filter`。
- 7 种卡片类型当前均无对应组件 reference，页面实现时按本 layout §Block Patterns 的几何约束自定义。

## validation_notes

- 验收 checklist 参考原始 `.tmp/layout-card.md` 的 §15。
- 卡片总高度不随文本长度变化（封面图固定 + 文字区固定）。
- section header 强制存在，是页面分区管理的核心手段。
- 跨类型通用元素（Rating badge、Play button）应抽取为可复用 snippet。
- 列数不随视口宽度变化（移动端固定布局）。
- search 初始 y≈96、随内容滚动、不得为 screen 直属固定浮层。
- `.layout-content` 不得设置 `z-index` / `transform` / `filter` / `opacity<1`。
- 浮层安全区 padding 已定义（content padding-top≈96px, bottom≈113px）。
- 卡片内 cover、badge、title、subtitle 防拉伸约束已明确。
- 实现输出必须先满足 Composition Mapping，再做模板注入与样式微调。

## source

- 原始 reference: `.tmp/layout-card.md`
- Pixso source node: `23:13468`（卡片布局）
- Canvas: `360 × 780`，长滚动
