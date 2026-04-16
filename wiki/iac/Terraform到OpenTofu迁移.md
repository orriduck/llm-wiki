---
tags: [opentofu, terraform, migration, iac]
---

# Migrating from Terraform to OpenTofu / 从 Terraform 迁移到 OpenTofu

## Overview / 概述

Migrating from Terraform to OpenTofu is designed to be low-risk. For most projects on Terraform ≤ 1.5.x, it is a drop-in replacement — no HCL rewrites needed. The migration path diverges slightly if you are on Terraform 1.6+ (post-BSL).

> 从 Terraform 迁移到 OpenTofu 的设计目标是低风险。对于大多数运行在 Terraform ≤ 1.5.x 上的项目，这是一个即插即用的替换——无需重写 HCL。如果你使用的是 Terraform 1.6+（BSL 之后），迁移路径略有不同。

---

## Pre-Migration Checklist / 迁移前检查清单

Before starting, verify the following:

> 开始之前，请确认以下事项：

- [ ] **Terraform version:** Check current version with `terraform version`. Versions ≤ 1.5.x migrate most cleanly.
- [ ] **State backend:** Know where your state lives (local file, S3, Terraform Cloud/HCP, etc.)
- [ ] **State backup:** Always create a manual backup of `terraform.tfstate` before migrating.
- [ ] **Provider versions:** Note any provider version pins in `required_providers`.
- [ ] **Team alignment:** All team members need to switch simultaneously to avoid state conflicts.
- [ ] **CI/CD pipelines:** Identify all places that call `terraform` (GitHub Actions, Jenkins, Atlantis, etc.).

> - [ ] **Terraform 版本：** `terraform version` 确认当前版本。≤ 1.5.x 迁移最顺畅。
> - [ ] **State 后端：** 确认 state 存储位置（本地文件、S3、Terraform Cloud/HCP 等）。
> - [ ] **State 备份：** 迁移前务必手动备份 `terraform.tfstate`。
> - [ ] **Provider 版本：** 记录 `required_providers` 中的版本约束。
> - [ ] **团队同步：** 所有成员需同时切换，避免 state 冲突。
> - [ ] **CI/CD 流水线：** 找出所有调用 `terraform` 的位置（GitHub Actions、Jenkins、Atlantis 等）。

---

## Step 1: Install OpenTofu / 第一步：安装 OpenTofu

### macOS (Homebrew)

```bash
brew install opentofu
tofu version   # verify
```

### Linux (Official Installer)

```bash
# Install via the official install script
curl --proto '=https' --tlsv1.2 -fsSL https://get.opentofu.org/install-opentofu.sh | \
  sh -s -- --install-method standalone

tofu version
```

### Linux (APT / DEB — Ubuntu/Debian)

```bash
# Add OpenTofu GPG key and repo
curl -fsSL https://packages.opentofu.org/opentofu/tofu/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/opentofu-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) \
  signed-by=/usr/share/keyrings/opentofu-archive-keyring.gpg] \
  https://packages.opentofu.org/opentofu/tofu/any/ any main" | \
  sudo tee /etc/apt/sources.list.d/opentofu.list > /dev/null

sudo apt-get update && sudo apt-get install -y tofu
```

### Using tfenv / tofuenv

```bash
# tofuenv is the OpenTofu equivalent of tfenv
git clone https://github.com/tofuutils/tofuenv.git ~/.tofuenv
export PATH="$HOME/.tofuenv/bin:$PATH"

tofuenv install latest
tofuenv use latest
```

> **注意：** `tofu` 是 OpenTofu 的命令行二进制，替代 `terraform`。两者命令语法完全相同，只是前缀不同。

---

## Step 2: Backup State / 第二步：备份 State

### Local state / 本地 state

```bash
cp terraform.tfstate terraform.tfstate.bak-$(date +%Y%m%d)
```

### S3 backend / S3 后端

```bash
# Enable versioning on the state bucket (if not already)
aws s3api put-bucket-versioning \
  --bucket <your-state-bucket> \
  --versioning-configuration Status=Enabled

# Download a local backup
aws s3 cp s3://<your-state-bucket>/path/to/terraform.tfstate \
  ./terraform.tfstate.bak-$(date +%Y%m%d)
```

> **黄金法则：** 备份完成前不要继续下一步。State 文件损坏意味着 Terraform/OpenTofu 不再知道哪些资源已经部署，恢复代价极高。

---

## Step 3: Run `tofu init` / 第三步：运行 `tofu init`

In your existing Terraform project directory, run:

> 在现有 Terraform 项目目录中运行：

```bash
tofu init
```

This re-downloads provider plugins using OpenTofu's own plugin cache. The existing HCL files and state file are used as-is — **no changes to `.tf` files are required at this step.**

> 此命令使用 OpenTofu 自己的插件缓存重新下载 provider 插件。现有的 HCL 文件和 state 文件原样使用——**此步骤不需要修改 `.tf` 文件。**

You should see output like:

> 应该看到类似输出：

```
Initializing the backend...
Initializing provider plugins...
- Reusing previous version of hashicorp/aws v5.x.x
- Using previously-installed hashicorp/aws v5.x.x

OpenTofu has been successfully initialized!
```

---

## Step 4: Validate and Plan / 第四步：验证与预览

```bash
tofu validate   # check HCL syntax
tofu plan       # should show "No changes" if nothing has drifted
```

If `tofu plan` shows no changes, your migration is complete for this workspace. The state is now being managed by OpenTofu.

> 如果 `tofu plan` 显示"No changes"，说明该工作区迁移已完成。State 现在由 OpenTofu 管理。

**If you see unexpected changes:** This can happen due to provider version differences. Pin your provider versions explicitly:

> **如果看到意外变更：** 可能是 provider 版本差异导致。明确固定 provider 版本：

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 5.31.0"   # pin to exact version used before migration
    }
  }
}
```

---

## Step 5: Update CI/CD Pipelines / 第五步：更新 CI/CD 流水线

Replace `terraform` with `tofu` everywhere in your automation:

> 在所有自动化脚本中将 `terraform` 替换为 `tofu`：

### GitHub Actions Example / GitHub Actions 示例

```yaml
# Before / 迁移前
- name: Terraform Init
  run: terraform init

- name: Terraform Plan
  run: terraform plan -out=tfplan

- name: Terraform Apply
  run: terraform apply tfplan
```

```yaml
# After / 迁移后
- name: Setup OpenTofu
  uses: opentofu/setup-opentofu@v1
  with:
    tofu_version: "1.8.x"

- name: OpenTofu Init
  run: tofu init

- name: OpenTofu Plan
  run: tofu plan -out=tfplan

- name: OpenTofu Apply
  run: tofu apply tfplan
```

### Atlantis / Atlantis

In your `atlantis.yaml` or Atlantis server config:

> 在 `atlantis.yaml` 或 Atlantis 服务端配置中：

```yaml
# atlantis.yaml
version: 3
projects:
  - dir: infra/
    terraform_version: tofu1.8.0   # specify OpenTofu version
    workflow: opentofu

workflows:
  opentofu:
    plan:
      steps:
        - init
        - plan
    apply:
      steps:
        - apply
```

> Atlantis v0.27+ 原生支持 OpenTofu，通过 `--tofu-version` 标志或 `atlantis.yaml` 中的 `terraform_version: tofuX.Y.Z` 指定。

---

## Step 6: Update `required_version` / 第六步：更新 `required_version`

Change the `required_version` constraint in your `versions.tf` to reflect OpenTofu:

> 修改 `versions.tf` 中的 `required_version` 约束：

```hcl
# Before / 迁移前
terraform {
  required_version = ">= 1.5.0"
  ...
}
```

```hcl
# After / 迁移后
terraform {
  required_version = ">= 1.6.0"   # OpenTofu 1.6+ compatible
  ...
}
```

> **注意：** OpenTofu 和 Terraform 共享 `terraform {}` 块语法（OpenTofu 不使用 `opentofu {}` 块，保持向后兼容）。

---

## Migrating from Terraform Cloud / HCP Terraform / 从 Terraform Cloud / HCP Terraform 迁移

If your state backend is Terraform Cloud (now HCP Terraform), you need to migrate the state to a different backend first.

> 如果 state 后端是 Terraform Cloud（现为 HCP Terraform），需要先将 state 迁移到其他后端。

### Step 1: Export state from TFC / 从 TFC 导出 state

```bash
# Using Terraform CLI while still pointing to TFC
terraform state pull > terraform.tfstate.exported
```

### Step 2: Reconfigure backend to S3 / 重新配置后端为 S3

```hcl
terraform {
  backend "s3" {
    bucket         = "<your-state-bucket>"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

### Step 3: Push state to new backend / 推送 state 到新后端

```bash
tofu init -migrate-state
# Terraform prompts you to copy existing state to the new backend
```

> TFC/HCP Terraform 与 OpenTofu 不直接兼容（HCP Terraform 是 HashiCorp 专有服务）。替代方案包括：**Spacelift**、**env0**、**Scalr** 或自托管 Atlantis + S3 后端。

---

## Handling Terraform 1.6+ State Files / 处理 Terraform 1.6+ 的 State 文件

Terraform 1.6+ added a new `terraform_version` field in the state file. OpenTofu 1.6+ can read these state files, but you may see a warning. To suppress it and formally transfer ownership:

> Terraform 1.6+ 在 state 文件中新增了 `terraform_version` 字段。OpenTofu 1.6+ 可以读取这些文件，但可能出现警告。要正式转移所有权：

```bash
# After tofu init, force a state re-write
tofu state push terraform.tfstate
```

Or use `tofu state replace-provider` if provider namespaces changed:

> 或者在 provider 命名空间变化时使用 `tofu state replace-provider`：

```bash
tofu state replace-provider registry.terraform.io/hashicorp/aws registry.opentofu.org/hashicorp/aws
```

> 实际上大多数情况下 provider 注册表地址相同，此步骤不必要；OpenTofu 默认从 `registry.terraform.io` 拉取 provider，与 Terraform 完全一致。

---

## Rollback Plan / 回滚方案

If something goes wrong after migration:

> 如果迁移后出现问题：

```bash
# Restore backed-up state
cp terraform.tfstate.bak-YYYYMMDD terraform.tfstate

# Or restore from S3 versioning
aws s3api list-object-versions \
  --bucket <your-state-bucket> \
  --prefix path/to/terraform.tfstate

aws s3api get-object \
  --bucket <your-state-bucket> \
  --key path/to/terraform.tfstate \
  --version-id <version-id> \
  terraform.tfstate.restored
```

Then switch back to `terraform` binary. Because state files are backward-compatible, reverting is safe.

> 然后切换回 `terraform` 二进制。由于 state 文件向后兼容，回滚是安全的。

---

## Post-Migration: Enable State Encryption / 迁移后：启用状态加密

Once on OpenTofu 1.7+, take advantage of native state encryption:

> 迁移到 OpenTofu 1.7+ 后，可以启用原生 state 加密：

```hcl
terraform {
  encryption {
    key_provider "aws_kms" "state_key" {
      kms_key_id = var.kms_key_id   # from var, not hardcoded
      region     = var.aws_region
    }

    method "aes_gcm" "default" {
      keys = key_provider.aws_kms.state_key
    }

    state {
      method = method.aes_gcm.default
      # enforced = true  # uncomment to reject unencrypted state
    }

    plan {
      method = method.aes_gcm.default
    }
  }
}
```

> **警告：** 启用加密后，未启用加密的机器将无法读取 state 文件。团队所有成员和 CI/CD 系统都需要访问相同的 KMS Key，并统一更新配置。建议先在非生产环境验证。

---

## Migration Complexity Matrix / 迁移复杂度矩阵

| Scenario / 场景 | Complexity / 复杂度 | Notes / 说明 |
|---|---|---|
| Local state, Terraform ≤ 1.5 | ⭐ Trivial / 极简 | Just swap binary + `tofu init` |
| S3 backend, Terraform ≤ 1.5 | ⭐ Trivial / 极简 | Same |
| S3 backend, Terraform 1.6–1.9 | ⭐⭐ Easy / 简单 | `tofu init`, watch for plan drift |
| Terraform Cloud backend | ⭐⭐⭐ Medium / 中等 | Migrate backend first |
| Sentinel policies | ⭐⭐⭐⭐ Hard / 较难 | No direct equivalent; use OPA/Conftest |
| Large monorepo with 50+ workspaces | ⭐⭐⭐ Medium / 中等 | Script the migration per workspace |

---

## See Also / 相关页面

- [[Terraform基础与AWS部署]] — Terraform fundamentals and AWS examples
- [[OpenTofu简介与优势]] — Why OpenTofu, feature comparison, and license analysis
