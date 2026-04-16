# Outerbounds Dependency Management / Outerbounds 依赖管理

> Detailed explanation of Fast Bakery's principles and usage, `@conda`/`@pypi` behavior on Outerbounds, Perimeter Policy impact on dependencies, and custom image workflows.

> 详解 fast-bakery 的原理与使用、`@conda`/`@pypi` 在 Outerbounds 上的行为、Perimeter Policy 对依赖的影响，以及自定义镜像工作流。

Related notes / 相关笔记：[[Metaflow工作流框架]] | [[Outerbounds概览]]

---

## Three Dependency Management Strategies Compared / 三种依赖管理策略对比

Outerbounds supports three container dependency management approaches, each with its own use cases:

> Outerbounds 支持三种容器依赖管理方式，各有适用场景：

| Method / 方式 | Principle / 原理 | Pros / 优点 | Cons / 缺点 | Use Case / 适用场景 |
|------|------|------|------|---------|
| **fast-bakery (@pypi/@conda)** | Platform auto-builds images from dependency declarations / 平台自动按依赖声明实时构建镜像 | No Dockerfile needed, fast iteration, dev-prod consistency / 无需写 Dockerfile、迭代快、开发生产一致 | First build takes a few minutes; may conflict with Perimeter Policy / 首次构建需几分钟；可能与 Perimeter Policy 冲突 | Rapid iteration, experimentation / 快速迭代、实验阶段 |
| **Third-party prebuilt images / 第三方预构建镜像** | Directly reference PyTorch Hub, HuggingFace, etc. official images / 直接引用官方镜像 | Quick start, includes specialized optimizations (CUDA, etc.) / 快速启动、包含专有优化 | Low flexibility, hard to customize, requires trusting third party / 灵活性低、难以定制 | Standard ML framework tasks / 标准 ML 框架任务 |
| **Organization custom private images / 组织自定义私有镜像** | Team maintains and pushes to private registry (ECR, etc.) / 团队维护并推送到私有 Registry | Full control, meets security/compliance requirements / 完全可控、符合安全合规要求 | High maintenance cost, hard to support project-specific deps / 维护成本高 | Production, regulated industries / 生产环境、受监管行业 |

---

## Fast Bakery

### What is Fast Bakery / 什么是 Fast Bakery

Fast Bakery is Outerbounds' proprietary dependency management acceleration system. When you declare `@pypi` or `@conda` dependencies in a Flow and run with `--environment=fast-bakery`, the platform will:

> Fast Bakery 是 Outerbounds 平台特有的依赖管理加速系统。当你在 Flow 中声明 `@pypi` 或 `@conda` 依赖，并使用 `--environment=fast-bakery` 参数运行时，平台会：

1. Analyze each step's dependency declarations / 分析每个 step 的依赖声明
2. Automatically build container images containing those dependencies / 自动构建包含这些依赖的容器镜像
3. Use that image for Kubernetes tasks / 在 Kubernetes 任务中使用该镜像

**Fast Bakery vs traditional conda/pip / Fast Bakery 与传统 conda/pip 的对比：**

> Fast Bakery does not use conda/mamba/micromamba/pip under the hood and is typically 1-2 orders of magnitude faster than conda/mamba/pip.

> Fast bakery 不使用 conda/mamba/micromamba/pip 作为底层，通常比 conda/mamba/pip 快 1-2 个数量级。

### Using Fast Bakery / 使用 Fast Bakery

```bash
# Activate fast-bakery environment during local development
# 本地开发时激活 fast-bakery 环境
python flow.py --environment=fast-bakery run --with kubernetes

# Deploy to production (recommended with fast-bakery)
# 部署到生产（推荐配合 fast-bakery）
python flow.py --environment=fast-bakery argo-workflows create

# Full command with specific compute_pool
# 带具体 compute_pool 的完整命令
python flow.py --environment=fast-bakery run \
  --with kubernetes:compute_pool=ml-training-pool

# Smoke test (quick validation, saves time and cost)
# 冒烟测试（快速验证，节省时间和成本）
python flow.py --environment=fast-bakery run \
  --with kubernetes:compute_pool=small-pool \
  --smoke True
```

---

## `@pypi` Decorator / `@pypi` 装饰器

Declare Python package dependencies at the individual step level:

> 在单个 step 级别声明 Python 包依赖：

```python
from metaflow import FlowSpec, step, pypi

class TrainingFlow(FlowSpec):
    
    @pypi(packages={
        "scikit-learn": "1.3.0",
        "pandas": "2.0.0",
        "numpy": "1.25.0"
    })
    @step
    def train(self):
        from sklearn.ensemble import RandomForestClassifier
        import pandas as pd
        ...
        self.next(self.end)
    
    @step
    def end(self):
        pass
```

**Flow-level `@pypi_base` (shared across all steps) / Flow 级别的 `@pypi_base`（所有 step 共享）：**

```python
from metaflow import FlowSpec, step
from metaflow.decorators import pypi_base

@pypi_base(packages={
    "pandas": "2.0.0",
    "numpy": "1.25.0"
}, python="3.10.0")
class MyFlow(FlowSpec):
    
    @step
    def start(self):
        import pandas as pd  # automatically available / 自动可用
        ...
```

---

## `@conda` Decorator / `@conda` 装饰器

Use conda to manage dependencies (including non-Python packages):

> 使用 conda 管理依赖（包括非 Python 包）：

```python
from metaflow import FlowSpec, step, conda

class NLPFlow(FlowSpec):
    
    @conda(libraries={
        "transformers": "4.30.0",
        "torch": "2.0.1",
        "cuda-toolkit": "11.8"
    }, python="3.10")
    @step
    def embed(self):
        from transformers import AutoTokenizer
        ...
```

> **Behavior on Outerbounds / 在 Outerbounds 上的行为**: `@conda` also supports Fast Bakery acceleration, but conda's package resolution can sometimes be slower than pure pypi. Prefer `@pypi` and use `@conda` only when non-Python binary packages are needed.

> `@conda` 同样支持 fast-bakery 加速，但 conda 的包解析有时比纯 pypi 慢。建议优先使用 `@pypi`，仅在需要非 Python 二进制包时使用 `@conda`。

---

## Perimeter Policy Impact on Dependencies / Perimeter Policy 对依赖的影响

Perimeter Policy can enforce all Flows to use a specific container image, which conflicts with fast-bakery dynamic builds.

> Perimeter Policy 可以强制要求所有 Flow 使用特定的容器镜像，这与 fast-bakery 动态构建存在冲突。

### Conflict Scenario / 冲突场景

```
Perimeter Policy: All Tasks must use <account-id>.dkr.ecr.<region>.amazonaws.com/<org>/ml-base:v2.1

Developer code / 开发者代码：
  @pypi(packages={"custom-lib": "1.0.0"})
  @kubernetes(compute_pool="training")
  def train(self): ...

Result / 结果：Policy takes effect → uses ml-base:v2.1 image → custom-lib unavailable → error
Policy 生效 → 使用 ml-base:v2.1 镜像 → custom-lib 不可用 → 报错
```

### Solutions / 解决方案

**Solution 1: Update the base image / 方案 1：更新基础镜像** (admin adds commonly used packages to the org image)

```dockerfile
# Dockerfile
FROM <account-id>.dkr.ecr.<region>.amazonaws.com/<org>/ml-base:v2.1
RUN pip install custom-lib==1.0.0
# Push as ml-base:v2.2 / 推送为 ml-base:v2.2
```

**Solution 2: Use fast-bakery in dev Perimeter, fixed images in prod Perimeter / 方案 2：在 dev Perimeter 使用 fast-bakery，prod Perimeter 使用固定镜像**

```bash
# Dev environment (no Policy restriction)
# dev 环境（无 Policy 限制）
METAFLOW_PROFILE=dev python flow.py --environment=fast-bakery run --with kubernetes

# Production environment (Policy enforces fixed image)
# production 环境（Policy 强制固定镜像）
METAFLOW_PROFILE=production python flow.py argo-workflows create
# @pypi declarations will be ignored; uses Policy-specified image
# 此时 @pypi 声明会被忽略，使用 Policy 指定的镜像
```

**Solution 3: Use `@kubernetes(image=...)` to explicitly specify / 方案 3：使用 `@kubernetes(image=...)` 显式指定** (requires Policy to allow this image)

```python
@kubernetes(
    image="<account-id>.dkr.ecr.<region>.amazonaws.com/<org>/custom-ml:v1.0",
    compute_pool="training-pool"
)
@step
def train(self):
    ...
```

---

## Custom Docker Image Workflow / 自定义 Docker 镜像工作流

### Building Custom Images / 构建自定义镜像

```dockerfile
# Recommended: use official Python image as base
# 推荐以官方 Python 镜像为基础
FROM python:3.10-slim

# Install system dependencies / 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages / 安装 Python 包
RUN pip install --no-cache-dir \
    metaflow \
    torch==2.0.1 \
    transformers==4.30.0 \
    scikit-learn==1.3.0

# Note: do not set ENTRYPOINT or CMD (Metaflow builds the container command itself)
# 注意：不要设置 ENTRYPOINT 或 CMD（Metaflow 自己构建容器命令）
```

**Build and push (building for Linux on macOS) / 构建和推送（macOS 上为 Linux 构建）：**

```bash
# Must specify platform on macOS / macOS 上必须指定平台
export DOCKER_DEFAULT_PLATFORM=linux/amd64

docker build -t my-ml-image:v1.0 .
docker tag my-ml-image:v1.0 <account-id>.dkr.ecr.<region>.amazonaws.com/ml-images:v1.0

# Push to ECR / 推送到 ECR
aws ecr get-login-password | docker login --username AWS \
  --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/ml-images:v1.0
```

### Using Custom Images in a Flow / 在 Flow 中使用自定义镜像

```python
# Method 1: Specify in decorator / 方式 1：在装饰器中指定
@kubernetes(
    image="<account-id>.dkr.ecr.<region>.amazonaws.com/ml-images:v1.0",
    compute_pool="training-pool",
    gpu=1
)
@step
def train(self):
    ...

# Method 2: Set default image via config file (used by all steps)
# 方式 2：通过配置文件设置默认镜像（所有 step 使用）
# In ~/.metaflowconfig/config.json:
# "METAFLOW_DEFAULT_CONTAINER_IMAGE": "<account-id>.dkr.ecr.<region>.amazonaws.com/ml-images:v1.0"
```

### Using Workstation Image / 使用 Workstation 镜像

When running `--with kubernetes` from a Workstation, the **platform automatically uses the Workstation's image** (no manual specification needed), ensuring dev and cloud execution environments are consistent.

> 当从 Workstation 运行 `--with kubernetes` 时，**平台自动使用 Workstation 的镜像**（无需手动指定），保证开发和云端执行环境一致。

---

## Dependency Management Best Practices / 依赖管理最佳实践

```python
# 1. Use exact version numbers (avoid "latest" for reproducibility)
# 1. 使用精确版本号（避免"最新版"导致的不可复现性）
@pypi(packages={"scikit-learn": "1.3.0"})  # Good / 好
@pypi(packages={"scikit-learn": ""})        # Avoid / 避免

# 2. Put heavyweight deps (PyTorch, etc.) in the base image; lightweight project packages via @pypi
# 2. 将重量级依赖（PyTorch 等）放入基础镜像，轻量级项目包用 @pypi
@kubernetes(image="pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime")
@pypi(packages={"my-project-utils": "0.1.0"})
@step
def train(self):
    import torch  # from base image / 来自基础镜像
    from my_project_utils import ...  # from @pypi / 来自 @pypi

# 3. Use @conda_base/@pypi_base for steps with identical deps to avoid repetition
# 3. 相同依赖的 steps 使用 @conda_base/@pypi_base 避免重复声明
@pypi_base(packages={"pandas": "2.0.0", "numpy": "1.25.0"})
class MyFlow(FlowSpec):
    ...
```

---

## References / 参考资料

- [Managing Dependencies](https://docs.outerbounds.com/outerbounds/managing-dependencies/)
- [Build a Custom Docker Image](https://docs.outerbounds.com/build-custom-image/)
- [Use a Custom Docker Image](https://docs.outerbounds.com/use-custom-image/)
- [Fast Bakery Introduction Blog](https://outerbounds.com/blog/containerize-with-fast-bakery)

*Last updated / 最后更新：2026-04-13*
