# AWS CloudTrail

> AWS API 调用的审计日志服务，记录谁在什么时间对哪个资源做了什么操作。
> 安全合规的核心基础设施。
> 事件可投递到 [[CloudWatch]] Logs 进行实时告警。
> 事件可路由到 [[EventBridge]] 触发自动化响应。
> 对 [[Lambda]] 调用和配置变更也会产生 CloudTrail 事件。

## 目录

- [[#核心概念]]
- [[#事件类型]]
- [[#Trail 配置]]
- [[#CloudTrail Lake]]
- [[#事件结构]]
- [[#安全调查常用查询]]
- [[#与 EventBridge 集成]]
- [[#与 CloudWatch 集成]]
- [[#组织级 Trail]]
- [[#安全最佳实践]]
- [[#成本优化]]
- [[#CLI 速查]]

---

## 核心概念

| 概念 | 说明 |
|------|------|
| **Event** | 一次 AWS API 调用的记录 |
| **Trail** | 配置哪些事件被记录、存储到哪里 |
| **Event History** | 默认保留 90 天的管理事件（免费，无需创建 Trail） |
| **CloudTrail Lake** | 托管的事件数据湖，支持 SQL 查询（替代 Athena） |
| **Insights** | 自动检测 API 调用量的异常波动 |

---

## 事件类型

| 类型 | 说明 | 示例 | 默认记录 |
|------|------|------|---------|
| **Management Events** | 控制面操作（资源的创建/修改/删除） | CreateBucket、RunInstances、PutRolePolicy | 是（免费 90 天） |
| **Data Events** | 数据面操作（资源内容的读写） | S3 GetObject/PutObject、Lambda Invoke、DynamoDB GetItem | 否（需开启，收费） |
| **Insights Events** | API 调用量异常检测 | 短时间内 RunInstances 调用量异常飙升 | 否（需开启） |
| **Network Activity Events** | VPC Endpoint 的网络活动 | 通过 VPC Endpoint 访问 S3 | 否（需开启） |

### 读写分类

每种事件可进一步分为：

- **Read**：不修改资源的操作（Describe、Get、List）
- **Write**：修改资源的操作（Create、Delete、Put、Update）

> **成本提示**：Data Events 中，S3 GetObject 通常是最大的日志量来源。仅在安全要求高时开启。

---

## Trail 配置

### 创建 Trail

```bash
# 基本 Trail：管理事件 → S3
aws cloudtrail create-trail \
    --name my-audit-trail \
    --s3-bucket-name my-cloudtrail-logs \
    --s3-key-prefix audit \
    --is-multi-region-trail \
    --enable-log-file-validation

# 启动日志记录
aws cloudtrail start-logging --name my-audit-trail
```

### 开启 Data Events

```bash
# 记录所有 S3 数据事件
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

# 记录 Lambda 调用事件
aws cloudtrail put-event-selectors \
    --trail-name my-audit-trail \
    --event-selectors '[{
        "ReadWriteType": "All",
        "IncludeManagementEvents": true,
        "DataResources": [{
            "Type": "AWS::Lambda::Function",
            "Values": ["arn:aws:lambda:us-east-1:123456789:function:my-function"]
        }]
    }]'
```

### 高级事件选择器（更精细控制）

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

### S3 Bucket 策略

CloudTrail 需要写入 S3 的权限：

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
      "Resource": "arn:aws:s3:::my-cloudtrail-logs/audit/AWSLogs/123456789/*",
      "Condition": {
        "StringEquals": {"s3:x-amz-acl": "bucket-owner-full-control"}
      }
    }
  ]
}
```

---

## CloudTrail Lake

托管的事件查询服务，支持 SQL，无需配置 Athena + Glue：

### 创建 Event Data Store

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

### SQL 查询

```sql
-- 最近 24 小时的 IAM 变更
SELECT eventTime, userIdentity.arn, eventName, requestParameters
FROM <event-data-store-id>
WHERE eventSource = 'iam.amazonaws.com'
  AND eventTime > '2026-04-12T00:00:00Z'
ORDER BY eventTime DESC

-- 特定用户的所有操作
SELECT eventTime, eventSource, eventName, sourceIPAddress
FROM <event-data-store-id>
WHERE userIdentity.arn = 'arn:aws:iam::123456789:user/alice'
  AND eventTime > '2026-04-01T00:00:00Z'

-- 控制台登录失败
SELECT eventTime, userIdentity.arn, sourceIPAddress, errorMessage
FROM <event-data-store-id>
WHERE eventName = 'ConsoleLogin'
  AND responseElements.ConsoleLogin = 'Failure'

-- 安全组变更
SELECT eventTime, userIdentity.arn, eventName, requestParameters
FROM <event-data-store-id>
WHERE eventName IN ('AuthorizeSecurityGroupIngress', 'AuthorizeSecurityGroupEgress',
                     'RevokeSecurityGroupIngress', 'RevokeSecurityGroupEgress')
```

```bash
# CLI 查询
QUERY_ID=$(aws cloudtrail start-query \
    --query-statement "SELECT eventTime, eventName FROM <eds-id> WHERE eventSource='s3.amazonaws.com' LIMIT 10" \
    --query 'QueryId' --output text)

aws cloudtrail get-query-results --query-id $QUERY_ID
```

---

## 事件结构

```json
{
  "eventVersion": "1.09",
  "userIdentity": {
    "type": "AssumedRole",
    "principalId": "AROA...:session-name",
    "arn": "arn:aws:sts::123456789:assumed-role/admin-role/alice",
    "accountId": "123456789",
    "sessionContext": {
      "sessionIssuer": {
        "type": "Role",
        "arn": "arn:aws:iam::123456789:role/admin-role"
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
  "recipientAccountId": "123456789"
}
```

### 关键字段速查

| 字段 | 说明 | 安全调查用途 |
|------|------|------------|
| `userIdentity` | 谁（IAM User/Role/Service） | 识别操作者 |
| `sourceIPAddress` | 来源 IP | 检测异常来源 |
| `eventName` | 什么操作 | 识别敏感操作 |
| `eventSource` | 哪个 AWS 服务 | 缩小范围 |
| `requestParameters` | 请求参数 | 操作细节 |
| `responseElements` | 响应内容（仅写操作） | 变更结果 |
| `errorCode` | 错误码（如果失败） | 检测权限探测 |
| `userAgent` | 调用工具 | 检测异常客户端 |

---

## 安全调查常用查询

### 使用 Event History（快速，90 天内）

```bash
# 谁删除了某个 S3 Bucket？
aws cloudtrail lookup-events \
    --lookup-attributes AttributeKey=EventName,AttributeValue=DeleteBucket \
    --start-time "2026-04-01T00:00:00Z"

# 特定用户的近期操作
aws cloudtrail lookup-events \
    --lookup-attributes AttributeKey=Username,AttributeValue=alice \
    --max-results 50

# 来自特定 IP 的操作
aws cloudtrail lookup-events \
    --lookup-attributes AttributeKey=ResourceType,AttributeValue=AWS::IAM::Role
```

### 使用 Athena（长期归档查询）

```sql
-- 在 Athena 中创建 CloudTrail 表
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
LOCATION 's3://my-cloudtrail-logs/audit/AWSLogs/123456789/CloudTrail/';

-- 查找 Root 账户使用
SELECT eventtime, eventname, sourceipaddress, useragent
FROM cloudtrail_logs
WHERE useridentity.type = 'Root'
  AND year = '2026' AND month = '04';

-- 未授权访问尝试
SELECT eventtime, useridentity.arn, eventname, errormessage, sourceipaddress
FROM cloudtrail_logs
WHERE errorcode IN ('AccessDenied', 'UnauthorizedAccess', 'Client.UnauthorizedAccess')
ORDER BY eventtime DESC
LIMIT 100;
```

---

## 与 EventBridge 集成

CloudTrail 管理事件自动发送到 EventBridge default bus：

```bash
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
    --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:123456789:function:sg-alert"
```

```bash
# IAM 策略变更告警
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

### 常见安全规则

| 场景 | eventSource | eventName |
|------|------------|-----------|
| 安全组变更 | ec2.amazonaws.com | Authorize/RevokeSecurityGroup* |
| IAM 策略变更 | iam.amazonaws.com | *Policy, *Role |
| Root 登录 | signin.amazonaws.com | ConsoleLogin（userIdentity.type=Root） |
| S3 Bucket 公开 | s3.amazonaws.com | PutBucketPolicy, PutBucketAcl |
| KMS 密钥操作 | kms.amazonaws.com | DisableKey, ScheduleKeyDeletion |
| VPC 变更 | ec2.amazonaws.com | Create/DeleteVpc, *RouteTable* |
| CloudTrail 停止 | cloudtrail.amazonaws.com | StopLogging, DeleteTrail |

---

## 与 CloudWatch 集成

### 将 CloudTrail 日志发送到 CloudWatch Logs

```bash
aws cloudtrail update-trail \
    --name my-audit-trail \
    --cloud-watch-logs-log-group-arn "arn:aws:logs:us-east-1:123456789:log-group:CloudTrail/audit:*" \
    --cloud-watch-logs-role-arn "arn:aws:iam::123456789:role/CloudTrail-CWLogs-Role"
```

### CloudWatch Metric Filter + Alarm

```bash
# Root 账户使用告警
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
    --alarm-actions arn:aws:sns:us-east-1:123456789:security-alerts

# 未授权 API 调用告警
aws logs put-metric-filter \
    --log-group-name CloudTrail/audit \
    --filter-name "UnauthorizedAPICalls" \
    --filter-pattern '{($.errorCode = "*UnauthorizedAccess*") || ($.errorCode = "AccessDenied*")}' \
    --metric-transformations \
        metricName=UnauthorizedAPICalls,metricNamespace=CloudTrailMetrics,metricValue=1
```

---

## 组织级 Trail

### AWS Organizations 集中审计

```bash
# 在管理账户创建组织级 Trail
aws cloudtrail create-trail \
    --name org-audit-trail \
    --s3-bucket-name org-cloudtrail-logs \
    --is-multi-region-trail \
    --is-organization-trail \
    --enable-log-file-validation

aws cloudtrail start-logging --name org-audit-trail
```

### 日志存储结构

```
s3://org-cloudtrail-logs/
  └── AWSLogs/
        └── o-orgid/
              ├── 111111111111/  (账户 A)
              │     └── CloudTrail/
              │           └── us-east-1/
              │                 └── 2026/04/13/
              ├── 222222222222/  (账户 B)
              └── 333333333333/  (账户 C)
```

---

## 安全最佳实践

1. **所有区域开启 Trail**：`--is-multi-region-trail`
2. **开启日志文件验证**：`--enable-log-file-validation`（检测日志被篡改）
3. **S3 Bucket 加密**：SSE-S3 或 SSE-KMS
4. **S3 Bucket 访问限制**：仅 CloudTrail 服务和安全团队可访问
5. **开启 CloudTrail Insights**：自动检测 API 调用量异常
6. **投递到 CloudWatch Logs**：实现实时告警
7. **跨账户集中存储**：用 Organizations Trail 或跨账户 S3
8. **监控 CloudTrail 本身**：检测 StopLogging、DeleteTrail 事件
9. **不要只依赖 Event History**：90 天后数据消失，必须有 Trail 持久化

### 开启 Insights

```bash
aws cloudtrail put-insight-selectors \
    --trail-name my-audit-trail \
    --insight-selectors '[
        {"InsightType": "ApiCallRateInsight"},
        {"InsightType": "ApiErrorRateInsight"}
    ]'
```

---

## 成本优化

| 项目 | 免费 | 收费 |
|------|------|------|
| 管理事件（第一份 Trail） | 免费 | 额外 Trail $2.00/10 万事件 |
| 数据事件 | — | $0.10/10 万事件 |
| Insights 事件 | — | $0.35/10 万事件分析 |
| CloudTrail Lake 摄入 | — | $2.50/GB |
| CloudTrail Lake 查询 | — | $0.005/GB 扫描 |
| S3 存储 | — | 标准 S3 费率 |

### 优化策略

1. **只开一份 Trail**：多份 Trail 重复收费
2. **Data Events 按需开启**：只监控敏感 Bucket/函数
3. **用 S3 Lifecycle 管理日志**：30 天 → IA，90 天 → Glacier
4. **CloudTrail Lake vs Athena**：小查询量用 Lake，大规模分析用 Athena + S3
5. **排除高频无风险的 Read 事件**：如果不需要审计 DescribeInstances

---

## CLI 速查

```bash
# Trail 管理
aws cloudtrail describe-trails
aws cloudtrail get-trail-status --name TRAIL
aws cloudtrail start-logging --name TRAIL
aws cloudtrail stop-logging --name TRAIL

# 事件查询（90 天内）
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

# 日志验证
aws cloudtrail validate-logs \
    --trail-arn arn:aws:cloudtrail:us-east-1:123456789:trail/TRAIL \
    --start-time "2026-04-01T00:00:00Z"
```

---

*最后更新：2026-04-13*
