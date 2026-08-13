# Counter

## Metadata

| 字段 | 值 |
|------|-----|
| 实现目录 | `src/components/Counter/` |
| Stories 路径 | `src/components/Counter/counter.stories.tsx` |
| Pixso 链接 | `https://pixso.cn/app/design/HA_e8I2mE7Oa0b5ZoeokSA?item-id=5314:19754` |
| Pixso item-id | `5314:19754` |
| MCP 工具来源 | `get_node_dsl` + `get_screenshot` + `design_to_code` |

## 组件变体树 JSON

- 路径：`src/components/Counter/counter.json`
- 生成方式：基于 `get_node_dsl` DSL 结构重建（`get_variants` 返回空对象 `{}`）
- `variantOptions.类型`：`["default", "Text below", "Up and down"]`
- `pixTreeNodes` 包含 3 个变体节点，guid 分别对应 `1:9856`、`1:9827`、`1:9807`

## 组成与用途

| 导出项 | 说明 |
|--------|------|
| `Counter` | 计数器组件，支持 3 种布局变体 |
| `counterTypes` | `["default", "Text below", "Up and down"]` 枚举常量 |
| `CounterProps` | Props 类型接口 |
| `CounterType` | `类型` prop 的联合类型 |

使用场景：数量选择、步进输入、购物车数量调整。

## 量化规格

### 通用

| 属性 | 值 | 来源 |
|------|-----|------|
| 字体 | HarmonyHeiTi Medium 16px | Pixso Text Style `602:9659` (Font/Body_L/Medium) |
| 文字颜色 | `rgba(0,0,0,0.898)` → `--harmony-font-primary` | Pixso Fill Style `602:9446` |
| 图标颜色 | `rgba(0,0,0,0.898)` → `--harmony-icon-primary` | Pixso Fill Style `602:9459` |
| 按钮背景 | `rgba(0,0,0,0.047)` → `--harmony-comp-background-tertiary` | Pixso Fill Style `602:9420` |
| 边框/分割线 | `rgba(0,0,0,0.098)` → `--harmony-comp-background-secondary` | Pixso Fill Style `602:9419` |
| 底部分割线 | `rgba(0,0,0,0.2)` → `--harmony-comp-divider` | Pixso Fill Style `602:9422` |

### 变体 default（`1:9856`）

| 属性 | 值 |
|------|-----|
| 整体尺寸 | 360×48px（最小宽度 360px） |
| 布局 | Horizontal flex，gap 18px，padding 0 24px |
| 标签区域 | flex 1，padding 13px 0，底部分割线 0.5px |
| 步进器 | gap 8px，minus(32px) + value(40px) + plus(32px) |
| 图标按钮 | 32×32px，border-radius 800px |

### 变体 Text below（`1:9827`）

| 属性 | 值 |
|------|-----|
| 布局 | Vertical flex，gap 8px，居中对齐 |
| 计数器胶囊 | padding 2px，border-radius 16px，border 1px |
| 胶囊内容 | gap 10px，minus(28px) + value(40px) + plus(28px) |
| 图标按钮 | 28×28px，border-radius 700px |
| 标签 | 居中文本，16px，line-height 22px |

### 变体 Up and down（`1:9807`）

| 属性 | 值 |
|------|-----|
| 布局 | Horizontal flex，gap 12px |
| 计数框 | height 32px，padding-left 12px，border-radius 8px，border 1px |
| 数值区域 | min-width 66px |
| 箭头区域 | 32×30px，border-left 1px，内含 up/down 箭头（24×12px each）+ 中间分割线 1px |
| 箭头间隔 | gap 1.5px，padding 1px |

## 状态与交互

| 状态 | 表现 |
|------|------|
| default | 正常显示，按钮可交互 |
| hover（按钮） | 背景色切换为 `--harmony-interactive-hover` |
| active/pressed（按钮） | 背景色切换为 `--harmony-interactive-pressed` |
| disabled | 整体 pointer-events: none，文字和值 opacity 0.4，按钮 cursor not-allowed + opacity 0.4 |
| 边界 min | 减按钮 disabled，不可继续减少 |
| 边界 max | 加按钮 disabled，不可继续增加 |

## Props

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `类型` | `"default" \| "Text below" \| "Up and down"` | `"default"` | 计数器布局变体 |
| `value` | `number` | `999` | 当前数值 |
| `label` | `string` | `"Quantity"` | 标签文本 |
| `min` | `number` | `0` | 最小值 |
| `max` | `number` | `999` | 最大值 |
| `step` | `number` | `1` | 步长 |
| `onChange` | `(value: number) => void` | — | 数值变化回调 |
| `disabled` | `boolean` | `false` | 禁用所有交互 |
| `className` | `string` | — | 额外 CSS 类名 |

### DSL ↔ Prop 对照

| DSL 字段/键名 | Prop 名 | 取值一致性 |
|--------------|---------|-----------|
| `类型` (组件变体属性) | `类型` | ✅ 一致：`default` / `Text below` / `Up and down` |
| `nodeText: "999"` (默认文本) | `value` (default) | ✅ 一致 |
| `nodeText: "Quantity"` (默认标签) | `label` (default) | ✅ 一致 |

## 样式引用

### 使用的 `global.css` 变量

| CSS 变量 | 用途 |
|----------|------|
| `--harmony-font-primary` | 文字颜色 |
| `--harmony-icon-primary` | 图标颜色 |
| `--harmony-comp-background-tertiary` | 圆形按钮背景 |
| `--harmony-comp-background-secondary` | 边框/分割线 |
| `--harmony-comp-divider` | default 变体底部分割线 |
| `--harmony-interactive-hover` | 按钮 hover 背景 |
| `--harmony-interactive-pressed` | 按钮 active 背景 |

所有变量均为 `global.css` 已有 Token，本次无需新增。

## 取舍说明

- **HM Symbol 图标字体**: Pixso DSL 已确认六个操作图标使用 `fontFamily: "HM Symbol"`。在原始 `nodeText` 缺失的情况下，按语义检索本地 `hmsymbol-map.json`，统一通过 `HMSymbolIcon` 渲染：`plus`（U+F0035）、`minus`（U+F002C）、`chevron_up`（U+F00D8）、`chevron_down`（U+F00DB）、`chevron_left`（U+F00DA）、`chevron_right`（U+F00D9）。
- **`get_variants` 返回空**: 变体树基于 `get_node_dsl` 结构重建。3 个变体直接来自 DSL 顶层 `childNode` 中的 `类型=default`、`类型=Text below`、`类型=Up and down` 三个 INSTANCE 节点。
- **default 变体宽度**: DSL 中 `1:9856` 宽度为 360px，组件中设为 `min-width: 360px` 以支持内容自适应。
