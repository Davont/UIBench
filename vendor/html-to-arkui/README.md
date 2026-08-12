# Vendored html-to-arkui runtime

`manifest.json` 的 `archive` 指向的 `local-html-to-arkui-<version>.tgz` 是 UIBench
固定使用的平台转换器包。压缩包包含 `dist`、公开契约，以及 `css-tree`、`parse5` 和
它们的传递运行依赖；因此可以通过仓库根目录的锁文件离线安装，不依赖相邻的
`html-to-arkui` 仓库。

部署或测试前运行：

```bash
npm ci --ignore-scripts --offline
```

包的大小、SHA-256、npm integrity、clean 来源 commit 和构建工具版本记录在
`manifest.json`，压缩包始终可以从 `sourceCommit` 检出并重建，不依赖未提交补丁。
更新包的流程：先在源仓库提交变更（`npm pack` 的 `prepack` 钩子会强制跑完整
`npm run verify`），再执行

```bash
python tools/vendor-html-to-arkui.py ../html-to-arkui/local-html-to-arkui-<version>.tgz
```

脚本会校验源仓库工作树干净，然后一次性更新压缩包、本目录 manifest、根
`package.json`/`package-lock.json` 与 `uibench/arkui/renderer_contract.json` 钉板副本，
并自动执行上述离线安装验证。`node_modules` 不提交。

开发转换器时仍可显式设置 `HTML_TO_ARKUI_ROOT=/absolute/path/to/html-to-arkui`，
让 bridge 临时加载该目录的 `dist/index.js`；未设置时只使用本仓库安装的固定包。
