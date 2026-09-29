# ADR 0003：为长路径 CODEX_HOME 使用短运行时 symlink

- 状态：Superseded by ADR 0004
- 日期：2026-09-29
- Supersedes：无

## 背景

Cockpit 为 CLI 实例生成的 `CODEX_HOME` 可能很长。Codex CLI 的 app-server daemon 会在这个目录下创建 Unix socket；macOS 对 Unix socket 地址有固定长度上限。路径超过上限时，CLI 会在 daemon 尚未就绪时退出，并提示 `path must be shorter than SUN_LEN`。

## 原决策

1. 别名配置继续保存 Cockpit 提供的真实 `CODEX_HOME`，不移动、复制或改写其中的文件。
2. 选中别名启动 Codex 时，在 `~/.codex-cli/homes/<name>` 创建指向真实目录的 symlink，并把这个短路径作为子进程的 `CODEX_HOME`。
3. 真实文件路径用于 `list`、`path` 和 `current` 的配置展示；`current` 额外显示实际注入的短运行时路径。
4. 管理器只更新自己创建的 symlink。若运行时路径被普通文件或目录占用，命令报错并保留占用者。

## 理由

Codex 只需要一个可读写的 `CODEX_HOME` 路径；短 symlink 能保持同一目录内容，同时让 daemon 构造的 socket 地址保持在 macOS 限制内。把运行时链接放在管理器自己的短目录下，不要求用户重命名 Cockpit 目录，也不改变别名的持久化语义。

## 验证结果与取代原因

Codex daemon 会在启动时把 `CODEX_HOME` symlink 解析为真实路径，随后仍用长路径构造 Unix socket。因此 symlink 不能绕过 macOS 的 `SUN_LEN` 限制；该方案由 ADR 0004 取代。
