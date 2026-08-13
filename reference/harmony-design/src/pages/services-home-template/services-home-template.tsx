import { type ReactNode, useState } from "react"

import { NewBookPreview } from "@/blocks/new-book-preview"
import { RecommendedNewBooks } from "@/blocks/recommended-new-books"
import { TopBanner } from "@/blocks/top-banner"
import { FloatingTab, type FloatingTabItem } from "@/components/Navigation/FloatingTab"
import { HMSymbolIcon } from "@/components/HMSymbolIcon"
import { StatusBar } from "@/components/Publis/StatusBar"
import { TitleBar } from "@/components/Navigation/TitleBar"
import { ListContainer } from "@/container-components/ListContainer"
import { NavigationContainer } from "@/container-components/NavigationContainer"
import { cn } from "@/lib/utils"

import "./services-home-template.css"

export interface ServicesHomeCategory {
  id: string
  label: string
  icon?: ReactNode
}

export interface ServicesHomeTemplatePageProps {
  className?: string
  pageTitle?: string
  heroSlot?: ReactNode
  categoryTabsSlot?: ReactNode
  newBookPreviewSlot?: ReactNode
  recommendedNewBooksSlot?: ReactNode
  bottomNavSlot?: ReactNode
  showStatusBar?: boolean
  showPageHeader?: boolean
  showSearchAction?: boolean
  showHero?: boolean
  showCategoryTabs?: boolean
  showNewBookPreview?: boolean
  showRecommendedNewBooks?: boolean
  showBottomNav?: boolean
  categories?: ServicesHomeCategory[]
  activeCategoryId?: string
  onCategoryChange?: (categoryId: string) => void
  onSearchClick?: () => void
  bottomTabs?: FloatingTabItem[]
  activeTabKey?: string
  onTabChange?: (key: string) => void
}

function buildCategories(): ServicesHomeCategory[] {
  return [
  { id: "picks", label: "精选", icon: <HMSymbolIcon name="star_fill" size={16} /> },
  { id: "novel", label: "小说", icon: <HMSymbolIcon name="book_open_fill" size={16} /> },
  { id: "business", label: "商业", icon: <HMSymbolIcon name="briefcase" size={16} /> },
  { id: "history", label: "历史", icon: <HMSymbolIcon name="clock" size={16} /> },
  ]
}

function buildTabs(): FloatingTabItem[] {
  return [
  { key: "shelf", label: "书架", icon: <HMSymbolIcon name="book_pages_fill_1" size={24} /> },
  { key: "store", label: "书城", icon: <HMSymbolIcon name="book_open_fill" size={24} /> },
  { key: "featured", label: "精品书", icon: <HMSymbolIcon name="star_fill" size={24} /> },
  { key: "me", label: "我的", icon: <HMSymbolIcon name="person_crop_circle_fill_1" size={24} /> },
  ]
}

function ServicesHomeTemplatePage({
  className,
  pageTitle = "首页",
  heroSlot,
  categoryTabsSlot,
  newBookPreviewSlot,
  recommendedNewBooksSlot,
  bottomNavSlot,
  showStatusBar = true,
  showPageHeader = true,
  showSearchAction = true,
  showHero = true,
  showCategoryTabs = true,
  showNewBookPreview = true,
  showRecommendedNewBooks = true,
  showBottomNav = true,
  categories,
  activeCategoryId,
  onCategoryChange,
  onSearchClick,
  bottomTabs,
  activeTabKey,
  onTabChange,
}: ServicesHomeTemplatePageProps) {
  const resolvedTabs = bottomTabs ?? buildTabs()
  const resolvedCategories = categories ?? buildCategories()
  const [uncontrolledCategoryId, setUncontrolledCategoryId] = useState(
    resolvedCategories[0]?.id ?? "picks",
  )
  const currentCategoryId = activeCategoryId ?? uncontrolledCategoryId
  const [uncontrolledTabKey, setUncontrolledTabKey] = useState("store")
  const currentTabKey = activeTabKey ?? uncontrolledTabKey

  return (
    <div className={cn("services-home-template", className)}>
      {showStatusBar ? (
        <StatusBar
          className="services-home-template__status"
          {...{ "Color Mode": "Dark" }}
        />
      ) : null}

      <NavigationContainer as="main" className="services-home-template__screen">
        <div className="services-home-template__overlay">
          {showPageHeader ? (
            <TitleBar
              category="normal-phone"
              className="services-home-template__titlebar"
              headingLevel={1}
              title={pageTitle}
              actions={
                showSearchAction
                  ? [
                      {
                        id: "search",
                        label: "搜索",
                        icon: <HMSymbolIcon name="magnifyingglass" size={28} />,
                        onClick: onSearchClick,
                      },
                    ]
                  : []
              }
            />
          ) : null}
        </div>

        <section className="services-home-template__content">
          {showHero ? (
            <section className="services-home-template__hero-slot" data-slot="heroSlot">
              {heroSlot ?? <TopBanner />}
            </section>
          ) : null}

          {showCategoryTabs ? (
            <div className="services-home-template__category-slot" data-slot="categoryTabsSlot">
              {categoryTabsSlot ?? (
                <ListContainer as="nav" className="services-home-template__category-scroll" role="tablist">
                  {resolvedCategories.map((category) => {
                    const isActive = category.id === currentCategoryId

                    return (
                      <button
                        key={category.id}
                        type="button"
                        role="tab"
                        aria-selected={isActive}
                        className="pixso-list-item services-home-template__category"
                        data-active={isActive}
                        onClick={() => {
                          setUncontrolledCategoryId(category.id)
                          onCategoryChange?.(category.id)
                        }}
                      >
                        <span aria-hidden="true">{category.icon}</span>
                        {category.label}
                      </button>
                    )
                  })}
                </ListContainer>
              )}
            </div>
          ) : null}

          {showNewBookPreview ? (
            <section
              className="services-home-template__new-book-slot"
              data-slot="newBookPreviewSlot"
            >
              {newBookPreviewSlot ?? <NewBookPreview />}
            </section>
          ) : null}

          {showRecommendedNewBooks ? (
            <section
              className="services-home-template__recommended-slot"
              data-slot="recommendedNewBooksSlot"
            >
              {recommendedNewBooksSlot ?? <RecommendedNewBooks />}
            </section>
          ) : null}
        </section>

        {showBottomNav ? (
          <footer className="services-home-template__bottom-nav" data-slot="bottomNavSlot">
            {bottomNavSlot ?? (
              <div className="services-home-template__bottom-nav-pill">
                <FloatingTab
                  items={resolvedTabs}
                  activeKey={currentTabKey}
                  onActiveKeyChange={(key) => {
                    setUncontrolledTabKey(key)
                    onTabChange?.(key)
                  }}
                  layout="port"
                  数量="4"
                  通透度="标准"
                />
              </div>
            )}
          </footer>
        ) : null}
      </NavigationContainer>
    </div>
  )
}

export { ServicesHomeTemplatePage }
