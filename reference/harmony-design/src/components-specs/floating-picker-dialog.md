# FloatingPickerDialog

## Metadata

- 实现目录：`src/components/Selection/FloatingPickerDialog/`
- Stories 路径：`src/components/Selection/FloatingPickerDialog/FloatingPickerDialog.stories.tsx`
- Pixso 链接：`https://pixso.cn/app/design/HA_e8I2mE7Oa0b5ZoeokSA?item-id=5322:1203`
- item-id：`5322:1203`
- Picker 类型 Pixso 链接：`https://pixso.cn/app/design/d0WMuB0Im216ZfRVW4uwyQ?item-id=5406:1544`
- Picker 类型 item-id：`5406:1544`
- ButtonGroup Pixso 链接：`https://pixso.cn/app/design/d0WMuB0Im216ZfRVW4uwyQ?item-id=5409:2830`
- ButtonGroup item-id：`5409:2830`
- MCP 工具来源：`get_node_dsl`（成功）、`get_screenshot`（成功）、`get_variants`（返回 `{}`，降级重建）、`design_to_code`（500，未采用）
- Picker 类型 MCP：`design_to_code` 超时、`get_screenshot` 超时、`get_variants` 返回 `[]`；按用户截图 + 既有 Picker 规格降级实现
- ButtonGroup MCP：`design_to_code` 超时、`get_screenshot` 超时、`get_variants` 返回 `[]`；按用户截图降级实现

## 组件变体树 JSON

- 路径：`src/components/Selection/FloatingPickerDialog/floating-picker-dialog.json`
- 生成方式：由 `get_node_dsl` 顶层 4 个实例名 `通透度=强|标准|降档|弱` 重建；Picker 类型与 ButtonGroup 变体由截图补齐
- 变体轴：`通透度`、`类型`、`ButtonGroup类型`、`ButtonGroup个数`

## 组成与用途

- `FloatingPickerDialog`：328 × 328 的浮层选择弹窗，含标题、类型化滚轮和底部双按钮
- 复用：内部复用 `PickerColumn` 以保持滚轮行高、吸附和选中态与现有 Picker 系统一致

## 量化规格

### 外层容器

- 尺寸：`328 × 328px`
- 圆角：`32px`
- 内边距：`8px 24px 16px`
- 标题区高：`48px`
- Picker 区高：`200px`
- 按钮区高：`56px`

### 标题

- 默认文本：`Friday, July 7, 2025`
- 字体：`HarmonyHeiTi`
- 字号：`20px`
- 字重：`500`
- 行高：`27px`
- 字间距：`0`
- 颜色：`--harmony-font-primary`

### Picker 类型与列宽

- `类型=Time`：3 列，`AM/PM 102px | 小时 78px | 分钟 50px`
- `类型=Year with date`：3 列，`年份 102px | 月份 78px | 日期 50px`
- `类型=Date with time`：4 列，`日期 78px | AM/PM 64px | 小时 50px | 分钟 48px`
- 列间距：`10px`
- 选中带：`56px` 高，`0.5px` 上下分隔线

### 滚轮文字

- 复用 `PickerColumn` / `PickerItem`
- Mini：`14px / 19px / opacity 0.4`
- Small：`16px / 21px / opacity 0.6`
- Medium：`20px / 27px / 500 / --harmony-brand`

### ButtonGroup

- `ButtonGroup类型=normal`：支持 `ButtonGroup个数=1/2`
  - 1 个：单个文字按钮，居中显示 `BUTTON`
  - 2 个：左 `Cancel`、右 `OK`，中间分隔线 `0.5 × 24px`
- `ButtonGroup类型=emphasize`：支持 `ButtonGroup个数=1/2`
  - 1 个：单个蓝色主按钮，宽度铺满内容区
  - 2 个：左文字按钮，右蓝色主按钮
- `ButtonGroup类型=emphasize-port`：支持 `ButtonGroup个数=1/2/3`
  - 1 个：单个蓝色主按钮
  - 2 个：蓝色主按钮在上，文字按钮在下
  - 3 个：蓝色主按钮在上，两个文字按钮竖向排列在下
- 文字按钮尺寸：`116 × 40px`
- 主按钮高度：`40px`
- 圆角：`20px`
- 字号：`16px`
- 字重：`500`
- 行高：`21px`
- 文字按钮颜色：`--harmony-font-emphasize`
- 主按钮背景：`--harmony-brand`
- 主按钮文字：`--harmony-font-on-primary`

## 状态与交互

- `通透度=强`：高光最强，暖色反射明显，使用 `Material_background_THICK` 系列近似还原
- `通透度=标准`：以 `FLOATING_THICK` 材质为主，内阴影与 blur 最完整
- `通透度=降档`：趋近实体白底，blur 与高光减弱
- `通透度=弱`：透明度更高，依赖淡白底与弱高光
- 列滚动：沿用 `PickerColumn` 的中心吸附和自动对齐
- 按钮：hover/pressed 覆盖 `interactive-hover` / `interactive-pressed`

## Props 与 DSL 对照

| DSL 字段 | Prop 名 | 取值 | 默认值 | 说明 |
|---|---|---|---|---|
| 顶层实例名 `通透度=*` | `通透度` | `"强" \| "标准" \| "降档" \| "弱"` | `"标准"` | 与 DSL 唯一可见变体轴硬对齐 |
| Picker-Phone `类型=*` | `类型` | `"Time" \| "Year with date" \| "Date with time"` | `"Time"` | 中间 Picker 样式，来自新 Pixso 截图与既有 Picker 类型规格 |
| ButtonGroup `类型=*` | `ButtonGroup类型` | `"normal" \| "emphasize" \| "emphasize-port"` | `"normal"` | 底部按钮组样式，来自 ButtonGroup 截图 |
| ButtonGroup `个数=*` | `ButtonGroup个数` | `1 \| 2 \| 3` | `2` | `normal/emphasize` 最多支持 2，`emphasize-port` 支持 1/2/3；非法组合自动回落到 2 |
| 截图标题文案 | `标题` | `string` | 自动从首列生成 | DSL 未直接暴露文本属性，运行时覆盖入口 |
| 嵌套 Picker 文本序列 | `columns` | `FloatingPickerDialogColumn[]` | 按 `类型` 内置 | 依据截图与嵌套 picker 结构抽象；传入后覆盖类型默认列 |
| 嵌套 Picker 当前项 | `selectedIndices` | `number[]` | 由默认列决定 | 运行时受控索引 |
| 嵌套 Picker 当前项 | `defaultSelectedIndices` | `number[]` | 由 `类型` 默认列决定 | 非受控初始值 |
| 嵌套 Picker 变化 | `onSelectedIndicesChange` | `(indices, values) => void` | — | 运行时回调 |
| 通用按钮文本 | `按钮文案` | `string` | `"BUTTON"` | 用于单按钮、emphasize 和 emphasize-port 变体 |
| 底部左按钮文本 | `取消文案` | `string` | `"Cancel"` | DSL 未暴露，按截图补齐 |
| 底部右按钮文本 | `确认文案` | `string` | `"OK"` | DSL 未暴露，按截图补齐 |
| 底部左按钮行为 | `onCancel` | `() => void` | — | 运行时回调 |
| 底部右按钮行为 | `onConfirm` | `(values, indices) => void` | — | 运行时回调 |

> 说明：原始节点的 `get_node_dsl` 只稳定暴露了 `通透度` 这个外层变体轴；新 Picker 类型和 ButtonGroup 节点 MCP 超时且 `get_variants` 返回空数组，因此 `类型` 与 `ButtonGroup*` 依据用户截图补齐。

## 样式引用

- 复用全局变量：
  - `--FLOATING_THICK_fill`
  - `--FLOATING_THICK_fill_blend_mode`
  - `--Material_background_THICK_fill`
  - `--Material_background_THICK_fill_blend_mode`
  - `--harmony-font-primary`
  - `--harmony-font-emphasize`
  - `--harmony-brand`
  - `--harmony-font-on-primary`
  - `--harmony-interactive-hover`
  - `--harmony-interactive-pressed`
  - `--harmony-interactive-focus`
- 未新增 `global.css` token

## 取舍说明

1. `get_variants` 返回空对象，因此 `{名称}.json` 由顶层实例名降级重建。
2. `design_to_code` 返回 500，按 skill 要求忽略 codegen，最终以 DSL + 截图手工实现。
3. Pixso 暖色高光来自背景图穿透与材质叠加，组件内用渐变高光近似复现，以便在 Storybook 任意背景下保持接近观感。
4. 内部滚轮继续复用既有 `PickerColumn`，优先保证滑动吸附、字号层级和中心选中规则与仓库 Picker 体系一致。
5. ButtonGroup 节点 MCP 超时，`normal / emphasize / emphasize-port` 和合法按钮个数依据用户截图实现；`ButtonGroup个数=3` 在 `normal/emphasize` 下自动按 2 个渲染。
