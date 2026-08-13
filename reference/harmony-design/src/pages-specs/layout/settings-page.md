# Page Template: settings-page

> 页面模板说明：`settings-page` 是 `mobile-settings` 布局族下的通用设置页模板。
> 实现位置：`src/pages/settings-page-template/`
> 外部来源：`dragonestdwolf/Vibe-UI-Forge`（public fork of `JunLR/Vibe-UI-Forge`），
> 原始 spec: `.resources/harmony/layout/settings-page.md`，原始 TSX: `harmony-ui-playground/src/pages/settings-page.tsx`。
> 本仓库版本对外引用做了本地化翻译（见 §translation_notes）。

## hit_rules

当需求命中 `mobile-settings`，并且同时满足以下特征时，优先参考 `settings-page`：

- 页面标题为「设置」或通用系统设置语义，而不是某个单一功能设置页
- 主体由多组设置卡片组成，每组包含 1 到 3 个设置项
- 设置项类型混合出现：开关项、值展示项、跳转项
- 设置项左侧通常有图标，右侧可能有 Switch、值文本、箭头或状态说明
- 页面内容覆盖多个系统类别，如网络、显示、通知、安全、存储、语言、系统更新、关于设备
- 页面长度可超过单屏，需要保留竖向滚动或自然延展空间

## exclusion_rules

出现以下任一特征时，不应优先使用该模板：

- 只围绕单一功能配置，例如喝水提醒、提醒时间、目标设定，应使用 `settings-page` 的分组/行项节奏裁剪生成，而不是完整复刻通用系统设置页内容
- 页面主体为健康任务、进度可视化、卡片任务列表
- 页面主体是底部半模态浮层
- 页面需要表单提交、复杂输入或固定底部主操作按钮
- 页面主要内容是图表、信息流、详情页、网格卡片或营销内容

## reference_blocks

- `settings-page`

## layout_skeleton

```html
<main class="template-settings-page">
  <section class="template-status-bar"></section>
  <header class="template-titlebar"></header>
  <section class="template-content">
    <section class="template-setting-group template-setting-group-network"></section>
    <section class="template-setting-group template-setting-group-display"></section>
    <section class="template-setting-group template-setting-group-notification"></section>
    <section class="template-setting-group template-setting-group-security"></section>
    <section class="template-setting-group template-setting-group-storage"></section>
    <section class="template-setting-group template-setting-group-system"></section>
    <section class="template-setting-group template-setting-group-about"></section>
  </section>
  <footer class="template-home-indicator"></footer>
</main>
```

### Layout Family

| Field | Value |
|---|---|
| layout_family | `mobile-settings` |
| page_template | `settings-page` |
| source_block | `src/pages/settings-page-template/settings-page-template.tsx` |
| viewport | `360px` width, **fixed** `792px` height (NOT min-height) |
| content_width | `328px` |

## needed_components

- `status-bar` — 36px 系统状态条
- `floating-title-bar` — 顶部 titlebar（secondary header variant，带 back leading action）
- `hmsymbol-icon` — 设置行左侧系统图标
- `list-phone` — 设置行文本和值/跳转主体
- `switch-phone` — 设置行开关
- `aibottombar` — 底部 home indicator pill

## local_component_mapping

- status bar: 使用 `@/components/StatusBar`（`Color Mode="Light"`）。
- titlebar: 使用 `@/components/TitleBar`（`category="secondary page-phone"`，通过 `leadingAction={{ kind: "back" }}` 提供返回按钮）。
- switch row: 使用 `@/components/SwitchPhone`（`Selected="ON" | "OFF"`）。
- bottom home indicator: 使用 `@/components/Aibottombar` 取代手写 5px 横条。
- setting row leading icon: 普通设置行直接使用 `ListPhone left="24dp_ic" leftIconName={row.icon}`；`ListPhone` 负责左侧 24px Symbol、文本列与 divider 的几何。彩色图标瓦仅在设计稿明确要求时使用受控 tile 变体，并在页面日志记录设计稿依据；不得以 `leftSlot`、匿名 `div` 或 `<HMSymbolIcon size={20} />` 自行拼装默认设置行。

## composition_mapping

| Template Region | Component | Source Pattern (Adapted) |
|---|---|---|
| `status bar` | `StatusBar` | `<StatusBar Color Mode="Light" />`，背景与页面 canvas 一致 |
| `titlebar` | `TitleBar` | `<TitleBar category="secondary page-phone" title="设置" leadingAction={{ kind: "back", label: "Back" }} />` |
| `setting group` | 本地 `SettingsGroup` 容器 | 圆角 20px 白色卡片，`margin-top: 12px`（`mt-3`），组间 12px 节奏 |
| `switch row` | `ListPhone` + `SwitchPhone` | `<ListPhone left="24dp_ic" leftIconName={row.icon} right="Switch" title="..." />` + `<SwitchPhone Selected="ON" />` |
| `value row` | `ListPhone` | 固定传 `left="24dp_ic" leftIconName={row.icon}`；仅 value 行传 `rightText="当前值"`，根据页面需要使用 `right="Text"` 或 `right="Arrow"`（值 + chevron） |
| `link/jump row` | `ListPhone` | 固定传 `left="24dp_ic" leftIconName={row.icon}` + `right="Arrow"`，仅 chevron |
| `group divider` | 1px hairline | `border-top: 1px solid var(--harmony-comp-divider)`，组内首项不画、末项不画 |
| `home indicator` | 本地 indicator 行 | 360×28，底部居中 112×5 圆角指示条 |

## generation_constraints

- 生成通用设置页时，优先读取 `settings-page-template.tsx` 的分组节奏和行项组合方式
- 不要把 `settings-page` 当成组件 API；它是页面模板 block
- 保留 `360px` 页面宽度和 `328px` 主内容宽度的移动端壳层约束
- 多组设置卡片应使用本地 `SettingsGroup` 容器 + `ListPhone`，不要自由拼接匿名 div 行项
- 禁止卡片嵌套卡片；设置分组之间保持平铺堆叠，不通过在组卡片内部再包一层卡片制造层级
- 禁止在设置卡片上大面积使用渐变色阴影来凸显视觉；如需强调，仅允许轻量、克制的实色阴影或边框对比
- 开关设置必须使用 `SwitchPhone`
- 跳转设置右侧应保持 `value + chevron` 或单独 `chevron` 的结构
- 设置行数据必须使用 `kind` 判别联合：`link` 行禁止 `value`，`value` / `accentValue` 行必须有非空 `value`，`switch` 行必须有 `defaultChecked`。渲染时只为 value 类行传 `rightText`，不得统一传 `row.value`。
- 普通设置行左侧系统图标必须使用 `ListPhone left="24dp_ic" + leftIconName`；禁止使用 `leftSlot`、匿名 `div` 或 `<HMSymbolIcon size={20} />` 改写默认图标尺寸或容器。
- 只有设计稿明确要求彩色图标瓦、头像或图片时才允许脱离普通 `24dp_ic` 模式；必须使用受控变体并在页面日志记录设计稿依据。彩色图标瓦的前景色遵循 `hmsymbol-icon` 规格：饱和底板使用 `--harmony-icon-on-primary`，浅 tint 底板才允许深色图标。
- 如果需求是单一功能设置页，应复用 `settings-page` 的壳层、分组节奏和行项组合方式，并裁剪为更小的设置组
- `.template-content` 不得设置 `z-index` / `transform` / `filter` / `opacity<1` / `isolation: isolate`
- `titlebar` 背板为常驻纵向渐隐层；不得用 `scrollTop` / `.is-scrolled` 切换硬背板，不得在 titlebar 根节点添加整块 `backdrop-filter`

## semantic_tokens

| Semantic Part | Template Usage |
|---|---|
| Page canvas | `comp_background_gray` |
| Group card surface | `comp_background_primary` |
| Primary text | setting title, titlebar text — `font_primary` |
| Secondary text | right-side value, status description — `font_secondary` |
| Accent value text | `font_emphasize`（如「已是最新」品牌色） |
| Interactive control | `SwitchPhone` |
| Navigation affordance | chevron icon — `icon_tertiary` |
| Divider inside group | `comp_divider` |
| Group spacing | `mt-2`（首组与 titlebar 间距 8px）、`mt-3`（组间 12px）、`mt-4`（末组与 home indicator 间距 16px） |

## source_grounding

默认读取（已迁移至本仓库）：

- `src/pages/settings-page-template/settings-page-template.tsx`
- `src/pages/settings-page-template/settings-page-template.css`

按需读取（本仓库 component）：

- `src/components/StatusBar/StatusBar.tsx`
- `src/components/TitleBar/title-bar.tsx`
- `src/components/ListPhone/ListPhone.tsx`
- `src/components/SwitchPhone/SwitchPhone.tsx`
- `src/components/Aibottombar/Aibottombar.tsx`
- `src/components/IconButton/IconButton.tsx`

## translation_notes

外部 `dragonestdwolf/Vibe-UI-Forge` 资源到本仓库的翻译决策：

| External (`harmony-ui-playground`) | This repo | Decision |
| --- | --- | --- |
| `@/component/StatusBar` | `@/components/StatusBar` | 直接映射，名称为 `StatusBar` |
| `@/component/TitleBar` | `@/components/TitleBar` | 直接映射，名称为 `TitleBar`，API 字段不同（`title` / `leadingAction` 等） |
| `@/component/List` + `ListItem` | `@/components/ListPhone` | 使用 `ListPhone` 单文件变体承载行级布局；variant 通过 `right` / `行数` props 表达 |
| `@/component/Switch` | `@/components/SwitchPhone` | 使用 `SwitchPhone`，`Selected="ON"\|"OFF"` 表达开关态 |
| `comp-background-gray`（Tailwind token） | `var(--harmony-comp-background-gray)`（CSS 变量） | 通过 `src/styles/global.css` 的 CSS 变量直接绑定 |
| `icon-chevron-backward.png` / `icon-arrow-right-small.png`（外部 pixso 资源） | lucide-react icons (`ChevronLeft`, `ChevronRight`) + 本地 inline SVG | 外部 pixso 资源未引入本仓库；使用 lucide 与本地 SVG 替代 |
| `mt-2` / `mt-3` / `mt-4`（Tailwind utility） | `margin-top: 8px / 12px / 16px`（CSS） | 本模板的 CSS 不依赖 Tailwind utility class |

不做的事：

- 不复制外部仓库的 `package.json` 依赖。
- 不复制外部 import alias `@/component/*`。
- 不在运行时依赖 `/tmp/Vibe-UI-Forge-eval` 或 `dragonestdwolf/Vibe-UI-Forge` 任何路径。
- 不把 `settings-page-v30`（display/brightness 详细页）当作通用 `settings-page` 的真值来源；它是一个更具体的渲染变体。

## validation_notes

- 本 spec 的 `reference_blocks` 必须能被设计系统资源校验流程通过
- 验收时确认不存在组卡片内部再包卡片的结构
- 验收时确认卡片强调未依赖大面积渐变色阴影
- 生成页至少需要通过 `npm run build-storybook`
- 静态检查命令（来自原始 `Acceptance Criteria`）：
  - `rg "Pages/SettingsPage|SettingsPageTemplate|settings-page" src/pages src/pages-specs src/route-index.md src/blocks-specs`
  - `rg "@/component|/tmp/Vibe-UI-Forge" src/pages src/pages-specs src/route-index.md src/blocks-specs`
  - 上述命令在 settings-page-template 范围内不得命中外部 import alias 或 `/tmp` 路径

## variant_notes

- `settings-page`：通用系统设置（多组多类）。
- 具体的 `settings-page-v30` 等「display/brightness 详情页」是更具体的渲染变体，不替代通用模板。
