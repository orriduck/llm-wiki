# Claude Code Skills 自动激活 / Skills Auto-Activation

> 来源：[Skills Auto-Activation — MCP Market](https://mcpmarket.com/zh/tools/skills/skills-auto-activation) · 通过 lizard-eat 整理 · 2026-04-20

> This page covers why Claude Code Skills don't reliably auto-activate, and three escalating solutions — from better descriptions to a custom UserPromptSubmit hook system.

> 本页讲解 Claude Code Skills 无法可靠自动激活的原因，以及三个递进解法——从优化描述到自定义 UserPromptSubmit Hook 系统。

Related notes / 相关笔记：[[Claude-Code插件与MCP]]

---

## 核心问题 / The Problem

**症状 / Symptoms：**
- Skill 描述中的关键词存在于 prompt 中，但 Skill 未被使用
- 正在编辑的文件应该触发 Skill，但什么也没发生
- Skill 存在于配置中，但实际上形同虚设

**根本原因 / Root cause：**

> Skills activation relies on Claude recognizing relevance — it is **not deterministic**.

> Skills 的激活依赖 Claude 自行判断相关性，**不是确定性的**。

这是 Claude Code 的已知问题（GitHub Issue #9954）。官方承认激活"尚不可靠"。

---

## 三级解决方案 / Three-Level Solutions

| 级别 | 方案 | 工作量 | 可靠性 | 适用场景 |
|------|------|--------|--------|----------|
| **Level 1** | 优化描述 + 显式请求 | 低 | 中等 | 小项目、入门 |
| **Level 2** | 在 CLAUDE.md 中引用 Skill | 低 | 中等 | 文档化模式 |
| **Level 3** | 自定义 Hook 系统 | 高 | 很高 | 大型项目、已建立规范 |

**原则：先试 Level 1，不够再升级。**

> Rule: Try Level 1 first, upgrade to Level 3 only if needed.

---

## Level 1：优化 Skill 描述 / Better Descriptions

### 描述的好与坏 / Good vs Bad Descriptions

**差的描述 / Bad：**
```yaml
name: backend-dev
description: Helps with backend development
```

**好的描述 / Good：**
```yaml
name: backend-dev-guidelines
description: Use when creating API routes, controllers, services, or repositories
             in backend - enforces TypeScript patterns, error handling with Sentry,
             and Prisma repository pattern
```

**好描述的关键要素 / Key elements：**
- **具体关键词**：`API routes`、`controllers`、`services`（不能只说 `backend`）
- **使用时机**：`Use when creating...`
- **强制内容**：`enforces X patterns, Y error handling`

### 显式触发 / Explicit Invocation

代替：`怎么创建一个 endpoint？`

改为：`用我的 backend-dev-guidelines skill 创建一个 endpoint`

缺点：每次都要手动说，容易忘。

### 检查设置 / Check Settings

- Settings > Capabilities > **Enable code execution**（必须开启）
- Settings > Capabilities > **Skills toggle on**（必须开启）
- 团队/企业版：检查组织级别设置是否允许

---

## Level 2：在 CLAUDE.md 中引用 / CLAUDE.md References

在项目的 `CLAUDE.md` 中显式提醒 Claude 检查相关 Skill：

```markdown
## 后端开发规范

做后端修改前：
1. 查阅 `/skills/backend-dev-guidelines` 中的模式
2. 遵循数据库访问的 Repository 模式

backend-dev-guidelines skill 包含完整示例。
```

**优点 / Pros：** 无需写代码  
**缺点 / Cons：** Claude 仍然可能不去检查

---

## Level 3：自定义 Hook 系统 / Custom Hook System

### 工作原理 / How It Works

```
用户提交 prompt
    ↓
UserPromptSubmit hook 拦截（Claude 看到之前）
    ↓
分析 prompt（关键词、意图模式、文件路径）
    ↓
与 skill-rules.json 规则匹配
    ↓
注入激活提示词
    ↓
Claude 看到："🎯 USE these skills: ..."
    ↓
Claude 加载并使用相关 Skill
```

实际效果：用户报告"判若云泥——Skills 从摆设变成真正有用的工具"。

### skill-rules.json 配置 / Configuration

放置位置：`~/.claude/skill-rules.json`

```json
{
  "backend-dev-guidelines": {
    "type": "domain",
    "enforcement": "suggest",
    "priority": "high",
    "promptTriggers": {
      "keywords": ["backend", "controller", "service", "API", "endpoint"],
      "intentPatterns": [
        "(create|add|build).*?(route|endpoint|controller|service)",
        "(how to|pattern).*?(backend|API)"
      ]
    },
    "fileTriggers": {
      "pathPatterns": ["backend/src/**/*.ts", "server/**/*.ts"],
      "contentPatterns": ["express\\.Router", "export.*Controller"]
    }
  },
  "test-driven-development": {
    "type": "process",
    "enforcement": "suggest",
    "priority": "high",
    "promptTriggers": {
      "keywords": ["test", "TDD", "testing"],
      "intentPatterns": [
        "(write|add|create).*?(test|spec)",
        "test.*(first|before|TDD)"
      ]
    },
    "fileTriggers": {
      "pathPatterns": ["**/*.test.ts", "**/*.spec.ts"],
      "contentPatterns": ["describe\\(", "it\\(", "test\\("]
    }
  }
}
```

### 四种触发器类型 / Trigger Types

| 类型 | 字段 | 说明 |
|------|------|------|
| **Keyword Triggers** | `keywords` | 字符串匹配（大小写不敏感）|
| **Intent Pattern Triggers** | `intentPatterns` | 正则，匹配动作+对象的组合 |
| **File Path Triggers** | `pathPatterns` | glob 模式匹配文件路径 |
| **Content Pattern Triggers** | `contentPatterns` | 正则匹配文件内容 |

### Hook 实现（高层骨架）/ Hook Implementation

放置位置：`~/.claude/hooks/user-prompt-submit/skill-activator.js`

```javascript
#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

// 加载规则 / Load rules
const rules = JSON.parse(fs.readFileSync(
  path.join(process.env.HOME, '.claude/skill-rules.json'), 'utf8'
));

// 读取 prompt / Read prompt from stdin
let promptData = '';
process.stdin.on('data', chunk => promptData += chunk);

process.stdin.on('end', () => {
    const prompt = JSON.parse(promptData);
    const activatedSkills = analyzePrompt(prompt.text);  // 自行实现匹配逻辑

    if (activatedSkills.length > 0) {
        const context = `
🎯 SKILL ACTIVATION CHECK

Relevant skills for this prompt:
${activatedSkills.map(s => `- **${s.skill}** (${s.priority} priority)`).join('\n')}

Check if these skills should be used before responding.
`;
        console.log(JSON.stringify({
            decision: 'approve',
            additionalContext: context
        }));
    } else {
        console.log(JSON.stringify({ decision: 'approve' }));
    }
});

function analyzePrompt(text) {
    // 遍历 rules，匹配 keywords / intentPatterns / fileTriggers
    // 返回匹配到的 skill 列表（含 priority）
}
```

> 注意：上面是骨架，完整实现需自行编写 `analyzePrompt()`，或参考 hyperpowers 插件中的 `hooks/user-prompt-submit/10-skill-activator.js`。

### 渐进式搭建建议 / Progressive Enhancement

```
第 1 周：基础关键词匹配
{"keywords": ["backend", "API", "controller"]}

第 2 周：加入意图模式
{"intentPatterns": ["(create|add).*?(route|endpoint)"]}

第 3 周：加入文件触发
{"fileTriggers": {"pathPatterns": ["backend/**/*.ts"]}}

第 4 周起：根据观察持续优化
```

---

## Hook 系统的局限性 / Limitations

| 问题 | 说明 |
|------|------|
| 非内置 | 需要手动搭建 hook，Claude Code 不自带 |
| 维护成本 | `skill-rules.json` 需随 Skill 变化持续更新 |
| 过度激活 | 太多 Skill 同时激活会撑爆 context window |
| 非完美 | 最终仍靠 Claude 决定是否真正使用 Skill |
| Token 开销 | 每次 prompt 增加约 50–100 token（多 Skill 更多）|
| 延迟 | Hook 为每条 prompt 增加约 100–300ms 处理时间 |

**避免过度激活 / Avoid over-activation：**
- 为每条规则设置 `priority`（`high` / `medium` / `low`）
- 限制同时激活的 Skill 数量
- 定期审查 `skill-rules.json`，去掉无效规则

---

## 其他方案对比 / Alternative Approaches

| 方案 | 优点 | 缺点 |
|------|------|------|
| MCP 集成 | 内置于 Claude 系统 | 仍不确定性，同样的激活问题 |
| 自定义 System Prompt | 无需 Hook | 仅限 Pro 计划，无法按项目定制 |
| 手动纪律（每次显式请求）| 无需设置 | 繁琐、容易忘、不可扩展 |
| 合并进 CLAUDE.md | 总会被加载 | 违反渐进式信息披露，浪费 token |

**推荐：大型项目用 Level 3（Hook），小项目用 Level 1。**

---

## 验证清单（上 Hook 之前）/ Checklist Before Building Hook

- [ ] 已尝试改进 Skill 描述（Level 1）
- [ ] 已尝试显式请求 Skill（Level 1）
- [ ] 已确认 Settings > Capabilities 中相关开关已开启
- [ ] 已观察哪些 prompt 应该激活哪些 Skill
- [ ] 已识别激活失败的规律
- [ ] 项目规模足以支撑 Hook 的维护成本
- [ ] 有 ~2 小时的初始搭建时间

**Level 1 够用就不要搭 Hook 系统。**

---

## 相关资源 / References

- [原始来源 — MCP Market](https://mcpmarket.com/zh/tools/skills/skills-auto-activation)
- [[Claude-Code插件与MCP]] — Skills 体系概览、安装方式
- [Anthropic Skills Best Practices](https://docs.anthropic.com/en/docs/claude-code/skills)
- [Claude Code Hooks Guide](https://docs.anthropic.com/en/docs/claude-code/hooks)
- Hyperpowers 插件：包含完整的 `hooks/user-prompt-submit/10-skill-activator.js` 实现
