# today-movie-list — Block 规格文档

## Metadata

| 字段 | 值 |
|------|------|
| 实现目录 | `src/blocks/today-movie-list/` |
| stories 路径 | `src/blocks/today-movie-list/today-movie-list.stories.tsx` |
| Pixso 链接 | `https://pixso.cn/app/design/qrOa6NRNgGxLv4vptY_6Kw?item-id=47:12` |
| item-id | `47:12` |
| 变体树 JSON | `src/blocks/today-movie-list/today-movie-list.json` |
| MCP 工具来源 | 本轮可用 MCP：`get_screenshot(guid="47:12")`、`get_variants(guid="47:12")`、`get_export_image(guid="47:12")`、`get_screenshot(guid="62:29")` 均 300s 超时；当前环境未暴露 `get_node_dsl`，沿用既有 DSL 量化记录 + 用户截图手工复核 |

## 组成与用途

- **导出项**：`TodayMovieList`、`MovieListItem`、`TodayMovieListProps`
- **用途**：影音/影视场景的「今日热播大片」推荐列表；SubHeader 单行标题区 + 1×N 宫格影片卡片
- **复用组件**：SubHeader（标题区）、Badge（信息角标）
- **复用资源**：电影封面图来自 `src/blocks/today-movie-list/assets/movie1.png`、`movie2.png`、`movie3.png`

## 量化规格

### 根容器 (1xNgrids控件)

| 参数 | 值 | 来源 |
|------|------|------|
| Width | 360px | DSL root |
| Height | 233px | DSL root |
| Background | transparent | DSL fillPaints rgba(255,255,255,0) visible=false |

### SubHeader-Phone

| 参数 | 值 | 来源 |
|------|------|------|
| Width | 328px | DSL child[1] |
| Height | 72px | DSL child[1] |
| Position | top | Auto-layout |
| Left align | 16px | 与三张卡片左边缘对齐 |

### 宫格区域 (画板 83)

| 参数 | 值 | 来源 |
|------|------|------|
| Width | 360px | DSL child[0] |
| Height | 185px | DSL child[0] |
| Left margin | 16px | DSL: cell[2].left=16 |
| Right margin | 16px | Calculated: 240+104+16=360 |
| Card gap | 8px | DSL: cell positions 16→128→240, diff=128-16-104=8 |

### 单个影片卡片 (.宫格)

| 参数 | 值 | 来源 |
|------|------|------|
| Width | 104px | DSL |
| Height | 185px | DSL 185.034546 |
| Poster (画板 9) | 104×144px, r=8 | DSL |
| Text area (14r+12r) | 104×37px | DSL |

### Typography

| 元素 | Font Size | Weight | Line Height | Max Lines | Color | Pixso Style ID |
|------|-----------|--------|-------------|-----------|-------|------|
| Title | 14px | 400 | 19px | 2 | rgba(255,255,255,0.898039) | inheritTextStyleID=2:59747 |
| Description | 12px | 400 | 16px | 1 | rgba(255,255,255,0.4) | inheritTextStyleID=2:60338 |
| Badge/右下标签 | 10px | 500 | 14px | — | rgba(255,255,255,1) | 参考 `62:29` 截图 |

### DSL 实际文本样本

| Card | Title | Description | Badge |
|------|-------|-------------|-------|
| Cell[2] (left=16) | 有罪之身 | 魏大勋以身入局 | 更新至34集 |
| Cell[1] (left=128) | 罚罪2 | 黄景瑜正邪对决 | 24集全 |
| Cell[0] (left=240) | 生命树 | 边境生命守护者 | 30集全 |

## 状态与交互

- default: 深色主题三列宫格展示
- hover: 无 Pixso hover 状态（静态展示 Block）
- 色彩模式: dark / light（CSS custom properties 双主题）

## Props — DSL ↔ Prop 对照

| DSL 属性/节点 | Prop 名 | 类型 | 默认值 | 取值集合 | 映射说明 |
|---------------|---------|------|--------|----------|----------|
| SubHeader-Phone → 标题 | `标题` | ReactNode | "今日热播大片" | 任意字符串 | SubHeader 标题字段 |
| SubHeader-Phone → 副标题 | `描述` | ReactNode | "" | 任意字符串 | 本截图为单行标题结构，不展示副标题 |
| SubHeader-Phone → 操作文本 | `操作文本` | string | "更多" | 任意字符串 | SubHeader 操作文本 |
| SubHeader-Phone → 左/右侧类型 | 固定=`title` + `arrow` | — | — | — | Block 级固定，不暴露为 Prop |
| .宫格[数量] | `影片列表` | MovieListItem[] | 3 条默认数据 | 1~3 条 | DSL 3 条 → 默认 3，运行时截取前 3 条保持 360px 三列画板 |
| Title nodeText | `MovieListItem.标题` | ReactNode | — | 任意字符串 | 对齐 DSL Title 字段 |
| Description nodeText | `MovieListItem.描述` | ReactNode | — | 任意字符串 | 对齐 DSL Description 字段 |
| 实例 8/12/4 | `MovieListItem.封面图` | string | `movie1.png` / `movie2.png` / `movie3.png` | URL/path | 对齐 DSL image instance；本轮按用户指定替换为本 Block assets |
| .信息标签/.右下标签 nodeText | `MovieListItem.角标文本` | string | "更新至34集"/"24集全"/"30集全" | 任意字符串 | 截图要求每张电影卡片均显示标签 |
| .信息标签类型 | `MovieListItem.角标类型` | enum | "none" | episode/vip/rating/none | DSL .信息标签 → Badge 类型映射 |
| Root fillPaints (暗色) | `色彩模式` | enum | "dark" | dark/light | DSL 暗色为默认，light 为反向映射 |

## 样式引用

### 使用的 global.css / src/styles 变量

| 变量名 | 用途 | 对应 DSL |
|--------|------|----------|
| `--harmony-font-primary` | Title 文字色 dark 模式 | rgba(255,255,255,0.898039) |
| `--harmony-font-secondary` | SubHeader 操作文字色 | rgba(255,255,255,0.6) |
| `--harmony-font-tertiary` | Description 文字色 | rgba(255,255,255,0.4) |
| `--harmony-font-size-subtitle-l` | SubHeader 标题字号参考 | 18px |
| `--harmony-font-size-subtitle-s` | SubHeader 副标题字号参考 | 14px |
| `--harmony-page-margin` | 宫格左右边距 | 16px |

### Block 局部 CSS 变量（新增，未写入 global.css）

| 变量名 | 取值 | Pixso 来源 | 适用范围 |
|--------|------|------------|----------|
| `--tml-title-font-size` | 14px | DSL Title fontSize | 本 Block |
| `--tml-title-font-weight` | 400 | DSL Title fontWeight | 本 Block |
| `--tml-title-line-height` | 19px | DSL Title height | 本 Block |
| `--tml-desc-font-size` | 12px | DSL Description fontSize | 本 Block |
| `--tml-desc-font-weight` | 400 | DSL Description fontWeight | 本 Block |
| `--tml-desc-line-height` | 16px | DSL Description height | 本 Block |
| `--tml-poster-radius` | 8px | DSL 画板 9 cornerRadius | 本 Block |
| `--tml-badge-bg` | rgba(0,0,0,0.3) | `62:29` 截图右下半透明胶囊标签 | 本 Block |
| `--tml-badge-text-color` | rgba(255,255,255,1) | DSL badge nodeText fill | 本 Block |
| `--badge-radius` | 6px 2px 6px 2px | 用户标注：左上 6、右上 2、左下 2、右下 6 | 本 Block 覆盖 Badge |

> 这些变量值均与已有 global.css Token 可等价映射（primary/secondary/tertiary 对应关系明确），但 Block 内局部变量提供了更精确的 DSL 对齐控制，不会污染全局。

## 取舍说明

| 偏差 | 原因 | 影响 |
|------|------|------|
| 截图未取得 | 本轮 `get_screenshot`、`get_variants`、`get_export_image` 均 300s 超时；当前可用 Pixso MCP 未暴露 `get_node_dsl` | 1:1 对照依赖既有 DSL 量化参数 + 本地封面资源人工复核 |
| Badge 类型映射 | DSL .信息标签含 .右下标签(集数) 和 VIP/评分等，映射为 Prop `角标类型` | 可表达 DSL 中所有信息标签变体 |
| 宫格固定 3 卡 | Pixso 节点为 360px 宽三列画板，本轮仅替换三张卡片封面 | 传入超过 3 条时运行时截取前三条，保证画板对齐 |
| SubHeader 左侧类型固定 | 截图为单行大标题 + 右侧 arrow，不暴露为 Prop | 如果需要 2line/select 变体，用户需自行嵌套 SubHeader |
