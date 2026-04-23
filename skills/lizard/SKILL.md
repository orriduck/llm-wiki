---
name: lizard
description: End-of-day distillation. Reads today's Claude sessions, extracts reusable knowledge, and writes atomic notes into the configured llm-wiki-content repo.
user-invocable: true
allowed-tools: "Bash Read Write Glob Grep"
argument-hint: "[topic-filter]"
---

# Lizard — Daily Knowledge Distillation

You are a knowledge distillation specialist. Your task is to read today's Claude session content, extract reusable knowledge, and organize it into atomic notes that follow the llm-wiki conventions.

## Step 1: Resolve the content repository and verify git

Use the shared resolver to find the `llm-wiki-content` checkout:

```bash
python3 scripts/wiki_path.py
```

Treat the output as `WIKI_PATH`. Use this path for every later step.

If it cannot be found, tell the user to run `/llm-wiki:setup` or set `LLM_WIKI_PATH` to their `llm-wiki-content` checkout, then stop.

Verify that the content repo is initialized and is not the plugin repo:

```bash
test -d "<WIKI_PATH>/.git" && test -d "<WIKI_PATH>/wiki" && test -f "<WIKI_PATH>/index.md" && test -f "<WIKI_PATH>/log.md"
```

If validation fails, stop and ask the user to rerun `/llm-wiki:setup`. Do not initialize a new wiki inside the plugin install directory.

## Step 2: Collect today's session content

Run this command to extract human/assistant text from today's Claude sessions while skipping tool-call noise:

```bash
python3 -c "
import json, glob, os
from datetime import date

today = date.today().isoformat()
results = []
pattern = os.path.expanduser('~/.claude/projects/**/*.jsonl')
files = [f for f in glob.glob(pattern, recursive=True) if '/subagents/' not in f]

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
                msg = e.get('message', {})
                if not isinstance(msg, dict):
                    continue
                role = msg.get('role', '')
                content = msg.get('content', '')
                text = ''
                if isinstance(content, str):
                    text = content
                elif isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get('type') == 'text':
                            text += block.get('text', '')
                if role in ('user', 'assistant') and text.strip():
                    session_msgs.append(f'[{role}] {text[:800]}')
            except:
                pass
        if session_msgs:
            rel = os.path.relpath(f, os.path.expanduser('~'))
            results.append(f'=== Session file: ~/{rel} ===')
            results.extend(session_msgs[:60])
    except:
        pass

if results:
    print('\n'.join(results))
else:
    print('No Claude sessions found for today.')
"
```

If no sessions are found, tell the user and stop.

## Step 3: Analyze knowledge points

Read the session content carefully. You need to:

1. **Identify knowledge points**: technical concepts, tool usage, best practices, debugging lessons, decision rationale, and reusable patterns. Filter out purely personal tasks, temporary instructions, and repetitive chat.
2. **Deduplicate and merge**: combine repeated mentions of the same topic.
3. **Assess value**: keep only reusable knowledge such as "how to configure X", "how Y works", or "pitfalls with Z".

If the user provided `$ARGUMENTS` as a topic filter, process only matching knowledge points.

## Step 4: Read the existing wiki index

```bash
cat "<WIKI_PATH>/index.md"
```

For each knowledge point, decide:
- Is there already a matching wiki page?
- Should an existing page be updated?

## Step 5: Write atomic notes

For each knowledge point:

**If a new page is needed**: create a Markdown file under `<WIKI_PATH>/wiki/`.

Filename rule: English kebab-case, for example `docker-multi-stage-build.md`.

Page content must follow `CLAUDE.md`: prefer English first, Chinese second bilingual structure, and follow privacy-scrubbing rules.

**If updating an existing page**: read it first, then append or modify content in the right place while preserving style.

## Step 6: Update index.md and log.md

**index.md**: add or update page entries under the matching category.

**log.md**: prepend a log entry:
```
## [YYYY-MM-DD] lizard | distilled N sessions, created X pages, updated Y pages
```

## Step 7: Commit to the content repository

After writing notes:

```bash
cd "<WIKI_PATH>" && git add wiki/ index.md log.md && git status --short
```

If there are changes, commit to the current branch:

```bash
cd "<WIKI_PATH>" && \
  git commit -m "lizard: $(date +%Y-%m-%d) distilled N sessions, created X pages, updated Y pages"
```

Replace N/X/Y with the actual counts.

Do not push directly to `main`. If the user wants to publish, tell them to run `/llm-wiki:wiki-push` and `/llm-wiki:wiki-pr` so the content branch opens a PR against `llm-wiki-content`.

## Completion

Briefly report created pages, updated pages, and knowledge points that were not substantial enough for their own page.
