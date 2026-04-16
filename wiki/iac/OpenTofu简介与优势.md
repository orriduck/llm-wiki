---
tags: [opentofu, terraform, iac, open-source]
---

# OpenTofu: Introduction & Advantages over Terraform / OpenTofu 简介与相比 Terraform 的优势

## Background / 背景

In August 2023, HashiCorp announced that Terraform — previously licensed under the Mozilla Public License 2.0 (MPL 2.0, open-source) — would switch to the **Business Source License (BSL 1.1)**. Under BSL, competitors cannot use the source code to build competing products without a commercial agreement. This change alarmed the community that had built an entire ecosystem around Terraform.

> 2023 年 8 月，HashiCorp 宣布将 Terraform 的许可证从 Mozilla Public License 2.0（开源）切换为**Business Source License（BSL 1.1）**。BSL 下，竞争者不得在未签商业协议的情况下使用源码构建竞品。这一变更引发了整个 Terraform 生态社区的强烈反应。

In response, a coalition of companies (Gruntwork, Spacelift, env0, Harness, Scalr, and others) forked Terraform at its last MPL 2.0 commit and created **OpenTofu** under the Linux Foundation. OpenTofu 1.6.0 was released in January 2024 as the first stable release.

> 作为回应，Gruntwork、Spacelift、env0、Harness、Scalr 等公司联合在最后一个 MPL 2.0 版本处分叉，在 Linux Foundation 旗下创建了 **OpenTofu**。2024 年 1 月，OpenTofu 1.6.0 作为首个稳定版本发布。

---

## License: The Core Difference / 许可证：核心区别

| | Terraform (post-1.5) | OpenTofu |
|---|---|---|
| License / 许可证 | BSL 1.1 (source-available) | Mozilla Public License 2.0 (open-source) |
| Can competitors use it? / 竞争者能使用吗？ | No / 否 | Yes / 是 |
| Governed by / 治理方 | HashiCorp / IBM | Linux Foundation |
| Community PRs? / 社区 PR？ | HashiCorp decides / HashiCorp 决定 | Open governance / 开放治理 |

BSL 1.1 has a "Change Date" after which the code converts to GPL — but for Terraform, that is 4 years from each file's release date, making it effectively proprietary for years.

> BSL 1.1 设有"Change Date"，届时代码将转为 GPL，但对 Terraform 而言是每个文件发布日起 4 年后，实际上相当于数年内是专有软件。

---

## Advantages of OpenTofu / OpenTofu 的优势

### 1. Truly Open-Source License / 真正的开源许可证

MPL 2.0 is a well-understood copyleft license with clear terms. You can fork, modify, redistribute, and build commercial products on top of OpenTofu without restriction. There is no risk of a future license change by a single corporate owner.

> MPL 2.0 是条款清晰的弱著佐权许可证。你可以自由 fork、修改、再发行，并在其之上构建商业产品，不受限制。也不存在单一企业主私自修改许可证的风险。

### 2. Open Governance / 开放治理

OpenTofu is governed by the Linux Foundation with a Technical Steering Committee (TSC) composed of representatives from multiple companies. No single vendor controls the roadmap.

> OpenTofu 由 Linux Foundation 治理，设有技术指导委员会（TSC），成员来自多家公司。没有单一厂商控制路线图。

### 3. Faster Feature Iteration / 更快的功能迭代

Since the BSL change, Terraform's open contribution model has effectively closed. OpenTofu merges community PRs more aggressively and has shipped features ahead of Terraform, including:

> BSL 变更后，Terraform 的开放贡献模式实际上已关闭。OpenTofu 更积极地合并社区 PR，已有多项功能领先于 Terraform 发布，包括：

- **State encryption** (`var.` references in provider configs): built-in AES-GCM or AWS KMS/GCP KMS encryption of the state file at rest — no more plaintext secrets in remote state.

  > **状态加密**：内置 AES-GCM 或 AWS KMS/GCP KMS 的 state 文件静态加密，远程 state 中不再有明文密钥。

- **Provider-defined functions**: providers can ship HCL functions (e.g. `provider::aws::arn_parse()`), not just resources.

  > **Provider 自定义函数**：provider 可以随带 HCL 函数（如 `provider::aws::arn_parse()`），而不仅是资源。

- **`removed` block**: cleanly remove a resource from state without destroying it — useful for refactors.

  > **`removed` 块**：从 state 中移除资源但不销毁，适合重构场景。

- **Loopable `import` blocks**: use `for_each` on `import` blocks to bulk-import resources.

  > **可循环的 `import` 块**：在 `import` 块上使用 `for_each` 批量导入资源。

### 4. State Encryption (Killer Feature) / 状态加密（杀手级特性）

OpenTofu 1.7+ ships native state encryption. No external tooling required.

> OpenTofu 1.7+ 原生支持状态加密，无需外部工具。

```hcl
terraform {
  encryption {
    key_provider "pbkdf2" "my_passphrase" {
      passphrase = var.state_encryption_passphrase
    }

    method "aes_gcm" "default_method" {
      keys = key_provider.pbkdf2.my_passphrase
    }

    state {
      method = method.aes_gcm.default_method
    }

    plan {
      method = method.aes_gcm.default_method
    }
  }
}
```

Or using AWS KMS:

> 也可使用 AWS KMS：

```hcl
terraform {
  encryption {
    key_provider "aws_kms" "my_key" {
      kms_key_id = "arn:aws:kms:us-east-1:<account-id>:key/<key-id>"
      region     = "us-east-1"
    }

    method "aes_gcm" "kms_method" {
      keys = key_provider.aws_kms.my_key
    }

    state {
      method = method.aes_gcm.kms_method
    }
  }
}
```

### 5. No Vendor Lock-in Risk / 无厂商锁定风险

HashiCorp was acquired by IBM in 2024. Corporate priorities may shift. With OpenTofu (Linux Foundation), the project cannot be unilaterally shut down, re-licensed, or pivoted by a single acquirer.

> HashiCorp 于 2024 年被 IBM 收购，企业优先级可能随时变化。OpenTofu 归属 Linux Foundation，项目不会被单一收购方单方面关闭、重新授权或转向。

### 6. Drop-in Compatibility / 即插即用兼容性

OpenTofu is a near-perfect drop-in replacement for Terraform ≤ 1.5.x. Most codebases migrate with a single binary swap and a `tofu init`.

> OpenTofu 是 Terraform ≤ 1.5.x 的近乎完美的替代品。大多数代码库只需替换二进制文件并运行 `tofu init` 即可完成迁移。

---

## Feature Comparison / 功能对比

| Feature / 功能 | Terraform 1.9 | OpenTofu 1.8 |
|---|---|---|
| License / 许可证 | BSL 1.1 | MPL 2.0 ✅ |
| State encryption / 状态加密 | ❌ (needs Vault/external) | ✅ native |
| Provider-defined functions / Provider 函数 | Limited / 有限 | ✅ full support |
| `removed` block | ✅ (added in 1.7) | ✅ |
| Loopable `import` | Partial / 部分 | ✅ |
| Community governance / 社区治理 | ❌ HashiCorp-controlled | ✅ Linux Foundation |
| HCP Terraform integration / HCP 集成 | ✅ native | Via third-party / 第三方 |
| Terraform Registry | ✅ | ✅ (same registry) |
| `terraform` binary → `tofu` binary | — | Renamed / 已重命名 |

---

## Ecosystem & Tooling Support / 生态与工具支持

Most major tools in the Terraform ecosystem now support OpenTofu:

> Terraform 生态中的主要工具现已支持 OpenTofu：

- **Terragrunt** — supports `--tofu` flag; Gruntwork (author) is an OpenTofu founding member
- **Atlantis** — `--tofu-version` flag
- **Checkov / tfsec / tflint** — updated to parse OpenTofu configurations
- **Spacelift, env0, Scalr** — native OpenTofu support
- **Terraform Registry** — OpenTofu uses the same public registry (registry.terraform.io), modules and providers work without changes

> - **Terragrunt**：支持 `--tofu` 标志；Gruntwork（作者）是 OpenTofu 创始成员
> - **Atlantis**：`--tofu-version` 标志
> - **Checkov / tfsec / tflint**：已更新以解析 OpenTofu 配置
> - **Spacelift, env0, Scalr**：原生 OpenTofu 支持
> - **Terraform Registry**：OpenTofu 使用相同的公共 Registry，模块和 provider 无需修改

---

## When to Stick with Terraform / 什么情况下继续使用 Terraform

OpenTofu is the better choice for most new projects. However, Terraform still makes sense if:

> 大多数新项目 OpenTofu 是更好的选择。但以下情况仍推荐 Terraform：

- Your organization has an existing **HCP Terraform** (Terraform Cloud) subscription and is deeply integrated with it
- You require **Sentinel policy-as-code** (HCP Terraform-exclusive)
- Your compliance team has already approved Terraform's BSL and the legal review cost of switching isn't justified

> - 组织已有深度集成的 **HCP Terraform**（Terraform Cloud）订阅
> - 需要 **Sentinel 策略即代码**（仅 HCP Terraform）
> - 合规团队已批准 BSL，切换的法务审查成本不合算

---

## See Also / 相关页面

- [[Terraform基础与AWS部署]] — Terraform fundamentals and AWS examples
- [[Terraform到OpenTofu迁移]] — Step-by-step migration guide
