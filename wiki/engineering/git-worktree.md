# git worktree

> 允许在同一个 git 仓库中**同时检出多个工作目录**，每个目录可以对应不同的分支，互不干扰。

## 是什么

通常一个 git 仓库只有一个工作目录（working tree），切换分支就必须 `git checkout`，当前未提交的改动要先 stash 或 commit 才能切走。

`git worktree` 打破了这个限制：你可以在仓库目录之外，**额外创建一个或多个工作目录**，每个工作目录绑定到一个不同的分支。多个工作目录共享同一个 `.git` 目录（对象库、引用），因此：

- 切换分支 = 直接 `cd` 到另一个目录，不需要 stash
- 多个 worktree 之间完全隔离：不同目录里的文件改动互不影响
- 同一个分支**不能**被两个 worktree 同时检出（会报错）

## 为什么用

| 场景 | 没有 worktree | 用 worktree |
|------|--------------|-------------|
| 正在 feature 分支开发，需要紧急修 hotfix | 必须 stash → checkout → 修复 → 回来 pop | 直接在另一个目录改，互不影响 |
| 需要对比两个分支的代码 | 来回切换，容易搞混 | 两个目录并排打开，同时查看 |
| CI/CD 脚本需要同时操作多个分支 | 需要 clone 多份仓库 | 一个仓库多个 worktree，节省磁盘 |
| 代码审查时想在本地跑起来看看 | clone 或 stash | 新建临时 worktree 检出 PR 分支 |

---

## 核心命令

### 创建 worktree

```bash
# 基本语法
git worktree add <路径> [分支名]

# 检出已有分支到指定路径
git worktree add ../my-hotfix hotfix/v1.2

# 新建分支并检出（-b 标志）
git worktree add -b feature/new-ui ../feature-ui main

# 指定路径和分支（路径可以是绝对路径或相对路径）
git worktree add /tmp/review-pr-123 origin/pr-123
```

> **命名惯例**：路径通常放在仓库目录的兄弟目录中，例如 `../repo-hotfix`，或专用子目录如 `.worktrees/hotfix`。

### 查看所有 worktree

```bash
git worktree list

# 示例输出：
# /Users/me/Devs/myrepo          abc1234 [main]
# /Users/me/Devs/myrepo-hotfix   def5678 [hotfix/v1.2]
# /tmp/feature-ui                 ghi9012 [feature/new-ui]
```

### 删除 worktree

```bash
# 先手动删除目录，再清理 git 记录
rm -rf ../my-hotfix
git worktree prune

# 或者一步完成（Git 2.17+）
git worktree remove ../my-hotfix

# 如果目录中有未提交改动，需要强制删除
git worktree remove --force ../my-hotfix
```

### 修复损坏的 worktree

```bash
# 如果 worktree 目录被手动删除但 git 记录还在，清理悬空引用
git worktree prune
```

---

## 常用工作流示例

### 场景一：紧急 hotfix

```bash
# 当前在 feature/dashboard 分支开发
# 线上出问题了，需要立刻修 main

# 创建 hotfix worktree
git worktree add -b hotfix/login-bug ../myrepo-hotfix main

# 进入新目录修复
cd ../myrepo-hotfix
# ... 修改代码、测试 ...
git commit -am "fix: 修复登录超时问题"
git push origin hotfix/login-bug

# 回到原来的工作
cd ../myrepo
# feature/dashboard 分支状态完全保留

# 修完后清理
git worktree remove ../myrepo-hotfix
```

### 场景二：检出远程 PR 分支审查

```bash
# 拉取远程分支引用
git fetch origin

# 新建 worktree 检出 PR 分支
git worktree add ../review-pr-456 origin/feature/refactor-auth

# 在新目录里跑测试、查看代码
cd ../review-pr-456
npm install && npm test

# 审查完毕删除
git worktree remove ../review-pr-456
```

### 场景三：对比两个版本

```bash
# 同时检出两个分支，用 IDE 或 diff 工具对比
git worktree add ../myrepo-v1 v1.0.0
git worktree add ../myrepo-v2 v2.0.0

# 在编辑器里分别打开两个目录
code ../myrepo-v1
code ../myrepo-v2
```

---

## 常见参数速查

| 命令 | 说明 |
|------|------|
| `git worktree add <path> <branch>` | 检出已有分支到 path |
| `git worktree add -b <branch> <path> <start>` | 从 start 新建分支并检出到 path |
| `git worktree add --detach <path> <commit>` | 以 detached HEAD 检出某 commit |
| `git worktree list` | 列出所有 worktree |
| `git worktree list --porcelain` | 机器可读格式输出 |
| `git worktree remove <path>` | 删除干净的 worktree |
| `git worktree remove --force <path>` | 强制删除（有未提交改动时） |
| `git worktree prune` | 清理已删除目录的 git 记录 |
| `git worktree move <old> <new>` | 移动 worktree 到新路径 |
| `git worktree lock <path>` | 锁定 worktree（防止 prune 误删） |
| `git worktree unlock <path>` | 解锁 |

---

## 注意事项

- **同一分支不能被两个 worktree 同时检出**，会报 `fatal: 'xxx' is already checked out`。需要先移除一个才能在另一个中检出同名分支。
- Worktree 共享 `.git` 目录，所以 `git fetch`、`git log` 在任一 worktree 中执行都会更新全局状态。
- **`git stash` 是全局共享的**，在一个 worktree 里 stash 的改动，在另一个 worktree 里也能 pop——但要注意路径冲突。
- 删除 worktree 只删除该目录，原始 `.git` 仓库和其他 worktree 不受影响。
- **锁定（lock）**：如果 worktree 在网络磁盘或临时路径上，可以 `git worktree lock` 防止 `prune` 意外清理引用。

---

## 与 Claude Code worktree 集成

Claude Code 的 `superpowers:using-git-worktrees` skill 基于 git worktree 构建了隔离的开发流程：

- 每个功能分支在独立 worktree 中开发，不污染主工作区
- 使用 `EnterWorktree` / `ExitWorktree` 工具在 worktree 间切换
- 任务完成后 worktree 自动清理

相关页面：[[Claude-Code插件与MCP]]

---

## 相关页面

- [[fish]] — fish shell 中可用 `abbr -a gwt "git worktree"` 简化命令
- [[Claude-Code插件与MCP]] — Claude Code 的 worktree 集成工作流
