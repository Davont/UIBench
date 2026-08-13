# ScrollBar 组件规格

## Metadata

| 项目 | 值 |
| ------ | ------ |
| 实现目录 | `src/components/ScrollBar/` |
| Stories 路径 | `src/components/ScrollBar/ScrollBar.stories.tsx` |
| Pixso 链接 | [5410:23811](https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5410:23811) |
| MCP 工具来源 | `get_node_dsl` (5410:23811) + `get_screenshot` (5410:23811) |
| 变体树 JSON | `src/components/ScrollBar/ScrollBar.json`（由 `get_node_dsl` + `get_variants` 降级构建） |

## 组件变体树 JSON

- **文件路径**: `src/components/ScrollBar/ScrollBar.json`
- **数据来源**: `get_node_dsl` (5410:23811) 返回 `pixComponentTreeDslNodes`；`get_variants` 返回 `{}`（空），通过 DSL 中实例的 `componentNormName` 字段（"normal" / "press"）提取变体属性。
- **variantOptions**: `{ "状态": ["normal", "press"] }`

## 组成与用途

- **导出项**: `ScrollBar`（容器）、`ScrollBarThumb`（滑块）
- **使用场景**: 滚动区域的滚动条指示器，鸿蒙风格。滑块可独立使用或包裹于 ScrollBar 容器中。
- **复用现有组件**: 无直接依赖，纯样式组件。

## 量化规格

| 参数 | normal | press |
| ------ | ------ | ------ |
| 滑块宽度 | 4px | 8px |
| 滑块高度 | 80px | 80px |
| 圆角 (borderRadius) | 16px（全角） | 16px（全角） |
| 填充色 | `rgba(0,0,0,1)` → `comp_foreground_primary` | 同 |
| 不透明度 | 0.4 | 0.4 |
| 容器尺寸 | 32×80px | 32×80px |
| 滑块右间距 (right-margin) | 4px (left:24, width:4, 32-24-4=4) | 0px (left:20, width:8, 32-20-8=4) |
| 水平约束 | MAX（右对齐） | MAX（右对齐） |
| 过渡动画 | width 150ms ease-out | 同 |

> **坐标校验**: normal 态 `left:24, width:4` → 右边缘 = 24+4 = 28，距容器右边 = 32-28 = 4px。press 态 `left:20, width:8` → 右边缘 = 20+8 = 28，距容器右边 = 4px。两者右边缘一致，滑块从右边缘向左扩展 4px → 8px。

## 状态与交互

| 状态 | 触发方式 | 视觉变化 |
| ------ | ------ | ------ |
| normal | 默认 | 4px 宽滑块 |
| press | 用户拖拽/点击 | 8px 宽滑块，宽度过渡动画 |

## Props

### ScrollBarThumb

| Prop 名 | 类型 | 默认值 | DSL 对应字段 |
| ------ | ------ | ------ | ------ |
| 状态 | `"normal" \| "press"` | `"normal"` | `componentNormName` (实例级) |
| className | `string` | — | — |
| ...props | `HTMLAttributes<HTMLDivElement>` | — | — |

**DSL ↔ Prop 对照**:
- DSL `componentNormName` ∈ {`normal`, `press`} → Prop `状态` ∈ {`normal`, `press`}（直接使用 Pixso 原始属性名）

### ScrollBar

| Prop 名 | 类型 | 默认值 | 说明 |
| ------ | ------ | ------ | ------ |
| orientation | `"horizontal" \| "vertical"` | `"vertical"` | 滚动方向 |
| className | `string` | — | — |

## 样式引用

| Token / 类 | 取值来源 | 用途 |
| ------ | ------ | ------ |
| `bg-[rgba(0,0,0,1)]` | Pixso DSL fillPaints → `Light/comp_foreground_primary` | 滑块填充色 |
| `opacity-40` | Pixso DSL `opacity: 0.4` | 滑块不透明度 |
| `w-1` / `w-2` | Tailwind（4px / 8px） | 滑块宽度 |
| `h-20` / `h-full` | Tailwind（80px） | 滑块高度 |
| `rounded-full` | Tailwind（完全圆角 ≈ 16px on 80px height） | 滑块端圆角 |
| `transition-[width] duration-150 ease-out` | 实现补充 | normal↔press 过渡 |
| `bg-[#f3f4f6]` | 仓库 Storybook 约定 | 画布背景 |

**新增全局 Token**: 无。填充色可直接映射到 `rgba(0,0,0,1)`，与现有 `comp_foreground_primary` 一致。

## 取舍说明

- **无新增全局 Token**: 填充色 `rgba(0,0,0,1)` 与 `global.css` 中 `--harmony-comp_foreground_primary` 一致，直接复用。
- **horizontal 方向**: DSL 仅展示 vertical 态，horizontal 为合理推断扩展（8px 高轨道 + 过渡动画）。
- **组件抽象**: DSL 中 `ScrollBar` Frame 是两个实例并排的展示画板，实际使用抽象为 `ScrollBar`（容器）+ `ScrollBarThumb`（滑块）两层，滑块为核心还原对象。
