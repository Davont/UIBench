# Layout: services-me

> Page Type: Services Me. 云服务个人中心页（我的页面），适用于阅读、视频、音乐、游戏、应用市场、主题、云空间&查找、浏览器等云服务类 App 的用户个人中心我的页面。原始 Pixso source 为 `云服务-我的页面`，节点 `36:3663`，画布 `360 × 792`。

## hit_rules

命中 `services-me` 时，页面应同时满足以下特征：

- 用户明确要求个人中心页、我的页面、用户中心页、个人主页、个人资产页。
- 页面是移动端个人中心，顶部为页面标题「我的」+ 消息入口，首屏核心为身份卡片（头像+姓名+勋章+会员中心入口）。
- 页面包含多个业务内容区块垂直串联，常见组合为 `IdentityCard`（身份卡片）+ `QuickActions`（快捷操作/用户资产）+ `FeedbackCard`（产品体验反馈）+ `CommonServices`（常用服务宫格）+ `ListCard`（公共区列表卡片）。
- 存在底部主导航，active tab 为「我的」。
- Prompt 中出现 `身份卡片`、`韩梅梅`、`用户资产`、`快捷操作`、`常用服务`、`公共区列表`、`会员中心`、`个人主页` 等已登记 Block/页面名称时，应优先命中本 page type，而不是泛化到 `mobile-list` 或 `mobile-grid`。

## exclusion_rules

- 仅为通用卡片流、无身份卡片 → 优先评估 `mobile-card`。
- 以宫格卡片为核心、无身份卡片锚定 → 优先评估 `mobile-grid`。
- 以入口列表、资产中心列表为核心但无身份卡片 → 优先评估 `mobile-list`。
- 顶部有沉浸式大 Hero → 优先评估 `services-home`。
- 设置 / 表单 / 后台管理 / 详情页 / 播放器页不命中本布局。
- 若页面只有单个 Block 展示，不构成完整个人中心模板，则先抽取或复用 Block，不生成本 page type。

## reference_blocks

- `identity-card` — 默认 IdentityCardSlot，用于用户身份卡片展示（头像+姓名+会员管理入口）；对应 block `src/blocks/identity-card/`。
- `quick-entry-card` — 默认 QuickEntryCardSlot，用于横向滚动快捷操作宫格（用户资产入口）；对应 block `src/blocks/quick-entry-card/`。
- `feedback-card` — 默认 FeedbackCardSlot，用于产品体验反馈入口卡片；对应 block `src/blocks/feedback-card/`。
- `service-list-card` — 默认 ServiceListCardSlot，用于公共区列表卡片（优惠券/金币/权益兑换/消费记录）；对应 block `src/blocks/service-list-card/`。
- `playlist-section-card` — 默认 PlaylistSectionCardSlot，用于播单区域卡片（自建/收藏播单计数+播单列表+查看全部）；对应 block `src/blocks/playlist-section-card/`。
- `recently-watching-grid-card` — 默认 RecentlyWatchingGridCardSlot，用于最近在追宫格卡片（2×3 视频宫格含封面+评分/集数角标）；对应 block `src/blocks/recently-watching-grid-card/`。

## layout_skeleton

```html
<main class="layout-services-me">
  <header data-slot="statusBarSlot"></header>

  <header data-slot="titleBarSlot"></header>

  <section class="layout-content">
    <section data-slot="identityCardSlot"></section>
    <section data-slot="quickEntryCardSlot"></section>
    <section data-slot="feedbackCardSlot"></section>
    <section data-slot="serviceListCardSlot"></section>
    <section data-slot="playlistSectionCardSlot"></section>
    <section data-slot="recentlyWatchingGridCardSlot"></section>
  </section>

  <footer data-slot="bottomNavSlot"></footer>
</main>
```

## layout_runtime

| 能力 | 源码支撑 | 说明 |
| --- | --- | --- |
| 页面实现 | `src/pages/services-me/ServicesMePage.tsx` | 360×792 固定移动端页面壳 |
| IdentityCard slot | `identityCardSlot?: ReactNode` + `showIdentityCard` | 默认渲染身份卡片（头像+姓名+勋章+个人主页+会员中心）；可替换为同类用户卡片 block 或隐藏 |
| QuickActions slot | `quickActionsSlot?: ReactNode` + `showQuickActions` | 默认渲染横向滚动快捷操作宫格（5 个入口），可替换为同尺寸快捷入口 |
| FeedbackCard slot | `feedbackCardSlot?: ReactNode` + `showFeedbackCard` | 默认渲染 NPS 反馈卡片（标题+描述+插图+关闭按钮），可替换或隐藏 |
| Services slot | `servicesSlot?: ReactNode` + `showServices` | 默认渲染 4 列常用服务宫格（8 个入口含「更多」），可替换为同类服务入口 |
| ListCard slot | `listCardSlot?: ReactNode` + `showListCard` | 默认渲染公共区列表卡片（4 行列表），可替换为同类列表 |
| 页面标题 + 消息入口 | `showPageHeader` / `showMessageAction` | 页面标题「我的」与消息图标按钮必须通过 Header 区域渲染；消息按钮可单独隐藏 |
| 滚动顶部遮罩 | `isScrolled` state | 内容向上滚动时顶部渐变遮罩（`--harmony-background-secondary` → transparent） |
| 底部导航 slot | `bottomNavSlot?: ReactNode` + `showBottomNav` | 默认 `FloatingTab` 4 个 Tab，active 为「我的」；可替换或隐藏 |

## fixed_blocks

| Block / Component | 位置 | 是否必选 | 说明 |
| --- | --- | --- | --- |
| status-bar | Header 顶部 | 否 | 默认显示，Light 模式 |
| title-bar | Header | 否 | 页面标题「我的」必须渲染；消息 IconButton 可单独隐藏 |
| bottom floating tab | bottomNavSlot | 否 | 默认 4 Tab 主导航，active=「我的」；若业务无底部 tab 可隐藏 |

## slots

| Slot | 默认 Block | 可替换 Block 清单 | 是否必选 | 说明 |
| --- | --- | --- | --- | --- |
| IdentityCardSlot | `identity-card` | `identity-card` / profile-card / user-card / none | 是 | 页面核心锚定区块：头像+姓名+会员管理入口；用户明确要求替换时只替换此槽 |
| QuickEntryCardSlot | `quick-entry-card` | `quick-entry-card` / quick-actions / asset-grid / quick-entry-rail / none | 否 | 横向滚动快捷操作入口宫格；可替换为同尺寸横向 rail |
| FeedbackCardSlot | `feedback-card` | `feedback-card` / nps-card / promo-banner / none | 否 | 产品体验反馈卡片含插图；可替换或隐藏 |
| ServiceListCardSlot | `service-list-card` | `service-list-card` / list-card / entry-list / link-list / none | 否 | 公共区列表卡片（优惠券/金币/权益兑换/消费记录） |
| PlaylistSectionCardSlot | `playlist-section-card` | `playlist-section-card` / playlist-grid / collection-card / none | 否 | 播单区域卡片（自建/收藏播单计数+播单列表+查看全部） |
| RecentlyWatchingGridCardSlot | `recently-watching-grid-card` | `recently-watching-grid-card` / watching-grid / video-grid / none | 否 | 最近在追宫格卡片（2×3 视频宫格含封面+评分/集数角标） |
| BottomNavSlot | `floating-tab` | `floating-tab` / bottom-tab / none | 否 | 4 Tab 主导航，active=「我的」 |

## visibility_rules

| 区域 | 默认 | 显隐 prop | 何时隐藏 |
| --- | --- | --- | --- |
| StatusBar | 显示 | `showStatusBar` | 外部壳层已提供系统状态栏时隐藏 |
| PageHeader | 显示 | `showPageHeader` | 外部壳层已提供标题栏时隐藏 |
| MessageAction | 显示 | `showMessageAction` | 页面无消息入口时隐藏 |
| IdentityCardSlot | 显示 | `showIdentityCard` | 外部已提供用户身份信息时隐藏 |
| QuickActionsSlot | 显示 | `showQuickActions` | 业务无快捷操作入口时隐藏 |
| FeedbackCardSlot | 显示 | `showFeedbackCard` | 业务无反馈入口时隐藏 |
| ServicesSlot | 显示 | `showServices` | 业务无常用服务入口时隐藏 |
| ListCardSlot | 显示 | `showListCard` | 业务无公共区入口时隐藏 |
| BottomNavSlot | 显示 | `showBottomNav` | 页面嵌入到已有 tab shell 时隐藏 |

## needed_components

- `status-bar`
- `icon-button`
- `floating-tab`
- `hmsymbol-icon` 或 `lucide-react` 图标
- `divider`

## composition_mapping

| 页面区域 | 优先使用 | 可替换为 | 说明 |
| --- | --- | --- | --- |
| StatusBarSlot | `StatusBar` | none | 默认 Light 模式；不得手写匿名 status bar 替代 |
| TitleBarSlot | 页面 `<header>` + `<h1>`「我的」+ `IconButton` | none | 标题字阶 `Font/Title_L/Bold` 30px/700；消息按钮 `Icon={1}` `尺寸={40}` |
| IdentityCardSlot | `IdentityCard` | 同类 profile/user card block | 默认 328×128，圆角 20px；白色卡片 + LINEAR_DODGE 高光叠加；包含头像圆形渐变、姓名、3 个勋章 badge、个人主页入口、分割线、底部文本+红点、会员中心按钮（`#D3B685`）；身份卡片支持 3 个变体：默认（会员管理样式）/ Compact（仅头像+姓名+个人主页 328×72）/ Icon Badges（勋章仅图标无文字 20×20） |
| QuickActionsSlot | 页面级 quick actions scroll | `chips-tab` 组合 / 横向 rail | 外层 clip 圆角 20px，内层横向 scroll；item 尺寸 69×76，5 个入口；icon 容器 40×40 含 28×28 图标；红点 6×6 绝对定位右上角 |
| FeedbackCardSlot | 页面级 feedback card | 同类 NPS / promo banner | 白色卡片圆角 20px，padding 24px 20px 24px 12px；左侧标题+描述，右侧 98×74 插图（PNG）；右上角 16×16 关闭按钮 |
| ServicesSlot | 页面级 common services grid | 同类 service/tool grid | 白色卡片圆角 20px，padding 4px 12px；4 列 grid gap 4px；8 个入口含「更多」（三点网格 SVG 图标）；item 垂直列 gap 6px, padding 12px 4px, 圆角 12px；hover/active 交互反馈 |
| ListCardSlot | 页面级 `ListCard` | 同类 entry/link list | 白色卡片圆角 20px，padding 4px 12px；行高 56px；左侧 24×24 icon + 16px/500 label + 可选红点；右侧 14px text + 16px chevron；分割线 0.5px，left=36px |
| BottomNavSlot | `FloatingTab` 4 Tab | `BottomTab` / none | 默认 4 个 Tab（Tab / Tab / Tab / 我的），active=「我的」；整体贴底；FloatingTab 自带底部手势指示条，不得额外叠加 `Aibottombar` |

## spatial_tokens

- 画布：`360 × 792`。
- 页面背景：`--harmony-background-secondary` = `#F1F3F5`，非白色。
- StatusBar：高 `36px`，Light 模式。
- Header：y 紧接 StatusBar，padding `8px 16px 12px`，flex row space-between；标题 `Font/Title_L/Bold` = 30px / 700 / 36px。
- 内容区：absolute top=92px（StatusBar 36 + Header ~56），bottom=0，overflow-y auto；padding `8px 16px 16px`；子元素 gap `10px`。
- 滚动遮罩：内容区 scrollTop > 0 时 `.is-scrolled::after` 显示，40px 高，top=92px，z-index 10，`linear-gradient(to bottom, --harmony-background-secondary 0%, transparent 100%)`。
- IdentityCardSlot：宽 `328px`（360 - 16×2），最小高 `128px`，圆角 `20px`，内 padding `12px 12px 14px`；白色卡片 + `::before` LINEAR_DODGE 双渐变高光（`linear-gradient(135deg, rgba(255,255,255,0.20) 0%, rgba(255,255,255,0) 100%)` ×2）。
  - 头像：`48×48` 圆形，灰色渐变 (`linear-gradient(180deg, rgba(255,255,255,0.6), rgba(255,255,255,0.2))` + `linear-gradient(135deg, #c8c8c8, #a0a0a0)`)，文字 `22px/700/24px #fff`。
  - 用户名：`Font/Subtitle_L/Medium` 18px / 500 / 24px，`--harmony-font-primary`。
  - 勋章 badges：`44×16` each，gap `4px`，文字 `Font/Caption_S/Regular` 8px / 400 / 16px，带背景图片。
  - 个人主页：absolute right，垂直居中，`Font/Body_M/Regular` 14px / 400 / 20px，`--harmony-font-tertiary`，hover→secondary，active→primary。
  - 分割线：`0.5px`，`--harmony-comp-divider`，margin `12px 0`。
  - 底部文本行：`Font/Body_M/Regular` 14px / 400 / 20px，`--harmony-font-secondary`，红点 `6×6` `--harmony-warning`。
  - 会员中心按钮：`72×28`，圆角 `14px`，背景 `#D3B685`，文字 `#4D4339`，`Font/Body_M/Medium` 14px / 500 / 16px；hover opacity 0.85，active 0.7。
  - Compact 变体：最小高 `72px`，padding `12px 12px`，无分割线和底部行。
  - Icon Badges 变体：勋章 `20×20`，无文字，使用图标 PNG。
- QuickActionsSlot：宽 `328px`，最小高 `104px`，圆角 `20px`；白色卡片 + LINEAR_DODGE 高光同 IdentityCard。
  - 内层 scroll：padding `14px 0 14px 8px`，横向滚动，隐藏 scrollbar。
  - item 尺寸：`69×76`，垂直列 gap `4px`，flex-shrink 0。
  - icon 容器：`40×40`，padding `10px`，内含 `28×28` 图标。
  - label：`Font/Body_S/Regular` 12px / 400 / 16px，`--harmony-font-primary`。
  - subtitle：10px / 400 / 14px，`--harmony-font-tertiary`。
  - 红点：`6×6` 圆形，absolute 右上角，`--harmony-warning`。
- FeedbackCardSlot：宽 `328px`（全宽减去 padding），高 `82px`，圆角 `20px`，padding `24px 20px 24px 12px`；白色背景。
  - 标题：`Font/Subtitle_L/Bold` 18px / 700 / 26px。
  - 描述：`Font/Caption_L/Regular` 12px / 400 / 16px，`--harmony-font-tertiary`。
  - 插图：`98×74`，margin-left `16px`，flex-shrink 0。
  - 关闭按钮：`16×16`，absolute top=8px right=8px，opacity 0.6，hover 1.0。
- ServicesSlot：宽 `328px`（全宽减去 padding），最小高 `232px`，圆角 `20px`，padding `4px 12px`；白色背景。
  - 标题：`Font/Subtitle_L/Medium` 18px / 500 / 24px，padding `12px 0 8px`。
  - 网格：`grid-template-columns: repeat(4, 1fr)`，gap `4px`。
  - item：垂直列 gap `6px`，padding `12px 4px`，圆角 `12px`；hover `--harmony-interactive-hover`，active `--harmony-interactive-pressed`。
  - label：12px / 16px，`--harmony-font-primary`，text-align center。
- ListCardSlot：宽 `328px`（全宽减去 padding），圆角 `20px`，padding `4px 12px`；白色背景。
  - 行高：`56px`，flex row space-between，gap `12px`。
  - 左侧：24×24 icon + 16px/500/22px label + 可选 6×6 红点，gap `12px`。
  - 右侧：14px/400/20px rightText（`--harmony-font-secondary`）+ 16px chevron（`--harmony-icon-fourth`），gap `4px`。
  - 分割线：`0.5px`，absolute bottom，left=36px。
  - clickable 行：hover `rgba(0,0,0,0.04)`，active `rgba(0,0,0,0.08)`，focus-visible outline `2px rgba(10,89,247,0.4)`。
- 底部 spacer：高 `84px`，flex-shrink 0（为 FloatingTab 56px tab pill + 28px 内置底部手势指示条预留空间）。
- BottomNavSlot：absolute bottom，全宽；FloatingTab 4 Tab，active=「我的」；不再渲染独立 Aibottombar。

## shell_rules

- 页面固定为 360px 宽移动端壳层，居中于预览容器。
- 根背景为 `--harmony-background-secondary` = `#F1F3F5`，对齐 Pixso Frame fill。
- StatusBar 与 Header 正常流顶部；内容区 absolute top=92px 可纵向滚动。
- 内容区子区块（IdentityCard / QuickActions / FeedbackCard / Services / ListCard）全部为白色卡片，圆角统一 `20px`。
- IdentityCard 与 QuickActions 卡片使用 `::before` LINEAR_DODGE 双渐变高光叠加，不得省略。
- 底部预留 84px spacer，FloatingTab 浮动贴底。
- slot 为 `none` 或 `show* = false` 时不保留空白容器。

## stacking_context

| Layer | z-index | Positioning | Notes |
| --- | --- | --- | --- |
| 滚动遮罩 | 10 | absolute top=92px | `.is-scrolled::after` 渐变遮罩，pointer-events none |
| 卡片高光 | 0 (::before) | absolute inset | IdentityCard / QuickActions LINEAR_DODGE 高光 |
| 内容区 | auto | absolute top=92px | scrollable，子区块正常流 |
| bottomNavSlot | auto（FloatingTab 自身管理） | absolute bottom=0 | `360 × (56+28)` self-contained FloatingTab |

## adaptive_behavior

- 当前 page type 只覆盖竖屏手机页面；宽度保持 360px。
- 内容区允许纵向滚动；Header / StatusBar 不随内容滚动。
- QuickActions 可横向滚动，末尾保留右侧 padding。
- 常用服务固定 4 列网格，不响应宽度变化。
- 替换 block 必须能在 328px 宽容器内稳定渲染（页面 padding 16px × 2）。

## semantic_tokens

| Semantic Part | Token / Value |
| --- | --- |
| Page canvas | `--harmony-background-secondary` `#F1F3F5` |
| Card background | `--harmony-comp-background-primary` `#FFFFFF` |
| Primary text | `--harmony-font-primary` `rgba(0,0,0,0.898)` |
| Secondary text | `--harmony-font-secondary` `rgba(0,0,0,0.6)` |
| Tertiary text | `--harmony-font-tertiary` `rgba(0,0,0,0.4)` |
| Divider | `--harmony-comp-divider` `rgba(0,0,0,0.2)` |
| Warning / red dot | `--harmony-warning` `#E84026` |
| Interactive hover | `--harmony-interactive-hover` `rgba(0,0,0,0.04)` |
| Interactive pressed | `--harmony-interactive-pressed` `rgba(0,0,0,0.08)` |
| Interactive focus | `--harmony-interactive-focus` `rgba(10,89,247,0.4)` |
| Member button bg | `#D3B685` (会员金色，无对应 token) |
| Member button text | `#4D4339` (会员深棕，无对应 token) |
| Avatar gradient | `linear-gradient(180deg, rgba(255,255,255,0.6), rgba(255,255,255,0.2))` + `linear-gradient(135deg, #c8c8c8, #a0a0a0)` |
| Card highlight | `linear-gradient(135deg, rgba(255,255,255,0.20) 0%, transparent 100%)` ×2 |
| Scroll fade | `linear-gradient(to bottom, #F1F3F5 0%, transparent 100%)` |

## generation_constraints

- `services-me` 默认组合必须保留 `identity-card`、`quick-actions`、`feedback-card`、`common-services`、`list-card` 五个内容 slot；身份卡片是页面核心锚定区块，默认命中，只有用户明确替换时才传入其他 `identityCardSlot`。
- 顶部页面标题「我的」和消息入口不得手写匿名 header 替代；标题必须用 `<h1>`，消息按钮必须调用 `IconButton` 组件（`Icon={1}`, `尺寸={40}`）。
- 身份卡片必须包含三个子区域：顶部行（头像+姓名+勋章+个人主页）、分割线、底部行（文本+红点+箭头+会员中心按钮）。不要遗漏 LINEAR_DODGE 高光叠加。
- 快捷操作卡片必须使用双层容器模式：外层 clip 圆角，内层横向 scroll。不得使用单层容器。
- 反馈卡片右侧插图必须为 PNG 图片（`assets/nps-illustration.png`），不得省略。
- 常用服务第 8 个入口为「更多」使用三点网格 SVG 图标，其余 7 个使用五角星 SVG 图标（来自 DSL）。
- 公共区列表卡片每行 56px 高，分割线从 x=36px 开始（从 icon 右侧），不得全宽。
- 底部 FloatingTab 固定 4 个 Tab，active 为「我的」；Tab wrapper 贴底。
- 内容区滚动顶部渐变遮罩仅在 `scrollTop > 0` 时显示，初始状态无遮罩。
- 可隐藏 slot 隐藏后不保留空白容器。
- 不要把本页面错误命中到 `mobile-list` 或 `mobile-grid`：本模板的核心是身份卡片锚定的个人中心页，不是入口型列表页或宫格首页。
- 不要将整个 Pixso 页面作为单张图片；必须保留 slot 装配能力。
- 使用语义化 token，不使用硬编码颜色值（会员金色按钮 `#D3B685` / `#4D4339` 除外）。

## validation_notes

- `src/pages/services-me/ServicesMePage.tsx` 已提供身份卡片、快捷操作、反馈卡片、常用服务宫格、公共区列表卡片和底部 FloatingTab 的完整实现。
- `src/pages/services-me/services-me.css` 覆盖所有区块的完整 CSS 样式（696 行），包括身份卡片三种变体（默认 / Compact / Icon Badges）。
- `src/pages/services-me/services-me.json` 包含 Pixso DSL 变体树：10 个变体属性 + 5 个 Pixso 子实例节点。
- Storybook: `Pages/ServicesMe`，Playground 和 Default 两个 Story。
- 资产文件：`assets/badge-1.png`, `assets/badge-2.png`, `assets/badge-3.png`, `assets/badge-icon-1.png`, `assets/badge-icon-2.png`, `assets/badge-icon-3.png`, `assets/nps-illustration.png`。
- Pixso `design_to_code(36:3663)` 可能返回 500；本 spec 使用 `get_screenshot` + `get_node_dsl` 校准页面骨架、尺寸和默认内容。
- 身份卡片子节点 `41:614` 单独通过 DSL 还原，支持变体切换。

## source

- Pixso: `https://pixso.cn/app/design/f3YuUJ1DHBrZxJcUHOJeYg?item-id=36:3663`
- Node: `36:3663`
- Node name: `云服务-我的页面`
- 身份卡片子节点: `41:614` (User Profile Card)
- Canvas: `360 × 792`
