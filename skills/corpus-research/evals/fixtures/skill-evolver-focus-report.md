## 结论

`skill-evolver` 的核心做法，是把 `Skill` 当成可以被「训练」的对象：先用标准答案和评测计划定义什么叫好，再让 Agent 在受控工作区中按轮次提出小改动、真实运行评测、用硬门控决定保留或回滚，最后把每轮结果、失败样例和执行轨迹沉淀为下一轮诊断依据。

资料库中只有一篇文章把核心对象明确命名为 `skill-evolver`：`《让Skill自己训练自己：8阶段Loop、3层评测、5维AND门控，从此实现自进化》`。其余相关文章主要提供相邻背景，例如「Skill 开发 Harness」「Skill 迭代式编写」「Trace2Skill / EvoSkill / SkillOpt」等，但核心对象不是 `skill-evolver`，因此只作为部分相关背景，不作为判断 `skill-evolver` 机制的主证据。

关键机制可以概括为 6 点：

1. **来源拼装**：`Skill-Evolver = AutoResearch` 的外循环骨架 + `skill-creator` 的评测引擎 + `Meta-Harness` 的 trace 诊断大脑。证据见 `tengxunyun/让Skill自己训练自己_8阶段Loop_3层评测_5维AND门控_从此实现自进化.md:114-116`、`:350-357`。
2. **数据定义目标**：用 GT 定义期望输出，用 8 种 assertion 检查结果，用 dev / holdout / regression 区分优化、泛化和回归防护。证据见同文 `:134-142`、`:193-203`。
3. **8 阶段循环**：`Setup → Review → Ideate → Modify → Commit → Verify → Gate → Log → Loop`；每轮只做一个原子改动，先提交保留审计轨迹，再评测和门控。证据见同文 `:148-174`。
4. **三层评测**：L1 做结构和安全快速门卫，L2 跑全量 dev GT case，L3 在触发条件下跑 holdout / regression / blind A/B。证据见同文 `:178-203`。
5. **5 维 AND 门控**：任一维度不通过就 `git revert`，避免用一个高分维度掩盖另一个维度退化。证据见同文 `:207-211`。
6. **trace 驱动诊断**：每个 case 的完整执行记录落盘；下一轮 proposer 先看 trace，再用证据解释失败原因和改动方向，禁止凭感觉修改。证据见同文 `:219-221`。

## 覆盖范围

- 资料库：`E:/work/gongzhonghao_md`
- 是否递归：是
- 纳入扩展名：`.md`
- 扫描文件数：412
- 候选资料数：57
- 全文阅读上限：15 篇
- 完整阅读资料数：4 篇
- 检索词：`skill-evolver`、`Skill Evolver`、`evolver`、`Skill 自我迭代`、`Skill 自进化`、`Skill 评测`、`Skill 测评`、`8阶段`、`3层评测`、`5维AND`、`AND门控`、`Meta-Harness`、`分层 mutation`、`Ground Truth`、`Rubric`、`skill-creator`、`skill-judge`、`EvoSkill`、`SkillOpt`、`Trace2Skill`、`SkillClaw`、`SkillTrustBench`、`skill-eval-setup`
- 搜索方式：文件名、标题 / 一级标题 / 二级标题、正文全文高召回检索；对关键词命中的候选做主题校验。
- 禁读约束：未打开、读取或搜索 `E:/work/my-ai-resource/skills/corpus-research/evals/behavior_gt.json`，也未读取任何 GT / must_recall / should_not_include 答案文件。

## 相关文章

| 文章名 | 路径 | 相关性 | 关键内容 |
| --- | --- | --- | --- |
| 《让Skill自己训练自己：8阶段Loop、3层评测、5维AND门控，从此实现自进化》 | `E:/work/gongzhonghao_md/tengxunyun/让Skill自己训练自己_8阶段Loop_3层评测_5维AND门控_从此实现自进化.md` | 相关 | 唯一明确命名 `skill-evolver` 的文章；完整说明 8 阶段 Loop、三层评测、5 维 AND 门控、trace 诊断、meta-evolution 实验和业务实战。 |
| 《Harness Engineering：长程自动化 AI Coding / Skills 开发实践》 | `E:/work/gongzhonghao_md/alitech/Harness_Engineering_长程自动化_AI_Coding___Skills_开发实践.md` | 部分相关 | 讨论 `Skill` 开发 Harness 的评测改进循环、角色隔离、Rubric 判分和平台化可视化；不是 `skill-evolver`，但与其「评测驱动 Skill 迭代」思想相邻。 |
| 《Agent skill 迭代式编写实战》 | `E:/work/gongzhonghao_md/taobaotech/Agent_skill_迭代式编写实战.md` | 部分相关 | 讨论人工 / 半自动的 `Skill` 迭代开发，包含 `skill-creator`、`skill-judge`、外部 eval、触发率优化；不是 `skill-evolver`。 |
| 《如何更科学、方向可控的实现 Skill 的“自进化”?》 | `E:/work/gongzhonghao_md/aliyun/如何更科学_方向可控的实现_Skill_的_自进化__.md` | 部分相关 | 综述 Trace2Skill、EvoSkill、SkillOpt 三类 Skill 自进化方案；核心对象不是 `skill-evolver`，但能解释同类问题中为什么需要验证、门控和反过拟合。 |

## 综合总结

### `skill-evolver` 为什么不是普通 prompt 调参

文章认为，一个 `Skill` 表面上像 `prompt`，实际上更像一套 `harness`：它包含触发边界、安全规则、references 一致性、脚本兼容性等工程约束。普通做法是手工写 `SKILL.md`、手动测几个用例、发现不对再改；问题是作者很难知道改动是否真正匹配数据分布，也难判断改了一个 case 会不会弄坏另一个 case。主文用「员工离职后邮箱还在不在」却应该命中通讯录资料的例子，说明「能跑」和「真的好」之间的差距在于输出是否匹配既定数据和标准。

所以 `skill-evolver` 的目标不是让语法检查通过，而是让 `Skill` 在用户定义的输入分布上逼近目标效果。它用 GT 和 assertion 定义「好」，用循环评测和门控决定是否保留改动，用 trace 把失败变成可诊断证据。

### 外循环：从 AutoResearch 借来「试错、保留、回滚」

主文明确说 `skill-evolver` 拼接了三种思想：`AutoResearch` 提供自主迭代外循环，`skill-creator` 提供评测和创建能力，`Meta-Harness` 提供原始 trace 驱动诊断。它不是让 Agent 一次性生成完美 `Skill`，而是让 Agent 像做实验一样一轮轮尝试：提出一个原子改动，运行评测，达标就保留，不达标就回滚。

8 阶段 Loop 中，`Phase 0` 负责创建 workspace、生成评测计划、建立 baseline；后续每轮经过 `Review`、`Ideate`、`Modify`、`Commit`、`Verify`、`Gate`、`Log`、`Loop`。其中 `Review` 会读最近的 git log、results.tsv、experiments.jsonl 和失败 case；`Ideate` 必须引用 trace 证据做反事实诊断；`Modify` 每轮只允许一个原子改动；`Gate` 决定 keep 或 revert；`Log` 把结果写回，让下一轮有记忆。

### 内层评测：从便宜硬规则到昂贵泛化验证

`skill-evolver` 的评测分三层：

- `L1 快速门卫`：每轮都跑，纯程序检查，不需要 LLM。包括 `SKILL.md` 结构、`quick_validate`、安全规则扫描、随机抽 GT case 做基本结构检查。critical 规则不过就直接丢弃，不跑更贵的评测。
- `L2 Dev Eval`：每轮跑全量 dev 集 GT case，逐条执行 8 种 assertion。能程序判定的就程序判，需要语义理解的用 LLM 做 YES / NO 分类，结果写入 per-case JSON，供下一轮诊断。
- `L3 Strict Eval`：条件触发，例如每 N 轮、dev pass_rate 达阈值、层晋升前。它跑 holdout 集防止过拟合，跑 regression 集防止老 case 退化，也可做 blind A/B 对比。

这套设计的重点是成本分层：坏改动先在 L1 被快速挡掉，日常用 L2 给反馈，关键节点才用 L3 验证泛化和回归。

### 门控：为什么是 5 维 AND，而不是加权平均

主文强调每一轮改动都要过「5 维 AND 门控」：所有问题都必须是 YES 才保留，任何一个 NO 就 `git revert`。文章给出的理由是，加权求和可能让某个维度的高分掩盖另一个维度的退化；例如质量涨了但 token 成本翻倍，在加权机制里可能仍然通过，而 AND 不允许这种补偿。

这里的本质是把 LLM 不擅长稳定执行的控制流交给程序：LLM 负责提出局部改动和解释，程序负责强制验证、强制回滚。文章后文也总结，LLM 会偷懒、过拟合和自作主张，所以「规矩写进代码」比写更长 prompt 更可靠。

### 诊断：trace 不是摘要，而是「去现场看」

`skill-evolver` 不只给优化器一个总分，而是把每个 case 的完整执行记录落盘。下一轮 proposer 会得到失败 case 和 trace 文件路径，自己去读证据。文章特别强调，不是把 10M token trace 全塞进 prompt，而是给一张「地图」。提出改动前必须先看 trace、再诊断、再修改；没有 trace 证据就不许动手。

这解释了它为什么能做「自我迭代」：不是靠模糊的分数驱动，而是用具体失败路径驱动。比如某 case 把离职问题路由到邮箱分类，但正确答案在通讯录，下一轮就可以有针对性地修改索引提示或路由规则。

### 分层 mutation：控制每轮改动的风险和成本

主文把 mutation 分成 3 层：先改便宜的触发关键词，再改中等成本的 `SKILL.md` 正文，最后才改辅助脚本和 references。它要求不准跨层，每轮只改一层。这个规则让迭代更像受控实验：每轮变量少，出现回归时更容易定位原因，也能避免一轮里改太多导致不可解释。

### 自证和业务验证

主文给出两类验证结果：

- `meta-evolution`：让 `Skill Evolver` 自己优化自己，跑了 19 轮，0 次崩溃，0 轮被丢弃，测试用例从 17 扩到 31，最终 31 个用例共 71 个检查点全绿，主文件从 1411 行缩到 557 行并拆成 13 个单一职责文件。证据见主文 `:238-244`、`:248-272`。
- 真实业务 skill：在客服问答路径召回场景中，目标是把候选路径从约 10 个压到约 6 个，同时不降低召回。压缩后召回先掉到 86%，交给 `skill-evolver` 后修掉 9 个 miss，S1 路径召回到 98.67%，标准题 100%，难题 97.3%，Stage 2 压力降低 59%。证据见主文 `:280-286`。

这些数字来自文章作者的实验记录；本轮研究只确认资料库文本中的表述，未独立复现实验。

### 相邻资料如何帮助理解，但不能替代主证据

`《Harness Engineering：长程自动化 AI Coding / Skills 开发实践》` 的 `Skills 开发 Harness 实践` 部分与 `skill-evolver` 很接近：它也要求多 Agent 协作、效果基准、Rubric 评测、设定阈值和迭代轮次，并通过 `skill-eval-setup.md` 编排主 Agent、执行 Agent、评估 Agent，避免执行者知道评测标准造成分数虚高。证据见 `alitech/Harness_Engineering_长程自动化_AI_Coding___Skills_开发实践.md:406-453`。但它的核心对象是一个 `Skill` 开发平台 / Harness，不是 `skill-evolver`。

`《Agent skill 迭代式编写实战》` 更偏实战手册：建议用 `skill-creator` 生成、`skill-judge` 评估，并把外部 eval 拆成测试用例、断言、评估-修改-重跑循环、description 触发率优化。证据见 `taobaotech/Agent_skill_迭代式编写实战.md:82-83`、`:148-157`。它能解释 `skill-evolver` 所继承的评测文化，但没有讲 `skill-evolver`。

`《如何更科学、方向可控的实现 Skill 的“自进化”?》` 则是理论综述，覆盖 Trace2Skill、EvoSkill、SkillOpt。它指出单条轨迹容易把 `Skill` 带偏，因此需要离线收集、人工审核 / 评测验证、灰度上线或更可控的自进化机制；还强调验证集得分相当于进化方向的奖励信号。它和 `skill-evolver` 的「验证、门控、反过拟合」同向，但文章核心不是 `skill-evolver`。

## 单篇文章摘要

### 《让Skill自己训练自己：8阶段Loop、3层评测、5维AND门控，从此实现自进化》

- 路径：`E:/work/gongzhonghao_md/tengxunyun/让Skill自己训练自己_8阶段Loop_3层评测_5维AND门控_从此实现自进化.md`
- 相关性：相关
- 核心观点：`Skill` 不该只是手工打磨的 prompt，而应作为可训练、可回滚、可选优的对象。`skill-evolver` 把 `AutoResearch` 外循环、`skill-creator` 评测引擎和 `Meta-Harness` trace 诊断结合起来，让 `Skill` 自己迭代、评测、回归并选出最佳 checkpoint。
- 关键证据：
  - 文章明确命名 `skill-evolver`，并给出公式式定义：`AutoResearch` loop 骨架 + Creator 评测引擎 + `Meta-Harness` 诊断大脑。位置：`:114-116`。
  - 用 GT 定义标准答案，用 8 种 assertion 检查结果，用 holdout split 防止 dev 过拟合，用分层 mutation 控制改动粒度。位置：`:134-142`。
  - 8 阶段 Loop 包含 setup、review、ideate、modify、commit、verify、gate、log、loop；`Phase 0` 会生成 `evolve_plan.md`，决定评测策略、门控阈值和起始 mutation 层。位置：`:148-158`。
  - `Phase 1` 读 git log、results.tsv、experiments.jsonl 和失败 case，提取成功改法、失败改法、持续失败 case、脆弱 case 和卡住信号。位置：`:160-168`。
  - `Phase 2` 要先基于 trace 做反事实诊断，`Phase 3` 每轮只允许一个原子改动，`Phase 8` 决定继续、升层或终止。位置：`:170-174`。
  - 三层评测：L1 结构 / 安全快速门卫，L2 dev GT 全量评测，L3 holdout / regression / blind A/B 严格评测。位置：`:178-203`。
  - 5 维 AND 门控要求所有问题均为 YES，否则 `git revert`；避免加权求和掩盖退化。位置：`:207-211`。
  - trace 诊断把每个 case 的完整执行记录落盘，下一轮 proposer 先看 trace 再诊断再改，禁止无证据修改。位置：`:219-221`。
  - 自证实验：19 轮、0 崩溃、0 被丢弃、17→31 个用例、71/71 检查点全绿、主文件 1411→557 行。位置：`:238-244`。
  - 业务实验：客服问答 skill 压缩候选路径后，召回从 86% 拉到 98.67%，候选数约 10 降到约 6，Stage 2 压力降 59%。位置：`:280-286`。
  - 局限：LLM 评测有噪声，同一状态跑 4 次可在 0.79~0.92 漂移；GT 质量决定天花板；自动迭代成本高，前 3-5 轮最好人工观察方向。位置：`:294-300`。

### 《Harness Engineering：长程自动化 AI Coding / Skills 开发实践》

- 路径：`E:/work/gongzhonghao_md/alitech/Harness_Engineering_长程自动化_AI_Coding___Skills_开发实践.md`
- 相关性：部分相关
- 核心观点：该文把 Harness Engineering 定义为能持续感知、反馈、优化的自主演进环境；在 `Skills` 开发中，它通过多 Agent 协作、效果基准、Rubric 和平台化任务来驱动 `Skill` 多轮评测改进。
- 关键证据：
  - `Skill` 开发 Harness 是对根据 `Skill Prd` 生成的 `Skill` 做评测改进循环，直到达到目标或循环轮次。位置：`:406-407`。
  - 核心要素包括多 Agent 协作、效果基准 / 迭代轮次强制要求、Rubric 科学化评测。位置：`:410-421`。
  - 平台流程包括发布任务、Agent 认领执行、查看评测报告和改进过程、检查版本差异并下载最终 skill 包。位置：`:422-427`。
  - `skill-eval-setup.md` 编排主 Agent、执行 Agent、评估 Agent；执行者看不到评测标准，以避免自出题、自执行、自判卷导致分数虚高。位置：`:445-453`。
  - 未达标时根据结构化建议优化 `SKILL.md` 并进入下一轮，直到超过阈值或达到最大轮次。位置：`:453-459`。
- 主题校验：没有出现 `skill-evolver`，核心对象是更泛化的 `Skill` 开发 Harness / 平台。因此只作为相邻背景。

### 《Agent skill 迭代式编写实战》

- 路径：`E:/work/gongzhonghao_md/taobaotech/Agent_skill_迭代式编写实战.md`
- 相关性：部分相关
- 核心观点：该文将 `Skill` 定义为模块化领域知识资产，强调渐进式披露、决策树、负向约束替代方案、自查和外部 eval；它讨论的是人工 / 半自动迭代开发经验，不是 `skill-evolver`。
- 关键证据：
  - 推荐 `skill-creator` 用于生成 `Skill`，`skill-judge` 用于评估 `Skill`。位置：`:82-83`。
  - 外部验证 eval 机制包括测试用例、断言、评估→修改→重跑→再评估循环、description 触发率优化。位置：`:148-157`。
  - 文章提醒每轮只看少数用例容易把 `Skill` 改成只对这些 case 有效，因此要从反馈中抽取通用规律，而不是针对测试用例修补。位置：`:156`。
- 主题校验：核心对象是 `Agent Skill` 编写实践，不是 `skill-evolver`；可用于解释 `skill-evolver` 所处的评测驱动开发背景。

### 《如何更科学、方向可控的实现 Skill 的“自进化”?》

- 路径：`E:/work/gongzhonghao_md/aliyun/如何更科学_方向可控的实现_Skill_的_自进化__.md`
- 相关性：部分相关
- 核心观点：该文从企业级 `Skill` 自进化风险出发，综述 Trace2Skill、EvoSkill、SkillOpt 三类方法。它强调单条轨迹驱动的在线更新容易过拟合或跑偏，验证机制是让进化方向可控的关键。
- 关键证据：
  - 文中指出大多数 `Skill` 自我沉淀基于单轮 Agent 轨迹，极端 case 可能带偏进化方向。位置：`:32-43`。
  - Trace2Skill 通过并行分析大量轨迹、分层整合经验，归纳出更泛化的 `Skill`。位置：`:56-70`。
  - EvoSkill 引入执行者、提案者、搭建者三个角色，并在验证集上比较新旧版本。位置：`:148-176`。
  - SkillOpt 把 `Skill` 看成外部可训练文本参数，引入验证 gate、rejected-edit buffer、学习率约束和元学习。位置：`:212-300`。
- 主题校验：文章未讨论 `skill-evolver`，核心对象是三篇论文 / 三类方案；仅作为同类方法论背景。

## 排除或低相关资料

| 文章名 | 原因 |
| --- | --- |
| 《SkillClaw × Nacos：从一次 Agent 会话到可治理 Skill Registry 的自动演化闭环》 | 关键词命中 `Evolver`、`Skill`，但核心对象是 SkillClaw、Nacos Skill Registry 和会话到 Registry 的治理闭环，不是 `skill-evolver`。 |
| 《AI Agent & Skill 测评方案及落地实践》 | 命中 `Skill`、`测评`、`Rubric`、`Ground Truth`，但核心对象是通用 AI Agent / Skill 测评框架，不是 `skill-evolver` 的自迭代机制。 |
| 《谁是 Agent 最强守门员？首个 Agent 技能安全评测基准 SkillTrustBench 正式发布》 | 命中 `Skill` 和 `评测`，但主题是 Agent 技能安全评测基准 SkillTrustBench，不是 Skill 自我迭代。 |
| 《Agent Skill规范、构建与设计模式》 | 命中 `skill-creator`、`Skill`、`评测`，但主题是 `Agent Skill` 规范和构建模式，不是 `skill-evolver`。 |
| 《Skill Factory：三天手搓面向Harness设计的技能工厂（附AI coding实践）》 | 命中 `SkillFactory`、`skill-creator`、`Trace2Skill`，但主题是技能工厂 / 生成流程，不是 `skill-evolver`。 |
| 《如何写好 Skill：一份终极实战经验手册》 | 命中 `Skill`、`skill-creator`、迭代相关词，但主题是写好 `Skill` 的通用经验，不是 `skill-evolver`。 |
| 《让AI变成Super员工的秘密：高效训练Skills》 | 命中 `训练 Skills`，但主题是高效训练 / 使用 `Skills` 的经验，不是 `skill-evolver` 机制。 |
| 《深度解析 Hermes Agent 如何实现“自进化”及其 Prompt / Context / Harness 的设计实践》 | 命中 `自进化`、`Skill`，但核心对象是 Hermes Agent，不是 `skill-evolver`。 |
| 《Loop Engineering 概念解析、思考与实践》 | 命中 `Loop`、`Skill 自进化`、`EvoSkill`、`SkillOpt`，但主题是 Loop Engineering 概念，不是 `skill-evolver`。 |
| 《OpenClaw构建自我迭代AI助手笔记》 | 命中 `自我迭代`，但核心对象是 OpenClaw / AI 助手实践，不是 `skill-evolver`。 |
| 其余低命中候选（43 篇） | 多为只命中 1 次 `Rubric`、`Ground Truth`、`Skill`、`自进化`、`Agent` 等泛词，主题分别是通用 Agent、知识库、RAG、运维、模型发布、Benchmarks 或产品实践；经主题校验，不以 `skill-evolver` 为核心对象。 |

## 不确定性

- 本报告只基于 `E:/work/gongzhonghao_md` 下 412 个 `.md` 文件的本轮检索与阅读；不承诺资料库外没有更多 `skill-evolver` 资料。
- 候选资料数 57 是基于本轮检索词集合得到的高召回集合；若文章完全不用 `skill-evolver`、`Skill 自进化`、`评测`、`Loop`、`GT`、`Rubric` 等词，可能未被召回。
- 只有 4 篇进入全文阅读集合，其余低相关候选主要依据标题、命中词和主题片段做排除；若需要对 57 篇全部逐篇全文排除，可另开更长读文流程。
- 主文中的实验数字来自文章作者记录；本轮没有运行 `skill-evolver` 工具，也没有独立复现实验。
- 相邻资料能解释同类机制，但不能替代主文对 `skill-evolver` 的直接证据；本报告已将它们标为「部分相关」。
