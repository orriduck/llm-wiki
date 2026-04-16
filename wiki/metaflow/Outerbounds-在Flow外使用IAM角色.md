# Outerbounds: Using IAM Roles Outside a Flow / 在 Flow 外使用 IAM 角色

> Use Outerbounds-issued task roles (`obp-*-task`) to access AWS resources from plain Python scripts or interactive environments — without writing a Metaflow Flow.
>
> 不写 Metaflow Flow，直接在普通 Python 脚本或交互环境中使用 Outerbounds 平台颁发的任务角色（`obp-*-task`）访问 AWS 资源。

Related / 相关笔记：[[Outerbounds-认证与权限]] | [[Outerbounds-Perimeter]] | [[Outerbounds概览]]

---

## Conclusion / 结论

**Yes, it works.** Outerbounds' AWS auth mechanism does not depend on a Flow runtime context. It only requires:

> **可以**。Outerbounds 的 AWS 认证机制不依赖 Flow 运行上下文，只需要：

1. A valid `SERVICE_URL` and `SERVICE_HEADERS` (API Key) in the local Metaflow config file (`.metaflowconfig`)
2. Network access to the Outerbounds auth server (e.g. `auth.<org>.obp.outerbounds.com`)

> 1. 本地 Metaflow 配置文件（`.metaflowconfig`）中有有效的 `SERVICE_URL` 和 `SERVICE_HEADERS`（API Key）
> 2. 能访问 Outerbounds 认证服务器（如 `auth.<org>.obp.outerbounds.com`）

`current.perimeter` is also available outside a Flow — it is set at module import time from the config file's `OBP_PERIMETER` field, not from the Flow runtime.

> `current.perimeter` 也在 Flow 外可用 —— 它在模块导入时就从配置文件的 `OBP_PERIMETER` 字段写入，不依赖 Flow 运行时。

---

## Auth Chain / 认证链原理

```
Local call to get_boto3_session()
    → Requests auth.<org>.obp.outerbounds.com/generate/aws (with SERVICE_HEADERS API Key)
    → Auth server returns: JWT OIDC Token + task role ARN + optional CSPR role ARN
    → Writes /tmp/obp_token.<hash> as Web Identity Token file
    → Configures AWS_CONFIG_FILE with two profiles:
        - profile task (Web Identity → task role, e.g. obp-<id>-task)
        - profile cspr (task role → CSPR role, if configured)
    → Returns boto3 Session
```

Core code: `metaflow_extensions/outerbounds/plugins/__init__.py:get_boto3_session()`

> 核心代码：`metaflow_extensions/outerbounds/plugins/__init__.py:get_boto3_session()`

---

## Role Naming Convention / 角色命名规则

| Role ARN / 角色 ARN | Purpose / 用途 |
|---------|------|
| `arn:aws:iam::<account-id>:role/obp-<perimeter-id>-task` | Perimeter base task role / Perimeter 基础任务角色 |
| `arn:aws:iam::<account-id>:role/obp-<perimeter-id>-task--*` | Sub-roles per project/namespace (wildcard) / 按 project/namespace 创建的子角色（通配） |

`<perimeter-id>` is the perimeter identifier, corresponding to S3 bucket prefix `obp-<perimeter-id>-metaflow`.

> `<perimeter-id>` 是 perimeter 标识符，对应 S3 存储桶前缀 `obp-<perimeter-id>-metaflow`。

`PERIMETER_BUCKET_ACCESS_ROLE` (for accessing Outerbounds-managed S3 buckets) is stored at SSM path:
`/outerbounds/perimeter/{perimeter}/runtime-config`

> `PERIMETER_BUCKET_ACCESS_ROLE`（用于访问 Outerbounds 管理的 S3 桶）存储在 SSM 路径：
> `/outerbounds/perimeter/{perimeter}/runtime-config`

---

## Usage Methods / 使用方法

### Method 1: `get_boto3_session()` (lowest level) / 方法一：`get_boto3_session()`（最底层）

```python
from metaflow_extensions.outerbounds.plugins import get_boto3_session

# Use default task role (obp-<id>-task) or CSPR role (if configured)
session = get_boto3_session()
s3 = session.client('s3')

# Explicitly specify a role (assume a sub-role on top of task role)
session = get_boto3_session(
    role_arn='arn:aws:iam::<account-id>:role/obp-<perimeter-id>-task--my-project'
)
s3 = session.client('s3')
```

### Method 2: `get_aws_client()` (Outerbounds wrapper) / 方法二：`get_aws_client()`（Outerbounds 封装的 Metaflow API）

```python
from metaflow import get_aws_client  # uses ObpAuthProvider under the hood

s3 = get_aws_client('s3')

# Specify a role
s3 = get_aws_client('s3', role_arn='arn:aws:iam::<account-id>:role/obp-<perimeter-id>-task')
ssm = get_aws_client('ssm', client_params={'region_name': 'us-west-2'})
```

### Method 3: `OBP_ASSUME_ROLE_ARN` environment variable / 方法三：`OBP_ASSUME_ROLE_ARN` 环境变量

The `@assume_role` decorator's underlying mechanism is setting this env var. It works outside a Flow too:

> `@assume_role` 装饰器的底层机制就是设置这个环境变量。在 Flow 外同样有效：

```python
import os
os.environ['OBP_ASSUME_ROLE_ARN'] = 'arn:aws:iam::<account-id>:role/obp-<perimeter-id>-task'

from metaflow import get_aws_client, S3

s3_client = get_aws_client('s3')       # automatically uses the role
sts = get_aws_client('sts')            # also works
```

Priority: explicit `role_arn` param > `OBP_ASSUME_ROLE_ARN` env var > CSPR role

> 优先级：显式传入的 `role_arn` > `OBP_ASSUME_ROLE_ARN` 环境变量 > CSPR role

Reference: `global_aliases_for_metaflow_package.py:57-93`

### Method 4: Metaflow `S3()` client with explicit role / 方法四：Metaflow `S3()` 客户端 + 显式角色

```python
from metaflow import S3  # Outerbounds-wrapped version

with S3(
    role='arn:aws:iam::<account-id>:role/obp-<perimeter-id>-task',
    s3root='s3://obp-<perimeter-id>-metaflow/'
) as s3:
    files = s3.list_paths()
    obj = s3.get('some/key')
```

### Method 5: `load_parameter()` to read Perimeter config / 方法五：`load_parameter()` 读取 Perimeter 配置

`current.perimeter` works outside a Flow (set from config file `OBP_PERIMETER: default`), so you can call directly:

> `current.perimeter` 在 Flow 外也是可用的（来自配置文件 `OBP_PERIMETER: default`），因此可以直接调用：

```python
from your_org.utils.systems_manager import load_parameter

config = load_parameter('/outerbounds/perimeter/default/runtime-config')
# Returns:
# {
#   "PERIMETER_BUCKET_ACCESS_ROLE": "arn:aws:iam::<account-id>:role/...",
#   "PERIMETER_BUCKETS": {"scratch": "obp-<perimeter-id>-...", ...},
#   "PERIMETER_SWE_BUCKETS_ACCESS_ROLE": "...",
#   ...
# }

obj_role = config['PERIMETER_BUCKET_ACCESS_ROLE']
```

---

## What Does NOT Work Outside a Flow / 在 Flow 外不能用的

| Class/Method / 类/方法 | Reason / 原因 |
|--------|------|
| `OrgS3(flow, ...)` | Requires a `flow` object and depends on `current.run` internally / 显式要求传入 `flow` 对象，且内部依赖 `current.run` |
| `PerimeterConfigFlowDecorator` | Only used as a Flow decorator; `flow_init()` is called during Flow initialization / 仅作为 Flow 装饰器使用，`flow_init()` 在 Flow 初始化时调用 |
| `_get_perimeter_config_from_flow(flow)` | Reads `perimeter_config` attribute from the flow object / 从 flow 对象上读取 `perimeter_config` 属性 |

---

## Config Reference / 配置参考

```
OBP_PERIMETER: default
OBP_AUTH_SERVER: auth.<org>.obp.outerbounds.com
METAFLOW_SERVICE_URL: https://metadata.<org>.obp.outerbounds.com/p/default/
METAFLOW_DATASTORE_SYSROOT_S3: s3://obp-<perimeter-id>-metaflow/metaflow
SSM config path: /outerbounds/perimeter/default/runtime-config
```

---

*Last updated / 最后更新：2026-04-15*
