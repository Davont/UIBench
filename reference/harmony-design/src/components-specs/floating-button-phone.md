# FloatingButton-Phone

## Metadata

- **实现目录**: `src/components/FloatingButtonPhone/`
- **Stories 路径**: `src/components/FloatingButtonPhone/FloatingButtonPhone.stories.tsx`
- **Pixso 链接**: `https://pixso.cn/app/design/QeDttX-H4qVEUZXJjNfTCw?item-id=4950:6`
- **MCP 工具来源**: `get_screenshot` (Success), `get_node_dsl` (Success for representative nodes), `get_all_components` (Success), `get_variants` (Failed — 返回 `{}`)

## 组件变体树 JSON

- **路径**: `src/components/FloatingButtonPhone/floating-button-phone.json`
- **生成方式**: `get_variants` 返回空对象 `{}`，变体树按 `get_all_components` 中本地 `FloatingButton-Phone` 组件集重建
- **MCP 调用**: `get_screenshot` / `get_node_dsl` / `get_all_components` (itemId=4950:6)

## 组成与用途

- **导出项**: `FloatingButtonPhone`（组件）、`floatingButtonPhoneSizes`、`floatingButtonPhoneTypes`、`floatingButtonPhoneStates`、`floatingButtonPhoneOpacities`
- **使用场景**: Phone 端悬浮材质主操作按钮，支持强调、普通、警告、选中与未选中视觉语义，并覆盖 loading / focus / disabled 状态

## 量化规格

| 参数 | 值 | 来源 |
|------|-----|------|
| Medium 尺寸 | 120 × 40px | DSL `5333:21992` / `5333:22005` |
| Medium Selected 尺寸 | 高度 28px | 当前实现按产品确认调整 |
| Medium Unselected 尺寸 | 高度 28px | 当前实现按产品确认调整 |
| Medium Loading | 128 × 40px | DSL `5333:21994` |
| Small 尺寸 | 72 × 28px | DSL `5333:21990` / `5333:22003` |
| Small Loading | 92 × 28px | DSL `5333:21981` |
| Medium 内边距 | 16px 左右，8px 间距 | DSL auto layout |
| Small 内边距 | 8px 左右，4px 间距 | DSL auto layout |
| 圆角 | 20px / 14px | DSL `cornerRadius` |
| 字号 | 16px / 14px | DSL text styles `602:9659` / `602:9662` |
| 字重 | 500（强调态），400（Selected/Unselected） | 参照 Pixso 文字观感与仓库 Button-Phone 同类规则 |
| 阴影 | `0 8px 48px rgba(0,0,0,0.08)` 基础层 | DSL effect style `4957:207` |

## 状态与交互

- `Enabled`: 默认展示
- `Hover`: 覆盖 `--harmony-interactive-hover`
- `Pressed`: 覆盖 `--harmony-interactive-click`
- `Focus`: 外侧 2px 强调焦点环
- `Loading`: 显示 Pixso 同款椭圆轨道 loading glyph，并切换文案为 `Loading`
- `Disabled`: 整体透明度 0.4

## Props

| DSL 字段 | Prop 名 | 类型 | 默认值 | 可取值的集合 |
|----------|---------|------|--------|-------------|
| `尺寸` | `尺寸` | `"Medium" \| "Small"` | `"Medium"` | Medium, Small |
| `类型` | `类型` | `"Emphasized" \| "Normal" \| "Warning" \| "Selected" \| "Unselected"` | `"Emphasized"` | Emphasized, Normal, Warning, Selected, Unselected |
| `状态` | `状态` | `"Enabled" \| "Hover" \| "Pressed" \| "Focus" \| "Loading" \| "Disabled"` | `"Enabled"` | Enabled, Hover, Pressed, Focus, Loading, Disabled |
| `通透度` | `通透度` | `"标准" \| "强" \| "降档" \| "弱"` | `"弱"` | 标准, 强, 降档, 弱 |
| 文案 | `children` | `ReactNode` | `BUTTON` / `BTN` | 可传业务文案；`状态="Loading"` 时强制显示 `Loading` |
| App 导航目标 | `navigateTo` / `导航目标` | `string` | `undefined` | 多页真实 App 中的 page id / route key；点击时触发导航协议 |
| App 导航回调 | `onNavigate` | `(target, event) => void` | `undefined` | 由页面或 App shell 接收并切换当前页面 |

## App 导航协议

- `FloatingButtonPhone` 保持原生 `button` 语义，不引入外部 router。
- 当传入 `navigateTo` 或中文别名 `导航目标` 时，点击顺序为：先执行 `onClick`；若未 `preventDefault()` 且按钮非 `Disabled` / `Loading`，再调用 `onNavigate(target, event)`；最后派发可冒泡、可取消的 `hm:navigate` CustomEvent。
- `hm:navigate.detail` 固定包含 `{ source: "FloatingButtonPhone", target }`，多页 App shell 可以在根节点监听该事件并执行 `setCurrentPage(target)`。
- 若 `onClick` 或 `onNavigate` 调用了 `event.preventDefault()`，不再派发 `hm:navigate`，用于表单校验、权限拦截或二次确认。
- 生成真实 App / 多页 Demo 时，作为页面跳转入口的 FloatingButton 必须传入 `navigateTo` / `导航目标`，并由上层 shell 显式接入 `onNavigate` 或 `hm:navigate` 事件；不得只渲染纯视觉按钮。

### DSL ↔ Prop 对照

- **属性名策略**: 直接使用 Pixso 原始字段名，无命名映射
- **变体重建依据**: `get_variants` 不可用，组件名与 DSL 实例名稳定出现 `尺寸=... / 类型=... / 状态=... / 通透度=...`
- **补充说明**: `类型` 取值集合依照 FloatingButton-Phone 与现有 `Button-Phone` 语义对齐，保留强调、普通、警告、选中、未选中五类悬浮按钮；`通透度` 已按本地组件集补齐 `标准 / 强 / 降档 / 弱` 四档，共 240 个变体

## 样式引用

- `--Floating_backgrount_emphasize_fill` — Emphasized 背景；组件内按 Pixso「穿透」效果使用 `background-blend-mode: normal, normal`
- `--Floating_backgrount_emphasize_secondary_fill` — Selected 背景
- `.hm-material-style-layer-floating-thin-*` — `标准` 通透度多层材质（`Light/Blur/FLOATING_THIN`）
- `--FLOATING_THIN_fill` — 其他通透度或未使用材质层时的表面参考
- `--Material_background_ULTRA_THIN_fill` — 强通透度表面
- `--comp_background_color_floating_smooth_fill` — 降档通透度表面
- `--Floating_background_weak_fill` — 弱通透度表面
- `--Floating_background_line_fill` — 降档通透度描边
- `--harmony-font-primary` / `--harmony-font-emphasize` / `--harmony-font-on-primary`
- `--harmony-warning`
- `--harmony-interactive-hover` / `--harmony-interactive-click` / `--harmony-interactive-focus`

**无新增全局 Token** — 现有 `global.css` 变量已覆盖该组件所需的所有色值与材质语义。

## 取舍说明

- **Skill 注册说明**: `skills/01-resource-injection/pixso-to-shadcn-react/SKILL.md` 不在当前会话可直接启用的已注册 skill 列表中，因此本次按其仓库工作流手动执行，而不是通过平台的 skill loader 启用
- **`get_variants` 失败**: 组件变体树通过 `get_all_components` 中的本地 `FloatingButton-Phone` 组件集重建，已写入 `floating-button-phone.json`
- **通透度补齐**: `get_all_components` 显示该组件集包含 `标准 / 强 / 降档 / 弱` 四档，每档 60 个变体；样式映射沿用同库浮动组件材质 token
- **Selected 高度调整**: 按当前实现要求，`尺寸=Medium` 且 `类型=Selected` 时高度收敛为 `28px`，与默认 `Medium` 40px 区分处理
- **Unselected 高度调整**: 按当前实现要求，`尺寸=Medium` 且 `类型=Unselected` 时高度也收敛为 `28px`
