该项目是一个基于 **Claude Code** 的价值投资研究框架，其“构建系统”并非传统的代码编译或容器化部署，而是围绕 **AI Agent 协作、数据精确校验与报告标准化发布** 建立的一套自动化工作流。

### 1. 核心构建与执行环境
- **运行时**：依赖 `@anthropic-ai/claude-code` CLI 工具。项目通过 `skills/*.md` 文件定义 16 个标准化的投研指令（如 `/investment-team`, `/earnings-review`），这些文件需复制到 `~/.claude/commands/` 目录下作为全局命令使用。
- **执行模式**：采用 **多 Agent 并行架构**。例如 `/investment-team` 会同时启动 4 个独立 Agent（分别扮演段永平、巴菲特、芒格、李录视角）进行并行搜索与分析，最后由 Team Lead Agent 汇总输出。

### 2. 数据严谨性与自动化工具链 (`tools/`)
为解决 LLM 在金融计算中的幻觉问题，项目内置了一套 Python 工具集作为“构建验证层”：
- **精确计算引擎**：`tools/financial_rigor.py` 使用 `decimal.Decimal` 替代浮点数，提供市值验算 (`verify-market-cap`)、估值指标计算 (`verify-valuation`) 及 Benford 定律检测，确保财务数据的数学严谨性。
- **量化回测与筛选**：`tools/momentum_backtest.py` 和 `tools/stock_screener.py` 用于动量价值双因子回测及全市场去劣筛选，支持从数据到决策的闭环验证。
- **情报采集**：`tools/xueqiu_scraper.py` 用于从社交媒体（雪球）采集实时市场情绪与大师发言。
- **日志审计**：`tools/log-command.sh` 配合 Claude Code 的 hook 机制，自动记录用户指令至 `logs/command-log.jsonl`，用于后续的研究复盘与上下文补充。

### 3. 报告产出与版本控制规范
- **标准化目录结构**：所有研究报告必须按公司名归档于 `reports/{Company}/` 目录下，遵循严格的命名规范（如 `{公司名}-research-{YYYYMMDD}.md`）。
- **Git 发布流程**：项目采用手动 Git 工作流。开发者在完成报告后，需执行 `git pull --rebase origin main` 解决冲突，并使用中文 Commit Message 推送至 GitHub。禁止推送中间过程文件（如 `data_collection.md`）。
- **质量门禁**：报告生成后需经过“客观性原则”审查（区分事实与观点），关键数据需至少 2 个来源交叉验证，并强制输出明确的投资建议（通过/不通过/灰色地带）。

### 4. 开发者约定
- **技能安装**：新成员需手动同步 `skills/` 目录下的 `.md` 文件到本地 Claude Code 配置目录。
- **数据校验**：涉及市值、PE 等关键指标时，必须调用 `financial_rigor.py` 进行手算校验，严禁直接采信 LLM 的心算结果。
- **语言与风格**：所有产出物必须为中文，风格要求直接犀利，禁止模棱两可的“平衡式”分析。