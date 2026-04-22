# Multi-Agent Entry (Codex / OpenAI Agents)

This repository is a shared LLM-maintained wiki. All agents (Codex, Claude, etc.) must follow the same core rules defined in `CLAUDE.md`.

## Core Principles

- The wiki is a persistent, compounding knowledge base (NOT stateless RAG)
- All pages are markdown and interlinked
- Index (`index.md`) and log (`log.md`) must always be updated
- All content must be generalized (no sensitive/internal data)
- Preferred format: English first, Chinese second (same as CLAUDE.md)

## Path Resolution

Agents should resolve wiki root using this priority:

1. `LLM_WIKI_PATH` env var
2. Current repo root
3. Claude plugin install path (fallback)

Use: `python3 scripts/wiki_path.py`

## Common Operations

### Search

Always search before answering:

```
python3 scripts/wiki_search.py <query>
```

### Write / Update

When adding knowledge:

1. Create or update page under `wiki/`
2. Update `index.md`
3. Append to `log.md`

### Ingest

Agents may ingest from:
- current conversation
- pasted transcripts
- URLs

Follow schema in `CLAUDE.md`

## Notes

- Codex does NOT use Claude Skills format
- This file acts as the entry point for non-Claude agents
- Keep adapters thin, reuse shared scripts
