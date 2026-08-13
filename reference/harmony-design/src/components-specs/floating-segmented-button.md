# FloatingSegmentedButton

## Metadata

- 所属注册表：`src/components-specs/components.json`（id: `floating-segmented-button`）
- 实现目录：`src/components/Selection/FloatingSegmentedButton/`
- Stories 路径：`src/components/Selection/FloatingSegmentedButton/FloatingSegmentedButton.stories.tsx`
- Pixso 链接：`https://pixso.cn/app/design/HA_e8I2mE7Oa0b5ZoeokSA?item-id=5322:984`
- item-id：`5322:984`
- Item 变体 Pixso 链接：`https://pixso.cn/app/design/d0WMuB0Im216ZfRVW4uwyQ?item-id=4528:12914`
- Item 变体 item-id：`4528:12914`
- MCP 工具来源：`get_node_dsl`、`get_screenshot`

## 组件变体树 JSON

- 路径：`src/components/Selection/FloatingSegmentedButton/floating-segmented-button.json`
- 生成方式：`get_node_dsl` item `5322:984` 成功，`get_variants` 返回 `{}`，据 root child name `组数=*, 通透度=*` 与截图矩阵重建
- Item 变体：`get_variants` item `4528:12914` 返回 `状态=Enable / 状态=activated / 状态=Selected`，`Icon`、`Text` 来自截图右侧变体开关
- 备注：`design_to_code` 返回 `500`，未采用 codegen 结果

## 组成与用途

- `FloatingSegmentedButton`：带 floating 材质容器的单选分段按钮
- 默认子项由 `.highlight` 24px 图标与 `Tabs` 文案组成
- 适用于地图/浮层场景下的快速模式切换

## 量化规格

- 容器：`328 × 64`
- 容器 padding：`4`
- 容器圆角：`20`
- 子项高度：`56`
- 子项圆角：`18`
- 子项内边距：`4 12`
- 子项布局：vertical，`gap=4`
- 文本：`HarmonyHeiTi / Medium / 14px / line-height 20px / letter-spacing 0`
- 图标：`.highlight`，`24 × 24`
- `activated` 子项：`comp_background_secondary` 背景，阴影 `0 0 3 rgba(0,0,0,0.2)`，文字与图标为 `font_primary/icon_primary`
- `Selected` 子项：`comp_background_emphasize` 背景，文字与图标为 `font_on_primary/icon_on_primary`
- `Enable` 子项：透明底，文字与图标为 `font_secondary/icon_secondary`

## 通透度规格

- `弱`
  使用 `--Floating_background_weak_fill`，blend mode `--Floating_background_weak_fill_blend_mode`，弱模糊与轻内高光
- `标准`
  使用 `hm-material-style-layer-floating-thin-*` 多层材质，视觉真值以 Pixso screenshot 为准
- `强`
  使用 `--Material_background_ULTRA_THIN_fill`，`blur(8px) saturate(120%)`
- `降档`
  使用 `--comp_background_color_floating_smooth_fill` + `--Floating_background_line_fill` 边线

## Props

### DSL ↔ Prop 对照

| DSL 字段 | Prop 名 | 取值 | 默认值 | 说明 |
|---|---|---|---|---|
| `组数` | `组数` | `2 \| 3 \| 4 \| 5` | `3` | 直接对齐 DSL |
| `通透度` | `通透度` | `弱 \| 标准 \| 强 \| 降档` | `弱` | 直接对齐 DSL |
| `.FloatingItems/状态` | `状态` | `Enable \| activated \| Selected` | `activated` | 当前激活项的默认 Item 状态；也可在 `items[]` 内逐项覆写 |
| `.FloatingItems/Text` | `Text` | `true \| false` | `true` | 全局文本可见性；也可在 `items[]` 内逐项覆写 |
| `.FloatingItems/Icon` | `Icon` | `true \| false` | `true` | 全局图标可见性；也可在 `items[]` 内逐项覆写 |

### 运行时补充 Props

| Prop 名 | 类型 | 默认值 | 用途 |
|---|---|---|---|
| `items` | `FloatingSegmentedButtonItem[]` | 按 `组数` 生成 `Tabs` | 业务内容注入 |
| `selectedIndex` | `number` | 非受控时取 `defaultSelectedIndex` | 当前激活项 |
| `defaultSelectedIndex` | `number` | `1` | 默认激活第二项，和 Pixso 示例一致 |
| `onSelectedIndexChange` | `(index: number) => void` | — | 交互回调 |

### FloatingSegmentedButtonItem

| 字段 | 类型 | 默认值 | 用途 |
|---|---|---|---|
| `label` | `string` | `Tabs` | Item 文案 |
| `icon` | `ReactNode` | `.highlight` HMSymbol | Item 图标 |
| `状态` | `Enable \| activated \| Selected` | 未设置时由 `selectedIndex` 推导 | 单个 Item 状态 |
| `Icon` | `boolean` | 继承组件 `Icon` | 单个 Item 图标可见性 |
| `Text` | `boolean` | 继承组件 `Text` | 单个 Item 文本可见性 |

## 样式引用

- 复用 `src/styles/global.css`：
  `--Floating_background_weak_fill`
  `--Floating_background_weak_fill_blend_mode`
  `--Material_background_ULTRA_THIN_fill`
  `--Material_background_ULTRA_THIN_fill_blend_mode`
  `--comp_background_color_floating_smooth_fill`
  `--Floating_background_line_fill`
  `--harmony-comp-background-secondary`
  `--harmony-comp-background-emphasize`
  `--harmony-font-primary`
  `--harmony-font-secondary`
  `--harmony-font-on-primary`
- 复用全局材质层类：
  `hm-material-style-layer-floating-thin-fill-1`
  `hm-material-style-layer-floating-thin-fill-2`
  `hm-material-style-layer-floating-thin-effect-1..8`
- 无新增全局 Token

## 状态与交互

- `default`：容器浮层材质，第二项 `activated`
- `Enable`：Item 透明底，继承非激活文字/图标色
- `activated`：Item 使用浅色选中背板
- `Selected`：Item 使用强调蓝背板
- `focus-visible`：子项外描边
- `hover/pressed`：当前版本未额外叠加交互蒙层，保持与 Pixso 静态稿一致
- `disabled`：DSL 当前未提供 disabled 变体，未扩展

## 取舍说明

1. `get_variants` 返回空对象，组件变体树按 DSL 实例名和截图矩阵重建。
2. `design_to_code` 返回 `500`，最终实现完全以 `get_node_dsl + get_screenshot` 为真值手写。
3. Pixso 根节点截图中 `标准`/`强` 部分实例 guid 输出截断，JSON 中以 `reconstructed-*` 占位保留树结构，并在规格中注明来源。
4. 为了让组件可实际用于业务，补充了 `items / selectedIndex / onSelectedIndexChange` 这组运行时 props；核心 DSL 变体 `组数 / 通透度 / Text / Icon` 未被改名或改写。
