# Outerbounds Branch Resolution / Outerbounds 分支解析机制

## What Branch Resolution Means / 什么是分支解析
In Outerbounds + Metaflow deployment workflows, branch resolution is the rule set that maps a runtime invocation to the exact deployed workflow namespace.

> 在 Outerbounds + Metaflow 部署流程中，分支解析是把一次运行请求映射到“具体已部署工作流命名空间”的规则集合。

## Namespace Model / 命名空间模型
A practical mental model is:

> 一个实用心智模型如下：

- Production deployment: `<project>.production`
  > 生产部署：`<project>.production`
- Branch deployment: `<project>.branch.<branch_name>`
  > 分支部署：`<project>.branch.<branch_name>`
- Local/default user namespace: user-scoped namespace for development
  > 本地/默认用户命名空间：开发阶段的用户隔离命名空间

This lets production and feature branches coexist without overwriting each other.

> 这样可以让生产版本和特性分支并存，而不会互相覆盖。

## Resolution Priority / 解析优先级
Typical priority in CI/CD and automation contexts:

> 在 CI/CD 与自动化场景中，常见优先级如下：

1. Explicit CLI flag (`--production` or `--branch <name>`)
   > 显式 CLI 参数（`--production` 或 `--branch <name>`）
2. Environment-derived branch name (for example from CI variables)
   > 来自环境变量的分支名（例如 CI 注入变量）
3. Fallback default (often production for main branch pipelines, otherwise branch mode)
   > 回退默认策略（主分支流水线通常走 production，其它分支通常走 branch 模式）

## Recommended CI Mapping / 推荐的 CI 映射策略
Use one deterministic mapping function:

> 建议使用单一确定性映射函数：

- `main` / `master` -> deploy with `--production`
  > `main` / `master` -> 使用 `--production` 部署
- non-main branches -> deploy with `--branch "$BRANCH_NAME"`
  > 非主分支 -> 使用 `--branch "$BRANCH_NAME"` 部署
- tags/releases -> pin to production namespace and immutable artifact versions
  > tag/release -> 固定到 production 命名空间并绑定不可变制品版本

## Failure Modes and Guards / 常见失败模式与防护
- Branch name normalization mismatch (e.g., `/` vs `-`) can create duplicate logical environments.
  > 分支名标准化不一致（如 `/` 与 `-`）会造成重复逻辑环境。
- Using both `--production` and `--branch` in different pipeline steps can lead to split deployments.
  > 在同一流水线不同步骤混用 `--production` 与 `--branch` 会导致部署分裂。
- Missing branch pinning in trigger step may run the wrong namespace.
  > 触发步骤未固定分支参数时，可能触发到错误命名空间。

Guardrails:

> 防护建议：

- Centralize branch resolution in one script (`resolve_deploy_mode.sh` or Python helper).
  > 把分支解析收敛到单一脚本（`resolve_deploy_mode.sh` 或 Python helper）。
- Log resolved mode + branch in every deploy and trigger step.
  > 在每个部署与触发步骤打印最终解析结果（mode + branch）。
- Add a policy check: main branch cannot deploy with `--branch`.
  > 增加策略校验：主分支禁止通过 `--branch` 部署。

## Minimal Checklist / 最小检查清单
- One source of truth for branch resolution.
  > 分支解析规则只有一个真源。
- Same mode used in both create/deploy and trigger phases.
  > create/deploy 与 trigger 阶段模式保持一致。
- Branch name sanitation documented and tested.
  > 分支名清洗规则有文档且有测试。
- Production path protected by branch and review rules.
  > production 路径受分支保护与评审策略约束。

## Related Pages / 相关页面
- [[Outerbounds-部署与调度]]
- [[Outerbounds-认证与权限]]
