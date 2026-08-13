# Recommended New Books

## Metadata

| 字段 | 内容 |
| --- | --- |
| Block ID | `recommended-new-books` |
| Block 名称 | `Recommended New Books` |
| 实现目录 | `src/blocks/recommended-new-books/` |
| Stories 路径 | `src/blocks/recommended-new-books/recommended-new-books.stories.tsx` |
| Pixso 链接 | `https://pixso.cn/app/design/KXylddm-EMqGBCzGr6ZZgQ?item-id=67:56856` |
| Pixso item-id | `67:56856` |
| Pixso 节点名 | `#illustration_书海漫游备份 5` |

## 组成与用途

- 导出项：`RecommendedNewBooks`、`RecommendedNewBooksProps`、`RecommendedNewBooksItem`
- 用途：阅读/书城服务中的推荐新书区块，适合在深色沉浸页或浅色内容页中展示 3 本推荐书。
- 结构：标题区 + 右侧箭头入口 + 3 条纵向书籍列表。
- 资产：默认使用 `src/assets/image/services/book5.png`、`book6.png`、`book7.png` 作为 3:4 书封。

## 量化规格

| 项 | Pixso DSL / codegen | 实现 |
| --- | --- | --- |
| 根尺寸 | `328 × 372` | `.recommended-new-books { width: 328px; height: 372px }` |
| 标题区 | `328 × 72`，内容 left=12 top=15 | header 高 `72px`，左右 padding `12px` |
| 标题 | `新书强推`，Source Han Serif CN Bold `24px` | serif fallback，`24px / 32px`，`font-weight: 700` |
| 描述 | `最新品质好书等你来读！`，Body_S Medium `12px` | `12px / 16px`，距标题 `5px` |
| 右侧箭头 | `12 × 24`，left=304 top=30 | `button` 宽 `12px` 高 `24px`，同路径 SVG |
| 列表区 | `304 × 288`，left=12 top=80 | 3 行 flex column，每行 `304 × 96` |
| 书封组 | `51 × 79`，top=14 | cover stack `51 × 79` |
| 书封 | `51 × 68`，内部 3:4 书封组件缩放 | `51 × 68`，圆角 `2px`，3 层阴影 |
| 文本组 | width `211.7457`，left=63 top=19.5 | copy width `211.75px`，margin-left `12px`，margin-top `19.5px` |
| 书名 | Body_L Medium `16px` | `16px / 21px`，单行省略 |
| 作者 / 元信息 | Body_S Regular `12px` | `12px / 16px`，三级文字色 |
| 元信息间隔 | icon+rating、1px 分隔线、分类、人气 | flex row，gap `4px`，分隔线 `1 × 9px` |

## Props

```ts
interface RecommendedNewBooksItem {
  coverImage?: string
  title?: ReactNode
  author?: ReactNode
  rating?: ReactNode
  category?: ReactNode
  popularity?: ReactNode
}

interface RecommendedNewBooksProps extends Omit<HTMLAttributes<HTMLElement>, "title"> {
  标题?: ReactNode
  描述?: ReactNode
  更多标签?: string
  on更多点击?: () => void
  书籍列表?: RecommendedNewBooksItem[]
  色彩模式?: "dark" | "light"
}
```

## 复用边界

- 推荐用于固定 3 条纵向推荐书列表；超过 3 条时应抽为独立可滚动列表或页面级内容流。
- `色彩模式="dark"` 对齐 Pixso codegen 中的 Dark/font 样式，适合深色背景。
- `色彩模式="light"` 复用同一结构，仅切换文字和分隔线透明度，适合浅色页面。
- 书封图片应保持 3:4 内容比例；实现内按 `51 × 68` 容器裁剪。

## 取舍说明

- Pixso `get_variants` 返回 `{}`，该节点没有组件变体树。
- Pixso 根节点为 VECTOR 导出，DSL 同时暴露了内部 `list` 组件；实现按内部 `list` 的尺寸和文本层级重建为可复用 React Block。
- `book5~7` 由 Pixso codegen 临时导出的三张书封资源落盘到 `src/assets/image/services/`，避免依赖临时 localhost URL。
- 书封组件内的书脊纹理和底部阴影以 CSS overlay / gradient 复刻，不保留 Pixso 生成的临时蒙版位图。
