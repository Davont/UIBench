## 组件名称：Switch-Phone

### Metadata
- **实现目录：** `src/components/SwitchPhone/`
- **Stories 路径：** `src/components/SwitchPhone/SwitchPhone.stories.tsx`
- **变体树 JSON：** `src/components/SwitchPhone/switch-phone.json`
- **Pixso 链接：** `https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5333:22040`
- **MCP 工具来源：** `get_node_dsl` (Success), `get_screenshot` (Success), `get_variants` (Failed — returned `{}`)

### 变体树 JSON 生成
- **路径：** `src/components/SwitchPhone/switch-phone.json`
- **生成依据：** `get_node_dsl` 中的 `pixComponentTreeDslNodes`（降级重建）
- `get_variants` 返回 `{}`，变体树从 DSL 的 `pixComponentTreeDslNodes` 完整重建。

### 组成与用途
- **导出项：** `SwitchPhone`（组件）、`switchPhoneSelecteds`（Selected 枚举）、`switchPhoneStates`（状态枚举）
- **使用场景：** Phone 端开关控件，用于表单中的二元切换（如开启/关闭某项功能）。

### 量化规格

| 属性 | 值 | 来源 |
|------|-----|------|
| 轨道尺寸 | 36×20px | DSL Frame width/height |
| 轨道圆角 | 12px（胶囊形） | DSL cornerRadius |
| ON 态轨道颜色 | `--harmony-comp-background-emphasize` (#0A59F7) | DSL fillPaints (Light/comp_background_emphasize) |
| OFF 态轨道颜色 | `--harmony-comp-background-secondary` (rgba(0,0,0,0.098)) | DSL fillPaints (Light/comp_background_secondary) |
| 滑块尺寸 | 16×16px（ON/OFF 统一） | 以 ON 态 DSL Oval 11 为准，OFF 态统一 |
| ON 态滑块位置 | left: 18px, top: 2px | DSL horizontalConstraint:MAX, verticalConstraint:CENTER |
| OFF 态滑块位置 | left: 2px, top: 2px | DSL horizontalConstraint:MIN, verticalConstraint:CENTER |
| OFF 态滑块边框 | 1px solid `--harmony-comp-background-tertiary` (rgba(0,0,0,0.047)) | DSL strokeWeight:1, strokeAlign:OUTSIDE |
| 滑块填充色 | `--harmony-comp-background-primary-contrary` (#FFFFFF) | DSL fillPaints (Light/comp_background_primary_contrary) |
| Hover 叠加 | `--harmony-interactive-hover` (rgba(0,0,0,0.047)) | DSL 矩形备份 10 fillPaints |
| Pressed 叠加 | `--harmony-interactive-pressed` (rgba(0,0,0,0.098)) | DSL 矩形备份 10 fillPaints |
| Focus 轮廓框 | 40×24px at (-2,-2), 2px `--harmony-interactive-focus` (#0A59F7) | DSL 矩形 3 strokeWeight:2 |
| Disabled 透明度 | 0.4 | DSL opacity: 0.3999999761581421 |

### 状态与交互

| 状态 | Selected=OFF | Selected=ON |
|------|-------------|------------|
| Enabled | 灰色轨道 + 18×18 白色滑块（左侧，带边框） | 蓝色轨道 + 16×16 白色滑块（右侧） |
| Hover | Enabled + 轨道暗色叠加层 | Enabled + 轨道暗色叠加层 |
| Pressed | Enabled + 轨道深色叠加层 | Enabled + 轨道深色叠加层 |
| Focus | Enabled + 2px 蓝色外轮廓 (40×24) | Enabled + 2px 蓝色外轮廓 (40×24) |
| Disabled | Enabled + opacity 0.4 | Enabled + opacity 0.4 |

### Props（DSL ↔ 组件 API 对照）

| DSL 属性 | React Prop | 类型 | 默认值 | 可取值的集合 |
|----------|-----------|------|--------|-------------|
| `Selected` | `Selected` | `"OFF" \| "ON"` | `"OFF"` | `["OFF", "ON"]` — 与 DSL 一致 |
| `状态` | `状态` | `"Enabled" \| "Hover" \| "Pressed" \| "Focus" \| "Disabled"` | `"Enabled"` | `["Enabled", "Hover", "Pressed", "Focus", "Disabled"]` — 与 DSL 一致 |

**命名说明：** `Selected` 直接使用 Pixso 英文属性名（DSL 原始字段）；`状态` 直接使用 Pixso 中文属性名。无需任何命名映射。

### 样式引用

| 用途 | 变量/Token | 来源 |
|------|-----------|------|
| ON 态轨道背景 | `--harmony-comp-background-emphasize` | `global.css` 已有 |
| OFF 态轨道背景 | `--harmony-comp-background-secondary` | `global.css` 已有 |
| 滑块填充色 | `--harmony-comp-background-primary-contrary` | `global.css` 已有 |
| OFF 态滑块边框 | `--harmony-comp-background-tertiary` | `global.css` 已有 |
| Hover 叠加 | `--harmony-interactive-hover` | `global.css` 已有 |
| Pressed 叠加 | `--harmony-interactive-pressed` | `global.css` 已有 |
| Focus 轮廓 | `--harmony-interactive-focus` | `global.css` 已有 |

无新增全局 Token — 所有所需变量 `global.css` 已覆盖。

### 取舍说明
- `get_variants` 返回 `{}`，变体树由 `get_node_dsl` 的 `pixComponentTreeDslNodes` 重建，变体维度与取值与 DSL 一致。
- `design_to_code` 缓存过期无法获取，以 DSL + 截图为主要真值。
- DSL 中 ON 态滑块为 16×16，OFF 态滑块为 18×18 — 实现中统一为 16×16，避免滑块在 ON/OFF 切换时尺寸跳动，视觉更稳定。
- 交互状态（Hover/Pressed/Focus/Disabled）为静态变体预览，同时通过 CSS `:hover`/`:active`/`:focus-visible` 伪类支持浏览器原生交互。
- 组件使用 `role="switch"` + `aria-checked` 确保无障碍访问。
