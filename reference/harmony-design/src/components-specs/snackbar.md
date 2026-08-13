# Snackbar

## Metadata

| 字段 | 值 |
|------|-----|
| 实现目录 | `src/components/Snackbar/` |
| Stories 路径 | `src/components/Snackbar/Snackbar.stories.tsx` |
| Pixso 链接 | https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5410:23844 |
| Pixso item-id | `5410:23844` |
| MCP 工具来源 | `get_node_dsl`, `get_screenshot`, `design_to_code` |
| 变体树 JSON | `src/components/Snackbar/snackbar.json` |

## 组件变体树 JSON

- **路径**: `src/components/Snackbar/snackbar.json`
- **生成方式**: `get_variants` 返回空 `{}`，从 `get_node_dsl` 提取 `左侧区域` 变体属性重建
- **变体属性**: `左侧区域`: `"1"` | `"2"`

## 组成与用途

鸿蒙风格 Toast 通知条（Snackbar），用于在屏幕底部或任意位置显示轻量级通知消息。

- `Snackbar` — 主组件
- 导出项：`Snackbar`（default + named）、`SnackbarProps`、`Snackbar左侧区域`、`snackbar左侧区域Options`

### 内部结构

```
Snackbar (328×auto, max-width:400)
├── 左侧区域（196px 固定宽度）
│   ├── 图标（24px HM Symbol，flex-shrink:0）
│   └── 文本区（flex-1）
│       ├── [左侧区域=1] 标题（14px Regular，单行）
│       └── [左侧区域=2] 标题（14px Medium）+ 副标题（12px Regular，gap:2px）
└── 右侧区域（flex-shrink:0）
    ├── 文字按钮（14px Regular，brand色，rounded-16px，px-2 py-1.5）
    └── 关闭图标按钮（16px HM Symbol，p-2，rounded-16px）
```

## 量化规格

### 容器

| 属性 | 值 | 来源 |
|------|-----|------|
| 宽度 | 328px | DSL `width` |
| 最大宽度 | 400px | DSL `maxWidth` |
| 高度 | auto（1-line: 48px / 2-line: 54px） | DSL |
| 圆角 | 18px | DSL `cornerRadius` |
| 内边距 | 0px 8px 0px 12px | DSL `autoLayout` |
| 子元素间距 | 8px | DSL `autoLayoutItemSpacing` |
| 布局方向 | 水平（row） | DSL `stackMode: HORIZONTAL` |
| 对齐 | flex-start / center | DSL `autoLayoutPrimaryAlign` / `autoLayoutCounterAlign` |

### 材质（ULTRA_THICK）

| 属性 | 值 | 来源 |
|------|-----|------|
| 背景色 | rgba(255,255,255,0.9) | DSL `fillPaints` (inheritFillStyleID: 616:9117) |
| 投影 | 0px 10px 60px 0px rgba(0,0,0,0.2) | DSL `effects` DROP_SHADOW |
| 背景模糊 | blur(40px) = DSL radius 80 / 2 | DSL `effects` BACKGROUND_BLUR + CLAUDE.md 换算规则 |

### 左侧区域（1-line, 属性1="24icon"）

| 属性 | 值 | 来源 |
|------|-----|------|
| 宽度 | 196px | DSL |
| Gap | 12px | CSS `Left1line` |
| 上下内边距 | 12px 0 | CSS `Left1line` |
| 图标字号 | 24px | CSS |
| 图标字体 | HM Symbol-Regular | CSS |
| 标题字号 | 14px | DSL `fontSize` |
| 标题字重 | 400 (Regular) | DSL `fontStyle` |
| 标题字体 | HarmonyHeiTi | DSL `fontFamily` |
| 标题颜色 | --harmony-font-primary | DSL `inheritFillStyleID: 602:9446` |
| 标题行高 | 22px (leading-[22px]) | CSS text-fontbody_mregular |

### 左侧区域（2-line, 属性1="24icon"）

| 属性 | 值 | 来源 |
|------|-----|------|
| 宽度 | 196px | DSL |
| Gap | 12px | CSS `Left2line` |
| 上下内边距 | 8px 0 | CSS `Left2line` |
| 图标字号 | 24px | CSS |
| 标题字号 | 14px | DSL `fontSize` |
| 标题字重 | 500 (Medium) | DSL text-fontsubtitle_smedium |
| 标题字体 | HarmonyHeiTi | DSL `fontFamily` |
| 标题颜色 | --harmony-font-primary | DSL |
| 标题行高 | 20px | CSS |
| 副标题字号 | 12px | DSL `fontSize` |
| 副标题字重 | 400 (Regular) | DSL text-fontbody_sregular |
| 副标题字体 | HarmonyHeiTi | DSL `fontFamily` |
| 副标题颜色 | --harmony-font-secondary | DSL `inheritFillStyleID: 1912:10031` |
| 标题-副标题间距 | 2px | CSS `gap` |

### 右侧操作区

| 属性 | 值 | 来源 |
|------|-----|------|
| 文字按钮内边距 | 6px 8px | CSS `Textbutton` |
| 文字按钮圆角 | 16px | CSS `border-radius` |
| 文字按钮字号 | 14px | DSL |
| 文字按钮字重 | 400 (Regular) | DSL |
| 文字按钮颜色 | --harmony-brand | DSL `inheritFillStyleID: 602:9440` |
| 文字按钮 Hover 背景 | rgba(0,0,0,0.047) | DSL `inheritFillStyleID: 602:9466` |
| 文字按钮 Pressed 背景 | rgba(0,0,0,0.098) | DSL `inheritFillStyleID: 602:9467` |
| 关闭按钮内边距 | 8px | CSS `Cancel0` |
| 关闭按钮圆角 | 16px | CSS `Cancel0` |
| 关闭按钮字号 | 16px | CSS |
| 关闭按钮字体 | HM Symbol-Regular | CSS |

## 状态与交互

| 状态 | 说明 |
|------|------|
| Default | 正常展示状态，文字按钮与关闭按钮均可见 |
| Hover (文字按钮) | 背景变为 rgba(0,0,0,0.047)，圆角 16px |
| Pressed (文字按钮) | 背景变为 rgba(0,0,0,0.098)，圆角 16px |
| Hover (关闭按钮) | 背景变为 rgba(0,0,0,0.047)，圆角 16px |
| Pressed (关闭按钮) | 背景变为 rgba(0,0,0,0.098)，圆角 16px |

## Props

### 核心类型签名

```typescript
interface SnackbarProps {
  左侧区域?: "1" | "2";
  icon?: React.ReactNode;
  title?: string;
  subtitle?: string;
  actionText?: string;
  onAction?: () => void;
  onClose?: () => void;
  className?: string;
  id?: string;
}
```

### DSL ↔ Prop 对照

| DSL 字段 / 变体属性 | Prop 名 | 合法取值 | 默认值 | 说明 |
|---------------------|---------|----------|--------|------|
| `左侧区域` (variant property) | `左侧区域` | `"1"` \| `"2"` | `"1"` | 直接使用 Pixso 原始属性名，无需映射 |
| `slot_2674_9532` (icon slot) | `icon` | ReactNode | `HMSymbolIcon name="segmented_button_highlight"`（U+F012F） | 左侧图标插槽，使用本地 HM Symbol 字体资源 |
| `slot_2674_9533` (title slot) | `title` | string | `"Title"` | 标题文本 |
| `slot_2674_9544` (subtitle slot) | `subtitle` | string | `"Subtitle"` | 副标题（仅 左侧区域=2） |
| `slot_2674_9573` (text button slot) | `actionText` | string | `"TEXT BT"` | 右侧文字按钮文本 |
| — | `onAction` | `() => void` | — | 开发体验 Prop，DSL 无直接映射 |
| — | `onClose` | `() => void` | — | 开发体验 Prop，DSL 无直接映射 |

## 样式引用

### 使用的 `global.css` 变量

| 变量 | 用途 |
|------|------|
| `--COMPONENT_ULTRA_THICK_fill` | 容器背景色；Light 为 `rgba(255,255,255,0.9)`，Dark 为 `rgba(46,48,51,0.9)` |
| `--harmony-font-primary` | 标题文字色 |
| `--harmony-font-secondary` | 副标题文字色 |
| `--harmony-icon-primary` | 图标/关闭按钮色 |
| `--harmony-brand` | 文字按钮色 |

### 新增全局 Token

本次未新增全局 Token。所有样式均通过现有 `global.css` 变量 + Tailwind arbitrary values 实现。

## 取舍说明

1. **设计稿简化**：原 Pixso 设计稿中的 Snackbar 由多个独立子组件（Left1line、Left2line、Right、Textbutton、Cancel0）组合而成。本实现将它们内联为一个自包含组件，避免创建 5+ 个仅在此处使用的微小依赖组件。视觉效果与 DSL 保持 1:1 一致。
2. **背景模糊值**：DSL BACKGROUND_BLUR radius=80，按 CLAUDE.md 规则除以 2 得 40px。`design_to_code` 导出的 CSS 使用了 26.67px（≈80/3），本实现遵循项目 CLAUDE.md 约定使用 40px。
3. **开发体验 Props**：`onAction`、`onClose`、`icon` 等交互回调与插槽 Props 在 DSL 中无直接对应字段，属于实用的 React 组件 API 扩展。已通过 props 表格注明 DSL 无映射。
4. **默认图标**：通过本地 `HMSymbolIcon` 渲染 Pixso 节点对应的 U+F012F（`segmented_button_highlight`），字体资源来自 `src/assets/hmsymbol/HMSymbolVF.ttf`，不依赖系统安装字体；调用方仍可通过 `图标` Prop 覆盖。
5. **关闭图标**：设计稿确认使用 HM Symbol-Regular，但本地 DSL 未保留精确 `nodeText`；按“关闭/退出”语义检索本地 `hmsymbol-map.json` 后，使用 `xmark`（U+F0056）。组件保持原有 32px 点击布局与 16px 可视字形。
