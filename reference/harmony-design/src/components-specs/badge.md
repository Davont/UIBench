# Badge 组件规格

## Metadata

| 项目 | 值 |
|------|------|
| 实现目录 | `src/components/Badge/` |
| Stories 路径 | `src/components/Badge/Badge.stories.tsx` |
| 变体树 JSON | `src/components/Badge/badge.json` |
| Pixso 链接 | `https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5410:23817` |
| MCP 工具来源 | `get_node_dsl` + `get_screenshot` |
| 所属注册表 | `src/components-specs/components.json`（id: `badge`） |

## 组件变体树 JSON

- 路径：`src/components/Badge/badge.json`
- 生成方式：`get_node_dsl` 返回 `pixTreeNodes`，手动构建 `variantOptions`（因 `get_variants` 返回 `{}`）
- 变体属性：`类型`（DSL 原始属性名）

## 组成与用途

Badge 是角标/徽标组件，用于在 UI 元素上展示数字、状态圆点或文本标记。常见场景：消息未读数、红点提示、标签标记。

**导出项：**
- `Badge` — 主组件
- `badgeVariants` — 变体值数组 `["Dot", "Text", "Longest text"]`
- 类型：`BadgeProps`, `BadgeVariant`

## 量化规格

### 尺寸与形状

| 变体 | 宽 | 高 | 圆角 | 水平内边距 | 垂直内边距 |
|------|-----|-----|------|-----------|-----------|
| Dot | 6px | 6px | 100px（full circle） | 0 | 0 |
| Text（1 位） | 16px | 16px | 100px（full circle） | 0 | 0 |
| Text（2 位） | 自动 | 16px | 100px（full circle） | 6px | 0 |
| Longest text | ≥30px | 16px | 8px | 6px | 1px |

### 颜色

| 属性 | Pixso 色值 | 全局 Token |
|------|-----------|-----------|
| 背景填充 | `rgba(232, 64, 38, 1)` | `--harmony-warning` |
| 文字颜色 | `rgba(255, 255, 255, 1)` | `--harmony-font-on-primary` |

### 字体

| 属性 | Pixso 值 | 说明 |
|------|---------|------|
| 字体族 | HarmonyHeiTi | 组件内声明，fallback: "HarmonyOS Sans", "PingFang SC", sans-serif |
| 字号 | 10px | 对应 `--harmony-font-size-caption-m`（10px），但权重不同 |
| 字重 | 400 (Regular) | `--harmony-font-weight-caption-m` 为 500，故使用组件级 CSS 变量覆盖 |
| 行高 | 14px | 由文字内容实际高度决定（DSL text node height=14px） |
| 对齐 | center/center | flex 居中 |

## 状态与交互

Badge 为纯展示组件，无交互状态（无 hover / active / disabled 等视觉变化）。

## Props

```ts
interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  类型?: "Dot" | "Text" | "Longest text"  // 默认 "Text"
  count?: number | string                  // 角标数字或文本
  maxCount?: number                        // 默认 99，超过显示 "99+"
  children?: ReactNode                     // 自定义内容（覆盖 count）
}
```

### DSL ↔ Prop 对照

| DSL 字段 | DSL 取值 | Prop 名 | 说明 |
|----------|---------|---------|------|
| `类型`（变体属性） | `"Dot"`, `"Text"`, `"Longest text"` | `类型` | 直接使用 DSL 原始属性名 |
| 组件内文本（"3", "99+"） | 由 count + maxCount 计算 | `count`, `maxCount` | DSL 无对应字段，为组件 API 扩展 |
| 组件内文本内容 | — | `children` | DSL 无对应字段，为组件 API 扩展 |

**命名说明：** `类型` 为 DSL 原始变体属性名，直接使用。TypeScript/JSX 中中文字段名合法，无需映射。

## 样式引用

### 使用的全局 Token

| Token | 取值 | 用途 |
|-------|------|------|
| `--harmony-warning` | `rgba(232, 64, 38, 1)` | 背景填充 |
| `--harmony-font-on-primary` | `rgba(255, 255, 255, 1)` | 文字颜色 |

### 组件级 CSS 变量

| 变量 | 默认值 | 用途 |
|------|--------|------|
| `--badge-bg` | `var(--harmony-warning)` | 背景色 |
| `--badge-fg` | `var(--harmony-font-on-primary)` | 文字色 |
| `--badge-height` | `16px` | 高度 |
| `--badge-radius` | `8px` | 圆角 |
| `--badge-font-size` | `10px` | 字号 |
| `--badge-font-weight` | `400` | 字重 |
| `--badge-line-height` | `14px` | 行高 |

### 新增全局 Token

本次实现 **未新增** 全局 Token。所有色值均可映射至 `global.css` 已有变量。

字体 `HarmonyHeiTi` 在组件 CSS 中直接声明（与项目内其他 Harmony 组件一致）。

## 取舍说明

- **字重偏差**：DSL 文本样式 `Font/Caption_M/Regular` 字重为 400，而 `global.css` 中 `--harmony-font-weight-caption-m` 为 500。组件使用 CSS 变量 `--badge-font-weight: 400` 精确匹配稿面，未直接引用全局 token。
- **字体族**：`HarmonyHeiTi` 未在 `global.css` 的 `font-family` 配置中出现，组件内直接声明字体族名称并添加 fallback。
- **Dot 变体隐藏文字**：Dot 变体不显示文字内容，通过 CSS `.harmony-badge--Dot .harmony-badge__text { display: none }` 隐藏。
