---
name: wiki-search
description: Search the configured llm-wiki-content repository.
user-invocable: true
allowed-tools: "Bash Read Glob Grep"
argument-hint: "<query>"
---

# Wiki Search

## Step 1: Resolve the wiki path

```bash
python3 scripts/wiki_path.py
```

If it cannot be found, tell the user to run `/llm-wiki:setup` or set `LLM_WIKI_PATH` to their `llm-wiki-content` checkout.

## Step 2: Run search

```bash
python3 scripts/wiki_search.py "$ARGUMENTS"
```

## Step 3: Summarize results

Read the most relevant pages from the search results and summarize them.

If there are no results, suggest creating new knowledge with `lizard` or `lizard-eat`.
