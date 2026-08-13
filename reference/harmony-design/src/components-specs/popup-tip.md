# PopupTip — 浮动提示气泡

## Metadata

| 属性 | 值 |
|------|-----|
| 实现目录 | `src/components/PopupTip` |
| stories 路径 | `src/components/PopupTip/PopupTip.stories.tsx` |
| Pixso 链接 | https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5410:23937 |
| MCP 工具来源 | Pixso MCP (`get_node_dsl`, `get_screenshot`, `get_export_image`, `design_to_code`) |
| 变体树 JSON | `src/components/PopupTip/popup-tip.json` |

## 组件变体树 JSON

- 路径：`src/components/PopupTip/popup-tip.json`
- 生成方式：`get_variants` 返回 `{}`，降级从 PopupTip 根节点 `get_node_dsl` 的子 INSTANCE 名称提取 `variantOptions`
- `variantOptions.类型` 包含 6 个变体值

## 组成与用途

| 导出项 | 类型 | 说明 |
|--------|------|------|
| `PopupTip` | React.FC | 主组件 |
| `popupTipTypes` | readonly tuple | 类型枚举常量 |
| `CloseIcon` | React.FC | 本地 `HMSymbolIcon name="xmark"`（U+F0056） |
| `TextLink` | React.FC | 文本链接子组件 |
| `PopupTipProps` | TypeScript interface | 组件 Props 类型 |
| `PopupTipType` | TypeScript type | 类型 取值联合类型 |

## 量化规格

### 尺寸

| 变体 | 宽度 | 高度 | Padding | Gap |
|------|------|------|---------|-----|
| Text | 312px | 44px | 12px | 10px |
| Text inline | 312px | 36px | 8px 16px | 10px |
| multiline text | 312px | 90px | 12px | 12px |
| multiline text inline | 312px | 90px | 12px | 12px |
| Full pattern | 312px | 114px | 12px | 12px |
| Full pattern inline | 312px | 114px | 12px | 12px |

### 圆角

- 容器：`border-radius: 20px`（所有变体）
- 图片：`border-radius: 8px`（Full pattern 变体）

### 颜色

| 元素 | Token | Pixso 来源 |
|------|-------|-----------|
| 卡片背景 | `--harmony-floating-ultra-thick-surface` | PopupBasic / Light Blur COMPONENT_ULTRA_THICK + `comp_background_tertiary` 叠层 |
| 主文本 | `--harmony-font-primary` (rgba(0,0,0,0.898)) | DSL 602:9446 |
| 次要文本 | `--harmony-font-secondary` (rgba(0,0,0,0.6)) | DSL 602:9447 |
| 链接文本 | `--harmony-font-emphasize` (rgba(10,89,247,1)) | DSL 602:9440 |
| 关闭图标 | `--harmony-icon-primary` (rgba(0,0,0,0.898)) | DSL `cancel6.svg` 与本地 `xmark` 形状比对后统一替换 |
| 默认图片 | `src/components/PopupTip/assets/popup-tip-default-image.png` | Pixso codegen 资源 `54c43711510c0bafc42c4db5cfe862f7ab41b580.png` |

### 字体

| 元素 | fontSize | fontWeight | lineHeight | letterSpacing | fontFamily |
|------|----------|------------|------------|---------------|------------|
| 标题 (Full pattern) | 16px | 500 (Medium) | 22px | normal | HarmonyHeiTi-Medium |
| 正文 (Text variants) | 14px | 400 | 20px | normal | HarmonyHeiTi |
| 描述 (multiline/Full pattern) | 14px | 400 | ~19px | normal | HarmonyHeiTi |
| 链接文本 | 14px | 500 (Medium) | 20px | normal | HarmonyHeiTi |

### 效果（Glass Morphism）

**非 inline 变体（Text, multiline text, Full pattern）：**

- 复用全局材质类 `hm-material-floating-ultra-thick`
- 背景：`--harmony-floating-ultra-thick-surface`
- 阴影：`--harmony-floating-ultra-thick-shadow`
- 高光 / 边缘：`--harmony-floating-ultra-thick-highlight` 与 `--harmony-floating-ultra-thick-edge`
- 模糊：`--harmony-floating-ultra-thick-backdrop`
- 图片：`drop-shadow(0 0 50px rgba(0,0,0,0.15))`

**inline 变体：**

- 仅保留 `--harmony-floating-ultra-thick-surface` 的表面叠层
- 不启用 backdrop blur、edge highlight、outer shadow（对应 DSL `effects.visible: false`）

### 布局

- 水平 Flex 行（`flex flex-row`）
- 内容列垂直 Flex（`flex flex-col`）
- 链接行水平 Flex（`flex flex-row gap-4`）
- 关闭按钮 `shrink-0`, 文本内容 `flex-1 min-w-0`

### 关键坐标

| 元素 | 尺寸 | 位置 |
|------|------|------|
| 关闭按钮 | 18×18px | 右上角，与文本同行 |
| 图片 | 32×32px | 左侧 |
| 链接按钮 | 75×20px | 底行，间距 16px |
| 描述文本 | 38px 高度 | 2 行截断 |

## 状态与交互

| 状态 | 行为 |
|------|------|
| default | 显示卡片 |
| 点击 close | 触发 `onClose` 回调；可由父组件控制 `close` prop 隐藏按钮 |

## Props

### DSL ↔ Prop 对照

| DSL 字段 | Prop 名 | 类型 | 默认值 | 合法取值 | 说明 |
|----------|---------|------|--------|---------|------|
| `visible_27_7` / `close` | `close` | `boolean` | `true` | `true \| false` | 关闭按钮可见性 |
| `visible_27_9` / `image` | `image` | `boolean` | `true` | `true \| false` | 图片可见性（Full pattern） |
| `visible_27_11` / `Link` | `Link` | `boolean` | `true` | `true \| false` | 链接按钮可见性 |
| INSTANCE name `类型=*` | `类型` | `PopupTipType` | `"Text"` | 6 个枚举值 | 变体选择器 |
| 节点 text | `title` | `string` | DSL AAAA... | 任意字符串 | 主文本 / 标题 |
| 节点 text | `description` | `string` | DSL AAAA... | 任意字符串 | 描述文本 |
| 节点 text | `linkText1` | `string` | `"Text button"` | 任意字符串 | 链接文本 1 |
| 节点 text | `linkText2` | `string` | `"Text button"` | 任意字符串 | 链接文本 2 |
| image src | `imageSrc` | `string` | `undefined` | URL | 图片源 |

### 命名说明

`close`, `image`, `Link` 直接使用 DSL `propDefMap` 中的 `name` 字段，不做翻译。`类型` 使用 DSL INSTANCE 名称中的中文变体属性名。所有 `propDefMap` 中的默认值与合法取值集合均与 DSL 一致。

## 样式引用

### 使用的全局 Token（`global.css`）

| Token | 适用范围 |
|-------|---------|
| `--harmony-font-primary` | 主文本颜色 |
| `--harmony-font-secondary` | 描述文本颜色 |
| `--harmony-font-emphasize` | 链接文本颜色 |
| `--harmony-icon-primary` | 关闭图标颜色 |
| `--harmony-floating-ultra-thick-surface` | 浮层表面背景 |
| `--harmony-floating-ultra-thick-shadow` | 非 inline 材质阴影 |
| `--harmony-floating-ultra-thick-backdrop` | 非 inline 毛玻璃 |
| `--harmony-floating-ultra-thick-highlight` | 非 inline 顶部高光 |
| `--harmony-floating-ultra-thick-edge` | 非 inline 内边缘 |

### 新增 Token

无。所有样式均复用已有 `global.css` Token + Tailwind arbitrary values。

## 取舍说明

| 项目 | 说明 |
|------|------|
| `get_variants` 返回 `{}` | `variantOptions` 从 INSTANCE 名称正则提取降级重建 |
| `get_screenshot` 可用 | 以截图做主视觉真值，同时使用 `get_export_image` 落盘对照 |
| `design_to_code` | 仅作为结构草案；最终以 DSL 与截图回校正文案、间距与材质层 |
| PopupBasic 箭头包装 | 当前节点内部已将 `Arrow=false`，因此实现只保留弹层本体，不渲染箭头 |
| 字体回退 | 显式引入 `src/styles/harmony-heiti-fallback.css`，文本统一走 HarmonyHeiTi 字体栈 |
| Storybook 校验基线 | `Overview` story 使用 Pixso 原始 2×3 排布、默认文案与默认图片，直接对照 `item-id=5410:23937` |
