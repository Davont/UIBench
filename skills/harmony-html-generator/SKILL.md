---
name: harmony-html-generator
description: 为设计师生成、重新生成、修改或审查精致且不依赖固定模板的鸿蒙风格移动端 HTML 页面。适用于创建新的鸿蒙 HTML 页面、重复相同提示重新生成新版本、优化已有页面或检查现有产物。严格区分创建、修改和审查，采用本地 HarmonyOS Sans 与 HarmonyOS Symbol、语义化 Design Token、稳定 data-node-id、受支持 data-component、离线资源、无障碍属性和确定性校验。
---

# 生成鸿蒙 HTML

将本 Skill 目录视为 `<SKILL_DIR>`。自由设计页面构图；禁止从预定义的首页、列表页、设置页、表单页或详情页模板起步。

## 设计目标

让页面像系统原生界面一样自然：任务清楚、信息关系明确、空间层级平衡、平台资产准确、反馈可预期。每个视觉决定都必须服务于内容、层级、分组或操作，不为“高级感”添加无意义装饰。

华为官方资料提供设计方向；本 Skill 的颜色、间距、圆角、字号和 390px 视口是为了 UIBench HTML 运行时而确定的实现 Token，不宣称为所有 HarmonyOS 产品的官方固定数值。仅在审计规范、更新本 Skill 或用户索要依据时读取 [`references/official-basis.md`](references/official-basis.md)。

## 交付物

创建以下离线目录：

```text
<output>/
├── index.html
└── assets/
    ├── harmony-runtime.css
    ├── fonts/
    └── media/                 # 仅在页面确实需要本地图片时存在
```

确保 `index.html` 可完全离线渲染，不依赖 Tailwind CDN、Lucide、远程字体、远程图片或其他项目目录。

## 任务模式

执行任何页面读取或写入前，只根据用户**当前请求的明确措辞**选择一种模式。优先级为：当前请求 > 本轮明确引用的上下文 > 更早的对话 > 工作区已有文件。不得仅因为目标目录已有 HTML、浏览器正显示旧页面或用户重复了提示词，就自行切换成修改或审查模式。

### 创建模式

- 触发词包括“生成、创建、设计、做一个、再生成、重新生成、重做”，以及没有修改对象、直接描述所需新页面的请求。
- 用户重复发送相同或近似的创建请求时，仍执行创建模式：从需求重新做设计决策并生成全新版本。
- 不主动读取、检查、复用或模仿已有 `index.html`、旧页面截图、baked 页面或页面模板；只有用户明确指定某个现有产物为参考时才读取它。可以复用本 Skill 的运行时、字体、图标映射和用户明确提供的媒体资源。
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

## 创建与修改工作流

1. 创建模式根据用户需求推断简洁的 kebab-case 页面名、无冲突输出目录和 `light` / `dark` 主题，未指定主题时使用 `light`。修改模式定位用户明确指向的现有页面并保留其主题，除非用户要求改变。仅在目标文件、输出位置或信息架构存在实质歧义时询问。
2. 完整读取 [`references/design-language.md`](references/design-language.md)。不要检查庞大的 UIBench 组件目录、baked 页面或页面模板。
3. 在内部按顺序确定：用户此刻的主要任务、必须显示的信息、第一阅读焦点、信息密度、主导构图、表面层级、唯一主要操作。除非用户要求，否则不要输出规划文件。
4. 创建模式直接从需求编写新的 body 片段或完整 HTML，不读取旧页面。修改模式先读取目标 HTML，再做最小相关修改。先建立阅读顺序和分组，再选择组件和 Token；不要从页面类型模板反推内容。
5. 编写时同步添加稳定的 `data-node-id` 和受支持的 `data-component`。需要表达产品语义时使用可选的 kebab-case `data-ui-role`，它不能替代组件标注。
6. 只使用设计语言参考中列出的本地 class。禁止 `<style>`、行内 `style`、`<script>`、内联事件、远程 URL、JavaScript 和任意颜色字面量。
7. 同步完成无障碍语义：按钮使用 `type="button"` 并提供可见文字或 `aria-label`；输入控件提供 `aria-label`；图标使用 `aria-hidden="true"`；图片提供有意义的 `alt`。
8. 若使用用户提供的图片，先复制到 `<output>/assets/media/`，再以相对路径引用。不要用远程占位图代替缺失内容。
9. 执行收尾：

   ```bash
   node <SKILL_DIR>/scripts/finalize-html.mjs \
     --input <source-html> \
     --out <output-directory> \
     --title "<页面标题>" \
     --theme <light|dark>
   ```

   输入为片段时，收尾器补充中性的文档外壳，同时注入本地运行时、物化已知鸿蒙图标并复制字体。该外壳只是运行基础设施，不是视觉页面模板。
10. 运行确定性校验：

    ```bash
    node <SKILL_DIR>/scripts/validate-html.mjs <output-directory>/index.html
    ```

11. 仅当本轮创建或修改的产物未通过校验时，才优先局部修复失败节点并重新运行；最多执行两轮修复，仍受阻时准确报告剩余问题。这条局部修复规则只适用于本轮校验，不得用来把创建模式改成修改或审查模式。
12. 返回 `index.html` 的绝对路径、所用主题和校验结果。

## 审查工作流

1. 确认用户指向的 `index.html`，不要推断另一个相似页面。
2. 完整读取 [`references/design-language.md`](references/design-language.md)；用户要求视觉、高保真或截图审查时，再读取 [`references/visual-review.md`](references/visual-review.md)。
3. 运行确定性校验；需要视觉审查且环境允许时，按质量模式渲染所选主题。
4. 按严重度报告结构、Token、组件、视觉和无障碍问题，并区分已验证事实与未执行的检查。
5. 未得到修复请求时不写入任何页面文件。用户要求修复时切换为修改模式，并在修改后重新校验。

## 质量模式

“精致”“好看”属于默认生成标准，不单独触发截图。仅当用户明确要求视觉验收、高保真检查、像素级检查、截图复核，或说明页面将用于正式展示评审时，启用质量模式：

1. 先完成当前模式对应的创建、修改或审查工作流。
2. 完整读取 [`references/visual-review.md`](references/visual-review.md)。
3. 使用可用浏览器以 390×844 渲染所选主题。若浏览器禁止直接访问 `file://`，在权限允许时使用现有运行环境启动仅监听 `127.0.0.1` 的临时静态服务器；不要安装依赖。
4. 按“目的 → 层级 → 几何 → Token → 平台特征 → 无障碍”的顺序检查截图，并确认 390px 宽度下不存在横向溢出。
5. 只做一轮聚焦修复，保留正确内容、结构和数据属性。
6. 再次校验最终 HTML。用户明确要求同时验收深浅色时，分别渲染两种主题。

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
- `list` 只能直接包含 `list-item`，`grid` 只能直接包含 `grid-item`，`tabs` 只能直接包含 `tab-content`，`text` 只能直接包含 `span`。
- `scroll`、`button`、`list-item` 和 `grid-item` 最多只能有一个直接标注的子组件；需要组合内容时，先添加一个 `row` 或 `column` 子组件。
- 对应组件使用原生 `<button>`、`<img>` 和 `<input>` 元素。所有输入控件都必须有 `aria-label`。
- 图标使用成对的空元素 `<i data-lucide="..." data-component="symbol" aria-hidden="true"></i>`，由收尾器插入固定的本地 HarmonyOS Symbol 字形。
- 禁止输出 `textarea`、`select`、`progress`、不受支持的组件名、反向 flex、grid span 或按列流动的 grid。

详细机器规则位于 [`references/component-contract.json`](references/component-contract.json)。通常让校验器读取它，不要把它加载进生成上下文。

## 参考文件路由

- 普通生成：完整读取 [`references/design-language.md`](references/design-language.md)。
- 视觉验收：额外读取 [`references/visual-review.md`](references/visual-review.md)。
- 精确图标不在常用清单中：只检索 [`references/icon-map.json`](references/icon-map.json)；不要完整加载。
- 审计来源、更新规范或回答依据问题：读取 [`references/official-basis.md`](references/official-basis.md)。
- 组件结构：由校验器读取 [`references/component-contract.json`](references/component-contract.json)。

## 加速规则

- 默认只加载设计语言；不要加载官方来源、完整图标表或完整组件库。
- 除非用户要求，只生成一个方案，不生成多个候选。
- 复用内置 CSS、字体和图标映射，禁止重新生成或内联。
- 默认运行静态校验，仅在质量模式下截图。
- 仅在本轮产物校验失败时修复失败节点，不重写本轮已经正确的 HTML；此规则不影响任务模式判定。
- 使用真实、简洁的可见内容。需要简化时，先移除装饰复杂度，再删减次要信息，最后才考虑减少必要内容。

## 边界

- 未渲染并检查最终页面时，不要声称已经达到严格视觉一致。
- 即使工作区存在页面模板，也禁止使用。
- 不把本 Skill 的实现 Token 描述成华为官方唯一数值。
- 执行页面生成任务时，不要修改 UIBench 应用代码。
