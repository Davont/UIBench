# Mobile Phone Shell Contract

页面使用 `MobilePhoneShellTemplatePage` 时读取。

## NavigationContainer

Shell 自身已经提供一个页面级 `NavigationContainer`。使用该 Shell 的页面不得在 children 内再次添加页面级 `NavigationContainer`。

最终渲染树以“恰好一个”为准，而不是要求每个页面源码都直接 import 它。

## 默认值

源码默认逻辑：

```tsx
showFloatingTab = mode === "app-home"
showAIBottomBar = false
```

因此：

- `app-home` 缺省显示 FloatingTab
- `secondary` / `immersive` 缺省不显示 FloatingTab
- 显式写 `showFloatingTab={false}` 是可读性要求，不代表缺省值为 true

## 选型矩阵

| 场景 | mode | FloatingTab | AIBottomBar |
| --- | --- | --- | --- |
| 应用入口一级主页 | `app-home` | 缺省 true | 缺省 false |
| 一级 Tab 内容页 | `app-home` | 保留 | 按场景 |
| 设置、详情、表单、流程 | `secondary` | 显式 false | 按场景 |
| 启动页、专注录音、全屏播放 | `immersive` | 显式 false | 显式 false |
| 阅读、搜索、对话、视频、音乐等 AI 唤起场景 | 按层级 | 按层级 | 显式 true |

禁止 `mode="app-home"` 与 `showFloatingTab={false}` 无理由组合。若页面确实使用沉浸式替代内容，应改用更符合语义的 mode 或在日志说明。

## 目标范围自检

只检查当前 `<TARGET_DIR>`：

```bash
rg -n 'mode=|showFloatingTab=|showAIBottomBar=' <TARGET_DIR> --glob '*.tsx'
```

日志记录页面 mode、FloatingTab、AIBottomBar 的实际声明和选择理由；不要为单页任务扫描固定数量的历史页面。
