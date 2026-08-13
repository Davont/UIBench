# LoadingProgressBar

## Metadata

| 字段 | 值 |
|------|------|
| 实现目录 | `src/components/LoadingProgressBar/` |
| Stories 路径 | `src/components/LoadingProgressBar/loading-progress-bar.stories.tsx` |
| Pixso 链接 | [Loading Progress Bar](https://pixso.cn/app/design/KXylddm-EMqGBCzGr6ZZgQ?item-id=67:56839) |
| item-id | `67:56839` |
| MCP 工具来源 | `get_node_dsl`, `get_screenshot`, `get_variants`, `design_to_code` |
| 变体树 JSON | `src/components/LoadingProgressBar/loading-progress-bar.json` |

## 组件变体树 JSON

- `get_variants(itemId=67:56839)` 返回 `{}`。
- JSON 按 `get_node_dsl` 中 `.信息层/进度条` 节点和 5 个矩形子节点重建。
- 该节点无 Pixso variant 轴；`variantOptions` 为空对象。

## 组成与用途

- **导出项**：`LoadingProgressBar`、`LoadingProgressBarProps`、`loadingProgressBarSegments`
- **用途**：信息层上的分段加载/进度提示。默认展示 5 段，其中首段为当前高亮段。

## 量化规格

| 元素 | 数值 |
|------|------|
| 选中实例截图尺寸 | `328 × 24px` |
| 主组件定义尺寸 | `360 × 24px` |
| 默认实现尺寸 | `328 × 24px`，与 `get_screenshot` 一致 |
| 布局 | 横向 flex，居中对齐 |
| 分段数量 | 5 |
| 分段间距 | `4px` |
| 分段高度 | `2px` |
| 分段宽度 | 默认 `62.4px`（`328px - 4px * 4` 后五等分） |
| 圆角 | `3.125px` |
| 高亮段颜色 | `rgba(255,255,255,1)`，整体 `opacity: 0.9000000358` |
| 普通段颜色 | `rgba(255,255,255,0.2)` |

## 状态与交互

| 状态 | 表现 |
|------|------|
| Default | 第 1 段高亮，其余 4 段为白色 20% |

当前 Pixso 节点无可配置状态轴，也无点击/拖拽交互。

## Props

```ts
interface LoadingProgressBarProps extends Omit<HTMLAttributes<HTMLDivElement>, "title"> {
  title?: boolean
  Description?: boolean
}
```

### DSL ↔ Prop 对照

| DSL 字段 | Prop 名 | 取值集合 | 默认值 | 说明 |
|----------|---------|----------|--------|------|
| `propDefMap.visible_17_3.name = "title"` | `title` | `boolean` | `true` | Pixso visible override；当前节点未渲染对应文本。因 HTML 原生 `title` 属性为 string，实现使用 `Omit<HTMLAttributes<HTMLDivElement>, "title">` 保留 Pixso 原名 |
| `propDefMap.visible_17_8.name = "Description"` | `Description` | `boolean` | `true` | Pixso visible override；当前节点未渲染对应文本 |

## 样式引用

| 变量名 | 用途 |
|--------|------|
| `--harmony-icon-on-primary` | 高亮段填充 |
| `--harmony-icon-on-fourth` | 普通段填充 |

无新增 `global.css` token。

## 取舍说明

| 项目 | 说明 |
|------|------|
| 默认宽度 | DSL 主组件定义为 `360px`，但选中实例的子符号宽度与截图均为 `328px`；默认实现采用 `328px` 以匹配截图真值。Story `Overview` 额外展示 `360px` 容器内 `w-full` 用法。 |
| 变体树 | `get_variants` 返回空，按 DSL 子节点重建静态树。 |
| `title` / `Description` | 这两个 visible override 在 DSL 中存在，因此按原名暴露为 Props；当前 Pixso 截图未显示文本，组件仅透传为 data 属性用于可追溯性。 |

## 1:1 还原验证

- `get_node_dsl(itemId=67:56839)` 成功。
- `get_screenshot(itemId=67:56839)` 成功，返回 PNG。
- `design_to_code(itemId=67:56839, react)` 成功；生成 CSS 确认 `height: 24px`、`gap: 4px`、分段 `height: 2px`、`border-radius: 3.125px`。
- 未执行自动 SSIM；本轮以 DSL 量化参数 + Pixso 截图人工对照 + Storybook 预览为验收方式。
