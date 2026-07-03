该仓库目前**未集成**专业的结构化日志框架（如 Python `logging`、`loguru` 或 `structlog`）。其“日志”行为主要体现在以下两个层面：

1. **用户指令审计日志 (Command Audit Log)**：
   - **实现方式**：通过 `tools/log-command.sh` 脚本实现。该脚本由 Claude Code 的 `user_prompt_submit` hook 触发，将用户的输入指令以 JSONL 格式追加到 `logs/command-log.jsonl`。
   - **结构**：每条记录包含时间戳 (`time`) 和截断后的指令内容 (`prompt`)。
   - **目的**：用于追踪研究过程中的用户交互历史，并提供计数器提醒功能。
   - **存储**：日志存储在 `logs/` 目录下，该目录下的 `.counter` 文件被 `.gitignore` 排除，但 `command-log.jsonl` 未被明确排除（需注意隐私与体积）。

2. **工具脚本的基础输出 (Basic Output)**：
   - **实现方式**：在 `tools/` 目录下的 Python 脚本（如 `financial_rigor.py`）中，直接使用内置的 `print()` 函数向标准输出打印验算结果、警告或状态信息。
   - **特点**：缺乏日志级别（INFO/WARN/ERROR）管理，不支持文件持久化，仅作为交互式 CLI 的即时反馈。

**开发建议**：
- 若需增强可观测性，建议在 Python 工具中引入 `logging` 模块，配置统一的格式器（Formatter）和处理器（Handler）。
- 对于 `logs/command-log.jsonl`，建议在根目录 `.gitignore` 中增加 `logs/*.jsonl` 以防止敏感指令数据意外提交至版本控制系统。