# Spec: aibottombar

## Metadata
- Implementation: `src/components/Aibottombar/Aibottombar.tsx`
- Stories: `src/components/Aibottombar/Aibottombar.stories.tsx`
- Variant tree JSON: `src/components/Aibottombar/aibottombar.json`
- Pixso: `https://pixso.cn/app/design/jal1gO3LzkzJLEhgbrD-6w?item-id=5319:7`
- MCP evidence:
  - Success: `get_node_dsl(itemId=5319:7)`, `get_screenshot(itemId=5319:7)`, `design_to_code(itemId=5319:7, react)`
  - Fallback note: `get_variants(itemId=5319:7)` returned `{}` — variant tree in `aibottombar.json` reconstructed from `get_node_dsl` instance ids and `design_to_code` sub-component definitions

## Composition
- **Aibottombar**: bottom home indicator bar for phone mockup screens.
- Main component variant axis:
  - `Color Mode`: `Light | Dark | Transparent`
- Contains a single centered pill indicator (`hm-aibottombar__pill`) with backdrop blur.

## Quantified Spec
- **Container size**: `width: 100%` (responsive), height 28px
- **Layout**: `position: relative` container; pill uses absolute positioning centered horizontally
- **Pill indicator** (portrait reference 360×28):
  - Width: 31.111111% of container (112px / 360px)
  - Height: 5px
  - Corner radius: 4px
  - Position: horizontally centered, `bottom: 6px` (equivalent to DSL `left: 124px; top: 17px` on 360×28)
- **Pill colors by Color Mode** (from `design_to_code` CSS, aligned with DSL `fillPaints`):
  | Color Mode | Background | CSS backdrop-filter blur |
  |---|---|---|
  | Light | rgba(0,0,0,0.2) | blur(45.303px) |
  | Dark | rgba(255,255,255,0.5) | blur(18.122px) |
  | Transparent | rgba(255,255,255,0.7) | blur(27.183px) |
- **DSL BACKGROUND_BLUR radius** (raw Pixso effect values, ~3× CSS blur): Light 135.91px, Dark 54.37px, Transparent 81.55px — CSS implementation uses `design_to_code` converted values.
- **Landscape phone context** (792×32): pill ratio remains 31.111% width; vertical inset equivalent to 6px from bottom.

## States
- Default variant: Light mode, pill visible with dark semi-transparent fill
- No interactive states (purely decorative)

## Props
```ts
interface AibottombarProps extends HTMLAttributes<HTMLDivElement> {
  "Color Mode"?: "Light" | "Dark" | "Transparent"
}
```

## DSL ↔ Prop

| DSL field | React prop | Legal values |
| --- | --- | --- |
| `Color Mode` | `Color Mode` | `Light`, `Dark`, `Transparent` |

组件 Props 直接使用 Pixso 原始属性名 `Color Mode`，不做翻译。

## Style References
- `src/styles/global.css` — no new tokens added; pill colors are component-local (backdrop-blur semi-transparent overlays with no direct Harmony token equivalent).

## Tradeoffs
- `get_variants(itemId=5319:7)` returned `{}` — variant tree reconstructed from `get_node_dsl` child instances and `design_to_code` Aibottombar.tsx.
- Pill width uses 31.111111% to preserve 112/360 ratio across portrait and landscape phone frames.
- CSS `backdrop-filter` blur values follow `design_to_code` export; DSL raw BACKGROUND_BLUR radii are ~3× larger — documented above, visual verified against `get_screenshot`.
