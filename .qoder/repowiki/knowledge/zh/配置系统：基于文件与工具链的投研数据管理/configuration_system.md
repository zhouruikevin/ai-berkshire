该项目（AI Berkshire）是一个基于 AI Agent 的价值投资研究框架，其“配置系统”并非传统意义上的应用运行时配置（如 `application.yaml` 或 `.env`），而是体现为**投研数据源、关注列表与计算工具的静态化管理**。系统通过 JSON 文件管理股票池与基本面数据，通过 Python 脚本封装外部 API 交互逻辑，并通过 Markdown 文件定义 Agent 的行为规范。

### 1. 核心配置方式
*   **静态 JSON 数据源**：使用 `data/` 目录下的 JSON 文件作为核心数据配置。`watchlist.json` 定义了分板块（AI芯片、AI应用、港股互联网等）的股票关注池；`fundamentals.json` 存储了关键财务指标（营收增速、毛利率、EPS超预期）的历史季度数据，供量化工具读取。
*   **环境变量注入**：在涉及敏感操作的工具中（如 `tools/xueqiu_scraper.py`），采用环境变量（`XQ_PHONE`, `XQ_PASSWORD`）注入凭据，避免硬编码，符合安全最佳实践。
*   **行为即配置（Skills as Config）**：系统的核心逻辑由 `skills/` 目录下的 Markdown 文件定义。这些文件充当了 AI Agent 的“系统提示词配置”，规定了不同投研场景（如深度研究、财报分析、行业筛选）下的执行流程、输出格式和思维框架（四大师视角）。

### 2. 关键文件与路径
*   **数据配置**：
    *   `data/watchlist.json`：定义默认扫描的股票标的，支持按赛道分组。
    *   `data/fundamentals.json`：结构化存储个股季度财务表现，是动量筛选工具的核心输入。
*   **工具配置与逻辑**：
    *   `tools/financial_rigor.py`：金融严谨性工具，内置精确十进制计算引擎，提供市值验算、估值指标计算、多源交叉验证等 CLI 接口。
    *   `tools/stock_screener.py`：动量发现与价值验证工具，读取 `watchlist.json` 和 `fundamentals.json` 执行自动化选股。
    *   `tools/morningstar_fair_value.py`：配置了 Morningstar API 的抓取逻辑与筛选条件（如公允价值估计非空）。
    *   `tools/xueqiu_scraper.py`：雪球爬虫，通过 `--state-path` 参数配置登录态缓存路径，支持断点续爬。
*   **Agent 行为规范**：
    *   `CLAUDE.md` / `ai_CLAUDE.md`：项目级指令与记忆文件，配置了报告目录结构、命名规范、Git 推送流程以及投研核心原则（如客观性、反偏见机制）。
    *   `skills/*.md`：16 个投研 Skill 的定义文件，决定了 Agent 在不同任务下的行为模式。

### 3. 架构约定与开发规则
*   **零外部依赖原则**：核心计算工具（如 `financial_rigor.py`）仅使用 Python 标准库，确保在任何环境下均可直接运行，无需复杂的虚拟环境配置。
*   **数据与逻辑分离**：股票池和基础财务数据外置为 JSON，工具脚本通过读取这些文件执行逻辑，使得更新关注列表或补充财务数据无需修改代码。
*   **精确计算强制化**：在涉及金融计算时，强制使用 `decimal.Decimal` 而非 `float`，并通过 `tools/financial_rigor.py` 提供统一的验算入口，防止浮点误差导致的决策偏差。
*   **本地状态持久化**：爬虫类工具（如雪球 scraper）将登录态（Storage State）持久化到本地文件系统（默认 `/tmp/xueqiu_state.json`），并通过进度文件实现断点续爬，减少重复登录的配置开销。