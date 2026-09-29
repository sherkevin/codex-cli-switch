# cxs：Codex CLI 配置切换器

`cxs` 是一个单文件终端工具，用 Codex CLI 自带的 profile 机制切换模型/provider，用 `CODEX_HOME` 切换隔离的登录态、配置和会话目录。

它不会改写已有的 `~/.codex/config.toml`，也不会复制、读取或打印 `auth.json` 的内容。

运行要求：Python 3.9+，只使用标准库。

## 安装

把 [cxs](./cxs) 复制到 PATH 中的目录：

```bash
git clone https://github.com/sherkevin/codex-cli-switch.git
cd codex-cli-switch
mkdir -p ~/.local/bin
install -m 755 cxs ~/.local/bin/cxs
export PATH="$HOME/.local/bin:$PATH"
```

如果 `~/.local/bin` 还没有加入 shell 的 PATH，把上面的 `export` 放进 `~/.zshrc` 或 `~/.bashrc`。

## 最常用的流程

```bash
# 创建一个只覆盖模型的 profile
cxs new fast --model gpt-6-sol --reasoning-effort low

# 选择它
cxs use fast
cxs current

# 用当前选择执行真实 Codex CLI
cxs run
cxs run exec "检查当前目录"

# 查看脱敏摘要
cxs show fast
```

`cxs use` 保存选择，但无法改变已经运行的父 shell 环境。因此直接输入 `codex` 仍会调用原始命令。若希望直接输入 `codex` 也使用当前选择，执行一次：

```bash
eval "$(cxs shell-init zsh)"
```

这会在当前 shell 中定义一个 `codex()` 函数，把参数交给 `cxs run`；真实的 Codex 二进制仍由 `cxs` 调用。

## 自定义 provider

`--env-key` 只接受环境变量名，不接受密钥值。密钥由你的 shell 或密钥管理器提供：

```bash
cxs new aisa \
  --model my-coding-model \
  --base-url https://proxy.example.test/v1 \
  --env-key AIS_API_KEY \
  --provider-name "My Responses proxy"
cxs use aisa
AIS_API_KEY=... cxs run exec "hello"
```

生成的 profile 使用 `model_provider`、`[model_providers.<id>]`、`base_url`、`env_key` 和 `wire_api = "responses"`。工具不会把 `AIS_API_KEY` 的值写进文件。

如果要改内置 OpenAI provider 的地址，可以显式指定 `--provider-id openai`；工具会生成 `openai_base_url`，不会创建被 Codex 保留的 `[model_providers.openai]` 表：

```bash
cxs new residency --model gpt-6-sol \
  --provider-id openai --base-url https://us.api.openai.com/v1
```

## 复用 Cockpit 的 CLI 实例

Cockpit 的 CLI 实例有自己的 `CODEX_HOME`、`config.toml` 和登录文件。`cxs` 会自动发现 `~/.antigravity_cockpit/instances/codex/cli-*`：

```bash
cxs homes
cxs use-home cli-<实例 ID>
cxs current
cxs run login status
cxs run
```

`cxs use-home default` 可回到默认 `~/.codex`。切换 home 时，如果当前 profile 在新 home 中不存在，工具会清除 profile 选择。复用 Cockpit home 前先停止仍在使用该目录的实例，避免两个进程同时写会话状态。

也可以自己创建隔离的账号目录；`cxs` 不会替你复制默认 home 的登录文件：

```bash
mkdir -p ~/.codex-cli/accounts/work
cxs use-home ~/.codex-cli/accounts/work
cxs run login
```

如果需要每个 home 使用独立的文件凭据，可在对应的基础 `config.toml` 中设置：

```toml
cli_auth_credentials_store = "file"
```

Codex 也支持 `keyring`、`auto` 和 `ephemeral`；这些模式的凭据生命周期由 Codex 和操作系统凭据存储管理，`cxs` 不会迁移它们。

## 命令

| 命令 | 作用 |
| --- | --- |
| `cxs list` | 列出当前 home 的 profile，`*` 是当前选择 |
| `cxs current` | 显示当前 home、profile、配置路径和 auth 文件是否存在 |
| `cxs new NAME --model MODEL ...` | 创建 profile；已有文件不会覆盖 |
| `cxs use NAME` | 选择 profile |
| `cxs clear` | 清除 profile 选择，使用 home 的基础配置 |
| `cxs show [NAME]` | 显示脱敏配置摘要 |
| `cxs path [NAME]` | 打印 profile 文件路径 |
| `cxs edit [NAME]` | 用 `$VISUAL`/`$EDITOR` 编辑 profile |
| `cxs homes` | 列出默认 home、Cockpit homes 和当前自定义 home |
| `cxs use-home REF` | 选择 `default`、Cockpit 的 `cli-*`，或一个已有目录 |
| `cxs run ...` | 设置选中的 `CODEX_HOME`，按需加入 `--profile`，原样执行 Codex |
| `cxs shell-init zsh` | 输出直接包装 `codex` 的 shell 函数 |

切换器状态保存在当前调用者默认 `CODEX_HOME/cli-switch/state.json`，权限为 0600；选中的 profile/home 只是名称和路径，不包含密钥。

## 设计依据

Codex 官方文档规定 profile 文件位于 `$CODEX_HOME/<name>.config.toml`，通过 `--profile <name>` 选择；profile 在基础用户配置之上叠加。自定义 provider 使用 `model_provider` 和 `[model_providers.<id>]`，推荐通过 `env_key` 引用环境变量；`experimental_bearer_token` 不适合作为长期配置。

- [Codex 配置基础](https://learn.chatgpt.com/docs/config-file/config-basic)
- [Codex 高级配置：Profiles 与 Custom model providers](https://learn.chatgpt.com/docs/config-file/config-advanced)
- [Codex 配置参考](https://learn.chatgpt.com/docs/config-file/config-reference)

### 已知边界

- `cxs use` 不会让未包装的现有 `codex` 进程变更配置；新进程必须通过 `cxs run` 或 shell 函数启动。
- `cxs` 不会验证 provider 的网络可达性，也不会替你启动 Cockpit sidecar 或 router。
- `cxs show` 只解析用于摘要的简单字段；未知字段会保留在原文件中，不会被重写。
- `cxs run` 使用真实的 `codex` 二进制；测试工具时可用 `CODEX_CLI_PATH` 指向一个本地替身，但生产运行不要这样配置。

## 开发与测试

项目没有第三方 Python 依赖：

```bash
python3 -m unittest discover -s tests -v
```
