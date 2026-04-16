# AWS Lambda

> Serverless compute service, billed per invocation and execution time, no server management needed.
> Deeply integrated with [[EventBridge]], [[CloudWatch]], and [[CloudTrail]].
> In Metaflow, lightweight Step Functions steps can compile to Lambda execution; see [[Metaflow工作流框架]].

> 无服务器计算服务，按调用次数和执行时间付费，无需管理服务器。
> 与 [[EventBridge]]、[[CloudWatch]]、[[CloudTrail]] 深度集成。
> Metaflow 中 Step Functions 的轻量 step 可编译为 Lambda 执行，见 [[Metaflow工作流框架]]。

## Table of Contents / 目录

- [[#Core Concepts / 核心概念]]
- [[#Execution Model / 运行模型]]
- [[#Deployment & Configuration / 部署与配置]]
- [[#Trigger Methods / 触发方式]]
- [[#Layers & Dependency Management / Layer 与依赖管理]]
- [[#Concurrency Control / 并发控制]]
- [[#Error Handling & Retries / 错误处理与重试]]
- [[#Performance Optimization / 性能优化]]
- [[#Monitoring & Debugging / 监控与调试]]
- [[#Security & Permissions / 安全与权限]]
- [[#Cost Optimization / 成本优化]]
- [[#Common Patterns / 常见模式]]
- [[#CLI Quick Reference / CLI 速查]]

---

## Core Concepts / 核心概念

| Concept / 概念 | Description / 说明 |
|------|------|
| **Function** | A piece of executable code, the basic unit of Lambda / 一段可执行代码，Lambda 的基本单位 |
| **Handler** | Entry function, receives `event` and `context` parameters / 入口函数，接收 `event` 和 `context` 两个参数 |
| **Runtime** | Execution environment (Python 3.12, Node.js 20, Java 21, custom, etc.) / 执行环境（Python 3.12、Node.js 20、Java 21、自定义等） |
| **Layer** | Reusable dependency package (max 5 Layers per function) / 可复用的依赖包（最多 5 个 Layer / 函数） |
| **Execution Environment** | Sandbox container allocated by Lambda, can be reused (warm start) / Lambda 分配的沙盒容器，可被复用（warm start） |
| **Event** | JSON data that triggers the function / 触发函数的 JSON 数据 |
| **Context** | Runtime information (remaining time, request ID, function name, etc.) / 运行时信息（剩余时间、请求 ID、函数名等） |
| **Alias** | Pointer to a specific version (usable for blue-green deployments) / 指向特定版本的指针（可用于蓝绿部署） |
| **Version** | Immutable snapshot of function code and configuration / 函数代码和配置的不可变快照 |

### Resource Limits / 资源限制

| Limit / 限制 | Value / 值 |
|------|------|
| Max execution time / 最大执行时间 | 15 minutes / 15 分钟 |
| Max memory / 最大内存 | 10,240 MB |
| Deployment package (zip) / 部署包大小（zip） | 50 MB (direct upload) / 250 MB (unzipped) / 50 MB（直接上传）/ 250 MB（解压后） |
| Container image size / 容器镜像大小 | 10 GB |
| `/tmp` temp storage / `/tmp` 临时存储 | 512 MB (expandable to 10 GB) / 512 MB（可扩展到 10 GB） |
| Environment variables total / 环境变量总大小 | 4 KB |
| Default concurrent executions / 并发执行数（默认） | 1,000 per region (can request increase) / 1,000 / 区域（可申请提升） |

---

## Execution Model / 运行模型

### Invocation Types / 调用方式

| Type / 方式 | Description / 说明 | Typical Scenario / 典型场景 |
|------|------|---------|
| **Synchronous (RequestResponse)** | Caller waits for result / 调用方等待结果返回 | API Gateway, direct invocation / API Gateway、直接调用 |
| **Asynchronous (Event)** | Caller returns immediately, Lambda executes async / 调用方立刻返回，Lambda 异步执行 | S3 events, SNS, EventBridge / S3 事件、SNS、EventBridge |
| **Streaming (ResponseStream)** | Chunked streaming response / 分块流式返回响应 | Large file generation, SSE / 大文件生成、SSE |

### Lifecycle / 生命周期

```
Cold Start                              Warm Start
冷启动                                   热启动
┌──────────────────────────┐         ┌──────────────┐
│ Download code → Start    │         │              │
│ runtime → Init code      │         │  Execute     │
│ outside handler →        │         │  handler     │
│ Execute handler          │         │  directly    │
│                          │         │              │
│ 下载代码 → 启动运行时 →    │         │  直接执行      │
│ 初始化 handler 外的代码 → │         │  handler      │
│ 执行 handler            │         │              │
└──────────────────────────┘         └──────────────┘
```

**Cold start latency / 冷启动耗时**:
- Python/Node.js: ~200-500ms
- Java: ~1-3s (JVM startup / JVM 启动)
- Container image / 容器镜像: ~1-5s (depends on image size / 取决于镜像大小)

---

## Deployment & Configuration / 部署与配置

### Basic Function Structure (Python) / 基本函数结构（Python）

```python
# lambda_function.py
import json
import boto3
import os

# Init code (outside handler) — runs only once on cold start
# 初始化代码（handler 外）——只在冷启动时执行一次
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    """
    event: JSON of the triggering event / 触发事件的 JSON
    context: Runtime context / 运行时上下文
        - context.function_name
        - context.memory_limit_in_mb
        - context.get_remaining_time_in_millis()
        - context.aws_request_id
    """
    try:
        result = table.get_item(Key={'id': event['id']})
        return {
            'statusCode': 200,
            'body': json.dumps(result.get('Item', {}))
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

### Deploy with Container Image / 使用容器镜像部署

```dockerfile
FROM public.ecr.aws/lambda/python:3.12

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ${LAMBDA_TASK_ROOT}/

CMD ["lambda_function.lambda_handler"]
```

```bash
# Build and push to ECR / 构建并推送到 ECR
docker build -t my-lambda .
docker tag my-lambda:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/my-lambda:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/my-lambda:latest

# Create function / 创建函数
aws lambda create-function \
    --function-name my-function \
    --package-type Image \
    --code ImageUri=<account-id>.dkr.ecr.us-east-1.amazonaws.com/my-lambda:latest \
    --role arn:aws:iam::<account-id>:role/lambda-execution-role
```

### Environment Variables / 环境变量

```bash
aws lambda update-function-configuration \
    --function-name my-function \
    --environment "Variables={DB_HOST=mydb.cluster.us-east-1.rds.amazonaws.com,STAGE=prod}"
```

**Do not** store sensitive information in environment variables; use Secrets Manager or SSM Parameter Store and read them during function initialization.

> **敏感信息**不要存环境变量，用 Secrets Manager 或 SSM Parameter Store，在函数初始化时读取。

---

## Trigger Methods / 触发方式

### Event Source Mapping / 事件源映射

Lambda actively polls for events.

> Lambda 主动拉取事件。

| Event Source / 事件源 | Description / 说明 |
|--------|------|
| SQS | Batch poll messages, supports batch size and batch window / 批量拉取消息，支持 batch size 和 batch window |
| Kinesis | Poll stream data by shard / 按 shard 拉取流数据 |
| DynamoDB Streams | Table change events / 表变更事件 |
| Kafka (MSK / self-managed) | Consume Kafka topic / 消费 Kafka topic |

### Direct Triggers / 直接触发

Event sources push events to Lambda.

> 事件源推送事件到 Lambda。

| Event Source / 事件源 | Invocation / 调用方式 | Description / 说明 |
|--------|---------|------|
| API Gateway | Synchronous / 同步 | REST/HTTP API → Lambda |
| ALB | Synchronous / 同步 | Load balancer backend / 负载均衡器后端 |
| S3 | Asynchronous / 异步 | Object create/delete events / 对象创建/删除事件 |
| SNS | Asynchronous / 异步 | Message notification / 消息通知 |
| [[EventBridge]] | Asynchronous / 异步 | Scheduled/event rule trigger / 定时/事件规则触发 |
| CloudFormation | Asynchronous / 异步 | Custom resources / 自定义资源 |
| IoT | Asynchronous / 异步 | IoT rules engine / IoT 规则引擎 |

### EventBridge Scheduled Trigger Example / EventBridge 定时触发示例

```bash
# Trigger every 5 minutes / 每 5 分钟触发
aws events put-rule \
    --name "every-5-min" \
    --schedule-expression "rate(5 minutes)"

aws events put-targets \
    --rule "every-5-min" \
    --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:<account-id>:function:my-function"

# Authorize EventBridge to invoke Lambda / 授权 EventBridge 调用 Lambda
aws lambda add-permission \
    --function-name my-function \
    --statement-id eventbridge-invoke \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:us-east-1:<account-id>:rule/every-5-min
```

---

## Layers & Dependency Management / Layer 与依赖管理

### Create Layer / 创建 Layer

```bash
# Directory structure must match runtime requirements
# 目录结构必须符合运行时要求
mkdir -p python/lib/python3.12/site-packages
pip install -t python/lib/python3.12/site-packages pandas numpy
zip -r layer.zip python/

aws lambda publish-layer-version \
    --layer-name data-deps \
    --zip-file fileb://layer.zip \
    --compatible-runtimes python3.12
```

### Attach Layer to Function / 附加 Layer 到函数

```bash
aws lambda update-function-configuration \
    --function-name my-function \
    --layers arn:aws:lambda:us-east-1:<account-id>:layer:data-deps:1
```

**Limit**: Max 5 Layers, total unzipped size <= 250 MB. For large dependencies, use container image deployment.

> **限制**：最多 5 个 Layer，解压后总大小 <= 250 MB。大依赖建议用容器镜像部署。

---

## Concurrency Control / 并发控制

| Type / 类型 | Description / 说明 |
|------|------|
| **Unreserved Concurrency** | Default, shares regional quota (1000) / 默认，共享区域配额（1000） |
| **Reserved Concurrency** | Reserves fixed concurrency for a function, other functions cannot use it / 为函数预留固定并发数，其他函数不能占用 |
| **Provisioned Concurrency** | Pre-warms specified number of execution environments, eliminates cold starts / 预热指定数量的执行环境，消除冷启动 |

```bash
# Reserved concurrency (max 100 instances) / 预留并发（最大 100 个实例）
aws lambda put-function-concurrency \
    --function-name my-function \
    --reserved-concurrent-executions 100

# Provisioned concurrency (keep 10 warm instances) / 预置并发（保持 10 个热实例）
aws lambda put-provisioned-concurrency-config \
    --function-name my-function \
    --qualifier prod \
    --provisioned-concurrent-executions 10
```

---

## Error Handling & Retries / 错误处理与重试

### Synchronous Invocation / 同步调用

The caller receives the error and decides whether to retry.

> 调用方收到错误，由调用方决定是否重试。

### Asynchronous Invocation / 异步调用

Lambda retries automatically:

> Lambda 自动重试：

```
First failure → wait 1 min → Second retry → still fails → send to DLQ / destination
第一次失败 → 等待 1 分钟 → 第二次重试 → 仍然失败 → 发送到 DLQ / 目标
```

```bash
# Configure async invocation: max 1 retry, send failures to SQS DLQ
# 配置异步调用：最多重试 1 次，失败发送到 SQS DLQ
aws lambda put-function-event-invoke-config \
    --function-name my-function \
    --maximum-retry-attempts 1 \
    --maximum-event-age-in-seconds 3600 \
    --destination-config '{
        "OnFailure": {
            "Destination": "arn:aws:sqs:us-east-1:<account-id>:lambda-dlq"
        }
    }'
```

### Idempotency / 幂等性

Asynchronous invocations may deliver duplicates (at-least-once). **Handlers must be idempotent**.

> 异步调用可能重复投递（at-least-once），**handler 必须幂等**。

```python
import hashlib

def lambda_handler(event, context):
    # Generate idempotency key from event content
    # 用事件内容生成幂等 key
    idempotency_key = hashlib.sha256(
        json.dumps(event, sort_keys=True).encode()
    ).hexdigest()
    
    # Check if already processed (DynamoDB conditional write)
    # 检查是否已处理（DynamoDB 条件写入）
    try:
        table.put_item(
            Item={'idempotency_key': idempotency_key, 'ttl': int(time.time()) + 3600},
            ConditionExpression='attribute_not_exists(idempotency_key)'
        )
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return {'statusCode': 200, 'body': 'Already processed'}
    
    # Actual processing logic... / 实际处理逻辑...
```

---

## Performance Optimization / 性能优化

### Cold Start Optimization / 冷启动优化

1. **Reduce deployment package size / 减小部署包大小**: Only package necessary dependencies / 只打包必要依赖
2. **Use Provisioned Concurrency / 使用 Provisioned Concurrency**: Pre-warm critical path functions / 关键路径函数预热
3. **SnapStart (Java)**: JVM snapshot, cold start reduced to ~200ms / JVM 快照，冷启动降到 ~200ms
4. **Put init code outside handler / 初始化代码放 handler 外**: Global variables, SDK clients initialized on cold start, reused on warm start / 全局变量、SDK 客户端在冷启动时初始化，热启动复用

### Memory & CPU / 内存与 CPU

Lambda allocates CPU **proportionally** to memory:

> Lambda 的 CPU 和内存**成比例分配**：

- 128 MB → minimum CPU / 最小 CPU
- 1,769 MB → 1 vCPU
- 10,240 MB → 6 vCPU

```python
# For compute-intensive tasks, allocate more memory even if not needed for RAM (to get more CPU)
# 计算密集型任务，即使不需要大内存也应分配更多内存（获得更多 CPU）
# 1769 MB = 1 vCPU, recommended starting point for compute / 计算型建议起步 1769 MB
```

### Connection Reuse / 连接复用

```python
import urllib3

# Initialize outside handler — reuse connection pool across requests
# handler 外初始化——跨请求复用连接池
http = urllib3.PoolManager()
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # Reuse existing connections / 复用已有连接
    response = http.request('GET', 'https://api.example.com/data')
    ...
```

---

## Monitoring & Debugging / 监控与调试

### CloudWatch Metrics / CloudWatch 指标

Metrics Lambda automatically pushes to [[CloudWatch]]:

> Lambda 自动推送到 [[CloudWatch]] 的指标：

| Metric / 指标 | Description / 说明 |
|------|------|
| `Invocations` | Invocation count / 调用次数 |
| `Duration` | Execution time / 执行时间 |
| `Errors` | Function error count / 函数错误次数 |
| `Throttles` | Throttled count / 被限流次数 |
| `ConcurrentExecutions` | Concurrent execution count / 并发执行数 |
| `IteratorAge` | Stream event source delay (Kinesis/DynamoDB) / 流事件源延迟（Kinesis/DynamoDB） |

### Logging / 日志

```python
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(f"Request ID: {context.aws_request_id}")
    logger.info(f"Event: {json.dumps(event)}")
    # Logs automatically written to CloudWatch Logs
    # 日志自动写入 CloudWatch Logs
    # Log Group: /aws/lambda/<function-name>
```

### X-Ray Tracing / X-Ray 追踪

```bash
aws lambda update-function-configuration \
    --function-name my-function \
    --tracing-config Mode=Active
```

```python
from aws_xray_sdk.core import xray_recorder, patch_all
patch_all()  # Automatically trace boto3, requests, etc. / 自动追踪 boto3、requests 等调用

def lambda_handler(event, context):
    with xray_recorder.in_subsegment('process-data'):
        # Custom trace segment / 自定义追踪段
        result = process(event)
    return result
```

---

## Security & Permissions / 安全与权限

### Execution Role / 执行角色

IAM Role used by Lambda function at runtime:

> Lambda 函数运行时使用的 IAM Role：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

Trust policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
```

### Resource-based Policy / 资源策略

Controls who can invoke this function.

> 控制谁可以调用此函数。

```bash
# Allow S3 trigger / 允许 S3 触发
aws lambda add-permission \
    --function-name my-function \
    --statement-id s3-trigger \
    --action lambda:InvokeFunction \
    --principal s3.amazonaws.com \
    --source-arn arn:aws:s3:::my-bucket \
    --source-account <account-id>
```

### VPC Access / VPC 接入

```bash
# Lambda accessing VPC resources (RDS, ElastiCache, etc.)
# Lambda 访问 VPC 内资源（RDS、ElastiCache 等）
aws lambda update-function-configuration \
    --function-name my-function \
    --vpc-config SubnetIds=subnet-aaa,subnet-bbb,SecurityGroupIds=sg-xxx
```

**Note**: VPC Lambda needs NAT Gateway for public internet access. Use VPC Endpoints for AWS services (S3, DynamoDB, Secrets Manager).

> **注意**：VPC Lambda 访问公网需要 NAT Gateway。建议用 VPC Endpoint 访问 AWS 服务（S3、DynamoDB、Secrets Manager）。

---

## Cost Optimization / 成本优化

### Pricing Model / 定价模型

| Billing Item / 计费项 | Unit Price (us-east-1) / 单价（us-east-1） |
|--------|------------------|
| Request count / 请求次数 | $0.20 / million / 百万次 |
| Execution time / 执行时间 | $0.0000166667 / GB-second / GB-秒 |
| Provisioned Concurrency | $0.0000041667 / GB-second (charged even when idle) / GB-秒（空闲也收费） |
| Free tier / 免费额度 | 1M requests/month + 400K GB-seconds/month / 100 万次/月 + 40 万 GB-秒/月 |

### Optimization Strategies / 优化策略

1. **Right-size memory / Right-size 内存**: Use [AWS Lambda Power Tuning](https://github.com/alexcasalboni/aws-lambda-power-tuning) to find optimal memory / 用工具找到最佳内存
2. **Use ARM64 (Graviton2)**: 20% cheaper, equal or better performance / 价格低 20%，性能持平或更好
3. **Avoid unnecessary Provisioned Concurrency / 避免不必要的 Provisioned Concurrency**
4. **Lower `maximum-event-age` in async mode / 异步模式下调低 `maximum-event-age`**: Don't retry failed events indefinitely / 失败事件不要无限重试

```bash
# Use ARM64 architecture / 使用 ARM64 架构
aws lambda create-function \
    --function-name my-function \
    --architectures arm64 \
    --runtime python3.12 \
    ...
```

---

## Common Patterns / 常见模式

### API Backend / API 后端

```
Client → API Gateway → Lambda → DynamoDB
```

### Event Processing Pipeline / 事件处理管道

```
S3 Upload → Lambda A (validate) → SQS → Lambda B (process) → DynamoDB
S3 上传 → Lambda A（验证）→ SQS → Lambda B（处理）→ DynamoDB
                                                    → S3 (results / 结果)
```

### Scheduled Tasks / 定时任务

```
EventBridge (cron) → Lambda → Clean expired data / Generate reports
EventBridge (cron) → Lambda → 清理过期数据 / 生成报表
```

### Fan-out / 扇出

```
SNS/EventBridge → Lambda A (send email / 发邮件)
               → Lambda B (write to DB / 写数据库)
               → Lambda C (push notification / 推送通知)
```

---

## CLI Quick Reference / CLI 速查

```bash
# Create function / 创建函数
aws lambda create-function --function-name NAME \
    --runtime python3.12 --handler lambda_function.lambda_handler \
    --zip-file fileb://function.zip --role arn:aws:iam::<account-id>:role/ROLE

# Update code / 更新代码
aws lambda update-function-code --function-name NAME \
    --zip-file fileb://function.zip

# Update configuration / 更新配置
aws lambda update-function-configuration --function-name NAME \
    --memory-size 512 --timeout 60

# Invoke (synchronous) / 调用（同步）
aws lambda invoke --function-name NAME \
    --payload '{"key":"value"}' output.json

# Invoke (asynchronous) / 调用（异步）
aws lambda invoke --function-name NAME \
    --invocation-type Event --payload '{"key":"value"}' output.json

# View logs (recent) / 查看日志（最近）
aws logs tail /aws/lambda/NAME --follow

# List functions / 列出函数
aws lambda list-functions --query 'Functions[].FunctionName'

# Delete function / 删除函数
aws lambda delete-function --function-name NAME
```

---

*Last updated / 最后更新：2026-04-13*
