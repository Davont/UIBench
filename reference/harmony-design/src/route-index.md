# Route Index

> 页面类型路由：prompt / Figma 意图 -> page_type -> layout path

## Page Types


| page_type             | layout                          | hit_rules                                                | exclusion_rules                                          |
| --------------------- | ------------------------------- | -------------------------------------------------------- | -------------------------------------------------------- |
| service-search        | layout/service-search.md        | "ServiceSearch" / "servicessearch" / "服务搜索" / "云服务搜索" / "搜索页" / "视频搜索" / "应用市场搜索" / "音乐搜索" / "游戏搜索" / "主题搜索" / "阅读搜索" / "云空间搜索" / "查找搜索" / "浏览器搜索" / "搜索历史" / "搜索中" / "搜索结果" / "搜索结果页" / "搜索完成" / "搜索完成态" / "completed-results" / "综合" / "分类胶囊" / "歌手卡片" / "多歌手多卡" / "播放全部" / "在线搜索" / "搜索列表" / "热搜榜" / "新歌榜" / "SearchSecondPage" | "首页" / "服务首页" / "设置" / "详情页" / "纯列表" / "后台管理" |
| services-categories   | layout/services-categories.md   | "Categories" / "筛选" / "分类" / "全部" / "视频分类" / "电影分类" / "服务分类" / "FilterChip" / "评分筛选" / "年份筛选" / "地区筛选" / "MovieCard" | "首页" / "设置" / "详情页" / "后台管理" / "播放器" / "沉浸式Banner" |
| services-home         | layout/services-home.md         | "云服务首页" / "服务首页" / "Services Home" / "阅读首页" / "书城首页" / "视频首页" / "音乐厅首页" / "游戏首页" / "游戏库首页" / "应用市场首页" / "主题首页" / "云空间首页" / "浏览器首页" / "top banner" / "TopBanner" / "top-banner-2" / "TopBanner2" / "南方有嘉木" / "新书速览" / "新书强推" / "我的游戏" / "MyGameReview" / "my-game-review" / "新游情报局" / "RecommendedNewGames" / "recommended-new-games" / "Hi Raven，为你推荐" / "music-recommended" / "MusicRecommended" / "欢迎你回来续看" / "my-movie-review" / "MyMovieReview" / "today-movie-list" / "今日热播大片" | "设置" / "详情页" / "纯列表" / "后台管理" / "表单" |
| services-launch-page  | layout/services-launch-page.md  | "Launch" / "Splash" / "权限启动" / "隐私协议" / "首次启动" / "应用授权" / "同意/取消" / "华为视频" / "启动页" / "闪屏" | "设置" / "登录" / "注册" / "手机号验证" / "多步注册" |
| services-me           | layout/services-me.md           | "Services Me" / "服务个人中心" / "用户中心" / "身份卡片" / "IdentityCard" / "用户资产" / "常用服务" / "公共区列表" / "个人主页" | "设置" / "详情页" / "纯卡片流" / "无身份卡片" / "沉浸式Banner" |
| services-ranking      | layout/services-ranking.md      | "Ranking" / "排行榜" / "榜单" / "视频排行" / "音乐排行" / "热度榜" / "电影榜" / "电视剧榜" / "综合榜" / "MainChart03" / "主榜" / "麦穗" / "ChipsTab" | "设置" / "详情页" / "无排名列表" / "无头图" |
| services-setting      | layout/services-setting.md      | "Service Setting" / "服务设置" / "应用设置" / "Bottom Sheet 设置" / "数据和隐私" / "第三方SDK" / "服务模式" / "应用服务模式" | "系统设置" / "喝水设置" / "显示与亮度" / "情景模式" / "云空间" |
| mobile-card           | layout/mobile-card.md           | "首页" / "工作台" / "内容页" / "发现页" / "推荐页" / "猜你喜欢" / "相关推荐" / "多类型卡片" | "分类入口" / "设置" / "纯列表" / "瀑布流"               |
| mobile-grid           | layout/mobile-grid.md           | "首页" / "发现页" / "推荐页" / "音乐首页" / "宫格布局" / "宫格卡片"     | "列表" / "设置" / "瀑布流"                               |
| mobile-list           | layout/mobile-list.md           | "我的" / "个人中心" / "资产中心" / "会员中心" / "服务大厅" / "入口列表" | "开关为主" / "表单录入" / "多列瀑布流" / "feed 流"       |
| mobile-settings       | layout/mobile-settings.md       | "设置" / "设置页" / "喝水设置" / "系统设置"                            | "显示与亮度" / "情景模式" / "云空间" / "智慧多窗"        |
| settings-context-list | layout/settings-context-list.md | "显示与亮度" / "情景模式" / "云空间" / "智慧多窗"                      |                                                          |


## Page Templates

Generic, reusable page templates registered in this repository. Prompts may prefer a template when the design intent is generalizable.

| page_type             | template                       | template source                                                       | description                                                |
| --------------------- | ------------------------------ | --------------------------------------------------------------------- | ---------------------------------------------------------- |
| mobile-card           | mobile-card-template           | `src/pages/mobile-card-template/`                             | 多卡片类型垂直堆叠内容页（hero + 多类卡片 + 4-tab 底部栏）        |
| mobile-grid           | mobile-grid-template           | `src/pages/mobile-grid-template/`                             | 宫格首页/发现页（hero + chip + 水平滚动宫格 + miniplayer 底部栏）  |
| mobile-list           | mobile-list-template           | `src/pages/mobile-list-template/`                             | 入口型列表页（appicon + title + aux / value + chevron）         |
| mobile-settings       | settings-page                  | `src/pages/settings-page-template/`                                   | 通用系统设置页（多组设置卡片，开关/值/跳转行）                          |
| page-shell            | mobile-phone-shell-template    | `src/pages/mobile-phone-shell-template/`                      | 通用手机壳层实体模板；作为路由未命中时的兜底 page_type（见 Fallback），命中后必须使用 `MobilePhoneShellTemplatePage` 作为页面根壳层 |
| service-search        | service-search-template        | `src/pages/service-search-template/`                          | 云服务应用搜索页模板，适用于视频/应用市场/音乐/游戏/主题/阅读/云空间/查找/浏览器等 APP 搜索；支持搜索前 history/ranking、搜索中 result-list、搜索完成 completed-results(category-tabs + artist-card + completed-result-list) 三种组合；固定顶部搜索壳层，底部区域按场景使用底部导航、在线搜索 CTA 或 FloatingTab MiniPlayer |
| services-categories   | services-categories            | `src/pages/services-categories/`                              | 云服务业务筛选分类页模板，多行筛选 Chip + 内容网格宫格布局 |
| services-home         | services-home-template         | `src/pages/services-home-template/`                           | 云服务业务首页模板，适用于阅读、视频、音乐厅、游戏、应用市场、主题、云空间&查找、浏览器等云服务类 App 首页；固定顶部状态栏/标题搜索与底部主导航，主体 Block 可替换；默认阅读形态为 TopBanner + NewBookPreview + RecommendedNewBooks，游戏形态为 top-banner-2(Game) + my-game-review + recommended-new-games，音乐厅形态为 top-banner-2(Music) + music-recommended，电影形态为 top-banner-2(Movie) + my-movie-review + today-movie-list |
| services-launch-page  | services-launch-page           | `src/pages/services-launch-page/`                             | 云服务业务权限启动页模板，首次启动隐私协议场景，双按钮决策（同意/取消） |
| services-me           | services-me                    | `src/pages/services-me/`                                      | 云服务个人中心模板，身份卡片 + 快捷操作 + 常用服务 + 列表卡片 + 底部主导航 |
| services-ranking      | services-ranking               | `src/pages/services-ranking/`                                 | 云服务业务榜单模板，头图背景 + 金色标题 + 分类页签 + 纵向排名卡片流 |
| services-setting      | services-setting               | `src/pages/services-setting/`                                 | 服务类 App 底部弹出设置 Sheet 模板，全页半透明蒙层 + 底部毛玻璃圆角面板 + 分组列表设置项 |


## Fallback

> 未命中上述任何 `page_type` 规则时，默认路由到 `page-shell`（即 `mobile-phone-shell-template`）。
> 理由：`mobile-phone-shell` 是最通用的手机壳层容器，无任何业务语义偏向；其他模板（`mobile-card / mobile-grid / mobile-list / settings-page / ...`）均以它为壳层实现。
> 命中兜底后，最终页面必须以 `@/pages/mobile-phone-shell-template` 导出的 `MobilePhoneShellTemplatePage` 作为手机根壳层，业务内容只能作为 children 填入。不得仅拆用 `FloatingTitleBar`、`Aibottombar` 或自写 `.xxx-canvas` / `.xxx-body` 后声称使用了 `page-shell`。
> `page-shell` 只提供壳层，不提供具体业务布局；不得仅因命中兜底就把页面默认渲染成 `mobile-settings` 之类的具体业务布局。

## Active Notes

- `health-dashboard` 与 `mobile-sheet` 的历史 block 已停用，不再作为 active page_type 参与工作流路由
- `mobile-card` / `mobile-grid` / `mobile-list` 由 `.tmp/layout-card.md`、`.tmp/layout-grid.md`、`.tmp/layout-list.md` 提取
- `settings-page` 模板由 `dragonestdwolf/Vibe-UI-Forge` 资源适配，外部 import alias / 资源路径已翻译为本仓库约定

## Notes

- page_type 使用 kebab-case
- layout 路径相对于 `src/pages-specs/`
- 模板目录约定：`src/pages/<template-name>-template/`，每个目录含 `*.tsx` / `*.css` / `index.ts`
