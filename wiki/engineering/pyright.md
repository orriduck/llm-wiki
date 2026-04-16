# pyright — Microsoft's Python Static Type Checker / pyright — 微软 Python 静态类型检查器

pyright is a high-performance Python static type checker developed by Microsoft in TypeScript/Node.js. It is 3-5x faster than mypy, performs stricter type inference, and powers the VSCode Pylance extension.

> pyright 是微软用 TypeScript/Node.js 开发的高性能 Python 静态类型检查器，比 mypy 快 3-5 倍，类型推断更严格，是 VSCode Pylance 插件的底层引擎。

## What is pyright / pyright 是什么

Key characteristics:

> 主要特点：

- **Extremely fast**: 3-5x faster than mypy using just-in-time lazy evaluation
- **Strict**: checks unannotated functions by default, with more precise type inference
- **Standards-compliant**: full support for the latest Python type specifications (PEP 526, 612, 673, etc.)
- **IDE integration**: the underlying engine for VSCode's Pylance extension, providing real-time type checking

> - **极快**：比 mypy 快 3-5 倍，采用懒加载（just-in-time）求值策略
> - **严格**：对未标注函数也默认进行检查，类型推断更精确
> - **标准兼容**：完整支持最新 Python 类型规范（PEP 526、612、673 等）
> - **IDE 集成**：VSCode Pylance 扩展的底层引擎，提供实时类型检查

Best suited for: large codebases requiring strict type guarantees, new projects establishing type safety from scratch, or migrating from mypy for faster checks.

> 适合场景：需要严格类型保障的大型代码库、新项目从零开始建立类型安全、从 mypy 迁移寻求更快检查速度。

---

## Installation / 安装

```bash
# via pip
pip install pyright

# add as dev dependency with uv (recommended)
uv add --dev pyright

# run without installing via uvx
uvx pyright .

# global install via npm (native method, requires Node.js)
npm install -g pyright
```

pyproject.toml is updated automatically:

> pyproject.toml 自动更新：

```toml
[dependency-groups]
dev = [
    "pyright>=1.1",
]
```

Note: pyright installed via pip/uv is a wrapper around the Node.js version — Node.js still runs underneath.

> 注意：pip/uv 安装的 pyright 是 Node.js 版本的封装，底层仍运行 Node.js。

---

## Basic Usage / 基本用法

```bash
# check current directory
pyright .

# check a specific directory
pyright src/

# check a single file
pyright src/my_module/api.py

# specify a config file
pyright -p pyrightconfig.json

# specify Python version
pyright --pythonversion 3.11 src/

# specify virtual environment path
pyright -v .venv src/

# watch mode (for development)
pyright --watch src/

# output JSON format (for CI parsing)
pyright --outputjson src/

# via uv run
uv run pyright src/

# via uvx (no installation needed)
uvx pyright src/
```

---

## Configuration: `pyrightconfig.json` / 配置：`pyrightconfig.json`

Create `pyrightconfig.json` in the project root:

> 在项目根目录创建 `pyrightconfig.json`：

```json
{
  "include": ["src"],
  "exclude": [
    "**/node_modules",
    "**/__pycache__",
    "src/migrations",
    "src/legacy"
  ],
  "ignore": ["src/oldstuff"],
  "defineConstant": {
    "DEBUG": true
  },
  "stubPath": "src/stubs",
  "venvPath": ".",
  "venv": ".venv",
  "pythonVersion": "3.11",
  "pythonPlatform": "Linux",
  "typeCheckingMode": "standard",
  "reportMissingImports": "error",
  "reportMissingTypeStubs": "warning"
}
```

---

## Configuration: `[tool.pyright]` in `pyproject.toml` / 配置：`pyproject.toml` 中的 `[tool.pyright]`

Centralizing configuration in `pyproject.toml` is recommended to avoid extra files:

> 推荐将配置集中在 `pyproject.toml`，避免额外文件：

```toml
[tool.pyright]
# scope of checks
include = ["src"]
exclude = [
    "**/node_modules",
    "**/__pycache__",
    "src/migrations",
]
ignore = ["src/legacy"]

# Python environment
pythonVersion = "3.11"
pythonPlatform = "Linux"

# virtual environment (relative to pyproject.toml location)
venvPath = "."
venv = ".venv"

# strictness level
typeCheckingMode = "standard"   # off | basic | standard | strict

# override individual rule severity (overrides typeCheckingMode defaults)
reportMissingImports = "error"
reportMissingTypeStubs = "warning"
reportUnknownVariableType = "none"   # disable a rule
```

Configuration priority: `pyrightconfig.json` > `pyproject.toml` > VSCode settings.

> 配置优先级：`pyrightconfig.json` > `pyproject.toml` > VSCode 设置。

---

## typeCheckingMode Explained / typeCheckingMode 说明

| Mode | Description | Best For |
|------|-------------|----------|
| `off` | Disables type checking; still reports syntax errors | Syntax-only checks |
| `basic` | Basic loose checks | Gradually introducing types to legacy codebases |
| `standard` | Standard checks (**default**) | Most projects |
| `strict` | Strict; all inferred unknown types are errors | New projects or high type-coverage projects |

Each mode is progressively stricter; `strict` requires complete type annotations on all functions.

> 各模式在严格程度上逐级递增，`strict` 要求所有函数都有完整类型注解。

---

## Comparison with mypy / 与 mypy 的差异对比

| Dimension | pyright | mypy |
|-----------|---------|------|
| **Implementation language** | TypeScript/Node.js | Python |
| **Speed** | 3-5x faster (JIT lazy loading) | Slower (multi-pass analysis) |
| **Unannotated functions** | **Checked by default** | Skipped by default (requires `--check-untyped-defs`) |
| **Return type inference** | Inferred from function body | Assumed `Any` if unannotated |
| **Type narrowing** | Supports literal equality, membership tests, boolean coercion | Fewer guard patterns |
| **Union operations** | Always uses union (preserves type info) | Often uses join (may lose type info) |
| **Instance variables** | Infers union type from all assignments | Uses first assignment (may produce false positives) |
| **Class variable distinction** | Distinguishes pure class / instance / class-instance variables | Mixed handling |
| **Class decorators** | Full support | Mostly ignored |
| **Any vs Unknown** | Distinguishes explicit `Any` from implicit `Unknown` | Tracks only explicit `Any` |
| **Plugin system** | None (by design, avoids security/maintenance issues) | Supports plugins |
| **Circular references** | Cannot resolve some scenarios | Multi-pass can handle some |
| **Type comments (`# type:`)** | Partial support | Full support |
| **VSCode integration** | Pylance (official) | mypy extension (third-party) |

---

## Gradual Typing Strategy / 渐进式类型化策略

Recommended path from zero type annotations to strict type safety:

> 从零类型注解到严格类型安全的推荐路径：

**Step 1: basic mode — assess current state / 第一步：basic 模式，了解现状**

```toml
[tool.pyright]
include = ["src"]
typeCheckingMode = "basic"
```

```bash
uv run pyright src/  # see how many errors exist
```

**Step 2: fix import-related issues / 第二步：修复 import 相关问题**

```toml
[tool.pyright]
typeCheckingMode = "basic"
reportMissingImports = "error"
reportMissingTypeStubs = "warning"
```

Install missing stub packages:

> 安装缺失的 stub 包：

```bash
uv add --dev types-requests types-PyYAML pandas-stubs
```

**Step 3: upgrade to standard, tighten per module / 第三步：升级到 standard 模式，逐模块收紧**

```toml
[tool.pyright]
typeCheckingMode = "standard"

# relax some rules for legacy code
reportUnknownVariableType = "none"
reportUnknownParameterType = "none"
```

**Step 4: enable strict on new code, protect core modules / 第四步：对新代码启用 strict，保护核心模块**

```toml
[tool.pyright]
typeCheckingMode = "standard"

# enforce strict on specific directories
strict = ["src/core", "src/api"]
```

Or add a comment at the top of a file:

> 或在文件顶部添加注释：

```python
# pyright: strict
```

**Step 5: global strict mode / 第五步：全局 strict 模式**

```toml
[tool.pyright]
typeCheckingMode = "strict"
```

---

## VSCode Integration (Pylance) / VSCode 集成（Pylance）

pyright is the underlying engine of the VSCode **Pylance extension**. Installing Pylance enables real-time type checking.

> pyright 是 VSCode **Pylance 扩展**的底层引擎，安装 Pylance 后即可获得实时类型检查。

Setup steps:

> 安装步骤：

1. Search for **Pylance** in the VSCode Extensions marketplace and install it
2. Open a Python file and select the Python interpreter in the bottom-right corner
3. Pylance automatically reads `pyrightconfig.json` or `pyproject.toml` from the project

`.vscode/settings.json` configuration:

> `.vscode/settings.json` 配置：

```json
{
  "python.languageServer": "Pylance",
  "python.analysis.typeCheckingMode": "standard",
  "python.analysis.autoImportCompletions": true,
  "python.analysis.inlayHints.variableTypes": true,
  "python.analysis.inlayHints.functionReturnTypes": true
}
```

Note: `python.analysis.typeCheckingMode` in VSCode has the same effect as `typeCheckingMode` in `pyrightconfig.json`, but `pyrightconfig.json` takes higher priority.

> 注意：VSCode 中的 `python.analysis.typeCheckingMode` 与 `pyrightconfig.json` 中的 `typeCheckingMode` 效果相同，但 `pyrightconfig.json` 优先级更高。

---

## pre-commit Hook Configuration / pre-commit Hook 配置

pyright has no official pre-commit repository; use a local hook:

> pyright 无官方 pre-commit 仓库，使用 local hook：

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pyright
        name: pyright
        language: system
        entry: uv run pyright
        types: [python]
        args: ["src/"]
        pass_filenames: false   # pyright needs to analyze the entire package
```

Or use uvx (no prior installation needed):

> 或使用 uvx（无需提前安装）：

```yaml
repos:
  - repo: local
    hooks:
      - id: pyright
        name: pyright
        language: system
        entry: uvx pyright
        types: [python]
        args: ["src/"]
        pass_filenames: false
```

Install and run:

> 安装与运行：

```bash
uv add --dev pre-commit
uv run pre-commit install
uv run pre-commit run --all-files
```

---

## Common Errors and Solutions / 常见报错类型和解决方法

| Error Code | Meaning | Solution |
|------------|---------|----------|
| `reportMissingImports` | Module not found | Install package or stub; check `venvPath`/`venv` config |
| `reportMissingTypeStubs` | No type stubs for module | Install `types-xxx` stub package, or set to `"none"` |
| `reportUnknownVariableType` | Variable type inferred as Unknown | Add type annotation, or set to `"none"` |
| `reportUnknownParameterType` | Function parameter type unknown | Add type annotation to parameter |
| `reportReturnType` | Return type mismatch | Fix function return type annotation |
| `reportAttributeAccessIssue` | Accessing nonexistent attribute | Check object type, add `hasattr` guard |
| `reportOperatorIssue` | Incompatible operator types | Ensure operand types support the operator |
| `reportIndexIssue` | Subscript access type error | Check if container type supports the index type |
| `reportArgumentType` | Function argument type mismatch | Fix argument type or function signature |
| `reportCallIssue` | Calling a non-callable object | Confirm the object is callable |

Inline suppression comments:

> 常用内联抑制注释：

```python
x: int = some_func()  # type: ignore  # mypy-compatible style
x: int = some_func()  # pyright: ignore[reportReturnType]  # pyright precise style

# set checking mode at the top of the file
# pyright: basic
# pyright: strict
```

---

## Run Without Installing via uvx / uvx 无需安装直接运行

```bash
# check current directory
uvx pyright .

# check src directory
uvx pyright src/

# specify Python version
uvx pyright --pythonversion 3.11 src/

# specify version
uvx pyright@1.1.390 src/
```

Suitable for CI environments or one-off checks without adding pyright to project dependencies.

> 适合 CI 环境或临时检查，无需将 pyright 添加到项目依赖。

---

*最后更新：2026-04-16*
