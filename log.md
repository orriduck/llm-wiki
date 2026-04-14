# Wiki 日志

## [2026-04-13] init | 初始化 wiki

从 Claude Code 记忆中提取工作相关内容，建立初始 wiki 结构。

**创建页面：**
- `wiki/Python工具链.md` — Poetry、black、isort、pytest 规范
- `wiki/AWS与Metaflow.md` — Metaflow 框架和 AWS 服务映射

**待补充：**
- AWS 账户/IAM 具体配置
- 更多 Metaflow 装饰器用法
- 其他工作领域页面

## [2026-04-14] ingest | fish shell 使用指南

新增 fish shell 工具页面，涵盖安装、设置默认 shell、配置、语法速查、插件管理。

**创建页面：**
- `wiki/engineering/fish.md` — fish shell 优势、安装（macOS/Linux）、chsh 设为默认 shell、config.fish 配置、语法速查（变量/条件/循环/函数）、abbr 缩写、Fisher 插件管理器、常用插件（Tide/Starship/fzf.fish/z.fish）、与 bash 兼容性说明

**更新页面：**
- `index.md` — 添加 fish shell 页面索引

---

## [2026-04-13] ingest | AWS 核心服务独立页面

为 5 个 AWS 重点服务各创建独立 wiki 页面，从 AWS与Metaflow 中拆分出通用知识。

**创建页面：**
- `wiki/aws/S3.md` — 对象存储、存储类别、权限、加密、版本控制、生命周期、性能优化
- `wiki/aws/Lambda.md` — 无服务器计算、触发方式、Layer、并发控制、冷启动、重试
- `wiki/aws/EventBridge.md` — 事件总线、规则匹配、Scheduler、Pipes、Archive/Replay
- `wiki/aws/CloudWatch.md` — 指标、日志、告警、Logs Insights、EMF、异常检测
- `wiki/aws/CloudTrail.md` — API 审计、事件类型、Lake 查询、安全调查

**更新页面：**
- `index.md` — 添加 5 个 AWS 服务页面索引
