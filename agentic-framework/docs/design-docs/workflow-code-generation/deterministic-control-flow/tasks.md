# 实施任务清单

> 由 `spec.md` 生成  
> 任务总数：3  
> 核心原则：先实现纯控制流内核和测试，再接入实际工作流文档入口，最后做全量验证与记录。

## 依赖关系总览

```text
Task 1（控制流内核与单元测试）
  ↓
Task 2（工作流入口接线）
  ↓
Task 3（集成验证与文档收口）
```

## 变更影响概览

### 文件变更清单

| 文件 | 操作 | 涉及任务 | 说明 |
| --- | --- | --- | --- |
| `skills/workflow-code-generation/scripts/workflow_control.py` | 新建 | Task 1 | 确定性分波、状态、阻塞、恢复与 CLI |
| `scripts/test_workflow_control.py` | 新建 | Task 1 | 固定控制流 case 与文本写回测试 |
| `skills/workflow-code-generation/SKILL.md` | 修改 | Task 2 | 将内核设为实际编排强制入口 |
| `skills/workflow-code-generation/reference/delegated-execution-guide.md` | 修改 | Task 2 | 补逐波调用、结果应用和恢复命令 |
| `docs/10-harness-engineering-practices.md` | 修改 | Task 3 | 记录控制流测试落地状态 |
| `docs/design-docs/workflow-code-generation/deterministic-control-flow/spec.md` | 修改 | Task 3 | 验证后归档 |
| `docs/design-docs/workflow-code-generation/deterministic-control-flow/tasks.md` | 修改 | Task 1～3 | 实时记录任务状态与证据 |

### 受影响接口

| 接口 | 变更类型 | 调用方 | 涉及任务 |
| --- | --- | --- | --- |
| `workflow_control.py` CLI | 新增 | `workflow-code-generation` 编排流程 | Task 1、2 |
| `lint_task_deps.parse_tasks()` | 复用，不改签名 | 控制流内核 | Task 1 |

### 构建系统变更

- 不新增第三方依赖或构建配置。

## 风险与假设

| # | 描述 | 影响任务 | 假设或处理 |
| --- | --- | --- | --- |
| 1 | Prompt 文档无法像 Hook 一样强制执行脚本 | Task 2 | 将命令列为 Phase 0、逐波和恢复的强制步骤，并由测试保证脚本决策正确 |
| 2 | 当前工作区已有 `10-harness-engineering-practices.md` 未提交修改 | Task 3 | 保留既有内容，只追加本功能状态，交付时单独标明来源 |
| 3 | 恢复需要 Git 与 worktree 事实 | Task 1 | 内核只消费 `merged_task_ids`，不直接调用 Git |

## 任务列表

### 任务 1：[x] 实现确定性控制流内核与测试

- 状态：完成
- 文件：`agentic-framework/skills/workflow-code-generation/scripts/workflow_control.py`（新建）、`agentic-framework/scripts/test_workflow_control.py`（新建）
- depends_on：[]
- review_profile：standard
- spec 映射：4.2、4.3、7.1、7.2
- 说明：复用现有解析器，实现稳定分波、可调度判断、结果应用、重试耗尽、阻塞传播、恢复计划、精准状态写回和最小 CLI。
- context_files：
  - `agentic-framework/skills/workflow-code-generation/scripts/lint_task_deps.py`——现有任务解析与状态契约
  - `agentic-framework/skills/workflow-code-generation/reference/delegated-execution-guide.md`——控制流规则来源
  - `agentic-framework/scripts/test_lint_task_deps.py`——现有测试风格
- verification：
  - [x] `python -m unittest agentic-framework/scripts/test_workflow_control.py` 通过
  - [x] `python -m unittest agentic-framework/scripts/test_lint_task_deps.py` 通过
  - [x] 5 类核心控制流均有固定 case
  - [x] 测试不访问网络、不调用模型、不创建 worktree
- artifacts：
  - `agentic-framework/skills/workflow-code-generation/scripts/workflow_control.py`
  - `agentic-framework/scripts/test_workflow_control.py`
- 子任务：
  - [x] 1.1：定义最小不可变结果和决策数据类
  - [x] 1.2：实现分波、状态、阻塞和恢复逻辑
  - [x] 1.3：实现精准文本写回和 CLI
  - [x] 1.4：调用 `workflow-test-generation` 补齐正常路径和关键边界测试
  - [x] 1.5：运行测试，全部通过

### 任务 2：[x] 将控制流内核接入工作流入口

- 状态：完成
- 文件：`agentic-framework/skills/workflow-code-generation/SKILL.md`（修改）、`agentic-framework/skills/workflow-code-generation/reference/delegated-execution-guide.md`（修改）
- depends_on：[Task 1]
- review_profile：standard
- spec 映射：4.1、4.3
- 说明：将波次生成、逐波推进、状态写回和恢复改为调用 `workflow_control.py`，删除与脚本冲突的手工判断表述。
- context_files：
  - `agentic-framework/skills/workflow-code-generation/scripts/workflow_control.py`——Task 1 新接口
  - `agentic-framework/skills/workflow-code-generation/SKILL.md`——实际工作流入口
  - `agentic-framework/skills/workflow-code-generation/reference/delegated-execution-guide.md`——下放执行细则
- verification：
  - [x] 文档中的命令与 CLI `--help` 一致
  - [x] 分波、失败后阻塞和恢复均明确调用同一脚本
  - [x] `python agentic-framework/scripts/lint_skill_graph.py` 通过
- artifacts：
  - `agentic-framework/skills/workflow-code-generation/SKILL.md`
  - `agentic-framework/skills/workflow-code-generation/reference/delegated-execution-guide.md`
- 子任务：
  - [x] 2.1：修改 SKILL 的波次与恢复入口
  - [x] 2.2：修改执行手册命令与顺序
  - [x] 2.3：核对 CLI 示例可执行

### Review 修复记录

- 2026-07-12：修复首轮 Review 的 8 项 finding：拆分质量门与合并事件、拒绝自依赖、统一合法状态转换、持久化修复次数、缺失依赖字段失败关闭、原子写回、拒绝 CR / LF 原因、补同波失败隔离集成测试。
- 2026-07-12：修复第二轮 Review 的 3 项 finding：持久化 `control_stage` 并限制合并阶段、启动前复核依赖、原子写回保留权限和 CRLF；补对应负向测试。

### 任务 3：[x] 完成集成验证与审核记录

- 状态：完成
- 文件：`agentic-framework/docs/10-harness-engineering-practices.md`（修改）、`agentic-framework/docs/design-docs/workflow-code-generation/deterministic-control-flow/spec.md`（修改）、`agentic-framework/docs/design-docs/workflow-code-generation/deterministic-control-flow/tasks.md`（修改）
- depends_on：[Task 2]
- review_profile：standard
- spec 映射：7、8、9
- 说明：运行仓库级测试和机器验证，记录实际结果、Review 结论与限制，归档规格。
- context_files：
  - `verify.config.json`——仓库机器验证配置
  - `agentic-framework/docs/10-harness-engineering-practices.md`——路线图状态
  - `agentic-framework/docs/design-docs/workflow-code-generation/deterministic-control-flow/spec.md`——验收契约
- verification：
  - [x] `python -m unittest discover -s agentic-framework/scripts -p "test_*.py"` 通过：40 个通过，1 个跳过
  - [x] `python -m compileall -q agentic-framework/scripts agentic-framework/skills/workflow-code-generation/scripts` 通过
  - [x] `python agentic-framework/skills/workflow-code-generation/scripts/lint_task_deps.py <tasks.md>` 通过：0 error，0 warning
  - [x] `git diff --check` 通过
- artifacts：
  - 更新后的 `spec.md`、`tasks.md` 和 Harness 实践文档
  - 测试与验证结果摘要
- 子任务：
  - [x] 3.1：运行全量单元测试与编译检查
  - [x] 3.2：执行标准档代码 Review 并处理 keep finding
  - [x] 3.3：记录验证结果和已知限制
  - [x] 3.4：归档规格并提交本地 Git

### 最终审核与验证记录

- 标准档首轮 Review：`NEEDS_CHANGES`，确认 4 项 P1 和 4 项 P2。
- 第一轮复审：6 项已修复，2 项部分修复，新增 1 项 P2。
- 第二轮复审：`PASS`，未发现新的 P0 或 P1。
- 全量测试：40 个通过，1 个跳过。
- 既存限制：Prompt 入口不具备 Hook 级强制性；恢复仍依赖编排层提供真实 Git 合并事实。

## Spec 覆盖映射

| Spec 章节 | 任务 | 说明 |
| --- | --- | --- |
| 4.1 | Task 2 | 编排层接入控制流内核 |
| 4.2 | Task 1 | 模块、接口、数据与错误处理 |
| 4.3 | Task 1、2 | 核心算法和实际入口 |
| 4.4～6 | Task 3 | 取舍与限制记录 |
| 7 | Task 1、3 | 单元和集成验证 |
| 8～9 | Task 3 | 运维说明与变更记录 |
