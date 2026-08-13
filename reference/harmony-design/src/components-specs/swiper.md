# Swiper

统一 Swiper 组件，合并原 `SwiperBanner2in1`、`SwiperNumberPhone`、`SwiperProgressBannerPhone`。

## Metadata

| 字段 | 值 |
|------|-----|
| 实现目录 | `src/components/Swiper/` |
| Stories 路径 | `src/components/Swiper/Swiper.stories.tsx` |
| JSON 路径 | `src/components/Swiper/swiper.json` |

`banner-2in1` 左右翻页按钮使用本地 HMSymbol `chevron_left`（U+F00DA）与 `chevron_right`（U+F00D9）。

## 变体（`变体` prop）

| 变体 | 原组件 | 主要 Props |
|------|--------|------------|
| `banner-2in1` | SwiperBanner2in1 | `尺寸`, `banners`, `活跃索引`, `onIndexChange` |
| `number-phone` | SwiperNumberPhone | `当前页`, `总页数` |
| `progress-banner-phone` | SwiperProgressBannerPhone | `激活索引`, `进度数` |

## 示例

`banner-2in1` 支持受控 `活跃索引` + `onIndexChange`（内外箭头/外层手势均可驱动）。

```tsx
const [index, setIndex] = useState(0)
<Swiper 变体="banner-2in1" banners={slides} 活跃索引={index} onIndexChange={setIndex} />
<Swiper 变体="number-phone" 当前页={12} 总页数={22} />
<Swiper 变体="progress-banner-phone" 激活索引={0} 进度数={5} />
```

圆点指示器见独立组件 `FloatingSwiperDotPhone`。
