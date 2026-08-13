# BigImageCard 大图卡片-首屏大卡片

## Metadata

- **实现目录**：`src/blocks/big-image-card/`
- **Stories 路径**：`src/blocks/big-image-card/BigImageCard.stories.tsx`
- **Pixso 链接**：https://pixso.cn/app/design/xFQdeTDAPFQG4jOEn2upBQ?item-id=22:12739
- **MCP 工具来源**：`get_node_dsl` (Success), `get_screenshot` (Success), `get_variants` ({} — 非组件集节点，无变体), `design_to_code` (Cache expired)

## 组件变体树 JSON

- **路径**：`src/blocks/big-image-card/big-image-card.json`
- 该节点非组件集，无变体（`get_variants` 返回空）。`pixTreeNodes` 从 `get_node_dsl` 子节点层级提取。

## 组成与用途

- **导出项**：`BigImageCard`、`BigImageCardProps`
- **使用场景**：首屏大图卡片，用于展示含背景图、主标题、推荐语和地点信息的精选内容卡片。适用于旅游推荐、美食精选等内容发现场景。

## 量化规格

| 属性 | 值 | DSL 来源 |
|------|------|----------|
| 卡片宽度 | 328px | DSL 22:12740 width |
| 卡片高度 | 328px | DSL 22:12740 height |
| 卡片圆角 | 20px | DSL 22:12740 cornerRadius |
| 卡片背景色 | #735631 | DSL 22:12740 fillPaints |
| 图片高度 | 246px | DSL 22:12741 height |
| 渐变覆盖高度 | 195px | DSL 29:12271 height |
| 渐变起始位置 | y=133 | DSL 29:12271 top |
| 标题字号 | 24px | DSL 22:12745 fontSize |
| 标题字重 | Bold (700) | DSL 22:12745 fontStyle |
| 标题颜色 | rgba(255,255,255,0.9) | DSL style 2:376058 "固定白色90" |
| 标题行高 | 27px | DSL 22:12745 height |
| 标题 Blend Mode | plus-lighter (LINEAR_DODGE) | DSL 22:12745 blendMode |
| 推荐语字号 | 14px | DSL 22:12746 fontSize |
| 推荐语字重 | Regular (400) | DSL 22:12746 fontWeight |
| 推荐语颜色 | rgba(255,255,255,0.4) | DSL style 2:376239 "固定白色40" |
| 推荐语最大行数 | 2 | DSL 22:12746 maxLines |
| 推荐语行高 | 16px | 32px / 2 lines |
| 推荐语文字投影 | 0px 0px 2px rgba(0,0,0,0.2) | DSL style 2:376238 "栏目名称投影" |
| 推荐语 Blend Mode | plus-lighter (LINEAR_DODGE) | DSL 22:12746 blendMode |
| 地点图标尺寸 | 16×16px | DSL 22:12747 |
| 地点文字字号 | 12px | DSL 22:12752 fontSize |
| 地点文字行高 | 16px | DSL 22:12752 height |
| 地点次要文字色 | rgba(255,255,255,0.6) | DSL 22:12752_0_2 fillPaints |
| 地点主要文字色 | rgba(255,255,255,0.9) | DSL 22:12752_0_1 fillPaints |
| 内容区左右内边距 | 12px | DSL 各文本节点 left=12 |
| 内容区底部内边距 | 17px | 328 - 295 - 16 |

### 布局约束

所有文本节点使用 `verticalConstraint: "MAX"`（底部约束），内容区从卡片底部向上排列：

- 底部内边距：17px
- 地点行（图标+文字）：16px
- 地点→推荐语间距：11px
- 推荐语（最大2行）：32px
- 推荐语→标题间距：2px
- 标题：27px

## 状态与交互

本组件为**纯展示组件**，无交互状态。图片使用 `loading="lazy"` 延迟加载。

## Props

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `图片` | `string` | — | 卡片背景图 URL。对应 DSL 节点 22:12741 (image 425) |
| `标题` | `string` | `"吃brunch！好chill！"` | 主标题文案。对应 DSL 节点 22:12745 (实例 108 / Size1) |
| `推荐语` | `string` | `"推荐语占位推荐语占位..."` | 推荐语/副标题，最多 2 行截断。对应 DSL 节点 22:12746 |
| `地点数` | `number` | `12` | 地点数量。对应 DSL 节点 22:12752 |
| `地点名` | `string` | `"圣家堂"` | 地点名称。对应 DSL 节点 22:12752 (SemiBold span) |
| `卡片背景色` | `string` | `"#735631"` | 卡片背景色与渐变遮罩基色。对应 DSL 节点 22:12740 fill |
| `className` | `string` | — | 外部样式类名 |

### DSL ↔ Prop 对照

| DSL 节点/属性 | 实现 Prop | 说明 |
|--------------|----------|------|
| 22:12741 image fill | `图片` | 图片 URL，默认值为空时不渲染 img |
| 22:12745 text "吃brunch！好chill！" | `标题` | 字符串，默认值与 DSL 一致 |
| 22:12746 text "推荐语占位..." | `推荐语` | 字符串，默认值与 DSL 一致 |
| 22:12752 " 等 12 个地点圣家堂" | `地点数` + `地点名` | 拆分为数量与名称，渲染格式 " 等 {N} 个地点{名称}" |
| 22:12740 fill #735631 | `卡片背景色` | 默认值与 DSL 一致；变更后同步更新渐变遮罩 |

## 样式引用

组件使用作用域 CSS 自定义属性（定义于 `big-image-card.css`），未引用 `global.css` 中的 Token。原因：本卡片为**深色背景卡片**，文字色使用白色系透明度阶梯（90%/60%/40%），与全局 Harmony Token 的浅色主题语义不完全匹配。

- 字体：`HarmonyHeiTi`, `Geist Variable`（与 `global.css` `--button-harmony-font-family` 一致）
- 布局：Flexbox + absolute positioning
- 图标：内联 SVG（location pin，16×16，白色 60% 填充）

## 取舍说明

1. **`get_variants` 返回空**：Pixso 节点 22:12739 为 FRAME，非组件集，无变体暴露。
2. **`design_to_code` 缓存过期**：`localhost:3667` 资源已失效，样式全部基于 `get_node_dsl` + `get_screenshot` 手工还原。
3. **图片资源不可提取**：DSL 中的图片为 Pixso 内部资源（hash: `68df7e9e0f2567cc4d69eeda0905acc3b63a6c81`），无法提取到本地；`图片` Prop 需由调用方提供 URL，默认值为空（不渲染 img）。
4. **地点图标**：DSL 中为 VECTOR 节点（svgSha: "local"），无法提取原始 SVG path data。使用语义等价的标准 location pin SVG 图标替代，视觉上以截图对照确认。
5. **渐变遮罩**：DSL 中使用了带 transform 矩阵的渐变向量。CSS 中使用 `linear-gradient(to bottom, ...)` 近似还原，色标位置从 DSL 的 gradient stops 直接映射。
6. **混合模式**：标题与推荐语在 DSL 中设置 `blendMode: LINEAR_DODGE` / `LINEAR_DODGE`，CSS 中使用 `mix-blend-mode: plus-lighter`（CSS 中最接近 LINEAR_DODGE 的等价表达）。该效果在白色文字叠加于深色背景时视觉差异极小。
7. **`卡片背景色` 动态渐变**：当 `卡片背景色` 非默认值时，通过内联 style 动态生成匹配的渐变遮罩（hex + alpha 合成），确保渐变终点与卡片背景色一致。
