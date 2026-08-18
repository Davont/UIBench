# 官方依据与 HTML 映射边界

本文件用于审计和维护，不在普通页面生成时加载。资料核验日期：2026-08-17。

## 导航

- 三层边界
- 官方结论：设计、色彩、字体、图标、间距、圆角、栅格、材质、无障碍
- 当前 Skill 的适用范围

## 三层边界

1. **华为官方方向与参数**：来自当前 HarmonyOS 官方设计与开发文档，原始单位通常为 `vp` / `fp`。
2. **HTML 预览映射**：将官方原则转译为语义 HTML、CSS Token、Web 无障碍和响应式行为；不能冒充 ArkUI 原生实现。
3. **UIBench 契约**：`data-component`、`data-node-id`、class 白名单、390px 预览尺寸和部分 Token 值，是本项目的确定性实现。

不要把 `vp` / `fp` 与 CSS `px` / `rem` 宣称为系统级固定换算。不要把 CSS 阴影、模糊半径、`999px` 胶囊、390×844 视口或项目触控基线称作华为官方数值。

## 可操作的官方结论

### 设计原则

- 以人为本，让文字、图标和交互清晰可感知。
- 使用字号、字重、语义色和间隔建立信息层级，避免用无意义装饰代替结构。
- 在设备之间保持视觉和交互的一致性，同时按屏幕、输入方式和场景做适配。
- 动效用于解释状态、空间关系和反馈；不为装饰制造额外等待。

来源：

- https://developer.huawei.com/consumer/cn/doc/design-guides/design-concepts-0000001795698445
- https://developer.huawei.com/consumer/cn/design/devstart/
- https://developer.huawei.com/consumer/cn/app/planning/

### 色彩与主题

- 使用基础、语义、控件三层 Token；页面只消费语义角色。
- 相同语义 Token 在深浅模式下保持名称稳定，由主题映射不同色值。
- 普通文本与图标按 primary、secondary、tertiary、fourth 分层；品牌色只强调核心信息和操作。
- `onPrimary` 用于强调色容器或图片上的前景，不用于普通画布。

已核验的典型官方语义色：

| 角色 | Light | Dark |
| --- | --- | --- |
| brand | `#0A59F7` | `#317AF7` |
| warning / 危险提醒 | `#E84026` | `#D94838` |
| alert / 注意提醒 | `#ED6F21` | `#DB6B42` |
| confirm / 成功确认 | `#64BB5C` | `#5BA854` |
| primary text/icon | 90% 黑 | 90% 白 |
| secondary text/icon | 60% 黑 | 60% 白 |
| tertiary text/icon | 40% 黑 | 40% 白 |
| fourth text/icon | 20% 黑 | 20% 白 |

官方表格可能使用前置 Alpha 的八位色值；转成 CSS 时要改为 `rgba()` 或 CSS 后置 Alpha，不能原样复制。

来源：https://developer.huawei.com/consumer/cn/doc/design-guides/color-0000001776857164

### 字体

- 默认使用 HarmonyOS Sans，并减少无意义的字号、字重和颜色变化。
- 支持系统字体放大；自定义字体只用于确有必要的品牌或沉浸场景。
- 本 Skill 的 `24 / 16 / 12px` 分别映射官方手机层级中的 Title_M、Body_L、Caption_L；这是 HTML 预览映射。

来源：

- https://developer.huawei.com/consumer/cn/doc/design-guides/font-0000001828772001
- https://developer.huawei.com/consumer/cn/doc/design-guides/typography-0000002622688363

### 图标

- 优先使用 HarmonyOS Symbol，并让图标字重、字号和文本基线协调。
- 官方界面图标默认体量为 24×24vp，主体参考区约 22×22vp；图形强调简洁、几何和柔和转角。
- 应用图标规范与界面 Symbol 不同，不能混用两类参数。

来源：

- https://developer.huawei.com/consumer/cn/doc/design-guides/system-icons-0000001929854962
- https://developer.huawei.com/consumer/cn/design/harmonyos-symbol/HarmonyOS

### 间距、圆角与栅格

- 间距采用 4vp / 8vp 的节奏倍数；更高层级和更独立的内容使用更大间隔。
- 泛手机常见边距为 16vp、卡片间距为 12vp、普通无边界间隔为 8vp。
- 相同类型和层级使用一致圆角；官方常见示例包含 4 / 8 / 16 / 20 / 32vp，不应把一个圆角应用到所有表面。
- 移动优先；小窗口保证任务完整，大窗口再增加列、侧栏或主从结构。
- 官方横向栅格示例为 `<600vp` 4 列、`600–839vp` 8 列、`≥840vp` 12 列。

本 Skill 为保持现有 UIBench Token 兼容，继续使用 20px 卡片圆角和 16px 控件圆角；它们是项目实现，不是对官方 16vp / 20vp 场景映射的逐项复制。

来源：

- https://developer.huawei.com/consumer/cn/doc/design-guides/interval-parameter-0000002562577161
- https://developer.huawei.com/consumer/cn/doc/design-guides/corner-radius-parameter-0000002556468705
- https://developer.huawei.com/consumer/cn/doc/design-guides/design-layout-basics-0000001795579413
- https://developer.huawei.com/consumer/cn/doc/best-practices/bpta-multi-device-screen-layout

### 空间材质与交互

- 沉浸光感用于悬浮组件与内容发生空间重叠的场景，用来强化 Z 轴关系和可读性，不是所有卡片的默认效果。
- HTML 中的半透明背景、`backdrop-filter` 和 CSS 阴影只是预览近似，不能称作系统材质实现。
- 悬浮、按压和焦点反馈应清楚但克制，同类控件保持一致。

来源：

- https://developer.huawei.com/consumer/cn/doc/design-guides/immersivelight-0000002612101053
- https://developer.huawei.com/consumer/cn/doc/design-guides/hmi-cursor-0000001795531205
- https://developer.huawei.com/consumer/cn/doc/design-guides/hmi-focus-0000001748650376

### 无障碍、主题与安全区

- 为按钮、图标、图片和输入控件提供准确可访问名称；暴露选中、展开、禁用等状态。
- 让 DOM、视觉和键盘焦点顺序一致；弹窗打开与关闭时正确转移和恢复焦点。
- 深浅模式使用两套语义资源，不能对整页简单反色。
- 背景可以延伸到系统区域，关键内容和交互必须避开状态栏、手势区、挖孔、屏幕圆角和折叠转轴。

本 Skill 的 44px 触控基线是项目的 Web 可用性策略；当前官方页面未确认其为所有 HarmonyOS 控件的统一值。

来源：

- https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/accessibility-approve-experience
- https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/improve-screen-reader-experience
- https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/test-app-accessibility
- https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/ui-dark-light-color-adaptation
- https://developer.huawei.com/consumer/cn/doc/best-practices/bpta-multi-device-window-immersive

## 当前 Skill 的适用范围

默认输出是 390px 手机竖屏 HTML 预览，不声称完成折叠屏、平板、电脑、圆屏、ArkUI 组件行为或系统级沉浸材质适配。用户明确要求多设备时，应扩展运行时与质量矩阵，而不是只把手机页面等比放大。
