# S3 → Lambda Trigger / S3 → Lambda 触发器

> S3 object create/delete events can directly trigger [[Lambda]] function execution, one of the most common serverless event processing patterns.
> Related pages: [[S3#事件通知]], [[Lambda#触发方式]], [[EventBridge]]

> S3 对象创建/删除等事件可直接触发 [[Lambda]] 函数执行，是最常见的无服务器事件处理模式之一。
> 相关页面：[[S3#事件通知]]、[[Lambda#触发方式]]、[[EventBridge]]

## Table of Contents / 目录

- [[#Core Mechanism / 核心机制]]
- [[#Supported Event Types / 支持的事件类型]]
- [[#Configuration Methods / 配置方法]]
- [[#Event Structure (Complete) / Event 结构（完整）]]
- [[#Multi-file Upload Behavior / 多文件同时上传的行为]]
- [[#Permission Configuration / 权限配置]]
- [[#Error Handling & Retries / 错误处理与重试]]
- [[#Common Pitfalls / 常见陷阱]]
- [[#Advanced Approaches / 进阶方案]]
- [[#Lambda Code Examples / Lambda 代码示例]]

---

## Core Mechanism / 核心机制

S3 event notifications use an **asynchronous push** model.

> S3 事件通知采用**异步推送**模式。

```
S3 PutObject
    ↓ Event notification (async) / 事件通知（异步）
Lambda invoked (Event invocation type) / Lambda 被调用（Event 调用类型）
    ↓
Lambda executes handler, event parameter contains S3 event info
Lambda 执行 handler，event 参数包含 S3 事件信息
```

- S3 event notifications are **asynchronous** triggers; Lambda invocation type is `Event` (does not wait for result)
- S3 **does not guarantee** exactly-once delivery (at-least-once semantics); Lambda handlers should be **idempotent**
- Lambda and S3 bucket must be in the **same Region**

> - S3 事件通知是**异步**触发，Lambda 调用类型为 `Event`（不等待结果）
> - S3 **不保证**只调用一次（at-least-once 语义），Lambda handler 应设计为**幂等**
> - Lambda 与 S3 bucket 必须在**同一个 Region**

---

## Supported Event Types / 支持的事件类型

| Event Type / 事件类型 | Description / 说明 |
|---------|------|
| `s3:ObjectCreated:*` | All object creation events (wildcard) / 所有对象创建事件（通配） |
| `s3:ObjectCreated:Put` | Standard PUT upload / 普通 PUT 上传 |
| `s3:ObjectCreated:Post` | HTML form-based POST upload / 基于 HTML 表单的 POST 上传 |
| `s3:ObjectCreated:Copy` | Server-side copy (CopyObject API) / 服务端复制（CopyObject API） |
| `s3:ObjectCreated:CompleteMultipartUpload` | Multipart upload complete / 分片上传完成 |
| `s3:ObjectRemoved:*` | All delete events (wildcard) / 所有删除事件（通配） |
| `s3:ObjectRemoved:Delete` | Permanent delete (without versioning) / 永久删除（无版本控制时） |
| `s3:ObjectRemoved:DeleteMarkerCreated` | Delete marker when versioning is enabled / 版本控制开启时的删除标记 |
| `s3:ObjectRestore:Post` | Glacier object restore initiated / Glacier 对象恢复发起 |
| `s3:ObjectRestore:Completed` | Glacier object restore completed / Glacier 对象恢复完成 |
| `s3:ReducedRedundancyLostObject` | RRS storage class object lost / RRS 存储类别对象丢失 |
| `s3:Replication:*` | Cross-region replication events / 跨区域复制相关事件 |

**Multipart upload trigger timing**: `s3:ObjectCreated:Put` only triggers after a single PUT completes. For multipart uploads, the client must call `CompleteMultipartUpload` before `s3:ObjectCreated:CompleteMultipartUpload` fires, at which point the object is fully available.

> **分片上传触发时机**：`s3:ObjectCreated:Put` 仅在单次 PUT 完成后触发。分片上传需要客户端调用 `CompleteMultipartUpload` 后，才会触发 `s3:ObjectCreated:CompleteMultipartUpload`，这时对象才完整可用。

---

## Configuration Methods / 配置方法

### Method 1: AWS Console (recommended, permissions auto-configured) / 方式一：AWS Console（推荐，权限自动配置）

Lambda Console → Function → Add trigger → S3:

> Lambda Console → 函数 → Add trigger → S3：

- Select Bucket / 选择 Bucket
- Event type: select `PUT` (or other needed types) / Event type 选 `PUT`（或其他所需类型）
- Optional: set Prefix / Suffix filter / 可选：设置 Prefix / Suffix 过滤

Console automatically adds S3 invocation permission to the Lambda resource policy.

> Console 会自动在 Lambda 资源策略中添加 S3 的调用权限。

### Method 2: AWS CLI / 方式二：AWS CLI

**Step 1: Configure S3 notification / 第一步：配置 S3 通知**

```bash
aws s3api put-bucket-notification-configuration \
    --bucket your-bucket-name \
    --notification-configuration '{
        "LambdaFunctionConfigurations": [{
            "LambdaFunctionArn": "arn:aws:lambda:us-east-1:<account-id>:function:your-function",
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

**Step 2: Manually add Lambda resource policy / 第二步：手动添加 Lambda 资源策略** (CLI does not auto-add / CLI 方式不会自动添加)

```bash
aws lambda add-permission \
    --function-name your-function \
    --statement-id s3-trigger-permission \
    --action lambda:InvokeFunction \
    --principal s3.amazonaws.com \
    --source-arn arn:aws:s3:::your-bucket-name \
    --source-account <account-id>
```

Adding `--source-account` is recommended to prevent confused deputy attacks (other accounts' buckets spoofing triggers).

> `--source-account` 建议加上，防止 confused deputy 攻击（其他账户的 bucket 伪造触发）。

---

## Event Structure (Complete) / Event 结构（完整）

The `event` parameter received by Lambda (official complete example):

> Lambda 收到的 `event` 参数结构（官方完整示例）：

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

### Key Fields / 关键字段说明

| Field / 字段 | Description / 说明 |
|------|------|
| `Records` | Event record array (see below) / 事件记录数组（见下方说明） |
| `eventName` | Event type, **without** `s3:` prefix (e.g. `ObjectCreated:Put`) / 事件类型，**不含** `s3:` 前缀 |
| `eventTime` | Event timestamp (ISO 8601 UTC) / 事件发生时间（ISO 8601 UTC） |
| `userIdentity.principalId` | IAM principal ID that triggered the operation / 触发操作的 IAM 主体 ID |
| `requestParameters.sourceIPAddress` | IP address that initiated the upload / 发起上传的 IP 地址 |
| `responseElements` | Request ID for tracing and debugging / 请求 ID，用于追踪和排查问题 |
| `s3.object.key` | Object Key (URL-encoded, spaces as `+`, decode with `urllib.parse.unquote_plus`) / 对象 Key（URL 编码，空格为 `+`，需解码） |
| `s3.object.size` | Object size in bytes. **Not present in delete events** / 对象大小（字节）。**删除事件无此字段** |
| `s3.object.eTag` | Object ETag (MD5 or composite hash for multipart) / 对象 ETag |
| `s3.object.versionId` | Version ID, only present when Bucket versioning is enabled / 版本 ID，仅在 Bucket 开启版本控制时存在 |
| `s3.object.sequencer` | Guarantees event order for the same Key, hex string / 保证同一 Key 的事件顺序，16 进制字符串 |

**Key decoding**: The key in S3 events is URL-encoded; filenames with spaces become `+`. Always decode with `urllib.parse.unquote_plus(key)`.

> **Key 解码**：S3 event 中 key 是 URL 编码的，含空格的文件名会变成 `+`。务必用 `urllib.parse.unquote_plus(key)` 解码。

```python
from urllib.parse import unquote_plus
key = unquote_plus(record['s3']['object']['key'])
```

---

## Multi-file Upload Behavior / 多文件同时上传的行为

**Conclusion: Each file independently triggers one Lambda invocation; they are not merged.**

> **结论：每个文件独立触发一次 Lambda，不合并。**

```
Upload file-a.json, file-b.json, file-c.json simultaneously
同时上传 file-a.json、file-b.json、file-c.json
    ↓
Lambda invocation #1: event.Records = [{ key: "file-a.json" }]
Lambda invocation #2: event.Records = [{ key: "file-b.json" }]
Lambda invocation #3: event.Records = [{ key: "file-c.json" }]
```

Although `Records` is an array and can theoretically contain multiple entries, **in practice S3 direct-to-Lambda triggers almost always contain 1 record**. When using SQS as an intermediary, SQS → Lambda events may contain multiple records (batch size configuration).

> 虽然 `Records` 是数组，理论上可包含多条，但**实践中 S3 直接触发 Lambda 几乎总是 1 条**。使用 SQS 作为中间层时，SQS → Lambda 的事件可能包含多条（batch size 配置）。

**Always iterate over the Records array in your code**; never hard-code `[0]`.

> **编写代码时永远遍历 Records 数组**，不要硬取 `[0]`。

```python
def lambda_handler(event, context):
    for record in event['Records']:
        process(record)
```

### If You Need to Wait for All Files Before Processing / 如果需要等所有文件到齐再处理

Pure S3 triggers cannot achieve this. Additional mechanisms are needed:

> 纯 S3 触发无法实现。需要额外机制：

| Approach / 方案 | Description / 说明 |
|------|------|
| **SQS + batch window** | S3 → SQS → Lambda, configure `MaximumBatchingWindowInSeconds` to batch / 配置攒批 |
| **DynamoDB counter** | Each file trigger writes to DynamoDB; trigger processing when count is met / 每个文件触发后写入 DynamoDB，计数满后触发处理 |
| **Step Functions** | Orchestrate multi-file wait logic / 协调多文件等待逻辑 |
| **S3 Event Notifications + SNS fan-out** | Send to SNS first, then route to processing logic / 先发 SNS，再路由到处理逻辑 |

---

## Permission Configuration / 权限配置

### Lambda Execution Role Required Permissions / Lambda 执行角色需要的权限

```json
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject"
  ],
  "Resource": "arn:aws:s3:::your-bucket-name/*"
}
```

If Lambda only needs to process metadata from the event (bucket/key) and doesn't need to read file content, `s3:GetObject` is **not required**.

> 如果 Lambda 只需要处理 event 中的元信息（bucket/key），不需要读取文件内容，则**不需要** `s3:GetObject`。

### S3 Permission to Invoke Lambda / S3 调用 Lambda 的权限

Lambda resource policy (auto-added by Console, manual for CLI):

> Lambda 资源策略（由 Console 自动添加，CLI 需手动）：

```json
{
  "Effect": "Allow",
  "Principal": {"Service": "s3.amazonaws.com"},
  "Action": "lambda:InvokeFunction",
  "Resource": "arn:aws:lambda:us-east-1:<account-id>:function:your-function",
  "Condition": {
    "ArnLike": {
      "AWS:SourceArn": "arn:aws:s3:::your-bucket-name"
    },
    "StringEquals": {
      "AWS:SourceAccount": "<account-id>"
    }
  }
}
```

---

## Error Handling & Retries / 错误处理与重试

S3 → Lambda is an **asynchronous invocation**; failure behavior is as follows:

> S3 → Lambda 是**异步调用**，失败行为如下：

```
Lambda execution fails / Lambda 执行失败
    ↓ wait ~1 min / 等待约 1 分钟
First retry / 第一次重试
    ↓ still fails, wait ~2 min / 仍然失败，等待约 2 分钟
Second retry / 第二次重试
    ↓ still fails / 仍然失败
Event discarded (or sent to DLQ / failure destination)
事件被丢弃（或发送到 DLQ / 失败目标）
```

Default: max **2 retries**, events retained for up to **6 hours** before being discarded.

> 默认最多重试 **2 次**，事件最长保留 **6 小时**，之后丢弃。

### Configure DLQ (Dead Letter Queue) / 配置 DLQ（死信队列）

```bash
# Send failed events to SQS DLQ / 失败事件发送到 SQS DLQ
aws lambda put-function-event-invoke-config \
    --function-name your-function \
    --maximum-retry-attempts 1 \
    --maximum-event-age-in-seconds 3600 \
    --destination-config '{
        "OnFailure": {
            "Destination": "arn:aws:sqs:us-east-1:<account-id>:your-dlq"
        }
    }'
```

### S3 Does Not Retry Failed Lambda Invocations / S3 不重试失败的 Lambda 调用

Note: S3 itself is **unaware** of whether Lambda succeeded. The retry logic is handled by the Lambda async invocation framework, not S3 re-sending events.

> 注意：S3 本身**不感知** Lambda 是否成功，重试逻辑由 Lambda 异步调用框架负责，不是 S3 重发事件。

---

## Common Pitfalls / 常见陷阱

### 1. Recursive Trigger / 循环触发

Lambda writes to the same Bucket that triggered it → new file triggers Lambda again → infinite loop.

> Lambda 写入触发它的同一个 Bucket → 新文件再次触发 Lambda → 无限循环。

**Solution / 解决方案**:
- Use different Buckets for input and output / 输入/输出分别用不同的 Bucket
- Or configure Prefix filters to ensure Lambda output Key prefix doesn't match the trigger rule / 或配置 Prefix 过滤，确保 Lambda 输出的 Key 前缀不匹配触发规则

### 2. Permissions Not Updated After CLI Configuration / CLI 配置后权限未更新

After configuring S3 notifications via CLI, the Lambda resource policy is not automatically updated, preventing S3 from invoking Lambda. You must manually run `aws lambda add-permission` (see [[#Configuration Methods / 配置方法]]).

> 用 CLI 配置 S3 通知后，Lambda 资源策略不会自动更新，导致 S3 无权调用 Lambda。需手动执行 `aws lambda add-permission`（见[[#配置方法]]）。

### 3. Special Characters in Key Not Decoded / Key 中含特殊字符未解码

The key in S3 events is URL-encoded; using it directly causes GetObject to return NoSuchKey.

> S3 event 中的 key 是 URL 编码的，直接使用会导致 GetObject 报 NoSuchKey。

```python
# Wrong / 错误
key = event['Records'][0]['s3']['object']['key']

# Correct / 正确
from urllib.parse import unquote_plus
key = unquote_plus(event['Records'][0]['s3']['object']['key'])
```

### 4. Cross-Region Configuration / 跨 Region 配置

S3 bucket and Lambda must be in the same Region; cross-Region direct triggers are not supported. For cross-Region scenarios, use S3 Cross-Region Replication (CRR) + Lambda in the destination Region.

> S3 bucket 和 Lambda 必须在同一个 Region，不支持跨 Region 直接触发。跨 Region 场景需要用 S3 跨区域复制（CRR）+ 目标 Region 的 Lambda。

### 5. Same Function Triggered by Multiple Buckets / 同一函数被多个 Bucket 触发

The event contains `s3.bucket.name`; the handler should check the bucket to avoid processing events from the wrong bucket (in multi-trigger configurations).

> 事件中有 `s3.bucket.name`，handler 内应做 bucket 判断，避免误处理来自其他 bucket 的事件（多 trigger 配置时）。

---

## Advanced Approaches / 进阶方案

### Via EventBridge (More Flexible) / 通过 EventBridge（更灵活）

```bash
# Enable S3 → EventBridge notifications / 开启 S3 → EventBridge 通知
aws s3api put-bucket-notification-configuration \
    --bucket your-bucket \
    --notification-configuration '{"EventBridgeConfiguration": {}}'
```

EventBridge advantages / EventBridge 的优势:
- **Multiple targets / 多目标**: One event can route to multiple Lambda / SQS / SNS simultaneously / 一个事件可同时路由到多个 Lambda / SQS / SNS
- **Stronger filtering / 更强过滤**: Supports filtering on object Key, size, tag, metadata / 支持对象 Key、size、tag、metadata 等内容过滤
- **Archive/Replay**: Can replay historical events / 可回放历史事件
- **Cross-account / 跨账户**: Supports cross-account event routing / 支持跨账户事件路由

### Via SQS for Decoupling (Increased Reliability) / 通过 SQS 解耦（增加可靠性）

```
S3 PutObject → SQS Queue → Lambda (batch poll / 批量拉取)
```

Advantages / 优势:
- Events retained in SQS when Lambda fails, auto-retry / Lambda 失败时事件保留在 SQS，自动重试
- Supports batch size, process multiple events at once / 支持 batch size，多条事件一次处理
- Supports Dead Letter Queue (move to DLQ after exceeding retries) / 支持 Dead Letter Queue
- Peak smoothing, controls Lambda concurrency / 削峰填谷，控制 Lambda 并发

---

## Lambda Code Examples / Lambda 代码示例

### Basic: Forward Event to Custom Endpoint / 基础：转发 event 到自定义 endpoint

```python
import json
import urllib.request
from urllib.parse import unquote_plus

ENDPOINT_URL = "https://your-custom-endpoint.example.com/webhook"

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
            "raw": record  # Forward complete record / 转发完整 record
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

### Advanced: Read File Content Then Forward / 进阶：读取文件内容后转发

```python
import json
import boto3
import urllib.request
from urllib.parse import unquote_plus

s3_client = boto3.client('s3')  # Init outside handler, reused on warm start / handler 外初始化，热启动复用
ENDPOINT_URL = "https://your-custom-endpoint.example.com/ingest"

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])

        # Read file content / 读取文件内容
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

### Idempotent Processing (Prevent Duplicate Invocations) / 幂等处理（防止重复调用）

```python
import boto3
import hashlib
import time

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('lambda-idempotency')

def lambda_handler(event, context):
    for record in event['Records']:
        # Use sequencer as idempotency key (S3 guarantees unique incrementing sequencer per object)
        # 用 sequencer 作为幂等 key（S3 保证同一对象的 sequencer 唯一递增）
        sequencer = record['s3']['object']['sequencer']
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        idempotency_key = f"{bucket}/{key}/{sequencer}"

        try:
            table.put_item(
                Item={
                    'id': idempotency_key,
                    'ttl': int(time.time()) + 86400  # DynamoDB TTL auto-deletes after 24h / 24 小时后自动删除
                },
                ConditionExpression='attribute_not_exists(id)'
            )
        except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            print(f"Skipping duplicate event: {idempotency_key}")
            continue

        process(bucket, key)
```

---

*Last updated / 最后更新：2026-04-15*
