# Harness Engineering 是什么？核心组件 / 模式研究报告

## 结论

**Harness Engineering（驾驭工程 / 马具工程）是 2026 年初在 AI 工程圈成形的一套工程范式：把大模型「之外」的所有工程基础设施系统化地设计出来，让一个「聪明但不可预测的非确定性引擎」在约束、反馈与验证中稳定、持续、不失控地完成真实软件交付。** 它的核心公式是 **Agent = Model + Harness**——「模型提供智能，Harness 让智能变得有用」。

- **起源**：术语由 Mitchell Hashimoto（HashiCorp 创始人）在 2026 年 2 月博客《My AI Adoption Journey》第五阶段「Engineer the Harness」首次命名；同月 OpenAI 发布《Harness Engineering: Leveraging Codex in an Agent-First World》，披露「3–7 人团队 5 个月生成约 100 万行生产级代码、1500 个 PR、零行人工编写」的实验，引爆行业讨论。其思想前身可追溯到 ReAct（2022/2023）、Reflexion、Tree of Thoughts 等论文，以及 Anthropic《Effective Harnesses for Long-Running Agents》(2025.11)、LangChain《The Anatomy of an Agent Harness》(2026.03)、Thoughtworks/Martin Fowler 的前馈/反馈分类。
- **核心组件（资料库内最权威的一份「六大组件」拆解）**：① 文件系统、② Bash + 沙箱、③ 记忆（AGENTS.md）、④ Web Search + MCP、⑤ 上下文工程、⑥ 编排 + Hooks，外加贯穿全部的 System Prompt「神经系统」。其它资料给出平行的组件视图：Rule / Skill / Sub Agent / Workflow / Scripts / MCP（万字干货）、上下文架构/架构约束/自验证循环/上下文隔离/熵治理/可拆卸性「六大支柱」（技术教科书）、以及生产级 Multi-Agent Harness 的五模块（架构编排/工具治理/状态与记忆/评估体系/成本控制）。
- **核心模式**：探索-规划-执行三段循环、上下文隔离子 Agent（上下文防火墙）、分支-合并并行、分层/渐进式上下文压缩、Planner-Generator-Evaluator 角色分离（Anthropic F-Harness）、前馈控制（Rules）+ 反馈控制（Hooks）双环、确定性门禁（fail-closed）、渐进式披露（AGENTS.md 当目录而非百科）、技术债后台「垃圾回收」Agent、模型路由 + Token 预算分级降级、宠物/牲畜基础设施哲学、控制论（设定目标→感知偏差→施加干预→消除偏差）。
- **共识贯穿全部资料**：瓶颈不在模型智能而在 Harness；工程师角色从「写代码」迁移到「设计环境、明确意图、构建反馈回路、做验收」（Human steer, agents execute）；规则/知识必须沉淀进版本库（Agent 看不到的就不存在）；模型越强、所需 Harness 越薄（Harness 衰变定律）。

资料库内 Harness 主题文章极多（96 篇提及、61 篇深度提及），本报告通过相关性分级与主题校验，区分出「系统讲解 HE 概念/组件/模式」的文章（判为相关）与「只是用到 HE、或某业务的 Harness 实践案例 / 产品公告 / 借 Harness 之名实讲评测」的文章（判为部分相关/低相关/排除）。

## 覆盖范围

- **资料库**：`E:/work/gongzhonghao_md`（子目录 alitech / aliyun / aliyunys / taobaotech / tengxuntech / tengxunyun）
- **是否递归**：是
- **扫描文件数**：412 个 `.md` 文件
- **候选资料数**：96 篇正文出现「Harness」；其中 61 篇为「≥5 次提及」的有效候选（另 35 篇为 1–4 次的顺带提及，归入低相关）。文件名直接含「Harness」者 42 篇（含 aliyun/aliyunys 跨号重复）。
- **全文阅读上限**：15 篇（用户指定）
- **完整阅读资料数**：13 篇（其中 11 篇逐篇全文通读；`万字干货` 因 1570 行超长，完整读毕定义章 01–02 与全文标题结构；`技术教科书` 因 1397 行超长，完整读毕 Part 7「Harness Engineering」专章与全文标题结构。两篇均做了分段/结构化阅读，已在下文注明。）
- **检索词**：
  - 英文/术语：`Harness`、`harness`、`Harness Engineering`、`Agent Harness`、`Multi-Agent Harness`、`Model + Harness`、`AGENTS.md`、`MCP`、`Hooks`、`Sub Agent`、`Orchestration`、`Context Engineering`、`Cybernetics`、`F-Harness`、`Codex`
  - 中文：驾驭工程、马具、缰绳、挽具、六大组件、核心模式、控制论、前馈/反馈、上下文工程、编排、门禁、沙箱、记忆、自验证循环、规格驱动 SDD、人类掌舵 Agent 执行

## 相关文章

| 文章名 | 路径 | 相关性 | 关键内容 |
| --- | --- | --- | --- |
| 一文讲透如何构建Harness——六大组件全解析 | tengxunyun/一文讲透如何构建Harness__六大组件全解析.md | 相关 | 最权威的「六大组件」拆解；Agent=Model+Harness；裸模型四硬伤；System Prompt 神经系统 |
| 深入浅出Harness Engineerring之核心模式与理念 | tengxunyun/深入浅出Harness_Engineerring之核心模式与理念.md | 相关 | 设计模式目录（持久化指令/作用域上下文/分层记忆/做梦整理/渐进压缩/工作流编排/工具权限/确定性 Hooks）；Claude/Harness/Sandbox 三件套；Hermes 五段循环+五层记忆 |
| 从Prompt、Context到Harness，工程的三次进化与终局之战 | tengxunyun/从Prompt_Context到Harness_工程的三次进化与终局之战.md | 相关 | 三次进化嵌套关系；OpenAI 三大策略；Anthropic F-Harness（Planner/Generator/Evaluator）；Harness 衰变定律 |
| 一文讲透：Harness Engineering即控制论！ | tengxunyun/一文讲透_Harness_Engineering即控制论_.md | 相关 | HE 起源（OpenAI/George）；OpenAI 七条实践教训；控制论（信息/控制/反馈/可能性空间/共轭控制/传感器） |
| 从Harness架构到Token经济学的探索 | tengxunyun/从Harness架构到Token经济学的探索.md | 相关 | HE 诞生史时间线 + 学术论文；LangChain 52.8%→66.5% 数据；前馈(Rules)+反馈(Hooks)双环；四层 .codebuddy；KV Cache/Token 经济学 |
| 从零设计生产级 Multi-Agent Harness | tengxunyun/从零设计生产级_Multi_Agent_Harness_架构_评估_记忆_成本与_MCP_工具接入全拆解.md | 相关 | 生产级 Harness=Agent 操作系统；五模块（编排/工具治理/状态记忆/评估/成本）+ MCP；落地三阶段 |
| Harness Engineering 来了，SDD 还有意义吗？ | tengxunyun/Harness_Engineering_来了_SDD_还有意义吗_.md | 相关 | Hashimoto 定义；OpenAI 仓库结构（specs/plans/docs）；Spec 三角色；Harness 飞轮；AGENTS.md 当目录 |
| 万字干货！Harness Engineering如何工程化落地？ | tengxunyun/万字干货_Harness_Engineering如何工程化落地_.md | 相关 | 组件定义（Rule/Skill/Sub Agent/Workflow/Scripts/MCP/SPEC/dev-map/任务看板）；JK Launcher 真实项目；七 Agent 结构化调度演进 |
| 技术教科书：顶级开发团队设计的Harness工程项目源码什么样 | tengxuntech/技术教科书_顶级开发团队设计的Harness工程项目源码什么样.md | 相关 | 从 ~512K 行编码 Agent 源码反推 HE「六大支柱」；query() 16 步循环；五层权限 fail-closed；AutoDream 熵治理 |
| AI 不缺智商缺纪律：我的 Harness 工程化实践 | aliyun/AI_不缺智商缺纪律_我的_Harness_工程化实践.md | 相关 | harness=可执行/可约束/可评测框架；「模型供智商，harness 供纪律」；三层加载；19 节点链×G1–G8 门禁；dispatcher 状态机+文件交接；经验三级进化 |
| 从玩具到生产力：用真实项目讲透 AI Agent 的 Harness Engineering | aliyun/从玩具到生产力_用真实项目讲透_AI_Agent_的_Harness_Engineering.md | 相关 | 传统 SWE 管确定性 vs HE 管非确定性；架构坐标系四象限；伪/劣质 Harness 避坑；契约式设计（前置/后置/不变式）；8 阶段 SOP |
| Harness驾驭工程是AI平权的必经之路？ | aliyun/Harness驾驭工程是AI平权的必经之路_.md | 相关 | 马具隐喻；三次工程演进（人类角色 用户→Builder→用户）；4 个外部案例（Hashline/技术债放大/上下文防火墙/反馈回路）；群体智能 HiClaw |
| Harness Engineering落地前，先想清楚这几个问题 | tengxunyun/Harness_Engineering落地前_先想清楚这几个问题.md | 部分相关 | 主题主要是 AI 产品前端架构（图表推荐/流式高亮）；仅后半 Part 3–4 涉及 HE 思路（规则进仓库/收敛出口/Design Token/显式可搜索） |

## 综合总结

### 1. Harness Engineering 是什么（高度共识）

资料库内所有相关文章对定义高度一致，可归纳为三层表述：

- **隐喻层**：Harness 原意「马具/挽具/缰绳」。模型是强大但黑盒不可控的「马/龙/引擎」，Harness 是让这股力量「指哪打哪」的整套装备，工程师是骑手（《六大组件》《三次进化》《AI 平权》均用此喻）。
- **公式层**：**Agent = Model + Harness**——「模型之外的一切工程基础设施」。多篇直接引用 LangChain 原话「The model contains the intelligence and the harness is the system that makes that intelligence useful」（《Token 经济学》《六大组件》）。
- **本质层**：HE 解决的不是「让 AI 更聪明」，而是「把一个聪明但缺常识、非确定性的引擎，纳入可约束、可协作、可校验、可持续维护的工程体系」（《万字干货》《从玩具到生产力》）。《从玩具到生产力》给出最锐利的边界判定：**传统软件工程管「确定性」（防人手滑），Harness Engineering 管「非确定性」（防概率引擎暴走）**——这是 HE 区别于「老软件工程实践换皮」质疑的关键。

**起源与时间线**（《控制论》《Token 经济学》《SDD》《AI 平权》交叉印证，一致）：
- 2022–2023：ReAct（Thought-Action-Observation 循环）、Reflexion（失败→反思→长期记忆）、Tree of Thoughts 奠定算法基础。
- 2025.11：Anthropic《Effective Harnesses for Long-Running Agents》——双 Agent 架构 + 进度文件解决长任务跨窗口失忆。
- 2026.02：Mitchell Hashimoto 在《My AI Adoption Journey》第五阶段命名 Harness Engineering，定义「每当发现 Agent 犯错，就工程化一个让它永不再犯的方案」。
- 2026.02：OpenAI《Harness Engineering: Leveraging Codex...》——3–7 人 / 5 月 / ~100 万行生产代码 / 1500 PR / 零行人工编写，提出「Human steer, agents execute」。
- 2026.03–04：LangChain《Anatomy of an Agent Harness》（引入控制论）、Thoughtworks/Martin Fowler（前馈 vs 反馈控制分类）、Meta-Harness（Stanford/MIT，自动搜索最优 Harness，同模型性能差最高 6 倍）。

### 2. 核心组件（多套平行视图，互相印证又各有侧重）

资料库给出至少四套「组件分解」，它们不是冲突而是不同抽象层/不同落地形态：

**视图 A — 六大组件（《一文讲透·六大组件全解析》，最系统）**
1. **文件系统**：Agent 的「外部大脑」，突破上下文窗口；+ Git 给 Agent「试错/回滚」能力。
2. **Bash + 沙箱**：从「说」到「做」；核心是「写→跑→看→修→再来」自我验证循环（实测任务完成率高 40–60%）；沙箱（Docker/gVisor/Firecracker/WASM）是必要前提，非可选加固。
3. **记忆（AGENTS.md）**：「上下文注入 = 不改权重给模型加知识」；层次化存放、双向可编辑、可审计。
4. **Web Search + MCP**：突破知识截止；MCP 是「AI 世界的 USB-C」，把感知范围从公网扩到任何可编程数据源。
5. **上下文工程**：对抗 Context Rot；策略含压缩、工具输出卸载、Skills 渐进加载、分层上下文；是影响所有组件的「元能力」。
6. **编排 + Hooks**：单兵→集团军；编排管「谁做什么」（线性/DAG/动态/层级），Hooks 管「做得对不对」（Lint/续接/格式/安全/成本），用「确定性校验」兜住「概率性生成」。
- 贯穿全部的 **System Prompt** 是「神经系统」（定义角色边界/注入领域知识/约束安全/影响所有组件）。

**视图 B — 工程落地零件（《万字干货》）**：Rule（软约束红线）/ Skill（标准操作手册）/ Sub Agent（角色分工）/ Workflow（接力赛规则）/ Scripts（最硬的门禁，「跑过我这关才算」）/ MCP（外接工程系统的标准插座）/ SPEC（作战目标）/ dev-map（开发导航地图）/ 任务看板。强调 Rule 是软约束、Scripts 是硬门禁——「成熟的 Harness 最终越来越依赖脚本，而非提示词」。

**视图 C — 六大支柱（《技术教科书》，从源码反推）**：上下文架构 / 架构约束（fail-closed，遗漏不是漏洞）/ 自验证循环（query() 16 步只有 1 步调模型）/ 上下文隔离（进程级+通信接口化+控制面/数据面分离）/ 熵治理（AutoDream 后台整合）/ 可拆卸性（依赖注入、Skills=Markdown、MCP 标准、模型降级）。佐证「512K 行代码中模型调用相关 <5%，95% 是 Harness」。

**视图 D — 生产级 Multi-Agent 五模块（《从零设计生产级》）**：架构编排（Orchestrator 独占五项决策权）/ 工具治理（Tool Registry 九项元信息、RBAC）/ 状态与记忆（State 三层 vs Memory 两类，含遗忘机制）/ 评估体系（Component/Trajectory/Task/E2E 四层 Eval，「不要只看答案要看轨迹」）/ 成本控制（Token Budget 绿黄红熔断分级 + Model Routing）+ MCP 安全接入。

### 3. 核心模式 / 设计模式

最完整的模式目录见《深入浅出·核心模式与理念》，与其它文章互补，可归纳为：

- **上下文/记忆模式**：持久化指令文件（AGENTS.md/CLAUDE.md）、作用域上下文组装、分层记忆（常驻精华/按需细节/仅搜索历史）、做梦整理（后台去重重组，类垃圾回收）、渐进式上下文压缩、上下文裁剪/卸载。
- **工作流/编排模式**：探索-规划-行动三段循环（只读探索→对齐规划→有写权执行）、上下文隔离子 Agent（HumanLayer「上下文防火墙」：父 Agent 用强模型规划、子 Agent 隔离上下文用弱模型执行、只回压缩结果）、分支-合并并行、Planner-Generator-Evaluator 分离（Anthropic F-Harness，生成者与评估者独立以对抗 AI「给自己 bug 打高分」）、结构化调度（《万字干货》七 Agent + 只做路由的 PM）、dispatcher 状态机 + 文件交接（《AI 不缺智商缺纪律》）。
- **工具/权限模式**：渐进式工具扩展、命令风险分类（安全/有风险/危险 → 自动/确认/拦截）、单用途工具设计、Tool Registry 白名单、高风险走 Human-in-the-Loop。
- **控制/反馈模式**：确定性生命周期 Hooks、前馈控制（Rules，行动前注入约束）+ 反馈控制（Hooks，行动后检测纠偏）双环（《Token 经济学》）、fail-closed 默认拒绝、确定性门禁 G1–G8、「成功应沉默、失败才发声」（HumanLayer，避免 4000 行通过日志污染上下文）、循环检测、强制验收 checklist。
- **基础设施哲学**：宠物/牲畜（Session 是宠物要持久保存；Harness/Sandbox 是牲畜可随时重建）、凭证永不进沙盒（vault+proxy）、控制面/数据面分离、最小真相源（Spec is Truth）。
- **成本模式**：Model Routing（简单任务小模型、复杂任务强模型）、Token Budget 分级降级、KV Cache/前缀缓存（稳定 Rules 文本 = 高命中 = 实际成本远低于字面字数）、disable-model-invocation。

### 4. 反复出现的跨文章共识（强）

1. **瓶颈不在模型，在 Harness**：LangChain 实验「同一模型仅换 Harness，TerminalBench 2.0 从 52.8%→66.5%、排名 30 外→前 5」被《Token 经济学》《技术教科书》《AI 平权》多次引用。
2. **工程师角色迁移**：从「写代码的人」→「定义目标、设计环境、构建反馈回路、做验收的控盘者」；衡量标准从「个人产出」转向「系统杠杆」（《三次进化》给出新旧标准对照表）。
3. **Agent 看不到的就不存在**：所有设计决策、规则、知识必须版本化进代码仓库（OpenAI 原则，《SDD》《控制论》《落地前》一致强调）。
4. **AGENTS.md 当目录而非百科**：OpenAI 踩过「大型 AGENTS.md」四宗罪（挤占上下文/过多失效/立即腐烂/难核实），结论控制在 ~100 行做索引，配合渐进式披露。
5. **技术债被 Agent 指数放大**：一次坏实现会被 Agent 当「先例」系统性复制（自繁殖系统/癌细胞比喻），需后台「垃圾回收/doc-gardening」Agent 持续小步偿还。
6. **确定性兜底概率性**：用确定性脚本/Hooks/门禁约束概率性模型输出，是当前最有效的质量保障。

### 5. 差异与张力（资料间不完全一致之处）

- **「核心组件」到底是几个**：六大组件 vs 六大支柱 vs 五模块 vs Rule/Skill/Agent/Workflow/Scripts——并非矛盾，而是「能力分解」「源码落地」「生产模块」「工程零件」四种视角。读者应理解为同一系统的不同切面，而非一份权威清单。
- **Harness 该多「厚」**：《三次进化》提出「Harness 衰变定律——模型越强所需 Harness 越简单」，主张「不要过度设计模型未来能自我解决的问题」；《SDD》则反向强调「Harness 越强、Spec 越重要（放大器效应）」。两者并不冲突（前者讲约束规则的厚度会随模型变薄，后者讲意图/规范的价值会被放大），但侧重相反，工程取舍需自行权衡。
- **多 Agent 编排机制选型**：《AI 不缺智商缺纪律》实测后认为 Claude Code 原生 Workflow（计算平面）、Agent Team（协作平面）都不适合做「有状态工序链+人工门禁+跨天续跑」的控制平面，最终选 dispatcher 状态机 + 文件交接；而《从零设计生产级》推荐 LangGraph/自研状态机。属经验性差异。
- **「等待成本 vs 纠错成本」**：OpenAI 主张「PR 生命周期尽量短、不因偶发失败阻塞」（纠错成本低于等待成本）；《控制论》作者明确对此存疑——金融支付等场景「安全稳定比快更重要」。

## 单篇文章摘要

### 《一文讲透如何构建Harness——六大组件全解析》
- 路径：tengxunyun/一文讲透如何构建Harness__六大组件全解析.md（作者 李伟山，2026-04-01）
- 相关性：相关（资料库内回答「核心组件」最直接、最系统的一篇）
- 核心观点：Agent=Model+Harness；裸模型四硬伤（无跨会话状态/不能执行代码/无实时知识/无工作环境）一一对应六大组件补救；竞争壁垒在 Harness 层不在模型层。
- 关键证据：四硬伤→组件对应表（行 123–128）；六大组件逐节展开（文件系统行 134、Bash+沙箱行 189、AGENTS.md 行 251、Web Search+MCP 行 309、上下文工程 365、编排+Hooks 413）；「上下文工程是 Harness 的元能力，Harness 本质上是好的上下文工程的交付机制」（行 407）；System Prompt 神经系统四角色（行 471–504）；自我验证循环高 40–60%（行 215）。

### 《深入浅出Harness Engineerring之核心模式与理念》
- 路径：tengxunyun/深入浅出Harness_Engineerring之核心模式与理念.md（作者 张碧泉，2026-04-29）
- 相关性：相关（资料库内「核心模式」目录最全的一篇）
- 核心观点：以模式目录形式罗列 Harness 设计模式及其「代价」，并拆解 Claude Managed Agents 的三件套解耦与 Hermes 自进化架构。
- 关键证据：Claude Code 模式族（持久化指令文件/作用域上下文组装/分层记忆/做梦整理/渐进压缩/探索-规划-行动/上下文隔离子智能体/分支-合并/渐进工具扩展/命令风险分类/单用途工具/确定性 Hooks，行 18–114）；宠物/牲畜哲学（行 120–125）；Claude(大脑)/Harness(双手)/Sandbox(工作台)解耦 + 凭证永不进沙盒 vault+proxy（行 127–158）；多脑一手/一脑多手/多脑多手（行 163–167）；Hermes 五段循环「规划→执行→观察→学习→适应」+ 五层记忆 L1–L5（行 193–253）。

### 《从Prompt、Context到Harness，工程的三次进化与终局之战》
- 路径：tengxunyun/从Prompt_Context到Harness_工程的三次进化与终局之战.md（作者 李伟山，2026-05-20）
- 相关性：相关
- 核心观点：Prompt→Context→Harness 三次进化是「层层包裹的嵌套」而非替代；三者分别回答「说什么/该知道什么/系统如何可靠运转」。
- 关键证据：OpenAI 三大策略（上下文治理/验证闭环/技术债清理，行 219–239）；Anthropic F-Harness 三角色 Planner/Generator/Evaluator 及代价对照表（单 Agent 20 分钟/$9 vs 三 Agent 6 小时/$200，行 251–267）；Harness 衰变定律「模型越强所需 Harness 越简单」（行 313–351）；工程师能力新旧衡量标准对照（行 383–390）；Human steer, agents execute（行 361）。

### 《一文讲透：Harness Engineering即控制论！》
- 路径：tengxunyun/一文讲透_Harness_Engineering即控制论_.md（作者 邬俊杰，2026-04-17）
- 相关性：相关
- 核心观点：HE 在数学上等价于维纳控制论（信息/控制/反馈）；AI 编程的「设定目标→感知偏差→施加干预→消除偏差」回路即控制循环。
- 关键证据：HE 起源于 OpenAI 2026-02-11 文章 + George《Harness Engineering Is Cybernetics》（行 22、32、130）；OpenAI 七条实践教训（给目录而非整本说明书/规则沉淀到仓库/务必有架构约束/构建 AI 可观测系统/等待成本高于纠错成本（作者存疑）/让 AI 清理垃圾代码/人类建议沉淀到仓库，行 40–66）；可能性空间、负反馈控制力累积（老鹰俯冲）、共轭控制（曹冲称象）、传感器（业务无关/业务相关，行 96–293）；古法编程 vs HE 工作内容对照表（行 343–351）。

### 《从Harness架构到Token经济学的探索》
- 路径：tengxunyun/从Harness架构到Token经济学的探索.md（作者 马俊昌，2026-06-23）
- 相关性：相关（学术脉络 + 双环控制 + Token 经济学最完整）
- 核心观点：Harness 是包裹模型的「壳」，决定模型「能看到什么/行为边界/如何知道做对」；其理论基础是控制论双环（前馈 Rules + 反馈 Hooks）、ReAct、Reflexion、MCTS、信息熵压缩。
- 关键证据：HE 诞生史时间线表（ReAct 2022→Reflexion→ToT→Anthropic 2025.11→Hashimoto 命名 2026.02→OpenAI→LangChain→Thoughtworks→Meta-Harness，行 50–60）；LangChain TerminalBench 52.8%→66.5%（行 30）；双环控制 ASCII 图（前馈=Rules、反馈=Hooks，行 75）；四层 .codebuddy（Commands/Skills/Rules/Hooks，行 220–231）；KV Cache/前缀缓存/Radix Tree（行 394–402）；优化后基础开销 -36%（行 406–412）；附完整学术论文与工程文章参考表（行 539–561）。

### 《从零设计生产级 Multi-Agent Harness》
- 路径：tengxunyun/从零设计生产级_Multi_Agent_Harness_架构_评估_记忆_成本与_MCP_工具接入全拆解.md（作者 李伟山，2026-05-13）
- 相关性：相关（生产级组件/治理视角最完整）
- 核心观点：Multi-Agent Harness 是 Agent 的「操作系统」，负责编排/调度/记忆/状态/工具治理/预算/可观测/安全；Demo 到生产的鸿沟靠 Harness 跨越。
- 关键证据：「Agent 负责局部智能，Harness 负责全局控制」，Orchestrator 独占五项决策权（任务生命周期/执行计划裁决/Agent 路由/失败处理/硬终止，行 76–87）；Tool Registry 九项元信息（行 124–135）；状态三层（Working/Session/Execution Log）vs 记忆两类（Episodic/Semantic）+ 遗忘机制（行 167–208）；四层 Eval（Component/Trajectory/Task/E2E，行 228–254）；Token Budget 绿黄红熔断 + Model Routing（行 284–320）；落地三阶段 MVP/Hardening/Scale（行 384–388）。

### 《Harness Engineering 来了，SDD 还有意义吗？》
- 路径：tengxunyun/Harness_Engineering_来了_SDD_还有意义吗_.md（作者 何艺萍，2026-03-31）
- 相关性：相关（提供 Hashimoto + OpenAI 双视角定义）
- 核心观点：Harness 与 SDD（规范驱动开发）不是竞争而是同一件事两个层面；Harness 是放大器，Spec 是被放大的内容——Harness 越强 Spec 越重要。
- 关键证据：Hashimoto 第五阶段「Engineer the Harness」定义（行 36–44）；OpenAI Harness 仓库结构 docs/ product-specs/ exec-plans/ design-docs/ + 自定义 linter + 结构测试 + 反馈回路 + 垃圾回收 Agent（行 48）；「Agent 看不到的就不存在」（行 70–73）；Spec 三角色（推理地图/约束语义基础/反馈正确性判据，行 84–118）；大型 AGENTS.md 四宗罪 → 当目录 ~100 行（行 196）；Harness 飞轮「Agent 犯错→诊断→工程化修复→不再重犯」（行 112）。

### 《万字干货！Harness Engineering如何工程化落地？》
- 路径：tengxunyun/万字干货_Harness_Engineering如何工程化落地_.md（作者未署，2026，1570 行长文）
- 相关性：相关（阅读方式：完整通读定义章 01–02 与全文 13 章标题结构，做了结构化分段阅读）
- 核心观点：以真实 Unity 启动器项目 JK Launcher 为样本，「人搭 Harness，AI 写代码，人没亲手写一行」，把 HE 拆成可叠加的工程零件并演进出七 Agent 结构化调度。
- 关键证据：六概念速览表 Rule/Skill/Sub Agent/Workflow/Scripts/MCP（行 36–43）；逐一定义（Rule 是软约束非硬门禁行 63；Scripts 是最硬的门禁「跑过我这关才算」行 191；Skill=标准操作手册；Workflow=接力赛规则三层；总门禁脚本检查清单行 199–206）；HE 全貌九块拼图（SPEC/Rule/Skill/Sub Agent/Workflow/Scripts/dev-map/任务看板/MCP，行 251–255）；先从 SPEC 开始、SPEC 不得含「建议/可以/推荐/可选」（行 344）；后续章节含三种多 Agent 做法对比、七 Agent 稳定结构、总验证脚本统一入口、Memory 两类、四块拼图（约束流程/反馈/知识库/进化）。

### 《技术教科书：顶级开发团队设计的Harness工程项目源码什么样》
- 路径：tengxuntech/技术教科书_顶级开发团队设计的Harness工程项目源码什么样.md（2026，1397 行长文）
- 相关性：相关（阅读方式：完整通读 Part 7「Harness Engineering」专章与全文 8 个 Part 的标题/源码结构）
- 核心观点：从某顶级编码 Agent ~512K 行源码反推，证明它是 HE 理念「最完整的工业级实现」——模型调用相关代码 <5%，95% 是 Harness。
- 关键证据：范式三部曲表 Prompt/Context/Harness（行 971–975）；六大支柱在源码的落地（上下文架构=四级压缩管道 Snip/Micro/Collapse/Auto；架构约束=五层权限 + buildTool() fail-closed「遗漏不是漏洞」行 1017–1028；自验证循环=query() 16 步只 1 步调模型 + transition 可断言状态机行 1036–1068；上下文隔离=进程级+UDS 通信+控制面/数据面分离 coordinator 只 3 工具行 1083–1090；熵治理=AutoDream 记忆巩固；可拆卸性=依赖注入+Skills=Markdown+MCP+模型降级）；综合 OpenAI/Anthropic/Martin Fowler/LangChain/Latent Space/Cassie Kozyrkov 六方文献（行 983）。

### 《AI 不缺智商缺纪律：我的 Harness 工程化实践》
- 路径：aliyun/AI_不缺智商缺纪律_我的_Harness_工程化实践.md（作者 杜学友，2026-06-16）
- 相关性：相关（既是个人实践，也系统提出可迁移的 harness 定义与机制）
- 核心观点：harness=把「AI 该怎么干活」固化成可执行/可约束/可评测的框架；「模型供给智商，harness 供给纪律」；对付 AI 不确定性「堆 prompt 是负债，做框架才是资产」。
- 关键证据：膨胀 CLAUDE.md「管用三天就崩」（行 21–24）；三层加载模型（常驻入口≤8K / 原子规则 / 按需上下文，行 48–121）；角色 Agent 流水线 dispatcher+orchestrator+三角色评审+执行链（行 77–102）；19 节点链 × G1–G8 门禁 × intent×risk 动态裁剪（行 147–167）；eval+hook 双机制、「流程强制执行必须从 LLM 推理外置到确定性基础设施 fail-closed」（行 143）；经验三级进化 lesson→pattern→instinct（行 128）；为何选 dispatcher 状态机+文件交接而非原生 Workflow/Team（行 234–257）；七维确定性评分平台（行 300–322）。引用 VILA-Lab/Reflexion/Lost in the Middle/RULER 等学术支撑。

### 《从玩具到生产力：用真实项目讲透 AI Agent 的 Harness Engineering》
- 路径：aliyun/从玩具到生产力_用真实项目讲透_AI_Agent_的_Harness_Engineering.md（作者 无岳，2026-04-21）
- 相关性：相关（概念边界 + 架构坐标系最清晰）
- 核心观点：没有 Harness 大模型只是高级玩具；HE 是把「非确定性引擎」嵌进「确定业务流水线」的物理控制面；程序员从执行者升级为控盘者。
- 关键证据：「传统软件工程管确定性，HE 管非确定性」（行 41）；架构坐标系 X 执行流路由(静态/动态)×Y 状态(隐式/显式)四象限（行 48–62）；伪 Harness（软约束陷阱/军火库陷阱）与劣质 Harness（盲打死循环/官僚重型文档）（行 68–81）；好 Harness 三要素（Evaluator 沙盒前置验证/最小真相源 Spec is Truth/物理门禁 Checkpoint，行 83–86）；契约式设计前置/后置/不变式三契约（行 158–172）；行业印证 OpenAI/Anthropic Checkpoint/deer-flow（行 178–190）；8 阶段 SOP + 三层目标 + 偏航 4 信号（行 226–267）。

### 《Harness驾驭工程是AI平权的必经之路？》
- 路径：aliyun/Harness驾驭工程是AI平权的必经之路_.md（阿里妹，2026-03-30；aliyunys 有近重复版）
- 相关性：相关（提供历史类比 + 4 个外部一手案例）
- 核心观点：OpenClaw 让 AI 主权从模型厂商转移到用户，权责对等催生 Harness 共识；HE 是「AI 时代的操作系统与软件工程方法论的统一体」。
- 关键证据：马具隐喻 + 工业/信息/AI 三次革命类比（行 18、30–40）；三次工程演进及人类角色 用户→Agent Builder→用户（行 44–60）；4 案例（① Hashline 编辑工具改进让 15 模型变强、Grok Code Fast 6.7%→68.3%；② 技术债指数放大/自我复制病毒 + OpenAI 品味编码为规则；③ HumanLayer 子 Agent 上下文防火墙、Terminal Bench 退化曲线；④ 反馈回路「成功应沉默失败才发声」+ LangChain 前 30→前 5，行 70–153）；群体智能 CLI-Anything / HiClaw Manager-Workers + AI Gateway（行 163–209）。

### 《Harness Engineering落地前，先想清楚这几个问题》
- 路径：tengxunyun/Harness_Engineering落地前_先想清楚这几个问题.md（作者 franslee，2026-06-12）
- 相关性：部分相关（主题校验：标题挂 HE，正文主体是 AI 产品前端架构）
- 核心观点：文章实际讲两件事——服务好 AI 产品（图表三维评分推荐引擎、流式代码高亮渲染）与服务好 AI Coding（用 HE 思路改造存量前端项目）。前者与 HE 概念关系弱，后者才是 HE 实践。
- 关键证据：Part 1–2 大篇幅讲图表推荐/Markdown 流式选中/代码高亮增量渲染（行 56–245，与 HE 核心问题无直接关系）；Part 3–4 才落到 HE 思路：把规则变成 AI 上下文进仓库（行 268–282）、给 AI 收敛的代码出口（no-restricted-imports 强约束，行 284–297）、Design Token 抽离（行 299–311）、显式优于隐式/可搜索优于可推导（行 379–406）。因系统讲解 HE 概念/组件的篇幅有限，降级为部分相关。

## 排除或低相关资料

下表为经主题校验后判为「部分相关 / 低相关 / 排除」的代表性资料及原因。资料库内 ≥5 次提及「Harness」的有效候选共 61 篇，扣除上表 13 篇已读，余约 48 篇未进入全文阅读；另有 35 篇仅 1–4 次顺带提及，整体归入低相关。下面按原因分组列举代表，未逐条展开的数量在每组注明。

| 文章名 | 原因 |
| --- | --- |
| 基于顶级Agent（Claude Code）的Harness工程搭建式业务Agent评测方案（aliyun） | 主题校验排除：关键词高度重叠（Harness/Claude Code/评测）但核心主题是「业务 Agent 评测方案」，Harness 只是搭建手段，非讲解 HE 概念/组件 |
| 你的Harness工作流真的在进步吗_我们用一场考试撕掉了遮羞布（tengxuntech） | 主题校验降级：主题是「用考试评测 Harness 工作流是否进步」，属评测方法，非系统讲 HE 是什么 |
| 让Skill自己训练自己_8阶段Loop_3层评测_5维AND门控（tengxunyun） | 主题校验排除：主题是 Skill 自进化/评测门控，仅顺带提及 Harness |
| 从3632个漏洞看AI时代的评测基准重构_VulnGym基准发布（tengxuntech） | 主题校验排除：主题是漏洞评测基准，与 HE 概念无关 |
| QQ音乐Harness_Engineering实践（tengxunyun） | 部分相关：具体业务（QQ 音乐）的 Harness 落地案例，复用 HE 但不系统定义概念/组件 |
| 更可靠的主播助理_淘宝主播Agent的Harness工程实战（aliyun） | 部分相关：淘宝主播 Agent 具体实战案例 |
| Harness_Engineering__C_端_AIGC_内容生产自优化实践（aliyun） | 部分相关：C 端 AIGC 业务自优化实践案例 |
| Harness_Engineering_耗时一周_我是如何将应用的AI_Coding率提升至90_的（aliyun） | 部分相关：个人提效实践复盘，偏「我怎么做的」而非「HE 是什么/组件」 |
| Harness_Engineering实践_做了一个平台让AI一晚上自动评测和优化你的系统（aliyun） | 部分相关：自动评测优化平台实践案例 |
| 当_Agent_替你值班_基于_Devix_构建_7x24_自动化运维_Harness_Engineering（aliyun） | 部分相关：运维场景 Harness 落地案例 |
| Qoder_CLI___Harness_Engineering_实战_构建_7_24h_无人值守用户反馈自动处理系统（aliyun） | 部分相关：Qoder 具体产品实战案例 |
| Qoder_工程实践_Harness_Engineering_指南（aliyun） | 部分相关：产品视角的 Harness 指南，偏 Qoder 实践 |
| 让_AI_自己做增长_基于OPC和Harness思想的自主增长系统探索（aliyun） | 部分相关：增长系统案例，借用 Harness 思想 |
| 首个_Java_Harness_Framework_来了_AgentScope...（aliyun + aliyunys 重复） | 部分相关：产品/框架发布公告（AgentScope Java），偏产品而非概念讲解 |
| AgentScope_Builder_快速体验_用_Harness_框架快速构建企业自进化智能体（aliyun + aliyunys 重复） | 部分相关：产品体验文，偏 AgentScope 工具 |
| 告别_氛围编程__基于_Harness_治理和_SDD_的团队级_AI_研发范式（aliyun） | 部分相关：团队研发范式实践，HE 与 SDD 混讲、偏治理落地 |
| Skill_Factory_三天手搓面向Harness设计的技能工厂（aliyun） | 部分相关：Skill 工厂实践，面向 Harness 但主题是技能生产 |
| 深度解析_OpenClaw / Claude Code / Hermes 在 Prompt+Context+Harness 的设计（aliyun，3 篇） | 部分相关：以具体 Agent 产品为对象的设计解析，Harness 仅为三维度之一 |
| AI_不缺智商缺纪律_一场_Harness_工程化实践（alitech） | 部分相关/疑似重复：与已读 aliyun 版「我的…」标题相近（「一场」vs「我的」），疑为跨号变体，未单独通读 |
| Harness_驾驭工程是_AI_平权之路（aliyunys） | 重复：与已读 aliyun《…AI平权的必经之路》为跨号重复版 |
| 其余约 28 篇（如 Coding_Agent下半场 / 从0到1搭建Agent / 重新思考研发基础设施 / 后端架构AI_Friendly / 认知重建之后步入Agentic / OpenClaw与Hermes源码 / 都是AI_Coding为什么Java 等） | 部分相关/低相关：Agent 通用架构、研发组织、其它工程主题中提及 Harness 作为局部环节，非以「HE 是什么/核心组件模式」为主题；按相关性排序后未进入前 15 |
| 另 35 篇仅 1–4 次顺带提及「Harness」 | 低相关：Harness 为非主题性顺带出现（如书单、随笔、其它技术主题），未逐条列出 |

## 不确定性

- **未读候选较多**：61 篇有效候选中仅完整/substantively 阅读 13 篇（受用户设定的 15 篇上限约束）。未读的约 48 篇里，部分（如 `Harness_Engineering实践心得`、`Code designs Harness 还是 Model drives Harnesses`、`阿里云Agent_Infra上长出的约束基建`、`工程知识引擎_Harness底座`）可能含额外的概念性论述或独特组件视角，本报告未能纳入，可能遗漏个别细节。
- **跨号重复未逐一核对**：aliyun 与 aliyunys 子目录存在多组同题/近题文章（AI 平权、Java Harness Framework、AgentScope Builder 等），疑为同文跨公众号转载；`alitech` 的「一场 Harness 工程化实践」与 aliyun「我的 Harness 工程化实践」标题相近但未逐字比对，是否完全相同未确认。
- **两篇长文为结构化分段阅读**：`万字干货`（1570 行）与 `技术教科书`（1397 行）未逐行通读全文，而是完整读毕其定义/核心专章 + 全文标题结构。其中后续章节（如万字干货第 5–12 章的多 Agent PK、总验证脚本细节；技术教科书 Part 1–6 的启动/工具/查询引擎源码）的具体数据可能有未覆盖之处。
- **一手来源为二手转述**：本报告所有「OpenAI 百万行实验、Anthropic F-Harness、LangChain 数据、Hashimoto 定义、控制论」均来自公众号文章对一手英文资料的转述/意译，个别数字（如 52.8%→66.5%、$9 vs $200、6.7%→68.3%）与原始出处可能存在表述差异，未回溯英文原文核验。
- **组件清单非唯一权威**：资料库给出至少四套「核心组件」分解，本报告将其并列呈现而非裁定唯一标准；不同作者的术语（如「上下文工程」是组件 vs 元能力）存在抽象层级差异。
- **时效性**：资料发布集中在 2026-03 至 2026-06，HE 概念仍在快速演化，「Harness 衰变定律」等论断本身预示当前结论可能随模型升级而部分失效。
