# AWS Lambda / AWS Lambda 无服务器计算

AWS Lambda is a serverless compute service that charges based on invocation count and execution duration, with no server management required. It integrates deeply with EventBridge, CloudWatch, and CloudTrail.

> AWS Lambda 是无服务器计算服务，按调用次数和执行时间付费，无需管理服务器。与 [[EventBridge]]、[[CloudWatch]]、[[CloudTrail]] 深度集成。

## Table of Contents / 目录

- [[#Core Concepts / 核心概念]]
- [[#Execution Model / 运行模型]]
- [[#Deployment and Configuration / 部署与配置]]
- [[#Trigger Methods / 触发方式]]
- [[#Layers and Dependency Management / Layer 与依赖管理]]
- [[#Concurrency Control / 并发控制]]
- [[#Error Handling and Retry / 错误处理与重试]]
- [[#Performance Optimization / 性能优化]]
- [[#Monitoring and Debugging / 监控与调试]]
- [[#Security and Permissions / 安全与权限]]
- [[#Cost Optimization / 成本优化]]
- [[#Common Patterns / 常见模式]]
- [[#CLI Quick Reference / CLI 速查]]

---

## Core Concepts / 核心概念

| Concept | Description |
|---------|-------------|
| **Function** | A piece of executable code; the basic unit of Lambda |
| **Handler** | Entry function accepting `event` and `context` parameters |
| **Runtime** | Execution environment (Python 3.12, Node.js 20, Java 21, custom, etc.) |
| **Layer** | Reusable dependency packages (max 5 layers per function) |
| **Execution Environment** | Sandbox container allocated by Lambda, may be reused (warm start) |
| **Event** | JSON data that triggers the function |
| **Context** | Runtime info (remaining time, request ID, function name, etc.) |
| **Alias** | Pointer to a specific version (usable for blue/green deployments) |
| **Version** | Immutable snapshot of function code and configuration |

> | 概念 | 说明 |
> |------|------|
> | **Function** | 一段可执行代码，Lambda 的基本单位 |
> | **Handler** | 入口函数，接收 `event` 和 `context` 两个参数 |
> | **Runtime** | 执行环境（Python 3.12、Node.js 20、Java 21、自定义等） |
> | **Layer** | 可复用的依赖包（最多 5 个 Layer / 函数） |
> | **Execution Environment** | Lambda 分配的沙盒容器，可被复用（warm start） |
> | **Event** | 触发函数的 JSON 数据 |
> | **Context** | 运行时信息（剩余时间、请求 ID、函数名等） |
> | **Alias** | 指向特定版本的指针（可用于蓝绿部署） |
> | **Version** | 函数代码和配置的不可变快照 |

### Resource Limits / 资源限制

| Limit | Value |
|-------|-------|
| Max execution time | 15 minutes |
| Max memory | 10,240 MB |
| Deployment package size (zip) | 50 MB (direct upload) / 250 MB (unzipped) |
| Container image size | 10 GB |
| `/tmp` temporary storage | 512 MB (expandable to 10 GB) |
| Total env variable size | 4 KB |
| Concurrent executions (default) | 1,000 / region (can request increase) |

> | 限制 | 值 |
> |------|------|
> | 最大执行时间 | 15 分钟 |
> | 最大内存 | 10,240 MB |
> | 部署包大小（zip） | 50 MB（直接上传）/ 250 MB（解压后）|
> | 容器镜像大小 | 10 GB |
> | `/tmp` 临时存储 | 512 MB（可扩展到 10 GB） |
> | 环境变量总大小 | 4 KB |
> | 并发执行数（默认） | 1,000 / 区域（可申请提升） |

---

## Execution Model / 运行模型

### Invocation Types / 调用方式

| Type | Description | Typical Use Case |
|------|-------------|-----------------|
| **Synchronous (RequestResponse)** | Caller waits for result | API Gateway, direct invocation |
| **Asynchronous (Event)** | Caller returns immediately; Lambda executes async | S3 events, SNS, EventBridge |
| **Streaming (ResponseStream)** | Chunked streaming response | Large file generation, SSE |

> | 方式 | 说明 | 典型场景 |
> |------|------|---------|
> | **同步（RequestResponse）** | 调用方等待结果返回 | API Gateway、直接调用 |
> | **异步（Event）** | 调用方立刻返回，Lambda 异步执行 | S3 事件、SNS、EventBridge |
> | **流式（ResponseStream）** | 分块流式返回响应 | 大文件生成、SSE |

### Lifecycle / 生命周期

```
Cold Start                                    Warm Start
┌──────────────────────────┐         ┌──────────────┐
│ Download code → start    │         │              │
│ runtime → init code      │         │  Execute     │
│ outside handler →        │         │  handler     │
│ execute handler          │         │  directly    │
└──────────────────────────┘         └──────────────┘
```

> ```
> 冷启动（Cold Start）                    热启动（Warm Start）
> ┌──────────────────────────┐         ┌──────────────┐
> │ 下载代码 → 启动运行时 →    │         │              │
> │ 初始化 handler 外的代码 → │         │  直接执行      │
> │ 执行 handler            │         │  handler      │
> └──────────────────────────┘         └──────────────┘
> ```

**Cold start latency:**
- Python/Node.js: ~200–500 ms
- Java: ~1–3 s (JVM startup)
- Container image: ~1–5 s (depends on image size)

> **冷启动耗时：**
> - Python/Node.js：~200-500ms
> - Java：~1-3s（JVM 启动）
> - 容器镜像：~1-5s（取决于镜像大小）

---

## Deployment and Configuration / 部署与配置

### Basic Function Structure (Python) / 基本函数结构（Python）

```python
# lambda_function.py
import json
import boto3
import os

# Initialization code (outside handler) — runs only once on cold start
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    """
    event: JSON of the triggering event
    context: runtime context
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

### Deploying with Container Images / 使用容器镜像部署

```dockerfile
FROM public.ecr.aws/lambda/python:3.12

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ${LAMBDA_TASK_ROOT}/

CMD ["lambda_function.lambda_handler"]
```

```bash
# Build and push to ECR
docker build -t my-lambda .
docker tag my-lambda:latest <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/my-lambda:latest
docker push <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/my-lambda:latest

# Create function
aws lambda create-function \
    --function-name my-function \
    --package-type Image \
    --code ImageUri=<your-account-id>.dkr.ecr.us-east-1.amazonaws.com/my-lambda:latest \
    --role arn:aws:iam::<your-account-id>:role/<lambda-execution-role>
```

> ```bash
> # 构建并推送到 ECR
> docker build -t my-lambda .
> docker tag my-lambda:latest <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/my-lambda:latest
> docker push <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/my-lambda:latest
>
> # 创建函数
> aws lambda create-function \
>     --function-name my-function \
>     --package-type Image \
>     --code ImageUri=<your-account-id>.dkr.ecr.us-east-1.amazonaws.com/my-lambda:latest \
>     --role arn:aws:iam::<your-account-id>:role/<lambda-execution-role>
> ```

### Environment Variables / 环境变量

```bash
aws lambda update-function-configuration \
    --function-name my-function \
    --environment "Variables={DB_HOST=<your-db-host>,STAGE=prod}"
```

> **Sensitive information** should not be stored in environment variables. Use Secrets Manager or SSM Parameter Store and retrieve values during function initialization.

> **敏感信息**不要存环境变量，用 Secrets Manager 或 SSM Parameter Store，在函数初始化时读取。

---

## Trigger Methods / 触发方式

### Event Source Mapping / 事件源映射

Lambda actively polls events from:

| Event Source | Description |
|-------------|-------------|
| SQS | Batch polling, supports batch size and batch window |
| Kinesis | Pull stream data per shard |
| DynamoDB Streams | Table change events |
| Kafka (MSK / self-managed) | Consume Kafka topics |

> Lambda 主动拉取事件来源：
>
> | 事件源 | 说明 |
> |--------|------|
> | SQS | 批量拉取消息，支持 batch size 和 batch window |
> | Kinesis | 按 shard 拉取流数据 |
> | DynamoDB Streams | 表变更事件 |
> | Kafka (MSK / self-managed) | 消费 Kafka topic |

### Direct Triggers / 直接触发

Event sources push events to Lambda:

| Event Source | Invocation | Description |
|-------------|-----------|-------------|
| API Gateway | Sync | REST/HTTP API → Lambda |
| ALB | Sync | Load balancer backend |
| S3 | Async | Object created/deleted events |
| SNS | Async | Message notification |
| [[EventBridge]] | Async | Scheduled/event rule triggers |
| CloudFormation | Async | Custom resources |
| IoT | Async | IoT rules engine |

> | 事件源 | 调用方式 | 说明 |
> |--------|---------|------|
> | API Gateway | 同步 | REST/HTTP API → Lambda |
> | ALB | 同步 | 负载均衡器后端 |
> | S3 | 异步 | 对象创建/删除事件 |
> | SNS | 异步 | 消息通知 |
> | [[EventBridge]] | 异步 | 定时/事件规则触发 |
> | CloudFormation | 异步 | 自定义资源 |
> | IoT | 异步 | IoT 规则引擎 |

### EventBridge Scheduled Trigger Example / EventBridge 定时触发示例

```bash
# Trigger every 5 minutes
aws events put-rule \
    --name "every-5-min" \
    --schedule-expression "rate(5 minutes)"

aws events put-targets \
    --rule "every-5-min" \
    --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:<your-account-id>:function:my-function"

# Grant EventBridge permission to invoke Lambda
aws lambda add-permission \
    --function-name my-function \
    --statement-id eventbridge-invoke \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:us-east-1:<your-account-id>:rule/every-5-min
```

> ```bash
> # 每 5 分钟触发
> aws events put-rule \
>     --name "every-5-min" \
>     --schedule-expression "rate(5 minutes)"
>
> aws events put-targets \
>     --rule "every-5-min" \
>     --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:<your-account-id>:function:my-function"
>
> # 授权 EventBridge 调用 Lambda
> aws lambda add-permission \
>     --function-name my-function \
>     --statement-id eventbridge-invoke \
>     --action lambda:InvokeFunction \
>     --principal events.amazonaws.com \
>     --source-arn arn:aws:events:us-east-1:<your-account-id>:rule/every-5-min
> ```

---

## Layers and Dependency Management / Layer 与依赖管理

### Creating a Layer / 创建 Layer

```bash
# Directory structure must conform to runtime requirements
mkdir -p python/lib/python3.12/site-packages
pip install -t python/lib/python3.12/site-packages pandas numpy
zip -r layer.zip python/

aws lambda publish-layer-version \
    --layer-name data-deps \
    --zip-file fileb://layer.zip \
    --compatible-runtimes python3.12
```

### Attaching a Layer to a Function / 附加 Layer 到函数

```bash
aws lambda update-function-configuration \
    --function-name my-function \
    --layers arn:aws:lambda:us-east-1:<your-account-id>:layer:data-deps:1
```

> **Limit:** Max 5 layers; total unzipped size ≤ 250 MB. For large dependencies, use container image deployment.

> **限制**：最多 5 个 Layer，解压后总大小 ≤ 250 MB。大依赖建议用容器镜像部署。

---

## Concurrency Control / 并发控制

| Type | Description |
|------|-------------|
| **Unreserved Concurrency** | Default; shares the regional quota (1,000) |
| **Reserved Concurrency** | Reserves a fixed concurrency count for the function; other functions cannot use it |
| **Provisioned Concurrency** | Pre-warms a specified number of execution environments, eliminating cold starts |

> | 类型 | 说明 |
> |------|------|
> | **Unreserved Concurrency** | 默认，共享区域配额（1000） |
> | **Reserved Concurrency** | 为函数预留固定并发数，其他函数不能占用 |
> | **Provisioned Concurrency** | 预热指定数量的执行环境，消除冷启动 |

```bash
# Reserved concurrency (max 100 instances)
aws lambda put-function-concurrency \
    --function-name my-function \
    --reserved-concurrent-executions 100

# Provisioned concurrency (keep 10 warm instances)
aws lambda put-provisioned-concurrency-config \
    --function-name my-function \
    --qualifier prod \
    --provisioned-concurrent-executions 10
```

---

## Error Handling and Retry / 错误处理与重试

### Synchronous Invocation / 同步调用

The caller receives the error and decides whether to retry.

> 调用方收到错误，由调用方决定是否重试。

### Asynchronous Invocation / 异步调用

Lambda retries automatically:

```
First failure → wait 1 min → first retry → still fails → send to DLQ / destination
```

> ```
> 第一次失败 → 等待 1 分钟 → 第二次重试 → 仍然失败 → 发送到 DLQ / 目标
> ```

```bash
# Configure async invocation: max 1 retry, failures sent to SQS DLQ
aws lambda put-function-event-invoke-config \
    --function-name my-function \
    --maximum-retry-attempts 1 \
    --maximum-event-age-in-seconds 3600 \
    --destination-config '{
        "OnFailure": {
            "Destination": "arn:aws:sqs:us-east-1:<your-account-id>:<your-dlq-name>"
        }
    }'
```

### Idempotency / 幂等性

Async invocations may be delivered multiple times (at-least-once). **The handler must be idempotent.**

> 异步调用可能重复投递（at-least-once），**handler 必须幂等**。

```python
import hashlib

def lambda_handler(event, context):
    # Generate idempotency key from event content
    idempotency_key = hashlib.sha256(
        json.dumps(event, sort_keys=True).encode()
    ).hexdigest()
    
    # Check if already processed (DynamoDB conditional write)
    try:
        table.put_item(
            Item={'idempotency_key': idempotency_key, 'ttl': int(time.time()) + 3600},
            ConditionExpression='attribute_not_exists(idempotency_key)'
        )
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return {'statusCode': 200, 'body': 'Already processed'}
    
    # Actual processing logic...
```

---

## Performance Optimization / 性能优化

### Cold Start Optimization / 冷启动优化

1. **Reduce deployment package size:** Only package necessary dependencies
2. **Use Provisioned Concurrency:** Pre-warm critical path functions
3. **SnapStart (Java):** JVM snapshot, cold start reduced to ~200 ms
4. **Place init code outside handler:** Global variables and SDK clients initialized once on cold start, reused on warm start

> 1. **减小部署包大小**：只打包必要依赖
> 2. **使用 Provisioned Concurrency**：关键路径函数预热
> 3. **SnapStart（Java）**：JVM 快照，冷启动降到 ~200ms
> 4. **初始化代码放 handler 外**：全局变量、SDK 客户端在冷启动时初始化，热启动复用

### Memory and CPU / 内存与 CPU

Lambda allocates CPU proportionally to memory:
- 128 MB → minimum CPU
- 1,769 MB → 1 vCPU
- 10,240 MB → 6 vCPU

> Lambda 的 CPU 和内存**成比例分配**：
> - 128 MB → 最小 CPU
> - 1,769 MB → 1 vCPU
> - 10,240 MB → 6 vCPU

### Connection Reuse / 连接复用

```python
import urllib3

# Initialize outside handler — reuse connection pool across requests
http = urllib3.PoolManager()
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # Reuse existing connections
    response = http.request('GET', 'https://api.example.com/data')
    ...
```

---

## Monitoring and Debugging / 监控与调试

### CloudWatch Metrics / CloudWatch 指标

Metrics Lambda automatically pushes to [[CloudWatch]]:

| Metric | Description |
|--------|-------------|
| `Invocations` | Invocation count |
| `Duration` | Execution time |
| `Errors` | Function error count |
| `Throttles` | Throttled invocation count |
| `ConcurrentExecutions` | Concurrent execution count |
| `IteratorAge` | Stream event source lag (Kinesis/DynamoDB) |

> | 指标 | 说明 |
> |------|------|
> | `Invocations` | 调用次数 |
> | `Duration` | 执行时间 |
> | `Errors` | 函数错误次数 |
> | `Throttles` | 被限流次数 |
> | `ConcurrentExecutions` | 并发执行数 |
> | `IteratorAge` | 流事件源延迟（Kinesis/DynamoDB） |

### Logs / 日志

```python
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(f"Request ID: {context.aws_request_id}")
    logger.info(f"Event: {json.dumps(event)}")
    # Logs are automatically written to CloudWatch Logs
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
patch_all()  # Auto-trace boto3, requests, etc.

def lambda_handler(event, context):
    with xray_recorder.in_subsegment('process-data'):
        # Custom trace segment
        result = process(event)
    return result
```

---

## Security and Permissions / 安全与权限

### Execution Role / 执行角色

The IAM Role used by Lambda at runtime:

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
      "Resource": "arn:aws:s3:::<your-bucket-name>/*"
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

Controls who can invoke this function:

> 控制谁可以调用此函数：

```bash
# Allow S3 to trigger
aws lambda add-permission \
    --function-name my-function \
    --statement-id s3-trigger \
    --action lambda:InvokeFunction \
    --principal s3.amazonaws.com \
    --source-arn arn:aws:s3:::<your-bucket-name> \
    --source-account <your-account-id>
```

### VPC Access / VPC 接入

```bash
# Lambda accesses VPC resources (RDS, ElastiCache, etc.)
aws lambda update-function-configuration \
    --function-name my-function \
    --vpc-config SubnetIds=subnet-aaa,subnet-bbb,SecurityGroupIds=sg-xxx
```

> **Note:** VPC Lambda accessing the public internet requires a NAT Gateway. Use VPC Endpoints to access AWS services (S3, DynamoDB, Secrets Manager).

> **注意**：VPC Lambda 访问公网需要 NAT Gateway。建议用 VPC Endpoint 访问 AWS 服务（S3、DynamoDB、Secrets Manager）。

---

## Cost Optimization / 成本优化

### Pricing Model / 定价模型

| Billing Item | Price (us-east-1) |
|-------------|-------------------|
| Request count | $0.20 / million |
| Execution time | $0.0000166667 / GB-second |
| Provisioned Concurrency | $0.0000041667 / GB-second (charged even when idle) |
| Free tier | 1M requests/month + 400K GB-seconds/month |

> | 计费项 | 单价（us-east-1） |
> |--------|------------------|
> | 请求次数 | $0.20 / 百万次 |
> | 执行时间 | $0.0000166667 / GB-秒 |
> | Provisioned Concurrency | $0.0000041667 / GB-秒（空闲也收费） |
> | 免费额度 | 100 万次/月 + 40 万 GB-秒/月 |

### Optimization Strategies / 优化策略

1. **Right-size memory:** Use [AWS Lambda Power Tuning](https://github.com/alexcasalboni/aws-lambda-power-tuning) to find optimal memory
2. **Use ARM64 (Graviton2):** 20% cheaper with equal or better performance
3. **Avoid unnecessary Provisioned Concurrency**
4. **Lower `maximum-event-age` in async mode:** Don't retry failed events indefinitely

> 1. **Right-size 内存**：用 AWS Lambda Power Tuning 工具找到最佳内存
> 2. **使用 ARM64（Graviton2）**：价格低 20%，性能持平或更好
> 3. **避免不必要的 Provisioned Concurrency**
> 4. **异步模式下调低 `maximum-event-age`**：失败事件不要无限重试

```bash
# Use ARM64 architecture
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
S3 upload → Lambda A (validate) → SQS → Lambda B (process) → DynamoDB
                                                             → S3 (results)
```

### Scheduled Tasks / 定时任务

```
EventBridge (cron) → Lambda → Clean up expired data / Generate reports
```

### Fan-out / 扇出

```
SNS/EventBridge → Lambda A (send email)
               → Lambda B (write to DB)
               → Lambda C (push notification)
```

---

## CLI Quick Reference / CLI 速查

```bash
# Create function
aws lambda create-function --function-name NAME \
    --runtime python3.12 --handler lambda_function.lambda_handler \
    --zip-file fileb://function.zip --role arn:aws:iam::<your-account-id>:role/<role-name>

# Update code
aws lambda update-function-code --function-name NAME \
    --zip-file fileb://function.zip

# Update configuration
aws lambda update-function-configuration --function-name NAME \
    --memory-size 512 --timeout 60

# Invoke (synchronous)
aws lambda invoke --function-name NAME \
    --payload '{"key":"value"}' output.json

# Invoke (asynchronous)
aws lambda invoke --function-name NAME \
    --invocation-type Event --payload '{"key":"value"}' output.json

# View recent logs
aws logs tail /aws/lambda/NAME --follow

# List functions
aws lambda list-functions --query 'Functions[].FunctionName'

# Delete function
aws lambda delete-function --function-name NAME
```

---

*最后更新：2026-04-16*
