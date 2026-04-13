# pyright

> 微软开发的高性能 Python 静态类型检查器，比 mypy 快 3-5 倍，类型推断更严格，VSCode Pylance 插件的底层引擎。

## pyright 是什么

pyright 是微软用 TypeScript/Node.js 开发的 Python 静态类型检查器，主要特点：

- **极快**：比 mypy 快 3-5 倍，采用懒加载（just-in-time）求值策略
- **严格**：对未标注函数也默认进行检查，类型推断更精确
- **标准兼容**：完整支持最新 Python 类型规范（PEP 526、612、673 等）
- **IDE 集成**：VSCode Pylance 扩展的底层引擎，提供实时类型检查

适合场景：需要严格类型保障的大型代码库、新项目从零开始建立类型安全、从 mypy 迁移寻求更快检查速度。

---

## 安装

```bash
# pip 安装
pip install pyright

# uv 添加为开发依赖（推荐）
uv add --dev pyright

# uvx 无需安装直接运行
uvx pyright .

# npm 全局安装（原生方式，需要 Node.js）
npm install -g pyright
```

pyproject.toml 自动更新：

```toml
[dependency-groups]
dev = [
    "pyright>=1.1",
]
```

注意：pip/uv 安装的 pyright 是 Node.js 版本的封装，底层仍运行 Node.js。

---

## 基本用法

```bash
# 检查当前目录
pyright .

# 检查指定目录
pyright src/

# 检查单个文件
pyright src/my_module/api.py

# 指定配置文件
pyright -p pyrightconfig.json

# 指定 Python 版本
pyright --pythonversion 3.11 src/

# 指定虚拟环境路径
pyright -v .venv src/

# 监听模式（开发时）
pyright --watch src/

# 输出 JSON 格式（CI 解析用）
pyright --outputjson src/

# 通过 uv run
uv run pyright src/

# 通过 uvx（无需安装）
uvx pyright src/
```

---

## 配置：`pyrightconfig.json`

在项目根目录创建 `pyrightconfig.json`：

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

## 配置：`pyproject.toml` 中的 `[tool.pyright]`

推荐将配置集中在 `pyproject.toml`，避免额外文件：

```toml
[tool.pyright]
# 检查范围
include = ["src"]
exclude = [
    "**/node_modules",
    "**/__pycache__",
    "src/migrations",
]
ignore = ["src/legacy"]

# Python 环境
pythonVersion = "3.11"
pythonPlatform = "Linux"

# 虚拟环境（相对于 pyproject.toml 所在目录）
venvPath = "."
venv = ".venv"

# 类型检查严格程度
typeCheckingMode = "standard"   # off | basic | standard | strict

# 自定义规则严格程度（覆盖 typeCheckingMode 的默认值）
reportMissingImports = "error"
reportMissingTypeStubs = "warning"
reportUnknownVariableType = "none"   # 关闭某条规则
```

配置优先级：`pyrightconfig.json` > `pyproject.toml` > VSCode 设置。

---

## typeCheckingMode 说明

| 模式 | 说明 | 适合场景 |
|------|------|----------|
| `off` | 禁用类型检查，仍报告语法错误 | 仅需语法检查 |
| `basic` | 基础检查，宽松 | 旧代码库渐进式引入 |
| `standard` | 标准检查（**默认**） | 大多数项目 |
| `strict` | 严格检查，所有推断未知类型均报错 | 新项目或高类型覆盖率项目 |

各模式在严格程度上逐级递增，`strict` 要求所有函数都有完整类型注解。

---

## 与 mypy 的差异对比

| 维度 | pyright | mypy |
|------|---------|------|
| **实现语言** | TypeScript/Node.js | Python |
| **速度** | 快 3-5 倍（JIT 懒加载） | 较慢（多遍分析） |
| **未注解函数** | **默认检查** | 默认跳过（需 `--check-untyped-defs`） |
| **返回值推断** | 从函数体推断返回类型 | 未注解返回值假设为 `Any` |
| **类型收窄** | 支持 literal equality、成员测试、布尔强制转换 | 支持较少守卫模式 |
| **Union 操作** | 始终用 union（保留类型信息） | 通常用 join（可能丢失类型信息） |
| **实例变量** | 从所有赋值推断联合类型 | 以第一次赋值为准（可能误报） |
| **类变量区分** | 区分纯类变量/实例变量/类实例变量 | 混淆处理 |
| **类装饰器** | 完整支持 | 大部分忽略 |
| **Any vs Unknown** | 区分显式 `Any` 和隐式 `Unknown` | 只跟踪显式 `Any` |
| **插件系统** | 无（设计决策，避免安全/维护问题） | 支持插件 |
| **循环引用** | 部分场景无法解析 | 多遍分析可处理部分循环 |
| **类型注释（# type:）** | 部分支持 | 完整支持 |
| **VSCode 集成** | Pylance（官方） | mypy 扩展（第三方） |

---

## 渐进式类型化策略

从零类型注解到严格类型安全的推荐路径：

**第一步：basic 模式，了解现状**

```toml
[tool.pyright]
include = ["src"]
typeCheckingMode = "basic"
```

```bash
uv run pyright src/  # 查看有多少错误
```

**第二步：修复 import 相关问题**

```toml
[tool.pyright]
typeCheckingMode = "basic"
reportMissingImports = "error"
reportMissingTypeStubs = "warning"
```

安装缺失的 stub 包：

```bash
uv add --dev types-requests types-PyYAML pandas-stubs
```

**第三步：升级到 standard 模式，逐模块收紧**

```toml
[tool.pyright]
typeCheckingMode = "standard"

# 对遗留代码关闭部分规则
reportUnknownVariableType = "none"
reportUnknownParameterType = "none"
```

**第四步：对新代码启用 strict，保护核心模块**

```toml
[tool.pyright]
typeCheckingMode = "standard"

# 对特定目录强制 strict
strict = ["src/core", "src/api"]
```

或在文件顶部添加注释：

```python
# pyright: strict
```

**第五步：全局 strict 模式**

```toml
[tool.pyright]
typeCheckingMode = "strict"
```

---

## VSCode 集成（Pylance）

pyright 是 VSCode **Pylance 扩展**的底层引擎，安装 Pylance 后即可获得实时类型检查。

安装步骤：
1. 在 VSCode 扩展市场搜索 **Pylance** 并安装
2. 打开 Python 文件，右下角选择 Python 解释器
3. Pylance 自动读取项目中的 `pyrightconfig.json` 或 `pyproject.toml`

`.vscode/settings.json` 配置：

```json
{
  "python.languageServer": "Pylance",
  "python.analysis.typeCheckingMode": "standard",
  "python.analysis.autoImportCompletions": true,
  "python.analysis.inlayHints.variableTypes": true,
  "python.analysis.inlayHints.functionReturnTypes": true
}
```

注意：VSCode 中的 `python.analysis.typeCheckingMode` 与 `pyrightconfig.json` 中的 `typeCheckingMode` 效果相同，但 `pyrightconfig.json` 优先级更高。

---

## pre-commit Hook 配置

pyright 无官方 pre-commit 仓库，使用 local hook：

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
        pass_filenames: false   # pyright 需要分析整个包
```

或使用 uvx（无需提前安装）：

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

安装与运行：

```bash
uv add --dev pre-commit
uv run pre-commit install
uv run pre-commit run --all-files
```

---

## 常见报错类型和解决方法

| 错误代码 | 含义 | 解决方法 |
|----------|------|----------|
| `reportMissingImports` | 找不到模块 | 安装包或 stub；检查 `venvPath`/`venv` 配置 |
| `reportMissingTypeStubs` | 模块无类型存根 | 安装 `types-xxx` stub 包，或设为 `"none"` |
| `reportUnknownVariableType` | 变量类型推断为 Unknown | 添加类型注解，或设为 `"none"` |
| `reportUnknownParameterType` | 函数参数类型未知 | 为参数添加类型注解 |
| `reportReturnType` | 返回值类型不匹配 | 修正函数返回类型注解 |
| `reportAttributeAccessIssue` | 访问不存在的属性 | 检查对象类型，添加 `hasattr` 守卫 |
| `reportOperatorIssue` | 操作符类型不兼容 | 确保操作数类型支持该操作符 |
| `reportIndexIssue` | 下标访问类型错误 | 检查容器类型是否支持该索引类型 |
| `reportArgumentType` | 函数参数类型不匹配 | 修正传参类型或函数签名 |
| `reportCallIssue` | 调用不可调用对象 | 确认对象是否为 callable |

常用内联抑制注释：

```python
x: int = some_func()  # type: ignore  # mypy 兼容写法
x: int = some_func()  # pyright: ignore[reportReturnType]  # pyright 精确写法

# 文件顶部设置检查模式
# pyright: basic
# pyright: strict
```

---

## uvx 无需安装直接运行

```bash
# 检查当前目录
uvx pyright .

# 检查 src 目录
uvx pyright src/

# 指定 Python 版本
uvx pyright --pythonversion 3.11 src/

# 指定版本
uvx pyright@1.1.390 src/
```

适合 CI 环境或临时检查，无需将 pyright 添加到项目依赖。

---

*最后更新：2026-04-13*
