// Single entry point for Babel inside this Skill's scripts.
//
// Always resolves to the vendored bundle in ./vendor — never to the host project's
// node_modules, even when one is present. The Skill is copied into other projects and
// run there, and a host that happens to have Babel 7 installed would otherwise silently
// change traverse()/generate() behaviour. One code path in every mode.
//
// Rebuild the bundle with ./build-babel-vendor.mjs (design-system checkout only).
//
// Default-export interop is normalised inside the bundle, so `traverse` and `generate`
// are directly callable — no `x.default ?? x` dance at the call site.

export { parse, traverse, generate, types } from "./vendor/babel-bundle.mjs"
