import type { ReactNode } from "react"
import { useState } from "react"

import { FloatingTab, type FloatingTabItem } from "@/components/Navigation/FloatingTab"
import {
  FloatingTitleBar,
  type FloatingTitleBarAction,
  type FloatingTitleBarLeadingAction,
} from "@/components/Navigation/FloatingTitleBar"
import { HMSymbolIcon } from "@/components/HMSymbolIcon"
import { Aibottombar } from "@/components/Publis/Aibottombar"
import { NavigationContainer } from "@/container-components/NavigationContainer"
import { cn } from "@/lib/utils"

import "./mobile-phone-shell-template.css"

export type MobilePhoneShellMode = "app-home" | "secondary" | "immersive"
export type MobilePhoneShellHeaderVariant = "big" | "normal" | "secondary" | "drawer"

export interface MobilePhoneShellTemplatePageProps {
  /** 页面级固定主操作区；传入时自动显示并避开底部系统指示条。 */
  bottomPrimaryAction?: ReactNode
  className?: string
  contentClassName?: string
  headerClassName?: string
  bottomClassName?: string
  children?: ReactNode
  mode?: MobilePhoneShellMode
  headerVariant?: MobilePhoneShellHeaderVariant
  title?: string
  subtitleText?: string
  subtitle?: boolean
  headerActions?: FloatingTitleBarAction[]
  leadingAction?: FloatingTitleBarLeadingAction | null
  tabs?: FloatingTabItem[]
  activeTabKey?: string
  defaultActiveTabKey?: string
  onActiveTabChange?: (key: string) => void
  showTitleBar?: boolean
  showFloatingTab?: boolean
  showAIBottomBar?: boolean
}

function buildTabs(): FloatingTabItem[] {
  return [
  { key: "home", label: "首页", icon: <HMSymbolIcon name="house_fill" size={24} /> },
  { key: "feed", label: "动态", icon: <HMSymbolIcon name="discover_fill" size={24} /> },
  { key: "shop", label: "会员购", icon: <HMSymbolIcon name="picture_fill" size={24} /> },
  { key: "me", label: "我的", icon: <HMSymbolIcon name="person_crop_circle_fill_1" size={24} /> },
  ]
}

const headerTypeByVariant: Record<MobilePhoneShellHeaderVariant, Parameters<typeof FloatingTitleBar>[0]["标题类型"]> = {
  big: "Big",
  normal: "Normal",
  secondary: "Secondary",
  drawer: "Drawer",
}

function getFloatingTabCount(count: number) {
  return String(Math.min(5, Math.max(2, count))) as "2" | "3" | "4" | "5"
}

function MobilePhoneShellTemplatePage({
  activeTabKey,
  bottomPrimaryAction,
  bottomClassName,
  children,
  className,
  contentClassName,
  defaultActiveTabKey,
  headerActions,
  headerClassName,
  headerVariant = "normal",
  leadingAction,
  mode = "app-home",
  onActiveTabChange,
  showAIBottomBar = false,
  showFloatingTab = mode === "app-home",
  showTitleBar = true,
  subtitle,
  subtitleText = "Subtitle",
  tabs,
  title = "标题",
}: MobilePhoneShellTemplatePageProps) {
  const resolvedTabs = tabs ?? buildTabs()
  const shouldShowBottomPrimaryAction = !showFloatingTab && Boolean(bottomPrimaryAction)
  const shouldShowAIBottomBar = !showFloatingTab && (showAIBottomBar || shouldShowBottomPrimaryAction)
  const [uncontrolledActiveKey, setUncontrolledActiveKey] = useState(
    defaultActiveTabKey ?? resolvedTabs[0]?.key,
  )
  const currentActiveKey = activeTabKey ?? uncontrolledActiveKey

  return (
    <NavigationContainer
      className={cn("mobile-phone-shell-template", className)}
      data-header-variant={headerVariant}
      data-has-ai-bottom-bar={shouldShowAIBottomBar ? "true" : "false"}
      data-has-bottom-primary-action={shouldShowBottomPrimaryAction ? "true" : "false"}
      data-has-floating-tab={showFloatingTab ? "true" : "false"}
      data-mode={mode}
    >
      {showTitleBar ? (
        <FloatingTitleBar
          className={cn("mobile-phone-shell-template__header", headerClassName)}
          标题类型={headerTypeByVariant[headerVariant]}
          title={title}
          subtitleText={subtitleText}
          subtitle={subtitle}
          leadingAction={leadingAction}
          actions={headerActions}
        />
      ) : null}

      <main className={cn("mobile-phone-shell-template__body", contentClassName)}>
        {children}
      </main>

      {showFloatingTab ? (
        <footer className={cn("mobile-phone-shell-template__bottom", bottomClassName)}>
          <FloatingTab
            className="mobile-phone-shell-template__floating-tab"
            items={resolvedTabs}
            activeKey={currentActiveKey}
            onActiveKeyChange={(key) => {
              setUncontrolledActiveKey(key)
              onActiveTabChange?.(key)
            }}
            layout="port"
            数量={getFloatingTabCount(resolvedTabs.length)}
          />
        </footer>
      ) : shouldShowAIBottomBar ? (
        <footer className={cn("mobile-phone-shell-template__system-bottom", bottomClassName)}>
          {shouldShowBottomPrimaryAction ? (
            <div className="mobile-phone-shell-template__primary-action">
              <div className="mobile-phone-shell-template__primary-action-content">
                {bottomPrimaryAction}
              </div>
            </div>
          ) : null}
          <Aibottombar
            {...{ "Color Mode": "Light" }}
            className="mobile-phone-shell-template__ai-bottom"
            aria-hidden="true"
          />
        </footer>
      ) : null}
    </NavigationContainer>
  )
}

export { MobilePhoneShellTemplatePage }
