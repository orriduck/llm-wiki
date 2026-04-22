# CircleCI Orb File Structure / CircleCI Orb 文件结构

## Why Structure Matters / 为什么结构重要
A clear orb repository structure makes authoring, packing, validating, and publishing reusable CI components predictable.

> 清晰的 orb 仓库结构可以让可复用 CI 组件的编写、打包、校验与发布更加可预测。

## Common Repository Layout / 常见仓库布局

```text
orb/
  src/
    @orb.yml
    commands/
      <command-name>.yml
    jobs/
      <job-name>.yml
    executors/
      <executor-name>.yml
    examples/
      <example-name>.yml
  dist/
    orb.yml
.circleci/
  config.yml
README.md
```

> 常见做法是用 `src/` 管理分片定义，通过打包生成 `dist/orb.yml`，并在 `.circleci/config.yml` 中做验证与发布流水线。

## Folder Responsibilities / 目录职责
- `src/@orb.yml`: orb metadata (description, display, high-level info).
  > `src/@orb.yml`：orb 元信息（描述、展示、基础信息）。
- `src/commands/`: reusable command units.
  > `src/commands/`：可复用命令单元。
- `src/jobs/`: higher-level jobs composed of commands/executors.
  > `src/jobs/`：由 commands/executors 组成的上层 job。
- `src/executors/`: runtime environments (docker/machine/macOS).
  > `src/executors/`：运行环境定义（docker/machine/macOS）。
- `src/examples/`: minimal usage snippets for registry docs.
  > `src/examples/`：用于注册页文档展示的最小使用示例。
- `dist/orb.yml`: packed artifact ready for validate/publish.
  > `dist/orb.yml`：可直接用于 validate/publish 的打包产物。

## Typical Authoring Workflow / 常见编写流程
1. Edit reusable pieces under `src/`.
   > 在 `src/` 下编辑可复用组件。
2. Pack into a single orb file.
   > 打包生成单文件 orb。
3. Validate packed orb.
   > 校验打包结果。
4. Publish dev version, test in downstream config.
   > 发布 dev 版本，并在下游配置中验证。
5. Promote to semantic release version.
   > 晋升为语义化正式版本。

## Design Conventions / 设计约定
- Keep commands small and composable.
  > command 保持小而可组合。
- Put policy (retries/timeouts/context) in jobs, not in every command.
  > 重试/超时/上下文等策略放在 job 层，不要散落到每个 command。
- Prefer explicit parameter names and defaults.
  > 参数命名与默认值尽量显式。
- Maintain one runnable example per command/job.
  > 每个 command/job 至少维护一个可运行示例。

## Versioning and Promotion / 版本与晋升
- `dev:*` tags for iteration and integration testing.
  > `dev:*` 标签用于快速迭代与集成测试。
- SemVer tags (`x.y.z`) for stable consumers.
  > 语义化版本（`x.y.z`）供稳定消费方使用。
- Promote only after downstream smoke tests pass.
  > 仅在下游冒烟测试通过后再晋升版本。

## Failure Modes and Guards / 常见失败模式与防护
- Drift between `src/` and `dist/orb.yml`.
  > `src/` 与 `dist/orb.yml` 漂移不一致。
- Hidden breaking changes from parameter rename/removal.
  > 参数重命名/删除导致隐性破坏性变更。
- Missing examples causing discoverability and adoption problems.
  > 缺少 examples 导致可发现性与采用率下降。

Guards:

> 防护建议：

- Repack + validate in CI for every PR.
  > 每个 PR 在 CI 中执行打包 + 校验。
- Add orb usage smoke tests in a consumer config.
  > 在消费方配置中增加 orb 用法冒烟测试。
- Enforce changelog + SemVer bump policy.
  > 强制 changelog 与 SemVer 升级策略。
