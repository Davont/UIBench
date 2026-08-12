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
- **多风格主题 Token**：移动端新生成结果使用统一的语义 Design Token，同一份 HTML
  可以在 HarmonyOS、Spotify、Netflix、Notion 之间迁移，并切换白天/黑夜。
- **AI 可选真实图片**：模型可按需调用本地 Unsplash MCP 搜图，获取结果后再生成
  HTML；不需要图片或工具失败时自动使用 Token 占位，不影响页面生成。

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
├── tools/
│   └── arkui-export.mjs       # html-to-arkui JSON 子进程桥
├── config/
│   ├── __init__.py
│   ├── settings.py            # 读取 models.yaml 的运行参数
│   └── models.yaml            # 唯一配置文件（端点+key+模型+参数）
├── uibench/
│   ├── __init__.py
│   ├── schemas.py             # pydantic 数据模型
│   ├── models.py              # LangChain 聊天模型工厂
│   ├── image_tools.py         # 跨供应商图片规划 + Unsplash MCP 客户端
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

## Unsplash MCP 图片接入（可选）

UIBench 使用社区项目
[`hellokaton/unsplash-mcp-server`](https://github.com/hellokaton/unsplash-mcp-server)
执行搜图。MCP 通过 stdio 运行，**无需手动常驻启动**：当 OpenAI 兼容模型发起
`search_photos`，或其他供应商命中明确的图片需求时，UIBench 会自动启动子进程、搜图、回传结果，
调用结束后自动退出。

```bash
# 1. 把 MCP 安装在已忽略的本地目录
git clone https://github.com/hellokaton/unsplash-mcp-server.git \
  .mcp/unsplash-mcp-server
uv sync --project .mcp/unsplash-mcp-server

# 2. 在项目根目录 .env 中写入 Unsplash Access Key
UNSPLASH_ACCESS_KEY=your_access_key
```

然后在 `config/models.yaml` 的 `options` 中开启：

```yaml
image_tools_enabled: true
image_tool_timeout: 90
image_tool_max_assets: 6
```

启动 UIBench 后，普通页面由模型判断是否需要摄影图片；商城、餐饮、酒店等图片密集
场景会由应用强制建立图片槽位。完整链路是：

```text
用户需求 → 模型/应用规划图片槽位 → UIBench 启动 MCP → Unsplash 批量搜索
         → 同轮模型共享图片库 → 模型输出 HTML → 使用不足时自动修复一次
```

UIBench 只接受 `images.unsplash.com` 的 HTTPS 图片。每个模型最多发起一次
`search_photos` 工具调用，但可在一次调用中按具名视觉槽位批量搜索最多
`image_tool_max_assets` 张图片。同一次对比运行会复用相同批次，避免五个模型重复消耗
Unsplash 配额；模型必须把返回图片用于对应槽位，并显示带链接的摄影师 / Unsplash
署名。需求中明确写出的数量（如“生成 5 张肖像图”）会直接成为槽位数量，并受
`image_tool_max_assets` 上限约束。Access Key、
MCP 目录和真实模型配置均被 Git 忽略，不会提交到 fork 仓库。

---

## 用法

```bash
python app.py
```

### 移动端多品牌风格 / 明暗主题

移动端生成 Prompt 要求模型使用 `dt-*` 语义类，例如：

```html
<main class="dt-bg-canvas dt-text-primary dt-font dt-p-page">
  <section class="dt-bg-surface dt-rounded-card dt-p-card">
    <label class="dt-bg-component-subtle dt-rounded-control">
      <input class="dt-text-primary dt-placeholder-secondary" placeholder="搜索" />
    </label>
    <button class="dt-bg-primary dt-text-on-primary dt-focus dt-interaction-hover dt-interaction-pressed">
      继续
    </button>
    <span class="dt-bg-accent dt-text-on-accent dt-rounded-pill">辅助强调</span>
  </section>
</main>
```

UIBench 在渲染时注入 `/design-tokens.css`。根节点通过
`data-token-theme="harmonyos|spotify|netflix|notion"` 选择风格，
通过 `data-theme="light|dark"` 选择明暗模式。页面上的主题按钮只重新渲染当前
iframe，不会再次请求模型，因此适合直接对比风格迁移效果。

Token 源文件位于 `uibench/design_tokens/tokens.json`；四个风格必须实现相同的
语义字段，而且各自的 `light` 与 `dark` 字段必须完全一致，应用启动和测试时会校验。
`GET /api/design-tokens` 可查看原始 Token，
`GET /design-tokens.css` 可查看转换后的 CSS Variables 与语义工具类。

从 v6 起，不透明页面层级使用 `dt-bg-layer-secondary` / `dt-bg-layer-tertiary`，
搜索框和弱按钮等组件填充使用 `dt-bg-component-subtle` /
`dt-bg-component-secondary`；组件轮廓与列表分割线分别使用
`dt-border-outline` 和 `dt-border-divider` / `dt-divide`，避免用同一个灰色值承担不同语义。

> 旧日志中的 HTML 在引入本功能前使用了硬编码 Tailwind 颜色类。UIBench 会通过兼容层
> 映射常见的中性色、边框、主色和状态色，因此可以进行基础风格切换，但不能保证完整
> 迁移。重新生成且使用 `dt-*` 合约的页面才具备完整主题能力。

### 可选 ArkUI 结构导出

移动端模式可勾选“生成 ArkUI 可导出元数据”。开启后，模型只使用当前
`html-to-arkui` 公共契约已支持的 10 个组件：`Column`、`Row`、`Stack`、
`Scroll`、`Text`、`Span`、`Image`、`SymbolGlyph`、`Divider`、`Button`。
`List`、`Grid`、表单输入等规划组件暂不允许导出。

转换器已作为包含全部运行依赖的固定 `.tgz` 放在
`vendor/html-to-arkui/`，安装 UIBench 时执行：

```bash
npm ci --ignore-scripts --offline
```

UIBench 默认只读取根目录 `node_modules/@local/html-to-arkui`，不依赖兄弟仓库，也不需要
访问 npm registry。转换器开发者可以用 `HTML_TO_ARKUI_ROOT` 显式覆盖到本地源仓库；
部署环境不应设置该变量。生成结果通过组件校验后，卡片会显示“下载鸿蒙工程”。
也可以直接调用：

```text
POST /api/arkui/export
{
  "html": "...",
  "page_name": "GeneratedPage",
  "mode": "annotated"
}
```

当前版本已完成 Component Manifest → 固定 390×844 浏览器快照 → Screen IR v2 →
ArkTS → 完整 HarmonyOS 工程链路。浏览器快照会固化当前主题的 computed style、bbox 和可见状态，
并在 CORS 允许时读取页面已经渲染的 PNG/JPEG/GIF/WebP 图片和简单背景图。后端按内容
校验、去重，输出 `resources/base/media` 和 `$r('app.media.*')` 绑定；它不会主动访问网络。
缺节点、资源抓取失败或包含阴影、transform、filter、复杂背景、非均匀边框等能力时返回
`lossy`。下载 ZIP 是 DevEco Studio 6.0.2 / HarmonyOS SDK 6.0.2（API 22）的单模块 Stage
工程，包含应用配置、UIAbility、页面路由、Hvigor 配置和资源。生成器及真实导出样例已通过
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
   通过校验的移动端结果还可以下载结构版 ArkTS。

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

Prompt（`uibench/prompts.py`）强制：单一完整 HTML 文档、Tailwind + Design
Token、按 ~390px 移动视口设计。除明确允许的 CDN 和模型通过工具获取的
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
