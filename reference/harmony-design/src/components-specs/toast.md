# Toast 轻提示组件规格

## Metadata

| 项目 | 值 |
|------|------|
| 实现目录 | `src/components/Toast/` |
| Stories 路径 | `src/components/Toast/Toast.stories.tsx` |
| Pixso 链接 | [5410:23821](https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5410:23821) |
| MCP 工具 | `get_node_dsl`、`get_screenshot`、`get_export_image`、`design_to_code`、`get_variants`、`get_all_components` |
| 变体树 JSON | `src/components/Toast/Toast.json` |

## 组件变体树 JSON

- **路径**：`src/components/Toast/Toast.json`
- **来源**：`get_node_dsl`（`5410:23821`）直接提取 + `get_variants`（返回空 `{}`）降级重建
- **生成方式**：由 `get_node_dsl` 的 `pixComponentTreeDslNodes` 提取组件实例名 `Toast-Phone`，结合实例名称中的变体信息 `类型=Phone` 重建
- **变体维度**：当前仅 `类型=Phone` 一个变体（`get_variants` 返回空，`get_all_components` 确认无其他变体）

## 组成与用途

Toast 是 HarmonyOS 系统的轻量级反馈提示组件，用于展示操作结果、状态通知等短时信息。

**导出项**：
- `Toast` — React 组件
- `toastTypes` — 类型枚举常量 `["Phone"]`
- `ToastProps` — Props 类型
- `ToastType` — 类型联合类型

**使用场景**：操作成功/失败提示、系统状态通知、短暂信息展示。

## 量化规格

### 尺寸与布局

| 属性 | Pixso DSL 值 | CSS 实现 |
|------|-------------|----------|
| 容器宽度 | 自适应（min-width: auto） | `inline-flex` |
| 容器最小高度 | 36px (min-height) | `min-h-9` (36px) |
| 圆角 | 18px | `rounded-[18px]` |
| 水平内边距 | 16px | `px-4` (16px) |
| 垂直内边距 | 8px | `py-2` (8px) |
| 子元素间距 | 10px (autoLayoutCounterItemSpacing) | `gap-2.5` (10px) |
| 对齐方式 | center / center | `items-center justify-center` |

### 表面样式

| 属性 | Pixso DSL 值 | CSS 实现 |
|------|-------------|----------|
| 填充色 | rgba(255,255,255,0.9) — `Light/Blur/COMPONENT_ULTRA_THICK` (style `616:9117`) | `bg-[var(--COMPONENT_ULTRA_THICK_fill)]` |
| 背景模糊 | BACKGROUND_BLUR radius=80, saturate=0 — `Light/Blur/COMPONENT_ULTRA_THICK` (style `1:347`) | `backdrop-blur-[40px]` (DSL radius 80 ÷ 2 = 40px，遵循仓库规则) |
| 投影 | DROP_SHADOW: rgba(0,0,0,0.2), offset(0,10), radius=60, spread=0 | `shadow-[0_10px_60px_rgba(0,0,0,0.2)]` |

### 文字样式

| 属性 | Pixso DSL 值 | CSS 实现 |
|------|-------------|----------|
| 字体系列 | HarmonyHeiTi — `Font/Body_M/Regular` (style `602:9661`) | `font-['HarmonyHeiTi',var(--font-sans)]` |
| 字号 | 14px | `text-[14px]` |
| 字重 | Regular (400) | `font-normal` |
| 行高 | 19px (DSL text frame auto-height for 14px Regular) | `leading-[19px]` |
| 字间距 | 0（DSL 未设置） | `tracking-normal` |
| 文字颜色 | rgba(0,0,0,0.898) — `Light/font_primary` (style `602:9446`) | `text-[var(--harmony-font-primary)]` |
| 文本对齐 | center | `text-center`（通过 `justify-center` 在 flex 容器内实现） |

## 状态与交互

Toast 为纯展示组件，无 hover/active/disabled 状态。通过内容变化表达不同业务场景。

组件设置了 ARIA 属性 `role="status"` 和 `aria-live="polite"`，确保屏幕阅读器在内容变化时播报。

## Props

```typescript
interface ToastProps extends React.HTMLAttributes<HTMLDivElement> {
  内容?: string;   // 提示文字内容，默认 "Toast content"
  类型?: "Phone";  // 变体类型，默认 "Phone"
}
```

### DSL ↔ Prop 对照表

| DSL 字段路径 | Prop 名 | 可取值 | 默认值 | 说明 |
|-------------|---------|--------|--------|------|
| `pixComponentTreeDslNodes[0].childNode[0].childNode[0].childNode[0].nodeText` | `内容` | 任意字符串 | `"Toast content"` | 直接映射 DSL 节点文本 "Toast content" |
| `variantOptions.类型` | `类型` | `["Phone"]` | `"Phone"` | DSL 变体属性，保持原名。实例名 `Toast-Phone` 确认该变体值 |

**命名说明**：Props 名称 `内容`、`类型` 直接使用 DSL / Pixso 原始属性名（中文），符合仓库规范。

## 样式引用

### 复用的全局 Token

| 全局 Token | Pixso 取值 | 用途 |
|-----------|-----------|------|
| `--COMPONENT_ULTRA_THICK_fill` | rgba(255,255,255,0.9) | 表面填充色（Light/Blur/COMPONENT_ULTRA_THICK fill style `616:9117`） |
| `--harmony-font-primary` | rgba(0,0,0,0.898) | 文字颜色（Light/font_primary fill style `602:9446`） |

### 新增/使用的全局样式

无新增全局 Token。所有样式值通过现有 `:root` / `.dark` 中已有的 `--COMPONENT_ULTRA_THICK_fill` 和 `--harmony-font-primary` 变量覆盖，组件自动适配 light/dark 主题。

### 字体

需确保项目加载 `HarmonyHeiTi` 字体。在 `global.css` 中添加 `@import "@fontsource/harmony-heiti"` （或使用系统字体 fallback）。

## 取舍说明

1. **背景模糊 `backdrop-blur-[40px]`**：DSL 中 `BACKGROUND_BLUR` radius=80，按仓库规则（CLAUE.md）除以 2 得 CSS blur(40px)。注：Pixso `design_to_code` 官方输出使用 `blur(26.667px)`（80÷3），本仓库实测 ÷2 更接近视觉效果，故沿用仓库规则。在 Storybook 纯色背景下不可见，实际应用中透明区域可见毛玻璃效果。
2. **投影**：DSL DROP_SHADOW 定义在 `Toast-Phone` 实例层（guid `5410:23818`），`组合 2` 内层也继承了该效果。组件使用一层 `shadow-[0_10px_60px_rgba(0,0,0,0.2)]` 直接映射 DSL 参数，比 `design_to_code` 的分离元素 + `filter:blur(20px)` 方案更精确对应 Pixso 投影语义。
3. **主题适配**：填充色 `--COMPONENT_ULTRA_THICK_fill` 和文字色 `--harmony-font-primary` 在 `:root`（light）和 `.dark` 中均有定义，组件自动响应主题切换。
4. **子元素间距 `gap-2.5`**：DSL `autoLayoutCounterItemSpacing: 10` 预留了图标与文字的间距，当前设计仅含文字，但 gap 已就位以便后续扩展图标变体。
5. **单变体**：当前 DSL 仅 `类型=Phone`，`get_variants` 返回空 `{}`，`get_all_components` 确认无其他变体。后续如新增变体（如 `类型=Pad`），在 `toastTypes` 和 `variantOptions` 中扩展即可。

## 变更记录

| 日期 | 变更内容 |
|------|---------|
| 2026-06-13 | 初始实现：基于 `get_node_dsl` + `design_to_code` |
| 2026-06-13 | **校验修复**：新增 `min-h-9`（36px 最小高度）、`gap-2.5`（10px 子元素间距）；填充色改用 `var(--COMPONENT_ULTRA_THICK_fill)`、文字色改用 `var(--harmony-font-primary)` 以对齐全局 Token 并支持主题切换；更新 `Toast.json` 变体树结构；完善 `get_variants` 降级重建说明 |
