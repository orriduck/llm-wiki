---
description: 将今日 wiki 更新（wiki/、index.md、log.md）暂存、提交并推送到远程。会自动从变更文件列表生成 commit message。
---

将 llm-wiki 的本地变更提交并推送到远程仓库。

## 步骤

1. 进入 wiki 仓库目录：
   ```bash
   cd "${WIKI_REPO_PATH}"
   ```
   若 `$WIKI_REPO_PATH` 未设置，提示用户先运行 `/setup`，然后停止。

2. 检查是否有变更：
   ```bash
   git status --short
   ```
   若没有任何变更，告知用户"无变更需要提交"，停止。

3. 查看变更文件列表，生成 commit message：
   - 格式：`[YYYY-MM-DD] wiki update: <新增/修改的页面名（逗号分隔，最多 3 个，超出则写 "等 N 页"）>`
   - 例：`[2026-04-16] wiki update: Docker多阶段构建, Rust所有权模型, 等 2 页`

4. 暂存 wiki 相关文件：
   ```bash
   git add wiki/ index.md log.md
   ```
   若有其他需要一并提交的文件（如 `.claude/` 下的配置），也一起暂存。

5. 提交：
   ```bash
   git commit -m "<生成的 commit message>"
   ```

6. 推送到当前分支：
   ```bash
   git push -u origin "$(git branch --show-current)"
   ```

7. 汇报推送结果，包括推送到的远程分支名。
