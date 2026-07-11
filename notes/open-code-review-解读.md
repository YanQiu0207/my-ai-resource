# Open Code Review 解读

> 来源：<https://github.com/alibaba/open-code-review>
> 阿里巴巴开源的 AI 代码审查 CLI 工具，Apache-2.0，约 10.4k star。
> 整理日期：2026-07-11

## 一句话概括

Open Code Review（简称 `ocr`）是阿里开源的命令行 AI 代码审查工具，脱胎于阿里内部经过两年、覆盖数千开发者打磨的系统。它的核心主张是「确定性工程 × Agent 混合」架构——用工程逻辑兜底关键步骤的正确性，把动态判断交给 LLM，从而在保证行级定位精度的同时大幅降低 token 消耗。

## 它要解决什么问题

通用 AI Agent 直接做代码审查有三个典型毛病：

1. **覆盖不全**：面对大改动集，Agent 会「挑着看」，漏掉重要文件。
2. **定位漂移**：报出来的问题经常对不上真实代码位置，行号不准。
3. **质量不稳**：纯自然语言驱动缺少硬约束，审查质量忽高忽低。

根因是：**纯语言驱动的架构无法保证确定性任务的正确性**。ocr 的思路就是把「哪些文件要审、审查单元怎么分、行号怎么定位」这类确定性问题从 LLM 手里拿走，交给工程代码处理。

## 架构：确定性工程 × Agent 混合

### 确定性层（硬约束，保证正确性）

- **精确文件选择**：确定性地判断哪些文件需要审查，不漏改动。
- **智能文件打包**（file bundling）：把相关文件分组成审查单元，每个单元作为隔离的子 Agent 并发执行。
- **细粒度规则匹配**：基于模板引擎做规则匹配，聚焦模型注意力，替代靠自然语言「提醒」模型的做法。
- **外部定位与反思模块**：独立模块系统性地提升行号定位与内容准确性。

### Agent 层（动态决策，发挥 LLM 所长）

- **场景调优的 Prompt**：针对代码审查场景专门优化的模板。
- **专用工具集**：工具集来自对生产环境调用轨迹的分析，稳定、可预测（文件查看、代码搜索、上下文检索等）。

## 效果数据（对比 Claude Code）

在相同底座模型下，对比通用 Agent（Claude Code）：

| 指标 | ocr 表现 |
| --- | --- |
| F1 | 显著更高 |
| Precision（准确率） | 大幅提升，误报更少 |
| Recall（召回率） | 有意做低——宁可漏报也不制造噪音 |
| Token 消耗 | 约为通用 Agent 的 **1/9** |

评测规模：**50 个开源仓库、200 个真实 PR、10 种编程语言**，由 **80+ 位资深工程师标注、共 1505 个问题**做基准。

> 一句话读懂它的取舍：**牺牲部分召回，换取高准确率 + 极低成本**。适合 CI 里做「高信噪比」把关，而不是追求「一个都不漏」。

## 核心功能

### 1. 基于 diff 的审查：`ocr review`

- 分析两个 ref/commit 之间的 Git diff。
- 生成带精确行号的结构化审查评论。
- 支持断点续跑（resumable session）。
- 可输出机器可读的 JSON，便于 CI 集成。

### 2. 全文件扫描：`ocr scan`

- 不依赖 diff，直接审查整个文件。
- 适合审计陌生代码库、迁移前分析。
- 可在非 git 目录工作（尊重 `.gitignore`）。
- 支持生成项目级摘要。

### 3. 内置规则集

针对常见缺陷做过微调的检测规则：

- **NPE**（空指针）
- **Thread Safety**（线程安全 / 并发竞争）
- **XSS**（跨站脚本）
- **SQL Injection**（SQL 注入）

### 4. 结构化输出

每条发现携带两个分类字段：

- **Category**：`bug` / `security` / `performance` / `maintainability` / `test` / `style` / `documentation` / `other`
- **Severity**：`critical` / `high` / `medium` / `low`

## 工作流程

1. 用户执行 `ocr review` 或 `ocr scan`。
2. 确定性管线识别出需要审查的文件。
3. 相关文件被打包成审查单元。
4. 对每个单元，Agent 接收场景化 Prompt → 调用工具（查看文件、搜索代码、检索上下文）→ 生成带精确定位的评论。
5. 反思模块校验并提升准确性。
6. 以 text 或 JSON 输出结构化结果。

### 会话管理

审查结果本地持久化在 `~/.opencodereview/sessions/`：

- `ocr session list`：列出已存会话
- `ocr session show <id>`：查看会话详情
- `--resume <id>`：续跑中断的审查
- `ocr viewer`：Web UI 浏览会话（默认 `localhost:5483`）

## 技术栈与环境

- **主语言**：Go（约 65%），前端部分为 TypeScript / JavaScript / HTML / CSS。
- **最低依赖**：Git ≥ 2.41。
- **支持平台**：Windows、macOS（Apple Silicon / Intel）、Linux（x86_64 / ARM64）。

## 支持的 LLM

采用 **provider 架构**，内置：

- **Anthropic**（Claude 系列）
- **OpenAI**（GPT 系列）
- **DashScope**（阿里百炼）
- **DeepSeek**
- **Z-AI**

也支持**自定义 provider**：指定 base URL、协议类型（`anthropic` 或 `openai`）、API 密钥、自定义 header / body。

> README 中出现的示例模型名：`claude-opus-4-6`、`claude-sonnet-4-6`、`gpt-4o`（仅为示例，非固定要求）。

## 集成方式

| 方式 | 说明 |
| --- | --- |
| **CLI** | 主接口，`ocr review / scan / config / session / viewer` 等 |
| **GitHub Actions** | 提供开箱即用的 composite Action，自动做 PR 行内评论、汇总评论、产物上传、重试与幂等 |
| **GitLab CI/CD** | 见 `examples/gitlab_ci/`，支持 MR 评论回帖 |
| **通用 CI** | `ocr review --from origin/main --to <sha> --format json` 输出 JSON，适配任意 CI |
| **Claude Code 插件** | `/plugin install open-code-review`，斜杠命令 `/open-code-review:review` |
| **Codex Skill** | `codex plugin marketplace add alibaba/open-code-review` |
| **Cursor 插件** | 市场搜索安装，`@Open Code Review review this branch against main` |
| **通用 Skill（MCP）** | `npx skills add alibaba/open-code-review` |

## 配置系统

### 规则优先级链（高 → 低）

1. `--rule` 命令行标志（显式覆盖，最高）
2. 项目配置 `<repo>/.opencodereview/rule.json`（可提交入库）
3. 全局配置 `~/.opencodereview/rule.json`
4. 内置系统默认规则（最低）

> 注：环境变量（`OCR_LLM_URL`、`OCR_LLM_TOKEN`、`OCR_LLM_MODEL` 等）用于 provider/model 配置，在 CI 场景优先级最高。

### 交互式配置（推荐）

```bash
ocr config provider    # provider 选择向导
ocr config model       # 模型选择
```

### 规则文件示例

```json
{
  "rules": [
    {
      "path": "src/**/Handler.java",
      "rule": "Validate all parameters for null values"
    }
  ],
  "include": ["src/main/**/*.java"],
  "exclude": ["**/generated/**"]
}
```

- 路径支持 `**` 递归、`{java,kt}` 花括号展开。
- 规则内容可内联文本，也可引用外部 markdown 文件。
- `merge_system_rule`：用户规则与内置系统规则合并。
- 默认排除测试文件（`**/*Test.java`、`**/__tests__/**` 等）。

## 安装

```bash
# NPM（推荐）
npm install -g @alibaba-group/open-code-review
ocr --version

# 一键脚本（macOS / Linux）
curl -fsSL https://raw.githubusercontent.com/alibaba/open-code-review/main/install.sh | sh

# 从源码构建
git clone https://github.com/alibaba/open-code-review.git
cd open-code-review && make build
```

## 进阶能力

- **MCP 扩展**：通过 stdio 接入外部工具（如 codegraph），扩展审查上下文。
- **可观测性**：集成 OpenTelemetry，支持 OTLP（gRPC / HTTP）导出遥测。
- **多模型切换**：`--model` 逐次覆盖，无需重配置。
- **audience 模式**：`--audience agent` 输出面向 Agent 的精简摘要，便于下游自动修复。

## 关键差异化总结

1. **Token 效率**：约为通用 Agent 的 1/9。
2. **准确优先**：刻意高 precision、低 recall，误报少。
3. **行级定位准**：确定性定位模块保证行号正确。
4. **质量稳定**：工程约束防漂移，已在阿里内部大规模验证。
5. **多 provider**：Anthropic / OpenAI / 自定义端点通吃。
6. **可续跑**：中断的审查可持久化并高效恢复。

## 值得借鉴的设计思想

对我们自己搞 AI 工程，这个项目最有参考价值的一点是它的**边界划分哲学**：

> 把「有唯一正确答案的确定性任务」（文件选择、单元切分、行号定位）交给工程代码；把「需要理解和判断的开放任务」交给 LLM。

这正是对抗「纯 Prompt 驱动质量不稳」的有效手段——不要指望用自然语言约束模型去精确完成本该由代码保证的事。这条经验对设计任何 Agent 系统都通用。
