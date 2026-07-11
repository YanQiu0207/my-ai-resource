# 会话遥测体系：设计决策与演进路线

## 结论

框架的可监测性按三层演进，当前只落地第一层：**transcript 后处理**（`scripts/analyze_session_metrics.py`）。它不采集任何数据，只消费 Claude Code 与 Codex 本来就在落盘的会话记录，回溯重建每个工作流阶段的耗时、token、子 agent 成本和 review 结论轨迹。零运行时侵入，历史会话全部可回溯。

本文记录第一层的设计决策与指标解读边界，以及第二、三层的启动条件。脚本用法见 README 与脚本 docstring，本文不重复。

## 解决什么问题

- 「简单改动为什么耗时」这类问题此前只能靠感觉；排查 review 循环耗时问题时，全部证据都要临时手工翻 transcript。
- [10-harness-engineering-practices.md](10-harness-engineering-practices.md) 缺口 1「为执行过程增加轻量、结构化的运行指标」需要落点。
- [ADR 003](adr/003-review-fix-loop-convergence.md)（review 循环收敛）需要观测口验证「质量是否受损」：复审轮新增 P0/P1 比例、需人工率。

## 三层架构与当前落点

| 层 | 机制 | 状态 | 启动条件 |
|---|---|---|---|
| 1. transcript 后处理 | 手动跑脚本，解析已落盘会话数据 | ✅ 已落地 | — |
| 2. hooks 常态采集 | PreToolUse / PostToolUse / SubagentStop 等客户端 hook 实时写 `.phase-metrics.jsonl` | ⏳ 未做 | 第一层的启发式锚点被证明不够可靠，或需要实时指标时 |
| 3. OTel 聚合 | 官方遥测导出，跨项目仪表盘 | ⏳ 未做 | 有多项目横向对比诉求时 |

先做第一层的理由：唯一能覆盖**历史会话**的方案；第二、三层只对启用后的会话生效，且要配置维护。

## 第一层设计决策

### 数据源：复用落盘数据，不新建采集

两个 CLI 都已完整落盘：

- Claude Code：`~/.claude/projects/<proj>/<session>.jsonl`，每条 assistant 消息带 `usage`（四类 token）与时间戳；子 agent 转录在伴生目录 `<session>/subagents/`，`meta.json` 带 `agentType`，reviewer 成本可按类型归账。
- Codex：`~/.codex/sessions/<Y>/<M>/<D>/rollout-*.jsonl`，token 在 `event_msg/token_count` 事件里，`session_meta.cwd` 可按项目过滤（Codex 会话集中存放不分项目）。

**风险**：两者都是 CLI 内部实现格式，不是稳定 API，版本升级可能需要适配解析。这是第二层（hook 是官方接口）的存在理由之一。

### 阶段锚点：三类，且放弃 tool_result 里的标记

切阶段的锚点：assistant 正文的 skill 首行标记（`Using workflow-xxx`，两源通用）；Claude 额外识别 `Skill` 工具调用和 `<command-name>` 命令注入。

**踩坑记录**：最初把出现在任何位置的标记都当锚点，实测发现 skill 正文（含标记原文）会通过 Read 工具返回值、Skill 工具返回值大量进入上下文——某会话 grep 到 21 处标记，真正的 assistant 回显只有 1 处。故只认 assistant 主动输出与显式加载动作，**不认工具返回值**。

框架强制每个 workflow skill 首行输出标记，原本是给触发评估（[08-evaluation-strategy.md](08-evaluation-strategy.md) Tier 1）做确定性判据的，在这里兑现了第二个用途：阶段边界。

### Codex token：累计值差分，不直接累加事件

`token_count` 事件携带的 `total_token_usage` 是会话累计值。直接累加各事件的 `last_token_usage` 会被重复事件污染；取相邻事件累计值的差分，重复事件差分为 0，天然去重。

### 质量账：格式即接口

review 结论轨迹（`NEEDS_CHANGES(P1×5) → PASS`）的提取完全依赖 `workflow-code-review` 的固定报告格式（`# Code Review 报告` + `## 总体结论` + `P{n}-{seq}` 编号）。该格式是框架「整个系统唯一固定格式」，在这里兑现第二个用途：机器可解析的质量数据源。**改报告模板 = 改遥测接口**，动模板前先看本文。

### 其他口径

- **活跃时长**：相邻条目间隔之和，单个间隔超过 `--idle-gap`（默认 300 秒）的部分按「等用户」剔除，避免人离开把阶段耗时撑大。
- **费率不硬编码**：成本折算走 `--rates` 外部费率表，过期费率产出错误数字的责任不进脚本。
- **账本**：`--history` 按 (source, session) 去重追加，为「改 skill 前后对比」积累基线，衔接 08 号文档 Tier 2 效果评估的 trace 需求。

## 指标解读注意事项

- 「(未标记)」段 = 首个锚点前的全部活动（含纯对话），不代表异常。
- 内置命令（`/exit`、`/clear`）也是锚点，其后的闲聊会挂在该命令名下。
- Codex 会话子 agent 列恒为 0：Codex 不落盘子 agent 独立转录，是数据源限制不是脚本缺陷。
- Codex 侧若模型未按 skill 要求回显首行标记，该段归入「(未标记)」。
- fork 出来的 Codex 会话首个 token 差分可能含父会话累计量，账面表现为首条虚高。
- 子 agent 的 token 总量精确，但按启动时间整体归入启动时所处阶段，跨阶段运行的子 agent 不拆分；时间归属同为近似。

## 已产出的实测结论

- review 重的是 Judge 编排而非 reviewer 本身：一次 strict review 会话中主链 Judge 消耗 326k output token，7 个 reviewer 子 agent 合计仅 46.5k（约 7:1）。这是 ADR 003 砍「重复全量重审」而非砍 reviewer 数量的数据依据。
- 修复循环轨迹可直接观测：`NEEDS_CHANGES(P1×5) → PASS` 即一次两轮收敛的循环。

## 演进路线

1. **积累账本**：持续 `--history` 收数据，先观测 review 结论轨迹。「复审轮新增 P0/P1 比例」「需人工率」两个指标（ADR 003 的质量验证口）需扩展报告解析——区分首审 / 复审、识别需人工终态——**当前尚未实现**，是账本之后的第一优先扩展。
2. **第二层 hooks**：满足上表启动条件时再上；skill 首行标记可同步升级为结构化事件。
3. **第三层 OTel**：有跨项目对比诉求时评估。
