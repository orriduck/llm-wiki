---
name: setup
description: llm-wiki 首次配置向导。设置本地 wiki 仓库路径（WIKI_REPO_PATH），写入用户全局 Claude 设置，让 lizard、wiki-search 等 skill 能正常工作。clone 仓库后第一件事运行这个。
user-invocable: true
allowed-tools: "Bash Read Write"
---

# llm-wiki 初始化设置

欢迎使用 llm-wiki！这个向导会帮你配置本地环境。

## 第一步：检测当前路径

运行：

```bash
pwd
```

同时检查当前目录是否为 llm-wiki repo（存在 `wiki/` 子目录和 `CLAUDE.md`）：

```bash
test -d "$(pwd)/wiki" && test -f "$(pwd)/CLAUDE.md" && echo "YES" || echo "NO"
```

若当前目录就是 llm-wiki repo，建议以 `$(pwd)` 作为 `WIKI_REPO_PATH`，并告知用户。

若不在 repo 目录内，询问用户：**"请输入 llm-wiki 仓库在你本机的绝对路径"**，并验证该路径存在且包含 `wiki/` 子目录：

```bash
test -d "<用户输入路径>/wiki" && echo "有效" || echo "路径无效或不含 wiki/ 目录"
```

## 第二步：写入 WIKI_REPO_PATH 到全局设置

读取 `~/.claude/settings.json`（若不存在则视为 `{}`），然后将 `WIKI_REPO_PATH` 写入 `env` 块：

```bash
python3 -c "
import json, os

settings_path = os.path.expanduser('~/.claude/settings.json')
try:
    with open(settings_path) as f:
        settings = json.load(f)
except FileNotFoundError:
    settings = {}

settings.setdefault('env', {})['WIKI_REPO_PATH'] = '<确认的路径>'

with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)

print('已写入 WIKI_REPO_PATH =', settings['env']['WIKI_REPO_PATH'])
"
```

## 第三步：验证

运行以下命令确认环境变量生效（需要重启 Claude Code 会话后才能在新会话中自动读取，但可以在当前 shell 中手动验证）：

```bash
python3 -c "
import json, os
p = os.path.expanduser('~/.claude/settings.json')
s = json.load(open(p))
print('WIKI_REPO_PATH =', s.get('env', {}).get('WIKI_REPO_PATH', '未找到'))
"
```

## 第四步：可选 — git 用户配置

检查 git 用户配置是否已设置：

```bash
git config --global user.name && git config --global user.email || echo "git 用户信息未配置"
```

若未配置，提示用户：

```
请运行：
  git config --global user.name "你的名字"
  git config --global user.email "你的邮箱"
```

## 完成

配置完成后告知用户：

```
✓ WIKI_REPO_PATH 已设置为：<路径>
✓ 配置已写入 ~/.claude/settings.json

接下来你可以：
- /lizard              — 蒸馏今日会话知识
- /wiki-search <关键词> — 搜索 wiki 内容
- /wiki-push           — 提交并推送 wiki 更新
- /wiki-pr             — 创建 Pull Request

注意：重启 Claude Code 后 WIKI_REPO_PATH 环境变量会自动加载。
```
