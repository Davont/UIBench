# RatingCard 评分卡片-普通

## Metadata

- **实现目录**：`src/blocks/rating-card/`
- **Stories 路径**：`src/blocks/rating-card/RatingCard.stories.tsx`
- **Pixso 链接**：https://pixso.cn/app/design/xFQdeTDAPFQG4jOEn2upBQ?item-id=22:12487
- **MCP 工具来源**：`get_node_dsl` (Success), `get_screenshot` (Success), `get_variants` ({} — 非组件集节点，无变体)

## 组件变体树 JSON

- **路径**：`src/blocks/rating-card/rating-card.json`
- 该节点非组件集，无变体（`get_variants` 返回空）。`pixTreeNodes` 从 `get_node_dsl` 子节点层级提取。

## 组成与用途

- **导出项**：`RatingCard`、`RatingCardProps`
- **使用场景**：展示聚合评分信息，包含评分分数（大号数字）、星级视觉呈现（复用 `RatingPhone`）、评分人数文案。适用于商品详情页、列表卡片等评分展示场景。

## 量化规格

| 属性 | 值 | DSL 来源 |
|------|------|----------|
| 卡片宽度 | 328px | DSL 22:12488 width |
| 卡片高度 | 72px | DSL 22:12488 height |
| 卡片圆角 | 20px | DSL 5:13945 cornerRadius |
| 卡片内边距 | 12px | DSL 22:12490 left=12 |
| 评分字号 | 38px | DSL 22:12490 fontSize |
| 评分数透明度 | 0.9 | DSL 22:12490 opacity |
| 评分人数字号 | 12px | DSL 22:12493 fontSize |

## 状态与交互

本组件为**纯展示组件**，无交互状态。星级通过 `RatingPhone`（`readOnly` 模式）渲染。

## Props

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `评分` | `number` | `4.5` | 评分分数。对应 DSL 节点 22:12490 |
| `评分人数` | `number` | `1024` | 评分总人数，展示时自动千分位格式化。对应 DSL 节点 22:12493 |
| `人数后缀` | `string` | `"人评分"` | 评分人数后缀文案 |
| `className` | `string` | — | 外部样式类名 |

### DSL ↔ Prop 对照

| DSL 节点 | 实现 Prop | 说明 |
|----------|----------|------|
| 22:12490 text "4.5" | `评分` | 数值型 |
| 22:12493 text "1,024 人评分" | `评分人数` + `人数后缀` | 拆分为数值和文案 |
| 22:12492 Rating-Phone | `RatingPhone` 组件 | 通过 CSS 覆盖星级尺寸为 16px 以匹配 DSL |

## 样式引用

- `--harmony-comp-background-primary` — 卡片背景
- `--harmony-font-primary` — 评分文字色
- `--harmony-font-secondary` — 评分人数文字色
- `RatingPhone` CSS 变量覆盖：`--rating-star-size: 16px`、`--rating-star-radius: 4px`、`--rating-gap: 0px`

## 取舍说明

1. **`get_variants` 返回空**：Pixso 节点非组件集，无变体暴露。
2. **星级复用 RatingPhone**：卡片内星级通过 `RatingPhone`（`readOnly`）渲染，CSS 覆盖星级尺寸为 16px 对齐 DSL。
3. **评分取整**：`RatingPhone` 仅支持整数评分 1-5，故 `评分` 经 `Math.round()` 后传入；分数文字仍保留原始小数值。
4. **`design_to_code` 缓存过期**：样式全部基于 `get_node_dsl` + `get_screenshot` 手工还原。
