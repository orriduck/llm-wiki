# fish shell

> 友好的交互式命令行 shell（**f**riendly **i**nteractive **sh**ell），开箱即用的自动补全、语法高亮和智能建议，无需繁琐配置。最新版本：4.0+（2025）。

## 为什么用 fish

fish 的设计理念是"用户友好优先"，把通常需要插件或大量配置才能实现的功能全部内置：

| 特性 | 描述 |
|------|------|
| **实时自动建议** | 根据历史记录和文件路径，灰色字显示建议，按 `→` 接受 |
| **语法高亮** | 输入时即时着色：命令存在为蓝色，不存在为红色，参数自动区分 |
| **开箱即用的 Tab 补全** | 读取 man 页面自动生成补全，无需手写补全脚本 |
| **Web 配置界面** | `fish_config` 打开浏览器 GUI，可视化配置主题、提示符、函数 |
| **缩写（abbr）** | 输入缩写自动展开为完整命令，展开后可见、可编辑，比 alias 更透明 |
| **通用变量** | `set -U` 设置跨 session 持久化变量，无需反复写入配置文件 |
| **脚本语法清晰** | 更接近自然语言，条件/循环不需要 `[ ]`，避免 bash 常见的坑 |

**与 bash/zsh 的核心区别：**

- fish **不兼容 POSIX**：脚本语法与 bash 不同，`$()` 变量赋值、`if` 等写法都不一样
- fish 适合**交互式使用**，自动化脚本建议仍用 bash（加 shebang `#!/bin/bash`）并从 fish 中调用
- zsh（配合 oh-my-zsh）功能相似但配置繁重；fish 同等效果开箱即用

---

## 安装

### macOS

```bash
# Homebrew（推荐）
brew install fish

# 确认路径
which fish   # /opt/homebrew/bin/fish
```

### Ubuntu / Debian

```bash
# 添加官方 PPA（获取最新版）
sudo apt-add-repository ppa:fish-shell/release-4
sudo apt update
sudo apt install fish

# 或使用发行版自带版本（版本较旧）
sudo apt install fish
```

### Fedora / RHEL / CentOS

```bash
# Fedora
sudo dnf install fish

# RHEL/CentOS（通过 openSUSE Build Service）
# 详见 https://software.opensuse.org/download.html?project=shells:fish:release:4&package=fish
```

### Arch Linux

```bash
sudo pacman -S fish
```

### 验证安装

```bash
fish --version   # fish, version 4.x.x
```

---

## 设置为默认 Shell

### 第一步：将 fish 加入合法 shell 列表

```bash
# 查看 fish 路径
which fish   # 例如 /opt/homebrew/bin/fish 或 /usr/bin/fish

# 将路径追加到 /etc/shells（需要 sudo）
echo /opt/homebrew/bin/fish | sudo tee -a /etc/shells
# Linux 通常已在列表中，可跳过此步
```

### 第二步：切换默认 shell

```bash
# 替换为你的 fish 实际路径
chsh -s /opt/homebrew/bin/fish        # macOS Homebrew
chsh -s /usr/bin/fish                  # Linux
```

输入当前用户密码后，**重新登录**（或重启终端）生效。

### 验证

```bash
echo $SHELL   # 应输出 fish 路径
```

### 回退到 bash/zsh

```bash
chsh -s /bin/bash
chsh -s /bin/zsh
```

> **注意（macOS）**：macOS 默认 shell 是 zsh，系统 shell 脚本（如 `/etc/profile`）不受影响，仅交互式终端改为 fish。

---

## 配置文件

fish 的配置目录是 `~/.config/fish/`：

```
~/.config/fish/
├── config.fish          # 启动配置（类似 .bashrc）
├── fish_plugins         # Fisher 插件列表
├── functions/           # 自定义函数（每个文件一个函数）
│   └── my_func.fish
└── completions/         # 自定义补全脚本
    └── mytool.fish
```

### config.fish 示例

```fish
# 环境变量
set -x EDITOR nvim
set -x GOPATH $HOME/go

# PATH 追加（fish 专用，自动去重）
fish_add_path /opt/homebrew/bin
fish_add_path $GOPATH/bin

# 别名（fish 中用 alias 或 abbr，推荐 abbr）
alias ll "ls -la"
alias g git
```

### Web 配置界面

```bash
fish_config
```

在浏览器中可视化配置：主题颜色、提示符样式、查看历史记录、管理函数。修改后自动写入配置文件。

---

## 语法速查

### 变量

```fish
# 设置变量（局部）
set name "world"
echo "hello $name"

# 导出为环境变量（-x）
set -x API_KEY "abc123"

# 通用变量：跨 session 持久化，不需要写入 config.fish（-U）
set -U fish_greeting ""   # 关闭欢迎语

# 列表变量
set fruits apple banana cherry
echo $fruits[1]   # apple（fish 索引从 1 开始）
```

### 条件判断

```fish
# if / else if / else / end
if test -f ~/.config/fish/config.fish
    echo "config exists"
else
    echo "no config"
end

# 字符串比较
if test "$status" = "0"
    echo "success"
end
```

### 循环

```fish
# for 循环
for file in *.md
    echo $file
end

# while 循环
while true
    echo "press ctrl-c to stop"
    sleep 1
end
```

### 函数

```fish
# 定义函数（可写入 ~/.config/fish/functions/greet.fish）
function greet
    echo "Hello, $argv[1]!"
end

greet World   # Hello, World!

# 查看所有函数
functions

# 查看某个函数源码
functions greet
```

### 命令替换

```fish
# 用 () 而不是 $()
set today (date +%Y-%m-%d)
echo $today
```

### 管道与重定向

```fish
# 与 bash 基本相同
ls -la | grep ".md"
echo "log" >> ~/log.txt

# 同时重定向 stdout 和 stderr（fish 4.x）
command &> output.txt
```

---

## 缩写（abbr）— 比 alias 更好

缩写在命令行**展开后可见**，执行前可以确认和修改，避免 alias 的"黑盒"问题：

```fish
# 添加缩写（永久生效，写入通用变量）
abbr -a gs "git status"
abbr -a gp "git push"
abbr -a gl "git log --oneline"
abbr -a k kubectl
abbr -a dc "docker compose"

# 列出所有缩写
abbr

# 删除缩写
abbr --erase gs
```

输入 `gs` 后按空格，自动展开为 `git status`，可再次编辑。

---

## Fisher：插件管理器

[Fisher](https://github.com/jorgebucaran/fisher) 是最流行的 fish 插件管理器，用纯 fish 编写，轻量无依赖。

### 安装 Fisher

```bash
curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && fisher install jorgebucaran/fisher
```

### 常用命令

```bash
fisher install <plugin>    # 安装插件
fisher update              # 更新所有插件
fisher remove <plugin>     # 卸载插件
fisher list                # 列出已安装插件
```

插件列表自动保存到 `~/.config/fish/fish_plugins`，可纳入版本控制，新机器运行 `fisher update` 一键恢复。

---

## 推荐插件与主题

### 提示符

| 插件 | 特点 |
|------|------|
| **[Tide](https://github.com/IlanCosman/tide)** | fish 专属，异步渲染不阻塞输入，向导式配置，功能最丰富 |
| **[Starship](https://starship.rs/)** | Rust 编写，跨 shell（fish/zsh/bash 通用），配置文件统一 |
| **[Pure](https://github.com/pure-fish/pure)** | 极简风格，轻量快速 |

```bash
# 安装 Tide
fisher install IlanCosman/tide@v6
tide configure   # 向导式交互配置

# 安装 Starship（需先 brew install starship）
echo 'starship init fish | source' >> ~/.config/fish/config.fish
```

### 实用插件

| 插件 | 功能 |
|------|------|
| [fzf.fish](https://github.com/PatrickF1/fzf.fish) | `Ctrl+R` 模糊搜索历史，`Ctrl+Alt+F` 搜索文件 |
| [z.fish](https://github.com/jethrokuan/z) | `z <keyword>` 跳转到常用目录（类似 autojump/zoxide） |
| [nvm.fish](https://github.com/jorgebucaran/nvm.fish) | Node 版本管理，纯 fish 实现，无需 nvm.sh |
| [puffer-fish](https://github.com/nickeb96/puffer-fish) | `..` 扩展为 `cd ..`，`...` 扩展为 `cd ../..` |
| [sponge](https://github.com/meaningful-ooo/sponge) | 自动清理历史记录中失败的命令 |

```bash
# 一次性安装多个插件
fisher install PatrickF1/fzf.fish jethrokuan/z jorgebucaran/nvm.fish
```

---

## 常用快捷键

| 快捷键 | 功能 |
|--------|------|
| `→` / `End` | 接受当前自动建议 |
| `Alt+→` | 接受建议的下一个单词 |
| `Tab` | 触发补全 / 在候选项间切换 |
| `Ctrl+R` | 搜索历史记录（需 fzf.fish 获得模糊搜索） |
| `Ctrl+C` | 取消当前命令 |
| `Ctrl+L` | 清屏 |
| `Alt+E` / `Alt+V` | 在 `$EDITOR` 中编辑当前命令行 |
| `Ctrl+Z` | 挂起进程，`fg` 恢复 |

---

## 与 bash/zsh 兼容性说明

fish **不是 POSIX shell**，以下场景需要注意：

```fish
# ❌ bash 写法（fish 不支持）
export VAR=value
VAR=$(command)
[ -f file ] && echo yes
source script.sh

# ✅ fish 等价写法
set -x VAR value
set VAR (command)
test -f file; and echo yes
source script.fish   # 或 . script.fish（仅限 fish 语法文件）
```

**建议**：
- 交互式工作全用 fish，享受自动补全和高亮
- 自动化脚本（CI、部署脚本）用 bash 并加 `#!/bin/bash` shebang
- 从 fish 中直接调用 bash 脚本：`bash script.sh`

---

## 相关页面

- [[uv]] — Python 包管理器，`fish_add_path` 集成 uv 工具链
- [[ruff]] — 代码格式化，可在 fish 中配置 `abbr -a rf "uvx ruff format ."`
