# Wiki Content Repository Migration

## Summary

On 2026-04-23, wiki content was split from the agent/skills repository.

- Source repository: `llm-wiki`
- Target repository path: `/workspace/llm-wiki-content`
- Migrated content:
  - `wiki/`
  - `index.md`
  - `log.md`

## Local migration commands

```bash
TARGET=/workspace/llm-wiki-content
mkdir -p "$TARGET"
rsync -a --delete /workspace/llm-wiki/wiki/ "$TARGET/wiki/"
cp /workspace/llm-wiki/index.md "$TARGET/index.md"
cp /workspace/llm-wiki/log.md "$TARGET/log.md"
```

## Notes

- `llm-wiki-content` was initialized as an independent Git repository and committed locally.
- If needed, add your GitHub remote in `llm-wiki-content` and push `main`.
