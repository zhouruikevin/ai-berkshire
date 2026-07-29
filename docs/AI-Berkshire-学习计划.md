# AI Berkshire 项目详细学习计划

> 面向 IT 工程师的系统化学习路径，共 8 个阶段约 16-18 小时。
> 核心策略：架构先行 → 报告倒推 → 源码精读 → 动手实践 → 工程理解 → 横向铺开 → 实战调用 → 贡献闭环

---

## 阶段一：建立全局认知（约 2 小时）

### 目标
理解项目"是什么、为什么这样设计、怎么组织的"，建立三层架构（Skill层 → Agent层 → 工具层）的全局心智模型。

### 步骤

**1.1 精读项目门面与设计哲学**
- 完整阅读 `README.md`（787行），重点章节：
  - Real Track Record（L21-L49）：实盘业绩，理解这不是纸上谈兵
  - 为什么不能直接问AI（L61-L167）：6 大核心差异——强制给结论、四大师对抗、反偏见机制、数据精确性、可复现流程、多Agent并行
  - 整体架构（L170-L182）：三层设计哲学
  - Skills 一览（L185-L230）：20 个 Skill 按五大场景分类
  - 设计理念（L711-L749）：四大师方法论融合 + 金融严谨性工具

**1.2 理解三层规则体系与项目约束**
- 阅读 `CLAUDE.md`（115行）：项目结构、报告命名规范、投研核心原则、GitHub操作
- 阅读 `AGENTS.md`（84行）：三平台兼容规则、研究质量规则、编辑规则
- 阅读 `.qoder/rules/research-principles.md`：投研核心原则精简版
- 阅读 `ai_CLAUDE.md`（65行）：用户画像、项目演进历史、已知教训（V1→V2 Skill 体系演化）

**1.3 利用 repowiki 快速建立知识图谱**
- 阅读 `.qoder/repowiki/zh/content/项目概述.md`：含 Mermaid 架构图
- 浏览 `.qoder/repowiki/zh/content/` 下子目录：技能系统详解、工具系统详解、投资研究方法论、报告生成与输出、实战案例分析、数据管理与存储
- 注意：repowiki 是 Qoder 自动生成的辅助材料，**不是 canonical 源**——权威信息以 `skills/*.md`、`AGENTS.md`、`CLAUDE.md` 为准

### 关键理解点
- 四大师是"对抗"不是"分工"：段永平说"好生意"，芒格问"怎么会死"；巴菲特说"够便宜"，李录问"10年后还在吗"
- `skills/*.md` 是**唯一 canonical 源**，`.qoder/skills` 和 `codex-skills` 是生成物，严禁手改
- 报告双轨制：新报告 → `qoder_report/`；历史归档 → `reports/`（只读）；三类活文件（thesis/portfolio-latest/bottleneck-map）仍在 `reports/` 维护

### 自测检查点

> **不看资料能回答以下问题 = 掌握，可以进入下一阶段**

**概念自测：**
1. 项目的三层架构是什么？每层分别负责什么？
2. 四大师各自代表什么视角？他们之间是"分工"还是"对抗"？举例说明。
3. `skills/*.md` 和 `.qoder/skills/` 是什么关系？哪个能直接改？为什么？
4. 新报告应该输出到哪个目录？哪三类文件是例外？
5. 项目支持哪三个 AI 客户端？哪个是主环境？

**动手验证：**
- 不看任何资料，用 5 句话向同事介绍这个项目（如果说不完整，回去重读 README）

---

## 阶段二：从真实报告倒推工作流（约 2 小时）

### 目标
通过阅读真实产出的报告，理解系统"长什么样"，建立对 Skill 输出形态的感性认知，为后续阅读源码提供锚点。

### 步骤

**2.1 精读 investment-team 最终报告（多Agent并行产出）**
- 阅读 `reports/拼多多/最终报告.md`：四维评分表 + Bull/Bear + Checklist + 分层建议
- 关注：信息丰富度评级（A/B/C）、四大师评分格式、`financial_rigor.py` 输出如何嵌入报告、最终投资建议的结构

**2.2 精读 investment-research 报告（七模块串行产出）**
- 阅读 `qoder_report/中天科技/中天科技-research-20260721.md`
- 关注：对比 investment-team（4 Agent并行）和 investment-research（7模块顺序执行）的差异；`valuation_percentile.py` 的使用记录

**2.3 精读行业漏斗和质量筛选报告**
- 阅读 `qoder_report/保险-funnel-20260720.md`：四层漏斗完整记录，关注"淘汰记录"设计
- 阅读 `qoder_report/8股去劣筛选-quality-screen-20260709.md`：7条硬指标 + 豁免规则

**2.4 阅读投资论文追踪文件（活文件机制）**
- 阅读 `reports/腾讯/腾讯-thesis.md` 或 `reports/拼多多/拼多多-thesis.md`
- 理解：thesis 是长期维护型文件，记录买入逻辑+估值锚点+证伪信号，理解它为什么留在 `reports/` 而不迁移

### 关键理解点
- 每类 Skill 有固定的报告命名规范（见 `CLAUDE.md` L42-L57）
- 报告中强制嵌入工具验证记录，不是"AI 自由发挥"
- 漏斗筛选的每层都留下淘汰理由，不是黑箱

### 自测检查点

> **不看资料能回答以下问题 = 掌握，可以进入下一阶段**

**概念自测：**
1. investment-team 和 investment-research 的报告结构有什么区别？
2. 报告中的"信息丰富度评级"是什么意思？有哪几级？
3. 漏斗筛选报告的"淘汰记录"为什么重要？
4. thesis 文件为什么留在 `reports/` 而不迁移到 `qoder_report/`？

**动手验证：**
- 打开一篇你没读过的报告（如 `qoder_report/创新药-funnel-20260715.md`），不看答案预测它的结构应该包含哪些部分，然后读一遍验证你的预测

---

## 阶段三：精读核心 Skill 源码（约 3 小时）

### 目标
深入理解 3-4 个核心 Skill 的源码结构，建立"母版"认知，后续其他 Skill 都是变体。

### 步骤

**3.1 精读"单公司研究"母版：investment-research.md（276行）**
- 完整阅读 `skills/investment-research.md`
- 提取写作模式：
  - YAML frontmatter 必须有 `name` 和 `description`
  - 使用 `$ARGUMENTS` 占位符接收用户输入，`$CURRENT_DATE` 锚定日期
  - 七模块研究框架：数据收集 → 生意本质(段永平) → 护城河(巴菲特) → 逆向思考(芒格) → 管理层评估 → 文明趋势(李录) → 估值与安全边际
  - 强制调用 `tools/financial_rigor.py` 的 bash 代码块
  - AI 偏见自觉机制（A/B/C级信息丰富度评级）
  - `report_audit.py` 抽检准出流程

**3.2 精读"多Agent并行"范式：investment-team.md（235行）**
- 完整阅读 `skills/investment-team.md`
- 重点理解：
  - Team/Task 工具调度 4 个后台 Agent
  - 4 Agent 角色分工（段永平/巴菲特/芒格/李录）
  - **WebSearch 权限预检**（issue #58 教训：后台 Agent 若 WebSearch 未放行会静默退化为"未联网的伪研究"——这是项目最重要的工程教训之一）
  - Team Lead 综合研判流程
- 对比 3.1：`investment-research` 是单 Agent 串行，`investment-team` 是 4 Agent 并行，理解何时选哪个

**3.3 精读"数据规范"：financial-data.md（212行）**
- 完整阅读 `skills/financial-data.md`
- 理解四市场数据源优先级与双源交叉验证规范：
  - 美股：macrotrends + stockanalysis
  - 港股：aastocks + macrotrends ADR
  - A股：TuShare + 东方财富
  - 台股：FinMind + Goodinfo
- 交叉验证规则：误差 >1% 须标记

**3.4 快速浏览 quality-screen.md（178行）**
- 阅读 `skills/quality-screen.md`
- 理解7条硬指标 + 3条豁免规则（作为后续实战调用的入门 Skill）

### 关键理解点
- `investment-research.md` 是所有 Skill 的"母版"——掌握它的结构后，其他 Skill 都是变体
- 每个 Skill 都内置了工具强制调用步骤和报告抽检准出流程
- `$ARGUMENTS` 和 `$CURRENT_DATE` 是 Skill 的标准占位符

### 自测检查点

> **不看资料能回答以下问题 = 掌握，可以进入下一阶段**

**概念自测：**
1. Skill 文件的 frontmatter 必须包含哪两个字段？
2. `$ARGUMENTS` 和 `$CURRENT_DATE` 分别是什么作用？
3. investment-research 的七模块框架是什么？按顺序说出。
4. investment-team 为什么需要 WebSearch 权限预检？不做会怎样（issue #58）？
5. investment-research 和 investment-team 什么时候选哪个？

**动手验证：**
- 不看源码，在白纸上画出 investment-research 的执行流程图（数据收集 → 七模块 → 工具验证 → 报告准出）

---

## 阶段四：动手运行工具链（约 2 小时）

### 目标
通过实际运行工具命令，理解工具层如何保证数据严谨性，建立"为什么不能直接问AI"的肌肉记忆。

### 步骤

**4.1 运行 financial_rigor.py 的 6 个子命令**
- 在仓库根目录执行（使用报告中的真实数据）：

```bash
# 市值验算（腾讯示例）
python3 tools/financial_rigor.py verify-market-cap \
  --price 510 --shares 9.11e9 --reported 4.65e12 --currency HKD

# 估值指标验算
python3 tools/financial_rigor.py verify-valuation \
  --price 510 --eps 23.5 --bvps 120 --fcf-per-share 18 --dividend 2.4

# 多源交叉验证
python3 tools/financial_rigor.py cross-validate \
  --field revenue --values '{"年报": 7518, "Yahoo": 7500, "StockAnalysis": 7520}' --unit 亿

# 精确计算器
python3 tools/financial_rigor.py calc --expr '510 * 9.11e9'

# 三情景估值
python3 tools/financial_rigor.py three-scenario \
  --price 510 --eps 23.5 --shares 9.11 \
  --growth 0.15 0.08 0.0 --pe 25 20 15 --years 3 --currency HKD

# Benford定律检测
python3 tools/financial_rigor.py benford --values '[1234,2345,3456,4567,5678,6789,7890,8901,9012]'
```

- 理解：所有计算用 `decimal.Decimal`（精确十进制），偏差 >5% 报 ❌，>1% 报 ⚠️

**4.2 运行 report_audit.py 的三步抽检流程**

```bash
# 提取数据点并预览（dry-run，不输出JSON）
python3 tools/report_audit.py extract \
  --report reports/拼多多/最终报告.md --dry-run

# 提取并输出JSON模板
python3 tools/report_audit.py extract \
  --report reports/拼多多/最终报告.md --seed 42

# 模拟准出判决
python3 tools/report_audit.py verdict \
  --results '[{"id":1,"label":"总营收","reported_value":4318,"unit":"亿","fetched_value":4318,"fetched_source":"年报","fetched_value2":4320,"fetched_source2":"Yahoo"}]' \
  --report "拼多多-最终报告"
```

- 理解：15% 随机抽样 + 1% 容差 + FAIL 退出码为1（可接CI）

**4.3 运行 A 股数据工具（免 token 优先）**

```bash
# 免 token 的 A 股行情（腾讯 API，推荐优先使用）
python3 tools/ashare_data.py quote 600519
python3 tools/ashare_data.py financials 600519

# 南向资金追踪（东财公开数据，免 token）
python3 tools/southbound_flow.py flow --days 30

# TuShare（需要 .env 中的 TUSHARE_TOKEN，可能过期）
# python3 tools/tushare_fetcher.py quote 601872.SH
```

**4.4 运行估值分位工具**

```bash
# A 股端到端
python3 tools/valuation_percentile.py ashare 600519 --growth 12

# 通用分位积木
python3 tools/valuation_percentile.py percentile \
  --series '[10,20,30,40,50,60,70,80]' --current 45 --forward 38
```

### 关键理解点
- `financial_rigor.py` 的 `exact()` 函数用 `Decimal(str(value))` 而非 `Decimal(value)` 避免浮点陷阱
- `report_audit.py` 三步流程：extract（抽15%）→ 人工填数 → verdict（准出/打回）
- 所有工具零外部依赖（仅 Python stdlib），用 `urllib.request` 做 HTTP 请求
- TuShare Token 可能过期，`ashare_data.py` 是免 token 的替代方案

### 自测检查点

> **不看资料能回答以下问题 = 掌握，可以进入下一阶段**

**概念自测：**
1. financial_rigor.py 有哪 6 个子命令？各自解决什么问题？
2. 为什么用 `decimal.Decimal` 而不用 `float`？
3. report_audit.py 的三步流程是什么？抽样比例和容差各是多少？
4. 偏差大于多少报 ❌？大于多少报 ⚠️？

**动手验证：**
- 独立运行 `verify-market-cap` 和 `calc` 命令，向自己解释输出的每一行含义
- 运行 `report_audit.py extract --dry-run`，确认你能理解输出的抽检清单

---

## 阶段五：理解工程架构与三平台同步（约 2 小时）

### 目标
理解项目的工程纪律：单一 canonical 源 → 三平台代码生成 → 安装部署的完整链路。

### 步骤

**5.1 对比阅读三个 sync 脚本**

| 脚本 | 行数 | 生成位置 | 关键差异 |
|------|------|---------|---------|
| `scripts/sync-qoder-skills.py` | 93行 | `.qoder/skills/<name>/SKILL.md` | 最简单：重写 frontmatter，正文原样保留 |
| `scripts/sync-codex-skills.py` | 128行 | `codex-skills/<name>/SKILL.md` | 最复杂：保留+补全 frontmatter，注入 Codex adapter note |
| `scripts/sync-codex-prompts.py` | 95行 | `codex-prompts/<name>.md` | 薄包装层，引用已安装的 skill |

- 三个脚本共享 `split_frontmatter()` 和 `first_heading()` 函数（代码重复，非共享模块——已知技术债）
- 均支持 `--check` 模式（只校验不写文件，退出码非0表示脱节）

**5.2 运行同步校验（只读验证）**

```bash
python3 scripts/sync-qoder-skills.py --check
python3 scripts/sync-codex-skills.py --check
python3 scripts/sync-codex-prompts.py --check
```

**5.3 对比阅读安装脚本**
- `scripts/install-qoder-skills.sh`（25行）：装到 `~/.qoder/skills`，支持 `QODER_HOME` 环境变量覆盖
- `scripts/install-codex-skills.sh`（22行）+ `.bat`（35行）：装到 `~/.codex/skills`，`.bat` 有 `py -3` vs `python` 探测逻辑
- `scripts/install-claude-commands.sh`（12行）：直接复制 `skills/*.md` 到 `~/.claude/commands`（无需 sync，canonical 源本身就是 Claude 格式）
- 理解：Qoder 打开仓库即自动加载项目级 skill，Claude Code/Codex 需手动安装

**5.4 理解 .qoder 目录完整结构**
- `.qoder/rules/`：常驻规则（2个文件，每次对话自动注入）
- `.qoder/skills/`：项目级技能（由 sync 生成，开箱即用）
- `.qoder/repowiki/`：Qoder 自动生成的项目知识库（辅助学习材料，非权威源）

**5.5 阅读开发规范**
- `CONTRIBUTING.md`（95行）：双语贡献指南，明确划分欢迎/不接受的贡献类型
- `.editorconfig`：2空格缩进（md/sh）、4空格缩进（py）、LF换行、UTF-8

### 关键理解点
- **铁律**：只改 `skills/*.md`，改完跑 sync 脚本。`.qoder/skills/` 和 `codex-skills/` 是生成物，会被覆盖
- `CLAUDE.md` 与 `.qoder/rules/project-rules.md` 内容高度重叠但有细微差异（前者 Claude Code 专用，后者 Qoder 专用）
- 安装脚本用 `rm -rf` + `cp -R` 全量替换策略，有 `set -euo pipefail` 错误处理

### 自测检查点

> **不看资料能回答以下问题 = 掌握，可以进入下一阶段**

**概念自测：**
1. 三个 sync 脚本各自生成什么？哪个最复杂？为什么？
2. `--check` 模式的作用是什么？退出码 0 和非 0 分别表示什么？
3. 为什么 Claude Code 的安装脚本不需要 sync？
4. Qoder 项目级 skill 需要手动安装吗？为什么？

**动手验证：**
- 运行三个 `--check` 命令，解释输出含义
- 对比 `skills/investment-research.md` 和 `.qoder/skills/investment-research/SKILL.md`，说出两者的差异

---

## 阶段六：横向铺开其余 Skill（约 1.5 小时）

### 目标
在已精读 3-4 个核心 Skill 的基础上，快速浏览其余 Skill，理解全貌和协作关系。

### 步骤

**6.1 按五大场景分类速览（每个只读前 30-50 行）**

| 场景 | Skill | 核心定位 |
|------|-------|---------|
| **深度研究** | `management-deep-dive` | 管理层纵深：CEO履历、决策记录、资本配置 |
| | `private-company-research` | 未上市公司：侦探式研究，置信度标注 |
| | `deep-company-series` | 8篇长文系列：公众号级深度内容 |
| **财报分析** | `earnings-review` | 财报精读：只读原始财报，不依赖二手研报 |
| | `earnings-team` | 财报团队：四大师并行+公众号发布 |
| **行业筛选** | `industry-research` | 产业链全景：按环节切片 |
| | `industry-funnel` | 漏斗精选：全市场→≤10家→3家 |
| | `bottleneck-hunter` | 供应链瓶颈：从超级趋势找物理瓶颈 |
| | `investment-checklist` | 6关快速筛选：10分钟决定是否深入 |
| **持仓管理** | `income-investment` | 收益型股票：区分可持续收益与陷阱 |
| | `portfolio-review` | 组合管理：仓位、集中度、再平衡 |
| | `thesis-tracker` | 论文追踪：买入后纪律系统 |
| | `news-pulse` | 股价异动归因：10分钟快速归因 |
| **思维工具** | `dyp-ask` | 段永平问答：以段永平方式思考 |
| | `wechat-article` | 公众号文章：三Agent协作产出 |
| | `thesis-drift` | 论文漂移检测 |

**6.2 理解 Skill 间的协作关系**
- 买入前链路：`quality-screen` → `investment-checklist` → `investment-research`/`investment-team` → `industry-funnel`
- 买入后链路：`thesis-tracker`（长期跟踪）+ `earnings-review`/`earnings-team`（财报季）+ `news-pulse`（异动归因）+ `portfolio-review`（组合管理）
- 内容产出链路：`deep-company-series` + `wechat-article`

### 自测检查点

> **不看资料能回答以下问题 = 掌握，可以进入下一阶段**

**概念自测：**
1. 买入前和买入后分别用哪些 Skill？画出完整链路。
2. earnings-review 和 earnings-team 的区别？什么场景用哪个？
3. news-pulse 和 investment-team 的区别？什么场景用哪个？
4. industry-research 和 industry-funnel 的区别？

**动手验证：**
- 给定场景："我刚买入腾讯，下周要发财报，同时股价突然跌了 8%"——说出应该依次用哪些 Skill，为什么

---

## 阶段七：实战调用 Skill（约 2 小时）

### 目标
在 Qoder 或 Claude Code 中实际调用 Skill，完成从"读代码"到"用工具"的闭环。

### 步骤

**7.1 调用轻量级 Skill：/quality-screen**

```
/quality-screen 腾讯, 美团, 拼多多
```

- 观察：AI 如何调用 WebSearch 收集 7 条指标数据、如何应用豁免规则、输出汇总表格式
- 对比：将产出报告与 `qoder_report/8股去劣筛选-quality-screen-20260709.md` 对比

**7.2 调用中等复杂度 Skill：/investment-research**

```
/investment-research 中天科技
```

- 观察：AI 如何执行七模块流程、在哪些节点调用 `financial_rigor.py`、如何执行 `report_audit.py` 抽检
- 对比：将产出报告与 `qoder_report/中天科技/中天科技-research-20260721.md` 对比

**7.3（进阶）调用多 Agent Skill：/investment-team**

```
/investment-team 工业富联
```

- 观察：Team Lead 如何创建 4 个后台 Agent、每个 Agent 独立搜索和验证数据、如何综合为一份报告
- **前置条件**：确认 WebSearch 权限白名单（见 `skills/investment-team.md` 中的预检步骤），避免 issue #58 的静默退化
- 对比：`qoder_report/工业富联/` 目录下的 01-04 四个分册和最终报告

### 关键理解点
- 先跑轻量 Skill（quality-screen）建立信心，再跑完整流程
- investment-team 的 WebSearch 权限预检是**必须执行的前置步骤**，否则 4 个后台 Agent 会静默退化为"未联网的伪研究"
- CLI 模式注意：非交互 `-p` 必须加 `--output-format text`，不要传 `--tools ""`

### 自测检查点

> **不看资料能回答以下问题 = 掌握，可以进入下一阶段**

**概念自测：**
1. 调用 /quality-screen 后，AI 大致执行了哪些步骤？
2. 调用 /investment-research 时，AI 在哪些节点调用了工具？
3. 如果 /investment-team 的输出质量明显低于已有报告，最可能的原因是什么？

**动手验证：**
- 将你用 /quality-screen 产出的报告与 `qoder_report/8股去劣筛选-quality-screen-20260709.md` 对比，找出 3 个差异并解释原因

---

## 阶段八：贡献闭环（约 1.5 小时）

### 目标
通过模拟"修改 Skill → 同步 → 验证"和"新增工具"两个完整流程，掌握项目的贡献方式。

### 步骤

**8.1 模拟"修改 Skill → 同步 → 验证"闭环**
- 选一个较小的 Skill（如 `skills/quality-screen.md`，7.3KB）
- 模拟修改：在 frontmatter 中调整 `description`，或在正文中增加一个步骤
- 运行三个同步脚本：

```bash
python3 scripts/sync-qoder-skills.py
python3 scripts/sync-codex-skills.py
python3 scripts/sync-codex-prompts.py
```

- 运行校验：`python3 scripts/sync-qoder-skills.py --check`
- 用 `git diff` 查看所有变动文件，确认只有预期改动

**8.2 模拟"新增工具"流程**
- 参照 `financial_rigor.py` 的模式（零依赖、argparse 子命令、Decimal 精确运算）
- 设计一个新工具，确保：
  - 仅用 Python stdlib（不用 requests/pandas）
  - 工作区相对路径调用（`python3 tools/xxx.py`）
  - 有 `--help` 文档
- 在相关 Skill 中增加调用该工具的 bash 代码块
- 运行同步脚本更新三平台

### 关键理解点
- 工具层铁律：零外部依赖（仅 stdlib），用 `urllib.request` 做 HTTP，用 `json` 模块处理 JSON
- `financial_rigor.py` 的 `exact_calc` 使用 `eval()` 但有字符集白名单防护（仅允许 `0123456789.+-*/() eE`）——新增类似功能时不应效仿
- 修改后必须跑 sync 脚本保持三平台一致

### 自测检查点

> **不看资料能回答以下问题 = 掌握，可以进入下一阶段**

**概念自测：**
1. 修改 Skill 后必须做什么？不做会怎样？
2. 新增工具必须遵守哪些约束？（至少说出 3 条）
3. `skills/*.md` 改完后，哪些文件会自动变化？

**动手验证：**
- 完成一次"修改 Skill description → 运行 sync → `--check` 验证 → `git diff` 确认"的完整闭环
- 确认 `git diff` 中只有预期改动，没有多余文件被修改

---

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 22 个 Skill 信息过载 | 陷入浏览式阅读，无法建立深度理解 | 严格遵循"先深后广"：只精读阶段三的 3-4 个核心 Skill，其余在阶段六只读前 30 行 |
| 混淆 generated 产物与 canonical 源 | 直接改 `.qoder/skills/` 或 `codex-skills/` 导致下次 sync 被覆盖 | 铁律：只改 `skills/*.md`，改完跑 sync |
| TuShare Token 过期 | `tushare_fetcher.py` 调用失败 | 改用 `tools/ashare_data.py`（腾讯 API，免 token） |
| WebSearch 未放行（issue #58） | investment-team 的后台 Agent 静默退化为训练知识作答 | 先执行 Skill 中的 WebSearch 权限预检步骤 |
| LLM 心算误差 | 直接问 AI 计算 PE/市值出现小数点错误 | 严格使用 `financial_rigor.py`，Skill 已内置强制调用 |
| 报告目录混淆 | 新报告错误输出到 `reports/` | 新报告 → `qoder_report/`；活文件（thesis/portfolio/bottleneck-map）→ `reports/` |
| `.env` 含真实 Token | 安全风险（虽被 .gitignore 排除） | 不在报告/commit/截图中暴露 token |
| Skill 改动后未同步 | 三平台不一致 | 改完 skill 后立即运行三个 sync 脚本 |
| CLAUDE.md 与 project-rules.md 差异 | 困惑哪个是权威 | 两份都读，核心原则一致，差异在细节；CLAUDE.md 是 Claude Code 专用，project-rules.md 是 Qoder 专用 |
| 安装脚本覆盖用户级配置 | 影响其他项目配置 | 学习阶段只运行 `--check` 模式，不运行 install 脚本 |

---

## 关键文件清单（Top 7）

| 排名 | 文件 | 为什么关键 |
|------|------|-----------|
| 1 | `skills/investment-research.md`（276行） | **母版 Skill**。浓缩了整个框架的方法论：AI偏见自觉、日期锚定、数据交叉验证、七模块框架、四大师追问。理解它就理解了 80% 的设计哲学 |
| 2 | `tools/financial_rigor.py`（452行） | **工具层核心**。展示"精确十进制计算"如何落地：Decimal引擎、6个子命令。是所有 Skill 数据严谨性的执行者 |
| 3 | `README.md`（787行） | **项目全景**。覆盖实盘业绩、设计哲学、架构图、20 Skill一览、快速开始。是最高效的"30分钟建立全局认知"入口 |
| 4 | `skills/investment-team.md`（235行） | **多Agent范式**。展示 Agent 层如何工作：Team/Task调度、4角色并行、WebSearch权限预检（issue #58教训） |
| 5 | `reports/拼多多/最终报告.md` | **最完整真实报告样本**。展示 investment-team 的最终产出形态，是倒推完整研究工作流的最佳案例 |
| 6 | `scripts/sync-codex-skills.py`（128行） | **最复杂的同步脚本**。展示 frontmatter 补全、Codex adapter note 注入、`--check` 模式实现 |
| 7 | `AGENTS.md`（84行） | **工程规范总纲**。定义单一数据源规则、兼容性规则、编辑规则。是贡献代码前必读的"交通规则" |

---

## 学习进度追踪

完成一个阶段后，在对应方框中打勾：

- [ ] 阶段一：建立全局认知（约 2 小时）
- [ ] 阶段二：从真实报告倒推工作流（约 2 小时）
- [ ] 阶段三：精读核心 Skill 源码（约 3 小时）
- [ ] 阶段四：动手运行工具链（约 2 小时）
- [ ] 阶段五：理解工程架构与三平台同步（约 2 小时）
- [ ] 阶段六：横向铺开其余 Skill（约 1.5 小时）
- [ ] 阶段七：实战调用 Skill（约 2 小时）
- [ ] 阶段八：贡献闭环（约 1.5 小时）

---

## 被拒绝的替代方案

| 替代方案 | 拒绝原因 |
|---------|---------|
| 按文件目录顺序逐个学习 | 缺乏上下文，读到 `tools/` 时不知道为什么要用 Decimal；读到 `codex-skills/` 时不知道它是生成物。改为"架构先行→报告倒推→源码精读"的递进路径 |
| 上来就调用完整 Skill（如 `/investment-team 腾讯`） | 信息过载+API额度浪费。不理解 Skill 结构就跑完整流程，无法判断输出质量。改为先读真实报告理解产出形态，再读源码理解流程，最后才实战调用 |
| 逐行阅读所有 22 个 Skill | 时间成本高且收益递减。改为精读 3-4 个核心 Skill 建立"母版"认知，其余只读 frontmatter + 前 30 行理解定位 |
| 只读代码不运行工具 | 无法建立"为什么不能直接问AI"的肌肉记忆。阶段四的动手实践是理解工具层价值的关键 |
| 从 Codex 视角切入学习 | Qoder 是主环境且开箱即用（`.qoder/` 随仓库入库），Codex 需要额外安装。学习阶段以 Qoder 为主，兼容性理解放在阶段五 |
