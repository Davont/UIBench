# PatternLock — 图案锁屏组件

## Metadata

| 项目 | 值 |
|------|-----|
| 组件名 | PatternLock |
| 实现目录 | `src/components/Input/PatternLock/` |
| Stories 路径 | `src/components/Input/PatternLock/pattern-lock.stories.tsx` |
| Pixso 链接 | https://pixso.cn/app/design/d0WMuB0Im216ZfRVW4uwyQ?item-id=40:35507 |
| item-id | 40:35507 |
| 变体树 JSON | `src/components/Input/PatternLock/pattern-lock.json` |

## 组成与用途

3×3 九宫格图案锁屏组件。用户通过手指滑动在 9 个点之间绘制图案，用于解锁/验证。

**导出项:**
- `PatternLock` — React 组件
- `PatternLockProps` — Props 类型

## 量化规格

### 尺寸

| 属性 | 值 | 来源 |
|------|-----|------|
| 组件尺寸 | 210 × 210 px | DSL `5314:20143` → `PatternLock-Phone` 尺寸 |
| 外层圆直径 | 18 px | SVG: `rx="9"` → 圆形直径 18 |
| 外层圆半径 | 9 px | 同上 |
| 内层圆半径 | 7 px | SVG: `<circle r="7">` |
| 连线宽度 | 4 px | SVG path 计算 |
| 触摸热区半径 | 36 px | 2× 外层直径，保证手指操作体验 |

### 网格坐标（相对 210×210 组件）

点索引 0–8，对应位置：

| 索引 | 中心坐标 | 说明 |
|------|---------|------|
| 0 | (9, 9) | 左上 |
| 1 | (105, 9) | 上中 |
| 2 | (201, 9) | 右上 |
| 3 | (9, 105) | 左中 |
| 4 | (105, 105) | 正中 |
| 5 | (201, 105) | 右中 |
| 6 | (9, 201) | 左下 |
| 7 | (105, 201) | 下中 |
| 8 | (201, 201) | 右下 |

网格间距：96 px（水平/垂直一致）

### 颜色

| 属性 | 颜色值 | 来源 |
|------|--------|------|
| 外层圆（选中/错误/ON） | Light: `rgba(0,0,0,0.2)` (icon-fourth)；Dark: `#BFBFBF` 100% | Pixso 40:35507 / Dark 视觉修正 |
| 外层圆（默认/OFF） | `opacity: 0` 不可见 | Pixso 40:35507 |
| 内层圆（默认） | `rgba(0,0,0,0.898)` (icon-primary) | Pixso 40:35507, Light/icon_primary |
| 内层圆（选中） | `#0A59F7` 品牌蓝 | Pixso 40:35507 |
| 内层圆（错误） | `#E84026` | 设计约定 |
| 连线填充（所有态） | `rgba(0,0,0,0.2)` (icon-fourth) 灰色 | Pixso 40:35507 |

### 字体

无文字元素（纯图形组件）。

## 状态与交互

| 状态 | 视觉表现 |
|------|---------|
| **默认 (Idle)** | 仅内层圆可见，icon-primary 黑色 (rgba(0,0,0,0.898))；无外层圆 |
| **选中 (Selected)** | 外层圆出现 (icon-fourth 浅灰)；内层圆放大 +1px 并变为品牌蓝 #0A59F7 |
| **拖拽中 (Dragging)** | 选中点间显示锥形连线（灰色）；悬浮点显示半透明预览线 |
| **禁用 (Disabled)** | `opacity: 0.4` + `pointer-events: none` |
| **错误 (Error)** | 内层圆红色 #E84026，外层圆浅灰，连线保持灰色 |

## Props

| Prop | 类型 | 默认值 | DSL 对齐 | 说明 |
|------|------|--------|---------|------|
| `value` | `number[]` | `[]` | — | 当前已选中点索引（0–8），受控模式 |
| `onChange` | `(selected: number[]) => void` | — | — | 选中变化回调 |
| `onComplete` | `(pattern: number[]) => void` | — | — | 手势结束回调 |
| `disabled` | `boolean` | `false` | — | 禁用交互 |
| `error` | `boolean` | `false` | — | 错误态 |
| `success` | `boolean` | `false` | — | 成功态 |
| `outerColor` | `string` | `var(--hm-pattern-lock-outer-color, var(--harmony-icon-fourth))` | Light/icon_fourth；Dark/#BFBFBF | 外层圆颜色 |
| `innerColor` | `string` | `rgba(0,0,0,0.898)` (icon-primary) | Light/icon_primary | 内层圆默认颜色 |
| `selectedInnerColor` | `string` | `#0a59f7` (品牌蓝) | — | 选中态内层圆颜色 |
| `errorColor` | `string` | `#e84026` | — | 错误态颜色 |
| `lineColor` | `string` | `rgba(0,0,0,0.2)` | Light/icon_fourth | 连线颜色 |
| `className` | `string` | — | — | 自定义类名 |

> **DSL ↔ Prop 说明：** 本组件为交互式图案锁，Pixso DSL 中无直接可映射的可配置属性字段（DSL 仅描述静态节点树与实例结构）。Props 依据设计稿视觉规格与典型图案锁交互模式设计。`get_node_dsl` 仅返回顶层 FRAME + INSTANCE 信息，`get_variants` 返回空，变体由 SVG 导出结构重建。详见 `pattern-lock.json`。

## 样式引用

### 使用的全局 Token

| Token | 用途 |
|-------|------|
| `--harmony-brand` | 内层圆默认颜色 |
| `--harmony-comp-divider` | 外层圆 / 连线默认颜色 |
| `--hm-pattern-lock-outer-color` | PatternLock 外层圆颜色，Dark 覆盖为 `#BFBFBF` |

### 新增全局 Token

无新增语义化全局 Token；仅在 `global.css` 中为组件作用域添加 `--hm-pattern-lock-outer-color`，用于 Dark 模式外层圆覆盖。

## 取舍说明

1. **连线路径：** Pixso 设计稿中连线采用复杂 SVG path（减去顶层形状实现锥形效果），本实现使用简化版圆角锥形路径 (`connectionPath`)，视觉上基本等效。
2. **触摸热区：** 设计稿中无明确触摸区域数据，本实现使用 36px 半径（2× 视觉点直径），符合移动端触控可及性标准。
3. **动画：** 设计稿未定义动画时长/缓动，本实现使用 150ms ease 过渡。
4. **变体：** `get_variants` 返回空，变体树基于 SVG 结构重建。
5. **`design_to_code`：** 临时 URL 已过期（`Invalid batch timestamp`），降级使用 DSL + SVG 导出手工还原。
