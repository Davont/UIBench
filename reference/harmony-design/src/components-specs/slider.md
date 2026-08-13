# Slider

## Metadata

- **实现目录**: `src/components/Selection/Slider/`
- **Slider Stories 路径**: `src/components/Selection/Slider/Slider.stories.tsx`
- **SliderSeekbar Stories 路径**: `src/components/Selection/SliderSeekbar/SliderSeekbar.stories.tsx`
- **测试路径**: `src/components/Selection/Slider/slider.test.tsx`
- **Pixso 来源**:
  - SliderPhone: `https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5322:21935`
  - SliderSeekbarPhone: `https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5322:22002`
  - SliderSeekbarPhone 单轴变体校准: `https://pixso.cn/app/design/d0WMuB0Im216ZfRVW4uwyQ?item-id=5410:185`
- **组件拆分**: `SliderPhone` → `Slider`，`SliderSeekbarPhone` → `SliderSeekbar`
- **SliderSeekbar 变体树 JSON**: `src/components/Selection/SliderSeekbar/SliderSeekbar.json`
- **默认端点图标**: 本地 HMSymbol `sun_min`（U+F0051）/ `sun_max`（U+F0050）

## 组成与用途

`Slider` 与 `SliderSeekbar` 默认按 360px 移动画板还原，共享布局变体与交互逻辑，但以两个独立组件表达不同轨道视觉。需要放入 328px 设置卡片或自定义容器时，使用 `layout="contained"` / `宽度="自适应"` 进入父容器自适应模式。

- `Slider`: Thick 胶囊轨道，20px 高，12px 白色滑块 + 品牌色描边环（来自 SliderPhone）
- `SliderSeekbar`: Thin 细线轨道，4px 高，16px 白色滑块 + 阴影（来自 SliderSeekbarPhone）

### 导出项

- `Slider`
- `SliderSeekbar`
- `sliderTypes`, `sliderStates`, `sliderSeekbarStates`
- `SliderProps` / `SliderSeekbarProps` / `SliderType` / `SliderState` / `SliderSeekbarState`

## Props

| Prop | 类型 | 默认值 | 说明 |
|---|---|---|---|
| 类型 | `SliderType` | `"Basic"` | 布局变体（9 种） |
| 状态 | `SliderState` | `"Enabled"` | 视觉状态 |
| layout | `"fixed" \| "contained"` | `"fixed"` | 宽度布局；`fixed` 保持 Pixso 360px，`contained` 随父容器收缩 |
| 宽度 | `"固定" \| "自适应"` | — | `layout` 的中文别名；`自适应` 等价于 `layout="contained"` |
| value | `number` | — | 受控值 |
| defaultValue | `number` | `42` | 非受控初始值 |
| min | `number` | `0` | 最小值 |
| max | `number` | `100` | 最大值 |
| step | `number` | `1` | 步长 |
| disabled | `boolean` | `false` | 禁用 |
| onChange | `(value: number) => void` | — | 变更回调 |
| title | `string` | `"Title"` | Title / Icon with title 标题 |
| progressValue | `string` | `"Progress value"` | Title 右侧文案 |
| leftLabel | `string` | `"A"` | Value with text change 左侧 |
| rightLabel | `string` | `"A"` | Value with text change 右侧 |
| smallLabel | `string` | `"Small"` | Textview 左侧 |
| bigLabel | `string` | `"Big"` | Textview 右侧 |
| icons | `[ReactNode, ReactNode]` | — | 自定义左右图标 |

### SliderSeekbar Props

`SliderSeekbar` 按 Pixso `Slider-Seekbar-Phone` 组件集收敛为单一变体轴，只保留 `状态`，不再对外暴露 `类型`。

| Prop | 类型 | 默认值 | 说明 |
|---|---|---|---|
| 状态 | `SliderSeekbarState` | `"enabled"` | Pixso 单轴变体 |
| value | `number` | — | 受控值 |
| defaultValue | `number` | `42` | 非受控初始值 |
| min | `number` | `0` | 最小值 |
| max | `number` | `100` | 最大值 |
| step | `number` | `1` | 步长 |
| disabled | `boolean` | `false` | 禁用 |
| onChange | `(value: number) => void` | — | 变更回调 |
| icons | `[ReactNode, ReactNode]` | — | `状态="icon"` 时的自定义左右图标 |

### 类型变体（9 种）

Basic, Scale, Icon, Value with text change, Value, Icon with title, Bubble, Title, Textview

### 状态（3 种）

Enabled（默认，自动响应 hover/focus）, Hover, Focus

### SliderSeekbar 状态（7 种）

`enabled`, `icon`, `focus`, `hover`, `Value`, `Bubble`, `Scale`

| Pixso 变体 | 内部类型 | 内部视觉状态 |
|---|---|---|
| `状态=enabled` | `Basic` | `Enabled` |
| `状态=icon` | `Icon` | `Enabled` |
| `状态=focus` | `Basic` | `Focus` |
| `状态=hover` | `Basic` | `Hover` |
| `状态=Value` | `Value` | `Enabled` |
| `状态=Bubble` | `Bubble` | `Enabled` |
| `状态=Scale` | `Scale` | `Enabled` |

## 量化规格

### Slider / Thick 轨道

| 项 | 数值 |
|---|---|
| 轨道高度 | `20px` |
| 轨道圆角 | `12px` |
| 滑块尺寸 | `12px` + `2px` 品牌描边环 |
| 激活轨道宽度（默认） | `140px` → 进度 `42` |

### Contained 自适应模式

| 项 | 规则 |
|---|---|
| 根节点 | `width: 100%; min-width: 0; max-width: none` |
| Icon / Value with text change | 取消默认 `padding-inline: 24px`，避免 328px 卡片内溢出 |
| Rail shell | 使用 `hm-slider__rail-shell--full`，不写固定 `--slider-track-width` |
| Thick track | `width: 100%; min-width: 0` |
| 画板级子布局 | `Scale`、`Title`、`Textview`、`Bubble` 等内部 360px 容器在 contained 下改为 `width: 100%` |

### SliderSeekbar / Thin 轨道

| 项 | 数值 |
|---|---|
| 轨道高度 | `4px` |
| 轨道圆角 | `12px` |
| 滑块尺寸 | `16px`（内圈）+ `24px`（外圈，hover 时显示） |
| 滑块阴影 | `0 0 3px rgba(0,0,0,0.2)` |
| Scale 刻度点 | 4×4px，绘制在灰色轨道背景层，位于蓝色进度条下方 |

## 组件变体树 JSON

- `src/components/Selection/SliderSeekbar/SliderSeekbar.json`
- `get_variants(5410:185)` 成功返回 7 个变体；展示顺序按 `enabled`, `icon`, `focus`, `hover`, `Value`, `Bubble`, `Scale` 排列。
- `design_to_code(5410:185)` 与 `get_screenshot(5410:185)` 在本轮执行中均 300s 超时；实现以 `get_variants` 结构和用户截图为依据。

## 样式引用

### 全局 Token

- `--harmony-brand`
- `--harmony-comp-background-tertiary`
- `--harmony-font-primary`
- `--harmony-font-secondary`
- `--harmony-font-on-primary`
- `--harmony-interactive-focus`
- `--slider-harmony-bubble`
- `--button-harmony-font-family`

### 暗色模式

`SliderSeekbar` 的 Thin 轨道通过组件级 CSS 变量支持 `:root[data-theme="dark"]` 暗色覆盖。`Slider` 的 Thick 轨道通过全局设计 token 自动适配。

## 取舍说明

1. **双组件视觉系统**: `Slider` 使用 Thick CSS 伪元素（`::before`/`::after`），`SliderSeekbar` 使用 Thin 独立 div 元素。两者共享内部 SliderRail 与拖拽逻辑，但对外不再通过 `轨道样式` prop 切换。
2. **统一拖拽交互**: 两个组件均使用 SliderPhone 的高级拖拽处理（window 级 mousemove/touchmove 事件），而非纯原生 input。
3. **Bubble 文案**: 气泡始终显示实时百分比 `${pct}%`，随滑块值自动更新。
4. **min/max/step 支持**: 来自 SliderSeekbarPhone，`Slider` 与 `SliderSeekbar` 均支持自定义范围和步长。
5. **SliderSeekbar API 收敛**: Pixso 新节点将 `enabled / icon / focus / hover / Value / Bubble / Scale` 全部表达为 `状态` 轴，因此 `SliderSeekbar` 对外合并原 `类型` 与 `状态`，内部仍复用 `SliderRoot` 的类型和视觉状态映射。
6. **宽度兼容策略**: 默认 `layout="fixed"` 保留 Pixso 360px 画板还原；`layout="contained"` 是容器适配扩展，用于 List card、设置页自定义行等窄容器，不再依赖页面深选择器覆盖 rail/track。
