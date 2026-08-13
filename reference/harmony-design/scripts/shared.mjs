import { existsSync, statSync } from "node:fs"
import { dirname, join, parse, relative, resolve } from "node:path"
import { fileURLToPath } from "node:url"

const scriptPath = fileURLToPath(import.meta.url)
const scriptDir = dirname(scriptPath)

/** standalone-page-generation Skill 根目录 */
export const skillDir = resolve(scriptDir, "..")

/** standalone 模式始终使用本 Skill 内置的 src/ */
export const sourceRoot = join(skillDir, "src")

/**
 * 向上搜索 design-system 项目根目录。
 * standalone 模式下总是排除 skillDir 自身，用于安全校验（禁止将 HTML 写入外部 design-system 项目的 src/）。
 */
export function findDesignSystemRoot(startDir, { excludedRoots = [skillDir] } = {}) {
  let current = resolve(startDir)
  if (existsSync(current) && !statSync(current).isDirectory()) current = dirname(current)

  while (true) {
    const excluded = excludedRoots.some((root) => {
      const rel = relative(resolve(root), current)
      return rel === "" || (!rel.startsWith("..") && !rel.startsWith("/"))
    })
    const sourceDir = join(current, "src")
    if (
      !excluded &&
      existsSync(join(sourceDir, "route-index.md")) &&
      statSync(join(sourceDir, "pages-specs/layout"), { throwIfNoEntry: false })?.isDirectory()
    ) {
      return current
    }

    const parent = dirname(current)
    if (parent === current || current === parse(current).root) return null
    current = parent
  }
}

export function isInsideOrEqual(path, parent) {
  const rel = relative(resolve(parent), resolve(path))
  return rel === "" || (!rel.startsWith("..") && !rel.startsWith("/"))
}
