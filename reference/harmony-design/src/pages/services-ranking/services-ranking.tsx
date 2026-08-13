/* eslint-disable react-refresh/only-export-components */
import { useState, useCallback } from "react"
import { cn } from "@/lib/utils"

import { Aibottombar } from "@/components/Publis/Aibottombar/Aibottombar"
import { RankingTopbanner } from "@/blocks/ranking-topbanner/ranking-topbanner"
import { RankingChipsTabPhone } from "@/blocks/ranking-chipstab-phone/ranking-chipstab-phone"
import { MainChart03 } from "@/blocks/ranking-list/ranking-list"
import type { MainChart03Item } from "@/blocks/ranking-list/ranking-list"
import type { ChipsTabPhoneItem } from "@/components/Navigation/ChipsTab"
import { NavigationContainer } from "@/container-components/NavigationContainer"

import img1Chaidan from "@/blocks/ranking-list/images/1-chaidan.png"
import img2Spiderman from "@/blocks/ranking-list/images/2-spiderman.png"
import img3Manchester from "@/blocks/ranking-list/images/3-manchester.png"
import img4Wonderwoman from "@/blocks/ranking-list/images/4-wonderwoman.png"
import img5InvisibleGuest from "@/blocks/ranking-list/images/5-invisible-guest.png"
import img6Interstellar from "@/blocks/ranking-list/images/6-interstellar.png"
import img7Luca from "@/blocks/ranking-list/images/7-luca.png"
import img8Soul from "@/blocks/ranking-list/images/8-soul.png"
import img9Oblivion from "@/blocks/ranking-list/images/9-oblivion.png"
import img10Brave from "@/blocks/ranking-list/images/10-brave.png"
import img11Totoro from "@/blocks/ranking-list/images/11-totoro.png"
import img12Jiangziya from "@/blocks/ranking-list/images/12-jiangziya.png"
import illustrationTopBanner from "./illustration-top-banner.png"

import "./services-ranking.css"

/* ─── Types ─── */

export interface ServicesRankingProps {
  /** 页面标题 (TitleBar 显示文字, DSL: "排行榜") */
  页面标题?: string
  /** 头图横幅 URL (位于 TitleBar 下方, 作为 header 区域背景)
      Pixso: #illustration_top banner-long */
  头图?: string
  /** 插图主标题 (Pixso 36:37056, 30px/900/gold, 默认"综合排行榜") */
  主标题?: string
  /** 插图描述 (Pixso 36:37057, 12px/400/gold×0.6, 默认"-根据榜单实时热度得出排名-") */
  描述?: string
  /** @deprecated 使用 主标题 + 描述 替代 */
  插图标题?: string
  /** ChipsTab 页签数据 (默认: 综合榜/电视剧榜/电影榜/综艺榜) */
  chipsTabItems?: ChipsTabPhoneItem[]
  /** 当前激活的页签 key (受控) */
  chipsTabActiveKey?: string
  /** 默认激活的页签 key */
  chipsTabDefaultActiveKey?: string
  /** 排行榜列表数据 */
  rankingItems?: MainChart03Item[]
  /** 页签切换回调 */
  on页签切换?: (key: string, item: ChipsTabPhoneItem) => void
  /** 标题栏返回按钮回调 */
  on返回?: () => void
  /** 标题栏搜索按钮回调 */
  on搜索?: () => void
  /** 自定义类名 */
  className?: string
}

/* ─── Default ChipsTab Items (Pixso DSL: 59:169 design_to_code)
   4 tabs: 综合榜(activated) / 电视剧榜 / 电影榜 / 综艺榜 ─── */

export const DEFAULT_CHIPS_TABS: ChipsTabPhoneItem[] = [
  { key: "all", label: "综合榜" },
  { key: "tv", label: "电视剧榜" },
  { key: "movie", label: "电影榜" },
  { key: "variety", label: "综艺榜" },
]

/* ─── Default Ranking Items (Pixso DSL: 45:1 主榜03)
   12 items — 与 DSL 36:37062 实例数据一致
   ═══════════════════════════════════════════════════ */

export const DEFAULT_RANKING_ITEMS: MainChart03Item[] = [
  { 排名: 1, 封面图: img1Chaidan, 标题: "拆弹专家2", 演员: "梁朝伟 / 刘德华 / 古天乐", 年份类型: "2017 · 科幻 · 冒险" },
  { 排名: 2, 封面图: img2Spiderman, 标题: "蜘蛛侠：英雄归来", 演员: "汤姆·赫兰德 / 赞达亚", 年份类型: "2017 · 科幻 · 冒险" },
  { 排名: 3, 封面图: img3Manchester, 标题: "海边的曼彻斯特", 演员: "肯尼思·洛纳根 / 卡西·阿弗", 年份类型: "2017 · 科幻 · 冒险" },
  { 排名: 4, 封面图: img4Wonderwoman, 标题: "神奇女侠", 演员: "派蒂·杰金斯 / 盖尔·加朵克", 年份类型: "2017 · 科幻 · 冒险" },
  { 排名: 5, 封面图: img5InvisibleGuest, 标题: "看不见的客人", 演员: "马里奥·卡萨斯 / 阿娜·瓦格纳", 年份类型: "2016 · 悬疑 · 剧情" },
  { 排名: 6, 封面图: img6Interstellar, 标题: "星际穿越", 演员: "马修·麦康纳 / 安妮·海瑟薇", 年份类型: "2014 · 科幻 · 悬疑" },
  { 排名: 7, 封面图: img7Luca, 标题: "夏日友晴天", 演员: "雅各布·特伦布莱 / 杰克·迪伦·格雷泽", 年份类型: "2021 · 喜剧 · 动画" },
  { 排名: 8, 封面图: img8Soul, 标题: "心灵奇旅", 演员: "杰米·福克斯 / 蒂娜·菲", 年份类型: "2020 · 音乐 · 奇幻" },
  { 排名: 9, 封面图: img9Oblivion, 标题: "遗落战境", 演员: "汤姆·克鲁斯 / 摩根·弗里曼", 年份类型: "2013 · 科幻 · 动作" },
  { 排名: 10, 封面图: img10Brave, 标题: "勇敢传说", 演员: "凯莉·麦克唐纳 / 艾玛·汤普森", 年份类型: "2012 · 奇幻 · 动画" },
  { 排名: 11, 封面图: img11Totoro, 标题: "龙猫", 演员: "日高范子 / 坂本千夏", 年份类型: "1988 · 奇幻 · 动画" },
  { 排名: 12, 封面图: img12Jiangziya, 标题: "姜子牙", 演员: "郑希 / 杨凝", 年份类型: "2020 · 剧情 · 动画" },
]

/* ─── Main Component ───
   榜单-宫格式列表 — Pixso 1:1 还原 (item-id=36:37008)
   DSL 真值 (get_node_dsl 36:37008 + 59:497):
   - 根: FRAME "排行榜" (36:37008) 360×792, fill rgba(24,24,26,1) #18181A
   - 头部容器 (59:497): 360×237, white bg
     - StatusBar: top=0
     - TitleBar-secondary page-Phone: 328×56, top=36, left=16
     - #illustration_title: 插图标题文字
     - #illustration_top banner-long: 背景图
   - 列表: FRAME "列表" (36:37062) 328×1440, left=16, top=294
   - 底部: Aibottombar ColorModeDark 360×28, top=764
   ═══════════════════════════════════════════════════ */

export function ServicesRanking({
  页面标题 = "排行榜",
  头图,
  主标题 = "综合排行榜",
  描述 = "-根据榜单实时热度得出排名-",
  插图标题,
  chipsTabItems = DEFAULT_CHIPS_TABS,
  chipsTabActiveKey,
  chipsTabDefaultActiveKey = "all",
  rankingItems = DEFAULT_RANKING_ITEMS,
  on页签切换,
  on返回,
  on搜索,
  className,
}: ServicesRankingProps) {
  // backward compat: 插图标题 降级为 主标题
  const displayTitle = 主标题 || 插图标题 || "综合排行榜"
  const [internalTabKey, setInternalTabKey] = useState<string>(
    chipsTabDefaultActiveKey
  )
  const currentTabKey = chipsTabActiveKey ?? internalTabKey

  const handleTabChange = useCallback(
    (key: string, item: ChipsTabPhoneItem) => {
      if (chipsTabActiveKey === undefined) {
        setInternalTabKey(key)
      }
      on页签切换?.(key, item)
    },
    [chipsTabActiveKey, on页签切换]
  )

  return (
    <div className={cn("srv-container", className)}>
      <NavigationContainer className="srv-navigation">
        {/* 头部 — RankingTopbanner 组件
            Pixso 36:37009 #illustration_top banner-long (360×237)
            头图背景 + StatusBar (Dark) + TitleBar (返回/搜索) + 麦穗金色插图 */}
        <RankingTopbanner
          页面标题={页面标题}
          头图={头图 || illustrationTopBanner}
          主标题={displayTitle}
          描述={描述}
          on返回={on返回}
          on右侧按钮点击={on搜索}
        />

        {/* 内容面板 — Pixso 36:37058 "bg" (360×578, top=214, #18181A, 圆角24/24/0/0)
            包含 ChipsTab + 列表，顶部圆角与 header 底部重叠 */}
        <div className="srv-content-panel">
          {/* ChipsTab 标签栏 — RankingChipsTabPhone (Pixso 36:37061, top=226, 360×64) */}
          <RankingChipsTabPhone
            className="srv-tab-section"
            chipsTabItems={chipsTabItems}
            chipsTabActiveKey={currentTabKey}
            chipsTabDefaultActiveKey={chipsTabDefaultActiveKey}
            onChipsTabChange={handleTabChange}
          />

          {/* 排名列表 — MainChart03 (Pixso 36:37062, top=294, left=16, 328×auto) */}
          <MainChart03 className="srv-list-section" items={rankingItems} />
        </div>
      </NavigationContainer>

      {/* 底部导航 — Aibottombar (Pixso 36:37075, top=764, 360×28, ColorModeDark) */}
      <div className="srv-bottom-bar">
        <Aibottombar {...{ "Color Mode": "Dark" }} />
      </div>
    </div>
  )
}

export default ServicesRanking
