# llm-wiki

**[中文](#中文) | [English](#english)**

---

<a name="中文"></a>
## 中文

### 这是什么

llm-wiki 是一个由 LLM 维护的个人知识库。和 RAG 不同，它不是每次查询都从原始文档重新检索——而是让 LLM **增量地构建并维护一个持久化的 wiki**：结构化的 markdown 文件、相互交叉引用、矛盾被标注、综合随时间复合增长。

你负责：提供来源、探索问题、问好问题。  
LLM 负责：摘要、交叉引用、归档、维护。

wiki 是一个不断增值的资产——每新增一个来源、每问一个好问题，它都会变得更丰富。

**适用场景**

- 技术学习：深入某个领域，按周/月积累，构建有体系的知识图谱
- 工作复盘：每天下班用 `/lizard` 从当天所有 Claude 会话中蒸馏出知识点
- 读书笔记：按章节归档，自动构建人物、主题、情节的交叉引用
- 团队内部 wiki：由 Slack 消息、会议记录、项目文档喂养，LLM 做维护

### 安装

#### 前提条件

- [Claude Code](https://claude.ai/code) CLI 已安装并登录
- [Obsidian](https://obsidian.md)（可选，用于浏览 wiki）

#### 步骤

在 Claude Code 中运行三条命令：

```
/plugin marketplace add https://github.com/orriduck/llm-wiki
/plugin install llm-wiki@llm-wiki
/reload-plugins
```

完成。无需 clone 仓库，无需配置环境变量。插件安装后 wiki 内容直接存储在插件目录中，所有 skill 会自动检测路径。

**用 Obsidian 打开**（可选）

插件安装路径为 `~/.claude/plugins/cache/llm-wiki/llm-wiki/<version>/`，将该目录作为 Obsidian vault 打开，即可在图谱视图中看到所有页面的连接关系。

### 日常使用

#### 每日收工：蒸馏当天知识

```
/llm-wiki:lizard
```

自动扫描今天所有 Claude 会话的 transcript，提取有价值的知识点，整理为原子笔记写入 `wiki/`，更新 `index.md` 和 `log.md`，并自动 commit + push。

支持按主题过滤：

```
/llm-wiki:lizard Python
```

#### 从外部 URL 摄取知识

```
/llm-wiki:lizard-eat <url> <topic>
```

抓取指定 URL 的内容，整理为详尽的原子笔记（附来源引用）。因为有完整原始资料，比 `lizard` 生成的笔记更详细。

#### 查询 wiki

```
/llm-wiki:wiki-search <关键词>
```

全文搜索 wiki 目录，返回匹配的页面和相关段落。

#### 提交变更

```
/llm-wiki:wiki-push
```

自动生成 commit message，暂存 wiki 相关文件，push 到远程。

#### 创建 Pull Request

```
/llm-wiki:wiki-pr
```

基于 `templates/pr-template.md` 自动填充 PR 描述（日期、新增/更新页面、知识摘要），用 `gh` 创建 PR。

### 仓库结构

```
llm-wiki/
├── .claude-plugin/    # Claude Code 插件配置
│   ├── plugin.json    # 插件清单
│   └── marketplace.json # Marketplace 注册
├── .github/
│   └── pull_request_template.md # PR 模板
├── agents/
│   └── wiki-curator.md # 批量操作 agent（模型：sonnet）
├── wiki/              # LLM 生成并维护的 wiki 页面
├── index.md           # 所有页面的索引，按分类组织
├── log.md             # 操作日志（ingest、query、lint 记录）
├── CLAUDE.md          # Schema：告诉 LLM wiki 的规范和工作流
├── skills/            # Claude Code skills
│   ├── lizard/        # 每日知识蒸馏（自动 push）
│   ├── lizard-eat/    # 从外部 URL 摄取知识
│   └── wiki-search/   # wiki 搜索
├── commands/          # Claude Code commands
│   ├── wiki-push.md   # 提交推送
│   └── wiki-pr.md     # 创建 PR
└── templates/
    └── pr-template.md # PR 描述模板
```

---

<a name="english"></a>
## English

### What is this

llm-wiki is a personal knowledge base maintained by an LLM. Unlike RAG, it doesn't re-retrieve from raw documents on every query — instead, it has the LLM **incrementally build and maintain a persistent wiki**: structured markdown files, cross-referenced, contradictions flagged, synthesis that compounds over time.

Your job: source content, explore ideas, ask good questions.  
The LLM's job: summarize, cross-reference, file, maintain.

The wiki is a compounding asset — every source you add and every good question you ask makes it richer.

**Use cases**

- Technical learning: go deep on a domain over weeks/months, build a structured knowledge graph
- Daily review: use `/lizard` at end of day to distill knowledge from all your Claude sessions
- Reading notes: file chapters as you go, auto-build cross-references for characters, themes, plot threads
- Team internal wiki: fed by Slack threads, meeting notes, project docs — LLM does the maintenance

### Installation

#### Prerequisites

- [Claude Code](https://claude.ai/code) CLI installed and logged in
- [Obsidian](https://obsidian.md) (optional, for browsing the wiki)

#### Steps

Run three commands inside Claude Code:

```
/plugin marketplace add https://github.com/orriduck/llm-wiki
/plugin install llm-wiki@llm-wiki
/reload-plugins
```

That's it. No cloning, no environment variables. The plugin auto-detects its own path — all skills work immediately.

**Open in Obsidian** (optional)

The plugin installs to `~/.claude/plugins/cache/llm-wiki/llm-wiki/<version>/`. Open that directory as an Obsidian vault to browse the wiki graph view.

### Daily workflow

#### End-of-day: distill today's knowledge

```
/llm-wiki:lizard
```

Scans all today's Claude session transcripts, extracts reusable knowledge, writes atomic notes to `wiki/`, updates `index.md` and `log.md`, then auto-commits and pushes.

Filter by topic:

```
/llm-wiki:lizard Python
```

#### Ingest from a URL

```
/llm-wiki:lizard-eat <url> <topic>
```

Fetches a URL and distills it into detailed atomic notes with source citations. More thorough than `lizard` because it has the full original content to work from.

#### Search the wiki

```
/llm-wiki:wiki-search <query>
```

Full-text search across the wiki directory, returning matching pages and relevant excerpts.

#### Commit changes

```
/llm-wiki:wiki-push
```

Auto-generates a commit message, stages wiki-related files, pushes to remote.

#### Create a Pull Request

```
/llm-wiki:wiki-pr
```

Fills in the PR template with date, new/updated pages, and a knowledge summary, then creates the PR via `gh`.

### Repository structure

```
llm-wiki/
├── .claude-plugin/    # Claude Code plugin configuration
│   ├── plugin.json    # Plugin manifest
│   └── marketplace.json # Marketplace registration
├── .github/
│   └── pull_request_template.md # PR template
├── agents/
│   └── wiki-curator.md # Bulk operations agent (model: sonnet)
├── wiki/              # LLM-generated and maintained wiki pages
├── index.md           # Index of all pages, organized by category
├── log.md             # Operation log (ingest, query, lint entries)
├── CLAUDE.md          # Schema: tells the LLM the wiki's conventions and workflows
├── skills/            # Claude Code skills
│   ├── lizard/        # Daily knowledge distillation (auto-push)
│   ├── lizard-eat/    # Ingest knowledge from a URL
│   └── wiki-search/   # Wiki search
├── commands/          # Claude Code commands
│   ├── wiki-push.md   # Commit and push
│   └── wiki-pr.md     # Create PR
└── templates/
    └── pr-template.md # PR description template
```
