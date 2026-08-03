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
- **逐模型容错**：某个模型缺 key 或报错，只在该卡片上显示错误，不影响其他模型。

---

## 项目结构

```
UIBench/
├── README.md                  # 本文档
├── requirements.txt           # 依赖清单
├── app.py                     # FastAPI 应用 + 单页 UI（核心入口）
├── config/
│   ├── __init__.py
│   ├── settings.py            # 读取 models.yaml 的运行参数
│   └── models.yaml            # 唯一配置文件（端点+key+模型+参数）
├── uibench/
│   ├── __init__.py
│   ├── schemas.py             # pydantic 数据模型
│   ├── models.py              # LangChain 聊天模型工厂
│   └── prompts.py             # 移动端 UI 生成 Prompt
└── tests/                     # pytest 套件（无需 API key）
    ├── conftest.py
    ├── test_schemas.py
    ├── test_models.py
    └── test_app.py
```

---

## 工作流程

```
用户在页面输入一句话需求
        │
        ▼
  POST /api/generate  ──────► app.py
        │                          │ asyncio.gather（并行）
        │                          ├── 模型 A ──► 返回 HTML ──► 耗时 tA
        │                          ├── 模型 B ──► 返回 HTML ──► 耗时 tB
        │                          └── 模型 C ──► 返回 HTML ──► 耗时 tC
        │ ◄─────── [{name, html, elapsed, error}, ...] ─────────┘
        ▼
  前端：每个模型一张卡片
   ├── 模型名 + 供应商 + ⏱ 耗时
   └── iframe srcdoc=HTML（手机框渲染）
```

---

## 安装

需要 Python 3.11+（在 3.13 上开发）。

```bash
# 1.（可选）创建虚拟环境
python -m venv .venv
.\.venv\Scripts\activate          # Windows
# source .venv/bin/activate       # macOS / Linux

# 2. 安装依赖
pip install -r requirements.txt

# 3. 编辑唯一配置文件 config/models.yaml，填入端点和 key（默认已预配 8 个模型）
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

## 用法

```bash
python app.py
```

然后浏览器打开 <http://127.0.0.1:8000>：

1. 在输入框填一句话移动端 UI 需求，例如：
   `一个带顶部搜索框、商品轮播图和底部 Tab 导航的电商首页`
2. 点击 **生成对比**。
3. 等待并行返回，页面下方会出现多张卡片，每张卡片含模型名、⏱ 耗时，
   以及一个手机框渲染该模型生成的 HTML。
4. 每张卡片可 **复制 HTML** 或 **新标签打开** 单独预览。

> 生产部署可改用 `uvicorn app:app --host 0.0.0.0 --port 8000`，并加 `--workers`
> 或反向代理。开发调试可加 `--reload`。

---

## 实现要点

### 并行调用

`app.py` 的 `/api/generate` 用 `asyncio.gather` 同时调度所有模型，每个模型
通过 `asyncio.to_thread` 调用 LangChain 的同步 `invoke`，从而真正并发。
返回的 `total_seconds` 是并行墙钟时间（≈最慢模型耗时）。

### 同屏渲染

每个模型返回的 HTML 经 `extract_html`（提取围栏代码块）后，通过
`<iframe srcdoc=... sandbox="allow-scripts allow-forms allow-modals allow-popups">`
渲染。`sandbox` 让每个模型的 CSS/JS 互相隔离，保证对比公平，且不影响父页面。

### 移动端聚焦

Prompt（`uibench/prompts.py`）强制：单一自包含 HTML 文档、内联 CSS/JS、
禁止外部网络请求、按 ~390px 移动视口设计。配合前端手机框样式，效果接近真机。

---

## 测试

测试套件完全离线 —— 用 LangChain 的 `FakeListChatModel` 替换真实模型，
通过 FastAPI `TestClient` 端到端验证页面与 `/api/generate` 接口。

```bash
python -m pytest tests/ -q
```

覆盖：数据模型校验、HTML 代码块提取、首页 HTML、生成接口（含错误处理）。

---

## 扩展

- **加模型**：在 `config/models.yaml` 追加一条 `provider`/`id`/`name`，无需改代码。
- **加供应商**：在 `uibench/models.py` 的 `build_chat_model` 增加分支，并在
  `uibench/schemas.py` 的 `Provider` 字面量、`config/settings.py` 加入对应字段。
- **改 Prompt**：直接编辑 `uibench/prompts.py`，所有模型共用同一条 Prompt 以
  保证公平对比。
