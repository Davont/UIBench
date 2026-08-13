# FloatingSwiperDotPhone（FloatingSwiper-Dot-Phone）

## Metadata

| 字段 | 值 |
|------|-----|
| 实现目录 | `src/components/FloatingSwiperDotPhone/` |
| Stories 路径 | `src/components/FloatingSwiperDotPhone/FloatingSwiperDotPhone.stories.tsx` |
| Pixso 链接 | `https://pixso.cn/app/design/H81fph4IPxYjDA3GCQmGGQ?item-id=5316:19502` |
| Pixso 组件名 | FloatingSwiper-Dot-Phone / Swiper-Dot-Phone |

## 组件变体树 JSON

| 字段 | 值 |
|------|-----|
| JSON 路径 | `src/components/FloatingSwiperDotPhone/floating-swiper-dot-phone.json` |

## 导出

| 导出项 | 说明 |
|--------|------|
| `FloatingSwiperDotPhone` | 悬浮轮播圆点指示器 |
| `floatingSwiperDotPhoneTypes` | `["OFF", "ON", "带symbol"]` |
| `floatingSwiperDotPhoneCounts` | `[2, 3, 4, 5, 6]` |
| `活跃索引` | 当前高亮圆点（0-based），与页面轮播同步 |
| `onIndexChange` | 点击圆点时回调，供外层切换轮播页 |

**使用场景：** 图片轮播底部分页指示器（原 `SwiperDot`）。

```tsx
const [index, setIndex] = useState(0)
<FloatingSwiperDotPhone 类型="OFF" 组数={5} 活跃索引={index} onIndexChange={setIndex} />
```
