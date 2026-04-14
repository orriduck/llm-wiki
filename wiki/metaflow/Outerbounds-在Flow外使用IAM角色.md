# Outerbounds：在 Flow 外使用 IAM 角色

> 不写 Metaflow Flow，直接在普通 Python 脚本或交互环境中使用 Outerbounds 平台颁发的任务角色（`obp-*-task`）访问 AWS 资源。

相关笔记：[[Outerbounds-认证与权限]] | [[Outerbounds-Perimeter]] | [[Outerbounds概览]]

---

## 结论

**可以**。Outerbounds 的 AWS 认证机制不依赖 Flow 运行上下文，只需要：

1. 本地 Metaflow 配置文件（`.metaflowconfig`）中有有效的 `SERVICE_URL` 和 `SERVICE_HEADERS`（API Key）
2. 能访问 Outerbounds 认证服务器（`auth.whoop.obp.outerbounds.com`）

`current.perimeter` 也在 Flow 外可用 —— 它在模块导入时就从配置文件的 `OBP_PERIMETER` 字段写入，不依赖 Flow 运行时。

---

## 认证链原理

```
本地调用 get_boto3_session()
    → 请求 auth.whoop.obp.outerbounds.com/generate/aws（携带 SERVICE_HEADERS API Key）
    → 认证服务器返回：JWT OIDC Token + task role ARN + 可选 CSPR role ARN
    → 写入 /tmp/obp_token.<hash> 作为 Web Identity Token 文件
    → 配置 AWS_CONFIG_FILE，设置两个 profile：
        - profile task（Web Identity → task role，如 obp-g29j8e-task）
        - profile cspr（task role → CSPR role，若配置了 CSPR）
    → 返回 boto3 Session
```

核心代码：`metaflow_extensions/outerbounds/plugins/__init__.py:get_boto3_session()`

---

## 角色命名规则（WHOOP mlp-prod）

| 角色 ARN | 用途 |
|---------|------|
| `arn:aws:iam::247681839910:role/obp-g29j8e-task` | Perimeter 基础任务角色 |
| `arn:aws:iam::247681839910:role/obp-g29j8e-task--*` | 按 project/namespace 创建的子角色（通配） |

`g29j8e` 是 perimeter 标识符，对应 S3 存储桶前缀 `obp-g29j8e-metaflow`。

`PERIMETER_BUCKET_ACCESS_ROLE`（用于访问 Outerbounds 管理的 S3 桶）存储在 SSM 路径：
`/outerbounds/perimeter/{perimeter}/runtime-config`

---

## 使用方法

### 方法一：`get_boto3_session()`（最底层）

```python
from metaflow_extensions.outerbounds.plugins import get_boto3_session

# 使用默认 task role（obp-g29j8e-task）或 CSPR role（若已配置）
session = get_boto3_session()
s3 = session.client('s3')

# 显式指定角色（在 task role 基础上再 assume 子角色）
session = get_boto3_session(
    role_arn='arn:aws:iam::247681839910:role/obp-g29j8e-task--my-project'
)
s3 = session.client('s3')
```

### 方法二：`get_aws_client()`（Outerbounds 封装的 Metaflow API）

```python
from metaflow import get_aws_client  # 实际走 ObpAuthProvider

s3 = get_aws_client('s3')

# 指定角色
s3 = get_aws_client('s3', role_arn='arn:aws:iam::247681839910:role/obp-g29j8e-task')
ssm = get_aws_client('ssm', client_params={'region_name': 'us-west-2'})
```

### 方法三：`OBP_ASSUME_ROLE_ARN` 环境变量

`@assume_role` 装饰器的底层机制就是设置这个环境变量。在 Flow 外同样有效：

```python
import os
os.environ['OBP_ASSUME_ROLE_ARN'] = 'arn:aws:iam::247681839910:role/obp-g29j8e-task'

from metaflow import get_aws_client, S3

s3_client = get_aws_client('s3')       # 自动使用该角色
sts = get_aws_client('sts')            # 同样生效
```

优先级：显式传入的 `role_arn` > `OBP_ASSUME_ROLE_ARN` 环境变量 > CSPR role

参考：`global_aliases_for_metaflow_package.py:57-93`

### 方法四：Metaflow `S3()` 客户端 + 显式角色

```python
from metaflow import S3  # Outerbounds 封装版本

with S3(
    role='arn:aws:iam::247681839910:role/obp-g29j8e-task',
    s3root='s3://obp-g29j8e-metaflow/'
) as s3:
    files = s3.list_paths()
    obj = s3.get('some/key')
```

### 方法五：`load_parameter()` 读取 Perimeter 配置

`current.perimeter` 在 Flow 外也是可用的（来自配置文件 `OBP_PERIMETER: default`），因此可以直接调用：

```python
from whoop_outerbounds.utils.systems_manager import load_parameter

config = load_parameter('/outerbounds/perimeter/default/runtime-config')
# 返回：
# {
#   "PERIMETER_BUCKET_ACCESS_ROLE": "arn:aws:iam::...",
#   "PERIMETER_BUCKETS": {"scratch": "obp-g29j8e-...", ...},
#   "PERIMETER_SWE_BUCKETS_ACCESS_ROLE": "...",
#   ...
# }

obj_role = config['PERIMETER_BUCKET_ACCESS_ROLE']
```

---

## 在 Flow 外不能用的

| 类/方法 | 原因 |
|--------|------|
| `WhoopS3(flow, ...)` | 显式要求传入 `flow` 对象，且内部依赖 `current.run`（`s3.py:170`） |
| `PerimeterConfigFlowDecorator` | 仅作为 Flow 装饰器使用，`flow_init()` 在 Flow 初始化时调用 |
| `_get_perimeter_config_from_flow(flow)` | 从 flow 对象上读取 `perimeter_config` 属性 |

---

## 配置参考（WHOOP mlp-prod）

```
OBP_PERIMETER: default
OBP_AUTH_SERVER: auth.whoop.obp.outerbounds.com
METAFLOW_SERVICE_URL: https://metadata.whoop.obp.outerbounds.com/p/default/
METAFLOW_DATASTORE_SYSROOT_S3: s3://obp-g29j8e-metaflow/metaflow
SSM 配置路径: /outerbounds/perimeter/default/runtime-config
```

---

*最后更新：2026-04-14*
