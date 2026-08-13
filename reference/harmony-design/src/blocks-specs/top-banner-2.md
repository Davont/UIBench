# Top Banner 2

## Metadata

| 字段 | 内容 |
| --- | --- |
| Block ID | `top-banner-2` |
| Block 名称 | `Top Banner 2` |
| 实现目录 | `src/blocks/top-banner-2/` |
| Stories 路径 | `src/blocks/top-banner-2/top-banner-2.stories.tsx` |
| Pixso 链接 | `https://pixso.cn/app/design/qrOa6NRNgGxLv4vptY_6Kw?item-id=38:2775` |
| Pixso item-id | `38:2775` |

## 组成与用途

- 导出项：`TopBanner2`、`TopBanner2Props`
- 用途：游戏、音乐、电影等内容推荐页面的顶部沉浸式推荐 Banner（简化版）。
- 结构：场景化全幅背景 + 450px 蒙层 + 前景 Logo + 标题 + 标签/描述 + 5 段式轮播指示条 + 进度条下方背景智能取渐变色。
- **与 top-banner 的区别**：前景区域展示 Logo/标题图，而不是书封卡片，其余结构与 top-banner 保持一致。
- 复用组件：`Badge` 用于分类标签，`SwiperDot` 用于底部轮播进度。
- 资产：内置 `game`、`music`、`movie` 三套场景素材，来自 `src/blocks/top-banner-2/assets/`。

## 量化规格

| 项 | Pixso DSL / codegen | 实现 |
| --- | --- | --- |
| 根布局尺寸 | `360 × 450` | `.top-banner-2 { width: 360px; height: 450px; overflow: visible }`，允许下方渐变层露出 |
| 背景图 | `359 × 403`，原图 `1920 × 1080` | `.top-banner-2__media` 高 `403px`，cover 裁剪 |
| 背景智能取渐变色 | `360 × 160`；`rgba(21,51,45,1) -> rgba(21,51,45,0)` | `.top-banner-2__smart-gradient` 固定 `360 × 160`，从 `top: 450px` 开始显示 |
| 蒙层 | `360 × 450` | `.top-banner-2__veil` 固定 `360 × 450`，上下渐变叠加 |
| 信息区 | `328px` 宽，left `16px` | game top `284px`；music top `132px`；movie top `96px` |
| 前景 Logo | 场景化图片 | game `164×118.87px`；music `222×88px`；movie `198×74px` |
| 标题 | `30px / 44px`，单行省略 | `font-size: 30px; line-height: 44px` |
| 标签 | `Badge` 组件，`24px` 起步半透明白底 | 复用 `Badge` |
| 描述 | `14px / 19px`，单行省略 | `font-size: 14px; line-height: 19px` |
| 指示条 | 5 段，每段约 `62.4 × 2`，间距 `4px` | 复用 `SwiperDot` |

## Props

```ts
interface TopBanner2Props extends Omit<HTMLAttributes<HTMLElement>, "title"> {
  场景?: "game" | "music" | "movie"
  标题?: ReactNode
  描述?: ReactNode
  标签?: ReactNode
  背景图片?: string
  Logo图片?: string
  智能渐变色?: string
  当前页?: number
  页数?: 2 | 3 | 4 | 5 | 6
}
```

## 场景预设

| 场景 | 标题 | 标签 | 描述 | 背景 | 前景 |
| --- | --- | --- | --- | --- | --- |
| `game` | — | 动画 | 奇幻色彩龙佑之邦，人类和龙和谐生活在一起 | `game-background.png` | `game-foreground.png` |
| `music` | — | 专题 | 第66届格莱美音乐奖大预测 | `music-background.png` | `music-foreground.png` |
| `movie` | — | 悬疑 | 双雄对峙，白夜真相再度浮现 | `movie- background.png` | `movie-foreground.png` |

## 复用边界

- 推荐用于 360px 移动端内容页首屏或顶部推荐位；根布局占位为 `360 × 450`，但底部渐变会继续向下延展 `160px`。
- 适合不需要突出展示书籍封面的简化 Banner 场景（游戏、音乐、影视推荐等）。
- `标题` 建议控制在 8 个中文字符以内；超出会单行省略。
- `描述` 建议控制在 20 个中文字符以内；超出会单行省略；可以为空（不显示）。
- `SwiperDot` 在此 block 内被覆写为线性分段样式。

## 与 top-banner 的结构对比

| 结构元素 | top-banner | top-banner-2 |
| --- | --- | --- |
| 背景图 `__media` | ✅ | ✅ |
| 背景智能取渐变色 `__smart-gradient` | ✅ | ✅ |
| 蒙层 `__veil` | ✅ | ✅ |
| 超级线条 `__super-line` | ✅ | ✅ |
| 内容容器 `__content` | ✅ | ✅ |
| 前景图包装 `__foreground` | ✅ | ✅（Logo/标题图） |
| 书封包装 `__book-wrap` | ✅ | ❌ |
| 书封图片 `__book-cover` | ✅ | ❌ |
| 标题 `__title` | ✅ | ✅ |
| 标签 + 描述 `__meta` | ✅ | ✅ |
| 轮播指示条 `__indicator` | ✅ | ✅ |

## 取舍说明

- **降级实现**：由于 Pixso MCP 连接失败（No valid session ID），本 Block 基于：
  - 用户提供的截图和描述
  - 现有 `top-banner` Block 结构
  - 使用 `top-banner-2/assets` 中的 game/music/movie 素材，保留 Badge 与 SwiperDot 复用
- 未执行自动 DSL 比对，建议后续 MCP 可用时进行视觉回归验证。
