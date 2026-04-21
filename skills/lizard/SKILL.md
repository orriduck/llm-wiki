---
name: lizard
description: 每日收工时运行，从今天所有 Claude 会话中蒸馏可复用的知识点，自动整理为原子笔记写入 wiki。适合在工作日结束时调用。
user-invocable: true
allowed-tools: "Bash Read Write Glob Grep"
argument-hint: "[topic-filter]"
---

# Lizard — 每日知识蒸馏

你是一个知识蒸馏专家。你的任务是：读取今天所有 Claude 会话的内容，提取其中有价值的、可复用的知识点，整理为符合 llm-wiki 规范的原子笔记。

## 第一步：检测 wiki 路径并确保 git 就绪

从 `~/.claude/plugins/installed_plugins.json` 自动获取安装路径：

```bash
python3 -c "
import json, os
p = os.path.expanduser('~/.claude/plugins/installed_plugins.json')
data = json.load(open(p))
for key, entries in data.get('plugins', {}).items():
    if 'llm-wiki' in key:
        print(entries[-1]['installPath'])
        break
"
```

将输出记为 `WIKI_PATH`，后续所有步骤都使用此路径。

若找不到，告知用户重新安装插件，然后停止。

确保 git 仓库已初始化：

```bash
if [ ! -d "<WIKI_PATH>/.git" ]; then
  cd "<WIKI_PATH>" && git init && git remote add origin https://github.com/orriduck/llm-wiki.git && git fetch origin && git checkout -b main && git reset --mixed origin/main
fi
```

## 第二步：获取今日会话内容

运行以下命令提取今天所有 Claude 会话中的对话文本（跳过工具调用的噪音，只保留 human/assistant 消息）：

```bash
python3 -c "
import json, glob, os
from datetime import date

today = date.today().isoformat()
results = []
pattern = os.path.expanduser('~/.claude/projects/**/*.jsonl')
files = [f for f in glob.glob(pattern, recursive=True) if '/subagents/' not in f]

for f in sorted(files):
    try:
        mdate = date.fromtimestamp(os.path.getmtime(f)).isoformat()
        if mdate != today:
            continue
        lines = open(f, encoding='utf-8', errors='ignore').readlines()
        session_msgs = []
        for line in lines:
            try:
                e = json.loads(line)
                msg = e.get('message', {})
                if not isinstance(msg, dict):
                    continue
                role = msg.get('role', '')
                content = msg.get('content', '')
                text = ''
                if isinstance(content, str):
                    text = content
                elif isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get('type') == 'text':
                            text += block.get('text', '')
                if role in ('user', 'assistant') and text.strip():
                    session_msgs.append(f'[{role}] {text[:800]}')
            except:
                pass
        if session_msgs:
            rel = os.path.relpath(f, os.path.expanduser('~'))
            results.append(f'=== 会话文件: ~/{rel} ===')
            results.extend(session_msgs[:60])
    except:
        pass

if results:
    print('\n'.join(results))
else:
    print('今日暂无 Claude 会话记录。')
"
```

若没有找到任何会话，告知用户并停止。

## 第三步：分析知识点

仔细阅读上述会话内容。你需要：

1. **识别知识点**：找出其中涉及的技术概念、工具用法、最佳实践、踩坑经验、决策依据等。过滤掉纯粹的个人私务、临时性指令、重复的闲聊。
2. **去重归并**：同一个主题的多处提及合并为一个知识点。
3. **评估价值**：只保留有复用价值的内容（"如何配置 X"、"Y 的工作原理"、"Z 的踩坑"等）。

若用户传入了 `$ARGUMENTS`（topic-filter），只处理与该主题相关的知识点。

## 第四步：读取现有 wiki 索引

```bash
cat "<WIKI_PATH>/index.md"
```

对于每个知识点，判断：
- 是否已有对应的 wiki 页面？
- 现有页面是否需要补充/更新？

## 第五步：写入原子笔记

对于每个知识点：

**若需新建页面**：在 `<WIKI_PATH>/wiki/` 创建新 markdown 文件。

文件命名规则：英文 kebab-case，如 `docker-multi-stage-build.md`。

页面格式：
```markdown
# 页面标题（中文）

> 来源：通过 lizard 从 Claude 会话蒸馏 · YYYY-MM-DD

## 核心概念

...

## 关键细节

...

## 相关链接

- [[相关页面]]
```

**若需更新现有页面**：读取页面后在合适的位置追加或修改内容，保持风格一致。

所有内容必须用**中文**编写（文件名和代码片段除外）。

## 第六步：更新 index.md 和 log.md

**index.md**：在对应分类下追加新页面条目，格式：
```
- [[页面名]] — 一句话摘要
```

**log.md**：在文件开头追加一条日志：
```
## [YYYY-MM-DD] lizard | 蒸馏今日 N 个会话，新增 X 页，更新 Y 页
```

## 第七步：自动 commit 并 push

笔记写入完成后：

```bash
cd "<WIKI_PATH>" && git add wiki/ index.md log.md skills/ && git status --short
```

若有变更，commit 并 push：

```bash
cd "<WIKI_PATH>" && \
  git commit -m "lizard: $(date +%Y-%m-%d) 蒸馏 N 个会话，新增 X 页，更新 Y 页" && \
  git push origin main
```

将 commit message 中的 N/X/Y 替换为实际数字。

若 push 失败，告知用户运行 `/llm-wiki:setup`。

## 完成后

简要汇报：新建了哪些页面、更新了哪些页面，以及有哪些知识点因内容不够充实而未单独建页（可以提示用户后续补充）。
