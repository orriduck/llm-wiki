# black + uv

> Integrating and using the black code formatter in uv-managed Python projects.

> 在 uv 管理的 Python 项目中集成和使用 black 代码格式化工具。

## Add black as a dev dependency / 添加 black 为开发依赖

```bash
# Add to dev dependency group / 添加到 dev 依赖组
uv add --dev black

# Add both black and isort / 同时添加 black 和 isort
uv add --dev black isort
```

After execution, `pyproject.toml` is automatically updated:

> 执行后 `pyproject.toml` 会自动更新：

```toml
[dependency-groups]
dev = [
    "black>=25.0",
    "isort>=5.13",
]
```

---

## Run black with `uv run` / 用 `uv run` 运行 black

`uv run` automatically syncs the environment before running, ensuring black is installed.

> `uv run` 在运行前自动同步环境，确保 black 已安装。

```bash
# Format current directory / 格式化当前目录
uv run black .

# Format specific directories / 格式化特定目录
uv run black src/ tests/

# Check mode (for CI/CD) / 检查模式（CI/CD 中使用）
uv run black --check .

# View diff / 查看差异
uv run black --diff .
```

---

## Run with `uvx` without installation / 用 `uvx` 无需安装直接运行

`uvx` runs black in a temporary isolated environment without adding it as a project dependency, suitable for one-off use or quick trials.

> `uvx` 在临时隔离环境中运行 black，无需将其添加为项目依赖，适合一次性使用或快速试用。

```bash
# Run directly (auto-downloads latest version) / 直接运行（自动下载最新版）
uvx black .

# Specify version / 指定版本
uvx black@25.1.0 .

# Check mode / 检查模式
uvx black --check src/

# Format and view diff / 格式化并查看差异
uvx black --diff .
```

`uvx` is equivalent to `uv tool run`:

> `uvx` 与 `uv tool run` 等价：

```bash
uv tool run black .    # Same as uvx black . / 等同于 uvx black .
```

---

## Configure uv scripts to call black in `pyproject.toml` / 在 `pyproject.toml` 中配置 uv scripts 调用 black

You can define aliases for common commands via `[tool.uv.scripts]` (or in `[project.scripts]` for tasks) (requires uv 0.5+ `tool.uv.scripts` or use `justfile` / `Makefile` directly).

> 通过 `[tool.uv.scripts]`（或在 `[project.scripts]` 中定义任务）可以为常用命令定义别名（需 uv 0.5+ 的 `tool.uv.scripts` 或直接使用 `justfile` / `Makefile`）。

A more common approach is to configure black in `pyproject.toml`:

> 更通用的做法是在 `pyproject.toml` 中配置 black：

```toml
[tool.black]
line-length = 88
target-version = ["py311", "py312"]
extend-exclude = '''
(
    migrations/
    | .*_pb2\.py
)
'''
```

Then `uv run black .` will read this configuration.

> 然后用 `uv run black .` 即可读取该配置。

### Using Makefile to wrap commands / 使用 Makefile 封装命令

```makefile
# Makefile
.PHONY: format lint check

format:
	uv run black .
	uv run isort .

lint:
	uv run ruff check .
	uv run mypy src/

check:
	uv run black --check .
	uv run isort --check-only .
```

---

## pre-commit with uv / pre-commit 中与 uv 配合

### Method 1: Use standard pre-commit mirror (recommended) / 方式一：使用标准 pre-commit 镜像（推荐）

pre-commit has its own environment management, independent of the uv virtual environment:

> pre-commit 有独立的环境管理，不依赖 uv 虚拟环境：

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black-pre-commit-mirror
    rev: 25.1.0
    hooks:
      - id: black
        language_version: python3.11
```

```bash
uv add --dev pre-commit
uv run pre-commit install
uv run pre-commit run --all-files
```

### Method 2: Use `uvx` to call black (local hook) / 方式二：使用 `uvx` 调用 black（local hook）

Delegate the hook to `uvx`, so pre-commit doesn't need to manage the black environment:

> 将 hook 委托给 `uvx` 运行，无需 pre-commit 自己管理 black 环境：

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: black
        name: black
        language: system
        entry: uvx black
        types: [python]
        args: []
```

### Method 3: black from the project environment / 方式三：project 环境中的 black

If black is already a project dev dependency, you can reference it directly:

> 如果 black 已在项目 dev 依赖中，可以直接引用：

```yaml
repos:
  - repo: local
    hooks:
      - id: black
        name: black
        language: system
        entry: uv run black
        types: [python]
        pass_filenames: true
```

---

## Complete `pyproject.toml` example / 完整 `pyproject.toml` 示例

```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["requests>=2.28"]

[dependency-groups]
dev = [
    "black>=25.0",
    "isort>=5.13",
    "pytest>=7.0",
    "mypy>=1.0",
    "pre-commit>=3.0",
]

[tool.black]
line-length = 88
target-version = ["py311", "py312"]
skip-string-normalization = false

[tool.isort]
profile = "black"
line_length = 88

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

---

## Quick reference / 快速参考

| Scenario / 场景 | Command / 命令 |
|------|------|
| Install black to project / 安装 black 到项目 | `uv add --dev black` |
| Format code / 格式化代码 | `uv run black .` |
| CI format check / CI 检查格式 | `uv run black --check .` |
| Run without installing / 不安装直接运行 | `uvx black .` |
| Run specific version / 指定版本运行 | `uvx black@25.1.0 .` |
| Install pre-commit / 安装 pre-commit | `uv add --dev pre-commit` |
| Run all hooks / 运行所有 hooks | `uv run pre-commit run --all-files` |

---

*Last updated: 2026-04-13 / 最后更新：2026-04-13*
