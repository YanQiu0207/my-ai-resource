# Claude Code 与 Codex 省 Token 实践

> 更新日期：2026-06-25（补充 Codex 上下文窗口、压缩时机与配置文件）
> 适用对象：日常使用 Claude Code 和 Codex 做代码阅读、修改、测试、Review、文档整理的个人或团队。

## 结论

省 token 的核心不是少打几个字，而是**减少 agent 反复读取无关上下文**。

Claude Code 和 Codex 的官方建议高度一致：

- 缩小任务范围。
- 控制会话上下文。
- 把长期规则写短。
- 把专项流程做成按需加载的 Skill / rules。
- 避免中途切模型、切 effort、改 MCP 或插件导致缓存失效。

## 最实用的技巧

### 1. 一件事一个会话 / 线程

**建议**：

- Claude Code：无关任务切换时用 `/clear`；长任务在自然断点用 `/compact <重点>`。
- Codex：一个线程只处理一个 coherent unit of work，不要把一个项目长期塞在同一个线程里。

**原因**：

- 旧对话、文件读取结果、工具输出会持续挤占上下文。
- 上下文越大，每轮调用越容易浪费 token，也更容易让 agent 被旧信息干扰。

### 2. Prompt 用「4 段式」

推荐模板：

```text
目标：只做 X。
上下文：重点看 A/B/C 文件；不要全仓库扫描。
约束：只做最小改动；不要重构无关代码。
完成标准：跑某个最小测试 / lint / 复现命令，通过后停止。
```

这样可以减少 agent 的探索范围，避免它因为任务模糊而全仓库搜索、反复读文件。

### 3. `CLAUDE.md` / `AGENTS.md` 要短

**建议**：

- 只放每次任务都需要知道的内容，例如项目结构、构建命令、测试命令、核心约束。
- 不要把长流程、低频规范、专项 Review 清单全部塞进去。
- 如果文件开始变长，把专项内容拆到 Skill、rules、或单独 Markdown 文档。

**原因**：

- Claude Code 的 `CLAUDE.md` 会在 session 开始时加载。
- Codex 的 `AGENTS.md` 会自动进入上下文。
- 长规则文件会让每个任务都背上不相关的上下文成本。

### 4. 专项流程做成 Skill，而不是长 prompt

适合做成 Skill 的内容：

- PR Review 流程。
- 安全检查流程。
- Markdown 规范化流程。
- OpenSpec / spec 工作流。
- 仓库学习、架构梳理、测试生成等重复任务。

原因：

- Skill 通常按需加载。
- 平时只暴露名称、描述和路径，不会把完整正文一开始就塞进上下文。
- 复杂流程沉淀为 Skill 后，可以少解释、多复用。

### 5. 少开没用的 MCP / 插件 / 工具

**建议**：

- 不用的 MCP server 关掉。
- 能用 CLI 工具解决的，优先用 `gh`、`aws`、`gcloud`、`sentry-cli` 等命令。
- 不要为了「可能用得上」把一堆 MCP 和插件默认打开。

**原因**：

- MCP 工具定义、插件能力说明可能进入上下文或影响缓存。
- 工具越多，agent 决策空间越大，也越容易做多余探索。

### 6. 不要在长会话中途频繁切模型 / effort / fast mode

**建议**：

- 会话开始时先选好模型和 effort。
- 长会话中途尽量不要频繁切换。
- Codex 的 Fast mode 是「更快但消耗更多 credits」，不是省钱模式。

**原因**：

- Claude Code 的 prompt cache 依赖前缀精确匹配。
- 切模型、切 effort、连接 / 断开 MCP、启用 / 禁用插件、compact 等动作，都可能让下一轮请求重新处理大量上下文。

### 7. 模型和 reasoning 按任务难度选

**Claude Code**：

- 简单明确任务：优先用较便宜、较快的模型。
- 普通编码任务：常规模型即可。
- 复杂架构、多步推理、疑难 Debug：再切到更强模型。

**Codex**：

- 简单、边界清晰的小任务：低 reasoning。
- 多文件修改、复杂调试：Medium / High。
- 长链路、强推理、跨模块任务：Extra High。

原则：不要把所有任务都当成最高推理任务。

### 8. 大日志、大测试输出先过滤

**建议**：

- 不要直接把 10,000 行日志丢给 agent。
- 用 `grep`、`rg`、测试 runner 参数、hook 或脚本先筛选失败片段。
- 测试输出只给失败用例、错误栈、相关上下文。

例子：

```bash
pytest 2>&1 | grep -A 5 -E "(FAIL|ERROR|error:)" | head -100
```

收益：

- 从几万 token 降到几百 token。
- 减少 agent 被无关成功日志干扰。

### 9. Subagent 要克制使用

**适合使用 subagent 的场景**：

- 并行代码审查。
- 多方向根因排查。
- 大范围资料搜索。
- 希望把大量探索隔离在子上下文里，只让主线程拿摘要。

**不适合使用 subagent 的场景**：

- 单文件小改。
- 目标非常明确的小修复。
- 已经知道准确位置和验证命令的任务。

原因：每个 subagent 都会消耗自己的模型和工具调用，可能比单 agent 更耗 token。

### 10. 用 `.claudeignore` 排除无关目录

**适用**：Claude Code

**建议**：

在项目根目录创建 `.claudeignore`，语法与 `.gitignore` 相同，排除 `node_modules/`、`dist/`、`*.lock` 等大型或无关目录。

**原因**：

- 防止 agent 误读或索引无关文件。
- 减少全仓库搜索时扫到的文件量，降低每轮工具调用的 token 消耗。

### 11. 用 `@` 文件引用替代粘贴内容

**适用**：Claude Code

**建议**：

在 prompt 中写 `@src/foo.py`，让 Claude Code 自行读取，而不是把代码整段粘贴进对话框。

**原因**：

粘贴的内容以纯文本形式保留在对话历史中，每轮都重复计入输入 token；`@` 引用只在需要时读取，不会在历史中重复保存。

### 12. 缩短输出，省输出 Token

**建议**：

对明确任务，在 prompt 末尾加一句「直接给结论，不要解释步骤」或「只输出修改后的代码，不要附说明」。

**原因**：

输出 token 同样计费。每次响应如果减少 50% 的解释性文字，长期累积可以显著降低费用。

### 13. 用 `/cost` 主动监控消耗

**适用**：Claude Code

**建议**：

长 session 中途运行 `/cost`，查看当前 session 的 token 消耗明细，及时决定是否 `/compact` 或新开会话。

**原因**：

不看消耗很难感知哪步是「大头」。知道之后才能有针对性地优化。

### 14. 避免滥用 Extended Thinking

**建议**：

Extended Thinking（深度推理）的 token 用量可以是普通回复的 5–10 倍。只对确实需要多步推理的复杂任务开启，简单编辑、格式修复、单文件小改不要触发。

**原因**：

大多数编码任务并不需要深度推理。默认开启等于每次任务都按最贵档计费。

### 15. 用 `allowedTools` 缩小工具集

**适用**：Claude Code

**建议**：

在 `.claude/settings.json` 里通过 `allowedTools` 只暴露当前任务必要的工具，不用的工具不要默认打开。

**原因**：

- 减少 agent 的决策空间，降低不必要探索的概率。
- 工具定义本身也占用上下文，工具越多，每轮系统提示越重。

### 16. Claude Code 上下文窗口和压缩配置

**适用**：Claude Code

**上下文窗口大小**：

| 模式 | 大小 | 启用条件 |
|---|---|---|
| 标准窗口 | 200,000 tokens | 默认，所有模型（Sonnet / Opus / Haiku / Fable）一致 |
| 扩展窗口 | 1,000,000 tokens | 使用 `sonnet[1m]` / `opus[1m]` 别名；仅 Max / Team / Enterprise 计划可用 |

**自动压缩触发时机**：

当剩余可用上下文 ≤ 13,000 tokens 时自动触发（即对话内容超过约 167K tokens）。

压缩策略：优先清理旧的工具输出 → 再摘要对话历史 → 保留 CLAUDE.md 和关键代码片段。

**手动控制命令**：

| 命令 | 作用 |
|---|---|
| `/context` | 查看当前窗口占用情况 |
| `/compact [focus]` | 手动压缩，可指定保留重点，如 `/compact focus on API changes` |
| `/clear` | 清空全部历史，完全重启 |

**配置项**：

`autoCompactEnabled` 写入 `~/.claude.json`（**不是** settings.json，写进 settings.json 无效）：

```json
{
  "autoCompactEnabled": false
}
```

环境变量（写在项目 `.claude/settings.json` 的 `env` 块）：

| 变量名 | 含义 | 默认值 | 备注 |
|---|---|---|---|
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | 触发压缩的上下文占用百分比 | ~95% | 代码内有硬上限，设置超过约 83% 无效（非官方确认） |
| `CLAUDE_CODE_AUTO_COMPACT_WINDOW` | 用于压缩计算的有效窗口大小（tokens） | 模型原生窗口（200K） | 可缩小有效窗口，再配合百分比触发 |
| `DISABLE_AUTO_COMPACT` | 完全禁用自动压缩 | 未设置（启用） | 设为 `true` 禁用 |

组合用法示例（更早触发压缩）：

```json
{
  "env": {
    "CLAUDE_CODE_AUTO_COMPACT_WINDOW": "150000",
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "80"
  }
}
```

效果：当对话内容达到 12 万 tokens（150K × 80%）时触发压缩。

**建议**：

- 长任务在七成占用时主动 `/compact`，避免被动压缩丢失关键信息。
- 在 CLAUDE.md 中加 `# Compact instructions` 章节，指定压缩时优先保留哪类内容。

### 17. Codex 上下文窗口和压缩阈值

**适用**：Codex

**结论**：

- Codex 的上下文窗口不是固定值，而是随模型变化；不配置时使用模型或 preset 默认值。
- 当前线程内的 prompt、模型输出、工具调用、工具输出、读取的文件内容等，都要放进模型的 context window。
- 长任务中 Codex 可能自动 compact；CLI 可用 `/compact` 手动总结对话并释放 tokens。

**配置文件**：

全局配置：

```text
C:\Users\<用户名>\.codex\config.toml
```

项目级配置：

```text
<repo>\.codex\config.toml
```

项目级配置优先级高于全局配置；项目 `.codex/` 层只在信任项目后加载。

**建议配置**：

```toml
# 默认让 Codex 按模型自动识别上下文窗口；除非你非常确定，否则别手动改
# model_context_window = 128000

# 自动压缩触发阈值，越低越早 compact
model_auto_compact_token_limit = 64000

# 每个工具输出最多保留多少 tokens，避免大日志污染上下文
tool_output_token_limit = 12000
```

**使用建议**：

- 平时优先调 `model_auto_compact_token_limit` 和 `tool_output_token_limit`，不要先改 `model_context_window`。
- 长任务自然断点可以手动执行 `/compact`，先让 agent 总结「当前决策、关键文件、未完成事项、验证命令」。
- 如果只想影响一个仓库，把配置放到该仓库的 `.codex/config.toml`；如果希望所有仓库都生效，再放到全局 `~/.codex/config.toml`。

## 社区信号

### GitHub

Claude Code 和 Codex 都有官方 GitHub 仓库，仓库 README 都把官方文档作为主要入口。省 token 策略仍应以官方文档为准，GitHub 仓库更适合查看安装方式、已知问题、插件和开源实现。

### X / 媒体报道

围绕 Claude Code Review 的讨论集中在「深度 Review 会消耗更多 compute / token」上。媒体报道提到，Claude Code Review 这类深度检查可能按 PR 复杂度产生较高费用。实践结论是：

- 小 PR 不要无脑跑深度、多 agent Review。
- 先用轻量检查和最小测试覆盖基础问题。
- 只有复杂、高风险 PR 再启用更深的 Review。

### Reddit

我只找到 Reddit 相关二手报道，未找到足以直接引用的一手帖子。二手报道中有人声称，通过依赖图式上下文层可以让 Claude Code 更快、更省。这个案例不能直接当通用事实，但可借鉴的方向是：

- 先定位相关代码。
- 再把最小必要上下文交给 agent。
- 避免让 agent 盲目全仓库搜索。

## 我的默认实践清单

每次开任务前，先确认：

- 这是不是一个独立任务？如果不是，拆小。
- 是否有明确文件范围？如果有，直接告诉 agent。
- 是否有明确验证命令？如果有，直接写进 prompt。
- 是否需要高 reasoning？如果不需要，先用低 / 中档。
- 是否需要 subagent？如果只是小改，不要开。
- 当前会话是否已经混入太多无关上下文？如果是，先 `/clear` 或新开线程。
- 是否把代码粘贴进了对话框？改用 `@` 文件引用。
- 是否需要 Extended Thinking？如果是简单任务，关掉。
- prompt 末尾是否要求了简洁输出？如果没有，加一句。

## 推荐 Prompt 模板

```text
请只完成以下任务：

目标：
- [写清楚要完成什么]

范围：
- 重点查看：[文件或目录]
- 不要修改：[文件或目录]

约束：
- 只做最小改动。
- 不要重构无关代码。
- 如果发现不确定点，先停下来说明。

验证：
- 修改后运行：[命令]
- 如果命令失败，先分析失败原因，不要扩大修改范围。

交付：
- 简述改动点。
- 给出验证结果。
```

## 参考资料

- [Claude Code：Manage costs effectively](https://docs.anthropic.com/en/docs/claude-code/costs)
- [Claude Code：Explore the context window](https://code.claude.com/docs/en/context-window)
- [Claude Code：Prompt caching](https://code.claude.com/docs/en/prompt-caching)
- [Claude Code：Best practices](https://code.claude.com/docs/en/best-practices)
- [Claude Code：How Claude remembers your project](https://docs.anthropic.com/en/docs/claude-code/memory)
- [Codex：Best practices](https://developers.openai.com/codex/learn/best-practices)
- [Codex：Prompting](https://developers.openai.com/codex/prompting)
- [Codex：AGENTS.md](https://developers.openai.com/codex/guides/agents-md)
- [Codex：Skills](https://developers.openai.com/codex/skills)
- [Codex：Subagents](https://developers.openai.com/codex/subagents)
- [Codex：Speed](https://developers.openai.com/codex/speed)
- [GitHub：anthropics/claude-code](https://github.com/anthropics/claude-code)
- [GitHub：openai/codex](https://github.com/openai/codex)
- [Business Insider：Claude Code Review token cost discussion](https://www.businessinsider.com/anthropic-claude-code-review-token-costs-developers-backlash-engineers-2026-3)
- [Economic Times：Reddit 二手报道与 GrapeRoot 案例](https://m.economictimes.com/news/new-updates/100k-savings-in-3-months-techie-says-claude-code-is-now-2x-faster-3x-cheaper-using-this-tool/articleshow/131522412.cms)
- [Codex：Config basics](https://developers.openai.com/codex/config-basic)
- [Codex：Configuration Reference](https://developers.openai.com/codex/config-reference)
- [Codex：CLI slash commands](https://developers.openai.com/codex/cli)
