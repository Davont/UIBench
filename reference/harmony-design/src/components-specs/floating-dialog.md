# FloatingDialog

## Metadata

| 字段 | 值 |
|------|-----|
| 实现目录 | `src/components/FloatingDialog/` |
| Stories 路径 | `src/components/FloatingDialog/floatingdialog.stories.tsx` |
| Pixso 链接 | `https://pixso.cn/app/design/Xs4by4YngOt5unb-_N4vxQ?item-id=5441:19170` |
| item-id | `5441:19170` |
| 变体树 JSON | `src/components/FloatingDialog/floatingdialog.json` |
| MCP 工具来源 | `get_node_dsl(guid=5441:19170)` 成功；`get_screenshot(guid=5441:19170)` 成功，PNG `766 × 914`；`get_variants(guid=5441:19170)` 返回 `{}`；`design_to_code(guids=["5441:19170"], clientFrameworks="react")` 返回 500 |
| 变体树来源 | `get_variants` 为空，按 `get_node_dsl.pixTreeNodes[].name` 中 `类型=... , 通透度=...` 重建 |

## 组成与用途

FloatingDialog 是 Harmony 浮动弹窗组件，覆盖纯内容、内容+按钮、标题+内容、标题+内容+按钮、进度条、进度条+按钮等轻量确认/进度提示场景。

### 导出项

- `FloatingDialog` — 主组件
- `FloatingDialogProps` — Props 类型
- `FloatingDialog类型` — Pixso `类型` 联合类型
- `FloatingDialog通透度` — Pixso `通透度` 联合类型
- `floatingDialog类型Options` / `floatingDialog通透度Options` — Storybook controls 与矩阵枚举

## DSL 组件属性/变体字段

| DSL 字段 | 取值 |
|----------|------|
| `类型` | `content` / `content+button` / `title+content_single line` / `title+content_2lines` / `title+content+2 button` / `title+content+3 button` / `progress bar` / `progress bar+button` |
| `通透度` | `标准` |

## 量化规格

| 参数 | 值 | 来源 |
|------|-----|------|
| 矩阵截图 | `766 × 914px` | `get_screenshot` |
| `content` | `328 × 90px` | DSL `5441:19171` |
| `content+button` | `328 × 109px` | DSL `5441:19174` |
| `title+content_single line` | `328 × 122px` | DSL `5441:19187` |
| `title+content_2lines` | `328 × 138px` | DSL `5441:19180` |
| `title+content+2 button` | `328 × 162px` | DSL `5441:19192` |
| `title+content+3 button` | `328 × 242px` | DSL `5441:19203` |
| `progress bar` | `328 × 96px` | DSL `5441:19216` |
| `progress bar+button` | `299 × 136px` | DSL `5441:19229` |
| 外层圆角 | `32px` | DSL `cornerRadius=32` 或四角 `32` |
| 外层材质 | `Light/Blur/FLOATING_ULTRA_THICK` | DSL `inheritFillStyleID=4528:17205`, `inheritEffectStyleID=4528:17209` |
| 外层填充 | `rgba(241,243,245,0.9)` | DSL local style `4528:17205`，实现复用 `--harmony-floating-ultra-thick-surface` |
| 背景模糊 | `blur(40px) saturate(120%)` | DSL local style `4528:17209` 与 `global.css` token |
| 阴影 | `0 8px 48px rgba(0,0,0,0.08)` 加多层 inner shadow | DSL local style `4528:17209` 与 `global.css` token |
| 主 padding | `24px` | `content` / `progress bar` DSL autoLayout padding |
| 标题区 | `312 × 56px`，padding `15px 24px` | DSL `LineOFF` |
| 标题+副标题区 | `312 × 72px`，padding `12px 24px`，gap `3px` | DSL `LineON` |
| 标题字体 | HarmonyHeiTi Bold `20px / 26px` | DSL `Font/Title_S/Bold` |
| 副标题字体 | HarmonyHeiTi Medium `14px / 19px` | DSL `Font/Body_M/Medium` |
| 正文字体 | HarmonyHeiTi Medium `16px / 21px` | DSL `Font/Body_L/Medium` |
| 正文块 | 两行 `280 × 42px`；单行 `280 × 21px` | DSL `1783:9440` / `1783:9442` |
| 按钮 | `120 × 40px`，圆角 `20px`，padding `9px 16px` | DSL Button instance |
| 双按钮行 | 宽 `328px`，左右 padding `16px`，gap `16px`，底部 padding `16px` | DSL `1:11560` |
| 三按钮列 | 宽 `328px`，按钮区高 `136px`，gap `4px`，底部 padding `8px` | DSL `1:11568` |
| `progress bar+button` 按钮区 | 子实例 `top=80`, `left=24`, `328 × 56px`；覆盖后符号宽 `251px`，按钮实例 `219 × 40px`，文字框 `187 × 21px`，蓝色文字按钮 | DSL `5441:19242` → `1:11558` → `58:35444` / `1:9458` |
| 进度块 | 通用 `200 × 48px`；`progress bar+button` 覆盖为 `251 × 48px`，位于 `top=24`, `left=24` | DSL `1:11619`, `5441:19230.props[0].width=251` |
| `progress bar+button` 进度轨道 | 轨道 `215 × 4px`，激活段 `92.5694 × 4px`，关闭按钮相对进度组 `left=227` | DSL `1:11624/36:34897`, `1:11624/1:13064`, `1:11625` |
| 进度文字 | Title `14px / 20px` Regular primary；`50%` 为 HarmonyHeiTi Regular `14px / 20px`、`32px` 宽、右对齐、secondary | DSL `1:11621`, `1:11623`, `inheritTextStyleID=602:9661` |
| 进度条 | 高 `4px`，圆角 `2px` | DSL `ProgressBar-Linear-Phone` |
| 关闭按钮 | `24 × 24px` 圆形 | DSL `.close` instance |

## Props

| Prop | 类型 | 默认值 | DSL 对齐 |
|------|------|--------|----------|
| `类型` | `FloatingDialog类型` | `content` | 完全使用 DSL 字段名与取值 |
| `通透度` | `FloatingDialog通透度` | `标准` | 完全使用 DSL 字段名与取值 |
| `className` | `string` | - | React 样式扩展，不映射 DSL 变体 |

### DSL ↔ Prop 对照

| DSL 字段 | Prop | 取值一致性 |
|----------|------|-----------|
| `类型` | `类型` | 完全一致 |
| `通透度` | `通透度` | 完全一致 |

## 样式引用

### 复用 global.css Token / 类

| Token / 类 | 用途 |
|------------|------|
| `.hm-material-floating-ultra-thick` | FLOATING_ULTRA_THICK 表面、模糊、inner shadow、drop shadow |
| `--harmony-font-primary` | 标题、正文、进度 Title |
| `--harmony-font-secondary` | 副标题、进度百分比 |
| `--harmony-font-emphasize` | Text 按钮文字 |
| `--harmony-font-on-primary` | Emphasized 按钮文字 |
| `--harmony-comp-background-emphasize` | Emphasized 按钮、进度值 |
| `--harmony-comp-background-secondary` | 进度轨道 |
| `--harmony-icon-tertiary` | 关闭按钮背景 |
| `--harmony-interactive-hover` / `--harmony-interactive-pressed` | 按钮交互叠层 |

### 新增 Token

无。DSL 中的材质、色值、字体角色均可复用现有 `global.css`。

## 状态与交互

| 状态 | 说明 |
|------|------|
| Default | 与 DSL 标准态一致 |
| Hover | 按钮叠加 `--harmony-interactive-hover` |
| Pressed | 按钮叠加 `--harmony-interactive-pressed` |

## 取舍说明

1. `get_variants` 返回 `{}`，因此 `floatingdialog.json` 从 `get_node_dsl.pixTreeNodes[].name` 解析 `类型` / `通透度` 重建，未改变取值集合。
2. `design_to_code` 返回 500，仅记录为失败；实现依据为 `get_node_dsl` + `get_screenshot`。
3. DSL 中按钮和进度条为子组件实例；为保证按钮文案与截图 `BUTTON` 一致，FloatingDialog 内部以局部 CSS 还原按钮几何与颜色，而不是复用仓库 `Button` 的固定默认文案。
4. `progress bar+button` 的按钮子组件是 `normal,个数=1` / `MediumTextEnabled`，因此实现为蓝色文字按钮，不使用 Emphasized 蓝底按钮。
5. 单节点 `5441:19229` 中进度与按钮存在实例覆盖尺寸：进度符号宽 `251px`、轨道宽 `215px`、激活段宽 `92.5694px`、按钮宽 `219px`。实现对该变体单独覆盖通用进度/按钮几何，以单节点 `get_screenshot(guid=5441:19229)` 视觉为准。
6. `progress bar` 与 `progress bar+button` 中的 `50%` 均使用子节点 `1:11623` 的字体规格：`Font/Body_M/Regular` / `602:9661`，即 HarmonyHeiTi Regular `14px / 20px`，宽 `32px` 且右对齐；实现中用独立 `.hm-floating-dialog__progress-percent` 锁定，避免继承标题或按钮字体。
