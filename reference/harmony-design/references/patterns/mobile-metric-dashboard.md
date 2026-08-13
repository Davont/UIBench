# Mobile metric dashboard pattern

Use only when a mobile page combines a primary metric, short period progress, a linear task/habit list, and bottom navigation. Adapt labels, data, icons, and brand accent; do not copy domain text blindly.

## Composition

```text
MobilePhoneShellTemplatePage
└─ viewport (360 × requested height)
   ├─ header / status / title
   ├─ scrollable main
   │  ├─ metric hero (value + label + progress visual + supporting copy)
   │  ├─ full-width primary action
   │  ├─ period section
   │  │  └─ GridContainer → pixso-grid-item × N
   │  └─ item section
   │     └─ ListContainer → pixso-list-item × N
   └─ bottom navigation
      └─ ListContainer → pixso-list-item × 3–5
```

## Data-first scaffold

Define period cells, list items, and tabs as typed arrays above the component. Keep only interaction state in the component:

```tsx
const periodItems = [{ key: "mon", label: "一", value: "21", done: true }]
const items = [{ key: "read", title: "阅读", meta: "07:30", icon: "book_open_fill" }]
const tabs = [{ key: "home", label: "首页", icon: "house_fill" }]

const [primaryDone, setPrimaryDone] = useState(false)
const [activeTab, setActiveTab] = useState("home")
```

## Geometry

- Canvas: use the requested fixed size; content width is canvas width minus 32px.
- Header: 104–124px. Bottom navigation: 64–72px with 10–12px inset.
- Hero: full content width, 150–180px, 22–26px radius.
- Primary action: 46–50px high, full content width, pill radius.
- Period grid: one row, equal columns, 6–8px gaps.
- Linear items: 58–68px high, 8–12px gaps.
- Scroll content bottom padding: bottom navigation height plus 20–28px.

## Token mapping

- Canvas/header: `--harmony-background-secondary`
- Main/card surface: `--harmony-background-primary`, `--harmony-comp-background-gray`
- Primary action/active state: selected semantic brand token from the A3 manifest
- Text: `--harmony-font-primary`, `--harmony-font-tertiary`
- Dividers/borders: `--harmony-comp-divider`

Use `color-mix()` with semantic variables for soft fills and shadows. Do not introduce literal color values.

## Adaptation checks

- Keep exactly one page-level `NavigationContainer`; the phone Shell already provides it.
- Use `GridContainer` for period cells and `ListContainer` for the item list/navigation.
- Put `pixso-grid-item` / `pixso-list-item` on direct child roots.
- Use only icon names returned by A3 or confirmed by the artifact validator.
- Preserve the requested primary metric and P0 text without truncation.
