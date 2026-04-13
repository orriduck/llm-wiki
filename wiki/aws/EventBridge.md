# Amazon EventBridge

> 无服务器事件总线，连接应用、AWS 服务和 SaaS 应用的事件驱动架构核心。
> 与 [[Lambda]]、[[CloudWatch]]、[[CloudTrail]] 紧密集成。
> Metaflow 中用于触发 Step Functions 定时调度，见 [[AWS与Metaflow]]。

## 目录

- [[#核心概念]]
- [[#事件结构]]
- [[#事件总线]]
- [[#规则与目标]]
- [[#事件模式匹配]]
- [[#定时调度]]
- [[#Pipes（管道）]]
- [[#Schema Registry]]
- [[#Archive 与 Replay]]
- [[#跨账户与跨区域]]
- [[#安全与权限]]
- [[#监控与调试]]
- [[#常见架构模式]]
- [[#CLI 速查]]

---

## 核心概念

| 概念 | 说明 |
|------|------|
| **Event Bus** | 事件的传输通道，可有多个（default + 自定义） |
| **Event** | 一个 JSON 对象，描述环境中的变化 |
| **Rule** | 匹配事件并路由到目标的规则 |
| **Target** | 接收匹配事件的 AWS 服务（Lambda、SQS、SNS 等） |
| **Pattern** | 规则中定义的事件匹配条件 |
| **Schema** | 事件结构的描述，可自动发现 |
| **Archive** | 事件的存档，可重放 |
| **Pipe** | 点对点集成：源 → 过滤 → 转换 → 目标 |
| **Scheduler** | 独立的定时调度服务（比 Rule 的 cron 更强大） |

---

## 事件结构

所有 EventBridge 事件遵循统一的信封格式：

```json
{
  "version": "0",
  "id": "12345678-1234-1234-1234-123456789012",
  "source": "com.myapp.orders",
  "account": "123456789012",
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

**信封字段**（EventBridge 管理）：`version`、`id`、`account`、`time`、`region`
**用户字段**：`source`、`detail-type`、`detail`（自定义业务数据）

---

## 事件总线

### 类型

| 类型 | 说明 |
|------|------|
| **default** | 每个账户自带，AWS 服务事件默认发送到这里 |
| **Custom** | 自定义事件总线，用于应用事件隔离 |
| **Partner** | SaaS 合作伙伴事件（Shopify、Datadog、Auth0 等） |

### 创建自定义事件总线

```bash
aws events create-event-bus --name my-app-bus

# 发送事件到自定义总线
aws events put-events --entries '[{
    "Source": "com.myapp.orders",
    "DetailType": "Order Placed",
    "Detail": "{\"orderId\":\"ORD-001\",\"amount\":99.99}",
    "EventBusName": "my-app-bus"
}]'
```

### 在代码中发送事件

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

# 检查失败
if response['FailedEntryCount'] > 0:
    print(f"Failed entries: {response['Entries']}")
```

> **批量发送**：`put_events` 单次最多 10 个事件，每个事件最大 256 KB。

---

## 规则与目标

### 创建规则

```bash
# 匹配特定事件模式
aws events put-rule \
    --name "order-placed-rule" \
    --event-bus-name "my-app-bus" \
    --event-pattern '{
        "source": ["com.myapp.orders"],
        "detail-type": ["Order Placed"]
    }'
```

### 添加目标

一条规则最多 5 个目标：

```bash
# Lambda 目标
aws events put-targets \
    --rule "order-placed-rule" \
    --event-bus-name "my-app-bus" \
    --targets '[
        {
            "Id": "process-order",
            "Arn": "arn:aws:lambda:us-east-1:123456789:function:process-order"
        },
        {
            "Id": "notify-queue",
            "Arn": "arn:aws:sqs:us-east-1:123456789:order-notifications"
        }
    ]'
```

### 支持的目标

| 目标 | 典型用途 |
|------|---------|
| [[Lambda]] | 事件处理逻辑 |
| SQS | 解耦、缓冲 |
| SNS | 扇出通知 |
| Step Functions | 启动工作流 |
| Kinesis Data Streams | 流式数据 |
| ECS Task | 启动容器任务 |
| API Gateway | 调用 HTTP API |
| 另一个 Event Bus | 跨账户/跨区域 |
| CloudWatch Log Group | 事件存档/调试 |
| Redshift / Batch / CodePipeline | 其他 AWS 服务 |

### Input Transformer

发送到目标前转换事件格式：

```bash
aws events put-targets \
    --rule "order-placed-rule" \
    --targets '[{
        "Id": "transformed-target",
        "Arn": "arn:aws:lambda:us-east-1:123456789:function:handler",
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

## 事件模式匹配

### 基本匹配

```json
// 精确匹配 source 和 detail-type
{
  "source": ["com.myapp.orders"],
  "detail-type": ["Order Placed", "Order Updated"]
}
```

### 内容过滤（detail 级别）

```json
// 金额 > 100 的订单
{
  "source": ["com.myapp.orders"],
  "detail": {
    "amount": [{"numeric": [">", 100]}]
  }
}
```

### 高级模式操作符

| 操作符 | 示例 | 说明 |
|--------|------|------|
| 精确匹配 | `["value"]` | 等于 |
| 前缀 | `[{"prefix": "prod-"}]` | 以...开头 |
| 后缀 | `[{"suffix": ".json"}]` | 以...结尾 |
| 数值范围 | `[{"numeric": [">=", 10, "<", 100]}]` | 区间 |
| 存在性 | `[{"exists": true}]` | 字段存在 |
| 不存在 | `[{"exists": false}]` | 字段不存在 |
| anything-but | `[{"anything-but": ["test"]}]` | 不等于 |
| wildcard | `[{"wildcard": "prod-*-us"}]` | 通配符 |

### 组合示例

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

### AWS 服务事件模式

```json
// EC2 实例状态变化
{
  "source": ["aws.ec2"],
  "detail-type": ["EC2 Instance State-change Notification"],
  "detail": {
    "state": ["stopped", "terminated"]
  }
}

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

## 定时调度

### Rule 方式（传统）

```bash
# cron 表达式（UTC）
aws events put-rule --name "daily-report" \
    --schedule-expression "cron(0 2 * * ? *)"

# rate 表达式
aws events put-rule --name "every-5-min" \
    --schedule-expression "rate(5 minutes)"
```

**cron 格式**：`cron(分 时 日 月 星期 年)` — 注意有 6 个字段（含年），日和星期不能同时指定（用 `?`）。

### EventBridge Scheduler（推荐）

独立服务，功能更强大：

```bash
# 一次性调度
aws scheduler create-schedule \
    --name "one-time-task" \
    --schedule-expression "at(2026-04-15T10:00:00)" \
    --schedule-expression-timezone "Asia/Shanghai" \
    --target '{"Arn":"arn:aws:lambda:...","RoleArn":"arn:aws:iam::..."}' \
    --flexible-time-window '{"Mode":"OFF"}'

# 循环调度（支持时区）
aws scheduler create-schedule \
    --name "daily-cn-morning" \
    --schedule-expression "cron(0 9 * * ? *)" \
    --schedule-expression-timezone "Asia/Shanghai" \
    --target '{"Arn":"arn:aws:lambda:...","RoleArn":"arn:aws:iam::..."}' \
    --flexible-time-window '{"Mode":"FLEXIBLE","MaximumWindowInMinutes":15}'
```

**Scheduler vs Rule**：

| 特性 | Rule（传统） | Scheduler |
|------|-------------|-----------|
| 时区支持 | 否（UTC only） | 是 |
| 一次性调度 | 否 | 是（`at()`） |
| 灵活时间窗口 | 否 | 是 |
| 重试策略 | 有限 | 完整（最多 185 次） |
| 最大调度数 | ~300 / 账户 | 100 万 / 账户 |
| DLQ | 否 | 是 |

---

## Pipes（管道）

点对点集成，替代"事件源 → 规则 → 目标"的简单模式：

```
Source → Filter → Enrichment → Target
```

```bash
aws pipes create-pipe \
    --name "sqs-to-lambda" \
    --source "arn:aws:sqs:us-east-1:123456789:orders-queue" \
    --target "arn:aws:lambda:us-east-1:123456789:function:process-order" \
    --role-arn "arn:aws:iam::123456789:role/pipes-role" \
    --source-parameters '{
        "SqsQueueParameters": {"BatchSize": 10}
    }' \
    --filter-criteria '{
        "Filters": [{
            "Pattern": "{\"body\":{\"amount\":[{\"numeric\":[\">\",100]}]}}"
        }]
    }'
```

支持的 Source：SQS、Kinesis、DynamoDB Streams、Kafka、MQ
支持的 Target：Lambda、SQS、SNS、Step Functions、API Gateway、ECS 等

---

## Schema Registry

自动发现和记录事件结构：

```bash
# 开启事件总线的 schema discovery
aws schemas update-discoverer \
    --discoverer-id <id> \
    --state STARTED

# 查看发现的 schema
aws schemas describe-schema \
    --registry-name discovered-schemas \
    --schema-name com.myapp.orders@OrderPlaced

# 生成代码绑定（Python/Java/TypeScript）
aws schemas get-code-binding-source \
    --registry-name discovered-schemas \
    --schema-name com.myapp.orders@OrderPlaced \
    --language Python36
```

---

## Archive 与 Replay

### 创建事件存档

```bash
aws events create-archive \
    --archive-name "all-orders" \
    --event-source-arn "arn:aws:events:us-east-1:123456789:event-bus/my-app-bus" \
    --event-pattern '{"source": ["com.myapp.orders"]}' \
    --retention-days 90
```

### 重放历史事件

```bash
aws events start-replay \
    --replay-name "replay-orders-apr" \
    --event-source-arn "arn:aws:events:us-east-1:123456789:event-bus/my-app-bus" \
    --destination '{"Arn": "arn:aws:events:us-east-1:123456789:event-bus/my-app-bus"}' \
    --event-start-time "2026-04-01T00:00:00Z" \
    --event-end-time "2026-04-10T00:00:00Z"
```

> **用途**：修复 bug 后重放事件、新消费者接入时回填数据、测试规则和目标。

---

## 跨账户与跨区域

### 跨账户事件路由

```bash
# 账户 A：允许账户 B 发送事件到自己的 bus
aws events put-permission \
    --event-bus-name my-app-bus \
    --action events:PutEvents \
    --principal 999888777666 \
    --statement-id "allow-account-b"

# 账户 B：发送事件到账户 A 的 bus
aws events put-events --entries '[{
    "Source": "com.teamb.service",
    "DetailType": "Data Ready",
    "Detail": "{}",
    "EventBusName": "arn:aws:events:us-east-1:123456789:event-bus/my-app-bus"
}]'
```

### 跨区域

用规则将事件转发到另一个区域的 Event Bus：

```bash
aws events put-targets \
    --rule "replicate-events" \
    --targets '[{
        "Id": "us-west-2-bus",
        "Arn": "arn:aws:events:us-west-2:123456789:event-bus/default"
    }]'
```

---

## 安全与权限

### 发送事件

```json
{
  "Effect": "Allow",
  "Action": "events:PutEvents",
  "Resource": "arn:aws:events:us-east-1:123456789:event-bus/my-app-bus"
}
```

### 管理规则

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
  "Resource": "arn:aws:events:us-east-1:123456789:rule/my-app-bus/*"
}
```

### 目标执行角色

EventBridge 调用目标需要一个 IAM Role：

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

## 监控与调试

### CloudWatch 指标

| 指标 | 说明 |
|------|------|
| `Invocations` | 规则匹配次数 |
| `FailedInvocations` | 目标调用失败次数 |
| `TriggeredRules` | 被触发的规则数 |
| `MatchedEvents` | 匹配事件数 |
| `ThrottledRules` | 被限流的规则 |

### 调试技巧

1. **添加 CloudWatch Logs 目标**：规则同时发送到 Log Group，方便查看匹配的事件
2. **Event Pattern 测试**：

```bash
# 在线测试模式匹配
aws events test-event-pattern \
    --event-pattern '{"source":["com.myapp"]}' \
    --event '{"source":"com.myapp","detail-type":"Test","detail":{}}'
```

3. **DLQ 监控**：异步目标失败时检查 Dead Letter Queue

---

## 常见架构模式

### 微服务事件总线

```
Service A ──► Event Bus ──► Rule 1 → Service B (Lambda)
                        ──► Rule 2 → Service C (SQS → ECS)
                        ──► Rule 3 → Analytics (Kinesis → S3)
```

### 审计与合规

```
AWS 服务 ──► CloudTrail ──► EventBridge ──► Lambda（告警/自动修复）
                                        ──► S3（审计存档）
```

### CQRS 事件溯源

```
写入 API → Lambda（写）→ DynamoDB
                      → EventBridge → Lambda（投影）→ Read Model (ES/RDS)
```

---

## CLI 速查

```bash
# 事件总线
aws events list-event-buses
aws events create-event-bus --name NAME
aws events delete-event-bus --name NAME

# 发送事件
aws events put-events --entries '[{...}]'

# 规则
aws events list-rules --event-bus-name NAME
aws events put-rule --name RULE --event-pattern '{...}'
aws events describe-rule --name RULE
aws events delete-rule --name RULE

# 目标
aws events list-targets-by-rule --rule RULE
aws events put-targets --rule RULE --targets '[{...}]'
aws events remove-targets --rule RULE --ids "target-1"

# 模式测试
aws events test-event-pattern --event-pattern '{...}' --event '{...}'

# Scheduler
aws scheduler list-schedules
aws scheduler create-schedule --name NAME --schedule-expression "rate(1 hour)" ...
aws scheduler delete-schedule --name NAME
```

---

*最后更新：2026-04-13*
