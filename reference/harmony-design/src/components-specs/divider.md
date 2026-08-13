# Divider 分割线

## Metadata

| 字段 | 值 |
|------|------|
| 实现目录 | `src/components/Views/Divider` |
| Stories 路径 | `src/components/Views/Divider/Divider.stories.tsx` |
| Pixso 链接 | https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5410:23710 |
| item-id | `5410:23710` |
| MCP 工具来源 | `get_node_dsl`, `get_screenshot` |
| 变体树 JSON | `src/components/Views/Divider/Divider.json`（由 `get_node_dsl` 生成） |

## 组成与用途

- **导出项**: `Divider`, `hmDividerSizes`, `hmDividerOrientations`, `hmDividerVariants`, `DividerProps`, `HmDividerSize`, `HmDividerOrientation`, `HmDividerVariant`
- **用途**: 统一横向/竖向、实线/虚线分隔，避免业务资产手写 `height/background/border/transform` 画线

## 量化规格

| 属性 | 尺寸=0.5 | 尺寸=1 | 尺寸=8 |
|------|----------|--------|--------|
| 横向尺寸 | 视觉 0.5px 高 | 1px 高 | 8px 高 |
| 竖向尺寸 | 视觉 0.5px 宽 | 1px 宽 | 8px 宽 |
| 默认颜色 | `--harmony-comp-divider` | `--harmony-comp-divider` | `--harmony-comp-background-tertiary` |
| 可覆盖颜色 | `颜色` prop | `颜色` prop | `颜色` prop |
| 圆角 | 无 | 无 | 无 |

## 状态与交互

无交互状态，纯展示组件。

## Props

```typescript
interface DividerProps extends HTMLAttributes<HTMLDivElement> {
  /** 分割线尺寸：0.5 = 发丝线, 1 = 1px 实线, 8 = 粗块 */
  尺寸?: "0.5" | "1" | "8"
  /** 分割线方向 */
  方向?: "horizontal" | "vertical"
  /** 分割线样式 */
  样式?: "solid" | "dashed"
  /** 覆盖分割线颜色，支持 CSS var 或任意 CSS color */
  颜色?: string
}
```

### DSL ↔ Prop 对照

| DSL 字段路径 | DSL 取值 | Prop 名 | Prop 类型 | 默认值 |
|-------------|---------|---------|-----------|--------|
| 节点名中的变体属性 `尺寸` | `"0.5"`, `"8"` | `尺寸` | `"0.5" \| "1" \| "8"` | `"0.5"` |
| 代码治理扩展 | 横向/竖向 | `方向` | `"horizontal" \| "vertical"` | `"horizontal"` |
| 代码治理扩展 | 实线/虚线 | `样式` | `"solid" \| "dashed"` | `"solid"` |

- **命名策略**: DSL 中节点名格式为 `尺寸=X`，属性名 `尺寸` 直接使用，无命名映射。
- **取值集合**: DSL 中原始 `"0.5"` 和 `"8"` 保留；为替换资产中的竖向 1px 结构分割线，代码层新增 `"1"` 尺寸。

## 样式引用

| Token | 取值 | 用途 |
|-------|------|------|
| `--harmony-comp-divider` | `rgba(0, 0, 0, 0.2)` | 尺寸=0.5 细线颜色 |
| `--harmony-comp-background-tertiary` | `rgba(0, 0, 0, 0.047)` | 尺寸=8 粗块背景色 |

以上 Token 均已存在于 `src/styles/global.css`，无需新增。

## 取舍说明

- DSL 中根容器（406×83px）仅用于展示两个变体实例的对比布局，组件实现取每个变体实例自身属性（360×1px / 360×8px），不硬编码容器尺寸。
- 组件宽度使用 `100%` 而非固定 360px，由父容器控制实际宽度，符合通用分割线组件行为。
- 业务资产使用 `Divider` 渲染线条；本地 CSS 只保留定位、inset、margin、width/height 约束，不再声明分割线绘制用的 background、hairline border 或 scale。
