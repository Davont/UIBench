# Top Banner

## Metadata

| 字段 | 内容 |
| --- | --- |
| Block ID | `top-banner` |
| Block 名称 | `Top Banner` |
| 实现目录 | `src/blocks/top-banner/` |
| Stories 路径 | `src/blocks/top-banner/top-banner.stories.tsx` |
| Pixso 链接 | `https://pixso.cn/app/design/KXylddm-EMqGBCzGr6ZZgQ?item-id=71:770` |
| Pixso item-id | `71:770` |
| Pixso 节点名 | `top banner` |

## 组成与用途

- 导出项：`TopBanner`、`TopBannerProps`
- 用途：阅读、书城、内容推荐页面的顶部沉浸式推荐 Banner。
- 结构：全幅山林背景 + 450px 蒙层 + 书封 + 标题 + 标签/描述 + 5 段式轮播指示条 + 进度条下方背景智能取渐变色。
- 复用组件：`Badge` 用于分类标签，`SwiperDot` 用于底部轮播进度。
- 资产：默认使用 `src/blocks/top-banner/assets/forest-background.png` 和 `src/assets/image/services/book8.png`。

## 量化规格

| 项 | Pixso DSL / codegen | 实现 |
| --- | --- | --- |
| 根布局尺寸 | `360 × 450` | `.top-banner { width: 360px; height: 450px; overflow: visible }`，允许下方渐变层露出 |
| 背景图 | `矩形`，`359 × 403`，原图 `1920 × 1080` | `.top-banner__media` 高 `403px`，cover 裁剪 |
| 背景智能取渐变色 | `.蒙层 / 实例 85`，top `450`，组件 props `360 × 160`；样式 `2:69649` / `取渐变色_青`，`rgba(21,51,45,1) -> rgba(21,51,45,0)` | `.top-banner__smart-gradient` 固定 `360 × 160`，从 `top: 450px` 开始显示在进度条下方；透明端不叠加白色底 |
| 蒙层 | `.蒙层`，`360 × 450.00003` | `.top-banner__veil` 固定 `360 × 450`，上下渐变叠加 |
| 信息区 | `360 × 272.6295`，top `189.3705` | 内容容器 left `16px`，top `232px` |
| 前景图 | `.前景图/4C`，主组件 `2:69556`，`328 × 118.8666` | `.top-banner__foreground { width: 328px; height: 118.87px }` |
| 书封 | 子图层 `4C` / `2:69670`，`164 × 118.8666`；导出图层 `2:69671`，`163.99995 × 118.97489` | 默认复用 `src/assets/image/services/book8.png`，按 `164 × 118.87` contain 显示 |
| 标题 | `南方有嘉木`，`328 × 44` | `30px / 44px`，单行省略 |
| 标签 | `文学`，组件内 `24 × 16` | 复用 `Badge`，覆盖为 `24px` 起步半透明白底 |
| 描述 | `三级阶梯顺序，呈现出荒原到人间的变化` | `14px / 19px`，单行省略 |
| 指示条 | 5 段，每段约 `62.4 × 2`，间距 `4px` | 复用 `SwiperDot`，在 block CSS 中覆写为段式进度 |

## Props

```ts
interface TopBannerProps extends Omit<HTMLAttributes<HTMLElement>, "title"> {
  标题?: ReactNode
  描述?: ReactNode
  标签?: ReactNode
  书封图片?: string
  背景图片?: string
  当前页?: number
  页数?: 2 | 3 | 4 | 5 | 6
  书名Alt?: string
}
```

## 复用边界

- 推荐用于 360px 移动端内容页首屏或顶部推荐位；根布局占位为 `360 × 450`，但底部渐变会继续向下延展 `160px`，承接后续页面内容背景。
- 适合 1 本主推书籍/内容的视觉推荐，不适合多卡片列表。
- `标题` 建议控制在 8 个中文字符以内；超出会单行省略。
- `描述` 建议控制在 20 个中文字符以内；超出会单行省略。
- `书封图片` 可替换；默认复用 services 资源 `book8.png`，组件内保留 `.前景图/4C` 的 `328 × 118.87` 外层尺寸，并按内部 `4C` 的 `164 × 118.87` contain 显示。
- `SwiperDot` 在此 block 内被覆写为线性分段样式，页面拼装时不要再把它当普通圆点样式嵌套进该区域。

## 取舍说明

- Pixso `get_variants` 返回 `{}`，节点没有变体树；实现提供内容和页数 props 作为复用参数。
- Pixso 内部标题、标签/描述、指示条均来自发布组件实例；仓库内没有同名组件真值，因此复用现有 `Badge` 与 `SwiperDot`，书封复用 `assets/image/services/book8.png`，其余只保留 block 级布局和图片资产。
- `.背景智能取渐变色` 和 `.蒙层` 节点已记录在 `top-banner.json`，避免后续 DSL 消费者只看到视觉 CSS 而丢失原始遮罩/取色渐变结构。
