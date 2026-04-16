# Outerbounds Configuration & CLI / Outerbounds 配置与 CLI

> Covers `~/.metaflowconfig` complete fields (Outerbounds version), multi-profile management, all known `outerbounds` CLI commands, and `METAFLOW_PROFILE` environment variable usage.

> 涵盖 `~/.metaflowconfig` 完整字段（Outerbounds 版本）、多 profile 管理、`outerbounds` CLI 所有已知命令、`METAFLOW_PROFILE` 环境变量用法。

Related notes / 相关笔记：[[Metaflow工作流框架]] | [[Outerbounds概览]]

---

## Config File Location and Structure / 配置文件位置与结构

Metaflow (including Outerbounds) configuration is stored in the `~/.metaflowconfig/` directory:

> Metaflow（包括 Outerbounds）的配置存储在 `~/.metaflowconfig/` 目录下：

```
~/.metaflowconfig/
├── config.json           # Default config (equivalent to config_default.json)
├── config_default.json   # Equivalent to config.json
├── config_ob.json        # Profile named "ob"
├── config_production.json # Profile named "production"
└── config_dev.json        # Profile named "dev"
```

**Profile activation rules / profile 激活规则：**

- No profile specified: uses `config.json` or `config_default.json` / 未指定 profile：使用 `config.json` 或 `config_default.json`
- Profile specified: uses `config_<profile_name>.json` / 指定 profile：使用 `config_<profile_name>.json`
- Environment variable > config file (env vars with the same name override config file values) / 环境变量 > 配置文件（同名环境变量会覆盖配置文件中的值）

---

## `~/.metaflowconfig` Config Fields (Outerbounds Version) / 配置字段（Outerbounds 版本）

Outerbounds automatically writes the following fields via `outerbounds configure`:

> Outerbounds 通过 `outerbounds configure` 命令自动写入以下字段：

### Core Connection Fields / 核心连接字段

| Field / 字段名 | Description / 说明 | Example / 示例值 |
|--------|------|--------|
| `METAFLOW_SERVICE_URL` | Outerbounds metadata service URL / 元数据服务 URL | `https://perimeter-xyz.ob.api.outerbounds.com/` |
| `METAFLOW_SERVICE_AUTH_KEY` | Auth token (PAT) / 认证 token（PAT） | `ob_xxxxxxxxxxxxxxxx` |
| `METAFLOW_DEFAULT_METADATA` | Metadata backend type / 元数据后端类型 | `service` |

### Data Storage Fields / 数据存储字段

| Field / 字段名 | Description / 说明 | Example / 示例值 |
|--------|------|--------|
| `METAFLOW_DATASTORE_SYSROOT_S3` | S3 data root directory / S3 数据根目录 | `s3://my-bucket/metaflow/` |
| `METAFLOW_DATASTORE_SYSROOT_GS` | GCS data root directory (GCP deployment) / GCS 数据根目录（GCP 部署） | `gs://my-bucket/metaflow/` |
| `METAFLOW_DATASTORE_SYSROOT_AZURE` | Azure Blob data root directory / Azure Blob 数据根目录 | `az://container/metaflow/` |
| `METAFLOW_DEFAULT_DATASTORE` | Default data store type / 默认数据存储类型 | `s3` / `gs` / `azure` |

### Kubernetes Related Fields / Kubernetes 相关字段

| Field / 字段名 | Description / 说明 | Example / 示例值 |
|--------|------|--------|
| `METAFLOW_KUBERNETES_NAMESPACE` | Default Kubernetes namespace / 默认 Kubernetes 命名空间 | `metaflow` |
| `METAFLOW_KUBERNETES_SERVICE_ACCOUNT` | Kubernetes service account / Kubernetes 服务账号 | `metaflow-sa` |
| `METAFLOW_DEFAULT_CONTAINER_IMAGE` | Default container image / 默认容器镜像 | `<account-id>.dkr.ecr.<region>.amazonaws.com/ml-base:v1` |
| `METAFLOW_DEFAULT_CONTAINER_REGISTRY` | Default container registry / 默认容器 Registry | `<account-id>.dkr.ecr.<region>.amazonaws.com` |
| `METAFLOW_KUBERNETES_TOLERATIONS` | Default Tolerations (JSON) / 默认 Tolerations（JSON） | `[{"key":"...","operator":"..."}]` |
| `METAFLOW_KUBERNETES_LABELS` | Default Pod Labels (JSON) / 默认 Pod Labels（JSON） | `{"team":"ml","env":"prod"}` |
| `METAFLOW_KUBERNETES_ANNOTATIONS` | Default Pod Annotations (JSON) / 默认 Pod Annotations（JSON）| `{"iam.amazonaws.com/role":"..."}` |

### Argo Workflows Fields / Argo Workflows 字段

| Field / 字段名 | Description / 说明 | Example / 示例值 |
|--------|------|--------|
| `METAFLOW_ARGO_WORKFLOWS_KUBERNETES_NAMESPACE` | Argo namespace / Argo 命名空间 | `argo` |
| `METAFLOW_ARGO_WORKFLOWS_SERVICE_ACCOUNT` | Argo service account / Argo 服务账号 | `argo-workflow-sa` |
| `METAFLOW_ARGO_WORKFLOWS_IMAGE_PULL_POLICY` | Argo image pull policy / Argo 镜像拉取策略 | `Always` |

### AWS Related Fields / AWS 相关字段

| Field / 字段名 | Description / 说明 | Example / 示例值 |
|--------|------|--------|
| `METAFLOW_ECS_S3_ACCESS_IAM_ROLE` | IAM Role for ECS tasks to access S3 / ECS 任务访问 S3 的 IAM Role | `arn:aws:iam::<account-id>:...` |
| `METAFLOW_BATCH_JOB_QUEUE` | AWS Batch job queue / AWS Batch 作业队列 | `arn:aws:batch:...` |
| `METAFLOW_SFN_IAM_ROLE` | Step Functions IAM Role | `arn:aws:iam::<account-id>:...` |
| `METAFLOW_EVENTS_SFN_ACCESS_IAM_ROLE` | SFN event access IAM Role / SFN 事件访问 IAM Role | `arn:aws:iam::<account-id>:...` |

### Conda Dependency Management Fields / conda 依赖管理字段

| Field / 字段名 | Description / 说明 | Example / 示例值 |
|--------|------|--------|
| `METAFLOW_CONDA_DEPENDENCY_RESOLVER` | Dependency resolver / 依赖解析器 | `fast-bakery` |
| `METAFLOW_CONDA_REMOTE_INSTALLER_ARCH` | Remote installer architecture / 远程安装器架构 | `linux-64` |

> **Note / 注意**: The Outerbounds platform writes all necessary fields automatically via `outerbounds configure`. **Manual editing of config files is usually unnecessary.** Documentation recommends using Perimeters for production/dev isolation rather than manually modifying configuration.

> Outerbounds 平台通过 `outerbounds configure` 命令自动写入所有必要字段，**通常不需要手动编辑配置文件**。文档建议对于生产/开发环境隔离，优先使用 Perimeter 而非手动修改配置。

### Complete Config Example (Outerbounds-Generated) / 完整配置示例（Outerbounds 生成）

```json
{
    "METAFLOW_SERVICE_URL": "https://perimeter-abc123.ob.api.outerbounds.com/",
    "METAFLOW_SERVICE_AUTH_KEY": "ob_XXXXXXXXXXXXXXXXXXXXXXXX",
    "METAFLOW_DEFAULT_METADATA": "service",
    "METAFLOW_DATASTORE_SYSROOT_S3": "s3://my-ml-artifacts/metaflow/",
    "METAFLOW_DEFAULT_DATASTORE": "s3",
    "METAFLOW_KUBERNETES_NAMESPACE": "metaflow",
    "METAFLOW_DEFAULT_CONTAINER_IMAGE": "<account-id>.dkr.ecr.<region>.amazonaws.com/ml-base:latest",
    "METAFLOW_CONDA_DEPENDENCY_RESOLVER": "fast-bakery"
}
```

---

## `outerbounds` CLI Commands / `outerbounds` CLI 命令

### Installation / 安装

```bash
pip install -U outerbounds
```

### Known Commands / 已知命令

**`outerbounds configure`** -- Configure local environment / 配置本地环境

```bash
# Basic configuration (default profile)
# 基本配置（使用默认 profile）
outerbounds configure <token-from-outerbounds-ui>

# Use a named profile (avoid conflicts with existing Metaflow config)
# 使用命名 profile（避免与现有 Metaflow 配置冲突）
outerbounds configure --profile ob <token>
outerbounds configure --profile production <prod-token>
outerbounds configure --profile dev <dev-token>

# Machine User OIDC authentication (CI/CD environments)
# Machine User OIDC 认证（CI/CD 环境）
outerbounds configure --machine-user
```

**`outerbounds check`** -- Verify connection status / 验证连接状态

```bash
# Basic connection verification (show all status lines)
# 基本连接验证（显示所有状态行）
outerbounds check -v

# Verify Workstation connection / 验证 Workstation 连接
outerbounds check -w

# Verify with a specific profile / 指定 profile 验证
METAFLOW_PROFILE=ob outerbounds check -v

# Successful output looks like:
# 成功时输出类似：
# [OK] Metadata service connection
# [OK] Datastore access (S3)
# [OK] Kubernetes cluster
```

> **Needs verification / 需要验证**: The complete subcommand list for the `outerbounds` CLI is not enumerated in public documentation. The following commands should be viewable via `outerbounds --help`. Known commands are `configure` and `check`; other subcommands like `workstation`, `perimeter` are pending verification.

> `outerbounds` CLI 的完整子命令列表未在公开文档中枚举。以下命令通过 `outerbounds --help` 应可查看。已知命令为 `configure` 和 `check`，其他子命令如 `workstation`、`perimeter` 等待验证。

```bash
# View all available commands / 查看所有可用命令
outerbounds --help

# View help for specific commands / 查看具体命令帮助
outerbounds configure --help
outerbounds check --help
```

---

## `METAFLOW_PROFILE` Environment Variable / `METAFLOW_PROFILE` 环境变量

`METAFLOW_PROFILE` is the core mechanism for switching configuration profiles.

> `METAFLOW_PROFILE` 是切换配置 profile 的核心机制。

### Basic Usage / 基本用法

```bash
# Use default profile (config.json)
# 使用默认 profile（config.json）
python my_flow.py run

# Use profile named "ob" (config_ob.json)
# 使用名为 "ob" 的 profile（config_ob.json）
METAFLOW_PROFILE=ob python my_flow.py run

# Session-level switch / 会话级别切换
export METAFLOW_PROFILE=production
python my_flow.py argo-workflows create
```

### Multi-Environment Workflow / 多环境工作流

```bash
# Development debugging / 开发调试
METAFLOW_PROFILE=dev python training_flow.py run

# Cloud testing / 云端测试
METAFLOW_PROFILE=dev python training_flow.py run --with kubernetes

# Staging environment validation / 暂存环境验证
METAFLOW_PROFILE=staging python training_flow.py argo-workflows create

# Production deployment / 生产部署
METAFLOW_PROFILE=production python training_flow.py \
  --environment=fast-bakery \
  argo-workflows create \
  --production
```

### Makefile Integration / 与 Makefile 集成

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

## `metaflow configure` Command (Open-Source Version) / `metaflow configure` 命令（开源版）

The open-source Metaflow configuration tool (for self-hosted Metaflow; Outerbounds users typically use `outerbounds configure`):

> 开源 Metaflow 的配置工具（适用于自建 Metaflow，Outerbounds 用户通常使用 `outerbounds configure`）：

```bash
# Interactive AWS integration configuration
# 交互式配置 AWS 集成
metaflow configure aws

# Interactive Kubernetes integration configuration
# 交互式配置 Kubernetes 集成
metaflow configure kubernetes

# Use a named profile / 使用命名 profile
metaflow configure aws --profile my-profile
```

---

## Runtime Environment Variable Overrides / 运行时环境变量覆盖

Any config file field can be overridden at runtime via a same-named environment variable:

> 任何配置文件中的字段都可以通过同名环境变量在运行时覆盖：

```bash
# Temporarily override default image
# 临时覆盖默认镜像
METAFLOW_DEFAULT_CONTAINER_IMAGE=my-custom-image:v2 \
  python flow.py run --with kubernetes

# Temporarily override Kubernetes namespace
# 临时覆盖 Kubernetes namespace
METAFLOW_KUBERNETES_NAMESPACE=test-namespace \
  python flow.py run --with kubernetes

# Override compute pool (more commonly set via decorator param, but env var also works)
# 覆盖 compute pool（通过装饰器参数更常见，但也可以通过 env var）
# Note: compute_pool is typically specified in @kubernetes decorator, not via env var
# 注意：compute_pool 通常在 @kubernetes 装饰器中指定，不通过环境变量
```

---

## Common Troubleshooting / 常见问题排查

```bash
# 1. Verify current profile config is correct
# 1. 验证当前使用的 profile 配置是否正确
outerbounds check -v

# 2. View current config file contents (do not share with others; contains token)
# 2. 查看当前配置文件内容（请勿分享给他人，含有 token）
cat ~/.metaflowconfig/config.json

# 3. If multiple profiles exist, list all config files
# 3. 如果同时有多个 profile，列出所有配置文件
ls ~/.metaflowconfig/

# 4. Verify Kubernetes cluster connectivity
# 4. 验证 Kubernetes 集群连通性
kubectl get nodes

# 5. Check Metaflow version / 查看 Metaflow 版本
python -c "import metaflow; print(metaflow.__version__)"
python -c "import outerbounds; print(outerbounds.__version__)"
```

---

## References / 参考资料

- [Connect to Outerbounds](https://docs.outerbounds.com/outerbounds/connect-to-outerbounds/)
- [Configuring Metaflow](https://docs.outerbounds.com/engineering/operations/configure-metaflow/)
- [Use Multiple Metaflow Configuration Files](https://docs.outerbounds.com/use-multiple-metaflow-configs/)

*Last updated / 最后更新：2026-04-13*
