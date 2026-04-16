# mypy

> A Python static type checker that detects type errors without running code, supporting gradual typing -- you can incrementally add type annotations from scratch.

> Python 静态类型检查器，在不运行代码的情况下检测类型错误，支持渐进式类型化——可以从零开始逐步为代码添加类型注解。

## Installation / 安装

```bash
# pip
pip install mypy

# Poetry (add to dev group) / Poetry（添加到 dev 组）
poetry add -D mypy

# uv
uv add --dev mypy

# pipx (global install) / pipx（全局安装）
pipx install mypy
```

Verify installation / 验证安装：

```bash
mypy --version
```

---

## Basic usage / 基本用法

```bash
# Check a single file / 检查单个文件
mypy program.py

# Check an entire package (directory) / 检查整个包（目录）
mypy src/my_package/

# Check multiple targets / 检查多个目标
mypy src/ tests/

# Strict mode (enable all optional checks) / 严格模式（启用所有可选检查）
mypy --strict src/

# Specify Python version / 指定 Python 版本
mypy --python-version 3.11 src/

# Ignore missing imports (common when third-party has no stubs)
# 忽略缺失的 import（第三方无 stub 时常用）
mypy --ignore-missing-imports src/
```

---

## Configuration (`[tool.mypy]` in `pyproject.toml`) / 配置（`pyproject.toml` 中的 `[tool.mypy]`）

```toml
[tool.mypy]
# Target Python version / 目标 Python 版本
python_version = "3.11"

# Enable all strict checks (equivalent to enabling many options below)
# 启用所有严格检查（等同于下方多个选项一起开启）
strict = true

# The following are specific options included in strict (can be configured individually)
# 以下是 strict 包含的具体选项（可单独配置）
disallow_untyped_defs = true        # Functions must have type annotations / 函数必须有类型注解
disallow_incomplete_defs = true     # No partial annotations (must be all or none) / 禁止部分注解（必须全注解或全不注解）
disallow_untyped_calls = true       # No calling unannotated functions from typed code / 禁止在类型化代码中调用未注解函数
disallow_any_generics = true        # No bare generics (e.g. list instead of list[int]) / 禁止裸泛型（如 list 而非 list[int]）
check_untyped_defs = true           # Check inside unannotated function bodies / 检查未注解函数体内部
warn_return_any = true              # Warn when returning Any / 返回 Any 时警告
warn_unused_ignores = true          # Warn on invalid # type: ignore / 无效的 # type: ignore 时警告
warn_unused_configs = true          # Warn on unused config sections / 未使用的配置节时警告
no_implicit_reexport = true         # No implicit re-exports / 禁止隐式重导出
strict_equality = true              # Stricter equality checks / 更严格的等号比较检查

# Ignore missing import errors (use per-package override instead)
# 忽略缺失 import 的错误（第三方库无 stub 时使用）
ignore_missing_imports = false      # Recommend keeping false, configure per package / 建议保持 false，按包单独配置

# Show error context / 显示错误上下文
show_error_context = true

# Show error codes (e.g. [attr-defined]) / 显示错误代码（如 [attr-defined]）
show_error_codes = true

# Pretty output / 美化输出
pretty = true

# Cache directory / 缓存目录
cache_dir = ".mypy_cache"
```

### Per-module configuration (overrides global settings) / 按模块单独配置（覆盖全局设置）

```toml
# Ignore import errors for specific third-party libraries
# 对特定第三方库忽略 import 错误
[[tool.mypy.overrides]]
module = "boto3.*"
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = ["cv2", "sklearn.*", "torch.*"]
ignore_missing_imports = true

# Relax requirements for legacy/migrating modules
# 对旧代码/迁移中的模块放宽要求
[[tool.mypy.overrides]]
module = "my_package.legacy.*"
disallow_untyped_defs = false
ignore_errors = true
```

---

## Common type annotation reference / 常用类型注解速查

### Basic types / 基础类型

```python
# Variable annotations / 变量注解
age: int = 25
name: str = "Alice"
price: float = 9.99
active: bool = True
data: bytes = b"hello"

# Function annotations / 函数注解
def greet(name: str) -> str:
    return f"Hello, {name}"

def process(items: list[str]) -> None:
    for item in items:
        print(item)
```

### Optional and Union / Optional 和 Union

```python
from typing import Optional, Union

# Optional (can be None) / Optional（可为 None）
def find_user(user_id: int) -> Optional[str]:
    ...

# Python 3.10+ syntax (recommended) / Python 3.10+ 语法（推荐）
def find_user(user_id: int) -> str | None:
    ...

# Union (multiple types) / Union（多种类型）
def process(value: Union[int, str]) -> str:
    return str(value)

# Python 3.10+ syntax / Python 3.10+ 语法
def process(value: int | str) -> str:
    return str(value)
```

### Collection types / 集合类型

```python
# Python 3.9+ can use built-in types directly
# Python 3.9+ 可直接使用内置类型
names: list[str] = ["Alice", "Bob"]
scores: dict[str, int] = {"Alice": 95}
tags: set[str] = {"python", "typing"}
point: tuple[int, int] = (1, 2)
coords: tuple[float, ...] = (1.0, 2.0, 3.0)  # Any length / 任意长度

# Python 3.8 and earlier require imports from typing
# Python 3.8 及更早需从 typing 导入
from typing import List, Dict, Set, Tuple
names: List[str] = ["Alice"]
```

### Callable

```python
from collections.abc import Callable

# Function that takes (int, str) and returns bool
# 接受 (int, str) 返回 bool 的函数
handler: Callable[[int, str], bool]

# Function with any arguments / 任意参数的函数
callback: Callable[..., None]
```

### TypeVar -- Generic functions / 泛型函数

```python
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T:
    return items[0]

# Constrained TypeVar / 带约束的 TypeVar
NumberT = TypeVar("NumberT", int, float)

def double(x: NumberT) -> NumberT:
    return x * 2
```

### Protocol -- Structural subtyping / 结构子类型

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None:
        ...

def render(obj: Drawable) -> None:
    obj.draw()

# Any class with a draw() method satisfies Drawable, no inheritance needed
# 任何有 draw() 方法的类都满足 Drawable，无需继承
```

### TypedDict -- Typed dictionaries / 有类型的字典

```python
from typing import TypedDict

class UserDict(TypedDict):
    name: str
    age: int
    email: str

# Optional keys / 可选键
class ConfigDict(TypedDict, total=False):
    debug: bool
    timeout: int

user: UserDict = {"name": "Alice", "age": 25, "email": "a@example.com"}
```

### Other common types / 其他常用类型

```python
from typing import Any, cast, TYPE_CHECKING
from typing import ClassVar, Final

# Any: accepts any type (use sparingly) / Any：接受任意类型（慎用）
value: Any = get_dynamic_value()

# Final: constant that cannot be reassigned / Final：不可重新赋值的常量
MAX_SIZE: Final = 100

# ClassVar: class variable (not instance variable) / ClassVar：类变量（不是实例变量）
class Config:
    debug: ClassVar[bool] = False

# cast: manually override type inference (does nothing at runtime)
# cast：手动覆盖类型推断（运行时不做任何事）
items = cast(list[str], get_items())

# TYPE_CHECKING: import only during type checking (avoids circular imports)
# TYPE_CHECKING：只在类型检查时导入（避免循环导入）
if TYPE_CHECKING:
    from my_module import SomeClass
```

---

## Stub package installation / Stub 包安装

When third-party libraries don't have built-in type annotations, you need to install corresponding stub packages:

> 当第三方库没有内置类型注解时，需要安装对应的 stub 包：

```bash
# Common stub packages / 常见 stub 包
pip install types-requests       # requests
pip install types-PyYAML         # pyyaml
pip install types-boto3          # boto3
pip install types-redis          # redis
pip install types-Pillow         # Pillow
pip install types-python-dateutil  # dateutil

# Search for available stub packages / 查找可用 stub 包
pip install types-  # Tab-complete to see options / 输入后 Tab 补全查看可选项
```

You can also let `mypy` suggest installations:

> 也可以用 `mypy` 提示安装：

```bash
$ mypy src/
src/api.py:3: error: Library stubs not installed for "yaml"
note: Hint: "python3 -m pip install types-PyYAML"
```

Add stub packages as dev dependencies in `pyproject.toml`:

> 在 `pyproject.toml` 中将 stub 包添加为 dev 依赖：

```toml
[dependency-groups]
dev = [
    "mypy>=1.0",
    "types-requests",
    "types-PyYAML",
]
```

---

## Gradual typing strategy / 渐进式类型化策略

Migrate from loose to strict gradually, avoiding large changes all at once.

> 从宽松到严格逐步迁移，避免一次性引入大量改动。

### Phase 1: Loose mode (starting point) / 阶段一：宽松模式（起点）

```toml
[tool.mypy]
python_version = "3.11"
ignore_missing_imports = true
# Only check annotated functions / 只检查有注解的函数
check_untyped_defs = false
```

### Phase 2: Begin requiring annotations / 阶段二：开始要求注解

```toml
[tool.mypy]
python_version = "3.11"
ignore_missing_imports = true
check_untyped_defs = true          # Check function bodies (even without annotations) / 检查函数体（即使没注解）
warn_return_any = true
```

### Phase 3: Enforce annotations / 阶段三：强制注解

```toml
[tool.mypy]
python_version = "3.11"
disallow_untyped_defs = true       # Functions must have annotations / 函数必须有注解
check_untyped_defs = true
warn_return_any = true
warn_unused_ignores = true

# Relax for legacy code modules / 对旧代码模块放宽
[[tool.mypy.overrides]]
module = "my_package.legacy.*"
disallow_untyped_defs = false
```

### Phase 4: Strict mode (goal) / 阶段四：严格模式（目标）

```toml
[tool.mypy]
python_version = "3.11"
strict = true

# Still need per-package config for third-party libs without stubs
# 仍需为无 stub 的第三方库单独配置
[[tool.mypy.overrides]]
module = ["boto3.*", "botocore.*"]
ignore_missing_imports = true
```

---

## Common errors and solutions / 常见报错和解决方法

| Error message / 错误信息 | Cause / 原因 | Solution / 解决方法 |
|----------|------|----------|
| `error: Library stubs not installed for "xxx"` | Third-party lib has no type info / 第三方库无类型信息 | `pip install types-xxx` or set `ignore_missing_imports = true` in overrides / 或在 overrides 中设置 |
| `error: Function is missing a return type annotation` | Function lacks return type / 函数缺少返回值注解 | Add `-> ReturnType` or `-> None` / 添加 `-> ReturnType` 或 `-> None` |
| `error: Incompatible types in assignment` | Type mismatch / 类型不匹配 | Check assignment type, may need cast or type narrowing / 检查赋值类型，可能需要 cast 或收窄类型 |
| `error: Item "None" of "Optional[X]" has no attribute "y"` | None not checked before access / None 未检查就访问属性 | Add `if obj is not None:` check first / 先检查 |
| `error: Argument 1 to "f" has incompatible type "X"; expected "Y"` | Parameter type mismatch / 参数类型不匹配 | Fix type annotation or convert at call site / 修正类型注解或调用时转换类型 |
| `error: Cannot determine type of "x"` | Variable type cannot be inferred / 变量类型无法推断 | Add explicit type annotation / 显式添加类型注解 |

### Temporarily ignore specific errors / 临时忽略特定错误

```python
x = some_untyped_function()  # type: ignore[no-untyped-call]
value: str = some_any_value  # type: ignore[assignment]
```

---

## pre-commit Hook configuration / pre-commit Hook 配置

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.11.0
    hooks:
      - id: mypy
        args: ["--strict", "--ignore-missing-imports"]
        additional_dependencies:
          - "types-requests"
          - "types-PyYAML"
```

Note: mypy needs access to project dependencies for correct checking. It's usually recommended to use `uv run mypy` directly rather than the pre-commit mirror (see [[mypy-uv]]).

> 注意：mypy 需要访问项目依赖才能正确检查，通常推荐直接用 `uv run mypy` 而非 pre-commit mirror（见 [[mypy-uv]]）。

---

*Last updated: 2026-04-13 / 最后更新：2026-04-13*
