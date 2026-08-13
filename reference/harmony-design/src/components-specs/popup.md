# Popup 气泡弹出框

## Metadata

| 字段 | 值 |
|------|-----|
| 实现目录 | `src/components/Popup/` |
| stories 路径 | `src/components/Popup/Popup.stories.tsx` |
| 组件 JSON | `src/components/Popup/popup.json` |
| Pixso 链接 | `https://pixso.cn/app/design/HA_e8I2mE7Oa0b5ZoeokSA?item-id=5322:68` |
| item-id | `5322:68` |
| MCP 工具来源 | `get_node_dsl`（成功）；`get_export_image`（成功）；`get_variants`（返回空 `{}`）；`design_to_code`（CSS/TSX URL 过期，fallback DSL+截图） |

## 组件变体树 JSON

- 路径：`src/components/Popup/popup.json`
- 生成来源：`get_node_dsl` INSTANCE 节点名正则解析 + `pixComponentTreeDslNodes` 完整树
- `get_variants` 返回空 `{}`，`variantOptions` 从 12 个 INSTANCE `name` 字段重建（格式 `方向=X,箭头=Y`）

## 组成与用途

| 组件 | 文件 | 用途 |
|------|------|------|
| `Popup` | `popup.tsx` | 玻璃质感（Glass Morphism）气泡容器，带方向性箭头指示 |
| `PopupDirections` | `popup.tsx` | 方向枚举：`["Left", "Right", "Up", "Down"]` |
| `PopupArrowPositions` | `popup.tsx` | 箭头位置枚举：`["1", "2", "3"]` |

## 量化规格

### 容器
| 属性 | 值 | 来源 |
|------|-----|------|
| 默认尺寸 | 100×100px | DSL: INSTANCE width=100, height=100 |
| 圆角 | 20px（四角统一） | DSL: `rectangleTopLeftCornerRadius` 等 |
| 溢出 | `visible` | 箭头延伸至容器外 |

### 背景
| 属性 | 值 | 来源 |
|------|-----|------|
| 填充色 | `rgba(255, 255, 255, 0.9)` | Pixso style `616:9117` — `Light/Blur/COMPONENT_ULTRA_THICK` |
| 背景模糊 | `blur(40px)` | Pixso style `1:345` — `Light/Blur/COMPONENT_THICK`，radius=80 → CSS 除以 2 |

### 箭头三角
| 属性 | Left/Right 方向 | Up/Down 方向 |
|------|----------------|-------------|
| DSL 三角尺寸 | 9×16px | 16×9px |
| 实现方式 | 9×16px 元素 + `clip-path: polygon()` 三角 | 16×9px 元素 + `clip-path: polygon()` 三角 |
| 突出距离 | 9px（精确匹配 DSL） | 9px（精确匹配 DSL） |
| 沿边高度/宽度 | 16px（精确匹配 DSL） | 16px（精确匹配 DSL） |
| 材质 | `rgba(255,255,255,0.9)` + `blur(40px)` — 与背景完全相同 | 同左 |
| 箭头 1 位置 | 距起始边 24px | 同左 |
| 箭头 2 位置 | 居中（42px from top/left） | 同左 |
| 箭头 3 位置 | 距末尾边 24px | 同左 |

## 状态与交互

| 状态 | 说明 |
|------|------|
| default | 玻璃质感背景 + 箭头显示 |
| no-arrow | `arrow=false`，隐藏箭头，纯玻璃容器 |

> Pixso 设计稿中无 hover/active/disabled 等交互态，该组件为纯展示容器。

## Props

| Prop | 类型 | 默认值 | DSL 映射 |
|------|------|--------|----------|
| `方向` | `"Left" \| "Right" \| "Up" \| "Down"` | `"Up"` | DSL 变体属性 `方向`，可选值完全一致 |
| `箭头` | `"1" \| "2" \| "3"` | `"1"` | DSL 变体属性 `箭头`，可选值完全一致 |
| `arrow` | `boolean` | `true` | DSL `propDefMap.visible_72_1` name=`Arrow` defaultValue=`true` |
| `children` | `ReactNode` | — | 新增扩展（Pixso 设计稿无内容层） |
| `className` | `string` | — | 自定义类名 |

### DSL ↔ Prop 对照

| DSL 字段路径 | Prop 名 | 一致性 |
|-------------|---------|--------|
| INSTANCE `name` 中 `方向=X` | `方向` | ✅ 属性名与可选值集合完全一致 |
| INSTANCE `name` 中 `箭头=Y` | `箭头` | ✅ 属性名与可选值集合完全一致 |
| `propDefMap.visible_72_1` name="Arrow" | `arrow` | ✅ 语义与默认值一致 |

## 样式引用

| Token | 来源 | 用途 |
|-------|------|------|
| — | 组件内硬编码 | `rgba(255,255,255,0.9)` 与 `global.css` `--COMPONENT_ULTRA_THICK_fill` 值一致 |
| — | 组件内硬编码 | `blur(40px)` — 无现有全局 Token |
| — | 未新增全局 Token | 组件级样式均在 `popup.css` 内 |

## 取舍说明

| 项目 | 说明 |
|------|------|
| `design_to_code` CSS/TSX 过期 | URL 返回 Invalid，降级 DSL + 截图手工还原 |
| `get_variants` 返回空 | `variantOptions` 从 INSTANCE 名正则解析重建 |
| `get_screenshot` 图片格式不支持 | 降级 `get_export_image`（PNG 成功下载） |
| 组件内容层 | Pixso 中 Popup 变体仅有背景+箭头，添加 `children` 支持实际使用 |
| 默认尺寸 100×100 | DSL 中所有变体均为 100×100，允许 `className` 覆盖 |
| 组件用途变更 | 旧版 Popup（item-id=164:12624）为文本气泡卡片；新版（item-id=5322:68）为玻璃质感方向性弹出容器 |
