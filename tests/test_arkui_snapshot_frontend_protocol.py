"""Static contract tests for the browser-side ArkUI snapshot handshake."""

import re

import app as app_mod
from uibench.arkui.snapshot import BrowserComputedStyle


def _function_source(name: str, next_name: str) -> str:
    html = app_mod.INDEX_HTML
    start = html.index(f"function {name}")
    end = html.index(f"function {next_name}", start)
    return html[start:end]


def test_snapshot_runtime_announces_session_ready_after_listener_registration() -> None:
    runtime = _function_source(
        "arkuiSnapshotRuntime", "arkuiSnapshotBootstrap",
    )

    listener = runtime.index("window.addEventListener('message'")
    ready = runtime.index("type: 'uibench-arkui-snapshot-ready'")
    assert listener < ready
    assert "request.session !== captureSession" in runtime
    assert runtime.count("session: captureSession") >= 3
    assert "await boundedWait(new Promise(function(resolve)" in runtime
    assert "}), 250);" in runtime

    bootstrap = _function_source("arkuiSnapshotBootstrap", "injectForRender")
    assert "JSON.stringify(captureSession)" in bootstrap


def test_parent_waits_for_matching_ready_before_snapshot_request() -> None:
    waiting = _function_source("waitForCaptureFrame", "requestSnapshotFromFrame")
    assert "new Promise(function(resolve, reject)" in waiting
    assert "type !== 'uibench-arkui-snapshot-ready'" in waiting
    assert "message.session !== captureSession" in waiting
    assert "finish(resolve)" in waiting
    assert "finish(reject, new Error('浏览器样式快照'" in waiting
    assert "frame.addEventListener('load', onLoad)" in waiting
    assert "frame.addEventListener('error', onError)" in waiting

    capture = _function_source("captureArkUiSnapshot", "requestArkUiExport")
    prepared = capture.index("var captureHtml = injectForRender")
    listen = capture.index("waitForCaptureFrame(frame, captureSession)")
    srcdoc = capture.index("frame.srcdoc = captureHtml")
    append = capture.index("document.body.appendChild(frame)")
    ready = capture.index("await readiness")
    request = capture.index("requestSnapshotFromFrame(frame, captureSession)")
    assert prepared < listen < srcdoc < append < ready < request


def test_snapshot_request_and_response_are_bound_to_session_and_token() -> None:
    request = _function_source("requestSnapshotFromFrame", "captureArkUiSnapshot")
    assert "newArkUiCaptureId('snapshot-request')" in request
    assert "message.session !== captureSession || message.token !== token" in request
    assert "session: captureSession" in request
    assert "reject(new Error('浏览器样式快照超时'))" in request


def test_download_does_not_fall_back_to_null_snapshot() -> None:
    html = app_mod.INDEX_HTML
    assert "snapshot = null" not in html
    assert "ArkUI browser snapshot unavailable" not in html
    assert "const snapshot = await captureArkUiSnapshot(r)" in html
    assert "console.error('ArkUI export failed', error)" in html
    assert "window.alert('ArkUI 导出失败：' + String(error))" in html
    assert "window.clearTimeout(exportLabelResetTimer)" in html


def test_export_failure_surfaces_the_reason_not_just_the_headline() -> None:
    """Canvas and snapshot gates report an object whose reason is the fix."""
    describe = _function_source(
        "describeExportErrorDetails", "requestArkUiExport",
    )

    assert "Array.isArray(details)" in describe
    assert "details.reason" in describe
    assert "details.nodeId" in describe
    assert "details.missingFields" in describe
    request = _function_source("requestArkUiExport", "downloadText")
    assert "describeExportErrorDetails(error.details)" in request


def test_blocked_export_button_explains_why_on_click() -> None:
    """A disabled button swallows clicks, so the blocked state stays
    clickable and the click lists the blocking diagnostics."""
    fill_card = _function_source("fillCard", "normalizeDesignTokenClassName")

    assert "exportBtn.disabled = !arkuiSummary.exportable" not in fill_card
    assert "exportBtn.classList.add('export-blocked')" in fill_card
    assert "点击查看不可导出的原因" in fill_card
    assert "window.alert(formatArkUiBlockReasons(r.arkui_manifest))" in fill_card
    # The blocked branch answers before any export work starts.
    assert (fill_card.index("formatArkUiBlockReasons")
            < fill_card.index("captureArkUiSnapshot"))
    assert ".tools button.export-blocked" in app_mod.INDEX_HTML

    reasons = _function_source(
        "formatArkUiBlockReasons", "describeExportErrorDetails",
    )
    # Mirrors metadata.py export_readiness: these warning codes block the
    # export too, and the single-root rule only exists as a summary counter.
    assert "item.severity !== 'error'" in reasons
    assert "'ARKUI_NODE_ID_MISSING'" in reasons
    assert "'ARKUI_COMPONENT_NOT_RENDERER_SUPPORTED'" in reasons
    assert "summary.rootComponents !== 1" in reasons
    assert "查看日志" in reasons


def test_lossy_download_surfaces_warning_details_in_page() -> None:
    """「已下载（有损）」alone answers nothing; the card keeps a button that
    lists every warning-level deviation from the export response."""
    fill_card = _function_source("fillCard", "normalizeDesignTokenClassName")

    assert "lossyBtn.style.display = 'none'" in fill_card
    assert "exported.quality.readiness !== 'ready'" in fill_card
    assert "item && item.severity === 'warning'" in fill_card
    assert "openArkUiLossDetails(r.name, exportDiagnostics)" in fill_card
    assert "tools.append(exportBtn, lossyBtn)" in fill_card
    # A fresh export hides the previous run's reasons before any work starts.
    handler_start = fill_card.index("exportBtn.onclick")
    assert (fill_card.index("lossyBtn.style.display = 'none'", handler_start)
            < fill_card.index("captureArkUiSnapshot", handler_start))

    details = _function_source("openArkUiLossDetails", "esc")
    assert "severity === 'warning'" in details
    assert "severity === 'notice'" in details
    assert "renderArkUiDiagnosticGroup(group, 'warning')" in details
    assert "工程 zip 已完整下载" in details

    html = app_mod.INDEX_HTML
    # Style-lossy diagnostics surface the exact CSS property; known codes get
    # a human explanation of what the deviation looks like on device.
    assert "UIBENCH_BROWSER_STYLE_LOSSY" in html
    assert "样式无法在 ArkUI 精确表达：" in html
    assert "ARKUI_SYMBOL_UNAVAILABLE" in html
    assert ".tools button.lossy-reasons" in html


def test_download_name_is_timestamped_without_touching_the_bundle_name() -> None:
    """Regression artifacts stay comparable; repeated downloads stay distinct."""
    stamp = _function_source("withDownloadTimestamp", "downloadBase64")
    fill_card = _function_source("fillCard", "normalizeDesignTokenClassName")

    assert "filename.lastIndexOf('.')" in stamp
    assert "filename.slice(0, dot) + '_' + stamp + filename.slice(dot)" in stamp
    assert "withDownloadTimestamp(" in fill_card
    # The server-side name has to stay deterministic for the fixture exports.
    assert "Date()" not in app_mod.INDEX_HTML.split("function withDownloadTimestamp", 1)[0]


def test_complete_project_download_fails_closed_without_bundle_content() -> None:
    fill_card = _function_source("fillCard", "normalizeDesignTokenClassName")
    request = _function_source("requestArkUiExport", "downloadText")

    assert "downloadBase64(" in fill_card
    assert "downloadText(" not in fill_card
    assert "typeof payload.bundle.contentBase64 !== 'string'" in request
    assert "!payload.bundle.contentBase64.trim()" in request
    assert "ArkUI 完整工程响应缺少 bundle.contentBase64" in request
    assert request.index("bundle.contentBase64") < request.index("return payload")


def test_mobile_preview_and_export_share_the_390_by_844_contract() -> None:
    html = app_mod.INDEX_HTML
    assert app_mod.MOBILE_VIEWPORT_WIDTH == 390
    assert app_mod.MOBILE_VIEWPORT_HEIGHT == 844
    assert ".phone { width: 390px; min-width: 390px; max-width: none;" in html
    assert "height: 844px; border: 0" in html
    assert ".skeleton { width: 390px; max-width: 100%; height: 844px" in html
    assert ".render-status { width: 390px; max-width: 100%" in html
    assert "minmax(min(calc(390px + 34px), 100%), 1fr)" in html
    assert "overflow-x: auto; overflow-y: hidden" in html
    assert "@media (max-width: 520px)" in html
    assert "width:390px;height:844px" in html
    assert "viewport_width: 390" in html
    assert "viewport_height: 844" in html
    assert "360px" not in html
    assert "640px" not in html
    assert "__UIBENCH_MOBILE_VIEWPORT_" not in html


def test_snapshot_runtime_captures_flex_sizing_properties() -> None:
    runtime = _function_source("arkuiSnapshotRuntime", "arkuiSnapshotBootstrap")
    assert "'flexGrow', 'flexShrink', 'flexBasis'" in runtime
    assert "getAttribute('data-node-id')" in runtime
    assert "directParentNodeId: directParentNodeId" in runtime
    assert "isFlexItem: isFlexItem" in runtime
    assert "directParentDisplay === 'flex'" in runtime
    assert "directParentDisplay === 'inline-flex'" in runtime


def test_snapshot_runtime_emits_every_validated_computed_style_field() -> None:
    runtime = _function_source("arkuiSnapshotRuntime", "arkuiSnapshotBootstrap")
    start = runtime.index("var styleProperties = [")
    end = runtime.index("];", start)
    emitted = set(re.findall(r"'([^']+)'", runtime[start:end]))
    emitted.update({"pseudoBeforeContent", "pseudoAfterContent"})
    expected = {
        str(field.serialization_alias or field.alias or field_name)
        for field_name, field in BrowserComputedStyle.model_fields.items()
    }

    assert emitted == expected
    assert "elementPosition !== 'absolute'" in runtime
    assert "elementPosition !== 'fixed'" in runtime


def test_snapshot_runtime_preserves_canvas_and_promotes_only_a_plain_color() -> None:
    runtime = _function_source("arkuiSnapshotRuntime", "arkuiSnapshotBootstrap")

    assert "function isTransparentColor(value)" in runtime
    assert "color === 'transparent'" in runtime
    assert "Number(alpha[1]) === 0" in runtime
    assert "function visibleCanvasBackground()" in runtime
    assert "htmlStyle.backgroundImage" in runtime
    assert "bodyStyle.backgroundImage" in runtime
    assert "bodyImage.trim().toLowerCase() !== 'none'" in runtime
    assert "canvasBackgroundColor: canvasBackground.backgroundColor" in runtime
    assert "canvasBackgroundImage:" in runtime
    assert "function singleAnnotatedRoot(elements)" in runtime
    assert "if (roots.length !== 1) return null" in runtime
    # Containment, not equality: every scrollable page is taller than the
    # viewport it was captured in.
    assert "rect.x + rect.width >= window.innerWidth - 1" in runtime
    assert "rect.y + rect.height >= window.innerHeight - 1" in runtime
    assert "Math.abs(rect.height - window.innerHeight)" not in runtime
    assert "return coversViewport ? root : null" in runtime
    assert "getAttribute('data-component')" in runtime
    assert "element === canvasRoot" in runtime
    assert "isTransparentColor(computed.backgroundColor)" in runtime
    assert "canvasBackground.backgroundImage.trim().toLowerCase() === 'none'" in runtime
    assert "computed.backgroundColor = canvasBackground.backgroundColor" in runtime


def test_snapshot_runtime_visibility_includes_ancestor_render_state() -> None:
    runtime = _function_source("arkuiSnapshotRuntime", "arkuiSnapshotBootstrap")

    assert "function isActuallyVisible(element, rect)" in runtime
    assert "element.checkVisibility" in runtime
    assert "checkOpacity: true" in runtime
    assert "opacityProperty: true" in runtime
    assert "checkVisibilityCSS: true" in runtime
    assert "visibilityProperty: true" in runtime
    assert "while (current)" in runtime
    assert "getComputedStyle(current)" in runtime
    assert "current = current.parentElement" in runtime
    assert "var visible = isActuallyVisible(element, rect)" in runtime
