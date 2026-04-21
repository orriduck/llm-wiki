# Outerbounds Getting Started: Scale → Environment → Deploy / Outerbounds 入门三部曲：扩展 → 环境 → 部署

> 来源：[First Scale](https://docs.outerbounds.com/outerbounds/first-scale/) · [Define the Environment](https://docs.outerbounds.com/outerbounds/define-environment/) · [First Deploy](https://docs.outerbounds.com/outerbounds/first-deploy/) · 通过 lizard-eat 整理 · 2026-04-20

> This page synthesizes the three official "first steps" tutorials into a single beginner reference. For deep dives, see the linked detailed pages.

> 本页将官方三篇入门教程整合为统一的参考起点。深入细节请查阅各专题页面。

Related notes / 相关笔记：[[Metaflow工作流框架]] | [[Outerbounds概览]] | [[Outerbounds-部署与调度]] | [[Outerbounds-依赖管理]] | [[Outerbounds-特有装饰器]]

---

## The Path: Local → Cloud → Production / 路径：本地 → 云端 → 生产

```
1. python flow.py run                          # local dev, no cloud costs
                                               # 本地开发，不消耗云资源

2. python flow.py run --with kubernetes        # single cloud execution for testing
                                               # 云端单次执行，用于测试

3. python flow.py argo-workflows create        # deploy to production scheduler
   python flow.py argo-workflows trigger       # 部署并触发生产调度
```

This progression is the core Outerbounds workflow. Every section below maps to one step of this path.

> 这个三步路径是 Outerbounds 的核心工作流。以下每节对应路径中的一个环节。

---

## Part 1: Scale — Parallelism and Resources / 第一部分：扩展 — 并行与资源

### `foreach` for Parallel Execution / 用 `foreach` 实现并行

`foreach` spawns one independent task per item in a list — each runs on its own cloud instance simultaneously.

> `foreach` 为列表中的每个元素生成一个独立任务，各任务在独立云实例上并发执行。

```python
from metaflow import FlowSpec, step, resources

class ScalableFlow(FlowSpec):

    @step
    def start(self):
        self.countries = ["us", "uk", "de", "jp"]
        self.next(self.train, foreach="countries")

    @resources(cpu=2, memory=16000)  # 2 CPU cores, 16 GB RAM per task
    @step
    def train(self):
        country = self.input          # current item in the foreach list
        # ... train a model for this country
        self.score = train_model(country)
        self.next(self.join)

    @step
    def join(self, inputs):
        self.best = max(inputs, key=lambda x: x.score)
        self.next(self.end)

    @step
    def end(self):
        print(f"Best model: {self.best.input}")
```

```bash
# Test locally / 本地测试
python scaleflow.py run

# Run all tasks in the cloud in parallel / 云端并行执行所有任务
python scaleflow.py run --with kubernetes
```

### `@resources` Parameters / `@resources` 参数

| Parameter / 参数 | Description / 说明 |
|---|---|
| `cpu` | CPU core count per task / 每个任务的 CPU 核数 |
| `memory` | RAM in MB per task / 每个任务的内存（MB） |
| `gpu` | Number of GPUs / GPU 数量 |
| `disk` | Disk in MB / 磁盘大小（MB） |

`@resources` is a lightweight alias — it applies the same values to `@kubernetes` and `@batch` automatically.

> `@resources` 是轻量别名，其值会自动同步到 `@kubernetes` 和 `@batch` 装饰器。

### Available Compute Pool Types / 可用计算资源类型

Outerbounds clusters unify multiple resource types under one compute interface:

> Outerbounds 集群将多种资源统一纳入同一计算接口：

- AWS / Azure / GCP standard and GPU instances
- NVIDIA DGX Cloud GPUs
- On-premises (on-prem) GPU and CPU nodes

Auto-scaling ensures you pay only when tasks are actively running.

> 自动扩缩容确保只在任务实际运行时才计费。

### Cluster Monitoring / 集群监控

The **Status** view in the Outerbounds UI shows:
- Aggregate CPU/GPU demand across all running tasks
- Real-time instance count changes
- Auto-scaling events triggered by demand spikes

> Outerbounds UI 的 **Status** 视图展示：
> - 所有运行中任务的 CPU/GPU 总需求
> - 实时实例数变化
> - 需求激增时触发的自动扩缩容事件

---

## Part 2: Environment — Dependencies and Docker Images / 第二部分：环境 — 依赖与镜像

### Automatic Code Packaging / 自动代码打包

Metaflow automatically packages your local Python files for cloud execution — no Dockerfile step required for your own code.

> Metaflow 会自动将本地 Python 文件打包到云端，无需为自己的代码手动写 Dockerfile。

Third-party libraries, however, must be provided via one of three strategies (see [[Outerbounds-依赖管理]] for details):

> 但第三方库必须通过以下三种策略之一提供（详见 [[Outerbounds-依赖管理]]）：

1. **`@pypi` / `@conda` + fast-bakery** — declare deps in code, platform builds image automatically
2. **Prebuilt third-party image** — use official images (PyTorch, HuggingFace, etc.)
3. **Custom private image** — organization-maintained image in ECR or other registry

### GPU Example: PyTorch with a Prebuilt Image / GPU 示例：使用预构建镜像运行 PyTorch

```python
from metaflow import FlowSpec, step, resources
from metaflow.profilers import gpu_profile

class TorchTestFlow(FlowSpec):

    @gpu_profile(interval=1)        # visualize GPU utilization in real time / 实时可视化 GPU 利用率
    @resources(gpu=1, memory=16000)
    @step
    def start(self):
        import torch
        x = torch.ones(1000, 1000, device="cuda")
        self.result = (x ** 2).sum().item()
        self.next(self.end)

    @step
    def end(self):
        print(self.result)
```

```bash
# Run locally (CPU only) / 本地运行（纯 CPU）
python torchtest.py run

# Run in the cloud with GPU + PyTorch image (first pull: 5-10 min for ~5-10 GB image)
# 云端 GPU 运行 + PyTorch 镜像（首次拉取约 5-10 GB，需几分钟）
python torchtest.py run \
  --with kubernetes:image=763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-training:2.3.0-gpu-py311-cu121-ubuntu20.04-ec2
```

> **Performance note / 性能说明:** A GPU handles ~74 matrix operations per second vs ~8 on a modern laptop CPU — a ~9× speedup for this type of workload.

> GPU 每秒可处理约 74 次矩阵运算，现代笔记本 CPU 约 8 次——此类负载下约 9× 加速。

---

## Part 3: Deploy — Production Scheduling / 第三部分：部署 — 生产调度

### Key Production Decorators / 核心生产装饰器

```python
from metaflow import FlowSpec, step, project, schedule, retry

@project(name="weather-forecast")   # namespace isolation for team collaboration
                                    # 团队协作的命名空间隔离
@schedule(hourly=True)              # run automatically every hour
                                    # 每小时自动执行
class WeatherFlow(FlowSpec):

    @retry(times=3)                 # retry failed steps up to 3 times
    @step                           # 失败时最多重试 3 次
    def start(self):
        self.data = fetch_weather()
        self.next(self.end)

    @step
    def end(self):
        print(self.data)
```

#### `@retry` Parameters / `@retry` 参数

| Parameter / 参数 | Type / 类型 | Default / 默认值 | Description / 说明 |
|---|---|---|---|
| `times` | int | 3 | Max retry attempts / 最大重试次数 |
| `minutes_between_retries` | int | 2 | Wait between retries (minutes) / 重试间隔（分钟） |

> **When to use / 何时使用:** Apply `@retry` to steps that call external APIs, load data from S3, or do any I/O that can transiently fail. Avoid on steps with side effects that are not idempotent.

> 对调用外部 API、从 S3 加载数据、或存在瞬时失败风险的 I/O 步骤使用 `@retry`。避免用于具有非幂等副作用的步骤。

### Testing Safely Before Production / 生产前安全测试

Metaflow namespaces isolate dev and prod Runs — local runs never pollute the production namespace:

> Metaflow 命名空间隔离开发和生产的 Run，本地运行不会污染生产命名空间：

```bash
# Safe local test with a parameter / 带参数的本地安全测试
python weatherflow.py run --location tokyo

# Results stored under your user namespace (not production)
# 结果存储在你的用户命名空间下（非 production）
```

### Production Deployment Commands / 生产部署命令

```bash
# Deploy to Argo Workflows (creates a Workflow Template)
# 部署到 Argo Workflows（创建 Workflow Template）
python weatherflow.py argo-workflows create

# Deploy as production namespace (isolated from dev runs)
# 部署为 production 命名空间（与开发 Run 隔离）
python weatherflow.py --production argo-workflows create

# Trigger a production run manually (runs independently of your machine)
# 手动触发一次生产 Run（独立于你的本地机器运行）
python weatherflow.py argo-workflows trigger --location "Las Vegas"
```

### Stable Production Environments / 稳定的生产环境

For reproducible production runs, pin dependencies explicitly:

> 为确保生产可复现，显式锁定依赖：

```python
# Option A: @pypi with fast-bakery / 方案 A：@pypi + fast-bakery
@pypi(packages={"requests": "2.31.0", "pandas": "2.0.0"})
@step
def fetch(self): ...

# Option B: custom container image / 方案 B：自定义容器镜像
```

```bash
# Deploy with custom image / 使用自定义镜像部署
python weatherflow.py argo-workflows create \
  --with kubernetes:image=<registry>/<org>/myimage:v1.2
```

### CI/CD (Recommended for Team Workflows) / CI/CD（团队工作流推荐）

Prefer GitHub Actions over manual `argo-workflows create` for production:

> 正式生产环境优先使用 GitHub Actions 而非手动 `argo-workflows create`：

```yaml
# .github/workflows/deploy.yml  (see [[Outerbounds-部署与调度]] for full example)
- name: Deploy to production
  run: python weatherflow.py --production argo-workflows create
```

---

## Quick Reference: Decorator Summary / 速查：装饰器汇总

| Decorator / 装饰器 | Purpose / 用途 | Scope / 作用域 |
|---|---|---|
| `@resources(cpu, memory, gpu)` | Request compute resources / 申请计算资源 | Step |
| `@pypi(packages={...})` | Declare Python deps / 声明 Python 依赖 | Step |
| `@gpu_profile()` | Real-time GPU utilization chart / 实时 GPU 利用率图 | Step |
| `@retry(times=3)` | Auto-retry on transient failure / 瞬时失败自动重试 | Step |
| `@schedule(hourly/daily/cron)` | Time-based trigger / 定时触发 | Flow |
| `@trigger(flow=...)` | Event-based trigger / 事件触发 | Flow |
| `@project(name=...)` | Namespace isolation / 命名空间隔离 | Flow |

---

## 相关链接 / References

- [First Scale](https://docs.outerbounds.com/outerbounds/first-scale/)
- [Define the Environment](https://docs.outerbounds.com/outerbounds/define-environment/)
- [First Deploy](https://docs.outerbounds.com/outerbounds/first-deploy/)
- [[Outerbounds-部署与调度]] — full scheduling & CI/CD details
- [[Outerbounds-依赖管理]] — fast-bakery, @conda/@pypi, custom images
- [[Outerbounds-特有装饰器]] — @checkpoint, @model, @secrets, @torchrun, @metaflow_ray
