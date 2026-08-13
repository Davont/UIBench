# Picker 选择器系统

## Metadata

- 实现目录：`src/components/Picker/`
- Stories 路径：`src/components/Picker/picker.stories.tsx`
- Pixso 链接：`https://pixso.cn/app/design/HA_e8I2mE7Oa0b5ZoeokSA?item-id=5322:727`
- item-id：`5322:727`
- MCP 工具来源：`get_node_dsl`（成功）、`get_variants`（返回空 `{}`，降级重建）、`get_screenshot`（成功：Time 和 Year with date 变体截图已获取）、`get_all_components`（部分 — 仅返回 Picker-Date-Phone，不含主变体集）

## 组件变体树 JSON

- 路径：`src/components/Picker/picker.json`
- 生成方式：`get_node_dsl` 子节点名称解析 + 实例树结构重建（`get_variants` 返回 `{}`）
- 变体轴：`类型`（Time / Year with date / Date with time）、`SlideRule类型`（Mini / Small / Medium）

## 组成与用途

4 个层级组件，由粒度从小到大：

| 组件 | 文件 | 用途 |
|------|------|------|
| `PickerItem` | `picker-item.tsx` | 单行滑动选项 |
| `PickerColumn` | `picker-column.tsx` | 单列滚轮（包含多个 PickerItem） |
| `Picker` | `picker.tsx` | 多列选择器主体 |
| `PickerDialog` | `picker-dialog.tsx` | 浮动弹窗式选择器 |

## 量化规格

### PickerItem（对照 DSL Text 节点）

| 属性 | Mini | Small | Medium（选中） |
|------|------|-------|---------------|
| 高度 | 36px | 36px | 56px |
| 字号 | 14px | 16px | 20px |
| 字重 | 400 (Regular) | 400 (Regular) | 500 (Medium) |
| 颜色 | var(--harmony-font-primary) | var(--harmony-font-primary) | var(--harmony-brand) |
| 透明度 | 0.4 | 0.6 | 1.0 |
| 行高 | 19px | 21px | 27px |
| 字间距 | 0 | 0 | 0 |
| 字体 | HarmonyHeiTi | HarmonyHeiTi | HarmonyHeiTi |
| Pixso 文本样式 | Body_M/Regular (602:9661) | Body_L/Regular (602:9658) | Title_S/Medium (602:9701) |
| Pixso 颜色样式 | — (渐变) | Light/font_primary (602:9446) | Light/font_emphasize (602:9440) |

### PickerColumn

- 总高度：200px
- 列间距：10px（对照 DSL `autoLayoutCounterItemSpacing: 10`，Pixso `5322:693` autoLayout）
- 列宽度（对照 DSL 实例 width 属性）：
  - **Time / Year with date（3 列）**：第一列 102px | 第二列 78px | 第三列 50px（总宽 250px，280px 容器内水平居中）
  - **Date with time（4 列）**：78px | 64px | 50px | 48px（总宽 280px，精度匹配 10px 间距）
- 滚动容器，隐藏滚动条
- 选中指示器：56px 高，上下各 0.25px solid `--harmony-comp-divider`（Pixso: Light/icon_fourth 602:9454）
- **滚轮交互**：`activeIndex` 由实时 scrollTop 计算（距视口中心最近的 item），而非固定 `selectedIndex`。蓝色选中样式始终固定在视口中心位置，滚动只改变中心位置对应的数值。
- **吸附（snap）**：滚动停止 180ms 后自动吸附到最近的整数项
- **顶部/底部 spacer**：各 72px `(200-56)/2`，确保首尾项也能滚入视口中心

### Picker

- 尺寸：280 × 200px
- 背景：transparent
- 布局：水平 flex，gap=0
- 类型变体（来自 DSL `5322:727` 下 INSTANCE 子节点）：
  - **Time**（`5322:693`）：3 列 — AM/PM(102px) | 小时(78px) | 分钟(50px)
  - **Year with date**（`5322:614`）：3 列 — 月-日(102px) | 时段(78px) | 年(50px)
  - **Date with time**（`5322:648`）：4 列 — 星期(78px) | AM/PM(64px) | 小时(50px) | 分钟(48px)（总宽 280px，精度匹配 10px 间距）

### PickerDialog (FloatingPickerDialog-Phone)

- 尺寸：328 × 328px
- 圆角：32px
- 背景：`--harmony-comp-background-primary`
- 材质：`backdrop-filter: blur(18px) saturate(120%)` + 多层 inset box-shadow
- 内边距：8px 24px 16px 24px
- 标题区：height=48px, fontSize=20px, fontWeight=500, color=font-primary, opacity=0.9, lineHeight=27px
- 按钮区：height=56px, 两个按钮各 140×40px, 圆角=20px
- 分隔线：0.5px × 24px, `--harmony-comp-divider`

## 状态与交互

| 状态 | 说明 |
|------|------|
| default | 各列显示可选列表，中心项高亮（brand 色 + Medium 尺寸） |
| hover | PickerItem hover 可选；Dialog 按钮 hover 背景为 `--harmony-interactive-hover` |
| active/pressed | 滚轮拖动选择 |
| selected | 中心项即为选中项（PickerItem selected=true），显示 brand 蓝色 + 最大字号 |
| open/closed | PickerDialog 通过 `open` prop 控制显隐 |

## Props DSL ↔ Prop 对照

| DSL 字段 | Prop 名 | 取值 | 默认值 | 说明 |
|----------|---------|------|--------|------|
| 实例名 `类型=*` | 类型 | "Mini" / "Small" / "Medium" | "Mini" | PickerItem 变体轴 |
| selected (概念) | selected | boolean | false | 选中态 — DSL 中 Medium=选中 |
| PickerColumn.items | items | string[] | — | 列内容 |
| PickerColumn.selectedIndex | selectedIndex | number | 0 | 选中项索引 |
| PickerColumn.onSelect | onSelect | (index: number) => void | — | 选择回调 |
| Picker 实例名 `类型=Time` 等 | 类型 | "Time" / "Year with date" / "Date with time" | "Time" | 直接对齐 DSL 变体轴 |
| Picker.columns | columns | PickerColumnProps[] | 由类型决定 | 自定义列配置 |
| PickerDialog.open | open | boolean | false | 弹窗开关 |
| PickerDialog.onOpenChange | onOpenChange | (open: boolean) => void | — | 开关回调 |
| PickerDialog.title | title | string | "Select" | 标题文本 |
| PickerDialog.类型 | 类型 | PickerType | "Time" | 透传至 Picker |
| PickerDialog.onConfirm | onConfirm | () => void | — | 确认回调 |
| PickerDialog.onCancel | onCancel | () => void | — | 取消回调 |
| PickerDialog.confirmLabel | confirmLabel | string | "Confirm" | 确认按钮文案 |
| PickerDialog.cancelLabel | cancelLabel | string | "Cancel" | 取消按钮文案 |

> **Props 命名策略**：所有 Props 直接使用 Pixso DSL 原始属性名（`类型`），符合仓库 Props 硬对齐规范。无命名映射例外。

## 样式引用

### 使用的 global.css 变量

| 变量 | 用途 |
|------|------|
| `--harmony-font-primary` | Small/Mini item 文字色 |
| `--harmony-brand` | Medium 选中项文字色 + confirm 按钮色 |
| `--harmony-comp-divider` | 选中指示器边框 + dialog 分隔线 |
| `--harmony-comp-background-primary` | Dialog 背景 |
| `--harmony-interactive-hover` | Dialog 按钮 hover 态 |

### 组件级 CSS

- `picker.css`（组件目录内），所有样式通过 CSS class 实现
- 无新增全局 Token（现有 `global.css` 变量已覆盖所有需要的设计 token）

## 取舍说明

1. **`get_variants` 返回 `{}`**：变体树从 `get_node_dsl` 子节点名称 + 实例树结构重建
2. **Mini item 渐变文字效果**：DSL 使用 GRADIENT_LINEAR fill 实现上下边缘淡出效果；CSS 使用 uniform `opacity: 0.4` 近似（CSS gradient text fill 跨浏览器兼容性差且与滚动交互不友好）
3. **`design_to_code` 未调用**：DSL + 截图证据充分，无需 codegen 草案
4. **PickerDialog 设计**：当前 Pixso 节点 5322:727 仅含 Picker 三种类型变体，不含 Dialog；Dialog 样式沿用仓库现有实现并微调至与全局材质规范一致
5. **行高校准**：DSL 文本节点高度（27px/21px/19px）作为各行高值直接落地，覆盖之前的 `line-height: 1.5`
