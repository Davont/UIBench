# Layout: settings-context-list

## overview

设置二级页通用布局的一种类型：页面整体 `360px` 宽度居中呈现；顶部固定 StatusBar + TitleBar（居中于页面宽度内），二者之间 gap=0；中部为灵活业务卡片区（支持居中或满宽横滑）；底部为固定 list 卡片组合（卡片间距 12，可内嵌 slider）。适用于"先呈现/预览，后调参/控制"的设置二级页。支持 light / dark 双主题，背景色通过 `background` 参数控制。

## hit_rules

- 情景模式 / 免打扰
- 显示与亮度
- 云空间
- 智慧多窗
- 需要顶部业务可视化（轮播、预览、对比图、容量环等）+ 下方多组设置卡的二级设置页
- 主内容由 1 个"居中业务展示卡 / 可滑动卡组" + 多个"list 卡片"自上而下垂直堆叠
- 可在 list 卡片中放置 Slider、Switch 控件

## exclusion_rules

- 通用一级"设置"主页（多组设置 list 但无业务展示卡）→ 命中 `mobile-settings`
- 顶部存在 tab / segmented control 作为页面主导航
- 页面主体为表单录入、富文本详情、信息流
- 半模态浮层场景
- 健康任务进度卡片为主体
- 底部存在固定主 CTA / 双按钮操作栏

## layout_skeleton

```text
Page
├── AppShell                       # 360 × 800 移动端壳层，居中于视口
│   ├── HeaderSlot                 # 固定 title 区，居中于页面 (gap-between=0)
│   │   ├── status-bar             #   贴顶，居中，36px
│   │   └── title-bar              #   紧贴状态栏，居中，56px，左返回 + 标题 + 右图标组
│   ├── ContextSlot                # 灵活 context 区
│   │   └── FeaturePromoCard       #   FeaturePromoCard 单卡或横向轮播组合 / 预览 / 容量环 / 对比图
│   ├── ListGroupSlot              # 固定 list 区（卡片间距 12px）
│   │   ├── subheader[?]           #   可选副标题标签（subtitle），紧贴下方 list 卡片，间距为 0
│   │   ├── list-card[1]           #   list 卡片，可含 list-item / switch / slider
│   │   ├── list-card[2]
│   │   └── list-card[n]
│   └── FooterSlot                 # 底部说明 / 安全区，默认隐藏
└── HomeIndicator                  # 底部 Home Indicator，28px
```

### Shell Rules

| 区域 | 高度 | 说明 |
|------|------|------|
| AppShell | 360px 宽度，居中于视口 | 容器层；背景色由 `background` 参数决定，支持 light/dark 切换 |
| status-bar | 36px | 贴顶，居中于 360px 壳层内，gap-below=0 |
| title-bar | 56px | 紧贴状态栏，居中于 360px 壳层内，无间距 |
| ContextSlot | flex | 灵活高度，依据业务卡片自适应 |
| ListGroupSlot | flex | 居中于 328px 主内容区；多张 list 卡片之间 gap=12px |
| HomeIndicator | 28px | 底部系统区域，居中 |

### Content Width
- **壳层宽度**：`360px`
- **主内容标准宽度**：`328px`（左右各 `16px` 边距，居中于壳层内）
- **ContextSlot 扩展宽度**：`360px` 满宽（用于横向轮播卡等需要突破边距的场景）
- **卡片水平安全边距**：ContextSlot 内的卡片（无论静态居中还是横向轮播）距页面两侧最小 **16px**，推荐 **32px**；使用满宽轮播（`contextWidth="bleed"`）时，轨道内须以 `padding-inline` 保留该边距，不得让卡片贴边。

### ContextSlot 间距规范
- ContextSlot 距上方内容（TitleBar 或描述文本）间距为 **8 的倍数**，最小 **16px**，推荐 **24px / 32px / 40px**。
- 若 ContextSlot 下方紧接 Subheader（`leftMode="text"`），则间距为 **0**（gap=0）。
- **卡片水平边距**：ContextSlot 内卡片距页面左右两侧最小 **16px**，推荐 **32px**；满宽轮播轨道应使用 `padding-inline: 32px`（至少 16px）保留该边距，不得贴边。
- **轮播居中对齐**：当 ContextSlot 为横向轮播时，当前选中卡片须居中展示（`scroll-snap-align: center`）；两侧可见区域宽度 = `(360px − 卡片宽度) / 2`，左右对称露出。

### SubHeader 间距约束
| 相邻组件关系 | 间距值 | 说明 |
|---|---|---|
| SubHeader → list-card | **0px** | SubHeader 下方紧接 list 卡片，间距为 0 |
| SubHeader → FootnoteText | **8px** | SubHeader 下方紧接纯文本（功能说明等），间距为 8px |
| SubHeader → 导航点组件 | **-12px** | SubHeader 上方接入导航点（dots）时，使用负 margin 拉近 |

### 文字规范（Typography）

| 文本位置 | 字体参数 | 颜色 Token | 颜色值（Light） | 颜色值（Dark） |
|---|---|---|---|---|
| TitleBar 下方副文本（页面描述） | `Font/Subtitle_S/Regular`（14px / lh 22px / wt 400） | `Light/font_secondary` | `rgba(0,0,0,0.6)` | `rgba(255,255,255,0.6)` |
| list 卡片下方说明文本（footnote） | `Font/Body_S/Regular`（12px / lh 18px / wt 400） | `Light/font_secondary` | `rgba(0,0,0,0.6)` | `rgba(255,255,255,0.6)` |

- **TitleBar 副文本**：TitleBar 下方可选放置一段页面描述副文本，说明本页功能概要，宽度对齐 328px 主内容区，颜色使用 `font_secondary`（非 `font_tertiary`）。
- **list 卡片说明文本**：list 卡片下方的功能说明、注意事项等辅助文字，使用 `footnote-text` 语义类，距上方卡片 8px，颜色同样使用 `font_secondary`。

## layout_runtime

| 能力 | 源码支撑 | 说明 |
|---|---|---|
| Slot 装配 | `mobile-phone-shell-template` + `status-bar` + `title-bar` + `list`/`list-phone` | 装配 HeaderSlot / ContextSlot / ListGroupSlot / FooterSlot |
| Header 零间距 | `HeaderSlot.gap=0` | StatusBar 与 TitleBar 之间不留间距 |
| 居中呈现 | `AppShell` | 页面整体 `360px` 宽度居中于视口，StatusBar 和 TitleBar 均居于 360px 壳层中心 |
| 双主题背景 | `background` 参数 | `background="#F1F3F5"`（light）或 `background="#000000"`（dark），ThemeProvider 驱动切换 |
| List 卡片间距 | `ListGroupSlot.gap=12` | 多张 list 卡片之间统一 12px 垂直间距 |
| ContextSlot 满宽 | `contextWidth="bleed"` | 横向轮播等场景可通过 `contextWidth="bleed"` 突破 328px 限制至 360px |
| 显隐控制 | `showContext` / `showFooter` | 控制业务区与底部区是否渲染 |
| 空 slot | `none` | slot 为 none 时不保留空容器 |
| Slider 嵌入 | `list-item.right=<Slider/>` 或 整行替换 | 允许 list-card 内放置滑块控件 |

## fixed_blocks

| Block | 位置 | 是否必选 | 说明 |
|---|---|---|---|
| status-bar | HeaderSlot | 是 | 系统状态栏，居中于 360px 壳层，theme 跟随 `background` 参数 |
| title-bar | HeaderSlot | 是 | 标题栏，居中于 360px 壳层，左返回；右侧图标组按需 |
| list-card | ListGroupSlot | 是 | 至少一张 list 卡片，圆角 20–24px |
| subheader | ListGroupSlot | 否 | 可选副标题标签，置于 list 卡片上方，距下方 list 卡片间距为 0 |

## slots

| Slot | 默认 Block | 可替换 Block 清单 | 是否必选 | 说明 |
|---|---|---|---|---|
| HeaderSlot | title-bar | title-bar / search-header | 是 | 状态栏 + 标题栏组合，二者间距固定为 0 |
| ContextSlot | FeaturePromoCard | scene-mode-carousel / FeaturePromoCard / display-mode-preview / cloud-storage-overview / multi-window-preview / hero-promo-card / none | 否 | 业务展示卡片；可横向滚动（轮播）或纵向静态卡；多卡时使用横向 scroll-snap 轨道 |
| ListGroupSlot | settings-list-group | settings-list-group / slider-list-group / grouped-list-section | 是 | list 卡片堆叠，可选 subheader 副标题置于最上方，距下方 list 卡片间距为 0 |
| SubheaderSlot | subtitle | subtitle / none | 否 | 副标题标签（使用 `leftMode="text"` + `text` 属性），紧贴下方 list 卡片，**subheader 与 list 卡片间距为 0**（gap=0） |
| FooterSlot | none | footer-note / bottom-actions / none | 否 | 底部说明文案或操作 |

## visibility_rules

| 区域 | 默认 | 何时隐藏 |
|---|---|---|
| HeaderSlot | 显示 | 永远显示，不可隐藏 |
| ContextSlot | 显示 | 页面无业务展示需求时隐藏（直接进入 list 区） |
| ListGroupSlot | 显示 | 永远显示，不可隐藏 |
| FooterSlot | 显示 | 需要底部说明或底部操作时显示 |

## needed_components

- status-bar
- title-bar
- subheader
- list
- list-item
- switch
- swiper（按需）
- slider
- divider（按需）
- FeaturePromoCard（按需）
- icon-tile（按需，list-item 左侧图标）

## reference_blocks

- settings-page
- scenario-mode-page-v3（FeaturePromoCard 在 ContextSlot 横向轮播的典型实现）
- grouped-list-section（SubHeader + list-card + footnote 的标准分组 block）

## composition_mapping

| 页面区域 | 优先使用 | 可替换为 | 说明 |
|---|---|---|---|
| HeaderSlot | title-bar | search-header | 是否需要搜索；二者均与 status-bar 紧贴 |
| ContextSlot | FeaturePromoCard | scene-mode-carousel / FeaturePromoCard / display-mode-preview / cloud-storage-overview / multi-window-preview / none | 选择匹配业务的展示卡片；多卡时使用横向 scroll-snap 轨道（如 `scenario-mode-page-v3` 三卡轮播） |
| ListGroupSlot | settings-list-group | slider-list-group / grouped-list-section | 含 subtitle 或 footnote 时优先 grouped-list-section；含 Slider 时可在 grouped-list-section 内承载 slider-list-group |
| SubheaderSlot | subtitle | none | **副标题标签（使用 `leftMode="text"` + `text` 属性）**，置于 list 卡片上方，**subheader 与下方 list 卡片间距为 0**（gap=0）；使用 `font_tertiary` token；**一般无右侧蓝色操作按钮**（`rightMode` 应为 `none`） |
| ContextSlot 间距 | 16px / 24px / 32px / 40px | — | ContextSlot 距上方内容（TitleBar 或描述文本）间距为 8 的倍数，最小 16px，推荐 24 / 32 / 40px；若 ContextSlot 下方紧接 Subheader 则间距为 0 |
| Subheader → 导航点 | -12px | — | Subheader 上方接入导航点（dots）组件时，间距为 -12px（拉近） |
| ContextSlot 卡片水平边距 | padding-inline ≥ 16px，推荐 32px | — | 卡片距页面两侧最小 16px，建议 32px；bleed 轮播轨道须在容器内设 padding-inline 保留边距，不得贴边 |
| ContextSlot 轮播选中卡居中 | scroll-snap-align: center | — | 当前选中卡片居中展示；两侧可见卡片露出量 = (360 − 卡片宽) / 2，左右对称推算 |
| Subheader → list-card | 0px | — | Subheader 下方紧接 list 卡片，间距为 0 |
| Subheader → Subheader | 12px | — | 两个 Subheader 之间，间距为 12px |
| List 卡片间距 | gap-12 | — | 列表内不同模块内容之间，间距为 12px |
| list-card → FootnoteText | 8px | — | list 卡片下方接入纯文本，间距为 8px |
| 卡片内行项 | list-item | list-item + switch / list-item + slider / list-item + value+chevron | 依据交互类型选择 |
| FooterSlot | none | footer-note | 需展示策略说明 / 跳转个性化设置时显示 |
| List 卡片下方副文本 | FootnoteText / footnote | — | 副文本距上方 list 卡片间距固定为 8px |
| TitleBar 副文本字体 | `Font/Subtitle_S/Regular` | — | 14px / lh 22px / wt 400；颜色 `font_secondary`（`rgba(0,0,0,0.6)`）；宽度对齐 328px 主内容区 |
| list-card 说明文本字体 | `Font/Body_S/Regular` | — | 12px / lh 18px / wt 400；颜色 `font_secondary`（`rgba(0,0,0,0.6)`）；距上方卡片 8px |

## generation_constraints

- 只能从 slots 的可替换 Block 清单中选择，不要临时发明新 Block。
- 如果 slot 选择 `none`，对应区域不要保留空白容器。
- **居中约束**：页面整体 `360px` 宽度居中于视口；StatusBar 和 TitleBar 均居于壳层中心（CSS `margin: 0 auto`），不可偏左或偏右。
- HeaderSlot 中 status-bar 与 title-bar 之间间距必须为 0；不允许插入 padding / margin / 任何中间区块。
- **背景色约定**：通过 `background` 参数控制。Light 模式使用 `#F1F3F5`，Dark 模式使用 `#000000`；不得硬编码背景色。
- ListGroupSlot 内多张 list 卡片之间的垂直间距固定为 12px；首张卡片距 ContextSlot 间距 ≥ 16px。
- **ContextSlot 间距约束**：中间业务卡片（ContextSlot）距上方内容（TitleBar 或描述文本）间距为 **8 的倍数**，最小 **16px**，推荐 **24px / 32px / 40px**。
- **ContextSlot + Subheader 间距**：若 ContextSlot 下方紧接 Subheader（`leftMode="text"`），则 ContextSlot 距 Subheader 间距为 **0**（gap=0）。
- **SubheaderSlot 间距约束**：subheader 距下方 list 卡片间距为 0（gap=0），不得插入任何额外间距。
- **grouped-list-section 约束**：当 list-card 同时带有 subheader 和/或 footnote 时，必须包裹在 `grouped-list-section` 中作为一个整体 block 参与 `ListGroupSlot` 排布；父级 `ListGroupSlot.gap=12` 只作用于 section 与 section 之间，section 内部 `gap=0`。
- **Subheader 样式规范**：当 Subheader 位于 list 卡片上方时，一般仅使用 `text` 内容，**无右侧蓝色操作按钮**（`rightMode` 应为 `none` 或不加 rightMode）；仅有 text 的 Subheader 视觉更简洁。
- **Footnote 间距约束**：list 卡片下方副文本（如功能说明、注意事项）距上方 list 卡片间距为 8px；该 8px 属于 `grouped-list-section` 内部规则，不应由 `ListGroupSlot` 的外部 gap 产生。
- **TitleBar 副文本字体约束**：TitleBar 下方若放置页面描述副文本，字体参数必须使用 `Font/Subtitle_S/Regular`（14px / line-height 22px / font-weight 400），颜色使用 `Light/font_secondary`（`rgba(0,0,0,0.6)`）；dark 模式使用 `rgba(255,255,255,0.6)`；不得使用 `font_tertiary` 或其他颜色 token。
- **list 卡片说明文本字体约束**：list 卡片下方说明文本（footnote）字体参数必须使用 `Font/Body_S/Regular`（12px / line-height 18px / font-weight 400），颜色使用 `Light/font_secondary`（`rgba(0,0,0,0.6)`）；dark 模式使用 `rgba(255,255,255,0.6)`；间距遵循 8px 上边距约束。
- **Subheader 与上方组件间距**：Subheader 距上方组件一般为 0px；若上方为导航点（dots）组件则间距为 -12px（使用负 margin 拉近）。
- **Subheader 与下方组件间距**：Subheader 距下方 list 卡片间距为 0px。
- **Subheader 之间间距**：两个 Subheader 之间（如"条件开启"与"智能推荐"）间距为 12px。
- **列表内模块间距**：list 卡片之间、不同模块内容之间间距为 12px。
- ContextSlot 高度由业务卡片决定，不要对 ContextSlot 设硬编码高度；横向轮播必须支持 `scroll-snap`；多张 FeaturePromoCard 横向排列时使用 `display:flex + gap-12 + overflow-x:auto + scroll-snap-type:x mandatory` 轨道组合。
- **ContextSlot 卡片水平边距约束**：ContextSlot 内卡片（居中卡或轮播卡）距页面两侧最小 **16px**，推荐 **32px**；使用 `contextWidth="bleed"` 横向轮播时，轨道容器须内设 `padding-inline`（至少 16px，建议 32px），**不得让卡片直接贴边**；选中卡片须居中对齐（`scroll-snap-align: center`），两侧可见卡片的露出量按 `(360px − 卡片宽度) / 2` 对称推算。
- list 卡片圆角统一为 20–24px，背景为 `comp_background_primary`，与页面背景保持对比。
- **list 图标规范**：普通设置行左侧系统图标统一使用 `ListPhone left="24dp_ic" + leftIconName`，前景为 `icon_primary`。只有设计稿明确要求时才使用受控彩色图标瓦；饱和、不透明彩色或渐变底板使用 `icon_on_primary` 浅色前景，浅 tint 底板才允许深色图标。禁止通过 `leftSlot`、匿名 `div` 或 `<HMSymbolIcon size={20} />` 自行拼装默认设置行；例外须在页面日志记录设计稿依据。
- list 卡片内允许嵌入 `slider`，应与 list-item 同列对齐；slider 行不再追加箭头。
- Markdown 中声明的 slot 和显隐规则，layout 源码必须有对应能力。
- 页面中的 Component 必须来自 `components.json`。
- 页面中的 Block 必须来自 `blocks.json` 或 layout 明确允许的 reference_blocks。
- 如果需要裁剪 Block 内部区域，先参考对应 `block/*.md` 的可隐藏规则。
- 保留 `360px` 页面宽度和 `328px` 主内容宽度的移动端壳层约束；ContextSlot 横滑卡组可至 `360px` 满宽。
- 设置行优先复用 list / list-item；普通系统图标走 `ListPhone left="24dp_ic" + leftIconName`，不要自由拼接匿名 div。

## semantic_tokens

| Semantic Part | Light Token | Dark Token |
|---|---|---|
| Page canvas（壳层背景） | `comp_background_gray` `#F1F3F5` | `comp_background_gray` `#000000` |
| Card surface（list 卡片背景） | `comp_background_primary` `#FFFFFF` | `comp_background_primary` `#1A1A1A` |
| Title / primary labels | `font_primary` `rgba(0,0,0,0.9)` | `font_primary` `rgba(255,255,255,0.9)` |
| Right-side value / note | `font_secondary` `rgba(0,0,0,0.6)` / `font_tertiary` `rgba(0,0,0,0.45)` | `font_secondary` `rgba(255,255,255,0.6)` / `font_tertiary` `rgba(255,255,255,0.45)` |
| Brand accent | `brand_blue` `#0A59F7` — 用于强调、Switch on、Slider 轨道 | `brand_blue` `#0A59F7`（保持一致） |
| Primary icons | `icon_primary` | `icon_primary`（跟随 token 变化） |
| Secondary icons / chevron | `icon_secondary` | `icon_secondary`（跟随 token 变化） |
| List 内图标（普通 list-item left） | `icon_primary`（`ListPhone left="24dp_ic"`） | `icon_primary`（跟随主题） |
| List 内图标（设计稿指定彩色 tile） | `icon_on_primary`（饱和底板）/ `icon_primary`（浅 tint 底板） | 按底板对比度选择同等语义 token |
| Subheader / Section label | `font_tertiary` `rgba(0,0,0,0.45)` | `font_tertiary` `rgba(255,255,255,0.45)` |
| Divider | `comp_divider` | `comp_divider`（跟随 token 变化） |
| TitleBar 下方副文本（页面描述） | `font_secondary` `rgba(0,0,0,0.6)` — `Font/Subtitle_S/Regular` 14px/22px/400 | `font_secondary` `rgba(255,255,255,0.6)` |
| list-card 下方说明文本（footnote） | `font_secondary` `rgba(0,0,0,0.6)` — `Font/Body_S/Regular` 12px/18px/400 | `font_secondary` `rgba(255,255,255,0.6)` |

> **List 图标规范**：普通设置行使用 `ListPhone left="24dp_ic" + leftIconName` 与 `icon_primary`。设计稿指定的彩色图标瓦是受控例外：饱和底板使用 `icon_on_primary` 浅色图标，浅 tint 底板才使用深色图标；不得将“不得使用纯白图标”应用于彩色 tile 场景。

### Background 参数约定

| 主题 | `background` 值 | 使用场景 |
|---|---|---|
| Light | `#F1F3F5`（鸿蒙 `comp_background_gray`） | 通用设置二级页，如情景模式、显示与亮度等 |
| Dark | `#000000`（鸿蒙 `comp_background_gray` dark） | 深色模式下的全屏深色页 |
| 页面可定制 | `#FFFFFF` 或其他 | 纯白背景覆盖场景（如 V2 免打扰页） |

组合 `mobile-phone-shell-template`、`status-bar`、`title-bar` 与列表区时，通过页面根容器 background 或主题 token 传入；ThemeProvider 驱动主题切换时，同步更新该参数值。

## validation_notes

- ContextSlot 与 ListGroupSlot 必须能独立验收：context 卡片可单独故事预览，list 组合可单独故事预览。
- list 卡片间距测量必须为 12px（允许 ±1px 渲染误差）。
- HeaderSlot 中 status-bar 底边与 title-bar 顶边像素级贴合（gap=0）。
- 生成页至少需要通过 `npm run build`；新增 stories 通过 `npm run build-storybook`。
- ContextSlot 内卡片（静态或轮播）距页面两侧边距不得小于 16px；推荐 32px；bleed 轮播轨道的 `padding-inline` 应可在 DevTools 中测量验收。
- 横向轮播的选中卡片须视觉上居中于 360px 壳层内；两侧露出量应左右对称（`scroll-snap-align: center` + `scroll-padding-inline` 对齐）。
- TitleBar 下方副文本颜色必须为 `rgba(0,0,0,0.6)`（Light）/ `rgba(255,255,255,0.6)`（Dark），字号 14px，行高 22px，不得使用 `rgba(0,0,0,0.45)` 或其他透明度值。
- list 卡片下方说明文本颜色必须为 `rgba(0,0,0,0.6)`（Light）/ `rgba(255,255,255,0.6)`（Dark），字号 12px，行高 18px；与上方卡片间距必须为 8px。
