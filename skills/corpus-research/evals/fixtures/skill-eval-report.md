# corpus-research 报告：Skill 评测有哪些方法 / 框架？

> 本文件双重用途：(1) behavior_gt.json 的测试夹具，验证 check_recall.py 有鉴别力；
> (2) corpus-research 对该问题的一次真实标准化输出。内容基于实读全文，非编造。
> 真正回归时，把本文件替换为 skill 当次运行产出的报告即可。

## 结论

公众号语料中关于 Skill / Harness 评测的方法可归为五套框架：Rubric 评测、Skill-Evolver 自进化、Harness Eval 考试系统、双层验证、SkillTrustBench 安全评测。核心共识：评测的「好」是光谱不是 boolean，需多维打分 + 证据 + 归因；制作者与检查者必须分离。

## 覆盖范围

- 资料库：E:/work/gongzhonghao_md
- 是否递归：是
- 扫描文件数：约 200+（alitech / taobaotech / tengxuntech / tengxunyun）
- 候选资料数：13
- 全文阅读上限：20
- 完整阅读资料数：9
- 检索词：skill 评测、Rubric、eval、SkillTrustBench、Harness、自进化、AND 门控、skill-judge、三角色

## 相关文章

| 文章名 | 路径 | 相关性 | 关键内容 |
| --- | --- | --- | --- |
| AI Agent & Skill 测评方案及落地实践 | tengxuntech/ | 相关 | 三类评委（确定性/Rubric/人工）+ 五维度，资料库最系统 |
| Harness Engineering：长程自动化 AI Coding / Skills 开发实践 | alitech/ | 相关 | Rubric 四层评测（L1-L4），Rubrics as Rewards 论文 |
| 让 Skill 自己训练自己：8 阶段 Loop、3 层评测、5 维 AND 门控 | tengxunyun/ | 相关 | skill-evolver 自进化框架 |
| 你的 Harness 工作流真的在进步吗（撕掉了遮羞布） | tengxuntech/ | 相关 | Harness Eval，出题/答题/改卷，三角色分离 |
| 谁是 Agent 最强守门员：SkillTrustBench 正式发布 | tengxuntech/ | 相关 | Skill 安全评测基准，T01-T09 |
| Agent skill 迭代式编写实战 | taobaotech/ | 相关 | 双层验证：内部自查 + 外部 eval |
| QoderWork Skills 开发实践 | taobaotech/ | 相关 | 四层结构，测试驱动开发占 70-80% |
| 面向 Skills 编程——淘宝企业购端对端研发提效实践 | taobaotech/ | 相关 | 质量瓶颈在知识工程，40%→90% |

## 综合总结

- **Rubric 评测**（长程自动化那篇）：把「好」拆成可独立评判的检查清单，条目分 Essential / Important / Optional / Pitfall，e2e 测试分 L1 功能正确性(40%) / L2 健壮性(25%) / L3 UI(20%) / L4 交互(15%)。
- **Skill-Evolver**（自己训练自己那篇）：8 阶段 Loop + 三层评测 + 5 维 AND 门控（不是加权求和）+ trace 诊断（Meta-Harness：只给分数比给完整 trace 差 44%）。
- **Harness Eval**（撕掉了遮羞布那篇）：考试隐喻，考官 / 考生 / 裁判三角色分离，判卷要上帝视角、看 tool call 真正做了什么；改进建议强制归因 workflow / eval / capability。
- **双层验证**（迭代式编写那篇）：内部自查（运行时护栏）+ 外部 eval（有无 skill 对比）。
- **SkillTrustBench**（守门员那篇）：安全维度，5520 用例，高召回 ≠ 可落地。
- **三类评委组合**（AI Agent & Skill 测评方案那篇，资料库最系统）：确定性评分器 + Rubric/LLM-as-Judge + 人工校准，优先级确定性 > Rubric > 人工；五维度 + pass@k/pass^k。

## 单篇文章摘要

### 《让 Skill 自己训练自己》
- 相关性：相关
- 核心观点：把 Skill 当神经网络参数训练，自己迭代、评测、回滚、选优。
- 关键证据：5 维 AND 门控；19 轮全 keep、主文件降 60%。

### 《你的 Harness 工作流真的在进步吗》
- 相关性：相关
- 核心观点：用「考试」而非「测试」评估 Harness 工作流。
- 关键证据：三角色分离；通过率 82.4%→100%。

## 排除或低相关资料

| 文章名 | 原因 |
| --- | --- |
| 给氛围编程系上安全带：阿里集团 AI 代码评审实践与 Benchmark 开源（AACR-Bench） | 关键词重叠但主题不同：测的是代码评审质量，不是 Skill 评测 |
| ROCK&ROLL：阿里双框架协同推动 Agentic RL 规模化应用 | RL 训练 / 环境沙箱框架，与 Skill 评测无关 |

## 不确定性

- 语料以 2026 年文章为主，方法仍在快速演进。
- 部分平台（阿里内部 Skill 评测平台）只有截图，无法核实细节。
