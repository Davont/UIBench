# FloatingSelect-Phone

## Metadata

- **实现目录：** `src/components/FloatingSelectPhone/`
- **Stories 路径：** `src/components/FloatingSelectPhone/FloatingSelectPhone.stories.tsx`
- **Pixso 链接：** `https://pixso.cn/app/design/QeDttX-H4qVEUZXJjNfTCw?item-id=4941:1`
- **item-id：** `4941:1`
- **MCP 工具来源：** `get_node_dsl` (成功)。`get_screenshot` / `design_to_code` / `get_variants` 曾并发超时，本轮按用户要求以 `get_node_dsl` 为准补齐。

## 组件变体树 JSON

- **路径：** `src/components/FloatingSelectPhone/floating-select-phone.json`
- **生成方式：** 按 `get_node_dsl` 中的组件命名模式重建
- **变体字段：** `尺寸`、`状态`、`通透度`

## 组成与用途

- **导出项：** `FloatingSelectPhone`、`floatingSelectPhoneSizes`、`floatingSelectPhoneStates`、`floatingSelectPhoneOpacities`
- **使用场景：** 手机端浮层选择胶囊按钮，用于筛选或下拉入口；传入 `options` 后点击展示与 `Select` 相同的 `PopupMenu`

## 量化规格

### Medium

| 属性 | 值 |
|------|-----|
| 宽度 | 95px |
| 高度 | 40px |
| 圆角 | 20px |
| 内边距 | 8px 8px 8px 16px |
| 子项间距 | 2px |
| 字号 | 16px |
| 字重 | 500 |
| 行高 | 21px |
| 字体 | HarmonyHeiTi |
| 图标尺寸 | 24 × 24 |

### Small

| 属性 | 值 |
|------|-----|
| 宽度 | 62px |
| 高度 | 28px |
| 圆角 | 20px |
| 内边距 | 2px 0 2px 8px |
| 子项间距 | 0px |
| 字号 | 14px |
| 字重 | 500 |
| 行高 | 19px |
| 字体 | HarmonyHeiTi |
| 文本宽度 | 总宽 30px，按设计稿将 `Select` 显示为 `Se...` |
| 图标尺寸 | 24 × 24 |

## 通透度与材质

| 通透度 | 视觉来源 | 实现映射 |
|------|------|------|
| 弱 | 弱背景 + background blur + 投影 | `--harmony-comp-background-tertiary` + `backdrop-filter` + `0 8px 48px rgba(0,0,0,0.08)` |
| 降档 | 弱背景 + 1px 黑色 10% 描边 | `--harmony-comp-background-tertiary` + `border rgba(0,0,0,0.1)` |
| 高 | 弱背景 | `--harmony-comp-background-tertiary` |
| 标准 | 弱背景 | `--harmony-comp-background-tertiary` |

## 状态与交互

| 状态 | 视觉效果 |
|------|------|
| Enabled | 仅展示当前材质表面 |
| Hover | 叠加 `--harmony-interactive-hover` |
| Pressed | 叠加 `--harmony-interactive-click` |
| Focus | 2px `--harmony-interactive-focus` 内描边 |
| Disabled | 整体内容 opacity 0.4 |

传入 `options` 时，组件复用 `Select` 的 `useSelectMenu` 与 `Menu 菜单类型="PopupMenu"`：点击按钮展开菜单，外部点击关闭，选择菜单项后同步 `value/defaultValue/onValueChange` 并关闭菜单。

## Props

```ts
interface FloatingSelectPhoneProps
  extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, "children" | "disabled"> {
  尺寸?: "Medium" | "Small"
  状态?: "Enabled" | "Hover" | "Pressed" | "Focus" | "Disabled"
  通透度?: "弱" | "降档" | "高" | "标准"
  文本?: string
  options?: SelectOption[]
  value?: string
  defaultValue?: string
  onValueChange?: (value: string) => void
  placeholder?: string
}
```

### DSL / 实例覆盖 ↔ Prop 对照

| 设计来源 | Prop 名 | 默认值 | 说明 |
|------|------|------|------|
| 组件命名 `尺寸=*` | `尺寸` | `"Medium"` | 直接沿用 Pixso 字段 |
| 组件命名 `状态=*` | `状态` | `"Enabled"` | 直接沿用 Pixso 字段，取值含 `Focus` |
| 组件命名 `通透度=*` | `通透度` | `"弱"` | 直接沿用 Pixso 字段 |
| `Text.nodeText = Select` | `文本` | `"Select"` | 对应实例文字覆盖 |
| 交互展示需求 | `options/value/defaultValue/onValueChange/placeholder` | - | 与 `Select` 组件的点击展开菜单效果一致 |

## 样式引用

### 使用的全局 Token

- `--harmony-comp-background-tertiary`
- `--harmony-interactive-hover`
- `--harmony-interactive-click`
- `--harmony-interactive-focus`
- `--harmony-font-primary`
- `--harmony-icon-primary`

### 新增全局 Token

无新增。组件完全复用现有 `src/styles/global.css` 变量。

## 取舍说明

1. **MCP 取数策略：** `get_screenshot` / `design_to_code` / `get_variants` 曾并发超时，本轮按用户要求先使用 `get_node_dsl`，变体树由 DSL 组件命名重建。
2. **Focus 描边：** 采用 2px 内描边复现蓝色聚焦状态，避免 backdrop/filter 叠加时外描边偏移。
3. **菜单交互：** 非 DSL 视觉变体字段，但为用户明确要求，复用 `Select` 的菜单逻辑以保持组件库交互一致。
