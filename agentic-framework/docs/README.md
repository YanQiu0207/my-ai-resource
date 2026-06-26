# Agentic Framework — 设计与决策记录

> 本目录沉淀「为快速构建**大型但非生产**项目而特化这套框架」的全部讨论、选型依据与设计规格。

## 这个框架是什么

它是 `agentic-engineering-framework` 的一个**特化分支**，服务一类特定场景：

> **快速构建大型但非生产环境的工具/项目，既要快，又要保证质量。**

核心取舍一句话：**前期人把关（需求 + 设计），执行段 AI 自主并行跑**——质量基建（多维 review）不打折，但执行不再逐 task 停等。

## 与原框架的关系

- **复制**了原框架中与本场景相关的 `workflow-*` 全套及其运行依赖（`bp-*` / `std-*` / `project-knowledge` / `self-refinement` / `agents/` 评审 subagent / 命令入口）。
- **未复制** `opsx-*`（OpenSpec 复刻）等与本场景无关的部分。
- **改造** `workflow-code-generation`：把执行段从「逐 task 停等串行」升级为「复杂度路由 + 下放 agent 执行（极轻改动主会话直改、中等+ 单 / 并行 agent）」，是本框架相对原框架的核心增量。

## 文档索引

| 文档 | 内容 | 何时读 |
| --- | --- | --- |
| [01-why-and-methodology.md](01-why-and-methodology.md) | 为什么要这个框架 + 诉求画像 + 方法论 | 想知道动机和打法 |
| [02-tool-landscape.md](02-tool-landscape.md) | 选型调研（Spec Kit / Superpowers / OpenSpec / Taskmaster，带来源）+ 为什么基于 `workflow-*` 改造 | 想知道选型依据 |
| [03-parallel-execution-mode.md](03-parallel-execution-mode.md) | `code-generation` 执行段（下放 agent + 并行）的设计规格 | 实现 / 理解执行段时 |
| [04-compound-engineering-comparison.md](04-compound-engineering-comparison.md) | compound-engineering-plugin 调研 + 与本框架对比 + 吸收决策 | 了解知识沉淀机制设计依据时 |
| [05-industry-comparison.md](05-industry-comparison.md) | 与 Superpowers / OpenSpec / Spec Kit / Taskmaster / ce-compound 的横向对比 | 评估框架定位 / 选型决策时 |

## 一句话结论

**Superpowers 的执行形态（自主 + 并行 + subagent-driven）× `workflow-*` 的质量基建（分级 review + 复杂度路由）** —— 拿成熟范本补 `workflow-*` 唯一的执行短板，而不丢它比 Superpowers 强的那几样。
