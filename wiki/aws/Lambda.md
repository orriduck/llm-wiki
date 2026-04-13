# AWS Lambda

> 无服务器计算服务，按调用次数和执行时间付费，无需管理服务器。
> 与 [[EventBridge]]、[[CloudWatch]]、[[CloudTrail]] 深度集成。
> Metaflow 中 Step Functions 的轻量 step 可编译为 Lambda 执行，见 [[Metaflow工作流框架]]。

## 目录

- [[#核心概念]]
- [[#运行模型]]
- [[#部署与配置]]
- [[#触发方式]]
- [[#Layer 与依赖管理]]
- [[#并发控制]]
- [[#错误处理与重试]]
- [[#性能优化]]
- [[#监控与调试]]
- [[#安全与权限]]
- [[#成本优化]]
- [[#常见模式]]
- [[#CLI 速查]]

---

## 核心概念

| 概念 | 说明 |
|------|------|
| **Function** | 一段可执行代码，Lambda 的基本单位 |
| **Handler** | 入口函数，接收 `event` 和 `context` 两个参数 |
| **Runtime** | 执行环境（Python 3.12、Node.js 20、Java 21、自定义等） |
| **Layer** | 可复用的依赖包（最多 5 个 Layer / 函数） |
| **Execution Environment** | Lambda 分配的沙盒容器，可被复用（warm start） |
| **Event** | 触发函数的 JSON 数据 |
| **Context** | 运行时信息（剩余时间、请求 ID、函数名等） |
| **Alias** | 指向特定版本的指针（可用于蓝绿部署） |
| **Version** | 函数代码和配置的不可变快照 |

### 资源限制

| 限制 | 值 |
|------|------|
| 最大执行时间 | 15 分钟 |
| 最大内存 | 10,240 MB |
| 部署包大小（zip） | 50 MB（直接上传）/ 250 MB（解压后）|
| 容器镜像大小 | 10 GB |
| `/tmp` 临时存储 | 512 MB（可扩展到 10 GB） |
| 环境变量总大小 | 4 KB |
| 并发执行数（默认） | 1,000 / 区域（可申请提升） |

---

## 运行模型

### 调用方式

| 方式 | 说明 | 典型场景 |
|------|------|---------|
| **同步（RequestResponse）** | 调用方等待结果返回 | API Gateway、直接调用 |
| **异步（Event）** | 调用方立刻返回，Lambda 异步执行 | S3 事件、SNS、EventBridge |
| **流式（ResponseStream）** | 分块流式返回响应 | 大文件生成、SSE |

### 生命周期

```
冷启动（Cold Start）                    热启动（Warm Start）
┌──────────────────────────┐         ┌──────────────┐
│ 下载代码 → 启动运行时 →    │         │              │
│ 初始化 handler 外的代码 → │         │  直接执行      │
│ 执行 handler            │         │  handler      │
└──────────────────────────┘         └──────────────┘
```

**冷启动耗时**：
- Python/Node.js：~200-500ms
- Java：~1-3s（JVM 启动）
- 容器镜像：~1-5s（取决于镜像大小）

---

## 部署与配置

### 基本函数结构（Python）

```python
# lambda_function.py
import json
import boto3
import os

# 初始化代码（handler 外）——只在冷启动时执行一次
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    """
    event: 触发事件的 JSON
    context: 运行时上下文
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

### 使用容器镜像部署

```dockerfile
FROM public.ecr.aws/lambda/python:3.12

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ${LAMBDA_TASK_ROOT}/

CMD ["lambda_function.lambda_handler"]
```

```bash
# 构建并推送到 ECR
docker build -t my-lambda .
docker tag my-lambda:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/my-lambda:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/my-lambda:latest

# 创建函数
aws lambda create-function \
    --function-name my-function \
    --package-type Image \
    --code ImageUri=123456789.dkr.ecr.us-east-1.amazonaws.com/my-lambda:latest \
    --role arn:aws:iam::123456789:role/lambda-execution-role
```

### 环境变量

```bash
aws lambda update-function-configuration \
    --function-name my-function \
    --environment "Variables={DB_HOST=mydb.cluster.us-east-1.rds.amazonaws.com,STAGE=prod}"
```

> **敏感信息**不要存环境变量，用 Secrets Manager 或 SSM Parameter Store，在函数初始化时读取。

---

## 触发方式

### 事件源映射（Event Source Mapping）

Lambda 主动拉取事件：

| 事件源 | 说明 |
|--------|------|
| SQS | 批量拉取消息，支持 batch size 和 batch window |
| Kinesis | 按 shard 拉取流数据 |
| DynamoDB Streams | 表变更事件 |
| Kafka (MSK / self-managed) | 消费 Kafka topic |

### 直接触发

事件源推送事件到 Lambda：

| 事件源 | 调用方式 | 说明 |
|--------|---------|------|
| API Gateway | 同步 | REST/HTTP API → Lambda |
| ALB | 同步 | 负载均衡器后端 |
| S3 | 异步 | 对象创建/删除事件 |
| SNS | 异步 | 消息通知 |
| [[EventBridge]] | 异步 | 定时/事件规则触发 |
| CloudFormation | 异步 | 自定义资源 |
| IoT | 异步 | IoT 规则引擎 |

### EventBridge 定时触发示例

```bash
# 每 5 分钟触发
aws events put-rule \
    --name "every-5-min" \
    --schedule-expression "rate(5 minutes)"

aws events put-targets \
    --rule "every-5-min" \
    --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:123456789:function:my-function"

# 授权 EventBridge 调用 Lambda
aws lambda add-permission \
    --function-name my-function \
    --statement-id eventbridge-invoke \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:us-east-1:123456789:rule/every-5-min
```

---

## Layer 与依赖管理

### 创建 Layer

```bash
# 目录结构必须符合运行时要求
mkdir -p python/lib/python3.12/site-packages
pip install -t python/lib/python3.12/site-packages pandas numpy
zip -r layer.zip python/

aws lambda publish-layer-version \
    --layer-name data-deps \
    --zip-file fileb://layer.zip \
    --compatible-runtimes python3.12
```

### 附加 Layer 到函数

```bash
aws lambda update-function-configuration \
    --function-name my-function \
    --layers arn:aws:lambda:us-east-1:123456789:layer:data-deps:1
```

> **限制**：最多 5 个 Layer，解压后总大小 ≤ 250 MB。大依赖建议用容器镜像部署。

---

## 并发控制

| 类型 | 说明 |
|------|------|
| **Unreserved Concurrency** | 默认，共享区域配额（1000） |
| **Reserved Concurrency** | 为函数预留固定并发数，其他函数不能占用 |
| **Provisioned Concurrency** | 预热指定数量的执行环境，消除冷启动 |

```bash
# 预留并发（最大 100 个实例）
aws lambda put-function-concurrency \
    --function-name my-function \
    --reserved-concurrent-executions 100

# 预置并发（保持 10 个热实例）
aws lambda put-provisioned-concurrency-config \
    --function-name my-function \
    --qualifier prod \
    --provisioned-concurrent-executions 10
```

---

## 错误处理与重试

### 同步调用

调用方收到错误，由调用方决定是否重试。

### 异步调用

Lambda 自动重试：

```
第一次失败 → 等待 1 分钟 → 第二次重试 → 仍然失败 → 发送到 DLQ / 目标
```

```bash
# 配置异步调用：最多重试 1 次，失败发送到 SQS DLQ
aws lambda put-function-event-invoke-config \
    --function-name my-function \
    --maximum-retry-attempts 1 \
    --maximum-event-age-in-seconds 3600 \
    --destination-config '{
        "OnFailure": {
            "Destination": "arn:aws:sqs:us-east-1:123456789:lambda-dlq"
        }
    }'
```

### 幂等性

异步调用可能重复投递（at-least-once），**handler 必须幂等**：

```python
import hashlib

def lambda_handler(event, context):
    # 用事件内容生成幂等 key
    idempotency_key = hashlib.sha256(
        json.dumps(event, sort_keys=True).encode()
    ).hexdigest()
    
    # 检查是否已处理（DynamoDB 条件写入）
    try:
        table.put_item(
            Item={'idempotency_key': idempotency_key, 'ttl': int(time.time()) + 3600},
            ConditionExpression='attribute_not_exists(idempotency_key)'
        )
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return {'statusCode': 200, 'body': 'Already processed'}
    
    # 实际处理逻辑...
```

---

## 性能优化

### 冷启动优化

1. **减小部署包大小**：只打包必要依赖
2. **使用 Provisioned Concurrency**：关键路径函数预热
3. **SnapStart（Java）**：JVM 快照，冷启动降到 ~200ms
4. **初始化代码放 handler 外**：全局变量、SDK 客户端在冷启动时初始化，热启动复用

### 内存与 CPU

Lambda 的 CPU 和内存**成比例分配**：
- 128 MB → 最小 CPU
- 1,769 MB → 1 vCPU
- 10,240 MB → 6 vCPU

```python
# 计算密集型任务，即使不需要大内存也应分配更多内存（获得更多 CPU）
# 1769 MB = 1 vCPU，计算型建议起步 1769 MB
```

### 连接复用

```python
import urllib3

# handler 外初始化——跨请求复用连接池
http = urllib3.PoolManager()
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # 复用已有连接
    response = http.request('GET', 'https://api.example.com/data')
    ...
```

---

## 监控与调试

### CloudWatch 指标

Lambda 自动推送到 [[CloudWatch]] 的指标：

| 指标 | 说明 |
|------|------|
| `Invocations` | 调用次数 |
| `Duration` | 执行时间 |
| `Errors` | 函数错误次数 |
| `Throttles` | 被限流次数 |
| `ConcurrentExecutions` | 并发执行数 |
| `IteratorAge` | 流事件源延迟（Kinesis/DynamoDB） |

### 日志

```python
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(f"Request ID: {context.aws_request_id}")
    logger.info(f"Event: {json.dumps(event)}")
    # 日志自动写入 CloudWatch Logs
    # Log Group: /aws/lambda/<function-name>
```

### X-Ray 追踪

```bash
aws lambda update-function-configuration \
    --function-name my-function \
    --tracing-config Mode=Active
```

```python
from aws_xray_sdk.core import xray_recorder, patch_all
patch_all()  # 自动追踪 boto3、requests 等调用

def lambda_handler(event, context):
    with xray_recorder.in_subsegment('process-data'):
        # 自定义追踪段
        result = process(event)
    return result
```

---

## 安全与权限

### 执行角色（Execution Role）

Lambda 函数运行时使用的 IAM Role：

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

Trust policy：

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

### 资源策略（Resource-based Policy）

控制谁可以调用此函数：

```bash
# 允许 S3 触发
aws lambda add-permission \
    --function-name my-function \
    --statement-id s3-trigger \
    --action lambda:InvokeFunction \
    --principal s3.amazonaws.com \
    --source-arn arn:aws:s3:::my-bucket \
    --source-account 123456789
```

### VPC 接入

```bash
# Lambda 访问 VPC 内资源（RDS、ElastiCache 等）
aws lambda update-function-configuration \
    --function-name my-function \
    --vpc-config SubnetIds=subnet-aaa,subnet-bbb,SecurityGroupIds=sg-xxx
```

> **注意**：VPC Lambda 访问公网需要 NAT Gateway。建议用 VPC Endpoint 访问 AWS 服务（S3、DynamoDB、Secrets Manager）。

---

## 成本优化

### 定价模型

| 计费项 | 单价（us-east-1） |
|--------|------------------|
| 请求次数 | $0.20 / 百万次 |
| 执行时间 | $0.0000166667 / GB-秒 |
| Provisioned Concurrency | $0.0000041667 / GB-秒（空闲也收费） |
| 免费额度 | 100 万次/月 + 40 万 GB-秒/月 |

### 优化策略

1. **Right-size 内存**：用 [AWS Lambda Power Tuning](https://github.com/alexcasalboni/aws-lambda-power-tuning) 工具找到最佳内存
2. **使用 ARM64（Graviton2）**：价格低 20%，性能持平或更好
3. **避免不必要的 Provisioned Concurrency**
4. **异步模式下调低 `maximum-event-age`**：失败事件不要无限重试

```bash
# 使用 ARM64 架构
aws lambda create-function \
    --function-name my-function \
    --architectures arm64 \
    --runtime python3.12 \
    ...
```

---

## 常见模式

### API 后端

```
Client → API Gateway → Lambda → DynamoDB
```

### 事件处理管道

```
S3 上传 → Lambda A（验证）→ SQS → Lambda B（处理）→ DynamoDB
                                                    → S3（结果）
```

### 定时任务

```
EventBridge (cron) → Lambda → 清理过期数据 / 生成报表
```

### 扇出（Fan-out）

```
SNS/EventBridge → Lambda A（发邮件）
               → Lambda B（写数据库）
               → Lambda C（推送通知）
```

---

## CLI 速查

```bash
# 创建函数
aws lambda create-function --function-name NAME \
    --runtime python3.12 --handler lambda_function.lambda_handler \
    --zip-file fileb://function.zip --role arn:aws:iam::XXX:role/ROLE

# 更新代码
aws lambda update-function-code --function-name NAME \
    --zip-file fileb://function.zip

# 更新配置
aws lambda update-function-configuration --function-name NAME \
    --memory-size 512 --timeout 60

# 调用（同步）
aws lambda invoke --function-name NAME \
    --payload '{"key":"value"}' output.json

# 调用（异步）
aws lambda invoke --function-name NAME \
    --invocation-type Event --payload '{"key":"value"}' output.json

# 查看日志（最近）
aws logs tail /aws/lambda/NAME --follow

# 列出函数
aws lambda list-functions --query 'Functions[].FunctionName'

# 删除函数
aws lambda delete-function --function-name NAME
```

---

*最后更新：2026-04-13*
