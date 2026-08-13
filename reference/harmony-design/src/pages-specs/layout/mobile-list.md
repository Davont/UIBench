# Layout: mobile-list

> 移动端入口型列表页：以入口型 list item 的垂直堆叠为核心内容组织形式。
> 原始 source: `.tmp/layout-list.md` (Pixso source node `23:16731`, canvas `360 × 792`)

## hit_rules

命中 `mobile-list` 时，页面应同时满足以下特征：

- 画布为单屏移动端竖向比例 `360 × 792`，主内容位于居中的单列内容区（328px）。
- 顶部存在稳定壳层：`titlebar`。
- 主体内容以圆角卡片为核心容器，卡片按单列自上而下堆叠，卡片之间间距固定。
- 卡片内部为入口型 list item：左侧 `appicon + title + aux`，右侧 `value + chevron`。
- list item 是页面的主导内容组织形式，占页面内容区 50% 以上。
- 部分卡片为「组卡片」：多个 item 共享同一个圆角容器，item 之间以 divider 分隔。
- 部分卡片为「单卡片」：一个 item 独占一个圆角容器。

## exclusion_rules

出现以下任一特征时，不应优先命中该布局：

- 卡片内 item 以 switch / checkbox / picker 等**控件操作为主**（原地操作，非导航跳转） → 优先评估 `mobile-settings`。如果设置页的 item 以入口导航（chevron 跳转下级）为主，仍应命中本布局。
- 页面主体为内容 feed、网格、瀑布流或多列排版。
- 页面为表单录入、富内容详情、图表看板。
- 顶部存在 tab / segmented control 作为页面主导航。
- 页面有复杂分段 + subheader 层级管理（多个独立内容区块需要标题层级），且 list item 不是主导内容形式。
- list item 仅作为页面的附属元素（如 sidebar、drawer 内列表），而非页面主体。

## reference_blocks

- `settings-page`（区分参考）

## layout_skeleton

```html
<main class="layout-mobile-list">
  <header class="layout-titlebar"></header>

  <section class="layout-content">
    <!-- 可选 header 卡（profile / banner / summary） -->
    <section class="layout-card layout-card-header"></section>

    <!-- 组卡片：N 个 item 共享同一个圆角容器 -->
    <section class="layout-card layout-card-group-entry"></section>

    <!-- 单卡片：1 个 item 独占一个圆角容器 -->
    <section class="layout-card layout-card-single-entry"></section>
  </section>

  <footer class="layout-bottom-bar"></footer>
</main>
```

## needed_components

- `status-bar` — 顶部状态栏，作为 titlebar 壳层内的独立系统组件
- `floating-title-bar` — 顶部 titlebar，包装在固定 124px 渐隐背板壳层内
- `hmsymbol-icon` — entry item 的 right chevron / 系统符号图标
- `list-phone` — entry item 的标题、副标题、右侧值文本行主体
- `aibottombar` — 独立 / 二级页面的底部 28px 指示条
- `bottom-tab` — 多 tab 应用主页的 4-tab 底部 pill；仅当明确需要 FloatingTab 风格时才替换为 `floating-tab`

## local_component_mapping

- statusbar: 使用 `@/components/StatusBar` 作为顶部 36px 状态栏；本地壳层只负责固定定位与渐隐背板。
- titlebar: 使用 `@/components/TitleBar`，`category` 在 `showBack` 时切换为 `secondary page-phone`（带 back leading action），否则 `normal-phone`。
- entry item 行: 使用本地 `EntryItem` helper 组合 appicon 圆角容器 + `@/components/ListPhone` + `@/components/HMSymbolIcon` chevron。`ListPhone` 负责 title/subtitle/rightText 的行级排版；appicon 与独立 right chevron 由页面模板承担，以满足 48×48 appicon 和右箭头几何。
- header card: 页面级自定义块，非 List/ListItem 组件；保留本地 `layout-card-header`。
- 组卡片: 页面级自定义容器；保留本地 `layout-card-group-entry`。
- 多 tab 应用主页底部: 使用 `@/components/BottomTab`（`layout="port"`）替代手写 4-tab pill。
- 独立 / 二级页面底部: 使用 `@/components/Aibottombar`（`Color Mode="Light"`）作为 28px 指示条。

## composition_mapping

| Layout Block | Component Reference | Variant / Composition | Layout Responsibility | Component Responsibility |
| --- | --- | --- | --- | --- |
| `titlebar` | `titlebar.md` | `harmony-titlebar` + `normal` + actions | 占据顶部壳层区域（`normal` variant = 124px），内含 status bar + 标题 + action icon | status bar 时间/图标、标题文本与 action icon 渲染 |
| `Header Card` | `cardview.md` + 自定义 | `harmony-cardview` 容器 + 自定义 header 内容 | 可选：页面级自定义卡片 | `cardview` 提供容器几何与圆角；内容为页面级自定义 |
| `Group Entry Card` | `ListPhone` + 页面级 card/divider | `harmony-cardview` 容器，内含 N× entry item + (N-1)× inset divider | 圆角卡片容器，容纳 N 个 entry item + 分割线 + appicon/chevron | `ListPhone` 提供 title/subtitle/rightText 行主体 |
| `Single Entry Card` | `ListPhone` + 页面级 card | `harmony-cardview(mini)` 容器，内含 1× entry item | 80px 圆角卡片，容纳 1 个 entry item | 同上，无 divider |
| `layout-bottom-bar`（独立/二级页） | `aibottombar.md` | `harmony-aibottombar` + `light` | 贴底 28px，指示条 | 指示条渲染 |
| `layout-bottom-bar`（多 tab 主页） | `bottomtab.md` | `harmony-bottomtab(4)` + `activeIndex=3`（「我的」tab 活跃） | 贴底 100px（含 aibottombar 28px + tab pill 56px + padding），4 tab 项 | 4 个 tab 图标、标签、激活态渲染；若替换为 FloatingTab，则不再叠加独立 Aibottombar |

## spatial_tokens

### Horizontal
- 页面边距：`16px`（内容区 328px 居中于 360px 画布）。
- 卡片内边距：`12px`。
- 卡片圆角：`16px`。
- entry item 内 icon 与 title 间距：由 list 组件 `horizontal` 的 `gap: 16px` 承载。
- 右侧 value 与 chevron 间距：`4px`。

### Vertical
- titlebar 内容层底边 → 首张卡片或首个浮层内容间距 `8px`。
- Header Card（若存在）→ 下一张卡片间距 `12px`。
- Group Entry Card → 下一张卡片间距 `12px`。
- Single Entry Card 之间间距：`12px`。
- 最后一张卡片 → 底部 bar 间距：由内容区高度自然吸收。

## shell_rules

- 画板固定 `360 × 792`。
- 页面背景使用 `background_secondary`，卡片使用 `comp_background_primary`。
- 顶部 titlebar 固定在 screen 内（`normal` = 124px）；`.layout-content` 通过 `padding-top: 100px` 预留首张卡片的初始视觉位置。
- 独立 / 二级页面：`aibottombar` 区域 `28px`。
- 多 tab 应用主页：`bottomtab` 区域 `100px`（含 aibottombar 28px + tab pill 56px + padding）。
- 组卡片高度 = `4 + N×72 + (N-1)×1 + 4`；单卡片高度固定 `80px`（item 72px + 上下各 4px 内边距）。
- Group Entry Card 内的 divider 只存在于 N≥2 时；单 item 卡片不需要 divider。

## stacking_context

| Layer | z-index | Positioning | Notes |
| --- | --- | --- | --- |
| `bottomtab` | 100 | `position: absolute; bottom: 0` | 包含 tab pill + home indicator |
| 可滚动首项浮层（若存在 search / header glass card） | 30 | `position: relative` | 高于 titlebar，保证首屏位于 titlebar 之上 |
| `titlebar` | 10 | `position: absolute; top: 0` | 常驻纵向渐隐背板 |
| 内容区 | `auto` | `position: relative` | 不得设置 `z-index` / `transform` / `filter` / `opacity<1` / `isolation: isolate` |

## adaptive_behavior

- `.screen` 固定高度 `792px`，`overflow: hidden; display: flex; flex-direction: column`。
- 内容滚动委托给 `.layout-content`（`overflow-y: auto; flex: 1 1 auto; min-height: 0`）。
- titlebar 标题、entry item title（16px）和 entry item right text（14px）必须先按 P0/P1/P2 分类：P0 完整展示、禁止省略；P1 最多两行且行项/卡片高度自适应；只有 P2 可单行省略。`right text` 的最大宽度 `96px` 仅适用于已有明确紧凑约束的 P2 辅助信息，不得用于 P0 状态、数量或风险提示。
- Group Entry Card 高度 = `4 + N×72 + (N-1)×1 + 4`（N 为 item 数）。
- Single Entry Card 高度固定 80px。
- 卡片内 appicon、chevron、divider 等固定几何元素禁止被拉伸。
- 当总高度超过可用高度时触发滚动，不压缩卡片间距。

## semantic_tokens

| Semantic Part | Token |
| --- | --- |
| Page canvas | `background_secondary` |
| Card surface（所有圆角卡片） | `comp_background_primary` |
| Titlebar title / entry item title | `font_primary` |
| Entry item right value | `font_secondary` |
| Entry item appicon background | `comp_background_tertiary` |
| Chevron (12×24) | `icon_tertiary` |
| Divider inside group card | `comp_divider` |
| Hover overlay（list item） | `interactive_hover` |
| Pressed overlay（list item） | `interactive_pressed` |
| Bottom tab active label | `font_emphasize` |
| Bottom tab inactive label | `font_primary` |

## generation_constraints

- 禁止把整页实现为连续的匿名 frame 容器。
- 禁止把所有区块写成逐元素绝对定位；仅允许壳层级使用固定定位。
- 卡片内容必须以可复用的语义块（header card / group entry card / single entry card）组织。
- 卡片内部优先使用 `flex` 或纵向流式布局。
- entry item 内 appicon、title、aux、right text、chevron 必须防拉伸。
- 禁止卡片嵌套卡片；如需表达层级，优先通过卡片内部分区、行组、留白或分割线处理。
- 禁止在设置卡片上大面积使用渐变色阴影来凸显视觉。
- Entry item 必须映射到 S3 `icon2lines`，并按 `list-tem.html` 的模板真值实例化，不允许页面级重写内部结构。
- 禁止只复用 `.harmony-list` 类名后自定义内部结构。
- titlebar 背板必须为常驻纵向渐隐层；不得按滚动状态切换透明/模糊，不得追加整块 `backdrop-filter`。
- bottomtab 背后应优先由自然滚动内容、列表卡片或页面纹理提供玻璃材质所需的视觉信息。禁止额外添加可见的整宽灰/白矩形探针面板。

## validation_notes

- 验收 checklist 参考原始 `.tmp/layout-list.md` 的 §15。
- 主内容宽度统一为 `328px` 居中列。
- Header Card（若存在）被识别为页面级自定义块，不映射到 list 组件。
- Entry item 的 Composition Mapping 已直接命中现有 list reference 的 S3 `icon2lines` variant。
- 卡片被抽象为「Header Card（可选）/ Group Entry Card / Single Entry Card」三类。
- titlebar 固定顶部，背板为常驻纵向渐隐层；不得按 `scrollTop` / `.is-scrolled` 切换透明/模糊。
- 内容区通过 `padding-top` 预留首张卡片初始视觉位置，不按完整 titlebar 几何高度硬推内容。
- `.layout-content` 未声明 `z-index` / `transform` / `filter` / `opacity<1` 等堆叠上下文属性。
- Group Entry Card 高度 = `4 + N×72 + (N-1)×1 + 4`，未被 flex 二次压缩。
- `icon2lines` 行内左右 divider 在同一 72px 行底部齐平。
- entry item 的 hover / pressed 状态层已接入。
- 实现输出必须先满足 Composition Mapping，再做模板注入与样式微调。

## source

- 原始 reference: `.tmp/layout-list.md`
- Pixso source node: `23:16731`（illustration_Phone）
- Canvas: `360 × 792`
