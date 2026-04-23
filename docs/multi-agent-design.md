# Multi-Agent Architecture

## Goal

Support multiple agents (Claude, Codex, OpenCode/Pi, etc.) using one shared content repository with minimal duplication.

## Design

```
llm-wiki (tooling/plugin)
├── scripts/
│   ├── wiki_path.py
│   ├── setup_wiki.py
│   └── wiki_search.py
├── skills/            # Claude plugin skills
├── commands/          # Claude plugin commands
├── agents/            # Claude managed agents
└── AGENTS.md          # thin cross-agent entry

llm-wiki-content (shared content)
├── CLAUDE.md or AGENTS.md-style schema
├── index.md
├── log.md
└── wiki/
```

## Key Principle

Do not write durable notes into the plugin checkout or plugin cache.

Instead, every agent resolves the shared content path before reading or writing:

```bash
python3 scripts/wiki_path.py
```

Resolution order:

1. `LLM_WIKI_PATH`
2. `~/.llm-wiki/config.json`
3. nearby development checkout such as `../llm-wiki-content`
4. common Obsidian/iCloud locations

If resolution fails, the agent should ask the user to run `/llm-wiki:setup`.

## New-Machine Flow

1. Install Obsidian and enable iCloud Drive if using the default vault location.
2. Install the `llm-wiki` plugin in Claude or the relevant agent environment.
3. Run `/llm-wiki:setup`.
4. Setup clones or connects `llm-wiki-content` inside the Obsidian iCloud folder.
5. Setup writes `~/.llm-wiki/config.json`.
6. All skills and agents operate on `llm-wiki-content`.
7. Note publishing goes through content branches and PRs to `llm-wiki-content`.

## Publishing Model

- `lizard` and `lizard-eat` write and commit notes in the content repo.
- `wiki-push` pushes the current content branch.
- `wiki-pr` opens a PR against `llm-wiki-content/main`.
- Plugin changes are committed separately in `llm-wiki`.

## Future Work

- transcript providers (claude / codex)
- unified ingest pipeline
- vector + semantic search
