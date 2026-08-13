# FloatingTab

## Metadata

- Implementation: `src/components/FloatingTab`
- Stories: `src/components/FloatingTab/FloatingTab.stories.tsx`
- Variant JSON: `src/components/FloatingTab/floating-tab.json`
- Pixso link: `https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5344:21809`
- item-id: `5344:21809`
- MCP calls: `get_node_dsl`, `get_screenshot`, `get_variants`

## MCP Result And Fallback

- `get_node_dsl`: success. Source node `容器 9` (`5344:21809`) contains `FloatingTab-Phone` (`5344:21795`).
- `get_screenshot`: success. Screenshot confirms three phone tabs, first active, second/third inactive.
- `get_variants`: returned `{}`. The variant tree JSON is reconstructed from `get_node_dsl.pixTreeNodes` and `get_node_dsl.pixComponentTreeDslNodes`.
- Fallback scope: only variant tree extraction falls back. The 3-tab geometry, color, typography, and state values are from DSL plus screenshot; 2/4/5-tab panel sizes are user-supplied companion specs.

## Quantified Specs

- Root frame: `409px × 173px`, white fill.
- Component frame for the linked `3` tab node: `236px × 56px`, located at `left=87px`, `top=63px`.
- Panel sizes by `数量`: `2 -> 160px × 56px`, `3 -> 236px × 56px`, `4 -> 328px × 56px`, `5 -> 328px × 56px`.
- Surface radius: `100px`.
- Surface padding: `top=4px`, `right=12px`, `bottom=4px`, `left=12px`.
- Inner rail: `212px × 48px`.
- Tab count in linked node: `3`; each layout slot is `70.6667px × 48px`.
- Slot widths by `数量`: `2 -> 68px`, `3 -> 70.6667px`, `4 -> 76px` inferred from `(328px - 24px padding) / 4`, `5 -> 60.8px`.
- Tab component visual content: icon `24px × 24px` at `top=4px`; label at `top=30px`, `17px × 14px`.
- Tab vertical gap: `2px`; tab vertical padding: `4px`.
- Label text: `Tab`; font family `HarmonyHeiTi`; font style `Medium`; font size `10px`; weight `500`; line-height implemented as `14px`; letter-spacing `0`.
- Active colors: label `Light/font_emphasize` and icon `Light/icon_emphasize`, both `rgba(10, 89, 247, 1)`.
- Inactive colors: label `Light/font_primary` and icon `Light/icon_primary`, both `rgba(0, 0, 0, 0.898039)`.
- Standard surface fill: `Light/Blur/FLOATING_THIN`, two white fills at `rgba(255, 255, 255, 0.1)`.
- Standard surface effects: drop shadow `0 8px 48px rgba(0,0,0,0.08)`, background blur radius `30px`, saturation `20`, and inner shadows from `Light/Blur/FLOATING_THIN`.
- Companion transparency tiers: `强` uses the existing ultra-thin material token; `降档` uses the floating smooth fill plus floating line token.

## DSL Components And Variants

- Container node: `容器 9`, `guid=5344:21809`.
- Floating node: `FloatingTab-Phone`, `guid=5344:21795`.
- Component states from `pixComponentTreeDslNodes`:
  - `激活=ON`, `guid=4126:12196`, `componentNormName=ON`.
  - `激活=OFF`, `guid=4126:12198`, `componentNormName=OFF`.
  - icon subcomponent `状态=Activated`, `guid=4126:12149`.
  - icon subcomponent `状态=Enable`, `guid=4126:12158`.
- Component property:
  - `propDefMap.visible_4248_1.name=文本`
  - `type=visible`
  - `defaultValue=true`
- Instance states in the target node: `["ON", "OFF", "OFF"]`.

## DSL To Props

| DSL / Pixso field | Prop | Values | Default | Notes |
| --- | --- | --- | --- | --- |
| `激活` from `激活=ON/OFF` | `激活` | `"ON"`, `"OFF"` per item | `["ON","OFF","OFF"]` | Array preserves the three instance states in the node. |
| `propDefMap.visible_4248_1.name` | `文本` | `true` | `true` | Direct Pixso prop name, controls label visibility. |
| `Light/Blur/FLOATING_THIN` | `材质` | `"Floating_Thine"` | `"Floating_Thine"` | Existing repo spelling retained for compatibility; maps to Pixso FLOATING_THIN material. |
| phone layout in node | `land` | `"OFF"` | `"OFF"` | Existing repo prop; `OFF` maps to phone/portrait. |
| single visual state | `状态` | `"默认"` | `"默认"` | Repo API field, no extra DSL visual states on this node. |
| transparency tier | `通透度` | `"标准"`, `"强"`, `"降档"` | `"标准"` | `标准` maps to `Light/Blur/FLOATING_THIN`; `强` and `降档` are companion material display tiers. |
| child count | `数量` | `"2"`, `"3"`, `"4"`, `"5"` | `"3"` | The linked node has three tabs; 2/4/5 dimensions are supplied companion specs. |

Runtime integration helpers `items`, `activeKey`, `defaultActiveKey`, `onActiveKeyChange`, and `layout` are not Pixso fields; they adapt the static design component for React usage. `activeKey` can override the DSL-derived active item at runtime.

## Global CSS Mapping

- Reused `global.css` material layers: `.hm-material-style-layer-floating-thin-fill-*` and `.hm-material-style-layer-floating-thin-effect-*`.
- Reused `global.css` tokens: `--Material_background_ULTRA_THIN_fill`, `--comp_background_color_floating_smooth_fill`, `--Floating_background_line_fill`, `--harmony-font-primary`, `--harmony-font-emphasize`, `--harmony-icon-primary`, `--harmony-icon-emphasize`.
- Added tokens: none. Existing global tokens match the DSL FLOATING_THIN material, font, and icon color styles closely enough for reuse.

## Storybook

- `Playground`: default DSL args: `数量="3"`, `land="OFF"`, `材质="Floating_Thine"`, `通透度="标准"`, `状态="默认"`, `激活=["ON","OFF","OFF"]`, `文本=true`.
- `PixsoMatrix`: renders `标准` / `强` / `降档` sections for each supported tab count on the repository canvas wrapper `bg-[#f3f4f6] p-8`.

## Usage Rules

### 组件默认高度

- **顶部间距**：`16px`（container `padding-top`）
- **Surface（tab 栏）**：`56px`
- **Bottombar（手势横条）**：`28px`
- **总高度**：`100px`（16 + 56 + 28）

### 底部导航栏场景（Bottom Navigation）

当 `FloatingTab` 用作页面底部导航栏时，必须遵循以下规则：

1. **禁止包裹在渐变遮罩容器中**：不得将 `FloatingTab` 嵌套在带有 `linear-gradient` 背景的 wrapper div 内（如 `service-search-template__bottom-nav`）。该渐变遮罩是音乐搜索页特有的视觉效果，不适用于通用底部导航场景。

2. **直接贴底，底部距离为 0**：`FloatingTab` 容器底部与页面/屏幕底部对齐，`bottom: 0`，无额外 padding 或 margin。

3. **水平居中**：在 360px 画布中，328px 宽的 FloatingTab 应水平居中（左右各 16px）。推荐实现方式：

   ```css
   .bottom-nav-container {
     display: flex;
     justify-content: center;
     align-items: flex-end;
     padding: 0;
     background: none; /* 无渐变遮罩 */
     height: auto;     /* 不固定高度 */
   }
   ```

4. **与模板 slot 的配合**：当使用 `ServiceSearchTemplatePage` 等模板的 `bottomNavSlot` 时，需通过 CSS 覆盖模板容器的默认渐变背景和固定高度：

   ```css
   .your-page .service-search-template__bottom-nav {
     background: none;
     height: auto;
     padding: 0;
     display: flex;
     justify-content: center;
     align-items: flex-end;
   }
   ```

### 音乐播放器场景（MiniPlayer / 1+bar）

当 `FloatingTab` 以 `数量="1+bar"` 变体用作音乐播放条时，保留模板默认的渐变遮罩效果（此为该场景的视觉需求）。

## Tradeoffs

- `get_variants` did not return Pixso variants, so `floating-tab.json` is rebuilt from the successful DSL response.
- CSS cannot express Pixso blend modes such as `LINEAR_DODGE` exactly across all browsers; the implementation uses the repository's established global material layer classes and standard CSS backdrop/shadow properties as the closest runnable equivalent.
