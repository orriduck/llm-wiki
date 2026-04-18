# Lambda Layer Docker 构建与冷启动配置模式

> 来源：通过 lizard 从 Claude 会话蒸馏 · 2026-04-18

## 核心概念

AWS Lambda Layer 是一种将依赖与函数代码分离的机制。使用 Docker 基于 Lambda 官方 Python runtime 镜像来构建 layer，可确保二进制兼容性（如 C 扩展库在 Amazon Linux 上的编译）。同时，敏感配置可在冷启动阶段从 Secrets Manager 动态读取，避免在构建时嵌入凭证。

> AWS Lambda Layers separate dependencies from function code. Building layers with Docker using the official Lambda Python runtime image ensures binary compatibility. Sensitive configuration can be loaded from Secrets Manager at cold start, avoiding credential embedding at build time.

## Layer 构建脚本模式

```bash
#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 无论成功或失败，清理中间文件
trap 'rm -rf "${SCRIPT_DIR}/.python"' EXIT

docker run --rm \
  -v "${SCRIPT_DIR}:/build" \
  --entrypoint /bin/bash \
  public.ecr.aws/lambda/python:3.12 \
  -c "pip install -r /build/requirements.txt -t /build/.python/python --quiet"

cd "${SCRIPT_DIR}/.python"
zip -r "${SCRIPT_DIR}/layer.zip" python/ --quiet
echo "Built layer.zip ($(du -sh "${SCRIPT_DIR}/layer.zip" | cut -f1))"
```

> Key points:
> - `trap ... EXIT` ensures `.python/` cleanup even on failure
> - Use the official `public.ecr.aws/lambda/python:3.12` image for binary compatibility
> - Install to `.python/python/` so Lambda can find packages at `/opt/python/`

### 关键细节

| 要点 | 说明 |
|------|------|
| `trap ... EXIT` | 确保中间目录（`.python/`）在构建失败时也被清理 |
| `public.ecr.aws/lambda/python:3.12` | 官方 Lambda runtime 镜像，确保 C 扩展的 ABI 兼容 |
| 安装目标 `.python/python/` | Lambda 运行时将 Layer 挂载在 `/opt`，Python 会在 `/opt/python/` 搜索包 |
| `--entrypoint /bin/bash` | 覆盖 Lambda 镜像默认入口，直接执行 shell 命令 |
| `zip` 工具 | Lambda 镜像中默认不含 `zip`；如需在容器内打包，先 `yum install -y zip` |

> The Lambda base image doesn't include `zip` by default. Either install it inside the container (`yum install -y zip`) or zip outside the container after the Docker run.

## 冷启动配置加载模式

将敏感配置（API 密钥、SDK 配置字符串等）存入 AWS Secrets Manager，Lambda 冷启动时读取并初始化：

```python
import json
import os
import subprocess
import boto3

# 冷启动时执行一次
_config = None

def _load_config():
    global _config
    if _config is not None:
        return _config

    sm = boto3.client("secretsmanager")
    resp = sm.get_secret_value(SecretId=os.environ["CONFIG_SECRET_NAME"])
    _config = json.loads(resp["SecretString"])

    # 例：运行 SDK 配置命令
    if "CONFIGURE_STRING" in _config:
        subprocess.run(
            ["some-cli", "configure", _config["CONFIGURE_STRING"]],
            check=True,
            env={**os.environ, "CONFIG_HOME": "/tmp/config"},
        )
    return _config

def handler(event, context):
    config = _load_config()
    # ... 使用 config 处理事件
```

> The pattern: module-level `_config` variable initialized on first invocation (cold start). Subsequent warm invocations reuse the cached config. Use `/tmp/` for any writable state — it's the only writable path in Lambda.

### 关键细节

| 要点 | 说明 |
|------|------|
| 模块级缓存 `_config` | 冷启动时初始化一次，warm invocation 复用 |
| `/tmp/` 目录 | Lambda 唯一可写路径，用于存放运行时生成的配置文件 |
| `CONFIG_SECRET_NAME` 环境变量 | 通过 Terraform 注入 Secret ARN/名称 |
| IAM 权限 | Lambda 执行角色需要 `secretsmanager:GetSecretValue` 权限 |

## Terraform 配置示例

```hcl
resource "aws_lambda_layer_version" "deps" {
  filename            = "${path.module}/lambda/layer/layer.zip"
  layer_name          = "my-function-deps"
  compatible_runtimes = ["python3.12"]
  source_code_hash    = filebase64sha256("${path.module}/lambda/layer/layer.zip")
}

resource "aws_lambda_function" "my_function" {
  function_name = "my-function"
  runtime       = "python3.12"
  handler       = "handler.handler"
  timeout       = 30
  memory_size   = 256

  filename         = data.archive_file.handler.output_path
  source_code_hash = data.archive_file.handler.output_base64sha256

  layers = [aws_lambda_layer_version.deps.arn]

  environment {
    variables = {
      CONFIG_SECRET_NAME = aws_secretsmanager_secret.config.name
      CONFIG_HOME        = "/tmp/config"
    }
  }
}
```

> Use `source_code_hash` on both the function and layer to trigger redeployment when code changes. Environment variables bridge Terraform-managed resources (secret names) to runtime code.

## pre-commit Hook 集成

可配置 pre-commit hook，在依赖变更时自动重新构建 layer：

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: build-lambda-layer
        name: Rebuild Lambda layer
        entry: bash lambda/layer/build.sh
        language: system
        files: 'lambda/layer/(requirements\.txt|build\.sh)$'
        pass_filenames: false
```

> This hook only triggers when `requirements.txt` or `build.sh` changes, keeping commits fast for unrelated changes.

## 注意事项

- Layer zip 体积上限 250MB（解压后）；超过需考虑 Docker image 部署方式
- `zip` 创建临时文件（如 `ziAB9dgD`）——正常行为，完成后自动清理
- `.python/` 目录应加入 `.gitignore` 作为安全网
- 冷启动配置加载会增加首次调用延迟（Secrets Manager 读取约 50-100ms）

> Layer unzipped size limit is 250MB. Zip creates temporary files during archiving — these are normal and cleaned up automatically. Add `.python/` to `.gitignore` as a safety net.

## 相关链接

- [[Lambda]]
- [[S3-Lambda触发器]]
