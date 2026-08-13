# Card 组件规格

## Metadata

| 项目 | 值 |
|------|-----|
| 实现目录 | `src/components/Card/` |
| Stories 路径 | `src/components/Card/card.stories.tsx` |
| Pixso 链接 | `https://pixso.cn/app/design/HA_e8I2mE7Oa0b5ZoeokSA?item-id=5322:613` |
| MCP 工具来源 | `get_node_dsl` (5322:613)、`get_export_image`、`design_to_code` |
| 变体树 JSON | `src/components/Card/card.json`（由 `get_node_dsl` 提取结构，`get_variants` 返回空 `{}`，降级从 DSL `pixComponentTreeDslNodes` 重建） |

## 组成与用途

- **导出项**：`Card`（默认导出元素）、`card尺寸Options`（尺寸枚举）、`CardProps`、`Card尺寸` 类型
- **使用场景**：HarmonyOS 风格卡片容器，用于承载列表项、内容区块等。自带 5 个预设尺寸和可选装饰性图标按钮。

## 卡片内操作层级

Card 是页面内容或局部任务的容器，卡片内操作**不得抢占整页主操作的视觉层级**。默认禁止在内容卡片内使用 `Button 类型="Emphasized"` 主按钮；局部、可选、可稍后处理的操作（例如“去开启”“查看详情”“稍后处理”）必须使用 `Button 类型="Text"` 的品牌色文字按钮。

提交、保存、继续、下一步、确认、购买、审批、创建、完成等整页主动作，属于页面级主操作，应放入 `Page Primary Action Area`，不应作为卡片内主按钮。

| 卡片意图 | 推荐交互 | 不应使用 |
|---|---|---|
| 整张卡片进入详情、设置或下一层 | 整卡可点击，或使用右侧 chevron | 额外添加“查看详情”文字按钮 |
| 局部、可选、可延后的操作 | `Button 类型="Text"`，使用品牌色文字 | `Emphasized` 主按钮 |
| 关闭、更多、收藏、分享等无文案轻量动作 | `IconButton` | 带背景的大尺寸主按钮 |
| 单纯展示信息或状态 | 不提供操作；必要时使用可点击文本链接 | 为填充卡片而添加按钮 |
| 页面级关键动作 | `Page Primary Action Area` | 卡片内 `Emphasized` 主按钮 |

当卡片本身可点击时，避免在同一触达区域内嵌套按钮；将次级操作置于独立的尾部区域。仅当卡片是独立、不可拆分的任务单元，且 Pixso 设计稿或稳定本地组件 API 明确要求时，才允许在卡片内使用 `Emphasized`；该动作不得与页面级主操作竞争，并须在实现或生成日志中记录例外原因。

## 文字优先级

| 优先级 | 文本类型 | 卡片约束 |
|---|---|---|
| P0 | 权限名称、状态、数量、风险提示 | 默认必须完整展示，禁止省略；空间不足时允许换行并使卡片增长。 |
| P1 | 说明文案 | 最多两行；卡片高度随内容增长，不得通过固定高度、裁切或省略号压缩文本。 |
| P2 | 歌名、用户名、列表右侧辅助信息等 | 仅在 Pixso 设计稿或布局规格明确要求紧凑单行时，才可单行省略；不得把省略作为默认实现。 |

既有 Card 尺寸是视觉基线，不得限制 P0/P1 内容展示；当 P0/P1 文本需要更多垂直空间时，卡片须向下扩展。

## 组件变体树 JSON

文件路径：`src/components/Card/card.json`

生成依据：`get_variants` 返回 `{}`，改为从 `get_node_dsl` 的 `pixComponentTreeDslNodes` 提取 5 个组件定义节点（Max/Larger/Medium/Small/Mini），每个含一个或两个 Icon Button 子节点。

```json
{
  "variantOptions": {
    "尺寸": ["Max", "Larger", "Medium", "Small", "Mini"]
  },
  "pixTreeNodes": [/* 5 个变体节点，含 guid、variants、childNode */]
}
```

## 量化规格

### 尺寸（宽 × 高）

| 尺寸 | 宽 | 高 | Icon Button 位置 |
|------|-----|-----|-----|
| Max | 328px | 496px | right:12px, bottom:12px |
| Larger | 328px | 328px | right:12px, bottom:12px |
| Medium | 328px | 156px | right:12px, bottom:12px |
| Small | 156px | 156px | right:12px, bottom:12px |
| Mini | 328px | 56px | left:12px, top:12px + right:12px, top:12px（双按钮） |

### 圆角

- 卡片容器：`20px`（DSL: `cornerRadius: 20`，所有尺寸一致）

### 色值

| 元素 | Pixso 样式 | 对应 Token | 取值 |
|------|-----------|-----------|------|
| 卡片背景 | `Light/comp_background_list_card` (602:9416) | `--harmony-comp-background-list-card` | rgba(255, 255, 255, 1) |
| Icon Button 背景 | `Light/comp_background_tertiary` (602:9420) | `--harmony-comp-background-tertiary` | rgba(0, 0, 0, 0.047) |
| Icon 颜色 | `Light/icon_primary` (602:9459) | `--harmony-icon-primary` | rgba(0, 0, 0, 0.898) |

### Icon Button 规格

| 属性 | 值 | 来源 |
|------|-----|------|
| 尺寸 | 32×32px | DSL `尺寸=32` 组件 |
| 圆角 | 999px（正圆） | DSL `cornerRadius: 800` |
| 内部图标 | HM Symbol `square_dashed` (󰄴) | DSL `nodeText` / `fontFamily: "HM Symbol"` |
| 图标尺寸 | 24px | DSL `fontSize: 24` |
| 图标居中偏移 | (4, 4) | DSL `top: 4, left: 4` |

## 状态与交互

- **Default**：白底卡片 + 可见图标按钮
- **Disabled / 隐藏图标按钮**：`hideIconButton=true` 时隐藏图标按钮，仅保留卡片容器
- 无 hover/active/focus 等额外交互态（纯容器组件）

## Props

| Prop | 类型 | 默认值 | DSL 字段 | 说明 |
|------|------|--------|---------|------|
| `尺寸` | `"Max" \| "Larger" \| "Medium" \| "Small" \| "Mini"` | `"Medium"` | Pixso `尺寸` 属性 | 控制卡片宽高 |
| `children` | `ReactNode` | — | — | 卡片内容插槽 |
| `hideIconButton` | `boolean` | `false` | — | 隐藏装饰性图标按钮 |
| `className` | `string` | — | — | 自定义类名 |
| `...props` | `ComponentPropsWithoutRef<"div">` | — | — | 透传 div 属性 |

### DSL ↔ Prop 对照

| DSL 属性 / 字段 | React Prop | 映射说明 |
|----------------|-----------|---------|
| Pixso `尺寸` 变体属性（取值：Max, Larger, Medium, Small, Mini） | `尺寸` | **直接使用**，名称与取值集合完全一致 |
| 组件实例 `props[].componentId` → 1:11537/1:11527/1:11530/1:11540/1:11533 | `尺寸` 内部映射 | 5 个变体组件与 `尺寸` 值一一对应 |

无命名映射例外——Prop 名与 DSL 属性名完全一致。

## 样式引用

### 使用的全局 Token

| Token | 用途 |
|-------|------|
| `--harmony-comp-background-list-card` | 卡片背景 |
| `--harmony-comp-background-tertiary` | Icon Button 圆形背景 |

### 新增全局 Token

无。现有 `--harmony-comp-background-list-card` 与 `--harmony-comp-background-tertiary` 已精确覆盖 Pixso 色值，无需新增。

## 取舍说明

| 项目 | 说明 |
|------|------|
| Icon Button | 组件内自实现轻量版（32×32 圆形 + HM Symbol 图标），未复用 `src/components/IconButton` 完整组件。原因：Card 内的 Icon Button 逻辑简单、固定样式，与独立 IconButton 组件的多尺寸/多通透度/多图标计数 API 重叠度低。 |
| `get_variants` 返回 `{}` | 降级从 `get_node_dsl` 的 `pixComponentTreeDslNodes` 提取变体树结构，并在 `card.json` 中记录重建依据。 |
| `get_screenshot` 不可用 | 转为 `get_export_image` 获取视觉真值，已下载 PNG 进行人工对照。 |
