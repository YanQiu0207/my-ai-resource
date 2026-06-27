---
name: workflow-verification
description: 研发后机器验证门。有 verify.config.json 时配置驱动跑 build / test / lint 等客观检查 + 改动前后基线对比、只追新增违规；无配置时自动探测项目 build / test 兜底。merge 前与 LLM review 并列的硬门。workflow-code-generation 实现后判定「是否真做完」，或用户要求跑验证时使用。
---

> 输出一行：`Using workflow-verification`

# 研发后机器验证门

把「完成」从 LLM 说了算变成机器绿灯。机器能验的不靠 LLM 背书。

## 两种模式

- **有 `verify.config.json`（大多数项目）** → 配置驱动，`scripts/verify.py` 跑 + 基线对比。
- **没有** → 零配置兜底，自动探测 build / test 跑一遍。

## 配置驱动

三类检查（config 的 `type` 字段）：

| type | 判定 | 用途 |
| --- | --- | --- |
| `exit_code` | 退出码 == `expect_code` | 编译必过、测试必过、自定义校验脚本 |
| `forbid_pattern` | 命中的每行算一处违规 | 静态规范：禁用 API / 语法 / 硬编码 |
| `count` | stdout 解析为数字按方向比 | 测试数不减少、文件不超长 |

`baseline_aware: true` 的检查参与基线对比，**只判超出基线的新增违规**（历史遗留不阻塞）。`forbid_pattern` 命令用 `-H` 保留文件路径、不带行号。

用法（`<skill-dir>` = 本 skill 安装目录）：

```bash
# 改动前采基线
python <skill-dir>/scripts/verify.py --save-baseline .verify/baseline.json
# 改动后验证并对比
python <skill-dir>/scripts/verify.py --baseline .verify/baseline.json
```

退出码：`0` 全过 / 无配置；`1` 有新增违规（进修复循环）；`2` 门禁自身出错（先排查配置）。

配置项目：`cp <skill-dir>/reference/verify.config.example.json verify.config.json`，按技术栈改 `command`；`.verify/` 加进 `.gitignore`。**怎么写配置、怎么接入自己的脚本见 [reference/config-guide.md](reference/config-guide.md)。**

## 零配置兜底（无 config）

探测项目根标志文件跑对应命令：`package.json`→scripts 里的 build/test/typecheck/lint；`go.mod`→`go build/test/vet`；`pyproject.toml`→`pytest`；`Cargo.toml`→`cargo build/test`；`Makefile`→`make`。都没探到就汇报「未做机器验证」，不阻塞。

## 执行规则

1. 改动所在 worktree、**review PASS 后**跑。
2. 全过（exit 0）→ 允许 merge。
3. **exit 1**（代码问题：编译错 / 测试挂 / 新增违规）→ 回实现改代码重跑，有限轮次仍 FAIL → 标 `需人工` + 附输出。**不停其他并行 task**。
4. **exit 2**（门禁自身坏了：工具缺失 / 正则非法 / 基线损坏）→ 改代码没用，直接标 `需人工` 排查配置 / 环境。
5. 无 config 又探不到命令 → 不阻塞，汇报「未做机器验证」，不假装通过。

## 与 workflow-code-generation 集成

| 时机 | 动作 |
| --- | --- |
| 动代码前（Fast-Path / Phase 0） | 有 config → `--save-baseline` 采基线 |
| review PASS 后、merge 前 | `--baseline` 验证，或无 config 时探测 |

> 下放执行在 worktree 内，基线须用**主仓库根绝对路径** `--baseline <repo-root>/.verify/baseline.json`（worktree 看不到未提交的基线）。
>
> **基线读多写一、并发安全**：`--save-baseline` 只在动代码前单点写一次，并行 task 验证时一律**只读对比**、不改基线；report 默认写各自 worktree 的 `.verify/report.json`（相对 cwd）。worktree 隔离是为了隔离代码改动，不是为了基线。

## 强制规则

| 规则 | 说明 |
| --- | --- |
| 客观优先 | 能机器判定的，不接受口头「应该没问题」 |
| 只追新增 | 基线下历史违规不阻塞，本次不得新增 |
| 无侵入 | 无 config 又探不到命令就静默跳过 |
| 不偷改 | 不得为过门删测试 / 放宽配置 |

## 信任边界

`command` 经 `shell=True` 执行，**仅自己信任的仓库自动跑**；审外部 PR / 不可信分支时先人工确认配置内容，不自动执行。
