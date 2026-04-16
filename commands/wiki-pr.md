---
description: Create a Pull Request based on the PR template, auto-filling the list of wiki pages added/updated today and a knowledge summary. / 基于 PR 模板创建 Pull Request，自动填充今日新增/更新的 wiki 页面列表和知识摘要。
---

Create a Pull Request for today's wiki updates.

> 为今日 wiki 更新创建一个 Pull Request。

## Steps / 步骤

1. Enter the wiki repo directory / 进入 wiki 仓库目录：
   ```bash
   cd "${WIKI_REPO_PATH}"
   ```
   If `$WIKI_REPO_PATH` is not set, prompt the user to run `/setup` first, then stop. / 若 `$WIKI_REPO_PATH` 未设置，提示用户先运行 `/setup`，然后停止。

2. Confirm the current branch is not main/master / 确认当前分支不是 main/master：
   ```bash
   git branch --show-current
   ```
   If on main/master, prompt the user to switch to a feature branch first, then stop. / 若在 main/master 上，提示用户先切换到功能分支，停止。

3. Get the diff against main and count changed wiki pages / 获取与 main 的差异，统计变更的 wiki 页面：
   ```bash
   git diff --name-only origin/main...HEAD -- wiki/ index.md log.md 2>/dev/null || \
   git diff --name-only main...HEAD -- wiki/ index.md log.md 2>/dev/null
   ```

4. Read the PR template / 读取 PR 模板：
   ```bash
   cat "${WIKI_REPO_PATH}/templates/pr-template.md"
   ```

5. Based on the template and change info, generate a complete PR description (fill in the date, new pages list, updated pages list, and a brief knowledge summary in both English and Chinese). / 基于模板和变更信息，生成完整的 PR 描述（自动填充日期、新增页面列表、更新页面列表，正文用中英双语填写）。

6. Create the PR / 创建 PR：
   ```bash
   gh pr create \
     --title "[$(date +%Y-%m-%d)] wiki update: <short title / 简短标题>" \
     --body "<filled PR description / 填充后的 PR 描述>" \
     --base main
   ```

7. Output the PR link. / 输出 PR 链接。
