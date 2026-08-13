# AlphabetIndexer 组件规格

## Metadata

| 字段 | 值 |
|------|------|
| 组件 ID | `alphabet-indexer` |
| 实现目录 | `src/components/Views/AlphabetIndexer/` |
| Stories 路径 | `src/components/Views/AlphabetIndexer/alphabet-indexer.stories.tsx` |
| Pixso 链接 | https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5410:23799 |
| MCP 工具来源 | `get_node_dsl` + `get_screenshot` + `get_export_image` + `design_to_code` |
| 变体树 JSON | `src/components/Views/AlphabetIndexer/alphabet-indexer.json` |

## 组成与用途

字母索引器样本组件，用于还原 Pixso 中联系人索引条的 `port` / `land` 两种展示形态。

**导出项：**
- `AlphabetIndexer`
- `AlphabetIndexerProps`
- `AlphabetIndexerType`
- `alphabetIndexerTypes`

**使用场景：**
- Storybook / 设计验收中的 1:1 对照样本
- 列表索引条资源沉淀

## 变体树

来源：`get_node_dsl` 顶层实例 + 组件树；`get_variants` 返回空，变体集合由 DSL 与 codegen 结构交叉确认。

- 顶层组件变体：`类型=port | land`
- `.Items` 子组件内部状态：`状态=enabled | hover | focus | activated`

注意：`状态` 属于 `.Items` 子组件，不是 `AlphabetIndexer` 顶层组件 Prop。

## 量化规格

### 顶层几何

| 属性 | port | land |
|------|------|------|
| 宽度 | 24px | 24px |
| 高度 | 284px | 224px |
| 左右内边距 | 3.998px | 4px |
| 布局方向 | vertical | vertical |

### 子项几何

| 元素 | 值 |
|------|------|
| item 尺寸 | 16 × 16px |
| item 内边距 | `1px 0` |
| item 圆角 | 20px |
| dot 尺寸 | 3 × 3px |
| star 图形尺寸 | 9 × 8.75px |

### Typography

| 属性 | 值 |
|------|------|
| fontFamily | `HarmonyHeiTi`, `HarmonyOS Sans SC`, `Geist Variable`, sans-serif |
| fontSize | 10px |
| fontWeight | 500 |
| lineHeight | 14px |
| letterSpacing | 0 |
| textAlign | center |

### 色值与 Token 映射

| 元素 | 色值 | Token |
|------|------|-------|
| 默认文字 | `rgba(0,0,0,0.6)` | `--harmony-font-secondary` |
| 激活文字 | `rgba(10,89,247,1)` | `--harmony-font-emphasize` |
| hover 背景 | `rgba(0,0,0,0.047059)` | `--harmony-interactive-hover` |
| activated 背景 | `rgba(10,89,247,0.1)` | `--harmony-comp-emphasize-tertiary` |
| dot | `rgba(0,0,0,0.4)` | `--harmony-font-tertiary` |
| star | Light: `rgba(0,0,0,0.6)` / Dark: `rgba(255,255,255,0.6)` | `--harmony-font-secondary` |
| 背景 | `rgba(255,255,255,1)` | `--harmony-background-primary` |

## 结构真值

### `类型=port`

固定序列：

`# → star → A → B → C → D → E → F → G(activated) → H → I → J(hover) → K → L → M → N → O → P → Q → R → S → T → U → V → W → X → Y → Z`

### `类型=land`

固定序列：

`# → A → · → G(activated) → · → J → · → O → · → S → · → W(hover) → · → Z`

## Props

### DSL ↔ Prop 对照表

| DSL 字段 / 路径 | Prop 名 | 可取值 | 说明 |
|-----------------|---------|--------|------|
| 顶层实例变体 `类型` | `类型` | `"port"` \| `"land"` | 直接使用 Pixso 原始字段名 |

### 类型签名

```ts
interface AlphabetIndexerProps extends HTMLAttributes<HTMLDivElement> {
  类型?: "port" | "land"
  activeLabel?: string
  defaultActiveLabel?: string
  labels?: readonly string[]
  onIndexSelect?: (label: string) => void
  onIndexPressStart?: (label: string) => void
  onIndexPressChange?: (label: string) => void
  onIndexPressEnd?: () => void
}
```

运行时约定：

- `activeLabel` 控制当前激活索引值；不传时组件使用 `defaultActiveLabel` 做非受控选中。
- `onIndexSelect` 在点击索引项时触发，父级列表应据此滚动到对应分组。
- `labels` 可用于定制索引项；不传时保持 Pixso 默认 `port` / `land` 序列。
- `onIndexPressStart` / `onIndexPressChange` / `onIndexPressEnd` 用于长按或按住拖动索引条时弹出、更新、收起放大预览 Label。

## Storybook

- `Playground`：单实例 + `类型` controls
- `Overview`：按 Pixso 根画板 125 × 473 的双列真值布局展示
- `Port`：单独展示 `类型=port`
- `Land`：单独展示 `类型=land`

## 样式引用

### 使用的 `global.css` Token

- `--harmony-background-primary`
- `--harmony-font-secondary`
- `--harmony-font-tertiary`
- `--harmony-font-emphasize`
- `--harmony-interactive-hover`
- `--harmony-comp-emphasize-tertiary`

### 新增资源

- `src/components/Views/AlphabetIndexer/assets/star.svg`
  - 来源：Pixso `Boolean_operation_1_9997.svg`
  - 用途：作为内联 SVG 路径来源，避免使用近似图标字形导致星标轮廓偏差，同时支持 dark 模式继承文字 token

## 取舍说明

1. 顶层组件不暴露 `状态` Prop：`get_node_dsl` 显示 `状态` 属于 `.Items` 子组件，而非顶层 `AlphabetIndexer-Phone` 的主变体。
2. 顶层组件保持 Pixso 固定示例态，不注入运行时 hover/focus 行为，避免浏览器交互覆盖设计稿中的指定状态。
3. `activated` 背景复用 `--harmony-comp-emphasize-tertiary`，与仓库现有 `rgba(10,89,247,0.1)` 映射保持一致。
