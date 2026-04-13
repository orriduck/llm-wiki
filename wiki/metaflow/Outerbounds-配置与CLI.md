# Outerbounds 配置与 CLI

> 涵盖 `~/.metaflowconfig` 完整字段（Outerbounds 版本）、多 profile 管理、`outerbounds` CLI 所有已知命令、`METAFLOW_PROFILE` 环境变量用法。

相关笔记：[[Metaflow工作流框架]] | [[Outerbounds概览]]

---

## 配置文件位置与结构

Metaflow（包括 Outerbounds）的配置存储在 `~/.metaflowconfig/` 目录下：

```
~/.metaflowconfig/
├── config.json           # 默认配置（等同于 config_default.json）
├── config_default.json   # 等同于 config.json
├── config_ob.json        # 名为 "ob" 的 profile
├── config_production.json # 名为 "production" 的 profile
└── config_dev.json        # 名为 "dev" 的 profile
```

**profile 激活规则：**
- 未指定 profile：使用 `config.json` 或 `config_default.json`
- 指定 profile：使用 `config_<profile_name>.json`
- 环境变量 > 配置文件（同名环境变量会覆盖配置文件中的值）

---

## `~/.metaflowconfig` 配置字段（Outerbounds 版本）

Outerbounds 通过 `outerbounds configure` 命令自动写入以下字段：

### 核心连接字段

| 字段名 | 说明 | 示例值 |
|--------|------|--------|
| `METAFLOW_SERVICE_URL` | Outerbounds 元数据服务 URL | `https://perimeter-xyz.ob.api.outerbounds.com/` |
| `METAFLOW_SERVICE_AUTH_KEY` | 认证 token（PAT）| `ob_xxxxxxxxxxxxxxxx` |
| `METAFLOW_DEFAULT_METADATA` | 元数据后端类型 | `service` |

### 数据存储字段

| 字段名 | 说明 | 示例值 |
|--------|------|--------|
| `METAFLOW_DATASTORE_SYSROOT_S3` | S3 数据根目录 | `s3://my-bucket/metaflow/` |
| `METAFLOW_DATASTORE_SYSROOT_GS` | GCS 数据根目录（GCP 部署）| `gs://my-bucket/metaflow/` |
| `METAFLOW_DATASTORE_SYSROOT_AZURE` | Azure Blob 数据根目录 | `az://container/metaflow/` |
| `METAFLOW_DEFAULT_DATASTORE` | 默认数据存储类型 | `s3` / `gs` / `azure` |

### Kubernetes 相关字段

| 字段名 | 说明 | 示例值 |
|--------|------|--------|
| `METAFLOW_KUBERNETES_NAMESPACE` | 默认 Kubernetes 命名空间 | `metaflow` |
| `METAFLOW_KUBERNETES_SERVICE_ACCOUNT` | Kubernetes 服务账号 | `metaflow-sa` |
| `METAFLOW_DEFAULT_CONTAINER_IMAGE` | 默认容器镜像 | `123456789.dkr.ecr.us-east-1.amazonaws.com/ml-base:v1` |
| `METAFLOW_DEFAULT_CONTAINER_REGISTRY` | 默认容器 Registry | `123456789.dkr.ecr.us-east-1.amazonaws.com` |
| `METAFLOW_KUBERNETES_TOLERATIONS` | 默认 Tolerations（JSON） | `[{"key":"...","operator":"..."}]` |
| `METAFLOW_KUBERNETES_LABELS` | 默认 Pod Labels（JSON） | `{"team":"ml","env":"prod"}` |
| `METAFLOW_KUBERNETES_ANNOTATIONS` | 默认 Pod Annotations（JSON）| `{"iam.amazonaws.com/role":"..."}` |

### Argo Workflows 字段

| 字段名 | 说明 | 示例值 |
|--------|------|--------|
| `METAFLOW_ARGO_WORKFLOWS_KUBERNETES_NAMESPACE` | Argo 命名空间 | `argo` |
| `METAFLOW_ARGO_WORKFLOWS_SERVICE_ACCOUNT` | Argo 服务账号 | `argo-workflow-sa` |
| `METAFLOW_ARGO_WORKFLOWS_IMAGE_PULL_POLICY` | Argo 镜像拉取策略 | `Always` |

### AWS 相关字段

| 字段名 | 说明 | 示例值 |
|--------|------|--------|
| `METAFLOW_ECS_S3_ACCESS_IAM_ROLE` | ECS 任务访问 S3 的 IAM Role | `arn:aws:iam::...` |
| `METAFLOW_BATCH_JOB_QUEUE` | AWS Batch 作业队列 | `arn:aws:batch:...` |
| `METAFLOW_SFN_IAM_ROLE` | Step Functions IAM Role | `arn:aws:iam::...` |
| `METAFLOW_EVENTS_SFN_ACCESS_IAM_ROLE` | SFN 事件访问 IAM Role | `arn:aws:iam::...` |

### conda 依赖管理字段

| 字段名 | 说明 | 示例值 |
|--------|------|--------|
| `METAFLOW_CONDA_DEPENDENCY_RESOLVER` | 依赖解析器 | `fast-bakery` |
| `METAFLOW_CONDA_REMOTE_INSTALLER_ARCH` | 远程安装器架构 | `linux-64` |

> **注意**：Outerbounds 平台通过 `outerbounds configure` 命令自动写入所有必要字段，**通常不需要手动编辑配置文件**。文档建议对于生产/开发环境隔离，优先使用 Perimeter 而非手动修改配置。

### 完整配置示例（Outerbounds 生成）

```json
{
    "METAFLOW_SERVICE_URL": "https://perimeter-abc123.ob.api.outerbounds.com/",
    "METAFLOW_SERVICE_AUTH_KEY": "ob_XXXXXXXXXXXXXXXXXXXXXXXX",
    "METAFLOW_DEFAULT_METADATA": "service",
    "METAFLOW_DATASTORE_SYSROOT_S3": "s3://company-ml-artifacts/metaflow/",
    "METAFLOW_DEFAULT_DATASTORE": "s3",
    "METAFLOW_KUBERNETES_NAMESPACE": "metaflow",
    "METAFLOW_DEFAULT_CONTAINER_IMAGE": "123456789.dkr.ecr.us-east-1.amazonaws.com/ml-base:latest",
    "METAFLOW_CONDA_DEPENDENCY_RESOLVER": "fast-bakery"
}
```

---

## `outerbounds` CLI 命令

### 安装

```bash
pip install -U outerbounds
```

### 已知命令

**`outerbounds configure`** — 配置本地环境

```bash
# 基本配置（使用默认 profile）
outerbounds configure <token-from-outerbounds-ui>

# 使用命名 profile（避免与现有 Metaflow 配置冲突）
outerbounds configure --profile ob <token>
outerbounds configure --profile production <prod-token>
outerbounds configure --profile dev <dev-token>

# Machine User OIDC 认证（CI/CD 环境）
outerbounds configure --machine-user
```

**`outerbounds check`** — 验证连接状态

```bash
# 基本连接验证（显示所有状态行）
outerbounds check -v

# 验证 Workstation 连接
outerbounds check -w

# 指定 profile 验证
METAFLOW_PROFILE=ob outerbounds check -v

# 成功时输出类似：
# [OK] Metadata service connection
# [OK] Datastore access (S3)
# [OK] Kubernetes cluster
```

> **需要验证**：`outerbounds` CLI 的完整子命令列表未在公开文档中枚举。以下命令通过 `outerbounds --help` 应可查看。已知命令为 `configure` 和 `check`，其他子命令如 `workstation`、`perimeter` 等待验证。

```bash
# 查看所有可用命令
outerbounds --help

# 查看具体命令帮助
outerbounds configure --help
outerbounds check --help
```

---

## `METAFLOW_PROFILE` 环境变量

`METAFLOW_PROFILE` 是切换配置 profile 的核心机制。

### 基本用法

```bash
# 使用默认 profile（config.json）
python my_flow.py run

# 使用名为 "ob" 的 profile（config_ob.json）
METAFLOW_PROFILE=ob python my_flow.py run

# 会话级别切换
export METAFLOW_PROFILE=production
python my_flow.py argo-workflows create
```

### 多环境工作流

```bash
# 开发调试
METAFLOW_PROFILE=dev python training_flow.py run

# 云端测试
METAFLOW_PROFILE=dev python training_flow.py run --with kubernetes

# 暂存环境验证
METAFLOW_PROFILE=staging python training_flow.py argo-workflows create

# 生产部署
METAFLOW_PROFILE=production python training_flow.py \
  --environment=fast-bakery \
  argo-workflows create \
  --production
```

### 与 Makefile 集成

```makefile
# Makefile
.PHONY: run-dev deploy-staging deploy-prod

run-dev:
	METAFLOW_PROFILE=dev python training_flow.py run --with kubernetes

deploy-staging:
	METAFLOW_PROFILE=staging python training_flow.py \
	  --environment=fast-bakery argo-workflows create

deploy-prod:
	METAFLOW_PROFILE=production python training_flow.py \
	  --environment=fast-bakery argo-workflows create --production
```

---

## `metaflow configure` 命令（开源版）

开源 Metaflow 的配置工具（适用于自建 Metaflow，Outerbounds 用户通常使用 `outerbounds configure`）：

```bash
# 交互式配置 AWS 集成
metaflow configure aws

# 交互式配置 Kubernetes 集成
metaflow configure kubernetes

# 使用命名 profile
metaflow configure aws --profile my-profile
```

---

## 运行时环境变量覆盖

任何配置文件中的字段都可以通过同名环境变量在运行时覆盖：

```bash
# 临时覆盖默认镜像
METAFLOW_DEFAULT_CONTAINER_IMAGE=my-custom-image:v2 \
  python flow.py run --with kubernetes

# 临时覆盖 Kubernetes namespace
METAFLOW_KUBERNETES_NAMESPACE=test-namespace \
  python flow.py run --with kubernetes

# 覆盖 compute pool（通过装饰器参数更常见，但也可以通过 env var）
# 注意：compute_pool 通常在 @kubernetes 装饰器中指定，不通过环境变量
```

---

## 常见问题排查

```bash
# 1. 验证当前使用的 profile 配置是否正确
outerbounds check -v

# 2. 查看当前配置文件内容（请勿分享给他人，含有 token）
cat ~/.metaflowconfig/config.json

# 3. 如果同时有多个 profile，列出所有配置文件
ls ~/.metaflowconfig/

# 4. 验证 Kubernetes 集群连通性
kubectl get nodes

# 5. 查看 Metaflow 版本
python -c "import metaflow; print(metaflow.__version__)"
python -c "import outerbounds; print(outerbounds.__version__)"
```

---

## 参考资料

- [Connect to Outerbounds](https://docs.outerbounds.com/outerbounds/connect-to-outerbounds/)
- [Configuring Metaflow](https://docs.outerbounds.com/engineering/operations/configure-metaflow/)
- [Use Multiple Metaflow Configuration Files](https://docs.outerbounds.com/use-multiple-metaflow-configs/)

*最后更新：2026-04-13*
