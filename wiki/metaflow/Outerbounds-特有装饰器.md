# Outerbounds 特有装饰器

> 详解 Outerbounds/Metaflow 生态中的高级装饰器：`@secrets`、`@checkpoint`、`@model`、`@huggingface_hub`、`@kubernetes`（完整参数）、`@gpu_profile`、`@torchrun`、`@metaflow_ray` 的用法和代码示例。

相关笔记：[[Metaflow工作流框架]] | [[Outerbounds概览]]

---

## 装饰器安装汇总

| 装饰器 | 来源包 | 安装命令 |
|--------|--------|---------|
| `@kubernetes` | `metaflow`（内置）| `pip install metaflow` |
| `@secrets` | `metaflow`（内置）| `pip install metaflow` |
| `@environment` | `metaflow`（内置）| `pip install metaflow` |
| `@checkpoint` | `metaflow-checkpoint` | `pip install metaflow-checkpoint` |
| `@model` | `metaflow-checkpoint` | `pip install metaflow-checkpoint` |
| `@huggingface_hub` | `metaflow-checkpoint` | `pip install metaflow-checkpoint` |
| `@torchrun` | `metaflow-torchrun` | `pip install metaflow-torchrun` |
| `@metaflow_ray` | `metaflow-ray` | `pip install metaflow-ray` |
| `@gpu_profile` | `metaflow-gpu-profile` | 手动复制 `gpu_profile.py` |

---

## `@kubernetes` 装饰器（完整参数）

`@kubernetes` 将 step 提交到 Kubernetes 集群执行。

### 基础资源参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `cpu` | int | 1 | CPU 核心数 |
| `memory` | int | 4096 | 内存大小（MB） |
| `disk` | int | 10240 | 磁盘大小（MB） |
| `gpu` | int | None | GPU 数量 |
| `gpu_vendor` | str | 环境变量 | GPU 供应商（nvidia/amd） |

### 镜像参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `image` | str | None | Docker 镜像（未指定则使用默认镜像）|
| `image_pull_policy` | str | 环境变量 | 镜像拉取策略（Always/IfNotPresent/Never）|
| `image_pull_secrets` | List[str] | [] | Kubernetes imagePullSecrets |

### Outerbounds 特有参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `compute_pool` | str | None | 指定计算池；不填则使用 Perimeter 内任意可访问的池 |
| `qos` | str | Burstable | Pod QoS 类别：Guaranteed / Burstable / BestEffort |
| `hostname_resolution_timeout` | int | 600 | gang 调度集群中主机名解析超时（秒）|

### Kubernetes 配置参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `namespace` | str | 环境变量 | Kubernetes 命名空间 |
| `service_account` | str | 环境变量 | Kubernetes 服务账号 |
| `secrets` | List[str] | None | 挂载的 Kubernetes Secrets |
| `node_selector` | Dict/str | None | Pod 节点选择器（字典或 `key=val,key2=val2`）|
| `tolerations` | List[Dict] | [] | Kubernetes Tolerations |
| `labels` | Dict | 环境变量 | Pod Labels |
| `annotations` | Dict | 环境变量 | Pod Annotations |
| `security_context` | Dict | None | 容器安全上下文 |

### 存储参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `use_tmpfs` | bool | False | 启用 tmpfs 临时文件系统 |
| `tmpfs_tempdir` | bool | True | 将 METAFLOW_TEMPDIR 指向 tmpfs |
| `tmpfs_size` | int | memory 的 50% | tmpfs 大小（MiB）|
| `tmpfs_path` | str | /metaflow_temp | tmpfs 挂载路径 |
| `persistent_volume_claims` | Dict | None | PVC 到挂载路径的映射 |
| `shared_memory` | int | None | 共享内存大小（MiB）|
| `port` | int | None | 容器暴露端口 |

### 完整使用示例

```python
from metaflow import FlowSpec, step, kubernetes, resources

class TrainingFlow(FlowSpec):
    
    # 基础用法
    @kubernetes(cpu=4, memory=16000, compute_pool="cpu-pool")
    @step
    def preprocess(self):
        ...
        self.next(self.train)
    
    # GPU 训练
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
    
    # 使用 PVC 持久化存储
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

## `@secrets` 装饰器

从 AWS Secrets Manager 等密钥存储中注入 secrets 作为环境变量。

```python
from metaflow import FlowSpec, step
# @secrets 通过 metaflow 内置提供（具体导入方式需根据版本确认）

class ModelFlow(FlowSpec):
    
    @step
    def start(self):
        import os
        # Secrets 作为环境变量注入
        api_key = os.environ.get("API_KEY")
        ...
```

> **需要验证**：`@secrets` 装饰器的具体导入路径和参数（secret_name、sources 等）在公开文档中没有完整的参数列表。已知其支持 AWS Secrets Manager，建议参考 Outerbounds UI 中的 Secrets 配置页面。

**通过 `@environment` 注入（可靠替代方案）：**

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

## `@checkpoint` 装饰器

为长时间训练任务提供断点续训能力，防止因节点故障丢失进度。

```python
from metaflow import FlowSpec, step, current
from metaflow_extensions.obcheckpoint.plugins.machine_learning_utilities.checkpoints.core import checkpoint

class LLMFineTuneFlow(FlowSpec):
    
    @checkpoint
    @kubernetes(gpu=8, memory=64000, compute_pool="gpu-h100-pool")
    @step
    def train(self):
        import torch
        
        # 检查是否从 checkpoint 恢复
        if current.checkpoint.is_loaded:
            # 从上次 checkpoint 恢复
            checkpoint_dir = current.checkpoint.directory
            model = load_model(checkpoint_dir)
            start_epoch = get_epoch_from_checkpoint(checkpoint_dir)
        else:
            model = initialize_model()
            start_epoch = 0
        
        for epoch in range(start_epoch, 100):
            train_epoch(model, epoch)
            
            # 定期保存 checkpoint
            save_model(model, current.checkpoint.directory)
            current.checkpoint.save()  # 通知平台保存
        
        self.model_path = current.checkpoint.directory
        self.next(self.evaluate)
    
    @step
    def evaluate(self):
        ...
```

**`@checkpoint` 核心 API：**

| API | 说明 |
|-----|------|
| `current.checkpoint.is_loaded` | 是否从 checkpoint 恢复（bool）|
| `current.checkpoint.directory` | checkpoint 文件目录路径 |
| `current.checkpoint.save()` | 通知平台保存当前 checkpoint |

**关键特性：**
- 自动隔离多用户的 checkpoint（防止互相覆盖）
- Outerbounds UI 中可视化查看 checkpoint 历史
- 与 `@retry` 配合使用，任务失败重试时自动加载最新 checkpoint

---

## `@model` 装饰器

为 Flow 中产出的模型提供版本化存储和跨环境加载能力。

```python
from metaflow import FlowSpec, step, current
from metaflow_extensions.obcheckpoint.plugins.machine_learning_utilities.models.core import model

class TrainingFlow(FlowSpec):
    
    @model(load=["pretrained_base"])  # 加载其他 Flow 保存的模型
    @kubernetes(gpu=2, compute_pool="gpu-pool")
    @step
    def fine_tune(self):
        # 加载预训练模型
        base_model_path = current.model.loaded["pretrained_base"]
        model = load_model(base_model_path)
        
        # 微调...
        fine_tuned_model = fine_tune(model)
        
        # 保存微调后的模型（自动版本化）
        save_model(fine_tuned_model, "/tmp/fine_tuned")
        current.model.save("/tmp/fine_tuned", label="fine_tuned_v1")
        
        self.next(self.end)
    
    @step
    def end(self):
        # self.model_ref 自动成为 Artifact，可被其他 Flow 引用
        pass
```

**跨 Flow 加载模型：**

```python
from metaflow import Flow, namespace

# 获取上一次成功训练的模型引用
namespace("production")
training_run = Flow("TrainingFlow").latest_successful_run
model_ref = training_run.data.model_ref

# 在推理 Flow 中加载
@model(load={"production_model": model_ref})
@step
def predict(self):
    model_path = current.model.loaded["production_model"]
    model = load_model(model_path)
    ...
```

---

## `@huggingface_hub` 装饰器

高效缓存和加载 HuggingFace Hub 上的模型，避免重复下载大模型。

```python
from metaflow import FlowSpec, step, current
from metaflow_extensions.obcheckpoint.plugins.machine_learning_utilities.hf_hub.core import huggingface_hub

class VideoGenerationFlow(FlowSpec):
    
    @huggingface_hub
    @kubernetes(gpu=4, memory=80000, compute_pool="gpu-a100-pool")
    @step
    def generate(self):
        # 从 HuggingFace Hub 下载（首次）或从缓存加载（后续更快）
        model_path = current.huggingface_hub.snapshot_download(
            repo_id="stabilityai/stable-video-diffusion-img2vid",
            # revision="main"  # 可指定版本
        )
        
        # 使用模型
        from diffusers import StableVideoDiffusionPipeline
        pipe = StableVideoDiffusionPipeline.from_pretrained(model_path)
        ...
```

**核心优势：**
- 模型缓存在 Outerbounds 的优化数据存储中，**比直接从 HuggingFace 下载快得多**
- 自动版本管理，不同模型版本互不干扰
- 与 `@model` 装饰器配合，将 HuggingFace 模型作为起点进行微调

---

## `@torchrun` 装饰器

用于多节点分布式 PyTorch 训练（DDP、FSDP 等），自动配置 `torchrun` 所需的网络地址和参数。

```python
from metaflow import FlowSpec, step, current
from metaflow_extensions.torchrun.plugins.torchrun_decorator import torchrun

class DistributedTrainingFlow(FlowSpec):
    
    @torchrun(nproc_per_node=8)  # 每节点 8 个 GPU 进程
    @kubernetes(
        gpu=8,
        memory=320000,
        cpu=64,
        compute_pool="multi-gpu-pool"
    )
    @step
    def train(self):
        # 此 step 以 torchrun 方式启动
        # 网络地址（MASTER_ADDR、MASTER_PORT）自动配置
        import torch.distributed as dist
        
        dist.init_process_group(backend="nccl")
        rank = dist.get_rank()
        
        # 分布式训练逻辑...
        ...

# 多节点训练（num_parallel 在 foreach 中指定节点数）
class MultiNodeFlow(FlowSpec):
    
    @step
    def start(self):
        self.next(self.train, num_parallel=4)  # 4 个节点
    
    @torchrun(nproc_per_node=8)
    @kubernetes(gpu=8, memory=320000, compute_pool="multi-gpu-pool")
    @step
    def train(self):
        # 4 节点 × 8 GPU = 32 GPU 分布式训练
        ...
        self.next(self.join)
    
    @step
    def join(self, inputs):
        self.next(self.end)
    
    @step
    def end(self):
        pass
```

**关键特性：**
- 自动从 `@kubernetes` 装饰器的 GPU 数量推导 `nproc_per_node`
- 网络地址（MASTER_ADDR、MASTER_PORT、WORLD_SIZE、RANK）自动注入
- 支持实时 Runs 可视化（在 Outerbounds UI 中查看训练进度）
- 与 `@checkpoint` 集成实现容错训练

---

## `@metaflow_ray` 装饰器

将 Ray 分布式计算框架集成到 Metaflow Flow 中，在 Kubernetes 上启动临时 Ray 集群。

```python
from metaflow import FlowSpec, step
from metaflow_extensions.ray.plugins.ray_decorator import metaflow_ray

class RayTrainingFlow(FlowSpec):
    
    @step
    def start(self):
        self.next(self.ray_train, num_parallel=4)  # 4 个节点的 Ray 集群
    
    @metaflow_ray(
        # all_nodes_started_timeout=600  # 等待所有节点启动的超时（秒）
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
        
        # Ray 集群已自动初始化
        @ray.remote
        def distributed_task(data):
            return process(data)
        
        # Ray Tune 超参数搜索
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

**`@metaflow_ray` 使用限制：**
- `num_parallel` 必须在 `@metaflow_ray` step 之前的 `self.next()` 中指定
- `@metaflow_ray` step 之后必须有对应的 `join` step
- 安装：`pip install metaflow-ray`

---

## `@gpu_profile` 装饰器

监控 GPU 使用情况，在 Metaflow Card 中可视化 GPU 利用率。

**安装步骤（非 pip 安装，需手动复制）：**

```bash
# 1. 从 GitHub 下载 gpu_profile.py
curl -O https://raw.githubusercontent.com/outerbounds/metaflow-gpu-profile/main/gpu_profile.py

# 2. 放到与 flow 文件同一目录
```

**使用方式：**

```python
from metaflow import FlowSpec, step
from gpu_profile import gpu_profile  # 从本地文件导入

class GPUTrainingFlow(FlowSpec):
    
    @gpu_profile()  # 注意必须加括号
    @kubernetes(gpu=1, memory=16000, compute_pool="gpu-pool")
    @step
    def train(self):
        import torch
        # GPU 利用率会自动记录到 Card 中
        model = train_model()
        ...
```

**注意事项：**
- 依赖 `nvidia-smi`，仅支持 NVIDIA GPU
- 生成的可视化报告在 Metaflow Card 中查看（Outerbounds UI 的 Cards 视图）
- 建议在调试和优化阶段使用，生产环境可去掉以减少额外开销

---

## 装饰器组合示例

实际生产中，多个装饰器经常组合使用：

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
        # 1. 从 HF Hub 获取基础模型（缓存加速）
        base_model_path = current.huggingface_hub.snapshot_download(
            repo_id="meta-llama/Llama-2-7b-hf"
        )
        
        # 2. 检查是否需要从 checkpoint 恢复
        if current.checkpoint.is_loaded:
            model = load_checkpoint(current.checkpoint.directory)
        else:
            model = load_base_model(base_model_path)
        
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

## 参考资料

- [@kubernetes API 文档](https://docs.metaflow.org/api/step-decorators/kubernetes)
- [metaflow-checkpoint GitHub](https://github.com/outerbounds/metaflow-checkpoint)
- [metaflow-torchrun GitHub](https://github.com/outerbounds/metaflow-torchrun)
- [metaflow-ray GitHub](https://github.com/outerbounds/metaflow-ray)
- [metaflow-gpu-profile GitHub](https://github.com/outerbounds/metaflow-gpu-profile)
- [Outerbounds Blog: Scale ML/AI Smoothly](https://outerbounds.com/blog/scale-ml-ai-smoothly)
- [Outerbounds Blog: Distributed Training](https://outerbounds.com/blog/distributed-training-with-metaflow)

*最后更新：2026-04-13*
