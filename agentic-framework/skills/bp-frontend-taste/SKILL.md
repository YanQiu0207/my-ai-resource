---
name: bp-frontend-taste
description: 前端视觉质量基准。生成 HTML 方案或写 UI 组件时加载，确保达到「用起来舒服、看起来专业」的基线。参考 taste-skill 社区实践。
---

> 输出一行：`Using bp-frontend-taste`

# 前端视觉质量基准

> 核心原则：**用起来舒服，看起来专业，不过度设计。**

---

## 1. 间距与节奏

- 使用 4/8px 为基础单位（Tailwind 默认间距系统）
- 相关元素间距小，不相关元素间距大（亲密性原则）
- 内容区最大宽度：阅读场景 `max-w-3xl`，应用场景 `max-w-7xl`
- 页面边距：移动端 `px-4`，桌面端 `px-6` 或 `px-8`

**禁止**：随意使用 13px、22px 等非 4 倍数值；禁止内容撑满整个视口宽度。

## 2. 字体与文本

- 正文：`text-base`（16px），最小 `text-sm`（14px）
- 标题层级最多 3 级（h1 / h2 / h3），层级差异须视觉明显
- 行高：正文 `leading-relaxed`（1.625），标题 `leading-tight`（1.25）
- 正文颜色：`text-gray-900` 或 `text-gray-800`，不用纯黑 `#000`
- 辅助文字：`text-gray-500`，禁止低于 `text-gray-400`（对比度不足）

**禁止**：正文 12px；全大写超过 3 个英文单词；大段文字无行高控制。

## 3. 颜色系统

- 主色 + 中性灰阶 + 3 种语义色（成功绿 / 警告黄 / 错误红）
- 正文与背景对比度 ≥ 4.5:1（WCAG AA）
- 主色系只取一个色相的 2-3 个深浅变体（如 `blue-500` / `blue-600` / `blue-700`）

**禁止**：超过 4 种主色调；直接用设计师色票中未出现的颜色；用饱和度极高的颜色做大面积背景。

## 4. 组件完整状态

每个交互元素必须设计所有状态，缺一不可：

| 元素 | 必须有的状态 |
|------|------------|
| 按钮 | default / hover / active / disabled / loading |
| 输入框 | default / focus / error / disabled |
| 链接 | default / hover / visited |
| 可点击卡片 | default / hover / active |

**空态、加载态、错误态**对每个数据展示区域同样必须设计：
- **空态**：说明为何为空 + 引导操作（不只是「暂无数据」）
- **加载态**：Skeleton 骨架屏优于 Spinner（减少布局抖动）
- **错误态**：说明出错原因 + 提供重试入口

## 5. 响应式

- Mobile-first：先写基础样式，用 `md:` / `lg:` 覆盖
- 必须测试的断点：375px（手机）/ 768px（平板）/ 1280px（桌面）
- 禁止固定宽度导致移动端横向滚动
- 表格在移动端须可横向滚动或转为卡片布局

## 6. 微交互

- 颜色过渡：`transition-colors duration-150 ease-in-out`
- 位移过渡：`transition-transform duration-200`
- 禁止：可点击元素无任何 hover / active 反馈；动画超过 300ms（除 page transition）

## 7. 常见反模式速查

| ❌ 低质量 | ✅ 正确做法 |
|---------|-----------|
| 按钮只有默认态 | 完整 5 态 |
| 文字撑满视口 | 限制 max-w，提升可读性 |
| 颜色随意堆叠 | 系统性颜色 token |
| 「暂无数据」空态 | 说明原因 + 引导操作 |
| Spinner 覆盖整页 | Skeleton 骨架屏 |
| 移动端横向溢出 | Mobile-first + 断点测试 |
| 没有 focus 样式 | `focus:ring-2 focus:ring-offset-2` |
