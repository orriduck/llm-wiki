# Amazon EventBridge

> Serverless event bus, the core of event-driven architectures connecting applications, AWS services, and SaaS applications.
> Tightly integrated with [[Lambda]], [[CloudWatch]], and [[CloudTrail]].
> Used in Metaflow for triggering Step Functions scheduled dispatches; see [[Metaflow工作流框架]].

> 无服务器事件总线，连接应用、AWS 服务和 SaaS 应用的事件驱动架构核心。
> 与 [[Lambda]]、[[CloudWatch]]、[[CloudTrail]] 紧密集成。
> Metaflow 中用于触发 Step Functions 定时调度，见 [[Metaflow工作流框架]]。

## Table of Contents / 目录

- [[#Core Concepts / 核心概念]]
- [[#Event Structure / 事件结构]]
- [[#Event Buses / 事件总线]]
- [[#Rules & Targets / 规则与目标]]
- [[#Event Pattern Matching / 事件模式匹配]]
- [[#Scheduled Invocations / 定时调度]]
- [[#Pipes / Pipes（管道）]]
- [[#Schema Registry]]
- [[#Archive & Replay / Archive 与 Replay]]
- [[#Cross-Account & Cross-Region / 跨账户与跨区域]]
- [[#Security & Permissions / 安全与权限]]
- [[#Monitoring & Debugging / 监控与调试]]
- [[#Common Architecture Patterns / 常见架构模式]]
- [[#CLI Quick Reference / CLI 速查]]

---

## Core Concepts / 核心概念

| Concept / 概念 | Description / 说明 |
|------|------|
| **Event Bus** | Transport channel for events; can have multiple (default + custom) / 事件的传输通道，可有多个（default + 自定义） |
| **Event** | A JSON object describing a change in the environment / 一个 JSON 对象，描述环境中的变化 |
| **Rule** | Rule that matches events and routes to targets / 匹配事件并路由到目标的规则 |
| **Target** | AWS service that receives matched events (Lambda, SQS, SNS, etc.) / 接收匹配事件的 AWS 服务 |
| **Pattern** | Event matching conditions defined in a rule / 规则中定义的事件匹配条件 |
| **Schema** | Description of event structure, can be auto-discovered / 事件结构的描述，可自动发现 |
| **Archive** | Event archive, can be replayed / 事件的存档，可重放 |
| **Pipe** | Point-to-point integration: source → filter → transform → target / 点对点集成：源 → 过滤 → 转换 → 目标 |
| **Scheduler** | Independent scheduling service (more powerful than Rule cron) / 独立的定时调度服务（比 Rule 的 cron 更强大） |

---

## Event Structure / 事件结构

All EventBridge events follow a unified envelope format.

> 所有 EventBridge 事件遵循统一的信封格式。

```json
{
  "version": "0",
  "id": "12345678-1234-1234-1234-123456789012",
  "source": "com.myapp.orders",
  "account": "<account-id>",
  "time": "2026-04-13T10:30:00Z",
  "region": "us-east-1",
  "detail-type": "Order Placed",
  "detail": {
    "orderId": "ORD-001",
    "customerId": "CUST-123",
    "amount": 99.99,
    "items": ["item-a", "item-b"]
  }
}
```

**Envelope fields** (managed by EventBridge): `version`, `id`, `account`, `time`, `region`

> **信封字段**（EventBridge 管理）：`version`、`id`、`account`、`time`、`region`

**User fields / 用户字段**: `source`, `detail-type`, `detail` (custom business data / 自定义业务数据)

---

## Event Buses / 事件总线

### Types / 类型

| Type / 类型 | Description / 说明 |
|------|------|
| **default** | Included with each account; AWS service events are sent here by default / 每个账户自带，AWS 服务事件默认发送到这里 |
| **Custom** | Custom event bus for application event isolation / 自定义事件总线，用于应用事件隔离 |
| **Partner** | SaaS partner events (Shopify, Datadog, Auth0, etc.) / SaaS 合作伙伴事件 |

### Create Custom Event Bus / 创建自定义事件总线

```bash
aws events create-event-bus --name my-app-bus

# Send event to custom bus / 发送事件到自定义总线
aws events put-events --entries '[{
    "Source": "com.myapp.orders",
    "DetailType": "Order Placed",
    "Detail": "{\"orderId\":\"ORD-001\",\"amount\":99.99}",
    "EventBusName": "my-app-bus"
}]'
```

### Send Events in Code / 在代码中发送事件

```python
import boto3
import json

client = boto3.client('events')

response = client.put_events(
    Entries=[
        {
            'Source': 'com.myapp.orders',
            'DetailType': 'Order Placed',
            'Detail': json.dumps({
                'orderId': 'ORD-001',
                'customerId': 'CUST-123',
                'amount': 99.99
            }),
            'EventBusName': 'my-app-bus'
        }
    ]
)

# Check for failures / 检查失败
if response['FailedEntryCount'] > 0:
    print(f"Failed entries: {response['Entries']}")
```

**Batch sending**: `put_events` supports max 10 events per call, each event max 256 KB.

> **批量发送**：`put_events` 单次最多 10 个事件，每个事件最大 256 KB。

---

## Rules & Targets / 规则与目标

### Create Rule / 创建规则

```bash
# Match specific event pattern / 匹配特定事件模式
aws events put-rule \
    --name "order-placed-rule" \
    --event-bus-name "my-app-bus" \
    --event-pattern '{
        "source": ["com.myapp.orders"],
        "detail-type": ["Order Placed"]
    }'
```

### Add Targets / 添加目标

One rule supports up to 5 targets.

> 一条规则最多 5 个目标。

```bash
# Lambda target
aws events put-targets \
    --rule "order-placed-rule" \
    --event-bus-name "my-app-bus" \
    --targets '[
        {
            "Id": "process-order",
            "Arn": "arn:aws:lambda:us-east-1:<account-id>:function:process-order"
        },
        {
            "Id": "notify-queue",
            "Arn": "arn:aws:sqs:us-east-1:<account-id>:order-notifications"
        }
    ]'
```

### Supported Targets / 支持的目标

| Target / 目标 | Typical Use / 典型用途 |
|------|---------|
| [[Lambda]] | Event processing logic / 事件处理逻辑 |
| SQS | Decoupling, buffering / 解耦、缓冲 |
| SNS | Fan-out notifications / 扇出通知 |
| Step Functions | Start workflows / 启动工作流 |
| Kinesis Data Streams | Streaming data / 流式数据 |
| ECS Task | Start container tasks / 启动容器任务 |
| API Gateway | Call HTTP API / 调用 HTTP API |
| Another Event Bus | Cross-account/cross-region / 跨账户/跨区域 |
| CloudWatch Log Group | Event archival/debugging / 事件存档/调试 |
| Redshift / Batch / CodePipeline | Other AWS services / 其他 AWS 服务 |

### Input Transformer

Transform event format before sending to target.

> 发送到目标前转换事件格式。

```bash
aws events put-targets \
    --rule "order-placed-rule" \
    --targets '[{
        "Id": "transformed-target",
        "Arn": "arn:aws:lambda:us-east-1:<account-id>:function:handler",
        "InputTransformer": {
            "InputPathsMap": {
                "orderId": "$.detail.orderId",
                "amount": "$.detail.amount"
            },
            "InputTemplate": "\"Order <orderId> received, amount: $<amount>\""
        }
    }]'
```

---

## Event Pattern Matching / 事件模式匹配

### Basic Matching / 基本匹配

```json
// Exact match source and detail-type / 精确匹配 source 和 detail-type
{
  "source": ["com.myapp.orders"],
  "detail-type": ["Order Placed", "Order Updated"]
}
```

### Content Filtering (detail level) / 内容过滤（detail 级别）

```json
// Orders with amount > 100 / 金额 > 100 的订单
{
  "source": ["com.myapp.orders"],
  "detail": {
    "amount": [{"numeric": [">", 100]}]
  }
}
```

### Advanced Pattern Operators / 高级模式操作符

| Operator / 操作符 | Example / 示例 | Description / 说明 |
|--------|------|------|
| Exact match / 精确匹配 | `["value"]` | Equals / 等于 |
| Prefix / 前缀 | `[{"prefix": "prod-"}]` | Starts with / 以...开头 |
| Suffix / 后缀 | `[{"suffix": ".json"}]` | Ends with / 以...结尾 |
| Numeric range / 数值范围 | `[{"numeric": [">=", 10, "<", 100]}]` | Range / 区间 |
| Exists / 存在性 | `[{"exists": true}]` | Field exists / 字段存在 |
| Not exists / 不存在 | `[{"exists": false}]` | Field does not exist / 字段不存在 |
| anything-but | `[{"anything-but": ["test"]}]` | Not equal / 不等于 |
| wildcard | `[{"wildcard": "prod-*-us"}]` | Wildcard / 通配符 |

### Combined Example / 组合示例

```json
{
  "source": ["com.myapp.orders"],
  "detail": {
    "status": ["COMPLETED"],
    "amount": [{"numeric": [">", 1000]}],
    "region": [{"anything-but": ["test-region"]}],
    "metadata": {
      "priority": [{"exists": true}]
    }
  }
}
```

### AWS Service Event Patterns / AWS 服务事件模式

```json
// EC2 instance state change / EC2 实例状态变化
{
  "source": ["aws.ec2"],
  "detail-type": ["EC2 Instance State-change Notification"],
  "detail": {
    "state": ["stopped", "terminated"]
  }
}

// S3 object created (requires CloudTrail or S3 Event Notifications enabled)
// S3 对象创建（需先开启 CloudTrail 或 S3 Event Notifications）
{
  "source": ["aws.s3"],
  "detail-type": ["Object Created"],
  "detail": {
    "bucket": {"name": ["my-bucket"]},
    "object": {"key": [{"prefix": "uploads/"}]}
  }
}
```

---

## Scheduled Invocations / 定时调度

### Rule Method (traditional) / Rule 方式（传统）

```bash
# cron expression (UTC)
aws events put-rule --name "daily-report" \
    --schedule-expression "cron(0 2 * * ? *)"

# rate expression
aws events put-rule --name "every-5-min" \
    --schedule-expression "rate(5 minutes)"
```

**cron format**: `cron(min hour day month weekday year)` -- note 6 fields (including year); day and weekday cannot both be specified (use `?`).

> **cron 格式**：`cron(分 时 日 月 星期 年)` — 注意有 6 个字段（含年），日和星期不能同时指定（用 `?`）。

### EventBridge Scheduler (recommended) / EventBridge Scheduler（推荐）

Independent service with more powerful features.

> 独立服务，功能更强大。

```bash
# One-time schedule / 一次性调度
aws scheduler create-schedule \
    --name "one-time-task" \
    --schedule-expression "at(2026-04-15T10:00:00)" \
    --schedule-expression-timezone "Asia/Shanghai" \
    --target '{"Arn":"arn:aws:lambda:...","RoleArn":"arn:aws:iam::..."}' \
    --flexible-time-window '{"Mode":"OFF"}'

# Recurring schedule (with timezone support) / 循环调度（支持时区）
aws scheduler create-schedule \
    --name "daily-cn-morning" \
    --schedule-expression "cron(0 9 * * ? *)" \
    --schedule-expression-timezone "Asia/Shanghai" \
    --target '{"Arn":"arn:aws:lambda:...","RoleArn":"arn:aws:iam::..."}' \
    --flexible-time-window '{"Mode":"FLEXIBLE","MaximumWindowInMinutes":15}'
```

**Scheduler vs Rule**:

| Feature / 特性 | Rule (traditional) / Rule（传统） | Scheduler |
|------|-------------|-----------|
| Timezone support / 时区支持 | No (UTC only) / 否 | Yes / 是 |
| One-time schedule / 一次性调度 | No / 否 | Yes (`at()`) / 是 |
| Flexible time window / 灵活时间窗口 | No / 否 | Yes / 是 |
| Retry policy / 重试策略 | Limited / 有限 | Full (up to 185 retries) / 完整（最多 185 次） |
| Max schedules / 最大调度数 | ~300 per account / 账户 | 1M per account / 100 万 / 账户 |
| DLQ | No / 否 | Yes / 是 |

---

## Pipes / Pipes（管道）

Point-to-point integration, replacing the simple "event source → rule → target" pattern.

> 点对点集成，替代"事件源 → 规则 → 目标"的简单模式。

```
Source → Filter → Enrichment → Target
```

```bash
aws pipes create-pipe \
    --name "sqs-to-lambda" \
    --source "arn:aws:sqs:us-east-1:<account-id>:orders-queue" \
    --target "arn:aws:lambda:us-east-1:<account-id>:function:process-order" \
    --role-arn "arn:aws:iam::<account-id>:role/pipes-role" \
    --source-parameters '{
        "SqsQueueParameters": {"BatchSize": 10}
    }' \
    --filter-criteria '{
        "Filters": [{
            "Pattern": "{\"body\":{\"amount\":[{\"numeric\":[\">\",100]}]}}"
        }]
    }'
```

Supported Sources: SQS, Kinesis, DynamoDB Streams, Kafka, MQ

> 支持的 Source：SQS、Kinesis、DynamoDB Streams、Kafka、MQ

Supported Targets: Lambda, SQS, SNS, Step Functions, API Gateway, ECS, etc.

> 支持的 Target：Lambda、SQS、SNS、Step Functions、API Gateway、ECS 等

---

## Schema Registry

Automatically discover and document event structures.

> 自动发现和记录事件结构。

```bash
# Enable schema discovery on event bus / 开启事件总线的 schema discovery
aws schemas update-discoverer \
    --discoverer-id <id> \
    --state STARTED

# View discovered schema / 查看发现的 schema
aws schemas describe-schema \
    --registry-name discovered-schemas \
    --schema-name com.myapp.orders@OrderPlaced

# Generate code bindings (Python/Java/TypeScript) / 生成代码绑定
aws schemas get-code-binding-source \
    --registry-name discovered-schemas \
    --schema-name com.myapp.orders@OrderPlaced \
    --language Python36
```

---

## Archive & Replay / Archive 与 Replay

### Create Event Archive / 创建事件存档

```bash
aws events create-archive \
    --archive-name "all-orders" \
    --event-source-arn "arn:aws:events:us-east-1:<account-id>:event-bus/my-app-bus" \
    --event-pattern '{"source": ["com.myapp.orders"]}' \
    --retention-days 90
```

### Replay Historical Events / 重放历史事件

```bash
aws events start-replay \
    --replay-name "replay-orders-apr" \
    --event-source-arn "arn:aws:events:us-east-1:<account-id>:event-bus/my-app-bus" \
    --destination '{"Arn": "arn:aws:events:us-east-1:<account-id>:event-bus/my-app-bus"}' \
    --event-start-time "2026-04-01T00:00:00Z" \
    --event-end-time "2026-04-10T00:00:00Z"
```

**Use cases**: Replay events after fixing a bug, backfill data for new consumers, test rules and targets.

> **用途**：修复 bug 后重放事件、新消费者接入时回填数据、测试规则和目标。

---

## Cross-Account & Cross-Region / 跨账户与跨区域

### Cross-Account Event Routing / 跨账户事件路由

```bash
# Account A: Allow account B to send events to its bus
# 账户 A：允许账户 B 发送事件到自己的 bus
aws events put-permission \
    --event-bus-name my-app-bus \
    --action events:PutEvents \
    --principal <other-account-id> \
    --statement-id "allow-account-b"

# Account B: Send events to account A's bus
# 账户 B：发送事件到账户 A 的 bus
aws events put-events --entries '[{
    "Source": "com.teamb.service",
    "DetailType": "Data Ready",
    "Detail": "{}",
    "EventBusName": "arn:aws:events:us-east-1:<account-id>:event-bus/my-app-bus"
}]'
```

### Cross-Region / 跨区域

Use rules to forward events to an Event Bus in another region.

> 用规则将事件转发到另一个区域的 Event Bus。

```bash
aws events put-targets \
    --rule "replicate-events" \
    --targets '[{
        "Id": "us-west-2-bus",
        "Arn": "arn:aws:events:us-west-2:<account-id>:event-bus/default"
    }]'
```

---

## Security & Permissions / 安全与权限

### Send Events / 发送事件

```json
{
  "Effect": "Allow",
  "Action": "events:PutEvents",
  "Resource": "arn:aws:events:us-east-1:<account-id>:event-bus/my-app-bus"
}
```

### Manage Rules / 管理规则

```json
{
  "Effect": "Allow",
  "Action": [
    "events:PutRule",
    "events:PutTargets",
    "events:DeleteRule",
    "events:RemoveTargets",
    "events:DescribeRule",
    "events:ListRules"
  ],
  "Resource": "arn:aws:events:us-east-1:<account-id>:rule/my-app-bus/*"
}
```

### Target Execution Role / 目标执行角色

EventBridge needs an IAM Role to invoke targets.

> EventBridge 调用目标需要一个 IAM Role。

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "events.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
```

---

## Monitoring & Debugging / 监控与调试

### CloudWatch Metrics / CloudWatch 指标

| Metric / 指标 | Description / 说明 |
|------|------|
| `Invocations` | Rule match count / 规则匹配次数 |
| `FailedInvocations` | Target invocation failure count / 目标调用失败次数 |
| `TriggeredRules` | Number of triggered rules / 被触发的规则数 |
| `MatchedEvents` | Matched event count / 匹配事件数 |
| `ThrottledRules` | Throttled rules / 被限流的规则 |

### Debugging Tips / 调试技巧

1. **Add CloudWatch Logs target**: Rule simultaneously sends to Log Group for viewing matched events / 规则同时发送到 Log Group，方便查看匹配的事件
2. **Event Pattern testing / Event Pattern 测试**:

```bash
# Test pattern matching online / 在线测试模式匹配
aws events test-event-pattern \
    --event-pattern '{"source":["com.myapp"]}' \
    --event '{"source":"com.myapp","detail-type":"Test","detail":{}}'
```

3. **DLQ monitoring / DLQ 监控**: Check Dead Letter Queue when async targets fail / 异步目标失败时检查 Dead Letter Queue

---

## Common Architecture Patterns / 常见架构模式

### Microservice Event Bus / 微服务事件总线

```
Service A ──► Event Bus ──► Rule 1 → Service B (Lambda)
                        ──► Rule 2 → Service C (SQS → ECS)
                        ──► Rule 3 → Analytics (Kinesis → S3)
```

### Audit & Compliance / 审计与合规

```
AWS Services ──► CloudTrail ──► EventBridge ──► Lambda (alert/auto-remediate / 告警/自动修复)
                                            ──► S3 (audit archive / 审计存档)
```

### CQRS Event Sourcing / CQRS 事件溯源

```
Write API → Lambda (write) → DynamoDB
写入 API → Lambda（写）→ DynamoDB
                      → EventBridge → Lambda (projection / 投影) → Read Model (ES/RDS)
```

---

## CLI Quick Reference / CLI 速查

```bash
# Event buses / 事件总线
aws events list-event-buses
aws events create-event-bus --name NAME
aws events delete-event-bus --name NAME

# Send events / 发送事件
aws events put-events --entries '[{...}]'

# Rules / 规则
aws events list-rules --event-bus-name NAME
aws events put-rule --name RULE --event-pattern '{...}'
aws events describe-rule --name RULE
aws events delete-rule --name RULE

# Targets / 目标
aws events list-targets-by-rule --rule RULE
aws events put-targets --rule RULE --targets '[{...}]'
aws events remove-targets --rule RULE --ids "target-1"

# Pattern testing / 模式测试
aws events test-event-pattern --event-pattern '{...}' --event '{...}'

# Scheduler
aws scheduler list-schedules
aws scheduler create-schedule --name NAME --schedule-expression "rate(1 hour)" ...
aws scheduler delete-schedule --name NAME
```

---

*Last updated / 最后更新：2026-04-13*
