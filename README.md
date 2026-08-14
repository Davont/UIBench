# UIBench

> 输入一句话移动端 UI 需求，并行调用多个大模型，**同屏渲染**对比各模型生成的
> HTML，并显示每个模型的执行耗时。

UIBench 只干一件事：

1. 用户在页面输入一句话的移动端 UI 需求（如“一个带搜索框和底部导航的电商首页”）。
2. 后端把同一条需求**并行**发送给所有已启用的 LLM。
3. 每个模型返回的 HTML 在同一页面上以**手机框 iframe** 渲染出来，每张卡片标注
   模型名称与执行耗时。

---

## 特性

- **一键对比**：一次输入，多个模型，同屏并排渲染。
- **多供应商**：OpenAI、Anthropic、Google Gemini、DeepSeek，全部通过 LangChain
  聊天模型接入，按需启用。
- **并行调用**：所有模型并发执行（线程池），总耗时≈最慢的那个模型。
- **隔离渲染**：每个结果渲染在带 `sandbox` 的 iframe 里，各模型样式/脚本互不污染。
- **耗时可见**：每张卡片显示该模型的执行秒数。
- **真实生成进度**：每个模型独立显示准备请求、等待生成、整理 HTML、
  自动补全和加载预览等后端真实阶段；不显示假百分比或原始思维链。
- **完成即展示**：谁先生成完成，谁的预览就先在原卡片中出现，无需等待最慢模型。
- **逐模型容错**：某个模型缺 key 或报错，只在该卡片上显示错误，不影响其他模型。
- **多风格主题 Token**：移动端模型只写 Tailwind；系统把 Design Token 编译成固定
  Tailwind Theme Preset，同一份 HTML 可以在 HarmonyOS、Spotify、Netflix、Notion
  之间迁移，并切换白天/黑夜。
- **AI 可选真实图片**：模型可按需调用 `search_photos` 获取摄影图片，默认走
  完全离线的本地分类图库（毫秒级、可复现、无外网依赖），也可切换为 Unsplash
  MCP 实时搜索；不需要图片或工具失败时自动使用 Token 占位，不影响页面生成。
- **HTML 离线资源包**：结果卡片可下载包含 `index.html`、主题样式、HarmonyOS 字体和
  页面实际引用的 `assets/` / 本地图库图片的 ZIP；解压后双击 HTML 即可正确读取本地资源。

---

## 项目结构

```
UIBench/
├── README.md                  # 本文档
├── requirements.txt           # 依赖清单
├── package.json               # 固定的本地 Node 运行包
├── package-lock.json          # 可复现、可离线的 Node 安装锁
├── vendor/html-to-arkui/      # 内置转换器 tgz、哈希及来源清单
├── app.py                     # FastAPI 应用 + 单页 UI（核心入口）
├── assets/gallery/            # 本地图库（生成物，Git 忽略，可随时重建）
├── tools/
│   ├── arkui-export.mjs       # html-to-arkui JSON 子进程桥
│   ├── gallery_topics.yaml    # 图库分类/搜索词/匹配词（纯数据）
│   └── build_gallery.py       # 一次性建库脚本（Unsplash → assets/gallery）
├── config/
│   ├── __init__.py
│   ├── settings.py            # 读取 models.yaml 的运行参数
│   └── models.yaml            # 唯一配置文件（端点+key+模型+参数）
├── uibench/
│   ├── __init__.py
│   ├── schemas.py             # pydantic 数据模型
│   ├── models.py              # LangChain 聊天模型工厂
│   ├── image_tools.py         # 图片工具契约 + 双源分发（本地图库 / Unsplash MCP）
│   ├── app_icons.py           # 请求级内置应用图标目录 + 错图自动纠正
│   ├── local_gallery.py       # 本地图库 manifest 加载与关键词匹配
│   ├── prompts.py             # 移动端 UI 生成 Prompt
│   ├── pc.py                  # PC 端 Prompt 与渲染适配
│   ├── arkui/                 # UIBench 标注、Screen IR 与 ArkTS 导出适配层
│   └── design_tokens/         # 独立的移动端 Design Token 功能
│       ├── __init__.py        # 校验、CSS 生成和 HTML 注入
│       ├── tokens.json        # light / dark 两套 Token
│       └── README.md          # Token 合约说明
└── tests/                     # pytest 套件（无需 API key）
    ├── conftest.py
    ├── test_schemas.py
    ├── test_models.py
    ├── test_arkui_components.py
    ├── test_arkui_export.py
    └── test_app.py
```

---

## 工作流程

```
用户在页面输入一句话需求
        │
        ▼
  POST /api/generate  ──────► app.py
        │                          │ create_task + Queue（并行）
        │                          ├── 模型 A ──► progress* ──► result
        │                          ├── 模型 B ──► progress* ──► result
        │                          └── 模型 C ──► progress* ──► result
        │ ◄── NDJSON: start ─► progress/result … ─► done ──────┘
        ▼
  前端：每个模型一张卡片
   ├── 模型名 + 供应商 + ⏱ 独立耗时 + 阶段日志
   └── iframe srcdoc=HTML（手机框渲染）
```

---

## 安装

需要 Python 3.11+（在 3.13 上开发）和 Node.js 18+。

```bash
# 1.（可选）创建虚拟环境
python -m venv .venv
.\.venv\Scripts\activate          # Windows
# source .venv/bin/activate       # macOS / Linux

# 2. 离线安装仓库内置的 html-to-arkui Node 运行包
npm ci --ignore-scripts --offline

# 3. 安装 Python 依赖
pip install -r requirements.txt

# 4. 编辑唯一配置文件 config/models.yaml，填入端点和 key（默认已预配 8 个模型）
```

---

## 配置（单文件）

所有配置都在 `config/models.yaml` 一个文件里：运行参数 + 端点 + key + 模型列表。

```yaml
# 运行参数
options:
  temperature: 0.0
  max_tokens: 4096
  request_timeout: 120

# 公共字段：下面的每个模型都继承这段
defaults:
  provider: openai
  base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
  api_key: "sk-..."            # 直接写 key

models:
  - id: deepseek-v4-pro
    name: "DeepSeek v4 Pro"
  - id: qwen3.7-plus
    name: "Qwen3.7 Plus"
  # ... 共 8 个模型
```

字段说明：

| 字段          | 作用                                                 |
|---------------|------------------------------------------------------|
| `options`     | 运行参数：`temperature` / `max_tokens` / `request_timeout` |
| `defaults`    | 公共字段，合并进每个模型（单条可覆盖）              |
| `provider`    | `openai` / `anthropic` / `google` / `deepseek`      |
| `base_url`    | 该模型端点（任意 OpenAI 兼容网关）                   |
| `api_key`     | 字面 key（本地用即可）                               |
| `api_key_env` | 存 key 的环境变量名（可选，替代 `api_key`，从系统环境变量读）|
| `enabled`     | 是否参与对比（默认 true）                            |

key 解析：`api_key` → `api_key_env` 指向的环境变量 → 无则报错卡片。
URL 解析：`base_url`。某个模型若 key 缺失或被端点拒绝，只在该卡片显示错误，
不影响其他模型。

> 若以后把这个目录纳入版本控制，建议把 `api_key` 改成 `api_key_env`，或把
> `config/models.yaml` 加入 `.gitignore`，避免密钥入库。

---

## 图片素材（本地图库为主，Unsplash 实时搜索备选）

模型通过统一的 `search_photos` 工具按具名槽位申请图片；图片来自哪个源由
`config/models.yaml` 的 `options.image_source` 决定（页面顶部还有
“离线图库 / 在线搜索”开关，可按次覆盖该默认值，选择会记忆在浏览器里；
每张结果卡片会标注本次用的是“本地图片”还是“在线图片”），模型侧无感知：

- **`local`（默认，推荐）**：完全离线的本地分类图库。搜索毫秒级返回，页面渲染时
  图片走同源 `/gallery/...`，不依赖外网、无 API 限流，同一需求每次拿到的图片
  确定，方便模型间公平对比。
- **`unsplash`**：通过本地 stdio MCP 实时搜索 Unsplash，图片更贴合具体需求，
  但受网络与 50 次/小时配额限制。

### 构建本地图库（一次性）

分类、搜索词与匹配关键词全部维护在 `tools/gallery_topics.yaml`（纯数据，
与运行时代码解耦）；脚本从 Unsplash 拉图并生成
`assets/gallery/manifest.json`，运行时只读这份 manifest：

```bash
# .env 写入 UNSPLASH_ACCESS_KEY（只有建库需要，运行时不需要）
python tools/build_gallery.py               # 全量建库（默认 10 类约 120 张 / 20+MB）
python tools/build_gallery.py -c food       # 只重建某分类
python tools/build_gallery.py --refresh-manifest  # 只按 yaml 更新匹配词，不联网
```

图库目录被 Git 忽略，可随时重建；想扩充分类或调整匹配词，改 yaml 重跑即可，
无需改代码。

### 下载 HTML 资源包

每张成功结果卡片提供“下载 HTML 包”。ZIP 根目录是 `index.html`，本地依赖统一放到
`assets/` 并改写为相对路径；只收集页面实际引用的文件，不会把整个图库重复打包。
解压 ZIP 后直接双击 `index.html` 即可。`https://` 图片、字体和 CDN 脚本会保留原 URL，
不会由服务端代抓，因此这些远程内容在完全断网时仍不可用。

### Unsplash 实时搜索（可选备选）

```bash
git clone https://github.com/hellokaton/unsplash-mcp-server.git \
  .mcp/unsplash-mcp-server
uv sync --project .mcp/unsplash-mcp-server
# .env: UNSPLASH_ACCESS_KEY=your_access_key
# config/models.yaml: options.image_source: unsplash
```

### 行为约定（两种源一致）

内容型但语义不明确的页面（例如“读书 APP”）会先由本轮首个 AI 模型统一判断是否
需要摄影图片，并一次性规划具名槽位；同一轮所有参评模型共享这份计划和同一批素材。
商城、餐饮、酒店等明确的图片密集场景仍保留应用侧最低图片数量护栏；其他页面除非
用户明确要求无图，也交给规划器按可见内容判断，不维护页面类型的免图片名单。完整链路是：

```text
用户需求 → AI 统一规划/应用硬护栏 → 图片源解析（本地 manifest 匹配 / MCP 搜索）
         → 同轮模型共享图片批次 → 模型输出 HTML → 使用不足时自动修复一次
```

每个模型最多发起一次 `search_photos` 工具调用，可在一次调用中按具名视觉槽位
批量获取最多 `image_tool_max_assets` 张图片。同一次对比运行复用相同批次；模型
必须把返回图片用于对应槽位，只能引用工具返回的 URL。模型自行编造图片 URL、
动态图片绑定或图片数量不足时只显示“图片异常”告警，仍会保留并渲染完整 HTML，
不设置预览阻断门槛。需求中明确写出的数量（如“生成 5 张肖像图”）会直接成为
槽位数量，并受 `image_tool_max_assets` 上限约束。Access Key、图库目录、
MCP 目录和真实模型配置均被 Git 忽略，不会提交到 fork 仓库。

应用 Logo 不进入摄影图库。需求提到应用图标、常用应用或已知应用名称时，UIBench 只把
相关的本地 `/assets/app-icons/*.png` 目录动态附加给模型；当前包含微信、支付宝、QQ、
抖音、淘宝、美团、小红书、哔哩哔哩，以及相机、地图、相册、通讯录。全部品牌应用采用
当前中国区 App Store 上架版本的应用图标；每个图标的开发者、Bundle ID、上架版本、
更新时间、原图地址和本地哈希记录在 `assets/app-icons/sources.json`。
规划器返回的 app icon / logo 照片槽位会被过滤；如果模型仍把同一张通用照片复用给多个
已知应用，生成后会按相邻应用名称自动绑定正确图标。PNG 会随 HTML 包和 ArkUI 资源捕获
一起进入导出结果；只有 UIBench 自有的通用系统图标保留 SVG 源文件。

---

## 用法

```bash
python app.py
```

### 移动端多品牌风格 / 明暗主题

移动端生成 Prompt 只要求模型使用 Tailwind。UIBench 注入的 Theme Preset 提供
`ui-*` 语义值，例如：

```html
<main class="bg-ui-canvas text-ui-fg font-ui p-ui-page">
  <section class="bg-ui-surface rounded-ui-card p-ui-card">
    <label class="bg-ui-component-subtle rounded-ui-control">
      <input class="text-ui-fg placeholder-ui-fg-secondary" placeholder="搜索" />
    </label>
    <button class="bg-ui-primary text-ui-on-primary hover:bg-ui-primary-hover focus-visible:ring-2 focus-visible:ring-ui-focus">
      继续
    </button>
    <span class="bg-ui-accent text-ui-on-accent rounded-ui-pill">辅助强调</span>
  </section>
</main>
```

`ui-page`、`ui-card`、`ui-item` 等是 Tailwind spacing key，因此模型可以按标准
Tailwind 语法组合出 `px-ui-page`、`py-ui-card`、`gap-ui-item`、`ml-ui-item`，无需
学习另一套 CSS 类规则。UIBench 在渲染时注入固定 preset 和 `/design-tokens.css`。根节点通过
`data-token-theme="harmonyos|spotify|netflix|notion"` 选择风格，
通过 `data-theme="light|dark"` 选择明暗模式。页面上的主题按钮只重新渲染当前
iframe，不会再次请求模型，因此适合直接对比风格迁移效果。

Token 源文件位于 `uibench/design_tokens/tokens.json`；四个风格必须实现相同的
语义字段，而且各自的 `light` 与 `dark` 字段必须完全一致，应用启动和测试时会校验。
`GET /api/design-tokens` 可查看原始 Token，
`GET /design-tokens.css` 可查看转换后的 CSS Variables 与语义工具类。

Design Token 仍是颜色、间距、字体和圆角的唯一数据源；Tailwind preset 只是模型侧
适配器。例如页面层级使用 `bg-ui-layer-secondary` / `bg-ui-layer-tertiary`，搜索框和
弱按钮使用 `bg-ui-component-subtle` / `bg-ui-component-secondary`，组件轮廓与列表
分割线分别使用 `border-ui-border` 和 `border-ui-divider` / `divide-ui-divider`。

> 旧日志中的 HTML 在引入本功能前使用了硬编码 Tailwind 颜色类。UIBench 会通过兼容层
> 映射常见的中性色、边框、主色和状态色，因此可以进行基础风格切换，但不能保证完整
> 迁移。旧 `dt-*` HTML 仍由兼容层支持；重新生成的页面使用 Tailwind Theme Preset。

### 可选 ArkUI 工程导出

移动端模式可勾选“生成 ArkUI 可导出元数据”。开启后，模型只使用当前
`html-to-arkui` 公共契约已支持的 22 个组件：`Column`、`Row`、`Stack`、
`Scroll`、`Text`、`Span`、`Image`、`SymbolGlyph`、`Divider`、`Button`、
`List`、`ListItem`、`Grid`、`GridItem`、`Toggle`、`Slider`、`TextInput`、`Search`、
`Checkbox`、`Radio`、`Tabs`、`TabContent`。
`List` 只接受 `ListItem` 子节点，
`ListItem` 最多包含一个已标注组件子节点，条目间距写在 `List` 上；横向列表按
浏览器实际主轴导出为 `.listDirection(Axis.Horizontal)`，无需额外标注。`Grid`
只接受 `GridItem` 子节点，轨道与间距从浏览器实测的 `grid-template-*` / `gap`
冻结为 `.columnsTemplate()` 等修饰器，显式跨行列（`col-span-*` 等）不支持并会
阻断导出。原生表单、选择和页签组件会把 HTML 的初始值、禁用状态、分组及页签文字写入
Screen IR；
双向状态与事件绑定仍由宿主工程负责。

转换器已作为包含全部运行依赖的固定 `.tgz` 放在
`vendor/html-to-arkui/`，安装 UIBench 时执行：

```bash
npm ci --ignore-scripts --offline
```

UIBench 默认只读取根目录 `node_modules/@local/html-to-arkui`，不依赖兄弟仓库，也不需要
访问 npm registry。转换器开发者可以用 `HTML_TO_ARKUI_ROOT` 显式覆盖到本地源仓库；
部署环境不应设置该变量。生成结果通过组件校验后，卡片会显示“下载鸿蒙工程”。
也可以直接调用。下面只展示请求形状；`computed` 为节选，不能原样提交：

```text
POST /api/arkui/export
{
  "html": "...",
  "page_name": "GeneratedPage",
  "mode": "annotated",
  "snapshot": {
    "snapshotVersion": 1,
    "viewportWidth": 390,
    "viewportHeight": 844,
    "theme": "light",
    "tokenTheme": "harmonyos",
    "canvasBackgroundColor": "rgb(255, 255, 255)",
    "canvasBackgroundImage": "none",
    "nodes": [{
      "nodeId": "page",
      "tag": "main",
      "bbox": [0, 0, 390, 844],
      "visible": true,
      "computed": {
        "display": "flex",
        "flexDirection": "column",
        "width": "390px",
        "height": "844px"
      }
    }]
  }
}
```

Web 页面会自动生成并提交完整 `BrowserSnapshot`。直接调用 annotated API 时也必须提供
经过校验的快照；缺少快照会返回 `UIBENCH_BROWSER_SNAPSHOT_REQUIRED`（HTTP 422）。每个
节点的 `computed` 必须包含浏览器捕获协议定义的全部白名单字段，而不只是
`display` / `width` / `height`；缺字段会返回
`UIBENCH_BROWSER_SNAPSHOT_INCOMPLETE`，其 `details.reason` 为
`computed-style-capture-fields-missing`，`details.missingFields` 列出缺失字段。这样不会把
Pydantic 补出的默认空值误认为真实浏览器样式，也不会再生成只有组件树、没有样式
modifier 的工程。`generic` 模式仍保留 source-only 的 best-effort 转换。
严格导出还会校验 HTML/body 的画布背景：纯色画布会被提升到唯一组件根（`dt-bg-canvas`
写在 `<body>` 上也可以），背景图或渐变返回 `UIBENCH_CANVAS_BACKGROUND_IMAGE_UNSUPPORTED`。
组件根上方有可寻址 wrapper、用半透明色与画布混合，或用自己的不透明色但没有包含整个视口
（可滚动页面的根比视口高，判定的是包含而非尺寸相等）时，浏览器里同时看得见画布和根两种
颜色而一个 ArkUI 背景表达不了，返回 `UIBENCH_CANVAS_BACKGROUND_ROOT_UNSUPPORTED`。每个节点还必须显式提交
`directParentNodeId` 与 `isFlexItem`（值可以是 `null` / `false`），避免省略 provenance
字段后绕过 DOM 结构校验。

当前版本已完成 Component Manifest → 固定 390×844 浏览器快照 → Screen IR v2 →
ArkTS → 完整 HarmonyOS 工程链路。浏览器快照会固化当前主题的 computed style、bbox 和可见状态，
并在 CORS 允许时读取页面已经渲染的 PNG/JPEG/GIF/WebP 图片和简单背景图。后端按内容
校验、去重，输出 `resources/base/media` 和 `$r('app.media.*')` 绑定；它不会主动访问网络。
缺少任一 annotated 节点快照，或 `Row` / `Column` 元数据与浏览器布局冲突时会阻止
导出；资源抓取失败或包含阴影、transform、filter、复杂背景等能力时返回 `lossy`。
Flex 扩展项只有在零 basis、兼容 shrink、直接 DOM 父节点与 Flex-item 身份均通过快照
验证后才会映射为 `layoutWeight`。完整工程响应缺少 ZIP 的
`bundle.contentBase64` 时，Web 页面会明确报错并停止下载，不会降级成单个 ETS 文件。
下载 ZIP 是 DevEco Studio 6.0.2 / HarmonyOS SDK 6.0.2
（API 22）的单模块 Stage 工程，包含应用配置、UIAbility、页面路由、Hvigor 配置和资源。
生成器及真实导出样例已通过
ArkTS 编译和 unsigned HAP 打包；签名和本机 SDK 路径由开发者打开工程后配置。旧 HTML
可使用 `mode: "generic"` 进行平台转换器的 best-effort 兜底。

仓库还提供三份固定视口的截图回归样本和离线比较工具。先准备工程与报告：

```bash
python tools/arkui-regression.py prepare \
  --case tests/fixtures/arkui_regression/typography/case.json \
  --out .artifacts/arkui-regression/typography

python tools/arkui-regression.py build \
  --run .artifacts/arkui-regression/typography
```

当前 `build` 子命令按 macOS 的 DevEco Studio `.app/Contents` 目录布局定位工具链；
可用 `--deveco-studio /absolute/path/to/DevEco-Studio.app` 指定应用路径。Windows
工具链路径探测尚未接入。

可以先只读检查 HDC 环境；有在线目标和本地调试签名 HAP 后，命令会校验 HAP 中的
Bundle/Module/Ability 及其与当前 run 构建产物的 payload 一致性，再安装、拉起页面并
采集原始整屏截图：

```bash
python tools/arkui-regression.py probe-hdc

python tools/arkui-regression.py capture-hdc \
  --run .artifacts/arkui-regression/typography \
  --hap /absolute/path/to/entry-default-signed.hap
```

默认不会尝试安装构建产生的 unsigned HAP，也不会生成、打包或记录签名证书、密码和
profile。文件名和 payload 校验不等于密码学验签，最终以目标设备接受安装为准；调试签名
应在开发者本机 DevEco Studio 中配置。回归专用工程壳会隐藏系统栏，并用自定义 Layout
先把页面唯一根节点固定测量为 case 的标准视口，再按设备 display/density 等比缩放；
交付用的 `export/page.ets` 不会被改写。HDC 整屏图仍不会自动进入比较，必须显式指定
物理像素 crop 和目标视口。下面是本机 API 22 模拟器 `1320×2856` 整屏图到标准
`390×844` 的确定性面积重采样；所有 crop 参数都必须由真实设备证据确定：

```bash
python tools/arkui-regression.py normalize-hdc \
  --run .artifacts/arkui-regression/typography \
  --crop 0,0,1320,2856 \
  --content-viewport 390x844 \
  --resample area-v1
```

归一化仍保持报告为 `incomplete`。随后把报告记录的当前
`screenshots/normalizations/<normalizationId>/arkui.png` 传给 `compare`，才会计算指标。
v1 `identity`/`box-v1` 继续支持 1～8 的整数 scale；v2 `area-v1` 由 crop 与目标视口完整
定义，使用有工作量上限的整数面积权重，并把来源截图、布局树、参数和输出哈希写入
manifest。工具不会猜测 crop、补边或系统栏范围。

也可以在外部获得同尺寸 ArkUI PNG 后，再生成像素指标和差异图：

```bash
python tools/arkui-regression.py compare \
  --run .artifacts/arkui-regression/typography \
  --arkui-screenshot /absolute/path/to/typography-arkui.png
```

每次比较先把 ArkUI 图、差异图和 Markdown 摘要写入独立的
`screenshots/comparisons/<comparisonId>/`，最后只原子切换 `report.json`，避免失败重跑
把上一轮报告与新截图混在一起；切换成功后只保留当前版本。输入必须是有界、全屏不透明
且尺寸一致的 PNG。同一个 run 的并发 `prepare`、`build`、`capture-hdc`、`compare`
会被互斥锁明确拒绝。

本机已在 HarmonyOS 6.0.2（API 22）模拟器上打通三份样本的完整链路。模拟器物理画布为
`1320×2856`、density 3.5，逻辑窗口约为 `377×816vp`；回归壳 v2 保持 `390×844`
canonical 布局后再适配设备画布。三份工程均通过 API 22 编译，模拟器实际接受当前
unsigned 调试 HAP；报告只记录 `device-install-accepted`，这不等于密码学验签，也不代表
真机可以安装。无阈值首轮结果均为 `observed`：`typography` MAE 5.41 / RMSE 23.47、
`stack-card` 3.61 / 14.02、`scroll-feed` 4.75 / 22.03。真实回归同时发现并修复了 intrinsic
单行文字被错误固化宽度、短 Scroll 内容默认居中两个通用映射问题。逐样本阈值将在更多
稳定设备样本形成后再提交，当前结果不标记为 `passed`。

然后浏览器打开 <http://127.0.0.1:8000>：

1. 在输入框填一句话移动端 UI 需求，例如：
   `一个带顶部搜索框、商品轮播图和底部 Tab 导航的电商首页`
2. 点击 **生成对比**。
3. 每张卡片会实时显示当前阶段、⏱ 耗时和最近的生成日志。先完成的模型
   会立即显示手机框预览，其他模型继续在原卡片中运行。
4. 每张卡片可 **复制 HTML** 或 **新标签打开** 单独预览；开启 ArkUI 元数据后，
   通过校验的移动端结果还可以下载带固化计算样式的完整 HarmonyOS 工程。

> 生产部署可改用 `uvicorn app:app --host 0.0.0.0 --port 8000`，并加 `--workers`
> 或反向代理。开发调试可加 `--reload`。

---

## 实现要点

### 并行调用

`app.py` 的 `/api/generate` 通过 `asyncio.create_task` 同时调度所有模型，
再用请求内 `asyncio.Queue` 汇流阶段事件和最终结果。模型的同步 SDK 请求通过
`asyncio.to_thread` 执行，从而真正并发。`progress` 事件只包含固定生命周期摘要
与单调耗时，不包含模型原始 reasoning。返回的 `total_seconds` 是并行墙钟时间
（≈最慢模型耗时）。

### 同屏渲染

每个模型返回的 HTML 经 `extract_html`（提取围栏代码块）后，通过
`<iframe srcdoc=... sandbox="allow-scripts allow-forms allow-modals allow-popups">`
渲染。`sandbox` 让每个模型的 CSS/JS 互相隔离，保证对比公平，且不影响父页面。

### 移动端聚焦

Prompt（`uibench/prompts.py`）要求：单一完整 HTML 文档、系统注入的 Tailwind
Theme Preset、按 ~390px 移动视口设计。除明确允许的 CDN 和模型通过工具获取的
Unsplash 图片外，禁止自行编造或引入其他远程资源。

---

## 测试

测试套件完全离线 —— 用 LangChain 的 `FakeListChatModel` 替换真实模型，
通过 FastAPI `TestClient` 端到端验证页面与 `/api/generate` 接口。

```bash
python -m pytest tests/ -q
```

覆盖：数据模型校验、HTML 代码块提取、首页 HTML、生成接口、ArkUI 契约同步、
Component Manifest → Screen IR、浏览器快照、资源物化、Node 桥接和导出接口。

---

## 扩展

- **加模型**：在 `config/models.yaml` 追加一条 `provider`/`id`/`name`，无需改代码。
- **加供应商**：在 `uibench/models.py` 的 `build_chat_model` 增加分支，并在
  `uibench/schemas.py` 的 `Provider` 字面量、`config/settings.py` 加入对应字段。
- **改 Prompt**：直接编辑 `uibench/prompts.py`，所有模型共用同一条 Prompt 以
  保证公平对比。
