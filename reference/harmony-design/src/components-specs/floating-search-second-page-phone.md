# FloatingSearchSecondPagePhone 组件规格

## Metadata

| 字段 | 值 |
|------|-----|
| 实现目录 | `src/components/FloatingSearchSecondPagePhone` |
| Stories 路径 | `src/components/FloatingSearchSecondPagePhone/FloatingSearchSecondPagePhone.stories.tsx` |
| Pixso 链接 | `https://pixso.cn/app/design/HA_e8I2mE7Oa0b5ZoeokSA?item-id=5400:101` |
| MCP 工具 | `get_node_dsl`、`get_screenshot`、`get_variants`、`design_to_code` |
| 变体树 JSON | `src/components/FloatingSearchSecondPagePhone/floating-search-second-page-phone.json` |
| 变体树来源 | `get_variants` 返回 `{}`，改由 `get_node_dsl` 顶层 4 个实例名称重建 |

## 组成与用途

`FloatingSearchSecondPagePhone` 对应 Pixso 中的第二页浮动搜索组件家族，默认呈现搜索中态的单行 phone search entry。

- 导出：`FloatingSearchSecondPagePhone`、`floatingSearchSecondPagePhoneOpacityOptions`
- 使用场景：地图/搜索类二级页面顶部搜索入口，展示返回、搜索输入和取景扫描动作

## 量化规格

| 参数 | 值 |
|------|-----|
| 整体宽高 | `328 × 40` |
| 外层布局 | `40 + 8 + 232 + 8 + 40` |
| 左右按钮 | `40 × 40`，圆角 `999px` |
| 搜索面板 | `232 × 40`，圆角 `24px` |
| 搜索面板 padding | `8 / 12 / 8 / 12` |
| 搜索图标 | `16 × 16` |
| 文本 | `Music`，`16px / 400 / 22px / letterSpacing 0` |
| 光标 | `1.5 × 24`，品牌蓝 |
| 清除图标 | `18 × 18` |
| 画板展示 frame | `405 × 290`，行距 `20px`，左侧偏移 `39px`，顶部偏移 `29px` |

## 状态与交互

当前节点为静态展示态，未暴露 hover / pressed / focus 的顶层组件变体。

- 左侧返回按钮：默认态
- 中间搜索框：输入中态，显示 `Music` 与光标
- 右侧扫描按钮：默认态

## Props

### DSL ↔ Prop 对照表

| DSL 字段 | Prop 名 | 类型 | 默认值 | 取值集合 | 一致性 |
|----------|---------|------|--------|----------|--------|
| 通透度 | 通透度 | `"标准" \| "强" \| "降档" \| "弱"` | `"标准"` | `["标准", "强", "降档", "弱"]` | ✅ 完全一致 |
| — | 文本 | `string` | `"Music"` | — | 额外 prop，对应当前节点默认文案 |
| 页面槽位显隐 | 显示扫描 | `boolean` | `true` | `true / false` | 页面复用扩展，默认保持组件集原貌 |
| 页面槽位显隐 | 显示清除 | `boolean` | `true` | `true / false` | 页面复用扩展，默认保持组件集原貌 |
| 页面槽位显隐 | 显示光标 | `boolean` | `true` | `true / false` | 页面复用扩展，默认保持组件集原貌 |
| 页面槽位语义 | 占位 | `boolean` | `false` | `true / false` | 页面复用扩展，用于 ServiceSearch 搜索前占位态 |

## 样式引用

### global.css Token

| Token | 用途 |
|-------|------|
| `--Floating_background_weak_fill` | 标准/弱搜索面板与弱态按钮背景 |
| `--Material_background_THIN_fill` | 强态背景 |
| `--comp_background_color_floating_smooth_fill` | 降档背景 |
| `--Floating_background_line_fill` | 降档描边 |
| `--harmony-font-primary` | 搜索文本 |
| `--harmony-icon-primary` | 左右按钮图标 |
| `--harmony-icon-secondary` | 搜索/清除图标 |
| `--harmony-brand` | 光标颜色 |

### 新增全局 Token

无新增。

## 取舍说明

1. `get_variants` 返回空对象，因此组件变体树由顶层 frame 的 4 个子实例名称重建。
2. `design_to_code` 返回 500，未作为实现依据。
3. 额外对 `5400:1`、`5400:26`、`5400:51`、`5400:76` 做了 `get_node_dsl`，但 Pixso 对内部实例的展开存在截断，因此强/降档/弱的细节最终以顶层截图和已解析样式 token 共同校准。
4. 三张单行补充截图请求超时，最终视觉对照基于 `5400:101` 整体截图与 `5400:1` 单行截图完成人工复核。
5. ServiceSearch page type 的 Pixso 节点 `36:45118` 已重新调用 Pixso MCP：`get_screenshot` 成功，`get_node_dsl` 成功，`design_to_code(react)` 返回 500，`get_variants` 返回 `{}`。顶部搜索实例 `36:45187` 为 `SearchSecondPagePhone`，坐标 `left=16 top=36 width=328 height=40`，实例属性为 `Left icon=true`、`Right icon=false`。页面复用该组件时使用 `显示扫描=false`、`显示清除=false`、`显示光标=false`、`占位=true`，保持左返回按钮 + 280px 搜索面板的 `328 × 40` 搜索区。
