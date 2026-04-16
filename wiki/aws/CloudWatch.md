# Amazon CloudWatch

> AWS unified monitoring and observability service, covering metrics, logs, alarms, dashboards, and application tracing.
> [[Lambda]] logs and metrics are automatically written to CloudWatch.
> [[EventBridge]] can trigger actions based on CloudWatch alarms.
> [[CloudTrail]] API audit logs can be delivered to CloudWatch Logs.
> Metaflow Batch job logs are written to CloudWatch Logs; see [[Metaflow工作流框架]].

> AWS 统一的监控与可观测性服务，涵盖指标、日志、告警、仪表盘和应用追踪。
> [[Lambda]] 日志和指标自动写入 CloudWatch。
> [[EventBridge]] 可基于 CloudWatch 告警触发动作。
> [[CloudTrail]] 的 API 审计日志可投递到 CloudWatch Logs。
> Metaflow Batch job 日志写入 CloudWatch Logs，见 [[Metaflow工作流框架]]。

## Table of Contents / 目录

- [[#Core Components / 核心组件]]
- [[#Metrics / Metrics（指标）]]
- [[#Logs / Logs（日志）]]
- [[#Alarms / Alarms（告警）]]
- [[#Dashboards / Dashboards（仪表盘）]]
- [[#Logs Insights / Logs Insights（日志查询）]]
- [[#Contributor Insights]]
- [[#Synthetics / Synthetics（合成监控）]]
- [[#Application Signals]]
- [[#Cost Optimization / 成本优化]]
- [[#CLI Quick Reference / CLI 速查]]

---

## Core Components / 核心组件

| Component / 组件 | Description / 说明 |
|------|------|
| **Metrics** | Time-series numeric data (CPU, memory, custom metrics) / 时序数值数据（CPU、内存、自定义指标） |
| **Logs** | Log collection, storage, and querying / 日志收集、存储、查询 |
| **Alarms** | Trigger actions based on metric thresholds (SNS, Auto Scaling, Lambda) / 基于指标阈值触发动作 |
| **Dashboards** | Visual dashboards / 可视化仪表盘 |
| **Logs Insights** | SQL-like query engine for logs / 日志的 SQL-like 查询引擎 |
| **Contributor Insights** | Identify top-N contributors (IPs, URLs, etc.) / 识别 top-N 贡献者（IP、URL 等） |
| **Synthetics** | Scheduled simulated user access (Canary) / 定时模拟用户访问（Canary） |
| **ServiceLens / X-Ray** | Distributed tracing and service map / 分布式追踪和服务地图 |

---

## Metrics / Metrics（指标）

### Concepts / 概念

| Concept / 概念 | Description / 说明 |
|------|------|
| **Namespace** | Logical grouping of metrics (e.g. `AWS/EC2`, `AWS/Lambda`, custom) / 指标的逻辑分组 |
| **Metric Name** | Metric name (e.g. `CPUUtilization`) / 指标名 |
| **Dimension** | Key-value pair to differentiate metrics (e.g. `InstanceId=i-xxx`) / 区分指标的键值对 |
| **Period** | Aggregation granularity (60s, 300s, etc.) / 统计粒度 |
| **Statistic** | Aggregation method (Average, Sum, Max, Min, p99, etc.) / 聚合方式 |
| **Resolution** | Standard (60s) or high resolution (1s) / 标准（60s）或高分辨率（1s） |

### AWS Service Built-in Metrics / AWS 服务内置指标

```
AWS/EC2:      CPUUtilization, NetworkIn/Out, DiskRead/WriteOps
AWS/Lambda:   Invocations, Duration, Errors, Throttles, ConcurrentExecutions
AWS/RDS:      DatabaseConnections, ReadLatency, FreeStorageSpace
AWS/S3:       BucketSizeBytes, NumberOfObjects
AWS/SQS:      ApproximateNumberOfMessagesVisible, ApproximateAgeOfOldestMessage
AWS/ELB:      RequestCount, TargetResponseTime, HTTPCode_Target_5XX_Count
```

### Custom Metrics / 自定义指标

```python
import boto3

cw = boto3.client('cloudwatch')

# Publish a single metric / 发布单个指标
cw.put_metric_data(
    Namespace='MyApp/Orders',
    MetricData=[{
        'MetricName': 'OrderCount',
        'Dimensions': [
            {'Name': 'Environment', 'Value': 'prod'},
            {'Name': 'Region', 'Value': 'us-east-1'}
        ],
        'Value': 1,
        'Unit': 'Count',
        'Timestamp': datetime.utcnow()
    }]
)
```

```python
# High resolution metric (1-second granularity) / 高分辨率指标（1 秒粒度）
cw.put_metric_data(
    Namespace='MyApp/Latency',
    MetricData=[{
        'MetricName': 'APILatency',
        'Value': 45.2,
        'Unit': 'Milliseconds',
        'StorageResolution': 1  # 1 = high resolution, 60 = standard / 1 = 高分辨率，60 = 标准
    }]
)
```

### Embedded Metric Format (EMF)

Embed metrics in logs; CloudWatch automatically extracts them as metrics (no separate `put_metric_data` call needed).

> 在日志中嵌入指标，CloudWatch 自动提取为指标（无需单独调用 `put_metric_data`）。

```python
import json

# In Lambda, just print; CloudWatch auto-parses
# 在 Lambda 中直接 print，CloudWatch 自动解析
print(json.dumps({
    "_aws": {
        "Timestamp": 1681234567890,
        "CloudWatchMetrics": [{
            "Namespace": "MyApp",
            "Dimensions": [["Service", "Environment"]],
            "Metrics": [
                {"Name": "ProcessingTime", "Unit": "Milliseconds"},
                {"Name": "ItemCount", "Unit": "Count"}
            ]
        }]
    },
    "Service": "OrderService",
    "Environment": "prod",
    "ProcessingTime": 125,
    "ItemCount": 42
}))
```

**Recommended**: Use EMF for publishing metrics in Lambda; more efficient than `put_metric_data` (no additional API calls).

> **推荐**：Lambda 中用 EMF 发布指标，比 `put_metric_data` 更高效（无额外 API 调用）。

---

## Logs / Logs（日志）

### Hierarchy / 层级结构

```
Log Group (/aws/lambda/my-function)
    └── Log Stream (2026/04/13/[$LATEST]abc123)
            └── Log Event (timestamp + message / 时间戳 + 消息)
```

### Log Retention / 日志保留

```bash
# Set Log Group retention period / 设置 Log Group 保留期
aws logs put-retention-policy \
    --log-group-name /aws/lambda/my-function \
    --retention-in-days 30

# Common values / 常用值: 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, permanent (unset) / 永久（不设置）
```

### Write Logs / 写入日志

```python
import boto3

logs = boto3.client('logs')

# Create Log Group and Stream / 创建 Log Group 和 Stream
logs.create_log_group(logGroupName='/myapp/service')
logs.create_log_stream(
    logGroupName='/myapp/service',
    logStreamName='instance-001'
)

# Write log events / 写入日志事件
logs.put_log_events(
    logGroupName='/myapp/service',
    logStreamName='instance-001',
    logEvents=[
        {'timestamp': int(time.time() * 1000), 'message': 'Processing started'},
        {'timestamp': int(time.time() * 1000), 'message': 'Item processed: ORD-001'}
    ]
)
```

Lambda, ECS, Batch, and other services automatically write to CloudWatch Logs; no manual calls needed.

> Lambda、ECS、Batch 等服务自动写入 CloudWatch Logs，无需手动调用。

### Metric Filter

Automatically extract metrics from logs.

> 从日志中自动提取指标。

```bash
# Count ERROR occurrences in logs / 统计日志中 ERROR 出现次数
aws logs put-metric-filter \
    --log-group-name /aws/lambda/my-function \
    --filter-name "ErrorCount" \
    --filter-pattern "ERROR" \
    --metric-transformations \
        metricName=ErrorCount,metricNamespace=MyApp,metricValue=1

# More complex pattern: extract values from JSON logs
# 更复杂的模式：提取 JSON 日志中的数值
aws logs put-metric-filter \
    --log-group-name /myapp/api \
    --filter-name "HighLatency" \
    --filter-pattern '{$.latency > 1000}' \
    --metric-transformations \
        metricName=HighLatencyCount,metricNamespace=MyApp,metricValue=1
```

### Log Subscription (Subscription Filter) / 日志订阅（Subscription Filter）

Stream logs to other services in real-time.

> 实时将日志流转到其他服务。

```bash
# Logs → Lambda (real-time processing) / 日志 → Lambda（实时处理）
aws logs put-subscription-filter \
    --log-group-name /aws/lambda/my-function \
    --filter-name "error-processor" \
    --filter-pattern "ERROR" \
    --destination-arn arn:aws:lambda:us-east-1:<account-id>:function:log-processor

# Logs → Kinesis → S3 (archive) / 日志 → Kinesis → S3（归档）
# Logs → OpenSearch (search & analytics) / 日志 → OpenSearch（搜索分析）
```

### Export Logs to S3 / 日志导出到 S3

```bash
aws logs create-export-task \
    --log-group-name /aws/lambda/my-function \
    --from 1680307200000 \
    --to 1681234567890 \
    --destination my-log-archive-bucket \
    --destination-prefix "lambda-logs"
```

---

## Alarms / Alarms（告警）

### Alarm States / 告警状态

```
OK  ──►  ALARM  ──►  OK
         │
         ▼
    INSUFFICIENT_DATA
```

### Create Alarm / 创建告警

```bash
# Lambda error rate alarm / Lambda 错误率告警
aws cloudwatch put-metric-alarm \
    --alarm-name "lambda-high-errors" \
    --metric-name Errors \
    --namespace AWS/Lambda \
    --dimensions Name=FunctionName,Value=my-function \
    --statistic Sum \
    --period 300 \
    --evaluation-periods 2 \
    --threshold 5 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --alarm-actions arn:aws:sns:us-east-1:<account-id>:alerts \
    --ok-actions arn:aws:sns:us-east-1:<account-id>:alerts \
    --treat-missing-data notBreaching
```

### Composite Alarm / 组合告警

```bash
# Combine multiple conditions / 多个条件组合
aws cloudwatch put-composite-alarm \
    --alarm-name "service-degraded" \
    --alarm-rule 'ALARM("high-latency") AND ALARM("high-error-rate")' \
    --alarm-actions arn:aws:sns:us-east-1:<account-id>:critical-alerts
```

### Math Expression Alarm / 数学表达式告警

```bash
# Error rate (errors / total invocations * 100) / 错误率（错误数 / 总调用数 * 100）
aws cloudwatch put-metric-alarm \
    --alarm-name "error-rate-high" \
    --metrics '[
        {"Id":"errors","MetricStat":{"Metric":{"Namespace":"AWS/Lambda","MetricName":"Errors","Dimensions":[{"Name":"FunctionName","Value":"my-func"}]},"Period":300,"Stat":"Sum"}},
        {"Id":"invocations","MetricStat":{"Metric":{"Namespace":"AWS/Lambda","MetricName":"Invocations","Dimensions":[{"Name":"FunctionName","Value":"my-func"}]},"Period":300,"Stat":"Sum"}},
        {"Id":"error_rate","Expression":"(errors/invocations)*100","Label":"Error Rate %"}
    ]' \
    --threshold 5 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 3 \
    --alarm-actions arn:aws:sns:us-east-1:<account-id>:alerts
```

### Anomaly Detection Alarm / 异常检测告警

```bash
# ML-based automatic thresholds / 基于机器学习的自动阈值
aws cloudwatch put-anomaly-detector \
    --namespace AWS/Lambda \
    --metric-name Duration \
    --dimensions Name=FunctionName,Value=my-function \
    --stat Average

aws cloudwatch put-metric-alarm \
    --alarm-name "lambda-anomaly-duration" \
    --metrics '[
        {"Id":"m1","MetricStat":{"Metric":{"Namespace":"AWS/Lambda","MetricName":"Duration","Dimensions":[{"Name":"FunctionName","Value":"my-function"}]},"Period":300,"Stat":"Average"}},
        {"Id":"ad1","Expression":"ANOMALY_DETECTION_BAND(m1, 2)"}
    ]' \
    --threshold-metric-id ad1 \
    --comparison-operator LessThanLowerOrGreaterThanUpperThreshold \
    --evaluation-periods 3 \
    --alarm-actions arn:aws:sns:us-east-1:<account-id>:alerts
```

---

## Dashboards / Dashboards（仪表盘）

### Create Dashboard / 创建仪表盘

```bash
aws cloudwatch put-dashboard \
    --dashboard-name "my-service" \
    --dashboard-body '{
        "widgets": [
            {
                "type": "metric",
                "x": 0, "y": 0, "width": 12, "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/Lambda", "Invocations", "FunctionName", "my-func"],
                        [".", "Errors", ".", "."]
                    ],
                    "period": 300,
                    "stat": "Sum",
                    "title": "Lambda Invocations & Errors"
                }
            },
            {
                "type": "log",
                "x": 12, "y": 0, "width": 12, "height": 6,
                "properties": {
                    "query": "SOURCE \"/aws/lambda/my-func\" | filter @message like /ERROR/ | stats count(*) as errors by bin(5m)",
                    "title": "Error Timeline"
                }
            }
        ]
    }'
```

---

## Logs Insights / Logs Insights（日志查询）

### Query Syntax / 查询语法

```sql
-- Recent error logs / 最近的错误日志
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 50

-- Lambda cold start statistics / Lambda 冷启动统计
filter @type = "REPORT"
| stats avg(@duration) as avg_duration,
        max(@duration) as max_duration,
        count(*) as invocations
  by bin(1h)

-- Trace by request ID / 按请求 ID 追踪
fields @timestamp, @message
| filter @requestId = "abc-123-def"
| sort @timestamp asc

-- P99 latency / P99 延迟
filter @type = "REPORT"
| stats pct(@duration, 99) as p99,
        pct(@duration, 95) as p95,
        pct(@duration, 50) as p50
  by bin(1h)

-- JSON log parsing / JSON 日志解析
fields @timestamp
| parse @message '{"orderId":"*","amount":*}' as orderId, amount
| filter amount > 100
| stats sum(amount) as totalRevenue by bin(1d)
```

### CLI Query / CLI 查询

```bash
# Start query / 启动查询
QUERY_ID=$(aws logs start-query \
    --log-group-name /aws/lambda/my-function \
    --start-time $(date -d '1 hour ago' +%s) \
    --end-time $(date +%s) \
    --query-string 'filter @message like /ERROR/ | stats count(*) by bin(5m)' \
    --query 'queryId' --output text)

# Get results / 获取结果
aws logs get-query-results --query-id $QUERY_ID
```

---

## Contributor Insights

Identify top-N contributors in the system (e.g. most frequent IPs, slowest APIs).

> 识别系统中的 top-N 贡献者（如最频繁的 IP、最慢的 API 等）。

```bash
aws cloudwatch put-insight-rule \
    --rule-name "top-error-apis" \
    --rule-state ENABLED \
    --rule-definition '{
        "Schema": {"Name": "CloudWatchLogRule", "Version": 1},
        "LogGroupNames": ["/myapp/api"],
        "LogFormat": "JSON",
        "Contribution": {
            "Keys": ["$.api_path"],
            "ValueOf": "$.error_count",
            "Filters": [{"Match": "$.status_code", "GreaterThan": 499}]
        },
        "AggregateOn": "Sum"
    }'
```

---

## Synthetics / Synthetics（合成监控）

Periodically simulate user behavior to detect service availability.

> 定时模拟用户行为，检测服务可用性。

```bash
# Create Canary (check API every 5 minutes) / 创建 Canary（每 5 分钟检测一次 API）
aws synthetics create-canary \
    --name "api-health-check" \
    --code '{"handler":"index.handler","zipFile":"..."}' \
    --artifact-s3-location "s3://my-canary-artifacts/" \
    --execution-role-arn "arn:aws:iam::<account-id>:role/canary-role" \
    --schedule '{"Expression":"rate(5 minutes)"}' \
    --runtime-version "syn-python-selenium-3.0"
```

---

## Application Signals

Automatically detect and monitor application SLIs/SLOs (Service Level Indicators/Objectives).

> 自动检测和监控应用的 SLI/SLO（服务水平指标/目标）。

```bash
# Set SLO for a service / 为服务设置 SLO
# e.g. API latency p99 < 500ms, availability > 99.9%
# 例如：API 延迟 p99 < 500ms，可用性 > 99.9%
# Easier to configure via Console; CLI is more complex
# 通过 Console 配置更方便，CLI 较复杂
```

---

## Cost Optimization / 成本优化

| Billing Item / 计费项 | Optimization / 优化方法 |
|--------|---------|
| Custom metrics / 自定义指标 | Reduce Dimension combinations, use EMF instead of `put_metric_data` / 减少 Dimension 组合，用 EMF 替代 |
| Log storage / 日志存储 | Set reasonable retention periods, export old logs to S3 / 设置合理保留期，旧日志导出到 S3 |
| Log ingestion / 日志摄入 | Filter unnecessary DEBUG logs, adjust log levels / 过滤不必要的 DEBUG 日志，调整日志级别 |
| Logs Insights queries / Logs Insights 查询 | Narrow time range and Log Group scope / 缩小时间范围和 Log Group 范围 |
| Alarms / 告警 | Avoid unnecessary high-resolution alarms / 避免创建不必要的高分辨率告警 |
| Dashboard / 仪表盘 | Don't set auto-refresh interval too short / 自动刷新间隔不要设太短 |
| Cross-account / 跨账户 | Use CloudWatch cross-account observability for centralized monitoring / 用 cross-account observability 集中监控 |

### Pricing Highlights / 定价要点

| Item / 项目 | Free Tier / 免费额度 | Overage Price / 超出价格 |
|------|---------|---------|
| Custom metrics / 自定义指标 | 10 | ~$0.30/metric/month / 指标/月 |
| Alarms / 告警 | 10 | ~$0.10/alarm/month / 告警/月 |
| API calls (GetMetricData) | 1M / 100 万次 | $0.01/1000 |
| Log ingestion / 日志摄入 | 5 GB | ~$0.50/GB |
| Log storage / 日志存储 | 5 GB | ~$0.03/GB/month / 月 |
| Logs Insights | -- | $0.005/GB scanned / 扫描 |

---

## CLI Quick Reference / CLI 速查

```bash
# Metrics / 指标
aws cloudwatch list-metrics --namespace AWS/Lambda
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda --metric-name Duration \
    --dimensions Name=FunctionName,Value=my-func \
    --start-time 2026-04-13T00:00:00Z --end-time 2026-04-13T23:59:59Z \
    --period 3600 --statistics Average Maximum

# Alarms / 告警
aws cloudwatch describe-alarms --state-value ALARM
aws cloudwatch set-alarm-state --alarm-name NAME --state-value OK --state-reason "manual reset"

# Logs / 日志
aws logs describe-log-groups
aws logs tail /aws/lambda/my-function --follow --since 1h
aws logs filter-log-events --log-group-name NAME --filter-pattern "ERROR"

# Dashboards / 仪表盘
aws cloudwatch list-dashboards
aws cloudwatch get-dashboard --dashboard-name NAME

# Insights queries / Insights 查询
aws logs start-query --log-group-name NAME \
    --start-time EPOCH --end-time EPOCH \
    --query-string 'fields @timestamp, @message | limit 20'
aws logs get-query-results --query-id ID
```

---

*Last updated / 最后更新：2026-04-13*
