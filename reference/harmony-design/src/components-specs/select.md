# Spec: select

## Metadata
- Implementation: `src/components/Select/select.tsx`（Pixso `Select-Phone` 胶囊变体）
- 2in1 implementation: `src/components/Select/select-2in1.tsx`（Pixso `Select-2in1` 节点，仅作同目录内部变体，不单独注册组件）
- Stories: `src/components/Select/select.stories.tsx`
- Variant tree JSON: `src/components/Select/select.json`、`src/components/Select/select-2in1.json`
- Pixso Phone: `https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5319:20144`
- Pixso 2in1: `https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5322:20193`
## Composition — Phone 胶囊（`Select`）
- Variant axes:
  - `尺寸`: `Medium | Small`
  - `状态`: `Enabled | Hover | Pressed | Focused | Disabled`
- 圆角 `20px` 胶囊样式，固定文案 "Select"

## Quantified Spec — Phone
- Medium: 95×40，padding `8px 8px 8px 16px`，gap `2px`，字号 16px
- Small: 62×28，padding `4.5px 0 4.5px 8px`，gap `0`，字号 14px；label 总宽 `30px`，按设计稿将 `Select` 显示为 `Se...`
- Focused: 2px `--harmony-brand` 描边

## Props — Phone
```ts
interface SelectProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, "disabled"> {
  尺寸?: "Medium" | "Small"
  状态?: "Enabled" | "Hover" | "Pressed" | "Focused" | "Disabled"
}
```

## DSL ↔ Prop — Phone

| DSL field | React prop | Legal values |
| --- | --- | --- |
| `尺寸` | `尺寸` | `Medium` `Small` |
| `状态` | `状态` | `Enabled` `Hover` `Pressed` `Focused` `Disabled` |

## Select-2in1 变体（同目录内部实现）

- 圆角 `8px`（Phone 为胶囊圆角）；尺寸轴为 `normal | small`（非 `Medium | Small`）
- focused 状态名保留 DSL 小写 `focused`
- Medium 对应 normal: 95×40；Small 对应 small: 74×28
- Storybook 入口：`TwoInOneMatrix`、`TwoInOneFullPagePreview`

### Props — 2in1
```ts
interface Select2in1Props {
  尺寸?: "normal" | "small"
  状态?: "Enabled" | "Hover" | "Pressed" | "focused" | "Disabled"
  children?: ReactNode
}
```

## Style References
- `--harmony-font-primary`
- `--harmony-icon-primary`
- `--harmony-comp-background-tertiary`
- `--harmony-interactive-hover`
- `--harmony-interactive-click`
- `--harmony-interactive-focus`
- `--harmony-brand`（Phone Focused 描边）

## Tradeoffs
- `get_variants` 对两个 Pixso 节点均返回空，变体树从 `get_node_dsl` 子节点矩阵重建。
- CSS 类名保留 `hm-select-phone` / `hm-select-2in1` 前缀，避免影响已有视觉校验基线。
- 旧目录 `SelectPhone/`、`Select2in1/` 已删除，统一从 `src/components/Select/` 导入。
