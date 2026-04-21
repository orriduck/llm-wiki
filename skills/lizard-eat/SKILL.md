---
name: lizard-eat
description: 给定一个 URL 和主题，自动抓取页面内容，整理为详尽的 wiki 原子笔记（附原始来源引用）。比 lizard 更详细，因为有完整参考资料。
user-invocable: true
allowed-tools: "Bash Read Write WebFetch Glob Grep"
argument-hint: "<url> <topic>"
---

# Lizard Eat — 外部资料摄取

你是一个知识整理专家。给定一个 URL 和主题，抓取原始资料，整理为符合 llm-wiki 规范的详尽原子笔记。

`$ARGUMENTS` 格式为：`<url> <topic>`，例如：
```
https://docs.example.com/feature  Kubernetes Operator 模式
```

## 第一步：解析参数

从 `$ARGUMENTS` 中提取：
- `URL`：第一个空格前的内容（以 `http` 开头）
- `TOPIC`：剩余部分（主题描述）

若缺少 URL 或 TOPIC，告知用户正确格式并停止。

## 第二步：检测 wiki 路径

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

将输出记为 `WIKI_PATH`。若找不到，告知用户重新安装插件并停止。

## 第三步：抓取 URL 内容

使用 WebFetch 工具获取 URL 的完整内容。若页面有多个子页面/分页，优先抓取主页面；若内容过长，聚焦与 TOPIC 最相关的部分。

若抓取失败，告知用户并停止。

## 第四步：读取现有 wiki 索引

```bash
cat "<WIKI_PATH>/index.md"
```

判断：
- 是否已有与 TOPIC 高度重叠的页面？若有，读取该页面内容，准备追加/更新而非新建。
- 该主题应归属哪个分类目录（`engineering/`、`aws/`、`metaflow/`、`ai-agents/`、`iac/`、`career/` 等）？若不属于任何现有分类，建议新建合适的子目录。

## 第五步：整理原子笔记

根据抓取内容和 TOPIC，拆分为一个或多个原子笔记。拆分原则：
- 每个笔记聚焦**一个**概念/工具/模式，可独立阅读
- 若内容涉及多个独立子主题，拆为多页（如"安装"+"配置"+"踩坑"可拆可合，视内容量决定）
- 内容要**详尽**：有原始资料作为参考，应包含完整的参数说明、示例代码、边界情况，不能像 lizard 那样只写摘要

**页面格式：**

```markdown
# 页面标题（中文）

> 来源：[原始文档标题或描述](<URL>) · 通过 lizard-eat 整理 · YYYY-MM-DD

## 核心概念

...（概念定义、适用场景、与相似工具的对比）

## 安装 / 快速开始

...（若适用）

## 关键配置 / 参数

...（完整参数表、示例）

## 常见用法 / 示例

```代码示例```

## 踩坑 / 注意事项

...（官方文档中的警告、已知限制、版本差异）

## 相关链接

- [原始文档](<URL>)
- [[相关 wiki 页面]]
```

所有内容用**中文**编写，文件名用英文 kebab-case。

## 第六步：写入文件

将笔记写入 `<WIKI_PATH>/wiki/<分类>/` 目录。若分类目录不存在，先创建：

```bash
mkdir -p "<WIKI_PATH>/wiki/<分类>/"
```

## 第七步：更新 index.md 和 log.md

**index.md**：在对应分类下追加新页面条目（若更新现有页面则修改摘要）：
```
- [[页面名]] — 一句话摘要
```

**log.md**：在文件开头追加：
```
## [YYYY-MM-DD] lizard-eat | 摄取 <URL>，新增 X 页，更新 Y 页
```

## 第八步：自动 commit 并 push

```bash
cd "<WIKI_PATH>" && git add wiki/ index.md log.md && git status --short
```

若有变更：

```bash
cd "<WIKI_PATH>" && \
  git commit -m "lizard-eat: <TOPIC> (来源: <URL 域名>)" && \
  git push origin main
```

若 push 失败，告知用户。

## 完成后

汇报：
- 新建/更新了哪些页面
- 哪些内容因过于细节或不具复用价值而略去
- 原始来源 URL
