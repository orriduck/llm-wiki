# AWS CloudTrail

> AWS API call audit logging service that records who did what to which resource and when.
> Core infrastructure for security and compliance.
> Events can be delivered to [[CloudWatch]] Logs for real-time alerting.
> Events can be routed to [[EventBridge]] to trigger automated responses.
> [[Lambda]] invocations and configuration changes also generate CloudTrail events.

> AWS API 调用的审计日志服务，记录谁在什么时间对哪个资源做了什么操作。
> 安全合规的核心基础设施。
> 事件可投递到 [[CloudWatch]] Logs 进行实时告警。
> 事件可路由到 [[EventBridge]] 触发自动化响应。
> 对 [[Lambda]] 调用和配置变更也会产生 CloudTrail 事件。

## Table of Contents / 目录

- [[#Core Concepts / 核心概念]]
- [[#Event Types / 事件类型]]
- [[#Trail Configuration / Trail 配置]]
- [[#CloudTrail Lake]]
- [[#Event Structure / 事件结构]]
- [[#Common Security Investigation Queries / 安全调查常用查询]]
- [[#EventBridge Integration / 与 EventBridge 集成]]
- [[#CloudWatch Integration / 与 CloudWatch 集成]]
- [[#Organization Trail / 组织级 Trail]]
- [[#Security Best Practices / 安全最佳实践]]
- [[#Cost Optimization / 成本优化]]
- [[#CLI Quick Reference / CLI 速查]]

---

## Core Concepts / 核心概念

| Concept / 概念 | Description / 说明 |
|------|------|
| **Event** | A record of one AWS API call / 一次 AWS API 调用的记录 |
| **Trail** | Configuration for which events are recorded and where they are stored / 配置哪些事件被记录、存储到哪里 |
| **Event History** | Default 90-day retention of management events (free, no Trail needed) / 默认保留 90 天的管理事件（免费，无需创建 Trail） |
| **CloudTrail Lake** | Managed event data lake with SQL query support (replaces Athena) / 托管的事件数据湖，支持 SQL 查询（替代 Athena） |
| **Insights** | Automatic detection of abnormal API call volume spikes / 自动检测 API 调用量的异常波动 |

---

## Event Types / 事件类型

| Type / 类型 | Description / 说明 | Example / 示例 | Recorded by Default / 默认记录 |
|------|------|------|---------|
| **Management Events** | Control plane operations (create/modify/delete resources) / 控制面操作（资源的创建/修改/删除） | CreateBucket, RunInstances, PutRolePolicy | Yes (free 90 days) / 是（免费 90 天） |
| **Data Events** | Data plane operations (read/write resource contents) / 数据面操作（资源内容的读写） | S3 GetObject/PutObject, Lambda Invoke, DynamoDB GetItem | No (must enable, charged) / 否（需开启，收费） |
| **Insights Events** | API call volume anomaly detection / API 调用量异常检测 | Abnormal spike in RunInstances calls / 短时间内 RunInstances 调用量异常飙升 | No (must enable) / 否（需开启） |
| **Network Activity Events** | VPC Endpoint network activity / VPC Endpoint 的网络活动 | Accessing S3 via VPC Endpoint / 通过 VPC Endpoint 访问 S3 | No (must enable) / 否（需开启） |

### Read/Write Classification / 读写分类

Each event type can be further classified as:

> 每种事件可进一步分为：

- **Read**: Operations that don't modify resources (Describe, Get, List) / 不修改资源的操作
- **Write**: Operations that modify resources (Create, Delete, Put, Update) / 修改资源的操作

**Cost tip**: In Data Events, S3 GetObject is typically the largest log volume source. Only enable when security requirements are high.

> **成本提示**：Data Events 中，S3 GetObject 通常是最大的日志量来源。仅在安全要求高时开启。

---

## Trail Configuration / Trail 配置

### Create Trail / 创建 Trail

```bash
# Basic Trail: management events → S3
# 基本 Trail：管理事件 → S3
aws cloudtrail create-trail \
    --name my-audit-trail \
    --s3-bucket-name my-cloudtrail-logs \
    --s3-key-prefix audit \
    --is-multi-region-trail \
    --enable-log-file-validation

# Start logging / 启动日志记录
aws cloudtrail start-logging --name my-audit-trail
```

### Enable Data Events / 开启 Data Events

```bash
# Record all S3 data events / 记录所有 S3 数据事件
aws cloudtrail put-event-selectors \
    --trail-name my-audit-trail \
    --event-selectors '[{
        "ReadWriteType": "All",
        "IncludeManagementEvents": true,
        "DataResources": [{
            "Type": "AWS::S3::Object",
            "Values": ["arn:aws:s3:::my-sensitive-bucket/"]
        }]
    }]'

# Record Lambda invocation events / 记录 Lambda 调用事件
aws cloudtrail put-event-selectors \
    --trail-name my-audit-trail \
    --event-selectors '[{
        "ReadWriteType": "All",
        "IncludeManagementEvents": true,
        "DataResources": [{
            "Type": "AWS::Lambda::Function",
            "Values": ["arn:aws:lambda:us-east-1:<account-id>:function:my-function"]
        }]
    }]'
```

### Advanced Event Selectors (finer control) / 高级事件选择器（更精细控制）

```bash
aws cloudtrail put-event-selectors \
    --trail-name my-audit-trail \
    --advanced-event-selectors '[{
        "Name": "S3WriteOnly",
        "FieldSelectors": [
            {"Field": "eventCategory", "Equals": ["Data"]},
            {"Field": "resources.type", "Equals": ["AWS::S3::Object"]},
            {"Field": "readOnly", "Equals": ["false"]},
            {"Field": "resources.ARN", "StartsWith": ["arn:aws:s3:::my-bucket/"]}
        ]
    }]'
```

### S3 Bucket Policy

CloudTrail needs write permission to S3.

> CloudTrail 需要写入 S3 的权限。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AWSCloudTrailAclCheck",
      "Effect": "Allow",
      "Principal": {"Service": "cloudtrail.amazonaws.com"},
      "Action": "s3:GetBucketAcl",
      "Resource": "arn:aws:s3:::my-cloudtrail-logs"
    },
    {
      "Sid": "AWSCloudTrailWrite",
      "Effect": "Allow",
      "Principal": {"Service": "cloudtrail.amazonaws.com"},
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::my-cloudtrail-logs/audit/AWSLogs/<account-id>/*",
      "Condition": {
        "StringEquals": {"s3:x-amz-acl": "bucket-owner-full-control"}
      }
    }
  ]
}
```

---

## CloudTrail Lake

Managed event query service with SQL support; no need to configure Athena + Glue.

> 托管的事件查询服务，支持 SQL，无需配置 Athena + Glue。

### Create Event Data Store / 创建 Event Data Store

```bash
aws cloudtrail create-event-data-store \
    --name my-audit-lake \
    --retention-period 365 \
    --advanced-event-selectors '[{
        "Name": "AllManagementEvents",
        "FieldSelectors": [
            {"Field": "eventCategory", "Equals": ["Management"]}
        ]
    }]'
```

### SQL Queries / SQL 查询

```sql
-- IAM changes in last 24 hours / 最近 24 小时的 IAM 变更
SELECT eventTime, userIdentity.arn, eventName, requestParameters
FROM <event-data-store-id>
WHERE eventSource = 'iam.amazonaws.com'
  AND eventTime > '2026-04-12T00:00:00Z'
ORDER BY eventTime DESC

-- All operations by a specific user / 特定用户的所有操作
SELECT eventTime, eventSource, eventName, sourceIPAddress
FROM <event-data-store-id>
WHERE userIdentity.arn = 'arn:aws:iam::<account-id>:user/alice'
  AND eventTime > '2026-04-01T00:00:00Z'

-- Console login failures / 控制台登录失败
SELECT eventTime, userIdentity.arn, sourceIPAddress, errorMessage
FROM <event-data-store-id>
WHERE eventName = 'ConsoleLogin'
  AND responseElements.ConsoleLogin = 'Failure'

-- Security group changes / 安全组变更
SELECT eventTime, userIdentity.arn, eventName, requestParameters
FROM <event-data-store-id>
WHERE eventName IN ('AuthorizeSecurityGroupIngress', 'AuthorizeSecurityGroupEgress',
                     'RevokeSecurityGroupIngress', 'RevokeSecurityGroupEgress')
```

```bash
# CLI query
QUERY_ID=$(aws cloudtrail start-query \
    --query-statement "SELECT eventTime, eventName FROM <eds-id> WHERE eventSource='s3.amazonaws.com' LIMIT 10" \
    --query 'QueryId' --output text)

aws cloudtrail get-query-results --query-id $QUERY_ID
```

---

## Event Structure / 事件结构

```json
{
  "eventVersion": "1.09",
  "userIdentity": {
    "type": "AssumedRole",
    "principalId": "AROA...:session-name",
    "arn": "arn:aws:sts::<account-id>:assumed-role/admin-role/alice",
    "accountId": "<account-id>",
    "sessionContext": {
      "sessionIssuer": {
        "type": "Role",
        "arn": "arn:aws:iam::<account-id>:role/admin-role"
      }
    }
  },
  "eventTime": "2026-04-13T10:30:00Z",
  "eventSource": "s3.amazonaws.com",
  "eventName": "PutObject",
  "awsRegion": "us-east-1",
  "sourceIPAddress": "203.0.113.50",
  "userAgent": "aws-sdk-python/1.26.0",
  "requestParameters": {
    "bucketName": "my-bucket",
    "key": "data/file.csv"
  },
  "responseElements": null,
  "requestID": "abc123",
  "eventID": "def456",
  "readOnly": false,
  "resources": [{
    "type": "AWS::S3::Object",
    "ARN": "arn:aws:s3:::my-bucket/data/file.csv"
  }],
  "eventType": "AwsApiCall",
  "recipientAccountId": "<account-id>"
}
```

### Key Fields Quick Reference / 关键字段速查

| Field / 字段 | Description / 说明 | Security Investigation Use / 安全调查用途 |
|------|------|------------|
| `userIdentity` | Who (IAM User/Role/Service) / 谁 | Identify operator / 识别操作者 |
| `sourceIPAddress` | Source IP / 来源 IP | Detect abnormal sources / 检测异常来源 |
| `eventName` | What operation / 什么操作 | Identify sensitive operations / 识别敏感操作 |
| `eventSource` | Which AWS service / 哪个 AWS 服务 | Narrow scope / 缩小范围 |
| `requestParameters` | Request parameters / 请求参数 | Operation details / 操作细节 |
| `responseElements` | Response content (write operations only) / 响应内容（仅写操作） | Change results / 变更结果 |
| `errorCode` | Error code (if failed) / 错误码（如果失败） | Detect permission probing / 检测权限探测 |
| `userAgent` | Calling tool / 调用工具 | Detect abnormal clients / 检测异常客户端 |

---

## Common Security Investigation Queries / 安全调查常用查询

### Using Event History (quick, within 90 days) / 使用 Event History（快速，90 天内）

```bash
# Who deleted a specific S3 Bucket? / 谁删除了某个 S3 Bucket？
aws cloudtrail lookup-events \
    --lookup-attributes AttributeKey=EventName,AttributeValue=DeleteBucket \
    --start-time "2026-04-01T00:00:00Z"

# Recent operations by a specific user / 特定用户的近期操作
aws cloudtrail lookup-events \
    --lookup-attributes AttributeKey=Username,AttributeValue=alice \
    --max-results 50

# Operations from a specific resource type / 来自特定资源类型的操作
aws cloudtrail lookup-events \
    --lookup-attributes AttributeKey=ResourceType,AttributeValue=AWS::IAM::Role
```

### Using Athena (long-term archive queries) / 使用 Athena（长期归档查询）

```sql
-- Create CloudTrail table in Athena / 在 Athena 中创建 CloudTrail 表
CREATE EXTERNAL TABLE cloudtrail_logs (
    eventversion STRING,
    useridentity STRUCT<type:STRING, arn:STRING, accountid:STRING, ...>,
    eventtime STRING,
    eventsource STRING,
    eventname STRING,
    sourceipaddress STRING,
    ...
)
ROW FORMAT SERDE 'org.apache.hive.hcatalog.data.JsonSerDe'
LOCATION 's3://my-cloudtrail-logs/audit/AWSLogs/<account-id>/CloudTrail/';

-- Find Root account usage / 查找 Root 账户使用
SELECT eventtime, eventname, sourceipaddress, useragent
FROM cloudtrail_logs
WHERE useridentity.type = 'Root'
  AND year = '2026' AND month = '04';

-- Unauthorized access attempts / 未授权访问尝试
SELECT eventtime, useridentity.arn, eventname, errormessage, sourceipaddress
FROM cloudtrail_logs
WHERE errorcode IN ('AccessDenied', 'UnauthorizedAccess', 'Client.UnauthorizedAccess')
ORDER BY eventtime DESC
LIMIT 100;
```

---

## EventBridge Integration / 与 EventBridge 集成

CloudTrail management events are automatically sent to the EventBridge default bus.

> CloudTrail 管理事件自动发送到 EventBridge default bus。

```bash
# Trigger Lambda when someone modifies a security group
# 当有人修改安全组时触发 Lambda
aws events put-rule \
    --name "sg-change-alert" \
    --event-pattern '{
        "source": ["aws.ec2"],
        "detail-type": ["AWS API Call via CloudTrail"],
        "detail": {
            "eventSource": ["ec2.amazonaws.com"],
            "eventName": [
                "AuthorizeSecurityGroupIngress",
                "AuthorizeSecurityGroupEgress",
                "RevokeSecurityGroupIngress"
            ]
        }
    }'

aws events put-targets --rule "sg-change-alert" \
    --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:<account-id>:function:sg-alert"
```

```bash
# IAM policy change alert / IAM 策略变更告警
aws events put-rule \
    --name "iam-policy-change" \
    --event-pattern '{
        "source": ["aws.iam"],
        "detail-type": ["AWS API Call via CloudTrail"],
        "detail": {
            "eventName": [
                "CreatePolicy", "DeletePolicy",
                "AttachRolePolicy", "DetachRolePolicy",
                "PutRolePolicy", "DeleteRolePolicy"
            ]
        }
    }'
```

### Common Security Rules / 常见安全规则

| Scenario / 场景 | eventSource | eventName |
|------|------------|-----------|
| Security group changes / 安全组变更 | ec2.amazonaws.com | Authorize/RevokeSecurityGroup* |
| IAM policy changes / IAM 策略变更 | iam.amazonaws.com | *Policy, *Role |
| Root login / Root 登录 | signin.amazonaws.com | ConsoleLogin (userIdentity.type=Root) |
| S3 Bucket made public / S3 Bucket 公开 | s3.amazonaws.com | PutBucketPolicy, PutBucketAcl |
| KMS key operations / KMS 密钥操作 | kms.amazonaws.com | DisableKey, ScheduleKeyDeletion |
| VPC changes / VPC 变更 | ec2.amazonaws.com | Create/DeleteVpc, *RouteTable* |
| CloudTrail stopped / CloudTrail 停止 | cloudtrail.amazonaws.com | StopLogging, DeleteTrail |

---

## CloudWatch Integration / 与 CloudWatch 集成

### Deliver CloudTrail Logs to CloudWatch Logs / 将 CloudTrail 日志发送到 CloudWatch Logs

```bash
aws cloudtrail update-trail \
    --name my-audit-trail \
    --cloud-watch-logs-log-group-arn "arn:aws:logs:us-east-1:<account-id>:log-group:CloudTrail/audit:*" \
    --cloud-watch-logs-role-arn "arn:aws:iam::<account-id>:role/CloudTrail-CWLogs-Role"
```

### CloudWatch Metric Filter + Alarm

```bash
# Root account usage alert / Root 账户使用告警
aws logs put-metric-filter \
    --log-group-name CloudTrail/audit \
    --filter-name "RootAccountUsage" \
    --filter-pattern '{$.userIdentity.type = "Root" && $.userIdentity.invokedBy NOT EXISTS && $.eventType != "AwsServiceEvent"}' \
    --metric-transformations \
        metricName=RootAccountUsage,metricNamespace=CloudTrailMetrics,metricValue=1

aws cloudwatch put-metric-alarm \
    --alarm-name "root-account-usage" \
    --metric-name RootAccountUsage \
    --namespace CloudTrailMetrics \
    --statistic Sum \
    --period 300 \
    --threshold 1 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --evaluation-periods 1 \
    --alarm-actions arn:aws:sns:us-east-1:<account-id>:security-alerts

# Unauthorized API calls alert / 未授权 API 调用告警
aws logs put-metric-filter \
    --log-group-name CloudTrail/audit \
    --filter-name "UnauthorizedAPICalls" \
    --filter-pattern '{($.errorCode = "*UnauthorizedAccess*") || ($.errorCode = "AccessDenied*")}' \
    --metric-transformations \
        metricName=UnauthorizedAPICalls,metricNamespace=CloudTrailMetrics,metricValue=1
```

---

## Organization Trail / 组织级 Trail

### AWS Organizations Centralized Audit / AWS Organizations 集中审计

```bash
# Create organization-level Trail in management account
# 在管理账户创建组织级 Trail
aws cloudtrail create-trail \
    --name org-audit-trail \
    --s3-bucket-name org-cloudtrail-logs \
    --is-multi-region-trail \
    --is-organization-trail \
    --enable-log-file-validation

aws cloudtrail start-logging --name org-audit-trail
```

### Log Storage Structure / 日志存储结构

```
s3://org-cloudtrail-logs/
  └── AWSLogs/
        └── o-orgid/
              ├── <account-id-a>/  (Account A / 账户 A)
              │     └── CloudTrail/
              │           └── us-east-1/
              │                 └── 2026/04/13/
              ├── <account-id-b>/  (Account B / 账户 B)
              └── <account-id-c>/  (Account C / 账户 C)
```

---

## Security Best Practices / 安全最佳实践

1. **Enable Trail in all regions / 所有区域开启 Trail**: `--is-multi-region-trail`
2. **Enable log file validation / 开启日志文件验证**: `--enable-log-file-validation` (detect log tampering / 检测日志被篡改)
3. **Encrypt S3 Bucket / S3 Bucket 加密**: SSE-S3 or SSE-KMS
4. **Restrict S3 Bucket access / S3 Bucket 访问限制**: Only CloudTrail service and security team can access / 仅 CloudTrail 服务和安全团队可访问
5. **Enable CloudTrail Insights / 开启 CloudTrail Insights**: Automatic API call volume anomaly detection / 自动检测 API 调用量异常
6. **Deliver to CloudWatch Logs / 投递到 CloudWatch Logs**: Enable real-time alerting / 实现实时告警
7. **Cross-account centralized storage / 跨账户集中存储**: Use Organizations Trail or cross-account S3 / 用 Organizations Trail 或跨账户 S3
8. **Monitor CloudTrail itself / 监控 CloudTrail 本身**: Detect StopLogging, DeleteTrail events / 检测 StopLogging、DeleteTrail 事件
9. **Don't rely solely on Event History / 不要只依赖 Event History**: Data disappears after 90 days; must have a Trail for persistence / 90 天后数据消失，必须有 Trail 持久化

### Enable Insights / 开启 Insights

```bash
aws cloudtrail put-insight-selectors \
    --trail-name my-audit-trail \
    --insight-selectors '[
        {"InsightType": "ApiCallRateInsight"},
        {"InsightType": "ApiErrorRateInsight"}
    ]'
```

---

## Cost Optimization / 成本优化

| Item / 项目 | Free / 免费 | Charged / 收费 |
|------|------|------|
| Management Events (first Trail) / 管理事件（第一份 Trail） | Free / 免费 | Additional Trail $2.00/100K events / 额外 Trail $2.00/10 万事件 |
| Data Events / 数据事件 | -- | $0.10/100K events / $0.10/10 万事件 |
| Insights Events / Insights 事件 | -- | $0.35/100K events analyzed / $0.35/10 万事件分析 |
| CloudTrail Lake ingestion / CloudTrail Lake 摄入 | -- | $2.50/GB |
| CloudTrail Lake query / CloudTrail Lake 查询 | -- | $0.005/GB scanned / 扫描 |
| S3 storage / S3 存储 | -- | Standard S3 rates / 标准 S3 费率 |

### Optimization Strategies / 优化策略

1. **Only create one Trail / 只开一份 Trail**: Multiple Trails incur duplicate charges / 多份 Trail 重复收费
2. **Enable Data Events selectively / Data Events 按需开启**: Only monitor sensitive Buckets/functions / 只监控敏感 Bucket/函数
3. **Use S3 Lifecycle for log management / 用 S3 Lifecycle 管理日志**: 30 days → IA, 90 days → Glacier
4. **CloudTrail Lake vs Athena**: Small query volume use Lake, large-scale analysis use Athena + S3 / 小查询量用 Lake，大规模分析用 Athena + S3
5. **Exclude high-frequency low-risk Read events / 排除高频无风险的 Read 事件**: e.g. if you don't need to audit DescribeInstances

---

## CLI Quick Reference / CLI 速查

```bash
# Trail management / Trail 管理
aws cloudtrail describe-trails
aws cloudtrail get-trail-status --name TRAIL
aws cloudtrail start-logging --name TRAIL
aws cloudtrail stop-logging --name TRAIL

# Event query (within 90 days) / 事件查询（90 天内）
aws cloudtrail lookup-events \
    --lookup-attributes AttributeKey=EventName,AttributeValue=RunInstances
aws cloudtrail lookup-events \
    --lookup-attributes AttributeKey=Username,AttributeValue=alice

# Insights
aws cloudtrail put-insight-selectors --trail-name TRAIL \
    --insight-selectors '[{"InsightType":"ApiCallRateInsight"}]'

# CloudTrail Lake
aws cloudtrail list-event-data-stores
aws cloudtrail start-query --query-statement "SELECT ..."
aws cloudtrail get-query-results --query-id ID

# Log validation / 日志验证
aws cloudtrail validate-logs \
    --trail-arn arn:aws:cloudtrail:us-east-1:<account-id>:trail/TRAIL \
    --start-time "2026-04-01T00:00:00Z"
```

---

*Last updated / 最后更新：2026-04-13*
