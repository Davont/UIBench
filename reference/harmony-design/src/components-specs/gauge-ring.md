# GaugeRing

## Metadata

- 实现目录：`src/components/GaugeRing/`
- Stories 路径：`src/components/GaugeRing/gauge-ring.stories.tsx`
- Pixso 链接：https://pixso.cn/app/design/HA_e8I2mE7Oa0b5ZoeokSA?item-id=5308:19271
- item-id：`5308:19271`
- 本轮渐变校准 Pixso 链接：https://pixso.cn/app/design/QeDttX-H4qVEUZXJjNfTCw?item-id=5395:1
- 本轮渐变校准 item-id：`5395:1`
- MCP 工具：`get_node_dsl`、`get_screenshot`、`get_variants`、`design_to_code`
- 本轮渐变校准工具：`get_node_dsl` + `test.txt` SVG 导出
- 变体树 JSON：`src/components/GaugeRing/gauge-ring.json`
  - `variantOptions` 来源于 DSL 实例命名解析：`类型=...,尺寸=...`
  - `pixTreeNodes` 记录 `5308:19271` 画板上的 15 个变体实例节点

## 组成与用途

- 导出项：`GaugeRing`、`GaugeRingProps`、`gaugeRingTypes`、`gaugeRingSizes`
- 适用场景：AQI、恢复值、运动进度、双值对照等半开口仪表盘

## 量化规格

- 尺寸档位
  - `Large`：`288 × 288`，主弧半径 `118px`，描边 `18px`
  - `Small`：`136 × 136`，主弧半径 `60px`，描边 `10px`
  - `Mini`：`88 × 88`，主弧半径 `38px`，描边 `8px`
- 主弧几何
  - 统一采用半开口上拱弧，起止角为约 `228° → 492°`
  - Default 使用红橙黄绿渐变；Large / Small 的 Line 使用绿黄橙红渐变；Mini Line 与 Default Mini 一致
  - Double Data 使用红色主弧 + 浅粉尾段
  - Progress 使用荧光绿色主弧 + 浅绿尾段
  - Multi Segment 使用蓝、青、绿、黄、橙、红多段离散弧，顺时针从左下蓝段起排布到右下红段
  - Multi Segment 默认渲染不再用百分比切割统一圆弧：Large 直接使用 `test.txt` 导出的 7 条填充 path + 7 条高光 path；Small / Mini 按 DSL 中 `136 × 136`、`88 × 88` 与 Large 的同构缩放关系渲染同一组真实 path
  - Multi Segment 默认黑色箭头使用 `test.txt` SVG 中 `.arrow small` 的两条 path 与原始 transform，位置落在第三段末尾，并随尺寸等比缩放
  - Multi Segment 渐变 stop 对齐 `5395:1` DSL 与 `test.txt` SVG：蓝/青段为亮色透明端到纯色端；绿/黄/橙/红段保留设计稿中间透明度 stop 与尾部透明 stop
- Typography
  - Large Default 主值：`56/72`，副文案：`16/24`
  - Large 其余类型主值：`80/108`
  - Small Default：`48/64`
  - Small Line：`36/64`
  - Mini 主值：`30/40`
  - Large 底部 `AQI`：`30/40`
  - Large 双值：`48/64`

## 状态与交互

- `Default`：渐变弧 + 左上箭头 + 主值 + 中心副文案/底部标签
- `Line`：渐变弧 + 左上箭头 + 主值 + 底部双值；Large / Small 与 Mini 的渐变方向不同
- `Double Data`：红色弧 + 底部双值
- `Progress`：绿色弧 + 跑步图标
- `Multi Segment`：多段彩色弧 + 右上箭头 + 底部标签

组件为纯展示，无 hover / active / disabled 交互状态。

## Props

| Prop | 类型 | 默认值来源 | 说明 |
|------|------|------------|------|
| `类型` | `"Default" \| "Line" \| "Double Data" \| "Multi Segment" \| "Progress"` | Pixso variant | 组件变体 |
| `尺寸` | `"Large" \| "Small" \| "Mini"` | Pixso variant | 组件尺寸 |
| `数值` | `string \| number` | 各实例中心文案 | 中心主值 |
| `标签` | `string` | 默认 / Multi Segment / Mini 的底部文案 | 底部单行标签 |
| `说明` | `string` | Large Default 中心副文案 | 中心说明文字 |
| `左值` | `string \| number` | Line / Double Data 默认左值 | 底部左侧值 |
| `右值` | `string \| number` | Line / Double Data 默认右值 | 底部右侧值 |
| `进度` | `number` | Progress / Double Data 默认弧长 | 弧线填充比例 |
| `分段` | `GaugeRingSegment[]` | Multi Segment 默认分段 | 自定义多段配色 |

### DSL ↔ Prop 对照

| DSL 字段/来源 | 最终 Prop | 备注 |
|---------------|-----------|------|
| `类型` | `类型` | 直接对齐 DSL variant |
| `尺寸` | `尺寸` | 直接对齐 DSL variant |
| 实例默认文本覆盖 | `数值` / `标签` / `说明` / `左值` / `右值` | 作为文案覆盖能力暴露 |
| 设计弧长比例 | `进度` | DSL 未单独命名，按截图量化为默认值 |
| 多段彩环路径拆分 | `分段` | 从截图与 codegen 颜色段重建 |

## 样式引用

- 使用全局 token
  - `--harmony-font-primary`
  - `--harmony-font-secondary`
- 未新增 `global.css` token
  - 渐变色、多段色和尾段色保留在组件内部，避免污染全局主题
  - Matrix story 使用白色 `772 × 1732` 画板，并复用 Pixso 中每个实例的 `left/top` 坐标做绝对排布
  - Multi Segment 默认 path / gradient / arrow 表来自 `5395:1` DSL 与 SVG：Large 使用 SVG 中 `paint_linear_0` 至 `paint_linear_13`、对应 path 以及 `.arrow small` path；Small/Mini 使用 DSL 尺寸关系等比缩放，避免旧实现的分段占比和箭头定位误差

## 取舍说明

- `get_variants` 返回空对象，因此变体集合由 `get_node_dsl` 的实例命名与子节点坐标重建。
- Pixso 中部分弧线由位图/矢量混合导出；Default / Line / Double Data / Progress 仍使用统一 SVG 弧线路径。Multi Segment 默认态改为真实导出 path 渲染，只有显式传入 `分段` 自定义数据时才回退到百分比分段算法。
- Large / Small 的 `Line` 渐变方向与 `Default` 不同，组件内按尺寸分支处理；`Multi Segment` 默认色段顺序也已按新稿重排。
- 自动 SSIM 对比依赖已可用，Matrix story 会作为 Storybook 与 Pixso 画板的视觉比对入口。
