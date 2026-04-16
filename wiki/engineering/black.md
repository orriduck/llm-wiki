# black

> The uncompromising Python code formatter that eliminates style debates and enforces a unified style to improve code review efficiency.

> 不妥协的 Python 代码格式化工具（"The Uncompromising Code Formatter"），通过消除格式讨论、强制统一风格来提升代码审查效率。

## Installation / 安装

```bash
# pip
pip install black

# Poetry (add to dev group) / Poetry（添加到 dev 组）
poetry add -D black

# uv
uv add --dev black

# pipx (global install, recommended) / pipx（全局安装，推荐）
pipx install black
```

Verify installation / 验证安装：

```bash
black --version
```

---

## Basic usage / 基本用法

### Format files/directories / 格式化文件/目录

```bash
# Format a single file / 格式化单个文件
black my_file.py

# Format an entire directory (recursive) / 格式化整个目录（递归）
black src/

# Format current directory / 格式化当前目录
black .

# Format multiple targets / 格式化多个目标
black src/ tests/ scripts/
```

### Check mode (don't modify files) / 检查模式（不修改文件）

```bash
# Check if formatting is needed (exit code 1 = needs formatting)
# 检查是否需要格式化（退出码 1 = 需要格式化）
black --check .

# View diff (don't modify files) / 查看差异（不修改文件）
black --diff .

# Check + diff / 检查 + 差异
black --check --diff .
```

Use `--check` in CI/CD to verify code is formatted:

> 在 CI/CD 中使用 `--check` 来验证代码已格式化：

```bash
black --check . || exit 1
```

### Other usage / 其他用法

```bash
# Format a code string (pass code directly) / 格式化字符串代码（直接传入代码）
black --code "x=1+2"

# Read from stdin / 从 stdin 读取
echo "x=1+2" | black -

# Verbose output (show skipped files) / 详细输出（显示被跳过的文件）
black --verbose .

# Quiet mode / 静默模式
black --quiet .
```

---

## Configuration (`[tool.black]` in `pyproject.toml`) / 配置（`pyproject.toml` 中的 `[tool.black]`）

black automatically searches upward from the common parent directory of the formatting targets for `pyproject.toml` and reads the `[tool.black]` section.

> black 自动从格式化目标的公共父目录向上搜索 `pyproject.toml`，找到后读取 `[tool.black]` 节。

```toml
[tool.black]
# Max characters per line (default 88) / 每行最大字符数（默认 88）
line-length = 88

# Target Python version (affects syntax feature detection)
# 目标 Python 版本（影响语法特性判断）
target-version = ["py310", "py311", "py312"]

# File include regex (default matches .py and .pyi)
# 要包含的文件正则（默认匹配 .py 和 .pyi）
include = '\.pyi?$'

# Additional exclude files/dirs (regex, stacked on top of defaults)
# 额外排除的文件/目录（正则，在默认排除基础上叠加）
extend-exclude = '''
(
    ^/migrations/.*
    | .*_pb2\.py
    | .*_generated\.py
)
'''

# Skip string quote normalization (keep original quotes)
# 跳过字符串引号标准化（保留原始引号）
skip-string-normalization = false

# Skip magic trailing comma behavior (see explanation below)
# 跳过 magic trailing comma 行为（见下方说明）
skip-magic-trailing-comma = false
```

### Default excluded directories / 默认已排除的目录

black skips by default: `.git`, `.hg`, `.mypy_cache`, `.tox`, `.venv`, `_build`, `buck-out`, `build`, `dist`.

> black 默认跳过：`.git`、`.hg`、`.mypy_cache`、`.tox`、`.venv`、`_build`、`buck-out`、`build`、`dist`。

### Common configuration example / 常用配置示例

```toml
[tool.black]
line-length = 100           # Widescreen projects can increase this / 宽屏项目可调大
target-version = ["py311"]
extend-exclude = '''
(
    migrations/
    | \.eggs
    | \.git
)
'''
```

---

## Key behavior explained / 关键行为说明

### Magic Trailing Comma

black treats a **trailing comma** as a "force expand" signal by default:

> black 默认将**末尾逗号**视为"强制展开"信号，即：

```python
# Has trailing comma -> black keeps one element per line (no merging)
# 有末尾逗号 → black 保持每行一个元素（不合并）
x = [
    1,
    2,
    3,    # <- trailing comma / 末尾逗号
]

# No trailing comma -> black may merge into one line
# 没有末尾逗号 → black 可能合并为一行
x = [1, 2, 3]
```

This behavior is called **magic trailing comma**. Use `--skip-magic-trailing-comma` or set `skip-magic-trailing-comma = true` to disable it.

> 这个行为叫 **magic trailing comma**。使用 `--skip-magic-trailing-comma` 或配置 `skip-magic-trailing-comma = true` 可关闭。

### String quotes / 字符串引号

black normalizes all strings to **double quotes** by default:

> black 默认将所有字符串统一改为**双引号**：

```python
# Before formatting / 格式化前
name = 'Alice'
msg = "Hello"

# After formatting (black unifies to double quotes)
# 格式化后（black 统一为双引号）
name = "Alice"
msg = "Hello"
```

If a string contains double quotes internally, black intelligently keeps single quotes to avoid escaping:

> 如果字符串内部包含双引号，black 会智能保留单引号以避免转义：

```python
msg = 'He said "hello"'    # Keep single quotes to avoid \" / 保留单引号，避免 \"
```

Use `--skip-string-normalization` or set `skip-string-normalization = true` to keep original quotes.

> 使用 `--skip-string-normalization` 或配置 `skip-string-normalization = true` 保留原始引号。

### Default line length of 88 / 行长度默认 88

black chose 88 (instead of the traditional 79/80) as an engineering compromise after analysis, reducing line wraps by about 10% while maintaining readability.

> black 选择 88（而非传统的 79/80）是经过分析后的工程折衷，减少了约 10% 的换行，同时保持可读性。

---

## Integration with isort / 与 isort 集成

black and isort each format code, but have conflicting import statement handling. The solution is to have isort use black-compatible mode:

> black 和 isort 各自格式化代码，但对 import 语句的处理有冲突。解决方案是让 isort 使用 black 兼容模式：

```toml
# pyproject.toml
[tool.isort]
profile = "black"
```

This makes isort's output compatible with black (using the same line length and style). See [[isort]] for details.

> 这会使 isort 的输出与 black 兼容（使用相同的行长和样式）。详见 [[isort]]。

Execution order: **run black first, then isort** (or use `profile = "black"` to make both outputs consistent, making order irrelevant).

> 执行顺序：**先运行 black，再运行 isort**（或使用 `profile = "black"` 让两者输出一致，顺序无关）。

---

## pre-commit Hook configuration / pre-commit Hook 配置

Create `.pre-commit-config.yaml` in the project root:

> 在项目根目录创建 `.pre-commit-config.yaml`：

```yaml
repos:
  - repo: https://github.com/psf/black-pre-commit-mirror
    rev: 25.1.0     # Use latest version / 使用最新版本号
    hooks:
      - id: black
        language_version: python3.11
```

Install hooks / 安装 hooks：

```bash
pip install pre-commit
pre-commit install        # Install to .git/hooks/pre-commit / 安装到 .git/hooks/pre-commit
pre-commit run --all-files  # Manually run on all files / 手动对所有文件运行一次
```

black automatically runs before each `git commit`; if changes are made, the commit is blocked (you need to `git add` again before committing).

> 每次 `git commit` 前 black 会自动运行，如果有修改则提交被拦截（需要重新 `git add` 后再提交）。

### Configuration with isort / 与 isort 一起配置

```yaml
repos:
  - repo: https://github.com/psf/black-pre-commit-mirror
    rev: 25.1.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/PyCQA/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black"]
```

---

## FAQ / 常见问题

### Q: black changed my code but the logic didn't change? / Q: black 改了我的代码，但逻辑没变？

black guarantees AST (abstract syntax tree) equivalence before and after formatting. It only makes pure formatting changes without modifying logic. Use `--fast` to skip AST verification (not recommended).

> black 保证格式化前后的 AST（抽象语法树）等价。它只做纯格式变化，不修改逻辑。可用 `--fast` 跳过 AST 校验（不推荐）。

### Q: How to skip formatting for a specific code block? / Q: 如何跳过某段代码的格式化？

```python
# fmt: off
my_matrix = [
    1, 0, 0,
    0, 1, 0,
    0, 0, 1,
]
# fmt: on
```

Or skip an entire file (at the top of the file) / 或对整个文件跳过（在文件顶部）：

```python
# fmt: off
```

### Q: What is the relationship between black and flake8/pylint? / Q: black 与 flake8/pylint 的关系？

black only does **formatting**, not code quality checks. flake8/pylint do linting (style checks, logic errors). They are complementary and typically used together. Note that flake8's E501 (line length) setting should match black:

> black 只做**格式化**，不做代码质量检查。flake8/pylint 做 linting（风格检查、逻辑错误）。两者互补，通常同时使用。需要注意 flake8 的 E501（行长度）设置要与 black 一致：

```ini
# setup.cfg or .flake8 / setup.cfg 或 .flake8
[flake8]
max-line-length = 88
extend-ignore = E203, W503
```

---

*Last updated: 2026-04-13 / 最后更新：2026-04-13*
