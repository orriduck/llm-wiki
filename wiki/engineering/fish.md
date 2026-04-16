# fish shell

> A friendly interactive shell (**f**riendly **i**nteractive **sh**ell) with out-of-the-box autocompletion, syntax highlighting, and smart suggestions, requiring no tedious configuration. Latest version: 4.0+ (2025).

> 友好的交互式命令行 shell（**f**riendly **i**nteractive **sh**ell），开箱即用的自动补全、语法高亮和智能建议，无需繁琐配置。最新版本：4.0+（2025）。

## Why use fish / 为什么用 fish

fish's design philosophy is "user-friendly first", building in features that usually require plugins or extensive configuration:

> fish 的设计理念是"用户友好优先"，把通常需要插件或大量配置才能实现的功能全部内置：

| Feature / 特性 | Description / 描述 |
|------|------|
| **Real-time auto-suggestions / 实时自动建议** | Shows suggestions in gray based on history and file paths; press `->` to accept / 根据历史记录和文件路径，灰色字显示建议，按 `→` 接受 |
| **Syntax highlighting / 语法高亮** | Instant coloring while typing: existing commands in blue, non-existent in red, arguments auto-distinguished / 输入时即时着色：命令存在为蓝色，不存在为红色，参数自动区分 |
| **Out-of-the-box Tab completion / 开箱即用的 Tab 补全** | Reads man pages to auto-generate completions, no need to write completion scripts / 读取 man 页面自动生成补全，无需手写补全脚本 |
| **Web configuration UI / Web 配置界面** | `fish_config` opens a browser GUI for visual theme, prompt, and function configuration / `fish_config` 打开浏览器 GUI，可视化配置主题、提示符、函数 |
| **Abbreviations (abbr) / 缩写（abbr）** | Type abbreviation and it auto-expands to the full command; expanded form is visible and editable, more transparent than alias / 输入缩写自动展开为完整命令，展开后可见、可编辑，比 alias 更透明 |
| **Universal variables / 通用变量** | `set -U` persists variables across sessions without writing to config files / `set -U` 设置跨 session 持久化变量，无需反复写入配置文件 |
| **Clear script syntax / 脚本语法清晰** | Closer to natural language; conditionals/loops don't need `[ ]`, avoiding common bash pitfalls / 更接近自然语言，条件/循环不需要 `[ ]`，避免 bash 常见的坑 |

**Key differences from bash/zsh / 与 bash/zsh 的核心区别：**

- fish is **not POSIX compatible**: Script syntax differs from bash; `$()` variable assignment, `if`, etc. are written differently

> fish **不兼容 POSIX**：脚本语法与 bash 不同，`$()` 变量赋值、`if` 等写法都不一样

- fish is best for **interactive use**; automation scripts should still use bash (with shebang `#!/bin/bash`) and be called from fish

> fish 适合**交互式使用**，自动化脚本建议仍用 bash（加 shebang `#!/bin/bash`）并从 fish 中调用

- zsh (with oh-my-zsh) has similar features but requires heavy configuration; fish achieves the same effect out of the box

> zsh（配合 oh-my-zsh）功能相似但配置繁重；fish 同等效果开箱即用

---

## Installation / 安装

### macOS

```bash
# Homebrew (recommended) / Homebrew（推荐）
brew install fish

# Confirm path / 确认路径
which fish   # /opt/homebrew/bin/fish
```

### Ubuntu / Debian

```bash
# Add official PPA (for latest version) / 添加官方 PPA（获取最新版）
sudo apt-add-repository ppa:fish-shell/release-4
sudo apt update
sudo apt install fish

# Or use distribution's built-in version (may be older)
# 或使用发行版自带版本（版本较旧）
sudo apt install fish
```

### Fedora / RHEL / CentOS

```bash
# Fedora
sudo dnf install fish

# RHEL/CentOS (via openSUSE Build Service)
# See https://software.opensuse.org/download.html?project=shells:fish:release:4&package=fish
# RHEL/CentOS（通过 openSUSE Build Service）
# 详见 https://software.opensuse.org/download.html?project=shells:fish:release:4&package=fish
```

### Arch Linux

```bash
sudo pacman -S fish
```

### Verify installation / 验证安装

```bash
fish --version   # fish, version 4.x.x
```

---

## Set as default shell / 设置为默认 Shell

### Step 1: Add fish to the list of valid shells / 将 fish 加入合法 shell 列表

```bash
# Check fish path / 查看 fish 路径
which fish   # e.g. /opt/homebrew/bin/fish or /usr/bin/fish

# Append the path to /etc/shells (requires sudo)
# 将路径追加到 /etc/shells（需要 sudo）
echo /opt/homebrew/bin/fish | sudo tee -a /etc/shells
# On Linux this is usually already in the list; you can skip this step
# Linux 通常已在列表中，可跳过此步
```

### Step 2: Switch default shell / 切换默认 shell

```bash
# Replace with your actual fish path / 替换为你的 fish 实际路径
chsh -s /opt/homebrew/bin/fish        # macOS Homebrew
chsh -s /usr/bin/fish                  # Linux
```

Enter your current user password, then **log out and back in** (or restart the terminal) for changes to take effect.

> 输入当前用户密码后，**重新登录**（或重启终端）生效。

### Verify / 验证

```bash
echo $SHELL   # Should output the fish path / 应输出 fish 路径
```

### Revert to bash/zsh / 回退到 bash/zsh

```bash
chsh -s /bin/bash
chsh -s /bin/zsh
```

> **Note (macOS)**: macOS default shell is zsh; system shell scripts (e.g. `/etc/profile`) are not affected -- only the interactive terminal changes to fish.

> **注意（macOS）**：macOS 默认 shell 是 zsh，系统 shell 脚本（如 `/etc/profile`）不受影响，仅交互式终端改为 fish。

---

## Configuration files / 配置文件

fish's configuration directory is `~/.config/fish/`:

> fish 的配置目录是 `~/.config/fish/`：

```
~/.config/fish/
├── config.fish          # Startup config (similar to .bashrc) / 启动配置（类似 .bashrc）
├── fish_plugins         # Fisher plugin list / Fisher 插件列表
├── functions/           # Custom functions (one file per function) / 自定义函数（每个文件一个函数）
│   └── my_func.fish
└── completions/         # Custom completion scripts / 自定义补全脚本
    └── mytool.fish
```

### config.fish example / config.fish 示例

```fish
# Environment variables / 环境变量
set -x EDITOR nvim
set -x GOPATH $HOME/go

# PATH append (fish-specific, auto-deduplicates) / PATH 追加（fish 专用，自动去重）
fish_add_path /opt/homebrew/bin
fish_add_path $GOPATH/bin

# Aliases (in fish use alias or abbr; abbr recommended) / 别名（fish 中用 alias 或 abbr，推荐 abbr）
alias ll "ls -la"
alias g git
```

### Web configuration UI / Web 配置界面

```bash
fish_config
```

Visually configure in the browser: theme colors, prompt style, view history, manage functions. Changes are automatically written to config files.

> 在浏览器中可视化配置：主题颜色、提示符样式、查看历史记录、管理函数。修改后自动写入配置文件。

---

## Syntax reference / 语法速查

### Variables / 变量

```fish
# Set variable (local) / 设置变量（局部）
set name "world"
echo "hello $name"

# Export as environment variable (-x) / 导出为环境变量（-x）
set -x API_KEY "YOUR_API_KEY"

# Universal variable: persists across sessions, no need to write to config.fish (-U)
# 通用变量：跨 session 持久化，不需要写入 config.fish（-U）
set -U fish_greeting ""   # Disable greeting / 关闭欢迎语

# List variables / 列表变量
set fruits apple banana cherry
echo $fruits[1]   # apple (fish index starts at 1) / apple（fish 索引从 1 开始）
```

### Conditionals / 条件判断

```fish
# if / else if / else / end
if test -f ~/.config/fish/config.fish
    echo "config exists"
else
    echo "no config"
end

# String comparison / 字符串比较
if test "$status" = "0"
    echo "success"
end
```

### Loops / 循环

```fish
# for loop / for 循环
for file in *.md
    echo $file
end

# while loop / while 循环
while true
    echo "press ctrl-c to stop"
    sleep 1
end
```

### Functions / 函数

```fish
# Define function (can be saved to ~/.config/fish/functions/greet.fish)
# 定义函数（可写入 ~/.config/fish/functions/greet.fish）
function greet
    echo "Hello, $argv[1]!"
end

greet World   # Hello, World!

# List all functions / 查看所有函数
functions

# View function source / 查看某个函数源码
functions greet
```

### Command substitution / 命令替换

```fish
# Use () instead of $() / 用 () 而不是 $()
set today (date +%Y-%m-%d)
echo $today
```

### Pipes and redirection / 管道与重定向

```fish
# Mostly the same as bash / 与 bash 基本相同
ls -la | grep ".md"
echo "log" >> ~/log.txt

# Redirect both stdout and stderr (fish 4.x)
# 同时重定向 stdout 和 stderr（fish 4.x）
command &> output.txt
```

---

## Abbreviations (abbr) -- Better than alias / 缩写（abbr）— 比 alias 更好

Abbreviations **expand visibly** on the command line, allowing you to confirm and edit before execution, avoiding alias's "black box" problem:

> 缩写在命令行**展开后可见**，执行前可以确认和修改，避免 alias 的"黑盒"问题：

```fish
# Add abbreviations (permanent, saved to universal variables)
# 添加缩写（永久生效，写入通用变量）
abbr -a gs "git status"
abbr -a gp "git push"
abbr -a gl "git log --oneline"
abbr -a k kubectl
abbr -a dc "docker compose"

# List all abbreviations / 列出所有缩写
abbr

# Delete abbreviation / 删除缩写
abbr --erase gs
```

Type `gs` then press space, and it auto-expands to `git status`, which you can then edit further.

> 输入 `gs` 后按空格，自动展开为 `git status`，可再次编辑。

---

## Fisher: Plugin manager / Fisher：插件管理器

[Fisher](https://github.com/jorgebucaran/fisher) is the most popular fish plugin manager, written in pure fish, lightweight with no dependencies.

> [Fisher](https://github.com/jorgebucaran/fisher) 是最流行的 fish 插件管理器，用纯 fish 编写，轻量无依赖。

### Install Fisher / 安装 Fisher

```bash
curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && fisher install jorgebucaran/fisher
```

### Common commands / 常用命令

```bash
fisher install <plugin>    # Install plugin / 安装插件
fisher update              # Update all plugins / 更新所有插件
fisher remove <plugin>     # Uninstall plugin / 卸载插件
fisher list                # List installed plugins / 列出已安装插件
```

The plugin list is auto-saved to `~/.config/fish/fish_plugins`, which can be version-controlled. Run `fisher update` on a new machine to restore everything.

> 插件列表自动保存到 `~/.config/fish/fish_plugins`，可纳入版本控制，新机器运行 `fisher update` 一键恢复。

---

## Recommended plugins and themes / 推荐插件与主题

### Prompts / 提示符

| Plugin / 插件 | Features / 特点 |
|------|------|
| **[Tide](https://github.com/IlanCosman/tide)** | fish-exclusive, async rendering doesn't block input, wizard-style config, most feature-rich / fish 专属，异步渲染不阻塞输入，向导式配置，功能最丰富 |
| **[Starship](https://starship.rs/)** | Written in Rust, cross-shell (fish/zsh/bash universal), unified config file / Rust 编写，跨 shell 通用，配置文件统一 |
| **[Pure](https://github.com/pure-fish/pure)** | Minimalist style, lightweight and fast / 极简风格，轻量快速 |

```bash
# Install Tide / 安装 Tide
fisher install IlanCosman/tide@v6
tide configure   # Wizard-style interactive configuration / 向导式交互配置

# Install Starship (requires brew install starship first)
# 安装 Starship（需先 brew install starship）
echo 'starship init fish | source' >> ~/.config/fish/config.fish
```

### Utility plugins / 实用插件

| Plugin / 插件 | Function / 功能 |
|------|------|
| [fzf.fish](https://github.com/PatrickF1/fzf.fish) | `Ctrl+R` fuzzy search history, `Ctrl+Alt+F` search files / 模糊搜索历史，搜索文件 |
| [z.fish](https://github.com/jethrokuan/z) | `z <keyword>` jump to frequently used directories (like autojump/zoxide) / 跳转到常用目录 |
| [nvm.fish](https://github.com/jorgebucaran/nvm.fish) | Node version management, pure fish implementation, no nvm.sh needed / Node 版本管理，纯 fish 实现 |
| [puffer-fish](https://github.com/nickeb96/puffer-fish) | `..` expands to `cd ..`, `...` expands to `cd ../..` |
| [sponge](https://github.com/meaningful-ooo/sponge) | Auto-cleans failed commands from history / 自动清理历史记录中失败的命令 |

```bash
# Install multiple plugins at once / 一次性安装多个插件
fisher install PatrickF1/fzf.fish jethrokuan/z jorgebucaran/nvm.fish
```

---

## Common keyboard shortcuts / 常用快捷键

| Shortcut / 快捷键 | Function / 功能 |
|--------|------|
| `->` / `End` | Accept current auto-suggestion / 接受当前自动建议 |
| `Alt+->` | Accept next word of suggestion / 接受建议的下一个单词 |
| `Tab` | Trigger completion / cycle through candidates / 触发补全 / 在候选项间切换 |
| `Ctrl+R` | Search history (needs fzf.fish for fuzzy search) / 搜索历史记录（需 fzf.fish 获得模糊搜索） |
| `Ctrl+C` | Cancel current command / 取消当前命令 |
| `Ctrl+L` | Clear screen / 清屏 |
| `Alt+E` / `Alt+V` | Edit current command line in `$EDITOR` / 在 `$EDITOR` 中编辑当前命令行 |
| `Ctrl+Z` | Suspend process, `fg` to resume / 挂起进程，`fg` 恢复 |

---

## bash/zsh compatibility notes / 与 bash/zsh 兼容性说明

fish **is not a POSIX shell**; be aware of the following:

> fish **不是 POSIX shell**，以下场景需要注意：

```fish
# ❌ bash syntax (not supported in fish) / bash 写法（fish 不支持）
export VAR=value
VAR=$(command)
[ -f file ] && echo yes
source script.sh

# ✅ fish equivalent syntax / fish 等价写法
set -x VAR value
set VAR (command)
test -f file; and echo yes
source script.fish   # Or . script.fish (fish syntax files only) / 或 . script.fish（仅限 fish 语法文件）
```

**Recommendations / 建议：**

- Use fish for all interactive work, enjoy autocompletion and highlighting

> 交互式工作全用 fish，享受自动补全和高亮

- Use bash for automation scripts (CI, deploy scripts) with `#!/bin/bash` shebang

> 自动化脚本（CI、部署脚本）用 bash 并加 `#!/bin/bash` shebang

- Call bash scripts directly from fish: `bash script.sh`

> 从 fish 中直接调用 bash 脚本：`bash script.sh`

---

## Related pages / 相关页面

- [[uv]] -- Python package manager, `fish_add_path` integrates uv toolchain / Python 包管理器，`fish_add_path` 集成 uv 工具链
- [[ruff]] -- Code formatter, can configure `abbr -a rf "uvx ruff format ."` in fish / 代码格式化，可在 fish 中配置缩写

---

*Last updated: 2026-04-13 / 最后更新：2026-04-13*
