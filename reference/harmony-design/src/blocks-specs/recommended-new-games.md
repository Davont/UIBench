# Recommended New Games

## Metadata

| 字段 | 内容 |
| --- | --- |
| Block ID | `recommended-new-games` |
| Block 名称 | `Recommended New Games` |
| 实现目录 | `src/blocks/recommended-new-games/` |
| Stories 路径 | `src/blocks/recommended-new-games/recommended-new-games.stories.tsx` |
| Pixso 链接 | `https://pixso.cn/app/design/qrOa6NRNgGxLv4vptY_6Kw?item-id=38:7806` |
| Pixso item-id | `38:7806` |
| Pixso 节点名 | 组合 29629 |

## 组成与用途

- 导出项：`RecommendedNewGames`、`FeaturedGameItem`、`SmallGameItem`、`RecommendedNewGamesProps`
- 用途：游戏服务首页中的推荐新游区块，适合在深色沉浸页或浅色内容页中展示 1 个特色推荐游戏 + 2 个小游戏推荐。
- 结构：**SubHeader** 标题区（`左侧类型="2line"` + `右侧类型="arrow"`）+ 上方大特色卡片 328×328（背景图+模糊渐变蒙版+内容描述区+半透明底栏+Logo+标题分类+去玩按钮）+ 下方两张小卡片 160×248 并排（HM Symbol play icon 毛玻璃圆圈+Logo+标题分类+去玩按钮）。
- 复用组件：`SubHeader`（标题区）、`Badge`（游戏角标标签）、`HMSymbolIcon`（play_fill 播放图标）。
- 资产：使用 `src/blocks/recommended-new-games/assets/` 中的 3 组游戏背景图+Logo 图。

## 量化规格

| 项 | Pixso DSL 值 | 实现 |
| --- | --- | --- |
| 根尺寸 | `328 × auto` | `.recommended-new-games { width: 328px }` |
| 标题区 | SubHeader INSTANCE `左侧类型="2line"` + `右侧类型="arrow"` | 复用 SubHeader Component，CSS 裁剪为暗色主题 |
| 标题 | `推荐新游`，serif 24px Bold | CSS override: `font-family: serif; font-size: 24px; font-weight: 700` |
| 副标题 | `精选热门新游`，12px Medium | CSS override: `font-size: 12px; font-weight: 500; color: rgba(255,255,255,0.6)` |
| 大特色卡片 | `328 × 328` r=16 | `.recommended-new-games__featured { border-radius: 16px }` |
| 大特色背景图 | absolute inset=0 object-fit:cover | `img` absolute，`z-index: 0` |
| 大特色模糊渐变 | inset=0 backdrop-filter:blur(40px) | 全卡片覆盖，8-stop inline gradient |
| 大特色渐变颜色 | `#0B2417`（深绿） | `gradientColor` prop → `buildGradientOverlayStyle()` |
| 大特色半透明底栏 | 328×64, rgba(0,0,0,0.1) | `.recommended-new-games__featured-bottom-bar { height: 64px; background: rgba(0,0,0,0.1) }` |
| 大特色角标 | Badge Text，top=8 left=8 | `<Badge>` absolute，`z-index: 5` |
| 大特色内容描述区 | 容器 2, 304×63, bottom=68px left=12px | `.recommended-new-games__featured-content { bottom: 68px; left: 12px; width: 304px }` |
| 内容标签 | 14px w=400, rgba(255,255,255,0.9) | `.recommended-new-games__content-tag` |
| 内容标题 | 14px w=500 lh=27, rgba(255,255,255,0.9) | `.recommended-new-games__content-title` |
| 内容描述 | 14px w=400 lh=16, rgba(255,255,255,0.9) | `.recommended-new-games__content-description` (ellipsis) |
| 大特色 info row | 容器 3, 304×40, bottom=12px gap=12px | `.recommended-new-games__featured-info { bottom: 12px; flex row; gap: 12px }` |
| 大特色 Logo | 40×40, r=8 | `img` 40px，圆角 `8px`，`flex-shrink: 0` |
| 大特色标题/分类 | 标题 14px w=500 lh=21, 分类 14px w=400 lh=16 | `flex column; gap: 2px` |
| 去玩按钮 | 60×28, r=14, rgba(255,255,255,0.1) | `.recommended-new-games__play-btn` 自定义按钮 |
| 小卡片行 | flex row，gap 8px | `.recommended-new-games__small-grid { display: flex; gap: 8px }` |
| 小卡片 | `160 × 248` r=12 | `.recommended-new-games__small { border-radius: 12px }` |
| 小卡片1渐变颜色 | `#24140B` | `gradientColor="#24140B"` |
| 小卡片2渐变颜色 | `#0B2417` | `gradientColor="#0B2417"` |
| HM Symbol play icon | 36×36 毛玻璃圆圈+play_fill(24px) | `HMSymbolIcon name="play_fill"` + `.play-icon-circle` CSS |
| HM Symbol 圆圈毛玻璃 | blur radius=20→CSS 10px | `backdrop-filter: blur(10px)` |
| HM Symbol 圆圈描边 | gradient: rgba(255,255,255,0.2→0.05) | `background-clip: padding-box, border-box; border: 0.6px` |
| 小卡片 Logo | 40×40, bottom=12 left=12 r=8 | `img` absolute |
| 小卡片标题 | 12px w=500 lh=21 | `.recommended-new-games__small-title` |
| 小卡片分类 | 12px w=400 lh=16 | `.recommended-new-games__small-category` |
| 小卡片文字区 | absolute bottom=67px left=12px | `.recommended-new-games__small-copy { bottom: 67px }` |
| 小卡片去玩按钮 | bottom=18px right=12px | `.recommended-new-games__play-btn--small { bottom: 18px; right: 12px }` |

## Props

```ts
interface FeaturedGameItem {
  backgroundImage?: string
  logoImage?: string
  title?: ReactNode
  category?: ReactNode
  badgeText?: string
  badgeType?: "Dot" | "Text" | "Longest text"
  gradientColor?: string
  contentTag?: string
  contentTitle?: string
  contentDescription?: string
  buttonText?: string
}

interface SmallGameItem {
  backgroundImage?: string
  logoImage?: string
  title?: ReactNode
  category?: ReactNode
  badgeText?: string
  badgeType?: "Dot" | "Text" | "Longest text"
  gradientColor?: string
  buttonText?: string
  showPlayIcon?: boolean
}

interface RecommendedNewGamesProps extends Omit<HTMLAttributes<HTMLElement>, "title"> {
  标题?: ReactNode
  描述?: ReactNode
  更多标签?: string
  on更多点击?: () => void
  featuredGame?: FeaturedGameItem
  游戏列表?: SmallGameItem[]
  色彩模式?: "dark" | "light"
}
```

## 复用的 Component 资源

| Component | 用途 | 嵌套方式 |
| --- | --- | --- |
| **SubHeader** | 标题区 | `<SubHeader 左侧类型="2line" 右侧类型="arrow" />`，CSS 裁剪暗色主题 |
| **Badge** | 游戏角标 | `<Badge 类型="Text" count="新" />` |
| **HMSymbolIcon** | play_fill 播放图标 | `<HMSymbolIcon name="play_fill" size=24 />` 嵌套在毛玻璃圆圈容器中 |

## 取舍说明

- **新增 content description section**：Pixso DSL 容器 2 (304×63) 包含标签+标题+描述三层文字。
- **新增 "去玩" 按钮**：未复用 Button Component，因自定义样式（rgba(255,255,255,0.1) 填充+白文字）差异较大。
- **新增 HM Symbol play icon**：复用 `HMSymbolIcon`（name="play_fill"），外包毛玻璃圆圈（CSS backdrop-filter blur + gradient border）。
- **新增半透明底栏**：Featured card 底部 328×64 rgba(0,0,0,0.1)。
- **Corner radius**：DSL 原值 20px，实际使用 Featured 16px / Small 12px（视觉调优）。
- backdrop-filter blur: 40px（Pixso radius / 2）；HM Symbol 圆圈 blur: 10px（Pixso radius=20 / 2）。
