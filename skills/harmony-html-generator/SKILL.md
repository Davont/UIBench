---
name: harmony-html-generator
description: 为设计师生成、重新生成、修改或审查精致且不依赖固定模板的鸿蒙风格移动端 HTML 页面。适用于创建新的鸿蒙 HTML 页面、重复相同提示重新生成新版本、优化已有页面、实现页面内操作或检查现有产物。有意义的操作需求默认输出纯离线、内存态的交互版；只有明确要求纯静态时才停在无脚本版。交互输出不生成 ArkTS，并在增强失败时确定性回退到已校验的静态页面。
---

# 生成鸿蒙 HTML

将本 Skill 目录视为 `<SKILL_DIR>`。自由设计页面构图；禁止从预定义的首页、列表页、设置页、表单页或详情页模板起步。

## 设计目标

让页面像系统原生界面一样自然：任务清楚、信息关系明确、空间层级平衡、平台资产准确、反馈可预期。每个视觉决定都必须服务于内容、层级、分组或操作，不为“高级感”添加无意义装饰。

华为官方资料提供设计方向；本 Skill 的颜色、间距、圆角、字号和 390px 视口是为了 UIBench HTML 运行时而确定的实现 Token，不宣称为所有 HarmonyOS 产品的官方固定数值。仅在审计规范、更新本 Skill 或用户索要依据时读取 [`references/official-basis.md`](references/official-basis.md)。

## 交付物

所有创建和修改任务都先生成以下无脚本离线基线：

```text
<output>/
├── index.html
└── assets/
    ├── harmony-runtime.css
    ├── fonts/
    └── media/                 # 仅在页面实际使用用户图片或内置图片时存在
```

默认的交互最终目录只额外包含一个脚本：

```text
<output>/
├── index.html
└── assets/
    ├── app.js
    ├── harmony-runtime.css
    ├── fonts/
    └── media/                 # 按需存在
```

两种输出都必须完全离线，不依赖 Tailwind CDN、Lucide、远程字体、远程图片或其他项目目录。交互版的静态 HTML 必须在脚本不可用时仍可阅读和操作原生控件；增强或交互校验失败时，最终目录发布已校验的静态版本，不发布半成品。

## 操作模式

执行任何页面读取或写入前，只根据用户**当前请求的明确措辞**选择创建、修改或审查中的一种操作模式。优先级为：当前请求 > 本轮明确引用的上下文 > 更早的对话 > 工作区已有文件。不得仅因为目标目录已有 HTML、浏览器正显示旧页面或用户重复了提示词，就自行切换成修改或审查模式。

### 创建模式

- 触发词包括“生成、创建、设计、做一个、再生成、重新生成、重做”，以及没有修改对象、直接描述所需新页面的请求。
- 用户重复发送相同或近似的创建请求时，仍执行创建模式：从需求重新做设计决策并生成全新版本。
- 不主动读取、检查、复用或模仿已有 `index.html`、旧页面截图、baked 页面或页面模板；只有用户明确指定某个现有产物为参考时才读取它。可以复用本 Skill 的运行时、字体、图标映射、内置离线图片库和用户明确提供的媒体资源。
- 目标输出目录已存在且用户未明确要求覆盖时，不覆盖、不把旧页面当输入；自动选择同级的递增版本目录，例如 `<slug>-v2`、`<slug>-v3`。只有用户明确要求覆盖某个路径时才原位写入。

### 修改模式

- 仅当用户明确说“修改、优化、调整、继续完善、修复、基于现有页面”或明确指向一个已有文件时使用。
- 读取用户指定的现有页面，保留无关内容、结构和稳定 `data-node-id`，只修改请求涉及的最小范围。
- “检查并修复”属于修改模式；先检查，再修复已确认的问题。

### 审查模式

- 仅当用户明确说“检查、评审、审查、审计、验证、找问题”，且没有要求修改时使用。
- 读取指定页面并报告发现；默认不修改、不重新生成、不覆盖文件。
- 用户随后要求修复时，下一轮切换为修改模式。

若一句请求同时包含多种动作，以用户要求的最终交付物判断：要求得到新页面用创建模式，要求现有页面发生变化用修改模式，只要求结论用审查模式。只有最终交付物确实无法判断时才询问。

## 输出模式

输出模式与创建、修改、审查正交判断：

- **交互模式（默认最终输出）**：创建或修改的页面包含有意义的操作控件、功能或动态反馈时使用。自然需求中的“支持播放/暂停、切歌、拖动进度、切换模式、排序或移除、收藏、展开、筛选、输入或提交”等功能描述本身就是交互需求；不要等待用户再写“带交互”、“可点击”或逐项解释点击后行为。“HTML 页面”、“完整 HTML”或“单文件 HTML”只描述交付形式，不是关闭交互的指令。先完成一份无脚本且独立成立的静态页面，再以外部 `assets/app.js` 渐进增强。
- **静态模式（显式退出）**：只有用户明确要求“纯静态、无脚本、不要 JavaScript、仅视觉稿、不需要交互”时，才在静态校验后直接交付无脚本版。如果需求确实是没有任何有意义操作的纯内容展示，也不为凑 `app.js` 虚构功能，可以交付静态版。
- **审查模式**不自行改变目标的输出模式；只按目标当前是否包含本地交互脚本选择对应校验器。

交互模式的最终输出目录必须尚不存在，并与静态基线分离且不互相嵌套。增强现有页面时默认选择同级 `<slug>-interactive`，冲突时递增为 `-interactive-v2`、`-interactive-v3`；不得覆盖输入页面。交互模式只交付 HTML/CSS/JavaScript。不得调用 ArkUI/ArkTS 导出流程，不得编写或声称生成 ArkTS；现有 `data-component` 仅作为页面结构元数据保留。

## 普通创建与修改的上下文预算

- 静态首稿阶段只完整读取 [`references/design-language.md`](references/design-language.md)；它是该阶段唯一需要加载的参考文件。
- 选择默认交互输出时，静态基线通过校验后才完整读取 [`references/interaction-language.md`](references/interaction-language.md) 并编写脚本。已选择静态输出时不读取该参考。
- 把收尾器、增强器和校验器当作黑盒执行。禁止读取 `scripts/finalize-html.mjs`、`scripts/enhance-html.mjs`、`scripts/validate-html.mjs` 或 `scripts/validate-interactive.mjs` 源码，禁止读取 `assets/harmony-runtime.css` 或字体。
- 禁止读取 [`references/component-contract.json`](references/component-contract.json)；机器契约由校验器使用。禁止完整读取 [`references/icon-map.json`](references/icon-map.json)；仅当所需图标不在设计语言的常用清单中时，用精确名称检索该文件的局部匹配。
- 禁止创建 todo、调用 todo 工具或输出规划。禁止使用 `ls`、`find`、`glob`、`tree` 或文件清单搜索探查工作区、Skill 目录或资产目录。执行环境已给出输出目录时直接使用；仅在未给出时检查一个已选定的具体目标路径是否冲突，不枚举目录。
- 禁止枚举或打开内置图片库及其 manifest。内容确实需要摄影图时，只在 `<img>` 上写语义查询，由收尾器确定性选图；用户媒体路径仍只处理用户明确提供的文件。

## 创建与修改工作流

1. 创建模式根据用户需求推断简洁的 kebab-case 页面名、无冲突输出目录和 `light` / `dark` 主题，未指定主题时使用 `light`。修改模式定位用户明确指向的现有页面并保留其主题，除非用户要求改变。仅在目标文件、输出位置或信息架构存在实质歧义时询问。
2. 完整读取 [`references/design-language.md`](references/design-language.md)，且遵守上述上下文预算。
3. 不调用工具、不输出规划，直接在内部确定：用户此刻的主要任务、必须显示的信息、第一阅读焦点、信息密度、主导构图、表面层级、唯一主要操作，以及摄影图片是否对内容理解或产品任务有实际价值。选择默认交互输出时还需确定有限的页面内状态、触发控件和预声明目标，但此时不编写 JavaScript。
4. 创建模式直接从需求编写新的 body 片段或完整 HTML，不读取旧页面。修改模式先读取目标 HTML，再做最小相关修改。先建立阅读顺序和分组，再选择组件和 Token；不要从页面类型模板反推内容。
5. 首稿只标注静态契约真正需要表达为 ArkUI 结构组件的节点，并同步写全稳定的 `data-node-id`、受支持的 `data-component` 和结构 class；这些标注本身不触发 ArkTS 生成。独立文字用一个 `text` 节点直接承载文字，不要再套 `span` 组件；只有同一段 `text` 内确实需要独立样式的局部富文本才使用直属、非空的 `span` 组件。`column` 必须有 `flex flex-col`，`row` 必须有 `flex flex-row`，`grid` 必须有 `grid` 且只直接包含 `grid-item`，`stack` 必须有 `relative`。普通分组和重复行默认使用 `column` / `row`；只有确实需要原生列表、网格或标签页语义时才使用 `list` / `grid` / `tabs`，并一次写对其完整契约。需要表达产品语义时使用可选的 kebab-case `data-ui-role`，它不能替代组件标注。
6. 只使用设计语言参考中列出的本地 class。静态首稿始终禁止 `<style>`、行内 `style`、`<script>`、内联事件、远程 URL、JavaScript 和任意颜色字面量。默认交互输出的静态首稿可额外写 inert 的 `data-action`、`data-target` 与稳定 `data-node-id`：所有点击后可能显示、隐藏或更新的复杂内容必须预先存在于 DOM，初始页面在没有脚本时仍完整成立。不得预先写脚本标签，也不得在后续脚本中创建或重排组件树。
7. 同步完成无障碍语义：按钮使用 `type="button"` 并提供可见文字或 `aria-label`。纯文字按钮直接写文字且不放已标注子组件；纯图标按钮只放一个 `symbol`；图标加文字时，只放一个已标注的 `row` 直接子组件，再把 `symbol` 和 `text` 放进该 `row`。禁止混用按钮直属原始文字与组件子节点，不要把按钮文字误标成 `span`。输入控件提供 `aria-label`；`radio` 还必须提供非空 `name` 和 `value`，`slider` 还必须提供 `min`、`max` 和 `value`。checkbox、radio 和 toggle 的 `control-row` 必须是完整 label 行，把已标注的可见标签内容与 input 一起包住；禁止让 `w-full` label 只包 input 并与外部文字并列。图标使用 `aria-hidden="true"`；图片提供有意义的 `alt`。
8. 图片只能走以下两条路径，且用户明确提供的图片优先：
   - **内置图片**：当真实内容需要摄影图时，在原生 `<img data-component="image">` 上写非空、简洁的英文 `data-media-query`，可选 `data-media-orientation="portrait|landscape|squarish"`，同时写稳定 `data-node-id`、准确 `alt` 和所需媒体 class；首稿不要写 `src`。收尾器会稳定匹配、批内去重、补充相对 `src`，并只复制命中的图片。默认最多使用 3 张；只有用户明确需要更多图片时才可增加，硬上限为 8 张。
   - **用户图片**：只有用户明确提供、可读取且已经实际复制成功的源文件，才可复制到 `<output>/assets/media/` 并以相对 `src` 引用；不得同时添加 `data-media-query`。

   不为装饰或“高级感”索取摄影图，不枚举内置文件，不读取图片 manifest，不猜测文件名，不写远程 URL、data URL、虚构的 `assets/media/...` 路径或 CSS URL。没有合适媒体价值时使用 surface、文字和 HarmonyOS Symbol。
9. 始终先调用一次 shell 工具，在同一条命令中依次完成无脚本收尾和静态校验。只有已选择静态输出时才原样使用以下命令的 `<output-directory>`；默认交互输出必须把它替换成执行环境中独立的临时 `<static-output-directory>`，并为增强器保留尚不存在的最终输出目录：

   ```bash
   node <SKILL_DIR>/scripts/finalize-html.mjs \
     --input <source-html> \
     --out <output-directory> \
     --title "<页面标题>" \
     --theme <light|dark> && \
    node <SKILL_DIR>/scripts/validate-html.mjs \
     <output-directory>/index.html
   ```

   不要在命令前读取两个脚本。输入为片段时，收尾器补充中性的文档外壳，同时注入本地运行时、物化已知鸿蒙图标、解析内置图片语义查询，并复制字体及实际命中的图片。该外壳只是运行基础设施，不是视觉页面模板。
10. 只有静态校验失败才进入修复：按完整校验报告的错误代码和 `data-node-id` 定位，只修改报告明确指出的失败节点、class 或资源及其直接相关结构。禁止重写整个源文件，也禁止顺手重构或改写没有 ERROR 的节点。一次批量完成本轮全部机械修复后，下一步立即原样重跑上述合并命令；最多两轮局部修复，仍受阻时准确报告剩余问题。不得因校验失败改变任务模式，也不得在静态基线未通过时尝试交互增强。
11. 只有已选择静态输出时才到此结束、不读取交互参考也不调用增强器。默认交互输出在静态基线通过后，完整读取 [`references/interaction-language.md`](references/interaction-language.md)，只针对已预声明的 DOM 编写一个临时 JavaScript 源文件，然后调用一次增强器：

    ```bash
    node <SKILL_DIR>/scripts/enhance-html.mjs \
      --input <static-output-directory> \
      --script <generated-js-source> \
      --out <final-output-directory>
    ```

    增强器在 staging 目录复制静态基线、写入 `assets/app.js`、注入唯一的 `<script src="assets/app.js" defer></script>`，并调用交互校验器；禁止手工改写已校验的 `index.html`。增强成功时原子发布 `mode=interactive`。脚本或交互校验失败时，它仍以退出码 0 原子发布字节不变的静态副本并返回 `mode=fallback-static`；接受该回退，不重写静态页面、不放宽校验。若增强器因无效基线或文件系统错误以非零状态退出，保留并返回已校验静态目录，不声称已生成交互版。
12. 返回最终 `index.html` 的绝对路径、所用主题、静态校验结果，以及实际输出模式 `static`、`interactive` 或 `fallback-static`。回退时明确说明页面仍是可用的原静态方案。

## 审查工作流

1. 确认用户指向的 `index.html`，不要推断另一个相似页面。
2. 完整读取 [`references/design-language.md`](references/design-language.md)；用户要求视觉、高保真或截图审查时，再读取 [`references/visual-review.md`](references/visual-review.md)。
3. 运行确定性校验：无脚本页面使用 `validate-html.mjs`；包含唯一 `assets/app.js` defer 脚本的页面使用 `validate-interactive.mjs`。只有审查交互行为时才读取交互语言参考。需要视觉审查且环境允许时，按质量模式渲染所选主题。
4. 按严重度报告结构、Token、组件、视觉和无障碍问题，并区分已验证事实与未执行的检查。
5. 未得到修复请求时不写入任何页面文件。用户要求修复时切换为修改模式，并在修改后重新校验。

## 质量模式

“精致”“好看”属于默认生成标准，不单独触发截图。仅当用户明确要求视觉验收、高保真检查、像素级检查、截图复核，或说明页面将用于正式展示评审时，启用质量模式：

1. 先完成当前模式对应的创建、修改或审查工作流。
2. 完整读取 [`references/visual-review.md`](references/visual-review.md)。
3. 使用可用浏览器以 390×844 渲染所选主题。若浏览器禁止直接访问 `file://`，在权限允许时使用现有运行环境启动仅监听 `127.0.0.1` 的临时静态服务器；不要安装依赖。
4. 按“目的 → 层级 → 几何 → Token → 平台特征 → 无障碍”的顺序检查截图，并确认 390px 宽度下不存在横向溢出。
5. 只做一轮聚焦修复，保留正确内容、结构和数据属性。交互模式只修改静态源和预声明 hooks，再重跑静态阶段与增强器；禁止手工修补已发布的交互目录。
6. 按最终输出模式再次运行静态或交互校验。用户明确要求同时验收深浅色时，分别渲染两种主题。

若环境没有浏览器或截图能力，或安全策略仍阻止访问本地页面，完成静态校验并明确说明未执行视觉检查。不要自动安装依赖。

## 组件契约

`data-component` 只能使用以下值：

```text
column row stack scroll text span image symbol divider button
list list-item grid grid-item search text-input checkbox radio
toggle tabs tab-content slider
```

遵守以下不变量：

- 每个组件必须拥有全局唯一、符合 `^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$` 的节点 ID。
- 页面必须恰好只有一个组件根节点；根节点使用 `min-h-screen bg-ui-canvas text-ui-fg font-ui`。
- 每个已标注节点的 DOM 父节点必须等于其组件父节点。禁止在两个已标注节点之间插入未标注 wrapper。
- `column` 使用 `flex flex-col`，`row` 使用 `flex flex-row`，`grid` 使用 `grid`，`stack` 使用 `relative`。
- 独立文字使用一个 `text` 节点并直接写文字；整段字体 class 也写在该 `text` 节点。不要因为 HTML 标签是 `<span>` 就标成 `data-component="span"`；普通 `<span>` 不写 `data-component` 或 `data-node-id`。`span` 组件只用于 `text` 直属、非空且需要局部独立样式的富文本。
- 普通分组和重复行优先使用 `column` / `row`，避免不必要的专用结构。使用 `list` 时只能直接包含 `list-item`，且每个 `list-item` 最多放一个 `row` 或 `column` 子组件；使用 `grid` 时只能直接包含 `grid-item`；使用 `tabs` 时写 `data-index="0"`，可见标签按钮行放在 `tabs` 外作为同级节点，`tabs` 内只直接包含带非空 `data-tab-bar` 的 `tab-content`。
- `scroll`、`button`、`list-item` 和 `grid-item` 最多只能有一个直接标注的子组件；需要组合内容时，先添加一个 `row` 或 `column` 子组件。
- 对应组件使用原生 `<button>`、`<img>` 和 `<input>` 元素。所有输入控件都必须有 `aria-label`。
- 内置图片首稿可用 `data-media-query` 代替 `src`，但收尾后的 `<img>` 必须拥有指向输出目录内真实文件的相对 `src`；用户图片始终直接使用已复制文件的相对 `src`。
- 图标使用成对的空元素 `<i data-lucide="..." data-component="symbol" aria-hidden="true"></i>`，由收尾器插入固定的本地 HarmonyOS Symbol 字形。
- 禁止输出 `textarea`、`select`、`progress`、不受支持的组件名、反向 flex、grid span 或按列流动的 grid。

详细机器规则位于 [`references/component-contract.json`](references/component-contract.json)。通常让校验器读取它，不要把它加载进生成上下文。

## 参考文件路由

- 所有创建与修改的静态首稿阶段：完整读取 [`references/design-language.md`](references/design-language.md)。
- 默认交互输出：静态基线校验通过后，再完整读取 [`references/interaction-language.md`](references/interaction-language.md)；已选择静态输出时不读取。
- 视觉验收：额外读取 [`references/visual-review.md`](references/visual-review.md)。
- 精确图标不在常用清单中：只检索 [`references/icon-map.json`](references/icon-map.json)；不要完整加载。
- 审计来源、更新规范或回答依据问题：读取 [`references/official-basis.md`](references/official-basis.md)。
- 组件结构：由校验器读取 [`references/component-contract.json`](references/component-contract.json)。
- 内置图片清单：由收尾器读取 `assets/media-library/manifest.json`；生成时不要加载、枚举或直接引用它。

## 加速规则

- 静态首稿阶段只加载设计语言；不要加载官方来源、脚本源码、运行时 CSS、完整图标表或机器组件契约。
- 除非用户要求，只生成一个方案，不生成多个候选。
- 用户没有指定精确数量时，同类演示数据最多渲染 3 条，用总数文案表达其余内容；不要为证明功能而复制长列表、长歌词或长卡片组。
- 复用内置 CSS、字体、图标映射和按需图片库，禁止重新生成或内联。
- 已选择静态输出时只调用一次合并的收尾+校验命令；默认交互输出在静态校验通过后再调用一次增强器。仅在失败局部修复后重跑静态阶段；交互增强失败直接接受静态回退。仅在质量模式下截图。
- 仅在本轮产物校验失败时修复失败节点，不重写本轮已经正确的 HTML；此规则不影响任务模式判定。
- 使用真实、简洁的可见内容。需要简化时，先移除装饰复杂度，再删减次要信息，最后才考虑减少必要内容。

## 边界

- 未渲染并检查最终页面时，不要声称已经达到严格视觉一致。
- 即使工作区存在页面模板，也禁止使用。
- 不把本 Skill 的实现 Token 描述成华为官方唯一数值。
- 交互模式只改变当前页面进程中的内存状态；不联网、不持久化、不产生页面外副作用，也不生成 ArkTS。
- 执行页面生成任务时，不要修改 UIBench 应用代码。
