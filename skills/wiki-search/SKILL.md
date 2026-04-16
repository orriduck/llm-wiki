---
name: wiki-search
description: Search llm-wiki for relevant content and return matching pages and passages. Use this before answering questions or when the user wants to find existing notes on a topic. / 在 llm-wiki 中搜索相关内容，返回匹配的页面和段落。适合在回答问题前先查阅知识库，或者用户想查找某个主题的已有笔记时使用。
user-invocable: true
allowed-tools: "Read Glob Grep Bash"
argument-hint: "<search keyword / 搜索关键词>"
---

# Wiki Search / Wiki 搜索

Search the llm-wiki knowledge base for content related to `$ARGUMENTS`.

> 在 llm-wiki 知识库中搜索与 `$ARGUMENTS` 相关的内容。

## Step 1: Confirm Path / 第一步：确认路径

```bash
echo "${WIKI_REPO_PATH:-not set / 未设置}"
```

If not set, prompt the user to run `/setup` first, then stop.

> 若未设置，提示用户先运行 `/setup`，然后停止。

If `$ARGUMENTS` is empty, prompt the user to provide search keywords, then stop.

> 若 `$ARGUMENTS` 为空，提示用户提供搜索关键词，然后停止。

## Step 2: Search index.md (High-Level Match) / 第二步：搜索 index.md（高层级匹配）

Read `$WIKI_REPO_PATH/index.md` and find entries whose title or summary contains the keyword. These are first-priority candidate pages.

> 读取 `$WIKI_REPO_PATH/index.md`，找出标题或摘要中包含关键词的条目。这些是第一优先级候选页面。

## Step 3: Full-Text Search wiki/ / 第三步：全文搜索 wiki/

Full-text search for the keyword (case-insensitive) in the `$WIKI_REPO_PATH/wiki/` directory, listing matching files and lines:

> 在 `$WIKI_REPO_PATH/wiki/` 目录下全文搜索关键词（大小写不敏感），列出匹配的文件和行：

```bash
grep -rli "$ARGUMENTS" "${WIKI_REPO_PATH}/wiki/" 2>/dev/null | head -20
```

Also get context around matching lines:

> 同时获取匹配行的上下文：

```bash
grep -rni "$ARGUMENTS" "${WIKI_REPO_PATH}/wiki/" --include="*.md" -A 2 -B 1 2>/dev/null | head -100
```

## Step 4: Read Most Relevant Pages / 第四步：读取最相关页面

Combine results from Steps 2 and 3, sort by relevance, and read the full content of the top **3 matching pages**.

> 综合第二、三步的结果，按相关度排序，读取最匹配的前 **3 个页面**的完整内容。

## Step 5: Return Results / 第五步：返回结果

Report search results in the following format: / 以如下格式汇报搜索结果：

```
## Search Results / 搜索结果：<keyword / 关键词>

Found N relevant pages / 找到 N 个相关页面：

### 1. [[Page Name / 页面名]]
Path / 路径：wiki/page-name.md
Relevant passage / 相关段落：
> <matching passage / 匹配的段落>

### 2. ...
```

If no matches are found, inform the user and suggest: / 若没有找到任何匹配内容，告知用户，并建议：
- Try different keywords / 尝试不同关键词
- The topic may not have notes yet — add via `/lizard` or manual ingest / 该主题可能尚未有笔记，可通过 `/lizard` 或手动 ingest 添加
