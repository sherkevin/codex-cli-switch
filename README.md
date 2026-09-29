# codex-cli

一个全局切换 Codex CLI `CODEX_HOME` 的小工具。

它把配置别名保存到 `~/.codex-cli/config.json`。`codex-cli use NAME` 后，同目录的 `codex` shim 会在任何工作区启动真实 Codex CLI 时注入对应的 `CODEX_HOME`。

## 安装

```bash
git clone https://github.com/sherkevin/codex-cli-switch.git
cd codex-cli-switch
mkdir -p ~/.local/bin
install -m 755 codex-cli codex ~/.local/bin/
export PATH="$HOME/.local/bin:$PATH"
hash -r 2>/dev/null || true
rehash 2>/dev/null || true
```

`~/.local/bin` 要排在 Homebrew 或 npm 安装的 Codex CLI 目录之前。可以用下面的命令确认当前实际执行的是 shim：

```bash
which codex
which codex-cli
```

如果真实 Codex 二进制无法自动找到，可以设置：

```bash
export CODEX_REAL_BIN=/opt/homebrew/bin/codex
```

## 日常用法

### 添加配置

配置名对应一个已有的 `CODEX_HOME` 目录：

```bash
codex-cli add jessica CODEX_HOME=/Users/you/.antigravity_cockpit/instances/codex/cli-d139edad9e1e
codex-cli add work CODEX_HOME=/Users/you/.codex-work
```

目录必须已经存在。`codex-cli` 不复制、不读取、不修改目录里的 `auth.json`。

### 查看配置

```bash
codex-cli list
codex-cli current
codex-cli path jessica
```

输出中的 `*` 表示当前全局选择。

### 全局切换

```bash
codex-cli use jessica
codex
codex exec "检查当前目录"
```

之后从任何工作区输入的 `codex` 都会使用 Jessica 对应的 `CODEX_HOME`。正在运行的 Codex 进程不会被重启；下一次启动的进程会使用新选择。

如果别名指向 Cockpit 这类较长路径，启动时会通过 `~/.codex-cli/homes/jessica` 这样的短 symlink 注入 `CODEX_HOME`，以避开 macOS Unix socket 的路径长度限制。配置、登录态和会话仍保存在 `add` 指定的真实目录中；`codex-cli current` 会同时显示真实路径和运行时路径。

### 恢复官方配置

```bash
codex-cli reset
```

这会让 shim 使用 `~/.codex`，保留已经添加的别名。`codex-cli use default` 等价于 `reset`。

### 其他操作

```bash
codex-cli remove jessica
codex-cli add jessica CODEX_HOME=/new/path --force
codex-cli help
```

`codex-cli run ...` 也可以直接按当前选择执行真实 Codex，例如 `codex-cli run --help`。

## 全局状态

默认状态文件：

```text
~/.codex-cli/config.json   # 权限 0600
```

格式示例：

```json
{
  "version": 1,
  "active": "jessica",
  "profiles": {
    "jessica": {
      "CODEX_HOME": "/Users/you/.antigravity_cockpit/instances/codex/cli-d139edad9e1e"
    }
  }
}
```

可用 `CODEX_CLI_HOME` 指定状态目录，方便测试或维护多套全局配置；可用 `CODEX_CLI_DEFAULT_HOME` 指定 reset 的官方 home。正常使用不需要设置它们。

## 开发与测试

项目没有第三方 Python 依赖，支持 Python 3.9+：

```bash
python3 -m unittest discover -s tests -v
```

测试使用临时目录和本地替身，不调用模型 API。

## 设计边界

- 全局切换的核心是 `codex` shim；只安装 `codex-cli` 而不安装同目录的 `codex`，`use` 不会影响直接输入的原始 `codex`。
- 工具只管理别名和 `CODEX_HOME` 路径，不管理模型 provider、API key、sidecar 或 Cockpit 进程。
- 默认 `reset` 指向 `~/.codex`，不会删除配置或登录态。

## 许可

MIT，见 [LICENSE](./LICENSE)。
