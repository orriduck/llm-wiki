---
name: lizard-eat
description: Given a URL and topic, fetch the source and turn it into detailed atomic wiki notes with source citations.
user-invocable: true
allowed-tools: "Bash Read Write WebFetch Glob Grep"
argument-hint: "<url> <topic>"
---

# Lizard Eat — External Source Ingest

## Step 1: Parse arguments

Parse `$ARGUMENTS` into URL and TOPIC.

## Step 2: Resolve the content repository

```bash
python3 scripts/wiki_path.py
```

Treat the output as `WIKI_PATH`. It must be the `llm-wiki-content` checkout, not the plugin install directory.

If it cannot be found, tell the user to run `/llm-wiki:setup` or set `LLM_WIKI_PATH` to their `llm-wiki-content` checkout, then stop.

## Step 3: Fetch the URL

Use WebFetch to fetch the page content.

## Step 4: Read the existing wiki index

```bash
cat "<WIKI_PATH>/index.md"
```

## Step 5: Create atomic notes

Follow the `CLAUDE.md` schema:
- English first, Chinese second
- scrub sensitive information
- use strong structure

## Step 6: Write files

Write notes under `<WIKI_PATH>/wiki/`.

## Step 7: Update index.md and log.md

## Step 8: Commit to the content repository

```bash
cd "<WIKI_PATH>" && git add wiki/ index.md log.md && git commit -m "lizard-eat: <TOPIC>"
```

Do not push directly to `main`. If the user wants to publish, tell them to run `/llm-wiki:wiki-push` and `/llm-wiki:wiki-pr` so the content branch opens a PR against `llm-wiki-content`.

## Completion

Output a concise change summary.
