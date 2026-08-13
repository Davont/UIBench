# GaugeStripGauge

## Metadata

- 实现目录：`src/components/GaugeStripGauge/`
- Stories 路径：`src/components/GaugeStripGauge/gauge-strip-gauge.stories.tsx`
- Pixso 链接：https://pixso.cn/app/design/HA_e8I2mE7Oa0b5ZoeokSA?item-id=5308:19500
- item-id：`5308:19500`
- MCP 工具：`get_node_dsl`、`get_screenshot`、`get_export_image`、`get_variants`、`design_to_code`
- 变体树 JSON：`src/components/GaugeStripGauge/gauge-strip-gauge.json`
  - `variantOptions` 来源于 `get_node_dsl` 的 `pixComponentTreeDslNodes` 实例命名解析：`类型=...,尺寸=...,vertical=...`
  - `pixTreeNodes` 记录 27 个变体实例节点
  - `get_variants` 返回 `{}`，变体集合由 DSL 实例命名重建

## 组成与用途

- 导出项：`GaugeStripGauge`、`GaugeStripGaugeProps`、`gaugeStripGaugeTypes`、`gaugeStripGaugeSizes`
- 适用场景：温度计、容量条、健康指标、存储空间、下载进度等线性仪表盘

## 量化规格

### 尺寸档位（水平 vertical=OFF）

| 尺寸 | 标准 W×H | Track W×H | Font Size | Gap | 圆角 |
|------|----------|-----------|-----------|-----|------|
| Small | 128×20 | 80×6 | 12 | 8 | 6 |
| Medium | 170×24 | 118×8 | 14 | 8 | 6 |
| Large | 214×26 | 158×10 | 16 | 8 | 6 |

Percentage 高度：
| 尺寸 | W×H | Track W×H | Bottom Font |
|------|-----|-----------|-------------|
| Small | 128×24 | 128×6 | 10 |
| Medium | 170×30 | 170×8 | 10 |
| Large | 214×37 | 214×10 | 14 |

### 尺寸档位（垂直 vertical=ON）

| 尺寸 | W×H | Track W×H | Font Size |
|------|-----|-----------|-----------|
| Small | 36×226 | 6×178 | 12 |
| Medium | 36×226 | 8×178 | 14 |
| Large | 36×226 | 10×168 | 16 |

### 颜色方案

**Pure Color:**
- 填充：`rgba(232, 64, 38, 1)` (红色)

**Progress:**
- 背景：`rgba(70, 177, 227, 0.3)` (浅蓝)
- 填充：`rgba(70, 177, 227, 1)` (蓝色)

**Double Progress:**
- 渐变填充：`rgba(182,228,103,1)` → `rgba(247,187,28,1)` (绿→黄)

**Multi Color / Percentage（7段光谱）:**
1. `rgba(70,177,227,1)` → `rgba(181,223,243,1)` (蓝)
2. `rgba(97,207,190,1)` → `rgba(191,235,229,1)` (青)
3. `rgba(193,227,189,1)` → `rgba(100,187,92,1)` (绿)
4. `rgba(165,214,29,1)` → `rgba(199,231,110,1)` (黄绿)
5. `rgba(247,206,0,1)` → `rgba(251,235,153,1)` (黄)
6. `rgba(249,160,30,1)` → `rgba(252,217,165,1)` (橙)
7. `rgba(245,116,78,1)` → `rgba(232,64,38,1)` (红)

**轨道背景:**
- `--harmony-comp-background-secondary`: `rgba(0, 0, 0, 0.098)`

**文本颜色:**
- 刻度值：`--harmony-font-primary`：`rgba(0, 0, 0, 0.898)`
- 百分比副文本：`--harmony-font-secondary`：`rgba(0, 0, 0, 0.6)`

### Typography

- 字体：HarmonyHeiTi Medium (500)
- Small: 12px, Medium: 14px, Large: 16px（刻度值）
- 箭头标记值：12px (Small/Medium), 14px (Large)
- Percentage 底部：10px (Small/Medium), 14px (Large)

## 状态与交互

- `Pure Color`：纯色条 + 箭头标记 + 当前值
- `Multi Color`：多段彩色条 + 箭头标记 + 当前值
- `Progress`：浅色底 + 纯色填充条（进度百分比）+ 起止值
- `Double Progress`：浅色底 + 渐变填充条（进度百分比）+ 起止值
- `Percentage`：多段光谱条 + 底部标签/值文本行

组件为纯展示，无 hover / active / disabled 交互状态。

## Props

| Prop | 类型 | 默认值来源 | 说明 |
|------|------|------------|------|
| `类型` | `"Pure Color" \| "Multi Color" \| "Progress" \| "Double Progress" \| "Percentage"` | Pixso variant | 组件变体 |
| `尺寸` | `"Small" \| "Medium" \| "Large"` | Pixso variant | 组件尺寸 |
| `vertical` | `boolean` | `false` (OFF) | 方向：true=垂直, false=水平 |
| `起始值` | `string` | 各实例默认文案 | 起始刻度值 |
| `结束值` | `string` | 各实例默认文案 | 结束刻度值 |
| `当前值` | `string` | Pure/Multi 默认 "26" | 箭头指示的当前值 |
| `进度` | `number` (0–100) | 各类型默认 | 填充百分比 |
| `标签` | `string` | Percentage 默认 "Phone" | Percentage 底部右侧标签 |
| `值文本` | `string` | Percentage 默认 "123GB/500GB" | Percentage 底部左侧值文本 |

### DSL ↔ Prop 对照

| DSL 字段/来源 | 最终 Prop | 备注 |
|---------------|-----------|------|
| `类型` (variant) | `类型` | 直接对齐 DSL variant |
| `尺寸` (variant) | `尺寸` | 直接对齐 DSL variant |
| `vertical` (variant) | `vertical` | ON=true, OFF=false |
| `visible_31_5` "index" | `起始值` | 起始刻度文字 |
| `visible_31_7` "Value" | `结束值` | 结束刻度文字 |
| 箭头位置文字 | `当前值` | Pure/Multi Color 箭头文本 |
| `visible_31_6` "present value" | `进度` | 填充百分比控制 |
| Percentage 底部文字 | `标签` / `值文本` | 底部信息行 |

## 样式引用

- 使用全局 token
  - `--harmony-font-primary`：刻度值、标签文字色
  - `--harmony-font-secondary`：百分比副文字色
  - `--harmony-comp-background-secondary`：轨道背景色
- 组件内自定义 CSS 变量
  - `--hm-strip-gauge-gap`：元素间距
  - `--hm-strip-gauge-track-width`：垂直方向轨道宽度
  - `--hm-strip-gauge-track-radius`：轨道圆角
  - `--hm-strip-gauge-track-bg`：轨道背景色
- 未新增 `global.css` token
  - 渐变色和段彩色保留在组件内部，避免污染全局主题

## 取舍说明

- `get_variants` 返回空对象 `{}`，变体集合由 `get_node_dsl` 的 `pixComponentTreeDslNodes` 命名重建。
- `get_screenshot` 返回图片在终端无法直接查看；视觉对照基于 DSL 量化参数手工复核。
- Percentage 类型的七段光谱宽度比例从 Large 尺寸 DSL 提取，统一应用于所有尺寸。
- 垂直尺寸的 Medium track 厚度 (8px) 通过 Small (6px) 和 Large (10px) 插值得到。
- 未执行自动 SSIM 视觉回归对比（脚本依赖的 `pngjs` 未安装），对照方式为人工复核 + 关键尺寸复算。
