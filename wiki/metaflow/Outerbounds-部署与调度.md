# Outerbounds 部署与调度

> 涵盖 Argo Workflows 生产部署、`@project` 装饰器的 namespace 隔离、`--production`/`--branch` 用法、`@schedule`/`@trigger` 事件触发，以及 CI/CD 集成流程。

相关笔记：[[Metaflow工作流框架]] | [[Outerbounds概览]]

---

## 生产部署概览

Outerbounds 的生产部署基于 **Argo Workflows**（也支持 AWS Step Functions 和 Apache Airflow，但 Outerbounds 平台主推 Argo）。

**开发 → 生产的完整路径：**

```
本地开发
    ↓  python flow.py run
调试验证
    ↓  python flow.py --with kubernetes run
云端单次执行
    ↓  python flow.py argo-workflows create
生产部署（手动触发或按计划自动执行）
```

---

## Argo Workflows 部署命令

### 基本部署

```bash
# 部署到 Argo Workflows（创建 Workflow Template）
python my_flow.py argo-workflows create

# 使用 fast-bakery 管理依赖（推荐）
python my_flow.py --environment=fast-bakery argo-workflows create

# 查看已部署的工作流
python my_flow.py argo-workflows list

# 手动触发一次执行
python my_flow.py argo-workflows trigger

# 传递参数触发
python my_flow.py argo-workflows trigger --alpha 0.01 --dataset s3://my-bucket/data.csv
```

### `--production` 标志

```bash
# 部署为 production 命名空间（正式生产流水线）
python my_flow.py argo-workflows create --production

# 触发 production 版本
python my_flow.py argo-workflows trigger --production
```

`--production` 的作用：
- Flow 的 Runs 记录在 **production 命名空间**，与开发/测试 Runs 分开
- 适合正式的定时任务和对外 SLA 承诺的流水线

### `--branch` 标志（多版本并行）

```bash
# 部署特性分支（不影响 production 流水线）
python my_flow.py argo-workflows create --branch feature-new-model

# 触发特性分支版本
python my_flow.py argo-workflows trigger --branch feature-new-model
```

`--branch` 的作用：
- 为同一个 Flow 的不同版本创建独立的命名空间
- 实现 A/B 测试、灰度发布、并行实验
- 不影响 `--production` 版本的运行

---

## `@project` 装饰器

`@project` 用于组织多个相关 Flow，并控制命名空间隔离。

```python
from metaflow import FlowSpec, step, project, schedule

@project(name="recommendation-system")
@schedule(daily=True)
class TrainingFlow(FlowSpec):
    
    @step
    def start(self):
        ...
    
    @step
    def end(self):
        ...
```

**`@project` 的 namespace 影响：**

| 部署命令 | 命名空间格式 |
|---------|------------|
| `argo-workflows create` | `recommendation-system.user.TrainingFlow` |
| `argo-workflows create --production` | `recommendation-system.production` |
| `argo-workflows create --branch exp-v2` | `recommendation-system.branch.exp-v2` |

**多个 Flow 共享 `@project`：**

```python
# training_flow.py
@project(name="my-ml-project")
class TrainingFlow(FlowSpec):
    ...

# inference_flow.py
@project(name="my-ml-project")
class InferenceFlow(FlowSpec):
    ...

# 两个 Flow 在同一 project 命名空间下，可以互相访问对方的 Artifacts
from metaflow import Flow, namespace
namespace("my-ml-project.production")
run = Flow("TrainingFlow").latest_successful_run
model = run.data.model
```

---

## `@schedule` 定时触发

```python
from metaflow import FlowSpec, step, schedule

# 每周日午夜执行
@schedule(weekly=True)
class WeeklyReportFlow(FlowSpec):
    ...

# 每天午夜执行
@schedule(daily=True)
class DailyBatchFlow(FlowSpec):
    ...

# 每小时执行
@schedule(hourly=True)
class HourlyMonitorFlow(FlowSpec):
    ...

# 自定义 Cron 表达式（Oracle cron 语法）
# 每周一到周五 上午 10:00 UTC 执行
@schedule(cron='0 10 * * ? *')
class WorkdayFlow(FlowSpec):
    ...
```

**`@schedule` 生效条件：**
- 必须将 Flow 部署到 Argo Workflows（`argo-workflows create`）后才会生效
- 本地 `run` 不会触发调度
- Argo Workflows 内置的 CronWorkflow 处理调度逻辑

---

## `@trigger` 事件触发

`@trigger` 允许 Flow 响应外部事件（另一个 Flow 完成、消息队列事件等）。

```python
from metaflow import FlowSpec, step, trigger

# 当 FeatureFlow 的 production 版本完成时，自动触发本 Flow
@trigger(flow="FeatureFlow")
class TrainingFlow(FlowSpec):
    ...

# 当指定 Flow 的特定 tag 版本完成时触发
@trigger(flow="DataPipelineFlow", tag="nightly")
class ModelTrainingFlow(FlowSpec):
    ...
```

**典型事件驱动架构：**

```
数据摄取 Flow
    ↓  完成事件
特征工程 Flow（@trigger(flow="DataIngestionFlow")）
    ↓  完成事件
模型训练 Flow（@trigger(flow="FeatureEngineeringFlow")）
    ↓  完成事件
模型评估 Flow（@trigger(flow="ModelTrainingFlow")）
```

---

## XGBoost Sensor/Event 模式

对于需要监控外部数据更新（如 S3 文件到达）的场景，可以用 Sensor Flow 模式：

```python
from metaflow import FlowSpec, step, schedule, trigger_on_finish

# Sensor Flow 定期检查数据是否更新
@schedule(hourly=True)
class DataSensorFlow(FlowSpec):
    
    @step
    def start(self):
        # 检查新数据是否到达
        self.has_new_data = check_for_new_data()
        self.next(self.trigger_training if self.has_new_data else self.end)
    
    @step
    def trigger_training(self):
        # 触发训练流水线
        ...
        self.next(self.end)
    
    @step
    def end(self):
        pass
```

---

## CI/CD 集成

### GitHub Actions 自动部署

```yaml
# .github/workflows/deploy-flow.yml
name: Deploy Production Flow

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -U outerbounds
          pip install -r requirements.txt
      
      - name: Configure Outerbounds
        run: outerbounds configure --machine-user
        # Machine User 通过 GitHub OIDC 认证
      
      - name: Deploy to Production
        run: |
          python training_flow.py \
            --environment=fast-bakery \
            argo-workflows create \
            --production
```

### 分支部署策略

```yaml
# 特性分支：部署为 branch 版本
- name: Deploy Feature Branch
  if: github.ref != 'refs/heads/main'
  run: |
    BRANCH_NAME=${GITHUB_REF#refs/heads/}
    python training_flow.py \
      --environment=fast-bakery \
      argo-workflows create \
      --branch $BRANCH_NAME

# main 分支：部署为 production
- name: Deploy Production
  if: github.ref == 'refs/heads/main'
  run: |
    python training_flow.py \
      --environment=fast-bakery \
      argo-workflows create \
      --production
```

---

## Argo Workflows UI

Argo Workflows 自带 Web UI，但默认不对外暴露。访问方式：

```bash
# 通过 kubectl port-forward 访问 Argo UI
kubectl port-forward -n argo service/argo-argo-workflows-server 2746:2746

# 然后在浏览器访问：http://localhost:2746
```

Outerbounds UI 中的 **Runs** 视图集成了主要的 Workflow 监控功能，通常无需直接访问 Argo UI。

---

## 其他调度后端

### AWS Step Functions

```bash
# 部署到 Step Functions（需要在 metaflowconfig 中配置 SFN 相关参数）
python my_flow.py step-functions create
python my_flow.py step-functions trigger
```

### Apache Airflow

```bash
# 编译为 Airflow DAG 文件
python my_flow.py airflow create my_flow_dag.py

# 将生成的 DAG 文件复制到 Airflow DAGs 目录
cp my_flow_dag.py $AIRFLOW_HOME/dags/

# 注意事项：
# - 仅支持 @kubernetes 计算层（不支持 @batch）
# - 最低 Airflow 版本要求 2.2.0
# - foreach 功能需要 Airflow 2.3.0+
# - @project 装饰器保证 dag_id 唯一性
```

---

## 参考资料

- [Schedule Flows on Argo Workflows](https://docs.outerbounds.com/schedule-flow-on-argo/)
- [Using Airflow with Metaflow](https://docs.outerbounds.com/engineering/operations/airflow/)
- [XGBoost Batch Inference 示例](https://docs.outerbounds.com/outerbounds/xgboost/)

*最后更新：2026-04-13*
