# ToolBar（工具栏）

## Metadata

- **实现目录**: `src/components/ToolBar`
- **Stories 路径**: `src/components/ToolBar/ToolBar.stories.tsx`
- **Pixso 链接**: `https://pixso.cn/app/design/cjiPj-NOUA9kxV0f1bJ_og?item-id=5323:23188`
- **Item ID**: `5323:23188`
- **MCP 工具来源**: `get_node_dsl` + `get_screenshot` + `design_to_code`
- **组件变体树 JSON**: `src/components/ToolBar/toolbar.json`

## 组件变体树 JSON

- **路径**: `src/components/ToolBar/toolbar.json`
- **`variantOptions`**:
  - `Land` ∈ {`OFF`, `ON`}
  - `个数` ∈ {`2`, `3`, `4`, `5`}
  - `状态` ∈ {`Enable`, `Activated`}
- **`pixTreeNodes`**: 记录 `ToolBar-Phone` 根组件及 `.Port` 子组件的变体实例树。
- **降级说明**: `get_variants` 返回空对象，因此由 `get_node_dsl` 实例树与 `design_to_code` 输出回填变体集合。

## 组成与用途

- **导出**: `ToolBar`、`toolbarLands`、`toolbarCounts`、`toolbarPortStates`
- **使用场景**: 手机端底部工具栏，含 2 到 5 个均分入口和底部手势条。

## 量化规格

### ToolBar-Phone 容器

| 参数 | Land=OFF | Land=ON | 来源 |
|------|----------|---------|------|
| 宽度 | 360px | 740px | `get_node_dsl` + `design_to_code` |
| 高度 | 76px | 76px | `get_node_dsl` |
| 上半区高度 | 48px | 48px | `get_node_dsl` |
| 下半区高度 | 28px | 28px | `get_node_dsl` |
| 背景 | `Light/Blur/COMPONENT_THICK` | `Light/Blur/COMPONENT_THICK` | `localStyleMap 616:9106` |
| 背景模糊 | 18.121866861979168px | 18.121866861979168px | `design_to_code` |

### 工具项 `.Port`

| 参数 | 值 | 来源 |
|------|----|------|
| 高度 | 48px | `get_node_dsl` |
| 布局 | 垂直居中，gap=2，padding=4 | `get_node_dsl.autoLayout` |
| 图标尺寸 | 24×24px | `get_node_dsl` |
| 文案 | `Action` | `get_node_dsl.nodeText` |
| 字号 | 10px | `Font/Caption_M/Medium` |
| 字重 | Medium | `Font/Caption_M/Medium` |
| 行高 | 14px | 文本层高度 |

### 项宽度（按 `个数` 均分）

| Land | `个数=2` | `个数=3` | `个数=4` | `个数=5` |
|------|----------|----------|----------|----------|
| `OFF` | 180px | 120px | 90px | 72px |
| `ON` | 370px | 246.6667px | 185px | 148px |

### 手势条

| 参数 | Land=OFF | Land=ON | 来源 |
|------|----------|---------|------|
| 外层尺寸 | 360×28px | 740×28px | `get_node_dsl` |
| Pill 宽度 | 112px | 230.222229px | `get_node_dsl` |
| Pill 高度 | 5px | 5px | `get_node_dsl` |
| Pill 顶部偏移 | 17px | 17px | `get_node_dsl` |
| 圆角 | 4px | 4px | `get_node_dsl` |

## 颜色映射

| Pixso Style | 全局 Token |
|-------------|------------|
| `Light/Blur/COMPONENT_THICK` | `--COMPONENT_THICK_fill` |
| `Light/font_primary` | `--harmony-font-primary` |
| `Light/font_emphasize` | `--harmony-font-emphasize` |
| `Light/icon_primary` | `--harmony-icon-primary` |
| `Light/icon_emphasize` | `--harmony-icon-emphasize` |

## Props

### DSL ↔ Prop 对照

| DSL 字段 | Prop 名 | 类型 | 默认值 | 可取值 |
|----------|---------|------|--------|--------|
| `Land` | `Land` | `ToolbarLand` | `"OFF"` | `"OFF" \| "ON"` |
| `个数` | `个数` | `ToolbarCount` | `"2"` | `"2" \| "3" \| "4" \| "5"` |

### 扩展 Props

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `items` | `ToolbarItem[]` | 按设计稿默认矩阵生成 | 允许覆盖标签、图标与激活态 |
| `selectedIndex` | `number` | 非受控时取 `defaultSelectedIndex` | 当前选中项索引（0-based），可通过 `items[selectedIndex]` 获得具体项；传入后进入受控模式，解析值同步输出到根节点 `data-selected-index` |
| `defaultSelectedIndex` | `number` | 设计稿默认激活位 | 非受控模式的初始选中项索引 |
| `onSelectedIndexChange` | `(index: number) => void` | — | 用户选择某一项时返回其索引 |
| `onActiveChange` | `(index: number) => void` | — | 已弃用的兼容回调，请使用 `onSelectedIndexChange` |
| `className` | `string` | — | 附加类名 |

## 状态与交互

- 根组件只直接暴露 `Land` 与 `个数` 两个 DSL 变体轴。
- `.Port` 有两种视觉状态：`Enable` 与 `Activated`。
- 默认激活位严格按设计稿矩阵复现：
  - `Land=OFF`: `2/3` 项时激活最后一项，`4/5` 项时激活第二项
  - `Land=ON`: 始终激活最后一项

## 样式引用

- **使用全局 Token**: `--COMPONENT_THICK_fill`, `--harmony-font-primary`, `--harmony-font-emphasize`, `--harmony-icon-primary`, `--harmony-icon-emphasize`
- **新增全局 Token**: 无
- **依赖组件**: 无（手势条已内联，避免现有 `Aibottombar` 的命名冲突影响 Storybook 预览）

## 校验结论

- 原 Storybook `Component/ToolBar` 与当前 Pixso 节点不符：原实现是富文本编辑工具条，不是 `ToolBar-Phone`。
- 当前实现与截图矩阵已对齐为 `Land × 个数` 两列四行布局，宽度、激活位、手势条尺寸均按设计稿重建。
- 自动 SSIM 未执行：仓库缺少 `pngjs` 依赖，当前采用 Pixso 截图与 Storybook 截图人工复核。
