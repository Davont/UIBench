# HMSymbol 查找与校验

页面或 Story 使用 `HMSymbolIcon`、`iconName`、`hmSymbolName`、`hmsymbolName`、`symbolName` 等 Harmony 图标字段时读取。

## 实现前：三级查找

严格按顺序查找，每个图标命中后停止：

1. `<SOURCE_ROOT>/assets/hmsymbol/hmsymbol-icons-common.md`
2. `<SOURCE_ROOT>/assets/hmsymbol/hmsymbol-index.md`
3. `node skills/01-resource-injection/shadcn/scripts/search-hmsymbol.mjs <关键词>`

禁止：

- 跳过前两级直接读取 `hmsymbol-map.json`
- 凭记忆猜名称
- 用 emoji、Lucide 或普通文本字符替代 Harmony 系统图标
- 在 JSX 里直接写私有码位

页面本地数据优先使用 `HMSymbolIconName`，外部 API 必须为 `string` 时仍需校验所有字面量默认值和 Story 入参。

## 实现后：精确校验

```bash
node <STANDALONE_PAGE_GENERATION_SKILL_DIR>/scripts/check-hmsymbol-usage.mjs <TARGET_DIR>
```

脚本失败时回到三级查找修正名称，直到通过。禁止隐藏、裁切或替换字体掩盖缺失图标。

## 日志

逐项记录：

| 语义 | 最终 name | 命中层级 | 来源/关键词 | 校验状态 |
| --- | --- | --- | --- | --- |

同时统计预设表、紧凑索引、搜索脚本和未找到数量。未找到项不得进入 page-build。
