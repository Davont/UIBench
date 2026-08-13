# DataPanelLinearGradient

## Metadata

- **实现目录**: `src/components/DataPanelLinearGradient/`
- **Stories 路径**: `src/components/DataPanelLinearGradient/data-panel-linear-gradient.stories.tsx`
- **Pixso 链接**: https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5413:111
- **item-id**: `5413:111`
- **MCP 工具来源**: `get_node_dsl` (成功), `get_screenshot` (成功), `get_export_image` (成功导出 PNG), `get_variants` (返回空 `{}`), `design_to_code` (成功，用于拉取 SVG 资源定位)
- **变体树 JSON**: `src/components/DataPanelLinearGradient/data-panel-linear-gradient.json`
  - 由 `get_node_dsl` 的 `pixComponentTreeDslNodes` 重建
  - `get_variants` 返回空，变体属性 `尺寸` 通过 DSL 中的 `componentNormName` 字段推断（`Small` / `Medium` / `Large`）

## 组成与用途

- **导出项**: `DataPanelLinearGradient` 组件, `DataPanelLinearGradientProps` 类型, 常量枚举 `dpLinearGradientSizes`
- **使用场景**: 存储空间使用率、数据加载进度等需要多彩渐变环形进度指示的场景
- **实现方式**: 基于 Pixso 导出的本地 SVG 资源绝对定位叠加，不再用圆环算法近似真实弧线轮廓

## 量化规格

### 尺寸 (3 个变体)

| 尺寸 | 容器 (px) | 圆环半径 (px) | 描边宽度 (px) | 值字号 (px) | 值行高 (px) |
|------|----------|--------------|--------------|------------|------------|
| Large | 288×288 | 114 | 24 | 60 | 80 |
| Medium | 136×136 | 55 | 18 | 36 | 48 |
| Small | 88×88 | 35 | 14 | — | — |

### 颜色与资源 (Pixso DSL 提取)

**四段线性渐变（顺时针从顶部起）：**

| 段位 | 渐变 ID | 起始色 | 结束色 |
|------|---------|--------|--------|
| 1 (黄) | dp-linear-yellow | `#FAD419` rgba(250,212,25,1) | `#FFAF38` rgba(255,175,56,1) |
| 2 (橙红) | dp-linear-orange | `#F8987B` rgba(248,152,123,1) | `#F5683D` rgba(245,104,61,1) |
| 3 (粉) | dp-linear-pink | `#ED8EB8` rgba(237,142,184,1) | `#E673A4` rgba(230,115,164,1) |
| 4 (紫) | dp-linear-purple | `#AE8BE0` rgba(174,139,224,1) | `#B66BED` rgba(182,107,237,1) |

**Large 发光弧角度渐变 (FOREGROUND_BLUR 13.59px)：**

| 偏移 | 颜色 |
|------|------|
| 33.47% | rgba(245,104,61,0.4) |
| 42.89% | rgba(230,115,164,0.4) |
| 47.88% | rgba(182,107,237,0.4) |
| 100% | rgba(255,175,56,0.4) |

**轨道圆环**: `rgba(0,0,0,0.047)` → `var(--harmony-comp-background-tertiary)`

**文字颜色**:
- 数值: `rgba(0,0,0,0.902)` → `var(--harmony-font-primary)`
- "%" 和副标题: `rgba(0,0,0,0.6)` → `var(--harmony-font-secondary)`

### Typography

| 元素 | 字体 | 字重 | 字号 | 行高 |
|------|------|------|------|------|
| 数值 (Large) | HarmonyHeiTi | 500 (Medium) | 60px | 80px |
| 数值 (Medium) | HarmonyHeiTi | 500 (Medium) | 36px | 48px |
| "%" 符号 | HarmonyHeiTi | 500 (Medium) | 16px | 22px |
| 副标题 (Large) | HarmonyHeiTi | 400 (Regular) | 14px | 20px |

### 资源文件

- `src/components/DataPanelLinearGradient/assets/Ellipse_1_12764.svg`
- `src/components/DataPanelLinearGradient/assets/Vector_1_12762.svg`
- `src/components/DataPanelLinearGradient/assets/Vector_1_12765.svg`
- `src/components/DataPanelLinearGradient/assets/Vector_1_12766.svg`
- `src/components/DataPanelLinearGradient/assets/Vector_1_12767.svg`
- `src/components/DataPanelLinearGradient/assets/Vector_1_12768.svg`
- `src/components/DataPanelLinearGradient/assets/Vector_1_12769.svg`
- `src/components/DataPanelLinearGradient/assets/Ellipse_1_13024.svg`
- `src/components/DataPanelLinearGradient/assets/Vector_1_13026.svg`
- `src/components/DataPanelLinearGradient/assets/Vector_1_13027.svg`
- `src/components/DataPanelLinearGradient/assets/Vector_1_13028.svg`
- `src/components/DataPanelLinearGradient/assets/Vector_1_13029.svg`
- `src/components/DataPanelLinearGradient/assets/Vector_1_13030.svg`
- `src/components/DataPanelLinearGradient/assets/Ellipse_1_13038.svg`
- `src/components/DataPanelLinearGradient/assets/Vector_1_13040.svg`
- `src/components/DataPanelLinearGradient/assets/Vector_1_13041.svg`
- `src/components/DataPanelLinearGradient/assets/Vector_1_13042.svg`
- `src/components/DataPanelLinearGradient/assets/Vector_1_13043.svg`
- `src/components/DataPanelLinearGradient/assets/Vector_1_13044.svg`

## 状态与交互

- **Default**: 静态进度展示
- 无 hover/active/disabled/focus 交互状态（纯展示组件）

## Props

| Prop | 类型 | 默认值 | DSL 来源 | 说明 |
|------|------|--------|----------|------|
| `尺寸` | `"Small" \| "Medium" \| "Large"` | `"Large"` | `componentNormName` (Small/Medium/Large) | 组件尺寸 |
| `进度` | `number \| string` | `75` | guid `1:12775` / `1:13034` 文本 "75" | 中心数值文本覆盖；当前不驱动弧线几何 |
| `副标题` | `string` | `"Used 98GB / 128GB"` | guid `1:12771` 文本 | 使用情况文字（仅 Large 显示） |

### DSL ↔ Prop 对照

| DSL 字段/节点 | Prop 名 | 可取值 | 备注 |
|---------------|---------|--------|------|
| `componentNormName` | `尺寸` | Small, Medium, Large | 直接对应，未翻译 |
| guid `1:12775` / `1:13034` nodeText `"75"` | `进度` | 任意数字或字符串 | 仅覆盖中心文案；Pixso 未提供可变弧长属性 |
| guid `1:12771` nodeText `"Used 98GB / 128GB"` | `副标题` | 任意字符串 | DSL 中为静态文本，实现为文案覆盖属性 |

## 样式引用

### 使用的全局 Token (`global.css`)

| Token | 用途 |
|-------|------|
| `--harmony-font-primary` | 数值文字颜色 |
| `--harmony-font-secondary` | "%" 和副标题颜色 |

### 新增全局 Token

本次未向 `global.css` 新增 Token。轨道、彩色弧线和发光弧均来自 Pixso 导出的本地 SVG 资源，与现有全局 Token 体系无冲突。

## 取舍说明

1. **`get_variants` 返回空**: 变体树 JSON 由 `get_node_dsl` 中的 `pixComponentTreeDslNodes` 重建，`variantOptions` 从 `componentNormName` 字段推断。
2. **真实矢量优先**: 为保证 1:1，还原已改为使用 Pixso 导出的本地 SVG 资源做绝对定位叠加，不再用圆弧算法近似各段轮廓。
3. **`进度` 的语义收敛**: 当前 Pixso 真值只覆盖固定的 75% 弧线状态，没有可变弧长属性；因此 `进度` 仅用于覆盖中心文案，未映射为动态弧线几何。
4. **Small 尺寸无文字**: 与 DSL 一致（Small 组件节点内无文本子节点）。
5. **Overview story**: 新增 `Overview` story，使用 `753 × 359` 白底画板复刻 Pixso 三尺寸排布，便于 Storybook 与设计稿做直接视觉对照。
