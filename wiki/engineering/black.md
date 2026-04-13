# black

> 不妥协的 Python 代码格式化工具（"The Uncompromising Code Formatter"），通过消除格式讨论、强制统一风格来提升代码审查效率。

## 安装

```bash
# pip
pip install black

# Poetry（添加到 dev 组）
poetry add -D black

# uv
uv add --dev black

# pipx（全局安装，推荐）
pipx install black
```

验证安装：

```bash
black --version
```

---

## 基本用法

### 格式化文件/目录

```bash
# 格式化单个文件
black my_file.py

# 格式化整个目录（递归）
black src/

# 格式化当前目录
black .

# 格式化多个目标
black src/ tests/ scripts/
```

### 检查模式（不修改文件）

```bash
# 检查是否需要格式化（退出码 1 = 需要格式化）
black --check .

# 查看差异（不修改文件）
black --diff .

# 检查 + 差异
black --check --diff .
```

在 CI/CD 中使用 `--check` 来验证代码已格式化：

```bash
black --check . || exit 1
```

### 其他用法

```bash
# 格式化字符串代码（直接传入代码）
black --code "x=1+2"

# 从 stdin 读取
echo "x=1+2" | black -

# 详细输出（显示被跳过的文件）
black --verbose .

# 静默模式
black --quiet .
```

---

## 配置（`pyproject.toml` 中的 `[tool.black]`）

black 自动从格式化目标的公共父目录向上搜索 `pyproject.toml`，找到后读取 `[tool.black]` 节。

```toml
[tool.black]
# 每行最大字符数（默认 88）
line-length = 88

# 目标 Python 版本（影响语法特性判断）
target-version = ["py310", "py311", "py312"]

# 要包含的文件正则（默认匹配 .py 和 .pyi）
include = '\.pyi?$'

# 额外排除的文件/目录（正则，在默认排除基础上叠加）
extend-exclude = '''
(
    ^/migrations/.*
    | .*_pb2\.py
    | .*_generated\.py
)
'''

# 跳过字符串引号标准化（保留原始引号）
skip-string-normalization = false

# 跳过 magic trailing comma 行为（见下方说明）
skip-magic-trailing-comma = false
```

### 默认已排除的目录

black 默认跳过：`.git`、`.hg`、`.mypy_cache`、`.tox`、`.venv`、`_build`、`buck-out`、`build`、`dist`。

### 常用配置示例

```toml
[tool.black]
line-length = 100           # 宽屏项目可调大
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

## 关键行为说明

### Magic Trailing Comma

black 默认将**末尾逗号**视为"强制展开"信号，即：

```python
# 有末尾逗号 → black 保持每行一个元素（不合并）
x = [
    1,
    2,
    3,    # ← 末尾逗号
]

# 没有末尾逗号 → black 可能合并为一行
x = [1, 2, 3]
```

这个行为叫 **magic trailing comma**。使用 `--skip-magic-trailing-comma` 或配置 `skip-magic-trailing-comma = true` 可关闭。

### 字符串引号

black 默认将所有字符串统一改为**双引号**：

```python
# 格式化前
name = 'Alice'
msg = "Hello"

# 格式化后（black 统一为双引号）
name = "Alice"
msg = "Hello"
```

如果字符串内部包含双引号，black 会智能保留单引号以避免转义：

```python
msg = 'He said "hello"'    # 保留单引号，避免 \"
```

使用 `--skip-string-normalization` 或配置 `skip-string-normalization = true` 保留原始引号。

### 行长度默认 88

black 选择 88（而非传统的 79/80）是经过分析后的工程折衷，减少了约 10% 的换行，同时保持可读性。

---

## 与 isort 集成

black 和 isort 各自格式化代码，但对 import 语句的处理有冲突。解决方案是让 isort 使用 black 兼容模式：

```toml
# pyproject.toml
[tool.isort]
profile = "black"
```

这会使 isort 的输出与 black 兼容（使用相同的行长和样式）。详见 [[isort]]。

执行顺序：**先运行 black，再运行 isort**（或使用 `profile = "black"` 让两者输出一致，顺序无关）。

---

## pre-commit Hook 配置

在项目根目录创建 `.pre-commit-config.yaml`：

```yaml
repos:
  - repo: https://github.com/psf/black-pre-commit-mirror
    rev: 25.1.0     # 使用最新版本号
    hooks:
      - id: black
        language_version: python3.11
```

安装 hooks：

```bash
pip install pre-commit
pre-commit install        # 安装到 .git/hooks/pre-commit
pre-commit run --all-files  # 手动对所有文件运行一次
```

每次 `git commit` 前 black 会自动运行，如果有修改则提交被拦截（需要重新 `git add` 后再提交）。

### 与 isort 一起配置

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

## 常见问题

### Q: black 改了我的代码，但逻辑没变？

black 保证格式化前后的 AST（抽象语法树）等价。它只做纯格式变化，不修改逻辑。可用 `--fast` 跳过 AST 校验（不推荐）。

### Q: 如何跳过某段代码的格式化？

```python
# fmt: off
my_matrix = [
    1, 0, 0,
    0, 1, 0,
    0, 0, 1,
]
# fmt: on
```

或对整个文件跳过（在文件顶部）：

```python
# fmt: off
```

### Q: black 与 flake8/pylint 的关系？

black 只做**格式化**，不做代码质量检查。flake8/pylint 做 linting（风格检查、逻辑错误）。两者互补，通常同时使用。需要注意 flake8 的 E501（行长度）设置要与 black 一致：

```ini
# setup.cfg 或 .flake8
[flake8]
max-line-length = 88
extend-ignore = E203, W503
```

---

*最后更新：2026-04-13*
