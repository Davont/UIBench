# Floating Snackbar

## Metadata

| 字段 | 值 |
|------|-----|
| 实现目录 | `src/components/FloatingSnackbar/` |
| Stories 路径 | `src/components/FloatingSnackbar/FloatingSnackbar.stories.tsx` |
| Pixso 链接 | https://pixso.cn/app/design/HA_e8I2mE7Oa0b5ZoeokSA?item-id=5322:157 |
| Pixso item-id | `5322:157` |
| MCP 工具来源 | `get_node_dsl`, `get_screenshot`, `get_variants`, `design_to_code`, `get_all_components` |
| 变体树 JSON | `src/components/FloatingSnackbar/floating-snackbar.json` |

## 组件变体树 JSON

- 路径：`src/components/FloatingSnackbar/floating-snackbar.json`
- 生成方式：`get_variants` 返回空 `{}`，按 `get_node_dsl` 中 8 个实例名重建。
- 变体属性：
  - `左侧区域`: `"1"` | `"2"`
  - `通透度`: `"标准"` | `"强"` | `"降档"` | `"弱"`

## 组成与用途

鸿蒙风格浮动提醒条，结构上接近 `Snackbar`，但视觉上是更明显的 floating material 版本，并且设计稿直接给出了 8 态矩阵。

- `FloatingSnackbar`：主组件
- 导出项：`FloatingSnackbar`、`FloatingSnackbarProps`、`FloatingSnackbarLeftRegion`、`FloatingSnackbarTransparency`

## 量化规格

### 容器

| 属性 | 值 | 来源 |
|------|-----|------|
| 宽度 | 328px | DSL `width` |
| 最大宽度 | 400px | DSL `autoLayout.maxWidth` |
| 高度 | 48px / 54px | DSL `height` |
| 圆角 | 18px | DSL `cornerRadius` |
| 左右内边距 | 12px / 8px | DSL `autoLayoutPaddingLeft/Right` |
| 主轴间距 | 8px | DSL `autoLayoutItemSpacing` |
| 布局 | 水平 auto-layout，纵向居中 | DSL `stackMode=HORIZONTAL`, `autoLayoutCounterAlign=center` |

### 左侧区域

| 属性 | 左侧区域=1 | 左侧区域=2 | 来源 |
|------|-----------|-----------|------|
| 左区宽度 | 196px | 196px | 截图量化 + 与 `Snackbar` 对照 |
| 图标尺寸 | 24px | 24px | DSL `fontSize=24` |
| 左区上下内边距 | 12px | 8px | 截图量化 |
| 图标与文本间距 | 12px | 12px | 截图量化 |
| 标题字号 | 14px | 14px | DSL `fontSize` |
| 标题字重 | 400 | 500 | DSL `fontStyle` |
| 标题行高 | 22px | 20px | 截图量化 + 现有 `Snackbar` 对照 |
| 副标题字号 | — | 12px | DSL `fontSize` |
| 副标题行高 | — | 16px | 截图量化 |
| 标题/副标题间距 | — | 2px | DSL `autoLayoutItemSpacing` |

### 右侧操作区

| 属性 | 值 | 来源 |
|------|-----|------|
| 文字按钮 | `Small / Text / Enabled` | `pixComponentTreeDslNodes` |
| 文字按钮字号 | 14px | DSL `602:9662` |
| 文字按钮文案 | `TEXT BT` | 截图 + DSL |
| 关闭按钮热区 | 32×32px | 截图量化 |
| 关闭按钮图标 | 16px | 截图量化 |

### 通透度材质

| 通透度 | 关键视觉 |
|--------|----------|
| `标准` | 单行更接近 ULTRA_THICK 浮层；双行为 `FLOATING_THICK` 材质，带内阴影与 8px drop shadow |
| `强` | 更偏 `Material_background_THICK`，双行版本内阴影更明显 |
| `降档` | 纯白 / 纯浅灰实体面，无 backdrop blur |
| `弱` | `Floating_background_weak`，保留透明与柔和高光 |

## 状态与交互

| 状态 | 说明 |
|------|------|
| Default | 设计稿提供的 8 个静态组合态 |
| Hover | 关闭按钮使用 `interactive_hover`，文字按钮沿用 `Button` 自身 hover |
| Pressed | 关闭按钮使用 `rgba(0,0,0,0.098)`，文字按钮沿用 `Button` 自身 pressed |

## Props

### 核心类型签名

```ts
interface FloatingSnackbarProps extends React.HTMLAttributes<HTMLDivElement> {
  左侧区域?: "1" | "2";
  通透度?: "标准" | "强" | "降档" | "弱";
  标题?: string;
  副标题?: string;
  按钮文案?: string;
  图标?: React.ReactNode;
  onAction?: () => void;
  onClose?: () => void;
  关闭按钮无障碍标签?: string;
}
```

### DSL ↔ Prop 对照

| DSL 字段 / 变体属性 | Prop 名 | 合法取值 | 默认值 | 说明 |
|---------------------|---------|----------|--------|------|
| `左侧区域` | `左侧区域` | `"1"` \| `"2"` | `"1"` | 与实例名保持一致 |
| `通透度` | `通透度` | `"标准"` \| `"强"` \| `"降档"` \| `"弱"` | `"标准"` | 与实例名保持一致 |
| 标题文本覆盖 | `标题` | `string` | `"Title"` | 对应标题文本节点实例覆盖 |
| 副标题文本覆盖 | `副标题` | `string` | `"Subtitle"` | 仅 `左侧区域="2"` 展示 |
| 按钮文本覆盖 | `按钮文案` | `string` | `"TEXT BT"` | 对应右侧 `Small Text Button` 文案 |
| 图标内容覆盖 | `图标` | `ReactNode` | 默认 24px 图标 | 对应左侧图标槽位 |
| — | `onAction` | `() => void` | — | React 交互扩展，DSL 无直接字段 |
| — | `onClose` | `() => void` | — | React 交互扩展，DSL 无直接字段 |

## 样式引用

### 使用的 `global.css` 变量

| 变量 | 用途 |
|------|------|
| `--COMPONENT_ULTRA_THICK_fill` | `标准` 单行浮层面 |
| `--FLOATING_THICK_fill` | `标准` 双行浮层面 |
| `--Material_background_THICK_fill` | `强` 材质面 |
| `--Floating_background_weak_fill` | `弱` 材质面 |
| `--harmony-font-primary` | 标题色 |
| `--harmony-font-secondary` | 副标题色 |
| `--harmony-icon-primary` | 图标 / 关闭按钮色 |
| `--harmony-font-emphasize` | 操作文案色 |
| `--harmony-interactive-hover` | 关闭按钮 hover 背景 |

### 新增全局 Token

本次未新增全局 token。

## 取舍说明

1. `design_to_code` 返回 500，未作为最终实现依据；以 `get_node_dsl + get_screenshot` 为准。
2. `get_variants` 返回 `{}`，按 8 个实例名重建 `variantOptions` 与 `pixTreeNodes`。
3. 右侧按钮直接复用仓库现有 `Button` 的 `Small / Text` 变体，因为 DSL 中也明确出现了同一颗小号文本按钮组件。
4. DSL 对文本可编辑槽位没有单独暴露字段名，因此 `标题 / 副标题 / 按钮文案 / 图标` 作为实例覆盖型 props 暴露，并在本表中明确标注来源。
