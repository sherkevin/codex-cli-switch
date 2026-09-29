# ADR 0001：用 Codex 原生 profile 和 `CODEX_HOME` 作为切换边界

- 状态：Superseded by ADR 0002
- 日期：2026-09-29

## 背景

需求是让终端里的 Codex CLI 像 Cockpit 一样切换配置。切换内容有两种：模型/provider 等 TOML 配置，以及不同账号的登录态、会话和缓存。它们不是同一个状态边界。Codex Desktop 的切号动作也不会自动改变当前 shell 中的 CLI。

Codex CLI 0.157.1 已提供 `--profile`。官方文档规定 profile 文件放在 `$CODEX_HOME/<name>.config.toml`，作为基础配置的叠加层。官方也把自定义 provider 放在用户级配置层，并建议用 `env_key` 引用环境变量。

## 决策

1. `cxs new/use` 管理 Codex 原生 profile 文件，不改写基础 `config.toml`。
2. `cxs run` 设置选中的 `CODEX_HOME`，并在没有显式 `--profile` 时加入当前 profile，然后执行真实的 `codex`。
3. 选择状态另存为 `<默认 CODEX_HOME>/cli-switch/state.json`，不随被选中的 home 移动。
4. Cockpit `cli-*` 目录只作为已有 `CODEX_HOME` 被发现和选择；不复制、不解析、不输出 `auth.json` 内容。
5. profile 中只写环境变量名（`env_key`），不写 API key、Bearer token 或静态授权 header。

## 理由

原生 profile 的优先级和文件命名由 Codex 自己解释，升级时比复制整份配置更稳定。`CODEX_HOME` 是 Codex 管理 auth、config、session 的自然隔离根，能复用 Cockpit 已创建的 CLI 实例。把选择状态独立保存，避免切到另一个 home 后找不到切换器自己的状态。

## 后果

用户需要使用 `cxs run`，或在 shell 中定义 `codex()` 包装函数；一次子进程无法改变父 shell 的环境。不同 home 如果使用操作系统 keyring，凭据是否按 home 隔离由 Codex/操作系统决定；需要文件隔离时可显式设置 `cli_auth_credentials_store = "file"`。同一个 Cockpit home 不应被两个进程同时写入。

## 不在本决策中的事项

本工具不启动或管理 Cockpit sidecar/router，不替用户探测 provider 是否可达，也不尝试把 Desktop 的当前账号复制到 CLI。未来若需要这些能力，应另写 ADR。
