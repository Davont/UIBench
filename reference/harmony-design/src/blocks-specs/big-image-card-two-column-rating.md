# BigImageCardTwoColumnRating（大图卡片-两列-评分）

## Metadata

| 项目 | 值 |
|------|-----|
| 实现目录 | `src/blocks/big-image-card-two-column-rating/` |
| 组件 TSX | `src/blocks/big-image-card-two-column-rating/big-image-card-two-column-rating.tsx` |
| 组件 CSS | `src/blocks/big-image-card-two-column-rating/big-image-card-two-column-rating.css` |
| Stories | `src/blocks/big-image-card-two-column-rating/BigImageCardTwoColumnRating.stories.tsx` |
| 变体 JSON | `src/blocks/big-image-card-two-column-rating/big-image-card-two-column-rating.json` |
| Pixso 链接 | `https://pixso.cn/app/design/xFQdeTDAPFQG4jOEn2upBQ?item-id=29:12267` |
| 节点名称 | 大图卡片-两列 |
| MCP 工具来源 | `get_node_dsl` + `get_screenshot`（`get_variants` 与 `get_all_components` 均返回空，`design_to_code` 缓存过期） |

## 组件变体树 JSON

- 路径：`src/blocks/big-image-card-two-column-rating/big-image-card-two-column-rating.json`
- `get_variants` 返回 `{}`，非组件集节点，无变体属性
- `pixTreeNodes` 基于 `get_node_dsl`（itemId=29:12267）的节点树手工构建
- 降级说明：由于无可枚举变体，`variantOptions` 为空对象；`pixTreeNodes` 直接从 DSL childNode 提取

## 组成与用途

- **导出项**：`BigImageCardTwoColumnRating`（组件），`BigImageCardTwoColumnRatingProps`（类型）
- **使用场景**：两列网格中的评分大图卡片，展示酒店/餐厅/景点等推荐内容，包含封面图、名称、星级评分和距离信息

## 量化规格

### 尺寸与间距

| 属性 | 值 | 来源 |
|------|-----|------|
| 卡片宽度 | 146px | DSL Frame width |
| 卡片高度 | 200px | DSL Frame height |
| 圆角 | 16px | DSL cornerRadius |
| 图片高度 | 156px | DSL Rectangle 29:12254 height |
| 渐变遮罩高度 | 84px | DSL Vector 29:12286 height |
| 渐变遮罩 top | 116px | DSL top |
| 标题 left | 12px | DSL Paragraph 29:12259 left |
| 标题 top | 138px | DSL Paragraph 29:12259 top |
| 标题宽度 | 124px | DSL Paragraph 29:12259 width (实际 122px + 2px 安全) |
| 评分行 top | 174px | DSL 评分/距离/星星 y 坐标 |

### 字体

| 元素 | fontSize | fontWeight | lineHeight | fontFamily | 来源 |
|------|----------|------------|------------|------------|------|
| 标题 | 12px | 700 (Bold) | 16px (32px/2行) | HarmonyHeiTi | DSL 29:12259 |
| 评分 | 10px | 600 (Semibold) | 14px | HarmonyOS Sans 2025 | DSL 29:12261 |
| 距离 | 10px | 400 (Regular) | 14px | HarmonyOS Sans SC 2025 | DSL 29:12266 |

### 色值

| 属性 | 值 | 来源 |
|------|-----|------|
| 标题颜色 | rgba(255,255,255,0.9) | DSL fillPaints color + alpha |
| 评分颜色 | #F9A01E (rgba(249,160,30,1)) | DSL fillPaints / localStyle Light/multi_color_10 |
| 距离颜色 | rgba(255,255,255,0.6) | DSL fillPaints |
| 渐变起 | rgba(89,66,45,0) | DSL gradient stops[0] |
| 渐变中1 | rgba(89,66,45,0.746) | DSL gradient stops[1] |
| 渐变中2 | rgba(89,66,45,0.933) | DSL gradient stops[2] |
| 渐变止 | rgba(89,66,45,1) | DSL gradient stops[3] |

## 状态与交互

| 状态 | 行为 |
|------|------|
| default | 静态卡片展示 |
| hover | 整体 scale(1.02) + 阴影增强（可选） |
| active/pressed | scale(0.98) |
| 无图片 | 显示占位背景色 |

## Props

| DSL 字段/节点 | Prop 名 | 类型 | 默认值 | 说明 |
|---------------|---------|------|--------|------|
| 29:12254 (image) | 图片 | `string` | `""` | 卡片封面图 URL |
| 29:12259 (paragraph) | 标题 | `string` | `"鹏瑞莱佛士酒店·云景Yun Jing"` | 标题文案，最多2行截断 |
| 29:12261 (paragraph) | 评分 | `string` | `"4.5"` | 评分数字 |
| 29:12266 (paragraph) | 距离 | `string` | `"距我 10.2 公里"` | 距离文案 |

### DSL ↔ Prop 对照

```
DSL 29:12254 image fill  →  图片: string
DSL 29:12259 nodeText    →  标题: string
DSL 29:12261 nodeText    →  评分: string
DSL 29:12266 nodeText    →  距离: string
```

无命名映射例外 — 所有 Prop 名直接使用 DSL 中文语义字段。

## 样式引用

### 使用的全局 Token（`global.css`）

| Token | 用途 |
|-------|------|
| `--harmony-font-primary` | 标题文字色（white 90%）— 不直接使用，保留组件内精确值 |
| `--harmony-font-secondary` | 距离文字色（white 60%）— 语义对齐 |
| `--harmony-comp-background-primary` | 可作为卡片背景色 fallback |

### 本组件专用 CSS 变量（定义在 `big-image-card-two-column.css`）

| 变量 | 值 | 来源 |
|------|-----|------|
| `--bictc-width` | 146px | DSL Frame width |
| `--bictc-height` | 200px | DSL Frame height |
| `--bictc-radius` | 16px | DSL cornerRadius |
| `--bictc-image-height` | 156px | DSL 29:12254 |
| `--bictc-gradient-top` | 116px | DSL 29:12286 top |
| `--bictc-gradient-height` | 84px | DSL 29:12286 height |
| `--bictc-title-font-size` | 12px | DSL 29:12259 |
| `--bictc-title-color` | rgba(255,255,255,0.9) | DSL 29:12259 |
| `--bictc-rating-color` | #F9A01E | DSL localStyle Light/multi_color_10 |
| `--bictc-distance-color` | rgba(255,255,255,0.6) | DSL 29:12266 |
| `--bictc-content-padding-x` | 12px | DSL 29:12259 left |

## 取舍说明

- `get_variants` 返回 `{}`，无变体属性可枚举；组件 Props 基于 DSL 中可变的文本/图片节点推导
- `design_to_code` 缓存过期（`Invalid batch timestamp`），样式完全基于 `get_node_dsl` 数值手工还原
- 标题 `lineHeight`：DSL 中 `lineHeightNumber: 14`，但 `maxLines: 2` 且区域高度 32px，实际行高按 16px（32/2）以确保两行截断一致性
- 渐变方向：DSL transform 矩阵包含旋转分量，简化处理为 `to bottom` 线性渐变（视觉效果等价）
- 星星图标：DSL 中有 SVG path 数据但 sha 引用方式；使用简化的内联 SVG star 图标
