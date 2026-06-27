# Agentic Framework — 安装指南

## 组件说明

| 目录 | 作用 | 安装目标 |
|------|------|---------|
| `commands/` | Slash 命令入口（`/code-generation`、`/quick-design` 等） | `.claude/commands/`、`.codex/commands/` |
| `agents/` | 专项 subagent 定义（reviewer、researcher 等） | `.claude/agents/`、`.codex/agents/` |
| `skills/` | 工作流执行指令，命令触发后由 Claude / Codex 读取 | `.claude/skills/`、`.codex/skills/` |

> 推荐用下方「自动安装」脚本一次性把三类目录拷进 `.claude` 与 `.codex`。手动安装小节作为按需 / 不便运行脚本时的替代方案保留。

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
- Codex：脚本拷出文件后，仍需按下方 Codex 小节在 `AGENTS.md` 中引用或内嵌对应 skill / agent（Codex 不自动扫描目录）。

---

## Claude Code

> 以下为手动安装（脚本的替代方案）：拷 `commands/` 与 `agents/`，`skills/` 改用路径引用留在源目录。若已用上方脚本安装，本节可跳过。

### 项目级安装（仅对当前项目生效）

在项目根目录执行：

```bash
fw="/e/work/my-ai-resource/agentic-framework"

mkdir -p .claude/commands .claude/agents

cp "$fw"/commands/* .claude/commands/
cp "$fw"/agents/*   .claude/agents/
```

然后在项目的 `.claude/CLAUDE.md`（不存在则新建）中追加：

```markdown
## Skills 路径

Skills 位于 `E:/work/my-ai-resource/agentic-framework/skills/`。
收到「调用 <name> skill」指令时，读取该目录下 `<name>/SKILL.md` 并严格按其执行。
```

### 全局安装（对所有项目生效）

```bash
fw="/e/work/my-ai-resource/agentic-framework"
cc="$HOME/.claude"

mkdir -p "$cc/commands" "$cc/agents"

cp "$fw"/commands/* "$cc/commands/"
cp "$fw"/agents/*   "$cc/agents/"
```

然后在 `~/.claude/CLAUDE.md` 中追加同样的 Skills 路径声明（见上方）。

### 按需选装

只安装部分命令或 agent：

```bash
fw="/e/work/my-ai-resource/agentic-framework"

# 只装代码生成和快速设计命令
cp "$fw/commands/code-generation.md" .claude/commands/
cp "$fw/commands/quick-design.md"    .claude/commands/

# 只装代码研究 agent
cp "$fw/agents/codebase-researcher.md" .claude/agents/
```

### 卸载

```bash
commands=(
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

卸载后手动删除 CLAUDE.md 中的 Skills 路径声明。

---

## Codex

Codex 通过项目根目录的 `AGENTS.md` 获取指令，不自动扫描 `.codex/` 目录。无论是否已用脚本把文件拷进 `.codex`，都需在 `AGENTS.md` 中按下方方式引用或内嵌对应 skill / agent 才能生效。

### 安装

**方式 A（直接引用 skill 文件路径，Codex 可读取本地文件时适用）**

在项目根 `AGENTS.md` 中追加：

```markdown
## 工作流 Skills

以下 skill 文件位于 `E:/work/my-ai-resource/agentic-framework/skills/`，
收到对应指令时读取并执行：

- 代码生成：`workflow-code-generation/SKILL.md`
- 快速设计：`workflow-quick-design/SKILL.md`
- 代码评审：`workflow-code-review/SKILL.md`
- 机器验证门：`workflow-verification/SKILL.md`
- 需求澄清：`workflow-requirements-clarification/SKILL.md`
- 系统设计：`workflow-system-design/SKILL.md`
- 测试生成：`workflow-test-generation/SKILL.md`
- 前端设计：`workflow-frontend-design/SKILL.md`
- 前端布局骨架：`bp-frontend-layout/SKILL.md`
- React 规范：`std-react/SKILL.md`
- 前端视觉基准：`bp-frontend-taste/SKILL.md`
- 前端浏览器验证：`frontend-playwright-verification/SKILL.md`
```

**方式 B（内嵌关键 skill，不依赖外部路径）**

```bash
fw="/e/work/my-ai-resource/agentic-framework"

# 将 skill 内容追加到 AGENTS.md
printf '\n---\n# workflow-code-generation\n' >> AGENTS.md
cat "$fw/skills/workflow-code-generation/SKILL.md" >> AGENTS.md
```

对每个需要的 skill 重复此操作。

### Agent 定义注册（Codex 不原生支持 subagent，以 prompt 片段形式注入）

```bash
fw="/e/work/my-ai-resource/agentic-framework"

printf '\n---\n# Subagent Definitions\n' >> AGENTS.md
cat "$fw/agents/codebase-researcher.md"      >> AGENTS.md
cat "$fw/agents/standards-reviewer.md"       >> AGENTS.md
cat "$fw/agents/spec-compliance-reviewer.md" >> AGENTS.md
```

### 卸载

Codex 无独立文件，删除 `AGENTS.md` 中对应的段落即可。

---

## 可用命令一览

| 命令 | 用途 |
|------|------|
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
