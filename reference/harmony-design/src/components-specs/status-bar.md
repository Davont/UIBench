# Spec: status-bar

## Metadata
- Implementation: `src/components/StatusBar/StatusBar.tsx`
- Stories: `src/components/StatusBar/StatusBar.stories.tsx`
- Variant tree JSON: `src/components/StatusBar/status-bar.json`
- Pixso (component definition): `https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5311:19205`
- Pixso (phone usage context / Size-Phone): `https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5311:19582`
- MCP evidence:
  - Success: `get_node_dsl(itemId=5311:19205)`, `get_screenshot(itemId=5311:19205)`
  - Success (icon SVGs): `get_export_image` × 8 — Cell types 1/2/3 (`67:23010`/`67:23008`/`67:23009`), Wifi (`67:25177`), SingleCard ON/OFF (`67:26645`/`67:26644`), DualCard ON/OFF (`67:28034`/`67:28033`)
  - Success (context): `get_node_dsl(itemId=5311:19582)`, `get_export_image(itemId=5311:19582)`, `design_to_code(itemId=5311:19582, react)`
  - Fallback: `design_to_code(itemId=5311:19205)` URLs expired (batch timestamp), `get_variants(itemId=5311:19205)` returned `{}`
  - **2026-07-15**: Wi-Fi 公共语义图标改用本地 `HMSymbolIcon name="wifi"`（U+F0000）；SIM/信号组合与电池变体继续保留 Pixso 专用矢量。
  - **2026-05-28**: StatusBar 专用组合图标替换为 Pixso 精确导出。此前的简化 SVG（信号矩形、`<text>5G</text>`）已由 `get_export_image(imageType=3)` 的布尔路径替代。

## Composition
- Root node `StatusBar` (`5311:19205`), a 403×138 px frame containing two StatusBar variant instances (Light at top:23, Dark at top:79).
- Main component variant axis:
  - `Color Mode`: `Light | Dark`
- Icon sub-components:
  - `CellSignalIcon` (`类型`: `1 | 2 | 3`) — exact SVG boolean operation paths from Pixso; each type has distinct inner bar pattern
  - `WifiIcon` (`Flux`: `boolean`, default `false`) — exact SVG concentric arc paths from Pixso
  - `SingleCardIcon` (`G`: `ON | OFF`) — SIM card outline (left) + five signal bars (right); the "5G" label in Pixso is rendered as vertical bars, not text
  - `DualCardIcon` (`G`: `ON | OFF`) — five signal bars only (no SIM card outline); no text element
- Default icon states: Cell `1`, SingleCard `OFF`, DualCard `OFF`, Wifi default.
- All icons use `fill="currentColor"` with per-element `fillOpacity` matching Pixso source; color adapts to Light/Dark mode via parent CSS `color` property.

## Quantified Spec
- **Size**: `width: 100%` (responsive; 360px portrait / 792px landscape as measured in Size-Phone context `5311:19582`), height 36px
- **Layout**: Horizontal flex, `space-between`, `center` cross-axis
- **Padding**: 8px (top/bottom), 24px (left/right)
- **Typography**:
  - Time text: `HarmonyHeiTi Medium 15px`, `lineHeight: 20px` (PIXELS), `letterSpacing: 0`
- **Icon dimensions** (within 96×13 px group, absolute positioning):
  - Wifi: 15.34 × 12 px (left: 0.4px)
  - Single Card: 21.50 × 12 px (left: 21.4px)
  - Dual Card: 17.50 × 12 px (left: 47.4px)
  - Cell Signal: 25.75 × 13 px (left: 70.25px)
- **Colors (Light mode)**:
  - Text: `var(--harmony-font-primary)` = rgba(0,0,0,0.898)
  - Icons: `var(--harmony-icon-primary)` = rgba(0,0,0,0.898)
  - Cell background fill (Type 1): rgba(0,0,0,0.1)
  - Cell background fill (Type 2): rgba(0,0,0,0.098)
- **Colors (Dark mode)**:
  - Text: `var(--harmony-font-on-primary)` = rgba(255,255,255,1)
  - Icons: `var(--harmony-icon-on-primary)` = rgba(255,255,255,1)

## Props
```ts
interface StatusBarProps extends HTMLAttributes<HTMLDivElement> {
  "Color Mode"?: "Light" | "Dark"
}
```

## DSL ↔ Prop

| DSL field | React prop | Legal values |
| --- | --- | --- |
| `Color Mode` | `Color Mode` | `Light`, `Dark` |

## Style References
- `src/styles/global.css`
  - `--harmony-font-primary` (Light mode text/icons)
  - `--harmony-icon-primary` (Light mode icons)
  - `--harmony-font-on-primary` (Dark mode text/icons)
  - `--harmony-icon-on-primary` (Dark mode icons)

No new global tokens added — all colors mapped to existing Harmony tokens.

## Tradeoffs
- `get_variants(itemId=5311:19205)` returned empty — the variant tree in `status-bar.json` reconstructed from `get_node_dsl` + component instance inspection.
- `design_to_code(itemId=5311:19205)` batch timestamp expired; implementation used DSL + exported icon SVGs + screenshot for 1:1 verification.
- **图标资源**：Wi-Fi 使用本地 HMSymbol `wifi`（U+F0000）；SingleCard、DualCard 与 CellSignal 含多卡编号、格数或电池状态等组合语义，继续使用 `get_export_image(imageType=3)` 的 Pixso 精确路径。各专用路径的透明度按源稿保留。
- SingleCard ON/OFF and DualCard ON/OFF SVG paths are byte-identical; the visual distinction is in component identity, not vector geometry.
- Cell type 1 includes a 10% opacity background fill; type 2 uses a 9.8% opacity background rect + separate signal bar path; type 3 omits the background fill (full signal bars only).
- The root frame (403×138) is a container for two StatusBar instance previews; the actual component dimensions are 360×36 (or responsive 100% width).

## Size-Phone Context (item-id=5311:19582)
The Size-Phone frame shows StatusBar usage in two phone orientations:
- **Portrait phone** (`5311:19274`): 360×792, StatusBar at top (0,0), 360×36
- **Landscape phone** (`5311:19212`): 792×360, StatusBar at top (0,0), 792×36

Both orientations share identical StatusBar layout parameters — the horizontal flex with `space-between` and fixed padding (24px left/right) ensures the time label stays left-aligned and the icon group stays right-aligned regardless of container width.
