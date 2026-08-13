# three-column-layout 规格文档

## Metadata

| 项目 | 内容 |
| --- | --- |
| 实现目录 | `src/blocks/three-column-layout/` |
| Stories 路径 | `src/blocks/three-column-layout/three-column-layout.stories.tsx` |
| Pixso 链接 | `https://pixso.cn/app/design/xFQdeTDAPFQG4jOEn2upBQ?item-id=5:13571` |
| item-id | `5:13571` |
| MCP 工具来源 | `get_node_dsl` (guid: `5:13571`) + `get_screenshot` (guid: `5:13571`) |
| 组件变体树 JSON | `src/blocks/three-column-layout/three-column-layout.json`（由 `get_node_dsl` 结构重建） |

## 组成与用途

**导出项：** `ThreeColumnLayout`（forwardRef 组件）

**使用场景：** 内容推荐页的"精选笔记"区块，展示 3 张横排卡片，顶部带标题和来源入口，每张卡片含封面图、标题、作者和点赞信息。适用于地图 POI 详情页、内容推荐 Feed 等场景。

## 量化规格

### 整体区块

| 属性 | 值 | 来源 |
| --- | --- | --- |
| 容器宽度 | 412px（无左右 padding，卡片 left 从 0 起） | DSL `5:13571` width=412 |
| 容器高度 | 240px (56px header + 182px cards + 2px 余量) | DSL `5:13571` height=240 |
| 卡片高度验证 | 132(图)+4+19(标题)+2+14(来源行)+12(底padding) = 183px ≈ 182px | 计算与 DSL 182px 有 1px 差异，以 DSL 182px 为准 |
| 页边距 | 无（由外层页面容器控制，DSL 卡片 left=0/140/280 无偏移） | — |

### Header (poi标题)

| 属性 | 值 | 来源 |
| --- | --- | --- |
| 高度 | 56px | DSL `5:13575` height=56 |
| 内容宽 | 328px | DSL `5:13575` width=328 |
| 左区布局 | flex row, gap 8px | DSL `5:13571` childNode |
| 右区布局 | flex row, gap 4px | DSL `5:13571` childNode |

#### 标题文字

| 属性 | 值 | DSL 映射 |
| --- | --- | --- |
| fontSize | 18px | `localStyleMap["4:4325"]` → Font/Subtitle_L/Medium |
| fontWeight | 500 (Medium) | `localStyleMap["4:4325"]` |
| fontFamily | HarmonyHeiTi | `localStyleMap["4:4325"]` |
| color | `--harmony-font-primary` (rgba(0,0,0,0.9)) | `localStyleMap["2:375853"]` → Light/font_primary |
| lineHeight | 1.33 (24px/18px) | DSL height=24, fontSize=18 |

#### 来源图标

| 属性 | 值 | 来源 |
| --- | --- | --- |
| 尺寸 | 16×16px | DSL `5:16950` width=16, height=16 |

#### "查看全部"文字

| 属性 | 值 | DSL 映射 |
| --- | --- | --- |
| fontSize | 14px | `localStyleMap["4:4136"]` → Font/Body_M/Regular |
| fontWeight | 400 (Regular) | `localStyleMap["4:4136"]` |
| color | `--harmony-font-secondary` (rgba(0,0,0,0.6)) | `localStyleMap["2:376057"]` → Light/font_secondary |
| lineHeight | 1.36 (19px/14px) | DSL height=19, fontSize=14 |

#### 箭头图标

| 属性 | 值 | 来源 |
| --- | --- | --- |
| 尺寸 | 12×24px | DSL `5:16948` width=12, height=24 |

### 卡片行

| 属性 | 值 | 来源 |
| --- | --- | --- |
| 卡片数量 | 3 | DSL 3× 卡片1 instances |
| 卡片宽度 | 132px | DSL `5:13572/3/4` width=132 |
| 卡片高度 | 182px | DSL `5:13572/3/4` height=182 |
| 卡片间距 | 8px | DSL left 差值: 140-132=8, 280-(140+132)=8 |
| 容器 padding | 无 | DSL 卡片 left=0，header width=328px 固定宽度 |

### 单张卡片 (132×182)

| 区域 | 属性 | 值 | 来源 |
| --- | --- | --- | --- |
| 容器 | 圆角 | 12px | DSL `5:16955` cornerRadius=12 |
| 容器 | 背景色 | white | DSL `5:16955` fillPaints SOLID r=255,g=255,b=255,a=1 |
| 封面图 | 尺寸 | 132×132px | DSL `5:16961` width=132, height=132 |
| 封面图 | 圆角 | 12px (四角) | DSL `5:16961` cornerRadius=12, 四角各自 CornerRadius=12 |
| 标题区 | top padding | 4px | DSL 图片 bottom=132, 标题 top=136, 136-132=4 |
| 标题区 | bottom padding | 12px | DSL 头像 bottom=170, 卡片底=182, 182-170=12 |
| 标题 | fontSize | 14px | `localStyleMap["4:3836"]` → Font/Body_M/Medium |
| 标题 | fontWeight | 500 (Medium) | `localStyleMap["4:3836"]` |
| 标题 | color | `--harmony-font-primary` | `localStyleMap["2:375853"]` → Light/font_primary |
| 标题 | lineHeight | 1.36 (19px/14px) | DSL height=19, fontSize=14 |
| 标题 | bottom margin | 2px | 用户反馈：头像到标题间距缩小 3px，原 DSL 推导值 5px → 调整为 2px |
| 来源行 | 高度 | 24px (157+24=181≈182) | DSL 元素 top=157 |
| 来源头像 | 尺寸 | 12×12px | DSL `5:16959` width=12, height=12 |
| 来源头像 | 圆角 | 50% (圆形) | DSL type=ELLIPSE |
| 作者名 | fontSize | 10px | `localStyleMap["4:5091"]` → Font/Caption_M/Regular |
| 作者名 | fontWeight | 400 (Regular) | `localStyleMap["4:5091"]` |
| 作者名 | color | `--harmony-font-secondary` | `localStyleMap["2:376057"]` → Light/font_secondary |
| 作者-点赞间距 | 16px | DSL 作者 right≈90, 点赞 left=106, 106-90=16 |
| 心形图标 | 尺寸 | 10×10px | DSL heart component 内 path ≈9.16×8.14 |
| 心形图标 | 颜色 | rgba(0,0,0,0.6) | `localStyleMap["5:13930"]` → Light/icon_secondary |
| 点赞数 | fontSize | 10px | `localStyleMap["4:5091"]` → Font/Caption_M/Regular |
| 点赞数 | color | `--harmony-font-secondary` | `localStyleMap["2:376057"]` |

### 视频标识

| 属性 | 值 | 来源 |
| --- | --- | --- |
| 尺寸 | 20×20px | DSL `5:16965` width=20, height=20 |
| 位置 | top: 8px, right: 8px | DSL `5:16965` left=104 (132-20-8=104), top=8 |
| 圆角 | 12px | DSL `5:16965` cornerRadius=12 |
| 背景色 | rgba(0,0,0,0.4) | DSL `5:16965` fillPaints SOLID r=0,g=0,b=0,a=0.4 |
| 播放图标 | 10px HM Symbol | DSL `5:16966` fontSize=10, fontFamily="HM Symbol" |
| 播放图标色 | white | DSL `5:16966` fillPaints r=255,g=255,b=255,a=1 |

## 状态与交互

| 状态 | 说明 |
| --- | --- |
| Default | 默认展示，卡片可点击 |
| Hover | 卡片可添加 hover 效果（当前未实现，按需扩展） |
| 视频 | 卡片右上角显示播放标识 |

## Props

### ThreeColumnLayoutProps

| Prop | 类型 | 默认值 | DSL 对齐 |
| --- | --- | --- | --- |
| 标题 | `string` | — | `5:16951` nodeText="精选笔记"，Font/Subtitle_L/Medium |
| 来源名称 | `string` | — | `5:16943` 小红书 / `5:16952` 大众点评 |
| 来源图标 | `string` | — | `5:16950` INSTANCE 16×16 |
| 卡片列表 | `ThreeColumnCardData[]` | `[]` | 3× `5:16954` 卡片实例 |
| on查看全部 | `() => void` | — | `5:16949` "查看全部" 点击 |

### ThreeColumnCardData

| Prop | 类型 | DSL 对齐 |
| --- | --- | --- |
| 图片 | `string` | `5:16961` RECTANGLE IMAGE 132×132 |
| 标题 | `string` | `5:16960` TEXT 14px Medium |
| 来源 | `string` | `5:16963` TEXT 8px (来源平台) |
| 来源头像 | `string` | `5:16959` ELLIPSE IMAGE 12×12 |
| 作者 | `string` | `5:16956` TEXT 10px Regular |
| 点赞数 | `string` | `5:16957` TEXT 10px Regular |
| 是否视频 | `boolean` | `5:16965` RECTANGLE (视频标识) visible |

## 样式引用

### 使用的 global.css Token

| Token | 取值 | 用途 |
| --- | --- | --- |
| `--harmony-page-margin` | 16px | 区块左右 padding |
| `--harmony-font-size-subtitle-l` | 18px | 区块标题字号 |
| `--harmony-font-weight-subtitle-l` | 500 | 区块标题字重 |
| `--harmony-font-primary` | rgba(0,0,0,0.9) | 标题/卡片标题颜色 |
| `--harmony-font-size-body-m` | 14px | "查看全部"/卡片标题字号 |
| `--harmony-font-weight-body-m` | 400 | "查看全部"字重 |
| `--harmony-font-secondary` | rgba(0,0,0,0.6) | "查看全部"/作者/点赞颜色 |
| `--harmony-font-size-caption-m` | 10px | 作者名/点赞数字号 |
| `--harmony-comp-background-primary` | white | 卡片背景 |

### 新增 Token

无新增 Token。所有值均使用已有 global.css 变量。

## 取舍说明

1. **箭头图标**：DSL 中箭头为 `Public/ic_public_arrow_right` (4:4082) 组件实例。实现中使用 Pixso 导出的原始 SVG path（去掉 mask/clipPath 包装），fill 颜色 `rgba(0,0,0,0.2)` 与 DSL 一致。
2. **心形图标**：DSL 中为 `heart` (5:14111) 组件，使用 Pixso 导出的原始 SVG path，fill `rgba(0,0,0,0.6)` (icon_secondary)，fillRule `nonzero`。
3. **视频播放图标**：DSL 中为 HM Symbol 字体字符 `󰂴` (U+F00B4)。实现中用 SVG 三角形 path 等价替代（无需引入 HM Symbol 字体依赖）。
4. **来源头像图片**：DSL 中为 IMAGE 类型的 ELLIPSE 填充。实现中用 `<img>` + `border-radius: 50%` 等价还原。
5. **布局定位**：DSL 中卡片使用绝对定位 (left: 0/140/280)。实现中改用 flex + gap: 8px，视觉效果一致但更灵活。
6. **卡片圆角**：封面图四角圆角 12px (cornerRadius=12, 四角各自 CornerRadius=12)。实现中封面图设 `border-radius: 12px`，容器设 `overflow: hidden` + `border-radius: 12px` 双重裁切确保视觉一致。
