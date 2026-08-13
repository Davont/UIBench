#!/usr/bin/env node
// prepare-template-merge.mjs
//
// Walks a top-level page template's import graph, recursively collects all
// nested `src/pages/**` templates, inlines them into a single TSX file.
// Imports are passed through as-is (no package specifier rewriting).
// Producing the merged TSX + CSS in one command makes Step 3 of
// standalone page generation deterministic and removes recursion-deduplication bugs.
//
// Two output modes:
//
//   standalone  → --out <merged.tsx> --css-out <merged.css>
//                  Inlines every nested template body into one TSX, inlines
//                  every sibling .css into <style>{styles}</style>.
//
//   design-system → --out-dir <target>
//                  Copies each template file (TSX/CSS/Story) into <target>,
//                  rewriting relative imports so the copies form a self-
//                  contained subgraph.
//
// Source-root resolution:
//   --source-root <dir>  Use this as the "@/" base.
//   Auto: try CWD upward for src/route-index.md + src/pages-specs/layout/;
//   if not found, fall back to <skill-dir>/src (the standalone snapshot).
//
// Usage:
//   node prepare-template-merge.mjs <top-tsx> --mode <m> [opts]
//
// Options:
//   --mode <standalone|design-system>   (required)
//   --out <file>                        (standalone) merged TSX output
//   --css-out <file>                    (standalone) merged CSS output
//   --out-dir <dir>                     (design-system) target directory
//   --source-root <dir>                 override source root
//   --top-component <Name>              component name to keep as the entry
//                                       default export (standalone only)

import { existsSync, mkdirSync, readFileSync, writeFileSync, statSync } from "node:fs"
import { dirname, isAbsolute, join, relative, resolve, sep } from "node:path"
import { fileURLToPath } from "node:url"

import { parse, traverse, generate, types as t } from "./babel.mjs"

const scriptDir = dirname(fileURLToPath(import.meta.url))
const skillDir = resolve(scriptDir, "..")

// ----------------------------------------------------------------------------
// CLI parsing
// ----------------------------------------------------------------------------

function printUsage() {
  console.log(`Usage:
  node prepare-template-merge.mjs <top-tsx> --mode <standalone|design-system> [opts]

Standalone:
  --out <file>          merged TSX output (required)
  --css-out <file>      merged CSS output (required)
  --top-component <N>   name of the entry component to expose as default

Design-system:
  --out-dir <dir>       target directory (required)

Common:
  --source-root <dir>   override source root (otherwise auto-detected)
`)
}

const argv = process.argv.slice(2)
if (argv.length === 0 || argv.includes("--help") || argv.includes("-h")) {
  printUsage()
  process.exit(argv.length === 0 ? 2 : 0)
}

const opts = {
  top: null,
  mode: null,
  out: null,
  cssOut: null,
  outDir: null,
  sourceRoot: null,
  topComponent: null,
}

for (let i = 0; i < argv.length; i++) {
  const a = argv[i]
  if (a === "--mode") opts.mode = argv[++i]
  else if (a === "--out") opts.out = argv[++i]
  else if (a === "--css-out") opts.cssOut = argv[++i]
  else if (a === "--out-dir") opts.outDir = argv[++i]
  else if (a === "--source-root") opts.sourceRoot = argv[++i]
  else if (a === "--top-component") opts.topComponent = argv[++i]
  else if (a.startsWith("--")) {
    console.error(`Unknown option: ${a}`)
    process.exit(2)
  } else if (!opts.top) {
    opts.top = resolve(a)
  } else {
    console.error(`Unexpected positional arg: ${a}`)
    process.exit(2)
  }
}

if (!opts.top || !opts.mode) {
  console.error("Missing required args.\n")
  printUsage()
  process.exit(2)
}
if (opts.mode === "standalone") {
  if (!opts.out || !opts.cssOut) {
    console.error("standalone mode requires --out and --css-out.\n")
    printUsage()
    process.exit(2)
  }
} else if (opts.mode === "design-system") {
  if (!opts.outDir) {
    console.error("design-system mode requires --out-dir.\n")
    printUsage()
    process.exit(2)
  }
} else {
  console.error(`Unknown --mode: ${opts.mode}`)
  process.exit(2)
}

// ----------------------------------------------------------------------------
// Source-root auto-detection
// ----------------------------------------------------------------------------

function detectSourceRoot() {
  // 1. Explicit override
  if (opts.sourceRoot) return resolve(opts.sourceRoot)
  // 2. Walk up from CWD looking for src/route-index.md + src/pages-specs/layout
  let cur = process.cwd()
  for (let i = 0; i < 8; i++) {
    const candidate = join(cur, "src")
    if (
      existsSync(join(candidate, "route-index.md")) &&
      existsSync(join(candidate, "pages-specs", "layout"))
    ) {
      return candidate
    }
    const parent = dirname(cur)
    if (parent === cur) break
    cur = parent
  }
  // 3. Fallback: skill's own src snapshot
  return join(skillDir, "src")
}

const SOURCE_ROOT = detectSourceRoot()

// ----------------------------------------------------------------------------
// Import classification
// ----------------------------------------------------------------------------
// Returns one of:
//   { kind: "external", spec }  (bare specifier, passed through as-is)
//   { kind: "pages-nested", abs }  (a src/pages/** template to inline)
//   { kind: "css-local", abs }  (./foo.css side-effect import)
//   { kind: "local-helper", abs }  (./foo.tsx non-template helper to inline)
//   { kind: "forbidden", spec }  (anything else — error)

function classifyImport(spec, sourceFile, sourceRootDir) {
  const fromDir = dirname(sourceFile)
  const resolveAbs = (p) =>
    isAbsolute(p) ? p : resolve(fromDir, p)

  // Bare specifiers — pass through as-is (no rewriting)
  if (
    spec === "react" ||
    spec === "react-dom" ||
    spec === "react-dom/client" ||
    spec === "react/jsx-runtime" ||
    spec === "react/jsx-dev-runtime"
  ) {
    return { kind: "external", spec }
  }

  // @/ aliases — pass through as-is
  if (
    spec.startsWith("@/components/") ||
    spec.startsWith("@/container-components/") ||
    spec === "@/lib/utils" ||
    spec.startsWith("@/lib/") ||
    spec.startsWith("@/blocks/") ||
    spec === "@/blocks"
  ) {
    return { kind: "external", spec }
  }

  // @/pages/** → nested template under SOURCE_ROOT/pages/**
  if (spec.startsWith("@/pages/") || spec === "@/pages") {
    const rel = spec.slice("@/pages".length).replace(/^[/]+/, "")
    const baseAbs = rel ? resolve(sourceRootDir, "pages", rel) : resolve(sourceRootDir, "pages")
    for (const ext of ["", ".ts", ".tsx", "/index.ts", "/index.tsx"]) {
      const candidate = baseAbs + ext
      if (existsSync(candidate) && statSync(candidate).isFile()) {
        return classifyLocalFile(candidate, sourceRootDir)
      }
    }
    return { kind: "forbidden", spec }
  }

  // Relative CSS
  if (spec.endsWith(".css")) {
    return { kind: "css-local", abs: resolveAbs(spec) }
  }

  // Relative .ts/.tsx
  if (spec.endsWith(".ts") || spec.endsWith(".tsx")) {
    const abs = resolveAbs(spec)
    return classifyLocalFile(abs, sourceRootDir)
  }

  // Relative without extension (. or ./foo)
  if (spec.startsWith("./") || spec.startsWith("../")) {
    // Try common extensions
    const baseAbs = resolveAbs(spec)
    for (const ext of ["", ".ts", ".tsx", "/index.ts", "/index.tsx"]) {
      const candidate = baseAbs + ext
      if (existsSync(candidate) && statSync(candidate).isFile()) {
        if (candidate.endsWith(".css")) return { kind: "css-local", abs: candidate }
        return classifyLocalFile(candidate, sourceRootDir)
      }
    }
  }

  return { kind: "forbidden", spec }
}

function classifyLocalFile(absPath, sourceRootDir) {
  // Template? anything under sourceRoot/pages/**
  const pagesDir = join(sourceRootDir, "pages")
  const normalizedPages = pagesDir.endsWith(sep) ? pagesDir : pagesDir + sep
  if (absPath.startsWith(normalizedPages)) {
    return { kind: "pages-nested", abs: absPath }
  }
  return { kind: "local-helper", abs: absPath }
}

// ----------------------------------------------------------------------------
// Recursive walk
// ----------------------------------------------------------------------------

function walkTemplate(topPath, sourceRootDir) {
  const visited = new Map() // abs path → { template, css, exports, importRewrites }
  const queue = [topPath]
  const order = [] // BFS-ish order for deterministic output

  while (queue.length) {
    const file = queue.shift()
    if (visited.has(file)) continue
    if (!existsSync(file)) {
      throw new Error(`Template file not found: ${file}`)
    }

    const source = readFileSync(file, "utf8")
    const ast = parse(source, {
      sourceType: "module",
      plugins: [["typescript", { dts: false }], "jsx"],
      errorRecovery: false,
    })

    const info = {
      absPath: file,
      source,
      ast,
      exports: new Set(),
      rewriteImports: [], // [{ originalSpec, newSpec, kind, importedNames }]
      sideCss: [],
      nested: [],
      reExportsToDrop: [], // AST nodes to skip when emitting body
    }

    // First pass: collect exports, side-effect CSS, classify imports
    traverse(ast, {
      // no-op visitor; we'll do structural pass next
    })

    // Walk ImportDeclarations + Export*Declarations to classify
    for (const node of ast.program.body) {
      if (t.isImportDeclaration(node)) {
        const spec = node.source.value
        const kind = classifyImport(spec, file, sourceRootDir)
        const importedNames = node.specifiers.map((s) => ({
          imported: t.isImportSpecifier(s) ? s.imported.name : null,
          local: s.local.name,
          kind: t.isImportDefaultSpecifier(s)
            ? "default"
            : t.isImportNamespaceSpecifier(s)
            ? "namespace"
            : "named",
        }))

        if (typeof kind === "string" || kind.kind === "external") {
          // Bare specifier → external keep (passthrough with original spec)
          const targetSpec = typeof kind === "string" ? kind : kind.spec
          info.rewriteImports.push({
            originalSpec: spec,
            newSpec: targetSpec,
            importKind: node.importKind || "value",
            sideEffect: node.specifiers.length === 0,
            names: importedNames,
          })
        } else if (kind.kind === "css-local") {
          info.sideCss.push(kind.abs)
        } else if (kind.kind === "pages-nested") {
          info.nested.push(kind.abs)
          queue.push(kind.abs)
        } else if (kind.kind === "local-helper") {
          // Inline the source into the merged output
          const helperSource = readFileSync(kind.abs, "utf8")
          info.rewriteImports.push({
            originalSpec: spec,
            newSpec: "__inline_helper__",
            inlineSource: helperSource,
            helperAbs: kind.abs,
          })
          // Recurse into helpers too (they may import other things)
          queue.push(kind.abs)
        } else if (kind.kind === "forbidden") {
          throw new Error(
            `Forbidden import in ${file}: ${spec}. ` +
              `Unrecognized bare specifier or unresolvable path.`,
          )
        }
      } else if (t.isExportNamedDeclaration(node)) {
        if (node.declaration) {
          // export const X = ... / export function X / export class X
          const d = node.declaration
          if (t.isVariableDeclaration(d)) {
            for (const dec of d.declarations) {
              if (t.isIdentifier(dec.id)) info.exports.add(dec.id.name)
            }
          } else if (
            t.isFunctionDeclaration(d) ||
            t.isClassDeclaration(d)
          ) {
            if (d.id) info.exports.add(d.id.name)
          }
        } else {
          for (const s of node.specifiers) info.exports.add(s.exported.name)
          // Re-export from another file: `export { X, Y } from "./foo"` —
          // treat the `from` like an import (classify + recurse if template).
          if (node.source) {
            const spec = node.source.value
            const kind = classifyImport(spec, file, sourceRootDir)
            if (typeof kind === "string" || kind.kind === "external") {
              // External keep — preserve these names as-is.
              info.rewriteImports.push({
                originalSpec: spec,
                newSpec: typeof kind === "string" ? kind : kind.spec,
                importKind: "value",
                sideEffect: false,
                names: node.specifiers.map((s) => ({
                  imported: t.isExportSpecifier(s)
                    ? s.local.name
                    : null,
                  local: s.exported.name,
                  kind: "named",
                })),
                isReExport: true,
              })
            } else if (kind.kind === "css-local") {
              info.sideCss.push(kind.abs)
            } else if (kind.kind === "pages-nested") {
              info.nested.push(kind.abs)
              queue.push(kind.abs)
              info.reExportsToDrop = info.reExportsToDrop || []
              info.reExportsToDrop.push(node)
            } else if (kind.kind === "local-helper") {
              const helperSource = readFileSync(kind.abs, "utf8")
              info.rewriteImports.push({
                originalSpec: spec,
                newSpec: "__inline_helper__",
                inlineSource: helperSource,
                helperAbs: kind.abs,
              })
              queue.push(kind.abs)
              info.reExportsToDrop = info.reExportsToDrop || []
              info.reExportsToDrop.push(node)
            } else if (kind.kind === "forbidden") {
              throw new Error(
                `Forbidden re-export in ${file}: ${spec}.`,
              )
            }
          }
        }
      } else if (t.isExportAllDeclaration(node)) {
        // `export * from "./foo"` — same classification as a re-export.
        if (node.source) {
          const spec = node.source.value
          const kind = classifyImport(spec, file, sourceRootDir)
          if (kind.kind === "pages-nested") {
            info.nested.push(kind.abs)
            queue.push(kind.abs)
            info.reExportsToDrop = info.reExportsToDrop || []
            info.reExportsToDrop.push(node)
          } else if (kind.kind === "local-helper") {
            const helperSource = readFileSync(kind.abs, "utf8")
            info.rewriteImports.push({
              originalSpec: spec,
              newSpec: "__inline_helper__",
              inlineSource: helperSource,
              helperAbs: kind.abs,
            })
            queue.push(kind.abs)
            info.reExportsToDrop = info.reExportsToDrop || []
            info.reExportsToDrop.push(node)
          } else if (typeof kind === "string" || kind.kind === "external" || kind.kind === "forbidden") {
            // Bare-specifier re-export of all names — keep but log.
            console.warn(
              `[prepare-template-merge] ${file}: re-export * from "${spec}" — symbols forwarded as-is`,
            )
          }
        }
      } else if (t.isExportDefaultDeclaration(node)) {
        info.exports.add("default")
      }
    }

    visited.set(file, info)
    order.push(file)
  }

  return { visited, order, topPath }
}

// ----------------------------------------------------------------------------
// Standalone merge
// ----------------------------------------------------------------------------

function mergeStandalone(visited, order, topPath, opts) {
  // 1. Collect imports by target spec + dedup
  const externalImports = new Map() // spec → { kind, names: Map<localName, { imported, kind }>, importKind }
  const helperSources = [] // [absPath, source]
  const cssPieces = []

  // Track which helper abs paths we've already inlined (to dedup)
  const seenHelpers = new Set()

  // The top template's exported component name (or override)
  let topDefaultName = opts.topComponent
  if (!topDefaultName) {
    const topInfo = visited.get(topPath)
    if (topInfo) {
      for (const exp of topInfo.exports) {
        if (exp !== "default") {
          topDefaultName = exp
          break
        }
      }
    }
  }
  if (!topDefaultName) {
    throw new Error(
      `Could not determine top-level component name for ${topPath}. ` +
        `Pass --top-component <Name>.`,
    )
  }

  // Collect type-only names per spec so we can split `import type` lines
  function ensureImport(spec, importKind) {
    if (!externalImports.has(spec)) {
      externalImports.set(spec, {
        spec,
        importKind: importKind || "value",
        names: new Map(),
      })
    } else if (
      importKind === "value" &&
      externalImports.get(spec).importKind === "type"
    ) {
      // Promote to value: a mixed spec must be a value import.
      externalImports.get(spec).importKind = "value"
    }
    return externalImports.get(spec)
  }

  // Walk each file's classified imports
  for (const file of order) {
    const info = visited.get(file)
    for (const ri of info.rewriteImports) {
      if (ri.newSpec === "__inline_helper__") {
        if (!seenHelpers.has(ri.helperAbs)) {
          seenHelpers.add(ri.helperAbs)
          helperSources.push([ri.helperAbs, ri.inlineSource])
        }
      } else {
        const target = ensureImport(ri.newSpec, ri.importKind)
        for (const n of ri.names) {
          if (!target.names.has(n.local)) {
            target.names.set(n.local, { ...n, importKind: ri.importKind })
          }
        }
      }
    }
    for (const css of info.sideCss) {
      if (existsSync(css)) {
        cssPieces.push([css, readFileSync(css, "utf8")])
      }
    }
  }

  // 2. For each template file: extract everything EXCEPT import statements
  // and the top default export.
  function extractNonImportBody(file, topPath, visited, topDefaultName) {
    const info = visited.get(file)
    if (!info) return []

    const ast = info.ast
    const stmts = []

    for (const node of ast.program.body) {
      // Drop import declarations (we'll rewrite at the top of the merged file)
      if (t.isImportDeclaration(node)) continue
      // Drop re-export nodes whose target has been inlined
      if (info.reExportsToDrop?.includes(node)) continue
      // For the top template, keep the default export
      // For nested templates, drop their default exports (we expose only the top)
      if (t.isExportDefaultDeclaration(node)) {
        if (file === topPath) {
          // Keep as-is (it's the page entry)
        } else {
          // Convert `export default X` → `const X = ...` so the symbol stays
          // available but no longer claims the default slot
          const decl = t.variableDeclaration("const", [
            t.variableDeclarator(
              t.identifier(
                node.declaration.id?.name ||
                  node.declaration.name ||
                  "AnonymousDefault",
              ),
              t.isIdentifier(node.declaration) || t.isExpression(node.declaration)
                ? node.declaration
                : t.isFunctionDeclaration(node.declaration) ||
                  t.isClassDeclaration(node.declaration)
                ? t.toExpression(node.declaration)
                : node.declaration,
            ),
          ])
          stmts.push(decl)
          continue
        }
      }
      stmts.push(node)
    }
    return stmts
  }

  // 3. Generate external import block — pass through original specifiers
  const importStmts = []

  for (const [spec, group] of externalImports) {
    // Drop jsx-runtime — Babel handles at runtime
    if (spec === "react/jsx-runtime" || spec === "react/jsx-dev-runtime") continue

    const specifiers = []

    for (const [, n] of group.names) {
      if (n.kind === "default") {
        specifiers.push(t.importDefaultSpecifier(t.identifier(n.local)))
      } else if (n.kind === "namespace") {
        specifiers.push(t.importNamespaceSpecifier(t.identifier(n.local)))
      } else {
        specifiers.push(
          t.importSpecifier(
            t.identifier(n.local),
            t.identifier(n.imported || n.local),
          ),
        )
      }
    }

    if (specifiers.length > 0) {
      importStmts.push(
        t.importDeclaration(specifiers, t.stringLiteral(spec)),
      )
    }
  }

  // 3a. Standalone bridge: ensure `import React from "react"` is present.
  // Babel standalone uses the classic JSX transform (presets: ["react"]),
  // which compiles JSX to `React.createElement(...)`. The source templates
  // are written for the automatic runtime (react-jsx) and only import named
  // hooks, so without this patch the page fails at runtime with
  // "ReferenceError: React is not defined".
  if (opts.mode === "standalone") {
    const reactStmt = importStmts.find(
      (s) => t.isImportDeclaration(s) && s.source.value === "react",
    )
    if (reactStmt) {
      const hasReactDefault = reactStmt.specifiers.some(
        (s) => t.isImportDefaultSpecifier(s) && s.local.name === "React",
      )
      if (!hasReactDefault) {
        reactStmt.specifiers.unshift(
          t.importDefaultSpecifier(t.identifier("React")),
        )
      }
    } else {
      importStmts.unshift(
        t.importDeclaration(
          [t.importDefaultSpecifier(t.identifier("React"))],
          t.stringLiteral("react"),
        ),
      )
    }
  }

  // 4. Compose program
  const programBody = []

  // 4a. External imports
  for (const s of importStmts) programBody.push(s)

  // 4b. Inline helper sources
  for (const [, source] of helperSources) {
    const helperAst = parse(source, {
      sourceType: "module",
      plugins: [["typescript", { dts: false }], "jsx"],
      errorRecovery: true,
    })
    for (const stmt of helperAst.program.body) {
      // Skip import statements inside helpers (their deps were already collected
      // via walkTemplate). Inline helper = body only.
      if (t.isImportDeclaration(stmt)) continue
      programBody.push(stmt)
    }
  }

  // 4c. Template bodies (top last so default export ends up at end)
  const orderedFiles = [...order].reverse()
  for (const file of orderedFiles) {
    const stmts = extractNonImportBody(file, topPath, visited, topDefaultName)
    for (const s of stmts) programBody.push(s)
  }

  // 4c'. Dedup top-level declarations.
  // The top template's version of any name wins. Later (nested) declarations
  // that collide are dropped to avoid "Identifier 'X' has already been
  // declared" errors.
  function declarationNames(stmt) {
    const names = []
    if (t.isFunctionDeclaration(stmt) && stmt.id) names.push(stmt.id.name)
    else if (t.isClassDeclaration(stmt) && stmt.id) names.push(stmt.id.name)
    else if (t.isVariableDeclaration(stmt)) {
      for (const dec of stmt.declarations) {
        if (t.isIdentifier(dec.id)) names.push(dec.id.name)
      }
    } else if (t.isTSTypeAliasDeclaration?.(stmt)) names.push(stmt.id.name)
    else if (t.isInterfaceDeclaration?.(stmt)) names.push(stmt.id.name)
    else if (t.isTSInterfaceDeclaration?.(stmt)) names.push(stmt.id.name)
    else if (
      t.isExportNamedDeclaration(stmt) &&
      stmt.declaration
    ) {
      // Same shape but wrapped
      return declarationNames(stmt.declaration)
    }
    return names
  }
  const seen = new Set()
  const deduped = []
  const dropped = []
  for (const stmt of programBody) {
    const names = declarationNames(stmt)
    if (names.length === 0) {
      deduped.push(stmt)
      continue
    }
    const collision = names.find((n) => seen.has(n))
    if (collision) {
      dropped.push({ name: collision, stmt })
      continue
    }
    for (const n of names) seen.add(n)
    deduped.push(stmt)
  }
  if (dropped.length) {
    console.log(
      `[prepare-template-merge] dropped ${dropped.length} duplicate declaration(s): ` +
        dropped.map((d) => d.name).join(", "),
    )
  }
  programBody.length = 0
  for (const s of deduped) programBody.push(s)

  // 5. Ensure the top component has a default export.
  // renderTsxString's findPageComponent() checks pageModule.default first,
  // then falls back to walking named exports. Without a default export the
  // fallback can pick a nested component (e.g. MobilePhoneShellTemplatePage)
  // that renders without page content, because the intended entry component
  // (e.g. SettingsPageTemplatePage) appears later in the module body.
  // Per SKILL.md "反模式" section this also prevents the "壳层去装饰" class
  // of bugs where an empty shell renders as the root.
  const alreadyHasDefault = programBody.some(
    (s) => t.isExportDefaultDeclaration(s) && !t.isExportNamedDeclaration(s),
  )
  if (!alreadyHasDefault) {
    programBody.push(
      t.exportDefaultDeclaration(t.identifier(topDefaultName)),
    )
  }

  // 6. Generate
  const mergedAst = t.program(programBody)
  const out = generate(mergedAst, {
    retainLines: false,
    compact: false,
    concise: false,
    jsescOption: { minimal: true },
  }, { /* input map; not needed since retainLines:false */ })

  // 7. Build CSS file
  const cssHeader = `/* Auto-merged by prepare-template-merge.mjs from ${order.length} files */\n`
  const cssBody = cssPieces
    .map(([p, src]) => `/* ${relative(SOURCE_ROOT, p)} */\n${src.trim()}\n`)
    .join("\n")

  // 8. Wrap CSS as JSX <style> literal in a helper string the agent can inline
  const cssForJsx =
    cssHeader +
    cssBody +
    `\n/* Inject into the page via: <style>{styles}</style> inside the rendered component. */`

  return { tsx: out.code, css: cssForJsx, cssPieces, topDefaultName }
}

// ----------------------------------------------------------------------------
// Design-system mode
// ----------------------------------------------------------------------------

function copyDesignSystem(visited, order, topPath, sourceRootDir, outDir) {
  mkdirSync(outDir, { recursive: true })

  // Map: original abs path → new abs path under outDir
  const pagesDir = join(sourceRootDir, "pages")
  const remap = new Map()

  for (const file of order) {
    const rel = relative(pagesDir, file)
    const target = join(outDir, rel)
    mkdirSync(dirname(target), { recursive: true })

    const info = visited.get(file)
    let src = info.source

    writeFileSync(target, src)
    remap.set(file, target)

    // Copy sibling CSS files (if not already handled as side-effect import)
    const info2 = visited.get(file)
    if (info2?.sideCss) {
      for (const cssAbs of info2.sideCss) {
        const cssRel = relative(pagesDir, cssAbs)
        const cssTarget = join(outDir, cssRel)
        mkdirSync(dirname(cssTarget), { recursive: true })
        writeFileSync(cssTarget, readFileSync(cssAbs, "utf8"))
      }
    }
  }

  return { remap }
}

// ----------------------------------------------------------------------------
// Main
// ----------------------------------------------------------------------------

function main() {
  if (!existsSync(opts.top)) {
    console.error(`Top template not found: ${opts.top}`)
    process.exit(2)
  }
  console.log(`[prepare-template-merge] source root: ${SOURCE_ROOT}`)
  console.log(`[prepare-template-merge] top:         ${opts.top}`)
  console.log(`[prepare-template-merge] mode:        ${opts.mode}`)

  const { visited, order, topPath } = walkTemplate(opts.top, SOURCE_ROOT)
  console.log(
    `[prepare-template-merge] walked: ${order.length} file(s) ` +
      `(${[...visited.values()].reduce((n, v) => n + v.nested.length, 0)} nested edges)`,
  )

  if (opts.mode === "standalone") {
    const merged = mergeStandalone(visited, order, topPath, opts)
    mkdirSync(dirname(resolve(opts.out)), { recursive: true })
    writeFileSync(resolve(opts.out), merged.tsx)
    if (merged.css) {
      mkdirSync(dirname(resolve(opts.cssOut)), { recursive: true })
      writeFileSync(resolve(opts.cssOut), merged.css)
    }
    console.log(
      `[prepare-template-merge] wrote ${opts.out} (${merged.tsx.length} chars)`,
    )
    console.log(
      `[prepare-template-merge] wrote ${opts.cssOut} (${merged.css.length} chars, ${merged.cssPieces.length} css files)`,
    )
    console.log(
      `[prepare-template-merge] top default export: ${merged.topDefaultName}`,
    )
  } else {
    const outDir = resolve(opts.outDir)
    const { remap } = copyDesignSystem(
      visited,
      order,
      topPath,
      SOURCE_ROOT,
      outDir,
    )
    console.log(
      `[prepare-template-merge] copied ${remap.size} file(s) → ${outDir}`,
    )
  }
}

main()
