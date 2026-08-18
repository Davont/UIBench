#!/usr/bin/env node

import {
  copyFileSync,
  cpSync,
  existsSync,
  mkdirSync,
  readFileSync,
  writeFileSync,
} from "node:fs"
import { dirname, join, resolve } from "node:path"
import { fileURLToPath } from "node:url"

function fail(message) {
  console.error(`ERROR: ${message}`)
  process.exit(2)
}

function parseArgs(argv) {
  const values = {}
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index]
    if (!arg.startsWith("--")) fail(`unexpected argument ${arg}`)
    const key = arg.slice(2)
    const value = argv[index + 1]
    if (!value || value.startsWith("--")) fail(`missing value for ${arg}`)
    values[key] = value
    index += 1
  }
  return values
}

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
}

function attributeValue(source, name) {
  const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
  const match = source.match(new RegExp(
    `\\b${escaped}\\s*=\\s*(?:"([^"]*)"|'([^']*)'|([^\\s>]+))`,
    "i",
  ))
  return match ? (match[1] ?? match[2] ?? match[3] ?? "") : null
}

function materializeIcons(html, iconMap) {
  const iconPattern = /<(i|span)\b([^>]*)>\s*<\/\1>/gi
  const unknown = new Set()
  const output = html.replace(iconPattern, (whole, tag, attrs) => {
    const iconName = attributeValue(attrs, "data-lucide")
    if (iconName === null) return whole
    const icon = iconMap.icons[iconName]
    if (!icon) {
      unknown.add(iconName)
      return whole
    }
    return `<${tag}${attrs}>&#x${icon.codepoint};</${tag}>`
  })
  if (unknown.size > 0) {
    fail(`unknown icon names: ${[...unknown].sort().join(", ")}`)
  }
  return output
}

function installRuntime(html, { title, theme }) {
  const titleText = escapeHtml(title)
  const runtimeLink = '<link rel="stylesheet" href="assets/harmony-runtime.css">'
  const viewport = '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
  const charset = '<meta charset="UTF-8">'
  const hasHtml = /<html\b/i.test(html)
  const hasHead = /<head\b/i.test(html)
  const hasBody = /<body\b/i.test(html)
  const shellParts = [hasHtml, hasHead, hasBody].filter(Boolean).length
  if (shellParts > 0 && shellParts < 3) {
    fail("input must be either an HTML fragment or a complete html/head/body document")
  }
  const isComplete = hasHtml && hasHead && hasBody

  if (!isComplete) {
    return [
      "<!DOCTYPE html>",
      `<html lang="zh-CN" data-theme="${theme}">`,
      "<head>",
      `  ${charset}`,
      `  ${viewport}`,
      `  <title>${titleText}</title>`,
      `  ${runtimeLink}`,
      "</head>",
      "<body>",
      html.trim(),
      "</body>",
      "</html>",
      "",
    ].join("\n")
  }

  let output = html
  if (!/<!doctype\s+html\s*>/i.test(output)) {
    output = `<!DOCTYPE html>\n${output.trimStart()}`
  }
  output = output.replace(/<html\b([^>]*)>/i, (whole, attrs) => {
    let next = attrs
    if (/\bdata-theme\s*=/i.test(next)) {
      next = next.replace(/\bdata-theme\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+)/i, `data-theme="${theme}"`)
    } else {
      next += ` data-theme="${theme}"`
    }
    if (!/\blang\s*=/i.test(next)) next += ' lang="zh-CN"'
    return `<html${next}>`
  })

  if (!/<meta\b[^>]*charset\s*=/i.test(output)) {
    output = output.replace(/<head\b[^>]*>/i, (head) => `${head}\n  ${charset}\n`)
  }
  if (!/<meta\b[^>]*name\s*=\s*["']viewport["']/i.test(output)) {
    output = output.replace(/<head\b[^>]*>/i, (head) => `${head}\n  ${viewport}\n`)
  }
  if (!/<title\b/i.test(output)) {
    output = output.replace(/<head\b[^>]*>/i, (head) => `${head}\n  <title>${titleText}</title>\n`)
  }
  if (!/<link\b[^>]*href\s*=\s*["']assets\/harmony-runtime\.css["']/i.test(output)) {
    output = output.replace(/<\/head>/i, `\n  ${runtimeLink}\n</head>`)
  }
  return output.endsWith("\n") ? output : `${output}\n`
}

const args = parseArgs(process.argv.slice(2))
if (!args.input) fail("--input is required")
if (!args.out) fail("--out is required")
const theme = args.theme ?? "light"
if (!new Set(["light", "dark"]).has(theme)) fail("--theme must be light or dark")
const inputPath = resolve(args.input)
const outputDir = resolve(args.out)
if (!existsSync(inputPath)) fail(`input does not exist: ${inputPath}`)
const scriptDir = dirname(fileURLToPath(import.meta.url))
const skillDir = resolve(scriptDir, "..")
const iconMap = JSON.parse(readFileSync(join(skillDir, "references", "icon-map.json"), "utf8"))

let html = readFileSync(inputPath, "utf8")
if (!html.trim()) fail("input HTML is empty")
html = materializeIcons(html, iconMap)
html = installRuntime(html, {
  title: args.title?.trim() || "HarmonyOS 页面",
  theme,
})

const assetsDir = join(outputDir, "assets")
mkdirSync(assetsDir, { recursive: true })
copyFileSync(
  join(skillDir, "assets", "harmony-runtime.css"),
  join(assetsDir, "harmony-runtime.css"),
)
cpSync(join(skillDir, "assets", "fonts"), join(assetsDir, "fonts"), {
  recursive: true,
  force: true,
})
const outputPath = join(outputDir, "index.html")
writeFileSync(outputPath, html, "utf8")
console.log(JSON.stringify({
  ok: true,
  input: inputPath,
  output: outputPath,
  theme,
  runtime: join(assetsDir, "harmony-runtime.css"),
}, null, 2))
