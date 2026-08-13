# music-recommended — Block 规格文档

## Metadata

| 字段 | 值 |
|------|------|
| 实现目录 | `src/blocks/music-recommended/` |
| stories 路径 | `src/blocks/music-recommended/music-recommended.stories.tsx` |
| Pixso 链接 | `https://pixso.cn/app/design/qrOa6NRNgGxLv4vptY_6Kw?item-id=43:9393` |
| item-id | `43:9393` |
| 变体树 JSON | `src/blocks/music-recommended/music-recommended.json` |
| 资源目录 | `src/blocks/music-recommended/assets/` |
| MCP 工具来源 | 当前环境仅暴露 `get_local_styles`，未暴露 Pixso 节点 DSL/截图导出工具；按用户截图 + 本地 assets 手工量化实现 |

## 组成与用途

- **导出项**：`MusicRecommended`、`MusicRecommendedItem`、`MusicRecommendedProps`
- **用途**：音乐首页「Hi Raven，为你推荐」横向推荐区块
- **复用组件**：`SubHeader`（标题 + 右箭头）
- **资源说明**：默认封面使用 `music1.png`、`music2.png`、`music3.png`；播放图标使用 `ic_play_24.png`

## 量化规格

| 元素 | 参数 | 值 |
|------|------|------|
| Root | Size | 428×243px |
| Root | Background | #171713 |
| Root | Top padding | 27px |
| Page margin | Left | 10px |
| SubHeader | Size | 328×24px |
| SubHeader | 左侧类型 / 右侧类型 | `title` / `arrow` |
| SubHeader title | Font | 18px / 700 / 24px |
| Card list | Top gap | 9px |
| Card | Size | 130×153px |
| Card gap | Gap | 9px |
| Cover | Size | 130×130px |
| Cover | Radius | 6px |
| Play info | Position | left 4px / bottom 4px |
| Play info | Gap | 2px |
| Play icon | Display size | 24×24px |
| Heat text | Font | 10px / 400 / 14px |
| Card title | Font | 13px / 400 / 18px |

## 默认内容

| Card | Cover | Title | Heat |
|------|-------|-------|------|
| 1 | `music1.png` | 暗夜歌剧心跳 | 257W |
| 2 | `music2.png` | 贝多芬黑胶馆 | 257W |
| 3 | `music3.png` | 舒伯特浪漫集 | 257W |

## Props — DSL ↔ Prop 对照

| 设计字段/节点 | Prop 名 | 类型 | 默认值 | 说明 |
|---------------|---------|------|--------|------|
| SubHeader 标题 | `标题` | string | "Hi Raven，为你推荐" | 对应截图主标题 |
| SubHeader 右侧箭头 | `on更多点击` | () => void | — | 传入 SubHeader 的 action |
| Card list | `推荐列表` | MusicRecommendedItem[] | 3 条默认数据 | 横向滚动渲染 |
| Card cover | `推荐列表[].封面图` | string | — | 专辑封面图 |
| Card title | `推荐列表[].标题` | ReactNode | — | 卡片下方标题 |
| Play count | `推荐列表[].热度` | ReactNode | "257W" | 播放 icon 后的热度文本 |
| Theme | `色彩模式` | "dark" / "light" | "dark" | 背景和文字颜色 token 切换 |

## 样式引用

- 复用 `SubHeader` 组件原有 DOM 与行为；Block 局部覆盖尺寸、上下 padding、箭头文本隐藏。
- 使用 `cn()` 合并 className。
- 未新增 `global.css` token。

## 取舍说明

| 偏差 | 原因 | 影响 |
|------|------|------|
| 未执行自动 DSL 比对 | 当前 Pixso MCP 未暴露节点 DSL/截图导出工具 | 依据用户截图与本地素材手工量化 |
| 专辑卡片未抽为全局 Component | 现有 `Card` 会带固定容器尺寸和默认装饰按钮，不匹配封面卡片 | 在 Block 内保留语义化 `article`，顶部仍复用 `SubHeader` |
