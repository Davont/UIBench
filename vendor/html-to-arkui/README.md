# Vendored html-to-arkui runtime

`local-html-to-arkui-0.3.1.tgz` 是 UIBench 固定使用的平台转换器包。压缩包包含
`dist`、公开契约，以及 `css-tree`、`parse5` 和它们的传递运行依赖；因此可以通过
仓库根目录的锁文件离线安装，不依赖相邻的 `html-to-arkui` 仓库。

部署或测试前运行：

```bash
npm ci --ignore-scripts --offline
```

包的大小、SHA-256、npm integrity、clean 来源 commit 和构建工具版本记录在
`manifest.json`。当前 0.3.1 包可直接从 `sourceCommit` 检出并重建，不依赖未提交补丁。
更新包时必须先提交源仓库变更并通过 `npm run verify`，从该 clean commit 重新执行
`npm pack`，更新根 `package.json`/`package-lock.json` 和本目录 manifest，并在空 npm
cache 中验证上述离线安装命令。`node_modules` 不提交。

开发转换器时仍可显式设置 `HTML_TO_ARKUI_ROOT=/absolute/path/to/html-to-arkui`，
让 bridge 临时加载该目录的 `dist/index.js`；未设置时只使用本仓库安装的固定包。
