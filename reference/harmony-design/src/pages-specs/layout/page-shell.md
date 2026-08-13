# Layout: page-shell

> 通用移动端手机壳层页：仅定义 360px 手机画布、顶部标题栏、内容滚动区与底部系统指示区，不附带具体业务内容布局。
> Source template: `src/pages/mobile-phone-shell-template/`

## hit_rules

命中 `page-shell` 时，通常满足以下任一场景：

- `src/route-index.md` 中其他 active `page_type` 均未命中，进入 fallback。
- 页面是二级页、详情页、轻量功能页、空白承载页或临时原型页，业务内容无法归入 `mobile-card` / `mobile-grid` / `mobile-list` / `mobile-settings` / `services-home` 等具体布局。
- 页面只需要通用手机壳层：顶部标题 / 返回 / 右侧操作、可滚动内容区、底部 home indicator。
- 业务内容可以作为 children 填入壳层，不需要模板预设的卡片、列表、宫格或首页结构。

## exclusion_rules

出现以下任一特征时，不应停留在 `page-shell`：

- 请求明确命中已注册业务 layout，例如设置页、入口列表页、宫格首页、内容卡片首页、服务首页。
- 页面主体内容已经有稳定模板可直接表达，例如 `mobile-list-template`、`settings-page-template`、`mobile-card-template`。
- 页面需要多 tab 应用主页结构，应优先评估具体主页模板；`page-shell` 只作为其底层壳层，不作为最终 page_type。
- 为规避具体 layout 约束而主动选择 `page-shell`。

## reference_blocks

- `mobile-phone-shell-template` — 通用手机壳层模板。`page-shell` 只提供 shell，不提供业务内容块。
- `list` — 业务 children 出现设置项、入口行、下拉菜单或分组列表时的推荐列表 block；命中 `page-shell` 仍需先使用壳层模板，再在 children 中按需组合 `List`。

## layout_skeleton

命中 `page-shell` 后，页面根壳层必须使用实体模板：

```tsx
import { MobilePhoneShellTemplatePage } from "@/pages/mobile-phone-shell-template"

<MobilePhoneShellTemplatePage
  mode="secondary"
  headerVariant="secondary"
  title="页面标题"
  leadingAction={{ kind: "back", label: "Back", onClick: handleBack }}
  headerActions={headerActions}
  showFloatingTab={false}
>
  <section className="page-business-content">
    {/* 业务内容只能作为 children 填入 */}
  </section>
</MobilePhoneShellTemplatePage>
```

不得只拆用 `FloatingTitleBar`、`Aibottombar` 或手写 `.xxx-canvas` / `.xxx-body` 后声称命中 `page-shell`。

## needed_components

- `floating-title-bar` — 由 `MobilePhoneShellTemplatePage` 内部承载，不在页面中重复手写壳层。
- `aibottombar` — 由 `MobilePhoneShellTemplatePage` 内部承载，不在页面中重复手写底部指示条。
- `floating-tab` — 仅在 `mode="app-home"` 或显式 `showFloatingTab={true}` 时由模板内部承载。
- `hmsymbol-icon` — 可用于业务内容图标或 `headerActions`。
- `list-phone` — 当 children 中包含列表行、设置行、入口行或下拉行时，作为 `List` block 的行级布局资源。

## local_component_mapping

- 页面根壳层：使用 `@/pages/mobile-phone-shell-template` 导出的 `MobilePhoneShellTemplatePage`。
- 二级页 / 详情页：推荐 `mode="secondary"`、`headerVariant="secondary"`、`showFloatingTab={false}`。
- 普通页面：可使用 `mode="app-home"`、`headerVariant="normal"`，并由模板提供底部 self-contained `FloatingTab`。`FloatingTab` 与独立 `Aibottombar` 必须二选一，不得同时渲染。
- 沉浸式页面：可使用 `mode="immersive"` 或 `showTitleBar={false}`，但仍必须保留 `MobilePhoneShellTemplatePage` 作为根壳层。
- 业务内容：放入 children，并通过页面级 CSS 控制业务内容区内部结构；不得重写模板的 root/body/bottom 几何。
- 列表型业务内容：优先使用 `@/blocks/list` 的 `List`（`variant="card"` / `"dropdown"` / `"grouped"`）承载分组列表或入口行；行级内容复用 `ListPhone`，不要在 shell children 内手写匿名列表行。

## composition_mapping

| Layout Block | Component Reference | Variant / Composition | Layout Responsibility | Component Responsibility |
| --- | --- | --- | --- | --- |
| `page-shell-root` | `MobilePhoneShellTemplatePage` | `mode` + `headerVariant` | 360×792 画布、背景、overflow、壳层变量 | 根壳层渲染 |
| `titlebar` | `FloatingTitleBar` | 由 `headerVariant` 映射 | 顶部高度、绝对定位、z-index、pointer-events | 状态栏、标题、返回、actions |
| `body` | `mobile-phone-shell-template__body` | children slot | 内容滚动、顶部/底部 padding、滚动条隐藏 | 承载业务 children |
| `bottom` | `Aibottombar` / `FloatingTab` | 由 `mode` / `showFloatingTab` 决定，互斥渲染 | 底部 shell 高度、渐隐背景、贴底定位 | 独立 home indicator 或 self-contained tab pill |
| `page-primary-action-area` | `bottomPrimaryAction` | 页面级固定主操作插槽 | 主操作按钮的底部安全区、间距、滚动预留 | 触发提交、保存、继续、确认等主动作 |
| `business-content` | 页面级自定义 | children | 业务区域布局 | 业务内容渲染 |
| `business-list-content` | `List` + `ListPhone` | `variant="card"` / `"dropdown"` / `"grouped"` | children 内列表区域宽度、间距、滚动内容流 | 分组列表、设置行、入口行、下拉行渲染 |

## spatial_tokens

- 画布宽度：`360px`，由 `--mobile-phone-shell-width` 控制。
- 画布高度：`792px`。
- 页面内容宽度：默认 `calc(360px - 2 * var(--harmony-page-margin, 16px))`，即 328px。
- normal / secondary / drawer titlebar 布局高度：`92px`。
- big titlebar 布局高度：`173px`。
- normal / secondary / drawer titlebar 渐变遮罩高度：`124px`，不参与 body 顶部占位。
- big titlebar 渐变遮罩高度：`205px`，不参与 body 顶部占位。
- app-home bottom 高度：`100px`，由 self-contained `FloatingTab` 承担 tab pill 与底部手势指示条。
- immersive bottom 高度：`28px`。
- Aibottombar 高度：`28px`。
- Page primary action 与 Aibottombar **组件容器**间距：`16px`。
- 启用 Page primary action 时，底部组合区高度为 `40px + 16px + 28px = 84px`；两个组件必须在同一个壳层底部容器中按垂直顺序渲染。
- 内容末尾与主操作按钮顶部间距：`16px`；因此启用 Page primary action 时，body 的底部 scroll inset 为 `84px + 16px = 100px`。
- children 业务内容区不应再重复声明整页级 `360 × 792` 画布。

## page_primary_action_area

`Page Primary Action Area` 是页面级主操作区，属于壳层几何规则，不属于 `Button` 组件自身规则。出现提交、保存、继续、下一步、确认、购买、审批、创建、完成等页面级主动作时，主操作按钮必须放入该区域。

- 使用 `MobilePhoneShellTemplatePage` 的 `bottomPrimaryAction` 插槽传入页面级主操作。模板会自动显示 Aibottombar，并在同一个底部组合容器内按“主操作 → `16px` 间距 → Aibottombar”顺序渲染；body 的底部滚动预留同步扩展。
- `bottomPrimaryAction` 只在 `showFloatingTab={false}` 时生效；传入首页 FloatingTab 场景会被忽略，避免覆盖 tab pill 与其内置手势条。
- 短页面 / 单屏页面：主操作区固定在页面底部组合容器内，与 Aibottombar 组件容器保留 `16px`；底部组合容器贴齐页面底部。
- 长页面 / 超长表单：主操作区可以固定在底部，也可以作为内容流末尾的最后一个操作区；若放在内容末尾，滚动到底部时仍必须与 Aibottombar 保持 `16px` 间距。
- 主操作区横向遵循页面内容宽度：默认 `left/right = var(--harmony-page-margin, 16px)`，宽度为 `var(--harmony-page-content-width)`。
- 滚动内容必须为主操作区预留底部空间：至少包含主按钮高度、按钮与 Aibottombar 的 `16px` 组件间距、Aibottombar `28px` 高度，以及内容末尾与按钮的 `16px` 间距（共 `100px`）；不得让按钮被底部 shell 遮挡。
- 多 tab 首页使用 `FloatingTab` 时不得再叠加独立 `Aibottombar`；主操作区不得覆盖 tab pill 或其内置底部手势指示条。如确需页面级主操作，应重新评估是否应使用二级页 / 任务页，而不是 app-home 底部导航页。
- `Button` 只负责视觉、尺寸、状态和交互；页面底部位置、滚动预留和安全区由 `page-shell` 负责。

## shell_rules

- `page-shell` 是实体模板契约，不是视觉参考概念。
- 命中 `page-shell` 时，最终页面 JSX 必须出现 `<MobilePhoneShellTemplatePage>` 作为手机壳层。
- 顶部 titlebar、滚动 body、底部 home indicator / tab bar 由模板负责。
- 页面级 CSS 只允许约束 children 内部业务内容，不得复制 `.mobile-phone-shell-template` 的 root/body/bottom 责任。
- 页面级主操作按钮必须遵循 `Page Primary Action Area`，不得临时手写 `bottom: 0` 或 `padding-bottom: 88px / 140px` 等魔法值来绕过 Aibottombar。
- 如确有极端场景无法使用实体模板，必须在生成日志中将 page_type 改为自定义 fallback，而不是继续声称 `page-shell`。

## stacking_context

| Layer | z-index | Positioning | Notes |
| --- | --- | --- | --- |
| `mobile-phone-shell-template__bottom` | 100 | absolute bottom | 底部 home indicator / tab pill |
| `mobile-phone-shell-template__header` | 10 | absolute top | 顶部 titlebar |
| `mobile-phone-shell-template__body` | auto | relative scroll | 业务 children 滚动区 |

业务 children 不得通过高 z-index 覆盖 titlebar / bottom shell，除非是明确的 modal / sheet / popover 反馈组件。

## adaptive_behavior

- 根壳层固定 `height: 792px; overflow: hidden`。
- 内容滚动交给 `mobile-phone-shell-template__body`。
- children 内容超高时自然滚动，不压缩顶部 / 底部 shell。
- headerVariant 变化时，由模板 CSS 自动调整 body padding-top。
- mode 变化时，由模板 CSS 自动调整 body padding-bottom。
- **文字优先级**：P0（权限名称、状态、数量、风险提示）默认完整展示、禁止省略；P1（说明文案）最多两行，内容卡片/行项高度随内容增长；P2（歌名、用户名、列表右侧辅助信息等）只有 Pixso 设计稿或布局规格明确要求紧凑单行时，才可省略。P0/P1 不得使用 `white-space: nowrap`、`text-overflow: ellipsis`、固定高度或裁切来换取布局紧凑。

## semantic_tokens

| Semantic Part | Token |
| --- | --- |
| Page canvas | `--harmony-background-secondary` |
| Content width | `--harmony-page-content-width` |
| Page margin | `--harmony-page-margin` |
| Primary text | `--harmony-font-primary` |
| Secondary text | `--harmony-font-secondary` |
| Component surface | `--harmony-comp-background-primary` |
| Divider | `--harmony-comp-divider` |

## generation_constraints

- 必须 import 并使用 `MobilePhoneShellTemplatePage`：`import { MobilePhoneShellTemplatePage } from "@/pages/mobile-phone-shell-template"`。
- 禁止只 import `FloatingTitleBar` / `Aibottombar` 来手动拼壳层。
- 禁止自写页面根画布类承担 `width: 360px; height: 792px; overflow: hidden` 等 shell root 责任。
- 禁止自写 body 容器承担顶部 / 底部 shell padding 计算。
- 禁止自写 bottom home indicator；使用模板内部 `Aibottombar`。
- 禁止在 `showFloatingTab={true}` / `mode="app-home"` 时额外渲染 `Aibottombar`；`MobilePhoneShellTemplatePage` 已在 `showFloatingTab` 与 `showAIBottomBar` 之间做互斥。
- 禁止把页面级主操作按钮贴到画布底部或直接压在 Aibottombar / FloatingTab 上。
- 禁止通过 `bottomClassName` 承载业务主按钮；`bottomClassName` 只用于调整模板 bottom shell 的样式，不用于注入页面业务操作。
- 禁止使用未说明来源的底部魔法值，例如 `padding-bottom: 88px`、`padding-bottom: 140px`、`bottom: 0`。
- **禁止给业务内容顶层 wrapper 加 `padding`**。壳层 `mobile-phone-shell-template__body` 已承担 top/bottom padding（header 高度 + Aibottombar 高度），且不提供水平 padding。页面边距应由**各内容块自行**用 `width: var(--harmony-page-content-width); margin-inline: auto` 管理，不得在包裹所有 children 的 `.xxx-page` / `.xxx-root` 容器上统一加 `padding: 0 16px` 或 `padding-bottom: calc(...)`。这会使业务 wrapper 沦为"二级 body"，重复壳层 padding 职责。
  - ❌ 反例：`.my-page { padding: 0 var(--harmony-page-margin); padding-bottom: calc(28px + 16px + 64px); }` — 整页 wrapper 既加了水平 padding 又用魔法值加底部 padding
  - ✅ 正例：`.my-page { display: flex; flex-direction: column; gap: 12px; }` + 各 card `{ width: var(--harmony-page-content-width); margin-inline: auto; }` + 最后一个内容块 `{ margin-bottom: calc(var(--sa-primary-action-gap) + var(--sa-primary-action-btn-h)); }`
- 业务内容只能作为 children 填入；业务区可自定义卡片、时间轴、表单、空状态等内容结构。
- 对每一段可见文本先标记 P0/P1/P2：P0/P1 必须保留完整内容与自适应高度；P2 的单行省略必须在实现或生成日志中注明对应的 Pixso / 布局约束。
- 若页面需要具体业务布局，应回退到对应 layout，而不是滥用 `page-shell`。

## validation_notes

- 检查 TSX 是否使用 `<MobilePhoneShellTemplatePage>` 包裹业务内容。
- 检查业务页面是否避免重复实现 titlebar/body/bottom shell。
- **检查业务内容顶层 wrapper 是否零 `padding`**。不得出现 `.xxx-page { padding: 0 16px; }` 或 `.xxx-page { padding-bottom: calc(...); }`；水平边距应由各内容块 `width + margin-inline: auto` 管理，底部预留应由最后一个内容块的 `margin-bottom` 表达。
- 检查页面级主操作按钮是否位于 `Page Primary Action Area`：固定底部时与 Aibottombar 组件容器 `gap: 16px`；内容末尾时滚动到底部仍保留 `16px` 间距。
- 检查主操作按钮是否避免覆盖 `Aibottombar` / `FloatingTab`，并避免 `88px / 140px` 等未绑定壳层变量的底部魔法值。
- 检查 P0 文本无省略且完整可见；P1 文本最多两行且父卡片/行项可随内容增长；P2 的省略存在明确的 Pixso 或布局依据。
- 检查日志中的 `matched page_type`、`layout file`、`template/source baseline` 与实际 JSX 保持一致。
- `page-shell` 可作为兜底，但兜底不等于放弃模板实体复用。

## source

- Template source: `src/pages/mobile-phone-shell-template/mobile-phone-shell-template.tsx`
- Template style: `src/pages/mobile-phone-shell-template/mobile-phone-shell-template.css`
- Route fallback: `src/route-index.md`
