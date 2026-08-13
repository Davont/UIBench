# FloatingToolBarOnlyiconPhone（仅图标悬浮工具栏）

## Metadata

- **实现目录**: `src/components/FloatingToolBarOnlyiconPhone`
- **Stories 路径**: `src/components/FloatingToolBarOnlyiconPhone/FloatingToolBarOnlyiconPhone.stories.tsx`
- **Pixso 链接**: `https://pixso.cn/app/design/cjiPj-NOUA9kxV0f1bJ_og?item-id=5324:23620`
- **Item ID**: `5324:23620`
- **MCP 工具来源**: `get_node_dsl` + `get_screenshot`
- **组件变体树 JSON**: `src/components/FloatingToolBarOnlyiconPhone/floating-tool-bar-onlyicon-phone.json`

## 组件变体树 JSON

- **路径**: `src/components/FloatingToolBarOnlyiconPhone/floating-tool-bar-onlyicon-phone.json`
- **`variantOptions`**:
  - `属性 1` ∈ {`3`, `4`, `5`, `6`, `纵向-icon`}
  - `通透度` ∈ {`标准`, `平滑`, `降档`, `弱`}
  - `状态` ∈ {`Enable`, `Activated`}
- **降级说明**:
  - `get_variants` 返回空对象。
  - `design_to_code` 返回 `500`。
  - `降档` / `弱` 两列直接来自 DSL 实例名和节点尺寸。
  - `标准` / `平滑` 两列由同版截图矩阵位置与命名模式补全，已在 stories 中按同坐标复现。

## 量化规格

### Root 容器

| 变体 | 宽度 | 高度 | 圆角 |
|------|------|------|------|
| `属性 1=3` | 168px | 56px | 28px |
| `属性 1=4` | 224px | 56px | 28px |
| `属性 1=5` | 280px | 56px | 28px |
| `属性 1=6` | 328px | 56px | 28px |
| `属性 1=纵向-icon` | 56px | 224px | 28px |

### Icon Slot

| 参数 | 值 | 说明 |
|------|----|------|
| 单项按钮尺寸 | 56×56px | 水平/垂直统一 |
| 图标尺寸 | 24×24px | 来自 `.icon` 子组件 |
| 默认激活项 | 第 2 项 | 与 Pixso 矩阵一致 |
| `属性 1=6` 特例 | 第 1 项后插入 1px divider | 对齐截图中的分隔竖线 |

## 颜色与材质映射

| Pixso / 语义 | 实现 |
|--------------|------|
| `标准` | `--FLOATING_THIN_fill` + `--harmony-floating-thin-highlight` + `--harmony-floating-thin-shadow` |
| `平滑` | `--harmony-floating-ultra-thick-surface` + `--harmony-floating-ultra-thick-shadow` |
| `降档` | `--comp_background_color_floating_smooth_fill` + `1px` 浮层描边 |
| `弱` | `--Floating_background_weak_fill` |
| 未激活图标 | `--harmony-icon-primary` |
| 激活图标 | `--harmony-icon-emphasize` |

## Props

### DSL ↔ Prop 对照

| DSL 字段 | Prop 名 | 类型 | 默认值 | 可取值 |
|----------|---------|------|--------|--------|
| `属性 1` | `属性 1` | `FloatingToolBarOnlyiconPhoneVariant` | `"3"` | `"3" \| "4" \| "5" \| "6" \| "纵向-icon"` |
| `通透度` | `通透度` | `FloatingToolBarOnlyiconPhoneTransparency` | `"标准"` | `"标准" \| "平滑" \| "降档" \| "弱"` |

### 扩展 Props

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `items` | `FloatingToolBarOnlyiconPhoneItem[]` | 按变体自动生成 | 允许覆盖图标、激活态、点击事件 |
| `selectedIndex` | `number` | 非受控时取 `defaultSelectedIndex` | 当前选中项索引（0-based），可通过 `items[selectedIndex]` 获得具体项；传入后进入受控模式，解析值同步输出到根节点 `data-selected-index` |
| `defaultSelectedIndex` | `number` | `1` | 非受控模式的初始选中项索引 |
| `onSelectedIndexChange` | `(index: number) => void` | — | 用户选择某一项时返回其索引 |
| `onActiveChange` | `(index: number) => void` | — | 已弃用的兼容回调，请使用 `onSelectedIndexChange` |
| `className` | `string` | — | 附加类名 |

## Storybook

- `Playground`: 单实例 Controls，直接对照 DSL 两个变体轴。
- `VariantGallery`: 4 组通透度 × 5 个结构变体。
- `PixsoReferenceMatrix`: 按截图矩阵的近似画板坐标绝对定位，便于 1:1 肉眼复核。

## 校验结论

- 该节点的代码化数据源不完整，因此本实现采用 **DSL 已知尺寸 + 截图矩阵重建**。
- 自动 SSIM 未执行；当前通过 Storybook 变体矩阵与 Pixso 截图进行人工逐列对照。
- 未新增全局 token，全部复用 `src/styles/global.css` 现有浮层材质变量。
