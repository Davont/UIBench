# HTML 转 ArkUI 初步可行性方案

> 更新时间：2026-08-12
> 状态：组件识别、浏览器快照、Screen IR、ArkTS 转换、静态资源物化、完整 HarmonyOS 工程导出和 HDC 回归链路已实现；三份样本已在 API 22 Phone 模拟器完成真实截图、显式归一化和首轮差异报告
> 参考项目：`/Users/beijixing/Desktop/html-to-arkui/`

## 一、结论

HTML 转 ArkUI 可行，但可行程度取决于目标范围。

| 目标 | 可行性 | 初步判断 |
| --- | --- | --- |
| 在 HarmonyOS 中直接展示 HTML | 高 | 可使用 ArkWeb `Web` 组件，但不属于原生 ArkUI 转换 |
| 固定 `390 × 844` 的静态 HTML 转原生 ArkTS 页面 | 中高 | 对 Pixso、设计稿导出等受限 HTML 方言较适合 |
| 当前 UIBench 生成的任意 Tailwind HTML 直接转 ArkUI | 低 | Tailwind、外部 Token CSS、Lucide 和响应式布局会大量丢失 |
| 响应式、交互完整、可直接上线的 ArkUI 工程 | 中低 | 需要中间 IR、资源处理、业务语义、工程生成和真实 SDK 验证 |

因此，`html-to-arkui` 可以作为转换器内核的原型，但不适合未经处理地直接串接在当前 UIBench HTML 输出之后。

长期更合适的方向是：

> 使用平台无关的 Screen IR 作为 HTML 和 ArkUI 的共同数据源；对历史或外部 HTML，通过浏览器先固化最终样式和布局，再进入 Screen IR。

## 二、目标边界

需要明确区分三种不同产物。

### 2.1 HTML 容器产物

使用 ArkWeb 加载本地或远程 HTML，视觉还原成本最低，可以继续运行网页布局和脚本。

它适合：

- 快速在 HarmonyOS 中展示现有网页。
- UIBench 设计稿预览。
- 对原生性能、组件语义和系统交互要求不高的场景。

它不等于 HTML 转原生 ArkUI，无法得到可继续按 ArkUI 组件维护的 `Row`、`List`、`Button` 等结构。

### 2.2 静态原生页面产物

将固定视口中的视觉结果映射成 `Row / Column / Stack / Text / Image` 等 ArkUI 组件。

它适合：

- 设计稿或营销页。
- 静态页面原型。
- 固定手机尺寸下的视觉迁移。

若以高视觉还原为第一目标，可以大量使用 `Stack + position`；代价是响应式、可维护性和语义较弱。

### 2.3 生产级原生应用产物

除视觉外，还需要生成或绑定：

- `List / Grid / WaterFlow / Swiper / Scroll` 等结构化布局。
- `Button / Search / TextInput / Tabs` 等交互组件。
- 页面状态、事件、导航、数据请求和错误处理。
- 图片、字体、Symbol、权限、路由和模块配置。
- 完整 HarmonyOS 工程及构建配置。

这一层不能仅依靠 CSS 语法映射完成，需要明确的组件和业务语义。

## 三、参考项目 `html-to-arkui` 分析

### 3.1 已有架构

参考项目已经形成比较清晰的转换链路：

```text
HTML 字符串
    ↓
parse5 解析 DOM
    ↓
css-tree 解析 CSS、计算受限级联
    ↓
HTML/CSS Lowering
    ↓
私有 UI IR
    ↓
ArkTS Renderer
    ↓
单个 .ets 源码字符串
```

核心模块包括：

- `src/dom.ts`：HTML 解析、安全过滤、复杂度限制。
- `src/css.ts`：选择器、级联、继承及不支持能力诊断。
- `src/lower.ts`：HTML/CSS 到 UI IR 的降级转换。
- `src/assets.ts`：图片、背景图和字体资源清单。
- `src/viewport.ts`：固定画布尺寸推断。
- `src/arkts/render.ts`：UI IR 到 ArkTS 源码。

### 3.2 优点

- 转换过程确定，相同输入能够得到稳定输出。
- 不执行 `<script>` 或内联事件。
- 有节点数、嵌套深度和数值范围限制。
- 能够显式报告不支持和近似转换，而不是静默丢失。
- 内部已经具有 diagnostics、assets、stats 和 confidence 等结构化结果。
- 支持 strict 和 best-effort 两种模式。
- 代码职责划分清晰，适合作为后续原型基础。

实际执行参考项目测试结果：

```text
Test Files  7 passed
Tests       110 passed
```

### 3.3 当前支持范围

目前主要支持：

- 文本、标题、段落和简单内联文本。
- `img`。
- 单行 flex row/column。
- 普通文档流容器。
- 明确的绝对定位和重叠层。
- 常见尺寸、间距、颜色、字号、字重和行高。
- 背景色、单背景图、线性渐变、圆角、统一边框和单层阴影。
- `object-fit`。

ArkTS Renderer 只输出以下五种组件：

```text
Row
Column
Stack
Text
Image
```

### 3.4 主要限制

当前不能完整处理：

- Tailwind CDN 在运行时生成的 CSS。
- 外部样式表。
- CSS Variables 和 `var()`。
- `calc()`、`min()`、`max()`、`clamp()`。
- 媒体查询和浏览器最终 used value。
- Grid、flex-wrap、复杂 intrinsic sizing。
- 滚动容器、虚拟列表和懒加载。
- 伪类、伪元素、attribute selector 和 sibling combinator。
- 富文本局部样式。
- SVG、Lucide、Canvas、WebGL、视频和表单控件。
- 业务事件、页面状态、路由和网络逻辑。
- HarmonyOS 工程、资源目录、权限和构建配置。

当前公开 API 只返回一个 ArkTS 字符串。正式接入时需要把内部的结构化结果升级为稳定公开契约，至少返回：

```ts
interface ConversionResult {
  code: string;
  diagnostics: Diagnostic[];
  assets: AssetManifest;
  stats: ConversionStats;
  confidence: ConfidenceBreakdown;
}
```

## 四、参考项目样例实测

参考项目自带的 `tests/fixtures/pixso-static.html` 属于它预期处理的固定画布方言。

实测结果：

| 指标 | 结果 |
| --- | ---: |
| 可见节点 | 11 |
| 成功处理的样式声明 | 80 |
| 有损声明 | 2 |
| confidence | 0.963 |
| ArkTS 行数 | 74 |

生成结果能正确包含：

- 固定 `390 × 844` 画布。
- Hero 背景图片。
- 绝对定位标题。
- 横向操作区及内部 Row。
- 图片尺寸、圆角、间距、字体和颜色。

同时仍会报告：

- `box-sizing` 不支持。
- `:hover` 选择器不支持。
- `transform` 不支持。
- 本地图片需要宿主工程物化。

这说明参考项目在“固定画布、内联静态 CSS、简单 flex/absolute”范围内具有实际价值。

## 五、当前 UIBench HTML 直接转换实测

UIBench 当前移动端生成协议要求：

- 使用 Tailwind CDN 工具类。
- 使用 Lucide CDN 和运行时脚本生成图标。
- 使用 `/design-tokens.css` 外部样式表。
- 不写自定义 `<style>`。
- 不用内联 `style` 完成布局。
- 使用响应式类适配不同手机。

这些约束与参考转换器的输入假设基本相反。

对 `logs/20260810_193313/` 中 5 个真实商城页面进行直接转换，结果如下：

| 模型页面 | 成功处理的 CSS 声明 | error 数 | 主要结果 |
| --- | ---: | ---: | --- |
| DeepSeek v4 Flash | 0 | 37 | 退化为 Column/Text/Image |
| Doubao Seed 2.1 Turbo | 0 | 37 | 退化为 Column/Text/Image |
| GLM 5.2 | 3 | 65 | 大量布局及元素损失 |
| Kimi k2.6 | 0 | 38 | 退化为 Column/Text/Image |
| MiniMax M3 | 0 | 33 | 退化为 Column/Text/Image |

五个结果均没有生成 `Row` 或 `Stack`。主要原因是转换器只看到了 class 名，却没有 Tailwind 运行后对应的 CSS。

典型损失包括：

- Tailwind 布局、间距、颜色、尺寸完全未解析。
- `/design-tokens.css` 被当作无法读取的外部样式表。
- Lucide 脚本不会执行，生成的 SVG 图标不存在。
- HTML 中已有的 SVG 会被判定为不支持元素。
- 图片缺少最终渲染尺寸。
- input、select、textarea 等表单控件被丢弃。
- 内联格式、滚动和固定导航无法保留。

### 5.1 confidence 指标问题

这些页面在视觉结构明显失真的情况下，confidence 仍然达到约 `0.686～0.755`。

原因是当前公式把“成功遍历的可见 DOM 节点”计入主要分子，即使这些节点没有成功解析任何 CSS，也会提高分数。

正式方案不能使用单一 confidence 作为发布门禁，建议拆成：

- DOM/内容覆盖率。
- CSS 最终样式覆盖率。
- 组件语义覆盖率。
- 资源解析率。
- ArkTS 编译结果。
- 浏览器与 ArkUI 截图视觉相似度。

## 六、推荐总体架构

```text
                        ┌──────────────────────┐
现有 UIBench HTML ─────▶│ 浏览器样式与布局固化 │
                        │ computedStyle        │
                        │ boundingClientRect   │
                        └──────────┬───────────┘
                                   │
新生成 manifest + tokens ──────────┤
                                   ▼
                        ┌──────────────────────┐
                        │ 平台无关 Screen IR   │
                        │ node / layout / text │
                        │ asset / action/token │
                        └──────────┬───────────┘
                                   │
                   ┌───────────────┴───────────────┐
                   ▼                               ▼
       ┌─────────────────────┐         ┌─────────────────────┐
       │ 结构化原生 ArkUI    │         │ 高保真静态 ArkUI    │
       │ Row/List/Grid/...   │         │ Stack + absolute    │
       └──────────┬──────────┘         └──────────┬──────────┘
                  └───────────────┬───────────────┘
                                  ▼
                       ┌──────────────────────┐
                       │ 资源与工程物化       │
                       │ media/font/route/... │
                       └──────────┬───────────┘
                                  ▼
                       ┌──────────────────────┐
                       │ SDK 编译 + 截图验证  │
                       └──────────────────────┘
```

### 6.1 浏览器固化层

针对现有自由 HTML，在固定视口中真正加载：

- Tailwind CDN 或本地编译后的 Tailwind CSS。
- UIBench Design Token CSS。
- 字体和允许使用的图片。
- Lucide 图标生成逻辑。

然后提取每个可见节点：

- `getComputedStyle()` 最终值。
- `getBoundingClientRect()` 几何信息。
- 文本、图片、背景、边框、圆角、阴影和透明度。
- DOM 层级、绘制顺序和 overflow 信息。
- `data-node-id`、`data-component` 和 ARIA 语义。
- 当前固定主题与明暗模式。

这一步解决 Tailwind、CSS Variables、级联、字体、百分比和媒体查询的最终值问题。

### 6.2 Screen IR

建议将 UIBench 规划中的 `manifest.json` 扩展为平台无关的 UI IR，而不是把 HTML AST 直接当作长期 IR。

示意结构：

```json
{
  "viewport": { "width": 390, "height": 844 },
  "theme": "harmonyos",
  "mode": "light",
  "root": {
    "id": "home",
    "semantic": "screen",
    "layout": { "kind": "column" },
    "children": []
  },
  "assets": [],
  "diagnostics": []
}
```

节点至少应表达：

- 稳定 ID 和来源 DOM 路径。
- 组件语义。
- 布局类型和几何尺寸。
- 文本及文本 runs。
- 图片和 Symbol 资源。
- 颜色、字体、间距、圆角、边框和阴影。
- 可选事件语义，例如 `navigate`、`submit`、`select-tab`。
- 转换置信信息和 fallback 策略。

现状注记：稳定 ID 已由 `data-node-id` 全链路落实；「来源 DOM 路径」尚未实现——
Screen IR 契约的 `meta.htmlPath` 是可选字段，UIBench 当前只输出 `nodeId`、
`htmlTag` 与 `bbox`，manifest 记录 `tag` 与 `parentNodeId`。单槽包裹等生成节点
（`<id>:item`、`<id>:content`）没有 DOM 来源，只有稳定 nodeId。

### 6.3 ArkUI Mapper

建议提供两种输出策略。

#### 结构化模式

从 DOM 语义、组件标记和几何关系推断：

- flex row → `Row`
- flex column → `Column`
- 可滚动重复条目 → `List/ListItem`
- 二维商品布局 → `Grid/GridItem`
- 轮播 → `Swiper`
- 搜索输入 → `Search`
- 普通输入 → `TextInput`
- 按钮 → `Button`
- 富文本 → `Text + Span` 或 StyledString
- 图标 → `SymbolGlyph` 或本地 Image 资源

优点是更原生、响应式和可维护；缺点是布局推断复杂，视觉结果可能与浏览器有差异。

#### 固定画布模式

将浏览器中最终坐标映射为 `Stack + position`。

优点是第一阶段更容易接近截图；缺点是：

- 设备适配弱。
- 字体变化容易造成偏差。
- 结构语义和可维护性弱。
- 不适合作为最终生产代码。

第一阶段可以用固定画布模式建立视觉基线，再逐步把稳定结构替换成原生组件。

### 6.4 工程和资源物化层

正式输出不能只有一个 `.ets` 字符串，还需要：

- HarmonyOS 工程模板。
- 页面文件和路由注册。
- `resources/base/media/` 图片。
- 字体资源和注册代码。
- URL 到 `$r('app.media.*')` 的映射。
- 网络图片权限及加载失败占位。
- `module.json5`、`build-profile.json5`、`oh-package.json5`。
- 目标 API Version 和兼容性配置。

### 6.5 ArkUI 组件识别应先于 HTML 标注协议

组件识别不能从“HTML 中出现一个纵向容器”直接推导为 `Column`。在 ArkUI 中，
普通布局、可滚动内容和重复数据集合属于不同组件类别：

| 类别 | 第一批目标组件 | 识别重点 |
| --- | --- | --- |
| 普通布局 | `Column`、`Row`、`Stack`、`Scroll` | 顺序、重叠和滚动能力 |
| 数据集合 | `List/ListItem`、`Grid/GridItem`、`Swiper` | 重复数据、子项约束和复用语义 |
| 基础显示 | `Text/Span`、`Image`、`SymbolGlyph`、`Divider` | 内容类型和资源类型 |
| 输入操作 | `Button`、`Search`、`TextInput`、`Checkbox`、`Radio`、`Toggle` | 状态、值和事件语义 |
| 导航容器 | `Tabs/TabContent`、`Navigation/NavDestination` | 页面或内容切换关系 |
| 业务复合组件 | `ProductCard`、`AppBar`、`BottomNavigation` 等 | 通过基础 ArkUI 组件组合生成 |

其中几组边界必须在注册表中明确：

```text
少量普通内容纵向排列
    → Column

重复数据 + 纵向滚动
    → List/ListItem

重复数据 + 二维排列
    → Grid/GridItem

普通长内容需要滚动
    → Scroll + Column/Row/Stack

子元素相互覆盖或绝对定位
    → Stack

可映射的系统/自定义 Symbol 图标
    → SymbolGlyph

摄影图片、商品图片、品牌 Logo
    → Image
```

无鸿蒙对应资源的图标不回退为 `Image`：图标节点没有现成的图片资源，回退到
`Image` 会因缺少 `src` 阻断导出。实际导出策略是先查经人工核对的近似字形表，
命中则替换为近似 Symbol 并记 `ARKUI_SYMBOL_APPROXIMATED` 警告；仍无命中则退化
为等大的空占位（`column`）并记 `ARKUI_SYMBOL_UNAVAILABLE` 警告，布局不变。

`Scroll` 不是 `Column` 的替代品，而是为一个实际布局容器增加滚动能力；
`SymbolGlyph` 是叶子显示组件，不是布局容器。

正式实现前应建立版本化的 ArkUI 组件注册表。每个条目至少记录：

- 平台无关组件 key。
- 对应 ArkUI 组件名称。
- 组件类别和计划阶段。
- 允许的父子组件。
- 最大直接子组件数量等结构限制。
- 状态、值和事件属性。
- 无法生成目标组件时的 fallback。
- 后续需要核对的最低 API Version 和系统能力。

### 6.6 HTML 组件元数据契约

HTML 中的结构映射和业务语义应分开表达：

```html
<section
  data-node-id="shop.products"
  data-component="grid"
  data-ui-role="product-grid"
  data-repeat="products"
  data-columns="2"
>
  <article
    data-node-id="shop.products.item-headphones"
    data-component="grid-item"
    data-ui-role="product-card"
    data-item-key="headphones"
  >
    <img
      data-node-id="shop.products.item-headphones.image"
      data-component="image"
      src="headphones.png"
      alt="无线耳机"
    >
    <button
      data-node-id="shop.products.item-headphones.add"
      data-component="button"
      data-action="cart.add"
    >加入购物车</button>
  </article>
</section>
```

第一版属性职责如下：

| 属性 | 职责 |
| --- | --- |
| `data-node-id` | 稳定、唯一的可寻址节点身份 |
| `data-component` | 组件注册表中的结构或控件 key，例如 `grid`、`button` |
| `data-ui-role` | 可选业务复合语义，例如 `product-card`、`app-bar` |
| `data-slot` | 复合组件内部的 image/title/action 等插槽 |
| `data-repeat` / `data-item-key` | 重复数据集合与条目身份 |
| `data-action` | 行为引用；不在 HTML 中承载业务实现 |
| `data-symbol` | Symbol/Lucide 的平台无关图标名称 |

HTML 原生语义仍然优先保留，例如 `<button>`、`<input type="checkbox">`、
`checked`、`disabled`、`role="search"`。`data-component` 用于确认目标组件和表达
HTML 标签无法覆盖的集合/布局语义，不应覆盖与原生标签明显冲突的类型。

识别优先级定义为：

```text
1. 通过注册表校验的 data-component
2. HTML 标签、type、role、checked、disabled 等原生语义
3. manifest 中的组件、重复数据和行为定义
4. 浏览器 computed style 与最终几何信息
5. DOM 重复模式和布局启发式推断
6. 无法识别时退化为 Column/Row/Stack，并输出诊断
```

第 1 条声明的是组件类型；当浏览器实测布局能唯一确定与声明不同的结果时，导出按
证据落地并产生 notice 级诊断，而不是把责任推回 Prompt：`row` / `column` 按
computed `display` 与 `flex-direction` 落成实际方向
（`UIBENCH_ARKUI_LAYOUT_FOLLOWS_BROWSER`），`list` / `grid` 的裸组件子项被包进
生成的 `ListItem` / `GridItem`（`ARKUI_LIST_CHILD_WRAPPED_AS_ITEM` /
`ARKUI_GRID_CHILD_WRAPPED_AS_ITEM`）。完整的偏差与诊断档位表见
`uibench/arkui/README.md`。

对旧 HTML，缺少元数据只产生覆盖率提示，不影响浏览器预览；对新生成 HTML，以下情况应
产生确定性诊断：

- `data-component` 不在组件注册表中。
- 组件节点缺少或重复 `data-node-id`。
- `List` 的直接组件子项不是 `ListItem`。
- `Grid` 的直接组件子项不是 `GridItem`。
- `Tabs` 的直接组件子项不是 `TabContent`。
- HTML 原生控件语义与显式 `data-component` 冲突。
- `SymbolGlyph` 缺少可解析的 `data-symbol` 或 Lucide 名称。

## 七、与 UIBench 当前产品方向的关系

UIBench 当前规划的核心是：

> 生成、筛选和持续修改高质量移动端设计稿的工作台。

当前设计产物已经规划为：

```text
design-version/
├── screen.html
├── tokens.json
├── manifest.json
└── preview.png
```

这个结构天然适合后续扩展 ArkUI exporter：

```text
screen.html   → 浏览器预览和历史 HTML 导入
tokens.json   → ArkUI 主题和 Resource 映射
manifest.json → Screen IR 和组件语义
preview.png   → HTML/ArkUI 视觉验收基线
```

建议 ArkUI 不改变 UIBench 当前主链路，而是作为可选的下游导出能力：

```text
设计生成/编辑
      ↓
设计版本产物
      ├── HTML Preview
      └── ArkUI Export
```

这样可以避免 ArkUI 转换的复杂度阻塞设计生成、筛选和编辑能力。

## 八、分阶段实施建议

### 阶段 0：定义验收口径

先建立 ArkUI 组件注册表和 HTML 元数据契约，并确定第一版只承诺：

- 移动端固定 `390 × 844`。
- 单页面静态视觉。
- Light + HarmonyOS Token 主题。
- 文本、图片、基础容器和简单图标。
- 输出能够被指定版本的 HarmonyOS SDK 编译。
- 不承诺业务交互、响应式和完整工程逻辑。

注册表第一批覆盖 `Column`、`Row`、`Stack`、`Scroll`、`Text`、`Span`、`Image`、
`SymbolGlyph`、`Divider` 和 `Button`；第二批再加入 `List/ListItem`、`Grid/GridItem`、
`Swiper`、搜索/输入/选择组件及 `Tabs/TabContent`。

### 阶段 1：浏览器固化 PoC

选择 UIBench 中 5～10 个真实移动页面：

1. 让新生成 HTML 为关键容器、集合和控件输出合法的组件元数据。
2. 校验 ID 唯一性、组件词表、父子约束和原生标签冲突。
3. 在浏览器中加载完整 Tailwind、Token 和 Lucide。
4. 导出 metadata、computed style、bbox、文本和图片。
5. 生成固定画布 Screen IR。
6. 使用 `Stack / Text / Image` 及明确识别的 Row/Column 生成静态 ArkTS。
7. 完成资源下载和本地资源引用。
8. 在真实 HarmonyOS 工程中编译。
9. 采集 ArkUI 截图，与浏览器截图比较。

阶段目标是证明“现有 UIBench HTML 能够转换成可编译、视觉基本一致的静态 ArkUI 页面”。

### 阶段 2：结构化原生组件

逐步加入：

- Row/Column 布局推断。
- List/Grid/Scroll/Swiper。
- Button/Search/TextInput/Tabs。
- Span/SymbolGlyph。
- Design Token 到 ArkUI Resource 的稳定映射。
- 固定导航、安全区和沉浸式布局。

### 阶段 3：生成协议升级

要求新生成页面提供：

- `data-node-id`。
- `data-component`。
- 明确的重复列表语义。
- Token 引用。
- 受限事件语义。
- manifest/Screen IR。

新页面可以直接从 Screen IR 生成 HTML 和 ArkUI，不再依赖反向解析。

### 阶段 4：生产工程能力

最后再考虑：

- 状态管理。
- 页面导航。
- 数据绑定和网络请求。
- 深浅色与多设备响应式。
- 可访问性。
- 完整工程和持续构建。
- 自动修复和人工编辑回写。

## 九、验收指标

第一阶段不应只使用代码是否生成或 confidence 数值判断成功。

建议至少包含：

| 指标 | 说明 |
| --- | --- |
| SDK 编译成功率 | 生成页面必须通过指定 HarmonyOS SDK 编译 |
| 资源解析率 | 可见图片、字体和图标是否均有可用映射 |
| 内容覆盖率 | 页面可见文本和图片是否完整保留 |
| 组件语义覆盖率 | 可识别节点是否映射为正确 ArkUI 组件 |
| error diagnostics | 是否存在阻断视觉或结构的转换错误 |
| 截图视觉差异 | 浏览器与 ArkUI 同视口截图的差异 |
| 确定性 | 同一输入和配置是否生成完全一致的结果 |
| 人工修改成本 | 导出结果需要多少人工调整才能进入下一阶段 |

截图差异需要在建立样本基线后再确定阈值，不应提前用单一像素比例作为质量结论。

## 十、主要风险

### 10.1 浏览器视觉不等于 ArkUI 视觉

字体 shaping、行高、自动换行、阴影、渐变和图片裁剪都可能存在平台差异。

### 10.2 高保真和原生结构存在冲突

大量绝对定位容易接近截图，但难以适配设备；结构化组件更原生，但可能产生视觉偏差。

### 10.3 HTML 缺少业务语义

从一个 `<div>` 或 `<button>` 无法可靠推断它应该触发导航、筛选、加购还是提交。生产交互必须依赖 manifest 或额外协议。

### 10.4 图标和资源处理复杂

Lucide 当前依赖脚本生成 SVG，需要转换为 Symbol、本地 SVG/PNG 或 ArkUI 可用资源。远程图片还涉及下载、版权、缓存、权限和失败处理。

### 10.5 转换器可能被误当作完成度很高

“生成了 ArkTS 字符串”不等于“视觉正确”，也不等于“工程可编译和可上线”。产品界面必须明确区分 warning、error、preview-only 和 production-ready。

## 十一、初步决策建议

1. 保留 `html-to-arkui` 的 DOM、CSS 诊断、资产清单和 ArkTS Renderer 思路。
2. 不直接扩大它成为完整浏览器 CSS 引擎。
3. 在它前面增加浏览器样式/几何固化层。
4. 把 UIBench 的 manifest 演进为平台无关 Screen IR。
5. 第一阶段使用固定画布模式验证可编译性和视觉效果。
6. 后续逐步扩展结构化 ArkUI 组件映射。
7. ArkUI exporter 保持为 UIBench 的可选下游能力，不阻塞当前设计工作台主线。
8. 当前已完成组件注册表、Manifest、浏览器样式/几何固化、Screen IR v2、ArkTS Renderer、首批图片资源物化、完整 HarmonyOS Stage 工程生成、离线截图回归框架和 HDC 采集器；三份样本已在真实 API 22 模拟器闭环，当前处于阈值校准阶段。

## 十二、当前执行状态

截至 2026-08-12，已完成第一批可执行基础设施：

| 工作项 | 状态 | 当前结果 |
| --- | --- | --- |
| ArkUI 组件注册表 | 已完成 | UIBench 保留 35 个规划标注 key；另锁定 `html-to-arkui` contract v2，只开放其真实支持的 14 个组件 |
| HTML 组件元数据协议 | 已完成 | 支持 `data-node-id`、`data-component`、`data-ui-role`、集合、动作和规范 Symbol 元数据 |
| 元数据解析与校验 | 已完成 | 可识别显式标注和原生 HTML 控件，诊断重复 ID、未知/未支持组件、标签冲突、必填字段及父子约束 |
| UIBench 生成提示词接入 | 已完成 | ArkUI 元数据改为显式开关；Prompt 只允许当前渲染器支持的 14 个组件 |
| Manifest 持久化 | 已完成 | 使用 `uibench-component-manifest`/`manifestVersion` 与 Screen IR 版本明确分层，并保存覆盖率、就绪状态和诊断 |
| Screen IR v2 适配器 | 已完成 | UIBench 标注可转换为标准 `schemaVersion: 2` 的组件树、文本、图片和 Symbol props |
| Node 导出桥与 API | 已完成 | `POST /api/arkui/export` 支持 annotated 结构导出与 generic best-effort 兜底，可输出 ArkTS |
| 自动化测试 | 已完成 | 自动化测试覆盖注册表同步、解析器、浏览器快照、样式映射、资源物化、Screen IR、Node 桥、导出 API、PNG 差异、原子化报告、失败降级、并发互斥、HAP provenance、HDC 探测/同 bundle UI 子树/截图/清理、显式截图归一化、回归构建/报告和原有生成链路 |
| 浏览器样式与几何固化 | 已完成 | 导出时在不可见 390×844 sandbox iframe 中等待字体/图片与双帧布局稳定，采集白名单 computed style、bbox、可见状态和主题 |
| 快照安全与降级诊断 | 已完成 | 限制请求/节点/字段，拒绝未知字段、重复 nodeId 和非有限数；缺失节点及未映射视觉属性返回 `lossy` |
| 图片资源物化 | 已完成（首批） | 浏览器侧无凭证读取已渲染的 PNG/JPEG/GIF/WebP 图片和简单背景图；后端按签名校验、SHA-256 去重并生成 `resources/base/media` 与 `$r('app.media.*')`；不在服务端抓取 URL |
| 完整 HarmonyOS 工程 | 已完成 | 输出 DevEco Studio 6.0.2 / HarmonyOS SDK 6.0.2（API 22）的单 `entry` Stage 工程，包含 app/module/build/Hvigor/oh-package 配置、UIAbility、页面路由、默认图标和静态资源；排除签名、本机路径、IDE 缓存及依赖目录 |
| HarmonyOS SDK 编译 | 已完成（基线） | 最小工程壳和包含真实 Screen IR、`$r('app.media.*')` 图片的导出样例均已通过本机 API 22 ArkTS 编译并生成 unsigned HAP；在线导出请求不重复执行 SDK 编译 |
| ArkUI 截图差异 | 已完成首轮真实闭环 | 已建立 `typography`、`stack-card`、`scroll-feed` 三份 390×844 样本并通过 API 22 编译；在 HarmonyOS 6.0.2 Phone 模拟器采集 1320×2856 原始截图，以显式全屏 crop 和确定性 `area-v1` 归一化到 390×844，再生成差异图。三份结果均为无阈值的 `observed`：MAE/RMSE 分别为 5.406638/23.474475、3.607066/14.023990、4.753786/22.026075，尚未定义 `passed` 阈值 |

当前诊断采用“记录但不阻塞 HTML 预览”的策略：元数据错误会进入 Manifest，避免组件识别能力影响现有 UIBench 主流程；进入 ArkUI Export 时再将错误提升为导出阻断条件。浏览器快照覆盖完整且所有样式和资源都有 Screen IR 表达时可返回 `ready`；否则返回 `lossy`。这里的 `ready` 表示当前转换契约内无已知损失；工程生成器已有 API 22 编译基线，但单次导出的 `ready` 仍不等于该页面已经逐次 SDK 编译、截图一致或生产可用。

## 十三、后续实施路线

后续工作的重点不再是继续扩充工程壳，而是用真实样本验证视觉效果，再根据差异有顺序地补齐组件、资源和交互能力。

### 13.1 建立浏览器与 ArkUI 截图回归基线（最高优先级）

先选取 3～5 个有代表性的 UIBench 页面打通流程，稳定后扩充到 10～20 个样本。样本至少应覆盖：

- 纯文本与多级排版页面。
- Row/Column 混合布局。
- Stack 叠层、圆角卡片、阴影和背景图。
- 长页面与 Scroll。
- 图片裁剪、按钮和图标。

每个样本执行相同的质量链路：

1. 在固定 390×844 视口采集浏览器截图。
2. 固化 computed style、bbox、文本和资源，生成 Screen IR。
3. 导出完整 HarmonyOS 工程。
4. 使用指定 HarmonyOS SDK 编译工程。
5. 在相同视口采集 ArkUI 截图。
6. 生成浏览器图、ArkUI 图和差异图，并记录转换诊断。

首轮重点排查字体、字号和行高、文本换行、状态栏与安全区、图片裁剪、滚动区域、圆角、阴影和渐变。差异阈值应在样本基线形成后确定，不能只用单一像素差作为成功标准。

### 13.2 扩展结构化原生组件

按照页面出现频率和视觉收益逐步扩展组件契约：

1. `List / ListItem`、`Grid / GridItem`。
2. `Checkbox / Radio / Toggle`。
3. `TextInput / Search`。
4. `Tabs / Swiper`。
5. `Navigation` 及固定导航区域。

组件识别遵循“显式元数据优先、HTML 原生语义其次、布局特征推断最后”的顺序。无法可靠识别的节点继续使用通用布局表达，并输出可追踪的 `lossy` 诊断，避免错误地把普通容器强行识别成业务组件。

### 13.3 增加受控交互转换

不尝试翻译任意 JavaScript，只支持可以通过协议明确描述的交互：

- `data-action` 到 ArkUI 事件回调。
- 显式状态到 `@State`。
- 页面跳转到受控路由调用。
- 重复数据到 `ForEach`。
- Checkbox、Tabs、输入框等组件的有限状态联动。

复杂业务逻辑、网络请求和第三方脚本保留为人工接入点，并在导出报告中明确标记。

### 13.4 完善资源管线

在现有 PNG/JPEG/GIF/WebP 支持基础上继续补齐：

- SVG 与 Lucide 图标的稳定转换。
- 自定义字体下载、授权检查、工程资源生成和回退策略。
- 跨域资源抓取失败时的占位图和人工补充入口。
- CSS 渐变、阴影及复杂背景的降级规则。
- 图片压缩、尺寸约束、重复资源统计和工程体积报告。

### 13.5 增加工程导出参数

当前固定工程壳可逐步开放以下配置，同时保留可复现的默认值：

- 应用名、Bundle Name、页面名和模块名。
- HarmonyOS API/SDK 基线。
- 目标设备类型、画布尺寸和安全区策略。
- 浅色/深色主题。
- 仅下载源码工程、编译验证、同时输出 unsigned HAP 三种模式。

日常获取和二次开发以完整工程 ZIP 为主；批量自动化场景仍可直接消费 ETS、静态资源和导出清单。

### 13.6 建立自动化质量门禁

后续 CI 或批量任务至少应检查：

- 导出 API 成功且输出文件确定性一致。
- HarmonyOS SDK 编译成功。
- 文本、图片和组件覆盖率不低于基线。
- 不出现新的 error 级诊断。
- 截图差异没有超过样本允许阈值。
- 失败时保存工程 ZIP、构建日志、两端截图和差异图，便于复现。

### 13.7 推荐执行顺序

1. 先完成 3～5 个页面的截图回归闭环。
2. 根据真实差异修正现有 Row/Column/Stack/Scroll/Text/Image 渲染。
3. 将样本扩展到 10～20 个，并对每个导出工程执行 SDK 编译。
4. 再加入 List/Grid 和常见表单组件。
5. 随后实现受控交互、资源增强和导出参数化。
6. 最后建立持续构建与截图质量门禁。

当前已完成截图回归基线的浏览器侧、导出侧、编译侧、HDC 环境预检/HAP 校验/安装启动截图链路、显式归一化和离线比较工具。回归工程采用独立 v2 测试壳：在不改规范 `page.ets` 的前提下隐藏系统栏、固定 390×844 设计视口并按显示密度等比放置。采集器不会保存设备连接键原文，也不会生成或打包签名材料；原始整屏图无论宽高是否碰巧一致都不会自动比较。`capture(raw + layout) → normalize(显式 crop/viewport/area-v1) → compare` 三步必须分开执行。真实模拟器闭环还推动了两项通用修正：只有浏览器证据表明文本宽度为内在 `auto` 时才省略 ArkUI Text 硬宽度，以及为 ArkUI `Scroll` 显式设置 `TopStart` 对齐。下一项直接任务是扩展更多字体、表单和长页面样本，分离系统抗锯齿噪声与转换误差后，再为每个样本提交可解释的验收阈值；真机链路另需受设备信任的调试签名。

## 十四、参考资料

### 本地项目

- `/Users/beijixing/Desktop/html-to-arkui/README.md`
- `/Users/beijixing/Desktop/html-to-arkui/src/index.ts`
- `/Users/beijixing/Desktop/html-to-arkui/src/internal.ts`
- `/Users/beijixing/Desktop/html-to-arkui/src/dom.ts`
- `/Users/beijixing/Desktop/html-to-arkui/src/css.ts`
- `/Users/beijixing/Desktop/html-to-arkui/src/lower.ts`
- `/Users/beijixing/Desktop/html-to-arkui/src/assets.ts`
- `/Users/beijixing/Desktop/html-to-arkui/src/arkts/render.ts`
- `/Users/beijixing/Desktop/UIBench/uibench/prompts.py`
- `/Users/beijixing/Desktop/UIBench/uibench/design_tokens/`
- `/Users/beijixing/Desktop/UIBench/README_REQUIREMENTS.md`

### 官方资料

- ArkUI 开发入门：<https://developer.huawei.com/consumer/cn/arkui/devstart/>
- ArkWeb 应用侧与前端页面数据通道：<https://developer.huawei.com/consumer/cn/doc/HarmonyOS-Guides/web-app-page-data-channel>
