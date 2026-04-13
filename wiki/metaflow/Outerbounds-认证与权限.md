# Outerbounds 认证与权限

> 涵盖 Outerbounds 平台的身份认证体系：个人用户的 PAT、CI/CD 场景的 Machine Users（GitHub OIDC / CircleCI / AWS IAM）、SSO 集成，以及 RBAC 角色权限模型。

相关笔记：[[Metaflow工作流框架]] | [[Outerbounds概览]]

---

## 认证体系概览

Outerbounds 的认证分为两类：

| 类型 | 适用场景 | 认证方式 |
|------|---------|---------|
| **个人用户** | 开发者日常使用 | SSO 登录 + Personal Access Token (PAT) |
| **Machine Users** | CI/CD 流水线、自动化脚本 | GitHub OIDC / CircleCI OIDC / AWS IAM Role |

---

## 个人用户：Personal Access Token (PAT)

PAT 是个人用户连接 Outerbounds 平台的凭证。

**获取 PAT：**
1. 登录 Outerbounds UI（通过组织的 SSO 入口）
2. 在个人设置中生成 Personal Access Token
3. 复制 token（只显示一次）

**配置本地环境：**

```bash
# 安装 outerbounds CLI
pip install -U outerbounds

# 使用 token 配置（token 存储在 ~/.metaflowconfig/ 下）
outerbounds configure <your-personal-access-token>

# 如果本地已有 Metaflow 配置，创建独立 profile 避免冲突
outerbounds configure --profile ob <your-personal-access-token>

# 激活 profile
export METAFLOW_PROFILE=ob
```

**重要限制：**
- PAT 与个人身份绑定，**不能共享**给他人
- 团队共享访问场景（CI/CD）应使用 Machine Users
- PAT 泄露时需立即在 UI 中吊销并重新生成

---

## SSO 集成

Outerbounds 支持企业 SSO（Single Sign-On）集成，用于统一管理用户登录。

**支持的 SSO 提供商（需要验证具体支持列表）：**
- Google Workspace
- Azure Active Directory / Microsoft Entra ID
- Okta

**SSO 工作流：**
1. 用户访问 Outerbounds UI
2. 被重定向到组织的 SSO 提供商进行身份验证
3. 验证成功后返回 Outerbounds，自动完成权限映射
4. Workstation 访问同样通过 SSO 授权

> SSO 配置属于平台管理员操作，具体配置步骤需在 Outerbounds Admin 界面中完成，并与 IT/身份管理团队协作。

---

## Machine Users（机器用户）

Machine Users 是为程序化访问（CI/CD、自动化脚本）设计的服务账号。与 PAT 不同，Machine Users **不绑定具体人员身份**，通过外部系统颁发的 OIDC Token 或 IAM Role 认证。

**创建 Machine User：**
1. 在 Outerbounds UI 中进入 **Users** → **Machines** 标签
2. 点击 **Create New**
3. 选择认证类型（GitHub / CircleCI / AWS IAM）
4. 填写必要配置
5. 完成后，系统提供对应的示例代码/配置

---

### 认证方式 1：GitHub Actions（OIDC）

GitHub Actions 使用 GitHub 颁发的 JWT OIDC Token 进行认证。

**配置参数：**

| 参数 | 必填 | 说明 |
|------|------|------|
| Organization | 是 | GitHub 组织名称 |
| Repository | 是 | 仓库名称 |
| Branch | 否 | 限定只有特定分支的 Actions 可以认证 |
| Workflow | 否 | 限定只有特定 workflow 文件可以认证 |
| Environment | 否 | 限定只有特定 GitHub Environment 可以认证 |

**GitHub Actions 工作流示例：**

```yaml
# .github/workflows/deploy.yml
name: Deploy ML Flow

on:
  push:
    branches: [main]

permissions:
  id-token: write  # 必须启用 OIDC token 权限
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
        # Outerbounds CLI 自动读取 GITHUB_TOKEN 进行 OIDC 认证
        run: outerbounds configure --machine-user
      
      - name: Deploy Flow
        run: |
          python my_flow.py argo-workflows create --production
```

---

### 认证方式 2：CircleCI（OIDC）

CircleCI 通过自动注入的 OIDC Token 环境变量认证。

**配置参数：**

| 参数 | 必填 | 说明 |
|------|------|------|
| Organization ID | 是 | CircleCI 组织 ID |
| Project ID | 是 | CircleCI 项目 ID |
| Source Control URL | 是 | 源码仓库 URL |
| Branch | 否 | 限定特定分支 |

**CircleCI 环境变量（自动注入）：**

```bash
$CIRCLE_OIDC_TOKEN     # CircleCI OIDC Token（推荐）
$CIRCLE_OIDC_TOKEN_V2  # CircleCI OIDC Token V2
```

**CircleCI 配置示例：**

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
            # CIRCLE_OIDC_TOKEN 自动可用
            outerbounds configure --machine-user --oidc-token $CIRCLE_OIDC_TOKEN
            python my_flow.py argo-workflows create --production
```

---

### 认证方式 3：AWS IAM Role

适用于能够 Assume IAM Role 的系统（EC2 实例、ECS Task、Lambda 等）。

**配置步骤：**

**Phase 1：准备 IAM Role**

```json
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

**Phase 2：在 Outerbounds UI 创建 Machine User**

1. Users → Machines → Create New
2. 选择 "AWS IAM"
3. 关联上述 IAM Role ARN
4. 按需配置权限范围

---

## RBAC 角色权限

> **需要验证**：Outerbounds 文档未公开详细的 RBAC 角色矩阵。以下基于文档中散落的描述整理，具体权限定义以 Outerbounds Admin UI 中实际显示为准。

权限管理在 **Perimeter 级别**实施，同一用户在不同 Perimeter 可以有不同角色。

**已知权限区分：**

| 操作 | 普通用户 | 管理员 |
|------|---------|--------|
| 运行 Flow | 是 | 是 |
| 查看 Runs | 是（自己的，或同 Perimeter 下的）| 是（全部）|
| 创建 Workstation | 否 | 是 |
| 创建 Perimeter | 否 | 是 |
| 管理用户 | 否 | 是 |
| 配置 SSO | 否 | 是 |
| 创建 Machine Users | 否（需要验证）| 是 |

**Machine Users 的权限范围：**

Machine Users 也遵循 Perimeter 级别的权限控制，在创建时需要指定允许访问的 Perimeter，防止 CI/CD 管道越权访问敏感环境。

---

## 凭证安全最佳实践

```bash
# 1. 不要在代码中硬编码 PAT
# 错误示例：
token = "ob_xxxxxxxxxxxxxxxx"  # 不要这样做

# 2. 使用环境变量或配置文件
export METAFLOW_PROFILE=production
python my_flow.py argo-workflows create

# 3. CI/CD 中使用 Machine Users（不用 PAT）
# 参考上述 GitHub Actions / CircleCI 示例

# 4. 生产环境和开发环境使用不同的 PAT / Machine User
# 通过 Perimeter 隔离确保凭证不能越权
```

---

## 参考资料

- [Connect to Outerbounds](https://docs.outerbounds.com/outerbounds/connect-to-outerbounds/)
- [Programmatic access via machine users](https://docs.outerbounds.com/outerbounds/machine-users/)
- [Configure an IAM role](https://docs.outerbounds.com/outerbounds/iam-role/)

*最后更新：2026-04-13*
