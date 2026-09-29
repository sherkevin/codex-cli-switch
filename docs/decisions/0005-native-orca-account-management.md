# ADR 0005：使用 Orca 原生多账户管理并停用自定义切换器

- 状态：已采用
- 日期：2026-09-29
- Supersedes：ADR 0002、ADR 0003、ADR 0004

## 背景

Orca 已经可以原生管理 Codex CLI 的多个账户和实例。自定义切换器同时提供了
`codex-cli` 状态、shell `codex()` 函数和 PATH 前置的 `codex` shim；这些入口都可能
修改 `CODEX_HOME`。当两个管理层同时存在时，终端中看到的实例可能不是 Orca 当前选择
的实例，且启动参数和认证配置会互相覆盖。

## 决策

1. Orca/Codex CLI 原生账户管理是唯一的账号和 `CODEX_HOME` 来源。
2. 不再安装或启用本项目的 `codex` shim、`codex-cli` 命令和 shell 包装函数。
3. 本项目不再自动注入 `CODEX_HOME`、provider、API key、sidecar 地址或其他认证信息。
4. 终端中的 `codex` 必须解析到 Orca/Codex 原生可执行文件；显式的
   `CODEX_HOME=/path codex` 由用户或 Orca 自己控制。
5. 仓库保留历史实现和决策记录，但 README 明确标记为弃用，不再作为安装入口。

## 理由

账户选择和认证状态应由创建它们的管理器解释。保留第二套全局状态会让同一个命令名
有两个可能的行为来源，也无法可靠判断哪个实例应该优先。移除包装层后，Codex CLI
只读取 Orca 或用户在当前进程中提供的环境，配置边界只有一个。

## 后果

旧的 `codex-cli add/use/reset` 命令不再可用；用户应使用 Orca 的账户管理界面或它
生成的启动命令。之前的自定义状态不需要删除即可停用，恢复时可以从本机迁移备份中
取回；官方 `~/.codex` 目录和 Orca 创建的实例目录不被本项目改写。

## 验证

新终端中 `command -v codex` 应显示 Orca/Codex 原生路径，`type -a codex` 不应再显示
本项目的 shim。由 Orca 生成的 `CODEX_HOME=/path codex` 命令应原样传给原生 CLI。
