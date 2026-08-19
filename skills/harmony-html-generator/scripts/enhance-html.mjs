#!/usr/bin/env node

import { createHash } from "node:crypto"
import { spawnSync } from "node:child_process"
import {
  chmodSync,
  copyFileSync,
  existsSync,
  lstatSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  readdirSync,
  realpathSync,
  renameSync,
  rmSync,
  writeFileSync,
} from "node:fs"
import { basename, dirname, isAbsolute, join, relative, resolve, sep } from "node:path"
import { TextDecoder } from "node:util"
import { fileURLToPath } from "node:url"

const limits = Object.freeze({
  maxDepth: 32,
  maxDirectories: 1_000,
  maxFileBytes: 32 * 1024 * 1024,
  maxFiles: 1_000,
  maxScriptBytes: 256 * 1024,
  maxTotalBytes: 100 * 1024 * 1024,
})

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
    if (!new Set(["input", "script", "out"]).has(key)) fail(`unknown argument ${arg}`)
    if (Object.hasOwn(values, key)) fail(`duplicate argument ${arg}`)
    const value = argv[index + 1]
    if (!value || value.startsWith("--")) fail(`missing value for ${arg}`)
    values[key] = value
    index += 1
  }
  for (const key of ["input", "script", "out"]) {
    if (!values[key]) fail(`--${key} is required`)
  }
  return values
}

function isWithin(parent, candidate) {
  const child = relative(parent, candidate)
  return child === "" || (
    child !== ".."
    && !child.startsWith(`..${sep}`)
    && !isAbsolute(child)
  )
}

function regularFile(path, label) {
  if (!existsSync(path)) throw new Error(`${label} does not exist: ${path}`)
  const item = lstatSync(path)
  if (item.isSymbolicLink() || !item.isFile()) {
    throw new Error(`${label} must be a regular file: ${path}`)
  }
  return item
}

function regularDirectory(path, label) {
  if (!existsSync(path)) throw new Error(`${label} does not exist: ${path}`)
  const item = lstatSync(path)
  if (item.isSymbolicLink() || !item.isDirectory()) {
    throw new Error(`${label} must be a regular directory: ${path}`)
  }
  return item
}

function copyTree(source, destination) {
  const state = { directories: 0, files: 0, totalBytes: 0 }
  mkdirSync(destination, { mode: 0o755 })

  function visit(sourceDir, destinationDir, depth) {
    if (depth > limits.maxDepth) throw new Error("static package exceeds the directory-depth limit")
    for (const name of readdirSync(sourceDir)) {
      const sourcePath = join(sourceDir, name)
      const destinationPath = join(destinationDir, name)
      const item = lstatSync(sourcePath)
      if (item.isSymbolicLink()) throw new Error(`static package contains a symbolic link: ${sourcePath}`)
      if (item.isDirectory()) {
        state.directories += 1
        if (state.directories > limits.maxDirectories) {
          throw new Error("static package exceeds the directory-count limit")
        }
        mkdirSync(destinationPath, { mode: 0o755 })
        visit(sourcePath, destinationPath, depth + 1)
        continue
      }
      if (!item.isFile()) throw new Error(`static package contains a non-regular file: ${sourcePath}`)
      state.files += 1
      state.totalBytes += item.size
      if (state.files > limits.maxFiles) throw new Error("static package exceeds the file-count limit")
      if (item.size > limits.maxFileBytes) throw new Error(`static package file is too large: ${sourcePath}`)
      if (state.totalBytes > limits.maxTotalBytes) throw new Error("static package exceeds the total-size limit")
      copyFileSync(sourcePath, destinationPath)
      chmodSync(destinationPath, 0o644)
    }
  }

  visit(source, destination, 0)
  return state
}

function runNode(script, args) {
  const result = spawnSync(process.execPath, [script, ...args], {
    encoding: "utf8",
    maxBuffer: 2 * 1024 * 1024,
  })
  return {
    error: result.error ? String(result.error.message ?? result.error) : "",
    status: result.status,
    stderr: result.stderr ?? "",
    stdout: result.stdout ?? "",
  }
}

function commandFailure(result) {
  return [result.error, result.stdout, result.stderr]
    .filter(Boolean)
    .join("\n")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, 4_000) || `process exited with status ${result.status}`
}

function publish(stage, outputDir) {
  if (existsSync(outputDir)) throw new Error(`output already exists: ${outputDir}`)
  renameSync(stage, outputDir)
}

function sha256(path) {
  return createHash("sha256").update(readFileSync(path)).digest("hex")
}

const args = parseArgs(process.argv.slice(2))
const scriptDir = dirname(fileURLToPath(import.meta.url))
const staticValidator = join(scriptDir, "validate-html.mjs")
const interactiveValidator = join(scriptDir, "validate-interactive.mjs")
const requestedInputDir = resolve(args.input)
const requestedOutputDir = resolve(args.out)

try {
  regularDirectory(requestedInputDir, "--input")
  regularFile(staticValidator, "static validator")
} catch (error) {
  fail(error.message)
}

const inputDir = realpathSync(requestedInputDir)
const inputIndex = join(inputDir, "index.html")
try {
  regularFile(inputIndex, "static index.html")
} catch (error) {
  fail(error.message)
}

mkdirSync(dirname(requestedOutputDir), { recursive: true })
const outputParent = realpathSync(dirname(requestedOutputDir))
const outputDir = join(outputParent, basename(requestedOutputDir))
if (existsSync(outputDir)) fail(`--out must not already exist: ${outputDir}`)
if (isWithin(inputDir, outputDir) || isWithin(outputDir, inputDir)) {
  fail("--input and --out must be separate, non-nested directories")
}

const baselineValidation = runNode(staticValidator, [inputIndex])
if (baselineValidation.status !== 0 || baselineValidation.error) {
  fail(`static baseline is not valid; no fallback can be guaranteed: ${commandFailure(baselineValidation)}`)
}

let stage = null
let fallbackReason = ""
try {
  stage = mkdtempSync(join(outputParent, ".harmony-interaction-"))
  rmSync(stage, { recursive: true, force: true })
  copyTree(inputDir, stage)

  const sourceScript = resolve(args.script)
  const scriptStat = regularFile(sourceScript, "--script")
  if (scriptStat.size > limits.maxScriptBytes) {
    throw new Error(`--script exceeds ${limits.maxScriptBytes} bytes`)
  }
  const scriptBytes = readFileSync(sourceScript)
  const scriptText = new TextDecoder("utf-8", { fatal: true }).decode(scriptBytes)
  if (!scriptText.trim() || scriptText.includes("\0")) {
    throw new Error("--script must be non-empty UTF-8 without NUL characters")
  }
  const syntaxCheck = runNode("--check", [sourceScript])
  if (syntaxCheck.status !== 0 || syntaxCheck.error) {
    throw new Error(`JavaScript syntax check failed: ${commandFailure(syntaxCheck)}`)
  }

  const appScript = join(stage, "assets", "app.js")
  if (existsSync(appScript)) throw new Error("static package already contains assets/app.js")
  mkdirSync(dirname(appScript), { recursive: true })
  writeFileSync(appScript, scriptText, { encoding: "utf8", mode: 0o644 })

  const stageIndex = join(stage, "index.html")
  const staticHtml = readFileSync(stageIndex, "utf8")
  const closingBody = staticHtml.match(/<\/body\s*>/i)
  if (!closingBody || closingBody.index === undefined) {
    throw new Error("static index.html has no closing body tag")
  }
  const scriptTag = '<script src="assets/app.js" defer></script>'
  const interactiveHtml = `${staticHtml.slice(0, closingBody.index)}${scriptTag}\n${staticHtml.slice(closingBody.index)}`
  writeFileSync(stageIndex, interactiveHtml, "utf8")

  const validation = runNode(interactiveValidator, [stageIndex])
  if (validation.status !== 0 || validation.error) {
    throw new Error(`interactive validation failed: ${commandFailure(validation)}`)
  }

  const baselineSha256 = sha256(inputIndex)
  const interactiveSha256 = sha256(stageIndex)
  publish(stage, outputDir)
  stage = null
  console.log(JSON.stringify({
    ok: true,
    mode: "interactive",
    output: join(outputDir, "index.html"),
    script: join(outputDir, "assets", "app.js"),
    baselineSha256,
    interactiveSha256,
  }, null, 2))
} catch (error) {
  fallbackReason = String(error?.message ?? error)
} finally {
  if (stage !== null) rmSync(stage, { recursive: true, force: true })
}

if (fallbackReason) {
  try {
    stage = mkdtempSync(join(outputParent, ".harmony-static-fallback-"))
    rmSync(stage, { recursive: true, force: true })
    copyTree(inputDir, stage)
    publish(stage, outputDir)
    stage = null
  } catch (error) {
    if (stage !== null) rmSync(stage, { recursive: true, force: true })
    fail(`interaction failed and static fallback could not be published: ${error.message}; interaction error: ${fallbackReason}`)
  }
  console.error(`WARNING: interaction enhancement failed; published the validated static baseline: ${fallbackReason}`)
  console.log(JSON.stringify({
    ok: true,
    mode: "fallback-static",
    output: join(outputDir, "index.html"),
    baselineSha256: sha256(inputIndex),
    interactionError: fallbackReason.slice(0, 4_000),
  }, null, 2))
}
