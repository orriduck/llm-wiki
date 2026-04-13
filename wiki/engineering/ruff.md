# ruff

> 用 Rust 编写的极速 Python linter 和格式化工具，可完全替代 black + isort + flake8 及多个插件，速度比同类工具快 10-100 倍。

## ruff 是什么

ruff 是 Astral 团队用 Rust 开发的 Python 代码质量工具，单一二进制文件同时承担：

- **格式化**（`ruff format`）：black 的直接替代，>99.9% 行为兼容
- **Import 排序**（`ruff check --select I`）：isort 的直接替代
- **Linting**（`ruff check`）：实现了 Flake8、flake8-bugbear、pyupgrade、pep8-naming 等 800+ 条规则

核心优势：比 black/flake8 快 10-100 倍；单工具替代多工具；深度集成，无需协调多个配置文件。

---

## 安装

```bash
# pip 安装到项目
pip install ruff

# uv 添加为开发依赖（推荐）
uv add --dev ruff

# uvx 无需安装直接运行（临时使用 / CI 快速检查）
uvx ruff check .
uvx ruff format .
```

pyproject.toml 自动更新：

```toml
[dependency-groups]
dev = [
    "ruff>=0.9",
]
```

---

## `ruff format`：格式化（替代 black）

### 基本用法

```bash
# 格式化当前目录
ruff format .

# 格式化指定路径
ruff format src/ tests/

# 检查模式（不修改文件，用于 CI）
ruff format --check .

# 预览差异（不修改文件）
ruff format --diff .

# 通过 uv run
uv run ruff format .

# 通过 uvx（无需安装）
uvx ruff format .
```

### 与 black 的行为差异

| 特性 | black | ruff format |
|------|-------|-------------|
| 整体兼容性 | — | >99.9% 行兼容 |
| f-string 内部格式化 | 不格式化 | **格式化** f-string `{}` 内表达式 |
| docstring 代码块格式化 | 不支持 | **支持**（需开启 `docstring-code-format`） |
| 方法链换行（preview） | 与自身相同风格 | 提供 fluent layout 可选风格 |
| 引号风格 | 仅双引号 | 可配置单/双引号 |
| 缩进 | 仅空格 | 可配置空格或 Tab |

### 与 black 的已知不兼容规则

启用以下 lint 规则会与 `ruff format` 冲突，**建议禁用**：

```toml
[tool.ruff.lint]
ignore = [
    "Q000", "Q001", "Q002", "Q003",  # 引号相关
    "COM812", "COM819",               # 尾随逗号相关
    "W191",                           # Tab 缩进
]
```

---

## `ruff check --select I`：Import 排序（替代 isort）

### 基本用法

```bash
# 检查 import 排序问题
ruff check --select I .

# 自动修复（等价于 isort .）
ruff check --select I --fix .

# 通过 uv run
uv run ruff check --select I --fix .

# 通过 uvx
uvx ruff check --select I --fix .
```

### 与 isort 的行为对比

| 特性 | isort | ruff（I 规则） |
|------|-------|----------------|
| 分组顺序 | stdlib → third-party → first-party | 相同 |
| black 兼容模式 | `profile = "black"` | 默认兼容 |
| `# isort: skip` 注释 | 支持 | **支持**（向后兼容） |
| `# isort: off/on` 注释 | 支持 | **支持** |
| 速度 | Python | Rust，快约 100 倍 |
| 独立配置段 | `[tool.isort]` | `[tool.ruff.lint.isort]` |

在 `pyproject.toml` 中配置 isort 行为：

```toml
[tool.ruff.lint.isort]
known-first-party = ["my_package"]
known-third-party = ["requests", "pydantic"]
force-sort-within-sections = false
split-on-trailing-comma = true
```

---

## `ruff check`：Linting

### 基本用法

```bash
# 检查当前目录
ruff check .

# 自动修复可修复的问题
ruff check --fix .

# 应用不安全修复（谨慎使用）
ruff check --fix --unsafe-fixes .

# 监听模式（开发时）
ruff check --watch .

# 输出指定规则的说明
ruff rule E501
```

### 常用规则集

| 前缀 | 来源 | 说明 |
|------|------|------|
| `E` / `W` | pycodestyle | PEP 8 风格检查（缩进、空格、行长） |
| `F` | Pyflakes | 未使用变量/import、未定义名称 |
| `I` | isort | import 排序 |
| `UP` | pyupgrade | 建议使用更新的 Python 语法 |
| `B` | flake8-bugbear | 常见 bug 和设计问题（如可变默认参数） |
| `N` | pep8-naming | 命名规范（类名、函数名等） |
| `D` | pydocstyle | docstring 格式规范 |
| `S` | flake8-bandit | 安全漏洞检测 |
| `C4` | flake8-comprehensions | 列表/字典推导式优化 |
| `SIM` | flake8-simplify | 代码简化建议 |
| `PTH` | flake8-use-pathlib | 建议用 pathlib 替代 os.path |
| `PL` | Pylint | 代码规范、错误、重构建议 |
| `RUF` | Ruff 专有 | Ruff 特有规则 |

### 推荐的起始规则集

```toml
[tool.ruff.lint]
# 保守起步（适合大多数项目）
select = ["E4", "E7", "E9", "F", "I"]

# 较积极（适合新项目）
select = ["E", "W", "F", "I", "UP", "B", "SIM"]

# 宽泛启用后逐步忽略（高级）
select = ["ALL"]
ignore = ["D", "ANN", "COM812"]
```

---

## `pyproject.toml` 完整配置示例

```toml
[tool.ruff]
# 目标 Python 版本
target-version = "py311"

# 行长（与 black 默认保持一致）
line-length = 88
indent-width = 4

# 排除目录（ruff 已有合理默认值，按需覆盖）
exclude = [
    ".git",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "migrations",   # Django 等自动生成文件
]

[tool.ruff.lint]
# 启用的规则集
select = ["E", "W", "F", "I", "UP", "B", "SIM"]

# 忽略的具体规则
ignore = [
    "E501",    # 行长（由 formatter 控制）
    "B008",    # 函数调用作为默认参数（FastAPI 常见模式）
    "COM812",  # 与 formatter 冲突
]

# 所有可修复规则都自动修复
fixable = ["ALL"]
unfixable = []

# 按文件路径忽略规则
[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101"]   # 测试文件允许 assert
"__init__.py" = ["F401"]     # __init__.py 允许未使用 import

# isort 配置
[tool.ruff.lint.isort]
known-first-party = ["my_package"]
split-on-trailing-comma = true

[tool.ruff.format]
# 引号风格（double 与 black 一致）
quote-style = "double"

# 缩进风格
indent-style = "space"

# 不跳过 magic trailing comma（与 black 一致）
skip-magic-trailing-comma = false

# 换行符
line-ending = "auto"

# 格式化 docstring 中的代码块（可选）
docstring-code-format = true
docstring-code-line-length = "dynamic"
```

---

## 内联忽略注释

```python
# 忽略单行的某条规则
import os  # noqa: F401

# 忽略单行的多条规则
x = 1  # noqa: E501, W291

# 忽略单行所有规则
some_line = "very long..."  # noqa

# 文件级忽略（放在文件任意位置）
# ruff: noqa
# ruff: noqa: F401

# 代码块级别忽略
# ruff: disable: E501
very_long_line = "..."
# ruff: enable: E501

# 格式化忽略（类似 black）
# fmt: off
matrix = [
    1, 0,
    0, 1,
]
# fmt: on

# 单行跳过格式化
x = {   'key': 'value'   }  # fmt: skip
```

---

## pre-commit Hook 配置

ruff 官方提供 `astral-sh/ruff-pre-commit` 仓库：

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0   # 替换为最新版本
    hooks:
      # lint 并自动修复（放在 format 之前）
      - id: ruff
        args: [--fix]
      # 格式化
      - id: ruff-format
```

排除 Jupyter Notebook（仅处理 .py 和 .pyi）：

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

安装与运行：

```bash
uv add --dev pre-commit
uv run pre-commit install
uv run pre-commit run --all-files
```

---

## uvx 无需安装直接运行

```bash
# 格式化
uvx ruff format .

# lint 检查
uvx ruff check .

# lint 并自动修复
uvx ruff check --fix .

# import 排序修复
uvx ruff check --select I --fix .

# 指定版本
uvx ruff@0.9.0 check .
```

适合 CI、一次性检查、或不想污染项目依赖的场景。

---

## 从 black + isort 迁移

ruff 可**完全替代** black + isort 组合，无需保留原有工具。

### 迁移步骤

**第一步**：安装 ruff，移除旧工具

```bash
uv add --dev ruff
uv remove black isort  # 如有
```

**第二步**：更新 `pyproject.toml`

```toml
# 删除旧配置
# [tool.black]
# [tool.isort]

# 添加 ruff 配置
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I"]

[tool.ruff.format]
quote-style = "double"
```

**第三步**：首次格式化整个代码库

```bash
# 先修复 import 排序
ruff check --select I --fix .

# 再格式化
ruff format .
```

**第四步**：更新 pre-commit 配置，替换 black 和 isort hook 为 ruff hook（见上方）。

### 能否完全替代？

| 场景 | 结论 |
|------|------|
| black 格式化 | 完全替代（>99.9% 兼容） |
| isort import 排序 | 完全替代 |
| flake8 基础规则（E/W/F） | 完全替代 |
| flake8 插件（bugbear、bandit 等） | 大部分替代（select 对应规则前缀） |
| mypy / pyright 类型检查 | **不替代**（ruff 无类型检查功能） |
| pylint 全部规则 | 部分替代（PL 前缀覆盖常用规则） |

---

*最后更新：2026-04-13*
