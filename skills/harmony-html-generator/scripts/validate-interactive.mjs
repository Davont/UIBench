#!/usr/bin/env node

import { randomUUID } from "node:crypto"
import { spawnSync } from "node:child_process"
import {
  existsSync,
  lstatSync,
  readFileSync,
  unlinkSync,
  writeFileSync,
} from "node:fs"
import { basename, dirname, join, resolve } from "node:path"
import { TextDecoder } from "node:util"
import { fileURLToPath } from "node:url"

const MAX_SCRIPT_BYTES = 256 * 1024

const args = process.argv.slice(2)
const jsonOutput = args.includes("--json")
const positional = args.filter((arg) => arg !== "--json")
if (positional.length !== 1 || positional[0].startsWith("--")) {
  console.error("Usage: node validate-interactive.mjs <index.html> [--json]")
  process.exit(2)
}

const target = resolve(positional[0])
if (!existsSync(target) || !lstatSync(target).isFile() || lstatSync(target).isSymbolicLink()) {
  console.error(`Target must be a regular file: ${target}`)
  process.exit(2)
}

const html = readFileSync(target, "utf8")
const outputDir = dirname(target)
const expectedScriptPath = join(outputDir, "assets", "app.js")
const errors = []
const warnings = []
let staticResult = null
let selectorCount = 0

function issue(collection, code, message, nodeId = null, source = "interaction") {
  collection.push({ code, message, nodeId, source })
}

function parseAttributes(source) {
  const attrs = []
  const pattern = /([^\s=/>]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+)))?/g
  let match
  while ((match = pattern.exec(source)) !== null) {
    const name = match[1].toLowerCase()
    if (name === "/") continue
    attrs.push({ name, value: match[2] ?? match[3] ?? match[4] ?? "" })
  }
  return attrs
}

function attributesByName(attributes) {
  const result = new Map()
  for (const attribute of attributes) {
    if (!result.has(attribute.name)) result.set(attribute.name, [])
    result.get(attribute.name).push(attribute.value)
  }
  return result
}

function parseElements(source) {
  const elements = []
  const pattern = /<([a-z][a-z0-9:-]*)\b([^<>]*?)>/gi
  let match
  while ((match = pattern.exec(source)) !== null) {
    if (match[0].startsWith("</")) continue
    const attributes = parseAttributes(match[2] ?? "")
    const attrs = attributesByName(attributes)
    elements.push({
      tag: match[1].toLowerCase(),
      attributes,
      attrs,
      nodeId: attrs.get("data-node-id")?.[0] ?? null,
    })
  }
  return elements
}

const elements = parseElements(html)
const nodeIdCounts = new Map()
const idCounts = new Map()
const actions = new Set()
const classes = new Set()
for (const element of elements) {
  const nodeId = element.attrs.get("data-node-id")?.[0]
  if (nodeId) nodeIdCounts.set(nodeId, (nodeIdCounts.get(nodeId) ?? 0) + 1)
  const id = element.attrs.get("id")?.[0]
  if (id) idCounts.set(id, (idCounts.get(id) ?? 0) + 1)
  const action = element.attrs.get("data-action")?.[0]
  if (action) actions.add(action)
  for (const className of (element.attrs.get("class")?.[0] ?? "").split(/\s+/).filter(Boolean)) {
    classes.add(className)
  }
  for (const attribute of element.attributes) {
    if (/^on[a-z0-9_-]+$/i.test(attribute.name)) {
      issue(
        errors,
        "INLINE_EVENT_HANDLER_FORBIDDEN",
        `Inline event handler ${attribute.name} is forbidden`,
        element.nodeId,
      )
    }
  }
  if (element.attrs.has("data-action") && !element.nodeId) {
    issue(errors, "ACTION_NODE_ID_MISSING", "Every data-action hook requires data-node-id")
  }
  if (element.attrs.has("data-action") && !action?.trim()) {
    issue(errors, "ACTION_VALUE_INVALID", "data-action must not be empty", element.nodeId)
  } else if (action && !/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(action)) {
    issue(errors, "ACTION_VALUE_INVALID", `Invalid data-action value: ${action}`, element.nodeId)
  }
  const targetNodeId = element.attrs.get("data-target")?.[0]
  if (element.attrs.has("data-target")) {
    const count = nodeIdCounts.get(targetNodeId) ?? 0
    // Counts are finalized below; defer reporting until every element is known.
    element.targetNodeId = targetNodeId
    element.targetCountAtParse = count
  }
}

for (const element of elements) {
  if (!Object.hasOwn(element, "targetNodeId")) continue
  const value = element.targetNodeId
  const count = nodeIdCounts.get(value) ?? 0
  if (!value || count !== 1) {
    issue(
      errors,
      "DATA_TARGET_INVALID",
      value
        ? `data-target must identify exactly one data-node-id; found ${count}: ${value}`
        : "data-target must not be empty",
      element.nodeId,
    )
  }
}

const scriptOpenings = [...html.matchAll(/<script\b/gi)]
const scriptPattern = /<script\b([^>]*)>([\s\S]*?)<\/script\s*>/gi
const scripts = [...html.matchAll(scriptPattern)]
if (scriptOpenings.length !== 1 || scripts.length !== 1) {
  issue(
    errors,
    "SCRIPT_COUNT_INVALID",
    `Expected exactly one complete script element, found ${scriptOpenings.length} opening tag(s) and ${scripts.length} complete element(s)`,
  )
}

let strippedHtml = null
let scriptContractValid = false
if (scriptOpenings.length === 1 && scripts.length === 1) {
  const script = scripts[0]
  const attributes = parseAttributes(script[1] ?? "")
  const attrs = attributesByName(attributes)
  const allowedNames = new Set(["src", "defer"])
  const unexpectedNames = [...attrs.keys()].filter((name) => !allowedNames.has(name))
  const srcValues = attrs.get("src") ?? []
  const deferValues = attrs.get("defer") ?? []

  if (unexpectedNames.length > 0 || srcValues.length !== 1 || deferValues.length !== 1) {
    issue(
      errors,
      "SCRIPT_ATTRIBUTES_INVALID",
      'The only allowed script form is <script src="assets/app.js" defer></script>',
    )
  }
  if (srcValues.length !== 1 || srcValues[0] !== "assets/app.js") {
    issue(errors, "SCRIPT_SRC_INVALID", "Script src must be exactly assets/app.js")
  }
  if (deferValues.length !== 1 || !new Set(["", "defer"]).has(deferValues[0].toLowerCase())) {
    issue(errors, "SCRIPT_DEFER_INVALID", "The app script requires the boolean defer attribute")
  }
  if ((script[2] ?? "").trim()) {
    issue(errors, "SCRIPT_INLINE_FORBIDDEN", "The app script element must not contain inline JavaScript")
  }

  scriptContractValid = unexpectedNames.length === 0
    && srcValues.length === 1
    && srcValues[0] === "assets/app.js"
    && deferValues.length === 1
    && new Set(["", "defer"]).has(deferValues[0].toLowerCase())
    && !(script[2] ?? "").trim()
  strippedHtml = `${html.slice(0, script.index)}${html.slice(script.index + script[0].length)}`
}

function runStaticValidation(source) {
  const scriptDir = dirname(fileURLToPath(import.meta.url))
  const validator = join(scriptDir, "validate-html.mjs")
  const temporaryTarget = join(
    outputDir,
    `.${basename(target)}.static-${process.pid}-${randomUUID()}.html`,
  )
  try {
    writeFileSync(temporaryTarget, source, { encoding: "utf8", flag: "wx", mode: 0o600 })
    const result = spawnSync(process.execPath, [validator, temporaryTarget, "--json"], {
      encoding: "utf8",
      maxBuffer: 4 * 1024 * 1024,
    })
    if (result.error) throw result.error
    let parsed
    try {
      parsed = JSON.parse(result.stdout)
    } catch {
      const diagnostic = [result.stdout, result.stderr].filter(Boolean).join(" ").replace(/\s+/g, " ").slice(0, 1_000)
      throw new Error(`Static validator returned invalid JSON: ${diagnostic}`)
    }
    return parsed
  } finally {
    if (existsSync(temporaryTarget)) unlinkSync(temporaryTarget)
  }
}

if (strippedHtml !== null) {
  try {
    staticResult = runStaticValidation(strippedHtml)
    for (const item of staticResult.errors ?? []) {
      issue(errors, item.code, item.message, item.nodeId ?? null, "static")
    }
    for (const item of staticResult.warnings ?? []) {
      issue(warnings, item.code, item.message, item.nodeId ?? null, "static")
    }
  } catch (error) {
    issue(errors, "STATIC_VALIDATOR_FAILED", String(error?.message ?? error), null, "static")
  }
}

function maskNonCode(source) {
  const output = source.split("")
  const literals = []
  const stack = [{ kind: "code", templateExpression: false, braceDepth: 0 }]
  let index = 0

  while (index < source.length) {
    const state = stack.at(-1)
    const char = source[index]
    const next = source[index + 1]

    if (state.kind === "code") {
      if (state.templateExpression && char === "}") {
        if (state.braceDepth === 0) {
          output[index] = " "
          stack.pop()
          const template = stack.at(-1)
          if (template?.kind === "template") template.segmentStart = index + 1
          index += 1
          continue
        }
        state.braceDepth -= 1
        index += 1
        continue
      }
      if (state.templateExpression && char === "{") {
        state.braceDepth += 1
        index += 1
        continue
      }
      if (char === "'" || char === '"') {
        output[index] = " "
        stack.push({ kind: "string", quote: char, start: index })
        index += 1
        continue
      }
      if (char === "`") {
        output[index] = " "
        stack.push({ kind: "template", segmentStart: index + 1 })
        index += 1
        continue
      }
      if (char === "/" && next === "/") {
        output[index] = " "
        output[index + 1] = " "
        stack.push({ kind: "line-comment" })
        index += 2
        continue
      }
      if (char === "/" && next === "*") {
        output[index] = " "
        output[index + 1] = " "
        stack.push({ kind: "block-comment" })
        index += 2
        continue
      }
      index += 1
      continue
    }

    if (state.kind === "string") {
      output[index] = " "
      if (char === "\\") {
        if (index + 1 < output.length) output[index + 1] = " "
        index += 2
      } else if (char === state.quote) {
        const literal = decodeSimpleJsString(source, state.start)
        literals.push(literal?.value ?? source.slice(state.start + 1, index))
        stack.pop()
        index += 1
      } else {
        index += 1
      }
      continue
    }

    if (state.kind === "line-comment") {
      if (char === "\n" || char === "\r") {
        stack.pop()
        index += 1
      } else {
        output[index] = " "
        index += 1
      }
      continue
    }

    if (state.kind === "block-comment") {
      output[index] = " "
      if (char === "*" && next === "/") {
        output[index + 1] = " "
        stack.pop()
        index += 2
      } else {
        index += 1
      }
      continue
    }

    // Template text is data. Preserve expressions so dangerous APIs inside ${...}
    // are still analyzed.
    output[index] = " "
    if (char === "\\") {
      if (index + 1 < output.length) output[index + 1] = " "
      index += 2
    } else if (char === "`") {
      literals.push(source.slice(state.segmentStart, index))
      stack.pop()
      index += 1
    } else if (char === "$" && next === "{") {
      literals.push(source.slice(state.segmentStart, index))
      output[index + 1] = " "
      stack.push({ kind: "code", templateExpression: true, braceDepth: 0 })
      index += 2
    } else {
      index += 1
    }
  }

  return { masked: output.join(""), literals }
}

function decodeSimpleJsString(source, start) {
  const quote = source[start]
  if (quote !== "'" && quote !== '"') return null
  let value = ""
  let index = start + 1
  while (index < source.length) {
    const char = source[index]
    if (char === quote) return { value, end: index + 1 }
    if (char === "\n" || char === "\r") return null
    if (char !== "\\") {
      value += char
      index += 1
      continue
    }
    const escaped = source[index + 1]
    if (escaped === undefined) return null
    const simpleEscapes = {
      "\\": "\\",
      "/": "/",
      "'": "'",
      '"': '"',
      n: "\n",
      r: "\r",
      t: "\t",
      b: "\b",
      f: "\f",
      v: "\v",
      0: "\0",
    }
    if (!Object.hasOwn(simpleEscapes, escaped)) return null
    value += simpleEscapes[escaped]
    index += 2
  }
  return null
}

function parseSingleLiteralArgument(source, callEnd) {
  let index = callEnd
  while (/\s/.test(source[index] ?? "")) index += 1
  const literal = decodeSimpleJsString(source, index)
  if (!literal) return null
  index = literal.end
  while (/\s/.test(source[index] ?? "")) index += 1
  if (source[index] !== ")") return null
  return literal.value
}

function validateSelector(selector) {
  const value = selector.trim()
  if (value === "[data-node-id]") return nodeIdCounts.size > 0 ? null : "target-missing"
  if (value === "[data-action]") return actions.size > 0 ? null : "target-missing"

  const idSelector = value.match(/^#([a-zA-Z][a-zA-Z0-9_.:-]*)$/)
  if (idSelector) return (idCounts.get(idSelector[1]) ?? 0) === 1 ? null : "target-missing"

  const attributeSelector = value.match(/^\[(data-node-id|data-action)\s*=\s*(["'])([^"']+)\2\]$/)
  if (attributeSelector) {
    const [, name, , expected] = attributeSelector
    const exists = name === "data-node-id"
      ? (nodeIdCounts.get(expected) ?? 0) === 1
      : actions.has(expected)
    return exists ? null : "target-missing"
  }
  return "unsupported"
}

function validateDomLookups(source, masked) {
  const calls = /\b(querySelectorAll|querySelector|closest|matches|getElementById)\s*\(/g
  const lookupMentions = [...masked.matchAll(/\b(?:querySelectorAll|querySelector|closest|matches|getElementById)\b/g)].length
  let directCalls = 0
  let match
  while ((match = calls.exec(masked)) !== null) {
    directCalls += 1
    selectorCount += 1
    const method = match[1]
    const literal = parseSingleLiteralArgument(source, match.index + match[0].length)
    if (literal === null) {
      issue(errors, "DOM_SELECTOR_DYNAMIC", `${method} requires one static string literal argument`)
      continue
    }
    if (method === "getElementById") {
      const count = idCounts.get(literal) ?? 0
      if (count !== 1) {
        issue(
          errors,
          "DOM_SELECTOR_TARGET_MISSING",
          `getElementById must identify exactly one declared target; found ${count}: ${literal}`,
        )
      }
      continue
    }
    const selectorStatus = validateSelector(literal)
    if (selectorStatus === "target-missing") {
      issue(errors, "DOM_SELECTOR_TARGET_MISSING", `Selector has no declared target: ${literal}`)
    } else if (selectorStatus === "unsupported") {
      issue(
        errors,
        "DOM_SELECTOR_UNSUPPORTED",
        `Selector must use an existing #id, data-node-id, or data-action hook: ${literal}`,
      )
    }
  }

  if (lookupMentions !== directCalls) {
    issue(
      errors,
      "DOM_LOOKUP_FORBIDDEN",
      "DOM lookup methods must be called directly with a static string literal",
    )
  }

  const computedLookup = /\[\s*(["'])(?:querySelectorAll|querySelector|closest|matches|getElementById)\1\s*\]/
  if (computedLookup.test(source)) {
    issue(errors, "DOM_LOOKUP_FORBIDDEN", "Computed DOM lookup method access is forbidden")
  }

  const unsupportedLookups = /\b(getElementsByClassName|getElementsByTagName|getElementsByName|evaluate)\s*\(/g
  while ((match = unsupportedLookups.exec(masked)) !== null) {
    issue(errors, "DOM_LOOKUP_FORBIDDEN", `${match[1]} is not an approved static DOM lookup`)
  }
}

function validateClassList(source, masked) {
  const calls = /\.\s*classList\s*\.\s*(add|remove|toggle|replace)\s*\(/g
  let match
  while ((match = calls.exec(masked)) !== null) {
    const method = match[1]
    let index = match.index + match[0].length
    const requiredLiterals = method === "replace" ? 2 : 1
    for (let literalIndex = 0; literalIndex < requiredLiterals; literalIndex += 1) {
      while (/\s/.test(source[index] ?? "")) index += 1
      const literal = decodeSimpleJsString(source, index)
      if (!literal) {
        issue(errors, "CLASS_NAME_DYNAMIC", `classList.${method} requires static class names`)
        break
      }
      if (!classes.has(literal.value)) {
        issue(errors, "CLASS_NAME_UNDECLARED", `Class is not declared in the static HTML: ${literal.value}`)
      }
      index = literal.end
      while (/\s/.test(source[index] ?? "")) index += 1
      if (literalIndex + 1 < requiredLiterals) {
        if (source[index] !== ",") {
          issue(errors, "CLASS_NAME_DYNAMIC", `classList.${method} requires static class names`)
          break
        }
        index += 1
      }
    }
  }
}

function validateJavaScript(source) {
  const { masked, literals } = maskNonCode(source)
  const dangerousRules = [
    ["JS_NETWORK_API_FORBIDDEN", "fetch", /\bfetch\b/],
    ["JS_NETWORK_API_FORBIDDEN", "XMLHttpRequest", /\bXMLHttpRequest\b/],
    ["JS_NETWORK_API_FORBIDDEN", "WebSocket", /\bWebSocket\b/],
    ["JS_NETWORK_API_FORBIDDEN", "EventSource", /\bEventSource\b/],
    ["JS_NETWORK_API_FORBIDDEN", "sendBeacon", /\bsendBeacon\b/],
    ["JS_DYNAMIC_CODE_FORBIDDEN", "eval", /\beval\b/],
    ["JS_DYNAMIC_CODE_FORBIDDEN", "Function constructor", /\bFunction\b/],
    ["JS_HTML_INJECTION_FORBIDDEN", "document.write", /\bdocument\s*\.\s*write(?:ln)?\b/],
    ["JS_HTML_INJECTION_FORBIDDEN", "innerHTML", /\.\s*innerHTML\b/],
    ["JS_HTML_INJECTION_FORBIDDEN", "outerHTML", /\.\s*outerHTML\b/],
    ["JS_HTML_INJECTION_FORBIDDEN", "insertAdjacentHTML", /\.\s*insertAdjacentHTML\b/],
    ["JS_DYNAMIC_IMPORT_FORBIDDEN", "import", /\bimport\b/],
    ["JS_STORAGE_FORBIDDEN", "localStorage", /\blocalStorage\b/],
    ["JS_STORAGE_FORBIDDEN", "sessionStorage", /\bsessionStorage\b/],
    ["JS_STORAGE_FORBIDDEN", "document.cookie", /\bdocument\s*\.\s*cookie\b/],
    ["JS_STORAGE_FORBIDDEN", "indexedDB", /\bindexedDB\b/],
    ["JS_STORAGE_FORBIDDEN", "Cache API", /\bcaches\s*\./],
    ["JS_DOM_MUTATION_FORBIDDEN", "DOM creation", /\.\s*(?:createElement|createElementNS|createTextNode|createDocumentFragment|cloneNode)\s*\(/],
    ["JS_DOM_MUTATION_FORBIDDEN", "DOM insertion or removal", /\.\s*(?:appendChild|insertBefore|replaceChild|replaceChildren|removeChild|insertAdjacentElement|insertAdjacentText|append|prepend|before|after|replaceWith)\s*\(/],
    ["JS_EXTERNAL_EFFECT_FORBIDDEN", "window.open", /\bwindow\s*\.\s*open\s*\(/],
    ["JS_EXTERNAL_EFFECT_FORBIDDEN", "navigation", /\b(?:location\s*\.\s*(?:assign|replace|reload)|history\s*\.\s*(?:pushState|replaceState|back|forward|go))\s*\(/],
    ["JS_EXTERNAL_EFFECT_FORBIDDEN", "navigation assignment", /\b(?:(?:window|document|globalThis)\s*\.\s*)?location(?:\s*\.\s*href)?\s*(?:=|\+=|\?\?=|\|\|=|&&=)/],
    ["JS_EXTERNAL_EFFECT_FORBIDDEN", "worker", /\b(?:Worker|SharedWorker)\s*\(/],
    ["JS_EXTERNAL_EFFECT_FORBIDDEN", "form submission", /\.\s*(?:submit|requestSubmit)\s*\(/],
    ["JS_EXTERNAL_EFFECT_FORBIDDEN", "clipboard", /\bclipboard\b/],
    ["JS_EXTERNAL_EFFECT_FORBIDDEN", "Notification", /\bNotification\b/],
    ["JS_EXTERNAL_EFFECT_FORBIDDEN", "geolocation", /\bgeolocation\b/],
    ["JS_EXTERNAL_EFFECT_FORBIDDEN", "mediaDevices", /\bmediaDevices\b/],
  ]
  for (const [code, label, pattern] of dangerousRules) {
    if (pattern.test(masked)) issue(errors, code, `${label} is not allowed in interactive artifacts`)
  }

  for (const literal of literals) {
    const value = literal.trim()
    if (/(?:https?|wss?):\/\//i.test(value) || value.startsWith("//")) {
      issue(errors, "JS_REMOTE_URL_FORBIDDEN", `Remote URL is not allowed in JavaScript strings: ${value.slice(0, 160)}`)
    }
  }

  const removeCalls = /\.\s*remove\s*\(/g
  let removeCall
  while ((removeCall = removeCalls.exec(masked)) !== null) {
    const prefix = masked.slice(Math.max(0, removeCall.index - 80), removeCall.index)
    if (!/\.\s*classList\s*$/.test(prefix)) {
      issue(errors, "JS_DOM_MUTATION_FORBIDDEN", "Removing a predeclared DOM node is forbidden")
    }
  }

  if (/\.\s*on[a-z][a-z0-9]*\s*=/i.test(masked)
      || /\[\s*(["'])on[a-z][a-z0-9]*\1\s*\]\s*=/i.test(source)) {
    issue(
      errors,
      "JS_EVENT_HANDLER_PROPERTY_FORBIDDEN",
      "Bind events with addEventListener instead of assigning on* properties",
    )
  }
  if (!/\.\s*addEventListener\s*\(/.test(masked)) {
    issue(errors, "JS_EVENT_LISTENER_MISSING", "Interactive JavaScript requires addEventListener")
  }

  // Reject the common bracket-notation escape for named dangerous properties.
  const computedDangerous = /\[\s*(["'])(?:fetch|XMLHttpRequest|WebSocket|EventSource|sendBeacon|eval|Function|write|writeln|innerHTML|outerHTML|insertAdjacentHTML|localStorage|sessionStorage|createElement|createElementNS|createTextNode|createDocumentFragment|cloneNode|appendChild|insertBefore|replaceChild|replaceChildren|removeChild|insertAdjacentElement|insertAdjacentText|append|prepend|before|after|replaceWith|remove)\1\s*\]/
  if (computedDangerous.test(source)) {
    issue(errors, "JS_COMPUTED_API_FORBIDDEN", "Computed access to a dangerous API is forbidden")
  }

  const selectorsBefore = selectorCount
  validateDomLookups(source, masked)
  if (selectorCount === selectorsBefore) {
    issue(
      errors,
      "DOM_LOOKUP_MISSING",
      "Interactive JavaScript requires at least one approved static DOM lookup",
    )
  }
  validateClassList(source, masked)
}

if (scriptContractValid) {
  if (!existsSync(expectedScriptPath)) {
    issue(errors, "SCRIPT_FILE_MISSING", "Referenced local script does not exist: assets/app.js")
  } else {
    const scriptStat = lstatSync(expectedScriptPath)
    if (scriptStat.isSymbolicLink() || !scriptStat.isFile()) {
      issue(errors, "SCRIPT_FILE_INVALID", "assets/app.js must be a regular file inside the output directory")
    } else if (scriptStat.size > MAX_SCRIPT_BYTES) {
      issue(
        errors,
        "SCRIPT_FILE_TOO_LARGE",
        `assets/app.js exceeds the ${MAX_SCRIPT_BYTES}-byte limit`,
      )
    } else {
      let javascript = null
      try {
        javascript = new TextDecoder("utf-8", { fatal: true }).decode(readFileSync(expectedScriptPath))
      } catch {
        issue(errors, "SCRIPT_ENCODING_INVALID", "assets/app.js must be valid UTF-8")
      }
      if (javascript !== null) {
        if (!javascript.trim() || javascript.includes("\0")) {
          issue(errors, "SCRIPT_CONTENT_INVALID", "assets/app.js must be non-empty UTF-8 without NUL characters")
        } else {
          validateJavaScript(javascript)
          const syntax = spawnSync(process.execPath, ["--check", expectedScriptPath], {
            encoding: "utf8",
            maxBuffer: 2 * 1024 * 1024,
          })
          if (syntax.error || syntax.status !== 0) {
            const detail = [syntax.stdout, syntax.stderr]
              .filter(Boolean)
              .join(" ")
              .replace(/\s+/g, " ")
              .trim()
              .slice(0, 1_000)
            issue(errors, "JS_SYNTAX_INVALID", detail || "assets/app.js contains invalid JavaScript")
          }
        }
      }
    }
  }
}

const staticErrors = errors.filter((item) => item.source === "static").length
const interactionErrors = errors.length - staticErrors
const result = {
  ok: errors.length === 0,
  target,
  script: expectedScriptPath,
  summary: {
    staticErrors,
    interactionErrors,
    errors: errors.length,
    warnings: warnings.length,
    selectors: selectorCount,
  },
  errors,
  warnings,
  staticSummary: staticResult?.summary ?? null,
}

if (jsonOutput) {
  console.log(JSON.stringify(result, null, 2))
} else {
  console.log(result.ok ? "PASS harmony-html interaction validation" : "FAIL harmony-html interaction validation")
  console.log(
    `staticErrors=${staticErrors} interactionErrors=${interactionErrors} errors=${errors.length} warnings=${warnings.length} selectors=${selectorCount}`,
  )
  for (const item of [...errors, ...warnings]) {
    const suffix = item.nodeId ? ` [${item.nodeId}]` : ""
    console.log(`${errors.includes(item) ? "ERROR" : "WARN"} ${item.code}${suffix}: ${item.message}`)
  }
}

process.exit(result.ok ? 0 : 1)
