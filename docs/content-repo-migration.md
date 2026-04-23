# Wiki Content Repository Migration

## Summary

On 2026-04-23, all vault content was migrated from `llm-wiki` into `llm-wiki-content`.

- Source repository: `llm-wiki` (agent-only after migration)
- Target repository path: `/workspace/llm-wiki-content`
- Migrated content:
  - `wiki/`
  - `.obsidian/`
  - `.obsidianignore`
  - `index.md`
  - `log.md`

## Local migration commands used

```bash
TARGET=/workspace/llm-wiki-content
mkdir -p "$TARGET"
rsync -a --delete /workspace/llm-wiki/wiki/ "$TARGET/wiki/"
rsync -a --delete /workspace/llm-wiki/.obsidian/ "$TARGET/.obsidian/"
cp /workspace/llm-wiki/.obsidianignore "$TARGET/.obsidianignore"
cp /workspace/llm-wiki/index.md "$TARGET/index.md"
cp /workspace/llm-wiki/log.md "$TARGET/log.md"
```

## Result

- `llm-wiki-content` has the migrated content committed locally.
- This `llm-wiki` repository now contains agent-related files only.
