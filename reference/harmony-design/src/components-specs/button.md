# Spec: button

## Metadata
- Implementation: `src/components/Button/button.tsx`
- 2in1 implementation: `src/components/Button/button-2in1.tsx`（Pixso `Button-2in1` 节点，仅作同目录内部变体，不单独注册组件）
- Stories: `src/components/Button/button.stories.tsx`
- Variant tree JSON: `src/components/Button/button.json`、`src/components/Button/button-2in1.json`
- Pixso: `https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5319:20057`
- MCP evidence:
  - Success: `get_node_dsl(itemId=5319:20057)`, `get_screenshot(itemId=5319:20057)`, `get_export_image(itemId=5319:20057)`, `design_to_code(itemId=5319:20057)`
  - Fallback note: `get_variants(itemId=5319:20057)` returned empty, so the variant tree was reconstructed from `get_node_dsl` + `design_to_code`
  - Storybook validation note: `http://localhost:6006/?path=/docs/component-button--docs` and `iframe.html?id=component-button--matrix&viewMode=story` were reachable; automated SSIM was skipped because the workspace lacked `pngjs` and Playwright's Chromium binary

## Composition
- Root button matrix node `button` (`3240:265`)
- Variant axes:
  - `尺寸`: `Medium | Small`
  - `类型`: `Emphasized | Normal | Warning | Text | Selected | Unselected`
  - `状态`: `Enabled | Hover | Pressed | Focus | Loading | Disabled`
- Loading state composes text + progress glyph

## Quantified Spec
- Medium:
  - height: `40px`
  - min width: `120px`
  - horizontal padding: `16px`
  - radius: `20px`
  - gap: `8px`
- Small:
  - height: `28px`
  - min width: `72px`
  - horizontal padding: `8px`
  - radius: `14px`
  - gap: `4px`
- Typography:
  - `Medium + Emphasized/Normal/Warning/Text`: `HarmonyHeiTi Medium 16px`
  - `Small + Emphasized/Normal/Warning/Text`: `HarmonyHeiTi Medium 14px`
  - `Medium + Selected/Unselected`: `HarmonyHeiTi Regular 14px`
  - `Small + Selected/Unselected`: `HarmonyHeiTi Regular 14px`
  - line-height: `21px` for `16px` text, `20px` for `14px` text
- Key colors:
  - emphasized fill: `#0A59F7`
  - warning text: `#E84026`
  - tertiary surface: `rgba(0,0,0,0.0470588244)`
  - selected fill: `rgba(10,89,247,0.2)`
  - primary text: `rgba(0,0,0,0.8980392218)`
  - hover overlay: `rgba(0,0,0,0.0470588244)`
  - pressed overlay: `rgba(0,0,0,0.0980392173)`
  - focus ring: `#0A59F7`

## Props
```ts
interface ButtonProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, "children" | "disabled" | "type"> {
  尺寸?: "Medium" | "Small"
  类型?: "Emphasized" | "Normal" | "Warning" | "Text" | "Selected" | "Unselected"
  状态?: "Enabled" | "Hover" | "Pressed" | "Focus" | "Loading" | "Disabled"
}
```

## DSL ↔ Prop

| DSL field | React prop | Legal values |
| --- | --- | --- |
| `尺寸` | `尺寸` | `Medium` `Small` |
| `类型` | `类型` | `Emphasized` `Normal` `Warning` `Text` `Selected` `Unselected` |
| `状态` | `状态` | `Enabled` `Hover` `Pressed` `Focus` `Loading` `Disabled` |

组件 Props 直接使用 Pixso 原始中文轴名，不再做英文映射；同时不暴露 `children` / `disabled` 作为 DSL 外的视觉配置入口，文案与禁用态均由 `尺寸`、`类型`、`状态` 三条 Pixso 轴决定。

## 卡片内操作关联

当 `Button` 位于 Card 内时，操作层级与使用边界以 [`card.md` 的“卡片内操作层级”](./card.md#卡片内操作层级)为准。本组件规格只定义 Button 的变体与 API，不重复定义卡片内的操作决策，避免规则漂移。

## Style References
- `src/styles/global.css`
  - `--button-harmony-blue`
  - `--button-harmony-warning`
  - `--button-harmony-tertiary`
  - `--button-harmony-selected`
  - `--button-harmony-primary-text`
  - `--button-harmony-secondary-text`
  - `--button-harmony-hover`
  - `--button-harmony-pressed`
  - `--button-harmony-ring`
  - `--button-harmony-on-primary`
  - `--button-harmony-font-family`

## Button-2in1 变体（同目录内部实现）

- Pixso: `https://pixso.cn/app/design/QeDttX-H4qVEUZXJjNfTCw?item-id=5364:21065`
- 圆角 `8px`（主 Button 为胶囊圆角）；`Small` 仅支持 `Emphasized / Normal`
- 禁用态字段为 `Disable`（主 Button 为 `Disabled`）
- 固定宽度：`Medium` 常规态 `120px`、Loading `128px`；`Small` 常规态 `72px`、Loading `86px`；`Small + Emphasized + Disable` 为 `80px`
- Storybook 入口：`TwoInOneMatrix`、`TwoInOneLoadingNormal`、`TwoInOneSmallEmphasizedLoading`

## Tradeoffs
- Pixso 的 `get_variants` 没返回结构，因此 `button.json` 中的 `variantOptions` 与根节点元数据由 `get_node_dsl` / `design_to_code` 联合校准；现有子节点 guid 延续同一套 Button 组件变体定义，供 Storybook 矩阵和 Props 轴使用。
- Loading 图形使用内联 SVG + CSS 旋转尾迹复刻轨道式动效，不依赖临时图片资源；图形颜色直接继承按钮 `color`，与文本文字保持一致。
- 自动视觉回归脚本未完成：本地缺少 `pngjs`，且 Playwright Chromium 未安装，因此本轮校验依据为 Pixso 真值图、DSL/codegen 量化参数、以及 Storybook 本地入口可达性确认。
