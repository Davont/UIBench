# FloatingToast 组件规格

## Metadata

| 项目 | 值 |
|------|------|
| 实现目录 | `src/components/FloatingToast/` |
| Stories 路径 | `src/components/FloatingToast/FloatingToast.stories.tsx` |
| Pixso 链接 | [5322:17](https://pixso.cn/app/design/HA_e8I2mE7Oa0b5ZoeokSA?item-id=5322:17) |
| MCP 工具 | `get_node_dsl`、`get_screenshot`、`get_variants`、`design_to_code`、`get_all_components` |
| 变体树 JSON | `src/components/FloatingToast/floating-toast.json` |

## 组件变体树 JSON

- 路径：`src/components/FloatingToast/floating-toast.json`
- 来源：`get_node_dsl` 直接读取节点 `5322:17` 的 4 个实例子节点
- 降级情况：`get_variants` 返回 `{}`，`design_to_code` 返回 500，因此按子节点名称 `通透度=标准 / 强 / 降档 / 弱` 重建 `variantOptions`

## 组成与用途

`FloatingToast` 是 `Toast-Phone` 的浮层材质版本封装，对外暴露单个可控 toast；Storybook `Overview` 1:1 对齐 Pixso 预览 frame，展示 4 个 `通透度` 变体在彩色背景上的差异。

导出项：
- `FloatingToast`
- `floatingToastTransparencies`
- `FloatingToastProps`
- `FloatingToastTransparency`

## 量化规格

### 根节点（Pixso frame `5322:17`）

| 属性 | 值 |
|------|------|
| 预览画板尺寸 | `171 × 217px` |
| 4 个 toast 宽高 | `119 × 36px` |
| 左偏移 | `28px` |
| 顶偏移 | `18 / 64 / 110 / 156px` |
| 垂直间距 | `10px` |

### Toast 本体（基于 `Toast-Phone` 主组件 `1:12693`）

| 属性 | Pixso DSL 值 | 实现 |
|------|------|------|
| 最小高度 | `36px` | `min-height: 36px` |
| 圆角 | `18px` | `border-radius: 18px` |
| 内边距 | `8px 16px` | `padding: 8px 16px` |
| 子项 gap | `10px` | `gap: 10px` |
| 文本字号 | `14px` | `font-size: 14px` |
| 文本字重 | `400` | `font-weight: 400` |
| 行高 | `19px` | `line-height: 19px` |
| 字距 | `0` | `letter-spacing: 0` |
| 文本颜色 | `Light/font_primary` | `var(--harmony-font-primary)` |

### 通透度材质映射

| 通透度 | Pixso 依据 | CSS 实现 |
|------|------|------|
| `标准` | fill `616:9117` + effect `1:347` | `--COMPONENT_ULTRA_THICK_fill` + `blur(40px)` + `0 10px 60px rgba(0,0,0,.2)` |
| `强` | fill `4903:5` + effect `4869:79` | `--Material_background_THICK_fill` + `background-blend-mode: var(--Material_background_THICK_fill_blend_mode)` + `blur(18px) saturate(120%)` |
| `降档` | fill `602:9417` + effect `4957:207` | `--harmony-comp_background_primary` + 无 backdrop blur + `0 8px 48px rgba(0,0,0,.08)` |
| `弱` | fill `4957:912` + `COMPONENT_THICK` 类模糊 | `--Floating_background_weak_fill` + `background-blend-mode: var(--Floating_background_weak_fill_blend_mode)` + `blur(40px)` |

Dark 模式下 `Dark/Blur/FLOATING_THICK` 使用多层材质填充：底层 `rgba(32,34,36,0.8)`、中层 `rgba(0,0,0,0.1)`、顶层 `rgba(255,255,255,0.1)`；全局 `hm-material-style-layer-floating-thick-*` dark 覆盖同步使用该分层。

## 状态与交互

该组件为纯展示型反馈，不包含 hover、pressed、disabled 等交互状态。实现中保留 `role="status"` 与 `aria-live="polite"`。

## Props

```ts
interface FloatingToastProps extends React.HTMLAttributes<HTMLDivElement> {
  内容?: string
  通透度?: "标准" | "强" | "降档" | "弱"
}
```

### DSL ↔ Prop 对照

| DSL 字段路径 | Prop 名 | 可取值 | 默认值 | 说明 |
|------|------|------|------|------|
| `pixComponentTreeDslNodes[*].childNode[0].childNode[0].nodeText` | `内容` | 任意字符串 | `"Toast content"` | 文本来源于 `Toast-Phone` 主组件标签节点 |
| `pixTreeNodes[0].childNode[*].name` | `通透度` | `["标准", "强", "降档", "弱"]` | `"标准"` | `get_variants` 不可用，按节点名称中的 `通透度=值` 重建 |

## 样式引用

复用全局 Token：
- `--COMPONENT_ULTRA_THICK_fill`
- `--Material_background_THICK_fill`
- `--Material_background_THICK_fill_blend_mode`
- `--Floating_background_weak_fill`
- `--Floating_background_weak_fill_blend_mode`
- `--harmony-comp_background_primary`
- `--harmony-font-primary`

新增全局 Token：无

## 取舍说明

1. Pixso 节点 `5322:17` 是“预览 frame”而非单一组件实例，因此实现上收敛为一个可控的 `FloatingToast` 组件，并用 Storybook `Overview` 还原原始 4 态排布。
2. 背景图在 DSL 中是 image fill，但当前 MCP 未直接提供该底图文件；因此 Storybook 预览使用 CSS 渐变重建背景氛围，并用 `get_screenshot` 对照整体构图。
3. `design_to_code` 返回 500，未采用 codegen 结果；实现完全以 `get_node_dsl + get_screenshot` 为准。
