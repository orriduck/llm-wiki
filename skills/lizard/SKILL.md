---
name: lizard
description: Run at end of day to distill reusable knowledge from all today's Claude sessions into atomic wiki notes. / 每日收工时运行，从今天所有 Claude 会话中蒸馏可复用的知识点，自动整理为原子笔记写入 wiki。
user-invocable: true
allowed-tools: "Bash Read Write Glob Grep"
argument-hint: "[topic-filter]"
---

# Lizard — Daily Knowledge Distillation / 每日知识蒸馏

You are a knowledge distillation expert. Your task: read all of today's Claude sessions, extract valuable and reusable knowledge points, and organize them as atomic notes that comply with the llm-wiki spec.

> 你是一个知识蒸馏专家。你的任务是：读取今天所有 Claude 会话的内容，提取其中有价值的、可复用的知识点，整理为符合 llm-wiki 规范的原子笔记。

## Step 1: Confirm Wiki Path / 第一步：确认 wiki 路径

Check whether the environment variable `$WIKI_REPO_PATH` is set:

> 检查环境变量 `$WIKI_REPO_PATH` 是否已设置：

```bash
echo "${WIKI_REPO_PATH:-not set / 未设置}"
```

If not set, prompt the user to run `/setup` first, then stop.

> 若未设置，提示用户先运行 `/setup`，然后停止。

## Step 2: Fetch Today's Session Content / 第二步：获取今日会话内容

Run the following command to extract conversation text from all of today's Claude sessions (skipping tool-call noise, keeping only human/assistant messages):

> 运行以下命令提取今天所有 Claude 会话中的对话文本（跳过工具调用的噪音，只保留 human/assistant 消息）：

```bash
python3 -c "
import json, glob, os
from datetime import date

today = date.today().isoformat()
results = []
pattern = os.path.expanduser('~/.claude/projects/**/*.jsonl')
files = glob.glob(pattern, recursive=True)

for f in sorted(files):
    try:
        mdate = date.fromtimestamp(os.path.getmtime(f)).isoformat()
        if mdate != today:
            continue
        lines = open(f, encoding='utf-8', errors='ignore').readlines()
        session_msgs = []
        for line in lines:
            try:
                e = json.loads(line)
                role = e.get('type') or e.get('role', '')
                text = e.get('text', '')
                if not text and isinstance(e.get('content'), str):
                    text = e['content']
                if not text and isinstance(e.get('content'), list):
                    for block in e['content']:
                        if isinstance(block, dict) and block.get('type') == 'text':
                            text += block.get('text', '')
                if role in ('human', 'user', 'assistant') and text.strip():
                    session_msgs.append(f'[{role}] {text[:800]}')
            except:
                pass
        if session_msgs:
            rel = os.path.relpath(f, os.path.expanduser('~'))
            results.append(f'=== Session file / 会话文件: ~/{rel} ===')
            results.extend(session_msgs[:60])
    except:
        pass

if results:
    print('\n'.join(results))
else:
    print('No Claude sessions found for today. / 今日暂无 Claude 会话记录。')
"
```

If no sessions are found, inform the user and stop.

> 若没有找到任何会话，告知用户并停止。

## Step 3: Analyze Knowledge Points / 第三步：分析知识点

Carefully read the session content above. You need to:

> 仔细阅读上述会话内容。你需要：

1. **Identify knowledge points / 识别知识点**: Find technical concepts, tool usage, best practices, pitfall experiences, and decision rationale. Filter out purely personal matters, one-off instructions, and repetitive small talk. / 找出其中涉及的技术概念、工具用法、最佳实践、踩坑经验、决策依据等。过滤掉纯粹的个人私务、临时性指令、重复的闲聊。
2. **Deduplicate and merge / 去重归并**: Consolidate multiple mentions of the same topic into one knowledge point. / 同一个主题的多处提及合并为一个知识点。
3. **Assess value / 评估价值**: Only keep content with reuse value ("how to configure X", "how Y works", "pitfalls of Z", etc.). / 只保留有复用价值的内容（"如何配置 X"、"Y 的工作原理"、"Z 的踩坑"等）。

If the user passed `$ARGUMENTS` (topic-filter), only process knowledge points related to that topic.

> 若用户传入了 `$ARGUMENTS`（topic-filter），只处理与该主题相关的知识点。

## Step 4: Read Existing Wiki Index / 第四步：读取现有 wiki 索引

```bash
cat "${WIKI_REPO_PATH}/index.md"
```

For each knowledge point, determine: / 对于每个知识点，判断：
- Is there already a corresponding wiki page? / 是否已有对应的 wiki 页面？
- Does the existing page need supplementation/updates? / 现有页面是否需要补充/更新？

## Step 5: Write Atomic Notes / 第五步：写入原子笔记

For each knowledge point: / 对于每个知识点：

**If a new page is needed / 若需新建页面**: Create a new markdown file in `$WIKI_REPO_PATH/wiki/`.

> 在 `$WIKI_REPO_PATH/wiki/` 创建新 markdown 文件。

File naming: English kebab-case, e.g. `docker-multi-stage-build.md`.

> 文件命名规则：英文 kebab-case，如 `docker-multi-stage-build.md`。

Page format (bilingual — English first, Chinese second / 页面格式，双语——英文在前，中文在后):
```markdown
# Page Title / 页面标题

> Source: distilled from Claude session via lizard · YYYY-MM-DD
> 来源：通过 lizard 从 Claude 会话蒸馏 · YYYY-MM-DD

## Core Concepts / 核心概念

...

## Key Details / 关键细节

...

## Related Links / 相关链接

- [[Related Page / 相关页面]]
```

**If updating an existing page / 若需更新现有页面**: Read the page first, then append or modify content at the appropriate location, maintaining style consistency.

> 读取页面后在合适的位置追加或修改内容，保持风格一致。

All content must be **bilingual: English first, Chinese second** (except filenames and code snippets).

> 所有内容必须为**双语：英文在前，中文在后**（文件名和代码片段除外）。

## Step 6: Update index.md and log.md / 第六步：更新 index.md 和 log.md

**index.md**: Append a new page entry under the appropriate category. Format:

> 在对应分类下追加新页面条目，格式：

```
| [[Page Name / 页面名]] | One-line summary / 一句话摘要 |
```

**log.md**: Prepend a log entry at the top of the file:

> 在文件开头追加一条日志：

```
## [YYYY-MM-DD] lizard | Distilled N sessions, created X pages, updated Y pages / 蒸馏今日 N 个会话，新增 X 页，更新 Y 页
```

## Done / 完成后

Briefly report: which pages were created, which were updated, and which knowledge points were not turned into standalone pages due to insufficient depth (you can suggest the user supplement them later).

> 简要汇报：新建了哪些页面、更新了哪些页面，以及有哪些知识点因内容不够充实而未单独建页（可以提示用户后续补充）。
