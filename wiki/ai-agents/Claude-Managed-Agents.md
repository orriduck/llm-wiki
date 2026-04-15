# Claude Managed Agents

> Anthropic 于 2026 年 4 月 8 日推出的托管 Agent 基础设施服务，将 Agent 的运行环境、沙盒、状态管理等"重活"全部托管化。
> 参见 [[OpenClaw概览]] 了解开源对标方案。
> 参见 [[OpenClaw-vs-Claude]] 了解两者定位对比。

## 目录

- [[#背景：为什么需要 Managed Agents]]
- [[#核心能力]]
- [[#Agent 类型]]
- [[#Claude Cowork]]
- [[#Dispatch 与定时任务]]
- [[#计费模式]]
- [[#早期用户案例]]
- [[#与 OpenClaw 的关系]]
- [[#技术限制与注意事项]]

---

## 背景：为什么需要 Managed Agents

自主 Agent 开发面临的通用痛点：

| 问题 | 说明 |
|------|------|
| **沙盒搭建** | 需要安全隔离的执行环境，防止 Agent 越权操作 |
| **状态持久化** | 长任务中途断线后如何恢复？ |
| **扩缩容** | 并发 Agent 数量激增时如何调度？ |
| **监控与审计** | Agent 做了什么？出错了如何排查？ |
| **基础设施维护** | 服务器、网络、安全补丁……耗时耗力 |

Managed Agents 的定位：**"把原型变成生产只需几天，而非几个月"**。

---

## 核心能力

Managed Agents 是一套**可组合的 API 套件**，用于构建和部署云端托管的自主 Agent：

### 托管执行环境
- 完全托管的 Agent harness，针对性能调优
- **安全沙盒**：隔离执行，防止横向移动
- **内置工具**：文件操作、代码执行、浏览器控制等开箱即用
- **SSE 流式传输**：实时接收 Agent 执行状态推送（Server-Sent Events）

### 状态管理
- 会话中断后**自动恢复**：进度和输出不丢失
- 跨会话的持久状态存储
- 支持长达 **14.5 小时任务跨度**的持续运行（基于 100 万 Token 上下文窗口）

### 生产级基础设施
- Anthropic 负责托管、扩缩容和监控
- 认证与访问控制内置
- 企业级管理员控制台（Feature 访问管理、用量追踪、费用控制）

---

## Agent 类型

Managed Agents 提供两种协作模式：

### Agent Teams（多 Agent 团队）
```
Team Coordinator
    ├── Agent A（独立上下文）
    ├── Agent B（独立上下文）
    └── Agent C（独立上下文）
```
- 多个 Claude 实例各自拥有**独立上下文**
- Agent 之间可**直接通信**
- 适合大规模并行任务分解

### Subagents（子智能体）
```
Main Agent（主 Agent）
    └── Subagent（同一会话）
         └── 只向主 Agent 汇报结果
```
- 在同一会话内运行
- 轻量，只向主 Agent 返回结果
- 适合简单的功能委托

---

## Claude Cowork

Claude Cowork 是面向个人和团队的 Agent 工作台，重点在于**本地计算机控制**：

### 计算机控制（Computer Use）
Claude 可以直接操控用户本机：
- 点击、输入、滚动（鼠标/键盘控制）
- 打开和操作本地文件
- 控制浏览器完成 Web 任务
- 优先调用精准 Connector（如 Slack、Google Calendar），无 Connector 时回退到屏幕控制

### 工作流
1. 用户通过 Cowork 或 Dispatch 分配任务
2. Claude 选择最合适的工具（Connector → 浏览器控制 → 屏幕控制）
3. 自主完成任务，完成后通知用户

---

## Dispatch 与定时任务

### Dispatch（研究预览，2026 年 3 月）

让用户在**手机**上远程操控桌面 Cowork 会话：

```
手机 Dispatch App
    → 发送任务指令
    → Claude Desktop 接收并执行
    → 完成后推送通知到手机
```

使用场景：
- 外出时分配任务，回来看结果
- 一个连续对话，手机和桌面无缝切换

### 定时任务（Scheduled Tasks）

可用计划：**Pro、Max、Team、Enterprise**

| 特性 | 说明 |
|------|------|
| **自定义频率** | 每天、每周、自定义间隔 |
| **任务内容** | 搜索 Slack、查询文件、Web 调研、生成报告 |
| **工具继承** | 使用用户已配置的全部 Connector 和 Plugin |
| **持久指令** | Claude 保存 Prompt 作为任务指令，按节奏自动运行 |

示例：
- "每天早上汇总昨日 Slack 重要消息"
- "每周一拉取上周指标并生成 PDF 报告"
- "监控竞品官网变动，有更新时通知我"

---

## 计费模式

```
总费用 = Token 费用（标准 Claude API 价格）
       + 会话时长费（$0.08 / 会话小时）
```

适合高频、长时运行的 Agent 场景；短对话不经济，用标准 API 更合适。

---

## 早期用户案例

| 公司 | 应用场景 |
|------|----------|
| **Notion** | AI 辅助文档整理与知识库维护 |
| **Asana** | 项目任务自动化分配与跟踪 |
| **Sentry** | 错误日志分析与自动生成修复建议 |

---

## 与 OpenClaw 的关系

| 维度 | OpenClaw | Claude Managed Agents |
|------|----------|-----------------------|
| **定位** | 开源框架，用户自部署 | 托管服务，Anthropic 运维 |
| **基础设施** | 用户自建 | Anthropic 全权负责 |
| **模型** | 模型无关（可用 Claude/DeepSeek/本地） | 绑定 Claude |
| **成本** | 框架免费 + API 费用 | API 费用 + $0.08/小时 |
| **上手难度** | 需配置 Gateway + SOUL.md + 插件 | API 即开即用 |
| **生态** | 社区驱动，15,000+ AgentSkills | Anthropic 官方生态 |
| **隐私** | 可完全本地化 | 数据经 Anthropic 服务器 |

两者本质是**互补**：OpenClaw 验证了执行型 Agent 的市场需求，Anthropic 将同等能力做成了企业级托管服务。详见 [[OpenClaw-vs-Claude]]。

---

## 技术限制与注意事项

- Computer Use 目前仍为**研究预览**（Research Preview），可能不稳定
- Dispatch 功能（手机远程控制）为研究预览状态
- 定时任务仅限 Pro 及以上付费计划
- 会话时长计费对低频、短任务场景不经济
- Agent Teams 的直接通信协议仍在演进中

---

## 参考来源

- [Claude Managed Agents 官方文档](https://platform.claude.com/docs/en/managed-agents/overview)
- [SiliconANGLE：Anthropic 发布 Managed Agents](https://siliconangle.com/2026/04/08/anthropic-launches-claude-managed-agents-speed-ai-agent-development/)
- [9to5Mac：企业功能扩展报道](https://9to5mac.com/2026/04/09/anthropic-scales-up-with-enterprise-features-for-claude-cowork-and-managed-agents/)
- [The New Stack：Managed Agents 深度分析](https://thenewstack.io/with-claude-managed-agents-anthropic-wants-to-run-your-ai-agents-for-you/)
- [Claude Cowork 官方介绍](https://claude.com/product/cowork)
- [Dispatch 与 Computer Use 发布公告](https://claude.com/blog/dispatch-and-computer-use)
