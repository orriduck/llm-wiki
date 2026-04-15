# Wiki 日志

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
