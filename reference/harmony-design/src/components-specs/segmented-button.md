# SegmentedButton 分段按钮

## Metadata

- 实现目录：`src/components/SegmentedButton/`
- Stories 路径：`src/components/SegmentedButton/segmented-button.stories.tsx`
- Pixso 链接：`https://pixso.cn/app/design/QeDttX-H4qVEUZXJjNfTCw?item-id=594:14854`
- item-id：`594:14854`
- MCP 工具来源：`get_node_dsl`（成功）、`get_variants`（返回 `{}`，降级重建）

## 组件变体树 JSON

- 路径：`src/components/SegmentedButton/segmented-button.json`
- 生成方式：`get_node_dsl` item `594:14854` 的 `pixTreeNodes` + `pixComponentTreeDslNodes` 交叉验证

## 组成与用途

| 组件 | 文件 | 用途 |
|------|------|------|
| `SegmentedButton` | `segmented-button.tsx` | 主组件，支持单选/多选模式 |
| `SegmentedButtonItemInternal` | `segmented-button.tsx` | 内部子项（可选 icon + label） |

子图层对应：
- `.Items`（单选模式子项）→ 状态：Enable / activated / Selected
- `.Multi selection`（多选模式子项）→ 位置：Left / Mid / Right × 状态：Enabled / Selected

## 量化规格

### 单选容器（Multi selection=OFF）

| 属性 | 组数=2,3,5 | 组数=4 |
|------|-----------|--------|
| 容器尺寸 | Icon=on: 328×60；Icon=off: 328×40 | Icon=on: 328×64；Icon=off: 328×40 |
| 容器 cr | 8px | 20px |
| 容器 fill | `comp_background_tertiary` rgba(0,0,0,0.047) | 同左 |
| padding | 2px | 2px |
| 子项尺寸 | 72×56 | 72×60 |
| 子项 cr | 6px | 6px |
| 子项 padding | 4px 12px | 6px 12px |

### 多选容器（Multi selection=ON）

| 属性 | 所有组数 |
|------|---------|
| 容器尺寸 | Icon=on: 328×64；Icon=off: 328×40 |
| 容器 cr | 20px |
| 容器 fill | transparent |
| padding | 0 |
| gap | 1px |
| 子项尺寸 | 80×64 |
| 子项 cr | 0（无圆角） |
| 子项 padding | 8px 12px |

### 子项状态

| 状态 | 模式 | 背景 | 文字 | 阴影 |
|------|------|------|------|------|
| Enable | OFF | transparent | `font_secondary` rgba(0,0,0,0.6) | — |
| activated | OFF | `comp_background_primary_contrary` white | `font_primary` rgba(0,0,0,0.9) | DROP_SHADOW r=3 |
| Selected | OFF | `comp_background_emphasize` brand | `font_on_primary` white | DROP_SHADOW r=3 |
| Enabled | ON | `comp_background_tertiary` rgba(0,0,0,0.047) | `font_secondary` rgba(0,0,0,0.6) | — |
| Selected | ON | `comp_background_emphasize` brand | `font_on_primary` white | — |

### 共用
- Icon (.highlight)：24×24px
- Icon 默认隐藏；`Icon="on"` 时显示，`Icon="off"` 时隐藏
- `Icon="off"` 时整体高度为 40px
- Label：`Font/Body_M/Medium` — fs=14px, fw=500, lh=20px, HarmonyHeiTi
- 子项内部 gap：4px（VERTICAL）
- 字体：HarmonyHeiTi, Geist Variable, sans-serif

## Props DSL ↔ Prop 对照

| DSL 字段 | Prop 名 | 取值 | 默认值 | 说明 |
|----------|---------|------|--------|------|
| Multi selection | multiSelection | "ON" / "OFF" | "OFF" | JSX 不支持空格 |
| — | Icon | "on" / "off" | "off" | 控制子项图标可见性 |
| 组数 | 组数 | 2 / 3 / 4 / 5 | 3 | 直接对齐 DSL |
| — | items | SegmentedButtonItem[] | 由组数生成 | 业务数据 |
| — | selectedIndex | number | 0 | 单选模式选中索引 |
| — | selectedIndices | number[] | [] | 多选模式选中索引 |
| — | onSelect | (index: number) => void | — | 单选回调 |
| — | onMultiSelect | (indices: number[]) => void | — | 多选回调 |
| 状态 | 状态 | Enable / activated / Selected | — | 内部子项使用 |
| 位置 | 位置 | Left / Mid / Right | — | 内部子项使用 |

### 命名映射说明
- DSL `Multi selection` → Prop `multiSelection`：因 JSX 语法限制，prop 名不可包含空格

## 样式引用

### 使用的 global.css 变量
- `--harmony-comp-background-tertiary` — 容器背景 / ON 子项背景
- `--harmony-comp-background-primary-contrary` — 保留但未在 SegmentedButton 中使用
- `--harmony-comp-background-primary-contrary-secondary` — OFF activated 子项背景（浅色 `#FFFFFF`，深色 `#666666`）
- `--harmony-comp-background-emphasize` — Selected 子项蓝底
- `--harmony-font-secondary` — Enable 子项文字
- `--harmony-font-primary` — activated 子项文字
- `--harmony-font-on-primary` — Selected 子项文字（白）

### 新增 CSS
- `segmented-button.css`（组件目录内），无新增全局 Token

## 取舍说明

1. `get_variants` 返回 `{}`，变体树由 `get_node_dsl` + `pixComponentTreeDslNodes` 交叉重建
2. DSL `Multi selection` prop 映射为 `multiSelection`，因 JSX 不支持带空格的 prop 名
3. DSL 中子项宽度为 FIXED（72px/80px），但实际使用 `flex: 1` 等分容器空间（视觉一致）
4. ON 模式子项无 border-radius（DSL cr=null），与旧版 20px 圆角不同
5. 组件未直接包含 `.highlight` 子组件，icon 通过 `icon` prop 传入 ReactNode
6. `activated` 状态（单选白底选中态）通过 `selectedIndex` 自动推导
