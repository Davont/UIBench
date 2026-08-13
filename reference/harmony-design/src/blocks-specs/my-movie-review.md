# my-movie-review — Block 规格文档

## Metadata

| 字段 | 值 |
|------|------|
| 实现目录 | `src/blocks/my-movie-review/` |
| stories 路径 | `src/blocks/my-movie-review/my-movie-review.stories.tsx` |
| Pixso 链接 | `https://pixso.cn/app/design/qrOa6NRNgGxLv4vptY_6Kw?item-id=43:8902` |
| item-id | `43:8902` |
| 变体树 JSON | `src/blocks/my-movie-review/my-movie-review.json` |
| MCP 工具来源 | `get_screenshot(guid="43:8902")`、`get_variants(guid="43:8902")`、`get_export_image(guid="43:8902")` 均 300s 超时；当前环境未暴露 `get_node_dsl`，按用户截图 + 仓库现有组件/资源手工量化实现 |

## 组成与用途

- **导出项**：`MyMovieReview`、`MyMovieReviewItem`、`MyMovieReviewProps`
- **用途**：视频/影视首页「欢迎你回来续看」横向滚动续看区块
- **复用组件**：`SubHeader`（标题 + 更多）、`Badge`（右上追看标签）
- **资源说明**：默认封面使用 `src/blocks/my-movie-review/assets/movie1.png`、`movie2.png`、`movie3.png`；组件通过 `影片列表[].封面图` 暴露替换入口

## 量化规格

| 元素 | 参数 | 值 |
|------|------|------|
| Root | Width | 360px |
| Root | Overflow | hidden |
| Page margin | Left/Right | 16px |
| SubHeader | 左侧类型 / 右侧类型 | `title` / `arrow` |
| Card | Width | 160px |
| Poster | Size | 160×90px |
| Poster | Radius | 8px |
| Card gap | Gap | 16px |
| Badge | Position | top 4px / right 4px |
| Badge | Size | 48×16px |
| Badge | Font | 10px / 700 / 14px |
| Badge | Radius | 0 6px 0 6px |
| Badge | Color | #ff7f0f / #ffffff |
| Title | Font | 16px / 500 / 22px |
| Description | Font | 13px / 400 / 18px |

## 默认内容

| Card | Title | Description | Badge |
|------|-------|-------------|-------|
| 1 | 沙丘2 | 经典年度科幻大作 | 您正在追 |
| 2 | 铁血战士狩猎 | 重磅归来！无敌英雄 | 您正在追 |
| 3 | 三体 | 外星文明入侵地球 | 您正在追 |

## Props — DSL ↔ Prop 对照

| 设计字段/节点 | Prop 名 | 类型 | 默认值 | 说明 |
|---------------|---------|------|--------|------|
| SubHeader 标题 | `标题` | ReactNode | "欢迎你回来续看" | 对应截图主标题 |
| SubHeader 右侧操作 | `操作文本` | string | "更多" | 传入 `SubHeader` 的 arrow 文案 |
| Card list | `影片列表` | MyMovieReviewItem[] | 3 条默认数据 | 横向滚动渲染 |
| Card title | `影片列表[].标题` | ReactNode | — | 卡片标题 |
| Card desc | `影片列表[].描述` | ReactNode | — | 卡片副标题 |
| Card image | `影片列表[].封面图` | string | — | 可替换为 Pixso 导出的前三张图 |
| Badge text | `影片列表[].追看标签` | string | "您正在追" / 空 | 有值时显示 Badge |
| Theme | `色彩模式` | "dark" / "light" | "dark" | 文字颜色 token 切换 |

## 样式引用

- 使用 `SubHeader`、`Badge` 组件原有 DOM 与行为；Block 仅通过局部 CSS 变量覆盖颜色、尺寸和位置。
- 使用 `cn()` 合并 className。
- 未新增 `global.css` token。

## 取舍说明

| 偏差 | 原因 | 影响 |
|------|------|------|
| 封面图改用本地 assets | 用户指定使用 `my-movie-review/assets` 下前三张图片 | 默认内容与 Storybook 示例一致 |
| 组件名统一为 `review` 拼写 | 用户指定命名为 `my-movie-review` | 目录、Storybook title、导出名均保持一致 |
