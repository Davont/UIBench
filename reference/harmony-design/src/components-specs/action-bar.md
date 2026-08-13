# Spec: action-bar

## Metadata
- Implementation: `src/components/ActionBar/action-bar.tsx`
- Stories: `src/components/ActionBar/action-bar.stories.tsx`
- Variant tree JSON: `src/components/ActionBar/action-bar.json`
- Pixso: `https://pixso.cn/app/design/QeDttX-H4qVEUZXJjNfTCw?item-id=5371:21687`
- MCP evidence:
  - Success: `get_node_dsl(itemId=5371:21687, clientFrameworks=react)`
  - Empty: `get_variants(itemId=5371:21687)` returned `{}`
  - Skipped by user request: `get_screenshot(itemId=5371:21687)` because Pixso MCP screenshot calls were hanging
  - Fallback: variant tree reconstructed from DSL instance names and `mainComponent` references

## Composition
- Pixso node is a 490×800 container with four `Actionbar-Phone` instances.
- Variant axes:
  - `Port`: `ON | OFF` — vertical vs horizontal layout
  - `个数`: `3 | 5` — action slot count
- Sub-components: PlayButton (56×56, primary), Stopwatch button (48×48), Voice button (48×48).
- Compatibility: previous implementation exposed `浮动` and `通透度` on `ActionBar`. Those props remain accepted; when `浮动=true`, `ActionBar` delegates to `FloatingActionBar`.

## Quantified Spec

### Layout
| Variant | Frame | Direction | Gap | Outer Padding | Surface Padding |
|---------|-------|-----------|-----|---------------|-----------------|
| Port=OFF, 个数=3 | 328×108px | Row | 24px | 24px 58px | 2px 6px |
| Port=OFF, 个数=5 | 328×108px | Row | 16px | 24px 2px | 2px 6px |
| Port=ON, 个数=3 | 108×360px | Column | 24px | 74px 24px | 6px 2px |
| Port=ON, 个数=5 | 108×360px | Column | 16px | 18px 24px | 6px 2px |

### Container
- Border radius: 36px.
- Background blur: `BACKGROUND_BLUR` radius `81.54840087890625`.
- Fill style: `Light/Blur/COMPONENT_REGULAR`, luminosity white `0.1019607857` plus normal white `0.6000000238`.
- Shadow: `rgba(0,0,0,0.1019607843)` offset `(0, 4)`, radius `16`.

### Action Items
| Type | Size | Background | Icon Color | Radius |
|------|------|------------|------------|--------|
| Primary PlayButton | 56×56px | `#0A59F7` / `--harmony-brand` | `#FFFFFF` / `--harmony-icon-on-primary` | 100px |
| Standard Time / SoundRecording | 48×48px | `rgba(0,0,0,0.0470588244)` / `--harmony-comp-background-tertiary` | `rgba(0,0,0,0.6)` / `--harmony-icon-secondary` | 100px |

### HM Symbol Icons
| Slot | Glyph Name | Unicode | Pixso Component |
|------|------------|---------|-----------------|
| Play | `play_fill` | U+F00B4 | `.play` / `66:22810` |
| Stopwatch | `stopwatch` | U+F05F0 | `.stopwatch` / `66:22811` |
| Voice | `mic_fill` | U+F0315 | `.voice` / `66:22812` |

## Props
```ts
interface ActionBarProps {
  Port?: "ON" | "OFF"
  个数?: "3" | "5"
  actions?: ActionBarAction[]
  activeActionId?: string
  defaultActiveActionId?: string
  onActionClick?: (action: ActionBarAction) => void
  className?: string
  浮动?: boolean
  通透度?: "标准" | "强" | "弱"
}
```

## DSL ↔ Prop
| DSL field | React prop | Legal values | Source |
|-----------|------------|--------------|--------|
| instance name `Port=...` | `Port` | `ON`, `OFF` | `get_node_dsl(5371:21687)` |
| instance name `个数=...` | `个数` | `3`, `5` | `get_node_dsl(5371:21687)` |
| legacy mixed API | `浮动` | `boolean` | Backward compatibility; delegates to `FloatingActionBar` |
| legacy mixed API | `通透度` | `标准`, `强`, `弱` | Backward compatibility; delegates to `FloatingActionBar` |
| N/A business extension | `actions`, `onActionClick` | callback/data | Required for real click interaction |

## Style References
- `src/styles/global.css`: `--harmony-brand`, `--harmony-icon-on-primary`, `--harmony-comp-background-tertiary`, `--harmony-icon-secondary`, `--harmony-interactive-focus`, `--FABShadow`.
- `src/components/HMSymbolIcon/`: HM Symbol PUA glyph rendering.
- `src/components/ActionBar/action-bar.css`: frame sizing, surface material, item states.

## Tradeoffs
- Screenshot evidence was skipped after user instruction because `get_screenshot` hung. 1:1 work here is based on DSL geometry, fills, effects, local styles, and existing HM Symbol glyph mappings.
- `get_variants` returned `{}`; `action-bar.json` is reconstructed from DSL instance names.
- `浮动` / `通透度` are not part of this ActionBar node but remain for previous-code mapping compatibility.
