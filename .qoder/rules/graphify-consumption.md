# Graphify 知识图谱消费规则（always-on）

本项目已用 Graphify 构建知识图谱（`graphify-out/graph.json`，454 节点 / 861 边 / 22 社区）。
本规则让 Qoder 在无 PreToolUse hook 的情况下实现与 Claude Code 等价的"查图优先"行为。

## 何时查图（Fast Path 触发条件）

用户提出**关于本项目结构与内容的自然语言问题**（架构 / 流程 / 依赖 / "X 在哪" / "Y 依赖 Z" /
"这个项目的报告审计流程是什么"），且 `graphify-out/graph.json` 存在时：

1. **跳过一切构建步骤**，直接执行 `graphify query "<问题>"`（BFS 遍历）。
2. 需要节点全貌时用 `graphify explain "节点名"`；需要两点关系链时用
   `graphify path "A" "B"`；需要影响面时用 `graphify affected "X"`。
3. 答案**必须引用节点 `source_file` / `source_location`** 作为来源标注。
4. 仅当问题不是关于代码/文档内容（如纯闲聊、通用知识），才走常规检索。

## 回源核查（回答前必做）

图谱定位到节点后，提取其 `source_file` 与 `source_location`，用 Read 工具读取真实源文件
对应行段做交叉验证，再回答。禁止只凭图谱边直接下结论——图谱是地图，不是领土。

## 复用人工审计结论

回答涉及推断关系（INFERRED / AMBIGUOUS 边）时，先读 Obsidian 审计台账：
`/Users/eleme/Documents/Obsidian Vault/MOC/Graphify审计台账.md`
- `#gf/audited` 的关系可直接引用（已回源确认）
- `#gf/rejected` 的关系必须跳过（已判定证据不足）
- `#gf/inferred` 的关系引用时须注明"未经人工核验"

MOC 导航（`/Users/eleme/Documents/Obsidian Vault/MOC/`）沉淀了人工策展的领域结构，
架构类问题可先读 L1 总览再下钻 L2 领域页，避免重复推导。

## 图谱维护

- `git commit` 后 post-commit hook 自动跑 `graphify update .`（AST 增量，无 LLM）刷新图谱；
  `git pull / merge` 后需手动 `graphify update .`。
- 语义缓存位于 `graphify-out/cache/`：skills/docs 文档未改动时，重跑不产生 LLM 消耗。
- 扫描范围由仓库根 `.graphifyignore` 白名单控制（tools/scripts/tests/skills/docs 顶层/根级 md）。
  图谱不含 reports/、qoder_report/ 等报告内容——问报告请直接检索目录。
- 完整技能文档：`.qoder/skills/graphify/SKILL.md`（构建 pipeline）与其 `references/query.md`（查询细节）。
