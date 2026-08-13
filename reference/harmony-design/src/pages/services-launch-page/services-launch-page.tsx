import type { ReactNode } from "react"

import { Aibottombar } from "@/components/Publis/Aibottombar"
import { Button } from "@/components/Controls/Button"
import { StatusBar } from "@/components/Publis/StatusBar"
import { ListContainer } from "@/container-components/ListContainer"
import { NavigationContainer } from "@/container-components/NavigationContainer"
import { cn } from "@/lib/utils"

import huaweiVideoIcon from "./assets/huawei-video-icon.png"

import "./services-launch-page.css"

export interface ServicesLaunchPageProps {
  className?: string
  appIconSlot?: ReactNode
  privacyIconSlot?: ReactNode
  title?: string
  subtitle?: string
  privacyText1?: string
  privacyLink?: string
  privacyText2?: string
  agreeLabel?: string
  cancelLabel?: string
  onAgree?: () => void
  onCancel?: () => void
  showStatusBar?: boolean
  showBottomBar?: boolean
}

const DEFAULT_PRIVACY_TEXT_1 =
  "本应用需联网，可能会读取和修改日程，用于提供在线视频服务。我们仅在您使用具体功能业务时，才会触发上述行为收集使用相关的个人信息。详情请参阅"
const DEFAULT_PRIVACY_LINK = "关于华为视频与隐私的声明"
const DEFAULT_PRIVACY_TEXT_2 =
  "请您仔细阅读上述声明，点击“同意”，即表示您知悉并同意我们向您提供本应用服务。"

function AppIcon() {
  return (
    <img
      src={huaweiVideoIcon}
      alt="华为视频应用图标"
      width={72}
      height={72}
      style={{ borderRadius: "16px", display: "block" }}
    />
  )
}

function PrivacyShieldIcon() {
  return (
    <svg
      viewBox="52 52 24 24"
      width="24"
      height="24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="隐私保护图标"
    >
      <path
        id="privacy-lock"
        d="M62.6912 53.3011L56.2684 56.4151C55.4926 56.7913 55 57.5776 55 58.4397L55 63.25C55 68.5172 58.3555 73.1121 63.252 74.7984C63.267 74.8035 63.2979 74.8135 63.3389 74.8265C63.7689 74.9628 64.2311 74.9627 64.6611 74.8264C64.7036 74.8129 64.7356 74.8026 64.7509 74.7973C69.6459 73.1101 73 68.5159 73 63.25L73 58.4397C73 57.5776 72.5074 56.7913 71.7316 56.4151L65.3088 53.3011C64.4823 52.9003 63.5177 52.9003 62.6912 53.3011ZM64.6544 54.6508L71.0772 57.7648C71.3358 57.8902 71.5 58.1523 71.5 58.4397L71.5 63.25L71.4991 63.3909C71.473 65.4045 70.888 67.3016 69.8765 68.9187C69.8244 68.605 69.7502 68.3082 69.6445 68.0833C69.2515 67.247 68.165 64.75 64.0018 64.75C59.8387 64.75 58.7703 67.247 58.3591 68.0833C58.2492 68.307 58.1729 68.6017 58.1201 68.9135C57.0872 67.2599 56.5 65.3138 56.5 63.25L56.5 58.4397C56.5 58.1523 56.6642 57.8902 56.9228 57.7648L63.3456 54.6508C63.7589 54.4504 64.2411 54.4504 64.6544 54.6508ZM63.875 58.12C62.2154 58.12 60.87 59.4653 60.87 61.125C60.87 62.7846 62.2154 64.13 63.875 64.13C65.5346 64.13 66.88 62.7846 66.88 61.125C66.88 59.4653 65.5346 58.12 63.875 58.12Z"
        fill="var(--harmony-video-brand)"
        fillRule="evenodd"
      />
    </svg>
  )
}

function ServicesLaunchPage({
  className,
  appIconSlot,
  privacyIconSlot,
  title = "华为视频",
  subtitle = "一站看遍全视界",
  privacyText1 = DEFAULT_PRIVACY_TEXT_1,
  privacyLink = DEFAULT_PRIVACY_LINK,
  privacyText2 = DEFAULT_PRIVACY_TEXT_2,
  agreeLabel = "同意",
  cancelLabel = "取消",
  onAgree,
  onCancel,
  showStatusBar = true,
  showBottomBar = true,
}: ServicesLaunchPageProps) {
  return (
    <div className={cn("services-launch-page", className)}>
      {showStatusBar && (
        <StatusBar className="services-launch-page__status" {...{ "Color Mode": "Dark" }} />
      )}

      <NavigationContainer as="main" className="services-launch-page__screen">
        <div className="services-launch-page__bg-mask" />
        <div className="services-launch-page__bg-mask-tertiary" />
        <div className="services-launch-page__bg-blur" />

        <section className="services-launch-page__hero">
          <div className="services-launch-page__app-icon" data-slot="appIconSlot">
            {appIconSlot ?? <AppIcon />}
          </div>
          <h1 className="services-launch-page__title">{title}</h1>
          <p className="services-launch-page__subtitle">{subtitle}</p>
        </section>

        <section className="services-launch-page__privacy">
          <div className="services-launch-page__privacy-icon" data-slot="privacyIconSlot">
            {privacyIconSlot ?? <PrivacyShieldIcon />}
          </div>
          <p className="services-launch-page__privacy-text">
            {privacyText1}
            <span className="services-launch-page__privacy-link">{privacyLink}</span>
            。
          </p>
          <p className="services-launch-page__privacy-text">{privacyText2}</p>
          <ListContainer className="services-launch-page__buttons">
            <Button
              className="pixso-list-item services-launch-page__btn-cancel"
              尺寸="Medium"
              类型="Normal"
              状态="Enabled"
              onClick={onCancel}
            >
              {cancelLabel}
            </Button>
            <Button
              className="pixso-list-item services-launch-page__btn-agree"
              尺寸="Medium"
              类型="Emphasized"
              状态="Enabled"
              onClick={onAgree}
            >
              {agreeLabel}
            </Button>
          </ListContainer>
        </section>

      </NavigationContainer>

      {showBottomBar && (
        <Aibottombar className="services-launch-page__bottom-bar" {...{ "Color Mode": "Dark" }} />
      )}
    </div>
  )
}

export { ServicesLaunchPage }
