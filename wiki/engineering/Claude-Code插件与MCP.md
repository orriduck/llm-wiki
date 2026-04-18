# Claude Code Plugins and MCP Ecosystem / Claude Code 插件与 MCP 生态

> Claude Code's capabilities can be significantly extended through Plugins and MCP (Model Context Protocol) servers. This page documents the plugin management workflow, common plugins, and the Skills system.

> Claude Code 的能力可通过插件（Plugin）和 MCP（Model Context Protocol）服务器大幅扩展。本页记录插件管理工作流、常用插件及 Skills 体系。

## Table of Contents / 目录

- [[#Core Concepts / 核心概念]]
- [[#Plugin Management Commands / 插件管理命令]]
- [[#Common Plugins / 常用插件]]
- [[#Skills System / Skills 体系]]
- [[#Chrome DevTools MCP]]
- [[#Notes / 注意事项]]

---

## Core Concepts / 核心概念

| Concept / 概念 | Description / 说明 |
|------|------|
| **Plugin** | Extension packages installed/enabled via `/plugin` command; can include MCP servers, Skills, Agent definitions, Hooks / 通过 `/plugin` 命令安装/启用的扩展包，可包含 MCP 服务器、Skills、Agent 定义、Hook |
| **MCP Server** | Tool services following the Model Context Protocol, providing additional tool-calling capabilities to Claude Code / 遵循 Model Context Protocol 的工具服务，为 Claude Code 提供额外工具调用能力 |
| **Skill** | Predefined prompt workflows triggered via `/skill-name` or the `Skill` tool, encapsulating common task patterns / 预定义的提示词工作流，通过 `/skill-name` 或 `Skill` 工具触发，封装常见任务模式 |
| **Hook** | Shell commands that auto-execute on specific events (before/after tool calls, etc.), configured via `settings.json` / 在特定事件（工具调用前后等）自动执行的 shell 命令，通过 `settings.json` 配置 |
| **Agent** | Specialized sub-agents with specific toolsets and task expertise, launched via the `Agent` tool / 专用子代理，具备特定工具集和任务专长，通过 `Agent` 工具启动 |

---

## Plugin Management Commands / 插件管理命令

```bash
# Open plugin management panel (interactive) / 打开插件管理面板（交互式）
/plugin

# Reload all plugins (must run after install/enable) / 重新加载所有插件（安装/启用后必须执行）
/reload-plugins

# View MCP server status / 查看 MCP 服务器状态
/mcp
```

**Standard workflow / 标准工作流：**

1. `/plugin` -> Install or enable a plugin from the list / 从列表中安装或启用插件
2. `/reload-plugins` -> Apply changes / 应用变更
3. `/mcp` -> Confirm MCP server is connected / 确认 MCP 服务器已连接

Example output after reload / 重载后输出示例：

```
Reloaded: 6 plugins · 5 skills · 7 agents · 1 hook · 3 plugin MCP servers · 0 plugin LSP servers
```

---

## Plugin Marketplace & Custom Plugins / 插件市场与自定义插件

Claude Code supports custom plugin distribution through a marketplace mechanism. A plugin repository needs:

> Claude Code 支持通过市场（marketplace）机制分发自定义插件。一个插件仓库需要：

### 仓库结构

```
my-plugin/
├── .claude-plugin/
│   ├── plugin.json          # 插件元数据（名称、描述、版本）
│   └── marketplace.json     # 市场注册信息
├── skills/
│   └── my-skill/
│       └── SKILL.md         # Skill 定义（prompt + metadata）
├── agents/
│   └── my-agent.md          # Agent 定义（model、tools、instructions）
└── settings.local.json      # 推荐的权限配置
```

### 关键文件

**`plugin.json`** — 保持最小化：

```json
{
  "name": "my-plugin",
  "description": "What this plugin does",
  "version": "0.1.0"
}
```

> Keep `plugin.json` minimal. Fields like `skills`, `commands`, `userConfig` are not part of the core plugin spec and may cause issues.

**`marketplace.json`** — 让插件可被搜索和安装：

```json
{
  "name": "my-plugin",
  "description": "Plugin description for marketplace listing",
  "publisher": "your-github-username"
}
```

### 安装自定义插件

```bash
# 1. 添加市场源（GitHub 仓库）
/plugin marketplace add <github-user>/<repo-name>

# 2. 从市场安装插件
/plugin install <marketplace-name>@<plugin-name>

# 3. 重载
/reload-plugins
```

> Custom plugins are installed from GitHub repositories registered as marketplaces. The marketplace repo is cloned locally to `~/.claude/plugins/marketplaces/`.

---

## Common Plugins / 常用插件

### superpowers

Provides a comprehensive set of development workflow Skills covering:

> 提供一套完整的开发工作流 Skills，涵盖：

| Skill | Trigger / 触发时机 |
|-------|---------|
| `superpowers:writing-plans` | Before implementing multi-step tasks, write a plan first / 多步骤任务实施前，先写计划 |
| `superpowers:executing-plans` | When there's an implementation plan, execute in an isolated session / 有实施计划时，在隔离 session 中执行 |
| `superpowers:subagent-driven-development` | Parallel sub-agent driven development / 并行子代理驱动开发 |
| `superpowers:systematic-debugging` | When encountering bugs/test failures, systematic investigation / 遇到 bug/测试失败时，系统化排查 |
| `superpowers:test-driven-development` | Write tests first, then implementation / 先写测试，再写实现 |
| `superpowers:verification-before-completion` | Before declaring completion, force verification commands / 声明完成前，强制运行验证命令 |
| `superpowers:requesting-code-review` | Request code review after completing a feature / 完成功能后请求代码审查 |
| `superpowers:writing-skills` | Create or edit Skills / 创建或编辑 Skills |
| `superpowers:dispatching-parallel-agents` | Dispatch in parallel when there are 2+ independent tasks / 2+ 个独立任务时并行分发 |
| `superpowers:using-git-worktrees` | When feature development needs an isolated workspace / 功能开发需隔离工作区时 |

Install: `/plugin` -> search `superpowers` -> Install -> `/reload-plugins`

> 安装命令：`/plugin` -> 搜索 `superpowers` -> 安装 -> `/reload-plugins`

### github

Enables the GitHub MCP server, providing tools for Issues, PRs, repository operations, etc.

> 启用 GitHub MCP 服务器，提供 Issues、PR、仓库操作等工具。

Enable: `/plugin` -> search `github` -> Enable -> `/reload-plugins`

> 启用命令：`/plugin` -> 搜索 `github` -> 启用（Enable）-> `/reload-plugins`

> Note: The difference between `github` and `superpowers` -- `github` is enabling an already-installed plugin, while `superpowers` is a fresh install.

> 注意：`github` 与 `superpowers` 的区别——`github` 是启用（Enable）已安装的插件，`superpowers` 是全新安装（Install）。

---

## Skills System / Skills 体系

Skills are callable workflows within a conversation, divided into two categories:

> Skills 是对话中的可调用工作流，分两类：

**Built-in Skills (triggered via `/skill-name`) / 内置 Skills（通过 `/skill-name` 触发）：**

- `/commit` -- Standardized commits / 规范化提交
- `/review-pr` -- PR review / PR 审查

**Plugin Skills (`plugin:skill-name` format) / 插件 Skills（`plugin:skill-name` 格式）：**

- `chrome-devtools-mcp:chrome-devtools` -- Chrome DevTools automation / Chrome DevTools 自动化
- `atlassian:triage-issue` -- Jira/Confluence integration / Jira/Confluence 集成
- `sre-agent:investigate` -- Production incident investigation / 生产事故调查

---

## Chrome DevTools MCP

The `chrome-devtools-mcp` plugin provides browser automation and debugging capabilities.

> `chrome-devtools-mcp` 插件提供浏览器自动化和调试能力。

**Core tools / 核心工具：**

| Tool / 工具 | Purpose / 用途 |
|------|------|
| `list_pages` / `select_page` | View and switch browser tabs / 查看和切换浏览器 Tab |
| `navigate_page` / `new_page` | Navigate or open new pages / 导航或打开新页面 |
| `take_snapshot` | Get page structure (with `uid` for subsequent interaction) / 获取页面结构（含 `uid`，用于后续交互） |
| `take_screenshot` | Take screenshot (visual inspection) / 截图（视觉检查） |
| `click` / `fill` / `type_text` | Element interaction (using `uid`) / 元素交互（使用 `uid`） |
| `evaluate_script` | Execute JavaScript / 执行 JavaScript |
| `list_network_requests` | View network requests / 查看网络请求 |
| `lighthouse_audit` | Performance/accessibility audit / 性能/可访问性审计 |
| `wait_for` | Wait for specific conditions / 等待特定条件 |

**Standard interaction flow / 标准交互流程：**

```
navigate_page -> wait_for -> take_snapshot -> click/fill (using uid)
```

**Related Skills / 相关 Skills：**

- `chrome-devtools-mcp:chrome-devtools` -- General automation / 通用自动化
- `chrome-devtools-mcp:debug-optimize-lcp` -- LCP performance optimization / LCP 性能优化
- `chrome-devtools-mcp:a11y-debugging` -- Accessibility debugging / 可访问性调试
- `chrome-devtools-mcp:troubleshooting` -- Connection troubleshooting / 连接问题排查

---

## Notes / 注意事项

- MCP servers may disconnect (`disconnected`); confirm status via `/mcp` before use

> MCP 服务器可能断开（`disconnected`），使用前通过 `/mcp` 确认状态

- After installing/enabling plugins, you **must** run `/reload-plugins` for changes to take effect

> 插件安装/启用后**必须** `/reload-plugins` 才能生效

- `chrome-devtools-mcp` auto-launches Chrome on the first tool call, using a persistent Profile

> `chrome-devtools-mcp` 首次工具调用时会自动启动 Chrome，使用持久化 Profile

- Once Skills are loaded, there's no need to call the `Skill` tool again; follow the instructions in the `<command-name>` tag directly

> Skills 已加载后无需重复调用 `Skill` 工具，直接按 `<command-name>` 标签中的指令操作
