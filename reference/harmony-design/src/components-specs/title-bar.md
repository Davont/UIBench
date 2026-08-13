# TitleBar

## Metadata

- Component id: `title-bar`
- Source path: `src/components/TitleBar/title-bar.tsx`
- Story path: `src/components/TitleBar/TitleBar.stories.tsx`
- Variant tree JSON: `src/components/TitleBar/title-bar.json`
- Pixso link: `https://pixso.cn/app/design/cjiPj-NOUA9kxV0f1bJ_og?item-id=5308:19178`
- Pixso item id: `5308:19178`
- MCP evidence (2026-05-28):
  - `get_node_dsl(itemId=5308:19178)` → 完整 DSL（159K），含 4 个变体 Frame
  - `get_all_components` → 提取 TitleBar 组件集属性名（`.Items`: `Icon`/`通透度`，`.icon left`: `属性1`）
  - `get_screenshot` → 成功
  - `design_to_code` → Failed (500)
  - `get_variants` → 空 `{}`

## Purpose

`TitleBar` is the Harmony phone title-header component for Pixso frame `5308:19178`.

Pixso component set `2.TitleBar - 标题栏` 含 3 个子组件集：

| 组件集 | Pixso 属性 | Pixso 取值 |
|--------|-----------|-----------|
| `.icon left` | `属性1` | `icon with title`, `icon with head` |
| `.Items` | `Icon` | `1`, `2`, `3` |
| `.Items` | `通透度` | `默认`, `材质-标准`, `材质-强`, `材质-降档`, `材质-弱` |
| `.ToolBar` | `组数` | `2..17`（非本组件关注） |

## Component Variant Tree JSON

- File: `src/components/TitleBar/title-bar.json`
- `variantOptions` now maps Pixso property names exactly: `Icon`, `通透度`, `属性1`
- All 4 categories have real Pixso guids from `get_node_dsl`

## Quantitative Spec (from DSL)

### Overall dimensions

| Category | Width | Height | Layout |
|----------|-------|--------|--------|
| normal-phone | 328px | 56px | HORIZONTAL, gap=8, counter=center |
| secondary page-phone | 328px | 56px | HORIZONTAL, gap=8 |
| title with icons-phone | 328px | 137px | VERTICAL (items 56px + title area 81px) |
| drawer-phone | 328px | 56px | HORIZONTAL, gap=8 |

### Icon Button

| Property | DSL value | Implementation |
|----------|-----------|---------------|
| Size | 40×40px | `size-10` |
| Corner radius | 1000px (circle) | `rounded-full` |
| Icon size | 24×24px | `size-6` |
| Icon color | `rgba(0,0,0,0.898)` | `--harmony-icon-primary` |
| Background | inherit (translucent) | `--harmony-comp-background-tertiary` |
| Gap between buttons | 8px | `gap-2` |

### Typography

| Category | Role | Font | Weight | Size | Line height | Color |
|----------|------|------|--------|------|-------------|-------|
| normal-phone | Title | HarmonyHeiTi | Bold | 26px | 35px | `--harmony-font-primary` |
| secondary page | Title | HarmonyHeiTi | Bold | 20px | 27px | `--harmony-font-primary` |
| secondary page | Subtitle | HarmonyHeiTi | Regular | 14px | 19px | `--harmony-font-secondary` |
| title with icons | Title | HarmonyHeiTi | Bold | 30px | 40px | `--harmony-font-primary` |
| title with icons | Subtitle | HarmonyHeiTi | Regular | 14px | 19px | `--harmony-font-secondary` |
| drawer | Title | HarmonyHeiTi | Bold | 26px | 35px | `--harmony-font-primary` |

### title with icons-phone layout

| Property | DSL value | Implementation |
|----------|-----------|---------------|
| .title-left height | 81px | implied by 137 - 56 |
| .title-left padding top | 8px | `pt-2` |
| .title-left padding bottom | 12px | `pb-3` |
| subtitle↔title gap | 2px | `gap-[2px]` |
| Subtitle order | ABOVE title | `{subtitleEl}{titleEl}` |
| letterSpacing | 0px all texts | `tracking-[0px]` |

### Visual Tokens

All color roles map to existing Harmony tokens — no new `global.css` tokens required.

| Role | Global Token |
|------|-------------|
| Title text | `--harmony-font-primary` |
| Subtitle text | `--harmony-font-secondary` |
| Icon color | `--harmony-icon-primary` |
| Icon button bg | `--harmony-comp-background-tertiary` |
| Icon button hover | `--harmony-interactive-hover` |
| Focus ring | `--harmony-interactive-focus` |

## React API

```ts
type TitleBarCategory =
  | "normal-phone"
  | "secondary page-phone"
  | "title with icons-phone"
  | "drawer-phone"

type TitleBarAction = {
  id?: string
  icon: React.ReactNode
  label: string
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void
  disabled?: boolean
}

type TitleBarLeadingAction = {
  kind?: "back" | "drawer"
  icon?: React.ReactNode
  label: string
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void
  disabled?: boolean
}

type TitleBarProps = {
  category?: TitleBarCategory
  title?: string
  subtitleText?: string
  subtitle?: boolean
  headingLevel?: 1 | 2 | 3 | 4 | 5 | 6
  leadingAction?: TitleBarLeadingAction | null
  actions?: TitleBarAction[]
  // Pixso `.Items` — 右侧图标按钮数量（预览模式）
  Icon?: 1 | 2 | 3
  // Pixso `.Items` — 图标按钮材质透明度
  通透度?: "默认" | "材质-标准" | "材质-强" | "材质-降档" | "材质-弱"
  // Pixso `.icon left` — 左侧图标区模式
  属性1?: "icon with title" | "icon with head"
  titleLeftSize?: "big title+subtitle"
  // @deprecated 向后兼容
  rightIcon?: boolean
  leftIcon?: boolean
}
```

## DSL ↔ Prop Alignment

| Pixso 组件集 / DSL 源 | React prop | DSL 取值 | 备注 |
| --- | --- | --- | --- |
| Frame variant name | `category` | `normal-phone`, `secondary page-phone`, `title with icons-phone`, `drawer-phone` | 直接映射 |
| `.Items` → `Icon` | `Icon` | `1`, `2`, `3` | 右侧图标按钮数量；预览模式用，生产用 `actions` |
| `.Items` → `通透度` | `通透度` | `默认`, `材质-标准`, `材质-强`, `材质-降档`, `材质-弱` | 图标按钮材质透明度 |
| `.icon left` → `属性1` | `属性1` | `icon with title`, `icon with head` | 左侧图标区模式 |
| `.title-left` | `titleLeftSize` | `big title+subtitle` | 仅 title-with-icons |
| Business abstraction | `leadingAction` | `TitleBarLeadingAction` | 从左侧 icon 节点升级 |
| Business abstraction | `actions` | `TitleBarAction[]` | 从 `.Items` icon 节点升级 |

## Storybook Coverage

- `playground`: single-instance controls entry（含 `Icon`、`通透度` 下拉控件）
- `pixso-matrix`: renders all 4 DSL categories
- `normal-phone` / `secondary page-phone` / `title with icons-phone` / `drawer-phone`: 逐类 story

## Change Log

- 2026-05-28 (v2): Props 硬对齐 Pixso 真实属性名 — `itemsIcon`→`Icon`、`itemsOpacity`→`通透度`（扩充到 5 个取值）、新增 `属性1`。来源：`get_all_components` 解析 Pixso 组件名 `属性=值` 格式。
- 2026-05-28 (v1): `get_node_dsl` 成功。修正 title-with-icons 副标题/标题顺序、padding、subtitle leading。variant JSON 更新为真实 Pixso guid。
