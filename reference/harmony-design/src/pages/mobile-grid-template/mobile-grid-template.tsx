import { useState } from "react"

import { List as ListBlock } from "@/blocks/list"
import { ChipsTab } from "@/components/Navigation/ChipsTab"
import { FloatingTab, type FloatingTabCount, type FloatingTabItem } from "@/components/Navigation/FloatingTab"
import { HMSymbolIcon } from "@/components/HMSymbolIcon"
import { ListPhone } from "@/components/Container/ListPhone"
import { Search } from "@/components/Input/Search"
import { StatusBar } from "@/components/Publis/StatusBar"
import { TitleBar } from "@/components/Navigation/TitleBar/title-bar"
import { ListContainer } from "@/container-components/ListContainer"
import { NavigationContainer } from "@/container-components/NavigationContainer"
import { cn } from "@/lib/utils"

import "./mobile-grid-template.css"

export interface MobileGridHeroCard {
  id: string
  title: string
  bg: string
}

export interface MobileGridChip {
  id: string
  label: string
  count?: string
}

export interface MobileGridGridCard {
  id: string
  coverBg: string
  title: string
  plays?: string
}

export interface MobileGridListItem {
  id: string
  coverBg: string
  title: string
  subtitle: string
}

export type MobileGridTabItem = FloatingTabItem

export interface MobileGridTemplatePageProps {
  className?: string
  title?: string
  searchPlaceholder?: string
  onSearchClick?: () => void
  onActionClick?: () => void
  onChipChange?: (chipId: string) => void
  activeChipId?: string
  heroCards?: MobileGridHeroCard[]
  chips?: MobileGridChip[]
  gridCards?: MobileGridGridCard[]
  gridTitle?: string
  showListRegion?: boolean
  listTitle?: string
  showListDot?: boolean
  listItems?: MobileGridListItem[]
  bottomTabs?: MobileGridTabItem[]
  activeTabKey?: string
  onTabChange?: (key: string) => void
}

const DEFAULT_HERO: MobileGridHeroCard[] = [
  { id: "h1", title: "今日推荐", bg: "linear-gradient(135deg,#5a6cf3,#2c3eb1)" },
  { id: "h2", title: "歌单广场", bg: "linear-gradient(135deg,#9b51e0,#5e2f9c)" },
  { id: "h3", title: "编辑精选", bg: "linear-gradient(135deg,#3ec1a3,#0c8a72)" },
]

const DEFAULT_CHIPS: MobileGridChip[] = [
  { id: "recommend", label: "推荐" },
  { id: "pop", label: "流行" },
  { id: "new", label: "新歌" },
  { id: "rock", label: "摇滚" },
  { id: "indie", label: "独立" },
  { id: "electronic", label: "电子" },
  { id: "jazz", label: "爵士" },
  { id: "classic", label: "古典" },
]

const DEFAULT_GRID: MobileGridGridCard[] = [
  { id: "g1", coverBg: "linear-gradient(135deg,#0a59f7,#0a3180)", title: "夜色电台·晚安", plays: "1.2 万" },
  { id: "g2", coverBg: "linear-gradient(135deg,#9b51e0,#5e2f9c)", title: "城市速写", plays: "8.6 千" },
  { id: "g3", coverBg: "linear-gradient(135deg,#ff6b81,#c41e3a)", title: "热歌雷达 Top 100", plays: "3.4 万" },
  { id: "g4", coverBg: "linear-gradient(135deg,#7a5af8,#3a1f9b)", title: "晨间轻音乐", plays: "5.1 万" },
  { id: "g5", coverBg: "linear-gradient(135deg,#0c8a72,#0c5a4f)", title: "深夜电波", plays: "2.7 万" },
]

const DEFAULT_LIST: MobileGridListItem[] = [
  { id: "l1", coverBg: "linear-gradient(135deg,#fbb5a1,#ed6f21)", title: "夏日漱石", subtitle: "橘子海" },
  { id: "l2", coverBg: "linear-gradient(135deg,#74ebd5,#9face6)", title: "Lover Boy 88", subtitle: "Phum Viphurit" },
  { id: "l3", coverBg: "linear-gradient(135deg,#a1c4fd,#c2e9fb)", title: "Plastic Love", subtitle: "竹内まりや" },
  { id: "l4", coverBg: "linear-gradient(135deg,#ffb86b,#ff7a59)", title: "海底", subtitle: "一枝榴莲" },
]

function buildTabs(): MobileGridTabItem[] {
  return [
  { key: "home", label: "首页", icon: <HMSymbolIcon name="house_fill" size={24} /> },
  { key: "concert", label: "音乐厅", icon: <HMSymbolIcon name="music_fill" size={24} /> },
  { key: "cafe", label: "Cafe 听", icon: <HMSymbolIcon name="discover_fill" size={24} /> },
  { key: "me", label: "我的", icon: <HMSymbolIcon name="person_crop_circle_fill_1" size={24} /> },
  ]
}

function getFloatingTabCount(count: number): FloatingTabCount {
  return String(Math.min(5, Math.max(2, count))) as FloatingTabCount
}

function MobileGridTemplatePage({
  className,
  title = "推荐",
  searchPlaceholder = "搜索歌曲 / 歌单 / 歌手",
  onSearchClick,
  onActionClick,
  onChipChange,
  activeChipId,
  heroCards = DEFAULT_HERO,
  chips = DEFAULT_CHIPS,
  gridCards = DEFAULT_GRID,
  gridTitle = "Hi Raven，为你推荐",
  showListRegion = true,
  listTitle = '喜欢「夏日漱石」的也喜欢',
  showListDot = true,
  listItems = DEFAULT_LIST,
  bottomTabs,
  activeTabKey,
  onTabChange,
}: MobileGridTemplatePageProps) {
  const resolvedTabs = bottomTabs ?? buildTabs()
  const [uncontrolledChip, setUncontrolledChip] = useState(chips[0]?.id ?? "recommend")
  const currentChip = activeChipId ?? uncontrolledChip
  const [uncontrolledTab, setUncontrolledTab] = useState(resolvedTabs[0]?.key ?? "home")
  const currentTab = activeTabKey ?? uncontrolledTab

  return (
    <div className={cn("layout-mobile-grid", className)}>
      <StatusBar className="layout-titlebar__status" />

      <NavigationContainer className="layout-mobile-grid__navigation">
        {/* Fixed top titlebar (z-index: 10) — uses the in-house TitleBar. */}
        <header className="layout-titlebar">
          <div className="layout-titlebar__inner">
            <TitleBar
              category="normal-phone"
              title={title}
              Icon={1}
              actions={[
                {
                  id: "titlebar-action",
                  label: "Action",
                  icon: <HMSymbolIcon name="dot_grid_2x2" size={20} />,
                  onClick: onActionClick,
                },
              ]}
            />
          </div>
        </header>

      {/* Scrollable content. NO z-index / transform / filter / opacity < 1. */}
      <section className="layout-content">
        {/* Search is the first content item and keeps its component-owned surface. */}
        <Search
          className="layout-search-bar"
          placeholder={searchPlaceholder}
          onClick={onSearchClick}
        />

        {/* Hero region: horizontal scroll, 224x280 cards */}
        <section className="layout-region-hero">
          <ListContainer className="layout-hero-scroll">
            {heroCards.map((c) => (
              <div key={c.id} className="pixso-list-item layout-hero-card" style={{ background: c.bg }}>
                <div className="layout-hero-card__copy">{c.title}</div>
              </div>
            ))}
          </ListContainer>
        </section>

        {/* Chipstab: page-level horizontal rail + in-house ChipsTab atoms. */}
        <section className="layout-chipstab">
          <ListContainer className="layout-chipstab__scroll" role="tablist">
            {chips.map((chip) => {
              const active = chip.id === currentChip
              return (
                <ChipsTab
                  key={chip.id}
                  类型="tab"
                  状态={active ? "activated" : "enable"}
                  numValue={chip.count}
                  className={cn("pixso-list-item", "layout-chip", active && "layout-chip--active")}
                  onClick={() => {
                    setUncontrolledChip(chip.id)
                    onChipChange?.(chip.id)
                  }}
                >
                  {chip.label}
                </ChipsTab>
              )
            })}
          </ListContainer>
        </section>

        {/* Grid region */}
        <section className="layout-region-grid">
          <header className="layout-section-header">
            <span className="layout-section-header__title">{gridTitle}</span>
            <button type="button" className="layout-section-header__more" aria-label="More">
              <HMSymbolIcon name="chevron_right" size={16} />
            </button>
          </header>
          <ListContainer className="layout-grid-scroll">
            {gridCards.map((c) => (
              <div key={c.id} className="pixso-list-item layout-grid-card">
                <div className="layout-grid-card__cover" style={{ background: c.coverBg }}>
                  <div className="layout-grid-card__overlay" aria-hidden="true">
                    <HMSymbolIcon name="play_fill" size={14} className="layout-grid-card__play-icon" />
                    {c.plays ? (
                      <span className="layout-grid-card__plays">{c.plays}</span>
                    ) : null}
                  </div>
                </div>
                <div className="layout-grid-card__title">{c.title}</div>
              </div>
            ))}
          </ListContainer>
        </section>

        {showListRegion ? (
          <section className="layout-region-list">
            <header className="layout-section-header layout-section-header--list">
              <span className="layout-section-header__title">{listTitle}</span>
              {showListDot ? <span className="layout-section-header__dot" aria-hidden="true" /> : null}
            </header>
            <ListBlock bodyClassName="layout-list-scroll">
              {listItems.map((it, index) => (
                <div
                  key={it.id}
	                  className={cn(
	                    "pixso-list-item",
	                    "layout-list-item",
	                  )}
	                >
	                  <div className="layout-list-item__cover" style={{ background: it.coverBg }} />
	                  <ListPhone
	                    className="layout-list-item__body"
	                    divider={index < listItems.length - 1}
	                    dividerMode="custom"
	                    dividerInsetStart={0}
	                    dividerInsetEnd={0}
	                    行数="2"
	                    right="Arrow"
	                    rightText=""
	                    title={it.title}
	                    subtitle={it.subtitle}
	                    tabIndex={-1}
	                  />
	                </div>
              ))}
            </ListBlock>
          </section>
        ) : null}
      </section>

      {/* Bottom navigation occupies its own layout row below the scroll area. */}
      <footer className="layout-bottom-bar">
        <div className="layout-bottom-bar__pill">
          <FloatingTab
            items={resolvedTabs}
            activeKey={currentTab}
            onActiveKeyChange={(key) => {
              setUncontrolledTab(key)
              onTabChange?.(key)
            }}
            layout="port"
            数量={getFloatingTabCount(resolvedTabs.length)}
          />
        </div>
      </footer>
      </NavigationContainer>
    </div>
  )
}

export { MobileGridTemplatePage }
