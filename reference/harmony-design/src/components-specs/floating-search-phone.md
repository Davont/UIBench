# FloatingSearchPhone 组件规格

## Metadata

| 字段 | 值 |
|------|-----|
| 实现目录 | `src/components/FloatingSearchPhone` |
| Stories 路径 | `src/components/FloatingSearchPhone/FloatingSearchPhone.stories.tsx` |
| Pixso 链接 | `https://pixso.cn/app/design/QeDttX-H4qVEUZXJjNfTCw?item-id=4528:12514` |
| MCP 工具 | `get_node_dsl`（`get_screenshot` 和 `get_variants` 被用户拒绝） |
| 变体树 JSON | `src/components/FloatingSearchPhone/floating-search-phone.json` |
| 变体树来源 | 从 `get_node_dsl` 返回的 `pixTreeNodes` 提取 |

## 组成与用途

浮动搜索栏组件，用于 HarmonyOS 浮动 UI 场景中的搜索功能入口。

- **导出**：`FloatingSearchPhone`（组件）、常量数组、类型
- **使用场景**：浮动地图页面、音乐播放页等需要搜索功能的浮动面板

## 量化规格

| 参数 | 值 |
|------|-----|
| 宽度 | 328px |
| 高度 | 40px |
| 圆角 | 24px |
| 布局 | Horizontal flex, counterAlign=center |
| gap (OFF Normal) | 8px |
| gap (ON Normal) | 8px |
| gap (ON Actived) | 6px |
| padding (OFF) | 9/12/9/12 (top/right/bottom/left) |
| padding (ON) | 4/4/4/12 |
| 字体 | HarmonyHeiTi Regular |
| 字号 | 16px |
| 行高 | 22px |
| 字重 | 400 |
| letterSpacing | 0 |
| 搜索图标 | 18×18, icon-secondary color |
| 搜索操作按钮 | 109×32, 含 voice icon(18×18) + divider(1×12) + "Search" text(14px, font-emphasize) |
| 光标 | 1.5×24, brand color (仅 Typing/Actived 状态可见) |

## 状态与交互

### Search=OFF 状态

| 状态 | 描述 |
|------|------|
| Normal | 基础填充色，placeholder 文字 (font-secondary) |
| Hover | 浮动提升效果：elevated shadow + highlight gradient |
| Press | 交互按压覆盖 (interactive-pressed) |
| Focus | 蓝色边框 (interactive-focus, 1px stroke) |
| Actived | 同 Hover 浮动效果，文字变为 font-primary |
| Typing | 光标可见，文字 font-primary |
| Output | 文字 font-primary |

### Search=ON 额外状态

| 状态 | 描述 |
|------|------|
| icon hover | 搜索图标变为 icon-primary |
| icon focus | 搜索图标变为 interactive-focus (brand) |
| icon press | 搜索图标变为 interactive-active (brand) |

## 通透度层级

| 通透度 | fillStyle 名称 | 填充 | backdrop | shadow | 额外 |
|--------|---------------|------|----------|--------|------|
| 标准 | Light/Blur/FLOATING_THIN | rgba(255,255,255,0.1) LINEAR_DODGE | blur(30px) saturate(80%) | floating-thin-shadow + highlight | — |
| 强 | Light/Blur/Material_background_THIN | rgba(255,255,255,0.4) LINEAR_DODGE | blur(8px) | 0 8px 48px rgba(0,0,0,0.08) | — |
| 降档 | Light/comp_background_color_floating_smooth | rgba(241,243,245,0.95) | none | 0 8px 48px rgba(0,0,0,0.08) | border: rgba(0,0,0,0.1), inner highlight |
| 弱 | Light/Floating_background_weak | rgba(255,255,255,0.7) | blur(20px) saturate(1.08) | floating-thin-shadow + border highlight | — |

## Props

### DSL ↔ Prop 对照表

| DSL 字段 | Prop 名 | 类型 | 默认值 | 取值集合 | 一致性 |
|----------|---------|------|--------|----------|--------|
| Search | Search | `"OFF" \| "ON"` | `"OFF"` | `["OFF", "ON"]` | ✅ 完全一致 |
| 状态 | 状态 | `string` | `"Normal"` | `["Normal", "Hover", "Press", "Focus", "Actived", "Typing", "Output", "icon hover", "icon focus", "icon press"]` | ✅ 完全一致 |
| 通透度 | 通透度 | `string` | `"标准"` | `["标准", "强", "降档", "弱"]` | ✅ 完全一致 |
| — | placeholder | `string` | `"搜索"` | — | 额外 prop（DSL 中为 nodeText） |
| — | searchButtonText | `string` | `"Search"` | — | 额外 prop（DSL 中为 Searchaction 组件文本） |
| — | value | `string` | `undefined` | — | 额外 prop（Typing/Output 输入文本） |
| — | onSearch | `() => void` | `undefined` | — | 额外 prop（搜索按钮回调） |

## 样式引用

### global.css Token

| Token | 用途 |
|-------|------|
| `--FLOATING_THIN_fill` | 标准通透度背景 |
| `--Material_background_THIN_fill` | 强通透度背景 |
| `--comp_background_color_floating_smooth_fill` | 降档通透度背景 |
| `--Floating_background_weak_fill` | 弱通透度背景 |
| `--FLOATING_REGULAR_fill` | Hover/Actived 状态提升背景（标准通透度） |
| `--harmony-floating-thin-shadow` | 标准/弱通透度浮动阴影 |
| `--harmony-floating-thin-highlight` | 标准/弱通透度高光 |
| `--Floating_background_line_fill` | 降档通透度边框 |
| `--harmony-font-secondary` | placeholder 文字色 |
| `--harmony-font-primary` | Typing/Output/Actived 文字色 |
| `--harmony-font-emphasize` | 搜索按钮文字色 |
| `--harmony-icon-secondary` | 搜索图标色 |
| `--harmony-icon-primary` | icon hover 时图标色 |
| `--harmony-interactive-focus` | Focus 边框色、icon focus 色 |
| `--harmony-interactive-active` | icon press 色 |
| `--harmony-interactive-hover` | hover 覆盖层 |
| `--harmony-interactive-pressed` | press 覆盖层 |
| `--harmony-brand` | 光标颜色 |
| `--harmony-comp-divider` | action divider 颜色 |

### 新增全局 Token

无新增。所有 Token 均来自 `global.css` 已有定义。

## 取舍说明

1. **未使用 `get_screenshot`/`get_variants`**：用户拒绝了这两个 MCP 调用。变体树和量化参数完全从 `get_node_dsl` 返回数据中提取。
2. **Hover/Actived 效果**：DSL 中 Hover 和 Actived 共享相同的 elevated shadow + highlight gradient 效果，已在 CSS 中统一实现。
3. **光标位置**：DSL 中 Search=OFF Typing 时 cursor 在文字前方，Search=ON Typing 时 cursor 在文字后方。已通过条件渲染实现。
4. **`value` 和 `onSearch` props**：DSL 中不存在这些字段，但作为功能组件的必要交互 props 添加，不影响视觉还原。
