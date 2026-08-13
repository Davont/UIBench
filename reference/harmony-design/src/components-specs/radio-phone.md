## 组件名称：Radio-Phone

### Metadata
- **实现目录：** `src/components/RadioPhone/`
- **Stories 路径：** `src/components/RadioPhone/RadioPhone.stories.tsx`
- **变体树 JSON：** `src/components/RadioPhone/radio-phone.json`
- **Pixso 链接：** `https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5331:21014`
- **MCP 工具来源：** `get_node_dsl` (Success), `get_screenshot` (Success), `get_variants` (Failed — returned `{}`)

### 变体树 JSON 生成
- **路径：** `src/components/RadioPhone/radio-phone.json`
- **生成依据：** `get_node_dsl` 中的 `pixComponentTreeDslNodes`（降级重建）
- `get_variants` 返回 `{}`，变体树从 DSL 的 `pixComponentTreeDslNodes` 完整重建。

### 组成与用途
- **导出项：** `RadioPhone`（组件）、`radioPhoneSelecteds`（Selected 枚举）、`radioPhoneStates`（状态枚举）
- **使用场景：** Phone 端单选控件，用于表单中的单项选择。

### 量化规格

| 属性 | 值 | 来源 |
|------|-----|------|
| 外层尺寸 | 24×24px | DSL Frame width/height |
| 外层圆角 | 12px（圆形） | DSL cornerRadius |
| 内圈尺寸 | 20×20px | DSL Group/椭圆 width/height |
| 内圈圆角 | 10px | DSL cornerRadius (Rectangle 2375) |
| ON 态内点尺寸 | 8×8px | 基于 DSL Rectangle 62 几何估算 |
| ON 态内点圆角 | 4px | 圆形 |
| OFF 态边框 | 1px solid `--harmony-icon-tertiary` | DSL strokeWeight:1, strokeAlign:INSIDE |
| OFF 态填充 | `rgba(255,255,255,0.2)` | DSL fillPaints (Light/fg_color_unchecked) |
| ON 态背景 | `--harmony-comp-background-emphasize` (#0A59F7) | DSL fillPaints (Light/comp_background_emphasize) |
| ON 态内点颜色 | `--harmony-comp-background-primary-contrary` (#FFF) | DSL fillPaints (Light/comp_background_primary_contrary) |
| 内点阴影 | 0.05px 1.41px 2px rgba(0,0,0,0.1) | DSL dropShadow effect |
| Focus 轮廓 | 2px `--harmony-interactive-focus` | DSL strokeWeight:2, strokeAlign:OUTSIDE |
| Hover 叠加 | `--harmony-interactive-hover` (#000 0.047) 24×24 圆 | DSL 椭圆 5 fillPaints |
| Disabled 透明度 | 0.4 | DSL opacity: 0.3999999761581421 |

### 状态与交互

| 状态 | Selected=OFF | Selected=ON |
|------|-------------|------------|
| Enabled | 灰色圆环（1px border） | 蓝色填充圆 + 白色内点 + 阴影 |
| Hover | Enabled + 24×24 hover 叠加层 | Enabled + 24×24 hover 叠加层 |
| Focus | Enabled + 2px 蓝色外轮廓 | Enabled + 2px 蓝色外轮廓 |
| Disabled | Enabled + opacity 0.4 | Enabled + opacity 0.4 |

### Props（DSL ↔ 组件 API 对照）

| DSL 属性 | React Prop | 类型 | 默认值 | 可取值的集合 |
|----------|-----------|------|--------|-------------|
| `Selected` | `Selected` | `"OFF" \| "ON"` | `"OFF"` | `["OFF", "ON"]` — 与 DSL 一致 |
| `状态` | `状态` | `"Enabled" \| "Hover" \| "Focus" \| "Disabled"` | `"Enabled"` | `["Enabled", "Hover", "Focus", "Disabled"]` — 与 DSL 一致 |

**命名说明：** `Selected` 直接使用 Pixso 英文属性名（DSL 原始字段）；`状态` 直接使用 Pixso 中文属性名。无需任何命名映射。

### 样式引用

| 用途 | 变量/Token | 来源 |
|------|-----------|------|
| OFF 态边框 | `--harmony-icon-tertiary` | `global.css` 已有 |
| ON 态背景 | `--harmony-comp-background-emphasize` | `global.css` 已有 |
| ON 态内点颜色 | `--harmony-comp-background-primary-contrary` | `global.css` 已有 |
| Hover 叠加 | `--harmony-interactive-hover` | `global.css` 已有 |
| Focus 轮廓 | `--harmony-interactive-focus` | `global.css` 已有 |

无新增全局 Token — 所有所需变量 `global.css` 已覆盖。

### 取舍说明
- `get_variants` 返回 `{}`，变体树由 `get_node_dsl` 的 `pixComponentTreeDslNodes` 重建，变体维度与取值与 DSL 一致。
- `design_to_code` 缓存过期无法获取，以 DSL + 截图为主要真值。
- ON 态标记使用本地 `HMSymbolIcon name="checkmark"`（U+F0013），保持 18×17 外盒、语义颜色和原阴影规格。
- 交互状态（Hover/Focus/Disabled）为静态变体预览，同时通过 CSS `:hover`/`:focus-visible` 伪类支持浏览器原生交互。
