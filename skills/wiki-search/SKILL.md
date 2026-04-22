---
name: wiki-search
description: 在 llm-wiki 中搜索相关内容
user-invocable: true
allowed-tools: "Bash Read Glob Grep"
argument-hint: "<搜索关键词>"
---

# Wiki 搜索

## 第一步：检测 wiki 路径

```bash
python3 scripts/wiki_path.py
```

## 第二步：执行搜索

```bash
python3 scripts/wiki_search.py "$ARGUMENTS"
```

## 第三步：整理结果

基于搜索结果，读取最相关页面并总结。

若无结果，提示用户创建新知识（lizard / lizard-eat）。
