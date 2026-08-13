# HarmonyOS 组件库 · AI 生成指南

（本文件由 tools/build-harmony-ai-guide.mjs 生成，组件库版本 1665f909）

## 0. 输出契约

1. 只输出 **body 内的内容**（从页面根 `<div>` 开始），页面壳（DOCTYPE/head/CSS 引入）由系统提供，不要输出。
2. 组件骨架必须从本指南**逐字符复制**后仅修改文本内容与图标；不得增删改组件内部的标签结构与类名。
3. **严禁凭记忆编造类名**：除骨架里的类和 Tailwind 工具类外，不得出现任何自创语义类（如 `card`、`title-bar`、`xxx__item` 这类仿冒类没有任何样式，页面会裸奔）。指南里没有的界面结构，用 Tailwind 工具类 + 内联 style 直接画。
4. 布局粘合（组件之间的排列、间距）使用 Tailwind 工具类或内联 style；**禁止** `<style>` 块、`<script>`、外部图片/字体/CDN 引用。
5. 页面按 390px 宽手机视口设计，整页可滚动区域用 `overflow-y-auto`。
6. 图片位置用纯色块或 CSS 渐变占位（内联 style），不要外链图片。

## 1. 章法规则

- 页面背景 `#F1F3F5`；内容卡片白底、圆角 16px（`rounded-2xl`）。
- 页面左右边距 **16px**（`px-4`）；卡片之间 **12px**（`gap-3`）；分组之间 **24px**（`mt-6` 或 SubHeader 分隔）。
- 文字层级：标题 17px 加粗、正文 14px、辅助 12px；辅助色 `rgba(0,0,0,0.4)`，正文色 `rgba(0,0,0,0.9)`。
- 固定结构：TitleBar 永远在最顶部（二级页面用带返回变体）；BottomTab 永远吸底且最多一个；主操作 Button（Emphasize 蓝色）每屏至多一个。
- 一屏（844px 高）内容密度：大卡片 ≤3 张，列表行 ≤8 行；宁可留白不要拥挤。
- 严格只做需求里提到的内容，不自行添加需求外的区块。

## 2. 页面骨架模板（先选一个，再往槽位里填组件）

### 模板：detail-page

```html
<!-- 页面模板：详情页（内容主体 + 主操作；TitleBar 用二级返回变体） -->
<div class="flex flex-col h-screen" style="background:#F1F3F5">
  <header class="shrink-0">
    <!-- 槽位：TitleBar 组件（secondary-page 变体，带返回） -->
  </header>
  <main class="flex-1 overflow-y-auto pb-4">
    <!-- 头图/主视觉区：通栏无边距；纯色块或图片，高度 180-240px -->
    <section class="w-full">
      <!-- 槽位：头图 / 大卡片 -->
    </section>
    <!-- 信息区：白底圆角卡片，页面边距 16px，卡片内边距 16px -->
    <section class="mx-4 mt-3 rounded-2xl bg-white p-4 flex flex-col gap-2">
      <!-- 标题 17px 加粗、正文 14px、辅助文字 12px 灰色（rgba(0,0,0,0.6)） -->
    </section>
    <section class="mx-4 mt-3 rounded-2xl bg-white p-4">
      <!-- 槽位：更多信息分组 / ListPhone / RatingPhone 等 -->
    </section>
  </main>
  <!-- 底部主操作：白底、上分割线，主按钮通栏 -->
  <footer class="shrink-0 px-4 py-3 bg-white" style="border-top:0.5px solid rgba(0,0,0,0.1)">
    <!-- 槽位：Button 组件（Emphasize 主按钮，宽度撑满） -->
  </footer>
</div>
```

### 模板：form-page

```html
<!-- 页面模板：表单页（输入、选择、开关 + 提交；TitleBar 二级返回） -->
<div class="flex flex-col h-screen" style="background:#F1F3F5">
  <header class="shrink-0">
    <!-- 槽位：TitleBar 组件（secondary-page 变体） -->
  </header>
  <main class="flex-1 overflow-y-auto px-4 pt-2 pb-6 flex flex-col gap-3">
    <!-- 表单分组：白底圆角卡片包裹同类字段；字段之间用 Divider 分隔 -->
    <section class="rounded-2xl bg-white px-4 py-1 flex flex-col">
      <!-- 槽位：TextInputBoxPhone / Select / Counter 等输入控件，纵向排列 -->
      <!-- 每个字段行高约 56px，字段间插入 Divider 组件 -->
    </section>
    <section class="rounded-2xl bg-white px-4 py-1 flex flex-col">
      <!-- 槽位：开关类字段（左标签 + 右 SwitchPhone/CheckBox），行高 48-56px -->
    </section>
    <!-- 说明文字：12px，rgba(0,0,0,0.4)，边距同页面 -->
    <p class="text-xs px-1" style="color:rgba(0,0,0,0.4)"><!-- 槽位：表单说明（可选） --></p>
  </main>
  <footer class="shrink-0 px-4 py-3">
    <!-- 槽位：Button 组件（Emphasize 主按钮通栏；次要操作用 Normal 变体并排） -->
  </footer>
</div>
```

### 模板：list-page

```html
<!-- 页面模板：列表页（设置、消息、目录等；TitleBar + 分组列表） -->
<div class="flex flex-col h-screen" style="background:#F1F3F5">
  <!-- 标题栏：一级页用 normal 变体，二级页用带返回箭头的 secondary 变体 -->
  <header class="shrink-0">
    <!-- 槽位：TitleBar 组件 -->
  </header>
  <main class="flex-1 overflow-y-auto px-4 pt-2 pb-6 flex flex-col gap-3">
    <!-- 每个分组：可选 SubHeader 做组标题，下面跟一个 ListPhone 列表卡片 -->
    <section>
      <!-- 槽位：SubHeader（可选） + ListPhone（列表项在卡片内部，白底圆角） -->
    </section>
    <!-- 分组之间间距 12px（gap-3 已提供）；需要更强分隔时组前加 mt-3 -->
    <section>
      <!-- 槽位：下一组 -->
    </section>
  </main>
</div>
```

### 模板：tab-home

```html
<!-- 页面模板：Tab 首页（顶部搜索 + 分类 Tab + 内容流 + 底部导航） -->
<div class="flex flex-col h-screen" style="background:#F1F3F5">
  <!-- 顶部固定区：状态栏高度已由壳处理，从搜索框开始 -->
  <header class="shrink-0 px-4 pt-3 pb-2" style="background:#F1F3F5">
    <!-- 槽位：Search 组件（328 宽度自动适配，居中） -->
  </header>
  <!-- 分类 Tab：横向滚动，紧贴搜索框 -->
  <nav class="shrink-0 pb-1">
    <!-- 槽位：ChipsTab 组件 -->
  </nav>
  <!-- 内容滚动区：卡片间距 12px，页面左右边距 16px -->
  <main class="flex-1 overflow-y-auto px-4 pt-2 pb-4 flex flex-col gap-3">
    <!-- 槽位：Card / 内容卡片若干；分组之间用 SubHeader 分隔，组间距 24px（mt-6） -->
  </main>
  <!-- 底部导航：吸底，自带毛玻璃背景 -->
  <footer class="shrink-0">
    <!-- 槽位：BottomTab 组件（3-5 个 Tab） -->
  </footer>
</div>
```


## 3. 一级组件（直接复制骨架，只改文本/图标）

尺寸为参考渲染值（宽×高，px）；多数组件宽度自适应父容器，高度固定。

### Card（根类 `hm-card`，328×328）
HarmonyOS 风格卡片容器，用于承载列表项、内容区块等。自带 5 个预设尺寸和可选装饰性图标按钮。
变体：Playground, Default, 隐藏图标按钮, 含内容

```html
<div class="hm-card hm-card--larger" data-size="Larger"></div>
```

### ListPhone（根类 `<div>（Tailwind 实现）`，328×48）
变体：Playground, Pixso Reference

```html
<div style="width: 328px; background: var(--harmony-comp-background-primary);"><div role="button" tabindex="0" class="list-phone list-phone--lines-1 list-phone--right-menu-select" data-component="ListPhone" data-lines="1" data-left="Text" data-right="Menu select" data-right-kind="menu-select" data-divider="show" data-divider-mode="content" data-size="S" style="--list-left-addon-width: 0px; --list-left-addon-gap: 0px;"><div class="list-phone__main" data-list-phone-region="main"><div class="list-phone__content list-phone__left" data-list-phone-region="content"><span class="list-phone__title" data-list-phone-line="title">Single list</span></div><div class="list-phone__right" data-list-phone-region="right"><span aria-label="Open menu" class="list-phone__action-wrap" data-list-phone-action="true" role="button" tabindex="0"><span class="list-phone__right-text" data-list-phone-right-text="true">Right text</span><span class="list-phone__chevron" aria-label="Open menu" role="img" style="color: var(--harmony-icon-tertiary);"><span aria-hidden="true" class="hm-symbol-icon" style="font-size: 14px; width: 14px; height: 14px;">󰈿</span></span></span></div></div></div></div>
```

### Button（根类 `pixso-button`，120×40）
变体：Playground, Warning Pressed, Loading Selected, Two In One Loading Normal, Two In One Small Emphasized Loading

```html
<button type="button" class="pixso-button pixso-button--medium pixso-button--type-Warning pixso-button--state-Pressed pixso-button--font-medium pixso-button--line-medium" data-size="Medium" data-type="Warning" data-state="Pressed"><span class="pixso-button__content"><span class="pixso-button__label">BUTTON</span></span></button>
```

### Chips（根类 `hm-symbol-icon`，75×28）
变体：Playground, Default, Without Icon, Without Close, Disabled, Multiple

```html
<button type="button" class="chips" data-state="Enabled" data-close="false" data-icon="true"><span class="chips__icon" aria-hidden="true"><span aria-hidden="true" class="hm-symbol-icon chips__icon-svg" style="font-size: 16px; width: 16px; height: 16px;">󰁎</span></span><span class="chips__text">Tabs</span></button>
```

### Select（根类 `hm-select-root`，95×40）
变体：Playground, With Menu, Two In One With Menu, Two In One Full Page Preview

```html
<div class="hm-select-root"><button type="button" class="hm-select-2in1 hm-select-2in1--normal hm-select-2in1--state-enabled" aria-expanded="false" aria-haspopup="listbox" data-size="normal" data-state="Enabled"><span class="hm-select-2in1__label">上海</span><span aria-hidden="true" class="hm-symbol-icon hm-select-2in1__arrow" style="font-size: 24px; width: 24px; height: 24px;">󰈿</span></button></div>
```

### Toggle（根类 `hm-toggle`，72×28）
移动端二元状态切换按钮（如选中/未选中、开/关），支持完整的交互状态反馈
变体：Playground, Custom Content

```html
<button class="hm-toggle hm-toggle--enabled hm-toggle--unselected">状态按钮</button>
```

### ToolBar（根类 `hm-toolbar-phone`，360×76）
手机端底部工具栏，含 2 到 5 个均分入口和底部手势条。
变体：Playground

```html
<div class="hm-toolbar-phone hm-toolbar-phone--land-OFF" data-selected-index="1" data-count="2" data-land="OFF"><div class="hm-toolbar-phone__ports"><button class="hm-toolbar-phone__port" type="button"><span class="hm-toolbar-phone__icon"><span aria-hidden="true" class="hm-symbol-icon" style="font-size: 24px; width: 24px; height: 24px; font-variation-settings: &quot;FILL&quot; 0, &quot;wght&quot; 400, &quot;GRAD&quot; 0, &quot;opsz&quot; 24;">󰁎</span></span><span class="hm-toolbar-phone__label">Action</span></button><button class="hm-toolbar-phone__port hm-toolbar-phone__port--activated" type="button"><span class="hm-toolbar-phone__icon"><span aria-hidden="true" class="hm-symbol-icon" style="font-size: 24px; width: 24px; height: 24px;">󰀉</span></span><span class="hm-toolbar-phone__label">Action</span></button></div><div aria-hidden="true" class="hm-toolbar-phone__bottom-bar"><span class="hm-toolbar-phone__bottom-pill"></span></div></div>
```

### Counter（根类 `<div>（Tailwind 实现）`，360×48）
变体：Playground, Default, Selected, Disabled

```html
<div class="counter counter--type-default" data-type="default"><div class="counter-default"><div class="counter-default__label-wrapper"><span class="counter-default__label">Quantity</span><div class="hm-divider hm-divider--horizontal hm-divider--0.5 hm-divider--solid counter-default__label-divider" aria-hidden="true" style="--hm-divider-color: var(--harmony-comp-divider, rgba(0, 0, 0, 0.2));"></div></div><div class="counter-default__stepper"><button type="button" class="counter-icon-btn" aria-label="Decrease"><span aria-hidden="true" class="hm-symbol-icon" style="font-size: 24px; width: 24px; height: 24px;">󰀬</span></button><span class="counter-value-cell counter-default__value"><span class="counter-value-text" role="button" tabindex="0">999</span><input inputmode="numeric" class="counter-value-input" autocomplete="off" type="text" value=""></span><button type="button" class="counter-icon-btn" disabled="" aria-label="Increase"><span aria-hidden="true" class="hm-symbol-icon" style="font-size: 24px; width: 24px; height: 24px;">󰀵</span></button></div></div></div>
```

### Search（根类 `hm-search`，294×40）
变体：Playground, Default, With Value, Disabled

```html
<div class="hm-search hm-search--type-phone" data-search="OFF" data-state="normal" role="searchbox"><span class="hm-search__overlay"></span><span class="hm-search__icon" aria-hidden="true"><span aria-hidden="true" class="hm-symbol-icon" style="font-size: 16px; width: 16px; height: 16px;">󰀩</span></span><input class="hm-search__input" placeholder="搜索" type="text" value=""></div>
```

### BottomTab（根类 `<nav>（Tailwind 实现）`，294×76）
变体：playground, app-navigation-example, pixso-reference-example, controlled-example, indicator-modes

```html
<nav aria-label="Bottom tab navigation" class="relative inline-flex w-[360px] max-w-full flex-col text-[color:var(--harmony-font-primary)]" data-count="2" data-indicator-mode="Light" data-land="OFF" data-layout="port"><div class="relative flex w-full flex-col overflow-hidden bg-[color:var(--harmony-comp-background-material-tabs,var(--harmony-comp-background-gray))] h-[76px]" style="backdrop-filter: var(--harmony-comp-background-material-tabs-blur, blur(80px));"><div class="grid w-full place-items-stretch h-12" style="grid-template-columns: repeat(2, minmax(0px, 1fr));"><div class="flex w-full items-center justify-center h-12"><button aria-label="Tab" class="group relative inline-flex h-full w-full items-center justify-center rounded-[10px] bg-transparent outline-none transition-colors focus-visible:ring-2 focus-visible:ring-[color:var(--harmony-interactive-focus)] focus-visible:ring-offset-1 focus-visible:ring-offset-[color:var(--harmony-comp-background-primary)] disabled:pointer-events-none disabled:opacity-40 flex-col gap-[2px] px-1 py-1" data-active="false" type="button"><span aria-hidden="true" class="inline-flex size-6 shrink-0 items-center justify-center [&amp;_svg]:size-6 [&amp;_svg]:shrink-0 text-[color:var(--harmony-icon-secondary)]"><span aria-hidden="true" class="hm-symbol-icon" style="font-size: 24px; width: 24px; height: 24px;">󰗳</span></span><span class="truncate text-[10px] font-medium leading-[14px] tracking-[0px] [font-family:&quot;HarmonyHeiTi&quot;,&quot;Geist_Variable&quot;,sans-serif] w-full text-center text-[color:var(--harmony-font-secondary)]">Tab</span></button></div><div class="flex w-full items-center justify-center h-12"><button aria-current="page" aria-label="Tab" class="group relative inline-flex h-full w-full items-center justify-center rounded-[10px] bg-transparent outline-none transition-colors focus-visible:ring-2 focus-visible:ring-[color:var(--harmony-interactive-focus)] focus-visible:ring-offset-1 focus-visible:ring-offset-[color:var(--harmony-comp-background-primary)] disabled:pointer-events-none disabled:opacity-40 flex-col gap-[2px] px-1 py-1" data-active="true" type="button"><span aria-hidden="true" class="inline-flex size-6 shrink-0 items-center justify-center [&amp;_svg]:size-6 [&amp;_svg]:shrink-0 text-[color:var(--harmony-icon-emphasize)]"><span aria-hidden="true" class="hm-symbol-icon" style="font-size: 24px; width: 24px; height: 24px;">󰗳</span></span><span class="truncate text-[10px] font-medium leading-[14px] tracking-[0px] [font-family:&quot;HarmonyHeiTi&quot;,&quot;Geist_Variable&quot;,sans-serif] w-full text-center text-[color:var(--harmony-font-emphasize)]">Tab</span></button></div></div><div class="relative h-7 w-full"><span aria-hidden="true" class="absolute left-1/2 top-[17px] block h-[5px] w-28 -translate-x-1/2 rounded-[4px] bg-[rgba(0,0,0,0.2)]"></span></div></div></nav>
```

### ChipsTab（根类 `pixso-chips-tab-list`，276×132）
变体：Playground, Tab Only, Tab With Icon, Activated, With Badge, Phone Playground

```html
<div class="rounded-[32px] bg-white px-10 py-12 shadow-[0_24px_80px_rgba(15,23,42,0.08)]"><div class="pixso-chips-tab-list" role="tablist" aria-label="Chips tabs"><div role="tab" aria-selected="true" tabindex="0" class="pixso-chips-tab pixso-chips-tab--activated" data-state="activated" data-material="默认" data-type="tab" data-num="false" data-icon="false"><span class="pixso-chips-tab__text-group"><span class="pixso-chips-tab__title">首页</span></span></div><div role="tab" aria-selected="false" tabindex="-1" class="pixso-chips-tab pixso-chips-tab--enable" data-state="enable" data-material="默认" data-type="tab" data-num="false" data-icon="false"><span class="pixso-chips-tab__text-group"><span class="pixso-chips-tab__title">探索</span></span></div><div role="tab" aria-selected="false" tabindex="-1" class="pixso-chips-tab pixso-chips-tab--enable" data-state="enable" data-material="默认" data-type="tab" data-num="false" data-icon="false"><span class="pixso-chips-tab__text-group"><span class="pixso-chips-tab__title">我的</span></span></div></div></div>
```

### TitleBar（根类 `<header>（Tailwind 实现）`，294×56）
变体：playground, normal-phone, secondary page-phone, title with icons-phone, drawer-phone

```html
<header class="w-[328px] max-w-full text-[color:var(--harmony-font-primary)] flex min-h-14 items-center gap-2" data-category="drawer-phone" data-通透度="默认" data-subtitle="false"><div class="flex min-w-0 flex-1 items-center gap-2"><button aria-label="Open drawer" class="inline-flex size-10 items-center justify-center rounded-full bg-[color:var(--harmony-comp-background-tertiary)] text-[color:var(--harmony-icon-primary)] outline-none transition-colors hover:bg-[color:var(--harmony-interactive-hover)] focus-visible:ring-2 focus-visible:ring-[color:var(--harmony-interactive-focus)] disabled:pointer-events-none disabled:opacity-40 shrink-0" title="Open drawer" type="button"><span aria-hidden="true" class="inline-flex size-6 items-center justify-center [&amp;_svg]:size-6 [&amp;_svg]:shrink-0"><span aria-hidden="true" class="hm-symbol-icon" style="font-size: 24px; width: 24px; height: 24px;">󰁩</span></span></button><div class="min-w-0 flex-1"><h1 class="truncate font-bold tracking-[0px] text-[color:var(--harmony-font-primary)] text-[26px] leading-[35px]">工作台</h1></div></div><div class="flex items-center gap-2"><button aria-label="Settings" class="inline-flex size-10 shrink-0 items-center justify-center rounded-full bg-[color:var(--harmony-comp-background-tertiary)] text-[color:var(--harmony-icon-primary)] outline-none transition-colors hover:bg-[color:var(--harmony-interactive-hover)] focus-visible:ring-2 focus-visible:ring-[color:var(--harmony-interactive-focus)] disabled:pointer-events-none disabled:opacity-40" title="Settings" type="button"><span aria-hidden="true" class="inline-flex size-6 items-center justify-center [&amp;_svg]:size-6 [&amp;_svg]:shrink-0"><span aria-hidden="true" class="hm-symbol-icon" style="font-size: 24px; width: 24px; height: 24px;">󰀠</span></span></button></div></header>
```

### IconButton（根类 `hm-icon-button`，184×104）
用于呈现 Pixso 公共组件中的图标按钮组预览，支持 1/2/3 个按钮、3 档材质表面和 3 种尺寸（40px / 32px / 28px）
变体：Playground

```html
<div class="inline-flex p-6"><div class="hm-icon-button hm-icon hm-icon-button--material-standard hm-icon-button--size-40" data-icon-count="3" data-transparency="材质-标准" data-size="40" role="group"><span aria-hidden="true" class="hm-icon-button__button hm-icon__button hm-material-style-layer-floating-ultra-thin-effect-2"><span class="hm-material-style-layer hm-material-style-layer-floating-ultra-thin-fill-1"></span><span class="hm-material-style-layer hm-material-style-layer-floating-ultra-thin-fill-2"></span><span class="hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-1"></span><span class="hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-3"></span><span class="hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-4"></span><span class="hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-5"></span><span class="hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-6"></span><span class="hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-7"></span><span class="hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-8"></span><span class="hm-icon-button__content hm-icon__content"><span aria-hidden="true" class="hm-symbol-icon hm-icon-button__glyph hm-icon__glyph" style="font-size: 24px; width: 24px; height: 24px;">󰄴</span></span></span><span aria-hidden="true" class="hm-icon-button__button hm-icon__button hm-material-style-layer-floating-ultra-thin-effect-2"><span class="hm-material-style-layer hm-material-style-layer-floating-ultra-thin-fill-1"></span><span class="hm-material-style-layer hm-material-style-layer-floating-ultra-thin-fill-2"></span><span class="hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-1"></span><span class="hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-3"></span><span class="hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-4"></span><span class="hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-5"></span><span class="hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-6"></span><span class="hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-7"></span><span class="hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-8"></span><span class="hm-icon-button__content hm-icon__content"><span aria-hidden="true" class="hm-symbol-icon hm-icon-button__glyph hm-icon__glyph" style="font-size: 24px; width: 24px; height: 24px;">󰄴</span></span></span><span aria-hidden="true" class="hm-icon-button__button hm-icon__button hm-material-style-layer-floating-ultra-thin-effect-2"><span class="hm-material-style-layer hm-material-style-layer-floating-ultra-thin-fill-1"></span><span class="hm-material-style-layer hm-material-style-layer-floating-ultra-thin-fill-2"></span><span class="hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-1"></span><span class="hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-3"></span><span class="hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-4"></span><span class="hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-5"></span><span class="hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-6"></span><span class="hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-7"></span><span class="hm-material-style-layer hm-material-style-layer-floating-ultra-thin-effect-8"></span><span class="hm-icon-button__content hm-icon__content"><span aria-hidden="true" class="hm-symbol-icon hm-icon-button__glyph hm-icon__glyph" style="font-size: 24px; width: 24px; height: 24px;">󰄴</span></span></span></div></div>
```

### CheckBox（根类 `hm-checkbox`，24×24）
变体：Playground, Default, Selected, Disabled

```html
<button type="button" class="hm-checkbox hm-checkbox--phone hm-checkbox--off hm-checkbox--enabled" role="checkbox" aria-checked="false"><span class="hm-checkbox__box"></span></button>
```

### RadioPhone（根类 `hm-radio-phone`，24×24）
变体：Playground

```html
<button class="hm-radio-phone hm-radio-phone--off hm-radio-phone--enabled" role="radio" aria-checked="false"><span class="hm-radio-phone__outer"></span></button>
```

### RatingPhone（根类 `pixso-rating-phone`，144×28）
变体：Playground, Interactive, Disabled, Read Only, Focus

```html
<div class="pixso-rating-phone" role="img" aria-label="Rating: 5 out of 5"><button type="button" class="pixso-rating-phone__star pixso-rating-phone__star--active" aria-label="1 star" tabindex="-1"><span aria-hidden="true" class="hm-symbol-icon pixso-rating-phone__star-icon" style="font-size: 28px; width: 28px; height: 28px;">󰀉</span></button><button type="button" class="pixso-rating-phone__star pixso-rating-phone__star--active" aria-label="2 stars" tabindex="-1"><span aria-hidden="true" class="hm-symbol-icon pixso-rating-phone__star-icon" style="font-size: 28px; width: 28px; height: 28px;">󰀉</span></button><button type="button" class="pixso-rating-phone__star pixso-rating-phone__star--active" aria-label="3 stars" tabindex="-1"><span aria-hidden="true" class="hm-symbol-icon pixso-rating-phone__star-icon" style="font-size: 28px; width: 28px; height: 28px;">󰀉</span></button><button type="button" class="pixso-rating-phone__star pixso-rating-phone__star--active" aria-label="4 stars" tabindex="-1"><span aria-hidden="true" class="hm-symbol-icon pixso-rating-phone__star-icon" style="font-size: 28px; width: 28px; height: 28px;">󰀉</span></button><button type="button" class="pixso-rating-phone__star pixso-rating-phone__star--active" aria-label="5 stars" tabindex="-1"><span aria-hidden="true" class="hm-symbol-icon pixso-rating-phone__star-icon" style="font-size: 28px; width: 28px; height: 28px;">󰀉</span></button></div>
```

### SegmentedButton（根类 `<div>（Tailwind 实现）`，328×40）
变体：Playground, Interactive White, Interactive Blue

```html
<div class="segmented-button segmented-button--off segmented-button--icon-off segmented-button--count-3" role="tablist" data-multi-selection="OFF" data-icon="off" data-group-count="3"><button type="button" role="tab" aria-selected="true" class="segmented-button__item segmented-button__item--left segmented-button__item--state-activated" data-position="Left" data-state="activated"><span class="segmented-button__label">Tab 1</span></button><button type="button" role="tab" aria-selected="false" class="segmented-button__item segmented-button__item--mid segmented-button__item--state-enable" data-position="Mid" data-state="Enable"><span class="segmented-button__label">Tab 2</span></button><button type="button" role="tab" aria-selected="false" class="segmented-button__item segmented-button__item--right segmented-button__item--state-enable" data-position="Right" data-state="Enable"><span class="segmented-button__label">Tab 3</span></button></div>
```

### Slider（根类 `hm-slider`，360×40）
变体：Playground, Pixso Canvas, Controlled, Custom Content, Disabled, Contained / 328px card

```html
<div class="hm-slider hm-slider--basic hm-slider--track-thick" data-layout="fixed"><div class="hm-slider__rail-shell" style="--slider-track-width: 336px;"><div class="hm-slider__track hm-slider__track--enabled" style="--slider-progress: 42%;"><input aria-label="slider" class="hm-slider__range" max="100" min="0" step="1" type="range" value="42"></div></div></div>
```

### SwitchPhone（根类 `hm-switch-phone`，36×20）
变体：Playground

```html
<button class="hm-switch-phone hm-switch-phone--off hm-switch-phone--enabled" role="switch" aria-checked="false"><span class="hm-switch-phone__thumb"></span></button>
```

### Badge（根类 `<span>（Tailwind 实现）`，16×16）
变体：Playground, Default, With Value, Disabled

```html
<span class="harmony-badge harmony-badge--Text" aria-label="3"><span class="harmony-badge__text">3</span></span>
```

### Divider（根类 `hm-divider`，294×1）
变体：Playground, Default, Thick, Vertical, Dashed

```html
<div class="hm-divider hm-divider--horizontal hm-divider--0.5 hm-divider--solid"></div>
```

### ProgressBar（根类 `hm-progress-bar`，288×24）
变体：Playground, Default, With Cache

```html
<div class="hm-progress-bar" style="--progress-bar-progress: 43%; --progress-bar-cache: 0%;"><div class="hm-progress-bar__track"><div class="hm-progress-bar__fill"></div></div></div>
```

### SubHeader（根类 `<div>（Tailwind 实现）`，358×120）
变体：Playground, States, Spinner Left (dropdown)

```html
<div style="background: var(--harmony-storybook-preview-bg, var(--harmony-background-secondary)); padding: 24px;"><div class="subheader subheader--left-2line subheader--right-text subheader--state-Enabled subheader--right-on" data-left-type="2line" data-right-type="text" data-right="true" data-state="Enabled"><div class="subheader__left"><span class="subheader__title">Content subheading</span><span class="subheader__subtitle">subheading</span></div><div class="subheader__right"><button type="button" class="subheader__action subheader__action--emphasize">Action</button></div></div></div>
```

### Toast（根类 `hm-toast`，88×36）
操作成功/失败提示、系统状态通知、短暂信息展示。
变体：Playground, Default

```html
<div class="hm-toast inline-flex items-center justify-center gap-2.5 min-h-9 rounded-[18px] px-4 py-2 backdrop-blur-[40px] shadow-[0_10px_60px_rgba(0,0,0,0.2)] text-[14px] font-normal leading-[19px] tracking-normal text-[var(--harmony-font-primary)] whitespace-nowrap select-none" role="status" aria-live="polite" style="background-color: var(--COMPONENT_ULTRA_THICK_fill);">操作成功</div>
```


## 4. 二级组件索引

以下组件库中存在但未附骨架。如需使用：整体结构参考一级组件的写法习惯，**根类名必须准确**；没把握时优先用一级组件或原子元素组合替代。

- **DialogPhone** `<div>（Tailwind 实现）`（294×36） 〔变体: Playground, Controlled Modal, Progress Interactive〕
- **Popup** `<div>（Tailwind 实现）`（100×100） 〔变体: Playground, Without Arrow〕
- **ActionBar** `pixso-actionbar`（328×108） 〔变体: Playground, Interactive, Controlled Active〕
- **ScrollBar** `<div>（Tailwind 实现）`（32×80）：滚动区域的滚动条指示器，鸿蒙风格。滑块可独立使用或包裹于 ScrollBar 容器中。 〔变体: Playground, Default〕
- **HMSymbolIcon** `hm-symbol-icon`（24×24） 〔变体: Playground, Escaped String Compatibility〕
- **TextInput** `hm-textinput`（250×135） 〔变体: Playground, Default, With Value, Error, Disabled, Playground, Default, Error, Playground, Normal, Hover, Focus, Typing, Actived, Error, Disabled, Count〕
- **LoadingProgressBar** `hm-loading-progress-bar`（358×160） 〔变体: Playground, Default〕
- **SwiperDot** `<div>（Tailwind 实现）`（68×30） 〔变体: Playground, Controlled With Page, On Type Controlled〕
- **Aibottombar** `hm-aibottombar`（294×28） 〔变体: Playground〕
- **Size** `hm-foldable`（740×834） 〔变体: Playground, Foldable Default, Phone Portrait, Phone Landscape, Tablet Portrait, Tablet Landscape〕
- **StatusBar** `hm-status-bar`（294×36）
- **CheckboxGroup** `hm-checkbox`（294×48）：多选列表；带超链接操作的复选框组（如协议确认、通知设置） 〔变体: Playground, Default, Selected, Disabled〕
- **SliderSeekbar** `hm-slider`（360×24） 〔变体: Playground, Pixso Canvas, Controlled, Values〕
- **AlphabetIndexer** `<div>（Tailwind 实现）`（24×224） 〔变体: Playground, Port, Land, Interactive〕
- **AlphabetIndexerLable** `hm-alphabet-indexer-lable`（56×56） 〔变体: Playground, Default, Cn, Interactive Cn〕
- **DataPanelLinearGradient** `hm-dp-linear-gradient`（288×288）：存储空间使用率、数据加载进度等需要多彩渐变环形进度指示的场景 〔变体: Playground, Default〕
- **DataPanelLoading** `hm-datapanel-loading`（288×288）：数据面板、下载进度、系统更新进度等环形进度展示 〔变体: Playground, Default, Small, Medium, Completed〕
- **DataPanelProgressCircle** `hm-dp-progress-circle`（88×88） 〔变体: Playground, Default, With Value, Small〕
- **GaugeRing** `hm-gauge-ring`（288×288） 〔变体: Playground, Default, Selected, WithValue〕
- **GaugeStripGauge** `hm-strip-gauge`（214×26） 〔变体: Playground, Default, WithValue, Selected〕
- **PopupTip** `hm-popup-tip`（358×200） 〔变体: Playground, Default, Text Inline, Multiline Text, Multiline Text Inline, Full Pattern, Full Pattern Inline, Without Close, Without Links〕
- **ProgressBarCapsule** `hm-progress-bar-capsule`（72×28）：胶囊型进度指示器，用于显示百分比进度（如文件上传、任务完成度、音量/亮度调节反馈等） 〔变体: Playground, Default, With Value, Disabled〕
- **ProgressBarEclipse** `<div>（Tailwind 实现）`（48×48） 〔变体: Playground, With icon=OFF, With icon=ON〕
- **ProgressBarLoading** `hm-progress-bar-loading`（40×40）：页面/区块加载中状态，环形 indeterminate spinner，适用于按钮、卡片、列表项等需要表明"正在加载"的场景 〔变体: Playground, Default〕
- **Snackbar** `<div>（Tailwind 实现）`（328×48） 〔变体: Playground, Text Button States (x4), Default, With Subtitle〕
- **TextClock** `hm-text-clock`（360×137） 〔变体: Playground, Default, Center With Simplify Date, Center〕
- 另有 21 个 Floating* 悬浮组件（浮层/弹窗/气泡）与 StatusBar：一次生成的静态页面不要使用。

## 5. HMSymbol 图标（用 `<span class="hm-symbol-icon" style="font-size:24px;width:24px;height:24px">实体</span>` 插入）

| 名称 | 含义 | HTML 实体 |
|---|---|---|
| `house_fill` | 首页-选中 | `&#xF0026;` |
| `magnifyingglass` | 搜索 | `&#xF0029;` |
| `person` | 账号 | `&#xF05E5;` |
| `gearshape` | 设置 | `&#xF0020;` |
| `heart` | 取消收藏 | `&#xF0025;` |
| `heart_fill` | 收藏 | `&#xF0021;` |
| `star_fill` | ic_favourites_filled | `&#xF0009;` |
| `plus` | 增加 | `&#xF0035;` |
| `xmark` | 退出 | `&#xF0056;` |
| `checkmark` | 确认 | `&#xF0013;` |
| `chevron_left` | 返回 | `&#xF00DA;` |
| `chevron_right` | 下一步 | `&#xF00D9;` |
| `chevron_down` | 向下 | `&#xF00DB;` |
| `arrow_left` | 返加 | `&#xF00CA;` |
| `play_fill` | 播放 | `&#xF00B4;` |
| `message` | 短信 | `&#xF008F;` |
| `phone_fill` | 童话 | `&#xF009E;` |
| `camera_fill` | 拍照 | `&#xF0438;` |
| `picture` | 图片 | `&#xF0003;` |
| `share` | 分享  | `&#xF003D;` |
| `trash` | 删除 | `&#xF0001;` |
| `square_and_pencil` | 编辑 | `&#xF0073;` |
| `clock` | 时长 | `&#xF03DD;` |
| `calendar` | 日历 | `&#xF03DA;` |
| `bell_fill` | 播放铃声 | `&#xF01D1;` |
| `lock_fill` | 锁 | `&#xF04C1;` |
| `eye` | 护眼模式 | `&#xF0120;` |
| `mic` | 语音 | `&#xF0006;` |
| `envelope` | 消息 | `&#xF0088;` |
| `doc_text` | 日志 | `&#xF00BC;` |
| `folder` | 存储 | `&#xF00C5;` |

## 6. 库外元素降级法则

组件库没有的元素（如步骤条、时间轴）：用 Divider/Badge/Button/原生标签 + Tailwind 拼装，颜色只用本指南出现过的值（蓝 `#0A59F7`、背景 `#F1F3F5`、白、黑色透明度系列），圆角用 8/12/16px 系列，保持与整页同族。
