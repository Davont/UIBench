# FloatingChipsTabPhone

## Metadata

- **实现目录**: `src/components/FloatingChipsTabPhone/`
- **Stories 路径**: `src/components/FloatingChipsTabPhone/FloatingChipsTabPhone.stories.tsx`
- **Pixso 链接**: `https://pixso.cn/app/design/QeDttX-H4qVEUZXJjNfTCw?item-id=5349:632`
- **Item ID**: `5349:632`（画板 `组合` 1560×240）
- **MCP 工具来源**: `get_node_dsl(itemId=5349:632)`

## 组件变体树 JSON

- **路径**: `src/components/FloatingChipsTabPhone/floating-chips-tab-phone.json`
- **生成依据**: `get_node_dsl` 返回的 `pixTreeNodes` 与 `localStyleMap`
- **降级说明**: `get_variants` 返回 `{}`，`design_to_code` 返回 500；`variantOptions` 与 `pixTreeNodes` 按四列材质样式和三行内容类型手工重建

## 组成与用途

- **FloatingChipsTabPhone**: 手机端悬浮胶囊标签栏，使用 `items: { key, label, icon }[]` 传入页签数据，用于顶部横向分类切换、筛选导航与带更多入口的场景
- 组件内部由 36px 高的 floating chip 和可选尾部更多按钮组成，整体画板宽 360px、高 56px

## 量化规格

| 项目 | 数值 |
|------|------|
| 组件尺寸 | 360 × 56px |
| Chip 高度 | 36px |
| Chip 水平间距 | 8px（图标型为 10px） |
| Chip 圆角 | 20px |
| Chip 宽度 | 未选中 **65px** / 选中 **87px**（DSL `enable` / `activated`） |
| Chip 内边距 | 8px 16px |
| More 按钮尺寸 | 36 × 36px |
| More 按钮位置 | `right: 16px; top: 10px` |
| 标题字号 | 14px |
| 标题行高 | 20px |
| 标题字距 | 0 |
| 标题字重 | 默认 400，选中态 500 |
| 图标尺寸 | 16 × 16px |

## 状态与交互

- `类型=文字`：5 个纯文案 chip（`div[role=tab]`），右侧渐隐裁切
- `类型=更多`：4 个纯文案 chip + 尾部更多按钮（`right:16px; top:10px`）
- `类型=图标`：5 个五角星图标+文案 chip，末项渐隐；图标为 Pixso `.TV` → `HMSymbolIcon star_fill`（U+F0009，16×16）
- 图标颜色：浅色底 `--harmony-icon-primary`（DSL `Light/font_primary`）；选中底 `--harmony-icon-on-primary`（DSL `Light/icon_on_primary`）
- 子页签使用 `div[role=tab]`，更多按钮保留 `button`（DSL `3.Icon Button`）
- `activeKey`：当前选中的 chip（87px 宽）；标准档与未选中相同叠 `FLOATING_ULTRA_THIN` 材质节点，再在其上叠 `--Floating_backgrount_emphasize_fill` 填充层

## Props

| Prop | 类型 | 默认值 | 可取值 | 说明 |
|------|------|--------|--------|------|
| `items` | `FloatingChipsTabPhoneItem[]` | — | `[{ key, label, icon, disabled }]` | 页签数据源，必须以数组传入 |
| `activeKey` / `defaultActiveKey` | `string` | 首项 `key` | `items[n].key` | 受控/非受控选中项 |
| `onActiveKeyChange` | `(key, item) => void` | — | — | 切换回调 |
| `通透度` | `string` | `"标准"` | `"标准"` / `"强档"` / `"降档"` / `"弱挡"` | 对应 Pixso 变体 `通透度=标准/强/降档/弱` |
| `类型` | `string` | `"文字"` | `"文字"` / `"更多"` / `"图标"` | 对应 Pixso 三行不同内容结构 |

```tsx
const items = [
  { key: "home", label: "首页", icon: <HMSymbolIcon name="house_fill" size={24} /> },
  { key: "explore", label: "探索", icon: <HMSymbolIcon name="discover_fill" size={24} /> },
  { key: "profile", label: "我的", icon: <HMSymbolIcon name="person_crop_circle_fill_1" size={24} /> },
]
```

### DSL ↔ Prop 对照

| DSL 字段 | 最终 Prop | 说明 |
|---------|-----------|------|
| Pixso 变体 `通透度=标准` | `通透度="标准"` | 样式 `Light/Blur/FLOATING_ULTRA_THIN` 多层材质层 |
| Pixso 变体 `通透度=强` | `通透度="强档"` | 样式 `Light/Blur/Material_background_ULTRA_THIN` |
| Pixso 变体 `通透度=降档` | `通透度="降档"` | 样式 `Light/comp_background_color_floating_smooth` + `Light/Floating_background_line` |
| Pixso 变体 `通透度=弱` | `通透度="弱挡"` | 样式 `Light/Floating_background_weak` |
| `pixTreeNodes` 三行结构 | `类型` | 根据同一截图中三种布局结构重建 |

## 样式引用

- `.hm-material-style-layer-floating-ultra-thin-fill-*` / `.hm-material-style-layer-floating-ultra-thin-effect-*` — 标准档 chip / more 按钮
- `--Floating_backgrount_emphasize_fill` / `--Floating_backgrount_emphasize_fill_blend_mode` — 标准档激活 chip 强调混合层
- `--comp_background_color_floating_smooth_fill`
- `--Floating_background_weak_fill`
- `--Floating_backgrount_emphasize_fill`
- `--Floating_background_line_fill`
- `--harmony-font-secondary`
- `--harmony-icon-secondary`
- `--harmony-font-on-primary`
- `--harmony-icon-on-primary`

## 取舍说明

1. Pixso 当前节点是整块对照画板而非单一变体组件，因此 `通透度` / `类型` 由 DSL 结构与截图共同归纳，不是直接从 `get_variants` 提取。
2. `FloatingChipsTabPhone` 的 `PixsoReference` story 使用 DSL 中的绝对定位坐标还原 1661 × 358 画板，用于人工 1:1 对照。
3. `design_to_code` 返回 500，未阻塞实现；样式由 `get_node_dsl` 中的 fill/effect/style 信息手工落地。
