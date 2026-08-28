# AI 竞争力提升计划：从"使用AI"到"交付AI应用"

> 对应问题：[背景.md](./背景.md)——"每天都在学习和使用AI，时间算下来已经超过一年了，AI并没有提升个人的实际竞争力"
> 数据调研截止：2026-08-26（JD 调研 + 落地场景调研 + 面试真题复盘）

---

## 一、诊断：为什么学了一年 AI 没有竞争力

**根源：消费型使用 vs 生产型交付**

过去一年是"消费型 AI 使用"：问 AI 干活、读框架、考问打分。产出是"我会了"（★评分、阅读清单），而招聘市场要的是"我交付了"（可运行、可演示、可解释的 AI 应用）。

竞争力的公式：**竞争力 = 交付成果 × 可展示性 × 与目标的关联度**

三个断点：
1. 学习产出停留在"掌握度"，没有变成"交付物"
2. 成果物没有与职业目标挂钩
3. AI 使用是消费型（问问题），不是生产型（完整交付）

**独特资产（多数候选人没有）**：
- AI Berkshire 是真实的 AI Agent 开源项目，已通过 T1-T3 掌握其架构（T1 ★5）
- 一年 Qoder/Claude Code + Skill + MCP 平台实战沉淀
- 从"研究它"转向"建设它"是最短差异化路径

---

## 二、目标岗位画像：AI 应用开发工程师（首选研发效能方向）

- 岗位大类：AI 应用开发（占 AI 岗位约 35%，Python/Java + LangChain + API 调用，不需要懂算法）
- 首选方向：**研发效能方向**——字节有"AI研发效能工程师/架构师"岗（推动 AI 在需求分析/编码/测试/发布运维/知识沉淀落地），滴滴有"AI Agent工程师（研发效能方向）"岗
- 理由：移动端研发经验 + 一年平台 AI Coding 实践 = 该方向最直接的经验组合；80% 的 AI 岗位不需要懂算法

---

## 三、JD 调研结论（2026-08-26）

### 数据来源
- 300 条 JD 频率统计（2026 春招转 AI 复盘：Java 后端 3 年背景，47 投 19 面 3 offer）
- 腾讯/字节/灵犀互娱/复旦/智联真实岗位 + BOSS直聘/猎聘摘要

### 高频技能频率表（JD 要求 vs 现状）

| 技能 | JD 频率 | 现状 |
|------|--------|------|
| Python | ~78% | 需补齐（Dart/Java 可迁移） |
| 大模型 API（通义/文心/DeepSeek） | ~70% | 已有使用经验 |
| LangChain/LlamaIndex 框架 | ~62% | 需补齐 |
| RAG | ~55% | 概念已懂，缺实现 |
| Prompt Engineering | ~50% | 已有（T1 ★5，Skill=Prompt 工程） |
| 向量数据库（Chroma/Milvus/Pinecone） | ~45% | 需补齐 |
| Agent/Function Calling | ~40% | 架构已懂（T2），缺编码实现 |
| Docker/K8s | ~35% | 需补齐 |

### 2026 新增趋势
- 招聘技能需求 = **LangChain + RAG + MCP** 三件套
- **MCP 已写进大厂 JD**：腾讯"了解或使用过 MCP 等 AI 工具集成协议"为加分项；面试常问 Function Calling schema 设计、工具调用失败后的重试与降级机制
- 企业侧平台化（Dify/Coze/n8n）是选型主流，但招聘 JD 仍写 LangChain——**JD 是滞后于实践的过滤词**
- 300 条 JD 中超过 40% 出现"认证优先"（阿里云 ACP 大模型工程师认证，多个面试官主动问起）

---

## 四、能力差距矩阵

**背景基准**：移动端工程师（Dart/Flutter + Java 移动端），非 Java 后端；服务端经验需从零补

### 已有（迁移强化即可）
- Prompt Engineering：T1 ★5，Skill 体系就是 prompt 工程实践
- Agent 架构：T2 多 Agent 对抗（上下文隔离、工具调用、权限预检）
- 评估思维：report_audit 抽检 = LLM 输出质量门禁雏形；信息丰富度评级 = 反偏见
- 开源项目资产：AI Berkshire 本身（可展示、可讲深）
- 平台化交付能力：Qoder/Claude Code + Skill + MCP 生态一年实战沉淀
- 编程基础：Dart/Java，工程习惯可迁移，Python 语法学习成本低

### 需补齐（由 M1-M3 覆盖）
- Python 开发（78% JD 必会）
- 后端服务能力（跨度最大）：HTTP API（FastAPI）、数据库、鉴权——移动端→后端的知识跃迁
- LangChain/LlamaIndex 编码（JD 62% 高频词）
- RAG 全链路：chunking → embedding → 向量库 → 检索 → rerank → 引用溯源
- Docker/K8s 部署
- 评估体系：RAGAS / LLM as Judge
- 模型基础理论：Transformer、注意力、训练流程
- 认证：阿里云 ACP（可选，加分项）

---

## 五、技术路线决策：平台 Skill vs LangChain（双轨制）

**问题**：基于 Qoder/Claude Code/Codex 平台搭 Skill 做"AI 生产者"，是否比 LangChain 更契合招聘市场？

**结论：双轨制，不二选一**

| 轨道 | 内容 | 用途 |
|------|------|------|
| 交付线（已有优势） | Qoder/Claude Code + Skill + MCP 生产 AI 应用 | M1/M3 走这条线，产出快、能演示 |
| 匹配线（JD 语言） | LangChain + FastAPI + Chroma 实现 RAG 项目 | M2 用 LangChain 写——JD 写 LangChain，面试官认这个名字 |
| 桥梁（双向复用） | MCP 协议概念 | 平台原生支持 MCP，面试可讲 Function Calling schema、失败重试/降级——一年平台经验在此转化为面试分数 |

**面试考深度不考名词**：真实项目才能讲出 chunk size/rerank/降级机制的深度。

---

## 六、落地场景矩阵（2026 快速落地场景全景）

用户 BOSS 直聘发现的两个方向（AI Coding、智能客服）已验证为 2026 落地最深的场景，且分别对应 M1/M2：

| 场景 | 市场信号 | 核心能力 | 契合度 | 达成路径 |
|------|---------|---------|--------|---------|
| **AI Coding / 研发效能**（用户发现） | 字节"AI研发效能工程师/架构师"岗、滴滴"AI Agent工程师（研发效能方向）"岗、麦肯锡 2026 白皮书：人均代码吞吐 +35% | 软件工程基础、AI 编程工具链（Claude Code/Qoder/Copilot）、CI/CD、测试自动化、效能度量 | ★★★★★ 移动端工程师 + 一年平台 AI Coding 实践 = 直接经验 | M1 即证明；扩展为"企业内部 AI Coding 落地案例" |
| **智能客服 / 知识库问答**（用户发现） | 2026 大模型知识库市场 200 亿美元（+24.7%）、腾讯云酒店集团案例（知识库准确率提升） | RAG 全链路、知识库准确性、人机协同、持续运营 | ★★★★ M2 天然对应 | M2 RAG 项目 + 客服场景案例 |
| **企业办公助手**（会议纪要/合同审查） | 火山引擎 HiAgent"企业办公助手"、知乎企业智能体场景报告（合同审查为典型场景） | 文档解析（PDF/Word）、RAG、结构化输出 | ★★★★ 0826.md 记"会议" | M2 变体 或 M3 扩展 |
| **HR / 招聘提效** | 知乎场景报告（HR/行政咨询助手降低重复咨询压力） | 文档解析 + RAG + 结构化评分 | ★★★ 0826.md 记"招聘" | M2 领域选项（招聘知识库） |
| **数据问答 / Text-to-SQL** | 企业 BI 普遍需求 | NL2SQL、数据库、Schema 理解、评估 | ★★★ 需补数据库 | M3 扩展 |
| **流程自动化**（工单/审批） | 工行社招 JD：场景 Agent 落地（Agent 引擎、知识库对接、Prompt、Workflow、记忆模块） | Agent、Workflow、工具调用、记忆模块 | ★★★★ 平台 Skill 经验直接迁移 | M3 Agent 项目 |

**关键判断**：研发效能方向有专门岗位（字节/滴滴），用户背景（移动端研发经验 + 一年平台 AI Coding 实践）在该方向契合度最高——**主攻"AI 应用开发（研发效能方向）"，智能客服/RAG 作为第二证明**。

---

## 七、三个里程碑项目（14 周）

### M1（4周）AI Berkshire 生产化 —— AI Coding 落地案例

- **对应 JD**：Python + Docker + 工程质量 + 平台交付线 + 研发效能场景
- **交付物**（全部为完成标准）：
  - pytest 测试套件（tools/ 下核心工具：financial_rigor.py、report_audit.py）
  - GitHub Actions CI（push 自动跑测试）
  - Dockerfile（可容器化运行）
  - README 部署章节（他人可复现）
- **价值**：把已有开源项目升级为"可展示的生产级项目"，简历第一行；同时完成 Python 入门与部署初体验
- **验收**：`python3 -m pytest` 全绿；CI badge 可用；`docker build` 成功

### M2（6周）RAG 知识库问答系统 —— 智能客服/知识库场景

- **对应 JD**：RAG + LangChain + 向量库 + Prompt + API（JD 最高频技能组）
- **技术栈**：FastAPI + LangChain + Chroma + 阿里云 text-embedding + bge-reranker + Streamlit 前端
- **领域绑定**：招聘知识库 / 客服知识库 / AI Berkshire 投资知识库，按数据可得性三选一（启动时定）
- **必做踩坑记录**（面试必问点，全部实战并记录）：
  - chunk size 选择：1000 效果差 → 500 + overlap 100（有理有据）
  - embedding 选型：bge-large-zh 部署麻烦 → 阿里云 text-embedding-v2 API（能说出理由）
  - Rerank：bge-reranker-v2-m3，量化准确率提升约 20%
  - 引用溯源（面试加分项，被问 3 次）：回答末尾附来源、页码、相关度
  - RAGAS 评估：Faithfulness / Answer Relevancy / Context Precision / Context Recall
- **后端职责**：FastAPI 同时承担"移动端→后端"知识跃迁载体（HTTP API、数据库、鉴权）
- **价值**：市场验证过的 offer 路径（复盘作者 15/19 场面试被问该项目）
- **验收**：可问答、有引用溯源、有 RAGAS 评估报告、有踩坑记录文档

### M3（4周）Agent 应用 + 工程化深度 —— 流程自动化场景

- **对应 JD**：Agent + 评估 + 监控 + 成本
- **交付物**：
  - Function Calling 多工具 Agent（复刻 AI Berkshire 工具调用模式，如"财报问答 Agent"）
  - LLM as Judge 评估 + 成本/延迟日志
  - 技术博客 2 篇（工程实践深度证明）
- **价值**：面试官区分"抄教程"与"真做过"的题全在 M2/M3 覆盖
- **验收**：Agent 可自主调用多工具完成任务；有评估与成本数据；博客发布

---

## 八、每周节奏与市场校准

每周固定"**交付-复盘-校准**"循环：

1. **交付**：本周完成一个可运行的小增量（不是阅读笔记）
2. **复盘**：对照项目验收清单自检（可运行/可演示/可解释）
3. **校准**：用面试题库自测（见下节），标记薄弱点

**市场反馈机制**：第 6 周起投递简历 + 面试，用真实反馈更新差距矩阵，避免闭门造车。

---

## 九、面试高频题库（19 场真题分类，每周自测材料）

> ⭐ = 被问 5 次以上。自测方式：闭卷口答，答不出即列入薄弱清单，下周回补。

### RAG 相关（最高频）
- ⭐ RAG 的完整流程是什么？每个环节可能遇到什么问题？
- ⭐ Chunk Size 怎么选？Overlap 的作用是什么？
- ⭐ 向量检索和关键词检索有什么区别？什么时候用哪个？
- ⭐ 如何评估 RAG 系统的效果？用什么指标？
- RAG 和 Fine-tuning 分别适用于什么场景？
- 如果检索到的上下文和问题无关，怎么处理？
- 项目中用的什么 Embedding 模型？为什么选它？

### Prompt Engineering
- ⭐ Few-shot Prompting 和 Zero-shot 有什么区别？
- ⭐ Chain-of-Thought 是什么？什么时候用？
- Prompt 太长导致回答质量下降怎么办？
- 如何设计 System Prompt 让 LLM 扮演特定角色？
- 项目中用过哪些 Prompt 技巧？效果如何？

### Agent 相关
- ⭐ Function Calling 和传统 API 调用有什么区别？（本质：LLM 根据用户意图自主决定调用哪个函数、传什么参数，是 Agent 自主决策能力的核心）
- Agent 的 ReAct 框架是什么？
- 多 Agent 协作怎么设计？有什么挑战？
- Agent 的幻觉问题怎么处理？

### 大模型基础
- ⭐ Transformer 的核心机制是什么？为什么比 RNN 好？
- 什么是注意力机制？Self-Attention 怎么计算？
- 大模型的训练流程（预训练→SFT→RLHF）分别做什么？
- 什么是 Temperature？Top-p？怎么调参？
- 通义千问和 GPT-4 有什么区别？各有什么优势？

### 工程实践
- ⭐ 模型部署用什么方案？怎么优化推理速度？（正确答案：KV Cache、量化 INT8/INT4、vLLM 框架、Continuous Batching、Speculative Decoding）
- LLM 的 Token 限制怎么处理？长文本怎么办？
- 如何监控 LLM 的输出质量？
- 多轮对话怎么管理上下文？
- 项目 QPS 能到多少？怎么做的压测？

### 曾答错的高频题（重点补）
1. **RAG 评估指标**：Faithfulness（忠实度）、Answer Relevancy（回答相关性）、Context Precision（上下文精确度）、Context Recall（上下文召回率）——RAGAS 框架
2. **Function Calling 本质**：LLM 自主决策调用哪个函数、传什么参数，不是简单 API 转发
3. **推理速度优化**：KV Cache、量化（INT8/INT4）、vLLM、批处理（Continuous Batching）、Speculative Decoding

---

## 十、现有学习系统的角色调整

- `docs/AI-Berkshire-学习计划.md`（8 阶段阅读计划）与 `docs/学习系统-主题导师版.md`：**降级为辅助手段**，不再作为主考核
- 主考核切换为：M1-M3 项目验收 + 面试题库自测 + 市场反馈
- 主题导师版中未完成的 T4/T5 可继续，但优先级低于里程碑项目
- 错题本机制保留：面试题库自测的薄弱点按同样格式记录

---

## 附：执行顺序总览

| 周次 | 内容 | 完成标准 |
|------|------|---------|
| 第 1-2 周 | Python 快速补齐（基于 M1 任务边做边学）| 能独立写 pytest 测试 |
| 第 1-4 周 | M1：AI Berkshire 生产化 | 测试全绿 + CI + Dockerfile + 部署文档 |
| 第 3 周起 | 面试题库每周自测 1 类 | 薄弱点入错题本 |
| 第 5-10 周 | M2：RAG 知识库问答系统 | 可问答 + 引用溯源 + RAGAS 报告 + 踩坑记录 |
| 第 6 周起 | 投递简历 + 面试校准 | 每 2 周一次反馈复盘 |
| 第 11-14 周 | M3：Agent + 工程化深度 | Agent 可用 + 评估成本数据 + 博客 2 篇 |

**数据与假设**：以上 JD 频率与市场数据来自 2026 春招复盘（300 条 JD 统计）与公开招聘信息；本项目是学习与研究用途，不是求职建议。
