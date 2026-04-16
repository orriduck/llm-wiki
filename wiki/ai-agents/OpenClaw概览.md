# OpenClaw Overview / OpenClaw 概览

> An open-source AI agentic framework with a red lobster icon. First released as Clawdbot in November 2025, renamed to OpenClaw in January 2026.
> Complementary to [[Claude-Managed-Agents]]: OpenClaw is the open-source framework, while Claude and other LLMs serve as its "brain."
> See [[OpenClaw-vs-Claude]] for a positioning comparison.

> 开源 AI 执行型智能体框架，以红色龙虾为图标，2025年11月以 Clawdbot 之名发布，2026年1月更名 OpenClaw。
> 与 [[Claude-Managed-Agents]] 是互补关系：OpenClaw 是开源框架，Claude 等 LLM 是其"大脑"。
> 参见 [[OpenClaw-vs-Claude]] 了解定位对比。

## Table of Contents / 目录

- [[#Background & History / 背景与发展]]
- [[#Core Architecture / 核心架构]]
- [[#Configuration File System / 配置文件系统]]
- [[#Heartbeat Scheduling / Heartbeat 定时调度]]
- [[#Platform Integrations / 平台集成]]
- [[#Plugin Ecosystem (ClawHub) / 插件生态（ClawHub）]]
- [[#Model Support / 模型支持]]
- [[#Multi-Agent Orchestration (v4.0 Roadmap) / 多智能体编排（v4.0 路线图）]]
- [[#Governance / 治理结构]]
- [[#Quick Start / 快速上手]]

---

## Background & History / 背景与发展

| Time / 时间 | Event / 事件 |
|------|------|
| 2025-11 | First released under the name **Clawdbot** / 以 **Clawdbot** 之名首次发布 |
| 2026-01 | Renamed to **OpenClaw**, GitHub Stars exceeded 180K / 更名为 **OpenClaw**，GitHub Stars 突破 18 万 |
| 2026-02 | **OpenClaw Foundation** established, governance formalized with public RFC process / 成立 **OpenClaw Foundation**，治理正式化，引入公开 RFC 流程 |
| 2026-04 | Stars surpassed **120K**, plugin ecosystem (ClawHub) exceeded 15,000 community skills / Stars 超过 **12 万**，插件生态（ClawHub）超过 15,000 个社区技能 |
| Mid-2026 | v4.0 milestone expected: new Plugin SDK, multi-agent orchestration, redesigned Dashboard / v4.0 里程碑预期发布：新 Plugin SDK、多智能体编排、重设计 Dashboard |

The project went viral partly because multiple city governments in China even introduced special policies to support "raising lobsters," sparking global buzz.

> 项目爆火原因：国内多个城市政府甚至出台专项政策支持"养龙虾"，引发全球热议。

---

## Core Architecture / 核心架构

OpenClaw's core abstraction is the **Gateway** — a persistent process running on the local loopback address:

> OpenClaw 的核心抽象是 **Gateway**——一个运行在本机回环地址的持久进程：

```
127.0.0.1:18789
```

The Gateway is responsible for:

> Gateway 负责：

- **Session management**: maintains the lifecycle of multiple Agent sessions / **会话管理**：维护多个 Agent 会话的生命周期
- **Routing**: dispatches messages to the corresponding Agent / **路由调度**：将消息分发到对应 Agent
- **Tool execution**: unified management of AgentSkills invocations / **工具执行**：统一管理 AgentSkills 的调用
- **State orchestration**: maintains context state across requests / **状态编排**：跨请求保持上下文状态

### ReAct Execution Loop / ReAct 执行循环

```
Read SOUL.md (persona configuration)
     ↓
Assemble context (history + memory + instructions)
     ↓
Call LLM for reasoning (Reason)
     ↓
Execute tool calls (Act)
     ↓
Integrate results, loop until task complete
```

Each time an Agent wakes up, it **first reads SOUL.md** to ensure persona and value consistency.

> 每次 Agent 唤醒时，**首先读取 SOUL.md**，确保人格和价值观一致。

---

## Configuration File System / 配置文件系统

OpenClaw defines Agent behavior through a set of Markdown configuration files:

> OpenClaw 通过一组 Markdown 配置文件定义 Agent 的行为：

| File / 文件 | Purpose / 用途 |
|------|------|
| **SOUL.md** | Persona settings: personality, values, communication style / 人格设定：性格、价值观、沟通风格 |
| **HEARTBEAT.md** | Scheduled tasks: periodic tasks described in natural language / 定时调度：自然语言描述的周期性任务 |
| **IDENTITY.md** | Identity definition: Agent's role and responsibilities / 身份定义：Agent 的角色和职责描述 |
| **USER.md** | User profile: records the owner's preferences and background / 用户画像：记录主人的偏好和背景信息 |
| **AGENTS.md** | Multi-agent configuration: capability declarations for collaborating Agents / 多智能体配置：定义协作 Agent 的能力声明 |
| **MEMORY.md** | Persistent memory: important information saved across sessions / 持久记忆：跨会话保存的重要信息 |

These files are all written in Markdown, directly readable by LLMs, **no additional parsing layer needed**.

> 这些文件统一用 Markdown 编写，LLM 可直接阅读，**无需额外解析层**。

---

## Heartbeat Scheduling / Heartbeat 定时调度

HEARTBEAT.md is OpenClaw's "scheduling brain." OpenClaw reads this file every **30 minutes** and executes the tasks within.

> HEARTBEAT.md 是 OpenClaw 的"调度大脑"。OpenClaw 每 **30 分钟**读取一次该文件并执行其中的任务。

### Key Features / 关键特性

- **Natural language scheduling**: no Cron syntax needed — just write "every Monday at 9 AM" or "every 2 hours" / **自然语言调度**：无需 Cron 语法，直接写 "每周一上午 9 点" 或 "每 2 小时"
- **Proactive patrol**: actively notifies users during unexpected events (Heartbeat Alert) / **主动巡逻**：突发事件时主动通知用户（Heartbeat Alert）
- **Multi-channel push**: configurable push to Discord, WhatsApp, Telegram, etc. / **多渠道推送**：可配置推送到 Discord、WhatsApp、Telegram 等

### Example Configuration (HEARTBEAT.md snippet) / 示例配置（HEARTBEAT.md 片段）

```markdown
## Daily Briefing / 每日早报
Every day at 8 AM, scrape HackerNews Top 10, send summary to Discord #daily-news

## Price Monitor / 价格监控
Check BTC price every hour; if 24h drop > 5%, send WhatsApp alert immediately

## Weekly Report / 周报整理
Every Friday at 5 PM, summarize important Slack messages for the week, generate summary email
```

---

## Platform Integrations / 平台集成

OpenClaw supports multi-platform bidirectional communication:

> OpenClaw 支持多平台双向通信：

| Category / 类别 | Platforms / 平台 |
|------|------|
| **Instant Messaging / 即时通讯** | WhatsApp, Telegram, Discord, Slack, Signal, iMessage |
| **Collaboration Tools / 协作工具** | Teams, Feishu |
| **Operating Systems / 操作系统** | Windows, macOS, Linux (Any OS) |

Users can send commands to the Agent through any connected channel and receive Heartbeat alerts and summaries.

> 用户可以在任意已连接的渠道中向 Agent 发送指令，也可接收 Heartbeat 推送的告警和摘要。

---

## Plugin Ecosystem (ClawHub) / 插件生态（ClawHub）

**ClawHub** is OpenClaw's official plugin marketplace. As of April 2026:

> **ClawHub** 是 OpenClaw 的官方插件市场，截至 2026 年 4 月已有：

- **15,000+** community-built skills (AgentSkills) / 社区构建的技能（AgentSkills）
- **100+** pre-configured skills (official) / 预配置技能（官方出品）

AgentSkills enable Agents to:

> AgentSkills 可让 Agent：

- Execute Shell commands / 执行 Shell 命令
- Manage file systems / 管理文件系统
- Perform Web automation / 执行 Web 自动化
- Call external APIs / 调用外部 API

The community project [awesome-openclaw-agents](https://github.com/mergisi/awesome-openclaw-agents) curates 162 production-grade Agent templates across 19 categories.

> 社区项目 [awesome-openclaw-agents](https://github.com/mergisi/awesome-openclaw-agents) 收录了 162 个生产级 Agent 模板，覆盖 19 个分类。

---

## Model Support / 模型支持

OpenClaw **does not bundle any models** and is completely model-agnostic:

> OpenClaw **不内置任何模型**，完全模型无关（Model-Agnostic）：

| Model Type / 模型类型 | Examples / 示例 |
|----------|------|
| **Cloud API / 云端 API** | Claude, GPT-4, DeepSeek, Kimi |
| **Local Models / 本地模型** | Any GGUF model running via Ollama / Ollama 运行的任意 GGUF 模型 |

Users bring their own API key; OpenClaw handles orchestration only. This means:

> 用户自带 API Key，OpenClaw 只负责编排。这也意味着：

- Cost = free framework + model API token fees / 使用成本 = 框架免费 + 模型 API Token 费用
- Can run fully offline (local model scenario) / 可完全离线运行（本地模型场景）
- Privacy-sensitive scenarios can avoid sending data to the cloud / 隐私敏感场景可不发送数据到云端

---

## Multi-Agent Orchestration (v4.0 Roadmap) / 多智能体编排（v4.0 路线图）

v4.0 (expected mid-2026) introduces formal multi-Agent architecture:

> v4.0（预期 2026 年中）引入正式的多 Agent 架构：

```
Supervisor Agent (Coordinator)
    ├── Research Agent
    ├── Code Agent
    └── Communication Agent
```

The pattern is **Supervisor Pattern**:

> 模式为 **Supervisor Pattern**：

- Supervisor receives tasks and routes based on each Agent's declared capabilities / Supervisor 接收任务，根据各 Agent 声明的能力进行路由
- Agents execute sub-tasks in parallel or sequentially / 各 Agent 并行/串行执行子任务
- Results are aggregated back to the Supervisor / 结果汇总回 Supervisor

The current version already supports preliminary multi-Agent configuration via AGENTS.md, but the formal orchestration API will stabilize in v4.0.

> 当前版本已可通过 AGENTS.md 进行初步的多 Agent 配置，但正式的编排 API 在 v4.0 才会稳定。

---

## Governance / 治理结构

The **OpenClaw Foundation** was established in February 2026. Governance mechanisms include:

> 2026 年 2 月成立 **OpenClaw Foundation**，治理机制包括：

- **RFC process**: major feature changes require public comment / **RFC 流程**：重大功能变更须公开征求意见
- **Quarterly community meetings**: operators vote on roadmap priorities / **季度社区会议**：运营者投票决定路线图优先级
- **Contributor rights**: core contributors can participate in foundation decisions / **贡献者权益**：核心贡献者可参与基金会决策

---

## Quick Start / 快速上手

```bash
# Install OpenClaw
pip install openclaw   # or use binary install per GitHub docs

# Start the Gateway
openclaw gateway start

# Configure SOUL.md (edit Agent persona)
openclaw config edit soul

# Configure model (using Claude as example)
openclaw config set model.provider anthropic
openclaw config set model.api_key YOUR_API_KEY

# Run your first task
openclaw run "Organize today's GitHub Issues"
```

---

## References / 参考来源

- [GitHub - openclaw/openclaw](https://github.com/openclaw/openclaw)
- [OpenClaw Official Website](https://openclaw.ai/)
- [OpenClaw Heartbeat Documentation](https://docs.openclaw.ai/gateway/heartbeat)
- [OpenClaw Architecture Analysis (Medium)](https://bibek-poudel.medium.com/how-openclaw-works-understanding-ai-agents-through-a-real-architecture-5d59cc7a4764)
- [OpenClaw Complete Tutorial 2026 (Towards AI)](https://pub.towardsai.net/openclaw-wont-bite-a-zero-to-hero-guide-for-people-who-hate-terminal-14dd1ae6d1c2)
- [DigitalOcean: What is OpenClaw?](https://www.digitalocean.com/resources/articles/what-is-openclaw)
