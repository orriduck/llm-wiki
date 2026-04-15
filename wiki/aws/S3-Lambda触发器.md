# S3 → Lambda 触发器

> S3 对象创建/删除等事件可直接触发 [[Lambda]] 函数执行，是最常见的无服务器事件处理模式之一。
> 相关页面：[[S3#事件通知]]、[[Lambda#触发方式]]、[[EventBridge]]

## 目录

- [[#核心机制]]
- [[#支持的事件类型]]
- [[#配置方法]]
- [[#Event 结构（完整）]]
- [[#多文件同时上传的行为]]
- [[#权限配置]]
- [[#错误处理与重试]]
- [[#常见陷阱]]
- [[#进阶方案]]
- [[#Lambda 代码示例]]

---

## 核心机制

S3 事件通知采用**异步推送**模式：

```
S3 PutObject
    ↓ 事件通知（异步）
Lambda 被调用（Event 调用类型）
    ↓
Lambda 执行 handler，event 参数包含 S3 事件信息
```

- S3 事件通知是**异步**触发，Lambda 调用类型为 `Event`（不等待结果）
- S3 **不保证**只调用一次（at-least-once 语义），Lambda handler 应设计为**幂等**
- Lambda 与 S3 bucket 必须在**同一个 Region**

---

## 支持的事件类型

| 事件类型 | 说明 |
|---------|------|
| `s3:ObjectCreated:*` | 所有对象创建事件（通配） |
| `s3:ObjectCreated:Put` | 普通 PUT 上传 |
| `s3:ObjectCreated:Post` | 基于 HTML 表单的 POST 上传 |
| `s3:ObjectCreated:Copy` | 服务端复制（CopyObject API） |
| `s3:ObjectCreated:CompleteMultipartUpload` | 分片上传完成 |
| `s3:ObjectRemoved:*` | 所有删除事件（通配） |
| `s3:ObjectRemoved:Delete` | 永久删除（无版本控制时） |
| `s3:ObjectRemoved:DeleteMarkerCreated` | 版本控制开启时的删除标记 |
| `s3:ObjectRestore:Post` | Glacier 对象恢复发起 |
| `s3:ObjectRestore:Completed` | Glacier 对象恢复完成 |
| `s3:ReducedRedundancyLostObject` | RRS 存储类别对象丢失 |
| `s3:Replication:*` | 跨区域复制相关事件 |

> **分片上传触发时机**：`s3:ObjectCreated:Put` 仅在单次 PUT 完成后触发。分片上传需要客户端调用 `CompleteMultipartUpload` 后，才会触发 `s3:ObjectCreated:CompleteMultipartUpload`，这时对象才完整可用。

---

## 配置方法

### 方式一：AWS Console（推荐，权限自动配置）

Lambda Console → 函数 → Add trigger → S3：
- 选择 Bucket
- Event type 选 `PUT`（或其他所需类型）
- 可选：设置 Prefix / Suffix 过滤

> Console 会自动在 Lambda 资源策略中添加 S3 的调用权限。

### 方式二：AWS CLI

**第一步：配置 S3 通知**

```bash
aws s3api put-bucket-notification-configuration \
    --bucket your-bucket-name \
    --notification-configuration '{
        "LambdaFunctionConfigurations": [{
            "LambdaFunctionArn": "arn:aws:lambda:us-east-1:123456789:function:your-function",
            "Events": ["s3:ObjectCreated:Put"],
            "Filter": {
                "Key": {
                    "FilterRules": [
                        {"Name": "prefix", "Value": "uploads/"},
                        {"Name": "suffix", "Value": ".json"}
                    ]
                }
            }
        }]
    }'
```

**第二步：手动添加 Lambda 资源策略**（CLI 方式不会自动添加）

```bash
aws lambda add-permission \
    --function-name your-function \
    --statement-id s3-trigger-permission \
    --action lambda:InvokeFunction \
    --principal s3.amazonaws.com \
    --source-arn arn:aws:s3:::your-bucket-name \
    --source-account 123456789012
```

> `--source-account` 建议加上，防止 confused deputy 攻击（其他账户的 bucket 伪造触发）。

---

## Event 结构（完整）

Lambda 收到的 `event` 参数结构（官方完整示例）：

```json
{
  "Records": [
    {
      "eventVersion": "2.1",
      "eventSource": "aws:s3",
      "awsRegion": "us-east-1",
      "eventTime": "2026-04-15T08:00:00.000Z",
      "eventName": "ObjectCreated:Put",
      "userIdentity": {
        "principalId": "AIDAJDPLRKLG7UEXAMPLE"
      },
      "requestParameters": {
        "sourceIPAddress": "203.0.113.1"
      },
      "responseElements": {
        "x-amz-request-id": "C3D13FE58DE4C810",
        "x-amz-id-2": "FMyUVURIY8/IgAtTv8xRjskZQpcIZ9KG4V5Wp6S7S/JRWeUWerMUE5JgHvANOjpD"
      },
      "s3": {
        "s3SchemaVersion": "1.0",
        "configurationId": "my-trigger-config",
        "bucket": {
          "name": "your-bucket-name",
          "ownerIdentity": {
            "principalId": "A3NL1KOZZKExample"
          },
          "arn": "arn:aws:s3:::your-bucket-name"
        },
        "object": {
          "key": "uploads/data.json",
          "size": 2048,
          "eTag": "d41d8cd98f00b204e9800998ecf8427e",
          "versionId": "096fKKXTRTtl3on89fVO.nfljtsv6qko",
          "sequencer": "0055AED6DCD90281E5"
        }
      }
    }
  ]
}
```

### 关键字段说明

| 字段 | 说明 |
|------|------|
| `Records` | 事件记录数组（见下方说明） |
| `eventName` | 事件类型，**不含** `s3:` 前缀（如 `ObjectCreated:Put`） |
| `eventTime` | 事件发生时间（ISO 8601 UTC） |
| `userIdentity.principalId` | 触发操作的 IAM 主体 ID |
| `requestParameters.sourceIPAddress` | 发起上传的 IP 地址 |
| `responseElements` | 请求 ID，用于追踪和排查问题 |
| `s3.object.key` | 对象 Key（URL 编码，空格为 `+`，需 `urllib.parse.unquote_plus` 解码） |
| `s3.object.size` | 对象大小（字节）。**删除事件无此字段** |
| `s3.object.eTag` | 对象 ETag（MD5 或分片上传的复合哈希） |
| `s3.object.versionId` | 版本 ID，仅在 Bucket 开启版本控制时存在 |
| `s3.object.sequencer` | 保证同一 Key 的事件顺序，16 进制字符串 |

> **Key 解码**：S3 event 中 key 是 URL 编码的，含空格的文件名会变成 `+`。务必用 `urllib.parse.unquote_plus(key)` 解码：
> ```python
> from urllib.parse import unquote_plus
> key = unquote_plus(record['s3']['object']['key'])
> ```

---

## 多文件同时上传的行为

**结论：每个文件独立触发一次 Lambda，不合并。**

```
同时上传 file-a.json、file-b.json、file-c.json
    ↓
Lambda 调用 #1：event.Records = [{ key: "file-a.json" }]
Lambda 调用 #2：event.Records = [{ key: "file-b.json" }]
Lambda 调用 #3：event.Records = [{ key: "file-c.json" }]
```

虽然 `Records` 是数组，理论上可包含多条，但**实践中 S3 直接触发 Lambda 几乎总是 1 条**。使用 SQS 作为中间层时，SQS → Lambda 的事件可能包含多条（batch size 配置）。

**编写代码时永远遍历 Records 数组**，不要硬取 `[0]`：

```python
def lambda_handler(event, context):
    for record in event['Records']:
        process(record)
```

### 如果需要等所有文件到齐再处理

纯 S3 触发无法实现。需要额外机制：

| 方案 | 说明 |
|------|------|
| **SQS + batch window** | S3 → SQS → Lambda，配置 `MaximumBatchingWindowInSeconds` 攒批 |
| **DynamoDB 计数器** | 每个文件触发后写入 DynamoDB，计数满后触发处理 |
| **Step Functions** | 协调多文件等待逻辑 |
| **S3 Event Notifications + SNS 扇出** | 先发 SNS，再路由到处理逻辑 |

---

## 权限配置

### Lambda 执行角色需要的权限

```json
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject"
  ],
  "Resource": "arn:aws:s3:::your-bucket-name/*"
}
```

> 如果 Lambda 只需要处理 event 中的元信息（bucket/key），不需要读取文件内容，则**不需要** `s3:GetObject`。

### S3 调用 Lambda 的权限

Lambda 资源策略（由 Console 自动添加，CLI 需手动）：

```json
{
  "Effect": "Allow",
  "Principal": {"Service": "s3.amazonaws.com"},
  "Action": "lambda:InvokeFunction",
  "Resource": "arn:aws:lambda:us-east-1:123456789:function:your-function",
  "Condition": {
    "ArnLike": {
      "AWS:SourceArn": "arn:aws:s3:::your-bucket-name"
    },
    "StringEquals": {
      "AWS:SourceAccount": "123456789012"
    }
  }
}
```

---

## 错误处理与重试

S3 → Lambda 是**异步调用**，失败行为如下：

```
Lambda 执行失败
    ↓ 等待约 1 分钟
第一次重试
    ↓ 仍然失败，等待约 2 分钟
第二次重试
    ↓ 仍然失败
事件被丢弃（或发送到 DLQ / 失败目标）
```

> 默认最多重试 **2 次**，事件最长保留 **6 小时**，之后丢弃。

### 配置 DLQ（死信队列）

```bash
# 失败事件发送到 SQS DLQ
aws lambda put-function-event-invoke-config \
    --function-name your-function \
    --maximum-retry-attempts 1 \
    --maximum-event-age-in-seconds 3600 \
    --destination-config '{
        "OnFailure": {
            "Destination": "arn:aws:sqs:us-east-1:123456789:your-dlq"
        }
    }'
```

### S3 不重试失败的 Lambda 调用

注意：S3 本身**不感知** Lambda 是否成功，重试逻辑由 Lambda 异步调用框架负责，不是 S3 重发事件。

---

## 常见陷阱

### 1. 循环触发

Lambda 写入触发它的同一个 Bucket → 新文件再次触发 Lambda → 无限循环。

**解决方案**：
- 输入/输出分别用不同的 Bucket
- 或配置 Prefix 过滤，确保 Lambda 输出的 Key 前缀不匹配触发规则

### 2. CLI 配置后权限未更新

用 CLI 配置 S3 通知后，Lambda 资源策略不会自动更新，导致 S3 无权调用 Lambda。需手动执行 `aws lambda add-permission`（见[[#配置方法]]）。

### 3. Key 中含特殊字符未解码

S3 event 中的 key 是 URL 编码的，直接使用会导致 GetObject 报 NoSuchKey。

```python
# 错误
key = event['Records'][0]['s3']['object']['key']

# 正确
from urllib.parse import unquote_plus
key = unquote_plus(event['Records'][0]['s3']['object']['key'])
```

### 4. 跨 Region 配置

S3 bucket 和 Lambda 必须在同一个 Region，不支持跨 Region 直接触发。跨 Region 场景需要用 S3 跨区域复制（CRR）+ 目标 Region 的 Lambda。

### 5. 同一函数被多个 Bucket 触发

事件中有 `s3.bucket.name`，handler 内应做 bucket 判断，避免误处理来自其他 bucket 的事件（多 trigger 配置时）。

---

## 进阶方案

### 通过 EventBridge（更灵活）

```bash
# 开启 S3 → EventBridge 通知
aws s3api put-bucket-notification-configuration \
    --bucket your-bucket \
    --notification-configuration '{"EventBridgeConfiguration": {}}'
```

EventBridge 的优势：
- **多目标**：一个事件可同时路由到多个 Lambda / SQS / SNS
- **更强过滤**：支持对象 Key、size、tag、metadata 等内容过滤
- **Archive/Replay**：可回放历史事件
- **跨账户**：支持跨账户事件路由

### 通过 SQS 解耦（增加可靠性）

```
S3 PutObject → SQS 队列 → Lambda（批量拉取）
```

优势：
- Lambda 失败时事件保留在 SQS，自动重试
- 支持 batch size，多条事件一次处理
- 支持 Dead Letter Queue（超出重试次数后移到 DLQ）
- 削峰填谷，控制 Lambda 并发

---

## Lambda 代码示例

### 基础：转发 event 到自定义 endpoint

```python
import json
import urllib.request
from urllib.parse import unquote_plus

ENDPOINT_URL = "https://your-custom-endpoint.com/webhook"

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        size = record['s3'].get('object', {}).get('size', 0)
        event_name = record['eventName']

        payload = {
            "bucket": bucket,
            "key": key,
            "size": size,
            "event": event_name,
            "raw": record  # 转发完整 record
        }

        body = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url=ENDPOINT_URL,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"Forwarded {key} → {response.status}")

    return {"statusCode": 200}
```

### 进阶：读取文件内容后转发

```python
import json
import boto3
import urllib.request
from urllib.parse import unquote_plus

s3_client = boto3.client('s3')  # handler 外初始化，热启动复用
ENDPOINT_URL = "https://your-custom-endpoint.com/ingest"

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])

        # 读取文件内容
        response = s3_client.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')

        payload = {
            "bucket": bucket,
            "key": key,
            "content": content
        }

        body = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url=ENDPOINT_URL,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"Sent {key} ({len(content)} bytes) → {resp.status}")
```

### 幂等处理（防止重复调用）

```python
import boto3
import hashlib
import time

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('lambda-idempotency')

def lambda_handler(event, context):
    for record in event['Records']:
        # 用 sequencer 作为幂等 key（S3 保证同一对象的 sequencer 唯一递增）
        sequencer = record['s3']['object']['sequencer']
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        idempotency_key = f"{bucket}/{key}/{sequencer}"

        try:
            table.put_item(
                Item={
                    'id': idempotency_key,
                    'ttl': int(time.time()) + 86400  # 24 小时后 DynamoDB TTL 自动删除
                },
                ConditionExpression='attribute_not_exists(id)'
            )
        except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            print(f"Skipping duplicate event: {idempotency_key}")
            continue

        process(bucket, key)
```

---

*最后更新：2026-04-15*
