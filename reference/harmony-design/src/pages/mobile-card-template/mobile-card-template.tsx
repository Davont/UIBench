import type { ReactNode } from "react"
import { useState } from "react"

import type { BottomTabItem } from "@/components/Navigation/BottomTab/bottom-tab"
import { HMSymbolIcon } from "@/components/HMSymbolIcon"
import { Search } from "@/components/Input/Search"
import {
  FloatingSwiperDotPhone,
  type FloatingSwiperDotPhoneCount,
} from "@/components/Navigation/FloatingSwiperDotPhone"
import { GridContainer } from "@/container-components/GridContainer"
import { ListContainer } from "@/container-components/ListContainer"
import { cn } from "@/lib/utils"
import { MobilePhoneShellTemplatePage } from "@/pages/mobile-phone-shell-template"

import "./mobile-card-template.css"

export interface MobileCardHeroItem {
  id: string
  title: string
  subtitle?: string
  bg: string
}

export interface MobileCardEntranceItem {
  id: string
  label: string
  icon: ReactNode
}

export interface MobileCardHorizontalCard {
  id: string
  coverBg: string
  title: string
  subtitle: string
  rating?: string
}

export interface MobileCardThumbCard {
  id: string
  coverBg: string
  title: string
  subtitle: string
  rating?: string
  showPlay?: boolean
}

export interface MobileCardFeatureLarge {
  id: string
  coverBg: string
  overlayTitle: string
  rating: string
  thumbBg: string
  title: string
  subtitle: string
  actionLabel: string
}

export interface MobileCardHorizontalFeature {
  id: string
  posterBg: string
  title: string
  meta: string
  plays: string
}

export interface MobileCardVerticalFeature {
  id: string
  coverBg: string
  title: string
  subtitle: string
}

export interface MobileCardSection {
  id: string
  title?: string
  variant:
    | "hero"
    | "entrance"
    | "h2col"
    | "thumb"
    | "feature-large"
    | "hfeature"
    | "vfeature"
  /** payload varies per variant; consumers may pass through with type assertions. */
  data: unknown
}

export type MobileCardBottomTabItem = BottomTabItem

export interface MobileCardTemplatePageProps {
  className?: string
  title?: string
  searchPlaceholder?: string
  tabs?: MobileCardBottomTabItem[]
  activeTabKey?: string
  onSearchClick?: () => void
  onActionClick?: () => void
  onTabChange?: (key: string) => void
  sections?: MobileCardSection[]
}

const DEFAULT_HERO: MobileCardHeroItem[] = [
  { id: "h1", title: "春日新品", subtitle: "限时折扣 5 折起", bg: "linear-gradient(135deg,#fbb5a1 0%,#f17a52 60%,#ed6f21 100%)" },
  { id: "h2", title: "城市漫游", subtitle: "本周热门路线", bg: "linear-gradient(135deg,#5a6cf3 0%,#2c3eb1 100%)" },
  { id: "h3", title: "会员专享", subtitle: "积分兑好礼", bg: "linear-gradient(135deg,#3ec1a3 0%,#0c8a72 100%)" },
  { id: "h4", title: "夜读电台", subtitle: "每晚 8 点更新", bg: "linear-gradient(135deg,#7a5af8 0%,#3a1f9b 100%)" },
  { id: "h5", title: "编辑精选", subtitle: "38 件作品", bg: "linear-gradient(135deg,#f5a524 0%,#b65b00 100%)" },
]

function heroDotCount(count: number): FloatingSwiperDotPhoneCount {
  return Math.min(6, Math.max(2, count)) as FloatingSwiperDotPhoneCount
}

function buildEntrance(): MobileCardEntranceItem[] {
  return [
  { id: "e1", label: "分类", icon: <HMSymbolIcon name="dot_grid_2x2" size={20} /> },
  { id: "e2", label: "排行", icon: <HMSymbolIcon name="star_fill" size={20} /> },
  { id: "e3", label: "优惠", icon: <HMSymbolIcon name="bookmark" size={20} /> },
  { id: "e4", label: "收藏", icon: <HMSymbolIcon name="bookmark_filled_on_bookmark" size={20} /> },
  { id: "e5", label: "会员", icon: <HMSymbolIcon name="person_crop_circle_fill_1" size={20} /> },
  ]
}

const DEFAULT_H2COL: MobileCardHorizontalCard[] = [
  { id: "h2c1", coverBg: "linear-gradient(135deg,#5a6cf3,#2c3eb1)", title: "设计灵感周刊", subtitle: "Editorial · 12 篇文章", rating: "9.2" },
  { id: "h2c2", coverBg: "linear-gradient(135deg,#7a5af8,#3a1f9b)", title: "前端架构实战", subtitle: "Engineering · 8 节课", rating: "8.7" },
  { id: "h2c3", coverBg: "linear-gradient(135deg,#3ec1a3,#0c8a72)", title: "商业观察日报", subtitle: "Insight · 24 篇", rating: "8.9" },
  { id: "h2c4", coverBg: "linear-gradient(135deg,#f5a524,#b65b00)", title: "影视解说精选", subtitle: "Story · 16 集", rating: "9.0" },
]

const DEFAULT_THUMB: MobileCardThumbCard[] = [
  { id: "t1", coverBg: "linear-gradient(135deg,#0a59f7,#0a3180)", title: "夜色电台", subtitle: "晚安", rating: "8.6", showPlay: true },
  { id: "t2", coverBg: "linear-gradient(135deg,#9b51e0,#5e2f9c)", title: "城市速写", subtitle: "City Pop", rating: "8.2", showPlay: true },
  { id: "t3", coverBg: "linear-gradient(135deg,#ff6b81,#c41e3a)", title: "热歌雷达", subtitle: "Top 100", rating: "9.1", showPlay: true },
]

const DEFAULT_FEATURE_LARGE: MobileCardFeatureLarge = {
  id: "fl1",
  coverBg: "linear-gradient(135deg,#1f2235 0%,#3a3f5a 60%,#0c0e1a 100%)",
  overlayTitle: "编辑精选 · 春日合辑",
  rating: "9.4",
  thumbBg: "linear-gradient(135deg,#0a59f7,#0a3180)",
  title: "本周话题榜首",
  subtitle: "12 位创作者 · 38 件作品",
  actionLabel: "已关注",
}

const DEFAULT_HFEATURE: MobileCardHorizontalFeature[] = [
  { id: "hf1", posterBg: "linear-gradient(135deg,#ff7e5f,#feb47b)", title: "回归线", meta: "电影 . 剧情片 . 2024", plays: "128 万次播放" },
  { id: "hf2", posterBg: "linear-gradient(135deg,#43cea2,#185a9d)", title: "深潜日志", meta: "纪录片 . 自然 . 2023", plays: "62 万次播放" },
  { id: "hf3", posterBg: "linear-gradient(135deg,#7f7fd5,#86a8e7)", title: "夏日漱石", meta: "MV . 流行 . 2022", plays: "240 万次播放" },
]

const DEFAULT_VFEATURE: MobileCardVerticalFeature[] = [
  { id: "v1", coverBg: "linear-gradient(135deg,#ffb86b,#ff7a59)", title: "城市游荡指南", subtitle: "City · 12 个目的地" },
  { id: "v2", coverBg: "linear-gradient(135deg,#74ebd5,#9face6)", title: "周末手作清单", subtitle: "Craft · 8 个项目" },
  { id: "v3", coverBg: "linear-gradient(135deg,#f6d365,#fda085)", title: "厨房灵感辑", subtitle: "Food · 24 个菜谱" },
  { id: "v4", coverBg: "linear-gradient(135deg,#a1c4fd,#c2e9fb)", title: "摄影构图心得", subtitle: "Photo · 18 篇笔记" },
]

function buildTabs(): MobileCardBottomTabItem[] {
  return [
  { key: "home", label: "首页", icon: <HMSymbolIcon name="house_fill" size={24} /> },
  { key: "feed", label: "动态", icon: <HMSymbolIcon name="discover_fill" size={24} /> },
  { key: "shop", label: "会员购", icon: <HMSymbolIcon name="picture_fill" size={24} /> },
  { key: "me", label: "我的", icon: <HMSymbolIcon name="person_crop_circle_fill_1" size={24} /> },
  ]
}

function buildSections(): MobileCardSection[] {
  return [
    { id: "s-hero", variant: "hero", data: DEFAULT_HERO },
    { id: "s-entrance", variant: "entrance", data: buildEntrance() },
    { id: "s-h2col-1", variant: "h2col", data: DEFAULT_H2COL.slice(0, 2) },
    { id: "s-thumb", title: "编辑推荐", variant: "thumb", data: DEFAULT_THUMB },
    { id: "s-feature-large", title: "每日精选", variant: "feature-large", data: DEFAULT_FEATURE_LARGE },
    { id: "s-h2col-2", variant: "h2col", data: DEFAULT_H2COL.slice(2) },
    { id: "s-hfeature", title: "往期回顾", variant: "hfeature", data: DEFAULT_HFEATURE },
    { id: "s-vfeature", variant: "vfeature", data: DEFAULT_VFEATURE },
  ]
}

function HeroRegion({
  items,
  className,
}: {
  items: MobileCardHeroItem[]
  className?: string
}) {
  const [activeIndex, setActiveIndex] = useState(0)
  const dotCount = heroDotCount(items.length)
  const safeIndex = Math.min(activeIndex, Math.max(items.length - 1, 0))

  return (
    <section className={cn("layout-region layout-region-hero", className)}>
      <ListContainer className="layout-hero-banner">
        {items.map((it, i) => {
          const offset = i - safeIndex

          return (
            <div
              key={it.id}
              className={cn(
                "pixso-list-item",
                "layout-hero-banner__slide",
                i === safeIndex && "layout-hero-banner__slide--active",
              )}
              style={{
                background: it.bg,
                transform: `translateX(${offset * 100}%)`,
              }}
              aria-hidden={i !== safeIndex}
            >
              <div className="layout-hero-banner__copy">
                <div className="layout-hero-banner__title">{it.title}</div>
                {it.subtitle ? (
                  <div className="layout-hero-banner__subtitle">{it.subtitle}</div>
                ) : null}
              </div>
            </div>
          )
        })}
      </ListContainer>
      <FloatingSwiperDotPhone
        className="layout-hero-indicator"
        类型="OFF"
        组数={dotCount}
        活跃索引={safeIndex}
        onIndexChange={setActiveIndex}
      />
    </section>
  )
}

function EntranceRegion({
  items,
  className,
}: {
  items: MobileCardEntranceItem[]
  className?: string
}) {
  return (
    <section className={cn("layout-region layout-region-entrance", className)}>
      <GridContainer className="layout-entrance-grid">
        {items.map((it) => (
          <div key={it.id} className="pixso-grid-item layout-entrance-item">
            <div className="layout-entrance-item__icon">{it.icon}</div>
            <div className="layout-entrance-item__label">{it.label}</div>
          </div>
        ))}
      </GridContainer>
    </section>
  )
}

function HorizontalCardRow({ cards }: { cards: MobileCardHorizontalCard[] }) {
  return (
    <GridContainer className="layout-grid-2col">
      {cards.map((c) => (
        <div key={c.id} className="pixso-grid-item layout-card-h">
          <div className="layout-card-h__cover" style={{ background: c.coverBg }}>
            {c.rating ? (
              <span className="layout-card-h__rating">{c.rating}</span>
            ) : null}
          </div>
          <div className="layout-card-h__title">{c.title}</div>
          <div className="layout-card-h__subtitle">{c.subtitle}</div>
        </div>
      ))}
    </GridContainer>
  )
}

function SectionHeader({ title }: { title?: string }) {
  if (!title) return null
  return <header className="layout-section-header">{title}</header>
}

function ThumbRegion({ cards }: { cards: MobileCardThumbCard[] }) {
  return (
    <GridContainer className="layout-grid-3col">
      {cards.map((c) => (
        <div key={c.id} className="pixso-grid-item layout-card-thumb">
          <div className="layout-card-thumb__cover" style={{ background: c.coverBg }}>
            {c.showPlay ? (
              <span className="layout-card-thumb__play" aria-hidden="true">
                <HMSymbolIcon name="play_fill" size={18} />
              </span>
            ) : null}
            {c.rating ? (
              <span className="layout-card-thumb__rating">{c.rating}</span>
            ) : null}
          </div>
          <div className="layout-card-thumb__title">{c.title}</div>
          <div className="layout-card-thumb__subtitle">{c.subtitle}</div>
        </div>
      ))}
    </GridContainer>
  )
}

function FeatureLargeRegion({ data }: { data: MobileCardFeatureLarge }) {
  return (
    <div className="layout-card-feature-large">
      <div className="layout-card-feature-large__cover" style={{ background: data.coverBg }}>
        <div className="layout-card-feature-large__overlay-title">{data.overlayTitle}</div>
        <span className="layout-card-feature-large__play" aria-hidden="true">
          <span className="layout-card-feature-large__play-surface">
            <HMSymbolIcon name="play_fill" size={20} />
          </span>
        </span>
        <span className="layout-card-feature-large__rating">{data.rating}</span>
      </div>
      <div className="layout-card-feature-large__info">
        <div className="layout-card-feature-large__thumb" style={{ background: data.thumbBg }} />
        <div className="layout-card-feature-large__text">
          <div className="layout-card-feature-large__title">{data.title}</div>
          <div className="layout-card-feature-large__subtitle">{data.subtitle}</div>
        </div>
        <button type="button" className="layout-card-feature-large__action">
          {data.actionLabel}
        </button>
      </div>
    </div>
  )
}

function HorizontalFeatureRegion({ cards }: { cards: MobileCardHorizontalFeature[] }) {
  return (
    <ListContainer className="layout-card-hfeature-list">
      {cards.map((c) => (
        <div key={c.id} className="pixso-list-item layout-card-hfeature">
          <div className="layout-card-hfeature__poster" style={{ background: c.posterBg }} />
          <div className="layout-card-hfeature__body">
            <div className="layout-card-hfeature__title">{c.title}</div>
            <div className="layout-card-hfeature__meta">{c.meta}</div>
            <div className="layout-card-hfeature__plays">{c.plays}</div>
            <div className="layout-card-hfeature__actions">
              <button type="button" className="layout-card-hfeature__btn layout-card-hfeature__btn--play">
                播放
              </button>
              <button type="button" className="layout-card-hfeature__btn layout-card-hfeature__btn--cache">
                缓存
              </button>
            </div>
          </div>
        </div>
      ))}
    </ListContainer>
  )
}

function VerticalFeatureRegion({ cards }: { cards: MobileCardVerticalFeature[] }) {
  return (
    <GridContainer className="layout-grid-2col">
      {cards.map((c) => (
        <div key={c.id} className="pixso-grid-item layout-card-vfeature">
          <div className="layout-card-vfeature__img" style={{ background: c.coverBg }} />
          <div className="layout-card-vfeature__text">
            <div className="layout-card-vfeature__title">{c.title}</div>
            <div className="layout-card-vfeature__subtitle">{c.subtitle}</div>
          </div>
        </div>
      ))}
    </GridContainer>
  )
}

function MobileCardTemplatePage({
  className,
  title = "推荐",
  searchPlaceholder = "搜索...",
  tabs,
  activeTabKey,
  onSearchClick,
  onActionClick,
  onTabChange,
  sections,
}: MobileCardTemplatePageProps) {
  const resolvedTabs = tabs ?? buildTabs()
  const resolvedSections = sections ?? buildSections()
  const [uncontrolledActiveKey, setUncontrolledActiveKey] = useState(resolvedTabs[0]?.key ?? "home")
  const currentActive = activeTabKey ?? uncontrolledActiveKey

  return (
    <MobilePhoneShellTemplatePage
      className={className}
      mode="app-home"
      headerVariant="normal"
      title={title}
      headerActions={[
        {
          id: "titlebar-action",
          label: "Action",
          icon: <HMSymbolIcon name="dot_grid_2x2" size={20} />,
          onClick: onActionClick,
        },
      ]}
      tabs={resolvedTabs}
      activeTabKey={currentActive}
      onActiveTabChange={(key) => {
        setUncontrolledActiveKey(key)
        onTabChange?.(key)
      }}
      showFloatingTab
    >
      <section className="layout-mobile-card">
        <Search
          className="layout-search-bar"
          placeholder={searchPlaceholder}
          onClick={onSearchClick}
        />

        {resolvedSections.map((section) => {
          if (section.variant === "hero") {
            return (
              <HeroRegion key={section.id} items={section.data as MobileCardHeroItem[]} />
            )
          }
          if (section.variant === "entrance") {
            return (
              <EntranceRegion key={section.id} items={section.data as MobileCardEntranceItem[]} />
            )
          }
          if (section.variant === "h2col") {
            return (
              <section key={section.id} className="layout-region layout-region-h2col">
                <HorizontalCardRow cards={section.data as MobileCardHorizontalCard[]} />
              </section>
            )
          }
          if (section.variant === "thumb") {
            return (
              <section key={section.id} className="layout-region layout-region-thumb">
                <SectionHeader title={section.title} />
                <ThumbRegion cards={section.data as MobileCardThumbCard[]} />
              </section>
            )
          }
          if (section.variant === "feature-large") {
            return (
              <section key={section.id} className="layout-region layout-region-feature">
                <SectionHeader title={section.title} />
                <FeatureLargeRegion data={section.data as MobileCardFeatureLarge} />
              </section>
            )
          }
          if (section.variant === "hfeature") {
            return (
              <section key={section.id} className="layout-region layout-region-hfeature">
                <SectionHeader title={section.title} />
                <HorizontalFeatureRegion cards={section.data as MobileCardHorizontalFeature[]} />
              </section>
            )
          }
          if (section.variant === "vfeature") {
            return (
              <section key={section.id} className="layout-region layout-region-vfeature">
                <VerticalFeatureRegion cards={section.data as MobileCardVerticalFeature[]} />
              </section>
            )
          }
          return null
        })}
      </section>
    </MobilePhoneShellTemplatePage>
  )
}

export { MobileCardTemplatePage }
