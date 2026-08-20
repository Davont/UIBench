# 鸿蒙 HTML 设计语言

生成页面前完整读取本文件。这里定义设计决策和 UIBench HTML 映射，不提供页面模板。

## 导航

- 1–2：来源边界与静默设计简报
- 3–5：构图、间距、圆角
- 6–8：色彩材质、字体、图标
- 9–10：控件反馈与组件样式
- 11–12：class 白名单与交付自检

## 1. 设计命题与来源边界

让页面像系统本来就应该这样工作：主要任务清楚，信息关系明确，空间层级平衡，平台资产准确，操作反馈自然。

- **官方方向**：以人为本、和谐统一、语义化色彩、HarmonyOS Sans、HarmonyOS Symbol、自然反馈与多设备适配。
- **HTML 映射**：使用语义 class、原生控件和 Web 无障碍近似表达平台原则。
- **项目契约**：390px 预览、`data-component`、节点 ID、class 白名单和具体 CSS 数值属于 UIBench。

具体来源和差异见 [`official-basis.md`](official-basis.md)，普通生成不要读取该文件。

## 2. 写标记前的静默设计简报

按顺序确定以下内容，不输出额外规划文件：

1. 用户此刻最重要的任务是什么？
2. 首屏必须看见什么，什么可以自然向下滚动？
3. 第一、第二、第三阅读目标分别是什么？
4. 页面应当紧凑、舒适还是沉浸？
5. 哪些内容属于同一组，哪些内容需要独立表面？
6. 唯一主要操作是什么？若没有真实主要操作，不要发明。
7. 主题是浅色还是深色？

高自由度用于信息架构、分组、焦点和构图；中自由度用于 Token 组合；组件契约、离线资源和无障碍属性没有自由发挥空间。

## 3. 构图与信息层级

- **原则**：先让任务和阅读顺序成立，再追求视觉表现。
- **默认**：建立一个明确焦点和不超过三层的阅读层级；先用字号、字重、留白和位置分组。
- **例外**：只有用户提供主要媒体，或页面内容确实需要摄影图并能从内置离线图库匹配时，才让图片成为首要焦点；只有简短同级数据才使用双列网格。
- **禁止**：从“首页、仪表盘、详情页”等页面类型模板起步；为填满画面添加 hero、指标、标签页、导航或操作。
- **验证**：遮住颜色后仍能从尺度和空间看出阅读顺序；删除装饰后页面任务仍完整。

重复同类内容使用规则列表；少量同级短内容可以使用网格；工具和设置使用可预测的行结构。保持内容驱动的非对称，不随机改变几何形态。

## 4. 间距与密度

- **原则**：组间距离大于组内距离；关系越紧密，间距越小。
- **默认**：页面左右使用 16px；主要页面区块之间使用 24px；卡片、行和同级元素使用 12px；紧密关系使用 8px。
- **例外**：图标与短标签等微关系可以使用 4px；沉浸媒体可以横向贴边，但文字和操作仍回到页面边距。
- **禁止**：无语义地混用一次性间距；用大量空白掩盖信息不足；让相邻元素因偶发 margin 产生错位。
- **Token/验证**：`px-ui-page` = 16px，`gap-6` = 24px，`gap-ui-item` / `gap-ui-card` = 12px，`gap-ui-compact` = 8px，`gap-1` = 4px。截图中概念分组必须明显大于组内节奏。

`ui-section`、`ui-card`、`ui-item` 在现有 UIBench Token 中都为 12px；不要用 `gap-ui-section` 冒充 24px 的页面大区块间距。

## 5. 圆角与形状

- **原则**：圆角表达组件类型和层级，相同类型保持一致。
- **默认**：内容表面使用 `rounded-ui-card`，输入与普通按钮使用 `rounded-ui-control`，真正的胶囊或圆形操作使用 `rounded-ui-pill`。
- **例外**：连续列表的内部行不分别加圆角；贴边媒体可由父表面裁切；小图标不需要背板。
- **禁止**：所有内容都包成卡片；同层级随机混用圆角；把胶囊用于每个标签和按钮。
- **Token/验证**：项目映射为卡片 20px、控件 16px、胶囊全圆角。这是 UIBench 实现，不是华为所有场景的唯一数值。

## 6. 色彩、表面与空间材质

- **原则**：颜色表达语义，表面表达空间；先保证内容可读，再添加层级效果。
- **默认**：使用平静画布、干净表面、最多三层空间和一种主强调色。普通卡片依靠画布与表面色区分，不加整圈边框和阴影。
- **例外**：真实浮层、悬浮工具条或与内容重叠的操作层可以使用 `bg-ui-canvas-translucent shadow-ui-surface`；状态色只用于真实成功、提醒和危险状态。
- **禁止**：原始 hex/rgb/hsl、`dark:*`、高反差装饰渐变、彩色阴影、整页玻璃拟态、多个实心主色操作。
- **Token/验证**：同一 DOM 只消费语义 Token；深浅主题由运行时映射。主蓝只强调操作、选择或核心信息。

常用表面：

| 目的 | class |
| --- | --- |
| 页面画布 | `bg-ui-canvas` |
| 次级/三级背景层 | `bg-ui-layer-secondary` / `bg-ui-layer-tertiary` |
| 普通内容表面 | `bg-ui-surface` |
| 顶层或抬升表面 | `bg-ui-surface-raised` |
| 弱控件背景 | `bg-ui-component-subtle` |
| 次级控件背景 | `bg-ui-component-secondary` |
| 轻量主色提示 | `bg-ui-primary-container-subtle` |
| 浮动近似材质 | `bg-ui-canvas-translucent shadow-ui-surface` |

状态容器只在真实状态出现时使用：`bg-ui-success-container text-ui-on-success`、`bg-ui-warning-container text-ui-on-warning`、`bg-ui-danger-container text-ui-on-danger`。轻量品牌提示使用 `bg-ui-primary-container` 或更弱的 `bg-ui-primary-container-subtle`。

浮动近似材质只表达真实 Z 轴关系；HTML 的模糊和阴影不等于 HarmonyOS 系统沉浸光感。

## 7. 字体层级

- **原则**：字号、字重和行高共同表达层级，正文优先保证连续阅读。
- **默认**：只使用三个字体角色和 400 / 500 / 700 三档字重；同屏尽量不超过三种显著文字样式。
- **例外**：短标题可加粗；次级元信息可降为 caption。不要因为卡片重要就把其中所有文字加粗。
- **禁止**：发明 `text-ui-*` 角色、大面积粗体、全大写装饰、斜体、额外字间距、低对比小字。
- **Token/验证**：标题 `text-ui-title` 24px，正文 `text-ui-body` 16px，说明 `text-ui-caption` 12px；配合 `font-ui`、`font-medium`、`font-bold`。

这三个项目角色分别近似映射官方手机 Title_M、Body_L、Caption_L。页面必须使用本地 HarmonyOS Sans。
前景按 `text-ui-fg`、`text-ui-fg-secondary`、`text-ui-fg-tertiary` 逐级弱化；`text-ui-fg-subtle` 是 `text-ui-fg-tertiary` 的兼容别名，只用于非关键、低强调辅助内容，不新增颜色层级。

## 8. 图标

- **原则**：图标首先传意，风格、体量、字重和基线保持一致。
- **默认**：使用本地 HarmonyOS Symbol，普通操作使用 24px；紧凑辅助图标可使用 16/20px，重要焦点图标最多 32px。
- **例外**：清单没有合适图标时优先省略装饰图标；确需精确图标时检索 `icon-map.json`。
- **禁止**：Emoji、字符拼图、远程 SVG、Lucide 运行时、风格混杂或仅为填空添加图标。
- **Token/验证**：使用 `size-4`、`size-5`、`size-6`、`size-8`；所有 Symbol 添加 `aria-hidden="true"`，由收尾器物化固定字形。

常用 `data-lucide` 名称：

```text
导航：home search settings user map calendar chevron-left chevron-right chevron-down arrow-left arrow-up arrow-down
操作：plus minus x check edit trash share-2 more-horizontal power
通信/媒体：message-circle phone camera image mic mail play pause music volume-2 volume-x skip-back skip-forward repeat shuffle list-music cast timer sliders
状态：heart star bell lock eye clock wifi battery battery-charging cloud cloud-rain
环境/家居：sun moon thermometer wind snowflake flame droplet leaf lightbulb zap wand-sparkles sofa
文件：file-text folder
```

## 9. 控件、反馈与无障碍

- **原则**：同类控件行为一致，反馈清楚但克制；可操作性不能只靠颜色表达。
- **静态基线**：使用原生 `<button>`、`<input>` 和运行时样式；按钮按下、键盘焦点、禁用和主题状态由运行时处理。本参考只指导无脚本静态基线，首稿只表达完整结构、初始状态和惰性交互 hooks；每个交互按钮的可见反馈节点也在首稿中预声明，最终是否增强为交互版由 `SKILL.md` 的输出模式决定。
- **例外**：纯图标按钮必须用 `aria-label` 提供名称；装饰性 Symbol 从无障碍树隐藏。
- **禁止**：在静态源中编写 JavaScript、内联脚本、内联事件、远程依赖、无法聚焦的伪按钮、占位符代替输入名称或没有标签的图标操作。不把 `symbol`、`text` 或容器加上 `role="button"` 充当控件；交互模式所需的复杂反馈节点必须预先存在于静态 DOM，不得留给脚本动态创建。
- **Token/验证**：本项目将 44px 作为 Web 触控基线。checkbox、radio 和 toggle 的 `<label class="flex flex-row items-center w-full" data-component="row" data-ui-role="control-row">` 必须是完整的可点击行，把已标注的可见标签内容与 input 一起包在同一个 label 内。禁止另建外层横向 row 放文字，再让一个 `w-full` label 只包 input，否则 label 会占满父行并把文字压成逐字换行。slider 由运行时提供 44px 操作高度。

按钮使用 `type="button"` 并包含可读文字或 `aria-label`。所有 input 提供 `aria-label`；`radio` 同时提供非空 `name` 和 `value`，`slider` 同时提供 `min`、`max` 和 `value`。图片提供准确 `alt`。DOM 顺序、视觉顺序和键盘焦点顺序保持一致。

交互首稿中，带 `data-action` 的按钮以 `data-target` 指向展开、隐藏或内容变化的节点，或以 `data-feedback` 指向可见状态文字/标签；目标必须是另一个已标注节点。不得只为按钮本身翻转 ARIA 或 `data-*` 并把它当作用户反馈。

组件标注保持最小而完整：独立文字只用一个 `data-component="text"` 节点直接承载文字，整段字体 class 也写在该节点，不再套 `span` 组件；`span` 组件只用于 `text` 直属、非空、需要独立样式的局部富文本。普通 HTML `<span>` 不等于 ArkUI `span` 组件，默认不写 `data-component` 或 `data-node-id`。纯文字按钮直接写文字且不放已标注子组件；纯图标按钮只放一个 `symbol`；图标加文字时，按钮只直接包含一个已标注的 `row`，再在该 `row` 中并列 `symbol` 与 `text`。禁止混用按钮直属原始文字与组件子节点。

## 10. 组件样式决策

- 普通卡片：`bg-ui-surface rounded-ui-card p-ui-card`。
- 弱控件：`bg-ui-component-subtle rounded-ui-control`。
- 主要操作：`bg-ui-primary text-ui-on-primary rounded-ui-control`。
- 次要操作：`bg-ui-component-secondary text-ui-fg rounded-ui-control`。
- 列表：一个表面容器包住规则行；相邻行使用 `border-b-ui-hairline border-ui-divider`，末行不加。
- 图片：用户明确提供的图片优先。内容确实需要摄影图而用户未提供媒体时，可在原生 `<img data-component="image">` 上写简洁英文 `data-media-query`，可选 `data-media-orientation="portrait|landscape|squarish"`，并写稳定 `data-node-id`、准确 `alt`、`object-cover` / `object-contain` 及明确比例；首稿不写 `src`，由收尾器稳定选图、批内去重、补充相对 `src` 并只复制命中的离线文件。默认最多 3 张，明确要求图片密集内容时最多 8 张。不要枚举图库、读取 manifest、猜文件名、使用远程 URL 或为装饰索取图片；没有真实媒体价值时改用 surface、文字和 HarmonyOS Symbol。
- 内置图库覆盖范围：头像与棚拍人像；精致餐食、拉面、咖啡；耳机、手表、护肤品、球鞋；笔记本、手机、抽象科技；度假村泳池、水上屋、酒店客房；山林海景；朋友生活、家居、跑步；书籍静物、阅读、图书馆；办公室、桌面、会议；猫狗与野生动物；绘画、画廊、雕塑。`data-media-query` 应描述这些范围内可见的具体主体；需求超出覆盖范围时不要强行使用近似图片。
- 原生控件：使用运行时几何，不手绘 toggle、radio、checkbox、slider 或 input。

普通分组、重复行和静态分段内容默认使用 `column` / `row`，不要为了外观使用专用结构。只有确实需要对应 ArkUI 语义时才使用：`list` 只直接包含 `list-item`，每项最多包含一个 `row` 或 `column`；`grid` 只直接包含 `grid-item`；可见标签按钮行位于 `tabs` 外，`tabs` 写非负整数 `data-index`，内部只直接包含带非空 `data-tab-bar` 的 `tab-content`。

`scroll` 最多只放一个已标注直属子组件，多个内容节点先统一包进一个 `column`。`list` 的分隔线 class 写在相邻 `list-item` 上，不要把 `divider` 作为 `list` 的直属子组件。

方形操作优先使用 `size-10`；`h-10` 只用于确实需要 40px 高度的非方形布局，避免与 `size-10`、`w-10` 重复。列表分隔仍使用 `border-b-ui-hairline border-ui-divider`；只有真实 Tabs 的选中标签可使用 `border-b-2 border-ui-primary`，不要给所有标签都添加强调下划线。

只有概念边界存在时才增加表面。优先通过字体、留白和对齐建立层级，再考虑卡片、边框和阴影。

## 11. 可用 authoring class

- 显示与定位：`flex grid block hidden relative absolute inset-0`。
- 方向与换行：`flex-row flex-col flex-wrap`。
- 对齐：`items-start items-center items-end justify-start justify-center justify-between justify-end`。
- 网格：`grid-cols-1 grid-cols-2 grid-cols-3 grid-cols-4`。
- 尺寸：`w-6 w-10 w-full h-10 h-full min-h-screen min-w-0 flex-1 shrink-0 aspect-square aspect-video size-4 size-5 size-6 size-8 size-10`。
- 溢出与媒体：`overflow-hidden overflow-x-auto overflow-y-auto object-cover object-contain`。
- 文本：`text-left text-center text-right truncate line-clamp-2`。
- 语义间距：`p|px|py|pt|pb|pl|pr|m|mx|my|mt|mb-ui-{page,section,card,item,compact}` 与 `gap-ui-{section,card,item,compact}`。
- 小范围间距：`gap-1 gap-2 gap-3 gap-4 gap-6 p-0 p-2 p-3 p-4 px-2 px-3 px-4 py-2 py-3 py-4 mt-1 mt-2 mt-3 mt-4 mb-1 mb-2 mb-3 mb-4`。
- 边框：`border border-b border-b-2 border-b-ui-hairline border-t-ui-hairline border-ui-border border-ui-divider border-ui-focus border-ui-primary`。
- 表面与颜色：本文件第 6、7、10 节列出的所有 `bg-ui-*`、`text-ui-*`、`border-ui-*`、圆角和 `shadow-ui-surface`。

禁止发明工具类、任意方括号值、透明度后缀、反向 flex、grid span、按列流动 grid、fixed、sticky、生成侧 transform/filter/backdrop class。

## 12. 交付前六项快速自检

1. 第一阅读焦点是否唯一？
2. 是否把本可用留白分组的内容过度卡片化？
3. 是否只有一个明显主要操作？
4. 大区块、组内和微间距是否形成 24 / 12 / 8 / 4 的稳定节奏？
5. 文案是否具体、真实、没有占位内容和重复标题？
6. 390px 下是否可能横向溢出、裁切或产生无意义空白？

拒绝通用 dashboard、landing page、无意义 hero、装饰性渐变光晕、整页玻璃拟态、卡片墙、徽章泛滥和可识别页面模板。生成克制、针对当前任务、明显为当前内容定制的构图。
