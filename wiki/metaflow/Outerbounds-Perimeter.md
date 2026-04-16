# Outerbounds Perimeter / Outerbounds Perimeter（隔离环境）

A Perimeter is the logical isolation unit on the Outerbounds platform, used to separate compute resources, metadata, and permission boundaries between different teams, projects, or lifecycle stages (dev/staging/prod).

> Perimeter 是 Outerbounds 平台上的逻辑隔离环境单元，用于分隔不同团队、项目或生命周期阶段（dev/staging/prod）的计算资源、元数据和权限边界。

Related: [[Metaflow工作流框架]] | [[Outerbounds概览]]

---

## What Is a Perimeter / 什么是 Perimeter

A Perimeter is the core isolation mechanism of the Outerbounds platform. Each Perimeter is an independent execution context with:

- An isolated metadata namespace (Flow run records are not visible across Perimeters)
- Independent user permissions (RBAC roles are assigned at the Perimeter level)
- An independent IAM Role (identity for accessing cloud resources)
- An independent Perimeter Policy (can enforce use of specific container images, etc.)
- Independent compute pool access permissions

> Perimeter（"围界"）是 Outerbounds 平台的核心隔离机制。每个 Perimeter 是一个独立的执行上下文，拥有：
>
> - 独立的元数据命名空间（不同 Perimeter 的 Flow 运行记录互不可见）
> - 独立的用户权限（RBAC 角色在 Perimeter 级别分配）
> - 独立的 IAM Role（访问云资源的身份）
> - 独立的 Perimeter Policy（可强制要求使用特定容器镜像等）
> - 独立的计算池访问权限

Typical use cases:

> 典型使用场景：

| Scenario / 场景 | Perimeter Division / Perimeter 划分方式 |
|------|------------------|
| Environment isolation / 环境隔离 | `dev`, `staging`, `production` three Perimeters / 三个 Perimeter |
| Team isolation / 团队隔离 | Separate Perimeters for different business teams / 不同业务团队各自的 Perimeter |
| Data security / 数据安全 | Isolate sensitive-data teams from general teams / 敏感数据团队与普通团队隔离 |
| Multi-cloud resource management / 多云资源管理 | Each Perimeter binds a different IAM Role to access different cloud accounts / 每个 Perimeter 绑定不同 IAM Role 访问不同云账号 |

---

## Viewing and Accessing Perimeters / 查看与访问 Perimeter

After logging in to the Outerbounds UI, the **Perimeters** view in the left navigation bar lists all available Perimeters in the current workspace.

> 登录 Outerbounds UI 后，在左侧导航栏可以看到 **Perimeters** 视图，列出当前工作区下所有可用的 Perimeter。

The user's active Perimeter is determined by the `METAFLOW_PROFILE` environment variable or the token bound during `outerbounds configure`. Different Perimeters correspond to different configuration profiles.

> 用户通过 `METAFLOW_PROFILE` 环境变量或 `outerbounds configure` 时绑定的 token 决定当前使用的 Perimeter。不同 Perimeter 对应不同的配置 profile。

---

## Creating a Perimeter (Admin Operation) / Perimeter 创建（管理员操作）

> **Note**: Creating and managing Perimeters requires platform administrator permissions. The following steps are based on documentation descriptions; the exact UI layout may change with platform versions. Refer to the latest documentation when working in the Outerbounds UI.

> **注意**：Perimeter 的创建和管理需要平台管理员权限。以下步骤基于文档描述，具体 UI 布局可能随平台版本变化，建议在 Outerbounds UI 中实际操作时参考最新文档。

**Creating a Perimeter via the Outerbounds UI:**

> **通过 Outerbounds UI 创建 Perimeter：**

1. Go to the **Admin** interface / 进入 **Admin** 界面
2. Select the **Perimeters** tab / 选择 **Perimeters** 标签
3. Click **Create Perimeter** / 点击 **Create Perimeter**
4. Fill in the following configuration items: / 填写以下配置项：

| Configuration Item / 配置项 | Description / 说明 |
|--------|------|
| Perimeter Name / Perimeter 名称 | Unique identifier, e.g. `production`, `ml-team-dev` |
| Associated IAM Role / 关联的 IAM Role | AWS/GCP/Azure service account bound to this Perimeter |
| Compute Pool Access / 计算池访问权限 | Specify which Compute Pools this Perimeter can use |
| User/Team Assignment / 用户/团队分配 | Assign Outerbounds users to this Perimeter |
| Perimeter Policy | Optional; set dependency/image usage policies |

---

## IAM Role Binding / IAM Role 绑定

A Perimeter accesses cloud resources (S3, RDS, Athena, etc.) by binding an IAM Role. Configuration steps:

> Perimeter 通过绑定 IAM Role 来访问云资源（S3、RDS、Athena 等）。配置流程：

**AWS IAM Role configuration steps:**

> **AWS IAM Role 配置步骤：**

```bash
# 1. Create an IAM Role in the AWS IAM console
# 2. In the Outerbounds UI Integrations page, select "IAM Role"
# 3. Apply the Trust Relationship provided by the UI to the Role's trust policy
# 4. Add required Tag:
#    Key: outerbounds.com/accessible-by-deployment
#    Value: <value provided in UI>
# 5. Record the Role ARN for later use
# 6. Attach AWS Policies as needed (S3, Athena, EMR, etc.)
```

Specifying an IAM Role to access AWS services in code:

> 在代码中指定 IAM Role 访问 AWS 服务：

```python
import boto3

# The role_arn is automatically injected on the Outerbounds platform,
# or can be specified explicitly
s3_client = boto3.client('s3')

# Using an Outerbounds helper function (if available)
from outerbounds.utils import get_aws_client
client = get_aws_client('athena', role_arn='arn:aws:iam::<your-account-id>:role/<your-role-name>')
```

---

## RBAC Permission Model / RBAC 权限模型

Outerbounds implements RBAC (Role-Based Access Control) at the Perimeter level. Users can have different roles in different Perimeters.

> Outerbounds 在 Perimeter 级别实现 RBAC（基于角色的访问控制）。用户在不同 Perimeter 可以有不同的角色。

**Common role types (confirm actual role names in the Outerbounds UI):**

> **常见角色类型（需在 Outerbounds UI 中确认实际角色名称）：**

| Role / 角色 | Typical Permissions / 典型权限 |
|------|---------|
| Admin | Create/delete Perimeters, manage users, configure policies / 创建/删除 Perimeter、管理用户、配置策略 |
| Developer | Run Flows, view Runs, access Workstations / 运行 Flow、查看 Runs、访问 Workstations |
| Read-only | View Runs and Artifacts only, cannot execute / 仅查看 Runs 和 Artifacts，不能执行 |

> **To verify**: Outerbounds documentation does not publicly detail specific RBAC role names and permission matrices. Contact the Outerbounds team or check the platform Admin documentation.

> **需要验证**：Outerbounds 文档未在公开页面详细列出具体 RBAC 角色名称和权限矩阵，建议联系 Outerbounds 团队或查看平台 Admin 文档。

---

## Perimeter Policy (Enforcement Policies) / Perimeter Policy（强制策略）

Perimeter Policy allows administrators to enforce uniform image/dependency standards at the Perimeter level, preventing users from bypassing organizational security requirements.

> Perimeter Policy 允许管理员在 Perimeter 级别强制执行统一的镜像/依赖规范，防止用户绕过组织安全要求。

**Typical use case: force all tasks to use an organization-maintained unified base image**

> **典型用例：强制所有任务使用组织维护的统一基础镜像**

Effect after configuration:

> 配置后效果：

- All Flow steps within the Perimeter must use the image specified by the policy / 该 Perimeter 内所有 Flow 步骤必须使用策略指定的镜像
- Images specified by the user in `@kubernetes(image=...)` are overridden by the policy / 用户在 `@kubernetes(image=...)` 中指定其他镜像会被策略覆盖
- **Conflicts** with `@pypi`/`@conda` dynamic image build approach (if the Policy requires a fixed image, fast-bakery dynamic builds cannot be used) / 与 `@pypi`/`@conda` 动态构建镜像方案**冲突**（若 Policy 要求固定镜像，则无法使用 fast-bakery 动态构建）

**Compatibility of three dependency strategies with Perimeter Policy:**

> **三种依赖策略与 Perimeter Policy 的兼容性：**

| Dependency Method / 依赖方式 | Compatible with Perimeter Policy / 是否兼容 Perimeter Policy |
|---------|--------------------------|
| `@pypi`/`@conda` + fast-bakery | **Incompatible** if Policy enforces fixed image / 若 Policy 强制固定镜像则**不兼容** |
| Third-party pre-built images (PyTorch Hub, etc.) / 第三方预构建镜像 | Compatible; Perimeter Policy can enforce them / 兼容，Perimeter Policy 可强制指定 |
| Organization custom private images / 组织自定义私有镜像 | Most compatible; the typical Perimeter Policy scenario / 最兼容，Perimeter Policy 的典型场景 |

---

## Multi-Environment Isolation Strategy / 多环境隔离策略

Recommended multi-environment Perimeter architecture:

> 推荐的多环境 Perimeter 架构：

```
Workspace
├── Perimeter: dev
│   ├── Bound IAM Role: arn:aws:iam::<dev-account-id>:role/<dev-role>
│   ├── Compute Pool: small-cpu-pool
│   └── Policy: None (allows fast-bakery dynamic builds)
├── Perimeter: staging
│   ├── Bound IAM Role: arn:aws:iam::<staging-account-id>:role/<staging-role>
│   ├── Compute Pool: staging-pool
│   └── Policy: Recommended image list
└── Perimeter: production
    ├── Bound IAM Role: arn:aws:iam::<prod-account-id>:role/<prod-role>
    ├── Compute Pool: prod-gpu-pool, prod-cpu-pool
    └── Policy: Enforce approved images
```

**Switching Perimeters (user side):**

> **切换 Perimeter（用户侧）：**

```bash
# Each Perimeter corresponds to one outerbounds profile
outerbounds configure --profile dev <dev-token>
outerbounds configure --profile production <prod-token>

# Switch environments
export METAFLOW_PROFILE=dev
python my_flow.py run --with kubernetes

export METAFLOW_PROFILE=production
python my_flow.py argo-workflows create
```

---

## Notes / 注意事项

- Runs and Artifacts within a Perimeter are not visible to users of other Perimeters (metadata namespace isolation) / Perimeter 内的 Runs 和 Artifacts 对其他 Perimeter 用户不可见（元数据命名空间隔离）
- Users within the same Perimeter can see each other's Runs (via the Metaflow Client API) / 同一 Perimeter 内的用户可以互相看到对方的 Runs（通过 Metaflow Client API）
- Perimeter deletion is irreversible; confirm all related resources are handled before deleting / Perimeter 删除操作不可逆，删除前需确认所有相关资源已妥善处理
- The token from `outerbounds configure` is bound to a specific Perimeter; do not share tokens across Perimeters / `outerbounds configure` 的 token 与特定 Perimeter 绑定，不要在不同 Perimeter 间共享 token

---

## References / 参考资料

- [Outerbounds Docs - Platform Architecture](https://docs.outerbounds.com/outerbounds/platform-architecture/)
- [Configure an IAM Role](https://docs.outerbounds.com/outerbounds/iam-role/)
- [Managing Dependencies](https://docs.outerbounds.com/outerbounds/managing-dependencies/)

*Last updated: 2026-04-16*
