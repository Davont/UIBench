# IconButton

## Metadata

- **实现目录**: `src/components/IconButton/`
- **Stories 路径**: `src/components/IconButton/IconButton.stories.tsx`
- **Pixso 链接**: `https://pixso.cn/app/design/cjiPj-NOUA9kxV0f1bJ_og?item-id=5320:24214`
- **MCP 工具来源**: `get_node_dsl` (Success), `get_screenshot` (Success), `get_variants` (Failed — 返回 `{}`), `design_to_code` (Failed — 500)

## 组件变体树 JSON

- **路径**: `src/components/IconButton/icon-button.json`
- **生成方式**: `get_variants` 返回空对象 `{}`，变体选项与树结构从 `get_node_dsl`、`get_all_components` 和截图矩阵重建
- **MCP 调用**: `get_node_dsl` (itemId=`5320:24214`), `get_all_components`
- **说明**: Pixso 仅直接暴露了 `材质-标准` 的 3 个画布实例、`材质-强` 的 3 图标组件变体节点与 `材质-降档` 的 1 个组件变体节点；`icon-button.json` 中其余叶子 guid 以 `reconstructed-*` 标记补齐，便于后续 Storybook 矩阵与 API 对齐

## 组成与用途

- **导出项**: `IconButton`、`iconButtonOptions`、`iconButton通透度Options`、`iconButton尺寸Options`
- **使用场景**: 用于呈现 Pixso 公共组件中的图标按钮组预览，支持 1/2/3 个按钮、3 档材质表面和 3 种尺寸（40px / 32px / 28px）

## 量化规格

### 公共参数

| 参数 | 值 | 来源 |
|------|-----|------|
| 布局 | 水平靠右，`flex-end` | DSL `stackMode=HORIZONTAL` / `autoLayoutPrimaryAlign=flex-end` |
| 单按钮圆角 | 1000px | DSL `cornerRadius=1000` |
| 图标字体 | `HM Symbol` / `Regular` | DSL text node |
| 图标颜色 | `--harmony-icon-primary` | DSL `inheritFillStyleID=602:9459` |

### 尺寸变体

| 尺寸 | 按钮尺寸 | 图标尺寸 | gap | padding | 容器宽度（3 按钮） |
|------|----------|----------|-----|---------|-------------------|
| 40px（默认） | 40×40px | 24×24px | 8px | 8px | 136px |
| 32px | 32×32px | 20×20px | 6px | 6px | 108px |
| 28px | 28×28px | 16×16px | 6px | 6px | 96px |

## 状态与交互

- 当前节点仅暴露数量与材质变体，**未提供 hover / pressed / focus / disabled 等交互状态**
- React 实现按 Pixso 静态稿还原，不额外引入设计稿之外的状态层

## Props

| DSL 字段 | Prop 名 | 类型 | 默认值 | 可取值的集合 |
|----------|---------|------|--------|-------------|
| `Icon` | `Icon` | `1 \| 2 \| 3` | `3` | 1, 2, 3 |
| `通透度` | `通透度` | `"材质-标准" \| "材质-强" \| "材质-降档"` | `"材质-标准"` | 材质-标准, 材质-强, 材质-降档 |
| `尺寸` | `尺寸` | `40 \| 32 \| 28` | `40` | 40, 32, 28 |
| — | `glyphs` | `readonly HMSymbolIconName[]` | `square_dashed` × N | 按序嵌入每个按钮的 HM Symbol 名 |
| — | `glyphNodes` | `readonly ReactNode[]` | — | 槽位自定义节点，优先于 `glyphs` |
| — | `glyphSize` | `number` | 按 `尺寸` 自动推算（40→24, 32→20, 28→16） | 内嵌 HM Symbol 字号，显式传入时覆盖自动值 |

### DSL ↔ Prop 对照

- **属性名策略**: 直接使用 Pixso 原始属性名，无命名映射
- **取值集合**: `get_node_dsl` 和 `get_all_components` 中均可追溯到 `Icon=1/2/3` 与 `通透度=材质-标准/材质-强/材质-降档`；`尺寸=40/32/28` 为新增变体维度

## 样式引用

- `--harmony-icon-primary` (global.css) — 图标前景
- `--Material_background_ULTRA_THIN_fill` (global.css) — `材质-标准` 表面
- `--comp_background_color_floating_smooth_fill` (global.css) — `材质-降档` 表面
- `--Floating_background_weak_fill` (global.css) — `材质-强` 表面
- `--Floating_background_line_fill` (global.css) — `材质-降档` 边线

**无新增全局 Token** — 当前实现完全复用 `src/styles/global.css` 中已有变量。

## 兼容说明

- `@/components/Icon` 保留为 deprecated 重导出，供 `src/pages/` 模板库等存量引用继续使用
- CSS 类名同时输出 `hm-icon-button` 与 `hm-icon` 别名，兼容页面级样式覆盖

## 取舍说明

- **`get_variants` 失败**: 按 skill 要求使用 `get_node_dsl` + `get_all_components` + 截图重建 `icon-button.json`
- **`design_to_code` 失败**: Pixso codegen 返回 500，未作为实现依据
- **材质效果落地**: Pixso 中 `Blur/Material_ULTRA_THIN`、`Floating_background_weak` 等效果组合在 Web 端用 `background + border + box-shadow + backdrop-filter` 等效实现
- **glyph 实现**: 默认 `square_dashed`；可通过 `glyphs` 为每个按钮指定 `HMSymbolIcon` 图标名（如编辑按钮 `square_and_pencil`、定位按钮 `location_north_up_right_circle_fill`）
