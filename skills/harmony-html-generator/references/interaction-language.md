# 鸿蒙 HTML 交互语言

当 `SKILL.md` 选择交互输出、且无脚本静态基线已经通过 `validate-html.mjs` 后读取本文件。这里约束页面级渐进增强；视觉、组件和 class 规则仍由 `design-language.md` 与静态校验器决定。

## 1. 增强边界

- 静态基线是唯一事实来源。不要在生成脚本时再次修改 `index.html`；增强器只会复制该目录、写入 `assets/app.js` 并注入唯一的 `<script src="assets/app.js" defer></script>`。
- `app.js` 只能操纵静态 HTML 已预声明的节点和状态。不得创建、删除、重排组件树，不得把字符串解析成 HTML。
- 无脚本时页面必须保持内容完整、阅读顺序正确、原生输入控件可用。脚本异常最多使增强行为失效，不能让基础内容消失。
- 所有状态只存在于当前页面进程的内存中。刷新可恢复初始状态；不要伪装成已保存、已同步或已提交到服务端。
- 交付物是离线 HTML/CSS/JavaScript，不调用 ArkUI/ArkTS 导出器。

## 2. 静态 DOM 契约

- 保留每个既有 `data-node-id` 的值、节点和父子关系。新交互只使用静态首稿中的 inert hooks：原生 `button` / `input` 触发控件写 kebab-case `data-action`；展开、隐藏或内容变化的目标写 `data-target="<data-node-id>"`；可见文字、状态或进度反馈写 `data-feedback="<data-node-id>"`。
- 每个 `data-target` / `data-feedback` 必须精确指向一个已存在且全局唯一的 `data-node-id`，不能指回触发控件自身。带 `data-action` 的按钮至少声明其中一个；原生 input 的值或选中状态本身可见，但影响其他内容时仍声明目标。复杂反馈、展开内容、标签面板和空状态必须预先存在；用 `hidden`、原生控件属性和 `aria-*` 表达初始状态。
- `data-target` 与 `aria-controls` 指向不同命名空间，不得混用。前者写目标的 `data-node-id`，后者写目标的原生 HTML `id`，例如触发器同时写 `data-target="player.queue" aria-controls="player-queue"`，目标写 `data-node-id="player.queue" id="player-queue"`。
- 操作使用原生 `button` 或合适的 `input`，不把 `symbol`、`text`、`span`、`div` 变成伪按钮。按钮保持 `type="button"`；表单演示不得产生真实提交。
- 交互脚本通过 `[data-action]`、`[data-node-id]` 和静态 `data-target` / `data-feedback` 建立引用，不依赖易变化的文案、DOM 顺序或纯视觉 class 选择节点。机械校验要求脚本可追踪地引用每个 action 和每个 target / feedback（使用对应 `data-node-id`、原生 `id` 或触发器 dataset）；它用于拦截“只在 HTML 声明、脚本完全未读取”的遗漏，不能替代对每个操作的实际点击验收。

## 3. 允许的状态变化

优先更新 DOM 自带状态：

- `hidden`、`checked`、`value`、`disabled`；
- `aria-expanded`、`aria-selected`、`aria-pressed`、`aria-hidden`、`aria-live`；
- 已预声明文字节点的 `textContent`；
- 聚焦到已经存在的合理目标；
- 在静态 HTML 已经出现且通过白名单校验的 class 之间切换。

一次动作同步更新视觉状态、可访问状态和控件状态。只翻转内存布尔值、`aria-*` 或不参与呈现的 `data-*` 不是完成的交互。标签页保持单选与面板对应；展开控件同步 `aria-expanded` 和目标可见性；状态按钮同时更新可见文字/class 与 `aria-pressed`；动态结果写入适当的 `aria-live` 区域。优先利用原生键盘行为，不重复模拟 `button`、checkbox、radio 或 slider 的键盘逻辑。

- Harmony Symbol 在收尾时已物化为固定字形；运行时改 `data-lucide` 不会更换肉眼可见的图标。需要播放/暂停、静音/恢复等图标切换时，在静态 DOM 中预声明两个已物化 Symbol，通过 `hidden` 切换，并同步更新可见状态文字。
- 用户要求“播放中、计时、倒计时、上传中”等持续过程时，活动期间必须让预声明的进度、时间或状态文字持续变化，暂停/结束后停止；不得只翻转 `playing` / `loading` 变量。
- 真实分享、跳转、网络提交、系统锁屏等超出离线页面边界的需求，用预声明面板或可见状态文字提供明确的本地演示反馈，不得静默地只写 `aria-pressed`。

## 4. 脚本约束

生成普通、无依赖的浏览器 JavaScript 源文件，不要输出 HTML 标签。允许使用 `addEventListener`、`dataset`、`querySelector(All)`、`Map`、`classList`、属性/属性值更新和页面内存变量。DOM 查询参数必须是静态字符串，并且只能是已存在的 `#id`、`[data-node-id]`、`[data-node-id="…"]`、`[data-action]` 或 `[data-action="…"]`；禁止动态、复合、class 和标签选择器。`classList` 的 class 名必须是静态 HTML 已声明的字符串字面量；允许用单个布尔变量在两个已声明的字面量之间做三元选择，禁止从变量、数组或拼接结果动态传入 class。读取 `data-target` 后，从预先建立的 `data-node-id` 映射中取目标，不把它拼进选择器。

禁止以下能力：

- 任何网络请求或远程资源，包括 `fetch`、`XMLHttpRequest`、`WebSocket`、`EventSource`、`sendBeacon` 和动态/静态 import；
- 持久化，包括 cookie、`localStorage`、`sessionStorage`、IndexedDB 和 Cache API；
- 动态代码或 HTML 注入，包括 `eval`、`Function`、`document.write`、`innerHTML`、`outerHTML` 和 `insertAdjacentHTML`；
- 导航、弹窗窗口、frame/worker、表单真实提交、下载，以及剪贴板、通知、定位、相机或文件系统等页面外副作用；
- 内联事件处理器、第二个脚本、模块脚本、远程脚本或 data/blob 脚本。
- 运行时改写 `data-lucide`。该属性是收尾期图标映射输入，不是运行时图标 API。

事件监听器只绑定静态页面中实际存在的 hooks。找不到可选节点时安全跳过；不要用异常作为正常分支，也不要吞掉会掩盖半初始化状态的错误。

## 5. 发布与回退

只把 JavaScript 源文件交给 `enhance-html.mjs`。增强器在 staging 中运行 `validate-interactive.mjs`，验证唯一 defer 脚本、静态契约、资源边界、危险 API 和 DOM 引用后再原子发布。

- `mode=interactive`：返回发布目录中的 `index.html`。
- `mode=fallback-static`：交互脚本或交互校验失败；增强器已经发布字节不变的静态副本。直接返回该静态页面，不重试生成、更改静态 DOM 或降低安全约束。
- 增强器非零退出：不应破坏已校验静态基线；返回其路径，并准确说明没有发布交互版。
