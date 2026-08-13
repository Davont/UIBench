# FloatingToolBarTextPhone（带文案悬浮工具栏）

## Metadata

- **实现目录**: `src/components/FloatingToolBarTextPhone`
- **Stories 路径**: `src/components/FloatingToolBarTextPhone/FloatingToolBarTextPhone.stories.tsx`
- **Pixso 链接**: `https://pixso.cn/app/design/cjiPj-NOUA9kxV0f1bJ_og?item-id=5324:24059`
- **Item ID**: `5324:24059`
- **MCP 工具来源**: `get_node_dsl` + `get_screenshot`
- **组件变体树 JSON**: `src/components/FloatingToolBarTextPhone/floating-tool-bar-text-phone.json`

## 组件变体树 JSON

- **路径**: `src/components/FloatingToolBarTextPhone/floating-tool-bar-text-phone.json`
- **`variantOptions`**:
  - `属性 1` ∈ {`3`, `4`, `5`, `6`, `纵向-icon`}
  - `通透度` ∈ {`标准`, `平滑`, `降档`, `弱`}
  - `状态` ∈ {`Enable`, `Activated`}
- **降级说明**:
  - `get_variants` 返回空对象。
  - `design_to_code` 返回 `500`。
  - `降档` / `弱` 的结构与尺寸直接来自 DSL。
  - `标准` / `平滑` 由同版截图矩阵 + 已知命名规律补全。

## 量化规格

### Root 容器

| 变体 | 宽度 | 高度 | 圆角 |
|------|------|------|------|
| `属性 1=3` | 192px | 56px | 28px |
| `属性 1=4` | 248px | 56px | 28px |
| `属性 1=5` | 304px | 56px | 28px |
| `属性 1=6` | 328px | 56px | 28px |
| `属性 1=纵向-icon` | 56px | 248px | 28px |

### Item Slot

| 参数 | 值 | 说明 |
|------|----|------|
| 常规项宽度 | 56px | `3/4/5` 和纵向项 |
| `属性 1=6` 项宽度 | 约 50.67px | `328 - 24` 后六等分 |
| 内边距 | 水平 `12px` / 纵向上下 `12px` | 来自 autoLayout |
| 图标尺寸 | 24×24px | DSL 子组件 |
| 文案 | `Tab` | 默认文案 |
| 字号/行高 | `10px / 14px` | `Font/Caption_M/Regular` |
| 激活项 | 第 2 项 | 与截图矩阵一致 |

## 颜色与材质映射

| Pixso / 语义 | 实现 |
|--------------|------|
| `标准` | `--FLOATING_THIN_fill` + `--harmony-floating-thin-highlight` |
| `平滑` | `--harmony-floating-ultra-thick-surface` |
| `降档` | `--comp_background_color_floating_smooth_fill` + `1px` 描边 |
| `弱` | `--Floating_background_weak_fill` |
| 普通图标/文字 | `--harmony-icon-primary` / `--harmony-font-primary` |
| 激活图标/文字 | `--harmony-icon-emphasize` / `--harmony-font-emphasize` |

## Props

### DSL ↔ Prop 对照

| DSL 字段 | Prop 名 | 类型 | 默认值 | 可取值 |
|----------|---------|------|--------|--------|
| `属性 1` | `属性 1` | `FloatingToolBarTextPhoneVariant` | `"3"` | `"3" \| "4" \| "5" \| "6" \| "纵向-icon"` |
| `通透度` | `通透度` | `FloatingToolBarTextPhoneTransparency` | `"标准"` | `"标准" \| "平滑" \| "降档" \| "弱"` |

### 扩展 Props

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `items` | `FloatingToolBarTextPhoneItem[]` | 自动生成 `Tab` 项 | 可覆盖文案、图标、状态、事件 |
| `selectedIndex` | `number` | 非受控时取 `defaultSelectedIndex` | 当前选中项索引（0-based），可通过 `items[selectedIndex]` 获得具体项；传入后进入受控模式，解析值同步输出到根节点 `data-selected-index` |
| `defaultSelectedIndex` | `number` | `1` | 非受控模式的初始选中项索引 |
| `onSelectedIndexChange` | `(index: number) => void` | — | 用户选择某一项时返回其索引 |
| `onActiveChange` | `(index: number) => void` | — | 已弃用的兼容回调，请使用 `onSelectedIndexChange` |
| `className` | `string` | — | 附加类名 |

## Storybook

- `Playground`: 单实例 controls。
- `VariantGallery`: 4 组材质 × 5 个结构变体。
- `PixsoReferenceMatrix`: 按 Pixso 截图坐标绝对定位，便于人工 1:1 复核。

## 校验结论

- 该节点不能直接走 codegen，因此本实现采用 **DSL 量化尺寸 + 截图矩阵重建**。
- 未新增全局 token，材质与颜色全部复用现有 `src/styles/global.css`。
- 自动 SSIM 未执行，当前通过 Storybook 与 Pixso 截图进行人工对照。
