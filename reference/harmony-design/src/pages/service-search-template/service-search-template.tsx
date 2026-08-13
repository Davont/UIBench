import { type ReactNode } from "react"

import { ArtistSearchResultCard } from "@/blocks/artist-search-result-card"
import { MusicSearchCompletedResultList } from "@/blocks/music-search-completed-result-list"
import { MusicSearchHistory } from "@/blocks/music-search-history"
import { MusicSearchingResultList } from "@/blocks/music-searching-result-list"
import { TopSongs } from "@/blocks/top-songs"
import albumCover from "@/assets/pages/mine-zhibanji-page/album.png"
import { FloatingButtonPhone } from "@/components/Controls/FloatingButtonPhone/FloatingButtonPhone"
import { HMSymbolIcon } from "@/components/HMSymbolIcon"
import { FloatingSearchSecondPagePhone } from "@/components/Input/FloatingSearchSecondPagePhone/FloatingSearchSecondPagePhone"
import { FloatingChipsTabPhone } from "@/components/Navigation/FloatingChipsTabPhone"
import { FloatingTab } from "@/components/Navigation/FloatingTab"
import { StatusBar } from "@/components/Publis/StatusBar"
import { ListContainer } from "@/container-components/ListContainer"
import { NavigationContainer } from "@/container-components/NavigationContainer"
import { cn } from "@/lib/utils"

import "./service-search-template.css"

export type ServiceSearchTemplateMode = "pre-search" | "in-search" | "completed-results"

export interface ServiceSearchTemplateCategoryTab {
  key: string
  label: string
}

export interface ServiceSearchTemplatePageProps {
  className?: string
  mode?: ServiceSearchTemplateMode
  searchSlot?: ReactNode
  historySlot?: ReactNode
  rankingRailSlot?: ReactNode
  bottomNavSlot?: ReactNode
  categoryTabsSlot?: ReactNode
  artistCardSlot?: ReactNode
  completedResultListSlot?: ReactNode
  resultActionSlot?: ReactNode
  resultListSlot?: ReactNode
  onlineSearchSlot?: ReactNode
  miniPlayerSlot?: ReactNode
  showStatusBar?: boolean
  showSearchBar?: boolean
  showSearchHistory?: boolean
  showRankingRail?: boolean
  showBottomNav?: boolean
  showCategoryTabs?: boolean
  showArtistCard?: boolean
  showCompletedResultList?: boolean
  showResultAction?: boolean
  showResultList?: boolean
  showOnlineSearch?: boolean
  showMiniPlayer?: boolean
  searchPlaceholder?: string
  categoryTabs?: ServiceSearchTemplateCategoryTab[]
  activeCategoryKey?: string
  historyItems?: Array<{ id?: string; label: string }>
  leftRankingTitle?: string
  rightRankingTitle?: string
  miniPlayerTitle?: string
  miniPlayerSubtitle?: string
  miniPlayerCoverImage?: string
  onBackClick?: () => void
  onSearchClick?: () => void
  onScanClick?: () => void
  onClearSearchClick?: () => void
  onlineSearchText?: string
  resultActionText?: string
}

const DEFAULT_HISTORY_ITEMS = [
  { id: "young", label: "少年" },
  { id: "memory", label: "世间的美好回忆" },
  { id: "coldplay", label: "ColdPlay" },
  { id: "father", label: "以父之名" },
]

const DEFAULT_CATEGORY_TABS: ServiceSearchTemplateCategoryTab[] = [
  { key: "all", label: "综合" },
  { key: "songs", label: "歌曲" },
  { key: "playlists", label: "歌单" },
  { key: "artists", label: "歌手" },
  { key: "albums", label: "专辑" },
]

const DEFAULT_SONGS = [
  { 排名: 1, 歌名: "Silk Sonic", 标签: "hot" as const },
  { 排名: 2, 歌名: "Monday", 标签: "up" as const },
  { 排名: 3, 歌名: "我们会在晚风里遇见", 标签: "new" as const },
  { 排名: 4, 歌名: "起风了" },
  { 排名: 5, 歌名: "Happier than ever", 标签: "up" as const },
  { 排名: 6, 歌名: "这世界那么多人" },
  { 排名: 7, 歌名: "离别开出花离别开出花" },
  { 排名: 8, 歌名: "还是会想你" },
  { 排名: 9, 歌名: "把回忆拼好给你" },
  { 排名: 10, 歌名: "Things You Said" },
  { 排名: 11, 歌名: "还是会想你" },
  { 排名: 12, 歌名: "把回忆拼好给你" },
  { 排名: 13, 歌名: "Things You Said" },
  { 排名: 14, 歌名: "离别开出花离别开出花离别开..." },
  { 排名: 15, 歌名: "还是会想你" },
  { 排名: 16, 歌名: "把回忆拼好给你" },
  { 排名: 17, 歌名: "Things You Said" },
  { 排名: 18, 歌名: "还是会想你" },
  { 排名: 19, 歌名: "把回忆拼好给你" },
  { 排名: 20, 歌名: "Things You Said" },
]

function ServiceSearchTemplatePage({
  className,
  mode = "pre-search",
  searchSlot,
  historySlot,
  rankingRailSlot,
  bottomNavSlot,
  categoryTabsSlot,
  artistCardSlot,
  completedResultListSlot,
  resultActionSlot,
  resultListSlot,
  onlineSearchSlot,
  miniPlayerSlot,
  showStatusBar = true,
  showSearchBar = true,
  showSearchHistory,
  showRankingRail,
  showBottomNav,
  showCategoryTabs,
  showArtistCard,
  showCompletedResultList,
  showResultAction,
  showResultList,
  showOnlineSearch,
  showMiniPlayer,
  searchPlaceholder = "Search",
  categoryTabs = DEFAULT_CATEGORY_TABS,
  activeCategoryKey = "all",
  historyItems = DEFAULT_HISTORY_ITEMS,
  leftRankingTitle = "新歌榜",
  rightRankingTitle = "热歌榜",
  miniPlayerTitle = "Espressos",
  miniPlayerCoverImage = albumCover,
  onBackClick,
  onSearchClick,
  onScanClick,
  onClearSearchClick,
  onlineSearchText = "试试在线搜索",
  resultActionText = "播放全部",
}: ServiceSearchTemplatePageProps) {
  const isPreSearch = mode === "pre-search"
  const isInSearch = mode === "in-search"
  const isCompletedResults = mode === "completed-results"
  const shouldShowSearchHistory = showSearchHistory ?? isPreSearch
  const shouldShowRankingRail = showRankingRail ?? isPreSearch
  const shouldShowBottomNav = showBottomNav ?? isPreSearch
  const shouldShowCategoryTabs = showCategoryTabs ?? isCompletedResults
  const shouldShowArtistCard = showArtistCard ?? isCompletedResults
  const shouldShowCompletedResultList = showCompletedResultList ?? isCompletedResults
  const shouldShowResultAction = showResultAction ?? isInSearch
  const shouldShowResultList = showResultList ?? isInSearch
  const shouldShowOnlineSearch = showOnlineSearch ?? isInSearch
  const shouldShowMiniPlayer = showMiniPlayer ?? (isInSearch || isCompletedResults)
  const resolvedSearchPlaceholder =
    searchPlaceholder === "Search" && isCompletedResults
      ? "APT"
      : searchPlaceholder === "Search" && isInSearch
        ? "周杰伦"
        : searchPlaceholder

  return (
    <div
      className={cn("service-search-template", className)}
      data-mode={mode}
      data-page-type="service-search"
    >
      {showStatusBar ? (
        <StatusBar
          className="service-search-template__status"
          data-slot="statusBarSlot"
          {...{ "Color Mode": "Light" }}
        />
      ) : null}

      <NavigationContainer as="main" className="service-search-template__screen">
        {showSearchBar ? (
          <div className="service-search-template__search-slot" data-slot="searchSlot">
            {searchSlot ?? (
              <FloatingSearchSecondPagePhone
                className="service-search-template__floating-search"
                通透度="标准"
                文本={resolvedSearchPlaceholder}
                显示扫描={isPreSearch}
                显示清除={true}
                显示光标={true}
                onBackClick={onBackClick}
                onClearClick={onClearSearchClick}
                onScanClick={onScanClick}
                onSearchClick={onSearchClick}
                占位={isPreSearch && resolvedSearchPlaceholder === "Search"}
              />
            )}
          </div>
        ) : null}

        {shouldShowSearchHistory ? (
          <section className="service-search-template__history-slot" data-slot="historySlot">
            {historySlot ?? <MusicSearchHistory 历史记录={historyItems} />}
          </section>
        ) : null}

        {shouldShowRankingRail ? (
          <section className="service-search-template__ranking-slot" data-slot="rankingRailSlot">
            {rankingRailSlot ?? (
              <ListContainer className="service-search-template__ranking-rail">
                <TopSongs
                  className="pixso-list-item"
                  标题={leftRankingTitle}
                  歌曲列表={DEFAULT_SONGS}
                />
                <TopSongs
                  className="pixso-list-item"
                  标题={rightRankingTitle}
                  歌曲列表={DEFAULT_SONGS}
                />
              </ListContainer>
            )}
          </section>
        ) : null}

        {shouldShowCategoryTabs ? (
          <section className="service-search-template__category-tabs" data-slot="categoryTabsSlot">
            {categoryTabsSlot ?? (
              <FloatingChipsTabPhone
                className="service-search-template__category-tabs-control"
                items={categoryTabs}
                activeKey={activeCategoryKey}
                类型="tab"
                通透度="标准"
              />
            )}
          </section>
        ) : null}

        {shouldShowArtistCard ? (
          <section className="service-search-template__artist-card-slot" data-slot="artistCardSlot">
            {artistCardSlot ?? <ArtistSearchResultCard />}
          </section>
        ) : null}

        {shouldShowCompletedResultList ? (
          <section
            className="service-search-template__completed-result-list-slot"
            data-slot="completedResultListSlot"
          >
            {completedResultListSlot ?? <MusicSearchCompletedResultList />}
          </section>
        ) : null}

        {shouldShowResultAction ? (
          <section className="service-search-template__result-action" data-slot="resultActionSlot">
            {resultActionSlot ?? <DefaultResultAction label={resultActionText} />}
          </section>
        ) : null}

        {shouldShowResultList ? (
          <section className="service-search-template__result-list-slot" data-slot="resultListSlot">
            {resultListSlot ?? <MusicSearchingResultList />}
          </section>
        ) : null}

        {shouldShowOnlineSearch ? (
          <section className="service-search-template__online-search" data-slot="onlineSearchSlot">
            {onlineSearchSlot ?? (
              <FloatingButtonPhone
                className="service-search-template__online-search-button"
                尺寸="Medium"
                类型="Normal"
                状态="Enabled"
                通透度="标准"
              >
                {onlineSearchText}
              </FloatingButtonPhone>
            )}
          </section>
        ) : null}

        {shouldShowMiniPlayer ? (
          <footer className="service-search-template__mini-player" data-slot="miniPlayerSlot">
            {miniPlayerSlot ?? (
              <FloatingTab
                className="service-search-template__floating-mini-tab"
                数量="1+bar"
                通透度="标准"
                歌曲标题={miniPlayerTitle}
                封面={miniPlayerCoverImage}
              />
            )}
          </footer>
        ) : null}

        {shouldShowBottomNav ? (
          <footer className="service-search-template__bottom-nav" data-slot="bottomNavSlot">
            {bottomNavSlot ?? (
              <FloatingTab
                className="service-search-template__bottom-tab"
                数量="1+bar"
                通透度="标准"
                歌曲标题={miniPlayerTitle}
                封面={miniPlayerCoverImage}
              />
            )}
          </footer>
        ) : null}
      </NavigationContainer>
    </div>
  )
}

function DefaultResultAction({ label }: { label: string }) {
  return (
    <div className="service-search-template__result-action-inner">
      <span className="service-search-template__result-play" aria-hidden="true" />
      <span className="service-search-template__result-label">{label}</span>
      <HMSymbolIcon
        className="service-search-template__result-list-icon"
        name="list_checkmask"
        size={24}
        aria-hidden="true"
      />
    </div>
  )
}

export { ServiceSearchTemplatePage }
