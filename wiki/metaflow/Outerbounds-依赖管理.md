# Outerbounds Dependency Management / Outerbounds 依赖管理

Detailed explanation of fast-bakery's principles and usage, the behavior of `@conda`/`@pypi` on Outerbounds, the impact of Perimeter Policy on dependencies, and custom image workflows.

> 详解 fast-bakery 的原理与使用、`@conda`/`@pypi` 在 Outerbounds 上的行为、Perimeter Policy 对依赖的影响，以及自定义镜像工作流。

Related: [[Metaflow工作流框架]] | [[Outerbounds概览]]

---

## Comparison of Three Dependency Management Strategies / 三种依赖管理策略对比

Outerbounds supports three container dependency management approaches, each with its applicable scenarios:

> Outerbounds 支持三种容器依赖管理方式，各有适用场景：

| Method / 方式 | Principle / 原理 | Pros / 优点 | Cons / 缺点 | Use Case / 适用场景 |
|------|------|------|------|---------|
| **fast-bakery (`@pypi`/`@conda`)** | Platform automatically builds images in real time based on declared dependencies / 平台自动按依赖声明实时构建镜像 | No Dockerfile needed, fast iteration, dev/prod consistency / 无需写 Dockerfile、迭代快、开发生产一致 | First build takes a few minutes; may conflict with Perimeter Policy / 首次构建需几分钟；可能与 Perimeter Policy 冲突 | Rapid iteration, experimental stage / 快速迭代、实验阶段 |
| **Third-party pre-built images / 第三方预构建镜像** | Reference official images from PyTorch Hub, HuggingFace, etc. directly / 直接引用 PyTorch Hub、HuggingFace 等官方镜像 | Fast startup, includes proprietary optimizations (CUDA, etc.) / 快速启动、包含专有优化（CUDA 等）| Low flexibility, hard to customize, security audit requires trusting third parties / 灵活性低、难以定制、安全审计需信任第三方 | Standard ML framework tasks / 标准 ML 框架任务 |
| **Organization custom private images / 组织自定义私有镜像** | Team maintains and pushes to private registry (ECR, etc.) / 团队维护并推送到私有 Registry（ECR 等）| Fully controlled, meets security compliance / 完全可控、符合安全合规要求 | High maintenance cost, hard to support project-specific dependencies / 维护成本高、难以支持项目特定依赖 | Production, regulated industries / 生产环境、受监管行业 |

---

## Fast Bakery

### What Is Fast Bakery / 什么是 Fast Bakery

Fast Bakery is a dependency management acceleration system unique to the Outerbounds platform. When you declare `@pypi` or `@conda` dependencies in a Flow and run with the `--environment=fast-bakery` flag, the platform will:

> Fast Bakery 是 Outerbounds 平台特有的依赖管理加速系统。当你在 Flow 中声明 `@pypi` 或 `@conda` 依赖，并使用 `--environment=fast-bakery` 参数运行时，平台会：

1. Analyze the dependency declarations for each step / 分析每个 step 的依赖声明
2. Automatically build container images containing those dependencies / 自动构建包含这些依赖的容器镜像
3. Use those images in Kubernetes tasks / 在 Kubernetes 任务中使用该镜像

**Fast Bakery vs. traditional conda/pip:**

> **Fast Bakery 与传统 conda/pip 的对比：**

> Fast bakery does not use conda/mamba/micromamba/pip under the hood, and is generally 1–2 orders of magnitude faster than conda/mamba/pip.

> Fast bakery 不使用 conda/mamba/micromamba/pip 作为底层，通常比 conda/mamba/pip 快 1-2 个数量级。

### Using Fast Bakery / 使用 Fast Bakery

```bash
# Activate fast-bakery environment for local development
python flow.py --environment=fast-bakery run --with kubernetes

# Deploy to production (recommended with fast-bakery)
python flow.py --environment=fast-bakery argo-workflows create

# Full command with a specific compute_pool
python flow.py --environment=fast-bakery run \
  --with kubernetes:compute_pool=ml-training-pool

# Smoke test (quick validation, saves time and cost)
python flow.py --environment=fast-bakery run \
  --with kubernetes:compute_pool=small-pool \
  --smoke True
```

---

## The `@pypi` Decorator / `@pypi` 装饰器

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

**Flow-level `@pypi_base` (shared by all steps):**

> **Flow 级别的 `@pypi_base`（所有 step 共享）：**

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
        import pandas as pd  # automatically available
        ...
```

---

## The `@conda` Decorator / `@conda` 装饰器

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

> **Behavior on Outerbounds**: `@conda` also supports fast-bakery acceleration, but conda package resolution is sometimes slower than pure pypi. It is recommended to use `@pypi` first and only use `@conda` when non-Python binary packages are needed.

> **在 Outerbounds 上的行为**：`@conda` 同样支持 fast-bakery 加速，但 conda 的包解析有时比纯 pypi 慢。建议优先使用 `@pypi`，仅在需要非 Python 二进制包时使用 `@conda`。

---

## Impact of Perimeter Policy on Dependencies / Perimeter Policy 对依赖的影响

Perimeter Policy can force all Flows to use a specific container image, which conflicts with fast-bakery dynamic builds.

> Perimeter Policy 可以强制要求所有 Flow 使用特定的容器镜像，这与 fast-bakery 动态构建存在冲突。

### Conflict Scenario / 冲突场景

```
Perimeter Policy: All Tasks must use <your-registry>/company/ml-base:v2.1

Developer code:
  @pypi(packages={"custom-lib": "1.0.0"})
  @kubernetes(compute_pool="training")
  def train(self): ...

Result: Policy enforced → uses ml-base:v2.1 image → custom-lib unavailable → error
```

### Solutions / 解决方案

**Option 1: Update the base image** (admin adds common packages to the org image)

> **方案 1：更新基础镜像**（管理员将常用包加入组织镜像）

```dockerfile
# Dockerfile
FROM <your-registry>/company/ml-base:v2.1
RUN pip install custom-lib==1.0.0
# Push as ml-base:v2.2
```

**Option 2: Use fast-bakery in the dev Perimeter, use fixed images in the prod Perimeter**

> **方案 2：在 dev Perimeter 使用 fast-bakery，prod Perimeter 使用固定镜像**

```bash
# dev environment (no Policy restriction)
METAFLOW_PROFILE=dev python flow.py --environment=fast-bakery run --with kubernetes

# production environment (Policy enforces fixed image)
METAFLOW_PROFILE=production python flow.py argo-workflows create
# @pypi declarations are ignored here; the Policy-specified image is used
```

**Option 3: Use `@kubernetes(image=...)` to specify explicitly** (Policy must allow that image)

> **方案 3：使用 `@kubernetes(image=...)` 显式指定**（需 Policy 允许该镜像）

```python
@kubernetes(
    image="<your-registry>/company/custom-ml:v1.0",
    compute_pool="training-pool"
)
@step
def train(self):
    ...
```

---

## Custom Docker Image Workflow / 自定义 Docker 镜像工作流

### Building a Custom Image / 构建自定义镜像

```dockerfile
# Recommended: use the official Python image as the base
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir \
    metaflow \
    torch==2.0.1 \
    transformers==4.30.0 \
    scikit-learn==1.3.0

# Note: do not set ENTRYPOINT or CMD (Metaflow constructs the container command itself)
```

**Build and push (building for Linux on macOS):**

> **构建和推送（macOS 上为 Linux 构建）：**

```bash
# Must specify platform on macOS
export DOCKER_DEFAULT_PLATFORM=linux/amd64

docker build -t my-ml-image:v1.0 .
docker tag my-ml-image:v1.0 <your-account-id>.dkr.ecr.<region>.amazonaws.com/ml-images:v1.0

# Push to ECR
aws ecr get-login-password | docker login --username AWS \
  --password-stdin <your-account-id>.dkr.ecr.<region>.amazonaws.com
docker push <your-account-id>.dkr.ecr.<region>.amazonaws.com/ml-images:v1.0
```

### Using a Custom Image in a Flow / 在 Flow 中使用自定义镜像

```python
# Method 1: specify in the decorator
@kubernetes(
    image="<your-account-id>.dkr.ecr.<region>.amazonaws.com/ml-images:v1.0",
    compute_pool="training-pool",
    gpu=1
)
@step
def train(self):
    ...

# Method 2: set a default image in the config file (used by all steps)
# In ~/.metaflowconfig/config.json:
# "METAFLOW_DEFAULT_CONTAINER_IMAGE": "<your-account-id>.dkr.ecr.<region>.amazonaws.com/ml-images:v1.0"
```

### Using the Workstation Image / 使用 Workstation 镜像

When running `--with kubernetes` from a Workstation, the **platform automatically uses the Workstation's image** (no need to specify manually), ensuring consistency between development and cloud execution environments.

> 当从 Workstation 运行 `--with kubernetes` 时，**平台自动使用 Workstation 的镜像**（无需手动指定），保证开发和云端执行环境一致。

---

## Dependency Management Best Practices / 依赖管理最佳实践

```python
# 1. Use exact version numbers (avoid "latest" causing non-reproducibility)
@pypi(packages={"scikit-learn": "1.3.0"})  # good / 好
@pypi(packages={"scikit-learn": ""})        # avoid / 避免

# 2. Put heavyweight dependencies (PyTorch, etc.) in the base image;
#    use @pypi for lightweight project packages
@kubernetes(image="pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime")
@pypi(packages={"my-project-utils": "0.1.0"})
@step
def train(self):
    import torch  # from base image / 来自基础镜像
    from my_project_utils import ...  # from @pypi / 来自 @pypi

# 3. Use @conda_base/@pypi_base for steps with the same dependencies
#    to avoid repeated declarations / 避免重复声明
@pypi_base(packages={"pandas": "2.0.0", "numpy": "1.25.0"})
class MyFlow(FlowSpec):
    ...
```

---

## References / 参考资料

- [Managing Dependencies](https://docs.outerbounds.com/outerbounds/managing-dependencies/)
- [Build a Custom Docker Image](https://docs.outerbounds.com/build-custom-image/)
- [Use a Custom Docker Image](https://docs.outerbounds.com/use-custom-image/)
- [Fast Bakery Blog Introduction](https://outerbounds.com/blog/containerize-with-fast-bakery)

*Last updated: 2026-04-16*
