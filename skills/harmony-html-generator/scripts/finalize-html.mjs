#!/usr/bin/env node

import { createHash } from "node:crypto"
import {
  chmodSync,
  copyFileSync,
  cpSync,
  existsSync,
  lstatSync,
  mkdirSync,
  readFileSync,
  realpathSync,
  readdirSync,
  rmSync,
  writeFileSync,
} from "node:fs"
import { dirname, isAbsolute, join, relative, resolve, sep } from "node:path"
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

const normalizableComponents = new Set(["column", "row", "stack", "grid"])
const conflictingLayoutClasses = new Map([
  ["column", new Set(["grid", "block", "flex-row", "flex-row-reverse", "flex-col-reverse"])],
  ["row", new Set(["grid", "block", "flex-col", "flex-row-reverse", "flex-col-reverse"])],
  ["stack", new Set(["absolute", "fixed", "sticky"])],
  ["grid", new Set(["flex", "block"])],
])
const rawTextTags = new Set(["script", "style", "textarea"])
const voidTags = new Set([
  "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
  "meta", "param", "source", "track", "wbr",
])

function isHtmlSpace(value) {
  return value !== undefined && /\s/.test(value)
}

function isAttributeNameCharacter(value) {
  return value !== undefined && !/[\s"'<>/=`]/.test(value)
}

function findTagEnd(html, start) {
  let quote = null
  for (let index = start; index < html.length; index += 1) {
    const character = html[index]
    if (quote !== null) {
      if (character === quote) quote = null
      continue
    }
    if (character === '"' || character === "'") {
      quote = character
    } else if (character === ">") {
      return index
    }
  }
  return -1
}

function scanTagAttributes(html, start, end) {
  const attributes = []
  let index = start
  while (index < end) {
    while (index < end && isHtmlSpace(html[index])) index += 1
    if (index >= end) break
    if (html[index] === "/") {
      index += 1
      continue
    }

    const nameStart = index
    while (index < end && isAttributeNameCharacter(html[index])) index += 1
    if (index === nameStart) return { attributes, valid: false }
    const name = html.slice(nameStart, index).toLowerCase()
    while (index < end && isHtmlSpace(html[index])) index += 1

    let value = null
    let valueStart = null
    let valueEnd = null
    let quote = null
    if (html[index] === "=") {
      index += 1
      while (index < end && isHtmlSpace(html[index])) index += 1
      if (index >= end) return { attributes, valid: false }
      if (html[index] === '"' || html[index] === "'") {
        quote = html[index]
        index += 1
        valueStart = index
        while (index < end && html[index] !== quote) index += 1
        if (index >= end) return { attributes, valid: false }
        valueEnd = index
        value = html.slice(valueStart, valueEnd)
        index += 1
      } else {
        valueStart = index
        while (index < end && !isHtmlSpace(html[index])) index += 1
        valueEnd = index
        value = html.slice(valueStart, valueEnd)
        if (!value) return { attributes, valid: false }
      }
    }
    attributes.push({ name, value, valueStart, valueEnd, quote })
  }
  return { attributes, valid: true }
}

function scanStartTags(html, nodeIdPattern) {
  const tags = []
  const stack = []
  const validNodeId = new RegExp(nodeIdPattern)
  let cursor = 0
  while (cursor < html.length) {
    const open = html.indexOf("<", cursor)
    if (open < 0) break
    if (html.startsWith("<!--", open)) {
      const commentEnd = html.indexOf("-->", open + 4)
      if (commentEnd < 0) break
      cursor = commentEnd + 3
      continue
    }

    const marker = html[open + 1]
    if (marker === "/") {
      let nameEnd = open + 2
      while (nameEnd < html.length && /[a-z0-9:-]/i.test(html[nameEnd])) nameEnd += 1
      const tagName = html.slice(open + 2, nameEnd).toLowerCase()
      const matchingIndex = stack.findLastIndex((item) => item.tagName === tagName)
      const tagEnd = findTagEnd(html, open + 2)
      if (tagEnd < 0) break
      if (matchingIndex >= 0) stack.length = matchingIndex
      cursor = tagEnd + 1
      continue
    }
    if (marker === "!" || marker === "?") {
      const tagEnd = findTagEnd(html, open + 2)
      if (tagEnd < 0) break
      cursor = tagEnd + 1
      continue
    }
    if (marker === undefined || !/[a-z]/i.test(marker)) {
      cursor = open + 1
      continue
    }

    let nameEnd = open + 1
    while (nameEnd < html.length && /[a-z0-9:-]/i.test(html[nameEnd])) nameEnd += 1
    const tagEnd = findTagEnd(html, nameEnd)
    if (tagEnd < 0) break
    const tagName = html.slice(open + 1, nameEnd).toLowerCase()
    const scanned = scanTagAttributes(html, nameEnd, tagEnd)
    const componentAttributes = scanned.attributes.filter(
      (item) => item.name === "data-component",
    )
    const nodeIdAttributes = scanned.attributes.filter(
      (item) => item.name === "data-node-id",
    )
    const component = componentAttributes.length === 1
      ? componentAttributes[0].value
      : null
    const nodeId = nodeIdAttributes.length === 1
      ? nodeIdAttributes[0].value
      : null
    let ancestorNodeId = null
    for (let index = stack.length - 1; index >= 0; index -= 1) {
      const ancestor = stack[index]
      if (
        ancestor.component !== null
        && ancestor.nodeId !== null
        && validNodeId.test(ancestor.nodeId)
      ) {
        ancestorNodeId = ancestor.nodeId
        break
      }
    }
    tags.push({
      ancestorNodeId,
      attributes: scanned.attributes,
      end: tagEnd,
      start: open,
      tagName,
      valid: scanned.valid,
    })
    cursor = tagEnd + 1

    if (rawTextTags.has(tagName)) {
      const closingPattern = new RegExp(`</${tagName}\\s*>`, "ig")
      closingPattern.lastIndex = cursor
      const closing = closingPattern.exec(html)
      cursor = closing ? closingPattern.lastIndex : html.length
      continue
    }
    let closeMarker = tagEnd - 1
    while (closeMarker >= 0 && isHtmlSpace(html[closeMarker])) closeMarker -= 1
    if (!voidTags.has(tagName) && html[closeMarker] !== "/") {
      stack.push({ component, nodeId, tagName })
    }
  }
  return tags
}

function insertionPointBeforeTagClose(html, tagEnd) {
  let index = tagEnd - 1
  while (index >= 0 && isHtmlSpace(html[index])) index -= 1
  return html[index] === "/" ? index : tagEnd
}

function requiredClassNormalization(html, tag, contract) {
  if (!tag.valid) return null
    const componentAttributes = tag.attributes.filter((item) => item.name === "data-component")
    if (componentAttributes.length !== 1) return null
    const component = componentAttributes[0].value
    if (!normalizableComponents.has(component)) return null

    const classAttributes = tag.attributes.filter((item) => item.name === "class")
    if (classAttributes.length > 1) return null
    const classAttribute = classAttributes[0] ?? null
    if (classAttribute !== null && classAttribute.value === null) return null
    const classValue = classAttribute?.value ?? ""
    const classes = new Set(classValue.split(/\s+/).filter(Boolean))
    const required = contract.components?.[component]?.classAll ?? []
    const missing = required.filter((item) => !classes.has(item))
    if (missing.length === 0) return null
    const conflicts = conflictingLayoutClasses.get(component) ?? new Set()
    if ([...classes].some((item) => conflicts.has(item))) return null

    const separator = !classValue || /\s$/.test(classValue) ? "" : " "
    const nextClassValue = `${classValue}${separator}${missing.join(" ")}`
    let edit
    if (classAttribute === null) {
      const insertionPoint = insertionPointBeforeTagClose(html, tag.end)
      edit = {
        end: insertionPoint,
        replacement: ` class="${nextClassValue}"`,
        start: insertionPoint,
      }
    } else if (classAttribute.quote !== null) {
      edit = {
        end: classAttribute.valueEnd,
        replacement: nextClassValue,
        start: classAttribute.valueStart,
      }
    } else {
      edit = {
        end: classAttribute.valueEnd,
        replacement: `"${nextClassValue}"`,
        start: classAttribute.valueStart,
      }
    }

    const nodeIdAttributes = tag.attributes.filter((item) => item.name === "data-node-id")
    return {
      edit,
      node: {
        nodeId: nodeIdAttributes.length === 1 ? nodeIdAttributes[0].value : null,
        component,
        addedClasses: missing,
      },
    }
}

function symbolNodeIdNormalization(html, tag, usedNodeIds, nodeIdPattern) {
  if (!tag.valid || tag.tagName !== "i" || tag.ancestorNodeId === null) return null
  const componentAttributes = tag.attributes.filter((item) => item.name === "data-component")
  if (componentAttributes.length !== 1 || componentAttributes[0].value !== "symbol") return null
  const nodeIdAttributes = tag.attributes.filter((item) => item.name === "data-node-id")
  if (nodeIdAttributes.length !== 0) return null
  const iconAttributes = tag.attributes.filter((item) => item.name === "data-lucide")
  if (iconAttributes.length !== 1) return null
  const iconName = iconAttributes[0].value
  if (iconName === null || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(iconName)) return null

  const base = `${tag.ancestorNodeId}.icon-${iconName}`
  let generatedNodeId = base
  let sequence = 2
  while (usedNodeIds.has(generatedNodeId)) {
    generatedNodeId = `${base}-${sequence}`
    sequence += 1
  }
  if (!new RegExp(nodeIdPattern).test(generatedNodeId)) return null
  usedNodeIds.add(generatedNodeId)
  const insertionPoint = insertionPointBeforeTagClose(html, tag.end)
  return {
    edit: {
      end: insertionPoint,
      replacement: ` data-node-id="${generatedNodeId}"`,
      start: insertionPoint,
    },
    node: {
      nodeId: generatedNodeId,
      component: "symbol",
      addedNodeId: generatedNodeId,
      ancestorNodeId: tag.ancestorNodeId,
      iconName,
    },
  }
}

function normalizeHtml(html, contract) {
  const edits = []
  const nodes = []
  const tags = scanStartTags(html, contract.nodeIdPattern)
  const usedNodeIds = new Set()
  for (const tag of tags) {
    for (const attribute of tag.attributes) {
      if (attribute.name === "data-node-id" && attribute.value !== null) {
        usedNodeIds.add(attribute.value)
      }
    }
  }
  for (const tag of tags) {
    const classNormalization = requiredClassNormalization(html, tag, contract)
    if (classNormalization !== null) {
      edits.push(classNormalization.edit)
      nodes.push(classNormalization.node)
    }
    const nodeIdNormalization = symbolNodeIdNormalization(
      html,
      tag,
      usedNodeIds,
      contract.nodeIdPattern,
    )
    if (nodeIdNormalization !== null) {
      edits.push(nodeIdNormalization.edit)
      nodes.push(nodeIdNormalization.node)
    }
  }

  let output = html
  for (const edit of edits.sort((left, right) => right.start - left.start)) {
    output = `${output.slice(0, edit.start)}${edit.replacement}${output.slice(edit.end)}`
  }
  return { html: output, nodes }
}

const builtinMediaOrientations = new Set(["portrait", "landscape", "squarish"])
const cjkPattern = /[\u3400-\u9fff]/
const humanQueryIntentKeywords = new Set([
  "athlete", "avatar", "boy", "colleague", "couple", "customer", "family",
  "friends", "girl", "headshot", "human", "man", "member", "party",
  "people", "person", "profile", "runner", "team", "user", "wedding",
  "woman", "人物", "人像", "头像", "男人", "女人", "朋友", "家庭",
  "团队", "顾客", "运动员",
])
const photoPeoplePresenceKeywords = new Set([
  "athlete", "boy", "bride", "child", "children", "colleague", "couple",
  "customer", "family", "friends", "girl", "groom", "headshot", "human",
  "lady", "man", "member", "people", "person", "runner", "selfie",
  "student", "woman", "人物", "人像", "头像", "男人", "女人", "朋友",
  "家庭", "顾客", "运动员",
])

function mediaTokens(value) {
  return new Set(
    (value.toLowerCase().match(/[a-z0-9]+/g) ?? [])
      .filter((item) => item.length >= 2),
  )
}

function mediaKeywordHits(keywords, tokens, text) {
  let hits = 0
  for (const rawKeyword of keywords ?? []) {
    const keyword = String(rawKeyword).trim().toLowerCase()
    if (!keyword) continue
    if (cjkPattern.test(keyword) ? text.includes(keyword) : tokens.has(keyword)) {
      hits += 1
    }
  }
  return hits
}

function mediaTiebreak(query, photoId) {
  return createHash("sha1").update(`${query}|${photoId}`).digest("hex")
}

function hasHumanMediaIntent(tokens, text) {
  return [...humanQueryIntentKeywords].some(
    (keyword) => cjkPattern.test(keyword) ? text.includes(keyword) : tokens.has(keyword),
  )
}

function hasPeopleInPhoto(categoryName, keywords) {
  if (categoryName === "avatar") return true
  return (keywords ?? []).some(
    (keyword) => photoPeoplePresenceKeywords.has(String(keyword).trim().toLowerCase()),
  )
}

function selectBuiltinPhoto(manifest, request, usedIds) {
  const categories = Object.entries(manifest.categories ?? {})
    .filter(([, category]) => category && typeof category === "object")
  if (categories.length === 0) fail("built-in media manifest has no categories")

  const text = request.query.toLowerCase()
  const tokens = mediaTokens(text)
  const fallbackNames = (manifest.fallback_categories ?? [])
    .map(String)
    .filter((name) => categories.some(([candidate]) => candidate === name))
  const queryWantsPeople = hasHumanMediaIntent(tokens, text)
  const candidates = []
  for (const [categoryName, category] of categories) {
    const categoryHits = mediaKeywordHits(category.match_keywords, tokens, text)
    const fallbackIndex = fallbackNames.indexOf(categoryName)
    for (const photo of category.photos ?? []) {
      const photoId = String(photo.id ?? "")
      const sourceFile = String(photo.files?.small ?? "")
      if (!photoId || !sourceFile || usedIds.has(photoId)) continue
      const photoHits = mediaKeywordHits(photo.keywords, tokens, text)
      const photoHasPeople = hasPeopleInPhoto(categoryName, photo.keywords)
      const orientationBonus = request.orientation && photo.orientation === request.orientation ? 1 : 0
      const peoplePenalty = photoHasPeople && !queryWantsPeople ? 6 : 0
      candidates.push({
        category: categoryName,
        categoryHits,
        fallbackRank: fallbackIndex >= 0 ? fallbackIndex : fallbackNames.length + 1,
        orientationBonus,
        photo,
        photoHasPeople,
        photoHits,
        score: 4 * photoHits + 2 * categoryHits + orientationBonus - peoplePenalty,
        sourceFile,
        tiebreak: mediaTiebreak(request.query, photoId),
      })
    }
  }

  const semanticCandidates = candidates.filter(
    (candidate) => candidate.photoHits > 0 || candidate.categoryHits > 0,
  )
  const ranked = (semanticCandidates.length > 0 ? semanticCandidates : candidates)
    .sort((left, right) => {
      if (semanticCandidates.length > 0) {
        return right.score - left.score
          || right.photoHits - left.photoHits
          || right.categoryHits - left.categoryHits
          || left.tiebreak.localeCompare(right.tiebreak)
      }
      return Number(left.photoHasPeople) - Number(right.photoHasPeople)
        || left.fallbackRank - right.fallbackRank
        || right.orientationBonus - left.orientationBonus
        || left.tiebreak.localeCompare(right.tiebreak)
    })
  const selected = ranked[0] ?? null
  if (selected !== null) {
    usedIds.add(String(selected.photo.id))
    return {
      category: selected.category,
      photo: selected.photo,
      sourceFile: selected.sourceFile,
    }
  }
  fail(`built-in media library has no unused photo for query: ${request.query}`)
}

function uniqueTagAttribute(tag, name) {
  const matches = tag.attributes.filter((item) => item.name === name)
  if (matches.length > 1) fail(`<${tag.tagName}> has duplicate ${name} attributes`)
  return matches[0] ?? null
}

function replaceOrInsertAttribute(html, tag, name, value) {
  const attribute = uniqueTagAttribute(tag, name)
  if (attribute === null) {
    const insertionPoint = insertionPointBeforeTagClose(html, tag.end)
    return {
      end: insertionPoint,
      replacement: ` ${name}="${value}"`,
      start: insertionPoint,
    }
  }
  if (attribute.value === null) fail(`${name} must have a value on <${tag.tagName}>`)
  return {
    end: attribute.valueEnd,
    replacement: attribute.quote === null ? `"${value}"` : value,
    start: attribute.valueStart,
  }
}

function safeMediaSource(mediaLibraryDir, sourceFile) {
  const sourcePath = resolve(mediaLibraryDir, sourceFile)
  const relativePath = relative(mediaLibraryDir, sourcePath)
  if (
    relativePath === ".."
    || relativePath.startsWith(`..${sep}`)
    || isAbsolute(relativePath)
  ) {
    fail(`built-in media path escapes the library: ${sourceFile}`)
  }
  if (!existsSync(sourcePath)) fail(`built-in media file is missing: ${sourceFile}`)
  const sourceStat = lstatSync(sourcePath)
  if (sourceStat.isSymbolicLink() || !sourceStat.isFile()) {
    fail(`built-in media source must be a regular file: ${sourceFile}`)
  }
  const realLibraryDir = realpathSync(mediaLibraryDir)
  const realSourcePath = realpathSync(sourcePath)
  const realRelativePath = relative(realLibraryDir, realSourcePath)
  if (
    realRelativePath === ".."
    || realRelativePath.startsWith(`..${sep}`)
    || isAbsolute(realRelativePath)
  ) {
    fail(`built-in media real path escapes the library: ${sourceFile}`)
  }
  return {
    relativePath: relativePath.split(sep).join("/"),
    sourcePath,
  }
}

function resolveBuiltinMedia(html, manifest, mediaLibraryDir, contract) {
  const edits = []
  const items = []
  const usedIds = new Set()
  const tags = scanStartTags(html, contract.nodeIdPattern)
  const mediaTags = tags.filter(
    (tag) => tag.attributes.some((item) => item.name === "data-media-query"),
  )
  if (mediaTags.length > 8) fail("a page can request at most 8 built-in photos")

  for (const tag of mediaTags) {
    const queryAttribute = uniqueTagAttribute(tag, "data-media-query")
    const orientationAttribute = uniqueTagAttribute(tag, "data-media-orientation")
    const componentAttribute = uniqueTagAttribute(tag, "data-component")
    const nodeIdAttribute = uniqueTagAttribute(tag, "data-node-id")
    const srcAttribute = uniqueTagAttribute(tag, "src")
    const query = String(queryAttribute?.value ?? "").trim()
    const orientation = String(orientationAttribute?.value ?? "").trim().toLowerCase()
    const nodeId = String(nodeIdAttribute?.value ?? "").trim() || null
    const existingSrc = String(srcAttribute?.value ?? "").trim()
    if (tag.tagName !== "img" || componentAttribute?.value !== "image") {
      fail("data-media-query is only supported on <img data-component=\"image\">")
    }
    if (!query) fail(`data-media-query must be non-empty${nodeId ? ` [${nodeId}]` : ""}`)
    if (orientation && !builtinMediaOrientations.has(orientation)) {
      fail(`invalid data-media-orientation: ${orientation}${nodeId ? ` [${nodeId}]` : ""}`)
    }
    if (existingSrc && !/^(?:\.\/)?assets\/media\/builtin\//.test(existingSrc)) {
      fail(`data-media-query cannot replace a user-provided src${nodeId ? ` [${nodeId}]` : ""}`)
    }

    const selected = selectBuiltinPhoto(manifest, { orientation, query }, usedIds)
    const source = safeMediaSource(mediaLibraryDir, selected.sourceFile)
    const outputRelative = `assets/media/builtin/${source.relativePath}`
    edits.push(replaceOrInsertAttribute(html, tag, "src", outputRelative))
    items.push({
      category: selected.category,
      nodeId,
      orientation: orientation || null,
      outputRelative,
      photoId: String(selected.photo.id),
      photographer: String(selected.photo.photographer ?? ""),
      query,
      sourcePath: source.sourcePath,
      sourceRelative: source.relativePath,
    })
  }

  let output = html
  for (const edit of edits.sort((left, right) => right.start - left.start)) {
    output = `${output.slice(0, edit.start)}${edit.replacement}${output.slice(edit.end)}`
  }
  return { html: output, items }
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

function makeOwnerWritable(path) {
  if (!existsSync(path)) return
  const stat = lstatSync(path)
  if (stat.isSymbolicLink()) return
  const permissionBits = stat.mode & 0o777
  if (stat.isDirectory()) {
    chmodSync(path, permissionBits | 0o700)
    for (const entry of readdirSync(path)) {
      makeOwnerWritable(join(path, entry))
    }
    return
  }
  chmodSync(path, permissionBits | 0o600)
}

function lstatOrNull(path) {
  try {
    return lstatSync(path)
  } catch (error) {
    if (error?.code === "ENOENT") return null
    throw error
  }
}

function pathIsWithin(root, candidate) {
  const relativePath = relative(root, candidate)
  return relativePath === ""
    || (!relativePath.startsWith(`..${sep}`) && relativePath !== ".." && !isAbsolute(relativePath))
}

function canonicalizeOutputPath(path) {
  let ancestor = path
  while (lstatOrNull(ancestor) === null) {
    const parent = dirname(ancestor)
    if (parent === ancestor) break
    ancestor = parent
  }
  return resolve(realpathSync(ancestor), relative(ancestor, path))
}

function assertSafeOutputDestination(outputDir, destination) {
  if (!pathIsWithin(outputDir, destination)) {
    fail(`output asset path escapes --out: ${destination}`)
  }
  let cursor = destination
  while (pathIsWithin(outputDir, cursor)) {
    const stat = lstatOrNull(cursor)
    if (stat?.isSymbolicLink()) {
      fail(`output asset path must not contain symbolic links: ${cursor}`)
    }
    if (cursor === outputDir) break
    cursor = dirname(cursor)
  }
}

function replaceCopiedAsset(
  source,
  destination,
  { outputDir, recursive = false } = {},
) {
  assertSafeOutputDestination(outputDir, destination)
  if (!existsSync(source)) fail(`bundled asset is missing: ${source}`)
  if (
    resolve(source) === resolve(destination)
    || (existsSync(destination) && realpathSync(source) === realpathSync(destination))
  ) {
    fail(`bundled asset source and destination must differ: ${source}`)
  }
  if (existsSync(destination)) {
    makeOwnerWritable(destination)
    rmSync(destination, { recursive, force: true })
  }
  if (recursive) {
    cpSync(source, destination, { recursive: true, force: true })
  } else {
    copyFileSync(source, destination)
  }
  // OpenCode snapshots Skills read-only. Keep generated copies owner-writable so
  // a validation repair can rerun this script without failing with EACCES.
  makeOwnerWritable(destination)
}

function removeCopiedAsset(destination, outputDir) {
  assertSafeOutputDestination(outputDir, destination)
  if (!existsSync(destination)) return
  makeOwnerWritable(destination)
  rmSync(destination, { recursive: true, force: true })
}

function copyBuiltinMedia(items, assetsDir, outputDir) {
  const outputRoot = join(assetsDir, "media", "builtin")
  removeCopiedAsset(outputRoot, outputDir)
  for (const item of items) {
    const destination = join(outputRoot, item.sourceRelative)
    assertSafeOutputDestination(outputDir, dirname(destination))
    mkdirSync(dirname(destination), { recursive: true })
    replaceCopiedAsset(item.sourcePath, destination, { outputDir })
  }
}

const args = parseArgs(process.argv.slice(2))
if (!args.input) fail("--input is required")
if (!args.out) fail("--out is required")
const theme = args.theme ?? "light"
if (!new Set(["light", "dark"]).has(theme)) fail("--theme must be light or dark")
const inputPath = resolve(args.input)
const requestedOutputDir = resolve(args.out)
if (!existsSync(inputPath)) fail(`input does not exist: ${inputPath}`)
const scriptDir = dirname(fileURLToPath(import.meta.url))
const skillDir = resolve(scriptDir, "..")
const outputDir = canonicalizeOutputPath(requestedOutputDir)
if (pathIsWithin(realpathSync(skillDir), outputDir)) {
  fail("--out must not be the Skill directory or one of its descendants")
}
const iconMap = JSON.parse(readFileSync(join(skillDir, "references", "icon-map.json"), "utf8"))
const contract = JSON.parse(readFileSync(join(skillDir, "references", "component-contract.json"), "utf8"))
const mediaLibraryDir = join(skillDir, "assets", "media-library")
const mediaManifest = JSON.parse(readFileSync(join(mediaLibraryDir, "manifest.json"), "utf8"))

let html = readFileSync(inputPath, "utf8")
if (!html.trim()) fail("input HTML is empty")
html = materializeIcons(html, iconMap)
const builtinMedia = resolveBuiltinMedia(html, mediaManifest, mediaLibraryDir, contract)
html = builtinMedia.html
html = installRuntime(html, {
  title: args.title?.trim() || "HarmonyOS 页面",
  theme,
})
const normalized = normalizeHtml(html, contract)
html = normalized.html

const assetsDir = join(outputDir, "assets")
assertSafeOutputDestination(outputDir, assetsDir)
mkdirSync(assetsDir, { recursive: true })
replaceCopiedAsset(
  join(skillDir, "assets", "harmony-runtime.css"),
  join(assetsDir, "harmony-runtime.css"),
  { outputDir },
)
replaceCopiedAsset(
  join(skillDir, "assets", "fonts"),
  join(assetsDir, "fonts"),
  { outputDir, recursive: true },
)
copyBuiltinMedia(builtinMedia.items, assetsDir, outputDir)
const outputPath = join(outputDir, "index.html")
assertSafeOutputDestination(outputDir, outputPath)
writeFileSync(outputPath, html, "utf8")
console.log(JSON.stringify({
  ok: true,
  input: inputPath,
  output: outputPath,
  theme,
  runtime: join(assetsDir, "harmony-runtime.css"),
  media: {
    count: builtinMedia.items.length,
    items: builtinMedia.items.map((item) => ({
      category: item.category,
      nodeId: item.nodeId,
      orientation: item.orientation,
      output: item.outputRelative,
      photoId: item.photoId,
      photographer: item.photographer,
      query: item.query,
    })),
  },
  normalizations: {
    count: normalized.nodes.length,
    nodes: normalized.nodes,
  },
}, null, 2))
