# UIBench 单次生成给模型发了什么

记录一次移动端生成里，UIBench 实际发给模型、以及发给图片来源的请求内容。所有
数据来自真实拦截，不是从代码推导的：以 `帮我生成一个播放器 首页` 为输入，模型
`doubao-seed-2-1-turbo-260628`，图片来源为本地离线图库；在线图源那一节的 HTTP
参数在 MCP 自身环境内单独拦截取得。

一次生成**最多两次**请求模型。第二次是否发生，取决于模型有没有调用 `search_photos`
工具。两次请求的 `system` 与 `user` 消息**完全一致**，第二次只是在消息数组尾部追加
了工具调用与工具结果。

---

## 第 1 次请求

### 消息

| # | role | 长度 | 内容 |
|---|------|------|------|
| 0 | system | 9048 字 | `uibench/prompts.py` 的 `SYSTEM_MOBILE` |
| 1 | user | 15 字 | `需求：帮我生成一个播放器 首页` |

`user` 消息只是把原始输入套进模板，没有任何改写、扩写或需求补全：

```94:99:uibench/prompts.py
MOBILE_GENERATION_PROMPT = ChatPromptTemplate(
    messages=[
        ("system", SYSTEM_MOBILE),
        ("human", "需求：{prompt}"),
    ],
)
```

`system` 由五段拼成，按出现顺序及在字符串中的起始位置：

| 段落 | 起始偏移 | 来源 |
|------|---------|------|
| 开场角色设定 | 0 | `SYSTEM_MOBILE_BASE` |
| 【输出规范】 | 110 | `SYSTEM_MOBILE_BASE` |
| 【Design Token 合约：多品牌风格 × 白天 / 黑夜】 | 1823 | `MOBILE_TOKEN_INSTRUCTIONS` |
| 【ArkUI 可导出组件元数据合约】 | 4111 | `MOBILE_ARKUI_METADATA_INSTRUCTIONS` |
| 【设计要求】 | 8291 | `SYSTEM_MOBILE_DESIGN_REQUIREMENTS` |
| 【交付格式】 | 8745 | `SYSTEM_MOBILE_DESIGN_REQUIREMENTS` |

ArkUI 那一段只在开启 ArkUI 导出时加入。关闭导出时走
`MOBILE_GENERATION_PROMPT_WITHOUT_ARKUI`，system 从 9048 字降到 4868 字。

### 请求参数

```json
{
  "model": "doubao-seed-2-1-turbo-260628",
  "temperature": 0.0,
  "max_tokens": 16384,
  "extra_body": { "thinking": { "type": "disabled" } },
  "tools": ["search_photos"],
  "tool_choice": "auto"
}
```

`thinking.disabled` 来自 `config/models.yaml` 的 `reasoning_effort: none`。
`tool_choice` 在有强制配图要求时是 `required`，否则是 `auto`。

### 携带的工具定义

```json
{
  "type": "function",
  "function": {
    "name": "search_photos",
    "description": "Search the curated photo library for multiple named visual slots in one call. When a UI contains a hero plus product/content cards, request a separate slot for each major visible photo (for example hero-banner, wireless-headphones, smartwatch). Use concise English queries. Do not call for icons, charts, decorative gradients, or when photography is unnecessary.",
    "parameters": {
      "type": "object",
      "properties": {
        "requests": {
          "type": "array",
          "minItems": 1,
          "maxItems": 8,
          "items": {
            "type": "object",
            "properties": {
              "slot": { "type": "string" },
              "query": { "type": "string" },
              "orientation": { "enum": ["portrait", "landscape", "squarish"] },
              "color": {
                "enum": ["black_and_white", "black", "white", "yellow", "orange",
                         "red", "purple", "magenta", "green", "teal", "blue"]
              }
            },
            "required": ["slot", "query"],
            "additionalProperties": false
          }
        }
      },
      "required": ["requests"],
      "additionalProperties": false
    }
  }
}
```

---

## 第 2 次请求

只有模型在第 1 次调用了 `search_photos`，或者该 prompt 有强制配图要求时才发生。

### 消息

| # | role | 长度 | 内容 |
|---|------|------|------|
| 0 | system | 9048 字 | **与第 1 次逐字相同** |
| 1 | user | 15 字 | **与第 1 次逐字相同** |
| 2 | assistant | 0 字 | `content` 为空，只带 `tool_calls` |
| 3 | tool | 2653 字 | 图库返回的 JSON |

### 请求参数的唯一变化

`tool_choice` 由 `auto` 变为 `none`，锁死工具，防止模型再搜一轮。其余参数
（`model` / `temperature` / `max_tokens` / `extra_body`）与第 1 次相同。

### 消息 2：模型自己拟的搜图请求

```json
{
  "requests": [
    { "slot": "hero-banner",  "query": "music concert stage lights neon purple blue",
      "orientation": "landscape", "color": "purple" },
    { "slot": "playlist-1",   "query": "lofi chill beats album cover",
      "orientation": "squarish", "color": "purple" },
    { "slot": "playlist-2",   "query": "jazz night city album cover",
      "orientation": "squarish", "color": "blue" },
    { "slot": "playlist-3",   "query": "electronic dance music album cover",
      "orientation": "squarish", "color": "magenta" },
    { "slot": "playlist-4",   "query": "acoustic folk guitar album cover",
      "orientation": "squarish", "color": "orange" },
    { "slot": "now-playing",  "query": "vinyl record music album",
      "orientation": "squarish", "color": "teal" }
  ]
}
```

搜什么图完全由模型自己决定，UIBench 不干预 —— 除非模型违反批量契约
（`_has_named_photo_batch` 判定 slot 不足或重名），此时应用会用
`_fallback_photo_requests` 生成的确定性计划替换掉模型的查询。

### 消息 3：图库回给模型的结果

```json
{
  "photos": [
    {
      "id": "f2b2pdbfH6U",
      "slot": "hero-banner",
      "query": "music concert stage lights neon purple blue",
      "category": "life",
      "description": "Sunrise over the rooftops of the city",
      "urls": {
        "small": "/gallery/life/f2b2pdbfH6U-small.jpg",
        "regular": "/gallery/life/f2b2pdbfH6U-regular.jpg"
      },
      "width": 1080,
      "height": 864,
      "photographer": "Brigitte Elsner",
      "photographer_url": ""
    }
  ],
  "usage_rules": [
    "Use only a returned urls.regular or urls.small URL; never invent a URL.",
    "Each photo.slot is the exact page slot it belongs to; do not swap unrelated assets.",
    "If a returned slot represents a visible product/content card, render its photo in that card instead of an icon or empty placeholder.",
    "If no photo fits, use a token-controlled placeholder instead."
  ]
}
```

上面只列了 6 张中的第 1 张，其余结构相同。URL 是本地路径，由 UIBench 自己的
`/gallery/...` 路由提供，不走外网。

---

## 什么时候只有一次请求

`_minimum_photo_slots(prompt_text)` 决定这个 prompt 是否**强制**配图：

| 命中条件 | 强制槽位数 |
|---------|-----------|
| 命中"不要图片"类表述 | 0 |
| prompt 里写明张数（如"4 张图"） | 该数字，上限 8 |
| 命中商品类关键词 | 4 |
| 命中图集类关键词 | 6 |
| 命中泛视觉关键词 | 2 |
| 都没命中 | 0 |

`帮我生成一个播放器 首页` 的结果是 **0**，即不强制。这种情况下搜不搜图纯由模型
自主判断：本次 Doubao 主动搜了，若某个模型判断不需要照片，它就只有一次请求，
整个流程到此结束。

强制槽位数大于 0 时，即使模型没调工具，应用也会用兜底计划搜图并追加第二次请求
（此时走的是 `assistant` + `user` 两条消息，而不是 `tool_calls` + `tool`）。

---

## 在线搜索（`image_source: unsplash`）每次发出什么

模型侧完全无感：`search_photos` 的工具定义、tool 消息的 JSON 形状在两种图源下
一模一样。差异全部发生在 UIBench 内部。

### 调用形态

UIBench 启动一个 MCP 子进程（stdio），在**同一个 session** 里对 6 个槽位
**顺序串行**循环，不做并发，也不打包成一次批量请求。

```
启动 .mcp/unsplash-mcp-server/.venv/bin/python server.py
  └─ session.call_tool("search_photos", {...})   × 6，逐个串行
```

整个 session 受 `options.image_tool_timeout`（当前 90 秒）约束。

### 每次发给 MCP 的输入

就是模型那条 request **去掉 `slot` 字段**。`slot` 仅留在 UIBench 本地用于回填，
不会发给图源：

| # | slot（本地保留） | 发给 MCP 的 tool_args |
|---|-----------------|----------------------|
| 1 | hero-banner | `{"query": "music concert stage lights neon purple blue", "per_page": 2, "orientation": "landscape", "color": "purple"}` |
| 2 | playlist-1 | `{"query": "lofi chill beats album cover", "per_page": 2, "orientation": "squarish", "color": "purple"}` |
| 3 | playlist-2 | `{"query": "jazz night city album cover", "per_page": 2, "orientation": "squarish", "color": "blue"}` |
| 4 | playlist-3 | `{"query": "electronic dance music album cover", "per_page": 2, "orientation": "squarish", "color": "magenta"}` |
| 5 | playlist-4 | `{"query": "acoustic folk guitar album cover", "per_page": 2, "orientation": "squarish", "color": "orange"}` |
| 6 | now-playing | `{"query": "vinyl record music album", "per_page": 2, "orientation": "squarish", "color": "teal"}` |

`per_page` 由 `image_search_requests` 固定为 2（模型未传时的默认值），多取一个
候选是为了在批次内避开重复命中。

### MCP 转出的实际 HTTP 请求

在 MCP 自身环境内 patch `httpx.AsyncClient` 拦截所得：

```
GET https://api.unsplash.com/search/photos
params  = {"query": "music concert stage lights neon purple blue",
           "page": 1, "per_page": 2, "order_by": "relevant",
           "color": "purple", "orientation": "landscape"}
headers = {"Accept-Version": "v1", "Authorization": "Client-ID <key>"}
timeout = 30.0
```

`page: 1` 与 `order_by: "relevant"` 是 `server.py` 内部补的固定值，UIBench 不传。

### 单模型一次生成的 Unsplash 请求数

| 阶段 | 请求 | 次数 |
|------|------|------|
| MCP 工具调用 | `session.call_tool("search_photos")` | 6 |
| 图片搜索 | `GET /search/photos` | 6 |
| 元数据补全 | `GET /photos/{id}` | 0 |
| 下载追踪 | `GET download_location` | ≤ 6 |

元数据补全为 0：该 MCP server 返回的对象已含 `photographer`、`photographer_url`、
`download_location`，`_enrich_photo_metadata` 的 `has_metadata` 检查直接跳过。
下载追踪只对真正渲染进最终 HTML 的图发出，故为上限值。

**单模型上限 12 次，5 模型一轮上限 60 次**，而 Unsplash demo key 的额度是
50 次/小时 —— 一轮即可打满。

### 缓存为什么通常不生效

`RunImageBatchCache` 的 key 是整个 requests 数组的 JSON（含 `query` /
`orientation` / `color` 全部字段）加 `max_requests` 与 `source`。模型自主搜图时
各家措辞不同，几乎不可能逐字相同，缓存基本不命中。

只有在触发强制配图、且模型未给出合规批量、从而走 `_fallback_photo_requests`
确定性计划时，各模型的 requests 才会完全一致，整轮才降到 12 次。

### 与本地图库的行为差异

| | `local` | `unsplash` |
|---|---------|-----------|
| 进程 | 无，进程内查表 | 每次生成拉起一个 MCP 子进程 |
| 网络 | 无 | 每槽位 1 次 HTTPS |
| 耗时 | 毫秒级，一次性返回 | 6 次串行请求 |
| 进度回调 | 只报一次 `6/6` | 每完成一个槽位报一次 |
| 配额 | 无 | 计入 50 次/小时 |
| tool 消息体积 | 2653 字符 / 839 token | 5701 字符 / 2398 token |

因为本地图库瞬间返回，进度会直接跳到 `6/6` 并停在那里，此后的等待全部是模型
在生成 HTML，与图片检索无关。

### 上下文体积差在哪

同样 6 个槽位，在线模式喂给模型的 tool 消息是本地的 2.15 倍（字符）/ 2.86 倍
（token）。差距几乎全部来自图片 URL：

| | 本地 | 在线 |
|---|------|------|
| 单个 `regular` URL | 37 字符 | 227 字符 |
| 单张图两个 URL 合计 | 72 字符 | 453 字符 |
| 单张 photo 对象 | 375 字符 | 884 字符 |

在线 URL 携带 `ixid` 签名串（形如 `?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3wxMDI0…&ixlib=rb-4.1.0&q=80&w=1080`），
本地只是 `/gallery/<分类>/<id>-regular.jpg`。token 倍数高于字符倍数，是因为
`ixid` 属于 base64 随机串，分词器几乎每两三个字符切一刀。

模型可见的字段仅差两个且体积可忽略：本地多 `category`，在线多 `unsplash_url`。
`download_location` 虽为在线独有，但 `image_tool_result_for_model` 会在发送前
剔除，不进上下文。

token 数按 `cl100k_base` 估算，各模型自身分词器的绝对值不同，倍数关系一致。

---

## 涉及的代码位置

| 位置 | 作用 |
|------|------|
| `uibench/prompts.py` `MOBILE_GENERATION_PROMPT` | system + user 模板 |
| `app.py` `_generate_one` | 整个两次请求的流程 |
| `app.py` `_minimum_photo_slots` | 强制配图判定 |
| `app.py` `_has_named_photo_batch` / `_fallback_photo_requests` | 批量契约校验与兜底计划 |
| `app.py` 内 `final_kwargs` 构造 | 第二次请求的参数覆盖 |
| `app.py` `RunImageBatchCache` | 同一轮内相同图片批次的去重 |
| `uibench/image_tools.py` `image_search_requests` | 归一化槽位、固定 `per_page` |
| `uibench/image_tools.py` `_call_unsplash_requests` | MCP 会话与逐槽位串行循环 |
| `.mcp/unsplash-mcp-server/server.py` | 拼装真正的 Unsplash HTTP 请求 |

---

## 自行复现

拦截 `root_client.chat.completions.create`，记录每次的 `kwargs` 后在第二次抛异常
提前中止，避免等待完整 HTML 生成：

```python
import asyncio, json
import app as A
from uibench.models import load_model_registry

captured = []
orig_factory = A.chat_model_for

def patched_factory(model_cfg):
    chat = orig_factory(model_cfg)
    rc = chat.root_client
    orig_create = rc.chat.completions.create
    def wrapper(**kwargs):
        captured.append(kwargs)
        if len(captured) >= 2:
            raise RuntimeError("captured both calls")
        return orig_create(**kwargs)
    rc.chat.completions.create = wrapper
    return chat

A.chat_model_for = patched_factory

cfg = next(m for m in load_model_registry() if m.id.startswith("doubao"))
try:
    asyncio.run(A._generate_one(cfg, "帮我生成一个播放器 首页", key="0",
                                run_id="probe", mode="mobile",
                                arkui_export_enabled=True))
except Exception:
    pass

print(json.dumps(captured, ensure_ascii=False, indent=2, default=str))
```

---

## 已知问题：图库语义匹配

本次实测中，模型请求的是演唱会灯光与各类专辑封面，图库实际返回的 6 张图有 5 张
来自 `life` 分类、1 张来自 `travel`，没有一张与音乐相关：

| slot | 模型要的 | 实际拿到的图片描述 | 分类 |
|------|---------|------------------|------|
| hero-banner | music concert stage lights neon purple blue | Sunrise over the rooftops of the city | life |
| playlist-1 | lofi chill beats album cover | A sunny day in our SF apartment | life |
| playlist-2 | jazz night city album cover | a bedroom with a bed and a night stand | travel |
| playlist-3 | electronic dance music album cover | brown wooden table with books on top | life |
| playlist-4 | acoustic folk guitar album cover | flatlay of the open pages of an interiors magazine | life |
| now-playing | vinyl record music album | taken at Coco Bowls in Warsaw | life |

根因是 `tools/gallery_topics.yaml` 目前的分类里没有音乐题材，匹配只能退化为取
最接近的图。改善方式是补充相应类目后重新运行 `python tools/build_gallery.py`。
