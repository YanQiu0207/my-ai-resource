# CodeGraph 安装、使用与卸载指南

> 快照日期：2026-07-12  
> 适用项目：[colbymchenry/codegraph](https://github.com/colbymchenry/codegraph)  
> 说明：本文依据官方 README 整理，尚未在本机实际安装验证。

## 结论

CodeGraph 适合通过 Codex CLI、Claude Code、Cursor 等编码 Agent 快速查找代码入口、调用链和修改影响范围。它会在项目内生成 `.codegraph/` 索引，并通过文件监听自动同步代码变更。

推荐先用交互式安装器完成 Agent 接线，再进入每个目标仓库执行 `codegraph init`。安装 Agent 配置和建立项目索引是两个独立步骤。

## 前置条件

- 安装 Node.js 和 npm。
- 确认终端可以执行 `npm`。
- 安装器可能修改 Agent 的 MCP 配置、指令文件和权限配置。执行前建议提交或备份相关文件。

检查环境：

```bash
node --version
npm --version
```

官方 README 说明，CodeGraph 的 CLI 和 MCP server 使用自包含运行时；只有把 npm 包作为 JavaScript Library API 嵌入应用时，才要求宿主使用 Node.js 22.5 或更高版本。

## 安装

### 方式一：全局安装

```bash
npm install -g @colbymchenry/codegraph
codegraph install
```

`codegraph install` 会交互式执行以下操作：

- 检测 Claude Code、Cursor、Codex CLI、Gemini CLI 等已安装 Agent。
- 选择全局配置或仅配置当前项目。
- 写入所选 Agent 的 MCP server 配置。
- 在 Agent 指令文件中写入带标记的 CodeGraph 使用说明。
- 为 Claude Code 配置可选的自动允许权限。

安装后重启编码 Agent，使 MCP 配置生效。

### 方式二：不全局安装，直接运行安装器

```bash
npx @colbymchenry/codegraph
```

该命令会下载并运行 CodeGraph 安装器，适合快速试用。

### 非交互式安装

自动检测并配置 Agent：

```bash
codegraph install --yes
```

只配置 Codex CLI 和 Claude Code：

```bash
codegraph install --target=codex,claude --yes
```

只生成某个 Agent 的配置片段，不写文件：

```bash
codegraph install --print-config codex
```

如果不希望安装器写入 Claude Code 的自动允许权限：

```bash
codegraph install --no-permissions
```

## 首次使用

### 1. 为项目建立索引

进入目标代码仓库：

```bash
cd /path/to/project
codegraph init
```

索引保存在项目的 `.codegraph/` 目录中。全局安装只需执行一次，但每个需要分析的项目都要分别执行一次 `codegraph init`。

### 2. 检查索引状态

```bash
codegraph status
```

CodeGraph 会监听源文件变化，并在默认 2 秒静默窗口后增量同步。Agent 重新连接时还会检查工作区变化，吸收 MCP server 未运行期间发生的修改。

在文件监听不可用或被禁用时，可以手动同步：

```bash
codegraph sync
```

需要完整重建索引时：

```bash
codegraph index --force
```

## 在编码 Agent 中使用

安装、初始化项目并重启 Agent 后，可以直接提问：

- 「这个项目有哪些入口点？我应该先读哪些文件？」
- 「从 HTTP 路由到数据库访问的调用链是什么？」
- 「谁调用了 `ProcessOrder`？它又调用了哪些函数？」
- 「修改 `UserService` 会影响哪些模块和测试？」
- 「梳理认证模块的核心符号、源码和关系。」

CodeGraph 默认向 MCP 暴露主要工具 `codegraph_explore`。一次查询可返回相关源码、调用路径、符号关系和影响范围摘要，减少 Agent 反复执行 `grep` 和逐文件读取。

如果某个项目没有 `.codegraph/` 索引，CodeGraph 会提示 Agent 回退到内置代码搜索工具，不会自动决定为项目建立索引。

## 命令行使用

### 搜索符号

```bash
codegraph query UserService
```

### 查看相关源码和调用关系

```bash
codegraph explore "How does authentication work?"
```

### 查看单个符号或文件

```bash
codegraph node UserService
codegraph node src/services/user.ts
```

### 查询调用方和被调用方

```bash
codegraph callers ProcessOrder
codegraph callees ProcessOrder
```

### 分析影响范围

```bash
codegraph impact ProcessOrder
```

### 根据改动筛选受影响的测试

```bash
git diff --name-only | codegraph affected --stdin
```

只输出测试文件路径：

```bash
git diff --name-only | codegraph affected --stdin --quiet
```

### 查看项目文件结构

```bash
codegraph files
```

## 更新

检查并安装新版本：

```bash
codegraph upgrade
```

只检查是否存在新版本：

```bash
codegraph upgrade --check
```

查看当前版本：

```bash
codegraph version
```

## 卸载

### 1. 删除项目索引

在目标项目中执行：

```bash
codegraph uninit
```

跳过确认：

```bash
codegraph uninit --force
```

该命令删除当前项目的 `.codegraph/` 索引。每个已初始化项目都需要分别处理。

### 2. 删除 Agent 配置并卸载 CLI

```bash
codegraph uninstall
```

该命令会移除 CodeGraph 写入的 MCP 配置、指令标记和权限配置，并卸载 CLI；项目中的 `.codegraph/` 索引不会随之删除。

如果只想删除 Agent 配置并保留 CLI：

```bash
codegraph uninstall --keep-cli
```

只清理指定 Agent：

```bash
codegraph uninstall --target=codex,claude
```

非交互式卸载：

```bash
codegraph uninstall --yes
```

### 3. 验证卸载结果

- 检查目标项目中是否还存在 `.codegraph/`。
- 重启 Agent，确认 CodeGraph MCP server 不再出现。
- 如果未使用 `--keep-cli`，检查 `codegraph version` 是否已无法执行。
- 检查 Agent 指令文件和 MCP 配置中是否还存在手动添加的 CodeGraph 内容。

## 验收清单

- [ ] `codegraph version` 能输出版本。
- [ ] 重启 Agent 后能识别 CodeGraph MCP server。
- [ ] 目标项目执行 `codegraph init` 成功。
- [ ] `codegraph status` 能显示项目索引状态。
- [ ] Agent 能定位入口点、调用链和影响范围。
- [ ] 修改源文件后，索引能够自动同步或通过 `codegraph sync` 更新。
- [ ] `codegraph affected` 能根据变更文件给出候选测试。
- [ ] 卸载前已确定是否需要保留项目中的 `.codegraph/` 索引。

## 使用边界

- CodeGraph 基于静态分析建立关系图，动态注册、反射、依赖注入和配置驱动调用可能无法完整识别。
- 影响分析结果用于缩小排查和测试范围，不能替代完整测试与源码验证。
- Agent 只有主动调用 CodeGraph 时才能获得收益；如果仍然大量使用普通搜索和逐文件读取，CodeGraph 可能只会增加额外开销。
- 索引结果引用待同步文件时，CodeGraph 会提示内容可能过期；此时应直接读取最新源码或等待同步完成。

## 事实来源

- [CodeGraph README](https://github.com/colbymchenry/codegraph)：安装、Agent 接线、项目初始化、自动同步、CLI、MCP 工具、更新和卸载说明。
- [CodeGraph 官方文档](https://colbymchenry.github.io/codegraph/)：索引、查询和使用指南。
