# FloatingMenu

## Metadata

- Implementation: `src/components/FloatingMenu`
- Stories: `src/components/FloatingMenu/FloatingMenu.stories.tsx`
- Variant JSON: `src/components/FloatingMenu/floating-menu.json`
- Pixso link: `https://pixso.cn/app/design/QeDttX-H4qVEUZXJjNfTCw?item-id=5373:1165`
- item-id: `5373:1165`
- Right icon state Pixso link: `https://pixso.cn/app/design/d0WMuB0Im216ZfRVW4uwyQ?item-id=19:35909`
- Right icon state item-id: `19:35909`
- Open content Pixso link: `https://pixso.cn/app/design/d0WMuB0Im216ZfRVW4uwyQ?item-id=5405:1852`
- Open content item-id: `5405:1852`
- MCP calls: `get_node_dsl`, `get_variants`

## MCP Result And Fallback

- `get_node_dsl`: success. Root GROUP `组合 1` (5373:1165) 1554×1519, contains 24 INSTANCE children (组数 1-6 × 通透度 弱/标准/降档/高).
- `get_screenshot`: skipped (user request).
- `get_variants`: skipped (user request). Variants extracted from child node names.
- `get_variants` for right icon state item `19:35909`: success. Returned `状态=selected`, `状态=collapse`, `状态=commence`.
- `get_screenshot` / `design_to_code` for item `19:35909`: timed out; visual state mapping uses user screenshot + successful `get_variants`.
- `design_to_code` / `get_screenshot` for open content item `5405:1852`: timed out.
- `get_variants` for open content item `5405:1852`: returned `[]`.
- Open content fallback: implemented from user screenshot. A main menu row opens downward into indented secondary rows; generated secondary row count supports 1-6.
- Fallback: variantOptions and pixTreeNodes reconstructed from get_node_dsl childNode names and guids.

## Variant Tree

- `variantOptions`:
  - 组数: `["1", "2", "3", "4", "5", "6"]`
  - 通透度: `["弱", "标准", "降档", "高"]`
- Generated via: `get_node_dsl` childNode name parsing.
- Variant JSON: `src/components/FloatingMenu/floating-menu.json`

## Quantified Specs

### Container

- Border radius: `20px` (all corners).
- Fill: `rgba(255, 255, 255, 0.9)` (white 90% opacity).
- Auto-layout: VERTICAL, padding `top=4, bottom=4, left=16, right=16`, counterAlign `center`.
- Content width: `192px` (all variants).

### Size Matrix

| 通透度 | Width | 组数=1 | 组数=2 | 组数=3 | 组数=4 | 组数=5 | 组数=6 |
|---------|-------|--------|--------|--------|--------|--------|--------|
| 弱      | 224   | 104    | 152    | 200    | 248    | 296    | 344    |
| 降档    | 224   | 104    | 152    | 200    | 248    | 296    | 344    |
| 标准    | 224   | 104    | 152    | 200    | 248    | 296    | 344    |
| 高      | 224   | 104    | 152    | 200    | 248    | 296    | 344    |

- All variants height formula: `56 + 组数 × 48`
- Per-item row height: `48px`.

### Effects By 通透度

| 通透度 | Backdrop Blur | Drop Shadow | Fill Style ID |
|---------|---------------|-------------|---------------|
| 弱      | blur(80px) rgba(0,0,0,0.25) | 0 8px 48px rgba(0,0,0,0.08) | 4957:912 (Light/Floating_background_weak) |
| 降档    | none          | none        | 602:9417 (Light/comp_background_primary) |
| 标准    | blur(54px) rgba(0,0,0,0.25) | 0 0 60px rgba(0,0,0,0.2) | 4528:13832 (Light/Blur/FLOATING_THICK) |
| 高      | blur(54px) rgba(0,0,0,0.25) | 0 0 60px rgba(0,0,0,0.2) | 4903:5 (Light/Blur/Material_background_THICK) |

Dark mode is driven by the global Storybook / app theme (`[data-theme="dark"]`), not by a component prop. In dark theme:

- `通透度=标准` uses `Dark/Blur/FLOATING_THICK` fill and shadow / blur stack.
- `通透度=弱` uses a lighter dark floating surface with weaker blur and shadow.
- `通透度=降档` uses a solid dark surface with no blur or shadow.
- `通透度=高` uses a heavier dark surface with stronger blur and shadow.
- `通透度=标准` also overrides the existing floating-thick material layers locally.

### Title Row (.Title / Primary list)

- Size: `192 × 48px`.
- Layout: HORIZONTAL, padding `top=12, bottom=12`.
- Font: `fontSize=18`, `fontFamily=HarmonyHeiTi`, `fontWeight=700` (Subtitle_M/Bold).
- Color: `rgba(0, 0, 0, 0.898)` = `--harmony-font-primary`.
- inheritFillStyleID: `602:9446` (Light/font_primary).

### Item Row (.Secondary list / Primary list)

- Size: `192 × 48px`.
- Layout: HORIZONTAL, `gap=8px`.
- Font: `fontSize=16`, `fontFamily=HarmonyHeiTi`, `fontWeight=400` (Body_L/Regular).
- Text height: `21px`, line-height: `21px`.
- Color: `rgba(0, 0, 0, 0.898)` = `--harmony-font-primary`.

### Open Content

- Trigger: clicking a primary menu row toggles its opened content.
- Only one primary row is open at a time in the built-in interaction.
- Generated submenu count: `1-6`, controlled by `submenuCount` or `菜单项[].submenuCount`.
- Submenu row height: `48px`.
- Submenu text indent: `20px` from content left.
- Submenu label default: `menu item`.
- Open primary row maps right icon state to `commence` when right icon is visible.

### Item States (状态)

| 状态     | Leading Icon | Trailing Icon | Component |
|----------|-------------|---------------|-----------|
| collapse | .highlight (24×24) | .Arrow-right (24×24) | 4939 series |
| commence | .highlight (24×24) | .Arrow-bottom (24×24) | 4939 series |
| selected | .highlight (24×24) | .ok checkmark (24×24) | 4939 series |

### Divider

- Style: `Light/comp_divider` (602:9422 / 1912:10028).
- Color: `rgba(0, 0, 0, 0.2)` = `--harmony-comp-divider`.
- Height: `0.5px` (hairline).

## DSL To Props

| DSL / Pixso field | Prop | Values | Default | Notes |
| --- | --- | --- | --- | --- |
| Node name `组数=N` | `组数` | 1, 2, 3, 4, 5, 6 | 3 | 控制菜单项数量 |
| Node name `通透度=X` | `通透度` | "弱", "标准", "降档", "高" | "弱" | 背景模糊与阴影效果 |
| — | `leftIcon` | boolean | false | 是否显示菜单项前置图标；Storybook 显示为 `Left icon` |
| — | `rightIcon` | boolean | false | 是否显示菜单项右侧状态指示器；Storybook 显示为 `Right icon` |
| Right icon state `状态` | `rightIconState` | "collapse", "commence", "selected" | "collapse" | 右侧图标默认状态；Storybook 显示为 `Right icon state` |
| Open content count | `submenuCount` | 1, 2, 3, 4, 5, 6 | 3 | 展开后默认生成的二级项数量；Storybook 显示为 `Primary Group` |
| Open content index | `openIndex` | `number \| null` | — | 受控展开项索引；`null` 表示全部收起 |
| Open content default index | `defaultOpenIndex` | `number \| null` | `null` | 非受控默认展开项索引 |
| Open content callback | `onOpenIndexChange` | `(index: number \| null) => void` | — | 展开项变化回调 |
| — | `显示图标` | boolean | — | 兼容旧字段，已由 `leftIcon` 替代 |
| — | `显示状态` | boolean | — | 兼容旧字段，已由 `rightIcon` 替代 |
| .Title text | `标题` | string | "标题" | 标题行文本 |
| .Secondary list instances | `菜单项` | FloatingMenuItem[] | [] | 菜单项列表 |
| Item text "subtitle" | `菜单项[].label` | string | — | 项文本标签 |
| Item leading .highlight | `菜单项[].icon` | ReactNode | `.highlight` HMSymbol | 前置图标覆盖项；`leftIcon=true` 且未传入时使用默认 `.highlight` |
| — | `菜单项[].leftIcon` | boolean | 继承 `leftIcon` | 单项前置图标可见性覆盖 |
| — | `菜单项[].rightIcon` | boolean | 继承 `rightIcon` | 单项右侧状态可见性覆盖 |
| Right icon state `状态` | `菜单项[].rightIconState` | "collapse", "commence", "selected" | 继承 `rightIconState` | 单项右侧图标状态覆盖 |
| Open content items | `菜单项[].submenuItems` | `FloatingMenuSubItem[]` | 按 `submenuCount` 生成 | 单项展开内容 |
| Open content count | `菜单项[].submenuCount` | 1, 2, 3, 4, 5, 6 | 继承 `submenuCount` | 单项展开数量 |
| Open content items | `菜单项[].子菜单项` | `FloatingMenuSubItem[]` | — | 兼容中文字段，已由 `菜单项[].submenuItems` 替代 |
| — | `菜单项[].显示图标` | boolean | — | 兼容旧字段，已由 `菜单项[].leftIcon` 替代 |
| — | `菜单项[].显示状态` | boolean | — | 兼容旧字段，已由 `菜单项[].rightIcon` 替代 |
| Item trailing (Arrow/ok) | `菜单项[].状态` | "collapse", "commence", "selected" | — | 兼容旧字段，已由 `菜单项[].rightIconState` 替代 |

## Global CSS Mapping

- Reused tokens: `--harmony-font-primary`, `--harmony-icon-primary`, `--harmony-comp-divider`, `--harmony-interactive-hover`, `--harmony-interactive-pressed`.
- Added tokens: none. All effects mapped directly to CSS properties.

## Storybook

- `Playground`: single instance with Controls (组数, 通透度, 标题, Left icon, Right icon, Right icon state, Group item, Primary Group, Left icon item, Right icon item).
- `Default`: 组数=3, 通透度=弱.
- `Selected`: items with selected state.
- `Right Icon States`: 展示 `collapse / commence / selected` 三种 right icon 状态。
- `Opened`: 展示 `组数=2 / 通透度=标准` 的打开内容。
- `Opacity Variants`: 4 通透度 side-by-side.
- `Matrix`: 组数(1-6) × 通透度(弱/标准/降档/高) gallery.
