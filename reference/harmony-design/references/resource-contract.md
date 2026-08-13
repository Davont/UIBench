# Resource Grounding Contract

本文件定义紧凑清单未覆盖、解析器失败或 Split Resource 不完整时的正式降级路径。正常页面生成由 `SKILL.md` 的三批流程和 `resolve-page-resources.mjs` 执行，无需单独读取本文件。

## 正式资源合同

`<SOURCE_ROOT>` 固定为 Skill 的 `src/`。Split Resource 五件套是唯一正式路由与资源合同：

```text
<SOURCE_ROOT>/route-index.md
<SOURCE_ROOT>/pages-specs/layout/{page_type}.md
<SOURCE_ROOT>/blocks-specs/blocks.json
<SOURCE_ROOT>/components-specs/components.json
<SOURCE_ROOT>/assets/assets.json
```

五项全部存在时，才能记录 `Split Resource: complete`。

不要通过 `src/components-specs/config.json`、根目录 `components.json` 或 alternate resource roots 推断资源模式。

## 三步 IO 合同

Grounding 只能使用 A1、A2、A3 三个 IO 批次：

- 同一批次中可并行读取的文件必须合并发出。
- A1 前不得增加项目探索、正式规划或 Source 预读。
- A3 必须合并 registry 与最终命中资源精读，不得按组件逐个拆成多轮预防性读取。
- 已读取文件不得在推导、实现、验证、日志或报告阶段重复读取。

### A1. Route

1. 读取 `<SOURCE_ROOT>/route-index.md`。
2. 根据用户意图匹配 `page_type`。
3. 同时检查 `hit_rules` 和 `exclusion_rules`。
4. 多候选时选择内容与布局重合度最高者，并记录排除原因。
5. 无规则命中时使用 `page-shell` fallback，不得把候选歧义伪装成无命中。

### A2. Layout

读取 `<SOURCE_ROOT>/pages-specs/layout/{page_type}.md`，优先提取：

- `hit_rules`
- `exclusion_rules`
- `layout_skeleton`
- `reference_blocks`
- `needed_components`
- `composition_mapping`
- `spatial_tokens`
- `page_primary_action_area`
- `generation_constraints`
- `validation_notes`
- `related_assets` / `asset_mapping`

### A3. Matched Resources

正常路径在 A3 运行：

```bash
node <STANDALONE_PAGE_GENERATION_SKILL_DIR>/scripts/resolve-page-resources.mjs <page_type> [--pattern <pattern-id>]
```

解析器读取并校验三份 registry，只输出 `references/page-resource-manifest.json` 中与当前 `page_type` 匹配的模板、组件、token、图标和 pattern。清单只用于收窄读取面，不替代正式 registry；任一清单项无法在 registry 或 `global.css` 中验证时，解析器必须失败。

仅当清单无对应 `page_type` 时执行以下 fallback：

1. 在同一批次读取 `blocks.json`、`components.json`、`assets.json`，只解析布局命中的条目。
2. design-system 模式在同一批次精读最终实现会直接使用的模板和稳定 TSX/API；standalone 模式精读 Skill 自身命中的 `src/pages/**` 模板源码与内置 `.md/.json` 规格，但不读取 registry 指向的 design-system Component/Block TSX/CSS。
3. standalone 模板 CSS 与 Story 只作为合并到 HTML `page-tsx` 节点内嵌 TSX 的实现证据；CSS、Story、`global.css`、pattern spec 和 HMSymbol 资料只有在已加载内容不足以支持实现时才加入 A3，不得另开预防性批次。
4. 拒绝指向生成目录的 registry 条目。
5. 已加载的数据直接进入推理阶段，不重复读取。

## Clean-room 边界

- 新建页面不得将历史 `src/render/**` 作为视觉或结构锚点。
- 允许读取当前已选定目标目录、用户明确要求继续/对比的历史 render、指定 baseline 和 Demo workspace。
- 未命中的组件、Block、CSS、Story、模板和资产目录不做预防性精读。
- `package.json` 只在确认验证命令或 page-build script 时读取。

## 缺失处理

五件套任一缺失时：

1. 记录缺失项。
2. 立即停止 route → layout → registry 解析。
3. design-system 模式不得回退 Skill 内置资源；standalone 模式不得搜索外部项目或 alternate resource roots。
4. 修复或重新同步资源后重试。

## Grounding 输出

```text
Split Resource: complete / incomplete (missing: ...)
Route candidates: ...
Matched page_type: ...
Excluded candidates: ...
Layout: ...
Matched blocks: ...
Matched components: ...
Matched assets / tokens / icons: ...
Fallback: none / reason and assumptions
```

资源解析不是独立交付。完成 grounding 后必须继续实现页面、执行源码验证并在完成报告中记录结果。
