# List — 统一列表 Block

## 概述

统一列表 block，替代原有的四个分散列表组件：`GroupedListSection`、`SettingsMultiRowList`、`SettingsSwitchList`、`DropdownList`。

## 三种视觉变体

| 变体 | `variant` 值 | 圆角 | 宽度 | 用途 |
|------|-------------|------|------|------|
| Card | `"card"` | 16px | 328px | 设置卡片列表（原 SettingsMultiRowList / SettingsSwitchList） |
| Dropdown | `"dropdown"` | 12px | auto | 下拉/导航列表（原 DropdownList） |
| Grouped | `"grouped"` | body 20px | 100% | 分组 section（原 GroupedListSection） |

## Props — `ListProps`

| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `variant` | `"card" \| "dropdown" \| "grouped"` | ❌ | `"card"` | 视觉变体 |
| `items` | `ListItem[]` | ❌ | — | 列表项（与 `children` 互斥） |
| `children` | `ReactNode` | ❌ | — | 直接传入 ListPhone 子元素 |
| `subtitle` | `ReactNode` | ❌ | — | grouped 变体的 section 标题 |
| `footnote` | `ReactNode` | ❌ | — | grouped 变体的脚注文本 |
| `theme` | `"light" \| "dark"` | ❌ | `"light"` | 主题 |
| `bodyClassName` | `string` | ❌ | — | body/card 容器额外 className；card、dropdown、grouped 均生效 |
| `className` | `string` | ❌ | — | 容器额外 className |

## Item Props — `ListItem`

| Prop | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `key` | `string` | ❌ | index | 唯一 key |
| `icon` | `ReactNode` | ❌ | — | 旧版 24px 左侧自定义图标简写；优先使用 `left` / `leftIconName` |
| `left` | `ListPhoneLeftType` | ❌ | 见下 | 透传到 `ListPhone.left`；显式控制 Dot、24dp_ic、40dp_ic、badge、Switch 等左侧 addon |
| `leftIconName` | `HMSymbolIconName` | ❌ | — | 透传到 `ListPhone.leftIconName`；未声明 `left` 时自动使用 `left="24dp_ic"` |
| `leftIconSize` | `number` | ❌ | `min(leftSize, 24)` | 透传到 `ListPhone.leftIconSize`，修正内置 HM Symbol glyph 尺寸 |
| `leftIconColor` | `string` | ❌ | `--harmony-icon-primary` | 透传到 `ListPhone.leftIconColor`，建议使用 Harmony token |
| `leftIconBackground` | `string` | ❌ | 按左侧类型 | 透传到 `ListPhone.leftIconBackground`，建议使用 Harmony token |
| `leftIconRadius` | `number \| string` | ❌ | 按左侧类型 | 透传到 `ListPhone.leftIconRadius` |
| `leftSlot` | `ReactNode` | ❌ | — | 透传到 `ListPhone.leftSlot`，完全替换左侧 addon；优先级高于 `icon` |
| `leftText` | `ReactNode` | ❌ | `"A"` | 透传到 `ListPhone.leftText`，用于 8/16dp mini mark |
| `leftBadgeText` | `ReactNode` | ❌ | `"1"` | 透传到 `ListPhone.leftBadgeText` |
| `leftSelected` | `ToggleSelected \| boolean` | ❌ | — | 透传到 `ListPhone.leftSelected`，用于左侧 Switch |
| `defaultLeftSelected` | `ToggleSelected \| boolean` | ❌ | `"ON"` | 透传到 `ListPhone.defaultLeftSelected` |
| `onLeftSelectedChange` | `(s: ToggleSelected) => void` | ❌ | — | 透传到 `ListPhone.onLeftSelectedChange` |
| `lines` | `"1" \| "2" \| "3"` | ❌ | 按内容推导 | 行数；有 `description` 默认为 3 行，有 `subtitle` 默认为 2 行，仅 `title` 默认为 1 行 |
| `title` | `ReactNode` | ✅ | — | 标题 |
| `subtitle` | `ReactNode` | ❌ | — | 副标题（lines ≥ 2） |
| `description` | `ReactNode` | ❌ | — | 第三行文本（lines = 3） |
| `type` | `ListItemType` | ❌ | 见下 | 右侧控件类型 |
| `value` | `ReactNode` | ❌ | — | 右侧显示值 |
| `defaultSelected` | `ToggleSelected` | ❌ | `"OFF"` | 非受控初始状态 |
| `selected` | `ToggleSelected` | ❌ | — | 受控状态 |
| `onSelectedChange` | `(s: ToggleSelected) => void` | ❌ | — | 状态变化回调 |
| `disabled` | `boolean` | ❌ | `false` | 禁用 |
| `divider` | `boolean` | ❌ | 最后一项 `false` | 是否显示分割线 |
| `dividerMode` | `"padding" \| "content" \| "full" \| "custom"` | ❌ | 有 `icon` 时 `"custom"`，否则 `"padding"` | 透传到 `ListPhone` 的分割线几何协议 |
| `dividerInsetStart` | `number \| string` | ❌ | 有 `icon` 时 `calc(var(--list-horizontal-padding) + 24px + 12px)` | 自定义分割线起点 |
| `dividerInsetEnd` | `number \| string` | ❌ | — | 自定义分割线终点 |
| `onClick` | `() => void` | ❌ | — | 行点击回调 |
| `className` | `string` | ❌ | — | 行额外 className |

> `type` 默认值：card 变体为 `"switch"`，dropdown 变体为 `"dropdown"`

## 自动行数推导

`items` API 不再默认两行，而是根据内容存在性推导：

```tsx
const inferredLines =
  item.lines ??
  (hasRenderableContent(item.description)
    ? "3"
    : hasRenderableContent(item.subtitle)
      ? "2"
      : "1")
```

这可以避免只有 `title` 的行出现 64px 空二行。需要固定两行高度时必须显式传 `lines: "2"`。

## Divider 规则

- 常规行使用 `ListPhone` 原生 divider，不在页面或 block 外层自绘。
- `items` 使用 `left`、`leftIconName`、`leftSlot` 或旧版 `icon` 时，左侧 addon 由 `ListPhone` 渲染，默认 `dividerMode="content"` 会从正文 main 区域起笔，天然避让左侧区域。
- 特殊封面、头像、索引器场景使用 `dividerMode="custom"` 和 `dividerInsetStart` / `dividerInsetEnd` 显式声明。
- 页面模板禁止通过 `.list-phone__divider` 深选择器覆盖常规 divider。

## 左侧 Slot 透传规则

- 推荐优先使用 `left` + `leftIconName` 声明内置 HM Symbol 图标。
- 只传 `leftIconName` 时，`List` 自动给内部 `ListPhone` 使用 `left="24dp_ic"`。
- 需要修正 glyph 尺寸、颜色、背景或圆角时，使用 `leftIconSize`、`leftIconColor`、`leftIconBackground`、`leftIconRadius`，并优先传 Harmony token。
- `leftSlot` 是完全自定义逃生口，优先级高于旧版 `icon`。
- `icon` 保留兼容旧调用，会被包装为 24px `.list__item-icon` 后透传到 `ListPhone.leftSlot`。

## `ListItemType` → `ListPhone` 映射

| `type` | ListPhone `right` | 效果 |
|--------|-------------------|------|
| `"switch"` | `"Switch"` | Toggle 开关 |
| `"navigate"` | `"Arrow"` | Chevron-right 箭头（可选 value 文本） |
| `"dropdown"` | `"Menu select"` | 文本 + chevron-down |
| `"text"` | `"Text"` | 纯文本值 |
| `"expand"` | `"Expand"` | 双行文本 + chevron-right |
| `"radio"` | `"Radio"` | 单选按钮 |
| `"checkbox"` | `"Checkbox"` | 复选框 |
| `"none"` | `"None"` | 无右侧控件 |

## 使用示例

### Card 变体

```tsx
import { List } from "@/blocks/list"

<List
  variant="card"
  items={[
    { title: "位置数据", subtitle: "开启后可获得基于地理位置的推荐", type: "switch", defaultSelected: "ON" },
    { title: "我的偏好", lines: "1", type: "navigate" },
  ]}
/>
```

### Dropdown 变体

```tsx
<List
  variant="dropdown"
  items={[
    { title: "自动更新应用", lines: "1", value: "仅 WLAN", type: "dropdown" },
    { title: "关于手机", lines: "1", type: "navigate" },
  ]}
/>
```

### Grouped 变体

```tsx
<List
  variant="grouped"
  subtitle="亮度调节"
  footnote="自动亮度会综合当前环境光、使用场景和电量状态做平衡。"
  items={[
    { title: "自动亮度", subtitle: "根据环境光自动调整", type: "switch" },
    { title: "日落后自动开启", type: "text", value: "20:00" },
  ]}
/>
```

### Children 插槽

```tsx
import { ListPhone } from "@/components/Container/ListPhone"

<List variant="grouped" subtitle="数据和隐私">
  <ListPhone 行数="2" title="个性化推荐" subtitle="..." right="Switch" divider />
  <ListPhone title="隐私协议" right="Arrow" divider={false} />
</List>
```

## 迁移指南

| 旧组件 | 新用法 |
|--------|--------|
| `<SettingsMultiRowList>` | `<List variant="card">` |
| `<SettingsSwitchList>` | `<List variant="card" items={items.map(i => ({ ...i, type: "switch", lines: "2" }))}>` |
| `<DropdownList>` | `<List variant="dropdown">` |
| `<GroupedListSection>` | `<List variant="grouped">` |

旧导入路径（`@/blocks/grouped-list-section` 等）仍可使用，但建议新代码直接使用 `@/blocks/list`。

## Token 引用

| 样式 | Token |
|------|-------|
| Card/下拉 背景 | `--harmony-background-primary` |
| Card/下拉 暗色背景 | `--harmony-comp-background-primary` |
| Grouped body 背景 | `--harmony-comp-background-primary` |
| Header 文本 | `--harmony-font-secondary` |
| Footnote 文本 | `--harmony-font-secondary` |
| 悬浮态背景 | `--harmony-interactive-hover` |
| 按压态背景 | `--harmony-interactive-pressed` |
