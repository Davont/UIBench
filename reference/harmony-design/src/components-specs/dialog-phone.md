# DialogPhone 手机对话框

## Metadata

- 实现目录：`src/components/DialogPhone/`
- Stories 路径：`src/components/DialogPhone/DialogPhone.stories.tsx`
- Pixso 链接：`https://pixso.cn/app/design/QeDttX-H4qVEUZXJjNfTCw?item-id=59:34748`
- item-id：`59:34748`
- MCP 工具来源：`get_node_dsl`（成功）、`get_variants`（返回 `{}`，降级重建）、`get_screenshot`（失败，跳过）

## 组件变体树 JSON

- 路径：`src/components/DialogPhone/dialog-phone.json`
- 生成方式：`get_node_dsl` item `59:34748` 的 `pixTreeNodes` 8 个子实例 + `pixComponentTreeDslNodes` 交叉验证

## 组成与用途

| 组件 | 文件 | 用途 |
|------|------|------|
| `DialogPhone` | `DialogPhone.tsx` | 可选遮罩的对话框（受控 `open`） |
| `DialogPhonePanel` | `DialogPhone.tsx` | 纯面板，用于 Storybook 矩阵与内嵌场景 |

## 量化规格

### 共用面板 (Surface)
- 宽度：328px（`progress bar+button` 为 299px）
- 圆角：32px
- 填充：`rgba(255,255,255,0.9)` — `Light/Blur/COMPONENT_ULTRA_THICK` (616:9117)
- 效果：`BACKGROUND_BLUR` radius=80 → CSS `backdrop-filter: blur(40px)` — `Light/Blur/COMPONENT_ULTRA_THICK` (1:347)
- 字体：`HarmonyHeiTi`, `Geist Variable`, sans-serif

### 标题 (`.Items` / `2 Line=OFF|ON`)
- 字号：20px Bold — `Font/Title_S/Bold` (602:9702)
- 行高：26px
- 对齐：center
- 颜色：`rgba(0,0,0,0.9)` — `Light/font_primary` (602:9446)
- 单行区高度：56px（padding 15px 24px）— `2 Line=OFF` (1:11626)
- 双行区高度：72px（padding 12px 24px）— `2 Line=ON` (1:11600)
- 双行子标题：14px, `rgba(0,0,0,0.6)` — `Font/Subtitle_S/Regular` (602:9691) + `Light/font_secondary` (602:9447)

### 内容 (Text / `属性 1=1 Line|2 Line|默认`)
- 字号：16px Medium — `Font/Body_L/Medium` (602:9659)
- 行高：21px
- 对齐：center
- 颜色：`rgba(0,0,0,0.9)` — `Light/font_primary` (602:9446)
- 1 Line：280×21 — `属性 1=1 Line` (1783:9442)
- 2 Line：280×42 — `属性 1=2 Line` (1783:9440)

### 按钮 (Button)
- 尺寸：120×40px，圆角 20px
- 字号：16px Medium — `Font/Body_L/Medium` (602:9659)
- Normal：透明背景，文字 `rgba(10,89,247,1)` — `Light/brand` (602:9401)
- Emphasize：背景 `rgba(10,89,247,1)` — `Light/brand`，文字 `rgba(255,255,255,1)` — `Light/font_on_primary` (602:9443)

### 按钮组 (.Button Group)
| DSL 变体 | 布局 | 尺寸 | 间距 |
|----------|------|------|------|
| `normal,个数=1` (1:11558) | HORIZONTAL | 328×56 | — |
| `normal,个数=2` (1:11564) | HORIZONTAL sp=8 | 328×56 | 分割线 0.5×24 |
| `emphasize,个数=1` (58:36403) | HORIZONTAL sp=8 | 328×56 | — |
| `emphasize,个数=2` (1:11560) | HORIZONTAL sp=16 | 328×56 | — |
| `emphasize-port,个数=2` (58:36443) | VERTICAL sp=4 | 328×92 | — |
| `emphasize-port,个数=3` (1:11568) | VERTICAL sp=4 | 328×136 | — |

### 进度条 (.progress bar)
- 进度区域：200×48 — `类型=normal` (1:11619)
- 标题行（画板 10）：HORIZONTAL sp=8 → 标题(fs=14, secondary) + 百分比(fs=14, primary)
- 轨道行（画板 11）：HORIZONTAL sp=12 → .close(24×24) + 进度条(flex fill, 4px)
- 关闭按钮：24×24 — `.close` (76:9068)，xmark_circle_fill icon
- 轨道填充：`Light/comp_background_emphasize` (602:9414)
- 轨道底色：`Light/comp_background_tertiary` (602:9420)

### 各变体 Surface 规格
| 类型 | 尺寸 | 布局 | 间距 | 对齐 |
|------|------|------|------|------|
| content | 328×90 | HORIZONTAL | 10 | flex-start, flex-start |
| content+button | 328×109 | VERTICAL | 8 | flex-start, center |
| title+content_single line | 328×122 | VERTICAL | — | flex-start, center |
| title+content_2lines | 328×138 | VERTICAL | — | flex-start, flex-start |
| title+content+2 button | 328×162 | VERTICAL | 8 | flex-start, flex-start |
| title+content+3 button | 328×242 | VERTICAL | 8 | flex-start, flex-start |
| progress bar | 328×96 | HORIZONTAL | — | center, center |
| progress bar+button | 299×136 | VERTICAL | 8 | flex-start, center |

## 状态与交互

- `open` / `onOpenChange`：受控弹层
- `buttons[].onClick`：按钮回调
- `onClose`：进度条关闭按钮 + 遮罩点击
- `progress`：0–100，驱动进度条填充宽度
- `内嵌`：容器内嵌模式，overlay 通过 `position: absolute; inset: 0` 约束在父级手机容器内
- 按钮 hover：`Light/interactive_hover` (602:9466) → `var(--harmony-interactive-hover)`

## Props DSL ↔ Prop 对照

| DSL 字段 | Prop 名 | 取值 | 默认值 | 说明 |
|----------|---------|------|--------|------|
| 类型 | 类型 | 见 `dialogPhoneTypes` | `"content"` | 与 Pixso 实例名一致 |
| — | title | ReactNode | `"Title"` | 标题文案 |
| — | content | ReactNode | 设计稿占位 | 正文文案 |
| — | progress | number | `50` | 进度条百分比 |
| — | buttons | `DialogPhoneButton[]` | 按类型推导 | 业务按钮配置 |
| — | open | boolean | — | 受控开关 |
| — | onOpenChange | `(open) => void` | — | 开关回调 |
| — | onClose | `() => void` | — | 进度条关闭 |
| — | 内嵌 | boolean | `false` | 容器内嵌模式（见下方说明） |

### 内嵌模式（容器约束定位）

当 DialogPhone 在 Storybook / render 生成页的手机原型容器内使用时，默认的 `position: fixed; inset: 0` overlay 会逃逸出容器覆盖整个浏览器视口。只要父级是 `position: relative` 且承担移动端页面视口，就必须传入 `内嵌` prop，将 overlay 切换为容器约束模式：

| 模式 | overlay 定位 | overlay 尺寸 | z-index | 适用场景 |
|------|-------------|-------------|---------|----------|
| 默认 (`内嵌=false`) | `position: fixed; inset: 0` | 全屏视口 | 1000 | 全屏 Web 应用 |
| 内嵌 (`内嵌=true`) | `position: absolute; inset: 0` | 跟随父级手机容器 | 60 | Storybook / render 手机原型容器 |

实现原理：overlay 元素添加 `data-container="true"` 属性，CSS 通过属性选择器覆盖默认定位。与项目中 `.trip-share-overlay` 等手机页面遮罩的定位模式一致。

Agent 生成规则：在 `src/render/**`、Storybook 预览页、或任何 360/375 宽的移动端页面壳中渲染受控 `DialogPhone open={...}` 时，必须传 `内嵌`。只有当 DialogPhone 代表真实全屏 Web 应用级弹层时，才保留默认 fixed 模式。

用法示例：

```tsx
// 在手机原型容器中使用
<div style={{ position: "relative", width: 360, height: 797, overflow: "hidden" }}>
  <DialogPhone
    类型="title+content+2 button"
    open={showDialog}
    onOpenChange={setShowDialog}
    title="确认操作？"
    content="此操作不可撤销。"
    内嵌
  />
</div>
```

### 类型与内置按钮组映射

| 类型 | 按钮组 DSL | 布局 |
|------|-----------|------|
| `content+button` | `normal,个数=1` (1:11558) | 水平 |
| `progress bar+button` | `normal,个数=1` (1:11558) | 水平 |
| `title+content+2 button` | `emphasize,个数=2` (1:11560) | 水平 gap 16 |
| `title+content+3 button` | `emphasize-port,个数=3` (1:11568) | 垂直 gap 4 |

## 样式引用

### 使用的 global.css 变量
- `--harmony-font-primary` → 标题/正文/进度百分比
- `--harmony-font-secondary` → 进度标题
- `--harmony-font-on-primary` → 强调按钮文字
- `--harmony-brand` → 普通按钮文字/强调按钮背景
- `--harmony-comp-background-emphasize` → 进度条填充
- `--harmony-comp-background-tertiary` → 进度条轨道底色
- `--harmony-interactive-hover` → 按钮 hover
- `--harmony-icon-primary` → 关闭按钮图标

### 新增 CSS
- 无新增全局 Token；样式在 `dialog-phone.css`

## 取舍说明

1. `get_variants` 返回 `{}`，变体树由 `get_node_dsl` 8 个子实例 + `pixComponentTreeDslNodes` 交叉重建
2. `get_screenshot` 失败（transport dropped），未执行自动视觉回归；结构依据 `pixComponentTreeDslNodes` + `localStyleMap` 量化
3. `BACKGROUND_BLUR` radius=80 → CSS `blur(40px)`（Pixso→CSS 除以 2，见 CLAUDE.md 换算规则）
4. 按钮组 INSTANCE 未展开子树，通过兄弟组件定义（nodes 26–32）解析内部结构
5. `DialogPhonePanel` 用于静态矩阵；`DialogPhone` + `open` 提供真实弹层交互
6. **内嵌模式**：Storybook / render 的移动端页面容器为 `position: relative` + 固定手机尺寸，默认 `position: fixed` overlay 会逃逸。通过 `内嵌` prop + `data-container` 属性选择器切换为 `position: absolute; inset: 0` 约束在容器内。z-index 降至 60 适配页面层级体系（Aibottombar 50 > share-sheet 41）。此模式与 `.trip-share-overlay` 等已有遮罩模式一致
