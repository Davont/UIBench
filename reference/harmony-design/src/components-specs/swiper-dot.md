# SwiperDot — 规格文档

## Metadata

| 字段 | 值 |
| --- | --- |
| 实现目录 | `src/components/SwiperDot/` |
| Stories 路径 | `src/components/SwiperDot/SwiperDot.stories.tsx` |
| Pixso 链接 | https://pixso.cn/app/design/HA_e8I2mE7Oa0b5ZoeokSA?item-id=5334:21976 |
| item-id | `5334:21976` |
| MCP 工具来源 | `get_node_dsl`（主真值）、`get_variants`（返回空 `{}`，降级从 DSL `name` 字段提取）、`get_screenshot`（base64 PNG） |

## 组件变体树 JSON

- 路径：`src/components/SwiperDot/swiper-dot.json`
- 生成依据：`get_node_dsl` 返回 `Swiper-Dot` 根节点 DSL，含 `pixTreeNodes` 和 `pixComponentTreeDslNodes`；`get_variants` 返回空，降级从 DSL 节点 `name` 字段解析出 `Multi Dot=OFF / ON / 带symbol`。
- 前置依赖：组件实现前已生成并作为变体真值使用。

## 组成与用途

`SwiperDot` 是非浮动的轮播圆点指示器，用于 Carousel / Swiper 组件底部，展示当前页位置。相比 `FloatingSwiperDotPhone`，无 material surface 层，无通透度变体。

导出项：
- `SwiperDot` — 默认组件
- `swiperDotTypes` — 类型常量 `["OFF", "ON", "带symbol"]`
- `swiperDotCounts` — 组数常量 `[2, 3, 4, 5, 6]`
- 类型：`SwiperDotProps`, `SwiperDotType`, `SwiperDotCount`

## 量化规格

### 圆点尺寸（来自 DSL 子组件）

| DSL 子组件名 | 尺寸 (W×H) | 圆角 | 颜色 | 对应 CSS 类 |
| --- | --- | --- | --- | --- |
| `状态=indicator,尺寸=Small` (8:36294) | 2×2 px | 4px | `rgba(0,0,0,0.098)` | `--small` |
| `状态=indicator,尺寸=medium` (8:36295) | 4×4 px | 4px | `rgba(0,0,0,0.098)` | `--medium` |
| `状态=defaults,尺寸=large` (8:35711) | 6×6 px | 4px | `rgba(0,0,0,0.098)` | `--large` |
| `状态=Active,尺寸=XL` (8:35710) | 12×6 px | 4px | `rgba(10,89,247,1)` | `--active` |

### 布局参数

| 参数 | 值 | 来源 |
| --- | --- | --- |
| 行容器高 | 32px | DSL `Multi Dot=OFF` 实例高度 |
| 行内 padding | 12px 上下 | DSL `autoLayoutPaddingTop/Bottom: 12` |
| 圆点间距 | 8px | DSL `autoLayoutItemSpacing: 8` |
| 多行间距 | ~19px（PixsoComparison 还原） | DSL 根节点内实例 top 差值 |
| Symbol 图标间距 | 10px 左边距 | DSL `Multi Dot=带symbol` 容器布局 |

### 字体（Symbol 图标）

| 属性 | 值 |
| --- | --- |
| fontFamily | HarmonyHeiTi |
| fontSize | 8px |
| fontWeight | 400 |
| lineHeight | 10px |
| 文本 | 󰘗 |
| 颜色 | `rgba(0,0,0,0.098)` |

### ON 模式圆点尺寸分布

固定 7 个圆点：`small(2×2) / medium(4×4) / large(6×6) / active(12×6) / large / medium / small`

## 状态与交互

| 状态 | 说明 |
| --- | --- |
| OFF | 所有非活跃圆点为 large(6×6)，活跃圆点为 active(12×6) |
| ON | 固定 7 圆点，尺寸对称渐变，中心为 active |
| 带symbol | 同 OFF + 右侧追加 HarmonyHeiTi 符号图标 |
| hover/active | 通过 `onIndexChange` 支持点击切换，无障碍 `aria-current` |

## Props

### 类型签名

```typescript
interface SwiperDotProps {
  "Multi Dot"?: "OFF" | "ON" | "带symbol"  // 默认 "OFF"
  组数?: 2 | 3 | 4 | 5 | 6                  // 默认 5
  活跃索引?: number                          // 0-based，默认居中
  onIndexChange?: (index: number) => void
}
```

### DSL ↔ Prop 对照

| DSL 字段/路径 | Prop 名 | 可取值 | 说明 |
| --- | --- | --- | --- |
| `Multi Dot`（根节点子实例 name 前缀） | `"Multi Dot"` | `"OFF"`, `"ON"`, `"带symbol"` | 直用 DSL 原始属性名 |
| `组数`（`pixComponentTreeDslNodes` 组件名，如 `组数=2`） | `组数` | `2, 3, 4, 5, 6` | OFF / 带symbol 下控制圆点数 |
| 活跃圆点索引（运行时状态） | `活跃索引` | `number` | 0-based，非 DSL 字段但为必要交互 |
| 点击回调（运行时交互） | `onIndexChange` | `(index: number) => void` | 非 DSL 字段但为必要交互 |

## 样式引用

### 使用的全局 Token（`global.css`）

| Token | 取值（light） | 取值（dark） | 用途 |
| --- | --- | --- | --- |
| `--harmony-comp-background-secondary` | `rgba(0,0,0,0.098)` | `rgba(255,255,255,0.098)` | 默认圆点填充色 |
| `--harmony-comp-background-emphasize` | `rgba(10,89,247,1)` | `rgba(49,122,247,1)` | 活跃圆点填充色 |

### 新增 Token

无。现有 Token 与稿面完全对齐。

## 取舍说明

- **无 `get_variants`**：返回空 `{}`，降级从 DSL `pixComponentTreeDslNodes[].name` 字段正则提取变体值（`Multi Dot=OFF` / `Multi Dot=ON` / `Multi Dot=带symbol`）。规格中已注明。
- **ON 模式圆点数固定 7**：从 DSL `Multi Dot=ON` → `.Pagintion` (8:36320) 下有 7 个子 `.indicator` 实例确认。
- **Symbol 图标文本**：DSL 中 `nodeText: 󰘗`（HarmonyHeiTi 私有区字符），直接复制到组件。
- **PixsoComparison 坐标**：按 DSL 根节点 `421×192` + 实例 `left:22, top:21.5/72.5/123.5` 精确还原。
