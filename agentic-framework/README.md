# Agentic Framework

> 为「快速构建大型但非生产环境的工具 / 项目」特化的 agentic engineering workflow：前期人把关需求与设计，执行段由 AI 自主并行跑，质量基建通过分级 review 与机器验证兜底。

## 这个框架是什么

它是 `agentic-engineering-framework` 的一个特化分支，核心取舍是：

> **前期人把关（需求 + 设计），执行段 AI 自主并行跑**——质量基建（多维 review）不打折，但执行不再逐 task 停等。

与原框架的关系：

- **复制**了原框架中与本场景相关的 `workflow-*` 全套及其运行依赖（`bp-*` / `std-*` / `project-knowledge` / `self-refinement` / `agents/` 评审 subagent / 命令入口）。
- **未复制** `opsx-*`（OpenSpec 复刻）等与本场景无关的部分。
- **改造** `workflow-code-generation`：把执行段从「逐 task 停等串行」升级为「复杂度路由 + 下放 agent 执行（极轻改动主会话直改、中等+ 单 / 并行 agent）」。

## 组件说明

| 目录 | 作用 | 安装目标 |
|------|------|---------|
| `commands/` | Slash 命令入口（`/code-generation`、`/quick-design` 等） | `.claude/commands/`、`.codex/commands/` |
| `agents/` | 专项 subagent 定义（reviewer、researcher 等） | `.claude/agents/`、`.codex/agents/` |
| `skills/` | 工作流执行指令，命令触发后由 Claude / Codex 读取 | `.claude/skills/`、`.codex/skills/` |

> 推荐用下方「自动安装」脚本一次性把三类目录拷进 `.claude` 与 `.codex`。

---

## 自动安装（推荐）

`scripts/install_agentic_framework.py` 把 `skills/`、`agents/`、`commands/` 拷进目标目录的 `.codex` 与 `.claude` 两个客户端目录。

```bash
# 装到当前项目（项目根作为 target_dir）
python scripts/install_agentic_framework.py .

# 装到全局
python scripts/install_agentic_framework.py "$HOME"

# 预览将拷贝哪些目录，不写盘
python scripts/install_agentic_framework.py . --dry-run
```

- 覆盖语义：同名文件按框架版本覆盖，目标侧无关文件保留；如在 `.claude/skills` 下有同名本地定制，先备份。
- Claude：`.claude/skills/<name>/SKILL.md` 由 Claude Code 自动发现，无需再在 CLAUDE.md 写路径。
- Codex：`.codex/skills/<name>/SKILL.md`、`.codex/agents/` 与 `.codex/commands/` 随脚本拷出；`AGENTS.md` 只保留项目级约定。

### 可选：并行浏览器验证 MCP

前端浏览器验证优先安装 `playwright-mcp-parallel`，而不是普通 `@playwright/mcp`。它是 `@playwright/mcp` 的增强版，支持多个隔离浏览器实例并行执行。

#### Claude Code

```bash
claude mcp add --transport stdio playwright-parallel -- npx -y playwright-mcp-parallel@latest
```

如需无头模式：

```bash
claude mcp add --transport stdio playwright-parallel -- npx -y playwright-mcp-parallel@latest --headless
```

验证：

```bash
claude mcp list
```

进入 Claude Code 后，也可以用 `/mcp` 检查服务状态。

#### Codex

```bash
codex mcp add playwright-parallel -- npx -y playwright-mcp-parallel@latest
```

如需无头模式：

```bash
codex mcp add playwright-parallel -- npx -y playwright-mcp-parallel@latest --headless
```

进入 Codex TUI 后，用 `/mcp` 检查服务状态。

#### 手动配置备选

如果不想用 CLI 命令，也可以手动写入对应客户端的 MCP 配置。配置形态如下：

```json
{
    "mcpServers": {
        "playwright-parallel": {
            "command": "npx",
            "args": [
                "-y",
                "playwright-mcp-parallel@latest"
            ]
        }
    }
}
```

说明：

- 需要 Node.js 18+。
- 适用于 `frontend-playwright-verification` 的并行浏览器验证场景。
- 如果要把 E2E 测试代码提交到项目里，项目本身仍可能需要按技术栈安装测试运行器（例如 `@playwright/test`）。

---

## Claude Code

自动安装后，Claude Code 从 `.claude/commands/`、`.claude/agents/` 与 `.claude/skills/` 读取对应资源；无需再在 `CLAUDE.md` 中手写 Skills 路径。

### 卸载

```bash
commands=(
    project-init.md
    requirements-clarification.md
    system-design.md
    quick-design.md
    code-generation.md
    code-review.md
    test-generation.md
    performance-optimization.md
    reflect.md
    troubleshooting.md
    frontend-design.md
)
agents=(
    codebase-researcher.md
    comprehensive-reviewer.md
    magical-prompt-reviewer.md
    performance-reviewer.md
    review-critic.md
    robustness-reviewer.md
    spec-compliance-reviewer.md
    standards-reviewer.md
)

# 项目级
for f in "${commands[@]}"; do rm -f ".claude/commands/$f"; done
for f in "${agents[@]}";   do rm -f ".claude/agents/$f";   done

# 全局（去掉上面两行，改用下面两行）
# for f in "${commands[@]}"; do rm -f "$HOME/.claude/commands/$f"; done
# for f in "${agents[@]}";   do rm -f "$HOME/.claude/agents/$f";   done
```

如果历史上手动在 `CLAUDE.md` 中写过 Skills 路径声明，卸载后也一并删除。

---

## Codex

自动安装后，Codex 从 `.codex/commands/`、`.codex/agents/` 与 `.codex/skills/` 读取对应资源；无需把 skill 或 agent 正文内嵌到 `AGENTS.md`。

`AGENTS.md` 仍适合放项目级约定，例如代码风格、验证命令、默认工作流入口和长期偏好。

### 卸载

删除 `.codex/commands/`、`.codex/agents/` 与 `.codex/skills/` 中对应文件即可。

---

## 可用命令一览

| 命令 | 用途 |
|------|------|
| `/project-init` | 项目初始化（版本管理模式选择、git init、CLAUDE.md / AGENTS.md / README / docs 骨架） |
| `/requirements-clarification` | 需求澄清，产出 spec 1-3 章 |
| `/system-design` | 系统设计，产出完整 spec |
| `/quick-design` | 快速设计（内部工具 / 小型服务） |
| `/code-generation` | 代码生成（统一入口，复杂度路由） |
| `/code-review` | 分级代码评审 |
| `/verification` | 零配置机器验证门（探测 build / test 跑一遍） |
| `/test-generation` | 测试生成（含 Playwright E2E） |
| `/frontend-design` | 前端 UI 设计（生成 HTML 方案 → 用户选择 → ui-spec.md） |
| `/performance-optimization` | 性能优化 |
| `/troubleshooting` | 问题排查 |
| `/reflect` | 经验反馈与 skill 更新 |

---

## 工具脚本

框架 `scripts/` 下的维护脚本（只服务框架仓库本身，不随安装分发）：

| 脚本 | 用途 |
|------|------|
| `install_agentic_framework.py` | 把 `skills/` / `agents/` / `commands/` 安装进目标目录的 `.claude` 与 `.codex` |
| `lint_skill_graph.py` | 静态校验 skill 引用图：dangling、command 目标缺失、name / 目录名一致、frontmatter description 完整、review 档位→reviewer 映射闭环、orphan |

流程门禁脚本随 `workflow-code-generation` skill 分发（`skills/workflow-code-generation/scripts/`，安装后在目标项目的 skill 目录内可用）：

| 脚本 | 用途 |
|------|------|
| `lint_task_deps.py` | 校验 tasks.md 依赖与字段：dangling 依赖、循环依赖、「改同一文件却无依赖关系」的并行冲突、必填字段（review_profile / context_files / verification / artifacts / 状态）齐全合法 |
| `lint_spec.py` | 校验 spec.md 章节完整性：状态字段合法、design 阶段查 1～3 章 / code 阶段查 1～4 章（Quick Draft 查简化章节），对照模板识别「复制未填」的占位章节 |
| `check_delivery.py` | 交付门：tasks.md 全部任务终态且附原因、spec 已归档（Archived）、git 工作区干净 |

```bash
# lint：有 ERROR 退出码 1，可进 CI / pre-commit
python scripts/lint_skill_graph.py

# graph：输出 Markdown 引用图，交给 LLM 判定语义遗漏 / 多余
python scripts/lint_skill_graph.py --graph

# 校验 tasks.md 依赖关系与必填字段
python skills/workflow-code-generation/scripts/lint_task_deps.py <tasks.md>

# 校验 spec.md 章节完整性（设计前 design / 编码前 code）
python skills/workflow-code-generation/scripts/lint_spec.py <spec.md> --phase code

# 交付门：宣布交付前必须通过（Fast-Path 只传 --repo）
python skills/workflow-code-generation/scripts/check_delivery.py --tasks <tasks.md> --spec <spec.md>
```

---

## 设计文档索引

`docs/` 只保留具体设计与决策记录：

| 文档 | 内容 | 何时读 |
|------|------|--------|
| [01-why-and-methodology.md](docs/01-why-and-methodology.md) | 为什么要这个框架 + 诉求画像 + 方法论 | 想知道动机和打法 |
| [02-tool-landscape.md](docs/02-tool-landscape.md) | 选型调研（Spec Kit / Superpowers / OpenSpec / Taskmaster）+ 为什么基于 `workflow-*` 改造 | 想知道选型依据 |
| [03-parallel-execution-mode.md](docs/03-parallel-execution-mode.md) | `code-generation` 执行段（下放 agent + 并行）的设计规格 | 实现 / 理解执行段时 |
| [04-compound-engineering-comparison.md](docs/04-compound-engineering-comparison.md) | compound-engineering-plugin 调研 + 与本框架对比 + 吸收决策 | 了解知识沉淀机制设计依据时 |
| [05-industry-comparison.md](docs/05-industry-comparison.md) | 与 Superpowers / OpenSpec / Spec Kit / Taskmaster / ce-compound 的横向对比 | 评估框架定位 / 选型决策时 |
| [06-official-frontend-skills-installation.md](docs/06-official-frontend-skills-installation.md) | 官方前端 skills 本地化来源与保留流程 | 理解本地前端 workflow 来源时 |
| [07-critical-review.md](docs/07-critical-review.md) | 框架独立批判性评估（短板 + 改进，标注已补项） | 审视框架短板 / 规划后续改进时 |
| [08-evaluation-strategy.md](docs/08-evaluation-strategy.md) | 评测体系分层落地 + 框架特有难点 | 规划 / 落地 skill 评测时 |

架构决策记录：

| 文档 | 决策 |
|------|------|
| [001-machine-verification-gate.md](docs/adr/001-machine-verification-gate.md) | 将机器验证设为与 LLM Code Review 并列的合并前硬门 |
