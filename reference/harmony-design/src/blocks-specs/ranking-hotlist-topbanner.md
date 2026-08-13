# ranking-hotlist-topbanner

## Metadata

| 属性 | 值 |
|------|------|
| 实现目录 | `src/blocks/ranking-hotlist-topbanner/` |
| Stories 路径 | `src/blocks/ranking-hotlist-topbanner/ranking-hotlist-topbanner.stories.tsx` |
| 组件 JSON | `src/blocks/ranking-hotlist-topbanner/ranking-hotlist-topbanner.json` |
| Pixso 链接 | `https://pixso.cn/app/design/poNuihoilaLFIwHQwxIlcQ?item-id=49:33` |
| item-id | `49:33` |
| MCP 工具来源 | `design_to_code` (成功) + `get_node_dsl` (降级 — 返回错误缓存节点) |

## 组分 JSON 变体树

- **路径**: `src/blocks/ranking-hotlist-topbanner/ranking-hotlist-topbanner.json`
- **MCP 调用**: `design_to_code` (guid: `49:33`) 
- **get_variants**: 不可用
- **重建依据**: `design_to_code` 提供完整 HTML/CSS 结构。`get_node_dsl` 对 49:33 返回不相关缓存节点 (48:57265)，变体树从 `design_to_code` HTML DOM 结构手工重建。

## 组成与用途

**导出项**: `RankingHotlistTopbanner`

**使用场景**: 排行榜头图卡片（单头图模式）。360×244px 紫色渐变背景 + 可替换头图照片，含标题栏（单按钮）+ 居中大字标题区（HOT LIST 标签 + 热播榜主标题 + 描述文字）。适用于各类排行榜的顶部视觉卡片。

**结构**: 49:33 Frame → 37:56407 头图组 → { 37:56408 背景组, 37:56472 标题栏, 37:56483 文本覆盖区 }

## 量化规格

### 整体
- 容器尺寸: **360×244px**
- overflow: hidden

### 背景 (Pixso 37:56410)
- 尺寸: 360×244px
- 渐变层 1 (紫色): 105deg, `rgba(75,93,157,1)` → `rgba(162,99,132,1)` 36% → `rgba(132,87,140,1)` 73% → `rgba(91,46,89,1)` 100%
- 渐变层 2 (暗色叠加): 138.5deg, `rgba(0,0,0,0.2)` → `rgba(0,0,0,0.25)`
- blend-mode: color-burn, normal

### 头图照片 (Pixso 37:56412)
- 尺寸: 1144×600px
- 位置: left=-392px, top=-150px (居中裁切于 360×244 视口内)
- object-fit: cover

### 暗色文字遮罩
- 渐变: 180deg, `rgba(0,0,0,0.3)` 0% → `rgba(0,0,0,0)` 40% → `rgba(0,0,0,0.4)` 100%

### 标题栏 / 返回按钮 (Pixso 49:87)
- 按钮尺寸: **40×40px**
- 位置: left=16px, top=36px
- 图标: HM Symbol 24px Regular, `rgba(255,255,255,0.898)` (dark/icon_primary)
- 图标字符: `󰣒` (HM Symbol 返回箭头)
- 图标在按钮内偏移: left=8px, top=8px（居中于 40×40 容器）
- 背景: 透明
- hover: opacity 0.7

### 文本覆盖区 (Pixso 37:56483)
- 尺寸: 163×86px
- 位置: 水平居中 (left=98.5px), top=100px

| 元素 | Pixso GUID | 文字 | 字号 | 字重 | 颜色 | CSS 类 |
|------|-----------|------|------|------|------|--------|
| 标签 | 37:56486 | HOT LIST | 12px | Bold (700) | rgba(255,255,255,0.4) | `fill-darkfont_tertiary` + `text-fontbody_sbold` |
| 主标题 | 37:56485 | 热播榜 | 38px | Bold (700) | rgba(255,255,255,1) | `fill-lightfont_on_primary` + `text-fontdisplay_sbold` |
| 描述 | 37:56484 | - 根据榜单实时热度得出排名 - | 12px | Regular (400) | rgba(255,255,255,0.4) | `fill-darkfont_tertiary` + `text-fontbody_sregular` |

### 文本间距
- 标签 → 主标题: **0px** (标签 bottom ≈16px, 主标题 top=16px)
- 主标题 → 描述: **16px** (主标题 bottom ≈54px, 描述 top=70px)

### 字体

| 元素 | 字体族 | 字重 | 字号 | 行高 | Token |
|------|--------|------|------|------|-------|
| 标签 | HarmonyHeiTi | Bold (700) | 12px | 16px | `--harmony-font-size-body-s` |
| 主标题 | HarmonyHeiTi | Bold (700) | 38px | 1 | `--harmony-font-size-display-s` |
| 描述 | HarmonyHeiTi | Regular (400) | 12px | 16px | `--harmony-font-size-body-s` |

## 状态与交互

| 状态 | 说明 |
|------|------|
| Default | 默认展示，渐变背景 + 文本覆盖 |
| With Image | 头图照片叠加在渐变背景之上 |
| Hover (按钮) | 更多按钮 opacity 降低至 0.7 |

## Props

| Prop | 类型 | 默认值 | DSL 对齐 | 说明 |
|------|------|--------|-------------|------|
| 主标题 | `string` | — | `37:56485` nodeText="热播榜" | 居中大字主标题 |
| 标签 | `string` | — | `37:56486` nodeText="HOT LIST" | 顶部小标签 |
| 描述 | `string` | — | `37:56484` nodeText="- 根据榜单实时热度得出排名 -" | 底部描述文字 |
| 头图 | `string` | — | `37:56412` IMAGE fill | 背景头图 URL |
| on返回 | `() => void` | — | — | 返回按钮点击回调 |
| className | `string` | `""` | — | 外层容器类名 |

## 样式引用

### 使用 global.css 变量
- `--harmony-font-size-display-s` (38px)
- `--harmony-font-size-subtitle-m` (16px)
- `--harmony-font-size-body-s` (12px)
- `--harmony-font-weight-body-s` (400)

### 新增 Token
无新增 Token。暗色文字颜色在暗色背景下硬编码（白色系），不随全局亮/暗主题切换。

## 取舍说明

1. **`get_node_dsl` 降级**: Pixso MCP `get_node_dsl` 对节点 49:33 及其子节点 37:56472 均返回不相关的缓存节点 `48:57265`（文字 "001 古怪的国王和聪明的王后"），疑为 Pixso 插件缓存 bug。`design_to_code` 提供完整 HTML/CSS 结构作为降级真值。
2. **单按钮设计**: 标题栏仅保留右侧"更多"按钮（40×40px），无返回按钮。与同源 `hot-chart-card`（双按钮）不同。
3. **无状态栏**: 与 `hot-chart-card` 不同，此设计不含 iOS 状态栏（时间/信号/电池）。
4. **渐变还原**: 紫色渐变精确复制自 `design_to_code` SVG linearGradient 色值和角度。
5. **图片定位**: 头图照片使用与 Pixso 一致的绝对定位坐标 (-392, -150)，确保裁切区域一致。
