# 如何降低 AI Agent 的 token 消耗 —— 资料库穷举研究报告

## 结论

资料库中确实存在一批**核心主题就是「降低 / 优化 Agent token 消耗」**的文章，且彼此互补，能拼出一套相对完整的方法论。综合已读资料，降低 Agent token 消耗的可落地手段可归纳为六个层次：

1. **认清成本结构**：用户那句话通常只占请求的 1%~5%，真正的大头是 System Prompt、工具/Skill 定义、会话历史、工具返回结果等「系统替你背的上下文」。优化要打大头，而不是把提问写短。
2. **保护与利用缓存（Prompt Cache / KV Cache）**：稳定前缀可享 ×0.1 缓存读取价。优化的关键不是「写短」而是「写稳」——一个 Session 干到底、别中途改配置 / 切模型、把静态内容前置。
3. **压缩进出上下文的内容**：终端输出压缩（RTK）、AI 回复压缩（Caveman）、通用上下文压缩（headroom）、工具结果沙箱化（context-mode）、分层水位线 + 增量摘要、上下文卸载 + Mermaid 结构化记忆。
4. **减少盲搜 / 用结构化检索代替全文堆叠**：代码知识图谱（Graphify / CodeGraph / Codebase-Memory）、本体论 Ontology、LSP 语义检索，可把「找代码」的 token 砍掉数倍到数十倍。
5. **模型路由与预算旋钮**：贵模型只干高价值推理，便宜模型干标准活；调 `thinking budget` / `reasoning effort` / `max output tokens`。
6. **多 Agent / Sub-Agent 上下文隔离**：Orchestrator-Worker 拆分，每个 Worker 只看当前步骤所需上下文，数据靠外置文件传递而非会话历史。

需特别注意：多篇资料的共识是 **Agent 成本绝大部分来自 Input Token（理解 / 寻找），而非 Output（生成）**；且「上下文压缩的真正目标是保护模型注意力，省钱只是顺带」。

## 覆盖范围

- **资料库**：`E:/work/gongzhonghao_md`（约 412 篇公众号技术文章，分 alitech / aliyun / aliyunys / taobaotech / tengxuntech / tengxunyun 六个子目录）
- **是否递归**：是（递归扫描所有子目录）
- **扫描文件数**：412 个 `.md` 文件
- **候选资料数**：含 `token` 关键词的 232 篇 → 收敛到含「降低/节省/减少 token、token 消耗/成本、上下文压缩/卸载、token 经济学、压缩策略」等聚焦检索词的约 107 篇 → 经标题 + 内容定位筛出约 15 篇进入主题校验
- **全文阅读上限**：15 篇（本次任务设定）
- **完整阅读资料数**：8 篇（7 篇全文通读 + 1 篇 ANOLISA 重点段落 + 全文结构核对）
- **检索词**：
  - 中文：token 消耗、token 成本、降低/节省/减少 token、省 token、上下文压缩、上下文卸载、压缩策略、token 经济学、成本控制、缓存、增量摘要、代码图谱、上下文工程、Tokenmaxxing
  - 英文 / 缩写：token, Token, Prompt Cache, KV Cache, Compaction, context offload, context compression, FinOps, MCP, sub-agent, RTK, Caveman, headroom, Ontology, LSP
  - 可能出现在标题里的词：节省、提升、经济学、烧钱、烧光、账单、压缩、第 7 个

## 相关文章

| 文章名 | 路径 | 相关性 | 关键内容 |
| --- | --- | --- | --- |
| 一篇搞懂 AI Coding Agent 的 Token 成本控制 | `E:\work\gongzhonghao_md\tengxuntech\一篇搞懂_AI_Coding_Agent_的_Token_成本控制.md` | 相关（核心） | 五层优化框架（使用习惯→模型路由→上下文压缩→代码图谱→多 Agent）+ RTK/Caveman/headroom/context-mode 四工具实测压缩率 + Prompt Cache 原理 + 行动清单 |
| 横向拆解 Claude Code、Codex 等六大 Agent 上下文压缩策略后，我们做了第 7 个 | `E:\work\gongzhonghao_md\tengxuntech\横向拆解Claude_Code_Codex等六大Agent上下文压缩策略后_我们做了第_7_个.md` | 相关（核心） | 六家产品压缩哲学横评 + 四级水位线 + 增量摘要 + 单调边界防缓存失效 + 云端三层特化设计 |
| 腾讯云 Agent Memory 节省 61% Token：Mermaid 无限画布 × 上下文卸载 | `E:\work\gongzhonghao_md\tengxunyun\腾讯云Agent_Memory节省61__Token提升52_成功率的诀窍_Mermaid无限画布_上下文卸载.md`（在 tengxuntech 有跨号转载） | 相关（核心） | 上下文卸载 + Mermaid 结构化记忆四层折叠（refs/JSONL/MMD/metadata）+ 四组评测实测最高省 61.38% token、通过率相对 +51.52% + 消融实验 |
| 一文搞懂 Token 经济学：同样额度多干 3 倍活 | `E:\work\gongzhonghao_md\tengxunyun\一文搞懂Token经济学_同样额度多干3倍活_只需理解消耗机制.md` | 相关（核心） | API 调用结构拆解 + KV 缓存三档价格 + 四类配置（Memory/Rules/Skills/MCP）加载机制与成本 + 配置侧 + 对话侧优化清单 + 误区纠正 |
| 从 Harness 架构到 Token 经济学的探索 | `E:\work\gongzhonghao_md\tengxunyun\从Harness架构到Token经济学的探索.md` | 相关（核心，token 为 Part4-5 主线） | Rules 分级（L1 always / L2 按需）+ disable-model-invocation + 模型配额分配 + 实测基础开销 -36% 的根因（去重复注入 + 按需加载）+ 用户习惯对 token 影响 |
| 本体论 Ontology 泛谈丨如何帮企业应对 Tokenmaxxing 困局 | `E:\work\gongzhonghao_md\aliyunys\本体论_Ontology_泛谈丨如何帮企业应对_Tokenmaxxing_困局.md` | 相关（核心，从架构侧降 token） | token 烧在哪（Input 主导、依赖探索 C2 是最大结构性成本）+ 代码知识图谱 10× token 压缩 + UModel 运维 Ontology 避免三类 token 开销 |
| RAG 已死？不，是 Grep 回归了 | `E:\work\gongzhonghao_md\tengxunyun\RAG已死_不_是Grep回归了_.md` | 部分相关 | 主题为检索架构（Grep vs 向量索引），但 4.4 节专讲 Grep 的 token 成本控制：prompt cache（实测 -81%）、auto-compaction、子 agent 隔离、LSP 实测 -40% token |
| Agent 烧钱如流水：Agentic OS (ANOLISA) 帮你逐笔看清 Token 账单 | `E:\work\gongzhonghao_md\aliyun\Agent_烧钱如流水_Agentic_OS_(ANOLISA)_帮你逐笔看清_Token_账单.md` | 部分相关 | 主题为 token 可观测（看清账单是省钱前提），含 Tokenless 优化工具包（模式压缩 / 响应压缩 / 命令重写）与「Token 节省」面板（压缩 MCP 响应保语义） |

## 综合总结

**资料中明确说了什么**

- **成本结构**（《Token 成本控制》《Token 经济学》《Ontology》一致）：一次请求 ≈ 固定前缀（System Prompt + 工具/Skill 定义）+ 会话历史 + 运行时检索 + 工具往返 + 输出。用户那句话占比 1%~5%，**Input Token 主导成本**。《Ontology》引三份外部报告（arXiv:2604.22750、Vantage.sh、Reddit 1 亿 token 样本）佐证 Input 占 85%~99%，且 token 消耗与准确率几乎无相关（r<0.15），即「多花钱买不到更好结果」。
- **缓存是一切优化的基础**（《Token 成本控制》1.4、《Token 经济学》第 2 章、《从 Harness…》4.2、《RAG 已死》4.4 共识）：稳定前缀命中缓存后读取价仅为基础价 ×0.1；缓存从头前缀匹配，**中间任何一环变了，其后全部失效**。因此「一个 Session 干到底、别中途改 Rules/Memory、别频繁切模型」是省钱第一性原则。《RAG 已死》给出实测：agentic 循环中 92% 前缀在相邻轮间相同，可降本约 81%。
- **具体压缩工具与实测压缩率**（《Token 成本控制》第 4 章独有）：RTK 压终端输出（测试日志 -90%~99.6%）、Caveman 压 AI 输出（-65%~75%）、headroom 压所有进上下文内容并可逆还原（-47%~92%）、context-mode 沙箱化工具结果（-98%）。代码图谱方面：Graphify 官方称比直读文件减少 71.5 倍 token，CodeGraph 7 仓库 benchmark 平均 -47% token / -58% tool call。
- **上下文压缩的工程化做法**（《横向拆解》独有）：六家产品（Claude Code 五段流水线、Codex handoff 摘要、OpenCode 可逆隐藏、Cline、Cursor、Amp 换线程、MemGPT）哲学横评 → 提炼共识：分层渐进、成本严格递增（本地零成本先做、LLM 摘要兜底）、增量摘要优于全量、用真实 token 别估算、用户消息有特权、保护近端、**单调边界绝不滑窗**（否则每 step 缓存失效，文中真实案例 177 step 烧 $77.3 其中 83% 是 cache_write）。
- **结构化记忆压缩**（《腾讯云 Agent Memory》独有）：上下文卸载（原文落 refs/*.md）+ Mermaid 无限画布（任务结构）+ 四层折叠（Raw→JSONL→MMD→metadata）按需逐级找回。四套评测实测：WideSearch 省 61.38% token、通过率相对 +51.52%；SWEbench 省 33%、完成率 +9.93%；消融实验证明「仅卸载省 15%，卸载 +MMD 省 31%~33%」。
- **配置层降本**（《从 Harness…》《Token 经济学》第 3 章独有）：四类配置（Memory 全量常驻 / Rules 常驻 + 触发 / Skills 按需加载不可卸 / MCP Schema 常驻）的加载机制各异；只把高频规则设 alwaysApply、流程型 Skill 设 `disable-model-invocation`、禁用闲置 MCP、精炼 Memory。《从 Harness…》给出实测基础开销 23.5K→15K（-36%）的逐项根因。
- **架构侧降本**（《Ontology》独有）：把实体关系提前结构化为知识图谱 / 本体论，让 Agent「查图」而非在文本里「现场推断关系」，依赖探索（最大结构性成本源 C2）的 token 可压 10×；企业运维领域因知识不在预训练语料中，Ontology 价值最不可能被「模型变强」吃掉。

**多篇资料的共识**

- Input Token 是大头，要打大头而非把提问写短（《成本控制》《经济学》《Ontology》）。
- 缓存稳定性 > 提示词长度；保护缓存链是省钱核心（《成本控制》《经济学》《从 Harness》《RAG 已死》）。
- 长会话 + 缓存比频繁开新窗口便宜（《经济学》明确 O(N²)→近似 O(N)，新窗口才最贵）。
- Sub-Agent 的价值是隔离上下文防膨胀，**不一定直接省钱**（《经济学》4.x 明确 Sub-Agent 冷启动无缓存反而更贵；《成本控制》第 6 章则强调任务边界清晰时多 Agent 更省）——二者并不矛盾，取决于子任务能否真正拆开、是否重复读背景。
- 压缩 / 卸载的目标是保护模型注意力（Context Rot：>70%~80% 上下文模型中段失忆），省 token 是顺带（《横向拆解》第 11 节、《腾讯云 Memory》3.1 一致）。

**差异与独有细节**

- Sub-Agent 是否省钱，《经济学》与《成本控制》侧重点不同（见上）。
- 检索路线分歧：《RAG 已死》主张代码场景零索引 + Grep（靠 prompt cache/compaction/子 agent 控成本），《Ontology》《成本控制》则主张用知识图谱 / 本体论预结构化来省 token——前者认为代码是 Grep 友好的、本地规模撑得住暴力扫描，后者认为依赖探索必须提前结构化。两者面向的规模与场景不同。
- 《横向拆解》独有「单调边界 vs 滑窗」对 Prompt Cache 的致命影响及生产成本数据，是其他文章未覆盖的工程陷阱。
- 《腾讯云 Memory》独有「Mermaid 结构化记忆 + 四层折叠 + 消融实验」量化数据。

## 单篇文章摘要

### 《一篇搞懂 AI Coding Agent 的 Token 成本控制》

- 路径：`E:\work\gongzhonghao_md\tengxuntech\一篇搞懂_AI_Coding_Agent_的_Token_成本控制.md`
- 相关性：相关（核心，是本主题最完整的「方法论总纲」）
- 核心观点：AI Agent 成本「本质不是你问了什么，而是系统为回答你重复搬运了多少上下文」。给出从便宜到贵的五层优化路径：使用习惯 → 模型路由 → 上下文压缩 → 代码图谱 → 多 Agent 架构。
- 关键证据：
  - 1.1 典型请求结构（System 5K / 文档 10K / Skill 20K / 工具 30K / 历史 100K / 代码 50K / 用户问题 0.1K）；1.3 五类成本（输入 / 输出 / 推理 / 工具往返 / 重试）；1.4 Prompt Cache「省的是重复成本、要写稳不写短」。
  - 第 2 章九条使用习惯（一个 Session 一件事、及时 /compact、外置记忆、限定输出格式、少装 Skill/MCP、CLI 优先、带完整路径、一次说清意图）。
  - 第 3 章模型路由表 + thinking budget；3.5 Skill/Agent/Command 绑模型。
  - 第 4 章四工具实测：RTK（30 分钟会话 118K→23.9K，-80%；cargo test -90%）、Caveman（-65%~75%）、headroom（-47%~92% 且准确率不降）、context-mode（工具输出 -98%）。
  - 第 5 章代码图谱：Graphify「比直读文件减少 71.5× token」、CodeGraph 7 仓库 benchmark（平均 -47% token / -58% tool call）。
  - 第 6 章 Orchestrator-Worker 实测把每轮成本压缩 5-10 倍；第 7 章六个误区；结语行动清单（今天 / 本周 / 本月）。

### 《横向拆解 Claude Code、Codex 等六大 Agent 上下文压缩策略后，我们做了第 7 个》

- 路径：`E:\work\gongzhonghao_md\tengxuntech\横向拆解Claude_Code_Codex等六大Agent上下文压缩策略后_我们做了第_7_个.md`
- 相关性：相关（核心，「上下文压缩 = 降 token」的工程横评 + 落地）
- 核心观点：上下文压缩已是 Agent 必做环节；六家哲学各异但有共识；自研 MUR AI 用四级水位线 + 增量摘要，云端再叠三层。
- 关键证据：
  - 第 1 节六家策略表；第 2 节第一代「撑不住才动手」的五个痛点（悬崖式触发、全量摘要丢细节、token 估算粗糙 text.length/3、不分信息价值、用户内容一刀切）。
  - 第 3 节逐家拆解（Claude Code 五段流水线 + cached_microcompact/apiMicrocompact 服务端裁剪；Codex 95% 触发 handoff；OpenCode 时间戳隐藏 + 回放最后指令；Cursor Dynamic Context Discovery 实测 -46.9% token）。
  - 3.x 滑窗 stub 陷阱：真实 Task 177 step 烧 $77.3，其中 83%($64.8) 是 cache_write（单价是 cache_read 的 12.5 倍）；**stub 决策必须单调推进不能滑窗**。
  - 第 4 节七条共识；第 5 节四级水位线（Tier0<60% / Tier1 Snip 60-80% 零成本 / Tier2 Prune 80-95% / Tier3 增量摘要 ≥95%）；第 6 节云端三层（存储分离、工具差异化、ReplacementCache 跨轮缓存按 part ID 存 Redis）；第 11 节「压缩真正目标是保护注意力（Context Rot），省钱顺带」。

### 《腾讯云 Agent Memory 节省 61% Token 提升 52% 成功率：Mermaid 无限画布 × 上下文卸载》

- 路径：`E:\work\gongzhonghao_md\tengxunyun\腾讯云Agent_Memory节省61__Token提升52_成功率的诀窍_Mermaid无限画布_上下文卸载.md`（注：`tengxuntech` 目录有同名跨号转载，正文基本一致）
- 相关性：相关（核心，带完整实验数据的「短期记忆压缩」方案）
- 核心观点：短期记忆压缩 = 上下文卸载（解决「信息太长」）+ Mermaid 无限画布（解决「结构丢失」），让「细节可恢复、结构不丢失」。
- 关键证据：
  - 符号化压缩三原则（通用知识 / 不过于复杂孤立 / 表达自由）；Flowchart 比 StateDiagram 效果好约 15%。
  - 四层折叠存储：Level0 Raw（refs/*.md）→ Level1 JSONL（工具调用级摘要）→ Level2 MMD（任务步骤级摘要 + 状态 + 时间戳）→ Level3 metadata（taskGoal/status/mmdFilePath）；按 node_id + grep + result_ref 逐级找回。
  - 层次化注意力（鸟瞰→聚焦→下钻）；3.1 引 Anthropic「上下文 >80% 发生上下文腐烂」。
  - 4.2 总体结果表：SWEbench 完成率 +9.93% / 省 33.09%；Toolathlon 通过率 20%→35% / 省 26.18%；WideSearch 通过率相对 +51.52% / 省 61.38%；AA-LCR 准确率 +7.95% / 省 30.98%。4.7 消融：仅卸载省 15%，卸载 +MMD 省 31%~33%。

### 《一文搞懂 Token 经济学：同样额度多干 3 倍活，只需理解消耗机制》

- 路径：`E:\work\gongzhonghao_md\tengxunyun\一文搞懂Token经济学_同样额度多干3倍活_只需理解消耗机制.md`
- 相关性：相关（核心，缓存机制 + 配置成本 + 优化清单）
- 核心观点：成本不在于你说了多少，而在两件事——配置侧精简系统税、对话侧保护缓存；两手抓同额度可多干 3-5 倍。
- 关键证据：
  - 第 2 章 KV 缓存三档价格（写入 ×1.25 / 命中 ×0.1 / 全价 ×1.0），实测 10 轮省 76%，无缓存 O(N²)→有缓存近似 O(N)；缓存从头匹配中间断了后面全废；缓存有效期 5 分钟（Pro/Max 1 小时），可定时保活。
  - 第 3 章四类配置加载机制（Memory 全量常驻 / Rules 三种模式 / Skills 加载前零开销但不可卸 / MCP Schema 常驻 + 结果永久留存）+ 选择指南 + 缓存链全貌图。
  - 第 4 章 Sub-Agent「不省钱但防膨胀」（冷启动全价对比 5.8K vs 15.5K）。
  - 第 5 章配置侧（精减常驻 Rules / 禁用闲置工具 / 精炼 Memory，实测每轮省 1.3K 等价）+ 对话侧七条；附 2 八个误区纠正（含「/compact 会断缓存除非接近窗口上限别用」「长对话恰恰更便宜」）。

### 《从 Harness 架构到 Token 经济学的探索》

- 路径：`E:\work\gongzhonghao_md\tengxunyun\从Harness架构到Token经济学的探索.md`
- 相关性：相关（前 3 部分讲 Harness 架构，Part 4-5 是 token 降本主线，含实测数据）
- 核心观点：在 Harness（Rules/Skills/Hooks/Commands 四层）工程实践基础上做 Token 经济学优化，实测每对话基础开销 -36%。
- 关键证据：
  - Part 4 KV Cache 三层意义（前缀缓存 / 多轮复用 / 工具调用）；4.3 优化前后表（alwaysApply Rules -47%、workspace_rules -60%、每对话基础开销 23.5K→15K -36%、dev Skill -27%）；根因三类（重复注入 ~6K、不必要 alwaysApply ~4.3K、空白占位 ~500）。
  - 流程型 Skill 设 `disable-model-invocation: true` 省推理 token；Rules 分级 L1 always / L2 按需。
  - Part 3 模型配额分配（Claude 25% / DeepSeek 50% / GLM 15% / Hy3 10%）；Part 5 用户习惯 token 差距表（模糊 vs `@文件:行号` 省 3K-15K）、Token 估算公式、7 条黄金法则、self-audit 脚本。

### 《本体论 Ontology 泛谈丨如何帮企业应对 Tokenmaxxing 困局》

- 路径：`E:\work\gongzhonghao_md\aliyunys\本体论_Ontology_泛谈丨如何帮企业应对_Tokenmaxxing_困局.md`
- 相关性：相关（核心，从「架构 / 知识结构」侧降 token，角度独特）
- 核心观点：Agent 的 token 大头是 Input 中的「依赖探索」，把实体关系提前结构化为 Ontology / 知识图谱，可把这部分 token 大幅压缩。
- 关键证据：
  - 三份外部数据（arXiv:2604.22750「agentic 是 chat 的约 1000×、Input 主导、token 与准确率 r<0.15」；Vantage.sh「Input/Output ≈ 25:1、Input 占 85%、前 10 轮探索期密度最高」；Reddit 1 亿 token「99.4% 开销来自 Input」）。
  - Input 五类归因（文件检索 / 关系追踪 / 上下文管理 / 生成循环 / 工具交互），C1 盲读 + C2 依赖探索是主体；C2 最适合架构手段干预。
  - 依赖探索三范式（Stuffing→RAG→Ontology）；代码知识图谱 Codebase-Memory（arXiv:2603.27277）实测「有图谱约 1000 token / 无图谱约 10000 token，10× 压缩、工具调用减 2.1×」；UModel 运维 Ontology 避免三类 token 开销（多轮元数据查询 / 字段映射推断 / 查询语法纠错循环）。
  - 判断：代码场景 Ontology 价值可能被模型内化，但运维等企业领域价值最稳固。

### 《RAG 已死？不，是 Grep 回归了》

- 路径：`E:\work\gongzhonghao_md\tengxunyun\RAG已死_不_是Grep回归了_.md`
- 相关性：部分相关（核心主题是检索架构选择，token 成本控制是其中一章）
- 核心观点：代码搜索场景 Claude Code/Codex 选择零索引 + LLM 驱动 Grep；针对「Grep 烧 token」的批评，给出三层成本控制机制。
- 关键证据：
  - 4.4 节：Milvus 批评 Grep 烧 token（实测 14 次调用 / 32.2k token / 59.3s）；Claude Code 三层应对——① prompt cache（相邻轮 92% 前缀相同，实测降本约 81%，system prompt 分块标缓存）② auto-compaction（接近窗口上限时 LLM 摘要替换旧历史）③ 子 agent 隔离搜索结果（仅精炼结论回主对话）。
  - LSP（v2.0.74）用「go to definition」替代部分 Grep+read，实测 -40% token；社区 Beacon 插件用 hooks 拦截 Grep 换混合搜索。
  - 注意：文中明确「三层机制都是通用工程手段，embedding 方案同样可用」——即这些降 token 手段不限于 Grep 路线。

### 《Agent 烧钱如流水：Agentic OS (ANOLISA) 帮你逐笔看清 Token 账单》

- 路径：`E:\work\gongzhonghao_md\aliyun\Agent_烧钱如流水_Agentic_OS_(ANOLISA)_帮你逐笔看清_Token_账单.md`
- 相关性：部分相关（主体是 token 可观测，含一个降本工具包）
- 核心观点：「要省无效 token，前提是先看见 token 花在哪」——提供 AgentSight 做会话 / 对话 / 模型级 token 消耗分析，并附 Tokenless 降本工具包。
- 关键证据：
  - 可观测能力：AgentSight 面板 / CLI（`agentsight token`、`audit`、`discover`）查看 token 明细、定位主要消耗环节。
  - 降本部分（占比小但是真方法）：v0.2 新增「Tokenless 优化工具包，通过模式压缩、响应压缩及命令重写三大核心策略，降低上下文窗口的 Token 消耗」；Dashboard「Token 节省」面板可看已省 token 数与优化前后对比（对 MCP 响应内容压缩、保持语义）。
  - 局限：文章主体是部署教程 + 账单可视化，对 Tokenless 三策略未展开方法细节。

## 排除或低相关资料

下列文章关键词与 token / 成本 / 上下文高度重叠，但经主题校验，其**核心贡献不是「降低 Agent token 消耗的方法」**，故排除或归为低相关：

| 文章名 | 原因 |
| --- | --- |
| 阿里云 AI 网关 FinOps 能力正式上线丨让每一个 Token 的消耗都看得见管得住 | 主题是 token 计量 / 成本治理 / 预算管控（FinOps 看得见管得住），是「省钱前提」而非降 token 方法；无降本技术手段（聚焦检索词无命中） |
| 从架构到代码：深入理解 OpenClaw 的双源记忆系统 | 主题是记忆系统架构（双源记忆 / Memory Flush / compaction 机制）；token 仅在附录二「token 消耗的计算」做构成解释，未提出降低方法 |
| 4 亿 token 买来 5 个教训：让 6 个 AI Agent 连写 4 天代码 | 「4 亿 token」只是规模背景；正文讲多 Agent 稳定运行的运维教训（保护措施、故障驱动迭代、别信工具数字），非降 token 方法 |
| 拒绝「感觉有效」：用数据证明 AI Coding 的真实团队价值（天猫 AI Coding 系列） | 主题是 AI Coding 价值 / ROI 度量；「Token 成本追踪」是度量维度（按 Task/迭代/需求聚合统计），目的是评估投入而非降低消耗 |
| 如何避免「烧光 Token 还出错」：OpenClaw 日志 × AnalyticDB Trace 诊断实战 | 主题是日志诊断 / 可观测排障，标题虽含「烧光 Token」但讲的是问题定位，非系统性降 token 方法 |
| 告别「黑箱」养虾：腾讯云可观测平台给你的 OpenClaw 装上「透视眼」 | 主题是 Agent 可观测 / Trace；token 仅作为被观测指标之一，非降本方法 |
| Agent 从「能用」到「管好」中间差了什么 | 主题是 Agent 治理 / 可观测 / 上线管控；token 是治理维度之一，非降本方法 |
| 其余按相关性排序未进入精读的候选（约 100 篇） | 多为 Harness 工程、Agent 架构、Skill 设计、记忆系统、Code Review、可观测、产品发布类文章，仅顺带出现 token/成本/上下文等词，核心主题与「降低 token 消耗」不一致。未逐条列出（Graphify/CodeGraph、Cursor/Codex 各家具体做法等已在精读文章内被覆盖引用） |

## 不确定性

- **召回完整性**：本报告基于关键词高召回搜索 + 标题/内容定位，不承诺「绝不遗漏」。约 100 篇低相关候选未逐篇全文阅读，理论上其中个别文章可能含未被标题/检索词暴露的降 token 段落（尤其 Harness 工程类长文常顺带讨论成本）。已读 8 篇覆盖了主流角度（使用习惯 / 缓存 / 压缩 / 卸载 / 配置 / 图谱 / 检索 / 可观测），但不等于穷尽所有方法。
- **跨号重复**：《腾讯云 Agent Memory 节省 61%》在 `tengxunyun` 与 `tengxuntech` 两目录均存在，经核对正文实质相同（仅 frontmatter/少量字符差异），本报告按一篇计入精读，路径以 tengxunyun 为主并标注转载。
- **ANOLISA / RAG 已死的归类**：二者归为「部分相关」是判断性结论。ANOLISA 主体是 token 可观测，降本仅一个工具包（Tokenless）且未展开细节；《RAG 已死》主体是检索架构，降 token 是其中一章。若按「核心贡献必须是降 token」从严判定，两者可下调为低相关；本报告保留为部分相关，因其确含可操作的降 token 机制。
- **数据口径**：各文实测压缩率 / 节省比例来自不同作者、不同测试集与估算方式（部分混用 token 与字符口径，如《Token 成本控制》RTK 表已自注），横向数字不宜直接比较，应视为方向性参考而非精确基准。
- **结论时效**：资料涉及具体产品版本、价格倍率、源码行为（如 Claude Code 缓存有效期、LSP 版本、API beta 标志），均有时效性，随产品迭代可能变化。
