# ChipsTab

## Metadata

- **实现目录**: `src/components/ChipsTab/`
- **Stories 路径**: `src/components/ChipsTab/chips-tab.stories.tsx`
- **Pixso 链接**: `https://pixso.cn/app/design/QeDttX-H4qVEUZXJjNfTCw?item-id=5336:20452`
- **Item ID**: `5336:20452`（画板 `容器 9` 747×616，含 ChipsTab-Phone 与 `.item` 页签项矩阵）
- **MCP 工具来源**: `get_node_dsl(itemId=5336:20452)`；`get_variants` 返回 `{}`；`get_screenshot` 用户跳过

## 组件变体树 JSON

- **路径**: `src/components/ChipsTab/chips-tab.json`
- **生成依据**: `get_node_dsl(itemId=5336:20452)` 的 `pixComponentTreeDslNodes`
- **降级说明**: `get_variants` 返回 `{}`；页签项（`状态`×`通透度`）与页签栏（`类型`×`栏通透度`）从组件命名解析

## 组成与用途

- **ChipsTab**: 页签组入口，使用 `items: { key, label, icon }[]` 批量传入页签数据，内部页签项为 `role="tab"`，`aria-selected` 随 `activeKey` 联动
- **ChipsTabPhone**: 手机页签栏容器（Pixso `ChipsTab-Phone` 360×56），`role="tablist"`，支持横向滚动、右侧更多按钮、图标行渐隐蒙版
- 导出常量: `chipsTabStates`、`chipsTabMaterials`、`chipsTabBarTypes`、`chipsTabBarMaterials`

## 量化规格

### 页签项 ChipsTab
| 属性 | 值 |
|------|-----|
| Width | enable **110px** / activated **111px**（DSL 固定外框；非纯内容 hug） |
| Height | 36px |
| Padding | 8px 16px |
| Border radius | 20px |
| Icon | 16×16px |
| Gap (icon ↔ text) | 6px |
| Gap (title ↔ num) | 2px |
| Title 字号/行高/字重 | 14px / 21px；activated=Medium(500)，enable=Regular(400) |
| Num 字号/行高 | 12px / 16px |

### 页签栏 ChipsTabPhone
| 属性 | 值 |
|------|-----|
| 尺寸 | 360×56px |
| 轨道高度 | 36px |
| Chip 间距 | 8px |
| 更多按钮 | 36×36px，图标 24×24px |
| 渐隐蒙版 | 视口 max-width 300px，右侧 60px 线性透明（`类型=tab with icon`，DSL 蒙版 300×56） |

### 字体与色值（`通透度=默认`）
| 状态 | Title | Num | Background |
|------|-------|-----|------------|
| activated | `#fff` / 500 | `rgba(255,255,255,0.4)` | `--harmony-brand` |
| enable | `rgba(0,0,0,0.6)` / 400 | `rgba(0,0,0,0.4)` | `--harmony-comp-background-tertiary` |

### 材质-弱
- `box-shadow: 0 8px 48px rgba(0,0,0,0.08)`
- `backdrop-filter: blur(80px)`

## 状态与交互

| 维度 | 取值 | 层级 |
|------|------|------|
| `状态` | `activated` / `enable` | 页签项 |
| `通透度` | `默认` / `材质-标准` / `材质-弱` / `材质-强` / `材质-降档` | 页签项 |
| `num` / `icon` | `true` / `false`（DSL `visible_*`） | 页签项 |
| `类型` | `tab` / `tab with icon` / `icontab` | 页签栏 |
| `栏通透度` | `强` / `弱` / `标准` / `降档` | 页签栏 |

## Props

### ChipsTab（页签组）

| DSL 字段 | Prop | 类型 | 默认 | 可取值 |
|---------|------|------|------|--------|
| 数据源 | `items` | `ChipsTabItem[]` | — | `[{ key, label, icon, numValue, disabled }]` |
| 选中项 | `activeKey` / `defaultActiveKey` | string | 首项 `key` | `items[n].key` |
| 选中回调 | `onActiveKeyChange` | `(key, item) => void` | — | — |
| 变体 `通透度` | `通透度` | string | `默认` | 见上表 |
| 栏级 `类型`（页级/c2d 复用） | `类型` | string | `tab with icon` | `tab` / `tab with icon` / `icontab`；`tab` 默认无图标，`icontab` 仅图标 |
| `visible_*` → `num` | `num` | boolean | `false` | `true` / `false` |
| `visible_*` → `icon` | `icon` | boolean | 按 `类型` 推导 | `true` / `false` |

```tsx
const items = [
  { key: "home", label: "首页", icon: <HMSymbolIcon name="house_fill" size={24} /> },
  { key: "explore", label: "探索", icon: <HMSymbolIcon name="discover_fill" size={24} /> },
  { key: "profile", label: "我的", icon: <HMSymbolIcon name="person_crop_circle_fill_1" size={24} /> },
]
```

### ChipsTabPhone（页签栏）

| DSL 变体维度 | Prop | 默认 | 可取值 |
|-------------|------|------|--------|
| `类型` | `类型` | `tab with icon` | `tab` / `tab with icon` / `icontab` |
| `通透度`（栏级） | `栏通透度` | `标准` | `强` / `弱` / `标准` / `降档` |
| — | `items` | 5 个预览项 | `ChipsTabPhoneItem[]`，字段为 `{ key, label, icon, numValue, disabled }` |
| — | `showMore` | `false` | boolean |

## 样式引用

- `--harmony-brand`、`--harmony-font-on-primary`、`--harmony-font-on-tertiary`
- `--harmony-comp-background-tertiary`、`--harmony-font-secondary`、`--harmony-font-tertiary`
- `--harmony-icon-on-primary`、`--harmony-icon-secondary`、`--harmony-icon-primary`

## 取舍说明

1. 页签项使用 `<div role="tab">`（非 `<button>`、非 `HmButton`）；选中项 `tabIndex={0}`，其余 `-1`；父级需 `role="tablist"`。右侧「更多」仍为 `3.Icon Button` 实例，保留 `<button>`。
2. 栏级 `类型=icontab` 时隐藏文案、仅保留图标槽（与 DSL 画板结构一致）。
3. `栏通透度` 与项级 `通透度` 在 DSL 中为不同变体轴；栏级材质差异主要为容器蒙版/背景，当前以 `data-bar-material` 预留，视觉与 `标准` 一致处待更细 DSL 段补充。
4. 默认图标使用 Pixso `.TV`（HM Symbol U+F0021）与 `.more`（`dot_grid_2x2` U+F0061），经 `HMSymbolIcon` 渲染。
5. `get_screenshot` 未执行；量化参数来自 `get_node_dsl`。
