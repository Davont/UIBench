# UIBench ArkUI export adapter

该目录实现 UIBench 专属的 HTML 元数据适配层。UIBench 负责理解
`data-component` 等定制标注，再生成标准 Screen IR v2；
`html-to-arkui` 只负责平台无关的契约校验、通用 HTML 转换和 ArkTS 渲染。

## 当前文件

- `component_registry.json`：UIBench 的 35 个 HTML 标注 key、业务分类和降级关系。
- `renderer_contract.json`：锁定的 `html-to-arkui` 公共组件契约快照。
- `components.py`：校验两层契约，只把渲染器真实支持的组件暴露给 Prompt。
- `metadata.py`：提取组件标注，生成 `uibench-component-manifest` 和导出诊断。
- `snapshot.py`：校验浏览器快照，并把白名单 computed style 映射到 Screen IR styles。
- `resources.py`：校验浏览器捕获的图片字节，去重并生成完整 HarmonyOS 工程 ZIP。
- `screen_ir.py`：把有效的 UIBench Component Manifest 转成标准 Screen IR v2。
- `exporter.py`：通过受限 JSON 子进程调用 `tools/arkui-export.mjs`。
- `visual_regression.py`：无额外图像依赖的 PNG 校验、像素指标和差异图生成。
- `regression.py`：版本化回归样本、工程准备、产物摘要和截图比较。

## 当前可导出组件

第一版只允许：

```text
column, row, stack, scroll, text, span,
image, symbol, divider, button
```

`list`、`grid`、`checkbox`、`text-input` 等仍保留在 UIBench 规划词汇中，
但会被标记为 `rendererSupported: false`，不能进入当前导出链路。渲染器扩展
公共契约后，UIBench 才能同步开放相应 Prompt 能力。

## HTML 标注示例

```html
<main data-node-id="page" data-component="scroll">
  <section data-node-id="page.content" data-component="column">
    <p data-node-id="page.title" data-component="text">标题</p>
    <button data-node-id="page.submit" data-component="button"
            data-action="submit">提交</button>
  </section>
</main>
```

- `data-node-id` 是稳定且全局唯一的小写路径。
- `data-component` 只表达基础结构或控件类型。
- `data-ui-role`、`data-repeat`、`data-item-key` 和 `data-action` 保留业务语义。
- `data-symbol` 必须是 `sys.symbol.*` 或 `app.symbol.*`，不能直接复制 Lucide 名称。
- 旧 HTML 可以不带标注，并继续使用通用 `generic` 转换模式，但不能保证语义。

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
- 实际 viewport、主题和 Token 主题。

后端把快照作为不可信输入处理：限制 HTML 为 2 MB、快照为 10000 个节点，并限制
字段长度和枚举，禁止
未知字段、NaN/Infinity 与重复 nodeId。能完整映射且没有其他 warning 时返回
`quality.readiness: ready`；缺节点、隐藏节点、Grid/反向 Flex、阴影、transform、filter、
背景图或非均匀边框等无法精确表达的属性会返回 `lossy`。

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
