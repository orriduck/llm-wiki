# Outerbounds Overview / Outerbounds 概览

> Outerbounds is a managed ML/AI platform built by the Netflix Metaflow core team, deployed in the customer's own cloud account using a BYOC (Bring Your Own Cloud) model. Essentially "enterprise-grade Metaflow as a Service."

> Outerbounds 是 Netflix Metaflow 核心团队打造的托管式 ML/AI 平台，采用 BYOC（Bring Your Own Cloud）模式部署在用户自己的云账号内。本质上是"企业级 Metaflow as a Service"。

Related notes / 相关笔记：[[Metaflow工作流框架]] | [[Outerbounds-Perimeter]] | [[Outerbounds-Workstations]] | [[Outerbounds-认证与权限]] | [[Outerbounds-部署与调度]] | [[Outerbounds-依赖管理]] | [[Outerbounds-特有装饰器]] | [[Outerbounds-配置与CLI]]

---

## Platform Positioning / 平台定位

Outerbounds' core value proposition: add enterprise-grade features while keeping all open-source Metaflow APIs unchanged.

> Outerbounds 的核心价值主张：在保留所有开源 Metaflow API 不变的前提下，叠加企业级功能。

| Dimension / 维度 | Open-Source Metaflow (Self-Hosted) / 开源 Metaflow（自建） | Outerbounds Managed Platform / Outerbounds 托管平台 |
|------|-------------------|--------------------|
| Deployment / 部署方式 | Build infrastructure yourself / 自己搭建基础设施 | CloudFormation/Terraform templates, ~15 min setup / 模板，约 15 分钟完成 |
| Metadata Service / 元数据服务 | Self-operated / 自己运维 | Platform-managed, BYOC in customer account / 平台托管，BYOC 部署在客户账号内 |
| Remote Dev Env / 远程开发环境 | None / 无 | Built-in Cloud Workstations / 内置 Cloud Workstations |
| Access Isolation / 权限隔离 | Cloud-native IAM / 依赖云原生 IAM | Perimeter (logical isolation) + RBAC / Perimeter（逻辑隔离环境）+ RBAC |
| Auth / 认证 | Custom or none / 自定义或无 | SSO (Google/Azure AD/Okta) + PAT + Machine Users |
| Production Scheduler / 生产调度器 | Self-built Argo/SFN / 需自建 Argo/SFN | Managed Argo Workflows / 托管 Argo Workflows |
| Dependency Mgmt / 依赖管理 | @conda/@pypi + manual Docker | Fast Bakery auto-containerization / 自动容器化 |
| UI | Open-source Metaflow UI (optional) / 开源 Metaflow UI（可选） | Unified Outerbounds UI / 统一 Outerbounds UI |
| Data Sovereignty / 数据主权 | Fully in own account / 完全在自己账号内 | Fully in own account (BYOC) / 完全在自己账号内（BYOC） |

---

## BYOC Architecture Model / BYOC 架构模型

Outerbounds is **not** SaaS (data never leaves the customer account) — it is a platform deployed within the customer's cloud account.

> Outerbounds **不是** SaaS（数据不出客户账号），而是部署在客户云账号内的平台。

```
┌────────────────────────────────────────────┐
│     Customer Cloud Account (Data Plane)    │
│           客户云账号（数据平面）              │
│                                            │
│  ┌──────────────┐  ┌────────────────────┐  │
│  │  Kubernetes  │  │  Cloud             │  │
│  │ (EKS/GKE/AKS)│  │  Workstations      │  │
│  └──────────────┘  └────────────────────┘  │
│                                            │
│  ┌──────────────┐  ┌────────────────────┐  │
│  │  Metadata    │  │  Object Storage    │  │
│  │  Service     │  │  (S3/GCS/Blob)     │  │
│  │ (PostgreSQL) │  │                    │  │
│  └──────────────┘  └────────────────────┘  │
│                                            │
│  ┌──────────────┐  ┌────────────────────┐  │
│  │  Argo        │  │  Perimeters        │  │
│  │  Workflows   │  │  (Isolation Envs)  │  │
│  │              │  │  （隔离环境）        │  │
│  └──────────────┘  └────────────────────┘  │
└────────────────────────────────────────────┘
         ↕ Only platform health telemetry sent
         ↕ 仅发送平台健康遥测数据
┌────────────────────────────────────────────┐
│  Outerbounds Control Plane (Outerbounds Co)│
│     Outerbounds 控制平面（Outerbounds 公司） │
│  (Does not store any customer data or code)│
│  （不存储任何客户业务数据或代码）             │
└────────────────────────────────────────────┘
```

**Key Data Sovereignty Guarantees / 关键数据主权保障：**

- All compute, data, metadata, and artifacts remain in the customer's cloud account.
- The Outerbounds control plane only receives platform health telemetry (not business data).
- Code and models never leave the customer's cloud account.

> - 所有计算、数据、元数据、Artifact 全部在客户云账号内
> - Outerbounds 控制平面只接收平台健康遥测（非业务数据）
> - 代码和模型不离开客户云账号

---

## Supported Cloud Platforms / 支持的云平台

| Cloud Platform / 云平台 | Compute Engine / 计算引擎 | Scheduler / 调度器 | Object Storage / 对象存储 |
|--------|---------|--------|---------|
| AWS | EKS (Kubernetes) / AWS Batch | Argo Workflows / AWS Step Functions | S3 |
| Google Cloud | GKE (Kubernetes) | Argo Workflows | GCS |
| Azure | AKS (Kubernetes) | Argo Workflows | Azure Blob Storage |
| On-Premises / Hybrid / 本地 / 混合云 | Kubernetes + Slurm | Argo Workflows | Object Storage (customizable) / 对象存储（可自定义） |

Deployment methods: CloudFormation (AWS one-click install) or Terraform modules (for teams already using Terraform).

> 部署方式：CloudFormation（AWS 一键安装）或 Terraform 模块（适合已用 Terraform 的团队）。

---

## Core Components Overview / 核心组件概览

### Perimeter (Permission Boundary) / Perimeter（权限边界）

A logically isolated execution environment. Each Perimeter has independent metadata, user permissions, IAM roles, and policies. Typical use: isolating dev/staging/production environments. See [[Outerbounds-Perimeter]].

> 逻辑隔离的执行环境，每个 Perimeter 有独立的元数据、用户权限、IAM 角色和策略。典型用途：隔离 dev/staging/production 环境。详见 [[Outerbounds-Perimeter]]。

### Workstations (Cloud Dev Environment) / Workstations（云端开发环境）

Personal development environments running in the customer's cloud account, accessible via VSCode extension or browser. Data stays in the cloud account, consistent with the production environment. See [[Outerbounds-Workstations]].

> 运行在客户云账号内的个人开发环境，通过 VSCode 扩展或浏览器访问。数据不出云账号，与生产环境一致。详见 [[Outerbounds-Workstations]]。

### Fast Bakery (Dependency Management) / Fast Bakery（依赖管理）

Automatically converts `@pypi`/`@conda` declarations into container images without writing Dockerfiles. Extremely fast image builds (seconds for dependency resolution, 6.7GB images in under 40 seconds). See [[Outerbounds-依赖管理]].

> 自动将 `@pypi`/`@conda` 声明转换为容器镜像，无需手写 Dockerfile。镜像构建速度极快（秒级解析，40 秒内完成 6.7GB 镜像）。详见 [[Outerbounds-依赖管理]]。

### Outerbounds UI

A unified web interface that includes:

> 统一的 Web 界面，包含：

- **Runs**: View all Flow execution records, DAG visualization, real-time logs, Artifact viewing
- **Cards**: Custom HTML visualization reports generated by the `@card` decorator
- **Workstations**: Manage development environment states
- **Admin**: User management, Perimeter configuration, SSO integration

> - **Runs**：查看所有 Flow 执行记录、DAG 可视化、实时日志、Artifact 查看
> - **Cards**：由 `@card` 装饰器生成的自定义 HTML 可视化报告
> - **Workstations**：管理开发环境状态
> - **Admin**：用户管理、Perimeter 配置、SSO 集成

---

## API Compatibility with Open-Source Metaflow / 与开源 Metaflow 的 API 兼容性

**Core principle: All open-source Metaflow APIs work on Outerbounds without any code changes.**

> **核心原则：所有开源 Metaflow API 在 Outerbounds 上完全可用，无需改动代码。**

Outerbounds provides the following on top of the open-source API:

> Outerbounds 在开源 API 之上额外提供：

| Feature / 功能 | Open-Source Metaflow / 开源 Metaflow | Outerbounds Enhancement / Outerbounds 增强 |
|------|-------------|----------------|
| `@kubernetes` | Available in open source / 开源可用 | Adds `compute_pool` parameter / 增加 `compute_pool` 参数 |
| `@conda`/`@pypi` | Available in open source / 开源可用 | Fast Bakery acceleration / Fast Bakery 加速 |
| `@secrets` | Requires extension / 需要扩展 | Native AWS Secrets Manager integration / 原生集成 AWS Secrets Manager |
| `@checkpoint` | Requires `metaflow-checkpoint` package / 需要包 | Deep platform integration / 平台深度集成 |
| `@model` | Requires `metaflow-checkpoint` package / 需要包 | Cross-cloud model loading / 跨云模型加载 |
| `@huggingface_hub` | Requires `metaflow-checkpoint` package / 需要包 | HuggingFace model caching / HuggingFace 模型缓存 |
| `@torchrun` | Requires `metaflow-torchrun` package / 需要包 | Distributed PyTorch training / 分布式 PyTorch 训练 |
| `@gpu_profile` | Requires `metaflow-gpu-profile` package / 需要包 | GPU usage visualization / GPU 使用可视化 |
| Perimeters | None / 无 | Platform-exclusive feature / 平台特有功能 |
| Machine Users | None / 无 | Unattended CI/CD auth / CI/CD 无人值守认证 |

---

## Quick Start Guide / 快速上手流程

```bash
# 1. Install CLI / 安装 CLI
pip install -U outerbounds

# 2. Get token from Outerbounds UI and configure local env
# 从 Outerbounds UI 获取 token，配置本地环境
outerbounds configure <token-from-ui>

# 3. Verify connection / 验证连接
outerbounds check -v

# 4. Run your first Flow / 运行第一个 Flow
python my_flow.py run

# 5. Scale to cloud compute / 扩展到云计算
python my_flow.py run --with kubernetes

# 6. Deploy to production / 部署到生产
python my_flow.py argo-workflows create --production
```

---

## References / 参考资料

- [Outerbounds Documentation Home](https://docs.outerbounds.com/)
- [Architecture Explained (Blog)](https://outerbounds.com/blog/architecture-explained)
- [Perimeters Launch Announcement (Blog)](https://outerbounds.com/blog/deploy-ml-ai-confidently)
- [Fast Bakery Introduction (Blog)](https://outerbounds.com/blog/containerize-with-fast-bakery)

*Last updated / 最后更新：2026-04-13*
