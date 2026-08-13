# SubHeader 组件规格

## Metadata

| 字段 | 值 |
|------|------|
| 实现目录 | `src/components/SubHeader/` |
| Stories 路径 | `src/components/SubHeader/subheader.stories.tsx` |
| Pixso 链接 | [SubHeader-Phone](https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5409:23700) |
| item-id | `5409:23700` |
| MCP 工具来源 | `get_screenshot`, `design_to_code` |

## 组件变体树 JSON

**文件路径：** `src/components/SubHeader/subheader.json`

**生成方式：** 基于 `get_node_dsl` 和截图分析重建

**变体维度：**
- 类型：`Default` | `WithAction`
- 状态：`Enabled` | `Disabled`

## 组成与用途

**导出项：**
- `SubHeader` - 主组件
- `subheaderTypes` - 类型枚举常量
- `subheaderStates` - 状态枚举常量
- `SubHeaderProps` - Props 类型
- `SubHeaderType` - 类型联合类型
- `SubHeaderState` - 状态联合类型

**使用场景：**
- 页面或区块的子标题栏
- 展示标题和副标题信息
- 可选右侧操作按钮（如"查看全部"、"更多"等）

## 量化规格

### 尺寸
| 元素 | 值 |
|------|------|
| 容器最小高度 | 72px |
| 容器内边距 | 16px |
| 标题与副标题间距 | 4px |

### 排版
| 元素 | 字号 | 字重 | 行高 | 字间距 |
|------|------|------|------|--------|
| 主标题 | 16px | 700 | 24px | 0 |
| 副标题 | 14px | 400 | 20px | 0 |
| 操作按钮 | 16px | 500 | 24px | 0 |

### 色值
| 元素 | Light 模式 | 变量引用 |
|------|------------|----------|
| 容器背景 | #ffffff | `--harmony-background-primary` |
| 主标题文字 | rgba(0,0,0,0.9) | `--harmony-font-primary` |
| 副标题文字 | rgba(0,0,0,0.6) | `--harmony-font-secondary` |
| 操作按钮文字 | #0a59f7 | `--harmony-font-emphasize` |
| 禁用状态文字 | rgba(0,0,0,0.2) | `--harmony-font-fourth` |

## 状态与交互

| 状态 | 表现 |
|------|------|
| Enabled | 正常交互，操作按钮可点击 |
| Disabled | 整体透明度 0.4，禁用指针事件 |

**交互反馈：**
- 操作按钮 hover：透明度 0.8
- 操作按钮 active：透明度 0.6

## Props

```typescript
interface SubHeaderProps extends HTMLAttributes<HTMLDivElement> {
  类型?: "Default" | "WithAction"  // 默认："WithAction"
  状态?: "Enabled" | "Disabled"   // 默认："Enabled"
  标题?: string                    // 默认："Content subheading"
  副标题?: string                  // 默认："subheading"
  操作文本?: string                // 默认："more"，text/arrow 右侧类型均使用该文案
  onAction?: () => void            // 操作按钮点击回调
  children?: ReactNode
}
```

### DSL ↔ Prop 对照

| DSL 属性 | Prop 名 | 取值集合 | 说明 |
|----------|---------|----------|------|
| 类型 | 类型 | Default, WithAction | 与 DSL 一致 |
| 状态 | 状态 | Enabled, Disabled | 与 DSL 一致 |
| 标题文字 | 标题 | 任意字符串 | 对应截图中的 "Content subheading" |
| 副标题文字 | 副标题 | 任意字符串 | 对应截图中的 "subheading" |
| 操作按钮文字 | 操作文本 | 任意字符串 | text / arrow 右侧类型显示的操作文案，默认 "more" |

## 样式引用

### 使用的 global.css 变量
| 变量名 | 用途 | 来源 |
|--------|------|------|
| `--harmony-background-primary` | 容器背景 | 现有 token |
| `--harmony-font-primary` | 主标题文字 | 现有 token |
| `--harmony-font-secondary` | 副标题文字 | 现有 token |
| `--harmony-font-emphasize` | 操作按钮文字 | 现有 token |
| `--harmony-font-fourth` | 禁用状态文字 | 现有 token |

### 新增 Token
无新增全局 Token，全部使用现有 Harmony 设计 token。

## 取舍说明

| 项目 | 说明 |
|------|------|
| 布局方案 | 使用 Flex 布局，左侧内容区 `flex: 1`，右侧操作按钮固定宽度 |
| 操作按钮样式 | 采用文字按钮样式，无背景和边框，与 Harmony 设计规范一致 |
| 禁用实现 | 使用 CSS `opacity` + `pointer-events: none`，简化实现同时保证视觉一致 |
| 字间距 | 截图中未显示明显字间距，设为 0 |

## 1:1 还原验证

**验证方式：** 人工对照截图 + 关键尺寸复算

**对照结论：**
- ✅ 容器高度 72px 与截图一致
- ✅ 标题字号 16px / 字重 700 与截图视觉一致
- ✅ 副标题字号 14px / 字重 400 / 灰色 与截图一致
- ✅ 操作按钮蓝色文字与截图一致
- ✅ 整体布局（左标题 + 右操作）与截图一致

**未执行自动 SSIM**，对照方式为人工复核 + 关键尺寸复算。
