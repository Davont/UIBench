# Layout: mobile-settings

> 来源：`history/spec/1.layout/layout.md` - mobile-settings-single-column

## hit_rules

命中 `mobile-settings` 时，页面应同时满足以下特征：
- 画布为单屏移动端竖向比例，页面主内容位于居中的单列内容区
- 顶部存在稳定壳层：`status bar` 与 `titlebar` 连续排列
- 主体内容以圆角卡片为核心容器，卡片按单列自上而下堆叠
- 卡片内部以设置项行为主，典型行为"标签 + 值 + 箭头"或"标签 + 控件"
- 页面底部可以存在说明文案，但无强制性的主操作区
- 信息组织优先按设置语义分组

## exclusion_rules

出现以下任一特征时，不应命中该布局：
- 顶部存在 tab、segmented control、二级导航切换，且其成为页面主导航
- 页面主体被 `subheader` 分成多个独立内容区块
- 底部存在固定主 CTA、双按钮操作栏或工具栏
- 页面主体为表单录入、富内容详情、图表看板或多列排版
- 卡片内部以网格、时间轴、内容流为主，而不是设置行
- 页面必须依赖逐元素绝对定位才能成立

## reference_blocks

- `settings-page`

## layout_skeleton

```html
<main class="layout-mobile-settings">
  <section class="layout-status-bar"></section>
  <header class="layout-titlebar"></header>
  <section class="layout-content">
    <section class="layout-card layout-card-entry"></section>
    <section class="layout-card layout-card-group"></section>
    <p class="layout-note"></p>
  </section>
  <footer class="layout-home-indicator"></footer>
</main>
```

### Shell Rules

| 区域 | 高度 | 说明 |
|------|------|------|
| status bar | 36px | 贴顶，系统壳层 |
| titlebar | 56px | 紧接状态栏下方 |
| content | flex | 单列卡片堆叠 |
| home indicator | 28px | 底部系统区域 |

### Content Width
- 主内容标准宽度：`328px`
- 水平居中，左右边距各 `16px`

## needed_components

- `status-bar`
- `title-bar`
- `hmsymbol-icon`
- `list-phone`
- `switch-phone`

## composition_mapping

| Layout Block | Component | Variant / Composition |
|---|---|---|
| `status bar` | `status-bar` | harmony-public + theme(light/dark) |
| `titlebar` | `title-bar` | default，左侧返回、标题、右侧可选 |
| `Hero Card` | `hero-card` | 244×220 r=24 毛玻璃面板，居中 icon + title + subtitle + 底部整宽 CTA 胶囊按钮 |
| `Entry Card` | `list-phone` | 外层 card container + trailing value + chevron |
| `Group Card` | `list-phone` + `switch-phone` / divider | 多行设置组，首行可为 switch |
| `Informational Note` | plain text | 非卡片文本块，font_secondary |

## generation_constraints

- 禁止把整页实现为连续的匿名 frame 容器
- 禁止把所有区块写成逐元素绝对定位；只允许壳层级固定区
- 禁止卡片嵌套卡片；如需表达层级，优先通过卡片内部分区、行组、留白或分割线处理
- 禁止在卡片表面大面积使用渐变色阴影来刻意凸显视觉重心；卡片强调应优先依赖内容层级、间距、圆角与轻量实色阴影
- 卡片内容必须以可复用的 entry row / setting row / control row / note 组织
- 卡片内部优先使用 flex 或纵向流式布局
- 右侧值区必须保持最小宽度
- 设置行优先复用 `list-phone` 承载行级布局
- 普通设置行左侧系统图标默认使用 `ListPhone left="24dp_ic" + leftIconName`；不得通过 `leftSlot`、匿名 `div` 或 `<HMSymbolIcon size={20} />` 自行拼装或改变默认尺寸。
- 彩色图标瓦、头像或图片仅在设计稿明确要求时使用受控变体，并在页面日志记录设计稿依据；彩色底板上的图标前景遵循 `hmsymbol-icon` 规格。

## semantic_tokens

| Semantic Part | Token |
|---|---|
| Page canvas | `comp_background_gray` |
| Card surface | `comp_background_primary` |
| Title / primary labels | `font_primary` |
| Right-side value / note | `font_secondary` |
| Primary icons | `icon_primary` |
| Secondary icons / chevron | `icon_secondary` |
| Divider | `comp_divider` |

## validation_notes

- 验收 checklist 参见 `history/spec/1.layout/layout.md` Section 15
- 必须能映射到 `list-phone` 组件的行级布局
- 卡片堆叠顺序与 reference block 一致
- 验收时确认不存在 card-in-card 结构
- 验收时确认卡片未通过大面积渐变色阴影制造视觉主次
- Build 通过且 Storybook 组件故事存在
