# BigImageCardTwoColumnNormal 大图卡片-两列-普通

## Metadata

- **实现目录**：`src/blocks/big-image-card-two-column-normal/`
- **Stories 路径**：`src/blocks/big-image-card-two-column-normal/BigImageCardTwoColumnNormal.stories.tsx`
- **Pixso 链接**：https://pixso.cn/app/design/xFQdeTDAPFQG4jOEn2upBQ?item-id=22:12423
- **MCP 工具来源**：`get_node_dsl` (Success), `get_screenshot` (Success), `get_variants` ({} — 非组件集节点，无变体), `design_to_code` (Cache expired)

## 组件变体树 JSON

- **路径**：`src/blocks/big-image-card-two-column-normal/big-image-card-two-column-normal.json`
- 该节点非组件集，无变体（`get_variants` 返回空）。`pixTreeNodes` 从 `get_node_dsl` 子节点层级提取。

## 组成与用途

- **导出项**：`BigImageCardTwoColumnNormal`、`BigImageCardTwoColumnNormalProps`
- **使用场景**：两列布局中的普通大图卡片，用于展示含背景图、分类标签和标题的内容入口。适用于指南、美食、探店等推荐类内容网格展示。

## 量化规格

| 属性 | 值 | DSL 来源 |
|------|------|----------|
| 卡片宽度 | 160px | DSL 22:12423 width |
| 卡片高度 | 213px | DSL 22:12423 height |
| 卡片圆角 | 20px | DSL 22:12423 cornerRadius |
| 背景图片覆盖 | 160×213, object-fit: cover | DSL 22:12424 RECTANGLE |
| 渐变覆盖区域 | 160×106, top=107 | DSL 22:12425 VECTOR |
| 渐变色标 0% | rgba(19,36,8,0) | DSL 22:12425 stop 0 |
| 渐变色标 40% | rgba(19,36,8,0.8) | DSL 22:12425 stop 0.4 |
| 渐变色标 100% | rgba(19,36,8,1) | DSL 22:12425 stop 1 |
| 分类标签字号 | 10px | DSL 22:12428 fontSize |
| 分类标签字重 | 500 (Medium) | DSL 22:12428 fontWeight |
| 分类标签颜色 | rgba(255,255,255,0.6) | DSL 22:12428 fillPaints |
| 分类标签位置 | top=137, left=12 | DSL 22:12428 |
| 分类标签行高 | 14px | DSL 22:12428 lineHeightNumber |
| 标题字号 | 16px | DSL 22:12426 fontSize |
| 标题字重 | 700 (Bold) | DSL 22:12426 fontWeight |
| 标题颜色 | rgba(255,255,255,0.9) | DSL 22:12426 fillPaints |
| 标题行高 | 24px | DSL 22:12426 lineHeightNumber |
| 标题最大行数 | 2 | DSL 22:12426 maxLines |
| 标题位置 | top=153, left=12, width=136 | DSL 22:12426 |
| 文本混合模式 | plus-lighter (LINEAR_DODGE) | DSL 22:12426/22:12428 blendMode |

### 布局约束

所有内容元素使用绝对定位（DSL 非 Auto Layout 节点），坐标精确对齐：

- 背景图片：绝对定位，覆盖整个卡片 (0,0,100%,100%)
- 渐变遮罩：绝对定位，top=107px, height=106px
- 分类标签：绝对定位，top=137px, left=12px
- 标题：绝对定位，top=153px, left=12px, right=12px

## 状态与交互

本组件为**纯展示组件**，无交互状态。图片使用 `loading="lazy"` 延迟加载。

## Props

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `图片` | `string` | — | 卡片封面图 URL。对应 DSL 节点 22:12424 |
| `分类标签` | `string` | `"指南"` | 分类标签文案。对应 DSL 节点 22:12428 |
| `标题` | `string` | `"深圳周末"出逃"计划：私藏后花园指南"` | 标题文案，最多 2 行截断。对应 DSL 节点 22:12426 |
| `className` | `string` | — | 外部样式类名 |

### DSL ↔ Prop 对照

| DSL 节点/属性 | 实现 Prop | 说明 |
|--------------|----------|------|
| 22:12424 RECTANGLE IMAGE fill | `图片` | 图片 URL，默认值为空时不渲染 img |
| 22:12428 text "指南" | `分类标签` | 字符串，默认值与 DSL 一致 |
| 22:12426 text "深圳周末"出逃"计划：私藏后花园指南" | `标题` | 字符串，默认值与 DSL 一致 |

## 样式引用

组件使用作用域 CSS 自定义属性（定义于 `big-image-card-two-column-normal.css`），未引用 `global.css` 中的 Token。原因：本卡片为**深色背景卡片**，文字色使用白色系透明度阶梯（90%/60%），与全局 Harmony Token 的浅色主题语义不完全匹配。

- 字体：`HarmonyHeiTi`, `Geist Variable`（与 `global.css` `--button-harmony-font-family` 一致）
- 布局：Absolute positioning（DSL 非 Auto Layout 节点）
- 渐变：CSS `linear-gradient`，色标位置从 DSL gradient stops 直接映射

## 取舍说明

1. **`get_variants` 返回空**：Pixso 节点 22:12423 为 FRAME，非组件集，无变体暴露。
2. **`design_to_code` 缓存过期**：`localhost:3667` 资源已失效，样式全部基于 `get_node_dsl` + `get_screenshot` 手工还原。
3. **图片资源不可提取**：DSL 中的图片为 Pixso 内部资源（hash: `Rectangle_22_12424`, 1080×1505），无法提取到本地；`图片` Prop 需由调用方提供 URL。
4. **混合模式**：标题与分类标签在 DSL 中设置 `blendMode: LINEAR_DODGE`，CSS 中使用 `mix-blend-mode: plus-lighter`（CSS 中最接近 LINEAR_DODGE 的等价表达）。该效果在白色文字叠加于深色背景时视觉差异极小。
5. **渐变遮罩**：DSL 中使用带 transform 矩阵的渐变向量（90° 旋转 + 平移）。CSS 中使用 `linear-gradient(to bottom, ...)` 近似还原，色标位置从 DSL gradient stops 直接映射，视觉效果等效。
6. **卡片背景色**：DSL 渐变终点为 `rgba(19,36,8,1)`（深绿色），CSS 中卡片 `background-color` 设为 `#132408`，与渐变终点一致，确保无图片降级时视觉合理。
