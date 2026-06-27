# 前端官方 Skills 本地化说明

## 结论

前端工作流不再依赖 Claude Code / Codex 的会话技能探测。

本框架已经把常用官方前端技能中文化后合并到本地：

| 本地 skill | 主要吸收来源 |
| --- | --- |
| `workflow-frontend-design` | Anthropic `frontend-design`、Anthropic `web-artifacts-builder`、OpenAI `frontend-app-builder` |
| `bp-frontend-layout` | `frontend-design` / `frontend-app-builder` 的布局与完整页面规则 |
| `std-react` | OpenAI `react-best-practices`、`shadcn-best-practices` |
| `bp-frontend-taste` | `frontend-design` / `frontend-app-builder` 的视觉质量标准 |
| `frontend-playwright-verification` | Anthropic `webapp-testing`、OpenAI `frontend-testing-debugging` |

## 本地链路

```text
workflow-frontend-design（设计方向 / ui-spec）
  → bp-frontend-layout（页面骨架）
  → workflow-code-generation + std-react（实现）
  → workflow-test-generation（测试任务）
  → bp-frontend-taste（视觉质检）
  → frontend-playwright-verification（浏览器验证）
```

## 闭环归属

闭环由本地 workflow 承担。官方技能的能力被拆到不同阶段使用：

1. 需求事实来自 `spec.md`。
2. 设计能力沉淀到 `workflow-frontend-design` 和 `ui-spec.md`。
3. 实现能力沉淀到 `workflow-code-generation`、`std-react` 和具体 tasks。
4. 测试 / 校验能力沉淀到 tasks.md 的测试任务、`bp-frontend-taste` 和 `frontend-playwright-verification`。
5. 交付前必须完成最终浏览器校验，失败则回到实现修复。

## 来源

- Anthropic skills：<https://github.com/anthropics/skills>
- Anthropic `frontend-design`：<https://github.com/anthropics/skills/tree/main/skills/frontend-design>
- Anthropic `web-artifacts-builder`：<https://github.com/anthropics/skills/tree/main/skills/web-artifacts-builder>
- Anthropic `webapp-testing`：<https://github.com/anthropics/skills/tree/main/skills/webapp-testing>
- OpenAI `build-web-apps`：<https://github.com/openai/plugins/tree/main/plugins/build-web-apps>
