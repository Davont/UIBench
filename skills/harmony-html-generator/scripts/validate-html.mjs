#!/usr/bin/env node

import { existsSync, readFileSync } from "node:fs"
import { dirname, isAbsolute, join, relative, resolve, sep } from "node:path"
import { fileURLToPath } from "node:url"

const args = process.argv.slice(2)
const jsonOutput = args.includes("--json")
const targetArg = args.find((arg) => !arg.startsWith("--"))
if (!targetArg) {
  console.error("Usage: node validate-html.mjs <index.html> [--json]")
  process.exit(2)
}

const target = resolve(targetArg)
if (!existsSync(target)) {
  console.error(`Target does not exist: ${target}`)
  process.exit(2)
}

const scriptDir = dirname(fileURLToPath(import.meta.url))
const skillDir = resolve(scriptDir, "..")
const contract = JSON.parse(readFileSync(join(skillDir, "references", "component-contract.json"), "utf8"))
const iconMap = JSON.parse(readFileSync(join(skillDir, "references", "icon-map.json"), "utf8"))
const bundledRuntimeCss = readFileSync(join(skillDir, "assets", "harmony-runtime.css"), "utf8")
const knownRuntimeClasses = new Set()
for (const block of bundledRuntimeCss.matchAll(/([^{}]+)\{/g)) {
  for (const item of block[1].matchAll(/\.([a-z_][a-z0-9_-]*)/gi)) knownRuntimeClasses.add(item[1])
}
const html = readFileSync(target, "utf8")
const errors = []
const warnings = []

function issue(collection, code, message, nodeId = null) {
  collection.push({ code, message, nodeId })
}

function parseAttributes(source) {
  const attrs = {}
  const pattern = /([^\s=/>]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+)))?/g
  let match
  while ((match = pattern.exec(source)) !== null) {
    const name = match[1].toLowerCase()
    if (name === "/") continue
    attrs[name] = match[2] ?? match[3] ?? match[4] ?? ""
  }
  return attrs
}

function classesFor(element) {
  return new Set((element.attrs.class ?? "").split(/\s+/).filter(Boolean))
}

function hasMeaningfulText(value) {
  return value.replace(/&(?:#x?[0-9a-f]+|[a-z]+);/gi, "x").trim().length > 0
}

function hasReadableText(value) {
  return value.replace(/&(?:#x?[0-9a-f]+|[a-z]+);/gi, "").trim().length > 0
}

const voidTags = new Set(["area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"])
const allElements = []
const componentNodes = []
const stack = []
const tokenPattern = /<\/?([a-z][a-z0-9:-]*)\b([^<>]*?)>/gi
let previousEnd = 0
let maxHtmlDepth = 0
let maxComponentDepth = 0
let match

while ((match = tokenPattern.exec(html)) !== null) {
  const text = html.slice(previousEnd, match.index)
  if (text && stack.length > 0) {
    for (const element of stack) element.text += text
  }
  previousEnd = tokenPattern.lastIndex

  const whole = match[0]
  const tag = match[1].toLowerCase()
  if (whole.startsWith("</")) {
    const matchingIndex = stack.findLastIndex((item) => item.tag === tag)
    if (matchingIndex < 0) {
      issue(errors, "HTML_CLOSING_TAG_UNEXPECTED", `Unexpected closing tag </${tag}>`)
    } else {
      if (matchingIndex !== stack.length - 1) {
        issue(errors, "HTML_TAG_NESTING_INVALID", `Closing </${tag}> before <${stack.at(-1).tag}>`)
      }
      stack.length = matchingIndex
    }
    continue
  }

  const attrs = parseAttributes(match[2] ?? "")
  const domParent = stack.at(-1) ?? null
  const parentComponent = [...stack].reverse().find((item) => item.component) ?? null
  const element = {
    tag,
    attrs,
    component: attrs["data-component"] ?? null,
    nodeId: attrs["data-node-id"] ?? null,
    domParent,
    parentComponent,
    componentChildren: [],
    text: "",
    htmlDepth: stack.length + 1,
    componentDepth: attrs["data-component"] ? (parentComponent?.componentDepth ?? 0) + 1 : 0,
  }
  maxHtmlDepth = Math.max(maxHtmlDepth, element.htmlDepth)
  allElements.push(element)
  if (element.component) {
    maxComponentDepth = Math.max(maxComponentDepth, element.componentDepth)
    componentNodes.push(element)
    if (parentComponent) parentComponent.componentChildren.push(element)
  }
  if (!voidTags.has(tag) && !whole.endsWith("/>")) stack.push(element)
}

if (stack.length > 0) {
  issue(errors, "HTML_TAG_UNCLOSED", `Unclosed tag <${stack.at(-1).tag}>`)
}
if (maxHtmlDepth > contract.htmlDepthLimit) {
  issue(errors, "HTML_DEPTH_EXCEEDED", `HTML depth ${maxHtmlDepth} exceeds ${contract.htmlDepthLimit}`)
}
if (maxComponentDepth > contract.componentDepthLimit) {
  issue(errors, "COMPONENT_DEPTH_EXCEEDED", `Component depth ${maxComponentDepth} exceeds ${contract.componentDepthLimit}`)
}

if (!/<!doctype\s+html\s*>/i.test(html)) issue(errors, "HTML_DOCTYPE_MISSING", "Document must start with an HTML doctype")
if (!/<html\b/i.test(html) || !/<head\b/i.test(html) || !/<body\b/i.test(html)) {
  issue(errors, "HTML_DOCUMENT_INCOMPLETE", "Document must contain html, head, and body elements")
}
if (!/<meta\b[^>]*name\s*=\s*["']viewport["']/i.test(html)) issue(errors, "HTML_VIEWPORT_MISSING", "Viewport metadata is required")
if (!/<link\b[^>]*href\s*=\s*["']assets\/harmony-runtime\.css["']/i.test(html)) {
  issue(errors, "RUNTIME_STYLESHEET_MISSING", "assets/harmony-runtime.css must be linked")
}
const htmlElement = allElements.find((element) => element.tag === "html")
if (!htmlElement?.attrs.lang?.trim()) issue(errors, "HTML_LANG_MISSING", "The html element requires a language")
if (!new Set(["light", "dark"]).has(htmlElement?.attrs["data-theme"]?.toLowerCase())) {
  issue(errors, "HTML_THEME_INVALID", 'The html element requires data-theme="light" or data-theme="dark"')
}
const titleMatch = html.match(/<title\b[^>]*>([\s\S]*?)<\/title>/i)
if (!titleMatch || !hasReadableText(titleMatch[1])) issue(errors, "HTML_TITLE_MISSING", "A non-empty document title is required")
if (/<style\b/i.test(html)) issue(errors, "CUSTOM_STYLE_BLOCK_FORBIDDEN", "Generated HTML must not contain style blocks")
if (/\sstyle\s*=/i.test(html)) issue(errors, "INLINE_STYLE_FORBIDDEN", "Generated HTML must not contain inline style attributes")
if (/<(?:textarea|select|progress)\b/i.test(html)) issue(errors, "UNSUPPORTED_NATIVE_CONTROL", "textarea, select, and progress are not supported")

const references = [...html.matchAll(/\b(src|href)\s*=\s*["']([^"']+)["']/gi)].map((item) => ({
  attribute: item[1].toLowerCase(),
  value: item[2].trim(),
}))
const outputDir = dirname(target)
for (const item of references) {
  const reference = item.value
  if (item.attribute === "href" && /^(?:#|mailto:|tel:)/i.test(reference)) continue
  if (/^(?:https?:)?\/\//i.test(reference) || /^(?:javascript|data|blob):/i.test(reference) || reference.startsWith("/")) {
    issue(errors, "EXTERNAL_RESOURCE_FORBIDDEN", `Resource must be local and relative: ${reference}`)
    continue
  }
  const pathPart = reference.split(/[?#]/, 1)[0]
  if (!pathPart) continue
  const resolvedReference = resolve(outputDir, pathPart)
  const relativeReference = relative(outputDir, resolvedReference)
  if (relativeReference === ".." || relativeReference.startsWith(`..${sep}`) || isAbsolute(relativeReference)) {
    issue(errors, "RESOURCE_PATH_ESCAPE", `Resource must stay inside the output directory: ${reference}`)
  } else if (!existsSync(resolvedReference)) {
    issue(errors, "LOCAL_RESOURCE_MISSING", `Referenced local resource does not exist: ${reference}`)
  }
}

if (/<script\b/i.test(html)) {
  issue(errors, "SCRIPT_FORBIDDEN", "Generated HTML must not contain scripts")
}

const nativeExpected = new Map([
  ["button", "button"],
  ["img", "image"],
])
for (const element of allElements) {
  const uiRole = element.attrs["data-ui-role"]
  if (uiRole !== undefined && !new RegExp(contract.uiRolePattern).test(uiRole)) {
    issue(errors, "UI_ROLE_INVALID", `Invalid data-ui-role: ${uiRole}`, element.nodeId)
  }
  if (nativeExpected.has(element.tag) && !element.component) {
    issue(errors, "NATIVE_COMPONENT_ANNOTATION_MISSING", `<${element.tag}> requires data-component="${nativeExpected.get(element.tag)}"`)
  }
  if (element.tag === "input" && !element.component) {
    issue(errors, "NATIVE_COMPONENT_ANNOTATION_MISSING", "<input> requires a supported data-component annotation")
  }
  if (element.attrs["data-lucide"] && element.component !== "symbol") {
    issue(errors, "SYMBOL_ANNOTATION_MISSING", 'Elements with data-lucide must use data-component="symbol"', element.nodeId)
  }
  if (element.component && element.parentComponent && element.domParent !== element.parentComponent) {
    issue(errors, "UNANNOTATED_COMPONENT_WRAPPER", "Annotated components cannot be separated by an unannotated DOM wrapper", element.nodeId)
  }
}

const knownComponents = contract.components
const controlRowComponents = new Set(contract.controlRowComponents ?? [])
const nodeIds = new Set()
const roots = componentNodes.filter((node) => node.parentComponent === null)
if (roots.length !== 1) issue(errors, "COMPONENT_ROOT_COUNT_INVALID", `Expected exactly one component root, found ${roots.length}`)
if (roots.length === 1) {
  const rootClasses = classesFor(roots[0])
  for (const required of contract.rootClassAll ?? ["min-h-screen"]) {
    if (!rootClasses.has(required)) {
      issue(errors, "COMPONENT_ROOT_CLASS_MISSING", `The component root requires class ${required}`, roots[0].nodeId)
    }
  }
}

const forbiddenClasses = new Set(["fixed", "sticky", "flex-row-reverse", "flex-col-reverse", "grid-flow-col"])
for (const element of allElements) {
  for (const className of classesFor(element)) {
    if (!knownRuntimeClasses.has(className)) {
      issue(errors, "RUNTIME_CLASS_UNKNOWN", `Class is not defined by harmony-runtime.css: ${className}`, element.nodeId)
    }
    if (forbiddenClasses.has(className) || /^(?:col|row)-span-/.test(className)) {
      issue(errors, "LAYOUT_CLASS_FORBIDDEN", `Forbidden layout class: ${className}`, element.nodeId)
    }
    if (/\[|\]|(?:^|:)(?:bg|text|border)-(?:black|white|gray|slate|red|blue|green|yellow)/.test(className)) {
      issue(errors, "RAW_STYLE_CLASS_FORBIDDEN", `Use semantic token classes instead of ${className}`, element.nodeId)
    }
  }
}

for (const node of componentNodes) {
  const definition = knownComponents[node.component]
  if (!definition) {
    issue(errors, "COMPONENT_UNKNOWN", `Unsupported data-component: ${node.component}`, node.nodeId)
    continue
  }
  if (!node.nodeId) {
    issue(errors, "NODE_ID_MISSING", "Every component requires data-node-id", null)
  } else if (!new RegExp(contract.nodeIdPattern).test(node.nodeId)) {
    issue(errors, "NODE_ID_INVALID", `Invalid data-node-id: ${node.nodeId}`, node.nodeId)
  } else if (nodeIds.has(node.nodeId)) {
    issue(errors, "NODE_ID_DUPLICATE", `Duplicate data-node-id: ${node.nodeId}`, node.nodeId)
  } else {
    nodeIds.add(node.nodeId)
  }

  const classList = classesFor(node)
  for (const required of definition.classAll ?? []) {
    if (!classList.has(required)) issue(errors, "COMPONENT_CLASS_MISSING", `${node.component} requires class ${required}`, node.nodeId)
  }

  if (definition.tag && node.tag !== definition.tag) issue(errors, "COMPONENT_TAG_INVALID", `${node.component} must use <${definition.tag}>`, node.nodeId)
  if (definition.tagAny && !definition.tagAny.includes(node.tag)) issue(errors, "COMPONENT_TAG_INVALID", `${node.component} must use one of ${definition.tagAny.join(", ")}`, node.nodeId)
  for (const required of definition.requiredAttributes ?? []) {
    if (!(required in node.attrs) || !node.attrs[required].trim()) issue(errors, "COMPONENT_ATTRIBUTE_MISSING", `${node.component} requires ${required}`, node.nodeId)
  }
  if (definition.inputType && node.attrs.type?.toLowerCase() !== definition.inputType) issue(errors, "INPUT_TYPE_INVALID", `${node.component} requires type="${definition.inputType}"`, node.nodeId)
  if (definition.inputTypeAny && !definition.inputTypeAny.includes(node.attrs.type?.toLowerCase())) issue(errors, "INPUT_TYPE_INVALID", `${node.component} has unsupported input type`, node.nodeId)
  if (node.component === "button") {
    if (node.attrs.type !== undefined && node.attrs.type.toLowerCase() !== "button") {
      issue(errors, "BUTTON_TYPE_INVALID", 'button requires type="button"', node.nodeId)
    }
    if (!node.attrs["aria-label"]?.trim() && !hasReadableText(node.text)) {
      issue(errors, "BUTTON_ACCESSIBLE_NAME_MISSING", "button requires visible text or aria-label", node.nodeId)
    }
  }
  if (node.component === "symbol" && node.attrs["aria-hidden"] !== undefined && node.attrs["aria-hidden"].toLowerCase() !== "true") {
    issue(errors, "SYMBOL_ARIA_HIDDEN_INVALID", 'symbol requires aria-hidden="true"', node.nodeId)
  }
  if (controlRowComponents.has(node.component)) {
    const controlRow = node.parentComponent
    if (controlRow?.component !== "row" || controlRow.tag !== "label" || controlRow.attrs["data-ui-role"] !== "control-row") {
      issue(
        errors,
        "CONTROL_ROW_REQUIRED",
        `${node.component} must be a direct child of <label data-component="row" data-ui-role="control-row">`,
        node.nodeId,
      )
    } else {
      const controlRowClasses = classesFor(controlRow)
      for (const required of ["items-center", "w-full"]) {
        if (!controlRowClasses.has(required)) {
          issue(errors, "CONTROL_ROW_CLASS_MISSING", `control-row requires class ${required}`, controlRow.nodeId)
        }
      }
      const hasLabelContent = controlRow.componentChildren.some(
        (child) => !controlRowComponents.has(child.component) && hasReadableText(child.text),
      )
      if (contract.controlRowRequiresLabelContent && !hasLabelContent) {
        issue(
          errors,
          "CONTROL_ROW_LABEL_CONTENT_MISSING",
          "control-row must include annotated visible label content alongside its control; keep the label content and input in the same <label>",
          controlRow.nodeId,
        )
      }
    }
  }
  if (definition.leaf && node.componentChildren.length > 0) issue(errors, "LEAF_COMPONENT_HAS_CHILDREN", `${node.component} cannot contain component children`, node.nodeId)
  if (definition.maxComponentChildren !== undefined && node.componentChildren.length > definition.maxComponentChildren) {
    issue(errors, "COMPONENT_CHILD_COUNT_EXCEEDED", `${node.component} allows at most ${definition.maxComponentChildren} component child`, node.nodeId)
  }
  if (definition.allowedChildren) {
    for (const child of node.componentChildren) {
      if (!definition.allowedChildren.includes(child.component)) issue(errors, "COMPONENT_CHILD_INVALID", `${node.component} cannot directly contain ${child.component}`, child.nodeId)
    }
  }
  if (definition.allowedParents && !definition.allowedParents.includes(node.parentComponent?.component)) {
    issue(errors, "COMPONENT_PARENT_INVALID", `${node.component} requires parent ${definition.allowedParents.join(" or ")}`, node.nodeId)
  }
  if (definition.requireText && !hasMeaningfulText(node.text)) issue(errors, "COMPONENT_TEXT_MISSING", `${node.component} requires non-empty text`, node.nodeId)
  if (node.component === "symbol") {
    const iconName = node.attrs["data-lucide"]
    const icon = iconMap.icons[iconName]
    if (!icon) {
      issue(errors, "ICON_UNKNOWN", `Unknown local icon: ${iconName}`, node.nodeId)
    } else if (!new RegExp(`&#x0*${icon.codepoint};`, "i").test(node.text)) {
      issue(errors, "ICON_GLYPH_MISMATCH", `Icon ${iconName} does not contain its pinned Harmony glyph`, node.nodeId)
    }
    if (!hasMeaningfulText(node.text)) issue(errors, "ICON_GLYPH_MISSING", `Icon ${iconName} was not materialized`, node.nodeId)
  }
  if (node.component === "tabs" && !/^\d+$/.test(node.attrs["data-index"] ?? "")) issue(errors, "TABS_INDEX_INVALID", "tabs requires a non-negative integer data-index", node.nodeId)
}

const outputRuntimePath = join(dirname(target), "assets", "harmony-runtime.css")
if (!existsSync(outputRuntimePath)) {
  issue(errors, "RUNTIME_FILE_MISSING", `Missing runtime file: ${outputRuntimePath}`)
} else if (readFileSync(outputRuntimePath, "utf8") !== bundledRuntimeCss) {
  issue(errors, "RUNTIME_FILE_MISMATCH", "Output runtime does not match the Skill's pinned harmony-runtime.css")
}
for (const fontName of ["HarmonyOS-Regular.woff2", "HarmonyOS-Medium.woff2", "HarmonyOS-Bold.woff2", "HMSymbolVF.ttf"]) {
  const fontPath = join(dirname(target), "assets", "fonts", fontName)
  if (!existsSync(fontPath)) issue(errors, "FONT_FILE_MISSING", `Missing font file: ${fontPath}`)
}

const primaryButtons = componentNodes.filter((node) => node.component === "button" && classesFor(node).has("bg-ui-primary"))
if (primaryButtons.length > 1) {
  issue(warnings, "PRIMARY_ACTION_MULTIPLE", `Page has ${primaryButtons.length} primary buttons; keep one dominant action`)
}
if (componentNodes.length > 90) issue(warnings, "COMPONENT_COUNT_HIGH", `Page has ${componentNodes.length} annotated components; consider simplifying it`)
const result = {
  ok: errors.length === 0,
  target,
  summary: {
    components: componentNodes.length,
    nodeIds: nodeIds.size,
    errors: errors.length,
    warnings: warnings.length,
  },
  errors,
  warnings,
}

if (jsonOutput) {
  console.log(JSON.stringify(result, null, 2))
} else {
  console.log(result.ok ? "PASS harmony-html validation" : "FAIL harmony-html validation")
  console.log(`components=${result.summary.components} nodeIds=${result.summary.nodeIds} errors=${errors.length} warnings=${warnings.length}`)
  for (const item of [...errors, ...warnings]) {
    const suffix = item.nodeId ? ` [${item.nodeId}]` : ""
    console.log(`${errors.includes(item) ? "ERROR" : "WARN"} ${item.code}${suffix}: ${item.message}`)
  }
}

process.exit(result.ok ? 0 : 1)
