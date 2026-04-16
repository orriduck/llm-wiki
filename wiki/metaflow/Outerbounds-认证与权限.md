# Outerbounds Authentication & Permissions / Outerbounds 认证与权限

> Covers the Outerbounds platform's authentication system: PAT for personal users, Machine Users for CI/CD scenarios (GitHub OIDC / CircleCI / AWS IAM), SSO integration, and the RBAC role permission model.

> 涵盖 Outerbounds 平台的身份认证体系：个人用户的 PAT、CI/CD 场景的 Machine Users（GitHub OIDC / CircleCI / AWS IAM）、SSO 集成，以及 RBAC 角色权限模型。

Related notes / 相关笔记：[[Metaflow工作流框架]] | [[Outerbounds概览]]

---

## Authentication System Overview / 认证体系概览

Outerbounds authentication falls into two categories:

> Outerbounds 的认证分为两类：

| Type / 类型 | Use Case / 适用场景 | Auth Method / 认证方式 |
|------|---------|---------|
| **Personal Users / 个人用户** | Developer daily use / 开发者日常使用 | SSO login + Personal Access Token (PAT) |
| **Machine Users / 机器用户** | CI/CD pipelines, automation scripts / CI/CD 流水线、自动化脚本 | GitHub OIDC / CircleCI OIDC / AWS IAM Role |

---

## Personal Users: Personal Access Token (PAT) / 个人用户：Personal Access Token (PAT)

PAT is the credential for personal users to connect to the Outerbounds platform.

> PAT 是个人用户连接 Outerbounds 平台的凭证。

**Obtaining a PAT / 获取 PAT：**

1. Log in to the Outerbounds UI (via your organization's SSO entry point) / 登录 Outerbounds UI（通过组织的 SSO 入口）
2. Generate a Personal Access Token in your personal settings / 在个人设置中生成 Personal Access Token
3. Copy the token (displayed only once) / 复制 token（只显示一次）

**Configuring the local environment / 配置本地环境：**

```bash
# Install outerbounds CLI / 安装 outerbounds CLI
pip install -U outerbounds

# Configure with token (stored in ~/.metaflowconfig/)
# 使用 token 配置（token 存储在 ~/.metaflowconfig/ 下）
outerbounds configure <your-personal-access-token>

# If local Metaflow config already exists, create a separate profile to avoid conflicts
# 如果本地已有 Metaflow 配置，创建独立 profile 避免冲突
outerbounds configure --profile ob <your-personal-access-token>

# Activate the profile / 激活 profile
export METAFLOW_PROFILE=ob
```

**Important limitations / 重要限制：**

- PAT is bound to personal identity and **cannot be shared** with others.
- Use Machine Users for team shared access scenarios (CI/CD).
- If a PAT is leaked, revoke it immediately in the UI and regenerate.

> - PAT 与个人身份绑定，**不能共享**给他人
> - 团队共享访问场景（CI/CD）应使用 Machine Users
> - PAT 泄露时需立即在 UI 中吊销并重新生成

---

## SSO Integration / SSO 集成

Outerbounds supports enterprise SSO (Single Sign-On) integration for unified user login management.

> Outerbounds 支持企业 SSO（Single Sign-On）集成，用于统一管理用户登录。

**Supported SSO providers (verify the exact list) / 支持的 SSO 提供商（需要验证具体支持列表）：**

- Google Workspace
- Azure Active Directory / Microsoft Entra ID
- Okta

**SSO Workflow / SSO 工作流：**

1. User accesses the Outerbounds UI / 用户访问 Outerbounds UI
2. Redirected to the organization's SSO provider for authentication / 被重定向到组织的 SSO 提供商进行身份验证
3. After successful verification, returned to Outerbounds with automatic permission mapping / 验证成功后返回 Outerbounds，自动完成权限映射
4. Workstation access is also authorized through SSO / Workstation 访问同样通过 SSO 授权

> SSO configuration is an admin operation. Specific configuration steps must be completed in the Outerbounds Admin interface in collaboration with the IT/identity management team.

> SSO 配置属于平台管理员操作，具体配置步骤需在 Outerbounds Admin 界面中完成，并与 IT/身份管理团队协作。

---

## Machine Users / 机器用户

Machine Users are service accounts designed for programmatic access (CI/CD, automation scripts). Unlike PATs, Machine Users are **not bound to a specific person's identity** and authenticate via OIDC Tokens or IAM Roles issued by external systems.

> Machine Users 是为程序化访问（CI/CD、自动化脚本）设计的服务账号。与 PAT 不同，Machine Users **不绑定具体人员身份**，通过外部系统颁发的 OIDC Token 或 IAM Role 认证。

**Creating a Machine User / 创建 Machine User：**

1. In the Outerbounds UI, go to **Users** > **Machines** tab / 进入 **Users** > **Machines** 标签
2. Click **Create New** / 点击 **Create New**
3. Select authentication type (GitHub / CircleCI / AWS IAM) / 选择认证类型
4. Fill in the required configuration / 填写必要配置
5. Upon completion, the system provides corresponding example code/configuration / 完成后，系统提供对应的示例代码/配置

---

### Auth Method 1: GitHub Actions (OIDC) / 认证方式 1：GitHub Actions（OIDC）

GitHub Actions authenticates using JWT OIDC Tokens issued by GitHub.

> GitHub Actions 使用 GitHub 颁发的 JWT OIDC Token 进行认证。

**Configuration parameters / 配置参数：**

| Parameter / 参数 | Required / 必填 | Description / 说明 |
|------|------|------|
| Organization | Yes / 是 | GitHub organization name / GitHub 组织名称 |
| Repository | Yes / 是 | Repository name / 仓库名称 |
| Branch | No / 否 | Restrict to specific branch Actions / 限定只有特定分支的 Actions 可以认证 |
| Workflow | No / 否 | Restrict to specific workflow file / 限定只有特定 workflow 文件可以认证 |
| Environment | No / 否 | Restrict to specific GitHub Environment / 限定只有特定 GitHub Environment 可以认证 |

**GitHub Actions workflow example / GitHub Actions 工作流示例：**

```yaml
# .github/workflows/deploy.yml
name: Deploy ML Flow

on:
  push:
    branches: [main]

permissions:
  id-token: write  # Must enable OIDC token permission / 必须启用 OIDC token 权限
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install -U outerbounds
      
      - name: Configure Outerbounds (OIDC)
        # Outerbounds CLI automatically reads GITHUB_TOKEN for OIDC auth
        # Outerbounds CLI 自动读取 GITHUB_TOKEN 进行 OIDC 认证
        run: outerbounds configure --machine-user
      
      - name: Deploy Flow
        run: |
          python my_flow.py argo-workflows create --production
```

---

### Auth Method 2: CircleCI (OIDC) / 认证方式 2：CircleCI（OIDC）

CircleCI authenticates via automatically injected OIDC Token environment variables.

> CircleCI 通过自动注入的 OIDC Token 环境变量认证。

**Configuration parameters / 配置参数：**

| Parameter / 参数 | Required / 必填 | Description / 说明 |
|------|------|------|
| Organization ID | Yes / 是 | CircleCI organization ID / CircleCI 组织 ID |
| Project ID | Yes / 是 | CircleCI project ID / CircleCI 项目 ID |
| Source Control URL | Yes / 是 | Source repo URL / 源码仓库 URL |
| Branch | No / 否 | Restrict to specific branch / 限定特定分支 |

**CircleCI environment variables (auto-injected) / CircleCI 环境变量（自动注入）：**

```bash
$CIRCLE_OIDC_TOKEN     # CircleCI OIDC Token (recommended / 推荐)
$CIRCLE_OIDC_TOKEN_V2  # CircleCI OIDC Token V2
```

**CircleCI configuration example / CircleCI 配置示例：**

```yaml
# .circleci/config.yml
version: 2.1

jobs:
  deploy:
    docker:
      - image: cimg/python:3.10
    steps:
      - checkout
      - run:
          name: Install outerbounds
          command: pip install -U outerbounds
      - run:
          name: Deploy Flow
          command: |
            # CIRCLE_OIDC_TOKEN is automatically available
            # CIRCLE_OIDC_TOKEN 自动可用
            outerbounds configure --machine-user --oidc-token $CIRCLE_OIDC_TOKEN
            python my_flow.py argo-workflows create --production
```

---

### Auth Method 3: AWS IAM Role / 认证方式 3：AWS IAM Role

Suitable for systems that can assume an IAM Role (EC2 instances, ECS Tasks, Lambda, etc.).

> 适用于能够 Assume IAM Role 的系统（EC2 实例、ECS Task、Lambda 等）。

**Configuration steps / 配置步骤：**

**Phase 1: Prepare IAM Role / 准备 IAM Role**

```json
// Policy to attach to the IAM Role (access Outerbounds Control Plane's Secrets Manager)
// 需要附加到 IAM Role 的策略（访问 Outerbounds Control Plane 的 Secrets Manager）
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:<region>:<control-plane-account-id>:secret:outerbounds/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "kms:Decrypt"
      ],
      "Resource": "arn:aws:kms:<region>:<control-plane-account-id>:key/<key-id>"
    }
  ]
}
```

**Phase 2: Create Machine User in Outerbounds UI / 在 Outerbounds UI 创建 Machine User**

1. Users > Machines > Create New
2. Select "AWS IAM" / 选择 "AWS IAM"
3. Associate the IAM Role ARN above / 关联上述 IAM Role ARN
4. Configure permission scope as needed / 按需配置权限范围

---

## RBAC Role Permissions / RBAC 角色权限

> **Needs verification / 需要验证**: Outerbounds documentation does not publicly detail the RBAC role matrix. The following is based on scattered descriptions in the docs; refer to the actual Outerbounds Admin UI for specific permission definitions.

> Outerbounds 文档未公开详细的 RBAC 角色矩阵。以下基于文档中散落的描述整理，具体权限定义以 Outerbounds Admin UI 中实际显示为准。

Permission management is enforced at the **Perimeter level**; the same user can have different roles in different Perimeters.

> 权限管理在 **Perimeter 级别**实施，同一用户在不同 Perimeter 可以有不同角色。

**Known permission distinctions / 已知权限区分：**

| Operation / 操作 | Regular User / 普通用户 | Admin / 管理员 |
|------|---------|--------|
| Run Flow / 运行 Flow | Yes / 是 | Yes / 是 |
| View Runs / 查看 Runs | Yes (own, or within same Perimeter) / 是（自己的，或同 Perimeter 下的）| Yes (all) / 是（全部）|
| Create Workstation / 创建 Workstation | No / 否 | Yes / 是 |
| Create Perimeter / 创建 Perimeter | No / 否 | Yes / 是 |
| Manage Users / 管理用户 | No / 否 | Yes / 是 |
| Configure SSO / 配置 SSO | No / 否 | Yes / 是 |
| Create Machine Users / 创建 Machine Users | No (needs verification) / 否（需要验证）| Yes / 是 |

**Machine Users permission scope / Machine Users 的权限范围：**

Machine Users also follow Perimeter-level access control. When created, you must specify which Perimeters they can access, preventing CI/CD pipelines from accessing sensitive environments beyond their scope.

> Machine Users 也遵循 Perimeter 级别的权限控制，在创建时需要指定允许访问的 Perimeter，防止 CI/CD 管道越权访问敏感环境。

---

## Credential Security Best Practices / 凭证安全最佳实践

```bash
# 1. Don't hardcode PATs in code
# 1. 不要在代码中硬编码 PAT
# Bad example / 错误示例：
token = "ob_xxxxxxxxxxxxxxxx"  # Don't do this / 不要这样做

# 2. Use environment variables or config files
# 2. 使用环境变量或配置文件
export METAFLOW_PROFILE=production
python my_flow.py argo-workflows create

# 3. Use Machine Users in CI/CD (not PATs)
# 3. CI/CD 中使用 Machine Users（不用 PAT）
# See GitHub Actions / CircleCI examples above
# 参考上述 GitHub Actions / CircleCI 示例

# 4. Use different PATs / Machine Users for production and dev environments
# 4. 生产环境和开发环境使用不同的 PAT / Machine User
# Ensure credentials cannot escalate via Perimeter isolation
# 通过 Perimeter 隔离确保凭证不能越权
```

---

## References / 参考资料

- [Connect to Outerbounds](https://docs.outerbounds.com/outerbounds/connect-to-outerbounds/)
- [Programmatic access via machine users](https://docs.outerbounds.com/outerbounds/machine-users/)
- [Configure an IAM role](https://docs.outerbounds.com/outerbounds/iam-role/)

*Last updated / 最后更新：2026-04-13*
