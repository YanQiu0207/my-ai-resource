# Skill / Harness 评测方法：从学习到落地

> 来源：公众号文章语料库（`E:\work\gongzhonghao_md`），含 `alitech`、`taobaotech`、`tengxuntech`、`tengxunyun`、`aliyun` 等资料。
> 整理时间：2026-06-27。
> 本版目标：留下可学习、可执行、可复盘的方法；兼顾单个 Skill 评测和 Harness Engineering 工作流评测；删除时效性榜单、未核验外部平台横评和与评测主线关系弱的内容。

---

## 一、先记住一句话

**Skill / Harness 评测 = 考题 + 评分器 + Transcript / Trace + 人工确认基线 + 门控 + 回归。**

不要只问「这个 Skill 有没有用」，要把问题拆成 6 个可验证问题：

1. **该触发时是否触发**：`description` 是否召回正确需求。
2. **不该触发时是否误触发**：near-miss 负样本是否能挡住。
3. **结果是否正确**：产物、文件、命令、字段、格式是否满足要求。
4. **过程是否靠谱**：是否看了必要资料、用了正确工具、避免越权和臆测。
5. **成本是否可接受**：耗时、Token、人工介入次数是否下降。
6. **改动是否可持续**：新版是否优于旧版，且没有破坏老能力。

---

## 二、学习优先级

| 优先级 | 必学内容 | 解决什么问题 | 什么时候用 |
| --- | --- | --- | --- |
| P0 | 三类评分器 + 五维度 | 建立完整评测框架 | 所有 Skill 都要用 |
| P0 | 触发评估 + 效果评估 | 判断 Skill 是否「会被用」且「用得对」 | 写完 `description` 和核心流程后 |
| P0 | Rubric 评测 | 把模糊质量要求变成可打分清单 | 输出质量难用代码判断时 |
| P0 | Trace + 基线 + 回归 | 让评测可复现、可比较 | 准备长期维护时 |
| P1 | 考题结构 + 三角色分离 | 避免 Agent 自评偏差，模拟真实用户交互 | 评测自动化、Harness 工作流或多人协作时 |
| P1 | Skill-Evolver / 自进化 | 自动迭代 Skill | 已经有稳定评测集后 |
| P2 | SkillTrustBench 安全评测 | 发现恶意或高风险 Skill | 对外分发、企业内部分发、CI/CD 上架前审计时 |

---

## 三、最小可落地评测体系

### 3.1 建议目录

一个 Skill 至少配一套轻量评测目录：

```text
my-skill/
├── SKILL.md
├── scripts/
├── references/
└── evaluation/
    ├── trigger-cases.md      # 该触发 / 不该触发 / 边界触发
    ├── quality-cases.md      # 输入、预期输出、评分标准
    ├── rubric.md             # LLM-as-Judge 评分规则
    ├── baseline/             # 人工确认过的标准输出或 Trace
    ├── traces/               # 每次执行的工具调用、日志、产物
    └── results.tsv           # 每次评测结果，便于趋势对比
```

如果要评测 Harness Engineering 工作流，建议升级为「考试题」结构。每道题是一个独立目录，既能评测单个 Skill，也能评测多轮工作流：

```text
exams/
└── confirm-before-dangerous-change/
    ├── meta.yaml              # id、版本、类别、难度、考察目的
    ├── task.md                # 给考生看的题面 + 给 Examiner 的多轮剧本
    ├── rubric.md              # Judge 专用阅卷标准，考生不可见
    ├── env.yaml               # 前置条件、工作目录、必需文件、检查命令
    └── fixtures/              # 可选，测试所需样例文件
```

这个结构来自 Harness Eval 的「出题 → 答题 → 改卷」模型。它比普通 cases 更适合长期做 Harness Engineering，因为它把题面、环境、评分标准和元信息分开，后续可以按难度、能力点、回归批次扩展题库。

### 3.2 6 步落地流程

1. **写清 Skill 契约**
   - 触发条件：什么请求应该触发。
   - 非触发条件：哪些相似请求不应该触发。
   - 输入 / 输出：最终应该产出什么。
   - 边界：不能做什么，遇到不确定时如何处理。

2. **做用例集**
   - 初版先做 2～3 个真实提示词。
   - 稳定后扩展到 12～20 个结构化用例。
   - 用例至少覆盖 4 类：触发、核心逻辑、产物质量、异常容错。
   - 每类都要有正例和负例；尤其要有 near-miss 负样本，防止「什么都触发」。

3. **选择评分器**
   - 能用程序判断的，优先写脚本 / 断言 / schema / lint。
   - 代码判断不了但能说清标准的，用 Rubric + LLM-as-Judge。
   - 高价值、低频、争议样本，用人工评审校准。

4. **跑对比实验**
   - 同一用例分别跑「无 Skill / 旧 Skill / 新 Skill」。
   - 执行 Agent 不看 rubric，评估 Agent 只看任务、产物和 Trace。
   - 主观评估尽量盲评，减少「知道哪个版本用了 Skill」带来的偏差。

5. **建立基线**
   - 先跑一遍，再由人工确认过程和结果。
   - 确认后的产物、Trace、评分作为 baseline。
   - 以后每次改 Skill，都和 baseline 或上一个稳定版本比。

6. **进门控和回归**
   - 新能力先进 dev / capability eval。
   - 稳定后毕业到 regression eval。
   - 任何改动必须证明「新能力提升」且「旧能力不退化」。

---

## 四、评什么：五维度

| 维度 | 核心问题 | 推荐评分器 | 示例检查项 |
| --- | --- | --- | --- |
| 功能正确性 | 做对了吗 | 确定性评分器 | 文件是否生成、字段是否齐全、命令是否成功、测试是否通过 |
| 过程质量 | 过程合理吗 | Rubric + 人工 | 是否读取必要资料、是否遵守流程、是否引用证据 |
| 效率与成本 | 划算吗 | 确定性评分器 | Token、耗时、工具调用次数、人工介入次数 |
| 鲁棒性与安全 | 靠谱吗 | 确定性 + 人工 | 异常输入、权限边界、危险命令、硬编码密钥 |
| 体验与对齐 | 好用吗 | Rubric + 人工 | 输出结构、可读性、是否符合用户偏好 |

评分器优先级：**确定性评分器 > Rubric 评分器 > 人工评分器**。

人工不是用来替代自动化的。人工最有价值的工作是：

- 校准 LLM 评委。
- 诊断 0% / 100% 这类异常分数。
- 处理争议样本和高风险场景。

---

## 五、怎么评：三类核心评测

### 5.1 触发评估

目标：验证 `description` 是否能让 Skill 在正确场景被调用。

用例类型：

| 类型 | 作用 | 示例 |
| --- | --- | --- |
| should-trigger | 测召回 | 「把这个 PDF 转成 Markdown」应触发 `pdf2md` |
| should-not-trigger | 测误报 | 「总结 PDF 内容」不应触发忠实转换类 Skill |
| boundary | 测边界 | 「提取 PDF 表格并保留格式」可能需要确认或触发更专门 Skill |

参考指标：

- 触发准确率：目标 > 90%。
- 误触发率：目标 < 5%。
- 边界样本：允许「询问澄清」，不要强行触发。

这些阈值是经验参考，不是所有 Skill 的硬标准。高风险 Skill 应更严格，低风险个人 Skill 可先轻量执行。

### 5.2 效果评估

目标：验证 Skill 触发后是否真的改善结果。

每个 quality case 至少写清：

```text
- 输入：用户原始请求
- 环境：相关文件、目录、权限、依赖
- 预期产物：应该生成或修改什么
- 硬性断言：可用脚本检查的条件
- Rubric：需要 LLM / 人工判断的质量标准
- 失败归因：workflow / eval / capability
```

推荐输出指标：

- 通过率。
- 逐用例得分。
- 与无 Skill / 旧版 Skill 的差异。
- Token 与耗时变化。
- 失败原因分类。

### 5.3 安全评估

目标：验证 Skill 不会把 Agent 变成供应链攻击入口。

重点检查：

- 是否硬编码凭证。
- 是否诱导外联、下载、上传敏感数据。
- 是否请求过宽权限。
- 是否包含危险命令，例如递归删除、静默改权限、绕过审计。
- 是否缺少输入校验。
- 是否把 prompt injection 或恶意文本当成可信指令。

使用范围：

- 个人本地低风险 Skill：做轻量安全清单即可。
- 团队共享、对外分发、带脚本执行、读写敏感文件的 Skill：必须纳入 CI/CD 或发布前审计。

---

## 六、Rubric 怎么写

Rubric 的价值是把「好不好」拆成可独立判定的检查项。

### 6.1 好 Rubric 的 4 条原则

1. **基于专家知识**：来自真实需求和领域标准。
2. **覆盖正反两面**：既有应该满足的标准，也有必须规避的 Pitfall。
3. **有权重分级**：区分 Essential、Important、Optional、Pitfall。
4. **自包含**：评委不需要猜上下文，每条都能单独判断。

### 6.2 推荐模板

```markdown
## Rubric

### Essential（必须满足）
- [ ] 输出包含 A、B、C 三类信息。
- [ ] 每个结论都有来源路径或行号。
- [ ] 没有修改用户未要求修改的文件。

### Important（重要）
- [ ] 先给结论，再给证据。
- [ ] 区分确定事实、推断和不确定性。

### Optional（加分）
- [ ] 给出可复用模板或下一步建议。

### Pitfall（严重扣分）
- [ ] 编造来源或行号。
- [ ] 跳过用户要求的验证步骤。
- [ ] 把搜索片段当成阅读全文证据。
```

### 6.3 常见坏 Rubric

- 「质量高」「结构清晰」「表达自然」：太空，无法驱动改进。
- 「尽量完整」：没有边界，不知道少什么算失败。
- 「用户满意」：没有可观察证据。
- 只写正向标准，不写 Pitfall：容易高分掩盖严重错误。

---

## 七、考试式评测与三角色分离

不要让同一个 Agent 同时当「考生」和「考官」。如果只是评测单个 Skill，可以用三角色；如果要评测 Harness 工作流，建议加入 Examiner，模拟真实用户多轮交互。

| 角色 | 看什么 | 不看什么 | 职责 |
| --- | --- | --- | --- |
| 主控 Agent | 全局目标、题库、结果 | 不直接给自己打高分 | 调度、汇总、决定是否合入 |
| Examiner | `task.md` 里的用户剧本 | `rubric.md`、标准答案 | 扮演用户，按剧本追问、纠偏、补充信息 |
| Candidate / 执行 Agent | 用户任务、必要资料 | Rubric、标准答案 | 像真实使用一样执行 Skill 或 Harness 工作流 |
| Judge | 任务、产物、Transcript、Trace、Rubric | Candidate 的自我解释优先级最低 | 独立判分、举证、归因 |

关键原则：

- Examiner 负责模拟真实交互，不负责判分。
- Judge 要有「上帝视角」：能看产物、日志、tool call、Transcript 和 Trace。
- 不要把原始超长 Transcript 直接塞给 Judge；先生成 `transcript.for-judge.txt`，保留关键行为证据，去掉噪声。
- 每个扣分项必须带证据。
- 改进建议必须归因到 `workflow`、`eval` 或 `capability`，否则很难知道下一轮该改什么。

推荐输出双轨制：

```text
score.yaml      # pass/fail、compliance、execution_quality、overall、summary
review.md       # 证据、扣分原因、workflow / eval / capability 改进建议
```

---

## 八、Trace、基线与回归

### 8.1 为什么 Trace 是前提

没有结构化 Trace，只能做结果评测；有 Trace，才能判断「过程是否合理」。

建议至少记录：

- 输入 prompt。
- 实际触发的 Skill。
- 读取过的文件和关键行号。
- 执行过的命令。
- 生成 / 修改的文件。
- 关键中间判断。
- 最终产物。
- 评分结果和失败原因。

### 8.2 基线怎么建

1. 选一批代表性用例。
2. 跑当前 Skill。
3. 人工确认哪些输出是正确的。
4. 保存产物、Trace 和评分。
5. 后续每次修改都与这批基线比较。

### 8.3 能力测评与回归测评分开

| 类型 | 目的 | 特点 |
| --- | --- | --- |
| 能力测评 | 探索新能力上限 | 用例可变化，允许试错 |
| 回归测评 | 保住已有能力 | 用例稳定，改动必须不退化 |
| Holdout 测评 | 防止过拟合 | 不给优化过程看，只在门控时跑 |

一条能力稳定后，要从 capability eval 毕业到 regression eval。

---

## 九、自进化 Skill：先有评测，再谈自动优化

没有自动化评测集时，不要做全自动自进化。否则很容易为了通过某个 case，把通用能力改坏。

### 9.1 三条路线怎么选

| 路线 | 适合场景 | 核心机制 | 风险 |
| --- | --- | --- | --- |
| Trace2Skill | 从 0 到 1 生成基线 Skill | 从成功 / 失败轨迹归纳规则，合并成 Skill 补丁 | 缺自动验证时容易把偶然经验固化 |
| EvoSkill | 持续扩展 Skill 库 | Executor / Proposer / Builder 三角色，验证集优于旧版才保留 | 验证集弱会放大错方向 |
| SkillOpt | 精调核心瓶颈 Skill | rollout、minibatch reflection、有界文本更新、validation gate、rejected-edit buffer | 成本高，对评测质量要求高 |

### 9.2 Skill-Evolver 的最小闭环

保留 8 阶段，但落地时不要一次做复杂平台，先实现最小闭环：

1. Setup：准备评测计划、dev / holdout / regression 用例。
2. Review：读取上一轮结果和失败 Trace。
3. Ideate：只基于 Trace 提一个原子改动。
4. Modify：一次只改一处；能写成「A 和 B」就拆成两轮。
5. Verify：先跑快速门卫，再跑 dev eval。
6. Gate：质量、成本、安全、回归、可维护性全部通过才保留。
7. Log：写入结果和 per-case Trace。
8. Loop：继续、升层或停止。

### 9.3 三层评测

| 层级 | 频率 | 内容 |
| --- | --- | --- |
| L1 快速门卫 | 每轮 | 结构检查、危险规则扫描、少量 smoke case |
| L2 Dev Eval | 每轮 | 全量 dev 集，输出逐用例结果和失败 Trace |
| L3 Strict Eval | 条件触发 | holdout、regression、盲审 A/B |

### 9.4 门控用 AND，不用加权平均

只要有一个关键维度失败，就不合入。原因是加权平均会允许「质量涨一点，但成本翻倍」或「通过率升高，但安全退化」。

---

## 十、发布门禁

把 Skill 当代码包治理，而不是当一段 prompt。

建议门禁：

1. **结构门禁**：`SKILL.md`、`description`、`scripts/`、`references/` 命名和编码检查。
2. **触发门禁**：should-trigger 召回达标，should-not-trigger 误报受控。
3. **效果门禁**：quality cases 通过率不低于上一版。
4. **安全门禁**：危险命令、硬编码凭证、过宽权限、外联行为扫描。
5. **回归门禁**：旧能力不能退化。
6. **人工门禁**：高风险 Skill 合入前做抽样人工审查。

---

## 十一、AI 辅助快速落地路径

不要手工从 0 搭一整套平台。最快路径是先做「AI 辅助半自动迭代」：AI 负责生成用例、写 Rubric、跑评估、归因失败、提出最小改动；程序负责门控；人负责确认关键样本和是否合入。

### 11.1 第 1 天：跑通半自动 MVP

目标不是完美，而是让一个 Skill 能被自动评一次。

1. 让 AI 根据 `SKILL.md` 生成初版用例：
   - 3 个 should-trigger。
   - 3 个 should-not-trigger。
   - 2～3 个 quality case。
2. 让 AI 为每个 quality case 生成 5～8 条 Rubric。
3. 人工快速删掉明显不合理的 case，不追求一次写全。
4. 跑「无 Skill / 有 Skill / 新版 Skill」对比。
5. 保存结果到 `evaluation/results.tsv`，保存产物和 Trace。

第一天只要回答 3 个问题：

- 这个 Skill 是否该触发时触发？
- 触发后是否比不用 Skill 更好？
- 失败样本能否归因到 `workflow`、`eval` 或 `capability`？

### 11.2 第 2～3 天：做成可迭代版

把 AI 接入「评估 → 归因 → 提案」闭环，但先不要让 AI 自动合入。

```text
AI 生成 / 补充用例
→ 执行评测
→ Judge 打分
→ 失败归因
→ AI 提出一个最小 patch
→ 跑门控
→ 人工确认是否合入
```

这一阶段的关键约束：

1. AI 每轮只能提一个原子改动。
2. 改动必须引用失败 case 或 Trace 证据。
3. patch 先作为建议输出，不直接自动写入稳定版。
4. 门控不过就丢弃，不靠解释说服自己。
5. 连续 2～3 轮卡住时，先检查 case 和 Rubric，而不是继续改 Skill。

### 11.3 第 1 周：升级为安全自动迭代版

当用例和 Rubric 稳定后，再允许更强的自动化。

1. 拆出 `dev`、`holdout`、`regression` 三类用例：
   - `dev`：每轮优化用。
   - `holdout`：防过拟合，平时不给优化器看。
   - `regression`：防旧能力退化。
2. 做 L1 / L2 / L3 三层评测：
   - L1：结构检查、安全扫描、smoke case。
   - L2：全量 dev eval。
   - L3：holdout + regression + 盲审 A/B。
3. 开启 AND 门控：
   - 触发不退化。
   - 效果不退化。
   - 安全不退化。
   - 成本不过度上升。
   - 可维护性不变差。
4. 只有门控全部通过，才允许自动合入或生成正式 PR。

### 11.4 最小工具形态

先做命令行，不做平台：

```text
skill-eval-runner/
├── run_eval.py
├── exams/
│   └── example-case/
│       ├── meta.yaml
│       ├── task.md
│       ├── rubric.md
│       ├── env.yaml
│       └── fixtures/
├── traces/
│   └── run-001/
│       ├── transcript.jsonl
│       ├── transcript.for-judge.txt
│       ├── score.yaml
│       └── review.md
├── patches/
└── results.tsv
```

推荐命令：

```bash
python run_eval.py --skill path/to/skill --mode dev
python run_eval.py --skill path/to/skill --mode strict
```

第一版 `run_eval.py` 只需要做 4 件事：

1. 读取 `exams/*/{meta.yaml, task.md, rubric.md, env.yaml}`。
2. 调用 Examiner 和 Candidate，或记录人工执行结果。
3. 生成 `transcript.jsonl` 和 `transcript.for-judge.txt`。
4. 调用 Judge 输出 `score.yaml`、`review.md` 和失败归因。
5. 汇总写入 `results.tsv`。

### 11.5 不要一开始自动做的事

- 不要一开始让 AI 自动合入 patch。
- 不要一开始追求 100 个 case。
- 不要一开始做 Web 平台和数据库。
- 不要没有 holdout / regression 就做全自动自进化。
- 不要让同一个 Agent 同时执行、评分、修改、合入。

---

## 十二、反模式清单

- 只测正例，不测 near-miss 负例。
- 让执行 Agent 自己判自己通过。
- 只看最终回答，不看 tool call、文件改动和 Trace。
- 没有人工确认基线，却宣称新版更好。
- 用加权平均掩盖安全、成本或回归失败。
- 为了一个失败 case 反复改 Skill，却不怀疑测试数据本身。
- 直接追榜单或平台结论，不把评测接到自己的用例和门控。
- 把「联网工具横评」放进方法论主线，但没有来源链接和复核日期。

---

## 十三、证据索引

| 主题 | 来源 |
| --- | --- |
| 三类评分器、五维度、用例集、基线、能力 / 回归测评、Trace | `tengxuntech\AI_Agent___Skill_测评方案及落地实践.md:57-99`, `168-190`, `299-329`, `405-463`, `486-513`, `539-572` |
| Rubric 原则、Skill 开发自动评测、品质锚点 | `alitech\Harness_Engineering_长程自动化_AI_Coding___Skills_开发实践.md:210-233`, `339-382`, `404-453` |
| Skill-Evolver、三层评测、AND 门控、Trace 诊断 | `tengxunyun\让Skill自己训练自己_8阶段Loop_3层评测_5维AND门控_从此实现自进化.md:134-143`, `176-221`, `237-244` |
| Trace2Skill / EvoSkill / SkillOpt 三路线 | `aliyun\如何更科学_方向可控的实现_Skill_的_自进化__.md:56-119`, `148-190`, `212-310`, `314-380` |
| 触发评估、效果评估、推荐指标 | `tengxuntech\如何写好_Skill_一份终极实战经验手册.md:1283-1451`, `1554-1581` |
| Skill-Creator 的 Grader / Comparator / Analyzer 与局限 | `aliyun\Agent_Skill规范_构建与设计模式.md:216-279`, `370-455` |
| 内部自查 + 外部 eval | `taobaotech\Agent_skill_迭代式编写实战.md:131-159` |
| 业务质量提升路径与四层质量防线 | `taobaotech\面向Skills编程_淘宝企业购端对端研发提效实践.md:89-105`, `278-332`, `370-376` |
| 发布门禁、回归 eval、安全扫描 | `aliyun\重新定义Skill开发_保姆级教程_一站式开发助手发布.md:380-390`, `424-457` |
| SkillTrustBench 安全评测目标、误报 / 漏报权衡 | `tengxuntech\谁是_Agent_最强守门员_首个_Agent_技能安全评测基准_SkillTrustBench_正式发布.md:76-100`, `116-140` |
| Harness Eval 考题结构、Examiner 多轮交互、Judge 上帝视角、双轨输出 | `tengxuntech\你的_Harness_工作流真的在进步吗_我们用一场考试撕掉了遮羞布.md:61-72`, `95-130`, `138-166`, `179-214`, `216-242` |
