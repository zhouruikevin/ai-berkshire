---
name: valuation-percentile
description: 历史估值分位：以周为单位计算个股历史PE/PB时间序列，定位当前PE与远期预估PE在历史分布中的百分位（便宜/贵）。默认回溯2年，可指定更长年限。
---

## Qoder adapter note

This skill is generated from `skills/valuation-percentile.md`. Qoder and Claude Code share one canonical workflow.

- **Tool mapping**: This skill may reference `Task` (background agent), `Team` (multi-agent), or `run_in_background`. In Qoder, use the `Agent` tool for background/sub-agents (with `is_background=true` for Bash) and launch multiple parallel `Agent` calls instead of `Team`.
- **Permission config**: `.claude/settings.local.json` references do not apply. In Qoder, tool permissions are handled by the IDE; if a tool is blocked, grant it via the IDE's permission prompt.
- **Project rules**: References to `CLAUDE.md` are for project conventions. Qoder uses `AGENTS.md` and `.qoder/rules/` for the same purpose — follow whichever file is present and scoped to your role.
- **Placeholders**: `$ARGUMENTS` and `$CURRENT_DATE` work identically in Qoder.
- **Report output**: Use `qoder_report/` as the output directory (see CLAUDE.md report naming conventions).
- **Shared tools**: Commands use workspace-relative paths (`python3 tools/...`), run from the repo root.

# 历史估值分位：当前 PE / 远期 PE 在历史周频分布中的位置

对 $ARGUMENTS 计算历史估值分位——以「周」为单位构建历史 PE_TTM / PB 时间序列，判断**当前值**与**远期预估值**落在其历史分布的哪个百分位（便宜还是贵），用于"贵/贱"锚定与择时参考。

所有确定性计算（周频重采样、分位、远期 PE）一律通过 `tools/valuation_percentile.py` 完成，**禁止 LLM 心算分位**。

## 日期锚定

当前日期为 `$CURRENT_DATE`。回溯窗口**默认 2 年**（约 ~104 个周样本），`end_date` = 今日；**外部可通过 `--years N` 或 `--start YYYYMMDD` 指定更长年限，无上限**。远期一致预期数据必须标注来源与获取时间，搜索 query 中必须包含当前年份。

## 设计原则

- **分位是相对该股回溯窗口内自身**的位置（默认近 2 年），不等于跨牛熊周期的绝对贵贱。历史"贵"≠现在贵：成长提速会抬高合理中枢、降速会压低——分位低也可能是价值陷阱。
- **PE 与 PB 双维度**：亏损/周期股 PE 失真时，PB 分位更稳健。
- **远期 PE 是近似**：远期 PE 基于预估盈利，却对照历史 trailing(TTM) 分布定位，属跨口径近似，必须在报告注明。
- 亏损期（PE_TTM≤0）已从 PE 分布剔除，剔除周数在输出中体现。

## 执行流程

### 第一步：判定市场

按代码后缀判定：`.SH/.SZ/.BJ` 或 6/0/3 开头 6 位 → **A股**；`.HK` → 港股；纯字母 → 美股。

### 第二步（A股）：端到端全自动

```bash
python3 tools/valuation_percentile.py ashare <code> --growth <未来一年一致预期增速>
# 指定更长回溯（默认2年）：--years 5   或   --start 20150101
# 显式远期EPS（远期PE）：--forward-eps <远期EPS>
# 远期PB（可选，需远期每股净资产）：--forward-bvps <远期BVPS>
python3 tools/valuation_percentile.py ashare <code> --forward-eps <远期EPS> --forward-bvps <远期BVPS>
```

- `ashare` 自动经 TuShare `daily_basic` 拉取回溯期逐日 `pe_ttm`/`pb` → 周频重采样 → 分位。默认回溯 2 年，`--years N` / `--start YYYYMMDD` 可指定更长。
- 输出含 `周频历史序列`（逐周 date/PE/PB），供报告呈现「历史 PE 数据」与当前/远期落点。
- 远期 PB 需 `--forward-bvps`（web 搜远期每股净资产一致预期）；缺省则如实标注"未计算"。
- 远期增速/EPS：先 web 搜"未来 1 年一致预期净利润/EPS 增速"（券商研报、Wind/东财一致预期、雪球），**标注来源与日期**；用户可手动指定 `--growth` / `--forward-eps` 覆盖。
- 若无远期数据，省略 `--growth`，仅输出当前 PE/PB 分位。

### 第三步（美股/港股）：周线价 + 历史 TTM EPS 组装

```bash
# 1) 取周线价
python3 tools/valuation_percentile.py weekly-prices <ticker> > /tmp/prices.json
# 2) 用 financial-data skill / web 补历史季度 TTM EPS（macrotrends、stockanalysis）
#    组织为 [{"date":"2024-03-31","eps_ttm":x}, ...] 存 /tmp/eps.json
# 3) 组装 PE 序列并定位
python3 tools/valuation_percentile.py pe-series \
  --prices /tmp/prices.json --eps /tmp/eps.json --forward-eps <远期EPS>
```

- 历史 TTM EPS 需覆盖近 2 年各报告期（至少每季一点），来源逐一标注。
- **必须在报告显著位置标注**：美股/港股历史 EPS 由外部补入，可能有缺口/口径差异，**可靠性低于 A股 tushare 口径**；PB 分位在此路径不计算（除非另有可靠历史 BVPS）。

### 第四步：交叉验证当前值

用 `tools/tushare_fetcher.py quote <code>`（A股）或行情站点核对当前 PE 与工具输出一致（误差 >1% 须说明）。

## 输出格式

```markdown
# {公司名}（{代码}）历史估值分位报告

**日期**：{当天日期}　**回溯窗口**：{近N年}（周频，{周样本数}个样本）　**数据源**：{TuShare / Yahoo+外部EPS}

## 一、估值分位总览（当前值 & 远期值所处位置）

| 指标 | 当前值 | 历史百分位 | 所处区间 | 远期值 | 远期百分位 | 远期区间 |
|------|-------|-----------|---------|-------|-----------|---------|
| PE_TTM | {x} | {p}% | {低估区/偏低/合理/偏高/高估区} | {远期PE} | {p}% | {区间} |
| PB | {x} | {p}% | {区间} | {远期PB或"未计算"} | {p}% | {区间} |

> 区间口径：<20% 低估区 / 20–40% 偏低 / 40–60% 合理 / 60–80% 偏高 / >80% 高估区
> 远期PB 仅在提供远期每股净资产（`--forward-bvps`）时计算；否则如实标注"未计算"，不臆造。

## 二、历史区间（分布关键分位）

| 指标 | min | p25 | 中位数 | p75 | max | 剔除周数 |
|------|-----|-----|-------|-----|-----|---------|
| PE_TTM | | | | | | {亏损周} |
| PB | | | | | | |

## 三、历史 PE/PB 数据（周频序列）

取工具输出的 `周频历史序列`，**按月末（每月最后一个周样本）抽样**成表呈现，行数过多时正文放月末抽样、完整逐周序列放文末附录：

| 日期 | PE_TTM | PB |
|------|--------|----|
| {YYYY-MM} | {pe} | {pb} |
| … | | |
| {当前周} | {pe}★当前 | {pb}★当前 |

（标出当前值、远期 PE/PB 相对该序列的落点；有条件可附一句走势/极值描述或简单折线示意。）

## 四、周频走势描述
{回溯期内 PE/PB 的高低点、当前处于什么位置、最近趋势方向，用数据描述}

## 五、正反两面
**为何"便宜"（低分位的支撑）**：{数据支撑}
**但另一方面（是否价值陷阱）**：{盈利质量、增速降档、行业Beta下移、一次性利润扰动等反面论据}

## 六、远期一致预期
- 未来一年增速/EPS：{数值}（来源：{XX研报/一致预期}，{日期}，估计）
- 远期每股净资产（如用于远期PB）：{数值}（来源，估计）
- 远期 PE/PB 计算方式与近似性说明

## 七、结论与评分
估值吸引力：{★1-5}
{结论必须从分位数据自然推出，不预设立场}

## 八、数据来源与局限
- 数据源、交叉验证、误差
- 局限性声明（见下）

## 附录：完整周频 PE/PB 序列（可选）
{逐周 date / PE_TTM / PB，来自工具 `周频历史序列`}
```

## 输出要求

1. **报告位置**：`qoder_report/{公司名}/{公司名}-valuation-{YYYYMMDD}.md`（放公司文件夹内）。
2. **语言**：中文；风格直接、犀利、不说废话。
3. **数据**：所有数据标注来源；关键数据（如当前 PE）2 源交叉验证；估计值标"估计"。
4. **不预设立场**：先摆分位数据 → 推逻辑 → 出结论；不预设看多/看空。
5. **正反两面**：低分位必须附"是否价值陷阱"的反面论据；高分位必须附"是否成长消化估值"的反面论据。
6. **评分**：用 ★（★1-5，不含半星）。
7. 穿插巴菲特/芒格/段永平/李录关于"价格 vs 价值""别人贪婪我恐惧"的语录点评。

## 局限性声明（必须写入报告）

- 分位是相对该股**回溯窗口内自身**的相对位置（默认近 2 年）；若窗口短则不覆盖完整牛熊周期，历史"便宜/贵"不等于当下绝对便宜/贵。回溯越长可比性越强，但早期成长阶段的高估值也会拉高分布。
- 远期 PE 基于预估盈利、对照历史 trailing 分布，属**跨口径近似**定位。
- 亏损期 PE 已剔除；周频取每周最后一个交易日。
- 美股/港股历史 EPS 依赖外部补入，可能有缺口，可靠性低于 A股。
