# ProgressBarLoading — 环形加载指示器

## Metadata

| 字段 | 值 |
|------|-----|
| 实现目录 | `src/components/ProgressBarLoading/` |
| Stories 路径 | `src/components/ProgressBarLoading/progress-bar-loading.stories.tsx` |
| Pixso 链接 | `https://pixso.cn/app/design/HA_e8I2mE7Oa0b5ZoeokSA?item-id=5318:20130` |
| MCP 工具来源 | `get_node_dsl`（5318:20130）、`design_to_code`、`get_export_image` |
| 变体树 JSON | `src/components/ProgressBarLoading/progress-bar-loading.json` |
| JSON 生成方式 | 基于 `get_node_dsl` 的 `pixComponentTreeDslNodes` 重建 |

## 组成与用途

- **导出项**：`ProgressBarLoading` 组件、`ProgressBarLoadingProps` 类型、`ProgressBarLoadingSize` 类型、`progressBarLoadingSizes` 常量
- **使用场景**：页面/区块加载中状态，环形 indeterminate spinner，适用于按钮、卡片、列表项等需要表明"正在加载"的场景

## 动画机制

与 Button `LoadingGlyph` 同款的 `useSpinnerProgress`（rAF 驱动）控制旋转：

| 参数 | 值 |
|------|-----|
| 驱动方式 | `requestAnimationFrame`（JS 驱动，60fps），与 Button `useSpinnerProgress` 一致 |
| 循环周期 | 1150ms（prefers-reduced-motion 时 1800ms） |
| 视觉 | 部分弧环（75% 圆周 `stroke-dasharray`）+ 渐变拖尾 + rAF 平滑旋转 |
| 线帽 | `stroke-linecap: round`（圆形端头） |
| 起始角度 | -45°（`transform: rotate(-45 …)`） |
| 拖尾 | SVG `linearGradient`：icon_secondary → icon_tertiary → 透明 |

## 量化规格（从 Pixso DSL 提取）

### 尺寸变体

| 尺寸 | 容器 | SVG 显示尺寸 | 轨道环描边宽度 | 追逐点半径 |
|------|------|-------------|---------------|-----------|
| 24   | 24×24 | 24×24 | 2px | 2.25px |
| 32   | 32×32 | 32×32 | 2.5px | 3px |
| 40   | 40×40 | 40×40 | 3px | 3.75px |
| 72   | 72×72 | 72×72 | 4px | 6.75px |

> 轨道环描边宽度为 Pixso DSL 实测值，非等比公式计算。通过 `orbitStrokeWidthMap` 按尺寸显式映射。

> SVG viewBox 固定 24×24，所有坐标在 viewBox 空间内计算，通过 width/height 属性等比缩放到目标像素尺寸。

### 色值

| 视觉角色 | Harmony Token | 颜色值（light） |
|----------|---------------|-----------------|
| 轨道环 + 追逐点 | `--harmony-icon-secondary` | `rgba(0,0,0,0.6)` |

> SVG 使用 `fill="currentColor"` / `stroke="currentColor"`，颜色由容器 `color` 属性统一控制，继承自 `--harmony-icon-secondary`。

## 状态与交互

| 状态 | 行为 |
|------|------|
| default | 椭圆形轨道追逐点动画，1150ms 循环 |
| prefers-reduced-motion | 周期延长至 1800ms |

> 本组件为 indeterminate 加载指示器，无 hover/active/disabled 交互状态。

## Props（与 DSL 硬对齐）

| Prop | 类型 | 默认值 | DSL 来源 | 说明 |
|------|------|--------|----------|------|
| `尺寸` | `"24" \| "32" \| "40" \| "72"` | `"40"` | `get_node_dsl` 子节点名 `尺寸=24/32/40/72` | Pixso 原始属性名，4 个变体 |

### DSL ↔ Prop 对照

| DSL 字段/节点 | 实现 Prop | 可取值的集合 | 备注 |
|--------------|-----------|-------------|------|
| `pixComponentTreeDslNodes[].name` 中的 `尺寸=X` | `尺寸` | `"24"`, `"32"`, `"40"`, `"72"` | 直接使用 DSL 原始属性名，无命名映射 |

## 样式引用

### 使用到的全局 Token

| Token | 用途 |
|-------|------|
| `--harmony-icon-secondary` | 轨道环描边 + 追逐点填充颜色（通过 `color: var(--harmony-icon-secondary)` + `currentColor`） |

### 新增全局 Token

无。本组件全部复用已有 `global.css` Token，未新增全局变量。

## 取舍说明

| 项目 | 说明 |
|------|------|
| 动效方案 | CSS `stroke-dasharray` 部分弧环 + `linearGradient` 渐变拖尾 + CSS `@keyframes` 旋转，精确还原 Pixso DSL 中环形 + 端帽结构 |
| 无 Pixso 截图可用 | `get_screenshot` 返回不支持的格式，`get_export_image` 已下载但工具无法渲染。以 DSL + SVG asset + `design_to_code` 三源交叉验证还原 |
| `get_variants` 返回 `{}` | 变体树 JSON 基于 `get_node_dsl` 的 `pixComponentTreeDslNodes` 手动重建，完整覆盖所有 4 个实例节点 |
| DSL Boolean/椭圆形结构 | 原设计为静态环形 + 端帽结构；实现中使用环形弧线拖尾模型，避免 Button LoadingGlyph 的椭圆追逐点破坏 ProgressBarLoading 的环形语义 |
