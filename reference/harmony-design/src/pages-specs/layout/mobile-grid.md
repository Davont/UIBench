# Layout: mobile-grid

> 移动端首页/发现页（宫格布局）：以水平滚动的宫格卡片 + 多内容区域混合编排为核心组织形式。
> 原始 source: `.tmp/layout-grid.md` (Pixso node `118:19305`, canvas `360 × 792`)

## hit_rules

命中 `mobile-grid` 时，页面应同时满足以下特征：

- 画布为单屏移动端竖向比例 `360 × 792`。
- 顶部固定壳层为 `titlebar`（已内含 status bar）；`search bar` 属于内容区首项，初始与 titlebar 视觉重叠但随内容滚动。
- 内容区由 2 个以上独立区域（section）垂直堆叠，每个区域有 section header（标题 + 可选右箭头）。
- 至少一个区域为宫格卡片：等宽卡片水平排列，卡片宽度在 120~180px 之间，卡片之间间距 8px，一行内水平滚动。
- 宫格卡片以「封面图 + 文字信息」为核心结构，图片占比 > 60% 卡片面积。
- 底部为 `FloatingTab`（4~5 tab）浮动导航，可含 miniplayer。

## exclusion_rules

出现以下任一特征时，不应优先命中该布局：

- 页面内容为单列垂直 list item 堆叠，无水平滚动区域 → 优先评估 `mobile-list`。
- 卡片内以 icon + 文本为主、无封面图 → 优先评估 `mobile-list`。
- 页面为纯设置/控件操作页 → 优先评估 `mobile-settings`。
- 页面为多列瀑布流（卡片高度参差、非等宽等距）→ 本布局不覆盖。
- 页面无 section header 直接进入内容区。
- 底部无 tab bar（仅 home indicator）且全页为独立功能页。

## reference_blocks


## layout_skeleton

```html
<main class="layout-mobile-grid">
  <header class="layout-titlebar"></header>

  <section class="layout-content">
    <!-- Search 是 .layout-content 的首个内容项，初始 y≈100，与 titlebar 重叠 24px，
         但必须随纵向内容一起滚动。 -->
    <section class="layout-search-bar"></section>

    <!-- Hero 大卡区（水平滚动） -->
    <section class="layout-region layout-region-hero">
      <div class="layout-hero-scroll"></div>
    </section>

    <!-- 类别分类标签栏（chip 水平滚动） -->
    <section class="layout-chipstab"></section>

    <!-- 宫格卡片区（section header + 水平滚动卡片） -->
    <section class="layout-region layout-region-grid">
      <header class="layout-section-header"></header>
      <div class="layout-grid-scroll"></div>
    </section>

    <!-- 可选补充列表区 -->
    <section class="layout-region layout-region-list">
      <header class="layout-section-header"></header>
      <div class="layout-list-scroll"></div>
    </section>
  </section>

  <footer class="layout-bottom-bar">
    <div class="layout-bottom-floating-tab"></div>
    <div class="layout-miniplayer"></div>
  </footer>

  <div class="layout-home-indicator"></div>
</main>
```

## needed_components

- `title-bar` — 顶部 titlebar，包装在固定 124px 渐变背板壳层内
- `status-bar` — 顶部状态栏，作为 titlebar 壳层内的独立系统组件
- `search` — 浮动搜索条（详见 §local-component-mapping 备注）
- `chips-tab` — 横向 chip rail 中的单个 chip 按钮
- `hmsymbol-icon` — section / play / chevron 类系统图标
- `list-phone` — 补充列表区的 title/subtitle 行主体
- `floating-tab` — self-contained 4~5 tab 底部浮动导航，已包含底部手势指示条区域

## local_component_mapping

- statusbar: 使用 `@/components/StatusBar` 作为顶部 36px 状态栏；本地壳层只负责固定定位与渐隐背板。
- titlebar: 使用 `@/components/TitleBar`；本地壳层提供 124px 高度与常驻纵向渐隐背板。
- search bar: 使用 `@/components/Search`（Search=OFF variant）。**API mismatch**：Search 组件的固定尺寸为 343×40，而本布局的搜索条规格为 328×40，差 15px；搜索条居中渲染以匹配 360 画板。
- chip tab rail: 使用本地 `layout-chipstab__scroll` 作为水平滚动容器，单个 chip 使用 `@/components/ChipsTab`（`类型="tab"`，按 active 切换 `状态`）。`FloatingChipsTabPhone` 仍不适用，因为它无法表达每 chip 独立 label+可选 count。
- list region item: 左侧 48px cover 与右侧 chevron 由页面容器承载，title/subtitle 行主体使用 `@/components/ListPhone`（`行数="2"`，`right="None"`）。
- section / play / chevron 类图标: 使用 `@/components/HMSymbolIcon`，避免引入外部图标风格。
- bottom floating tab: 使用 `@/components/FloatingTab`（`layout="port"`，4 tab）作为 328×56 底部浮动导航；本地壳层只叠加 miniplayer affordance，不得再叠加独立 Aibottombar。
- bottom home indicator: `FloatingTab` 已自带底部手势指示条区域；禁止手写 5px 横条，也禁止额外渲染 `Aibottombar`。
- hero 大卡 / 宫格卡片：仍为页面级自定义内容块；列表项文本结构与 chip 原子使用本地组件承载。

## composition_mapping

| Layout Block | Component Reference | Variant / Composition | Layout Responsibility | Component Responsibility |
| --- | --- | --- | --- | --- |
| `statusbar` | `statusbar.md` | `harmony-statusbar` + `light` | 360×36，位于 titlebar 容器内部首位，独立组件节点 | 时间文本、PNG 图标资源（wifi/single-card/dual-card/battery） |
| `titlebar` | `titlebar.md` | `harmony-titlebar` + `normal` + 1 action（grid icon） | 占据顶部 124px 壳层（内含独立 statusbar 组件），标题「推荐」 | 常驻纵向渐隐背板、标题文本、右侧 icon button 渲染 |
| `search bar` | `search.md` | `harmony-search` + `off` + `normal` | 328×40 glass pill，作为 `.layout-content` 首项，初始位于 y≈100 | 搜索 icon、placeholder 文本、glass morphism 效果 |
| `Hero Card` | 无 — 页面级自定义 | 224×280 图片卡片，水平滚动 | 管理 hero scroll 容器 + 卡片间距 | 整图渲染，圆角 |
| `Chipstab` | `ChipsTab` + 页面级滚动容器 | `harmony-chipstab` + `类型=tab` | 473×52 类别标签栏，位于 hero 下方，管理横向滚动 | chip 项渲染、激活/非激活态、文本与可选 count |
| `Section Header`（grid） | `subheader.md` 或自定义 | 328×72，左侧推荐语 + 右箭头 | 区域标题头部 | 文本 + 可选箭头 |
| `Grid Card` | 无 — 页面级自定义 | 131×173，cover(131×131,r=8) + overlay + title | 管理 grid scroll 容器 + 卡片间距 | cover 图片、play count overlay（icon+text）、title 文本 |
| `Section Header`（list） | `subheader.md` 或自定义 | 176×56，左侧标题 + 红点指示 | 区域标题头部 | 文本 + 红点指示器 |
| `List Item`（list region） | `ListPhone` + 页面级封面/chevron | 48×48 封面图 + 2 行文本 + more icon，72px 高 | 管理 list scroll 容器 + divider + cover + chevron | title+artist 文本行主体 |
| `bottom bar` | `FloatingTab` | `harmony-floating-tab(4)` + `activeIndex=0` | 贴底 100px（含 56px floating tab + miniplayer + FloatingTab 自带 indicator 区域） | 4 tab 项、浮动玻璃 pill 与内置底部指示条 |

## spatial_tokens

### Horizontal
- 页面固定内容边距：`16px`。
- 水平滚动区域起始边距：`16px`。
- 宫格卡片间距：`8px`。
- Hero 卡片间距：`8px`。
- Section header 右箭头与文本间距：`8px`。

### Vertical
- titlebar → search bar：`-24px`（搜索栏顶部与 titlebar 底部重叠 24px）。
- search bar → hero region：约 `16px`。
- hero region → chipstab：约 `8px`。
- chipstab → grid region：约 `0px`。
- grid region → list region：间距由内容区自然流动。

## shell_rules

- 画板固定 `360 × 792`；页面背景使用 `background_secondary`。
- 顶部固定保留 titlebar `124px`（已内含 status bar）。
- 底部固定保留 `bottom bar` `100px`（含 FloatingTab pill + fold/miniplayer + FloatingTab 内置 indicator + gradient mask）。
- 水平滚动区域可超出视口宽度，无固定最大宽度。
- 内容区通过 `padding-top: 100px` 预留 search 初始视觉位置，`padding-bottom: 116px` 预留 bottom floating tab + 安全余量。

## stacking_context

| Layer | z-index | Positioning | Notes |
| --- | --- | --- | --- |
| `bottom floating tab` | 100 | `position: absolute; bottom: 0` | 包含 self-contained FloatingTab pill + fold/miniplayer + indicator |
| `search bar` (内容流首项) | 30 | `position: relative` | 随内容滚动，初始 y≈100 |
| `titlebar` | 10 | `position: absolute; top: 0` | 常驻纵向渐隐背板 |
| 内容区 | `auto` | `position: relative` | 不得设置 `z-index` / `transform` / `filter` / `opacity<1` / `isolation: isolate` |

## adaptive_behavior

- `.screen` 固定高度 `792px`，`overflow: hidden; display: flex; flex-direction: column`。
- 内容滚动委托给 `.layout-content`（`overflow-y: auto; flex: 1 1 auto; min-height: 0`）。
- 水平滚动容器 `overflow-x: auto; scroll-snap-type: x mandatory`，隐藏滚动条。
- 水平滚动容器只允许在主轴方向裁切；cross-axis 必须给卡片圆角、阴影和 overlay 留出空间。
- 末张卡片右侧保留适当余量（建议 16px），确保滚动到底时卡片不贴边。
- Grid Card cover 固定 131×131，图片使用 `object-fit: cover`；title 最多 2 行截断。
- Hero Card 尺寸固定 224×280，不接受内容驱动的尺寸变化。
- 玻璃元素使用统一 glass token 体系。

## semantic_tokens

| Semantic Part | Token |
| --- | --- |
| Page canvas | `background_secondary` |
| Titlebar title / section header title | `font_primary` |
| Grid card title | `font_primary` |
| Search placeholder / search icon | `font_secondary` |
| Play count text | `font_on_primary`（白色文字叠在深色渐变上） |
| List item subtitle / artist | `font_tertiary` |
| Chevron / more icon | `icon_tertiary` |
| Divider | `comp_divider` |
| Chipstab active chip bg | `floating_backgrount_emphasize`（品牌蓝） |
| Chipstab active chip text | `font_on_primary`（白色） |
| Chipstab inactive chip bg | `material_background_ultra_thin`（半透明） |
| Chipstab inactive chip text | `font_secondary` |
| Glass fill（search bar / FloatingTab / miniplayer） | glass token |
| Bottom tab active | `font_emphasize`（红色品牌色） |
| Bottom tab inactive | `font_primary` |
| Red dot indicator | `brand_red` 或 `#FF1949` |

## generation_constraints

- 禁止把整页实现为连续的匿名 frame 容器。
- 禁止把所有区块写成逐元素绝对定位；仅壳层级使用固定/sticky 定位。
- 水平滚动区域必须使用原生的 `overflow-x: auto` 或 `scroll`，不得用 JS 模拟滚动。
- Grid Card 内部必须防拉伸：cover 不随 title 长度变化而变形。
- 现有 `cardview.md` 的 variant 均不匹配 131×173 宫格卡片，禁止强行映射。
- Grid Card 暂时无组件 reference 对应，页面实现时作为容器级自定义块。
- 音乐首页若包含 miniplayer，底部导航必须优先使用仓内 `FloatingTab`，miniplayer 作为页面级浮层补充。
- FloatingTab 的容器背景必须来自组件自身材质；不要把 `.pixso-floating-tab` 自身写成不透明背景。
- 不得额外添加可见的整宽灰/白探针面板；如果底部内容已经延伸到栏后方，就不需要探针层。
- titlebar 背板必须为常驻纵向渐隐层；不得用 `scrollTop` / `.is-scrolled` 切换硬背板，不得在 titlebar 根节点添加整块 `backdrop-filter`。

## validation_notes

- 验收 checklist 参考原始 `.tmp/layout-grid.md` 的 §15。
- chipstab 类别标签栏：473×52，位于 hero 下方，滚动容器保留在页面模板内，chip 原子映射到 `ChipsTab`。
- 宫格卡片几何约束明确：131×173，cover 131×131 r=8，间距 8px。
- 水平滚动区域正确标记为 `layout-*-scroll`，overflow 约束已定义。
- Grid Card 的 reference 缺失已在 §composition_mapping 标注，映射策略已明确。
- search 初始 y≈100、随内容滚动、不得为 screen 直属固定浮层。
- titlebar 与下方首个卡片区域的直接间距已明确为 8px。
- `.layout-content` 未声明 `z-index` / `transform` / `filter` / `opacity<1` 等堆叠上下文属性。
- 壳层高度（titlebar 124 + bottom bar 100，self-contained FloatingTab）已正确扣除。
- Grid Card 内 cover、overlay、title 防拉伸约束已明确。
- 实现输出必须先满足 Composition Mapping，再做模板注入与样式微调。

## source

- 原始 reference: `.tmp/layout-grid.md`
- Pixso source node: `118:19305`（首页-直板机）
- Canvas: `360 × 792`
