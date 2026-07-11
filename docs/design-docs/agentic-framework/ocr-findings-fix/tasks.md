# 实施任务清单

> 由 `spec.md` 生成
> 任务总数：5
> 核心原则：按独立脚本拆分修复和回归测试，最后统一验证与复审。

## 依赖关系总览

```text
Task 1 ─┐
Task 2 ─┤
Task 3 ─┼──> Task 5
Task 4 ─┘
```

## 变更影响概览

### 文件变更清单

| 文件 | 操作 | 涉及任务 | 说明 |
| --- | --- | --- | --- |
| `agentic-framework/skills/workflow-verification/scripts/verify.py` | 修改 | Task 1 | 纳入未跟踪规格文件 |
| `agentic-framework/skills/workflow-verification/scripts/test_verify.py` | 新建 | Task 1 | 规格漂移回归测试 |
| `agentic-framework/scripts/lint_skill_graph.py` | 修改 | Task 2 | 全量目标检查和 Frontmatter 错误处理 |
| `agentic-framework/scripts/test_lint_skill_graph.py` | 新建 | Task 2 | Skill 图回归测试 |
| `agentic-framework/scripts/lint_task_deps.py` | 修改 | Task 3 | 字段存在性和重复任务检查 |
| `agentic-framework/scripts/test_lint_task_deps.py` | 新建 | Task 3 | 任务依赖回归测试 |
| `agentic-framework/scripts/install_agentic_framework.py` | 修改 | Task 4 | 复制预检和失败回滚 |
| `agentic-framework/scripts/setup_code_review.py` | 修改 | Task 4 | 修正预演就绪语义 |
| `agentic-framework/scripts/test_install_agentic_framework.py` | 新建 | Task 4 | 安装回滚测试 |
| `agentic-framework/scripts/test_setup_code_review.py` | 新建 | Task 4 | 预演输出测试 |
| `.verify/report.json` | 生成 | Task 5 | 机器验证报告 |

### 受影响接口

- 不修改公开 CLI 参数。
- 内部解析函数可能增加明确的错误状态或异常，由各自 `main()` 转换为现有错误输出和非零退出码。

### 构建系统变更

- 无。

## 风险与假设

| # | 描述 | 影响任务 | 假设／处理 |
| --- | --- | --- | --- |
| 1 | 安装失败可能发生在任意一次目录复制 | Task 4 | 复制前备份相关目标树，异常时恢复本次涉及的目标树 |
| 2 | `--dry-run` 的成功表示预演成功，不表示工具已经安装 | Task 4 | 保持退出码为 `0`，但不输出就绪提示 |
| 3 | 仓库没有现成测试框架 | Task 1～4 | 使用 Python 标准库 `unittest` |

## 任务列表

### 任务 1：[x] 修正规格漂移检查

- 状态：已完成
- 文件：`agentic-framework/skills/workflow-verification/scripts/verify.py`（修改）、`agentic-framework/skills/workflow-verification/scripts/test_verify.py`（新建）
- depends_on: []
- review_profile: standard
- spec 映射：规格漂移检查
- 说明：让未跟踪的相关规格文件参与关联判断，并覆盖相关和无关文件场景。
- context_files:
    - `agentic-framework/skills/workflow-verification/scripts/verify.py:evaluate_spec_drift()` — 直接修改目标
    - `agentic-framework/skills/workflow-verification/scripts/verify.py:_related_spec_files()` — 关联规则消费者
- verification:
    - [x] `python -m unittest discover -s agentic-framework/skills/workflow-verification/scripts -p "test_*.py"` 通过
    - [x] `python -m py_compile agentic-framework/skills/workflow-verification/scripts/verify.py` 通过
- artifacts:
    - `agentic-framework/skills/workflow-verification/scripts/verify.py`
    - `agentic-framework/skills/workflow-verification/scripts/test_verify.py`
- 子任务：
    - [x] 1.1：修正规格文件集合
    - [x] 1.2：通过 `workflow-test-generation` 补充相关与无关文件测试
    - [x] 1.3：运行测试

### 任务 2：[x] 修复 Skill 图漏检和 Frontmatter 误报

- 状态：已完成
- 文件：`agentic-framework/scripts/lint_skill_graph.py`（修改）、`agentic-framework/scripts/test_lint_skill_graph.py`（新建）
- depends_on: []
- review_profile: standard
- spec 映射：Skill 图和任务依赖 Lint
- 说明：检查全部 Skill 调用，并为未闭合 Frontmatter 输出直接错误且避免伪依赖。
- context_files:
    - `agentic-framework/scripts/lint_skill_graph.py:find_command_target_errors()` — 命令目标检查
    - `agentic-framework/scripts/lint_skill_graph.py:frontmatter_end()` — Frontmatter 边界识别
    - `agentic-framework/scripts/lint_skill_graph.py:collect_nodes()` — 元数据错误输出
    - `agentic-framework/scripts/lint_skill_graph.py:outgoing_edges()` — 图关系提取
- verification:
    - [x] `python -m unittest agentic-framework/scripts/test_lint_skill_graph.py` 通过
    - [x] `python agentic-framework/scripts/lint_skill_graph.py` 退出码为 `0`
- artifacts:
    - `agentic-framework/scripts/lint_skill_graph.py`
    - `agentic-framework/scripts/test_lint_skill_graph.py`
- 子任务：
    - [x] 2.1：修复全量匹配和 Frontmatter 三态判断
    - [x] 2.2：通过 `workflow-test-generation` 补充回归测试
    - [x] 2.3：运行测试和现有 Lint

### 任务 3：[x] 修复任务依赖字段和重复 ID 检查

- 状态：已完成
- 文件：`agentic-framework/scripts/lint_task_deps.py`（修改）、`agentic-framework/scripts/test_lint_task_deps.py`（新建）
- depends_on: []
- review_profile: standard
- spec 映射：Skill 图和任务依赖 Lint
- 说明：区分空字段与缺失字段，并拒绝重复任务 ID。
- context_files:
    - `agentic-framework/scripts/lint_task_deps.py:parse_deps()` — 依赖字段解析
    - `agentic-framework/scripts/lint_task_deps.py:parse_tasks()` — 任务索引构建
    - `agentic-framework/scripts/lint_task_deps.py:main()` — CLI 错误输出
- verification:
    - [x] `python -m unittest agentic-framework/scripts/test_lint_task_deps.py` 通过
    - [x] 使用包含空依赖字段和重复 ID 的临时输入验证退出码
- artifacts:
    - `agentic-framework/scripts/lint_task_deps.py`
    - `agentic-framework/scripts/test_lint_task_deps.py`
- 子任务：
    - [x] 3.1：修正字段存在性判断和重复 ID 错误
    - [x] 3.2：通过 `workflow-test-generation` 补充回归测试
    - [x] 3.3：运行测试

### 任务 4：[x] 修复安装原子性和预演语义

- 状态：已完成
- 文件：`agentic-framework/scripts/install_agentic_framework.py`（修改）、`agentic-framework/scripts/setup_code_review.py`（修改）、`agentic-framework/scripts/test_install_agentic_framework.py`（新建）、`agentic-framework/scripts/test_setup_code_review.py`（新建）
- depends_on: []
- review_profile: standard
- spec 映射：安装和环境配置
- 说明：复制前统一预检，失败时恢复目标树；预演不再输出错误的就绪提示。
- context_files:
    - `agentic-framework/scripts/install_agentic_framework.py:install()` — 安装编排
    - `agentic-framework/scripts/install_agentic_framework.py:copy_tree()` — 目录复制
    - `agentic-framework/scripts/install_agentic_framework.py:main()` — Code Review 配置调用方
    - `agentic-framework/scripts/setup_code_review.py:install_ocr()` — `ocr` 安装状态
    - `agentic-framework/scripts/setup_code_review.py:setup()` — 就绪提示消费者
- verification:
    - [x] `python -m unittest agentic-framework/scripts/test_install_agentic_framework.py agentic-framework/scripts/test_setup_code_review.py` 通过
    - [x] 模拟后续复制失败后，全部相关目标树恢复为调用前状态
    - [x] `ocr` 缺失的 `--dry-run` 不输出就绪提示且退出码为 `0`
- artifacts:
    - `agentic-framework/scripts/install_agentic_framework.py`
    - `agentic-framework/scripts/setup_code_review.py`
    - `agentic-framework/scripts/test_install_agentic_framework.py`
    - `agentic-framework/scripts/test_setup_code_review.py`
- 子任务：
    - [x] 4.1：实现复制预检、临时备份和失败回滚
    - [x] 4.2：修正预演状态传播
    - [x] 4.3：通过 `workflow-test-generation` 补充异常路径测试
    - [x] 4.4：运行测试

### 任务 5：[x] 整体验证和 `ocr` 复审

- 状态：完成
- 文件：`.verify/report.json`（生成）
- depends_on: [Task 1, Task 2, Task 3, Task 4]
- review_profile: standard
- spec 映射：验收标准
- 说明：运行全部回归测试、现有验证门和相同范围的 `ocr scan`。
- context_files:
    - `verify.config.json` — 验证命令配置
    - `docs/design-docs/agentic-framework/ocr-findings-fix/spec.md` — 验收标准
    - `docs/design-docs/agentic-framework/ocr-findings-fix/tasks.md` — 任务状态和文件范围
- verification:
    - [x] 两组 `unittest discover` 命令通过
    - [x] 5 个目标脚本通过 `python -m py_compile`
    - [x] `workflow-verification` 报告通过且 `spec_drift` 通过
    - [x] 相同 5 个文件的 `ocr scan` 不再报告本次 7 条问题
- artifacts:
    - `.verify/report.json`
    - `ocr` JSON 审查结果
- 子任务：
    - [x] 5.1：运行整体代码评审
    - [x] 5.2：运行机器验证
    - [x] 5.3：运行 `ocr` 复审

## Spec 覆盖映射

| Spec 章节 | 任务 | 说明 |
| --- | --- | --- |
| 规格漂移检查 | Task 1 | 修复未跟踪规格文件判断 |
| Skill 图和任务依赖 Lint | Task 2、Task 3 | 修复漏检、误报和静默覆盖 |
| 安装和环境配置 | Task 4 | 修复部分写入和预演提示 |
| 验收标准 | Task 5 | 统一验证和外部复审 |
