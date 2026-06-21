---
name: workflow-code-generation
description: 代码文件修改的统一入口与执行引擎。任何代码变更（新功能、优化、Bug 修复、重构）必须首先调用此 skill。它按复杂度路由：极轻改动（单文件局部、改一行级）主会话直接改；中等及以上下放 agent 执行（单 agent，或多 task 无依赖时并行分波，worktree 隔离），设计与 tasks.md 经用户批准后自主连跑、不逐 task 停等，每个产物过 workflow-code-review + verify.py，末尾一次性汇总 + intent 沉淀。仅适用于代码文件（.cc/.cpp/.h/.go/.py 等），改 .md 等非代码文件不需要调用。
---

> 输出一行：`Using workflow-code-generation`

# 代码生成（统一执行入口）

> 所有代码修改的统一入口。**先加载规范，再写代码。** 前期设计门（需求 / 设计 / tasks 批准）与质量基建（多维 review + verify + intent 沉淀）是地基；执行形态按复杂度路由：**极轻改动主会话直改，中等及以上下放 agent 执行（单 / 并行），自主连跑不逐 task 停等。**

## 执行形态总览

| 复杂度 | 执行形态 | 前置 |
| --- | --- | --- |
| **极轻**（单文件、局部、改一行级） | **Fast-Path**：主会话直接改 | 免 spec / tasks |
| **中等及以上**（多文件 / 多 task / 需设计） | **下放 agent 执行**，tasks 批准后自主连跑 | spec + tasks 批准 |

> 下放执行再分两形态：**单 task / 串行依赖** → 单 agent 逐波；**多 task 无依赖** → 并行分波。两者同一套机制（worktree 隔离 + 每产物质量门 + 失败隔离 + 合并），只差波内并行度。

---

## 步骤 1：评估复杂度与路由

> ⚠️ **防御性检查**：如果无法明确回答「要改什么模块 / 文件」「要实现什么行为」「怎样算完成」三个问题中的任何一个，**立即停止**，调用 `workflow-requirements-clarification`。本 skill 不负责需求澄清。

路由判定：

- **极轻改动**（能在路由阶段确定完整文件列表，且只涉及 1 个文件的局部修改）→ 走 **Fast-Path**（主会话直接改）。
- **其余一切**（多文件、需要 spec、可拆成多 task）→ 走**标准流程**（下放 agent 执行）。

> **无法确定 → 标准流程。** 执行中发现 Fast-Path 改动外溢到多文件 → **立即退出 Fast-Path**，转标准流程。

---

## Fast-Path（极轻改动，主会话直接改）

主会话直接修改，不起 agent / worktree（改一行级别下放反而绕）。**不走 tasks.md 状态机 / 测试环 / 续跑那套——那些是下放执行（中等+）的机制；** 极轻改动只做下面几步。

0. **采集基线（仅当存在 `verify.config.json`）**：动代码前加载 `workflow-verification`，运行 `verify.py --save-baseline .verify/baseline.json`；无配置则跳过。
1. 加载编码规范（同步骤 4）。
2. 实现改动。
3. 执行中发现需改多个文件 → **立即退出**，转标准流程。
4. 询问用户是否需要 code review：
   - **需要** → 加载 `workflow-code-review`（`skip_reviewers: [magical-prompt-reviewer]`）→ 修复循环。
   - **不需要** → 跳过，进入 4.5。
4.5. **门禁验证（仅当 `verify.config.json` 或 `.verify/baseline.json` 其一存在）**：加载 `workflow-verification`。
   - `.verify/baseline.json` 存在 → `verify.py --baseline .verify/baseline.json`（config 不存在时脚本报 ERROR）
   - 仅 `verify.config.json` 存在 → `verify.py`
   - 退出码 0 进入下一步；1（新增违规）修复后重跑；2（门禁故障）**停止交付**，排查 config / 工具 / 基线后再跑。**门禁通过前禁止汇报完成。**
4.6. **交付前沉淀检查（🚨 强制，与 verify 门禁无关）**：无论是否存在 `verify.config.json` 都强制执行。加载 `project-knowledge`，**逐条对照其沉淀检查信号表**（架构决策 / 放弃方案 / 新红线约束），每行明确「命中 → 已沉淀到 <具体 ADR / 章节>」或「未命中」，**禁止用一句笼统的「无需沉淀」代替逐条判定**；命中则写或更新 ADR 后再继续。**未给出逐条判定结论前，禁止宣布完成。**
5. 输出改动说明（含沉淀判定结论），**结束**。

---

## 标准流程

### 步骤 2：查找 / 确认 spec

查找 `docs/design-docs/<module>/<feature>/spec.md`：
- 存在且完整 → **仔细通读全文**（不要只读关注章节），确认理解。
- 存在且状态为 `Quick Draft` → 检查是否含问题、目标、核心方案、关键接口 / 数据模型（如适用）和验收标准；满足则进入任务规划，否则调用 `workflow-quick-design` 补齐。
- 不存在 / 不完整 → **调用 `workflow-requirements-clarification`**（禁止自行澄清）。

**强制**：`spec.md` 与 `tasks.md` 同时存在时，编码前必须完整读取两者。

### 步骤 3：检查 / 创建 tasks.md

- **已存在** → 进入步骤 4。
- **不存在** → **先读取** [reference/task_planning_guide.md](reference/task_planning_guide.md)，严格按其流程创建 `tasks.md`。每个 task 须带 `depends_on` 依赖、context（直接修改文件 + 上游 + 下游）、可机械执行的验收标准——**`depends_on` 是后续分波并行的依据，必须填**。

创建 / 更新 `tasks.md` 时，如本次改动可能涉及不可逆 / 高影响的架构决策、放弃某方案或新增红线约束，加载 `project-knowledge`，预留一个「intent 沉淀」任务（最终在步骤 6 收口）。

> 🚨 **创建 tasks.md 后必须停下来等用户确认。** 展示任务列表（含依赖关系），**停止并等待用户回复**。这是**人把关的最后一道闸**；批准后执行段自主连跑、不再逐 task 停。

### 步骤 4：加载编码规范（🚨 强制前置）

> **未加载规范就写代码 → 立即停止，先加载。** 下放 agent 时，须把规范要点写进 agent 的 prompt，或令其自行加载对应 skill。

| 规范 | 何时加载 |
| --- | --- |
| `bp-coding-best-practices` | 必须 |
| `bp-performance-optimization` | 必须（所有代码都性能敏感） |
| `std-cpp` / `std-go` / `std-python` | `.cc/.cpp/.h` / `.go` / `.py` 文件 |
| `bp-distributed-systems` | 网络通信 / 多节点协调 / 一致性 / 故障恢复 |

### 步骤 5：下放 agent 执行（🚨 批准后自主连跑）

tasks.md 经用户批准后，**执行下放给 agent，主会话只编排，不亲自写代码、不逐 task 停等**，全部跑完一次性汇总。单 task 就是「1 波 1 agent」，多 task 无依赖就并行分波——同一套机制。

#### 编排模型（按 CLI 嵌套能力二选一，先判定）

`workflow-code-review` 自身要派 reviewer 子 agent。**子 agent 能否再派子 agent**（嵌套 dispatch）决定 review/verify 跑在哪层，不同 CLI 支持不同。

- **快速实测**：派一个子 agent 让它尝试再派一个孙 agent 回一句话；成功即支持。
- **已知**：Claude Code **支持**嵌套（较新版本起；具体版本号与来源见 `docs/03-parallel-execution-mode.md`，可能随 CLI 更新而变）；**最终以上面的快速实测为准。**
  > ⚠️ **嵌套深度上限 5 层**（固定、不可配置；第 5 层子 agent 不再获得 `Agent` 工具）。模式 A 链深 3 层（主 agent → owner → reviewer），距上限尚余 2 层；不要设计更深的派生链。

- **模式 A — 嵌套支持（默认，Claude Code）**：每 task 派一个 **owner 子 agent**，在自己的 worktree 内**自闭环**完成：实现 → 加载 `workflow-test-generation`（**内嵌 / 无人值守路径，不停等确认**）写 + 跑测试（与实现同批）→ 自跑 `workflow-code-review`（派 reviewer 孙 agent）→ 自跑 `verify.py` → 有限轮次自修复 → 返回「通过 / 需人工 + 报告」。主 agent **不亲自 review**。
- **模式 B — 嵌套不支持（兜底，其他 CLI）**：implementer 子 agent **实现 + 写 / 跑测试**（`workflow-test-generation` 走内嵌 / 无人值守路径，与实现同批）；review 与 verify 由**主 agent**对每个产物逐一执行（扮演 `workflow-code-review` 的 Judge 派 reviewer）。

#### Phase 0：准备

1. **加载编码规范**（步骤 4 已做）。
2. **采集验证基线（仅当根目录存在 `verify.config.json`）**：加载 `workflow-verification`，运行 `verify.py --save-baseline .verify/baseline.json`，并**记下基线的主仓库根绝对路径**（`<repo-root>/.verify/baseline.json`）——worktree 基于 HEAD 新建、看不到这个未提交（通常已 gitignore）的基线文件，Phase 1 必须用绝对路径引用它。
   > ⚠️ 信任前提：`verify.config.json` 的命令会以 shell 执行。自己的仓库可直接跑；处理外部分支且 config 含未审查变更时，**先人工确认命令安全**再执行。无 config 则跳过。
3. **构建依赖波（wave）**：读每个 task 的 `depends_on` 做拓扑分层——同波内 task 互不依赖、可并行；后波依赖前波产物、串行等前波合并完成再开始；**缺 `depends_on` 无法判断依赖 → 保守串行或回问，禁止对未知依赖直接全并行**。单 task 即单波。

#### Phase 1：逐波执行（波内并行，波间串行）

对每个 wave：

> 🗂 **tasks.md 是进度真相源**：每个 task 的 `状态:` 字段实时写回（合法值 `未开始` / `进行中` / `完成` / `需人工` / `阻塞`）——dispatch 标 `进行中`、合并成功标 `完成`、失败 / 冲突标 `需人工`（附原因 + 失败输出）、上游未合并的下游标 `阻塞`。下面各步动作完成即更新，**中断后靠它定位续跑**。

1. **dispatch 子 agent**：波内每个 task 派一个子 agent（模式 A 为 owner、模式 B 为 implementer），各自在**隔离 git worktree**（基于当前分支 HEAD）工作，受并发上限约束、超出排队。多个子 agent **在同一条消息里并行派发**。
   - worktree：用 Agent 工具的 `isolation: "worktree"`，或手动 `git worktree add -b <task-branch> <path> HEAD`。
   - prompt 公共部分：task 描述 + context（直接修改文件 + 上游 + 下游）+ `spec`/`tasks` 摘要 + 编码规范要点 + worktree 路径 + 「只在此 worktree 内改、改完提交」。
   - 职责边界：**模式 A** 令其自闭环（实现 → 加载 `workflow-test-generation`（内嵌路径，不停等确认）写 + 跑测试 → 加载 `workflow-code-review`（`skip_reviewers: [magical-prompt-reviewer]`）→ 跑 `verify.py` → 有限轮次（建议 ≤ 2）自修复 → 返回结论）；**模式 B** 令其实现 + 写 / 跑测试（`workflow-test-generation` 内嵌路径）。
   - **测试与实现同批交付**：接口层与核心逻辑必须有能跑通、覆盖关键路径的测试，不允许先实现后补。
2. **质量门**：
   - **模式 A**：质量门已在 owner 内跑完，主 agent 只**收集**结论。
   - **模式 B**：主 agent 对每个产物（在其 worktree 内）扮演 `workflow-code-review` 的 Judge 派 reviewer（`skip_reviewers: [magical-prompt-reviewer]`）→ 裁决。
   - **verify 门禁（两模式一致，仅当 `verify.config.json` 或 Phase 0 已采基线时启用）**，在产物所在 worktree 内：
     - Phase 0 采过基线 → `verify.py --baseline <repo-root>/.verify/baseline.json`（**用主仓库根绝对路径**，不要用 worktree 内相对路径——worktree 看不到它，会让基线对比被静默跳过、清零「测试数不得减少」等防回退检查；对比之下 Fast-Path 在仓库根原地运行、不进 worktree，故那里用相对路径即可）。绝对路径不可达时按门禁故障（ERROR）处理，**不得**静默退回无基线路径。
     - Phase 0 未采基线但有 `verify.config.json` → `verify.py`（无基线绝对校验）。
     - 退出码 0 过；1（新增违规）回修；2（门禁故障）停止交付、排查后重跑，不当作新增违规改代码。
3. **失败隔离**：**测试 / code-review / verify 任一不过** → 有限轮次（≤ 2）自修复后重跑（模式 A 在 owner 内、模式 B 由主 agent 派 fixer 在同一 worktree 修）；超过轮次上限仍不过、或子 agent 报告范围 / 依赖问题无法在本 task 内解决 → 在 `tasks.md` **标 `需人工` 并附原因 + 失败输出**（review finding / verify 报告 / 错误摘要）；**子 agent 崩溃 / 超时 / 无产物返回** → 标 `需人工` 注明「agent 未返回，需重 dispatch」。标 `需人工` 的 task **其 worktree 保留**供人工排查、不清理。以上**均不阻塞同波其他 task、不停整个流程**。
4. **合并**：波内通过质量门的 task，其 worktree / 分支**依次**合并回主分支（`git merge --no-ff <task-branch>`），合并成功即在 `tasks.md` 标 `完成`、清理该 worktree（`git worktree remove`）；冲突 → 标 `需人工`（记录冲突文件），**其 worktree 保留待人工**，跳过、继续合并其余。
   - **上游未合并 → 下游阻塞**：某 task 因失败 / 冲突标 `需人工` 后，**依赖它的后波 task 一并标 `阻塞`**（原因记「上游 Task N 未合并」）并跳过 dispatch——否则后波会 dispatch 在缺该产物的 HEAD 上，破坏「先建后迁后删可编译」。上游经人工解决并合并后，`阻塞` task 方可恢复。
5. **不停等用户**，进入下一波，直到所有波处理完。

> **现状类信息**（模块 / 接口 / 数据流怎么变）不沉淀——那是代码的职责。若本波某 task 引入值得沉淀的 intent，可趁热预留「intent 沉淀」任务，步骤 6 统一收口。

### 步骤 6：功能交付与 intent 沉淀（🚨 强制，全部 task 完成后触发）

全部 wave 处理完、`tasks.md` 所有任务为 `完成` / `需人工`（或 `阻塞`）时，**禁止直接宣布交付**，先走本步骤：

1. **汇总报告**（一次性，不逐 task）：每个 task 的实现 / review / verify 结果，列出哪些「需人工」（附原因）、哪些 `阻塞`（附上游归因，如「上游 Task N 未合并」）、哪些合并冲突。
2. **交付前沉淀检查**：加载 `project-knowledge`，**逐条对照沉淀检查信号表**，对每个信号逐行作答「命中 → 已沉淀到 <具体 ADR / spec 章节>」或「未命中」——单句笼统的「无需沉淀」不构成有效判定；命中则写或更新 ADR，并逐条核销步骤 3 / Phase 1 预留的「intent 沉淀」任务。
3. **归档**：按 `project-knowledge` 约定把 `spec.md` 头部 `状态` 改为 `Archived`（文件原地保留）。
4. 交付，等用户验收「需人工」/ `阻塞` 项的处理。

> 🚨 **强制发生**：未给出显式逐条沉淀判定结论前，不得宣布功能交付完成。沉默 = 未完成。判定需沉淀但当前无法完成时，在 `tasks.md` 建「intent 沉淀」任务，不要跳过。

---

## 🚨 强制规则

1. 极轻改动外的一切，未经 spec + `tasks.md` 用户批准，**禁止**进入下放执行。
2. 有依赖的 task **禁止**放进同一波并行；依赖信息缺失时保守串行或回问。
3. 每个产物**必须**过 `workflow-code-review` + `verify.py`（若启用），合并前必须通过，不得跳过。
4. 单 task 失败 / 不过 / 冲突**必须**标记「需人工」，不得静默丢弃或假装通过，也不得因此停掉其他 task；**依赖某 `需人工` task 的后波 task 必须标 `阻塞` 并跳过 dispatch**，不得在缺上游产物的 HEAD 上下放（上游合并后方可解阻）。
5. 收尾**必须**做 intent 沉淀检查并给出逐条结论。
6. 嵌套派生链控制在主 agent → owner → reviewer 3 层内，不触达 5 层上限。
7. **下放执行**的每个 task，**测试与实现同批交付**：接口层与核心逻辑必须有能跑通、覆盖关键路径的测试，不允许先实现后补（要让「测试不得偷删」也成门禁，项目可在 `verify.config.json` 配 count + not_decrease 的测试数检查）。Fast-Path（极轻改动）不强制写测试。
8. **进度表述校准**：「已查看 / 已核对」只用于读取核对；「已开始 / 进行中」只用于已 dispatch agent 或已改代码；「已完成」只用于结果已落地且已合并核对。禁止把「看过」说成「已开始」、把「想过」说成「在推进」。

## 用户跳过 spec 时

必须生成简化版 spec.md（标注 `状态: Quick Draft`）。**禁止无 spec 修改中等+代码。** 该路径交付前同样受步骤 6 约束。

## 恢复中断的任务

`tasks.md` 是进度真相源，续跑三步：

1. **读 `tasks.md` 定位**：找状态为 `进行中` / `未开始` / `阻塞` 的 task；`进行中` 的优先（上次很可能中断在它身上）；`阻塞` 的先看上游是否已合并，已合并则解阻。
2. **处理 worktree 残留**：`git worktree list` 列出 worktree，按分支名 `<task-branch>` 回连 tasks.md 的 task——
   - 对应 `进行中` task：**先 `git branch --merged <主分支>` 核对该分支是否已并入主分支**（防中断在「已合并未标完成」窗口）；已合并 → 直接标 `完成`、清理，不重跑；未合并 → 核对产物是否过质量门，过了就合并标 `完成`，没过就重跑质量门或重新 dispatch。
   - 对应 `需人工` task：**保留不动**（供人工排查）。
   - 分支名回连不到任何 task 的废弃 worktree：清理掉。
3. **重新加载编码规范 → 重建依赖波 → 继续下放执行**，直至全部 task 为 `完成` / `需人工` / `阻塞`（`阻塞` 项须待其上游经人工解决后，下次续跑再处理，本身即可接受终态）。

**最后必须进入步骤 6 执行交付前沉淀检查、给出逐条判定结论，再宣布交付——恢复路径不豁免步骤 6。**

## 与其他 skill 的关系

本 skill 是所有代码修改的统一入口。`workflow-verification`（verify 门禁）、`workflow-code-review`（多维评审）、`project-knowledge`（intent 沉淀）是它调用的质量基建；`workflow-test-generation` 内嵌在每个 task 的执行流程中（实现后即写 / 跑测试，与实现同批）。设计阶段由 `workflow-requirements-clarification` / `workflow-system-design` / `workflow-quick-design` 承担。
