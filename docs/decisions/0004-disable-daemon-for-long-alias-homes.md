# ADR 0004：长路径别名启动时关闭 Codex 共享 daemon

- 状态：Superseded by ADR 0005
- 日期：2026-09-29
- Supersedes：ADR 0003

## 背景

Cockpit 的 CLI `CODEX_HOME` 可能很长。Codex CLI 0.157.1 的共享 app-server daemon 会把 `CODEX_HOME` 解析为真实路径，再在其下构造 Unix socket。macOS 对 Unix socket 地址有固定长度上限，导致交互启动报 `path must be shorter than SUN_LEN`。

## 决策

1. 别名仍直接注入 `add` 保存的真实 `CODEX_HOME`，不移动、复制或改写 Cockpit 目录。
2. active alias 启动交互 TUI、`resume` 或 `fork` 时，shim 自动加入 Codex 官方的 `--no-daemon` 参数。
3. `exec` 等已有独立执行路径保留原始参数，不盲目加入不被子命令接受的全局选项。
4. 未选择别名时保持官方 `~/.codex` 的原始启动行为。

## 理由

`--no-daemon` 是 Codex 自己提供的路径，绕过产生长 Unix socket 的共享后台服务，同时继续使用真实 `CODEX_HOME`，所以登录态、配置、会话和新写入内容都留在 Cockpit 原目录。它不依赖 macOS 额外挂载工具，也不要求移动用户目录。

## 后果

active alias 的交互启动不共享 Codex 后台 daemon，可能失去跨进程复用带来的启动优化。用户仍可显式运行真实 Codex 并自行传入其他参数；如果未来 Codex 改进长路径处理，可以在新 ADR 中重新评估默认策略。
