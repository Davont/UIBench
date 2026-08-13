# NewBookPreview

## Metadata

| 字段 | 内容 |
| --- | --- |
| Block ID | `new-book-preview` |
| 实现目录 | `src/blocks/new-book-preview/` |
| Stories 路径 | `src/blocks/new-book-preview/new-book-preview.stories.tsx` |
| Pixso 链接 | `https://pixso.cn/app/design/KXylddm-EMqGBCzGr6ZZgQ?item-id=67:58045` |
| Pixso item-id | `67:58045` |
| MCP 工具 | `get_node_dsl` |

## 组成与用途

- 导出项：`NewBookPreview`、`NewBookPreviewProps`、`BookItem`
- 用途：移动端新书预览区块，适用于阅读/书店类 App 的新书推荐模块；自身不绘制底板，背景由页面或上层 Hero 渐变承接。
- 复用组件：无（自包含 Block）。
- 资产：
  - `src/assets/image/services/book2.png`：书籍封面（老人与海 / 百年孤独 等）
  - `src/assets/image/services/book3.png`：书籍封面（CLOD MOUN / 三体 等）
  - `src/assets/image/services/book4.png`：书籍封面（巨人的方法 / 活着 等）

## 量化规格

| 项 | Pixso DSL | 实现 |
| --- | --- | --- |
| 根尺寸 | Frame `422 × 198` | `max-width: 422px`，宽度自适应 |
| 背景 | Frame 无独立底板 | `background: transparent`，页面内透出上层 TopBanner 取色渐变或页面底色 |
| 标题栏高度 | `328 × 48`，left `0` | `.new-book-preview__header { width: min(328px, 100%); height: 48px; padding: 0 }` |
| 标题 | `新书速览`，Source Han Serif CN Bold 18px / 24px，色值 rgba(255,255,255,0.90) | `font-family: "Source Han Serif CN"; font-size: 18px; font-weight: 700; line-height: 24px; color: var(--harmony-font-on-primary)` |
| "更多"按钮 | HarmonyHeiTi Regular 14px / 19px，色值 rgba(255,255,255,0.60) + 箭头 SVG `6.74 × 12.81` | `font-size: 14px; font-weight: 400; color: var(--harmony-font-on-secondary)` + inline SVG 箭头 |
| 横向间距 | `book组` 之间间距 `15px`；4 组总宽约 `94 × 4 + 15 × 3 = 421px`，贴合 Frame `422px` | `.new-book-preview__scroller { padding: 0; gap: 15px }` |
| 书封尺寸 | `book/单本/3:4` 组件 `94 × 124.45` | `width: 94px; height: calc(94px * 4/3)` ≈ `125.33px` |
| 书封圆角 | `cornerRadius: 2` | `border-radius: 2px` |
| 书封阴影 | 3 层 DROP_SHADOW：上(0,-2,5,-2,0.14) + 左(-3,0,5,-2,0.18) + 右(3,0,5,-2,0.16) | `box-shadow: 0 -2px 5px -2px rgba(0,0,0,0.14), -3px 0 5px -2px rgba(0,0,0,0.18), 3px 0 5px -2px rgba(0,0,0,0.16)` |
| 底部阴影 | `底部阴影` 组件 `98 × 32`，top=115.89（叠封面底部 8.56px） | `position: absolute; top: 116px;` 32px 高，CSS gradient |
| 书名 | HarmonyHeiTi Regular 14px / 19px，色值 rgba(255,255,255,0.86) | `color: var(--harmony-font-on-primary)`，单行省略 |
| 封面→书名间距 | DSL 封面底 124.45 → 文字顶 132 = **7.55px** | `margin-top: 7px`（CSS 封面高 125.33，补偿差值） |
| 左对齐 | 标题、第一本书封、第一本书名均为 left `0` | block 内不加左右 padding；页面级边距由外层 slot 决定 |

## 状态与交互

- 默认：4 本书横向排列，超出视口可横向滑动。
- "更多"按钮：可选点击回调 `on更多点击`。
- 横向滚动：支持 touch scroll，隐藏滚动条（`scrollbar-width: none`）。
- 无 disabled / hover 状态的视觉变体（DSL 未暴露对应状态）。

## Props 与 DSL 对照

```ts
interface BookItem {
  coverImage?: string   // 封面图 URL
  title?: string        // 书名
}

interface NewBookPreviewProps extends Omit<HTMLAttributes<HTMLElement>, "title"> {
  标题?: ReactNode      // 默认 "新书速览"
  更多文本?: ReactNode   // 默认 "更多"
  on更多点击?: () => void // "更多"点击回调
  书籍列表?: BookItem[]   // 默认 4 本书
}
```

| DSL 字段 / 节点 | Prop | 默认值 | 说明 |
| --- | --- | --- | --- |
| text node `2:68950` | `标题` | `新书速览` | 标题文本 |
| right arrow text | `更多文本` | `更多` | 右侧操作文本 |
| `2:68956` image | `书籍列表[].coverImage` | book2/3/4.png | 书封图片 |
| text nodes `67:58089~92` | `书籍列表[].title` | DSL 文案 | 书名 |

## 样式引用

- 使用现有全局 Token：
  - `--harmony-font-on-primary`：标题 / 书名颜色
  - `--harmony-font-on-secondary`："更多"文本颜色
  - `--harmony-font-size-body-m`：书名 / "更多"字号
  - `--harmony-page-margin`：左右边距
- 未新增 `src/styles/global.css` Token。

## 取舍说明

- `get_variants` 返回空对象 `{}`，节点 `67:58045` 无组件变体。
- Pixso Remote MCP token 已失效，使用本地 Pixso Desktop MCP（`localhost:3667`）获取 DSL。
- 书封 `book/单本/3:4` 组件内嵌的 3 张 Pixso 原始图片不可直接使用，替换为项目已有 `src/assets/image/services/book2~4.png`。
- 底部阴影组件（`Component_2_68951`）原始实现为位图 + 蒙版，以 CSS `linear-gradient` 近似还原。
- 书脊纹理（`2:68957`）以 CSS semi-transparent overlay 模拟 3D 书脊效果。
- 背景处理：Frame 不生成独立黑色底板；放入 `services-home` 时需要透出 TopBanner 底部取色渐变，避免覆盖 Hero 与内容区的层叠关系。
