# ListPhone — 列表项组件

## Metadata

- **实现目录**: `src/components/Container/ListPhone/`
- **组件文件**: `ListPhone.tsx`
- **样式文件**: `list-phone.css`
- **Stories**: `ListPhone.stories.tsx`
- **测试**: `list-phone.test.tsx`
- **变体树 JSON**: `list-phone.json`
- **Pixso 链接**: https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=62:35191
- **Item ID**: `62:35191`
- **MCP 数据来源**: `get_node_dsl` + `get_screenshot` + `design_to_code` for `62:35191`; divider geometry checked against `List-Phone` and `.Left - * lines` variants.

## 组成与用途

`ListPhone` 是移动端设置页和列表页的基础行项组件。它负责行高、标题层级、分隔线、左侧 addon 和右侧 value/control/icon 的一致渲染。

**导出项**: `ListPhone`, `listPhoneLines`, `listPhoneRightTypes`, `listPhoneLeftTypes`, `ListPhoneProps`, `ListPhoneLines`, `ListPhoneRightType`, `ListPhoneLeftType`

## 量化规格

### 尺寸与行数

| 行数 | 根高度 | 内容结构 | 内容 padding |
|---|---:|---|---:|
| `"1"` | 48px | title | 13px 0 |
| `"2"` | 64px | title + subtitle | 8px 0 |
| `"3"` | 80px | title + subtitle + description | 7px 0 |

- 根容器: `width: 100%`, horizontal padding `12px`, gap `12px`
- 分隔线: 属于正文 main 内容区域，由 `.list-phone__main::after` 绘制 `height: 1px + scaleY(0.5)` 发丝线；由 `divider` prop 控制是否渲染，默认 `true`，多行列表最后一行显式传 `divider={false}` 隐藏
- 分隔线几何: `dividerMode` 默认为 `"content"`；divider 与正文/右侧操作共享 main 起点，天然避让内置左侧 addon；`"padding"` 仅保留为兼容别名并按 content 绘制；`"full"` 从根容器两端绘制；`"custom"` 使用 `dividerInsetStart` / `dividerInsetEnd`
- 标题: 16px / 21px, weight 500, `var(--harmony-font-primary)`
- 第二行: 14px / 19px, weight 400, `var(--harmony-font-secondary)`
- 第三行: 14px / 19px, weight 400, `var(--harmony-font-secondary)`
- 文本展示遵循仓库文字优先级：P0（权限名称、状态、数量、风险提示）必须完整展示；P1（说明文案）最多两行且行项/卡片高度随内容增长；P2（歌名、用户名、列表右侧辅助信息等）仅在 Pixso 设计稿或布局规格明确要求紧凑单行时才可 ellipsis。

### 文字优先级与行高

- 设置页的 `title`、涉及权限/状态/数量/风险的 `rightText` 属于 P0；不得放入会触发单行省略的固定宽度区域，空间不足时必须换行并增加行项高度。
- `subtitle`、`description` 默认属于 P1；最多两行，禁止 `white-space: nowrap`、`text-overflow: ellipsis` 或固定行高导致内容裁切。
- 仅业务已明确标记为 P2 的 `title`、`rightText` 或元信息可使用单行 ellipsis；“紧凑”本身不是充分理由，必须有 Pixso 设计稿或布局规格依据。
- 现有固定 `行数` 仅是基础视觉变体；当 P0/P1 内容无法完整显示时，生成页面必须选择或扩展可自适应高度的行项，不能以截断替代内容展示。

### 左侧变体

`left` 是对 `list-phone.json` 中 `left-1/left-2/left-3` 的兼容合并表达:

| JSON/Pixso 值 | Prop 表达 | 渲染 |
|---|---|---|
| `Text`, `默认` | `left="Text"` | 无独立 addon，仅文本区 |
| Pixso 截图圆点形态 | `left="Dot"` | 8px emphasize 圆点 |
| `8dp_ic`, `16dp_ic`, `24dp_ic`, `40dp_ic`, `48dp_ic` | 同名 prop | HM Symbol 图标或小尺寸圆标 |
| `badge`, `badge longest` | 同名 prop | 轻量内部 badge |
| `Switch` | 同名 prop | 复用 `SwitchPhone` |
| 无左侧 | `left="None"` | 无 addon |

### 右侧变体

`right` 同时保留旧导出值和 `list-phone.json` 中 Pixso 原始值。规范化后的渲染如下:

| right | 渲染 | 说明 |
|---|---|---|
| `Menu select` | `rightText` + downward chevron | 用于可展开/菜单选择 |
| `Text` | `rightText` | 纯值文本 |
| `Arrow` | optional `rightText` + right chevron | 右侧进入箭头；无 `rightText` 时仅箭头 |
| `Radio` | `RadioPhone` | `rightSelected`, `rightDisabled` 控制状态 |
| `Checkbox` | `CheckBox` | `rightSelected`, `rightDisabled` 控制状态 |
| `Switch` | `SwitchPhone` | `rightSelected`, `rightDisabled` 控制状态 |
| `Button` | `Button` | 使用仓库按钮 `尺寸="Small"`, `类型="Normal"` |
| `Expand` | 两行右侧文本 + down/up chevron | `rightSubtitle`, `rightExpanded` 控制 |
| `Icon`, `8dp_ic` | `Icon` with 1 HM Symbol | 兼容旧名和 Pixso 名；必须使用组件内置 icon 变体，禁止通过 `rightSlot` / `IconButton` 替换 |
| `2Icons` | `Icon` with 2 HM Symbols | Pixso `2Icons` |
| `image` | `img` or placeholder | 无通用图片组件时使用轻量内部实现 |
| `badge` | badge | 轻量内部 badge |
| `loading` | CSS spinner | 无独立 LoadingPhone 组件时使用轻量内部实现 |
| `None` | empty right region | 保持布局稳定 |

## Props 与 DSL 对照

| DSL/JSON 属性 | Prop 名 | 类型 | 默认值 | 说明 |
|---|---|---|---|---|
| `行数` | `行数` | `"1" \| "2" \| "3"` | `"1"` | 控制 DOM 文本行数和根高度；省略时等同 1 行 |
| `right` | `right` | `ListPhoneRightType` | `"Menu select"` | 右侧内容类型，含旧名和 Pixso 名别名 |
| `left-1/left-2/left-3` | `left` | 按 `行数` 收窄 | 1/2 行 `"Text"`，3 行 `"默认"` | 合并的左侧 addon 变体；先选 `行数`，再从 `listPhoneLeftOptionsByLines[行数]` 选择 |
| left text node | `title` | `ReactNode` | `"Single list"` | 标题 |
| second text node | `subtitle` | `ReactNode` | fallback `"Secondary text"` | 第二行，仅 `行数!="1"` |
| third text node | `description` | `ReactNode` | fallback `"Third line text"` | 第三行，仅 `行数="3"` |
| right text node | `rightText` | `ReactNode` | `undefined` | 右侧主文本；无业务状态值时不渲染占位文本。`right="Arrow"` 未传该 prop 时仅显示箭头 |
| right secondary text | `rightSubtitle` | `ReactNode` | `"More detail"` for Expand | 右侧第二行 |
| selected state | `rightSelected` | `"ON" \| "OFF" \| boolean` | `"ON"` | Radio/Checkbox/Switch 状态 |
| disabled state | `rightDisabled` | `boolean` | `false` | 右侧控件禁用 |
| expand state | `rightExpanded` | `boolean` | `false` | Expand chevron 方向 |
| badge text | `rightBadgeText`, `leftBadgeText` | `ReactNode` | `"New"`, `"1"` | Badge 文本 |
| image override | `rightImageSrc`, `rightImageAlt` | `string` | undefined, `""` | image 变体资源 |
| icon override | `rightIconGlyphs`, `leftIconName` | `HMSymbolIconName[]`, `HMSymbolIconName` | `gearshape/bookmark` | HM Symbol glyph；`right="Icon"` 仅接受此内置图标配置，不接受 `IconButton` |
| left icon style | `leftIconSize`, `leftIconColor`, `leftIconBackground`, `leftIconRadius` | `number`, `string`, `string`, `number \| string` | 见 CSS | 内置左侧 HM Symbol glyph 尺寸、颜色、容器背景和圆角修正；颜色/背景优先使用 Harmony token |
| custom left slot | `leftSlot` | `ReactNode` | `undefined` | 自定义左侧区域；替换 `left` 内置 addon，divider 仍跟随 main 内容区避让 |
| custom right slot | `rightSlot` | `ReactNode` | `undefined` | 自定义右侧区域；`right="Icon"` 时会被忽略，避免覆盖规定的内置 icon 变体 |
| divider | `divider` | `boolean` | `true` | 是否渲染底部 1px 分割线；多行列表最后一行传 `false` |
| divider mode | `dividerMode` | `"padding" \| "content" \| "full" \| "custom"` | `"content"` | 控制分割线起止协议；`"padding"` 为旧调用兼容别名，按 content 处理；页面模板带外部 icon / cover 时优先使用 `leftSlot` 纳入 main 几何，必要时再用 custom |
| divider inset start | `dividerInsetStart` | `number \| string` | undefined | 自定义分割线起点；number 自动转 px |
| divider inset end | `dividerInsetEnd` | `number \| string` | undefined | 自定义分割线终点；number 自动转 px |
| interaction | `onClick` | `() => void` | undefined | 根行点击；子控件 stopPropagation |
| style hook | `className` | `string` | undefined | 外部样式覆盖 |

## Divider 使用规则

| 场景 | 推荐配置 |
|---|---|
| 普通无左侧 addon 行 | 默认 `dividerMode="content"` |
| 使用 `left="24dp_ic"`、`left="48dp_ic"` 等内置左侧 addon | 默认 `dividerMode="content"` |
| 需要贯穿整行的分割线 | `dividerMode="full"` |
| 页面外层绘制 icon / cover | 优先改为 `leftSlot`，让 divider 继续归属 main；确需外部几何时使用 `dividerMode="custom"` |

禁止页面模板通过 `.list-phone__divider` 深选择器覆盖常规 divider 几何；应使用 props 或 CSS 变量表达 inset。

### Pixso divider 归属校准

Pixso `62:35191` 中 `List-Phone` 根节点左右 padding 为 12px，divider 不是整行独立元素，而是嵌在左侧文本组件与右侧操作组件内部:

| 变体 | 左组件内 divider 起点 | 根节点内绝对起点 |
|---|---:|---:|
| `left-1=Text` | 0px | 12px |
| `left-1=8dp_ic` | 20px | 32px |
| `left-1=24dp_ic` | 40px | 52px |
| `left-1=40dp_ic` | 56px | 68px |
| `left-1=48dp_ic` | 64px | 76px |

本地实现用外层 flex 分配 `leftAddon + main`，并由 `.list-phone__main::after` 绘制 divider，使 divider 与正文和右侧操作区域同属一个 main 容器；调用方不需要再按左侧图标宽度计算 divider 偏移。

## 样式引用

无新增全局 token。组件继续使用:

- `var(--harmony-font-primary)`, `var(--harmony-font-secondary)`
- `var(--harmony-icon-primary)`, `var(--harmony-icon-secondary)`, `var(--harmony-icon-fourth)`, `var(--harmony-icon-emphasize)`
- `var(--harmony-comp-background-secondary)`, `var(--harmony-comp-background-emphasize)`, `var(--harmony-comp-divider)`
- `var(--harmony-warning)`, `var(--harmony-font-on-primary)`
- `var(--harmony-interactive-hover)`, `var(--harmony-interactive-pressed)`, `var(--harmony-interactive-focus)`

## 复用来源

- `Radio` -> `src/components/RadioPhone/RadioPhone.tsx`
- `Checkbox` -> `src/components/CheckBox/CheckBox.tsx`
- `Switch` and left `Switch` -> `src/components/SwitchPhone/SwitchPhone.tsx`
- `Button` -> `src/components/Button/button.tsx`
- `Icon`, `2Icons`, `8dp_ic` -> 内置 `HMSymbolIcon`；`right="Icon"` 严禁嵌入或复用 `IconButton`
- `Arrow`, `Menu select`, `Expand`, image placeholder -> `HMSymbolIcon`

## Storybook 覆盖

- `Playground`: 单实例 Controls
- `Line Matrix`: `行数=1/2/3`
- `Right Variant Matrix`: 遍历 `listPhoneRightTypes`
- `Left Variant Matrix`: 遍历 `listPhoneLeftTypes`
- `Pixso Reference`: 按需求文档中的 Pixso 截图描述组合文本、圆点、icon、三行和主要右侧控件
- `Divider Inset Matrix`: 无 icon、24px icon、48px icon、自定义 inset 的 divider 起点对比
- `Dark Matrix`: dark token scope 下验证文本、图标和 divider token

## 测试覆盖

`src/components/Container/ListPhone/list-phone.test.tsx` 使用 server render 验证:

- `行数="1" | "2" | "3"` 的 `data-lines` 和文本行 DOM 差异
- `listPhoneRightTypes` 每个导出值都有 `data-right` 与 `data-right-kind`
- Radio/Checkbox/Switch 输出复用组件的 role 与 `aria-checked`
- 左侧 Dot/Icon 输出稳定 `data-list-phone-left-*`
- `dividerMode` 和 `dividerInsetStart` / `dividerInsetEnd` 输出稳定 data attribute 与 CSS 变量
- divider 由 `.list-phone__main::after` 绘制，不再渲染独立 `Divider` / `hm-divider` DOM

## 取舍说明

- 2026-07-22 重新接入 Pixso MCP：`62:35191` 已成功返回 DSL、截图和 design_to_code manifest。divider 归属修正为 main 容器伪元素，旧 `padding` 模式作为兼容别名保留但不再推荐。
- `Button` 组件当前不暴露自定义视觉 label，ListPhone 的 Button 变体复用仓库 Button 的默认 small label，并用 `aria-label` 继承 `rightText` 语义。
- `Badge`, `Loading`, `image` 未发现独立 Phone 组件，采用 ListPhone 内部轻量实现。
- `right="Icon"` 是封闭变体：调用方只能通过 `rightIconGlyphs` 选择其规定的 HM Symbol 图标，不能传入 `rightSlot`，更不能额外嵌套 `IconButton`；组件层会忽略该 `rightSlot` 组合以防止视觉回归。
- `rightText` 没有占位默认值。调用方只应在存在真实业务状态（如“已开启”“简体中文”）时传入；link/jump 行不传该 prop，避免出现“Right text”类伪状态。
