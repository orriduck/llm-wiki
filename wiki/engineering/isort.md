# isort

> A Python import statement auto-sorting tool that organizes imports by standard library, third-party, and local packages, keeping code clean and consistent.

> Python import 语句自动排序工具，将 import 按照标准库、第三方库、本地库分组排列，保持代码整洁一致。

## Installation / 安装

```bash
# pip
pip install isort

# Poetry (add to dev group) / Poetry（添加到 dev 组）
poetry add -D isort

# uv
uv add --dev isort

# pipx (global install) / pipx（全局安装）
pipx install isort
```

Verify installation / 验证安装：

```bash
isort --version
```

---

## Basic usage / 基本用法

### Sort import statements / 排序 import 语句

```bash
# Format a single file / 格式化单个文件
isort my_file.py

# Format multiple files / 格式化多个文件
isort file1.py file2.py

# Recursively process current directory / 递归处理当前目录
isort .

# Process specific directories / 处理特定目录
isort src/ tests/
```

### Check mode (don't modify files) / 检查模式（不修改文件）

```bash
# Check if sorting is needed (exit code 1 = needs sorting)
# 检查是否需要排序（退出码 1 = 需要排序）
isort --check-only .
isort -c .          # Short form / 简写

# Show diff (don't modify files) / 显示差异（不修改文件）
isort --diff .

# Check + diff / 检查 + 差异
isort --check-only --diff .
```

### Other options / 其他选项

```bash
# Atomic mode (verify syntax after sorting, rollback on error)
# 原子模式（排序后验证语法，有错则回滚）
isort --atomic .

# Skip a file / 跳过某个文件
isort --skip migrations/

# Show verbose output / 显示详细输出
isort --verbose .

# Quiet mode / 静默模式
isort --quiet .
```

---

## Configuration (`[tool.isort]` in `pyproject.toml`) / 配置（`pyproject.toml` 中的 `[tool.isort]`）

```toml
[tool.isort]
# Use a preset profile (recommended for use with black)
# 使用预设 profile（推荐与 black 配合使用）
profile = "black"

# Max characters per line (default 79, black uses 88)
# 每行最大字符数（默认 79，black 用 88）
line_length = 88

# Known local/first-party modules (auto-identified as FIRSTPARTY)
# 已知的本地/第一方模块（自动识别为 FIRSTPARTY）
known_first_party = ["my_package", "my_lib"]

# Known third-party modules / 已知的第三方模块
known_third_party = ["requests", "pydantic"]

# Multi-line import style (0-11, black profile uses 3)
# 多行 import 样式（0-11，black profile 使用 3）
multi_line_output = 3

# Add trailing comma in parentheses (default on with black profile)
# 在括号末尾添加逗号（black profile 默认开启）
include_trailing_comma = true

# Force grid wrap (even when short enough) / 强制在括号内换行（即使短到不需要）
force_grid_wrap = 0

# Add blank line between import and from...import
# import 和 from...import 之间是否加空行
lines_between_types = 1

# Number of blank lines after imports / 各 section 之间的空行数
lines_after_imports = 2

# Source paths (isort auto-identifies first-party modules)
# 源代码路径（isort 自动识别第一方模块）
src_paths = ["src", "tests"]

# Skip files/directories / 跳过的文件/目录
skip = ["migrations", ".venv"]
extend_skip = [".gitignore"]
skip_glob = ["**/generated/*.py"]

# Alphabetical sort (unified across sections) / 按字母排序（跨 section 统一排序）
force_alphabetical_sort = false

# Combine as imports with regular imports on the same line
# 将 as 导入与普通导入合并在同一行
combine_as_imports = false
```

---

## Black compatible mode (`profile = "black"` is key) / Black 兼容模式（`profile = "black"` 是关键）

isort and black have default conflicts in how they format import statements. The solution:

> isort 与 black 对 import 语句的格式化方式存在默认冲突。解决方案：

```toml
[tool.isort]
profile = "black"
```

`profile = "black"` is equivalent to the following full configuration:

> `profile = "black"` 等价于以下完整配置：

```toml
[tool.isort]
multi_line_output = 3          # Vertical Hanging Indent
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
line_length = 88
```

Formatting comparison / 格式化效果对比：

```python
# isort default output (conflicts with black)
# isort 默认输出（与 black 冲突）
from module import (ClassA,
    ClassB, ClassC)

# profile = "black" output (consistent with black)
# profile = "black" 输出（与 black 一致）
from module import (
    ClassA,
    ClassB,
    ClassC,
)
```

---

## Execution order with black / 与 black 的执行顺序

Two approaches / 两种方案：

**Approach 1: Run black first, then isort (using black profile) / 方案一：先运行 black，再运行 isort（使用 black profile）**

```bash
black .
isort .
```

Recommended to fix this order in Makefile or pre-commit. As long as isort uses `profile = "black"`, the two outputs won't overwrite each other.

> 推荐在 Makefile 或 pre-commit 中固定此顺序。只要 isort 使用 `profile = "black"`，两者输出不会再互相覆盖。

**Approach 2: Run once (order doesn't matter) / 方案二：只运行一次（顺序无关）**

With `profile = "black"` set, isort's output already satisfies black's requirements, and running black afterward won't modify the import section. Therefore order has no effect on the final result.

> 设置 `profile = "black"` 后，isort 的输出已经满足 black 的要求，black 再运行后不会修改 import 部分。因此顺序对最终结果没有影响。

---

## pre-commit Hook configuration / pre-commit Hook 配置

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black-pre-commit-mirror
    rev: 25.1.0
    hooks:
      - id: black

  - repo: https://github.com/PyCQA/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black", "--filter-files"]
```

`--filter-files` makes isort skip files in `.gitignore` (requires git environment).

> `--filter-files` 让 isort 跳过 `.gitignore` 中的文件（需要 git 环境）。

Install and run / 安装并运行：

```bash
pre-commit install
pre-commit run --all-files
```

---

## Common profile comparison / 常用 profile 对比

| Profile | multi_line_output | trailing_comma | Use case / 适用场景 |
|---------|-------------------|----------------|----------|
| `black` | 3 (Hanging Indent) | Yes / 是 | With black (recommended) / 与 black 配合（推荐） |
| `google` | 3 | No / 否 | Google style guide / Google 风格指南 |
| `pycharm` | 5 (Hanging Grid Grouped) | Yes / 是 | PyCharm default / PyCharm 默认 |
| `django` | 5 | No / 否 | Django projects / Django 项目 |
| `attrs` | 3 | Yes / 是 | attrs library style / attrs 库风格 |
| `open_stack` | 5 | Yes / 是 | OpenStack style / OpenStack 风格 |

---

## multi_line_output style reference / multi_line_output 样式速查

| Value / 值 | Name / 名称 | Example / 示例 |
|----|------|------|
| 0 | Grid | `from x import (A, B,` |
| 1 | Vertical | `from x import (A,\n    B,` |
| 2 | Hanging Indent | `from x import (\n    A, B,` |
| 3 | Vertical Hanging Indent | Each import on its own line, trailing comma (used by black) / 每个 import 单独一行，末尾逗号（black 用此） |
| 4 | Balanced Wrapping | Balanced wrapping / 平衡换行 |
| 5 | Hanging Grid Grouped | Grouped wrapping / 分组换行 |

---

## Skip specific imports / 跳过特定导入

```python
import os
import sys  # isort:skip

# Skip entire file (at the top of the file) / 跳过整个文件（文件开头）
# isort:skip_file
```

---

*Last updated: 2026-04-13 / 最后更新：2026-04-13*
