# TextInput 规格文档

## Metadata

| 字段 | 值 |
|------|-----|
| 组件 ID | `text-input-box-phone` / `text-input-none-phone` / `text-input-muti-phone` |
| 实现目录 | `src/components/Input/TextInput/` |
| Stories 路径 | `src/components/Input/TextInput/TextInputBoxPhone.stories.tsx` / `TextInputNonePhone.stories.tsx` / `TextInputMutiPhone.stories.tsx` |
| Pixso 链接 | `https://pixso.cn/app/design/QeDttX-H4qVEUZXJjNfTCw?item-id=40:35480` |
| Pixso item-id | `40:35480` |
| MCP 工具 | `get_node_dsl` (✓), `get_variants` (✗ 降级), `get_all_components` (✓ 降级补全) |
| get_screenshot | 未调用（用户指定不调用） |

## 组件变体树

路径：`src/components/Input/TextInput/textinput.json`

生成方式：`get_variants` 返回 `{}`，降级使用 `get_node_dsl` 的 `pixComponentTreeDslNodes`（69 个 SYMBOL 节点）+ `get_all_components` 名称解析重建。

## 组成与用途

Phone 系列已从旧 `TextInput` 的 `类型` 属性拆分为 3 个公开组件：

| 组件 | 固定 DSL 变体 | 说明 |
|------|---------------|------|
| `TextInputBoxPhone` | `textinput-box-phone` | 手机圆角方框单行输入框 |
| `TextInputNonePhone` | `textinput-none-phone` | 手机胶囊形无右侧图标输入框 |
| `TextInputMutiPhone` | `textinput-muti-phone` | 手机多行文本框（沿用 DSL 中的 `muti` 拼写） |

`TextInput` 保留为兼容导出，可继续接收 `类型`，但 Storybook 与组件注册表主推上述 3 个组件。

原始 DSL 中包含以下变体：

| 变体 | 说明 | DSL 来源 GUID |
|------|------|---------------|
| `textinput-box-phone` | 手机圆角方框单行输入框 | 2804-range |
| `textinput-muti-phone` | 手机多行文本框 | 2804:11961 |
| `textinput-none-phone` | 手机胶囊形无边框输入框 | 40-range |
| `textinput-single line-2in1` | 2in1 单行输入框 | 1:12412 |
| `textinput-multi line-2in1` | 2in1 多行文本框 | 推导 |
| `textinput-withscrollbar-2in1` | 2in1 带滚动条多行输入 | 331:12777 |
| `textinput-box-2in1` | 2in1 方框风格输入框 | 推导（box-phone + 2in1） |
| `textinput-multi-2in1` | 2in1 多选列表 | 推导（含 选中 radio） |

## 量化规格

### textinput-box-phone（40-range, corner=24）

| 参数 | 值 |
|------|-----|
| 宽度 | 250px |
| 高度（单行） | 40px |
| 高度（Error） | 64px |
| 圆角 | **24px**（pill 胶囊形，DSL corner=24） |
| 填充（灰色场景=OFF） | rgba(0,0,0,0.05) |
| 填充（灰色场景=ON） | rgba(255,255,255,1) |
| 内边距 | L16 R4 T8 B8 |
| 间距 | gap=8, HORIZONTAL |
| 字号 | 16px |
| 行高 | 21px |
| Placeholder 颜色 | rgba(0,0,0,0.60) → `--harmony-font-secondary` |
| 输入文字颜色 | rgba(0,0,0,0.90) → `--harmony-font-primary` |
| 光标 | 1.5×24px, rgba(10,89,247,1) → `--harmony-brand` |
| Right icon | 32×32px, corner=16, 默认本地 HM Symbol Eye 图标 |

### textinput-none-phone（40-range, corner=24）

| 参数 | 值 |
|------|-----|
| 宽度 | 250px |
| 高度 | 40px |
| 圆角 | **24px**（pill 胶囊形，DSL corner=24） |
| 填充 | 同 box-phone |
| 内边距 | L16 R4 T8 B8 |
| 间距 | gap=8, HORIZONTAL |
| Normal/Hover/Actived/Disable 底部分隔线 | 0.5px solid `--harmony-comp-divider`，位置对齐 Error 态 field-wrapper bottom |
| Typing 底部分隔线 | 0.5px solid primary 50%，light 为 `rgba(0,0,0,0.5)`，dark 为 `rgba(255,255,255,0.5)` |
| Focus 边框 | 2px solid rgba(10,89,247,1) |

### textinput-muti-phone（40-range, corner=24）

| 参数 | 值 |
|------|-----|
| 宽度 | 250px |
| 高度 | 135px |
| 圆角 | **24px**（pill 胶囊形） |
| 内边距 | L16 R16 T8 B8 |
| 布局 | VERTICAL |
| 文本区域 | 16px, 105px 高 |
| 提示区域 | 10px, 14px 高, rgba(0,0,0,0.40) |

### textinput-single line-2in1（Space 变体）

| 参数 | Space=OFF | Space=ON |
|------|-----------|----------|
| 宽度 | 256px | 256px |
| 高度 | 56px | 48px |
| 圆角 | 0 | 0 |
| 内边距 | T4 B4 | T13 B13 |
| 底部矩形（矩形 7） | 256×48, 0.5px stroke rgba(0,0,0,0.2) | 无（整体 stroke） |
| 整体 border | 无 | 0.5px solid rgba(0,0,0,0.2) |

#### 状态色彩（2in1）

| 状态 | Stroke 颜色 | Stroke 宽度 |
|------|-------------|-------------|
| Normal | rgba(0,0,0,0.2) | 0.5px |
| Hover | rgba(0,0,0,0.2) + bg rgba(0,0,0,0.05) | 0.5px |
| Focus | rgba(10,89,247,1) | 2px |
| Typing | rgba(0,0,0,0.5) | 0.5px |
| Actived | rgba(0,0,0,0.2) | 0.5px |
| Error | rgba(217,72,56,1) | 1px |
| Disable | rgba(0,0,0,0.2) | 0.5px |

### textinput-withscrollbar-2in1

| 参数 | 值 |
|------|-----|
| 宽度 | 250px |
| 高度 | 110px |
| 圆角 | 4px |
| 填充 | rgba(255,255,255,1) |
| 边框 | 2px solid rgba(10,89,247,1) |
| ScrollBar | 32×40px instance |

## 状态与交互

| 状态 | 说明 | 典型视觉变化 |
|------|------|-------------|
| Normal | 默认态 | placeholder 文字, 基础边框/填充 |
| Hover | 鼠标悬停 | 背景叠加 rgba(0,0,0,0.05), 出现文本光标图标 |
| Focus | 获得焦点 | 边框变蓝 (brand), stroke 加粗到 2px |
| Typing | 正在输入 | 光标闪烁, 文字颜色变深 (0.9), stroke 加深 |
| Actived | 已激活 | 光标在起始位置 |
| Error | 错误态 | 边框变红 (warning), 显示错误提示 |
| Disable | 禁用态 | 文字颜色变浅 (0.4), 不可交互 |
| Count | 计数态 | 显示计数文字, 边框变红 |

## Props 与 DSL 对照

拆分后，公开组件不再暴露 `类型` 属性；组件名本身即固定 DSL 变体。

| DSL 属性 | Prop 名 | 类型 | 默认值 | 说明 |
|----------|---------|------|--------|------|
| 类型（phone 变体帧名） | 组件名 | `TextInputBoxPhone` / `TextInputNonePhone` / `TextInputMutiPhone` | — | 由组件固定，不再作为 Storybook Control |
| 状态 | `状态` | `TextInputState` | `undefined` (自动推导) | 8 种交互状态 |
| 灰色场景=OFF/ON | `灰色场景` | `"OFF" \| "ON"` | `"OFF"` | phone 系列背景切换 |
| icon=1/2（DSL 图标变体） | `icon` | `"none" \| "eye" \| "eye-cancel"` | `"none"` | 仅 `TextInputBoxPhone` 暴露 |
| — | `rightIcon` | `ReactNode` | `undefined` | 仅 `TextInputBoxPhone` 暴露，自定义右侧图标（覆盖 `icon`） |
| — | `errorText` | `string` | `"Error"` | `TextInputBoxPhone` / `TextInputNonePhone` 错误提示 |
| — | `helperText` | `string` | `"100"` | `TextInputBoxPhone` / `TextInputNonePhone` 计数上限 |
| — | `hintText` | `string` | `"最多 200 字"` | 仅 `TextInputMutiPhone` 多行提示文字 |
| — | `value` | `string` | `undefined` | 受控值 |
| — | `placeholder` | `string` | `"Input"` | 占位文字 |
| — | `onChange` | `(v: string) => void` | `undefined` | 值变化回调 |
| — | `disabled` | `boolean` | `undefined` | 是否禁用 |
| — | `inputType` | `"text" \| "password"` | `undefined` | 仅单行组件可用，`icon` 为 eye 时自动切换 |

**命名映射说明：** `状态`、`灰色场景` 继续直接使用 DSL 原始属性名；`类型` 已上移为组件名，避免在使用侧通过属性切换结构性变体。`icon` 对齐 DSL 中的 `icon=1` / `icon=2` 变体维度。`rightIcon`、`errorText` 等为组件功能性 Props。

## 右侧图标（icon 维度）

DSL 中包含 `.right_icon` 实例（32×32px, corner=16），以及图标子组件：

| DSL 组件 | 尺寸 | 说明 | 实现 |
|----------|------|------|------|
| `.eye` | 20×20 | 眼睛图标（显示/隐藏密码） | `HMSymbolIcon`：`eye`（U+F0120）/ `eye_slash`（U+F011F） |
| `.Small cancel` | 18×18 | 清除图标（xmark） | `HMSymbolIcon name="xmark"`（U+F0056） |
| `icon=1` | 32×32 | 仅含 `.eye` | `icon="eye"` |
| `icon=2` | 64×32 | 含 `.eye` + `.Small cancel` | `icon="eye-cancel"` |

交互行为：
- `icon="eye"`: 点击切换 `inputType` 在 `text` / `password` 之间，图标在 Eye / EyeOff 之间切换
- `icon="eye-cancel"`: 除眼睛切换外，当有输入值时额外显示清除按钮（X），点击清空内容

## 样式引用

### 使用的全局 Token

| Token | 用途 |
|-------|------|
| `--harmony-brand` | Focus 边框色、光标色、滚动条边框 |
| `--harmony-warning` | Error 边框色、错误提示文字色 |
| `--harmony-font-primary` | 输入文字色 (0.9) |
| `--harmony-font-secondary` | Placeholder 色 (0.6) |
| `--harmony-font-tertiary` | Disabled 文字色 (0.4)、提示色 |
| `--harmony-comp-divider` | 默认边框色 (0.2) |
| `--harmony-comp-background-tertiary` | 填充色 (0.05) |
| `--harmony-comp-background-primary` | 白色背景（灰色场景=ON） |

### 新增全局 Token

无新增 Token。所有色值均可通过现有 `global.css` Token 覆盖。

## 取舍说明

| 项目 | 取舍 | 原因 |
|------|------|------|
| `get_screenshot` | 未调用 | 用户指定不调用 |
| `get_variants` | 返回空 `{}` | 降级使用 `get_node_dsl` + `get_all_components` 名称解析 |
| `textinput-multi line-2in1` | 从 box-phone multi 推导 | DSL 中无独立 2in1 multi-line 节点，基于同类结构推导 |
| `textinput-box-2in1` | 从 box-phone + 2in1 尺寸推导 | DSL 中无独立 box-2in1 节点 |
| `textinput-multi-2in1` | 从 radio 组件（选中=OFF/ON）推导 | DSL 中有 radio 子组件但未组合为 multi-2in1 独立节点 |
| 光标动画 | CSS blink 动画 | DSL 仅有静态光标矩形，实现增加闪烁以符合真实输入体验 |
| Hover 文本光标图标 | CSS cursor: text | DSL 中 `.CURSOR TYPE` 为矢量图标，以 CSS cursor 属性近似 |
