---
description: Create a Pull Request for the current llm-wiki-content branch, filling in changed pages and a knowledge summary.
---

Create a Pull Request for wiki updates.

## Steps

1. Resolve and enter the content repo:
   ```bash
   WIKI_REPO_PATH="$(python3 scripts/wiki_path.py)"
   cd "${WIKI_REPO_PATH}"
   ```
   If resolution fails, tell the user to run `/llm-wiki:setup`, then stop.

2. Confirm the current branch is not `main` or `master`:
   ```bash
   git branch --show-current
   ```
   If on `main` or `master`, ask the user to switch to a content branch and stop.

3. Get the diff against `main` and list changed wiki pages:
   ```bash
   git diff --name-only origin/main...HEAD -- wiki/ index.md log.md 2>/dev/null || \
   git diff --name-only main...HEAD -- wiki/ index.md log.md 2>/dev/null
   ```

4. Read the PR template:
   ```bash
   cat "<PLUGIN_PATH>/templates/pr-template.md"
   ```
   `<PLUGIN_PATH>` is the current `llm-wiki` plugin repository path; the PR target is still `llm-wiki-content`.

5. Generate a complete PR body from the template and changed files. Fill in date, created pages, updated pages, and a concise knowledge summary.

6. Create the PR:
   ```bash
   gh pr create \
     --title "[$(date +%Y-%m-%d)] wiki update: <short title>" \
     --body "<filled PR body>" \
     --base main
   ```

7. Output the PR link.
