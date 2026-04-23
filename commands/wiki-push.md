---
description: Stage, commit, and push wiki updates from llm-wiki-content on the current content branch. Generates a commit message from changed files.
---

Commit and push local `llm-wiki-content` changes to the remote repository.

## Steps

1. Resolve and enter the content repo:
   ```bash
   WIKI_REPO_PATH="$(python3 scripts/wiki_path.py)"
   cd "${WIKI_REPO_PATH}"
   ```
   If resolution fails, tell the user to run `/llm-wiki:setup`, then stop.

2. Check for changes:
   ```bash
   git status --short
   ```
   If there are no changes, say "no changes to commit" and stop.

3. Confirm the current branch is not `main` or `master`:
   ```bash
   git branch --show-current
   ```
   If on `main` or `master`, ask the user to switch to a content branch and stop.

4. Inspect changed files and generate a commit message:
   - Format: `[YYYY-MM-DD] wiki update: <new/updated page names, comma-separated, max 3; use "and N more" for extras>`
   - Example: `[2026-04-16] wiki update: Docker multi-stage builds, Rust ownership, and 2 more`

5. Stage wiki content files:
   ```bash
   git add wiki/ index.md log.md
   ```
   Do not stage plugin repository files such as `skills/`, `scripts/`, or `commands/`. Those belong to `llm-wiki`, not `llm-wiki-content`.

6. Commit:
   ```bash
   git commit -m "<generated commit message>"
   ```

7. Push the current branch:
   ```bash
   git push -u origin "$(git branch --show-current)"
   ```

8. Report the pushed remote branch.
