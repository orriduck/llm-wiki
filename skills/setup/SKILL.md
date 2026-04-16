---
name: setup
description: First-time setup wizard for llm-wiki. Sets the local wiki repo path (WIKI_REPO_PATH), writes it to global Claude settings so skills like lizard and wiki-search work correctly. Run this right after cloning the repo. / llm-wiki 首次配置向导。设置本地 wiki 仓库路径（WIKI_REPO_PATH），写入用户全局 Claude 设置，让 lizard、wiki-search 等 skill 能正常工作。clone 仓库后第一件事运行这个。
user-invocable: true
allowed-tools: "Bash Read Write"
---

# llm-wiki Setup / llm-wiki 初始化设置

Welcome to llm-wiki! This wizard will help you configure your local environment.

> 欢迎使用 llm-wiki！这个向导会帮你配置本地环境。

## Step 1: Detect Current Path / 第一步：检测当前路径

Run: / 运行：

```bash
pwd
```

Also check whether the current directory is the llm-wiki repo (contains a `wiki/` subdirectory and `CLAUDE.md`):

> 同时检查当前目录是否为 llm-wiki repo（存在 `wiki/` 子目录和 `CLAUDE.md`）：

```bash
test -d "$(pwd)/wiki" && test -f "$(pwd)/CLAUDE.md" && echo "YES" || echo "NO"
```

If the current directory is the llm-wiki repo, suggest using `$(pwd)` as `WIKI_REPO_PATH` and inform the user.

> 若当前目录就是 llm-wiki repo，建议以 `$(pwd)` 作为 `WIKI_REPO_PATH`，并告知用户。

If not in the repo directory, ask the user: **"Please enter the absolute path of the llm-wiki repo on your machine / 请输入 llm-wiki 仓库在你本机的绝对路径"**, and validate that the path exists and contains a `wiki/` subdirectory:

> 若不在 repo 目录内，询问用户，并验证该路径存在且包含 `wiki/` 子目录：

```bash
test -d "<user-input-path>/wiki" && echo "valid / 有效" || echo "invalid path or missing wiki/ / 路径无效或不含 wiki/ 目录"
```

## Step 2: Write WIKI_REPO_PATH to Global Settings / 第二步：写入 WIKI_REPO_PATH 到全局设置

Read `~/.claude/settings.json` (treat as `{}` if it doesn't exist), then write `WIKI_REPO_PATH` into the `env` block:

> 读取 `~/.claude/settings.json`（若不存在则视为 `{}`），然后将 `WIKI_REPO_PATH` 写入 `env` 块：

```bash
python3 -c "
import json, os

settings_path = os.path.expanduser('~/.claude/settings.json')
try:
    with open(settings_path) as f:
        settings = json.load(f)
except FileNotFoundError:
    settings = {}

settings.setdefault('env', {})['WIKI_REPO_PATH'] = '<confirmed path / 确认的路径>'

with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)

print('Written WIKI_REPO_PATH = / 已写入 WIKI_REPO_PATH =', settings['env']['WIKI_REPO_PATH'])
"
```

## Step 3: Verify / 第三步：验证

Run the following to confirm the environment variable was saved (a new Claude Code session must be restarted for it to auto-load, but you can verify manually in the current shell):

> 运行以下命令确认环境变量生效（需要重启 Claude Code 会话后才能在新会话中自动读取，但可以在当前 shell 中手动验证）：

```bash
python3 -c "
import json, os
p = os.path.expanduser('~/.claude/settings.json')
s = json.load(open(p))
print('WIKI_REPO_PATH =', s.get('env', {}).get('WIKI_REPO_PATH', 'not found / 未找到'))
"
```

## Step 4 (Optional): Git User Config / 第四步（可选）：git 用户配置

Check whether git user config is set: / 检查 git 用户配置是否已设置：

```bash
git config --global user.name && git config --global user.email || echo "git user info not configured / git 用户信息未配置"
```

If not configured, prompt the user: / 若未配置，提示用户：

```
Please run / 请运行：
  git config --global user.name "Your Name / 你的名字"
  git config --global user.email "your@email.com"
```

## Done / 完成

After configuration, inform the user: / 配置完成后告知用户：

```
✓ WIKI_REPO_PATH set to / 已设置为：<path / 路径>
✓ Config written to / 配置已写入 ~/.claude/settings.json

Next steps / 接下来你可以：
- /lizard              — Distill today's session knowledge / 蒸馏今日会话知识
- /wiki-search <keyword / 关键词> — Search wiki content / 搜索 wiki 内容
- /wiki-push           — Commit and push wiki updates / 提交并推送 wiki 更新
- /wiki-pr             — Create Pull Request / 创建 Pull Request

Note / 注意：WIKI_REPO_PATH will auto-load after restarting Claude Code. / 重启 Claude Code 后 WIKI_REPO_PATH 环境变量会自动加载。
```
