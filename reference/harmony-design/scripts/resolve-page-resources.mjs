#!/usr/bin/env node

import { existsSync, readFileSync } from "node:fs"
import { dirname, join, resolve } from "node:path"
import { fileURLToPath } from "node:url"

import { sourceRoot } from "./shared.mjs"

const usage = `Usage:
  node resolve-page-resources.mjs <page_type> [--pattern <pattern-id>]

Prints a compact A3 resource payload validated against the three formal registries.
When a page_type has no manifest entry, use the normal targeted registry fallback.`

const args = process.argv.slice(2)
if (args.includes("--help") || args.includes("-h")) {
  console.log(usage)
  process.exit(0)
}

const pageType = args.find((arg) => !arg.startsWith("--"))
const patternIndex = args.indexOf("--pattern")
const patternId = patternIndex >= 0 ? args[patternIndex + 1] : null

if (!pageType || (patternIndex >= 0 && !patternId)) {
  console.error(usage)
  process.exit(2)
}

const scriptDir = dirname(fileURLToPath(import.meta.url))
const skillDir = resolve(scriptDir, "..")
const manifestPath = join(skillDir, "references/page-resource-manifest.json")
const manifest = JSON.parse(readFileSync(manifestPath, "utf8"))
const entry = manifest.pageTypes[pageType] ?? null

if (!entry) {
  console.log(JSON.stringify({
    schema: manifest.schema,
    sourceMode: "standalone",
    sourceRoot,
    pageType,
    manifestEntry: null,
    fallback: "targeted-registry-read",
  }, null, 2))
  process.exit(0)
}

function collectRecords(value, records = []) {
  if (Array.isArray(value)) {
    for (const item of value) collectRecords(item, records)
  } else if (value && typeof value === "object") {
    if (value.id || value.name || value.path || value.files) records.push(value)
    for (const child of Object.values(value)) collectRecords(child, records)
  }
  return records
}

function resolveSrc(relativePath) {
  const normalized = relativePath.replaceAll("\\", "/")
  if (normalized === "src") return sourceRoot
  if (normalized.startsWith("src/")) return join(sourceRoot, normalized.slice("src/".length))
  return join(sourceRoot, normalized)
}

function readRegistry(relativePath) {
  const path = resolveSrc(relativePath)
  if (!existsSync(path)) throw new Error(`Missing formal registry: ${relativePath}`)
  return collectRecords(JSON.parse(readFileSync(path, "utf8")))
}

const blocks = readRegistry("src/blocks-specs/blocks.json")
const components = readRegistry("src/components-specs/components.json")
const assets = readRegistry("src/assets/assets.json")
const byId = (records, id) => records.find((record) => record.id === id) ?? null
const template = byId(blocks, entry.templateId)
const matchedComponents = entry.componentIds.map((id) => byId(components, id))
const missingComponents = entry.componentIds.filter((_, index) => !matchedComponents[index])

const tokenPath = resolveSrc(manifest.tokenSource)
const tokenText = readFileSync(tokenPath, "utf8")
const tokenDeclarations = Object.fromEntries(manifest.sharedTokens.map((token) => {
  const escaped = token.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
  const match = tokenText.match(new RegExp(`${escaped}\\s*:\\s*([^;]+);`))
  return [token, match?.[1]?.trim() ?? null]
}))
const missingTokens = Object.entries(tokenDeclarations)
  .filter(([, value]) => value === null)
  .map(([token]) => token)
const iconText = readFileSync(resolveSrc(manifest.iconSource), "utf8")
const missingIcons = entry.commonIcons.filter(
  (icon) => !iconText.includes(`"${icon}"`),
)

const selectedPatterns = patternId
  ? entry.patterns.filter((pattern) => pattern.id === patternId)
  : entry.patterns
const resolvedPatterns = selectedPatterns.map((pattern) => {
  const sourceMarker = "/references/"
  const markerIndex = pattern.source?.indexOf(sourceMarker) ?? -1
  const resolvedSource = markerIndex >= 0
    ? join(skillDir, pattern.source.slice(markerIndex + 1))
    : pattern.source
  return { ...pattern, resolvedSource }
})
const missingPattern = patternId && selectedPatterns.length === 0 ? patternId : null

const result = {
  schema: manifest.schema,
  sourceMode: "standalone",
  sourceRoot,
  pageType,
  template,
  components: matchedComponents.filter(Boolean),
  assets: entry.assetIds?.map((id) => byId(assets, id)).filter(Boolean) ?? [],
  tokens: tokenDeclarations,
  commonIcons: entry.commonIcons,
  patterns: resolvedPatterns,
  diagnostics: {
    missingTemplate: template ? null : entry.templateId,
    missingComponents,
    missingTokens,
    missingIcons,
    missingPattern,
  },
}

if (
  result.diagnostics.missingTemplate ||
  missingComponents.length ||
  missingTokens.length ||
  missingIcons.length ||
  missingPattern
) {
  console.error(JSON.stringify(result, null, 2))
  process.exit(1)
}

console.log(JSON.stringify(result, null, 2))
