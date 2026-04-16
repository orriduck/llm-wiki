# Outerbounds Workstations / Outerbounds Workstations

> Cloud Workstations are personal cloud development environments running within the customer's cloud account, accessible via VSCode extension or browser Web UI. Data stays in the cloud account and the environment is consistent with production.

> Cloud Workstation 是运行在客户云账号内的个人云端开发环境，通过 VSCode 扩展或浏览器 Web UI 访问，数据不出云账号，并与生产环境保持一致。

Related notes / 相关笔记：[[Metaflow工作流框架]] | [[Outerbounds概览]]

---

## What is a Workstation / Workstation 是什么

An Outerbounds Cloud Workstation is essentially a Linux container instance running on the customer's cloud infrastructure (EKS/GKE/AKS nodes), providing each user with an independent development environment.

> Outerbounds Cloud Workstation 本质上是一台运行在客户云基础设施（EKS/GKE/AKS 节点）上的 Linux 容器实例，为每位用户提供独立的开发环境。

**Core advantages / 核心优势：**

| Feature / 特点 | Description / 说明 |
|------|------|
| Data Security / 数据安全 | Workstation runs in customer cloud account; data doesn't need to be copied to local laptop / 在客户云账号内运行，数据不需要复制到本地笔记本 |
| Production Consistency / 生产一致性 | Same Linux environment as Kubernetes tasks; eliminates "works locally, fails in cloud" issues / 与 Kubernetes 任务同为 Linux 环境，消除"本地能跑，云端报错"问题 |
| Pre-configured Integration / 预配置集成 | Out-of-the-box connection to Artifact storage, Metaflow Metadata Service, Runs tracking / 开箱即用连接 Artifact 存储、Metaflow Metadata Service、Runs 追踪 |
| Flexible Scaling / 灵活扩展 | Submit to Kubernetes cluster directly from Workstation when local resources are insufficient / 当本地资源不足时，直接从 Workstation 提交到 Kubernetes 集群 |
| Identity Management / 身份管理 | Unified authentication through SSO, integrated with the organization's permission system / 通过 SSO 统一认证，接入组织的权限体系 |

**Workstations are optional** -- users can also connect to Outerbounds from a local laptop or existing cloud environment.

> **Workstation 是可选的**——用户也可以从本地笔记本或已有云环境连接 Outerbounds。

---

## Supported Development Interfaces / 支持的开发界面

- **Local Visual Studio Code** (remote connection via Outerbounds extension)
- **Browser Web UI** (based on code-server, no local VSCode installation required)
- **Jupyter Notebook** (launched within the Web UI)

> - **本地 Visual Studio Code**（通过 Outerbounds 扩展远程连接）
> - **浏览器 Web UI**（基于 code-server，无需本地安装 VSCode）
> - **Jupyter Notebook**（在 Web UI 内启动）

---

## Admin: Creating a Workstation / 管理员：创建 Workstation

> Only platform admins can create Workstations.

> 只有平台管理员可以创建 Workstation。

**Creation steps / 创建步骤：**

1. Go to **Setup Workstations** in the Outerbounds UI / 在 Outerbounds UI 中进入 **Setup Workstations**
2. Click **Add workstation** / 点击 **Add workstation**
3. Fill in configuration items / 填写配置项：

| Config Item / 配置项 | Description / 说明 |
|--------|------|
| **Workstation Name** | Unique identifier (recommend including username and purpose, e.g., `alice-dev`) / 唯一标识符（建议包含用户名和用途，例如 `alice-dev`）|
| **Owner** | Assign to an invited platform user / 分配给已受邀的平台用户 |
| **Hosting** | Cloud (default) or on-premises (contact support team) / 云端（默认）或本地（on-premises，需联系支持团队）|
| **CPU / Memory** | Allocated compute resources; should meet local dev needs while allowing scaling to Kubernetes / 分配的计算资源，应满足本地开发需求，同时允许从 Workstation 扩展到 Kubernetes |
| **Container Image** | Select a container image with required dependencies pre-installed / 选择预装了所需依赖的容器镜像（参考依赖管理文档）|
| **Inactivity Shutdown** | When enabled, Workstation auto-hibernates after idle period (saves cost) / 启用后，Workstation 在空闲一段时间后自动休眠（节省成本）|
| **Multi-User Access** | Allows other users to use this Workstation's credentials, **use with caution** (shares Owner's identity) / 允许其他用户使用该 Workstation 的凭证，**谨慎使用**（会共享 Owner 的身份）|

4. After creation, the Workstation needs a few minutes to initialize / 创建后，Workstation 需要几分钟时间完成初始化

**Prerequisites / 前提条件：**

- The target user must already be invited via the platform's User Management interface and have completed SSO login.

> - 目标用户必须已通过平台的 User Management 界面受邀并完成 SSO 登录

---

## User: Connecting to a Workstation / 用户：连接 Workstation

### Method 1: VSCode Extension (Recommended) / 方式一：VSCode 扩展（推荐）

```
1. Open VSCode / 打开 VSCode
2. Click the Extensions icon on the left / 点击左侧 Extensions 图标
3. Search for "Outerbounds" and install the extension / 搜索 "Outerbounds" 并安装扩展
4. Open the extension panel, copy the Personal Access Token from the Outerbounds UI and paste it as prompted
   打开扩展面板，按提示复制 Outerbounds UI 中的 Personal Access Token 并粘贴
5. After successful auth, select your Workstation from the list and click "Connect"
   认证成功后，从列表中选择你的 Workstation，点击 "Connect"
6. A new window opens; "workstation in ws-[ID]" in the bottom-left corner indicates a successful connection
   新窗口打开，左下角显示 "workstation in ws-[ID]" 表示连接成功
```

The first connection may take about 1 minute to complete initialization.

> 首次连接可能需要约 1 分钟完成初始化。

### Method 2: Browser Web UI / 方式二：浏览器 Web UI

```
1. Go to the "Workstations" view in the Outerbounds UI
   在 Outerbounds UI 中进入 "Workstations" 视图
2. Find your Workstation / 找到你的 Workstation
3. Click the "Actions" dropdown menu, select "Web UI"
   点击 "Actions" 下拉菜单，选择 "Web UI"
4. Browser opens a code-server-based VSCode interface connected to the same Workstation backend
   浏览器打开基于 code-server 的 VSCode 界面，连接到同一 Workstation 后端
```

### SSH Connection / SSH 连接

> **Needs verification / 需要验证**: Detailed SSH connection instructions are not found in public documentation. Connecting via VSCode's Remote-SSH extension is theoretically possible (the VSCode extension itself uses SSH under the hood), but Outerbounds official docs only describe the two methods above. Contact Outerbounds support for SSH connection needs.

> 公开文档中未找到 SSH 直接连接的详细说明。通过 VSCode 的 Remote-SSH 扩展理论上可行（VSCode 扩展本身底层使用 SSH 协议），但 Outerbounds 官方文档仅描述了上述两种连接方式。如有 SSH 连接需求，建议联系 Outerbounds 支持团队。

---

## Development Workflow / 开发工作流

### Basic Development Loop / 基本开发循环

```bash
# Inside the Workstation terminal:
# 在 Workstation 终端内：

# 1. Clone/pull code / 克隆/拉取代码
git pull origin main

# 2. Local test (using Workstation's compute resources)
# 本地测试（使用 Workstation 的计算资源）
python my_flow.py run

# 3. Scale to Kubernetes (using cloud compute pools)
# 扩展到 Kubernetes（使用云计算池）
python my_flow.py run --with kubernetes

# 4. Deploy to production (Argo Workflows)
# 部署到生产（Argo Workflows）
python my_flow.py --environment=fast-bakery argo-workflows create
```

### Workstation and Kubernetes Relationship / Workstation 与 Kubernetes 的关系

When running `run --with kubernetes` from a Workstation, the platform **automatically uses the Workstation's container image** as the Kubernetes task image. This ensures:

> 当从 Workstation 执行 `run --with kubernetes` 时，平台**自动使用 Workstation 的容器镜像**作为 Kubernetes 任务镜像。这保证了：

- Code that runs on the Workstation will also run on Kubernetes.
- No need to manually specify `--image` parameter (unless there are special requirements).

> - 在 Workstation 上能跑的代码，在 Kubernetes 上也能跑
> - 无需手动指定 `--image` 参数（除非有特殊需求）

---

## Workstation Lifecycle Management / Workstation 生命周期管理

### Status Indicators / 状态指示

| Status Icon / 状态图标 | Meaning / 含义 |
|---------|------|
| Green indicator / 绿色指示灯 | Running, ready to connect / 运行中，可以连接 |
| Spinning loader / 旋转加载图标 | Starting up or shutting down / 正在启动或停止 |
| Gray circle / 灰色圆圈 | Hibernated, not consuming compute resources / 已休眠（Hibernated），不消耗计算资源 |

### Hibernate / 休眠

- Hibernated Workstations **do not consume compute resources** (no charges).
- Persistent storage (code, config files) is retained during hibernation.
- Recovery requires manual action or is triggered automatically via Inactivity Shutdown.

> - 休眠状态下 Workstation **不消耗计算资源**（不计费）
> - 持久存储（代码、配置文件）在休眠期间保留
> - 需要手动或通过 Inactivity Shutdown 自动触发恢复

### Data Persistence / 数据持久化

- Each Workstation has an independent **persistent storage volume**; data survives restarts and hibernation.
- **Note**: Workstations are not suitable for long-term data storage. Recommendations:
  - Push code to Git repositories promptly.
  - Store large datasets in S3/GCS/Azure Blob object storage.
  - Do not use Workstations as the sole data storage location.

> - 每个 Workstation 有独立的**持久存储卷**，重启和休眠不会丢失数据
> - **注意**：Workstation 不适合作为长期数据存储，建议：
>   - 代码及时推送到 Git 仓库
>   - 大型数据集存放在 S3/GCS/Azure Blob 等对象存储
>   - 不要将 Workstation 用作唯一的数据存储位置

### Cost Control / 成本控制

- Multiple Workstations can share the same Kubernetes node (managed by platform scheduling).
- Enable Inactivity Shutdown to automatically release resources when users are inactive.
- Compute pools support Spot instances to further reduce costs.

> - 多个 Workstation 可以共享同一个 Kubernetes 节点（由平台调度）
> - 启用 Inactivity Shutdown 可以在用户不活跃时自动释放资源
> - 计算池支持 Spot 实例，进一步降低成本

---

## Dependency Management on Workstations / Workstation 上的依赖管理

The container image used by a Workstation is specified by the admin at creation time. Common approaches:

> Workstation 使用的容器镜像在创建时由管理员指定。常见方案：

```python
# Approach 1: Workstation image already contains all dependencies, no extra declaration needed
# Suitable for organization-managed standardized environments
# 方案 1：Workstation 镜像已包含所有依赖，无需额外声明
# 适合组织统一管理的标准化环境

# Approach 2: Use fast-bakery to dynamically install per-step dependencies
# When running --with kubernetes from Workstation, a new image is built
# 方案 2：使用 fast-bakery 动态按步骤安装依赖
# 在 Workstation 上运行 --with kubernetes 时会构建新镜像
@step
@pypi(packages={"scikit-learn": "1.3.0", "pandas": "2.0.0"})
def train(self):
    from sklearn import ...
```

See [[Outerbounds-依赖管理]] for details.

> 详见 [[Outerbounds-依赖管理]]。

---

## References / 参考资料

- [Overview of cloud workstations](https://docs.outerbounds.com/outerbounds/cloud-workstation-overview/)
- [Setting up a cloud workstation](https://docs.outerbounds.com/outerbounds/setup-workstation/)
- [Connecting to a cloud workstation](https://docs.outerbounds.com/outerbounds/connect-to-workstation/)
- [Cost Optimization Overview](https://docs.outerbounds.com/outerbounds/cost-optimization/)

*Last updated / 最后更新：2026-04-13*
