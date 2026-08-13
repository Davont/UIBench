# ranking-ChipsTab-Phone (RankingChipsTabPhone)

## Metadata

| 属性 | 值 |
|------|------|
| Block ID | `ranking-chipstab-phone` |
| 实现目录 | `src/blocks/ranking-chipstab-phone/` |
| Stories 路径 | `src/blocks/ranking-chipstab-phone/ranking-chipstab-phone.stories.tsx` |
| 块区 JSON | `src/blocks/ranking-chipstab-phone/ranking-chipstab-phone.json` |
| Storybook Title | `Blocks/ranking-ChipsTab-Phone` |
| Pixso 链接 | `https://pixso.cn/app/design/poNuihoilaLFIwHQwxIlcQ?item-id=59:169` |
| item-id | `59:169` |
| MCP 工具来源 | `get_node_dsl` + `design_to_code` + `get_screenshot` (三证据) |

## MCP 执行记录

| 工具 | 状态 | 结果 |
|------|------|------|
| `get_node_dsl` | ✅ SUCCESS | FRAME "容器 29954" (59:169): 360×64px, transparent bg; INSTANCE "类型=tab" (59:125): 360×56px, mainComponent=2:66757 |
| `design_to_code` | ✅ SUCCESS | ChipsTabPhone React 组件 + 4 个 Item 子组件, 4 tabs: 综合榜/电视剧榜/电影榜/综艺榜 |
| `get_screenshot` | ✅ SUCCESS | PNG 预览截取 |
| `get_variants` | ⚠️ Empty | 返回 `{}`, 该节点无可通过 variants API 暴露的变体属性 |

## 组件变体树 JSON

- **文件路径**: `src/blocks/ranking-chipstab-phone/ranking-chipstab-phone.json`
- **MCP 调用**: `get_node_dsl` (guid: `59:169`) + `design_to_code` (guids: `["59:169"]`)
- **get_variants**: 返回空 `{}` — `variantOptions` 从 `design_to_code` slot 结构重建

## 组成与用途

**导出项**: `RankingChipsTabPhone` (主组件)、`DEFAULT_RANKING_CHIPS_TABS` (Pixso 默认页签)、`RankingChipsTabPhoneProps` (Props 类型)

**使用场景**: 榜单页面的 ChipsTab 标签栏切换。4 个纯文字页签 (综合榜/电视剧榜/电影榜/综艺榜)，360×64px，类型=tab，无图标无数字。

```
ranking-ChipsTab-Phone (Pixso 59:169: 360×64px, transparent)
└── ChipsTabPhone (类型=tab, 栏通透度=标准)
    ├── 综合榜 (activated, 74px) — Pixso 2:66760
    ├── 电视剧榜 (enable, 88px)  — Pixso 2:66761
    ├── 电影榜 (enable, 74px)    — Pixso 2:66762
    └── 综艺榜 (enable, 74px)    — Pixso 2:66763
```

## 量化规格

### 整体尺寸 (Pixso 已验证)

| 参数 | 值 | 来源 |
|------|------|------|
| 容器尺寸 | 360×64px | Pixso `get_node_dsl`: frame-59_169 |
| 背景 | transparent | Pixso DSL: 无 fillPaints |

### Tab (Pixso 已验证)

| 参数 | 值 | 来源 |
|------|------|------|
| Tab 实例尺寸 | 360×56px (在 64px 容器内居中) | Pixso `get_node_dsl`: instance 59:125 |
| Tab 类型 | `"tab"` (纯文字) | Pixso DSL: `name="类型=tab"` |
| 栏通透度 | `"标准"` | 对应 Pixso 材质样式 |
| Item 高度 | 36px | Pixso `design_to_code` |
| Item 宽度 | 74-88px (随文字长度) | Pixso `design_to_code`: 综合榜 74px, 电视剧榜 88px |
| 字体 | HarmonyHeiTi Medium | Pixso: `fontbody_mmedium` |
| 字号 | 14px | Pixso: `fontbody_mmedium` |
| 字重 | 500 (Medium) | Pixso DSL |
| 行高 | 19px | 14px 文本高度 |
| 图标 | 无 (`visible_9_4=false`) | Pixso `design_to_code` |
| 数字 | 无 (`visible_9_1=false`) | Pixso `design_to_code` |

### Tab 状态样式 (Pixso 已验证)

| 状态 | 背景 | 文字颜色 | Pixso 来源 |
|------|------|----------|-----------|
| activated | `fill-lightcomp_background_emphasize` | `fill-lightfont_on_primary` | 2:66740 |
| enable | `fill-lightcomp_background_tertiary` | `fill-lightfont_primary` | 2:66735 |

## 状态与交互

| 状态 | 触发条件 | 视觉效果 |
|------|----------|----------|
| Default | 初始渲染 | 综合榜 activated, 其余 enable |
| Tab switch | 点击页签 | 被点击页签变 activated (emphasize bg + on_primary text), 其余变 enable |
| Focus | 键盘聚焦 | focus-visible 环 (ChipsTab 内置) |

## Props

### RankingChipsTabPhoneProps

| Prop | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| chipsTabItems | `ChipsTabPhoneItem[]` | `DEFAULT_RANKING_CHIPS_TABS` | 页签数据, 默认来自 Pixso 59:169 |
| chipsTabActiveKey | `string \| undefined` | — | 当前激活页签 key (受控) |
| chipsTabDefaultActiveKey | `string \| undefined` | `"all"` | 默认激活页签 key (非受控) |
| onChipsTabChange | `(key, item) => void` | — | 页签切换回调 |
| className | `string` | — | 自定义类名 |

### DSL ↔ Prop 对照

| DSL 字段 | Prop | 取值 |
|----------|------|------|
| `59:125` INSTANCE name="类型=tab" | `chipsTabItems` | `[{key:"all",label:"综合榜",...}]` |
| slot `2:66760` state="activated" | `chipsTabDefaultActiveKey` | `"all"` |
| `visible_9_1=false` | `itemNum={false}` | `false` |
| `visible_9_4=false` | `itemIcon={false}` | `false` |
| component `2:66757` type="tab" | `类型="tab"` | `"tab"` |

## 样式引用

### 使用的 global.css 变量

| CSS 变量 | 用途 |
| --- | --- |
| `--harmony-font-on-primary` | activated 文字 |
| `--harmony-font-primary` | enable 文字 |

### 局部 Token

| Token | 值 | 用途 |
|-------|------|------|
| `--rct-width` | 360px | 容器宽度 |
| `--rct-height` | 64px | Pixso frame-59_169 高度 |
| `--rct-bg` | transparent | Pixso 无填充 |

## 取舍说明

- **get_variants 返回空**: `variantOptions` 从 `design_to_code` slot 结构提取
- **组件本质是 ChipsTabPhone 标签栏**: Pixso 节点 59:169 为纯标签栏 (360×64px)，含 4 个 tab
- **复用 ChipsTabPhone**: 使用项目已有的 `ChipsTabPhone` 组件，Props 与 Pixso DSL 精确对齐
