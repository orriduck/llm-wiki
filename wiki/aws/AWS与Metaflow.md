# AWS 与 Metaflow

> Metaflow 在 AWS 上的架构、IAM 权限设计、各服务配置细节，以及 Outerbounds 托管方案对比。
> Metaflow 框架本身的用法见 [[Metaflow工作流框架]]。

## 目录

- [[#整体架构]]
- [[#S3：Artifact Store]]
- [[#AWS Batch：计算层]]
- [[#ECR：镜像管理]]
- [[#Step Functions：调度与编排]]
- [[#IAM 权限结构]]
- [[#Metaflow 配置文件]]
- [[#Outerbounds vs 自建]]
- [[#运维与监控]]

---

## 整体架构

```
开发者本机
    │
    │  python flow.py run
    │
    ▼
Metaflow CLI/SDK
    ├──► S3 Bucket          (artifact 读写)
    ├──► AWS Batch          (计算 job 提交)
    │        └──► EC2/Fargate (实际执行容器)
    │                 └──► ECR (拉取镜像)
    ├──► CloudWatch Logs    (日志)
    └──► Step Functions     (定时/事件触发调度)

Metadata Service（可选，自建或 Outerbounds 提供）
    └──► RDS / DynamoDB     (run/task 元数据索引)
```

### 各服务职责

| AWS 服务 | Metaflow 中的角色 | 触发条件 |
|---------|-----------------|---------|
| **S3** | 所有 artifact、代码包的存储后端 | 每次 step 开始/结束都读写 |
| **AWS Batch** | `@batch` 装饰器的执行环境 | step 有 `@batch` 时提交 job |
| **ECR** | 存储自定义 Docker 镜像 | `@batch(image=...)` 指定 ECR URI 时 |
| **CloudWatch Logs** | Batch job 的 stdout/stderr | 所有 Batch step 自动写入 |
| **Step Functions** | 将 Flow 编译为 State Machine 定时调度 | `python flow.py step-functions create` |
| **EventBridge** | 触发 Step Functions 的定时/事件规则 | 配合 Step Functions 使用 |
| **IAM** | 权限控制（用户、Batch Job Role、ECS Task Role） | 贯穿所有服务 |

---

## S3：Artifact Store

### 存储结构

Metaflow 在 S3 上用固定的路径前缀组织所有数据：

```
s3://<BUCKET>/<PREFIX>/
  └── metaflow/
        ├── data/
        │   └── <content_hash>          # artifact 内容，按内容寻址（去重）
        ├── <FlowName>/
        │   └── <run_id>/
        │       └── <step_name>/
        │           └── <task_id>/
        │               └── <artifact_name>  # 实际是指向 data/ 的指针文件
        └── _snowflake/                  # 内部元数据（可忽略）
```

**内容寻址（Content-addressable）的意义**：
- 相同内容的 artifact 只存一份，节省 S3 空间
- 两个 run 引用同一份数据时，S3 上没有冗余副本
- artifact 的"路径文件"只记录 content hash，指向 `data/` 目录

### S3 配置

```bash
# ~/.metaflowconfig 中配置
{
    "METAFLOW_DATASTORE_SYSROOT_S3": "s3://my-metaflow-bucket/prefix",
    "METAFLOW_DEFAULT_DATASTORE": "s3"
}
```

```bash
# 运行时临时覆盖
python flow.py run --datastore=s3 \
    --datastore-root=s3://other-bucket/other-prefix
```

### S3 存储成本优化

```json
{
  "Rules": [
    {
      "ID": "MetaflowDataLifecycle",
      "Filter": {"Prefix": "metaflow/data/"},
      "Status": "Enabled",
      "Transitions": [
        {"Days": 30, "StorageClass": "STANDARD_IA"},
        {"Days": 90, "StorageClass": "GLACIER_IR"}
      ],
      "Expiration": {"Days": 365}
    }
  ]
}
```

> **注意**：只对 `metaflow/data/` 前缀设置生命周期，不要对元数据路径（`<FlowName>/`）设置过短的过期时间，否则 Client API 查询会失败。

### S3 访问模式

```python
# 在 step 中直接使用 Metaflow 的 S3 客户端（性能优化）
from metaflow.plugins.aws.aws_utils import get_s3_client
from metaflow import S3

@step
def process(self):
    # 方式1：Metaflow S3 工具类（批量操作更快）
    with S3(run=self) as s3:
        s3_objects = s3.get_many([
            "s3://bucket/file1.parquet",
            "s3://bucket/file2.parquet",
        ])
        local_files = [obj.path for obj in s3_objects]
    
    # 方式2：直接用 boto3（需要 IAM 权限）
    import boto3
    s3 = boto3.client('s3')
    s3.download_file('bucket', 'key', '/tmp/file')
    
    self.next(self.end)
```

---

## AWS Batch：计算层

### 核心概念

```
Compute Environment  →  Job Queue  →  Job Definition  →  Job
     （EC2 实例池）       （调度队列）    （容器模板）      （实际执行）
```

Metaflow **自动创建 Job Definition**（每次运行），不需要预先定义。只需要预先配置 Compute Environment 和 Job Queue。

### Compute Environment 配置

**按需（MANAGED，推荐）**：

```json
{
  "computeEnvironmentName": "metaflow-ce-managed",
  "type": "MANAGED",
  "state": "ENABLED",
  "computeResources": {
    "type": "SPOT",
    "allocationStrategy": "SPOT_CAPACITY_OPTIMIZED",
    "minvCpus": 0,
    "maxvCpus": 1024,
    "desiredvCpus": 0,
    "instanceTypes": ["m5", "m5a", "m4", "c5", "r5"],
    "subnets": ["subnet-xxxxxxxx", "subnet-yyyyyyyy"],
    "securityGroupIds": ["sg-xxxxxxxx"],
    "instanceRole": "arn:aws:iam::123456789:instance-profile/ecsInstanceRole",
    "tags": {"Project": "metaflow"}
  },
  "serviceRole": "arn:aws:iam::123456789:role/AWSBatchServiceRole"
}
```

**GPU 专用 Compute Environment**：

```json
{
  "computeEnvironmentName": "metaflow-ce-gpu",
  "computeResources": {
    "type": "EC2",
    "instanceTypes": ["p3.2xlarge", "p3.8xlarge", "g4dn.xlarge"],
    "allocationStrategy": "BEST_FIT_PROGRESSIVE",
    "minvCpus": 0,
    "maxvCpus": 256
  }
}
```

### Job Queue 配置

```json
{
  "jobQueueName": "metaflow-queue-default",
  "state": "ENABLED",
  "priority": 100,
  "computeEnvironmentOrder": [
    {"order": 1, "computeEnvironment": "metaflow-ce-spot"},
    {"order": 2, "computeEnvironment": "metaflow-ce-ondemand"}
  ]
}
```

多个 Compute Environment 按优先级顺序尝试（Spot 失败时 fallback 到 On-Demand）。

### Batch 中的 @batch 参数映射

| `@batch` 参数 | Batch Job Definition 字段 | 说明 |
|--------------|--------------------------|------|
| `cpu` | `vcpus` | vCPU 数量 |
| `memory` | `memory` (MB) | 内存 MB |
| `gpu` | `resourceRequirements[type=GPU]` | GPU 数量 |
| `image` | `containerProperties.image` | Docker 镜像 URI |
| `queue` | `jobQueueArn` | 指定 Job Queue |
| `execution_role` | `executionRoleArn` | Fargate 用 |
| `job_role` | `jobRoleArn` | 容器内的 IAM 角色 |
| `num_parallel` | `arrayProperties.size` | 并行节点数（`@parallel` 用） |

### 排查 Batch Job 失败

```bash
# 1. 查看 Metaflow 日志（会显示 Batch job ID）
python flow.py logs <run_id>/<step_name>/<task_id>

# 2. 在 AWS Console 或 CLI 查看 Job 详情
aws batch describe-jobs --jobs <job-id>

# 3. 查看 CloudWatch 日志
aws logs get-log-events \
    --log-group-name /aws/batch/job \
    --log-stream-name <log-stream-name>

# 4. 常见失败原因
# - Exit code 137: OOM（内存不够，加大 @batch(memory=...)）
# - Exit code 1 + ModuleNotFoundError: 镜像缺依赖（加 @pypi）
# - FAILED status + reason "Host EC2 terminated": Spot 被回收（加 @retry）
```

---

## ECR：镜像管理

### 为什么需要自定义镜像

默认情况下 Metaflow Batch job 使用 Python 官方镜像，配合 `@conda`/`@pypi` 动态安装依赖。自定义 ECR 镜像适合：

1. **需要系统级依赖**（CUDA、libgomp、GDAL 等）
2. **安装时间太长**（几十个包）
3. **私有包**（公司内部 PyPI 无法从 Batch 访问）
4. **固化依赖**（生产稳定性要求）

### 构建和推送镜像

```dockerfile
# Dockerfile.metaflow
FROM python:3.11-slim

# 系统依赖
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Metaflow 本身必须安装
RUN pip install metaflow
```

```bash
# 构建并推送到 ECR
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=us-east-1
REPO_NAME=metaflow-base
IMAGE_TAG=v1.0.0

# 创建 ECR 仓库（首次）
aws ecr create-repository --repository-name $REPO_NAME

# 登录 ECR
aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin \
    $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# 构建并推送
docker build -t $REPO_NAME:$IMAGE_TAG -f Dockerfile.metaflow .
docker tag $REPO_NAME:$IMAGE_TAG \
    $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG
docker push \
    $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG
```

```python
# 在 Flow 中使用 ECR 镜像
ECR_IMAGE = f"{AWS_ACCOUNT_ID}.dkr.ecr.{REGION}.amazonaws.com/metaflow-base:v1.0.0"

@batch(cpu=4, memory=16000, image=ECR_IMAGE)
@step
def train(self):
    import special_private_package  # 镜像内已有
    ...
```

### ECR 生命周期策略

```json
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Keep last 10 tagged images",
      "selection": {
        "tagStatus": "tagged",
        "tagPrefixList": ["v"],
        "countType": "imageCountMoreThan",
        "countNumber": 10
      },
      "action": {"type": "expire"}
    },
    {
      "rulePriority": 2,
      "description": "Delete untagged images after 1 day",
      "selection": {
        "tagStatus": "untagged",
        "countType": "sinceImagePushed",
        "countUnit": "days",
        "countNumber": 1
      },
      "action": {"type": "expire"}
    }
  ]
}
```

---

## Step Functions：调度与编排

### 工作原理

`python flow.py step-functions create` 将 Metaflow Flow 编译成 AWS Step Functions State Machine 的 JSON 定义，再结合 EventBridge 规则实现定时触发。

```
EventBridge Rule (cron)
    │
    ▼
Step Functions State Machine
    ├── State: start      → Lambda/Batch job
    ├── State: process    → Batch job
    └── State: end        → Lambda/Batch job
```

### 部署和管理

```bash
# 首次创建 State Machine
python flow.py step-functions create

# 更新（重新部署）
python flow.py step-functions create --recreate-failed-sfn

# 立刻触发一次执行
python flow.py step-functions trigger

# 传入参数触发
python flow.py step-functions trigger --lr 0.01 --model xgb

# 查看状态
python flow.py step-functions list-runs

# 删除
python flow.py step-functions deregister
```

### 定时调度配置

```python
# 在 FlowSpec 上用 @schedule 装饰器声明调度
from metaflow import FlowSpec, step, schedule

@schedule(cron='0 2 * * *')   # 每天 UTC 02:00 运行
class DailyTrainingFlow(FlowSpec):
    ...
```

```python
# 也可以用 weekly/daily/hourly 简写
@schedule(weekly=True)   # 每周一 00:00 UTC
@schedule(daily=True)    # 每天 00:00 UTC
@schedule(hourly=True)   # 每小时整点
```

### Step Functions 执行追踪

```bash
# 查看最近执行的状态
aws stepfunctions list-executions \
    --state-machine-arn arn:aws:states:us-east-1:123456789:stateMachine:MyFlow \
    --status-filter FAILED

# 查看执行详情和失败原因
aws stepfunctions describe-execution \
    --execution-arn arn:aws:states:us-east-1:123456789:execution:MyFlow:run-42
```

---

## IAM 权限结构

Metaflow 涉及多个 IAM 实体，权限职责各不相同：

```
开发者 IAM User/Role
    ├── 提交 Batch Job
    ├── 读写 S3 artifact
    ├── 推送 Step Functions 定义
    └── 查看 CloudWatch Logs

Batch Job Role（容器内使用）
    ├── 读写 S3 artifact（运行时存取 artifact）
    ├── 读取 ECR 镜像（拉取自定义镜像）
    └── 写入 CloudWatch Logs

ECS Instance Role（Batch EC2 节点使用）
    ├── ECR 拉取权限
    ├── CloudWatch Logs 写入
    └── EC2 基础权限（AmazonEC2ContainerServiceforEC2Role）
```

### 开发者权限策略

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3ArtifactAccess",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject", "s3:PutObject", "s3:DeleteObject",
        "s3:ListBucket", "s3:GetBucketLocation"
      ],
      "Resource": [
        "arn:aws:s3:::my-metaflow-bucket",
        "arn:aws:s3:::my-metaflow-bucket/*"
      ]
    },
    {
      "Sid": "BatchJobSubmit",
      "Effect": "Allow",
      "Action": [
        "batch:SubmitJob",
        "batch:DescribeJobs",
        "batch:TerminateJob",
        "batch:ListJobs",
        "batch:DescribeJobQueues",
        "batch:DescribeComputeEnvironments",
        "batch:RegisterJobDefinition",
        "batch:DescribeJobDefinitions"
      ],
      "Resource": "*"
    },
    {
      "Sid": "StepFunctionsManage",
      "Effect": "Allow",
      "Action": [
        "states:CreateStateMachine",
        "states:UpdateStateMachine",
        "states:DeleteStateMachine",
        "states:DescribeStateMachine",
        "states:ListStateMachines",
        "states:StartExecution",
        "states:ListExecutions",
        "states:DescribeExecution"
      ],
      "Resource": "arn:aws:states:*:123456789:stateMachine:*"
    },
    {
      "Sid": "EventBridgeSchedule",
      "Effect": "Allow",
      "Action": [
        "events:PutRule", "events:DeleteRule",
        "events:PutTargets", "events:RemoveTargets",
        "events:DescribeRule"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CloudWatchLogsRead",
      "Effect": "Allow",
      "Action": [
        "logs:GetLogEvents",
        "logs:FilterLogEvents",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams"
      ],
      "Resource": "arn:aws:logs:*:123456789:log-group:/aws/batch/job:*"
    },
    {
      "Sid": "ECRRead",
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:DescribeRepositories",
        "ecr:ListImages"
      ],
      "Resource": "*"
    }
  ]
}
```

### Batch Job Role（容器内 IAM）

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3ArtifactReadWrite",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject", "s3:PutObject",
        "s3:ListBucket", "s3:GetBucketLocation"
      ],
      "Resource": [
        "arn:aws:s3:::my-metaflow-bucket",
        "arn:aws:s3:::my-metaflow-bucket/*"
      ]
    },
    {
      "Sid": "CloudWatchLogsWrite",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/aws/batch/job:*"
    }
  ]
}
```

Trust policy（允许 ECS 容器担任此角色）：

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "ecs-tasks.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
```

### 最小权限原则建议

1. **S3 Bucket 级别限制**：不要给 `s3:*` 全桶权限，限定到 Metaflow 专用 bucket
2. **Batch 提交限制**：可限制只能提交到特定 Job Queue（`arn:aws:batch:...:job-queue/metaflow-*`）
3. **Job Role 与开发者 Role 分开**：容器内 Role 权限应比开发者权限更小
4. **跨账户访问**：开发账户提交 Job，Job 运行在专用数据账户，用 role assumption 跨账户访问 S3

---

## Metaflow 配置文件

`~/.metaflowconfig` 是 JSON 格式，控制所有默认行为：

```json
{
    "METAFLOW_DEFAULT_DATASTORE": "s3",
    "METAFLOW_DATASTORE_SYSROOT_S3": "s3://my-metaflow-artifacts/prod",

    "METAFLOW_DEFAULT_METADATA": "service",
    "METAFLOW_SERVICE_URL": "https://metaflow-metadata.internal/",
    "METAFLOW_SERVICE_AUTH_KEY": "secret-key",

    "METAFLOW_BATCH_JOB_QUEUE": "metaflow-queue-default",
    "METAFLOW_ECS_S3_ACCESS_IAM_ROLE": "arn:aws:iam::123456789:role/MetaflowBatchJobRole",
    "METAFLOW_BATCH_CONTAINER_IMAGE": "123456789.dkr.ecr.us-east-1.amazonaws.com/metaflow-base:latest",

    "METAFLOW_AWS_DEFAULT_REGION": "us-east-1",

    "METAFLOW_SFN_STATE_MACHINE_PREFIX": "metaflow-prod",
    "METAFLOW_SFN_IAM_ROLE": "arn:aws:iam::123456789:role/MetaflowStepFunctionsRole",
    "METAFLOW_EVENTS_SFN_ACCESS_IAM_ROLE": "arn:aws:iam::123456789:role/MetaflowEventsRole"
}
```

### 多环境配置切换

```bash
# 方法1：环境变量覆盖（优先级最高）
export METAFLOW_DATASTORE_SYSROOT_S3=s3://my-bucket/staging

# 方法2：不同配置文件
METAFLOW_CONFIG_PATH=~/.metaflowconfig.staging python flow.py run

# 方法3：在 CI/CD 中用环境变量完全替代文件
export METAFLOW_DEFAULT_DATASTORE=s3
export METAFLOW_DATASTORE_SYSROOT_S3=s3://ci-bucket/ci
export METAFLOW_BATCH_JOB_QUEUE=metaflow-ci-queue
```

---

## Outerbounds vs 自建

### 功能对比

| 维度 | 自建 Metaflow on AWS | Outerbounds 托管 |
|------|---------------------|----------------|
| **Metadata Service** | 需自建（可用官方 CloudFormation 模板） | 托管，开箱即用 |
| **UI / 可视化** | 无（需自建 Metaflow UI） | 内置 Outerbounds Platform UI |
| **权限管理** | 手动配置 IAM，维护成本高 | 细粒度 RBAC，UI 操作 |
| **多租户隔离** | Namespace 软隔离，无强制 | 项目/团队级强隔离 |
| **计算后端** | AWS Batch / Kubernetes | AWS Batch、GCP、Azure、K8s 均支持 |
| **Cards 功能** | 有限（需部署额外服务） | 完整支持，含历史卡片存储 |
| **成本** | 只付 AWS 资源费用 | AWS 资源费用 + Outerbounds 平台费 |
| **Spot 实例管理** | 手动配置 CE 和 fallback | 智能 Spot 管理，更高命中率 |
| **升级维护** | 手动跟进 Metaflow 版本 | 托管升级，无需运维 |
| **审计日志** | CloudTrail（AWS 级别） | 细粒度操作审计 + 合规报告 |

### 自建核心组件清单

使用官方 CloudFormation 模板（[github.com/Netflix/metaflow-tools](https://github.com/Netflix/metaflow-tools)）可以自动创建：

- Metadata Service（ECS Fargate 上的 Python API）
- RDS PostgreSQL（存储 run/step/task 元数据）
- API Gateway（对外暴露 Metadata Service）
- 相关 IAM Role 和 Security Group

```bash
# 使用官方 CloudFormation 部署自建基础设施
aws cloudformation deploy \
    --template-file metaflow-cfn-template.yml \
    --stack-name metaflow-infra \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides \
        MetaflowS3Bucket=my-metaflow-bucket \
        BatchComputeEnvironmentAMI=ami-xxxxxxxxx
```

### 选择建议

| 场景 | 推荐方案 |
|------|---------|
| 个人项目 / 小团队 | 自建（用 CloudFormation 模板，成本低） |
| 中大型团队，有 MLOps 工程师 | 自建，定制化更高 |
| 没有专职 MLOps，团队需要快速上线 | Outerbounds |
| 多云需求（AWS + GCP） | Outerbounds（原生多云支持） |
| 合规/数据主权要求严格 | 自建（数据完全在自己 AWS 账户） |

---

## 运维与监控

### 关键监控指标

```bash
# Batch Job 成功率（CloudWatch 自定义指标）
# 可在 end step 中手动上报
import boto3

@step
def end(self):
    cw = boto3.client('cloudwatch')
    cw.put_metric_data(
        Namespace='Metaflow/Flows',
        MetricData=[{
            'MetricName': 'FlowSuccess',
            'Dimensions': [{'Name': 'FlowName', 'Value': 'TrainingFlow'}],
            'Value': 1,
            'Unit': 'Count'
        }]
    )
```

### 告警设置

```bash
# Batch Job 失败告警
aws cloudwatch put-metric-alarm \
    --alarm-name "MetaflowBatchJobFailed" \
    --metric-name "FailedJobCount" \
    --namespace "AWS/Batch" \
    --statistic Sum \
    --period 300 \
    --threshold 1 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --evaluation-periods 1 \
    --alarm-actions arn:aws:sns:us-east-1:123456789:metaflow-alerts
```

### 成本管理

| 成本项 | 优化方法 |
|--------|---------|
| EC2 Batch 计算 | 优先使用 Spot，配置 fallback CE |
| S3 存储 | 设置生命周期策略，旧 artifact 转 Glacier |
| CloudWatch Logs | 设置 Log Group 保留期（30 天够用） |
| ECR 存储 | 设置镜像生命周期策略，删除旧镜像 |
| NAT Gateway | Batch 节点用 VPC Endpoint 访问 S3/ECR，避免 NAT 流量费 |

### VPC Endpoint 配置（重要成本优化）

Batch 容器访问 S3 和 ECR 时默认走公网（经过 NAT Gateway），配置 VPC Endpoint 后走 AWS 内网：

```bash
# S3 Gateway Endpoint（免费）
aws ec2 create-vpc-endpoint \
    --vpc-id vpc-xxxxxxxx \
    --service-name com.amazonaws.us-east-1.s3 \
    --route-table-ids rtb-xxxxxxxx

# ECR Interface Endpoint（收费，但比 NAT 便宜）
aws ec2 create-vpc-endpoint \
    --vpc-id vpc-xxxxxxxx \
    --vpc-endpoint-type Interface \
    --service-name com.amazonaws.us-east-1.ecr.dkr \
    --subnet-ids subnet-xxxxxxxx \
    --security-group-ids sg-xxxxxxxx
```

---

*最后更新：2026-04-13*
