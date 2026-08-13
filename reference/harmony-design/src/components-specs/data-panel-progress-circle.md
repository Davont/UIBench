# DataPanelProgressCircle 组件规格

## Metadata

| 字段 | 值 |
|------|------|
| 实现目录 | `src/components/DataPanelProgressCircle/` |
| Stories 路径 | `src/components/DataPanelProgressCircle/data-panel-progress-circle.stories.tsx` |
| Pixso 链接 | [DataPanelProgressCircle](https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5413:34) |
| item-id | `5413:34` |
| MCP 工具来源 | `get_node_dsl`, `get_screenshot` |

## 组件变体树 JSON

**文件路径：** `src/components/DataPanelProgressCircle/data-panel-progress-circle.json`

**生成方式：** 基于 `get_node_dsl` 中 `pixComponentTreeDslNodes` 节点结构重建（`get_variants` 返回空对象 `{}`）

**变体维度：**
- 尺寸：`Large` | `Medium` | `Small`

## 组成与用途

**导出项：**
- `DataPanelProgressCircle` - 主组件
- `dpProgressCircleSizes` - 尺寸选项枚举常量
- `DataPanelProgressCircleProps` - Props 类型
- `DpProgressCircleSize` - 尺寸联合类型
- `dpProgressCircleSizeMap` / `dpProgressCircleRadiusMap` / `dpProgressCircleStrokeMap` 等 - 尺寸映射常量

**使用场景：**
- Dashboard 数据面板环形进度展示
- 系统版本/存储/电量等环形指标
- 需要渐变进度弧线的数据可视化

## 量化规格

### 尺寸
| 尺寸 | 容器 | 轨道圆半径 (中心线) | 描边宽度 | 值字号 | 值行高 |
|------|------|---------------------|----------|--------|--------|
| Large | 288×288 | 114px | 24px | 56px | 74px |
| Medium | 136×136 | 55px | 18px | 36px | 48px |
| Small | 88×88 | 35px | 14px | — | — |

### 色值
| 元素 | 色值 | 变量引用 |
|------|------|----------|
| 轨道圆 (灰色背景圈) | rgba(0,0,0,0.047) | `--harmony-comp-background-tertiary` |
| 进度弧线起始色 | #86C1FF | 渐变起点（无现有 token 对应） |
| 进度弧线结束色 | #254FF7 | 渐变终点（无现有 token 对应） |
| 投影弧线模糊 | blur(13.59px) | Large 专属，opacity 0.4 |
| 数值文字 | rgba(0,0,0,0.898) | `--harmony-font-primary` |
| 百分号/版本 | rgba(0,0,0,0.6) | `--harmony-font-secondary` |

### 字体
| 元素 | fontFamily | fontWeight | 说明 |
|------|------------|------------|------|
| 数值 | HarmonyHeiTi | 500 (Medium) | 与 DSL 一致 |
| 百分号 | HarmonyHeiTi | 500 (Medium) | 与 DSL 一致 |
| 版本号 | HarmonyHeiTi | 500 (Medium) | 与 DSL 一致 |

## 状态与交互

| 状态 | 表现 |
|------|------|
| Default | 显示对应尺寸的环形进度，渐变蓝色弧线 + 灰色轨道 |
| Large | 额外显示投影模糊弧线（FOREGROUND_BLUR radius=13.59） + 版本号文本 |
| Medium | 显示数值 + 百分号 |
| Small | 仅显示环形进度，无文本 |

## Props

```typescript
interface DataPanelProgressCircleProps extends HTMLAttributes<HTMLDivElement> {
  尺寸?: DpProgressCircleSize  // 默认："Large"，可选 "Large" | "Medium" | "Small"
  进度?: number                // 默认：30，进度百分比 0-100
  版本?: string                // 默认："1.0.0"，仅 Large 尺寸显示
}
```

### DSL ↔ Prop 对照

| DSL 属性 | Prop 名 | 取值集合 | 说明 |
|----------|---------|----------|------|
| 尺寸 (componentNormName) | 尺寸 | "Large", "Medium", "Small" | 与 DSL 三种组件实例名一致 |
| value (nodeText) | 进度 | 0-100 | DSL 中 Large=30, Medium=50 |
| Text/version (nodeText) | 版本 | string | DSL 中 Large="1.0.0" |

**命名说明：** `尺寸`、`进度`、`版本` 均为中文 Prop 名，与 DSL 属性语义直接对应，无命名映射。

## 样式引用

### 使用的 global.css 变量
| 变量名 | 用途 | 来源 |
|--------|------|------|
| `--harmony-comp-background-tertiary` | 轨道圆背景色 | 现有 token |
| `--harmony-font-primary` | 数值文字色 | 现有 token |
| `--harmony-font-secondary` | 百分号/版本文字色 | 现有 token |

### 新增 Token
无新增全局 Token。渐变弧线色值 `#86C1FF` → `#254FF7` 在 SVG `<linearGradient>` 中直接定义，不写入 `global.css`。投影模糊值 13.59px 通过 CSS 自定义属性 `--dp-shadow-blur` 在组件内传递。

## 取舍说明

| 项目 | 说明 |
|------|------|
| 布局方案 | 容器 `position: relative` + SVG `position: absolute` 覆盖，文字内容 `position: absolute` 居中叠放 |
| 进度弧线实现 | 使用 SVG `<circle>` + `stroke-dasharray` / `stroke-dashoffset`，旋转 -90° 使起点在 12 点钟方向 |
| 渐变方向 | SVG linearGradient x1=0 y1=1 x2=1 y2=0（左下→右上），对应 DSL 中 gradient transform 的近似方向 |
| 投影弧线 | Large 独占，使用相同 circle + `filter: blur(13.59px)` + `opacity: 0.4`，对应 DSL FOREGROUND_BLUR |
| 字号行高 | 使用 CSS 自定义属性动态传递，避免为每种尺寸创建独立 CSS 规则 |
| Small 无文本 | 与 DSL 一致：Small 变体无 value/Text 子节点 |
| DSL 中 % 符号 | 作为独立 Text 节点，实现为组件内部固定渲染 |
| strokeLinecap | 使用 `round`，对应 DSL strokeJoin=ROUND（Large） |
| get_variants | 返回空对象 `{}`，变体树基于 `get_node_dsl` 中 `pixComponentTreeDslNodes` 重建 |
| design_to_code | CSS/TSX URL 返回 Invalid URL（批次缓存过期），按 DSL + 截图手工还原 |

## 1:1 还原验证

**验证方式：** 人工对照截图 + DSL 数据交叉验证

**对照结论：**
- ✅ 三种尺寸容器 (288/136/88) 与 DSL 一致
- ✅ 轨道圆半径 (114/55/35) 由 DSL ellipse 尺寸减 strokeWeight 计算得出
- ✅ 描边宽度 (24/18/14) 与 DSL strokeWeight 一致
- ✅ 渐变起止色 #86C1FF → #254FF7 与 DSL gradient stops 一致
- ✅ 数值字号 (56/36) 与 DSL fontSize 一致
- ✅ 数值行高 (74/48) 与 DSL lineHeightNumber 一致
- ✅ Large 投影模糊 13.59px 与 DSL FOREGROUND_BLUR radius 一致
- ✅ 轨道色 rgba(0,0,0,0.047) 与 DSL 一致
- ✅ 字体 HarmonyHeiTi Medium 与 DSL 一致
- ✅ Small 无文字与 DSL 一致

**未执行自动 SSIM**，对照方式为人工复核 + DSL 数据交叉验证。
