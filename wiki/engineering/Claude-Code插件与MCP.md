# Claude Code 插件与 MCP 生态

> Claude Code 的能力可通过插件（Plugin）和 MCP（Model Context Protocol）服务器大幅扩展。本页记录插件管理工作流、常用插件及 Skills 体系。
> 会话 ID：d2ee5346-3090-4cd4-b6cc-547a52485680（2026-04-15）

## 目录

- [[#核心概念]]
- [[#插件管理命令]]
- [[#常用插件]]
- [[#Skills 体系]]
- [[#Chrome DevTools MCP]]
- [[#注意事项]]

---

## 核心概念

| 概念 | 说明 |
|------|------|
| **Plugin** | 通过 `/plugin` 命令安装/启用的扩展包，可包含 MCP 服务器、Skills、Agent 定义、Hook |
| **MCP Server** | 遵循 Model Context Protocol 的工具服务，为 Claude Code 提供额外工具调用能力 |
| **Skill** | 预定义的提示词工作流，通过 `/skill-name` 或 `Skill` 工具触发，封装常见任务模式 |
| **Hook** | 在特定事件（工具调用前后等）自动执行的 shell 命令，通过 `settings.json` 配置 |
| **Agent** | 专用子代理，具备特定工具集和任务专长，通过 `Agent` 工具启动 |

---

## 插件管理命令

```bash
# 打开插件管理面板（交互式）
/plugin

# 重新加载所有插件（安装/启用后必须执行）
/reload-plugins

# 查看 MCP 服务器状态
/mcp
```

**标准工作流：**
1. `/plugin` → 从列表中安装或启用插件
2. `/reload-plugins` → 应用变更
3. `/mcp` → 确认 MCP 服务器已连接

重载后输出示例：
```
Reloaded: 6 plugins · 5 skills · 7 agents · 1 hook · 3 plugin MCP servers · 0 plugin LSP servers
```

---

## 常用插件

### superpowers

提供一套完整的开发工作流 Skills，涵盖：

| Skill | 触发时机 |
|-------|---------|
| `superpowers:writing-plans` | 多步骤任务实施前，先写计划 |
| `superpowers:executing-plans` | 有实施计划时，在隔离 session 中执行 |
| `superpowers:subagent-driven-development` | 并行子代理驱动开发 |
| `superpowers:systematic-debugging` | 遇到 bug/测试失败时，系统化排查 |
| `superpowers:test-driven-development` | 先写测试，再写实现 |
| `superpowers:verification-before-completion` | 声明完成前，强制运行验证命令 |
| `superpowers:requesting-code-review` | 完成功能后请求代码审查 |
| `superpowers:writing-skills` | 创建或编辑 Skills |
| `superpowers:dispatching-parallel-agents` | 2+ 个独立任务时并行分发 |
| `superpowers:using-git-worktrees` | 功能开发需隔离工作区时 |

安装命令：`/plugin` → 搜索 `superpowers` → 安装 → `/reload-plugins`

### github

启用 GitHub MCP 服务器，提供 Issues、PR、仓库操作等工具。

启用命令：`/plugin` → 搜索 `github` → 启用（Enable）→ `/reload-plugins`

> 注意：`github` 与 `superpowers` 的区别——`github` 是启用（Enable）已安装的插件，`superpowers` 是全新安装（Install）。

---

## Skills 体系

Skills 是对话中的可调用工作流，分两类：

**内置 Skills（通过 `/skill-name` 触发）：**
- `/commit` — 规范化提交
- `/review-pr` — PR 审查

**插件 Skills（`plugin:skill-name` 格式）：**
- `chrome-devtools-mcp:chrome-devtools` — Chrome DevTools 自动化
- `atlassian:triage-issue` — Jira/Confluence 集成
- `sre-agent:investigate` — 生产事故调查

---

## Chrome DevTools MCP

`chrome-devtools-mcp` 插件提供浏览器自动化和调试能力。

**核心工具：**

| 工具 | 用途 |
|------|------|
| `list_pages` / `select_page` | 查看和切换浏览器 Tab |
| `navigate_page` / `new_page` | 导航或打开新页面 |
| `take_snapshot` | 获取页面结构（含 `uid`，用于后续交互） |
| `take_screenshot` | 截图（视觉检查） |
| `click` / `fill` / `type_text` | 元素交互（使用 `uid`） |
| `evaluate_script` | 执行 JavaScript |
| `list_network_requests` | 查看网络请求 |
| `lighthouse_audit` | 性能/可访问性审计 |
| `wait_for` | 等待特定条件 |

**标准交互流程：**
```
navigate_page → wait_for → take_snapshot → click/fill（使用 uid）
```

**相关 Skills：**
- `chrome-devtools-mcp:chrome-devtools` — 通用自动化
- `chrome-devtools-mcp:debug-optimize-lcp` — LCP 性能优化
- `chrome-devtools-mcp:a11y-debugging` — 可访问性调试
- `chrome-devtools-mcp:troubleshooting` — 连接问题排查

---

## 注意事项

- MCP 服务器可能断开（`disconnected`），使用前通过 `/mcp` 确认状态
- 插件安装/启用后**必须** `/reload-plugins` 才能生效
- `chrome-devtools-mcp` 首次工具调用时会自动启动 Chrome，使用持久化 Profile
- Skills 已加载后无需重复调用 `Skill` 工具，直接按 `<command-name>` 标签中的指令操作
