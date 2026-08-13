# Menu

## Metadata

| Field | Value |
|-------|-------|
| 实现目录 | `src/components/Menu` |
| Stories | `src/components/Menu/menu.stories.tsx` |
| Pixso 来源 | `https://pixso.cn/app/design/QeDttX-H4qVEUZXJjNfTCw?item-id=18:36032` |
| item-id | `18:36032` |
| MCP 工具 | `get_node_dsl` |
| 组件变体 JSON | `src/components/Menu/menu.json` |
| JSON 生成方式 | `get_node_dsl` → 65 pixComponentTreeDslNodes 解析 |

## MCP Result And Fallback

- `get_node_dsl`: success, 349K chars, 65 pixComponentTreeDslNodes
- Root: SECTION `3.Menu - 菜单` (18:36032) 4095×2181

## 组成与用途

菜单组件系统，覆盖 DSL 全部组件家族:

| 家族 | GUID | 尺寸 | 圆角 | 说明 |
|------|------|------|------|------|
| **Menu-Phone** | 21:36xxx | 344×N | r=20 | 浮动毛玻璃容器 |
| **Menu-2in1** | 320:12382~12392 | 224×N | r=8 | PC 标准容器 |
| **.single line** | 320:12345~12366 | 216×40 | — | PC 单项(5种类型) |
| **.Primary list** | 1:9552~1:9568 | 192×48 | — | Phone 单项(3种状态) |
| **.Primary Group** | 20:35966~35998 | 192×N | — | Phone 项目组(含标题) |
| **items** | 320:12369~17024 | 216×N | — | PC 项目列表(gap=2) |
| **.bg** | 2831:10255~10259 | 216×40 | r=4 | PC 交互背景(4态) |
| **.Title** | 1:9548 | 192×48 | — | 标题行(Bold 18px) |
| **.Secondary list** | 1:9578 | 192×48 | — | Phone 文本行(Regular 16px) |
| **.Divider** | 320:12395 | 192×0.5 | — | 分割线 |
| **位置** | 331:13303~13325 | 224×174 | r=8 | 浮动定位(12方位) |

## Variant Tree

- `variantOptions`:
  - 菜单类型: `["Text with icon", "Text with subtitle", "subMenu", "PopupMenu"]`
  - 类型: `["Normal", "selected", "right element", "with select", "List title"]`
  - 状态: `["collapse", "commence", "selected"]`
  - 组数: `["1", "2", "3", "4", "5", "6"]`
  - items: `["1", "2", "3", "4", "5", "6"]`
  - 属性 1: `["normal", "hover", "click", "focus"]`
  - 通透度: `["标准", "高", "降档", "弱"]`
  - 位置: 12 方位
- Variant JSON: `src/components/Menu/menu.json`

## 量化规格

### Menu-Phone 容器 (21:36xxx)

| 属性 | DSL 值 |
|------|--------|
| Width | 344px |
| Corner radius | 20px |
| Fill | rgba(255,255,255,0.9) [616:9117] |
| BACKGROUND_BLUR | radius=54.37 |
| DROP_SHADOW | 0 0 60px rgba(0,0,0,0.2) |
| Padding | T=4, B=4, L=16, R=16 |
| Counter align | center (items 居中) |
| Layout | VERTICAL |

### Menu-2in1 容器 (320:12382~12392)

| 属性 | Text with icon | Text with subtitle | subMenu | PopupMenu |
|------|---------------|-------------------|---------|-----------|
| Width | 224px | 224px | 444px | 224px |
| Height | 174px | 172px | 221px | 174px |
| Corner radius | 8px | 8px | — | 8px |
| Stroke | 1px OUTSIDE rgba(0,0,0,0.1) | same | — | — |
| Shadow | 0 0 16px rgba(0,0,0,0.2) | same | — | — |
| Inner padding | T4 B4 L4 R4 | same | — | same |
| Items gap | 2px | 2px | — | 2px |

### .single line (320:12345~12366) — 216×40

| 类型 | Gap | Padding | Label | Trailing |
|------|-----|---------|-------|----------|
| Normal | 8px | L12 R12 | Medium 16px/22px | .Arrow-right |
| selected | 8px | L12 R12 | Medium 16px/22px | .ok (emphasize) |
| right element | 8px | T8 B8 L12 R12 | Medium 16px/22px | shortcut + .Arrow-right |
| with select | 8px | T8 B8 L12 R12 | Medium 16px/22px | shortcut + .ok |
| List title | 10px | T13 B8 L12 R56 | Medium 12px/19px, rgba(0,0,0,0.6) | — |

### .Primary list (1:9552~1:9568) — 192×48

| 属性 | DSL 值 |
|------|--------|
| Size | 192×48 |
| Layout | HORIZONTAL, gap=8 |
| Padding | T12 B12 |
| Label | Medium 16px/21px [602:9689] |
| Fill | rgba(0,0,0,0.898) [602:9446] |
| collapse | .highlight + label + .Arrow-right |
| commence | .highlight + label + .Arrow-bottom |
| selected | .highlight + label + .ok |

### .bg 交互状态 (2831:10255~10259) — 216×40, r=4

| 属性 1 | Fill | Stroke |
|--------|------|--------|
| normal | transparent | — |
| hover | rgba(0,0,0,0.047) [602:9466] | — |
| click | rgba(0,0,0,0.098) [602:9464] | — |
| focus | transparent | 1px INSIDE rgba(10,89,247,1) [602:9465] |

### .Title (1:9548) — 192×48

| 属性 | DSL 值 |
|------|--------|
| Size | 192×48 |
| Layout | HORIZONTAL, pad T12 B12 |
| Font | Bold 18px/24px [602:9687] |
| Fill | rgba(0,0,0,0.898) [602:9446] |

### .Secondary list (1:9578) — 192×48

| 属性 | DSL 值 |
|------|--------|
| Size | 192×48 |
| Layout | HORIZONTAL, gap=18, pad T13 B13 L8 |
| Font | Regular 16px/21px [602:9658] |
| Fill | rgba(0,0,0,0.898) [602:9446] |

### .Divider (320:12395)

| 属性 | DSL 值 |
|------|--------|
| Vector | 192×0.5px |
| Fill | rgba(0,0,0,0.2) [602:9420] |

## Props

| Prop | 类型 | 默认值 | DSL 来源 |
|------|------|--------|----------|
| `外观` | `"手机" \| "PC"` | `"手机"` | Menu-Phone vs Menu-2in1 |
| `菜单类型` | `MenuType` | `"Text with icon"` | 320:12382~12392 |
| `items` | `MenuGroup[]` | 默认数据 | 业务接口 |
| `浮动` | `boolean` | `false` | 位置 variants |
| `通透度` | `MenuTransparency` | `"标准"` | 通透度= |

### MenuItem 属性

| Prop | 类型 | DSL 来源 |
|------|------|----------|
| `label` | `string` | 文本内容 |
| `icon` | `ReactNode` | .highlight (24×24) |
| `状态` | `"collapse" \| "commence" \| "selected"` | .Primary list (1:9552~1:9568) |
| `类型` | `MenuItemType` | .single line (320:12345~12366) |
| `subtitle` | `string` | Text with subtitle 模式 |
| `shortcut` | `string` | right element / with select |
| `disabled` | `boolean` | 交互控制 |

### DSL ↔ Prop 对照

| DSL 字段 | Prop | 一致性 |
|----------|------|--------|
| 菜单类型=X | `菜单类型` | ✅ 完全一致 |
| 类型=X | `MenuItem.类型` | ✅ 完全一致 |
| 状态=X | `MenuItem.状态` | ✅ 完全一致 |
| 属性 1=X | CSS 伪类 | normal→default, hover→:hover, click→:active, focus→:focus-visible |
| 组数=X | items 数组长度 | 间接对应 |

## 样式引用

| Token | 用途 |
|-------|------|
| `--harmony-comp-background-primary` | PC 标准模式背景 |
| `--harmony-font-primary` | 文本颜色 fallback |

其余色值直接使用 DSL 原始 rgba 值以确保 1:1 还原。

## 取舍说明

1. **subMenu 双列布局**: DSL 320:12387 为 444×221 双列结构，当前仅设容器宽度 444px
2. **浮动高度**: DSL 21:36xxx 容器高度为固定值 (224~464px)，实现使用内容自适应
3. **Phone 单项 divider**: DSL 中 Divider-Phone 在文本画板内绝对定位，实现使用 absolute bottom
