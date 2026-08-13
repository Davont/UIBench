# CheckBox

## Metadata

- **实现目录：** `src/components/CheckBox/`
- **Stories 路径：** `src/components/CheckBox/CheckBox.stories.tsx`
- **Pixso 链接：** `https://pixso.cn/app/design/QeDttX-H4qVEUZXJjNfTCw?item-id=44:35189`
- **MCP 工具来源：** `get_node_dsl`（`44:35189`，Section "1.CheckBox - 勾选"，包含两种类型共 20 个变体实例）

## 组件变体树 JSON

- **路径：** `src/components/CheckBox/checkbox.json`
- **生成来源：** `get_node_dsl` 中 `pixComponentTreeDslNodes` 提取（两组组件集各 10 个变体）
- **变体轴：**
  - `type`: `"phone"`, `"2in1"`
  - `Selected`: `"OFF"`, `"ON"`
  - `状态`: `"Enabled"`, `"Hover"`, `"Pressed"`, `"Focus"`, `"Disabled"`
- **总变体数：** 2 × 2 × 5 = 20

## 组成与用途

- **导出项：** `CheckBox`（组件）、`checkBoxTypes`、`checkBoxSelecteds`、`checkBoxStates`（枚举常量）
- **使用场景：** 复选框组件，用于多选场景（勾选/取消勾选）。支持两种形状：圆形（phone）和圆角矩形（2in1）。
- **点击交互：** uncontrolled 模式下（不传 `Selected`）点击自动切换 ON/OFF；controlled 模式下由外部状态驱动，`onClick` 回调返回切换后的值。

## 量化规格

### 共享参数（两种类型通用）

| 属性 | 值 | 来源 |
|------|-----|------|
| 组件尺寸 | 24 × 24 px | DSL 容器 |
| 内盒尺寸 | 20 × 20 px，居中偏移 (2,2) | DSL Group / 矩形 6 / 椭圆 1 |
| OFF 边框 | 1px solid `--harmony-icon-tertiary`（rgba(0,0,0,0.4)）| DSL strokeAlign:INSIDE, icon_tertiary |
| OFF 填充 | rgba(255,255,255,0.2) | DSL fg_color_unchecked |
| ON 填充 | `--harmony-comp-background-emphasize`（rgba(10,89,247,1)）| DSL comp_background_emphasize |
| 勾选标记 | 18 × 17 px, white stroke 2px, drop-shadow(0 0.7px 1px rgba(0,0,0,0.1)) | DSL Rectangle 62 |
| Hover 叠加 | 24 × 24 px, `--harmony-interactive-hover`（rgba(0,0,0,0.047)）| DSL interactive_hover |
| Pressed 叠加 | 24 × 24 px, `--harmony-interactive-pressed`（rgba(0,0,0,0.098)）| DSL interactive_click |
| Disabled 不透明度 | 0.4 | DSL opacity |

### Type "phone"（圆形）— DSL Set 2 (guids `1:10xxx`)

| 属性 | 值 | 来源 |
|------|-----|------|
| 外层圆角 | 12px（正圆）| DSL cornerRadius:12 |
| 内盒圆角 | 10px（正圆）| DSL cornerRadius:10 |
| 叠加层圆角 | 12px | 同外层 |
| Focus 轮廓 | 2px solid `--harmony-interactive-focus` | DSL strokeWeight:2, strokeAlign:OUTSIDE |

### Type "2in1"（圆角矩形）— DSL Set 1 (guids `2804:12xxx`)

| 属性 | 值 | 来源 |
|------|-----|------|
| 外层圆角 | 6px | DSL cornerRadius:6 |
| 内盒 OFF 圆角 | 4px | DSL 矩形 6 cornerRadius:4 |
| 内盒 ON 圆角 | 10px（squircle）| DSL Rectangle 2375 Copy cornerRadius:10 |
| 叠加层圆角 | 6px | 同外层 |
| Focus 轮廓 | 1px solid `--harmony-interactive-focus` | DSL strokeWeight:1, strokeAlign:OUTSIDE |

## 状态与交互

| 状态 | Selected=OFF | Selected=ON |
|------|-------------|------------|
| Enabled | 灰色边框空心 | 蓝色填充 + 白色勾选 |
| Hover | + interactive_hover 叠加层 | + interactive_hover 叠加层 |
| Pressed | + interactive_pressed 叠加层 | + interactive_pressed 叠加层 |
| Focus | + interactive_focus 外轮廓 | + interactive_focus 外轮廓 |
| Disabled | 整体 opacity: 0.4 | 整体 opacity: 0.4 |

**点击交互：** 组件渲染为 `<button>`，Enabled 状态下点击自动切换 ON↔OFF。`:hover` 和 `:active` 伪类提供浏览器级视觉反馈。

## Props

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `type` | `"phone" \| "2in1"` | `"phone"` | 形状类型：圆形 / 圆角矩形 |
| `Selected` | `"OFF" \| "ON"` | 受控/非受控切换 | 对应 DSL `Selected`；不传则内部状态管理 |
| `状态` | `"Enabled" \| "Hover" \| "Pressed" \| "Focus" \| "Disabled"` | `"Enabled"` | 对应 DSL `状态` |
| `onClick` | `(next: CheckBoxSelected) => void` | — | 回调返回切换后的值 |

### DSL ↔ Prop 对照

| DSL 字段 | Prop 名 | 取值一致？ | 备注 |
|----------|---------|-----------|------|
| 组件集类型 | `type` | 是 | 两种组件集：圆形 → "phone"，圆角矩形 → "2in1" |
| `Selected` | `Selected` | 是 | 直用原名 |
| `状态` | `状态` | 是 | 直用原名 |

## 样式引用

- `--harmony-icon-tertiary`（OFF 边框）
- `--harmony-comp-background-emphasize`（ON 填充）
- `--harmony-interactive-hover`（Hover 叠加）
- `--harmony-interactive-pressed`（Pressed 叠加）
- `--harmony-interactive-focus`（Focus 轮廓）

以上变量均为 `global.css` 中已有 Token，未新增全局变量。

## 取舍说明

- `get_variants` 未获取到，变体树从 `get_node_dsl` 的 `pixComponentTreeDslNodes` 重建，两组各 10 个变体。
- `get_screenshot` 未执行，1:1 对照以 DSL 量化参数为准。
- 勾选标记使用本地 `HMSymbolIcon name="checkmark"`（U+F0013）；保持 18×17 外盒与原 `drop-shadow`，仅字形折点比例有小幅差异。
- Type "2in1" ON 态内盒使用 squircle border-radius:10px（DSL Rectangle 2375 Copy），与 "phone" 的圆形 border-radius:10px 视觉近似但语义不同。
- Focus 轮廓宽度按 DSL 实例级参数："phone" 为 2px，"2in1" 为 1px。
