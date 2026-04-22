# Multi-Agent Architecture

## Goal

Support multiple agents (Claude, Codex, etc.) using a shared wiki core with minimal duplication.

## Design

```
Core (shared)
├── CLAUDE.md (schema)
├── AGENTS.md (entry)
├── scripts/
│   ├── wiki_path.py
│   └── wiki_search.py

Adapters
├── Claude (skills/)
├── Codex (AGENTS.md + future commands)
```

## Key Principle

Do NOT share agent-specific formats.

Instead share:
- wiki schema
- file structure
- scripts
- workflows

## Future Work

- transcript providers (claude / codex)
- unified ingest pipeline
- vector + semantic search
