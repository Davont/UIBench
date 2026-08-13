# TextClock 组件规格

## Metadata

| 字段 | 值 |
|------|------|
| 实现目录 | `src/components/TextClock/` |
| Stories 路径 | `src/components/TextClock/TextClock.stories.tsx` |
| Pixso 链接 | [TextClock](https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5413:374) |
| item-id | `5413:374` |
| MCP 工具来源 | `get_node_dsl`, `get_screenshot` |

## 组件变体树 JSON

**文件路径：** `src/components/TextClock/text-clock.json`

**生成方式：** 基于 `get_node_dsl` 直接提取；`get_variants` 返回 `{}`，降级使用 `get_node_dsl` 中的 `pixTreeNodes` 结构 + `get_all_components` 正则解析验证。

**变体维度：**
- 类型：`Number` | `Center with simplify date` | `Center`

## 组成与用途

**导出项：**
- `TextClock` - 主组件
- `textClockTypes` - 类型枚举常量数组
- `TextClockProps` - Props 类型
- `TextClockType` - 类型联合类型

**使用场景：**
- 锁屏/待机界面时间显示
- 状态栏/通知栏时间展示
- 桌面时钟小组件

## 量化规格

### 尺寸

| 元素 | 值 |
|------|------|
| 容器宽度 | 360px |
| Number 变体上下内边距 | 24px |
| Number 变体左右内边距 | 12px |
| Number 变体间距 | 4px |
| Center/Center simplify 变体上下内边距 | 5px |
| Center/Center simplify 变体左右内边距 | 12px |
| Center/Center simplify 变体间距 | 10px |

### 字体

| 元素 | fontSize | fontWeight | lineHeight | fontFamily |
|------|----------|------------|------------|------------|
| 时间文本 | 48px | 500 (Medium) | 64px (auto) | HarmonyHeiTi |
| 日期文本 | 16px | 500 (Medium) | 21px (auto) | HarmonyHeiTi |

### 色值

| 元素 | 色值 | 变量引用 |
|------|------|----------|
| 时间文本 | rgba(0,0,0,0.898) | `--harmony-font-primary` |
| 日期文本 | rgba(0,0,0,0.6) | `--harmony-font-secondary` |

## 状态与交互

TextClock 为纯展示组件，无交互状态。三种变体由 `类型` prop 控制切换。

## Props

```typescript
interface TextClockProps extends HTMLAttributes<HTMLDivElement> {
  类型?: "Number" | "Center with simplify date" | "Center"  // 默认："Number"
  时间?: string                                               // 默认："17:00"
  日期?: string                                               // 默认："Monday, March 13th, 2023"
}
```

### DSL ↔ Prop 对照

| DSL 属性 | Prop 名 | 取值集合 | 说明 |
|----------|---------|----------|------|
| 类型 (INSTANCE name) | 类型 | "Number", "Center with simplify date", "Center" | 与 DSL 中三个 INSTANCE 子节点名称一一对应 |
| Time nodeText | 时间 | 任意字符串 | 仅在类型="Number" 时渲染，默认值 "17:00" 来自 DSL |
| Date nodeText | 日期 | 任意字符串 | 所有变体均渲染，默认值按变体不同 |

## 样式引用

### 使用的 global.css 变量

| 变量名 | 用途 | 来源 |
|--------|------|------|
| `--harmony-font-primary` | 时间文本色 + Center/Center-simplify 日期文本色 | 现有 token |
| `--harmony-font-secondary` | Number 变体日期文本色 | 现有 token |
| `--harmony-font-size-display-m` | 时间字号 48px | 现有 token |
| `--harmony-font-size-body-l` | 日期字号 16px | 现有 token |

### 新增 Token

无新增全局 Token。所有色值与字号均与现有 Harmony Token 对齐。

## 取舍说明

| 项目 | 说明 |
|------|------|
| 布局方案 | 三个变体均使用 `flex-col + items-center`，与 DSL 中 `stackMode: VERTICAL` + `stackPrimaryAlign: center` + `stackCounterAlign: center` 一致 |
| lineHeight 处理 | DSL 中 `textAutoResize: HEIGHT` 表示高度自适应，对应 CSS 不设固定 line-height；当前使用 `leading-[64px]`（Time）和 `leading-[21px]`（Date）近似。若需精确到 px 行高，后续可加任意值 |
| letterSpacing | DSL 中未显式指定 letterSpacing，默认使用 0（normal） |
| 字体族 | DSL 指定 HarmonyHeiTi，组件 CSS 中声明 `font-family: HarmonyHeiTi, sans-serif`，在无 HarmonyHeiTi 的环境中降级到系统 sans-serif |
| get_variants 降级 | `get_variants` 返回 `{}`，变体信息从 `get_node_dsl` 的 pixTreeNodes + childNode INSTANCE 名称中提取，并与 `get_all_components` 返回的组件 name 字段交叉验证一致 |

## 1:1 还原验证

**验证方式：** 人工对照截图 + DSL 数据交叉验证

**对照结论：**
- ✅ 三种变体和 DSL 三个 INSTANCE 子节点一一对应
- ✅ 时间文本 48px Medium 与 DSL Font/Display_M/Medium 一致
- ✅ 日期文本 16px Medium 与 DSL Font/Body_L/Medium 一致
- ✅ 时间色值 `--harmony-font-primary` 与 DSL Light/font_primary 一致
- ✅ Number 变体日期色 `--harmony-font-secondary` 与 DSL Light/font_secondary（inheritFillStyleID: 602:9447）一致
- ✅ Center/Center-simplify 变体日期色 `--harmony-font-primary` 与 DSL Light/font_primary（inheritFillStyleID: 602:9446）一致
- ✅ Number 变体 padding 24px/12px 与 DSL autoLayoutPadding 一致
- ✅ Center 变体 padding 5px/12px 与 DSL autoLayoutPadding 一致
- ✅ 布局方向 vertical + centered 与 DSL autoLayout stackMode/align 一致

**未执行自动 SSIM**，对照方式为人工复核 + DSL 数据交叉验证。
