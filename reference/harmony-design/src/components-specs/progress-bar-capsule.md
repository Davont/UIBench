# ProgressBar-Capsule

## Metadata

| 项目 | 值 |
|------|-----|
| 实现目录 | `src/components/ProgressBarCapsule/` |
| Stories 路径 | `src/components/ProgressBarCapsule/progress-bar-capsule.stories.tsx` |
| Pixso 链接 | https://pixso.cn/app/design/HA_e8I2mE7Oa0b5ZoeokSA?item-id=5318:20101 |
| item-id | `5318:20101` |
| MCP 工具来源 | `get_node_dsl` (成功), `get_screenshot` (不可用 — unsupported), `get_export_image` (降级), `design_to_code` (batch timestamp expired), `get_variants` (返回 `{}`) |
| 变体树 JSON | `src/components/ProgressBarCapsule/progress-bar-capsule.json` |
| 变体树来源 | `get_node_dsl` 直接提取；`get_variants` 返回空对象 `{}`，使用 DSL 的 `pixComponentTreeDslNodes` 中 5 个子组件实例（Enabled/Hover/Pressed/Focus/Disabled）的 `componentNormName` 重建 variantOptions |

## 组成与用途

- **导出项**: `ProgressBarCapsule` (组件), `ProgressBarCapsuleProps` (类型), `ProgressBarCapsuleState` (类型), `progressBarCapsuleStates` (状态常量数组)
- **使用场景**: 胶囊型进度指示器，用于显示百分比进度（如文件上传、任务完成度、音量/亮度调节反馈等）

## 量化规格

### 几何尺寸

| 参数 | 值 | 来源 |
|------|-----|------|
| 组件宽度 | 72px | DSL `width` |
| 组件高度 | 28px | DSL `height` |
| 圆角 | 14px (全圆角胶囊) | DSL `cornerRadius` |
| 内边距 | top: 4px, bottom: 4px, left: 8px, right: 8px | DSL `autoLayout.padding*` |
| 边框 | 1px inside stroke | DSL `strokeWeight`, `strokeAlign: INSIDE` |

### 填充条 (Rectangle 2)

| 参数 | 值 | 来源 |
|------|-----|------|
| 位置 | absolute, left: 0, top: 0 | DSL `autoLayoutItemAbsolutePos: true` |
| 高度 | 100% (STRETCH vertical) | DSL `verticalConstraint: STRETCH` |
| 宽度 | 百分比驱动 (`{value}%`) | DSL `horizontalConstraint: SCALE` |
| 左圆角 | top-left: 14px, bottom-left: 14px | DSL `rectangleTopLeftCornerRadius: 14`, `rectangleBottomLeftCornerRadius: 14` |
| 右圆角 | 0px (独立角控制) | DSL `rectangleCornerToolIndependent: true` |

### 填充颜色

| 元素 | 色值 | 全局 Token |
|------|------|-----------|
| 默认填充条 | rgba(10, 89, 247, 0.2) | `--harmony-comp-emphasize-secondary` |
| 胶囊表面 | rgba(255, 255, 255, 0.298) | 组件专属 `--hm-progress-capsule-surface` |
| 边框 | rgba(10, 89, 247, 0.2) | `--harmony-comp-emphasize-secondary` |
| 文字 | rgba(0, 0, 0, 0.898) | `--harmony-font-primary` |
| Hover 叠加层 | rgba(0, 0, 0, 0.047) | `--harmony-interactive-hover` |
| Pressed 叠加层 | rgba(0, 0, 0, 0.098) | `--harmony-interactive-click` |
| Focus 环描边 | rgba(10, 89, 247, 1) | `--harmony-interactive-focus` |
| Disabled 填充条 | rgba(82, 145, 255, 0.2) | 组件专属 `--hm-progress-capsule-disabled-fill` |

### 排版

| 参数 | 值 | Tailwind / CSS |
|------|-----|---------------|
| fontFamily | HarmonyHeiTi | `font-family: 'HarmonyHeiTi', 'Geist Variable', sans-serif` |
| fontSize | 14px | `font-size: 14px` (`--harmony-font-size-body-m`) |
| fontWeight | 500 (Medium) | `font-weight: 500` |
| lineHeight | 19px (~1.357) | `line-height: 19px` (精确值，DSL text height 19px / fontSize 14px) |
| letterSpacing | 0 | `letter-spacing: 0` |
| textAlign | center | `text-align: center` |
| textColor | rgba(0, 0, 0, 0.898) | `--harmony-font-primary` |

### Focus 环

采用 Button 组件相同的 Focus 环模式（`::before` + CSS 变量控制 opacity）：

| 参数 | 值 | 来源 |
|------|-----|------|
| 偏移 | `inset: -4px`（组件外扩 4px） | 与 Button 组件 Focus 模式对齐 |
| 圆角 | `999px`（完全圆角） | 与 Button 组件 Focus 模式对齐 |
| 描边 | `2px solid var(--harmony-interactive-focus)` | 与 Button 共用同一全局 Token |
| 控制方式 | `--hm-progress-capsule-outline-opacity` CSS 变量 | `状态="Focus"` 时设为 `1`；`:focus-visible` 同样触发 |

> **取舍说明**：DSL 中 Focus 环为 `inset: -2px` + `border-radius: 100px` + 色值 `rgba(37,79,247,1)`。为与设计系统中 Button 组件保持一致的 Focus 视觉语言，改为使用 Button 的 `inset: -4px` + `border-radius: 999px` + `var(--harmony-interactive-focus)` 模式。

## 状态与交互

| 状态 | DSL 值 | 视觉效果 |
|------|--------|----------|
| Enabled | `状态=Enabled` | 默认状态：蓝色填充条 + 百分比文字 |
| Hover | `状态=Hover` | 叠加 rgba(0,0,0,0.047) 暗色层 |
| Pressed | `状态=Pressed` | 叠加 rgba(0,0,0,0.098) 暗色层 |
| Focus | `状态=Focus` | 2px 蓝色 focus 环 (76×32, -2px 偏移) |
| Disabled | `状态=Disabled` | opacity: 0.4; 填充条变 rgba(49,122,247,0.2) |

## Props

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `状态` | `"Enabled" \| "Hover" \| "Pressed" \| "Focus" \| "Disabled"` | `"Enabled"` | 组件状态 |
| `value` | `number` (0-100) | `27` | 进度百分比 |
| `className` | `string` | — | 额外 CSS 类名 |

### DSL ↔ Prop 对照

| DSL 属性路径 | Prop 名 | 取值集合 | 映射说明 |
|-------------|---------|---------|----------|
| `componentNormName` (子组件实例) | `状态` | `"Enabled"`, `"Hover"`, `"Pressed"`, `"Focus"`, `"Disabled"` | 直用 Pixso 原始属性名；5 种状态从 DSL `pixComponentTreeDslNodes` 中 5 个 SYMBOL 节点的 `componentNormName` 提取 |
| `🔤Text.nodeText` (进度文字) | `value` | `0–100` (number) | 文字 "27%" 为示例值；Prop 使用纯数字，组件内部拼接 `%` 后缀 |

## 样式引用

### 使用 `global.css` Token

| Token | 用途 |
|-------|------|
| `--harmony-comp-emphasize-secondary` | 填充条默认色 + 边框色 |
| `--harmony-font-primary` | 文字颜色 |
| `--harmony-interactive-hover` | Hover 叠加层 |
| `--harmony-interactive-click` | Pressed 叠加层 |

### 组件专属 CSS 自定义属性 (新增)

| 变量名 | 默认值 | Pixso 来源 | 说明 |
|--------|--------|-----------|------|
| `--hm-progress-capsule-surface` | rgba(255, 255, 255, 0.298) | `Light/on_primary30` (styleID 602:9503) | 胶囊表面填充。未升为全局 Token：该值为 `on_primary30`，覆盖场景窄（白色半透明表面上使用），暂作为组件级变量；若后续多组件复用可提升至 global.css |
| `--hm-progress-capsule-outline-opacity` | `0` | — | Focus 环可见性控制（与 Button `--button-outline-opacity` 同模式）。`状态="Focus"` 时为 `1` |
| `--hm-progress-capsule-overlay` | `transparent` | — | Hover/Pressed 状态叠加层颜色（与 Button `--button-overlay` 同模式） |
| `--hm-progress-capsule-opacity` | `1` | — | Disabled 状态整体透明度控制。`状态="Disabled"` 时为 `0.4` |
| `--hm-progress-capsule-fill-color` | `var(--harmony-comp-emphasize-secondary)` | `Light/brand20` | 填充条颜色。Disabled 态覆盖为 `Dark/brand20` |
| `--hm-progress-capsule-disabled-fill` | rgba(82, 145, 255, 0.2) | `Dark/brand20` (styleID 602:9537) | Disabled 态填充色（使用 Dark 主题 brand20）。该值为 Pixso 设计稿中 Disabled 态的覆盖颜色，应为意图性设计决策 |

## 取舍说明

1. **`get_screenshot` 返回 unsupported**：Pixso MCP `get_screenshot` 返回 `[Unsupported Image]` 格式，降级使用 `get_export_image` 成功获取 PNG 截图。1:1 对照基于 DSL 量化参数 + 截图人工复核。

2. **`design_to_code` batch expired**：生成代码的临时 URL（`localhost:3667/code/1781495176964/...`）返回 "Invalid URL"，批次缓存已过期。按 MCP 故障矩阵降级路径，不阻塞，以 DSL + 截图手写 CSS 实现。

3. **`get_variants` 返回 `{}`**：Pixso 组件变体接口未暴露此组件的变体属性。`variantOptions` 由 DSL `pixComponentTreeDslNodes` 中 5 个 SYMBOL 节点的 `componentNormName` 重建（Enabled/Hover/Pressed/Focus/Disabled）。

4. **文字 "27%" vs 填充条 46px**：DSL 中示例文字为 "27%"，但填充条宽度 46px / 72px ≈ 64%。设计稿中各状态的百分比文字为固定占位文本，实际操作中填充条宽度由 `value` prop 驱动，与文字同步。

5. **`lineHeight` 未映射到 `--harmony-font-size-body-m`**：DSL 文字高度 19px / fontSize 14px = ~1.357，全局 `--harmony-font-size-body-m` 为 14px/400 无精确 lineHeight 对应。使用 `line-height: 19px` 精确值实现，未修改全局 Token。

6. **未修改 `src/styles/global.css`**：组件级 CSS 变量（surface、outline-opacity、overlay、opacity、fill-color、disabled-fill）限定于本组件。若后续多组件复用可提升至 global.css 并补全 dark 模式。

7. **Focus 环与 DSL 偏差**：DSL 中 Focus 环偏移为 -2px、圆角 100px、色值 rgba(37,79,247,1)。为与 Button 组件保持一致的 Focus 视觉语言，改为 `inset: -4px` + `border-radius: 999px` + `var(--harmony-interactive-focus)`（与 Button `::before` Focus 环完全一致）。
