# FloatingBindSheet

## Metadata

- Component id: `floating-bind-sheet`
- Source path: `src/components/Container/FloatingBindSheet/FloatingBindSheet.tsx`
- Story path: `src/components/Container/FloatingBindSheet/FloatingBindSheet.stories.tsx`
- Variant tree JSON: `src/components/Container/FloatingBindSheet/floating-bind-sheet.json`
- Pixso link: `https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5344:21851`
- Pixso item id: `5344:21851`
- MCP evidence: `get_node_dsl`, `get_screenshot`, `get_variants`

## MCP Result And Fallback

- `get_node_dsl(itemId=5344:21851)`: success.
- `get_screenshot(itemId=5344:21851)`: success.
- `get_variants(itemId=5344:21851)`: returned `{}`.
- Fallback scope: only the variant tree extraction falls back. Geometry, material, typography, and fixed composition come from DSL plus screenshot. `通透度` and `状态` remain the repository's established FloatingBindSheet variant axes for this single visual node.

## Quantitative Spec

| Item | Value |
| --- | --- |
| Root frame | `420px × 312px`, white fill |
| Sheet frame | `360px × 240px`, `left=31px`, `top=34px` |
| Sheet radius | top-left `32px`, top-right `32px`, bottom corners `0` |
| Sheet padding | top `8px`, left `16px`, right `16px`, bottom `0` |
| Sheet layout | Handle is absolute overlay; implemented grid rows are `56px / 176px` so TitleBar starts at `top=8px` and content starts at `top=64px` |
| Handle instance | `64px × 16px`, `left=132px`, `top=0`; pill `48px × 4px`, radius `2px`, visible top `8px` |
| TitleBar | `328px × 56px`, `left=16px`, `top=8px`, horizontal gap `32px` |
| Title text | `256px × 27px`, text `Title` |
| Close button | `40px × 40px`, radius `20px`; icon `18px × 18px` |
| Content slot | DSL child at `left=16px`, `top=64px`; slot size `328px × 176px`, default render has no fill |

## Typography And Colors

| Role | Value | Token |
| --- | --- | --- |
| Title font | `HarmonyHeiTi Bold`, `20px`, `27px`, letter spacing `0` | `--harmony-font-size-title-s` and explicit line-height |
| Title color | `rgba(0,0,0,0.898039)` | `--harmony-font-primary` |
| Close icon color | `rgba(0,0,0,0.898039)` | `--harmony-icon-primary` |
| Handle color | `rgba(0,0,0,0.2)` | `--harmony-icon-fourth` |
| Content area | transparent by default | blue Pixso placeholder removed to avoid implying component-owned content fill |
| Sheet fill | `rgba(241,243,245,0.9)` plus restored surface layers | `--harmony-floating-ultra-thick-surface` over `--FLOATING_ULTRA_THICK_fill` |

## Material Effects

- Sheet effect style: `Light/Blur/FLOATING_ULTRA_THICK`.
- Backdrop: DSL radius `40`, saturation `20`; mapped to `--harmony-floating-ultra-thick-backdrop`.
- Shadow: inner layers `0 10 80 rgba(197,197,197,0.08)` with `LINEAR_BURN`, `0 -4 40 rgba(0,0,0,0.03)`, side/top/bottom hairlines, and drop shadow `0 8 48 rgba(0,0,0,0.08)`.
- CSS fallback: the `LINEAR_BURN` gray inset is reduced to `.03` opacity because normal CSS `box-shadow` cannot reproduce Pixso blend-mode compositing and otherwise creates a dirty neutral-gray wash.
- Surface fallback: the visible fill is split into a translucent surface layer plus a narrow 24px highlight rim, so the sheet keeps the Pixso glass material without turning the top area into an opaque white block.
- Close button material: `Light/Blur/FLOATING_ULTRA_THIN` fill/effect reused through `--FLOATING_ULTRA_THIN_fill` plus local circular shadow/backdrop rules.

## DSL Components And Fields

| DSL source | Field | Values observed | React prop |
| --- | --- | --- | --- |
| Repository FloatingBindSheet variant axis for this node | `通透度` | `"标准"` | `通透度` |
| Repository FloatingBindSheet variant axis for this node | `状态` | `"默认"` | `状态` |
| Title symbol prop name / text node | `Title` | `"Title"` | `Title` |
| TitleBar component property | `Right icon` | `true`, `false`; target node uses `true` | `Right icon` |
| Content symbol prop name | `content` | `true` | `content` |
| TitleBar component tree | `Subtitle` | `true` in component definition | not exposed for this `TextLine2OFF` instance |
| TitleBar component tree | `Left icon` | `true` in related component definitions | not exposed for this `TextLine2OFF` instance |

## React API

```ts
type FloatingBindSheetProps = {
  通透度?: "标准"
  状态?: "默认"
  Title?: string
  "Right icon"?: boolean
  content?: true
  title?: string
  closeButtonLabel?: string
  onClose?: React.MouseEventHandler<HTMLButtonElement>
  closeButtonProps?: Omit<
    React.ButtonHTMLAttributes<HTMLButtonElement>,
    "aria-label" | "children" | "onClick" | "type"
  >
  children?: React.ReactNode
  draggable?: boolean
  defaultHeight?: number
  minHeight?: number
  maxHeight?: number
  snapHeights?: readonly number[]
  fixedToBottom?: boolean
}
```

`title`, `children`, close callbacks, and drag sizing props are runtime adapters. Stories use the DSL-aligned props `Title`, `Right icon`, `content`, `通透度`, and `状态` as their defaults.

Runtime drag behavior:

- `draggable=true` enables the top handle as a vertical resize control.
- Dragging upward increases panel height; dragging downward decreases it.
- Height is clamped by `minHeight` and `maxHeight`.
- `snapHeights` enables release snapping: drag remains fluid, and pointer release snaps to the nearest configured tier. The shared default for semi-modal sheets is `DEFAULT_SHEET_SNAP_HEIGHTS = [149, 434, 748]`.
- Keyboard fallback on the handle: `ArrowUp/PageUp` increases height, `ArrowDown/PageDown` decreases height, `Home` and `End` jump to min/max.
- When `snapHeights` is provided, keyboard fallback moves between adjacent snap tiers instead of 16px steps.
- The handle is CSS-centered with `left: 50%` and `translateX(-50%)` so it stays visually centered on the 360px panel.

## Semi-Modal Usage

For page generation, `FloatingBindSheet` is the component for 半模态面板: a
bottom-attached sheet with no left, right, or bottom viewport gaps. Use
`src/blocks-specs/floating-sheet-semi-modal.md`.

Do not use `FloatingBindSheet` for inset popup-style floating panels with visible
side and bottom margins. For the petal-map variant of that shape, see the
`harmony-map` branch.

## Global CSS Mapping

- Reused: `--FLOATING_ULTRA_THICK_fill`, `--harmony-floating-ultra-thick-backdrop`, `--harmony-floating-ultra-thick-shadow`, `--harmony-floating-ultra-thick-highlight`, `--harmony-floating-ultra-thick-edge`, `--harmony-font-primary`, `--harmony-icon-primary`, `--harmony-icon-fourth`, `--FLOATING_ULTRA_THIN_fill`.
- Added: `--harmony-floating-ultra-thick-surface`, following the same pattern as FloatingTab where the component-visible surface fill is separate from the utility shadow/highlight layers.
- Updated existing token: `--harmony-floating-ultra-thick-backdrop` from `blur(20px)` to `blur(40px)` to match the DSL effect radius for `5344:21851`.

## Storybook Coverage

- `Playground`: DSL defaults with `bg-[#f3f4f6]` decorator.
- `PixsoMatrix`: single DSL combination `通透度=标准`, `状态=默认`, `Title=Title`, `Right icon=true`, `content=true`.
- `WithCustomContent` and `MaterialReview`: runtime adapter examples that keep the same shell geometry and material.

## Tradeoffs

- `get_variants` returned `{}`, so `floating-bind-sheet.json` was reconstructed from successful DSL data.
- CSS cannot exactly reproduce Pixso blend modes such as `LINEAR_DODGE`; implementation uses the repository's split FLOATING material tokens and pseudo layers as the closest runnable equivalent.
