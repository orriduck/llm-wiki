# Wiki 日志

## [2026-04-16] ingest | Terraform & OpenTofu 系列文章

整理 Terraform 与 OpenTofu 的完整知识体系，包括基础使用、优势对比及迁移指南，新建 IaC 分类。

**创建页面：**
- `wiki/iac/Terraform基础与AWS部署.md` — HCL 核心概念（provider/resource/state/variable/module）、核心工作流（init/plan/apply/destroy）、S3/EC2/Lambda/RDS 完整 AWS 部署示例、项目结构最佳实践、常用命令速查
- `wiki/iac/OpenTofu简介与优势.md` — BSL 许可证变更背景、MPL 2.0 vs BSL 对比、Linux Foundation 治理模式、原生 state 加密特性（AES-GCM/AWS KMS）、provider 自定义函数、与 Terraform 功能对比表、生态工具支持（Terragrunt/Atlantis/Checkov 等）
- `wiki/iac/Terraform到OpenTofu迁移.md` — 迁移前检查清单、多平台安装方式（Homebrew/APT/tofuenv）、state 备份与验证、tofu init 流程、CI/CD 更新（GitHub Actions/Atlantis）、Terraform Cloud 迁移、state 加密启用、回滚方案、迁移复杂度矩阵

**更新页面：**
- `index.md` — 新增"基础设施即代码（IaC）"分类，添加 3 个页面索引

---

## [2026-04-15] maintain | 整理与隐私清洗

对 `Outerbounds-在Flow外使用IAM角色.md` 进行隐私清洗（移除真实 AWS 账户 ID、内部 URL、公司名称），转为双语格式，添加到 index.md。移除 index 中空的 UI/UX 分类。

**更新页面：**
- `wiki/metaflow/Outerbounds-在Flow外使用IAM角色.md` — 隐私清洗 + 双语化
- `index.md` — 添加缺失页面索引，移除空分类

---

## [2026-04-15] ingest | 如何充分利用一对一

根据公司内部指南整理，涵盖一对一最佳实践及 L1–L8 各级别具体话题指导。

**创建页面：**
- `wiki/career/如何充分利用一对一.md` — 关系演变模型、七条最佳实践、L1–L8 各级别核心话题与注意事项

**更新页面：**
- `index.md` — 新增"职业发展"分类，添加页面索引

---

## [2026-04-15] ingest | Claude Code 插件与 MCP 生态

根据实际操作会话（d2ee5346-3090-4cd4-b6cc-547a52485680），整理 Claude Code 插件管理工作流、superpowers/github 插件安装、Chrome DevTools MCP 工具体系。

**创建页面：**
- `wiki/engineering/Claude-Code插件与MCP.md` — 插件管理命令、superpowers/github 插件、Skills 体系、Chrome DevTools MCP 工具速查、标准操作流程

**更新页面：**
- `index.md` — 在"工程规范 / 架构"分类添加 Claude-Code插件与MCP 索引

---

## [2026-04-15] ingest | OpenClaw vs Claude 智能体笔记

搜集 OpenClaw 开源框架与 Anthropic Claude Managed Agents 最新资料，新建 AI 智能体分类，创建 3 篇 wiki 页面。

**创建页面：**
- `wiki/ai-agents/OpenClaw概览.md` — 背景发展、Gateway 架构、SOUL.md/HEARTBEAT.md 配置文件系统、Heartbeat 自然语言调度、多平台集成（WhatsApp/Discord/Telegram）、ClawHub 插件生态（15,000+ AgentSkills）、模型无关性、v4.0 多 Agent 路线图、OpenClaw Foundation 治理
- `wiki/ai-agents/Claude-Managed-Agents.md` — 2026-04-08 发布背景、托管执行环境与安全沙盒、Agent Teams + Subagents 协作模式、Claude Cowork 计算机控制、Dispatch 手机远程任务（研究预览）、定时任务配置、$0.08/会话小时计费、Notion/Asana/Sentry 早期用户案例
- `wiki/ai-agents/OpenClaw-vs-Claude.md` — 定位对比表、执行模式差异、架构关系（互补非竞争）、Anthropic 跟进时间线、场景选型指南、成本对比模型、关键洞察（开源探路商业收割）

**更新页面：**
- `index.md` — 新增"AI 智能体"分类，添加 3 个页面索引

---

## [2026-04-15] ingest | S3 → Lambda 触发器完整指南

根据对话中的 AWS 问答，结合官方文档和网络搜索整理，新增 S3 Lambda 触发器专题页面。

**创建页面：**
- `wiki/aws/S3-Lambda触发器.md` — 触发机制、所有事件类型、完整 Event JSON 结构、多文件上传行为、权限配置（Console vs CLI 差异）、错误处理与重试、常见陷阱（循环触发/Key 解码/跨 Region）、进阶方案（EventBridge/SQS）、Lambda 代码示例（转发 endpoint / 读文件内容 / 幂等处理）

**更新页面：**
- `index.md` — 添加 S3-Lambda触发器页面索引

## [2026-04-13] init | 初始化 wiki

从 Claude Code 记忆中提取工作相关内容，建立初始 wiki 结构。

**创建页面：**
- `wiki/Python工具链.md` — Poetry、black、isort、pytest 规范
- `wiki/AWS与Metaflow.md` — Metaflow 框架和 AWS 服务映射

**待补充：**
- AWS 账户/IAM 具体配置
- 更多 Metaflow 装饰器用法
- 其他工作领域页面

## [2026-04-16] ingest | Python PII 检测库对比

研究并整理主流 Python PII（个人身份信息）检测库横向对比页面。

**创建页面：**
- `wiki/engineering/python-pii库对比.md` — 7 个主流库的详细对比，覆盖使用难度、可扩展性、检测准确度、支持的 PII 类型、多语言支持、维护状态；含快速选型表、综合对比表、多语言中文适配说明

**覆盖库：** Microsoft Presidio、scrubadub、DataFog、PIICatcher、detect-secrets、pii-masker（HydroXai）、pii-codex

**更新页面：**
- `index.md` — 添加 python-pii库对比 条目

---

## [2026-04-14] ingest | fish shell 使用指南

新增 fish shell 工具页面，涵盖安装、设置默认 shell、配置、语法速查、插件管理。

**创建页面：**
- `wiki/engineering/fish.md` — fish shell 优势、安装（macOS/Linux）、chsh 设为默认 shell、config.fish 配置、语法速查（变量/条件/循环/函数）、abbr 缩写、Fisher 插件管理器、常用插件（Tide/Starship/fzf.fish/z.fish）、与 bash 兼容性说明

**更新页面：**
- `index.md` — 添加 fish shell 页面索引

---

## [2026-04-13] ingest | AWS 核心服务独立页面

为 5 个 AWS 重点服务各创建独立 wiki 页面，从 AWS与Metaflow 中拆分出通用知识。

**创建页面：**
- `wiki/aws/S3.md` — 对象存储、存储类别、权限、加密、版本控制、生命周期、性能优化
- `wiki/aws/Lambda.md` — 无服务器计算、触发方式、Layer、并发控制、冷启动、重试
- `wiki/aws/EventBridge.md` — 事件总线、规则匹配、Scheduler、Pipes、Archive/Replay
- `wiki/aws/CloudWatch.md` — 指标、日志、告警、Logs Insights、EMF、异常检测
- `wiki/aws/CloudTrail.md` — API 审计、事件类型、Lake 查询、安全调查

**更新页面：**
- `index.md` — 添加 5 个 AWS 服务页面索引
