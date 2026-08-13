# AlphabetIndexerLable 组件规格

## Metadata

| 字段 | 值 |
|------|------|
| 组件 ID | `alphabet-indexer-lable` |
| 实现目录 | `src/components/Views/AlphabetIndexerLable/` |
| Stories 路径 | `src/components/Views/AlphabetIndexerLable/AlphabetIndexerLable.stories.tsx` |
| Pixso 链接 | https://pixso.cn/app/design/HA_e8I2mE7Oa0b5ZoeokSA?item-id=5317:20448 |
| MCP 工具来源 | `get_node_dsl` + `get_screenshot` + `design_to_code` + `get_all_components` |
| 变体树 JSON | `src/components/Views/AlphabetIndexerLable/alphabet-indexer-lable.json` |

## 组成与用途

字母索引标签组件，HarmonyOS COMPONENT_REGULAR 玻璃材质。两种形式：

- **Latin**: 圆形玻璃按钮 (56×56)，显示单个字母
- **cn**: 竖条中文索引 (66×178)，显示多个索引项

**导出项：**
- `AlphabetIndexerLable`
- `AlphabetIndexerLableProps`
- `AlphabetIndexerLableType`
- `CnIndexItem`
- `alphabetIndexerLableTypes`

## 量化规格

### 顶层变体

| 属性 | 可取值 |
|------|------|
| 类型 | `Latin` / `cn` |

### Latin

| 属性 | 值 | DSL 来源 |
|------|------|------|
| 可见尺寸 | `56 × 56px` | instance props |
| 圆角 | `28px` | cornerRadius: 28 |
| 内边距 | `12px` | autoLayout padding: 12 |
| 背景模糊 | `blur(40.77px)` | BACKGROUND_BLUR radius: 81.55 / 2 |
| 投影 | `0px 4px 16px rgba(0,0,0,0.102)` | DROP_SHADOW |
| 填充 | COMPONENT_REGULAR | inheritFillStyleID: 616:9110 |

### cn

| 属性 | 值 | DSL 来源 |
|------|------|------|
| 外层尺寸 | `66 × 178px` | width×height |
| 外层内边距 | `5px` | autoLayout padding: 5 |
| 面板尺寸 | `56 × 168px` | 推算 |
| 面板圆角 | `36px` | cornerRadius: 36 |
| 面板内边距 | `4px` | autoLayout padding: 4 |
| 面板项间距 | `8px` | autoLayout itemSpacing: 8 |
| 背景模糊 | `blur(15px)` | BACKGROUND_BLUR radius: 30 / 2 |

### Keyword 单项

| 属性 | 值 |
|------|------|
| 尺寸 | `48 × 48px` |
| 圆角 | `28px` |
| 内边距 | `8px` |
| 文字区 | `32 × 32px` |

### Typography

| 属性 | 值 |
|------|------|
| fontFamily | HarmonyHeiTi, HarmonyOS Sans SC, Geist Variable, sans-serif |
| fontSize | `24px` |
| fontWeight | `500` (Medium) |
| lineHeight | `32px` |
| letterSpacing | `0` |

### 色值

| 元素 | 取值 |
|------|------|
| 默认文字 | `--harmony-font-primary` |
| 激活文字 | `--harmony-font-emphasize` |
| 激活底 | `--harmony-comp-background-tertiary` |
| 表面填充 | `--COMPONENT_REGULAR_fill`，Light: `linear-gradient(rgba(255,255,255,0.6)) + rgba(255,255,255,0.102)` / Dark: `rgba(0,0,0,0.4)` |

## 状态

| 状态 | 适用 | 视觉效果 |
|------|------|------|
| enabled | Latin + cn 项 | 默认文字色，透明底 |
| activated | Latin + cn 项 | 蓝文字 (#0A59F7) + 灰色底 |

## Props

### DSL ↔ Prop 对照

| DSL 属性 | React Prop | 可取值 |
|------|------|------|
| `类型` | `类型` | `"Latin"` \| `"cn"` |
| `状态` | `CnIndexItem.状态` | `"enabled"` \| `"activated"` |

### 类型签名

```ts
interface AlphabetIndexerLableProps {
  类型?: "Latin" | "cn"
  value?: string
  items?: readonly CnIndexItem[]
  activeIndex?: number
  onItemSelect?: (item: CnIndexItem, index: number) => void
}
```

默认: `类型="Latin"`, `value="G"`

运行时约定：

- `value` 驱动 Latin 圆形标签的显示文字，页面滚动或索引选中时应传入当前索引值。
- `items` / `activeIndex` / `onItemSelect` 驱动 cn 竖条内容、选中态与点击交互。
- 不传运行时 props 时保持 Pixso 样本态，兼容既有页面与 Storybook 验收。

## Storybook

| Story | 说明 |
|------|------|
| `Playground` | Controls 切换类型 |
| `TypeGallery` | Latin + cn 并排对照 |
| `Default` | Latin |
| `Cn` | cn (含 activated 项) |
| `InteractiveCn` | cn 运行时交互示例 |

## 样式引用

- `--harmony-font-primary`
- `--harmony-font-emphasize`
- `--harmony-comp-background-tertiary`
- `--COMPONENT_REGULAR_fill`
