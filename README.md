# codex-cli-switch（已弃用）

这个项目已经停止使用。现在由 Orca/Codex CLI 原生的多账户功能管理账号和
`CODEX_HOME`；本项目的全局 `codex` shim、`codex-cli` 状态文件和 shell 包装函数
不应继续安装或启用。

## 本机迁移

如果之前安装过本项目：

1. 从 `PATH` 中移除项目安装目录里的 `codex` 和 `codex-cli`。
2. 删除或停用 `.zshrc` 中由本项目添加的 `codex()` 包装函数。
3. 重启 Terminal，确认 `command -v codex` 指向 Orca/Codex 原生可执行文件。
4. 只有在 Orca 明确给出命令时，才使用 `CODEX_HOME=/path codex`；本项目不会再覆盖
   这个环境变量。

本仓库保留旧实现和决策记录，方便追溯；它们只代表历史方案，不再发布、维护或作为
安装说明。当前采用的方案记录在
[ADR 0005](docs/decisions/0005-native-orca-account-management.md)。

## 许可

MIT，见 [LICENSE](LICENSE)。
