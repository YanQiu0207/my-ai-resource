---
name: std-react
description: React 18 + TypeScript 前端编码规范。写 .tsx/.ts 前端文件时加载，定义技术栈选型、项目结构、类型安全、状态管理、数据获取、测试标准。
---

> 输出一行：`Using std-react`

# React + TypeScript 编码规范

> 技术栈选型依据：训练数据覆盖最广、社区最活跃、AI 代码生成质量最高的前端组合。

## 核心技术栈

| 层次 | 选型 | 版本 |
|------|------|------|
| UI 框架 | React | 18.x |
| 类型系统 | TypeScript | 5.x strict 模式 |
| 构建工具 | Vite | 5.x |
| 样式 | Tailwind CSS | 3.x |
| 状态管理 | Zustand | 4.x（客户端状态） |
| 数据获取 | TanStack Query（React Query） | 5.x |
| E2E 测试 | Playwright | 最新稳定版 |
| 单元测试 | Vitest + @testing-library/react | — |

**禁止**：class 组件；`any` 类型；直接操作 DOM（除非 ref 场景）；在组件内做副作用性数据获取（用 TanStack Query）。

---

## TypeScript 规则

```jsonc
// tsconfig.json 必须开启
{
  "compilerOptions": {
    "strict": true,           // 包含 noImplicitAny, strictNullChecks
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true
  }
}
```

- 优先 `interface` 声明对象形状，`type` 用于联合类型 / 工具类型
- Props 必须有类型声明，禁止 `FC<any>` 或省略 Props 类型
- API 响应用 Zod 或手写 type guard 校验，不能直接 `as ResponseType`
- 枚举用 `const` 对象 + `as const`，不用 `enum` 关键字（避免运行时开销）

---

## 组件规则

```tsx
// ✅ 标准函数组件
interface CardProps {
  id: string
  title: string
  description?: string
  onSelect: (id: string) => void
}

export function Card({ id, title, description, onSelect }: CardProps) {
  return (
    <div className="..." onClick={() => onSelect(id)}>
      {/* ... */}
    </div>
  )
}
```

- 每个文件只导出一个主组件（工具函数可并列导出）
- 组件名与文件名一致，均用 PascalCase
- 禁止在组件内定义子组件（会导致每次渲染重新创建）
- `key` 不能用数组索引（除非列表永不重排序）
- 副作用全部放 `useEffect`，清理函数必须返回

---

## 目录结构

```
src/
├── components/          # 可复用 UI 组件（无业务逻辑）
│   └── Button/
│       ├── Button.tsx
│       └── Button.test.tsx
├── features/            # 业务功能模块（页面级）
│   └── UserList/
│       ├── UserList.tsx
│       ├── UserList.e2e.ts   # Playwright E2E
│       ├── useUserList.ts    # 数据 hook
│       └── userStore.ts      # Zustand store（如需）
├── hooks/               # 通用 hooks
├── lib/                 # API 客户端、工具函数
└── types/               # 全局类型定义
```

---

## 状态管理

**Zustand**（客户端状态，如 UI 状态、用户偏好）：

```ts
// userStore.ts
import { create } from 'zustand'

interface UserStore {
  selectedId: string | null
  setSelectedId: (id: string | null) => void
}

export const useUserStore = create<UserStore>((set) => ({
  selectedId: null,
  setSelectedId: (id) => set({ selectedId: id }),
}))
```

**TanStack Query**（服务端状态，所有 API 数据）：

```ts
// useUserList.ts
import { useQuery } from '@tanstack/react-query'

export function useUserList() {
  return useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const res = await fetch('/api/users')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      return res.json()
    },
    staleTime: 5 * 60 * 1000,
  })
}
```

**禁止**：用 `useState` + `useEffect` 做数据获取；全局 Redux（Zustand 足够）。

---

## 测试标准

### 单元测试（Vitest + Testing Library）

```tsx
// Button.test.tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from './Button'

test('点击后调用 onClick', async () => {
  const onClick = vi.fn()
  render(<Button onClick={onClick}>提交</Button>)
  await userEvent.click(screen.getByRole('button', { name: '提交' }))
  expect(onClick).toHaveBeenCalledOnce()
})
```

- 测试**行为**，不测实现（不 assert 内部 state，测用户可见的结果）
- 用 `screen.getByRole` 优先（可访问性语义），次选 `getByText`，禁止 `getByTestId`（除非不得已）

### E2E 测试（Playwright）

- 每个核心用户流程必须有 E2E 覆盖（见 `workflow-test-generation` E2E 章节）
- 文件命名：`<feature>.e2e.ts`，放在 feature 目录内
- 前置条件：本地或 CI 环境已安装 `@playwright/test` 且 `npx playwright install` 已运行

---

## 性能规则

- `React.memo` 仅在 profiling 证明有收益时才加（不要预防性 memo）
- 列表渲染 > 100 条用虚拟化（TanStack Virtual）
- 图片用 `loading="lazy"` + 明确 `width`/`height` 避免 CLS
- 代码分割：路由级别用 `React.lazy` + `Suspense`

---

## 禁止事项速查

| ❌ 禁止 | ✅ 替代 |
|--------|--------|
| `any` 类型 | 明确类型或 `unknown` + type guard |
| `enum` 关键字 | `const` 对象 + `as const` |
| `useEffect` 获取数据 | TanStack Query |
| 数组索引作 `key` | 稳定唯一 ID |
| 组件内定义子组件 | 提到文件顶层或独立文件 |
| 直接 `as ResponseType` | Zod / type guard 校验 |
| 预防性 `React.memo` | 先 profile，再 memo |
