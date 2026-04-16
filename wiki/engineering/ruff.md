# ruff

> An ultra-fast Python linter and formatter written in Rust that can fully replace black + isort + flake8 and multiple plugins, 10-100x faster than comparable tools.

> 用 Rust 编写的极速 Python linter 和格式化工具，可完全替代 black + isort + flake8 及多个插件，速度比同类工具快 10-100 倍。

## What is ruff / ruff 是什么

ruff is a Python code quality tool developed in Rust by the Astral team. A single binary handles:

> ruff 是 Astral 团队用 Rust 开发的 Python 代码质量工具，单一二进制文件同时承担：

- **Formatting** (`ruff format`): A direct replacement for black, >99.9% behavior compatible

> **格式化**（`ruff format`）：black 的直接替代，>99.9% 行为兼容

- **Import sorting** (`ruff check --select I`): A direct replacement for isort

> **Import 排序**（`ruff check --select I`）：isort 的直接替代

- **Linting** (`ruff check`): Implements 800+ rules from Flake8, flake8-bugbear, pyupgrade, pep8-naming, etc.

> **Linting**（`ruff check`）：实现了 Flake8、flake8-bugbear、pyupgrade、pep8-naming 等 800+ 条规则

Core advantages: 10-100x faster than black/flake8; single tool replaces multiple tools; deep integration, no need to coordinate multiple config files.

> 核心优势：比 black/flake8 快 10-100 倍；单工具替代多工具；深度集成，无需协调多个配置文件。

---

## Installation / 安装

```bash
# pip install to project / pip 安装到项目
pip install ruff

# uv add as dev dependency (recommended) / uv 添加为开发依赖（推荐）
uv add --dev ruff

# uvx run without installing (temporary use / CI quick check)
# uvx 无需安装直接运行（临时使用 / CI 快速检查）
uvx ruff check .
uvx ruff format .
```

pyproject.toml auto-updates / pyproject.toml 自动更新：

```toml
[dependency-groups]
dev = [
    "ruff>=0.9",
]
```

---

## `ruff format`: Formatting (replaces black) / 格式化（替代 black）

### Basic usage / 基本用法

```bash
# Format current directory / 格式化当前目录
ruff format .

# Format specific paths / 格式化指定路径
ruff format src/ tests/

# Check mode (don't modify files, for CI) / 检查模式（不修改文件，用于 CI）
ruff format --check .

# Preview diff (don't modify files) / 预览差异（不修改文件）
ruff format --diff .

# Via uv run / 通过 uv run
uv run ruff format .

# Via uvx (no install needed) / 通过 uvx（无需安装）
uvx ruff format .
```

### Behavior differences from black / 与 black 的行为差异

| Feature / 特性 | black | ruff format |
|------|-------|-------------|
| Overall compatibility / 整体兼容性 | -- | >99.9% line compatible / >99.9% 行兼容 |
| f-string internal formatting / f-string 内部格式化 | Not formatted / 不格式化 | **Formats** expressions inside f-string `{}` / **格式化** f-string `{}` 内表达式 |
| Docstring code block formatting / docstring 代码块格式化 | Not supported / 不支持 | **Supported** (enable `docstring-code-format`) / **支持**（需开启） |
| Method chain wrapping (preview) / 方法链换行（preview） | Same style / 与自身相同风格 | Optional fluent layout style / 提供 fluent layout 可选风格 |
| Quote style / 引号风格 | Double quotes only / 仅双引号 | Configurable single/double / 可配置单/双引号 |
| Indentation / 缩进 | Spaces only / 仅空格 | Configurable spaces or tabs / 可配置空格或 Tab |

### Known incompatible rules with black / 与 black 的已知不兼容规则

Enabling these lint rules will conflict with `ruff format` -- **recommend disabling**:

> 启用以下 lint 规则会与 `ruff format` 冲突，**建议禁用**：

```toml
[tool.ruff.lint]
ignore = [
    "Q000", "Q001", "Q002", "Q003",  # Quote-related / 引号相关
    "COM812", "COM819",               # Trailing comma related / 尾随逗号相关
    "W191",                           # Tab indentation / Tab 缩进
]
```

---

## `ruff check --select I`: Import sorting (replaces isort) / Import 排序（替代 isort）

### Basic usage / 基本用法

```bash
# Check import sorting issues / 检查 import 排序问题
ruff check --select I .

# Auto-fix (equivalent to isort .) / 自动修复（等价于 isort .）
ruff check --select I --fix .

# Via uv run / 通过 uv run
uv run ruff check --select I --fix .

# Via uvx / 通过 uvx
uvx ruff check --select I --fix .
```

### Behavior comparison with isort / 与 isort 的行为对比

| Feature / 特性 | isort | ruff (I rules / I 规则) |
|------|-------|----------------|
| Group order / 分组顺序 | stdlib -> third-party -> first-party | Same / 相同 |
| black compatible mode / black 兼容模式 | `profile = "black"` | Compatible by default / 默认兼容 |
| `# isort: skip` comments / 注释 | Supported / 支持 | **Supported** (backward compatible) / **支持**（向后兼容） |
| `# isort: off/on` comments / 注释 | Supported / 支持 | **Supported / 支持** |
| Speed / 速度 | Python | Rust, ~100x faster / Rust，快约 100 倍 |
| Config section / 独立配置段 | `[tool.isort]` | `[tool.ruff.lint.isort]` |

Configure isort behavior in `pyproject.toml`:

> 在 `pyproject.toml` 中配置 isort 行为：

```toml
[tool.ruff.lint.isort]
known-first-party = ["my_package"]
known-third-party = ["requests", "pydantic"]
force-sort-within-sections = false
split-on-trailing-comma = true
```

---

## `ruff check`: Linting

### Basic usage / 基本用法

```bash
# Check current directory / 检查当前目录
ruff check .

# Auto-fix fixable issues / 自动修复可修复的问题
ruff check --fix .

# Apply unsafe fixes (use with caution) / 应用不安全修复（谨慎使用）
ruff check --fix --unsafe-fixes .

# Watch mode (during development) / 监听模式（开发时）
ruff check --watch .

# Output explanation for a specific rule / 输出指定规则的说明
ruff rule E501
```

### Common rule sets / 常用规则集

| Prefix / 前缀 | Source / 来源 | Description / 说明 |
|------|------|------|
| `E` / `W` | pycodestyle | PEP 8 style checks (indentation, spacing, line length) / PEP 8 风格检查（缩进、空格、行长） |
| `F` | Pyflakes | Unused variables/imports, undefined names / 未使用变量/import、未定义名称 |
| `I` | isort | Import sorting / import 排序 |
| `UP` | pyupgrade | Suggest newer Python syntax / 建议使用更新的 Python 语法 |
| `B` | flake8-bugbear | Common bugs and design issues (e.g. mutable default args) / 常见 bug 和设计问题（如可变默认参数） |
| `N` | pep8-naming | Naming conventions (class names, function names, etc.) / 命名规范（类名、函数名等） |
| `D` | pydocstyle | Docstring format standards / docstring 格式规范 |
| `S` | flake8-bandit | Security vulnerability detection / 安全漏洞检测 |
| `C4` | flake8-comprehensions | List/dict comprehension optimization / 列表/字典推导式优化 |
| `SIM` | flake8-simplify | Code simplification suggestions / 代码简化建议 |
| `PTH` | flake8-use-pathlib | Suggest pathlib over os.path / 建议用 pathlib 替代 os.path |
| `PL` | Pylint | Code standards, errors, refactoring suggestions / 代码规范、错误、重构建议 |
| `RUF` | Ruff-specific / Ruff 专有 | Ruff-exclusive rules / Ruff 特有规则 |

### Recommended starting rule sets / 推荐的起始规则集

```toml
[tool.ruff.lint]
# Conservative start (suitable for most projects)
# 保守起步（适合大多数项目）
select = ["E4", "E7", "E9", "F", "I"]

# More aggressive (suitable for new projects)
# 较积极（适合新项目）
select = ["E", "W", "F", "I", "UP", "B", "SIM"]

# Broad enable then gradually ignore (advanced)
# 宽泛启用后逐步忽略（高级）
select = ["ALL"]
ignore = ["D", "ANN", "COM812"]
```

---

## Complete `pyproject.toml` configuration example / `pyproject.toml` 完整配置示例

```toml
[tool.ruff]
# Target Python version / 目标 Python 版本
target-version = "py311"

# Line length (consistent with black default) / 行长（与 black 默认保持一致）
line-length = 88
indent-width = 4

# Excluded directories (ruff has sensible defaults, override as needed)
# 排除目录（ruff 已有合理默认值，按需覆盖）
exclude = [
    ".git",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "migrations",   # Django etc. auto-generated files / Django 等自动生成文件
]

[tool.ruff.lint]
# Enabled rule sets / 启用的规则集
select = ["E", "W", "F", "I", "UP", "B", "SIM"]

# Ignored specific rules / 忽略的具体规则
ignore = [
    "E501",    # Line length (controlled by formatter) / 行长（由 formatter 控制）
    "B008",    # Function call as default arg (common FastAPI pattern) / 函数调用作为默认参数（FastAPI 常见模式）
    "COM812",  # Conflicts with formatter / 与 formatter 冲突
]

# All fixable rules auto-fix / 所有可修复规则都自动修复
fixable = ["ALL"]
unfixable = []

# Ignore rules per file path / 按文件路径忽略规则
[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101"]   # Allow assert in test files / 测试文件允许 assert
"__init__.py" = ["F401"]     # Allow unused imports in __init__.py / __init__.py 允许未使用 import

# isort configuration / isort 配置
[tool.ruff.lint.isort]
known-first-party = ["my_package"]
split-on-trailing-comma = true

[tool.ruff.format]
# Quote style (double matches black) / 引号风格（double 与 black 一致）
quote-style = "double"

# Indent style / 缩进风格
indent-style = "space"

# Don't skip magic trailing comma (matches black) / 不跳过 magic trailing comma（与 black 一致）
skip-magic-trailing-comma = false

# Line ending / 换行符
line-ending = "auto"

# Format code blocks in docstrings (optional) / 格式化 docstring 中的代码块（可选）
docstring-code-format = true
docstring-code-line-length = "dynamic"
```

---

## Inline ignore comments / 内联忽略注释

```python
# Ignore a specific rule on a single line / 忽略单行的某条规则
import os  # noqa: F401

# Ignore multiple rules on a single line / 忽略单行的多条规则
x = 1  # noqa: E501, W291

# Ignore all rules on a single line / 忽略单行所有规则
some_line = "very long..."  # noqa

# File-level ignore (anywhere in the file) / 文件级忽略（放在文件任意位置）
# ruff: noqa
# ruff: noqa: F401

# Block-level ignore / 代码块级别忽略
# ruff: disable: E501
very_long_line = "..."
# ruff: enable: E501

# Format ignore (similar to black) / 格式化忽略（类似 black）
# fmt: off
matrix = [
    1, 0,
    0, 1,
]
# fmt: on

# Single-line skip formatting / 单行跳过格式化
x = {   'key': 'value'   }  # fmt: skip
```

---

## pre-commit Hook configuration / pre-commit Hook 配置

ruff officially provides the `astral-sh/ruff-pre-commit` repository:

> ruff 官方提供 `astral-sh/ruff-pre-commit` 仓库：

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0   # Replace with latest version / 替换为最新版本
    hooks:
      # Lint and auto-fix (before format) / lint 并自动修复（放在 format 之前）
      - id: ruff
        args: [--fix]
      # Format / 格式化
      - id: ruff-format
```

Exclude Jupyter Notebooks (only process .py and .pyi):

> 排除 Jupyter Notebook（仅处理 .py 和 .pyi）：

```yaml
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks:
      - id: ruff
        types_or: [python, pyi]
        args: [--fix]
      - id: ruff-format
        types_or: [python, pyi]
```

Install and run / 安装与运行：

```bash
uv add --dev pre-commit
uv run pre-commit install
uv run pre-commit run --all-files
```

---

## uvx run without installation / uvx 无需安装直接运行

```bash
# Format / 格式化
uvx ruff format .

# Lint check / lint 检查
uvx ruff check .

# Lint and auto-fix / lint 并自动修复
uvx ruff check --fix .

# Import sorting fix / import 排序修复
uvx ruff check --select I --fix .

# Specify version / 指定版本
uvx ruff@0.9.0 check .
```

Suitable for CI, one-off checks, or scenarios where you don't want to pollute project dependencies.

> 适合 CI、一次性检查、或不想污染项目依赖的场景。

---

## Migrating from black + isort / 从 black + isort 迁移

ruff can **fully replace** the black + isort combination; there's no need to keep the original tools.

> ruff 可**完全替代** black + isort 组合，无需保留原有工具。

### Migration steps / 迁移步骤

**Step 1**: Install ruff, remove old tools / 安装 ruff，移除旧工具

```bash
uv add --dev ruff
uv remove black isort  # If present / 如有
```

**Step 2**: Update `pyproject.toml` / 更新 `pyproject.toml`

```toml
# Remove old config / 删除旧配置
# [tool.black]
# [tool.isort]

# Add ruff config / 添加 ruff 配置
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I"]

[tool.ruff.format]
quote-style = "double"
```

**Step 3**: Format the entire codebase for the first time / 首次格式化整个代码库

```bash
# Fix import sorting first / 先修复 import 排序
ruff check --select I --fix .

# Then format / 再格式化
ruff format .
```

**Step 4**: Update pre-commit config, replace black and isort hooks with ruff hooks (see above).

> 更新 pre-commit 配置，替换 black 和 isort hook 为 ruff hook（见上方）。

### Can it fully replace? / 能否完全替代？

| Scenario / 场景 | Conclusion / 结论 |
|------|------|
| black formatting / black 格式化 | Fully replaces (>99.9% compatible) / 完全替代（>99.9% 兼容） |
| isort import sorting / isort import 排序 | Fully replaces / 完全替代 |
| flake8 basic rules (E/W/F) / flake8 基础规则 | Fully replaces / 完全替代 |
| flake8 plugins (bugbear, bandit, etc.) / flake8 插件 | Mostly replaces (select corresponding rule prefixes) / 大部分替代（select 对应规则前缀） |
| mypy / pyright type checking / 类型检查 | **Does not replace** (ruff has no type checking) / **不替代**（ruff 无类型检查功能） |
| pylint all rules / pylint 全部规则 | Partially replaces (PL prefix covers common rules) / 部分替代（PL 前缀覆盖常用规则） |

---

*Last updated: 2026-04-13 / 最后更新：2026-04-13*
