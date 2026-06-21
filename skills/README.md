# Skills

本目录用于归档可复用的 AI 技能，按运行环境拆分：

- `codex/`：Codex 使用的技能。
- `claude-code/`：Claude Code 使用的技能。

## 目录结构

```text
skills/
├── codex/
│   └── <skill-name>/
│       ├── SKILL.md
│       └── agents/openai.yaml
└── claude-code/
    └── <skill-name>/
        └── SKILL.md
```

## 安装指令

在本仓库的 `skills/` 目录执行以下命令。

### 安装 Codex 技能

```powershell
$skillName = "code-reading-assistant"
Copy-Item -LiteralPath ".\codex\$skillName" -Destination "$HOME\.codex\skills" -Recurse -Force
```

### 安装 Claude Code 技能

```powershell
$skillName = "code-reading-assistant"
Copy-Item -LiteralPath ".\claude-code\$skillName" -Destination "$HOME\.claude\skills" -Recurse -Force
```

## 新增技能维护规则

新增或修改技能时，必须同时维护两份：

1. `codex/<skill-name>/`：保留 Codex 需要的 `SKILL.md`，如需手动触发或 UI 元数据，同步维护 `agents/openai.yaml`。
2. `claude-code/<skill-name>/`：保留 Claude Code 使用的 `SKILL.md`。

如果两个平台需要不同触发规则，优先保持技能正文一致，只在平台专属配置文件中表达差异。
