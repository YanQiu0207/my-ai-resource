# 如何评测一个 AI Agent —— 本地资料库研究报告

## 结论

资料库中确有一批高质量、可直接落地的「AI Agent 评测」资料，且彼此能拼出一张较完整的方法论地图。综合 8 篇相关 / 部分相关文章，可以归纳出当前业界（阿里、淘天、腾讯）对「如何评测一个 AI Agent」的主流共识：

1. **核心公式**：`Eval = Agent 输入 → 执行 → 捕获执行过程（Trace + 产物）→ 一组检查规则 → 可对比的分数`。评测目标不是「跑通一次」，而是建立**可重复、可量化、可归因、可持续回归**的闭环，用数据代替「感觉变好了」的主观 vibes。
2. **不能只看最终答案，必须看轨迹（Trajectory）**：Agent 的非确定性、黑盒化、错误级联放大三大特性，决定了「答案对」可能掩盖「过程错」（用了未授权数据源、十几次无意义工具调用、靠重试撞对、关键事实来自错误检索）。多篇资料一致强调**过程评估 / 轨迹评估**是 Agent 评测区别于传统软件测试、也是区别于单轮模型评测的最大创新点。
3. **三类评委组合，没有银弹**：确定性评分器（脚本 / 断言 / Schema / LCS，负责硬指标）＞ LLM-as-a-Judge / Rubric 评分器（负责开放式软指标）＞ 人工评分器（校准、诊断、兜底）。优先级是「能用代码判断的绝不用模型，必要时用模型，人工只用于校准与诊断」。
4. **多维度指标体系**：功能正确性、过程质量、效率与成本、鲁棒性与安全、体验与对齐；稳定性用 `pass@k`（峰值能力）与 `pass^k`（一致性）区分。
5. **工程化是关键**：黄金评测集（小而精、覆盖边界、GT 可复核、版本化）＋ 基线快照 ＋ 多轮（N 次）执行 ＋ 进 CI 回归 ＋ Trace 输出能力 ＋ 隔离环境（git worktree）。
6. **新范式**：用一个「顶级 Agent（如 Claude Code）」当 Harness 搭建评测骨架，把评测逻辑从「代码」升级为「Prompt」；甚至让 AI 自主生成评测集、模拟用户跑评测、读报告自动优化系统，实现「一晚上自动评测 + 优化」。

需要强调的覆盖限制：资料库以阿里 / 淘天 / 腾讯系公众号工程实践为主，**偏工程落地与平台搭建**，对学术 Benchmark（AgentBench、τ-bench、GAIA、SWE-bench 等）只有零散引用，没有专门系统综述；唯一偏学术综述的是 Agent-Memory 子领域。

## 覆盖范围

- 资料库：`E:/work/gongzhonghao_md`（子目录：alitech / taobaotech / tengxuntech / tengxunyun / aliyun / aliyunys）
- 是否递归：是
- 扫描文件数：412 个 `.md` 文件
- 候选资料数：约 18 篇（文件名 / 标题 / 正文命中「评测 / 评估 / Benchmark / Eval / Agent」组合后，经第一轮相关性判断纳入观察；其中关键词重叠但主题不同者经全文或抽样做了主题校验）
- 全文阅读上限：15 篇（本任务约定）
- 完整阅读资料数：8 篇（相关 / 部分相关全部逐篇读完；另对 5 篇「关键词重叠但主题不同」的资料做了全文或抽样主题校验后排除）
- 检索词：
  - 中文：评测、评估、测评、基准、基准测试、评测集、评测维度、评分器、评委、裁判、打分、通过率、任务完成度、轨迹评估、过程评估、稳定性、黄金标准 / Ground Truth、自动化评测
  - 英文：Eval、Evaluation、Benchmark、LLM-as-a-Judge / LLM-as-Judge、Rubric、Trace、Trajectory、pass@k、pass^k、AgentBench、SWE-bench、GAIA、τ-bench / tau-bench
  - Agent 相关：Agent、智能体、多智能体、Multi-Agent、Agentic、Agentic Ops、工具调用 / Tool call、子 Agent、Harness

## 相关文章

| 文章名 | 路径 | 相关性 | 关键内容 |
| --- | --- | --- | --- |
| AI Agent & Skill 测评方案及落地实践 | `E:/work/gongzhonghao_md/tengxuntech/AI_Agent___Skill_测评方案及落地实践.md` | 相关（最系统） | 三类评委（确定性 / Rubric / 人工）＋ 五维度（功能正确性 / 过程质量 / 效率成本 / 鲁棒安全 / 体验对齐）＋ 用例四场景 ＋ 基线 ＋ 稳定性（pass@k / pass^k）＋ CI 工程化 ＋ TPerf 实战案例 |
| 你的 Harness 工作流真的在进步吗？我们用一场考试撕掉了遮羞布 | `E:/work/gongzhonghao_md/tengxuntech/你的_Harness_工作流真的在进步吗_我们用一场考试撕掉了遮羞布.md` | 相关 | 「考试」式 Harness Eval：出题（meta/task/rubric/env）→ 答题（Examiner 多轮模拟用户 + Examinee）→ 改卷（独立 Judge「上帝视角」看 transcript 逐帧打分举证）；多维度＋证据＋三维度归因改进 [workflow]/[eval]/[capability]；git worktree 隔离、回归趋势 |
| 基于顶级 Agent（Claude Code）的 Harness 工程搭建式业务 Agent 评测方案 | `E:/work/gongzhonghao_md/aliyun/基于顶级_Agent（Claude_Code）的_Harness_工程搭建式业务_Agent_评测方案.md` | 相关 | 用强 Agent（CC）搭评测 Harness，把评测逻辑从代码变 Prompt；三层指标框架 L1/L2/L3；「评测 Agent 调被测 Agent」；LLM-as-Judge rubric 设计；效率对比 ~5-10x |
| Harness Engineering 实践：做了一个平台让 AI 一晚上自动评测和优化你的系统 | `E:/work/gongzhonghao_md/aliyun/Harness_Engineering实践_做了一个平台让AI一晚上自动评测和优化你的系统.md` | 相关 | AI First 评测平台：AI 自主发任务 / 生成评测集 / 模拟用户跑评测 / 提交报告 / 读报告自动优化；标准评测集 vs rubrics 分级；UI + 内容质量评测；三轮自动优化分数 90.7→97.4→99.1 |
| 面向智能导购的 Agent 评测实践 | `E:/work/gongzhonghao_md/taobaotech/面向智能导购的Agent评测实践.md` | 相关 | 端到端自动化评估链路：Benchmark → LLM-as-a-judge（91.9% 准确率）→ 人工抽样校准 → 自动报告；两级评测维度（4 一级 / 22 二级）；多基座横向对比；PLCC 评测模型一致性 |
| Agent-Memory 评测全景：基准、评估与记忆系统（理论篇） | `E:/work/gongzhonghao_md/taobaotech/Agent_Memory_评测全景_基准_评估与记忆系统（理论篇）.md` | 相关（子领域） | Agent 长期记忆评测综述：基准（MUSE/LOCOMO）、评估框架（MemoryAgentBench/LONGMEMEVAL/MemBench）、四能力（准确检索 / 测试时学习 / 长程理解 / 冲突解决）、四维评测（检索正确性 / 使用有效性 / 时间 / 成本） |
| 从零设计生产级 Multi-Agent Harness：架构、评估、记忆、成本与 MCP 工具接入全拆解 | `E:/work/gongzhonghao_md/tengxunyun/从零设计生产级_Multi_Agent_Harness_架构_评估_记忆_成本与_MCP_工具接入全拆解.md` | 部分相关 | 第 05 节专讲评估：四层 Eval Pipeline（组件 / 轨迹 / 任务完成度 / 端到端）；LLM-as-Judge 非万能、必须混合确定性检查；Eval 必须进 CI（Prompt 即代码、轨迹即日志） |
| 阿里云正式发布 RCA Benchmark：业界首个面向 Agentic Ops 的根因分析开源基准体系 | `E:/work/gongzhonghao_md/aliyunys/阿里云正式发布_RCA_Benchmark_业界首个面向_Agentic_Ops_的根因分析开源基准体系.md` | 部分相关（领域窄） | 评测对象是 RCA 运维智能体：运行环境（微服务仿真）+ 四层结构化真值（故障类型 / 归一根因实体 / 因果传播链 / 关键证据）+ 定因/定界/过程三维加权（40/30/30），近七成确定性量化、规避随机命中 |

## 综合总结

### 一、为什么 Agent 评测难、且不同于传统测试

多篇资料给出高度一致的「三大难题」诊断（《AI Agent & Skill 测评》《Multi-Agent Harness》《你的 Harness 工作流》）：

- **非确定性**：同一 prompt 多次执行结果不同，「跑通一次」≠「稳定能跑」。
- **黑盒化 / 行为漂移**：模型升级、Prompt 微调、工具链变化都可能让旧场景悄悄退化。
- **错误级联放大**：一次任务几十步工具调用，前序小偏差沿链路逐级放大。

由此推出一个共识：传统单元测试那套「assert output == expected」的二值判定不够用。《你的 Harness 工作流》把它升华为「从**测试**到**考试**的思维跃迁」——测试验证「对不对」（boolean），考试评估「好不好」（多维度打分 + 证据 + 改进建议），因为 Agent 的「正确」是一个光谱而非布尔值。

### 二、谁来评：三类评委组合（强共识）

《AI Agent & Skill 测评》给出最完整的对照，《Multi-Agent Harness》《Agent 评测方案》《Harness 自动评测平台》《智能导购》均印证：

- **确定性评分器**（脚本 / 断言 / Lint / AST / Schema / LCS）：快、便宜、客观、可复现，负责「能用代码判断」的硬指标（文件存在、构建通过、工具调用序列、token 阈值）。是日常主力与硬门禁。
- **Rubric / LLM-as-a-Judge 评分器**：灵活，处理开放式自然语言输出（回答质量、语气、推理合理性）。但**多篇资料反复警告其有偏差、不是万能药**——对事实正确性、代码可运行性、SQL 结果、权限合规应优先用确定性检查。
- **人工评分器**：最贵，只用于六个场景，其中**「校准 LLM 评委」是最核心用途**（抽样 100-200 条，与 LLM 打分一致率 ≥ 85% 才算可用），其余为诊断 0%/100% 异常、建 Ground Truth、Trace 采样审查、高风险兜底。

优先级一致：**确定性 > Rubric > 人工**。

### 三、评什么：维度体系（各家有详略，但骨架一致）

- 最系统的是《AI Agent & Skill 测评》的**五大类**：功能正确性（结果正确性 / 任务完成度 / 指令遵循 / 工具调用正确性，P0）、过程质量（推理合理性 / 步骤最优性 / 信息完整性 / 上下文利用 / 自我纠错，P1）、效率与成本（Token / 工具调用次数 / 延迟 / 重试率 / 单次成本，P1）、鲁棒性与安全（一致性 pass^k / 异常恢复 / 抗注入 / 幻觉率 / 越权 / 合规 / 拒绝合理性，P0）、体验与对齐（语气 / 清晰度 / 主动澄清 / 同理心 / 满意度，P2）。
- 《Multi-Agent Harness》给出**四层 Eval Pipeline**：组件评估（单 Agent 选对工具 / 参数合规）→ 轨迹评估（步骤是否必要 / 顺序 / 是否循环，「最大创新点」）→ 任务完成度评估 → 端到端业务效果（采纳率 / 返工率 / 单位成本）。
- 《智能导购》给出**两级维度**（4 一级宏观能力 + 22 二级诊断细节）的具体落地样例。
- 共同强调的「过程 / 轨迹」维度，是 Agent 评测区别于单轮模型评测的标志。

### 四、稳定性度量：pass@k 与 pass^k（多篇统一术语）

- `pass@k`：k 次中**至少 1 次**通过的概率 → 衡量峰值能力。
- `pass^k`：k 次中**每次都**通过的概率 → 衡量一致性 / 稳定性。
- 《AI Agent & Skill 测评》给出按 Agent 类型分级的容忍阈值：关键决策类 0% 容忍（N/N 全过）、辅助分析类 ≤10%、创意生成类 ≤40%；并指出「0% pass^N 通常是任务定义 / 评分器坏了，不是模型弱」。Anthropic 推荐：确定性任务用例集整体通过率需 100%，非确定性任务 ≥95%。

### 五、工程化要素（落地共识）

- **黄金评测集**：小而精（20-55 条覆盖边界优于 200+ 条简单 case）、分布均衡、GT 可复核、随被测 Prompt 版本化（《Agent 评测方案》《AI Agent & Skill 测评》）。
- **基线快照**：「先跑出来 → 人工确认 → 即成预期基线」，后续与基线逐项对比；Agent 逻辑 / 模型升级 / 用例修改时需重建基线。
- **Trace / 轨迹是前提**：被测 Agent 必须能输出结构化执行轨迹（JSONL：工具名 / 入参 / 返回 / 时间戳 / 思维链），否则过程评测无从下手。判分须有「上帝视角」（看 tool call 实际行为，而非只看对话里 Agent「说」做了什么）——《你的 Harness 工作流》把「让考官顺便判分」列为踩过最痛的坑。
- **隔离与回归**：每个用例 / run 在隔离环境执行（clone / git worktree / 环境重置）；评测必须进 CI，每次改 Prompt / 换模型 / 加工具都跑回归；记录 workflow_rev（git commit）以定位「哪一版改了什么导致涨跌」。
- **多评测模型 / 多评委投票**降噪（《智能导购》用 PLCC 相关性选最优评测口径）。

### 六、两条「AI First / Harness 化」新范式（独有机制，需保留）

1. **用强 Agent 搭评测 Harness**（《Agent 评测方案》）：让 Claude Code 当方案架构师 / 数据工程师 / Harness 工程师 / 数据分析师，把评测脚本（Python/Java）替换为「评测 Agent 提示词」，由「评测 Agent 通过工具调用被测 Agent」获取输出再打分；单 Agent 全流程从 ~1.5 周压到 1-2 天（~5x）。
2. **AI 全自动评测 + 优化闭环**（《Harness 自动评测平台》）：平台只允许 AI 操作、从入口杜绝人干苦力；AI 自主发任务、生成评测集（标准型 + rubrics 分级）、模拟用户跑评测（含连浏览器做 UI + 内容质量评测）、提交报告，再让 CC/Cursor 读报告自动优化系统，往复三轮，分数 90.7→97.4→99.1 稳步上升。

### 共识、差异与不确定

- **共识**：三类评委组合、过程 / 轨迹评估不可省、LLM-as-Judge 必须人工校准且非万能、稳定性多轮 + pass@k/pass^k、评测进 CI、基线驱动回归。多篇明确参考 OpenAI / Anthropic 一手资料（如 Anthropic 的 *Demystifying evals for AI agents*、*Evaluating AI agents*）。
- **差异 / 侧重**：腾讯系（《AI Agent & Skill 测评》《你的 Harness 工作流》）偏**通用方法论 + 平台工程**；阿里 / 淘天（《Agent 评测方案》《Harness 自动评测平台》《智能导购》）偏 **Harness / AI First 自动化**与具体业务落地；《Agent-Memory 评测全景》偏**学术 Benchmark 综述**（且专注记忆子能力）；《RCA Benchmark》偏**特定领域（运维智能体）标准化基准**。
- **不确定 / 留白**：资料库缺少对通用 Agent 学术 Benchmark（AgentBench、τ-bench、GAIA、SWE-bench）的系统介绍，仅《智能导购》参考文献列了 VisualAgentBench / DeepResearch Bench / WideSearch。多模态、长程任务、人机协同实时评测被多篇列为「未来方向」，尚无成熟方案。

## 单篇文章摘要

### 《AI Agent & Skill 测评方案及落地实践》

- 路径：`E:/work/gongzhonghao_md/tengxuntech/AI_Agent___Skill_测评方案及落地实践.md`
- 相关性：相关（资料库中最系统、最完整的一篇，约 1026 行）
- 核心观点：面对 Agent 非确定性、黑盒化、错误级联放大三大难题，建立「确定性评分器 + Rubric 评分器 + 人工评分器」三类组合框架，覆盖功能正确性 / 过程质量 / 效率成本 / 鲁棒安全 / 体验对齐五大维度。核心公式 `Eval = 输入→执行→捕获 Trace+产物→检查规则→可对比分数`。
- 关键证据：
  - 三类评委优先级「确定性 > Rubric > 人工」，人工 60%+ 时间花在「校准 LLM 评委」（一致率 ≥85% 才可用）和「诊断异常」（第 2 章 2.1）。
  - 五大维度表 + P0/P1/P2 优先级（2.2）；术语：pass@k 衡量峰值、pass^k 衡量稳定性。
  - 用例设计四场景（触发 / 核心逻辑 / 产物质量 / 异常容错），各含正 / 负向用例；核心逻辑用例量最大（3.1）。
  - 评分负分制（初始 100，达标 80）、基线「先跑出来再确认即预期」（3.2-3.3）。
  - 稳定性按 Agent 类型分容忍阈值：关键决策 0%、辅助分析 ≤10%、创意生成 ≤40%（4.3）；「0% pass^N 多是任务 / 评分器坏了」。
  - 前置依赖：被测 Agent 必须输出结构化 Trace（JSONL，如 CodeBuddy-Code `-p` 模式）（4.1）。
  - TPerf 性能分析 Agent 实战：确定性（操作步骤 LCS 对齐 -10 / 效率 -10）+ 模型评分（关键判定 -80 / 章节内容每项 -5）；模型对比报告含 pass@1 / pass^5（第 5 章）。
  - 明确参考 Anthropic *Demystifying evals for AI agents*、*Evaluating AI agents* 与 OpenAI *Eval skills*（第 6 章）。

### 《你的 Harness 工作流真的在进步吗？我们用一场考试撕掉了遮羞布》

- 路径：`E:/work/gongzhonghao_md/tengxuntech/你的_Harness_工作流真的在进步吗_我们用一场考试撕掉了遮羞布.md`
- 相关性：相关（一套完整的 Harness/Agent 工作流闭环评测系统「Harness Eval」）
- 核心观点：不可量化的东西不可优化；Harness 工作流是「规则驱动的概率程序」，必须用「考试」（多维打分 + 证据 + 改进建议）而非「测试」（二值）来评估，否则面对「薛定谔式退化」。
- 关键证据：
  - 三原则：可重复 > 精确、可归因 > 高分、闭环 > 单向。
  - 系统三件事：出题 → 答题 → 改卷。一道题 = meta.yaml + task.md + rubric.md + env.yaml（题面与阅卷分离，考生看不到 rubric）。题库分 5 波次（主干闭环 / 状态机门禁 / 知识库 / 周边 skill / 韧性）。
  - 引入 **Examiner（考官，LLM 扮演用户多轮交互）**，因真实场景是多轮的，去掉交互测的是「Agent 自嗨能力」。
  - **判卷独立于对话**（踩过最痛的坑）：Judge 是独立进程、无共享上下文，输入仅 rubric.md + 精简版 transcript，须有「上帝视角」看 tool call 实际行为；逐项核对硬性标准、评估过程质量、多维度打分、引用 transcript 原文举证、强制三维度归因改进 [workflow]/[eval]/[capability]。
  - 输出 score.yaml（result + compliance/execution_quality/overall 0~5）+ review.md（evidence + improvements）。
  - 工程：Go 单 CLI、git worktree 隔离并发、symlink 替换工作流快照、transient 错误分级重试、workflow_rev 记录 git commit 追因。
  - 效果：通过率 82.4%（14/17）→ 100%（17/17），4 轮迭代 + 50+ run。

### 《基于顶级 Agent（Claude Code）的 Harness 工程搭建式业务 Agent 评测方案》

- 路径：`E:/work/gongzhonghao_md/aliyun/基于顶级_Agent（Claude_Code）的_Harness_工程搭建式业务_Agent_评测方案.md`
- 相关性：相关
- 核心观点：用一个顶级 Agent（Claude Code）当 Harness 搭建者，把评测逻辑从「代码」升级为「Prompt」，系统性评测一群业务 Agent；解决「业务 Agent 天级迭代但传统评测周级搭建」的矛盾。
- 关键证据：
  - 三层指标框架：L1 通用基础（格式合规率 / 字段完整率，必报）、L2 按能力类型选用（分类准确率 / 召回精确率 / MAE / LLM-as-Judge 1-5 分）、L3 Agent 专属。
  - 评测 Agent 提示词模板（角色 + 工具声明 + 约束 + 工作流 + 输出 Schema）；最核心创新是「把评测脚本替换为评测 Agent 提示词」「一个 Agent 评测另一个 Agent」。
  - 「评测 Agent 调被测 Agent」链路与踩坑（忘记调工具 / 参数传递失败 / 重试耗尽 token / 输出截断）。
  - LLM-as-Judge rubric 设计：每个分值（1-5）须有具体可区分标准，避免「好 / 较好 / 一般」。
  - 评测集设计原则：小而精（20-55 条）、分布均衡、GT 可复核、版本化。
  - 效率：单 Agent 全流程 ~1.5 周 → 1-2 天（~5x），方案设计 ~10x；与 OpenAI Evals 框架「理念类似但更轻量、无需工程部署」。

### 《Harness Engineering 实践，做了一个平台让 AI 一晚上自动评测和优化你的系统》

- 路径：`E:/work/gongzhonghao_md/aliyun/Harness_Engineering实践_做了一个平台让AI一晚上自动评测和优化你的系统.md`
- 相关性：相关
- 核心观点：AI First 评测理念——定义好评测任务后，让 AI 自主生成评测集、模拟用户运行评测、生成报告，乃至读报告自动优化系统并往复迭代；平台从入口层面只允许 AI 操作。
- 关键证据：
  - 平台三能力：创建评测任务（含评测目标 / 验收标准）、创建评测集（明确步骤 + 预期结果）、创建评测报告（打分）。
  - 两类评测集：标准型（明确成功 / 失败状态）与 rubrics 型（内容质量无法二值，生成不同等级评测用例）。
  - 案例：钉钉文档 MCP 全功能评测（AI 自动设计 13 个用例、总分 95，可推广到 skill 包生成几百个评测用例判断触发与效果）；绘报 PPT 的 UI + 内容质量评测（连浏览器、共享登录态）；系统自动优化往复三轮，v1→v2→v3 分数 90.7→97.4→99.1。
  - 先决条件：系统 UI 规范 / 基础设施达标（否则 AI 在 UI 里迷路）、系统 AI Coding 含量高（否则 AI 难跑通和优化）。

### 《面向智能导购的 Agent 评测实践》

- 路径：`E:/work/gongzhonghao_md/taobaotech/面向智能导购的Agent评测实践.md`
- 相关性：相关
- 核心观点：为家居导购 Agent 搭端到端自动化评估链路，基于结构化多维度 Benchmark + LLM-as-a-judge（91.9% 准确率）+ 人工抽样校准，量化对比不同基座模型并做错误归因。
- 关键证据：
  - 四模块闭环：Benchmark 创建 → LLM 模拟人工评测（多评审投票）→ 人工抽样验收（质量闸门）→ 自动化评测与报告。
  - 两级评测维度：4 个一级（宏观能力 / 任务完成度）+ 22 个二级（诊断指标，True/False 输出后聚合）。
  - 量化结果：gpt51 总分 0.680 最优，较线上 qwen3-vl（0.584）提升 16.4%；评测模型一致性用 PLCC 相关性排序（gemini25 0.962 最高），选最优评测口径。
  - 三大共性瓶颈：无法识别已有家具（重复推荐）、未抓住核心需求（跑题）、推荐过量。
  - 评测准确率 = (1927-156)/1927 = 91.90%；参考 VisualAgentBench / DeepResearch Bench / WideSearch。

### 《Agent-Memory 评测全景：基准、评估与记忆系统（理论篇）》

- 路径：`E:/work/gongzhonghao_md/taobaotech/Agent_Memory_评测全景_基准_评估与记忆系统（理论篇）.md`
- 相关性：相关（聚焦 Agent 评测的「长期记忆」子能力，偏学术综述）
- 核心观点：系统梳理 Agent 长期记忆评测全景，沿基准数据集 / 评估框架 / 记忆系统三主线；指出评测不应止于「跑分排名」，要回答「记什么、怎么记、是否带来可量化任务收益」。
- 关键证据：
  - Benchmark：MUSE、LOCOMO（50 对话 / 平均 300 轮，QA / 事件总结 / 多模态生成，gpt-4-turbo 32.4 远低于人类 87.9）。
  - Evaluation：MemoryAgentBench（四核心能力：准确检索 AR / 测试时学习 TTL / 长程理解 LRU / 冲突解决 CR；CR 多跳准确率最高仅 6%）、LONGMEMEVAL（准确率下降 30-60%）、MemBench（事实 + 反思记忆、参与 + 观察场景、准确率 / 召回 / 容量 / 效率多指标）。
  - System：THEANINE/TeaFarm（反事实评估）、RMM、M3-Agent/M3-Bench、Mem0/Mem0g（LOCOMO 上单跳 / 多跳 / 时间 / 开放域，F1 + BLEU + LLM 评估，p50/p95 延迟）。
  - 现有评测共性问题：增益难归因、口径不统一（命中但无用）、动态更新 / 遗忘覆盖不足、成本约束缺位；建议同时覆盖检索正确性 / 使用有效性 / 时间维度 / 成本维度四维。

### 《从零设计生产级 Multi-Agent Harness：架构、评估、记忆、成本与 MCP 工具接入全拆解》

- 路径：`E:/work/gongzhonghao_md/tengxunyun/从零设计生产级_Multi_Agent_Harness_架构_评估_记忆_成本与_MCP_工具接入全拆解.md`
- 相关性：部分相关（全文讲 Harness 架构，第 05 节「评估体系」直接命中主题）
- 核心观点（评估部分）：Multi-Agent 评估是被低估最严重的环节，「不要只看答案，要看轨迹」；只看最终答案会漏掉「答案对但过程错」的危险信号。
- 关键证据：
  - 四层 Eval Pipeline：① 组件评估（单 Agent 选对工具 / 参数合规 / 输出符合角色）② 轨迹评估（步骤是否必要 / 顺序 / 重复调用 / 是否循环，「Multi-Agent 最大创新点」）③ 任务完成度评估 ④ 端到端业务效果（采纳 / 返工率 / 时长 / 单位成本）。
  - 「LLM-as-Judge 不是万能药」：适合开放式表达，事实正确性 / 代码可运行 / SQL / 权限合规应优先确定性检查；成熟 Eval 必然混合（单测 + Schema + 规则引擎 + 检索对齐 + LLM-Judge + 人工抽检 + 线上反馈）。
  - Eval 必须进 CI：「Prompt 就是代码，工具 Schema 就是接口，执行轨迹就是日志，Eval 就是测试体系」。
  - （其余章节：Orchestrator 五项决策权、Tool Registry 九项元信息、状态 / 记忆分层、Token Budget 分级降级、MCP 接入治理——与评测主题相关性较弱，作为上下文。）

### 《阿里云正式发布 RCA Benchmark，业界首个面向 Agentic Ops 的根因分析开源基准体系》

- 路径：`E:/work/gongzhonghao_md/aliyunys/阿里云正式发布_RCA_Benchmark_业界首个面向_Agentic_Ops_的根因分析开源基准体系.md`
- 相关性：部分相关（评测对象确为 AI Agent——运维智能体 RCA Agent，但领域窄、偏产品 / 标准发布）
- 核心观点：根因分析是运维智能体能力评估中复杂度最高、最难标准化的环节；不同于有固定标准答案的文本 / 代码任务，RCA Agent 需主动从多源观测数据交互式诊断，传统静态日志 + 单标签评测全面失效。建立标准化、可复现、可审计的 Agent 故障诊断评估基准。
- 关键证据：
  - 基准三模块：运行环境（K8s 上 40+ 服务、最长 7 层调用链的微服务仿真，支持 Agent 交互式诊断查询）、结构化样本集（四层 Ground Truth：故障类型 / 归一化根因实体 / 因果传播链 / 关键证据检查点）、评估协议（确定性规则为核心，最大限度减少大模型评审依赖）。
  - 三维加权评分：定因 / 定界 / 过程 = 40% / 30% / 30%，近七成依托故障类型拓扑语义距离、实体拓扑距离做确定性量化，规避随机命中。
  - 含「过程」评分维度（评估 Agent 的诊断过程）、统一实体模型 UModel 解决跨域标识割裂、四层 GSTO 质量门禁、200+ 样本分 L1-L4 难度（以 L2/L3 为核心）。
  - 价值：为运维智能体诊断能力提供可横向对标、可量化的统一标尺。

## 排除或低相关资料

| 文章名 | 原因 |
| --- | --- |
| 谁是 Agent 最强守门员？首个 Agent 技能安全评测基准 SkillTrustBench 正式发布（`tengxuntech/谁是_Agent_最强守门员...SkillTrustBench_正式发布.md`） | **主题校验排除**：含「Agent / 评测 / 基准 / Benchmark / Leaderboard」等大量重叠关键词，但评测核心对象是 **Skill 的安全可信度 + 安全扫描方案 / 大模型的恶意 Skill 检测效能**（召回 / 误报 / F1），不是 AI Agent 的任务完成度 / 工具调用 / 多轮推理能力。属于供应链安全检测 Benchmark。 |
| 让 Skill 自己训练自己：8 阶段 Loop、3 层评测、5 维 AND 门控，从此实现自进化（`tengxunyun/让Skill自己训练自己...自进化.md`） | **主题校验排除**：核心是单个 **Skill 的自进化 / 自训练框架**，其中「3 层评测」是自训练 Loop 内对「单个 skill 输出是否 match 数据分布」的质量门控，评测对象是 Skill（能力单元）而非 AI Agent 系统的任务 / 工具 / 多轮能力。方法论上与 Agent 评测有重叠（回归、门控），但主体不同。 |
| 如何定义"人味儿"？——HeartBench 评测体系建设实践（`aliyun/如何定义_人味儿____HeartBench评测体系建设实践.md`） | **主题校验排除**：评测对象是**大模型的情感 / 社交智能（「人味儿」）**这一内容 / 输出特质，对标 MMLU/HumanEval 之外的情感维度，属于模型能力 Benchmark，非 AI Agent 系统评测。 |
| 给"氛围编程"系上安全带：阿里集团 AI 代码评审实践与 Benchmark 开源（`alitech/给_氛围编程_系上安全带...Benchmark_开源.md`） | **主题校验排除**（恰为 SKILL.md 列举的典型例子）：含「评测 / Benchmark / 同一家公司」，但评测对象是 **AI 代码评审（Code Review）的质量**（CodeReview Benchmark），不是 AI Agent 的任务执行能力。 |
| 从 3632 个漏洞看 AI 时代的评测基准重构！VulnGym 基准发布（`tengxuntech/从3632个漏洞看...VulnGym基准发布.md`） | **主题校验排除**：含「评测基准 / Benchmark」，但评测对象是**漏洞检测工具 / 模型的漏洞发现能力**（业务逻辑漏洞），属安全检测 Benchmark，非 AI Agent 系统评测。 |
| 拒绝"感觉有效"：用数据证明 AI Coding 的真实团队价值（`taobaotech/拒绝_感觉有效__用数据证明_AI_Coding_的真实团队价值...md`） | **低相关**：是 **AI Coding 的 ROI / 团队价值度量体系**（质量 / 链路 / 结果三层、采纳率 / 覆盖率 / Token 成本），其中「质量指标—离线评测」对模型编码能力有评测，但全文主体是衡量「AI Coding 对团队的真实价值」，非「如何评测一个 AI Agent」的方法论。 |
| 阿里开源 Open Code Review 一周揽下 5k star，更专业的代码评审 CLI（`alitech/阿里开源_Open_Code_Review...CLI.md` 及 aliyun 同名） | **低相关**：代码评审工具产品介绍，评审对象是代码，不是 Agent 评测。 |
| Hy3 preview 发布并开源 / 腾讯混元 Hy3 preview（Agent 能力大幅提升）、赛博斗蛐蛐 9 大模型决战三国志 等 | **低相关（按原因分组，约 4-6 篇，未逐条列出）**：均为**模型能力评测 / 模型对比**（含 Agent 能力跑分），评测对象是底座模型而非「AI Agent 系统的评测方法论」；与本问题相关性弱，未进入全文阅读。 |

> 说明：除上表逐条列出者外，资料库中另有约 4-6 篇仅在正文零散出现「评测 / 评估」但主题为 Harness 工程 / Skill 编写 / Agent 架构 / 记忆系统 / Token 成本（如《Harness Engineering 长程自动化》《如何写好 Skill》《腾讯云 Agent Memory 节省 61%》等）的文章，因评测非其核心主题、且无独立的 Agent 评测方法论贡献，按相关性排序后未进入前述阅读集合，此处不逐条展开。

## 不确定性

- **候选总量为估计值**：检索词命中分布广（含 Harness / Skill / Memory / 成本等弱相关上下文），「候选 ~18 篇」是经第一轮人工相关性判断后的观察集合，非精确去重统计；命中「评测 / 评估」关键词的文件总数达 60+，但绝大多数属弱相关上下文。
- **未读资料的残余风险**：受 15 篇全文上限约束，对判为「低相关 / 模型评测类」的文章仅做了标题 + 摘要 / 抽样校验，不排除其中个别章节含可用的 Agent 评测细节；但其核心主题已足以判定主次。
- **学术 Benchmark 覆盖不足**：资料库以工程实践为主，对通用 Agent 学术基准（AgentBench、τ-bench、GAIA、SWE-bench、WebArena 等）无系统介绍，本报告对这些的描述仅来自资料内零散引用，不能视为资料库对该子主题的完整覆盖。
- **RCA Benchmark 的归类**：将其判为「部分相关」是基于其评测对象确为 AI Agent（运维智能体）且含过程 / 轨迹评分；但它领域很窄、偏标准 / 产品发布、缺少可迁移到通用 Agent 的细粒度方法步骤，故未上调为「相关」。若研究目标只关注通用方法论，可进一步下调。
- **时效性**：资料发布集中在 2026 年 3-6 月，反映的是该时间窗的业界实践；术语（pass@k/pass^k 用法、LLM-as-a-Judge 校准阈值）在不同团队间已基本对齐，但具体阈值（如一致率 ≥85%、通过率 100%/95%）为各团队经验值，非行业硬标准。
