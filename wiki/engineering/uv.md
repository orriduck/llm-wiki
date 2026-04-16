# uv — Fast Python Package Manager / uv — 极速 Python 包管理器

uv is an extremely fast Python package and project manager written in Rust by Astral. It claims to be 10-100x faster than pip and can replace pip, pip-tools, pipx, poetry, pyenv, virtualenv, and more.

> uv 是 Astral 出品、用 Rust 编写的极速 Python 包管理器，号称比 pip 快 10-100 倍，可替代 pip、pip-tools、pipx、poetry、pyenv、virtualenv 等多个工具。

## Installation / 安装

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows PowerShell
irm https://astral.sh/uv/install.ps1 | iex

# via pip
pip install uv

# via Homebrew (macOS)
brew install uv
```

Verify installation:

> 验证安装：

```bash
uv --version
uv self update    # self-update
```

---

## Project Initialization: `uv init` / 项目初始化：`uv init`

```bash
# create a project in a new directory
uv init my-project
cd my-project

# initialize in the current directory
uv init

# create a library (lib) project (without main.py)
uv init --lib my-lib

# specify Python version
uv init --python 3.12 my-project
```

`uv init` automatically generates:

> `uv init` 自动生成：

```
my-project/
  .python-version    # specifies Python version
  .gitignore
  README.md
  main.py            # example entry file
  pyproject.toml
```

Initial `pyproject.toml` structure:

> 初始 `pyproject.toml` 结构：

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.12"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

---

## Dependency Management Commands / 依赖管理命令

### `uv add` — Add Dependencies / 添加依赖

```bash
uv add requests                          # add runtime dependency
uv add "requests>=2.28"                 # specify version constraint
uv add --dev pytest black isort         # add dev dependencies
uv add --optional mysql mysqlclient     # add optional dependency (extras)

uv add "git+https://github.com/example/repo"   # Git source
uv add ./local-package                           # local path (editable)

uv add requests --frozen                 # don't update lockfile (only update pyproject.toml)
```

Dev dependencies are written to the `[dependency-groups]` section of `pyproject.toml`:

> 开发依赖会写入 `pyproject.toml` 的 `[dependency-groups]` 节：

```toml
[dependency-groups]
dev = [
    "pytest>=7.0",
    "black>=24.0",
]
```

### `uv remove` — Remove Dependencies / 移除依赖

```bash
uv remove requests
uv remove --dev pytest
```

### `uv sync` — Sync Environment / 同步环境

Fully synchronizes the virtual environment with `uv.lock` (installs missing, uninstalls extra).

> 将虚拟环境与 `uv.lock` 完全同步（安装缺少的，卸载多余的）。

```bash
uv sync                                  # sync all dependencies (including dev)
uv sync --no-dev                         # install only runtime dependencies (production)
uv sync --only-dev                       # install only dev dependencies
uv sync --group lint                     # include specified dependency group
uv sync --frozen                         # don't update lockfile, install strictly from existing lockfile
uv sync --no-install-project             # don't install the project itself
```

### `uv lock` — Lock Dependencies / 锁定依赖

```bash
uv lock                                  # generate/update uv.lock
uv lock --upgrade                        # upgrade all dependencies to latest compatible versions
uv lock --upgrade-package requests       # upgrade only a specific package
uv lock --check                          # check if lockfile is up to date
```

### `uv pip` — pip-compatible Interface / 兼容 pip 的接口

```bash
uv pip install requests                  # equivalent to pip install
uv pip install -r requirements.txt
uv pip list
uv pip freeze
uv pip compile requirements.in           # equivalent to pip-compile
```

---

## uv Configuration in `pyproject.toml` / `pyproject.toml` 中 uv 的配置方式

```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.28",
    "pydantic>=2.0",
]

# dev dependency groups
[dependency-groups]
dev = ["pytest>=7.0", "black", "mypy"]
lint = ["ruff", "isort"]

# uv-specific configuration
[tool.uv]
# specify Python version (higher priority than .python-version)
python = "3.12"

# custom package sources
[[tool.uv.index]]
name = "private"
url = "https://pypi.example.com/simple"   # replace with your private index URL
priority = "primary"    # first / primary / supplemental / default

# packages to install in editable mode
[tool.uv.sources]
my-lib = { path = "../my-lib", editable = true }
# or workspace member
other-pkg = { workspace = true }

# extra constraints (limit versions without directly depending on them)
constraint-dependencies = ["numpy<2.0"]

# override specific package versions (force a specific version)
override-dependencies = ["urllib3==1.26.18"]
```

---

## Virtual Environment Management: `uv venv` / 虚拟环境管理：`uv venv`

```bash
# create .venv in the project directory (uv sync creates it automatically)
uv venv

# specify Python version
uv venv --python 3.11

# specify path
uv venv /path/to/my-env

# activate virtual environment
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate          # Windows
```

uv manages `.venv` automatically; manual creation is rarely needed.

> uv 会自动管理 `.venv`，大多数情况下不需要手动创建。

---

## `uv run` — Run Scripts / Tools / `uv run` — 运行脚本/工具

`uv run` automatically syncs the environment before running to ensure dependencies are current.

> `uv run` 在运行前自动同步环境，确保依赖最新。

```bash
# run a Python file
uv run main.py

# run an installed tool
uv run pytest tests/
uv run black .
uv run mypy src/

# temporarily add dependencies at runtime (without modifying pyproject.toml)
uv run --with httpx python -c "import httpx; print(httpx.__version__)"

# run a single-file script (with inline dependency declaration)
uv run script.py
```

### Inline Dependencies for Single-File Scripts (PEP 723) / 单文件脚本的内联依赖（PEP 723）

```python
# script.py
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests", "rich"]
# ///

import requests
from rich import print

resp = requests.get("https://httpbin.org/json")
print(resp.json())
```

```bash
uv run script.py    # automatically installs requests and rich, then runs
```

---

## `uv tool` — Global Tool Management / 全局工具管理

```bash
# run a tool temporarily (no installation, uses isolated environment)
uvx black .
uvx ruff check .
uvx mypy src/

# install global tools (added to PATH)
uv tool install black
uv tool install mypy
uv tool install ruff

# run a specific version
uvx black@24.3.0 .
uvx --from 'black==24.3.0' black .

# run with extra dependencies
uvx --with mkdocs-material mkdocs build

# list installed tools
uv tool list

# upgrade tools
uv tool upgrade black
uv tool upgrade --all

# uninstall tools
uv tool uninstall black
```

---

## Workspace Support / Workspace 支持

Suitable for monorepos — multiple Python packages sharing a single `uv.lock`.

> 适合 monorepo，多个 Python 包共享一个 `uv.lock`。

### Root `pyproject.toml` / 根目录 `pyproject.toml`

```toml
[tool.uv.workspace]
members = ["packages/*"]
exclude = ["packages/experimental"]
```

### Inter-package Dependencies / 成员间互相依赖

```toml
# packages/app/pyproject.toml
[project]
name = "app"
dependencies = ["shared-utils"]

[tool.uv.sources]
shared-utils = { workspace = true }
```

### Workspace Directory Structure / workspace 目录结构

```
monorepo/
  pyproject.toml        # workspace root (defines members)
  uv.lock               # shared lockfile
  packages/
    app/
      pyproject.toml
      src/
    shared-utils/
      pyproject.toml
      src/
```

---

## Speed / Feature Comparison with Poetry / 与 Poetry 的速度/功能对比

| Feature | Poetry | uv |
|---------|--------|----|
| Language | Python | Rust |
| Install speed | Slow (seconds) | Extremely fast (milliseconds, 10-100x faster) |
| Dependency resolution | Custom resolver | Custom PubGrub resolver |
| Python version management | Not supported | Built-in (`uv python install`) |
| Lockfile | `poetry.lock` (Poetry-specific) | `uv.lock` (cross-platform) |
| Workspace (monorepo) | Not supported | Native support |
| PyPI publishing | Built-in | via `uv build` + `uv publish` |
| pip-compatible interface | None | `uv pip` |
| Global tool management | None (needs pipx) | `uv tool` / `uvx` |
| Single-file script dependencies | None | Supports PEP 723 |
| pre-commit integration | Moderate | Good (uvx is fast) |
| Config standard | Mixed (`tool.poetry` + `project`) | Standard PEP 621 |
| Maturity | High (since 2018) | Newer (since 2024, rapidly evolving) |

---

## Migrating a Poetry Project to uv / 迁移 Poetry 项目到 uv

### Steps / 步骤

**1. Install uv / 安装 uv**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**2. Migrate `pyproject.toml` / 迁移 `pyproject.toml`**

Poetry dependency syntax must be migrated to the standard `[project]` section:

> Poetry 的依赖写法需迁移到标准 `[project]` 节：

```toml
# Poetry old style
[tool.poetry.dependencies]
python = "^3.10"
requests = "^2.28"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0"

# After migration (uv / PEP 621 standard)
[project]
requires-python = ">=3.10"
dependencies = ["requests>=2.28"]

[dependency-groups]
dev = ["pytest>=7.0"]

[build-system]
requires = ["hatchling"]    # or "flit-core", "setuptools"
build-backend = "hatchling.build"
```

**3. Migrate lockfile from `poetry.lock` / 从 `poetry.lock` 迁移 lockfile**

```bash
# delete poetry.lock and let uv regenerate
rm poetry.lock
uv lock        # generate uv.lock
uv sync        # install all dependencies
```

**4. Replace common commands / 替换常用命令**

| Poetry | uv |
|--------|----|
| `poetry install` | `uv sync` |
| `poetry add requests` | `uv add requests` |
| `poetry add -D pytest` | `uv add --dev pytest` |
| `poetry remove requests` | `uv remove requests` |
| `poetry update` | `uv lock --upgrade` |
| `poetry run pytest` | `uv run pytest` |
| `poetry shell` | `source .venv/bin/activate` |
| `poetry build` | `uv build` |
| `poetry publish` | `uv publish` |

**5. Update CI/CD configuration / 更新 CI/CD 配置**

```yaml
# GitHub Actions example
- name: Install uv
  uses: astral-sh/setup-uv@v4

- name: Install dependencies
  run: uv sync --frozen

- name: Run tests
  run: uv run pytest
```

---

*最后更新：2026-04-16*
