# ranking-categories (RankingCategories)

## Metadata

| 属性 | 值 |
|------|------|
| 实现目录 | `src/blocks/ranking-categories/` |
| Stories 路径 | `src/blocks/ranking-categories/ranking-categories.stories.tsx` |
| 块区 JSON | `src/blocks/ranking-categories/ranking-categories.json` |
| Pixso 链接 | `https://pixso.cn/app/design/poNuihoilaLFIwHQwxIlcQ?item-id=45:277` |
| item-id | `45:277` |
| MCP 工具来源 | `get_node_dsl` + `get_screenshot` |

## 组分 JSON 变体树

- **路径**: `src/blocks/ranking-categories/ranking-categories.json`
- **MCP 调用**: `get_node_dsl` (guid: `45:277`)
- **get_variants**: 不可用 — 变体从 DSL component tree 重建
- **重建依据**: DSL 组件树展示 11 个分类项 — 1 个激活态（金色文字 + 麦穗图标 + 白色半透明背景 + 8px 圆角）和 10 个非激活态（40% 白色文字 + 透明背景）

## 组成与用途

**导出项**: `RankingCategories`, `RankingCategoriesItem`

**使用场景**: 深色主题排行榜多级分类侧边栏。竖排分类标签列表，激活态显示麦穗装饰图标 + 金色文字 + 白色半透明圆角背景，用于切换不同榜单分类（如传奇榜、古装榜、科幻榜等）。

组合区块，由以下元素拼装：
- 深色背景容器 (74px 宽, `#18181A`)
- 分类标签项 (74×56px per item)
- 麦穗图标 (24×60px，左侧翻转 180°)
- 金色激活文字 (Bold, 14px)

## 量化规格

### 整体尺寸
- 容器宽度: **74px**
- 容器高度: **由内容决定**（设计稿 11 项 = 56×11 + 10×10 = 716px，含垂直间距）

### 单个分类项

| 属性 | 值 | 备注 |
|------|------|------|
| 宽度 | 74px | 固定 |
| 高度 | 56px | 固定 |
| 内边距 | 10px 16px | 上下 10px，左右 16px |
| 项间距 | 10px | 垂直排列 gap |

### 布局坐标（激活态 74×56 item）

| 元素 | 尺寸 | 备注 |
|------|------|------|
| 激活框架 | 44×20px | 居中容器，含麦穗+文字 |
| 左麦穗图标 | 24×60px | 翻转 180°，opacity 0.5 |
| 右麦穗图标 | 24×60px | 正常朝向，opacity 0.7 |
| 金色标签文字 | auto×19px | 14px Bold，居中 |

### 圆角
- 激活态背景: **8px**

### 色值

| 角色 | CSS 值 | Token 映射 |
|------|--------|------------|
| 容器背景 | `#18181A` | `--rc-bg` (DSL fillPaints) |
| 普通文字 | rgba(255, 255, 255, 0.40) | `--rc-text` (DSL Dark/font_tertiary) |
| 激活态背景 | rgba(255, 255, 255, 0.10) | `--rc-active-bg` (DSL fillPaints 10% white) |
| 激活态金色文字 | rgba(228, 182, 119, 0.898) | `--harmony-chart-gold` (复用全局 token) |
| 麦穗图标色 | rgba(255, 233, 189, 1) | `--rc-wheat` (DSL 矢量 fillPaints) |
| hover 叠加 | rgba(255, 255, 255, 0.05) | `--rc-hover` |
| pressed 叠加 | rgba(255, 255, 255, 0.10) | `--rc-pressed` |

### 字体

| 元素 | 字体族 | 字重 | 字号 | 行高 | Token |
|------|--------|------|------|------|-------|
| 普通标签 | HarmonyHeiTi | Regular (400) | 14px | 19px | `--harmony-font-size-body-m` |
| 激活标签 | HarmonyHeiTi | Bold (700) | 14px | 19px | `--harmony-font-size-body-m` + font-weight:700 |
| 麦穗图标 | HM Symbol | Regular (400) | 18px | 1 | HM Symbol 字体 |

## 状态与交互

| 状态 | 触发条件 | 视觉效果 |
|------|----------|----------|
| Default | `激活=false` | 40% 白色文字，透明背景 |
| Active | `激活=true` | 金色 Bold 文字 + 左右麦穗图标 + 10% 白色圆角背景 (r=8px) |
| Hover (默认项) | 鼠标悬停 | 5% 白色背景叠加 |
| Hover (激活项) | 鼠标悬停 | 15% 白色背景叠加 |
| Pressed | 点击 | 10%/20% 白色背景叠加 |

## Props

### RankingCategoriesItem

| Prop | 类型 | 默认值 | DSL ↔ Prop | 说明 |
|------|------|--------|-------------|------|
| 标签 | `string` | — | `37:56489 → nodeText` | 分类标签文字 |
| 激活 | `boolean` | `false` | `37:56490 vs 37:56488` | 是否激活态 |

### RankingCategories

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| categories | `RankingCategoriesItem[]` | `[]` | 分类标签数据数组 |
| className | `string` | `""` | 外层容器类名 |

## 样式引用

### 使用 global.css 变量

- `--harmony-chart-gold`: 激活态金色文字（全库扩展，已在 `chart-categories` 中新增）

### 新增局部 Token（组件内 `:root` 定义）

| Token 名称 | Pixso 取值 | 适用范围 |
|------------|-----------|----------|
| `--rc-bg` | #18181A (r:24, g:24, b:26) | 深色背景（仅本组件） |
| `--rc-text` | rgba(255, 255, 255, 0.40) | 非激活标签文字 |
| `--rc-active-bg` | rgba(255, 255, 255, 0.10) | 激活态背景 |
| `--rc-wheat` | rgba(255, 233, 189, 1) | 麦穗图标色 |
| `--rc-hover` | rgba(255, 255, 255, 0.05) | hover 叠加 |
| `--rc-pressed` | rgba(255, 255, 255, 0.10) | pressed 叠加 |

## 取舍说明

- `get_variants` 不可用，变体树从 `get_node_dsl` (guid: `45:277`) 手动重建
- Pixso `design_to_code` 未执行（该节点非组件实例，为 FRAME 节点）
- 麦穗图标使用 HM Symbol Unicode 字符 `"󰀶"`，与 `chart-categories` 组件一致
- DSL `37:56491` 子节点布局：实例 40 (`37:56493`, left:0, 无旋转) = 左侧麦穗；实例 41 (`37:56517`, left:38, angle:180) = 右侧麦穗（翻转 180°）。实现：左侧无旋转，右侧 `transform: rotate(180deg)`，与 DSL 精确对齐。两实例同源 left-麦穗 COMPONENT (`2:66801`)，其内矢量已内置 opacity 0.5~0.7 渐变
- 暗色主题 Token 定义为组件局部变量（`:root` 中 `--rc-*`），因与该组件专属的深色背景色值与全局亮色主题不兼容
- `--rc-active-text` 复用全局 `--harmony-chart-gold` token，金色的色值在亮色/暗色下保持一致（设计稿中不随主题变化）
- 该组件为 `chart-categories`（榜单分类）的深色主题变体，命名 `ranking-categories`
