#!/usr/bin/env node

import {
  existsSync,
  mkdtempSync,
  readdirSync,
  readFileSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs"
import { tmpdir } from "node:os"
import { basename, dirname, extname, join, relative, resolve, sep } from "node:path"
import { spawnSync } from "node:child_process"
import { fileURLToPath } from "node:url"

import { parse as babelParse, traverse } from "./babel.mjs"

const args = process.argv.slice(2)
const targetArg = args.find((arg) => !arg.startsWith("--"))
const pageBuildRequested = args.includes("--page-build-requested")
const standaloneMode = args.includes("--standalone")

if (!targetArg) {
  console.error(
    "Usage: node validate-page-artifact.mjs <target-dir-or-html> [--page-build-requested] [--standalone]",
  )
  process.exit(2)
}

const targetPath = resolve(targetArg)

if (!existsSync(targetPath)) {
  console.error(`Target does not exist: ${targetPath}`)
  process.exit(2)
}

const targetStats = statSync(targetPath)
if (standaloneMode && (!targetStats.isFile() || extname(targetPath) !== ".html")) {
  console.error(`Standalone target must be an HTML file: ${targetPath}`)
  process.exit(2)
}
if (!standaloneMode && !targetStats.isDirectory()) {
  console.error(`Design-system target must be a directory: ${targetPath}`)
  process.exit(2)
}

const targetDir = standaloneMode ? dirname(targetPath) : targetPath

const sourceExtensions = new Set([".ts", ".tsx", ".js", ".jsx"])
const ignoredDirs = new Set(["node_modules", ".git", "dist", "storybook-static"])
const errors = []
const warnings = []
const notes = []

function collectArtifactFiles(dir) {
  const files = []

  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (entry.isDirectory() && ignoredDirs.has(entry.name)) continue

    const entryPath = join(dir, entry.name)
    if (entry.isDirectory()) {
      files.push(...collectArtifactFiles(entryPath))
    } else if (entry.isFile()) {
      files.push(entryPath)
    }
  }

  return files
}

function countMatches(text, pattern) {
  return text.match(pattern)?.length ?? 0
}

function displayPath(file) {
  return relative(process.cwd(), file) || basename(file)
}

// ---------------------------------------------------------------------------
// Template-required-components manifest. Loaded from
// references/template-required-components.json so adding a new page template
// is one JSON edit instead of touching validator code. Each entry maps a
// top-level template component name to the registered React components its
// rendered tree must keep. Validator consults this for the "template-required
// components preservation" check so swapping shells does not leave a coverage
// gap (e.g. forgetting to require FloatingTitleBar just because a different
// shell template is in use).
// ---------------------------------------------------------------------------

// When the manifest itself is missing, collectJsxStats still runs (a missing
// manifest is not a syntax error) but needs a seed of template names so the
// hand-written fallback further down — guarded by `!templateManifest.ok` — can
// still see the shell it knows how to check. Keep this in sync with the names
// that fallback handles.
const LEGACY_FALLBACK_TEMPLATE_NAMES = new Set(["MobilePhoneShellTemplatePage"])

function loadTemplateManifest() {
  const scriptDir = resolve(fileURLToPath(new URL(".", import.meta.url)))
  const manifestPath = join(scriptDir, "..", "references", "template-required-components.json")
  if (!existsSync(manifestPath)) {
    return { ok: false, path: manifestPath, templates: {}, recognizedNames: new Set(), alwaysRequired: [] }
  }
  try {
    const data = JSON.parse(readFileSync(manifestPath, "utf8"))
    const templates = data.templates ?? {}
    const recognizedNames = new Set(Object.keys(templates))
    return { ok: true, path: manifestPath, templates, recognizedNames, alwaysRequired: data["always-required-jsx"] ?? [] }
  } catch (error) {
    return {
      ok: false,
      path: manifestPath,
      error: error instanceof Error ? error.message : String(error),
      templates: {},
      recognizedNames: new Set(),
      alwaysRequired: [],
    }
  }
}

// ---------------------------------------------------------------------------
// Babel-based JSX inspection. The previous regex-based props extractor
// (e.g. /<MobilePhoneShellTemplatePage\b([\s\S]*?)(?:\/>|>)/g) was unable to
// distinguish a JSX tag close `>` from `>` inside inline arrow functions
// (`onClick={() => …}`), string literals, JSX children, generics, or comparison
// operators — causing false negatives such as "secondary should explicitly
// declare showFloatingTab={false}" appearing even when the prop was declared.
// Parsing with @babel/parser and walking the AST removes that ambiguity.
// ---------------------------------------------------------------------------
function parseSourceAsModule(text) {
  try {
    return babelParse(text, {
      sourceType: "module",
      plugins: ["jsx", "typescript"],
      errorRecovery: false,
    })
  } catch {
    return null
  }
}

function readJsxStringAttribute(attr) {
  if (!attr || attr.type !== "JSXAttribute") return undefined
  const value = attr.value
  if (!value) return ""
  if (value.type === "StringLiteral") return value.value
  if (value.type === "Literal") return value.value
  if (value.type === "JSXExpressionContainer") {
    const expr = value.expression
    if (expr.type === "BooleanLiteral") return String(expr.value)
    if (expr.type === "NumericLiteral") return String(expr.value)
    if (expr.type === "StringLiteral" || expr.type === "Literal") return expr.value
    return "__expr__"
  }
  return undefined
}

function getJsxElementName(nameNode) {
  if (!nameNode) return null
  if (nameNode.type === "JSXIdentifier") return nameNode.name
  if (nameNode.type === "JSXMemberExpression") {
    const parts = []
    let node = nameNode
    while (node && node.type === "JSXMemberExpression") {
      parts.unshift(node.property.name)
      node = node.object
    }
    if (node && node.type === "JSXIdentifier") parts.unshift(node.name)
    return parts.join(".")
  }
  return null
}

// Set of recognized template-component names. Populated from the
// references/template-required-components.json manifest; populateTemplateStack
// walks function declarations of these names so we can skip their bodies when
// counting JSX usages (in standalone mode the template implementation is
// inlined alongside the call site, so its internal JSX would otherwise be
// double-counted).
function collectJsxStats(text, recognizedTemplateNames) {
  const ast = parseSourceAsModule(text)
  if (!ast) {
    return {
      ok: false,
      templateUsageProps: [],
      jsxElementNames: new Map(),
    }
  }

  const templateUsageProps = []
  // Map of element-local-name -> count of JSXOpeningElement occurrences.
  const jsxElementNames = new Map()
  // Stack of template function definitions we are currently inside, paired with
  // their scope depth so we know when to exit. Each entry tracks whether the
  // current path is inside THAT specific template's implementation body.
  const templateScopeStack = []

  traverse(ast, {
    enter(path) {
      if (
        path.isFunctionDeclaration() &&
        path.node.id &&
        recognizedTemplateNames.has(path.node.id.name)
      ) {
        templateScopeStack.push({
          name: path.node.id.name,
          depth: path.scope.depth,
        })
      }
      if (path.isJSXOpeningElement()) {
        const name = getJsxElementName(path.node.name)
        if (name) {
          const local = name.split(".").pop()
          jsxElementNames.set(local, (jsxElementNames.get(local) ?? 0) + 1)
          if (
            recognizedTemplateNames.has(local) &&
            !templateScopeStack.some((entry) => entry.name === local)
          ) {
            const props = {}
            for (const attr of path.node.attributes) {
              if (attr.type !== "JSXAttribute" || !attr.name) continue
              if (attr.name.type !== "JSXIdentifier") continue
              props[attr.name.name] = readJsxStringAttribute(attr)
            }
            templateUsageProps.push({ name: local, props })
          }
        }
      }
    },
    exit(path) {
      if (
        path.isFunctionDeclaration() &&
        path.node.id &&
        recognizedTemplateNames.has(path.node.id.name)
      ) {
        for (let i = templateScopeStack.length - 1; i >= 0; i -= 1) {
          if (templateScopeStack[i].depth === path.scope.depth) {
            templateScopeStack.splice(i, 1)
            break
          }
        }
      }
    },
  })

  return { ok: true, templateUsageProps, jsxElementNames }
}

const artifactFiles = standaloneMode ? [targetPath] : collectArtifactFiles(targetDir)
const files = artifactFiles.filter((file) => sourceExtensions.has(extname(file)))
let sourceFiles = files.filter(
  (file) =>
    !/\.stories\.[jt]sx?$/.test(file) &&
    !/\.(test|spec)\.[jt]sx?$/.test(file) &&
    !/(^|\/)(entry|c2d-prerender)\.[jt]sx?$/.test(file),
)
const storyFiles = files.filter((file) => /\.stories\.[jt]sx?$/.test(file))
const fileText = new Map(files.map((file) => [file, readFileSync(file, "utf8")]))

const pageTsxScriptPattern =
  /<script\b(?=[^>]*\bid=["']page-tsx["'])(?=[^>]*\btype=["']text\/plain["'])[^>]*>([\s\S]*?)<\/script\s*>/gi

function extractPageTsxScripts(html) {
  return [...html.matchAll(pageTsxScriptPattern)].map((match) => ({
    source: match[1],
  }))
}

function maskStandaloneTemplate(html) {
  return html
    .replace(/<title>[\s\S]*?<\/title>/i, "<title>__PAGE_TITLE__</title>")
    .replace(
      pageTsxScriptPattern,
      '<script type="text/plain" id="page-tsx">__PAGE_TSX__</script>',
    )
}

function collectImportSources(text) {
  const sources = []
  const staticImportPattern =
    /\bimport\s+(?:type\s+)?(?:[\s\S]*?\s+from\s+)?["']([^"']+)["']/g
  const dynamicImportPattern = /\bimport\s*\(\s*["']([^"']+)["']\s*\)/g
  const requirePattern = /\brequire\s*\(\s*["']([^"']+)["']\s*\)/g

  for (const match of text.matchAll(staticImportPattern)) {
    sources.push({ kind: "import", source: match[1] })
  }
  for (const match of text.matchAll(dynamicImportPattern)) {
    sources.push({ kind: "dynamic import", source: match[1] })
  }
  for (const match of text.matchAll(requirePattern)) {
    sources.push({ kind: "require", source: match[1] })
  }
  return sources
}

function collectNamedValueImports(text, source) {
  return collectNamedValueImportBindings(text, source).map(({ imported }) => imported)
}

function collectNamedValueImportBindings(text, source) {
  const escaped = source.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
  const pattern = new RegExp(
    `\\bimport\\s*\\{([\\s\\S]*?)\\}\\s*from\\s*["']${escaped}["']`,
    "g",
  )
  const bindings = []
  for (const match of text.matchAll(pattern)) {
    for (const specifier of match[1].split(",")) {
      const normalized = specifier.trim()
      if (!normalized || normalized.startsWith("type ")) continue
      const [imported, alias] = normalized.split(/\s+as\s+/).map((part) => part.trim())
      if (imported) bindings.push({ imported, local: alias || imported })
    }
  }
  return bindings
}

if (standaloneMode) {
  const standaloneHtmlFiles = artifactFiles.filter((file) => extname(file) === ".html")
  if (artifactFiles.length !== 1 || standaloneHtmlFiles.length !== 1) {
    errors.push(
      `standalone output must contain exactly one page .shadcn.html file; found ${artifactFiles.length} artifact file(s) and ${standaloneHtmlFiles.length} page .shadcn.html file(s)`,
    )
  }

  sourceFiles = []
  if (standaloneHtmlFiles.length === 1) {
    const htmlFile = standaloneHtmlFiles[0]
    const html = readFileSync(htmlFile, "utf8")
    const embeddedScripts = extractPageTsxScripts(html)
    const fileLabel = displayPath(htmlFile)

    if (!/^[a-z0-9]+(?:-[a-z0-9]+)*\.shadcn\.html$/.test(basename(htmlFile))) {
      errors.push(`${fileLabel}: standalone HTML filename must use kebab-case with .shadcn.html extension`)
    }

    if (embeddedScripts.length !== 1) {
      errors.push(
        `${fileLabel}: expected exactly one <script type="text/plain" id="page-tsx"> block; found ${embeddedScripts.length}`,
      )
    } else {
      const embeddedTsx = embeddedScripts[0].source
      if (!embeddedTsx.trim()) {
        errors.push(`${fileLabel}: embedded page TSX must not be empty`)
      } else {
        sourceFiles = [htmlFile]
        fileText.set(htmlFile, embeddedTsx)
      }
    }

    if (html.includes("// tsx 代码 生成位置")) {
      errors.push(`${fileLabel}: standalone TSX insertion marker was not replaced`)
    }

    const pageTitle = html.match(/<title>([\s\S]*?)<\/title>/i)?.[1]?.trim()
    if (!pageTitle || pageTitle === "Babel TSX 字符串模板") {
      errors.push(`${fileLabel}: standalone HTML title must use the actual page title`)
    }

    const scriptDir = resolve(fileURLToPath(new URL(".", import.meta.url)))
    const templatePath = resolve(
      scriptDir,
      "../babel-render-tsx/html-template/babel-string-template.html",
    )
    if (!existsSync(templatePath)) {
      errors.push(`standalone HTML template is missing: ${templatePath}`)
    } else {
      const template = readFileSync(templatePath, "utf8")
      if (maskStandaloneTemplate(html) !== maskStandaloneTemplate(template)) {
        errors.push(
          `${fileLabel}: standalone HTML shell must match the bundled template except for <title> and embedded TSX`,
        )
      }
    }
  }

  const vendorDir = resolve(targetDir, "..", "design-system-vendor")
  if (!existsSync(vendorDir) || !statSync(vendorDir).isDirectory()) {
    errors.push(
      `standalone shared vendor directory is missing beside the output directory: ${vendorDir}`,
    )
  }

  if (pageBuildRequested) {
    errors.push("standalone mode does not support page-build artifacts")
  }

  for (const file of sourceFiles) {
    const text = fileText.get(file)
    const fileLabel = displayPath(file)
    const imports = collectImportSources(text)

    for (const item of imports) {
      if (item.kind !== "import") {
        errors.push(
          `${fileLabel}: ${item.kind} is forbidden in standalone output (${item.source})`,
        )
      }
    }

    const reExportPattern =
      /\bexport\s+(?:type\s+)?(?:\*|\{[\s\S]*?\})\s+from\s+["']([^"']+)["']/g
    for (const match of text.matchAll(reExportPattern)) {
      errors.push(
        `${fileLabel}: re-export from "${match[1]}" is forbidden in standalone output`,
      )
    }

    const directHookImports = [
      ...collectNamedValueImports(text, "design-components"),
      ...collectNamedValueImports(text, "blocks-components"),
    ].filter((name) => /^use[A-Z0-9_]/.test(name))
    if (directHookImports.length) {
      errors.push(
        `${fileLabel}: import Hooks through React members, not named imports (${directHookImports.join(", ")})`,
      )
    }

    if (!/<style\b[^>]*>[\s\S]*<\/style>/.test(text)) {
      errors.push(
        `${fileLabel}: standalone output must render page styles with an inline <style> element`,
      )
    }

    if (/<(?:img|picture|source)\b/i.test(text)) {
      errors.push(`${fileLabel}: image elements are forbidden in standalone output`)
    }
    if (text.includes("__TEMPLATE_CSS__")) {
      errors.push(
        `${fileLabel}: standalone TSX still contains the "__TEMPLATE_CSS__" placeholder; rerun scaffold-standalone-html.mjs with --css-file <path-to-merged.css> so template-private CSS is substituted into the <style> block`,
      )
    }
    if (
      /\burl\s*\(/i.test(text) ||
      /\bimage-set\s*\(/i.test(text) ||
      /data:image\//i.test(text) ||
      /["'`][^"'`\n]+\.(?:avif|gif|jpe?g|png|svg|webp)(?:[?#][^"'`\n]*)?["'`]/i.test(text)
    ) {
      errors.push(`${fileLabel}: image references are forbidden in standalone output`)
    }
    if (/@import\s+(?:url\s*\()?/i.test(text)) {
      errors.push(`${fileLabel}: CSS @import is forbidden in standalone output`)
    }
    if (
      /document\.createElement\s*\(\s*["']style["']\s*\)/.test(text) ||
      /\.insertRule\s*\(/.test(text) ||
      /\badoptedStyleSheets\b/.test(text)
    ) {
      errors.push(
        `${fileLabel}: runtime style injection is forbidden; render an inline <style> element`,
      )
    }
  }

  notes.push(
    "standalone contract: selected HTML with embedded TSX, package imports, inline styles, no images",
  )
}

const renderMarker = `${sep}src${sep}render${sep}`
const renderIndex = targetDir.indexOf(renderMarker)
const artifactId =
  renderIndex >= 0
    ? targetDir.slice(renderIndex + renderMarker.length).split(sep).filter(Boolean)[0]
    : null

let navigationProviders = 0
let listContainers = 0
let gridContainers = 0
let listItemMarkers = 0
let gridItemMarkers = 0
let usesHMSymbol = false

const templateManifest = loadTemplateManifest()
if (!templateManifest.ok) {
  warnings.push(
    `template-required-components manifest could not be loaded; template-specific required-component checks will be skipped (${templateManifest.error ?? "missing " + templateManifest.path})`,
  )
}

for (const file of sourceFiles) {
  const text = fileText.get(file)
  const navigationCount = countMatches(text, /<NavigationContainer\b/g)
  const shellCount = countMatches(text, /<MobilePhoneShellTemplatePage\b/g)
  const fileLabel = displayPath(file)

  // standalone 递归合并会把 shell 实现（含 NavigationContainer）与 shell 调用并入同一 TSX；
  // 二者代表同一个 provider，取较大值避免重复计数。design-system 下文件分离，维持原加总。
  navigationProviders += standaloneMode
    ? Math.max(navigationCount, shellCount)
    : navigationCount + shellCount
  listContainers += countMatches(text, /<ListContainer\b/g)
  gridContainers += countMatches(text, /<GridContainer\b/g)
  listItemMarkers += countMatches(text, /pixso-list-item/g)
  gridItemMarkers += countMatches(text, /pixso-grid-item/g)
  usesHMSymbol ||= /HMSymbolIcon|iconName|hmSymbolName|hmsymbolName|symbolName/.test(text)

  if (navigationCount > 1) {
    errors.push(`${fileLabel}: contains ${navigationCount} NavigationContainer nodes`)
  }

  // standalone 合并后 shell 定义与 shell 调用同文件并存是合法的，跳过该 per-file 冲突。
  if (!standaloneMode && navigationCount > 0 && shellCount > 0) {
    errors.push(
      `${fileLabel}: MobilePhoneShellTemplatePage already supplies NavigationContainer`,
    )
  }

  if (/<(?:List|Grid)Container\b[^>]*\basChild\b/.test(text)) {
    errors.push(`${fileLabel}: List/Grid containers support "as", not "asChild"`)
  }

  // -------------------------------------------------------------------------
  // Babel-based JSX inspection (replaces the previous regex-based props loop,
  // which silently truncated at the first `>` it encountered — including the
  // `>` inside inline arrow functions like `onClick={() => …}`).
  // -------------------------------------------------------------------------
  // Parse regardless of manifest availability. A missing manifest only disables the
  // manifest-driven rules below — it says nothing about whether the TSX parses.
  // Folding both conditions into one flag made a missing manifest report "could not
  // be parsed", sending readers to hunt a syntax error that was never there, and left
  // the manifest-less fallback further down unreachable.
  const jsxStats = collectJsxStats(
    text,
    templateManifest.ok ? templateManifest.recognizedNames : LEGACY_FALLBACK_TEMPLATE_NAMES,
  )

  if (!jsxStats.ok) {
    errors.push(
      `${fileLabel}: embedded TSX could not be parsed as a JS module; check syntax`,
    )
  } else {
    const jsxNames = jsxStats.jsxElementNames

    // -------------------------------------------------------------------
    // Mode-aware syntactic warnings on <MobilePhoneShellTemplatePage …>.
    // These are not template-required-component rules (those live in the
    // manifest); kept inline because they encode argument *defaults* that
    // are easier to read at the call site.
    // -------------------------------------------------------------------
    for (const usage of jsxStats.templateUsageProps) {
      if (usage.name !== "MobilePhoneShellTemplatePage") continue
      const props = usage.props
      const mode = props.mode
      const floatingTabRaw = props.showFloatingTab
      const aiBottomBarRaw = props.showAIBottomBar
      const showTitleBarRaw = props.showTitleBar

      const defaultedFloatingTab =
        floatingTabRaw === undefined || floatingTabRaw === "__expr__"
          ? mode === "app-home"
          : floatingTabRaw === "true"
      const defaultedShowTitleBar =
        showTitleBarRaw === undefined || showTitleBarRaw === "__expr__"
          ? true
          : showTitleBarRaw !== "false"
      const defaultedAIBottomBar =
        aiBottomBarRaw === undefined || aiBottomBarRaw === "__expr__"
          ? false
          : aiBottomBarRaw === "true"

      if (mode === "app-home" && !defaultedFloatingTab) {
        errors.push(`${fileLabel}: app-home unexpectedly disables FloatingTab`)
      }
      if (
        (mode === "secondary" || mode === "immersive") &&
        defaultedFloatingTab
      ) {
        warnings.push(
          `${fileLabel}: ${mode ?? "unset"} should explicitly declare showFloatingTab={false}`,
        )
      }
      if (mode === "immersive" && defaultedAIBottomBar) {
        warnings.push(
          `${fileLabel}: immersive should explicitly declare showAIBottomBar={false}`,
        )
      }

      // No-op suppression to indicate we read these defaults — they are
      // consumed by the per-template rules below.
      void defaultedShowTitleBar
      void defaultedAIBottomBar
    }

    // -------------------------------------------------------------------
    // Manifest-driven "template-required components preservation" check.
    // Each template JSX usage pulls its rules from
    // references/template-required-components.json. Adding a new shell means
    // adding one JSON entry; the validator does not need to be touched.
    // -------------------------------------------------------------------
    for (const usage of jsxStats.templateUsageProps) {
      const rule = templateManifest.templates[usage.name]
      if (!rule) continue
      const requiredJsx = rule["required-jsx"] ?? []
      const missing = requiredJsx.filter(
        (name) => (jsxNames.get(name) ?? 0) === 0,
      )
      if (missing.length) {
        errors.push(
          `${fileLabel}: template "${usage.name}" (page-type: ${rule["page-type"] ?? "n/a"}) is rendered but its required registered components are missing: ${missing.join(", ")}; replace self-rolled HTML with the registered components`,
        )
      }
      const requiredAnyOf = rule["required-any-of"] ?? []
      if (requiredAnyOf.length) {
        const satisfied = requiredAnyOf.some((group) =>
          group.every((name) => (jsxNames.get(name) ?? 0) > 0),
        )
        if (!satisfied) {
          errors.push(
            `${fileLabel}: template "${usage.name}" needs at least one of the registered block sets; none of the documented alternatives were found: ${requiredAnyOf.map((g) => g.join("+")).join(" / ")}`,
          )
        }
      }
    }

    // Cross-cutting: if any template JSX is present, also enforce
    // always-required JSX names declared at the manifest root.
    if (jsxStats.templateUsageProps.length > 0 && templateManifest.alwaysRequired.length) {
      const missingAlways = templateManifest.alwaysRequired.filter(
        (name) => (jsxNames.get(name) ?? 0) === 0,
      )
      if (missingAlways.length) {
        errors.push(
          `${fileLabel}: required baseline components missing from any template render: ${missingAlways.join(", ")}`,
        )
      }
    }

    // ---------------------------------------------------------------------
    // Legacy single-template fallback only when the manifest refuses to
    // declare MobilePhoneShellTemplatePage rules. When the manifest IS
    // loaded, the rules above already cover shell chrome.
    // ---------------------------------------------------------------------
    if (!templateManifest.ok) {
      for (const usage of jsxStats.templateUsageProps) {
        if (usage.name !== "MobilePhoneShellTemplatePage") continue
        const props = usage.props
        const mode = props.mode
        const floatingTabRaw = props.showFloatingTab
        const aiBottomBarRaw = props.showAIBottomBar
        const showTitleBarRaw = props.showTitleBar
        const defaultedFloatingTab =
          floatingTabRaw === undefined || floatingTabRaw === "__expr__"
            ? mode === "app-home"
            : floatingTabRaw === "true"
        const defaultedShowTitleBar =
          showTitleBarRaw === undefined || showTitleBarRaw === "__expr__"
            ? true
            : showTitleBarRaw !== "false"
        const defaultedAIBottomBar =
          aiBottomBarRaw === undefined || aiBottomBarRaw === "__expr__"
            ? false
            : aiBottomBarRaw === "true"
        const floatingTitleBarCount = jsxNames.get("FloatingTitleBar") ?? 0
        const floatingTabCount = jsxNames.get("FloatingTab") ?? 0
        const aibottombarCount = jsxNames.get("Aibottombar") ?? 0
        const navigationCountLocal = jsxNames.get("NavigationContainer") ?? 0
        if (defaultedShowTitleBar && floatingTitleBarCount === 0) {
          errors.push(
            `${fileLabel}: MobilePhoneShellTemplatePage is rendered with showTitleBar enabled but <FloatingTitleBar> is absent`,
          )
        }
        if (defaultedFloatingTab && floatingTabCount === 0) {
          errors.push(
            `${fileLabel}: MobilePhoneShellTemplatePage is rendered with showFloatingTab enabled but <FloatingTab> is absent`,
          )
        }
        if (defaultedAIBottomBar && aibottombarCount === 0) {
          errors.push(
            `${fileLabel}: MobilePhoneShellTemplatePage is rendered with showAIBottomBar enabled but <Aibottombar> is absent`,
          )
        }
        if (navigationCountLocal === 0) {
          errors.push(
            `${fileLabel}: MobilePhoneShellTemplatePage body is missing <NavigationContainer>`,
          )
        }
      }
    }
  }
}

if (navigationProviders === 0) {
  warnings.push(
    "No NavigationContainer provider found; confirm that an external baseline or host supplies it",
  )
} else if (navigationProviders > 1) {
  warnings.push(
    `Found ${navigationProviders} possible NavigationContainer providers; verify the final rendered tree has exactly one`,
  )
}

if (listContainers > 0 && listItemMarkers === 0) {
  warnings.push(
    "ListContainer is present but no pixso-list-item marker was found; ListPhone is the only exemption",
  )
}

if (gridContainers > 0 && gridItemMarkers === 0) {
  errors.push("GridContainer is present but no pixso-grid-item marker was found")
}

notes.push(
  `containers: navigation providers=${navigationProviders}, list=${listContainers}, grid=${gridContainers}`,
)
notes.push(`markers: list=${listItemMarkers}, grid=${gridItemMarkers}`)

if (!standaloneMode) {
  for (const storyFile of storyFiles) {
    const text = fileText.get(storyFile)
    const storyTitle = text.match(/\btitle\s*:\s*["']([^"']+)["']/)?.[1]
    const storyLabel = displayPath(storyFile)

    if (!storyTitle) {
      errors.push(`${storyLabel}: missing static Storybook meta.title`)
      continue
    }

    if (artifactId && !storyTitle.startsWith(`RENDER/${artifactId}`)) {
      errors.push(
        `${storyLabel}: title "${storyTitle}" must start with "RENDER/${artifactId}"`,
      )
    } else if (!artifactId && !storyTitle.startsWith("RENDER/")) {
      warnings.push(`${storyLabel}: render artifact title should start with "RENDER/"`)
    }
  }

  if (storyFiles.length === 0) {
    errors.push("No Storybook story file found in target directory")
  }
}

const packagingArtifacts = standaloneMode
  ? []
  : ["entry.tsx", "c2d-prerender.tsx", "dist"].filter((name) =>
      existsSync(join(targetDir, name)),
    )

const indexExportPath = join(targetDir, "index.ts")
if (!standaloneMode && !pageBuildRequested && existsSync(indexExportPath)) {
  const gitResult = spawnSync(
    "git",
    ["status", "--porcelain", "--", relative(process.cwd(), indexExportPath)],
    { cwd: process.cwd(), encoding: "utf8" },
  )
  const changedInCurrentWorktree =
    gitResult.status === 0 && gitResult.stdout.trim().length > 0

  if (changedInCurrentWorktree) {
    errors.push(
      `${displayPath(indexExportPath)}: index.ts was created or modified without page-build; import the page component directly`,
    )
  } else {
    warnings.push(
      `${displayPath(indexExportPath)}: pre-existing index.ts detected; do not modify or recreate it unless page-build is requested`,
    )
  }
}

if (!standaloneMode && !pageBuildRequested && packagingArtifacts.length > 0) {
  warnings.push(
    `Page-build was not requested, but existing packaging artifacts were found: ${packagingArtifacts.join(", ")}. Confirm they were not created or updated by this task.`,
  )
}

if (usesHMSymbol) {
  const scriptDir = resolve(fileURLToPath(new URL(".", import.meta.url)))
  const checker = join(scriptDir, "check-hmsymbol-usage.mjs")
  let checkerTarget = targetDir
  let temporaryDir = null

  if (standaloneMode) {
    temporaryDir = mkdtempSync(join(tmpdir(), "page-generation-hmsymbol-"))
    checkerTarget = join(temporaryDir, "embedded-page.tsx")
    writeFileSync(checkerTarget, fileText.get(sourceFiles[0]))
  }

  const result = spawnSync(process.execPath, [checker, checkerTarget], {
    encoding: "utf8",
  })

  if (temporaryDir) {
    rmSync(temporaryDir, { recursive: true, force: true })
  }

  if (result.stdout.trim()) process.stdout.write(`${result.stdout.trim()}\n`)
  if (result.stderr.trim()) process.stderr.write(`${result.stderr.trim()}\n`)

  if (result.status !== 0) {
    errors.push("HMSymbol validation failed")
  } else {
    notes.push("HMSymbol validation passed")
  }
}

for (const note of notes) console.log(`NOTE: ${note}`)
for (const warning of warnings) console.warn(`WARN: ${warning}`)
for (const error of errors) console.error(`ERROR: ${error}`)

if (errors.length > 0) {
  console.error(
    `Page artifact validation failed with ${errors.length} error(s) and ${warnings.length} warning(s).`,
  )
  process.exit(1)
}

console.log(
  `Page artifact validation passed with ${warnings.length} warning(s). Manual direct-child and rendered-tree review is still required.`,
)
