# FloatingTitleBar

## Metadata

- Component id: `floating-title-bar`
- Source path: `src/components/Navigation/FloatingTitleBar/FloatingTitleBar.tsx`
- Story path: `src/components/Navigation/FloatingTitleBar/FloatingTitleBar.stories.tsx`
- Styles: `src/components/Navigation/FloatingTitleBar/floating-title-bar.css`
- Variant tree JSON: `src/components/Navigation/FloatingTitleBar/floating-title-bar.json`
- Pixso link: `https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5368:23368`
- Pixso item id: `5368:23368`
- Related dark gradient backing node: `https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5451:96`
- MCP evidence:
  - `design_to_code(itemId=5368:23368, react)` -> failed with 500
  - `get_screenshot(itemId=5368:23368)` -> success, 4x4 visual matrix
  - `get_variants(itemId=5368:23368)` -> empty `{}`
  - `get_node_dsl(itemId=5368:23368)` -> success, root frame `FLoatingTitleBar` 1790x747 with `FloatingTitleBar` instances, StatusBar, TitleBar subframes, material fills/effects
  - `get_export_image(itemId=5368:23368)` -> saved as `src/components/Navigation/FloatingTitleBar/pixso-reference.png`

## Purpose

`FloatingTitleBar` renders the Harmony floating phone title header shown in the Pixso matrix. It combines a light `StatusBar`, a translucent titlebar surface/mask, and one of four title structures.

## Component Variant Tree JSON

- File: `src/components/Navigation/FloatingTitleBar/floating-title-bar.json`
- `get_variants` returned `{}`, so the JSON was reconstructed from `get_node_dsl` visible instances plus the Pixso screenshot matrix.
- `variantOptions` preserves Pixso-facing prop names: `标题类型`, `通透度`, `Icon`.

## Quantitative Spec

| Role | Value |
| --- | --- |
| Root width | 360px |
| Root height / `title with icons-phone` | 173px |
| Root height / `normal-phone` | 92px |
| Root height / `secondary page-phone`, `drawer-phone` | 92px |
| Gradient surface height / `title with icons-phone` | 205px |
| Gradient surface height / other variants | 124px |
| StatusBar | 360x36px, top 0 |
| Title row | 360x56px, top 36px, padding left/right 16px |
| Icon button | 40x40px, radius 999px, icon 24x24px |
| Icon group gap | 8px |
| Large title block | left 16px, top 36+78px, width 232px, gap 2px |
| Secondary/drawer leading icon | 40x40px at left 16px; title starts after 8px gap |

## Typography

| Variant | Text | Font | Weight | Size | Line height | Letter spacing | Color |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `title with icons-phone` | title | HarmonyHeiTi | 700 | 30px | 40px | 0 | `--harmony-font-primary` |
| `normal-phone`, `drawer-phone` | title | HarmonyHeiTi | 700 | 26px | 35px | 0 | `--harmony-font-primary` |
| `secondary page-phone` | title | HarmonyHeiTi | 700 | 20px | 27px | 0 | `--harmony-font-primary` |
| subtitle | subtitle | HarmonyHeiTi | 400 | 14px | 19px | 0 | `--harmony-font-secondary` |

## Props

```ts
type FloatingTitleBarType =
  | "title with icons-phone"
  | "normal-phone"
  | "secondary page-phone"
  | "drawer-phone"

type FloatingTitleBarProps = {
  标题类型?: FloatingTitleBarType
  通透度?: "标准" | "平滑" | "降档" | "弱"
  Icon?: 1 | 3
  title?: string
  subtitleText?: string
  subtitle?: boolean
  leadingAction?: FloatingTitleBarLeadingAction | null
  actions?: FloatingTitleBarAction[]
}
```

## DSL ↔ Prop Alignment

| DSL / screenshot source | React prop | Values | Notes |
| --- | --- | --- | --- |
| Matrix row / nested TitleBar names | `标题类型` | `title with icons-phone`, `normal-phone`, `secondary page-phone`, `drawer-phone` | Pixso frame names are English; prop keeps Chinese axis name for the reconstructed component |
| Matrix column / material appearance | `通透度` | `标准`, `平滑`, `降档`, `弱` | Reconstructed from 4 screenshot columns and existing floating material naming in repo |
| `.Items` icon count | `Icon` | `1`, `3` | Target matrix uses 3 actions for first two rows, 1 action for secondary/drawer rows |
| Text nodes `Title` / `Subtitle` | `title`, `subtitleText`, `subtitle` | text / boolean | Content overrides; default strings match Pixso |
| Leading icon instances | `leadingAction` | `back`, `drawer`, `null` | Business abstraction for clickable left icon; defaults follow `标题类型` |
| `.Items` right icons | `actions` | array | Business abstraction for clickable right actions; default preview uses `CircleDashed` |

## Styles And Tokens

No new `src/styles/global.css` tokens were added. The component uses existing Harmony tokens:

| Role | Token |
| --- | --- |
| Title text | `--harmony-font-primary` |
| Subtitle text | `--harmony-font-secondary` |
| Icon color | `--harmony-icon-primary` |
| Standard surface material | `.hm-material-style-layer-floating-ultra-thin-*` (`Light/Blur/FLOATING_ULTRA_THIN`) |
| Titlebar gradient backing fill | `--comp_background_gradient_smooth_fill` |
| Floating weak button fill | `--Floating_background_weak_fill` + `--Floating_background_weak_fill_blend_mode` |
| Smooth / ultra-thin button fill | `--FLOATING_ULTRA_THIN_fill` + `--FLOATING_ULTRA_THIN_fill_blend_mode` |
| Downgrade button fill | `--comp_background_color_floating_smooth_fill` |
| Hover/click/focus | `--harmony-interactive-hover`, `--harmony-interactive-click`, `--harmony-interactive-focus` |

Note: the titlebar gradient backing keeps the original multi-stop mask geometry, but derives each stop from `--comp_background_gradient_smooth_fill` so system light/dark token switching can update the fill source. The backing is intentionally taller than the layout root: normal / secondary / drawer reserve 92px in page flow while the gradient surface remains 124px; big reserves 173px while the gradient surface remains 205px. The backing does not add a separate circular highlight layer; material layer classes such as `.hm-material-style-layer-floating-thin-*` are not modified by this component.

## States And Interaction

- Buttons expose native `button` semantics, `aria-label`, disabled opacity, hover, active, and focus-visible ring.
- `leadingAction={null}` suppresses the default back/drawer button for the two variants that normally show it.
- `actions` are capped to the selected `Icon` count so the geometry remains aligned with Pixso.

## Storybook Coverage

- `Playground`: controls for `标题类型`, `通透度`, `Icon`, title and subtitle text.
- `Matrix`: renders all 4 `标题类型` rows across all 4 `通透度` columns.
- `Variant`: semantic single variant preview.
- `PixsoReference`: embeds the exported Pixso PNG reference.

## Tradeoffs

- `design_to_code` failed with 500 and `get_variants` returned `{}`; the variant tree is therefore reconstructed and records synthetic row/column guids where Pixso did not expose a stable child id in the truncated DSL output.
- The dotted square action icon is represented by `lucide-react` `CircleDashed` to match existing `TitleBar` preview behavior; consumers can pass exact icons through `actions`.
