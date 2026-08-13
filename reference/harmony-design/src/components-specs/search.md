# Search 组件规格

## Metadata

| 字段 | 值 |
|------|-----|
| 实现目录 | `src/components/Search` |
| Stories 路径 | `src/components/Search/Search.stories.tsx` |
| Pixso 链接 | `https://pixso.cn/app/design/QeDttX-H4qVEUZXJjNfTCw?item-id=40:34230` |
| MCP 工具 | `get_node_dsl` |
| 变体树 JSON | `src/components/Search/search.json` |
| 变体树来源 | 从 `get_node_dsl` 返回的 `pixTreeNodes` 提取 |

## 组成与用途

Search 组件家族，包含 3 种类型的搜索 UI 组件。

### 组件类型

| 组件 | 尺寸 | 圆角 | 描述 |
|------|------|------|------|
| **Search** | 328×40 | 24px | 标准搜索框（phone 尺寸） |
| **Search2in1** | 240×40 | 8px | 紧凑双搜索框 |
| **SearchIconButton** | 40×40 | circle(1000px) / rounded(8px) | 图标按钮 |

## 量化规格

### Search (328×40)

| 参数 | OFF | ON Normal | ON Actived |
|------|-----|-----------|------------|
| 宽度 | 328px | 328px | 328px |
| 高度 | 40px | 40px | 40px |
| 圆角 | 24px | 24px | 24px |
| gap | 8px | 8px | 6px |
| padding (T/R/B/L) | 9/12/9/12 | 4/4/4/12 | 4/4/4/12 |
| 背景 | comp_background_tertiary rgba(0,0,0,0.047) | 同左 | 同左 |
| 文字 | "Search" 16px/22px Regular, font-secondary | 同左 | 同左 |
| 搜索图标 | 16×16, icon-primary | 同左 | 同左 |
| 操作按钮 | — | voice(18×18) + divider(1×12) + "Search" btn(14px, font-emphasize) | 同左 |

### Search2in1 (240×40)

| 参数 | OFF | ON Normal | ON Actived |
|------|-----|-----------|------------|
| 宽度 | 240px | 240px | 240px |
| 高度 | 40px | 40px | 40px |
| 圆角 | 8px | 8px | 8px |
| gap | 8px | 8px | 6px |
| padding (T/R/B/L) | 9/12/9/12 | 4/4/4/12 | 4/4/4/12 |
| 文字区域宽度 | 192px | 83px | 83px |

### SearchIconButton (40×40)

| 参数 | 值 |
|------|-----|
| 尺寸 | 40×40 |
| 圆角 | circle: 1000px, rounded: 8px |
| 背景 | comp_background_tertiary rgba(0,0,0,0.047) |
| 图标 | ArrowAppback 24×24, icon-primary |

## 状态与交互

### Search/Search2in1 状态

| 状态 | 效果 |
|------|------|
| Normal | 基础样式 |
| Hover | overlay: interactive-hover rgba(0,0,0,0.047) |
| Press | overlay: interactive-pressed rgba(0,0,0,0.098) |
| Focus | border: interactive-focus rgba(10,89,247,1) |
| Actived | border: transparent; gap 缩至 6px |
| Typing | 文字色变为 font-primary; 光标可见 |
| Output | 文字色变为 font-primary |
| icon hover | 搜索图标: icon-primary |
| icon focus | 搜索图标: interactive-focus |
| icon press | 搜索图标: interactive-active |

### 操作栏交互 (Search=ON)

| 元素 | hover | press |
|------|-------|-------|
| voice 按钮 | bg: interactive-hover | bg: interactive-pressed |
| Search 按钮 | bg: interactive-hover | bg: interactive-pressed |

### SearchIconButton 状态

| 状态 | 效果 |
|------|------|
| Default | 基础样式 |
| Hover | overlay: interactive-hover |
| Pressed | overlay: interactive-pressed |
| Focus | 2px focus ring (interactive-focus) |

## Props

### Search

| DSL 字段 | Prop 名 | 类型 | 默认值 | 取值 | 一致性 |
|----------|---------|------|--------|------|--------|
| Search | Search | `"OFF" \| "ON"` | `"OFF"` | `["OFF", "ON"]` | ✅ |
| 状态 | 状态 | `string` | `"Normal"` | 10 种状态 | ✅ |
| 通透度 | 通透度 | `string` | `undefined` | `["标准","强","降档","弱"]` | ✅ 向后兼容 |
| — | placeholder | `string` | `"搜索"` | — | 额外 |
| — | searchButtonText | `string` | `"Search"` | — | 额外 |
| — | value | `string` | `undefined` | — | 额外（受控输入） |
| — | onSearch | `(v: string) => void` | `undefined` | — | 额外 |

### Search2in1

| DSL 字段 | Prop 名 | 类型 | 默认值 | 取值 | 一致性 |
|----------|---------|------|--------|------|--------|
| Search | Search | `"OFF" \| "ON"` | `"OFF"` | `["OFF", "ON"]` | ✅ |
| 状态 | 状态 | `string` | `"Normal"` | 10 种状态 | ✅ |

### SearchIconButton

| DSL 字段 | Prop 名 | 类型 | 默认值 | 取值 | 一致性 |
|----------|---------|------|--------|------|--------|
| 状态 | 状态 | `string` | `"Default"` | `["Default","Hover","Pressed","Focus"]` | ✅ |
| 圆角 | 圆角 | `string` | `"circle"` | `["circle","rounded"]` | ✅ |

## 样式引用

### global.css Token

| Token | 用途 |
|-------|------|
| `--harmony-comp-background-tertiary` | 背景色 |
| `--harmony-font-secondary` | placeholder 文字 |
| `--harmony-font-primary` | Typing/Output 文字 |
| `--harmony-font-emphasize` | 搜索按钮文字 |
| `--harmony-icon-primary` | 搜索图标、语音图标 |
| `--harmony-interactive-hover` | hover overlay |
| `--harmony-interactive-pressed` | press overlay |
| `--harmony-interactive-focus` | focus border/ring |
| `--harmony-interactive-active` | icon press 色 |
| `--harmony-brand` | 光标颜色 |

### 新增全局 Token

无新增。

## 向后兼容性

- `Search` 组件导出路径不变：`@/components/Search/Search`
- 现有页面模板 (`mobile-grid-template`, `mobile-card-template`) 使用 `<Search placeholder={...} onClick={...} />`，新版完全兼容
- `通透度` prop 保留（向后兼容），但基础 DSL 不含此维度
- 旧 `searchOptions`、`stateOptions`、`transparencyOptions` 从 `search.constants.ts` 以新名称导出

## 取舍说明

1. **未使用 `get_screenshot`/`get_variants`**：用户要求只调用 `get_node_dsl`
2. **本地图标资源**：Search、Voice、SearchIconButton 分别使用 `magnifyingglass`（U+F0029）、`mic`（U+F0006）、`chevron_left`（U+F00DA）；原 Material 返回箭头与本地字形差异小，统一通过 `HMSymbolIcon` 渲染。
3. **voice/Search button hover/press**：DSL 中通过 Searchaction 内子组件 overlay 实现，已用 CSS hover/active 等效实现
4. **基础 Search 不含通透度**：基础 328×40 节点不含通透度维度；通透度变体已在 `FloatingSearchPhone` 组件实现
