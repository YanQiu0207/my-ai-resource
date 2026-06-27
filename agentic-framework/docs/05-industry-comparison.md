# 业界框架横向对比

> 本文在 `02-tool-landscape.md`（Superpowers 深度对比）和 `04-compound-engineering-comparison.md`（ce-compound 对比）基础上，补充 OpenSpec、Spec Kit、Taskmaster 的对比，形成完整的横向视图。
>
> **置信度说明**：Superpowers 和 ce-compound 经过联网深度调研；OpenSpec、Spec Kit、Taskmaster 来自工具文档 + 公开描述，置信度中等，细节以实际使用为准。

---

## 一句话定位

| 框架 | 定位 | 核心解决什么问题 |
|---|---|---|
| **本框架** | 快速构建大型非生产工具的 AI 工程方法论 | 结构与速度的平衡：前重设计门 + 执行段自主并行 |
| **Superpowers** | 编码 agent 的完整开发方法论（通用） | 执行段自主并行 + subagent-driven + worktree 隔离 |
| **OpenSpec** | 轻量规格协议，给承重决策做结构化文档 | AI agent 行为规格的标准化表达 |
| **Spec Kit** | GitHub 官方工程规范工具包（生产偏向） | 需求→设计→实现的标准化四步路径 |
| **Taskmaster** | PRD→带依赖任务清单的自动化拆解工具 | 复杂任务的结构化拆解与追踪 |
| **compound-engineering-plugin** | 工程经验即时沉淀工具 | 把解决问题的过程知识固化为可复用资产 |

---

## 维度对比

### 工作流完整性

| 维度 | 本框架 | Superpowers | OpenSpec | Spec Kit | Taskmaster |
|---|---|---|---|---|---|
| 需求澄清 | ✅ workflow-requirements-clarification | ✅ brainstorming（设计硬门） | ❌ 无 | ✅ 四步路径第一步 | ⚠️ 依赖输入 PRD |
| 系统设计 | ✅ system-design / quick-design | ✅ writing-plans | ⚠️ 核心定位（规格文档） | ✅ 第二步 | ❌ 无 |
| 任务拆解 | ✅ tasks.md（用户批准） | ✅ writing-plans（2-5 分钟小任务） | ❌ 无 | ✅ 第三步 | ✅ 自动拆解（核心功能）|
| 并行执行 | ✅ DAG 分波 + worktree 隔离 | ✅ dispatching-parallel-agents | ❌ 无 | ❌ 无 | ❌ 无 |
| 代码评审 | ✅ 分级多维（3档 / 5+1 agent） | ⚠️ 单 reviewer subagent | ❌ 无 | ✅ 有质量门（偏静态检查）| ❌ 无 |
| 客观门禁 | ✅ workflow-verification（零配置机器门，探测 build/test） | ❌ 无 | ❌ 无 | ✅ CI 集成（生产向） | ❌ 无 |
| 知识沉淀 | ✅ ADR + arch-snapshot + spec 归档 | ❌ 无 | ⚠️ 规格本身即沉淀 | ⚠️ spec 文档 | ❌ 无 |

### 执行自主性

| 框架 | 执行节奏 | 人工干预点 |
|---|---|---|
| 本框架 | tasks 批准后自主连跑 | 需求→设计→tasks 批准；收尾汇报 |
| Superpowers | brainstorm 批准后自主连跑 | 设计批准；完成后 code review |
| OpenSpec | 无执行引擎，只是规格协议 | — |
| Spec Kit | 按步骤推进，每步有人工节点 | 四步各有审批点 |
| Taskmaster | 有任务清单，但无强制审批 | 可选干预，无强制门禁 |

### 质量基建深度

| 框架 | review 机制 | 验证机制 | 对抗性验证 |
|---|---|---|---|
| 本框架 | 3档位 × 5维度 reviewer + critic judge | ✅ workflow-verification（零配置 build/test 机器门） | ✅ review-critic 专项驳斥 |
| Superpowers | 单 reviewer subagent | ❌ 无 | ❌ 无 |
| OpenSpec | ❌ 无 | ❌ 无 | ❌ 无 |
| Spec Kit | 有质量门（以静态检查为主） | ✅ CI 集成 | ❌ 无 |
| Taskmaster | ❌ 无 | ❌ 无 | ❌ 无 |

---

## 各框架的核心优势与短板

### Superpowers

**强在**：执行形态最完整——并行 dispatch、worktree 隔离、subagent-driven、TDD 强制。这是本框架执行段的直接原型。

**弱在**：
- 无分级 review（单 reviewer，质量深度不足）
- 无知识沉淀机制（每次探索成本全归零）
- 无 Fast-Path（所有改动都走完整流程）

**适用场景**：通用 AI 辅助开发，对质量深度要求中等、更看重执行速度的场景。

---

### OpenSpec

**强在**：
- 专注规格表达，是轻量的「行为规范协议」
- 给 AI agent 的行为约束提供结构化载体（YAML 前置 + markdown 正文）
- 对「承重决策」做最小化但足够结构化的文档

**弱在**：
- 不是工作流框架，无执行引擎
- 无代码评审、无验证、无知识沉淀
- 本质上是「规格格式标准」，需要搭配其他工具才能形成完整工作流

**与本框架的关系**：OpenSpec 解决的是「如何写规格」；本框架解决的是「如何把规格转化为高质量实现」。可以组合：用 OpenSpec 格式写 spec.md，本框架驱动执行。

**不采用原因**（来自 `02-tool-landscape.md` 的选型逻辑）：本框架维护 workflow-* 自己的 spec 格式，OpenSpec 的格式标准化对非跨团队场景收益有限；且本框架明确不维护「现状规范库」，而 OpenSpec 的定位偏向中央规范库。

---

### Spec Kit（GitHub）

**强在**：
- GitHub 官方背书，与 GitHub Actions / PR 流程深度集成
- 四步路径（需求→设计→实现→review）有成熟的工程实践沉淀
- 质量门与 CI 集成，适合生产系统

**弱在**：
- 偏生产气质，完整路径三道质量门——速度不够快
- 无 AI 自主并行执行引擎
- 无 AI 驱动的多维代码评审
- 知识沉淀主要靠 PR 描述和 spec 文档，无结构化的 intent 沉淀机制

**适用场景**：生产系统的团队协作开发，需要与 GitHub 生态深度集成的场景。

**与本框架的关系**：定位和目标用户基本不重叠——Spec Kit 为生产协作而生，本框架为快速构建大型非生产工具而生。

---

### Taskmaster

**强在**：
- PRD→带依赖关系任务清单，自动拆解是核心价值
- 任务依赖追踪成熟，适合有复杂依赖关系的大型任务集

**弱在**：
- 无强制质量门（review / verify 均无）
- 无需求澄清、系统设计阶段
- 无知识沉淀
- 任务拆解质量依赖输入 PRD 的质量

**与本框架的关系**：Taskmaster 解决「把 PRD 拆成可执行 tasks」这一步，本框架的 tasks.md 也做这件事但更轻量、且包含前后两端（需求澄清 + 质量门）。可以将 Taskmaster 作为 tasks.md 的生成工具，但额外引入一个工具的复杂度收益存疑。

---

### compound-engineering-plugin（详见 doc 04）

**强在**：解决问题时即时沉淀（上下文最新鲜），Overlap Detection 防碎片化。

**弱在**：沉淀对象是「解决问题的过程知识」，不是「系统架构理解」或「决策 intent」——定位不同。

**已吸收的点**：ADR 即时触发原则、「放弃的方案」独立成节、「适用条件」字段。

---

## 综合定位图

```
                    执行自主性
                    高 ↑
                    │
         Superpowers │ 本框架
         (执行强,    │ (执行强 + 质量深
          质量中)    │  + 知识沉淀)
                    │
────────────────────┼──────────────────── 质量深度
低                  │                   高
                    │
     Taskmaster     │   Spec Kit
     (任务拆解,     │   (质量门完整,
      无质量门)     │    执行非自主)
                    │
                    ↓ 低
```

**结论**：本框架在「执行自主性 × 质量深度」的二维象限上占据右上角，这个位置目前没有现成工具直接竞争——Superpowers 偏左（质量深度不足），Spec Kit 偏下（执行非自主）。代价是复杂度最高，不适合轻量场景。

---

## 来源盲区（诚实标注）

- OpenSpec 的完整功能集来自公开文档摘要，未深度调研，部分描述可能不准确
- Spec Kit 「三道质量门是否为硬阻断」未确认（来自 `02-tool-landscape.md` 标注的盲区）
- 各框架的活跃维护状态、版本号未实时核对，以实际安装版本为准
- 以上对比基于 2026-06 公开信息，框架迭代较快，建议定期复核
