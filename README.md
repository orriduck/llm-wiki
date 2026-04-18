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

**1. Clone 仓库**

```bash
git clone https://github.com/orriduck/llm-wiki.git
cd llm-wiki
```

**2. 安装为 Claude Code Plugin**

打开 Claude Code，进入 `/plugins` 界面，添加 marketplace：

```json
// 在 ~/.claude/settings.json 的 extraKnownMarketplaces 中添加：
{
  "extraKnownMarketplaces": {
    "llm-wiki": {
      "source": {
        "source": "github",
        "repo": "orriduck/llm-wiki"
      }
    }
  }
}
```

然后在 `/plugins` 界面找到 `llm-wiki`，点击安装。安装时会提示输入本地仓库路径。

**或者**，在 Claude Code 中直接用本地路径加载（开发/测试用）：

```bash
claude --plugin-dir /path/to/llm-wiki
```

**3. 初始化配置**

打开 Claude Code，进入 llm-wiki 目录后运行：

```
/setup
```

这会将 `WIKI_REPO_PATH` 写入 `~/.claude/settings.json`，后续所有 skill 都依赖此路径。

**4. 用 Obsidian 打开**（可选）

将 llm-wiki 目录作为 Obsidian vault 打开，即可在图谱视图中看到所有页面的连接关系。

### 日常使用

#### 每日收工：蒸馏当天知识

```
/lizard
```

自动扫描今天所有 Claude 会话的 transcript，提取有价值的知识点，整理为原子笔记写入 `wiki/`，并更新 `index.md` 和 `log.md`。

支持按主题过滤：

```
/lizard Python
```

#### 查询 wiki

```
/wiki-search <关键词>
```

全文搜索 wiki 目录，返回匹配的页面和相关段落。

#### 手动 ingest 来源

直接告诉 Claude：

```
帮我把这篇文章整理进 wiki：[粘贴内容或文件路径]
```

Claude 会读取来源、提取关键信息、写摘要页、更新相关页面和索引。

#### 提交变更

```
/wiki-push
```

自动生成 commit message，暂存 wiki 相关文件，push 到当前分支。

#### 创建 Pull Request

```
/wiki-pr
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
│   ├── lizard/        # 每日知识蒸馏
│   ├── wiki-search/   # wiki 搜索
│   └── setup/         # 初始化配置
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

**1. Clone the repo**

```bash
git clone https://github.com/orriduck/llm-wiki.git
cd llm-wiki
```

**2. Install as a Claude Code Plugin**

Open Claude Code, go to `/plugins`, and add this marketplace:

```json
// Add to extraKnownMarketplaces in ~/.claude/settings.json:
{
  "extraKnownMarketplaces": {
    "llm-wiki": {
      "source": {
        "source": "github",
        "repo": "orriduck/llm-wiki"
      }
    }
  }
}
```

Then find `llm-wiki` in `/plugins` and install it. You'll be prompted to enter your local repo path.

**Alternatively**, load directly from a local path (for development/testing):

```bash
claude --plugin-dir /path/to/llm-wiki
```

**3. Run setup**

Inside Claude Code, from the llm-wiki directory:

```
/setup
```

This writes `WIKI_REPO_PATH` to `~/.claude/settings.json` — all other skills depend on this.

**4. Open in Obsidian** (optional)

Open the llm-wiki directory as an Obsidian vault. The graph view shows how all pages connect.

### Daily workflow

#### End-of-day: distill today's knowledge

```
/lizard
```

Scans all today's Claude session transcripts, extracts reusable knowledge, writes atomic notes to `wiki/`, and updates `index.md` and `log.md`.

Filter by topic:

```
/lizard Python
```

#### Search the wiki

```
/wiki-search <query>
```

Full-text search across the wiki directory, returning matching pages and relevant excerpts.

#### Manually ingest a source

Just tell Claude:

```
Please ingest this into the wiki: [paste content or file path]
```

Claude reads the source, extracts key information, writes a summary page, updates related pages and the index.

#### Commit changes

```
/wiki-push
```

Auto-generates a commit message, stages wiki-related files, pushes to the current branch.

#### Create a Pull Request

```
/wiki-pr
```

Fills in the PR template (`templates/pr-template.md`) with date, new/updated pages, and a knowledge summary, then creates the PR via `gh`.

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
│   ├── lizard/        # Daily knowledge distillation
│   ├── wiki-search/   # Wiki search
│   └── setup/         # Initial configuration
├── commands/          # Claude Code commands
│   ├── wiki-push.md   # Commit and push
│   └── wiki-pr.md     # Create PR
└── templates/
    └── pr-template.md # PR description template
```
