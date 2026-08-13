---
name: harmony-design
description: 端到端生成或修改可独立运行的 HarmonyOS React 单页 HTML。匹配内置 route、layout、注册 Component/Block、token 与模板，并将完整可由 Babel 编译的 TSX 和内联样式写入一个 .shadcn.html 文件，同时使用本 Skill 自带的 vendor 与资源快照。适用于不在 design-system 工作区中交付独立 HTML 页面。不要用于 src/render、Storybook、page-workshop Demo 子页面、静态 HTML/dist/ZIP 的 design-system 项目交付；这些使用 page-generation 或 page-build。
---

# Standalone Page Generation

将当前 `SKILL.md` 的目录记为 `<STANDALONE_PAGE_GENERATION_SKILL_DIR>`。本 Skill 是自包含的：只读取自身 `src/`、`references/`、`scripts/` 与 `babel-render-tsx/`，不得读取或依赖任何 design-system 工作区、`page-generation` 或 `page-workshop`。

默认快速路径：

```text
锁定目标 → A1 Route → A2 Layout → A3 Resources → 合并模板并生成 HTML → 单文件验证 → 完成报告
```

不要启动浏览器、Storybook、截图、视觉审计或 page-build。不要创建独立规划阶段。

## 不可突破的边界

- 只生成或修改输出目录中的一个 `{page-name}.shadcn.html`；完整、可由 Babel 编译的 TSX 必须嵌入其 `page-tsx` 纯文本节点，不能降级为手写静态 HTML。
- 目标 HTML 必须位于 agent `<Artifact Folder>` 产物目录（即 `./.octo/<sessionId>/outputs/`。【路径约束】在运行任何脚本之前，先通过 `$env:OCTO_ARTIFACT_FOLDER` 或检查当前工作目录确定会话 artifacts 输出目录，确保 HTML 生成到正确的会话目录下，不得自行编造 sessionId 或路径。不得位于本 Skill 目录、任意 design-system 项目 `src/` 或系统临时目录；禁止自创 artifacts 文件夹；
- 完成后在对话中输出 `<artifact type="text/link">HTML 的绝对路径</artifact>`。
- 只从本 Skill 的 `src/pages/**` 读取模板。该目录只读，命中模板和嵌套模板均必须复制并合并到嵌入 TSX，不能保留 `@/pages/**`、相对页面模板或其他本地 import。
- 必须实际渲染至少一个注册的 `design-components` Component/Container；不得用原生元素或本地伪组件替代 Layout、registry 或模板命中的 Component/Block。
- 页面级 `NavigationContainer` 恰好一个；单轴集合使用 `ListContainer`，直接子项带 `pixso-list-item`；二维集合使用 `GridContainer`，直接子项带 `pixso-grid-item`。

## 1. 锁定目标与独立 Source Root

只使用用户输入及其提供的 PRD、DesignBrief 或 baseline，确定输出目录、kebab-case 页面名、中文标题与页面范围。范围不清且会改变信息架构时转回 `prd-prototype-scope` / `design-brief`。本阶段不读取 route、layout、registry、模板或历史产物。

`<SOURCE_ROOT>` 固定为 `<STANDALONE_PAGE_GENERATION_SKILL_DIR>/src`。缺少正式 grounding 文件时直接报错；不得访问 design-system 工作区补齐资源。

输出约定：

- HTML 名称为 `{page-name}.shadcn.html`，输出目录不再创建 artifact-id 子目录。
- 同一输出目录可保留其他历史 HTML；本次只修改指定页面文件。
- 共享 vendor 位于输出目录父目录 `design-system-vendor/`。存在时直接复用，不检查、不补齐、不覆盖。

## 2. 三批 Minimal Grounding

同一文件本次只读一次，同批可并行读取。

1. **A1 Route**：只读 `<SOURCE_ROOT>/route-index.md`，应用 `hit_rules` 与 `exclusion_rules`，得到 `page_type`；无命中使用 `page-shell`。
2. **A2 Layout**：只读 `<SOURCE_ROOT>/pages-specs/layout/{page_type}.md`，提取骨架、section/Block、组件、资产、空间约束、主操作区与验证约束；缺失直接报错。
3. **A3 Resources**：运行：

   ```bash
   node <STANDALONE_PAGE_GENERATION_SKILL_DIR>/scripts/resolve-page-resources.mjs <page_type> [--pattern <pattern-id>]
   ```

   精读内置 `.md/.json` 规格、命中 pattern、顶层模板的 TSX/CSS、递归解析到的所有嵌套页面模板和必需本地辅助源码。组件/Block 源码路径仅作为 package export 合同，不能读取外部项目源码。没有 manifest 条目时按 [`references/resource-contract.md`](references/resource-contract.md) 做 targeted-registry fallback。

仅在动态图标、名称失败或用户要求图标审计时读 [`references/hmsymbol-audit.md`](references/hmsymbol-audit.md)，仅在复杂集合时读 [`references/container-audit.md`](references/container-audit.md)，仅在 Shell 冲突时读 [`references/shell-contract.md`](references/shell-contract.md)。

输出 A3 摘要：目标、page_type、layout、模板/组件/Block/token/icon/pattern 与资源边界。

## 3. 合并并生成 HTML

1. 从顶层模板生成可编辑 TSX 与全部模板私有 CSS：

   ```bash
   node <STANDALONE_PAGE_GENERATION_SKILL_DIR>/scripts/prepare-template-merge.mjs \
     <顶层模板 .tsx> \
     --mode standalone \
     --source-root <SOURCE_ROOT> \
     --out <输出目录外的临时 merged.tsx> \
     --css-out <输出目录外的临时 merged.css> \
     --top-component <顶层组件名>
   ```

   脚本会递归并入嵌套模板、去重声明并输出 CSS（import 原样透传，不重写）。出现循环依赖、重名导出无法消解或规格缺失时直接报错。

2. 仅在合并产物上调整业务数据、局部结构和本地辅助代码。复合 Shell（如 `MobilePhoneShellTemplatePage`）的 `NavigationContainer`、`FloatingTitleBar`、`FloatingTab`、`Aibottombar` 等模板 JSX 必须保留；只允许微调 props，不能重写为自制 `<div>`。
3. 将模板私有 CSS 和新增样式写入组件内的 `<style>{styles}</style>`。推荐让 `const styles` 包含 `__TEMPLATE_CSS__` 占位符，并使用 `--css-file` 注入；不要假定 vendor CSS 包含模板私有 CSS。
4. 通过脚手架创建或更新 HTML：

   ```bash
   node <STANDALONE_PAGE_GENERATION_SKILL_DIR>/scripts/scaffold-standalone-html.mjs \
     <输出目录> <page-name> --title "<页面中文名称>" \
     --tsx-file <临时 merged.tsx> \
     --css-file <临时 merged.css>
   ```

   新文件只允许替换 title 与 `page-tsx` 节点；已有文件只替换 `page-tsx`。脚手架负责首次复制 HTML 壳与共享 vendor，并在成功后删除临时 TSX。不得生成独立 TSX、CSS、Story、entry、dist、ZIP 或图片文件。

## 4. 单文件验证与交付

运行：

```bash
node <STANDALONE_PAGE_GENERATION_SKILL_DIR>/scripts/validate-source-fast.mjs <输出目录>/<page-name>.shadcn.html
```

验证器只校验指定 HTML、其嵌入 TSX、HTML 壳、共享 vendor、package import、内联样式、无图片、Navigation/List/Grid 与 HMSymbol；不运行 TypeScript 或 ESLint，也不扫描同目录其他页面。

报告目标、page_type、layout、命中资源、验证结果和 HTML 绝对路径。

## 5. 提交到构建服务（仅在用户明确包含「打包」关键字时执行）

在 HTML 生成目录下运行：

```bash
# macOS / Linux
curl -fsSL -F "file=@<page-name>.shadcn.html" -o "<page-name>.shadcn.zip" http://10.68.143.77:5050/api/build/HarmonyOS
```

```powershell
# Windows (CMD & PowerShell)
curl.exe -fsSL -F "file=@<page-name>.shadcn.html" -o "<page-name>.shadcn.zip" http://10.68.143.77:5050/api/build/HarmonyOS
```

其中 `<page-name>` 替换为实际页面 kebab-case 名称。用户未说「打包」则跳过此步骤。

## 完成检查

- 使用且仅使用本 Skill 的资源，A1/A2/A3 与模板递归合并完成。
- 指定 HTML 位于合法 `<Artifact Folder>` 产物目录（`./.octo/<sessionId>/outputs/`），`page-tsx` 含完整 TSX，HTML 壳除 title 与 TSX 外保持模板原样。
- agent 对话框输出 `<artifact type="text/link">HTML 的绝对路径</artifact>`。
- 共享 vendor 位于输出目录同级，嵌入 TSX 无 CSS/动态 import 与任何图片引用。
- 模板私有 CSS 已进入内联 `<style>`，`__TEMPLATE_CSS__` 不残留；注册组件、导航、集合和 HMSymbol 验证通过。
