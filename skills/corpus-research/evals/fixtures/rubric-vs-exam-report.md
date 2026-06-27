## 结论

Rubric 评测和考试式（Harness Eval）评测不是互斥的两类东西，而是「评分方法」和「评测系统形态」的区别：

- **Rubric 评测**：核心是把「好不好」拆成可执行、可举证的评分量表或检查清单，常用于开放式、主观性强、不能简单精确匹配的输出。它回答的是「这次输出按哪些标准给多少分」。证据见《AI Agent & Skill 测评方案及落地实践》对 Rubric 的定义：用结构化提示词让大模型充当评委打分（`E:/work/gongzhonghao_md/tengxuntech/AI_Agent___Skill_测评方案及落地实践.md:192-196`），以及 Rubric 规则示例把观察点、过程分、结果分和虚假成功标记写入结构化规则（同文 `:133-153`）。
- **考试式（Harness Eval）评测**：核心是把 Harness 工作流放进一套可回归的「考试系统」里，有题库、题面、阅卷标准、考场环境、考官多轮交互、考生执行、完整录像、独立裁判、批量成绩单和改进闭环。它回答的是「这个 Harness 工作流在一组标准化任务上是否稳定进步」。证据见《你的 Harness 工作流真的在进步吗？我们用一场考试撕掉了遮羞布》明确把系统概括为「出题、答题、改卷」闭环（`E:/work/gongzhonghao_md/tengxuntech/你的_Harness_工作流真的在进步吗_我们用一场考试撕掉了遮羞布.md:83-92`）。

最关键的关系是：**Rubric 可以是 Harness Eval 的阅卷标准之一，但 Harness Eval 不只是 Rubric**。Harness Eval 还包含题库组织、环境布置、交互模拟、执行隔离、trace 记录、独立判卷、批量统计和回归改进。

## 覆盖范围

- 资料库：`E:/work/gongzhonghao_md`
- 是否递归：是
- 纳入文件类型：`.md`
- 扫描文件数：412
- 搜索命中资料数：273（包含宽泛命中，如「评测」「Harness」「Eval」「考试」「标准答案」等）
- 候选资料数：17（经标题、正文命中和主题校验后形成）
- 全文阅读上限：15
- 完整阅读资料数：9
- 检索词：`Rubric`、`rubric`、`评分标准`、`评测标准`、`打分标准`、`Harness Eval`、`Harness`、`harness`、`考试`、`考试式`、`标准答案`、`参考答案`、`评测`、`评估`、`Eval`、`evaluation`、`benchmark`、`LLM-as-a-Judge`、`judge`、`裁判`、`打分`、`判题`、`单元测试`、`测试用例`、`通过率`、`pass`、`fail`、`golden`、`answer key`、`Binary Eval`
- 主题校验口径：关键词重叠不等于相关。只有文章核心对象是 Agent / Skill / Harness / Benchmark 评测，且能直接解释 Rubric、考试式评测、Harness Eval、GT / 标准答案、trace、judge、回归闭环之一，才纳入相关或部分相关。

## 相关文章

| 文章名 | 路径 | 相关性 | 关键内容 |
| --- | --- | --- | --- |
| 《你的 Harness 工作流真的在进步吗？我们用一场考试撕掉了遮羞布》 | `E:/work/gongzhonghao_md/tengxuntech/你的_Harness_工作流真的在进步吗_我们用一场考试撕掉了遮羞布.md` | 相关 | 直接定义 Harness Eval；提出「测试」到「考试」跃迁；题库由 `meta.yaml`、`task.md`、`rubric.md`、`env.yaml` 组成；独立 Judge 按 rubric 和 transcript 判卷。 |
| 《AI Agent & Skill 测评方案及落地实践》 | `E:/work/gongzhonghao_md/tengxuntech/AI_Agent___Skill_测评方案及落地实践.md` | 相关 | 系统区分确定性评分器、Rubric 评分器、人工评分器；说明 Rubric 负责代码难以判定但可结构化描述的开放式输出；基线可作为 Reference Answer。 |
| 《Harness Engineering：长程自动化 AI Coding / Skills 开发实践》 | `E:/work/gongzhonghao_md/alitech/Harness_Engineering_长程自动化_AI_Coding___Skills_开发实践.md` | 相关 | 从 Harness Engineering 角度解释 evaluator、Rubric 原则、E2E Rubric 四层、Skill 开发 Harness 中执行者与评估者隔离。 |
| 《基于顶级 Agent（Claude Code）的 Harness 工程搭建式业务 Agent 评测方案》 | `E:/work/gongzhonghao_md/aliyun/基于顶级_Agent（Claude_Code）的_Harness_工程搭建式业务_Agent_评测方案.md` | 相关 | 讲 Harness 式评测如何把传统测试工程改成评测方案、评测集、GT、评测 Agent 提示词和报告；说明 LLM-as-Judge 的 1-5 分 rubric。 |
| 《Harness Engineering 实践，做了一个平台让 AI 一晚上自动评测和优化你的系统》 | `E:/work/gongzhonghao_md/aliyun/Harness_Engineering实践_做了一个平台让AI一晚上自动评测和优化你的系统.md` | 部分相关 | 明确区分「标准」评测集和 `rubrics` 评测集：前者有明确成功 / 失败，后者用于内容质量等不能直接二值判定的场景。 |
| 《如何定义“人味儿”？——HeartBench 评测体系建设实践》 | `E:/work/gongzhonghao_md/aliyun/如何定义_人味儿____HeartBench评测体系建设实践.md` | 部分相关 | 从 Benchmark 构建角度说明开放式问题没有单一标准答案时要用 Rubrics，并通过专家盲测校准 LLM-as-a-Judge。 |
| 《让 AI 自己做增长：基于 OPC 和 Harness 思想的自主增长系统探索》 | `E:/work/gongzhonghao_md/aliyun/让_AI_自己做增长_基于OPC和Harness思想的自主增长系统探索.md` | 部分相关 | 讨论 Harness 中 evaluator 独立性、元评估、Benchmark、Golden Answer、静态 / 动态验证和评分体系。 |
| 《让 Skill 自己训练自己：8 阶段 Loop、3 层评测、5 维 AND 门控，从此实现自进化》 | `E:/work/gongzhonghao_md/tengxunyun/让Skill自己训练自己_8阶段Loop_3层评测_5维AND门控_从此实现自进化.md` | 部分相关 | 说明 Skill 评测既不是纯单元测试，也不是纯数字 Benchmark；使用 GT、assertion、holdout、三层评测和 trace 诊断。 |
| 《重新定义 Skill 开发：保姆级教程 & 一站式开发助手发布》 | `E:/work/gongzhonghao_md/aliyun/重新定义Skill开发_保姆级教程_一站式开发助手发布.md` | 部分相关 | 说明 Skill 发布应有回归 eval 门禁，并提到 Binary Eval / Self-Improving Loop 用二元评估器替代主观打分。 |

## 综合总结

### 1. Rubric 评测的本质：把「好不好」写成可判定标准

Rubric 评测解决的是「开放式输出如何评分」的问题。资料中反复出现的共识是：当任务无法用简单断言判断，或者输出质量有程度差异时，需要把标准拆成细项。

《AI Agent & Skill 测评方案及落地实践》把评委分成三类：确定性评分器、Rubric 评分器和人工评分器。确定性评分器负责文件存在、测试通过、工具调用等「能用代码判断」的事；Rubric 评分器负责回答质量、语气、规范遵循度等「代码搞不定但能结构化描述」的事；人工评分器用于校准、诊断异常和高风险兜底（`E:/work/gongzhonghao_md/tengxuntech/AI_Agent___Skill_测评方案及落地实践.md:57-99`）。这说明 Rubric 的定位不是替代所有检查，而是补足确定性检查覆盖不到的语义质量判断。

《Harness Engineering：长程自动化 AI Coding / Skills 开发实践》进一步把 Rubric 设计原则具体化：Rubric 要基于专家知识、全面覆盖、区分 Essential / Important / Optional / Pitfall 权重，并且自包含可评判（`E:/work/gongzhonghao_md/alitech/Harness_Engineering_长程自动化_AI_Coding___Skills_开发实践.md:210-232`）。这与考试式评测里的 `rubric.md` 角色相呼应：Rubric 是「阅卷标准」，但不是完整的考试系统。

### 2. 考试式（Harness Eval）的本质：用标准化题目模拟真实工作流并回归

《你的 Harness 工作流真的在进步吗？我们用一场考试撕掉了遮羞布》是最直接的证据。它明确指出传统单元测试验证「对不对」，而 Harness 工作流的「正确」不是 boolean，而是光谱；因此需要「考试」来评估「好不好」，形式是多维度打分、证据和改进建议（`E:/work/gongzhonghao_md/tengxuntech/你的_Harness_工作流真的在进步吗_我们用一场考试撕掉了遮羞布.md:61-72`）。

这套考试式评测至少多出七个 Rubric 本身没有的系统能力：

1. **题库结构**：一道题由题面、阅卷标准、环境前提和元信息组成，落实为 `meta.yaml`、`task.md`、`rubric.md`、`env.yaml`（同文 `:95-106`）。
2. **题面和阅卷分离**：考生只能看到 `task.md`，看不到 `rubric.md`，避免对着标准答案抄（同文 `:112-115`）。
3. **多轮交互模拟**：引入 Examiner 扮演用户，按剧本和被测 Agent 多轮互动，测真实场景下的表现而不是 Agent 自嗨（同文 `:138-166`）。
4. **全过程录像**：完整记录对话文本、tool call、shell 命令和结果，判卷不只看最终答案，还看过程质量（同文 `:165-177`）。
5. **独立判卷**：Judge 与答题对话隔离，只拿 `rubric.md` 和 `transcript.for-judge.txt`，避免考官顺手打分造成视角偏差（同文 `:179-204`）。
6. **结构化成绩单**：输出 pass / fail、流程遵循度、执行质量、综合分、证据和改进建议（同文 `:206-242`）。
7. **批量回归与版本追踪**：记录 `workflow_rev`，用 latest、history、batch-insights 看不同工作流版本的趋势（同文 `:268-279`）。

所以，考试式评测更像「有考场、有考卷、有考官、有考生、有录像、有阅卷官、有成绩档案」的系统，而 Rubric 只是其中的「评分标准 / 阅卷量表」。

### 3. 两者的核心差异表

| 维度 | Rubric 评测 | 考试式（Harness Eval）评测 |
| --- | --- | --- |
| 核心对象 | 输出质量、过程质量或某个单次 trial 的评分标准 | 整个 Harness 工作流在标准任务集上的稳定表现 |
| 主要问题 | 「这次输出好不好，按哪些维度扣分？」 | 「这版工作流相比上一版进步还是退步，坏在哪？」 |
| 输入材料 | 输出文本、报告、截图、trace 摘要、参考答案或评分说明 | 题目目录、题面、环境、被测 Agent、Examiner 对话、完整 transcript、tool call、Judge 输入 |
| 标准形态 | 评分量表、检查项、1-5 分档、Essential / Pitfall 等 | 一道题 = `meta.yaml` + `task.md` + `rubric.md` + `env.yaml`，再由执行引擎批量运行 |
| 判定方式 | LLM-as-Judge、人工或脚本按 Rubric 打分 | 独立 Judge 拿 rubric 和 transcript 逐项举证，输出 pass / fail + 多维分 + 改进建议 |
| 过程要求 | 可以只看最终输出，也可以看 trace | 必须强调过程录像、交互过程、工具调用和环境证据 |
| 回归能力 | 本身不必然包含版本回归；可嵌入回归流程 | 原生强调批量 run、历史分数、`workflow_rev` 和 batch insights |
| 适用场景 | 开放式回答、内容质量、UI 品味、解释清晰度、主观体验 | 评估 Rules / Skills / Agent 工作流变更是否稳定、可复现、可归因 |
| 最大风险 | Rubric 模糊、LLM Judge 抖动、专家一致性低 | 题目歧义、环境不稳、评测系统本身 bug、成本较高 |

### 4. 「标准答案」在两类评测里的位置不同

资料显示，标准答案 / GT 在两类评测里都可能出现，但作用不同。

在 Rubric 或 Agent 评测中，GT 可以作为 Reference Answer。《AI Agent & Skill 测评方案及落地实践》说基线是经人工确认的预期过程和预期结果，后续执行时可用基线做程序化客观判定，也可让 Rubric 评分器对比本次产出与基线的语义差异（`E:/work/gongzhonghao_md/tengxuntech/AI_Agent___Skill_测评方案及落地实践.md:405-449`）。

在考试式 Harness Eval 中，标准答案更像被封装进题目的「阅卷材料」。考生看不到 `rubric.md`，Judge 才能看到它，并结合 transcript 判卷（`E:/work/gongzhonghao_md/tengxuntech/你的_Harness_工作流真的在进步吗_我们用一场考试撕掉了遮羞布.md:197-214`）。也就是说，考试式评测更强调「考生与标准隔离」和「按完整录像举证」。

### 5. 为什么不能把 Harness Eval 简化成单元测试

多篇资料都反对把 Agent / Skill / Harness 评测简化成传统单元测试。

《你的 Harness 工作流真的在进步吗？我们用一场考试撕掉了遮羞布》说传统软件是确定性的，同样输入同样输出；但 Harness 工作流是由 Prompt、Rules、Skills、Model 共同决定的概率程序，输出有波动，且「好」本身缺乏定义（`E:/work/gongzhonghao_md/tengxuntech/你的_Harness_工作流真的在进步吗_我们用一场考试撕掉了遮羞布.md:53-59`）。

《让 Skill 自己训练自己》也说 Skill 评测既不是跑单元测试那种纯确定性的东西，也不是跑 Benchmark 那种纯数字的东西，更像语文老师批作文：带主观性，又要有一致性（`E:/work/gongzhonghao_md/tengxunyun/让Skill自己训练自己_8阶段Loop_3层评测_5维AND门控_从此实现自进化.md:92-96`）。这说明 Harness Eval 使用「考试」比喻，是因为它需要同时覆盖结果、过程、主观质量、稳定性、证据和回归。

### 6. 什么时候更像 Rubric，什么时候更像考试式 Harness Eval

- 如果你只有一个输出，例如报告、回答、UI 截图、文案，并想问「是否完整、准确、清晰、符合风格」，这更像 Rubric 评测。
- 如果你有一套 Agent / Skill / Rules 工作流，需要验证它在多个任务、多个版本、多轮交互、真实工具调用和环境变化下是否稳定，这更像考试式 Harness Eval。
- 如果考试题里有 `rubric.md`，那说明 Harness Eval **使用了 Rubric**，但不能反过来说「有 Rubric 就是 Harness Eval」。必须还要看是否有题库、执行、隔离、trace、独立判卷和回归闭环。

## 单篇文章摘要

### 《你的 Harness 工作流真的在进步吗？我们用一场考试撕掉了遮羞布》

- 路径：`E:/work/gongzhonghao_md/tengxuntech/你的_Harness_工作流真的在进步吗_我们用一场考试撕掉了遮羞布.md`
- 相关性：相关
- 核心观点：Harness 工作流不能靠「主观 vibes」判断进步，需要一套面向 Harness 工作流的轻量、可回归闭环评测系统。文章明确把传统「测试」升级为「考试」：测试验证对不对，考试评估好不好。
- 关键证据：
  - 团队无法回答 rule / skill 改动是进步还是退步、工作流回归是否被破坏等问题（`:22-41`）。
  - Harness 工作流是规则驱动的概率程序，输出波动且「好」缺乏定义（`:53-59`）。
  - 「测试」是二值判定，「考试」是多维度打分、证据、改进建议（`:61-72`）。
  - 一道题由 `meta.yaml`、`task.md`、`rubric.md`、`env.yaml` 构成；`rubric.md` 是答案与给分标准（`:95-106`）。
  - rubric 必须可量化，题面与阅卷分离，考生不能看到 rubric（`:112-115`）。
  - Examiner 模拟真实用户多轮交互，transcript 记录对话、tool call 和命令结果（`:138-166`）。
  - Judge 独立读取 `rubric.md` 和 `transcript.for-judge.txt`，按硬性标准、过程质量、多维分数、引用证据和改进建议判卷（`:197-214`）。
  - 实践中通过 4 轮 workflow 迭代、50+ 次自动化 run，把通过率从 82.4% 提升到 100%（`:281-294`）。

### 《AI Agent & Skill 测评方案及落地实践》

- 路径：`E:/work/gongzhonghao_md/tengxuntech/AI_Agent___Skill_测评方案及落地实践.md`
- 相关性：相关
- 核心观点：Agent / Skill 测评需要「确定性评分器 + Rubric 评分器 + 人工评分器」组合。Rubric 评分器负责开放式、自然语言、过程质量等难以用代码判断的场景。
- 关键证据：
  - Eval 被定义为输入、执行、捕获 Trace 与产物、一组检查规则、可对比分数的闭环（`:41-50`）。
  - 三类评委中，确定性评分器快、客观；Rubric 评分器灵活但有抖动；人工评分器昂贵但可校准（`:57-99`）。
  - Rubric 规则示例包含观察点、过程分、结果分和虚假成功标记（`:133-153`）。
  - Rubric 被定义为评分量表 / 评分标准，即用结构化评分提示词让另一个大模型充当评委打分（`:192-196`）。
  - 基线是人工确认的预期过程和预期结果，Rubric 可用基线作为 Reference Answer 做语义差异评分（`:405-449`）。
  - 稳定性评估通过 N 次运行检测非确定性，关键决策类要求 0% 失败容忍（`:582-604`）。
  - TPerf 案例用确定性评分 + 模型评分，满分 100 分扣分制；关键判定不一致直接扣 80 分（`:673-706`）。

### 《Harness Engineering：长程自动化 AI Coding / Skills 开发实践》

- 路径：`E:/work/gongzhonghao_md/alitech/Harness_Engineering_长程自动化_AI_Coding___Skills_开发实践.md`
- 相关性：相关
- 核心观点：Harness Engineering 需要上下文控制、专业 Agent 分工、评估反馈和结构化执行回路；Rubric 是让 evaluator 有明确、客观、结构化评估标准的关键。
- 关键证据：
  - Harness Engineering 目标是让 Agent 运行过程可观测、可控制、可迭代（`:20-25`）。
  - 专业化分工把 planner、developer、evaluator 分离，避免写的人给自己打分（`:120-127`）。
  - 评估反馈依赖明确目标和客观结果衡量标准，文章明确说下文会重点讲 Rubric 原则（`:150-157`）。
  - Rubric 使用专家知识、全面覆盖、分级权重和自包含可评判四原则（`:210-232`）。
  - E2E Rubric 分为功能正确性、健壮性、UI 呈现、交互体验四层，并给出权重公式（`:235-313`）。
  - Rubric 加入后，问卷系统多轮评分从 3.35 提升到 4.66，功能逻辑和 UI 交互均改善（`:315-337`）。
  - Skill 开发 Harness 要求执行者不可见评测标准，评估者基于 Rubric 独立判分并给证据（`:437-453`）。

### 《基于顶级 Agent（Claude Code）的 Harness 工程搭建式业务 Agent 评测方案》

- 路径：`E:/work/gongzhonghao_md/aliyun/基于顶级_Agent（Claude_Code）的_Harness_工程搭建式业务_Agent_评测方案.md`
- 相关性：相关
- 核心观点：Harness 式评测把传统评测脚本工程替换为由强 Agent 搭建的评测方案、数据集、评测 Agent 提示词和报告流程；Rubric 是其中 LLM-as-Judge 的评分标准。
- 关键证据：
  - 传统评测工程痛点是启动成本高、人力密集、迭代慢、可复现性差、指标不统一（`:26-37`）。
  - Harness 式做法由顶级 Agent 搭建评测方案、数据集、评测逻辑和分析流程，人只做关键决策（`:38-59`）。
  - 传统 `test_runner.py` 对应评测 Agent 提示词，`conftest.py + fixtures` 对应 GT 标注和 `ground_truth` 字段（`:71-81`）。
  - `system.question` 列包含被测 Agent 输入字段和 `ground_truth`，评测 Agent 读取即可获得输入与预期输出（`:167-179`）。
  - 评测 Agent 工作流为读取样本、调用被测 Agent、解析输出、硬规则检查、LLM 打分、输出 JSON（`:181-199`）。
  - 文本生成类 Agent 使用 1-5 分 rubric，要求每个分值有具体、可区分标准，避免模糊描述（`:262-281`）。
  - 局限包括 LLM-as-Judge 偏差、评测集规模受人工 GT 限制、平台稳定性问题（`:338-346`）。

### 《Harness Engineering 实践，做了一个平台让 AI 一晚上自动评测和优化你的系统》

- 路径：`E:/work/gongzhonghao_md/aliyun/Harness_Engineering实践_做了一个平台让AI一晚上自动评测和优化你的系统.md`
- 相关性：部分相关
- 核心观点：平台化 Harness 评测可以让 AI 创建任务、评测集、评测报告并自动优化。文章直接区分「标准」与 `rubrics` 两种评测集。
- 关键证据：
  - 平台由 AI 创建评测任务、评测集和评测报告，每个任务要求写明目标和验收标准（`:38-45`）。
  - 评测集分为「标准」和 `rubrics`：标准有明确成功 / 失败状态；`rubrics` 用于内容质量等无法直接二值判定的场景（`:48-53`）。
  - 钉钉文档 MCP 案例自动生成 13 个用例并提交 95 分报告（`:70-108`）。
  - 自动优化案例三轮评分从 90.7、97.4 到 99.1，说明评测报告可反哺系统迭代（`:146-166`）。

### 《如何定义“人味儿”？——HeartBench 评测体系建设实践》

- 路径：`E:/work/gongzhonghao_md/aliyun/如何定义_人味儿____HeartBench评测体系建设实践.md`
- 相关性：部分相关
- 核心观点：在没有单一标准答案、主观性强的开放式评测中，Rubrics 能把「好」拆成可操作标准，并通过专家盲测校准 LLM-as-a-Judge。
- 关键证据：
  - HeartBench 包含 1126 道样例、10772 条 Rubrics、33 个场景和 15 个具体能力（`:38-48`）。
  - 文章对比多项选择、开放式问题、成对比较、评分 / 排序题等评估方式，开放式问题基于 rubrics 评分（`:85-97`）。
  - 心理社科评测没有客观标准答案，因此用专家盲测验证 LLM Judge 与人类专家一致性（`:104-123`）。
  - 沉淀经验明确说传统 Benchmark 有套路，但情感智能评测没有标准答案，需多维度 rubric 而非单一标签（`:173-176`）。
  - Rubric 每个分数档位要有可观测行为和示例，避免「共情能力强」这类模糊描述（`:187-192`）。

### 《让 AI 自己做增长：基于 OPC 和 Harness 思想的自主增长系统探索》

- 路径：`E:/work/gongzhonghao_md/aliyun/让_AI_自己做增长_基于OPC和Harness思想的自主增长系统探索.md`
- 相关性：部分相关
- 核心观点：Harness 系统里 evaluator 要独立、可度量，并且可以进一步用 Benchmark 做「元评估」，评估 evaluator 评得准不准。
- 关键证据：
  - 经典 Harness Engineering 中 Evaluator 会在评分前直接操作运行页面，截图并研究效果，再给评估结论（`:38-50`）。
  - 评审与生成要彻底分离，Evaluator 只输出反馈不改代码，并对 Builder 声明保持零信任（`:168-190`）。
  - Evaluator 的评审能力可用 Benchmark 评估：评的不是代码质量，而是 Evaluator 评得准不准（`:206-220`）。
  - Benchmark 数据集包含 good / bad example、Golden Answer、bug 植入和难度分级（`:239-263`）。
  - 评分体系区分代码片段模式和完整项目模式，完整项目包含静态分析和动态验证，并用能力系数防止「纸上谈兵」拿高分（`:304-325`）。

### 《让 Skill 自己训练自己：8 阶段 Loop、3 层评测、5 维 AND 门控，从此实现自进化》

- 路径：`E:/work/gongzhonghao_md/tengxunyun/让Skill自己训练自己_8阶段Loop_3层评测_5维AND门控_从此实现自进化.md`
- 相关性：部分相关
- 核心观点：Skill 评测既不等于单元测试，也不等于纯数字 Benchmark；要用 GT、assertion、holdout、trace 和分层门控构建可回归的训练 / 评测闭环。
- 关键证据：
  - Skill 评测带主观性又要一致性，既不是纯单元测试，也不是纯数字 Benchmark（`:92-96`）。
  - GT 是标准答案，assertion 是检查方式，holdout 用于防止只在 dev 集上背答案（`:134-142`）。
  - 8 阶段 Loop 中 Verify 阶段跑三层评测，Gate 阶段用 5 维 AND 门控决定 keep / discard（`:146-158`）。
  - L1 做结构和安全检查，L2 跑 dev 集 GT case，L3 跑 holdout / regression / blind A/B（`:176-203`）。
  - LLM 评测有噪声，同一 skill 和同一 GT 多次运行结果可漂移；GT 质量决定天花板（`:292-298`）。

### 《重新定义 Skill 开发：保姆级教程 & 一站式开发助手发布》

- 路径：`E:/work/gongzhonghao_md/aliyun/重新定义Skill开发_保姆级教程_一站式开发助手发布.md`
- 相关性：部分相关
- 核心观点：Skill 应作为代码包严肃发布，使用回归 eval、Binary Eval 和自我改进闭环防止退化。
- 关键证据：
  - 发布治理中建议 CI 跑 schema、关键词扫描、prompt-lint、脚本单测，并用回归 eval 做合入门禁（`:384-389`）。
  - 自我进化闭环为执行 Skill、Binary Eval 自动打分、失败时 Reflection Agent 生成 patch、通过 eval 复测后 commit（`:424-432`）。
  - Binary Evals 用二元 pass / fail 评估器替代主观打分，failure case 自动触发改 Skill（`:434-440`）。
  - 没有 eval 兜底的自我修改会导致自我退化，必须配套 binary eval、版本快照和人工 review（`:453-459`）。

## 排除或低相关资料

| 文章名 | 原因 |
| --- | --- |
| 《如何写好 Skill：一份终极实战经验手册》 | 关键词命中「评分标准」「标准答案」「测试用例」，但核心对象是 Skill 写作教程，不是 Rubric vs Harness Eval 的评测范式对比；只在后段涉及 Skill Creator 效果评估。 |
| 《OpenClaw 与 Hermes：源码里的 AI Agent 架构知识大复盘》 | 命中 `Rubric`、`Harness`、`Eval`，但核心对象是 OpenClaw / Hermes 源码架构复盘，评测不是主线。 |
| 《「纯干货」几万字都讲不明白的 Memory 架构与思考》 | 命中 `Rubric`，但核心对象是 Memory 架构，不讨论 Rubric 评测与 Harness Eval 差异。 |
| 《高考那几天，鹅厂员工遇到过什么至今难忘的事？》 | 命中「考试」，但主题是高考故事，与技术评测 / Harness Eval 无关。 |
| 《RAG 全链路技术详解》 | 命中「标准答案」「答案」频次较高，但核心对象是 RAG，不是 Agent / Skill / Harness 评测。 |
| 《如何构建一个更“好”的知识库？》 | 命中「标准答案」「答案」，但核心对象是知识库构建，未围绕 Rubric 或 Harness Eval。 |
| 《基于浏览器请求录制与 AI 代码生成的 E2E 接口自动化测试实践》 | 命中「标准答案」，但主题是接口自动化测试，不是 Harness 工作流考试式评测。 |
| 《阿里云正式发布 RCA Benchmark，业界首个面向 Agentic Ops 的根因分析开源基准体系》 | 命中 Benchmark 和标准答案，但核心对象是 RCA 根因分析 Benchmark，无法直接解释 Rubric vs Harness Eval。 |
| 《微信测试团队斩获 CVPR 2026 NTIRE RAIM 挑战赛冠军》 | 命中 LLM Judge、评分、Evaluation，但主题是图像质量挑战赛，不是 Agent / Harness 工作流评测。 |
| 《TencentDB Agent Memory 全球正式开源：让 Agent 沉淀经验，让人专注创造》 | 命中「标准答案」，但主题是 Agent Memory，非评测范式。 |
| 《万级实时推理的商品领域 Agent 实践思考和总结》 | 命中 Harness、Evaluation、打分规则集，但核心是商品领域 Agent 工程实践，评测差异不是主线。 |
| 《从零设计生产级 Multi-Agent Harness：架构、评估、记忆、成本与 MCP 工具接入全拆解》 | 命中 Harness 和评估，但核心是 Multi-Agent Harness 架构总览，缺少 Rubric / 考试式评测对比。 |
| 《万字干货！Harness Engineering 如何工程化落地？》 | 命中 Harness、测试用例、打分，但核心是 Harness 落地方法，不聚焦 Rubric 或 Harness Eval。 |
| 《一文讲透如何构建 Harness——六大组件全解析》 | 命中 Harness，但主题是 Harness 组件科普，不是评测体系。 |
| 《拒绝“感觉有效”：用数据证明 AI Coding 的真实团队价值【天猫 AI Coding 实践系列】》 | 命中「考试」「二元」「答案」，但核心是 AI Coding 价值度量，非 Harness Eval 机制。 |

未逐条列出的宽泛命中资料：约 258 篇。主要原因是只命中「评测」「评估」「Eval」「答案」「pass」「fail」等通用词，主题分别是图像比赛、RAG、知识库、Agent 架构、产品发布、AI Coding 价值度量或非技术故事，经主题校验未进入全文阅读集合。

## 不确定性

- 本次只扫描 `E:/work/gongzhonghao_md` 下递归 `.md` 文件；没有纳入图片 OCR、网页原文、PDF、代码仓库或外部链接。
- 文章中的图片可能包含额外细节；本报告只基于 Markdown 正文中可读文字与图片替代文本。
- 当前执行严格避开了 `E:/work/my-ai-resource/skills/corpus-research/evals/behavior_gt.json` 及任何 GT / must_recall / should_not_include 答案文件；结论来自本轮对资料库的独立检索与阅读。
- 当前环境没有可调用的子 agent 工具；因此没有按 `corpus-research` 的子 agent 分工执行，而是由本轮 eval 执行者直接按只读检索、主题校验、全文阅读和报告门禁完成。
- 「候选资料数」按主题校验后的候选计数，不等同于宽泛搜索命中数；宽泛命中用于召回，主题候选用于全文阅读决策。
