---
description: Stage, commit, and push today's wiki updates (wiki/, index.md, log.md) to remote. Auto-generates a commit message from the list of changed files. / 将今日 wiki 更新（wiki/、index.md、log.md）暂存、提交并推送到远程。会自动从变更文件列表生成 commit message。
---

Commit and push local llm-wiki changes to the remote repository.

> 将 llm-wiki 的本地变更提交并推送到远程仓库。

## Steps / 步骤

1. Enter the wiki repo directory / 进入 wiki 仓库目录：
   ```bash
   cd "${WIKI_REPO_PATH}"
   ```
   If `$WIKI_REPO_PATH` is not set, prompt the user to run `/setup` first, then stop. / 若 `$WIKI_REPO_PATH` 未设置，提示用户先运行 `/setup`，然后停止。

2. Check for changes / 检查是否有变更：
   ```bash
   git status --short
   ```
   If there are no changes, inform the user "No changes to commit / 无变更需要提交" and stop. / 若没有任何变更，告知用户并停止。

3. Review the list of changed files and generate a commit message / 查看变更文件列表，生成 commit message：
   - Format / 格式：`[YYYY-MM-DD] wiki update: <page names, comma-separated, max 3; if more write "and N more pages" / 新增/修改的页面名，逗号分隔，最多 3 个，超出则写 "等 N 页">`
   - Example / 例：`[2026-04-16] wiki update: Docker多阶段构建, Rust所有权模型, 等 2 页`

4. Stage wiki-related files / 暂存 wiki 相关文件：
   ```bash
   git add wiki/ index.md log.md
   ```
   If there are other files to commit together (e.g. config under `.claude/`), stage them too. / 若有其他需要一并提交的文件（如 `.claude/` 下的配置），也一起暂存。

5. Commit / 提交：
   ```bash
   git commit -m "<generated commit message / 生成的 commit message>"
   ```

6. Push to current branch / 推送到当前分支：
   ```bash
   git push -u origin "$(git branch --show-current)"
   ```

7. Report the push result, including the name of the remote branch pushed to. / 汇报推送结果，包括推送到的远程分支名。
