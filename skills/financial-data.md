---
name: financial-data
description: 财务数据获取与交叉验证规范。确保每个关键数据来自两个独立来源，误差大于1%须标记。
---

# 财务数据获取与交叉验证规范

本规范适用于所有涉及企业财务数据的研究。**每个关键数据必须来自两个独立来源，误差>1%须标记。**

---

## 数据源优先级

### 美股（PDD、腾讯ADR、网易ADR等）

| 优先级 | 来源 | URL | 获取方式 |
|--------|------|-----|---------|
| 1（主） | **macrotrends** | macrotrends.net/stocks/charts/{ticker} | 直接访问，无需注册 |
| 2（副） | **stockanalysis** | stockanalysis.com/stocks/{ticker}/financials | 直接访问，无需注册 |
| 原始一手 | SEC EDGAR | sec.gov/cgi-bin/browse-edgar | 10-K / 10-Q 原文 |

### 港股（腾讯0700、网易9999、美团3690等）

| 优先级 | 来源 | URL | 获取方式 |
|--------|------|-----|---------|
| 1（主） | **aastocks** | aastocks.com/tc/stocks/analysis/company-fundamental | 直接访问 |
| 2（副） | **macrotrends**（ADR代码） | 腾讯用TCEHY，网易用NTES | 直接访问 |
| 原始一手 | HKEX披露易 | hkexnews.hk | 年报PDF |

### A股（多氟多、工业富联、兆易创新等）

| 优先级 | 来源 | URL | 获取方式 |
|--------|------|-----|--------|
| 1（主） | **TuShare Pro** | API 调用 | `python3 tools/tushare_fetcher.py quote <代码>` 或 `update-all` |
| 2（副） | **东方财富** | eastmoney.com → 搜股票代码 → 财务报表 | 直接访问（交叉验证用） |
| 原始一手 | **巨潮资讯** | cninfo.com.cn | 原始年报/季报PDF |

#### TuShare Pro 快速命令

```bash
# 估值快照（PE_TTM/PB/市值）
python3 tools/tushare_fetcher.py quote 002407.SZ

# 批量估值（watchlist 中所有 A 股）
python3 tools/tushare_fetcher.py batch-quote

# 财务指标（最近季度 EPS/ROE/毛利率）
python3 tools/tushare_fetcher.py financials 002407.SZ

# 利润表（营收/净利润 + 同比）
python3 tools/tushare_fetcher.py income 002407.SZ

# 资产负债表（总资产/总负债/净资产/资产负债率）
python3 tools/tushare_fetcher.py balancesheet 002407.SZ

# 现金流量表（经营/投资/筹资/自由现金流）
python3 tools/tushare_fetcher.py cashflow 002407.SZ

# 更新本地缓存（单只/全部，含以上全部数据）
python3 tools/tushare_fetcher.py update 002407.SZ
python3 tools/tushare_fetcher.py update-all
```

#### TuShare API 接口参考

| 接口 | 用途 | 数据时效 |
|------|------|--------|
| `daily_basic` | PE(TTM)/PB/总市值/流通市值 | 当日收盘后更新 |
| `daily` | 日线行情（开高低收量） | 当日收盘后更新 |
| `fina_indicator` | 财务指标（EPS/ROE/毛利率等） | 财报发布后更新 |
| `income` | 利润表（营收/净利润） | 财报发布后更新 |
| `balancesheet` | 资产负债表（总资产/负债/净资产/货币资金） | 财报发布后更新 |
| `cashflow` | 现金流量表（经营/投资/筹资/自由现金流） | 财报发布后更新 |

### 台股（台积电2330、联发科2454、大立光3008等）

| 优先级 | 来源 | URL | 获取方式 |
|--------|------|-----|---------|
| 1（主） | **FinMind API** | api.finmindtrade.com | `tools/twstock_data.py`（零依赖脚本，见下） |
| 2（副） | **Goodinfo台湾股市资讯网** | goodinfo.tw/tw/StockDetail.asp?STOCK_ID={代码} | 直接访问 |
| 原始一手 | 公开资讯观测站（MOPS） | mops.twse.com.tw | 财报原文/月营收公告 |

**FinMind 取数工具**（分析台股时优先调用，输出自带市值验算）：

```bash
python3 tools/twstock_data.py quote 2330        # 最新行情 + PER/PBR/殖利率 + 市值验算
python3 tools/twstock_data.py valuation 2330    # 估值指标 + PER一年区间 + 52周高低
python3 tools/twstock_data.py financials 2330   # 近5年年度核心财务（营收/毛利率/归母净利/EPS/ROE）
python3 tools/twstock_data.py revenue 2330      # 近13个月月营收及同比
python3 tools/twstock_data.py dividend 2330     # 近年股利政策（现金/股票股利、除息日）
python3 tools/twstock_data.py search 台積        # 搜索股票代码（注意台股名称为繁体）
```

台股特别注意：

1. **货币单位是新台币（TWD）**，与港币/人民币/美元混排时必须显式标注，跨市场对比先统一换算
2. **月营收是台股独有优势**：上市柜公司每月10日前强制披露上月营收，是跟踪基本面拐点最快的公开信号，earnings-review/thesis-tracker 类分析应优先利用（`revenue` 子命令）
3. FinMind 损益表为**单季值**，工具已自动加总为年度值；不足4季的年份会标注"仅前N季累计"
4. FinMind 未注册可直接用（有小时级限额）。注册后的 API token **只存本机、严禁提交到 git**，工具按优先级自动读取：①环境变量 `FINMIND_TOKEN`；②本地文件 `local/finmind_token.txt`（`local/` 已被 `.gitignore` 永久排除，把 token 单独一行写入该文件即可）。token 不得出现在报告、skill、commit 中
5. 交叉验证：FinMind 数值与 Goodinfo（或 macrotrends 上的 ADR，如 TSM）对照，误差规则同下；台积电等有 ADR 的公司注意 ADR 与台股原股的汇率/存托比率差异（1 TSM ADR = 5 股 2330）

---

## 执行规范

### 第一步：获取数据

对每个财务指标（收入、净利润、毛利率、经营现金流、资产负债率等），分别从**来源1**和**来源2**取数。

### 第二步：误差计算与标记

```
误差率 = |来源1数值 - 来源2数值| / 来源1数值 × 100%
```

| 误差 | 处理方式 |
|------|---------|
| ≤ 1% | ✅ 一致，取来源1数值，标注两个来源 |
| 1% ~ 5% | ⚠️ 标记"数据存在差异"，注明两个数值，说明可能原因（汇率/会计口径） |
| > 5% | ❌ 标记"数据存在重大差异"，必须查原始财报核实，不得直接使用 |

### 第三步：数据呈现格式

每个关键数据必须按以下格式标注：

```
收入：1,239亿元 ✅
  - macrotrends: 1,241亿元
  - stockanalysis: 1,237亿元
  - 误差: 0.3%
```

差异示例：
```
净利润：245亿元 ⚠️ 数据存在差异
  - macrotrends: 245亿元（GAAP）
  - stockanalysis: 278亿元（Non-GAAP）
  - 误差: 13.5% — 原因：会计口径不同（GAAP vs Non-GAAP）
```

---

## 常见差异原因（不一定是数据错误）

| 原因 | 说明 |
|------|------|
| GAAP vs Non-GAAP | 最常见，尤其是利润类数据 |
| 汇率换算 | 港币/人民币/美元换算时间点不同 |
| 财年定义 | 自然年 vs 财年（如苹果财年10月结束） |
| 合并口径 | 是否含少数股东权益 |
| 数据更新滞后 | 某平台尚未更新最新一期财报 |

---

## 数据时效性要求

> **日期锚定**：当前日期为 `$CURRENT_DATE`。

| 数据类型 | 时效性要求 | 判断标准 |
|---------|-----------|---------|
| 年度财报数据 | 必须包含截至今日已披露的最近完整财年 | 如今天2026年6月，多数公司2025年报已披露 → 必须用2025年数据 |
| 季度数据 | 必须包含截至今日已披露的最近季度 | 如2026年6月 → 2026Q1已披露（多数公司4-5月披露Q1） |
| 股价/市值 | 必须为最近一个交易日收盘价 | 标注具体日期（如"2026年6月20日收盘价"） |
| 装机/产能等运营数据 | 必须为最近已披露的报告期数据 | 优先取季报/半年报中的运营数据 |

**时效性检查**：如果数据源尚未更新最新一期财报，必须标注"**数据截至XXXX年X季度，尚未更新至最新期**"，不得默认使用过期数据。

---

## 特别规则

1. **未上市公司**（米哈游、莉莉丝等）：只有一手数据来源时，数据前标记 `[估计]`，不执行交叉验证
2. **季度数据 vs 年度数据**：优先使用年度数据做交叉验证，季度数据部分来源可能有滞后
3. **原始财报优先**：若两个来源均与原始财报（10-K/年报PDF）不符，以原始财报为准，标记来源错误

---

## 股价与复权（历史序列必读）

价格有三种口径，混用会让历史股价位置、长期涨幅、历史估值分位全部失真：

| 口径 | 含义 | 用途 |
|------|------|------|
| 不复权 | 实际成交价，除权除息日跳空 | 仅用于"当前时点"快照 |
| 前复权 | 以最新价为基准回调历史价 | 历史股价对比、N年涨幅、历史PE band 一律用它 |
| 后复权 | 以上市首日为基准前推 | 计算历史总回报/年化收益 |

规则：

1. 涉及历史价格的分析统一用**前复权**，且同一分析内**不得混用**复权与不复权来源。
2. 当前市值/当前PE 用**当前实际股价 × 当前总股本**即可，与复权无关——复权只影响历史序列。
3. 跨越拆股/大比例送转的每股指标（历史EPS、历史股价），必须复权还原后再同比。
4. 总回报/年化收益需计入分红（后复权已含），只看价格涨幅会低估。
5. 增发/回购后市值验算以最新总股本为准（`financial_rigor.py verify-market-cap` 偏差>5% 会提示核对）。

---

## 快速索引

| 场景 | 主要来源 | 备用来源 |
|------|---------|--------|
| A 股（多氟多、工业富联等） | TuShare Pro API | 东方财富 |
| 三七互娱 | TuShare Pro（002555.SZ） | eastmoney.com |
| 吉比特 | TuShare Pro（603444.SH） | eastmoney.com |
| PDD / 拼多多 | macrotrends.net/stocks/charts/PDD | stockanalysis.com/stocks/pdd |
| 腾讯 | macrotrends.net/stocks/charts/TCEHY | aastocks（0700.HK） |
| 网易 | macrotrends.net/stocks/charts/NTES | aastocks（9999.HK） |
| Nintendo | macrotrends.net/stocks/charts/NTDOY | stockanalysis.com/stocks/ntdoy |
| Capcom | macrotrends（CCOEY） | stockanalysis（CCOEY） |
| 台积电 | tools/twstock_data.py（2330） | goodinfo.tw / macrotrends（TSM，注意1 ADR=5股） |
| 联发科 | tools/twstock_data.py（2454） | goodinfo.tw |
