# BottomTab

## Metadata

- Component id: `bottom-tab`
- Source path: `src/components/BottomTab/bottom-tab.tsx`
- Story path: `src/components/BottomTab/BottomTab.stories.tsx`
- Variant JSON: `src/components/BottomTab/bottom-tab.json`
- Pixso link: `https://pixso.cn/app/design/cjiPj-NOUA9kxV0f1bJ_og?item-id=5308:19547`
- Pixso item id: `5308:19547`
- MCP evidence (2026-05-28):
  - `get_node_dsl(itemId=5308:19547)` → 完整 DSL（247K），含 8 个 BottomTab-Phone 子变体
  - `design_to_code(itemId=5308:19547)` → React + CSS manifests
  - `get_screenshot` / `get_export_image` → 已导出截图
- Verification exports:
  - `5308:19483` for port example (2 items, `land=OFF`)
  - `5308:19431` for port 3 items
  - `5308:19391` for port 4 items
  - `5308:19363` for port 5 items
  - `5308:19299` for land example (5 items, `land=ON`)
  - `5308:19247` for land 4 items
  - `5308:19207` for land 3 items
  - `5308:19179` for land 2 items

## Purpose

`BottomTab` is the Harmony phone bottom navigation component defined by the Pixso showcase board at `5308:19547`.

Variant axes (from DSL `get_node_dsl`):
1. `个数`: `2 | 3 | 4 | 5`
2. `land`: `OFF | ON`
3. `Activated`: `OFF | ON` (per-item state)
4. `Color Mode`: `Light | Dark | Transparent` (handle tone)

## Component Variant Tree JSON

- File: `src/components/BottomTab/bottom-tab.json`
- Source: `get_node_dsl` + `get_all_components` cross-referenced with `get_variants` (returned empty; parsed from component names via regex)
- `variantOptions`: `个数`, `land`, `Activated`, `Color Mode`
- `pixTreeNodes`: 1 root (容器 9) with 8 BottomTab-Phone children matching DSL tree

## Quantitative Spec (from DSL)

### Overall dimensions

| Layout | Width | Total Height | Content Rail Height | Bottom Handle Area |
|--------|-------|-------------|---------------------|-------------------|
| Port (`land=OFF`) | 360px | **76px** | **48px** | 28px |
| Land (`land=ON`) | 360px | **68px** | **40px** | 28px |

### Port item (`.Port` — DSL `5314:17690`)

| Property | DSL value | Implementation |
|----------|-----------|---------------|
| stackMode | VERTICAL | `flex-col` |
| Width | `360 / 个数` px | grid column |
| Height | 48px | `h-12` |
| Icon size | 24×24px | `size-6` |
| Icon↔text gap | **2px** | `gap-[2px]` |
| Padding | **4px** all sides | `px-1 py-1` |
| Primary align | center | `justify-center` |
| Counter align | center | `items-center` |

### Land item (`.Land` — DSL `5314:18804`)

| Property | DSL value | Implementation |
|----------|-----------|---------------|
| stackMode | HORIZONTAL | `flex-row` |
| Width | `360 / 个数` px | grid column |
| Height | 40px | `h-10` |
| Icon size | 24×24px | `size-6` |
| Icon↔text gap | **8px** | `gap-2` |
| Padding | **8px** all sides | `px-2 py-2` |
| Primary align | center | `justify-center` |
| Counter align | center | `items-center` |

### Bottom Handle (`矩形` — DSL `5314:18817`)

| Property | DSL value |
|----------|-----------|
| Width | 112px |
| Height | 5px |
| Corner radius | 4px |
| Position | top: 17px within 28px rail |
| Light tone | `rgba(0,0,0,0.2)` |
| Dark tone | `rgba(255,255,255,0.5)` |
| Transparent tone | `rgba(255,255,255,0.7)` |

### Typography (text node — DSL `5314:17728`)

| Property | DSL value | Implementation |
|----------|-----------|---------------|
| fontFamily | HarmonyHeiTi | `[font-family:"HarmonyHeiTi","Geist_Variable",sans-serif]` |
| fontWeight | Medium (500) | `font-medium` |
| fontSize | 10px | `text-[10px]` |
| lineHeight | 14px (implied by 14px PARAGRAPH height) | `leading-[14px]` |
| letterSpacing | 0px | `tracking-[0px]` |
| textAlign (port) | center | `text-center` |
| textAlign (land) | left | `text-left` |

### Colors

| Role | DSL color | Global Token |
|------|-----------|-------------|
| Active text | `rgba(10,89,247,1)` | `--harmony-font-emphasize` |
| Inactive text | `rgba(0,0,0,0.6)` | `--harmony-font-secondary` |
| Active icon | `rgba(10,89,247,1)` | `--harmony-icon-emphasize` |
| Inactive icon | `rgba(0,0,0,0.4)` | `--harmony-icon-tertiary` |
| Surface fill | `rgba(241,243,245,0.8)` + `rgba(230,230,230,0.1)` | `--harmony-comp-background-material-tabs` (new) |
| Surface blur | `blur(80px)` | `--harmony-comp-background-material-tabs-blur` (new) |
| Handle Light | `rgba(0,0,0,0.2)` | `--harmony-comp-divider` (value matches) |
| Focus ring | brand blue | `--harmony-interactive-focus` |

### New `global.css` Tokens

| Token | Light value | Dark value |
|-------|------------|------------|
| `--harmony-comp-background-material-tabs` | `rgba(241,243,245,0.8)` | `rgba(25,26,28,0.8)` |
| `--harmony-comp-background-material-tabs-blur` | `blur(80px)` | `blur(80px)` |

Both added to `src/styles/global.css` in `:root` (system light) and `:root[data-theme="dark"]` sections.

## React API

```ts
type BottomTabItem = {
  key: string
  label: string
  icon: React.ReactNode
  activeIcon?: React.ReactNode
  disabled?: boolean
  onSelect?: (event: React.MouseEvent<HTMLButtonElement>) => void
}

type BottomTabProps = {
  items?: BottomTabItem[]
  activeKey?: string
  defaultActiveKey?: string
  onActiveKeyChange?: (key: string, item: BottomTabItem) => void
  layout?: "port" | "land"
  indicatorMode?: "Light" | "Dark" | "Transparent"

  // Pixso-compatible preview props
  个数?: "2" | "3" | "4" | "5"
  land?: "OFF" | "ON"
}
```

## DSL ↔ Prop Alignment

| Pixso / DSL field | React prop | Notes |
| --- | --- | --- |
| `个数` | `个数` | Preserved as-is. DSL values: `2`, `3`, `4`, `5`. Used when `items` is absent. |
| `land` | `land` | Preserved as-is. `ON` → horizontal item layout, `OFF` → vertical item layout. |
| `Activated` | `activeKey` / `defaultActiveKey` | Lifted from per-item variant state into controlled/uncontrolled navigation API. |
| `Color Mode` | `indicatorMode` | Applied to bottom handle tone. DSL values: `Light`, `Dark`, `Transparent`. |

## Storybook Coverage

- `playground`: single-instance controls entry
- `app-navigation-example`: production usage with 4 Chinese-labeled tabs
- `pixso-reference-example`: preview mode with 5 Pixso-matching tabs
- `controlled-example`: stateful navigation with `activeKey` + `onActiveKeyChange`
- `pixso-matrix`: all 8 `个数 × land` variants in a Matrix layout
- `indicator-modes`: `Light / Dark / Transparent` handle tones side by side

## Quality Notes

- `items`, `activeKey`, and `onActiveKeyChange` are the recommended API for production usage.
- `个数` and `land` are preserved as Pixso-compatible preview props for design review and Storybook matrices.
- Port height (76px) and land height (68px) are derived from DSL `get_node_dsl` measurements.
- Surface uses `--harmony-comp-background-material-tabs` with `backdrop-filter: blur(80px)` matching Pixso effect style `1:345`.
- Handle tone `Light` maps to `rgba(0,0,0,0.2)` matching DSL `--harmony-comp-divider`.
