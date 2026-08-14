# Mobile Design Tokens

该目录独立承载 UIBench 移动端多品牌风格与明暗主题功能，避免重排原项目结构。

- `tokens.json`：HarmonyOS、Spotify、Netflix、Notion 四套主题，每套包含
  `light` / `dark` 两种模式。
- `__init__.py`：Token 校验、CSS Variables、Tailwind Theme Preset 和 HTML 注入。

约束：

- 所有风格必须实现完全相同的语义 Token Key。
- 每套主题中的 Light 与 Dark 必须拥有完全相同的模式 Token Key。
- 字体、间距和圆角属于各风格的 `shared`，切换明暗模式时保持不变。
- 模型生成的移动端 HTML 只使用 Tailwind。系统注入的 `ui-*` theme key 把 Tailwind
  utility 映射到 Token CSS Variables；模型不直接写变量、颜色或 `dark:*`。
- `data-token-theme` 选择设计体系，`data-theme` 选择明暗模式。
- 主题切换由 UIBench 渲染器控制，不重新调用模型，也不复制页面 DOM。

当前模型侧接口：

```html
<main class="bg-ui-canvas text-ui-fg font-ui px-ui-page">
  <section class="bg-ui-surface rounded-ui-card p-ui-card mt-ui-section">
    <button class="bg-ui-primary text-ui-on-primary hover:bg-ui-primary-hover">
      继续
    </button>
  </section>
</main>
```

`ui-page`、`ui-section`、`ui-card`、`ui-item`、`ui-compact` 是 Tailwind spacing
key，而不是另一套类名，因此 `px-ui-card`、`gap-ui-card`、`ml-ui-item` 等标准
方向组合都由 Tailwind 生成。底层 `--dt-*` 变量和旧 `dt-*` utility 只供主题编译与
历史 HTML 兼容，不再暴露给新生成 Prompt。

Token 颜色不接受 Tailwind 的 `/10`、`/20`、`/90` 透明度后缀，因为跨主题透明度必须
由稳定语义决定。生成结果中的常见写法会在保存和预览前自动归一化：

- `bg-ui-primary/10` → `bg-ui-primary-container-subtle`
- `bg-ui-surface-raised/90` → `bg-ui-surface-raised`
- `bg-ui-warning/15` → `bg-ui-warning-container`
- `shadow-ui-primary/20` → `shadow-ui-surface`

HarmonyOS 普通内容卡片以白色表面和灰色画布建立层级，默认不使用整圈描边或表面阴影；
卡片内部列表使用 `border-b-ui-hairline border-ui-divider` 绘制视觉 0.5px 发丝线，
且最后一行不绘制。为兼容历史生成结果，HarmonyOS 主题会忽略同时带有
`bg-ui-surface rounded-ui-card border border-ui-border` 的普通卡片外框，其他主题不受影响。

当前风格定位：

- `harmonyos`：依据 HarmonyOS 官方语义色映射宇宙蓝、雪域灰、明暗表面层级和
  交互叠加色，并使用 HarmonyOS Sans 字体栈。
- `spotify`：亮绿、高对比深色表面、胶囊控件和内容优先的音乐应用风格。
  `accent` 兼容性地映射到绿色 `primary`，不再引入无当前官方语义依据的
  洋红第二品牌色。
- `netflix`：Netflix Red、黑色画布和高对比沉浸式媒体风格。
- `notion`：黑白灰、暖白纸张和低圆角的内容优先风格。

v3 契约增加 `accent` / `accent-hover` / `on-accent`，对应
`dt-bg-accent` / `dt-bg-accent-hover` / `dt-text-accent` / `dt-text-on-accent`，
用于表达品牌主题中的辅助强调层级；在 HarmonyOS 中它们兼容性地映射到主色，
不再引入非官方的紫色。

Spotify 同样将 `accent` 组映射到 `primary` 绿色：之前的
`#AF2896` / `#E133C5` 是 UIBench 人为补充的装饰色，不是当前 Encore 的
通用品牌 `accent` 语义。新生成页面不得为了颜色丰富而自由使用
`dt-bg-accent`；一般 CTA、选中态和品牌强调应使用 `primary` 语义。

v4 契约增加两类语义 Token：

- `primary-container` / `primary-container-subtle`：主色 20% / 10% 高亮容器，
  对应 `dt-bg-primary-container` / `dt-bg-primary-container-subtle`。
- `interaction-hover` / `interaction-pressed` / `interaction-selected`：悬停、按压、
  选中叠加色，对应 `dt-interaction-hover` / `dt-interaction-pressed` /
  `dt-interaction-selected`。它们与背景类组合使用，不再为每个状态发明新的实色。

`primary-hover` 与旧 utility 暂时保留供历史 HTML 兼容；新生成内容使用
`bg-ui-primary hover:bg-ui-primary-hover`。

v5 契约补充 `canvas-translucent` 与辅助强调色容器，用于粘性顶部栏和低强调色块，
对应 `dt-bg-canvas-translucent`、`dt-bg-accent-container`、
`dt-bg-accent-container-subtle`。渲染前会把常见的模型误写规范化为正式类名，例如：

- `dt-rounded-full` → `dt-rounded-pill`
- `dt-bg-canvas/90` → `dt-bg-canvas-translucent`
- `dt-bg-primary/10` → `dt-bg-primary-container-subtle`
- `hover:dt-bg-*` / `active:dt-bg-*` → `dt-interaction-hover` /
  `dt-interaction-pressed`
- `focus:dt-focus` / `placeholder:dt-placeholder-secondary` → 无前缀的正式类名
- `dt-py-3` → `dt-py-card`

间距契约还提供 `dt-mb-section`、`dt-mt-compact` 和 `dt-py-card`，分别使用主题的
section、compact 和 card 空间值；浏览器 CSS 与 ArkUI 快照因此共享同一套间距语义。

v6 契约拆分背景层级与组件填充，修正了把 HarmonyOS 官方 `#E5E5EA` 直接作为
轻量组件背景的语义错误：

- `layer-secondary` / `layer-tertiary` 是不透明背景层级，对应
  `dt-bg-layer-secondary` / `dt-bg-layer-tertiary`。HarmonyOS Light 的
  `#E5E5EA` 只保留在 `layer-tertiary`。
- `component-subtle` / `component-secondary` 是组件填充，对应
  `dt-bg-component-subtle` / `dt-bg-component-secondary`。HarmonyOS 使用约
  4.7% / 9.8% 的黑白叠加色，因此会根据组件所在表面正确合成。
- `text-tertiary` / `text-fourth` 补充三级、四级文字；HarmonyOS 分别使用
  40% / 20% 黑白透明度。
- `border` 仅作为较强组件轮廓，`divider` 独立承担轻量列表分割线。HarmonyOS 的
  `divider` 使用 20% 黑/白并配合视觉 0.5px 发丝线，而不是作为 1px 卡片外框。

HarmonyOS 映射以当前官方色彩指南为主，并用官方组件资源交叉验证：品牌色、状态基础色、
文字透明度、背景层级和交互叠加色属于官方语义映射；`canvas-translucent`、状态容器、
禁用色、遮罩和阴影仍是 UIBench 为统一跨主题合约提供的扩展值，不应表述为鸿蒙官方
Token。`border` 和 `divider` 即使色值相同，也必须按几何与组件角色区分：前者只用于
明确的强轮廓，后者只用于列表内部的发丝分隔，二者不能互换。

- HarmonyOS 色彩设计指南：<https://developer.huawei.com/consumer/cn/doc/design-guides/color-0000001776857164>
- HarmonyOS 官方设计资源：<https://developer.huawei.com/consumer/cn/design/resource/?open_in_browser=true>

`surface-subtle` 与 `dt-bg-surface-subtle` 暂时保留供历史 HTML 使用；新生成内容必须
选用明确的 `layer-*` 或 `component-*` 语义。

无法规范化的旧 utility 或未知 `ui-*` Tailwind theme key 会保留并写入服务日志，
便于继续完善契约，而不会中断该模型其余 HTML 的预览。

这些 Token 是为 UIBench 统一语义契约制作的兼容映射，不代表导入了对应设计系统的
完整组件库；后续可继续从组件级 Token 扩展。
