# Size

## Metadata

- **实现目录**: `src/components/Size/`
- **Stories 路径**: `src/components/Size/Size.stories.tsx`
- **变体树 JSON**: `src/components/Size/size.json`
- **Pixso 链接**:
  - Size-Phone: `https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5311:19582`
  - Size-Tablet: `https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5316:19975`
  - Size-Foldable: `https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5316:19575`

## 组成与用途

- **导出**: `SizePhone`、`SizeTablet`、`SizeFoldable` 三个独立组件（从单 `Size` 的 `类型` 维度拆分得到，对外建议使用三者而非旧 dispatcher）；保留 dispatcher `Size`（向后兼容，按 `类型` 路由到对应 wrapper）；常量 `sizeTypes`（`["Phone", "Tablet", "Foldable"]`），`landOptions`（`["OFF", "ON"]`）
- **组成**: `StatusBar`（顶部，Light 模式）+ 空白内容区 + `Aibottombar`（底部，Light 模式）
- **用途**: 设备外框占位组件，分别对应 Phone / Tablet / Foldable 三种设备尺寸

## 量化规格

### Phone (类型="Phone")

| 属性 | 竖屏 (Land=OFF) | 横屏 (Land=ON) |
|------|----------------|----------------|
| 宽 × 高 | 360 × 792 px | 792 × 360 px |

### Tablet (类型="Tablet")

| 属性 | 竖屏 (Land=OFF) | 横屏 (Land=ON) |
|------|----------------|----------------|
| 宽 × 高 | 800 × 1280 px | 1280 × 800 px |

### Foldable (类型="Foldable")

| 属性 | 值 |
|------|-----|
| 宽 × 高 | 740 × 834 px |

### 通用

| 属性 | 值 |
|------|-----|
| 背景色 | `var(--harmony-background-secondary)` (#F1F3F5) |
| 布局 | Flex column, `space-between` |
| StatusBar 高度 | 36 px（组件自适应） |
| Aibottombar 高度 | 28 px（组件自适应） |
| 溢出 | `overflow: hidden` |

## Props

### 拆分后的独立组件

| 组件 | Props | 默认值 | 说明 |
|------|-------|--------|------|
| `SizePhone` | `Land?: "OFF" \| "ON"` | `"OFF"` | 手机外框（360×792 / 792×360） |
| `SizeTablet` | `Land?: "OFF" \| "ON"` | `"OFF"` | 平板外框（800×1280 / 1280×800） |
| `SizeFoldable` | （无） | — | 折叠屏外框（740×834，无 Land 维度） |

三者均透传 `HTMLAttributes<HTMLDivElement>`，可传 `className`、`children`、`style` 等。

### 兼容性 dispatcher `Size`

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `类型` | `"Phone" \| "Tablet" \| "Foldable"` | `"Phone"` | 设备形态（按此路由到对应 wrapper） |
| `Land` | `"OFF" \| "ON"` | `"OFF"` | 控制 Phone / Tablet 方向（Foldable 忽略） |

> 新代码建议直接使用 `SizePhone` / `SizeTablet` / `SizeFoldable`，而非通过 `类型` 切换。

### DSL ↔ 属性对照

| DSL 字段 | 对应组件 / Prop | 取值集合 | 说明 |
|----------|----------------|----------|------|
| `Size-Phone` 子树 | `SizePhone` / `Land` | `"OFF"`, `"ON"` | Pixso 设备外框 `5311:19582`，竖屏/横屏切换 |
| `Size-Tablet` 子树 | `SizeTablet` / `Land` | `"OFF"`, `"ON"` | Pixso 设备外框 `5316:19975`，竖屏/横屏切换 |
| `Size-Foldable` 子树 | `SizeFoldable` | — | Pixso 设备外框 `5316:19575`，固定 740×834 |

## 样式引用

| 变量 | 用途 |
|------|------|
| `--harmony-background-secondary` | 设备外框背景色 (#F1F3F5) |

无新增全局 Token。

## 取舍说明

| 项目 | 说明 |
|------|------|
| 三组件再拆分 | 原 `Phone` / `Foldable` / `SizeTablet` 曾合并为统一 `Size`，现沿用 TextInput/Slider 拆分范式，按设备形态拆为 `SizePhone` / `SizeTablet` / `SizeFoldable` 三个独立导出组件；保留 `Size` dispatcher 仅作向后兼容 |
| `get_variants` 返回空 | 各子树的变体轴均基于 `get_node_dsl` 子帧结构重建，详见 `size.json` 中 `_mcp_evidence` |
| Foldable 无 Land 轴 | DSL 仅包含单个 740×834 画板，`SizeFoldable` 不暴露 `Land` |
