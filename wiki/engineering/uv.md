# uv

> An ultra-fast Python package manager built with Rust by Astral, claimed to be 10-100x faster than pip, capable of replacing pip, pip-tools, pipx, poetry, pyenv, virtualenv, and more.

> Astral 出品、用 Rust 编写的极速 Python 包管理器，号称比 pip 快 10-100 倍，可替代 pip、pip-tools、pipx、poetry、pyenv、virtualenv 等多个工具。

## Installation / 安装

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows PowerShell
irm https://astral.sh/uv/install.ps1 | iex

# Via pip / 通过 pip 安装
pip install uv

# Via Homebrew (macOS) / 通过 Homebrew（macOS）
brew install uv
```

Verify installation / 验证安装：

```bash
uv --version
uv self update    # Self-update / 自我更新
```

---

## Project initialization: `uv init` / 项目初始化：`uv init`

```bash
# Create project in a new directory / 在新目录中创建项目
uv init my-project
cd my-project

# Initialize in current directory / 在当前目录初始化
uv init

# Create a library (lib) project (without main.py)
# 创建库（lib）项目（不带 main.py）
uv init --lib my-lib

# Specify Python version / 指定 Python 版本
uv init --python 3.12 my-project
```

`uv init` auto-generates / `uv init` 自动生成：

```
my-project/
  .python-version    # Specifies Python version / 指定 Python 版本
  .gitignore
  README.md
  main.py            # Example entry file / 示例入口文件
  pyproject.toml
```

Initial `pyproject.toml` structure / 初始 `pyproject.toml` 结构：

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

## Dependency management commands / 依赖管理命令

### `uv add` -- Add dependency / 添加依赖

```bash
uv add requests                          # Add runtime dependency / 添加运行时依赖
uv add "requests>=2.28"                 # Specify version constraint / 指定版本约束
uv add --dev pytest black isort         # Add dev dependencies / 添加开发依赖
uv add --optional mysql mysqlclient     # Add optional dependency (extras) / 添加可选依赖（extras）

uv add "git+https://github.com/user/repo"   # Git source / Git 源
uv add ./local-package                       # Local path (editable) / 本地路径（editable）

uv add requests --frozen                 # Don't update lockfile (only update pyproject.toml) / 不更新 lockfile（只更新 pyproject.toml）
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

### `uv remove` -- Remove dependency / 移除依赖

```bash
uv remove requests
uv remove --dev pytest
```

### `uv sync` -- Sync environment / 同步环境

Fully synchronizes the virtual environment with `uv.lock` (installs missing packages, removes extra ones).

> 将虚拟环境与 `uv.lock` 完全同步（安装缺少的，卸载多余的）。

```bash
uv sync                                  # Sync all dependencies (including dev) / 同步所有依赖（含 dev）
uv sync --no-dev                         # Install only runtime dependencies (production) / 只安装运行时依赖（生产环境）
uv sync --only-dev                       # Install only dev dependencies / 只安装 dev 依赖
uv sync --group lint                     # Include specific dependency group / 包含指定依赖组
uv sync --frozen                         # Don't update lockfile, install strictly from existing lockfile / 不更新 lockfile，严格按现有 lockfile 安装
uv sync --no-install-project             # Don't install the project itself / 不安装项目本身
```

### `uv lock` -- Lock dependencies / 锁定依赖

```bash
uv lock                                  # Generate/update uv.lock / 生成/更新 uv.lock
uv lock --upgrade                        # Upgrade all deps to latest compatible version / 升级所有依赖到最新兼容版本
uv lock --upgrade-package requests       # Upgrade specific package only / 只升级指定包
uv lock --check                          # Check if lockfile is up to date / 检查 lockfile 是否最新
```

### `uv pip` -- pip-compatible interface / 兼容 pip 的接口

```bash
uv pip install requests                  # Equivalent to pip install / 等同 pip install
uv pip install -r requirements.txt
uv pip list
uv pip freeze
uv pip compile requirements.in           # Equivalent to pip-compile / 等同 pip-compile
```

---

## uv configuration in `pyproject.toml` / `pyproject.toml` 中 uv 的配置方式

```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.28",
    "pydantic>=2.0",
]

# Dev dependency groups / 开发依赖组
[dependency-groups]
dev = ["pytest>=7.0", "black", "mypy"]
lint = ["ruff", "isort"]

# uv-specific configuration / uv 专属配置
[tool.uv]
# Specify Python version (higher priority than .python-version)
# 指定 Python 版本（优先级高于 .python-version）
python = "3.12"

# Custom package source / 自定义包源
[[tool.uv.index]]
name = "private"
url = "https://pypi.example.com/simple"
priority = "primary"    # first / primary / supplemental / default

# Editable dev installs / 开发模式安装的包（editable）
[tool.uv.sources]
my-lib = { path = "../my-lib", editable = true }
# Or workspace member / 或 workspace 成员
other-pkg = { workspace = true }

# Extra constraints (not direct deps but limit versions)
# 额外约束（不直接依赖但限制版本）
constraint-dependencies = ["numpy<2.0"]

# Override specific package versions (force a version)
# 覆盖特定包版本（强制使用指定版本）
override-dependencies = ["urllib3==1.26.18"]
```

---

## Virtual environment management: `uv venv` / 虚拟环境管理：`uv venv`

```bash
# Create .venv in project directory (uv sync creates it automatically)
# 在项目目录创建 .venv（uv sync 会自动创建）
uv venv

# Specify Python version / 指定 Python 版本
uv venv --python 3.11

# Specify path / 指定路径
uv venv /path/to/my-env

# Activate virtual environment / 激活虚拟环境
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate          # Windows
```

uv automatically manages `.venv`; in most cases you don't need to create it manually.

> uv 会自动管理 `.venv`，大多数情况下不需要手动创建。

---

## `uv run` -- Run scripts/tools / 运行脚本/工具

`uv run` automatically syncs the environment before running, ensuring dependencies are up to date.

> `uv run` 在运行前自动同步环境，确保依赖最新。

```bash
# Run a Python file / 运行 Python 文件
uv run main.py

# Run installed tools / 运行已安装的工具
uv run pytest tests/
uv run black .
uv run mypy src/

# Temporarily add dependency at runtime (doesn't modify pyproject.toml)
# 运行时临时添加依赖（不修改 pyproject.toml）
uv run --with httpx python -c "import httpx; print(httpx.__version__)"

# Run single-file script (with inline dependency declaration)
# 运行单文件脚本（带内联依赖声明）
uv run script.py
```

### Inline dependencies for single-file scripts (PEP 723) / 单文件脚本的内联依赖（PEP 723）

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
uv run script.py    # Automatically installs requests and rich before running / 自动安装 requests 和 rich 后运行
```

---

## `uv tool` -- Global tool management / 全局工具管理

```bash
# Run tool temporarily (no install, uses isolated environment)
# 临时运行工具（不安装，使用隔离环境）
uvx black .
uvx ruff check .
uvx mypy src/

# Install global tool (added to PATH) / 安装全局工具（添加到 PATH）
uv tool install black
uv tool install mypy
uv tool install ruff

# Run specific version / 运行特定版本
uvx black@24.3.0 .
uvx --from 'black==24.3.0' black .

# Run with extra dependencies / 带额外依赖运行
uvx --with mkdocs-material mkdocs build

# View installed tools / 查看已安装工具
uv tool list

# Upgrade tools / 升级工具
uv tool upgrade black
uv tool upgrade --all

# Uninstall tool / 卸载工具
uv tool uninstall black
```

---

## Workspace support / Workspace 支持

Suitable for monorepos where multiple Python packages share a single `uv.lock`.

> 适合 monorepo，多个 Python 包共享一个 `uv.lock`。

### Root `pyproject.toml` / 根目录 `pyproject.toml`

```toml
[tool.uv.workspace]
members = ["packages/*"]
exclude = ["packages/experimental"]
```

### Inter-member dependencies / 成员间互相依赖

```toml
# packages/app/pyproject.toml
[project]
name = "app"
dependencies = ["shared-utils"]

[tool.uv.sources]
shared-utils = { workspace = true }
```

### Workspace directory structure / workspace 目录结构

```
monorepo/
  pyproject.toml        # Workspace root (defines members) / workspace 根（定义 members）
  uv.lock               # Shared lockfile / 共享 lockfile
  packages/
    app/
      pyproject.toml
      src/
    shared-utils/
      pyproject.toml
      src/
```

---

## Speed/feature comparison with Poetry / 与 Poetry 的速度/功能对比

| Feature / 功能 | Poetry | uv |
|------|--------|-----|
| Language / 语言 | Python | Rust |
| Install speed / 安装速度 | Slow (seconds) / 慢（秒级） | Extremely fast (milliseconds, 10-100x faster) / 极快（毫秒级，快 10-100x） |
| Dependency resolver / 依赖解析 | Custom resolver / 自研解析器 | Custom PubGrub resolver / 自研 PubGrub 解析器 |
| Python version management / Python 版本管理 | Not supported / 不支持 | Built-in (`uv python install`) / 内置 |
| Lockfile | `poetry.lock` (Poetry-specific / Poetry 专属) | `uv.lock` (cross-platform universal / 跨平台通用) |
| Workspace (monorepo) | Not supported / 不支持 | Native support / 原生支持 |
| PyPI publishing / PyPI 发布 | Built-in / 内置 | Via `uv build` + `uv publish` / 通过 `uv build` + `uv publish` |
| pip-compatible interface / pip 兼容接口 | None / 无 | `uv pip` |
| Global tool management / 全局工具管理 | None (needs pipx) / 无（需 pipx） | `uv tool` / `uvx` |
| Single-file script deps / 单文件脚本依赖 | None / 无 | Supports PEP 723 / 支持 PEP 723 |
| pre-commit integration / pre-commit 集成 | Fair / 一般 | Good (uvx is fast) / 良好（uvx 快速） |
| Config standard / 配置标准 | Mixed (tool.poetry + project) / 混合 | Standard PEP 621 / 标准 PEP 621 |
| Maturity / 成熟度 | High (since 2018) / 高（2018 年起） | Newer (since 2024, rapidly evolving) / 较新（2024 年起，快速迭代） |

---

## Migrating a Poetry project to uv / 迁移 Poetry 项目到 uv

### Steps / 步骤

**1. Install uv / 安装 uv**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**2. Migrate `pyproject.toml` / 迁移 `pyproject.toml`**

Poetry's dependency syntax needs to be migrated to the standard `[project]` section:

> Poetry 的依赖写法需迁移到标准 `[project]` 节：

```toml
# Poetry old syntax / Poetry 旧写法
[tool.poetry.dependencies]
python = "^3.10"
requests = "^2.28"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0"

# After migration (uv / PEP 621 standard) / 迁移后（uv / PEP 621 标准）
[project]
requires-python = ">=3.10"
dependencies = ["requests>=2.28"]

[dependency-groups]
dev = ["pytest>=7.0"]

[build-system]
requires = ["hatchling"]    # Or "flit-core", "setuptools" / 或 "flit-core", "setuptools"
build-backend = "hatchling.build"
```

**3. Migrate lockfile from `poetry.lock` / 从 `poetry.lock` 迁移 lockfile**

```bash
# Delete poetry.lock and let uv regenerate / 删除 poetry.lock，让 uv 重新生成
rm poetry.lock
uv lock        # Generate uv.lock / 生成 uv.lock
uv sync        # Install all dependencies / 安装所有依赖
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
# GitHub Actions example / GitHub Actions 示例
- name: Install uv
  uses: astral-sh/setup-uv@v4

- name: Install dependencies
  run: uv sync --frozen

- name: Run tests
  run: uv run pytest
```

---

*Last updated: 2026-04-13 / 最后更新：2026-04-13*
