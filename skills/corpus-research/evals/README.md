# corpus-research 评测套件

三层评测,守护这个 skill 不退化。对接 `E:\work\skill-evolution\skill-evolver-fork` 的评测框架,但每层都能独立运行。

## 三层概览

| 层 | 评什么 | 文件 | 是否需真跑 skill | 是否需 LLM |
| --- | --- | --- | --- | --- |
| **A 静态规则** | SKILL.md 是否保留关键规则 | `evals.json` | 否 | 否 |
| **B 行为召回** | 真跑后是否漏召回 / 误纳文章 | `behavior_gt.json` + `checks/check_recall.py` | 是 | 否 |
| **C 事实覆盖** | 报告是否覆盖关键事实 | `behavior_gt.json::key_facts` + `checks/check_facts.py` | 是 | 否(锚词近似) |

设计依据:`skill-evolver-fork/.../references/eval_strategy.md`——「LLM 只做二分类,程序算分」。本套件把能确定性判的全部脚本化,LLM 一概不用。

## A 层：静态规则守护（零成本，随时跑）

评测对象是 **SKILL.md 全文(静态文本)**,不执行 skill。用 skill-evolver 的 `LocalEvaluator` 跑 `evals.json` 里的 contains/regex 断言。

```bash
# 在 skill-evolver-fork 的 scripts 目录可 import LocalEvaluator，示例：
python - <<'PY'
import sys; sys.path.insert(0, r"E:/work/skill-evolution/skill-evolver-fork/plugin/skills/skill-evolver/scripts")
from evaluators import LocalEvaluator
from pathlib import Path
skill = Path(r"E:/work/my-ai-resource/skills/corpus-research")
gt = skill / "evals" / "evals.json"
ev = LocalEvaluator()
for split in ("regression", "dev", "holdout"):
    r = ev.full_eval(skill, gt, split=split)
    print(split, r["total_passed"], "/", r["total_assertions"])
PY
```

`regression` split 守护 2026-06-27 新增的三道防护(主题校验 / 对等笔记 / 密度均衡),被未来迭代删掉会立刻报红。

## B 层：行为召回（需先真跑 skill 得报告）

直击「不能遗漏重要知识」。流程:

```
1. 真跑 corpus-research 处理某个 case 的 question → 把报告存成 report.md
2. python checks/check_recall.py <report.md> <case_id>
3. 召回率 <100% 或有误纳 → 未达标（exit 1）
```

例:

```bash
export PYTHONIOENCODING=utf-8   # Windows 防中文乱码
python checks/check_recall.py fixtures/skill-eval-report.md skill-eval-methods
```

判定区是报告的「## 相关文章 / ## 单篇摘要」区,叙述区(综合 / 不确定性)里顺带提到的文章名不算召回——避免否定语境误判。

## C 层：事实覆盖（需报告，确定性锚词法）

验证报告有没有覆盖关键事实(如「5 维 AND 门控不是加权求和」)。

```bash
python checks/check_facts.py <report.md> <case_id> [min_coverage]
# 默认 min_coverage=1.0，要求全覆盖
python checks/check_facts.py fixtures/skill-eval-report.md skill-eval-methods 0.8
```

锚词法是 `fact_coverage` 的确定性近似——同义改写不算覆盖。要语义级判断,改用 skill-evolver 的 `fact_coverage` Preset 模式(LLM 二分类)。

## 逐 case 真跑 SOP（换 LLM / 新会话照抄即可）

剩余待跑 case：`skill-evolver-focus`、`rubric-vs-exam`、`skill-security`、`agentic-engineering`、`multi-agent`、`build-agent`。

对每个 case 走四步：

**第 1 步·取 question**：在 `behavior_gt.json` 里找到该 `case_id`，读它的 `question` 字段。

**第 2 步·真跑**：派一个**能写文件的子 agent**（如 general-purpose），**绝不把 GT / must_recall 给它**（三角色分离，执行者不可见答案）。用下面的 prompt 模板，替换 `{QUESTION}` 和 `{CASE_ID}`：

```
你要严格按一个技能的指导独立执行一次资料库研究，我不会给你答案。
1) 完整阅读 E:/work/my-ai-resource/skills/corpus-research/SKILL.md，
   理解其流程与全部规则（相关性判断、主题校验、报告结构、质量门禁）。
2) 按该 SKILL.md 流程，针对问题做高召回研究：
   - 问题：{QUESTION}
   - 资料库：E:/work/gongzhonghao_md（递归，纳入 .md）
   - 主题校验：关键词重叠 ≠ 主题相关，必须确认文章核心对象就是问题所指对象。
   - 相关 / 部分相关文章逐篇读全文（≤ 15 篇），笔记对等详尽，不凭印象压缩。
3) 按 SKILL.md 报告结构，用 Write 写到（UTF-8）：
   E:/work/my-ai-resource/skills/corpus-research/evals/fixtures/{CASE_ID}-report.md
   必含章节：## 结论、## 覆盖范围、## 相关文章（表格）、## 综合总结、
   ## 单篇文章摘要、## 排除或低相关资料（表格）、## 不确定性。
完成后回报：哪些判相关、哪些排除及各自理由（尤其关键词重叠但主题不同的）。
```

**第 3 步·评测**（在 `evals/` 目录下）：

```bash
export PYTHONIOENCODING=utf-8
python checks/check_recall.py fixtures/{CASE_ID}-report.md {CASE_ID}
python checks/check_facts.py  fixtures/{CASE_ID}-report.md {CASE_ID}
```

**第 4 步·未达标时怎么改**：
- **误纳**（should_not_include 命中）→ 多半是 skill 主题校验不够，值得改 SKILL.md。
- **漏召回**（召回 < 100%）→ 先判是不是 GT 漏标：**亲自读那篇文章确认**它确实该召回，是则把它补进该 case 的 `must_recall`（配唯一锚词）后重跑；否则才是 skill 真漏，改 SKILL.md。
- 经验：前三次真跑（agent-eval / token-optimization / harness-engineering）漏召回基本都是 GT 漏标了「该主题最完整的那篇」，不是 skill 问题（见「已知边界」最后一条）。

## GT 怎么扩（behavior_gt.json）

当前 10 个 case,覆盖十种检索模式 / 主题:

| case_id | split | 模式 / 主题 |
| --- | --- | --- |
| skill-eval-methods | dev | Skill 评测·穷举罗列 |
| skill-evolver-focus | dev | Skill 评测·聚焦深挖(测过度召回) |
| rubric-vs-exam | dev | Skill 评测·对比 |
| skill-security | holdout | Skill 安全评测 |
| token-optimization | holdout | token 优化·跨主题 |
| harness-engineering | dev | Harness Engineering·概念组件 |
| agentic-engineering | holdout | Agentic Engineering·概念辨析 |
| multi-agent | dev | Multi-Agent 架构设计 |
| build-agent | holdout | 从零搭建 Agent |
| agent-eval | dev | Agent 评测(测与 Skill/模型评测的区分) |

加新 case 的铁律:**must_recall 必须基于真读过的文章标注,不能凭标题臆测**。每篇给唯一锚词(归一化后子串匹配,跨标点 / 空格)。`should_not_include` 放「关键词重叠但主题不同」的易混项(如 AACR-Bench、ROCK&ROLL)——这正是 skill 最容易误纳的。

## 已知边界

- A 层只能证明「规则文本还在」,不能证明「跑起来有效」——那是 B/C 层。
- B/C 层的第 1 步「跑 skill 得报告」必须真执行(花 token),框架不替你跑;`check_*.py` 只负责核对报告。
- 已有 4 份真实报告夹具:`skill-eval-methods`(手写基线)+ `agent-eval` / `token-optimization` / `harness-engineering`(**子 agent 真跑产出**)。其余 6 个 case 暂无夹具,按上面「逐 case 真跑 SOP」补。
- 真跑是发现 GT 盲区的有效手段,而且这是**反复出现的模式**:agent-eval 真跑召回了漏标的《AI Agent & Skill 测评方案及落地实践》,token-optimization 真跑召回了漏标的《一篇搞懂 Token 成本控制》——两次都是「该主题下最完整的那篇」被漏标。根因:扩 GT 时只看少量候选,会系统性漏掉最核心文章。结论:每个 case 至少真跑一次来校准 GT,别只靠候选清单标注。
