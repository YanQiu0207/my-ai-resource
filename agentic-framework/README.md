# Agentic Framework — 安装指南

## 组件说明

| 目录 | 作用 | 安装目标 |
|------|------|---------|
| `commands/` | Slash 命令入口（`/code-generation`、`/quick-design` 等） | `.claude/commands/` |
| `agents/` | 专项 subagent 定义（reviewer、researcher 等） | `.claude/agents/` |
| `skills/` | 工作流执行指令，命令触发后由 Claude 读取 | 本地保留，路径写入 CLAUDE.md |

---

## Claude Code

### 项目级安装（仅对当前项目生效）

在项目根目录执行：

```powershell
$fw = "E:/work/my-ai-resource/agentic-framework"

New-Item -ItemType Directory -Force ".claude/commands" | Out-Null
New-Item -ItemType Directory -Force ".claude/agents"   | Out-Null

Copy-Item "$fw/commands/*" ".claude/commands/" -Force
Copy-Item "$fw/agents/*"   ".claude/agents/"   -Force
```

然后在项目的 `.claude/CLAUDE.md`（不存在则新建）中追加：

```markdown
## Skills 路径

Skills 位于 `E:/work/my-ai-resource/agentic-framework/skills/`。
收到「调用 <name> skill」指令时，读取该目录下 `<name>/SKILL.md` 并严格按其执行。
```

### 全局安装（对所有项目生效）

```powershell
$fw  = "E:/work/my-ai-resource/agentic-framework"
$cc  = "$env:USERPROFILE/.claude"

New-Item -ItemType Directory -Force "$cc/commands" | Out-Null
New-Item -ItemType Directory -Force "$cc/agents"   | Out-Null

Copy-Item "$fw/commands/*" "$cc/commands/" -Force
Copy-Item "$fw/agents/*"   "$cc/agents/"   -Force
```

然后在 `~/.claude/CLAUDE.md` 中追加同样的 Skills 路径声明（见上方）。

### 按需选装

只安装部分命令或 agent：

```powershell
$fw = "E:/work/my-ai-resource/agentic-framework"

# 只装代码生成和快速设计命令
Copy-Item "$fw/commands/code-generation.md" ".claude/commands/" -Force
Copy-Item "$fw/commands/quick-design.md"    ".claude/commands/" -Force

# 只装代码研究 agent
Copy-Item "$fw/agents/codebase-researcher.md" ".claude/agents/" -Force
```

### 卸载

```powershell
$commands = @(
    "requirements-clarification.md",
    "system-design.md",
    "quick-design.md",
    "code-generation.md",
    "code-review.md",
    "test-generation.md",
    "performance-optimization.md",
    "reflect.md",
    "troubleshooting.md",
    "frontend-design.md"
)
$agents = @(
    "codebase-researcher.md",
    "magical-prompt-reviewer.md",
    "performance-reviewer.md",
    "review-critic.md",
    "robustness-reviewer.md",
    "spec-compliance-reviewer.md",
    "standards-reviewer.md"
)

# 项目级
$commands | ForEach-Object { Remove-Item -Path ".claude/commands/$_" -Force -ErrorAction SilentlyContinue }
$agents   | ForEach-Object { Remove-Item -Path ".claude/agents/$_"   -Force -ErrorAction SilentlyContinue }

# 全局（去掉上面两行，改用下面两行）
# $commands | ForEach-Object { Remove-Item -Path "$env:USERPROFILE/.claude/commands/$_" -Force -ErrorAction SilentlyContinue }
# $agents   | ForEach-Object { Remove-Item -Path "$env:USERPROFILE/.claude/agents/$_"   -Force -ErrorAction SilentlyContinue }
```

卸载后手动删除 CLAUDE.md 中的 Skills 路径声明。

---

## Codex

Codex 通过项目根目录的 `AGENTS.md` 获取指令。Skills 内容需内嵌或引用。

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
- 需求澄清：`workflow-requirements-clarification/SKILL.md`
- 系统设计：`workflow-system-design/SKILL.md`
- 测试生成：`workflow-test-generation/SKILL.md`
- 前端设计：`workflow-frontend-design/SKILL.md`
- 前端视觉基准：`bp-frontend-taste/SKILL.md`
- React 规范：`std-react/SKILL.md`
```

**方式 B（内嵌关键 skill，不依赖外部路径）**

```powershell
$fw = "E:/work/my-ai-resource/agentic-framework"

# 将 skill 内容追加到 AGENTS.md
"", "---", "# workflow-code-generation" | Add-Content AGENTS.md
Get-Content "$fw/skills/workflow-code-generation/SKILL.md" | Add-Content AGENTS.md
```

对每个需要的 skill 重复此操作。

### Agent 定义注册（Codex 不原生支持 subagent，以 prompt 片段形式注入）

```powershell
$fw = "E:/work/my-ai-resource/agentic-framework"

"", "---", "# Subagent Definitions" | Add-Content AGENTS.md
Get-Content "$fw/agents/codebase-researcher.md"    | Add-Content AGENTS.md
Get-Content "$fw/agents/standards-reviewer.md"     | Add-Content AGENTS.md
Get-Content "$fw/agents/spec-compliance-reviewer.md" | Add-Content AGENTS.md
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
| `/test-generation` | 测试生成（含 Playwright E2E） |
| `/frontend-design` | 前端 UI 设计（生成 HTML 方案 → 用户选择 → ui-spec.md） |
| `/performance-optimization` | 性能优化 |
| `/troubleshooting` | 问题排查 |
| `/reflect` | 经验反馈与 skill 更新 |
