# Agent Instructions

`CLAUDE.md` is the single source of truth for this wiki's operating model, structure, language policy, privacy rules, and maintenance workflows.

This repository is tooling only. Wiki content lives in the separately configured `llm-wiki-content` checkout. All agents, including Codex/OpenAI agents, should resolve that content path with `python3 scripts/wiki_path.py` before reading or writing notes.

Keep this file intentionally thin so the repository has only one canonical instruction document to maintain.

For quick orientation:

- Read `CLAUDE.md`.
- Resolve the content repo with `python3 scripts/wiki_path.py`; if it fails, run `/llm-wiki:setup`.
- Search existing wiki content before answering or writing.
- When adding or updating knowledge, update the relevant `wiki/` page, `index.md`, and `log.md`.
- Keep generated wiki content bilingual: English first, Chinese second.
- Generalize or omit sensitive information before writing it to the wiki.
- Do not write note content into the plugin checkout or plugin cache. Use `llm-wiki-content`.
