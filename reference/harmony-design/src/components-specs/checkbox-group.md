# CheckboxGroup

## Metadata

| 字段 | 值 |
|------|-----|
| 实现目录 | `src/components/CheckboxGroup/` |
| Stories 路径 | `src/components/CheckboxGroup/CheckboxGroup.stories.tsx` |
| Pixso 链接 | `https://pixso.cn/app/design/HA_e8I2mE7Oa0b5ZoeokSA?item-id=5309:19534` |
| MCP 工具来源 | `get_node_dsl` (item-id 5309:19534) |

## 组件变体树 JSON

| 字段 | 值 |
|------|-----|
| 路径 | `src/components/CheckboxGroup/checkbox-group.json` |
| 生成方式 | 从 `get_node_dsl` 的 `pixTreeNodes` 与 INSTANCE `componentNormName` 字段提取组合 |
| 是否由 `get_variants` 直接得到 | 否（`get_variants` 返回 `{}`），基于 DSL 节点树重建 |

## 组成与用途

- **导出项**：`CheckboxGroup` 组件、`checkboxGroupHyperlinks` / `checkboxGroupStates` 枚举常量、相关 TypeScript 类型
- **使用场景**：多选列表；带超链接操作的复选框组（如协议确认、通知设置）
- **内部复用**：`CheckBox` 组件（`src/components/CheckBox/`）作为每行的勾选控件

## 量化规格

### 单行尺寸（DSL INSTANCE 328×48）
| 属性 | 值 | 来源 |
|------|-----|------|
| 行宽 | 328px | DSL width |
| 行高 | 48px | DSL height |
| 上/下内边距 | 12px | DSL autoLayoutPaddingTop/Bottom |
| CheckBox 与文本间距 | 12px | DSL autoLayoutItemSpacing |
| 圆角 | 8px | DSL cornerRadius |

### CheckBox（24×24，复用现有组件，固定 phone 圆形）
| 属性 | 值 |
|------|-----|
| 类型 | "phone" — 圆形：外 radius 12px，内 radius 10px |

### 排版
| 属性 | 值 | DSL 来源 |
|------|-----|----------|
| fontFamily | HarmonyHeiTi | DSL fontFamily |
| fontSize | 14px | DSL fontSize，对应 `--harmony-font-size-body-m` |
| fontWeight | 400 (Regular) | DSL fontStyle |
| lineHeight | 19px | 行内文本自然高度 |
| textAlignVertical | middle | DSL textAlignVertical |

### 色值（Light 主题）
| 语义 | 变量 | 色值 | DSL 来源 |
|------|------|------|----------|
| 主文本色 | `--harmony-font-primary` | rgba(0,0,0,0.898) | Light/font_primary |
| 强调色（超链接） | `--harmony-font-emphasize` | rgba(10,89,247,1) | Light/font_emphasize |
| Hover 背景 | `--harmony-comp-background-tertiary` | rgba(0,0,0,0.047) | Light/comp_background_tertiary |
| Pressed 背景 | `--harmony-interactive-click` | rgba(0,0,0,0.098) | Light/interactive_click |
| Focus 边框 | `--harmony-interactive-focus` | rgba(10,89,247,1) | Light/interactive_focus |
| CheckBox 填充（ON） | `--harmony-comp-background-emphasize` | rgba(10,89,247,1) | Light/comp_background_emphasize |

## 状态与交互

| 状态 | 行外观 | 触发条件 |
|------|--------|----------|
| Default | 透明背景、无边框 | 初始/空闲 |
| Hover | 背景 `--harmony-comp-background-tertiary` | 鼠标悬停 |
| Pressed | 背景 `--harmony-interactive-click` | 鼠标按下 |
| Focus | 2px 内边框 `--harmony-interactive-focus`，超链接文字带 pill 框 | 键盘聚焦 |

| 禁用状态 | 整体 opacity 40%，指针事件禁用 |
|-----------|------|

## Props

### 核心类型签名

```ts
interface CheckboxGroupItem {
  标签: string
  值: string
  超链接?: string   // undefined → Hyperlink=OFF; string → Hyperlink=ON
  选中?: boolean
  禁用?: boolean
}

interface CheckboxGroupProps {
  选项: CheckboxGroupItem[]
  状态?: "Default" | "Hover" | "Pressed" | "Focus"
  选中变更?: (项: CheckboxGroupItem, 已选: boolean) => void
  超链接点击?: (项: CheckboxGroupItem) => void
  className?: string
}
```

### DSL ↔ Prop 对照

| DSL 字段/属性 | Prop 名 | 取值 | 说明 |
|---------------|---------|------|------|
| INSTANCE `Hyperlink` | `超链接?: string` | undefined 或 string | undefined = OFF，有值 = ON；命名字段差异因为 `Hyperlink` 在 JSX 中为保留字；取值语义完全对应 |
| INSTANCE `状态` | `状态` | "Default" \| "Hover" \| "Pressed" \| "Focus" | 完全对齐，直接使用原始属性名 |
| `🔤Text` 节点 | `标签` | string | 主文本内容 |
| 超链接 `🔤Text` | `超链接` | string | 右侧蓝色链接文本 |

## 样式引用

### 使用的 `global.css` / `src/styles` 变量

| 变量 | 用途 |
|------|------|
| `--harmony-font-primary` | 主标签文本色 |
| `--harmony-font-emphasize` | 超链接文本色 |
| `--harmony-comp-background-tertiary` | Hover 状态行背景 |
| `--harmony-interactive-click` | Pressed 状态行背景 |
| `--harmony-interactive-focus` | Focus 状态边框色 |
| `--harmony-comp-background-emphasize` | 透传至内部 CheckBox 的 ON 态填充 |

### 新增写入 `global.css` 的全局 Token

无。所有色值和字体均已由现有 `global.css` Token 覆盖。

## 取舍说明

- 组件 Props 使用中文属性名以保持与 Pixso DSL 一致性；`Hyperlink` 字段因 JSX 保留字冲突，改用 `超链接?: string`（undefined=OFF, string=ON），语义保持完全对应，在规格中已注明映射关系。
- 行级 `padding-left` / `padding-right` 设为 0，与 DSL 表现一致（DSL 实例未明确设定水平内边距）。
- `get_variants` 返回空对象，变体树完全基于 `get_node_dsl` 的 `pixTreeNodes` / `pixComponentTreeDslNodes` 重建。
- Hyperlink=ON + Focus 状态下的超链接 pill 框：DSL 中该子节点有 strokeWeight:2, cornerRadius:3, padding 1.5/2，实现使用 `ring-2` + `rounded-[3px]` + `px-0.5 py-[1.5px]` 近似还原。
