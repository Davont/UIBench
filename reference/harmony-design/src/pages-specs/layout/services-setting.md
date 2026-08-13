# Layout: services-setting

> Page Type: Services Setting. 服务类 App 底部弹出设置 Sheet，带全页半透明蒙层与毛玻璃面板。展示数据隐私、隐私政策、服务模式、关于等分组设置项。原始 Pixso source 为 `设置首页_全内容`，节点 `36:49162`，画布 `360 × 792`。

## hit_rules

命中 `services-setting` 时，页面应同时满足以下特征：

- 用户明确要求服务设置页、应用设置页、底部弹出设置面板、Service Setting 或底部 Sheet 设置。
- 页面是移动端底部弹出模态页面（Bottom Sheet Modal），包含全页半透明蒙层 + 底部白色毛玻璃圆角面板。
- 内容为分组列表设置项，常见分组为数据隐私、隐私政策、服务模式、关于等。
- 使用 `List`（`variant="grouped"`）+ `ListPhone` 组件展示设置行，行右侧可带 Arrow / Menu select / 文本 / 红点。
- Prompt 中出现 `数据和隐私`、`业务与隐私的声明`、`第三方 SDK 列表`、`应用服务模式`、`服务管理` 等设置项名称时，应优先命中本 page type。
- 页面包含全页 `rgba(0,0,0,0.2)` 蒙层 + 底部 Sheet 面板结构的，应命中本 page type，而非泛化到 `mobile-settings`。

## exclusion_rules

- 系统级设置、喝水设置等通用系统设置页 → 优先评估 `mobile-settings`。
- 显示与亮度、情景模式、云空间、智慧多窗 → 优先评估 `settings-context-list`。
- 以开关控件为主、底部无 Sheet 蒙层的设置页 → 优先评估 `mobile-settings`。
- 不是底部 Sheet 模态结构（无蒙层、无底部弹出面板、无毛玻璃效果）→ 不命中本布局。
- 表单录入 / 后台管理 / 详情页 / 播放器页不命中本布局。

## reference_blocks

- `floating-sheet-semi-modal` — 半模态容器 block，提供全页蒙层、底部 Sheet、拖拽手柄、标题栏、关闭按钮和滚动内容区。
- `list` — 分组列表容器（`variant="grouped"`），提供 subtitle + body + footnote 三段式结构。
列表行由 `list-phone` 组件承载（行数=1, 尺寸=Medium），支持 Arrow / Menu select / 右侧文本 / 红点标记。

## slots

| Slot              | 默认 Block                                  | 可替换 Block 清单            | 是否必选 | 说明                                                                      |
| ----------------- | ------------------------------------------- | ---------------------------- | -------- | ------------------------------------------------------------------------- |
| StatusBarSlot     | `status-bar`                                | `status-bar` / none          | 否       | Light 模式状态栏，外部壳层已提供时隐藏                                    |
| DataPrivacySlot   | `list`（`variant="grouped"`）+ `list-phone` | `list` + `list-phone` / none | 否       | 数据和隐私分组（subtitle + 可变行数 + footnote），行数和行内容随 App 变化 |
| PrivacyPolicySlot | `list`（`variant="grouped"`）+ `list-phone` | `list` + `list-phone` / none | 否       | 隐私政策分组（可变行数），行标题、红点标记位置随 App 变化                 |
| MoreSlot          | `list`（`variant="grouped"`）+ `list-phone` | `list` + `list-phone` / none | 否       | 更多分组（subtitle + 可变行数），右侧文本、Menu select 位置随 App 变化    |
| AboutSlot         | `list`（`variant="grouped"`）+ `list-phone` | `list` + `list-phone` / none | 否       | 关于分组（可变行数），版本号、红点标记随 App 变化                         |

## layout_skeleton

```html
<main class="services-setting-root">
  <header data-slot="statusBarSlot"></header>

  <FloatingSheetSemiModal title="设置" showClose defaultHeight="{748}">
    <section class="services-setting-page">
      <!-- Group: 数据和隐私（subtitle + 5 行 + footnote） -->
      <section data-group="data-privacy"></section>

      <!-- Group: 隐私政策（6 行，含红点标记） -->
      <section data-group="privacy-policy"></section>

      <!-- Group: 更多（subtitle + 3 行，含 Menu select） -->
      <section data-group="more"></section>

      <!-- Group: 关于（2 行，含红点 + 版本号） -->
      <section data-group="about"></section>
    </section>
  </FloatingSheetSemiModal>
</main>
```

## layout_runtime

| 能力            | 源码支撑                                                         | 说明                                                                                          |
| --------------- | ---------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| 页面实现        | `src/pages/services-setting/services-setting-page.tsx`           | 360×792 固定移动端页面壳                                                                      |
| 半模态容器      | `FloatingSheetSemiModal`（`@/blocks/floating-sheet-semi-modal`） | 统一提供全页蒙层、底部 Sheet、拖拽手柄、标题栏、关闭按钮和滚动内容区，`defaultHeight=748`     |
| 全页蒙层        | `FloatingSheetSemiModal` backdrop                                | `rgba(0,0,0,0.2)` 全页半透明黑色覆盖，`z-index: 1`                                            |
| 底部 Sheet 面板 | `FloatingSheetSemiModal` + `FloatingBindSheet`                       | 底部弹出，32px 顶部圆角，最高档使用纯色 `--harmony-background-secondary`，`max-height: 748px` |
| 拖拽手柄        | `FloatingSheetSemiModal` handle                                  | 48×4px 灰色胶囊条，圆角 2px，使用 block 内置拖拽能力                                          |
| 标题栏          | `FloatingSheetSemiModal` title/header                            | 56px 高，左侧标题「设置」（20px/700），右侧 × 关闭按钮（40×40px 圆形）                        |
| 内容滚动区      | `FloatingSheetSemiModal` body                                    | 弹性撑满，纵向滚动，隐藏滚动条                                                                |
| 状态栏          | `StatusBar`（`Color Mode="Light"`）                              | 位于蒙层之上，`z-index: 10`                                                                   |
| 分组列表        | `List variant="grouped"` + `ListPhone`                           | 白色圆角卡片（20px），行高 48px/56px，内置分隔线                                              |
| Section 标题    | `.services-setting-section-title`                                | 14px/400/19px，`--harmony-font-secondary` 色                                                  |
| 红点标记        | `.services-setting-page__red-dot`                                | 6×6px 圆形，`--harmony-warning` 色，与标题文字 `inline-flex` + `gap: 6px` 排列                |
| Footnote        | `.grouped-list-section__footnote`                                | 12px/400/18px，`--harmony-font-secondary` 色                                                  |

## fixed_blocks

| Block / Component         | 位置            | 是否必选 | 说明                                                  |
| ------------------------- | --------------- | -------- | ----------------------------------------------------- |
| status-bar                | overlay 顶部    | 是       | Light 模式，`z-index: 10`，蒙层之上可见               |
| floating-sheet-semi-modal | overlay + Sheet | 是       | 统一承载蒙层、Sheet、手柄、标题、关闭按钮和滚动内容区 |

## content_groups

| Group          | 内容                                    | 行数 | 特殊项                                                         |
| -------------- | --------------------------------------- | ---- | -------------------------------------------------------------- |
| data-privacy   | 数据和隐私（subtitle）+ 5 行 + footnote | 5    | subtitle 14px/400，footnote「了解我们如何使用您的数据」        |
| privacy-policy | 隐私政策相关 6 行                       | 6    | 「业务与隐私的声明」行带红点标记                               |
| more           | 更多（subtitle）+ 3 行                  | 3    | 「应用服务模式」右文本「全量模式」，「服务管理」右 Menu select |
| about          | 关于 + 服务协议                         | 2    | 「关于」带红点标记 + 右文本「版本 1.0.0」                      |

## visibility_rules

| 区域          | 默认 | 说明                                       |
| ------------- | ---- | ------------------------------------------ |
| StatusBar     | 显示 | Light 模式，蒙层之上；外部壳层已提供时隐藏 |
| Overlay       | 显示 | 全页半透明蒙层，底部 Sheet 模态的必要元素  |
| Sheet Handle  | 显示 | 拖拽手柄视觉，当前为静态元素               |
| Sheet Header  | 显示 | 标题「设置」+ 关闭按钮                     |
| Sheet Content | 显示 | 内容滚动区，承载全部分组列表               |

## needed_components

- `status-bar`
- `list-phone`
- 关闭按钮使用 `FloatingSheetSemiModal` 内置 CloseGlyph，无需引入额外图标组件

## composition_mapping

| 页面区域                                  | 优先使用                                                             | 可替换为 | 说明                                                                                |
| ----------------------------------------- | -------------------------------------------------------------------- | -------- | ----------------------------------------------------------------------------------- |
| StatusBarSlot                             | `StatusBar` `Color Mode="Light"`                                     | none     | 位于蒙层之上，不得省略                                                              |
| SemiModal                                 | `FloatingSheetSemiModal title="设置" showClose defaultHeight={748}`  | none     | 统一提供 overlay、Sheet Handle、Sheet Header、Sheet Content；页面不得手写半模态壳层 |
| 多行卡片（数据和隐私/隐私政策/更多/关于） | `List variant="grouped"` + `ListPhone`（带 `divider`）               | none     | 48px 行高（Medium 尺寸），最后一行 `divider={false}`                                |
| Section Subtitle                          | `.services-setting-section-title` 或 `.grouped-list-section__header` | none     | 14px/400/19px，`--harmony-font-secondary`；独立 section title 有 `margin-top: 16px` |
| Footnote                                  | `.grouped-list-section__footnote`                                    | none     | 12px/400/18px，「数据和隐私」下 footnote 使用 14px/400/19px                         |
| 红点标记                                  | `.services-setting-page__red-dot`                                    | none     | 6×6px 圆形，`--harmony-warning`，`inline-flex` + `gap: 6px` 嵌入 title              |
| 右侧 Arrow                                | `ListPhone right="Arrow"`                                            | none     | 默认右箭头图标                                                                      |
| 右侧文本                                  | `ListPhone right="Arrow" rightText="全量模式"`                       | none     | Arrow + 文本并排                                                                    |
| 右侧 Menu select                          | `ListPhone right="Menu select"`                                      | none     | 下拉菜单箭头                                                                        |

## spatial_tokens

- 画布：`360 × 792`，圆角 `24px`，背景 `#F1F3F5`（`--harmony-background-secondary`）。
- StatusBar：高度 `36px`（由 StatusBar 组件决定），`z-index: 10`，位于画布顶部。
- Overlay：`inset: 0` 铺满画布，`z-index: 1`。
- Sheet 面板：`max-height: 748px`（792 − 44），顶部圆角 `32px 32px 0 0`，底部贴边，`z-index: 2`。
- Sheet 背景：`rgba(255,255,255,0.8)` + `backdrop-filter: blur(27.18px)`。
- 拖拽手柄：`48 × 4px`，圆角 `2px`，容器高度 `16px`（含 `padding-top: 8px`）。
- 标题栏：高度 `56px`，左右 padding `16px`，标题 `20px / 700 / 27px`。
- 关闭按钮：`40 × 40px`，圆形，背景 `--harmony-comp-background-tertiary`。
- 内容区：`gap: 12px`，padding `8px 0 16px`；左右 16px 由 `FloatingSheetSemiModal` / `FloatingBindSheet` 壳层提供。
- 卡片圆角：`20px`（`grouped-list-section__body`）。
- 卡片内列表上下 padding：`4px 0`（`.grouped-list-section__body` override）。
- 多行卡片行高：`48px`（Medium 尺寸 ListPhone）。
- Section header：`14px / 400 / 19px`，颜色 `--harmony-font-secondary`，padding `0 12px`。
- Section subtitle：独立 `margin-top: 16px`，`margin-bottom: -4px`。
- Footnote：`12px / 400 / 18px`（默认），`14px / 400 / 19px`（数据和隐私下），颜色 `--harmony-font-secondary`。
- 红点：`6 × 6px`，圆形，颜色 `--harmony-warning`（`rgba(232, 64, 38, 1)`），与标题文字 `gap: 6px`。

## shell_rules

- 页面固定为 360px 宽移动端壳层，居中于预览容器。
- 根背景为 `#F1F3F5`（`--harmony-background-secondary`），圆角 24px。
- 全页蒙层铺满画布，`z-index: 1`，颜色固定 `rgba(0,0,0,0.2)`。
- Sheet 面板底部贴边，顶部 32px 圆角，最大高度 748px；内容超出时纵向滚动。
- 状态栏位于蒙层之上（`z-index: 10`），确保时间/电量等系统信息可见。
- 本页面为静态展示页；半模态拖拽与关闭按钮能力由 `FloatingSheetSemiModal` 提供。
- 禁止使用 `MobilePhoneShellTemplatePage` 作为壳层——本页面为底部 Sheet 模态，不是整页壳层。

## stacking_context

| Layer         | z-index | Positioning      | Notes                              |
| ------------- | ------- | ---------------- | ---------------------------------- |
| statusBarSlot | 10      | absolute top     | Light 模式 StatusBar，蒙层之上可见 |
| sheet         | 2       | absolute bottom  | 底部弹出 Sheet 面板，毛玻璃背景    |
| overlay       | 1       | absolute inset 0 | 全页半透明黑色蒙层                 |
| root bg       | auto    | relative         | `#F1F3F5` 画布背景                 |

## adaptive_behavior

- 当前 page type 只覆盖 4C 竖屏手机页面；宽度保持 360px。
- Sheet 内容区允许纵向滚动；蒙层和 Sheet 面板不随内容重排。
- Sheet 最大高度 748px（792 − 44 StatusBar），内容超出时内部滚动。
- 分组卡片宽度与内容区间距固定，不响应式变化。

## semantic_tokens

| Semantic Part             | Token / Value                                              |
| ------------------------- | ---------------------------------------------------------- |
| Page canvas bg            | `#F1F3F5` / `--harmony-background-secondary`               |
| Overlay bg                | `rgba(0,0,0,0.2)`                                          |
| Sheet bg                  | `rgba(255,255,255,0.8)` + `backdrop-filter: blur(27.18px)` |
| Sheet handle              | `--harmony-icon-fourth` / `rgba(0,0,0,0.2)`                |
| Sheet title               | `--harmony-font-primary` / `rgba(0,0,0,0.9)`、20px / 700   |
| Close button bg           | `--harmony-comp-background-tertiary` / `rgba(0,0,0,0.047)` |
| Close button icon         | `--harmony-icon-primary` / `rgba(0,0,0,0.9)`               |
| Card bg                   | `--harmony-comp-background-primary` / `#FFFFFF`            |
| Card radius               | 20px                                                       |
| Section header / subtitle | `--harmony-font-secondary` / `rgba(0,0,0,0.6)`             |
| Footnote                  | `--harmony-font-secondary` / `rgba(0,0,0,0.6)`             |
| Red dot                   | `--harmony-warning` / `rgba(232, 64, 38, 1)`               |
| ListPhone active          | `rgba(0,0,0,0.08)`                                         |
| ListPhone hover           | `rgba(0,0,0,0.04)`                                         |

## generation_constraints

- 页面必须以 `.services-setting-root` 为根容器，360×792px，圆角 24px。
- 半模态壳层必须使用 `FloatingSheetSemiModal`，不得手写 `.services-setting-overlay` / `.services-setting-sheet`。
- 最高档 Sheet 背景使用 `FloatingSheetSemiModal` 的 expanded solid 模式；蒙层由 block 内置 backdrop 提供。
- 关闭按钮使用 `FloatingSheetSemiModal` 内置 CloseGlyph，不得手写匿名 SVG 按钮。
- 分组列表必须使用 `List variant="grouped"` + `ListPhone` 组件，不得手写匿名列表容器。
- 红点标记嵌入 title 文本末尾，通过 `inline-flex` + `gap: 6px` 对齐，不得使用绝对定位。
- 页面为无 props 静态展示页，所有内容为静态数据，不接收外部配置。
- 禁止使用 `MobilePhoneShellTemplatePage` 作为壳层——本页面是底部 Sheet 模态，自包含蒙层 + Sheet 布局。
- 不要把本页面错误命中到 `mobile-settings`：本页面的核心是底部 Sheet 蒙层 + 毛玻璃面板 + 分组列表，不是整页系统设置。
- 不要将整个 Pixso 页面作为单张图片；必须保留组件装配能力。

## validation_notes

- `src/pages/services-setting/services-setting-page.tsx` 为静态展示页，无 props，不接收外部 slot；半模态壳层复用 `FloatingSheetSemiModal`，页面只维护 service-setting 内容数据和局部间距覆盖。
- 变体树 JSON: `src/pages/services-setting/services-setting.json`，包含 `Color Mode=Light`、`行数=1`、`尺寸=Medium`、`属性 1=默认`、`Land=OFF` 五个变体属性。
- 与 `mobile-settings`（`settings-page-template`）的区别：本页面是 Service App 专属底部 Sheet 模态，带蒙层 + 毛玻璃面板；`mobile-settings` 是整页系统设置，无蒙层和毛玻璃效果。
- 本 page type 当前未注册在 `route-index.md` 中，需手动添加后方可被路由系统命中。

## source

- Pixso: `https://pixso.cn/app/design/f3YuUJ1DHBrZxJcUHOJeYg?item-id=36:49162`
- Node: `36:49162`
- Node name: `设置首页_全内容`
- Canvas: `360 × 792`
