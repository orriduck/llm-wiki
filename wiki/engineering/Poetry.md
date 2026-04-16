# Poetry / Poetry

> A Python dependency management and packaging tool that unifies project metadata, dependencies, and virtual environments through `pyproject.toml`, providing reproducible builds.

> Python 依赖管理与打包工具，通过 `pyproject.toml` 统一管理项目元数据、依赖和虚拟环境，提供可重现的构建。

## Installation / 安装

### Recommended: Install via pipx (isolated environment) / 推荐方式：通过 pipx 安装（隔离环境）

```bash
pipx install poetry
```

### Official install script / 官方安装脚本

```bash
# macOS / Linux / WSL
curl -sSL https://install.python-poetry.org | python3 -

# Windows PowerShell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

### Verify installation / 验证安装

```bash
poetry --version
poetry self update   # Upgrade to the latest version / 升级到最新版本
```

Poetry requires Python 3.10+ and always runs in an isolated virtual environment without polluting the global Python environment.

> Poetry 需要 Python 3.10+，始终在独立虚拟环境中运行，不污染全局 Python 环境。

---

## Project initialization / 初始化项目

```bash
# Initialize in an existing directory (interactive Q&A)
# 在已有目录中初始化（交互式问答）
poetry init

# Create a brand new project / 创建全新项目
poetry new my-project

# Install dependencies after creation (reads pyproject.toml)
# 创建后安装依赖（读取 pyproject.toml）
poetry install
```

---

## `pyproject.toml` structure explained / `pyproject.toml` 结构详解

Poetry 2.0+ recommends using the PEP 621 standard `[project]` section while retaining `[tool.poetry]` for extended configuration.

> Poetry 2.0+ 推荐使用 PEP 621 标准的 `[project]` 节，同时保留 `[tool.poetry]` 做扩展配置。

```toml
[project]
name = "my-package"
version = "0.1.0"
description = "Short description"
readme = "README.md"
requires-python = ">=3.10"
license = "MIT"
authors = [
    { name = "Your Name", email = "you@example.com" }
]
keywords = ["example", "package"]
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
]

# Runtime dependencies / 运行时依赖
dependencies = [
    "requests>=2.28",
    "pydantic>=2.0",
]

# Optional dependency groups (extras) / 可选依赖组（extras）
[project.optional-dependencies]
mysql = ["mysqlclient>=1.3,<2.0"]
pgsql = ["psycopg2>=2.9,<3.0"]

# CLI entry points / CLI 入口点
[project.scripts]
my-cli = "my_package.console:main"

[project.urls]
repository = "https://github.com/example/my-package"
documentation = "https://docs.example.com"

# Poetry extended configuration / Poetry 扩展配置
[tool.poetry]
packages = [{ include = "my_package" }]

# Dev dependencies (managed via groups) / 开发依赖（通过 groups 管理）
[tool.poetry.group.dev.dependencies]
pytest = ">=7.0"
black = "*"
isort = "*"
mypy = "*"

[tool.poetry.group.docs.dependencies]
mkdocs = "*"
mkdocs-material = "*"

# Build backend / 构建后端
[build-system]
requires = ["poetry-core>=2.0.0"]
build-backend = "poetry.core.masonry.api"
```

### Version constraint syntax / 版本约束语法

| Syntax / 语法 | Meaning / 含义 |
|------|------|
| `^2.1` | `>=2.1.0, <3.0.0` (compatible version, recommended / 兼容版本，推荐) |
| `~2.1.3` | `>=2.1.3, <2.2.0` (patch-level compatible / 补丁级兼容) |
| `>=2.1,<3.0` | Explicit range / 显式范围 |
| `2.1.*` | Wildcard / 通配符 |
| `*` | Any version / 任意版本 |

---

## Dependency management commands / 依赖管理命令

### add -- Add dependency / 添加依赖

```bash
poetry add requests                        # Add runtime dependency / 添加运行时依赖
poetry add "requests>=2.28"               # Specify version constraint / 指定版本约束
poetry add pytest --group dev             # Add to dev group / 添加到 dev 组
poetry add -D black                        # Same as --group dev (old syntax) / 等同于 --group dev（旧语法）
poetry add mkdocs --group docs             # Add to custom group / 添加到自定义组

poetry add git+https://github.com/user/repo.git  # Git source / Git 源
poetry add ./local-package/                        # Local path / 本地路径
poetry add "requests[security]"            # With extras / 带 extras

poetry add requests --dry-run              # Preview, no actual changes / 预览，不实际修改
poetry add requests --lock                 # Only update lockfile, don't install / 只更新 lockfile，不安装
```

### remove -- Remove dependency / 移除依赖

```bash
poetry remove requests                  # Remove runtime dependency / 移除运行时依赖
poetry remove pytest --group dev        # Remove from specific group / 从指定组移除
poetry remove black --dry-run           # Preview / 预览
```

### update -- Update dependencies / 更新依赖

```bash
poetry update                           # Update all dependencies (within constraints) / 更新所有依赖（在约束范围内）
poetry update requests                  # Update specific package / 只更新指定包
poetry update --lock                    # Only update lockfile, don't reinstall / 只更新 lockfile，不重装
poetry update --dry-run                 # Preview updates / 预览更新内容
```

### show -- View dependencies / 查看依赖

```bash
poetry show                             # List all installed packages / 列出所有已安装包
poetry show requests                    # View package details / 查看某包详情
poetry show --tree                      # Show dependency tree / 显示依赖树
poetry show --outdated                  # Show updatable packages / 显示可更新的包
poetry show --latest                    # Show latest available versions / 显示最新可用版本
poetry show --format json               # JSON format output / JSON 格式输出
```

### install -- Install dependencies / 安装依赖

```bash
poetry install                          # Install all dependencies (including dev) / 安装所有依赖（含 dev）
poetry install --without dev            # Skip dev group (production) / 跳过 dev 组（生产环境）
poetry install --only main              # Install only main dependencies / 只安装主依赖
poetry install --with docs              # Include optional groups / 包含可选组
poetry install --all-groups             # Install all groups / 安装所有组
poetry install --no-root                # Don't install the project itself / 不安装项目本身
poetry install --extras "mysql pgsql"   # Install specific extras / 安装指定 extras
poetry install --compile                # Compile to bytecode (.pyc) / 编译成字节码（.pyc）
```

### lock -- Lock dependencies / 锁定依赖

```bash
poetry lock                             # Generate/update poetry.lock / 生成/更新 poetry.lock
poetry lock --regenerate                # Regenerate lockfile from scratch / 从头重新生成 lockfile
poetry check                            # Verify pyproject.toml and lockfile consistency / 验证 pyproject.toml 与 lockfile 一致性
poetry check --lock                     # Check if lockfile exists and is up to date / 检查 lockfile 是否存在且最新
```

### version -- Version management / 版本管理

```bash
poetry version                          # Show current version / 显示当前版本
poetry version patch                    # 1.0.0 → 1.0.1
poetry version minor                    # 1.0.0 → 1.1.0
poetry version major                    # 1.0.0 → 2.0.0
poetry version 2.1.0                    # Set version directly / 直接设置版本
```

---

## Virtual environment management / 虚拟环境管理

Poetry automatically creates and manages virtual environments.

> Poetry 自动创建和管理虚拟环境。

```bash
# View current environment info / 查看当前环境信息
poetry env info
poetry env info --path                  # Show path only / 只显示路径

# List all associated virtual environments / 列出所有关联的虚拟环境
poetry env list

# Switch/create environment using a specific Python version
# 切换/创建使用特定 Python 版本的环境
poetry env use python3.11
poetry env use /usr/bin/python3.10

# Delete virtual environment / 删除虚拟环境
poetry env remove python3.11
poetry env remove --all

# Activate virtual environment (enter shell) / 激活虚拟环境（进入 shell）
poetry shell                            # Start a sub-shell / 启动子 shell
eval $(poetry env activate)            # Activate in current shell (Poetry 2.0+) / 激活到当前 shell（Poetry 2.0+）
```

### Virtual environment location / 虚拟环境位置

| Configuration / 配置 | Default behavior / 默认行为 |
|------|----------|
| Global (default) / 全局（默认） | `~/.cache/pypoetry/virtualenvs/` |
| In-project / 项目内 | `poetry config virtualenvs.in-project true` -> `.venv/` in project root / 项目根目录的 `.venv/` |

Using `virtualenvs.in-project true` is recommended in CI/CD or Docker environments.

> 在 CI/CD 或 Docker 中通常推荐 `virtualenvs.in-project true`。

---

## Scripts / Tasks configuration / Scripts / Tasks 配置

Define CLI entry points via `[project.scripts]` (callable after package installation), and dev-only task scripts via `[tool.poetry.scripts]` (Poetry 2.0+ supports task scripts).

> 通过 `[project.scripts]` 定义 CLI 入口点（随包安装后可直接调用），通过 `[tool.poetry.scripts]` 定义只在开发时使用的任务脚本（Poetry 2.0+ 支持任务脚本）。

```toml
# CLI entry points (installed to PATH) / CLI 入口点（会被安装到 PATH）
[project.scripts]
my-cli = "my_package.cli:main"

# Poetry task scripts (dev environment only, invoked via poetry run)
# Poetry 任务脚本（仅开发环境，poetry run 调用）
[tool.poetry.scripts]
lint = "scripts.lint:run"
test = "pytest:main"
```

```bash
# Run task scripts / 运行任务脚本
poetry run my-cli --help
poetry run pytest tests/
poetry run black .
```

---

## Publishing packages / 发布包

### Build / 构建

```bash
poetry build                            # Generate sdist and wheel (in dist/) / 生成 sdist 和 wheel（放在 dist/）
poetry build --format wheel             # Build wheel only / 只构建 wheel
poetry build --format sdist             # Build source package only / 只构建源码包
poetry build --clean                    # Clean dist/ before build / 构建前清理 dist/
```

### Publish to PyPI / 发布到 PyPI

```bash
# Configure PyPI token (recommended, avoids password)
# 配置 PyPI token（推荐，避免密码）
poetry config pypi-token.pypi YOUR_API_KEY

# Publish / 发布
poetry publish                          # Publish built packages / 发布已构建的包
poetry publish --build                  # Build then publish immediately / 构建后立即发布

# Publish to private repository / 发布到私有仓库
poetry publish --repository my-repo
```

### Configure private repository / 配置私有仓库

```toml
[[tool.poetry.source]]
name = "private-repo"
url = "https://pypi.example.com/simple"
priority = "primary"    # primary / supplemental / explicit / default
```

```bash
poetry config http-basic.private-repo username password
```

---

## Common configuration (poetry config) / 常用配置（poetry config）

```bash
# View all configuration / 查看所有配置
poetry config --list

# Place virtual environment inside project directory (recommended)
# 虚拟环境放在项目目录内（推荐）
poetry config virtualenvs.in-project true

# Always create virtual environment (even if already in a venv)
# 总是创建虚拟环境（即使已在 venv 中）
poetry config virtualenvs.create true

# Set Python path preference / 设置 Python 路径偏好
poetry config virtualenvs.prefer-active-python true

# Configure cache directory / 配置缓存目录
poetry config cache-dir /tmp/poetry-cache

# Project-level configuration (affects current project only)
# 项目级别配置（只影响当前项目）
poetry config virtualenvs.in-project true --local
```

### Common configuration options / 常用配置项说明

| Config key / 配置键 | Default / 默认值 | Description / 说明 |
|--------|--------|------|
| `virtualenvs.in-project` | `false` | Whether to create `.venv` in project directory / 是否在项目目录创建 `.venv` |
| `virtualenvs.create` | `true` | Whether to auto-create virtual environment / 是否自动创建虚拟环境 |
| `virtualenvs.prefer-active-python` | `false` | Prefer currently active Python / 优先使用当前激活的 Python |
| `installer.max-workers` | CPU count / CPU 数量 | Max threads for parallel installation / 并行安装的最大线程数 |
| `installer.parallel` | `true` | Whether to install in parallel / 是否并行安装 |

---

## Comparison with pip / 与 pip 的对比

| Feature / 功能 | pip / pip-tools | Poetry |
|------|----------------|--------|
| Install packages / 安装包 | `pip install` | `poetry add` |
| Dependency locking / 依赖锁定 | `pip-compile` (requires extra tool / 需额外工具) | Built-in `poetry.lock` / 内置 `poetry.lock` |
| Virtual environment / 虚拟环境 | Manual `python -m venv` / 手动 `python -m venv` | Auto-managed / 自动管理 |
| Dependency groups / 依赖分组 | None (requires multiple requirements files / 需多个 requirements 文件) | Native `groups` support / `groups` 原生支持 |
| Package publishing / 发布包 | `twine` (requires extra tool / 需额外工具) | Built-in `poetry publish` / `poetry publish` 内置 |
| `pyproject.toml` | Partial support / 部分支持 | Native core / 原生核心 |
| Speed / 速度 | Fast / 快 | Slow (heavy dependency resolution / 依赖解析较重) |
| Learning curve / 学习曲线 | Low / 低 | Medium / 中 |

---

*Last updated: 2026-04-13 / 最后更新：2026-04-13*
