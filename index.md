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
| [[Outerbounds-特有装饰器]] | `@secrets`、`@checkpoint`、`@model`、`@huggingface_hub`、`@kubernetes`（完整参数）、`@gpu_profile`、`@torchrun`、`@metaflow_ray`、`@retry` |
| [[Outerbounds-入门三部曲]] | 本地→云端→生产三步路径、`foreach`并行、`@resources`、PyTorch GPU镜像示例、`@retry`、`@schedule`、`@project` 速查 |
| [[Outerbounds-配置与CLI]] | `~/.metaflowconfig` 完整字段（OB 版本）、多 profile 管理、`outerbounds` CLI 命令、`METAFLOW_PROFILE` |
| [[Outerbounds-在Flow外使用IAM角色]] | 在 Flow 外使用 `obp-*-task` 角色访问 AWS 资源的 5 种方法、认证链原理、角色命名规则 |
| [[Outerbounds-Branch-Resolution]] | Outerbounds 分支解析机制：`--production` / `--branch` 命名空间映射、CI 分支决策、常见错误与防护 |
| [[Metaflow-FanOut-Join模式]] | Fan-out/join 并行数据加载模式、merge_artifacts、PyArrow S3FileSystem 读取、@card 摘要 |
| [[Metaflow-PreRun生命周期与FlowMutator]] | Pre-run 三阶段（config→mutate→check）、FlowMutator 独立执行、pre_mutate 静态分析模式 |
| [[Metaflow-打包文件选择机制]] | MetaflowPackage 文件选择：user code 目录遍历 + MetaflowCodeContentV1 模块解析、扫描范围对比 |

## AWS

| 页面 | 摘要 |
|------|------|
| [[S3]] | 对象存储、存储类别、权限控制、加密、版本控制、生命周期、事件通知、性能优化 |
| [[Lambda]] | 无服务器计算、触发方式、Layer、并发控制、冷启动优化、错误处理与重试 |
| [[S3-Lambda触发器]] | S3 PutObject 触发 Lambda 全攻略：事件类型、Event JSON 结构、多文件行为、权限配置、错误重试、常见陷阱、SQS/EventBridge 进阶方案 |
| [[EventBridge]] | 事件总线、规则与目标、模式匹配、Scheduler、Pipes、Archive/Replay、跨账户 |
| [[CloudWatch]] | 指标、日志、告警、仪表盘、Logs Insights 查询、EMF、异常检测 |
| [[CloudTrail]] | API 审计日志、事件类型、CloudTrail Lake SQL 查询、安全调查、组织级 Trail |
| [[Lambda-Layer构建与冷启动]] | Lambda Layer Docker 构建脚本（trap 清理）、冷启动 Secrets Manager 配置加载、Terraform 示例、pre-commit 集成 |

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
| [[fish]] | 友好交互式 shell：开箱即用自动建议/语法高亮，安装、设为默认 shell、Fisher 插件管理 |
| [[Claude-Code插件与MCP]] | Claude Code 插件管理工作流、superpowers/github/chrome-devtools-mcp/claude-hud/llm-wiki 插件、Skills 体系、MCP 工具速查 |
| [[Claude-Code-Skills自动激活]] | Skills 不可靠激活的根因、三级解法（优化描述/CLAUDE.md/自定义Hook）、skill-rules.json 配置、UserPromptSubmit Hook 骨架代码 |
| [[vue-number-flow]] | `@number-flow/vue` 数字滚动动效组件，METAR KPI 面板集成、格式化选项、slot 用法 |
| [[map-dead-reckoning-raf]] | requestAnimationFrame 地图标记死推算（匀速运动插值），30kt 速度阈值，箭头/圆点图标切换 |
| [[python-pii库对比]] | Python PII 检测库横向对比：Presidio、scrubadub、DataFog、PIICatcher、detect-secrets、pii-masker 等，覆盖使用难度、扩展性、准确度、支持范围 |
| [[importlib-resources]] | `importlib.resources.files()` 包内资源定位、vs `os.path` 对比、`__init__.py` 要求、Metaflow 远程执行注意事项 |
| [[pydantic-type-coercion]] | Pydantic 自动类型强制转换（string→date）、Parquet schema 兼容性陷阱、`str()` 回转、v1/v2 差异 |
| [[CircleCI-Orb文件结构]] | CircleCI Orb 标准目录：`src/@orb.yml`、commands/jobs/executors/examples、`dist/orb.yml` 及发布校验流程 |

## AI 智能体

| 页面 | 摘要 |
|------|------|
| [[OpenClaw概览]] | 开源执行型 Agent 框架：Gateway 架构、SOUL.md/HEARTBEAT.md 配置文件、定时调度、WhatsApp/Discord 集成、ClawHub 插件生态、多 Agent 路线图 |
| [[Claude-Managed-Agents]] | Anthropic 托管 Agent 服务（2026-04）：Agent Teams、Subagents、Claude Cowork 计算机控制、Dispatch 定时任务、$0.08/小时计费 |
| [[OpenClaw-vs-Claude]] | OpenClaw（开源框架）vs Claude（商业 LLM + Agent 服务）全面对比：定位、架构关系、成本、适用场景、Anthropic 跟进动作 |

## 基础设施即代码（IaC）

| 页面 | 摘要 |
|------|------|
| [[Terraform基础与AWS部署]] | HCL 核心概念、state/provider/module、S3/EC2/Lambda/RDS 完整部署示例、常用命令速查、项目结构最佳实践 |
| [[OpenTofu简介与优势]] | BSL 许可证风波背景、MPL 2.0 开源优势、Linux Foundation 治理、原生 state 加密、与 Terraform 功能对比、生态工具支持 |
| [[Terraform到OpenTofu迁移]] | 迁移前检查清单、安装方式、备份 state、`tofu init` 流程、更新 CI/CD、TFC 后端迁移、回滚方案、迁移复杂度矩阵 |

## 职业发展

| 页面 | 摘要 |
|------|------|
| [[如何充分利用一对一]] | 与经理一对一的最佳实践：七条核心原则 + L1–L8 各级别具体话题指导，关系从指导到战略伙伴的演变 |
