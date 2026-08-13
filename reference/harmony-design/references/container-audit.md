# 集合容器深度审计

批量页面、大量重复 JSX、横向 chips/Tab、宫格、KPI、海报/商品网格、双层卡、集合边界或 Pixso item 出错时读取。常规简单页面不要预加载。

## 目录

1. 容器决策
2. 正向审计
3. 反向审计
4. 直接子项审计
5. List Block 与 ListContainer
6. 常见反模式

所有命令只针对当前任务的 `<TARGET_DIR>`，不得硬编码扫描历史 render 集合。

## 1. 容器决策

```text
多个同构兄弟节点？
├─ 否：视觉装饰、图表、波形、纯静态结构 → 保留普通语义容器
└─ 是
   ├─ 单轴排列：单列或单行滚动 → ListContainer
   └─ 二维排列：多行多列、自适应列、跨行/跨列 → GridContainer
```

- Tab、导航、按钮组、筛选组、单行轮播仍属于单轴集合。
- 商品、海报、应用入口、KPI 面板等二维布局属于 Grid。
- 瀑布流使用匹配的 WaterFlow/masonry，不强行解释为普通 Grid。
- 同一集合不得同时使用或嵌套 `ListContainer` 与 `GridContainer`。

## 2. 正向审计

逐个页面回答：

1. 页面中有哪些 `ListContainer`？
2. 每个直接子项是否为 `ListPhone`？
   - 是：豁免 `pixso-list-item`
   - 否：最终根节点必须包含 `pixso-list-item`
3. 页面中有哪些 `GridContainer`，为什么属于二维网格？
4. Grid 的每个直接子项最终根节点是否包含 `pixso-grid-item`？
5. 容器是否直接承担原根节点的布局、滚动、裁切、样式、data 和可访问性职责？
6. 是否为了容器或 item class 新增了无职责包装层？

## 3. 反向审计

先定位当前目标中可能遗漏的同构集合：

```bash
rg -n -B 8 -A 4 "\\.map\\(" <TARGET_DIR> --glob '*.{ts,tsx,js,jsx}'
rg -n "<(div|section|nav|ul|ol)[^>]*>" <TARGET_DIR> --glob '*.{ts,tsx,js,jsx}'
```

对每个 `.map()` 或连续重复 JSX 判断：

1. 是否生成多个同构业务条目？
2. 最近的集合根节点是什么？
3. 单轴还是二维？
4. 是否已使用正确容器？
5. 直接子项是否包含正确 Pixso class？

以下通常不需要 List/Grid：

- 纯视觉波形条或图表柱
- 时间线装饰节点
- 日历内部绘制单元
- 不构成业务集合的静态结构

如果这些节点本身承载可操作业务项，重新按单轴/二维判定。

## 4. 直接子项审计

- Pixso class 必须位于容器的直接子项最终 DOM 根节点。
- 自定义组件通过已有 `className` 透传能力接收 class。
- Fragment 内的每个直接真实节点分别检查。
- 不得把 class 放到容器自身或更深层后代。
- 除下述嵌套 `ListContainer` 特例外，不得通过 `cloneElement` 运行时注入或新增 wrapper 规避。
- 动态类名使用 `cn("pixso-list-item", existing)` 或 `cn("pixso-grid-item", existing)`，不得覆盖原类名。

多行 JSX 至少向后检查到真实 `className`，不要只看开标签首行。

### 嵌套 ListContainer 列表项

内层 `ListContainer` 本身是外层 `ListContainer` 的直接列表项时，必须增加一个合法语义父节点：

```tsx
<ListContainer as="ul">
  {groups.map((group) => (
    <li
      key={group.id}
      className="pixso-list-item"
    >
      <ListContainer className="group-list">
        {/* group items */}
      </ListContainer>
    </li>
  ))}
</ListContainer>
```

- 外层渲染为 `ul` / `ol` 时使用 `li`；其他场景使用 `div` 或对父级合法的语义元素。
- 把循环 `key` 移到新增包装节点。
- 从内层 `ListContainer` 移除 `pixso-list-item`，不得重复保留。
- 内层 `ListContainer` 原有的其他 class、布局、样式、`data-*` 与可访问性属性保持不变。
- 包装节点只承载 `key` 和 `pixso-list-item`，不得使用 `display: contents`，也不得接管内层容器职责。

## 5. List Block 与 ListContainer

| 场景 | 使用 | 原因 |
| --- | --- | --- |
| 设置项列表（开关、跳转、值、chevron） | `List` Block | 复用统一 ListPhone 行与卡片壳 |
| 自定义记录行、通知行、复合卡片 | `ListContainer` | 保留页面自定义行布局 |
| 横向 chips、Tab、按钮组 | `ListContainer` | 单轴集合 |
| 应用入口、商品、KPI 宫格 | `GridContainer` | 二维集合 |
| 波形、图表、纯装饰时间线 | 普通容器 | 不属于业务条目集合 |

不要把 `List` Block 当作纯集合容器，否则容易产生双层白底、固定宽度和语义错位。

## 6. 常见反模式

- 子项内部使用了 `ListPhone`，便误以为外层不需要 `ListContainer`
- 删除 `List` Block 后改成裸 `div`，同时丢失集合语义
- KPI 或快捷入口因为只有一行，误判成 List；只要布局模型是二维面板仍使用 Grid
- 外层 `section` 内虽然已有正确容器，却因粗扫产生假阳性
- Pixso class 脱离对应容器，挂在普通容器的子项上
- 为了修 class 新增 wrapper，导致 DOM 层级膨胀
- 嵌套 `ListContainer` 直接承担 `pixso-list-item`，未使用透明合法语义包装节点

审计结果写入日志的 `Compliance`，只记录当前目标的实际容器和结论。
