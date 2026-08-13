# Layout: services-launch

> Page Type: Services Launch. 云服务业务权限启动页模板，适用于华为视频等应用首次启动时展示隐私协议的场景。原始 Pixso source 为 `权限启动页`，节点 `36:54423`，画布 `360 × 792`。

## hit_rules

命中 `services-launch` 时，页面应同时满足以下特征：

- 用户明确要求权限启动页、隐私协议页、首次启动页、应用授权页或类似场景。
- 页面包含沉浸式深色背景 + 模糊面板 + 遮罩层。
- 页面核心为 App 图标、标题、副标题 Hero 区 + 隐私声明文本 + 同意/取消双按钮。
- 存在品牌色按钮（如视频品牌色 `#FF7500`），且同意/取消按钮样式有明显区分。
- Prompt 中出现 `权限启动`、`隐私协议`、`同意`、`取消`、`华为视频`、`首次启动` 等关键词时，应优先命中本 page type。

## exclusion_rules

- 仅为通用设置页或关于页 → 优先评估 `mobile-list`。
- 需要复杂表单交互（如手机号验证、多步注册）→ 不命中本布局。
- 页面主体不是双按钮决策（同意/取消）→ 优先评估其他 page type。
- 登录/注册/绑定手机号等需要输入框的页面不命中本布局。

## reference_blocks

无独立业务 Block 绑定。Hero、Privacy、Actions 为页面内置组合；StatusBarSlot 和 BottomBarSlot 使用注册组件承载。

## layout_skeleton

```html
<main class="layout-services-launch">
  <section class="launch-bg">
    <div data-layer="mask-fourth"></div>
    <div data-layer="blur-panel"></div>
    <div data-layer="mask-tertiary"></div>
  </section>

  <div class="launch-overlay">
    <header data-slot="statusBarSlot"></header>
  </div>

  <section data-slot="heroSlot"></section>

  <section data-slot="privacySlot"></section>

  <section data-slot="actionsSlot"></section>

  <footer data-slot="bottomBarSlot"></footer>
</main>
```

## layout_runtime

| 能力 | 源码支撑 | 说明 |
| --- | --- | --- |
| 页面实现 | `src/pages/services-launch-page/services-launch-page.tsx` | 360×792 固定移动端页面壳 |
| 背景层 | 内置渲染 | 三层背景：mask_fourth (z=1) + blur_panel (z=2) + mask_tertiary (z=5)，不可替换 |
| Hero slot | `heroSlot?: ReactNode` + `showHero` | 默认渲染 App 图标 + 标题 + 副标题；可替换整段或隐藏 |
| Privacy slot | `privacySlot?: ReactNode` + `showPrivacy` | 默认渲染隐私盾牌图标 + 隐私声明文本 + 链接；可替换 |
| Actions slot | `actionsSlot?: ReactNode` + `showActions` | 默认渲染同意（Emphasized）+ 取消（Normal）双按钮；可替换 |
| 顶部状态栏显隐 | `showStatusBar` | 默认显示深色模式状态栏 |
| 底部栏显隐 | `showBottomBar` | 默认显示深色模式 Aibottombar |

## fixed_blocks

| Block / Component | 位置 | 是否必选 | 说明 |
| --- | --- | --- | --- |
| status-bar | overlay 顶部 | 否 | 默认显示，`Color Mode="Dark"` |
| background-layers | 页面底层 | 是 | mask_fourth + blur_panel + mask_tertiary 三层背景，不可替换 |
| aibottombar | bottomBarSlot | 否 | 默认显示，`Color Mode="Dark"`，360×28 贴底 |

## slots

| Slot | 默认 Block | 可替换 Block 清单 | 是否必选 | 说明 |
| --- | --- | --- | --- | --- |
| HeroSlot | 页面内置 Hero 组合 | app-hero / brand-hero / none | 是 | App 图标 + 标题 + 副标题；不同业务替换图标和文案 |
| PrivacySlot | 页面内置 Privacy 组合 | privacy-shield / privacy-text-only / none | 是 | 隐私盾牌图标 + 声明文本 + 链接；不同业务替换文案 |
| ActionsSlot | 页面内置 Button 组合 | button-group / none | 是 | 同意 + 取消双按钮；不同业务替换按钮文案和品牌色 |
| BottomBarSlot | aibottombar | aibottombar / none | 否 | 底部 home indicator bar |

## visibility_rules

| 区域 | 默认 | 显隐 prop | 何时隐藏 |
| --- | --- | --- | --- |
| StatusBar | 显示 | `showStatusBar` | 外部壳层已提供系统状态栏时隐藏 |
| HeroSlot | 显示 | `showHero` | 不需要 App 品牌展示区时隐藏 |
| PrivacySlot | 显示 | `showPrivacy` | 隐私声明在其他区域展示时隐藏 |
| ActionsSlot | 显示 | `showActions` | 按钮由外部控制时隐藏 |
| BottomBar | 显示 | `showBottomBar` | 页面嵌入已有 shell 时隐藏 |

## needed_components

- `status-bar`
- `button`（Emphasized + Normal 变体）
- `aibottombar`
- `hmsymbol-icon` 或内联 SVG（隐私盾牌图标）

## composition_mapping

| 页面区域 | 优先使用 | 可替换为 | 说明 |
| --- | --- | --- | --- |
| StatusBarSlot | `StatusBar Color Mode="Dark"` | none | 复用现有组件，props 硬对齐 DSL |
| HeroSlot | 页面级 App 图标（72×72 PNG）+ 标题 + 副标题 | 同类品牌展示区 | 图标 `border-radius: 16px`；标题 30px/500，副标题 14px/400 |
| PrivacySlot | 隐私盾牌内联 SVG + 声明文本 + 链接 | 同类隐私声明区 | 隐私文本 10px/400；链接使用品牌色 `#FF7500` |
| ActionsSlot | `Button 尺寸="Medium" 类型="Emphasized"` + `Button 尺寸="Medium" 类型="Normal"` | 同类双按钮组 | 同意按钮 158×40，品牌色填充；取消按钮 158×40，品牌色文字描边；gap 16px，居中 |
| BottomBarSlot | `Aibottombar Color Mode="Dark"` | none | 复用现有组件 |

## spatial_tokens

- 画布：`360 × 792`。
- 背景层：全画布覆盖，mask_fourth (z=1) → blur_panel (z=2) → mask_tertiary (z=5)。
- 遮罩层 mask_fourth：360×792，`Dark/mask_fourth` = rgba(0,0,0,0.4)，absolute 全屏。
- 遮罩层 mask_tertiary：360×792，`Dark/mask_tertiary` = rgba(0,0,0,0.2)，absolute 全屏。
- 模糊面板 blur_panel：360×748，`Dark/Blur/COMPONENT_ULTRA_THICK` = rgba(46,48,51,0.9)，圆角 32px 32px 0 0，`backdrop-filter: blur(9px)`（DSL blur(18.12px) ÷ 2）。
- StatusBar：360×36，顶部。
- HeroSlot：312×161，绝对定位；App 图标 72×72，`border-radius: 16px`；标题 `Font/Title_L/Medium` = 30px/500，行高 36px，`Dark/font_on_primary`；副标题 `Font/Body_M/Regular` = 14px/400，`Dark/font_secondary`。
- PrivacySlot：隐私盾牌图标 76×76（内联 SVG），隐私文本 `Font/Caption_M/Regular` = 10px/400，`Dark/font_tertiary`；隐私链接品牌色 `#FF7500`。
- ActionsSlot：flex row，gap 16px，居中；按钮 158×40。
- BottomBarSlot：360×28 贴底。

## shell_rules

- 页面固定为 360px 宽移动端壳层，居中于预览容器。
- 根背景为深色 `#18181A`（`沉浸式背景-星空灰`），对齐 Pixso Frame fill。
- 背景三层（遮罩 + 模糊面板 + 遮罩）使用 absolute 定位叠加，不可替换。
- 内容区使用 absolute 定位叠在背景之上，与 DSL Bounding Box 一致，不使用 `flex-1` 近似替代。
- slot 为 `none` 或 `show* = false` 时不保留空白容器。

## stacking_context

| Layer | z-index | Positioning | Notes |
| --- | --- | --- | --- |
| mask_fourth | 1 | absolute full | rgba(0,0,0,0.4) 遮罩 |
| blur_panel | 2 | absolute bottom | 360×748，圆角顶部，backdrop-filter blur |
| mask_tertiary | 5 | absolute full | rgba(0,0,0,0.2) 遮罩 |
| statusBarSlot | 10 | absolute top | 深色模式状态栏 |
| heroSlot | 10 | absolute | App 图标 + 标题 + 副标题 |
| privacySlot | 10 | absolute | 隐私盾牌 + 声明文本 |
| actionsSlot | 10 | absolute | 同意 + 取消按钮组 |
| bottomBarSlot | 10 | absolute bottom | Aibottombar |

## adaptive_behavior

- 当前 page type 只覆盖 4C 竖屏手机页面；宽度保持 360px。
- 背景层固定全屏，不随内容滚动。
- 内容元素使用 absolute 定位，确保 1:1 还原 Pixso 设计稿。
- Hero/Privacy/Actions 替换 block 必须能在 360px 宽容器内稳定渲染。

## semantic_tokens

| Semantic Part | Token / Value |
| --- | --- |
| Page canvas | `沉浸式背景-星空灰` `#18181A` |
| mask_fourth | `Dark/mask_fourth` `rgba(0,0,0,0.4)` |
| blur_panel | `Dark/Blur/COMPONENT_ULTRA_THICK` `rgba(46,48,51,0.9)` |
| mask_tertiary | `Dark/mask_tertiary` `rgba(0,0,0,0.2)` |
| Hero title | `Dark/font_on_primary` `rgba(255,255,255,0.9)` |
| Hero subtitle | `Dark/font_secondary` `rgba(255,255,255,0.6)` |
| Privacy text | `Dark/font_tertiary` `rgba(255,255,255,0.4)` |
| Privacy link | `视频品牌色-填充` `#FF7500` |
| Agree button bg | 视频品牌色 `#FF7500`（CSS override `--button-bg`） |
| Agree button text | `Dark/font_on_primary` `rgba(255,255,255,0.9)` |
| Cancel button text | 视频品牌色 `#FF7500`（CSS override `--button-fg`） |

## generation_constraints

- `services-launch` 默认组合必须保留背景三层（mask_fourth + blur_panel + mask_tertiary），不可替换或省略。
- Hero、Privacy、Actions 都是可替换 slot；生成页面时不得把它们写死成不可替换的内部 DOM。
- App 图标使用 PNG 图片通过 `<img>` 引入，`border-radius: 16px`；隐私图标使用内联 SVG。
- 按钮颜色通过 CSS 变量 `--button-bg` / `--button-fg` 覆盖为品牌色，不修改 Button 组件源码。
- 模糊半径：DSL `blur(18.12px)` 按 Pixso Skill 规范除以 2 → CSS `blur(9px)`。
- 页面元素使用 `absolute` 定位（与 DSL Bounding Box 一致），不使用 `flex-1` 近似替代。
- 若 prompt 要替换其中任一区块，只替换对应 slot，不重写整个页面模板。
- 可隐藏 slot 隐藏后不保留空白容器。

## validation_notes

- `src/pages/services-launch-page/services-launch-page.tsx` 已提供 `heroSlot`、`privacySlot`、`actionsSlot` 和对应 `show*` 显隐能力。
- Storybook: `Pages/services-launch-page`。
- 组件变体树 JSON 路径: `src/pages/services-launch-page/services-launch-page.json`，数据来源 `get_node_dsl` (item-id `36:54423`)。
- Token `--harmony-video-brand-fill` 已新增到 `global.css`（Pixso `视频品牌色-填充` `2:66201`）。
- Token `--harmony-immersive-bg-starry-gray` 已新增到 `global.css`（Pixso `沉浸式背景-星空灰` `2:66226`）。
- Token `--harmony-dark-mask-tertiary` 已新增到 `global.css`（Pixso `Dark/mask_tertiary`）。

## source

- Pixso: `https://pixso.cn/app/design/f3YuUJ1DHBrZxJcUHOJeYg?item-id=36:54423`
- Node: `36:54423`
- Node name: `权限启动页`
- Canvas: `360 × 792`
