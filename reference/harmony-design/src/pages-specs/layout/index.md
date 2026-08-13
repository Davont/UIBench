# Layout Index

> 布局索引：page_type -> layout markdown

## Available Layouts


| page_type             | layout file              | description                                                 |
| --------------------- | ------------------------ | ----------------------------------------------------------- |
| page-shell            | page-shell.md            | 通用移动端手机壳层 — 必须使用 MobilePhoneShellTemplatePage 作为根壳层，业务内容作为 children 填入 |
| service-search        | service-search.md        | 云服务应用搜索页 — 固定顶部搜索壳层，支持搜索前 history/ranking rail 与搜索中 result-list/在线搜索/MiniPlayer 两种组合 |
| services-home         | services-home.md         | 云服务业务首页 — 默认 TopBanner Hero + 分类胶囊 + 新书/推荐内容 slot + 底部浮动导航 |
| services-me           | services-me.md           | 云服务个人中心页（我的页面）— 身份卡片 + 快捷操作 + 反馈卡片 + 常用服务宫格 + 公共区列表 + 底部导航 |
| mobile-card           | mobile-card.md           | 移动端内容卡片页 — 多卡片类型垂直堆叠 + section header 分区管理 |
| mobile-grid           | mobile-grid.md           | 移动端宫格首页/发现页 — 水平滚动宫格卡片 + 多区域混合编排        |
| mobile-list           | mobile-list.md           | 移动端入口型列表页 — appicon + title + aux / value + chevron |
| mobile-settings       | mobile-settings.md       | 喝水设置页面 - 设置项列表与开关控制                                         |
| settings-context-list | settings-context-list.md | 情景模式 / 显示与亮度 / 云空间 / 智慧多窗 - 顶部业务卡片（轮播/预览/容量环）+ 下方 list 卡片组合 |
| poi-detail            | poi-detail.md            | POI 详情页 — Hero 图 + AI 摘要 + 精选笔记与联动入口 |
| photo-album           | photo-album.md           | 相册页 — 2 列图片网格 + 上传区域 |
| panorama              | panorama.md              | 全景图页 — 暗色全屏图片展示 |
| video                 | video.md                 | 视频页 — 暗色播放器壳子 + 进度条 + 控制栏 |


## Page Templates


| template                     | layout family         | template file            | source block                                          | description                 |
| ---------------------------- | --------------------- | ------------------------ | ----------------------------------------------------- | --------------------------- |
| mobile-phone-shell-template  | page-shell            | page-shell.md            | src/pages/mobile-phone-shell-template/mobile-phone-shell-template.tsx | 通用手机壳层实体模板；命中 page-shell 时必须作为页面根壳层使用 |
| service-search-template      | service-search        | service-search.md        | src/pages/service-search-template/service-search-template.tsx | 云服务搜索页通用模板，默认映射 MusicSearchHistory 与 TopSongs；spec 已定义搜索中结果列表组合 slot |
| services-home-template       | services-home         | services-home.md         | src/pages/services-home-template/services-home-template.tsx | 云服务首页模板，默认 Hero 使用 top-banner，并提供 Hero / NewBookPreview / RecommendedNewBooks 三个业务内容 slot |
| services-me                  | services-me           | services-me.md           | src/pages/services-me/ServicesMePage.tsx                    | 云服务个人中心页，身份卡片 + 快捷操作 + 反馈卡片 + 常用服务 + 列表卡片 + 底部 Tab |
| settings-page                | mobile-settings       | settings-page.md         | src/pages/settings-page-template/settings-page-template.tsx | 通用系统设置页模板，多组设置卡片           |
| mobile-card-template         | mobile-card           | mobile-card.md           | src/pages/mobile-card-template/mobile-card-template.tsx     | 多卡片类型垂直堆叠内容页通用模板 |
| mobile-grid-template         | mobile-grid           | mobile-grid.md           | src/pages/mobile-grid-template/mobile-grid-template.tsx     | 宫格首页/发现页通用模板       |
| mobile-list-template         | mobile-list           | mobile-list.md           | src/pages/mobile-list-template/mobile-list-template.tsx     | 入口型列表页通用模板           |

## Layout Supplements

| supplement | source | description |
| ---------- | ------ | ----------- |
| floating-sheet-semi-modal | `src/blocks-specs/floating-sheet-semi-modal.md` | 半模态面板：FloatingBindSheet，左右与底部完全贴边，无视口边距 |


## Layout Structure

每个 layout markdown 必须包含：

- `hit_rules` - 命中规则
- `exclusion_rules` - 排除规则
- `reference_blocks` - 参考区块
- `layout_skeleton` - 布局骨架
- `needed_components` - 需要的组件
- `composition_mapping` - 组合映射
- `spatial_tokens` - 间距/尺寸 token（新增）
- `shell_rules` - 壳层规则（新增）
- `stacking_context` - z-index 与堆叠上下文约束（新增）
- `adaptive_behavior` - 自适应行为（新增）
- `semantic_tokens` / `semantic token usage` - 语义 token
- `generation_constraints` - 生成约束
- `validation_notes` - 验证笔记
- `source` - 原始 reference 链接（Pixso source node + canvas）

## Token Note

- Harmony layout 相关样式统一引用 `src/styles/global.css`
- 运行时 CSS 变量命名空间统一为 `--harmony-*`
- 模板 CSS 不依赖 Tailwind utility class；margin/padding 直接以 px 表达
