# Outerbounds Workstations

> Cloud Workstation 是运行在客户云账号内的个人云端开发环境，通过 VSCode 扩展或浏览器 Web UI 访问，数据不出云账号，并与生产环境保持一致。

相关笔记：[[Metaflow工作流框架]] | [[Outerbounds概览]]

---

## Workstation 是什么

Outerbounds Cloud Workstation 本质上是一台运行在客户云基础设施（EKS/GKE/AKS 节点）上的 Linux 容器实例，为每位用户提供独立的开发环境。

**核心优势：**

| 特点 | 说明 |
|------|------|
| 数据安全 | Workstation 在客户云账号内运行，数据不需要复制到本地笔记本 |
| 生产一致性 | 与 Kubernetes 任务同为 Linux 环境，消除"本地能跑，云端报错"问题 |
| 预配置集成 | 开箱即用连接 Artifact 存储、Metaflow Metadata Service、Runs 追踪 |
| 灵活扩展 | 当本地资源不足时，直接从 Workstation 提交到 Kubernetes 集群 |
| 身份管理 | 通过 SSO 统一认证，接入组织的权限体系 |

**Workstation 是可选的**——用户也可以从本地笔记本或已有云环境连接 Outerbounds。

---

## 支持的开发界面

- **本地 Visual Studio Code**（通过 Outerbounds 扩展远程连接）
- **浏览器 Web UI**（基于 code-server，无需本地安装 VSCode）
- **Jupyter Notebook**（在 Web UI 内启动）

---

## 管理员：创建 Workstation

> 只有平台管理员可以创建 Workstation。

**创建步骤：**

1. 在 Outerbounds UI 中进入 **Setup Workstations**
2. 点击 **Add workstation**
3. 填写配置项：

| 配置项 | 说明 |
|--------|------|
| **Workstation Name** | 唯一标识符（建议包含用户名和用途，例如 `alice-dev`）|
| **Owner** | 分配给已受邀的平台用户 |
| **Hosting** | 云端（默认）或本地（on-premises，需联系支持团队）|
| **CPU / Memory** | 分配的计算资源，应满足本地开发需求，同时允许从 Workstation 扩展到 Kubernetes |
| **Container Image** | 选择预装了所需依赖的容器镜像（参考依赖管理文档）|
| **Inactivity Shutdown** | 启用后，Workstation 在空闲一段时间后自动休眠（节省成本）|
| **Multi-User Access** | 允许其他用户使用该 Workstation 的凭证，**谨慎使用**（会共享 Owner 的身份）|

4. 创建后，Workstation 需要几分钟时间完成初始化

**前提条件：**
- 目标用户必须已通过平台的 User Management 界面受邀并完成 SSO 登录

---

## 用户：连接 Workstation

### 方式一：VSCode 扩展（推荐）

```
1. 打开 VSCode
2. 点击左侧 Extensions 图标
3. 搜索 "Outerbounds" 并安装扩展
4. 打开扩展面板，按提示复制 Outerbounds UI 中的 Personal Access Token 并粘贴
5. 认证成功后，从列表中选择你的 Workstation，点击 "Connect"
6. 新窗口打开，左下角显示 "workstation in ws-[ID]" 表示连接成功
```

首次连接可能需要约 1 分钟完成初始化。

### 方式二：浏览器 Web UI

```
1. 在 Outerbounds UI 中进入 "Workstations" 视图
2. 找到你的 Workstation
3. 点击 "Actions" 下拉菜单，选择 "Web UI"
4. 浏览器打开基于 code-server 的 VSCode 界面，连接到同一 Workstation 后端
```

### SSH 连接

> **需要验证**：公开文档中未找到 SSH 直接连接的详细说明。通过 VSCode 的 Remote-SSH 扩展理论上可行（VSCode 扩展本身底层使用 SSH 协议），但 Outerbounds 官方文档仅描述了上述两种连接方式。如有 SSH 连接需求，建议联系 Outerbounds 支持团队。

---

## 开发工作流

### 基本开发循环

```bash
# 在 Workstation 终端内：

# 1. 克隆/拉取代码
git pull origin main

# 2. 本地测试（使用 Workstation 的计算资源）
python my_flow.py run

# 3. 扩展到 Kubernetes（使用云计算池）
python my_flow.py run --with kubernetes

# 4. 部署到生产（Argo Workflows）
python my_flow.py --environment=fast-bakery argo-workflows create
```

### Workstation 与 Kubernetes 的关系

当从 Workstation 执行 `run --with kubernetes` 时，平台**自动使用 Workstation 的容器镜像**作为 Kubernetes 任务镜像。这保证了：

- 在 Workstation 上能跑的代码，在 Kubernetes 上也能跑
- 无需手动指定 `--image` 参数（除非有特殊需求）

---

## Workstation 生命周期管理

### 状态指示

| 状态图标 | 含义 |
|---------|------|
| 绿色指示灯 | 运行中，可以连接 |
| 旋转加载图标 | 正在启动或停止 |
| 灰色圆圈 | 已休眠（Hibernated），不消耗计算资源 |

### Hibernate（休眠）

- 休眠状态下 Workstation **不消耗计算资源**（不计费）
- 持久存储（代码、配置文件）在休眠期间保留
- 需要手动或通过 Inactivity Shutdown 自动触发恢复

### 数据持久化

- 每个 Workstation 有独立的**持久存储卷**，重启和休眠不会丢失数据
- **注意**：Workstation 不适合作为长期数据存储，建议：
  - 代码及时推送到 Git 仓库
  - 大型数据集存放在 S3/GCS/Azure Blob 等对象存储
  - 不要将 Workstation 用作唯一的数据存储位置

### 成本控制

- 多个 Workstation 可以共享同一个 Kubernetes 节点（由平台调度）
- 启用 Inactivity Shutdown 可以在用户不活跃时自动释放资源
- 计算池支持 Spot 实例，进一步降低成本

---

## Workstation 上的依赖管理

Workstation 使用的容器镜像在创建时由管理员指定。常见方案：

```python
# 方案 1：Workstation 镜像已包含所有依赖，无需额外声明
# 适合组织统一管理的标准化环境

# 方案 2：使用 fast-bakery 动态按步骤安装依赖
# 在 Workstation 上运行 --with kubernetes 时会构建新镜像
@step
@pypi(packages={"scikit-learn": "1.3.0", "pandas": "2.0.0"})
def train(self):
    from sklearn import ...
```

详见 [[Outerbounds-依赖管理]]。

---

## 参考资料

- [Overview of cloud workstations](https://docs.outerbounds.com/outerbounds/cloud-workstation-overview/)
- [Setting up a cloud workstation](https://docs.outerbounds.com/outerbounds/setup-workstation/)
- [Connecting to a cloud workstation](https://docs.outerbounds.com/outerbounds/connect-to-workstation/)
- [Cost Optimization Overview](https://docs.outerbounds.com/outerbounds/cost-optimization/)

*最后更新：2026-04-13*
