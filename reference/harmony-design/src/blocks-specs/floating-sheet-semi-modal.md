# FloatingBindSheet Semi-Modal Block

## Purpose

`floating-sheet-semi-modal` is the block recipe for 半模态面板.

Use it when the panel must attach to the phone viewport edges. A semi-modal
panel is not a floating popup: it has no left, right, or bottom gap, at any
height.

## Component

Use the resource block at `src/blocks/floating-sheet-semi-modal/`.

It wraps `src/components/Container/FloatingBindSheet` and includes optional example content
variants. Pass `children` to replace the example content entirely.

Required props for the shell:

```tsx
<FloatingBindSheet
  className="page__semi-modal"
  fixedToBottom
  draggable
  defaultHeight={434}
  minHeight={149}
  maxHeight={748}
  snapHeights={DEFAULT_SHEET_SNAP_HEIGHTS}
  Title=""
  content
  {...{ "Right icon": false }}
>
  <div className="page__semi-modal-body" data-floating-panel-scroll>
    {content}
  </div>
</FloatingBindSheet>
```

## Geometry

For a `360x792` phone viewport:

| Item        |           Value |
| ----------- | --------------: |
| width       |         `360px` |
| left gap    |           `0px` |
| right gap   |           `0px` |
| bottom gap  |           `0px` |
| radius      | `32px 32px 0 0` |
| low height  |         `149px` |
| mid height  |         `434px` |
| high height |         `748px` |

Use `DEFAULT_SHEET_SNAP_HEIGHTS = [149, 434, 748]` for release snapping. Drag
remains fluid while the pointer is down; release snaps to the nearest tier.

## Expanded State

When the sheet reaches the highest snap tier (`748px` in the standard phone
viewport), the semi-modal switches from floating material to a solid surface:

- the sheet background uses `expandedBgColor` (`--harmony-background-secondary`
  / `#f1f3f5` by default);
- `FLOATING_ULTRA_THICK` pseudo layers, blur, and shadow are disabled;
- a full-page `rgba(0,0,0,0.2)` backdrop is shown behind the sheet.

Lower and middle snap tiers keep the normal `FloatingBindSheet` material.

CSS:

```css
.page__semi-modal-shell {
  position: absolute;
  inset: 0;
}

.page__semi-modal-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.2);
}

.page__semi-modal.pixso-floating-sheet {
  position: absolute;
  left: 50%;
  bottom: 0;
  width: 360px;
  transform: translateX(-50%);
  border-radius: 32px 32px 0 0;
}

.page__semi-modal--headerless.pixso-floating-sheet {
  grid-template-rows: 40px minmax(0, 1fr);
}

.page__semi-modal--headerless .pixso-floating-sheet__header {
  height: 0;
  min-height: 0;
  overflow: hidden;
}

.page__semi-modal .pixso-floating-sheet__content {
  min-height: 0;
  overflow: hidden;
}

.page__semi-modal-body {
  box-sizing: border-box;
  height: 100%;
  min-height: 0;
  padding: 0 0 24px;
  overflow-y: auto;
  scrollbar-width: none;
}

.page__semi-modal-body::-webkit-scrollbar {
  display: none;
}
```

## Content Slot

The body is a flexible slot. It may contain cards, lists, forms, tabs, media,
search results, or custom content. The content must scroll inside the body and
must not create side gaps around the sheet.

Content rules:

- Let `FloatingBindSheet` own the `16px` horizontal padding. Do not add another
  `16px` on the body wrapper, or the content will shrink and look like an inset
  popup.
- Keep direct child width within the body content width, usually `328px`.
- Use flex/grid inside the body, not absolute positioning for every item.
- Clamp long card titles and descriptions.
- For horizontal strips, put `overflow-x: auto` on the strip, not on the whole
  sheet.
- Use `data-floating-panel-scroll` on the main body to document the intended
  scroll area.

## Optional Content Fill Examples

The TSX block includes these examples as `variant` values. They are optional
resource examples, not required structure. Use them only when the prompt asks
for richer content, "more filled", multiple cards, browsing content, or
page-like information density.

### Example A: Browse Sheet

Good for Explore Sheet, recommendation browsing, map discovery, search landing.
Use `variant="browse"`.

```tsx
<div className="page__semi-modal-body" data-floating-panel-scroll>
  <div className="page__sheet-chips">{chips}</div>
  <section className="page__hero-card">{largeImageCard}</section>
  <section className="page__section">
    <h3>{sectionTitle}</h3>
    <div className="page__horizontal-cards">{smallCards}</div>
  </section>
  <section className="page__section">
    <h3>{secondaryTitle}</h3>
    <div className="page__vertical-list">{listRows}</div>
  </section>
</div>
```

Content notes:

- Use one prominent card first, then one or two supporting sections.
- Horizontal cards should be fixed width and scroll inside their own strip.
- Section titles are short and functional.
- Use this when the sheet feels like a first-level page continuation.

### Example B: Results Sheet

Good for search results, item collections, route choices, nearby services.
Use `variant="results"`.

```tsx
<div className="page__semi-modal-body" data-floating-panel-scroll>
  <div className="page__sheet-toolbar">{searchOrFilters}</div>
  <div className="page__result-summary">{countAndSort}</div>
  <div className="page__result-list">{resultCards}</div>
</div>
```

Content notes:

- Keep result rows/card widths within the `328px` body.
- Put filters or chips in a horizontal strip.
- Clamp row titles and metadata so the list stays stable.

### Example C: Detail Continuation

Good for a detail page that rises from a map/media base.
Use `variant="detail"`.

```tsx
<div className="page__semi-modal-body" data-floating-panel-scroll>
  <header className="page__detail-header">{titleAndMeta}</header>
  <section className="page__primary-card">{summaryOrAiCard}</section>
  <section className="page__detail-section">{keyValueList}</section>
  <section className="page__detail-section">{relatedCards}</section>
</div>
```

Content notes:

- Use the top of the sheet for identity and summary.
- Put heavier details below the fold.
- Avoid bottom-fixed action bars unless the prompt asks for one; if used, keep
  the scroll body padded so content is not hidden.

### Example D: List Sheet

Good for settings, action lists, service management, permissions, privacy
entries, and any semi-modal whose main content is grouped rows. Use
`variant="list"`.

```tsx
import { List } from "@/blocks/list"

<FloatingSheetSemiModal variant="list" title="设置" showClose defaultHeight={748} />

<FloatingSheetSemiModal title="设置" showClose defaultHeight={748}>
  <div className="page__semi-modal-list">
    <List
      variant="grouped"
      subtitle="数据和隐私"
      footnote="了解我们如何使用您的数据"
      items={[
        { title: "个性化推荐", type: "navigate", lines: "1" },
        { title: "权限管理", type: "navigate", lines: "1" },
      ]}
    />
  </div>
</FloatingSheetSemiModal>
```

Content notes:

- Use `List variant="grouped"` for grouped cards and section subtitles.
- Keep list width at the sheet content width (`328px` in a 360px viewport).
- When the first grouped list appears directly below the sheet title, reduce only
  its first subtitle header top padding so the title-to-list spacing stays
  compact; keep later grouped list spacing at the default list rhythm.
- Prefer `items` for simple rows; use `children` with `ListPhone` only when a
  row needs richer custom title/content.
- Keep the scroll area on the sheet body, not inside each grouped list.

## When To Use

Use this block for:

- 半模态 / 半屏面板
- bottom sheet / sheet
- Explore Sheet
- 一级页面承接页
- page-like content that rises from the bottom
- full-width map/detail/search continuation panels

## Do Not

- Do not set width to `344px`.
- Do not center it with visible left/right margins.
- Do not add a bottom offset such as `bottom: 28px`.
- Do not round the bottom corners.
- Do not let child content resize the shell height.

## Validation

- Computed left/right/bottom gaps are `0px`.
- Width is `360px` in the standard phone viewport.
- Only top corners are rounded.
- Low, mid, and high heights stay inside the viewport.
- Body content scrolls internally without changing shell geometry.
