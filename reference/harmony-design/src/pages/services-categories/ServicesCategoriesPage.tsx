import { HMSymbolIcon } from "@/components/HMSymbolIcon"
import { Aibottombar } from "@/components/Publis/Aibottombar"
import { StatusBar } from "@/components/Publis/StatusBar"
import { GridContainer } from "@/container-components/GridContainer"
import { ListContainer } from "@/container-components/ListContainer"
import { NavigationContainer } from "@/container-components/NavigationContainer"
import { cn } from "@/lib/utils"

import cover1 from "./assets/蒙版-1.png"
import cover2 from "./assets/蒙版-2.png"
import cover3 from "./assets/蒙版-3.png"
import cover4 from "./assets/蒙版-4.png"
import cover5 from "./assets/蒙版-5.png"
import cover6 from "./assets/蒙版-6.png"
import cover7 from "./assets/蒙版-7.png"
import cover8 from "./assets/蒙版-8.png"
import cover9 from "./assets/蒙版-9.png"

import "./services-categories.css"

/* ─── Types ─── */

export interface FilterRow {
  id: string
  label: string
  options: FilterOption[]
}

export interface FilterOption {
  id: string
  label: string
  active?: boolean
}

export interface MovieItem {
  id: string
  title: string
  rating: string
  vip?: boolean
  cover: string
}

export interface ServicesCategoriesPageProps {
  className?: string
  /** 筛选行数据 */
  filters?: FilterRow[]
  /** 电影列表 */
  movies?: MovieItem[]
  /** 返回按钮点击 */
  onBack?: () => void
  /** 搜索按钮点击 */
  onSearch?: () => void
  /** 筛选选项点击 */
  onFilterChange?: (rowId: string, optionId: string) => void
}

/* ─── Default Data ─── */

const defaultFilters: FilterRow[] = [
  {
    id: "rating",
    label: "评分",
    options: [
      { id: "rating", label: "评分", active: true },
      { id: "newest", label: "最新" },
      { id: "hottest", label: "最热" },
      { id: "latest-release", label: "最新上架" },
      { id: "highest-rated", label: "最高评分" },
      { id: "classic", label: "经典" },
      { id: "popular", label: "大众好评" },
      { id: "niche", label: "小众精选" },
      { id: "award", label: "获奖影片" },
    ],
  },
  {
    id: "year",
    label: "年份",
    options: [
      { id: "year", label: "年份", active: true },
      { id: "2025", label: "2025" },
      { id: "2024", label: "2024" },
      { id: "2023", label: "2023" },
      { id: "2022", label: "2022" },
      { id: "2021", label: "2021" },
      { id: "2020", label: "2020" },
      { id: "older", label: "更早" },
      { id: "all-years", label: "全部年份" },
    ],
  },
  {
    id: "region",
    label: "地区",
    options: [
      { id: "region", label: "地区", active: true },
      { id: "china-mainland", label: "中国大陆" },
      { id: "china-hk-tw", label: "中国港台" },
      { id: "western", label: "欧美" },
      { id: "korea", label: "韩国" },
      { id: "japan", label: "日本" },
      { id: "india", label: "印度" },
      { id: "thailand", label: "泰国" },
      { id: "other", label: "其他" },
    ],
  },
  {
    id: "member",
    label: "会员",
    options: [
      { id: "member", label: "会员", active: true },
      { id: "free", label: "免费" },
      { id: "vip-exclusive", label: "VIP 专享" },
      { id: "trial", label: "试看" },
      { id: "purchase", label: "付费购买" },
      { id: "rental", label: "租赁" },
      { id: "package", label: "套餐包含" },
    ],
  },
  {
    id: "genre",
    label: "类型",
    options: [
      { id: "genre", label: "类型", active: true },
      { id: "comedy", label: "喜剧" },
      { id: "romance", label: "爱情" },
      { id: "drama", label: "剧情" },
      { id: "action", label: "动作" },
      { id: "scifi", label: "科幻" },
      { id: "animation", label: "动画" },
      { id: "thriller", label: "悬疑" },
      { id: "documentary", label: "纪录片" },
    ],
  },
  {
    id: "platform",
    label: "华为视频",
    options: [
      { id: "huawei", label: "华为视频", active: true },
      { id: "tencent", label: "腾讯" },
      { id: "youku", label: "优酷" },
      { id: "mango", label: "芒果TV" },
      { id: "iqiyi", label: "爱奇艺" },
      { id: "bilibili", label: "哔哩哔哩" },
      { id: "sohu", label: "搜狐" },
      { id: "letv", label: "乐视" },
      { id: "pptv", label: "PPTV" },
    ],
  },
]

const defaultMovies: MovieItem[] = [
  { id: "1", title: "夏日友晴天", rating: "8.7", vip: true, cover: cover1 },
  { id: "2", title: "勇敢传说", rating: "8.7", vip: true, cover: cover2 },
  { id: "3", title: "飞屋环游记", rating: "8.7", vip: true, cover: cover3 },
  { id: "4", title: "寻梦环游记", rating: "8.7", vip: true, cover: cover4 },
  { id: "5", title: "心灵奇旅", rating: "8.7", vip: true, cover: cover5 },
  { id: "6", title: "巴斯光年", rating: "8.7", vip: true, cover: cover6 },
  { id: "7", title: "玩具总动员", rating: "8.7", vip: true, cover: cover7 },
  { id: "8", title: "超人总动员", rating: "8.7", vip: true, cover: cover8 },
  { id: "9", title: "怪兽电力公司", rating: "8.7", vip: true, cover: cover9 },
]

/* ─── Sub-components ─── */

function FilterChip({
  option,
  onClick,
  className,
}: {
  option: FilterOption
  onClick?: () => void
  className?: string
}) {
  return (
    <button
      type="button"
      className={cn(
        "services-categories__chip",
        option.active ? "services-categories__chip--active" : "services-categories__chip--inactive",
        className,
      )}
      onClick={onClick}
    >
      {option.label}
    </button>
  )
}

function MovieCard({ movie, className }: { movie: MovieItem; className?: string }) {
  return (
    <div className={cn("services-categories__movie-card", className)}>
      <div className="services-categories__movie-poster">
        <img
          className="services-categories__movie-poster-img"
          src={movie.cover}
          alt={movie.title}
        />
        {movie.vip && <span className="services-categories__movie-vip">VIP</span>}
        <div className="services-categories__movie-rating">
          <span className="services-categories__movie-rating-text">{movie.rating}</span>
        </div>
      </div>
      <span className="services-categories__movie-title">{movie.title}</span>
    </div>
  )
}

/* ─── Main Component ─── */

export function ServicesCategoriesPage({
  className,
  filters = defaultFilters,
  movies = defaultMovies,
  onBack,
  onSearch,
  onFilterChange,
}: ServicesCategoriesPageProps) {
  return (
    <div className={cn("services-categories-page", className)}>
      {/* Top Status Bar */}
      <StatusBar {...{ "Color Mode": "Dark" }} />

      <NavigationContainer className="services-categories__navigation">
      {/* Title Bar */}
      <div className="services-categories__titlebar">
        <button
          type="button"
          className="services-categories__titlebar-back"
          onClick={onBack}
          aria-label="返回"
        >
          <HMSymbolIcon name="chevron_left" size={22} />
        </button>
        <span className="services-categories__titlebar-title">全部</span>
        <button
          type="button"
          className="services-categories__titlebar-search"
          onClick={onSearch}
          aria-label="搜索"
        >
          <HMSymbolIcon name="magnifyingglass" size={20} />
        </button>
      </div>

      <div className="services-categories__content">
        {/* Filter Section */}
        <ListContainer className="services-categories__filters">
          {filters.map((row) => (
            <div className="pixso-list-item" key={row.id}>
              <ListContainer className="services-categories__filter-row">
                {row.options.map((option) => (
                  <FilterChip
                    className="pixso-list-item"
                    key={option.id}
                    option={option}
                    onClick={() => onFilterChange?.(row.id, option.id)}
                  />
                ))}
              </ListContainer>
            </div>
          ))}
        </ListContainer>

        {/* Movie Grid */}
        <GridContainer className="services-categories__grid">
          {movies.map((movie) => (
            <MovieCard className="pixso-grid-item" key={movie.id} movie={movie} />
          ))}
        </GridContainer>
      </div>
      </NavigationContainer>

      {/* Bottom Bar */}
      <Aibottombar {...{ "Color Mode": "Dark" }} />
    </div>
  )
}

export default ServicesCategoriesPage
