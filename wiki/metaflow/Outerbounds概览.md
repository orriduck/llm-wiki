# Outerbounds 概览

> Outerbounds 是 Netflix Metaflow 核心团队打造的托管式 ML/AI 平台，采用 BYOC（Bring Your Own Cloud）模式部署在用户自己的云账号内。本质上是"企业级 Metaflow as a Service"。

相关笔记：[[Metaflow工作流框架]] | [[Outerbounds-Perimeter]] | [[Outerbounds-Workstations]] | [[Outerbounds-认证与权限]] | [[Outerbounds-部署与调度]] | [[Outerbounds-依赖管理]] | [[Outerbounds-特有装饰器]] | [[Outerbounds-配置与CLI]]

---

## 平台定位

Outerbounds 的核心价值主张：在保留所有开源 Metaflow API 不变的前提下，叠加企业级功能。

| 维度 | 开源 Metaflow（自建） | Outerbounds 托管平台 |
|------|-------------------|--------------------|
| 部署方式 | 自己搭建基础设施 | CloudFormation/Terraform 模板，约 15 分钟完成 |
| 元数据服务 | 自己运维 | 平台托管，BYOC 部署在客户账号内 |
| 远程开发环境 | 无 | 内置 Cloud Workstations |
| 权限隔离 | 依赖云原生 IAM | Perimeter（逻辑隔离环境）+ RBAC |
| 认证 | 自定义或无 | SSO（Google/Azure AD/Okta）+ PAT + Machine Users |
| 生产调度器 | 需自建 Argo/SFN | 托管 Argo Workflows |
| 依赖管理 | @conda/@pypi + 手动 Docker | Fast Bakery 自动容器化 |
| UI | 开源 Metaflow UI（可选） | 统一 Outerbounds UI |
| 数据主权 | 完全在自己账号内 | 完全在自己账号内（BYOC） |

---

## BYOC 架构模型

Outerbounds **不是** SaaS（数据不出客户账号），而是部署在客户云账号内的平台。

```
┌────────────────────────────────────────────┐
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
│  │  Workflows   │  │  (隔离环境)         │  │
│  └──────────────┘  └────────────────────┘  │
└────────────────────────────────────────────┘
         ↕ 仅发送平台健康遥测数据
┌────────────────────────────────────────────┐
│     Outerbounds 控制平面（Outerbounds 公司） │
│  （不存储任何客户业务数据或代码）             │
└────────────────────────────────────────────┘
```

**关键数据主权保障：**
- 所有计算、数据、元数据、Artifact 全部在客户云账号内
- Outerbounds 控制平面只接收平台健康遥测（非业务数据）
- 代码和模型不离开客户云账号

---

## 支持的云平台

| 云平台 | 计算引擎 | 调度器 | 对象存储 |
|--------|---------|--------|---------|
| AWS | EKS（Kubernetes）/ AWS Batch | Argo Workflows / AWS Step Functions | S3 |
| Google Cloud | GKE（Kubernetes） | Argo Workflows | GCS |
| Azure | AKS（Kubernetes） | Argo Workflows | Azure Blob Storage |
| 本地 / 混合云 | Kubernetes + Slurm | Argo Workflows | 对象存储（可自定义） |

部署方式：CloudFormation（AWS 一键安装）或 Terraform 模块（适合已用 Terraform 的团队）。

---

## 核心组件概览

### Perimeter（权限边界）
逻辑隔离的执行环境，每个 Perimeter 有独立的元数据、用户权限、IAM 角色和策略。典型用途：隔离 dev/staging/production 环境。详见 [[Outerbounds-Perimeter]]。

### Workstations（云端开发环境）
运行在客户云账号内的个人开发环境，通过 VSCode 扩展或浏览器访问。数据不出云账号，与生产环境一致。详见 [[Outerbounds-Workstations]]。

### Fast Bakery（依赖管理）
自动将 `@pypi`/`@conda` 声明转换为容器镜像，无需手写 Dockerfile。镜像构建速度极快（秒级解析，40 秒内完成 6.7GB 镜像）。详见 [[Outerbounds-依赖管理]]。

### Outerbounds UI
统一的 Web 界面，包含：
- **Runs**：查看所有 Flow 执行记录、DAG 可视化、实时日志、Artifact 查看
- **Cards**：由 `@card` 装饰器生成的自定义 HTML 可视化报告
- **Workstations**：管理开发环境状态
- **Admin**：用户管理、Perimeter 配置、SSO 集成

---

## 与开源 Metaflow 的 API 兼容性

**核心原则：所有开源 Metaflow API 在 Outerbounds 上完全可用，无需改动代码。**

Outerbounds 在开源 API 之上额外提供：

| 功能 | 开源 Metaflow | Outerbounds 增强 |
|------|-------------|----------------|
| `@kubernetes` | 开源可用 | 增加 `compute_pool` 参数 |
| `@conda`/`@pypi` | 开源可用 | Fast Bakery 加速 |
| `@secrets` | 需要扩展 | 原生集成 AWS Secrets Manager |
| `@checkpoint` | 需要 `metaflow-checkpoint` 包 | 平台深度集成 |
| `@model` | 需要 `metaflow-checkpoint` 包 | 跨云模型加载 |
| `@huggingface_hub` | 需要 `metaflow-checkpoint` 包 | HuggingFace 模型缓存 |
| `@torchrun` | 需要 `metaflow-torchrun` 包 | 分布式 PyTorch 训练 |
| `@gpu_profile` | 需要 `metaflow-gpu-profile` 包 | GPU 使用可视化 |
| Perimeters | 无 | 平台特有功能 |
| Machine Users | 无 | CI/CD 无人值守认证 |

---

## 快速上手流程

```bash
# 1. 安装 CLI
pip install -U outerbounds

# 2. 从 Outerbounds UI 获取 token，配置本地环境
outerbounds configure <token-from-ui>

# 3. 验证连接
outerbounds check -v

# 4. 运行第一个 Flow
python my_flow.py run

# 5. 扩展到云计算
python my_flow.py run --with kubernetes

# 6. 部署到生产
python my_flow.py argo-workflows create --production
```

---

## 参考资料

- [Outerbounds 文档主页](https://docs.outerbounds.com/)
- [架构解析（Blog）](https://outerbounds.com/blog/architecture-explained)
- [Perimeters 发布公告（Blog）](https://outerbounds.com/blog/deploy-ml-ai-confidently)
- [Fast Bakery 介绍（Blog）](https://outerbounds.com/blog/containerize-with-fast-bakery)

*最后更新：2026-04-13*
