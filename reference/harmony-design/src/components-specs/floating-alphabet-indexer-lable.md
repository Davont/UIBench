# FloatingAlphabetIndexerLable 组件规格

## Metadata

| 字段 | 值 |
|------|------|
| 组件 ID | `floating-alphabet-indexer-lable` |
| 实现目录 | `src/components/Views/FloatingAlphabetIndexerLable/` |
| Stories 路径 | `src/components/Views/FloatingAlphabetIndexerLable/FloatingAlphabetIndexerLable.stories.tsx` |
| Pixso 链接 | https://pixso.cn/app/design/HA_e8I2mE7Oa0b5ZoeokSA?item-id=5317:20448 |
| MCP 工具来源 | `get_node_dsl` (成功) + `get_screenshot` (返回) + `design_to_code` (成功) + `get_all_components` (成功) |
| 变体树 JSON | `src/components/Views/FloatingAlphabetIndexerLable/floating-alphabet-indexer-lable.json` |

## 组成与用途

浮动字母索引标签组件，HarmonyOS 玻璃材质风格，用于字母/中文索引快速跳转。

- **Latin**: 圆形玻璃按钮 (56×56)，显示单个字母，支持点击跳转到对应字母区段
- **cn**: 竖条中文索引条 (66×178)，显示多个中文索引项，支持选中态切换

**导出项：**
- `FloatingAlphabetIndexerLable` — 主组件
- `FloatingAlphabetIndexerLableProps` — Props 类型
- `FloatingAlphabetIndexerLableType` — 类型枚举
- `FloatingAlphabetIndexerLableOpacity` — 通透度枚举
- `CnIndexItem` — cn 索引项类型
- `floatingAlphabetIndexerLableTypes` — 类型可选值常量
- `floatingAlphabetIndexerLableOpacities` — 通透度可选值常量

## 组件变体树 JSON

- 文件：`src/components/Views/FloatingAlphabetIndexerLable/floating-alphabet-indexer-lable.json`
- 生成依据：
  - `get_node_dsl` 当前选中节点 `5317:20448` (预览 FRAME)
  - `get_node_dsl` 内 `pixComponentTreeDslNodes` 含组件定义 `Latin` (1:9990) 和 `cn` (1:9978)
  - `get_all_components` 确认组件归属: `1.AlphabetIndexer - 索引条` → `类型=Latin` / `类型=cn`
  - `get_variants` 返回 `{}` (节点为 FRAME 非组件集)
  - 通透度完整变体集来自 Pixso 材质档位 (COMPONENT_REGULAR/THICK/THIN/ULTRA_THIN)

## 量化规格

### 顶层变体

| 属性 | 可取值 |
|------|------|
| 类型 | `Latin` / `cn` |
| 通透度 | `标准` / `强` / `降档` / `弱` |

### Latin (类型=Latin)

| 属性 | 值 | DSL 来源 |
|------|------|------|
| 可见主体尺寸 | `56 × 56px` | `5317:20446` instance props |
| 圆角 | `28px` | `cornerRadius: 28` |
| 内边距 | `12px` | `autoLayout.padding*: 12` |
| 字符尺寸框 | `32 × 32px` | Text `width×height` |
| 字号 | `24px` | `fontSize: 24` |
| 字重 | `500` (Medium) | `fontStyle: Medium` |
| 行高 | `32px` | text auto height |
| 字间距 | `0` | 默认 |
| 背景模糊 | `blur(40.77px)` | `BACKGROUND_BLUR radius: 81.55 / 2` |
| 投影 | `0px 4px 16px rgba(0,0,0,0.102)` | `DROP_SHADOW offset(0,4), radius:16` |
| 填充 | COMPONENT_REGULAR | `inheritFillStyleID: 616:9110` |
| 填充层1 | `rgba(255,255,255,0.102)` luminosity | `fillPaints[0]` |
| 填充层2 | `rgba(255,255,255,0.6)` normal | `fillPaints[1]` |

### cn (类型=cn)

| 属性 | 值 | DSL 来源 |
|------|------|------|
| 外层尺寸 | `66 × 178px` | `5317:20438` width×height |
| 外层内边距 | `5px` | `autoLayout.padding*: 5` |
| 内层面板尺寸 | `56 × 168px` | 推算: 66-10=56, 178-10=168 |
| 面板圆角 | `36px` | `画板 1 cornerRadius: 36` |
| 面板内边距 | `4px` | `autoLayout.padding*: 4` |
| 面板项间距 | `8px` | `autoLayout.itemSpacing: 8` |
| 背景模糊 | `blur(15px)` | `画板 1 BACKGROUND_BLUR radius: 30 / 2` |
| 投影 | 同 Latin | `有效效果合并` |
| 填充 | COMPONENT_REGULAR | 同 Latin `inheritFillStyleID` |

### Keyword 单项 (共用)

| 属性 | 值 | DSL 来源 |
|------|------|------|
| 尺寸 | `48 × 48px` | `27:34465/27:34464` width×height |
| 圆角 | `28px` | `cornerRadius: 28` |
| 内边距 | `8px` | `autoLayout.padding*: 8` |
| 文字区 | `32 × 32px` | Text width×height |

### Typography (全部文本)

| 属性 | 值 |
|------|------|
| fontFamily | `HarmonyHeiTi`, `HarmonyOS Sans SC`, `Geist Variable`, sans-serif |
| fontSize | `24px` |
| fontWeight | `500` (Medium) |
| lineHeight | `32px` |
| letterSpacing | `0` |
| textAlign | `center` |

### 色值与效果

| 元素 | 取值 | DSL 来源 |
|------|------|------|
| 默认文字 | `--harmony-font-primary` / `rgba(0,0,0,0.898039)` | `602:9446` Light/font_primary |
| 激活文字 | `--harmony-font-emphasize` / `rgba(10,89,247,1)` | `602:9440` Light/font_emphasize |
| 激活底 | `--harmony-comp-background-tertiary` / `rgba(0,0,0,0.047059)` | `602:9420` Light/comp_background_tertiary |
| 标准填充 | `linear-gradient(rgba(255,255,255,0.6)) + rgba(255,255,255,0.102)` | `616:9110` Light/Blur/COMPONENT_REGULAR |
| 强填充 | `linear-gradient(rgba(230,230,230,0.102)) + rgba(241,243,245,0.8)` | COMPONENT_THICK |
| 降档填充 | `linear-gradient(rgba(255,255,255,0.4)) + rgba(255,255,255,0.102)` | COMPONENT_THIN |
| 弱填充 | `linear-gradient(rgba(255,255,255,0.102)) + rgba(255,255,255,0.102)` | COMPONENT_ULTRA_THIN |

## 状态与交互

| 状态 | 适用 | 视觉效果 | DSL 来源 |
|------|------|------|------|
| enabled | Latin + cn 项 | 默认文字色 (font_primary)，透明底 | `27:34465` 状态=enabled |
| activated | Latin + cn 项 | 蓝文字 (font_emphasize) + 灰色底 (comp_background_tertiary) | `27:34464` 状态=activated |

> 注: DSL 中未定义 hover/focus/disabled 状态，当前实现仅覆盖 enabled 和 activated。

## Props

### DSL ↔ Prop 对照

| DSL 字段 / 路径 | React Prop | 可取值 | 说明 |
|-----------------|---------|--------|------|
| 组件变体 `类型` | `类型` | `"Latin"` \| `"cn"` | 直用 Pixso 原始属性名 |
| 材质属性 `通透度` | `通透度` | `"标准"` \| `"强"` \| `"降档"` \| `"弱"` | 直用 Pixso 原始属性名 |
| 子项 `状态` | `CnIndexItem.状态` | `"enabled"` \| `"activated"` | 直用 Pixso 原始属性名 |

### 类型签名

```ts
interface FloatingAlphabetIndexerLableProps
  extends Omit<ComponentPropsWithoutRef<"div">, "children"> {
  类型?: "Latin" | "cn"
  通透度?: "标准" | "强" | "降档" | "弱"
  value?: string
  items?: readonly CnIndexItem[]
  activeIndex?: number
  onItemSelect?: (item: CnIndexItem, index: number) => void
}

type CnIndexItem = {
  text: string
  状态?: "activated" | "enabled"
}
```

**默认值：** `类型="Latin"`, `通透度="标准"`, `value="G"`

运行时约定：

- `value` 驱动 Latin 圆形浮标的显示文字，页面滚动时应传入当前索引值。
- `items` / `activeIndex` / `onItemSelect` 驱动 cn 竖条内容、选中态与点击交互。
- 不传运行时 props 时保持 Pixso 样本态，兼容既有页面与 Storybook 验收。

## Storybook

| Story | 类型 | 说明 |
|------|------|------|
| `Playground` | 交互式 | 单实例 + Controls 切换 |
| `Matrix` | 全局变体预览 | 类型 × 通透度 全矩阵 (2×4 = 8 组合) |
| `Default` | 语义: Default | Latin × 标准 |
| `Cn` | 语义: Variant | cn × 标准 (含 activated 项) |
| `Strong` | 语义: Variant | Latin × 强 |
| `Weak` | 语义: Variant | cn × 弱 |

## 样式引用

### 使用的全局 Token

| Token | 用途 |
|------|------|
| `--harmony-font-primary` | 默认文字色 |
| `--harmony-font-emphasize` | 激活态文字色 |
| `--harmony-comp-background-tertiary` | 激活态底色 |

### 组件内局部变量 (CSS custom properties)

所有材质/效果参数通过 `--floating-indexer-*` 局部变量实现，详见 `floating-alphabet-indexer-lable.css`。不同通透度变体覆盖对应变量值。

### 本次未新增 `global.css` Token

当前稿面所需主色与激活底色均可映射到现有全局 token；不同通透度的材质层使用组件内局部 CSS 变量实现，未新增全局 `--*` 变量。

## 取舍说明

1. **`get_variants` 返回空**: 节点 `5317:20448` 为 FRAME 非组件集，变体树由 `get_node_dsl` 中的 `pixComponentTreeDslNodes` + `get_all_components` 重建。
2. **Latin vs cn 背景模糊值不同**: DSL 明确 Latin=`81.55px/2≈40.77px`, cn=`30px/2=15px`。上版本统一使用 `36px`，本版本已修正为差异化值。
3. **填充材质**: 上版本使用 FLOATING_THICK 系列值，本版本按 DSL `inheritFillStyleID: 616:9110` (Light/Blur/COMPONENT_REGULAR) 修正为标准填充。
4. **截图验证**: `get_screenshot` 返回了截图（格式不兼容无法直接观看），`design_to_code` 成功返回 code/css，用于交叉验证布局结构。视觉效果以 DSL 量化参数为准。
5. **cn 内容**: DSL 实例覆盖值为 `G`(activated) → `古` → `顾`，实现保持此顺序与内容不变。
