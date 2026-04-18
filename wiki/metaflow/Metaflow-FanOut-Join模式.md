# Metaflow Fan-Out/Join 并行数据加载模式

> 来源：通过 lizard 从 Claude 会话蒸馏 · 2026-04-18

## 核心概念

Metaflow 原生支持 DAG 分支，通过 `self.next()` 分发到多个并行 step，再用 `join` step 汇合。这种模式特别适合**多数据源并行加载**场景——每个 step 独立读取一个数据源，join 时合并所有 artifact。

> Metaflow natively supports DAG branching via `self.next()` to fan out to parallel steps, then converge at a `join` step. This pattern is ideal for **parallel multi-source data loading** — each step reads one source independently, then artifacts are merged at the join.

## 基本模式

```python
from metaflow import FlowSpec, step

class ParallelLoadFlow(FlowSpec):

    @step
    def start(self):
        self.next(self.read_source_a, self.read_source_b, self.read_source_c)

    @step
    def read_source_a(self):
        self.df_a = pd.read_parquet("s3://bucket/source_a/")
        self.next(self.join_inputs)

    @step
    def read_source_b(self):
        self.df_b = pd.read_parquet("s3://bucket/source_b/")
        self.next(self.join_inputs)

    @step
    def read_source_c(self):
        self.df_c = pd.read_parquet("s3://bucket/source_c/")
        self.next(self.join_inputs)

    @step
    def join_inputs(self, inputs):
        # merge_artifacts 将所有分支的 artifact 合并到当前 step
        self.merge_artifacts(inputs, include=["df_a", "df_b", "df_c"])
        self.next(self.process)

    @step
    def process(self):
        # 此时 self.df_a, self.df_b, self.df_c 均可用
        merged = pd.merge(self.df_a, self.df_b, on="id")
        self.next(self.end)

    @step
    def end(self):
        pass
```

> The key method is `self.merge_artifacts(inputs, include=[...])` in the join step. It collects specified artifacts from all incoming branches into the current step's namespace.

## 关键细节

### `merge_artifacts` 参数

| 参数 | 说明 |
|------|------|
| `inputs` | join step 的第一个参数（必须），代表所有入边 |
| `include=[]` | 白名单——只合并这些 artifact（推荐用法） |
| `exclude=[]` | 黑名单——合并除此之外的所有 artifact |

> 若不同分支有**同名 artifact 但不同值**，`merge_artifacts` 会抛异常。要么用 `include` 精确指定互不冲突的名称，要么手动遍历 `inputs` 挑选。

### join step 中手动遍历

当需要更复杂的合并逻辑时，可直接遍历 `inputs`：

```python
@step
def join_inputs(self, inputs):
    for inp in inputs:
        if hasattr(inp, "df_a"):
            self.df_a = inp.df_a
        if hasattr(inp, "df_b"):
            self.df_b = inp.df_b

    # 校验数据完整性
    for name in ["df_a", "df_b"]:
        df = getattr(self, name)
        if df.empty:
            raise ValueError(f"{name} is empty — check upstream data")

    self.next(self.process)
```

> When more complex merge logic is needed, iterate over `inputs` directly. Each element is a namespace containing that branch's artifacts.

### 使用 PyArrow S3FileSystem 读取 S3

在 Metaflow step 中直接读 S3 parquet，推荐用 PyArrow `S3FileSystem`：

```python
from pyarrow.fs import S3FileSystem

@step
def read_source(self):
    s3fs = S3FileSystem(role_arn=self.iam_role)
    # 注意：需去掉 s3:// 前缀
    path = self.input_path.replace("s3://", "")
    self.df = pd.read_parquet(path, filesystem=s3fs)
    self.next(self.join_inputs)
```

> PyArrow's `S3FileSystem` + `pd.read_parquet(filesystem=...)` is the preferred pattern for reading S3 data in Metaflow flows. It avoids downloading files to local disk and supports IAM role assumption.

### 在 `@card` 中添加摘要信息

加载数据后，在 step 中附加 Metaflow Card 信息，方便在 UI 中检查：

```python
from metaflow.cards import Markdown

@card
@step
def read_source(self):
    self.df = pd.read_parquet(...)
    current.card.append(Markdown(f"""
    **Source Summary**
    - Rows: {len(self.df)}
    - Columns: {list(self.df.columns)}
    - Unique IDs: {self.df['id'].nunique()}
    """))
    self.next(self.join_inputs)
```

> Metaflow Cards provide built-in visualization in the UI. Append a Markdown summary after loading data to make the flow self-documenting.

## 适用场景

- **ETL pipeline 并行读取多源数据**：nightly metrics + menstrual stats + manifest 等多个 S3 路径
- **模型训练前的特征加载**：并行读取不同特征表，join 后合并为训练集
- **任何需要 I/O 并行化的 DAG**：每个分支独立运行在不同的 Kubernetes pod 上

> Fan-out/join is the natural Metaflow pattern for any DAG where multiple I/O-bound steps can run independently. Each branch runs as a separate task (potentially on separate Kubernetes pods) for true parallelism.

## 注意事项

- join step 的 `inputs` 参数类型在 mypy 中无明确定义，通常标注为 `Any`
- `merge_artifacts` 在 artifact 名冲突时会报错——确保每个分支写入的 artifact 名不重复
- 若某个分支的数据可选（如 "previous assignments" 可能不存在），在该分支 step 中 try/except 并返回空 DataFrame，避免整个 flow 失败

> The `inputs` parameter in join steps has no explicit type in mypy — annotate as `Any`. Ensure artifact names don't collide across branches. Handle optional data sources with try/except to prevent flow failures.

## 相关链接

- [[Metaflow工作流框架]]
- [[Outerbounds-特有装饰器]]
- [[Outerbounds-部署与调度]]
