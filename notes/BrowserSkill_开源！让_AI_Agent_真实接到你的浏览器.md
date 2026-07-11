# BrowserSkill 开源！让 AI Agent 真实接到你的浏览器

![图片](https://mmbiz.qpic.cn/sz_mmbiz_gif/W7W9IgARmG8QIl1wLoKuZTWmXwTBUHcCRgYOs3IkIPeKwVlnZyeIU55GicVVpZK7iahfMpspDMsMHAB9Qia0a7ptw/640?wx_fmt=gif&from=appmsg&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=0)

**导语**  AI Agent 能写代码、能查资料、能分析数据——但只要你让它"登录后台导出这个月的报表"，它立刻束手无策。因为 Agent 拿不到你的登录态，绕不过验证码，也分不清哪些操作该做、哪些不该做。

BrowserSkill 就是为此而生的：它让 AI Agent 接入你电脑上正在使用的真实浏览器，在你的登录态下、在你的视线内执行自动化任务。任务结束即归还控制权，全程透明、全程可控。

## 一、BrowserSkill 是什么

BrowserSkill 是腾讯开源的一套浏览器桥接方案。它在你的本机浏览器和 AI Agent 之间建立安全的通信链路，让 Agent 能够操作你真实登录的网页——而你始终握有控制权。

🔗 项目地址：https://github.com/Tencent/BrowserSkill

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/ggaaFhpMJaxbawhMT26JLMhHNgicxY7EVqVawSADs8QQibHWHTDqX0k9KsVrwJHY0L3dJGeqb905KxVUGKT0FJ165V9D5VkD1TaKZx1ltQbyY/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

工作机制很简单：

**① Agent 发起任务：**通过 `bsk CLI` 下发浏览器操作指令

**② 本机守护进程转发：**Daemon 将请求安全地传递给浏览器扩展

**③ Agent Window 隔离执行：**扩展在独立的 Agent Window 中完成自动化操作；必要时向用户发起借用（Borrow）请求，使用已有的标签页

![图片](https://mmbiz.qpic.cn/mmbiz_png/ggaaFhpMJaww7ucjyLNmmeAbhj0EnSflWJbzFgbyY0AL9IE6Bq1eBZ95xpaDcDuALncYqWWGP98efOia7ncic6ThnNMrdECOvteibUYH66Ssdg/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=2)

## 二、为什么需要

在使用传统浏览器自动化工具（Puppeteer、Playwright）或云端 Agent 服务时，你大概率遇到过这些问题：

| Field | Value |
| --- | --- |
| 痛点 | BrowserSkill 的解法 |
| **登录态断裂：远程/沙盒浏览器看不到你的账号内容** | 直连本机真实浏览器，直接复用你的登录态 |
| **多 Agent 互相干扰：多个 Agent 和用户抢一个浏览器实例** | Agent Window 独立窗口，与你日常浏览完全隔离 |
| **生态绑定：换一个 Agent 平台就得换一套工具** | 标准 CLI（bsk），一次安装，所有 Agent 通用 |
| **自动化中途卡死：遇到验证码、OTP、登录确认，Agent 无计可施** | Human-in-loop：Agent 主动暂停，把页面交给你处理 |
| **操作不透明：看不到 Agent 在做什么，缺乏安全感** | 所有操作在独立窗口清晰可见，敏感页面需显式借用 |

简而言之：你看到的页面 = Agent 看到的页面；你不给的权限 = Agent 拿不到。

这对涉及企业内部系统或私人账号的任务尤为重要。

## 三、与行业方案对比

目前行业里已有一些让 Agent 操作浏览器的方案，但它们大多绑定特定平台或模型，生态碎片化严重。BrowserSkill 定位为一个**开放的通用能力层**——同时内置 Borrow 机制和 Human-in-loop 的浏览器桥接方案。

| Column 1 | Column 2 | Column 3 | Column 4 | Column 5 | Column 6 | Column 7 |
| --- | --- | --- | --- | --- | --- | --- |
| 维度 | BrowserSkill | Playwright | Puppeteer | Claude in Chrome | Codex ext | Kimi WebBridge |
| 登录态复用 | ✅ 支持 | ⚠️ 有限（需手动配置持久化存储） | ⚠️ 有限 | ✅ | ✅ | ✅ |
| 适配范围 | 任意 Agent（MCP/CLI） | 编程API+MCP server | 编程 API | Claude 生态 | Codex app | 任意 Agent |
| 开源 | ✅ 开源 | ✅ 开源 | ✅ 开源 | 闭源 | 闭源 | 闭源 |
| 权限模型 | Agent Window 沙盒 + 标签页借用（Borrow） | 无隔离，全浏览器控制 | 无隔离，全浏览器控制 | 标签页级，随Claude 授权 | 信息待确认 | 站点级权限确认 |
| 人机协作 | ✅ 内建<br>request-help | 需自行实现 | 需自行实现 | 依赖 Agent能力（非独立 bridge 层） | 依赖 Agent能力 | 依赖 Agent能力 |
| 数据隐私 | 不离开本机 | 取决于用法 | 取决于用法 | 取决于用法 | 取决于用法 | 取决于用法 |

**选择建议：**如果你只用某一个官方 Agent（如 Claude），官方扩展也许是最省心的选择；但如果你希望一套浏览器自动化能力被多个 Agent 共同复用，BrowserSkill 的通用性和安全性将带来不可替代的价值。

## 四、能做什么

BrowserSkill 不是为了炫技式地控制浏览器——它解决的是**需要登录、需要点击、需要确认**的真实场景。

### 📧 场景一：登录态网页总结

让 Agent 打开你已经登录的页面，对内容进行总结和提炼。比如：

-   汇总 Gmail 中本周未回复的重要邮件
    
-   整理知乎收藏夹、B 站"稍后再看"列表
    
-   抓取公司内部看板数据，生成周报摘要
    

_为什么传统方案做不到：远程浏览器没有你的登录 Cookie，无法访问需要登录的页面；API 方案则需要繁琐的 Token 配置。_

### 📋 场景二：表单与数据录入

把本地的 CSV 文件、任务列表或 Excel 数据，让 Agent 一条条自动录入 Web 系统。比如：

-   批量导入客户信息到 CRM
    
-   将面试评估表中的候选人数据同步到招聘系统
    
-   按日自动填写工时系统
    

### 🔍 场景三：多站点信息检索与整理

跨多个平台检索、对比、归纳，最终输出一份结构化的结果。比如：

-   扫描得到、微信读书笔记、豆瓣书单，整理成个人月度阅读报告
    
-   在多个招聘平台搜索同一岗位，汇总薪资、要求和投递链接
    
-   跨电商平台比价，生成一份最优购买方案
    

### 🤝 场景四：人机协作流程

Agent 负责可自动化的繁琐步骤，人只在关键节点介入：

-   Agent 自动填写长表单，遇到验证码时暂停，交给用户处理，完成后继续
    
-   用户手动完成复杂的前置流程（如多级审批），再由 Agent 接管后续操作
    
-   Agent 生成操作结果，用户最终审核确认后提交
    

## ⚡ 1 分钟快速开始

### 第 1 步：安装 CLI 与配置

在 WorkBuddy、Cursor、Claude Code 或其他支持的 Agent 中，发送以下指令：

Set up browser-skill on this machine by following  
https://raw.githubusercontent.com/Tencent/BrowserSkill/main/AGENT\_INSTALL.md

Agent 会自动完成 CLI 安装和 Skill 配置。

### 第 2 步：安装浏览器扩展

从 Chrome Web Store 安装 BrowserSkill 扩展：

🔗 https://chromewebstore.google.com/detail/hhcmgoofomhgciiibhipgmgkgnoenaoi

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/ggaaFhpMJaww1cAE5mNeQLBqNdU6MPib5iaO7xvpSicQFiaC6wI4MGDugkCRYESkEusGHekd3YA8jTu2UHdiaftKlUsZVichhoH5fVFYgL7BoA2X0/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=3)

安装完成，即可使用。

### 已支持一键安装的 Agent

**AI 编程助手：**WorkBuddy · CodeBuddy · Cursor · Claude Code · Codex

**通用 Agent：**OpenClaw · Pi · Hermes Agent

如果你常用的 Agent 不在列表中？欢迎来 GitHub：https://github.com/Tencent/BrowserSkill 提 Issue，或直接提交 PR 添加支持。

## 📱 应用案例

**场景：**让 Agent 在小红书上搜索 "BrowserSkill" 相关信息并汇总结果。

❌ 未使用 BrowserSkill

在 WorkBuddy 中直接输入指令：

查找小红书上关于 BrowserSkill 的帖子

Agent 无法直接访问需要登录的小红书页面。退而通过通用搜索引擎进行间接检索，搜索结果不完整、不够及时，最终的回答质量受到明显影响。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/ggaaFhpMJazmDYzw7iaoPEs5fSFqJ333iaRfJibC3qW0XP8Q4jXwC5IYVL142gkRZ2YSMQrAicyBD8oJnNRcTH52HVu8jMaTEFZMRvH9m3XjbEQ/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=4)

✅ 使用 BrowserSkill

在 WorkBuddy 中使用 BrowserSkill 技能并输入指令：

@skill:browser-skill 查找小红书上关于 BrowserSkill 的帖子

整个过程，Agent 的每一步操作都在独立窗口中清晰可见；用户的日常浏览器标签页不会受到任何干扰。

## 🏗️ 技术架构

BrowserSkill 的工作流设计遵循三个原则：

![图片](https://mmbiz.qpic.cn/mmbiz_png/ggaaFhpMJaxX9Vj6oXkc3r55CWs9PpxFqODdA6uJV0dWPG0MhJRq2od9z0LrDWaoMtzic0N9wZicxP9VjL5eBk4DICL5ukkPKUiaF8iac2O2L30/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=7)

🔒 **本机桥接：**浏览器扩展只连接本机 Daemon，不直接连接远程 AI 服务。所有通信发生在你的机器内部，不存在数据外泄风险。

🧩 **会话隔离：**每个 Agent Session 绑定一个独立的 Agent Window。自动化写操作默认限制在 Agent Window 内，保护用户的日常浏览不受影响。

👤 **用户控制：**已有标签页的访问需要显式借用（Borrow）；Human-in-loop 机制确保验证码、OTP、敏感确认等关键步骤可以随时交还给用户——你可以先手动处理，再把页面交还 Agent 继续。

现在就开始

BrowserSkill 不追求"炫技式地操控浏览器"。它只做一件事：让 Agent 替你完成那些需要登录、需要点击、需要确认的真实工作——同时把控制权 100% 留在你手里。

⭐ **Star & Try：**https://github.com/Tencent/BrowserSkill（MIT 协议）

🔧 **一键安装：**在任意支持的 Agent 中发送安装指令，3 分钟完成配置

🐛 **提 Issue：**遇到问题或希望支持新的 Agent？欢迎提交 Issue

💬 **加入社群：**扫码加入官方交流群，与开发团队直接沟通

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/ggaaFhpMJaxa45vRIABBQH1sIuFydaQGSPZwE5ffI5NObWYKDAbbLswzTG9y586bLl3dsg7N9bOtoxUgGM5W8kQ4eMUeTFbdMpcO4eDEX1c/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=8)

关注腾讯开源公众号

获取更多最新腾讯官方开源信息！

---

## 个人评估结论

**当前不安装 BrowserSkill，继续使用 Playwright。**

BrowserSkill 的突出价值是连接真实、已登录的 Chromium 浏览器，并在验证码、OTP 或确认操作出现时支持人工接管。它更适合操作小红书、管理后台等依赖现有登录态的网站，而不是替代浏览器测试框架。

Playwright 已能完成自动登录、保存并复用认证状态、页面与元素截图、自动等待断言、失败重试、并行测试、Trace、网络拦截和 Mock，并原生覆盖 Chromium、Firefox 与 WebKit。对于当前以自动化测试和结果验证为主的需求，Playwright 的能力更完整，额外安装 BrowserSkill 的收益有限。

只有出现以下明确需求时，再考虑安装 BrowserSkill：

- 必须直接使用日常 Chrome 或 Edge 中已有的登录状态。
- 经常需要人在验证码、OTP 或敏感确认环节临时接管。
- 需要让多个不同 Agent 通过统一的 `bsk` CLI 操作同一个真实浏览器。

参考资料：

- [BrowserSkill 官方 README](https://github.com/Tencent/BrowserSkill)
- [BrowserSkill Agent 安装说明](https://raw.githubusercontent.com/Tencent/BrowserSkill/main/AGENT_INSTALL.md)
- [Playwright Authentication](https://playwright.dev/docs/auth)
- [Playwright 官方能力说明](https://playwright.dev/)
