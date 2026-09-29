# ADR 0002：用全局别名和 `codex` shim 切换 CODEX_HOME

- 状态：已采用
- 日期：2026-09-29
- Supersedes：ADR 0001

## 背景

实际工作流是从 Cockpit Tools 复制一个已有 CLI 实例的 `CODEX_HOME=/path` 命令。用户需要在任意工作区用一个短名称切换它，例如 `codex-cli use jessica`，随后直接输入 `codex` 就使用 Jessica 的 CLI 实例。

原先的 profile 管理器要求用户记住 `cxs run` 或配置 shell 函数，并且把模型、provider、Cockpit home 等多个概念放进同一套命令。这个界面超出了实际需求。

## 决策

1. 对外命令固定为 `codex-cli`，核心操作是 `add NAME CODEX_HOME=/path`、`list`、`use NAME`、`reset` 和 `help`。
2. 别名和当前选择保存在全局 `~/.codex-cli/config.json`，不依赖当前工作区，也不依赖当前 shell 的 `CODEX_HOME`。
3. 同目录提供 `codex` shim。shim 调用真实 Codex，并把当前选择注入为子进程的 `CODEX_HOME`。
4. `reset` 选择 `~/.codex`，保留已添加的别名和各目录内容。
5. `codex-cli` 只管理路径和状态，不复制、读取或修改目标 home 的 `auth.json`，不管理 provider、sidecar 或 Cockpit 进程。

## 理由

shell 子进程无法修改父 shell 的环境变量，因此单独运行 `codex-cli use` 不足以影响随后输入的 `codex`。把 `codex` 放在 PATH 前端作为 shim，才能让全局选择在不同工作区和新终端进程中生效。使用一个独立状态目录避免把管理器状态混入任何 Codex home。

## 后果

安装时必须把 `codex-cli` 和 `codex` 一起放到 PATH 前端。已经运行的 Codex 进程不会被重启；切换影响下一次启动的进程。真实 Codex 二进制通过 PATH 自动寻找，也可以用 `CODEX_REAL_BIN` 指定。

## 不在本决策中的事项

配置内容、API key、ChatGPT 登录、模型 provider、Cockpit 实例生命周期由 Codex 或 Cockpit 自己管理。本工具只提供全局路径别名和启动入口。
