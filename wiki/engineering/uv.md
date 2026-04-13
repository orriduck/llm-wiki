# uv

> Astral 出品、用 Rust 编写的极速 Python 包管理器，号称比 pip 快 10-100 倍，可替代 pip、pip-tools、pipx、poetry、pyenv、virtualenv 等多个工具。

## 安装

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows PowerShell
irm https://astral.sh/uv/install.ps1 | iex

# 通过 pip 安装
pip install uv

# 通过 Homebrew（macOS）
brew install uv
```

验证安装：

```bash
uv --version
uv self update    # 自我更新
```

---

## 项目初始化：`uv init`

```bash
# 在新目录中创建项目
uv init my-project
cd my-project

# 在当前目录初始化
uv init

# 创建库（lib）项目（不带 main.py）
uv init --lib my-lib

# 指定 Python 版本
uv init --python 3.12 my-project
```

`uv init` 自动生成：

```
my-project/
  .python-version    # 指定 Python 版本
  .gitignore
  README.md
  main.py            # 示例入口文件
  pyproject.toml
```

初始 `pyproject.toml` 结构：

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

## 依赖管理命令

### `uv add` — 添加依赖

```bash
uv add requests                          # 添加运行时依赖
uv add "requests>=2.28"                 # 指定版本约束
uv add --dev pytest black isort         # 添加开发依赖
uv add --optional mysql mysqlclient     # 添加可选依赖（extras）

uv add "git+https://github.com/user/repo"   # Git 源
uv add ./local-package                       # 本地路径（editable）

uv add requests --frozen                 # 不更新 lockfile（只更新 pyproject.toml）
```

开发依赖会写入 `pyproject.toml` 的 `[dependency-groups]` 节：

```toml
[dependency-groups]
dev = [
    "pytest>=7.0",
    "black>=24.0",
]
```

### `uv remove` — 移除依赖

```bash
uv remove requests
uv remove --dev pytest
```

### `uv sync` — 同步环境

将虚拟环境与 `uv.lock` 完全同步（安装缺少的，卸载多余的）。

```bash
uv sync                                  # 同步所有依赖（含 dev）
uv sync --no-dev                         # 只安装运行时依赖（生产环境）
uv sync --only-dev                       # 只安装 dev 依赖
uv sync --group lint                     # 包含指定依赖组
uv sync --frozen                         # 不更新 lockfile，严格按现有 lockfile 安装
uv sync --no-install-project             # 不安装项目本身
```

### `uv lock` — 锁定依赖

```bash
uv lock                                  # 生成/更新 uv.lock
uv lock --upgrade                        # 升级所有依赖到最新兼容版本
uv lock --upgrade-package requests       # 只升级指定包
uv lock --check                          # 检查 lockfile 是否最新
```

### `uv pip` — 兼容 pip 的接口

```bash
uv pip install requests                  # 等同 pip install
uv pip install -r requirements.txt
uv pip list
uv pip freeze
uv pip compile requirements.in           # 等同 pip-compile
```

---

## `pyproject.toml` 中 uv 的配置方式

```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.28",
    "pydantic>=2.0",
]

# 开发依赖组
[dependency-groups]
dev = ["pytest>=7.0", "black", "mypy"]
lint = ["ruff", "isort"]

# uv 专属配置
[tool.uv]
# 指定 Python 版本（优先级高于 .python-version）
python = "3.12"

# 自定义包源
[[tool.uv.index]]
name = "private"
url = "https://pypi.company.com/simple"
priority = "primary"    # first / primary / supplemental / default

# 开发模式安装的包（editable）
[tool.uv.sources]
my-lib = { path = "../my-lib", editable = true }
# 或 workspace 成员
other-pkg = { workspace = true }

# 额外约束（不直接依赖但限制版本）
constraint-dependencies = ["numpy<2.0"]

# 覆盖特定包版本（强制使用指定版本）
override-dependencies = ["urllib3==1.26.18"]
```

---

## 虚拟环境管理：`uv venv`

```bash
# 在项目目录创建 .venv（uv sync 会自动创建）
uv venv

# 指定 Python 版本
uv venv --python 3.11

# 指定路径
uv venv /path/to/my-env

# 激活虚拟环境
source .venv/bin/activate      # macOS / Linux
.venv\Scripts\activate          # Windows
```

uv 会自动管理 `.venv`，大多数情况下不需要手动创建。

---

## `uv run` — 运行脚本/工具

`uv run` 在运行前自动同步环境，确保依赖最新。

```bash
# 运行 Python 文件
uv run main.py

# 运行已安装的工具
uv run pytest tests/
uv run black .
uv run mypy src/

# 运行时临时添加依赖（不修改 pyproject.toml）
uv run --with httpx python -c "import httpx; print(httpx.__version__)"

# 运行单文件脚本（带内联依赖声明）
uv run script.py
```

### 单文件脚本的内联依赖（PEP 723）

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
uv run script.py    # 自动安装 requests 和 rich 后运行
```

---

## `uv tool` — 全局工具管理

```bash
# 临时运行工具（不安装，使用隔离环境）
uvx black .
uvx ruff check .
uvx mypy src/

# 安装全局工具（添加到 PATH）
uv tool install black
uv tool install mypy
uv tool install ruff

# 运行特定版本
uvx black@24.3.0 .
uvx --from 'black==24.3.0' black .

# 带额外依赖运行
uvx --with mkdocs-material mkdocs build

# 查看已安装工具
uv tool list

# 升级工具
uv tool upgrade black
uv tool upgrade --all

# 卸载工具
uv tool uninstall black
```

---

## Workspace 支持

适合 monorepo，多个 Python 包共享一个 `uv.lock`。

### 根目录 `pyproject.toml`

```toml
[tool.uv.workspace]
members = ["packages/*"]
exclude = ["packages/experimental"]
```

### 成员间互相依赖

```toml
# packages/app/pyproject.toml
[project]
name = "app"
dependencies = ["shared-utils"]

[tool.uv.sources]
shared-utils = { workspace = true }
```

### workspace 目录结构

```
monorepo/
  pyproject.toml        # workspace 根（定义 members）
  uv.lock               # 共享 lockfile
  packages/
    app/
      pyproject.toml
      src/
    shared-utils/
      pyproject.toml
      src/
```

---

## 与 Poetry 的速度/功能对比

| 功能 | Poetry | uv |
|------|--------|-----|
| 语言 | Python | Rust |
| 安装速度 | 慢（秒级） | 极快（毫秒级，快 10-100x） |
| 依赖解析 | 自研解析器 | 自研 PubGrub 解析器 |
| Python 版本管理 | 不支持 | 内置（`uv python install`） |
| lockfile | `poetry.lock`（Poetry 专属） | `uv.lock`（跨平台通用） |
| Workspace（monorepo）| 不支持 | 原生支持 |
| PyPI 发布 | 内置 | 通过 `uv build` + `uv publish` |
| pip 兼容接口 | 无 | `uv pip` |
| 全局工具管理 | 无（需 pipx） | `uv tool` / `uvx` |
| 单文件脚本依赖 | 无 | 支持 PEP 723 |
| pre-commit 集成 | 一般 | 良好（uvx 快速） |
| 配置标准 | 混合（tool.poetry + project） | 标准 PEP 621 |
| 成熟度 | 高（2018 年起） | 较新（2024 年起，快速迭代） |

---

## 迁移 Poetry 项目到 uv

### 步骤

**1. 安装 uv**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**2. 迁移 `pyproject.toml`**

Poetry 的依赖写法需迁移到标准 `[project]` 节：

```toml
# Poetry 旧写法
[tool.poetry.dependencies]
python = "^3.10"
requests = "^2.28"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0"

# 迁移后（uv / PEP 621 标准）
[project]
requires-python = ">=3.10"
dependencies = ["requests>=2.28"]

[dependency-groups]
dev = ["pytest>=7.0"]

[build-system]
requires = ["hatchling"]    # 或 "flit-core", "setuptools"
build-backend = "hatchling.build"
```

**3. 从 `poetry.lock` 迁移 lockfile**

```bash
# 删除 poetry.lock，让 uv 重新生成
rm poetry.lock
uv lock        # 生成 uv.lock
uv sync        # 安装所有依赖
```

**4. 替换常用命令**

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

**5. 更新 CI/CD 配置**

```yaml
# GitHub Actions 示例
- name: Install uv
  uses: astral-sh/setup-uv@v4

- name: Install dependencies
  run: uv sync --frozen

- name: Run tests
  run: uv run pytest
```

---

*最后更新：2026-04-13*
