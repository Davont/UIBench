# DataPanelLoading

## Metadata

| 字段 | 值 |
|------|-----|
| 实现目录 | `src/components/DataPanelLoading/` |
| Stories 路径 | `src/components/DataPanelLoading/DataPanelLoading.stories.tsx` |
| Pixso 链接 | https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5413:78 |
| item-id | `5413:78` |
| MCP 工具 | `get_node_dsl`, `get_screenshot` |
| 变体树 JSON | `src/components/DataPanelLoading/DataPanelLoading.json` |
| JSON 数据来源 | `get_node_dsl`（`get_variants` 返回空，从 DSL `pixTreeNodes` 子节点 `尺寸=Small/Medium/Large` 重建） |

## 组成与用途

环形进度指示器组件，用于数据面板加载场景。提供 Small / Medium / Large 三种尺寸变体。

- **导出项**: `DataPanelLoading`（组件）、`DataPanelLoadingProps`（类型）
- **使用场景**: 数据面板、下载进度、系统更新进度等环形进度展示

## 量化规格

### 尺寸与圆环参数

| 属性 | Small | Medium | Large |
|------|-------|--------|-------|
| 容器尺寸 | 88×88 | 136×136 | 288×288 |
| 灰色轨道圆直径 | 84 | 128 | 252 |
| 轨道描边宽度 | 14 | 18 | 24 |
| 蓝色进度弧描边宽度 | 14 | 18 | 24 |
| SVG track 半径 (r) | 35 | 55 | 114 |

### 颜色

| 用途 | 色值 | 全局 Token |
|------|------|-----------|
| 灰色轨道圆 | `rgba(0,0,0,0.047059)` | `--harmony-comp-background-tertiary` |
| 蓝色进度弧（起点） | `rgba(134,193,255,0)` | 组件内 SVG gradient |
| 蓝色进度弧（终点） | `rgba(37,79,247,1)` | 组件内 SVG gradient |
| 主文本（数值/Logo） | `rgba(0,0,0,0.898039)` | `--harmony-font-primary` |
| 次要文本（%/版本号） | `rgba(0,0,0,0.6)` | `--harmony-font-secondary` |
| 容器背景 | transparent | 无（由父级控制） |

### 字体

| 用途 | 字号 | 字重 | 行高 | 字体 |
|------|------|------|------|------|
| Medium 进度数值 | 36px | 500 (Medium) | 48px | HarmonyHeiTi |
| Medium "%" 后缀 | 16px | 500 (Medium) | 21px | HarmonyHeiTi |
| Large Logo "HarmonyOS" | 20px | 500 (Medium) | 30px | HarmonyHeiTi |
| Large 版本号 | 16px | 500 (Medium) | 21px | HarmonyHeiTi |

> 注：Logo "HarmonyOS" 在 Pixso DSL 中为 VECTOR 图形（`guid:1:12744, svgSha:HarmonyOS.svg`），当前实现以文字渲染（fallback），字号 20px，未与原始矢量图形像素级对齐。

### 布局

- Small：仅圆环，无中心内容
- Medium：圆环 + 中心百分比（数值 + "%" 后缀，上下排列）
- Large：圆环 + 中心 Logo + 版本号（上下排列）

## 状态与交互

- **Default**: 静态环形进度展示，无交互状态
- 进度通过 `进度` prop (0–100) 控制弧线长度
- 弧线过渡动画：`stroke-dashoffset` transition 0.3s ease

## Props

| Prop | 类型 | 默认值 | 说明 | DSL 来源 |
|------|------|--------|------|----------|
| `尺寸` | `"Small" \| "Medium" \| "Large"` | `"Large"` | 尺寸变体 | DSL 子节点 `尺寸=Small/Medium/Large` |
| `进度` | `number` | `50` | 进度百分比 0–100 | DSL Medium 实例 value 节点默认 "50" |
| `版本` | `string` | `"5.0.0"` | 版本号（Large 显示） | DSL Large 实例 Text 节点 "5.0.0" |
| `className` | `string` | - | 额外 CSS 类名 | 标准 React |
| `style` | `CSSProperties` | - | 额外内联样式 | 标准 React |

### DSL ↔ Prop 对照

| DSL 字段/路径 | Prop 名 | 取值 | 说明 |
|---------------|---------|------|------|
| 子节点 `name="尺寸=Small"` | `尺寸` | `"Small"` | 直接映射 |
| 子节点 `name="尺寸=Medium"` | `尺寸` | `"Medium"` | 直接映射 |
| 子节点 `name="尺寸=Large"` | `尺寸` | `"Large"` | 直接映射 |
| Medium > value nodeText="50" | `进度` | number | DSL 默认值 50 |
| Large > Text nodeText="5.0.0" | `版本` | string | DSL 默认值 "5.0.0" |

## 样式引用

### 使用的全局 Token

| Token | 用途 |
|-------|------|
| `--harmony-comp-background-tertiary` | 灰色轨道圆颜色 |
| `--harmony-font-primary` | Logo 文字色、进度数值色 |
| `--harmony-font-secondary` | "%" 后缀、版本号文字色 |

### 组件内定义

| 样式 | 说明 |
|------|------|
| SVG `<linearGradient>` | 蓝色进度弧渐变：`rgba(134,193,255,0)` → `rgba(37,79,247,1)`（对角方向） |

### 新增全局 Token

无。组件所需色值已全部映射到现有 `global.css` Token。蓝色渐变定义在组件 SVG 内部，属于图形资源而非全局样式 Token。

## 取舍说明

1. **HarmonyOS Logo**: Pixso DSL 中为 SVG 矢量图形（`svgSha: "HarmonyOS.svg"`），当前 `design_to_code` 临时资源 URL 已过期无法获取。以文本 "HarmonyOS" 渲染（字号 20px/Max 500/#898 black），与原始矢量图形的字号、字间距可能存在差异。后续获取原始 SVG 后可替换。
2. **Dark 模式**: 组件使用语义 Token（`--harmony-font-primary`、`--harmony-font-secondary`、`--harmony-comp-background-tertiary`），已通过 `global.css` 的 `.dark` 规则自动适配暗色模式。
3. **动画**: Pixso DSL 为静态设计稿，未定义旋转动画。组件仅实现进度弧线过渡动画（0.3s ease）。
4. **Small 变体无中心内容**: 与 DSL 一致，Small 尺寸仅显示圆环。
