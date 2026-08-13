# HMSymbolIcon

## Metadata

- 实现目录：`src/components/HMSymbolIcon/`
- Stories 路径：`src/components/HMSymbolIcon/HMSymbolIcon.stories.tsx`
- 字体资产：`src/assets/hmsymbol/HMSymbolVF.ttf`
- 官方映射：`src/assets/hmsymbol/hmsymbol-map.json`
- 生成映射：`src/components/HMSymbolIcon/hmsymbol-icon.generated.ts`

## 用途

`HMSymbolIcon` 是 Harmony 系统图标的唯一运行时入口。移动端页面、Render 产物、组件内的系统图标、底部导航、chevron、播放/保存/分享/编辑等图标，应优先使用 `HMSymbolIcon`，而不是直接写 Unicode 私有码位、临时 SVG、emoji 或 lucide 图标。

## Agent 生成规则

- 必须写成 `<HMSymbolIcon name="semantic_name" size={24} />`。
- `name` 必须通过三级查找确认：① 预设表 `hmsymbol-icons-common.md`（151 高频图标）→ ② 紧凑索引 `hmsymbol-index.md`（404 全量图标）→ ③ 搜索脚本 `node skills/01-resource-injection/shadcn/scripts/search-hmsymbol.mjs <关键词>`（支持别名 / 中英文 / 分类查询）。例如 `save`、`share`、`pencil_line_1`、`location_north_up_right_circle_fill`。
- **页面风格统一**：生成一个页面或 render 前，必须先确定 `面性（filled）` 或 `线性（outline）` 作为主图标风格；该页面中导航、工具栏、列表、宫格、操作、反馈和底部 Tab 等可见 `HMSymbolIcon` 均须统一遵循这一选择，禁止因相同语义同时存在两种变体而混用。仅当 Pixso 设计稿、稳定本地组件 API 或必需系统/状态符号明确限定样式时可例外，并须在生成日志中说明原因。
- **彩色底板前景色**：图标的 `color` 必须由承载底板决定，而不是沿用页面默认深色。浅色 / 低饱和 tint 底板可用 `--harmony-icon-primary`、`--harmony-icon-secondary` 或分类深色；饱和、不透明彩色底板及渐变底板必须用 `var(--harmony-icon-on-primary)`。禁止在蓝、绿、橙、红、紫等彩色实底板上放置黑色、深灰或深色分类图标。若 `--harmony-icon-on-primary` 不满足至少 3:1 的对比度，调整或加深底板，不能改用深色图标。
- 禁止直接把完整 `hmsymbol-map.json` 读入模型上下文（6000+ 行）。必须通过上述三级查找按需获取图标名称。
- 禁止在 JSX 文本节点中直接写 `\u{F003B}`、`󰀻` 等私有区字符。
- 禁止把 `"\\u{F003B}"` 当普通字符串传给非 HMSymbol 组件；这会在 Storybook 里显示成字符文本。
- 只有在官方映射缺失且组件规格已登记 legacy alias 时，才使用 legacy alias，例如 `segmented_button_highlight`。
- 当 HM Symbol 没有合适语义图标时，优先使用本地已注册图片 / SVG 资产；最后才使用 lucide-react，并在生成日志说明 fallback 原因。

### 页面/render 图标风格自检

交付前盘点页面全部可见图标，确认：

1. 已声明主图标风格为面性或线性；
2. 所有 `HMSymbolIcon` 与已登记的 fallback 图标均符合该风格；
3. 每个彩色实底板 / 渐变底板上的图标均使用 `--harmony-icon-on-primary` 或等效浅色 token；浅色 tint 底板才允许深色图标；
4. 每个例外均有可追溯的设计稿、组件 API 或系统状态约束说明。

## 按需检索协议（三级查找）

`hmsymbol-map.json` 是源数据（6000+ 行），不是提示词材料。查找图标名称必须严格按以下顺序：

**① 预设表**（最高优先，覆盖 90% 高频场景）：

读取 `src/assets/hmsymbol/hmsymbol-icons-common.md`，按页面类型 / UI 场景分组的表格。从中匹配目标图标名称。

**② 紧凑索引**（① 未命中时使用）：

读取 `src/assets/hmsymbol/hmsymbol-index.md`，404 个全量图标按 15 个分类组织，每行格式 `name: 中文名`。

**③ 搜索脚本**（①② 均未命中时使用）：

```bash
node skills/01-resource-injection/shadcn/scripts/search-hmsymbol.mjs wifi 蓝牙 安全
node skills/01-resource-injection/shadcn/scripts/search-hmsymbol.mjs --category 箭头
node skills/01-resource-injection/shadcn/scripts/search-hmsymbol.mjs --list
```

搜索脚本从 `hmsymbol-map.json` 和 `hmsymbol-aliases.json` 中查找，支持中英文关键词、别名和分类模糊匹配。

**禁止行为**：

- ❌ 未查①②就直接读取 `hmsymbol-map.json` → 严重违规（6000+ 行上下文爆炸）
- ❌ 凭记忆猜测图标名称 → 可能编造不存在的 `name`

**查后验证**（仅用于编程确认名称是否存在，不是查找手段）：

```bash
node -e 'const fs=require("fs");const data=JSON.parse(fs.readFileSync("src/assets/hmsymbol/hmsymbol-map.json","utf8"));const names=new Set(data.icons.map(i=>i.name));for(const name of process.argv.slice(1))console.log(`${name}: ${names.has(name)?"OK":"MISSING"}`)' save share
```

生成日志中记录使用过的 HM Symbol 名称及其查找层级（①②③）；不得记录未经查找确认的臆造名称。

## Props

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | `HMSymbolIconName \| string` | — | 图标语义名；兼容历史字符串但生成代码应使用语义名 |
| `size` | `number \| string` | `24` | 同步设置 font-size / width / height |
| `decorative` | `boolean` | `true` | 装饰性图标默认 `aria-hidden` |
| `title` | `string` | — | 非装饰性图标的可访问名称 |

## 映射来源

`hmsymbol-icon.generated.ts` 由 `hmsymbol-map.json` 的 404 个官方图标机械生成，提供完整语义名到 Unicode 的映射。`hmsymbol-icon.constants.ts` 在官方映射外只保留少量历史 alias：

| Alias | Unicode | 原因 |
|-------|---------|------|
| `square_dashed` | `F0134` | 兼容早期组件 API；官方映射名为 `circle_dashed` |
| `tv` | `F0021` | 兼容早期组件规格中的 Pixso `.TV` 命名 |
| `stopwatch` | `F05F0` | 兼容早期组件 API；官方映射名为 `stopwatch_2` |
| `segmented_button_highlight` | `F012F` | SegmentedButton 设计稿使用但官方 `name_map_new.json` 未收录 |

## Storybook 渲染注意

Storybook 已在 `.storybook/preview.ts` 全局引入 `src/components/HMSymbolIcon/hmsymbol-icon.css`。如果图标显示为 `\u{...}` 文本，通常不是字体未加载，而是代码没有通过 `HMSymbolIcon` 或传入了普通转义字符串。

正确：

```tsx
<HMSymbolIcon name="save" size={24} />
```

错误：

```tsx
<span>{"\\u{F003B}"}</span>
<span className="hm-symbol-icon">{"\\u{F003B}"}</span>
```

兼容但不推荐：

```tsx
<HMSymbolIcon name={"\\u{F003B}"} size={24} />
```

## 取舍说明

1. 保留 `name: HMSymbolIconName | string` 是为了兼容历史页面和 Pixso 原始字符输入；新代码必须使用语义名。
2. 组件会把形如 `"\\u{F003B}"` 的历史字符串解析成真实码位，避免 Storybook 直接显示反斜杠文本。
3. 若传入不在映射内的普通字符串，组件会原样渲染；这只用于向后兼容，不是生成规范。
