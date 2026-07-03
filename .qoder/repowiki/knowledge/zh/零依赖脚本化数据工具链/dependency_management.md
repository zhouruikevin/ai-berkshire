该仓库采用**零外部依赖（Zero-dependency）**的 Python 脚本化策略进行数据获取与金融计算，未使用传统的包管理器（如 pip/poetry/npm）或锁文件机制。

### 1. 核心策略：标准库优先
- **无第三方依赖**：核心工具 `tools/financial_rigor.py` 明确声明仅使用 Python 标准库（`decimal`, `json`, `math`, `argparse`），确保在任何安装了 Python 3.7+ 的环境中即可直接运行，无需 `pip install`。
- **精确计算引擎**：为避免浮点数误差，所有金融计算（市值、PE、ROE 等）均使用 `decimal.Decimal` 模块实现精确十进制运算，替代了常见的 `float` 或 `numpy`。

### 2. 关键工具与隐式依赖
- **金融严谨性工具 (`financial_rigor.py`)**：提供市值验算、估值指标交叉验证、Benford 定律检测等功能。作为 CLI 工具被 Claude Code Skills 自动调用，不依赖任何外部 API 客户端库。
- **雪球爬虫 (`xueqiu_scraper.py`)**：这是仓库中唯一引入外部依赖的模块，依赖 **Playwright** (`playwright.async_api`) 进行浏览器自动化操作。其依赖管理依赖于用户本地环境的全局安装或手动配置，未在项目中通过 `requirements.txt` 固化。
- **其他脚本**：`stock_screener.py`、`momentum_backtest.py` 等同样遵循标准库优先原则，部分可能依赖 `pandas` 或 `numpy`（需进一步确认代码内部 import，但当前 `financial_rigor.py` 明确强调零依赖）。

### 3. 敏感信息与状态管理
- **环境变量注入**：爬虫所需的凭据（如 `XQ_PHONE`, `XQ_PASSWORD`）通过环境变量传入，严禁硬编码在代码中。
- **本地状态持久化**：登录态（Cookies/Storage State）保存在本地临时路径（如 `/tmp/xueqiu_state.json`），并通过 `.gitignore` 排除在版本控制之外，防止敏感信息泄露。

### 4. 开发者规范
- **禁止引入重型框架**：为保持工具的轻量级和可移植性，避免引入 Web 框架或复杂的 ORM。
- **手动环境配置**：由于缺乏统一的依赖清单，新成员需根据脚本头部的注释手动安装必要的运行时（如 Python 3.7+ 和 Playwright 驱动）。
- **数据验证纪律**：所有关键金融数据必须经过 `financial_rigor.py` 中的交叉验证逻辑（至少两个独立来源），偏差超过阈值（默认 2%）时需人工介入。