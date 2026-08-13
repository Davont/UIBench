# FloatingTextSelection

## Metadata

- Pixso link: `https://pixso.cn/app/design/Xs4by4YngOt5unb-_N4vxQ?item-id=5427:24`
- Pixso item-id: `5427:24`
- MCP calls: `get_node_dsl(guid=5427:24, clientFrameworks=react)`, `get_screenshot(guid=5427:24, clientFrameworks=react)`
- Screenshot fallback: `get_screenshot` succeeded, so `get_export_image` was not used.
- Component path: `src/components/FloatingTextSelection`
- Storybook title: `Components/FloatingTextSelection`

## DSL Properties And Variants

| DSL field | DSL values | React prop | Default |
| --- | --- | --- | --- |
| `语言` | `中文`, `英文` | `语言` | `中文` |
| `通透度` | `标准` | `通透度` | `标准` |

Name mapping: Pixso `Textselection/textselection` maps to React `FloatingTextSelection` and requested component name `floatingtextselection`.

## Quantitative Spec

| Item | Value |
| --- | --- |
| Selected node bounds | `398px × 186px` flattened PNG/vector preview |
| Chinese visual pill | `302px × 40px` |
| English visual pill | `260px × 40px` |
| Standard PNG bounds | Chinese `398px × 136px`, English `356px × 136px` including blur/shadow bounds |
| Radius | `20px` |
| Container padding | `4px 4px 4px 18px` |
| Main gap | `12px` between text group and more button |
| Text group gap | `24px` |
| Text group width | Chinese `236px`, English `194px` |
| More button | visual slot `32px × 32px`; internal glyph about `19.2px × 19.2px` |
| Text | HarmonyHeiTi Medium, `14px`, `19px` text box height |
| Chinese labels | `剪切`, `复制`, `全选`, `翻译`, `分享` |
| English labels | `CUT`, `COPY`, `SELECT ALL`; DSL also contains hidden `TRANSLATE` |

## Token Mapping

| DSL style | Value | Token / implementation |
| --- | --- | --- |
| `Light/font_primary` | `rgba(0,0,0,0.898039)` | `--harmony-font-primary` |
| `Light/icon_primary` | `rgba(0,0,0,0.898039)` | `--harmony-icon-primary` |
| `Light/comp_background_tertiary` | `rgba(0,0,0,0.047059)` | `--harmony-comp-background-tertiary` |
| `Light/Blur/FLOATING_THICK` | floating thick fill/effects | `--FLOATING_THICK_fill` plus `hm-material-style-layer-floating-thick-*` classes |
| `Dark/font_primary` | `rgba(255,255,255,0.898039)` | `[data-theme="dark"]` local text token |
| `Dark/icon_primary` | `rgba(255,255,255,0.898039)` | `[data-theme="dark"]` local icon token |
| `Dark/comp_background_tertiary` | `rgba(255,255,255,0.047059)` | `[data-theme="dark"]` more button background |
| `Dark/Blur/FLOATING_THICK` | dark floating thick fill/effects | `[data-theme="dark"]` local material-layer overrides |

No new `src/styles/global.css` token is required.
