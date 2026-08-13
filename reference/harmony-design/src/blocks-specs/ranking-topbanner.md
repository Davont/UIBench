# 排行榜-头图 (RankingTopbanner)

## Metadata

| 字段 | 值 |
|------|-----|
| 实现目录 | `src/blocks/ranking-topbanner/` |
| Stories 路径 | `src/blocks/ranking-topbanner/ranking-topbanner.stories.tsx` |
| Storybook title | `Blocks/ranking-topbanner` |
| Pixso 链接 | `https://pixso.cn/app/design/poNuihoilaLFIwHQwxIlcQ?item-id=36:37010` |
| item-id | `36:37010` (#illustration_title 容器) · `36:37011` (icon_font 麦穗 "编组 6") · `36:37056` (综合排行榜) · `36:37057` (描述文字) · `59:497` (frame 头图容器) · `69:333` (TitleBar) |
| MCP 工具来源 | `query_nodes` (36:37010) ✅ · `get_screenshot` ✅ · `design_to_code` (59:497, 原始实现) ✅ |

## 组件变体树 JSON

- **路径**: `src/blocks/ranking-topbanner/ranking-topbanner.json`
- **生成方式**: `query_nodes` (guid: `69:225`) → #illustration_title 容器 221.25×63.45px + `get_screenshot` (69:225) 124KB PNG 真值截图
- **重建依据**: `query_nodes` 返回 69:226 为 `icon_font` "编组 6" (fill_container × 58.85px)，矢量分解为 69:227 (左麦穗) + 69:249 (右麦穗)

## 组成与用途

- **导出项**: `RankingTopbanner`（默认导出）、`RankingTopbannerProps`
- **用途**: 排行榜头图。360×237px 白色背景，含 StatusBar (Dark) + TitleBar (返回+右侧按钮) + 金色插图标题。
- **复用组件**: `StatusBar`、`TitleBar`
- **结构**: frame-59_497 → StatusBar + TitleBar + Illustration（金色标题 + 装饰矢量）

## 量化规格

### 容器 (DSL frame-59_497)
| 属性 | 值 | 来源 |
|------|-----|------|
| 尺寸 | 360 × 237px | DSL CSS |
| 背景色 | rgba(255, 255, 255, 1) | DSL fillPaints |

### StatusBar (DSL instance-69_273)
| 属性 | 值 | 来源 |
|------|-----|------|
| 尺寸 | 360 × 36px | DSL CSS |
| ColorMode | Dark | DSL prop |

### TitleBar (DSL instance-69_333)
| 属性 | 值 |
|------|-----|
| 尺寸 | 328 × 56px |
| 位置 | left=16px, top=36px |
| 类型 | secondary page-Phone |
| 返回按钮 | IconButton 40×40 + Chevronbackward 24×24 |
| 右侧按钮 | IconButton 40×40 + Ic (HM Symbol 24px) |
| 按钮圆角 | 1000px (pill) |

### 插图文字
| 元素 | DSL GUID | 字号 | 字重 | 行高 | 字间距 | 颜色 |
|------|----------|------|------|------|--------|------|
| 主标题 | 69:271 | 30px | 900 | 1.2 | 1px | rgba(224,175,137,1) |
| 描述 | 69:272 | 12px | 400 | 17px | 1px | rgba(224,175,137,1) × 0.6 |

### 装饰矢量 (Pixso 69:225 #illustration_title → 69:226 icon_font "编组 6")

| 属性 | 值 | 来源 |
|------|-----|------|
| 容器 | 221.25 × 63.45px | query_nodes 69:225 |
| 麦穗类型 | icon_font (fill_container × 58.85px) | query_nodes 69:226 |
| 渲染方式 | SVG 矢量对 (左 24×59 left=0 + 右 24×59 left=197) | design_to_code 分解 |
| 左矢量 | 24 × 59px, left=0, vector-left.svg | SVG 7 层麦穗矢量 |
| 右矢量 | 24 × 59px, left=197, vector-right.svg | SVG 7 层麦穗矢量 (镜像) |

## 状态与交互

| 状态 | 说明 |
|------|------|
| **default** | 白色头部 + StatusBar + TitleBar + 金色标题 |
| **返回按钮** | 点击触发 `on返回` |
| **右侧按钮** | 点击触发 `on右侧按钮点击` |

## Props

```typescript
interface RankingTopbannerProps {
  主标题?: string      // 默认"综合排行榜" (DSL paragraph-69_271)
  描述?: string        // 默认"- 根据榜单实时热度得出排名 -" (DSL paragraph-69_272)
  页面标题?: string    // TitleBar 标题 (DSL slot 2:60402)
  页面副标题?: string  // 默认"排行榜" (DSL slot 2:60403)
  on返回?: () => void
  on右侧按钮点击?: () => void
  className?: string
}
```

### DSL ↔ Prop 对照

| DSL 字段 | Prop 名 | 取值 | 一致性 |
|----------|---------|------|--------|
| paragraph-69_271 nodeText | `主标题` | "综合排行榜" | ✅ DSL 原始属性名直用 |
| paragraph-69_272 nodeText | `描述` | "- 根据榜单实时热度得出排名 -" | ✅ DSL 原始属性名直用 |
| slot 2:60402 | `页面标题` | "" | ✅ 映射自 DSL slot |
| slot 2:60403 | `页面副标题` | "排行榜" | ✅ 映射自 DSL slot |

## 样式引用

| 色值 | 用途 | DSL 来源 |
|------|------|----------|
| rgba(255, 255, 255, 1) | 头部背景 | DSL fillPaints |
| rgba(224, 175, 137, 1) | 金色标题/描述 | DSL color |
| rgba(224, 175, 137, 0.6) | 描述半透明 | DSL opacity 0.6 |

## MCP 调用清单

| 工具 | 状态 | 详情 |
|------|------|------|
| `query_nodes` | ✅ 成功 | guid=69:225, searchDepth=3, readDepth=3, 返回 #illustration_title + icon_font 麦穗 + 文字节点 |
| `get_screenshot` | ✅ 成功 | guid=69:225, 124KB PNG base64 真值截图 |
| `get_screenshot` | ✅ 成功 | guid=69:225 旧版 (原 59:497 设计参考) |
| `design_to_code` | ✅ 成功 | guid=59:497, framework=react, 产出 TSX+CSS (原始实现) |
| `get_node_dsl` | ❌ 超时 | guid=69:225 节点过大，降级使用 query_nodes |

## 取舍说明

1. **麦穗 icon_font → SVG 矢量**: Pixso `36:37011` 在 query_nodes 中为 `icon_font` "编组 6" (fill_container × 58.85px)，HM Symbol 字体中无可直接对应 221px 全幅麦穗装饰的单字符。`design_to_code` 解析为两个 24×59px SVG 矢量对，经 `get_screenshot` 验证为像素精确渲染，因此保留 SVG 实现。
2. **字体**: Pixso 36:37056/36:37057 指定 `fontFamily: "Source Han Serif CN"` (思源宋体)，`font-family` 顺序设为 `"Source Han Serif CN", "HarmonyHeiTi", ...`，`line-height: 1.47` (44px/30px)。
3. **布局**: 麦穗 absolute 底层 (z-index:0)，文字 relative 覆盖其上 (z-index:1)，容器 221×63px。
