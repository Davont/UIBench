# Spec: floating-action-bar

## Metadata
- Implementation: `src/components/FloatingActionBar/floating-action-bar.tsx`
- Shared implementation: `src/components/ActionBar/action-bar.tsx`
- Stories: `src/components/FloatingActionBar/FloatingActionBar.stories.tsx`
- Variant tree JSON: `src/components/FloatingActionBar/floating-action-bar.json`
- Pixso: `https://pixso.cn/app/design/QeDttX-H4qVEUZXJjNfTCw?item-id=5371:21688`
- MCP evidence:
  - Success: `get_node_dsl(itemId=5371:21688, clientFrameworks=react)`
  - Empty: `get_variants(itemId=5371:21688)` returned `{}`
  - Skipped by user request: `get_screenshot(itemId=5371:21688)` because Pixso MCP screenshot calls were hanging
  - Fallback: variant tree reconstructed from DSL instance names

## Composition
- Pixso node is a 1554×686 container with `FloatingActionbar-Phone` instances.
- Variant axes:
  - `Port`: `ON | OFF`
  - `个数`: `3 | 5`
  - `通透度`: `标准 | 强 | 弱`
- Uses the same action slots as `ActionBar`: Stopwatch, PlayButton, Voice.
- Click interaction is supported through `actions[].onClick`, `onActionClick`, and active state props.

## Quantified Spec

### Layout
| Variant | Frame | Direction | Gap | Outer Padding | Surface Padding |
|---------|-------|-----------|-----|---------------|-----------------|
| Port=OFF, 个数=3 | 328×108px | Row | 24px | 24px 58px | 2px 6px |
| Port=OFF, 个数=5 | 328×108px | Row | 16px | 24px 2px | 2px 6px |
| Port=ON, 个数=3 | 108×360px | Column | 24px | 74px 24px | 6px 2px |
| Port=ON, 个数=5 | 108×360px | Column | 16px | 18px 24px | 6px 2px |

### Floating Material
| 通透度 | DSL style evidence | Implementation |
|--------|--------------------|----------------|
| 标准 | white luminosity `0.1019607857` + white normal `0.6000000238`; `FLOATINGshadow` | `data-transparency="标准"` surface background and `--FLOATINGshadow` |
| 强 | `Light/Blur/Material_background_THIN` fill (`0.4` normal + `0.15` linear dodge) | `--Material_background_THIN_fill` |
| 弱 | `Light/Blur/FLOATING_THIN` fill (`0.1` normal + `0.1` linear dodge), shadow `0 8 48 rgba(0,0,0,0.08)` | `--FLOATING_THIN_fill`, `--harmony-floating-thin-shadow` |

Dark mode keeps the same three transparency levels, but scopes the non-floating dark surface override away from `FloatingActionBar`. Because the shared dark `THIN` tokens are visually too close, `强` uses a brighter `rgba(255,255,255,0.32)` material layer and `弱` uses a softer `rgba(255,255,255,0.18)` material layer.

### Action Items
| Type | Size | Background | Icon Color | Radius |
|------|------|------------|------------|--------|
| Primary PlayButton | 56×56px | Light: `#0A59F7` / `--harmony-brand`; Dark: `#5291FF` | `#FFFFFF` / `--harmony-icon-on-primary` | 100px |
| Standard Time / SoundRecording | 48×48px | `rgba(0,0,0,0.0470588244)` / `--harmony-comp-background-tertiary` | `rgba(0,0,0,0.6)` / `--harmony-icon-secondary` | 100px |

## Props
```ts
interface FloatingActionBarProps {
  Port?: "ON" | "OFF"
  个数?: "3" | "5"
  通透度?: "标准" | "强" | "弱"
  actions?: ActionBarAction[]
  activeActionId?: string
  defaultActiveActionId?: string
  onActionClick?: (action: ActionBarAction) => void
  className?: string
}
```

## DSL ↔ Prop
| DSL field | React prop | Legal values | Source |
|-----------|------------|--------------|--------|
| instance name `Port=...` | `Port` | `ON`, `OFF` | `get_node_dsl(5371:21688)` |
| instance name `个数=...` | `个数` | `3`, `5` | `get_node_dsl(5371:21688)` |
| instance name `通透度=...` | `通透度` | `标准`, `强`, `弱` | `get_node_dsl(5371:21688)` |
| N/A business extension | `actions`, `onActionClick` | callback/data | Required click interaction |

## Style References
- `src/styles/global.css`: `--FLOATING_THIN_fill`, `--FLOATING_THIN_fill_blend_mode`, `--harmony-floating-thin-shadow`, `--harmony-floating-thin-backdrop`, `--Material_background_THIN_fill`, `--FLOATINGshadow`.
- `src/components/ActionBar/action-bar.css`: shared layout and item styling.
- `src/components/HMSymbolIcon/`: HM Symbol PUA glyph rendering.

## Tradeoffs
- Screenshot evidence was skipped after user instruction because `get_screenshot` hung. 1:1 work here is based on DSL geometry, fills, effects, local styles, and existing HM Symbol glyph mappings.
- `get_variants` returned `{}`; `floating-action-bar.json` is reconstructed from DSL instance names.
- Component implementation is shared with `ActionBar` to preserve previous mixed `ActionBar` mapping while exposing `FloatingActionBar` as an independent registered component.
