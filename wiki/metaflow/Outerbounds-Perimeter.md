# Outerbounds Perimeter

> Perimeter 是 Outerbounds 平台上的逻辑隔离环境单元，用于分隔不同团队、项目或生命周期阶段（dev/staging/prod）的计算资源、元数据和权限边界。

相关笔记：[[Metaflow工作流框架]] | [[Outerbounds概览]]

---

## 什么是 Perimeter

Perimeter（"围界"）是 Outerbounds 平台的核心隔离机制。每个 Perimeter 是一个独立的执行上下文，拥有：

- 独立的元数据命名空间（不同 Perimeter 的 Flow 运行记录互不可见）
- 独立的用户权限（RBAC 角色在 Perimeter 级别分配）
- 独立的 IAM Role（访问云资源的身份）
- 独立的 Perimeter Policy（可强制要求使用特定容器镜像等）
- 独立的计算池访问权限

典型使用场景：

| 场景 | Perimeter 划分方式 |
|------|------------------|
| 环境隔离 | `dev`、`staging`、`production` 三个 Perimeter |
| 团队隔离 | 不同业务团队各自的 Perimeter |
| 数据安全 | 敏感数据团队与普通团队隔离 |
| 多云资源管理 | 每个 Perimeter 绑定不同 IAM Role 访问不同 AWS 账号 |

---

## 查看与访问 Perimeter

登录 Outerbounds UI 后，在左侧导航栏可以看到 **Perimeters** 视图，列出当前工作区下所有可用的 Perimeter。

用户通过 `METAFLOW_PROFILE` 环境变量或 `outerbounds configure` 时绑定的 token 决定当前使用的 Perimeter。不同 Perimeter 对应不同的配置 profile。

---

## Perimeter 创建（管理员操作）

> **注意**：Perimeter 的创建和管理需要平台管理员权限。以下步骤基于文档描述，具体 UI 布局可能随平台版本变化，建议在 Outerbounds UI 中实际操作时参考最新文档。

**通过 Outerbounds UI 创建 Perimeter：**

1. 进入 **Admin** 界面
2. 选择 **Perimeters** 标签
3. 点击 **Create Perimeter**
4. 填写以下配置项：

| 配置项 | 说明 |
|--------|------|
| Perimeter 名称 | 唯一标识符，例如 `production`、`ml-team-dev` |
| 关联的 IAM Role | 绑定到此 Perimeter 的 AWS/GCP/Azure 服务账号 |
| 计算池访问权限 | 指定此 Perimeter 可以使用哪些 Compute Pool |
| 用户/团队分配 | 将 Outerbounds 用户分配到此 Perimeter |
| Perimeter Policy | 可选，设置依赖/镜像使用策略 |

---

## IAM Role 绑定

Perimeter 通过绑定 IAM Role 来访问云资源（S3、RDS、Athena 等）。配置流程：

**AWS IAM Role 配置步骤：**

```bash
# 1. 在 AWS IAM 控制台创建 IAM Role
# 2. 在 Outerbounds UI 的 Integrations 页面选择 "IAM Role"
# 3. 将 UI 提供的 Trust Relationship 应用到 Role 的信任策略
# 4. 添加必需 Tag：
#    Key: outerbounds.com/accessible-by-deployment
#    Value: <UI 中提供的值>
# 5. 将 Role ARN 记录备用
# 6. 按需附加 AWS Policy（S3、Athena、EMR 等）
```

在代码中指定 IAM Role 访问 AWS 服务：

```python
import boto3

# 通过 role_arn 直接指定
s3_client = boto3.client(
    's3',
    # role_arn 在 Outerbounds 平台上会自动注入，或显式指定
)

# 使用 Outerbounds 提供的辅助函数（如有）
from outerbounds.utils import get_aws_client
client = get_aws_client('athena', role_arn='arn:aws:iam::...')
```

---

## RBAC 权限模型

Outerbounds 在 Perimeter 级别实现 RBAC（基于角色的访问控制）。用户在不同 Perimeter 可以有不同的角色。

**常见角色类型（需在 Outerbounds UI 中确认实际角色名称）：**

| 角色 | 典型权限 |
|------|---------|
| Admin | 创建/删除 Perimeter、管理用户、配置策略 |
| Developer | 运行 Flow、查看 Runs、访问 Workstations |
| Read-only | 仅查看 Runs 和 Artifacts，不能执行 |

> **需要验证**：Outerbounds 文档未在公开页面详细列出具体 RBAC 角色名称和权限矩阵，建议联系 Outerbounds 团队或查看平台 Admin 文档。

---

## Perimeter Policy（强制策略）

Perimeter Policy 允许管理员在 Perimeter 级别强制执行统一的镜像/依赖规范，防止用户绕过组织安全要求。

**典型用例：强制所有任务使用组织维护的统一基础镜像**

配置后效果：
- 该 Perimeter 内所有 Flow 步骤必须使用策略指定的镜像
- 用户在 `@kubernetes(image=...)` 中指定其他镜像会被策略覆盖
- 与 `@pypi`/`@conda` 动态构建镜像方案**冲突**（若 Policy 要求固定镜像，则无法使用 fast-bakery 动态构建）

**三种依赖策略与 Perimeter Policy 的兼容性：**

| 依赖方式 | 是否兼容 Perimeter Policy |
|---------|--------------------------|
| `@pypi`/`@conda` + fast-bakery | 若 Policy 强制固定镜像则**不兼容** |
| 第三方预构建镜像（PyTorch Hub 等） | 兼容，Perimeter Policy 可强制指定 |
| 组织自定义私有镜像 | 最兼容，Perimeter Policy 的典型场景 |

---

## 多环境隔离策略

推荐的多环境 Perimeter 架构：

```
Workspace
├── Perimeter: dev
│   ├── 绑定 IAM Role: arn:aws:iam::dev-account/role
│   ├── 计算池: small-cpu-pool
│   └── Policy: 无（允许 fast-bakery 动态构建）
├── Perimeter: staging
│   ├── 绑定 IAM Role: arn:aws:iam::staging-account/role
│   ├── 计算池: staging-pool
│   └── Policy: 推荐镜像列表
└── Perimeter: production
    ├── 绑定 IAM Role: arn:aws:iam::prod-account/role
    ├── 计算池: prod-gpu-pool, prod-cpu-pool
    └── Policy: 强制使用审批镜像
```

**切换 Perimeter（用户侧）：**

```bash
# 每个 Perimeter 对应一个 outerbounds profile
outerbounds configure --profile dev <dev-token>
outerbounds configure --profile production <prod-token>

# 切换环境
export METAFLOW_PROFILE=dev
python my_flow.py run --with kubernetes

export METAFLOW_PROFILE=production
python my_flow.py argo-workflows create
```

---

## 注意事项

- Perimeter 内的 Runs 和 Artifacts 对其他 Perimeter 用户不可见（元数据命名空间隔离）
- 同一 Perimeter 内的用户可以互相看到对方的 Runs（通过 Metaflow Client API）
- Perimeter 删除操作不可逆，删除前需确认所有相关资源已妥善处理
- `outerbounds configure` 的 token 与特定 Perimeter 绑定，不要在不同 Perimeter 间共享 token

---

## 参考资料

- [Outerbounds 文档 - 平台架构](https://docs.outerbounds.com/outerbounds/platform-architecture/)
- [Configure an IAM Role](https://docs.outerbounds.com/outerbounds/iam-role/)
- [Managing Dependencies](https://docs.outerbounds.com/outerbounds/managing-dependencies/)

*最后更新：2026-04-13*
