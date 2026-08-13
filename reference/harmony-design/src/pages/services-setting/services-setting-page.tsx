import { List } from "@/blocks/list"
import { FloatingSheetSemiModal } from "@/blocks/floating-sheet-semi-modal"
import { ListPhone } from "@/components/Container/ListPhone"
import { Aibottombar } from "@/components/Publis/Aibottombar"
import { StatusBar } from "@/components/Publis/StatusBar"
import { NavigationContainer } from "@/container-components/NavigationContainer"

import "./services-setting-page.css"

function ServicesSettingPage() {
  return (
    <div className="services-setting-root">
      {/* ── 状态栏（蒙层之上可见） ── */}
      <StatusBar
        {...{ "Color Mode": "Light" }}
        className="services-setting-status-bar"
      />

      <NavigationContainer>
        <FloatingSheetSemiModal
          className="services-setting-semi-modal"
          title="设置"
          showClose
          defaultHeight={748}
          role="dialog"
          aria-label="设置"
        >
          <section className="services-setting-page">
          {/* ── 数据和隐私 ── */}
          <div className="services-setting-section-title">数据和隐私</div>
          <List
            variant="grouped"
            className="services-setting-data-privacy"
            footnote="了解我们如何使用您的数据"
          >
            <ListPhone title="个性化推荐" right="Arrow" rightText="" divider />
            <ListPhone title="分析与改进" right="Arrow" rightText="" divider />
            <ListPhone title="权限管理" right="Arrow" rightText="" divider />
            <ListPhone title="自定义列表" right="Arrow" rightText="" divider />
            <ListPhone
              title="更多"
              right="Arrow"
              rightText=""
              divider={false}
            />
          </List>

          {/* ── 隐私政策相关 ── */}
          <List variant="grouped">
            <ListPhone
              title={
                <span className="services-setting-page__title-with-dot">
                  业务与隐私的声明
                  <span
                    className="services-setting-page__red-dot"
                    aria-label="重要"
                  />
                </span>
              }
              right="Arrow"
              rightText=""
              divider
            />
            <ListPhone
              title="第三方共享信息清单"
              right="Arrow"
              rightText=""
              divider
            />
            <ListPhone
              title="第三方 SDK 列表"
              right="Arrow"
              rightText=""
              divider
            />
            <ListPhone
              title="已收集个人信息清单"
              right="Arrow"
              rightText=""
              divider
            />
            <ListPhone
              title="隐私声明摘要"
              right="Arrow"
              rightText=""
              divider
            />
            <ListPhone
              title="自定义列表"
              right="Arrow"
              rightText=""
              divider={false}
            />
          </List>

          {/* ── 更多 ── */}
          <div className="services-setting-section-title">更多</div>
          <List variant="grouped" className="services-setting-more">
            <ListPhone
              title="应用服务模式"
              right="Arrow"
              rightText="全量模式"
              divider
            />
            <ListPhone title="服务管理" right="Menu select" divider />
            <ListPhone
              title="其他"
              right="Arrow"
              rightText=""
              divider={false}
            />
          </List>

          {/* ── 关于 / 服务协议 ── */}
          <List variant="grouped">
            <ListPhone
              title={
                <span className="services-setting-page__title-with-dot">
                  关于
                  <span
                    className="services-setting-page__red-dot"
                    aria-label="重要"
                  />
                </span>
              }
              right="Arrow"
              rightText="版本 1.0.0"
              divider
            />
            <ListPhone
              title="服务协议与规则"
              right="Arrow"
              rightText=""
              divider={false}
            />
          </List>
          </section>
        </FloatingSheetSemiModal>
      </NavigationContainer>

      <Aibottombar
        {...{ "Color Mode": "Light" }}
        className="services-setting-ai-bottom-bar"
        aria-hidden="true"
      />
    </div>
  )
}

export { ServicesSettingPage }
