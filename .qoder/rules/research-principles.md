# 投研分析核心原则

## 客观性（最高优先级）

- **客观、客观、客观**——所有投研分析必须基于事实和数据，严禁主观臆断
- 严格区分"事实"与"观点"：事实用数据支撑，观点必须明确标注为"观点"或"推测"
- **不预设立场**：不预设看多或看空，先摆数据、再推逻辑、最后得结论。结论必须从数据中自然推出
- 禁止使用"我认为"、"我觉得"、"显然"等主观表述，改用"数据显示"、"证据表明"、"根据XX来源"
- **呈现正反两面**：每个核心判断都必须附带反面论据（"但另一方面..."），让读者自己权衡
- 对不确定的事情诚实说"不确定"或"数据不足"，不要用推测填充确定性

## 报告语言与风格

- 所有报告使用**中文**
- 风格：直接、犀利、不说废话
- 数据必须标注来源，关键数据至少2个来源交叉验证
- 估计值必须注明"估计"
- 评分使用★符号（★1-5），不含半星
- 穿插巴菲特/芒格/段永平/李录的语录点评

## 报告目录结构

> **输出目录（2026-07-03 起）**：新生成的报告统一输出到 `qoder_report/`（结构/命名同下）。原 `reports/` 为历史归档只读；`portfolio-latest.md`、`{公司名}-thesis.md`、`bottleneck-map/` 三类活文件仍在 `reports/` 维护。

所有报告按**公司名**建文件夹，公司相关的所有报告放在对应文件夹内。行业报告、漏斗筛选报告、主题级综合报告放 qoder_report/ 根目录。

## 报告命名规范

| Skill | 文件命名格式 |
|------|---------|
| investment-team | `{公司名}/` 目录内含4个视角+最终报告 |
| investment-research | `{公司名}-research-{YYYYMMDD}.md` |
| investment-checklist | `{公司名}-checklist-{YYYYMMDD}.md` |
| industry-research | `{行业名}-industry-{YYYYMMDD}.md`（根目录） |
| industry-funnel | `{行业名}-funnel-{YYYYMMDD}.md`（根目录） |
| private-company-research | `{公司名}-private-{YYYYMMDD}.md` |
| earnings-review | `{公司名}-earnings-{期间}.md` |
| thesis-tracker | `{公司名}-thesis.md`（长期维护） |
| portfolio-review | `portfolio-latest.md`（根目录，持续更新） |
| management-deep-dive | `{公司名}-management-{YYYYMMDD}.md` |

## 数据校验

- 市值必须手算校验：股价 × 总股本，与报告市值对比
- 货币单位要明确（港币/人民币/美元），防止混淆
- PE/ROE等指标用 tools/financial_rigor.py 精确计算
- 报告写完后主动询问是否推送到GitHub
