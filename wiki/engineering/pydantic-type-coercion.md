# Pydantic 类型强制转换与数据管道兼容性

> 来源：通过 lizard 从 Claude 会话蒸馏 · 2026-04-18

## 核心概念

Pydantic `BaseModel` 在验证时会**自动将输入值强制转换为字段声明的类型**。最常见的场景：JSON 字符串 `"2023-11-09"` 被转为 `datetime.date` 对象。这在数据管道中可能导致意外的 schema 变更——上游用字符串，Pydantic 转为 date 对象，写入 Parquet 后列类型改变，下游代码因类型不匹配而出错。

> Pydantic `BaseModel` automatically coerces input values to match field type declarations during validation. The most common case: JSON string `"2023-11-09"` gets parsed into a `datetime.date` object. In data pipelines, this can cause unexpected schema changes — strings become date objects in Parquet, breaking downstream code that expects strings.

## 典型陷阱

```python
from pydantic import BaseModel
import datetime

class Request(BaseModel):
    request_date: datetime.date  # 字符串 → date 对象

# JSON 输入
data = {"request_date": "2023-11-09"}
req = Request.model_validate(data)

type(req.request_date)  # datetime.date，不再是字符串！
```

当 `req.request_date` 被插入 DataFrame 并写入 Parquet 时，列类型从 `string` 变为 `date`。下游代码如 `pd.to_datetime(df["request_date"])` 可能仍然工作，但 `.dt.strftime()` 等操作的行为可能不同。

> When `req.request_date` is inserted into a DataFrame and written to Parquet, the column type changes from `string` to `date`. Downstream code may still work but behave differently — a subtle, hard-to-debug issue.

## `str()` 与 `isoformat()` 行为

```python
import datetime

d = datetime.date(2023, 11, 9)
str(d)           # '2023-11-09'  — 调用 __str__，即 isoformat()
d.isoformat()    # '2023-11-09'  — ISO 8601 格式
repr(d)          # 'datetime.date(2023, 11, 9)'
```

> `str(datetime.date)` calls `__str__()` which is defined in the Python standard library as returning `date.isoformat()` — always `YYYY-MM-DD`. This is guaranteed behavior, not implementation-dependent.

**安全回转方式：** 需要保持字符串类型时，用 `str()` 包装：

```python
df.insert(1, "request_ts", str(req.request_date))
# 列类型保持为 string，值为 "2023-11-09"
```

## Pydantic 常见类型转换表

| 字段类型 | JSON 输入 | Pydantic 输出 | 回转方式 |
|---------|-----------|--------------|---------|
| `datetime.date` | `"2023-11-09"` | `date(2023, 11, 9)` | `str(value)` |
| `datetime.datetime` | `"2023-11-09T10:30:00"` | `datetime(...)` | `value.isoformat()` |
| `int` | `"42"` | `42` | `str(value)` |
| `float` | `"3.14"` | `3.14` | `str(value)` |
| `bool` | `"true"` / `1` | `True` | — |
| `Decimal` | `"99.99"` | `Decimal('99.99')` | `str(value)` |

> Pydantic v2 uses "lax" coercion by default. In strict mode (`model_config = ConfigDict(strict=True)`), strings won't be coerced to dates — validation will fail instead.

## 数据管道最佳实践

1. **明确 Schema 契约**：在管道文档中写明每一列的预期类型（string vs date vs int）
2. **在边界处转换**：Pydantic model → DataFrame 的转换点，显式控制类型
3. **写入前校验列类型**：`assert df["col"].dtype == "object"` 确保是字符串
4. **优先保持原始类型**：如果上下游都期望字符串，从 JSON 直接取原始值而非经过 model

> Best practice: control types explicitly at the Pydantic → DataFrame boundary. If downstream expects strings, either use `str()` on Pydantic fields or extract raw JSON values directly.

```python
# 方式 A：Pydantic model + str() 回转
df["date_col"] = str(model.date_field)

# 方式 B：跳过 Pydantic，直接从 JSON dict 取原始字符串
df["date_col"] = raw_json["date_field"]
```

## Pydantic v1 vs v2 差异

| 行为 | v1 (`parse_obj`) | v2 (`model_validate`) |
|------|-------------------|-----------------------|
| 日期字符串转换 | 自动转为 `date` | 自动转为 `date` |
| 严格模式 | 需 validator | `ConfigDict(strict=True)` |
| 整数字符串转换 | 自动 | 默认自动，strict 模式拒绝 |

> Both v1 and v2 auto-coerce date strings to `datetime.date`. The behavior is consistent; the API names differ (`parse_obj` → `model_validate`).

## 相关链接

- [[mypy]]
- [[pyright]]
