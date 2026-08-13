# Pattern 组件规格

## Metadata

| 字段 | 值 |
|------|-----|
| 实现目录 | `src/components/Pattern/` |
| Stories 路径 | `src/components/Pattern/Pattern.stories.tsx` |
| Pixso 链接 | `https://pixso.cn/app/design/HA_e8I2mE7Oa0b5ZoeokSA?item-id=5322:2028` |
| Pixso item-id | `5322:2028` |
| MCP 工具来源 | `get_node_dsl` (5322:2028), `get_node_dsl` (3503:26192 — 默认主组件), `get_export_image` (4 变体) |
| Design-to-code | 不可用（返回 500），基于 DSL + 截图手工还原 |
| 插画兜底图标 | 本地 `HMSymbolIcon name="rectangle"`（U+F0070，旋转为竖屏设备轮廓） |

## 组件变体树 JSON

- 路径：`src/components/Pattern/pattern.json`
- 生成来源：`get_node_dsl` (5322:2028) → `pixTreeNodes` 子节点名称
- 降级说明：`get_variants` 返回空 `{}`，`variantOptions.布局` 从 DSL 中 4 个 INSTANCE 子节点的 `name` 字段提取

## 组成与用途

### 导出项

| 导出 | 类型 | 说明 |
|------|------|------|
| `Pattern` | 组件 | 设置页面布局模板，通过 `布局` prop 切换 4 个变体 |
| `PatternProps` | 类型 | 组件 Props 接口 |
| `PatternLayout` | 类型 | `"默认" \| "文本" \| "卡片" \| "插画"` |
| `patternLayoutOptions` | 常量 | `["默认", "文本", "卡片", "插画"] as const` |

### 使用场景

- 设置页面快速搭建：选择布局变体并传入卡片组、子标题等数据
- 设计系统 Pattern 展示：在 Storybook 中作为布局模板参考
- 页面原型开发：配合 `page-generation` Skill 生成完整的设置页

### 内部复用组件

| 组件 | 来源 | 使用位置 |
|------|------|----------|
| `TitleBar` | `src/components/TitleBar/` | 全部 4 个变体（顶部导航） |
| `SubHeader` | `src/components/SubHeader/` | 默认/文本/卡片 变体 |
| `ListPhone` | `src/components/ListPhone/` | 全部 4 个变体（卡片组内容） |
| `PopupTip` | `src/components/PopupTip/` | 卡片变体 |
| `Aibottombar` | `src/components/Aibottombar/` | 插画变体 |

## 量化规格

### 尺寸

| 元素 | 宽度 | 高度 | 备注 |
|------|------|------|------|
| Phone 容器 | 360px | 792px | `pattern__phone`，bg=rgba(241,243,245,1)，r=24px |
| TitleBar 区域 | 328px | 56px | 距顶 36px（状态栏高度），距左 16px |
| SubHeader 区域 | 328px | 72px | 距左 16px |
| 卡片组（Card Group） | 328px | 104px | bg=white，r=20px，含 2 个 ListPhone（各 48px） |
| 描述文字块（文本变体） | 304px | 57px~ | 14px/19px，距左 28px |
| 脚注（Footnote） | 304px | 16px | 12px/16px，距左 28px |
| PopupTip（卡片变体） | 312px | 114px | r=20px，距顶 100px |
| 插画区域（插画变体） | 288px | 288px | r=20px，bg=white，距顶 92px |
| 插画标题 | 312px | 27px | 20px/700，text-align:center |
| 插画描述 | 312px | 38px | 14px/19px，text-align:center |
| Swiper 圆点 | 360px | 32px | 3 个 8×8 圆点，8px 间距 |
| Aibottombar | 360px | 28px | 底部绝对定位 |

### 圆角

| 元素 | 圆角值 |
|------|--------|
| Phone 容器 | 24px |
| 卡片组 | 20px |
| PopupTip | 20px |
| 插画区域 | 20px |

### 色值

| 元素 | Pixso 样式 | 对应 Token | 值 |
|------|-----------|-----------|-----|
| 页面背景 | Solid fill | `--harmony-background-secondary` | rgba(241, 243, 245, 1) |
| 卡片组背景 | Solid fill | `--harmony-comp-background-primary` | rgba(255, 255, 255, 1) |
| 主文字 | — | `--harmony-font-primary` | rgba(0, 0, 0, 0.9) |
| 次要文字 | — | `--harmony-font-secondary` | rgba(0, 0, 0, 0.6) |
| 三级文字（脚注） | — | `--harmony-font-tertiary` | rgba(0, 0, 0, 0.4) |
| 分隔线 | — | `--harmony-comp-divider` | rgba(0, 0, 0, 0.2) |
| Swiper 非激活点 | — | `--harmony-font-fourth` | rgba(0, 0, 0, 0.2) |

### 字体

| 元素 | 字号 | 字重 | 行高 | 字间距 |
|------|------|------|------|--------|
| 描述文字 | 14px | 400 | 19px | — |
| 脚注 | 12px | 400 | 16px | — |
| 插画标题 | 20px | 700 | 27px | — |
| 插画描述 | 14px | 400 | 19px | — |

## 状态与交互

Pattern 组件是纯展示型布局模板，无交互状态。所有交互由内部子组件（TitleBar、ListPhone、PopupTip 等）各自处理。

| 子组件 | 状态 |
|--------|------|
| TitleBar | leadingAction 返回按钮（hover/active 由 TitleBar 内部处理） |
| ListPhone | 可点击行（hover/active 由 ListPhone 内部处理） |
| PopupTip | 仅为展示（close=false, Link=false） |
| Aibottombar | 纯装饰 |

## Props

### `PatternProps`

| Prop | 类型 | 默认值 | DSL 字段 | 描述 |
|------|------|--------|----------|------|
| `布局` | `"默认" \| "文本" \| "卡片" \| "插画"` | `"默认"` | `设置布局` | 布局变体 |
| `titleBarTitle` | `string` | `"设置"` | — | TitleBar 标题 |
| `cardGroups` | `PatternCardGroup[]` | 按变体预设 | — | 卡片组数据 |
| `subHeaders` | `PatternSubHeader[]` | 按变体预设 | — | 子标题数据 |
| `footnote` | `string` | 预设文案 | — | 脚注文字 |
| `description` | `string` | 预设文案 | — | 描述文字（文本变体） |
| `popupTipTitle` | `string` | `"新功能提示"` | — | PopupTip 标题（卡片变体） |
| `popupTipDescription` | `string` | 预设文案 | — | PopupTip 描述 |
| `illustrationTitle` | `string` | `"个性化您的专属设置"` | — | 插画标题（插画变体） |
| `illustrationDescription` | `string` | 预设文案 | — | 插画描述 |
| `illustrationSrc` | `string` | `""` | — | 插画图片 URL |
| `illustrationChildren` | `ReactNode` | — | — | 插画区域自定义内容 |

### DSL ↔ Prop 对照

| DSL 字段/路径 | Prop 名 | 说明 |
|---------------|---------|------|
| `设置布局`（INSTANCE name → variant） | `布局` | 中文直用，无命名映射 |

## 样式引用

### 使用的全局 Token

| Token | 用途 |
|-------|------|
| `--harmony-background-secondary` | 页面背景 (#f1f3f5) |
| `--harmony-comp-background-primary` | 卡片组/插画区域背景 (#ffffff) |
| `--harmony-font-primary` | 插画标题、Swiper 活跃点 |
| `--harmony-font-secondary` | 描述文字、次要信息 |
| `--harmony-font-tertiary` | 脚注文字 |
| `--harmony-font-fourth` | Swiper 非活跃点 |
| `--harmony-comp-divider` | （ListPhone 内部使用） |

### 新增全局 Token

无。本组件全部复用已有 Token。

## 取舍说明

1. **卡片组（CardGroup）内联渲染**：未抽取为独立组件，原因是 328×104 白底圆角容器 + 2 个 ListPhone 的组合模式目前仅在设置页中使用，尚不足以作为通用组件提取。若其他页面出现相同模式，可后续重构。

2. **Swiper 圆点简化实现**：Pixso 设计中包含 `Navigation/Swiper/Phone/Dot` 组件，此处以 3 个 8×8 的 SVG 圆点直接实现，理由：(a) Swiper 组件是为轮播横幅设计的完整组件，仅引用其圆点部分会引入不必要的复杂性；(b) 3 个静态圆点仅需简单的 CSS，无需 Swiper 的全套交互逻辑。

3. **Pixso INSTANCE 子节点不可展开**：Pattern 的 4 个变体子节点是 COMPONENT INSTANCE 类型，`get_node_dsl` 返回的是实例元数据而非展开的子节点树。变体的内部结构（TitleBar、SubHeader、ListPhone 等）是通过 `pixComponentTreeDslNodes`（默认变体，3503:26192）获取的验证证据。

4. **设计截图不可查看**：本环境的 Pixso `get_screenshot` 返回 `[Unsupported Image]`，`get_export_image` 的导出图片同样无法渲染。1:1 还原以 DSL 量化参数为准，并通过 Storybook Overview 矩阵进行人工视觉对照。

5. **No design_to_code**：Pixso `design_to_code` API 对 Pattern 节点和所有子变体均返回 500，CSS 资源不可用。所有样式基于 DSL 坐标、颜色、排版参数手工推导。

## 附录：MCP 调用清单

| 工具 | 目标节点 | 结果 |
|------|----------|------|
| `get_screenshot` | 5322:2028 | 不可查看 |
| `get_node_dsl` | 5322:2028 | 成功（Pattern 框架 + 4 INSTANCE 子节点） |
| `get_node_dsl` | 5322:1206 | 成功（默认变体 INSTANCE 元数据） |
| `get_node_dsl` | 5322:1672 | 成功（文本变体 INSTANCE 元数据） |
| `get_node_dsl` | 3503:26192 | 成功（默认变体主组件，含 pixComponentTreeDslNodes） |
| `get_variants` | 5322:2028 | 返回空 `{}` |
| `get_all_components` | — | 成功（数据量大，Pattern 关键词无匹配） |
| `get_export_image` | 5322:2028 | 成功下载（748KB，不可查看） |
| `get_export_image` | 5322:1206 | 成功下载（164KB，不可查看） |
| `get_export_image` | 5322:1672 | 成功下载（186KB，不可查看） |
| `get_export_image` | 5322:1841 | 成功下载（187KB，不可查看） |
| `get_export_image` | 5322:1406 | 成功下载（140KB，不可查看） |
| `design_to_code` | 5322:2028, 5322:1206 | 均返回 500 |
