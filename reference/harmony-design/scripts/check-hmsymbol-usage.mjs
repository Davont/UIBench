#!/usr/bin/env node

/**
 * Validate HMSymbolIcon names used in generated pages.
 *
 * Usage:
 *   node <STANDALONE_PAGE_GENERATION_SKILL_DIR>/scripts/check-hmsymbol-usage.mjs <file-or-directory> [more paths...]
 *
 * The check is intentionally exact: every discovered HM Symbol name must exist
 * in the local full symbol map or in the component's local legacy aliases.
 */

import fs from 'node:fs'
import path from 'node:path'

import { sourceRoot } from './shared.mjs'

const root = process.cwd()
const mapPath = path.join(sourceRoot, 'assets/hmsymbol/hmsymbol-map.json')
const constantsPath = path.join(sourceRoot, 'components/HMSymbolIcon/hmsymbol-icon.constants.ts')

const targetArgs = process.argv.slice(2)

if (targetArgs.length === 0) {
  console.error('[hmsymbol-check] 用法: node <STANDALONE_PAGE_GENERATION_SKILL_DIR>/scripts/check-hmsymbol-usage.mjs <file-or-directory> [more paths...]')
  process.exit(1)
}

const validNames = loadValidNames()
const files = collectFiles(targetArgs)
const usages = files.flatMap((file) => extractUsages(file))
const missing = usages.filter((usage) => !validNames.has(usage.name))

if (usages.length === 0) {
  console.log('[hmsymbol-check] 未发现 HMSymbolIcon 字面量使用。')
  process.exit(0)
}

if (missing.length === 0) {
  console.log(`[hmsymbol-check] OK: ${usages.length} 个 HM Symbol name 均存在于本地资源表。`)
  process.exit(0)
}

console.error(`[hmsymbol-check] FAILED: 发现 ${missing.length} 个不存在于本地资源表的 HM Symbol name。`)
for (const item of missing) {
  console.error(`  ${path.relative(root, item.file)}:${item.line}:${item.column} ${item.kind}="${item.name}"`)
}
const lookupHint = `\`${path.join(sourceRoot, 'assets/hmsymbol/hmsymbol-icons-common.md')}\` 或 \`${path.join(sourceRoot, 'assets/hmsymbol/hmsymbol-index.md')}\``
console.error(`\n请使用 ${lookupHint} 选择本地存在的 name 后重试。`)
process.exit(1)

function loadValidNames() {
  const names = new Set()

  const map = JSON.parse(fs.readFileSync(mapPath, 'utf8'))
  for (const icon of map.icons ?? []) {
    if (icon.name) names.add(icon.name)
  }

  const constants = fs.readFileSync(constantsPath, 'utf8')
  const legacyBlock = constants.match(/const hmSymbolLegacyAliases = \{([\s\S]*?)\} as const/)
  if (legacyBlock) {
    for (const match of legacyBlock[1].matchAll(/^\s*([A-Za-z0-9_]+)\s*:/gm)) {
      names.add(match[1])
    }
  }

  return names
}

function collectFiles(inputs) {
  const files = []
  for (const input of inputs) {
    const absolute = path.isAbsolute(input)
      ? input
      : path.resolve(process.cwd(), input)
    if (!fs.existsSync(absolute)) {
      console.error(`[hmsymbol-check] 路径不存在: ${input}`)
      process.exit(1)
    }
    collectFile(absolute, files)
  }
  return files.sort()
}

function collectFile(target, files) {
  const stat = fs.statSync(target)
  if (stat.isDirectory()) {
    for (const entry of fs.readdirSync(target, { withFileTypes: true })) {
      if (entry.name === 'dist' || entry.name === 'node_modules' || entry.name.startsWith('.')) continue
      collectFile(path.join(target, entry.name), files)
    }
    return
  }

  if (/\.(tsx?|jsx?)$/.test(target)) {
    files.push(target)
  }
}

function extractUsages(file) {
  const source = fs.readFileSync(file, 'utf8')
  const usages = []

  const directNamePattern = /<HMSymbolIcon\b[^>]*\bname\s*=\s*["']([^"']+)["']/gs
  for (const match of source.matchAll(directNamePattern)) {
    usages.push(createUsage(file, source, match, 'HMSymbolIcon name'))
  }

  const expressionNamePattern = /<HMSymbolIcon\b[^>]*\bname\s*=\s*\{([^}]*)\}/gs
  for (const match of source.matchAll(expressionNamePattern)) {
    const expression = match[1]
    const expressionOffset = match.index + match[0].indexOf(match[1])
    for (const literal of expression.matchAll(/["']([^"']+)["']/g)) {
      if (!shouldValidateExpressionLiteral(expression, literal.index)) continue
      usages.push(createUsageFromOffset(file, source, expressionOffset + literal.index + 1, literal[1], 'HMSymbolIcon name'))
    }
  }

  const hasHMSymbolContext = /HMSymbolIcon\b/.test(source) || /\b(?:\w*[iI]conName|\w*[sS]ymbolName)\s*[:=]/.test(source)
  if (hasHMSymbolContext) {
    const fieldPattern = /\b(?:\w*[iI]conName|\w*[sS]ymbolName)\s*:\s*["']([^"']+)["']/g
    for (const match of source.matchAll(fieldPattern)) {
      usages.push(createUsage(file, source, match, 'icon field'))
    }

    const propPattern = /\b(?:\w*[iI]conName|\w*[sS]ymbolName)\s*=\s*["']([^"']+)["']/g
    for (const match of source.matchAll(propPattern)) {
      usages.push(createUsage(file, source, match, 'icon prop'))
    }
  }

  return usages
}

function createUsage(file, source, match, kind) {
  const offset = match.index + match[0].indexOf(match[1])
  return createUsageFromOffset(file, source, offset, match[1], kind)
}

function createUsageFromOffset(file, source, offset, name, kind) {
  const { line, column } = getLineColumn(source, offset)
  return {
    file,
    line,
    column,
    kind,
    name,
  }
}

function shouldValidateExpressionLiteral(expression, literalIndex) {
  const trimmed = expression.trim()
  if (/^["'][^"']+["']$/.test(trimmed)) return true

  const previous = expression.slice(0, literalIndex).trimEnd()
  if (previous.length === 0) return true

  return /[?:,\[]$/.test(previous)
}

function getLineColumn(source, offset) {
  let line = 1
  let column = 1
  for (let index = 0; index < offset; index += 1) {
    if (source.charCodeAt(index) === 10) {
      line += 1
      column = 1
    } else {
      column += 1
    }
  }
  return { line, column }
}
