# Metaflow Pre-Run Lifecycle & FlowMutator / Metaflow Pre-Run 生命周期与 FlowMutator

> Source: Distilled from Claude sessions via lizard · 2026-04-20
> 来源：通过 lizard 从 Claude 会话蒸馏 · 2026-04-20

## Overview / 概述

When `python flow.py run` is invoked, Metaflow goes through several phases **before** any step code executes. Understanding these phases is critical for building custom pre-run checks (static analysis, lint rules) or flow transformations.

当执行 `python flow.py run` 时，Metaflow 在任何 step 代码执行**之前**会经历多个阶段。理解这些阶段对构建自定义 pre-run 检查（静态分析、lint 规则）或流变换至关重要。

## Pre-Run Phase Sequence / Pre-Run 阶段序列

```
1. Flow class loaded & parsed
   流类加载与解析

2. _process_config_decorators()          ← PHASE 1
   ├─ Config values resolved / Config 值解析
   ├─ FlowMutator.pre_mutate()          ← 可增删参数和装饰器
   └─ Graph re-calculated / 图重新计算

3. CLI parsed (--with flags, etc.)
   CLI 解析（--with 标志等）

4. FlowMutator.mutate()                 ← PHASE 2：参数/装饰器只读，可修改 steps
   Graph re-calculated again / 图再次重新计算

5. _check()                             ← PHASE 3：图 lint + Pylint
   ├─ lint.linter.run_checks(graph)     ← 18 项结构检查（无环性、step 名称等）
   └─ PyLint(fname).run()               ← Python 语法检查
```

Source: `metaflow/flowspec.py` (`_process_config_decorators`, `_check` methods)

来源：`metaflow/flowspec.py`（`_process_config_decorators`、`_check` 方法）

## FlowMutator Basics / FlowMutator 基础

FlowMutator is a decorator that implements `pre_mutate()` and/or `mutate()` to transform flows before execution.

FlowMutator 是一个装饰器，实现 `pre_mutate()` 和/或 `mutate()` 来在执行前变换流。

### Key Properties / 关键特性

| Property / 特性 | Detail / 详情 |
|---|---|
| **Independent execution / 独立执行** | Each mutator gets a **fresh `MutableFlow` wrapper** — no shared state between invocations / 每个 mutator 获得**全新 `MutableFlow` 包装器**——调用之间无共享状态 |
| **Sequential ordering / 顺序执行** | Mutators run in `cls._flow_state[FlowStateItems.FLOW_MUTATORS]` order / 按 `_flow_state` 中注册顺序执行 |
| **`pre_mutate` capabilities / pre_mutate 能力** | Can add/remove parameters and decorators / 可增删参数和装饰器 |
| **`mutate` capabilities / mutate 能力** | Parameters/decorators are read-only; can only modify step code / 参数和装饰器只读；只能修改 step 代码 |

Source: `flowspec.py:407-428` loop:

```python
for deco in cls._flow_state[FlowStateItems.FLOW_MUTATORS]:
    mutable_flow = MutableFlow(cls, pre_mutate=True, ...)
    deco.pre_mutate(mutable_flow)
```

### What's Accessible Inside `pre_mutate` / `pre_mutate` 内可访问的内容

| What / 可访问内容 | How / 访问方式 | Example / 示例 |
|---|---|---|
| Concrete flow class / 具体流类 | `mutable_flow._flow_cls` | `CostReportingFlow` |
| Flow source file / 流源文件 | `inspect.getfile(mutable_flow._flow_cls)` | `flows/cost_reporting/flow.py` |
| Step functions / Step 函数 | `mutable_flow.steps` → yields `(name, MutableStep)` | `start`, `process`, `end` |
| Step source code / Step 源代码 | `inspect.getsource(step_func)` | Each step body / 每个 step 的函数体 |
| Flow module / 流模块 | `sys.modules[flow_cls.__module__]` | Everything imported / 所有已导入内容 |
| Filesystem / 文件系统 | Standard `pathlib`/`os` | Any file on disk / 磁盘上的任意文件 |

## Using FlowMutator for Static Analysis / 使用 FlowMutator 进行静态分析

A powerful pattern is using `pre_mutate()` as a **read-only static analysis hook** that raises on violations, rather than actually mutating the flow.

一个强大的模式是将 `pre_mutate()` 用作**只读静态分析钩子**，在违规时抛出异常，而不实际变换流。

### Example: No-Print-Statements Check / 示例：禁止 print 语句检查

```python
class FlowPreRunChecks(FlowMutator):
    """Read-only mutator that runs static analysis checks."""

    def pre_mutate(self, mutable_flow):
        flow_cls = mutable_flow._flow_cls
        source_file = inspect.getfile(flow_cls)
        tree = ast.parse(Path(source_file).read_text())

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "print":
                    raise FlowCheckViolation(
                        f"print() found at line {node.lineno}"
                    )
```

### Why This Doesn't Conflict / 为什么不会冲突

Existing mutators **modify** the flow (e.g., `project_tag_decorator` adds decorators via `add_decorator()`). A read-only check mutator coexists safely because:
1. Each mutator gets a fresh `MutableFlow` — no interference
2. Read-only mutators don't alter `MutableFlow` state
3. Ordering doesn't matter when the mutator only inspects

现有 mutator **修改**流（如 `project_tag_decorator` 通过 `add_decorator()` 添加装饰器）。只读检查 mutator 可安全共存：
1. 每个 mutator 获得全新 `MutableFlow`——无干扰
2. 只读 mutator 不改变 `MutableFlow` 状态
3. 当 mutator 只做检查时，顺序无关紧要

## Related Pages / 相关页面

- [[Metaflow工作流框架]] — Core concepts and decorators / 核心概念与装饰器
- [[Metaflow-打包文件选择机制]] — How packaging determines file scope / 打包如何决定文件范围
- [[Outerbounds-部署与调度]] — `@project` decorator and production deployment / `@project` 装饰器与生产部署
