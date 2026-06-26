---
name: workflow-frontend-design
description: 前端 UI 设计工作流。代码实现前生成 2-3 个 HTML 静态方案让用户在浏览器中预览选择，产出 UI 规格，作为 workflow-code-generation 的视觉契约。
---

> 输出一行：`Using workflow-frontend-design`

# 前端 UI 设计

## 适用场景

任何涉及用户界面的功能，在 spec 确认后、代码实现前调用：
- 新页面 / 新组件
- 现有页面的大幅改版
- 交互流程设计

极轻 UI 调整（仅改样式 / 修文案）→ 跳过，直接进 `workflow-code-generation`。

## 前置条件

**需要用户在本机有 Chrome 或已安装 Playwright**。开始前确认：

```
UI 方案需要在浏览器中预览。请确认你有以下任一工具：
- Chrome / Edge / Safari（直接打开 HTML 文件预览）
- Playwright（已安装：npx playwright --version）
```

---

## 工作流程

### Step 1：理解 UI 需求

**防御性检查**：先确认 `docs/design-docs/<module>/<feature>/spec.md` 存在。若不存在，立即停止并告知用户：

```
缺少 spec.md，无法提取 UI 需求。请先运行 /requirements-clarification 或 /quick-design 生成功能规格，再调用本工作流。
```

spec.md 存在后，从中提取：
- 页面 / 组件的功能目标与用户场景
- 数据结构（展示哪些字段、哪些是核心信息）
- 已知约束（品牌色 / 现有组件库 / 响应式要求）

如界面需求有明显信息缺口，一次问完（不分轮）。信息足够则直接进入 Step 2。

### Step 2：生成 HTML 方案

**不询问用户**，直接生成 **2-3 个** 设计方向各异的静态 HTML 文件：

- 单文件，Tailwind CSS CDN 引入，无需构建工具即可在浏览器直接打开
- 每个方案体现不同设计方向，例如：
  - 方案 A：简约 / 信息克制
  - 方案 B：信息密度高 / 功能导向
  - 方案 C：卡片式 / 视觉层次强
- 每个方案必须包含：正常态 / 空态 / 加载态 / 错误态

加载 `bp-frontend-taste` 确保视觉质量达标。

**文件路径**：`docs/design-docs/<module>/<feature>/ui-mockup-A.html`（B、C 以此类推）

### Step 3：用户选择

生成完告知用户：

```
已生成 N 个 UI 方案，请在浏览器中打开对比：

- 方案 A（路径）：[一句话描述设计方向]
- 方案 B（路径）：[一句话描述设计方向]
- 方案 C（路径，如有）：[一句话描述设计方向]

请告知选择哪个方案，或需要融合哪些元素。
```

等待用户选择。

### Step 4：迭代调整（通常 1-2 轮）

根据用户反馈在选定方案基础上调整，直到用户确认。

### Step 5：产出 UI 规格

将确认方案整理为 `docs/design-docs/<module>/<feature>/ui-spec.md`：

```markdown
# UI 规格：<feature>

## 选定方案
[方案 X，一句话描述]

## 组件清单
- [组件名]：[职责]

## 交互行为
- hover / focus / active 状态
- 空态：[描述]
- 加载态：[描述]
- 错误态：[描述 + 重试入口]

## 响应式断点
- 移动端（< 768px）：[布局说明]
- 桌面端（≥ 1024px）：[布局说明]

## 关键设计决策
- [决策 + 原因]
```

告知用户 UI 规格路径，**立即加载 `workflow-code-generation`**，并在步骤 2 中将 `ui-spec.md` 路径显式传入：

```
UI 规格已产出：docs/design-docs/<module>/<feature>/ui-spec.md
正在进入代码实现阶段，加载 workflow-code-generation（步骤 2 将一并读取 spec.md 与 ui-spec.md）。
```

---

## 强制规则

1. **先出方案再让用户选**：不问「你想要什么风格」，直接给 2-3 个方向
2. **HTML 必须单文件、可直接在浏览器打开**：禁止依赖 npm / 构建步骤
3. **必须包含非正常态**：空态 / 加载态 / 错误态，禁止只做 happy path
4. **必须加载 `bp-frontend-taste`**：确保视觉质量基线

## 反模式

| ❌ | ✅ |
|----|-----|
| 问「你喜欢什么风格？」 | 直接生成 2-3 个不同方向 |
| HTML 需要 npm install 才能预览 | Tailwind CDN，单文件直接开 |
| 只有正常态 | 包含空态、加载态、错误态 |
| 跳过 UI 设计直接写代码 | 视觉契约先于实现 |
