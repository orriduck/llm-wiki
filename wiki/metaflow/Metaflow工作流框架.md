# Metaflow Workflow Framework / Metaflow 工作流框架

> An open-source ML/data science workflow framework from Netflix. Core design philosophy: **code is the workflow, decorators are infrastructure**. Local development experience and cloud execution are fully unified.

> Netflix 开源的 ML/数据科学工作流框架。核心设计哲学：**代码即流程，装饰器即基础设施**。本地开发体验与云端执行能力完全统一。

## Table of Contents / 目录

- [[#Core Concepts / 核心概念]]
- [[#FlowSpec and Step Details / FlowSpec 与 step 详解]]
- [[#Artifact System / Artifact 系统]]
- [[#Run and Execution Model / Run 与执行模型]]
- [[#Common Decorators Quick Reference / 常用装饰器速查]]
- [[#Local vs Cloud Execution / 本地 vs 云端运行]]
- [[#Metaflow Client API]]
- [[#Development Patterns and Best Practices / 开发模式与最佳实践]]
- [[#Common Pitfalls / 常见陷阱]]

---

## Core Concepts / 核心概念

Metaflow's four fundamental concepts form the backbone of the entire framework.

> Metaflow 的四个基础概念构成整个框架的骨架：

| Concept / 概念 | Definition / 定义 | Analogy / 类比 |
|------|------|------|
| **FlowSpec** | Class definition of a workflow, inheriting from `FlowSpec` / 工作流的类定义，继承自 `FlowSpec` | Blueprint of a flowchart / 流程图的蓝图 |
| **step** | An execution unit in the flow, marked with `@step` / 流程中的一个执行单元，用 `@step` 标记 | A node in a flowchart / 流程图中的节点 |
| **artifact** | A Python object persisted to the datastore after step execution / step 执行后持久化到 datastore 的 Python 对象 | Input/output snapshot of a step / 步骤的输入/输出快照 |
| **run** | A complete execution instance of a FlowSpec / FlowSpec 的一次完整执行实例 | One instantiated run of the blueprint / 蓝图的一次实例化运行 |

### Hierarchy / 关系层次

```
Flow (class definition)
  └── Run (one execution, with a unique run_id)
        └── Step (each @step corresponds to a step instance)
              └── Task (actual execution unit of a step; multiple for foreach)
                    └── Artifact (persisted object produced by a task)
```

### Path Addressing (Pathspec) / 路径寻址（Pathspec）

Metaflow uses slash-separated paths to uniquely identify each object.

> Metaflow 用斜杠分隔的路径唯一标识每个对象：

```
FlowName/run_id/step_name/task_id/artifact_name

# Example / 示例
MyFlow/42/process/1/result
MyFlow/42/foreach_step/[1,2,3]/model
```

---

## FlowSpec and Step Details / FlowSpec 与 step 详解

### Minimal Runnable Example / 最小可运行示例

```python
from metaflow import FlowSpec, step

class LinearFlow(FlowSpec):

    @step
    def start(self):
        self.message = "hello"
        self.next(self.end)

    @step
    def end(self):
        print(self.message)  # artifact automatically passed between steps

if __name__ == "__main__":
    LinearFlow()
```

### Control Flow Types / 控制流类型

Metaflow supports three control flow types, declared via `self.next()`.

> Metaflow 支持三种控制流，通过 `self.next()` 声明：

**1. Linear / 线性**
```python
self.next(self.next_step)
```

**2. Branch — Static Parallelism / 分支 — 静态并行**
```python
# Trigger multiple steps simultaneously, merging at a join step
# 同时触发多个 step，最终在 join step 汇合
@step
def start(self):
    self.next(self.branch_a, self.branch_b)

@step
def branch_a(self):
    self.result_a = compute_a()
    self.next(self.join)

@step
def branch_b(self):
    self.result_b = compute_b()
    self.next(self.join)

@step
def join(self, inputs):
    # inputs is a list containing artifacts from all branches
    # inputs 是包含所有分支 artifact 的列表
    self.merged = [i.result_a for i in inputs if hasattr(i, 'result_a')]
    self.merge_artifacts(inputs, exclude=['result_a', 'result_b'])
    self.next(self.end)
```

**3. foreach — Dynamic Parallelism / foreach — 动态并行**
```python
@step
def start(self):
    self.params = [{'lr': 0.01}, {'lr': 0.001}, {'lr': 0.0001}]
    self.next(self.train, foreach='params')

@step
def train(self):
    # self.input is the current iteration element
    # self.input 是当前迭代的元素
    config = self.input
    self.model = train_model(lr=config['lr'])
    self.next(self.join)

@step
def join(self, inputs):
    best = max(inputs, key=lambda x: x.model.score)
    self.best_model = best.model
    self.next(self.end)
```

### merge_artifacts

The `join` step must explicitly handle artifact conflicts from multiple branches.

> `join` step 必须明确处理来自多个分支的 artifact 冲突：

```python
@step
def join(self, inputs):
    # Automatically merge artifacts shared across all branches with identical values
    # 自动合并所有分支共同拥有且值相同的 artifact
    self.merge_artifacts(inputs)
    
    # Exclude certain artifacts (handle manually)
    # 排除某些 artifact（手动处理）
    self.merge_artifacts(inputs, exclude=['conflict_field'])
    
    # Merge only specific artifacts
    # 只合并特定 artifact
    self.merge_artifacts(inputs, include=['shared_config'])
    self.next(self.end)
```

---

## Artifact System / Artifact 系统

### What is an Artifact / 什么是 Artifact

Any attribute assigned to `self` inside a step method is automatically serialized and stored to the datastore by Metaflow (locally at `~/.metaflow`, or S3 in the cloud).

> 在 step 方法内给 `self` 赋值的任何属性，Metaflow 都会自动序列化并存储到 datastore（本地为 `~/.metaflow`，云端为 S3）。

```python
@step
def process(self):
    self.df = pd.read_parquet("data.parquet")   # artifact: DataFrame
    self.model = train(self.df)                  # artifact: model object
    self.metrics = {"acc": 0.95, "loss": 0.05}  # artifact: dict
    self.next(self.end)
```

### Serialization Mechanism / 序列化机制

| Object Type / 对象类型 | Serialization / 序列化方式 | Notes / 说明 |
|---------|-----------|------|
| Python built-in types / Python 内置类型 | pickle | int, str, list, dict, etc. |
| numpy / pandas | pickle (internally optimized) / pickle（内部优化） | Size limit warnings for large arrays / 大数组有尺寸限制警告 |
| Custom classes / 自定义类 | pickle | Class definition must exist at unpickle time / 需确保 unpickle 时类定义存在 |
| Large objects / 大型对象 | S3 chunked upload / S3 分块上传 | Handled automatically / 自动处理，无需手动干预 |

> **Note / 注意**: The default single artifact size limit is approximately **10 GB** (constrained by pickle and memory). Store S3 paths rather than the objects themselves for very large datasets.

> **注意**：默认单个 artifact 上限约 **10 GB**（受 pickle 和内存限制）。超大数据集应存 S3 路径而非对象本身。

### Accessing Artifacts from Previous Runs (Common Pattern) / 访问上一次 run 的 Artifact（常见模式）

```python
from metaflow import Flow, Run

# Get artifacts from the latest successful run
# 获取最新成功 run 的 artifact
run = Flow('TrainingFlow').latest_successful_run
model = run['train'].task.data.model

# Reference previous run results within a Flow (incremental training scenario)
# 在 Flow 内部引用之前 run 的结果（增量训练场景）
@step
def train(self):
    from metaflow import Flow
    prev_run = Flow('TrainingFlow').latest_successful_run
    prev_model = prev_run['train'].task.data.model
    self.model = fine_tune(prev_model, self.new_data)
    self.next(self.end)
```

---

## Run and Execution Model / Run 与执行模型

### run_id and Reproducibility / run_id 与重现性

Each `python flow.py run` produces a monotonically increasing `run_id` (integer). All artifacts are archived under this ID, enabling full reproduction of any historical execution.

> 每次 `python flow.py run` 都产生一个单调递增的 `run_id`（整数）。所有 artifact 用这个 ID 归档，可完整重现任何历史执行。

```bash
python flow.py run
# Run id is 47

python flow.py run --run-id-file /tmp/run_id.txt
# Write run_id to a file for CI/CD scripts to read
# 将 run_id 写入文件，供 CI/CD 脚本读取
```

### Task Retry and Recovery / Task 的重试与恢复

```bash
# Resume from the failed step instead of starting over
# 从失败的 step 恢复，而不是从头运行
python flow.py resume <failed_run_id>

# Specify which step to restart from
# 指定从哪个 step 重新开始
python flow.py resume <run_id> --origin-run-id <run_id> process
```

---

## Common Decorators Quick Reference / 常用装饰器速查

### @step

The fundamental decorator required for all steps. Usually placed as the **innermost** decorator (closest to the function definition).

> 所有步骤必须有的基础装饰器，通常放在其他装饰器的**最内层**（最靠近函数定义）。

```python
@batch(cpu=4)
@step          # @step must be closest to the function
def process(self):
    ...
```

### @batch

Submits the step for execution on AWS Batch.

> 将 step 提交到 AWS Batch 执行。

```python
from metaflow import batch

@batch(
    cpu=4,              # Number of vCPUs / vCPU 数量
    memory=16000,       # Memory in MB / 内存 MB
    gpu=1,              # Number of GPUs / GPU 数量
    image='python:3.11',# Custom Docker image (ECR URI or public image)
    queue='ml-jobs',    # Specify Batch Job Queue
    execution_role='arn:aws:iam::<account-id>:role/BatchRole',
)
@step
def train(self):
    ...
```

### @resources

Declares resource requirements, more general than `@batch` (also works with `@kubernetes`).

> 声明资源需求，比 `@batch` 更通用（也适用于 `@kubernetes`）。

```python
from metaflow import resources

@resources(cpu=8, memory=32000, disk=50000)
@step
def preprocess(self):
    ...
```

> When `@resources` and `@batch` are used together, `@batch` parameters take higher priority.

> `@resources` 与 `@batch` 同时使用时，`@batch` 的参数优先级更高。

### @conda / @pypi

Isolate step-level Python dependencies without relying on external packages.

> 隔离 step 的 Python 依赖，不依赖环境外的包。

```python
from metaflow import conda, pypi

# Use conda to manage dependencies
# 使用 conda 管理依赖
@conda(libraries={'scikit-learn': '1.3.0', 'pandas': '2.0.0'})
@step
def train(self):
    import sklearn  # version guaranteed
    ...

# Use pypi to manage dependencies (faster, recommended)
# 使用 pypi 管理依赖（更快，推荐）
@pypi(packages={'xgboost': '2.0.0', 'lightgbm': '4.1.0'})
@step
def boost(self):
    import xgboost
    ...
```

> **Best practice / 最佳实践**: `@pypi` installs faster than `@conda`. Prefer `@pypi` and only use `@conda` when non-Python system libraries are needed.

> `@pypi` 比 `@conda` 安装更快，推荐优先使用 `@pypi`，只在需要非 Python 系统库时用 `@conda`。

### @retry

Automatically retries on step failure.

> step 失败时自动重试。

```python
from metaflow import retry

@retry(times=3, minutes_between_retries=2)
@step
def call_api(self):
    # Only use @retry for idempotent operations
    # 幂等操作才应加 @retry
    self.response = requests.get(API_URL).json()
    self.next(self.end)
```

> **Warning / 警告**: Only use `@retry` for idempotent operations. Be cautious with side effects like database writes or sending messages.

> 只对幂等操作使用 `@retry`。写数据库、发消息等副作用操作需谨慎。

### @timeout

Limits the maximum execution time of a step; fails on timeout (use with `@retry`).

> 限制 step 最长执行时间，超时则失败（配合 `@retry` 使用）。

```python
from metaflow import timeout

@timeout(minutes=30)
@retry(times=2)
@step
def long_job(self):
    ...
```

Parameters: choose one of `seconds`, `minutes`, `hours`.

> 参数：`seconds`、`minutes`、`hours` 三选一。

### @catch

Catches step exceptions, allowing the flow to continue without aborting.

> 捕获 step 异常，让流程继续而不中止。

```python
from metaflow import catch

@catch(var='error_msg', print_exception=True)
@step
def risky_step(self):
    result = might_fail()
    self.output = result
    self.next(self.end)

@step
def end(self):
    if self.error_msg:
        # error_msg artifact being set means the previous step failed
        # error_msg artifact 被设置说明上一步失败了
        print(f"risky_step failed: {self.error_msg}")
    else:
        print(f"result: {self.output}")
```

### @parallel (Multi-Node Distributed) / @parallel（多节点分布式）

Used for MPI-style multi-node parallel tasks (e.g., distributed training).

> 用于 MPI 风格的多节点并行任务（如分布式训练）。

```python
from metaflow import parallel, batch

@parallel
@batch(cpu=8, memory=32000, num_parallel=4)  # 4 nodes in parallel / 4 个节点并行
@step
def distributed_train(self):
    # self.parallel.num_nodes == 4
    # self.parallel.node_index == current node index (0-3) / 当前节点编号 (0-3)
    if self.parallel.node_index == 0:
        # Primary node logic / 主节点逻辑
        ...
    self.next(self.end)
```

### foreach (Dynamic Fan-out) / foreach（动态扇出）

`foreach` is not a decorator but a parameter of `self.next()`.

> `foreach` 不是装饰器，而是 `self.next()` 的参数：

```python
@step
def start(self):
    self.configs = [
        {'model': 'xgb', 'n_estimators': 100},
        {'model': 'lgbm', 'n_estimators': 200},
        {'model': 'rf', 'n_estimators': 50},
    ]
    self.next(self.train, foreach='configs')

@step
def train(self):
    cfg = self.input  # current iteration element / 当前迭代的元素
    self.score = run_experiment(cfg)
    self.next(self.join)

@step
def join(self, inputs):
    self.results = [(i.input, i.score) for i in inputs]
    self.best = max(inputs, key=lambda x: x.score).input
    self.next(self.end)
```

### Decorator Stacking Order / 装饰器叠加顺序

When stacking multiple decorators, **execution order is from outer to inner**, but `@step` must be closest to the function.

> 多个装饰器叠加时，**执行顺序从外到内**，但 `@step` 必须紧贴函数：

```python
@batch(cpu=4, memory=8000)    # Outermost: determines where to run / 最外层：决定在哪里运行
@pypi(packages={'torch': '2.1.0'})  # Middle: environment dependencies / 中间层：环境依赖
@retry(times=2)               # Middle: retry logic / 中间层：重试逻辑
@timeout(hours=2)             # Middle: timeout control / 中间层：超时控制
@step                         # Innermost: must be closest to function / 最内层：必须紧贴函数
def train(self):
    ...
```

---

## Local vs Cloud Execution / 本地 vs 云端运行

### Execution Mode Comparison / 运行方式对比

| Dimension / 维度 | Local Execution / 本地运行 | Cloud Execution (AWS Batch) / 云端运行（AWS Batch） |
|------|---------|-------------------|
| **Trigger / 触发方式** | `python flow.py run` | `python flow.py run` (with `@batch` decorator) |
| **Artifact Storage / Artifact 存储** | `~/.metaflow/` | S3 bucket |
| **Compute Resources / 计算资源** | Local CPU/memory / 本机 CPU/内存 | On-demand EC2 instances / 按需启动的 EC2 实例 |
| **Dependency Management / 依赖管理** | Uses current Python env / 使用当前 Python 环境 | `@conda`/`@pypi` auto-install / 自动安装 |
| **Logging / 日志** | Real-time terminal output / 终端实时输出 | CloudWatch Logs |
| **Best for / 适合场景** | Dev/debug, small data / 开发调试、小数据 | Production, large-scale compute / 生产、大规模计算 |

### --with Flag (Temporary Override) / --with 标志（临时覆盖）

```bash
# Force all steps to run on Batch (even without @batch decorator)
# 强制所有 step 在 Batch 上运行（即使没有 @batch 装饰器）
python flow.py run --with batch

# Force all steps to use specific resources
# 强制所有 step 使用特定资源
python flow.py run --with 'batch:cpu=8,memory=32000'

# Run locally but use cloud S3 artifact storage
# 本地运行但使用云端 S3 artifact 存储
python flow.py run --datastore=s3
```

### Environment Isolation Strategy / 环境隔离策略

```bash
# Local: use conda env; Cloud: use @conda decorator
# 本地用 conda 环境，云端用 @conda 装饰器
# Development: activate local conda env and run
# 开发时：本地 conda env 激活后运行
conda activate myenv
python flow.py run

# Production: @conda decorator ensures consistent cloud env
# 生产时：@conda 装饰器确保云端环境一致
@conda(python='3.11', libraries={'pandas': '2.0'})
@step
def process(self):
    ...
```

### Hybrid Mode (Some Steps in Cloud) / 混合模式（部分 step 在云端）

```python
class HybridFlow(FlowSpec):

    @step
    def start(self):
        # Local: lightweight data preparation
        # 本地：轻量级数据准备
        self.s3_path = upload_data_to_s3()
        self.next(self.heavy_compute)

    @batch(cpu=32, memory=128000, gpu=4)
    @pypi(packages={'torch': '2.1.0'})
    @step
    def heavy_compute(self):
        # Cloud: high-resource training
        # 云端：高资源训练
        self.model_path = train_large_model(self.s3_path)
        self.next(self.evaluate)

    @step
    def evaluate(self):
        # Local: lightweight evaluation
        # 本地：轻量级评估
        self.metrics = evaluate_model(self.model_path)
        self.next(self.end)

    @step
    def end(self):
        print(self.metrics)
```

---

## Metaflow Client API

The Client API is used to query historical execution data outside of a Flow. Core use cases: model registry, experiment tracking, data lineage analysis.

> Client API 用于在 Flow 外部查询历史执行数据，核心场景：模型注册、实验追踪、数据血缘分析。

### Core Object Hierarchy / 核心对象层次

```
metaflow.Flow          → corresponds to a FlowSpec class / 对应一个 FlowSpec 类
  metaflow.Run         → one execution / 一次执行
    metaflow.Step      → one step's execution / 一个 step 的执行
      metaflow.Task    → actual task of a step (multiple for foreach) / step 的实际任务（foreach 时有多个）
        metaflow.DataArtifact → a single artifact / 单个 artifact
```

### Basic Queries / 基本查询

```python
from metaflow import Flow, Run, Step, Task, namespace

# List all runs / 列出所有 run
flow = Flow('TrainingFlow')
for run in flow.runs():
    print(run.id, run.finished_at, run.successful)

# Get the latest successful run / 获取最新成功 run
run = Flow('TrainingFlow').latest_successful_run
print(run.id)

# Get a specific run / 获取特定 run
run = Run('TrainingFlow/47')

# Get artifacts from a specific step of a run
# 获取 run 的特定 step 的 artifact
task = run['train'].task          # single task step
model = task.data.model           # .data accesses artifact namespace
metrics = task.data.metrics

# foreach steps have multiple tasks
# foreach step 有多个 task
for task in run['train'].tasks():
    print(task.data.score)
```

### namespace (Multi-User Isolation) / namespace（多用户隔离）

```python
from metaflow import namespace

# Default namespace is "user:<username>"
# 默认 namespace 是 "user:<username>"
namespace('user:alice')   # only see alice's runs / 只看 alice 的 run
namespace(None)           # see all namespaces (global view) / 看所有 namespace（全局视图）
namespace('production')   # custom namespace (common in CI/CD) / 自定义 namespace（CI/CD 中常用）
```

```bash
# Specify namespace at runtime / 运行时指定 namespace
python flow.py run --namespace production
```

### Practical Query Patterns / 实用查询模式

```python
from metaflow import Flow
import pandas as pd

# Collect experiment metrics from all successful runs
# 收集所有成功 run 的实验指标
def collect_experiments(flow_name: str) -> pd.DataFrame:
    flow = Flow(flow_name)
    records = []
    for run in flow.runs():
        if not run.successful:
            continue
        try:
            task = run['train'].task
            records.append({
                'run_id': run.id,
                'finished_at': run.finished_at,
                'accuracy': task.data.metrics['accuracy'],
                'config': task.data.config,
            })
        except Exception:
            pass
    return pd.DataFrame(records)

# Get artifact from the latest run with a specific tag
# 获取最新 run 中特定 tag 的 artifact
def get_model_by_tag(tag: str):
    flow = Flow('TrainingFlow')
    for run in flow.runs():
        if tag in run.tags:
            return run['train'].task.data.model
    raise ValueError(f"No run found with tag {tag}")
```

### Tags (Labeling Runs) / Tags（给 Run 打标签）

```python
# Tag at runtime / 运行时打标签
python flow.py run --tag experiment:v2 --tag baseline

# Tag programmatically (after run completes)
# 程序内打标签（需要在 run 完成后）
from metaflow import Run
run = Run('TrainingFlow/47')
run.add_tag('production-model')
run.remove_tag('draft')

# Query runs with a specific tag
# 查询带特定 tag 的 run
for run in Flow('TrainingFlow').runs('production-model'):
    print(run.id)
```

### Complete Example: Model Service Loading Latest Model / 完整示例：模型服务加载最新模型

```python
from metaflow import Flow, namespace

def load_production_model():
    """Load the latest production model from Metaflow"""
    """从 Metaflow 加载最新生产模型"""
    namespace(None)  # allow cross-user queries / 允许跨用户查询
    
    flow = Flow('TrainingFlow')
    
    # Method 1: find by tag / 方法1：通过 tag 查找
    prod_runs = list(flow.runs('production'))
    if prod_runs:
        run = prod_runs[0]  # runs() returns in reverse chronological order
        return run['train'].task.data.model
    
    # Method 2: latest successful run / 方法2：最近成功 run
    return flow.latest_successful_run['train'].task.data.model
```

---

## Development Patterns and Best Practices / 开发模式与最佳实践

### Pattern 1: Parameter Parameterization / 模式一：Parameter 参数化

```python
from metaflow import FlowSpec, step, Parameter

class ParameterizedFlow(FlowSpec):

    learning_rate = Parameter(
        'lr',
        help='Learning rate for training',
        default=0.001,
        type=float,
    )
    
    model_type = Parameter(
        'model',
        help='Model architecture',
        default='xgb',
    )

    @step
    def start(self):
        print(f"lr={self.learning_rate}, model={self.model_type}")
        self.next(self.train)

    @step
    def train(self):
        self.model = build_model(
            model_type=self.model_type,
            lr=self.learning_rate,
        )
        self.next(self.end)

    @step
    def end(self):
        pass
```

```bash
python flow.py run --lr 0.01 --model lgbm
```

### Pattern 2: IncludeFile for External Files / 模式二：IncludeFile 包含外部文件

```python
from metaflow import FlowSpec, step, IncludeFile

class ConfigFlow(FlowSpec):

    config_file = IncludeFile(
        'config',
        help='YAML config file',
        default='config.yaml',
    )

    @step
    def start(self):
        import yaml
        self.config = yaml.safe_load(self.config_file)
        self.next(self.end)
```

### Pattern 3: Cards Visualization / 模式三：卡片（Cards）可视化

```python
from metaflow import FlowSpec, step, card
from metaflow.cards import Image, Table

class ReportFlow(FlowSpec):

    @card
    @step
    def evaluate(self):
        self.metrics = compute_metrics()
        
        # Add content to card (inside a @card decorated step)
        # 向卡片添加内容（在 @card 装饰的 step 中）
        from metaflow import current
        current.card.append(Table([[k, str(v)] for k, v in self.metrics.items()]))
        self.next(self.end)
```

```bash
# View the card / 查看卡片
python flow.py card view evaluate
```

### Pattern 4: Incremental Training (Referencing Previous Runs) / 模式四：增量训练（引用上次 run）

```python
class IncrementalFlow(FlowSpec):

    @step
    def start(self):
        from metaflow import Flow
        try:
            prev = Flow('IncrementalFlow').latest_successful_run
            self.base_model = prev['train'].task.data.model
            self.is_incremental = True
        except Exception:
            self.base_model = None
            self.is_incremental = False
        self.next(self.train)

    @batch(cpu=8, memory=32000)
    @step
    def train(self):
        if self.is_incremental and self.base_model:
            self.model = fine_tune(self.base_model, new_data())
        else:
            self.model = train_from_scratch(all_data())
        self.next(self.end)
```

### Best Practices Summary / 最佳实践总结

| Principle / 原则 | Practice / 具体做法 |
|------|---------|
| **Keep steps small and idempotent / Step 要小而幂等** | Each step does one thing; safe to retry on failure / 每个 step 做一件事，失败可安全重试 |
| **Avoid storing large files in artifacts / 避免在 artifact 存大文件** | Store S3 paths for data over 1GB / 超过 1GB 的数据存 S3，artifact 只存路径 |
| **Declare dependencies explicitly / 依赖显式声明** | Use `@pypi`/`@conda` for each step needing specific libraries / 每个需要特定库的 step 用 `@pypi`/`@conda` 声明 |
| **Test locally before going to cloud / 本地先跑通再上云** | Use `--max-workers 1` or small datasets for local validation / 用 `--max-workers 1` 或小数据集本地验证逻辑 |
| **Use namespace for environment isolation / 用 namespace 区分环境** | `production` / `staging` / `user:xxx` isolation / 隔离 |
| **Tag important runs / 给重要 run 打 tag** | `run.add_tag('v1.2-candidate')` for easy lookup / 便于查找 |
| **Handle conflicts in join steps / join step 处理冲突** | `merge_artifacts` + manually handle differing fields / 手动处理分支间差异字段 |
| **Use Parameter instead of hard-coding / Parameter 替代硬编码** | Declare all hyperparameters with `Parameter` for reproducibility / 所有超参数用 `Parameter` 声明，保留实验可重现性 |

---

## Common Pitfalls / 常见陷阱

### 1. OOM from Oversized Artifacts / artifact 太大导致 OOM

```python
# Wrong: storing a large DataFrame directly as an artifact
# 错误：直接把大 DataFrame 存为 artifact
@step
def load(self):
    self.df = pd.read_parquet("100GB_file.parquet")  # will OOM

# Correct: store only the S3 path
# 正确：只存 S3 路径
@step
def load(self):
    s3_path = "s3://my-bucket/data/100GB_file.parquet"
    self.data_path = s3_path  # store path only
```

### 2. Missing merge_artifacts in foreach join / foreach 的 join 没有调用 merge_artifacts

```python
# Wrong: forgetting merge_artifacts causes earlier artifacts to be lost
# 错误：忘记 merge_artifacts，之前步骤的 artifact 丢失
@step
def join(self, inputs):
    self.best = max(inputs, key=lambda x: x.score)
    self.next(self.end)  # self.config and other shared artifacts are lost

# Correct / 正确
@step
def join(self, inputs):
    self.best_score = max(i.score for i in inputs)
    self.merge_artifacts(inputs, include=['config', 'dataset_path'])
    self.next(self.end)
```

### 3. Importing Packages Without Declaring Dependencies / 在 step 中 import 包但没有声明依赖

```python
# Wrong: torch exists locally but not in the cloud Batch env
# 错误：本地有 torch，但云端 Batch 环境没有
@batch(cpu=8, gpu=1)
@step
def train(self):
    import torch  # ModuleNotFoundError in Batch env

# Correct: declare with @pypi
# 正确：用 @pypi 声明
@batch(cpu=8, gpu=1)
@pypi(packages={'torch': '2.1.0'})
@step
def train(self):
    import torch
```

### 4. Wrong @step Position / @step 位置错误

```python
# Wrong: @step is not the innermost decorator
# 错误：@step 不在最内层
@step
@batch(cpu=4)
def train(self): ...

# Correct: @step is closest to the function definition
# 正确：@step 紧贴函数定义
@batch(cpu=4)
@step
def train(self): ...
```

### 5. Modifying Class Definitions of Existing Artifacts / 修改已有 artifact 的类定义

If an artifact stores an instance of a custom class and you later modify the class structure, old artifacts may fail to unpickle. Workarounds:

> 如果 artifact 存了一个自定义类的实例，后来修改了这个类的结构，老的 artifact 可能无法 unpickle。避免方法：

- Use standard data structures (dict, list) instead of custom classes for storage
- Or add a `__reduce__` method to custom classes for backward compatibility

> - 用标准数据结构（dict, list）代替自定义类存储数据
> - 或为自定义类添加 `__reduce__` 方法保持向后兼容

---

*Last updated / 最后更新：2026-04-13*
