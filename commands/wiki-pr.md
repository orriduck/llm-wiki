---
description: 基于 PR 模板创建 Pull Request，自动填充今日新增/更新的 wiki 页面列表和知识摘要。
---

为今日 wiki 更新创建一个 Pull Request。

## 步骤

1. 进入 wiki 仓库目录：
   ```bash
   cd "${WIKI_REPO_PATH}"
   ```
   若 `$WIKI_REPO_PATH` 未设置，提示用户先运行 `/setup`，然后停止。

2. 确认当前分支不是 main/master：
   ```bash
   git branch --show-current
   ```
   若在 main/master 上，提示用户先切换到功能分支，停止。

3. 获取与 main 的差异，统计变更的 wiki 页面：
   ```bash
   git diff --name-only origin/main...HEAD -- wiki/ index.md log.md 2>/dev/null || \
   git diff --name-only main...HEAD -- wiki/ index.md log.md 2>/dev/null
   ```

4. 读取 PR 模板：
   ```bash
   cat "${WIKI_REPO_PATH}/templates/pr-template.md"
   ```

5. 基于模板和变更信息，生成完整的 PR 描述（中文填写正文，自动填充日期、新增页面列表、更新页面列表）。

6. 创建 PR：
   ```bash
   gh pr create \
     --title "[$(date +%Y-%m-%d)] wiki update: <简短标题>" \
     --body "<填充后的 PR 描述>" \
     --base main
   ```

7. 输出 PR 链接。
