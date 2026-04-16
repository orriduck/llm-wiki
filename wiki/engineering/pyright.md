# pyright

> A high-performance Python static type checker developed by Microsoft, 3-5x faster than mypy with stricter type inference, and the underlying engine for the VSCode Pylance extension.

> 微软开发的高性能 Python 静态类型检查器，比 mypy 快 3-5 倍，类型推断更严格，VSCode Pylance 插件的底层引擎。

## What is pyright / pyright 是什么

pyright is a Python static type checker developed by Microsoft in TypeScript/Node.js. Key features:

> pyright 是微软用 TypeScript/Node.js 开发的 Python 静态类型检查器，主要特点：

- **Extremely fast**: 3-5x faster than mypy, using just-in-time lazy evaluation strategy

> **极快**：比 mypy 快 3-5 倍，采用懒加载（just-in-time）求值策略

- **Strict**: Checks unannotated functions by default, more precise type inference

> **严格**：对未标注函数也默认进行检查，类型推断更精确

- **Standards compliant**: Full support for latest Python type specifications (PEP 526, 612, 673, etc.)

> **标准兼容**：完整支持最新 Python 类型规范（PEP 526、612、673 等）

- **IDE integration**: Underlying engine for the VSCode Pylance extension, providing real-time type checking

> **IDE 集成**：VSCode Pylance 扩展的底层引擎，提供实时类型检查

Suitable for: large codebases needing strict type guarantees, new projects building type safety from scratch, migrating from mypy for faster checking.

> 适合场景：需要严格类型保障的大型代码库、新项目从零开始建立类型安全、从 mypy 迁移寻求更快检查速度。

---

## Installation / 安装

```bash
# pip install / pip 安装
pip install pyright

# uv add as dev dependency (recommended) / uv 添加为开发依赖（推荐）
uv add --dev pyright

# uvx run without installing / uvx 无需安装直接运行
uvx pyright .

# npm global install (native method, requires Node.js)
# npm 全局安装（原生方式，需要 Node.js）
npm install -g pyright
```

pyproject.toml auto-updates / pyproject.toml 自动更新：

```toml
[dependency-groups]
dev = [
    "pyright>=1.1",
]
```

Note: The pip/uv-installed pyright is a wrapper around the Node.js version; it still runs Node.js underneath.

> 注意：pip/uv 安装的 pyright 是 Node.js 版本的封装，底层仍运行 Node.js。

---

## Basic usage / 基本用法

```bash
# Check current directory / 检查当前目录
pyright .

# Check specific directory / 检查指定目录
pyright src/

# Check a single file / 检查单个文件
pyright src/my_module/api.py

# Specify config file / 指定配置文件
pyright -p pyrightconfig.json

# Specify Python version / 指定 Python 版本
pyright --pythonversion 3.11 src/

# Specify virtual environment path / 指定虚拟环境路径
pyright -v .venv src/

# Watch mode (during development) / 监听模式（开发时）
pyright --watch src/

# Output JSON format (for CI parsing) / 输出 JSON 格式（CI 解析用）
pyright --outputjson src/

# Via uv run / 通过 uv run
uv run pyright src/

# Via uvx (no install needed) / 通过 uvx（无需安装）
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

Recommended to centralize configuration in `pyproject.toml` to avoid extra files:

> 推荐将配置集中在 `pyproject.toml`，避免额外文件：

```toml
[tool.pyright]
# Check scope / 检查范围
include = ["src"]
exclude = [
    "**/node_modules",
    "**/__pycache__",
    "src/migrations",
]
ignore = ["src/legacy"]

# Python environment / Python 环境
pythonVersion = "3.11"
pythonPlatform = "Linux"

# Virtual environment (relative to pyproject.toml location)
# 虚拟环境（相对于 pyproject.toml 所在目录）
venvPath = "."
venv = ".venv"

# Type checking strictness / 类型检查严格程度
typeCheckingMode = "standard"   # off | basic | standard | strict

# Custom rule strictness (overrides typeCheckingMode defaults)
# 自定义规则严格程度（覆盖 typeCheckingMode 的默认值）
reportMissingImports = "error"
reportMissingTypeStubs = "warning"
reportUnknownVariableType = "none"   # Disable a specific rule / 关闭某条规则
```

Configuration priority: `pyrightconfig.json` > `pyproject.toml` > VSCode settings.

> 配置优先级：`pyrightconfig.json` > `pyproject.toml` > VSCode 设置。

---

## typeCheckingMode explained / typeCheckingMode 说明

| Mode / 模式 | Description / 说明 | Suitable for / 适合场景 |
|------|------|----------|
| `off` | Disables type checking, still reports syntax errors / 禁用类型检查，仍报告语法错误 | Syntax checking only / 仅需语法检查 |
| `basic` | Basic checking, lenient / 基础检查，宽松 | Legacy codebases with gradual adoption / 旧代码库渐进式引入 |
| `standard` | Standard checking (**default**) / 标准检查（**默认**） | Most projects / 大多数项目 |
| `strict` | Strict checking, all inferred unknown types are errors / 严格检查，所有推断未知类型均报错 | New projects or high type coverage projects / 新项目或高类型覆盖率项目 |

Each mode is progressively stricter; `strict` requires all functions to have complete type annotations.

> 各模式在严格程度上逐级递增，`strict` 要求所有函数都有完整类型注解。

---

## Comparison with mypy / 与 mypy 的差异对比

| Dimension / 维度 | pyright | mypy |
|------|---------|------|
| **Implementation language / 实现语言** | TypeScript/Node.js | Python |
| **Speed / 速度** | 3-5x faster (JIT lazy loading) / 快 3-5 倍（JIT 懒加载） | Slower (multi-pass analysis) / 较慢（多遍分析） |
| **Unannotated functions / 未注解函数** | **Checks by default / 默认检查** | Skips by default (needs `--check-untyped-defs`) / 默认跳过 |
| **Return type inference / 返回值推断** | Infers return type from function body / 从函数体推断返回类型 | Assumes `Any` for unannotated returns / 未注解返回值假设为 `Any` |
| **Type narrowing / 类型收窄** | Supports literal equality, member tests, boolean coercion / 支持 literal equality、成员测试、布尔强制转换 | Supports fewer guard patterns / 支持较少守卫模式 |
| **Union operations / Union 操作** | Always uses union (preserves type info) / 始终用 union（保留类型信息） | Usually uses join (may lose type info) / 通常用 join（可能丢失类型信息） |
| **Instance variables / 实例变量** | Infers union type from all assignments / 从所有赋值推断联合类型 | Uses first assignment (may have false positives) / 以第一次赋值为准（可能误报） |
| **Class variable distinction / 类变量区分** | Distinguishes pure class/instance/class-instance vars / 区分纯类变量/实例变量/类实例变量 | Conflates handling / 混淆处理 |
| **Class decorators / 类装饰器** | Full support / 完整支持 | Mostly ignored / 大部分忽略 |
| **Any vs Unknown** | Distinguishes explicit `Any` and implicit `Unknown` / 区分显式 `Any` 和隐式 `Unknown` | Only tracks explicit `Any` / 只跟踪显式 `Any` |
| **Plugin system / 插件系统** | None (design decision to avoid security/maintenance issues) / 无（设计决策，避免安全/维护问题） | Supports plugins / 支持插件 |
| **Circular references / 循环引用** | Some scenarios can't be resolved / 部分场景无法解析 | Multi-pass analysis handles some / 多遍分析可处理部分循环 |
| **Type comments (# type:) / 类型注释** | Partial support / 部分支持 | Full support / 完整支持 |
| **VSCode integration / VSCode 集成** | Pylance (official) / Pylance（官方） | mypy extension (third-party) / mypy 扩展（第三方） |

---

## Gradual typing strategy / 渐进式类型化策略

Recommended path from zero type annotations to strict type safety:

> 从零类型注解到严格类型安全的推荐路径：

**Step 1: basic mode, assess current state / basic 模式，了解现状**

```toml
[tool.pyright]
include = ["src"]
typeCheckingMode = "basic"
```

```bash
uv run pyright src/  # See how many errors there are / 查看有多少错误
```

**Step 2: Fix import-related issues / 修复 import 相关问题**

```toml
[tool.pyright]
typeCheckingMode = "basic"
reportMissingImports = "error"
reportMissingTypeStubs = "warning"
```

Install missing stub packages / 安装缺失的 stub 包：

```bash
uv add --dev types-requests types-PyYAML pandas-stubs
```

**Step 3: Upgrade to standard mode, tighten per module / 升级到 standard 模式，逐模块收紧**

```toml
[tool.pyright]
typeCheckingMode = "standard"

# Disable some rules for legacy code / 对遗留代码关闭部分规则
reportUnknownVariableType = "none"
reportUnknownParameterType = "none"
```

**Step 4: Enable strict for new code, protect core modules / 对新代码启用 strict，保护核心模块**

```toml
[tool.pyright]
typeCheckingMode = "standard"

# Force strict for specific directories / 对特定目录强制 strict
strict = ["src/core", "src/api"]
```

Or add a comment at the top of a file / 或在文件顶部添加注释：

```python
# pyright: strict
```

**Step 5: Global strict mode / 全局 strict 模式**

```toml
[tool.pyright]
typeCheckingMode = "strict"
```

---

## VSCode integration (Pylance) / VSCode 集成（Pylance）

pyright is the underlying engine for the VSCode **Pylance extension**; installing Pylance gives you real-time type checking.

> pyright 是 VSCode **Pylance 扩展**的底层引擎，安装 Pylance 后即可获得实时类型检查。

Installation steps / 安装步骤：

1. Search for **Pylance** in the VSCode extension marketplace and install / 在 VSCode 扩展市场搜索 **Pylance** 并安装
2. Open a Python file, select the Python interpreter in the bottom right / 打开 Python 文件，右下角选择 Python 解释器
3. Pylance automatically reads `pyrightconfig.json` or `pyproject.toml` from the project / Pylance 自动读取项目中的配置文件

`.vscode/settings.json` configuration / `.vscode/settings.json` 配置：

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

## pre-commit Hook configuration / pre-commit Hook 配置

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
        pass_filenames: false   # pyright needs to analyze the entire package / pyright 需要分析整个包
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

Install and run / 安装与运行：

```bash
uv add --dev pre-commit
uv run pre-commit install
uv run pre-commit run --all-files
```

---

## Common error types and solutions / 常见报错类型和解决方法

| Error code / 错误代码 | Meaning / 含义 | Solution / 解决方法 |
|----------|------|----------|
| `reportMissingImports` | Module not found / 找不到模块 | Install package or stub; check `venvPath`/`venv` config / 安装包或 stub；检查配置 |
| `reportMissingTypeStubs` | Module has no type stubs / 模块无类型存根 | Install `types-xxx` stub package, or set to `"none"` / 安装 stub 包，或设为 `"none"` |
| `reportUnknownVariableType` | Variable type inferred as Unknown / 变量类型推断为 Unknown | Add type annotation, or set to `"none"` / 添加类型注解，或设为 `"none"` |
| `reportUnknownParameterType` | Function parameter type unknown / 函数参数类型未知 | Add type annotation to parameters / 为参数添加类型注解 |
| `reportReturnType` | Return type mismatch / 返回值类型不匹配 | Fix function return type annotation / 修正函数返回类型注解 |
| `reportAttributeAccessIssue` | Accessing non-existent attribute / 访问不存在的属性 | Check object type, add `hasattr` guard / 检查对象类型，添加守卫 |
| `reportOperatorIssue` | Operator type incompatible / 操作符类型不兼容 | Ensure operand types support the operator / 确保操作数类型支持该操作符 |
| `reportIndexIssue` | Index access type error / 下标访问类型错误 | Check if container type supports the index type / 检查容器类型是否支持该索引类型 |
| `reportArgumentType` | Function argument type mismatch / 函数参数类型不匹配 | Fix argument type or function signature / 修正传参类型或函数签名 |
| `reportCallIssue` | Calling a non-callable object / 调用不可调用对象 | Confirm the object is callable / 确认对象是否为 callable |

Common inline suppression comments / 常用内联抑制注释：

```python
x: int = some_func()  # type: ignore  # mypy-compatible syntax / mypy 兼容写法
x: int = some_func()  # pyright: ignore[reportReturnType]  # pyright precise syntax / pyright 精确写法

# Set checking mode at file top / 文件顶部设置检查模式
# pyright: basic
# pyright: strict
```

---

## uvx run without installation / uvx 无需安装直接运行

```bash
# Check current directory / 检查当前目录
uvx pyright .

# Check src directory / 检查 src 目录
uvx pyright src/

# Specify Python version / 指定 Python 版本
uvx pyright --pythonversion 3.11 src/

# Specify version / 指定版本
uvx pyright@1.1.390 src/
```

Suitable for CI environments or temporary checks without adding pyright to project dependencies.

> 适合 CI 环境或临时检查，无需将 pyright 添加到项目依赖。

---

*Last updated: 2026-04-13 / 最后更新：2026-04-13*
