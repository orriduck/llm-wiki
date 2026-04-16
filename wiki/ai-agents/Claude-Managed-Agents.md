# Claude Managed Agents / Claude 托管智能体

> Anthropic's managed Agent infrastructure service launched on April 8, 2026, fully hosting the runtime environment, sandbox, state management, and other "heavy lifting" for Agents.
> See [[OpenClaw概览]] for the open-source counterpart.
> See [[OpenClaw-vs-Claude]] for a positioning comparison.

> Anthropic 于 2026 年 4 月 8 日推出的托管 Agent 基础设施服务，将 Agent 的运行环境、沙盒、状态管理等"重活"全部托管化。
> 参见 [[OpenClaw概览]] 了解开源对标方案。
> 参见 [[OpenClaw-vs-Claude]] 了解两者定位对比。

## Table of Contents / 目录

- [[#Background: Why Managed Agents / 背景：为什么需要 Managed Agents]]
- [[#Core Capabilities / 核心能力]]
- [[#Agent Types / Agent 类型]]
- [[#Claude Cowork]]
- [[#Dispatch & Scheduled Tasks / Dispatch 与定时任务]]
- [[#Pricing Model / 计费模式]]
- [[#Early Adopter Cases / 早期用户案例]]
- [[#Relationship with OpenClaw / 与 OpenClaw 的关系]]
- [[#Technical Limitations & Notes / 技术限制与注意事项]]

---

## Background: Why Managed Agents / 背景：为什么需要 Managed Agents

Common pain points in autonomous Agent development:

> 自主 Agent 开发面临的通用痛点：

| Problem / 问题 | Description / 说明 |
|------|------|
| **Sandbox setup / 沙盒搭建** | Need a securely isolated execution environment to prevent Agent privilege escalation / 需要安全隔离的执行环境，防止 Agent 越权操作 |
| **State persistence / 状态持久化** | How to recover when a long-running task disconnects mid-way? / 长任务中途断线后如何恢复？ |
| **Scaling / 扩缩容** | How to schedule when concurrent Agent count surges? / 并发 Agent 数量激增时如何调度？ |
| **Monitoring & audit / 监控与审计** | What did the Agent do? How to troubleshoot errors? / Agent 做了什么？出错了如何排查？ |
| **Infrastructure maintenance / 基础设施维护** | Servers, networking, security patches... time-consuming and labor-intensive / 服务器、网络、安全补丁……耗时耗力 |

Managed Agents' positioning: **"Turn prototypes into production in days, not months."**

> Managed Agents 的定位：**"把原型变成生产只需几天，而非几个月"**。

---

## Core Capabilities / 核心能力

Managed Agents is a **composable API suite** for building and deploying cloud-hosted autonomous Agents:

> Managed Agents 是一套**可组合的 API 套件**，用于构建和部署云端托管的自主 Agent：

### Managed Execution Environment / 托管执行环境

- Fully managed Agent harness, performance-optimized / 完全托管的 Agent harness，针对性能调优
- **Secure sandbox**: isolated execution, prevents lateral movement / **安全沙盒**：隔离执行，防止横向移动
- **Built-in tools**: file operations, code execution, browser control, etc. out of the box / **内置工具**：文件操作、代码执行、浏览器控制等开箱即用
- **SSE streaming**: real-time Agent execution status push (Server-Sent Events) / **SSE 流式传输**：实时接收 Agent 执行状态推送（Server-Sent Events）

### State Management / 状态管理

- **Auto-recovery** after session interruption: progress and output are not lost / 会话中断后**自动恢复**：进度和输出不丢失
- Persistent state storage across sessions / 跨会话的持久状态存储
- Supports continuous runs spanning up to **14.5 hours** (based on 1M token context window) / 支持长达 **14.5 小时任务跨度**的持续运行（基于 100 万 Token 上下文窗口）

### Production-Grade Infrastructure / 生产级基础设施

- Anthropic handles hosting, scaling, and monitoring / Anthropic 负责托管、扩缩容和监控
- Built-in authentication and access control / 认证与访问控制内置
- Enterprise-grade admin console (feature access management, usage tracking, cost control) / 企业级管理员控制台（Feature 访问管理、用量追踪、费用控制）

---

## Agent Types / Agent 类型

Managed Agents provides two collaboration modes:

> Managed Agents 提供两种协作模式：

### Agent Teams / 多 Agent 团队

```
Team Coordinator
    ├── Agent A (independent context)
    ├── Agent B (independent context)
    └── Agent C (independent context)
```

- Multiple Claude instances each with **independent context** / 多个 Claude 实例各自拥有**独立上下文**
- Agents can **communicate directly** with each other / Agent 之间可**直接通信**
- Suited for large-scale parallel task decomposition / 适合大规模并行任务分解

### Subagents / 子智能体

```
Main Agent
    └── Subagent (same session)
         └── Reports results to Main Agent only
```

- Runs within the same session / 在同一会话内运行
- Lightweight, only returns results to the Main Agent / 轻量，只向主 Agent 返回结果
- Suited for simple capability delegation / 适合简单的功能委托

---

## Claude Cowork

Claude Cowork is an Agent workspace for individuals and teams, focused on **local computer control**:

> Claude Cowork 是面向个人和团队的 Agent 工作台，重点在于**本地计算机控制**：

### Computer Use / 计算机控制

Claude can directly control the user's local machine:

> Claude 可以直接操控用户本机：

- Click, type, scroll (mouse/keyboard control) / 点击、输入、滚动（鼠标/键盘控制）
- Open and manipulate local files / 打开和操作本地文件
- Control browser to complete web tasks / 控制浏览器完成 Web 任务
- Prioritizes precise Connectors (e.g., Slack, Google Calendar); falls back to screen control when no Connector is available / 优先调用精准 Connector（如 Slack、Google Calendar），无 Connector 时回退到屏幕控制

### Workflow / 工作流

1. User assigns task via Cowork or Dispatch / 用户通过 Cowork 或 Dispatch 分配任务
2. Claude selects the most appropriate tool (Connector -> browser control -> screen control) / Claude 选择最合适的工具（Connector → 浏览器控制 → 屏幕控制）
3. Autonomously completes task and notifies user upon completion / 自主完成任务，完成后通知用户

---

## Dispatch & Scheduled Tasks / Dispatch 与定时任务

### Dispatch (Research Preview, March 2026) / Dispatch（研究预览，2026 年 3 月）

Lets users remotely control desktop Cowork sessions from their **phone**:

> 让用户在**手机**上远程操控桌面 Cowork 会话：

```
Phone Dispatch App
    → Send task instruction
    → Claude Desktop receives and executes
    → Push notification to phone upon completion
```

Use cases:

> 使用场景：

- Assign tasks while away, review results when back / 外出时分配任务，回来看结果
- One continuous conversation, seamless switching between phone and desktop / 一个连续对话，手机和桌面无缝切换

### Scheduled Tasks / 定时任务

Available plans: **Pro, Max, Team, Enterprise**

> 可用计划：**Pro、Max、Team、Enterprise**

| Feature / 特性 | Description / 说明 |
|------|------|
| **Custom frequency / 自定义频率** | Daily, weekly, custom intervals / 每天、每周、自定义间隔 |
| **Task content / 任务内容** | Search Slack, query files, web research, generate reports / 搜索 Slack、查询文件、Web 调研、生成报告 |
| **Tool inheritance / 工具继承** | Uses all Connectors and Plugins the user has configured / 使用用户已配置的全部 Connector 和 Plugin |
| **Persistent instructions / 持久指令** | Claude saves the prompt as a task instruction, runs automatically on schedule / Claude 保存 Prompt 作为任务指令，按节奏自动运行 |

Examples:

> 示例：

- "Summarize yesterday's important Slack messages every morning" / "每天早上汇总昨日 Slack 重要消息"
- "Pull last week's metrics every Monday and generate a PDF report" / "每周一拉取上周指标并生成 PDF 报告"
- "Monitor competitor websites for changes and notify me when updated" / "监控竞品官网变动，有更新时通知我"

---

## Pricing Model / 计费模式

```
Total cost = Token cost (standard Claude API pricing)
           + Session duration fee ($0.08 / session-hour)
```

Suited for high-frequency, long-running Agent scenarios; not economical for short conversations — use the standard API instead.

> 适合高频、长时运行的 Agent 场景；短对话不经济，用标准 API 更合适。

---

## Early Adopter Cases / 早期用户案例

| Company / 公司 | Use Case / 应用场景 |
|------|----------|
| **Notion** | AI-assisted document organization and knowledge base maintenance / AI 辅助文档整理与知识库维护 |
| **Asana** | Automated project task assignment and tracking / 项目任务自动化分配与跟踪 |
| **Sentry** | Error log analysis and auto-generated fix suggestions / 错误日志分析与自动生成修复建议 |

---

## Relationship with OpenClaw / 与 OpenClaw 的关系

| Dimension / 维度 | OpenClaw | Claude Managed Agents |
|------|----------|-----------------------|
| **Positioning / 定位** | Open-source framework, self-deployed / 开源框架，用户自部署 | Managed service, Anthropic-operated / 托管服务，Anthropic 运维 |
| **Infrastructure / 基础设施** | User-managed / 用户自建 | Fully managed by Anthropic / Anthropic 全权负责 |
| **Model / 模型** | Model-agnostic (Claude/DeepSeek/local) / 模型无关（可用 Claude/DeepSeek/本地） | Bound to Claude / 绑定 Claude |
| **Cost / 成本** | Free framework + API fees / 框架免费 + API 费用 | API fees + $0.08/hr / API 费用 + $0.08/小时 |
| **Onboarding difficulty / 上手难度** | Requires Gateway + SOUL.md + plugins setup / 需配置 Gateway + SOUL.md + 插件 | API ready to use / API 即开即用 |
| **Ecosystem / 生态** | Community-driven, 15,000+ AgentSkills / 社区驱动，15,000+ AgentSkills | Anthropic official ecosystem / Anthropic 官方生态 |
| **Privacy / 隐私** | Can be fully local / 可完全本地化 | Data goes through Anthropic servers / 数据经 Anthropic 服务器 |

The two are fundamentally **complementary**: OpenClaw validated the market demand for agentic execution, and Anthropic turned the same capabilities into an enterprise-grade managed service. See [[OpenClaw-vs-Claude]] for details.

> 两者本质是**互补**：OpenClaw 验证了执行型 Agent 的市场需求，Anthropic 将同等能力做成了企业级托管服务。详见 [[OpenClaw-vs-Claude]]。

---

## Technical Limitations & Notes / 技术限制与注意事项

- Computer Use is currently still a **Research Preview** and may be unstable / Computer Use 目前仍为**研究预览**（Research Preview），可能不稳定
- Dispatch (phone remote control) is in Research Preview status / Dispatch 功能（手机远程控制）为研究预览状态
- Scheduled tasks are limited to Pro and above paid plans / 定时任务仅限 Pro 及以上付费计划
- Session duration billing is not economical for low-frequency, short-task scenarios / 会话时长计费对低频、短任务场景不经济
- Agent Teams' direct communication protocol is still evolving / Agent Teams 的直接通信协议仍在演进中

---

## References / 参考来源

- [Claude Managed Agents Official Docs](https://platform.claude.com/docs/en/managed-agents/overview)
- [SiliconANGLE: Anthropic Launches Claude Managed Agents](https://siliconangle.com/2026/04/08/anthropic-launches-claude-managed-agents-speed-ai-agent-development/)
- [9to5Mac: Enterprise Feature Expansion](https://9to5mac.com/2026/04/09/anthropic-scales-up-with-enterprise-features-for-claude-cowork-and-managed-agents/)
- [The New Stack: Managed Agents Deep Dive](https://thenewstack.io/with-claude-managed-agents-anthropic-wants-to-run-your-ai-agents-for-you/)
- [Claude Cowork Official Page](https://claude.com/product/cowork)
- [Dispatch & Computer Use Announcement](https://claude.com/blog/dispatch-and-computer-use)
