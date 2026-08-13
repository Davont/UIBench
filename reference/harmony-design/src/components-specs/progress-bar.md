# ProgressBar 组件规格

## Metadata

| 字段 | 值 |
|------|------|
| 实现目录 | `src/components/ProgressBar/` |
| Stories 路径 | `src/components/ProgressBar/progress-bar.stories.tsx` |
| Pixso 链接 | [ProgressBar](https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5410:23706) |
| item-id | `5410:23706` |
| MCP 工具来源 | `get_node_dsl`, `get_screenshot` |

## 组件变体树 JSON

**文件路径：** `src/components/ProgressBar/progress-bar.json`

**生成方式：** 基于 `get_node_dsl` + `get_screenshot` 分析

**变体维度：**
- 缓存：`OFF` | `ON`

## 组成与用途

**导出项：**
- `ProgressBar` - 主组件
- `progressBarCacheOptions` - 缓存选项枚举常量
- `ProgressBarProps` - Props 类型
- `ProgressBarCacheOption` - 缓存选项联合类型

**使用场景：**
- 媒体播放进度显示（视频/音频）
- 带缓冲缓存的下载进度
- 通用线性进度展示

## 量化规格

### 尺寸
| 元素 | 值 |
|------|------|
| 轨道宽度 | 288px |
| 轨道高度 | 4px |
| 圆角 | 2px |
| 容器高度 | 24px（含点击区域） |

### 色值
| 元素 | 色值 | 变量引用 |
|------|------|----------|
| 轨道背景 | rgba(0,0,0,0.098) | `--harmony-comp-background-secondary` |
| 进度填充 | rgba(10,89,247,1) | `--harmony-comp-background-emphasize` |
| 缓存层 | rgba(10,89,247,0.2) | brand 20% 透明度（无现有 token 对应） |

## 状态与交互

| 状态 | 表现 |
|------|------|
| 缓存 OFF | 仅显示轨道 + 进度填充 |
| 缓存 ON | 显示轨道 + 缓存层 + 进度填充（三层叠加） |

**层级关系（从底到顶）：** 轨道背景 → 缓存层 → 进度填充

## Props

```typescript
interface ProgressBarProps extends HTMLAttributes<HTMLDivElement> {
  进度?: number       // 默认：43，进度百分比 0-100
  Cache?: boolean      // 默认：false，是否显示缓存层
  Cache进度?: number   // 默认：58，缓存百分比 0-100
}
```

### DSL ↔ Prop 对照

| DSL 属性 | Prop 名 | 取值集合 | 说明 |
|----------|---------|----------|------|
| Cache | Cache | false, true | 与 DSL 变体名 Cache=ON/OFF 对应 |
| Progress (Rectangle width ratio) | 进度 | 0-100 | 进度填充宽度百分比 |
| Cache (Rectangle width ratio) | Cache进度 | 0-100 | 缓存层宽度百分比 |

## 样式引用

### 使用的 global.css 变量
| 变量名 | 用途 | 来源 |
|--------|------|------|
| `--harmony-comp-background-secondary` | 轨道背景 | 现有 token |
| `--harmony-comp-background-emphasize` | 进度填充 | 现有 token |

### 新增 Token
无新增全局 Token。缓存层色值 `rgba(10,89,247,0.2)` 直接在组件 CSS 中使用，为 brand 色 20% 透明度，语义上与 `--harmony-comp-emphasize-secondary` 一致。

## 取舍说明

| 项目 | 说明 |
|------|------|
| 布局方案 | 容器 24px 高度（含交互区域），轨道居中 4px，使用 `flex + align-items: center` |
| 缓存层实现 | 使用绝对定位 + `overflow: hidden` 实现三层叠加，与 DSL 层级一致 |
| 宽度控制 | 使用 CSS 自定义属性 `--progress-bar-progress` 和 `--progress-bar-cache` 动态控制 |
| 圆角 | 轨道与填充层均使用 2px 圆角，与 DSL `cornerRadius: 2` 一致 |
| 缓存色值 | DSL 中缓存层为 `rgba(10,89,247,0.2)`，与现有 token `--harmony-comp-emphasize-secondary` 值一致，但为确保精确还原，直接在 CSS 中使用具体值 |

## 1:1 还原验证

**验证方式：** 人工对照截图 + 关键尺寸复算

**对照结论：**
- ✅ 轨道高度 4px、圆角 2px 与 DSL 一致
- ✅ 轨道背景色 `rgba(0,0,0,0.098)` 与 DSL `inheritFillStyleID: 602:9419` 一致
- ✅ 进度填充色 `rgba(10,89,247,1)` 与 DSL `inheritFillStyleID: 602:9414` 一致
- ✅ 缓存层色值 `rgba(10,89,247,0.2)` 与 DSL 一致
- ✅ 三层叠加顺序（track → cache → fill）与 DSL childNode 顺序一致
- ✅ 变体 Cache=ON/OFF 二态与 DSL 一致

**未执行自动 SSIM**，对照方式为人工复核 + DSL 数据交叉验证。
