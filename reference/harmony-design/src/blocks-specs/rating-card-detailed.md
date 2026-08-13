# 评分卡片-详细 (RatingCardDetailed)

## Metadata

| 字段 | 值 |
|------|-----|
| 实现目录 | `src/blocks/rating-card-detailed/` |
| 组件文件 | `rating-card-detailed.tsx` |
| 样式文件 | `rating-card-detailed.css` |
| Stories | `rating-card-detailed.stories.tsx` |
| 变体树 JSON | `rating-card-detailed.json` |
| Pixso 链接 | `https://pixso.cn/app/design/xFQdeTDAPFQG4jOEn2upBQ?item-id=22:12494` |
| item-id | `22:12494` |
| MCP 工具来源 | `get_node_dsl` (Success), `get_screenshot` (Success), `get_variants` ({}) |

## 组件变体树 JSON

- 路径：`src/blocks/rating-card-detailed/rating-card-detailed.json`
- `get_variants` 返回 `{}`（非组件集节点），`get_all_components` 返回 `[]`（当前文档无远程组件库返回）
- 变体树从 `get_node_dsl` 完全重建，无变体属性（单一设计实例）

## 组成与用途

- **导出项**: `RatingCardDetailed` (组件), `RatingCardDetailedProps` (类型)
- **使用场景**: 展示用户评价的详细卡片，包含用户信息、星级评分、评价内容、图片及日期信息

## 量化规格

### 尺寸与布局

| 参数 | 值 | 来源 |
|------|-----|------|
| 卡片宽度 | 328px | DSL frame width |
| 卡片圆角 | 20px | Container/Cardview/Phone/Basic |
| 卡片背景 | `--harmony-comp-background-primary` (#ffffff) | DSL Card/light |
| 左右内边距 | 12px | DSL 子元素 left 坐标 |
| 顶部内边距 | 8px | DSL header top |
| 底部内边距 | 12px | 推算 |

### 头像

| 参数 | 值 | 来源 |
|------|-----|------|
| 尺寸 | 32×32px | DSL 22:12499 |
| 形状 | 圆形（border-radius: 50%） | DSL Mask 22:12514 |
| 占位背景 | `--harmony-comp-background-secondary` | 推定 |

### 星级

| 参数 | 值 | 来源 |
|------|-----|------|
| 单星尺寸 | 12×12px | DSL 22:12503-12507 |
| 数量 | 5 | DSL 组合 1344 |
| 激活态填充 | #f7ce00 | DSL Selection/Rating/Phone/Star_activited |
| 未激活填充 | rgba(0, 0, 0, 0.102) | DSL Star_enabled |

### 精选徽章

| 参数 | 值 | 来源 |
|------|-----|------|
| 尺寸 | 28×16px | DSL 22:12511 |
| 圆角 | 4px | DSL cornerRadius |
| 背景色 | rgba(199, 158, 99, 0.2) | DSL fillPaints + opacity |
| 文字色 | #806540 | DSL 22:12512 |

### 图片

| 参数 | 值 | 来源 |
|------|-----|------|
| 尺寸 | 48×48px | DSL 22:12517-12519 |
| 圆角 | 8px | DSL cornerRadius |
| 间距 | 8px | 推算式：(160−48×3)/2 |
| 最大数量 | 3 | DSL 组合 1343 |

### 字体

| 元素 | 字体族 | 字号 | 字重 | 行高 | 颜色 | 来源 |
|------|--------|------|------|------|------|------|
| 用户名 | HarmonyHeiTi | 14px | 400 | 14px (1.0) | `--harmony-font-primary` | DSL 22:12500 |
| 评分描述 | HarmonyHeiTi | 10px | 400 | 14px | `--harmony-font-tertiary` | DSL 22:12509 |
| 来源 | HarmonyHeiTi | 10px | 400 | 14px | `--harmony-font-tertiary` | DSL 22:12513 |
| 评论正文 | HarmonyHeiTi | 14px | 400 | 19px (~1.357) | `--harmony-font-primary` | DSL 22:12515 |
| 日期 | HarmonyHeiTi | 10px | 400 | 14px | `--harmony-font-tertiary` | DSL 22:12522 |
| 徽章文字 | HarmonyOS Sans SC | 10px | 400 | 12px | #806540 | DSL 22:12512 |

### 间距

| 关系 | 值 | 来源 |
|------|-----|------|
| 头像→名字 | 12px | DSL left 差值 |
| 名字→星级行 | 5px | DSL top 差值 |
| 星级→评分文案 | 4px | 衡量 |
| Header→正文 | 8px | DSL top 56 − header底 48 |
| 正文→图片 | 12px | DSL top 106 − body底 94 |
| 图片→底部 | 4px | DSL top 158 − images底 154 |

## 状态与交互

- 本组件为展示型卡片，无交互状态切换
- 图片区域无图片时不渲染

## Props

| Prop | 类型 | 默认值 | DSL 节点 | 说明 |
|------|------|--------|----------|------|
| `头像` | `string` | `undefined` | 22:12499/22:12514 | 头像图片URL |
| `用户名` | `string` | `"大众点评网友"` | 22:12500 | 用户名称 |
| `评分` | `1 \| 2 \| 3 \| 4 \| 5` | `5` | 22:12502-12507 | 星级评分 1-5 |
| `评分描述` | `string` | `"很不错"` | 22:12509 | 评分描述文案 |
| `精选` | `boolean` | `true` | 22:12510 | 是否显示精选徽章 |
| `来源` | `string` | `"来自大众点评"` | 22:12513 | 来源文案 |
| `评论内容` | `string` | `"谁能想到这是奈雪啊..."` | 22:12515 | 评论正文 |
| `图片列表` | `string[]` | `[]` | 22:12517-12519 | 图片URL列表(最多3张) |
| `日期` | `string` | `"2024/3/2"` | 22:12522 | 日期文案 |

### DSL ↔ Prop 对照

| DSL 字段路径 | Prop 名 | 取值是否一致 | 备注 |
|-------------|---------|-------------|------|
| `22:12499` app/40 image fill | `头像` | 是 | 类型为 string (URL) |
| `22:12500` characters | `用户名` | 是 | 默认值与 DSL 一致 |
| `22:12502-12507` 星级图标 | `评分` | 是 | 枚举 1-5，与 DSL 激活态一致 |
| `22:12509` characters | `评分描述` | 是 | 默认值与 DSL 一致 |
| `22:12510` visible | `精选` | 是 | 布尔控制显示/隐藏 |
| `22:12513` characters | `来源` | 是 | 默认值与 DSL 一致 |
| `22:12515` characters | `评论内容` | 是 | 默认值与 DSL 一致 |
| `22:12517-12519` image fill | `图片列表` | 是 | 最多 3 项 |
| `22:12522` characters | `日期` | 是 | 默认值与 DSL 一致 |

## 样式引用

### 使用的全局 Token

| Token | 用途 |
|-------|------|
| `--harmony-comp-background-primary` | 卡片背景 |
| `--harmony-font-primary` | 用户名、评论正文颜色 |
| `--harmony-font-tertiary` | 评分描述、来源、日期颜色 |
| `--harmony-comp-background-secondary` | 头像占位背景 |
| `--harmony-icon-secondary` | 底部 icon 颜色 |

### 组件专属 Token（CSS 变量，未写入 global.css）

| 变量 | 值 | 说明 |
|------|-----|------|
| `--rcd-star-active` | `#f7ce00` | 激活星星颜色 |
| `--rcd-star-inactive` | `rgba(0,0,0,0.102)` | 未激活星星颜色 |
| `--rcd-badge-bg` | `rgba(199,158,99,0.2)` | 精选徽章背景 |
| `--rcd-badge-text` | `#806540` | 精选徽章文字色 |

> 这些色值属于本组件专属语义（星星/徽章），与现有全局 Token 无直接等价映射，保留为组件级 CSS 变量。若未来有多组件共用星星/徽章模式，可提炼为全局 Token。

## 取舍说明

1. **design_to_code 资源过期**：`Invalid batch timestamp`，已按 MCP 故障矩阵降级，以 DSL + 截图为主要真值，不做 `design_to_code` 依赖。
2. **get_variants 返回空**：节点 22:12494 为 Frame 而非 ComponentSet，无变体属性。Props 从 DSL 静态内容的可配置维度提取。
3. **星星不复用 RatingPhone**：RatingPhone 使用 28×28 星星，本卡片使用 12×12 星星，尺寸不兼容。直接内联 12px SVG 以保持 1:1 还原。
4. **行高推算**：DSL 评论正文高度 38px/2 行≈19px/行，设定 `line-height: 19px`；DSL 中 10px 文字高度为 14px（如日期、来源），设定 `line-height: 14px`。
