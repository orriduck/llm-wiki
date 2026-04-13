# Outerbounds 依赖管理

> 详解 fast-bakery 的原理与使用、`@conda`/`@pypi` 在 Outerbounds 上的行为、Perimeter Policy 对依赖的影响，以及自定义镜像工作流。

相关笔记：[[Metaflow工作流框架]] | [[Outerbounds概览]]

---

## 三种依赖管理策略对比

Outerbounds 支持三种容器依赖管理方式，各有适用场景：

| 方式 | 原理 | 优点 | 缺点 | 适用场景 |
|------|------|------|------|---------|
| **fast-bakery（@pypi/@conda）** | 平台自动按依赖声明实时构建镜像 | 无需写 Dockerfile、迭代快、开发生产一致 | 首次构建需几分钟；可能与 Perimeter Policy 冲突 | 快速迭代、实验阶段 |
| **第三方预构建镜像** | 直接引用 PyTorch Hub、HuggingFace 等官方镜像 | 快速启动、包含专有优化（CUDA 等）| 灵活性低、难以定制、安全审计需信任第三方 | 标准 ML 框架任务 |
| **组织自定义私有镜像** | 团队维护并推送到私有 Registry（ECR 等）| 完全可控、符合安全合规要求 | 维护成本高、难以支持项目特定依赖 | 生产环境、受监管行业 |

---

## Fast Bakery

### 什么是 Fast Bakery

Fast Bakery 是 Outerbounds 平台特有的依赖管理加速系统。当你在 Flow 中声明 `@pypi` 或 `@conda` 依赖，并使用 `--environment=fast-bakery` 参数运行时，平台会：

1. 分析每个 step 的依赖声明
2. 自动构建包含这些依赖的容器镜像
3. 在 Kubernetes 任务中使用该镜像

**Fast Bakery 与传统 conda/pip 的对比：**

> Fast bakery 不使用 conda/mamba/micromamba/pip 作为底层，通常比 conda/mamba/pip 快 1-2 个数量级。

### 使用 Fast Bakery

```bash
# 本地开发时激活 fast-bakery 环境
python flow.py --environment=fast-bakery run --with kubernetes

# 部署到生产（推荐配合 fast-bakery）
python flow.py --environment=fast-bakery argo-workflows create

# 带具体 compute_pool 的完整命令
python flow.py --environment=fast-bakery run \
  --with kubernetes:compute_pool=ml-training-pool

# 冒烟测试（快速验证，节省时间和成本）
python flow.py --environment=fast-bakery run \
  --with kubernetes:compute_pool=small-pool \
  --smoke True
```

---

## `@pypi` 装饰器

在单个 step 级别声明 Python 包依赖：

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

**Flow 级别的 `@pypi_base`（所有 step 共享）：**

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
        import pandas as pd  # 自动可用
        ...
```

---

## `@conda` 装饰器

使用 conda 管理依赖（包括非 Python 包）：

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

> **在 Outerbounds 上的行为**：`@conda` 同样支持 fast-bakery 加速，但 conda 的包解析有时比纯 pypi 慢。建议优先使用 `@pypi`，仅在需要非 Python 二进制包时使用 `@conda`。

---

## Perimeter Policy 对依赖的影响

Perimeter Policy 可以强制要求所有 Flow 使用特定的容器镜像，这与 fast-bakery 动态构建存在冲突。

### 冲突场景

```
Perimeter Policy: 所有 Task 必须使用 ecr.amazonaws.com/company/ml-base:v2.1

开发者代码：
  @pypi(packages={"custom-lib": "1.0.0"})
  @kubernetes(compute_pool="training")
  def train(self): ...

结果：Policy 生效 → 使用 ml-base:v2.1 镜像 → custom-lib 不可用 → 报错
```

### 解决方案

**方案 1：更新基础镜像**（管理员将常用包加入组织镜像）

```dockerfile
# Dockerfile
FROM ecr.amazonaws.com/company/ml-base:v2.1
RUN pip install custom-lib==1.0.0
# 推送为 ml-base:v2.2
```

**方案 2：在 dev Perimeter 使用 fast-bakery，prod Perimeter 使用固定镜像**

```bash
# dev 环境（无 Policy 限制）
METAFLOW_PROFILE=dev python flow.py --environment=fast-bakery run --with kubernetes

# production 环境（Policy 强制固定镜像）
METAFLOW_PROFILE=production python flow.py argo-workflows create
# 此时 @pypi 声明会被忽略，使用 Policy 指定的镜像
```

**方案 3：使用 `@kubernetes(image=...)` 显式指定**（需 Policy 允许该镜像）

```python
@kubernetes(
    image="ecr.amazonaws.com/company/custom-ml:v1.0",
    compute_pool="training-pool"
)
@step
def train(self):
    ...
```

---

## 自定义 Docker 镜像工作流

### 构建自定义镜像

```dockerfile
# 推荐以官方 Python 镜像为基础
FROM python:3.10-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 包
RUN pip install --no-cache-dir \
    metaflow \
    torch==2.0.1 \
    transformers==4.30.0 \
    scikit-learn==1.3.0

# 注意：不要设置 ENTRYPOINT 或 CMD（Metaflow 自己构建容器命令）
```

**构建和推送（macOS 上为 Linux 构建）：**

```bash
# macOS 上必须指定平台
export DOCKER_DEFAULT_PLATFORM=linux/amd64

docker build -t my-ml-image:v1.0 .
docker tag my-ml-image:v1.0 123456789.dkr.ecr.us-east-1.amazonaws.com/ml-images:v1.0

# 推送到 ECR
aws ecr get-login-password | docker login --username AWS \
  --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/ml-images:v1.0
```

### 在 Flow 中使用自定义镜像

```python
# 方式 1：在装饰器中指定
@kubernetes(
    image="123456789.dkr.ecr.us-east-1.amazonaws.com/ml-images:v1.0",
    compute_pool="training-pool",
    gpu=1
)
@step
def train(self):
    ...

# 方式 2：通过配置文件设置默认镜像（所有 step 使用）
# ~/.metaflowconfig/config.json 中设置：
# "METAFLOW_DEFAULT_CONTAINER_IMAGE": "123456789.dkr.ecr.../ml-images:v1.0"
```

### 使用 Workstation 镜像

当从 Workstation 运行 `--with kubernetes` 时，**平台自动使用 Workstation 的镜像**（无需手动指定），保证开发和云端执行环境一致。

---

## 依赖管理最佳实践

```python
# 1. 使用精确版本号（避免"最新版"导致的不可复现性）
@pypi(packages={"scikit-learn": "1.3.0"})  # 好
@pypi(packages={"scikit-learn": ""})        # 避免

# 2. 将重量级依赖（PyTorch 等）放入基础镜像，轻量级项目包用 @pypi
@kubernetes(image="pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime")
@pypi(packages={"my-project-utils": "0.1.0"})
@step
def train(self):
    import torch  # 来自基础镜像
    from my_project_utils import ...  # 来自 @pypi

# 3. 相同依赖的 steps 使用 @conda_base/@pypi_base 避免重复声明
@pypi_base(packages={"pandas": "2.0.0", "numpy": "1.25.0"})
class MyFlow(FlowSpec):
    ...
```

---

## 参考资料

- [Managing Dependencies](https://docs.outerbounds.com/outerbounds/managing-dependencies/)
- [Build a Custom Docker Image](https://docs.outerbounds.com/build-custom-image/)
- [Use a Custom Docker Image](https://docs.outerbounds.com/use-custom-image/)
- [Fast Bakery 介绍博客](https://outerbounds.com/blog/containerize-with-fast-bakery)

*最后更新：2026-04-13*
