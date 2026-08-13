# QRCode

## Metadata

| 字段 | 值 |
|------|------|
| 实现目录 | `src/components/QRCode/` |
| Stories 路径 | `src/components/QRCode/QRCode.stories.tsx` |
| Pixso 链接 | https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5413:349 |
| MCP 工具来源 | `get_node_dsl`（`get_variants` 返回空，降级为 DSL 节点名解析） |

## 组件变体树 JSON

- 路径：`src/components/QRCode/qrcode.json`
- 生成方式：`get_variants` 返回 `{}`，降级从 `get_node_dsl` 的 `pixTreeNodes` 子节点名（`类型=X,状态=Y`）解析变体属性与取值。
- `variantOptions`：`类型` → `["Routine", "Avatar", "Icon", "Default"]`；`状态` → `["Default", "Error", "Loading"]`

## 组成与用途

| 导出项 | 用途 |
|--------|------|
| `QRCode` | 主组件 |
| `qrCodeTypes` | `类型` 可选值常量数组 |
| `qrCodeStates` | `状态` 可选值常量数组 |

适用场景：展示二维码（纯码/带头像/带图标），支持正常/过期刷新/加载中三种状态。

## 量化规格

| 参数 | 值 | 来源 |
|------|-----|------|
| 容器尺寸 | 240×240 px | DSL `width`/`height` |
| 容器圆角 | 12px | DSL `cornerRadius` |
| 容器背景 | `#FFFFFF`（`Light/comp_background_primary`） | DSL `inheritFillStyleID: 602:9417` |
| 二维码区域 | 206×206 px，距左上角 (17, 17) | DSL `qr code 2` GROUP 坐标 |
| 二维码前景色 | `#000000`（`Light/comp_foreground_primary`） | DSL `inheritFillStyleID: 602:9425` |
| 头像占位 | 56×56 px，圆形（`border-radius: 50%`），居中 | DSL `椭圆 1` VECTOR（类型=Avatar） |
| 图标占位 | 56×56 px，圆角 14px，居中 | DSL `矩形 2` GROUP（类型=Icon） |
| 刷新图标 | 24×24 px，HM Symbol `󰃇` | DSL `.refresh` INSTANCE（状态=Error） |
| 过期文案 | 16px HarmonyHeiTi Medium | DSL `18fp center` PARAGRAPH（状态=Error） |
| 加载动画 | 40×40 px，居中 | DSL `ProgressBar-Loading-Phone` INSTANCE（状态=Loading） |
| Error/Loading 二维码透明度 | `opacity: 0.1` | DSL `qr code 2` GROUP `opacity` |

## 状态与交互

| 状态 | 表现 |
|------|------|
| **Default** | 完整显示二维码；Avatar/Icon 类型叠加居中覆盖层 |
| **Error** | 二维码 10% 透明度 + 居中刷新图标 + "The QR code has expired, click refresh" |
| **Loading** | 二维码 10% 透明度 + 居中旋转加载动画 |

## Props

| Prop | 类型 | 默认值 | DSL 对应 | 说明 |
|------|------|--------|----------|------|
| `类型` | `"Routine" \| "Avatar" \| "Icon" \| "Default"` | `"Routine"` | `pixTreeNodes[].name` 中 `类型=` | 二维码类型 |
| `状态` | `"Default" \| "Error" \| "Loading"` | `"Default"` | `pixTreeNodes[].name` 中 `状态=` | 二维码状态 |
| `avatarSrc` | `string`（可选） | `src/assets/image/avatar.png` | 功能扩展 | Avatar 类型头像图片 URL |
| `iconSrc` | `string`（可选） | `src/assets/image/appicon.png` | 功能扩展 | Icon 类型图标图片 URL |
| `errorText` | `string` | `"The QR code has expired, click refresh"` | DSL `nodeText`（状态=Error） | 过期提示文案 |
| `onRefresh` | `() => void`（可选） | — | 功能扩展 | 点击刷新回调 |
| `className` | `string`（可选） | — | — | 额外 CSS 类名 |

### DSL ↔ Prop 对照

| DSL 字段路径 / 键名 | Prop 名 | 可取值的集合是否一致 | 备注 |
|---------------------|---------|---------------------|------|
| `pixTreeNodes[].name` 中 `类型=` | `类型` | ✅ 一致 | Pixso 原始属性名，直用 |
| `pixTreeNodes[].name` 中 `状态=` | `状态` | ✅ 一致 | Pixso 原始属性名，直用 |
| `状态=Error` 中 `nodeText` | `errorText` | ✅ 一致 | 默认值与 DSL 文案一致 |
| — | `avatarSrc` / `iconSrc` | N/A | 功能扩展：DSL 中头像/图标为静态嵌入资源 |
| — | `defaultAvatarImg` / `defaultIconImg`（内部 import） | N/A | Avatar/Icon 图片资源来自 Pixso 导出，存放于 `src/assets/image/` |

## 样式引用

### 使用的 global.css Token

| Token | 用途 | 是否新增 |
|-------|------|----------|
| `--harmony-comp-background-primary` | 容器背景、SVG 二维码背景 | ❌ 已有 |
| `--harmony-comp-foreground-primary` | SVG 二维码模块色、默认头像/图标填充 | ❌ 已有 |
| `--harmony-font-primary` | 过期文案颜色 | ❌ 已有 |
| `--harmony-icon-primary` | 刷新图标颜色 | ❌ 已有 |
| `--harmony-icon-secondary` | 加载动画弧线颜色 | ❌ 已有 |

### 新增 Token

无。所有设计 Token 均与已有 `global.css` 变量对齐。

## 取舍说明

1. **QR 码来源**：Pixso DSL 中 QR 码原为静态嵌入图片（`type: IMAGE`，hash `qrcode`）。当前实现已从原图无损提取 21×21 模块矩阵，并由内联 SVG `<path>` 绘制；背景和模块分别使用 `--harmony-comp-background-primary` 与 `--harmony-comp-foreground-primary`，不再依赖 `qr-code.png`，可正确响应深浅色 Token。
2. **HM Symbol 字体**：刷新图标的 Pixso `nodeText` 为 `󰃇`（U+F00C7），映射到本地 `HMSymbolIcon name="arrow_clockwise"`，由 `HMSymbolVF.ttf` 渲染，不依赖系统字体。
3. **`get_variants` 返回空**：降级从 `get_node_dsl` 的 `pixTreeNodes` 子节点名解析变体属性，未遗漏维度。
4. **降级设计真值**：`design_to_code` CSS 资源 URL 已过期（`Invalid batch timestamp`），样式参数完全基于 `get_node_dsl` DSL + `get_screenshot` 截图交叉验证。
