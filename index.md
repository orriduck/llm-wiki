# Wiki 索引

## Metaflow / Outerbounds

| 页面 | 摘要 |
|------|------|
| [[Metaflow工作流框架]] | FlowSpec、step、artifact、装饰器速查、Client API、开发模式与最佳实践 |
| [[Outerbounds概览]] | BYOC 架构、平台定位、与自建 Metaflow 的差异对比、支持的云平台 |
| [[Outerbounds-Perimeter]] | Perimeter 核心概念、创建配置步骤、IAM Role 绑定、RBAC 权限、Perimeter Policy、多环境隔离策略 |
| [[Outerbounds-Workstations]] | Workstation 架构、管理员创建步骤、VSCode 扩展连接、Web UI、开发工作流、生命周期管理 |
| [[Outerbounds-认证与权限]] | 个人 PAT、Machine Users（GitHub OIDC / CircleCI / AWS IAM）、SSO 集成、RBAC 权限模型 |
| [[Outerbounds-部署与调度]] | Argo Workflows 部署、`@project` 装饰器、`--production`/`--branch`、`@schedule`/`@trigger`、CI/CD 集成 |
| [[Outerbounds-依赖管理]] | fast-bakery 原理与用法、`@conda`/`@pypi` 在 OB 上的行为、Perimeter Policy 对依赖的影响、自定义镜像 |
| [[Outerbounds-特有装饰器]] | `@secrets`、`@checkpoint`、`@model`、`@huggingface_hub`、`@kubernetes`（完整参数）、`@gpu_profile`、`@torchrun`、`@metaflow_ray` |
| [[Outerbounds-配置与CLI]] | `~/.metaflowconfig` 完整字段（OB 版本）、多 profile 管理、`outerbounds` CLI 命令、`METAFLOW_PROFILE` |

## AWS

| 页面 | 摘要 |
|------|------|
| [[AWS与Metaflow]] | AWS 架构（S3/Batch/ECR/Step Functions）、IAM 权限、Outerbounds vs 自建 |
| [[S3]] | 对象存储、存储类别、权限控制、加密、版本控制、生命周期、事件通知、性能优化 |
| [[Lambda]] | 无服务器计算、触发方式、Layer、并发控制、冷启动优化、错误处理与重试 |
| [[EventBridge]] | 事件总线、规则与目标、模式匹配、Scheduler、Pipes、Archive/Replay、跨账户 |
| [[CloudWatch]] | 指标、日志、告警、仪表盘、Logs Insights 查询、EMF、异常检测 |
| [[CloudTrail]] | API 审计日志、事件类型、CloudTrail Lake SQL 查询、安全调查、组织级 Trail |

## 工程规范 / 架构

| 页面 | 摘要 |
|------|------|
| [[Poetry]] | 安装与初始化、pyproject.toml 结构、依赖管理命令、虚拟环境、发布包、与 pip 对比 |
| [[uv]] | 极速 Python 包管理器（Rust）、uv init/add/sync/run/tool、workspace 支持、Poetry 迁移指南 |
| [[black]] | 不妥协的代码格式化工具、配置选项、magic trailing comma、与 isort 集成、pre-commit |
| [[black-uv]] | 在 uv 项目中使用 black：uv add/run、uvx、pre-commit 集成 |
| [[isort]] | import 语句排序工具、black 兼容模式（profile="black"）、配置选项、pre-commit |
| [[mypy]] | Python 静态类型检查、配置选项、类型注解速查、stub 包、渐进式类型化策略 |
| [[ruff]] | Rust 编写的极速 linter + formatter，替代 black + isort + flake8，uvx 直接运行 |
| [[pyright]] | 微软静态类型检查器（Pylance 底层），比 mypy 快 3-5 倍，渐进式 strict 模式 |

## UI / UX

| 页面 | 摘要 |
|------|------|
| （待添加） | |
