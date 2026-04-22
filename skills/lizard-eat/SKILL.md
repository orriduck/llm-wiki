---
name: lizard-eat
description: 给定一个 URL 和主题，自动抓取页面内容，整理为详尽的 wiki 原子笔记（附原始来源引用）。
user-invocable: true
allowed-tools: "Bash Read Write WebFetch Glob Grep"
argument-hint: "<url> <topic>"
---

# Lizard Eat — 外部资料摄取

## 第一步：解析参数

解析 `$ARGUMENTS` 得到 URL 和 TOPIC。

## 第二步：检测 wiki 路径

```bash
python3 scripts/wiki_path.py
```

将输出记为 `WIKI_PATH`。

## 第三步：抓取 URL 内容

使用 WebFetch 获取页面内容。

## 第四步：读取现有 wiki 索引

```bash
cat "<WIKI_PATH>/index.md"
```

## 第五步：整理原子笔记

遵循 `CLAUDE.md` schema：
- English first, Chinese second
- 去敏感信息
- 强结构化

## 第六步：写入文件

写入 `<WIKI_PATH>/wiki/`。

## 第七步：更新 index.md 和 log.md

## 第八步：commit 并 push

```bash
cd "<WIKI_PATH>" && git add wiki/ index.md log.md scripts/ AGENTS.md && git commit -m "lizard-eat: <TOPIC>" && git push origin main
```

## 完成

输出变更摘要。
