#!/usr/bin/env node

import { spawn } from "node:child_process"
import { existsSync, readdirSync, statSync } from "node:fs"
import { dirname, extname, join, relative, resolve } from "node:path"
import { fileURLToPath } from "node:url"

import { findDesignSystemRoot, isInsideOrEqual, skillDir, sourceRoot } from "./shared.mjs"
import { tmpdir } from "node:os"

const usage = `Usage:
  node validate-source-fast.mjs <target>
    [--with-eslint]
    [--eslint-file <path>]...
    [--page-build-requested]

In design-system mode, runs artifact validation and TypeScript concurrently.
In standalone mode, <target> must be the generated Babel-template HTML file;
the validator checks that file and its embedded TSX only.
HMSymbol validation is triggered by the artifact validator.
ESLint runs only in design-system mode when --with-eslint or at least one --eslint-file is provided.
With --with-eslint and no --eslint-file, source files under <target-dir> are selected automatically.`

const args = process.argv.slice(2)
if (args.includes("--help") || args.includes("-h")) {
  console.log(usage)
  process.exit(0)
}

let targetArg = null
let pageBuildRequested = false
let withEslint = false
const eslintFiles = []

for (let index = 0; index < args.length; index += 1) {
  const arg = args[index]
  if (arg === "--with-eslint") {
    withEslint = true
    continue
  }
  if (arg === "--page-build-requested") {
    pageBuildRequested = true
    continue
  }
  if (arg === "--eslint-file") {
    const value = args[index + 1]
    if (!value || value.startsWith("--")) {
      console.error(`Missing value for --eslint-file\n\n${usage}`)
      process.exit(2)
    }
    eslintFiles.push(resolve(value))
    withEslint = true
    index += 1
    continue
  }
  if (arg.startsWith("--")) {
    console.error(`Unknown option: ${arg}\n\n${usage}`)
    process.exit(2)
  }
  if (targetArg) {
    console.error(`Unexpected positional argument: ${arg}\n\n${usage}`)
    process.exit(2)
  }
  targetArg = arg
}

if (!targetArg) {
  console.error(usage)
  process.exit(2)
}

const targetPath = resolve(targetArg)
if (!existsSync(targetPath)) {
  console.error(`Validation target does not exist: ${targetPath}`)
  process.exit(2)
}

const scriptDir = dirname(fileURLToPath(import.meta.url))
const projectDir = process.cwd()
const artifactValidator = join(scriptDir, "validate-page-artifact.mjs")
const designSystemMode = false
const targetStats = statSync(targetPath)

if (designSystemMode && !targetStats.isDirectory()) {
  console.error(`Design-system validation target must be a directory: ${targetPath}`)
  process.exit(2)
}
if (
  !designSystemMode &&
  (!targetStats.isFile() || extname(targetPath) !== ".html")
) {
  console.error(`Standalone validation target must be an HTML file: ${targetPath}`)
  process.exit(2)
}

// Standalone 最高指令 Point 3：HTML 不得放在 skill 自身目录、项目 src/、系统临时目录
if (!designSystemMode) {
  const forbiddenParents = [
    { path: skillDir, label: "skill 自身目录" },
    { path: tmpdir(), label: "系统临时目录" },
  ]

  // 即使当前是 standalone 模式，也要检测 target 是否被写入了某个 design-system 项目的 src/
  const targetDesignSystemRoot = findDesignSystemRoot(dirname(targetPath), {
    excludedRoots: [skillDir],
  })
  if (targetDesignSystemRoot) {
    forbiddenParents.push({
      path: join(targetDesignSystemRoot, "src"),
      label: `design-system 项目 src/ 目录（${targetDesignSystemRoot}/src）`,
    })
  }

  const violated = forbiddenParents.filter(({ path }) => {
    try {
      return isInsideOrEqual(targetPath, path)
    } catch {
      return false
    }
  })

  if (violated.length) {
    console.error(
      `[fast-validation] 违禁路径: standalone HTML 不得放在以下目录中:\n${violated.map((v) => `  - ${v.label}: ${v.path}`).join("\n")}\n` +
        `当前路径: ${targetPath}\n` +
        `请将 .shadcn.html 输出到 agent 产物目录（独立于 skill、项目 src、临时目录之外的目录）。`,
    )
    process.exit(2)
  }
}
const eslintCli = designSystemMode
  ? join(projectDir, "node_modules/eslint/bin/eslint.js")
  : null
const tscCli = designSystemMode
  ? join(projectDir, "node_modules/typescript/bin/tsc")
  : null

const requiredPaths = [artifactValidator]
if (tscCli) requiredPaths.push(tscCli)
if (designSystemMode && withEslint && eslintCli) requiredPaths.push(eslintCli)

for (const requiredPath of requiredPaths) {
  if (!existsSync(requiredPath)) {
    console.error(`Required validation executable is missing: ${requiredPath}`)
    process.exit(2)
  }
}

function collectLintFiles(dir) {
  const files = []
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (["node_modules", "dist", "storybook-static"].includes(entry.name)) continue
    const path = join(dir, entry.name)
    if (entry.isDirectory()) files.push(...collectLintFiles(path))
    else if ([".ts", ".tsx", ".js", ".jsx"].includes(extname(entry.name))) files.push(path)
  }
  return files
}

const selectedLintFiles = designSystemMode && withEslint
  ? eslintFiles.length
    ? eslintFiles
    : collectLintFiles(targetPath)
  : []
if (designSystemMode && withEslint && !selectedLintFiles.length) {
  console.error(`No ESLint source files found under: ${targetPath}`)
  process.exit(2)
}

function run(name, script, commandArgs) {
  const started = Date.now()
  console.log(`[fast-validation] START ${name}`)
  return new Promise((resolvePromise) => {
    const child = spawn(process.execPath, [script, ...commandArgs], {
      cwd: projectDir,
      stdio: "inherit",
    })
    child.on("error", (error) => {
      console.error(`[fast-validation] ERROR ${name}: ${error.message}`)
      resolvePromise({ name, status: 1, durationMs: Date.now() - started })
    })
    child.on("exit", (status, signal) => {
      const resolvedStatus = status ?? 1
      console.log(
        `[fast-validation] END ${name} status=${resolvedStatus} duration=${Date.now() - started}ms${signal ? ` signal=${signal}` : ""}`,
      )
      resolvePromise({ name, status: resolvedStatus, durationMs: Date.now() - started })
    })
  })
}

const artifactArgs = [targetPath]
if (pageBuildRequested) artifactArgs.push("--page-build-requested")
if (!designSystemMode) artifactArgs.push("--standalone")

const started = Date.now()
const jobs = [
  run("artifact", artifactValidator, artifactArgs),
]

console.log(`[fast-validation] SOURCE mode=standalone root=${sourceRoot}`)

if (designSystemMode && tscCli) {
  jobs.push(run("typescript", tscCli, ["--noEmit"]))
} else {
  console.log("[fast-validation] SKIP typescript (standalone mode)")
}

if (designSystemMode && withEslint && eslintCli) {
  jobs.push(run("eslint", eslintCli, selectedLintFiles.map((file) => relative(projectDir, file))))
} else if (!designSystemMode) {
  console.log("[fast-validation] SKIP eslint (standalone mode)")
} else {
  console.log("[fast-validation] SKIP eslint (use --with-eslint to enable)")
}

const results = await Promise.all(jobs)

const failed = results.filter((result) => result.status !== 0)
console.log(`[fast-validation] TOTAL duration=${Date.now() - started}ms`)

if (failed.length) {
  console.error(
    `[fast-validation] FAILED: ${failed.map((result) => `${result.name}(${result.status})`).join(", ")}`,
  )
  process.exit(1)
}

console.log("[fast-validation] PASSED")
