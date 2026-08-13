#!/usr/bin/env node

import {
  cpSync,
  existsSync,
  mkdirSync,
  readFileSync,
  statSync,
  writeFileSync,
} from "node:fs"
import { readdirSync } from "node:fs"
import { dirname, join, resolve } from "node:path"
import { fileURLToPath } from "node:url"

const usage = `Usage:
  node scaffold-standalone-html.mjs <output-dir> <page-name> --title <page-title>
    [--tsx-file <path>] [--css-file <path>]

Creates <output-dir>/<page-name>.shadcn.html from the bundled Babel template when the
HTML does not exist. Existing HTML is preserved. The shared design-system-vendor
directory is copied beside <output-dir> only when it does not already exist.
When --tsx-file is provided, only the page-tsx script content is replaced.

The --css-file option reads a CSS file (typically the merged.css produced by
prepare-template-merge.mjs) and substitutes its contents into the embedded TSX
wherever the placeholder token "__TEMPLATE_CSS__" appears. This is the
recommended way to ship template-private CSS (mobile-phone-shell-template.css,
settings-page-template.css, etc.) inside a standalone HTML — those styles do
NOT live in the design-components.css / blocks-components.css vendor files.
Without --css-file (or manual inlining) the shell chrome and template-specific
row styles are absent and the page renders as plain DOM.`

const TEMPLATE_CSS_PLACEHOLDER = "__TEMPLATE_CSS__"

const args = process.argv.slice(2)
if (args.includes("--help") || args.includes("-h")) {
  console.log(usage)
  process.exit(0)
}

const positional = []
let pageTitle = null
let tsxFile = null
let cssFile = null

for (let index = 0; index < args.length; index += 1) {
  const arg = args[index]
  if (arg === "--title") {
    const value = args[index + 1]
    if (!value || value.startsWith("--")) {
      console.error(`Missing value for --title\n\n${usage}`)
      process.exit(2)
    }
    pageTitle = value
    index += 1
    continue
  }
  if (arg === "--tsx-file") {
    const value = args[index + 1]
    if (!value || value.startsWith("--")) {
      console.error(`Missing value for --tsx-file\n\n${usage}`)
      process.exit(2)
    }
    tsxFile = resolve(value)
    index += 1
    continue
  }
  if (arg === "--css-file") {
    const value = args[index + 1]
    if (!value || value.startsWith("--")) {
      console.error(`Missing value for --css-file\n\n${usage}`)
      process.exit(2)
    }
    cssFile = resolve(value)
    index += 1
    continue
  }
  if (arg.startsWith("--")) {
    console.error(`Unknown option: ${arg}\n\n${usage}`)
    process.exit(2)
  }
  positional.push(arg)
}

if (positional.length !== 2 || !pageTitle) {
  console.error(usage)
  process.exit(2)
}

const [outputArg, pageName] = positional
if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(pageName)) {
  console.error(`Page name must use kebab-case: ${pageName}`)
  process.exit(2)
}

const scriptDir = dirname(fileURLToPath(import.meta.url))
const skillDir = resolve(scriptDir, "..")
const templatePath = join(
  skillDir,
  "babel-render-tsx/html-template/babel-string-template.html",
)
const vendorSource = join(skillDir, "babel-render-tsx/design-system-vendor")
const outputDir = resolve(outputArg)
const outputParent = dirname(outputDir)
const outputHtml = join(outputDir, `${pageName}.shadcn.html`)
const vendorTarget = join(outputParent, "design-system-vendor")

for (const requiredPath of [templatePath, vendorSource]) {
  if (!existsSync(requiredPath)) {
    console.error(`Required standalone resource is missing: ${requiredPath}`)
    process.exit(2)
  }
}

mkdirSync(outputDir, { recursive: true })

// Runtime vendor files copied into standalone output. Excludes the React
// 8-file split (now bundled into react-vendor-19.2.6.js) and the build/entry
// sources used by `build-vendor.mjs`.
//
// Font files (extracted from design-components.css base64 data) must be
// included so that @font-face rules resolve as file references instead of
// blocking the page with a multi-MB synchronous CSS download.
const RUNTIME_VENDOR_FILES = [
  "react-vendor-19.2.6.js",
  "design-components.js",
  "design-components.css",
  "blocks-components.js",
  "blocks-components.css",
  "babel-standalone.js",
  "tailwind-browser.js",
  // HMSymbol icon font (referenced by hmsymbol-font.css <link>)
  "hmsymbol-font.css",
  "HMSymbolVF.ttf",
]

if (existsSync(vendorTarget)) {
  console.log(`[standalone-scaffold] SKIP vendor exists: ${vendorTarget}`)
} else {
  mkdirSync(vendorTarget, { recursive: true })
  const present = new Set(readdirSync(vendorSource))
  const missing = []
  for (const file of RUNTIME_VENDOR_FILES) {
    if (!present.has(file)) {
      missing.push(file)
      continue
    }
    cpSync(join(vendorSource, file), join(vendorTarget, file))
  }
  if (missing.length) {
    console.error(
      `[standalone-scaffold] missing runtime vendor files in ${vendorSource}: ${missing.join(", ")}`,
    )
    process.exit(2)
  }
  console.log(
    `[standalone-scaffold] COPY vendor: ${vendorTarget} (${RUNTIME_VENDOR_FILES.length} files)`,
  )
}

if (existsSync(outputHtml)) {
  console.log(`[standalone-scaffold] PRESERVE html exists: ${outputHtml}`)
} else {
  const escapedTitle = pageTitle
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
  const template = readFileSync(templatePath, "utf8")
  if (!template.includes("// tsx 代码 生成位置")) {
    console.error(`Standalone HTML template is missing the TSX insertion marker: ${templatePath}`)
    process.exit(2)
  }
  const html = template.replace(
    "<title>Babel TSX 字符串模板</title>",
    `<title>${escapedTitle}</title>`,
  )
  writeFileSync(outputHtml, html)
  console.log(`[standalone-scaffold] CREATE html: ${outputHtml}`)
}

if (tsxFile) {
  if (!existsSync(tsxFile) || !statSync(tsxFile).isFile()) {
    console.error(`TSX source file does not exist: ${tsxFile}`)
    process.exit(2)
  }

  const tsxSource = readFileSync(tsxFile, "utf8").trim()
  if (!tsxSource) {
    console.error(`TSX source file is empty: ${tsxFile}`)
    process.exit(2)
  }
  if (/<\/script\s*>/i.test(tsxSource)) {
    console.error(`TSX source cannot contain a closing </script> tag: ${tsxFile}`)
    process.exit(2)
  }

  const pageTsxPattern =
    /(<script\b(?=[^>]*\bid=["']page-tsx["'])(?=[^>]*\btype=["']text\/plain["'])[^>]*>)[\s\S]*?(<\/script\s*>)/i
  const html = readFileSync(outputHtml, "utf8")
  if (!pageTsxPattern.test(html)) {
    console.error(`Standalone HTML is missing the page-tsx script block: ${outputHtml}`)
    process.exit(2)
  }

  // Substitute __TEMPLATE_CSS__ placeholder with the merged.css content
  // before injecting into the page-tsx script. The TSX is expected to embed
  // the placeholder inside the styles template literal, e.g.
  //   const styles = `__TEMPLATE_CSS__
  //                   .my-extra { … }`
  //   return <…><style>{styles}</style></…>
  // The placeholder does not need to be inside the same script tag — it can
  // appear anywhere in the TSX text. When --css-file is omitted, the
  // placeholder is left intact so that the validator's leak check surfaces
  // the missing wire-up as a diagnostic.
  let tsxAfterCss = tsxSource
  if (cssFile) {
    if (!existsSync(cssFile) || !statSync(cssFile).isFile()) {
      console.error(`CSS source file does not exist: ${cssFile}`)
      process.exit(2)
    }
    const cssSource = readFileSync(cssFile, "utf8")
    const placeholderOccurrences = tsxSource.split(TEMPLATE_CSS_PLACEHOLDER).length - 1
    if (placeholderOccurrences === 0) {
      console.error(
        `[standalone-scaffold] --css-file provided but TSX contains no "${TEMPLATE_CSS_PLACEHOLDER}" placeholder; nothing to substitute in ${outputHtml}`,
      )
      process.exit(2)
    }
    tsxAfterCss = tsxAfterCss.split(TEMPLATE_CSS_PLACEHOLDER).join(cssSource)
    console.log(
      `[standalone-scaffold] INJECT css: ${cssFile} (${placeholderOccurrences} placeholder occurrence(s) substituted)`,
    )
  } else if (tsxSource.includes(TEMPLATE_CSS_PLACEHOLDER)) {
    console.error(
      `[standalone-scaffold] TSX contains "${TEMPLATE_CSS_PLACEHOLDER}" placeholder but --css-file was not provided; pass --css-file <path-to-merged.css> to substitute template CSS`,
    )
    process.exit(2)
  }

  const injected = html.replace(
    pageTsxPattern,
    (_match, openingTag, closingTag) =>
      `${openingTag}\n${tsxAfterCss}\n  ${closingTag}`,
  )
  writeFileSync(outputHtml, injected)
  console.log(`[standalone-scaffold] INJECT tsx: ${outputHtml}`)
} else {
  console.log(`[standalone-scaffold] TSX marker: // tsx 代码 生成位置`)
}
