# Harmony Design — 目录结构说明

自包含的 HarmonyOS React 独立 HTML 页面生成 Skill。不依赖 design-system 工作区，只读取自身内置资源完成端到端页面生成。

## 文件树

```
harmony-design/
├── README.md
├── SKILL.md
├── agents/
│   └── openai.yaml
├── babel-render-tsx/
│   ├── design-system-vendor/
│   │   ├── react-vendor-19.2.6.js      # React 19 浏览器端运行时
│   │   ├── babel-standalone.js          # 浏览器端 Babel 编译器
│   │   ├── tailwind-browser.js          # 浏览器端 Tailwind CSS
│   │   ├── design-components.js         # 组件 JS bundle
│   │   ├── design-components.css        # 组件样式（含 token）
│   │   ├── blocks-components.js         # Block JS bundle
│   │   ├── blocks-components.css        # Block 样式
│   │   ├── hmsymbol-font.css            # HMSymbol 字体引用
│   │   └── HMSymbolVF.ttf               # HMSymbol 可变字体
│   └── html-template/
│       └── babel-string-template.html   # HTML 骨架模板
├── references/
│   ├── container-audit.md               # 容器审计规则
│   ├── hmsymbol-audit.md                # HMSymbol 图标审计
│   ├── page-resource-manifest.json      # 页面资源清单
│   ├── resource-contract.md             # 资源解析合约
│   ├── shell-contract.md                # Shell 模板合约
│   ├── template-required-components.json # 模板必需组件清单
│   └── patterns/
│       └── mobile-metric-dashboard.md   # 页面复用模式
├── scripts/
│   ├── shared.mjs                       # 共享模块（skillDir / sourceRoot）
│   ├── resolve-page-resources.mjs       # A3 资源解析器
│   ├── prepare-template-merge.mjs       # 模板合并器
│   ├── scaffold-standalone-html.mjs     # HTML 脚手架
│   ├── validate-page-artifact.mjs       # 产物校验
│   ├── validate-source-fast.mjs         # 快速源码验证
│   ├── check-hmsymbol-usage.mjs         # HMSymbol 使用审计
│   ├── babel.mjs                        # Babel 编译入口
│   └── vendor/
│       └── babel-bundle.mjs             # Babel bundle
└── src/
    ├── route-index.md                   # 路由索引
    ├── styles/
    │   └── global.css                   # 设计 token
    ├── assets/
    │   ├── assets.json                  # 资源注册表
    │   └── hmsymbol/
    │       ├── HMSymbolVF.ttf
    │       ├── hmsymbol-aliases.json
    │       ├── hmsymbol-icons-common.md
    │       ├── hmsymbol-index.md
    │       └── hmsymbol-map.json
    ├── pages-specs/layout/              # 14 个 page_type 布局规格
    │   ├── index.md
    │   ├── mobile-card.md
    │   ├── mobile-grid.md
    │   ├── mobile-list.md
    │   ├── mobile-settings.md
    │   ├── page-shell.md
    │   ├── service-search.md
    │   ├── services-categories.md
    │   ├── services-home.md
    │   ├── services-launch-page.md
    │   ├── services-me.md
    │   ├── services-ranking.md
    │   ├── services-setting.md
    │   ├── settings-context-list.md
    │   └── settings-page.md
    ├── pages/                           # 页面模板（只读起点）
    │   ├── mobile-card-template/
    │   ├── mobile-grid-template/
    │   ├── mobile-list-template/
    │   ├── mobile-phone-shell-template/
    │   ├── service-search-template/
    │   ├── services-home-template/
    │   ├── settings-page-template/
    │   ├── services-categories/         # 完整页面（含 assets/）
    │   ├── services-launch-page/
    │   ├── services-me/
    │   ├── services-ranking/
    │   └── services-setting/
    ├── components-specs/                # 70+ 组件规格 + components.json
    │   ├── components.json
    │   ├── button.md
    │   ├── card.md
    │   ├── dialog-phone.md
    │   ├── floating-title-bar.md
    │   ├── ...                          # 其余 .md 规格文件
    │   └── toggle.md
    ├── blocks-specs/                    # 30+ Block 规格 + blocks.json
    │   ├── blocks.json
    │   ├── ranking-list.md
    │   ├── top-banner.md
    │   └── ...
    └── components/
        └── HMSymbolIcon/               # 图标组件 TypeScript 常量
            ├── hmsymbol-icon.constants.ts
            └── hmsymbol-icon.generated.ts
```

## 目录总览

```
harmony-design/
├── SKILL.md                  # Skill 入口 SOP 文档
├── agents/                   # AI 代理配置
├── babel-render-tsx/         # 浏览器端运行时依赖
├── references/               # 参考文档与合约
├── scripts/                  # 工具链脚本
└── src/                      # 自包含只读资源快照
```

---

## `SKILL.md`
Skill 入口文档，定义完整 SOP 流程：

```
锁定目标 → A1 Route → A2 Layout → A3 Resources → 合并模板生成 HTML → 验证 → 报告
```

核心边界：不依赖 design-system 工作区，所有资源自给自足，输出单文件 `.shadcn.html`。

---

## `agents/`
| 文件 | 作用 |
|------|------|
| `openai.yaml` | 备用 AI 代理配置 |

---

## `babel-render-tsx/` — 浏览器端运行时依赖

独立 HTML 在浏览器中通过 Babel standalone 编译 TSX 所需的全部 vendor 文件。

### `babel-render-tsx/design-system-vendor/`
| 文件 | 作用 |
|------|------|
| `react-vendor-19.2.6.js` | React 19 浏览器端运行时 |
| `babel-standalone.js` | 浏览器端 Babel 编译器，将 TSX 实时编译为 JS |
| `tailwind-browser.js` | 浏览器端 Tailwind CSS 引擎 |
| `design-components.js` | 所有注册组件的预构建 JS bundle |
| `design-components.css` | 组件样式（含 CSS 设计 token） |
| `blocks-components.js` | Block 复合 UI 块的预构建 JS bundle |
| `blocks-components.css` | Block 样式 |
| `hmsymbol-font.css` | HMSymbol 图标字体引用 |
| `HMSymbolVF.ttf` | HMSymbol 可变字体文件 |

### `babel-render-tsx/html-template/`
| 文件 | 作用 |
|------|------|
| `babel-string-template.html` | 最终 `.shadcn.html` 的 HTML 骨架模板，含 `page-tsx` 占位节点和 vendor 引用 |

---

## `references/` — 参考文档与合约

| 文件 | 作用 |
|------|------|
| `page-resource-manifest.json` | 页面资源清单 — 定义每种 `page_type` 需要的模板、组件、token、图标、pattern |
| `template-required-components.json` | 模板必需组件清单 — 各模板的硬性组件依赖 |
| `resource-contract.md` | A3 资源解析合约 — 定义正式五件套（route → layout → registry × 3）和 fallback 降级规则 |
| `container-audit.md` | 容器审计规则 — `ListContainer`（单轴集合 + `pixso-list-item`）、`GridContainer`（二维集合 + `pixso-grid-item`）、`NavigationContainer`（页面级唯一）的使用规范 |
| `hmsymbol-audit.md` | HMSymbol 图标审计规则 — 图标名称校验与使用规范 |
| `shell-contract.md` | Shell（手机外壳模板）合约 — `MobilePhoneShellTemplatePage` 的结构约束与内联合并规则 |
| `references/patterns/` | 页面复用模式 — 如 `mobile-metric-dashboard.md` 等预定义页面模式 |

---

## `scripts/` — 工具链脚本

| 脚本 | 作用 | SOP 阶段 |
|------|------|----------|
| `shared.mjs` | 共享模块 — 导出 `skillDir`、`sourceRoot`、`findDesignSystemRoot`、`isInsideOrEqual`，无模式检测 | 全局 |
| `resolve-page-resources.mjs` | A3 资源解析器 — 输入 `page_type`，输出经过正式 registry 校验的模板、组件、token、图标、pattern | A3 |
| `prepare-template-merge.mjs` | 模板合并器 — 递归并入嵌套模板、去重声明、输出合并后的 TSX + CSS | 步骤 3 |
| `scaffold-standalone-html.mjs` | HTML 脚手架 — 基于 `babel-string-template.html` 创建或更新 `.shadcn.html`，注入合并后的 TSX 和内联样式 | 步骤 3 |
| `validate-page-artifact.mjs` | 产物校验器 — 检查 HTML 壳、嵌入 TSX、Navigation/List/Grid 容器、HMSymbol 图标等 | 步骤 4 |
| `validate-source-fast.mjs` | 快速源码验证 — 并发运行 artifact + TypeScript 检查（standalone 模式仅 artifact），可选 ESLint | 步骤 4 |
| `babel.mjs` | Babel 编译入口 | 辅助 |
| `check-hmsymbol-usage.mjs` | HMSymbol 图标使用审计 — 扫描 TSX 中的 `HMSymbolIcon` 引用，校验 name 是否存在于本地资源表 | 按需 |
| `scripts/vendor/babel-bundle.mjs` | Babel 编译 bundle | 辅助 |

---

## `src/` — 自包含只读资源快照

从主项目 `src/` 裁剪出的独立子集，standalone 模式的唯一资源来源。

### `src/route-index.md`
路由索引 — 用户意图 → `page_type` 匹配规则。含 `hit_rules` 和 `exclusion_rules`，无命中时 fallback 为 `page-shell`。

### `src/pages-specs/layout/`
布局规格 — 每种 `page_type` 一份 `.md`，定义骨架、section/Block 清单、组件约束、空间 token、验证规则。

| 文件 | 对应 page_type |
|------|---------------|
| `index.md` | 布局索引 |
| `mobile-card.md` | 卡片布局页 |
| `mobile-grid.md` | 网格布局页 |
| `mobile-list.md` | 列表布局页 |
| `mobile-settings.md` | 移动端设置页 |
| `page-shell.md` | 通用 Shell（无命中 fallback） |
| `service-search.md` | 服务搜索页 |
| `services-categories.md` | 服务分类页 |
| `services-home.md` | 服务首页 |
| `services-launch-page.md` | 服务启动页 |
| `services-me.md` | 我的页面 |
| `services-ranking.md` | 排行榜页 |
| `services-setting.md` | 服务设置页 |
| `settings-context-list.md` | 上下文列表设置页 |
| `settings-page.md` | 通用设置页 |

### `src/pages/`
页面模板 — 按模板生成新页面时的起点（只读）。

| 目录 | 说明 |
|------|------|
| `mobile-card-template/` | 移动端卡片模板 — 卡片垂直堆叠 + section header |
| `mobile-grid-template/` | 移动端网格模板 — 二维网格布局 |
| `mobile-list-template/` | 移动端列表模板 — 单轴列表布局 |
| `mobile-phone-shell-template/` | 手机外壳模板 — 含 `NavigationContainer`、`FloatingTitleBar`、`FloatingTab`、`Aibottombar` 等完整 Shell |
| `service-search-template/` | 服务搜索模板 |
| `services-home-template/` | 服务首页模板 |
| `settings-page-template/` | 设置页模板 |
| `services-categories/` | 服务分类完整页面（含 12 张蒙版图片） |
| `services-launch-page/` | 服务启动完整页面 |
| `services-me/` | 我的页面完整页面 |
| `services-ranking/` | 排行榜完整页面 |
| `services-setting/` | 服务设置完整页面 |

### `src/components-specs/`
组件规格 — `components.json` 注册表 + 50+ 个组件的 `.md` 规格文件（Button、Card、Dialog、Swiper、Picker、Chip、Tab、Toast、Slider、Menu、Search、Toggle、Checkbox、Radio、Switch、TextInput、Select、Counter、Progress、Toolbar、BottomTab、FloatingTitleBar 等）。

### `src/blocks-specs/`
Block 规格 — `blocks.json` 注册表 + 25+ 个复合 UI 块（top-banner、ranking-list、music-search、rating-card、filter-list、floating-sheet、recommended-new-books 等）。

### `src/components/`
组件源码 — 仅含需要本地 TypeScript 常量的特殊组件。

| 目录 | 说明 |
|------|------|
| `HMSymbolIcon/` | HMSymbol 图标组件 — `hmsymbol-icon.constants.ts`（常量定义）+ `hmsymbol-icon.generated.ts`（自动生成） |

### `src/assets/`
资源注册表与字体文件。

| 文件 | 说明 |
|------|------|
| `assets.json` | 资源注册表 |
| `hmsymbol/HMSymbolVF.ttf` | HMSymbol 可变字体 |
| `hmsymbol/hmsymbol-aliases.json` | 图标别名映射 |
| `hmsymbol/hmsymbol-icons-common.md` | 常用图标清单 |
| `hmsymbol/hmsymbol-index.md` | 图标全量索引 |
| `hmsymbol/hmsymbol-map.json` | 图标名称 → 字形映射 |

### `src/styles/global.css`
设计 token — 200+ CSS 自定义属性（颜色、间距、字体、圆角、阴影等语义化 token）。

---

## 工作流串联

```text
用户意图
  ↓
SKILL.md（SOP 入口）
  ↓
src/route-index.md（A1 Route — 意图 → page_type）
  ↓
src/pages-specs/layout/{page_type}.md（A2 Layout — 骨架 + 组件清单）
  ↓
scripts/resolve-page-resources.mjs（A3 Resources — 校验 registry + 输出命中资源）
  ↓
scripts/prepare-template-merge.mjs（合并模板 — 递归并入嵌套模板）
  ↓
babel-render-tsx/html-template/babel-string-template.html（HTML 骨架）
  + babel-render-tsx/design-system-vendor/*（浏览器端运行时）
  ↓
scripts/scaffold-standalone-html.mjs（生成 .shadcn.html）
  ↓
scripts/validate-source-fast.mjs（快速验证）
  ↓
交付：{page-name}.shadcn.html
```
