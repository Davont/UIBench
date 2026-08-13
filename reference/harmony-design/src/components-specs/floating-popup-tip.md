# FloatingPopupTip

## Metadata

| 属性 | 值 |
|------|-----|
| 实现目录 | `src/components/FloatingPopupTip` |
| stories 路径 | `src/components/FloatingPopupTip/FloatingPopupTip.stories.tsx` |
| Pixso 链接 | https://pixso.cn/app/design/HA_e8I2mE7Oa0b5ZoeokSA?item-id=5322:558 |
| MCP 工具来源 | Pixso MCP (`get_node_dsl`, `get_screenshot`, `get_variants`, `design_to_code`, `get_all_components`) |
| 变体树 JSON | `src/components/FloatingPopupTip/floating-popup-tip.json` |

## 组件变体树 JSON

- 路径：`src/components/FloatingPopupTip/floating-popup-tip.json`
- 生成方式：`get_variants` 返回 `{}`，改为从根节点 `5322:558` 的 DSL 读取矩阵，再对 `5322:373 / 384 / 400 / 419 / 430 / 446 / 465 / 476 / 492 / 511 / 522 / 538` 做定点探测补全叶子 guid
- `variantOptions`
  - `类型`: `Text | multiline text | Full pattern`
  - `通透度`: `标准 | 强 | 降档 | 弱`

## 组成与用途

- 导出项：`FloatingPopupTip`
- 变体常量：`floatingPopupTipTypes`、`floatingPopupTipTransparencies`
- 用途：浮动提示气泡，覆盖单行文本、双行说明、带图片标题说明三种结构，叠加四档浮层材质

## 量化规格

- 宽度：`312px`
- 高度：
  - `Text`: `44px`
  - `multiline text`: `90px`
  - `Full pattern`: `114px`
- 圆角：`20px`
- Padding：`12px`
- Gap：
  - `Text`: `10px`
  - 其余：`12px`
- 图片：
  - 尺寸：`32 × 32`
  - 圆角：`8px`
- 链接行：
  - 间距：`16px`
  - 单个宽度：`75px`

## Typography

- 主文本 `Text`
  - `fontSize: 14px`
  - `fontWeight: 400`
  - `lineHeight: 20px`
  - `letterSpacing: 0px`
- 标题 `Full pattern`
  - `fontSize: 16px`
  - `fontWeight: 500`
  - `lineHeight: 22px`
  - `letterSpacing: 0px`
- 描述与链接
  - `fontSize: 14px`
  - 描述 `fontWeight: 400`, `lineHeight: 19px`
  - 链接 `fontWeight: 500`, `lineHeight: 20px`

## 状态与交互

- `close=true` 时显示关闭按钮，点击触发 `onClose`
- `image=true` 时仅 `Full pattern` 显示左侧图片
- `Link=true` 时显示双链接行动区

## Props

| DSL 字段 | Prop 名 | 默认值 | 取值 |
|----------|---------|--------|------|
| 变体名 `类型=*` | `类型` | `Text` | `Text \| multiline text \| Full pattern` |
| 变体名 `通透度=*` | `通透度` | `标准` | `标准 \| 强 \| 降档 \| 弱` |
| `visible_27_7 / close` | `close` | `true` | `boolean` |
| `visible_27_9 / image` | `image` | `true` | `boolean` |
| `visible_27_11 / Link` | `Link` | `true` | `boolean` |
| 文本节点 | `title` | DSL 默认文案 | `string` |
| 文本节点 | `description` | DSL 默认文案 | `string` |
| 文本节点 | `linkText1` | `Text button` | `string` |
| 文本节点 | `linkText2` | `Text button` | `string` |
| 图片节点 | `imageSrc` | PopupTip 默认图 | `string` |

## 样式引用

- 使用的全局 token
  - `--harmony-comp-background-primary`
  - `--harmony-font-primary`
  - `--harmony-font-secondary`
  - `--harmony-font-emphasize`
  - `--harmony-icon-secondary`
  - `--Material_background_THICK_fill`
  - `--FLOATING_THICK_fill`
- 使用的全局材质层
  - `hm-material-style-layer-floating-thick-fill-1`
  - `hm-material-style-layer-floating-thick-fill-2`
  - `hm-material-style-layer-floating-thick-effect-2...8`
- 新增全局 token：无

## 取舍说明

- `design_to_code` 对该节点返回 `500`，未作为最终结构来源
- `get_screenshot` 可用，因此最终排版与材质以截图为主、DSL 为量化辅证
- `标准` 档采用仓库已有 `FLOATING_THICK` 多层材质层实现；`强 / 降档 / 弱` 直接映射 DSL 对应填充和 effect 组合
- 设计稿是带背景矩阵的总览 frame，不是单个组件主件；因此 story 中单独提供了 `Overview` 作为 12 态对照面板
