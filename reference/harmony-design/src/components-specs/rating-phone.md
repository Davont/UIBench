# RatingPhone

## Metadata

- **Implementation:** `src/blocks/rating-phone/rating-phone.tsx`
- **Stories:** `src/blocks/rating-phone/RatingPhone.stories.tsx`
- **Variant JSON:** `src/blocks/rating-phone/rating-phone.json`
- **Pixso Source:** `https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5322:22058`
- **MCP Evidence:**
  - `get_node_dsl` — Success (itemId=5322:22058)
  - `get_screenshot` — Success (itemId=5322:22058)

## Composition

A horizontal row of 5 star icons used for rating display and input. Each star is 28×28px with 6px corner radius, arranged directly adjacent (0px gap). The component uses `value` for static display and controlled interaction; Storybook shows this control as `评分`.

## Quantified Spec

| Property | Value |
|----------|-------|
| Star size | 28×28px |
| Star corner radius | 6px |
| Gap between stars | 0px |
| Active star fill | #F7CE00 (gold) |
| Inactive star fill | rgba(0,0,0,0.098) |
| Hover overlay | rgba(0,0,0,0.047) |
| Focus stroke | #0A59F7, 2px |

## States & Interaction

| State | Description |
|-------|-------------|
| Default | Stars 1..N filled gold, stars N+1..5 dimmed |
| Hover (interactive) | Preview fill on hovered star + overlay on individual star |
| Focus (interactive) | Blue focus ring 2px on focused star |
| Disabled | No interaction, cursor default |
| Read-only | No interaction, cursor default |

## Props

```ts
interface RatingPhoneProps {
  value?: 1 | 2 | 3 | 4 | 5          // Controlled rating value
  defaultValue?: 1 | 2 | 3 | 4 | 5   // Uncontrolled default rating
  onChange?: (value: RatingValue) => void  // Change callback
  max?: number                        // Max stars (default 5)
  disabled?: boolean                  // Disable interaction
  readOnly?: boolean                  // Display only
}
```

## DSL to Prop

| DSL Field | Prop | Values | Notes |
|-----------|------|--------|-------|
| `评分` | `value` | 1, 2, 3, 4, 5 | Storybook displays `value` as `评分`; used for static/display and controlled API |
| (interactive) | `onChange` | callback | Business callback |
| `max` prop | `max` | number | Extended beyond DSL, defaults to 5 |

## Style References

| Token | Source | Value |
|-------|--------|-------|
| `--rating-star-active` | Component-local (from Pixso `Light/multi_color_11`) | #F7CE00 |
| `--rating-star-inactive` | `--harmony-comp-background-secondary` | rgba(0,0,0,0.098) |
| `--rating-overlay-hover` | `--harmony-interactive-hover` | rgba(0,0,0,0.047) |
| `--rating-ring-focus` | `--harmony-interactive-focus` | #0A59F7 |

## Tradeoffs

- Star 使用本地 `HMSymbolIcon name="star_fill"`（U+F0009）；与 Pixso `svgSha: "Star"` 轮廓差异小，激活/未激活状态继续由颜色 token 表达。
- `max` prop is an extension beyond DSL (DSL only defines 5-star variant). Used for flexibility but defaults match DSL exactly.
- Interactive hover shows fill-preview across all stars up to hovered index (not present in DSL static variants). Chosen over per-star-only hover for better UX.
