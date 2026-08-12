# UIBench ArkUI export adapter

该目录实现 UIBench 专属的 HTML 元数据适配层。UIBench 负责理解
`data-component` 等定制标注，再生成标准 Screen IR v2；
`html-to-arkui` 只负责平台无关的契约校验、通用 HTML 转换和 ArkTS 渲染。

## 当前文件

- `component_registry.json`：UIBench 的 35 个 HTML 标注 key、业务分类和降级关系。
- `renderer_contract.json`：锁定的 `html-to-arkui` 公共组件契约快照。
- `symbol_registry.json`：从本机 DevEco SDK 固化的 3778 个系统 Symbol 资源名，
  以及经过核对的 Lucide 图标对照表。
- `lucide_registry.json`：从固定版本 lucide npm 包固化的图标名与别名目录，
  用于映射表校验和覆盖率审计。
- `components.py`：校验两层契约，只把渲染器真实支持的组件暴露给 Prompt。
- `symbols.py`：把 `data-symbol` 解析成真实存在的系统资源名。
- `metadata.py`：提取组件标注，生成 `uibench-component-manifest` 和导出诊断。
- `snapshot.py`：校验浏览器快照，并把白名单 computed style 映射到 Screen IR styles。
- `resources.py`：校验浏览器捕获的图片字节，去重并生成完整 HarmonyOS 工程 ZIP。
- `screen_ir.py`：把有效的 UIBench Component Manifest 转成标准 Screen IR v2。
- `exporter.py`：通过受限 JSON 子进程调用 `tools/arkui-export.mjs`。
- `visual_regression.py`：无额外图像依赖的 PNG 校验、像素指标和差异图生成。
- `regression.py`：版本化回归样本、工程准备、产物摘要和截图比较。

## 当前可导出组件

当前只允许：

```text
column, row, stack, scroll, text, span,
image, symbol, divider, button, list, list-item, grid, grid-item
```

`list` 期望 `list-item` 子节点，`list-item` 期望出现在 `list` 内且最多包含一个
已标注组件子节点；条目间距写在 `list` 上，渲染为 `List({ space: N })`。这两条
偏差不阻断导出：`list` 里的普通组件会被包进一层生成的 `ListItem`，落单的
`list-item` 按 `column` 导出（见下方偏差表）。

ArkUI 的 `List` 默认纵向排列，所以导出会按 computed layout 把 `list` 的主轴写成
`listDirection`，渲染为 `.listDirection(Axis.Horizontal)` 或 `Axis.Vertical`；
`space` 也取该主轴上的 gap（横向读 `column-gap`，纵向读 `row-gap`）。和 `row`／
`column` 一样，浏览器没有把 `list` 排在单一主轴上（例如 `row-reverse`）时按
`UIBENCH_ARKUI_LAYOUT_METADATA_CONFLICT` 阻断，不会静默倒向默认方向。

`grid` 期望 `grid-item` 子节点且节点必须真的以 `display: grid` 布局，否则按
`UIBENCH_ARKUI_LAYOUT_METADATA_CONFLICT` 阻断；普通组件直接放进 `grid` 会被包进
一层生成的 `GridItem`。轨道模板取 computed 的已用值（浏览器已把作者写的 `fr`
解析成像素）：等宽轨道只有在连同 `gap` 恰好铺满容器内容区时才回写成每轨 `1fr`
（此时无损且在别的屏宽下保持自适应）——ArkUI 会把 `fr` 摊满整条轴，浏览器留有
空白的固定轨道（如 390px 容器里的 `100px 100px`）若写成 `1fr` 会被静默拉伸，
因此这类轨道与不等宽轨道一样冻结成捕获时的精确 `vp` 值；`gap` 落成
`columnsGap` / `rowsGap`。ArkUI 的 `List` / `Grid` 没有 `justifyContent` /
`alignItems` 修饰符，条目在设备上始终从主轴起点排布，捕获到 `center`、
`space-between` 等其他分布时记 lossy 告警，不会静默改变内容位置。ArkUI 的
`GridItem` 只支持按行序自动放置，所以 `grid-auto-flow` 不是 `row`、或格子带显式
`grid-row/column` 行号与 `span` 时分别按 `UIBENCH_ARKUI_LAYOUT_METADATA_CONFLICT`
与 `UIBENCH_ARKUI_GRID_PLACEMENT_UNSUPPORTED` 阻断，不会导出一个放置顺序不同的
网格。

`checkbox`、`text-input`、`swiper` 等仍保留在 UIBench 规划词汇中，
但会被标记为 `rendererSupported: false`，不能进入当前导出链路。渲染器扩展
公共契约后，UIBench 才能同步开放相应 Prompt 能力。

## HTML 标注示例

```html
<main data-node-id="page" data-component="scroll">
  <section data-node-id="page.content" data-component="column"
           class="flex flex-col">
    <p data-node-id="page.title" data-component="text">标题</p>
    <button data-node-id="page.submit" data-component="button"
            data-action="submit">提交</button>
  </section>
</main>
```

- `data-node-id` 是稳定且全局唯一的小写路径。
- `data-component` 只表达基础结构或控件类型。
- `data-ui-role`、`data-repeat`、`data-item-key` 和 `data-action` 保留业务语义。
- 图标只需要 `data-lucide`，`data-symbol` 由导出侧解析，写了也只作为回退。
- `data-component="span"` 只在父节点也是 `text` 时成立，它与 HTML 的 `<span>` 标签无关。
  独立成块的文字一律标 `text`。`text` 里混排的直接文本（如 `共 <span>3</span> 台`）
  会按文档顺序导出为多个 `Span`：ArkUI 的 `Text` 有 `Span` 子组件时不渲染自身
  content，所以外围文字必须自己成为 `Span` 才不会丢。
- 根节点要用 `min-h-screen` 铺满视口。画布背景写在 `<body>` 还是根节点上都可以。
- 旧 HTML 可以不带标注，并继续使用通用 `generic` 转换模式，但不能保证语义。

## 导出侧消化的标注偏差

标注是模型的声明，浏览器 computed layout 是证据。证据能唯一确定结果时，导出按证据走，
而不是把责任推回 Prompt。可以少写的合约，就不要写进 Prompt。

诊断分三档：`error` 阻断导出；`warning` 表示 ArkUI 工程已经无法还原截图；`notice` 表示
标注被改读了但渲染结果不变。只有 `warning` 会把 `readiness` 降为 `lossy`，所以「有损」
这个结论始终对应真实的视觉差异，不会被结构性改写稀释。

| 偏差 | 处理 | 诊断 | 档位 |
| --- | --- | --- | --- |
| 图标资源名 | 先验证 `data-lucide` 在固定 Lucide 目录中，再两级解析，`data-symbol` 仅作回退 | — | — |
| `data-lucide` 不是 Lucide 图标 | 浏览器本来就渲染不出图标，退化成等大空占位，不查鸿蒙同名资源 | `ARKUI_LUCIDE_ICON_UNKNOWN` | warning |
| 画布背景留在 `<body>` | 提升到 ArkUI 页面根 | — | — |
| 单槽容器塞了多个子节点 | 生成继承其方向/对齐/间距的包裹层 | `ARKUI_CONTENT_WRAPPED_FOR_SINGLE_SLOT` | notice |
| `list` 直接子节点不是 `list-item` | 每个条目包进一层生成的 `ListItem`，几何不变 | `ARKUI_LIST_CHILD_WRAPPED_AS_ITEM` | notice |
| `grid` 直接子节点不是 `grid-item` | 每个格子包进一层生成的 `GridItem`，几何不变 | `ARKUI_GRID_CHILD_WRAPPED_AS_ITEM` | notice |
| `list-item` 不在 `list` 内 | 按 `column` 导出 | `ARKUI_LIST_ITEM_PROMOTED_TO_COLUMN` | notice |
| `Row`/`Column` 与 computed 方向不符 | 按浏览器实际方向导出 | `UIBENCH_ARKUI_LAYOUT_FOLLOWS_BROWSER` | notice |
| `span` 不在 `text` 内 | 按 `text` 导出 | `ARKUI_SPAN_PROMOTED_TO_TEXT` | notice |
| `text` 直接包含 `symbol`，且 computed layout 是普通 flex 行/列 | 父节点按实际方向改为 `Row`/`Column`，原始文字片段生成独立 `Text` | `ARKUI_TEXT_SYMBOL_LAYOUT_ADAPTED` | notice |
| `text` 直接包含 `symbol`，但没有普通 flex 行/列证据 | 不猜测 inline、grid 或 reverse 布局 | `UIBENCH_TEXT_SYMBOL_LAYOUT_CONFLICT` | error |
| `button` 唯一的直接 `text` 子组件漏写 `data-node-id` | 预览和快照前按父 ID 生成 `.label`，冲突时追加序号 | `ARKUI_NODE_ID_GENERATED` | notice |
| 鸿蒙只有近似字形 | 按人工核对的近似表替换，字形相似但非原图标 | `ARKUI_SYMBOL_APPROXIMATED` | warning |
| 鸿蒙没有该图标 | 退化成等大空占位，布局不变但少一个图标 | `ARKUI_SYMBOL_UNAVAILABLE` | warning |
| `image` 没有 `src` | 按 `column` 导出，图片位置变成空容器 | `ARKUI_IMAGE_SRC_MISSING` | warning |

仍然阻断的是证据也救不回来的情况：叶子组件挂了子节点、渲染器契约里没有的组件、缺少
`data-node-id`（浏览器快照按该属性索引，没有它就没有这个节点的任何证据）、标注为
`row`/`column` 却渲染成 `inline`、`row-reverse` 等对应不上的布局（未标注 `grid` 的
`display: grid` 同理），以及组件树与真实 DOM 对不上：直接 DOM 父节点不是元数据声明的
父组件时（`UIBENCH_ARKUI_DOM_PARENT_MISMATCH`），未标注的中间 wrapper 无法投影进
ArkUI 布局树；快照缺少父子 provenance 字段时（`UIBENCH_BROWSER_PARENT_PROVENANCE_MISSING`），
组件树无法被验证。

## 平台默认值不对齐的属性

样式映射默认只输出与初始值不同的属性，这依赖两个平台的初始值一致。`Button` 是唯一的例外：
ArkUI 给它自带主题填充色、内边距和 20vp 圆角（API 18 起默认 `ROUNDED_RECTANGLE`，此前是
`Capsule`），而 HTML `<button>` 这三项都是无。于是对 `Button` 来说「零」和「没说」是两种
主张，浏览器实测到的透明、`0` 内边距和 `0` 圆角都会被显式写出（`#00000000` / `padding(0)`
/ `borderRadius(0)`）。少写任何一项，一行本该透明的设置项都会在设备上变成蓝色圆角块。

## 精确表达而非标损的样式

以下 computed style 有 ArkUI 原生的精确形式，按原生形式导出，不再标 `lossy`；括号里
是仍会告警的残余情况：

- `align-items: normal/stretch`（flex 容器）：几何已按 bbox 冻结，拉伸的子项自带容器
  尺寸、定尺寸的子项贴交叉轴起点，映射为 `alignItems(Start)` 即像素等价；不写反而会
  落到 ArkUI 的 Center 默认对齐。
- `text-transform: uppercase/lowercase`：导出文本是冻结的静态字符串，大小写直接烘焙进
  `content`，设备上不会再出现 DOM 原文（`capitalize` 按 UAX#29 分词首字母定题，普通
  字符串变换无法保真，仍告警）。
- `letter-spacing`：`Text` / `Span` 映射为 `letterSpacing()`；带直出文本 label 的
  `Button` 因 ButtonAttribute 没有该修饰符仍告警。其他组件上它不渲染任何自有文本，
  标注的 Text/Span 后代会继承并自行导出，不再误报。
- `white-space: nowrap`、`text-overflow: ellipsis`、`-webkit-line-clamp: N`（`Text`）：
  映射为 `maxLines(1|N)` 加 `textOverflow({ overflow: TextOverflow.Ellipsis })`。
  line-clamp 在浏览器里自带省略号；裸 nowrap 是裁切，与 ArkUI 的默认值一致，不额外
  写省略号。没有行数限制的 ellipsis 在浏览器里也画不出来，不算损失。
- 非均匀边框：按 ArkUI `EdgeWidths` / `EdgeColors` / `EdgeStyles` 分边导出，行分隔线的
  0.5px 底边框不再消失；各边一致的部分仍收敛成标量，贴近手写 ArkTS。残余告警只剩
  ArkUI 没有的线型（`border-style:double` 等）与不支持的颜色语法（`border-color`）。
- `Button` 的 `line-height` / `text-align` / `letter-spacing`：只在 Button 以
  `Button("label")` 直出文本时才可能有损；内容是组件子节点时，这三个属性在浏览器的
  flex 布局里本来就不参与渲染，不再告警。

## span 的唯一合理读法

ArkUI 的 `Span` 在 `Text` 之外没有任何合法形式，因此父节点不是 `text` 的 span 只有一种
读法，就是注册表里已经声明的 `"span": {"fallback": "text"}`。这类节点会按 `text` 导出并
记一条 `ARKUI_SPAN_PROMOTED_TO_TEXT` notice：节点、文本、几何和 computed style 全部保留，
不新增也不删除任何节点，所以它不是有损降级，而是把误标读回唯一成立的语义；保留 notice
级诊断是为了让日志能看见模型标错了。同样的读法适用于 `list` 之外的 `list-item`：`ListItem`
在 `List` 之外没有合法形式，按 `column` 导出并记 `ARKUI_LIST_ITEM_PROMOTED_TO_COLUMN`。
除这两条外，其余 `fallback` 仍然不参与自动降级——它们会改变页面语义。
`text` 内部没有文本的 span 依旧按 `ARKUI_SPAN_CONTENT_MISSING` 阻断。

## text + symbol 的兼容读法

ArkUI `Text` 只能容纳 `Span`，不能容纳 `SymbolGlyph`。模型偶尔会把一个实际使用
`display:flex` 的「图标 + 文字」容器误标成 `text`。元数据分析器会先保留这项可修复意图，
不再立即报 `ARKUI_COMPONENT_CHILD_INVALID`；浏览器快照确认它是普通 `flex` /
`inline-flex` 且方向为 `row` 或 `column` 后，Screen IR 才把父节点改成对应的
`Row` / `Column`。

父节点自己的 DOM 文字片段按原顺序生成独立 `Text`，并复制字体、字号、颜色、行高、字距、
对齐和截断属性；原 `SymbolGlyph` 仍处于同一位置。若同时存在富文本 `Span`，它会成为同级
`Text` 并保留自己的 computed style。普通 block/inline 流、grid、`row-reverse` 和
`column-reverse` 没有唯一等价读法，仍以 `UIBENCH_TEXT_SYMBOL_LAYOUT_CONFLICT` 阻断，
避免把同行内容错误堆成上下两行。

## 缺失节点 ID 的安全修复

`data-node-id` 同时是 HTML、浏览器快照和 Screen IR 的跨层主键，只在后端补值会导致快照找
不到同一节点。因此 UIBench 在生成结果进入预览 iframe 之前执行一次确定性修复。目前只处理
一种没有歧义的结构：拥有合法且全局唯一 ID 的 `button`，恰好只有一个直接元素、没有额外
直接文本，且该元素是漏写 ID 的唯一 `text` 组件子节点。生成值为 `<button-id>.label`；
若该值已被占用，则依次使用
`.label-2`、`.label-3`。命名不读取文案，所以翻译或改字不会改变 ID。

修复后的 HTML 会带 `data-uibench-generated-node-id="button-label"`，元数据报告据此记录
`ARKUI_NODE_ID_GENERATED` notice；预览、快照与导出都使用同一份 HTML。父 ID 缺失、非法或
重复，Text 已写空/非法 ID，Button 有多个直接组件子节点，以及其他无法唯一命名的情况都不
自动猜测，仍由 `ARKUI_NODE_ID_MISSING` / `ARKUI_NODE_ID_INVALID` 阻断。

## 系统 Symbol 资源

`SymbolGlyph` 只渲染系统预置资源，凭空编造的名字能通过任何语法检查，却会在设备上
显示异常。因此 `data-symbol` 不做正则校验，而是解析到一份从本机 DevEco SDK
（HarmonyOS 6.0.2 / API 22）固化的名单：

```bash
python tools/export-symbol-registry.py
```

该工具只读取 SDK 的 `toolchains/id_defined.json`，并保留仓库里已人工核对的
`lucideSymbolMap` 与 `lucideSymbolNearMap`。生成的注册表在写盘前先过运行时
加载器的同一个解析校验（`parse_symbol_registry`），运行时拒绝加载的产物在
这里就直接失败、旧注册表原样保留——包括映射指向本 SDK 不存在的名字、近似
条目被精确条目遮蔽，以及新 SDK 恰好新增了与近似键同名的符号（如新增
`globe`）使 `globe→worldclock` 变成本该直查命中的条目这类刷新才会暴露的
失效。校验只有加载器这一份实现，工具不再手抄规则。

解析以 `data-lucide` 为准，不需要模型写 `data-symbol`：页面不写 `data-lucide` 就渲染不出
图标，所以它是证据，而 `data-symbol` 只是模型对映射关系的猜测。实测同一批页面里模型自己
写的 `data-symbol` 只有 65% 命中真实资源，照 `data-lucide` 查表则是 95%。

解析前先在固化的 Lucide 目录里验证这个名字：页面加载的 CDN 构建渲染不出的
`data-lucide`（如 `person`，Lucide 里叫 `user`）在浏览器截图上本来就没有图标，
即使鸿蒙恰好有同名资源、或模型声明了 `data-symbol`，也不映射——否则设备上会凭空
多出截图里不存在的图标。这类名字按 `ARKUI_LUCIDE_ICON_UNKNOWN` 警告退化成等大
空占位。目录内的名字再做两级解析：先查 `lucideSymbolMap` 里人工核对过的条目，再把
Lucide 的 kebab-case 直接当下划线名查一次 SDK 名单——两个图标库同名的部分不必
手工登记。显式 `data-symbol` 仅在 `data-lucide` 解析失败时作为回退，此时仍会折叠
分隔符与大小写差异（`chevron-right`、`chevron.right` 都归一到 `chevron_right`），
Screen IR 与 ArkTS 始终输出 SDK 拼写。

精确解析（映射表、同名直查、显式 `data-symbol`）都失败时，最后查一张人工核对的
近似表 `lucideSymbolNearMap`（`globe→worldclock`、`badge-check→seal`）：命中则渲染
这个相似字形并记 `ARKUI_SYMBOL_APPROXIMATED` warning——页面不缺图标，但字形不是
原图标，导出如实标记 `lossy`。近似表也没有的（如 `air-vent`、`rocket`）返回
`ARKUI_SYMBOL_UNAVAILABLE` 警告，并按 `"symbol": {"fallback": "column"}` 退化成
等大的空占位：周围布局不变，只是缺一个图标，不会让整页导出失败。要消掉这类警告
就往 `lucideSymbolMap` 或 `lucideSymbolNearMap` 里补一条——补在引擎里，不用动
Prompt。

## Lucide 目录与覆盖率审计

miss 不再只靠导出时踩到才发现。仓库把页面实际加载的那个 Lucide 版本固化成第二本
注册表（`lucide_registry.json`，当前 1.31.0：1767 个规范名 + 254 个仍可渲染的
历史别名），Prompt 中的 CDN 引用也固定为同一版本号，不再使用 `lucide@latest`：

```bash
npm pack lucide@1.31.0 && tar -xzf lucide-1.31.0.tgz
python tools/export-lucide-registry.py --package package
python tools/audit-lucide-coverage.py --out .artifacts/lucide-coverage.json
```

导出工具只 check in JSON，不 vendor tarball，也不给仓库增加 npm 依赖。浏览器按
`toPascalCase` 折叠 `data-lucide` 后查 PascalCase 键，这是唯一无歧义的匹配方向
（`clock-10` 与 `arrow-down-0-1` 使反向转换不可判定），因此名单校验也在
PascalCase 空间进行；规范名、别名以及等价拼写（`arrow-down-01`）都被识别。

审计工具把每个图标按真实解析路径分类为 `reviewed`（人工表命中）、`direct`
（同名直查命中）、`miss-suggested`（有近似建议待人工看）、`miss-none`。测试
钉死 `lucideSymbolMap` 的每个 key 都必须是该目录里可渲染的名字，映射到不存在
的 SDK 资源仍然在加载时直接失败。

登记原则：只有资源名语义无歧义地指向同一对象时才写入精确表（`palette→paintpalette`、
`map-pin→local`、`menu→line_3_horizontal`）；风格差异可接受（`_fill` 仅此一形时
沿用 `bus→bus_fill` 先例），拿不准的留在 miss 清单等下一轮。真缺失但有相似字形的
走近似表 `lucideSymbolNearMap`（23 条，如 `globe→worldclock`、`chevrons-down→
chevron_down`、`more-vertical→more`）：审计里单列 `near` 档，不计入覆盖率，命中时
导出保持 `lossy`。除逐条核对外，还有两类系统性来源：别名继承
（别名与规范名同字形，规范名可解析则别名直接登记，零风险）与词汇对照生成
（`x/check/alert/user/mail` 对应 `xmark/checkmark/exclamationmark/person/envelope`、
`circle-foo` 与 `foo_circle` 语序互换、`foo-off` 与 `foo_slash`），生成的候选仍需
逐条人工核对后写入。几轮审计后精确表从 153 条扩到 315 条，规范图标覆盖
226/1767 → 360/1767，别名覆盖 59/254；条数与覆盖率一律以
`tools/audit-lucide-coverage.py` 的输出为准。长尾主要是车机、医疗、体育等鸿蒙确实
没有对应资源的领域图标。

## 两种输出契约

`metadata.py` 输出的是 UIBench 自定义清单：

```json
{
  "kind": "uibench-component-manifest",
  "manifestVersion": 1,
  "screenIrSchemaVersion": 2
}
```

它不是 Screen IR。只有通过 `screen_ir.py` 适配后才得到：

```json
{
  "schemaVersion": 2,
  "page": {"name": "GeneratedPage"},
  "ui": {"componentName": "Scroll", "meta": {"nodeId": "page"}}
}
```

## 浏览器固化

从页面点击导出时，UIBench 会创建一个不可见的固定 `390×844` sandbox iframe，使用
当前 light/dark 与 Token 主题重新渲染 HTML。快照脚本等待字体、图片和两帧布局稳定，
再回传：

- 每个 `data-node-id` 的 bbox 和可见状态。
- 布局、间距、背景、边框、圆角、文字和图片裁剪等白名单 computed style。
- HTML/body 实际画布的 `canvasBackgroundColor` 与
  `canvasBackgroundImage`；祖先的 display、visibility、opacity 或
  content-visibility 使节点不可见时，后代也会记录为不可见。
- `Divider` 的单侧 solid 边框会映射为原生 `dividerColor`、
  `dividerStrokeWidth`、`dividerVertical`，再生成 ArkUI
  `.color()`、`.strokeWidth()`、`.vertical()`。
- 实际 viewport、主题和 Token 主题。

后端把快照作为不可信输入处理：限制 HTML 为 2 MB、快照为 10000 个节点，并限制
字段长度和枚举，禁止
未知字段、NaN/Infinity 与重复 nodeId。能完整映射且没有其他 warning 时返回
`quality.readiness: ready`。任一 annotated 节点缺少快照项（包括隐藏祖先的后代）时会阻止
导出；隐藏节点和阴影、transform、filter、复杂背景图等无法精确表达的属性会返回 `lossy`。

`Row` / `Column` 是模型对节点的声明，浏览器 computed layout 才是证据，两者冲突时按证据
导出并记一条 `UIBENCH_ARKUI_LAYOUT_FOLLOWS_BROWSER` 警告：`flex` / `inline-flex` 按实际
`flex-direction` 落成 `Row` 或 `Column`（Tailwind 裸写 `flex` 就是 row，这是模型最常标反
的地方），`block` / `inline-block` / `flow-root` / `list-item` 这类正常流按 `Column` 落地，
因为正常流本来就是自上而下堆叠。`grid`、`inline`、`row-reverse` 等 ArkUI 没有对应表达的
布局仍然返回 `UIBENCH_ARKUI_LAYOUT_METADATA_CONFLICT` 阻断。
下载工程的严格路径只接受纯色画布；HTML/body 画布包含背景图或渐变时会返回
`UIBENCH_CANVAS_BACKGROUND_IMAGE_UNSUPPORTED`，不会静默丢弃后继续生成工程。ArkUI 的页面根
背后不再有 body 画布，页面根自己承担整个背景，因此盖住 viewport 的透明根由 Screen IR
直接接过画布颜色，把 `dt-bg-canvas` 写在 `<body>` 上是可以的；根自带不透明颜色时按它
自己的颜色导出。

设备上重现不了画布颜色时拒绝，返回 `UIBENCH_CANVAS_BACKGROUND_ROOT_UNSUPPORTED`：
根上方还有可寻址 wrapper（`canvas-root-has-addressable-wrapper`）、根用半透明色与画布
混合（`canvas-root-is-translucent`）、根没有盖住整个 viewport 导致画布在根之外露出
（`canvas-root-does-not-cover-viewport`）。最后一条对透明根和与画布同色的根同样成立：
Screen IR 只对盖住 viewport 的页面根提升画布颜色，工程窗口背景固定为白
（`HARMONY_WINDOW_BACKGROUND`），所以深色画布配一个 100×100 的透明根会在设备上变成
白屏——只有画布本身就是窗口白时，短根才可以放行。盖住 viewport 但组件不是页面根
白名单（`Column`/`Row`/`Stack`/`Scroll`/`List`/`Grid`）的透明根按
`canvas-root-cannot-inherit-canvas` 拒绝。"盖住 viewport" 判定的是根矩形是否**包含**
viewport，不是尺寸相等：可滚动页面的根一定比 viewport 高。这套判定只有一份实现
（`screen_ir.root_covers_viewport` / `is_viewport_page_root`），导出闸门与 Screen IR
的画布提升、页面根识别共用它，页面根的宽高始终导出为 `100%`。
面向下载的 annotated 导出还要求每个节点实际提交完整的 computed-style 捕获字段集；
模型默认填入的空字符串不算捕获证据。字段缺失时返回
`UIBENCH_BROWSER_SNAPSHOT_INCOMPLETE`，其中 `details.reason` 固定为
`computed-style-capture-fields-missing`，`details.missingFields` 使用浏览器协议字段名。
顶层 provenance 字段 `directParentNodeId` / `isFlexItem` 也必须显式提交，即使值为
`null` / `false`；缺失时使用 `node-capture-fields-missing`。
Web 下载端同样按完整工程契约失败闭合：响应没有 `bundle.contentBase64` 就报错，不会
静默退化成单个 `.ets` 文件。

快照还记录每个节点的直接 DOM 父节点与它是否确实为 Flex item。只有
`flex-grow > 0`、`flex-basis` 为 `0px` / `0%`、`flex-shrink` 可兼容，且直接 DOM
父节点就是元数据中的 `Row` / `Column` 时，才会安全映射为 ArkUI `layoutWeight`；否则
保留浏览器 bbox，并把导出标记为 `lossy`。
即使满足以上条件，当已验证的 flex 容器本身是 `scroll`（导出为纵向 `Scroll`）且
flex 主轴与滚动方向一致时也拒绝映射为 `layoutWeight`：浏览器给 flex 子项保底
min-content，滚动区里的高内容仍能撑出滚动范围，而 ArkUI 的 `layoutWeight` 没有这个
下限，会把权重锚定到滚动视口，把整页压成恰好一屏、彻底失去滚动。此时保留浏览器
bbox 高度，并补一条 `constraintSize({ minHeight: '100%' })`——`constraintSize` 的
下限在 Scroll 的无限主轴约束里依然生效：内容不足一屏时撑满视口，超过一屏时照常
滚动，与 CSS 行为一致，因此不再计为有损。`flex-grow` 落在 `scroll` 节点自己身上
（三明治布局里 `Scroll` 在固定高度页面列中占满剩余空间）不受影响，仍然映射为
`layoutWeight`。

## 图片资源物化

浏览器固化层只读取页面已经使用的 `Image` 和单一 `url(...)` 背景图。资源读取使用
`credentials: omit`，只允许 `https:`、`data:` 和 `blob:`；跨域图片必须允许 CORS。
后端不会访问网络，也不信任浏览器上报的 MIME：按文件签名重新识别 PNG、JPEG、GIF、
WebP，单文件限制 2 MB、总量限制 8 MB，并按 SHA-256 去重。

成功物化后，Screen IR 使用稳定的 `asset://media/...` 引用，ArkTS 使用
`$r('app.media.*')`，下载结果是一个确定性的完整 HarmonyOS Stage 工程 ZIP。当前工程
锁定本机已验证的 DevEco Studio 6.0.2 / HarmonyOS SDK 6.0.2（API 22），包含：

```text
AppScope/app.json5
AppScope/resources/base/*
build-profile.json5
hvigor/hvigor-config.json5
hvigorfile.ts
oh-package.json5
entry/build-profile.json5
entry/hvigorfile.ts
entry/oh-package.json5
entry/src/main/module.json5
entry/src/main/ets/entryability/EntryAbility.ets
entry/src/main/ets/pages/<Page>.ets
entry/src/main/resources/base/media/*
entry/src/main/resources/base/element/*
entry/src/main/resources/base/profile/main_pages.json
uibench-export.json
```

工程使用单 `entry` 模块、Stage 模型和 `UIAbility` 入口，可以直接用 DevEco Studio 打开。
签名材料、本机 `local.properties`、`.idea`、构建缓存和依赖目录不会打包；安装到设备前由
开发者配置自动签名。CORS 失败、文件超限、格式不支持或资源用途与节点不匹配时，保留
原引用并返回 `lossy` 诊断。

## 截图回归基线

仓库内已有三份固定 `390×844`、无远程依赖的首批样本：

```text
tests/fixtures/arkui_regression/typography
tests/fixtures/arkui_regression/stack-card
tests/fixtures/arkui_regression/scroll-feed
```

它们分别覆盖文字换行、Row/Column/Stack 卡片，以及 Scroll、重复 Row 和图片资源去重。
每个目录包含 `case.json`、`screen.html`、真实浏览器截图 `browser.png` 和经过
`BrowserSnapshot` 校验的 `browser-snapshot.json`。运行产物统一写入已忽略的
`.artifacts/arkui-regression/`：

```bash
python tools/arkui-regression.py prepare \
  --case tests/fixtures/arkui_regression/typography/case.json \
  --out .artifacts/arkui-regression/typography

python tools/arkui-regression.py build \
  --run .artifacts/arkui-regression/typography

python tools/arkui-regression.py probe-hdc

python tools/arkui-regression.py capture-hdc \
  --run .artifacts/arkui-regression/typography \
  --hap /absolute/path/to/entry-default-signed.hap

python tools/arkui-regression.py normalize-hdc \
  --run .artifacts/arkui-regression/typography \
  --crop 0,0,1320,2856 \
  --content-viewport 390x844 \
  --resample area-v1

python tools/arkui-regression.py compare \
  --run .artifacts/arkui-regression/typography \
  --arkui-screenshot \
    .artifacts/arkui-regression/typography/screenshots/normalizations/<normalizationId>/arkui.png
```

`prepare` 会验证视口、主题、节点和 PNG，直接复用 `export_annotated_html()` 输出
`screen-ir.json`、`page.ets`、完整工程 ZIP、浏览器截图和不含大体积 base64 的摘要。
其中 `page.ets` 始终保留转换器的规范输出；只在回归用工程 ZIP 内注入 v2 测试壳：
EntryAbility 在加载页面前等待全屏和系统栏隐藏完成，页面外层通过自定义测量/布局先固定
`390×844` 设计视口，再依据显示密度等比缩放到设备左上角。该壳不会进入日常 ArkTS
导出，也不会把设备适配逻辑混入 `html-to-arkui` 转换器。
`build` 使用 DevEco Studio 自带的 Node、Hvigor、JBR 和 SDK 编译工程，把去除 ANSI
控制字符的日志、退出码、unsigned HAP 哈希和签名状态写回 `report.json`。
当前实现按 macOS 的 DevEco Studio `.app/Contents` 布局定位工具链，
`--deveco-studio` 用于指定 `.app` 根目录；Windows 路径探测尚未接入。
`probe-hdc` 只读返回 HDC 版本和目标状态。`capture-hdc` 从 HAP 内校验
Bundle/Module/Ability，并要求显式 HAP payload 与当前 run 的构建产物一致，再使用显式
目标完成安装、Ability 启动、页面就绪检查、截图和拉取；
目标连接键只以摘要写入回归报告，命令日志也会脱敏。未显式传入 `--hap` 时，只接受报告
中唯一且经哈希复核的 signed HAP；当前 unsigned 构建不会被偷偷当作默认可安装产物。
显式 HAP 还必须与当前 run 的 unsigned payload 一致，是否接受其签名最终由目标设备决定。签名
证书、密码和 profile 必须由开发者在本机 DevEco Studio 配置，不进入导出 ZIP 或报告。
当前预检不是密码学验签，报告会明确记录验签状态，最终以目标设备接受安装为准。
在没有 ArkUI 截图时，报告只能是 `incomplete`；没有配置阈值时，比较结果是
`observed`，不会伪装成通过。设置 `maxDifferentRatio` 或
`maxMeanAbsoluteError` 后才会得到 `passed`/`failed`。两端尺寸不一致会被明确拒绝，
不会静默缩放；截图还必须使用全屏不透明画布。每次比较的 ArkUI 图、差异图和 Markdown
摘要写入 `screenshots/comparisons/<comparisonId>/`，完整目录落盘后才原子切换
`report.json`；失败重跑不会破坏上一份有效证据，切换成功后会清理未引用的旧版本。
同一个 run 的并发 `prepare`、`build`、`capture-hdc`、`compare` 会返回
`UIBENCH_REGRESSION_RUN_BUSY`，
不会让两个进程互相覆盖报告或清理对方的证据。重新准备或构建会在改写旧产物前先把
报告原子降级为 `incomplete`/`running`；中途失败不会保留上一轮的伪通过状态。即使视觉阈值满足，只要
`buildVerification` 尚未通过，报告总状态仍是
`incomplete`；构建失败会把总状态提升为 `failed`。

三份样本当前导出均为 `ready` 且已分别通过本机 API 22 编译，期间发现并修复了
API 22 `ButtonAttribute` 不支持 `.lineHeight()` 的映射问题。HDC 采集器会保留原始 PNG、
布局证据和脱敏日志；原始整屏图不会自动进入像素比较，也不做隐式 crop/resize。
归一化 v2 的 `area-v1` 接受显式物理像素 crop 和目标视口，可确定性处理非整数设备比例；
旧的 v1 `identity`/整数倍 `box-v1` 仍兼容。归一化 manifest 会固化 raw/layout 哈希、
完整参数和输出哈希，`compare` 只接受当前报告记录且再次通过哈希验证的归一化产物。

2026-08-12 已在 HarmonyOS 6.0.2（API 22）Phone 模拟器上跑通真实闭环。设备截图为
`1320×2856`，显式全屏 crop 后用 `area-v1` 归一化到 `390×844`。三份报告均未配置
接受阈值，因此状态是 `observed`，不是 `passed`：

| 样本 | MAE | RMSE | 当前结论 |
| --- | ---: | ---: | --- |
| `typography` | 5.406638 | 23.474475 | 已获得真实基线，继续校准字体和抗锯齿差异 |
| `stack-card` | 3.607066 | 14.023990 | 已修复浏览器内在宽度导致的数字换行 |
| `scroll-feed` | 4.753786 | 22.026075 | 已修复短内容在 ArkUI `Scroll` 中默认居中的偏移 |

`pixelThreshold=0` 时，背景色单通道相差 1、字体抗锯齿等系统噪声会让
`differentRatio` 显著放大，所以首轮不以该比例单独判定通过。当前模拟器接受了显式提供、
且 payload 来源校验通过的 unsigned HAP，报告记为 `device-install-accepted`；这不是密码学
验签结论，也不代表真机或其他模拟器会接受 unsigned HAP。

换用真机或要求受信任签名的目标时，仍需在 DevEco Studio 完成一次本机配置：

1. 打开 `.artifacts/arkui-regression/<case>/project`。
2. 在 `File > Project Structure > Project > SigningConfigs` 选择 HarmonyOS 并启用自动调试签名。
3. 在 DevEco 中构建/运行一次，取得 `entry-default-signed.hap`，再执行带 `--hap` 的
   `capture-hdc`。

完成 GUI 签名后不要再次执行本仓库的 `build` 子命令：它会从原始 `project.zip` 重新创建
`project/`，从而覆盖只保存在本机工程里的签名配置。签名证书、密码和 profile 不应提交到仓库。

## 当前限制

结构、文本、图片、Symbol props、computed style 和 bbox 已可生成并渲染为 ArkTS。
PNG/JPEG/GIF/WebP 图片和简单背景图已可物化。CSS 阴影、transform、复杂多背景、渐变、
字体文件等仍只有诊断、没有近似映射。因此包含这些能力的页面仍为 `lossy`。这不代表
截图一致性。工程生成器及带真实 Screen IR/图片资源的样例已经通过 API 22 ArkTS 编译和
unsigned HAP 打包；每次在线导出本身不会在 API 请求中重复运行 SDK 编译。

平台转换器已固定为仓库内 `vendor/html-to-arkui/*.tgz`，其中包含全部 Node 运行依赖。
首次部署执行：

```bash
npm ci --ignore-scripts --offline
```

bridge 默认只从根目录 `node_modules/@local/html-to-arkui/dist/index.js` 加载，不依赖
相邻仓库。仅在开发转换器时可显式覆盖：

```bash
export HTML_TO_ARKUI_ROOT=/absolute/path/to/html-to-arkui
```
