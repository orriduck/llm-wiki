# Metaflow Packaging & File Selection / Metaflow 打包文件选择机制

> Source: Distilled from Claude sessions via lizard · 2026-04-20
> 来源：通过 lizard 从 Claude 会话蒸馏 · 2026-04-20

## Overview / 概述

When running remotely, Metaflow packages user code into a tarball sent to the execution environment. Understanding which files get packaged is critical for debugging remote execution failures and for scoping static analysis checks.

远程运行时，Metaflow 将用户代码打包成 tarball 发送到执行环境。理解哪些文件被打包对于调试远程执行失败和确定静态分析检查范围至关重要。

You can inspect the package contents with:
可以通过以下命令查看打包内容：

```bash
python flows/your_flow/flow.py package list
```

## Two Categories of Packaged Files / 打包文件的两个类别

### 1. User Code / 用户代码

Source: `package/__init__.py:633-655` (`_user_code_tuples()`)

```python
flowdir = os.path.dirname(os.path.abspath(sys.argv[0])) + "/"
walk(flowdir, file_filter=suffix_filter, exclude_tl_dirs=...)
```

This walks **the directory containing the flow file**. For `flows/cost_reporting/flow.py`, it packages everything under `flows/cost_reporting/`.

这会遍历**包含流文件的目录**。对于 `flows/cost_reporting/flow.py`，它会打包 `flows/cost_reporting/` 下的所有内容。

### 2. Module Content / 模块内容

Source: `packaging_sys/v1.py:40-82` (`MetaflowCodeContentV1`)

The module selector (`package/__init__.py:74-93`) includes modules tracked via `FlowMutatorMeta._import_modules` — a set populated when FlowMutator subclasses are imported. This captures:

模块选择器包括通过 `FlowMutatorMeta._import_modules` 跟踪的模块——这是一个在 FlowMutator 子类被导入时填充的集合。这会捕获：

- The module where the FlowMutator class was defined / FlowMutator 类定义所在的模块
- Dependencies imported by those modules / 这些模块导入的依赖

`MetaflowCodeContentV1` resolves module names to file paths using distribution metadata and `sys.modules`.

`MetaflowCodeContentV1` 使用 distribution 元数据和 `sys.modules` 将模块名解析为文件路径。

## Scanning Scope Comparison / 扫描范围对比

| Approach / 方案 | Coverage / 覆盖范围 | Implementation Difficulty / 实现难度 | Matches `package list` / 与打包一致性 |
|---|---|---|---|
| **Flow file only / 只扫流文件** | `flows/cost_reporting/flow.py` | Lowest / 最低 — `inspect.getfile()` + AST | Partial — only entry file / 部分——仅入口文件 |
| **Flow directory / 流所在目录** | `flows/cost_reporting/*.py` | Low / 低 — `os.walk()` + AST | Matches user code portion / 等同 user code 部分 |
| **Directory + `_import_modules`** | Directory + `whoop_outerbounds/**/*.py` | Medium / 中 — manual module name resolution / 需手动解析模块名 | Close — edge cases with namespace packages / 接近一致 |
| **`MetaflowCodeContentV1`** | Full package scope / 完整打包范围 | Medium / 中 — uses metaflow internal class / 用 metaflow 内部类 | Exact match / 完全一致 |

## Using `MetaflowCodeContentV1` at `pre_mutate` Time / 在 `pre_mutate` 时使用 `MetaflowCodeContentV1`

**Don't use `MetaflowPackage`** directly — it requires a flow **instance**, an `environment` object, and an `echo` callback. At `pre_mutate` time you only have the flow **class**.

**不要直接使用 `MetaflowPackage`**——它需要流的**实例**、`environment` 对象和 `echo` 回调。在 `pre_mutate` 时你只有流的**类**。

**Use `MetaflowCodeContentV1` instead** — it only needs a `criteria` callback and operates entirely on `sys.modules`. All modules are already imported at `pre_mutate` time:

**改用 `MetaflowCodeContentV1`**——它只需要一个 `criteria` 回调，完全基于 `sys.modules` 操作。在 `pre_mutate` 时所有模块已经导入：

```python
from metaflow.packaging_sys.v1 import MetaflowCodeContentV1
from metaflow.package import MetaflowPackage

content = MetaflowCodeContentV1(
    criteria=MetaflowPackage._get_module_criteria()
)
# content._files_from_modules contains resolved file paths
```

Note: This pulls in metaflow internals and does distribution resolution work that may be overkill for simple checks. For matching Metaflow's existing pylint scope (single flow file), `inspect.getfile()` is sufficient.

注意：这会引入 metaflow 内部类并执行 distribution 解析工作，对于简单检查可能过重。若只需匹配 Metaflow 现有 pylint 范围（单个流文件），`inspect.getfile()` 即可。

## Related Pages / 相关页面

- [[Metaflow-PreRun生命周期与FlowMutator]] — Pre-run phases and FlowMutator pattern / Pre-run 阶段与 FlowMutator 模式
- [[Metaflow工作流框架]] — Core concepts / 核心概念
- [[Outerbounds-依赖管理]] — Dependency packaging for remote execution / 远程执行的依赖打包
