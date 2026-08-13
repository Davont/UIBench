import { useState } from "react"
import type { ReactNode } from "react"

import { List as ListBlock } from "@/blocks/list"
import type { HMSymbolIconName } from "@/components/HMSymbolIcon"
import { ListContainer } from "@/container-components/ListContainer"
import { cn } from "@/lib/utils"
import { MobilePhoneShellTemplatePage } from "@/pages/mobile-phone-shell-template"

import "./settings-page-template.css"

interface SettingRowBase {
  id: string
  title: string
  /** Standard 24dp HM Symbol shown by ListPhone. */
  iconName?: HMSymbolIconName
  /** Custom visual slot for exceptional rows such as avatars or image tiles. */
  icon?: ReactNode
  /** When `true`, the row is the last item of its group; no bottom divider. */
  isLast?: boolean
}

export type SettingRow =
  | (SettingRowBase & {
      kind: "switch"
      /** Initial value for switch rows. */
      defaultChecked: boolean
      value?: never
    })
  | (SettingRowBase & {
      kind: "value" | "accentValue"
      /** Right-aligned value text. */
      value: string
      defaultChecked?: never
    })
  | (SettingRowBase & {
      kind: "link"
      /** Link rows are chevron-only and cannot carry a value. */
      value?: never
      defaultChecked?: never
    })

export type SettingRowKind = SettingRow["kind"]

export interface SettingGroup {
  id: string
  rows: SettingRow[]
}

export interface SettingsPageTemplatePageProps {
  className?: string
  title?: string
  showBack?: boolean
  onBack?: () => void
  onRowClick?: (groupId: string, rowId: string) => void
  onSwitchChange?: (groupId: string, rowId: string, value: boolean) => void
  groups?: SettingGroup[]
}

function buildGroups(): SettingGroup[] {
  return [
  {
    id: "network",
    rows: [
      {
        id: "wlan",
        title: "WLAN",
        iconName: "wifi",
        kind: "switch",
        defaultChecked: true,
      },
      {
        id: "bluetooth",
        title: "蓝牙",
        iconName: "bluetooth",
        kind: "switch",
        defaultChecked: true,
      },
      {
        id: "location",
        title: "位置信息",
        iconName: "location_north_up_right_circle_fill",
        kind: "value",
        value: "已开启",
        isLast: true,
      },
    ],
  },
  {
    id: "display",
    rows: [
      {
        id: "dark-mode",
        title: "深色模式",
        iconName: "moon_fill",
        kind: "switch",
        defaultChecked: false,
      },
      {
        id: "brightness",
        title: "亮度",
        iconName: "sun_max",
        kind: "value",
        value: "中等",
        isLast: true,
      },
    ],
  },
  {
    id: "notification",
    rows: [
      {
        id: "notification",
        title: "通知",
        iconName: "bell_fill",
        kind: "switch",
        defaultChecked: true,
      },
      {
        id: "sound",
        title: "声音",
        iconName: "speaker",
        kind: "switch",
        defaultChecked: true,
        isLast: true,
      },
    ],
  },
  {
    id: "security",
    rows: [
      {
        id: "security",
        title: "安全与隐私",
        iconName: "checkmark_shield_fill",
        kind: "link",
        isLast: true,
      },
    ],
  },
  {
    id: "storage",
    rows: [
      {
        id: "storage",
        title: "存储和备份",
        iconName: "externaldrive_fill",
        kind: "value",
        value: "128GB/256GB",
        isLast: true,
      },
    ],
  },
  {
    id: "system",
    rows: [
      {
        id: "language",
        title: "语言和地区",
        iconName: "worldclock",
        kind: "value",
        value: "简体中文",
      },
      {
        id: "date",
        title: "日期和时间",
        iconName: "calendar",
        kind: "link",
      },
      {
        id: "update",
        title: "系统更新",
        iconName: "arrow_up_circle",
        kind: "accentValue",
        value: "已是最新",
        isLast: true,
      },
    ],
  },
  {
    id: "about",
    rows: [
      {
        id: "about",
        title: "关于手机",
        iconName: "gearshape",
        kind: "value",
        value: "Mate 70 Pro",
        isLast: true,
      },
    ],
  },
  ]
}

function SettingsPageTemplatePage({
  className,
  title = "设置",
  showBack = true,
  onBack,
  onRowClick,
  onSwitchChange,
  groups,
}: SettingsPageTemplatePageProps) {
  const resolvedGroups = groups ?? buildGroups()
  // Track switch state in a derived initial map; consumers may pass controlled defaults.
  const initialChecked: Record<string, boolean> = {}
  for (const g of resolvedGroups) {
    for (const row of g.rows) {
      if (row.kind === "switch") {
        initialChecked[`${g.id}::${row.id}`] = row.defaultChecked ?? false
      }
    }
  }
  const [checked, setChecked] = useState<Record<string, boolean>>(initialChecked)

  return (
    <MobilePhoneShellTemplatePage
      className={cn("settings-page-template-shell", className)}
      mode="secondary"
      headerVariant="secondary"
      title={title}
      leadingAction={showBack ? { kind: "back", label: "Back", onClick: onBack } : null}
      showAIBottomBar
      showFloatingTab={false}
    >
      <ListContainer as="section" className="template-settings-page">
        {resolvedGroups.map((group) => (
          <div className="pixso-list-item" key={group.id}>
            <ListBlock
              bodyClassName="template-setting-group"
              items={group.rows.map((row, index) => {
                const key = `${group.id}::${row.id}`
                const isLastRow = row.isLast ?? index === group.rows.length - 1
                return {
                  key: row.id,
                  icon: row.icon,
                  left: row.iconName ? "24dp_ic" : undefined,
                  leftIconName: row.iconName,
                  lines: "1",
                  title: row.title,
                  type: row.kind === "switch" ? "switch" : "navigate",
                  value: row.kind === "value" || row.kind === "accentValue" ? row.value : undefined,
                  selected: row.kind === "switch" ? (checked[key] ? "ON" : "OFF") : undefined,
                  divider: !isLastRow,
                  className: cn(
                    "template-setting-row",
                    row.kind === "accentValue" && "template-setting-row--accent",
                    isLastRow && "template-setting-row--last",
                  ),
                  onClick: () => onRowClick?.(group.id, row.id),
                  onSelectedChange:
                    row.kind === "switch"
                      ? (selected) => {
                          const nextValue = selected === "ON"
                          setChecked((prev) => ({ ...prev, [key]: nextValue }))
                          onSwitchChange?.(group.id, row.id, nextValue)
                        }
                      : undefined,
                }
              })}
            />
          </div>
        ))}
      </ListContainer>
    </MobilePhoneShellTemplatePage>
  )
}

export { SettingsPageTemplatePage }
