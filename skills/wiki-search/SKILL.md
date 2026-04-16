---
name: wiki-search
description: 在 llm-wiki 中搜索相关内容，返回匹配的页面和段落。适合在回答问题前先查阅知识库，或者用户想查找某个主题的已有笔记时使用。
user-invocable: true
allowed-tools: "Read Glob Grep Bash"
argument-hint: "<搜索关键词>"
---

# Wiki 搜索

在 llm-wiki 知识库中搜索与 `$ARGUMENTS` 相关的内容。

## 第一步：确认路径

```bash
echo "${WIKI_REPO_PATH:-未设置}"
```

若未设置，提示用户先运行 `/setup`，然后停止。

若 `$ARGUMENTS` 为空，提示用户提供搜索关键词，然后停止。

## 第二步：搜索 index.md（高层级匹配）

读取 `$WIKI_REPO_PATH/index.md`，找出标题或摘要中包含关键词的条目。这些是第一优先级候选页面。

## 第三步：全文搜索 wiki/

在 `$WIKI_REPO_PATH/wiki/` 目录下全文搜索关键词（大小写不敏感），列出匹配的文件和行：

```bash
grep -rli "$ARGUMENTS" "${WIKI_REPO_PATH}/wiki/" 2>/dev/null | head -20
```

同时获取匹配行的上下文：

```bash
grep -rni "$ARGUMENTS" "${WIKI_REPO_PATH}/wiki/" --include="*.md" -A 2 -B 1 2>/dev/null | head -100
```

## 第四步：读取最相关页面

综合第二、三步的结果，按相关度排序，读取最匹配的前 **3 个页面**的完整内容。

## 第五步：返回结果

以如下格式汇报搜索结果：

```
## 搜索结果：<关键词>

找到 N 个相关页面：

### 1. [[页面名]]
路径：wiki/页面名.md
相关段落：
> <匹配的段落>

### 2. ...
```

若没有找到任何匹配内容，告知用户，并建议：
- 尝试不同关键词
- 该主题可能尚未有笔记，可通过 `/lizard` 或手动 ingest 添加
