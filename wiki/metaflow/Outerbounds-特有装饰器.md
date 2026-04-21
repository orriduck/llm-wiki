# Outerbounds-Specific Decorators / Outerbounds 特有装饰器

> Detailed guide to advanced decorators in the Outerbounds/Metaflow ecosystem: `@secrets`, `@checkpoint`, `@model`, `@huggingface_hub`, `@kubernetes` (full parameters), `@gpu_profile`, `@torchrun`, `@metaflow_ray`, `@retry` with usage and code examples.

> 详解 Outerbounds/Metaflow 生态中的高级装饰器：`@secrets`、`@checkpoint`、`@model`、`@huggingface_hub`、`@kubernetes`（完整参数）、`@gpu_profile`、`@torchrun`、`@metaflow_ray`、`@retry` 的用法和代码示例。

Related notes / 相关笔记：[[Metaflow工作流框架]] | [[Outerbounds概览]]

---

## Decorator Installation Summary / 装饰器安装汇总

| Decorator / 装饰器 | Source Package / 来源包 | Install Command / 安装命令 |
|--------|--------|---------|
| `@kubernetes` | `metaflow` (built-in / 内置) | `pip install metaflow` |
| `@secrets` | `metaflow` (built-in / 内置) | `pip install metaflow` |
| `@environment` | `metaflow` (built-in / 内置) | `pip install metaflow` |
| `@checkpoint` | `metaflow-checkpoint` | `pip install metaflow-checkpoint` |
| `@model` | `metaflow-checkpoint` | `pip install metaflow-checkpoint` |
| `@huggingface_hub` | `metaflow-checkpoint` | `pip install metaflow-checkpoint` |
| `@torchrun` | `metaflow-torchrun` | `pip install metaflow-torchrun` |
| `@metaflow_ray` | `metaflow-ray` | `pip install metaflow-ray` |
| `@gpu_profile` | `metaflow-gpu-profile` | Manual copy of `gpu_profile.py` / 手动复制 |
| `@retry` | `metaflow` (built-in / 内置) | `pip install metaflow` |

---

## `@retry` Decorator / `@retry` 装饰器

`@retry` automatically retries a step when it fails due to transient errors (network issues, API timeouts, spot-instance preemptions, etc.).

> `@retry` 在 step 因瞬时错误失败时自动重试（网络问题、API 超时、Spot 实例被抢占等）。

```python
from metaflow import FlowSpec, step, retry

class RobustFlow(FlowSpec):

    @retry(times=3, minutes_between_retries=2)
    @step
    def fetch_data(self):
        # Safe to retry: read-only external call / 可安全重试：只读外部调用
        import requests
        self.data = requests.get("https://api.example.com/data").json()
        self.next(self.end)

    @step
    def end(self):
        print(self.data)
```

| Parameter / 参数 | Type / 类型 | Default / 默认值 | Description / 说明 |
|---|---|---|---|
| `times` | int | 3 | Max retry attempts (not counting the initial attempt) / 最大重试次数（不含首次执行）|
| `minutes_between_retries` | int | 2 | Wait between retries in minutes / 每次重试之间等待的分钟数 |

**When to use `@retry` / 何时使用 `@retry`:**

- Steps that call external APIs or fetch data from S3/GCS/Azure Blob
- Steps that may be killed by spot-instance preemption
- Any step where failure is likely transient and retrying is safe

**When NOT to use `@retry` / 何时不用 `@retry`:**

- Steps with non-idempotent side effects (e.g., sending an email, writing to a database without deduplication)
- Steps where failure indicates a logic bug that retrying will not fix

> **与 `@checkpoint` 配合使用：** `@checkpoint` 保存中间状态，`@retry` 失败重试时自动加载最新 checkpoint，避免长训练任务从头开始。

---

## `@kubernetes` Decorator (Full Parameters) / `@kubernetes` 装饰器（完整参数）

`@kubernetes` submits a step for execution on a Kubernetes cluster.

> `@kubernetes` 将 step 提交到 Kubernetes 集群执行。

### Basic Resource Parameters / 基础资源参数

| Parameter / 参数 | Type / 类型 | Default / 默认值 | Description / 说明 |
|------|------|--------|------|
| `cpu` | int | 1 | CPU cores / CPU 核心数 |
| `memory` | int | 4096 | Memory size in MB / 内存大小（MB） |
| `disk` | int | 10240 | Disk size in MB / 磁盘大小（MB） |
| `gpu` | int | None | Number of GPUs / GPU 数量 |
| `gpu_vendor` | str | env var / 环境变量 | GPU vendor (nvidia/amd) / GPU 供应商 |

### Image Parameters / 镜像参数

| Parameter / 参数 | Type / 类型 | Default / 默认值 | Description / 说明 |
|------|------|--------|------|
| `image` | str | None | Docker image (uses default if unset) / Docker 镜像（未指定则使用默认镜像）|
| `image_pull_policy` | str | env var / 环境变量 | Image pull policy (Always/IfNotPresent/Never) / 镜像拉取策略 |
| `image_pull_secrets` | List[str] | [] | Kubernetes imagePullSecrets |

### Outerbounds-Specific Parameters / Outerbounds 特有参数

| Parameter / 参数 | Type / 类型 | Default / 默认值 | Description / 说明 |
|------|------|--------|------|
| `compute_pool` | str | None | Specify compute pool; uses any accessible pool in Perimeter if unset / 指定计算池；不填则使用 Perimeter 内任意可访问的池 |
| `qos` | str | Burstable | Pod QoS class: Guaranteed / Burstable / BestEffort / Pod QoS 类别 |
| `hostname_resolution_timeout` | int | 600 | Hostname resolution timeout in gang scheduling (seconds) / gang 调度集群中主机名解析超时（秒）|

### Kubernetes Configuration Parameters / Kubernetes 配置参数

| Parameter / 参数 | Type / 类型 | Default / 默认值 | Description / 说明 |
|------|------|--------|------|
| `namespace` | str | env var / 环境变量 | Kubernetes namespace / Kubernetes 命名空间 |
| `service_account` | str | env var / 环境变量 | Kubernetes service account / Kubernetes 服务账号 |
| `secrets` | List[str] | None | Mounted Kubernetes Secrets / 挂载的 Kubernetes Secrets |
| `node_selector` | Dict/str | None | Pod node selector (dict or `key=val,key2=val2`) / Pod 节点选择器 |
| `tolerations` | List[Dict] | [] | Kubernetes Tolerations |
| `labels` | Dict | env var / 环境变量 | Pod Labels |
| `annotations` | Dict | env var / 环境变量 | Pod Annotations |
| `security_context` | Dict | None | Container security context / 容器安全上下文 |

### Storage Parameters / 存储参数

| Parameter / 参数 | Type / 类型 | Default / 默认值 | Description / 说明 |
|------|------|--------|------|
| `use_tmpfs` | bool | False | Enable tmpfs temporary filesystem / 启用 tmpfs 临时文件系统 |
| `tmpfs_tempdir` | bool | True | Point METAFLOW_TEMPDIR to tmpfs / 将 METAFLOW_TEMPDIR 指向 tmpfs |
| `tmpfs_size` | int | 50% of memory | tmpfs size in MiB / tmpfs 大小（MiB）|
| `tmpfs_path` | str | /metaflow_temp | tmpfs mount path / tmpfs 挂载路径 |
| `persistent_volume_claims` | Dict | None | PVC to mount path mapping / PVC 到挂载路径的映射 |
| `shared_memory` | int | None | Shared memory size in MiB / 共享内存大小（MiB）|
| `port` | int | None | Container exposed port / 容器暴露端口 |

### Complete Usage Example / 完整使用示例

```python
from metaflow import FlowSpec, step, kubernetes, resources

class TrainingFlow(FlowSpec):
    
    # Basic usage / 基础用法
    @kubernetes(cpu=4, memory=16000, compute_pool="cpu-pool")
    @step
    def preprocess(self):
        ...
        self.next(self.train)
    
    # GPU training / GPU 训练
    @kubernetes(
        gpu=2,
        memory=32000,
        compute_pool="gpu-a100-pool",
        image="nvcr.io/nvidia/pytorch:23.10-py3"
    )
    @step
    def train(self):
        import torch
        device = torch.device("cuda")
        ...
        self.next(self.end)
    
    # Using PVC persistent storage / 使用 PVC 持久化存储
    @kubernetes(
        cpu=2,
        memory=8000,
        persistent_volume_claims={"my-pvc": "/data"},
        compute_pool="storage-pool"
    )
    @step
    def save_artifacts(self):
        ...
        self.next(self.end)
    
    @step
    def end(self):
        pass
```

---

## `@secrets` Decorator / `@secrets` 装饰器

Injects secrets from AWS Secrets Manager or other secret stores as environment variables.

> 从 AWS Secrets Manager 等密钥存储中注入 secrets 作为环境变量。

```python
from metaflow import FlowSpec, step
# @secrets is built into metaflow (exact import path depends on version)
# @secrets 通过 metaflow 内置提供（具体导入方式需根据版本确认）

class ModelFlow(FlowSpec):
    
    @step
    def start(self):
        import os
        # Secrets are injected as environment variables
        # Secrets 作为环境变量注入
        api_key = os.environ.get("API_KEY")
        ...
```

> **Needs verification / 需要验证**: The exact import path and parameters for `@secrets` (secret_name, sources, etc.) are not fully documented in public docs. It is known to support AWS Secrets Manager. Refer to the Outerbounds UI Secrets configuration page.

> `@secrets` 装饰器的具体导入路径和参数（secret_name、sources 等）在公开文档中没有完整的参数列表。已知其支持 AWS Secrets Manager，建议参考 Outerbounds UI 中的 Secrets 配置页面。

**Injecting via `@environment` (reliable alternative) / 通过 `@environment` 注入（可靠替代方案）：**

```python
from metaflow import FlowSpec, step, environment
import os

class ModelFlow(FlowSpec):
    
    @environment(vars={
        "DB_PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "MODEL_API_KEY": os.environ.get("MODEL_API_KEY", "")
    })
    @kubernetes(compute_pool="inference-pool")
    @step
    def inference(self):
        import os
        db_password = os.environ.get("DB_PASSWORD")
        ...
```

---

## `@checkpoint` Decorator / `@checkpoint` 装饰器

Provides checkpoint/resume capability for long training tasks, preventing progress loss from node failures.

> 为长时间训练任务提供断点续训能力，防止因节点故障丢失进度。

```python
from metaflow import FlowSpec, step, current
from metaflow_extensions.obcheckpoint.plugins.machine_learning_utilities.checkpoints.core import checkpoint

class LLMFineTuneFlow(FlowSpec):
    
    @checkpoint
    @kubernetes(gpu=8, memory=64000, compute_pool="gpu-h100-pool")
    @step
    def train(self):
        import torch
        
        # Check if resuming from a checkpoint
        # 检查是否从 checkpoint 恢复
        if current.checkpoint.is_loaded:
            # Resume from last checkpoint / 从上次 checkpoint 恢复
            checkpoint_dir = current.checkpoint.directory
            model = load_model(checkpoint_dir)
            start_epoch = get_epoch_from_checkpoint(checkpoint_dir)
        else:
            model = initialize_model()
            start_epoch = 0
        
        for epoch in range(start_epoch, 100):
            train_epoch(model, epoch)
            
            # Periodically save checkpoint / 定期保存 checkpoint
            save_model(model, current.checkpoint.directory)
            current.checkpoint.save()  # notify platform to save / 通知平台保存
        
        self.model_path = current.checkpoint.directory
        self.next(self.evaluate)
    
    @step
    def evaluate(self):
        ...
```

**`@checkpoint` Core API / `@checkpoint` 核心 API：**

| API | Description / 说明 |
|-----|------|
| `current.checkpoint.is_loaded` | Whether resumed from a checkpoint (bool) / 是否从 checkpoint 恢复 |
| `current.checkpoint.directory` | Checkpoint file directory path / checkpoint 文件目录路径 |
| `current.checkpoint.save()` | Notify platform to save current checkpoint / 通知平台保存当前 checkpoint |

**Key features / 关键特性：**

- Automatically isolates checkpoints across multiple users (prevents overwriting each other).
- Checkpoint history viewable in the Outerbounds UI.
- Combined with `@retry`, automatically loads the latest checkpoint on task failure and retry.

> - 自动隔离多用户的 checkpoint（防止互相覆盖）
> - Outerbounds UI 中可视化查看 checkpoint 历史
> - 与 `@retry` 配合使用，任务失败重试时自动加载最新 checkpoint

---

## `@model` Decorator / `@model` 装饰器

Provides versioned storage and cross-environment loading for models produced in Flows.

> 为 Flow 中产出的模型提供版本化存储和跨环境加载能力。

```python
from metaflow import FlowSpec, step, current
from metaflow_extensions.obcheckpoint.plugins.machine_learning_utilities.models.core import model

class TrainingFlow(FlowSpec):
    
    @model(load=["pretrained_base"])  # Load model saved by another Flow / 加载其他 Flow 保存的模型
    @kubernetes(gpu=2, compute_pool="gpu-pool")
    @step
    def fine_tune(self):
        # Load pretrained model / 加载预训练模型
        base_model_path = current.model.loaded["pretrained_base"]
        model = load_model(base_model_path)
        
        # Fine-tune / 微调...
        fine_tuned_model = fine_tune(model)
        
        # Save fine-tuned model (auto-versioned)
        # 保存微调后的模型（自动版本化）
        save_model(fine_tuned_model, "/tmp/fine_tuned")
        current.model.save("/tmp/fine_tuned", label="fine_tuned_v1")
        
        self.next(self.end)
    
    @step
    def end(self):
        # self.model_ref automatically becomes an Artifact, referenceable by other Flows
        # self.model_ref 自动成为 Artifact，可被其他 Flow 引用
        pass
```

**Loading models across Flows / 跨 Flow 加载模型：**

```python
from metaflow import Flow, namespace

# Get model reference from the last successful training run
# 获取上一次成功训练的模型引用
namespace("production")
training_run = Flow("TrainingFlow").latest_successful_run
model_ref = training_run.data.model_ref

# Load in an inference Flow / 在推理 Flow 中加载
@model(load={"production_model": model_ref})
@step
def predict(self):
    model_path = current.model.loaded["production_model"]
    model = load_model(model_path)
    ...
```

---

## `@huggingface_hub` Decorator / `@huggingface_hub` 装饰器

Efficiently caches and loads models from HuggingFace Hub, avoiding repeated downloads of large models.

> 高效缓存和加载 HuggingFace Hub 上的模型，避免重复下载大模型。

```python
from metaflow import FlowSpec, step, current
from metaflow_extensions.obcheckpoint.plugins.machine_learning_utilities.hf_hub.core import huggingface_hub

class VideoGenerationFlow(FlowSpec):
    
    @huggingface_hub
    @kubernetes(gpu=4, memory=80000, compute_pool="gpu-a100-pool")
    @step
    def generate(self):
        # Download from HuggingFace Hub (first time) or load from cache (faster on subsequent runs)
        # 从 HuggingFace Hub 下载（首次）或从缓存加载（后续更快）
        model_path = current.huggingface_hub.snapshot_download(
            repo_id="stabilityai/stable-video-diffusion-img2vid",
            # revision="main"  # optionally specify version / 可指定版本
        )
        
        # Use the model / 使用模型
        from diffusers import StableVideoDiffusionPipeline
        pipe = StableVideoDiffusionPipeline.from_pretrained(model_path)
        ...
```

**Core advantages / 核心优势：**

- Models are cached in Outerbounds' optimized data store, **much faster than downloading directly from HuggingFace**.
- Automatic version management; different model versions do not interfere with each other.
- Combines with `@model` decorator to use HuggingFace models as starting points for fine-tuning.

> - 模型缓存在 Outerbounds 的优化数据存储中，**比直接从 HuggingFace 下载快得多**
> - 自动版本管理，不同模型版本互不干扰
> - 与 `@model` 装饰器配合，将 HuggingFace 模型作为起点进行微调

---

## `@torchrun` Decorator / `@torchrun` 装饰器

For multi-node distributed PyTorch training (DDP, FSDP, etc.), automatically configures the network addresses and parameters required by `torchrun`.

> 用于多节点分布式 PyTorch 训练（DDP、FSDP 等），自动配置 `torchrun` 所需的网络地址和参数。

```python
from metaflow import FlowSpec, step, current
from metaflow_extensions.torchrun.plugins.torchrun_decorator import torchrun

class DistributedTrainingFlow(FlowSpec):
    
    @torchrun(nproc_per_node=8)  # 8 GPU processes per node / 每节点 8 个 GPU 进程
    @kubernetes(
        gpu=8,
        memory=320000,
        cpu=64,
        compute_pool="multi-gpu-pool"
    )
    @step
    def train(self):
        # This step launches via torchrun
        # 此 step 以 torchrun 方式启动
        # Network addresses (MASTER_ADDR, MASTER_PORT) are auto-configured
        # 网络地址（MASTER_ADDR、MASTER_PORT）自动配置
        import torch.distributed as dist
        
        dist.init_process_group(backend="nccl")
        rank = dist.get_rank()
        
        # Distributed training logic...
        # 分布式训练逻辑...
        ...

# Multi-node training (num_parallel specifies node count in foreach)
# 多节点训练（num_parallel 在 foreach 中指定节点数）
class MultiNodeFlow(FlowSpec):
    
    @step
    def start(self):
        self.next(self.train, num_parallel=4)  # 4 nodes / 4 个节点
    
    @torchrun(nproc_per_node=8)
    @kubernetes(gpu=8, memory=320000, compute_pool="multi-gpu-pool")
    @step
    def train(self):
        # 4 nodes x 8 GPUs = 32 GPU distributed training
        # 4 节点 x 8 GPU = 32 GPU 分布式训练
        ...
        self.next(self.join)
    
    @step
    def join(self, inputs):
        self.next(self.end)
    
    @step
    def end(self):
        pass
```

**Key features / 关键特性：**

- Automatically derives `nproc_per_node` from the `@kubernetes` decorator's GPU count.
- Network addresses (MASTER_ADDR, MASTER_PORT, WORLD_SIZE, RANK) are auto-injected.
- Supports real-time Runs visualization (view training progress in the Outerbounds UI).
- Integrates with `@checkpoint` for fault-tolerant training.

> - 自动从 `@kubernetes` 装饰器的 GPU 数量推导 `nproc_per_node`
> - 网络地址（MASTER_ADDR、MASTER_PORT、WORLD_SIZE、RANK）自动注入
> - 支持实时 Runs 可视化（在 Outerbounds UI 中查看训练进度）
> - 与 `@checkpoint` 集成实现容错训练

---

## `@metaflow_ray` Decorator / `@metaflow_ray` 装饰器

Integrates the Ray distributed computing framework into Metaflow Flows, launching ephemeral Ray clusters on Kubernetes.

> 将 Ray 分布式计算框架集成到 Metaflow Flow 中，在 Kubernetes 上启动临时 Ray 集群。

```python
from metaflow import FlowSpec, step
from metaflow_extensions.ray.plugins.ray_decorator import metaflow_ray

class RayTrainingFlow(FlowSpec):
    
    @step
    def start(self):
        self.next(self.ray_train, num_parallel=4)  # 4-node Ray cluster / 4 个节点的 Ray 集群
    
    @metaflow_ray(
        # all_nodes_started_timeout=600  # timeout waiting for all nodes to start (seconds)
        #                                # 等待所有节点启动的超时（秒）
    )
    @kubernetes(
        cpu=16,
        memory=64000,
        gpu=4,
        compute_pool="ray-pool"
    )
    @step
    def ray_train(self):
        import ray
        from ray import tune
        
        # Ray cluster is already auto-initialized
        # Ray 集群已自动初始化
        @ray.remote
        def distributed_task(data):
            return process(data)
        
        # Ray Tune hyperparameter search / Ray Tune 超参数搜索
        analysis = tune.run(
            train_fn,
            config={"lr": tune.loguniform(1e-4, 1e-1)},
            num_samples=100
        )
        
        self.best_config = analysis.best_config
        self.next(self.join)
    
    @step
    def join(self, inputs):
        self.next(self.end)
    
    @step
    def end(self):
        pass
```

**`@metaflow_ray` usage limitations / `@metaflow_ray` 使用限制：**

- `num_parallel` must be specified in `self.next()` before the `@metaflow_ray` step.
- A `join` step must follow the `@metaflow_ray` step.
- Install: `pip install metaflow-ray`

> - `num_parallel` 必须在 `@metaflow_ray` step 之前的 `self.next()` 中指定
> - `@metaflow_ray` step 之后必须有对应的 `join` step
> - 安装：`pip install metaflow-ray`

---

## `@gpu_profile` Decorator / `@gpu_profile` 装饰器

Monitors GPU usage and visualizes GPU utilization in Metaflow Cards.

> 监控 GPU 使用情况，在 Metaflow Card 中可视化 GPU 利用率。

**Installation steps (not pip-installed; requires manual copy) / 安装步骤（非 pip 安装，需手动复制）：**

```bash
# 1. Download gpu_profile.py from GitHub
# 1. 从 GitHub 下载 gpu_profile.py
curl -O https://raw.githubusercontent.com/outerbounds/metaflow-gpu-profile/main/gpu_profile.py

# 2. Place it in the same directory as your flow file
# 2. 放到与 flow 文件同一目录
```

**Usage / 使用方式：**

```python
from metaflow import FlowSpec, step
from gpu_profile import gpu_profile  # import from local file / 从本地文件导入

class GPUTrainingFlow(FlowSpec):
    
    @gpu_profile()  # Note: must include parentheses / 注意必须加括号
    @kubernetes(gpu=1, memory=16000, compute_pool="gpu-pool")
    @step
    def train(self):
        import torch
        # GPU utilization is automatically recorded in the Card
        # GPU 利用率会自动记录到 Card 中
        model = train_model()
        ...
```

**Notes / 注意事项：**

- Depends on `nvidia-smi`; only supports NVIDIA GPUs.
- Generated visualization reports are viewed in Metaflow Cards (Outerbounds UI Cards view).
- Recommended for debugging and optimization phases; can be removed in production to reduce overhead.

> - 依赖 `nvidia-smi`，仅支持 NVIDIA GPU
> - 生成的可视化报告在 Metaflow Card 中查看（Outerbounds UI 的 Cards 视图）
> - 建议在调试和优化阶段使用，生产环境可去掉以减少额外开销

---

## Decorator Composition Example / 装饰器组合示例

In real production, multiple decorators are often combined:

> 实际生产中，多个装饰器经常组合使用：

```python
from metaflow import FlowSpec, step, current, schedule, project
from metaflow_extensions.obcheckpoint.plugins.machine_learning_utilities.checkpoints.core import checkpoint
from metaflow_extensions.obcheckpoint.plugins.machine_learning_utilities.hf_hub.core import huggingface_hub

@project(name="llm-finetuning")
@schedule(weekly=True)
class LLMFineTuneFlow(FlowSpec):
    
    @huggingface_hub
    @checkpoint
    @kubernetes(
        gpu=8,
        memory=320000,
        compute_pool="h100-pool",
        qos="Guaranteed"
    )
    @step
    def fine_tune(self):
        # 1. Get base model from HF Hub (cache-accelerated)
        # 1. 从 HF Hub 获取基础模型（缓存加速）
        base_model_path = current.huggingface_hub.snapshot_download(
            repo_id="meta-llama/Llama-2-7b-hf"
        )
        
        # 2. Check if resuming from checkpoint
        # 2. 检查是否需要从 checkpoint 恢复
        if current.checkpoint.is_loaded:
            model = load_checkpoint(current.checkpoint.directory)
        else:
            model = load_base_model(base_model_path)
        
        # 3. Train (periodic checkpointing)
        # 3. 训练（定期 checkpoint）
        for step_num in range(1000):
            train_step(model)
            if step_num % 100 == 0:
                save_state(model, current.checkpoint.directory)
                current.checkpoint.save()
        
        self.next(self.end)
    
    @step
    def end(self):
        pass
```

---

## References / 参考资料

- [@kubernetes API Docs](https://docs.metaflow.org/api/step-decorators/kubernetes)
- [metaflow-checkpoint GitHub](https://github.com/outerbounds/metaflow-checkpoint)
- [metaflow-torchrun GitHub](https://github.com/outerbounds/metaflow-torchrun)
- [metaflow-ray GitHub](https://github.com/outerbounds/metaflow-ray)
- [metaflow-gpu-profile GitHub](https://github.com/outerbounds/metaflow-gpu-profile)
- [Outerbounds Blog: Scale ML/AI Smoothly](https://outerbounds.com/blog/scale-ml-ai-smoothly)
- [Outerbounds Blog: Distributed Training](https://outerbounds.com/blog/distributed-training-with-metaflow)

*Last updated / 最后更新：2026-04-13*
