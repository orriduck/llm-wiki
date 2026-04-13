# Poetry

> Python 依赖管理与打包工具，通过 `pyproject.toml` 统一管理项目元数据、依赖和虚拟环境，提供可重现的构建。

## 安装

### 推荐方式：通过 pipx 安装（隔离环境）

```bash
pipx install poetry
```

### 官方安装脚本

```bash
# macOS / Linux / WSL
curl -sSL https://install.python-poetry.org | python3 -

# Windows PowerShell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

### 验证安装

```bash
poetry --version
poetry self update   # 升级到最新版本
```

Poetry 需要 Python 3.10+，始终在独立虚拟环境中运行，不污染全局 Python 环境。

---

## 初始化项目

```bash
# 在已有目录中初始化（交互式问答）
poetry init

# 创建全新项目
poetry new my-project

# 创建后安装依赖（读取 pyproject.toml）
poetry install
```

---

## `pyproject.toml` 结构详解

Poetry 2.0+ 推荐使用 PEP 621 标准的 `[project]` 节，同时保留 `[tool.poetry]` 做扩展配置。

```toml
[project]
name = "my-package"
version = "0.1.0"
description = "简短描述"
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

# 运行时依赖
dependencies = [
    "requests>=2.28",
    "pydantic>=2.0",
]

# 可选依赖组（extras）
[project.optional-dependencies]
mysql = ["mysqlclient>=1.3,<2.0"]
pgsql = ["psycopg2>=2.9,<3.0"]

# CLI 入口点
[project.scripts]
my-cli = "my_package.console:main"

[project.urls]
repository = "https://github.com/example/my-package"
documentation = "https://docs.example.com"

# Poetry 扩展配置
[tool.poetry]
packages = [{ include = "my_package" }]

# 开发依赖（通过 groups 管理）
[tool.poetry.group.dev.dependencies]
pytest = ">=7.0"
black = "*"
isort = "*"
mypy = "*"

[tool.poetry.group.docs.dependencies]
mkdocs = "*"
mkdocs-material = "*"

# 构建后端
[build-system]
requires = ["poetry-core>=2.0.0"]
build-backend = "poetry.core.masonry.api"
```

### 版本约束语法

| 语法 | 含义 |
|------|------|
| `^2.1` | `>=2.1.0, <3.0.0`（兼容版本，推荐） |
| `~2.1.3` | `>=2.1.3, <2.2.0`（补丁级兼容） |
| `>=2.1,<3.0` | 显式范围 |
| `2.1.*` | 通配符 |
| `*` | 任意版本 |

---

## 依赖管理命令

### add — 添加依赖

```bash
poetry add requests                        # 添加运行时依赖
poetry add "requests>=2.28"               # 指定版本约束
poetry add pytest --group dev             # 添加到 dev 组
poetry add -D black                        # 等同于 --group dev（旧语法）
poetry add mkdocs --group docs             # 添加到自定义组

poetry add git+https://github.com/user/repo.git  # Git 源
poetry add ./local-package/                        # 本地路径
poetry add "requests[security]"            # 带 extras

poetry add requests --dry-run              # 预览，不实际修改
poetry add requests --lock                 # 只更新 lockfile，不安装
```

### remove — 移除依赖

```bash
poetry remove requests                  # 移除运行时依赖
poetry remove pytest --group dev        # 从指定组移除
poetry remove black --dry-run           # 预览
```

### update — 更新依赖

```bash
poetry update                           # 更新所有依赖（在约束范围内）
poetry update requests                  # 只更新指定包
poetry update --lock                    # 只更新 lockfile，不重装
poetry update --dry-run                 # 预览更新内容
```

### show — 查看依赖

```bash
poetry show                             # 列出所有已安装包
poetry show requests                    # 查看某包详情
poetry show --tree                      # 显示依赖树
poetry show --outdated                  # 显示可更新的包
poetry show --latest                    # 显示最新可用版本
poetry show --format json               # JSON 格式输出
```

### install — 安装依赖

```bash
poetry install                          # 安装所有依赖（含 dev）
poetry install --without dev            # 跳过 dev 组（生产环境）
poetry install --only main              # 只安装主依赖
poetry install --with docs              # 包含可选组
poetry install --all-groups             # 安装所有组
poetry install --no-root                # 不安装项目本身
poetry install --extras "mysql pgsql"   # 安装指定 extras
poetry install --compile                # 编译成字节码（.pyc）
```

### lock — 锁定依赖

```bash
poetry lock                             # 生成/更新 poetry.lock
poetry lock --regenerate                # 从头重新生成 lockfile
poetry check                            # 验证 pyproject.toml 与 lockfile 一致性
poetry check --lock                     # 检查 lockfile 是否存在且最新
```

### version — 版本管理

```bash
poetry version                          # 显示当前版本
poetry version patch                    # 1.0.0 → 1.0.1
poetry version minor                    # 1.0.0 → 1.1.0
poetry version major                    # 1.0.0 → 2.0.0
poetry version 2.1.0                    # 直接设置版本
```

---

## 虚拟环境管理

Poetry 自动创建和管理虚拟环境。

```bash
# 查看当前环境信息
poetry env info
poetry env info --path                  # 只显示路径

# 列出所有关联的虚拟环境
poetry env list

# 切换/创建使用特定 Python 版本的环境
poetry env use python3.11
poetry env use /usr/bin/python3.10

# 删除虚拟环境
poetry env remove python3.11
poetry env remove --all

# 激活虚拟环境（进入 shell）
poetry shell                            # 启动子 shell
eval $(poetry env activate)            # 激活到当前 shell（Poetry 2.0+）
```

### 虚拟环境位置

| 配置 | 默认行为 |
|------|----------|
| 全局（默认） | `~/.cache/pypoetry/virtualenvs/` |
| 项目内 | `poetry config virtualenvs.in-project true` → 项目根目录的 `.venv/` |

在 CI/CD 或 Docker 中通常推荐 `virtualenvs.in-project true`。

---

## Scripts / Tasks 配置

通过 `[project.scripts]` 定义 CLI 入口点（随包安装后可直接调用），通过 `[tool.poetry.scripts]` 定义只在开发时使用的任务脚本（Poetry 2.0+ 支持任务脚本）。

```toml
# CLI 入口点（会被安装到 PATH）
[project.scripts]
my-cli = "my_package.cli:main"

# Poetry 任务脚本（仅开发环境，poetry run 调用）
[tool.poetry.scripts]
lint = "scripts.lint:run"
test = "pytest:main"
```

```bash
# 运行任务脚本
poetry run my-cli --help
poetry run pytest tests/
poetry run black .
```

---

## 发布包

### 构建

```bash
poetry build                            # 生成 sdist 和 wheel（放在 dist/）
poetry build --format wheel             # 只构建 wheel
poetry build --format sdist             # 只构建源码包
poetry build --clean                    # 构建前清理 dist/
```

### 发布到 PyPI

```bash
# 配置 PyPI token（推荐，避免密码）
poetry config pypi-token.pypi your-token-here

# 发布
poetry publish                          # 发布已构建的包
poetry publish --build                  # 构建后立即发布

# 发布到私有仓库
poetry publish --repository my-repo
```

### 配置私有仓库

```toml
[[tool.poetry.source]]
name = "private-repo"
url = "https://pypi.company.com/simple"
priority = "primary"    # primary / supplemental / explicit / default
```

```bash
poetry config http-basic.private-repo username password
```

---

## 常用配置（poetry config）

```bash
# 查看所有配置
poetry config --list

# 虚拟环境放在项目目录内（推荐）
poetry config virtualenvs.in-project true

# 总是创建虚拟环境（即使已在 venv 中）
poetry config virtualenvs.create true

# 设置 Python 路径偏好
poetry config virtualenvs.prefer-active-python true

# 配置缓存目录
poetry config cache-dir /tmp/poetry-cache

# 项目级别配置（只影响当前项目）
poetry config virtualenvs.in-project true --local
```

### 常用配置项说明

| 配置键 | 默认值 | 说明 |
|--------|--------|------|
| `virtualenvs.in-project` | `false` | 是否在项目目录创建 `.venv` |
| `virtualenvs.create` | `true` | 是否自动创建虚拟环境 |
| `virtualenvs.prefer-active-python` | `false` | 优先使用当前激活的 Python |
| `installer.max-workers` | CPU 数量 | 并行安装的最大线程数 |
| `installer.parallel` | `true` | 是否并行安装 |

---

## 与 pip 的对比

| 功能 | pip / pip-tools | Poetry |
|------|----------------|--------|
| 安装包 | `pip install` | `poetry add` |
| 依赖锁定 | `pip-compile`（需额外工具） | 内置 `poetry.lock` |
| 虚拟环境 | 手动 `python -m venv` | 自动管理 |
| 依赖分组 | 无（需多个 requirements 文件） | `groups` 原生支持 |
| 发布包 | `twine`（需额外工具） | `poetry publish` 内置 |
| `pyproject.toml` | 部分支持 | 原生核心 |
| 速度 | 快 | 慢（依赖解析较重） |
| 学习曲线 | 低 | 中 |

---

*最后更新：2026-04-13*
