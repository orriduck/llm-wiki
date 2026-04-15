# OpenClaw 概览

> 开源 AI 执行型智能体框架，以红色龙虾为图标，2025年11月以 Clawdbot 之名发布，2026年1月更名 OpenClaw。
> 与 [[Claude-Managed-Agents]] 是互补关系：OpenClaw 是开源框架，Claude 等 LLM 是其"大脑"。
> 参见 [[OpenClaw-vs-Claude]] 了解定位对比。

## 目录

- [[#背景与发展]]
- [[#核心架构]]
- [[#配置文件系统]]
- [[#Heartbeat 定时调度]]
- [[#平台集成]]
- [[#插件生态（ClawHub）]]
- [[#模型支持]]
- [[#多智能体编排（v4.0 路线图）]]
- [[#治理结构]]
- [[#快速上手]]

---

## 背景与发展

| 时间 | 事件 |
|------|------|
| 2025-11 | 以 **Clawdbot** 之名首次发布 |
| 2026-01 | 更名为 **OpenClaw**，GitHub Stars 突破 18 万 |
| 2026-02 | 成立 **OpenClaw Foundation**，治理正式化，引入公开 RFC 流程 |
| 2026-04 | Stars 超过 **12 万**，插件生态（ClawHub）超过 15,000 个社区技能 |
| 2026-中 | v4.0 里程碑预期发布：新 Plugin SDK、多智能体编排、重设计 Dashboard |

项目爆火原因：国内多个城市政府甚至出台专项政策支持"养龙虾"，引发全球热议。

---

## 核心架构

OpenClaw 的核心抽象是 **Gateway**——一个运行在本机回环地址的持久进程：

```
127.0.0.1:18789
```

Gateway 负责：
- **会话管理**：维护多个 Agent 会话的生命周期
- **路由调度**：将消息分发到对应 Agent
- **工具执行**：统一管理 AgentSkills 的调用
- **状态编排**：跨请求保持上下文状态

### ReAct 执行循环

```
读取 SOUL.md（人格配置）
     ↓
组装上下文（历史 + 记忆 + 指令）
     ↓
调用 LLM 推理（Reason）
     ↓
执行工具调用（Act）
     ↓
整合结果，循环直到任务完成
```

每次 Agent 唤醒时，**首先读取 SOUL.md**，确保人格和价值观一致。

---

## 配置文件系统

OpenClaw 通过一组 Markdown 配置文件定义 Agent 的行为：

| 文件 | 用途 |
|------|------|
| **SOUL.md** | 人格设定：性格、价值观、沟通风格 |
| **HEARTBEAT.md** | 定时调度：自然语言描述的周期性任务 |
| **IDENTITY.md** | 身份定义：Agent 的角色和职责描述 |
| **USER.md** | 用户画像：记录主人的偏好和背景信息 |
| **AGENTS.md** | 多智能体配置：定义协作 Agent 的能力声明 |
| **MEMORY.md** | 持久记忆：跨会话保存的重要信息 |

这些文件统一用 Markdown 编写，LLM 可直接阅读，**无需额外解析层**。

---

## Heartbeat 定时调度

HEARTBEAT.md 是 OpenClaw 的"调度大脑"。OpenClaw 每 **30 分钟**读取一次该文件并执行其中的任务。

### 关键特性

- **自然语言调度**：无需 Cron 语法，直接写 "每周一上午 9 点" 或 "每 2 小时"
- **主动巡逻**：突发事件时主动通知用户（Heartbeat Alert）
- **多渠道推送**：可配置推送到 Discord、WhatsApp、Telegram 等

### 示例配置（HEARTBEAT.md 片段）

```markdown
## 每日早报
每天早上 8 点，爬取 HackerNews Top 10，摘要发到 Discord #daily-news

## 价格监控
每小时检查 BTC 价格，如果 24h 跌幅 > 5% 立刻发 WhatsApp 告警

## 周报整理
每周五下午 5 点，汇总本周 Slack 重要消息，生成摘要邮件
```

---

## 平台集成

OpenClaw 支持多平台双向通信：

| 类别 | 平台 |
|------|------|
| **即时通讯** | WhatsApp、Telegram、Discord、Slack、Signal、iMessage |
| **协作工具** | Teams、Feishu（飞书） |
| **操作系统** | Windows、macOS、Linux（Any OS） |

用户可以在任意已连接的渠道中向 Agent 发送指令，也可接收 Heartbeat 推送的告警和摘要。

---

## 插件生态（ClawHub）

**ClawHub** 是 OpenClaw 的官方插件市场，截至 2026 年 4 月已有：

- **15,000+** 社区构建的技能（AgentSkills）
- **100+** 预配置技能（官方出品）

AgentSkills 可让 Agent：
- 执行 Shell 命令
- 管理文件系统
- 执行 Web 自动化
- 调用外部 API

社区项目 [awesome-openclaw-agents](https://github.com/mergisi/awesome-openclaw-agents) 收录了 162 个生产级 Agent 模板，覆盖 19 个分类。

---

## 模型支持

OpenClaw **不内置任何模型**，完全模型无关（Model-Agnostic）：

| 模型类型 | 示例 |
|----------|------|
| **云端 API** | Claude、GPT-4、DeepSeek、Kimi |
| **本地模型** | Ollama 运行的任意 GGUF 模型 |

用户自带 API Key，OpenClaw 只负责编排。这也意味着：
- 使用成本 = 框架免费 + 模型 API Token 费用
- 可完全离线运行（本地模型场景）
- 隐私敏感场景可不发送数据到云端

---

## 多智能体编排（v4.0 路线图）

v4.0（预期 2026 年中）引入正式的多 Agent 架构：

```
Supervisor Agent（协调者）
    ├── Research Agent（研究专家）
    ├── Code Agent（代码专家）
    └── Communication Agent（通知专家）
```

模式为 **Supervisor Pattern**：
- Supervisor 接收任务，根据各 Agent 声明的能力进行路由
- 各 Agent 并行/串行执行子任务
- 结果汇总回 Supervisor

当前版本已可通过 AGENTS.md 进行初步的多 Agent 配置，但正式的编排 API 在 v4.0 才会稳定。

---

## 治理结构

2026 年 2 月成立 **OpenClaw Foundation**，治理机制包括：

- **RFC 流程**：重大功能变更须公开征求意见
- **季度社区会议**：运营者投票决定路线图优先级
- **贡献者权益**：核心贡献者可参与基金会决策

---

## 快速上手

```bash
# 安装 OpenClaw
pip install openclaw   # 或参考 GitHub 文档使用二进制安装

# 启动 Gateway
openclaw gateway start

# 配置 SOUL.md（编辑 Agent 人格）
openclaw config edit soul

# 配置模型（以 Claude 为例）
openclaw config set model.provider anthropic
openclaw config set model.api_key sk-ant-xxx

# 运行第一个任务
openclaw run "帮我整理今天的 GitHub Issues"
```

---

## 参考来源

- [GitHub - openclaw/openclaw](https://github.com/openclaw/openclaw)
- [OpenClaw 官网](https://openclaw.ai/)
- [OpenClaw Heartbeat 文档](https://docs.openclaw.ai/gateway/heartbeat)
- [OpenClaw 架构解析 (Medium)](https://bibek-poudel.medium.com/how-openclaw-works-understanding-ai-agents-through-a-real-architecture-5d59cc7a4764)
- [OpenClaw 完整教程 2026 (Towards AI)](https://pub.towardsai.net/openclaw-wont-bite-a-zero-to-hero-guide-for-people-who-hate-terminal-14dd1ae6d1c2)
- [DigitalOcean: What is OpenClaw?](https://www.digitalocean.com/resources/articles/what-is-openclaw)
