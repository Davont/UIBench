import { useState } from "react"

import { List as ListBlock } from "@/blocks/list"
import type { BottomTabItem } from "@/components/Navigation/BottomTab/bottom-tab"
import { HMSymbolIcon } from "@/components/HMSymbolIcon"
import { ListPhone } from "@/components/Container/ListPhone"
import { cn } from "@/lib/utils"
import { MobilePhoneShellTemplatePage } from "@/pages/mobile-phone-shell-template"

import "./mobile-list-template.css"

export interface MobileListEntryItem {
  id: string
  iconBg: string
  iconColor?: string
  title: string
  subtitle?: string
  value?: string
  /** When `true`, render as a jump row (chevron only, no value text). */
  jumpOnly?: boolean
  /** When `true`, render the value text in accent color (font_emphasize). */
  accentValue?: boolean
}

export interface MobileListEntryGroup {
  id: string
  items: MobileListEntryItem[]
}

export interface MobileListHeaderCardProps {
  avatarInitial?: string
  username: string
  meta?: string
  onClick?: () => void
}

export interface MobileListBottomVariant {
  /** Choose between `aibottombar` (independent page) or `bottomtab` (multi-tab home). */
  variant: "aibottombar" | "bottomtab"
  activeTabKey?: string
  tabs?: MobileListBottomTabItem[]
}

export type MobileListTabItem = BottomTabItem
export type MobileListBottomTabItem = BottomTabItem

export interface MobileListTemplatePageProps {
  className?: string
  title?: string
  showBack?: boolean
  onBack?: () => void
  onActionClick?: () => void
  headerCard?: MobileListHeaderCardProps
  groups?: MobileListEntryGroup[]
  bottom?: MobileListBottomVariant
  onEntryClick?: (groupId: string, itemId: string) => void
  onTabChange?: (key: string) => void
}

function buildTabs(): MobileListBottomTabItem[] {
  return [
  { key: "home", label: "首页", icon: <HMSymbolIcon name="house_fill" size={24} /> },
  { key: "feed", label: "动态", icon: <HMSymbolIcon name="discover_fill" size={24} /> },
  { key: "shop", label: "会员购", icon: <HMSymbolIcon name="picture_fill" size={24} /> },
  { key: "me", label: "我的", icon: <HMSymbolIcon name="person_crop_circle_fill_1" size={24} /> },
  ]
}

const DEFAULT_GROUPS: MobileListEntryGroup[] = [
  {
    id: "g-orders",
    items: [
      { id: "i-orders", iconBg: "rgba(10, 89, 247, 0.12)", title: "我的订单", value: "3 个进行中" },
      { id: "i-coupons", iconBg: "rgba(255, 107, 129, 0.16)", title: "优惠券", value: "5 张可用" },
      { id: "i-points", iconBg: "rgba(155, 81, 224, 0.16)", title: "积分", value: "1,280" },
    ],
  },
  {
    id: "g-services",
    items: [
      { id: "i-addr", iconBg: "rgba(62, 193, 163, 0.16)", title: "收货地址" },
      { id: "i-pay", iconBg: "rgba(10, 89, 247, 0.12)", title: "支付管理" },
      { id: "i-fav", iconBg: "rgba(245, 165, 36, 0.18)", title: "我的收藏", value: "24" },
    ],
  },
  {
    id: "g-about",
    items: [
      { id: "i-help", iconBg: "rgba(0, 0, 0, 0.05)", title: "帮助中心" },
      { id: "i-feedback", iconBg: "rgba(0, 0, 0, 0.05)", title: "意见反馈" },
      { id: "i-about", iconBg: "rgba(0, 0, 0, 0.05)", title: "关于", value: "v 1.0.0" },
    ],
  },
]

const DEFAULT_BOTTOM: MobileListBottomVariant = { variant: "bottomtab" }

function EntryItem({
  item,
  showDivider,
  onClick,
}: {
  item: MobileListEntryItem
  showDivider: boolean
  onClick?: () => void
}) {
  const showRightText = !item.jumpOnly && item.value !== undefined
  return (
    <div
      role="button"
      tabIndex={0}
      className="layout-list-row"
      onClick={onClick}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault()
          onClick?.()
        }
      }}
    >
      <div className="layout-list-row__icon" style={{ background: item.iconBg, color: item.iconColor ?? "inherit" }}>
        <HMSymbolIcon name="person_crop_circle_fill_1" size={20} />
      </div>
      <ListPhone
        className={cn("layout-list-row__content", item.accentValue && "layout-list-row__content--accent")}
        divider={showDivider}
        dividerMode="custom"
        dividerInsetStart={0}
        dividerInsetEnd={0}
        行数={item.subtitle ? "2" : "1"}
        right="Arrow"
        rightText={showRightText ? item.value : ""}
        title={item.title}
        subtitle={item.subtitle}
        tabIndex={-1}
      />
    </div>
  )
}

function MobileListTemplatePage({
  className,
  title = "我的",
  showBack = false,
  onBack,
  onActionClick,
  headerCard,
  groups = DEFAULT_GROUPS,
  bottom = DEFAULT_BOTTOM,
  onEntryClick,
  onTabChange,
}: MobileListTemplatePageProps) {
  const tabs = bottom.tabs ?? buildTabs()
  const [uncontrolledTab, setUncontrolledTab] = useState(bottom.activeTabKey ?? "me")
  const currentTab = bottom.activeTabKey ?? uncontrolledTab
  const showFloatingTab = bottom.variant === "bottomtab"

  return (
    <MobilePhoneShellTemplatePage
      className={className}
      mode={showFloatingTab ? "app-home" : "secondary"}
      headerVariant={showBack ? "secondary" : "normal"}
      title={title}
      leadingAction={showBack ? { kind: "back", label: "Back", onClick: onBack } : null}
      headerActions={
        onActionClick
          ? [
              {
                id: "titlebar-action",
                label: "Action",
                icon: <HMSymbolIcon name="square_dashed" size={20} />,
                onClick: onActionClick,
              },
            ]
          : []
      }
      tabs={tabs}
      activeTabKey={currentTab}
      onActiveTabChange={(key) => {
        setUncontrolledTab(key)
        onTabChange?.(key)
      }}
      showFloatingTab={showFloatingTab}
    >
      <section className="layout-mobile-list">
        {headerCard ? (
          <section className="layout-card layout-card-header">
            <button
              type="button"
              className="layout-card-header__inner"
              onClick={headerCard.onClick}
            >
              <div className="layout-card-header__avatar">
                {headerCard.avatarInitial ?? "U"}
              </div>
              <div className="layout-card-header__body">
                <div className="layout-card-header__name">{headerCard.username}</div>
                {headerCard.meta ? (
                  <div className="layout-card-header__meta">{headerCard.meta}</div>
                ) : null}
              </div>
              <HMSymbolIcon name="chevron_right" size={14} className="layout-card-header__chevron" />
            </button>
          </section>
        ) : null}

        {groups.map((group) => (
          <ListBlock
            key={group.id}
            bodyClassName="layout-card-group-entry"
          >
            {group.items.map((item, index) => (
              <div key={item.id} className="pixso-list-item layout-list-card-item">
                <EntryItem
                  item={item}
                  showDivider={index < group.items.length - 1}
                  onClick={() => onEntryClick?.(group.id, item.id)}
                />
              </div>
            ))}
          </ListBlock>
        ))}
      </section>
    </MobilePhoneShellTemplatePage>
  )
}

export { MobileListTemplatePage }
